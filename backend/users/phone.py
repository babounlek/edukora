"""
Frontière unique de normalisation des numéros de téléphone.

Historique : tout le projet stockait le numéro au format local camerounais à 9
chiffres (`677123456`), et chaque intégration réajoutait l'indicatif à la main
(`f"237{phone_number}"` dans payments.campay_client et whatsapp.backends). Ce
choix rendait `users.User` structurellement mono-pays alors que le catalogue est
multi-pays (voir catalog.Country.dial_code).

Le stockage canonique est désormais l'E.164 (`+237677123456`) sur users.User et
users.OTPCode. Les deux helpers ci-dessous sont les seuls endroits qui savent
convertir : `to_e164` à l'entrée (API, admin, imports), `to_msisdn` à la sortie
vers un fournisseur qui refuse le `+` (CamPay, WhatsApp Graph API).

Volontairement sans dépendance à `phonenumbers` : la validation ici est
structurelle (E.164 bien formé), pas une validation d'attribution réelle de
numéro. Un opérateur qui refuse le numéro reste la source de vérité finale.
"""

import re

from django.conf import settings
from django.core.exceptions import ValidationError

# E.164 : '+', un indicatif ne commençant jamais par 0, 15 chiffres au maximum
# (norme UIT-T E.164), 8 au minimum - en dessous, aucun numéro mobile national
# des pays visés n'est valide.
E164_REGEX = re.compile(r"^\+[1-9]\d{7,14}$")


def _default_dial_code():
    """
    Indicatif appliqué à un numéro saisi au format local, sans indicatif. Reste le
    Cameroun par défaut : c'est le seul pays réellement ouvert aux inscriptions, et
    un numéro local saisi sans contexte y appartient. Devra devenir un choix
    explicite (indicatif du Country visé) le jour où un second pays ouvre.
    """
    return str(getattr(settings, "DEFAULT_DIAL_CODE", "237")).lstrip("+")


def to_e164(raw, dial_code=None):
    """
    Normalise une saisie en E.164. Accepte les trois formes qui circulent réellement
    dans le projet, pour qu'aucun appelant existant n'ait à changer de contrat :

        "677123456"      -> "+237677123456"   (format local historique)
        "237677123456"   -> "+237677123456"   (format opérateur, sans '+')
        "+237677123456"  -> "+237677123456"   (déjà canonique, inchangé)

    Les séparateurs de confort (espaces, points, tirets, parenthèses) sont retirés.
    Lève ValidationError si le résultat n'est pas un E.164 structurellement valide -
    jamais de retour silencieux d'une valeur douteuse, qui finirait stockée telle
    quelle et ferait échouer l'envoi du SMS bien plus loin dans la chaîne.
    """
    if raw is None:
        return None

    cleaned = re.sub(r"[\s.\-()]", "", str(raw))
    if not cleaned:
        return None

    dial = str(dial_code).lstrip("+") if dial_code else _default_dial_code()

    if cleaned.startswith("+"):
        candidate = cleaned
    elif cleaned.startswith(dial) and len(cleaned) > len(dial):
        # Numéro déjà préfixé de son indicatif mais sans le '+' : forme renvoyée par
        # CamPay et l'API Graph. Le test de longueur évite de confondre l'indicatif
        # avec le début d'un numéro local qui commencerait par les mêmes chiffres.
        candidate = f"+{cleaned}"
    else:
        candidate = f"+{dial}{cleaned.lstrip('0')}"

    if not E164_REGEX.match(candidate):
        raise ValidationError(f"Numéro de téléphone invalide : {raw!r}")
    return candidate


def to_msisdn(e164):
    """
    Format attendu par les fournisseurs qui refusent le '+' (CamPay, WhatsApp Graph
    API) : les chiffres seuls, indicatif compris. Tolère une entrée déjà au format
    local historique, le temps que toutes les données stockées soient migrées.
    """
    if not e164:
        return ""
    return to_e164(e164).lstrip("+")


def to_local(e164, dial_code=None):
    """
    Retire l'indicatif, pour l'affichage et pour les comparaisons avec des données
    historiques encore stockées au format local. Retourne l'entrée inchangée si elle
    ne porte pas l'indicatif attendu - un numéro étranger n'a pas de forme locale
    signifiante ici.
    """
    if not e164:
        return ""
    dial = str(dial_code).lstrip("+") if dial_code else _default_dial_code()
    digits = to_msisdn(e164)
    if digits.startswith(dial):
        return digits[len(dial):]
    return digits
