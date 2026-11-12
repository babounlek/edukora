# 06 - Parcours connecté (complément de l'audit, 2026-11-12, local, mobile 375x812)

Autorisation du user : lecture en base locale du code de connexion des comptes `[TEST]` (aucun compte créé, aucune écriture en dehors du fonctionnement normal du produit). Comptes utilisés : `[TEST] Élève abonné` (id 116, BEPC, e-mail en @exemple.local) et `[TEST] Parent de famille` (id 119, deux profils : Test et Cadet).
Effets de bord en base locale, à connaître : 2 codes de connexion créés et consommés (116 et 119), 1 séance de quiz du compte 116 (session 532, 7 questions, séance du jour validée, XP gagnés). Aucun paiement, aucune déclaration de paiement (je me suis arrêté avant "J'ai effectué le paiement", qui déclenche un SMS dans le produit). Deux tentatives d'envoi d'e-mail vers `@exemple.local` passent par le SMTP configuré en local (smtp.gmail.com) : sans destinataire réel.
Limites : comptes élève libre (117), expiré (118), paiement en attente (127), A Level, session expirée et retour arrière sur les écrans de paiement non rejoués. Simulation, pas un test utilisateur.

## 1. Déroulé et humeur (-2 à +2)
| Étape | Observé | Humeur |
|---|---|---|
| Connexion e-mail (élève) | Saisie de l'adresse, "L'envoi peut prendre quelques secondes...", environ 12 s avant l'écran du code ; champ code en `autocomplete=one-time-code`, `inputmode=numeric`, 6 caractères ; "Valider" → arrivée sur Aujourd'hui | -1 (attente), puis +1 |
| Aujourd'hui | "200 jours avant l'examen · BEPC 2027, le 31 mai", thème du jour "Algorithmique" avec message personnalisé ("Content de te revoir. On reprend en douceur. Tu as raté ce thème il y a 5 jours : 7 minutes pour le fixer"), durée au choix (10, 25, 45 min), objectif de points, série, mini-inédite de la semaine, "À reprendre", progression | +2 (pic) |
| Quiz de la séance | 7 questions, mélange de réponses ouvertes (je vois la correction puis je m'auto-évalue : Réussi / Partiel / Échec) et de QCM | +1 |
| Résultat | "0 / 7", "Pas grave, c'est comme ça qu'on apprend", "Séance du jour validée", "Pour progresser" (revoir le cours, refaire les questions ratées), prochain quiz, mon compte | 0 (voir UX-18) |
| Ma progression | 5 savoirs maîtrisés sur 1 122 (0 %), 14 matières, "Entraînement libre" | 0 |
| Réviser (épreuves) | Liste filtrée d'office sur le cursus de l'élève (293 épreuves BEPC), "Lire le corrigé" partout | +1 |
| Corrigé d'une épreuve payante (BEPC 2025) | Ouvert en entier (21 314 caractères), aucun verrou | +1 |
| Mon compte | Bilan (séances, questions, réussite, série), accès, carnet, partage, rythme, rappels, connexion et sécurité | +1 |
| Connexion parent (e-mail) | Le premier envoi a abouti ; le second a échoué ("Le code n'a pas pu être envoyé pour le moment. Réessaie dans 60 secondes.") ; "J'ai déjà un code" reprend l'adresse saisie et mène au champ code | -1, puis +1 |
| Qui étudie ? | Choix du profil (Test, Cadet), proposition d'un code parent ("Plus tard") | +1 |
| Mes accès | "1 sur 2 enfants ont un abonnement actif", par enfant : formule, jours restants, "Payer pour Cadet" (lien `/tarifs?profil=41`), code parent, code de profil | +2 (pic) |
| Abonnement (cursus 14, 3 mois) | Total 6 000 FCFA, date de fin d'accès, "Tu paies pour : Test", paiement manuel Orange Money ou MTN MoMo : montant, numéro, bénéficiaire, boutons "Copier", "Vérifiée par notre équipe sous 3 heures", "J'ai effectué le paiement" | +1 puis 0 (voir UX-19, UX-20) |
| Mes paiements | État vide expliqué ("Rien à suivre pour l'instant") | +1 |

## 2. Constats (complètent 01-constats.md ; IDs UX-18 à UX-22)
| ID | Constat | Sévérité | Impact |
|----|---------|----------|--------|
| UX-18 | **RETIRÉ après vérification dans le code (2026-11-12, Phase d'amélioration)** : le « +0 points » est le point de départ du compteur animé du résultat (`useCompteur`, `requestAnimationFrame`) ; le navigateur intégré de l'audit, en arrière-plan, ne fait pas tourner les animations, d'où la valeur figée à 0 (le serveur renvoie bien réponses + bonus de séance, `quiz/xp.py: bilan_session`). Artefact de mesure, pas un défaut du produit. Reste une **hypothèse** : les 4 questions auto-évaluées "Partiel" comptent pour 0 dans "0 / 7" et "Refaire les 7 questions ratées" les inclut (décourageant ; choix de conception à valider). | Cosmétique | Rétention |
| UX-19 | **Fait** : demande de code par e-mail : environ 12 s d'attente au premier envoi, échec au second avec "Réessaie dans 60 secondes". En local, l'adresse est en @exemple.local, donc l'échec est attendu ; mais l'envoi est synchrone dans la requête (délai maximal réglé à 10 s). **Hypothèse à vérifier en production** : si le SMTP est un compte Gmail (limite d'envoi quotidienne du fournisseur, à confirmer) ou si l'envoi reste lent, des élèves en 3G attendront ou n'auront pas de code au pic du lancement ; plafonds applicatifs : 60 demandes d'e-mail par IP et par heure (risque si des opérateurs partagent une même adresse IP, hypothèse), 5 000 e-mails par jour au total. | Majeur (hypothèse, non vérifiable en local) | Conversion, rétention, support |
| UX-20 | **Fait** : un parent qui suit /tarifs → "Continuer" arrive sur "Abonnement pour Test" (profil actif, déjà abonné au BEPC : "Ton accès actuel est prolongé jusqu'au 23 août 2027") alors que l'enfant à abonner est Cadet. Le bandeau "Tu paies pour : Test" informe, il n'y a pas de sélecteur d'enfant ; le bon chemin existe ("Payer pour Cadet" dans Mes accès → `/tarifs?profil=41`). **Hypothèse** : erreur de paiement possible pour un parent qui n'a pas changé de profil ; déjà noté par le projet comme choix de conception. | Mineur | Conversion, litiges de paiement |
| UX-21 | **Fait** : à l'écran de paiement, "Le paiement automatique est momentanément indisponible. Paiement manuel : ..." (en local `CAMPAY_ACTIVE` est faux). **À vérifier en production** : si le paiement automatique y fonctionne, UX-04 (attente de 3 h) devient secondaire ; sinon, ce message affiché à tout payeur au lancement fait douter de la fiabilité. | À vérifier en prod | Conversion, confiance |
| UX-22 | **Hypothèse** : l'anneau de progression affiche "0 %" avec 5 savoirs maîtrisés sur 1 122 ; démotivant les premières semaines (le texte "44 thèmes déjà abordés" compense). | Cosmétique | Rétention |
| (non retenu) | Réglages "Ta séance du jour par e-mail : ajoute et confirme d'abord ton e-mail" alors que l'e-mail est le moyen de connexion : **artefact du jeu de données de test** (`email_verified` faux pour les comptes semés), pas un défaut du produit (un compte créé par e-mail est marqué vérifié). | - | - |

## 3. Ce qui marche bien (connecté)
Séance du jour personnalisée avec compte à rebours jusqu'à la date d'examen ; ton encourageant et informatif ; auto-évaluation honnête des réponses ouvertes ; écran de résultat avec étapes suivantes ; liste d'épreuves filtrée d'office sur son cursus ; compte avec bilan chiffré, rythmes, sons, rappels ; "J'ai déjà un code" ; profils d'enfants avec code parent ; "Mes accès" par enfant avec "Payer pour <enfant>" ; page de paiement manuel claire (montant, bénéficiaire, copier, délai) ; "Mes paiements" explicite.

## 4. Satisfaction (notée à chaud, simulation, confiance faible)
- **Élève abonné (BEPC)** : Q1 4/5 (pic : séance du jour personnalisée avec compte à rebours), Q2 2/5, Q3 4/5, revenir "demain", recommander 7/10, "je continue de payer" : oui, avec la séance (6 140 questions) ; creux : résultat "0 / 7" (les réponses "Partiel" comptent 0).
- **Parent** : Q1 4/5 (contre 3/5 en visiteur), Q3 4/5 (Mes accès par enfant), payer : peut-être oui, 6/10 (contre 5) ; ce qui manque : voir le délai réel d'activation et une confirmation automatique ; creux : /tarifs mène au profil déjà abonné (UX-20) et message "paiement automatique indisponible" (UX-21).
- Impact sur l'agrégat global (4 personas visiteur + 2 connectés) : revenir 6,8, recommander 6,3, payer 5,3. La séance du jour **démontre** la valeur une fois connecté : la barrière est de la montrer avant la connexion (F1).

## 5. Conséquences pour la feuille de route
- R1 s'étend : confirmer en production **le fournisseur SMTP et sa capacité**, les plafonds OTP (e-mail et SMS) au regard du trafic attendu, et l'état de **CamPay** (paiement automatique).
- R7 est **réalisé en partie** (élève abonné et parent, jusqu'à l'écran de paiement) ; restent à rejouer en recette : déclaration de paiement et activation, élève libre / expiré, session expirée.
- Ajouts à "juste après" : sélecteur d'enfant à l'abonnement (UX-20).
