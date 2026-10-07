"""
Moteur de la recherche globale : de la requête saisie aux résultats groupés par type.

Trois étapes, toutes portables SQLite/Postgres (voir recherche.texte pour la raison) :
  1. Candidats : SQL, un jeu de conditions « le mot commence ici » par jeton exigé, sur les clés
     courtes ET le texte public de l'index. Seules des colonnes légères sont relues.
  2. Classement : en Python, sur ces candidats seulement (plafonnés) - correspondance dans le
     titre d'abord, puis dans les clés (thème, matière, série), puis dans le texte.
  3. Habillage : les seules lignes affichées sont relues en entier, avec leur niveau d'accès.

Une recherche qui ne donne rien est retentée avec le vocabulaire du catalogue (fautes de frappe).
"""

import math
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from django.db.models import Exists, F, OuterRef, Q
from django.db.models.functions import Length
from django.utils import timezone

from access.services import bulk_active_inedite_cursus_ids, bulk_active_subscription_cursus_ids
from catalog.models import Cours, Cursus, Exercise, Lesson, StatutContenu, Subject, resolve_examen_label
from quiz.services import COEFFICIENT_PAR_DEFAUT, _coefficient_par_subject

from . import intention as comprendre
from . import synonymes, texte
from .indexation import RANG_EXAMEN, RANG_EXAMEN_AUTRE, texte_public_cours
from .models import EntreeRecherche, RechercheSansResultat, TermeRecherche, TypeResultat

# Ordre d'affichage des groupes : le thème d'abord (la meilleure porte d'entrée), les questions
# de quiz en dernier (la plus fine).
ORDRE_GROUPES = [t.value for t in TypeResultat]

# Au-delà, une requête n'est plus une recherche (« maths » seul touche presque tout l'index) :
# on classe les premiers candidats seulement, sans jamais charger 30 000 lignes.
PLAFOND_CANDIDATS = 15000
LIMITE_DEFAUT = 6
LIMITE_MAX = 40
LONGUEUR_EXTRAIT = 170
MAX_JETONS = 8
LONGUEUR_MAX_REQUETE = 100
# Sous ce nombre de résultats dans le cursus de l'élève, on lui dit combien il en reste ailleurs.
SEUIL_AUTRES_CURSUS = 10
NB_SUGGESTIONS = 6
# Page de recherche sans requête : quelques thèmes de plus à proposer pour commencer.
NB_SUGGESTIONS_ACCUEIL = 8
# Journal des recherches vides (voir RechercheSansResultat) : bornes de prudence.
JOURNAL_LONGUEUR_MIN = 3
JOURNAL_LONGUEUR_MAX = 80
JOURNAL_MAX_JETONS = 8
JOURNAL_MAX_CHIFFRES = 5
JOURNAL_MAX_LIGNES = 5000


def _analyser(requete):
    """Jetons utiles d'une requête, au singulier approximatif, sans doublon."""
    jetons = [texte.racine(j) for j in texte.jetons(str(requete)[:LONGUEUR_MAX_REQUETE])]
    return list(dict.fromkeys(jetons))[:MAX_JETONS]


@dataclass
class Terme:
    """Un mot à chercher : lui-même, ses équivalents connus (voir recherche.synonymes), et s'il est exigé."""

    texte: str
    alts: list = field(default_factory=list)
    requis: bool = False

    @property
    def formes(self):
        return [self.texte, *self.alts]


def _termes(jetons):
    return [Terme(j, synonymes.alternatives(j), synonymes.est_requis(j)) for j in jetons]


# --- Étape 1 : candidats ---------------------------------------------------------------


def _queryset(
    pays, termes, *, cursus_ids=None, matiere=None, matieres=None, annees=None, type_=None,
):
    """`matiere` : un code (le filtre choisi dans l'interface) ; `matieres` : des codes (ce que la requête
    nomme, voir intention) ; `annees` : les années nommées ; `cursus_ids` : les examens visés."""
    queryset = EntreeRecherche.objects.filter(pays=pays)
    if matiere:
        queryset = queryset.filter(matiere__code=matiere)
    if matieres:
        queryset = queryset.filter(matiere__code__in=matieres)
    if annees:
        queryset = queryset.filter(annee__in=annees)
    if type_:
        queryset = queryset.filter(type=type_)
    if cursus_ids:
        lien = EntreeRecherche.cursus.through.objects.filter(
            entreerecherche_id=OuterRef("pk"), cursus_id__in=cursus_ids,
        )
        queryset = queryset.filter(Q(tous_cursus=True) | Exists(lien))
    for terme in termes:
        if not terme.requis:
            continue
        # Début de mot : l'index range ses textes entourés d'espaces (voir indexation._cles). Un mot est
        # trouvé s'il l'est lui-même OU par l'un de ses équivalents.
        condition = Q()
        for forme in terme.formes:
            debut = f" {forme}"
            condition |= Q(cles_norm__contains=debut) | Q(texte_norm__contains=debut)
        queryset = queryset.filter(condition)
    return queryset


