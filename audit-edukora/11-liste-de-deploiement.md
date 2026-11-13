# 11 - Liste de déploiement (état du dépôt au 2026-11-13, SHA 796ac60a)

Cases à cocher, dans l'ordre. Serveur : `/srv/edukora`. Déploiement : workflow GitHub « deploy » (SHA), qui lance `deploy/deploy.sh`.
Le SHA ci-dessus contient aussi le travail d'autres sessions (tarif du 2e enfant, essai d'inédite sans compte, « Mes erreurs ») : relire ce qui part avant de déployer.

## 0. Avant
- [ ] Aucun lot de contenu en cours (`deploy.sh` refuse sinon : verrou `/srv/edukora-lots/.sync.lock`).
- [ ] Les actions GitHub `release.yml` (construction des images du SHA) et `ci.yml` sont vertes.
- [ ] Choisir une heure creuse : les migrations tournent avant la bascule.

## 1. Migrations qui partiront (si la production ne les a pas déjà)
Repérées dans le dépôt depuis le 1er novembre. Toutes ajoutent des tables ou des colonnes ; `deploy.sh` les applique après une sauvegarde Postgres.
- `aide 0001`, `analytics 0016-0017`, `catalog 0069-0070` (sessions d'examen 2027, musique et travail manuel), `payments 0014` (mois), `quiz 0022`, `subscriptions 0026-0027` (tarif au mois), `users 0019` (chrono quiz), **`users 0020` (champ `est_invite`)**.
- [ ] Sur le serveur, avant : `docker compose exec backend python manage.py showmigrations | grep "\[ \]"` pour voir celles qui manquent réellement.

## 2. Déployer
- [ ] Workflow « deploy » avec le SHA, ou `deploy/deploy.sh <SHA>` sur le serveur.
- [ ] `curl -s https://edukora.africa/healthz` répond la version déployée.
- [ ] `docker compose ps` : db, backend, caddy, relances, backup en marche ; `docker compose logs --tail 50 backend` sans erreur.

## 3. Après le déploiement, dans cet ordre
```bash
cd /srv/edukora
export COMPOSE_FILE=docker-compose.yml:docker-compose.prod.yml
```
- [ ] **PDF de sujet** (une seule fois, montants retirés) : essai sur un sujet, puis tout en arrière-plan.
```bash
docker compose exec backend python manage.py shell -c "from catalog.models import Lesson; print(Lesson.objects.get(slug='mathematiques-bepc-2026').id)"
docker compose exec backend python manage.py generate_sujet_pdfs --lesson <ID> --force
docker compose exec -d backend sh -c "python manage.py generate_sujet_pdfs --force > /tmp/pdf.log 2>&1"
docker compose exec backend tail -f /tmp/pdf.log
```
  Télécharger un PDF : le bas de page ne doit plus afficher de montant. Ouvrir aussi un PDF de cours, d'inédite et de fiche (aucun prix attendu).
- [ ] **Invités** (essai d'inédite sans compte) : planifier la purge, par exemple hebdomadaire : `docker compose exec backend python manage.py purger_invites` (voir la note du chantier).
- [ ] **Recherche** : si des contenus ont changé, `docker compose exec backend python manage.py indexer_recherche`.

## 4. Vérifier en production (depuis votre poste)
```bash
curl -s -A "Googlebot/2.1" https://edukora.africa/cm/examens/bepc | head -c 800
curl -s -A "Googlebot/2.1" -o /dev/null -w "%{http_code}\n" https://edukora.africa/cm/examens/inconnu
curl -s -A "Googlebot/2.1" https://edukora.africa/cm/epreuves/mathematiques-bepc-2026 | grep -c "Rappel de m"
curl -s -A "Googlebot/2.1" https://edukora.africa/cm/epreuves/mathematiques-bepc-2025 | grep -c "Rappel de m"
curl -s https://edukora.africa/sitemap-1.xml | grep -c "examens"
```
Attendu : la page d'examen en 200 avec titre et texte ; `404` pour l'examen inconnu ; plusieurs occurrences pour l'épreuve libre ; `0` pour la payante ; des entrées « examens » dans le sitemap (elles peuvent être dans le fichier 2 ou 3).
- [ ] Navigateur, sur mobile : `/cm`, `/cm/examens/bepc`, une fiche d'épreuve (fil d'Ariane), `/tarifs`, `/connexion` après « Continuer ».
- [ ] CLS proche de 0 sur l'accueil et une épreuve (script de `07-correctifs-appliques.md`).

## 5. Search Console
- [ ] Sitemap `https://edukora.africa/sitemap.xml` envoyé.
- [ ] Inspection d'URL sur : accueil, `/cm/examens/bepc`, `/cm/examens/bac-d`, une épreuve libre, `/tarifs`.

## 6. À vérifier une fois (point L1)
- [ ] Redirections : `curl -sI http://edukora.africa/` et `https://www.edukora.africa/` vers `https://edukora.africa/`.
- [ ] `docker compose exec backend printenv EMAIL_HOST EMAIL_PORT CAMPAY_ACTIVE` : fournisseur d'e-mails (limite d'envoi quotidienne), paiement automatique actif ou non.
- [ ] Déjà vérifié le 2026-11-12 : `x-robots-tag: index, follow`, sitemap en `https://edukora.africa`.

## 7. Retour arrière
- Images : `deploy/rollback.sh` (voir `deploy/README-TUNNEL.md`). Un retour d'images ne défait pas les migrations (elles sont additives).
- PDF : une régénération se refait avec la même commande ; rien d'irréversible.
