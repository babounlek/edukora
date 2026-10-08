"""
Contrôle indépendant d'une épreuve inédite générée, AVANT son ingestion.

L'ingestion (voir inedit.ingestion) refuse déjà ce qui rendrait l'épreuve inutilisable
(somme des points, numéro répété, Tag inconnu). Ce contrôle regarde plus loin, sur les
fichiers JSON produits par le skill concepteur-epreuve-inedite, et dit TOUT ce qui ne va pas
en une seule passe plutôt qu'une erreur à la fois :

- structure et barème : titre et nombre d'exercices conformes au blueprint, points par exercice
  égaux à ceux du blueprint, points de chaque question en quarts, somme des questions égale aux
  points de l'exercice, grille de notation dont la somme égale les points (jamais sur une QCM),
  barème annoncé dans l'énoncé égal aux points ;
- contenu : Tags existants (et issus des compétences du blueprint), aucun numéro de question
  répété en tête d'énoncé, aucune formule creuse ni tiret cadratin, un seul rappel de méthode
  par corrigé et repris mot pour mot dans `rappels_de_methode` ;
- cours : un fichier de cours par rappel ; un squelette doit pointer vers un Cours VALIDE
  existant, d'un cursus compatible avec l'épreuve ; un cours complet a les 7 sections et une
  `formule_principale` en LaTeX sans `$` ni `%` non échappé.

Les fichiers de cours sont ceux du même dossier, nommés `<external_id>_cours_*.json`.
"""
import glob
import json
import os
import re
from dataclasses import dataclass, field

from catalog.models import Cours, Cursus, StatutContenu, Tag

from .ingestion import numero_repete_en_tete

# Tournures que le skill interdit (tiret cadratin compris) : voir sa section « Style ».
INTERDITS = [
    "—", "Il est à noter", "Force est de constater", "Notons que", "En définitive", "En somme,", "Pour conclure,",
]
SECTIONS_COURS = ["accroche", "prerequis", "regle", "exemple_resolu", "erreurs_classiques", "exercices_application", "synthese"]

_BAREME_ANNONCE_RE = re.compile(r"\*\(([\d,\.]+) ?pts?\)\*|\(([\d,\.]+) ?pts?\)")


@dataclass
class Resultat:
    external_id: str
    erreurs: list = field(default_factory=list)
    avertissements: list = field(default_factory=list)
    questions: int = 0
    figures: int = 0
    squelettes: int = 0
    cours_complets: int = 0
    rappels: int = 0

    @property
    def ok(self):
        return not self.erreurs

    def resume(self):
        return (
            f"{self.questions} questions, {self.figures} svg, {self.squelettes} squelettes + "
            f"{self.cours_complets} cours complets, {self.rappels} rappels"
        )


def _nombre(valeur):
    return float(str(valeur).replace(",", "."))


def _en_quarts(valeur):
    return abs(valeur * 4 - round(valeur * 4)) < 1e-9


def _cibles_cursus(blueprint):
    """Les Cursus que l'épreuve vise, pour juger si un cours existant est de son niveau."""
    series = [c["serie"] for c in blueprint["cursus"] if c.get("serie")]
    examen = blueprint["cursus"][0]["examen"]
    qs = Cursus.objects.filter(examen__iexact=examen)
    qs = qs.filter(series__code__in=series) if series else qs.filter(series__isnull=True)
    return {str(c) for c in qs}


