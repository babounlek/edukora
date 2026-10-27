# Tirage au hasard pour l'enseignant de maths (campagne B1)

Date : 2026-10-27. 20 questions DEJA EN LIGNE, tirees au hasard (graine fixe) parmi celles que l'enseignant n'a pas encore vues : 10 des vagues 1 et 2, 10 de la vague 3. But : savoir si le taux de rejet du premier echantillon (12 sur 48) vaut pour l'ensemble des 320 autres questions. Les textes sont ceux d'aujourd'hui, corriges.

Pour chaque question : **OK**, **a corriger** (dire quoi) ou **a retirer**.

## 1. `cqc-coordonnees-d-un-vecteur-moyenne-0` (vague 1)

**Enonce :**

Dans un repère orthonormé, on donne les points $A(-3\,;\,2)$, $B(1\,;\,-1)$ et $C(4\,;\,3)$.

On calcule les coordonnées des vecteurs $\overrightarrow{AB}$ et $\overrightarrow{BC}$, puis celles de leur somme. Quelles sont les coordonnées du vecteur $\overrightarrow{AB} + \overrightarrow{BC}$ ?

- a) $(-1\,;\,7)$
- b) $(7\,;\,-1)$
- c) $(7\,;\,1)$
- d) $(5\,;\,2)$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Les coordonnées d'un vecteur $\overrightarrow{MN}$ s'obtiennent par $\overrightarrow{MN}\,(x_N - x_M\,;\,y_N - y_M)$. Les coordonnées d'une somme de vecteurs s'obtiennent en additionnant les coordonnées. La relation de Chasles $\overrightarrow{AB} + \overrightarrow{BC} = \overrightarrow{AC}$ fournit une vérification gratuite dès que l'on a calculé trois vecteurs qui s'enchaînent.

### Corrigé

**Coordonnées des vecteurs.**

$$\overrightarrow{AB}\,(1-(-3)\,;\,-1-2) = (4\,;\,-3)$$

$$\overrightarrow{BC}\,(4-1\,;\,3-(-1)) = (3\,;\,4)$$

**Somme.**

$$\overrightarrow{AB} + \overrightarrow{BC} = (4+3\,;\,-3+4) = (7\,;\,1)$$

**Vérification par la relation de Chasles.**

$$\overrightarrow{AC}\,(4-(-3)\,;\,3-2) = (7\,;\,1)$$

On retrouve bien $\overrightarrow{AB} + \overrightarrow{BC} = \overrightarrow{AC}$.

### Pourquoi les autres réponses sont fausses
- **a)** $(-1\,;\,7)$ vient de $\overrightarrow{BA}\,(-4\,;\,3)$ pris à la place de $\overrightarrow{AB}$ : on a soustrait dans le mauvais ordre.
- **b)** $(7\,;\,-1)$ vient de $\overrightarrow{BC}\,(3\,;\,2)$ : erreur de signe, $3 - (-1) = 4$ et non $2$.
- **d)** $(5\,;\,2)$ vient de l'addition des coordonnées des points $B$ et $C$ au lieu de celles des vecteurs.

</details>

Avis : 

---

## 2. `cqc-fonction-affine-moyenne-3` (vague 2)

**Enonce :**

La fonction $f$ est définie par $f(x) = 250x + 4\,000$. Pour quelle valeur de $x$ a-t-on $f(x) = 9\,000$ ?

- a) $x = 20$
- b) $x = 52$
- c) $x = 36$
- d) $x = 0{,}05$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Pour trouver l'antécédent d'un nombre par une fonction affine, on remplace $f(x)$ par la valeur donnée, ce qui transforme le problème en une équation du premier degré que l'on résout en isolant $x$.

### Corrigé

*Mise en équation.*

$$250x + 4\,000 = 9\,000$$

*Isolement du terme en $x$.*

$$250x = 9\,000 - 4\,000$$

$$250x = 5\,000$$

*Division par $250$.*

$$x = \frac{5\,000}{250} = 20$$

$$x = 20$$

*Contrôle.* $f(20) = 250 \times 20 + 4\,000 = 5\,000 + 4\,000 = 9\,000$ ✔

### Pourquoi les autres réponses sont fausses

- **b)** $x = 52$ : en passant $4\,000$ de l'autre côté, on l'a ajouté au lieu de le soustraire ($13\,000 \div 250$).
- **c)** $x = 36$ : on a divisé $9\,000$ par $250$ en oubliant le terme constant $4\,000$.
- **d)** $x = 0{,}05$ : la division est faite à l'envers, $250 \div 5\,000$ au lieu de $5\,000 \div 250$.

</details>

Avis : 

---

## 3. `cqc-droite-moyenne-2` (vague 2)

**Enonce :**

Dans un repère, on donne les points $P(-3\,;\,4)$ et $Q(1\,;\,-2)$. Quelle est une équation de la droite $(PQ)$ ?

