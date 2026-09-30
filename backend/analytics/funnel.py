"""
Entonnoir d'acquisition et de paiement, calculé à partir des tables qui existent déjà
(comptes, séances, paiements) plutôt que d'évènements à poser : il se lit donc
RÉTROACTIVEMENT, sur tout l'historique, dès le premier jour.

Le but est de répondre à une seule question : à quelle étape les élèves inscrits
s'arrêtent-ils ? Chaque étape est un sous-ensemble de la précédente lue sur la même
cohorte (comptes créés dans la fenêtre), jamais un compte d'évènements bruts - un élève
qui lance dix séances compte une fois.

Volontairement absent : les visiteurs anonymes qui ne s'inscrivent jamais. Aucun
identifiant n'est conservé pour eux (voir AnalyticsEvent) ; seuls les évènements
`tarifs_vus`/`abonnement_ouvert` en donnent une idée, en volume.
"""

from datetime import timedelta
from statistics import median

from django.db.models import Min
from django.utils import timezone

from payments.models import ManualPayment, ManualPaymentStatus, StatutTransaction, Transaction
from quiz.models import QuizSession, SeanceJournaliere, StatutSeance
from users.models import User

from .models import AnalyticsEvent, EventName

# Une transaction « en attente » depuis moins que ça est un paiement en cours de
# confirmation, pas un abandon.
DELAI_ABANDON = timedelta(hours=1)
JOURS_RETOUR = 7


def _pourcentage(partie, total):
    return round(100 * partie / total, 1) if total else None


def _etape(cle, libelle, ids, precedent, total):
    return {
        "cle": cle,
        "libelle": libelle,
        "eleves": len(ids),
        "part_des_inscrits": _pourcentage(len(ids), total),
        # Ce que l'élève a fait de l'étape d'avant : c'est CE chiffre qui désigne la fuite.
        "part_de_l_etape_precedente": _pourcentage(len(ids), len(precedent)) if precedent is not None else None,
    }


def _ids_avec_paiement_reussi():
    return set(
        Transaction.objects.filter(status=StatutTransaction.SUCCESSFUL).values_list("user_id", flat=True),
    ) | set(
        ManualPayment.objects.filter(status=ManualPaymentStatus.APPROVED).values_list("user_id", flat=True),
    )


def _ids_avec_tentative_de_paiement():
    return set(Transaction.objects.values_list("user_id", flat=True)) | set(
        ManualPayment.objects.values_list("user_id", flat=True),
    )


def _ids_revenus_apres(cohorte, jours):
    """Élèves qui ont refait une activité (séance, quiz, épreuve inédite) au moins `jours`
    jours après leur inscription - le vrai « ils sont revenus »."""
    from inedit.models import TentativeInedite

    inscription = dict(cohorte.values_list("id", "date_joined"))
    revenus = set()
    # SeanceJournaliere/QuizSession/TentativeInedite sont par profil (voir
    # users.Profil), jamais par compte - remonté ici via profil__compte_id, chaque
    # compte n'ayant à ce stade qu'un seul profil (voir users.profils.profil_actif).
    activites = (
        SeanceJournaliere.objects.filter(profil__compte_id__in=inscription, statut=StatutSeance.TERMINEE)
        .values_list("profil__compte_id", "termine_at"),
        QuizSession.objects.filter(profil__compte_id__in=inscription).values_list("profil__compte_id", "started_at"),
        TentativeInedite.objects.filter(profil__compte_id__in=inscription).values_list("profil__compte_id", "started_at"),
    )
    for lot in activites:
        for user_id, quand in lot:
            if quand and quand >= inscription[user_id] + timedelta(days=jours):
                revenus.add(user_id)
    return revenus


def entonnoir(jours=30, *, maintenant=None):
    """Entonnoir des comptes créés dans les `jours` derniers jours, plus l'état des paiements."""
    maintenant = maintenant or timezone.now()
    debut = maintenant - timedelta(days=jours)

    cohorte = User.objects.filter(date_joined__gte=debut, is_staff=False, is_superuser=False)
    inscrits = set(cohorte.values_list("id", flat=True))
    total = len(inscrits)

    a_declare = set(cohorte.filter(cursus_prepare__isnull=False).values_list("id", flat=True))
    a_lance = set(
        SeanceJournaliere.objects.filter(profil__compte_id__in=inscrits).values_list("profil__compte_id", flat=True),
    )
    a_termine = set(
        SeanceJournaliere.objects.filter(profil__compte_id__in=inscrits, statut=StatutSeance.TERMINEE)
        .values_list("profil__compte_id", flat=True),
    )
    a_essaye = inscrits & _ids_avec_tentative_de_paiement()
    a_paye = inscrits & _ids_avec_paiement_reussi()

    etapes = []
    precedent = None
    for cle, libelle, ids in (
        ("inscrits", "Comptes créés", inscrits),
        ("examen_declare", "Ont déclaré l'examen qu'ils préparent", a_declare),
        ("seance_lancee", "Ont ouvert une séance du jour", a_lance),
        ("seance_terminee", "Ont terminé une séance", a_termine),
        ("paiement_tente", "Ont tenté de payer", a_essaye),
        ("paiement_reussi", "Ont payé", a_paye),
    ):
        etapes.append(_etape(cle, libelle, ids, precedent, total))
        precedent = ids

    # Le retour à J+7 ne se juge que sur les comptes assez anciens pour l'avoir permis.
    murs = cohorte.filter(date_joined__lte=maintenant - timedelta(days=JOURS_RETOUR))
    ids_murs = set(murs.values_list("id", flat=True))
    revenus = _ids_revenus_apres(murs, JOURS_RETOUR)
    retour = {
        "eleves_assez_anciens": len(ids_murs),
        "revenus_apres_7_jours": len(revenus),
        "part": _pourcentage(len(revenus), len(ids_murs)),
        "revenus_parmi_ceux_qui_ont_termine_une_seance": _pourcentage(
            len(revenus & a_termine), len(ids_murs & a_termine),
        ),
    }

    return {
        "fenetre_jours": jours,
        "genere_le": maintenant.isoformat(),
        "etapes": etapes,
        "retour_j7": retour,
        "delai_median_jusqu_au_paiement_jours": _delai_median_jusqu_au_paiement(inscrits),
        "paiements": etat_des_paiements(debut, maintenant),
        "frequentation": _frequentation(debut),
    }


