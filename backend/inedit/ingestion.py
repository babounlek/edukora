"""
Traduit la sortie JSON de la future skill de conception d'épreuves inédites vers
inedit.Blueprint/EpreuveInedite. Réutilise volontairement les résolveurs de
catalog.ingestion (IngestionError, _resolve_subject, _resolve_cursus_list,
_resolve_country, _normalize_qcm_choix, DIFFICULTE_MAP...) plutôt que de les dupliquer -
même référentiel pays/matière/cursus/difficulté que catalog.Question et
quiz.CompetenceItem (voir la note "consistance correction-experte" côté mémoire projet).

Pipeline en DEUX temps distincts, jamais fusionnés (contrainte non négociable de
l'audit "Épreuves Inédites" - "un blueprint doit être validé avant la génération") :
1. ingest_blueprint - crée un Blueprint en statut=BROUILLON. Ne génère aucun contenu
   élève. Nécessite une validation humaine (admin, action "Marquer Validé") avant de
   pouvoir servir de base à une génération.
2. ingest_epreuve_inedite - génère une EpreuveInedite à partir d'un Blueprint DÉJÀ
   VALIDE (résolu par blueprint_external_id, jamais créé à la volée ici) - lève
   IngestionError si le blueprint est introuvable ou pas encore validé, pour ne jamais
   laisser un même passage créer ET valider ET consommer un blueprint dans le même
   souffle. Créée elle aussi en statut=BROUILLON (décision "statut de publication par
   défaut", même audit) - contrairement à quiz.CompetenceItem, la publication reste un
   geste humain explicite (inedit.admin), jamais automatique à l'ingestion.

Convention de dossier : `ingest/_inedit/<code_pays>/...`, même raisonnement que
`ingest/_quiz/<code_pays>/...` (voir quiz.ingestion) - réutilise le bind mount Docker
existant de `ingest/`. `_inedit` (préfixe underscore) est déjà exclu automatiquement de
catalog.ingestion.run_ingestion (exclusion généralisée à tout préfixe `_`, voir la
mémoire projet "feedback_correction_experte_consistency", Dixième vérification) -
aucune modification de catalog.ingestion nécessaire pour ce nouveau sous-dossier.

Chaque fichier JSON porte un objet UNIQUE (pas un tableau, contrairement à
quiz.ingestion), avec un champ `type` ("blueprint" ou "epreuve") qui détermine la
fonction d'ingestion appelée - explicite plutôt que deviné depuis la forme du JSON, un
Blueprint et une EpreuveInedite partageant trop de champs (titre, matiere/subject,
cursus) pour un tri fiable par simple présence de clé.
"""

import json
import re
from pathlib import Path

from django.db import transaction

from catalog.ingestion import (
    DIFFICULTE_MAP,
    IngestionError,
    _get_or_create_tags,
    _link_tags_to_savoir,
    _normalize,
    _normalize_qcm_choix,
    _repair_double_json_escaping,
    _repair_missing_matrix_row_separators,
    _resolve_country,
    _resolve_cursus_list,
    _resolve_savoir_officiel,
    _resolve_subject,
    _strip_em_dash,
    _validate_pays_matches_country,
)
from catalog.ingestion_repairs import _repair_dict_shaped_cours_sections
from catalog.models import Cours, Cursus, Exercise, Lesson, Question, StatutContenu, Subject, Tag, TypeReponse
from programme.models import Savoir

from .models import Blueprint, EpreuveInedite, ExerciceInedite, QuestionInedite, RappelDeMethodeInedite
from .quality import calculer_scores

SELECTION_FLOOR = 2
SELECTION_LIMIT = 5
SELECTION_MAX_REFERENCE_EXERCISES = 4

BLUEPRINT_REQUIRED_KEYS = ["external_id", "titre", "matiere", "cursus", "competences"]
EPREUVE_REQUIRED_KEYS = ["external_id", "titre", "blueprint_external_id", "exercices"]


