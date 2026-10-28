"""
Retire (statut REJETE) les cours « systèmes d'équations » en doublon du BEPC : script sûr pour la production.

Simulation par défaut. Variables : B6_JSON (défaut /tmp/b6_retraits.json), B6_APPLIQUER=1 pour écrire,
B6_RESTAURER=<fichier d'avant> pour revenir en arrière (avec B6_APPLIQUER=1 pour écrire).

Usage (conteneur backend) :
    python manage.py shell -c "exec(open('/tmp/retirer_cours.py', encoding='utf-8').read())"

Un cours n'est touché que si TOUT concorde : external_id, titre, matière, et empreinte SHA-256 (titre + contenu)
identique à celle de la base locale relue. Il est ignoré s'il a des lectures ou des marques d'étude (un élève y
revient), ou s'il n'est plus VALIDE. Les ids locaux ne sont jamais utilisés. Rien n'est supprimé : REJETE = retrait.
L'état d'avant est écrit dans un fichier AVANT toute écriture.
"""
import hashlib
import json
import os
from datetime import datetime

from django.db import transaction

from access.models import LectureProgress, MarqueEtude
from catalog.models import Cours, StatutContenu

ecrire = os.environ.get("B6_APPLIQUER") == "1"


def empreinte(c):
    return hashlib.sha256((c.titre + "\x00" + c.content_markdown).encode("utf-8")).hexdigest()


if os.environ.get("B6_RESTAURER"):
    avant = json.load(open(os.environ["B6_RESTAURER"], encoding="utf-8"))
    print(("RESTAURATION" if ecrire else "SIMULATION DE RESTAURATION") + f" : {len(avant)} cours")
    for ligne in avant:
        c = Cours.objects.filter(pk=ligne["pk"], external_id=ligne["external_id"]).first()
        print(f"  {ligne['external_id']} : retour à {ligne['statut']}" if c else f"  {ligne['external_id']} : introuvable")
        if c and ecrire:
            Cours.objects.filter(pk=c.pk).update(statut=ligne["statut"])
else:
    retraits = json.load(open(os.environ.get("B6_JSON", "/tmp/b6_retraits.json"), encoding="utf-8"))
    print(("ECRITURE" if ecrire else "SIMULATION") + f" : {len(retraits)} cours à retirer")
    a_faire = []
    for r in retraits:
        cands = list(Cours.objects.filter(external_id=r["external_id"]).select_related("subject"))
        if len(cands) != 1:
            print(f"  {r['external_id']} : {len(cands)} résultat(s), ignoré")
            continue
        c = cands[0]
        if c.titre != r["titre"] or c.subject.code != r["matiere"] or empreinte(c) != r["sha256"]:
            print(f"  {r['external_id']} : titre, matière ou contenu différents de l'original relu, ignoré")
        elif c.statut != StatutContenu.VALIDE:
            print(f"  {r['external_id']} : déjà {c.statut}, ignoré")
        elif LectureProgress.objects.filter(cours=c).exists() or MarqueEtude.objects.filter(cours=c).exists():
            print(f"  {r['external_id']} : des élèves l'ont lu ou annoté, ignoré (à décider à la main)")
        else:
            print(f"  pk={c.pk} {r['external_id']} : VALIDE -> REJETE")
            a_faire.append(c)
    if ecrire and a_faire:
        fichier = f"/tmp/b6_avant_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json.dump([{"pk": c.pk, "external_id": c.external_id, "statut": c.statut} for c in a_faire], open(fichier, "w", encoding="utf-8"), indent=1)
        print(f"État d'avant sauvegardé : {fichier}")
        for c in a_faire:
            with transaction.atomic():
                Cours.objects.filter(pk=c.pk).update(statut=StatutContenu.REJETE)
    print(f"{'Retirés' if ecrire else 'À retirer'} : {len(a_faire)}")
