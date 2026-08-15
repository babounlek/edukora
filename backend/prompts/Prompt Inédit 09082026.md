# PROMPT — Conception de la verticale « Épreuves Inédites Edukora » (v2)

## 0. RÔLE

Tu agis comme un Staff Engineer/PM EdTech travaillant *sur* le dépôt Edukora existant
(Django + DRF côté backend, React côté frontend). Tu combines jugement produit
(monétisation, rétention, marché francophone africain), architecture logicielle
(Django, pipelines IA, génération documentaire) et ingénierie pédagogique. Mais ton
premier réflexe doit toujours être celui d'un mainteneur de ce dépôt précis, pas d'un
consultant qui repart d'une page blanche.

## 1. MISSION EN UNE PHRASE

Concevoir — puis, seulement après validation explicite — implémenter une verticale
premium qui génère des épreuves d'examen **inédites** (jamais une paraphrase d'un sujet
existant), organisées comme un vrai pipeline de conception (référentiel → blueprint →
génération → correction → validation → publication), réservée aux abonnés payants à
tous les niveaux du système (pas seulement au bouton frontend), et pensée comme un
levier de conversion/rétention pour Edukora.

## 2. RÈGLE D'OR — AUDIT D'ABORD, CODE APRÈS VALIDATION

**Ta toute première réponse ne doit contenir aucune migration, aucun modèle, aucun
endpoint.** Elle doit se limiter à la section 7 (Livrable de la première réponse).
Tu codes uniquement après que j'ai validé les décisions structurantes (notamment
l'Ambiguïté #1 ci-dessous).

## 3. VÉRITÉS TERRAIN CONNUES (à vérifier, pas à recopier aveuglément)

Ce qui suit vient d'une lecture réelle du dépôt à une date donnée — **confirme-le par
grep/lecture avant de t'appuyer dessus**, le code a pu bouger depuis :

- **Hiérarchie pédagogique déjà partiellement construite** dans `catalog/models.py` :
  `Country` → `ExamenLabel` (habillage du nom d'examen par pays, ex. BEPC/BFEM) →
  `Series` (rattachée à un `Country`) → `Cursus` (combinaison validée
  `country + examen + series`) → `Subject`, `Tag` (thèmes/mots-clés, le plus proche
  candidat existant pour « compétence/notion »), `Lesson`, `Exercise`, `Question`,
  `Figure`, `Cours`, `RappelDeMethode`. L'abstraction Pays→Système→Examen→Série→
  Matière→Programme→Compétences demandée en section « vision produit » du brief
  d'origine **existe donc déjà en grande partie** : à étendre, pas à réinventer.
- **L'abonnement n'est PAS un palier global aujourd'hui.** `subscriptions.Plan` est
  rattaché à un `Cursus` précis (prix + durée, éventuellement « jusqu'à l'examen » via
  `ExamSession`), et `Subscription` est une ligne par `(user, cursus)`. Il n'existe
  aucune notion de palier transverse type ESSENTIEL/PERFORMANCE/MAX. Voir Ambiguïté #1.
- **Le contrôle d'accès a déjà un point de vérité unique** : `access/services.py`
  (`has_access(user, obj)`) interroge `Subscription` et gère le cas vitrine/anonyme.
  Toute nouvelle règle d'accès (type `user.can_access_inedite_exams()`) doit suivre ce
  même patron — une seule fonction/service appelée partout, jamais dupliquée.
- **Un précédent architectural quasi identique existe déjà : l'app `quiz`.**
  `quiz.CompetenceItem` (contenu auto-suffisant généré, pas extrait verbatim d'un
  examen) + `quiz/ingestion.py` (`ingest_competence_item`/`run_ingestion`, réutilise les
  résolveurs matière/cursus/difficulté de `catalog.ingestion`) + la commande
  `manage.py ingest_quiz_content` + la skill de génération `concepteur-quiz-competence`
  + la skill de run `generer-batch-quiz-competence` (sélection déterministe par
  `select_quiz_batch`, capée en volume, sans LLM pour le choix du lot). **C'est le
  template à copier/adapter pour `conception-epreuve-inedite`**, pas un problème à
  résoudre depuis zéro.
- **`correction-experte`** est la skill/le standard de qualité déjà en place pour la
  rédaction de corrigés — la génération de correction d'une épreuve inédite doit viser
  le même niveau, et peut réutiliser le même style/gabarit.
- **`analytics.AnalyticsEvent`/`EventName`** existe déjà pour le suivi d'événements
  produit — les KPI de la section business doivent s'y brancher plutôt que créer un
  système de métriques parallèle.
- **`payments`** gère déjà des paiements réels (CamPay via `Transaction`, plus
  `ManualPayment`). Toute hypothèse de pricing doit se raccorder à ce système existant,
  pas supposer une couche de facturation abstraite.
- **Convention de stockage** : tout chemin média dérivé d'un contenu (pas un nom
  aléatoire/UUID) doit être préfixé par le code pays en minuscule (`<cc>/...`), comme
  `Lesson.sujet_pdf` et `Figure.image` — applique la même règle à tout nouveau PDF
  généré (épreuve, corrigé).
