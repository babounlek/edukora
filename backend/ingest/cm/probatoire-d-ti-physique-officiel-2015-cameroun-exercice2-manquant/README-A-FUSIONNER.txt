DOSSIER COMPLEMENTAIRE - ACTION HUMAINE REQUISE
================================================

Ce dossier contient l'EXERCICE 2 (Énergie électrique, 7 points) de l'épreuve
"Probatoire D, TI - Physique - 2015 - Cameroun (officiel)".

Il a été produit le 2026-09-26 car cet exercice est ABSENT du dossier déjà en
ligne pour cette même épreuve :

    json/cm/probatoire-d-ti-physique-officiel-2015-cameroun/

Ce dossier existant ne contient que exercice_1.json (Exercice I - Lentilles
minces et instruments d'optique) et exercice_3.json (Exercice III - Énergie
mécanique, sous le nom "exercice_3"). Son fichier exercice_1.json porte, dans
son champ "incertitudes", la mention que l'Exercice II aurait été absent du
document source ("lacune réelle du document source, exercice non imprimé").

CETTE MENTION EST INEXACTE. La lecture visuelle intégrale du PDF source
(/home/claude/batch20/pdf/probatoire-d-ti-physique-2015-officiel-cameroun.pdf,
2 pages) confirme que l'EXERCICE II : ÉNERGIE ÉLECTRIQUE (7 points) est bien
imprimé en totalité en page 1, entre l'Exercice I et l'Exercice III :
  1. Production du courant alternatif (4 points) : alternateur (parties et
     rôles), loi de Lenz, calcul de la f.é.m. induite maximale à partir du
     flux φ(t) = 4 sin(31,4 t).
  2. Énergie électrique dans une portion de circuit (3 points) : générateur
     (E=19V, r=1,5Ω) + moteur (E'=12V, r'=2Ω) + résistor (R=10,5Ω) en série -
     intensité, rendement du générateur, diagramme des échanges d'énergie du
     moteur.

Il s'agit très probablement d'une erreur d'extraction du traitement précédent
(l'en-tête "Exercice II" a peut-être été repéré en fin de page 1 sans que le
texte qui suit immédiatement, sur la même page, n'ait été lu).

CONTENU DE CE DOSSIER (6 fichiers, prêts à l'ingestion) :
- probatoire-d-ti-physique-officiel-2015-cameroun_exercice_2.json (6 questions)
- probatoire-d-ti-physique-officiel-2015-cameroun_exercice_2_fig_1.png
  (diagramme des échanges d'énergie du moteur, figure produite pour le corrigé)
- 4 fichiers cours_*.json (un par rappel de méthode de l'exercice 2, tous
  complets en 7 sections)

VALIDATION :
- valider_schema.py : "Corpus conforme." (6 questions contrôlées, 0 défaut)
- verifier_lot.py : "LOT À CORRIGER" à cause du seul point suivant, un FAUX
  POSITIF déjà documenté à plusieurs reprises dans dernier_passage.txt pour
  cette même combinaison série/matière (voir entrées probatoire-d-ti-physique-
  2008/2010/2011-officiel-cameroun) : l'heuristique du script
  "re.search(r'\bTI\b', serie) et matiere hors liste informatique" déclenche
  à tort dès que serie contient "TI", alors que "D, TI" est une combinaison
  série scientifique+technique légitime au Cameroun et que la Physique y est
  bien enseignée (voir le périmètre officiel du skill correction-experte :
  "Physique (... Première D et TI ...)"). Le MÊME faux positif a été vérifié
  ce jour sur les deux fichiers DÉJÀ EN LIGNE exercice_1.json et exercice_3.json
  de cette épreuve, testés isolément avec le même script : ce n'est donc pas
  un défaut introduit par ce dossier complémentaire.

ACTION REQUISE :
1. Vérifier ce contenu (corrigé, cours, figure).
2. Copier ces 6 fichiers dans le dossier
   json/cm/probatoire-d-ti-physique-officiel-2015-cameroun/ pour compléter
   l'épreuve (aucune collision de nom de fichier avec exercice_1/exercice_3
   ni avec les cours déjà présents).
3. Corriger le champ "incertitudes" de exercice_1.json de ce même dossier
   pour retirer la mention erronée sur l'Exercice II manquant (ou l'annoter
   comme corrigée).
4. Une fois la fusion faite, le PDF source pourra être déplacé de
   non_traites/cm/ vers traites/cm/ (laissé en l'état pour l'instant : il
   reste dans non_traites/cm/, ni déplacé ni supprimé, dans l'attente de
   cette décision humaine).