def _country_code_from_inedit_ingest_path(path):
    """Variante de catalog.ingestion._country_code_from_path, ancrée sur le segment
    `_inedit` plutôt que `ingest` - voir la convention de dossier en tête de module."""
    parts = Path(path).resolve().parts
    lowered = [p.lower() for p in parts]
    if "_inedit" not in lowered:
        return None
    idx = lowered.index("_inedit")
    if idx + 1 >= len(parts):
        return None
    return parts[idx + 1]


def _resolve_cursus_from_entries(cursus_data, country):
    """
    Un Blueprint/une EpreuveInedite peut cibler plusieurs cursus à la fois (ex. Maths BAC
    C/E) - même besoin et même contrat JSON que quiz.ingestion._resolve_cursus_from_entries,
    copié ici plutôt qu'importé (voir la note "consistance correction-experte" côté mémoire
    projet, même arbitrage que ResultatDeclare plus haut dans ce module : détail
    d'implémentation trop mineur pour justifier une dépendance inter-app).

    `cursus_data` : liste d'objets {"examen": "bac", "serie": "C"} (serie omise/vide pour
    un examen sans série, ex. BEPC) - chaque entrée est résolue via _resolve_cursus_list,
    qui gère déjà nativement une `serie` combinée type "C-E" (voir _split_series côté
    catalog.ingestion) : une épreuve commune à plusieurs séries peut donc être décrite
    soit par plusieurs entrées, soit par une seule entrée à `serie` combinée.
    """
    if not cursus_data:
        raise IngestionError("cursus est requis et doit contenir au moins une entrée.")

    cursus_list = []
    seen = set()
    for entry in cursus_data:
        if not isinstance(entry, dict) or not entry.get("examen"):
            raise IngestionError(f"Entrée cursus invalide (examen manquant) : {entry!r}")
        for cursus in _resolve_cursus_list(entry["examen"], entry.get("serie"), country):
            if cursus.pk not in seen:
                seen.add(cursus.pk)
                cursus_list.append(cursus)
    return cursus_list


def _resolve_tags(names):
    """
    Résout une liste de noms vers des Tag déjà existants - doivent avoir été créés via
    correction-experte, jamais inventés par ce pipeline (même principe que
    quiz.ingestion._resolve_theme, appliqué à une liste). Peut retourner une liste
    vide (voir _resolve_competences pour la variante qui l'interdit).
    """
    tags = []
    for name in names or []:
        name = _strip_em_dash(str(name or "")).strip()
        if not name:
            continue
        try:
            tags.append(Tag.objects.get(name=name))
            continue
        except Tag.DoesNotExist:
            pass
        candidats = list(Tag.objects.filter(name__iexact=name))
        if len(candidats) == 1:
            tags.append(candidats[0])
        elif len(candidats) > 1:
            raise IngestionError(f"Plusieurs Tag correspondent à {name!r} à la casse près - ambigu, à corriger à la main.")
        else:
            raise IngestionError(f"Compétence (Tag) introuvable : {name!r} - doit déjà exister en base.")
    return tags


def _resolve_competences(names):
    """
    Compétences (Tag) visées par un Blueprint - un Blueprint d'épreuve complète vise
    généralement plusieurs compétences à la fois, contrairement à un CompetenceItem qui
    en cible exactement une (voir _resolve_tags pour la résolution elle-même, ici
    seulement rendue obligatoire : au moins une compétence).
    """
    if not names:
        raise IngestionError("competences est requis et doit contenir au moins une entrée.")
    tags = _resolve_tags(names)
    if not tags:
        raise IngestionError("competences est requis et doit contenir au moins une entrée valide.")
    return tags


