## Étape E - Couverture quiz du lot (à ajouter au skill `tunnel-completude-edukora`, après l'étape D)

Un lot « propre » (étape D) n'est pas un lot « complet » : le tunnel signale seulement, en INFO, les
thèmes sans quiz VALIDE. Cette étape transforme ce constat en travail, sans jamais bloquer le lot.

**Quand** : après `TUNNEL VALIDÉ` sur tous les dossiers du lot. Ne jamais la lancer sur un lot dont
le tunnel n'est pas validé (générer des quiz sur un contenu non validé propage ses défauts).

### E1 - Mesurer la couverture du lot

Depuis un shell Django (`docker exec -i edukora-backend-1 python manage.py shell`), pour chaque leçon
du lot (`slug` visible dans le rapport) : thèmes de ses questions, dont ceux sans `CompetenceItem`
VALIDE. Noter le total, et le nombre de thèmes portés par au moins 2 questions du lot
(`select_quiz_batch` n'en propose pas de moins couverts : un thème porté par une seule question ne
définit pas une compétence, voir `SELECTION_MIN_QUESTIONS`).

### E2 - Sélectionner sur la matière du lot

```bash
MSYS_NO_PATHCONV=1 docker exec edukora-backend-1 python manage.py select_quiz_batch \
  --pays <pays> --matiere <CODE_MATIERE> --limit 5 --floor 6 --output /app/ingest/_quiz/_batch_<pays>_<lot>.json
```

`--matiere` reçoit le code de matière de la leçon (`PROGRAMMATION`, `SYSTEMES_INFORMATION`, `MATHS`...).
Jamais plus de 5 compétences par passe (coût et vérification rigoureuse item par item).

### E3 - Générer

Suivre le skill `concepteur-quiz-competence` pour chaque requête du fichier, une par une, en écrivant
`backend/ingest/_quiz/<pays>/<competence_slug>.json`. Reprendre `theme` tel quel (Tag existant),
`matiere` et `cursus` de la requête ; **omettre `savoir_officiel`** (en standby depuis le 2026-09-18).
Chaque valeur d'un corrigé doit être recalculée indépendamment (script Python, `sqlite3` pour du SQL)
avant d'être écrite : un script de génération qui échoue sur une divergence vaut mieux qu'une relecture.

### E4 - Ingérer puis valider

```bash
MSYS_NO_PATHCONV=1 docker exec edukora-backend-1 python manage.py ingest_quiz_content /app/ingest/_quiz/<pays>
bash scripts/tunnel_validation.sh <since>
```

Les erreurs `Champs obligatoires manquants ... item 0 - '?'` sur d'autres fichiers du dossier sont
d'anciens lots au mauvais format, pas ce lot : les lister à part (classe « Humain »), ne pas les
corriger dans ce passage. Le tunnel doit finir sur `TUNNEL VALIDÉ`.

### E5 - Rapport (complète le rapport final)

- Thèmes du lot : total, avec ≥ 2 questions, couverts avant/après.
- Compétences traitées et nombre d'items créés.
- **Reste à couvrir** : thèmes du lot encore sans quiz (à relancer par passes de 5, jamais en une fois).
- Un lot n'est « complet » qu'à couverture visée atteinte ; sinon il est « propre, couverture partielle »
  et le dit.

### Règles propres à l'étape E

- Ne jamais ingérer un item dont un recalcul indépendant diverge du corrigé.
- Un `theme` doit être le nom exact d'un Tag existant ; aucune variante inventée.
- Les items entrent `VALIDE` et sont servis aux élèves immédiatement : la vérification avant ingestion
  est la seule barrière.
