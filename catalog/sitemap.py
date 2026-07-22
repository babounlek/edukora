from django.conf import settings
from django.http import Http404, HttpResponse

from .models import Cours, Lesson, StatutContenu

# django.contrib.sitemaps résout le domaine via request.get_host() ou le framework
# Sites - les deux donneraient le domaine de CETTE API, pas celui du frontend où les
# pages sont réellement consultables. On construit donc le XML à la main avec
# settings.FRONTEND_URL plutôt que de lutter contre ces hypothèses. Ça suppose qu'en
# production, /sitemap.xml et /sitemap-N.xml sur le domaine du frontend sont routés
# (reverse proxy) vers cette API - à mettre en place au moment du déploiement.

# Plafond volontairement plus bas que la limite du protocole (50 000 URLs/fichier) :
# des fichiers plus petits sont re-crawlés plus vite et restent simples à déboguer.
# /sitemap.xml sert toujours un sitemap index qui pointe vers un ou plusieurs
# /sitemap-N.xml d'au plus MAX_URLS_PER_SITEMAP chacun - même à un seul fichier
# aujourd'hui, cette structure absorbe la croissance du catalogue sans changement
# d'URL ni de format plus tard.
MAX_URLS_PER_SITEMAP = 1000

_STATIC_PAGES = [
    ("", "1.0", "daily"),
    ("/cours", "0.8", "daily"),
    ("/tarifs", "0.5", "weekly"),
    ("/cgu", "0.3", "monthly"),
    ("/confidentialite", "0.3", "monthly"),
]


def _url_entry(loc, lastmod=None, priority="0.5", changefreq="weekly"):
    lastmod_tag = f"<lastmod>{lastmod.date().isoformat()}</lastmod>" if lastmod else ""
    return (
        f"<url><loc>{loc}</loc>{lastmod_tag}"
        f"<changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>"
    )


def _all_entries():
    """Reconstruite à chaque appel depuis la base VALIDE - jamais de cache, jamais de
    fichier à régénérer manuellement : le sitemap est donc toujours à jour."""
    base = settings.FRONTEND_URL
    entries = [
        _url_entry(f"{base}{path}", priority=priority, changefreq=changefreq)
        for path, priority, changefreq in _STATIC_PAGES
    ]

    for lesson in Lesson.objects.filter(statut=StatutContenu.VALIDE).only("id", "updated_at"):
        entries.append(_url_entry(f"{base}/lecons/{lesson.id}", lastmod=lesson.updated_at, priority="0.7"))

    for cours in Cours.objects.filter(statut=StatutContenu.VALIDE).only("id", "updated_at"):
        entries.append(_url_entry(f"{base}/cours/{cours.id}", lastmod=cours.updated_at, priority="0.7"))

    return entries


def _chunks(entries):
    chunks = [entries[i:i + MAX_URLS_PER_SITEMAP] for i in range(0, len(entries), MAX_URLS_PER_SITEMAP)]
    return chunks or [[]]


def sitemap_index(request):
    chunk_count = len(_chunks(_all_entries()))
    base = settings.FRONTEND_URL
    sitemaps = "".join(f"<sitemap><loc>{base}/sitemap-{i + 1}.xml</loc></sitemap>" for i in range(chunk_count))
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + sitemaps
        + "</sitemapindex>"
    )
    return HttpResponse(xml, content_type="application/xml")


def sitemap_chunk(request, page):
    chunks = _chunks(_all_entries())
    index = page - 1
    if index < 0 or index >= len(chunks):
        raise Http404("Sitemap introuvable.")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(chunks[index])
        + "</urlset>"
    )
    return HttpResponse(xml, content_type="application/xml")
