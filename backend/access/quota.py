"""
Quotas quotidiens de téléchargement des PDF.

Un téléchargement est la délivrance, par le backend, d'un PDF protégé : jamais une page HTML, un bouton, une lecture en
ligne, un refus ni une erreur survenue avant l'envoi. Toute vue qui sert un PDF passe par `livrer_pdf` : une seule
logique, appliquée côté serveur, que le client soit le site, curl ou un robot.

Règle de comptage (voir aussi `autoriser`)
  - Une UNITÉ est un triplet (jour, demandeur, document). La première délivrance d'octets d'un document ce jour-là, par
    ce demandeur, consomme 1 crédit. Redemander le même PDF le même jour - relance après une coupure, reprise, second
    clic - retombe sur l'unité existante et ne coûte rien : une connexion instable ne pénalise personne. Il n'y a pas
    de trou par requêtes partielles : toute requête qui livre des octets crée l'unité si elle n'existe pas, et Django ne
    sert d'ailleurs jamais de 206 (le fichier est renvoyé en entier).
  - On ne peut pas savoir si le fichier est arrivé en entier : une coupure APRÈS l'envoi consomme le crédit. Une erreur
    AVANT l'envoi (ouverture du fichier, 5xx) l'annule (`Decision.annuler`).
  - HEAD et OPTIONS ne livrent rien et ne consomment rien ; HEAD est refusé (405) sur les routes de PDF.

Qui est qui
  - Connecté : le compteur est celui du compte (`c:<id>`) ; un profil avec un abonnement actif (Subscription,
    InscriptionInedite ou InscriptionRepetiteur non expirés, lus ICI, jamais fournis par le client) a le sien (`p:<id>`) et
    le quota « abonné ». Un compte qui crée des profils n'obtient donc pas de crédits gratuits en plus.
  - Anonyme : un identifiant aléatoire dans un cookie SIGNÉ (`edk_v`). Le cookie peut être effacé ; c'est pourquoi le
    nombre de nouveaux visiteurs reconnus par réseau et par jour est plafonné : au-delà, les visiteurs sans cookie valide
    de ce réseau partagent UN seul quota (`r:<réseau>`). Un plafond de PDF par réseau (IPv4 exacte / IPv6 /64, puis bloc
    /24 ou /48) et un budget global des anonymes bornent la rotation d'adresses. L'IP n'est jamais une identité : seul son
    hachage salé sert de clé de compteur, et les plafonds réseau sont larges (réseaux scolaires et mobiles partagés).
  - Les plafonds réseau valent aussi pour les comptes SANS abonnement (sinon créer des comptes en série contournerait
    tout). Les abonnés n'y sont jamais soumis.

Journée : civile, dans le fuseau des réglages (Africa/Douala), calculée par le serveur. Concurrence : chaque crédit est
pris par un UPDATE conditionnel atomique (`nombre < plafond`) dans une transaction, jamais par « lire puis écrire » ;
l'ordre des verrous est toujours le même, donc aucune impasse.
"""
import hashlib
import ipaddress
import secrets
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from functools import reduce
from operator import or_
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core import signing
from django.db import IntegrityError, transaction
from django.db.models import F, Q
from django.http import FileResponse
from django.utils import timezone
from django.utils.cache import patch_vary_headers
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle

from subscriptions.models import InscriptionInedite, InscriptionRepetiteur, Subscription

from .models import CompteurQuota, ReglagesTelechargement, TelechargementPdf
from .services import _du_profil

COOKIE_VISITEUR = "edk_v"
DUREE_COOKIE_S = 400 * 24 * 3600
_SEL_COOKIE = "access.quota.visiteur"

VISITEUR, CONNECTE, ABONNE = "visiteur", "connecte", "abonne"

QUOTA_DEPASSE, PLAFOND_RESEAU, BUDGET_GLOBAL = "quota_depasse", "plafond_reseau", "budget_global"

FR, EN = "fr", "en"

