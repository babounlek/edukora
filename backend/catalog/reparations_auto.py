"""
Réparations automatiques à l'ingestion, avec journal.

Deux familles, choisies parce que leur correction est déterministe et vérifiable :

1. `_repair_literal_dollars` : `$` littéraux (variables PHP, références de tableur) que le
   moteur KaTeX apparierait à tort comme délimiteurs de formule. Cause de la plupart des 29
   échecs de rendu du 2026-09-19. Appliquée en mémoire à chaque ingestion (même convention
   que ingestion_repairs.py : une source régénérée hors de ce process ne défait rien).
2. `proposer_themes` : une Question sans thème reçoit des thèmes proposés depuis les frères
   de l'exercice, puis le texte, puis les mots-clés. Heuristique : chaque proposition est
   journalisée "À REVOIR" et réécrite dans le JSON source par run_ingestion.

Tout ce qui est réparé est consigné dans JOURNAL, lu par run_ingestion puis affiché par
ingest_corrections : rien n'est corrigé en silence.
"""

import re
from collections import Counter

# tunnel importé à l'usage : il tire quiz/inedit, qui importent eux-mêmes catalog (import circulaire au chargement).

JOURNAL = []
PROPOSITIONS_THEMES = []


def vider_journal():
    JOURNAL.clear()
    PROPOSITIONS_THEMES.clear()


def journaliser(message):
    JOURNAL.append(message)


# --- 1. `$` littéraux ---------------------------------------------------------------

# Zones où un `$` est sans risque : code (le rendu les ignore) et formule display déjà équilibrée.
_PROTEGE = re.compile(r"(```.*?```|~~~.*?~~~|\$\$.*?\$\$|`[^`\n]*`)", re.DOTALL)
_SUPERGLOBALE = re.compile(r"(?<![\\\w$])\$_(?:GET|POST|SESSION|SERVER|COOKIE|REQUEST|FILES)\b")
_REF_TABLEUR = re.compile(r"(?<![\\\w$])\$[A-Z]{1,3}\$\d+")
_VAR_PHP = re.compile(r"(?<![\\\w$])\$[A-Za-z_]\w*")


def _est_variable_php(text, match):
    """
    `$nom` (2 lettres ou plus) est un littéral PHP, et non l'ouverture d'une formule, s'il est
    suivi de `->`, de `['`/`["`, ou d'une instruction terminée par `;` (`$nom = valeur;`).
    `$a=1$;` et `$x = [a;b]$` sont des formules.
    """
    nom = match.group(0)[1:]
    if len(nom) < 2 and not nom.startswith("_"):
        return False  # `$x`, `$a` : variables de formule, jamais de code PHP réaliste
    suite = text[match.end():]
    if re.match(r"\s*(?:->|\[['\"])", suite):
        return True
    # Affectation ou instruction terminée : `$nom = valeur;` / `$nom;`. La valeur ne porte ni
    # LaTeX (`\`) ni crochet/parenthèse ouvert non refermé : `$x = [0 ; 1]$` reste une formule.
    instruction = re.match(r"\s*(?:[-+.*/]?=\s*([^;$\\\n]*))?;", suite)
    if not instruction:
        return False
    valeur = instruction.group(1) or ""
    return valeur.count("(") == valeur.count(")") and valeur.count("[") == valeur.count("]")


def _est_reference_tableur(text, match):
    """
    `$B$2:$B$5` (plage) ou une référence précédée d'un opérateur/séparateur de formule
    (`=SOMME($A$1;...`). `1. $A$1.` (événements $A$, numérotation) reste une formule : sans
    contexte de tableur, on ne touche à rien.
    """
    if re.match(r":\$[A-Z]{1,3}\$\d+", text[match.end():]):
        return True
    avant = text[: match.start()].rstrip(" ")
    return bool(avant) and avant[-1] in "=(;:,+*/-"


def _echapper_dollars(texte):
    parties = _PROTEGE.split(texte)
    total = 0
    sorties = []
    for i, partie in enumerate(parties):
        if i % 2:  # zone protégée, intacte
            sorties.append(partie)
            continue
        positions = set()
        for m in _SUPERGLOBALE.finditer(partie):
            positions.add(m.start())
        for m in _REF_TABLEUR.finditer(partie):
            if _est_reference_tableur(partie, m):
                positions.add(m.start())
        for m in _VAR_PHP.finditer(partie):
            if _est_variable_php(partie, m):
                positions.add(m.start())
        if positions:
            total += len(positions)
            partie = "".join(("\\$" if k in positions else c) for k, c in enumerate(partie))
        sorties.append(partie)
    resultat = "".join(sorties)
    resultat, orphelin = _echapper_dollar_orphelin(resultat)
    return resultat, total + orphelin


_CANDIDAT_ORPHELIN = re.compile(r"(?<![\\\w$])\$[A-Za-z_]\w{2,}(?!\w)(?!\$)")