def _lignes(pays, termes, **filtres):
    return list(
        _queryset(pays, termes, **filtres).values_list(
            "id", "type", "titre_norm", "cles_norm", "annee", "groupe", "poids", "matiere_id",
            "frequence", "popularite", "niveau",
        )[:PLAFOND_CANDIDATS],
    )


# --- Étape 2 : classement --------------------------------------------------------------

# Un équivalent (« disque » pour « cercle ») vaut un peu moins que le mot tapé : à pertinence égale, celui
# qui contient le mot de l'élève passe devant.
POIDS_EQUIVALENT = 0.8

# Signaux de départage (voir _bonus_signaux). Une fréquence de 100 % vaut 5 points ; un contenu lu par 32
# élèves distincts en vaut 2 ; un coefficient de 5 en vaut 2.
POIDS_FREQUENCE = 0.05
POIDS_POPULARITE = 0.4
POIDS_COEFFICIENT = 0.4
BONUS_NIVEAU_EGAL = 2.0
BONUS_NIVEAU_FONDATION = 1.0
MALUS_NIVEAU_AU_DELA = -1.5
# Pas de référentiel de coefficients dans le modèle : on les lit des épreuves (voir _coefficients).
DUREE_CACHE_COEFFICIENTS_S = 600


@dataclass
class Signaux:
    """Ce que le moteur sait de l'EXAMEN de l'élève (jamais de l'élève lui-même) : son niveau d'examen et le
    coefficient de chaque matière à cet examen. Vide pour un visiteur qui n'a rien déclaré."""

    rang_eleve: int | None = None
    coefficients: dict = field(default_factory=dict)


_CACHE_COEFFICIENTS = {}


def _coefficients(cursus):
    """{matière: coefficient dominant à cet examen}, calculé depuis les épreuves (voir
    quiz.services._coefficient_par_subject) puis gardé dix minutes : la requête parcourt toutes les épreuves
    du cursus, trop pour être refaite à chaque frappe d'un élève."""
    maintenant = time.monotonic()
    en_cache = _CACHE_COEFFICIENTS.get(cursus.id)
    if en_cache and maintenant - en_cache[0] < DUREE_CACHE_COEFFICIENTS_S:
        return en_cache[1]
    coefficients = _coefficient_par_subject(cursus)
    _CACHE_COEFFICIENTS[cursus.id] = (maintenant, coefficients)
    return coefficients


def _signaux(cursus_id):
    if not cursus_id:
        return Signaux()
    cursus = Cursus.objects.filter(pk=cursus_id).first()
    if cursus is None:
        return Signaux()
    return Signaux(rang_eleve=RANG_EXAMEN.get(cursus.examen, RANG_EXAMEN_AUTRE), coefficients=_coefficients(cursus))


def _suite_de_mots(mots, jetons):
    """Vrai si `jetons` apparaissent consécutivement (chacun comme début de mot) dans `mots`."""
    taille = len(jetons)
    return any(
        all(mots[i + k].startswith(jetons[k]) for k in range(taille))
        for i in range(len(mots) - taille + 1)
    )


def _points(forme, mots, titre_norm, cles_norm):
    """(points, hors_titre) d'UNE forme de mot : (0, None) si elle n'apparaît ni dans le titre ni dans les
    clés (elle n'a alors été trouvée que dans le texte)."""
    court = len(forme) < 3
    # Une forme courte (« d », « ti ») ne vaut que comme MOT entier : en préfixe elle toucherait
    # n'importe quel mot qui commence par la même lettre.
    if forme in mots:
        return 12, False
    if not court and any(m.startswith(forme) for m in mots):
        return 8, False
    if (f" {forme} " if court else f" {forme}") in cles_norm:
        return 4, True
    if not court and forme in titre_norm:
        return 2, False
    return 0, None


def _score(ligne, termes, signaux):
    _id, _type, titre_norm, cles_norm, annee, _groupe, poids, matiere_id, frequence, popularite, niveau = ligne
    mots = titre_norm.split()
    score = 0.0
    hors_titre = 0
    for terme in termes:
        meilleur, hors = 0.0, None
        for rang, forme in enumerate(terme.formes):
            points, hors_forme = _points(forme, mots, titre_norm, cles_norm)
            points *= 1 if rang == 0 else POIDS_EQUIVALENT
            if points > meilleur:
                meilleur, hors = points, hors_forme
        if meilleur > 0:
            score += meilleur
            hors_titre += bool(hors and terme.requis)
        elif terme.requis:
            score += 1  # trouvé seulement dans le texte
            hors_titre += 1
    requis = [t for t in termes if t.requis]
    if requis and hors_titre == 0:
        score += 10  # tous les mots exigés sont dans le titre
    if len(termes) > 1:
        utiles = [m for m in mots if m not in texte.MOTS_VIDES]
        if _suite_de_mots(utiles, [t.texte for t in termes]):
            score += 15  # l'expression exacte, dans l'ordre
    # Départages : titre court (plus précis), contenu abondant (thème riche), année récente.
    score -= 0.15 * len(mots)
    score += 0.5 * min(math.log2(1 + poids), 6)
    score += (annee or 0) / 10000
    return score + _bonus_signaux(frequence, popularite, niveau, matiere_id, signaux)


