import sentry_sdk
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from subscriptions.models import Plan, solde_credit_parrainage

from .campay_client import CampayError
from .models import ManualPayment, MobileMoneyAccount, StatutTransaction, Transaction
from .serializers import ManualPaymentDeclareSerializer, ManualPaymentSerializer, MobileMoneyAccountSerializer


def _report_campay_error(exc, transaction):
    """
    CampayError est déjà gérée gracieusement ici (réponse 502 propre, jamais un
    crash) - donc jamais remontée automatiquement par l'intégration Django de Sentry,
    qui ne capture que les exceptions non gérées. Un échec de la chaîne de paiement
    reste pourtant le signal le plus critique du produit (voir l'audit UX, reco 5.1)
    - capturé explicitement, avec un tag dédié pour pouvoir configurer une alerte
    prioritaire dans Sentry sans avoir à filtrer sur le texte du message.
    """
    with sentry_sdk.new_scope() as scope:
        scope.set_tag("critical_path", "payment")
        scope.set_context("transaction", {"id": transaction.id, "status": transaction.status})
        sentry_sdk.capture_exception(exc)


@api_view(["POST"])
def initiate_payment(request):
    plan_id = request.data.get("plan_id")
    phone_number = request.data.get("phone_number")

    if not plan_id or not phone_number:
        return Response({"error": "Fournis plan_id et phone_number."}, status=400)

    plan = get_object_or_404(Plan, pk=plan_id, is_active=True)

    prix = plan.effective_price()
    # Remise automatique par crédit parrainage disponible (voir
    # subscriptions.models.solde_credit_parrainage) - jamais sur le paiement manuel
    # pour l'instant, qui suppose un vrai transfert Mobile Money à déclarer/prouver.
    credit_applique = min(prix, solde_credit_parrainage(request.user))
    montant_a_payer = prix - credit_applique

    if montant_a_payer == 0:
        transaction = Transaction.objects.creer_couverte_par_credit(
            user=request.user, plan=plan, phone_number=phone_number, credit_applique=credit_applique,
        )
        return Response({
            "transaction_id": transaction.id, "status": transaction.status,
            "amount": transaction.amount, "credit_applique": transaction.credit_applique,
        })

    transaction = Transaction.objects.create(
        user=request.user, plan=plan, amount=montant_a_payer,
        phone_number=phone_number, credit_applique=credit_applique,
    )

    try:
        transaction.initiate()
    except CampayError as exc:
        transaction.status = StatutTransaction.FAILED
        transaction.save(update_fields=["status", "updated_at"])
        _report_campay_error(exc, transaction)
        return Response({"error": str(exc)}, status=502)

    return Response({
        "transaction_id": transaction.id, "status": transaction.status,
        "amount": transaction.amount, "credit_applique": transaction.credit_applique,
    })


@api_view(["GET"])
def check_payment_status(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id, user=request.user)

    if transaction.status == StatutTransaction.PENDING and transaction.campay_reference:
        try:
            transaction.sync_status()
        except CampayError as exc:
            _report_campay_error(exc, transaction)
            return Response({"error": str(exc)}, status=502)

    return Response({
        "status": transaction.status,
        "subscription_active": transaction.subscription.is_active if transaction.subscription else False,
        "inscription_inedite_active": transaction.inscription_inedite.is_active if transaction.inscription_inedite else False,
    })


@api_view(["GET"])
def list_manual_payment_methods(request):
    accounts = MobileMoneyAccount.objects.filter(active=True)
    return Response(MobileMoneyAccountSerializer(accounts, many=True).data)


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def declare_manual_payment(request):
    serializer = ManualPaymentDeclareSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    payment = serializer.save()
    return Response(ManualPaymentSerializer(payment).data, status=201)


@api_view(["GET"])
def list_my_manual_payments(request):
    payments = ManualPayment.objects.filter(user=request.user).select_related(
        "plan", "plan__cursus", "plan__cursus__country", "plan__cursus__series",
    )
    return Response(ManualPaymentSerializer(payments, many=True).data)
