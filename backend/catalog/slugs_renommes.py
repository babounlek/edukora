"""
Anciennes adresses (slugs) devenues d'autres adresses après un renommage éditorial, pour que les liens déjà partagés,
favoris et pages indexées continuent de fonctionner. Le fichier `slugs_renommes.json` est de la forme
{"lesson": {"ancien-slug": "nouveau-slug"}, "epreuveinedite": {...}} ; il est écrit par les commandes de renommage
(voir renommer_sciences_serie_a) et lu ici, sans base ni migration.
"""
import json
from functools import lru_cache
from pathlib import Path

FICHIER = Path(__file__).with_name("slugs_renommes.json")


@lru_cache(maxsize=1)
def _table():
    try:
        return json.loads(FICHIER.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def slug_actuel(modele, slug):
    """Le slug en vigueur pour `slug` (le même s'il n'a jamais été renommé). `modele` : nom du modèle en minuscules."""
    return _table().get(modele, {}).get(slug, slug)


def recharger():
    _table.cache_clear()