def _bonus_signaux(frequence, popularite, niveau, matiere_id, signaux):
    """
    Ce qui départage deux contenus aussi bien appariés au texte : ce qui tombe vraiment à l'examen, ce que
    d'autres élèves ont ouvert, ce qui est au niveau de l'élève, ce qui compte dans son examen. Au plus une
    dizaine de points, contre 12 pour un mot trouvé dans le titre : ces signaux ne font jamais remonter un
    contenu qui ne correspond pas à la requête, ils ordonnent ceux qui y correspondent.
    """
    bonus = POIDS_FREQUENCE * frequence + POIDS_POPULARITE * min(math.log2(1 + popularite), 5)
    if signaux.rang_eleve is not None and niveau >= 0:
        if niveau == signaux.rang_eleve:
            bonus += BONUS_NIVEAU_EGAL
        elif niveau < signaux.rang_eleve:
            bonus += BONUS_NIVEAU_FONDATION  # un acquis qui sert encore
        else:
            bonus += MALUS_NIVEAU_AU_DELA  # au-delà de son examen
    if signaux.coefficients:
        bonus += POIDS_COEFFICIENT * signaux.coefficients.get(matiere_id, COEFFICIENT_PAR_DEFAUT)
    return bonus


def _classer(lignes, termes, signaux):
    """{type: [(score, id, nb)]} trié par score décroissant. Les questions de quiz d'un même
    thème forment UN résultat (nb = nombre de questions qui correspondent), et disparaissent si
    ce thème est déjà proposé en tant que thème - sa carte donne déjà accès au quiz."""
    par_type = defaultdict(list)
    for ligne in lignes:
        par_type[ligne[1]].append((_score(ligne, termes, signaux), ligne[0], ligne[5], ligne[2], ligne[7]))

    # Deux thèmes de même intitulé dans la même matière (« Thalès » / « thalès », deux étiquettes pour une
    # notion) ne font qu'un résultat : on garde le mieux classé.
    uniques = {}
    for score, entree_id, groupe, titre_norm, matiere_id in par_type.get(TypeResultat.THEME.value, ()):
        cle = (titre_norm, matiere_id)
        if cle not in uniques or (score, -entree_id) > (uniques[cle][0], -uniques[cle][1]):
            uniques[cle] = (score, entree_id, groupe, titre_norm, matiere_id)
    if uniques:
        par_type[TypeResultat.THEME.value] = list(uniques.values())

    themes_proposes = {e[2] for e in par_type.get(TypeResultat.THEME.value, ())}
    quiz = {}
    for score, entree_id, groupe, _titre, _matiere in sorted(par_type.get(TypeResultat.QUIZ.value, ()), reverse=True):
        if groupe in themes_proposes:
            continue
        if groupe in quiz:
            quiz[groupe][2] += 1
        else:
            quiz[groupe] = [score, entree_id, 1]

    resultat = {}
    for type_, entrees in par_type.items():
        if type_ == TypeResultat.QUIZ.value:
            continue
        resultat[type_] = sorted(((e[0], e[1], None) for e in entrees), key=lambda e: (-e[0], e[1]))
    if quiz:
        resultat[TypeResultat.QUIZ.value] = sorted(
            ((s, i, nb) for s, i, nb in quiz.values()), key=lambda e: (-e[0], e[1]),
        )
    return resultat


# --- Fautes de frappe ------------------------------------------------------------------

# Distance d'édition maximale entre le mot tapé et un mot de même prononciation : « fotosyntese » est à 4 de
# « photosynthese » - la prononciation rapproche des graphies que la seule distance écarterait.
ECART_PHONETIQUE_MAX = 4


def corriger(jetons):
    """{jeton: mot du catalogue le plus proche} pour les jetons qui n'existent nulle part (même
    pas comme début de mot).

    D'abord par la PRONONCIATION (voir texte.phonetique) : un élève écrit « teoreme », « fotosyntese »,
    « hthales » comme il les entend, et la distance d'édition hésite (« tales » est aussi près de « table »
    que de « thales »). Ensuite, à défaut, par la distance d'édition : une ou deux fautes selon la longueur du
    mot, même initiale exigée - sans cela, comparer chaque mot à tout le vocabulaire coûterait des secondes.
    À égalité, le mot le plus fréquent du catalogue gagne."""
    corrections = {}
    for jeton in jetons:
        if len(jeton) < 4 or TermeRecherche.objects.filter(terme__startswith=jeton).exists():
            continue
        meilleur = None
        cle = texte.phonetique(jeton)
        if len(cle) >= 3:
            for terme, frequence in TermeRecherche.objects.filter(phonetique=cle).values_list("terme", "frequence"):
                ecart = texte.distance(jeton, terme, ECART_PHONETIQUE_MAX)
                if ecart <= ECART_PHONETIQUE_MAX and (meilleur is None or (ecart, -frequence) < meilleur[0]):
                    meilleur = ((ecart, -frequence), terme)
        if meilleur is None:
            tolerance = 1 if len(jeton) <= 5 else 2
            proches = (
                TermeRecherche.objects.filter(terme__startswith=jeton[0])
                .annotate(longueur=Length("terme"))
                .filter(longueur__gte=len(jeton) - tolerance, longueur__lte=len(jeton) + tolerance)
                .values_list("terme", "frequence")
            )
            for terme, frequence in proches:
                ecart = texte.distance(jeton, terme, tolerance)
                if ecart <= tolerance and (meilleur is None or (ecart, -frequence) < meilleur[0]):
                    meilleur = ((ecart, -frequence), terme)
        if meilleur:
            corrections[jeton] = meilleur[1]
    return corrections




