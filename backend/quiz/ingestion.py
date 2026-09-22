"""
Traduit la sortie JSON du skill concepteur-quiz-competence (items de quiz écrits pour
être autonomes, jamais un extrait d'épreuve) vers quiz.CompetenceItem.

Réutilise volontairement les résolveurs de catalog.ingestion (IngestionError,
_resolve_subject, _resolve_cursus_list, _resolve_country, _normalize_qcm_choix,
DIFFICULTE_MAP...) plutôt que de les dupliquer : un CompetenceItem et une
catalog.Question partagent le même référentiel pays/matière/cursus/difficulté - toute
évolution de ce référentiel doit se répercuter aux deux pipelines d'ingestion en même
temps, jamais à un seul (voir la note "consistance correction-experte" côté mémoire
projet).

Convention de dossier : `ingest/_quiz/<code_pays>/...` - un sous-dossier de l'arbre
`ingest/` déjà monté dans le conteneur (voir catalog.admin.INGEST_DIR), plutôt qu'un
arbre séparé qui aurait exigé un nouveau bind mount Docker. `_quiz` (préfixe
underscore, jamais un code pays valide) distingue ce sous-dossier des vrais dossiers
pays de correction-experte ; catalog.ingestion.run_ingestion l'ignore explicitement
(voir son garde-fou dédié) pour ne jamais tenter d'y lire un exercice ou un cours.
"""

import json
from pathlib import Path

from django.db import transaction
from django.db.models import Count

from catalog.ingestion import (
    DIFFICULTE_MAP,
    IngestionError,
    _est_tag_structurel,
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
)
from catalog.models import Exercise, Question, StatutContenu, Subject, Tag, TypeReponse
from programme.models import Savoir

from .models import CompetenceItem

SELECTION_FLOOR = 6
SELECTION_LIMIT = 5

# Nombre minimal de Question validées portant un couple (thème, matière) pour qu'il soit
# proposé comme compétence de quiz. Un seul exercice ne suffit pas à caractériser une
# compétence : le skill n'a alors qu'un matériel de référence, et le nom du tag ne dit
# pas ce qu'il recouvre réellement (constaté le 2026-08-17 - « loi de Hooke » proposé en
# Mathématiques sur la foi d'un unique exercice de fonction affine où un ressort servait
# de décor). C'est un arbitrage, pas une détection : il écarte aussi des compétences
# légitimes encore peu documentées, qui reviendront dès qu'un second exercice sera tagué.
# Abaissable à 1 via --min-questions pour retrouver l'ancien comportement.
SELECTION_MIN_QUESTIONS = 2

# _est_tag_structurel (filtre les tags qui nomment un FORMAT plutôt qu'une notion, ex.
# « QCM… », « situation-problème ») vit désormais dans catalog.ingestion (déplacé le
# 2026-09-07) : _link_tags_to_savoir en a besoin aussi, pas seulement la sélection de
# compétences ci-dessous - voir son import en tête de fichier.
SELECTION_REPARTITION = {"FAIBLE": 2, "MOYENNE": 3, "ELEVEE": 1}
SELECTION_MAX_REFERENCE_QUESTIONS = 4

REQUIRED_KEYS = ["theme", "matiere", "cursus", "enonce_markdown", "corrige_markdown"]


def _country_code_from_quiz_ingest_path(path):
    """
    Variante de catalog.ingestion._country_code_from_path, ancrée sur le segment
    `_quiz` plutôt que `ingest` - voir la convention de dossier en tête de module.
    """
    parts = path.resolve().parts
    lowered = [p.lower() for p in parts]
    if "_quiz" not in lowered:
        return None
    idx = lowered.index("_quiz")
    if idx + 1 >= len(parts):
        return None
    return parts[idx + 1]