def _find_undercovered_subject_cursus(country, floor):
    """
    Couples (Subject, Cursus) de ce pays, restreints à ceux qui ont déjà du contenu réel
    validé (Lesson) pour servir de matériel de référence, avec moins de `floor`
    Blueprint VALIDE - granularité (matière, cursus), pas juste compétence
    (quiz.ingestion._find_undercovered_competencies raisonne par compétence isolée ; un
    blueprint d'épreuve complète en couvre plusieurs par construction, donc la bonne
    unité de couverture est le couple matière/cursus visé).
    """
    pairs = (
        Lesson.objects.filter(statut=StatutContenu.VALIDE, cursus__country=country)
        .values("subject", "cursus")
        .distinct()
    )
    candidates = []
    seen = set()
    for pair in pairs:
        key = (pair["subject"], pair["cursus"])
        if key in seen:
            continue
        seen.add(key)
        subject = Subject.objects.get(pk=pair["subject"])
        cursus = Cursus.objects.get(pk=pair["cursus"])
        covered = Blueprint.objects.filter(subject=subject, cursus=cursus, statut=StatutContenu.VALIDE).count()
        gap = floor - covered
        if gap > 0:
            candidates.append((subject, cursus, gap))

    candidates.sort(key=lambda c: c[2], reverse=True)
    return candidates


def _savoirs_prioritaires(subject, cursus, limit=5):
    """
    Best-effort, purement informatif : les savoirs officiels de ce (matière, cursus)
    avec le moins de Question réelles déjà rattachées (via Tag.savoir_officiel),
    triés du moins couvert au plus couvert - un signal pour équilibrer les compétences
    choisies dans `sections_plan`, jamais un critère qui change le (matière, cursus)
    déjà retenu par _find_undercovered_subject_cursus (celle-ci reste aveugle à la
    couverture par savoir, voir sa docstring - ceci ne fait qu'ajouter un indice pour le
    skill, pas une nouvelle voie de sélection comme côté quiz.ingestion). Liste vide si
    ce (matière, cursus) n'a pas de référentiel programme (aujourd'hui Cameroun+Maths
    uniquement).
    """
    savoirs = Savoir.objects.filter(module__subject=subject, module__cursus=cursus).select_related("module")
    counted = [
        (
            Question.objects.rattachees_au_savoir(savoir).filter(
                exercise__lesson__subject=subject, exercise__lesson__cursus=cursus,
                exercise__statut=StatutContenu.VALIDE,
            ).count(),
            savoir,
        )
        for savoir in savoirs
    ]
    counted.sort(key=lambda c: c[0])
    return [
        {
            "classe": savoir.module.classe, "serie_label": savoir.module.serie_label,
            "module_numero": savoir.module.numero, "savoir_numero": savoir.numero,
            "intitule": savoir.intitule,
        }
        for _, savoir in counted[:limit]
    ]


def _build_blueprint_request(country, subject, cursus, gap):
    exercises = (
        Exercise.objects.filter(
            statut=StatutContenu.VALIDE, lesson__statut=StatutContenu.VALIDE,
            lesson__subject=subject, lesson__cursus=cursus,
        )
        .select_related("lesson")
        .order_by("-lesson__year")[:SELECTION_MAX_REFERENCE_EXERCISES]
    )
    materiel_reference = [
        {
            "exercise_id": exercise.pk, "numero_exercice": exercise.numero_exercice,
            "points": exercise.points, "enonce_markdown": exercise.enonce_markdown,
        }
        for exercise in exercises
    ]

    return {
        "pays": country.code.lower(),
        "matiere": subject.label,
        "cursus": [{"examen": cursus.examen.lower(), "serie": cursus.series.code if cursus.series else ""}],
        "cible": {"nombre_blueprints": gap},
        "materiel_reference": materiel_reference,
        "savoirs_prioritaires": _savoirs_prioritaires(subject, cursus),
    }


def select_inedit_batch(country, limit=SELECTION_LIMIT, floor=SELECTION_FLOOR):
    """
    Sélectionne jusqu'à `limit` couples (matière, cursus) sous-couverts en Blueprint
    VALIDE pour `country`, avec du matériel réel pour ancrer le style/la difficulté -
    pure sélection déterministe, aucun jugement éditorial, jamais le contenu du
    blueprint lui-même. Fonction partagée par la commande CLI `select_inedit_batch` et
    un futur bouton admin (voir quiz.admin.CompetenceItemAdmin.select_batch_view pour
    le précédent, délibérément pas encore répliqué ici - voir le plan de phases).
    """
    candidates = _find_undercovered_subject_cursus(country, floor)[:limit]
    return [_build_blueprint_request(country, subject, cursus, gap) for subject, cursus, gap in candidates]


