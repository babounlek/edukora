# 08 - Plan de mise en œuvre jusqu'au lancement (mardi 2026-12-01) et au-delà

Date : jeudi 2026-11-12 (J-19). Ce plan transforme la feuille de route (02) en lots livrables : chaque lot a un responsable, des étapes, un critère de validation, un retour arrière et ses dépendances. Efforts : S ≤ 1 jour, M = 2 à 3 jours, L = 4 jours ou plus. Estimations à confirmer par l'équipe.
Légende des responsables : **Vous** (accès production, décisions, équipe), **Claude** (code, tests, vérifications en local), **Les deux**.

## 0. Principes
1. **Un lot = un commit = un déploiement** : on déploie par petits lots, jamais en bloc, pour pouvoir revenir en arrière lot par lot (`git revert` du commit + rebuild).
2. **Gel du code le vendredi 27 novembre**. Du 28 au 30 : recette, mesures, aucune nouvelle fonction. Seuls les correctifs de blocage passent.
3. **Chaque lot a une preuve** : une mesure ou une commande à relancer (voir les critères). Pas de lot "terminé" sans elle.
4. **Aucune action de production sans votre accord explicite** (déploiement, Search Console, données).

## 1. Calendrier
| Jour | Lots | Qui |
|---|---|---|
| Ven 13 nov | L0 décisions, L1 vérifications de production | Vous |
| Lun 16 - mar 17 | L2 déploiement du lot déjà committé et réparation des 2 tests ; démarrage de L3 (pages par cursus) | Les deux |
| Mer 18 - ven 20 | L3 pages par cursus (livraison du MVP) ; L4 conversion parent (petits correctifs) | Claude, vous relisez |
| Lun 23 - mer 25 | L3 déployé et mesuré ; L5 recette du parcours connecté et du paiement | Les deux |
| Jeu 26 - ven 27 | L6 performance et SEO secondaire ; **gel du code vendredi soir** | Claude |
| Sam 28 - lun 30 | L7 recette finale, Search Console, permanence paiement | Vous (Claude en appui) |
| Mar 1er déc | Lancement, L8 surveillance | Vous |

## 2. Lots

### L0 - Décisions (vous, vendredi 13)
| Décision | Options | Recommandation | Débloque |
|---|---|---|---|
| D1 Chemin canonique des épreuves GCE | (a) garder le double adressage FR/EN (actuel, documenté dans `prerendu.py`), (b) chemin anglais canonique, l'URL française redirige ou pointe en canonical | (b) : un contenu = une URL ; garde l'accès par l'URL française pour les élèves | L3 (sitemap), SEO-04 |
| D2 Titles avec "corrigé" | oui / non | oui pour les épreuves de type corrigé, à l'identique côté moteurs et navigateur | lot L6 |
| D3 Permanence d'activation des paiements du 1er au 3 décembre | qui, quels créneaux | une personne nommée, délai cible ≤ 3 h, suivi dans un tableau partagé | L7, UX-04 |
| D4 Forme des pages par cursus | URL (ex. `/cm/annales/bepc`), contenu minimal | voir L3 | L3 |
Critère : les quatre décisions sont écrites (même une ligne chacune).

### L1 - Vérifier la production (vous, vendredi 13, S)
Aucune modification, des constats seulement. Résultat à noter dans un fichier partagé.
1. `curl -sI https://edukora.africa/` : pas de `noindex` dans `X-Robots-Tag` (`ROBOTS_TAG` du `.env` de production).
2. `curl -s https://edukora.africa/sitemap.xml | head -c 400` : les `<loc>` commencent par `https://edukora.africa`.
3. `curl -sI http://edukora.africa/` et `https://www.edukora.africa/` : redirection vers l'adresse canonique.
4. En-têtes de compression : `curl -sI -H "Accept-Encoding: br" https://edukora.africa/assets/<fichier>.js` : présence de `br` ou `gzip`.
5. **E-mail (UX-19)** : fournisseur SMTP de production, limite d'envoi quotidienne du fournisseur, `EMAIL_CODE_MAX_PER_IP_PER_HOUR` (60) et `EMAIL_CODE_DAILY_GLOBAL_CAP` (5 000) face au trafic attendu ; test d'envoi réel à votre propre adresse : délai mesuré.
6. **CamPay (UX-21)** : le paiement automatique est-il actif en production ? Si oui, UX-04 devient secondaire ; si non, le message "momentanément indisponible" s'affichera à chaque payeur.
7. Search Console : propriété vérifiée, sitemap envoyé.
Critère : les 7 points ont une valeur écrite. Retour arrière : sans objet.
Risque : un `noindex` oublié (Bloquant) ; une limite d'envoi dépassée le jour J (Majeur).