- a) $2x + 3y - 6 = 0$
- b) $3x + 2y + 1 = 0$
- c) $3x + 2y - 17 = 0$
- d) $3x - 2y + 17 = 0$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Pour déterminer une équation d'une droite $(PQ)$ à partir de deux points, on calcule d'abord les coordonnées du vecteur directeur $\vec{PQ}(x_Q-x_P\,;\,y_Q-y_P)$, puis on applique la condition de colinéarité $b(x-x_P) - a(y-y_P) = 0$ avec $\vec{PQ}(a\,;\,b)$.

### Corrigé

*Vecteur directeur.*

$$\vec{PQ}\,(x_Q-x_P\,;\,y_Q-y_P) = \vec{PQ}\,\big(1-(-3)\,;\,-2-4\big) = \vec{PQ}\,(4\,;\,-6)$$

On peut simplifier ce vecteur directeur en $(2\,;\,-3)$ (en divisant chaque coordonnée par $2$).

*Équation de la droite.* Avec $P(-3\,;\,4)$ et $(a\,;\,b)=(2\,;\,-3)$ :

$$-3\big(x-(-3)\big) - 2(y-4) = 0$$

$$-3x - 9 - 2y + 8 = 0$$

$$-3x - 2y - 1 = 0 \quad \text{soit} \quad 3x + 2y + 1 = 0$$

*Vérification.* Pour $P(-3\,;\,4)$ : $3\times(-3)+2\times4+1 = -9+8+1=0$. Pour $Q(1\,;\,-2)$ : $3\times1+2\times(-2)+1=3-4+1=0$. Les deux points vérifient bien l'équation.

La droite $(PQ)$ a donc pour équation $3x + 2y + 1 = 0$.

### Pourquoi les autres réponses sont fausses
- **a)** Formule appliquée à l'envers, $a(x-x_P) - b(y-y_P) = 0$ : on obtient $2x + 3y - 6 = 0$, qui passe par $P$ mais pas par $Q$ ($2 - 6 - 6 \neq 0$).
- **c)** Erreur de signe sur $x_P$ : on a écrit $x - 3$ au lieu de $x-(-3) = x+3$ ; ni $P$ ni $Q$ ne vérifient l'équation.
- **d)** Erreur de signe sur une coordonnée du vecteur directeur : la droite obtenue passe par $P$ mais pas par $Q$ ($3 + 4 + 17 \neq 0$).

</details>

Avis : 

---

## 4. `cqc-carre-parfait-faible-0` (vague 1)

**Enonce :**

Le nombre entier $226$ est-il un carré parfait ? Choisis la réponse correctement justifiée.

- a) Oui, car $226 = 15^2$
- b) Oui, car $\sqrt{226} = 113$
- c) Non, car $15^2 < 226 < 16^2$
- d) Non, car $14^2 < 226 < 15^2$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Pour savoir si un entier $N$ est un carré parfait, on l'encadre entre les carrés de deux entiers naturels consécutifs $n$ et $n+1$ : si $n^2 < N < (n+1)^2$ (inégalité stricte des deux côtés), alors $N$ n'est égal au carré d'aucun entier, donc $N$ n'est pas un carré parfait.

### Corrigé

On cherche deux entiers consécutifs dont les carrés encadrent $226$.

$15^2 = 225$ et $16^2 = 256$.

Or $225 < 226 < 256$ : l'inégalité est stricte des deux côtés, donc $226$ n'est égal ni à $15^2$ ni à $16^2$.

**Conclusion : $226$ n'est pas un carré parfait.**

### Pourquoi les autres réponses sont fausses

- **a)** $15^2 = 225$ et non $226$ : il ne faut pas confondre $226$ avec le carré parfait voisin $225$.
- **b)** $113$ est la moitié de $226$ : la racine carrée n'est pas la moitié du nombre ($113^2 = 12\,769$).
- **d)** L'encadrement est faux : $15^2 = 225 < 226$, donc $226$ n'est pas compris entre $14^2 = 196$ et $15^2 = 225$.

</details>

Avis : 

---

## 5. `cqc-calculatrice-moyenne-3` (vague 1)

**Enonce :**

On sait que $\sin(\widehat{HIJ}) = 0{,}65$.

À l'aide de la calculatrice, quelle est la mesure de l'angle $\widehat{HIJ}$, arrondie à l'entier le plus proche ?

- a) $40°$
- b) $41°$
- c) $49°$
- d) $33°$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

On utilise la touche $\sin^{-1}$ de la calculatrice (en mode degrés) pour retrouver la mesure de l'angle à partir de son sinus, puis on arrondit à la précision demandée.

### Corrigé

On calcule :

$$\widehat{HIJ} = \sin^{-1}(0{,}65) \approx 40{,}54°$$

Arrondi à l'entier le plus proche :

$$\widehat{HIJ} \approx 41°$$

*Contrôle.* $\sin 41° \approx 0{,}656$, valeur très proche de $0{,}65$ : l'arrondi est cohérent.

### Pourquoi les autres réponses sont fausses

