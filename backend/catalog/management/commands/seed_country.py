from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Country, Cursus, Examen, Series, Subject

# Référentiel repris de celui du Cameroun (voir migrations 0003_seed_referentiel,
# 0011_seed_litterature, 0018_seed_eps) : point de départ raisonnable pour un pays qui
# partage le système BEPC/Probatoire/BAC hérité du modèle français, mais Subject/Series
# sont désormais propres à chaque pays (voir catalog.models) - à revoir depuis l'admin
# après coup, une série ou une matière pouvant ne pas exister (ou porter un autre nom)
# dans le système scolaire réel de ce pays.
SUBJECTS = [
    ("MATHS", "Mathématiques"),
    ("PHYSIQUE_CHIMIE", "Physique-Chimie"),
    ("SVT", "Sciences de la Vie et de la Terre"),
    ("FRANCAIS", "Français"),
    ("PHILOSOPHIE", "Philosophie"),
    ("HISTOIRE_GEO", "Histoire-Géographie"),
    ("ANGLAIS", "Anglais"),
    ("ECONOMIE", "Économie"),
    ("DROIT", "Droit"),
    ("LITTERATURE", "Littérature"),
    ("EPS", "Éducation physique et sportive"),
]

SERIES = [
    ("A", "Lettres-Philo"),
    ("SES", "Sciences Économiques et Sociales"),
    ("C", "Maths"),
    ("D", "Sciences"),
    ("E", "Mathématiques et Techniques"),
    ("TI", "Techniques Industrielles"),
    ("COM", "Techniques Commerciales et de Gestion"),
]


class Command(BaseCommand):
    help = (
        "Amorce le référentiel (Country, Subject, Series, Cursus) d'un nouveau pays à "
        "partir de celui du Cameroun, pour éviter d'écrire une migration de données "
        "ponctuelle à chaque nouveau pays (voir 0015_country.py pour l'ancien procédé). "
        "Idempotent : ré-exécuter ne duplique rien, et complète un pays déjà partiellement "
        "seedé. Le résultat est un point de départ à ajuster ensuite depuis l'admin."
    )

    def add_arguments(self, parser):
        parser.add_argument("code", help="Code pays à 2 lettres, celui du dossier ingest/<code>/ (ex : bj).")
        parser.add_argument("label", help="Nom du pays (ex : Bénin).")
        parser.add_argument("--dial-code", default="", help="Indicatif téléphonique international sans le + (ex : 229).")
        parser.add_argument("--currency", default="", help="Code devise ISO 4217 (ex : XOF).")

    def handle(self, *args, **options):
        code = options["code"].strip().upper()
        if len(code) != 2:
            raise CommandError(f"Code pays invalide : {code!r} - attendu 2 lettres (celui du dossier ingest/<code>/).")

        label = options["label"].strip()
        if not label:
            raise CommandError("Le nom du pays (label) est obligatoire.")

        with transaction.atomic():
            country, country_created = Country.objects.get_or_create(
                code=code,
                defaults={"label": label, "dial_code": options["dial_code"], "currency": options["currency"]},
            )
            if not country_created:
                self.stdout.write(self.style.WARNING(f"Country {code} existe déjà - référentiel complété si besoin."))

            subjects_created = sum(
                Subject.objects.get_or_create(country=country, code=subj_code, defaults={"label": subj_label})[1]
                for subj_code, subj_label in SUBJECTS
            )

            series_objs = {}
            series_created = 0
            for series_code, series_label in SERIES:
                series, was_created = Series.objects.get_or_create(
                    country=country, code=series_code, defaults={"label": series_label},
                )
                series_objs[series_code] = series
                series_created += was_created

            _, bepc_created = Cursus.objects.get_or_create(country=country, examen=Examen.BEPC, series=None)
            cursus_created = int(bepc_created)
            for series in series_objs.values():
                _, prob_created = Cursus.objects.get_or_create(country=country, examen=Examen.PROBATOIRE, series=series)
                _, bac_created = Cursus.objects.get_or_create(country=country, examen=Examen.BAC, series=series)
                cursus_created += int(prob_created) + int(bac_created)

        self.stdout.write(self.style.SUCCESS(
            f"{country.label} ({country.code}) : {subjects_created} matière(s), "
            f"{series_created} série(s), {cursus_created} cursus créé(s).",
        ))
        self.stdout.write(
            "Référentiel calqué sur celui du Cameroun - vérifie et ajuste depuis l'admin "
            "(Subject/Series) si ce pays n'a pas exactement les mêmes matières/séries.",
        )