### L2 - Déployer le lot déjà committé (Les deux, lundi 16 - mardi 17, S)
Contenu : commit `c45367cc` (CLS, descriptions, corrigé libre pour les moteurs, rappel du choix à la connexion).
1. **Claude** : mettre à jour les 2 tests `catalog.test_pdf_langue` (attendent "15 000 FCFA", le PDF annonce "2 000 FCFA par mois") et relancer les suites backend et frontend.
2. **Vous** : rebuild du backend et de l'image `caddy`, mise en ligne.
3. **Les deux** : `curl -A "Googlebot/2.1"` sur une épreuve libre (corrigé présent, canonical `/lire`) et une payante (aucun corrigé) ; mesure du CLS sur `/tarifs` et une épreuve ; demande d'inspection d'URL sur 2 ou 3 épreuves libres.
Critère : les trois vérifications passent en production. Retour arrière : `git revert c45367cc` puis rebuild.
Risque : une épreuve vitrine mal choisie expose son corrigé aux moteurs : c'est voulu, mais relire la liste des épreuves `est_vitrine` avant le déploiement (une par cursus d'après le modèle).

### L3 - Pages d'atterrissage par cursus (Claude, du 16 au 25, L) - SEO-02
**Pourquoi** : aucune page indexable pour "annales BEPC Cameroun", "BAC D annales corrigées". C'est le plus gros levier d'acquisition.
**MVP (avant le gel)** : une page par cursus (11 francophones + GCE O Level + GCE A Level). La version par matière vient après le lancement.
Étapes :
1. **Spécification (0,5 j)** : URL française et anglaise (segments partagés dans `segments-url.json`, lu aussi par Caddy), contenu minimal : `h1`, paragraphe d'introduction, nombre d'épreuves et de cours, liste des épreuves récentes (avec corrigé libre signalé), lien vers "thèmes qui tombent" et quiz gratuit, appel à l'abonnement. Validation par vous (D4).
2. **Backend (1 j)** : point d'accès public qui renvoie les chiffres et la liste du cursus ; extension de `prerendu.py` (nouveau genre de page, canonical, hreflang, titre, description) ; vrai 404 pour un cursus inconnu.
3. **Caddy (0,5 j)** : ajouter le nouveau genre à l'expression de chemin des robots moteurs et des aperçus de partage (`@robots_moteurs`, `@robots_apercu`), qui énumère aujourd'hui `epreuves|cours|...`.
4. **Frontend (1,5 j)** : page React, titre et description propres (`useSeo`), liens depuis l'accueil, les listes et le pied de page (maillage), canonical dans `BalisesDeRoute`.
5. **Sitemap (0,5 j)** : ajouter les pages (FR et EN, hreflang).
6. **Tests (1 j)** : prérendu (200 avec contenu, 404 si inconnu), sitemap, composant, cohérence des segments d'URL.
7. **Déploiement et mesure** : `curl -A Googlebot` sur les 13 pages ; inspection d'URL dans la Search Console ; ajout au sitemap soumis.
Critère : chaque page répond 200 pour Googlebot avec du texte (≥ 200 mots hors liste), un canonical propre, est listée au sitemap ; le filtre `?cursus=` garde son canonical vers la page de liste. Retour arrière : retirer les URLs du sitemap et `git revert`.
Dépendances : L2 (même chaîne de déploiement), D1 (si le sitemap GCE change), D4.
Risque : effort sous-estimé si la page demande de la rédaction ; garde-fou : le MVP n'exige que du contenu calculé (chiffres, listes).

### L4 - Conversion du parent (Claude, du 18 au 20, S à M) - UX-03, 05, 18, 20
Quatre petits correctifs indépendants, un commit chacun :
1. **UX-20** : sélecteur d'enfant sur la page d'abonnement quand le compte a plusieurs profils (ou, au minimum, avertissement quand le profil actif est déjà abonné au cursus choisi).
2. **UX-03** : bloc "Parents" sur l'accueil (prix, mode de paiement, "Montrer à mes parents") ; texte validé par vous.
3. ~~UX-18~~ : **retiré**, le "+0 points" était un artefact de mesure (compteur animé, voir 06). Reste à décider avec vous si une réponse "Partiel" doit compter comme à moitié juste dans le score affiché.
4. **UX-05** : test A/B ou réglage de l'ordre téléphone / e-mail à la connexion (décision après les données du lancement, pas avant).
Critère : tests existants verts + test par correctif ; relecture visuelle sur mobile 375 px. Retour arrière : `git revert` par commit.

