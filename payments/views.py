from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from subscriptions.models import Plan

from .campay_client import CampayError
from .models import StatutTransaction, Transaction


@api_view(["POST"])
def initiate_payment(request):
    plan_id = request.data.get("plan_id")
    phone_number = request.data.get("phone_number")

    if not plan_id or not phone_number:
        return Response({"error": "Fournis plan_id et phone_number."}, status=400)

    plan = get_object_or_404(Plan, pk=plan_id, is_active=True)
    transaction = Transaction.objects.create(
        user=request.user, plan=plan, amount=plan.price, phone_number=phone_number,
    )

    try:
        transaction.initiate()
    except CampayError as exc:
        transaction.status = StatutTransaction.FAILED
        transaction.save(update_fields=["status", "updated_at"])
        return Response({"error": str(exc)}, status=502)

    return Response({"transaction_id": transaction.id, "status": transaction.status})


@api_view(["GET"])
def check_payment_status(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id, user=request.user)

    if transaction.status == StatutTransaction.PENDING and transaction.campay_reference:
        try:
            transaction.sync_status()
        except CampayError as exc:
            return Response({"error": str(exc)}, status=502)

    return Response({
        "status": transaction.status,
        "subscription_active": transaction.subscription.is_active if transaction.subscription else False,
    })
