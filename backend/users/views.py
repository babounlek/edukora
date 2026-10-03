from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address
from django.utils import timezone
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
    confirm_email_link,
    request_email_link,
    IdentityNotFound,
    LastIdentityError,
    PhoneAlreadyTaken,
    PhoneUnchanged,
    confirm_email_link,
    confirm_phone_change,
    request_email_link,
    request_phone_change,
    unlink_identity,
)
from .email_service import (
    EmailAlreadyTaken,
    EmailCapReached,
    EmailInvalid,
    EmailSendFailed,
    EmailThrottled,
    request_email_code,
    verify_email_code,
)
from . import pin as pin_module
from .email_service import consume_email_code
from .otp_service import (
    OTPCapReached, OTPInvalid, OTPSendFailed, OTPThrottled, consume_otp, request_otp, verify_otp,
)
from .models import AuthIdentity, AuthProvider, Profil, User
from .parent import creer_jeton, exiger_mode_parent, jeton_parent_valide, session_restreinte
from .phone import to_e164
from .profils import profil_actif
from .serializers import (
    EmailCodeRequestSerializer,
    EmailCodeVerifySerializer,
    EmailLinkConfirmSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    PhoneChangeConfirmSerializer,
    PhoneChangeRequestSerializer,
    ProfilSerializer,
    ProfilWriteSerializer,
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


def _reponse_session_enfant(request, profil):
    """Tokens d'une session enfant : claim `profil_id` + `restreint` (voir users.parent)."""
    user = profil.compte
    _realigner_cursus_prepare(user, profil)
    refresh = RefreshToken.for_user(user)
    refresh["profil_id"] = profil.id
    refresh["restreint"] = True
    data = UserSerializer(user, context={"request": request}).data
    data["profil_actif"] = ProfilSerializer(profil).data
    data["session_restreinte"] = True
    response = Response({"access": str(refresh.access_token), "user": data})
    _set_refresh_cookie(response, refresh)
    return response



@api_view(["POST"])
@permission_classes([AllowAny])
def otp_request_view(request):
    serializer = OTPRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        request_otp(serializer.validated_data["phone_number"], ip_address=_client_ip(request))
    except OTPThrottled as exc:
        return Response({"error": str(exc)}, status=429)
    except (OTPCapReached, OTPSendFailed) as exc:
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
    # Un enfant qui se connecte avec SON numéro (voir Profil.connexion_phone) ouvre une
    # session limitée à son profil - jamais un compte créé sur ce numéro.
    try:
        numero = to_e164(serializer.validated_data["phone_number"])
    except ValidationError:
        numero = None
    profil_enfant = (
        Profil.objects.filter(connexion_phone=numero).select_related("compte").first() if numero else None
    )
    if profil_enfant is not None:
        try:
            consume_otp(numero, serializer.validated_data["code"])
        except OTPInvalid as exc:
            return Response({"error": str(exc)}, status=400)
        return _reponse_session_enfant(request, profil_enfant)


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
        "user": UserSerializer(user, context={"request": request}).data,
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
        "user": UserSerializer(user, context={"request": request}).data,
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

    return Response(UserSerializer(request.user, context={"request": request}).data)


def _reponse_envoi_email(exc):
    """
    Traduction commune des trois pannes d'envoi, partagée par la connexion et le
    rattachement : les deux appellent le même service et doivent répondre pareil, faute
    de quoi le frontend afficherait deux messages différents pour une seule cause.
    """
    if isinstance(exc, EmailThrottled):
        return Response({"error": str(exc)}, status=429)
    # 503 pour les deux autres : notre plafond volontaire comme la panne SMTP subie sont
    # des indisponibilités de service, rien que le demandeur puisse corriger.
    return Response({"error": str(exc)}, status=503)


@api_view(["POST"])
@permission_classes([AllowAny])
def email_code_request_view(request):
    """
    Envoie un code à une adresse quelconque, sans jamais dire si un compte y est associé.
    C'est volontaire : répondre différemment selon que l'adresse est connue transformerait
    cet endpoint en outil d'énumération des comptes de la plateforme.
    """
    serializer = EmailCodeRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        request_email_code(serializer.validated_data["email"], ip_address=_client_ip(request))
    except (EmailThrottled, EmailCapReached, EmailSendFailed) as exc:
        return _reponse_envoi_email(exc)

    return Response({"message": "Code envoyé par e-mail."})


@api_view(["POST"])
@permission_classes([AllowAny])
def email_code_verify_view(request):
    """Renvoie exactement la même charge utile qu'otp_verify_view et google_signin_view."""
    serializer = EmailCodeVerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user, cree = verify_email_code(
            email=serializer.validated_data["email"],
            code=serializer.validated_data["code"],
            referral_code=serializer.validated_data.get("referral_code", ""),
        )
    except EmailAlreadyTaken as exc:
        # 409 comme pour Google : la requête est valide, c'est l'état du compte qui
        # empêche d'aboutir, et le frontend doit orienter vers le rattachement.
        return Response({"error": str(exc)}, status=409)
    except EmailInvalid as exc:
        return Response({"error": str(exc)}, status=400)

    refresh = RefreshToken.for_user(user)
    response = Response({
        "access": str(refresh.access_token),
        "user": UserSerializer(user, context={"request": request}).data,
        "created": cree,
    })
    _set_refresh_cookie(response, refresh)
    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def email_link_request_view(request):
    """Envoie un code a l'adresse à rattacher. La session prouve déjà la possession du compte."""
    serializer = EmailCodeRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        request_email_link(
            request.user,
            serializer.validated_data["email"],
            ip_address=_client_ip(request),
        )
    except EmailAlreadyTaken as exc:
        return Response({"error": str(exc)}, status=409)
    except (EmailThrottled, EmailCapReached, EmailSendFailed) as exc:
        return _reponse_envoi_email(exc)

    return Response({"message": "Code envoyé à cette adresse."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def email_link_confirm_view(request):
    serializer = EmailLinkConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user = confirm_email_link(
            request.user,
            serializer.validated_data["email"],
            serializer.validated_data["code"],
        )
    except EmailAlreadyTaken as exc:
        return Response({"error": str(exc)}, status=409)
    except EmailInvalid as exc:
        return Response({"error": str(exc)}, status=400)

    return Response(UserSerializer(user, context={"request": request}).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def phone_change_request_view(request):
    """Envoie un code au nouveau numéro. La session prouve déjà la possession du compte."""
    if (refus := exiger_mode_parent(request)) is not None:
        return refus
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
    except (OTPCapReached, OTPSendFailed) as exc:
        return Response({"error": str(exc)}, status=503)

    return Response({"message": "Code envoyé au nouveau numéro."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def phone_change_confirm_view(request):
    if (refus := exiger_mode_parent(request)) is not None:
        return refus
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

    return Response(UserSerializer(user, context={"request": request}).data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def unlink_identity_view(request, provider):
    """Détache une méthode de connexion, jamais la dernière (voir users.account)."""
    if (refus := exiger_mode_parent(request)) is not None:
        return refus
    try:
        user = unlink_identity(request.user, provider)
    except IdentityNotFound as exc:
        return Response({"error": str(exc)}, status=404)
    except LastIdentityError as exc:
        return Response({"error": str(exc)}, status=409)

    return Response(UserSerializer(user, context={"request": request}).data)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me_view(request):
    if request.method == "PATCH":
        # Le bilan parent est un réglage du titulaire du compte : un enfant sur sa session
        # limitée, ou sur un appareil dont le code parent n'a pas été saisi, ne le change pas.
        if "bilan_parent_actif" in request.data and (refus := exiger_mode_parent(request)) is not None:
            return refus
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            # {"error": "..."} plutôt que le format DRF par défaut (dict par champ) :
            # convention déjà suivie par les autres vues de ce module (otp_request_view
            # etc.) - c'est ce que lit ApiError côté frontend (voir api/client.ts).
            first_field_errors = next(iter(serializer.errors.values()))
            return Response({"error": str(first_field_errors[0])}, status=400)
        serializer.save()

    return Response(UserSerializer(request.user, context={"request": request}).data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def profils_view(request):
    """
    GET : les profils du compte (un enfant par profil, voir Profil) - toujours au
    moins un, voir la docstring de profils_actif. POST : en ajoute un nouveau (achat
    d'un abonnement supplémentaire pour un second enfant, voir AccesPage.tsx
    "Ajouter un enfant") - ordre placé après les profils existants du compte.
    """
    if request.method == "POST":
        if (refus := exiger_mode_parent(request)) is not None:
            return refus
        serializer = ProfilWriteSerializer(data=request.data)
        if not serializer.is_valid():
            first_field_errors = next(iter(serializer.errors.values()))
            return Response({"error": str(first_field_errors[0])}, status=400)
        dernier_ordre = request.user.profils.order_by("-ordre").values_list("ordre", flat=True).first()
        profil = serializer.save(compte=request.user, ordre=(dernier_ordre or 0) + 1)
        return Response(ProfilSerializer(profil).data, status=201)

    profils = request.user.profils.all()
    return Response(ProfilSerializer(profils, many=True).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def profil_detail_view(request, profil_id):
    """Renomme un profil - jamais celui d'un autre compte (voir le filtre ci-dessous,
    même garde que unlink_identity/les autres vues "propriété du compte connecté")."""
    if (refus := exiger_mode_parent(request)) is not None:
        return refus
    profil =request.user.profils.filter(pk=profil_id).first()
    if profil is None:
        return Response({"error": "Profil introuvable."}, status=404)

    serializer = ProfilWriteSerializer(profil, data=request.data, partial=True)
    if not serializer.is_valid():
        first_field_errors = next(iter(serializer.errors.values()))
        return Response({"error": str(first_field_errors[0])}, status=400)
    serializer.save()
    return Response(ProfilSerializer(profil).data)


def _realigner_cursus_prepare(user, profil):
    """
    `User.cursus_prepare` reste account-level (voir sa docstring sur le modèle) - sans
    ce réalignement, basculer vers un enfant qui ne prépare pas le cursus actuellement
    déclaré sur le compte laisse "Aujourd'hui" montrer l'examen du PRÉCÉDENT enfant
    actif (bug signalé : le menu affichait "Junior · BAC C" alors que Junior n'a
    jamais préparé que le BEPC).

    Ne touche à rien si le cursus déjà déclaré correspond à un abonnement ACTIF de ce
    profil - un enfant qui prépare plusieurs cursus (ex. Serge : BAC C et BEPC) ne doit
    pas se voir réinitialisé sur un autre des siens à chaque bascule. Sinon, retombe
    sur `Profil.cursus_prepare` s'il est déclaré, puis sur son abonnement actif le plus
    récent, par ordre d'expiration - jamais une 3e source de vérité : la valeur
    retenue est toujours écrite dans `User.cursus_prepare`, qui reste l'unique champ lu
    partout ailleurs (voir quiz.views).
    """
    from subscriptions.models import Subscription

    abonnements_du_profil = Subscription.objects.filter(profil=profil, expires_at__gt=timezone.now())
    if user.cursus_prepare_id in set(abonnements_du_profil.values_list("cursus_id", flat=True)):
        return

    cursus = profil.cursus_prepare
    if cursus is None:
        abonnement = abonnements_du_profil.order_by("-expires_at").first()
        cursus = abonnement.cursus if abonnement else None

    if cursus is not None and cursus.id != user.cursus_prepare_id:
        user.cursus_prepare = cursus
        user.save(update_fields=["cursus_prepare"])


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def activer_profil_view(request, profil_id):
    """
    Bascule le profil actif du compte - voir la docstring de `users.profils.profil_actif`.
    Réémet un access token (claim `profil_id`) ET le cookie de refresh : sans ce
    dernier, le choix ne survivrait pas aux 2h de vie de l'access token - le prochain
    `/auth/token/refresh/` relirait l'ancien cookie, sans la claim, et retomberait sur
    le premier profil du compte.

    `cursus_id` (optionnel) : le sélecteur "Examen préparé" (Header.tsx/TeteAccueil.tsx)
    liste des ABONNEMENTS individuels, pas de simples cursus - deux profils du même
    compte peuvent y apparaître sur le même examen ("BEPC (Serge)"/"BEPC (Junior)").
    Cliquer l'un d'eux doit basculer sur CE couple (profil, cursus) précis, jamais sur
    le profil seul suivi d'un réalignement générique (`_realigner_cursus_prepare`) qui
    pourrait retomber sur un AUTRE cursus du même profil - régression signalée :
    "un enfant avec un cursus qui n'est pas le sien". Sans `cursus_id` (bascule depuis
    "Changer d'enfant", qui ne connaît qu'un profil), le réalignement générique reste
    le repli.
    """
    if session_restreinte(request):
        return Response(
            {"error": "Depuis ta session, tu ne peux pas changer de profil.", "code": "session_restreinte"},
            status=403,
        )
    profil = request.user.profils.filter(pk=profil_id).first()
    if profil is None:
        return Response({"error": "Profil introuvable."}, status=404)

    # PIN du profil, vérifié ici (côté serveur) : jamais seulement dans l'interface. Pas
    # redemandé pour le profil déjà actif (rechargement), ni en mode parent ; le PIN parent
    # ouvre aussi n'importe quel profil (code enfant oublié).
    # `reverifier` : l'écran de verrouillage après inactivité redemande le code du profil
    # DÉJÀ actif (voir VerrouInactivite côté frontend).
    demande_reverif = bool(request.data.get("reverifier"))
    if (
        profil.pin_hash
        and (profil_actif(request).pk != profil.pk or demande_reverif)
        and not jeton_parent_valide(request)
    ):
        saisi = request.data.get("pin")
        if not saisi:
            return Response({"error": "Saisis le code de ce profil.", "code": "pin_requis"}, status=403)
        try:
            try:
                pin_module.verifier(profil, pin_module.PROFIL, str(saisi))
            except pin_module.PinInvalide:
                if not request.user.pin_parent_hash:
                    raise
                pin_module.verifier(request.user, pin_module.PARENT, str(saisi))
        except pin_module.PinBloque as exc:
            return Response({"error": str(exc), "code": "pin_bloque"}, status=429)
        except pin_module.PinInvalide as exc:
            return Response({"error": str(exc), "code": "pin_incorrect"}, status=403)

    if cursus_id := request.data.get("cursus_id"):
        from subscriptions.models import Subscription

        a_cet_abonnement = Subscription.objects.filter(
            profil=profil, cursus_id=cursus_id, expires_at__gt=timezone.now(),
        ).exists()
        if not a_cet_abonnement:
            return Response({"error": "Ce cursus n'appartient pas à ce profil."}, status=400)
        if str(request.user.cursus_prepare_id) != str(cursus_id):
            request.user.cursus_prepare_id = cursus_id
            request.user.save(update_fields=["cursus_prepare"])
    else:
        _realigner_cursus_prepare(request.user, profil)

    refresh = RefreshToken.for_user(request.user)
    refresh["profil_id"] = profil.id
    # La requête courante porte encore l'ANCIENNE claim (ou aucune) : profil_actif(request),
    # lu via UserSerializer.get_profil_actif, ne verrait pas encore ce changement -
    # le profil nouvellement actif est donc injecté explicitement plutôt que relu.
    data = UserSerializer(request.user, context={"request": request}).data
    data["profil_actif"] = ProfilSerializer(profil).data
    response = Response({"access": str(refresh.access_token), "user": data})
    _set_refresh_cookie(response, refresh)
    return response


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


# --- PIN parent, PIN des profils et connexion propre d'un enfant -----------------------
# Voir users.pin (codes), users.parent (mode parent, session enfant) et la docstring de
# Profil. Toutes ces vues sont refusées à une session enfant.


def _refus_session_enfant(request):
    if session_restreinte(request):
        return Response({"error": "Cette action est réservée au parent.", "code": "session_restreinte"}, status=403)
    return None


def _reponse_pin(exc):
    if isinstance(exc, pin_module.PinBloque):
        return Response({"error": str(exc), "code": "pin_bloque"}, status=429)
    return Response({"error": str(exc), "code": "pin_incorrect"}, status=403)


def _pin_depuis(request, cle="pin"):
    valeur = request.data.get(cle)
    return str(valeur) if valeur is not None else ""


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def parent_verifier_view(request):
    """Saisie du PIN parent : renvoie le jeton court du « mode parent » (en-tête X-Parent-Token)."""
    if (refus := _refus_session_enfant(request)) is not None:
        return refus
    if not request.user.pin_parent_hash:
        return Response({"error": "Aucun code parent n'est défini."}, status=400)
    try:
        pin_module.verifier(request.user, pin_module.PARENT, _pin_depuis(request))
    except (pin_module.PinBloque, pin_module.PinInvalide) as exc:
        return _reponse_pin(exc)
    from .parent import DUREE_SECONDES

    return Response({"jeton": creer_jeton(request.user), "expire_dans": DUREE_SECONDES})


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def parent_pin_view(request):
    """
    POST : définit (ou change) le PIN parent - le changement exige `pin_actuel`.
    DELETE : le retire - exige `pin_actuel`. Un oubli passe par la réinitialisation par code.
    """
    if (refus := _refus_session_enfant(request)) is not None:
        return refus
    user = request.user
    if user.pin_parent_hash:
        try:
            pin_module.verifier(user, pin_module.PARENT, _pin_depuis(request, "pin_actuel"))
        except (pin_module.PinBloque, pin_module.PinInvalide) as exc:
            return _reponse_pin(exc)

    if request.method == "DELETE":
        pin_module.effacer(user, pin_module.PARENT)
    else:
        try:
            pin_module.definir(user, pin_module.PARENT, _pin_depuis(request))
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)
    return Response(UserSerializer(user, context={"request": request}).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def parent_reinitialiser_demander_view(request):
    """PIN parent oublié : envoie un code de vérification au numéro (ou à l'e-mail confirmé) du compte."""
    if (refus := _refus_session_enfant(request)) is not None:
        return refus
    user = request.user
    try:
        if user.phone_number:
            request_otp(user.phone_number, ip_address=_client_ip(request))
        elif user.email and user.email_verified:
            request_email_code(user.email, ip_address=_client_ip(request))
        else:
            return Response({"error": "Aucun moyen de te joindre n'est enregistré sur ce compte."}, status=400)
    except (OTPThrottled, EmailThrottled) as exc:
        return Response({"error": str(exc)}, status=429)
    except (OTPCapReached, OTPSendFailed, EmailCapReached, EmailSendFailed) as exc:
        return Response({"error": str(exc)}, status=503)
    return Response({"message": "Code envoyé."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def parent_reinitialiser_confirmer_view(request):
    """Vérifie le code reçu puis retire le PIN parent (on peut alors en définir un nouveau)."""
    if (refus := _refus_session_enfant(request)) is not None:
        return refus
    user = request.user
    code = str(request.data.get("code", ""))
    try:
        if user.phone_number:
            consume_otp(user.phone_number, code)
        elif user.email and user.email_verified:
            consume_email_code(user.email, code)
        else:
            return Response({"error": "Aucun moyen de te joindre n'est enregistré sur ce compte."}, status=400)
    except (OTPInvalid, EmailInvalid) as exc:
        return Response({"error": str(exc)}, status=400)
    pin_module.effacer(user, pin_module.PARENT)
    return Response(UserSerializer(user, context={"request": request}).data)


def _profil_du_compte(request, profil_id):
    return request.user.profils.filter(pk=profil_id).first()


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def profil_pin_view(request, profil_id):
    """Définit (POST {pin}) ou retire (DELETE) le PIN d'un profil - mode parent requis."""
    if (refus := exiger_mode_parent(request)) is not None:
        return refus
    profil = _profil_du_compte(request, profil_id)
    if profil is None:
        return Response({"error": "Profil introuvable."}, status=404)
    if request.method == "DELETE":
        pin_module.effacer(profil, pin_module.PROFIL)
    else:
        try:
            pin_module.definir(profil, pin_module.PROFIL, _pin_depuis(request))
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)
    return Response(ProfilSerializer(profil).data)


def _numero_connexion_libre(profil, saisie):
    """(numéro E.164, None) si le numéro de l'enfant est utilisable, sinon (None, Response d'erreur)."""
    try:
        numero = to_e164(saisie)
    except ValidationError:
        numero = None
    if not numero:
        return None, Response({"error": "Numéro de téléphone invalide."}, status=400)
    pris = (
        User.objects.filter(phone_number=numero).exists()
        or AuthIdentity.objects.filter(provider=AuthProvider.PHONE, provider_uid=numero).exists()
        or Profil.objects.filter(connexion_phone=numero).exclude(pk=profil.pk).exists()
    )
    if pris:
        return None, Response({"error": "Ce numéro est déjà utilisé par un autre compte."}, status=409)
    return numero, None


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def profil_connexion_demander_view(request, profil_id):
    """Envoie un code au numéro de l'enfant pour qu'il puisse se connecter lui-même."""
    if (refus := exiger_mode_parent(request)) is not None:
        return refus
    profil = _profil_du_compte(request, profil_id)
    if profil is None:
        return Response({"error": "Profil introuvable."}, status=404)
    numero, erreur = _numero_connexion_libre(profil, request.data.get("phone_number"))
    if erreur is not None:
        return erreur
    try:
        request_otp(numero, ip_address=_client_ip(request))
    except OTPThrottled as exc:
        return Response({"error": str(exc)}, status=429)
    except (OTPCapReached, OTPSendFailed) as exc:
        return Response({"error": str(exc)}, status=503)
    return Response({"message": "Code envoyé au numéro de l'enfant."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def profil_connexion_confirmer_view(request, profil_id):
    """Confirme le code reçu par l'enfant : le numéro devient sa connexion personnelle."""
    if (refus := exiger_mode_parent(request)) is not None:
        return refus
    profil = _profil_du_compte(request, profil_id)
    if profil is None:
        return Response({"error": "Profil introuvable."}, status=404)
    numero, erreur = _numero_connexion_libre(profil, request.data.get("phone_number"))
    if erreur is not None:
        return erreur
    try:
        consume_otp(numero, str(request.data.get("code", "")))
    except OTPInvalid as exc:
        return Response({"error": str(exc)}, status=400)
    profil.connexion_phone = numero
    profil.save(update_fields=["connexion_phone"])
    return Response(ProfilSerializer(profil).data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def profil_connexion_supprimer_view(request, profil_id):
    if (refus := exiger_mode_parent(request)) is not None:
        return refus
    profil = _profil_du_compte(request, profil_id)
    if profil is None:
        return Response({"error": "Profil introuvable."}, status=404)
    profil.connexion_phone = None
    profil.save(update_fields=["connexion_phone"])
    return Response(ProfilSerializer(profil).data)
