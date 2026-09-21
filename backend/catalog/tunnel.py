"""
Tunnel de validation post-ingestion : logique pure partagée par les commandes
`dump_rendering_corpus` (--since) et `valider_ingestion`.

Périmètre = contenu créé/modifié depuis un instant donné (`--since`), pas le corpus
entier : un round d'ingestion doit pouvoir être validé en quelques secondes, l'audit
corpus-entier (skill audit-qualite-rendu) reste la vérification périodique.

Gravités : BLOQUANT (exit != 0), ALERTE (à arbitrer, bloque seulement avec --strict),
INFO (rapport de couverture). Le rendu KaTeX réel tourne côté frontend (vitest), voir
scripts/tunnel_validation.sh.
"""

import re
import time
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

from django.utils import timezone

from catalog.models import Cours, Exercise, Lesson, Question, StatutContenu, Tag, TypeReponse
from inedit.models import EpreuveInedite, QuestionInedite
from quiz.models import CompetenceItem

BLOQUANT, ALERTE, INFO = "BLOQUANT", "ALERTE", "INFO"

_TITRE_RAPPEL = re.compile(r"###\s*Rappel de m[eé]thode", re.IGNORECASE)

# Réponse déguisée en Rappel (physique-probatoire-d-et-ti-2019, 2026-09-21) : question de cours
# (Définir / Qu'appelle-t-on / Donner le principe...) dont le premier paragraphe du Rappel n'est pas
# une formule de méthode ("Pour...", "Lorsque...") mais une phrase déclarative qui répond à la question.
_RAPPEL_PREMIER_PARAGRAPHE = re.compile(r"\A\s*###\s*Rappel de m[eé]thode[^\n]*\n+(.*?)(?=\n{2,}|\Z)", re.IGNORECASE | re.DOTALL)
_ENONCE_DE_COURS = re.compile(
    r"(?m)^[\W\d]*(?:\*\*[^*]*\*\*)?\W*(d[ée]finir|qu['’]appelle|[ée]noncer|rappeler|citer"
    r"|donner\s+(?:la|le|les|l['’])\s*(?:d[ée]finition|principe|[ée]nonc[ée]|r[ôo]le|loi)|indiquer\s+le\s+r[ôo]le)",
    re.IGNORECASE,
)
_RAPPEL_FORMULE_DE_METHODE = re.compile(
    r"\s*(pour|lorsqu|quand|si |afin|d[eè]s |on |avant|face|il faut|une (?:d[ée]finition|question)|d[ée]finir|citer|[ée]noncer)",
    re.IGNORECASE,
)


def rappel_est_reponse_deguisee(enonce, corrige):
    """Vrai si la question demande du cours et que le Rappel qui ouvre le corrigé y répond au lieu d'expliquer COMMENT répondre."""
    match = _RAPPEL_PREMIER_PARAGRAPHE.match(corrige or "")
    if not match or not _ENONCE_DE_COURS.search(enonce or ""):
        return False
    return not _RAPPEL_FORMULE_DE_METHODE.match(match.group(1))

_RELATIF = re.compile(r"^(\d+)\s*([mhd])$")


def parse_since(value):
    """'90m', '2h', '1d' (relatif à maintenant) ou un datetime ISO 8601."""
    value = (value or "").strip()
    match = _RELATIF.match(value)
    if match:
        n, unite = int(match.group(1)), match.group(2)
        delta = {"m": timedelta(minutes=n), "h": timedelta(hours=n), "d": timedelta(days=n)}[unite]
        return timezone.now() - delta
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"--since invalide ({value!r}) : attendu 90m, 2h, 1d ou un datetime ISO 8601.") from exc
    return timezone.make_aware(parsed) if timezone.is_naive(parsed) else parsed


def _scoped(queryset, since, field="updated_at"):
    return queryset if since is None else queryset.filter(**{f"{field}__gte": since})


def _record(model, pk, ref, field, pipeline, markdown):
    return {"model": model, "pk": pk, "ref": ref, "field": field, "pipeline": pipeline, "markdown": markdown or ""}


def _choix_records(model, pk, ref, choix):
    """Fragment court rendu inline (pipeline 'bare') - un enregistrement par texte de choix QCM."""
    records = []
    for entry in choix or []:
        if isinstance(entry, dict) and entry.get("texte"):
            records.append(_record(model, pk, f"{ref} choix {entry.get('lettre', '?')}", "choix.texte", "bare", entry["texte"]))
    return records


