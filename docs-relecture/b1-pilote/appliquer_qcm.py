"""
Applique en base les QCM du pilote B1 (conversion SUR PLACE d'items ouverts en QCM). Version 2, sûre pour la production.

NE S'EXECUTE PAS SANS L'ACCORD de l'utilisateur. Par défaut : SIMULATION (rien n'est écrit).

Variables d'environnement :
    B1_JSON        propositions (défaut /tmp/b1_propositions.json)
    B1_ORIGINAUX   empreintes des versions d'origine (défaut /tmp/b1_originaux.json)
    B1_APPLIQUER=1 écrire vraiment (sinon simulation)
    B1_RESTAURER=<fichier d'avant>  remet les lignes d'un fichier d'avant (retour arrière), avec B1_APPLIQUER=1 pour écrire

Usage (dans le conteneur backend) :
    python manage.py shell -c "exec(open('/tmp/appliquer_qcm.py', encoding='utf-8').read())"

Pourquoi une v2 : les identifiants (pk) d'une base locale ne désignent PAS les mêmes lignes en production, et les
external_id « cqc-<thème>-<difficulté>-<n> » ne contiennent pas la matière (collisions connues). Un item n'est donc
modifié que si TOUT concorde : external_id, matière Mathématiques, thème, et empreinte SHA-256 de (énoncé + corrigé)
identique à celle de la version d'origine de la base locale. Sinon il est ignoré et signalé : jamais de modification
d'un item que le pilote n'a pas relu.

Garde-fous : seuls les items OUVERTE et VALIDÉS sont touchés ; statut, est_vitrine, thème, cursus et figures ne sont
JAMAIS modifiés ; les quiz déjà joués portent un instantané (l'historique des élèves n'est pas touché) ; une
transaction par item ; AVANT toute écriture, l'état d'origine des lignes concernées est écrit dans un fichier
(retour arrière possible) ; rapport ligne à ligne.
"""
import hashlib
import json
import os
from datetime import datetime

from django.db import transaction

from catalog.models import StatutContenu, TypeReponse
from quiz.models import CompetenceItem

ecrire = os.environ.get("B1_APPLIQUER") == "1"
CHAMPS = ["enonce_markdown", "corrige_markdown", "type_reponse", "choix", "reponse_correcte", "updated_at"]


def empreinte(item):
    return hashlib.sha256((item.enonce_markdown + "\x00" + item.corrige_markdown).encode("utf-8")).hexdigest()


# ------------------------------------------------------------------ retour arrière
if os.environ.get("B1_RESTAURER"):
    avant = json.load(open(os.environ["B1_RESTAURER"], encoding="utf-8"))
    print(("RESTAURATION" if ecrire else "SIMULATION DE RESTAURATION") + f" : {len(avant)} lignes dans {os.environ['B1_RESTAURER']}")
    for ligne in avant:
        item = CompetenceItem.objects.filter(pk=ligne["pk"], external_id=ligne["external_id"]).first()
        if item is None:
            print(f"  pk={ligne['pk']} {ligne['external_id']} : introuvable, ignoré")
            continue
        print(f"  pk={item.pk} {ligne['external_id']} : retour à l'état d'avant ({ligne['type_reponse']})")
        if ecrire:
            with transaction.atomic():
                item.enonce_markdown, item.corrige_markdown = ligne["enonce_markdown"], ligne["corrige_markdown"]
                item.type_reponse, item.choix, item.reponse_correcte = ligne["type_reponse"], ligne["choix"], ligne["reponse_correcte"]
                item.save(update_fields=CHAMPS)
else:
    chemin = os.environ.get("B1_JSON", "/tmp/b1_propositions.json")
    originaux = json.load(open(os.environ.get("B1_ORIGINAUX", "/tmp/b1_originaux.json"), encoding="utf-8"))
    propositions = json.load(open(chemin, encoding="utf-8"))
    print(("ECRITURE" if ecrire else "SIMULATION") + f" : {len(propositions)} propositions lues dans {chemin}")

    # 1. Résolution et contrôles, SANS rien écrire.
    a_faire, ignores = [], []
    for p in propositions:
        ref = originaux[str(p["id"])]
        candidats = list(CompetenceItem.objects.filter(external_id=ref["external_id"]).select_related("subject", "theme"))
        if len(candidats) != 1:
            ignores.append((p["id"], f"external_id {ref['external_id']} : {len(candidats)} résultat(s), ignoré"))
            continue
        item = candidats[0]
        if item.subject.code != "MATHS" or item.theme.name.lower() != p["theme"].lower():
            ignores.append((p["id"], f"{ref['external_id']} : matière/thème différents ({item.subject.code}/{item.theme.name}), ignoré"))
        elif item.statut != StatutContenu.VALIDE or item.type_reponse != TypeReponse.OUVERTE:
            ignores.append((p["id"], f"{ref['external_id']} : déjà modifié (statut={item.statut}, type={item.type_reponse}), ignoré"))
        elif empreinte(item) != ref["sha256"]:
            ignores.append((p["id"], f"{ref['external_id']} : le contenu diffère de l'original relu en pilote, ignoré"))
        else:
            lettres = [c["lettre"] for c in p["choix"]]
            assert p["reponse_correcte"] in lettres and len(lettres) == 4, p["id"]
            a_faire.append((item, p))
    for pk, msg in ignores:
        print(f"  [{pk}] {msg}")
    for item, p in a_faire:
        print(f"  pk={item.pk} {item.external_id} : OUVERTE -> QCM (bonne réponse {p['reponse_correcte']})")

    # 2. Écriture : d'abord l'état d'avant dans un fichier, puis une transaction par item.
    if ecrire and a_faire:
        fichier = f"/tmp/b1_avant_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json.dump(
            [{"pk": i.pk, "external_id": i.external_id, "type_reponse": i.type_reponse, "choix": i.choix,
              "reponse_correcte": i.reponse_correcte, "enonce_markdown": i.enonce_markdown,
              "corrige_markdown": i.corrige_markdown} for i, _ in a_faire],
            open(fichier, "w", encoding="utf-8"), ensure_ascii=False, indent=1,
        )
        print(f"État d'avant sauvegardé : {fichier}")
        for item, p in a_faire:
            with transaction.atomic():
                item.enonce_markdown = p["enonce_markdown"]
                item.corrige_markdown = p["corrige_markdown"]
                item.type_reponse = TypeReponse.QCM
                item.choix = p["choix"]
                item.reponse_correcte = p["reponse_correcte"]
                item.save(update_fields=CHAMPS)
    print(f"{'Appliqués' if ecrire else 'À appliquer'} : {len(a_faire)} ; ignorés : {len(ignores)}")
