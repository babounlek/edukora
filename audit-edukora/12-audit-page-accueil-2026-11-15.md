# 12 - Audit de la page d'accueil (/cm) - 2026-11-15

Objectif fixé : amener l'accueil au niveau des meilleures edtech mondiales.
Rien n'a été modifié : audit en lecture seule.

## Méthode et limites
- **Vu à l'écran** : vitrine visiteur en local (image caddy, http://127.0.0.1/cm), mobile 375x812 et bureau 1366x800, page entière ; accueil de l'élève abonné (compte [TEST]) en mobile, premier écran et texte complet.
- **Mesuré** : ressources chargées (API Performance du navigateur), en-têtes et poids des fichiers de la **production** (curl, brotli), HTML servi à Googlebot et à WhatsApp en production.
- **Lu** : `frontend/src/pages/CataloguePage.tsx`, `SectionParents`, `SocialProofSection`, `index.html`, `backend/catalog/prerendu.py`.
- **Non mesuré** : LCP et INP (le navigateur d'audit ne remonte pas ces mesures), téléphone d'entrée de gamme réel, 3G réelle, contrastes de couleur, version anglaise (/en/cm), état « élève connecté sans abonnement ». Ce n'est pas un test utilisateur.
- **Comparaison** : faite d'après les pratiques connues de Duolingo, Khan Academy, Brilliant, Quizlet, Seneca, Save My Exams, Kartable et uLesson. Leurs pages n'ont pas été reparcourues aujourd'hui.

## Verdict
La page est propre, honnête et claire : c'est une bonne page de jeune produit. Elle n'est pas encore au niveau mondial. Note d'ensemble (jugement de l'auditeur) : **2,8 / 5**.

Ce qui la sépare du meilleur niveau tient en cinq points, par ordre d'importance :
1. **La promesse n'a pas de bouton.** Le titre vend la séance du jour, aucun bouton n'y mène.
2. **Le produit n'est pas montré.** Une photo d'illustration occupe la place de la carte de séance, qui est pourtant l'écran le plus convaincant du site.
3. **Aucune preuve sociale.** En production, l'API des témoignages renvoie une liste vide : la section ne s'affiche pas.
4. **Page blanche tant que le JavaScript n'est pas chargé** : 297 Ko compressés avant le premier pixel.
5. **Rien n'est mesuré sur cette page** : aucun évènement sur les boutons, donc aucune optimisation possible.

## Grille de notation
| Critère | Note | Constat principal |
|---------|------|-------------------|
| Promesse comprise en 5 secondes | 4 / 5 | « Chaque jour, on te dit quoi réviser » est net et différenciant. Le paragraphe dessous fait 43 mots (6 lignes sur mobile). |
| Délai avant la première valeur | 2 / 5 | Voir A1. Trois touchers et une longue page avant la première question de quiz. |
| Démonstration du produit | 2,5 / 5 | L'extrait réel de corrigé est un bon réflexe. La séance du jour, elle, n'apparaît nulle part. |
| Preuve sociale et confiance | 1 / 5 | Zéro témoignage, aucun nombre d'élèves, aucun auteur ou relecteur nommé. Seules les trois puces de volume rassurent. |
| Hiérarchie et longueur | 3 / 5 | 6 269 px sur mobile (7,7 écrans), redites entre sections. |
| Publics (examen, parent, GCE) | 3,5 / 5 | Tout existe, mais le choix d'examen est dans un bandeau refermable et le bloc parent arrive au 6e écran. |
| Prix et conversion | 3 / 5 | 2 000 FCFA par mois n'apparaît qu'au 7e écran. Aucun bouton « Commencer gratuitement ». |
| Performance mobile | 2,5 / 5 | Voir C. Le décalage de mise en page est à 0 (bon). |
| Référencement de l'accueil | 3,5 / 5 | Prérendu pour les robots en place ; un défaut de langue et un contenu maigre (voir D). |
| Mesure | 1 / 5 | Un seul évènement sur la page (`pdf_fiche_sujet_landing`). |
| Identité visuelle | 3,5 / 5 | Typographie et couleurs soignées ; cartes toutes identiques, aucune image du produit, aucun mouvement. |

