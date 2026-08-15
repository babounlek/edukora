"""
Contrôle qualité déterministe d'une EpreuveInedite fraîchement générée - aucun appel
LLM ici (voir l'audit "Épreuves Inédites" : aucune intégration LLM backend n'existe dans
ce dépôt, solution volontairement simple pour le MVP). Les deux scores sont purement
informatifs : ils ne bloquent rien mécaniquement, la publication reste un geste humain
explicite (inedit.admin, action "Marquer Validé") - une EpreuveInedite naît toujours en
statut=BROUILLON quel que soit le score (voir inedit.ingestion.ingest_epreuve_inedite).
"""

import difflib

from catalog.models import Question, StatutContenu, Tag

_CORPUS_SAMPLE_SIZE = 500


def _corpus_enonces(subject, cursus_qs):
    """
    Corpus de comparaison pour l'originalité : énoncés déjà publiés (Question VALIDE
    sur un Exercise/Lesson VALIDE) du même (matière, cursus) - le risque de similitude
    le plus probable est avec du contenu déjà présent pour ce sujet/niveau précis, pas
    le corpus entier tous pays/matières confondus. `cursus_qs` : tous les cursus de
    l'épreuve source (voir EpreuveInedite.cursus, M2M) - une épreuve commune à plusieurs
    séries (ex. Maths BAC C/E) se compare au corpus de CHAQUE série visée. Échantillon
    plafonné (les plus récents d'abord) plutôt que le corpus complet : borne le coût
    O(n×m) de score_originalite sans dépendre du volume réel du corpus, qui grandit avec
    le temps.
    """
    return list(
        Question.objects.filter(
            exercise__statut=StatutContenu.VALIDE,
            exercise__lesson__statut=StatutContenu.VALIDE,
            exercise__lesson__subject=subject,
            exercise__lesson__cursus__in=cursus_qs,
        )
        .order_by("-exercise__lesson__year")
        .distinct()
        .values_list("enonce_markdown", flat=True)[:_CORPUS_SAMPLE_SIZE]
    )


def score_originalite(epreuve):
    """
    Score 0-100 (100 = aucune similitude détectée avec le corpus existant) - similarité
    textuelle (difflib.SequenceMatcher, ratio de blocs communs) entre chaque énoncé
    généré et le corpus déjà publié du même (matière, cursus). Pas une solution
    sémantique (embeddings) : aucune infra vectorielle dans ce dépôt aujourd'hui,
    solution déterministe suffisante pour le MVP - à réévaluer seulement si les faux
    négatifs (paraphrases non détectées par une comparaison purement textuelle)
    s'avèrent un problème réel en usage.

    Retourne 100 si l'épreuve n'a encore aucune question générée, ou si aucun corpus de
    comparaison n'existe pour ce (matière, cursus) - jamais None (contrairement au champ
    modèle EpreuveInedite.score_originalite, qui distingue "non évalué" de "évalué à 100").
    """
    enonces_generes = [
        question.enonce_markdown
        for exercice in epreuve.exercices.all()
        for question in exercice.questions.all()
    ]
    if not enonces_generes:
        return 100

    corpus = _corpus_enonces(epreuve.subject, epreuve.cursus.all())
    if not corpus:
        return 100

    max_similarite = 0.0
    for enonce in enonces_generes:
        for reference in corpus:
            ratio = difflib.SequenceMatcher(None, enonce, reference).ratio()
            if ratio > max_similarite:
                max_similarite = ratio
            if max_similarite >= 0.99:
                break
        if max_similarite >= 0.99:
            break

    return round((1 - max_similarite) * 100)


def score_qualite(epreuve):
    """
    Score 0-100 - part des compétences visées par le Blueprint source (voir
    Blueprint.competences) réellement couvertes par au moins une QuestionInedite
    générée (voir QuestionInedite.themes). Autres vérifications structurelles (nombre
    d'exercices, barème total) volontairement différées : ExerciceInedite.points reste
    un texte libre (même choix que catalog.Exercise.points, pas fiablement sommable) et
    Blueprint.sections_plan n'a pas encore de schéma assez stable pour un contrôle
    automatique robuste sans risquer des faux négatifs sur un format par ailleurs
    légitime - à construire une fois ce schéma éprouvé en usage réel.

    Retourne 100 si le Blueprint source ne vise explicitement aucune compétence (cas
    défensif seulement - inedit.ingestion.ingest_blueprint l'interdit déjà en pratique).
    """
    competences_visees = set(epreuve.blueprint.competences.values_list("pk", flat=True))
    if not competences_visees:
        return 100

    competences_couvertes = set(
        Tag.objects.filter(questions_inedites_as_theme__exercice__epreuve=epreuve).values_list("pk", flat=True),
    )
    ratio = len(competences_visees & competences_couvertes) / len(competences_visees)
    return round(ratio * 100)


def calculer_scores(epreuve):
    """
    Calcule et enregistre les deux scores sur `epreuve` - point d'entrée unique,
    appelé automatiquement en fin d'inedit.ingestion.ingest_epreuve_inedite (jamais un
    geste manuel séparé : les deux scores sont déterministes et gratuits, rien ne
    justifie de les différer). Retourne `epreuve` pour permettre le chaînage.
    """
    epreuve.score_originalite = score_originalite(epreuve)
    epreuve.score_qualite = score_qualite(epreuve)
    epreuve.save(update_fields=["score_originalite", "score_qualite", "updated_at"])
    return epreuve
