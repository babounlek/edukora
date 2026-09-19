"""
Traduit la sortie JSON de la compétence correction-experte vers nos modèles :
- Mode automatisation (un objet = un exercice) -> Lesson/Exercise/RappelDeMethode
  (ingest_exercise)
- Mode cours (un objet = un cours dérivé d'un rappel de méthode) -> Cours
  (ingest_cours)

Tolère à la fois l'ancienne nomenclature des séries (A, C, D, F pour "TI") que
la compétence a pu utiliser avant sa mise à jour, et la nomenclature réelle
actuelle (A, C, D, E, TI) utilisée dans notre base. "B"/"SES" (Sciences
Économiques et Sociales) n'est plus toléré : série supprimée du référentiel
(décision utilisateur, 2026-08-19), plus aucune cible pour ce code. "G"
(Techniques Commerciales, ex-COM, supprimée le même jour) non plus, mais pour
une autre raison : le technique se raisonne désormais en spécialité (STT/STI/
Hôtellerie-Tourisme - voir catalog.models.Filiere), et "G" seul ne dit pas
laquelle - une épreuve technique doit être ingérée avec le code de spécialité
exact (ex: "comptabilite_gestion") plutôt qu'une série ambiguë.

Tolère aussi les épreuves communes à plusieurs séries (ex: Maths BAC C/E,
très courant au Cameroun) : le champ `serie` peut contenir plusieurs codes
séparés par un tiret, une virgule ou un slash ("C-E", "C, E", "C/E"), et le
champ `coefficient` peut être une valeur unique ou un objet {code_serie:
coefficient} quand il diffère selon la série (voir _format_coefficient).

Le pays n'est jamais résolu depuis le JSON : il est dérivé du chemin sur disque,
convention `ingest/<code_pays>/<epreuve>/...json` (voir _country_code_from_path) pour
un exercice, hérité de l'épreuve source pour un cours. La compétence fournit désormais
aussi un champ `pays` (voir SKILL.md) censé reproduire ce même code - _validate_pays_
matches_country s'en sert uniquement comme signal de contrôle redondant (erreur si
incohérent), jamais comme source de vérité.
"""

import json
import os
import re
import subprocess
import sys
import unicodedata
from datetime import datetime
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image, UnidentifiedImageError
from django.db import transaction
from django.utils import timezone

from .ingestion_repairs import (
    _dedupe_exercise_heading,
    _dedupe_question_enonce,
    _dedupe_trailing_exercise_reference,
    _drop_processing_notes,
    _merge_series_from_folder_name,
    _repair_dict_shaped_cours_sections,
    _repair_double_json_escaping,
    _repair_glued_hline,
    _repair_missing_exercise_heading,
    _repair_missing_matrix_row_separators,
    _repair_narrow_array_columns,
    _reposition_trailing_exercise_reference,
    _strip_em_dash,
)
from .models import Cours, Country, Cursus, Difficulte, Examen, Exercise, Figure, FiliereSerieA, Lesson, LessonType, NatureEpreuve, Origine, OrigineFigure, PartieEpreuveFrancais, Question, RappelDeMethode, Series, StatutContenu, Subject, SUBJECT_FAMILIES, Tag, TypeReponse, VarianteSujet, _join_fr, institution_officielle
from programme.models import Module, Savoir


class IngestionError(Exception):
    pass


def _normalize(value):
    if value is None:
        return ""
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    return text.strip().lower()


# "A-ABI" (vu sur au moins une épreuve source) : sans rapport avec les vraies séries
# multiples ("C-E" = deux séries distinctes sur une même épreuve) - "ABI" n'est pas un
# code de série (décision utilisateur, 2026-08-18 : ABI = "A4 Bilingue", une filière de
# la Série A, pas une série à part - voir FiliereSerieA/Lesson.filiere_serie_a). Retiré
# ici avant le découpage générique des séries pour ne pas être pris pour une deuxième
# série inconnue ; capturé séparément par _resolve_filiere_serie_a, appelé sur la même
# chaîne AVANT ce retrait.
_SERIE_NOISE_SUFFIX_RE = re.compile(r"-abi\b", re.IGNORECASE)


def _split_series(serie_raw):
    """'C-E' -> ['C', 'E'] ; 'C, E' -> ['C', 'E'] ; 'C' -> ['C'] ; 'A-ABI' -> ['A'] ;
    'D et TI' -> ['D', 'TI'] (vu sur bac-blanc-d-ti-physique-2025-cameroun) ;
    'D & TI' -> ['D', 'TI'] (vu sur bac-d-maths-2018/2019/2020-cameroun)."""
    cleaned = _SERIE_NOISE_SUFFIX_RE.sub("", str(serie_raw or ""))
    parts = re.split(r"[,/\-–—\s]+", cleaned.strip())
    # "et"/"&" (conjonctions, jamais un code de série) n'ont de sens comme séparateur
    # QUE lorsqu'ils tombent entre deux vrais tokens (espaces des deux côtés dans la
    # chaîne d'origine) - un split générique sur tout espace les fait ressortir comme
    # un token à part entière au même titre que "D"/"TI", d'où le filtrage après coup
    # plutôt qu'une simple exclusion de motif dans le pattern de split lui-même.
    return [p for p in parts if p and p.lower() != "et" and p != "&"]


MATIERE_MAP = {
    "mathematiques": "MATHS",
    "maths": "MATHS",
    "physique-chimie": "PHYSIQUE_CHIMIE",
    "physique chimie": "PHYSIQUE_CHIMIE",
    # Décision utilisateur du 2026-08-08 : Physique et Chimie sont deux Subject à part
    # entière (avant cette date, toutes deux étaient conflatées vers PHYSIQUE_CHIMIE -
    # voir SUBJECT_FAMILIES et la logique de "promotion" dans ingest_exercise pour le
    # cas réel d'une épreuve qui mélange les deux, ex. bac-d-physique-chimie-1995-
    # cameroun ou bac-c-physique-chimie-2016-congo, où le matiere déclaré varie déjà
    # par exercice au sein d'un même epreuve_source). PHYSIQUE_CHIMIE reste la Subject
    # à utiliser quand la source déclare littéralement les deux ensemble, ou quand la
    # discipline exacte n'est pas déterminable - jamais supprimée ni renommée.
    "physique": "PHYSIQUE",
    "chimie": "CHIMIE",
    "sciences de la vie et de la terre": "SVT",
    "svt": "SVT",
    # Nom officiel actuel de la matière au BAC camerounais (constaté sur bac-c-ti-
    # svteehb-2024-cameroun, série C-TI) : "Sciences de la Vie et de la Terre, Éducation
    # à l'Environnement, Hygiène et Biotechnologie" - même matière que SVT, juste
    # l'intitulé complet/à jour du programme (contenu vérifié identique : osmose,
    # immunologie, génétique... rien de spécifiquement "environnement/hygiène" qui
    # justifierait une Subject à part), pas une discipline distincte.
    "svteehb": "SVT",
    "francais": "FRANCAIS",
    "langue francaise": "FRANCAIS",
    # Composantes de l'épreuve de Français au BEPC camerounais (jamais notées comme
    # une seule épreuve "Français" - le sujet source distingue ces intitulés par
    # exercice/partie), toutes vues sur bepc-etude-de-texte-*/bepc-orthographe-2016-
    # cameroun : pas des matières à part, la même Subject FRANCAIS que le reste du
    # corpus.
    "etude de texte": "FRANCAIS",
    "expression ecrite": "FRANCAIS",
    "orthographe": "FRANCAIS",
    "philosophie": "PHILOSOPHIE",
    "histoire-geographie": "HISTOIRE_GEO",
    "histoire geographie": "HISTOIRE_GEO",
    "histoire-geo": "HISTOIRE_GEO",
    # Décision utilisateur du 2026-09-07, qui inverse celle du 2026-08-11 ci-dessous :
    # Histoire et Géographie redeviennent deux Subject à part entière (voir
    # SUBJECT_FAMILIES dans catalog.models) - un élève qui filtre sur "Histoire" ne doit
    # plus voir une épreuve de pure Géographie et réciproquement. HISTOIRE_GEO n'est
    # conservé que pour les intitulés explicitement combinés ci-dessus
    # (histoire-geographie/histoire geographie/histoire-geo), constatés sur
    # bepc-histoire-2008/2017/2020-officiel-cameroun ("matiere": "Histoire-Géographie"
    # dans le JSON source) - le BEPC camerounais examine sinon le plus souvent Histoire
    # et Géographie séparément (bepc-histoire-2025-cameroun, bepc-geographie-2026-
    # cameroun), tout comme le Probatoire/BAC (bac-c-d-ti-geographie-2025-cameroun).
    "histoire": "HISTOIRE",
    "geographie": "GEOGRAPHIE",
    "anglais": "ANGLAIS",
    # Deuxième langue vivante, examinée au BEPC camerounais (voir bepc-espagnol-2018-
    # cameroun) - décision utilisateur du 2026-08-15 : Subject à part entière, jamais un
    # alias vers ANGLAIS, un élève filtrant sur "Anglais" n'ayant rien à faire d'une
    # épreuve d'espagnol. Contenu resté bloqué à l'ingestion jusqu'ici (5 fichiers en
    # erreur "Matière inconnue" à chaque run), faute d'exister au référentiel.
    "espagnol": "ESPAGNOL",
    # Nouvelle matière (décision utilisateur du 2026-09-07) - même traitement
    # qu'Espagnol/Dessin par le passé : Subject à part entière plutôt qu'un alias,
    # même en l'absence de contenu déjà ingéré sous ce nom.
    "allemand": "ALLEMAND",
    "economie": "ECONOMIE",
    "droit": "DROIT",
    "education civique": "EDUCATION_CIVIQUE",
    "education a la citoyennete": "EDUCATION_CIVIQUE",  # synonyme vu sur bepc-ecm-2026-cameroun ("ECM" = Éducation à la Citoyenneté et à la Morale).
    "education morale et civique": "EDUCATION_CIVIQUE",  # intitulé "EMC" des années 1990 (bepc-emc-1995/1996/1997-officiel-cameroun), même matière que ECM sous son ancienne dénomination.
    "ecm": "EDUCATION_CIVIQUE",  # sigle brut plutôt que l'intitulé développé, vu sur bepc-blanc-littoral-2026-cameroun.
    "litterature": "LITTERATURE",
    "litterature ou culture generale": "LITTERATURE",
    "litterature / culture generale": "LITTERATURE",  # variante slash-espacé, vue sur bac-c-e-lit-cg-2017-cameroun.
    "litterature/culture generale": "LITTERATURE",  # même variante, sans espaces, vue sur bac-c-d-e-ti-lit-cg-2025-corrige-cameroun.
    "litterature et culture generale": "LITTERATURE",  # variante "et" plutôt que "/", vue sur bac-c-d-e-ti-lit-cg-2023-cameroun.
    "culture generale": "LITTERATURE",
    "eps": "EPS",
    "education physique et sportive": "EPS",
    "education physique": "EPS",
    "informatique": "INFORMATIQUE",
    # Décision utilisateur du 2026-09-16, précisée le 2026-09-17 : en Série TI
    # (Probatoire et BAC), l'Informatique n'est PAS une seule épreuve généraliste - elle
    # se décompose systématiquement en trois épreuves distinctes au sein d'une même
    # session (voir SUBJECT_FAMILIES dans catalog.models). "informatique" seul ne
    # continue de résoudre vers le code combiné INFORMATIQUE que pour le BEPC et le
    # Bac C/D/E théorique (hors Série TI) - voir corriger_ti_informatique_split, qui a
    # repris les 10 Lesson de Série TI déjà en base à cette date (toutes CM) mal
    # rattachées à INFORMATIQUE.
    "programmation": "PROGRAMMATION",
    "systeme d'information": "SYSTEMES_INFORMATION",
    "systemes d'information": "SYSTEMES_INFORMATION",
    "systeme d information": "SYSTEMES_INFORMATION",
    "systemes d information": "SYSTEMES_INFORMATION",
    # "Informatique Théorique" est l'ancien intitulé officiel de cette même discipline
    # pour la Série TI (constaté sur bac-ti-informatique-theorique-2022-officiel-
    # cameroun, contenu UML/base de données/modélisation - rien de commun avec
    # l'Algorithmique et Programmation) - décision utilisateur du 2026-09-17.
    "informatique theorique": "SYSTEMES_INFORMATION",
    "reseaux, internet et securite informatique": "RESEAUX_SECURITE",
    "reseaux internet et securite informatique": "RESEAUX_SECURITE",
    "reseau, internet et securite informatique": "RESEAUX_SECURITE",
    "reseaux et securite informatique": "RESEAUX_SECURITE",
    "reseaux et internet": "RESEAUX_SECURITE",
    "securite informatique": "RESEAUX_SECURITE",
    # Matière officielle distincte au BEPC camerounais (une seule épreuve couvrant les
    # trois volets), à ne pas confondre avec PHYSIQUE_CHIMIE (Probatoire/BAC, qui ne
    # couvre pas la technologie) - décision utilisateur du 2026-08-08 : nouvelle Subject
    # dédiée plutôt qu'un alias vers PHYSIQUE_CHIMIE, pour ne pas perdre le volet
    # technologie dans l'intitulé affiché à l'élève.
    "physique-chimie-technologie": "PHYSIQUE_CHIMIE_TECH",
    # Matière examinée au BEPC camerounais (voir bepc-dessin-2026-cameroun) - décision
    # utilisateur du 2026-08-26 : Subject à part entière, même traitement que
    # Espagnol/Éducation Civique par le passé. Contenu resté bloqué à l'ingestion
    # jusqu'ici, faute d'exister au référentiel.
    "dessin": "DESSIN",
}

