"""
Charge les articles du centre d'aide depuis aide/articles/ vers la base.

Un article = un fichier français `<slug>.md` et, s'il est traduit, un fichier `<slug>.en.md` :

    ---
    categorie: paiement          (français seulement : demarrer, connexion, paiement, utiliser, parents, autres)
    ordre: 10                    (français seulement)
    populaire: oui               (français seulement)
    pages: /connexion,/tarifs    (français seulement)
    titre: ...
    resume: ...
    mots_cles: mot, autre mot
    ---
    Le corps en Markdown.

Idempotent. Un article créé ou mis à jour ici reste « non modifié à la main » ; un article corrigé dans l'admin
est SAUTÉ (et listé) pour ne pas écraser le travail de l'équipe, sauf avec --forcer.

    python manage.py charger_aide            # crée les manquants, met à jour ceux jamais retouchés
    python manage.py charger_aide --a-blanc  # montre ce qui changerait, n'écrit rien
    python manage.py charger_aide --forcer   # réécrit aussi les articles retouchés à la main
"""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from aide.models import ArticleAide, CategorieAide

DOSSIER = Path(__file__).resolve().parents[2] / "articles"
_VRAI = {"oui", "true", "1", "vrai", "yes"}


def lire_fichier(chemin):
    """(entetes, corps) d'un fichier d'article. Lève CommandError si l'en-tête est absent ou mal fermé."""
    texte = chemin.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not texte.startswith("---\n"):
        raise CommandError(f"{chemin.name} : l'en-tête '---' manque en première ligne.")
    fin = texte.find("\n---\n", 4)
    if fin == -1:
        raise CommandError(f"{chemin.name} : l'en-tête n'est pas refermé par '---'.")
    entetes = {}
    for ligne in texte[4:fin].split("\n"):
        if not ligne.strip():
            continue
        cle, separateur, valeur = ligne.partition(":")
        if not separateur:
            raise CommandError(f"{chemin.name} : ligne d'en-tête sans ':' -> {ligne!r}")
        entetes[cle.strip()] = valeur.strip()
    return entetes, texte[fin + 5 :].strip()


def lire_articles():
    """{slug: {"fr": (entetes, corps), "en": (entetes, corps) ou None}} pour tout le dossier."""
    articles = {}
    for chemin in sorted(DOSSIER.glob("*.md")):
        nom = chemin.stem
        langue = "en" if nom.endswith(".en") else "fr"
        slug = nom[:-3] if langue == "en" else nom
        articles.setdefault(slug, {"fr": None, "en": None})[langue] = lire_fichier(chemin)
    for slug, versions in articles.items():
        if versions["fr"] is None:
            raise CommandError(f"{slug}.en.md n'a pas de version française {slug}.md.")
    return articles


def champs_depuis(slug, versions):
    entetes, corps = versions["fr"]
    categorie = entetes.get("categorie", "")
    if categorie not in CategorieAide.values:
        raise CommandError(f"{slug}.md : catégorie {categorie!r} inconnue. Attendu : {CategorieAide.values}.")
    for obligatoire in ("titre", "resume"):
        if not entetes.get(obligatoire):
            raise CommandError(f"{slug}.md : '{obligatoire}' manque dans l'en-tête.")
    champs = {
        "categorie": categorie,
        "ordre": int(entetes.get("ordre", 100)),
        "populaire": entetes.get("populaire", "").lower() in _VRAI,
        "pages_liees": entetes.get("pages", ""),
        "titre_fr": entetes["titre"],
        "resume_fr": entetes["resume"],
        "corps_fr": corps,
        "mots_cles_fr": entetes.get("mots_cles", ""),
        "titre_en": "",
        "resume_en": "",
        "corps_en": "",
        "mots_cles_en": "",
    }
    if versions["en"]:
        entetes_en, corps_en = versions["en"]
        if not (entetes_en.get("titre") and entetes_en.get("resume") and corps_en):
            raise CommandError(f"{slug}.en.md : titre, résumé et corps sont tous requis (sinon supprime le fichier).")
        champs.update(
            titre_en=entetes_en["titre"],
            resume_en=entetes_en["resume"],
            corps_en=corps_en,
            mots_cles_en=entetes_en.get("mots_cles", ""),
        )
    return champs


class Command(BaseCommand):
    help = "Charge les articles du centre d'aide depuis aide/articles/ (idempotent, n'écrase pas les retouches de l'admin)."

    def add_arguments(self, parser):
        parser.add_argument("--a-blanc", action="store_true", help="Ne rien écrire : seulement dire ce qui changerait.")
        parser.add_argument("--forcer", action="store_true", help="Réécrire aussi les articles retouchés à la main dans l'admin.")

    def handle(self, *args, **options):
        a_blanc, forcer = options["a_blanc"], options["forcer"]
        crees = misajour = inchanges = sautes = 0
        for slug, versions in lire_articles().items():
            champs = champs_depuis(slug, versions)
            existant = ArticleAide.objects.filter(slug=slug).first()
            if existant is None:
                crees += 1
                self.stdout.write(f"+ {slug}")
                if not a_blanc:
                    ArticleAide.objects.create(slug=slug, **champs)
                continue
            if existant.modifie_a_la_main and not forcer:
                sautes += 1
                self.stdout.write(self.style.WARNING(f"~ {slug} : retouché à la main, laissé tel quel (--forcer pour réécrire)"))
                continue
            if all(getattr(existant, nom) == valeur for nom, valeur in champs.items()):
                inchanges += 1
                continue
            misajour += 1
            self.stdout.write(f"* {slug}")
            if not a_blanc:
                for nom, valeur in champs.items():
                    setattr(existant, nom, valeur)
                existant.modifie_a_la_main = False
                existant.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"{'À blanc : ' if a_blanc else ''}{crees} créé(s), {misajour} mis à jour, {inchanges} inchangé(s), {sautes} laissé(s) à l'admin."
            )
        )
