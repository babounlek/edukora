# B6 : cours « systèmes d'équations » en BEPC, quoi garder (proposition, rien n'est modifié)

Date : 2026-10-26. Origine : test élève Guyguy, « 17 cours pareils, lequel je prends ? ».

## Constat corrigé

Sur les 39 cours dont le sous-thème est « systèmes d'équations », **seulement 13 sont dans le cursus BEPC** (par la lignée de leurs épreuves sources). Les 26 autres sont des cours de Probatoire A/D, de BAC A/C/D/E ou de Chimie : ils n'apparaissent pas dans une liste BEPC filtrée. Les « 39 quasi doublons dont des cours de Terminale » que j'avais annoncés surestimaient donc le problème BEPC ; les 17 cours vus par Guyguy venaient de ces 13 plus des cours trouvés par le texte de la recherche.

## Les 13 cours du BEPC, groupés par méthode

| Méthode | Cours | Sources | Fréquence BEPC | Proposition |
|---|---|---|---|---|
| Substitution | **7989** La méthode de substitution pour résoudre un système d'équations | 2 | 56 % | **Garder** (référence) |
| | 5802 La résolution d'un système … par substitution | 2 | | Doublon de 7989 : retirer ou fusionner |
| Combinaison | **11431** … par combinaison (addition ou soustraction) | 1 | | **Garder** (référence) |
| | 3362 … par soustraction | 1 | | Cas particulier de 11431 : retirer ou fusionner |
| Égalisation | **7277** … par la méthode d'égalisation | 1 | | **Garder** |
| Mise en équation | **7309** Traduire un problème en système d'équations | 1 | 56 % | **Garder** (référence) |
| | **5575** Résoudre un problème d'achat par un système d'équations | 2 | 56 % | **Garder** (type de problème très fréquent) |
| | **3388** … issu d'une situation concrète | 6 | | **Garder** (le mieux sourcé) |
| | 3435 … périmètre d'un rectangle sous deux transformations | 1 | | Cas trop particulier : retirer |
| Présenter la réponse | **5577** Écrire correctement l'ensemble solution | 2 | | **Garder** (c'est une consigne de rédaction, pas un doublon) |
| Lecture graphique | **7412** Interprétation graphique de la solution d'un système | 1 | | **Garder** |
| Hors thème ou hors niveau | 4037 Résoudre graphiquement un système d'**inéquations** de signe sur plusieurs fonctions | 0 | | **Retirer du BEPC** (aucune épreuve source, niveau supérieur) |
| | 5967 Déterminer deux effectifs inconnus … **somme et moyenne** | 0 | | Plutôt un cours de statistiques : rattacher à ce thème ou retirer d'ici |

Résultat si tout est suivi : **13 → 8 cours** (7989, 11431, 7277, 7309, 5575, 3388, 5577, 7412).

## Un cas à part

**11621** « Résoudre un système de deux équations linéaires par combinaison » : sans cursus, sans épreuve source, il ne sort dans aucune liste BEPC. C'est un doublon de 11431 déjà orphelin ; à retirer.

## Comment « retirer » sans rien détruire

La convention du projet est de ne jamais supprimer : un retrait = statut REJETE (le cours reste en base, disparaît du site). Un cours REJETE ne peut pas être lu par un élève qui aurait gardé un lien : à vérifier avant d'appliquer s'il existe des lectures en cours (`LectureProgress`) sur ces cours (3388, 5575, 7989, 11431 sont les plus probables d'en avoir).

## Décisions à prendre

1. Valider le tableau ci-dessus (ou me dire quels cours garder en plus).
2. **Retirer = passer en REJETE** (recommandé) ou seulement les écarter de la liste BEPC ? Écarter sans retirer est possible si ces cours servent à d'autres examens, mais le modèle n'offre pas de bouton « masquer pour un examen » : il faudrait ajouter un champ.
3. Même traitement pour les autres thèmes proches (la même analyse peut se refaire en une requête pour tous les sous-thèmes du BEPC qui ont plus de 6 cours).

Aucune base n'a été modifiée. La requête d'analyse est reproductible (sources, lignée BEPC, fréquence).