- **a)** On a tronqué $40{,}54°$ au lieu de l'arrondir : la première décimale $5$ impose d'arrondir à $41°$.
- **c)** C'est $\cos^{-1}(0{,}65) \approx 49{,}46°$ : on a utilisé la touche $\cos^{-1}$ au lieu de $\sin^{-1}$.
- **d)** C'est $\tan^{-1}(0{,}65) \approx 33{,}02°$ : on a utilisé la touche $\tan^{-1}$ au lieu de $\sin^{-1}$.

</details>

Avis : 

---

## 6. `cqc-fonction-affine-elevee-5` (vague 2)

**Enonce :**

Un artisan facture ses réparations selon une fonction affine $f$ du nombre d'heures $x$ travaillées. On sait que $f(2) = 9\,000$ F et $f(5) = 18\,000$ F. Quel est le prix d'une réparation de $7$ heures ?

- a) $24\,000$ F
- b) $21\,000$ F
- c) $31\,500$ F
- d) $25\,200$ F

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Pour déterminer une fonction affine $f(x) = ax + b$ à partir de deux couples connus $(x_1\,;\,f(x_1))$ et $(x_2\,;\,f(x_2))$, on calcule d'abord le coefficient directeur $a = \dfrac{f(x_2) - f(x_1)}{x_2 - x_1}$, puis on détermine $b$ en remplaçant dans l'une des deux égalités connues.

### Corrigé

*Calcul du coefficient directeur.*

$$a = \frac{f(5) - f(2)}{5 - 2} = \frac{18\,000 - 9\,000}{3} = \frac{9\,000}{3} = 3\,000$$

*Calcul de $b$, à l'aide de $f(2) = 9\,000$.*

$$f(2) = 3\,000 \times 2 + b$$

$$9\,000 = 6\,000 + b$$

$$b = 3\,000$$

*Expression de $f$.*

$$f(x) = 3\,000x + 3\,000$$

*Vérification avec $f(5)$.* $f(5) = 3\,000 \times 5 + 3\,000 = 15\,000 + 3\,000 = 18\,000$ ✔

*Calcul de $f(7)$.*

$$f(7) = 3\,000 \times 7 + 3\,000 = 21\,000 + 3\,000 = 24\,000$$

Une réparation de $7$ heures coûte donc $24\,000$ F.

*Interprétation.* Le nombre $b = 3\,000$ F représente un forfait de déplacement ou de dossier, facturé même pour un temps de travail nul.

### Pourquoi les autres réponses sont fausses

- **b)** $21\,000$ F : c'est seulement $3\,000 \times 7$, on a oublié le terme constant $b = 3\,000$.
- **c)** $31\,500$ F : on a traité le prix comme proportionnel au temps à partir de $f(2)$ ($4\,500$ F l'heure), alors que $f$ est affine et non linéaire.
- **d)** $25\,200$ F : même erreur de proportionnalité, faite à partir de $f(5)$ ($3\,600$ F l'heure).

</details>

Avis : 

---

## 7. `cqc-classes-elevee-0` (vague 1)

**Enonce :**

Voici la répartition des notes (sur 20) obtenues par 50 élèves à un devoir de mathématiques, groupées en classes :

$[0\,;\,4[$ : 4 élèves ; $[4\,;\,8[$ : 10 élèves ; $[8\,;\,12[$ : 20 élèves ; $[12\,;\,16[$ : 12 élèves ; $[16\,;\,20[$ : 4 élèves.

Quelle est la moyenne de cette série, calculée en utilisant le centre de chaque classe ?

- a) $8{,}16$
- b) $10$
- c) $10{,}16$
- d) $12{,}16$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Pour une série groupée en classes, on ne connaît pas chaque valeur individuelle : on remplace chaque classe par son centre (la moyenne de ses deux bornes), et on calcule la moyenne pondérée de ces centres par les effectifs : $\bar{x} = \dfrac{\sum n_i \times c_i}{N}$.

### Corrigé

*Centres des classes.*
$$c_1 = \frac{0+4}{2} = 2 \qquad c_2 = \frac{4+8}{2} = 6 \qquad c_3 = \frac{8+12}{2} = 10 \qquad c_4 = \frac{12+16}{2} = 14 \qquad c_5 = \frac{16+20}{2} = 18$$

*Somme des produits effectif $\times$ centre.*
$$4 \times 2 = 8 \qquad 10 \times 6 = 60 \qquad 20 \times 10 = 200 \qquad 12 \times 14 = 168 \qquad 4 \times 18 = 72$$
$$8 + 60 + 200 + 168 + 72 = 508$$

*Effectif total.*
$$N = 4 + 10 + 20 + 12 + 4 = 50$$

*Moyenne.*
$$\bar{x} = \frac{508}{50} = 10{,}16$$

La moyenne de la série est **$10{,}16$ sur 20**.

*Contrôle de vraisemblance.* La classe la plus chargée, $[8\,;\,12[$, a pour centre $10$ : la moyenne trouvée ($10{,}16$) est logiquement très proche de ce centre ✔

### Pourquoi les autres réponses sont fausses

- **a)** $8{,}16$ : on a utilisé la borne inférieure de chaque classe au lieu de son centre.
- **b)** $10$ : c'est la moyenne des cinq centres sans tenir compte des effectifs (moyenne non pondérée).
- **d)** $12{,}16$ : on a utilisé la borne supérieure de chaque classe au lieu de son centre.

</details>

Avis : 

---

## 8. `cqc-diagonales-moyenne-2` (vague 2)

**Enonce :**

Un architecte trace un quadrilatère $PQRS$. Il vérifie que les diagonales $[PR]$ et $[QS]$ se coupent en leur milieu commun. Il mesure ensuite $PR = 10$ m et $QS = 7$ m, et constate que ces deux diagonales ne sont pas perpendiculaires.

Quelle est la nature la plus précise du quadrilatère $PQRS$ ?

- a) Un rectangle qui n'est pas un losange
- b) Un parallélogramme qui n'est ni un rectangle ni un losange
- c) Un losange qui n'est pas un rectangle
- d) Un quadrilatère qui n'est pas un parallélogramme

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Des diagonales qui se coupent en leur milieu suffisent à garantir un parallélogramme. Pour un rectangle, il faut en plus que les diagonales aient la même longueur ; pour un losange, il faut qu'elles soient perpendiculaires. Sans l'une de ces deux conditions supplémentaires, le parallélogramme reste « quelconque ».

### Corrigé

*Parallélogramme.* Les diagonales $[PR]$ et $[QS]$ se coupent en leur milieu : $PQRS$ est un **parallélogramme**.

*Rectangle ?* $PR = 10$ m et $QS = 7$ m : les diagonales n'ont pas la même longueur, donc $PQRS$ **n'est pas un rectangle**.

*Losange ?* Les diagonales ne sont pas perpendiculaires, donc $PQRS$ **n'est pas non plus un losange**.

$PQRS$ est un parallélogramme qui n'est ni un rectangle ni un losange.

### Pourquoi les autres réponses sont fausses

- **a)** Un rectangle exigerait des diagonales de même longueur, or $10 \neq 7$.
- **c)** Un losange exigerait des diagonales perpendiculaires, ce qui n'est pas le cas.
- **d)** Des diagonales qui se coupent en leur milieu suffisent à faire un parallélogramme : la figure n'est pas quelconque.

