from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .google import (
    GoogleAccountConflict,
    GoogleAuthError,
    GoogleNotConfigured,
    link_google_identity,
    resolve_google_account,
    verify_google_id_token,
)
from .account import (
    IdentityNotFound,
    LastIdentityError,
    PhoneAlreadyTaken,
    PhoneUnchanged,
    confirm_phone_change,
    request_phone_change,
    unlink_identity,
)
from .otp_service import OTPCapReached, OTPInvalid, OTPThrottled, request_otp, verify_otp
from .serializers import (
    OTPRequestSerializer,
    OTPVerifySerializer,
    PhoneChangeConfirmSerializer,
    PhoneChangeRequestSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
)

# Nom distinct de "sessionid"/"csrftoken" (jamais utilisés ici - voir REST_FRAMEWORK,
# aucune SessionAuthentication) pour qu'il ne soit jamais confondu avec un cookie
# Django standard en observant le trafic. Path restreint à /auth/ : ce cookie n'a de
# sens qu'aux deux endpoints qui le lisent (token_refresh_view/logout_view) - un
# scope plus large le renverrait sur chaque appel API sans jamais servir à rien.
REFRESH_COOKIE_NAME = "edukamer_refresh"
REFRESH_COOKIE_PATH = "/auth/"


def _set_refresh_cookie(response, refresh_token):
    """
    Le refresh token (longue durée, 30j - voir SIMPLE_JWT) ne transite plus jamais en
    JSON ni ne vit en localStorage côté frontend : un cookie httpOnly ne peut pas être
    lu par du JavaScript, donc invisible à un XSS qui parviendrait à s'exécuter sur la
    page. L'access token (courte durée, 2h) reste lui géré en mémoire côté frontend -
    voir api/client.ts - jamais dans un cookie, donc jamais soumis au CSRF.

    secure=SESSION_COOKIE_SECURE (pas une valeur séparée) : réutilise le même calcul
    que le reste du projet (dérivé de SECURE_SSL_REDIRECT, voir settings.py) pour que
    ce cookie suive exactement la même règle dev (HTTP autorisé) vs prod (HTTPS
    obligatoire) que les cookies Django existants, sans une deuxième source de vérité.

    samesite="Lax" comme seule protection CSRF (pas de token CSRF explicite) : un
    cookie Lax n'est jamais envoyé sur une requête POST cross-site (la vraie surface
    d'attaque CSRF), seulement sur les navigations GET de premier niveau - suffisant
    ici puisque ce cookie n'est lu que par deux endpoints POST (refresh/logout), et
    DRF désactive de toute façon la protection CSRF Django standard sur les vues API
    (voir APIView, csrf_exempt implicite) tant qu'aucune SessionAuthentication n'est
    utilisée.
    """
    max_age = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        str(refresh_token),
        max_age=max_age,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="Lax",
        path=REFRESH_COOKIE_PATH,
    )


def _client_ip(request):
    """
    IP réelle du demandeur, pour le plafond par source de users.otp_service.request_otp.

    REMOTE_ADDR ne sert à rien en production : derrière Caddy (voir
    docker/caddy/Caddyfile), Django ne voit jamais que l'IP du conteneur reverse proxy,
    identique pour tout le monde. On lit donc X-Forwarded-For - mais l'entrée la plus à
    DROITE, pas la première : Caddy AJOUTE l'IP du pair qu'il constate à la valeur
    éventuellement déjà présente dans la requête entrante. Les entrées de gauche sont
    donc fournies par le client, librement falsifiables, et le seul maillon de confiance
    est la dernière, écrite par notre propre proxy. Ce raisonnement ne tient que tant
    qu'il y a exactement un proxy de confiance devant Django (le cas ici : gunicorn
    n'est joignable que sur le réseau interne Docker, jamais exposé) - il serait à
    revoir en insérant un CDN ou un second proxy devant Caddy.

    Retourne None plutôt qu'une valeur douteuse si rien d'exploitable n'est trouvé :
    request_otp sait traiter ce cas (il saute le plafond par IP, le plafond global
    couvrant toujours), là où une chaîne non validée ferait échouer l'écriture en base
    (GenericIPAddressField = type `inet` côté PostgreSQL) et transformerait un en-tête
    malformé en erreur 500.
    """
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    candidate = forwarded.split(",")[-1].strip() if forwarded else request.META.get("REMOTE_ADDR", "")
    if not candidate:
        return None
    try:
        validate_ipv46_address(candidate)
    except ValidationError:
        return None
    return candidate


@api_view(["POST"])
@permission_classes([AllowAny])
def otp_request_view(request):
    serializer = OTPRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        request_otp(serializer.validated_data["phone_number"], ip_address=_client_ip(request))
    except OTPThrottled as exc:
        return Response({"error": str(exc)}, status=429)
    except OTPCapReached as exc:
        # 503 et pas 429 : le demandeur n'a rien à corriger ni à ralentir, c'est le
        # service qui est indisponible - un 429 inviterait le frontend à afficher
        # "vous allez trop vite" à quelqu'un qui n'a fait qu'une seule tentative.
        return Response({"error": str(exc)}, status=503)

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
    response = Response({
        "access": str(refresh.access_token),
        "user": UserSerializer(user).data,
    })
    _set_refresh_cookie(response, refresh)
    return response


