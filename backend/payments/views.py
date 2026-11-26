from datetime import timedelta

import sentry_sdk
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from subscriptions.models import Plan, solde_credit_parrainage
from users.models import phone_validator
from users.parent import exiger_mode_parent
from users.phone import to_e164, to_local
from users.profils import profil_actif

from .providers import PaiementFournisseurError
from .models import ManualPayment, MobileMoneyAccount, StatutTransaction, Transaction
from .serializers import (
    ManualPaymentDeclareSerializer, ManualPaymentSerializer, MobileMoneyAccountSerializer, TransactionSerializer,
)

# Une demande de paiement reste validable quelques minutes sur le téléphone du payeur. Tant qu'elle peut encore
# aboutir, en envoyer une deuxième sans le dire, c'est risquer deux débits (voir initiate_payment).
FENETRE_DEMANDE_EN_ATTENTE = timedelta(minutes=10)

# Ce que le payeur lit quand l'agrégateur fait défaut, par code (voir PaiementFournisseurError.code). Le texte de
# l'exception, lui, est technique : « Échec d'authentification CamPay : {"non_field_errors": ...} » s'affichait tel
# quel sur l'écran de paiement (audit du tunnel de paiement, 2026-11-26). Le client traduit d'après le code ; ce
# texte français est le repli.
MESSAGES_PAYEUR = {
    "paiement_indisponible": (
        "Le paiement Mobile Money est momentanément indisponible. Rien n'a été débité : réessaie dans quelques minutes."
    ),
    "numero_refuse": (
        "Ce numéro n'a pas été accepté. Vérifie que c'est bien un numéro Orange ou MTN avec un compte Mobile Money "
        "actif, puis réessaie."
    ),
}


def _resoudre_profil(request):
    """
    Le profil (l'enfant) pour qui cet achat est fait - `profil_id` optionnel dans le
    corps de la requête (voir "Ajouter un enfant", AccesPage.tsx), jamais accepté sans
    vérifier qu'il appartient bien au compte connecté. Retombe sur le profil ACTIF
    de la requête par défaut (voir users.profils.profil_actif : sans profil choisi,
    c'est le premier du compte, donc inchangé pour l'immense majorité des achats -
    compte à un seul profil). Avant, le repli était toujours `profils.first()` : un
    parent connecté sur le profil du cadet payait pour l'aîné (test élève 2026-10-24).

    Retourne (profil, erreur) - `erreur` est une Response 400 prête à renvoyer si
    `profil_id` est fourni mais n'appartient pas au compte, None sinon.
    """
    profil_id = request.data.get("profil_id")
    if not profil_id:
        return profil_actif(request), None
    profil = request.user.profils.filter(pk=profil_id).first()
    if profil is None:
        return None, Response({"error": "Profil introuvable."}, status=400)
    return profil, None


def _lire_mois(request, plan):
    """
    Le nombre de mois demandé (`mois`, 1 par défaut), vérifié contre ce que le plan autorise - voir
    Plan.mois_max : jamais un nombre de mois accepté tel quel, qui permettrait d'acheter des mois après
    l'examen, ou d'en demander pour un plan qui ne se vend pas au mois. Retourne (mois, erreur), `erreur` étant
    une Response 400 prête à renvoyer.
    """
    brut = request.data.get("mois", 1)
    try:
        mois = int(brut)
    except (TypeError, ValueError):
        return None, Response({"error": "Nombre de mois invalide."}, status=400)
    if not plan.mois_valide(mois):
        maximum = plan.mois_max()
        message = (
            f"Choisis entre 1 et {maximum} mois : au-delà, ton examen serait déjà passé."
            if plan.est_au_mois and maximum > 1
            else "Ce plan s'achète en une seule fois."
        )
        return None, Response({"error": message, "mois_max": maximum}, status=400)
    return mois, None