# --- Étape 3 : habillage ---------------------------------------------------------------


class _Acces:
    """Ce que le visiteur a le droit de lire - calculé UNE fois par requête HTTP (voir
    access.services.bulk_active_*), jamais un test par résultat affiché."""

    def __init__(self, utilisateur):
        self.connecte = bool(utilisateur is not None and utilisateur.is_authenticated)
        self.abonnements = bulk_active_subscription_cursus_ids(utilisateur)
        self.inedites = bulk_active_inedite_cursus_ids(utilisateur)

    def niveau(self, entree):
        """"libre" (sans abonnement), "ouvert" (ce visiteur y a droit), "verrouille" (abonnement
        requis), ou None quand la notion n'a pas de sens (un thème n'est pas un contenu payant).
        Miroir de access.services.has_access / has_access_inedite - c'est la PAGE du contenu qui
        applique la vraie règle, ceci n'est qu'un indice affiché à côté du résultat."""
        if entree.type == TypeResultat.THEME:
            return None
        ids = set(entree.meta.get("acces_ids", ()))
        if entree.type == TypeResultat.INEDITE:
            if entree.est_gratuit:
                return "libre"
            return "ouvert" if ids & self.inedites else "verrouille"
        if entree.est_gratuit:
            return "libre"
        if not self.connecte:
            return "verrouille"
        # Aucun cursus d'accès propre (cours « toutes séries ») : n'importe quel abonnement actif suffit.
        if not ids:
            return "ouvert" if self.abonnements else "verrouille"
        return "ouvert" if ids & self.abonnements else "verrouille"


class _Etiquettes:
    """Libellé court d'un cursus (« BAC C », « BEPC ») - le nom d'examen peut varier d'un pays à
    l'autre (voir catalog.models.ExamenLabel), d'où le cache par (pays, examen)."""

    def __init__(self):
        self._examens = {}

    def cursus(self, cursus):
        cle = (cursus.country_id, cursus.examen)
        if cle not in self._examens:
            self._examens[cle] = resolve_examen_label(cursus.country, cursus.examen)
        serie = cursus.series.code if cursus.series_id else ""
        return f"{self._examens[cle]} {serie}".strip()


def serialiser(entree, acces, etiquettes, *, cursus_prefere=None, nb=None, extrait=""):
    niveau = acces.niveau(entree)
    cursus = sorted(entree.cursus.all(), key=lambda c: c.id)
    ids = [c.id for c in cursus]
    # Cursus vers lequel les liens d'un thème/quiz mènent : celui de l'élève s'il en fait partie.
    cursus_cible = cursus_prefere if cursus_prefere in ids else (ids[0] if ids else None)
    apercu = extrait or entree.apercu
    if entree.type == TypeResultat.QUIZ and niveau == "verrouille":
        apercu = ""  # l'énoncé d'une question de quiz n'est montré qu'à qui peut la jouer
    return {
        "id": entree.id,
        "type": entree.type,
        "titre": entree.titre,
        "apercu": apercu,
        "annee": entree.annee,
        "matiere": {"code": entree.matiere.code, "label": entree.matiere.label},
        "cursus": [{"id": c.id, "label": etiquettes.cursus(c)} for c in cursus[:4]],
        "cursus_total": len(cursus),
        "tous_cursus": entree.tous_cursus,
        "cursus_cible": cursus_cible,
        "acces": niveau,
        "nb": nb,
        "details": {cle: valeur for cle, valeur in entree.meta.items() if cle != "acces_ids"},
    }


def _entrees(ids):
    return {
        e.id: e for e in EntreeRecherche.objects.filter(id__in=ids)
        .select_related("matiere").prefetch_related("cursus__series", "cursus__country")
    }


