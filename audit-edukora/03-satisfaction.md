# 03 - Satisfaction (PARTIEL : Phase 1)
**Avertissement** : simulation, pas un test utilisateur. Une seule passe par persona, en mode visiteur, par un auditeur qui avait lu la liste des routes en Phase 0 (ignorance de l'élève non garantie ; pas de sous-agent, par choix de budget). Confiance globale : **faible à moyenne**. Les scores servent à repérer des creux, pas à mesurer des élèves réels. Tunnel connecté/paiement non exécuté.

## Persona 1 : Parent (peu à l'aise avec le numérique), mobile 375 px, visiteur
Mission : "je découvre, je comprends ce que mon enfant obtient, je regarde le prix et je décide si je paie" (≈ 10 min).
Courbe d'humeur (-2 à +2) :
1. Accueil /cm : message clair mais écrit pour l'élève, 0 ("c'est pour mon fils, pas pour moi")
2. Lien Voir les prix -> /tarifs : prix en gras, "2 000 FCFA par mois", pastilles Mobile Money / sans prélèvement : +1
3. Choix BEPC -> total 6 000 FCFA, date de fin d'accès, barre d'achat fixe : +2 (pic)
4. Continuer -> /connexion : e-mail demandé, ni récap du choix ni numéro de paiement : -1 (creux)
5. À propos : bloc "Parent", éditeur identifié : +1
Fin : s'arrête avant de se connecter (je ne donne pas mon e-mail avant de voir où et comment payer) : -1 (la fin pèse double).
- Q1 satisfaction : 3/5 (pic "total + date + barre fixe" ; creux = connexion avant de voir le numéro de paiement)
- Q2 effort : 2/5 (facile jusqu'à la connexion)
- Q3 "j'ai compris ce que mon enfant obtient ?" : 4/5 (liste "Tout ce dont tu as besoin", tableau vs fascicule)
- Q4 revenir : peut-être, "si mon enfant me montre l'écran du résultat de quiz" ; tombe à non sans moyen de payer sans e-mail
- Q5 recommander à une autre famille : 5/10
- Q6 payer : peut-être ; manque : voir le numéro Mobile Money et le délai d'activation avant de donner mon e-mail ; rassurance humaine (WhatsApp présent mais en bas)
- Q7 verbatim : "Les prix sont clairs, mais je dois d'abord donner mon e-mail avant de savoir où envoyer l'argent."
Plafonds respectés : oui (un Majeur hypothétique sur le chemin => Q1 ≤ 4).
Scores demandés (0-10) : envie de revenir 6, de recommander 5, de payer 5.

## Persona 2 : Élève BEPC (~15 ans), Android d'entrée de gamme, mobile 375 px, visiteur
Mission : "je cherche de quoi réviser les maths, je teste, je décide si je reviens" (≈ 12 min).
Courbe d'humeur :
1. Accueil : promesse claire, "Quiz gratuit, sans compte" : +1
2. Lire un corrigé gratuit -> liste de 126 épreuves gratuites : +1
3. Maths BEPC 2026 (sujet + corrigé libres) : +2 (pic : un vrai corrigé complet, sans compte)
4. Maths BEPC 2025 : corrigé payant, lien direct /lire -> /connexion sans explication : -1 (creux)
5. Quiz essai Identité remarquable : retour immédiat "Bravo !", explication dépliable : +2
6. Résultat 2/5 : "+20 points ... non gardés", appels "Voir les abonnements" / "Créer mon compte" : 0
7. Recherche "équation du second degré" : réponse en bref et compteurs : +1
Fin : positive, avec un petit regret (compte requis pour garder les points) : +1.
- Q1 satisfaction : 4/5 (pic cité : corrigé gratuit complet + quiz sans compte)
- Q2 effort : 2/5
- Q3 plus prêt pour l'examen ? : 3/5 (un seul thème essayé)
- Q4 revenir : cette semaine, "pour d'autres matières gratuites"
- Q5 recommander à un camarade par WhatsApp : 7/10 ("Montrer à mes parents" et "Partager ce quiz" aident)
- Q6 payer : peut-être, mais la décision est celle de mes parents ; manque : preuve que la séance du jour vaut les 2 000 FCFA (non testable sans compte)
- Q7 verbatim : "Tu as des corrigés gratuits et un petit quiz qui t'explique, c'est bien pour réviser les maths."
Plafonds respectés : oui. Scores : revenir 7, recommander 7, payer 5.

## Agrégé provisoire (2 personas sur 4)
Revenir 6,5 / Recommander 6 / Payer 5. Confiance : faible (simulation, visiteur seul, 1 passe, pas de réseau bridé). Élèves Probatoire et GCE (Phase 2) à venir.

---
# Phase 2 (ajout)
Même avertissement : simulation, visiteur seul, 1 passe, ignorance non garantie, pas de réseau bridé.

## Persona 3 : Élève Probatoire C (~17 ans, smartphone, data limitée), mobile 375 px, visiteur
Mission : "je prépare le Probatoire C, je repère ce qui tombe en physique et je vois si je peux m'entraîner gratuitement" (≈ 12 min).
Courbe d'humeur :
1. Accueil : je choisis Probatoire C, l'accueil répond "Tu prépares : Probatoire C" et adapte l'exemple : +1
2. Thèmes qui tombent : "Tableau de variation 93 %, 27 sessions sur 29" : +2 (pic)
3. Physique : "Vergence 72 %", puis 21 exercices (un gratuit, des aperçus) : +1
4. Bouton Quiz du thème : page /quiz générique, pas de quiz de physique : -1 (creux)
5. Cours "La vergence d'une lentille mince" : onglets, lecture claire, "Lire sans réseau" : +2
Fin : +1 (je repars avec un thème et un cours, mais sans quiz de physique).
- Q1 : 4/5 (pic cité : classement avec pourcentages et cours en onglets ; plafond respecté : aucun S1/S2 sur le chemin)
- Q2 : 2/5
- Q3 : 4/5 (je sais quoi réviser en premier)
- Q4 : cette semaine, pour le cours et les thèmes ; condition : un quiz de physique
- Q5 : 7/10
- Q6 : peut-être ; manque : voir un exemple de séance avant de demander 2 000 FCFA à mon père ; mes parents paient, pas moi
- Q7 : "Il te dit les thèmes qui tombent le plus au Probatoire C et te donne le cours, c'est utile."
Scores : revenir 7, recommander 7, payer 5.

## Persona 4 : Élève GCE O Level (anglophone), interface anglaise, mobile 375 px, visiteur
Mission : "I look for a free past paper and a quick quiz in English, and I check how much it costs" (≈ 12 min).
Courbe d'humeur :
1. /en : tout en anglais, "Choose your exam : GCE O Level / GCE A Level" : +1
2. Mathematics GCE O Level 2019 Paper 2 : "Free-access solution", code 0570, sections A et B : +2 (pic)
3. Pricing : 2 000 FCFA a month, mais GCE O Level est en bas d'une liste de cursus francophones : -1
4. Login : bouton "Continuer avec Google" en français : -1 (creux léger)
5. Quiz GCE Mathematics Statistics : question à réponse ouverte, "scrap paper" : +1
Fin : +1 (404 en anglais propre).
- Q1 : 4/5 (pic cité : épreuve GCE 2019 libre avec corrigé)
- Q2 : 2/5
- Q3 : 3/5 (séance du jour non vue, seulement les contenus)
- Q4 : cette semaine ; condition : des papers plus récents
- Q5 : 6/10
- Q6 : peut-être ; manque : confirmation que mes options O Level sont dans l'abonnement ; Mobile Money OK
- Q7 : "Free GCE papers with solutions and a quiz, all in English."
Scores : revenir 7, recommander 6, payer 5.

## Agrégé provisoire (4 personas)
| Persona | Revenir | Recommander | Payer | Q1 | Confiance |
|---|---|---|---|---|---|
| Parent | 6 | 5 | 5 | 3 | faible |
| Élève BEPC | 7 | 7 | 5 | 4 | faible |
| Élève Probatoire C | 7 | 7 | 5 | 4 | faible |
| Élève GCE O Level | 7 | 6 | 5 | 4 | faible |
| **Global (moyenne)** | **6,75** | **6,25** | **5,0** | **3,75** | **faible** |
Lecture : l'intention de payer plafonne à 5/10 pour tous, pour la même raison : aucun persona n'a vécu la séance du jour ni le paiement (choix visiteur seul), donc la valeur de l'abonnement reste une promesse. Indices relatifs, pas la satisfaction d'élèves réels.

---
# Synthèse finale de la satisfaction (Phase 4)
Les scores de la Phase 2 sont confirmés : revenir 6,75/10, recommander 6,25/10, payer 5,0/10 (moyenne de 4 personas jouées en visiteur seul). Plafonds du skill respectés : aucune note ne dépasse ce que permettent les frictions rencontrées.
Courbes d'humeur : pics = corrigé gratuit complet (BEPC +2), classement des thèmes avec pourcentages (Probatoire +2), total et date de fin d'accès sur /tarifs (Parent +2), épreuve GCE libre (+2) ; creux = connexion exigée avant de voir où payer (Parent -1), quiz du thème sans Physique (Probatoire -1), bouton Google en français et GCE en bas de liste (GCE -1).
Lecture : satisfaction correcte (Q1 = 4 sauf Parent 3), intention de payer plafonnée à 5 partout. C'est un problème de **valeur démontrée** (la séance du jour, non visible sans compte), non d'ergonomie. À confirmer par de vrais utilisateurs.
Confiance : **faible à moyenne** par persona (une seule passe, visiteur seul, mobile non bridé, testeur ayant lu la liste des routes en Phase 0). Une simulation n'est pas un test utilisateur ; "je reviens cette semaine" est une intention déclarée, pas un comportement observé.
