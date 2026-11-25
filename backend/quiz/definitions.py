"""
Les définitions écrites des mots que l'élève et le parent lisent. Une seule par mot : plusieurs écrans les calculaient
chacun à leur façon (audit du 2026-11-25, E7 et E8).

THÈME MAÎTRISÉ
    Au moins 3 réponses et 70 % de réussite : quiz.services.est_maitrise. C'est la règle de TOUS les compteurs
    (« thèmes maîtrisés », anneau de préparation, bilan). La jauge d'un thème a deux crans au-dessus de ce seuil, « Solide »
    puis « Très solide » (6 réponses et 85 %) : les deux comptent comme maîtrisés. Sauter la méthode dans une séance
    demande davantage (5 réponses, voir quiz.services._theme_deja_maitrise) : ce n'est pas un compteur.

    Comptent comme réponses : les quiz (hors rejeu et quiz chronométré) et les QCM des copies rendues en conditions réelles
    (voir quiz.copies.reponses_qcm_de_copies).

JOUR ACTIF
    L'élève a fait quelque chose qui prouve un travail ce jour-là : points gagnés, séance terminée, réponse à un quiz, ou
    copie d'examen blanc rendue avec au moins une question traitée. Une connexion ne compte pas. C'est le « jour de
    révision » du bilan de l'élève et du parent (voir jours_actifs ci-dessous).

JOUR RÉUSSI
    Une séance terminée, ou l'objectif de points du jour atteint. Fait avancer la série (quiz.serie) et fait taire le
    rappel du jour, par notification comme par e-mail (relances).
"""

from django.utils import timezone

from .models import JourXP


def jours_actifs(profil, debut, fin, *, seances=(), reponses=(), copies=()):
    """
    Les jours actifs de ce profil entre `debut` et `fin` (dates locales incluses), voir JOUR ACTIF plus haut. L'appelant
    fournit ce qu'il a déjà lu : les dates des séances terminées, les instants des réponses de quiz et des copies rendues.
    Les points gagnés sont lus ici.
    """
    jours = set(seances)
    jours.update(timezone.localtime(quand).date() for quand in reponses)
    jours.update(timezone.localtime(quand).date() for quand in copies)
    jours.update(
        JourXP.objects.filter(profil=profil, xp__gt=0, jour__gte=debut, jour__lte=fin).values_list("jour", flat=True)
    )
    return {jour for jour in jours if debut <= jour <= fin}
