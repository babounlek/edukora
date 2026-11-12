"""Pages d'atterrissage par examen : `/cm/examens/bepc`, `/cm/examens/bac-d`, `/en/cm/exams/gce-o-level`.

Une page par cursus (examen + série) qui porte au moins une épreuve publiée. Avant elles, le filtre `?cursus=14` de
la liste des épreuves était ramené par canonical à `/cm/epreuves` : « annales BEPC Cameroun » ou « BAC D annales
corrigées » n'avaient aucune page à indexer (audit du 2026-11-12, SEO-02).

Tout est CALCULÉ depuis la base (chiffres, années, matières, liste des épreuves récentes) : il n'y a aucun texte à
rédiger par cursus, seulement les gabarits de phrases ci-dessous. Et rien de payant n'y paraît : des titres, des
chiffres et l'indication « corrigé en accès libre » (Lesson.est_vitrine), jamais un corrigé.

Ce module sert quatre consommateurs, pour qu'ils ne divergent pas : l'API (`ExamenPageView`), le prérendu des moteurs
(`prerendu._page_examen`), l'aperçu de partage (`apercu_partage._infos_examen`) et le sitemap.
"""
from django.db.models import Count, Max, Min
from django.utils.text import slugify

from .models import Cours, Cursus, Langue, Lesson, StatutContenu

NB_EPREUVES_LISTEES = 30

TEXTES = {
    "fr": {
        "titre": "Annales {libelle} corrigées au Cameroun",
        "description": (
            "{epreuves} annales {libelle} au Cameroun{annees}, avec corrigés détaillés : {libres} en accès libre. "
            "Sujets, cours et quiz."
        ),
        "intro": (
            "EduKora réunit {epreuves} épreuves du {libelle} au Cameroun{annees}, dans {matieres} matières{cours}. "
            "Les sujets sont toujours consultables gratuitement ; le corrigé "
            "détaillé est en accès libre pour {libres} d'entre elles et s'ouvre avec l'abonnement pour les autres. "
            "Chaque jour, une séance de 25 minutes cible les thèmes qui tombent le plus à cet examen."
        ),
        "recentes": "Épreuves récentes",
        "matieres_titre": "Matières couvertes",
        "n_epreuves": "{n} épreuves",
        "libre": "corrigé en accès libre",
        "sujet_libre": "sujet libre",
        "annees": " ({debut} à {fin})",
        "annee_unique": " ({annee})",
        "plus_de": "plus de {n}",
        "cours": ", avec {n} cours et fiches de méthode rattachés à cet examen",
    },
    "en": {
        "titre": "{libelle} past papers with solutions in Cameroon",
        "description": (
            "{epreuves} {libelle} past papers in Cameroon{annees}, with detailed solutions: {libres} free to read. "
            "Papers, lessons and quizzes."
        ),
        "intro": (
            "EduKora gathers {epreuves} {libelle} papers from Cameroon{annees}, across {matieres} subjects{cours}. "
            "The papers are always free to read; the detailed solution is free "
            "for {libres} of them and opens with a subscription for the others. Every day, a 25-minute session "
            "targets the topics that come up most in this exam."
        ),
        "recentes": "Recent papers",
        "matieres_titre": "Subjects covered",
        "n_epreuves": "{n} papers",
        "libre": "free solution",
        "sujet_libre": "free paper",
        "annees": " ({debut} to {fin})",
        "annee_unique": " ({annee})",
        "plus_de": "over {n}",
        "cours": ", with {n} lessons and method sheets linked to this exam",
    },
}


def libelle_examen(cursus):
    """« BEPC », « BAC D », « GCE O Level » : l'examen et, s'il y en a une, la série."""
    examen = cursus.display_examen()
    return f"{examen} {cursus.series.code}" if cursus.series_id else examen


def slug_depuis(examen_affiche, code_serie=None):
    """Le segment d'URL d'un examen (et de sa série) : `bepc`, `probatoire-c`, `bac-ti`, `gce-o-level`."""
    base = slugify(examen_affiche)
    return f"{base}-{slugify(code_serie)}" if code_serie else base


def slug_cursus(cursus):
    return slug_depuis(cursus.display_examen(), cursus.series.code if cursus.series_id else None)


def _lessons(cursus):
    return Lesson.objects.visibles().filter(cursus=cursus)


def cursus_avec_epreuves(code_pays):
    """[(cursus, nombre d'épreuves publiées)] du pays, seulement ceux qui en ont : pas de page vide à indexer."""
    cursus_du_pays = (
        Cursus.objects.select_related("series", "country")
        .filter(country__code__iexact=code_pays, country__actif=True)
        .order_by("id")
    )
    resultat = []
    for cursus in cursus_du_pays:
        n = _lessons(cursus).distinct().count()
        if n:
            resultat.append((cursus, n))
    return resultat