def ingest_blueprint(data, country):
    """
    Ingère un objet JSON (un Blueprint). Retourne (blueprint, created).

    Idempotent via external_id (voir unique_blueprint_external_id_when_set) : un
    blueprint déjà ingéré n'est jamais modifié - un ré-import ne recouvre pas une
    validation/correction manuelle déjà faite depuis l'admin.

    Créé en statut=BROUILLON, TOUJOURS (voir la docstring de module) : jamais VALIDE à
    l'ingestion, contrairement à quiz.ingestion.ingest_competence_item.
    """
    missing = [key for key in BLUEPRINT_REQUIRED_KEYS if not data.get(key)]
    if missing:
        raise IngestionError(f"Champs obligatoires manquants (blueprint) : {missing}")

    external_id = str(data["external_id"]).strip()
    existing = Blueprint.objects.filter(external_id=external_id).first()
    if existing:
        return existing, False

    subject = _resolve_subject(data["matiere"], country)
    cursus_list = _resolve_cursus_from_entries(data["cursus"], country)
    competences = _resolve_competences(data["competences"])

    with transaction.atomic():
        blueprint = Blueprint.objects.create(
            external_id=external_id,
            subject=subject,
            titre=_strip_em_dash(data["titre"]),
            sections_plan=data.get("sections_plan") or [],
            duree_minutes=data.get("duree_minutes") or None,
            bareme_total=data.get("bareme_total") or None,
            statut=StatutContenu.BROUILLON,
        )
        blueprint.cursus.set(cursus_list)
        blueprint.competences.set(competences)

        # "savoirs_officiels" est un tableau parallèle à "competences" (même index ->
        # même compétence), pas un objet unique : un Blueprint vise plusieurs
        # compétences à la fois (contrairement à un CompetenceItem, voir
        # quiz.ingestion.ingest_competence_item). Optionnel et tolérant : une entrée
        # absente ou à null n'échoue jamais, elle laisse simplement ce tag non lié -
        # zip() tronque proprement si le tableau est plus court que "competences".
        for tag, raw_savoir in zip(competences, data.get("savoirs_officiels") or []):
            _link_tags_to_savoir([tag], _resolve_savoir_officiel(raw_savoir, subject))

    return blueprint, True


# Repère de groupe/exercice ("**PARTIE I : ...**", "**EXERCICE 2 : Titre (8 points)**",
# ou la forme combinée "**Partie A (24 pts) - Exercice 1 : Titre (8 pts)**") parfois
# rédigé par concepteur-epreuve-inedite en tête de la première question d'un exercice -
# alors que numero_exercice/points sont déjà des champs structurés sur ExerciceInedite,
# affichés indépendamment par le Badge de InediteTentativePage.tsx ET par l'en-tête
# généré par EpreuveInedite.compile_from_exercices. Non retiré, ce repère s'affiche donc
# deux fois. `\b` après PARTIE exclut "Partiel" ; les repères de sous-partie légitimes
# ("**A. Décroissance radioactive (2 points).**") ne commencent ni par "Partie" ni par
# "Exercice" et ne sont donc jamais touchés.
_REDUNDANT_EXERCICE_HEADING_RE = re.compile(r"^\*\*(PARTIE\b[^*\n]*|EXERCICE\s*\d+[^*\n]*)\*\*\s*", re.IGNORECASE)


def _strip_redundant_exercice_heading(enonce_markdown):
    text = enonce_markdown
    while True:
        match = _REDUNDANT_EXERCICE_HEADING_RE.match(text)
        if not match:
            return text
        text = text[match.end():]


