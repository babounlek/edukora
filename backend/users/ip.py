"""
Adresse IP réelle du demandeur - une seule lecture pour tout le projet (plafonds des codes de
connexion, comptes invités, quota de PDF, signal de fraude des revendeurs).
"""

from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address


def _valide(candidate):
    if not candidate:
        return None
    try:
        validate_ipv46_address(candidate)
    except ValidationError:
        return None
    return candidate


def client_ip(request):
    """
    IP réelle du demandeur.

    REMOTE_ADDR ne sert à rien en production : derrière Caddy (voir docker/caddy/Caddyfile),
    Django ne voit jamais que l'IP du conteneur reverse proxy, identique pour tout le monde.

    Première source : l'en-tête X-Client-IP, que Caddy ÉCRASE sur chaque requête avec l'adresse
    qu'il tient pour celle du client (`request_header X-Client-IP {client_ip}`). Derrière
    Cloudflare, déclaré proxy de confiance dans le Caddyfile, c'est l'adresse de l'élève
    (CF-Connecting-IP) et non celle du nœud Cloudflare - sans quoi tous les élèves sortant du
    même nœud partageraient les plafonds par adresse. Un client ne peut pas forger cet en-tête :
    Caddy remplace toujours la valeur reçue.

    Repli (serveur de développement, Caddyfile d'avant cet en-tête) : X-Forwarded-For, mais
    l'entrée la plus à DROITE, pas la première - Caddy AJOUTE l'IP du pair qu'il constate à la
    valeur éventuellement déjà présente. Les entrées de gauche sont fournies par le client,
    librement falsifiables ; la dernière est écrite par notre propre proxy.

    Retourne None plutôt qu'une valeur douteuse si rien d'exploitable n'est trouvé : les
    appelants savent traiter ce cas (le plafond par IP est sauté, le plafond global couvre
    toujours), là où une chaîne non validée ferait échouer l'écriture en base
    (GenericIPAddressField = type `inet` côté PostgreSQL) et transformerait un en-tête malformé
    en erreur 500.
    """
    declaree = _valide(request.META.get("HTTP_X_CLIENT_IP", "").strip())
    if declaree:
        return declaree
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    candidate = forwarded.split(",")[-1].strip() if forwarded else request.META.get("REMOTE_ADDR", "")
    return _valide(candidate)
