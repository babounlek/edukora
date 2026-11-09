"""Point d'entrée du skill veille-corpus-epreuves.

    python scripts/corpus/corpus.py audit [--rafraichir]         # AUDIT (lecture seule)
    python scripts/corpus/corpus.py qualifier <pdf> [--cible ...] # CONTRÔLE d'un document (aucune écriture de PDF)
    python scripts/corpus/corpus.py head <url>                    # RECHERCHE : valide une URL de PDF sans la télécharger
    python scripts/corpus/corpus.py collecter <url> --langue fr|en ...   # COLLECTE (télécharge dans la zone de dépôt)
    python scripts/corpus/corpus.py synchroniser <pdf-accepté> ...       # SYNCHRONISATION (copie vers ingest/_telechargements_*)
    python scripts/corpus/corpus.py registre ...                  # lecture/écriture du registre de recherches
    python scripts/corpus/corpus.py decouper <compilation.pdf>    # QUALIFICATION : une compilation -> un PDF par épreuve
    python scripts/corpus/corpus.py base-doublons <pdf>...        # CONTRÔLE : le candidat est-il déjà en base ? (lecture seule)

Jamais de `publish`, jamais de ssh, jamais d'écriture dans `ingest/cm/` ni en base.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Sous `python -I`, la console Windows écrit en cp1252 : accents cassés ou UnicodeEncodeError. UTF-8 imposé.
for _flux in (sys.stdout, sys.stderr):
    try:
        _flux.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):  # flux déjà redirigé ou remplacé (tests)
        pass

import cartographie  # noqa: E402
from commun import AUDIT, INGEST, RACINE_DEPOT  # noqa: E402

CONTENEUR = "edukora-backend-1"


def _rafraichir_base(destination):
    """Instantané de la base locale : docker cp du script, exécution dans le shell Django, docker cp du résultat."""
    script = os.path.join(RACINE_DEPOT, "scripts", "corpus", "extraire_base.py")
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    subprocess.run(["docker", "cp", script, CONTENEUR + ":/tmp/extraire_base.py"], check=True)
    subprocess.run(["docker", "exec", CONTENEUR, "python", "manage.py", "shell", "-c",
                    "exec(open('/tmp/extraire_base.py').read())"], check=True, capture_output=True)
    subprocess.run(["docker", "cp", CONTENEUR + ":/tmp/corpus_base.json", destination], check=True)


def commande_audit(args):
    date = args.date or datetime.date.today().isoformat()
    sortie = os.path.join(AUDIT, "corpus", date)
    base_json = os.path.join(sortie, "corpus_base.json")
    if args.rafraichir or not os.path.isfile(base_json):
        _rafraichir_base(base_json)
    carte = cartographie.analyser(cartographie.charger_base(base_json), args.reference)
    matrice, incoherences = cartographie.ecrire_sorties(carte, sortie)
    rapport = os.path.join(sortie, "rapport_cartographie.md")
    with open(rapport, "w", encoding="utf-8") as fh:
        fh.write(cartographie.rapport_markdown(carte, date))
    print("Rapport      :", rapport)
    print("Matrice      :", matrice)
    print("Incohérences :", incoherences)
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sous = p.add_subparsers(dest="commande", required=True)
    a = sous.add_parser("audit", help="cartographie du corpus (lecture seule)")
    a.add_argument("--rafraichir", action="store_true", help="relit la base locale via Docker")
    a.add_argument("--date", help="AAAA-MM-JJ (défaut : aujourd'hui)")
    a.add_argument("--reference", default=os.path.join(RACINE_DEPOT, "batches", "_reference-prod.json"))
    a.set_defaults(fonction=commande_audit)
    # Les autres commandes sont ajoutées par les modules correspondants (voir plus bas).
    try:
        import commandes_extra
        commandes_extra.ajouter(sous)
    except ImportError:
        pass
    args = p.parse_args(argv)
    return args.fonction(args)


if __name__ == "__main__":
    sys.exit(main())