def _extraits(tranches, entrees, jetons):
    """{id d'entrée: passage du texte public où le mot cherché apparaît} pour les cours, épreuves et
    exercices affichés dont le TITRE n'explique pas la correspondance (« Mathématiques BEPC 2024 »
    pour la requête « thalès » : sans le passage, l'élève ne sait pas pourquoi il est là). Relu dans
    la source - jamais dans l'index, qui ne garde que du texte sans accents ni casse - et pour les
    seules lignes affichées : une poignée de requêtes groupées."""
    voulus = defaultdict(dict)  # type -> {objet_id: id d'entrée}
    for type_groupe in (TypeResultat.COURS.value, TypeResultat.EPREUVE.value, TypeResultat.EXERCICE.value):
        for _s, i, _nb in tranches.get(type_groupe, ()):
            entree = entrees.get(i)
            if entree and not all(j in entree.titre_norm for j in jetons if texte.est_requis(j)):
                voulus[type_groupe][entree.objet_id] = i

    sources = {}
    if voulus[TypeResultat.COURS.value]:
        for cours in Cours.objects.filter(id__in=voulus[TypeResultat.COURS.value]).only("id", "sections_raw"):
            sources[voulus[TypeResultat.COURS.value][cours.id]] = texte_public_cours(cours.sections_raw)
    if voulus[TypeResultat.EXERCICE.value]:
        for exercice in Exercise.objects.filter(id__in=voulus[TypeResultat.EXERCICE.value]).only(
            "id", "enonce_intro_markdown", "enonce_markdown",
        ):
            sources[voulus[TypeResultat.EXERCICE.value][exercice.id]] = (
                f"{exercice.enonce_intro_markdown}\n{exercice.enonce_markdown}"
            )
    if voulus[TypeResultat.EPREUVE.value]:
        par_epreuve = defaultdict(list)
        for lesson_id, intro, enonce in Exercise.objects.filter(
            lesson_id__in=voulus[TypeResultat.EPREUVE.value], statut=StatutContenu.VALIDE,
        ).order_by("numero_exercice").values_list("lesson_id", "enonce_intro_markdown", "enonce_markdown"):
            par_epreuve[lesson_id].append(f"{intro}\n{enonce}")
        for lesson_id, entree_id in voulus[TypeResultat.EPREUVE.value].items():
            sources[entree_id] = "\n\n".join(par_epreuve.get(lesson_id, ()))
    extraits = {}
    for entree_id, source in sources.items():
        passage = texte.extrait(source, jetons, LONGUEUR_EXTRAIT)
        if passage:
            extraits[entree_id] = passage

    # Aucun passage : la correspondance vient des THÈMES étiquetés (l'index les range dans les clés
    # d'une épreuve ou d'un exercice). On montre le thème, plus parlant que l'ouverture du sujet.
    requis = [j for j in jetons if texte.est_requis(j)]
    for type_groupe, lien in (
        (TypeResultat.EPREUVE.value, Lesson.themes.through),
        (TypeResultat.EXERCICE.value, Exercise.themes.through),
    ):
        sans_passage = {oid: eid for oid, eid in voulus[type_groupe].items() if eid not in extraits}
        if not sans_passage:
            continue
        cle = "lesson_id" if type_groupe == TypeResultat.EPREUVE.value else "exercise_id"
        correspondants = defaultdict(list)
        for objet_id, nom in lien.objects.filter(**{f"{cle}__in": list(sans_passage)}).values_list(cle, "tag__name"):
            normalise = f" {texte.normaliser(nom)}"
            if any(f" {j}" in normalise for j in requis) and nom not in correspondants[objet_id]:
                correspondants[objet_id].append(nom)
        for objet_id, noms in correspondants.items():
            extraits[sans_passage[objet_id]] = "Thème : " + " · ".join(noms[:3])
    return extraits


def _habiller(classement, par_groupe, decalage, type_, acces, cursus_prefere, jetons, types_voulus=()):
    """Tranche chaque groupe, relit les lignes retenues et les sérialise. Les types que la requête réclame
    (« corrigé », « cours »...) passent en premier : ils ne sont jamais les seuls renvoyés, mais ils ouvrent la liste."""
    ordre = [t for t in ORDRE_GROUPES if t in types_voulus] + [t for t in ORDRE_GROUPES if t not in types_voulus]
    tranches = {}
    for type_groupe in ordre:
        liste = classement.get(type_groupe)
        if not liste:
            continue
        tranches[type_groupe] = liste[decalage:decalage + par_groupe] if type_ else liste[:par_groupe]
    entrees = _entrees([i for tranche in tranches.values() for _, i, _nb in tranche])
    extraits = _extraits(tranches, entrees, jetons)
    etiquettes = _Etiquettes()
    groupes = []
    for type_groupe in ordre:
        if type_groupe not in tranches:
            continue
        resultats = [
            serialiser(
                entrees[i], acces, etiquettes, cursus_prefere=cursus_prefere, nb=nb, extrait=extraits.get(i, ""),
            )
            for _s, i, nb in tranches[type_groupe] if i in entrees
        ]
        groupes.append({
            "type": type_groupe, "libelle": TypeResultat(type_groupe).label,
            "total": len(classement[type_groupe]), "resultats": resultats,
        })
    return groupes


def _theme_generique(titre_norm):
    """Vrai pour un « thème » qui n'en est pas un : « Terminale C », « BEPC », « bac d »... Ces étiquettes
    de niveau sont rattachées à des centaines de contenus (donc en tête du classement par volume) mais
    ne désignent aucune notion à travailler."""
    mots = titre_norm.split()
    return not mots or all(mot in texte.MOTS_DE_NIVEAU for mot in mots)


