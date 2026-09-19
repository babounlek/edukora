from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Country, Cursus, Examen, Filiere, Groupe, Series, Subject

# Référentiel repris de celui du Cameroun (voir migrations 0003_seed_referentiel,
# 0011_seed_litterature, 0018_seed_eps) : point de départ raisonnable pour un pays qui
# partage le système BEPC/Probatoire/BAC hérité du modèle français, mais Subject/Series
# sont désormais propres à chaque pays (voir catalog.models) - à revoir depuis l'admin
# après coup, une série ou une matière pouvant ne pas exister (ou porter un autre nom)
# dans le système scolaire réel de ce pays.
SUBJECTS = [
    ("MATHS", "Mathématiques"),
    ("PHYSIQUE", "Physique"),
    ("CHIMIE", "Chimie"),
    ("PHYSIQUE_CHIMIE", "Physique-Chimie"),
    ("SVT", "Sciences de la Vie et de la Terre"),
    ("FRANCAIS", "Français"),
    ("PHILOSOPHIE", "Philosophie"),
    ("HISTOIRE", "Histoire"),
    ("GEOGRAPHIE", "Géographie"),
    ("HISTOIRE_GEO", "Histoire-Géographie"),
    ("ANGLAIS", "Anglais"),
    ("ESPAGNOL", "Espagnol"),
    ("ALLEMAND", "Allemand"),
    ("ECONOMIE", "Économie"),
    ("DROIT", "Droit"),
    ("EDUCATION_CIVIQUE", "Éducation Civique"),
    ("LITTERATURE", "Littérature"),
    ("EPS", "Éducation physique et sportive"),
    ("INFORMATIQUE", "Informatique"),
    # Décomposition de l'Informatique en Série TI (2026-09-16) - voir
    # catalog.models.SUBJECT_FAMILIES : INFORMATIQUE reste le code combiné, ces trois
    # codes couvrent le cas normal d'une copie mono-discipline.
    ("PROGRAMMATION", "Programmation"),
    ("SYSTEMES_INFORMATION", "Systèmes d'Information"),
    ("RESEAUX_SECURITE", "Réseaux, Internet et Sécurité Informatique"),
    ("PHYSIQUE_CHIMIE_TECH", "Physique-Chimie-Technologie"),
    ("DESSIN", "Dessin"),
]

SERIES = [
    ("A", "Lettres-Philo", Groupe.GENERAL),
    ("C", "Maths", Groupe.GENERAL),
    ("D", "Sciences", Groupe.GENERAL),
    ("E", "Mathématiques et Techniques", Groupe.GENERAL),
    # TI = Technologie de l'Information (dominante du général), pas la filière
    # industrielle - voir la correction de libellé en 0052_series_groupe.
    ("TI", "Technologie de l'Information", Groupe.GENERAL),
    # Pas de série technique "générique" ici : depuis l'introduction de Filiere, le
    # technique se raisonne en spécialité rattachée à une famille - voir SPECIALITES.
]

# Grandes familles de l'enseignement technique - contrairement au général (où la
# Series EST la filière - A, C, D...), le technique se raisonne en famille +
# spécialité (précision utilisateur, 2026-08-19).
FILIERES = [
    ("STT", "Sciences et Technologies du Tertiaire"),
    ("STI", "Sciences et Technologies Industrielles"),
    ("ESF_SMS", "Économie Sociale et Familiale / Sciences Médico-Sociales"),
    ("HOTELLERIE_TOURISME", "Hôtellerie et Tourisme"),
    ("AGRICULTURE", "Agriculture et domaines connexes"),
]

# (filiere_code, series_code, series_label) - une spécialité = une Series technique
# rattachée à sa Filiere. Pas de code officiel court connu (contrairement à A/C/D/E) -
# codes dérivés du libellé. ESF/SMS et Agriculture : aucune spécialité listée par
# l'utilisateur ("selon les établissements") - Filiere créée ci-dessus, sans
# spécialité enfant pour l'instant plutôt que d'en inventer.
SPECIALITES = [
    ("STT", "COMPTABILITE_GESTION", "Comptabilité et Gestion"),
    ("STT", "SECRETARIAT_BUREAUTIQUE", "Secrétariat / Bureautique"),
    ("STT", "COMMERCE", "Commerce"),
    ("STT", "BANQUE", "Banque"),
    ("STI", "ELECTRICITE", "Électricité"),
    ("STI", "ELECTROTECHNIQUE", "Électrotechnique"),
    ("STI", "ELECTRONIQUE", "Électronique"),
    ("STI", "MECANIQUE", "Mécanique"),
    ("STI", "GENIE_CIVIL", "Génie Civil"),
    ("STI", "CONSTRUCTION", "Construction"),
    ("STI", "FABRICATION_MECANIQUE", "Fabrication Mécanique"),
    ("HOTELLERIE_TOURISME", "RESTAURATION", "Restauration"),
    ("HOTELLERIE_TOURISME", "HEBERGEMENT", "Hébergement"),
    ("HOTELLERIE_TOURISME", "TOURISME", "Tourisme"),
]


