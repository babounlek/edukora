from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.ingestion import run_ingestion
from catalog.models import Country, Cursus, Question, StatutContenu, Subject
from programme.models import Module, Savoir
from quiz.models import CompetenceItem


class _RollbackAudit(Exception):
    """Signal interne pour annuler la transaction d'ingestion à blanc (voir
    _report_blocked_ingestion) - jamais laissée remonter au-delà de son propre except."""


class Command(BaseCommand):
    help = (
        "Croise le référentiel programme officiel (programme.Module/Savoir) avec le "
        "contenu réellement ingéré, par pays/matière, pour repérer les trous avant "
        "qu'ils ne deviennent des tickets urgents - jamais en devinant depuis la "
        "mémoire d'une session précédente, toujours en interrogeant la base et le "
        "dossier ingest/ réels. Trois sections indépendantes : (1) périmètre - un "
        "cursus réel sans aucun module officiel pour une matière déjà couverte "
        "ailleurs par le référentiel (ex. Chimie 1ère TI) ; (2) contenu - un savoir "
        "du référentiel sans aucune Question d'épreuve ni CompetenceItem de quiz "
        "validé qui s'y rattache ; (3) ingestion bloquée - rejoue tout le dossier "
        "ingest/<pays> dans une transaction systématiquement annulée, pour lister "
        "sans rien écrire les fichiers qui échoueraient aujourd'hui (cours "
        "orphelins référençant un rappel de méthode introuvable, etc.)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--country", default="CM",
            help="Code pays (défaut CM - seul pays avec un référentiel programme aujourd'hui).",
        )
        parser.add_argument(
            "--subject",
            help="Limite le rapport à ce code matière (défaut : toutes les matières déjà couvertes par le référentiel pour ce pays).",
        )
        parser.add_argument(
            "--skip-ingestion-check", action="store_true",
            help="Saute la section (3) - utile si ingest/<pays> est volumineux ou absent de cet environnement.",
        )

    def handle(self, *args, **options):
        country_code = options["country"]
        subject_filter = options["subject"]

        try:
            country = Country.objects.get(code=country_code)
        except Country.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Pays inconnu : {country_code!r}"))
            return

        # "Déjà couvertes par le référentiel" = au moins un Module existe pour cette
        # matière, quelle que soit sa classe/série - une matière absente du référentiel
        # (ex. Anglais, jamais construit) est hors scope pour ce rapport : le signaler
        # comme un "trou" serait juste redire ce qui est déjà connu et volontaire,
        # jamais une découverte. Voir la section (1) pour le vrai signal de nouveauté.
        covered_subject_ids = set(
            Module.objects.filter(subject__country=country).values_list("subject_id", flat=True).distinct()
        )
        subjects = Subject.objects.filter(pk__in=covered_subject_ids)
        if subject_filter:
            subjects = subjects.filter(code=subject_filter)
        subjects = list(subjects.order_by("code"))

        # Les trois sections sont indépendantes (voir l'aide de la commande) : (3) est
        # un audit du dossier ingest/<pays> entier, sans rapport avec --subject ni avec
        # l'état du référentiel - une matière absente du référentiel ne doit jamais
        # empêcher de sauter (1)/(2) tout en gardant (3).
        if subjects:
            self._report_scope_gaps(country, subjects)
            self._report_content_gaps(country, subjects)
        else:
            self.stdout.write(self.style.WARNING(
                f"Aucune matière du référentiel programme officiel pour {country_code}"
                + (f" (matière {subject_filter!r})" if subject_filter else "")
                + " - sections 1 et 2 sautées."
            ))

        if not options["skip_ingestion_check"]:
            self._report_blocked_ingestion(country)

    def _report_scope_gaps(self, country, subjects):
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\n=== 1. Trous de périmètre (cursus réel sans aucun module officiel) ===",
        ))
        all_cursus_ids = set(Cursus.objects.filter(country=country).values_list("pk", flat=True))
        any_found = False

        for subject in subjects:
            covered_cursus_ids = set(
                Cursus.objects.filter(modules_officiels__subject=subject).values_list("pk", flat=True).distinct()
            )
            # "confirmé" : du contenu catalogue VALIDE existe déjà pour ce (matière,
            # cursus) alors que le référentiel ne le couvre pas - signal fort, ne peut
            # jamais être un faux positif de combo pédagogiquement inexistante puisque
            # du contenu réel y a déjà été publié.
            content_cursus_ids = set(
                Cursus.objects.filter(
                    lessons__subject=subject, lessons__statut=StatutContenu.VALIDE,
                ).values_list("pk", flat=True).distinct()
            )
            confirmed_ids = content_cursus_ids - covered_cursus_ids
            # "à vérifier" : tout autre cursus du pays non couvert par le référentiel,
            # sans qu'on sache si cette matière y est même enseignée - informationnel
            # seulement (ex. Chimie 1ère TI : exclusion déjà connue et délibérée, pas un
            # bug tant qu'aucun contenu réel ne le contredit), jamais présenté comme un
            # trou confirmé.
            to_verify_ids = all_cursus_ids - covered_cursus_ids - confirmed_ids

            if not confirmed_ids and not to_verify_ids:
                continue
            any_found = True
            self.stdout.write(f"\n{subject.code} ({subject.label}) :")
            for cursus in Cursus.objects.filter(pk__in=confirmed_ids).select_related("series").order_by("examen", "series__code"):
                self.stdout.write(self.style.ERROR(
                    f"  [CONFIRMÉ] {cursus} - du contenu existe déjà, aucun module officiel ne le couvre.",
                ))
            for cursus in Cursus.objects.filter(pk__in=to_verify_ids).select_related("series").order_by("examen", "series__code"):
                self.stdout.write(
                    f"  [à vérifier] {cursus} - non couvert par le référentiel, aucun contenu catalogue existant pour trancher.",
                )

        if not any_found:
            self.stdout.write("Aucun trou de périmètre détecté.")

    def _report_content_gaps(self, country, subjects):
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\n\n=== 2. Trous de contenu (savoir du référentiel sans contenu validé) ===",
        ))
        savoirs = (
            Savoir.objects.filter(module__subject__in=subjects, module__cursus__country=country)
            .select_related("module", "module__subject")
            .distinct()
            .order_by("module__subject__code", "module__ordre", "ordre")
        )

        any_found = False
        for savoir in savoirs:
            subject = savoir.module.subject
            # Même filtre (subject, country) que quiz.ingestion._find_undercovered_savoirs_officiels
            # (voir cursus__country) : Tag est un vocabulaire global, pas rattaché à un
            # pays - sans ce filtre un Tag identique réutilisé ailleurs fausserait le résultat.
            has_catalog = Question.objects.filter(
                themes__savoir_officiel=savoir,
                exercise__statut=StatutContenu.VALIDE,
                exercise__lesson__statut=StatutContenu.VALIDE,
                exercise__lesson__subject=subject,
                exercise__lesson__cursus__country=country,
            ).exists()
            has_quiz = CompetenceItem.objects.filter(
                theme__savoir_officiel=savoir, subject=subject, statut=StatutContenu.VALIDE,
            ).exists()
            if has_catalog and has_quiz:
                continue

            any_found = True
            missing = []
            if not has_catalog:
                missing.append("aucune Question d'épreuve")
            if not has_quiz:
                missing.append("aucun CompetenceItem de quiz")
            serie = f"/{savoir.module.serie_label}" if savoir.module.serie_label else ""
            self.stdout.write(
                f"  [{subject.code}] {savoir.module.classe}{serie} M{savoir.module.numero} - {savoir} : "
                f"{', '.join(missing)}",
            )

        if not any_found:
            self.stdout.write("Aucun trou de contenu détecté.")

    def _report_blocked_ingestion(self, country):
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\n\n=== 3. Ingestion bloquée (dossier ingest/<pays>, transaction annulée) ===",
        ))
        ingest_path = Path(settings.BASE_DIR) / "ingest" / country.code.lower()
        if not ingest_path.exists():
            self.stdout.write(f"Dossier introuvable, section sautée : {ingest_path}")
            return

        # run_ingestion ne lève jamais elle-même (chaque fichier est essayé dans sa
        # propre transaction.atomic() interne et ses erreurs sont collectées, voir
        # catalog.ingestion.run_ingestion) - le seul moyen de "dry-run" tout le dossier
        # sans rien écrire est donc d'envelopper l'appel entier dans notre propre
        # transaction et de forcer nous-mêmes un rollback après coup.
        report = {}

        def _run():
            report.update(run_ingestion(ingest_path))
            raise _RollbackAudit()

        try:
            with transaction.atomic():
                _run()
        except _RollbackAudit:
            pass

        if report["errors"]:
            self.stdout.write(self.style.ERROR(
                f"{len(report['errors'])} fichier(s) bloqué(s) sur {report['files_found']} (rien n'a été écrit) :",
            ))
            for error in report["errors"]:
                self.stdout.write(self.style.ERROR(f"  - {error}"))
        else:
            self.stdout.write(
                f"Aucun blocage sur {report['files_found']} fichier(s) - tout ingère proprement (à blanc, rien n'a été écrit).",
            )
