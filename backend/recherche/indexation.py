"""
Construction de l'index de recherche globale (EntreeRecherche) depuis les vrais modèles.

Reconstruction COMPLÈTE par type, dans une transaction : l'index n'est jamais une source de
vérité, on peut le jeter et le refaire. Une reconstruction par signal à chaque save() serait
fausse ici - l'ingestion pose les relations M2M (cursus, thèmes) APRÈS le save() de l'objet,
un signal verrait donc des contenus à moitié construits - et très lente pendant une campagne
d'ingestion de plusieurs centaines de fichiers. D'où la commande `indexer_recherche`, à lancer
après un lot (voir recherche.management.commands.indexer_recherche).

Seul du contenu PUBLIC est indexé (voir EntreeRecherche) : jamais un corrigé.
"""

from collections import Counter, defaultdict

from django.db import transaction
from django.db.models import Prefetch

from catalog.models import (
    Cours, Cursus, Exercise, Lesson, LessonType, Origine, RappelDeMethode, StatutContenu, Subject, Tag,
    resolve_examen_label,
)
from inedit.models import EpreuveInedite, RappelDeMethodeInedite
from quiz.models import CompetenceItem

from . import texte
from .models import EntreeRecherche, TermeRecherche, TypeResultat


# Plafonds de taille : l'index sert à retrouver, pas à stocker. Un énoncé de problème
# dépasse facilement 6 000 caractères - les 2 000 premiers portent déjà ses mots-clés.
LIMITE_CLES = 700
LIMITE_TEXTE = {
    TypeResultat.COURS: 1800,
    TypeResultat.EPREUVE: 3500,
    TypeResultat.EXERCICE: 2500,
    TypeResultat.QUIZ: 1200,
}
LONGUEUR_APERCU = 170
TAILLE_LOT = 500
VOCABULAIRE_LONGUEUR_MIN = 4
VOCABULAIRE_LONGUEUR_MAX = 40

# Un thème n'a une page de résultat propre qu'à partir de ce volume de contenu : un thème qui ne
# mène qu'à UN cours ferait doublon avec ce cours dans les résultats.
THEME_MIN_CONTENUS = 2

VALIDE = StatutContenu.VALIDE


class _Contexte:
    """Données de référence partagées par tous les types, chargées une fois."""

    def __init__(self):
        self.matieres = {s.id: s for s in Subject.objects.select_related("country")}
        self.mots_matiere = {
            sid: texte.normaliser(f"{s.label} {s.code}") for sid, s in self.matieres.items()
        }
        # Mots d'un cursus qui entrent dans les clés d'un contenu : l'examen (et ses synonymes :
        # « baccalauréat », « brevet ») et le code de série. Le libellé de série est exclu EXPRÈS :
        # « Mathématiques et sciences physiques » (série C) ferait remonter toute la série C sur
        # la requête « maths », quelle que soit la matière du contenu.
        self.mots_cursus = {}
        for cursus in Cursus.objects.select_related("country", "series"):
            mots = [
                resolve_examen_label(cursus.country, cursus.examen),
                texte.SYNONYMES_EXAMEN.get(cursus.examen, ""),
                cursus.series.code if cursus.series_id else "",
            ]
            self.mots_cursus[cursus.id] = texte.normaliser(" ".join(mots))

    def cursus_mots(self, cursus_ids):
        return " ".join(self.mots_cursus.get(c, "") for c in cursus_ids)


def _jetons_plafonnes(chaine, limite):
    """Mots de `chaine` (déjà normalisée), dédupliqués, coupés à `limite` caractères pour ne
    jamais finir en milieu de mot."""
    sortie, taille = [], 1
    for jeton in dict.fromkeys(chaine.split()):
        if taille + len(jeton) + 1 > limite:
            break
        sortie.append(jeton)
        taille += len(jeton) + 1
    return " " + " ".join(sortie) + " "


def _cles(*morceaux):
    return _jetons_plafonnes(texte.normaliser(" ".join(str(m) for m in morceaux if m)), LIMITE_CLES)


def _texte_norm(type_, markdown):
    return _jetons_plafonnes(texte.normaliser(texte.nettoyer(markdown)), LIMITE_TEXTE[type_])