def _ingest_question_inedite(exercice, data, subject):
    numero = str(data.get("numero") or "").strip()
    if not numero or not data.get("enonce_markdown") or not data.get("corrige_markdown"):
        raise IngestionError(
            f"Question incomplète dans l'exercice {exercice.numero_exercice!r} : "
            "numero/enonce_markdown/corrige_markdown requis.",
        )

    type_reponse = TypeReponse.QCM if _normalize(data.get("type_reponse")) == "qcm" else TypeReponse.OUVERTE
    if type_reponse == TypeReponse.QCM:
        choix, reponse_correcte = _normalize_qcm_choix(data.get("choix"), data.get("reponse_correcte"))
    else:
        choix, reponse_correcte = [], ""

    difficulte = DIFFICULTE_MAP.get(_normalize(data.get("difficulte_estimee")), "")
    themes = _resolve_tags(data.get("themes"))

    question = QuestionInedite.objects.create(
        exercice=exercice,
        numero=numero,
        ordre=data.get("ordre") or 1,
        # Sous-partie locale optionnelle (voir QuestionInedite.groupe_local) - jamais à
        # recopier dans enonce_intro_markdown de l'exercice parent, qui ne s'affiche
        # qu'une seule fois en tête de TOUTES ses questions.
        groupe_local=_strip_em_dash(str(data.get("groupe_local") or "")),
        enonce_markdown=_strip_redundant_exercice_heading(_strip_em_dash(data["enonce_markdown"])),
        corrige_markdown=_strip_em_dash(data["corrige_markdown"]),
        difficulte_estimee=difficulte,
        type_reponse=type_reponse,
        choix=choix,
        reponse_correcte=reponse_correcte,
    )
    if themes:
        question.themes.set(themes)
        _link_tags_to_savoir(themes, _resolve_savoir_officiel(data.get("savoir_officiel"), subject))

    # Rattaché à `exercice` (pas à `question`) : même choix de conception que
    # catalog.ingestion.ingest_exercise (voir la docstring de RappelDeMethodeInedite).
    # Contrairement à catalog.ingestion, pas de repli sur un cours_id sibling ni sur une
    # clé texte historique : ce contenu est fraîchement généré, pas issu d'un corpus PDF
    # ancien - un id explicite est toujours exigé sans filet.
    for rappel_data in data.get("rappels_de_methode") or []:
        rappel_id = rappel_data.get("id")
        if not rappel_id:
            raise IngestionError(
                f"rappels_de_methode : entrée sans 'id' pour la question {numero!r} de "
                f"l'exercice {exercice.numero_exercice!r}.",
            )
        RappelDeMethodeInedite.objects.get_or_create(
            external_id=rappel_id,
            defaults={
                "exercice": exercice,
                "competence": _strip_em_dash(rappel_data.get("competence") or ""),
                "contenu_markdown": _strip_em_dash(rappel_data.get("contenu_markdown") or ""),
            },
        )


def _ingest_exercice_inedite(epreuve, data, subject):
    numero_exercice = str(data.get("numero_exercice") or "").strip()
    if not numero_exercice:
        raise IngestionError(f"numero_exercice manquant pour un exercice de {epreuve.external_id!r}.")

    groupes = [str(g).strip() for g in data.get("groupes") or [] if str(g).strip()]

    exercice = ExerciceInedite.objects.create(
        epreuve=epreuve, numero_exercice=numero_exercice, points=str(data.get("points") or ""),
        groupes=groupes,
        # Support partagé par les questions de l'exercice (voir
        # ExerciceInedite.enonce_intro_markdown) - optionnel, vide pour la plupart des
        # matières, attendu en SVT où l'exploitation de documents est la forme normale.
        enonce_intro_markdown=_strip_em_dash(str(data.get("enonce_intro_markdown") or "")),
    )

    questions_data = data.get("questions") or []
    if not questions_data:
        raise IngestionError(f"Aucune question pour l'exercice {numero_exercice!r} de {epreuve.external_id!r}.")
    for question_data in questions_data:
        _ingest_question_inedite(exercice, question_data, subject)