def collect_rendering_records(since=None):
    """Un enregistrement par champ markdown rendu côté élève ; `since=None` = corpus entier."""
    records = []

    for lesson in _scoped(Lesson.objects.all(), since):
        records.append(_record("Lesson", lesson.pk, lesson.slug, "content_markdown", "full", lesson.content_markdown))

    for cours in _scoped(Cours.objects.all(), since):
        records.append(_record("Cours", cours.pk, cours.slug, "content_markdown", "full", cours.content_markdown))

    for exercise in _scoped(Exercise.objects.select_related("lesson"), since):
        ref = f"{exercise.lesson.slug}#{exercise.numero_exercice}"
        records.append(_record("Exercise", exercise.pk, ref, "enonce_markdown", "full", exercise.enonce_markdown))
        records.append(_record("Exercise", exercise.pk, ref, "corrige_markdown", "full", exercise.corrige_markdown))

    for question in _scoped(Question.objects.select_related("exercise__lesson"), since):
        ref = f"{question.exercise.lesson.slug}#{question.exercise.numero_exercice}.{question.numero}"
        records.append(_record("Question", question.pk, ref, "enonce_markdown", "full", question.enonce_markdown))
        records.append(_record("Question", question.pk, ref, "corrige_markdown", "full", question.corrige_markdown))
        records.extend(_choix_records("Question", question.pk, ref, question.choix))

    for item in _scoped(CompetenceItem.objects.select_related("theme"), since):
        ref = f"competence:{item.theme.name}#{item.pk}"
        records.append(_record("CompetenceItem", item.pk, ref, "enonce_markdown", "full", item.enonce_markdown))
        records.append(_record("CompetenceItem", item.pk, ref, "corrige_markdown", "full", item.corrige_markdown))
        records.extend(_choix_records("CompetenceItem", item.pk, ref, item.choix))

    for epreuve in _scoped(EpreuveInedite.objects.all(), since):
        records.append(_record("EpreuveInedite", epreuve.pk, epreuve.slug, "enonce_markdown", "full", epreuve.enonce_markdown))
        records.append(_record("EpreuveInedite", epreuve.pk, epreuve.slug, "corrige_markdown", "full", epreuve.corrige_markdown))

    for question in _scoped(
        QuestionInedite.objects.select_related("exercice__epreuve"), since, "exercice__epreuve__updated_at",
    ):
        ref = f"{question.exercice.epreuve.slug}#{question.exercice.numero_exercice}.{question.numero}"
        records.append(_record("QuestionInedite", question.pk, ref, "enonce_markdown", "full", question.enonce_markdown))
        records.append(_record("QuestionInedite", question.pk, ref, "corrige_markdown", "full", question.corrige_markdown))
        records.extend(_choix_records("QuestionInedite", question.pk, ref, question.choix))

    return records


@dataclass
class Finding:
    gate: str
    severity: str
    message: str


def tag_key(name):
    """Clé de rapprochement : sans accent, casse, tirets ni pluriel simple."""
    # Seuls les signes diacritiques sont retirés : un caractère non latin (API "/aɪ/" ≠ "/aʊ/")
    # doit rester distinct, un encodage en ASCII les aurait tous effacés.
    decomposed = unicodedata.normalize("NFKD", name)
    folded = "".join(c for c in decomposed if not unicodedata.combining(c)).lower()
    # Seuls espaces, tirets et apostrophes sont neutralisés : "$_GET"/"gets()" (code) ne
    # doivent jamais se confondre avec le mot "get".
    words = re.sub(r"[\s'\-]+", " ", folded).split()
    return " ".join(w[:-1] if len(w) > 3 and w[-1] in "sx" and w[-2].isalpha() else w for w in words)


_VARIANT_INDEX = {"built_at": None, "by_key": {}}
_AMBIGU = object()


def _rebuild_variant_index():
    by_key = {}
    for tag_id, name in Tag.objects.values_list("id", "name"):
        key = tag_key(name)
        by_key[key] = _AMBIGU if key in by_key else tag_id
    _VARIANT_INDEX["by_key"] = by_key
    _VARIANT_INDEX["built_at"] = time.monotonic()


