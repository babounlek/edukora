# Revendeurs Edukora — cahier des charges du module

État : projet, rien n'est codé. Rédigé le 2026-10-26 à partir des décisions du fondateur et d'une lecture du code existant (`payments`, `subscriptions`, `users`).

## 1. Décisions arrêtées

| Sujet | Décision |
|---|---|
| Cibles | Commerciaux, répétiteurs, écoles et centres |
| Rémunération | Commission après chaque vente, jamais de stock ni de codes prépayés |
| Taux de base | 14 % du montant encaissé |
| Durée | 12 mois : toutes les ventes du compte attribué, y compris les enfants supplémentaires et les add-ons |
| Palier de bonus | Oui, réservé aux commerciaux (valeurs proposées au § 3, à confirmer) |
| Argent | Le revendeur n'encaisse jamais pour Edukora : le client paie Edukora directement (Campay ou Mobile Money manuel) |

Repères chiffrés au tarif actuel (15 000 F le 1er enfant, 12 000 F chaque enfant supplémentaire) :

| Vente | 14 % | 17 % (palier) |
|---|---|---|
| 15 000 F | 2 100 F | 2 550 F |
| 12 000 F | 1 680 F | 2 040 F |

## 2. Ce que le code fournit déjà

- `User.referral_code` et `User.referred_by` (`users/models.py`) : un code est saisi à l'inscription par les trois chemins (OTP téléphone, e-mail, Google), champ `referral_code` limité à 10 caractères.
- Le **parrainage est gelé depuis le 2026-09-28** (`subscriptions/models.py`, `recompenser_parrainage`) : plus aucune récompense n'est versée, seuls les anciens crédits restent dépensables. Il n'y a donc **aucun conflit de double récompense** à gérer aujourd'hui. Si le parrainage est un jour réactivé, il faudra décider qu'une vente donne une récompense **ou** une commission, jamais les deux.
- Deux chemins de paiement qui convergent chacun en un point unique :
  - `Transaction._confirmer_succes` (Campay) ;
  - `ManualPayment.approve` (paiement manuel validé par un admin).
  Les deux sont atomiques, verrouillés et idempotents. C'est là qu'on branche la commission.
- `ManualPayment.declared_ip`, `payer_phone_number` et `reviewed_by` servent aux contrôles anti-fraude.
- `?ref=` est **déjà utilisé** pour tracer l'origine des liens des PDF (`fiches/pdf.py`). Le lien revendeur utilisera donc `?rev=CODE`, pour ne rien mélanger.

## 3. Règles de commission

1. **Attribution.** Un compte est rattaché à un revendeur par son code, à l'inscription. Rattachement tardif possible tant que le compte n'a **aucun paiement validé** (champ « Code revendeur » au moment de payer). Ensuite l'attribution est figée ; seul un admin peut la corriger, avec un motif.
2. **Base de calcul.** Le montant réellement encaissé :
   - `Transaction.amount` (déjà net du crédit parrainage) ;
   - `ManualPayment.amount_declared` une fois validé par l'admin. Un paiement dont le montant déclaré diffère du montant attendu est mis en vérification.
   Un achat couvert à 100 % par du crédit (montant 0) ne donne aucune commission.
3. **Fenêtre.** Tous les paiements validés dans les 12 mois suivant la date d'attribution, tous types de plan (`ABONNEMENT`, `ADDON_REPETITEUR`).
4. **Taux.** 14 % pour tout revendeur. Pour un **commercial** uniquement : 14 % jusqu'à la 30e vente du mois civil (fuseau Africa/Douala), **17 % sur les ventes à partir de la 31e**. Le palier est marginal, comme une tranche d'impôt : il ne s'applique pas rétroactivement aux 30 premières ventes. Seuil et taux sont des paramètres de la fiche revendeur, pas du code. Une annulation ne recalcule pas les autres commissions.
5. **Arrondi.** Au franc inférieur.
6. **Acquisition.** Une commission est *en attente* pendant 14 jours après le paiement, puis *acquise*. Pas de tâche planifiée nécessaire : on stocke la date d'acquisition et le statut « en attente » ou « acquise » se déduit de la date.
7. **Annulation.** Un admin peut annuler une commission en attente (remboursement, fraude avérée). Après acquisition, l'annulation n'est possible que pour fraude, et le montant est alors déduit du prochain versement (solde négatif reporté).
8. **Une commission par paiement**, garantie par une contrainte en base (même schéma que `ParrainageRecompense` : exactement une source, `transaction` ou `manual_payment`).

## 4. Modèle de données (nouvelle app `revendeurs`)

