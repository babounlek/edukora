"""Controle mecanique d'une epreuve inedite GCE (blueprint + epreuve) AVANT ingestion.

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\controle_inedite_gce.py ep-....json [bp-....json]
        [--corpus backend/ingest/cm --matiere maths] [--type qcm|redige]

Ce que ce controle verifie (voir scripts/gce/INEDITES_GCE.md pour les regles) :
  - contrat JSON du skill concepteur-epreuve-inedite (champs, bareme exact, numero non repete, rappels verbatim) ;
  - regles propres au GCE (examen gce_ol/gce_al, serie vide, langue anglaise, matiere et code du Board, duree) ;
  - format du paper (50 QCM a 4 choix pour un Paper 1, cles equilibrees) ;
  - style (pas de tiret cadratin dans le contenu, pas de formule d'IA), `$` equilibres ;
  - ORIGINALITE : chaque question est comparee a toutes les questions reelles du corpus de la matiere.
Code de sortie 1 s'il y a une ERREUR ; les AVERTISSEMENTS se relisent.
"""
import argparse
import difflib
import glob
import json
import os
import re
import sys

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CODES_BOARD = {"mathematics": "0570", "physics": "0580", "chemistry": "0515", "biology": "0510", "english language": "0530", "french": "0545", "additional mathematics": "0575", "human biology": "0565", "commerce": "0520"}
FORMULES_IA = [
    r"\bit is worth noting\b", r"\bit should be noted\b", r"\bnote that\b", r"\bnotice that\b", r"\bdelve\b",
    r"\bin conclusion\b", r"\bfurthermore\b", r"\bmoreover\b", r"\bit is important to note\b", r"\bin summary\b",
    r"\bil est \u00e0 noter\b", r"\bforce est de constater\b",
]
RE_SVG = re.compile(r"<svg\b.*?</svg>", re.S)


class Rapport:
    def __init__(self):
        self.erreurs, self.avertissements = [], []

    def err(self, msg):
        self.erreurs.append(msg)

    def warn(self, msg):
        self.avertissements.append(msg)


def sans_svg(t):
    return RE_SVG.sub(" [figure] ", t or "")


def normaliser(t):
    t = sans_svg(t).lower()
    t = re.sub(r"[\\${}^_]|\\(?:dfrac|frac|text|mathbf|times|cdot|leq|geq|circ)", " ", t)
    t = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9.\u2212\- ]+", " ", t))
    return t.strip()


def corps(t):
    """Enonce sans le paragraphe de consigne imprime de chaque question de completion multiple ou d'assertion-raison
    (« **Instructions (Questions 8-10):** ... » : le format du vrai sujet, repris tel quel, n'est pas du contenu)."""
    t = t or ""
    if t.lstrip().startswith("**Instructions"):
        reste = t.lstrip().split(chr(10) * 2, 1)
        t = reste[1] if len(reste) > 1 else t
    return re.sub(r"\|\s*First statement\s*\|\s*Second statement\s*\|\s*\n\|[-| ]+\|\s*\n?", "", t)


def nombres(t):
    return set(re.findall(r"\d+(?:\.\d+)?", sans_svg(t)))