def _echapper_dollar_orphelin(texte):
    """
    Dernier filet : si, une fois les règles ci-dessus appliquées, il reste un nombre IMPAIR de `$`
    hors code (donc un délimiteur jamais refermé) et un SEUL `$` suivi d'un identifiant de 3 lettres
    ou plus non refermé par un `$` (`$nbart articles`), c'est lui le littéral. `$ABC$` (formule) et
    tout cas ambigu (0 ou plusieurs candidats) restent intacts.
    """
    parties = _PROTEGE.split(texte)
    hors_code = "".join(p for i, p in enumerate(parties) if i % 2 == 0)
    if len(re.findall(r"(?<!\\)\$", hors_code)) % 2 == 0:
        return texte, 0
    candidats = [(i, m.start()) for i, p in enumerate(parties) if i % 2 == 0 for m in _CANDIDAT_ORPHELIN.finditer(p)]
    if len(candidats) != 1:
        return texte, 0
    i, debut = candidats[0]
    parties[i] = parties[i][:debut] + "\\" + parties[i][debut:]
    return "".join(parties), 1


# Champs qui portent du Markdown rendu (KaTeX) : seuls ceux-là sont réparés. Un titre, un nom de
# Tag ou un thème est du texte brut - y échapper un `$` créerait un Tag "\$_POST".
_CHAMPS_MARKDOWN_HORS_SUFFIXE = {"justification", "pourquoi_faux"}


def _est_champ_markdown(cle):
    return isinstance(cle, str) and (cle.endswith("_markdown") or cle in _CHAMPS_MARKDOWN_HORS_SUFFIXE)


def _walk_dollars(valeur, cle=None):
    """(valeur_réparée, nombre_de_$_échappés). `cle` est la clé du champ (conservée à travers les listes)."""
    if isinstance(valeur, str):
        return _echapper_dollars(valeur) if _est_champ_markdown(cle) else (valeur, 0)
    if isinstance(valeur, list):
        sortie, total = [], 0
        for x in valeur:
            v, n = _walk_dollars(x, cle)
            sortie.append(v)
            total += n
        return sortie, total
    if isinstance(valeur, dict):
        sortie, total = {}, 0
        for k, x in valeur.items():
            v, n = _walk_dollars(x, k)
            sortie[k] = v
            total += n
        return sortie, total
    return valeur, 0


def _repair_literal_dollars(data, reference=""):
    """Retourne (data, a_changé). Journalise le nombre de `$` échappés."""
    reparee, total = _walk_dollars(data)
    if not total:
        return data, False
    journaliser(f"[RÉPARÉ] {reference or 'document'} : {total} `$` littéral(aux) échappé(s) (variable PHP / référence de tableur).")
    return reparee, True


# --- 2. Thèmes -----------------------------------------------------------------------

_MIN_LONGUEUR_THEME = 5


def vocabulaire_matiere(subject):
    """Counter {nom de Tag: nombre d'usages} pour une matière (Questions et Cours)."""
    from .models import Cours, Question

    usage = Counter()
    for name in Question.objects.filter(exercise__lesson__subject=subject).values_list("themes__name", flat=True):
        if name:
            usage[name] += 1
    for name in Cours.objects.filter(subject=subject).values_list("tags__name", flat=True):
        if name:
            usage[name] += 1
    return usage


def _jetons(texte):
    from .tunnel import tag_key

    return tag_key(re.sub(r"[^\w'\-\s]", " ", texte or "")).split()


def _contient(jetons_texte, jetons_theme):
    n = len(jetons_theme)
    return n > 0 and any(jetons_texte[i:i + n] == jetons_theme for i in range(len(jetons_texte) - n + 1))


def proposer_themes(q_data, questions_data, data, subject, maximum=2):
    """
    Thèmes proposés pour une question sans thème, avec leur origine : (noms, origine) ou ([], None).
    Ordre : frères de l'exercice (thème majoritaire), puis vocabulaire de la matière retrouvé dans
    le texte, puis mots-clés de l'exercice qui correspondent à un Tag existant.
    """
    from .tunnel import find_tag_variant, tag_key

    freres = Counter()
    avec_theme = 0
    for autre in questions_data:
        if autre is q_data:
            continue
        themes = [t for t in (autre.get("themes") or []) if isinstance(t, str) and t.strip()]
        if themes:
            avec_theme += 1
            freres.update(themes)
    majoritaires = [t for t, n in freres.most_common() if n * 2 >= avec_theme][:maximum]
    if majoritaires:
        return majoritaires, "thèmes des autres questions de l'exercice"

    jetons_texte = _jetons(f"{q_data.get('enonce_markdown', '')} {q_data.get('corrige_markdown', '')}")
    trouves = []
    for nom, usages in vocabulaire_matiere(subject).items():
        if len(nom) < _MIN_LONGUEUR_THEME:
            continue
        jetons_theme = tag_key(nom).split()
        if _contient(jetons_texte, jetons_theme):
            trouves.append((len(jetons_theme), usages, nom))
    if trouves:
        trouves.sort(key=lambda t: (-t[0], -t[1], t[2]))
        return [nom for _, _, nom in trouves[:maximum]], "vocabulaire de la matière retrouvé dans le texte"

    par_mots_cles = []
    for mot in data.get("mots_cles_recherche") or []:
        tag = find_tag_variant(mot) if isinstance(mot, str) and mot.strip() else None
        if tag is not None and tag.name not in par_mots_cles:
            par_mots_cles.append(tag.name)
    if par_mots_cles:
        return par_mots_cles[:maximum], "mots-clés de l'exercice"

    return [], None


def enregistrer_proposition(reference, index_question, themes, origine):
    PROPOSITIONS_THEMES.append({"question_index": index_question, "themes": list(themes)})
    journaliser(f"[À REVOIR] {reference} : thèmes proposés automatiquement {themes} ({origine}).")