class Command(BaseCommand):
    help = (
        "Amorce le référentiel (Country, Subject, Series, Filiere, Cursus) d'un nouveau "
        "pays à partir de celui du Cameroun, pour éviter d'écrire une migration de "
        "données ponctuelle à chaque nouveau pays (voir 0015_country.py pour l'ancien "
        "procédé). Idempotent : ré-exécuter ne duplique rien, et complète un pays déjà "
        "partiellement seedé. Le résultat est un point de départ à ajuster ensuite "
        "depuis l'admin. Le pays est créé inactif (Country.actif=False) : un clonage de "
        "référentiel n'est pas une localisation réelle, l'activation publique reste un "
        "geste manuel délibéré."
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
                defaults={
                    "label": label,
                    "dial_code": options["dial_code"],
                    "currency": options["currency"],
                    # Un référentiel cloné depuis le Cameroun (voir commentaire SUBJECTS
                    # ci-dessus) n'est jamais une localisation réelle - le pays reste
                    # invisible du catalogue public (voir VisibleQuerySet.visibles()) tant
                    # qu'un admin ne l'a pas vérifié et activé à la main depuis l'admin.
                    "actif": False,
                },
            )
            if not country_created:
                self.stdout.write(self.style.WARNING(f"Country {code} existe déjà - référentiel complété si besoin."))

            subjects_created = sum(
                Subject.objects.get_or_create(country=country, code=subj_code, defaults={"label": subj_label})[1]
                for subj_code, subj_label in SUBJECTS
            )

            series_objs = {}
            series_created = 0
            for series_code, series_label, series_groupe in SERIES:
                series, was_created = Series.objects.get_or_create(
                    country=country, code=series_code, defaults={"label": series_label, "groupe": series_groupe},
                )
                series_objs[series_code] = series
                series_created += was_created

            filiere_objs = {}
            filieres_created = 0
            for filiere_code, filiere_label in FILIERES:
                filiere, was_created = Filiere.objects.get_or_create(
                    country=country, code=filiere_code, defaults={"label": filiere_label},
                )
                filiere_objs[filiere_code] = filiere
                filieres_created += was_created

            for filiere_code, series_code, series_label in SPECIALITES:
                series, was_created = Series.objects.get_or_create(
                    country=country, code=series_code,
                    defaults={"label": series_label, "groupe": Groupe.TECHNIQUE, "filiere": filiere_objs[filiere_code]},
                )
                series_objs[series_code] = series
                series_created += was_created

            _, bepc_created = Cursus.objects.get_or_create(country=country, examen=Examen.BEPC, series=None)
            cursus_created = int(bepc_created)
            for series_code, series in series_objs.items():
                _, prob_created = Cursus.objects.get_or_create(country=country, examen=Examen.PROBATOIRE, series=series)
                _, bac_created = Cursus.objects.get_or_create(country=country, examen=Examen.BAC, series=series)
                cursus_created += int(prob_created) + int(bac_created)
                if series.filiere_id:
                    # Le CAP réutilise les mêmes spécialités que le Bac technique
                    # (précision utilisateur, 2026-08-19) - pas de Cursus(CAP,
                    # series=None) comme le BEPC : le CAP n'existe qu'avec une
                    # spécialité (une Series rattachée à une Filiere).
                    _, cap_created = Cursus.objects.get_or_create(country=country, examen=Examen.CAP, series=series)
                    cursus_created += int(cap_created)

        self.stdout.write(self.style.SUCCESS(
            f"{country.label} ({country.code}) : {subjects_created} matière(s), "
            f"{series_created} série(s), {filieres_created} filière(s), {cursus_created} cursus créé(s).",
        ))
        self.stdout.write(
            "Référentiel calqué sur celui du Cameroun - vérifie et ajuste depuis l'admin "
            "(Subject/Series/Filiere) si ce pays n'a pas exactement les mêmes matières/séries.",
        )
        if country_created:
            self.stdout.write(self.style.WARNING(
                f"{country.label} créé inactif (Country.actif=False) - invisible du catalogue "
                "public jusqu'à activation manuelle depuis l'admin, une fois le référentiel "
                "vérifié et du contenu réel ingéré.",
            ))
