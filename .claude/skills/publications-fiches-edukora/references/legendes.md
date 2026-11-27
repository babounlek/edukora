# Écrire les légendes

Le brouillon `legendes.md` contient tout ce qui doit être exact (en-tête, années, liens, hashtags, invitations). Tu
écris les passages `⟦…⟧`, rien d'autre. Si une ligne calculée te semble fausse, la cause est dans `semaine.json` ou
sur le site : corrige là, supprime `legendes.md` et relance plutôt que de retoucher la ligne.

## Pour qui on écrit

Des élèves de 3e (BEPC) ou de 1re (Probatoire) au Cameroun, qui lisent sur un téléphone, souvent en fin de journée,
parfois avec peu de données. Les parents lisent aussi. On tutoie l'élève.

## Le ton

- Phrases courtes, mots simples. Une idée par phrase.
- L'accroche pose **la difficulté réelle** de la notion, sous forme de question à l'élève : ce qu'on confond, ce
  qu'on oublie, le choix à faire. Pas une généralité (« Thalès est important »), pas de promesse (« réussis à coup
  sûr »).
- Puis ce que l'élève trouvera en touchant l'image, et ce qu'on attend de lui en commentaire. Finir par « correction ce
  soir » (format methode) ou « La fiche arrive ce soir » (format definition, déjà écrit).
- Pas d'émoji en dehors du 📘 de l'en-tête. Pas de points d'exclamation en série. Pas de total de fiches.
- Le statut WhatsApp tient sur une ligne : la question de l'exercice, dite simplement.
- Le soir : la réponse de la fiche, puis **le pourquoi** en une phrase (la règle qui la donne, l'erreur à éviter).
  Reprends la réponse rappelée dans le passage `⟦…⟧` ; ne refais pas le calcul de tête et n'arrondis pas autrement.
- Le hashtag du jour nomme la notion ou son domaine : `#Pythagore`, `#Trigonométrie`, `#Géométrie`, `#Solutions`,
  `#Algorithmique`. Un seul, sans espace (`#ÉducationCivique` est accepté).
- **Formules en texte simple** : Facebook, Instagram et WhatsApp n'affichent pas le LaTeX. Écris `11/(2(2x − 3))`,
  `MA² + MB²`, `f′(x)`, `≈ 51,67`, `+∞`, `[0 ; 4[`, comme le rappel de réponse du brouillon. Le signe moins « − » se
  lit mieux que le trait d'union.
- Les fiches d'éducation civique du lycée n'ont pas été extraites de questions « Définis… » : n'écris pas « comme à
  l'examen » ni « l'examen te demandera de la définir ».
- Une fête datée peut ouvrir une accroche (« Ce 11 février, Fête de la Jeunesse… ») ; écris dans le LISEZMOI de la
  semaine qu'elle est à retirer si la date bouge.

## Exemples (semaines déjà relues par l'utilisateur)

Maths BEPC, jour 1 :

> Pythagore : tu connais la formule. Sais-tu quand additionner et quand soustraire ?
> La méthode en 4 étapes, un exemple et le piège à éviter. Touche l'image pour voir la méthode, puis réponds à la dernière image en commentaire. Correction ce soir.

Statut : « À toi : calcule AC. Réponds à ce statut, correction ce soir. »

Le soir : « La réponse : AC = 10 cm. Ton angle droit est en B : l'hypoténuse est donc [AC], on additionne les carrés. »

Maths BEPC, jour 2 :

> Cosinus, sinus ou tangente ? Le choix dépend des deux côtés que tu connais.
> Regarde la méthode, puis trouve l'angle de la dernière image. Écris ta réponse en commentaire, correction ce soir.

Le soir : « On connaît le côté opposé et le côté adjacent à l'angle C : c'est la tangente. L'angle mesure environ 18°. »

Maths BEPC, jour 4 :

> Pyramide ou cône : une seule formule, et une division à ne pas oublier.
> Calcule le volume de la dernière image et écris-le en commentaire, avec son unité.

Maths Probatoire D, jour 3 :

> MA² + MB² = k : tu trouves un cercle. Mais son rayon, c'est le nombre que tu obtiens ou sa racine carrée ?

Le soir : « 2MO² + 50 = 100, donc MO = 5 : cercle de centre O, de rayon 5. Le calcul donne MO² = 25 : le rayon est sa
racine carrée, 5, pas 25. »

Éducation civique BEPC (format definition), la question qui oriente :

> Que font les candidats pendant cette période, et dans quel but ? Dis-le avec tes mots.
> Un sentiment, mais aussi des comportements : lesquels ?
> Tu en as sûrement entendu parler. Sauras-tu la définir comme à l'examen ?

La question oriente sans donner la définition : elle ne contient aucun mot clé de la réponse.

## Semaines GCE (en anglais)

Même ton, en anglais simple : des élèves de Form 5 au Cameroun anglophone, « you ». Les nombres gardent le point
décimal des fiches (0.4 kg), les unités s'écrivent comme au GCE (J kg⁻¹ K⁻¹). Exemple (Physics O Level, jour 3) :

> A hot metal is dropped into cold water. Which temperature change goes with the metal, and which goes with the water?

Le soir : « The answer: heat gained by the water = 0.2 × 4200 × (30 − 20) = 8400 J. […] The heat lost by the metal is the
heat gained by the water, and each body has its own temperature change: 70 K for the metal, 10 K for the water. »

## TikTok

`legendes-tiktok.md` reprend l'accroche et les hashtags du matin, et ajoute `#ApprendreSurTikTok`. Relis-le : sur
TikTok, une accroche plus courte marche mieux. Si celle du matin dépasse deux lignes sur un téléphone, raccourcis-la
dans `legendes-tiktok.md` seulement. Pas de lien cliquable : « edukora.africa » en clair, déjà écrit.

## Avant de rendre

- Plus aucun `⟦` dans le fichier (`construire.mjs … --verifier` le contrôle).
- Chaque réponse du soir correspond à celle de la fiche.
- Aucune légende n'annonce un nombre de fiches, une note garantie ou un « nouveau » qui ne l'est pas.
- Pour une notion sensible (élections, religion, politique), une ligne dans le LISEZMOI de la semaine : surveiller les
  commentaires et écarter ceux qui tournent au débat partisan.
