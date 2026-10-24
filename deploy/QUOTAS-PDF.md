# Quotas quotidiens de téléchargement des PDF

Code : `backend/access/quota.py` (règles et commentaires), modèles dans `backend/access/models.py`
(`ReglagesTelechargement`, `CompteurQuota`, `TelechargementPdf`), tests dans `backend/access/test_quota.py`.

## Ce qui est limité
Tout PDF livré par le backend : PDF de cours, sujet des épreuves classiques, sujet des épreuves inédites, fiche et
correction d'un quiz, sujet et corrigé d'une fiche répétiteur. Un seul quota commun. Pages HTML, lecture en ligne,
statut du quota et refus ne consomment rien.

## Règles par défaut (modifiables dans l'admin : « Réglages des téléchargements PDF »)
| Réglage | Défaut |
|---|---|
| Visiteur ou compte sans abonnement actif | 3 PDF par jour |
| Profil avec un abonnement actif (Subscription, Inscription Inédites ou Répétiteur non expirée) | 12 PDF par jour |
| Journée | civile, fuseau `Africa/Douala`, remise à zéro à minuit |
| Nouveaux visiteurs reconnus par réseau et par jour | 40 (au-delà : un quota commun sans cookie) |
| PDF par jour et par réseau (IPv4 exacte, IPv6 /64) | 60 |
| PDF par jour et par bloc (IPv4 /24, IPv6 /48) | 200 |
| Budget global des visiteurs anonymes par jour | 3000 |
| Rétention du journal | 90 jours |

Décompte : une unité = (jour, demandeur, document). Le même PDF redemandé le même jour est gratuit. Toute requête
qui livre des octets (y compris `Range`) crée l'unité. Une coupure après l'envoi consomme le crédit ; une erreur avant
l'envoi le rend. `HEAD` est refusé (405).

## Mise en service
1. Déployer le backend, puis `python manage.py migrate access` (migration 0008, additive, réversible).
2. Rebuild de l'image `caddy` (frontend + `Caddyfile`) : `docker compose build caddy && docker compose up -d caddy`.
   Le `Caddyfile` bloque désormais `/media/sujets_pdf/*` et `/media/sujets_pdf_avant_filigrane/*` (les PDF « sujet » passent
   par `/access/lessons/<id>/sujet.pdf`) et refuse les robots d'IA connus sur les routes de PDF.
3. Vérifier : `curl -s -o /dev/null -w "%{http_code}" https://<domaine>/media/sujets_pdf/x.pdf` → 404 ;
   `curl https://<domaine>/access/telechargements/quota/` → JSON `{"limite":3,...}`.
4. Planifier `python manage.py purger_telechargements` (hebdomadaire).

## Exploitation
- Statistiques : `python manage.py stats_telechargements --jours 7`, ou l'admin (« Compteurs quota » : `refus_*`,
  `quota_atteint`, `identites`, `global_anonyme`).
- Couper les quotas en urgence : décocher « actif » dans les réglages.
- Si le disjoncteur anonyme se déclenche (`refus_budget_global`), c'est un signal d'aspiration : regarder `reseau` /
  `reseau_large` du jour.

## Limites connues
- Si l'objet est sur Spaces avec l'ACL `public-read`, l'adresse CDN d'un ancien sujet reste publique : seul Caddy bloque
  `/media/sujets_pdf/`. Passer ces objets en privé fermera ce chemin.
- Le contenu HTML des cours et des épreuves reste lisible librement (décision produit) ; il n'a qu'un limiteur de débit.
- Un attaquant qui change d'adresse IP sur plusieurs réseaux et crée des comptes vérifiés par SMS peut obtenir plus
  que le quota d'un seul visiteur ; les plafonds réseau, le budget global et le coût des comptes (OTP) bornent l'abus
  sans l'empêcher absolument.
- Les limiteurs de débit (`QuotaThrottle`, `LectureThrottle`) sont en mémoire de chaque processus gunicorn.