TEXTES = {
    QUOTA_DEPASSE: {
        FR: "Tu as atteint ta limite quotidienne de {limite} téléchargements PDF. Tu pourras télécharger à nouveau après la réinitialisation du quota, à minuit.",
        EN: "You have reached your daily limit of {limite} PDF downloads. You can download again after the quota resets at midnight.",
    },
    PLAFOND_RESEAU: {
        FR: "Beaucoup de PDF ont déjà été téléchargés aujourd'hui depuis ta connexion. Réessaie après minuit, ou connecte-toi avec un abonnement.",
        EN: "A lot of PDFs have already been downloaded from your connection today. Try again after midnight, or sign in with a subscription.",
    },
    BUDGET_GLOBAL: {
        FR: "Les téléchargements sans compte sont indisponibles pour le reste de la journée. Connecte-toi pour continuer, ou réessaie après minuit.",
        EN: "Downloads without an account are unavailable for the rest of today. Sign in to continue, or try again after midnight.",
    },
}


def _langue(request):
    """Langue du message : celle du compte connecté, sinon l'en-tête Accept-Language du navigateur."""
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        return EN if getattr(user, "langue", "fr") == "en" else FR
    return EN if request.META.get("HTTP_ACCEPT_LANGUAGE", "").lower().startswith("en") else FR


# --- Réseau --------------------------------------------------------------------------------------------------------

def _ip_cliente(request):
    # Même lecture que pour les codes OTP : la dernière entrée de X-Forwarded-For, écrite par notre proxy, jamais une
    # entrée de gauche que le client peut forger (voir users.views._client_ip).
    from users.views import _client_ip

    return _client_ip(request)


def _hacher(valeur):
    return hashlib.sha256(f"{settings.SECRET_KEY}|reseau|{valeur}".encode()).hexdigest()[:20]


def _reseaux(ip):
    """(réseau fin, réseau large) hachés : IPv4 exacte puis /24 ; IPv6 /64 puis /48. (None, None) si pas d'IP."""
    if not ip:
        return None, None
    adresse = ipaddress.ip_address(ip)
    if adresse.version == 6 and adresse.ipv4_mapped:
        adresse = adresse.ipv4_mapped
    fin, large = (32, 24) if adresse.version == 4 else (64, 48)
    return (
        _hacher(ipaddress.ip_network((adresse, fin), strict=False)),
        _hacher(ipaddress.ip_network((adresse, large), strict=False)),
    )


# --- Journée -------------------------------------------------------------------------------------------------------

def _fuseau(reglages):
    try:
        return ZoneInfo(reglages.fuseau)
    except Exception:
        return ZoneInfo(settings.TIME_ZONE)


def jour_et_reinitialisation(reglages, maintenant=None):
    """La journée en cours et l'instant de sa fin, dans le fuseau des réglages. Jamais l'heure du navigateur."""
    fuseau = _fuseau(reglages)
    local = (maintenant or timezone.now()).astimezone(fuseau)
    demain = local.date() + timedelta(days=1)
    return local.date(), datetime.combine(demain, time.min, tzinfo=fuseau)


# --- Compteurs -----------------------------------------------------------------------------------------------------

def _filtre(jour, cles):
    return Q(jour=jour) & reduce(or_, [Q(portee=p, cle=c) for p, c in cles])


def _incrementer(jour, portee, cle):
    """+1 atomique, sans plafond (statistiques, nouveaux visiteurs). Renvoie la valeur obtenue."""
    CompteurQuota.objects.get_or_create(jour=jour, portee=portee, cle=cle)
    CompteurQuota.objects.filter(jour=jour, portee=portee, cle=cle).update(nombre=F("nombre") + 1)
    return CompteurQuota.objects.values_list("nombre", flat=True).get(jour=jour, portee=portee, cle=cle)


def _nombres(jour, cles):
    return {
        (p, c): n
        for p, c, n in CompteurQuota.objects.filter(_filtre(jour, cles)).values_list("portee", "cle", "nombre")
    }


# --- Demandeur -----------------------------------------------------------------------------------------------------

def _est_abonne(user, profil):
    maintenant = timezone.now()
    filtre = {"user": user, "expires_at__gt": maintenant, **_du_profil(profil)}
    return (
        Subscription.objects.filter(**filtre).exists()
        or InscriptionInedite.objects.filter(**filtre).exists()
        or InscriptionRepetiteur.objects.filter(**filtre).exists()
    )


def _lire_cookie(request):
    brut = request.COOKIES.get(COOKIE_VISITEUR)
    if not brut:
        return None
    try:
        return signing.loads(brut, salt=_SEL_COOKIE, max_age=DUREE_COOKIE_S)
    except signing.BadSignature:
        return None


