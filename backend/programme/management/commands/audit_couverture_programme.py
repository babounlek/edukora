import json
from collections import defaultdict
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.ingestion import IngestionError, _resolve_subject, run_ingestion
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
        "orphelins référençant un rappel de méthode introuvable, etc.) ; (4) références "
        "programme manquantes - les questions des fichiers ingest/<pays> qui sortent "
        "sans `savoir_officiel` alors que leur matière a bien un référentiel, en "
        "distinguant les épreuves de génération récente (champ présent mais toujours "
        "null - la compétence ne le remplit pas) des épreuves antérieures au champ."
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

        # Les quatre sections sont indépendantes (voir l'aide de la commande) : (3) est
        # un audit du dossier ingest/<pays> entier, sans rapport avec --subject ni avec
        # l'état du référentiel - une matière absente du référentiel ne doit jamais
        # empêcher de sauter (1)/(2)/(4) tout en gardant (3).
        if subjects:
            self._report_scope_gaps(country, subjects)
            self._report_content_gaps(country, subjects)
        else:
            self.stdout.write(self.style.WARNING(
                f"Aucune matière du référentiel programme officiel pour {country_code}"
                + (f" (matière {subject_filter!r})" if subject_filter else "")
                + " - sections 1, 2 et 4 sautées."
            ))

        if not options["skip_ingestion_check"]:
            self._report_blocked_ingestion(country)

        # Après (3) pour que les sections s'affichent dans l'ordre de leur numéro, alors
        # même que (4) dépend de `subjects` comme (1)/(2) et pas de --skip-ingestion-check :
        # elle ne fait que lire les fichiers (aucune ingestion à blanc), donc elle reste
        # bon marché même quand (3) est sautée pour cause de dossier volumineux.
        if subjects:
            self._report_missing_savoir_refs(country, subjects)

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
            has_catalog = Question.objects.rattachees_au_savoir(savoir).filter(
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

    def _report_missing_savoir_refs(self, country, subjects):
        """
        Contrepartie amont de la section (2) : celle-ci constate qu'un savoir n'a aucun
        contenu, celle-là montre POURQUOI - du contenu existe bien, mais il arrive sans
        `savoir_officiel`, donc rien ne le rattache au référentiel. Sans cette section,
        un savoir couvert par trois épreuves reste indéfiniment listé comme un trou, et
        les trois outils de pilotage (audit, quiz.select_quiz_batch,
        inedit._savoirs_prioritaires) réclament du contenu déjà écrit.

        Grain volontairement large - matière et dossier, jamais classe/série. `classe`
        n'existe que dans une poignée de fichiers (champ récent) et `niveau` est du
        texte libre ("Terminale", "Terminale C, D, E", "Troisième"...) : en tirer une
        classe demanderait le parsing approximatif que `_resolve_savoir_officiel` refuse
        précisément de faire. Une matière au référentiel suffit à rendre le signal
        exploitable, sans jamais rien affirmer de faux.

        Purement descriptif : aucun seuil, aucun échec. Un dossier listé ici n'est pas
        forcément un défaut (une épreuve peut porter sur une classe hors référentiel,
        ex. Histoire 3e absente alors que la Géographie 3e existe) - c'est à l'opérateur
        de trancher, même discipline que le [à vérifier] de la section (1).
        """
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\n\n=== 4. Références programme manquantes (fichiers ingest/<pays>) ===",
        ))
        ingest_path = Path(settings.BASE_DIR) / "ingest" / country.code.lower()
        if not ingest_path.exists():
            self.stdout.write(f"Dossier introuvable, section sautée : {ingest_path}")
            return

        # Même discipline que run_ingestion (voir son commentaire) : _resolve_subject est
        # mémoïsée sur (matiere, country) et rendrait sinon des Subject capturés lors d'un
        # appel précédent - sans effet en usage CLI (un process par run), mais la commande
        # est aussi appelée en test où plusieurs runs se suivent dans le même process.
        _resolve_subject.cache_clear()
        subject_ids = {subject.pk for subject in subjects}
        # dossier -> {code matière -> [questions_total, sans_référence, questions_portant_la_clé]}
        per_folder = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))

        for file_path in sorted(ingest_path.rglob("*.json")):
            # Même convention d'exclusion que run_ingestion (voir son commentaire) : un
            # composant de chemin préfixé par "_" est du tooling, jamais du contenu.
            if any(part.startswith("_") for part in file_path.relative_to(ingest_path).parts):
                continue
            try:
                raw = json.loads(file_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Déjà signalé nommément par la section (3), inutile de le redire ici.
                continue

            for data in raw if isinstance(raw, list) else [raw]:
                # Seuls les exercices comptent : c'est `Question.themes` qui porte le
                # rattachement mesuré par la section (2). Un cours (objet à "sections")
                # a bien un `meta.savoir_officiel`, mais il ne pèse sur aucun des trois
                # outils de pilotage - l'inclure diluerait le signal.
                if not isinstance(data, dict) or "sections" in data:
                    continue
                questions = data.get("questions")
                if not isinstance(questions, list) or not questions:
                    continue
                try:
                    subject = _resolve_subject(data.get("matiere"), country)
                except (IngestionError, TypeError):
                    continue
                if subject.pk not in subject_ids:
                    continue

                folder = file_path.parent.relative_to(ingest_path).as_posix() or "."
                stats = per_folder[folder][subject.code]
                for question in questions:
                    if not isinstance(question, dict):
                        continue
                    stats[0] += 1
                    if "savoir_officiel" in question:
                        stats[2] += 1
                    if not question.get("savoir_officiel"):
                        stats[1] += 1

        # Deux populations à ne surtout pas confondre : une épreuve dont les questions
        # PORTENT la clé à null a été générée par une compétence qui connaît le champ et
        # le laisse vide malgré tout - c'est un défaut actif, réparable en régénérant. Une
        # épreuve où la clé est absente est simplement antérieure au champ : même manque
        # de rattachement, mais rien à reprocher à la génération d'aujourd'hui. Les
        # confondre ferait passer un bug courant pour une dette historique.
        actifs, legacy = [], defaultdict(lambda: [0, 0])
        for folder, par_matiere in per_folder.items():
            for code, (total, manquantes, avec_cle) in sorted(par_matiere.items()):
                if not manquantes:
                    continue
                if avec_cle:
                    actifs.append((manquantes, total, folder, code))
                else:
                    legacy[code][0] += manquantes
                    legacy[code][1] += 1

        if not actifs and not legacy:
            self.stdout.write("Toutes les questions des matières du référentiel portent une référence programme.")
            return

        if actifs:
            self.stdout.write(
                "Champ présent mais laissé null - la compétence connaît `savoir_officiel` "
                "et ne le remplit pas (régénérable) :",
            )
            for manquantes, total, folder, code in sorted(actifs, key=lambda a: (-a[0], a[2])):
                self.stdout.write(self.style.ERROR(
                    f"  [{code}] {folder} : {manquantes}/{total} question(s) sans référence",
                ))

        if legacy:
            self.stdout.write("\nChamp absent - épreuves antérieures à `savoir_officiel` (dette, pas régression) :")
            for code, (manquantes, dossiers) in sorted(legacy.items()):
                self.stdout.write(f"  [{code}] {manquantes} question(s) sur {dossiers} épreuve(s)")

        total_manquantes = sum(a[0] for a in actifs) + sum(v[0] for v in legacy.values())
        total_questions = sum(
            stats[0] for par_matiere in per_folder.values() for stats in par_matiere.values()
        )
        self.stdout.write(self.style.WARNING(
            f"\nTotal : {total_manquantes} question(s) sans référence programme sur {total_questions} "
            f"pour les matières du référentiel.",
        ))