@api_view(["POST"])
@permission_classes([AllowAny])
def google_signin_view(request):
    """
    « Continuer avec Google » : reçoit l'ID token émis par Google Identity Services
    côté navigateur et renvoie exactement la même charge utile que otp_verify_view
    (access token + cookie de refresh), pour que le frontend traite les deux
    connexions par le même chemin.
    """
    try:
        claims = verify_google_id_token(request.data.get("credential"))
        user, cree = resolve_google_account(
            claims, referral_code=request.data.get("referral_code", "") or "",
        )
    except GoogleNotConfigured:
        return Response({"error": "La connexion Google n'est pas disponible."}, status=503)
    except GoogleAccountConflict as exc:
        # 409 et pas 400 : la requête est valide, c'est l'état du compte qui empêche
        # d'aboutir, et le frontend doit orienter vers le rattachement plutôt que
        # laisser croire à une saisie erronée.
        return Response({"error": str(exc)}, status=409)
    except GoogleAuthError as exc:
        return Response({"error": str(exc)}, status=401)

    refresh = RefreshToken.for_user(user)
    response = Response({
        "access": str(refresh.access_token),
        "user": UserSerializer(user).data,
        "created": cree,
    })
    _set_refresh_cookie(response, refresh)
    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def google_link_view(request):
    """
    Rattache Google à un compte déjà connecté. Séparé de google_signin_view parce que
    la règle de sécurité n'est pas la même : ici la possession du compte est prouvée
    par la session, ce qui autorise un rattachement que la connexion refuserait.
    """
    try:
        claims = verify_google_id_token(request.data.get("credential"))
        link_google_identity(request.user, claims)
    except GoogleNotConfigured:
        return Response({"error": "La connexion Google n'est pas disponible."}, status=503)
    except GoogleAccountConflict as exc:
        return Response({"error": str(exc)}, status=409)
    except GoogleAuthError as exc:
        return Response({"error": str(exc)}, status=401)

    return Response(UserSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def phone_change_request_view(request):
    """Envoie un code au nouveau numéro. La session prouve déjà la possession du compte."""
    serializer = PhoneChangeRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        request_phone_change(
            request.user,
            serializer.validated_data["phone_number"],
            ip_address=_client_ip(request),
        )
    except (PhoneAlreadyTaken, PhoneUnchanged) as exc:
        return Response({"error": str(exc)}, status=409)
    except OTPThrottled as exc:
        return Response({"error": str(exc)}, status=429)
    except OTPCapReached as exc:
        return Response({"error": str(exc)}, status=503)

    return Response({"message": "Code envoyé au nouveau numéro."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def phone_change_confirm_view(request):
    serializer = PhoneChangeConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user = confirm_phone_change(
            request.user,
            serializer.validated_data["phone_number"],
            serializer.validated_data["code"],
        )
    except PhoneAlreadyTaken as exc:
        return Response({"error": str(exc)}, status=409)
    except OTPInvalid as exc:
        return Response({"error": str(exc)}, status=400)

    return Response(UserSerializer(user).data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def unlink_identity_view(request, provider):
    """Détache une méthode de connexion, jamais la dernière (voir users.account)."""
    try:
        user = unlink_identity(request.user, provider)
    except IdentityNotFound as exc:
        return Response({"error": str(exc)}, status=404)
    except LastIdentityError as exc:
        return Response({"error": str(exc)}, status=409)

    return Response(UserSerializer(user).data)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me_view(request):
    if request.method == "PATCH":
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            # {"error": "..."} plutôt que le format DRF par défaut (dict par champ) :
            # convention déjà suivie par les autres vues de ce module (otp_request_view
            # etc.) - c'est ce que lit ApiError côté frontend (voir api/client.ts).
            first_field_errors = next(iter(serializer.errors.values()))
            return Response({"error": str(first_field_errors[0])}, status=400)
        serializer.save()

    return Response(UserSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def token_refresh_view(request):
    """
    Remplace TokenRefreshView (djangorestframework_simplejwt) : le refresh token n'est
    plus jamais fourni dans le corps de la requête (voir SIMPLE_JWT côté frontend, qui
    ne le détient plus du tout) mais lu depuis le cookie httpOnly posé par
    otp_verify_view. AllowAny : un access token expiré ne doit jamais empêcher de le
    rafraîchir, c'est précisément le cas d'usage de cet endpoint.

    Ne fait volontairement pas de rotation (pas de nouveau refresh token émis à chaque
    appel) : SIMPLE_JWT ne l'active pas non plus aujourd'hui (ROTATE_REFRESH_TOKENS
    absent = False par défaut), et l'activer demanderait la blacklist de l'ancien
    jeton (app token_blacklist, non installée) pour empêcher sa réutilisation - hors
    scope de cette migration, qui ne change QUE l'emplacement du refresh token
    (cookie plutôt que localStorage), pas sa politique de rotation.
    """
    raw_refresh = request.COOKIES.get(REFRESH_COOKIE_NAME)
    if not raw_refresh:
        return Response({"error": "Session expirée."}, status=401)

    try:
        refresh = RefreshToken(raw_refresh)
    except TokenError:
        return Response({"error": "Session expirée."}, status=401)

    return Response({"access": str(refresh.access_token)})


@api_view(["POST"])
@permission_classes([AllowAny])
def logout_view(request):
    """
    AllowAny : une déconnexion doit réussir même si l'access token en mémoire côté
    frontend est déjà expiré - le seul état qui compte ici est le cookie à effacer,
    pas l'authentification de la requête elle-même. Pas de blacklist du refresh token
    (voir token_refresh_view) : effacer le cookie suffit à empêcher tout futur usage
    depuis CE navigateur, qui est la seule chose que "se déconnecter" doit garantir.
    """
    response = Response({"message": "Déconnecté."})
    response.delete_cookie(REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)
    return response
