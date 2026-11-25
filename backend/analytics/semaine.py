"""
Le point de la semaine pour l'équipe : l'entonnoir, la rétention, la réponse à la question posée après une séance et les
questions signalées, sur une seule page de l'administration (audit du 2026-11-25 : l'entonnoir n'avait pas d'écran, la
rétention ne sortait que par une commande, et la liste des signalements ne montrait ni l'énoncé ni la matière).

Rien n'est recalculé : la page assemble analytics.funnel, analytics.retention et les tables existantes.
"""

from collections import Counter
from datetime import timedelta

from django.utils import timezone

from quiz.models import SeanceJournaliere, SignalementQuestion, StatutSeance, StatutSignalement

from .funnel import entonnoir
from .models import AnalyticsEvent, EventName
from .retention import retention

# La question est posée à partir de la troisième séance terminée : avant, l'élève ne peut pas encore juger.
SEANCES_AVANT_AVIS = 3
AVIS = {"oui": "Oui", "un_peu": "Un peu", "non": "Non"}
MOTIFS = {
    "trop_facile": "Trop facile",
    "trop_difficile": "Trop difficile",
    "pas_mon_programme": "Pas ce que je vois en classe",
    "trop_long": "Trop long",
    "autre": "Autre chose",
}
SIGNALEMENTS_MONTRES = 30


def demander_avis_seance(user, profil):
    """Faut-il poser « Cette séance t'a aidé ? » à cet élève ? Une seule fois, à partir de sa troisième séance terminée."""
    if AnalyticsEvent.objects.filter(user=user, name=EventName.SEANCE_AVIS).exists():
        return False
    terminees = SeanceJournaliere.objects.filter(profil=profil, statut=StatutSeance.TERMINEE)
    return terminees.count() >= SEANCES_AVANT_AVIS


def avis_des_seances(depuis):
    proprietes = list(
        AnalyticsEvent.objects.filter(name=EventName.SEANCE_AVIS, created_at__gte=depuis).values_list("properties", flat=True)
    )
    avis = Counter(p.get("avis") for p in proprietes if p.get("avis") in AVIS)
    motifs = Counter(p.get("motif") for p in proprietes if p.get("motif") in MOTIFS)
    total = sum(avis.values())
    return {
        "total": total,
        "part_oui": round(100 * avis["oui"] / total) if total else None,
        "reponses": [{"libelle": libelle, "nombre": avis[cle]} for cle, libelle in AVIS.items()],
        "motifs": [{"libelle": MOTIFS[cle], "nombre": nombre} for cle, nombre in motifs.most_common()],
    }


def signalements_a_traiter():
    qs = (
        SignalementQuestion.objects.filter(statut=StatutSignalement.NOUVEAU)
        .select_related("competence_item__subject", "competence_item__theme").order_by("-cree_le")
    )
    lignes = []
    for signalement in qs[:SIGNALEMENTS_MONTRES]:
        item = signalement.competence_item
        lignes.append({
            "id": signalement.pk,
            "date": signalement.cree_le,
            "motif": signalement.get_motif_display(),
            "commentaire": signalement.commentaire,
            "item_id": signalement.competence_item_id_garde,
            "matiere": item.subject.label if item else "contenu supprimé",
            "theme": item.theme.name if item else "",
            "enonce": item.enonce_markdown if item else "",
        })
    return {"total": qs.count(), "lignes": lignes}


def point_de_la_semaine(maintenant=None):
    maintenant = maintenant or timezone.now()
    semaine = maintenant - timedelta(days=7)
    return {
        "genere_le": maintenant,
        "entonnoir_7": entonnoir(7, maintenant=maintenant),
        "entonnoir_30": entonnoir(30, maintenant=maintenant),
        "retention": retention(30, maintenant=maintenant),
        "avis_7": avis_des_seances(semaine),
        "avis_30": avis_des_seances(maintenant - timedelta(days=30)),
        "signalements": signalements_a_traiter(),
        "fiches": {
            "lectures": AnalyticsEvent.objects.filter(name=EventName.FICHE_LUE, created_at__gte=semaine).count(),
            "gardees": AnalyticsEvent.objects.filter(name=EventName.FICHE_GARDEE, created_at__gte=semaine).count(),
        },
    }
