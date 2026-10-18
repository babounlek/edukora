#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Génère les redirections 301 `/en/<segments français>` -> `/en/<segments anglais>` du Caddyfile.

Usage :
    python scripts/generer_caddy_segments.py --ecrire     réécrit le bloc entre les deux marqueurs
    python scripts/generer_caddy_segments.py --verifier   code 1 si le Caddyfile n'est pas à jour (utilisé par les tests)

Source : frontend/src/lib/i18n/segments-url.json (la même table que le routeur et le backend). Chaque route
dont au moins un segment fixe est traduit donne UNE règle : une ancienne forme française sous /en (lien déjà
partagé, saisie à la main) est renvoyée en 301 vers la forme anglaise, pour qu'une page n'ait qu'une adresse.
Le français (sans préfixe /en) n'est pas concerné.
"""
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
JSON_SEGMENTS = RACINE / "frontend" / "src" / "lib" / "i18n" / "segments-url.json"
CADDYFILE = RACINE / "docker" / "caddy" / "Caddyfile"
DEBUT = "    # >>> redirections-segments-en (GÉNÉRÉ par scripts/generer_caddy_segments.py : ne pas modifier à la main)"
FIN = "    # <<< redirections-segments-en"


def generer(donnees):
    segments = donnees["segments"]
    lignes = [
        DEBUT,
        "    # Une URL anglaise portant encore des segments français (/en/cm/epreuves/x) est redirigée en 301 vers sa forme",
        "    # anglaise (/en/cm/past-papers/x) : une page, une adresse. La query est conservée (sans « ? » orphelin).",
        "    map {http.request.uri.query} {qs_en} {",
        '        ""      ""',
        '        default "?{http.request.uri.query}"',
        "    }",
    ]
    numero = 0
    for patron in donnees["patrons"]:
        parts = [p for p in patron.split("/") if p]
        if not any(p in segments for p in parts):
            continue  # rien à traduire : identique dans les deux langues
        numero += 1
        regex, cible, groupe = ["^/en"], ["/en"], 0
        for p in parts:
            if p.startswith(":"):
                groupe += 1
                regex.append("/([a-z]{2})" if p == ":country" else "/([^/]+)")
                cible.append(f"/{{re.seg{numero}.{groupe}}}")
            else:
                regex.append("/" + p)
                cible.append("/" + segments.get(p, p))
        lignes.append(f"    @seg_en_{numero} path_regexp seg{numero} {''.join(regex)}/?$")
        lignes.append(f"    redir @seg_en_{numero} {''.join(cible)}{{qs_en}} 301")
    lignes.append(FIN)
    return "\n".join(lignes) + "\n"


def appliquer(contenu, bloc):
    """Remplace le bloc balisé, ou l'insère avant le premier `handle_path /static`."""
    motif = re.compile(re.escape(DEBUT) + r".*?" + re.escape(FIN) + r"\n", re.S)
    if motif.search(contenu):
        return motif.sub(lambda _m: bloc, contenu)
    repere = "    handle_path /static/*"
    assert repere in contenu, "repère introuvable dans le Caddyfile"
    return contenu.replace(repere, bloc + "\n" + repere, 1)


def main():
    donnees = json.loads(JSON_SEGMENTS.read_text(encoding="utf-8"))
    with open(CADDYFILE, encoding="utf-8", newline="") as f:
        contenu = f.read()
    attendu = appliquer(contenu, generer(donnees))
    if "--verifier" in sys.argv:
        if attendu != contenu:
            print("Caddyfile obsolète : relancer scripts/generer_caddy_segments.py --ecrire", file=sys.stderr)
            return 1
        print("Caddyfile à jour")
        return 0
    with open(CADDYFILE, "w", encoding="utf-8", newline="") as f:
        f.write(attendu)
    print(f"{attendu.count('redir @seg_en_')} redirections écrites dans {CADDYFILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