</details>

Avis : 

---

## 9. `cqc-difference-de-deux-carres-moyenne-2` (vague 2)

**Enonce :**

On considère l'expression $K(x) = 49 - (3x-1)^{2}$. Quelles sont les solutions de l'équation $K(x) = 0$ ?

- a) $x = 2$ ou $x = -2$
- b) $x = -\dfrac{8}{3}$ ou $x = 2$
- c) $x = \dfrac{8}{3}$ ou $x = -2$
- d) $x = \dfrac{8}{3}$ seulement

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Une expression de la forme $a^{2} - b^{2}$ se factorise avec l'identité remarquable $a^{2} - b^{2} = (a-b)(a+b)$. Une fois l'expression factorisée en produit de facteurs, l'équation $\text{produit} = 0$ se résout en annulant chaque facteur séparément.

### Corrigé

*Factorisation.* $49 = 7^{2}$, donc

$$K(x) = 7^{2} - (3x-1)^{2} = \big[7-(3x-1)\big]\big[7+(3x-1)\big]$$

*Réduction de chaque crochet.*

$$7-(3x-1) = 7-3x+1 = 8-3x$$

$$7+(3x-1) = 7+3x-1 = 3x+6$$

$$K(x) = (8-3x)(3x+6) = 3(8-3x)(x+2)$$

*Contrôle pour $x=0$.* Expression de départ : $49 - (-1)^{2} = 48$. Forme factorisée : $3 \times 8 \times 2 = 48$ ✔

*Résolution.* Un produit de facteurs est nul si et seulement si l'un au moins des facteurs est nul :

$$8-3x=0 \iff x = \frac{8}{3} \qquad \text{ou} \qquad x+2=0 \iff x=-2$$

L'équation $K(x)=0$ admet deux solutions : $x = \dfrac{8}{3}$ et $x = -2$.

### Piège à éviter

Le signe $-$ devant la parenthèse $(3x-1)$ change **tous** les signes à l'intérieur : $7-(3x-1)$ vaut $8-3x$, et non $7-3x-1=6-3x$.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe : $7-(3x-1)$ a été réduit en $6-3x$, ce qui donne la solution $2$ au lieu de $\dfrac{8}{3}$.
- **b)** Les signes ont été inversés en annulant chaque facteur : $8-3x=0$ donne $x=\dfrac{8}{3}$, pas $-\dfrac{8}{3}$, et $x+2=0$ donne $-2$, pas $2$.
- **d)** On a seulement résolu $3x-1 = 7$ en oubliant le cas $3x-1 = -7$, qui donne $x=-2$.

</details>

Avis : 

---

## 10. `cqc-aire-d-un-triangle-faible-0` (vague 1)

**Enonce :**

