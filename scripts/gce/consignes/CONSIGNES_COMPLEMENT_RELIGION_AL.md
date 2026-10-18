# Complément aux consignes - GCE ADVANCED LEVEL, RELIGIOUS STUDIES (code 0785)

Lis `CONSIGNES.md` (forme générale, LaTeX, figures), puis `CONSIGNES_COMPLEMENT_AL.md` (niveau, identité, formats de papers), puis ce fichier.
**Ce fichier prime** pour tout ce qui touche aux Études religieuses : codes, noms de dossier, papers, règles de choix, exactitude, thèmes.

## Identité du sujet

- `examen` `"gce_al"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"Religious Studies"`, `code_matiere` `"0785"` (page de garde : « ADVANCED LEVEL », « 0785 RELIGIOUS STUDIES »).
  Autre matière, autre code ou autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-al-religion-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`.
- Sources : `D:\edukora\backend\ingest\_telechargements_gce_2026-10-13\gcerevision_al_2019_2026\GCE_AL_RELIGIOUS_STUDIES_<ANNEE>_P<n>.pdf` (scans sans couche texte : lis chaque page en image avec Read, paramètre `pages`).
- Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les trois papers

- **Paper 1** : 50 QCM, 1h30 (questions de connaissance sur la Bible, l'Évangile, l'histoire de l'Islam, les religions africaines traditionnelles ; en 2023, Ancien Testament puis Nouveau Testament, Islam, ATR). UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"`,
  `type_reponse` `"qcm"`, lettres `a` à `d` minuscules, `reponse_correcte` une lettre, `points` `""`, `groupes` `[]`, `regles_choix` `[]`. Chaque clé s'établit sur un fait CLASSIQUE et reconnu des textes (Bible, Coran, tradition islamique,
  manuels d'ATR) ; un QCM dont deux options sont défendables, dont la clé suppose un détail de manuel local invérifiable ou dont l'énoncé est défectueux : convertis en `ouverte`
  (`node D:\edukora\scripts\gce\convertir_en_ouverte.js <fichier.json> <numero...>`), jamais une lettre au hasard.
- **Paper 2** : « The Old Testament / Islam and African Traditional Beliefs and Practices » (3 h), « Answer FOUR questions chosen from any ONE SECTION ONLY. All questions carry equal marks », 25 points chacune.
  Sections typiques : « Section 1.1 The Patriarchs to David » (Old Testament), « Section 5.3 Islam », « Section 5.5 African Traditional Religious Beliefs and Practices » : les numéros et titres peuvent changer, copie ceux imprimés.
- **Paper 3** : « The New Testament, Religion in Relation to Philosophy, Ethics and Morality, Historical Development of Islam (570CE-661CE) » (3 h), même consigne « FOUR questions chosen from ONE SECTION ONLY ». Sections typiques : 2.1 The Gospel According to Luke,
  2.2 The Fourth Gospel, 2.3 The Early Church as reflected in Acts and 1 Corinthians, 4.1 Philosophy of Religion, 4.2 Ethics and Morality, 6.0 The Historical Development of Islam. Lis la page de garde de CHAQUE année (les papers et sections ont pu être réorganisés).
