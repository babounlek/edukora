import csv
import re
import sys

from django.core.management.base import BaseCommand

from catalog.models import Exercise, Question

# Signaux forts qu'une sous-question DEMANDE un tracé (construction géométrique,
# courbe, schéma, graphique) - voir la section "Figures produites dans le corrigé"
# du SKILL.md de correction-experte, corrigée le 2026-08-26 pour rendre la
# production de l'image obligatoire dès qu'un de ces motifs apparaît dans l'énoncé.
_GEOM_NOUNS = (
    r"(point|figure|image|triangle|cercle|droite|segment|courbe|parall[ée]logramme|"
    r"m[ée]diatrice|bissectrice|sym[ée]trique|quadrilat[èe]re|losange|rectangle|"
    r"carr[ée]|vecteur|rep[èe]re|graphique|sch[ée]ma)"
)

_PATTERNS = {
    "tracer": re.compile(r"\btracer\b", re.IGNORECASE),
    "construire_geom": re.compile(
        rf"\bconstrui(?:re|sez|sons)\b.{{0,40}}\b{_GEOM_NOUNS}\b", re.IGNORECASE,
    ),
    "representer_graphiquement": re.compile(r"\brepr[ée]senter\s+graphiquement\b", re.IGNORECASE),
    "schematiser": re.compile(r"\bsch[ée]matis(?:er|ez|ons)\b", re.IGNORECASE),
    "faire_schema": re.compile(r"\b(?:faire|r[ée]aliser)\s+(?:un|une)\s+sch[ée]ma\b", re.IGNORECASE),
    "completer_figure": re.compile(r"\bcompl[ée]ter\s+(?:la|le)\s+(?:figure|sch[ée]ma)\b", re.IGNORECASE),
    "placer_points": re.compile(r"\bplacer\s+(?:le|les)\s+points?\b", re.IGNORECASE),
    "dessiner": re.compile(r"\bdessin(?:er|ez|ons)\b", re.IGNORECASE),
}

# `.*?` non-greedy, pas `[^\]]*` : une légende peut contenir un `]` (ex. notation
# d'intervalle ouvert "]0;pi[") qui ferait échouer un `[^\]]*` sur le premier `]`
# rencontré - voir la même correction dans catalog/models.py.
_IMAGE_PLACEHOLDER_RE = re.compile(r"!\[.*?\]\([^)]+\)")

# "construire/tracer le tableau de variations/de signes" reste en LaTeX par règle
# explicite du skill (jamais une image) - toute phrase qui mentionne "tableau" à
# proximité d'un verbe de tracé est exclue, quel que soit le motif déclenché.
_TABLEAU_RE = re.compile(r"\btableau\b", re.IGNORECASE)

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")


def _sentences_avec_demande(text):
    """Renvoie [(motif, phrase)] pour chaque phrase du texte qui demande un tracé,
    hors mentions de tableau (variations/signes, jamais concernées par cette règle)."""
    trouvailles = []
    for phrase in _SENTENCE_SPLIT_RE.split(text or ""):
        phrase = phrase.strip()
        if not phrase or _TABLEAU_RE.search(phrase):
            continue
        for label, pattern in _PATTERNS.items():
            if pattern.search(phrase):
                trouvailles.append((label, phrase))
                break
    return trouvailles


