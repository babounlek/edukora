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
from collections import Counter, defaultdict

from django.db.models import Exists, F, OuterRef, Q
from django.db.models.functions import Length
from django.utils import timezone

from access.services import bulk_active_inedite_cursus_ids, bulk_active_subscription_cursus_ids
from catalog.models import Cours, Exercise, Lesson, StatutContenu, Subject, resolve_examen_label

from . import texte
from .indexation import texte_public_cours
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


# --- Étape 1 : candidats ---------------------------------------------------------------


def _queryset(pays, requis, *, cursus_id=None, matiere=None, type_=None):
    queryset = EntreeRecherche.objects.filter(pays=pays)
    if matiere:
        queryset = queryset.filter(matiere__code=matiere)
    if type_:
        queryset = queryset.filter(type=type_)
    if cursus_id:
        lien = EntreeRecherche.cursus.through.objects.filter(
            entreerecherche_id=OuterRef("pk"), cursus_id=cursus_id,
        )
        queryset = queryset.filter(Q(tous_cursus=True) | Exists(lien))
    for jeton in requis:
        # Début de mot : l'index range ses textes entourés d'espaces (voir indexation._cles).
        debut = f" {jeton}"
        queryset = queryset.filter(Q(cles_norm__contains=debut) | Q(texte_norm__contains=debut))
    return queryset


def _lignes(pays, requis, **filtres):
    return list(
        _queryset(pays, requis, **filtres).values_list(
            "id", "type", "titre_norm", "cles_norm", "annee", "groupe", "poids", "matiere_id",
        )[:PLAFOND_CANDIDATS],
    )


# --- Étape 2 : classement --------------------------------------------------------------


def _suite_de_mots(mots, jetons):
    """Vrai si `jetons` apparaissent consécutivement (chacun comme début de mot) dans `mots`."""
    taille = len(jetons)
    return any(
        all(mots[i + k].startswith(jetons[k]) for k in range(taille))
        for i in range(len(mots) - taille + 1)
    )


def _score(ligne, jetons, requis):
    _id, _type, titre_norm, cles_norm, annee, _groupe, poids, _matiere = ligne
    mots = titre_norm.split()
    score = 0.0
    hors_titre = 0
    for jeton in jetons:
        court = len(jeton) < 3
        # Un jeton court (« d », « ti ») ne vaut que comme MOT entier : en préfixe il toucherait
        # n'importe quel mot qui commence par la même lettre.
        if jeton in mots:
            score += 12
        elif not court and any(m.startswith(jeton) for m in mots):
            score += 8
        elif (f" {jeton} " if court else f" {jeton}") in cles_norm:
            score += 4
            hors_titre += jeton in requis
        elif not court and jeton in titre_norm:
            score += 2
        elif jeton in requis:
            score += 1  # trouvé seulement dans le texte
            hors_titre += 1
    if len(requis) > 0 and hors_titre == 0:
        score += 10  # tous les mots exigés sont dans le titre
    if len(jetons) > 1:
        utiles = [m for m in mots if m not in texte.MOTS_VIDES]
        if _suite_de_mots(utiles, jetons):
            score += 15  # l'expression exacte, dans l'ordre
    # Départages : titre court (plus précis), contenu abondant (thème riche), année récente.
    score -= 0.15 * len(mots)
    score += 0.5 * min(math.log2(1 + poids), 6)
    score += (annee or 0) / 10000
    return score


def _classer(lignes, jetons, requis):
    """{type: [(score, id, nb)]} trié par score décroissant. Les questions de quiz d'un même
    thème forment UN résultat (nb = nombre de questions qui correspondent), et disparaissent si
    ce thème est déjà proposé en tant que thème - sa carte donne déjà accès au quiz."""
    par_type = defaultdict(list)
    for ligne in lignes:
        par_type[ligne[1]].append((_score(ligne, jetons, requis), ligne[0], ligne[5]))

    themes_proposes = {groupe for _, _, groupe in par_type.get(TypeResultat.THEME.value, ())}
    quiz = {}
    for score, entree_id, groupe in sorted(par_type.get(TypeResultat.QUIZ.value, ()), reverse=True):
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
        resultat[type_] = sorted(((s, i, None) for s, i, _g in entrees), key=lambda e: (-e[0], e[1]))
    if quiz:
        resultat[TypeResultat.QUIZ.value] = sorted(
            ((s, i, nb) for s, i, nb in quiz.values()), key=lambda e: (-e[0], e[1]),
        )
    return resultat


# --- Fautes de frappe ------------------------------------------------------------------