### L5 - Recette du parcours connecté et du paiement (Les deux, du 23 au 25, M) - R7, UX-04
À faire dans un environnement de recette ou en local, jamais avec un paiement réel :
1. Comptes de test : élève libre, expiré, abonné, parent (déjà présents dans `seed_donnees_test`).
2. Parcours : inscription par e-mail et par téléphone, séance du jour, quiz, déclaration de paiement, activation par l'équipe, accès ouvert, session expirée, retour arrière sur le paiement.
3. **La déclaration de paiement envoie un SMS** : la faire uniquement avec un numéro de test que vous contrôlez, ou la décrire sans l'exécuter.
4. Mesurer le délai réel d'activation avec l'équipe qui assurera la permanence.
Critère : parcours complet sans erreur ; délai d'activation ≤ 3 h dans la simulation ; notes écrites. Retour arrière : sans objet.

### L6 - Performance et SEO secondaire (Claude, jeudi 26 - vendredi 27, M)
Dans cet ordre, chacun indépendant :
1. **Bandeau "Choisis ton examen"** : réserver sa hauteur pendant le chargement (CLS résiduel ≈ 0,10) ; décider du comportement si la liste ne charge pas (pas de trou vide).
2. **Titles avec "corrigé"** (si D2 = oui) : prérendu et navigateur à l'identique.
3. **Données structurées** : Organization (accueil), BreadcrumbList et fil d'Ariane sur épreuves et cours.
4. **Sitemap** : ajouter `/cm/themes-frequents` et `/a-propos`.
5. **Cache et compression (infrastructure)** : brotli si absent en production (L1), cache des images `/media` à 1 jour minimum.
Critère : CLS ≤ 0,1 sur accueil, épreuve, tarifs ; titles et JSON-LD vérifiés par `curl` ; test des résultats enrichis. Retour arrière : par commit.
Gel : tout ce qui n'est pas terminé le vendredi 27 passe en "après lancement".

### L7 - Recette finale et préparation du jour J (vous, du 28 au 30)
1. Rejouer les commandes de L1 et les mesures de L2/L3 sur la production.
2. Search Console : sitemap soumis, 5 URLs inspectées (accueil, une épreuve libre, une page de cursus, une page GCE, `/tarifs`).
3. Permanence d'activation (D3) : planning, accès administrateur, numéro WhatsApp joignable, message d'attente prêt.
4. Tableau de suivi du jour J : inscriptions, codes envoyés et échecs d'envoi, paiements déclarés et activés, erreurs 5xx.
5. Plan de repli : qui décide, comment revenir au commit précédent.
Critère : liste cochée et datée.

### L8 - Après le lancement (décembre)
| Lot | Contenu |
|---|---|
| L8a | Pages par matière (cursus × matière) et enrichissement de contenu ; 404 serveur pour les routes inconnues ; maillage interne dans le HTML des moteurs |
| L8b | Mesure réelle : LCP et INP sur la production (PageSpeed Insights, données de terrain) |
| L8c | Échantillon de la séance du jour pour un visiteur (F1), message de résumé pour le parent (F3), pages éditoriales pour parents (F4) |
| L8d | 5 à 8 entretiens courts avec de vrais élèves et parents sur mobile ; comparer aux scores simulés |
| L8e | Revue J+7 : entonnoir (visite, connexion, paiement déclaré, activation), échecs d'envoi de code, retours support |

## 3. Chemin critique et risques
- **Chemin critique** : L1 → L2 → L3 (le plus long) → L7. Si L3 glisse, on livre le MVP réduit (cursus francophones seulement) et le reste en décembre.
- **Risque n°1** : configuration de production (L1). À traiter vendredi 13, car tout le reste en dépend.
- **Risque n°2** : envoi du code par e-mail au pic (UX-19). Pistes si L1 le confirme : envoi asynchrone, second fournisseur, ou authentification par téléphone mise en avant ; à chiffrer seulement si L1 le justifie.
- **Risque n°3** : permanence d'activation (D3) non assurée.
- **Risque n°4** : charge de relecture de votre côté (textes de L3 et L4) ; fixer une relecture rapide (24 h).

## 4. Ce que je peux démarrer dès votre accord
1. L2, étape 1 : réparer les 2 tests `test_pdf_langue` (S).
2. L3, étape 1 : rédiger la spécification des pages par cursus pour votre validation.
3. L6, étape 1 : bandeau "Choisis ton examen".