Un terrain agricole a la forme d'un triangle $ABC$. Le côté $[BC]$, pris comme base, mesure $14$ m et la hauteur issue de $A$, perpendiculaire à $(BC)$, mesure $9$ m. Quelle est l'aire de ce terrain ?

- a) $126$ m²
- b) $63$ m²
- c) $31{,}5$ m²
- d) $23$ m²

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

L'aire d'un triangle se calcule à partir d'un côté choisi comme base et de la hauteur qui lui correspond, c'est-à-dire la longueur du segment perpendiculaire reliant cette base au sommet opposé : $\mathcal A = \dfrac{\text{base} \times \text{hauteur}}{2}$.

### Corrigé

La base est $BC = 14$ m et la hauteur correspondante est $h = 9$ m.

$\mathcal A = \dfrac{BC \times h}{2} = \dfrac{14 \times 9}{2} = \dfrac{126}{2} = 63$

L'aire du terrain est donc $63$ m².

### Pourquoi les autres réponses sont fausses

- **a)** $126$ m² : on a oublié de diviser le produit base $\times$ hauteur par $2$ (c'est l'aire d'un rectangle).
- **c)** $31{,}5$ m² : on a divisé par $2$ une fois de trop.
- **d)** $23$ m² : on a additionné la base et la hauteur au lieu de les multiplier.

</details>

Avis : 

---

## 11. `cqc-reciproque-du-theoreme-de-pythagore-faible-1` (vague 3)

**Enonce :**

Un triangle $RST$ a pour côtés $RS = 9$ cm, $ST = 12$ cm et $RT = 15$ cm. Que peut-on affirmer ?

- a) Le triangle est rectangle en $R$.
- b) Le triangle n'est pas rectangle, car $9+12\neq15$.
- c) Le triangle est rectangle en $S$.
- d) Le triangle est rectangle en $T$.

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

La réciproque du théorème de Pythagore permet de démontrer qu'un triangle est rectangle à partir des longueurs de ses trois côtés : si le carré du plus grand côté est égal à la somme des carrés des deux autres, alors le triangle est rectangle, et l'angle droit se trouve au sommet opposé au plus grand côté.

### Corrigé

*Identification du plus grand côté.* Le plus grand est $[RT]$.

$$RT^{2} = 15^{2} = 225 \qquad RS^{2} + ST^{2} = 81 + 144 = 225$$

$RT^{2} = RS^{2} + ST^{2}$ : d'après la réciproque du théorème de Pythagore, le triangle $RST$ est rectangle au sommet opposé à $[RT]$, c'est-à-dire **rectangle en $S$**.

### Pourquoi les autres réponses sont fausses
- **a)** $R$ est une extrémité de l'hypoténuse $[RT]$ : l'angle droit n'y est pas.
- **b)** On a comparé les longueurs ($9+12=21\neq15$) au lieu de leurs carrés.
- **d)** $T$ est l'autre extrémité de $[RT]$ : même confusion de sommet.

</details>

Avis : 

---

## 12. `cqc-systeme-d-equations-moyenne-0` (vague 3)

**Enonce :**

La somme de l'âge d'un père et de l'âge de son fils est 44 ans. Dans 4 ans, l'âge du père sera le triple de l'âge de son fils à cette date. Quels sont l'âge actuel du père et l'âge actuel du fils ?

- a) Le père a 32 ans et le fils 12 ans
- b) Le père a 36 ans et le fils 8 ans
- c) Le père a 35 ans et le fils 9 ans
- d) Le père a 33 ans et le fils 11 ans

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Pour résoudre un problème d'âges, on choisit une lettre pour chaque âge inconnu, on traduit chaque phrase de l'énoncé par une équation, puis on résout le système obtenu par substitution ou combinaison. On vérifie enfin que les valeurs trouvées ont un sens dans le contexte (âges positifs et cohérents).

### Corrigé

Soit $x$ l'âge actuel du père et $y$ l'âge actuel du fils.

- « La somme de leurs âges est 44 ans » se traduit par : $x + y = 44$.
- « Dans 4 ans, l'âge du père sera le triple de l'âge du fils » se traduit par : $x + 4 = 3(y + 4)$, c'est-à-dire $x = 3y + 8$.

On substitue $x = 3y + 8$ dans la première équation :
$(3y + 8) + y = 44$
$4y = 36$
$y = 9$

On en déduit $x = 3\times9 + 8 = 35$.

Vérification :
- $x + y = 35 + 9 = 44$ ✓
- Dans 4 ans, le père aura $35 + 4 = 39$ ans et le fils $9 + 4 = 13$ ans, et $39 = 3\times13$ ✓

Le père a actuellement 35 ans et le fils 9 ans.

### Pourquoi les autres réponses sont fausses
- **a)** 32 ans et 12 ans : on a écrit $x + 4 = 3y$, en oubliant d'ajouter 4 ans à l'âge du fils.
- **b)** 36 ans et 8 ans : on a écrit $x = 3(y + 4)$, en oubliant d'ajouter 4 ans à l'âge du père.
- **d)** 33 ans et 11 ans : on a mal développé $3(y + 4)$ en $3y + 4$.