def _delai_median_jusqu_au_paiement(inscrits):
    premiers = (
        Transaction.objects.filter(user_id__in=inscrits, status=StatutTransaction.SUCCESSFUL)
        .values("user_id").annotate(premier=Min("created_at"))
    )
    inscription = dict(User.objects.filter(id__in=inscrits).values_list("id", "date_joined"))
    delais = [(p["premier"] - inscription[p["user_id"]]).total_seconds() / 86400 for p in premiers]
    return round(median(delais), 1) if delais else None


def etat_des_paiements(debut, fin):
    """Tentatives de paiement de la période et élèves qui ont décroché avant la fin."""
    transactions = Transaction.objects.filter(created_at__gte=debut, created_at__lte=fin)
    limite = fin - DELAI_ABANDON
    reussis = _ids_avec_paiement_reussi()

    par_statut = {statut: transactions.filter(status=statut).count() for statut in StatutTransaction.values}
    en_attente_depuis_longtemps = transactions.filter(status=StatutTransaction.PENDING, created_at__lt=limite)
    manuels = ManualPayment.objects.filter(created_at__gte=debut, created_at__lte=fin)

    tentes = set(transactions.values_list("user_id", flat=True)) | set(manuels.values_list("user_id", flat=True))
    abandonnes = tentes - reussis

    return {
        "transactions": sum(par_statut.values()),
        "par_statut": par_statut,
        "reussite": _pourcentage(par_statut.get(StatutTransaction.SUCCESSFUL, 0), sum(par_statut.values())),
        "en_attente_depuis_plus_d_une_heure": en_attente_depuis_longtemps.count(),
        "paiements_manuels": {
            statut: manuels.filter(status=statut).count() for statut in ManualPaymentStatus.values
        },
        "eleves_ayant_tente": len(tentes),
        "eleves_n_ayant_jamais_paye": len(abandonnes),
    }


def _frequentation(debut):
    """Volumes des évènements de page (anonymes compris) : tarifs vus, page d'abonnement ouverte."""
    evenements = AnalyticsEvent.objects.filter(created_at__gte=debut)
    return {
        nom.value: evenements.filter(name=nom).count()
        for nom in (
            EventName.TARIFS_VUS, EventName.ABONNEMENT_OUVERT, EventName.PAYMENT_INITIATED,
            EventName.PAYMENT_SUCCEEDED, EventName.PAYMENT_FAILED, EventName.PAYMENT_TIMEOUT,
        )
    }


def _lisible(valeur):
    return "-" if valeur is None else valeur


def rendre_texte(rapport):
    lignes = [f"Entonnoir des comptes créés ces {rapport['fenetre_jours']} derniers jours", ""]
    for etape in rapport["etapes"]:
        suite = etape["part_de_l_etape_precedente"]
        lignes.append(
            f"  {etape['libelle']:<45} {etape['eleves']:>5}"
            f"  {etape['part_des_inscrits'] if etape['part_des_inscrits'] is not None else '-':>6} % des inscrits"
            + (f"  ({suite} % de l'étape d'avant)" if suite is not None else ""),
        )
    retour = rapport["retour_j7"]
    lignes += [
        "",
        f"Retour après 7 jours : {retour['revenus_apres_7_jours']} sur {retour['eleves_assez_anciens']}"
        f" comptes assez anciens ({retour['part']} %)",
        f"  dont parmi ceux qui ont terminé une séance : {_lisible(retour['revenus_parmi_ceux_qui_ont_termine_une_seance'])} %",
        f"Délai médian inscription -> paiement : {_lisible(rapport['delai_median_jusqu_au_paiement_jours'])} jours",
        "",
    ]
    p = rapport["paiements"]
    lignes += [
        f"Paiements de la période : {p['transactions']} transaction(s), réussite {p['reussite']} %",
        f"  par statut : {p['par_statut']}",
        f"  en attente depuis plus d'une heure : {p['en_attente_depuis_plus_d_une_heure']}",
        f"  paiements manuels : {p['paiements_manuels']}",
        f"  élèves ayant tenté de payer : {p['eleves_ayant_tente']}, dont jamais aboutis : {p['eleves_n_ayant_jamais_paye']}",
        "",
        f"Fréquentation (évènements de la période) : {rapport['frequentation']}",
    ]
    return "\n".join(lignes)
