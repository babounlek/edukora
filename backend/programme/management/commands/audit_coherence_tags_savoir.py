from django.core.management.base import BaseCommand

from catalog.ingestion import _tag_en_conflit_avec_un_autre_savoir
from catalog.models import Tag


class Command(BaseCommand):
    help = (
        "Audit rétrospectif : liste les Tag déjà rattachés à un Savoir officiel (voir "
        "catalog.Tag.savoir_officiel) qui côtoient, sur un autre Cours ou une autre "
        "Question, un tag voisin ou un rattachement direct pointant vers un savoir "
        "différent - même détection que les 3 gardes de "
        "catalog.ingestion._link_tags_to_savoir (voir sa docstring, incident du "
        "2026-09-07 : « racine évidente » rattaché à tort à TRIGONOMETRIE), mais "
        "rejouée sur les tags déjà rattachés plutôt qu'au moment de l'ingestion. Les "
        "gardes protègent le futur, cette commande balaie le passé - y compris les "
        "rattachements posés par la passe de curation map_tags_to_savoir_officiel ou à "
        "la main dans TagAdmin (formulaire libre, sans garde). Read-only : ne modifie "
        "jamais Tag.savoir_officiel, se contente de lister - la correction (dérattacher "
        "via le shell, ou réaffecter) reste une décision manuelle."
    )

    def add_arguments(self, parser):
        parser.add_argument("--country", default="CM", help="Code pays (défaut CM - seul pays avec un référentiel programme aujourd'hui).")
        parser.add_argument(
            "--subject", default=None,
            help="Code matière (défaut : toutes les matières du pays qui ont des tags rattachés).",
        )

    def handle(self, *args, **options):
        country_code = options["country"]
        subject_code = options["subject"]

        tags = (
            Tag.objects.filter(
                savoir_officiel__isnull=False,
                savoir_officiel__module__subject__country__code=country_code,
            )
            .select_related("savoir_officiel__module__subject")
        )
        if subject_code:
            tags = tags.filter(savoir_officiel__module__subject__code=subject_code)
        tags = tags.order_by("savoir_officiel__module__subject__code", "name")

        total = tags.count()
        suspects = [tag for tag in tags if _tag_en_conflit_avec_un_autre_savoir(tag, tag.savoir_officiel)]

        if not suspects:
            self.stdout.write(self.style.SUCCESS(f"{total} tag(s) rattaché(s) examiné(s), aucun conflit détecté."))
            return

        for tag in suspects:
            savoir = tag.savoir_officiel
            self.stdout.write(
                f"{tag.name!r} (id={tag.pk}) -> {savoir.module.subject.code}/{savoir.module.classe}/"
                f"{savoir.module.serie_label or '-'} M{savoir.module.numero} : {savoir}",
            )
        self.stdout.write(self.style.WARNING(
            f"\n{len(suspects)}/{total} tag(s) rattaché(s) présentent un signe de conflit - "
            "à revoir à la main (voir Tag.savoir_officiel dans TagAdmin, ou un script ciblé "
            "type celui du 2026-09-07 pour les dérattacher).",
        ))