def controler_epreuve(chemin):
    """Contrôle le fichier JSON d'une épreuve (chemin complet) et ses fichiers de cours voisins."""
    dossier = os.path.dirname(os.path.abspath(chemin))
    ep = json.load(open(chemin, encoding="utf-8"))
    ext = ep["external_id"]
    res = Resultat(external_id=ext)
    err, avert = res.erreurs, res.avertissements

    chemin_bp = os.path.join(dossier, ep["blueprint_external_id"] + ".json")
    if not os.path.exists(chemin_bp):
        err.append(f"blueprint introuvable à côté de l'épreuve : {ep['blueprint_external_id']}.json")
        return res
    bp = json.load(open(chemin_bp, encoding="utf-8"))

    if ep["titre"] != bp["titre"]:
        err.append(f"titre différent du blueprint : {ep['titre']!r}")
    if len(ep["exercices"]) != len(bp["sections_plan"]):
        err.append("nombre d'exercices différent du blueprint")
    competences = set(bp["competences"])
    rappels = {}

    for i, ex in enumerate(ep["exercices"]):
        plan = bp["sections_plan"][i] if i < len(bp["sections_plan"]) else None
        points_ex = _nombre(ex["points"])
        if plan and abs(points_ex - plan["points"]) > 1e-9:
            err.append(f"ex{ex['numero_exercice']}: points {points_ex} != blueprint {plan['points']}")
        somme = 0.0
        for pos, q in enumerate(ex["questions"], 1):
            res.questions += 1
            ou = f"ex{ex['numero_exercice']} Q{q['numero']}"
            points = q.get("points")
            if points is None:
                err.append(f"{ou}: points absents")
                continue
            points = float(points)
            somme += points
            if not _en_quarts(points):
                err.append(f"{ou}: points {points} pas en quarts")
            enonce, corrige = q["enonce_markdown"], q["corrige_markdown"]
            if numero_repete_en_tete(str(q["numero"]).strip(), enonce):
                err.append(f"{ou}: le numéro est répété au début de l'énoncé (la plateforme l'affiche déjà : « 1. 1. »)")
            texte = enonce + corrige
            res.figures += texte.count("<svg")
            for mot in INTERDITS:
                if mot in texte:
                    err.append(f"{ou}: interdit {mot!r}")
            if q.get("type_reponse", "ouverte") == "qcm":
                if q.get("criteres_notation"):
                    err.append(f"{ou}: QCM avec critères")
                if q.get("reponse_correcte") not in [c["lettre"] for c in (q.get("choix") or [])]:
                    err.append(f"{ou}: reponse_correcte invalide")
            else:
                criteres = q.get("criteres_notation") or []
                if criteres and abs(sum(c["points"] for c in criteres) - points) > 1e-9:
                    err.append(f"{ou}: somme critères {sum(c['points'] for c in criteres)} != points {points}")
                if not criteres and points > 0.5:
                    avert.append(f"{ou}: pas de critères pour {points} pts")
            annonce = _BAREME_ANNONCE_RE.search(enonce)
            if annonce and abs(_nombre(annonce.group(1) or annonce.group(2)) - points) > 1e-9:
                err.append(f"{ou}: barème annoncé {annonce.group(1) or annonce.group(2)} != points {points}")
            if not q.get("themes"):
                err.append(f"{ou}: pas de thèmes")
            for theme in (q.get("themes") or []):
                if theme not in competences:
                    avert.append(f"{ou}: thème hors blueprint {theme!r}")
                if not Tag.objects.filter(name=theme).exists():
                    err.append(f"{ou}: Tag inexistant {theme!r}")
            if corrige.count("### Rappel de méthode") > 1:
                err.append(f"{ou}: plusieurs Rappel de méthode")
            for rappel in (q.get("rappels_de_methode") or []):
                rappels[rappel["id"]] = rappel
                if rappel["contenu_markdown"] not in corrige:
                    err.append(f"{ou}: rappel non verbatim ({rappel['id']})")
                attendu = f"rdi-{ext}-ex{ex['numero_exercice']}-q{pos}-0"
                if rappel["id"] != attendu:
                    avert.append(f"{ou}: id rappel {rappel['id']} != attendu {attendu}")
            if "$" in enonce.replace("$$", "") and enonce.count("$") % 2:
                avert.append(f"{ou}: nombre impair de $ dans l'énoncé")
        if abs(somme - points_ex) > 1e-9:
            err.append(f"ex{ex['numero_exercice']}: somme questions {somme} != {points_ex}")
        if plan and len(ex["questions"]) != plan["nombre_questions"]:
            avert.append(f"ex{ex['numero_exercice']}: {len(ex['questions'])} questions (blueprint {plan['nombre_questions']})")
        intro = (ex.get("enonce_intro_markdown") or "")
        res.figures += intro.count("<svg")
        for mot in INTERDITS:
            if mot in intro:
                err.append(f"ex{ex['numero_exercice']} intro: interdit {mot!r}")
    res.rappels = len(rappels)

    _controler_cours(res, dossier, ext, bp, rappels)
    return res


def _controler_cours(res, dossier, ext, bp, rappels):
    err = res.erreurs
    couverts = set()
    cibles = None
    for chemin_cours in sorted(glob.glob(os.path.join(dossier, ext + "_cours_*.json"))):
        nom = os.path.basename(chemin_cours)
        cours = json.load(open(chemin_cours, encoding="utf-8"))
        rappel_id = cours["source"]["rappel_id"]
        if rappel_id not in rappels:
            err.append(f"{nom}: rappel_id inconnu {rappel_id}")
        if rappel_id in couverts:
            err.append(f"{nom}: plusieurs fichiers de cours pour le rappel {rappel_id}")
        couverts.add(rappel_id)
        titre = cours["meta"]["titre"]
        if cours.get("sections"):
            res.cours_complets += 1
            types = [s["type"] for s in cours["sections"]]
            if types != SECTIONS_COURS:
                err.append(f"{nom}: sections {types}")
            for s in cours["sections"]:
                if s["type"] != "regle":
                    continue
                formule = (s.get("formule_principale") or "")
                if "$" in formule or re.search(r"(?<!\\)%", formule):
                    err.append(f"{nom}: formule_principale {formule!r}")
            if "—" in json.dumps(cours, ensure_ascii=False):
                err.append(f"{nom}: tiret cadratin")
            # Le cours que CE fichier a déjà créé (même external_id) n'est pas un doublon : le
            # contrôle sert aussi après l'ingestion.
            homonyme = Cours.objects.filter(titre__iexact=titre, statut=StatutContenu.VALIDE).exclude(
                external_id=cours.get("cours_id", ""),
            )
            if homonyme.exists():
                err.append(f"{nom}: un cours complet porte le titre d'un cours existant : {titre!r} (faire un squelette)")
            continue
        res.squelettes += 1
        existants = Cours.objects.filter(titre__iexact=titre)
        if not existants.exists():
            err.append(f"{nom}: squelette sans Cours existant : {titre!r}")
            continue
        valides = [c for c in existants if c.statut == StatutContenu.VALIDE]
        if not valides:
            err.append(f"{nom}: Cours non VALIDE : {titre!r}")
            continue
        cursus = {str(k) for k in valides[0].cursus.all()}
        if cibles is None:
            cibles = _cibles_cursus(bp)
        if cursus and not (cursus & cibles):
            err.append(f"{nom}: cursus hors niveau {sorted(cursus)[:2]} pour {titre!r}")
    manque = [r for r in rappels if r not in couverts]
    if manque:
        err.append(f"rappels sans fichier de cours : {len(manque)} ex. {manque[:3]}")
