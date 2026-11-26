# 19. Audit du tunnel de paiement CamPay (2026-11-26)

Question posée : le paiement CamPay est en place ; où le payeur peut-il encore buter ?

## 1. Verdict

Le chemin nominal est court et propre : prix → compte → un numéro, un bouton, une validation sur le téléphone. Les frictions sont toutes **à côté du chemin nominal** : quand la demande n'apparaît pas sur le téléphone, quand le payeur valide après deux minutes, quand CamPay refuse ou tombe. Dans ces cas, l'écran laisse le payeur seul, et depuis que le paiement manuel est coupé il n'a plus aucune autre porte.

Cinq points à traiter avant de pousser du trafic payant : F1 à F5.

## 2. Ce qui a été regardé, et ce qui ne l'a pas été

- **Production, en visiteur, téléphone 375 × 812** : `/tarifs` → choix BEPC → « Continuer · 1 mois · 2 000 FCFA » → écran de connexion. Articles d'aide « Comment payer » et « Paiement refusé ». `GET /payments/config/` répond `campay_active: true`, `manual_active: false`, `sms_active: true`.
- **Code** : `payments/views.py`, `campay_client.py`, `providers/campay.py`, `models.py`, `rattrapage.py`, `relances/services.py` et `views.py`, `SubscribePage.tsx`, `PricingPage.tsx`, `BandeauReprisePaiement.tsx`, `api/client.ts`, textes `fr.ts`.
- **CamPay** : README et `sdk.py` du SDK Python officiel. La documentation Postman et le portail développeur n'ont pas pu être lus.
- **Non fait** : l'écran de paiement connecté n'a pas été vu à l'écran (Docker local n'a pas démarré, pas de compte en production) ; ses constats viennent du code. **Aucun paiement réel n'a été lancé** : rien ne prouve ici que les identifiants CamPay de production sont acceptés (ils étaient refusés le matin même, HTTP 400).

## 3. Constats

### Forts