def champs_texte(obj, chemin=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from champs_texte(v, f"{chemin}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from champs_texte(v, f"{chemin}[{i}]")
    elif isinstance(obj, str):
        yield chemin, obj


def verifier_dollars(t):
    """Nombre de `$` non echappes, hors blocs de code, hors svg : doit etre pair."""
    t = RE_SVG.sub("", t)
    t = re.sub(r"`[^`]*`", "", t)
    t = t.replace("\\$", "")
    return t.count("$") % 2 == 0


def charger_corpus(dossier, matiere):
    refs = []
    for d in sorted(glob.glob(os.path.join(dossier, f"gce-ol-{matiere}-*"))):
        for f in glob.glob(os.path.join(d, "*.json")):
            try:
                j = json.load(open(f, encoding="utf8"))
            except Exception:
                continue
            if not isinstance(j, dict) or "questions" not in j:
                continue
            for q in j["questions"]:
                enonce = (j.get("enonce_intro_markdown") or "") + " " + corps(q.get("enonce_markdown") or "")
                opts = " ".join(c.get("texte", "") for c in q.get("choix") or [])
                refs.append({"src": f"{os.path.basename(d)}#{q.get('numero')}", "stem": normaliser(enonce), "stem0": normaliser(corps(q.get("enonce_markdown") or "")),
                             "texte": enonce + " " + opts, "opts": frozenset(normaliser(c.get("texte", "")) for c in q.get("choix") or [])})
    return refs


def originalite(questions, refs, rap, seuil_err=0.82, seuil_warn=0.66):
    """Compare chaque question (enonce + options) a chaque question reelle. Le gabarit d'une question de syllabus
    (« The median of ... is ») revient forcement ; ce qui ne doit JAMAIS revenir : memes donnees, meme contexte,
    memes options. Le score combine la ressemblance du texte et la part de nombres communs."""
    pires = []
    for q in questions:
        enonce_q = corps(q["enonce_markdown"])
        stem = normaliser(enonce_q)
        opts = " ".join(c["texte"] for c in q.get("choix") or [])
        nums = nombres(enonce_q + " " + opts)
        # options « riches » seulement : « 2 », « 13 » reviennent partout et ne prouvent rien
        opts_n = frozenset(o for o in (normaliser(c["texte"]) for c in q.get("choix") or []) if len(o) >= 5)
        meilleur = (0.0, 0.0, None)
        plus_proche = (0.0, None)  # enonce le plus ressemblant, quel que soit le score (les nombres communs peuvent masquer un enonce identique)
        for r in refs:
            # l'enonce reel est compare avec ET sans la consigne generale de l'exercice qui le precede (« Multiple choice questions ... »),
            # sinon cette consigne dilue la ressemblance d'un enonce court identique
            cibles = [r["stem"]] + ([r["stem0"]] if r.get("stem0") else [])
            ratio = max(difflib.SequenceMatcher(None, stem, c).quick_ratio() for c in cibles)
            if ratio < 0.5:
                continue
            ratio = max(difflib.SequenceMatcher(None, stem, c).ratio() for c in cibles)
            # un jeu d'options commun ne prouve une copie que si l'ENONCE se ressemble aussi : le vocabulaire d'une matiere est
            # ferme (Xylem, Phloem, Cambium reviennent d'une annee a l'autre dans des questions differentes)
            if ratio >= 0.6 and len(opts_n & {o for o in r["opts"] if len(o) >= 5}) >= 3:
                rap.err(f"Q{q['numero']}: au moins 3 options identiques (non triviales) et un enonce proche de {r['src']} (texte {ratio:.2f})")
            if ratio > plus_proche[0]:
                plus_proche = (ratio, r["src"])
            communs = len(nums & nombres(r["texte"])) / max(1, len(nums | nombres(r["texte"])))
            score = 0.6 * ratio + 0.4 * communs
            if score > meilleur[0]:
                meilleur = (score, ratio, r["src"], communs)
        if meilleur[2] is not None:
            pires.append((meilleur[0], q["numero"], meilleur))
            # un énoncé qui ne porte que 0 à 2 nombres (« Solve the equation f(x)=0 ») ne prouve rien par ses nombres communs :
            # ERREUR seulement avec au moins 3 nombres en jeu, sinon AVERTISSEMENT
            # un énoncé court SANS nombres (« Which of the following ... has the longest wavelength ? ») identique ou presque à un énoncé réel est
            # la même question : la plateforme le voit (score d'originalité 0), le contrôle doit le voir avant
            if plus_proche[0] >= 0.9 and len(nums) < 3 and len(stem) >= 40:
                rap.err(f"Q{q['numero']}: énoncé quasi identique à un énoncé réel, {plus_proche[1]} (texte {plus_proche[0]:.2f}) : changer de question, pas de mots")
            elif meilleur[1] >= seuil_err and meilleur[3] >= 0.5 and len(nums) >= 3:
                rap.err(f"Q{q['numero']}: trop proche de {meilleur[2]} (texte {meilleur[1]:.2f}, nombres communs {meilleur[3]:.2f})")
            elif meilleur[1] >= seuil_warn and meilleur[3] >= 0.5:
                rap.warn(f"Q{q['numero']}: ressemble a {meilleur[2]} (texte {meilleur[1]:.2f}, nombres communs {meilleur[3]:.2f}) : a relire")
    pires.sort(reverse=True)
    return pires[:5]


def controler(ep, bp, refs, type_paper, rap, sections_attendues=None):
    # --- blueprint
    if bp:
        for k in ("external_id", "titre", "matiere", "cursus", "competences", "sections_plan", "duree_minutes", "bareme_total"):
            if not bp.get(k):
                rap.err(f"blueprint: champ {k!r} manquant")
        for c in bp.get("cursus") or []:
            if c.get("examen") not in ("gce_ol", "gce_al"):
                rap.err(f"blueprint: examen {c.get('examen')!r} invalide pour le GCE (gce_ol ou gce_al, jamais gce seul)")
            if c.get("serie") not in ("", None, "Technical"):
                rap.err(f"blueprint: serie {c.get('serie')!r} : le GCE n'a pas de serie (vide, ou Technical)")
        if bp.get("savoirs_officiels"):
            rap.err("blueprint: savoirs_officiels doit etre omis pour le GCE (pas de referentiel programme)")
        mat = (bp.get("matiere") or "").lower()
        if mat not in CODES_BOARD:
            rap.warn(f"blueprint: matiere {bp.get('matiere')!r} absente de la table locale des codes du Board (a verifier)")
        if type_paper == "qcm" and bp.get("duree_minutes") != 90:
            rap.err("blueprint: un Paper 1 QCM dure 90 minutes (1h30)")
        if ep and bp.get("external_id") != ep.get("blueprint_external_id"):
            rap.err("epreuve.blueprint_external_id ne correspond pas au blueprint")
        if "\u2014" in (bp.get("titre") or ""):
            rap.err("titre: tiret cadratin interdit")
    if not ep:
        return
    # --- champs obligatoires
    for k in ("external_id", "titre", "blueprint_external_id", "exercices"):
        if not ep.get(k):
            rap.err(f"epreuve: champ {k!r} manquant")
    exs = ep.get("exercices") or []
    if type_paper == "qcm":
        if len(exs) != 1:
            rap.err(f"Paper 1 QCM : un seul exercice attendu (le vrai sujet n'en a qu'un), trouve {len(exs)}")
        if exs and exs[0].get("groupes"):
            rap.err("Paper 1 QCM : pas de groupes (structure plate)")
    # --- style et syntaxe
    for chemin, t in champs_texte(ep):
        # un « \r », « \t » ou « \b » écrit dans une chaîne Python non brute devient un caractère de contrôle : « \rightarrow »
        # s'affiche « ightarrow », « \times » perd son « t ». Le rendu KaTeX ne le voit pas (texte ordinaire).
        ctrl = sorted({hex(ord(c)) for c in t if ord(c) < 32 and c != "\n"})
        if ctrl:
            rap.err(f"{chemin}: caractère(s) de contrôle {ctrl} (commande LaTeX à backslash simple dans une chaîne non brute ?)")
        if chemin.endswith(".titre"):
            continue
        for tiret in ("\u2014", "\u2013"):
            if tiret in sans_svg(t):
                rap.err(f"{chemin}: tiret cadratin ou demi-cadratin dans le contenu")
        for motif in FORMULES_IA:
            if re.search(motif, sans_svg(t), re.I):
                rap.warn(f"{chemin}: formule d'IA ({motif})")
        if not verifier_dollars(t):
            rap.err(f"{chemin}: nombre impair de $ (formule non fermee ou $ nu)")
        if re.search(r"[\u00ab\u00bb]", t) and "<svg" in t:
            rap.err(f"{chemin}: guillemets francais dans une figure")
    # --- questions
    toutes = []
    cles = []
    pour_originalite = []  # une entree par question, avec le support de l'exercice (un paper redige partage son intro)
    par_groupe = {}
    for ex in exs:
        pts_q = 0
        groupe = (ex.get("groupes") or ["-"])[0]
        stat = par_groupe.setdefault(groupe, [0, 0.0])
        stat[0] += 1
        stat[1] += float(ex.get("points") or 0)
        for q in ex.get("questions") or []:
            toutes.append(q)
            pour_originalite.append({
                "numero": f"{ex.get('numero_exercice')}.{q.get('numero')}", "choix": q.get("choix") or [],
                "enonce_markdown": (ex.get("enonce_intro_markdown") or "") + " " + (q.get("enonce_markdown") or ""),
            })
            n = str(q.get("numero"))
            crit = q.get("criteres_notation") or []
            if crit and abs(sum(float(c["points"]) for c in crit) - float(q.get("points") or 0)) > 1e-9:
                rap.err(f"Q{ex.get('numero_exercice')}.{n}: criteres_notation {sum(float(c['points']) for c in crit)} != points {q.get('points')}")
            if type_paper == "redige" and q.get("type_reponse") == "ouverte" and not crit and float(q.get("points") or 0) > 0.5:
                rap.err(f"Q{ex.get('numero_exercice')}.{n}: question ouverte de plus d'un demi-point sans criteres_notation")
            for k in ("numero", "enonce_markdown", "corrige_markdown"):
                if not q.get(k):
                    rap.err(f"Q{n}: champ {k!r} manquant")
            if re.match(r"\s*\*{0,2}\s*" + re.escape(n) + r"\s*[.)](\s|\*|$)", q.get("enonce_markdown", "")):
                rap.err(f"Q{n}: l'enonce commence par son propre numero")
            if re.match(r"\s*\*{0,2}\s*" + re.escape(n) + r"\s*[.)](\s|\*|$)", q.get("corrige_markdown", "")):
                rap.err(f"Q{n}: le corrige commence par son propre numero")
            if not q.get("themes"):
                rap.err(f"Q{n}: themes manquants")
            pts = q.get("points")
            if pts in (None, ""):
                rap.err(f"Q{n}: points manquants (bareme exact obligatoire)")
            else:
                pts_q += float(pts)
            corr = q.get("corrige_markdown", "")
            if "### Rappel de m\u00e9thode" not in corr:
                rap.err(f"Q{n}: corrige sans bloc '### Rappel de methode'")
            reste = re.sub(r"### Rappel de m\u00e9thode\n[^\n]*(\n(?!\n)[^\n]*)*", "", corr).strip()
            reste = re.sub(r"###[^\n]*\n[^\n]*(\n(?!\n)[^\n]*)*", "", reste).strip()
            if len(reste) < 20:
                rap.err(f"Q{n}: le corrige n'est fait que de blocs Rappel/Piege/Conseil (reponse en clair absente)")
            # rappel verbatim, un seul paragraphe, jamais une reponse deguisee
            for r in q.get("rappels_de_methode") or []:
                if set(r) != {"id", "competence", "contenu_markdown", "cours_genere", "cours_id"}:
                    rap.err(f"Q{n}: cles inattendues dans rappels_de_methode : {sorted(r)}")
                if r["contenu_markdown"] not in corr:
                    rap.err(f"Q{n}: rappel non verbatim dans le corrige")
                if "\n\n" in r["contenu_markdown"]:
                    rap.err(f"Q{n}: rappel de plusieurs paragraphes")
            if not q.get("rappels_de_methode"):
                rap.warn(f"Q{n}: aucun rappel_de_methode extrait")
            if q.get("type_reponse") == "qcm":
                lettres = [c["lettre"] for c in q.get("choix") or []]
                if type_paper == "qcm" and lettres != list("abcd"):
                    rap.err(f"Q{n}: les choix d'un Paper 1 sont a, b, c, d (trouve {lettres})")
                if q.get("reponse_correcte") not in lettres:
                    rap.err(f"Q{n}: reponse_correcte absente des choix")
                if len({c["texte"] for c in q["choix"]}) != len(q["choix"]):
                    rap.err(f"Q{n}: deux choix identiques")
                if q.get("criteres_notation"):
                    rap.err(f"Q{n}: une QCM n'a pas de criteres_notation")
                m = re.search(r"\*\*Answer: ([A-D])\.\*\*", corr)
                if not m or m.group(1).lower() != q.get("reponse_correcte"):
                    rap.err(f"Q{n}: '**Answer: X.**' absent ou different de reponse_correcte")
                cles.append(q.get("reponse_correcte"))
            elif type_paper == "qcm":
                rap.err(f"Q{n}: un Paper 1 est entierement QCM")
        if ex.get("points") and abs(pts_q - float(ex["points"])) > 1e-9:
            rap.err(f"exercice {ex.get('numero_exercice')}: somme des points {pts_q} != {ex['points']}")
    if type_paper == "qcm":
        if len(toutes) != 50:
            rap.err(f"Paper 1 QCM : 50 questions attendues, trouve {len(toutes)}")
        for l in "abcd":
            if not 10 <= cles.count(l) <= 15:
                rap.warn(f"cles : la lettre {l} sort {cles.count(l)} fois sur {len(cles)} (viser 12-13)")
        if any(cles[i] == cles[i + 1] == cles[i + 2] for i in range(len(cles) - 2)):
            rap.warn("cles : trois reponses identiques de suite")
        diffs = [q.get("difficulte_estimee") for q in toutes]
        part_faible = diffs.count("faible") / max(1, len(diffs))
        if not 0.45 <= part_faible <= 0.7:
            rap.warn(f"difficulte : {part_faible:.0%} de questions faibles (corpus reel : 61 %, viser 45-70 %)")
        if diffs.count("elevee") > 4:
            rap.warn(f"difficulte : {diffs.count('elevee')} questions elevees (corpus reel : ~0-1 par sujet)")
    if type_paper == "redige":
        if sections_attendues:
            for groupe, (nb, pts) in sections_attendues.items():
                reel = par_groupe.get(groupe)
                if not reel or reel[0] != nb or abs(reel[1] - pts) > 1e-9:
                    rap.err(f"{groupe}: attendu {nb} exercices et {pts} points, trouve {reel}")
        total = sum(v[1] for v in par_groupe.values())
        if bp and bp.get("bareme_total") and abs(float(bp["bareme_total"]) - total) > 1e-9:
            rap.err(f"bareme_total du blueprint {bp['bareme_total']} != somme des points {total}")
        if any(q.get("type_reponse") == "qcm" for q in toutes):
            rap.err("Paper redige : aucune QCM attendue")
        diffs = [q.get("difficulte_estimee") for q in toutes]
        part_faible = diffs.count("faible") / max(1, len(diffs))
        if not 0.45 <= part_faible <= 0.7:
            rap.warn(f"difficulte : {part_faible:.0%} de sous-questions faibles (corpus reel Maths P2 : 50-62 % sur 2023-2026, viser 45-70 %)")
        if diffs.count("elevee") > 4:
            rap.warn(f"difficulte : {diffs.count('elevee')} sous-questions elevees (corpus reel : 0-1 par sujet)")
    # --- originalite
    pires = originalite(pour_originalite if type_paper == "redige" else toutes, refs, rap) if refs else []
    return pires


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("epreuve")
    ap.add_argument("blueprint", nargs="?")
    ap.add_argument("--corpus", default=os.path.join(RACINE, "backend", "ingest", "cm"))
    ap.add_argument("--matiere", default="maths", help="fragment du dossier gce-ol-<matiere>-* du corpus de reference")
    ap.add_argument("--type", default="qcm", choices=["qcm", "redige"])
    ap.add_argument("--sections", default="", help='paper redige : "SECTION A:10:45,SECTION B:4:60" (groupe:nombre exercices:points)')
    ap.add_argument("--jumeau", default="", help="JSON de l'epreuve jumelle (autre paper de la session) : compare aussi a elle")
    a = ap.parse_args()
    ep = json.load(open(a.epreuve, encoding="utf8"))
    bp = json.load(open(a.blueprint, encoding="utf8")) if a.blueprint else None
    refs = charger_corpus(a.corpus, a.matiere)
    if a.jumeau:
        jum = json.load(open(a.jumeau, encoding="utf8"))
        for ex in jum["exercices"]:
            for q in ex["questions"]:
                enonce = (ex.get("enonce_intro_markdown") or "") + " " + (q.get("enonce_markdown") or "")
                refs.append({"src": f"JUMEAU {jum['external_id']}#{q.get('numero')}", "stem": normaliser(enonce),
                             "texte": enonce + " " + " ".join(c.get("texte", "") for c in q.get("choix") or []),
                             "opts": frozenset(normaliser(c.get("texte", "")) for c in q.get("choix") or [])})
    sections = {}
    for part in filter(None, a.sections.split(",")):
        g, nb, pts = part.rsplit(":", 2)
        sections[g.strip()] = (int(nb), float(pts))
    rap = Rapport()
    pires = controler(ep, bp, refs, a.type, rap, sections)
    print(f"corpus de reference : {len(refs)} questions reelles (gce-ol-{a.matiere}-*)")
    for score, n, m in pires or []:
        print(f"  plus proche, Q{n}: {m[2]} (texte {m[1]:.2f}, nombres communs {m[3]:.2f})")
    for w in rap.avertissements:
        print("AVERTISSEMENT", w)
    for e in rap.erreurs:
        print("ERREUR", e)
    print(f"{len(rap.erreurs)} erreur(s), {len(rap.avertissements)} avertissement(s)")
    return 1 if rap.erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