@dataclass
class Contexte:
    reglages: object
    jour: object
    reinitialisation: datetime
    profil_type: str
    demandeur: str
    limite: int
    reseau: str = None
    reseau_large: str = None
    cookie: str = None  # valeur signée à poser sur la réponse (nouveau visiteur reconnu)

    def cles(self):
        """Compteurs consultés ou consommés, TOUJOURS dans cet ordre (c'est l'ordre des verrous)."""
        cles = [("demandeur", self.demandeur)]
        if self.profil_type != ABONNE:
            if self.reseau:
                cles += [("reseau", self.reseau), ("reseau_large", self.reseau_large)]
            if self.profil_type == VISITEUR:
                cles.append(("global_anonyme", ""))
        return cles

    def plafonds(self):
        r = self.reglages
        plafonds = {("demandeur", self.demandeur): self.limite}
        if self.reseau:
            plafonds[("reseau", self.reseau)] = r.plafond_reseau
            plafonds[("reseau_large", self.reseau_large)] = r.plafond_reseau_large
        plafonds[("global_anonyme", "")] = r.budget_global_anonyme
        return plafonds

    def marge(self, nombres):
        """(utilisés, restants, motif qui limite) d'après les compteurs donnés."""
        utilise = nombres.get(("demandeur", self.demandeur), 0)
        marges = []
        for cle in self.cles():
            motif = {"demandeur": QUOTA_DEPASSE, "global_anonyme": BUDGET_GLOBAL}.get(cle[0], PLAFOND_RESEAU)
            marges.append((self.plafonds()[cle] - nombres.get(cle, 0), motif))
        restant, motif = min(marges, key=lambda m: m[0])
        return utilise, max(0, restant), motif


def contexte(request):
    """Le demandeur et ses plafonds pour cette requête (mis en cache sur la requête)."""
    memo = getattr(request, "_edk_quota", None)
    if memo is not None:
        return memo

    reglages = ReglagesTelechargement.charger()
    jour, reinitialisation = jour_et_reinitialisation(reglages)
    reseau, reseau_large = _reseaux(_ip_cliente(request))
    cookie = None

    user = request.user
    if user.is_authenticated:
        from users.profils import profil_actif

        profil = profil_actif(request)
        if _est_abonne(user, profil):
            profil_type = ABONNE
            demandeur = f"p:{profil.pk}" if profil is not None else f"c:{user.pk}"
        else:
            profil_type, demandeur = CONNECTE, f"c:{user.pk}"
    else:
        profil_type = VISITEUR
        visiteur = _lire_cookie(request)
        if visiteur:
            demandeur = f"v:{visiteur}"
        elif reseau is None:
            demandeur = "r:inconnu"
        elif _incrementer(jour, "identites", reseau) <= reglages.plafond_identites_reseau:
            visiteur = secrets.token_hex(12)
            demandeur, cookie = f"v:{visiteur}", signing.dumps(visiteur, salt=_SEL_COOKIE)
        else:
            # Trop de « nouveaux visiteurs » sur ce réseau aujourd'hui : plus de cookie, un quota commun.
            demandeur = f"r:{reseau}"

    ctx = Contexte(
        reglages=reglages, jour=jour, reinitialisation=reinitialisation, profil_type=profil_type, demandeur=demandeur,
        limite=reglages.quota_abonne if profil_type == ABONNE else reglages.quota_visiteur,
        reseau=reseau, reseau_large=reseau_large, cookie=cookie,
    )
    request._edk_quota = ctx
    return ctx


# --- Décision ------------------------------------------------------------------------------------------------------

class _Refus(Exception):
    def __init__(self, motif):
        self.motif = motif


class _DejaLivre(Exception):
    pass


@dataclass
class Decision:
    contexte: Contexte
    autorise: bool
    gratuit: bool = False  # déjà téléchargé aujourd'hui : aucun crédit consommé
    motif: str = ""
    utilise: int = 0
    restant: int = 0
    illimite: bool = False
    unite_id: int = None
    consommes: list = field(default_factory=list)

    def annuler(self):
        """Rend le crédit si la délivrance a échoué AVANT l'envoi."""
        if self.unite_id is None:
            return
        with transaction.atomic():
            TelechargementPdf.objects.filter(pk=self.unite_id).delete()
            for portee, cle in self.consommes:
                CompteurQuota.objects.filter(
                    jour=self.contexte.jour, portee=portee, cle=cle, nombre__gt=0,
                ).update(nombre=F("nombre") - 1)
        self.unite_id = None
        self.utilise = max(0, self.utilise - 1)
        self.restant += 1