</details>

Avis : 

---

## 13. `cqc-simplification-de-racines-moyenne-2` (vague 3)

**Enonce :**

On considère le nombre $E = (2 + \sqrt{7})^{2} - 3\sqrt{28}$. Quelle est son écriture sous la forme $a + b\sqrt{7}$, où $a$ et $b$ sont des entiers relatifs ?

- a) $11 - 6\sqrt{7}$
- b) $11 - 2\sqrt{7}$
- c) $11 - 4\sqrt{7}$
- d) $11 - 8\sqrt{7}$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Pour écrire un nombre sous la forme $a + b\sqrt{n}$, on développe d'abord les carrés avec les identités remarquables, on simplifie chaque radical en extrayant les carrés parfaits, puis on regroupe séparément les termes sans radical et les termes en $\sqrt{n}$.

### Corrigé

*Développement du carré.* Avec $x = 2$ et $y = \sqrt{7}$ :

$$(2 + \sqrt{7})^{2} = 2^{2} + 2 \times 2 \times \sqrt{7} + (\sqrt{7})^{2} = 4 + 4\sqrt{7} + 7 = 11 + 4\sqrt{7}$$

*Simplification de $\sqrt{28}$.* $28 = 4 \times 7$ :

$$\sqrt{28} = 2\sqrt{7} \quad \Longrightarrow \quad 3\sqrt{28} = 6\sqrt{7}$$

*Soustraction.*

$$E = 11 + 4\sqrt{7} - 6\sqrt{7} = 11 - 2\sqrt{7}$$

En identifiant avec la forme $a + b\sqrt{7}$ : $a = 11$ et $b = -2$.

*Contrôle numérique.* $\sqrt{7} \approx 2{,}646$ : $(2 + 2{,}646)^{2} - 3 \times 5{,}292 \approx 21{,}58 - 15{,}875 = 5{,}70$, et $11 - 2 \times 2{,}646 = 11 - 5{,}292 = 5{,}708$.

### Pourquoi les autres réponses sont fausses

- **a)** $11 - 6\sqrt{7}$ : on a oublié le double produit $2 \times 2 \times \sqrt{7}$ en développant $(2 + \sqrt{7})^{2}$.
- **c)** $11 - 4\sqrt{7}$ : on a écrit le double produit $2\sqrt{7}$ au lieu de $4\sqrt{7}$ (oubli du facteur $2$ de l'identité remarquable).
- **d)** $11 - 8\sqrt{7}$ : on a écrit $\sqrt{28} = 4\sqrt{7}$ en sortant $4$ sans prendre sa racine, d'où $3\sqrt{28} = 12\sqrt{7}$.

</details>

Avis : 

---

## 14. `cqc-resolution-algebrique-elevee-1` (vague 3)

**Enonce :**

Résous dans $\mathbb{R} \times \mathbb{R}$ le système suivant : $\begin{cases} 4x + y = 34 \\ 2x + 3y = 32 \end{cases}$ Quel est l'ensemble des solutions ?

- a) $S = \{(6\,;\,7)\}$
- b) $S = \{(-7\,;\,62)\}$
- c) $S = \{(7\,;\,6)\}$
- d) $S = \{(35\,;\,-106)\}$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

La méthode par substitution consiste à exprimer une inconnue en fonction de l'autre à partir de l'équation la plus simple, puis à reporter cette expression dans la seconde équation en développant soigneusement les parenthèses obtenues.

### Corrigé

Le système s'écrit :

$$\begin{cases} 4x + y = 34 \\ 2x + 3y = 32 \end{cases}$$

*Expression de $y$.* La première équation donne directement

$$y = 34 - 4x$$

*Substitution dans la seconde équation.*

$$2x + 3(34 - 4x) = 32$$

$$2x + 102 - 12x = 32$$

$$-10x + 102 = 32$$

$$-10x = 32 - 102 = -70$$

$$x = \frac{-70}{-10} = 7$$

*Retour à $y$.*

$$y = 34 - 4 \times 7 = 34 - 28 = 6$$

*Vérification.* Première équation : $4 \times 7 + 6 = 28 + 6 = 34$ ✔. Seconde équation : $2 \times 7 + 3 \times 6 = 14 + 18 = 32$ ✔

$$S = \{(7\,;\,6)\}$$

### Pourquoi les autres réponses sont fausses

- **a)** Les valeurs de $x$ et de $y$ sont inversées : le couple $(6\,;\,7)$ donne $4 \times 6 + 7 = 31 \neq 34$.
- **b)** Erreur de signe dans la division : $\frac{-70}{-10}$ vaut $7$ et non $-7$.
- **d)** Développement incomplet : $3(34 - 4x)$ a été écrit $102 - 4x$ au lieu de $102 - 12x$.

</details>

Avis : 

---

## 15. `cqc-pave-droit-faible-1` (vague 3)

**Enonce :**

