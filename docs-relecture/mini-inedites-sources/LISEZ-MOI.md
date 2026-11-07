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

## Ajout du 2026-11-05 (3) : 6 minis BAC TI (programmation, systemes d'information, reseaux)

`bp-cm-programmation-bac-ti-mini-1/2`, `bp-cm-si-bac-ti-mini-1/2`, `bp-cm-reseaux-bac-ti-mini-1/2` (+ les `ep-...-2026-s1`). Generateurs : `generateur/spec_ti_prog.py`, `spec_ti_si.py`, `spec_ti_res.py`.
Valeurs verifiees par execution : C compile (gcc, conteneur alpine), JavaScript (Node), PHP 8.1 (Laragon), SQL (sqlite3), adresses (ipaddress), Cesar (script). UML decrit sous forme de tableaux (pas de SVG).
Relues par 3 relecteurs independants (un par matiere), 0 bloquant ; corrections appliquees (identifiants UML, grilles trop etroites, nom permuter, acteur Banque, mesures de securite).

## Ajout du 2026-11-06 : 5 minis de SVT pour le Probatoire (C et TI n°1-2, D n°1-3)

`bp-cm-svt-probatoire-c-ti-mini-1/2` et `bp-cm-svt-probatoire-d-mini-1/2/3` (+ les `ep-...-2026-s1`). Generateur : `generateur/spec_svt_prob.py`.
Chaque exercice s'appuie sur un support chiffre ou decrit ; valeurs recalculees par script (vitesses sismiques, expansion, rendements, depenses, ADN, Meselson-Stahl, pourcentages). Relues par 2 relecteurs independants (0 bloquant), corrections appliquees (erreur « quarantaine de grammes » = 25 g, generation 2 non exploitee pour la reaction semi-conservative, principes de recoupement et d'horizontalite, grilles).

## Ajout du 2026-11-07 : 5 minis de SVT pour le BAC (D n°1-3, C et TI n°1-2)

`bp-cm-svt-bac-d-mini-1/2/3` et `bp-cm-svt-bac-c-ti-mini-1/2` (+ les `ep-...-2026-s1`). Generateur : `generateur/spec_svt_bac.py`.
Supports chiffres recalcules par script (probabilites en fractions, glycemie, conduction nerveuse, rapports hormonaux, selection de moustiques resistants, F2 et test-cross, recombinaison et centimorgans, ADN en mitose et meiose, rheobase et chronaxie). Relues par 2 relecteurs independants (0 bloquant), corrections appliquees (disposition des alleles des genes lies justifiee par les resultats, effectifs de F2 differents de ceux de Mendel, « tension » et non « intensite » en volts, notation des genotypes de deux genes independants, rôle de la progesterone).

## Ajout du 2026-11-07 (2) : 4 minis d'Anglais pour le BEPC (n°1 a 4)

`bp-cm-anglais-bepc-mini-1/2/3/4` (+ les `ep-...-2026-s1`). Generateur : `generateur/spec_anglais.py`.
Enonces en anglais, explications du corrige en francais. Exercice 1 = grammaire et vocabulaire (formes verbales, question tags, formation de mots, voix passive, relatifs, collocations, conditionnels, discours indirect, contraires, comparatifs, too/enough, prepositions) ; exercice 2 = lecture (textes de 94 et 106 mots) ou ecriture guidee (lettre amicale, recit court de 50 a 70 mots avec modele de reponse).
Pas de verification par execution possible : nombre de mots des textes et des modeles controle par script, relecture par 2 enseignants d'anglais independants (0 bloquant). Corrections appliquees : items a plusieurs reponses correctes (possible, cooked, catch a taxi, less difficult, sad/rude), coherence present/passe du texte, « spread » et non « cause » pour le paludisme, preuves notees a part, tolerances de grille.

## Ajout du 2026-11-07 (3) : 8 minis TI pour les trous de couverture (audit du meme jour)

Probatoire TI : programmation n°1-2, systemes d'information n°1-2, chimie n°1-2 ; BAC TI : chimie n°1-2 (`bp-cm-<programmation|si|chimie>-<probatoire-ti|bac-ti>-mini-N`). Generateur : `generateur/spec_ti_gaps.py`.
Les cases « informatique » du Probatoire TI et du BAC TI de l'audit etaient des annales mal etiquetees (Programmation BAC TI 2018/2019, Systemes d'Information Probatoire TI 2023 Blanc), pas de vrais trous.
Verifications : chimie, chemin critique, SQL par script ; C simule en Python (pas de compilateur, reseau Docker indisponible) ; JavaScript execute avec Node ; CSS raisonne (specificite). Relues par 3 relecteurs independants (0 bloquant). Piege PDF : un printf avec guillemets droits dans un code d'enonce recoit des asterisques (retire des enonces, on demande les valeurs finales des variables).

## Ajout du 2026-11-07 (4) : 8 minis d'Anglais pour le Probatoire et le BAC

`bp-cm-anglais-<probatoire-a|probatoire-c-d-e-ti|bac-a|bac-c-d-e-ti>-mini-1/2` (+ les `ep-...-2026-s1`). Generateur : `generateur/spec_anglais2.py`.
n°1 = grammaire et vocabulaire + lecture (textes de 151 a 183 mots) ; n°2 = grammaire et vocabulaire + redaction guidee (titre et introduction, puis 50 a 100 mots) avec modele de reponse dont la longueur est controlee par script. Enonces en anglais, explications du corrige en francais.
Relues par 2 enseignants d'anglais independants (0 bloquant). Corrections : alternatives correctes non prevues (do you look, set up an experiment, has worked, unwillingness, could/might), libelles de bareme des redactions dont la somme n'etait pas claire, item de lecture a deux lectures raisonnables.