def find_tag_variant(name, ttl_seconds=60):
    """
    Tag existant équivalent à `name` aux accents, casse, tirets et pluriel simple près (clé
    `tag_key`), ou None. Utilisé à l'ingestion pour ne plus recréer "elimination" quand
    "élimination" existe. Ambigu (plusieurs Tag pour la même clé, ex. un conflit de
    savoir_officiel laissé volontairement) : None, on ne devine pas. L'index est mis en
    cache `ttl_seconds` puis reconstruit ; une entrée dont le Tag a disparu depuis
    (fusion) le fait reconstruire aussitôt.
    """
    built_at = _VARIANT_INDEX["built_at"]
    if built_at is None or time.monotonic() - built_at > ttl_seconds:
        _rebuild_variant_index()
    key = tag_key(name)
    for attempt in range(2):
        tag_id = _VARIANT_INDEX["by_key"].get(key)
        if tag_id is None or tag_id is _AMBIGU:
            return None
        tag = Tag.objects.filter(pk=tag_id).first()
        if tag is not None:
            return tag
        _rebuild_variant_index()
    return None


def _scope_counts(since):
    return {
        "Lesson": _scoped(Lesson.objects.all(), since).count(),
        "Exercise": _scoped(Exercise.objects.all(), since).count(),
        "Question": _scoped(Question.objects.all(), since).count(),
        "Cours": _scoped(Cours.objects.all(), since).count(),
        "CompetenceItem": _scoped(CompetenceItem.objects.all(), since).count(),
    }


def _scope_tag_ids(since):
    ids = set()
    ids.update(_scoped(Lesson.objects.all(), since).values_list("themes", flat=True))
    ids.update(_scoped(Exercise.objects.all(), since).values_list("themes", flat=True))
    ids.update(_scoped(Question.objects.all(), since).values_list("themes", flat=True))
    ids.update(_scoped(Cours.objects.all(), since).values_list("tags", flat=True))
    ids.update(_scoped(CompetenceItem.objects.all(), since).values_list("theme_id", flat=True))
    ids.discard(None)
    return ids


def gate_structure(since):
    """Cohérence interne de ce qui vient d'être ingéré (bloquant : contenu inutilisable tel quel)."""
    findings = []

    sans_theme = _scoped(Question.objects.filter(themes__isnull=True), since).select_related("exercise__lesson")
    total = sans_theme.count()
    if total:
        exemples = ", ".join(f"{q.exercise.lesson.slug}#{q.exercise.numero_exercice}.{q.numero}" for q in sans_theme[:5])
        findings.append(Finding(
            "structure", BLOQUANT,
            f"{total} Question sans aucun thème (invisibles du Parcours par thèmes) - ex. {exemples}",
        ))

    for ex in _scoped(Exercise.objects.filter(rappels_de_methode__isnull=False), since).distinct().select_related("lesson"):
        # Sans le titre, le rendu n'affiche jamais le rappel alors qu'il existe en base
        # (Programmation Bac TI 2022/2023, corrigé le 2026-09-19).
        nb_rappels = ex.rappels_de_methode.count()
        nb_titres = len(_TITRE_RAPPEL.findall(ex.corrige_markdown or ""))
        # Partiel = ALERTE : un titre peut légitimement couvrir plusieurs sous-questions.
        if nb_titres < nb_rappels:
            findings.append(Finding(
                "structure", BLOQUANT if nb_titres == 0 else ALERTE,
                f"{ex.lesson.slug}#{ex.numero_exercice} : {nb_rappels} rappel(s) en base mais {nb_titres} titre(s) "
                "`### Rappel de méthode` dans le corrigé (rappels jamais affichés)",
            ))
        deguises = [
            q.numero for q in ex.questions.all() if rappel_est_reponse_deguisee(q.enonce_markdown, q.corrige_markdown)
        ]
        if deguises:
            findings.append(Finding(
                "structure", ALERTE,
                f"{ex.lesson.slug}#{ex.numero_exercice} : le Rappel de la/des sous-question(s) {', '.join(deguises)} "
                "commence par une phrase déclarative, pas par une formule de méthode - probable réponse déguisée "
                "en Rappel (la réponse va en clair dans le corps du corrigé)",
            ))
        sans_cours = ex.rappels_de_methode.filter(cours__isnull=True).count()
        if sans_cours:
            findings.append(Finding(
                "structure", ALERTE,
                f"{ex.lesson.slug}#{ex.numero_exercice} : {sans_cours} rappel(s) sans cours lié "
                "(cours non ingérés ? voir les erreurs du run)",
            ))

    for label, model in (("Question", Question), ("CompetenceItem", CompetenceItem)):
        for item in _scoped(model.objects.filter(type_reponse=TypeReponse.QCM), since):
            lettres = {c.get("lettre") for c in (item.choix or []) if isinstance(c, dict)}
            if len(lettres) < 2 or item.reponse_correcte not in lettres:
                findings.append(Finding(
                    "structure", BLOQUANT,
                    f"{label}#{item.pk} QCM incohérent : reponse_correcte={item.reponse_correcte!r}, choix={sorted(map(str, lettres))}",
                ))

    brouillons = _scoped(CompetenceItem.objects.exclude(statut=StatutContenu.VALIDE), since).count()
    if brouillons:
        findings.append(Finding(
            "structure", INFO,
            f"{brouillons} CompetenceItem pas VALIDE (hors du pool de quiz tant qu'ils ne le sont pas)",
        ))
    return findings


