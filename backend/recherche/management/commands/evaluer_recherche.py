import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from catalog.models import Country
from recherche import moteur, texte

FICHIER_PAR_DEFAUT = Path(__file__).resolve().parents[2] / "requetes_reference.json"
TETE = 5  # résultats examinés par groupe


def _titres(reponse, type_=None):
    return [
        r["titre"] for g in reponse["groupes"] if type_ in (None, g["type"]) for r in g["resultats"][:TETE]
    ]


def _contient(titres, fragment):
    voulu = texte.normaliser(fragment)
    return any(voulu in texte.normaliser(t) for t in titres)


def verifier(cas, reponse):
    """Les écarts entre ce que dit `cas` et ce que renvoie le moteur (liste vide : le cas passe)."""
    ecarts = []
    total = reponse["total"]
    if "total_min" in cas and total < cas["total_min"]:
        ecarts.append(f"total {total} < {cas['total_min']}")
    if "total_max" in cas and total > cas["total_max"]:
        ecarts.append(f"total {total} > {cas['total_max']}")
    if "titre_contient" in cas and not _contient(_titres(reponse), cas["titre_contient"]):
        ecarts.append(f"aucun titre ne contient « {cas['titre_contient']} »")
    for type_, fragment in cas.get("titre_dans_groupe", {}).items():
        if not _contient(_titres(reponse, type_), fragment):
            ecarts.append(f"groupe {type_} : aucun titre ne contient « {fragment} »")
    if "premier_type_dans" in cas:
        premier = reponse["groupes"][0]["type"] if reponse["groupes"] else None
        if premier not in cas["premier_type_dans"]:
            ecarts.append(f"premier groupe {premier}, attendu {cas['premier_type_dans']}")
    if "corrige_contient" in cas and cas["corrige_contient"] not in (reponse["corrige"] or ""):
        ecarts.append(f"correction {reponse['corrige']!r} ne contient pas {cas['corrige_contient']!r}")
    for cle, attendu in cas.get("intention", {}).items():
        compris = (reponse["intention"] or {}).get(cle)
        valeur = compris.get("libelle") if isinstance(compris, dict) else compris
        if valeur != attendu:
            ecarts.append(f"intention {cle} = {valeur!r}, attendu {attendu!r}")
    return ecarts


class Command(BaseCommand):
    help = (
        "Rejoue la liste de requêtes de référence (recherche/requetes_reference.json) contre l'index RÉEL et "
        "dit lesquelles ne donnent plus ce qu'on attend. À lancer après tout changement du moteur ou des "
        "synonymes : un moteur « plus intelligent » peut dégrader des cas qui marchaient. Code de sortie "
        "non nul s'il y a un écart."
    )

    def add_arguments(self, parser):
        parser.add_argument("--pays", default="cm")
        parser.add_argument("--fichier", default=str(FICHIER_PAR_DEFAUT))

    def handle(self, *args, **options):
        pays = Country.objects.filter(code__iexact=options["pays"]).first()
        if pays is None:
            raise CommandError(f"Pays inconnu : {options['pays']}")
        cas = json.loads(Path(options["fichier"]).read_text(encoding="utf-8"))
        echecs = 0
        for un_cas in cas:
            reponse = moteur.chercher(un_cas["q"], pays=pays, limite=TETE)
            ecarts = verifier(un_cas, reponse)
            if ecarts:
                echecs += 1
                self.stdout.write(self.style.ERROR(f"ÉCHEC  {un_cas['q']!r}"))
                for ecart in ecarts:
                    self.stdout.write(f"         {ecart}")
            else:
                self.stdout.write(f"ok     {un_cas['q']!r}")
        self.stdout.write("")
        message = f"{len(cas) - echecs}/{len(cas)} requêtes conformes."
        if echecs:
            raise CommandError(f"{echecs} écart(s). {message}")
        self.stdout.write(self.style.SUCCESS(message))