## A. Constats de conversion (faits observés)
| ID | Constat | Preuve |
|----|---------|--------|
| A1 | Le bouton principal « Lire un corrigé gratuit » mène à une **liste** (`/cm/epreuves?gratuit=true`) : le visiteur doit encore choisir. Le bouton « Quiz gratuit, sans compte » mène à `/quiz`, où il faut choisir l'examen, puis la matière, puis « Essayer ». | `CataloguePage.tsx:330` et `:340` ; page /quiz parcourue |
| A2 | Choisir son examen dans le bandeau ne mène nulle part : la page se personnalise (exemple, inédites) mais aucun « voici ta première séance » n'apparaît. La séance n'est visible qu'une fois connecté. | `SeanceDuJour.tsx:81` |
| A3 | Sur mobile, le premier écran ne contient ni image du produit ni preuve : la photo commence à 760 px sur 812, les puces de volume sont au 2e écran. | Capture mobile |
| A4 | La photo du hero est une illustration générique (élève, salle vide). Elle ne dit rien du produit. | Capture |
| A5 | Ligne GCE en double langue, lourde : « Preparing the GCE (English-language system)? Tu prépares le GCE (sous-système anglophone) ? Switch to English ». | Capture mobile |
| A6 | Les épreuves inédites sont présentées **trois fois** (bandeau « Exclusif », 4e avantage, encart vedette). « Comment ça marche » et « Pourquoi EduKora ? » redisent les mêmes mécanismes. Deux blocs « Voir les prix » se suivent en bas de page. | Texte de la page |
| A7 | Aucun témoignage en production : `GET /catalog/temoignages/` renvoie `[]`. | curl du 2026-11-15 |
| A8 | Le prix, argument fort (2 000 FCFA, Mobile Money, sans engagement), n'est visible qu'en bas de page. | Texte de la page |
| A9 | « 14 158 cours structurés » à côté de « 1 565 épreuves » : le chiffre peut sembler gonflé si un « cours » est en réalité un rappel de méthode. **Hypothèse** à valider, le libellé est peut-être à préciser. | Puces du hero |
| A10 | Aucun évènement de mesure sur les boutons du hero, le choix d'examen ou le bloc parent. | grep `trackEvent` |

## B. Accueil de l'élève abonné (aperçu, hors objectif principal)
- Un seul bouton principal clair (« Commencer : faire un exercice »), le compte à rebours et la raison du thème (« raté il y a 22 jours ») : c'est au bon niveau.
- La page empile ensuite une quinzaine de blocs (lecture en cours, erreurs, palier, défi, rappel par e-mail, à reprendre, progression, plan, prochaine inédite). À trier par usage réel une fois la mesure en place.
- Le titre de la séance reprend le nom brut du thème (« Image d'une figure ») : ambigu hors contexte.

## C. Performance (production, mesurée)
| Mesure | Valeur | Niveau visé |
|--------|--------|-------------|
| HTML utile pour un humain | Aucun : `<div id="root">` vide | Hero présent dans le HTML |
| Poids bloquant avant le premier affichage | **297 Ko** brotli (JS 255 Ko en 18 fichiers, CSS 37 Ko) | Moins de 150 Ko |
| Délai du premier octet (HTML) | 0,48 à 0,66 s à chaud, 1,8 s à froid ; `cf-cache-status: DYNAMIC` | HTML servi depuis le cache Cloudflare |
| Chargé ensuite pour l'accueil | Morceau de page 23 Ko, puis rendu Markdown et KaTeX 144 Ko + 47 Ko pour l'extrait de corrigé. **Rectificatif** : ce chargement était déjà différé (à l'approche de l'extrait, ou après 8 s sur une bonne connexion, voir `EpreuveMarkdownLazy`) ; il ne pèse pas sur le premier affichage | Déjà en place |
| Appels d'API au chargement | 12 | 1 à 3 |
| Total de la page (local) | 87 requêtes, 759 Ko compressés, 2,2 Mo décompressés | - |
| Image du hero | 20 Ko, WebP, `srcset`, priorité haute : bien. Mais découverte tard (elle est référencée dans un morceau chargé à la demande) | Préchargée depuis le HTML |
| Décalage de mise en page (CLS) | 0,000 en local | Tenu |

Lecture : sur un téléphone d'entrée de gamme en 3G, l'élève regarde un écran blanc pendant le téléchargement et l'exécution d'environ 1 Mo de JavaScript décompressé. Les sites de référence envoient le hero dans le HTML.

## D. Référencement de l'accueil
| ID | Constat | Preuve |
|----|---------|--------|
| D1 | **Défaut** : la page française servie aux robots porte `<html lang="en">`. La langue est déduite de `bilingue`, vrai pour toutes les pages d'ensemble. | `prerendu.py:303`, curl Googlebot sur la production |
| D2 | Le HTML des robots fait 124 mots et son H1 (« Corrigés BEPC, Probatoire, BAC - Cameroun ») diffère de celui des visiteurs. Aucune des sections de la page n'y figure. | curl Googlebot |
| D3 | Aucune donnée structurée dans le HTML des robots de l'accueil (Organization et WebSite ne sont que dans la coquille de l'application). | curl Googlebot, 0 bloc JSON-LD |
| D4 | `/` répond 200 puis redirige en JavaScript vers `/cm`. Une redirection serveur serait plus propre pour l'adresse la plus partagée. | `App.tsx:86`, curl |
| D5 | Aperçu WhatsApp correct (titre, description, image 1200x630). | curl WhatsApp |