# Tolère l'ancienne nomenclature (A/C/D/F, "F" pour "TI") ET la nomenclature actuelle.
# "B" et "G" ne sont plus tolérés (SES et COM supprimées, voir docstring en tête de
# module) - une épreuve avec ces codes fait échouer l'ingestion explicitement plutôt
# que de résoudre vers une série qui n'existe plus.
# a1/a2 : pas un alias de "A" mais le code réel de deux séries distinctes en Côte
# d'Ivoire (Lettres-Philosophie / Lettres-Langues, voir Series pour ce pays) - le
# Cameroun n'a qu'une série "A" unique, donc ces deux nomenclatures coexistent sans
# collision (Series.code n'est unique que par pays).
SERIE_MAP = {
    "a": "A",
    "a1": "A1",
    "a2": "A2",
    # "b"/"ses" (Sciences Économiques et Sociales) retiré le 2026-08-19 : série
    # supprimée du référentiel (décision utilisateur), plus aucune cible.
    "c": "C",
    "d": "D",
    "e": "E",
    "f": "TI", "ti": "TI",
    # "g"/"com" (Techniques Commerciales, ex-COM) retiré le 2026-08-19 : ambigu depuis
    # l'introduction de Filiere, ne dit pas quelle spécialité STT (Comptabilité et
    # Gestion, Secrétariat/Bureautique, Commerce, Banque) - voir le docstring en tête
    # de module. Une épreuve "Série G" doit désormais être ingérée avec le code de
    # spécialité exact plutôt qu'une série ambiguë.
}

EXAMEN_MAP = {
    "bepc": Examen.BEPC,
    "bfem": Examen.BEPC,  # nom sénégalais du même niveau (fin de collège) - voir ExamenLabel.
    "probatoire": Examen.PROBATOIRE,
    "bac": Examen.BAC,
    "baccalaureat": Examen.BAC,  # nom complet en toutes lettres, vu sur bac-d-physique-chimie-1995/1996/1997 et bac-d-ti-physique-1999-2016-cameroun (60 fichiers) - _normalize() a déjà retiré l'accent sur "baccalauréat".
    # "bac_blanc" (vu sur bac-d-ti-maths-2026-cameroun, 5 fichiers) : le niveau réel est
    # bien BAC, le caractère "blanc"/non-officiel de l'épreuve est déjà porté par
    # `origine` (Origine.BLANC ou Origine.ETABLISSEMENT selon le cas) - un examen blanc
    # cible quand même un (examen, série) existant, il n'a jamais été un niveau d'examen
    # à part entière (voir Origine, docstring). Même défaut de mélange examen/origine que
    # "Cameroun" dans ORIGINE_MAP (_resolve_origine) : dérive stochastique de la
    # compétence, pas une ambiguïté réelle du référentiel.
    "bac_blanc": Examen.BAC,
    "bac blanc": Examen.BAC,
    "autre": Examen.AUTRE,
    # ATTENTION : aucun Cursus n'existe (ni n'est jamais seedé par seed_country) pour
    # Examen.AUTRE - un examen dont la valeur résout ici échouera toujours la résolution
    # de Cursus plus bas avec "Cursus introuvable", série ou pas. N'a jamais été exercé
    # en pratique par le corpus existant ; laissé tel quel (pas notre bug à corriger sans
    # cas réel pour en déterminer le bon niveau cible) plutôt que supprimé.
    "devoir surveille": Examen.AUTRE,
    # "devoir harmonisé" (vu sur terminale-c-maths-jean-tabi-2025-2026, 4 fichiers,
    # serie="C", etablissement="Collège Jean Tabi d'Étoudi ... Période 5") : contrairement
    # à "devoir surveille" juste au-dessus, il ne s'agit pas ici d'un niveau à part -
    # coefficient (7) et durée (4h) correspondent exactement au BAC C Maths, l'épreuve
    # cible bien le niveau Terminale C = BAC C, simplement organisée en interne par
    # l'établissement (déjà porté par origine="etablissement") plutôt que par l'examen
    # national - donc Examen.BAC ici, jamais Examen.AUTRE (qui échouerait la résolution
    # de Cursus, voir juste au-dessus).
    "devoir harmonise": Examen.BAC,
    "devoir_harmonise": Examen.BAC,
}

DIFFICULTE_MAP = {
    "faible": Difficulte.FAIBLE,
    "moyenne": Difficulte.MOYENNE,
    "elevee": Difficulte.ELEVEE,
}

NATURE_MAP = {
    "theorique": NatureEpreuve.THEORIQUE,
    "pratique": NatureEpreuve.PRATIQUE,
}

PARTIE_FRANCAIS_MAP = {
    "etude de texte": PartieEpreuveFrancais.ETUDE_TEXTE,
    "expression ecrite": PartieEpreuveFrancais.EXPRESSION_ECRITE,
    "orthographe": PartieEpreuveFrancais.ORTHOGRAPHE,
}

VARIANTE_SUJET_MAP = {
    "sujet 1": VarianteSujet.SUJET_1,
    "sujet1": VarianteSujet.SUJET_1,
    "sujet 2": VarianteSujet.SUJET_2,
    "sujet2": VarianteSujet.SUJET_2,
}

FILIERE_SERIE_A_MAP = {
    "abi": FiliereSerieA.ABI,
    "a4 bilingue": FiliereSerieA.ABI,
}

_FILIERE_SERIE_A_IN_SERIE_RE = re.compile(r"\babi\b", re.IGNORECASE)

ORIGINE_MAP = {
    "officiel": Origine.OFFICIEL,
    "officielle": Origine.OFFICIEL,  # accord grammatical variant ("épreuve officielle") vu sur bac-d-maths-1994/1995/1996/1997-cameroun.
    # "compilation" : sujet officiel réel, simplement transcrit depuis un ouvrage
    # compilant plusieurs sessions plutôt que depuis le sujet de l'année seule (vu sur
    # bac-c-maths-2015-cameroun) - décision utilisateur du 2026-08-03 : traiter comme
    # un sujet officiel classique, sans distinction visible pour l'élève.
    "compilation": Origine.OFFICIEL,
    "examen blanc": Origine.BLANC,
    "examen_blanc": Origine.BLANC,  # variante underscore, vu sur bac-c-maths-blanc-2003-cameroun - même dérive que "bac_blanc" dans EXAMEN_MAP.
    "blanc": Origine.BLANC,
    "sujet zero": Origine.SUJET_ZERO,  # _normalize() retire déjà l'accent ("zéro" -> "zero"), une seule entrée suffit.
    "etablissement": Origine.ETABLISSEMENT,
    "epreuve d'etablissement": Origine.ETABLISSEMENT,
    "autre": Origine.AUTRE,
}

REQUIRED_KEYS = [
    "epreuve_source", "numero_exercice", "matiere", "examen",
]


def _country_code_from_path(path):
    """
    Dérive le code pays (ex: "cm") du chemin sur disque : convention
    `ingest/<code_pays>/<epreuve>/...` (voir INGEST_DIR dans catalog.admin) - le
    sous-dossier direct sous le dossier littéralement nommé "ingest" porte le code
    pays. Fonctionne quel que soit le chemin passé à run_ingestion (dossier racine,
    sous-dossier pays, ou fichier unique) puisqu'on résout toujours le chemin absolu
    avant de chercher ce repère.
    """
    parts = path.resolve().parts
    lowered = [p.lower() for p in parts]
    if "ingest" not in lowered:
        return None
    idx = lowered.index("ingest")
    if idx + 1 >= len(parts):
        return None
    return parts[idx + 1]


# Ces trois résolveurs sont des lookups purs (même entrée -> même sortie tant que le
# référentiel Country/Subject/Series/Cursus ne change pas) mais sont appelés une fois
# PAR FICHIER ingéré - sur un dossier de plusieurs centaines de fichiers partageant
# tous le même pays/matière/cursus (ex. tout un lot "bac-c-d-chimie-*-cameroun"), ça
# fait des centaines de requêtes identiques pour la même réponse. lru_cache les rend
# gratuits après le premier appel ; `run_ingestion` vide le cache à chaque exécution
# (voir son propre commentaire) pour ne jamais servir une réponse obsolète d'un run
# précédent si le référentiel a changé entre-temps (ex. Subject ajouté depuis l'admin).
@lru_cache(maxsize=None)
def _resolve_country(code):
    if not code:
        raise IngestionError(
            "Impossible de déterminer le pays : le fichier ne se trouve pas sous "
            "un dossier ingest/<code_pays>/...",
        )
    try:
        return Country.objects.get(code__iexact=code)
    except Country.DoesNotExist:
        raise IngestionError(f"Pays inconnu : {code!r} - créez d'abord ce Country en base.")


@lru_cache(maxsize=None)
def _resolve_subject(matiere_raw, country):
    code = MATIERE_MAP.get(_normalize(matiere_raw))
    if not code:
        raise IngestionError(
            f"Matière inconnue : {matiere_raw!r}. Attendu l'une de : {sorted(set(MATIERE_MAP.values()))}",
        )
    try:
        return Subject.objects.get(code=code, country=country)
    except Subject.DoesNotExist:
        raise IngestionError(f"Subject introuvable en base pour le code {code!r} et le pays {country}.")


def _refuser_informatique_generique_en_serie_ti(subject, cursus_list):
    """
    Décision utilisateur du 2026-09-17 : en Série TI, l'Informatique se décompose toujours
    en Programmation, Systèmes d'Information ou Réseaux, Internet et Sécurité Informatique,
    jamais « Informatique » générique (réservé au BEPC et au BAC C/D/E théorique). Refuser
    à l'ingestion plutôt que de laisser une épreuve mal classée, à reprendre ensuite par
    `corriger_ti_informatique_split` (une seule occurrence constatée, 2026-09-19).
    """
    if subject.code != "INFORMATIQUE":
        return
    if any(c.series_id is not None and c.series.code == "TI" for c in cursus_list):
        raise IngestionError(
            "Série TI : matiere ne peut pas être « Informatique » - utiliser « Programmation », "
            "« Systèmes d'Information » ou « Réseaux, Internet et Sécurité Informatique » selon la "
            "discipline réellement examinée.",
        )


def _subject_family_codes(code):
    """
    Tous les codes de Subject d'une même famille (ex. {PHYSIQUE, CHIMIE,
    PHYSIQUE_CHIMIE}), à traiter comme "la même épreuve potentielle" pour un même
    epreuve_source - voir SUBJECT_FAMILIES et son usage dans ingest_exercise. Symétrique
    : PHYSIQUE et CHIMIE renvoient tous deux la famille complète (pas seulement
    {code, combiné}), sans quoi un exercice de Chimie ne retrouverait jamais le Lesson
    déjà créé par un exercice de Physique de la même épreuve - c'est précisément le
    mécanisme anti-fragmentation. Toujours au moins {code} lui-même : comportement
    inchangé pour toute matière hors famille (l'écrasante majorité des cas).
    """
    combined = SUBJECT_FAMILIES.get(code, code)
    members = {k for k, v in SUBJECT_FAMILIES.items() if v == combined}
    return {combined, *members} if members else {code}


@lru_cache(maxsize=None)
def _resolve_cursus_list(examen_raw, serie_raw, country):
    """
    Retourne la liste des Cursus concernés (plusieurs si l'épreuve est commune à
    plusieurs séries), toujours filtrée par `country` : Examen est un référentiel
    partagé entre pays, mais Subject/Series/(country, examen, série) sont propres à
    chaque pays - sans ce filtre, deux pays partageant un même (examen, série) (ex:
    BAC Série C ailleurs qu'au Cameroun) feraient lever *.MultipleObjectsReturned.

    Retourne un tuple (pas une liste) : la valeur est mise en cache par lru_cache et
    donc potentiellement partagée entre plusieurs appelants - un tuple immuable évite
    qu'un appelant qui la muterait par erreur ne corrompe silencieusement le cache
    pour tous les autres fichiers du même lot.
    """
    examen = EXAMEN_MAP.get(_normalize(examen_raw))
    if not examen:
        raise IngestionError(f"Examen inconnu : {examen_raw!r}. Attendu BEPC/Probatoire/BAC/Autre.")

    if examen == Examen.BEPC:
        try:
            return (Cursus.objects.get(country=country, examen=examen, series__isnull=True),)
        except Cursus.DoesNotExist:
            raise IngestionError(f"Cursus BEPC introuvable en base pour {country}.")

    serie_parts = _split_series(serie_raw)
    if not serie_parts:
        raise IngestionError(f"Série manquante pour un examen {examen_raw!r} qui en requiert une.")

    cursus_list = []
    for part in serie_parts:
        series_code = SERIE_MAP.get(_normalize(part))
        if not series_code:
            raise IngestionError(
                f"Série inconnue : {part!r} (dans {serie_raw!r}). Attendu l'une de : {sorted(set(SERIE_MAP.values()))}",
            )
        try:
            series = Series.objects.get(code=series_code, country=country)
            cursus_list.append(Cursus.objects.get(country=country, examen=examen, series=series))
        except (Series.DoesNotExist, Cursus.DoesNotExist):
            raise IngestionError(f"Cursus introuvable pour pays={country}, examen={examen_raw!r}, série={part!r}.")

    return tuple(cursus_list)