def ingest_epreuve_inedite(data, country):
    """
    Ingère un objet JSON (une EpreuveInedite complète, exercices/questions inclus).
    Retourne (epreuve, created).

    Nécessite un Blueprint DÉJÀ VALIDE, résolu par blueprint_external_id - jamais créé
    ni validé ici (voir la docstring de module). Toujours créée en statut=BROUILLON :
    contrairement à quiz.ingestion.ingest_competence_item, aucun statut=VALIDE
    automatique - la publication reste un geste humain explicite (inedit.admin).

    Idempotent via external_id (voir unique_epreuveinedite_external_id_when_set).
    """
    missing = [key for key in EPREUVE_REQUIRED_KEYS if not data.get(key)]
    if missing:
        raise IngestionError(f"Champs obligatoires manquants (épreuve) : {missing}")

    external_id = str(data["external_id"]).strip()
    existing = EpreuveInedite.objects.filter(external_id=external_id).first()
    if existing:
        return existing, False

    blueprint_external_id = str(data["blueprint_external_id"]).strip()
    try:
        blueprint = Blueprint.objects.get(external_id=blueprint_external_id)
    except Blueprint.DoesNotExist:
        raise IngestionError(f"Blueprint introuvable : {blueprint_external_id!r} - doit déjà exister en base.")
    if blueprint.statut != StatutContenu.VALIDE:
        raise IngestionError(
            f"Blueprint {blueprint_external_id!r} pas encore validé (statut={blueprint.statut!r}) - "
            "une génération ne peut jamais s'appuyer sur un blueprint en brouillon.",
        )

    exercices_data = data.get("exercices") or []
    if not exercices_data:
        raise IngestionError("exercices est requis et doit contenir au moins une entrée.")

    with transaction.atomic():
        epreuve = EpreuveInedite.objects.create(
            blueprint=blueprint,
            external_id=external_id,
            subject=blueprint.subject,
            titre=_strip_em_dash(data["titre"]),
            statut=StatutContenu.BROUILLON,
        )
        epreuve.cursus.set(blueprint.cursus.all())
        for exercice_data in exercices_data:
            _ingest_exercice_inedite(epreuve, exercice_data, epreuve.subject)

        epreuve.compile_from_exercices()
        calculer_scores(epreuve)

    return epreuve, True


def ingest_cours_inedite(data):
    """
    Ingère un objet JSON produit par concepteur-epreuve-inedite (mode "Génération des
    cours en lot") - miroir de catalog.ingestion.ingest_cours. Retourne (cours, created).

    Cours (catalog.models.Cours) est entièrement origine-agnostique : le dédoublonnage
    par titre ci-dessous porte donc naturellement sur TOUT Cours déjà validé, qu'il
    vienne de correction-experte ou de ce pipeline - "on branche simplement le rappel
    au cours s'il existe déjà sinon on le crée".

    Ne s'auto-répare pas via _repair_double_json_escaping/_repair_missing_matrix_row_
    separators (contrairement à catalog.ingestion.ingest_cours) : même convention que
    ingest_blueprint/ingest_epreuve_inedite dans ce module, qui s'appuient uniquement
    sur le pré-traitement de run_ingestion pour ces deux réparations.
    """
    data, _ = _repair_dict_shaped_cours_sections(data)

    meta = data.get("meta") or {}
    source = data.get("source") or {}

    cours_id = data.get("cours_id")
    if not cours_id or not meta.get("titre") or not meta.get("matiere") or not source.get("rappel_id"):
        raise IngestionError("Champs obligatoires manquants : cours_id, meta.titre, meta.matiere, source.rappel_id")

    existing = Cours.objects.filter(external_id=cours_id).first()
    if existing:
        rappel = RappelDeMethodeInedite.objects.filter(external_id=source.get("rappel_id")).first()
        if rappel and rappel.cours_id != existing.pk:
            rappel.cours = existing
            rappel.save(update_fields=["cours"])
        return existing, False

    try:
        rappel = RappelDeMethodeInedite.objects.select_related("exercice__epreuve").get(
            external_id=source["rappel_id"],
        )
    except RappelDeMethodeInedite.DoesNotExist:
        raise IngestionError(
            f"RappelDeMethodeInedite introuvable pour source.rappel_id={source['rappel_id']!r} - "
            "l'épreuve inédite source doit être ingérée avant le cours qui en dérive.",
        )

    # Dédoublonnage par titre - identique à catalog.ingestion.ingest_cours, porte sur
    # TOUT Cours (jamais restreint à l'origine inédite) : c'est le mécanisme demandé.
    titre = _strip_em_dash(meta["titre"])
    duplicate = Cours.objects.filter(titre__iexact=titre, statut=StatutContenu.VALIDE).first()
    if duplicate:
        rappel.cours = duplicate
        rappel.save(update_fields=["cours"])
        return duplicate, False

    # EpreuveInedite.cursus est un M2M (comme Lesson.cursus) - .first() car tous les
    # cursus d'une même épreuve partagent le même pays (voir _resolve_cursus_from_entries,
    # appelé avec un seul `country` par fichier ingéré).
    country = rappel.exercice.epreuve.cursus.first().country
    _validate_pays_matches_country(meta.get("pays"), country)
    subject = _resolve_subject(meta["matiere"], country)

    with transaction.atomic():
        cours = Cours.objects.create(
            external_id=cours_id, titre=titre, subject=subject,
            sous_theme=_strip_em_dash(meta.get("sous_theme") or ""),
            duree_estimee_min=meta.get("duree_estimee_min") or None,
            sections_raw=_strip_em_dash(data.get("sections") or []),
            statut=StatutContenu.VALIDE,
        )
        if meta.get("serie"):
            cours.cursus.set(rappel.exercice.epreuve.cursus.all())
        tags = _get_or_create_tags(meta.get("tags"))
        cours.tags.set(tags)
        _link_tags_to_savoir(tags, _resolve_savoir_officiel(meta.get("savoir_officiel"), subject))
        cours.compile_from_sections()
        rappel.cours = cours
        rappel.save(update_fields=["cours"])

    return cours, True