Une caisse de rangement a la forme d'un cube d'arête $15\text{ cm}$.

Quel est le volume de cette caisse ?

- a) $3375\text{ cm}^3$
- b) $225\text{ cm}^3$
- c) $1350\text{ cm}^3$
- d) $45\text{ cm}^3$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Le volume d'un pavé droit se calcule par $V = L \times l \times h$. Dans le cas particulier du cube, les trois dimensions sont égales à l'arête $c$ (on a $L = l = h = c$), donc la formule devient $V = c \times c \times c = c^3$.

### Corrigé

Ici $c = 15\text{ cm}$, donc :

$V = c^3 = 15^3 = 15 \times 15 \times 15$

$15 \times 15 = 225$, puis $225 \times 15 = 3375$

$V = 3375\text{ cm}^3$

Le volume de la caisse cubique est donc $3375\text{ cm}^3$.

### Pourquoi les autres réponses sont fausses

- **b)** $225 = 15^2$ : c'est l'aire d'une face, on a oublié de multiplier par la troisième dimension.
- **c)** $1350 = 6 \times 15^2$ : c'est l'aire totale des 6 faces (en $\text{cm}^2$), pas le volume.
- **d)** $45 = 3 \times 15$ : on a confondu $c^3$ avec $3c$.

</details>

Avis : 

---

## 16. `cqc-resolution-algebrique-faible-1` (vague 3)

**Enonce :**

Quelle est la solution dans $\mathbb{R}$ de l'équation $9x + 14 = 86$ ?

- a) $x = 8$
- b) $x = \frac{100}{9}$
- c) $x = 63$
- d) $x = 648$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Une équation du premier degré de la forme $ax + b = c$ se résout en isolant l'inconnue : on retranche d'abord le terme constant aux deux membres, puis on divise par le coefficient de $x$.

### Corrigé

$$9x + 14 = 86$$

On retranche $14$ aux deux membres :

$$9x = 86 - 14$$

$$9x = 72$$

On divise les deux membres par $9$ :

$$x = \frac{72}{9} = 8$$

*Vérification.* $9 \times 8 + 14 = 72 + 14 = 86$ ✔

$$S = \{8\}$$

### Pourquoi les autres réponses sont fausses

- **b)** Le terme $14$ a été ajouté au lieu d'être retranché : $9x = 100$.
- **c)** On a retranché $9$ au lieu de diviser par $9$ : $72 - 9 = 63$.
- **d)** On a multiplié par $9$ au lieu de diviser : $72 \times 9 = 648$.

</details>

Avis : 

---

## 17. `cqc-rapport-de-reduction-faible-1` (vague 3)

**Enonce :**

Une maquette représente un immeuble à échelle réduite. Un mur de l'immeuble réel mesure $8$ m de hauteur. Sur la maquette, ce même mur mesure $20$ cm. Quel est le rapport de réduction $k$ qui permet de passer de la hauteur réelle du mur à sa hauteur sur la maquette ?

- a) $\dfrac{5}{2}$
- b) $\dfrac{1}{400}$
- c) $\dfrac{1}{40}$
- d) $40$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Le rapport de réduction $k$ qui permet de passer d'une figure à sa réduction est le quotient d'une longueur de la figure réduite par la longueur correspondante de la figure d'origine : $k = \dfrac{\text{longueur réduite}}{\text{longueur d'origine}}$. Les deux longueurs doivent être exprimées dans la même unité avant de calculer le quotient.

### Corrigé

*Conversion des unités.* La hauteur réelle est $8$ m, soit $800$ cm, pour pouvoir la comparer aux $20$ cm de la maquette.

*Calcul du rapport.*

$$k = \frac{20}{800}$$

On simplifie en divisant numérateur et dénominateur par $20$ :

$$k = \frac{20 \div 20}{800 \div 20} = \frac{1}{40}$$

$$k = \frac{1}{40}$$

La fraction $\dfrac{1}{40}$ est irréductible : $1$ et $40$ n'ont pas d'autre diviseur commun que $1$.

### Pourquoi les autres réponses sont fausses

- **a)** $\dfrac{5}{2}$ : on a calculé $\dfrac{20}{8}$ sans convertir les mètres en centimètres.
- **b)** $\dfrac{1}{400}$ : on a converti $8$ m en $8\,000$ cm au lieu de $800$ cm.
- **d)** $40$ : on a inversé le quotient (longueur d'origine sur longueur réduite) ; un rapport de réduction est inférieur à $1$.

</details>

Avis : 

---

## 18. `cqc-puissances-decroissantes-faible-0` (vague 3)

**Enonce :**

Quelle est la forme développée, réduite et ordonnée suivant les puissances décroissantes de $x$ de l'expression $P(x) = (5x-2)^{2}$ ?

- a) $25x^{2}-20x+4$
- b) $25x^{2}+4$
- c) $25x^{2}-10x+4$
- d) $25x^{2}-20x-4$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