def _entree(
    type_, objet_id, *, matiere, titre, cles, cursus_ids=(), tous_cursus=False, markdown="",
    apercu_source="", annee=None, gratuit=False, meta=None, groupe="", poids=0,
):
    entree = EntreeRecherche(
        type=type_, objet_id=objet_id, pays_id=matiere.country_id, matiere_id=matiere.id,
        tous_cursus=tous_cursus, titre=titre[:255], titre_norm=texte.normaliser(titre)[:255], cles_norm=cles,
        texte_norm=_texte_norm(type_, markdown) if markdown and type_ in LIMITE_TEXTE else "",
        apercu=texte.apercu(apercu_source, LONGUEUR_APERCU)[:255] if apercu_source else "",
        annee=annee, est_gratuit=gratuit, meta=meta or {}, groupe=groupe, poids=poids,
    )
    return entree, sorted(set(cursus_ids))


def _lots(queryset):
    return queryset.iterator(chunk_size=TAILLE_LOT)


# --- Cours ---------------------------------------------------------------------------


def _cursus_cours():
    """
    ({cours_id: cursus effectifs ou None}, {cours_id: cursus d'ACCÈS}, {cours_id vitrine}).

    « Effectifs » = ceux auxquels le cours est PROPOSÉ, même règle que catalog.models.
    q_cours_du_cursus : ses cursus directs, ses cursus recommandés, et - seulement s'il n'en a
    aucun en propre - ceux des épreuves dont il est tiré. None = proposé à tout cursus (aucun
    cursus, aucune épreuve source). « D'accès » = les cursus directs seuls, ce que lit
    access.services.has_access (vide = n'importe quel abonnement actif suffit).
    """
    direct, recommandes, lignee = defaultdict(set), defaultdict(set), defaultdict(set)
    for cours_id, cursus_id in Cours.cursus.through.objects.values_list("cours_id", "cursus_id"):
        direct[cours_id].add(cursus_id)
    for cours_id, cursus_id in Cours.cursus_recommandes.through.objects.values_list("cours_id", "cursus_id"):
        recommandes[cours_id].add(cursus_id)
    sources = RappelDeMethode.objects.filter(cours__isnull=False).values_list("cours_id", "exercise__lesson__cursus")
    for cours_id, cursus_id in sources:
        lignee.setdefault(cours_id, set())  # une épreuve source existe, même sans cursus
        if cursus_id is not None:
            lignee[cours_id].add(cursus_id)
    sources_inedites = RappelDeMethodeInedite.objects.filter(cours__isnull=False).values_list(
        "cours_id", "exercice__epreuve__cursus",
    )
    for cours_id, cursus_id in sources_inedites:
        lignee.setdefault(cours_id, set())
        if cursus_id is not None:
            lignee[cours_id].add(cursus_id)

    effectifs, acces = {}, {}
    for cours_id in Cours.objects.values_list("id", flat=True):
        propres = direct.get(cours_id, set())
        ensemble = set(propres) | recommandes.get(cours_id, set())
        if not propres:
            ensemble |= lignee.get(cours_id, set())
        effectifs[cours_id] = ensemble or None
        acces[cours_id] = propres
    vitrine = set(
        RappelDeMethode.objects.filter(cours__isnull=False, exercise__lesson__est_vitrine=True)
        .values_list("cours_id", flat=True).distinct(),
    )
    return effectifs, acces, vitrine


def texte_public_cours(sections):
    """
    Texte de l'aperçu PUBLIC d'un cours : accroche, prérequis, règle - mêmes sections que
    catalog.rendering.cours_preview_markdown (à garder alignées : indexer une section payante
    la ferait retrouver par ses mots). Lu directement dans `sections_raw` plutôt que via
    `Cours.preview_markdown()` : cette méthode résout chaque prérequis vers un autre cours par
    une requête SQL, soit ~25 ms par cours - 4 minutes pour les 10 000 cours du catalogue.
    """
    if not isinstance(sections, list):
        return ""
    morceaux = []
    for section in sections:
        if not isinstance(section, dict):
            continue
        genre = section.get("type")
        if genre == "accroche":
            morceaux.append(section.get("contenu_markdown") or "")
        elif genre == "prerequis":
            items = section.get("items") or section.get("items_markdown") or []
            morceaux.extend(item for item in items if isinstance(item, str))
        elif genre == "regle":
            morceaux.append(section.get("titre") or "")
            morceaux.append(section.get("contenu_markdown") or "")
            for variante in section.get("variantes") or []:
                if isinstance(variante, dict):
                    morceaux.append(variante.get("nom") or "")
                    morceaux.append(variante.get("contenu_markdown") or "")
    return "\n\n".join(m for m in morceaux if isinstance(m, str) and m)