def _resolve_theme(theme_name, allow_create=False):
    """
    Correspondance exacte d'abord (Tag.name est sensible à la casse en base), repli
    insensible à la casse ensuite - le skill est censé recopier le nom exact d'un Tag
    existant, mais une dérive mineure de casse est un risque réaliste à ne pas traiter
    comme une erreur bloquante quand une correspondance non ambiguë existe.

    `allow_create` : par défaut, ce pipeline n'invente jamais un Tag - il doit déjà
    exister (créé via correction-experte). Seule exception : un `theme` accompagné d'un
    `savoir_officiel` qui a résolu avec succès (voir ingest_competence_item) - la
    compétence est alors ancrée à une entrée réelle du référentiel programme, ce n'est
    plus une invention libre, juste un nom qui n'a jamais encore été utilisé côté
    catalog.Tag (cas normal pour un savoir jusqu'ici sans aucun contenu).
    """
    name = _strip_em_dash(str(theme_name or "")).strip()
    if not name:
        raise IngestionError("theme manquant.")
    try:
        return Tag.objects.get(name=name)
    except Tag.DoesNotExist:
        pass
    candidats = list(Tag.objects.filter(name__iexact=name))
    if len(candidats) == 1:
        return candidats[0]
    if len(candidats) > 1:
        raise IngestionError(f"Plusieurs Tag correspondent à {name!r} à la casse près - ambigu, à corriger à la main.")
    # Variante aux accents/pluriel près d'un Tag existant : réutilisée (voir catalog.tunnel).
    from catalog.tunnel import find_tag_variant

    variante = find_tag_variant(name)
    if variante is not None:
        return variante
    if allow_create:
        tag, _ = Tag.objects.get_or_create(name=name)
        return tag
    raise IngestionError(
        f"Compétence (Tag) introuvable : {name!r} - doit déjà exister en base (créée via "
        "correction-experte), jamais inventée par ce pipeline.",
    )