**Revendeur**
- `user` (OneToOne, il se connecte avec son compte Edukora)
- `type` : COMMERCIAL, REPETITEUR, ECOLE_CENTRE
- `nom_affiche`
- `code` : 4 à 10 caractères majuscules et chiffres, unique **et vérifié contre `User.referral_code`** (même espace de noms, car le formulaire d'inscription n'a qu'un champ)
- `taux_base_pct` (14), `palier_seuil` et `palier_taux_pct` (null si pas de palier)
- `statut` : EN_ATTENTE, ACTIF, SUSPENDU, RESILIE
- `contrat_accepte_le`
- `operateur_versement` et `numero_versement`
- dates de création et de mise à jour

**AttributionRevendeur** (remplace les deux champs sur `User` prévus au départ : pas de migration sur le modèle utilisateur, pas de dépendance circulaire) : `client` (OneToOne), `revendeur`, `attribue_le`, `source` (INSCRIPTION, PAIEMENT, ADMIN).

**Commission**
- `revendeur`, `client` (User), `plan`
- `transaction` / `manual_payment` (exactement un des deux)
- `base_fcfa`, `taux_pct`, `montant_fcfa`
- `acquise_le`
- `statut` stocké : ACTIVE, ANNULEE, PAYEE
- `motif_annulation`
- `a_verifier` (drapeau de fraude)
- `versement` (FK nullable)

**Versement**
- `revendeur`, `periode`
- `montant_brut`, `frais`, `montant_net`
- `operateur`, `reference_mobile_money`
- `paye_par`, `paye_le`

**Journal** : toute modification d'attribution, d'annulation ou de taux est tracée (qui, quand, motif).

## 5. Points d'accroche dans le code existant

- `Transaction._confirmer_succes` et `ManualPayment.approve` appellent `revendeurs.services.enregistrer_commission(paiement)` après l'activation, dans la transaction atomique existante.
- **Principe de sécurité : une erreur de commission ne doit jamais bloquer l'accès d'un client qui a payé.** L'appel est protégé par un point de sauvegarde, l'erreur est journalisée et signalée à l'admin.
- Résolution du code à l'inscription : les trois fonctions d'inscription cherchent d'abord un `Revendeur.code` actif, puis `User.referral_code`. Le champ `referral_code` du formulaire reste le même, avec la même limite de 10 caractères.
- Lien de partage : `/?rev=CODE`, conservé 30 jours côté navigateur, appliqué à l'inscription. Les aperçus de lien (OG) ne changent pas.

## 6. Contrôles anti-fraude

La commission n'est versée que sur un paiement réellement validé, et la validation manuelle sert déjà de barrière. À ajouter :

- **Auto-achat bloqué** : numéro du client, numéro payeur ou numéro de versement identique à celui du revendeur.
- **Drapeau « à vérifier »** (la commission est retenue jusqu'à décision d'un admin) quand :
  - plus de N clients du même revendeur partagent la même adresse IP en 24 h ;
  - des numéros de téléphone se suivent ;
  - plusieurs clients paient avec le même numéro payeur ;
  - les clients d'un même revendeur ont un taux d'abandon anormal.
  L'IP seule ne bloque pas : sur mobile au Cameroun, beaucoup d'abonnés partagent la même adresse.
- **Limite d'attributions par jour et par revendeur**, et limitation du nombre d'essais sur la vérification d'un code (pour ne pas pouvoir énumérer les codes).
- **Suspension** d'un revendeur : plus de nouvelles attributions ; les nouveaux paiements de ses clients créent bien une commission, mais **retenue** (`a_verifier`) jusqu'à décision d'un admin. Un revendeur résilié ou en attente ne génère plus de commission.

## 7. Versements

- Mensuel, sur les commissions **acquises, non annulées et non signalées**.
- Seuil minimum de 5 000 F ; en dessous, le solde est reporté.
- Écran admin « Préparer les versements du mois » : un `Versement` par revendeur, export CSV pour un paiement Mobile Money groupé, puis saisie de la référence et statut PAYEE.
- Les frais de retrait Mobile Money sont à charge d'Edukora pendant le pilote (paramètre à reprendre après mesure du coût réel).

## 8. Interfaces

**Admin Django**
- Revendeurs : création, activation, suspension, changement de taux.
- Commissions : filtres par revendeur, mois et statut ; actions annuler, lever le drapeau, exporter.
- Versements.

**Espace revendeur** (nouvelle page, route française avec son équivalent anglais selon la convention des segments traduits)
- Tableau de bord : ventes du mois, progression vers le palier, commissions en attente, acquises et payées.
- Liste des ventes : **client masqué** (initiales et 4 derniers chiffres du téléphone), plan, date, montant, commission. Jamais de coordonnées complètes.
- Mon code, mon lien, un bouton copier et partager.
- Mes versements.
- Charte à accepter à la première connexion.

## 9. Tests à écrire

- Création de commission par les deux chemins de paiement, une seule fois même si l'appel est répété.
- Calcul : taux de base, palier marginal commerciaux, arrondi, achat couvert par crédit, plan d'enfant supplémentaire.
- Fenêtre de 12 mois (11 mois 29 jours oui, 12 mois 1 jour non).
- Attribution : inscription, rattachement tardif avant et après le premier paiement, code inconnu, code suspendu.
- Auto-achat refusé, drapeau de fraude, retenue de la commission signalée.
- Annulation avant et après acquisition, solde négatif reporté.
- Erreur dans le calcul de commission : le client est quand même activé.
- Un revendeur ne voit que ses propres données.

## 10. Phasage

| Phase | Contenu | Taille |
|---|---|---|
| 1 | Modèles, attribution à l'inscription, commission sur les deux chemins de paiement, admin, tests — **fait le 2026-10-26, non committé** | M |
| 2 | Lien `?rev=`, champ au paiement, espace revendeur en lecture seule — **fait le 2026-10-26** (API `/revendeurs/moi/`, `/revendeurs/moi/ventes/`, `/revendeurs/rattachement/` ; page `/espace-revendeur`, EN `/en/reseller-area`). Sans la charte à accepter ni « Mes versements » : la charte attend sa rédaction (phase 4), les versements la phase 3. Le code mémorisé par un lien est oublié à la première connexion (appareil partagé) ; un compte existant qui se connecte après avoir cliqué le lien doit donc ressaisir son code au paiement | M |
| 3 | Versements groupés, export CSV, drapeaux de fraude — **fait le 2026-10-26** (modèle `Versement`, action « Préparer les versements », CSV, références saisies dans la liste, reprises, commande `preparer_versements`, module `fraude.py`, section « Vos versements » de l'espace) | S à M |
| 4 (en parallèle, sans code) | Charte, contrat d'apport d'affaires, fiche d'accueil, support de vente | S |

Pilote : 5 à 10 revendeurs pendant 6 à 8 semaines à partir de la phase 1. Les versements du pilote peuvent se faire à la main depuis l'admin.

## 11. Déploiement

- Une seule migration nouvelle (`revendeurs/0001_initial`), aucune sur `users`, à rejouer en production.
- Le frontend est servi par l'image Caddy : reconstruire l'image après toute modification de l'espace revendeur.
- La production n'est pas déployée par un pipeline à ce jour : la mise à jour est manuelle et à prévoir.

## 12. Points ouverts

1. **Fiscalité** : traitement fiscal des commissions versées (retenue éventuelle selon le statut du revendeur), à valider avec un fiscaliste ou un expert-comptable camerounais.
2. **Contrat et charte** : à faire relire par un juriste. Ils doivent exclure le salariat, interdire toute promesse de résultat, fixer le prix public unique, interdire le partage de comptes et prévoir la résiliation.
3. **Palier** : seuil de 30 ventes et taux de 17 % à confirmer.
4. **Politique de remboursement** : le délai de 14 jours suppose qu'on sache quand un remboursement est possible. À définir avec le support.
5. **Écoles et centres** : même commission que les autres. Une offre groupée ou une remise pour leurs élèves serait une décision séparée, hors de ce module.
6. **Frais de retrait** : absorbés pendant le pilote, à revoir ensuite.

## 13. Réalisation de la phase 3 (2026-10-26)

**Circuit mensuel.** Admin > Revendeurs > action « Préparer les versements » (ou `manage.py preparer_versements [--simuler] [--code X]`) → Admin > Versements > « Exporter en CSV » → envoi de l'argent en Mobile Money → saisie de la référence dans la liste → « Marquer comme payé » (la référence est obligatoire ; SMS au revendeur). « Annuler » libère les commissions réservées.

**Règles.** Seules les commissions acquises, non retenues et pas encore réservées sont versées. Le seuil est de 5 000 F : en dessous, le solde est reporté. Un revendeur en attente, suspendu ou sans numéro de versement n'est pas payé. Un seul versement préparé à la fois par revendeur. Les frais de retrait sont à la charge d'Edukora (champ `frais_retrait`, à titre d'information).

**Reprises.** Une commission déjà payée puis annulée pour fraude devient une reprise : son montant est déduit du prochain versement, et reporté tant que le net reste sous le seuil.

**Signaux de fraude** (une commission qui en déclenche un est retenue, jamais refusée ; seuils dans `models.py`) : 3 clients du même revendeur payant depuis la même IP en 24 h ; 3 comptes clients réglés depuis le même numéro ; 2 numéros voisins (écart de 2) parmi ses clients ; 3 paiements manuels refusés parmi ses clients en 30 jours ; 50 clients rattachés le même jour. Écarts avec le § 6 : le « taux d'abandon anormal » est remplacé par les paiements refusés en série (le signal réellement mesurable), et la « limite d'attributions par jour » est un signal de rétention plutôt qu'un blocage, pour ne pas refuser une école qui inscrit une classe entière.

**Reste à faire.** Les seuils de fraude sont des estimations à ajuster avec le pilote ; aucun envoi automatique de l'argent (le paiement reste manuel) ; les frais de retrait réels sont à mesurer.
