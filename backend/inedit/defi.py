"""
Le défi de la semaine (audit produit 2026-11-13, R17) : une mini-inédite, la même pour tous les élèves d'un cursus, du lundi
au dimanche. Trois règles :

- le choix est FIGÉ en base à la première demande de la semaine (DefiSemaine) : il ne bouge pas quand une mini s'ajoute, et
  les défis passés, donc les badges, se retrouvent toujours ;
- on ne repropose une mini qu'après avoir fait le tour des autres du cursus (la moins récemment proposée d'abord) ;
- la comparaison est la bande anonyme du classement hebdomadaire (voir quiz.classement) : jamais un rang ni une note
  d'autrui, seulement « le quart supérieur » ou « la moitié supérieure », au-delà de SEUIL_COHORTE participants, et publiée
  à partir du dimanche. L'élève qui a fait le défi hors chrono est compté comme participant au badge, pas au classement :
  sa note, corrigé ouvert, ne se compare pas à celle d'une copie chronométrée.
"""
from datetime import datetime, time, timedelta

from django.db import IntegrityError, transaction
from django.db.models import Max
from django.utils import timezone

from catalog.models import StatutContenu
from quiz import classement

from .models import DefiSemaine, EpreuveInedite, TentativeInedite


def lundi_de(jour):
    return jour - timedelta(days=jour.weekday())


def _choisir(cursus, debut):
    """La mini la moins récemment proposée à ce cursus (jamais proposée d'abord), à égalité la plus ancienne par id."""
    minis = list(
        EpreuveInedite.objects.filter(est_mini=True, statut=StatutContenu.VALIDE, cursus=cursus).order_by("id"),
    )
    if not minis:
        return None
    derniere = {
        d.epreuve_id: d.debut
        for d in DefiSemaine.objects.filter(cursus=cursus, epreuve__in=minis).order_by("debut")
    }
    return min(minis, key=lambda e: (derniere.get(e.pk) is not None, derniere.get(e.pk) or debut, e.pk))


def defi_de_la_semaine(cursus, aujourdhui=None):
    """Le DefiSemaine de la semaine en cours pour ce cursus, créé au besoin ; None sans mini publiée."""
    aujourdhui = aujourdhui or timezone.localdate()
    debut = lundi_de(aujourdhui)
    existant = DefiSemaine.objects.select_related("epreuve").filter(cursus=cursus, debut=debut).first()
    if existant is not None:
        return existant
    choisie = _choisir(cursus, debut)
    if choisie is None:
        return None
    try:
        with transaction.atomic():
            return DefiSemaine.objects.create(cursus=cursus, debut=debut, epreuve=choisie)
    except IntegrityError:  # deux premières demandes en même temps : la première a gagné
        return DefiSemaine.objects.select_related("epreuve").get(cursus=cursus, debut=debut)


def _rendues_dans_la_semaine(defi):
    """Les copies rendues pendant la semaine du défi (du lundi 00 h au dimanche minuit, heure locale)."""
    debut = timezone.make_aware(datetime.combine(defi.debut, time.min))
    return TentativeInedite.objects.filter(
        epreuve_id=defi.epreuve_id, submitted_at__gte=debut, submitted_at__lt=debut + timedelta(days=7),
    )


def a_releve(profil, defi):
    return _rendues_dans_la_semaine(defi).filter(profil=profil).exists()


def bande(profil, defi):
    """{disponible, bande} parmi les participants chronométrés du défi ; même forme que quiz.classement.classement_hebdo."""
    meilleures = dict(
        _rendues_dans_la_semaine(defi)
        .filter(exam_mode_started_at__isnull=False, note_obtenue__isnull=False, profil__compte__is_staff=False)
        .values("profil_id").annotate(m=Max("note_obtenue")).values_list("profil_id", "m"),
    )
    if len(meilleures) < classement.SEUIL_COHORTE:
        return {"disponible": False, "bande": None}
    moi = meilleures.get(profil.pk)
    if moi is None:
        return {"disponible": True, "bande": None}
    part = sum(1 for m in meilleures.values() if m < moi) / len(meilleures)
    return {
        "disponible": True,
        "bande": classement.BANDE_QUART if part >= 0.75 else classement.BANDE_MOITIE if part >= 0.5 else None,
    }


def _fiche(defi):
    e = defi.epreuve
    return {
        "epreuve_id": e.pk, "slug": e.slug, "titre": e.titre, "duree_minutes": e.blueprint.duree_minutes,
        "debut": defi.debut.isoformat(), "fin": (defi.debut + timedelta(days=6)).isoformat(),
    }


def etat_du_defi(profil, cursus, aujourdhui=None):
    """
    Ce que l'accueil affiche : le défi en cours (titre, durée, jours restants), si l'élève l'a relevé, et - à partir du
    dimanche - sa bande. `precedent` : le défi de la semaine dernière, seulement si l'élève y a pris part.
    """
    aujourdhui = aujourdhui or timezone.localdate()
    defi = defi_de_la_semaine(cursus, aujourdhui)
    if defi is None:
        return None
    fiche = _fiche(defi)
    fiche["jours_restants"] = (defi.debut + timedelta(days=6) - aujourdhui).days
    fiche["releve"] = a_releve(profil, defi)
    fiche["resultat_ouvert"] = aujourdhui >= defi.debut + timedelta(days=6)
    fiche["bande"] = bande(profil, defi) if fiche["releve"] and fiche["resultat_ouvert"] else None
    precedent = DefiSemaine.objects.select_related("epreuve").filter(
        cursus=cursus, debut=defi.debut - timedelta(days=7),
    ).first()
    fiche["precedent"] = None
    if precedent is not None and a_releve(profil, precedent):
        fiche["precedent"] = {"titre": precedent.epreuve.titre, "bande": bande(profil, precedent)}
    return fiche


def defis_releves(profil):
    """Le nombre de défis (semaines) relevés par ce profil : l'unique fait derrière les badges « Défi relevé »."""
    par_epreuve = {}
    for d in DefiSemaine.objects.filter(epreuve__tentatives__profil=profil).distinct():
        par_epreuve.setdefault(d.epreuve_id, []).append(d)
    if not par_epreuve:
        return 0
    relevés = set()
    for t in TentativeInedite.objects.filter(
        profil=profil, epreuve_id__in=par_epreuve, submitted_at__isnull=False,
    ).only("epreuve_id", "submitted_at"):
        jour = timezone.localtime(t.submitted_at).date()
        for d in par_epreuve[t.epreuve_id]:
            if d.debut <= jour <= d.debut + timedelta(days=6):
                relevés.add(d.pk)
    return len(relevés)
