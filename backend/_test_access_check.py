import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edtech_cm.settings")
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

from users.models import User

user = User.objects.get(phone_number="670401393")
token = str(RefreshToken.for_user(user).access_token)

client = APIClient()
client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

resp = client.get("/catalog/lessons/23/")
print(resp.status_code, resp.json())
