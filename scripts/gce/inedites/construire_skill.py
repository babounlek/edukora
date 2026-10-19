"""Reconstruit concepteur-epreuve-inedite.skill : SKILL.md du skill VIVANT (installe dans le Desktop) + section « Mode GCE »
(skill_section_mode_gce.md) + scripts du skill + outils GCE du depot.

    D:\\edukora\\venv\\Scripts\\python.exe scripts\\gce\\inedites\\construire_skill.py

Le skill vivant n'est jamais modifie : le .skill produit s'installe par « Save skill » dans le Desktop. La description du
frontmatter ne doit pas depasser 1024 caracteres (refus a l'import sinon).
"""
import json
import os
import re
import shutil
import sys
import zipfile

import yaml

SKILL_VIVANT = os.path.join(
    os.environ.get("APPDATA", r"C:\Users\Administrateur\AppData\Roaming"),
    "..", "Local", "Packages", "Claude_pzs8sxrjxfjjc", "LocalCache", "Roaming", "Claude", "local-agent-mode-sessions",
    "skills-plugin", "b753a7e6-84a4-4175-9017-11ed073d6178", "109e0e24-b249-4600-8c4f-284c2f0b64eb", "skills",
    "concepteur-epreuve-inedite",
)
ICI = os.path.dirname(os.path.abspath(__file__))
GCE = os.path.dirname(ICI)
MARQUEUR = "## Contrat de sortie \u2014 mode `blueprint`"

DESCRIPTION = (
    "G\u00e9n\u00e8re du contenu pour la verticale \"\u00c9preuves In\u00e9dites\" d'edukora (soutien scolaire francophone et GCE anglophone) : soit un Blueprint "
    "(plan d'une \u00e9preuve : sections, bar\u00e8me, comp\u00e9tences, jamais de contenu \u00e9l\u00e8ve), soit une EpreuveInedite compl\u00e8te (\u00e9nonc\u00e9s et corrig\u00e9s, \u00e0 partir d'un "
    "Blueprint d\u00e9j\u00e0 valid\u00e9). Produit un JSON pour inedit.ingestion, avec figures SVG exactes contr\u00f4l\u00e9es visuellement. \u00c0 utiliser d\u00e8s qu'on demande un "
    "blueprint, une \u00e9preuve blanche/simul\u00e9e/in\u00e9dite pour un cursus donn\u00e9, un paper GCE (O Level, A Level, Paper 1/2/3), ou le contenu d'une \u00e9preuve \u00e0 partir "
    "d'un blueprint valid\u00e9, m\u00eame sans dire \"blueprint\" ou \"JSON\" (ex. \"pr\u00e9pare une \u00e9preuve blanche de maths Terminale C\", \"cr\u00e9e un Paper 1 Mathematics O Level\"). "
    "Diff\u00e9rent de correction-experte (transcrit une \u00e9preuve R\u00c9ELLE) et de concepteur-quiz-competence (questions isol\u00e9es) : invente une \u00e9preuve ENTI\u00c8RE et coh\u00e9rente, jamais une paraphrase."
)


def main():
    racine_skill = os.path.join(ICI, "skill")
    sortie = os.path.join(racine_skill, "concepteur-epreuve-inedite")
    if os.path.isdir(racine_skill):
        shutil.rmtree(racine_skill)
    os.makedirs(sortie)
    vivant = os.path.normpath(SKILL_VIVANT)
    txt = open(os.path.join(vivant, "SKILL.md"), encoding="utf8").read()
    sec = open(os.path.join(ICI, "skill_section_mode_gce.md"), encoding="utf8").read()
    assert txt.count(MARQUEUR) == 1, "marqueur de section introuvable dans le skill vivant"
    # idempotent : si le skill vivant porte deja une section « Mode GCE » (version precedente installee), on la remplace
    debut = txt.find("## Mode GCE")
    if debut != -1:
        txt = txt[:debut] + txt[txt.index(MARQUEUR):]
    txt = txt.replace(MARQUEUR, sec.rstrip("\n") + "\n\n" + MARQUEUR)
    assert len(DESCRIPTION) <= 1024, len(DESCRIPTION)
    m = re.search(r"^description: .*$", txt, re.M)
    txt = txt[:m.start()] + "description: " + json.dumps(DESCRIPTION, ensure_ascii=False) + txt[m.end():]
    assert yaml.safe_load(txt.split("---")[1])["description"] == DESCRIPTION
    with open(os.path.join(sortie, "SKILL.md"), "w", encoding="utf8", newline="\n") as fh:
        fh.write(txt)
    shutil.copytree(os.path.join(vivant, "scripts"), os.path.join(sortie, "scripts"))
    shutil.rmtree(os.path.join(sortie, "scripts", "gce"), ignore_errors=True)  # version precedente des outils GCE
    shutil.copy(os.path.join(ICI, "outils_figures", "figures_svg.py"), os.path.join(sortie, "scripts", "figures_svg.py"))
    dst = os.path.join(sortie, "scripts", "gce")
    os.makedirs(os.path.join(dst, "inedites"))
    shutil.copy(os.path.join(GCE, "INEDITES_GCE.md"), dst)
    for f in os.listdir(ICI):
        p = os.path.join(ICI, f)
        if os.path.isfile(p) and f.endswith((".py", ".json")) and f != "construire_skill.py":
            shutil.copy(p, os.path.join(dst, "inedites", f))
    shutil.copytree(os.path.join(ICI, "outils_figures"), os.path.join(dst, "inedites", "outils_figures"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    zp = os.path.join(ICI, "concepteur-epreuve-inedite.skill")
    if os.path.exists(zp):
        os.remove(zp)
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, dn, fn in os.walk(sortie):
            dn[:] = [x for x in dn if x != "__pycache__"]
            for f in fn:
                full = os.path.join(dp, f)
                z.write(full, os.path.relpath(full, racine_skill).replace(os.sep, "/"))
    shutil.rmtree(racine_skill)
    print("description", len(DESCRIPTION), "caracteres ;", zp, os.path.getsize(zp), "octets ;", len(zipfile.ZipFile(zp).namelist()), "fichiers")


if __name__ == "__main__":
    sys.exit(main())