def build_lesson_title(
    subject, cursus_list, year, origine, etablissement,
    nature_epreuve="", partie_epreuve_francais="", variante_sujet="", filiere_serie_a="",
):
    """
    Titre affiché d'une épreuve, construit depuis ses champs structurés.

    Public (pas de préfixe `_`) et isolé ici plutôt que laissé en ligne dans
    `ingest_exercise` : le titre n'est calculé qu'à la CRÉATION du Lesson, donc toute
    correction ultérieure du cursus (voir _merge_series_from_folder_name, qui rattache
    après coup une épreuve aux séries que son JSON avait oubliées) laisse un titre
    périmé - "Chimie BAC C et D 2025" pour une épreuve désormais rattachée aussi à la
    Série E. La commande `corriger_series_et_reperes` rejoue donc cette fonction, qui
    doit rester l'unique source de vérité des deux côtés.

    Ne touche jamais au slug, lui : il est figé à la création (voir Lesson.slug) pour
    ne pas casser les URL déjà partagées et indexées.
    """
    # Regroupe par examen pour ne pas répéter le diplôme quand l'épreuve concerne
    # plusieurs séries : "BAC C et E" plutôt que "BAC - Série C / BAC - Série E".
    groups = {}
    for c in cursus_list:
        group = groups.setdefault(c.examen, {"examen_display": c.display_examen(), "series": []})
        if c.series:
            group["series"].append(c.series.code)
    cursus_label = " / ".join(
        f"{g['examen_display']} {_join_fr(g['series'])}" if g["series"] else g["examen_display"]
        for g in groups.values()
    )

    # Jamais de suffixe "Corrigé" : ce titre est affiché tel quel sur des surfaces qui
    # ne montrent QUE le sujet (fiche catalogue, page détail avant abonnement, en-tête
    # du PDF de sujet public - voir sujet_pdf.py) - y annoncer "Corrigé" est trompeur
    # pour un visiteur qui n'y voit que l'énoncé. Le statut "corrigé" se lit déjà via
    # lesson_type ailleurs.
    title = f"{subject.label} {cursus_label} {year or ''}".replace("  ", " ").strip()
    if origine == Origine.ETABLISSEMENT and etablissement:
        # Sans ça, deux épreuves d'établissements différents pour le même
        # (matière, cursus, année) produisent des titres identiques - indiscernables
        # dans le catalogue tant qu'on n'a pas cliqué dessus.
        title = f"{title} - {etablissement}"
    if origine == Origine.BLANC:
        # Sans ça, un examen blanc et le sujet officiel du même (matière, cursus,
        # année) produisent des titres identiques - indiscernables dans le catalogue
        # et dans l'admin tant qu'on n'a pas cliqué dessus. Seul BLANC est annoté :
        # OFFICIEL reste la forme "par défaut", déjà très majoritaire dans le corpus.
        title = f"{title} - Blanc"
    if origine == Origine.SUJET_ZERO:
        # Même motif que BLANC ci-dessus, catégorie distincte (voir Origine) : un
        # spécimen et le sujet officiel du même (matière, cursus, année) sont sinon
        # indiscernables.
        title = f"{title} - Sujet zéro"
    if nature_epreuve == NatureEpreuve.PRATIQUE:
        # Sans ça, l'épreuve pratique et sa jumelle théorique du même (matière, cursus,
        # année) produisent des titres identiques - indiscernables dans le catalogue et
        # dans l'admin tant qu'on n'a pas cliqué dessus. Seule la pratique est annotée :
        # la théorique reste la forme "par défaut", déjà majoritaire dans le corpus.
        title = f"{title} - Pratique"
    if partie_epreuve_francais:
        # Contrairement à Pratique (seule la minorité THEORIQUE/PRATIQUE annonce sa
        # forme, l'autre reste "par défaut") : ici les 3 valeurs sont annotées, aucune
        # n'est majoritaire dans le corpus Français au point de rester tacite.
        title = f"{title} - {PartieEpreuveFrancais(partie_epreuve_francais).label}"
    if variante_sujet:
        # Même logique que partie_epreuve_francais : aucun des deux sujets n'est plus
        # légitime que l'autre (distribués en alternance dans la même salle), donc les
        # deux sont annotés - contrairement à Pratique/Blanc où une seule forme l'est.
        title = f"{title} - {VarianteSujet(variante_sujet).label}"
    if filiere_serie_a:
        # Même motif que Pratique/Blanc : reste rattachée à la Série A (même Cursus),
        # seule la filière ABI est annotée - la Série A classique reste la forme "par
        # défaut", très largement majoritaire dans le corpus.
        title = f"{title} - {FiliereSerieA(filiere_serie_a).label}"
    return title


def _resolve_institution(data, origine, etablissement, country, cursus_list):
    """
    Organisme organisateur de l'épreuve. Dérivé du couple (pays, examen) pour un sujet
    officiel plutôt que recopié dans chacun des ~1200 JSON du corpus : pour un sujet
    officiel la valeur ne dépend de rien d'autre, donc la demander à la génération
    n'apporterait aucune information et multiplierait les occasions de divergence.

    Une valeur explicite dans le JSON l'emporte toujours - c'est le seul recours pour
    un examen blanc, dont l'organisateur (un lycée, une délégation régionale, le
    ministère) n'est déductible d'aucun autre champ. À défaut, une épreuve
    d'établissement est organisée par cet établissement lui-même. Tout le reste reste
    vide : mieux vaut ne rien afficher qu'afficher une institution inventée.
    """
    explicite = str(data.get("institution") or "").strip()
    if explicite:
        return explicite
    if origine == Origine.ETABLISSEMENT and etablissement:
        return etablissement
    if origine != Origine.OFFICIEL:
        return ""
    examen = cursus_list[0].examen if cursus_list else ""
    return institution_officielle(country.code, examen)


def _format_coefficient(coefficient_raw):
    """
    Le coefficient peut différer selon la série pour une même épreuve commune à
    plusieurs séries (ex: Maths coeff 7 en Série C, coeff 4 en Série E). La compétence
    transmet alors un objet {code_serie: coefficient} plutôt qu'une valeur unique -
    on le formate en chaîne lisible ("C : 7, E : 4") pour le champ d'affichage existant,
    sans changement de schéma. Une valeur simple (chaîne/nombre) passe telle quelle.
    """
    if isinstance(coefficient_raw, dict):
        return ", ".join(f"{serie} : {coef}" for serie, coef in coefficient_raw.items())
    return str(coefficient_raw or "")


def _resolve_origine(origine_raw, country):
    """Absent du JSON (compétence pas encore mise à jour, ou simplement omis pour un
    sujet officiel) -> OFFICIEL, le cas très largement majoritaire.

    Tolère aussi le nom du pays lui-même comme valeur de `origine` (ex. "Cameroun") :
    un défaut constaté à deux reprises sur des lots de physique-chimie distincts
    (bac-c-e-physique-2014/2015, puis bac-c(-e)-physique-2017 à 2022-cameroun, 36
    fichiers au total), toujours pour une épreuve par ailleurs authentiquement
    officielle - jamais rencontré pour un cas blanc/etablissement/autre, qui n'a aucune
    raison de coïncider avec un nom de pays. Sans dépendance dure à `country` : reste
    `None`-safe pour un éventuel appelant qui ne l'aurait pas encore résolu."""
    if not origine_raw:
        return Origine.OFFICIEL
    normalized = _normalize(origine_raw)
    origine = ORIGINE_MAP.get(normalized)
    if origine:
        return origine
    if country and normalized == _normalize(country.label):
        return Origine.OFFICIEL
    raise IngestionError(
        f"Origine inconnue : {origine_raw!r}. Attendu officiel/examen blanc/sujet zero/etablissement/autre.",
    )


def _resolve_nature_epreuve(nature_raw):
    """
    Champ optionnel (contrairement à `origine`/`examen`) : absent ou vide -> chaîne
    vide (pas de valeur, `Lesson.nature_epreuve` reste blank) plutôt qu'une erreur -
    la distinction Théorique/Pratique n'existe pas pour toutes les matières et la
    compétence ne doit jamais être forcée à en inventer une. Présent mais hors liste
    fermée -> erreur, même garde-fou que les autres champs contraints (une valeur
    "raisonnable" mais mal orthographiée doit être corrigée à la source, pas
    silencieusement ignorée)."""
    if not nature_raw:
        return ""
    nature = NATURE_MAP.get(_normalize(nature_raw))
    if not nature:
        raise IngestionError(f"Nature d'épreuve inconnue : {nature_raw!r}. Attendu théorique/pratique (ou absent).")
    return nature


def _resolve_partie_epreuve_francais(matiere_raw, partie_raw):
    """Champ optionnel, propre au Français (voir Lesson.partie_epreuve_francais).
    Deux sources, `partie_raw` (champ dédié explicite) prioritaire sur `matiere_raw` :
    une partie du corpus Français déclare déjà directement "Étude de texte"/
    "Expression écrite"/"Orthographe" comme valeur de `matiere` plutôt que "Français"
    (voir MATIERE_MAP) - cette info était jusqu'ici résolue vers la Subject FRANCAIS
    puis perdue. `partie_raw` présent mais hors liste fermée -> erreur (même contrat
    que _resolve_nature_epreuve) ; `matiere_raw` hors liste -> simplement ignoré, ce
    n'est pas son rôle de porter cette info pour la quasi-totalité des matières."""
    if partie_raw:
        partie = PARTIE_FRANCAIS_MAP.get(_normalize(partie_raw))
        if not partie:
            raise IngestionError(
                f"Partie d'épreuve de Français inconnue : {partie_raw!r}. "
                "Attendu étude de texte/expression écrite/orthographe (ou absent).",
            )
        return partie
    return PARTIE_FRANCAIS_MAP.get(_normalize(matiere_raw), "")


def _resolve_variante_sujet(variante_raw):
    """
    Champ optionnel (voir Lesson.variante_sujet) : absent ou vide -> chaîne vide, la
    grande majorité des épreuves n'ayant qu'une seule version. Présent mais hors liste
    fermée -> erreur, même garde-fou que _resolve_nature_epreuve.
    """
    if not variante_raw:
        return ""
    variante = VARIANTE_SUJET_MAP.get(_normalize(variante_raw))
    if not variante:
        raise IngestionError(f"Variante de sujet inconnue : {variante_raw!r}. Attendu sujet 1/sujet 2 (ou absent).")
    return variante


def _resolve_filiere_serie_a(filiere_raw, serie_raw):
    """Champ optionnel, propre à la Série A (voir Lesson.filiere_serie_a). Deux
    sources, `filiere_raw` (champ dédié explicite) prioritaire sur `serie_raw` : le
    corpus existant écrit déjà "A-ABI" directement dans `serie` plutôt que dans un
    champ dédié (imprimé ainsi sur l'épreuve source) - ce token, comme un nom de
    fichier qui le reprend explicitement, compte comme une indication explicite (même
    contrat que nature_epreuve/partie_epreuve_francais). `filiere_raw` présent mais
    hors liste fermée -> erreur (même garde-fou que _resolve_variante_sujet)."""
    if filiere_raw:
        filiere = FILIERE_SERIE_A_MAP.get(_normalize(filiere_raw))
        if not filiere:
            raise IngestionError(f"Filière de Série A inconnue : {filiere_raw!r}. Attendu ABI/A4 Bilingue (ou absent).")
        return filiere
    if _FILIERE_SERIE_A_IN_SERIE_RE.search(str(serie_raw or "")):
        return FiliereSerieA.ABI
    return ""


def _validate_pays_matches_country(pays_raw, country):
    """
    SKILL.md (mode automatisation ET mode cours) documente désormais un champ `pays`
    (code ISO 3166-1 alpha-2 minuscule) censé toujours reproduire le pays réellement
    résolu - le segment `<code_pays>` du dossier `ingest/<code_pays>/` pour un
    exercice, hérité de l'épreuve source pour un cours (voir ingest_cours). Ce module
    continue de résoudre `country` uniquement depuis cette source structurelle, jamais
    depuis ce champ (raison documentée en tête de fichier : la compétence ne fournissait
    pas ce champ à l'origine, et le dossier reste la source de vérité même maintenant
    qu'elle le fait) - `pays` sert donc de signal de contrôle redondant, pas de valeur
    à consommer.

    Absent (fichier généré avant l'ajout du champ à la compétence, ou par une version
    du skill qui ne le fournit pas encore) : aucune vérification, comportement inchangé
    - c'est le cas de tout le corpus `ingest/` existant au moment où ce contrôle a été
    ajouté. Présent et incohérent avec le pays réellement résolu (ex. contenu déposé
    dans le mauvais dossier, ou dérive du même type que celle documentée pour `origine`) :
    erreur explicite plutôt qu'une incohérence silencieuse entre le pays affiché et le
    pays réel de l'exercice/cours.
    """
    if not pays_raw:
        return
    normalized = _normalize(pays_raw)
    if normalized != country.code.lower():
        raise IngestionError(
            f"Le champ 'pays' ({pays_raw!r}) ne correspond pas au pays résolu "
            f"({country.code.lower()!r}, déduit du dossier ingest/<code_pays>/ pour un "
            "exercice, ou hérité de l'épreuve source pour un cours).",
        )


