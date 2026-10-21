# Complément aux consignes - GCE ORDINARY LEVEL, RELIGIOUS STUDIES (code 0585)

Lis `CONSIGNES.md` (forme générale, LaTeX, figures), puis ce fichier. **Ce fichier prime** pour tout ce qui touche à la Religious Studies O Level : codes, noms de dossier, papers, clés de QCM, exactitude, neutralité, thèmes.
Niveau O Level (Form 5). Pour l'A Level (0785), voir `CONSIGNES_COMPLEMENT_RELIGION_AL.md` : les deux ne se mélangent pas.

## Identité du sujet

- `examen` `"gce_ol"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"Religious Studies"`, `code_matiere` `"0585"` (page de garde : « ORDINARY LEVEL », « 0585 RELIGIOUS STUDIES 1 »).
  Autre matière, autre code ou autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-ol-religion-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`. Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.
- **Sources** : des copies de sites tiers (MeetLearn...), parfois mal nommées (un fichier « Advanced Level Paper 1 2018 » peut contenir un sujet O Level). **Le nom du fichier ne fait pas foi** : l'année, le niveau, le code et le numéro de paper sont ceux de la PAGE DE GARDE IMPRIMÉE du sujet.
  Si la page de garde imprimée manque (page couverture du site seule), lis le premier feuillet du sujet lui-même (« JUNE 20xx », « 0585 RELIGIOUS STUDIES 1 »). Un site peut intituler « Paper 2 » un QCM de 50 questions : s'il s'agit d'un QCM de 50 questions « Answer ALL the 50 questions », c'est le Paper 1.
- **Annotations manuscrites** : certains scans portent des lettres cochées, barrées ou entourées au stylo (réponses d'un candidat, de l'ancien propriétaire du sujet, ou d'un site). **Ne t'en sers JAMAIS comme clé** : elles ne sont pas officielles et peuvent être fausses. Établis chaque clé toi-même, puis note dans `incertitudes` que le scan porte des annotations ignorées.

## Le Paper 1 (QCM)

50 QCM, 1h30. UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"`, `type_reponse` `"qcm"`, lettres `a` à `d` minuscules, `reponse_correcte` une lettre, `points` `""`, `groupes` `[]`, `regles_choix` `[]`, `duree_epreuve` `"1h30"`.
Les rubriques imprimées (par exemple « PERSONAL AND SOCIAL RELATIONSHIPS AND PROBLEMS », Ancien et Nouveau Testament, Islam, religions africaines traditionnelles) ne sont pas des groupes d'exercice : ne les mets pas dans `groupes` ; recopie-les dans `introduction_markdown` et sers-t'en pour les thèmes.
`introduction_markdown` : la consigne de la page de garde (consignes aux candidats), identique pour tout le dossier.

## Corrigés (exactitude avant tout)

- Aucun corrigé officiel : chaque clé est établie sur un fait CLASSIQUE du programme O Level (morale chrétienne et sociale, vocabulaire de la famille, du mariage, de la justice, des droits de l'homme, de la sexualité, de l'amitié, du travail,
  de la drogue, de la conscience ; Bible ; Islam ; religions africaines traditionnelles). Le corrigé d'un QCM dit en une ou deux phrases pourquoi l'option est la bonne et pourquoi les autres ne conviennent pas, et se termine par « **Answer: C.** ».
- **Un QCM dont deux options sont défendables, dont la clé dépend d'une convention de manuel local, d'un sujet controversé ou d'une croyance propre à une tradition, ou dont l'énoncé est défectueux : convertis en `ouverte`** (`node D:\edukora\scripts\gce\convertir_en_ouverte.js <fichier.json> <numero...>`),
  jamais une lettre au hasard. Au moins une dizaine de conversions sont normales pour cette matière.
- **N'invente aucune référence** (verset, sourate, hadith, date, nom, article de loi). Le sujet imprime parfois une citation : recopie-la telle quelle.
- **Neutralité** : décris et explique sans prêcher ni dénigrer (« Christians believe », « Muslims hold », « in ATR »). Pour une question qui appelle un jugement moral contesté, la clé est celle du programme (morale chrétienne et civique classique) formulée comme telle (« according to Christian teaching ... »),
  et le doute va dans `incertitudes`.
- Les énoncés défectueux ou fautifs du sujet imprimé (fautes de frappe, option manquante) sont recopiés tels quels et notés dans `incertitudes`.

## Thèmes (`themes`)

1 à 2 noms anglais en minuscules, **tous préfixés `O Level Religious Studies - `** (le préfixe évite toute fusion avec les thèmes français et avec ceux de l'A Level, préfixés `A Level Religious Studies - `). Exemples : `O Level Religious Studies - friendship and love`, `... marriage and family`, `... sexuality and chastity`,
`... justice and human rights`, `... conscience and moral choice`, `... drugs and substance abuse`, `... work and unemployment`, `... corruption and embezzlement`, `... hiv and aids`, `... civil liberties`, `... sects and cults`, `... old testament`, `... new testament`, `... islam`, `... african traditional religion`.
Avant de créer un nom, fais un `Grep` des valeurs `"themes"` dans `D:\edukora\backend\ingest\_gce_staging\gce-ol-religion-*\*.json` pour RÉUTILISER les noms des autres sujets (plusieurs agents travaillent en parallèle : relis les dossiers des autres avant de créer un nom).

## Champs courts et contrôle final

`figures[].type`, `numero_exercice` et chaque repère de `groupes` : 30 CARACTÈRES MAXIMUM.

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --paper 1 --code 0585 --questions 50
```

Il doit afficher `OK`. Vérifie en plus par script que chaque `themes` commence par `O Level Religious Studies - `. Puis la SECONDE PASSE obligatoire et déclarée (relire chaque page, refaire chaque question, corriger l'écart). Ne lance JAMAIS l'ingestion, ne touche ni à la base ni à Docker ni à git.