- **Le dossier `ingest/` peut être régénéré/synchronisé en dehors de la session** :
  ne compte jamais sur une édition manuelle de JSON dans ce dossier pour persister.

## 4. AMBIGUÏTÉ #1 À TRANCHER AVANT TOUT CODE

Le brief d'origine suppose trois paliers globaux (ESSENTIEL/PERFORMANCE/MAX, MAX
donnant accès aux Épreuves Inédites). Le système actuel vend l'accès **par Cursus**, pas
par palier global. Introduire un palier global est un vrai changement de modèle
commercial, pas un simple renommage. Présente-moi ce choix avec une recommandation,
ne tranche pas seul :

- **Option A — Add-on au-dessus de l'existant.** Nouveau
  flag/plan « MAX » orthogonal, qui débloque Épreuves Inédites sur les Cursus déjà
  souscrits par l'utilisateur. Impact minimal sur le funnel d'achat actuel.
- **Option B — Refonte en paliers globaux.** `Plan`/`Subscription` évoluent pour
  remplacer l'achat par Cursus par un achat de palier transverse. Gros impact : tous les
  abonnements existants, le checkout, le pricing actuel sont concernés.
- **Option C — Add-on scoped Cursus, symétrique à l'existant.** Un second type de
  souscription, au même grain que `Subscription` aujourd'hui (par `user`+`cursus`, ou
  par `user`+`examen`), qui gate spécifiquement Épreuves Inédites. Le plus proche du
  modèle de données actuel, donc le plus rétrocompatible.

Recommandation par défaut si rien ne s'y oppose côté produit : **C**, en cohérence avec
la contrainte « ne jamais casser l'existant » (section 6). Mais le choix a un impact
sur le pricing et le funnel : confirme avec moi avant d'implémenter.

## 5. CONTRAINTES NON NÉGOCIABLES

- **Pas de pipeline naïf** « programme → prompt LLM → sujet ». Un blueprint d'épreuve
  (sections, points, compétences visées, difficulté) doit être validé avant la
  génération des exercices ; la correction est générée et vérifiée indépendamment de
  l'énoncé ; un score d'originalité et un score de qualité conditionnent la publication.
- **La restriction d'accès s'applique à chaque couche** — service, permission DRF,
  génération, téléchargement, consultation, correction, historique — via la même
  source de vérité unique (mirroring `access.has_access`). Jamais un simple test
  frontend qui cache un bouton.
- **Réutilisation avant création** : hiérarchie `catalog`, précédent `quiz` (modèle +
  ingestion + skill + commande), gating `access`/`subscriptions`, facturation
  `payments`, métriques `analytics`. Ne duplique aucune logique d'autorisation.
- **Incrémental et rétrocompatible** : migrations non destructives, aucune régression
  sur l'existant, tests avant/après chaque étape.
- **Pas de sur-ingénierie** : pour chaque brique proposée (multi-agents, moteur de
  pré-génération, personnalisation par profil élève, cache…), réponds explicitement à
  « quel problème concret ça résout, et est-ce que la complexité se justifie
  aujourd'hui ? ». Si non : documente-la comme option future dans la roadmap, ne la code
  pas.
- **Budget IA piloté** : coût par génération tracé (modèle, tokens, coût estimé),
  plafond configurable, dégradation propre (pas de crash) si le budget ou l'API LLM
  n'est pas disponible.
- **Confidentialité minimale** sur les données de performance/personnalisation élève
  (pas de fuite inter-comptes, purge possible) — à documenter dès la conception même si
  l'implémentation complète attend une phase ultérieure.

## 6. AMBIGUÏTÉS SECONDAIRES — SIGNALE, NE TRANCHE PAS SEUL