def _entrees_cours(ctx, effectifs, acces, vitrine):
    queryset = Cours.objects.visibles().select_related("subject").prefetch_related("tags")
    for cours in _lots(queryset):
        apercu_public = texte_public_cours(cours.sections_raw)
        cursus_ids = effectifs.get(cours.id) or set()
        tags = [t.name for t in cours.tags.all()[:12]]
        yield _entree(
            TypeResultat.COURS, cours.id, matiere=cours.subject, titre=cours.titre,
            cles=_cles(cours.titre, cours.sous_theme, ctx.mots_matiere[cours.subject_id], *tags, ctx.cursus_mots(cursus_ids)),
            cursus_ids=cursus_ids, tous_cursus=effectifs.get(cours.id) is None, markdown=apercu_public,
            apercu_source=apercu_public, gratuit=cours.id in vitrine,
            meta={"slug": cours.slug, "sous_theme": cours.sous_theme, "acces_ids": sorted(acces.get(cours.id, ()))},
        )


# --- Épreuves (corrigés d'annales) et exercices ------------------------------------------


def _lesson_queryset():
    return Lesson.objects.visibles().select_related("subject").prefetch_related(
        "cursus", "themes",
        Prefetch("exercises", queryset=Exercise.objects.filter(statut=VALIDE).order_by("numero_exercice")),
    )


def _entrees_epreuves(ctx):
    for lesson in _lots(_lesson_queryset()):
        cursus_ids = [c.id for c in lesson.cursus.all()]
        exercices = list(lesson.exercises.all())
        # Le sujet est public (seul le corrigé est payant) : on indexe les énoncés. Une fiche ou
        # un sujet inédit sans Exercise n'a pas de séparation énoncé/corrigé et se lit tel quel.
        if exercices:
            public = "\n\n".join(e.enonce_intro_markdown + "\n" + e.enonce_markdown for e in exercices)
        else:
            public = lesson.content_markdown
        origine = "" if lesson.origine == Origine.OFFICIEL else lesson.get_origine_display()
        yield _entree(
            TypeResultat.EPREUVE, lesson.id, matiere=lesson.subject, titre=lesson.title,
            cles=_cles(
                lesson.title, ctx.mots_matiere[lesson.subject_id], ctx.cursus_mots(cursus_ids), lesson.year or "",
                origine, lesson.etablissement, lesson.institution, *[t.name for t in lesson.themes.all()[:15]],
            ),
            cursus_ids=cursus_ids, markdown=public, apercu_source=lesson.introduction_markdown or public,
            annee=lesson.year, gratuit=lesson.est_vitrine,
            meta={
                "slug": lesson.slug, "lesson_type": lesson.lesson_type, "acces_ids": sorted(cursus_ids),
                "type_libelle": LessonType(lesson.lesson_type).label,
            },
        )


def _libelle_exercice(numero):
    numero = str(numero or "").strip()
    return f"Exercice {numero}" if numero.isdigit() else (numero or "Exercice")


def _entrees_exercices(ctx):
    queryset = (
        Exercise.objects.filter(statut=VALIDE, lesson__statut=VALIDE, lesson__subject__country__actif=True)
        .select_related("lesson__subject").prefetch_related("lesson__cursus", "themes")
    )
    for exercice in _lots(queryset):
        lesson = exercice.lesson
        public = f"{exercice.enonce_intro_markdown}\n{exercice.enonce_markdown}".strip()
        if not public:
            continue
        cursus_ids = [c.id for c in lesson.cursus.all()]
        libelle = _libelle_exercice(exercice.numero_exercice)
        yield _entree(
            TypeResultat.EXERCICE, exercice.id, matiere=lesson.subject, titre=f"{libelle} · {lesson.title}",
            cles=_cles(
                libelle, lesson.title, ctx.mots_matiere[lesson.subject_id], ctx.cursus_mots(cursus_ids),
                lesson.year or "", *[t.name for t in exercice.themes.all()[:10]],
            ),
            cursus_ids=cursus_ids, markdown=public, apercu_source=public, annee=lesson.year, gratuit=lesson.est_vitrine,
            meta={
                "slug": lesson.slug, "numero": str(exercice.numero_exercice),
                "ancre": texte.ancre_exercice(exercice.numero_exercice), "libelle": libelle,
                "epreuve": lesson.title, "acces_ids": sorted(cursus_ids),
            },
        )


# --- Épreuves inédites -----------------------------------------------------------------