def _cours_sibling_rappel_id_map(source_dir):
    """
    Index {cours_id: rappel_id} construit à partir des fichiers cours déjà présents
    dans `source_dir` - toujours le même dossier que l'exercice source (voir
    run_ingestion, qui ingère systématiquement tous les exercices d'un dossier avant
    ses cours), donc ces fichiers existent déjà sur disque même si pas encore en base.

    Filet de secours pour un défaut constaté à deux reprises sur des lots de
    physique-chimie distincts (bac-c-e-physique-2014/2015, puis bac-c(-e)-physique-2017
    à 2022-cameroun, 36 fichiers au total à ce jour) : une entrée `rappels_de_methode`
    perd son `id` (requis, external_id du RappelDeMethode) et ne laisse que `cours_id` -
    un identifiant de bookkeeping interne à la compétence, normalement optionnel et
    jamais lu par ailleurs dans ce module (voir _link_rappels_lies plus bas, qui calcule
    le lien Cours -> RappelDeMethode côté base, jamais depuis ce JSON). Quand le cours
    correspondant a déjà été généré, son propre fichier contient la valeur perdue dans
    `source.rappel_id` (l'exercice source ne peut être faux : c'est de là que ce cours a
    été dérivé) - on la relit ici plutôt que de la deviner.

    Parcourt TOUS les `*.json` du dossier (pas seulement `*_cours_*.json`) et filtre par
    contenu (présence de `cours_id` + `source.rappel_id`), comme run_ingestion le fait
    déjà pour distinguer cours/exercice - même raison : le séparateur entre "cours" et
    le slug n'est pas fiable (`_cours_bijection-...` vu sur la plupart du corpus, mais
    `_cours-bijection-...` avec un tiret vu sur bac-c-maths-1985-1992-cameroun, 5
    dossiers, qui faisait manquer ces fichiers entièrement - le filtre par contenu
    ci-dessous ne dépend d'aucune convention de nommage).
    """
    mapping = {}
    for cours_file in Path(source_dir).glob("*.json"):
        try:
            cours_data = json.loads(cours_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        cours_id = cours_data.get("cours_id")
        rappel_id = (cours_data.get("source") or {}).get("rappel_id")
        if cours_id and rappel_id:
            mapping[cours_id] = rappel_id
    return mapping


def _lesson_from_source_dir(source_dir):
    """
    Retrouve la Lesson d'une épreuve depuis son dossier sur disque, en relisant le
    `epreuve_source` déclaré par les fichiers exercices qui y vivent - la valeur exacte
    avec laquelle ingest_exercise a créé cette Lesson, jamais un slug reconstruit depuis
    le nom du dossier.

    Dernier recours pour rattacher un cours dont le rappel source est introuvable (voir
    ingest_cours) : sur les 87 fichiers concernés, seuls 11 portent `source.epreuve_source`,
    mais les 5 dossiers ont chacun un et un seul `epreuve_source` côté exercices - le
    dossier identifie donc l'épreuve sans ambiguïté là où le JSON du cours ne dit rien.

    Renvoie None dès qu'il y a le moindre doute (dossier inconnu, aucun exercice lisible,
    ou plusieurs épreuves mélangées dans le même dossier) : un cours mal rattaché serait
    pire qu'un cours non ingéré.
    """
    if not source_dir:
        return None

    sources = set()
    for sibling in Path(source_dir).glob("*.json"):
        try:
            raw = json.loads(sibling.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for item in raw if isinstance(raw, list) else [raw]:
            # Même filtre par contenu que run_ingestion pour distinguer exercice et cours
            # (voir _cours_sibling_rappel_id_map) : aucune convention de nommage.
            if isinstance(item, dict) and item.get("epreuve_source") and "sections" not in item:
                sources.add(item["epreuve_source"])

    if len(sources) != 1:
        return None

    lessons = Lesson.objects.filter(epreuve_source=sources.pop())
    country_code = _country_code_from_path(Path(source_dir))
    if country_code:
        lessons = lessons.filter(cursus__country__code__iexact=country_code)
    # Plusieurs Lesson peuvent partager un même epreuve_source (une épreuve mixte
    # Physique/Chimie donne une Lesson par matière, voir ingest_exercise) : elles
    # dérivent alors du même sujet, donc même pays et même cursus - la première suffit
    # pour ce dont ingest_cours a besoin.
    return lessons.first()


_CHOIX_PREFIX_RE = re.compile(r"^\s*([A-Za-z])\)\s*(.*)$", re.DOTALL)


def _normalize_qcm_choix(choix_raw, reponse_correcte_raw):
    """
    Normalise `choix`/`reponse_correcte` vers le contrat interne attendu par Question
    (`choix`: [{"lettre": ..., "texte": "..."}], `reponse_correcte`: une lettre seule
    qui identifie un des `choix`) - correction-experte produit ce couple sous
    plusieurs formes observées en production, toutes légitimes :
    - `choix` en objets {lettre, texte} (le contrat documenté) - la lettre n'est pas
      forcément un caractère unique : un QCM d'appariement colonne A/colonne B utilise
      des codes composés ("b1", "b2", "b3"...), pas seulement a/b/c/d.
    - `choix` en chaînes "x) texte" (sans objet) - la lettre est alors extraite du
      préfixe.
    - `choix` en chaînes brutes sans aucune lettre (ex. Vrai/Faux : ["Vrai", "Faux"])
      - une lettre est alors synthétisée par position (a, b, c...), le texte reste la
      chaîne telle quelle.
    - `reponse_correcte` comme le texte complet du bon choix plutôt que sa seule
      lettre (constaté en production : la lettre seule est censée tenir dans
      `reponse_correcte` - max_length=10 - un texte complet dépasse largement et lève
      un DataError Postgres). Sans cette normalisation, la comparaison de correction
      (QuizAnswer.est_correcte) échouerait aussi silencieusement pour toute question
      ainsi mal formée : reponse_choisie est toujours une lettre (le bouton cliqué),
      jamais comparable à une phrase complète.
    """
    choix = []
    for index, item in enumerate(choix_raw or []):
        if isinstance(item, dict):
            lettre = str(item.get("lettre") or "").strip().lower()
            texte = _strip_em_dash(str(item.get("texte") or ""))
        else:
            match = _CHOIX_PREFIX_RE.match(str(item))
            if match:
                lettre, texte = match.group(1).lower(), _strip_em_dash(match.group(2).strip())
            else:
                lettre, texte = chr(ord("a") + index), _strip_em_dash(str(item).strip())
        choix.append({"lettre": lettre, "texte": texte})

    reponse_correcte_raw = str(reponse_correcte_raw or "").strip()
    lettres = {c["lettre"] for c in choix}

    if reponse_correcte_raw.lower() in lettres:
        # Correspondance directe avec une lettre de choix - couvre aussi bien "a" que
        # "b3" (QCM d'appariement), pas seulement les lettres à un caractère.
        reponse_correcte = reponse_correcte_raw.lower()
    else:
        match = _CHOIX_PREFIX_RE.match(reponse_correcte_raw)
        if match:
            reponse_correcte = match.group(1).lower()
        else:
            # Repli : reponse_correcte donné comme le texte d'un choix (sans lettre ni
            # préfixe "x) "), à faire correspondre par contenu plutôt que par position.
            texte_normalise = _strip_em_dash(reponse_correcte_raw)
            matching = next((c for c in choix if c["texte"] == texte_normalise), None)
            if not matching:
                raise IngestionError(
                    f"reponse_correcte ne correspond à aucune lettre ni à aucun texte de choix : {reponse_correcte_raw!r}",
                )
            reponse_correcte = matching["lettre"]

    return choix, reponse_correcte


def _get_or_create_tags(names):
    tags = []
    for name in names or []:
        name = _strip_em_dash(name).strip()
        if not name:
            continue
        tags.append(_resolve_or_create_tag(name))
    return tags


def _resolve_or_create_tag(name):
    """
    Correspondance exacte d'abord (Tag.name est sensible à la casse en base), repli
    insensible à la casse ensuite - deux ingestions indépendantes qui recopient le
    même thème avec une casse différente ("Alcanes" / "alcanes") ne doivent pas
    créer deux Tag distincts pour la même notion (même pattern que
    quiz.ingestion._resolve_theme, qui avait déjà ce repli).
    """
    try:
        return Tag.objects.get(name=name)
    except Tag.DoesNotExist:
        pass
    candidats = list(Tag.objects.filter(name__iexact=name))
    if len(candidats) == 1:
        return candidats[0]
    if len(candidats) > 1:
        raise IngestionError(f"Plusieurs Tag correspondent à {name!r} à la casse près - ambigu, à corriger à la main.")
    # Variante aux accents/pluriel près d'un Tag existant ("elimination" -> "élimination") :
    # réutilisée plutôt que recréée (voir catalog.tunnel.find_tag_variant).
    from .tunnel import find_tag_variant

    variante = find_tag_variant(name)
    if variante is not None:
        return variante
    tag, _ = Tag.objects.get_or_create(name=name)
    return tag


def _format_alternatives(values, limit=25):
    """
    Rend une liste de valeurs valides lisible dans un message d'erreur, tronquée pour
    ne jamais transformer une IngestionError en mur de texte (le référentiel Maths
    compte 14 couples (classe, série) et jusqu'à une vingtaine de modules par couple).
    """
    values = list(values)
    shown = ", ".join(repr(v) for v in values[:limit])
    if len(values) > limit:
        shown += f", ... (+{len(values) - limit})"
    return shown or "aucune"


def _resolve_savoir_officiel(raw, subject):
    """
    Référence optionnelle vers le référentiel programme officiel (programme.Module/
    Savoir) - {"classe": "1ere", "serie_label": "C-E", "module_numero": "21",
    "savoir_numero": "II"} ("serie_label" vide pour le BEPC, voir Module.serie_label).
    Absent -> None, comportement inchangé pour tout appelant qui ne fournit pas ce
    champ. Présent mais non résolvable -> IngestionError : mieux vaut échouer fort
    qu'ignorer en silence une référence fausse fournie par un skill.

    Les valeurs sont exigées à l'identique du référentiel, jamais rapprochées de façon
    approximative - et c'est délibéré. La tentation est grande de normaliser la série
    d'une épreuve ("C, D" tel qu'écrit dans le JSON) vers le `serie_label` du module
    ("C-D-E"), puisque c'est le décalage qui fait le plus souvent échouer une référence.
    Mais ce rapprochement n'est pas une simple différence d'écriture : une épreuve
    commune à plusieurs séries relève parfois de DEUX modules officiels distincts (en
    Maths Tle, la série C vit dans le module "C-E" et la D dans le module "D"), et
    "C, D" n'y désigne alors aucun module en particulier. Deviner reviendrait à en
    choisir un en silence - exactement le mode d'échec que cette fonction existe pour
    empêcher. Le décalage se règle donc en amont, en lisant le fixture (voir la section
    savoir_officiel du skill correction-experte) ; ici on se contente de rendre l'échec
    actionnable en listant les valeurs réellement disponibles.
    """
    if not raw:
        return None
    if not isinstance(raw, dict):
        raise IngestionError(f"savoir_officiel doit être un objet : {raw!r}")

    module_numero = str(raw.get("module_numero") or "").strip()
    if not module_numero:
        raise IngestionError("savoir_officiel.module_numero manquant.")
    classe = str(raw.get("classe") or "").strip()
    serie_label = str(raw.get("serie_label") or "").strip()
    savoir_numero = str(raw.get("savoir_numero") or "").strip()

    try:
        module = Module.objects.get(subject=subject, classe=classe, serie_label=serie_label, numero=module_numero)
    except Module.DoesNotExist:
        # Deux impasses très différentes derrière le même DoesNotExist, et les
        # distinguer change ce qu'il y a à corriger : soit le couple (classe, série)
        # n'existe pas du tout pour cette matière (erreur de `serie_label`, cas le plus
        # fréquent - voir la docstring), soit il existe et c'est le numéro de module qui
        # est faux. On liste les valeurs valides du niveau qui coince, jamais les deux :
        # noyer le bon indice sous l'autre liste rendrait le message inutilisable.
        combos = (
            Module.objects.filter(subject=subject, classe=classe, serie_label=serie_label).exists()
        )
        if combos:
            numeros = (
                Module.objects.filter(subject=subject, classe=classe, serie_label=serie_label)
                .order_by("ordre").values_list("numero", flat=True)
            )
            detail = f"Numéros de module disponibles pour ce couple : {_format_alternatives(numeros)}."
        else:
            disponibles = sorted(
                {
                    f"classe={c!r} serie_label={s!r}"
                    for c, s in Module.objects.filter(subject=subject).values_list("classe", "serie_label")
                }
            )
            detail = f"Couples (classe, serie_label) disponibles pour cette matière : {_format_alternatives(disponibles)}."
        raise IngestionError(
            f"savoir_officiel : aucun module officiel pour matière={subject.code!r} classe={classe!r} "
            f"serie_label={serie_label!r} numero={module_numero!r}. {detail}",
        )
    try:
        return module.savoirs.get(numero=savoir_numero)
    except Savoir.DoesNotExist:
        numeros = module.savoirs.order_by("ordre").values_list("numero", flat=True)
        raise IngestionError(
            f"savoir_officiel : le module {module} n'a pas de savoir numéro {savoir_numero!r}. "
            f"Numéros disponibles dans ce module : {_format_alternatives(numeros)}.",
        )
    except Savoir.MultipleObjectsReturned:
        # Ne devrait jamais arriver (numéro cense identifier un savoir de façon unique
        # au sein d'un module) - mais un doublon de numérotation dans le fixture source
        # (voir programme_officiel_cm_maths.json, incident du 2026-08-12 : "III." utilisé
        # deux fois dans le même module) doit échouer proprement ici plutôt que de laisser
        # remonter un Savoir.MultipleObjectsReturned brut jusqu'à l'appelant du skill.
        raise IngestionError(
            f"savoir_officiel : plusieurs savoirs numéro {savoir_numero!r} dans le module {module} - "
            "doublon de numérotation à corriger dans le fixture programme officiel.",
        )


def _link_tags_to_savoir(tags, savoir):
    """
    Best-effort, jamais bloquant pour l'ingestion elle-même : lie chaque Tag résolu au
    Savoir officiel visé, seulement s'il n'a pas déjà de rattachement (jamais
    d'écrasement d'un mapping déjà validé à la main - voir Tag.savoir_officiel). Effet
    de bord volontaire : chaque contenu neuf généré avec ce champ fait progresser le
    mapping des tags historiques vers le référentiel officiel, sans attendre la passe
    de curation dédiée pour ce tag précis.
    """
    if not savoir:
        return
    for tag in tags:
        if tag.savoir_officiel_id is None:
            tag.savoir_officiel = savoir
            tag.save(update_fields=["savoir_officiel"])


# Largeur maximale d'une figure une fois compressée - un scan de manuel ou une photo
# de tableau arrive souvent à une résolution largement supérieure à ce qu'un écran de
# lecture peut afficher utilement ; au-delà, ce ne sont que des octets gaspillés sur
# une connexion mobile instable (voir l'audit UX, reco 5.2, et la stratégie hors-ligne
# déjà en place côté frontend qui met précisément ces figures en cache le plus
# longtemps de tout le contenu - vite_config.ts, CacheFirst sur /media/figures/).
_FIGURE_MAX_WIDTH = 1200
_FIGURE_WEBP_QUALITY = 82


def _compress_figure_image(raw_bytes, filename):
    """
    Reconvertit une figure en WebP et la redimensionne à _FIGURE_MAX_WIDTH si besoin,
    avant stockage - jamais à la volée (voir la docstring de _attach_figures et
    l'audit UX, reco 5.2). Ne redimensionne jamais à la hausse une image déjà plus
    petite que la cible.

    En cas d'échec (fichier corrompu, format non reconnu par Pillow) : retombe sur les
    octets et le nom de fichier d'origine plutôt que de faire échouer l'ingestion de
    tout l'exercice pour une seule figure - même philosophie que le reste de cette
    fonction (voir illisibles_indispensables dans _attach_figures) : la
    qualité d'une figure est un problème pour un humain à trancher plus tard, jamais
    un motif de blocage automatique.
    """
    try:
        image = Image.open(BytesIO(raw_bytes))
        image.load()
    except (UnidentifiedImageError, OSError):
        return raw_bytes, filename

    if image.mode not in ("RGB", "L"):
        # RGBA/P/LA (transparence, palette) : aplati sur fond blanc - une figure de
        # cours (schéma, graphique, tableau scanné) n'a aucune raison d'avoir besoin
        # d'un canal alpha, et le WebP avec perte utilisé ici ne le conserverait pas
        # de toute façon.
        rgba = image.convert("RGBA")
        background = Image.new("RGB", rgba.size, "white")
        background.paste(rgba, mask=rgba.split()[-1])
        image = background

    if image.width > _FIGURE_MAX_WIDTH:
        ratio = _FIGURE_MAX_WIDTH / image.width
        image = image.resize((_FIGURE_MAX_WIDTH, round(image.height * ratio)), Image.LANCZOS)

    buffer = BytesIO()
    image.save(buffer, format="WEBP", quality=_FIGURE_WEBP_QUALITY)
    return buffer.getvalue(), f"{Path(filename).stem}.webp"


def _attach_figures(exercise, figures_data, source_dir):
    """
    Crée un Figure par entrée de `figures_data`, en lisant le PNG depuis `source_dir`
    (le dossier du fichier JSON source - voir SKILL.md "Traitement des figures et
    images" : les PNG sont livrés à côté des JSON de l'épreuve, jamais encodés dans
    le JSON). Réécrit ensuite chaque occurrence du nom de fichier original par l'URL
    réelle du fichier stocké, pour que le placeholder `![fig-N](nom_original.png)`
    pointe vers une image effectivement servable.

    Appelée après création des Question de `exercise` (voir ingest_exercise) : une
    figure peut être partagée par plusieurs sous-questions (ex. un graphique lu par
    la question 1 et exploité de nouveau en question 3), donc le placeholder est
    recherché dans le texte de chaque Question plutôt que dans un unique champ comme
    avant la scission en sous-questions - ainsi que dans enonce_intro_markdown, qui
    peut lui aussi référencer une figure partagée en préambule.
    """
    if not figures_data:
        return

    if source_dir is None:
        raise IngestionError("figures présentes dans le JSON mais aucun dossier source fourni pour résoudre les PNG.")

    questions = list(exercise.questions.all())
    illisibles_indispensables = []

    for fig_data in figures_data:
        if isinstance(fig_data, str):
            # Constaté sur bac-c-physique-2024/bac-d-physique-2019/2022-cameroun (9
            # fichiers) : la compétence a émis l'id de la figure comme simple chaîne
            # au lieu de l'objet {"id", "fichier", ...} attendu - même défaut de forme
            # que le cas "sans fichier" ci-dessous (aucun de ces id n'est référencé par
            # un placeholder ![...] dans enonce/corrige_markdown, vérifié corpus-wide),
            # donc traité identiquement : ignoré à l'ingestion plutôt que de faire
            # échouer tout l'exercice pour une figure qui n'était de toute façon pas
            # exploitable telle quelle.
            continue
        filename = fig_data.get("fichier")
        fig_id = fig_data.get("id")
        if not fig_id:
            raise IngestionError(f"Figure incomplète (id manquant) : {fig_data!r}")
        if not filename:
            # Cas fréquent sur les épreuves anciennes scannées (voir bac-d-ti-physique
            # 1999-2016, probatoire-c-d-chimie 2008/2011/2013) : la compétence décrit
            # une figure qu'elle sait avoir existé sur le sujet source (id + type +
            # description) mais n'a pas pu en extraire une image exploitable - jamais
            # référencée par un placeholder `![...]` dans enonce/corrige_markdown
            # (vérifié corpus-wide, 2026-08 : aucun des cas rencontrés ne s'appuie sur
            # l'image pour la lisibilité du texte), donc rien n'est perdu à l'ignorer
            plutôt qu'à faire échouer l'ingestion de tout l'exercice pour ça. Ce sont
            # en pratique des tracés que le corrigé construit (diagramme de Fresnel,
            # courbe à tracer...) plutôt que des images perdues du sujet : aucune
            # trace dans les incertitudes (172 notes purgées le 2026-09-19).
            continue

        image_path = source_dir / filename
        if not image_path.is_file():
            raise IngestionError(f"Fichier de figure introuvable : {image_path}")

        try:
            page_source = int(fig_data["page_source"]) if fig_data.get("page_source") not in (None, "") else None
        except (TypeError, ValueError):
            page_source = None

        indispensable = bool(fig_data.get("indispensable", True))
        lisibilite = str(fig_data.get("lisibilite") or "")
        origine = OrigineFigure.CORRIGE if _normalize(fig_data.get("origine_figure")) == "corrige" else OrigineFigure.ENONCE

        compressed_bytes, stored_filename = _compress_figure_image(image_path.read_bytes(), filename)

        figure = Figure.objects.create(
            exercise=exercise,
            external_id=fig_id,
            image=ContentFile(compressed_bytes, name=stored_filename),
            page_source=page_source,
            type_figure=_strip_em_dash(str(fig_data.get("type") or "")),
            legende=_strip_em_dash(str(fig_data.get("legende") or "")),
            indispensable=indispensable,
            lisibilite=lisibilite,
            origine=origine,
        )

        # Le placeholder `![fig-N](nom_original.png)` livré par correction-experte
        # porte l'id de la figure en texte alternatif, jamais une description utile à
        # un lecteur d'écran (voir l'audit UX, reco 6.1) - remplacé ici par la légende
        # déjà saisie par la compétence, ou à défaut le type de figure, plutôt que de
        # laisser "fig-1" tel quel. Repli sur le remplacement brut du seul nom de
        # fichier si jamais le placeholder ne respecte pas exactement cette convention
        # (contenu plus ancien, ou variation de rédaction) - mieux vaut un lien
        # fonctionnel sans alternative améliorée qu'un lien cassé.
        alt_text = figure.legende or figure.type_figure or "Figure du corrigé"
        placeholder_re = re.compile(r"!\[" + re.escape(fig_id) + r"\]\(" + re.escape(filename) + r"\)")
        replacement = f"![{alt_text}]({figure.image.url})"

        for question in questions:
            enonce = placeholder_re.sub(replacement, question.enonce_markdown).replace(filename, figure.image.url)
            corrige = placeholder_re.sub(replacement, question.corrige_markdown).replace(filename, figure.image.url)
            if enonce != question.enonce_markdown or corrige != question.corrige_markdown:
                question.enonce_markdown = enonce
                question.corrige_markdown = corrige
                question.save(update_fields=["enonce_markdown", "corrige_markdown", "updated_at"])

        intro = placeholder_re.sub(replacement, exercise.enonce_intro_markdown).replace(filename, figure.image.url)
        if intro != exercise.enonce_intro_markdown:
            exercise.enonce_intro_markdown = intro
            exercise.save(update_fields=["enonce_intro_markdown", "updated_at"])

        if indispensable and _normalize(lisibilite) == "illisible":
            illisibles_indispensables.append(fig_id)

    # Filet de sécurité mécanique pour la règle SKILL.md ("figure indispensable et
    # illisible -> incertitude majeure, mentionnée en premier") : la compétence est
    # censée le signaler elle-même dans son JSON, mais on ne s'y fie pas à 100% - même
    # logique que la protection mécanique déjà en place pour l'em dash.
    if illisibles_indispensables:
        note = (
            f"Figure(s) indispensable(s) mais illisible(s) : {', '.join(illisibles_indispensables)} - "
            "questions dépendantes non fiables."
        )
        if note not in exercise.incertitudes:
            exercise.incertitudes = [note, *exercise.incertitudes]
            exercise.save(update_fields=["incertitudes"])


def ingest_exercise(data, source_dir=None, force=False):
    """
    Ingère un objet JSON (un exercice). Retourne (exercise, created).
    Lève IngestionError si les champs de classification ne peuvent pas être résolus.
    Idempotent par défaut : si un Exercise existe déjà pour ce (lesson, numero_exercice),
    il n'est jamais modifié - un ré-import ne recouvre pas une correction manuelle faite
    depuis.

    `force=True` outrepasse volontairement cette protection : l'Exercise existant est
    supprimé (cascade propre sur Question/Figure/RappelDeMethode - voir leurs
    `on_delete`) puis recréé depuis `data`, exactement comme une première ingestion.
    Réservé à un ré-import délibéré après correction du JSON source (voir l'action
    admin sur ExerciseAdmin) - jamais utilisé par `run_ingestion`/la tâche planifiée,
    qui doivent conserver le comportement idempotent par défaut. Deux liens externes à
    l'Exercise supprimé sont préservés à travers la suppression/recréation : RappelDeMethode
    → Cours (par `external_id`) et quiz.CompetenceItem.source_exercises (M2M, par id
    d'item) - sans quoi ce dernier disparaît silencieusement, sans erreur.

    Valide et compile automatiquement : l'Exercise et le Lesson passent directement en
    VALIDE, et le Lesson est recompilé à chaque nouvel exercice ingéré - le contenu est
    donc immédiatement visible côté frontend, sans étape de validation manuelle. Le champ
    `statut` reste modifiable après coup (admin) pour retirer un contenu qui s'avère
    incorrect - ce n'est plus un verrou de publication, seulement un filtre a posteriori.

    `source_dir` : dossier où chercher les fichiers PNG référencés par `data["figures"]`
    (voir _attach_figures) - toujours le dossier du fichier JSON source, transmis par
    run_ingestion. Sert aussi, désormais, à déterminer le pays de l'épreuve (voir
    _country_code_from_path) : obligatoire même sans figures dans le JSON.

    `data["questions"]` porte la décomposition en sous-questions atomiques (voir
    catalog.models.Question) - toujours au moins une entrée, même pour un exercice à
    une seule question. enonce_markdown/corrige_markdown de l'Exercise ne sont plus lus
    depuis le JSON : ils sont compilés depuis les Question créées (voir
    Exercise.compile_from_questions), appelée en toute fin de cette fonction.
    """
    data, was_repaired = _repair_double_json_escaping(data)
    data, had_missing_separators = _repair_missing_matrix_row_separators(data)
    data, had_glued_hline = _repair_glued_hline(data)
    data, had_narrow_columns = _repair_narrow_array_columns(data)

    missing = [key for key in REQUIRED_KEYS if not data.get(key)]
    if missing:
        raise IngestionError(f"Champs obligatoires manquants : {missing}")

    if not data.get("questions"):
        raise IngestionError("'questions' est requis et doit contenir au moins une entrée.")

    data, had_missing_heading = _repair_missing_exercise_heading(data)
    # Après le filet ci-dessus, jamais avant : un repère tout juste injecté est déjà en
    # tête d'intro (voir _repair_missing_exercise_heading), rien à repositionner pour
    # lui - seul un repère PRÉEXISTANT mais mal placé (après un préambule propre à
    # l'exercice, pas seulement un chapeau d'épreuve) doit encore être déplacé.
    data, had_misplaced_heading = _reposition_trailing_exercise_reference(data)
    # Avant les deux dédoublonnages suivants, jamais après : un repère que l'on vient de
    # ramener en tête d'intro peut désormais faire doublon avec celui de la première
    # question (cas que seul _dedupe_exercise_heading sait traiter, voir sa docstring).
    data, had_duplicate_heading = _dedupe_exercise_heading(data)
    # Cas frère de _dedupe_exercise_heading, jamais traité par elle (voir sa
    # docstring) : le repère répété n'est pas en tête d'intro mais en DERNIÈRE ligne
    # (une fiche d'identité/un chapeau partagé précède), et n'est répété qu'en tête de
    # la PREMIÈRE question - voir _dedupe_trailing_exercise_reference.
    data, had_trailing_duplicate_heading = _dedupe_trailing_exercise_reference(data)

    # Relu APRÈS les rustines, jamais avant : _dedupe_exercise_heading/
    # _dedupe_trailing_exercise_reference réécrivent des entrées de `questions` (les
    # précédentes ne touchaient que l'intro), et une référence capturée plus haut
    # pointerait encore sur la liste d'origine - les corrections seraient alors
    # silencieusement perdues à la création des Question.
    questions_data = data["questions"]

    if source_dir is None:
        raise IngestionError("source_dir manquant : impossible de déterminer le pays de cet exercice.")
    country = _resolve_country(_country_code_from_path(source_dir))
    _validate_pays_matches_country(data.get("pays"), country)

    data, had_series_from_folder = _merge_series_from_folder_name(
        data, source_dir, SERIE_MAP, _split_series,
    )

    subject = _resolve_subject(data["matiere"], country)
    nature_epreuve = _resolve_nature_epreuve(data.get("nature_epreuve"))
    partie_epreuve_francais = _resolve_partie_epreuve_francais(data.get("matiere"), data.get("partie_epreuve_francais"))
    variante_sujet = _resolve_variante_sujet(data.get("variante_sujet"))
    filiere_serie_a = _resolve_filiere_serie_a(data.get("filiere_serie_a"), data.get("serie"))

    year = None
    if data.get("annee"):
        try:
            year = int(data["annee"])
        except (TypeError, ValueError):
            raise IngestionError(f"Année invalide : {data['annee']!r}")

    epreuve_source = data["epreuve_source"]
    numero_exercice = str(data["numero_exercice"])

    # Sortie rapide avant tout travail coûteux (résolution des cursus, transaction,
    # création/mise à jour du Lesson) : sur un dossier de plusieurs centaines de
    # fichiers déjà ingérés lors d'un run précédent, c'est le chemin emprunté pour
    # l'écrasante majorité des fichiers à chaque nouvelle exécution - un seul SELECT
    # (jointure Exercise -> Lesson) suffit à le confirmer, sans jamais toucher
    # `_resolve_cursus_list` ni ouvrir de transaction. Vérifie exactement la même clé
    # (lesson, numero_exercice) que le contrôle équivalent plus bas, juste résolue
    # directement par jointure plutôt qu'en deux temps (chercher/créer le Lesson, puis
    # chercher l'Exercise dessus). `force=True` (ré-import explicite depuis l'admin,
    # jamais depuis run_ingestion) court-circuite volontairement ce raccourci et
    # repasse par le chemin complet ci-dessous, seul à savoir supprimer puis recréer
    # l'Exercise existant.
    if not force:
        existing = Exercise.objects.filter(
            numero_exercice=numero_exercice,
            lesson__epreuve_source=epreuve_source,
            lesson__subject=subject,
            lesson__year=year,
            lesson__lesson_type=LessonType.CORR,
            lesson__cursus__country=country,
        ).first()
        if existing:
            return existing, False

    cursus_list = _resolve_cursus_list(data["examen"], data.get("serie"), country)
    _refuser_informatique_generique_en_serie_ti(subject, cursus_list)

    # Tout ce qui suit est all-or-nothing (y compris la création du Lesson s'il est
    # nouveau) : sans ce bloc, une IngestionError levée plus loin par _attach_figures
    # (ex. PNG manquant sur disque) laisserait un Lesson VALIDE déjà committé, avec
    # zéro exercice et un content_markdown vide - visible publiquement dans le
    # catalogue comme une fiche cassée, sans qu'un ré-import puisse la réparer (le
    # Lesson "existe déjà" et le reste de la fonction repart de cet état incohérent).
    with transaction.atomic():
        # cursus est M2M : ne peut pas faire partie de la clé de get_or_create.
        # Une épreuve est identifiée par (source, matière, année) ; le(s) cursus s'y ajoutent ensuite.
        # Filtré par pays (via cursus__country ET subject__country) pour ne jamais
        # fusionner deux épreuves de pays différents qui partageraient par coïncidence
        # (source, matière, année) - ex. deux "bac-blanc-maths-2024" non désambiguïsés
        # dans leur epreuve_source.
        #
        # subject__code__in=family_codes (pas juste subject=subject) : une épreuve peut
        # mélanger plusieurs disciplines d'une même famille au sein d'un même
        # epreuve_source, avec un matiere qui varie par exercice (constaté sur
        # bac-d-physique-chimie-1995-cameroun : exercices 1-2 "Physique", 3-4 "Chimie" ;
        # et bac-c-physique-chimie-2016-congo : exercices 1-2 "Chimie", 3-5 "Physique").
        # Sans cette recherche élargie, le 2e groupe créerait un second Lesson pour la
        # même épreuve physique au lieu de rejoindre le premier - voir la promotion
        # ci-dessous, qui élargit alors la Subject du Lesson existant plutôt que de le
        # fragmenter. `family_codes` ne contient que {subject.code} pour toute matière
        # hors famille (l'écrasante majorité) : comportement strictement inchangé.
        family_codes = _subject_family_codes(subject.code)
        lesson = Lesson.objects.filter(
            epreuve_source=epreuve_source, subject__code__in=family_codes, subject__country=country,
            year=year, lesson_type=LessonType.CORR, cursus__country=country,
        ).distinct().first()
        if lesson is not None and lesson.subject_id != subject.id and len(family_codes) > 1:
            # Promotion, jamais de retour en arrière : une fois qu'une épreuve s'avère
            # multidisciplinaire (ou explicitement déclarée "Physique-Chimie"), le
            # Lesson reste sous la Subject combinée pour le reste de son existence,
            # même si un exercice ultérieur redéclare une seule discipline - voir
            # SUBJECT_FAMILIES. get(..., subject.code) : no-op si le Lesson est déjà
            # sous la Subject combinée (cas le plus fréquent une fois promu une 1re fois).
            combined_code = SUBJECT_FAMILIES.get(subject.code, subject.code)
            if lesson.subject.code != combined_code:
                lesson.subject = Subject.objects.get(code=combined_code, country=country)
                lesson.save(update_fields=["subject", "updated_at"])
        if lesson is None:
            origine = _resolve_origine(data.get("origine"), country)
            etablissement = str(data.get("etablissement") or "")
            title = build_lesson_title(
                subject, cursus_list, year, origine, etablissement,
                nature_epreuve, partie_epreuve_francais, variante_sujet, filiere_serie_a,
            )

            lesson = Lesson.objects.create(
                epreuve_source=epreuve_source, subject=subject, year=year, lesson_type=LessonType.CORR,
                title=title, statut=StatutContenu.VALIDE,
                duree_epreuve=str(data.get("duree_epreuve") or ""),
                coefficient=_format_coefficient(data.get("coefficient")),
                introduction_markdown=_strip_em_dash(str(data.get("introduction_markdown") or "")),
                origine=origine,
                etablissement=etablissement,
                institution=_resolve_institution(data, origine, etablissement, country, cursus_list),
                nature_epreuve=nature_epreuve,
                partie_epreuve_francais=partie_epreuve_francais,
                variante_sujet=variante_sujet,
                filiere_serie_a=filiere_serie_a,
            )
        for cursus in cursus_list:
            lesson.cursus.add(cursus)

        # duree_epreuve/coefficient sont des attributs de l'épreuve entière, répétés par
        # exercice dans le JSON (même convention que matiere/serie/examen) : on complète
        # le Lesson si un exercice ultérieur les fournit alors que le premier ne les avait pas.
        update_fields = []
        if not lesson.duree_epreuve and data.get("duree_epreuve"):
            lesson.duree_epreuve = str(data["duree_epreuve"])
            update_fields.append("duree_epreuve")
        if not lesson.coefficient and data.get("coefficient"):
            lesson.coefficient = _format_coefficient(data["coefficient"])
            update_fields.append("coefficient")
        # introduction_markdown : même convention que duree_epreuve/coefficient
        # ci-dessus - une consigne d'épreuve entière (ex. "le candidat traitera un seul
        # sujet au choix") n'a de raison d'être fournie que par UN exercice (souvent le
        # premier ingéré, pas forcément le premier affiché), jamais reconstruite depuis
        # plusieurs fragments : le premier exercice qui la porte l'installe sur le Lesson,
        # les suivants ne l'écrasent jamais (protège une correction manuelle faite depuis).
        if not lesson.introduction_markdown and data.get("introduction_markdown"):
            lesson.introduction_markdown = _strip_em_dash(str(data["introduction_markdown"]))
            update_fields.append("introduction_markdown")
        if not lesson.etablissement and data.get("etablissement"):
            lesson.etablissement = str(data["etablissement"])
            update_fields.append("etablissement")
        if not lesson.nature_epreuve and nature_epreuve:
            lesson.nature_epreuve = nature_epreuve
            update_fields.append("nature_epreuve")
        if not lesson.partie_epreuve_francais and partie_epreuve_francais:
            lesson.partie_epreuve_francais = partie_epreuve_francais
            update_fields.append("partie_epreuve_francais")
        if not lesson.variante_sujet and variante_sujet:
            lesson.variante_sujet = variante_sujet
            update_fields.append("variante_sujet")
        if not lesson.filiere_serie_a and filiere_serie_a:
            lesson.filiere_serie_a = filiere_serie_a
            update_fields.append("filiere_serie_a")
        if not lesson.institution:
            institution = _resolve_institution(
                data, lesson.origine, lesson.etablissement, country, cursus_list,
            )
            if institution:
                lesson.institution = institution
                update_fields.append("institution")
        if update_fields:
            lesson.save(update_fields=[*update_fields, "updated_at"])

        existing = Exercise.objects.filter(lesson=lesson, numero_exercice=numero_exercice).first()
        cours_par_external_id = {}
        competence_item_ids = []
        themes_precedents = {}
        if existing:
            if not force:
                return existing, False
            # cours_genere n'est qu'une propriété calculée (cours_id is not None), pas
            # un champ à part - un rappel déjà à l'origine d'un Cours perdrait cette
            # trace si on le laissait simplement disparaître avec l'Exercise supprimé.
            # On la restaure après recréation, en faisant correspondre par external_id
            # (unique=True, voir RappelDeMethode).
            cours_par_external_id = dict(
                existing.rappels_de_methode.exclude(cours__isnull=True).values_list("external_id", "cours_id"),
            )
            # quiz.CompetenceItem.source_exercises (M2M, related_name
            # competence_items_generes) ne survit pas non plus à la suppression :
            # Django vide silencieusement la table de liaison, sans erreur ni
            # avertissement, ce qui a déjà fait perdre ce lien de traçabilité en
            # silence lors d'une campagne de rattachement savoir_officiel. On capture
            # les items concernés avant suppression pour les rattacher au nouvel
            # Exercise recréé ci-dessous.
            competence_item_ids = list(existing.competence_items_generes.values_list("id", flat=True))
            # Thèmes des sous-questions : une Question dont le JSON source n'en porte pas
            # (thèmes attribués après coup, exercice existant seulement en base) les
            # perdrait à la recréation. Restaurés plus bas, par numéro, quand le JSON n'en
            # fournit pas.
            themes_precedents = {
                q.numero: list(q.themes.values_list("name", flat=True)) for q in existing.questions.all()
            }
            # Chemins relevés avant suppression : Figure cascade avec l'Exercise (voir
            # catalog.models), mais Django ne supprime jamais le fichier physique d'un
            # FileField quand la ligne qui le porte disparaît - sans ça, chaque
            # réingestion "force" (ex. action admin "Réingérer depuis le fichier JSON
            # source") laisserait l'ancienne image orpheline sur le disque/Spaces.
            # Même geste déjà fait par LessonAdmin.purge_view pour la même raison.
            figure_paths = list(existing.figures.exclude(image="").values_list("image", flat=True))
            existing.delete()
            for storage_path in figure_paths:
                if default_storage.exists(storage_path):
                    default_storage.delete(storage_path)

        points = str(data.get("points") or "").split("(")[0].strip()

        groupes = [str(g).strip() for g in data.get("groupes") or [] if str(g).strip()]

        exercise = Exercise.objects.create(
            lesson=lesson,
            numero_exercice=numero_exercice,
            points=points,
            groupes=groupes,
            enonce_intro_markdown=_strip_em_dash(str(data.get("enonce_intro_markdown") or "")),
            incertitudes=_drop_processing_notes(data.get("incertitudes") or []),
            statut=StatutContenu.VALIDE,
        )

        exercise.mots_cles_recherche.set(_get_or_create_tags(data.get("mots_cles_recherche")))

        if competence_item_ids:
            exercise.competence_items_generes.set(competence_item_ids)

        for ordre, q_data in enumerate(questions_data, start=1):
            if not q_data.get("enonce_markdown") or not q_data.get("corrige_markdown"):
                raise IngestionError(f"questions[{ordre - 1}] : enonce_markdown et corrige_markdown sont requis.")

            difficulte = DIFFICULTE_MAP.get(_normalize(q_data.get("difficulte_estimee")), "")
            type_reponse = TypeReponse.QCM if _normalize(q_data.get("type_reponse")) == "qcm" else TypeReponse.OUVERTE

            if type_reponse == TypeReponse.QCM:
                choix, reponse_correcte = _normalize_qcm_choix(q_data.get("choix"), q_data.get("reponse_correcte"))
            else:
                choix, reponse_correcte = [], ""

            enonce = _dedupe_question_enonce(_strip_em_dash(q_data["enonce_markdown"]), exercise.enonce_intro_markdown)
            savoir_officiel = _resolve_savoir_officiel(q_data.get("savoir_officiel"), subject)
            question = Question.objects.create(
                exercise=exercise,
                numero=str(q_data.get("numero") or ordre),
                ordre=ordre,
                enonce_markdown=enonce,
                corrige_markdown=_strip_em_dash(q_data["corrige_markdown"]),
                difficulte_estimee=difficulte,
                type_reponse=type_reponse,
                choix=choix,
                reponse_correcte=reponse_correcte,
                # Rattachement direct, sans perte : c'est la seule voie qui conserve la
                # précision par sous-question (voir Question.savoir_officiel).
                savoir_officiel=savoir_officiel,
            )
            themes = _get_or_create_tags(q_data.get("themes") or themes_precedents.get(question.numero))
            question.themes.set(themes)
            # Conservé en plus du rattachement direct ci-dessus : c'est ce lien-là qui fait
            # progresser le mapping des tags historiques, et les épreuves déjà en base n'ont
            # que lui. Les deux voies coexistent, les lecteurs interrogent l'union.
            _link_tags_to_savoir(themes, savoir_officiel)

            for rappel_data in q_data.get("rappels_de_methode") or []:
                # _strip_em_dash appliqué identiquement ici et sur corrige_markdown
                # ci-dessus : _annotate_cours_links (voir models.py) fait correspondre
                # les deux par inclusion de chaîne exacte, donc une normalisation qui
                # diffère entre les deux casserait ce rapprochement silencieusement.
                # Le rappel reste rattaché à l'Exercise (pas à la Question) : Cours
                # continue de se générer au niveau de l'épreuve, pas de la sous-question.
                rappel_id = rappel_data.get("id")
                if not rappel_id and rappel_data.get("cours_id"):
                    # Voir _cours_sibling_rappel_id_map : `id` a été perdu, `cours_id`
                    # (bookkeeping) survit - on retrouve la valeur perdue via le fichier
                    # cours sibling plutôt que d'échouer ou d'inventer un identifiant.
                    rappel_id = _cours_sibling_rappel_id_map(source_dir).get(rappel_data["cours_id"])
                if not rappel_id:
                    raise IngestionError(
                        f"rappels_de_methode : entrée sans 'id' pour la question {q_data.get('numero')!r} "
                        "('cours_id' absent ou non résoluble depuis un fichier cours sibling).",
                    )
                RappelDeMethode.objects.get_or_create(
                    external_id=rappel_id,
                    defaults={
                        "exercise": exercise,
                        # `.get(key) or ""` et pas `.get(key, "")` : correction-experte
                        # émet parfois explicitement `null` plutôt que d'omettre la clé
                        # ou de tomber sur ""; hors valeur absente, `.get(key, "")` ne
                        # retourne son défaut que si la clé est absente, jamais si sa
                        # valeur JSON vaut déjà null - le None traverse alors jusqu'à
                        # la colonne NOT NULL (DataError Postgres constaté en prod).
                        "competence": _strip_em_dash(rappel_data.get("competence") or ""),
                        # "texte" (pas "contenu_markdown") : vu sur ~110 rappels répartis
                        # sur 7 dossiers d'épreuves de maths anciennes (bac-c-maths-1985/
                        # 1986/1989/1990/1991/1992/blanc-2003-cameroun), toujours couplé à
                        # la forme `id` absent + `cours_id` présent ci-dessus (même lot,
                        # vraisemblablement une convention de sortie plus ancienne du mode
                        # cours) - sans ce repli, `contenu_markdown` restait silencieusement
                        # vide : `id` se résolvait bien via le fichier cours sibling (pas
                        # d'IngestionError), mais _annotate_cours_links (catalog.rendering)
                        # ne peut jamais injecter le lien "[COURS_LINK:...]" sur un
                        # RappelDeMethode dont contenu_markdown.strip() est vide (voir sa
                        # garde `if r.cours_id and r.contenu_markdown.strip()`) - le lien
                        # "Voir le cours complet" disparaissait silencieusement du corrigé.
                        "contenu_markdown": _strip_em_dash(
                            rappel_data.get("contenu_markdown") or rappel_data.get("texte") or "",
                        ),
                    },
                )

        _attach_figures(exercise, data.get("figures") or [], source_dir)
        # Les réparations automatiques ci-dessus (was_repaired, had_*) ne laissent aucune
        # trace dans `incertitudes` : ce champ est réservé aux doutes réels sur le
        # contenu de l'épreuve, pas au journal de traitement.
        exercise.compile_from_questions()

        if cours_par_external_id:
            for rappel in exercise.rappels_de_methode.filter(external_id__in=cours_par_external_id):
                rappel.cours_id = cours_par_external_id[rappel.external_id]
                rappel.save(update_fields=["cours"])

        lesson.compile_from_exercises()

    return exercise, True


def _link_rappels_lies(cours, source):
    """
    SKILL.md (mode cours) documente `source.rappels_lies` : d'autres rappels de la
    même épreuve, déjà ingérés, que ce même cours couvre aussi - cas du mode
    interactif où plusieurs blocs "### Rappel de méthode" fournis ensemble donnent
    lieu à un seul cours (le mode automatisation produit toujours un rappel par
    fichier cours, donc une liste vide). Sans ce rattachement, ces rappels
    resteraient cours_genere=false alors qu'un cours existe bel et bien pour eux -
    silencieux jusqu'à ce qu'un élève tombe dessus ailleurs dans la même épreuve.
    Best-effort : un identifiant introuvable est ignoré plutôt que de faire échouer
    tout l'ingestion du cours pour une donnée secondaire.
    """
    external_ids = source.get("rappels_lies") or []
    if external_ids:
        RappelDeMethode.objects.filter(external_id__in=external_ids).update(cours=cours)


def ingest_cours(data, source_dir=None):
    """
    Ingère un objet JSON produit par le mode cours de correction-experte. Retourne
    (cours, created). Idempotent via `cours_id` (external_id).

    Un cours ne peut pas exister sans épreuve source tracée : IngestionError si celle-ci
    reste introuvable. En revanche le rappel de méthode précis dont le cours dérive peut
    manquer sans être bloquant - voir la résolution de `lesson_source` plus bas : le cours
    est alors publié rattaché à son épreuve, seul le lien rappel -> cours (le « voir le
    cours » affiché dans le corrigé) reste absent, faute de rappel où l'accrocher.

    Valide et compile automatiquement (voir ingest_exercise) : le Cours passe directement
    en VALIDE et son content_markdown est compilé avant de retourner - visible côté
    frontend dès l'ingestion, sans étape de validation manuelle.
    """
    data, _ = _repair_double_json_escaping(data)
    data, _ = _repair_missing_matrix_row_separators(data)
    data, _ = _repair_dict_shaped_cours_sections(data)

    meta = data.get("meta") or {}
    source = data.get("source") or {}

    cours_id = data.get("cours_id")
    if not cours_id or not meta.get("titre") or not meta.get("matiere") or not source.get("rappel_id"):
        raise IngestionError("Champs obligatoires manquants : cours_id, meta.titre, meta.matiere, source.rappel_id")

    # Vérifié avant de résoudre `rappel` : sur un dossier déjà ingéré lors d'un run
    # précédent (le cas courant à chaque nouvelle exécution sur tout `ingest/`), ce
    # seul lookup indexé (external_id, unique=True) suffit à confirmer qu'il n'y a
    # rien à faire - inutile d'aller chercher le RappelDeMethode source (une jointure
    # en plus) pour un cours qui existe déjà. Décale aussi, en bonus, la vérification
    # "le rappel source existe" pour qu'elle ne s'applique qu'aux cours réellement à
    # créer : un cours déjà ingéré reste idempotent même si son rappel source avait
    # depuis disparu ou changé d'external_id, au lieu de faire échouer à tort un
    # fichier qui n'avait de toute façon plus rien à ingérer.
    existing = Cours.objects.filter(external_id=cours_id).first()
    if existing:
        # `cours_id` est déterministe, dérivé uniquement de la compétence et du
        # niveau (voir SKILL.md) - jamais de l'épreuve source. Deux épreuves
        # différentes couvrant la même compétence produisent donc légitimement le
        # même `cours_id` : ce n'est pas seulement une ré-ingestion du même fichier,
        # c'est aussi le cas normal d'une notion récurrente d'un examen à l'autre.
        # Sans rattacher CE rappel-ci au Cours déjà existant, il resterait orphelin
        # (cours_genere jamais mis à true) même si le Cours qu'il devrait pointer
        # existe déjà et est publié - même geste que le dédoublonnage par titre
        # ci-dessous, jamais de contenu recréé. `rappel` peut rester introuvable
        # (source.rappel_id absent/changé) sans faire échouer l'idempotence : c'est
        # exactement le cas que ce fast-path est censé tolérer (voir commentaire
        # d'origine ci-dessus), on se contente alors de ne rien lier.
        rappel = RappelDeMethode.objects.filter(external_id=source.get("rappel_id")).first()
        if rappel and rappel.cours_id != existing.pk:
            rappel.cours = existing
            rappel.save(update_fields=["cours"])
            _link_rappels_lies(existing, source)
        return existing, False

    rappel = RappelDeMethode.objects.select_related("exercise__lesson").filter(
        external_id=source["rappel_id"],
    ).first()
    # Repli sur la leçon quand le rappel source n'existe pas, pour un défaut constaté sur
    # 87 fichiers (bac-a-anglais-2014 à 2017-cameroun, 85 ; bac-c-maths-1986-cameroun, 2) :
    # la passe cours a généré un cours PAR QUESTION (source.rappel_id = "rdm-...-ex1-qI.3-0")
    # alors que la passe exercices n'a émis qu'un rappel PAR EXERCICE ("rdm-...-ex1-0"), donc
    # aucun des deux ne se rejoint. Ces cours - du contenu réel, déjà rédigé - échouaient à
    # chaque run depuis, sans jamais être publiés.
    #
    # Le rappel sert à trois choses : le lien rappel -> cours, et l'héritage du pays et du
    # cursus depuis la leçon dont il dérive. Sans lui, seul le premier est réellement perdu -
    # la leçon reste identifiable par `source.epreuve_source`, le même champ que
    # Lesson.epreuve_source (voir ingest_exercise), donc pays et cursus restent connus avec
    # certitude plutôt que devinés. Publier vaut mieux que bloquer ; mais uniquement sur
    # cette identification exacte : sans épreuve retrouvée, on échoue toujours plutôt que de
    # rattacher un cours à peu près.
    lesson_source = rappel.exercise.lesson if rappel else (
        Lesson.objects.filter(epreuve_source=source.get("epreuve_source") or "").first()
        # `source.epreuve_source` est optionnel côté compétence et absent de 76 des 87
        # fichiers concernés - le dossier prend alors le relais.
        or _lesson_from_source_dir(source_dir)
    )
    if lesson_source is None:
        raise IngestionError(
            f"RappelDeMethode introuvable pour source.rappel_id={source['rappel_id']!r}, et "
            f"épreuve non identifiable (source.epreuve_source={source.get('epreuve_source')!r}, "
            f"dossier={source_dir}) - l'exercice source doit être ingéré avant le cours qui en dérive.",
        )

    # Dédoublonnage par titre : une même notion (ex. "Résolution d'équations du second
    # degré") peut être extraite de plusieurs épreuves différentes - avec la génération
    # de cours désormais systématique côté compétence (voir SKILL.md), inutile de
    # publier un Cours quasi identique à chaque occurrence. Même mécanisme (titre
    # exact, insensible à la casse) que celui déjà utilisé pour lier les prérequis
    # entre cours (voir Cours._render_section) : on rattache ce nouveau rappel au
    # Cours existant plutôt que d'en créer un doublon.
    titre = _strip_em_dash(meta["titre"])
    duplicate = Cours.objects.filter(titre__iexact=titre, statut=StatutContenu.VALIDE).first()
    if duplicate:
        if rappel:
            rappel.cours = duplicate
            rappel.save(update_fields=["cours"])
        _link_rappels_lies(duplicate, source)
        return duplicate, False

    # Un Cours n'a pas de dossier source à lui (pas de source_dir ici, contrairement à
    # ingest_exercise) : le pays se déduit du Cursus déjà résolu pour la leçon dont il
    # dérive plutôt que d'être re-parsé - garanti non vide, cursus est obligatoire
    # sur Lesson (voir Lesson.cursus) et déjà peuplé à ce stade de l'ingestion.
    country = lesson_source.cursus.first().country
    _validate_pays_matches_country(meta.get("pays"), country)
    subject = _resolve_subject(meta["matiere"], country)
    _refuser_informatique_generique_en_serie_ti(subject, list(lesson_source.cursus.select_related("series")))

    # all-or-nothing, même raison que le bloc équivalent d'ingest_exercise : sans ce
    # bloc, une exception levée par compile_from_sections() (ex. une forme de section
    # inattendue - voir Cours._render_section) laisserait un Cours VALIDE déjà
    # committé, avec un content_markdown vide - visible publiquement dans le
    # catalogue comme une fiche cassée, sans qu'un ré-import ne puisse la réparer
    # (le Cours "existe déjà" via external_id et le reste de la fonction repart de
    # cet état incohérent).
    with transaction.atomic():
        cours = Cours.objects.create(
            external_id=cours_id,
            titre=titre,
            subject=subject,
            sous_theme=_strip_em_dash(meta.get("sous_theme") or ""),
            duree_estimee_min=meta.get("duree_estimee_min") or None,
            sections_raw=_strip_em_dash(data.get("sections") or []),
            statut=StatutContenu.VALIDE,
        )

        # meta.serie/niveau ne portent pas l'examen (BEPC/Probatoire/BAC) requis pour
        # résoudre un Cursus - on hérite donc directement des cursus de l'épreuve source
        # plutôt que de re-parser ces champs. serie=null ("toutes séries") laisse cursus
        # vide : le cours reste alors accessible à tout abonné actif (voir has_access).
        if meta.get("serie"):
            cours.cursus.set(lesson_source.cursus.all())

        tags = _get_or_create_tags(meta.get("tags"))
        cours.tags.set(tags)
        _link_tags_to_savoir(tags, _resolve_savoir_officiel(meta.get("savoir_officiel"), subject))
        cours.compile_from_sections()

        if rappel:
            rappel.cours = cours
            rappel.save(update_fields=["cours"])
        _link_rappels_lies(cours, source)

    return cours, True


def run_ingestion(path):
    """
    Ingère tous les fichiers .json sous `path` (fichier unique, ou dossier - recherche
    récursive), qu'il s'agisse d'exercices (mode automatisation) ou de cours (mode
    cours). Point d'entrée partagé par la commande `ingest_corrections` et le bouton
    d'ingestion de l'admin, pour que les deux se comportent identiquement.

    Idempotent : ré-ingérer un fichier déjà traité ne recrée ni ne modifie rien (voir
    ingest_exercise/ingest_cours), donc relancer sur le même dossier sans le vider
    entre-temps est sans risque.

    Retourne {"files_found": int, "created": int, "skipped": int, "errors": [str, ...]}.
    """
    # Vidé à chaque run (jamais laissé vivre entre deux appels) : voir le commentaire
    # sur _resolve_country - garantit qu'un Country/Subject/Cursus ajouté ou modifié
    # depuis l'admin entre deux runs est bien vu par celui-ci, tout en profitant du
    # cache pour la durée d'un même run (le cas qui compte : des centaines de fichiers
    # du même lot partagent le même pays/matière/cursus).
    _resolve_country.cache_clear()
    _resolve_subject.cache_clear()
    _resolve_cursus_list.cache_clear()

    path = Path(path)
    # Tout composant de chemin préfixé par "_" (dossier ou fichier) est du tooling/état
    # interne, jamais du contenu à ingérer - convention déjà utilisée par "_quiz"
    # (sous-arbre réservé aux lots CompetenceItem du skill concepteur-quiz-competence,
    # voir quiz.ingestion.run_ingestion) et généralisée ici après un cas réel :
    # bac-blanc-d-ti-physique-2025-cameroun contenait un `_registry_dump.json` (état
    # interne de la génération) et un `_tmp_pages/` (crops PNG intermédiaires) laissés
    # par erreur dans l'arbre publié - un objet de ce genre n'a ni "epreuve_source" ni
    # "sections", donc atterrit dans exercice_items et fait échouer ingest_exercise sur
    # "Champs obligatoires manquants" à chaque ingestion, pour une erreur qui n'en est
    # pas une. Exclu ici plutôt que de laisser cette pollution se répéter à chaque
    # nouveau nom de fichier interne que la génération pourrait introduire.
    files = (
        [path] if path.is_file()
        else sorted(
            f for f in path.rglob("*.json")
            if not any(part.startswith("_") for part in f.relative_to(path).parts)
        )
    )

    # Un cours référence toujours un rappel de méthode déjà ingéré comme exercice
    # (source.rappel_id) : on ingère donc tous les exercices d'abord, puis tous les
    # cours, quel que soit l'ordre alphabétique des fichiers sur le disque.
    exercice_items = []
    cours_items = []
    errors = []

    for file_path in files:
        try:
            raw = json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(f"{file_path}: JSON invalide ({exc})")
            continue

        for data in raw if isinstance(raw, list) else [raw]:
            # Un objet "cours" (mode cours) porte "sections" ; un objet "exercice"
            # (mode automatisation) porte "corrige_markdown" - jamais les deux.
            if isinstance(data, dict) and "sections" in data:
                cours_items.append((file_path, data))
            else:
                exercice_items.append((file_path, data))

    created = 0
    skipped = 0
    lesson_ids = set()

    for file_path, data in exercice_items:
        # Fichier neutralisé intentionnellement (contenu dupliqué déjà fusionné dans un
        # autre fichier de l'épreuve, suppression physique refusée par l'utilisateur -
        # voir bac-c-e-maths-2015-cameroun_exercice_5.json) : "questions" y est laissé
        # vide pour signaler qu'il ne doit jamais être ingéré, mais ingest_exercise ne
        # connaît pas cette convention et lève IngestionError dessus à chaque lot -
        # une "erreur" qui n'en est pas une et qu'aucune correction de contenu ne peut
        # jamais faire disparaître. On l'ignore proprement ici, avant d'atteindre cette
        # validation, plutôt que de la compter comme un échec d'ingestion.
        if isinstance(data, dict) and str(data.get("statut", "")).startswith("obsolete"):
            skipped += 1
            continue
        try:
            exercise, was_created = ingest_exercise(data, source_dir=file_path.parent)
            lesson_ids.add(exercise.lesson_id)
            created += 1 if was_created else 0
            skipped += 0 if was_created else 1
        except Exception as exc:
            # Exception générique, pas seulement IngestionError : une erreur DB
            # inattendue (ex. DataError sur un champ mal formé par la compétence) ne
            # doit pas non plus planter tout le lot en cours de route et priver les
            # fichiers suivants d'être traités - chaque appel est déjà dans sa propre
            # transaction atomique (voir ingest_exercise), donc annuler celle-ci et
            # continuer est sans risque pour les autres fichiers.
            numero = data.get("numero_exercice", "?") if isinstance(data, dict) else "?"
            errors.append(f"{file_path} (exercice {numero}): {exc}")

    for file_path, data in cours_items:
        try:
            _, was_created = ingest_cours(data, source_dir=file_path.parent)
            created += 1 if was_created else 0
            skipped += 0 if was_created else 1
        except Exception as exc:
            cours_id = data.get("cours_id", "?") if isinstance(data, dict) else "?"
            errors.append(f"{file_path} (cours {cours_id}): {exc}")

    return {
        "files_found": len(files), "created": created, "skipped": skipped, "errors": errors,
        "lesson_ids": sorted(lesson_ids),
    }


# --- Ingestion en arrière-plan (bouton de l'admin) ---------------------------
#
# run_ingestion parcourt tout INGEST_DIR d'un bloc : ~30 s pour un dossier de 5 000
# fichiers déjà tous ingérés (donc uniquement des lectures), bien davantage dès qu'il
# reste du contenu neuf à écrire. C'est au-delà du `--timeout 30` de gunicorn (voir
# backend/entrypoint.sh) : lancée depuis le thread de requête, l'ingestion faisait tuer
# le worker en plein run (WORKER TIMEOUT), et l'admin renvoyait la page "Internal Server
# Error" de gunicorn - alors même que l'ingestion avait déjà commencé à écrire en base,
# chaque fichier étant dans sa propre transaction. Elle est donc lancée dans un processus
# détaché (même pattern que catalog.sujet_pdf.queue_sujet_pdf_generation, déjà éprouvé
# ici pour la génération des PDF), et le rapport - qui ne peut plus être renvoyé dans la
# réponse - est écrit sur disque pour que la page admin l'affiche à l'actualisation.
INGESTION_REPORT_PATH = Path(settings.BASE_DIR) / "logs" / "ingestion_report.json"


def write_ingestion_report(report, path=INGESTION_REPORT_PATH):
    """Écrit le rapport d'un run (voir read_ingestion_report pour sa lecture)."""
    path = Path(path)
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def read_ingestion_report(path=INGESTION_REPORT_PATH):
    """
    Rapport du dernier run - `status` valant "running" (processus lancé, pas encore
    terminé), "done" ou "error". None tant qu'aucun run n'a eu lieu, ou si le fichier
    est illisible : l'absence de rapport ne doit jamais empêcher la page de s'afficher.

    Les horodatages sont réhydratés en datetime pour rester filtrables côté template.
    """
    try:
        report = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    for key in ("started_at", "finished_at"):
        try:
            report[key] = datetime.fromisoformat(report[key])
        except (KeyError, TypeError, ValueError):
            pass
    return report


def queue_ingestion(path, report_path=INGESTION_REPORT_PATH):
    """
    Lance `manage.py ingest_corrections <path>` dans un processus détaché, complètement
    en dehors du process serveur - voir le commentaire ci-dessus sur INGESTION_REPORT_PATH.
    La commande écrit elle-même le rapport dans report_path en fin de traitement (option
    --report-json), et enchaîne sur la génération des PDF de sujet manquants.

    Le rapport "running" est écrit ici, avant le lancement, pour qu'une actualisation
    immédiate de la page admin montre déjà le run en cours plutôt que le rapport
    précédent (et pour que le bouton refuse d'en lancer un second en parallèle).
    """
    write_ingestion_report(
        {"status": "running", "started_at": timezone.now().isoformat(), "path": str(path)}, report_path,
    )

    manage_py = Path(settings.BASE_DIR) / "manage.py"
    args = [
        sys.executable, str(manage_py), "ingest_corrections", str(path),
        "--report-json", str(report_path),
    ]

    # PYTHONUTF8 / Popen "nu" / start_new_session : mêmes contraintes, pour les mêmes
    # raisons, que catalog.sujet_pdf.queue_sujet_pdf_generation - voir ses commentaires.
    logs_dir = Path(settings.BASE_DIR) / "logs"
    logs_dir.mkdir(exist_ok=True)
    log_f = open(logs_dir / "ingestion.log", "ab")
    env = {**os.environ, "PYTHONUTF8": "1"}

    kwargs = {}
    if sys.platform != "win32":
        kwargs["start_new_session"] = True

    try:
        subprocess.Popen(
            args, cwd=settings.BASE_DIR, env=env,
            stdin=subprocess.DEVNULL, stdout=log_f, stderr=log_f,
            **kwargs,
        )
    except OSError as exc:
        # Sans ça, un lancement impossible laisserait un rapport "running" éternel, qui
        # bloquerait aussi toute nouvelle tentative depuis l'admin.
        write_ingestion_report(
            {"status": "error", "started_at": timezone.now().isoformat(), "detail": str(exc)}, report_path,
        )
        raise
