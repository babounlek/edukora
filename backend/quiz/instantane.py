"""
Instantané du contenu d'une QuizQuestion.

Une session de quiz pioche des CompetenceItem (ou, avant la bascule, des catalog.Question)
vivants : l'admin peut les corriger, un script de correctifs les réécrire, la purge les
supprimer. Sans copie, une ancienne tentative afficherait silencieusement un autre énoncé,
ou une autre clé, que celui sur lequel l'élève a travaillé - et sa note ne voudrait plus rien
dire. L'instantané fige à la création de la session exactement ce qu'il faut pour rejouer,
corriger et relire une question : énoncé, choix, type, clé, corrigé, thème et matière.

Le corrigé est stocké BRUT : le lien « Voir le cours complet » est recalculé à la lecture (voir
quiz.views._competence_item_corrige), c'est une information vivante et non un contenu figé.
Les figures sont référencées par l'URL déjà réécrite dans le Markdown, pas copiées.

`donnees` est la seule porte d'entrée pour lire le contenu d'une QuizQuestion : l'instantané
quand il existe, le contenu vivant sinon (lignes créées hors des services).
"""

from catalog.models import TypeReponse

VERSION = 1


def figer_item(item):
    """Instantané d'un CompetenceItem - suppose item.theme et item.subject déjà chargés."""
    return {
        "v": VERSION,
        "source": "competence_item",
        "item_id": item.pk,
        "external_id": item.external_id,
        "enonce_markdown": item.enonce_markdown,
        "corrige_markdown": item.corrige_markdown,
        "type_reponse": item.type_reponse,
        "choix": item.choix,
        "reponse_correcte": item.reponse_correcte,
        "theme": {"id": item.theme_id, "name": item.theme.name},
        "subject": {"id": item.subject_id, "code": item.subject.code, "label": item.subject.label},
    }


def figer_question(question):
    """Instantané d'une catalog.Question (historique pré-bascule uniquement)."""
    exercise = question.exercise
    lesson = exercise.lesson
    return {
        "v": VERSION,
        "source": "question",
        "question_id": question.pk,
        "numero": question.numero,
        "enonce_intro_markdown": exercise.enonce_intro_markdown,
        "enonce_markdown": question.enonce_markdown,
        "corrige_markdown": question.corrige_markdown,
        "type_reponse": question.type_reponse,
        "choix": question.choix,
        "reponse_correcte": question.reponse_correcte,
        "lesson_id": lesson.pk,
        "lesson_title": lesson.title,
        "subject": {"label": lesson.subject.label},
        "themes": [theme.name for theme in question.themes.all()],
    }


def figer(quiz_question):
    """Instantané du contenu vivant d'une QuizQuestion, ou None s'il n'y en a plus."""
    if quiz_question.competence_item_id:
        return figer_item(quiz_question.competence_item)
    if quiz_question.question_id:
        return figer_question(quiz_question.question)
    return None


def donnees(quiz_question):
    """Contenu de la question : l'instantané s'il existe, sinon le contenu vivant figé à la volée."""
    return quiz_question.snapshot or figer(quiz_question)


def type_et_cle(quiz_question):
    """(type_reponse, reponse_correcte) - le strict nécessaire pour juger une réponse, sans
    charger thème ni matière quand il faut retomber sur le contenu vivant."""
    if quiz_question.snapshot:
        return quiz_question.snapshot["type_reponse"], quiz_question.snapshot["reponse_correcte"]
    contenu = quiz_question.contenu
    return contenu.type_reponse, contenu.reponse_correcte


def est_qcm(quiz_question):
    return type_et_cle(quiz_question)[0] == TypeReponse.QCM


def cle_a_change(quiz_question):
    """Vrai si la clé actuelle du contenu vivant diffère de celle sur laquelle la question a
    été jugée - pour afficher « corrigé depuis », jamais pour recalculer une note."""
    if not quiz_question.snapshot:
        return False
    vivant = quiz_question.contenu
    if vivant is None:
        return False
    return vivant.reponse_correcte != quiz_question.snapshot["reponse_correcte"]