def _entrees_inedites(ctx):
    queryset = (
        EpreuveInedite.objects.filter(statut=VALIDE, subject__country__actif=True)
        .select_related("subject", "blueprint").prefetch_related("cursus", "blueprint__competences")
    )
    for epreuve in _lots(queryset):
        cursus_ids = [c.id for c in epreuve.cursus.all()]
        # Les énoncés d'une épreuve inédite sont un contenu payant (voir has_access_inedite) : on
        # n'indexe que son identité et les compétences visées par son plan.
        competences = [t.name for t in epreuve.blueprint.competences.all()[:15]]
        yield _entree(
            TypeResultat.INEDITE, epreuve.id, matiere=epreuve.subject, titre=epreuve.titre,
            cles=_cles(
                epreuve.titre, "inedite blanche", ctx.mots_matiere[epreuve.subject_id],
                ctx.cursus_mots(cursus_ids), *competences,
            ),
            cursus_ids=cursus_ids, gratuit=epreuve.est_gratuite,
            meta={"slug": epreuve.slug, "id": epreuve.id, "acces_ids": sorted(cursus_ids)},
        )


# --- Questions de quiz -----------------------------------------------------------------


def _entrees_quiz(ctx):
    queryset = (
        CompetenceItem.objects.filter(statut=VALIDE, subject__country__actif=True)
        .select_related("theme", "subject").prefetch_related("cursus")
    )
    for item in _lots(queryset):
        cursus_ids = [c.id for c in item.cursus.all()]
        yield _entree(
            TypeResultat.QUIZ, item.id, matiere=item.subject, titre=item.theme.name,
            cles=_cles(item.theme.name, ctx.mots_matiere[item.subject_id], ctx.cursus_mots(cursus_ids)),
            cursus_ids=cursus_ids, markdown=item.enonce_markdown, apercu_source=item.enonce_markdown,
            gratuit=item.est_vitrine, groupe=f"{item.theme_id}:{item.subject_id}",
            meta={"tag_id": item.theme_id, "subject_code": item.subject.code, "acces_ids": sorted(cursus_ids)},
        )


# --- Thèmes ----------------------------------------------------------------------------


def _entrees_themes(ctx, effectifs):
    """Une entrée par couple (thème, matière) ayant assez de contenu. Compte, pour chacun, les
    cours, questions de quiz et exercices qui le portent, et l'union des cursus concernés."""
    stats = defaultdict(lambda: {"cours": 0, "quiz": 0, "exercices": 0, "cursus": set(), "tous": False})

    cours_tags = Cours.tags.through.objects.filter(
        cours__statut=VALIDE, cours__subject__country__actif=True,
    ).values_list("cours_id", "tag_id", "cours__subject_id")
    for cours_id, tag_id, matiere_id in cours_tags:
        s = stats[(tag_id, matiere_id)]
        s["cours"] += 1
        cursus = effectifs.get(cours_id)
        if cursus is None:
            s["tous"] = True
        else:
            s["cursus"] |= cursus

    cursus_items = defaultdict(set)
    for item_id, cursus_id in CompetenceItem.cursus.through.objects.values_list("competenceitem_id", "cursus_id"):
        cursus_items[item_id].add(cursus_id)
    items = CompetenceItem.objects.filter(statut=VALIDE, subject__country__actif=True).values_list(
        "id", "theme_id", "subject_id",
    )
    for item_id, tag_id, matiere_id in items:
        s = stats[(tag_id, matiere_id)]
        s["quiz"] += 1
        s["cursus"] |= cursus_items.get(item_id, set())

    cursus_lessons = defaultdict(set)
    for lesson_id, cursus_id in Lesson.cursus.through.objects.values_list("lesson_id", "cursus_id"):
        cursus_lessons[lesson_id].add(cursus_id)
    exercices = Exercise.themes.through.objects.filter(
        exercise__statut=VALIDE, exercise__lesson__statut=VALIDE, exercise__lesson__subject__country__actif=True,
    ).values_list("exercise__lesson_id", "tag_id", "exercise__lesson__subject_id")
    for lesson_id, tag_id, matiere_id in exercices:
        s = stats[(tag_id, matiere_id)]
        s["exercices"] += 1
        s["cursus"] |= cursus_lessons.get(lesson_id, set())

    retenus = {
        cle: s for cle, s in stats.items()
        if s["quiz"] >= 1 or s["cours"] + s["exercices"] >= THEME_MIN_CONTENUS
    }
    tags = {t.id: t for t in Tag.objects.filter(id__in={tag_id for tag_id, _ in retenus})}
    for (tag_id, matiere_id), s in retenus.items():
        tag, matiere = tags[tag_id], ctx.matieres[matiere_id]
        # Le rattachement Tag -> programme officiel (Tag.savoir_officiel) n'est volontairement ni indexé
        # ni affiché : il est connu pour être peu fiable (« théorème de Thalès » pointait sur
        # « Orthogonalité dans l'espace »), et en faire un mot-clé ferait remonter ce thème sur des
        # requêtes qui n'ont rien à voir.
        yield _entree(
            TypeResultat.THEME, tag_id, matiere=matiere, titre=tag.name,
            cles=_cles(tag.name, ctx.mots_matiere[matiere_id], ctx.cursus_mots(s["cursus"])),
            cursus_ids=s["cursus"], tous_cursus=s["tous"] or not s["cursus"],
            groupe=f"{tag_id}:{matiere_id}", poids=s["cours"] + s["quiz"] + s["exercices"],
            meta={
                "tag_id": tag_id, "subject_code": matiere.code, "nb_cours": s["cours"], "nb_quiz": s["quiz"],
                "nb_exercices": s["exercices"],
            },
        )