def _report_provider_error(exc, transaction):
    """
    PaiementFournisseurError (CampayError, etc.) est déjà gérée gracieusement ici (réponse 503 propre - jamais 502 : Cloudflare remplace le corps d un 502 par « error code: 502 » -, jamais un
    crash) - donc jamais remontée automatiquement par l'intégration Django de Sentry,
    qui ne capture que les exceptions non gérées. Un échec de la chaîne de paiement
    reste pourtant le signal le plus critique du produit (voir l'audit UX, reco 5.1)
    - capturé explicitement, avec un tag dédié pour pouvoir configurer une alerte
    prioritaire dans Sentry sans avoir à filtrer sur le texte du message.
    """
    with sentry_sdk.new_scope() as scope:
        scope.set_tag("critical_path", "payment")
        scope.set_context("transaction", {
            "id": transaction.id, "status": transaction.status, "provider": transaction.provider,
        })
        sentry_sdk.capture_exception(exc)


def _refus_fournisseur(exc):
    """La réponse 503 d'une défaillance de l'agrégateur : un message pour le payeur et son code, jamais le détail technique."""
    code = exc.code if exc.code in MESSAGES_PAYEUR else "paiement_indisponible"
    return Response({"error": MESSAGES_PAYEUR[code], "code": code}, status=503)


def _lire_numero(request):
    """
    Le numéro Mobile Money du payeur, ramené au format local à 9 chiffres (celui de Transaction.phone_number).
    Accepte aussi l'indicatif (« +237 6… », « 2376… ») : le numéro du compte est stocké ainsi. Retourne
    (numero, erreur) - un numéro mal formé était envoyé tel quel à l'agrégateur, ou débordait de la colonne.
    """
    try:
        numero = to_local(to_e164(request.data.get("phone_number")))
        phone_validator(numero)
    except DjangoValidationError:
        return None, Response(
            {"error": "Entre un numéro Mobile Money valide (9 chiffres, commence par 6).", "code": "numero_invalide"},
            status=400,
        )
    return numero, None


def _corps_transaction(transaction, **en_plus):
    """Ce que l'écran d'abonnement lit d'une transaction : de quoi afficher l'attente et la reprendre."""
    return {
        "transaction_id": transaction.id,
        "status": transaction.status,
        "amount": transaction.amount,
        "credit_applique": transaction.credit_applique,
        "phone_number": transaction.phone_number,
        "operator": transaction.operateur,
        "created_at": transaction.created_at,
        **en_plus,
    }


def _demandes_en_attente(user):
    """Les demandes du compte envoyées à l'agrégateur et encore validables sur le téléphone, la plus récente d'abord."""
    return Transaction.objects.filter(
        user=user, status=StatutTransaction.PENDING,
        created_at__gte=timezone.now() - FENETRE_DEMANDE_EN_ATTENTE,
    ).exclude(provider_reference="").order_by("-created_at")


@api_view(["GET"])
@permission_classes([AllowAny])
def payment_config(request):
    """
    État public des moyens de paiement, lu par /tarifs et /abonnement pour n'afficher
    que ce qui est réellement utilisable (voir settings.CAMPAY_ACTIVE). Public : la page
    des tarifs est ouverte aux visiteurs non connectés.

    `beneficiaires` : à qui part l'argent d'un transfert manuel, dit AVANT la création du compte (un parent veut le
    savoir avant de donner son numéro : audit du tunnel visiteur → abonné, 2026-11-21). Le nom et l'opérateur
    seulement : le numéro à créditer ne s'affiche qu'à un compte, sur l'écran de paiement, là où la déclaration se
    fait - publié ici, il inviterait à payer sans compte, donc sans pouvoir déclarer.

    `sms_active` : un code de connexion peut réellement partir par SMS (le backend console ne fait qu'écrire dans
    les journaux). L'écran de connexion ne propose le téléphone en premier que dans ce cas.
    """
    comptes = MobileMoneyAccount.objects.filter(active=True).order_by("operator")
    return Response({
        "campay_active": bool(settings.CAMPAY_ACTIVE),
        "manual_active": bool(settings.MANUAL_PAYMENT_ACTIVE),
        "beneficiaires": [
            {"operator": c.operator, "operator_display": c.get_operator_display(), "account_name": c.account_name}
            for c in comptes
        ] if settings.MANUAL_PAYMENT_ACTIVE else [],
        "sms_active": settings.SMS_BACKEND != "users.sms_backends.ConsoleSMSBackend",
    })


