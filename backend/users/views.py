from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .otp_service import OTPInvalid, OTPThrottled, request_otp, verify_otp
from .serializers import OTPRequestSerializer, OTPVerifySerializer, UserSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def otp_request_view(request):
    serializer = OTPRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        request_otp(serializer.validated_data["phone_number"])
    except OTPThrottled as exc:
        return Response({"error": str(exc)}, status=429)

    return Response({"message": "Code envoyé par SMS."})


@api_view(["POST"])
@permission_classes([AllowAny])
def otp_verify_view(request):
    serializer = OTPVerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user = verify_otp(
            phone_number=serializer.validated_data["phone_number"],
            code=serializer.validated_data["code"],
            referral_code=serializer.validated_data.get("referral_code", ""),
        )
    except OTPInvalid as exc:
        return Response({"error": str(exc)}, status=400)

    refresh = RefreshToken.for_user(user)
    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": UserSerializer(user).data,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(UserSerializer(request.user).data)