## E. Ce que font les meilleurs, et où en est EduKora
| Pratique | Exemples | EduKora aujourd'hui |
|----------|----------|---------------------|
| Un toucher entre l'accueil et le produit, sans compte | Duolingo, Brilliant | 3 touchers pour le quiz, liste à trier pour le corrigé |
| Le choix de l'examen est l'action du hero et mène droit au contenu | Save My Exams, Seneca, Kartable | Bandeau refermable, sans destination |
| On montre le produit, pas une photo | Duolingo, Brilliant, Quizlet | Photo d'illustration |
| Preuve chiffrée (élèves, avis, résultats) | Khan Academy, Seneca, uLesson | Aucune |
| Prix et gratuité dits tôt | uLesson | En bas de page |
| Page d'accueil rendue par le serveur | Tous | Coquille vide + JavaScript |
| Appli et hors-ligne mis en avant | uLesson, Duolingo | Le hors-ligne existe, l'accueil n'en parle pas |
| Tests A/B permanents du hero | Duolingo | Aucune mesure |

## F. Recommandations classées
### Lot 1 - rapide (une demi-journée à une journée au total)
| # | Action | Répond à |
|---|--------|----------|
| R1 | Corriger `lang` du prérendu : langue de la page pour les pages d'ensemble. | D1 |
| R2 | Raccourcir le paragraphe du hero à 20 mots, et ajouter sous les boutons une ligne de réassurance : gratuit pour essayer, 2 000 FCFA par mois ensuite, Mobile Money. | A8, promesse |
| R3 | Réduire la ligne GCE à une seule phrase, dans l'autre langue seulement. | A5 |
| R4 | Fusionner « Comment ça marche » et « Pourquoi EduKora ? », ne garder qu'une présentation des inédites et un seul bloc final de prix. Cible : 5 écrans sur mobile. | A6 |
| R5 | Mesurer : clic sur chaque bouton du hero, choix d'examen, clic du bloc parent (3 noms à ajouter au vocabulaire fermé du backend). | A10 |

### Lot 2 - structurant (2 à 5 jours chacun)
| # | Action | Répond à |
|---|--------|----------|
| R6 | **Hero « choisis ton examen, voici ta première séance »** : les examens deviennent l'action principale du hero. Au choix, afficher le thème n°1 réel de cet examen (« tombé dans 23 épreuves sur 28 ») avec un bouton « Commencer, 5 questions, sans compte » vers `/quiz/essai/:cursus/:subject/:theme`, route qui existe déjà. | A1, A2 |
| R7 | Remplacer la photo par la carte de séance (compte à rebours, thème, fréquence, 25 min), composant réel ou capture, visible dès le premier écran mobile. | A3, A4 |
| R8 | Preuve sociale vraie : recueillir trois témoignages (le modèle existe), dire qui rédige et relit les corrigés, afficher un compteur réel dès qu'il est présentable. Ne rien inventer. | A7 |
| R9 | Performance : hero dans le HTML pour les humains, extrait de corrigé rendu à l'avance ou chargé à l'approche de l'écran, un seul appel d'API pour l'accueil, HTML mis en cache chez Cloudflare, image du hero préchargée. Budget : moins de 150 Ko bloquants. | C |
| R10 | Section de questions fréquentes (gratuit ou non, paiement, téléphone et hors-ligne, examens couverts, auteurs) avec balisage FAQPage, reprise dans le HTML des robots avec le reste de la page. | D2, D3 |

