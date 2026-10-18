# Complément aux consignes - GCE ORDINARY LEVEL, CITIZENSHIP EDUCATION (code 0562)

Lis `CONSIGNES.md` (forme générale, figures), puis ce fichier. **Ce fichier prime** pour tout ce qui touche à Citizenship Education : codes, noms de dossier, papers, règles de choix, exactitude, thèmes.
Niveau O Level (Form 5).

## Identité du sujet

- `examen` `"gce_ol"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"Citizenship Education"`, `code_matiere` `"0562"` (page de garde : « ORDINARY LEVEL », « 0562 »).
  Autre matière, autre code ou autre niveau : ne transcris rien et signale-le. (Le PDF 2026 s'appelle « CITIZENSHIP EDUCATION » : même matière.)
- DOSSIER = `gce-ol-citizenship-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`. Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les deux papers

- **Paper 1** : 50 QCM, 1h30. UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"`, `type_reponse` `"qcm"`, lettres `a` à `d` minuscules, `reponse_correcte` une lettre, `points` `""`, `groupes` `[]`, `regles_choix` `[]`.
  Un QCM factuel dont deux options sont défendables, ou dont le fait imprimé est inexact : convertis en `ouverte` (`node D:\edukora\scripts\gce\convertir_en_ouverte.js <fichier.json> <numero...>`), jamais une lettre au hasard.
- **Paper 2** : 2h30, questions rédigées. Page de garde (à relire CHAQUE année ; exemple 2023) : « answer FOUR questions, choosing QUESTION 1 and THREE others from Sections A, B and C ; extra questions answered
  from each section shall not be marked ». UN fichier PAR QUESTION du sujet, `numero_exercice` = le numéro imprimé, sous-questions (a), (b), (c)... = `questions`, `groupes` = le repère de section (`["SECTION A"]`...) ;
  la question 1, quand elle est hors section, porte `groupes` `["COMPULSORY"]`. `regles_choix`, identiques dans TOUS les fichiers du dossier : une règle `parmi` par section à choix
  (`{"type":"parmi","portee":"SECTION A","repondre":1,"sur":<N de la section>}`, etc. : lis le sujet pour savoir combien de questions il faut traiter dans chaque section), rien pour la question 1 obligatoire.
  Recopie la consigne complète dans `introduction_markdown` ; ce qui n'est pas exprimable va dans `incertitudes`. Points : ceux imprimés dans `points` de l'exercice ; points des sous-questions entre crochets.
- `introduction_markdown` : la consigne de la page de garde, identique partout. `duree_epreuve` : `"1h30"` ou `"2h30"`.

## Corrigés (exactitude avant tout)

- Anglais clair niveau Form 5 : réponse modèle complète, introduction / développement / conclusion pour les questions longues ; respecte « define », « state », « explain », « outline », « discuss », « identify ».
  Programme : citoyenneté, droits et devoirs, constitution et institutions du Cameroun (exécutif, législatif, judiciaire, collectivités décentralisées), élections, valeurs civiques, droits de l'homme,
  organisations internationales et régionales (ONU, Union africaine, CEMAC, Commonwealth, Francophonie), environnement et développement durable, santé et VIH/SIDA, sécurité routière, vie en société.
- **N'invente aucun article de loi, numéro d'article, date, chiffre, nom d'institution ou de personne** : formulation générale et prudente (« the Constitution provides that... », « in the early 1960s ») quand tu
  n'es pas certain ; trace dans `incertitudes` tout fait que tu n'as pas pu établir avec certitude (par exemple une composition, un mandat ou un calendrier d'institution qui change dans le temps).
  Pas de position politique partisane : réponse factuelle et civique.
- Une carte ou un tableau imprimé : suis la section Figures de `CONSIGNES.md` (skill `reproduire-figure-sans-filigrane`, jamais `pdftoppm`) ; `figures[].type` : 30 caractères MAXIMUM.

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, explicites, **qualifiés** : par exemple `cameroon constitution and state institutions`, `rights and duties of citizens`, `civic values and responsibilities`, `elections and voting`,
`human rights protection`, `decentralisation and local councils`, `international and regional organisations`, `environmental protection and sustainable development`, `road safety and traffic rules`,
`hiv and aids prevention`, `national unity and bilingualism`, `family and community life`. `Tag.name` est UNIQUE et PARTAGÉ avec l'Éducation civique française (ECM) et les autres matières : n'emploie pas un mot qui existe
tel quel en français (« constitution », « citoyenneté », « élection », « environnement », « décentralisation » seuls...), ni une variante d'accent ou de pluriel d'un thème français : préfère des noms qualifiés de 2 à 4 mots.
Avant de créer un nom, fais un `Grep` des valeurs `"themes"` dans `D:\edukora\backend\ingest\cm\gce-ol-citizenship-*\*.json` et `_gce_staging\gce-ol-citizenship-*\*.json` pour RÉUTILISER les noms des autres papers
(plusieurs agents travaillent en parallèle : relis les dossiers des autres avant de créer un nom, n'invente pas trois noms pour la même notion).

## Champs courts et contrôle final

`figures[].type`, `numero_exercice` et chaque repère de `groupes` : 30 CARACTÈRES MAXIMUM.

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --paper <1|2> --code 0562 [--questions 50]
```

Il doit afficher `OK`, puis la SECONDE PASSE obligatoire et déclarée (relire chaque page, refaire chaque question, corriger l'écart). Ne lance JAMAIS l'ingestion, ne touche ni à la base ni à Docker ni à git.