@api_view(["POST"])
def initiate_payment(request):
    if (refus := exiger_mode_parent(request)) is not None:
        return refus
    if not settings.CAMPAY_ACTIVE:
        # Refus net, avant toute Transaction créée : un paiement lancé sur un fournisseur
        # coupé resterait sinon PENDING dans l'historique sans jamais pouvoir aboutir.
        # Le repli vers le transfert manuel n'est proposé que s'il existe (MANUAL_PAYMENT_ACTIVE).
        if not settings.MANUAL_PAYMENT_ACTIVE:
            return Response(
                {"error": MESSAGES_PAYEUR["paiement_indisponible"], "code": "paiement_indisponible"}, status=503,
            )
        return Response(
            {"error": "Le paiement automatique est momentanément indisponible. "
                      "Utilise le paiement manuel via Orange Money ou MTN MoMo."},
            status=503,
        )
    plan_id = request.data.get("plan_id")

    if not plan_id or not request.data.get("phone_number"):
        return Response({"error": "Fournis plan_id et phone_number."}, status=400)

    plan = get_object_or_404(Plan, pk=plan_id, is_active=True)
    phone_number, erreur = _lire_numero(request)
    if erreur is not None:
        return erreur
    profil, erreur = _resoudre_profil(request)
    if erreur is not None:
        return erreur

    mois, erreur = _lire_mois(request, plan)
    if erreur is not None:
        return erreur

    # Une demande est peut-être déjà en attente sur ce téléphone, pour le même achat : « Réessayer » après le
    # délai de l'écran, ou une page rechargée, en envoyait une deuxième, et qui validait les deux payait deux
    # fois (audit du tunnel de paiement, 2026-11-26). On relit d'abord la première auprès de l'agrégateur :
    # réussie, c'est elle la réponse ; échouée, on en envoie une neuve ; encore en attente, on la rend en le
    # disant (`deja_en_attente`), et l'écran propose d'en envoyer une autre (`nouvelle_demande`) si le payeur
    # le veut vraiment. Un autre numéro, un autre enfant ou un autre plan n'est pas la même demande.
    if not request.data.get("nouvelle_demande"):
        precedente = _demandes_en_attente(request.user).filter(
            plan=plan, phone_number=phone_number, **({"profil": profil} if profil is not None else {}),
        ).first()
        if precedente is not None:
            try:
                precedente.sync_status()
            except PaiementFournisseurError as exc:
                # Statut illisible : dans le doute elle est toujours en attente, on ne double pas la demande.
                _report_provider_error(exc, precedente)
            if precedente.status == StatutTransaction.SUCCESSFUL:
                return Response(_corps_transaction(precedente))
            if precedente.status == StatutTransaction.PENDING:
                return Response(_corps_transaction(precedente, deja_en_attente=True))

    tarif = plan.tarif(mois=mois)
    prix = tarif.prix
    # Remise automatique par crédit parrainage disponible (voir
    # subscriptions.models.solde_credit_parrainage) - mécanisme gelé depuis le
    # 2026-09-28 (le parrainage est redevenu un simple partage de lien, sans
    # récompense d'aucun côté, voir project_parrainage_eleve_recalibrage), conservé
    # ici uniquement pour que les crédits déjà accordés avant cette date restent
    # dépensables. Jamais sur le paiement manuel pour l'instant, qui suppose un vrai
    # transfert Mobile Money à déclarer/prouver.
    credit_applique = min(prix, solde_credit_parrainage(request.user))
    montant_a_payer = prix - credit_applique

    if montant_a_payer == 0:
        transaction = Transaction.objects.creer_couverte_par_credit(
            user=request.user, plan=plan, phone_number=phone_number, credit_applique=credit_applique,
            profil=profil, campagne=tarif.campagne, mois=mois,
        )
        return Response(_corps_transaction(transaction))

    transaction = Transaction.objects.create(
        user=request.user, plan=plan, amount=montant_a_payer,
        phone_number=phone_number, credit_applique=credit_applique, profil=profil,
        campagne=tarif.campagne, mois=mois,
    )

    try:
        transaction.initiate()
    except PaiementFournisseurError as exc:
        transaction.status = StatutTransaction.FAILED
        transaction.save(update_fields=["status", "updated_at"])
        _report_provider_error(exc, transaction)
        return _refus_fournisseur(exc)

    return Response(_corps_transaction(transaction))


