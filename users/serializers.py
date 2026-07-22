from rest_framework import serializers

from .models import User

PHONE_REGEX = r"^6\d{8}$"


class OTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.RegexField(regex=PHONE_REGEX)


class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.RegexField(regex=PHONE_REGEX)
    code = serializers.RegexField(regex=r"^\d{6}$")
    referral_code = serializers.CharField(required=False, allow_blank=True, max_length=10)


class UserSerializer(serializers.ModelSerializer):
    filleuls_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "phone_number", "full_name", "date_joined", "referral_code", "filleuls_count"]

    def get_filleuls_count(self, obj):
        return obj.filleuls.count()