def run_ingestion(path):
    """
    Ingère tous les fichiers .json sous `path` (fichier unique, ou dossier - recherche
    récursive) : chaque fichier porte un objet JSON UNIQUE (Blueprint, EpreuveInedite
    OU cours, jamais un tableau - contrairement à quiz.ingestion), discriminé par son
    champ `type` ("blueprint"/"epreuve"/"cours").

    Le pays se déduit du chemin sur disque, convention `ingest/_inedit/<code_pays>/...`
    (voir la docstring de module). Idempotent (voir ingest_blueprint/
    ingest_epreuve_inedite/ingest_cours_inedite) - relancer sur le même dossier sans le
    vider entre-temps est sans risque pour ce qui est déjà ingéré avec external_id.

    Retourne {"files_found", "blueprints_created", "epreuves_created", "cours_created", "skipped", "errors"}.
    """
    path = Path(path)
    files = (
        [path] if path.is_file()
        else sorted(f for f in path.rglob("*.json") if f.parent.name.lower() != "_inedit")
    )

    blueprints_created = 0
    epreuves_created = 0
    cours_created = 0
    skipped = 0
    errors = []

    for file_path in files:
        try:
            country = _resolve_country(_country_code_from_inedit_ingest_path(file_path))
        except IngestionError as exc:
            errors.append(f"{file_path}: {exc}")
            continue

        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(f"{file_path}: JSON invalide ({exc})")
            continue

        try:
            data, _ = _repair_double_json_escaping(data)
            data, _ = _repair_missing_matrix_row_separators(data)

            type_ = _normalize(data.get("type"))
            if type_ == "blueprint":
                _, created = ingest_blueprint(data, country)
            elif type_ == "epreuve":
                _, created = ingest_epreuve_inedite(data, country)
            elif type_ == "cours":
                _, created = ingest_cours_inedite(data)
            else:
                raise IngestionError(
                    f"Champ 'type' manquant ou invalide (attendu 'blueprint'/'epreuve'/'cours') : {data.get('type')!r}",
                )

            if type_ == "blueprint":
                blueprints_created += 1 if created else 0
            elif type_ == "epreuve":
                epreuves_created += 1 if created else 0
            else:
                cours_created += 1 if created else 0
            skipped += 0 if created else 1
        except Exception as exc:
            errors.append(f"{file_path}: {exc}")

    return {
        "files_found": len(files), "blueprints_created": blueprints_created,
        "epreuves_created": epreuves_created, "cours_created": cours_created,
        "skipped": skipped, "errors": errors,
    }