Si tu rencontres une décision à fort impact et faiblement réversible (ex. schéma de
scoring de qualité, granularité du modèle de personnalisation, mécanisme de détection
de similitude, format de stockage du blueprint), présente les options et ta
recommandation au lieu de choisir silencieusement — même règle que l'Ambiguïté #1.

## 7. LIVRABLE ATTENDU DE CETTE PREMIÈRE RÉPONSE

1. Confirmation ou correction des « vérités terrain » (section 3), par lecture réelle
   du code — cite fichier:ligne.
2. Diagnostic : réutilisable tel quel / à étendre / à créer, avec risques et dette
   technique identifiés.
3. Décision recommandée sur l'Ambiguïté #1 (section 4) et toute autre ambiguïté
   structurante rencontrée (section 6).
4. Modèle de données proposé, explicitement rattaché aux modèles existants
   (`Cursus`, `Subject`, `Tag`…) — pas un schéma parallèle.
5. Pipeline `conception-epreuve-inedite` proposé, calqué sur le précédent `quiz`
   (modèle + ingestion + skill + commande) sauf justification contraire.
6. Stratégie de contrôle qualité (originalité + validation pédagogique/structurelle),
   avec une décision justifiée sur le niveau de complexité (agent unique vs
   multi-agents).
7. Plan d'implémentation en phases indépendantes, testables séparément.
8. Risques, dette technique, points bloquants.

Attends ma validation avant toute migration ou tout code de production.

## 8. ANNEXE — PISTES MÉTIER (à évaluer et challenger, pas à implémenter telles quelles)

Ces pistes viennent du brief d'origine. Elles ne sont pas des instructions figées :
identifie les contradictions entre elles (ex. « MAX/annuel exclusivement » vs
« détermine le meilleur modèle parmi plusieurs ») et propose une version cohérente.

- **Positionnement** : « simulateur intelligent d'examens » — reproduire structure,
  durée, barème, style rédactionnel et niveau d'exigence réel de l'examen ciblé.
- **Marché** : Cameroun d'abord (BEPC, Probatoire, BAC, CAP…), extension Afrique
  francophone ensuite — l'abstraction pays existe déjà en bonne partie (section 3),
  donc le risque de code figé pour un seul pays est déjà partiellement couvert.
- **Monétisation** : parmi les modèles « MAX = accès inédit », « MAX = illimité »,
  « MAX = quota mensuel », « MAX = simulations + personnalisation + analyse » — choisis
  en fonction du coût LLM réel (si mesurable, regarde ce que coûtent déjà en tokens/
  appels `correction-experte`/`concepteur-quiz-competence`) plutôt que d'inventer des
  hypothèses de prix sans donnée. Ne propose pas de chiffres de pricing final comme des
  faits — présente-les comme des hypothèses à valider avec de vraies données marché/
  coût.
- **Rareté/rétention** : quotas de simulations premium, génération à la demande vs
  pré-génération (pre-generation engine pour lisser le coût), examens blancs
  hebdomadaires, recommandations basées sur les faiblesses détectées.
- **Data flywheel / personnalisation** : boucle réponse → performance → détection de
  lacunes → épreuve adaptée, en conservant un mode « simulation officielle » identique
  pour tous quand c'est pertinent (comparabilité entre candidats).
- **KPI** produit/business/IA — à faire remonter via `analytics.AnalyticsEvent`
  plutôt qu'un système parallèle.
- **Validation multi-agents** (concepteur / expert pédagogique / correcteur /
  auditeur / détecteur d'originalité / examinateur) : n'implémente que les rôles dont
  la valeur justifie le coût et la latence — un seul « agent » avec plusieurs passes
  outillées peut suffire au MVP.

## 9. RÈGLES DE TRAVAIL

1. Inspecte le dépôt avant de proposer quoi que ce soit — ne suppose jamais l'absence
   d'un fichier/modèle sans vérifier.
2. Réutilise au maximum l'existant (section 3), n'invente pas de structures
   parallèles.
3. Ne casse aucune fonctionnalité existante ; vérifie les dépendances avant de modifier.
4. Écris et lance les tests pertinents ; vérifie migrations, permissions, performances,
   coûts IA.
5. Documente les choix structurants, en particulier les ambiguïtés tranchées.

## 10. CRITÈRE DE RÉUSSITE

Edukora doit passer de « une plateforme qui donne accès à d'anciennes épreuves et
corrections » à « une plateforme qui simule en continu l'examen de l'élève et adapte
son entraînement à ses résultats » — la fonctionnalité Épreuves Inédites est la
première brique de cette transformation, pas une fonctionnalité isolée.