### Lot 3 - montée en gamme
- Compte à rebours de l'examen dans le hero (la date est déjà connue du produit).
- Mise en avant de l'installation et du hors-ligne (« marche sans réseau »).
- Illustrations ou mascotte propres à la marque, un peu de mouvement.
- Tests A/B du hero une fois R5 en place.
- Redirection serveur de `/` vers `/cm` (D4), à étudier avec la règle du pays mémorisé.

## G. À ne pas casser
Titre du hero ; extrait réel de corrigé ; personnalisation selon l'examen déclaré ; CLS à 0 ; image optimisée ; prérendu et aperçus de partage ; ton honnête (« les annales existent déjà gratuitement ») ; bloc parent ; prix en FCFA et Mobile Money ; bilinguisme.

## H. Statut après le lot 1 (2026-11-15, en local, non committé, non déployé)
| # | Statut | Vérification |
|---|--------|--------------|
| R1 | **Corrigé** : les pages d'ensemble annoncent la langue de la page (`langue_texte`). | Googlebot en local : `/cm` et `/cm/epreuves` en `lang="fr"`, `/en/cm` en `lang="en"` ; test ajouté |
| R2 | **Fait** : paragraphe du hero ramené de 43 à 20 mots ; ligne « Gratuit pour essayer. Ensuite 2 000 FCFA par mois, par Mobile Money, sans engagement. » sous les boutons. | Capture mobile |
| R3 | **Fait** : « Preparing the GCE? Switch to English » (variante compacte déjà existante). | Capture mobile |
| R4 | **Fait en partie** : grille « Pourquoi EduKora ? » et bandeau « Exclusif » retirés (la phrase sur les annales gratuites est gardée sous « Comment ça marche »), un seul « Voir les prix » sur la page. Longueur mobile : 6 269 px → **5 121 px (6,3 écrans)**. La cible de 5 écrans n'est pas atteinte : le reste tient à l'extrait de corrigé et à l'aperçu d'inédite, laissés entiers. | Mesure dans le navigateur |
| R5 | **Fait** : `accueil_bouton_clic` (`cible`) sur les boutons de la vitrine et `examen_choisi` (`source`, `cursus_id`) à la déclaration d'examen. Lecture dans l'admin, filtre par nom. | Deux évènements relus en base locale après clic |

Tests : 1 576 tests frontend et 119 tests backend (catalog prérendu, analytics) passent. Version anglaise des nouveaux textes écrite mais non vue à l'écran.
Déploiement : migration `analytics 0018`, puis rebuild du backend et de caddy.