class Command(BaseCommand):
    help = (
        "Repère les sous-questions dont l'énoncé demande un tracé (construction "
        "géométrique, courbe, schéma, graphique) mais dont le corrigé de l'exercice "
        "ne contient aucune image (aucun placeholder ![fig-X](...)) - le défaut "
        "signalé par l'utilisateur avant la correction du 2026-08-26 de la section "
        "'Figures produites dans le corrigé' du SKILL.md correction-experte, qui "
        "rendait la production de l'image optionnelle. Corpus déjà en base, produit "
        "avant cette correction : sert à cibler ce qui doit être retraité."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--country", default=None,
            help="Filtre par code pays (ex. cm) - défaut : tous les pays.",
        )
        parser.add_argument(
            "--matiere", default=None,
            help="Filtre par code matière (Subject.code) - défaut : toutes les matières.",
        )
        parser.add_argument(
            "--csv", action="store_true",
            help="Écrit le détail complet en CSV sur stdout (à rediriger vers un fichier) "
                 "au lieu du résumé lisible par défaut.",
        )
        parser.add_argument(
            "--sample", type=int, default=25,
            help="Nombre d'exemples détaillés affichés dans le résumé (défaut 25, ignoré avec --csv).",
        )

    def handle(self, *args, **options):
        exercises = Exercise.objects.select_related(
            "lesson", "lesson__subject", "lesson__subject__country",
        ).prefetch_related("questions")

        if options["country"]:
            exercises = exercises.filter(lesson__subject__country__code__iexact=options["country"])
        if options["matiere"]:
            exercises = exercises.filter(lesson__subject__code__iexact=options["matiere"])

        lignes = []
        total_questions_avec_demande = 0

        for exercise in exercises.order_by("lesson__subject__country__code", "lesson__epreuve_source", "numero_exercice"):
            questions = list(exercise.questions.order_by("ordre"))
            # Vérifié sur Question.corrige_markdown (la source de vérité que
            # attacher_figure_corrige/ingestion écrivent directement), jamais sur
            # Exercise.corrige_markdown : ce dernier n'est qu'un cache compilé depuis
            # les Question, et peut rester transitoirement désynchronisé (recompilation
            # ratée/en retard) - constaté en pratique : un exercice dont le corrigé de
            # chaque Question contenait bien l'image a pourtant été signalé à tort par
            # ce script tant qu'il ne lisait que le champ compilé de l'Exercise.
            a_une_image_dans_corrige = any(
                _IMAGE_PLACEHOLDER_RE.search(q.corrige_markdown or "") for q in questions
            )
            demande_par_question = {}
            for question in questions:
                demandes = _sentences_avec_demande(question.enonce_markdown or "")
                if demandes:
                    demande_par_question[question.pk] = demandes[0]

            if not demande_par_question:
                # Repli uniquement si AUCUNE sous-question n'a de demande dans son
                # propre texte : un problème à plusieurs parties annonce parfois "Partie
                # C : tracer la courbe de f" dans le préambule partagé alors que ce
                # préambule est un sommaire, pas une consigne répétée pour chaque
                # sous-question (I.1, II.a, etc. n'ont rien à voir avec un tracé) -
                # attribuer ce match à TOUTES les sous-questions produirait un faux
                # positif par sous-question non concernée. On l'attribue donc une seule
                # fois, à la dernière sous-question de l'exercice (celle qui porte
                # presque toujours la partie annoncée en dernier dans ce genre de sommaire).
                demandes_intro = _sentences_avec_demande(exercise.enonce_intro_markdown or "")
                if demandes_intro and questions:
                    demande_par_question[questions[-1].pk] = demandes_intro[0]

            for question in questions:
                if question.pk not in demande_par_question:
                    continue
                total_questions_avec_demande += 1
                if a_une_image_dans_corrige:
                    continue

                motif, phrase = demande_par_question[question.pk]
                lignes.append({
                    "pays": exercise.lesson.subject.country.code,
                    "matiere": exercise.lesson.subject.code,
                    "epreuve": exercise.lesson.epreuve_source or exercise.lesson.title,
                    "lesson_slug": exercise.lesson.slug,
                    "exercice": exercise.numero_exercice,
                    "question": question.numero,
                    "question_pk": question.pk,
                    "motif": motif,
                    "extrait": phrase[:200],
                })

        if options["csv"]:
            writer = csv.DictWriter(
                sys.stdout,
                fieldnames=["pays", "matiere", "epreuve", "lesson_slug", "exercice", "question", "question_pk", "motif", "extrait"],
            )
            writer.writeheader()
            for ligne in lignes:
                writer.writerow(ligne)
            return

        self.stdout.write(
            f"{total_questions_avec_demande} sous-question(s) avec un tracé demandé dans l'énoncé, "
            f"dont {len(lignes)} sans aucune image dans le corrigé de l'exercice.\n",
        )

        par_pays_matiere = {}
        for ligne in lignes:
            cle = (ligne["pays"], ligne["matiere"])
            par_pays_matiere[cle] = par_pays_matiere.get(cle, 0) + 1
        if par_pays_matiere:
            self.stdout.write("Répartition :")
            for (pays, matiere), count in sorted(par_pays_matiere.items(), key=lambda kv: -kv[1]):
                self.stdout.write(f"  {pays} / {matiere} : {count}")
            self.stdout.write("")

        for ligne in lignes[: options["sample"]]:
            self.stdout.write(
                f"[{ligne['pays']}] {ligne['epreuve']} - Exercice {ligne['exercice']}, "
                f"Q{ligne['question']} (pk={ligne['question_pk']}, motif={ligne['motif']})\n"
                f"    \"{ligne['extrait']}\"\n",
            )
        if len(lignes) > options["sample"]:
            self.stdout.write(f"... et {len(lignes) - options['sample']} autre(s) (relancer avec --csv pour le détail complet).")