def _decision_lecture(ctx, document=None):
    """État SANS effet de bord : ce que dirait `autoriser` maintenant."""
    if not ctx.reglages.actif:
        return Decision(ctx, True, gratuit=True, illimite=True)
    nombres = _nombres(ctx.jour, ctx.cles())
    utilise, restant, motif = ctx.marge(nombres)
    gratuit = bool(document) and TelechargementPdf.objects.filter(
        jour=ctx.jour, demandeur=ctx.demandeur, document=document,
    ).exists()
    return Decision(ctx, gratuit or restant > 0, gratuit=gratuit, motif="" if gratuit or restant > 0 else motif,
                    utilise=utilise, restant=restant)


def autoriser(request, document):
    """
    Décide, et consomme un crédit si le document n'a pas déjà été téléchargé aujourd'hui par ce demandeur.
    Un refus n'écrit qu'une statistique agrégée.
    """
    ctx = contexte(request)
    if not ctx.reglages.actif:
        return Decision(ctx, True, gratuit=True, illimite=True)

    cles = ctx.cles()
    plafonds = ctx.plafonds()
    consommes, unite = [], None
    try:
        with transaction.atomic():
            if TelechargementPdf.objects.filter(jour=ctx.jour, demandeur=ctx.demandeur, document=document).exists():
                raise _DejaLivre
            for portee, cle in cles:
                CompteurQuota.objects.get_or_create(jour=ctx.jour, portee=portee, cle=cle)
                pris = CompteurQuota.objects.filter(
                    jour=ctx.jour, portee=portee, cle=cle, nombre__lt=plafonds[(portee, cle)],
                ).update(nombre=F("nombre") + 1)
                if not pris:
                    raise _Refus({"demandeur": QUOTA_DEPASSE, "global_anonyme": BUDGET_GLOBAL}.get(portee, PLAFOND_RESEAU))
                consommes.append((portee, cle))
            try:
                with transaction.atomic():
                    unite = TelechargementPdf.objects.create(
                        jour=ctx.jour, demandeur=ctx.demandeur, type_demandeur=ctx.profil_type, document=document,
                    )
            except IntegrityError:
                # Une requête identique vient de créer l'unité : elle a payé pour les deux.
                raise _DejaLivre
    except _Refus as refus:
        _incrementer(ctx.jour, f"refus_{refus.motif}", ctx.profil_type)
        decision = _decision_lecture(ctx)
        decision.autorise, decision.motif = False, refus.motif
        return decision
    except _DejaLivre:
        decision = _decision_lecture(ctx, document)
        decision.autorise, decision.gratuit, decision.motif = True, True, ""
        return decision

    decision = _decision_lecture(ctx)
    decision.autorise, decision.motif, decision.unite_id, decision.consommes = True, "", unite.pk, consommes
    if decision.utilise >= ctx.limite:
        _incrementer(ctx.jour, "quota_atteint", ctx.profil_type)
    return decision


# --- Réponses ------------------------------------------------------------------------------------------------------

def etat_json(ctx, decision=None, gratuits=()):
    decision = decision or _decision_lecture(ctx)
    return {
        "actif": ctx.reglages.actif,
        "profil": ctx.profil_type,
        "limite": ctx.limite,
        "utilise": decision.utilise,
        "restant": decision.restant,
        # Pourquoi il n'en reste plus (quota_depasse, plafond_reseau, budget_global), vide tant qu'il en reste.
        "motif": decision.motif if decision.restant == 0 and not decision.illimite else "",
        "reinitialisation": ctx.reinitialisation.isoformat(),
        "fuseau": ctx.reglages.fuseau,
        "gratuits": list(gratuits),
    }


def poser_cookie(request, response):
    """Pose le cookie du visiteur s'il vient d'être reconnu (à appeler sur TOUTE réponse d'une route de quota)."""
    ctx = getattr(request, "_edk_quota", None)
    if ctx is not None and ctx.cookie:
        response.set_cookie(
            COOKIE_VISITEUR, ctx.cookie, max_age=DUREE_COOKIE_S, httponly=True, samesite="Lax",
            secure=settings.SESSION_COOKIE_SECURE, path="/",
        )
        ctx.cookie = None
    return response