## I. Statut après les lots 2 et 3 (2026-11-15, en local, non committé, non déployé)
| # | Statut | Ce qui a été fait | Vérification |
|---|--------|-------------------|--------------|
| R6 | **Fait** | Carte « Ta première séance » dans le hero (`PremiereSeance`). Sans examen : « Tu prépares quel examen ? » et les examens du pays. Examen choisi : thème gratuit le plus fréquent (mathématiques d'abord), matière, nombre de questions, « Tombé dans X épreuves sur Y », compte à rebours, bouton « Commencer, sans compte ». L'API des essais renvoie la fréquence aux épreuves officielles de la matière. | Mobile et bureau. BEPC : « Identité remarquable, tombé dans 26 épreuves sur 28 ». BAC D : « Équation différentielle, 13 sur 41 ». Un toucher sur « Commencer » ouvre la question 1 sur 6 |
| R7 | **Fait** | La photo d'illustration est retirée ; la carte prend sa place et arrive au premier écran sur mobile. Le bandeau « Choisis ton examen » ne s'affiche plus sur l'accueil (la carte pose la question). | Captures |
| R8 | **Non codé** | Rien n'a été inventé. Trois décisions sont à prendre (voir plus bas). | - |
| R9 | **Fait en partie** | Le titre et la promesse du hero sont dans le HTML (`index.html`), affichés dès la feuille de style, puis repris à l'identique par React (`CoquilleAccueil`). Un abonné ne voit plus la vitrine un instant (indice mémorisé). | Coquille présente dans le HTML servi ; CLS mesuré 0,026 ; LCP non mesurable dans le navigateur d'audit |
| R10 | **Fait** | Six questions fréquentes sur l'accueil (fichier partagé `faq-accueil.json`), reprises dans le HTML des moteurs avec le balisage FAQPage, plus Organization et WebSite. | Googlebot en local : 315 mots (124 avant), 6 questions, 3 blocs JSON-LD |
| Lot 3 | **En partie** | Compte à rebours dans la carte ; hors-ligne dit dans les questions fréquentes. | Capture |

### Ce qui n'a pas été fait, et pourquoi
- **Un seul appel d'API pour l'accueil (R9)** : 12 appels au chargement, inchangé. Les regrouper touche des clés de cache partagées avec les listes ; à faire à part.
- **HTML mis en cache chez Cloudflare (R9)** : écarté. Le serveur répond différemment aux moteurs selon le User-Agent (`Cache-Control: private`, voir `prerendu.py`) : un cache partagé servirait la mauvaise version.
- **Redirection serveur de `/` vers `/cm`, illustrations, tests A/B (lot 3)** : non codés.
- **Longueur de page** : 5 583 px sur mobile (6,9 écrans), contre 5 121 après le lot 1. La carte est plus haute que la photo et les questions fréquentes s'ajoutent.

### Décisions prises en codant, à valider
- Le tutoriel « Bienvenue » du visiteur ne s'ouvre plus tant que la carte est à l'écran, et le message « Noté : BEPC » n'apparaît plus quand l'examen est choisi depuis la carte : les deux recouvraient le bouton « Commencer » sur mobile. Le tutoriel peut encore s'ouvrir une fois la carte hors de l'écran.
- Le bouton « Lire un corrigé gratuit » devient secondaire (contour) et « Quiz gratuit, sans compte » est remplacé par la carte ; « Une autre matière » mène à /quiz.
- Texte corrigé dans le HTML des moteurs de /tarifs : il annonçait « un tarif réduit à partir du deuxième enfant », supprimé le 2026-11-13. Il dit maintenant « chacun au même prix ».

### Décisions attendues pour R8 (preuve sociale)
1. Afficher un compteur d'activité (questions répondues, par exemple) ? Le code dit que le nombre d'élèves n'est volontairement pas public (`PlatformStatsView`).
2. Recueillir des témoignages dans l'application (après une séance), avec modération dans l'admin ? Les élèves sont mineurs : la formule de consentement et le nom affiché sont à décider.
3. Qui rédige et relit les corrigés : il faut les faits pour l'écrire.

Tests : 1 590 tests frontend et 126 tests backend passent.
Déploiement : migration `analytics 0018`, puis rebuild du backend et de caddy.

## J. Compléments du 2026-11-15 au soir (en local, non committé, non déployé)
Remplace, pour ces deux points, la liste « Ce qui n'a pas été fait » de la section I.
| Point | Statut | Ce qui a été fait | Vérification |
|-------|--------|-------------------|--------------|
| Appels d'API de l'accueil (R9) | **Fait en partie : 12 → 9** | Route unique `GET /catalog/accueil/` (`backend/catalog/accueil_api.py`) pour les trois chiffres du hero et les témoignages, à la place de quatre appels. Elle interroge les vues des listes elles-mêmes : les chiffres ne peuvent pas diverger. | En local : 1 621 épreuves, 14 158 cours, 26 matières, identiques aux trois listes ; 9 appels au chargement ; CLS 0,000 |
| Redirection de `/` (D4) | **Fait** | Caddy redirige `/` vers `/cm` et `/en` vers `/en/cm` en 302, query conservée (lien de parrainage `/?ref=CODE`). 302 et non 301 : un seul pays est ouvert, la règle doit pouvoir changer le jour où un deuxième ouvre. | `curl` : `/`, `/?ref=ABC`, `/en`, et Googlebot sur `/` |

Les 9 appels restants : inédites récentes, campagne, statistiques et examens du pied de page, examens, pays, route de l'accueil, extrait de corrigé, inédite vedette. Les retarder ferait apparaître des sections pendant le défilement ; les fusionner toucherait l'en-tête et le pied de page de toutes les pages.

Tests : 1 591 tests frontend ; tests backend de la route, du prérendu, des segments et des essais au vert.
Déploiement : inchangé (migration `analytics 0018`, rebuild du backend et de caddy). Le Caddyfile change : la redirection de `/` prend effet au rebuild de caddy.

## K. Preuve sociale, volet 2 : avis recueillis dans l'application (2026-11-16, en local, non committé, non déployé)
Décision de l'utilisateur du 2026-11-16 : coder le volet 2 de la proposition R8. Le compteur d'activité (volet 1) et le
bloc « Comment sont faits nos corrigés » (volet 3) ne sont pas codés.

| Règle | Ce qui est en place | Où |
|-------|---------------------|----|
| Quand on demande | À partir du troisième quiz terminé, une seule fois par profil et par rôle (contrainte en base). Jamais à un compte invité. « Ne plus me demander » est retenu sur l'appareil. | `backend/catalog/avis.py`, `frontend/src/components/InviteAvis.tsx` |
| Où | Élève : page de résultat d'un quiz, sous les boutons pour continuer. Parent : page « Mes paiements » et écran « paiement réussi ». | `QuizResultPage`, `MesPaiementsPage`, `SubscribePage` |
| Consentement | Case non cochée d'office. Sans elle, l'avis est gardé pour l'équipe et sa publication est refusée (modèle, admin et liste publique). | `Temoignage.clean`, `TemoignageQuerySet.publies` |
| Ce qui s'affiche | Prénom et examen préparé (élève), prénom et « Parent d'élève » (parent). Le prénom n'accepte que des lettres. | `catalog/avis.py` |
| Modération | Tout avis arrive en brouillon. L'admin montre la provenance, la langue, le texte et « Publiable » ; provenance et consentement y sont en lecture seule. | `catalog/admin.py` |
| Langue | Un avis n'est montré qu'aux visiteurs de sa langue (`?langue=`), sur l'accueil et sur /tarifs. | `TemoignageListView`, `accueil_api.py` |
| Seuil d'affichage | La section n'apparaît qu'à partir de trois avis publiés, avec le titre « Ce qu'en disent les élèves et les parents ». | `SocialProofSection.tsx` |
| Retrait | Supprimer le profil ou le compte dépublie l'avis ; la ligne reste, détachée, pour que la purge des comptes de test garde ses comptages. | signal `pre_delete` dans `catalog/avis.py` |
| Confidentialité | Une puce « Avis » ajoutée à la politique de confidentialité (fr et en), date de mise à jour 2026-11-16. | `conf.d9`, `PrivacyPage.tsx` |

Vérifié en local : avis envoyé depuis le compte de test (201, brouillon, prénom et « BEPC »), absent de la liste
publique avant publication, section visible sur /cm avec trois avis publiés et absente avec un seul, invitation du
parent sur /mes-paiements, mobile sans débordement. Les lignes d'essai ont été supprimées.

Tests : 1 603 tests frontend, 1 001 tests backend (catalog, purge et seed des comptes de test, essais).

### Décisions prises en codant, à valider
- **Avis du parent après usage seulement.** La proposition disait « après un paiement réussi ». L'invitation n'apparaît
  que si le compte a déjà terminé trois quiz : un premier paiement n'a encore rien à juger, et l'écran du nouvel abonné
  reste consacré à son démarrage. Elle est aussi sur « Mes paiements », seule page vue par ceux qui paient par dépôt
  déclaré.
- **« Troisième séance » = troisième quiz terminé**, quel que soit son lancement (plan du jour ou quiz libre).
- **Une note seule est acceptée.** Sans texte elle n'est pas publiable, mais elle donne à l'équipe une mesure de
  satisfaction.
- **Pas de mesure d'audience ajoutée** : le nombre d'avis se lit dans l'admin.

### À relire par l'utilisateur
- La formule de consentement et la puce de la politique de confidentialité : ce sont des textes à portée juridique,
  les auteurs sont mineurs.
- Avant chaque publication, vérifier dans l'admin que « Auteur » est un prénom seul et que le texte ne nomme personne,
  ni établissement, ni ville.

Déploiement : migration `catalog 0071` (après `users 0020`), puis rebuild du backend et de caddy.