def gate_tags(since):
    """Cohérence du vocabulaire de thèmes : quasi-doublons et thèmes partagés entre matières."""
    findings = []
    ids = _scope_tag_ids(since)
    if not ids:
        return findings

    par_cle = defaultdict(list)
    for tag_id, name in Tag.objects.values_list("id", "name"):
        par_cle[tag_key(name)].append((tag_id, name))

    vus = set()
    for name in Tag.objects.filter(id__in=ids).values_list("name", flat=True):
        groupe = par_cle[tag_key(name)]
        cle = frozenset(i for i, _ in groupe)
        if len(groupe) > 1 and cle not in vus:
            vus.add(cle)
            findings.append(Finding(
                "tags", ALERTE,
                "quasi-doublon de Tag (accents/casse/pluriel) : " + " | ".join(f"id={i} {n!r}" for i, n in groupe)
                + " - fusionner (fusionner_tags_doublons) ou confirmer qu'ils sont distincts",
            ))

    sujets = defaultdict(set)
    liens = (
        (Lesson.themes.through, "tag_id", "lesson__subject_id"),
        (Exercise.themes.through, "tag_id", "exercise__lesson__subject_id"),
        (Question.themes.through, "tag_id", "question__exercise__lesson__subject_id"),
        (Cours.tags.through, "tag_id", "cours__subject_id"),
    )
    for through, tag_field, subject_field in liens:
        for tag_id, subject_id in through.objects.filter(**{f"{tag_field}__in": ids}).values_list(tag_field, subject_field):
            sujets[tag_id].add(subject_id)
    for tag_id, subject_id in CompetenceItem.objects.filter(theme_id__in=ids).values_list("theme_id", "subject_id"):
        sujets[tag_id].add(subject_id)

    partages = [tag_id for tag_id in ids if len(sujets[tag_id]) > 1]
    if partages:
        noms = ", ".join(repr(n) for n in Tag.objects.filter(id__in=partages).order_by("name").values_list("name", flat=True)[:10])
        findings.append(Finding(
            "tags", ALERTE,
            f"{len(partages)} thème(s) partagé(s) entre plusieurs matières (risque de collision de sens) - ex. {noms}",
        ))
    return findings


def gate_couverture(since):
    """Delta de couverture des thèmes touchés : quiz VALIDE et cours disponibles (rapport, jamais bloquant)."""
    ids = _scope_tag_ids(since)
    if not ids:
        return []

    avec_quiz = set(
        CompetenceItem.objects.filter(theme_id__in=ids, statut=StatutContenu.VALIDE).values_list("theme_id", flat=True),
    )
    avec_cours = set(Cours.objects.filter(tags__in=ids, statut=StatutContenu.VALIDE).values_list("tags", flat=True))
    noms = dict(Tag.objects.filter(id__in=ids).values_list("id", "name"))

    findings = [Finding("couverture", INFO, f"{len(ids)} thème(s) touché(s) par ce round")]
    for label, manquants in (("sans quiz VALIDE", ids - avec_quiz), ("sans cours VALIDE", ids - avec_cours)):
        if manquants:
            exemples = ", ".join(repr(noms[i]) for i in sorted(manquants, key=lambda i: noms[i])[:10])
            findings.append(Finding("couverture", INFO, f"{len(manquants)} thème(s) {label} - ex. {exemples}"))
    return findings


def run_db_gates(since):
    return [*gate_structure(since), *gate_tags(since), *gate_couverture(since)], _scope_counts(since)