$(a-b)^{2} = a^{2} - 2ab + b^{2}$ : le développement d'un carré fait toujours apparaître un double produit. Ordonner suivant les puissances décroissantes de $x$ signifie écrire le terme en $x^{2}$ d'abord, puis celui en $x$, puis la constante.

### Corrigé

On développe avec $a=5x$ et $b=2$ :
$$P(x) = (5x-2)^{2} = (5x)^{2} - 2\times 5x \times 2 + 2^{2}$$
$$P(x) = 25x^{2} - 20x + 4$$

L'expression est déjà ordonnée suivant les puissances décroissantes de $x$.

*Contrôle pour $x=1$.* Expression de départ : $(5-2)^{2} = 3^{2} = 9$. Forme développée : $25-20+4=9$. Les deux coïncident.

### Pourquoi les autres réponses sont fausses

- **b)** le double produit $-2\times5x\times2$ a été oublié : on a « distribué » le carré sur chaque terme.
- **c)** le double produit a été écrit $-5x\times2$ sans le facteur $2$ de la formule.
- **d)** le carré de $-2$ a été pris négatif, alors que $b^{2}=2^{2}=4$ est toujours positif.

</details>

Avis : 

---

## 19. `cqc-puissances-faible-0` (vague 3)

**Enonce :**

On pose $A = 3^{-2} \times 3^{4}$. Quelle est la valeur de $A$ ?

- a) $-9$
- b) $9$
- c) $\dfrac{1}{6\,561}$
- d) $6$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Pour multiplier deux puissances de même base, on additionne les exposants : $a^{m}\times a^{n}=a^{m+n}$. Un exposant négatif ne rend pas le résultat négatif : il correspond à un inverse.

### Corrigé

$$A = 3^{-2}\times 3^{4} = 3^{-2+4}=3^{2}=9$$

$$A=9$$

*Contrôle.* $3^{-2}=\dfrac{1}{9}$ et $3^{4}=81$, donc $\dfrac{1}{9}\times81=9$.

### Pourquoi les autres réponses sont fausses

- **a)** l'exposant négatif a été interprété comme un signe moins : $3^{-2}$ n'est pas négatif, c'est $\dfrac{1}{9}$.
- **c)** les exposants ont été multipliés ($-2\times4=-8$) au lieu d'être additionnés.
- **d)** l'exposant est juste ($3^{2}$), mais $3^{2}$ a été calculé comme $3\times2=6$ au lieu de $3\times3=9$.

</details>

Avis : 

---

## 20. `cqc-equation-de-droite-elevee-5` (vague 3)

**Enonce :**

On considère la droite $(D)$ d'équation $2x - y + 3 = 0$. Quelle est une équation de la droite $(\Delta)$ passant par le point $A(1\,;\,2)$ et perpendiculaire à $(D)$ ?

- a) $2x - y = 0$
- b) $x - 2y + 3 = 0$
- c) $x + 2y - 5 = 0$
- d) $x + 2y - 3 = 0$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode
Deux droites de coefficients directeurs $a$ et $a'$ sont perpendiculaires lorsque $a \times a' = -1$. On commence donc par lire le coefficient directeur de $(D)$, on en déduit celui de $(\Delta)$, puis on détermine son équation avec le point donné.

### Corrigé
*Coefficient directeur de $(D)$.* On isole $y$ :

$$2x - y + 3 = 0 \quad \Longrightarrow \quad y = 2x + 3$$

Le coefficient directeur de $(D)$ est $2$.

*Coefficient directeur de $(\Delta)$.* Les droites étant perpendiculaires, $a_{\Delta} \times 2 = -1$, donc

$$a_{\Delta} = -\frac{1}{2}$$

*Calcul de l'ordonnée à l'origine $b$.* Le point $A(1\,;\,2)$ appartient à $(\Delta) : y = -\dfrac{1}{2}x + b$ :

$$2 = -\frac{1}{2} \times 1 + b \qquad b = 2 + \frac{1}{2} = \frac{5}{2}$$

*Équation.* $(\Delta) : y = -\dfrac{1}{2}x + \dfrac{5}{2}$, soit en multipliant par $2$ :

$$2y = -x + 5 \qquad \Longrightarrow \qquad (\Delta) : x + 2y - 5 = 0$$

*Vérification avec $A(1\,;\,2)$.* $1 + 2 \times 2 - 5 = 0$ ✔

### Pourquoi les autres réponses sont fausses
- **a)** Cette droite passe bien par $A$ mais a le même coefficient directeur $2$ que $(D)$ : elle lui est parallèle, pas perpendiculaire.
- **b)** Coefficient directeur $\dfrac{1}{2}$ : on a pris l'inverse de $2$ en oubliant le signe moins ($2 \times \dfrac{1}{2} = 1 \neq -1$).
- **d)** Bon coefficient directeur $-\dfrac{1}{2}$, mais erreur de signe sur $b$ : $b = 2 - \dfrac{1}{2} = \dfrac{3}{2}$ ; le point $A$ ne vérifie pas cette équation ($1 + 4 - 3 = 2 \neq 0$).

</details>

Avis : 

---