def _resolve_cursus_from_entries(cursus_data, country):
    """
    `cursus_data` : liste d'objets {"examen": "bac", "serie": "C"} (serie omise/vide
    pour un examen sans série, ex. BEPC) - mêmes champs et mêmes valeurs que
    correction-experte (examen/serie), résolus par les mêmes fonctions, pour ne jamais
    diverger du référentiel pays/examen/série déjà utilisé côté catalog.
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


def _find_undercovered_competencies(country, floor, min_questions=SELECTION_MIN_QUESTIONS):
    """
    Groupe les Question validées de ce pays par (theme, matière) - une compétence est
    traitée par matière, pas seulement par nom de Tag : le même intitulé pourrait en
    théorie être réutilisé dans une autre matière, et le skill concepteur-quiz-
    competence a de toute façon besoin d'une matière unique par requête.

    Deux couples sont écartés avant tout calcul de couverture, parce qu'ils ne
    constituent pas des compétences traitables (voir SELECTION_MIN_QUESTIONS et
    catalog.ingestion._TAGS_STRUCTURELS_EXACTS pour le détail et les cas réels qui les
    ont motivés) :
    ceux dont le tag nomme la forme d'une question plutôt qu'une notion, et ceux
    adossés à moins de `min_questions` exercices.

    Aucun des deux ne prétend détecter une erreur de tagging inter-matières : rien dans
    les données ne dit que « loi de Hooke » est une loi de physique et non une
    compétence mathématique. Le filtre par volume l'écarte de fait, mais seulement
    parce que l'exercice de maths concerné était unique - jamais parce que la fuite
    aurait été comprise. Un tag de physique posé sur plusieurs exercices de maths
    passerait toujours, et resterait à repérer à la lecture du materiel_reference.

    Retourne une liste de (theme, subject, gap) triée par gap décroissant (la
    compétence la plus sous-couverte d'abord), gap = floor - couverture actuelle,
    uniquement pour gap > 0.
    """
    pairs = (
        Question.objects.filter(
            exercise__statut=StatutContenu.VALIDE,
            exercise__lesson__statut=StatutContenu.VALIDE,
            exercise__lesson__cursus__country=country,
            themes__isnull=False,
        )
        .values("themes", "exercise__lesson__subject")
        .annotate(n=Count("pk", distinct=True))
    )

    candidates = []
    for pair in pairs:
        if pair["n"] < min_questions:
            continue

        theme = Tag.objects.get(pk=pair["themes"])
        if _est_tag_structurel(theme.name):
            continue

        subject_id = pair["exercise__lesson__subject"]

        covered = CompetenceItem.objects.filter(
            theme_id=theme.pk, subject_id=subject_id, statut=StatutContenu.VALIDE,
        ).count()
        gap = floor - covered
        if gap <= 0:
            continue

        candidates.append((theme, Subject.objects.get(pk=subject_id), gap))

    candidates.sort(key=lambda c: c[2], reverse=True)
    return candidates


def _build_generation_request(country, theme, subject, gap):
    questions = list(
        Question.objects.filter(
            themes=theme,
            exercise__lesson__subject=subject,
            exercise__statut=StatutContenu.VALIDE,
            exercise__lesson__statut=StatutContenu.VALIDE,
            exercise__lesson__cursus__country=country,
        )
        .select_related("exercise__lesson")
        .order_by("exercise_id", "ordre")
    )

    materiel_reference = []
    seen_exercises = set()
    for question in questions:
        if question.exercise_id in seen_exercises:
            continue
        seen_exercises.add(question.exercise_id)
        materiel_reference.append({
            "exercise_id": question.exercise_id,
            "enonce_markdown": question.enonce_markdown,
            "corrige_markdown": question.corrige_markdown,
        })
        if len(materiel_reference) >= SELECTION_MAX_REFERENCE_QUESTIONS:
            break

    # Union des cursus de TOUTES les Question de cette compétence/matière, pas
    # seulement la première - une compétence couvre souvent plusieurs séries à la fois
    # (ex. Maths BAC C et E) : voir catalog.models.Lesson.cursus (M2M).
    cursus_entries = []
    seen_cursus = set()
    for question in questions:
        for cursus in question.exercise.lesson.cursus.filter(country=country):
            if cursus.pk in seen_cursus:
                continue
            seen_cursus.add(cursus.pk)
            cursus_entries.append({
                "examen": cursus.examen.lower(),
                "serie": cursus.series.code if cursus.series else "",
            })

    nombre_items = min(gap, sum(SELECTION_REPARTITION.values()))

    # Si ce thème est déjà rattaché à un savoir officiel (curation antérieure, ou item
    # déjà généré via _build_generation_request_from_savoir ci-dessous), transmet la
    # référence dans la requête plutôt que de laisser le skill la redécouvrir - voir
    # ingest_competence_item, qui la revalidera de toute façon à l'ingestion.
    savoir_officiel = None
    if theme.savoir_officiel_id:
        s = theme.savoir_officiel
        savoir_officiel = {
            "classe": s.module.classe, "serie_label": s.module.serie_label,
            "module_numero": s.module.numero, "savoir_numero": s.numero,
        }

    return {
        "competence": theme.name,
        "pays": country.code.lower(),
        "matiere": subject.label,
        "cursus": cursus_entries,
        "savoir_officiel": savoir_officiel,
        "cible": {
            "nombre_items": nombre_items,
            "repartition_difficulte": SELECTION_REPARTITION,
        },
        "materiel_reference": materiel_reference,
    }


def _find_undercovered_savoirs_officiels(country, floor):
    """
    Complète _find_undercovered_competencies, qui ne peut jamais voir un savoir du
    référentiel programme officiel (voir programme.models.Savoir) tant qu'aucun Tag/
    Question n'y a encore été rattaché - elle ne fait que grouper du contenu déjà
    existant, jamais le référentiel lui-même. Un savoir fraîchement ajouté (ou jamais
    encore couvert par le moindre item de quiz) reste donc invisible pour elle, aussi
    sous-couvert soit-il en réalité.

    Part ici du référentiel (programme.Savoir), pas du contenu : rend visibles les
    trous de couverture totale, pas seulement les trous dans ce qui a déjà été entamé.
    Uniquement pour un pays qui a un référentiel programme (aujourd'hui CM+MATHS) -
    liste vide sinon, jamais d'erreur.

    Retourne une liste de (savoir, subject, gap), même tri que la fonction sœur.
    """
    savoirs = (
        Savoir.objects.filter(module__cursus__country=country)
        .select_related("module", "module__subject")
        .distinct()
    )

    candidates = []
    for savoir in savoirs:
        subject = savoir.module.subject
        covered = CompetenceItem.objects.filter(
            theme__savoir_officiel=savoir, subject=subject, statut=StatutContenu.VALIDE,
        ).count()
        gap = floor - covered
        if gap <= 0:
            continue
        candidates.append((savoir, subject, gap))

    candidates.sort(key=lambda c: c[2], reverse=True)
    return candidates


def _build_generation_request_from_savoir(country, savoir, subject, gap):
    """
    Pendant de _build_generation_request, mais pour un savoir qui n'a - par
    construction (voir _find_undercovered_savoirs_officiels) - pas forcément de Tag ni
    de Question existante à grouper. `materiel_reference` reste peuplé en best-effort
    (via tout Tag déjà rattaché à ce savoir), `competence` est dérivé du référentiel lui
    -même plutôt que d'un nom de Tag.
    """
    questions = list(
        Question.objects.rattachees_au_savoir(savoir)
        .filter(
            exercise__lesson__subject=subject,
            exercise__statut=StatutContenu.VALIDE,
            exercise__lesson__statut=StatutContenu.VALIDE,
            exercise__lesson__cursus__country=country,
        )
        .select_related("exercise__lesson")
        .order_by("exercise_id", "ordre")
    )

    materiel_reference = []
    seen_exercises = set()
    for question in questions:
        if question.exercise_id in seen_exercises:
            continue
        seen_exercises.add(question.exercise_id)
        materiel_reference.append({
            "exercise_id": question.exercise_id,
            "enonce_markdown": question.enonce_markdown,
            "corrige_markdown": question.corrige_markdown,
        })
        if len(materiel_reference) >= SELECTION_MAX_REFERENCE_QUESTIONS:
            break

    cursus_entries = [
        {"examen": c.examen.lower(), "serie": c.series.code if c.series else ""}
        for c in savoir.module.cursus.filter(country=country)
    ]

    nombre_items = min(gap, sum(SELECTION_REPARTITION.values()))

    return {
        "competence": f"{savoir.module.titre} - {savoir.intitule}",
        "pays": country.code.lower(),
        "matiere": subject.label,
        "cursus": cursus_entries,
        "savoir_officiel": {
            "classe": savoir.module.classe, "serie_label": savoir.module.serie_label,
            "module_numero": savoir.module.numero, "savoir_numero": savoir.numero,
        },
        "cible": {
            "nombre_items": nombre_items,
            "repartition_difficulte": SELECTION_REPARTITION,
        },
        "materiel_reference": materiel_reference,
    }


def select_quiz_batch(
    country, limit=SELECTION_LIMIT, floor=SELECTION_FLOOR, min_questions=SELECTION_MIN_QUESTIONS,
    subject_code=None,
):
    """
    Sélectionne jusqu'à `limit` compétences sous-couvertes pour `country` et produit
    une liste de requêtes de génération au format attendu par le skill concepteur-
    quiz-competence (voir sa section "Entrée attendue") - pure sélection déterministe,
    aucun jugement éditorial, jamais le contenu du quiz lui-même.

    Combine deux sources depuis 2026-08-12 : les compétences (Tag) déjà entamées mais
    sous la barre (_find_undercovered_competencies), et les savoirs du référentiel
    programme officiel encore invisibles à celle-ci faute de tout contenu existant
    (_find_undercovered_savoirs_officiels - voir sa docstring). Un Tag déjà rattaché à
    un des savoirs retenus est retiré du premier lot : le signal savoir (granularité
    officielle) prime, pas la peine de le redemander deux fois sous deux formes.

    Fonction partagée par la commande `select_quiz_batch` (CLI) et
    `quiz.admin.CompetenceItemAdmin.select_batch_view` (bouton admin) - un seul
    endroit à faire évoluer si le critère de sélection change.
    """
    savoir_candidates = _find_undercovered_savoirs_officiels(country, floor)
    if subject_code:
        # Ciblage d'un lot (skill tunnel-completude-edukora, étape E) : une seule matière.
        savoir_candidates = [c for c in savoir_candidates if c[1].code == subject_code]
    savoir_ids_in_play = {savoir.pk for savoir, _, _ in savoir_candidates}

    tag_candidates = [
        (theme, subject, gap)
        for theme, subject, gap in _find_undercovered_competencies(country, floor, min_questions)
        if theme.savoir_officiel_id not in savoir_ids_in_play and (not subject_code or subject.code == subject_code)
    ]

    combined = sorted(
        [("tag", c) for c in tag_candidates] + [("savoir", c) for c in savoir_candidates],
        key=lambda item: item[1][2], reverse=True,
    )[:limit]

    requests = []
    for kind, candidate in combined:
        if kind == "tag":
            theme, subject, gap = candidate
            requests.append(_build_generation_request(country, theme, subject, gap))
        else:
            savoir, subject, gap = candidate
            requests.append(_build_generation_request_from_savoir(country, savoir, subject, gap))
    return requests


def ingest_competence_item(data, country):
    """
    Ingère un objet JSON (un CompetenceItem). Retourne (item, created).

    Idempotent via `external_id` quand renseigné (voir la contrainte
    unique_competenceitem_external_id_when_set) : un item déjà ingéré n'est jamais
    modifié - un ré-import ne recouvre pas une correction manuelle faite depuis
    l'admin. Sans `external_id` (item ad hoc, hors mode automatisation), toujours créé.

    Créé directement avec statut=VALIDE (comme catalog.ingestion.ingest_exercise) :
    publié et servable en Quiz dès l'ingestion, sans étape de relecture humaine
    préalable - la rigueur exigée du skill concepteur-quiz-competence (auto-
    vérification avant de finaliser chaque item, voir son SKILL.md) est la seule
    garantie avant qu'un élève ne voie ce contenu. `quiz.admin.CompetenceItemAdmin`
    reste disponible pour repasser un item en brouillon après coup si un problème est
    repéré une fois publié.
    """
    missing = [key for key in REQUIRED_KEYS if not data.get(key)]
    if missing:
        raise IngestionError(f"Champs obligatoires manquants : {missing}")

    external_id = str(data.get("external_id") or "").strip()
    if external_id:
        existing = CompetenceItem.objects.filter(external_id=external_id).first()
        if existing:
            return existing, False

    subject = _resolve_subject(data["matiere"], country)
    savoir = _resolve_savoir_officiel(data.get("savoir_officiel"), subject)
    theme = _resolve_theme(data["theme"], allow_create=bool(savoir))
    cursus_list = _resolve_cursus_from_entries(data["cursus"], country)
    _link_tags_to_savoir([theme], savoir)

    type_reponse = TypeReponse.QCM if _normalize(data.get("type_reponse")) == "qcm" else TypeReponse.OUVERTE
    if type_reponse == TypeReponse.QCM:
        choix, reponse_correcte = _normalize_qcm_choix(data.get("choix"), data.get("reponse_correcte"))
    else:
        choix, reponse_correcte = [], ""

    difficulte = DIFFICULTE_MAP.get(_normalize(data.get("difficulte_estimee")), "")

    with transaction.atomic():
        item = CompetenceItem.objects.create(
            external_id=external_id,
            theme=theme,
            subject=subject,
            enonce_markdown=_strip_em_dash(data["enonce_markdown"]),
            corrige_markdown=_strip_em_dash(data["corrige_markdown"]),
            difficulte_estimee=difficulte,
            type_reponse=type_reponse,
            choix=choix,
            reponse_correcte=reponse_correcte,
            statut=StatutContenu.VALIDE,
        )
        item.cursus.set(cursus_list)

        # Best-effort, jamais bloquant : source_exercises n'est que de la traçabilité
        # d'audit (voir CompetenceItem.source_exercises), un id qui ne résout plus rien
        # (exercice supprimé/mal recopié par le skill) ne doit pas faire échouer
        # l'ingestion d'un item par ailleurs valide - même logique que
        # catalog.ingestion._link_rappels_lies.
        source_ids = [i for i in (data.get("source_exercises") or []) if isinstance(i, int)]
        if source_ids:
            item.source_exercises.set(Exercise.objects.filter(pk__in=source_ids))

    return item, True


def run_ingestion(path):
    """
    Ingère tous les fichiers .json sous `path` (fichier unique, ou dossier - recherche
    récursive) : chaque fichier porte un tableau JSON de CompetenceItem (sortie brute
    du skill concepteur-quiz-competence), jamais un objet unique.

    Le pays se déduit du chemin sur disque, convention `ingest/_quiz/<code_pays>/...`
    (même mécanisme que catalog.ingestion._country_code_from_path, ancré sur `_quiz`
    plutôt que sur la racine `ingest` - voir la docstring de module).

    Idempotent (voir ingest_competence_item) : relancer sur le même dossier sans le
    vider entre-temps est sans risque pour les items déjà ingérés avec external_id.

    Retourne {"files_found": int, "created": int, "skipped": int, "errors": [str, ...]}.
    """
    path = Path(path)
    # select_quiz_batch écrit sa requête de sélection directement dans `_quiz/`
    # (ex. `_quiz/_batch_cm.json`, pas encore rattachée à un pays précis puisque
    # c'est une liste de requêtes, pas un lot ingérable) - jamais un CompetenceItem
    # valide, donc exclu ici plutôt que de produire une "Pays inconnu" trompeuse à
    # chaque scan complet de l'arbre `_quiz/`. Un vrai lot vit toujours au moins un
    # niveau plus bas, sous `_quiz/<code_pays>/...`.
    files = (
        [path] if path.is_file()
        else sorted(f for f in path.rglob("*.json") if f.parent.name.lower() != "_quiz")
    )

    created = 0
    skipped = 0
    errors = []

    for file_path in files:
        try:
            country = _resolve_country(_country_code_from_quiz_ingest_path(file_path))
        except IngestionError as exc:
            errors.append(f"{file_path}: {exc}")
            continue

        try:
            raw = json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(f"{file_path}: JSON invalide ({exc})")
            continue

        items_data = raw if isinstance(raw, list) else [raw]

        for index, data in enumerate(items_data):
            try:
                data, _ = _repair_double_json_escaping(data)
                data, _ = _repair_missing_matrix_row_separators(data)
                _, was_created = ingest_competence_item(data, country)
                created += 1 if was_created else 0
                skipped += 0 if was_created else 1
            except Exception as exc:
                theme = data.get("theme", "?") if isinstance(data, dict) else "?"
                errors.append(f"{file_path} (item {index} - {theme!r}): {exc}")

    return {"files_found": len(files), "created": created, "skipped": skipped, "errors": errors}