- Pour les Papers 2 et 3 : UN fichier PAR QUESTION, `numero_exercice` = le numéro imprimé (`"1"`, `"2"`... continu sur tout le sujet), sous-questions (a), (b)... = `questions`, `groupes` = le repère de la section imprimée
  (`["SECTION 1.1"]`, `["SECTION 5.3"]`..., 30 caractères MAXIMUM : abrège le titre au besoin, le titre complet reste dans l'énoncé de la première question de la section ou dans `introduction_markdown`).
  **`regles_choix` : `[]` partout** : « quatre questions d'UNE SEULE section » n'est pas exprimable avec `parmi` (un groupe) ni `ou` (sous-questions) ; ne code PAS « 4 sur N » par section (ce serait lu comme 4 par section). Recopie la consigne
  complète dans `introduction_markdown` et dis dans `incertitudes` que la règle « une seule section » n'est pas codable. `points` : le total imprimé (« 25 marks ») ; points des sous-questions entre crochets ; ne corrige jamais les points imprimés.
- `introduction_markdown` : la consigne de la page de garde (intitulé du paper compris), identique partout. `duree_epreuve` : `"1h30"` ou `"3h"`.

## Corrigés (exactitude avant tout)

- Anglais clair niveau Advanced. Réponse modèle d'un candidat qui obtient tous les points : introduction, développement structuré en arguments illustrés par des références PRÉCISES MAIS SÛRES (livre et passage biblique connu, sourate ou fait de la Sîra bien établi, institution ou rite reconnu),
  puis conclusion qui tranche (200 à 400 mots pour une question de 25 points ; un « (a) define... » court est court). Respecte « discuss », « examine », « assess », « justify », « evaluate », « to what extent », « outline », « how far ».
- **N'invente aucune référence** : ni verset, ni numéro de sourate, ni numéro de hadith, ni date, ni nom : cite seulement ce dont tu es certain (par exemple Luc 10 pour le bon Samaritain, Jean 11 pour Lazare, Actes 2 pour la Pentecôte). Quand le SUJET imprime une référence (« Al-Tirmizi No. 1924 »),
  recopie-la telle quelle sans la commenter. En cas de doute sur un fait précis, formulation prudente (« according to Islamic tradition », « the Gospel presents... ») et trace dans `incertitudes`.
- **Religions africaines traditionnelles (ATR)** : pas de traditions locales inventées ; reste au niveau des croyances et pratiques décrites par les auteurs classiques du programme (êtres suprêmes, divinités et esprits, ancêtres, sacrifices, fêtes, lieux sacrés, sorcellerie, vie après la mort, autorité,
  « I am because we are ») et note-le (« généralités, varient selon les peuples ») dans `incertitudes`.
- **Philosophie de la religion et éthique** : positions réelles de philosophes réels (Kant, Aristote, Aquin et les cinq voies, Hick et le theodicy, Flew et la falsification, Mill...), paraphrasées, jamais de citation inventée.
- **Neutralité** : décris, explique et évalue les croyances de chaque tradition de manière respectueuse, sans prêcher ni dénigrer ; évite toute affirmation de vérité d'une religion contre une autre : formule « Christians believe », « Muslims hold », « in ATR ».
- Une carte ou un schéma imprimés : suis la section Figures de `CONSIGNES.md` (skill `reproduire-figure-sans-filigrane`, jamais `pdftoppm`) ; `figures[].type` : 30 caractères MAXIMUM.

## Thèmes (`themes`) : collisions

`Tag.name` est UNIQUE et PARTAGÉ avec la plateforme francophone (histoire, philosophie, éducation civique) : un nom comme `islam`, `ramadan` ou `exodus` fusionnerait avec une variante d'accent ou de pluriel d'un tag français. **Tout thème commence par le préfixe `A Level Religious Studies - `**,
suivi d'un nom court en minuscules, explicite (jamais de thème sans préfixe). Exemples : `A Level Religious Studies - patriarchs of israel`, `... exodus and moses`, `... judges and the monarchy`, `... prophets of israel and judah`, `... five pillars of islam`, `... prophets in islam`,
`... festivals in islam`, `... women in islam`, `... atr supreme being and divinities`, `... atr festivals and sacred places`, `... atr witchcraft and magic`, `... gospel of luke`, `... gospel of john`, `... early church in acts`, `... paul and the corinthian church`,
`... attributes of god`, `... arguments for god's existence`, `... problem of evil`, `... ethics and moral theories`, `... religious experience`, `... pre-islamic arabia`, `... life of prophet muhammad`, `... rightly guided caliphs`, `... compilation of the quran`.
Avant d'en créer un, fais un `Grep` des valeurs `"themes"` dans `D:\edukora\backend\ingest\cm\gce-al-religion-*\*.json` et `_gce_staging\gce-al-religion-*\*.json` pour RÉUTILISER les noms des autres papers (plusieurs agents travaillent en parallèle : relis les dossiers des autres avant de créer un nom,
n'invente pas trois noms pour la même notion).

## Champs courts et contrôle final

`figures[].type`, `numero_exercice` et chaque repère de `groupes` : 30 CARACTÈRES MAXIMUM.

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --examen gce_al --paper <1|2|3> --code 0785 [--questions 50]
```

Il doit afficher `OK`. Vérifie en plus par script que chaque `themes` commence par `A Level Religious Studies - `. Puis la SECONDE PASSE obligatoire et déclarée (relire chaque page, refaire chaque question, corriger l'écart). Ne lance JAMAIS l'ingestion, ne touche ni à la base ni à Docker ni à git.
