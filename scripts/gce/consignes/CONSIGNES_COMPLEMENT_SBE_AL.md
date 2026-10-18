# Complément aux consignes - GCE ADVANCED LEVEL, SPECIAL BILINGUAL EDUCATION FRENCH (code 0746)

Lis `CONSIGNES.md` (forme générale, figures), puis `CONSIGNES_COMPLEMENT_AL.md` (niveau, identité, formats de papers), puis `CONSIGNES_COMPLEMENT_LANGUES_OL.md` (corrigés de langue : réponse modèle écrite avec soin, comptes de mots par script, thèmes préfixés),
puis ce fichier. **Ce fichier prime** pour cette matière : codes, noms de dossier, papers, règles de choix, langue des corrigés, thèmes.

## Identité du sujet

- `examen` `"gce_al"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"Special Bilingual Education French"`, `code_matiere` `"0746"` (page de garde : « ADVANCED LEVEL », « 0746 », intitulé « Special Bilingual Education French »).
  Autre matière, autre code ou autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-al-sbe-french-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`.
- Sources : `D:\edukora\backend\ingest\_telechargements_gce_2026-10-13\gcerevision_al_2019_2026\GCE_AL_SPECIAL_BILINGUAL_<ANNEE>_P<n>.pdf` (scans filigranés, couleur de fond verte ; lis chaque page en image avec Read, paramètre `pages`).
- Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Langue : FRANÇAIS

Le candidat répond « uniquement en français » (sauf la traduction vers l'anglais). Les énoncés sont recopiés tels qu'imprimés (français, avec accents et typographie). **Tes corrigés sont en français correct, naturel et de niveau Advanced**
(registre soutenu, plan apparent, citations d'œuvres seulement si tu es sûr), sauf la traduction vers l'anglais qui est en anglais. Rubriques de méthode (« Rappel de méthode ») en français.

## Les papers présents

- **Paper 2 : Literature / EPS / ECM** (3 h) : « Le candidat traitera quatre sujets au choix : deux de la section I, un de la section II, un de la section III. Tous les sujets valent 20 points. » (vérifie le texte imprimé).
  Section I Littérature (poésie, théâtre, roman : six sujets numérotés 1 à 6 ; « Le candidat traitera deux sujets de genres différents ») ; Section II Éducation physique et sportive (deux sujets, 7 et 8) ; Section III Éducation à la citoyenneté et à la morale (deux sujets, 9 et 10, dont une analyse de texte).
  UN fichier PAR SUJET, `numero_exercice` = le numéro imprimé (`"1"`... `"10"`), `groupes` `["SECTION I"]`, `["SECTION II"]`, `["SECTION III"]`, `points` `"20"`. `regles_choix`, identiques dans TOUS les fichiers du dossier :
  `{"type":"parmi","portee":"SECTION I","repondre":2,"sur":6}`, `{"type":"parmi","portee":"SECTION II","repondre":1,"sur":2}`, `{"type":"parmi","portee":"SECTION III","repondre":1,"sur":2}`.
  L'exigence « deux genres différents » n'est pas codable : recopie la consigne complète dans `introduction_markdown` et signale-la dans `incertitudes`.
- **Paper 3 : Essay writing and Translation** (3 h) : « Répondez à UNE SEULE question de la SECTION I et à TOUTES LES DEUX QUESTIONS de la SECTION II » (Section I : Rédaction, 40 %, trois sujets au choix, 400 mots ; Section II : Traduction, 60 %, 1. Traduisez en français, 2. Translate into English).
  Un fichier par sujet de rédaction (`numero_exercice` `"1"`, `"2"`, `"3"` ou `"I-1"`... selon le numérotage imprimé, `groupes` `["SECTION I"]`, `regles_choix` `[{"type":"parmi","portee":"SECTION I","repondre":1,"sur":3}]`)
  et un fichier par traduction (`groupes` `["SECTION II"]`, aucune règle car les deux sont obligatoires ; `points` : l'imprimé, sinon `""` avec les pourcentages de la page de garde dans `introduction_markdown`). Recopie les textes à traduire EN ENTIER et fidèlement.
  Corrigés : un essai modèle COMPLET de 400 mots environ (compte par script, hors titres), avec plan, argument, exemples précis et camerounais le cas échéant, puis critères (maîtrise de la langue, contenu, présentation) et deux erreurs fréquentes ;
  les traductions modèles COMPLÈTES, précises, suivies d'un tableau « difficulté / piège / bonne forme » de 6 à 10 lignes.
- Le Paper 1 (QCM) n'est pas dans les sources : ne crée rien pour lui.

## Corrigés : exactitude

- **Littérature (œuvres au programme)** : La Fontaine (fables), Racine, Jean Pliya (La Secrétaire particulière), Cheikh Hamidou Kane (L'aventure ambiguë), Bernard Nanga (Les Chauves-souris), Jacques Chevrier et le poème de Camara Laye ou de Sikhé cité dans le sujet : réponds avec les faits
  SÛRS des œuvres (personnages, situations générales, procédés) et n'invente ni citation, ni numéro de page, ni détail d'intrigue douteux ; un détail dont tu n'es pas certain reçoit une formulation générale et une ligne dans `incertitudes` (« œuvre non relue ici »).
  Le poème ou texte imprimé dans le sujet se cite tel qu'imprimé.
- **EPS et ECM** : réponses argumentées, exemples précis mais prudents (dates et faits historiques : seulement ceux dont tu es sûr ; le sujet 9 « Le Cameroun et l'ONU (1946-1961) » : chronologie générale, sans date douteuse, `incertitudes` en cas de doute).
  Analyse de texte (sujet 10, texte de Paul Biya) : recopie le texte et la consigne, analyse ce que le texte dit, sans position partisane.
- Pas de tiret cadratin ; guillemets français « » dans les textes de corrigé.

## Thèmes (`themes`) : collisions

`Tag.name` est UNIQUE et PARTAGÉ avec des centaines de thèmes de français (BEPC, Probatoire, BAC) et d'éducation civique. **Tout thème commence par le préfixe `A Level SBE French - `**, suivi d'un nom court en minuscules, en français (ou en anglais pour la traduction vers l'anglais) :
`A Level SBE French - poesie de la fontaine`, `... theatre classique et africain`, `... roman africain`, `... redaction argumentative`, `... traduction vers le francais`, `... traduction vers l'anglais`, `... education physique et sportive`, `... education civique et nationalisme`, `... analyse de texte`.
Réutilise les noms entre les deux papers (relis `D:\edukora\backend\ingest\_gce_staging\gce-al-sbe-french-*` avant de créer un nom : un autre agent travaille en parallèle sur l'autre paper). Pas d'accents dans les noms de thèmes (cohérent avec les autres matières GCE ci-dessus).

## Champs courts et contrôle final

`figures[].type`, `numero_exercice` et chaque repère de `groupes` : 30 CARACTÈRES MAXIMUM.

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --examen gce_al --paper <2|3> --code 0746
```

Il doit afficher `OK`. Vérifie en plus par script que chaque `themes` commence par `A Level SBE French - ` et que les `regles_choix` sont identiques dans tous les fichiers du dossier. Puis la SECONDE PASSE obligatoire et déclarée (relire chaque page, refaire chaque question, corriger l'écart).
Ne lance JAMAIS l'ingestion, ne touche ni à la base ni à Docker ni à git.
