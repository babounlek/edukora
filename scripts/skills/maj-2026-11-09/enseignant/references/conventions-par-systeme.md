# Conventions par système : ce qu'un correcteur d'examen attend

Le cahier des charges des corrigés est écrit dans le skill `correction-experte` (sections « Référentiel », « Mode GCE », « Spécificités pédagogiques par matière », « Registre, niveau de langue et profondeur »). Les lire comme une **norme à laquelle le contenu doit se conformer**, pas comme un raisonnement à suivre : un manquement est un constat E3 ou E4, une erreur scientifique reste E1 quelle que soit la norme. Cette fiche ne répète pas ces sections : elle liste ce que l'enseignant vérifie en plus, ou différemment.

## Francophone (BEPC/BFEM, Probatoire, BAC ; Cameroun, Sénégal, Côte d'Ivoire, Bénin)

- **Cursus** : le contenu est-il au programme de CET examen et de CETTE série ? Le BEPC n'a pas de série ; le Probatoire existe au Cameroun seulement ; un exercice de Terminale C n'est pas un exercice de BEPC même s'il est juste. Pour le Cameroun, utiliser `programme.Module/Savoir` ; pour les autres pays, le référentiel n'est pas garanti : le dire plutôt que trancher.
- **Mathématiques** : théorème cité avec son nom ; forme indéterminée écrite avant d'être levée ; tableau de variations pour une étude de fonction ; branches infinies traitées ; domaine de définition posé ; réciproque et contraposée non confondues ; arrondis et nombre de chiffres significatifs cohérents avec l'énoncé.
- **Physique-chimie** : loi littérale → application numérique → résultat AVEC unité ; ordres de grandeur plausibles ; équation chimique équilibrée avant toute stœchiométrie ; chiffres significatifs.
- **SVT** : vocabulaire conforme au programme ; schéma avec titre, légendes numérotées et sens des flèches ; format demandé respecté (texte, schéma, tableau).
- **Français** : introduction (accroche, problématique, annonce du plan), développement, conclusion, notés séparément ; plusieurs plans peuvent être valables, ne pas imposer le sien ; exemples tirés des œuvres du programme.
- **Philosophie** : problématisation en introduction, concepts définis, auteurs du programme avec leur thèse (une attribution fausse est une E1), plan dialectique ou conforme à la consigne.
- **Histoire-géographie** : dates et lieux situés ; État, nation, pays, territoire non confondus ; faits datés vérifiables (une date fausse est une E1).
- **Anglais (francophone)** : réponses complètes avec citation et reformulation ; format de production imposé (formal letter, essay, summary) respecté ; les exercices à choix fermé donnés en ligne sont des QCM : `choix` et `reponse_correcte` attendus.
- **Économie / Droit** : concepts définis avant usage ; graphiques légendés ; déplacement et glissement de courbe distingués.
- **Musique (Probatoire A)** : notes en notation française ; degrés de la gamme (I tonique, II sus-tonique, III médiante, IV sous-dominante, V dominante, VI sus-dominante, VII sensible) ; série de quatre notes = tétracorde ; chaque note d'un tracé sur portée contrôlée sur la bonne ligne ou le bon interligne. Faits d'histoire et d'instruments recoupés : une date ou un nom propre non vérifiable est un constat, pas une évidence.
- **Travail manuel (Probatoire A)** : épreuve à sujets au choix (un seul à traiter) ; devis recalculé (quantités × prix unitaires, total) ; faits techniques exacts (outils, étapes agricoles et d'élevage, sécurité électrique) ; critères de notation d'un dessin ou d'une réalisation explicites ; corrigé modèle plausible et non unique.
- **Registre** : corps du corrigé académique, blocs « Piège » et « Conseil » au tutoiement ; profondeur calibrée au niveau (BEPC plus détaillé que Terminale). Pas de jargon non expliqué à la première occurrence. Marqueurs d'écriture automatique à signaler en E4 (voir `correction-experte`, « Style rédactionnel »).

## GCE (Cameroun anglophone, O Level et A Level)

Ces règles PRIMENT sur les règles francophones pour tout contenu GCE.

- **Langue** : anglais clair, niveau Form 5 pour l'O Level ; orthographe cohérente (britannique, en usage au Board : le mélange britannique/américain dans un même document est un E4) ; contextes locaux (FCFA, Douala, Bamenda) ; `g = 10 m s^-2` ; calculatrice permise. Du français dans un contenu GCE (hors champ `incertitudes`) est un constat.
- **Pas de séries** : le GCE a des **matières** et des **papers** ; `numero_paper` 1 = QCM, 2 = rédigé ; un code matière du jury doit correspondre à la matière.
- **Paper 1** : 50 QCM, options a-d, une seule lettre correcte. Une clé imprimée fausse, ou une bonne valeur absente des options, doit avoir été traitée en question ouverte (voir `correction-experte`) : si le contenu garde un QCM dont aucune option n'est juste, c'est une E1.
- **Points** : les points imprimés du sujet ne se corrigent jamais, même s'ils ne somment pas ; une somme incohérente est notée en E4 « barème du sujet », jamais « corrigée ».
- **Aucun corrigé officiel** : tout corrigé GCE est écrit par l'auteur et doit être juste ; l'enseignant recalcule donc CHAQUE valeur, pas un échantillon, pour les épreuves scientifiques.
- **Syllabus** : pas de référentiel `programme` en base ; juger le niveau par le syllabus du Board et la difficulté de l'O Level. Dire quand on ne peut pas trancher.
- **Thèmes** : noms anglais courts en minuscules ; un thème anglais identique à un thème français fusionne avec lui (`Tag.name` est unique et partagé) : un thème ambigu est un constat E3.
- **Pas de « Rappel de méthode »** dans un corrigé d'épreuve GCE à la transcription (ajouté après ingestion à partir des cours).

## Ce qui ne relève pas de l'enseignant

- Rendu KaTeX/Markdown cassé : `audit-qualite-rendu`.
- Structure du lot, thèmes manquants, couverture quiz : `tunnel-completude-edukora`, `couverture-quiz-lot-edukora`.
- Couverture du programme officiel : `audit-couverture-programme`.
- Vécu de l'élève à l'écran : `eleve`.