@api_view(["GET"])
def check_payment_status(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id, user=request.user)

    if transaction.status == StatutTransaction.PENDING and transaction.provider_reference:
        try:
            transaction.sync_status()
        except PaiementFournisseurError as exc:
            _report_provider_error(exc, transaction)
            # Rien de débité ou non : on n'en sait rien ici, l'écran continue simplement de sonder.
            return Response(
                {"error": "Le statut du paiement n'a pas pu être relu pour le moment.", "code": "statut_illisible"},
                status=503,
            )

    return Response({
        "status": transaction.status,
        "operator": transaction.operateur,
        "subscription_active": transaction.subscription.is_active if transaction.subscription else False,
        "inscription_inedite_active": transaction.inscription_inedite.is_active if transaction.inscription_inedite else False,
    })


@api_view(["GET"])
def payment_en_cours(request):
    """
    La demande de paiement encore en attente du compte, s'il y en a une de moins de dix minutes : l'écran
    d'abonnement, rouvert ou rechargé, reprend son attente au lieu de présenter un formulaire vierge qui
    invite à payer une deuxième fois. `cursus` restreint à l'examen affiché. Ne relit pas l'agrégateur :
    c'est le sondage de l'écran qui le fait, dès la reprise.
    """
    en_attente = _demandes_en_attente(request.user)
    cursus = request.query_params.get("cursus")
    if cursus and cursus.isdigit():
        en_attente = en_attente.filter(plan__cursus_id=int(cursus))
    transaction = en_attente.first()
    if transaction is None:
        return Response({"en_cours": False})
    return Response(_corps_transaction(transaction, en_cours=True))


@api_view(["GET"])
def list_my_transactions(request):
    """
    Les paiements automatiques confirmés du compte, pour « Mes paiements » : la page ne montrait que les
    transferts déclarés à la main, et qui payait par la demande sur son téléphone n'y retrouvait rien.
    Les achats couverts en entier par un crédit (montant nul) n'y figurent pas : ce ne sont pas des paiements.
    """
    transactions = Transaction.objects.filter(
        user=request.user, status=StatutTransaction.SUCCESSFUL, amount__gt=0,
    ).select_related("plan", "plan__cursus", "plan__cursus__country", "plan__cursus__series", "profil")
    return Response(TransactionSerializer(transactions, many=True).data)


@api_view(["GET"])
def list_manual_payment_methods(request):
    accounts = MobileMoneyAccount.objects.filter(active=True) if settings.MANUAL_PAYMENT_ACTIVE \
        else MobileMoneyAccount.objects.none()
    return Response(MobileMoneyAccountSerializer(accounts, many=True).data)


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def declare_manual_payment(request):
    if (refus := exiger_mode_parent(request)) is not None:
        return refus
    if not settings.MANUAL_PAYMENT_ACTIVE:
        return Response({"error": "Le paiement manuel est momentanément indisponible."}, status=503)
    serializer = ManualPaymentDeclareSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    payment = serializer.save()
    return Response(ManualPaymentSerializer(payment).data, status=201)


@api_view(["GET"])
def list_my_manual_payments(request):
    payments = ManualPayment.objects.filter(user=request.user).select_related(
        "plan", "plan__cursus", "plan__cursus__country", "plan__cursus__series", "profil",
    )
    return Response(ManualPaymentSerializer(payments, many=True).data)