| # | Constat | Preuve |
|---|---|---|
| F1 | **Aucune issue quand le paiement échoue.** Paiement manuel coupé : l'écran « Le paiement a échoué » n'offre que « Réessayer ». Pas de WhatsApp, pas de conseil. L'aide en ligne conseille pourtant « fais toi-même le transfert par Orange Money ou MTN MoMo », qui n'existe plus. | `SubscribePage.tsx:983-1001` ; `/aide/paiement-refuse` en prod |
| F2 | **Les erreurs techniques sont affichées telles quelles au payeur.** Le serveur renvoie `str(exc)` : « Échec d'authentification CamPay : {"non_field_errors":[…]} », le message anglais de CamPay sur un numéro refusé, ou « CamPay est injoignable (HTTPSConnectionPool…) ». | `views.py:169`, `campay_client.py:32,54,81` ; `SubscribePage.tsx:406,987` |
| F3 | **L'écran d'attente ne dit pas quoi faire si rien n'apparaît sur le téléphone.** Texte : « Une demande Mobile Money a été envoyée au 6… ». Ni le code à composer, ni le montant, ni le nom du marchand qui s'affichera. Or CamPay renvoie `ussd_code` (« \*126# for MTN or #150\*50# for ORANGE ») et `operator` dans la réponse de `collect` ; ils sont stockés dans `raw_response` et jamais transmis à l'écran. | `views.py:171-174`, `fr.ts:1939-1941` ; README du SDK |
| F4 | **Après deux minutes, la page arrête de regarder.** Qui valide à 2 min 30 reste sur « La confirmation prend plus de temps que prévu ». L'accès ne s'ouvre qu'au rattrapage : une fois par heure, ou quand l'application est rouverte (et pas avant 3 minutes). | `SubscribePage.tsx:47,359-363`, `rattrapage.py:29`, `planifier_relances.py:38` |
| F5 | **Double paiement possible.** « Réessayer » (délai dépassé ou échec), « Revenir au formulaire » et un rechargement de page ramènent au formulaire ; `initiate_payment` crée une nouvelle demande sans regarder s'il en existe une en attente. Deux validations = deux paiements, l'accès est prolongé deux fois, rien ne rembourse. | `views.py:157-161` (aucun contrôle), `SubscribePage.tsx:367-373,940` |

### Moyens

| # | Constat | Preuve |
|---|---|---|
| F6 | **La page des prix annonce le mauvais geste.** Sous le bouton : « puis tu vois le numéro Mobile Money où envoyer ton paiement ». Avec CamPay seul, on ne voit aucun numéro : on saisit le sien. Texte fixe, quel que soit le mode. | Vu en prod ; `fr.ts:460` (`prix.avant_connexion`) |
| F7 | **« Campay » est présenté comme un moyen de paiement.** Étape 1 « Moyen de paiement » : une seule carte, « Campay · Recommandé ». Un parent connaît Orange Money et MTN MoMo, pas CamPay ; et une étape à choix unique n'est pas une étape. Même mot dans le crédit parrainage. | `SubscribePage.tsx:733-770`, `fr.ts:1919-1925` |
| F8 | **Tout numéro en 6xxxxxxxx est accepté.** Un numéro Camtel ou Nexttel part chez CamPay et revient en erreur brute (F2). L'opérateur n'est pas reconnu à la saisie, donc l'écran d'attente ne peut pas donner la bonne consigne (F3). | `SubscribePage.tsx:380` |
| F9 | **Un échec ne dit jamais pourquoi.** Statut `FAILED` lu au sondage : titre seul, aucun texte. Le SDK ne montre pas de champ de motif ; à défaut, un conseil utile (solde, code secret, délai dépassé) manque. | `SubscribePage.tsx:346-348,983-987` |
| F10 | **Le paiement CamPay ne laisse aucune trace dans l'application.** « Mes paiements » ne liste que les transferts déclarés. Le reçu est un SMS et, si l'adresse est confirmée, un e-mail. | `fr.ts:1632` (`pm.note_campay`), `views.py:215-220` |
| F11 | **L'aide en production décrit d'abord le transfert manuel**, sur quatre paragraphes, puis « le paiement automatique, quand il est proposé ». C'est l'inverse de ce que le payeur trouve. | `/aide/comment-payer` en prod |

### Techniques (invisibles aujourd'hui, visibles avec le volume)

| # | Constat | Preuve |
|---|---|---|
| F12 | **Un jeton CamPay est redemandé à chaque appel.** Chaque sondage fait deux requêtes vers CamPay (jeton + statut), soit environ 80 par paiement, avec 25 s de délai maximal cumulé sur un sondage toutes les 3 s. Un CamPay lent empile les requêtes. | `campay_client.py:42-55,87` |
| F13 | **Pas de notification de CamPay vers le serveur.** Tout repose sur le sondage. Le SDK n'en documente pas ; à demander à CamPay (leur tableau de bord propose peut-être une URL de rappel). Elle supprimerait F4 à la racine. | Non vérifié |
| F14 | Une réponse `collect` sans `reference` laisse la transaction « en attente » sans jamais être relue : deux minutes d'attente pour rien. | `providers/campay.py:31`, `views.py:181` |

## 4. Ce qui tient bien

- Le choix (« BEPC · 1 mois · 2 000 FCFA ») suit le visiteur jusqu'à l'écran de connexion, téléphone d'abord, SMS actif.
- Numéro du compte prérempli, durée rappelée et non redemandée, enfant concerné affiché.
- Activation sous verrou, sans double activation ; rattrapage des validations tardives pendant 48 h ; reçu par SMS et e-mail ; relance du paiement abandonné ; bandeau « reprendre mon paiement ».
- Échec du fournisseur remonté à Sentry avec l'étiquette `critical_path: payment`.

## 5. Corrections proposées

**Lot 1 : textes et issues (petit, sans migration)**
1. F2 : messages du serveur traduits en trois phrases pour le payeur (numéro refusé, service indisponible, réessaie) ; le détail part à Sentry seulement.
2. F1 + F9 : écran d'échec avec trois vérifications (solde, code secret, demande expirée) et le lien WhatsApp du support, déjà prérempli ailleurs.
3. F3 : `ussd_code` et `operator` renvoyés par `/payments/initiate/` ; l'écran d'attente affiche le montant et « Rien ne s'affiche ? Compose … », avec un lien d'appel.
4. F6, F7, F11 : phrase de la page des prix selon le mode ; carte « Orange Money ou MTN MoMo » sans étape de choix quand CamPay est seul ; articles d'aide réordonnés, puis `charger_aide` en production.

**Lot 2 : attente et double paiement (moyen)**
5. F4 : après deux minutes, sondage ralenti (toutes les 10 s pendant 10 minutes) au lieu de l'arrêt ; l'écran bascule seul sur le succès.
6. F5 : `initiate_payment` relit d'abord la demande en attente de moins de 10 minutes pour le même enfant et le même plan ; si elle existe, il la renvoie au lieu d'en créer une. L'écran d'abonnement reprend l'attente au rechargement.
7. F8 : opérateur reconnu au préfixe (liste MTN et Orange à faire confirmer), refus clair pour les autres.
8. F10 : paiements CamPay réussis listés dans « Mes paiements ».

**Lot 3 : robustesse**
9. F12 : jeton mis en cache (durée de validité à lire dans la réponse de `/api/token/`).
10. F13 : question à poser à CamPay sur l'URL de rappel.

## 5 bis. Corrections faites le jour même (en local, non committées, non déployées)

| Constat | Ce qui est en place | Où |
|---|---|---|
| F1, F9 | Écran d'échec : le message du serveur, ou à défaut trois vérifications (solde, code secret, demande expirée) et « Un paiement qui échoue n'est pas débité » ; bouton WhatsApp du support, lien vers l'article « paiement refusé ». | `SubscribePage.tsx` |
| F2 | Le serveur ne renvoie plus jamais le texte de l'exception : un code (`paiement_indisponible`, `numero_refuse`, `numero_invalide`) et un message pour le payeur. Le détail part à Sentry. Un numéro refusé ramène au formulaire, message sous le champ. | `providers/base.py`, `campay_client.py`, `views.py`, `SubscribePage.tsx` |
| F3 | `/payments/initiate/` et `/payments/status/` renvoient l'opérateur reconnu par CamPay. L'écran d'attente dit le montant et « Rien ne s'affiche ? Compose \*126# / #150\*50# », avec un bouton d'appel sur téléphone. | `models.py` (`Transaction.operateur`), `views.py`, `SubscribePage.tsx` |
| F4 | Après deux minutes, le sondage continue toutes les 10 s pendant 10 minutes ; l'écran s'ouvre seul sur le succès. Le sondage survit au retour sur le formulaire. | `SubscribePage.tsx` (`pollTransaction`) |
| F5 | `initiate_payment` relit d'abord la demande en attente de moins de 10 minutes (même compte, enfant, plan, numéro) : réussie, elle est la réponse ; échouée, une neuve part ; en attente, elle est rendue avec `deja_en_attente` et l'écran propose « Envoyer une nouvelle demande » (`nouvelle_demande`). Nouvelle route `GET /payments/en-cours/` : l'écran rechargé reprend l'attente. | `views.py`, `urls.py`, `SubscribePage.tsx` |
| F6 | Phrase sous le bouton des prix selon le mode (`prix.avant_connexion_direct`). | `PricingPage.tsx`, `fr.ts`, `en.ts` |
| F7 | CamPay seul : plus d'étape « Moyen de paiement », plus de carte au nom du prestataire ; « Orange Money ou MTN MoMo » et ce qui va se passer. Avec le manuel : la carte s'appelle « Paiement direct ». Le mot « Campay » ne reste que dans les CGU et la politique de confidentialité. | `SubscribePage.tsx`, `fr.ts`, `en.ts` |
| F8 | **Non fait, volontairement** : refuser un numéro d'après son préfixe exige une liste sûre des plages MTN et Orange ; une liste fausse refuserait des payeurs valides. À la place : le refus de CamPay est dit en clair (F2), l'opérateur vient de CamPay (F3), et le numéro est validé et normalisé côté serveur. | `views.py` (`_lire_numero`) |
| F10 | Nouvelle route `GET /payments/mine/` ; « Mes paiements » liste les paiements confirmés (montant, durée, date, opérateur, numéro de reçu). | `views.py`, `serializers.py`, `MesPaiementsPage.tsx` |
| F11 | Articles « Comment payer » et « Paiement refusé » réécrits, demande sur le téléphone d'abord, en français et en anglais. | `backend/aide/articles/` |
| F12 | Jeton CamPay gardé 5 minutes par processus, redemandé une fois s'il est refusé (401 ou 403). | `campay_client.py` |
| F14 | Une réponse `collect` sans référence est une erreur : la transaction passe en échec au lieu d'attendre. | `campay_client.py` |

Reste ouvert : F13 (demander à CamPay s'il existe une URL de rappel).

**Tests** : `payments/test_tunnel_paiement.py` (23 tests), 9 tests de plus dans `SubscribePage.test.tsx` ; suite du client complète verte (1 804). **Non vérifié à l'écran** : Docker n'a pas démarré, l'écran de paiement n'a pas été vu dans un navigateur.

**Déploiement** : aucune migration. Rebuild de `backend` et de `caddy`, puis `charger_aide` en production (les articles sont en base, pas lus depuis les fichiers).

## 6. À faire par toi avant tout

Un paiement réel de bout en bout, une fois depuis un numéro MTN et une fois depuis un numéro Orange, en notant : le nom affiché sur le téléphone, si la demande apparaît seule ou s'il faut composer le code, et le temps entre la validation et l'écran de bienvenue. C'est le seul contrôle que cet audit n'a pas pu faire.