def _suggestions(pays, cursus_id, acces, nombre=NB_SUGGESTIONS):
    """Thèmes les plus riches du pays (et du cursus), proposés quand rien ne correspond. Les étiquettes de
    niveau (« Terminale C », « BEPC ») sont écartées : elles dominent le classement par volume sans rien
    proposer à étudier."""
    queryset = EntreeRecherche.objects.filter(pays=pays, type=TypeResultat.THEME)
    if cursus_id:
        lien = EntreeRecherche.cursus.through.objects.filter(entreerecherche_id=OuterRef("pk"), cursus_id=cursus_id)
        queryset = queryset.filter(Q(tous_cursus=True) | Exists(lien))
    # Une marge : quelques-uns des premiers seront écartés.
    candidats = queryset.order_by("-poids", "id").values_list("id", "titre_norm")[: nombre * 6]
    ids = [i for i, titre_norm in candidats if not _theme_generique(titre_norm)][:nombre]
    entrees = _entrees(ids)
    etiquettes = _Etiquettes()
    return [serialiser(entrees[i], acces, etiquettes, cursus_prefere=cursus_id) for i in ids if i in entrees]


def _repartition_matieres(classement, matiere_de):
    """[{code, label, total}] des matières présentes dans les résultats, la plus fournie d'abord - le
    même décompte que `total` (un thème, un cours, une question groupée comptent chacun pour un)."""
    compteur = Counter(matiere_de[i] for liste in classement.values() for _s, i, _nb in liste)
    if not compteur:
        return []
    matieres = {s.id: s for s in Subject.objects.filter(id__in=compteur)}
    return [
        {"code": matieres[mid].code, "label": matieres[mid].label, "total": total}
        for mid, total in compteur.most_common() if mid in matieres
    ]


def _requete_corrigee(requete, corrections):
    """La requête de l'élève dont seuls les mots fautifs sont remplacés (les autres gardent leur
    graphie et leurs accents) - c'est ce qu'on lui montre : « Résultats pour équation du second degré »."""
    mots = []
    for mot in str(requete).split():
        normalise = texte.racine(texte.normaliser(mot))
        mots.append(corrections.get(normalise, mot))
    return " ".join(mots)


def _recherche(pays, jetons, intention, *, cursus, matiere, type_, corriger_auto, requete):
    """Une recherche complète avec UNE interprétation de la requête. Renvoie (lignes, termes, corrige) :
    `corrige` est la requête corrigée à montrer à l'élève, ou None."""
    termes = _termes(intention.restants)
    cursus_ids = intention.cursus_ids or ([cursus] if cursus else None)
    filtres = {
        "cursus_ids": cursus_ids, "matiere": matiere, "matieres": intention.matiere_codes or None,
        "annees": intention.annees or None, "type_": type_,
    }
    if not any(t.requis for t in termes) and not intention.filtres():
        return [], termes, None
    lignes = _lignes(pays, termes, **filtres)
    corrige = None
    if not lignes and corriger_auto:
        requis = [t.texte for t in termes if t.requis]
        corrections = corriger(requis)
        if corrections:
            termes_corriges = _termes([corrections.get(t.texte, t.texte) for t in termes])
            lignes_corrigees = _lignes(pays, termes_corriges, **filtres)
            if lignes_corrigees:
                lignes, termes = lignes_corrigees, termes_corriges
                corrige = _requete_corrigee(requete, corrections)
    return lignes, termes, corrige


