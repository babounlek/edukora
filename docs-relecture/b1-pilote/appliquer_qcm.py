"""
Applique en base les QCM du pilote B1 (conversion SUR PLACE d'items ouverts en QCM).

NE S'EXECUTE PAS SEUL : il faut l'accord explicite de l'utilisateur. Par défaut : simulation (rien n'est écrit).

Usage (dans le conteneur backend) :
    python manage.py shell -c "import os; os.environ['B1_JSON']='/tmp/b1_propositions.json'; exec(open('/tmp/appliquer_qcm.py', encoding='utf-8').read())"
    ... et, pour écrire vraiment : os.environ['B1_APPLIQUER']='1'

Garde-fous :
- un item n'est touché que s'il est encore OUVERTE et VALIDÉ (jamais un item déjà converti ou repassé en brouillon) ;
- `statut`, `est_vitrine`, thème, cursus et figures ne sont JAMAIS modifiés ;
- les quiz déjà joués portent un instantané (quiz.instantane) : l'historique des élèves n'est pas touché ;
- une transaction par item, un rapport ligne à ligne.
"""
import json
import os

from django.db import transaction

from catalog.models import StatutContenu, TypeReponse
from quiz.models import CompetenceItem

chemin = os.environ.get("B1_JSON", "/tmp/b1_propositions.json")
ecrire = os.environ.get("B1_APPLIQUER") == "1"
propositions = json.load(open(chemin, encoding="utf-8"))
print(("ECRITURE" if ecrire else "SIMULATION") + f" : {len(propositions)} propositions lues dans {chemin}")

appliques, ignores = 0, 0
for p in propositions:
    item = CompetenceItem.objects.filter(pk=p["id"]).first()
    if item is None:
        print(f"  #{p['id']} : introuvable, ignoré")
        ignores += 1
        continue
    if item.statut != StatutContenu.VALIDE or item.type_reponse != TypeReponse.OUVERTE:
        print(f"  #{p['id']} : déjà modifié (statut={item.statut}, type={item.type_reponse}), ignoré")
        ignores += 1
        continue
    lettres = [c["lettre"] for c in p["choix"]]
    assert p["reponse_correcte"] in lettres and len(lettres) == 4, p["id"]
    print(f"  #{p['id']} {item.theme.name} : OUVERTE -> QCM (bonne réponse {p['reponse_correcte']})")
    if ecrire:
        with transaction.atomic():
            item.enonce_markdown = p["enonce_markdown"]
            item.corrige_markdown = p["corrige_markdown"]
            item.type_reponse = TypeReponse.QCM
            item.choix = p["choix"]
            item.reponse_correcte = p["reponse_correcte"]
            item.save(update_fields=[
                "enonce_markdown", "corrige_markdown", "type_reponse", "choix", "reponse_correcte", "updated_at",
            ])
    appliques += 1
print(f"{'Appliqués' if ecrire else 'À appliquer'} : {appliques} ; ignorés : {ignores}")