# --- Orchestration ---------------------------------------------------------------------


def _remplacer(type_, paires):
    """Remplace tout le contenu d'un type, en une transaction : une recherche en cours ne voit
    jamais un type à moitié reconstruit."""
    with transaction.atomic():
        EntreeRecherche.objects.filter(type=type_).delete()
        EntreeRecherche.objects.bulk_create([entree for entree, _ in paires], batch_size=TAILLE_LOT)
        ids = {
            (objet_id, matiere_id): pk
            for pk, objet_id, matiere_id in EntreeRecherche.objects.filter(type=type_).values_list(
                "pk", "objet_id", "matiere_id",
            )
        }
        lien = EntreeRecherche.cursus.through
        lien.objects.bulk_create(
            [
                lien(entreerecherche_id=ids[(entree.objet_id, entree.matiere_id)], cursus_id=cursus_id)
                for entree, cursus_ids in paires for cursus_id in cursus_ids
            ],
            batch_size=1000,
        )
    return len(paires)


def _reconstruire_vocabulaire():
    """Mots du catalogue et leur fréquence (une fois par entrée) - pour « Vouliez-vous dire ? »."""
    compteur = Counter()
    for titre, cles in EntreeRecherche.objects.values_list("titre_norm", "cles_norm").iterator(chunk_size=2000):
        mots = set(titre.split()) | set(cles.split())
        compteur.update(
            m for m in mots
            if VOCABULAIRE_LONGUEUR_MIN <= len(m) <= VOCABULAIRE_LONGUEUR_MAX and not m.isdigit()
        )
    with transaction.atomic():
        TermeRecherche.objects.all().delete()
        TermeRecherche.objects.bulk_create(
            [TermeRecherche(terme=t, frequence=f) for t, f in compteur.items()], batch_size=2000,
        )
    return len(compteur)


TYPES_ORDRE = [
    TypeResultat.COURS, TypeResultat.EPREUVE, TypeResultat.EXERCICE, TypeResultat.INEDITE,
    TypeResultat.QUIZ, TypeResultat.THEME,
]


def reconstruire(types=None, ecrire=None):
    """Reconstruit l'index des `types` demandés (tous par défaut) puis le vocabulaire. Renvoie
    {type: nombre d'entrées, "termes": nombre de mots}."""
    voulus = {TypeResultat(t) for t in types} if types else set(TYPES_ORDRE)
    ctx = _Contexte()
    effectifs = acces = vitrine = None
    if voulus & {TypeResultat.COURS, TypeResultat.THEME}:
        effectifs, acces, vitrine = _cursus_cours()

    fabriques = {
        TypeResultat.COURS: lambda: _entrees_cours(ctx, effectifs, acces, vitrine),
        TypeResultat.EPREUVE: lambda: _entrees_epreuves(ctx),
        TypeResultat.EXERCICE: lambda: _entrees_exercices(ctx),
        TypeResultat.INEDITE: lambda: _entrees_inedites(ctx),
        TypeResultat.QUIZ: lambda: _entrees_quiz(ctx),
        TypeResultat.THEME: lambda: _entrees_themes(ctx, effectifs),
    }
    bilan = {}
    for type_ in TYPES_ORDRE:
        if type_ not in voulus:
            continue
        bilan[type_.value] = _remplacer(type_, list(fabriques[type_]()))
        if ecrire:
            ecrire(f"  {type_.label:<22} {bilan[type_.value]:>6}")
    bilan["termes"] = _reconstruire_vocabulaire()
    if ecrire:
        ecrire(f"  {'Vocabulaire':<22} {bilan['termes']:>6}")
    return bilan
