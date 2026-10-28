# Brief commun : rédiger les COURS associés aux rappels de méthode d'une épreuve francophone du Cameroun (2026-10-27)

Tu reçois : un NOM DE DOSSIER d'épreuve déjà ingéré. Tu rédiges un cours complet (7 sections) pour chaque entrée de `a_rediger` du plan de ce dossier. Les épreuves et leurs exercices existent déjà ; ne les modifie JAMAIS.

## 1. Fichiers
- Plan : `D:\edukora\backend\ingest\_cm_plan_cours\<DOSSIER>.json` : liste `a_rediger` (cours à écrire). Chaque entrée donne : `titre_exact` (à recopier tel quel dans `meta.titre`, accents compris), `matiere`, `examen`, `serie`, `niveau`, `rappel_id`, `exercice_numero`, `sous_question`, `rappels_lies`, `contenu_rappel` (le rappel de méthode d'origine, à développer), `cours_id` (à recopier tel quel). Les squelettes (`squelettes`) sont faits par un script : ne les écris pas.
- Exercices sources : `D:\edukora\backend\ingest\cm\<DOSSIER>\*_exercice_<N>.json` : lis l'énoncé et le corrigé de l'exercice/sous-question d'où vient le rappel, pour en tirer l'exemple résolu (`epreuve_source: true`).
- Sortie : `D:\edukora\backend\ingest\_cm_staging_cours\<DOSSIER>\<DOSSIER>_cours_<slug>.json`, un fichier par entrée de `a_rediger` (slug = `cours_id` sans le préfixe `cours-` ni le suffixe dossier ; tout slug minuscule sans accent est accepté tant que le nom contient `_cours_`). Crée le dossier. N'écris nulle part ailleurs ; fichiers temporaires dans un sous-dossier propre à toi du scratchpad (jamais un nom générique partagé comme p1.png).
- Modèles de style (cours déjà ingérés) : `D:\edukora\backend\ingest\cm\bepc-maths-2022-officiel-cameroun\*_cours_*.json` (schéma exact) et, pour ta matière, un cours d'un dossier voisin de `cm/` (même matière, même examen).

## 2. Lecture (une fois)
Lis le skill `correction-experte` : `C:\Users\Administrateur\AppData\Local\Claude-Data\claude_pzs8sxrjxfjjc\local-agent-mode-sessions\skills-plugin\b753a7e6-84a4-4175-9017-11ed073d6178\109e0e24-b249-4600-8c4f-284c2f0b64eb\skills\correction-experte\SKILL.md`, sections : Style rédactionnel (pas de marqueurs IA, PAS DE TIRET CADRATIN), `$` protégé, LaTeX/backslash doublés dans le JSON, accents, et SURTOUT « Mode cours » (principe, 7 sections, format JSON, règles de qualité). IGNORE la partie « Génération des cours en lot » sur les squelettes et le catalogue : ici le plan dit déjà quoi écrire.

## 3. Schéma d'un cours (identique au modèle de `bepc-maths-2022`)
```
{
 "cours_id": <plan.cours_id>,
 "meta": {"titre": <plan.titre_exact>, "matiere": <plan.matiere>, "pays": "cm", "niveau": <plan.niveau>,
          "serie": <plan.serie, ou null>, "sous_theme": "...", "duree_estimee_min": 25-40,
          "tags": [3 à 6 thèmes, formes EXACTES déjà utilisées dans les `themes` des exercices de ce dossier ou des dossiers voisins de cm/],
          "savoir_officiel": null, "statut": "brouillon"},
 "source": {"epreuve_id": "<DOSSIER>", "exercice_numero": "<plan.exercice_numero>", "rappel_id": <plan.rappel_id>,
            "rappels_lies": <plan.rappels_lies>, "correction_id": null},
 "sections": [ accroche, prerequis, regle, exemple_resolu, erreurs_classiques, exercices_application, synthese ]  (cet ordre, ces `type`)
}
```
Détail des sections et des clés : voir le modèle de `bepc-maths-2022` et le « Mode cours » du skill (`accroche.contenu_markdown` ; `prerequis.items` ; `regle.titre/contenu_markdown/formule_principale` (formule LaTeX réelle ou absente, jamais du code) `/variantes` ; `exemple_resolu.enonce_markdown/epreuve_source/etapes[numero,action,justification,resultat_markdown]/conclusion_markdown` ; `erreurs_classiques.items[erreur_markdown,pourquoi_faux,correction_markdown]` (2 à 4) ; `exercices_application.items[numero,difficulte facile|moyen|approfondissement,enonce_markdown,solution_markdown]` (3, SOLUTIONS COMPLÈTES, aucune étape masquée) ; `synthese.items_markdown` (4 à 6)).
- `meta.titre` = `titre_exact`, jamais reformulé. `meta.serie`, `meta.matiere` = ceux du plan (Série TI : jamais « Informatique »).
- Le cours enseigne la NOTION du rappel de manière générale (le rappel et la question d'origine servent d'ancrage, l'exemple résolu vient de l'exercice source). Il est utile à un élève qui n'a jamais vu la notion : jamais une paraphrase du rappel. Niveau calibré à l'examen (BEPC = 3e : plus détaillé).
- Matières : maths/physique/chimie = calculs refaits par script Python (`C:\ProgramData\anaconda3\python.exe -I`), unités, valeurs numériques exactes ; langues (allemand, français, espagnol...) = contenu dans la langue pédagogique du cours (explications en français, exemples en langue cible avec traduction) ; philosophie/histoire/lettres = auteurs, dates, œuvres cités avec prudence (aucun fait douteux ; en cas de doute, formule générale sans date ni citation inventée).
- Aucune donnée inventée présentée comme officielle ; l'exemple résolu issu de l'épreuve respecte l'énoncé du JSON source.
- Pas de tiret cadratin ni demi-cadratin ; accents partout (hors identifiants et code) ; tout `$` hors formule est protégé (span de code) ; backslashes LaTeX doublés dans le JSON (`\\frac`, `\\times`...) ; recharge chaque JSON avec `json.load` et vérifie qu'aucune chaîne ne contient de tabulation, `\x08` ni `\x0c`.
- Figures : aucune (pas de PNG pour les cours ; décris en Markdown/tableaux ; un tracé nécessaire se dit en mots et en tableau de valeurs).

## 4. Contrôle (obligatoire)
`C:\ProgramData\anaconda3\python.exe -I D:\edukora\scripts\cm\verifier_cours.py D:\edukora\backend\ingest\_cm_staging_cours\<DOSSIER> D:\edukora\backend\ingest\cm\<DOSSIER> D:\edukora\backend\ingest\_cm_plan_cours\<DOSSIER>.json` doit afficher `COURS PROPRES` (aucun `[BLOQUANT]`). Ne lance JAMAIS l'ingestion ; ne touche ni à la base, ni à Docker, ni à git, ni aux épreuves.
**Seconde passe obligatoire** après l'écriture : relis chaque cours comme un élève qui découvre la notion ; refais chaque calcul / chaque solution des 3 exercices une seconde fois. Un cours commencé se termine intégralement (7 sections, 3 solutions complètes) ; si le volume te presse, livre moins de cours plutôt que des cours bâclés et dis lesquels manquent.

## 5. Rapport (court)
Dossier, nombre de cours livrés / attendus, sortie du validateur, tags créés (hors formes existantes), doutes de fond (faits, dates, citations), seconde passe oui/non et ce qu'elle a corrigé.
