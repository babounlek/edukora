# Sources des 4 mini-inedites ecrites a la main (maths)

Copie de sauvegarde des JSON d'ingestion (blueprint `bp-` + epreuve `ep-`) de : BAC C, BAC D et TI, BAC E, Probatoire D et TI.
Les originaux vivent dans `backend/ingest/_inedit/cm/` (ignore par git) ; les epreuves sont aussi en base de production.
Pour les reingerer : copier les fichiers dans `backend/ingest/_inedit/cm/`, ingerer d'abord les `bp-` (statut VALIDE requis), puis les `ep-`.

## Ajout du 2026-11-03 : 10 minis de plus (n°2 et n°3)

BAC C n°2 et n°3, BAC E n°2 et n°3, BAC D et TI n°2 et n°3, Probatoire D et TI n°2 et n°3, Probatoire C et E n°2 et n°3.
Les JSON `bp-` / `ep-` correspondants sont dans ce dossier. Le dossier `generateur/` contient le generateur (`minigen.py`) et un fichier de
specification par cursus (`spec_*.py`) : modifier le texte dans la specification puis relancer le fichier (`python spec_bac_c.py`) regenere les JSON
dans `backend/ingest/_inedit/cm/` (le chemin de sortie est en tete de `minigen.py`).
Apres ingestion : passer le blueprint en VALIDE, ingerer l'epreuve, marquer `est_mini=True` (sources_mini vide), publier, puis `creer_mini_inedites` genere les PDF.
Relecture : 3 relecteurs independants (resolution a l'aveugle puis comparaison), aucun constat bloquant ; corrections appliquees (formes trigonometriques,
grilles, enonces precises, Probatoire D/TI n°3 exercice 2 remonte au niveau Premiere avec le produit scalaire). Pas encore relues par un enseignant humain.

## Ajout du 2026-11-03 (2) : 12 minis de physique et de chimie

Physique : BAC C et E n°1-2, BAC D et TI n°1-2, Probatoire C et E n°1-2, Probatoire D et TI n°1-2. Chimie : BAC C, D et E n°1-2, Probatoire C, D et E n°1-2.
Identifiants `bp-cm-physique-...-mini-N` / `bp-cm-chimie-...-mini-N` (dossier `generateur/` : `spec_phys_bac.py`, `spec_phys_prob.py`, `spec_chimie.py`).
Relues par 3 relecteurs independants (aveugle puis comparaison), aucun constat bloquant ; corrections appliquees. Retrait notable : l'exercice d'induction de
Physique Probatoire D et TI n°2 (hors programme de Premiere d'apres la fixture) remplace par un exercice sur l'oeil myope.

## Ajout du 2026-11-04 : 3 minis de Physique-Chimie-Technologie BEPC

`bp-cm-pct-bepc-mini-1` a `-3` (plan incline et fer a repasser ; combustion du carbone et solution de soude ; engrenage et poussee d'Archimede). Generateur : `generateur/spec_pct.py`.
Relues par un relecteur independant (aveugle puis comparaison), aucune erreur numerique ; corrections appliquees. Point a confirmer avec le programme : la dilution en 3e.

## Ajout du 2026-11-04 (2) : 3 minis d'Informatique BEPC

`bp-cm-informatique-bepc-mini-1` a `-3` (numeration et boucle for PHP ; unites, debit et tableur ; code ASCII et boucle while PHP). Generateur : `generateur/spec_info.py`.
Relues par un relecteur independant ; corrections appliquees (1 Ko = 1 024 octets comme les epreuves de la plateforme, donnee 37 au lieu de 45, tableaux fournis, grilles assouplies).
Piege PDF : dans un enonce, deux `$` sur la meme ligne (variables PHP en code en ligne) sont pris pour une formule par le moteur de PDF ; une seule variable `$` par ligne, hors blocs de code.

## Ajout du 2026-11-05 : 3 minis de SVT BEPC

`bp-cm-svt-bepc-mini-1` a `-3` (caryotype de Klinefelter et paludisme ; VIH et lymphocytes T4, roches sedimentaires d'une carriere ; tests allergiques et hypertension). Generateur : `generateur/spec_svt.py`.
Chaque exercice s'appuie sur un tableau chiffre. Relues par un relecteur independant (exactitude medicale verifiee), corrections appliquees. Pas d'avis d'enseignant humain.

## Ajout du 2026-11-05 (2) : 8 minis d'Informatique pour les series A, C, D et E

Probatoire A n°1-2, BAC A n°1-2, Probatoire C/D/E n°1-2, BAC C/D/E n°1-2 (`bp-cm-informatique-<cursus>-mini-N`). Generateurs : `generateur/spec_info_a.py` et `spec_info_cde.py`.
Valeurs verifiees par execution (Python, SQLite en memoire, Node, module ipaddress) ; relues par 2 relecteurs independants, corrections appliquees.
Pieges du moteur de PDF : pas de guillemets droits dans un bloc de code d'enonce (ils sont mis en italique), pas de `%d` entre `$` (commentaire LaTeX), une seule variable PHP `$x` par ligne.