def chercher(
    requete, *, pays, utilisateur=None, cursus=None, matiere=None, type_=None,
    limite=LIMITE_DEFAUT, decalage=0, elargir=False, corriger_auto=True, sans=(),
):
    """
    Cherche `requete` dans l'index du `pays` (instance de catalog.Country).

    `cursus` (id) restreint aux contenus proposés à cet examen - plus ceux « de tous les
    examens » - sauf `elargir`. `type_` ne garde qu'un groupe (et alors `decalage`/`limite`
    paginent ce groupe seul) ; sans lui, chaque groupe renvoie ses `limite` premiers résultats.
    `corriger_auto=False` : ne pas retenter avec le mot du catalogue le plus proche quand rien ne
    correspond (l'élève a refusé la suggestion).

    `sans` : parties de l'intention à ne pas interpréter (voir intention.PARTIES) - l'élève a retiré la
    pastille « BAC C » ou « 2019 », ces mots redeviennent des mots à chercher.
    """
    limite = max(1, min(int(limite), LIMITE_MAX))
    decalage = max(0, int(decalage))
    if type_ and type_ not in ORDRE_GROUPES:
        type_ = None
    filtre_cursus = None if elargir else cursus
    acces = _Acces(utilisateur)
    sans = frozenset(sans) & frozenset(comprendre.PARTIES)

    reponse = {
        "q": str(requete or "").strip()[:LONGUEUR_MAX_REQUETE],
        "corrige": None,
        "indexe": EntreeRecherche.objects.exists(),
        "trop_court": False,
        "total": 0,
        "groupes": [],
        "autres_cursus": 0,
        "matieres": [],
        "suggestions": [],
        "intention": None,
        "reponse": None,
    }
    jetons = _analyser(requete)
    intention = comprendre.analyser(jetons, pays, sans)
    if not any(synonymes.est_requis(j) for j in intention.restants) and not intention.filtres():
        reponse["trop_court"] = bool(jetons or reponse["q"])
        if not reponse["q"]:
            # Aucune requête (la page de recherche vient de s'ouvrir) : les thèmes de l'examen de l'élève, de
            # quoi commencer sans rien taper.
            reponse["suggestions"] = _suggestions(pays, filtre_cursus, acces, NB_SUGGESTIONS_ACCUEIL)
        return reponse

    # La matière choisie dans l'interface ne filtre PAS en SQL : la répartition par matière doit rester
    # visible une fois l'une d'elles choisie (« tangente » : maths, physique, chimie), pour pouvoir en
    # changer d'un clic.
    lignes, termes, corrige = _recherche(
        pays, jetons, intention, cursus=filtre_cursus, matiere=None, type_=type_,
        corriger_auto=corriger_auto, requete=requete,
    )
    ignoree = False
    if not lignes and (intention.filtres() or intention.types):
        # Une interprétation qui ne donne rien est abandonnée : mieux vaut chercher les mots tels quels que
        # répondre « aucun résultat » à une requête dont on a mal deviné le sens.
        intention = comprendre.analyser(jetons, pays, frozenset(comprendre.PARTIES))
        ignoree = True
        lignes, termes, corrige = _recherche(
            pays, jetons, intention, cursus=filtre_cursus, matiere=None, type_=type_,
            corriger_auto=corriger_auto, requete=requete,
        )
    reponse["corrige"] = corrige

    # L'examen « de l'élève » pour le classement : celui qu'il a déclaré, sinon celui que sa requête nomme.
    cursus_eleve = cursus or (intention.cursus_ids[0] if intention.cursus_ids else None)
    classement = _classer(lignes, termes, _signaux(cursus_eleve))
    matiere_de = {ligne[0]: ligne[7] for ligne in lignes}
    reponse["matieres"] = _repartition_matieres(classement, matiere_de)
    matiere_id = None
    if matiere:
        matiere_id = Subject.objects.filter(country=pays, code=matiere).values_list("id", flat=True).first()
        classement = {
            type_groupe: gardes for type_groupe, liste in classement.items()
            if (gardes := [e for e in liste if matiere_de[e[1]] == matiere_id])
        }
        lignes = [ligne for ligne in lignes if ligne[7] == matiere_id]
    jetons_affiches = [t.texte for t in termes]
    reponse["groupes"] = _habiller(
        classement, limite, decalage, type_, acces, cursus, jetons_affiches, intention.types,
    )
    reponse["total"] = sum(len(liste) for liste in classement.values())
    reponse["intention"] = {**intention.en_clair(), "ignoree": ignoree}
    # Seulement sur la vue d'ensemble : la carte répond à la requête, pas à un onglet ni à une page suivante.
    if not type_ and not decalage:
        reponse["reponse"] = _carte_reponse(classement, termes, intention, acces, cursus)

    if filtre_cursus and not intention.cursus_ids and reponse["total"] < SEUIL_AUTRES_CURSUS:
        filtres = {"type_": type_, "matieres": intention.matiere_codes or None, "annees": intention.annees or None}
        if matiere:
            filtres["matiere"] = matiere
        ailleurs = _queryset(pays, termes, **filtres).count()
        reponse["autres_cursus"] = max(0, ailleurs - len(lignes))
    if reponse["total"] == 0:
        reponse["suggestions"] = _suggestions(pays, filtre_cursus, acces)
    return reponse


# --- Carte-réponse -------------------------------------------------------------------

# Une carte-réponse ne répond qu'à une question COURTE (« loi d'ohm », « théorème de thalès ») : au-delà, la
# requête cherche autre chose qu'une définition.
CARTE_MAX_TERMES = 4
# Combien de mots plus long que la requête le titre du cours peut être (« Loi d'Ohm dans un circuit électrique »
# répond à « loi d'ohm », « Photosynthèse et respiration cellulaire » à « photosynthèse »).
CARTE_MARGE_TITRE = 3
CARTE_CANDIDATS = 5


