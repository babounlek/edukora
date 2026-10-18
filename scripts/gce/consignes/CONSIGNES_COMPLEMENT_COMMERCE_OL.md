# Complément aux consignes - GCE ORDINARY LEVEL, COMMERCE (code 0520)

Lis `CONSIGNES.md` (forme générale, LaTeX, figures), puis ce fichier. **Ce fichier prime** pour tout ce qui touche à Commerce : codes, noms de dossier, papers, règles de choix, corrigés, thèmes.
Niveau O Level (Form 5).

## Identité du sujet

- `examen` `"gce_ol"`, `serie` `null`, `pays` `"cm"`, `origine` `"officiel"`, `matiere` `"Commerce"`, `code_matiere` `"0520"` (page de garde : « ORDINARY LEVEL », « 0520 »).
  Autre matière, autre code ou autre niveau : ne transcris rien et signale-le.
- DOSSIER = `gce-ol-commerce-<annee>-p<paper>-officiel-cameroun` ; `epreuve_source` vaut `<DOSSIER>.pdf`. Sortie dans `D:\edukora\backend\ingest\_gce_staging\<DOSSIER>\` uniquement.

## Les deux papers

- **Paper 1** : 50 QCM, 1h30. UN fichier, `numero_exercice` `"1"`, questions `"1"` à `"50"`, `type_reponse` `"qcm"`, lettres `a` à `d` minuscules, `reponse_correcte` une lettre, `points` `""`, `groupes` `[]`,
  `regles_choix` `[]`. Un QCM de calcul commercial (remise, prix de revient, marge, TVA, intérêt, change) se justifie par le calcul recalculé avec Python. Un document imprimé (facture, chèque, bordereau)
  se recopie en tableau Markdown ou se recadre en PNG.
- **Paper 2** : 2h30, « Answer FOUR questions. All questions carry equal marks » (lis la page de garde de CHAQUE année : le nombre de questions et d'éventuelles sections peut changer ; calculatrice simple permise).
  UN fichier PAR QUESTION du sujet, `numero_exercice` = le numéro imprimé, sous-questions (a), (b), (c)... = `questions`. Sans sections : `groupes` `["PAPER 2"]` dans chaque fichier et
  `regles_choix` `[{"type":"parmi","portee":"PAPER 2","repondre":4,"sur":<N questions imprimées>}]`, identique dans TOUS les fichiers. Avec des sections à nombres imposés : une règle `parmi` par section (le minimum),
  `groupes` = le repère de section, consigne complète dans `introduction_markdown` et `incertitudes`. Points : « equal marks » ; `points` de l'exercice = le total imprimé s'il y en a un, sinon `""` ; points des
  sous-questions entre crochets.
- `introduction_markdown` : la consigne de la page de garde, identique dans tous les fichiers. `duree_epreuve` : `"1h30"` ou `"2h30"`.

## Corrigés

- Anglais clair niveau Form 5 : définitions précises du programme de Commerce (commerce et industrie, commerce de gros et de détail, canaux de distribution, publicité et promotion, transport et assurance,
  banques et moyens de paiement, documents commerciaux, commerce extérieur, entrepôts, protection du consommateur, organisations commerciales), exemples concrets (marché local, boutique, coopérative, banque, Douala, FCFA),
  introduction / développement / conclusion pour les questions longues. Respecte « define », « explain », « state », « distinguish », « calculate ».
- **Calculs commerciaux** (prix de revient, marge, remise commerciale ou de caisse, TVA, intérêts, taux de change, ristourne) : recalculés avec Python (`D:\edukora\venv\Scripts\python.exe`), formule, remplacement,
  résultat en FCFA ; les documents (facture, note de crédit, bon de commande, chèque) se recopient fidèlement en tableaux Markdown, totaux recalculés.
- **N'invente aucune statistique réelle, loi, taux d'imposition ou institution** : exemples hypothétiques (« suppose that... ») ; formulation prudente en cas de doute et trace dans `incertitudes`.
- Le `$` d'un prix s'écrit `\$` hors formule ; équation numérotée avec `\tag` : formule sur trois lignes. Un schéma imprimé (canal de distribution, chaîne de commerce) : suis la section Figures de `CONSIGNES.md`
  (skill `reproduire-figure-sans-filigrane`, jamais `pdftoppm`) ; `figures[].type` : 30 caractères MAXIMUM.

## Thèmes (`themes`)

1 à 3 noms anglais en minuscules, explicites, **propres à Commerce** : par exemple `channels of distribution`, `retail trade`, `wholesale trade`, `advertising and sales promotion`, `business documents`,
`invoices and credit notes`, `methods of payment`, `trade discounts and cash discounts`, `profit and mark-up calculations`, `insurance principles`, `warehousing`, `transport in commerce`, `communication services`,
`foreign trade documents`, `consumer protection`, `trade associations`, `commercial banking services`, `business ownership types`. `Tag.name` est UNIQUE et PARTAGÉ avec l'Economics (O et A Level), l'Accounting et le contenu
français : n'emploie pas un nom d'Economics (`demand and supply`, `international trade`, `money and banking`, `exchange rates`, `public finance`...), ni un mot identique en français (« assurance », « transport »,
« publicité » seuls...). Avant de créer un nom, fais un `Grep` des valeurs `"themes"` dans `D:\edukora\backend\ingest\cm\gce-*-economics-*\*.json` (pour NE PAS les réutiliser) et dans
`cm\gce-ol-commerce-*` et `_gce_staging\gce-ol-commerce-*` (pour RÉUTILISER les noms des autres papers de Commerce : plusieurs agents travaillent en parallèle, relis les dossiers des autres avant de créer un nom,
n'invente pas trois noms pour la même notion).

## Champs courts et contrôle final

`numero_exercice` et chaque repère de `groupes` : 30 CARACTÈRES MAXIMUM.

```
set PYTHONIOENCODING=utf-8
D:\edukora\venv\Scripts\python.exe D:\edukora\scripts\gce\valider_gce.py <dossier> --paper <1|2> --code 0520 [--questions 50]
```

Il doit afficher `OK`, puis la SECONDE PASSE obligatoire et déclarée (relire chaque page, refaire chaque question, corriger l'écart). Ne lance JAMAIS l'ingestion, ne touche ni à la base ni à Docker ni à git.