def _arrondi(n, langue):
    """« plus de 240 » plutôt que « 247 » : un total partagé entre cursus ne doit pas promettre trop."""
    return TEXTES[langue]["plus_de"].format(n=n // 10 * 10) if n >= 20 else str(n)


def donnees_examen(code_pays, slug):
    """Tout ce qu'affiche la page d'un examen, ou None s'il n'existe pas (ou n'a aucune épreuve publiée)."""
    cursus = next((c for c, _ in cursus_avec_epreuves(code_pays) if slug_cursus(c) == slug), None)
    if cursus is None:
        return None
    lessons = _lessons(cursus).distinct()
    bornes = lessons.aggregate(debut=Min("year"), fin=Max("year"))
    recentes = (
        lessons.select_related("subject").order_by("-year", "title")[:NB_EPREUVES_LISTEES]
    )
    return {
        "slug": slug,
        "country": cursus.country.code.lower(),
        "cursus_id": cursus.id,
        "libelle": libelle_examen(cursus),
        "examen_display": cursus.display_examen(),
        "langue": cursus.langue,
        "nb_epreuves": lessons.count(),
        "nb_epreuves_libres": lessons.filter(est_vitrine=True).count(),
        "nb_cours": Cours.objects.filter(cursus=cursus, statut=StatutContenu.VALIDE).count(),
        "nb_matieres": lessons.values("subject").distinct().count(),
        "matieres": [
            {"label": ligne["subject__label"], "n": ligne["n"]}
            for ligne in lessons.values("subject__label").annotate(n=Count("id", distinct=True)).order_by("-n", "subject__label")
        ],
        "annee_min": bornes["debut"],
        "annee_max": bornes["fin"],
        "epreuves": [
            {
                "slug": lesson.slug,
                "title": lesson.title,
                "year": lesson.year,
                "matiere": lesson.subject.label,
                "libre": lesson.est_vitrine,
            }
            for lesson in recentes
        ],
    }


def _annees(donnees, textes):
    debut, fin = donnees["annee_min"], donnees["annee_max"]
    if not debut:
        return ""
    if debut == fin:
        return textes["annee_unique"].format(annee=debut)
    return textes["annees"].format(debut=debut, fin=fin)


def textes_page(donnees, langue):
    """Le titre, la description et l'introduction de la page, dans la langue du contenu (`fr` ou `en`)."""
    textes = TEXTES[langue]
    valeurs = {
        "libelle": donnees["libelle"],
        "epreuves": _arrondi(donnees["nb_epreuves"], langue),
        "libres": donnees["nb_epreuves_libres"],
        # Beaucoup de cours ne sont rattachés à aucun examen : sans cours rattaché, la phrase n'en parle pas.
        "cours": textes["cours"].format(n=_arrondi(donnees["nb_cours"], langue)) if donnees["nb_cours"] else "",
        "matieres": donnees["nb_matieres"],
        "annees": _annees(donnees, textes),
    }
    description = textes["description"].format(**valeurs)
    return {
        "titre": textes["titre"].format(**valeurs),
        # « plus de 240 annales... » : une phrase commence par une majuscule.
        "description": description[:1].upper() + description[1:],
        "intro": textes["intro"].format(**valeurs),
    }


def langue_du_contenu(donnees):
    return "en" if donnees["langue"] == Langue.EN else "fr"


def corps_markdown(donnees, langue, chemin_epreuve):
    """Le texte de la page pour un robot : l'introduction, puis les épreuves récentes par matière, avec un lien vers
    chacune. `chemin_epreuve(slug)` donne l'adresse publique de la fiche d'une épreuve."""
    textes = TEXTES[langue]
    lignes = [textes_page(donnees, langue)["intro"], "", f"## {textes['matieres_titre']}", ""]
    lignes += [f"- {m['label']} : {textes['n_epreuves'].format(n=m['n'])}" for m in donnees["matieres"]]
    lignes += ["", f"## {textes['recentes']}"]
    par_matiere = {}
    for epreuve in donnees["epreuves"]:
        par_matiere.setdefault(epreuve["matiere"], []).append(epreuve)
    for matiere, epreuves in par_matiere.items():
        lignes += ["", f"### {matiere}", ""]
        for e in epreuves:
            etat = textes["libre"] if e["libre"] else textes["sujet_libre"]
            lignes.append(f"- [{e['title']}]({chemin_epreuve(e['slug'])}) - {etat}")
    return "\n".join(lignes)
