"""
Le centre d'aide sert-il ? Lecture des trois événements `aide_*` (article lu, utile oui/non, contact WhatsApp
ouvert) et des recherches sans résultat de l'aide, article par article.

C'est la liste de ce qu'il faut réécrire : un article lu souvent mais jugé inutile, ou après lequel on écrit
quand même au support, n'a pas répondu. Aucune donnée personnelle ici : les événements ne portent que le slug de
l'article, la rubrique et le oui/non (voir analytics.models.EventName), jamais le texte d'une recherche.
"""
from collections import Counter
from datetime import timedelta

from django.utils import timezone

from analytics.models import AnalyticsEvent, EventName

from .models import ArticleAide

# Sous ces effectifs, un pourcentage ne dit rien : on ne signale pas un article sur trois avis.
MIN_AVIS = 5
MIN_VUES = 10
SEUIL_UTILE = 60.0  # % d'avis « oui » en dessous duquel on signale
SEUIL_CONTACT = 20.0  # % de lectures suivies d'un clic vers WhatsApp au-dessus duquel on signale


def _pourcentage(partie, total):
    return round(100 * partie / total, 1) if total else None


def _compter(nom, jours):
    depuis = timezone.now() - timedelta(days=jours)
    return AnalyticsEvent.objects.filter(name=nom, created_at__gte=depuis).values_list("properties", flat=True)


def rapport_aide(jours=30):
    vues, oui, non, contacts = Counter(), Counter(), Counter(), Counter()
    for props in _compter(EventName.AIDE_ARTICLE_VU, jours):
        vues[(props or {}).get("slug")] += 1
    for props in _compter(EventName.AIDE_ARTICLE_UTILE, jours):
        props = props or {}
        (oui if props.get("utile") else non)[props.get("slug")] += 1
    contacts_hors_article = 0
    for props in _compter(EventName.AIDE_CONTACT_CLIC, jours):
        slug = (props or {}).get("slug")
        if slug:
            contacts[slug] += 1
        else:
            contacts_hors_article += 1
    sans_resultat = sum(1 for props in _compter(EventName.SEARCH_NO_RESULTS, jours) if (props or {}).get("source") == "aide")

    lignes = []
    for article in ArticleAide.objects.filter(publie=True):
        s = article.slug
        avis = oui[s] + non[s]
        taux_utile = _pourcentage(oui[s], avis)
        taux_contact = _pourcentage(contacts[s], vues[s])
        a_reecrire = []
        if avis >= MIN_AVIS and taux_utile is not None and taux_utile < SEUIL_UTILE:
            a_reecrire.append("jugé peu utile")
        if vues[s] >= MIN_VUES and taux_contact is not None and taux_contact > SEUIL_CONTACT:
            a_reecrire.append("souvent suivi d'un message au support")
        lignes.append({
            "slug": s,
            "titre": article.titre_fr,
            "categorie": article.get_categorie_display(),
            "vues": vues[s],
            "oui": oui[s],
            "non": non[s],
            "taux_utile": taux_utile,
            "contacts": contacts[s],
            "taux_contact": taux_contact,
            "a_reecrire": a_reecrire,
        })
    # Les plus lus d'abord : c'est là que se joue l'essentiel du support évité.
    lignes.sort(key=lambda ligne: (-ligne["vues"], ligne["slug"]))
    return {
        "jours": jours,
        "articles": lignes,
        "total_vues": sum(vues.values()),
        "total_contacts": sum(contacts.values()) + contacts_hors_article,
        "contacts_hors_article": contacts_hors_article,
        "recherches_sans_resultat": sans_resultat,
        "jamais_lus": [ligne["slug"] for ligne in lignes if ligne["vues"] == 0],
        "a_reecrire": [ligne for ligne in lignes if ligne["a_reecrire"]],
    }


def rendre_texte(rapport):
    """Le rapport en texte, pour la commande `rapport_aide`."""

    def pct(valeur):
        return "-" if valeur is None else f"{valeur:g} %"

    sortie = [
        f"Centre d'aide - {rapport['jours']} derniers jours",
        f"{rapport['total_vues']} lectures, {rapport['total_contacts']} clics vers le support, "
        f"{rapport['recherches_sans_resultat']} recherches sans résultat.",
        "",
        f"{'article':42} {'lu':>5} {'oui':>4} {'non':>4} {'utile':>8} {'contact':>8}",
    ]
    for ligne in rapport["articles"]:
        sortie.append(
            f"{ligne['slug'][:42]:42} {ligne['vues']:>5} {ligne['oui']:>4} {ligne['non']:>4} "
            f"{pct(ligne['taux_utile']):>8} {pct(ligne['taux_contact']):>8}"
        )
    if rapport["a_reecrire"]:
        sortie += ["", "À réécrire en priorité :"]
        sortie += [f"- {ligne['slug']} ({', '.join(ligne['a_reecrire'])})" for ligne in rapport["a_reecrire"]]
    if rapport["jamais_lus"]:
        sortie += ["", f"Jamais lus sur la période : {', '.join(rapport['jamais_lus'])}"]
    return "\n".join(sortie)