def en_tetes(request, response, decision=None):
    ctx = contexte(request)
    decision = decision or _decision_lecture(ctx)
    response["Cache-Control"] = "private, no-store"
    patch_vary_headers(response, ("Cookie", "Authorization"))
    if not decision.illimite:
        response["X-Quota-Limit"] = str(ctx.limite)
        response["X-Quota-Remaining"] = str(decision.restant)
        response["X-Quota-Reset"] = ctx.reinitialisation.isoformat()
    return poser_cookie(request, response)


def reponse_refus(request, decision):
    ctx = decision.contexte
    secondes = max(1, int((ctx.reinitialisation - timezone.now()).total_seconds()))
    message = TEXTES[decision.motif][_langue(request)].format(limite=ctx.limite)
    corps = {"error": message, "code": decision.motif, **etat_json(ctx, decision)}
    reponse = Response(corps, status=429, headers={"Retry-After": str(secondes)})
    return en_tetes(request, reponse, decision)


def verifier_credit(request, document):
    """Réponse 429 si ce demandeur n'a plus de crédit pour ce document, sinon None. Ne consomme rien : sert avant
    une génération coûteuse (voir access.views.download_cours_pdf)."""
    decision = _decision_lecture(contexte(request), document)
    if decision.autorise:
        return None
    _incrementer(decision.contexte.jour, f"refus_{decision.motif}", decision.contexte.profil_type)
    return reponse_refus(request, decision)


def livrer_pdf(request, document, ouvrir, **options):
    """
    Point de sortie UNIQUE d'un PDF protégé. Appelé APRÈS les contrôles d'accès propres à la route (un refus d'accès ne
    touche jamais au quota). `ouvrir()` renvoie le fichier ouvert ; `options` : as_attachment, filename.
    """
    if request.method == "HEAD":
        return Response(status=405, headers={"Allow": "GET"})
    decision = autoriser(request, document)
    if not decision.autorise:
        return reponse_refus(request, decision)
    try:
        fichier = ouvrir()
    except Exception:
        decision.annuler()
        raise
    reponse = FileResponse(fichier, content_type="application/pdf", **options)
    return en_tetes(request, reponse, decision)


# --- Documents -----------------------------------------------------------------------------------------------------

def cle_document(type_document, reference):
    """Clé stable d'un document pour les unités. `reference` : id (ou slug pour un cours)."""
    from catalog.models import Cours

    if type_document == "cours":
        cours = Cours.objects.visibles().par_slug_ou_id(str(reference)).first()
        return f"cours:{cours.pk}" if cours else None
    if type_document in {"lesson", "inedit"} and str(reference).isdigit():
        return f"{type_document}:{int(reference)}"
    if type_document in {"quiz", "fiche"}:
        identifiant, _, face = str(reference).partition(":")
        if identifiant.isdigit() and face in {"sujet", "corrige"}:
            return f"{type_document}:{int(identifiant)}:{face}"
    return None


class QuotaThrottle(SimpleRateThrottle):
    """Garde-fou de débit sur les routes de PDF et de statut : par compte, sinon par réseau. Très large - un réseau
    scolaire entier doit passer, et le client relance toutes les 2,5 s pendant qu'un PDF se prépare - car son seul but
    est d'écarter un robot qui martèle ; le vrai plafond est le quota. Compteur en mémoire de chaque processus."""

    scope = "pdf_quota"
    rate = "300/min"

    def allow_request(self, request, view):
        if not getattr(settings, "THROTTLE_PDF_ACTIF", True):
            return True
        return super().allow_request(request, view)

    def get_cache_key(self, request, view):
        ident = f"u{request.user.pk}" if request.user.is_authenticated else _reseaux(_ip_cliente(request))[0] or "inconnu"
        return self.cache_format % {"scope": self.scope, "ident": ident}


class LectureThrottle(QuotaThrottle):
    """Contenu HTML/JSON (lecture en ligne) : non décompté, seulement un plafond de débit très large pour écarter les
    aspirateurs. Un réseau scolaire entier doit passer : 600 requêtes par minute et par réseau."""

    scope = "lecture_contenu"
    rate = "600/min"