def _carte_reponse(classement, termes, intention, acces, cursus_prefere):
    """
    La RÈGLE du cours qui répond le mieux à la requête, montrée en tête des résultats - pour « loi d'ohm », la
    formule et son énoncé, sans ouvrir le cours. Rien n'est inventé : c'est la section « règle » d'un cours
    existant, que son aperçu public montre déjà à un visiteur non abonné.

    Seulement quand tout est net : une requête courte, sans type voulu, dont tous les mots exigés sont DANS le
    titre d'un cours qui a une règle, et dans la MÊME matière que le thème arrivé en tête (« dérivation » est
    d'abord un thème de maths : un circuit électrique « en dérivation » n'y répond pas). Sinon None : une carte
    hors sujet est pire qu'aucune carte.
    """
    requis = [t for t in termes if t.requis]
    if intention.types or not requis or len(requis) > CARTE_MAX_TERMES:
        return None
    candidats = classement.get(TypeResultat.COURS.value, [])[:CARTE_CANDIDATS]
    if not candidats:
        return None
    themes = classement.get(TypeResultat.THEME.value, [])
    matiere_du_theme = (
        EntreeRecherche.objects.filter(id=themes[0][1]).values_list("matiere_id", flat=True).first() if themes else None
    )
    entrees = {
        e.id: e for e in EntreeRecherche.objects.filter(id__in=[i for _s, i, _n in candidats])
        .select_related("matiere").prefetch_related("cursus__series", "cursus__country")
    }
    etiquettes = _Etiquettes()
    retenus = []
    for _score_, entree_id, _nb in candidats:
        entree = entrees.get(entree_id)
        regle = (entree.meta.get("regle_md") or "") if entree else ""
        if not regle or (matiere_du_theme and entree.matiere_id != matiere_du_theme):
            continue
        mots = entree.titre_norm.split()
        utiles = [m for m in mots if m not in texte.MOTS_VIDES]
        if len(utiles) > len(requis) + CARTE_MARGE_TITRE:
            continue
        if all(any(_points(f, mots, entree.titre_norm, "")[0] >= 8 for f in terme.formes) for terme in requis):
            retenus.append((entree, regle))
    if not retenus:
        return None
    # Le mieux classé : le classement pèse déjà fréquence, niveau et popularité ; le titre le plus court n'est pas
    # un meilleur juge (« Le théorème de Thalès dans un cône » est plus court que le cours de référence).
    entree, regle = retenus[0]
    return {**serialiser(entree, acces, etiquettes, cursus_prefere=cursus_prefere), "regle_md": regle}


# --- Complétion pendant la frappe -----------------------------------------------------

NB_COMPLETIONS = 8


def completer(requete, *, pays, cursus=None, limite=NB_COMPLETIONS):
    """
    Ce que l'élève est PEUT-ÊTRE en train d'écrire : des intitulés de thèmes qui contiennent tous les mots
    tapés, le dernier comme début de mot (« theoreme tha » -> « théorème de Thalès »). Les plus riches d'abord,
    sans les étiquettes de niveau, un seul par intitulé. Des thèmes seulement : ce sont les formulations les plus
    courtes et les plus proches de ce qu'on tape ; les titres de cours et d'épreuves sont des phrases.
    """
    jetons = texte.jetons(str(requete or "")[:LONGUEUR_MAX_REQUETE])
    if not jetons or len(jetons[-1]) < 2:
        return []
    queryset = EntreeRecherche.objects.filter(pays=pays, type=TypeResultat.THEME)
    if cursus:
        lien = EntreeRecherche.cursus.through.objects.filter(entreerecherche_id=OuterRef("pk"), cursus_id=cursus)
        queryset = queryset.filter(Q(tous_cursus=True) | Exists(lien))
    for jeton in jetons:
        queryset = queryset.filter(Q(titre_norm__startswith=jeton) | Q(titre_norm__contains=f" {jeton}"))
    vus, resultat = set(), []
    lignes = queryset.order_by("-poids", "id").values_list("titre", "titre_norm", "matiere__label")[: limite * 6]
    for titre, titre_norm, matiere in lignes:
        if titre_norm in vus or _theme_generique(titre_norm):
            continue
        vus.add(titre_norm)
        resultat.append({"texte": titre, "matiere": matiere})
        if len(resultat) >= limite:
            break
    return resultat


# --- Journal des recherches vides ------------------------------------------------------


def journaliser_vide(requete, pays_code):
    """
    Compte une recherche qui n'a rien donné (voir RechercheSansResultat pour le pourquoi et les
    écarts assumés avec analytics). Garde-fous : requête normalisée et plafonnée, jamais de
    numéro (téléphone, matricule) ni d'adresse e-mail, jamais une phrase entière collée, table
    bornée. Renvoie True si la requête a été comptée.
    """
    brut = str(requete or "")
    normalisee = texte.normaliser(brut)[:JOURNAL_LONGUEUR_MAX].strip()
    if not (JOURNAL_LONGUEUR_MIN <= len(normalisee)) or "@" in brut:
        return False
    if len(normalisee.split()) > JOURNAL_MAX_JETONS:
        return False
    if len(re.sub(r"\D", "", normalisee)) > JOURNAL_MAX_CHIFFRES:
        return False

    code = str(pays_code or "")[:10].lower()
    existante = RechercheSansResultat.objects.filter(requete=normalisee, pays_code=code)
    if existante.exists():
        existante.update(nb=F("nb") + 1, derniere_fois=timezone.now())
        return True
    if RechercheSansResultat.objects.count() >= JOURNAL_MAX_LIGNES:
        return False
    _, cree = RechercheSansResultat.objects.get_or_create(requete=normalisee, pays_code=code)
    if not cree:
        RechercheSansResultat.objects.filter(requete=normalisee, pays_code=code).update(
            nb=F("nb") + 1, derniere_fois=timezone.now(),
        )
    return True