def corriger(jetons):
    """{jeton: mot du catalogue le plus proche} pour les jetons qui n'existent nulle part (même
    pas comme début de mot). Une ou deux fautes selon la longueur du mot ; à distance égale, le
    mot le plus fréquent du catalogue gagne. Même initiale exigée : sans cela, comparer chaque mot
    à tout le vocabulaire coûterait des secondes."""
    corrections = {}
    for jeton in jetons:
        if len(jeton) < 4 or TermeRecherche.objects.filter(terme__startswith=jeton).exists():
            continue
        tolerance = 1 if len(jeton) <= 5 else 2
        proches = (
            TermeRecherche.objects.filter(terme__startswith=jeton[0])
            .annotate(longueur=Length("terme"))
            .filter(longueur__gte=len(jeton) - tolerance, longueur__lte=len(jeton) + tolerance)
            .values_list("terme", "frequence")
        )
        meilleur = None
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


def _habiller(classement, par_groupe, decalage, type_, acces, cursus_prefere, jetons):
    """Tranche chaque groupe, relit les lignes retenues et les sérialise."""
    tranches = {}
    for type_groupe in ORDRE_GROUPES:
        liste = classement.get(type_groupe)
        if not liste:
            continue
        tranches[type_groupe] = liste[decalage:decalage + par_groupe] if type_ else liste[:par_groupe]
    entrees = _entrees([i for tranche in tranches.values() for _, i, _nb in tranche])
    extraits = _extraits(tranches, entrees, jetons)
    etiquettes = _Etiquettes()
    groupes = []
    for type_groupe in ORDRE_GROUPES:
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


def _suggestions(pays, cursus_id, acces):
    """Thèmes les plus riches du pays (et du cursus), proposés quand rien ne correspond. Les étiquettes de
    niveau (« Terminale C », « BEPC ») sont écartées : elles dominent le classement par volume sans rien
    proposer à étudier."""
    queryset = EntreeRecherche.objects.filter(pays=pays, type=TypeResultat.THEME)
    if cursus_id:
        lien = EntreeRecherche.cursus.through.objects.filter(entreerecherche_id=OuterRef("pk"), cursus_id=cursus_id)
        queryset = queryset.filter(Q(tous_cursus=True) | Exists(lien))
    # Une marge : quelques-uns des premiers seront écartés.
    candidats = queryset.order_by("-poids", "id").values_list("id", "titre_norm")[:NB_SUGGESTIONS * 6]
    ids = [i for i, titre_norm in candidats if not _theme_generique(titre_norm)][:NB_SUGGESTIONS]
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


def chercher(
    requete, *, pays, utilisateur=None, cursus=None, matiere=None, type_=None,
    limite=LIMITE_DEFAUT, decalage=0, elargir=False, corriger_auto=True,
):
    """
    Cherche `requete` dans l'index du `pays` (instance de catalog.Country).

    `cursus` (id) restreint aux contenus proposés à cet examen - plus ceux « de tous les
    examens » - sauf `elargir`. `type_` ne garde qu'un groupe (et alors `decalage`/`limite`
    paginent ce groupe seul) ; sans lui, chaque groupe renvoie ses `limite` premiers résultats.
    `corriger_auto=False` : ne pas retenter avec le mot du catalogue le plus proche quand rien ne
    correspond (l'élève a refusé la suggestion).
    """
    limite = max(1, min(int(limite), LIMITE_MAX))
    decalage = max(0, int(decalage))
    if type_ and type_ not in ORDRE_GROUPES:
        type_ = None
    filtre_cursus = None if elargir else cursus
    acces = _Acces(utilisateur)

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
    }
    jetons = _analyser(requete)
    requis = [j for j in jetons if texte.est_requis(j)]
    if not requis:
        reponse["trop_court"] = bool(jetons or reponse["q"])
        return reponse

    # La matière ne filtre PAS en SQL : la répartition par matière doit rester visible une fois l'une
    # d'elles choisie (« tangente » : maths, physique, chimie), pour pouvoir en changer d'un clic.
    filtres = {"cursus_id": filtre_cursus, "type_": type_}
    lignes = _lignes(pays, requis, **filtres)
    if not lignes and corriger_auto:
        corrections = corriger(requis)
        if corrections:
            jetons_corriges = [corrections.get(j, j) for j in jetons]
            requis_corriges = [j for j in jetons_corriges if texte.est_requis(j)]
            lignes_corrigees = _lignes(pays, requis_corriges, **filtres)
            if lignes_corrigees:
                lignes, jetons, requis = lignes_corrigees, jetons_corriges, requis_corriges
                reponse["corrige"] = _requete_corrigee(requete, corrections)

    classement = _classer(lignes, jetons, requis)
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
    reponse["groupes"] = _habiller(classement, limite, decalage, type_, acces, cursus, jetons)
    reponse["total"] = sum(len(liste) for liste in classement.values())

    if filtre_cursus and reponse["total"] < SEUIL_AUTRES_CURSUS:
        ailleurs = _queryset(pays, requis, type_=type_).count()
        if matiere:
            ailleurs = _queryset(pays, requis, type_=type_, matiere=matiere).count()
        reponse["autres_cursus"] = max(0, ailleurs - len(lignes))
    if reponse["total"] == 0:
        reponse["suggestions"] = _suggestions(pays, filtre_cursus, acces)
    return reponse


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
