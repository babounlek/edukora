# Vague « partagées » (questions posées à plusieurs examens) : 59 QCM à faire relire par l'enseignant (campagne B1 maths)

Date : 2026-11-01. Sur 228 questions étudiées, **153** sont converties et **75** écartées (cursus incohérent, trop faciles, démonstrations). Vous en voyez **59** : celles que le relecteur aveugle a assorties d'une remarque, celles dont des séries ont été retirées, celles dont le fond a changé à la conversion, et un tirage de 15 autres. Le lot est prêt et simulé (153 mises à jour, 0 bloquant) mais n'est pas en ligne tant que vous n'avez pas répondu. Les 153 résolutions à l'aveugle donnent la clé, sauf deux questions jugées hors niveau pour la série A (série A retirée).

**Principe de niveau :** chaque question est écrite pour l'examen le plus bas où elle est posée (BEPC, puis Probatoire, puis BAC).

## Séries retirées par analogie avec vos avis (à confirmer)

- **Série A retirée** (BAC et Probatoire) de `systeme-lineaire-faible-0` et `-faible-1` (décomposition d'un vecteur dans une base).
- **Série A (Probatoire) retirée** de `arrangement-elevee-0` et `arrangement-moyenne-2` (combinaisons).
- **Série A (BAC) retirée** de `decomposition-en-facteurs-premiers-faible-0` et `-moyenne-2` (arithmétique).

## Points à trancher (nouveaux)

1. **Cursus incohérents** : 75 questions ont été écartées car étiquetées BEPC alors qu'elles utilisent dérivée, discriminant, produit vectoriel, logarithme, complexes... Faut-il retirer le BEPC de leur cursus (puis les convertir au niveau lycée) ? Liste dans `ecartes.json`.
2. **Limites hautes pour le BEPC** : homothétie en coordonnées ou de rapport négatif, classe modale par densité (amplitudes inégales), médiane par interpolation, tableau de signes à trois facteurs, équation irrationnelle simple, équation ((1+t)^2=1{,}21).
3. **Série A** : système 3x3, discussion d'un système paramétré, dénombrement avec arrangements, division euclidienne simple (`division-euclidienne-faible-0`, `-moyenne-2`).
4. **Un énoncé complété** : `classe-modale-moyenne-2` rappelle désormais la règle de la densité.
5. **Questions dont l'énoncé a changé de fond** (démonstration réduite à un résultat, méthode remplacée) : à examiner de près.

Pour chaque question : **OK**, **à corriger** (dire quoi), **à retirer**, ou **retirer la série X**.

## 1. `cqc-systeme-lineaire-elevee-0` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : système 3x3 pour la série A (Probatoire A), à confirmer au programme de 1re A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On considère le système suivant, d'inconnues réelles $x$, $y$ et $z$ :
$$\begin{cases} x + 2y - z = -6 \\ 3x - y + 2z = 21 \\ 2x + y + 3z = 19 \end{cases}$$
Quel est l'unique triplet $(x\,;\,y\,;\,z)$ solution de ce système ?

- a) $(-3\,;\,2\,;\,-5)$
- b) $(-2\,;\,3\,;\,5)$
- c) $(3\,;\,-2\,;\,5)$
- d) $(3\,;\,-2\,;\,-5)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour résoudre un système de trois équations à trois inconnues, on exprime une inconnue en fonction des deux autres à partir d'une équation où son coefficient vaut $1$, puis on la remplace dans les deux autres équations : on obtient un système de deux équations à deux inconnues, que l'on résout par combinaison. On remonte ensuite pour trouver la troisième inconnue, et on vérifie la solution dans les trois équations de départ.

### Corrigé

De la première équation : $x = -6 - 2y + z$.

On remplace dans la deuxième équation :
$$3(-6-2y+z) - y + 2z = 21 \Longleftrightarrow -18 - 7y + 5z = 21 \Longleftrightarrow -7y + 5z = 39.$$

On remplace dans la troisième équation :
$$2(-6-2y+z) + y + 3z = 19 \Longleftrightarrow -12 - 3y + 5z = 19 \Longleftrightarrow -3y + 5z = 31.$$

En soustrayant membre à membre ces deux équations : $(-7y+5z)-(-3y+5z) = 39-31$, soit $-4y = 8$, donc $y = -2$.

Puis $5z = 31 + 3y = 31 - 6 = 25$, donc $z = 5$, et $x = -6 - 2\times(-2) + 5 = 3$.

Vérification :
- $x+2y-z=3+2\times(-2)-5=-6$ ;
- $3x-y+2z=9+2+10=21$ ;
- $2x+y+3z=6-2+15=19$.

(Le déterminant des coefficients vaut $-20\neq0$ : la solution est bien unique.)

$$\boxed{(x\,;\,y\,;\,z) = (3\,;\,-2\,;\,5)}$$

### Pourquoi les autres réponses sont fausses

- **a)** $(-3\,;\,2\,;\,-5)$ : tous les signes sont inversés ; c'est la solution du système dont on aurait changé le signe des seconds membres en les transposant. Première équation : $-3+4+5=6\neq-6$.
- **b)** $(-2\,;\,3\,;\,5)$ : les valeurs de $x$ et de $y$ ont été interverties. Première équation : $-2+6-5=-1\neq-6$.
- **d)** $(3\,;\,-2\,;\,-5)$ : erreur de signe sur $z$ en remontant. Première équation : $3-4+5=4\neq-6$.

</details>

Avis : 

---

## 2. `cqc-aire-d-un-trapeze-moyenne-0` (séries BEPC: PROBATOIRE:D)

**Énoncé :**

$RSTU$ est un trapèze dont les côtés $[RS]$ et $[TU]$ sont parallèles. Son aire vaut $105$ cm², sa grande base $RS$ mesure $18$ cm et sa hauteur mesure $7$ cm.

Quelle est la longueur de la petite base $TU$ ?

- a) $12$ cm
- b) $30$ cm
- c) $15$ cm
- d) $48$ cm

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsque l'aire, la hauteur et l'une des deux bases d'un trapèze sont connues, on repart de la formule $\mathcal{A} = \dfrac{(B+b)\times h}{2}$ et on l'utilise comme une équation d'inconnue $b$ (ou $B$), en isolant progressivement le terme cherché.

### Corrigé

On a $\mathcal{A} = 105$ cm², $B = RS = 18$ cm et $h = 7$ cm. On cherche $b = TU$.

$105 = \dfrac{(18+b)\times 7}{2}$, donc $210 = (18+b)\times 7$, donc $18+b = \dfrac{210}{7} = 30$, et $b = 30 - 18 = 12$.

Vérification : $\dfrac{(18+12)\times 7}{2} = \dfrac{210}{2} = 105$.

La petite base $TU$ mesure donc $12$ cm.

### Pourquoi les autres réponses sont fausses

- **b)** $30$ cm : c'est la somme $B+b$ ; on a oublié de retrancher la grande base $18$.
- **c)** $15$ cm : on a calculé $105\div7$ en oubliant de multiplier l'aire par $2$ (et sans retrancher $18$).
- **d)** $48$ cm : on a ajouté $18$ au lieu de le retrancher ($30+18$).

</details>

Avis : 

---

## 3. `cqc-arrangement-elevee-0` (séries PROBATOIRE:A PROBATOIRE:C PROBATOIRE:E)

**Série(s) retirée(s) par analogie avec vos avis :** PROBATOIRE:A.

**Remarque du relecteur :** LIMITE : dénombrement combinant combinaisons et arrangements, exigeant pour la série A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Un jury de contrôle qualité de 4 personnes doit être constitué à partir d'une équipe technique de 12 personnes, composée de 7 hommes et 5 femmes. Le jury doit compter exactement 2 femmes et 2 hommes. Une fois les 4 membres du jury désignés, il faut attribuer parmi eux un poste de président du jury et un poste de rapporteur (deux fonctions distinctes) ; les deux autres membres du jury n'occupent aucune fonction particulière.

Combien de compositions de jury, fonctions attribuées comprises, sont-elles possibles au total ?

- a) $210$
- b) $1260$
- c) $10080$
- d) $2520$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour un dénombrement combinant des contraintes de catégorie et une attribution de fonctions distinctes, on procède par étapes : chaque contrainte de catégorie (un effectif imposé de femmes, un effectif imposé d'hommes) se traite par une combinaison $C_n^p$ propre à sa catégorie, et ces nombres se multiplient (principe multiplicatif) ; puis, dans chaque groupe retenu, l'attribution de fonctions distinctes à une partie de ses membres se traite par un arrangement $A_n^p$, portant sur le nombre de fonctions à pourvoir.

### Corrigé

**Étape 1 : groupe de 4 avec exactement 2 femmes et 2 hommes.**
Choix des 2 femmes parmi 5 : $C_5^2 = \dfrac{5!}{2!\,3!} = 10$. Choix des 2 hommes parmi 7 : $C_7^2 = \dfrac{7!}{2!\,5!} = 21$. Nombre de groupes : $10 \times 21 = 210$.

**Étape 2 : attribution des 2 fonctions distinctes (président, rapporteur) parmi les 4 membres.** L'ordre compte (président puis rapporteur) : $A_4^2 = 4 \times 3 = 12$.

**Principe multiplicatif :** $210 \times 12 = 2520$.

On peut former **2520 compositions de jury différentes**, fonctions attribuées comprises.

### Pourquoi les autres réponses sont fausses

- **a)** $210$ : c'est le nombre de groupes de 4 ; on a oublié l'attribution des deux fonctions.
- **b)** $1260$ : on a compté $210\times C_4^2 = 210\times6$, en choisissant les 2 membres qui ont une fonction sans distinguer le président du rapporteur.
- **c)** $10080$ : on a compté $A_5^2\times A_7^2\times A_4^2 = 20\times42\times12$, en tenant compte à tort de l'ordre dans le choix des femmes et des hommes.

</details>

Avis : 

---

## 4. `cqc-classe-modale-faible-0` (séries BAC:A BEPC: PROBATOIRE:A PROBATOIRE:D)

**Remarque du relecteur :** LIMITE : classe modale à amplitudes inégales (densité) rarement traitée au BEPC, où les classes sont d'ordinaire de même amplitude.

**Énoncé :**

Une ONG a mesuré la consommation d'eau quotidienne, en litres, de 45 ménages d'un quartier, et a regroupé les résultats dans le tableau suivant, où les deux classes n'ont pas la même amplitude :

| Consommation (L/jour) | [0,60[ | [60,90[ |
|---|---|---|
| Nombre de ménages $n_i$ | 24 | 21 |

Quelle est la classe modale de cette série, et pour quelle raison ?

- a) $[0\,;\,60[$, car son effectif, $24$, est le plus grand.
- b) $[0\,;\,60[$, car le quotient de l'amplitude par l'effectif y vaut $\dfrac{5}{2}$, contre $\dfrac{10}{7}$ pour $[60\,;\,90[$.
- c) $[60\,;\,90[$, car sa densité (effectif divisé par amplitude), $0{,}7$, dépasse celle de $[0\,;\,60[$, qui vaut $0{,}4$.
- d) Aucune : une série dont les classes n'ont pas la même amplitude n'a pas de classe modale.

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsque les classes d'une série n'ont pas toutes la même amplitude, comparer directement leurs effectifs n'a pas de sens : une classe plus large accumule mécaniquement plus d'individus. On compare alors la **densité** de chaque classe, définie par densité $=\dfrac{\text{effectif}}{\text{amplitude}}$ ; la classe modale est celle dont la densité est la plus grande.

### Corrigé

Amplitude de $[0\,;\,60[$ : $60-0=60$. Amplitude de $[60\,;\,90[$ : $90-60=30$. Les amplitudes diffèrent, il faut donc comparer les densités.

Densité de $[0\,;\,60[$ : $\dfrac{24}{60}=0{,}4$ ménage par litre. Densité de $[60\,;\,90[$ : $\dfrac{21}{30}=0{,}7$ ménage par litre.

Comme $0{,}7>0{,}4$, la classe $[60\,;\,90[$ est plus « dense » que $[0\,;\,60[$, bien qu'elle contienne moins de ménages (21 contre 24). La classe modale est donc $[60\,;\,90[$.

(Vérification : $24+21=45$ ménages.)

### Pourquoi les autres réponses sont fausses

- **a)** On a comparé les effectifs bruts, ce qui n'a pas de sens quand les amplitudes sont différentes.
- **b)** On a calculé l'inverse de la densité (amplitude divisée par effectif : $\dfrac{60}{24}=\dfrac{5}{2}$ et $\dfrac{30}{21}=\dfrac{10}{7}$), puis retenu la plus grande valeur.
- **d)** Une série à classes d'amplitudes inégales a bien une classe modale : il suffit de comparer les densités.

</details>

Avis : 

---

## 5. `cqc-division-euclidienne-moyenne-2` (séries BAC:A BAC:C BAC:E BEPC: PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Un pêcheur affirme avoir attrapé un nombre entier $N$ de poissons tel que la division euclidienne de $N$ par $13$ donne pour quotient $22$ et pour reste $9$. Un camarade prétend que le couple $(21\,;\,22)$ est, lui aussi, un couple quotient-reste de la division euclidienne de ce même $N$ par $13$.

Quelle affirmation est exacte ?

- a) $N=295$ et le camarade a raison, car $13\times21+22=295$.
- b) $N=295$ et le camarade a tort, car le reste $22$ n'est pas strictement inférieur au diviseur $13$.
- c) $N=295$ et le camarade a tort, car $13\times21+22\neq295$.
- d) $N=211$ et le camarade a tort, car le reste $22$ n'est pas strictement inférieur à $13$.

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans la division euclidienne de $N$ par $d$, le quotient $Q$ et le reste $r$ vérifient $N=dQ+r$ **et** $0\leqslant r<d$. Ce couple est unique : si $N=dQ+r=dQ'+r'$ avec $0\leqslant r<d$ et $0\leqslant r'<d$, alors $d(Q-Q')=r'-r$ est un multiple de $d$ strictement compris entre $-d$ et $d$, donc nul. L'égalité $N=dQ+r$ seule ne suffit pas : il faut vérifier la condition sur le reste.

### Corrigé

$N=13\times22+9=286+9=295$, et $0\leqslant9<13$ : le couple $(22\,;\,9)$ convient.

Pour le couple du camarade : $13\times21+22=273+22=295$, l'égalité est bien vérifiée. Mais le reste proposé, $22$, n'est pas strictement inférieur au diviseur $13$ : la condition $0\leqslant r<13$ n'est pas respectée.

Par unicité du couple quotient-reste, le seul couple valide est $(22\,;\,9)$ : $N=295$ et le camarade a tort, parce que $22\geqslant13$.

### Pourquoi les autres réponses sont fausses

- **a)** L'égalité $13\times21+22=295$ est vraie, mais elle ne suffit pas : le reste doit être strictement inférieur à $13$.
- **c)** La raison est fausse : $13\times21+22$ vaut bien $295$.
- **d)** On a confondu les rôles du diviseur et du reste en calculant $22\times9+13=211$ au lieu de $13\times22+9$.

</details>

Avis : 

---

## 6. `cqc-homothetie-faible-1` (séries BAC:C BAC:D BAC:E BAC:TI BEPC: PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : homothétie en coordonnées (déterminer le rapport puis l'image) au BEPC, à vérifier dans le programme de 3e.

**Énoncé :**

Le plan est muni d'un repère. Soit $h$ une homothétie de centre $I(3;-2)$. On sait que $h$ transforme le point $A(5;2)$ en le point $A'(11;14)$.

Quelles sont les coordonnées de l'image $B'$ du point $B(0;4)$ par $h$ ?

- a) $(-9;22)$
- b) $(-12;24)$
- c) $(0;16)$
- d) $(-9;6)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Si une homothétie de centre $I$ transforme $A$ en $A'$, alors $\overrightarrow{IA'} = k\overrightarrow{IA}$ : comparer les coordonnées des deux vecteurs permet de retrouver le rapport $k$. Une fois $k$ connu, l'image $M'$ de tout point $M$ se calcule par $\overrightarrow{IM'} = k\overrightarrow{IM}$, puis on ajoute les coordonnées du centre.

### Corrigé

**Rapport $k$.** $\overrightarrow{IA}=(5-3;2-(-2))=(2;4)$ et $\overrightarrow{IA'}=(11-3;14-(-2))=(8;16)$. On doit avoir $8=2k$ et $16=4k$, ce qui donne $k=4$ dans les deux cas.

**Image de $B$.** $\overrightarrow{IB}=(0-3;4-(-2))=(-3;6)$, donc $\overrightarrow{IB'}=4\overrightarrow{IB}=(-12;24)$.

Les coordonnées de $B'$ sont $(3-12;-2+24)$, soit $B'(-9;22)$.

### Pourquoi les autres réponses sont fausses

- **b)** $(-12;24)$ : ce sont les coordonnées du vecteur $\overrightarrow{IB'}$ ; on a oublié d'ajouter celles du centre $I$.
- **c)** $(0;16)$ : on a multiplié les coordonnées de $B$ par $4$, comme si le centre était l'origine du repère.
- **d)** $(-9;6)$ : erreur de signe dans l'ordonnée de $\overrightarrow{IB}$, calculée $4-2=2$ au lieu de $4-(-2)=6$.

</details>

Avis : 

---

## 7. `cqc-inequation-faible-0` (séries BEPC: PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Énoncé :**

Quel est l'ensemble des solutions dans $\mathbb{R}$ de l'inéquation $-7\leqslant 3x+2\leqslant 8$ ?

- a) $]-3\,;\,2[$
- b) $[-3\,;\,2]$
- c) $\left[-\dfrac{5}{3}\,;\,\dfrac{10}{3}\right]$
- d) $[-9\,;\,6]$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour résoudre un encadrement de la forme $p\leqslant ax+b\leqslant q$ (avec $a>0$), on isole $x$ au centre en appliquant la même opération aux trois membres : on conserve le sens des inégalités quand on ajoute ou soustrait un nombre, ou quand on multiplie ou divise par un nombre strictement positif ; on inverserait les deux inégalités pour un nombre négatif.

### Corrigé

On soustrait $2$ aux trois membres : $-7-2\leqslant 3x\leqslant 8-2$, soit $-9\leqslant 3x\leqslant 6$.

On divise les trois membres par $3$, nombre strictement positif : $-3\leqslant x\leqslant 2$.

Vérification : pour $x=-3$, $3\times(-3)+2=-7$ ; pour $x=2$, $3\times2+2=8$ ; les deux bornes sont atteintes, et les inégalités sont larges, donc incluses.

L'ensemble solution est $S=[-3\,;\,2]$.

### Pourquoi les autres réponses sont fausses

- **a)** Les bornes ont été exclues alors que les inégalités sont larges ($\leqslant$).
- **c)** On a ajouté $2$ aux trois membres au lieu de le soustraire : $\dfrac{-7+2}{3}=-\dfrac{5}{3}$ et $\dfrac{8+2}{3}=\dfrac{10}{3}$.
- **d)** On s'est arrêté à l'encadrement de $3x$, sans diviser par $3$.

</details>

Avis : 

---

## 8. `cqc-moyenne-ponderee-moyenne-1` (séries BAC:A BEPC: PROBATOIRE:A PROBATOIRE:C PROBATOIRE:E)

**Remarque du relecteur :** Le regroupement imposé est un détour artificiel (la moyenne sur les classes d'origine vaut 20,06) ; préciser « en prenant les centres des classes ».

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Un laboratoire de contrôle qualité a testé la durée de vie, en mois, de 80 ampoules LED avant leur première panne. Les résultats, groupés en classes d'amplitudes inégales, sont donnés dans le tableau suivant :

| Durée de vie (mois) | [0,10[ | [10,15[ | [15,20[ | [20,25[ | [25,30[ | [30,40[ |
|---|---|---|---|---|---|---|
| Nombre d'ampoules $n_i$ | 6 | 14 | 22 | 18 | 12 | 8 |

On regroupe cette série en 4 classes de même amplitude, égale à 10 mois. À partir de cette série regroupée, quelle est la durée de vie moyenne $\bar x$ d'une ampoule ?

- a) $15$ mois
- b) $25$ mois
- c) $20$ mois
- d) $20{,}75$ mois

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour obtenir des classes de même amplitude, on fusionne des classes adjacentes en additionnant leurs effectifs ; l'effectif total ne change pas. On calcule ensuite la moyenne pondérée à partir des centres des **nouvelles** classes.

### Corrigé

$[0\,;\,10[$ reste inchangée (effectif $6$). $[10\,;\,15[$ et $[15\,;\,20[$ se regroupent en $[10\,;\,20[$, d'effectif $14+22=36$. $[20\,;\,25[$ et $[25\,;\,30[$ se regroupent en $[20\,;\,30[$, d'effectif $18+12=30$. $[30\,;\,40[$ reste inchangée (effectif $8$).

| Durée regroupée (mois) | [0,10[ | [10,20[ | [20,30[ | [30,40[ |
|---|---|---|---|---|
| Effectif $n_i$ | 6 | 36 | 30 | 8 |

Vérification : $6+36+30+8=80$.

Les centres des nouvelles classes sont $5$, $15$, $25$, $35$ :
$$\sum n_ic_i = 6\times5+36\times15+30\times25+8\times35=30+540+750+280=1600$$

Donc $\bar x=\dfrac{1600}{80}=20$. La durée de vie moyenne d'une ampoule est de **20 mois**.

### Pourquoi les autres réponses sont fausses

- **a)** $15$ mois : on a pondéré les bornes inférieures des classes ($0$, $10$, $20$, $30$) au lieu de leurs centres.
- **b)** $25$ mois : on a pondéré les bornes supérieures des classes ($10$, $20$, $30$, $40$) au lieu de leurs centres.
- **d)** $20{,}75$ mois : les effectifs des deux classes centrales ont été intervertis en reportant le tableau regroupé ($30$ pour $[10\,;\,20[$ et $36$ pour $[20\,;\,30[$).

</details>

Avis : 

---

## 9. `cqc-rapport-moyenne-0` (séries BEPC: PROBATOIRE:C PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : homothétie en coordonnées (calcul du rapport puis de l'image), à la limite haute du BEPC.

**Énoncé :**

Le plan est muni d'un repère orthonormé. On considère une homothétie $h$ de centre $\Omega(-1\,;\,2)$. On sait que le point $A(3\,;\,4)$ a pour image $A'(7\,;\,6)$ par $h$.

Quelles sont les coordonnées de l'image $B'$ du point $B(2\,;\,-3)$ par $h$ ?

- a) $(6\,;\,-10)$
- b) $(4\,;\,-6)$
- c) $(5\,;\,-8)$
- d) $(5\,;\,0)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour déterminer le rapport $k$ d'une homothétie de centre $\Omega$ connaissant un point $M$ et son image $M'$, on calcule les vecteurs $\overrightarrow{\Omega M}$ et $\overrightarrow{\Omega M'}$ : ils vérifient $\overrightarrow{\Omega M'} = k\,\overrightarrow{\Omega M}$, et les deux coordonnées doivent donner la même valeur de $k$. On applique ensuite cette relation au point dont on cherche l'image.

### Corrigé

$\overrightarrow{\Omega A} = (3-(-1)\,;\,4-2) = (4\,;\,2)$ et $\overrightarrow{\Omega A'} = (7-(-1)\,;\,6-2) = (8\,;\,4)$.

$8 = 2\times 4$ et $4 = 2\times 2$ : le rapport est $k=2$.

$\overrightarrow{\Omega B} = (2-(-1)\,;\,-3-2) = (3\,;\,-5)$, donc $\overrightarrow{\Omega B'} = 2\,\overrightarrow{\Omega B} = (6\,;\,-10)$.

D'où $x_{B'} = -1+6 = 5$ et $y_{B'} = 2-10 = -8$ : $B'(5\,;\,-8)$.

Contrôle : $\Omega B = \sqrt{34}$ et $\Omega B' = \sqrt{136} = 2\sqrt{34}$, soit $2$ fois $\Omega B$.

### Pourquoi les autres réponses sont fausses

- **a)** $(6\,;\,-10)$ : ce sont les coordonnées du vecteur $\overrightarrow{\Omega B'}$ ; on a oublié d'ajouter celles du centre $\Omega$.
- **b)** $(4\,;\,-6)$ : on a multiplié les coordonnées de $B$ par $2$, comme si le centre était l'origine.
- **d)** $(5\,;\,0)$ : erreur de signe dans l'ordonnée de $\overrightarrow{\Omega B}$, calculée $-3+2=-1$ au lieu de $-3-2=-5$.

</details>

Avis : 

---

## 10. `cqc-tableau-de-signes-elevee-5` (séries BAC:A BEPC: PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : tableau de signes d'un quotient à trois facteurs, en haut du programme BEPC (signe de ax+b).

**Énoncé :**

On considère l'expression déjà factorisée $R(x) = \dfrac{(2x+3)(x-1)(x-3)}{x^2+2}$, définie pour tout réel $x$ (le dénominateur $x^2+2$ ne s'annule jamais, car $x^2+2 \geqslant 2$ quel que soit $x$).

Voici un tableau de signes partiellement rempli pour $R(x)$ : les lignes des trois facteurs du numérateur et celle du dénominateur sont entièrement données, mais la dernière ligne contient trois cases à compléter, notées « ? ».

| Intervalle | $x<-\frac{3}{2}$ | $x=-\frac{3}{2}$ | $-\frac{3}{2}<x<1$ | $x=1$ | $1<x<3$ | $x=3$ | $x>3$ |
|---|---|---|---|---|---|---|---|
| Signe de $2x+3$ | $-$ | $0$ | $+$ | $+$ | $+$ | $+$ | $+$ |
| Signe de $x-1$ | $-$ | $-$ | $-$ | $0$ | $+$ | $+$ | $+$ |
| Signe de $x-3$ | $-$ | $-$ | $-$ | $-$ | $-$ | $0$ | $+$ |
| Signe de $x^2+2$ | $+$ | $+$ | $+$ | $+$ | $+$ | $+$ | $+$ |
| Signe de $R(x)$ | $?$ | $0$ | $?$ | $0$ | $?$ | $0$ | $+$ |

Quels sont, dans l'ordre, les signes des trois cases manquantes, et combien de fois le signe de $R(x)$ change-t-il en parcourant $\mathbb{R}$ de $-\infty$ à $+\infty$ ?

- a) $-$, $+$, $-$ ; le signe change $3$ fois.
- b) $+$, $-$, $+$ ; le signe change $3$ fois.
- c) $-$, $+$, $-$ ; le signe change $4$ fois.
- d) $-$, $-$, $+$ ; le signe change $1$ fois.

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand le dénominateur d'un quotient est toujours strictement positif (ici $x^2+2 \geqslant 2$), il ne modifie pas le signe : le signe du quotient est celui du numérateur. On l'obtient colonne par colonne avec la règle des signes, en comptant les facteurs négatifs : un nombre pair donne un résultat positif, un nombre impair un résultat négatif.

### Corrigé

**Sur $x<-\frac{3}{2}$** : trois facteurs négatifs (nombre impair), donc $R(x)<0$. Contrôle : $R(-2) = \dfrac{(-1)\times(-3)\times(-5)}{6} = -\dfrac{5}{2} < 0$.

**Sur $-\frac{3}{2}<x<1$** : deux facteurs négatifs ($x-1$ et $x-3$), nombre pair, donc $R(x)>0$. Contrôle : $R(0) = \dfrac{3\times(-1)\times(-3)}{2} = \dfrac{9}{2} > 0$.

**Sur $1<x<3$** : un seul facteur négatif ($x-3$), donc $R(x)<0$. Contrôle : $R(2) = \dfrac{7\times1\times(-1)}{6} = -\dfrac{7}{6} < 0$.

La dernière ligne est donc : $-$, $0$, $+$, $0$, $-$, $0$, $+$.

**Changements de signe.** Le signe passe de négatif à positif en $-\frac{3}{2}$, de positif à négatif en $1$, puis de négatif à positif en $3$ : il change **3 fois**.

### Pourquoi les autres réponses sont fausses

- **b)** Règle des signes appliquée à l'envers (un nombre impair de facteurs négatifs donne un résultat négatif, pas positif).
- **c)** Les signes sont justes, mais on a compté les $4$ intervalles au lieu des $3$ changements de signe, qui ont lieu aux trois valeurs qui annulent $R(x)$.
- **d)** On a pris le signe « majoritaire » de chaque colonne au lieu d'appliquer la règle des signes : sur $-\frac{3}{2}<x<1$, deux signes $-$ contre un $+$ donnent pourtant un produit positif.

</details>

Avis : 

---

## 11. `cqc-echelle-moyenne-0` (séries BAC:D BAC:TI BEPC: PROBATOIRE:C PROBATOIRE:E)

**Énoncé :**

Un randonneur suit un sentier qui relie deux villages distants en réalité de $15$ km. Sur la carte qu'il utilise, ce sentier est représenté par un trait de $3$ cm.

Quelle est l'échelle de cette carte, écrite sous la forme $\dfrac{1}{k}$ ?

- a) $\dfrac{1}{500\,000}$
- b) $\dfrac{1}{5}$
- c) $\dfrac{1}{5\,000}$
- d) $\dfrac{1}{50\,000}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

L'échelle d'un plan est le rapport entre la distance mesurée sur le plan et la distance réelle correspondante, **exprimées dans la même unité** : échelle $= \dfrac{\text{distance plan}}{\text{distance réelle}}$. On simplifie ensuite la fraction jusqu'à obtenir un numérateur égal à $1$.

### Corrigé

On exprime les deux distances en centimètres : $15$ km $= 15\,000$ m $= 1\,500\,000$ cm.

Échelle $= \dfrac{3}{1\,500\,000} = \dfrac{1}{500\,000}$ (on divise numérateur et dénominateur par $3$).

L'échelle de cette carte est **$\dfrac{1}{500\,000}$**.

### Pourquoi les autres réponses sont fausses

- **b)** $\dfrac{1}{5}$ : on a divisé $3$ par $15$ sans convertir les kilomètres en centimètres.
- **c)** $\dfrac{1}{5\,000}$ : on a converti les kilomètres en mètres ($15\,000$ m) en gardant les centimètres sur la carte.
- **d)** $\dfrac{1}{50\,000}$ : erreur de conversion, $15$ km comptés $150\,000$ cm au lieu de $1\,500\,000$ cm.

</details>

Avis : 

---

## 12. `cqc-systeme-lineaire-faible-0` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A, PROBATOIRE:A.

**Remarque du relecteur :** Décomposition d'un vecteur dans une base : calcul vectoriel absent du programme léger de la série A (Probatoire A et BAC A listés).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan est muni d'une base $(\vec{e_1}\,;\,\vec{e_2})$. On donne les trois vecteurs suivants, exprimés dans cette base :

$$\vec{u} = 3\vec{e_1} + 5\vec{e_2}, \qquad \vec{v} = \vec{e_1} + 2\vec{e_2}, \qquad \vec{w} = 8\vec{e_1} + 13\vec{e_2}.$$

Quels sont les réels $\alpha$ et $\beta$ tels que $\vec{w} = \alpha\vec{u} + \beta\vec{v}$ ?

- a) $\alpha=3$ et $\beta=-1$
- b) $\alpha=3$ et $\beta=1$
- c) $\alpha=-1$ et $\beta=3$
- d) $\alpha=2$ et $\beta=2$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Décomposer un vecteur $\vec{w}$ comme combinaison de deux vecteurs donnés $\vec{u}$ et $\vec{v}$ revient à identifier séparément les coefficients de $\vec{e_1}$ et de $\vec{e_2}$ de part et d'autre de l'égalité $\vec{w}=\alpha\vec{u}+\beta\vec{v}$ : on obtient ainsi un système linéaire de deux équations aux deux inconnues $\alpha$ et $\beta$.

### Corrigé

En remplaçant $\vec{u}$, $\vec{v}$ et $\vec{w}$ par leurs expressions dans la base $(\vec{e_1}\,;\,\vec{e_2})$ :
$$\alpha(3\vec{e_1}+5\vec{e_2}) + \beta(\vec{e_1}+2\vec{e_2}) = 8\vec{e_1}+13\vec{e_2}$$
$$(3\alpha+\beta)\vec{e_1} + (5\alpha+2\beta)\vec{e_2} = 8\vec{e_1}+13\vec{e_2}$$

Par identification des coefficients de $\vec{e_1}$ et de $\vec{e_2}$ :
$$\begin{cases} 3\alpha + \beta = 8 \\ 5\alpha + 2\beta = 13 \end{cases}$$

De la première équation : $\beta = 8-3\alpha$. En remplaçant dans la seconde : $5\alpha + 2(8-3\alpha) = 13 \Rightarrow 5\alpha+16-6\alpha=13 \Rightarrow -\alpha=-3 \Rightarrow \alpha=3$.

On en déduit $\beta = 8-3\times3 = -1$.

Vérification : $3\times3+(-1)=8$ et $5\times3+2\times(-1)=13$.

$$\boxed{\alpha=3\,;\ \beta=-1 \qquad \text{c'est-à-dire } \vec{w}=3\vec{u}-\vec{v}}$$

### Pourquoi les autres réponses sont fausses

- **b)** erreur de signe en fin de calcul : $8-3\times3$ vaut $-1$ et non $1$ ; on obtiendrait $3\times3+1=10\neq8$.
- **c)** les coefficients ont été lus en colonnes au lieu de lignes (système $\alpha+3\beta=8$, $2\alpha+5\beta=13$) : les rôles de $\vec u$ et $\vec v$ sont confondus.
- **d)** ce couple vérifie la première équation ($6+2=8$) mais pas la seconde ($10+4=14\neq13$) : il faut vérifier les deux équations.

</details>

Avis : 

---

## 13. `cqc-arrangement-faible-1` (séries PROBATOIRE:A PROBATOIRE:C PROBATOIRE:E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Parmi 5 candidats à la direction d'un club de lecture, il faut d'abord retenir 2 finalistes, sans aucune distinction de rôle entre eux à ce stade. Une fois ces 2 finalistes connus, on décide lequel des deux devient président du club et lequel devient simple membre du bureau (les deux rôles sont différents).

Combien de résultats finaux différents peut-on obtenir, en tenant compte à la fois de l'identité des 2 finalistes retenus et de l'attribution des rôles entre eux ?

- a) $10$
- b) $25$
- c) $20$
- d) $9$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand un problème de dénombrement aboutit à attribuer des rôles distincts à des personnes distinctes, chaque résultat final est une liste ordonnée sans répétition (président, membre). On compte ces listes avec le principe multiplicatif : nombre de choix pour le premier rôle, multiplié par le nombre de choix restants pour le second.

### Corrigé

Un résultat final est entièrement déterminé par le choix du président puis par celui du simple membre, qui doit être une autre personne.

- Choix du président : 5 possibilités.
- Choix du simple membre parmi les 4 candidats restants : 4 possibilités.

**Principe multiplicatif :**
$$5 \times 4 = 20$$

On obtient **20 résultats finaux différents**.

Contrôle par les deux étapes de l'énoncé : il y a 10 paires de finalistes possibles (on peut les lister : $\{1\,;2\}$, $\{1\,;3\}$, ..., $\{4\,;5\}$), et chaque paire donne 2 attributions des rôles, soit $10\times2=20$ : on retrouve le même résultat, qui est le nombre d'arrangements $A_5^2 = 5\times4$.

### Pourquoi les autres réponses sont fausses

- **a)** on a seulement compté les paires de finalistes, en oubliant les 2 façons d'attribuer les rôles.
- **b)** $5\times5$ suppose qu'une même personne puisse occuper les deux rôles, ce qui est impossible.
- **d)** $5+4$ : on a additionné les nombres de choix au lieu de les multiplier.

</details>

Avis : 

---

## 14. `cqc-classe-modale-moyenne-0` (séries BAC:A BEPC: PROBATOIRE:A PROBATOIRE:D)

**Remarque du relecteur :** LIMITE : classe modale à amplitudes inégales (densité) rarement traitée au BEPC, où les classes sont d'amplitude égale.

**Énoncé :**

Une entreprise de messagerie a pesé, en kilogrammes, les 90 colis traités au cours d'une matinée, et les a répartis dans le tableau suivant, où les classes n'ont pas toutes la même amplitude :

| Poids (kg) | $[0\,;2[$ | $[2\,;5[$ | $[5\,;8[$ | $[8\,;16[$ |
|---|---|---|---|---|
| Nombre de colis $n_i$ | 14 | 27 | 18 | 31 |

Un employé affirme : « La classe modale est $[8\,;16[$, car c'est elle qui regroupe le plus de colis (31 sur 90). » Quelle est la véritable classe modale de cette série ?

- a) $[2\,;5[$
- b) $[8\,;16[$
- c) $[0\,;2[$
- d) $[5\,;8[$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
La classe modale n'est la classe de plus grand effectif brut qu'à condition que toutes les classes aient la même amplitude. Dès que les amplitudes diffèrent, il faut comparer la densité de chaque classe, $\text{densité}=\dfrac{\text{effectif}}{\text{amplitude}}$, et non les effectifs eux-mêmes : une classe large peut accumuler beaucoup d'individus sans être réellement la plus concentrée.

### Corrigé
Calculons d'abord l'amplitude de chaque classe : $[0\,;2[$ : $2-0=2$ ; $[2\,;5[$ : $5-2=3$ ; $[5\,;8[$ : $8-5=3$ ; $[8\,;16[$ : $16-8=8$. Les amplitudes ne sont pas toutes égales : l'employé ne peut donc pas comparer les effectifs bruts sans précaution.

Calculons la densité de chaque classe :
$[0\,;2[$ : $\dfrac{14}{2}=7$
$[2\,;5[$ : $\dfrac{27}{3}=9$
$[5\,;8[$ : $\dfrac{18}{3}=6$
$[8\,;16[$ : $\dfrac{31}{8}=3{,}875$

La densité la plus élevée est $9$, atteinte par la classe $[2\,;5[$, et non par $[8\,;16[$, dont la densité n'est que $3{,}875$, la plus faible des quatre.

L'employé a tort : $[8\,;16[$ contient bien le plus grand nombre de colis en valeur brute, mais uniquement parce que son amplitude (8 kg) est nettement supérieure aux autres. Une fois ramenée à une largeur comparable, cette classe est en réalité la moins dense de la série. La véritable classe modale est $[2\,;5[$.

(Vérification : $14+27+18+31=90$, ce qui correspond bien aux 90 colis annoncés.)

### Pourquoi les autres réponses sont fausses

- **b)** c'est la classe de plus grand effectif brut, mais aussi la plus large : sa densité ($\dfrac{31}{8}=3{,}875$) est la plus faible.
- **c)** c'est la classe la plus étroite ; sa densité vaut $7$, inférieure à celle de $[2\,;5[$ qui vaut $9$.
- **d)** classe de même amplitude que $[2\,;5[$ mais d'effectif plus petit ($18<27$) : sa densité n'est que de $6$.

</details>

Avis : 

---

## 15. `cqc-fraction-irreductible-moyenne-2` (séries BAC:D BEPC:)

**Énoncé :**

On considère le quotient de puissances suivant :

$$B = \dfrac{2^{5}\times3^{6}\times7}{2^{8}\times3^{2}\times7^{3}}$$

Quelle est l'écriture de $B$ sous forme de fraction irréductible ?

- a) $\dfrac{392}{81}$
- b) $\dfrac{81}{392}$
- c) $\dfrac{81}{2\,744}$
- d) $\dfrac{6\,561}{392}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour simplifier un quotient de puissances de nombres premiers, on regroupe les facteurs de même base au numérateur et au dénominateur, puis on soustrait les exposants : $\dfrac{a^{m}}{a^{n}} = a^{m-n}$. Un exposant final négatif signifie que la puissance correspondante reste au dénominateur ; un exposant final positif signifie qu'elle reste au numérateur.

### Corrigé

On traite chaque base séparément :
- base 2 : $2^{5-8} = 2^{-3}$, donc $2^{3}$ reste au dénominateur ;
- base 3 : $3^{6-2} = 3^{4}$, donc $3^{4}$ reste au numérateur ;
- base 7 : $7^{1-3} = 7^{-2}$, donc $7^{2}$ reste au dénominateur.

Donc $B = \dfrac{3^{4}}{2^{3}\times7^{2}} = \dfrac{81}{8\times49} = \dfrac{81}{392}$.

Vérification de l'irréductibilité : $81 = 3^{4}$ n'a que 3 comme facteur premier, tandis que $392 = 2^{3}\times7^{2}$ n'a que 2 et 7 comme facteurs premiers. Numérateur et dénominateur n'ont donc aucun facteur premier commun : $\dfrac{81}{392}$ est bien irréductible.

### Pourquoi les autres réponses sont fausses

- **a)** les puissances d'exposant négatif ont été placées au numérateur : la fraction est inversée.
- **c)** l'exposant $1$ du $7$ du numérateur a été oublié : on a gardé $7^3=343$ au dénominateur au lieu de $7^2$.
- **d)** les exposants de $3$ ont été additionnés ($3^{6+2}=3^8$) au lieu d'être soustraits.

</details>

Avis : 

---

## 16. `cqc-proportionnalite-faible-0` (séries BAC:D BAC:TI BEPC:)

**Remarque du relecteur :** Contexte de niveau BEPC/collège, très facile pour BAC D et TI.

**Énoncé :**

Pour préparer une pâte à beignets destinée à 5 personnes, une vendeuse de rue utilise 750 g de farine. Elle souhaite préparer la même recette, dans les mêmes proportions, pour 8 personnes.

| Nombre de personnes | 5 | 8 |
|---|---|---|
| Masse de farine (en g) | 750 | ? |

En admettant que la masse de farine utilisée est proportionnelle au nombre de personnes, quelle masse de farine faut-il pour préparer cette recette pour 8 personnes ?

- a) $468{,}75$ g
- b) $1\,050$ g
- c) $1\,200$ g
- d) $6\,000$ g

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Dans un tableau de proportionnalité à deux lignes, un terme manquant se calcule à l'aide d'un produit en croix : on multiplie les deux termes situés en diagonale du terme cherché, puis on divise le résultat par le terme restant du tableau.

### Corrigé
Le terme cherché, noté $x$, est en diagonale avec 8 et 750 ; le terme restant du tableau est 5.

$$x = \dfrac{750 \times 8}{5} = \dfrac{6\,000}{5} = 1\,200$$

Il faut donc **1 200 g de farine** pour préparer cette recette pour 8 personnes.

Vérification par le quotient : $\dfrac{750}{5} = 150$ g par personne, et $\dfrac{1\,200}{8} = 150$ g par personne également : les deux quotients sont égaux, ce qui confirme le résultat.

### Pourquoi les autres réponses sont fausses

- **a)** produit en croix mal placé : $\dfrac{750\times5}{8}$, ce qui donnerait moins de farine pour plus de personnes.
- **b)** modèle additif : on a ajouté $3\times100$ g pour 3 personnes de plus, sans calculer la part par personne ($150$ g).
- **d)** oubli de la division par $5$ : $750\times8$.

</details>

Avis : 

---

## 17. `cqc-rapport-moyenne-1` (séries BEPC: PROBATOIRE:C PROBATOIRE:E)

**Énoncé :**

Dans un triangle $SAB$, les points $M$ et $N$ appartiennent respectivement aux segments $[SA]$ et $[SB]$, avec $(MN)$ parallèle à $(AB)$.

On donne : $SA = 15$ cm, $SM = 6$ cm, $SB = 21$ cm, $SN = 8{,}4$ cm et $AB = 10$ cm.

Quelle est la longueur $MN$ ?

- a) $25$ cm
- b) $\dfrac{20}{3}$ cm
- c) $\dfrac{20}{7}$ cm
- d) $4$ cm

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Lorsque deux droites parallèles coupent deux droites sécantes en un point commun $S$, le théorème de Thalès donne, pour le triangle réduit $SMN$ par rapport à $SAB$, un même rapport $k = \dfrac{SM}{SA} = \dfrac{SN}{SB} = \dfrac{MN}{AB}$. Si les longueurs données ne donnent pas le même rapport sur les deux côtés, les données seraient incompatibles avec une configuration de Thalès.

### Corrigé
1) On calcule séparément les deux rapports :
$$\frac{SM}{SA} = \frac{6}{15} = 0{,}4 \qquad\qquad \frac{SN}{SB} = \frac{8{,}4}{21} = 0{,}4$$

Les deux rapports sont égaux, les données sont donc bien compatibles avec un même rapport de réduction $k = 0{,}4 = \dfrac{2}{5}$.

2) On applique ce rapport à la longueur $AB$ :
$$MN = k \times AB = \frac{2}{5} \times 10 = 4 \text{ cm}$$

Contrôle : le rapport $k=0{,}4$ a été confirmé de façon indépendante par les deux côtés $[SA]$ et $[SB]$ avant d'être appliqué à $AB$ ; le résultat $MN = 4$ cm est donc fiable.

### Pourquoi les autres réponses sont fausses

- **a)** le rapport a été inversé : on a divisé $AB$ par $k$ (ou multiplié par $\dfrac{SA}{SM}$) au lieu de multiplier par $k=\dfrac25$.
- **b)** le rapport $\dfrac{SM}{MA}=\dfrac69$ a été utilisé au lieu de $\dfrac{SM}{SA}$ : Thalès compare des longueurs mesurées depuis $S$.
- **c)** les côtés ont été mélangés : $\dfrac{SM}{SB}=\dfrac6{21}$ associe un point de $[SA]$ à la longueur $SB$.

</details>

Avis : 

---

## 18. `cqc-systeme-lineaire-faible-1` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A, PROBATOIRE:A.

**Remarque du relecteur :** Décomposition d'un vecteur dans une base : hors du programme léger de la série A (Probatoire A et BAC A listés) ; correct pour C, D, E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans une base $(\vec{e_1}\,;\,\vec{e_2})$ du plan, on donne trois vecteurs :
$$\vec{a} = 4\vec{e_1} - \vec{e_2}, \qquad \vec{b} = -\vec{e_1} + 3\vec{e_2}, \qquad \vec{c} = 11\vec{e_1} - 11\vec{e_2}.$$

Quels sont les réels $p$ et $q$ tels que $\vec{c} = p\,\vec{a} + q\,\vec{b}$ ?

- a) $p=2$ et $q=-3$
- b) $p=4$ et $q=5$
- c) $p=11$ et $q=0$
- d) $p=-3$ et $q=2$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour décomposer un vecteur du plan sur deux autres vecteurs donnés, on identifie, de part et d'autre de l'égalité vectorielle, le coefficient de chaque vecteur de la base : cela fournit un système linéaire aux deux inconnues cherchées, que l'on résout ensuite comme un système ordinaire.

### Corrigé

En remplaçant $\vec{a}$, $\vec{b}$ et $\vec{c}$ par leurs expressions :
$$p(4\vec{e_1}-\vec{e_2}) + q(-\vec{e_1}+3\vec{e_2}) = 11\vec{e_1}-11\vec{e_2}$$
$$(4p-q)\vec{e_1} + (-p+3q)\vec{e_2} = 11\vec{e_1}-11\vec{e_2}$$

Par identification :
$$\begin{cases} 4p - q = 11 \\ -p + 3q = -11 \end{cases}$$

De la seconde équation : $p = 3q+11$. En remplaçant dans la première : $4(3q+11) - q = 11 \Rightarrow 12q+44-q=11 \Rightarrow 11q=-33 \Rightarrow q=-3$.

On en déduit $p = 3\times(-3)+11 = 2$.

Vérification : $4\times2-(-3)=8+3=11$ et $-2+3\times(-3)=-2-9=-11$.

$$\boxed{p=2\,;\ q=-3}$$

### Pourquoi les autres réponses sont fausses

- **b)** On a oublié le signe de la seconde coordonnée de $\vec c$ : ce couple résout $-p+3q=11$ au lieu de $-p+3q=-11$.
- **c)** Distributivité incomplète lors de la substitution : $4(3q+11)$ a été écrit $12q+11$ au lieu de $12q+44$.
- **d)** Les rôles de $p$ et $q$ ont été échangés : on a bien $q=-3$ et $p=2$, et non l'inverse.

</details>

Avis : 

---

## 19. `cqc-arrangement-moyenne-0` (séries PROBATOIRE:A PROBATOIRE:C PROBATOIRE:E)

**Énoncé :**

Le digicode d'un immeuble demande de saisir une combinaison de 4 caractères : les deux premiers caractères sont des chiffres distincts choisis parmi les chiffres de 1 à 7 (un même chiffre ne peut pas apparaître deux fois parmi ces deux premiers caractères), les deux derniers caractères sont des lettres, chacune choisie librement parmi les lettres P, Q, R, S, T (une même lettre peut être répétée entre ces deux positions). Combien de combinaisons différentes ce digicode permet-il de former ?

- a) $1225$
- b) $1050$
- c) $840$
- d) $525$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'une combinaison de caractères comporte une partie où les éléments doivent être distincts et où l'ordre compte (un arrangement $A_n^p$), et une autre partie où la répétition est autorisée à chaque emplacement, chaque emplacement de cette seconde partie constitue un choix indépendant parmi $n$ possibilités, soit $n^p$ au total. On calcule chaque partie séparément, puis on applique le principe multiplicatif pour obtenir le nombre total de combinaisons.

### Corrigé

**Partie chiffrée (2 chiffres distincts parmi 7, ordre important) :**
$$A_7^2 = 7 \times 6 = 42$$

**Partie littérale (2 lettres, répétition permise, parmi 5) :** chaque position est un choix libre parmi 5 lettres, donc
$$5 \times 5 = 5^2 = 25$$

**Principe multiplicatif :**
$$42 \times 25 = 1050$$

Ce digicode permet de former **1050 combinaisons différentes**.

### Pourquoi les autres réponses sont fausses

- **a)** On a autorisé la répétition des chiffres : $7^2\times5^2=49\times25=1225$, alors que les deux chiffres doivent être distincts.
- **c)** On a interdit la répétition des lettres : $42\times(5\times4)=42\times20=840$, alors qu'une lettre peut être répétée.
- **d)** On a ignoré l'ordre des deux chiffres (division par $2$ : $21\times25=525$), alors que 12 et 21 sont deux codes différents.

</details>

Avis : 

---

## 20. `cqc-classe-modale-moyenne-2` (séries BAC:A BEPC: PROBATOIRE:A PROBATOIRE:D)

**Remarque du relecteur :** LIMITE : classes d'amplitudes inégales et densité au BEPC, la règle est rappelée dans l'énoncé.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Un club d'athlétisme a chronométré la distance parcourue, en kilomètres, par 58 coureurs lors d'une séance d'entraînement de fond, et a consigné les résultats dans le tableau suivant, où les classes n'ont pas toutes la même amplitude :

| Distance parcourue (km) | [5 ; 8[ | [8 ; 10[ | [10 ; 15[ |
|---|---|---|---|
| Nombre de coureurs $n_i$ | 12 | 15 | 31 |

On rappelle que, lorsque les classes n'ont pas toutes la même amplitude, la classe modale est celle de plus grande densité (effectif divisé par amplitude).

Quelle est la classe modale de cette série ?

- a) La classe $[10\,;\,15[$
- b) La classe $[5\,;\,8[$
- c) La classe $[8\,;\,10[$
- d) Aucune : on ne peut pas définir de classe modale quand les amplitudes sont différentes

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Une classe modale se détermine par sa densité, $\text{densité}=\dfrac{\text{effectif}}{\text{amplitude}}$, dès que les classes d'une série n'ont pas toutes la même amplitude. Comparer uniquement les effectifs bruts revient à avantager systématiquement les classes les plus larges, sans rapport avec la réalité de la répartition.

### Corrigé

Amplitudes : $[5\,;\,8[$ : $8-5=3$ ; $[8\,;\,10[$ : $10-8=2$ ; $[10\,;\,15[$ : $15-10=5$. Les trois classes ont des amplitudes différentes (3, puis 2, puis 5 km) : la comparaison des effectifs bruts n'est donc pas valable ici.

Densités : $[5\,;\,8[$ : $\dfrac{12}{3}=4$ ; $[8\,;\,10[$ : $\dfrac{15}{2}=7{,}5$ ; $[10\,;\,15[$ : $\dfrac{31}{5}=6{,}2$.

La densité la plus élevée est $7{,}5$, atteinte par la classe $[8\,;\,10[$, et non par $[10\,;\,15[$, dont la densité n'est que $6{,}2$.

La classe $[10\,;\,15[$ regroupe le plus grand nombre brut de coureurs, mais son amplitude (5 km) est plus de deux fois supérieure à celle de $[8\,;\,10[$ (2 km), ce qui gonfle son effectif sans traduire une concentration plus forte. La classe modale est donc **$[8\,;\,10[$**.

(Vérification : $12+15+31=58$, ce qui correspond bien aux 58 coureurs annoncés.)

### Pourquoi les autres réponses sont fausses

- **a)** On a comparé les effectifs bruts ($31$ est le plus grand) sans tenir compte des amplitudes inégales ; sa densité n'est que $6{,}2$.
- **b)** On a calculé le quotient à l'envers (amplitude sur effectif : $\dfrac{3}{12}=0{,}25$ est alors le plus grand), au lieu de l'effectif sur l'amplitude.
- **d)** Faux : on peut toujours définir la classe modale, il suffit de comparer les densités au lieu des effectifs.

</details>

Avis : 

---

## 21. `cqc-decomposition-en-facteurs-premiers-faible-0` (séries BAC:A BEPC: PROBATOIRE:C PROBATOIRE:E)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** Décomposition en facteurs premiers : niveau BEPC (examen le plus bas), mais arithmétique absente du programme de la série A au BAC.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Un maraîcher souhaite ranger 504 régimes de bananes dans des caisses contenant chacune le même nombre de régimes, sans qu'il en reste. Pour étudier les rangements possibles, il décompose 504 en produit de facteurs premiers. Quelle est cette décomposition ?

- a) $2^2\times3^2\times7$
- b) $2^3\times3^2\times7$
- c) $2^3\times3\times7$
- d) $2\times3\times7$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour décomposer un entier en produit de facteurs premiers, on le divise successivement par le plus petit nombre premier qui le divise exactement (2, puis 3, puis 5, puis 7...), en répétant l'opération sur chaque quotient obtenu, jusqu'à ce que le quotient soit égal à 1.

### Corrigé

On effectue les divisions successives :

$504 \div 2 = 252$ ; $252 \div 2 = 126$ ; $126 \div 2 = 63$ ; $63 \div 3 = 21$ ; $21 \div 3 = 7$ ; $7 \div 7 = 1$.

On a donc divisé trois fois par 2, deux fois par 3, puis une fois par 7 :
$$504 = 2\times2\times2\times3\times3\times7 = 2^3\times3^2\times7$$

Vérification par multiplication : $2^3=8$, $3^2=9$, donc $8\times9\times7 = 72\times7 = 504$.

### Pourquoi les autres réponses sont fausses

- **a)** Une division par $2$ a été oubliée : ce produit vaut $252$, pas $504$.
- **c)** Une division par $3$ a été oubliée : ce produit vaut $168$, pas $504$.
- **d)** On a écrit chaque facteur premier une seule fois, sans les exposants : ce produit vaut $42$.

</details>

Avis : 

---

## 22. `cqc-rapport-moyenne-2` (séries BEPC: PROBATOIRE:C PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : homothétie de rapport négatif en écriture vectorielle, limite haute pour le BEPC.

**Énoncé :**

Le plan est muni d'un repère $(\Omega\,;\, \vec{i}, \vec{j})$ d'origine $\Omega$. On considère une homothétie $h$ de centre $\Omega$. On donne un point $C$ tel que $\vec{\Omega C} = 3\vec{i} - 3\vec{j}$, et son image $C' = h(C)$ telle que $\vec{\Omega C'} = -\vec{i} + \vec{j}$.

Un point $D$ vérifie $\vec{\Omega D} = -6\vec{i} + 6\vec{j}$. Quel est le vecteur $\vec{\Omega D'}$, où $D' = h(D)$ ?

- a) $\vec{\Omega D'} = -2\vec{i} + 2\vec{j}$
- b) $\vec{\Omega D'} = 2\vec{i} - 2\vec{j}$
- c) $\vec{\Omega D'} = 18\vec{i} - 18\vec{j}$
- d) $\vec{\Omega D'} = -18\vec{i} + 18\vec{j}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Si $h$ est l'homothétie de centre $\Omega$ et de rapport $k$, alors pour tout point $M$ d'image $M'$, on a $\vec{\Omega M'} = k\,\vec{\Omega M}$. Quand les vecteurs sont donnés dans une décomposition sur $\vec{i}, \vec{j}$, le rapport $k$ est le coefficient multiplicateur commun aux deux composantes.

### Corrigé

**Rapport de $h$.** On compare les composantes de $\vec{\Omega C} = 3\vec{i} - 3\vec{j}$ et $\vec{\Omega C'} = -\vec{i} + \vec{j}$ :
$$-1 = k \times 3 \quad\Rightarrow\quad k = -\frac13 \qquad\text{et}\qquad 1 = k \times (-3) \quad\Rightarrow\quad k = -\frac13$$

Les deux composantes donnent la même valeur, donc $k = -\dfrac13$.

**Image de $D$.**
$$\vec{\Omega D'} = k\,\vec{\Omega D} = -\frac13 \times(-6\vec{i} + 6\vec{j}) = 2\vec{i} - 2\vec{j}$$

Contrôle : $\|\vec{\Omega D}\|=6\sqrt2$ et $\|\vec{\Omega D'}\|=2\sqrt2$, soit bien $\dfrac13$ de $6\sqrt2$.

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié le signe du rapport ($k=\dfrac13$ au lieu de $-\dfrac13$) : $C$ et $C'$ sont pourtant de part et d'autre de $\Omega$.
- **c)** On a inversé le quotient ($k=\dfrac{3}{-1}=-3$) en divisant la composante de $\vec{\Omega C}$ par celle de $\vec{\Omega C'}$.
- **d)** Quotient inversé et signe oublié ($k=3$) : on a cumulé les deux erreurs.

</details>

Avis : 

---

## 23. `cqc-translation-faible-1` (séries BAC:C BAC:E BEPC: PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** Les points R et T ne servent à rien ; donnée inutile mais pas trompeuse.

**Énoncé :**

Dans un repère du plan, une translation $t$ transforme le point $M(3;1)$ en son image $M'(0;6)$. Un triangle $RST$ a pour sommets $R(1;0)$, $S(4;-2)$ et $T(2;3)$.

Quelles sont les coordonnées du point $S'$, image de $S$ par la translation $t$ ?

- a) $S'(7;-7)$
- b) $S'(1;5)$
- c) $S'(9;-5)$
- d) $S'(1;3)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Le vecteur d'une translation qui transforme un point connu $M$ en son image connue $M'$ est $\vec u=\overrightarrow{MM'}$, de coordonnées $(x_{M'}-x_M;y_{M'}-y_M)$. Une fois ce vecteur déterminé, l'image de n'importe quel autre point s'obtient en lui ajoutant les mêmes coordonnées. Comme toute translation est une isométrie, l'image du triangle $RST$ lui est superposable.

### Corrigé

Le vecteur de la translation est $\vec u=\overrightarrow{MM'}=(x_{M'}-x_M;y_{M'}-y_M)=(0-3;6-1)=(-3;5)$.

On ajoute ces coordonnées à celles de $S$ :
$$S'=(4+(-3);-2+5)=(1;3).$$

(De même, $R'=(-2;5)$ et $T'=(-1;8)$ ; le triangle $R'S'T'$ est superposable à $RST$, car une translation conserve les longueurs et les angles.)

### Pourquoi les autres réponses sont fausses

- **a)** On a pris le vecteur $\overrightarrow{M'M}=(3;-5)$ au lieu de $\overrightarrow{MM'}$ : on a appliqué la translation réciproque.
- **b)** Erreur de calcul sur la seconde coordonnée du vecteur : $6-1=5$, et non $7$.
- **c)** On a interverti les coordonnées du vecteur, écrit $(5;-3)$ au lieu de $(-3;5)$.

</details>

Avis : 

---

## 24. `cqc-equation-produit-nul-moyenne-0` (séries BAC:A BEPC: PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Énoncé :**

Quel est l'ensemble des solutions dans $\mathbb{R}$ de l'équation suivante ?

$$x(2x+1) - 7(2x+1) = 0$$

- a) $S=\left\{\dfrac{1}{2}\,;\,-7\right\}$
- b) $S=\left\{-\dfrac{1}{2}\,;\,-7\right\}$
- c) $S=\left\{-\dfrac{1}{2}\,;\,7\right\}$
- d) $S=\left\{-2\,;\,7\right\}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Avant d'appliquer la règle du produit nul, il faut parfois factoriser en une seule étape simple : lorsque le même facteur apparaît clairement dans les deux termes d'une expression, on le met en facteur commun pour faire apparaître un produit. On applique ensuite la règle : un produit de facteurs est nul si et seulement si au moins un des facteurs est nul.

### Corrigé

Dans $x(2x+1) - 7(2x+1)$, le facteur $(2x+1)$ apparaît dans les deux termes :
$$x(2x+1) - 7(2x+1) = (2x+1)(x-7)$$

L'équation devient $(2x+1)(x-7)=0$.

**Premier facteur :** $2x+1=0 \Longleftrightarrow 2x=-1 \Longleftrightarrow x=-\dfrac{1}{2}$.

**Second facteur :** $x-7=0 \Longleftrightarrow x=7$.

**Vérification :** pour $x=-\dfrac12$, $2x+1=0$ donc les deux termes sont nuls ; pour $x=7$ : $7\times15 - 7\times15 = 0$.

L'ensemble des solutions est $S=\left\{-\dfrac{1}{2}\,;\,7\right\}$.

### Pourquoi les autres réponses sont fausses

- **a)** On a pris l'opposé de chaque solution ; pour $x=-7$, on obtient $(-13)\times(-14)\neq0$.
- **b)** Erreur de signe en factorisant : on a écrit $(2x+1)(x+7)$ au lieu de $(2x+1)(x-7)$.
- **d)** Division inversée dans $2x=-1$ : $x=-\dfrac12$, et non $-2$.

</details>

Avis : 

---

## 25. `cqc-systeme-lineaire-moyenne-0` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : système 3×3 à la limite haute pour la série A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Résous dans $\mathbb{R}^3$ le système suivant, d'inconnues $x$, $y$ et $z$ :
$$\begin{cases} 3x-2y+z=20 \\ 2x+y-3z=-1 \\ x+4y+2z=-4 \end{cases}$$

On admet que ce système admet une unique solution. Quel est le triplet solution $(x\,;\,y\,;\,z)$ ?

- a) $(4\,;\,3\,;\,2)$
- b) $(2\,;\,-3\,;\,4)$
- c) $(4\,;\,-3\,;\,2)$
- d) $(4\,;\,-4\,;\,2)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour résoudre un système de trois équations à trois inconnues par élimination, on combine les équations deux à deux (en les multipliant par des coefficients bien choisis) afin d'éliminer une même inconnue à chaque fois : on se ramène ainsi à un système de deux équations à deux inconnues, que l'on résout avant de revenir en arrière pour obtenir la dernière inconnue.

### Corrigé

On numérote les équations :
$$\begin{cases} 3x-2y+z=20 & (1) \\ 2x+y-3z=-1 & (2) \\ x+4y+2z=-4 & (3) \end{cases}$$

**Élimination de $y$ entre (1) et (2)** : $(1) + 2\times(2)$ :
$(3x-2y+z) + 2(2x+y-3z) = 20 + 2\times(-1)$
$\Rightarrow 7x - 5z = 18$ (4)

**Élimination de $y$ entre (1) et (3)** : $4\times(1) + 2\times(3)$ :
$4(3x-2y+z) + 2(x+4y+2z) = 4\times20 + 2\times(-4)$
$\Rightarrow 14x+8z=72 \Rightarrow 7x+4z=36$ (5)

**Résolution de (4) et (5)** : $(5)-(4)$ : $9z=18 \Rightarrow z=2$.

Dans (5) : $7x+4\times2=36 \Rightarrow 7x=28 \Rightarrow x=4$.

Dans (1) : $3\times4-2y+2=20 \Rightarrow 14-2y=20 \Rightarrow -2y=6 \Rightarrow y=-3$.

Vérification :
- (1) : $3\times4-2\times(-3)+2=12+6+2=20$ ;
- (2) : $2\times4+(-3)-3\times2=8-3-6=-1$ ;
- (3) : $4+4\times(-3)+2\times2=4-12+4=-4$.

Les trois équations sont vérifiées : $(x\,;\,y\,;\,z) = (4\,;\,-3\,;\,2)$, réponse **c)**.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe à la dernière étape : $14-2y=20$ donne $-2y=6$, donc $y=-3$ et non $y=3$.
- **b)** Les valeurs de $x$ et de $z$ ont été interverties : $3\times2-2\times(-3)+4=16\neq20$.
- **d)** Le terme $z$ a été oublié en revenant dans (1) : $12-2y=20$ donne $y=-4$, alors qu'il fallait $12-2y+2=20$.

</details>

Avis : 

---

## 26. `cqc-aire-moyenne-2` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI BEPC: PROBATOIRE:C PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : pour le BEPC, la formule ½·ab·sin n'est pas au programme ; il faut passer par la hauteur (trigonométrie du triangle rectangle) et connaître sin 60° = √3/2.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans un triangle $RST$, on donne $RS = 8$ cm, $RT = 6$ cm et $\widehat{SRT} = 60°$. Quelle est la valeur exacte de l'aire du triangle $RST$ ?

- a) $12\sqrt3$ cm²
- b) $24\sqrt3$ cm²
- c) $12$ cm²
- d) $24$ cm²

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'on connaît deux côtés d'un triangle et la mesure de l'angle qu'ils forment, on trace la hauteur issue de l'extrémité d'un de ces côtés : dans le triangle rectangle ainsi formé, le sinus de l'angle connu donne la longueur de cette hauteur. L'aire s'obtient ensuite par $\mathcal A = \dfrac{\text{base}\times\text{hauteur}}{2}$.

### Corrigé

Soit $H$ le pied de la hauteur issue de $S$ sur la droite $(RT)$. Le triangle $RHS$ est rectangle en $H$, d'hypoténuse $[RS]$, et l'angle en $R$ mesure $60°$, avec $\sin(60°) = \dfrac{\sqrt3}{2}$ :
$$SH = RS\times\sin(60°) = 8\times\dfrac{\sqrt3}{2} = 4\sqrt3$$

$$\mathcal A = \dfrac{RT\times SH}{2} = \dfrac{6\times4\sqrt3}{2} = 12\sqrt3$$

L'aire exacte du triangle $RST$ est donc $\mathcal A = 12\sqrt3$ cm², soit environ $20{,}78$ cm² (arrondi au centième), réponse **a)**.

### Pourquoi les autres réponses sont fausses

- **b)** La division par $2$ de la formule de l'aire a été oubliée : $6\times4\sqrt3 = 24\sqrt3$.
- **c)** $\sin(60°)$ a été confondu avec $\sin(30°)=\dfrac12$ : la hauteur vaudrait alors $4$ et l'aire $12$.
- **d)** Le triangle a été traité comme s'il était rectangle en $R$ : $\dfrac{8\times6}{2}=24$, sans tenir compte de l'angle de $60°$.

</details>

Avis : 

---

## 27. `cqc-arrangement-moyenne-2` (séries PROBATOIRE:A PROBATOIRE:C PROBATOIRE:E)

**Série(s) retirée(s) par analogie avec vos avis :** PROBATOIRE:A.

**Remarque du relecteur :** LIMITE : dénombrement combinaisons + permutations, à vérifier au programme de Probatoire A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une bibliothécaire souhaite composer une vitrine de présentation avec 3 ouvrages : 2 romans à choisir parmi 6 romans disponibles, et 1 essai à choisir parmi 4 essais disponibles. Les 3 ouvrages retenus seront ensuite placés côte à côte sur une étagère comportant 3 emplacements bien distincts. Combien de vitrines différentes (choix des ouvrages ET ordre sur l'étagère) peut-on composer ?

- a) $60$
- b) $720$
- c) $114$
- d) $360$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'il faut d'abord choisir un ensemble d'éléments sans tenir compte de l'ordre (une combinaison $C_n^p$ pour chaque catégorie disponible), puis disposer les éléments retenus sur des emplacements tous distincts, cette seconde étape est une permutation : $p!$ façons de ranger $p$ éléments sur $p$ emplacements. Le principe multiplicatif relie les deux étapes.

### Corrigé

**Étape 1, choix des ouvrages :**
Choix de 2 romans parmi 6 : $C_6^2 = \dfrac{6!}{2!\,4!} = 15$.
Choix de 1 essai parmi 4 : $C_4^1 = 4$.
Nombre de sélections d'ouvrages : $15 \times 4 = 60$.

**Étape 2, disposition des 3 ouvrages retenus sur les 3 emplacements distincts :** il s'agit d'une permutation des 3 ouvrages choisis :
$$3! = 6$$

**Principe multiplicatif :**
$$60 \times 6 = 360$$

On peut composer **360 vitrines différentes**, réponse **d)**.

### Pourquoi les autres réponses sont fausses

- **a)** L'ordre des ouvrages sur l'étagère a été oublié : $60$ ne compte que les sélections.
- **b)** Les catégories ont été ignorées : $10\times9\times8=720$ range 3 ouvrages quelconques parmi les 10, sans imposer 2 romans et 1 essai.
- **c)** Les choix des romans et de l'essai ont été additionnés au lieu d'être multipliés : $(15+4)\times6=114$.

</details>

Avis : 

---

## 28. `cqc-cone-moyenne-0` (séries BAC:C BEPC:)

**Remarque du relecteur :** VOCABULAIRE : « le tour du mur circulaire » évoque le périmètre, pas le rayon ; écrire plutôt « le cercle formé par le haut du mur circulaire ».

**Énoncé :**

Dans un village, la toiture d'une case traditionnelle a la forme d'un cône de révolution. Le rayon du cercle de base (le tour du mur circulaire sur lequel elle repose) mesure $R = 2{,}5$ m, et la hauteur de cette toiture conique mesure $h = 6$ m.

Quelle est l'aire de la surface de chaume nécessaire pour couvrir entièrement cette toiture (le disque de base n'est pas couvert) ? Le résultat est exprimé en fonction de $\pi$.

- a) $16{,}25\,\pi$ m²
- b) $15\,\pi$ m²
- c) $22{,}5\,\pi$ m²
- d) $32{,}5\,\pi$ m²

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un cône de révolution, le rayon de base $R$, la hauteur $h$ et la génératrice $g$ forment un triangle rectangle : $R$ et $h$ sont les deux côtés de l'angle droit, et $g$ en est l'hypoténuse. Le théorème de Pythagore donne donc $g^2 = R^2+h^2$. Une fois $g$ connue, l'aire latérale du cône s'obtient par $\mathcal{A}_{lat} = \pi R g$.

### Corrigé

D'après le théorème de Pythagore appliqué au triangle rectangle formé par $R$, $h$ et $g$ :
$$g^2 = R^2+h^2 = 2{,}5^2+6^2 = 6{,}25+36 = 42{,}25$$
$$g = \sqrt{42{,}25} = 6{,}5\ \text{m}$$

L'aire de chaume nécessaire est l'aire latérale du cône :
$$\mathcal{A}_{lat} = \pi R g = \pi\times 2{,}5\times 6{,}5 = 16{,}25\,\pi\ \text{m}^2$$

Réponse **a)**.

### Pourquoi les autres réponses sont fausses

- **b)** La hauteur a été utilisée à la place de la génératrice : $\pi\times2{,}5\times6=15\,\pi$.
- **c)** L'aire du disque de base ($6{,}25\,\pi$) a été ajoutée : c'est l'aire totale, alors que la base n'est pas couverte de chaume.
- **d)** La formule a été confondue avec $2\pi R g$ (périmètre de la base multiplié par la génératrice, sans la moitié) : $32{,}5\,\pi$.

</details>

Avis : 

---

## 29. `cqc-decomposition-en-facteurs-premiers-moyenne-2` (séries BAC:A BEPC: PROBATOIRE:C PROBATOIRE:E)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** Le PGCD relève du BEPC (examen le plus bas), mais l'arithmétique est hors programme de la série A au lycée.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une coopérative agricole de l'Ouest-Cameroun dispose de 252 sacs de riz et de 210 sacs de maïs à répartir entre plusieurs entrepôts régionaux, de sorte que chaque entrepôt reçoive exactement le même nombre de sacs de riz et le même nombre de sacs de maïs, sans qu'aucun sac ne reste non réparti. Quel est le nombre maximal d'entrepôts que la coopérative peut approvisionner ainsi, et combien de sacs de chaque sorte recevra alors chaque entrepôt ?

- a) 21 entrepôts ; 12 sacs de riz et 10 sacs de maïs chacun
- b) 42 entrepôts ; 6 sacs de riz et 5 sacs de maïs chacun
- c) 14 entrepôts ; 18 sacs de riz et 15 sacs de maïs chacun
- d) 6 entrepôts ; 42 sacs de riz et 35 sacs de maïs chacun

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Le nombre maximal de lots identiques que l'on peut former à partir de deux quantités correspond au PGCD de ces deux nombres. Pour l'obtenir par décomposition en facteurs premiers, on décompose chaque nombre, puis on multiplie les facteurs premiers communs aux deux décompositions, chacun affecté du plus petit exposant rencontré.

### Corrigé

252 ÷ 2 = 126, 126 ÷ 2 = 63, 63 ÷ 3 = 21, 21 ÷ 3 = 7, 7 ÷ 7 = 1, donc 252 = 2²×3²×7.

210 ÷ 2 = 105, 105 ÷ 3 = 35, 35 ÷ 5 = 7, 7 ÷ 7 = 1, donc 210 = 2×3×5×7.

Facteurs premiers communs aux deux décompositions : 2 (exposant min(2,1)=1), 3 (exposant min(2,1)=1), 7 (exposant min(1,1)=1). Le facteur 5 n'apparaît que dans 210, il n'est pas retenu.

PGCD(252, 210) = 2×3×7 = 42.

La coopérative peut donc approvisionner au maximum 42 entrepôts. Chaque entrepôt reçoit 252 ÷ 42 = 6 sacs de riz et 210 ÷ 42 = 5 sacs de maïs.

Vérification : 42×6 = 252 et 42×5 = 210. Réponse **b)**.

### Pourquoi les autres réponses sont fausses

- **a)** Le facteur commun 2 a été oublié : 21 = 3×7 est un diviseur commun, mais pas le plus grand.
- **c)** Le facteur commun 3 a été oublié : 14 = 2×7 convient pour une répartition, mais n'est pas maximal.
- **d)** Le facteur commun 7 a été oublié : 6 = 2×3 permet une répartition, mais avec beaucoup moins d'entrepôts que possible.

</details>

Avis : 

---

## 30. `cqc-effectifs-faible-0` (séries BAC:A BAC:D BEPC: PROBATOIRE:A PROBATOIRE:C PROBATOIRE:E)

**Remarque du relecteur :** VOCABULAIRE : « entre 14 et 16 ans » gagnerait à préciser « de 14 à 16 ans inclus » pour lever tout doute sur 16 ans.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une équipe de handball intercollèges rassemble 32 joueurs pour un tournoi. Parmi eux, 11 ont moins de 14 ans, 13 ont entre 14 et 16 ans, 4 ont exactement 17 ans, et les autres ont plus de 17 ans. Quelle proportion des joueurs de l'équipe a moins de 17 ans (fraction irréductible) ?

- a) $\dfrac78$
- b) $\dfrac{11}{32}$
- c) $\dfrac67$
- d) $\dfrac34$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand un effectif partiel n'est pas donné directement dans un texte, on le retrouve par soustraction : effectif manquant = effectif total moins la somme des effectifs déjà connus. La proportion (ou fréquence) d'une catégorie est le rapport entre l'effectif de cette catégorie et l'effectif total.

### Corrigé

Effectif total de l'équipe : $32$.

Effectifs connus : moins de 14 ans : $11$ ; entre 14 et 16 ans : $13$ ; exactement 17 ans : $4$. Leur somme est $11+13+4=28$, donc $32-28=4$ joueurs ont plus de 17 ans.

Les joueurs de moins de 17 ans sont ceux de moins de 14 ans et ceux entre 14 et 16 ans (les joueurs d'exactement 17 ans ne sont pas concernés, puisque 17 n'est pas strictement inférieur à 17) :
$$11+13=24$$

La proportion recherchée est donc :
$$f=\dfrac{24}{32}=\dfrac{3}{4}$$

Réponse **d)**.

### Pourquoi les autres réponses sont fausses

- **a)** Les 4 joueurs d'exactement 17 ans ont été comptés : $\dfrac{28}{32}=\dfrac78$.
- **b)** Seuls les joueurs de moins de 14 ans ont été comptés : $\dfrac{11}{32}$.
- **c)** La division a été faite par la somme des effectifs connus ($28$) au lieu de l'effectif total $32$ : $\dfrac{24}{28}=\dfrac67$.

</details>

Avis : 

---

## 31. `cqc-tableau-de-signes-moyenne-3` (séries BAC:A BEPC: PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : produit de trois facteurs affines par tableau de signes, limite haute pour le BEPC (tableaux toutefois fournis).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On donne séparément les deux tableaux de signes suivants, déjà entièrement établis.

Tableau de signes de $A(x) = x+1$ :

| Intervalle | $x<-1$ | $x=-1$ | $x>-1$ |
|---|---|---|---|
| Signe de $A(x)$ | $-$ | $0$ | $+$ |

Tableau de signes de $B(x) = (x-2)(x-4)$, déjà factorisée :

| Intervalle | $x<2$ | $x=2$ | $2<x<4$ | $x=4$ | $x>4$ |
|---|---|---|---|---|---|
| Signe de $B(x)$ | $+$ | $0$ | $-$ | $0$ | $+$ |

On pose $P(x) = A(x)\times B(x)$. Sur quel ensemble a-t-on $P(x)<0$ ?

- a) $]-1\,;\,2[\,\cup\,]4\,;\,+\infty[$
- b) $]2\,;\,4[$
- c) $]-\infty\,;\,-1[\,\cup\,]2\,;\,4[$
- d) $]-\infty\,;\,-1[$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour combiner deux tableaux de signes déjà connus en un tableau du produit, on réunit d'abord tous les points où l'un ou l'autre facteur s'annule, classés dans l'ordre croissant, pour obtenir les bornes des nouveaux intervalles. Sur chacun d'eux, le signe du produit s'obtient en multipliant les signes déjà connus de $A$ et de $B$, sans recalculer aucune racine.

### Corrigé

Les racines de $A$ (en $-1$) et de $B$ (en $2$ et $4$), classées dans l'ordre, donnent quatre intervalles : $x<-1$, $-1<x<2$, $2<x<4$, $x>4$.

**Sur $x<-1$** : $A(x)<0$ et $B(x)>0$ : produit négatif.

**Sur $-1<x<2$** : $A(x)>0$ et $B(x)>0$ : produit positif.

**Sur $2<x<4$** : $A(x)>0$ et $B(x)<0$ : produit négatif.

**Sur $x>4$** : $A(x)>0$ et $B(x)>0$ : produit positif.

En $-1$, $2$ et $4$, le produit est nul.

Vérification par points test : $P(-2)=(-1)\times(-4)\times(-6)=-24<0$ ; $P(0)=1\times(-2)\times(-4)=8>0$ ; $P(3)=4\times1\times(-1)=-4<0$ ; $P(5)=6\times3\times1=18>0$.

| Intervalle | $x<-1$ | $x=-1$ | $-1<x<2$ | $x=2$ | $2<x<4$ | $x=4$ | $x>4$ |
|---|---|---|---|---|---|---|---|
| Signe de $P(x)$ | $-$ | $0$ | $+$ | $0$ | $-$ | $0$ | $+$ |

Donc $P(x)<0$ sur $]-\infty\,;\,-1[\,\cup\,]2\,;\,4[$. Réponse **c)**.

### Pourquoi les autres réponses sont fausses

- **a)** C'est l'ensemble où $P(x)>0$ : les signes ont été inversés.
- **b)** Seul le signe de $B$ a été pris en compte, en oubliant que $A$ est négatif pour $x<-1$.
- **d)** Seul le signe de $A$ a été pris en compte, en oubliant que $B$ est négatif sur $]2\,;\,4[$.

</details>

Avis : 

---

## 32. `cqc-trigonometrie-faible-0` (séries BAC:C BAC:D BEPC: PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Énoncé :**

Dans un triangle $MNP$ rectangle en $N$, l'angle $\widehat{NMP}$ mesure $30°$ et l'hypoténuse $[MP]$ mesure $12$ cm. Quelle est la longueur du côté $[NP]$ ?

- a) $6\sqrt3$ cm
- b) $6$ cm
- c) $24$ cm
- d) $4\sqrt3$ cm

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un triangle rectangle, pour un angle aigu donné, le sinus de cet angle est égal au rapport entre la longueur du côté opposé à l'angle et la longueur de l'hypoténuse : $\sin(\text{angle}) = \dfrac{\text{côté opposé}}{\text{hypoténuse}}$. Connaissant l'angle et l'hypoténuse, on obtient le côté opposé en multipliant l'hypoténuse par le sinus de l'angle.

### Corrigé

Le triangle $MNP$ est rectangle en $N$, donc l'hypoténuse est $[MP]$. Le côté $[NP]$ ne touche pas le sommet $M$ : c'est le côté opposé à l'angle $\widehat{NMP}$.

$$\sin(\widehat{NMP}) = \dfrac{NP}{MP}$$

$30°$ est un angle usuel : $\sin(30°) = \dfrac{1}{2}$. Donc :

$$NP = MP \times \sin(30°) = 12 \times \dfrac{1}{2} = 6$$

La longueur $NP$ mesure $6$ cm. Réponse **b)**.

Contrôle de cohérence : le côté adjacent $MN = MP\cos(30°) = 6\sqrt3 \approx 10{,}39$ cm est plus long que $NP$, ce qui est attendu puisqu'il est opposé au plus grand angle aigu ($60°$ en $P$).

### Pourquoi les autres réponses sont fausses

- **a)** Le cosinus a été utilisé : $12\cos(30°)=6\sqrt3$ est la longueur du côté adjacent $[MN]$.
- **c)** L'hypoténuse a été divisée par le sinus au lieu d'être multipliée : $\dfrac{12}{1/2}=24$, plus long que l'hypoténuse, ce qui est impossible.
- **d)** La tangente a été utilisée avec l'hypoténuse : $12\tan(30°)=4\sqrt3$, alors que la tangente fait intervenir le côté adjacent.

</details>

Avis : 

---

## 33. `cqc-racine-carree-faible-1` (séries BAC:C BAC:E BEPC: PROBATOIRE:C PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : équation irrationnelle au BEPC, à vérifier dans le programme de 3e.

**Énoncé :**

Quel est l'ensemble des solutions dans $\mathbb{R}$ de l'équation $\sqrt{5 - 2x} = 3$ ?

- a) $S=\{1\}$
- b) $S=\{2\}$
- c) $S=\{-7\}$
- d) $S=\{-2\}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Une équation du type $\sqrt{A(x)} = k$, où $k$ est une constante positive, n'a de sens que si $A(x) \geq 0$. On pose cette condition d'existence, on élève les deux membres au carré pour supprimer la racine, on résout l'équation obtenue, puis on vérifie que la solution trouvée respecte la condition posée au départ.

### Corrigé

**Condition d'existence.** Il faut $5 - 2x \geq 0$, soit $x \leq \dfrac{5}{2}$.

**Résolution.** En élevant les deux membres au carré :
$$5 - 2x = 3^2 = 9$$
$$-2x = 4$$
$$x = -2$$

**Vérification.** On a bien $-2 \leq \dfrac{5}{2}$, et $\sqrt{5 - 2 \times (-2)} = \sqrt{9} = 3$.

L'ensemble des solutions est $S = \{-2\}$. Réponse **d)**.

### Pourquoi les autres réponses sont fausses

- **a)** Le membre de droite n'a pas été élevé au carré : $5-2x=3$ donne $x=1$, mais $\sqrt{3}\neq3$.
- **b)** Erreur de signe en divisant par $-2$ : $-2x=4$ donne $x=-2$, pas $2$ ; d'ailleurs $\sqrt{1}=1\neq3$.
- **c)** Le $5$ a été changé de membre sans changer de signe : $-2x=9+5$ ; or $\sqrt{19}\neq3$.

</details>

Avis : 

---

## 34. `cqc-systeme-lineaire-moyenne-1` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : système 3x3 pour les séries A, calcul lourd mais faisable par pivot de Gauss ou par vérification des choix.

**Énoncé :**

Trois réels $a$, $b$ et $c$ vérifient simultanément les trois égalités suivantes :
$$\begin{cases} 2a+3b-4c=4 \\ 3a-2b+5c=8 \\ 4a+5b-2c=4 \end{cases}$$

Quel est le triplet $(a\,;\,b\,;\,c)$ solution de ce système ?

- a) $(-11\,;\,10\,;\,1)$
- b) $(7\,;\,-2\,;\,-1)$
- c) $(-3\,;\,-2\,;\,-1)$
- d) $(3\,;\,-2\,;\,-1)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'aucune inconnue n'a un coefficient égal à $1$ (ou $-1$) dans une équation, une substitution directe n'est pas immédiate : on combine alors les équations deux à deux, en les multipliant chacune par un coefficient choisi pour faire disparaître une même inconnue, jusqu'à obtenir un système de deux équations plus simple à résoudre. On vérifie toujours le triplet trouvé dans les trois équations.

### Corrigé

On numérote les équations :
$$\begin{cases} 2a+3b-4c=4 & (1) \\ 3a-2b+5c=8 & (2) \\ 4a+5b-2c=4 & (3) \end{cases}$$

**Élimination de $a$ entre (1) et (2)** : $3\times(1) - 2\times(2)$ :
$3(2a+3b-4c) - 2(3a-2b+5c) = 3\times4-2\times8$
$\Rightarrow 6a+9b-12c-6a+4b-10c = -4$
$\Rightarrow 13b-22c=-4$ (4)

**Élimination de $a$ entre (1) et (3)** : $2\times(1) - (3)$ :
$2(2a+3b-4c) - (4a+5b-2c) = 2\times4-4$
$\Rightarrow 4a+6b-8c-4a-5b+2c = 4$
$\Rightarrow b-6c=4$ (5)

**Résolution de (4) et (5)** : de (5), $b=4+6c$. En remplaçant dans (4) :
$13(4+6c)-22c=-4 \Rightarrow 52+78c-22c=-4 \Rightarrow 56c=-56 \Rightarrow c=-1$.

Donc $b=4+6\times(-1)=-2$.

Dans (1) : $2a+3\times(-2)-4\times(-1)=4 \Rightarrow 2a-6+4=4 \Rightarrow 2a=6 \Rightarrow a=3$.

Vérification :
- (1) : $2\times3+3\times(-2)-4\times(-1)=6-6+4=4$ ;
- (2) : $3\times3-2\times(-2)+5\times(-1)=9+4-5=8$ ;
- (3) : $4\times3+5\times(-2)-2\times(-1)=12-10+2=4$.

$$\boxed{a=3\,;\ b=-2\,;\ c=-1}$$

La bonne réponse est **d)**.

### Pourquoi les autres réponses sont fausses

- **a)** $(-11\,;\,10\,;\,1)$ : erreur de signe en passant $52$ dans l'autre membre ($56c=56$ au lieu de $56c=-56$), d'où $c=1$, puis $b$ et $a$ faux ; la vérification dans (2) échoue.
- **b)** $(7\,;\,-2\,;\,-1)$ : erreur de signe dans le calcul de $-4\times(-1)$, compté $-4$ au lieu de $+4$ dans l'équation (1).
- **c)** $(-3\,;\,-2\,;\,-1)$ : erreur de signe dans le calcul de $3\times(-2)$, compté $+6$ au lieu de $-6$ dans l'équation (1).

</details>

Avis : 

---

## 35. `cqc-angle-inscrit-elevee-0` (séries BEPC: PROBATOIRE:C PROBATOIRE:E)

**Remarque du relecteur :** VW = 12 cm est une donnée inutile mais sans piège.

**Énoncé :**

Soit $(\Gamma)$ un cercle de centre $O$ et de diamètre $[VW]$, avec $VW = 12$ cm. Soit $X$ un point de $(\Gamma)$, distinct de $V$ et de $W$, tel que l'angle $\widehat{XVW}$ mesure $30°$. Soit $Y$ le point de $(\Gamma)$ diamétralement opposé à $X$, c'est-à-dire que $O$ est le milieu de $[XY]$.

Quelle est la mesure de l'angle inscrit $\widehat{YVW}$ ?

- a) $30°$
- b) $120°$
- c) $60°$
- d) $90°$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Un angle au centre mesure le double de l'angle inscrit qui intercepte le même arc. Lorsque deux angles de sommet $O$ ont un côté commun et que leurs deux autres côtés sont des demi-droites opposées, ces deux angles sont supplémentaires (leur somme vaut $180°$).

### Corrigé

**Angle au centre $\widehat{XOW}$.** Les angles $\widehat{XOW}$ (au centre) et $\widehat{XVW}$ (inscrit) interceptent le même arc $\overset{\frown}{XW}$ (celui ne contenant pas $V$), donc :
$$\widehat{XOW} = 2 \times \widehat{XVW} = 2 \times 30° = 60°$$

**Angle au centre $\widehat{YOW}$.** $O$ est le milieu de $[XY]$, donc les points $X$, $O$, $Y$ sont alignés et les demi-droites $[OX)$ et $[OY)$ sont opposées : les angles $\widehat{XOW}$ et $\widehat{YOW}$ sont supplémentaires.
$$\widehat{YOW} = 180° - \widehat{XOW} = 180° - 60° = 120°$$

**Angle inscrit $\widehat{YVW}$.** Les angles $\widehat{YOW}$ (au centre) et $\widehat{YVW}$ (inscrit) interceptent le même arc $\overset{\frown}{YW}$ (celui ne contenant pas $V$), donc :
$$\widehat{YVW} = \frac{\widehat{YOW}}{2} = \frac{120°}{2} = 60°$$

La bonne réponse est **c)**.

### Pourquoi les autres réponses sont fausses

- **a)** $30°$ : confusion avec l'angle $\widehat{XVW}$ donné dans l'énoncé, alors que $\widehat{YVW}$ intercepte un autre arc.
- **b)** $120°$ : c'est l'angle au centre $\widehat{YOW}$ ; on a oublié de le diviser par $2$ pour obtenir l'angle inscrit.
- **d)** $90°$ : on applique à tort la propriété de l'angle inscrit dans un demi-cercle, alors que $[YW]$ n'est pas un diamètre.

</details>

Avis : 

---

## 36. `cqc-coefficient-directeur-faible-1` (séries BAC:D BEPC: PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une droite du plan a pour équation $3x + 6y - 12 = 0$. Quel est le coefficient directeur de cette droite ?

- a) $-\dfrac12$
- b) $\dfrac12$
- c) $2$
- d) $-2$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand une droite est donnée par une équation de la forme $ax+by+c=0$ avec $b \neq 0$, on isole $y$ pour faire apparaître le coefficient qui multiplie $x$ : c'est ce nombre-là, et lui seul, qui est le coefficient directeur cherché.

### Corrigé

$3x + 6y - 12 = 0$

$6y = -3x + 12$

$y = -\dfrac{3}{6}x + \dfrac{12}{6} = -\dfrac12 x + 2$

Le nombre qui multiplie $x$ est $-\dfrac12$. Le coefficient directeur de cette droite est donc $m = -\dfrac12$.

La bonne réponse est **a)**.

### Pourquoi les autres réponses sont fausses

- **b)** $\dfrac12$ : oubli du changement de signe en faisant passer $3x$ dans l'autre membre.
- **c)** $2$ : c'est l'ordonnée à l'origine, pas le coefficient directeur.
- **d)** $-2$ : rapport inversé, on a calculé $-\dfrac{6}{3}$ au lieu de $-\dfrac{3}{6}$.

</details>

Avis : 

---

## 37. `cqc-decomposition-en-facteurs-premiers-moyenne-4` (séries BAC:A BEPC: PROBATOIRE:C PROBATOIRE:E)

**Énoncé :**

Deux lignes de bus quittent en même temps la gare routière centrale de Bafoussam. Le bus de la ligne 1 revient à la gare toutes les 36 minutes, celui de la ligne 2 toutes les 48 minutes. Après combien de minutes les deux bus se retrouveront-ils à nouveau ensemble à la gare pour la première fois ?

- a) 12 min
- b) 84 min
- c) 144 min
- d) $1\,728$ min

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Le plus petit intervalle de temps au bout duquel deux évènements périodiques coïncident à nouveau correspond au PPCM de leurs deux périodes. Pour l'obtenir par décomposition en facteurs premiers, on décompose chaque nombre, puis on multiplie tous les facteurs premiers apparus dans l'une ou l'autre décomposition, chacun affecté du plus grand exposant rencontré.

### Corrigé

$36 = 2^2\times3^2$ et $48 = 2^4\times3$.

Facteurs premiers en jeu : $2$ (exposant le plus grand : $4$) et $3$ (exposant le plus grand : $2$).

$$\text{PPCM}(36\,;48) = 2^4\times3^2 = 16\times9 = 144$$

Les deux bus se retrouveront donc ensemble à la gare 144 minutes après leur départ, soit 2 heures 24 minutes.

Vérification : $144 = 4\times36$ et $144 = 3\times48$.

La bonne réponse est **c)**.

### Pourquoi les autres réponses sont fausses

- **a)** 12 min : c'est le PGCD de 36 et 48 (facteurs communs avec le plus petit exposant), qui n'est un multiple d'aucune des deux périodes.
- **b)** 84 min : on a additionné les deux périodes ; or $84$ n'est un multiple ni de $36$ ni de $48$.
- **d)** $1\,728$ min : c'est le produit $36\times48$, un multiple commun mais pas le plus petit.

</details>

Avis : 

---

## 38. `cqc-mode-elevee-0` (séries BEPC: PROBATOIRE:A PROBATOIRE:D)

**Remarque du relecteur :** Énoncé long ; l'effectif illisible n n'est pas nécessaire (seul le total 30 compte).

**Énoncé :**

Un club sportif a organisé un tournoi de tennis de table réparti en deux groupes, le groupe Nord et le groupe Sud. Dans le groupe Nord, 30 joueurs ont disputé un nombre de matchs variable au cours du week-end ; les résultats sont donnés dans le tableau suivant, où l'effectif d'une des valeurs a été rendu illisible par une tache d'encre :

| Nombre de matchs joués $x_i$ | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Nombre de joueurs $n_i$ | 4 | $n$ | 10 | 6 | 2 |

Dans le groupe Sud, qui compte 20 joueurs, la valeur la plus fréquente du nombre de matchs joués est également 3, avec un effectif de 9 joueurs.

Dans lequel des deux groupes le mode (3 matchs) concerne-t-il la plus grande part des joueurs ? Les pourcentages sont arrondis au dixième.

- a) Le groupe Nord, car $10$ joueurs sont concernés contre $9$ dans le groupe Sud.
- b) Le groupe Sud : $45\,\%$ des joueurs contre environ $33{,}3\,\%$ dans le groupe Nord.
- c) Le groupe Nord : environ $45{,}5\,\%$ des joueurs contre $45\,\%$ dans le groupe Sud.
- d) Le groupe Nord : $50\,\%$ des joueurs contre $30\,\%$ dans le groupe Sud.

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand l'effectif d'une valeur est inconnu mais que l'effectif total de la série est donné, on le retrouve par soustraction : effectif manquant = effectif total moins la somme des effectifs connus. Pour comparer le poids du mode dans deux groupes dont les effectifs totaux diffèrent, comparer directement les effectifs bruts ne suffit pas : il faut calculer la **fréquence** du mode dans chaque groupe (effectif du mode divisé par l'effectif total du groupe).

### Corrigé

**Mode du groupe Nord.** La somme des effectifs connus est $4+10+6+2=22$, donc $n=30-22=8$. Les effectifs complets sont $4,\,8,\,10,\,6,\,2$ : le plus grand est $10$, atteint pour $x=3$. Le mode du groupe Nord est bien 3 matchs.

**Fréquences du mode** (arrondies au dixième de pourcentage) :
- groupe Nord : $\dfrac{10}{30}=\dfrac13\approx 33{,}3\,\%$ ;
- groupe Sud : $\dfrac{9}{20}=0{,}45=45\,\%$.

Puisque $45\,\%>33{,}3\,\%$, le mode concerne proportionnellement plus de joueurs dans le groupe Sud, bien que son effectif brut y soit inférieur ($9$ contre $10$).

La bonne réponse est **b)**.

### Pourquoi les autres réponses sont fausses

- **a)** On compare les effectifs bruts ($10>9$) sans tenir compte des tailles différentes des deux groupes.
- **c)** On a divisé $10$ par $22$, la somme des effectifs lisibles, en oubliant l'effectif manquant $n=8$.
- **d)** Les effectifs totaux ont été intervertis : $\dfrac{10}{20}$ et $\dfrac{9}{30}$ au lieu de $\dfrac{10}{30}$ et $\dfrac{9}{20}$.

</details>

Avis : 

---

## 39. `cqc-moyenne-ponderee-elevee-0` (séries BAC:A BEPC: PROBATOIRE:A PROBATOIRE:C PROBATOIRE:E)

**Remarque du relecteur :** Le choix a (26) est la valeur de n, piège voulu ; la question demande bien l'effectif total.

**Énoncé :**

Une coopérative agricole a recensé la production mensuelle de cacao, en tonnes, de ses plantations affiliées. Les résultats sont regroupés en classes dans le tableau suivant, où l'effectif d'une des classes a été effacé :

| Production (tonnes) | [2,4[ | [4,6[ | [6,8[ | [8,10[ |
|---|---|---|---|---|
| Nombre de plantations $n_i$ | 6 | $n$ | 14 | 10 |

On sait que la production moyenne de cette série, calculée à partir des centres de classes, vaut exactement $\bar x = 6$ tonnes. Quel est l'effectif total de plantations recensées ?

- a) 26
- b) 30
- c) 336
- d) 56

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand l'effectif d'une classe est inconnu, on exprime l'effectif total $N$ et la somme pondérée $\sum n_ic_i$ en fonction de cette inconnue $n$, à partir des centres de classes, puis on résout l'équation $\bar x=\dfrac{\sum n_ic_i}{N}$ donnée par l'énoncé pour déterminer $n$, et enfin $N$.

### Corrigé

Les centres de classes sont $c_i=3,\,5,\,7,\,9$.

L'effectif total, en fonction de $n$, est $N=6+n+14+10=30+n$.

La somme pondérée, en fonction de $n$, est :
$$\sum n_ic_i = 6\times3+n\times5+14\times7+10\times9=18+5n+98+90=206+5n$$

On sait que $\bar x=6$, donc :
$$\frac{206+5n}{30+n}=6$$

En multipliant les deux membres par $(30+n)$, strictement positif :
$$206+5n=180+6n \quad\text{d'où}\quad n=26$$

L'effectif total est donc $N=30+26=56$.

**Vérification :** $\sum n_ic_i=206+5\times26=336$ et $\dfrac{336}{56}=6$.

La bonne réponse est **d)**.

### Pourquoi les autres réponses sont fausses

- **a)** 26 : c'est l'effectif manquant $n$, pas l'effectif total.
- **b)** 30 : on a additionné les seuls effectifs lisibles, en oubliant l'effectif manquant.
- **c)** 336 : c'est la somme pondérée $\sum n_ic_i$, confondue avec l'effectif total.

</details>

Avis : 

---

## 40. `cqc-perimetre-elevee-0` (séries BAC:A BEPC: PROBATOIRE:A PROBATOIRE:D)

**Remarque du relecteur :** Tous les choix désignent Monsieur Kamdem : la première partie de la question ne discrimine pas.

**Énoncé :**

Dans le département du Ndé (région de l'Ouest), deux exploitants agricoles doivent clôturer leur terrain avant la saison sèche.
- Le terrain de Monsieur Kamdem est rectangulaire, de $84$ m de longueur sur $56$ m de largeur.
- Le terrain de Madame Njoya est carré ; son côté mesure les trois quarts de la longueur du terrain de Monsieur Kamdem.

Pour chaque terrain, la clôture est composée d'un grillage, facturé $1250$ FCFA le mètre, et de poteaux plantés tous les $4$ m tout autour, facturés $3500$ FCFA le poteau (matériau et pose compris).

Lequel des deux terrains coûte le plus cher à clôturer, et de combien ?

- a) Le terrain de Monsieur Kamdem, de $59\,500$ FCFA
- b) Le terrain de Monsieur Kamdem, de $35\,000$ FCFA
- c) Le terrain de Monsieur Kamdem, de $238\,000$ FCFA
- d) Le terrain de Monsieur Kamdem, de $24\,500$ FCFA

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour comparer le coût de deux clôtures, on calcule d'abord le périmètre de chaque terrain, puis le nombre de poteaux nécessaires (le périmètre divisé par l'espacement, sans ajouter $1$ puisque le contour est fermé), avant de multiplier chaque quantité par son prix unitaire et d'additionner les deux postes de dépense.

### Corrigé

**Terrain de Monsieur Kamdem** (rectangle $84$ m $\times$ $56$ m) :
$$P_1 = 2\times(84+56) = 2\times 140 = 280\ \text{m}$$

Coût du grillage : $280\times 1250 = 350\,000$ FCFA.
Nombre de poteaux : $\dfrac{280}{4}=70$, soit $70\times 3500=245\,000$ FCFA.
Coût total : $350\,000+245\,000=595\,000$ FCFA.

**Terrain de Madame Njoya** (carré) :
Côté : $\dfrac{3}{4}\times 84 = 63$ m. Périmètre :
$$P_2 = 4\times 63 = 252\ \text{m}$$

Coût du grillage : $252\times 1250 = 315\,000$ FCFA.
Nombre de poteaux : $\dfrac{252}{4}=63$, soit $63\times 3500=220\,500$ FCFA.
Coût total : $315\,000+220\,500=535\,500$ FCFA.

**Comparaison** : le terrain de Monsieur Kamdem coûte plus cher à clôturer, avec un écart de :
$$595\,000-535\,500=59\,500\ \text{FCFA}$$

La bonne réponse est **a)**.

### Pourquoi les autres réponses sont fausses

- **b)** $35\,000$ FCFA : seul le grillage a été comparé, le coût des poteaux a été oublié.
- **c)** $238\,000$ FCFA : le côté du carré a été pris égal aux trois quarts de la largeur ($42$ m) au lieu de la longueur.
- **d)** $24\,500$ FCFA : seuls les poteaux ont été comparés, le coût du grillage a été oublié.

</details>

Avis : 

---

## 41. `cqc-equation-du-second-degre-faible-1` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI BEPC: PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Quel est l'ensemble des solutions dans $\mathbb{R}$ de l'équation $(E) : x^2 + 10x + 25 = 0$ ?

- a) $S=\{5\}$
- b) $S=\{-5\,;\,5\}$
- c) $S=\{-5\}$
- d) $S=\varnothing$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Avant tout calcul, on regarde si le premier membre est une identité remarquable : $a^2+2ab+b^2=(a+b)^2$. Un carré est nul si et seulement si le nombre élevé au carré est nul.

### Corrigé

On reconnaît $x^2+10x+25 = x^2+2\times x\times5+5^2 = (x+5)^2$.

L'équation s'écrit donc $(x+5)^2=0$, ce qui équivaut à $x+5=0$, soit $x=-5$.

Vérification : $(-5)^2+10\times(-5)+25 = 25-50+25=0$.

$S = \{-5\}$

La bonne réponse est **c)**.

### Pourquoi les autres réponses sont fausses

- **a)** $S=\{5\}$ : erreur de signe en résolvant $x+5=0$ (ou en factorisant en $(x-5)^2$).
- **b)** $S=\{-5\,;\,5\}$ : confusion avec $x^2-25=0$ ; on a cru qu'un carré nul donnait deux solutions opposées.
- **d)** $S=\varnothing$ : on a cru que la somme de trois termes à coefficients positifs ne pouvait pas s'annuler, en oubliant que $x$ peut être négatif.

</details>

Avis : 

---

## 42. `cqc-systeme-lineaire-moyenne-2` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : discussion d'un système paramétré, haute pour la série A.

**Énoncé :**

On considère le système d'inconnues réelles $x$ et $y$, où $m$ désigne un paramètre réel :
$$\begin{cases} mx + 2y = m+1 \\ 4x + (m-2)y = 5 \end{cases}$$

Pour quelle(s) valeur(s) de $m$ ce système n'admet-il aucune solution ?

- a) $m=-2$
- b) $m=4$
- c) $m=-2$ ou $m=4$
- d) $m=-4$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour un système linéaire de deux équations à deux inconnues $\begin{cases}ax+by=e\\cx+dy=f\end{cases}$, on calcule le déterminant $D=ad-bc$. Si $D\neq0$, le système admet une unique solution, donnée par les formules de Cramer. Si $D=0$, les deux équations représentent des droites parallèles : il faut alors comparer directement les deux équations pour distinguer le cas où elles sont confondues (infinité de solutions) du cas où elles sont strictement parallèles et distinctes (aucune solution).

### Corrigé

Le déterminant du système est :
$$D(m) = m(m-2) - 2\times4 = m^2-2m-8.$$

Ce trinôme a pour discriminant $\Delta = (-2)^2-4\times1\times(-8) = 4+32=36=6^2$, donc ses racines sont $m=\dfrac{2-6}{2}=-2$ et $m=\dfrac{2+6}{2}=4$. Ainsi $D(m)=(m-4)(m+2)$.

**Cas où $m\neq4$ et $m\neq-2$.** Alors $D(m)\neq0$ : le système admet une unique solution, $\left(\dfrac{m+3}{m+2}\,;\,\dfrac{1}{m+2}\right)$ (formules de Cramer, avec $D_x=(m-4)(m+3)$ et $D_y=m-4$).

**Cas $m=4$.** Les deux équations deviennent $4x+2y=5$ et $4x+2y=5$ : c'est la même droite. Le système admet donc une infinité de solutions.

**Cas $m=-2$.** Les deux équations deviennent $-2x+2y=-1$ et $4x-4y=5$. En multipliant la première par $-2$, on obtient $4x-4y=2$, ce qui contredit la seconde équation ($4x-4y=5$) : les deux droites sont strictement parallèles et distinctes. Le système n'admet donc aucune solution.

Le système n'admet aucune solution pour $m=-2$ seulement.

### Pourquoi les autres réponses sont fausses

- **b)** pour $m=4$ les deux équations sont identiques : le système admet une infinité de solutions, pas aucune.
- **c)** annuler le déterminant ne suffit pas : il faut ensuite distinguer droites confondues ($m=4$) et strictement parallèles ($m=-2$).
- **d)** erreur de signe dans la recherche des racines de $m^2-2m-8$ (on obtient celles de $m^2+2m-8$) ; pour $m=-4$, $D=16\neq0$ et la solution est unique.

</details>

Avis : 

---

## 43. `cqc-coordonnees-faible-0` (séries BAC:C BAC:D BAC:E BEPC: PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Énoncé :**

Le plan est muni d'un repère orthonormé $(O;\vec\imath,\vec\jmath)$. On donne les points $A(5;-3)$ et $B(-2;4)$. Quelles sont les coordonnées du vecteur $\overrightarrow{AB}$ ?

- a) $(7\,;\,-7)$
- b) $(3\,;\,1)$
- c) $(-7\,;\,1)$
- d) $(-7\,;\,7)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Si $A(x_A;y_A)$ et $B(x_B;y_B)$ sont deux points du plan, les coordonnées du vecteur $\overrightarrow{AB}$ s'obtiennent en retranchant les coordonnées de l'origine $A$ à celles de l'extrémité $B$ : $\overrightarrow{AB}(x_B-x_A;y_B-y_A)$.

### Corrigé
$x_{\overrightarrow{AB}}=x_B-x_A=-2-5=-7$.

$y_{\overrightarrow{AB}}=y_B-y_A=4-(-3)=7$.

Donc $\overrightarrow{AB}(-7;7)$.

### Pourquoi les autres réponses sont fausses

- **a)** on a calculé $x_A-x_B$ et $y_A-y_B$ : ce sont les coordonnées de $\overrightarrow{BA}$.
- **b)** on a additionné les coordonnées de $A$ et de $B$ au lieu de les soustraire.
- **c)** erreur de signe sur l'ordonnée : $4-(-3)=7$ et non $4-3=1$.

</details>

Avis : 

---

## 44. `cqc-moyenne-ponderee-faible-0` (séries BAC:A BEPC: PROBATOIRE:A PROBATOIRE:C PROBATOIRE:E)

**Remarque du relecteur :** VOCABULAIRE : « poids (kg) » désigne une masse ; préférer « masse ».

**Énoncé :**

Un bureau de poste a pesé, en kg, les 40 colis reçus au cours d'une matinée. Les résultats sont regroupés dans le tableau suivant, où chaque colis est classé selon son poids :

| Poids (kg) | [0,2[ | [2,4[ | [4,6[ | [6,8[ | [8,10[ |
|---|---|---|---|---|---|
| Nombre de colis $n_i$ | 10 | 18 | 9 | 2 | 1 |

Quel est le poids moyen $\bar x$ d'un colis ?

- a) $2{,}3$ kg
- b) $3{,}3$ kg
- c) $4{,}3$ kg
- d) $26{,}4$ kg

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour une série statistique groupée en classes, chaque classe $[a\,;b[$ est représentée par son centre $c=\dfrac{a+b}{2}$. La moyenne pondérée s'obtient alors en multipliant chaque centre par l'effectif de sa classe, en additionnant ces produits, puis en divisant par l'effectif total : $\bar x=\dfrac{\sum n_ic_i}{\sum n_i}$.

### Corrigé
Les centres de classes sont $c_i=1,\,3,\,5,\,7,\,9$ (par exemple $\dfrac{0+2}{2}=1$ pour la première classe).

L'effectif total est $N=10+18+9+2+1=40$.

La somme pondérée est :
$$\sum n_ic_i = 10\times1+18\times3+9\times5+2\times7+1\times9=10+54+45+14+9=132$$

Donc $\bar x=\dfrac{132}{40}=3{,}3$ kg.

Le poids moyen d'un colis est de **3,3 kg**.

### Pourquoi les autres réponses sont fausses

- **a)** on a représenté chaque classe par sa borne inférieure au lieu de son centre ($\dfrac{92}{40}$).
- **c)** on a représenté chaque classe par sa borne supérieure au lieu de son centre ($\dfrac{172}{40}$).
- **d)** on a divisé la somme $132$ par le nombre de classes ($5$) au lieu de l'effectif total ($40$).

</details>

Avis : 

---

## 45. `cqc-mediane-moyenne-2` (séries BAC:A BEPC: PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : médiane par interpolation linéaire sur classes, à la limite haute du BEPC.

**Énoncé :**

Un concessionnaire automobile a relevé le kilométrage parcouru, en milliers de kilomètres, par chacun des 90 véhicules d'occasion actuellement en vente. Voici la répartition obtenue, regroupée en classes :

| Classe (milliers de km) | [0;20[ | [20;40[ | [40;60[ | [60;80[ | [80;100] |
|---|---|---|---|---|---|
| Effectif | 8 | 22 | 30 | 20 | 10 |

Quelle est la médiane de cette série, obtenue par interpolation linéaire ?

- a) $45$ milliers de km
- b) $55$ milliers de km
- c) $50$ milliers de km
- d) $40$ milliers de km

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une série groupée en classes, on peut retrouver la médiane sans tracer les polygones des effectifs cumulés : on repère, à l'aide des effectifs cumulés croissants (ECC), la classe où le cumul dépasse $\dfrac{N}{2}$, puis on interpole linéairement à l'intérieur de cette seule classe.

### Corrigé

Effectif total : $N = 8+22+30+20+10 = 90$, donc $\dfrac{N}{2} = 45$.

Effectifs cumulés croissants :

| Classe | [0;20[ | [20;40[ | [40;60[ | [60;80[ | [80;100] |
|---|---|---|---|---|---|
| Effectif | 8 | 22 | 30 | 20 | 10 |
| ECC | 8 | 30 | 60 | 80 | 90 |

Le cumul $45$ n'est pas atteint à la fin de la classe [20;40[ (ECC $30$) ; il est dépassé dans la classe [40;60[, où l'ECC passe de $30$ à $60$. C'est la classe médiane.

Interpolation linéaire dans cette classe, de largeur $20$ :

$$\mathrm{Me} = 40 + \dfrac{45-30}{60-30}\times 20 = 40 + \dfrac{15}{30}\times 20 = 40+10 = 50$$

La médiane de cette série est $\mathrm{Me} = 50$ milliers de kilomètres, soit $50\,000$ km.

### Pourquoi les autres réponses sont fausses

- **a)** $45$ est le rang $\dfrac{N}{2}$, un nombre de véhicules, pas un kilométrage.
- **b)** on a interpolé avec $\dfrac{45}{60}$ au lieu de $\dfrac{45-30}{60-30}$ : l'ECC de début de classe ($30$) a été oublié.
- **d)** c'est la borne inférieure de la classe médiane : l'interpolation n'a pas été faite.

</details>

Avis : 

---

## 46. `cqc-theoreme-de-thales-faible-0` (séries BEPC: PROBATOIRE:C PROBATOIRE:E)

**Énoncé :**

Dans le plan, on considère un point $I$ et deux droites sécantes en $I$. Sur la première droite, on place, dans cet ordre à partir de $I$, les points $I$, $J$ puis $K$. Sur la seconde droite, on place, dans cet ordre à partir de $I$, les points $I$, $L$ puis $M$. Les droites $(JL)$ et $(KM)$ sont parallèles. On donne : $IJ = 4$ cm, $IK = 10$ cm et $IL = 6$ cm.

Quelle est la longueur $IM$ ?

- a) $2{,}4$ cm
- b) $15$ cm
- c) $12$ cm
- d) $\dfrac{20}{3}$ cm

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsque deux droites sécantes en un point sont coupées par deux droites parallèles, les longueurs portées sur chaque sécante à partir du sommet commun sont proportionnelles : c'est le théorème de Thalès.

### Corrigé

Les droites $(IJK)$ et $(ILM)$ sont sécantes en $I$, et $(JL) \parallel (KM)$, donc, d'après le théorème de Thalès appliqué au sommet $I$ :
$$\frac{IJ}{IK} = \frac{IL}{IM}$$
$$\frac{4}{10} = \frac{6}{IM}$$

Par produit en croix :
$$4 \times IM = 10 \times 6 = 60$$
$$IM = \frac{60}{4} = 15 \text{ cm}$$

### Pourquoi les autres réponses sont fausses

- **a)** rapports mal appariés : on a écrit $\dfrac{IJ}{IK}=\dfrac{IM}{IL}$, ce qui donne une longueur $IM$ plus petite que $IL$, impossible puisque $L$ est entre $I$ et $M$.
- **c)** on a raisonné par différences ($IM=IL+(IK-IJ)$) : Thalès donne une proportionnalité, pas une égalité d'écarts.
- **d)** on a écrit $\dfrac{IJ}{IL}=\dfrac{IM}{IK}$, en mélangeant les longueurs des deux droites.

</details>

Avis : 

---

## 47. `cqc-aire-d-un-trapeze-faible-0` (séries BEPC: PROBATOIRE:D)

**Énoncé :**

$ABCD$ est un trapèze dont les côtés $[AB]$ et $[DC]$ sont parallèles. La grande base $AB$ mesure $14$ cm et la petite base $DC$ mesure $8$ cm. La hauteur du trapèze, c'est-à-dire la distance entre les droites $(AB)$ et $(DC)$, mesure $6$ cm.

Quelle est l'aire du trapèze $ABCD$ ?

- a) $132$ cm²
- b) $66$ cm²
- c) $42$ cm²
- d) $18$ cm²

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

L'aire d'un trapèze de grande base $B$, de petite base $b$ et de hauteur $h$ se calcule par la formule $\mathcal{A} = \dfrac{(B+b)\times h}{2}$, où $h$ désigne la distance entre les deux bases parallèles.

### Corrigé

Ici, $B = 14$ cm, $b = 8$ cm et $h = 6$ cm.

$\mathcal{A} = \dfrac{(14+8)\times 6}{2} = \dfrac{22\times 6}{2} = \dfrac{132}{2} = 66$

L'aire du trapèze $ABCD$ est donc $66$ cm².

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié de diviser par $2$ : $(14+8)\times 6 = 132$.
- **c)** On n'a pris que la grande base, comme pour un triangle : $\dfrac{14\times 6}{2} = 42$.
- **d)** On a soustrait les bases au lieu de les additionner : $\dfrac{(14-8)\times 6}{2} = 18$.

</details>

Avis : 

---

## 48. `cqc-centre-de-symetrie-faible-1` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI BEPC: PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** Le centre I est nommé mais inutile ; donnée superflue sans risque réel de tromper.

**Énoncé :**

Le plan est muni d'un repère. $ABCD$ est un parallélogramme de centre $I$. On donne les coordonnées $A(-2;3)$, $B(1;6)$ et $C(6;-1)$.

Quelles sont les coordonnées du point $D$ ?

- a) $D(9;2)$
- b) $D(1;-5)$
- c) $D(0;11)$
- d) $D(3;-4)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un parallélogramme, le centre de symétrie est le point d'intersection des diagonales, qui est aussi leur milieu commun. Le symétrique $M'$ d'un point $M$ par rapport à un centre $I$ vérifie la relation vectorielle $\overrightarrow{IM'}=-\overrightarrow{IM}$, ce qui permet de calculer les coordonnées de $M'$ à partir de celles de $I$ et de $M$.

### Corrigé

**Centre $I$.** $ABCD$ est un parallélogramme, donc ses diagonales $[AC]$ et $[BD]$ se coupent en leur milieu commun, le centre $I$. $I$ est le milieu de $[AC]$ :
$I\left(\dfrac{-2+6}{2};\dfrac{3+(-1)}{2}\right) = I(2;1)$.

**Point $D$.** $D$ est le symétrique de $B$ par rapport à $I$.
$\overrightarrow{IB}=(1-2;6-1)=(-1;5)$, donc $\overrightarrow{ID}=-\overrightarrow{IB}=(1;-5)$.
Donc $D = (2+1;1-5) = (3;-4)$.

**Vérification.** Milieu de $[BD]$ : $\left(\dfrac{1+3}{2};\dfrac{6+(-4)}{2}\right)=(2;1)=I$. On a aussi $\overrightarrow{AB}=(3;3)$ et $\overrightarrow{DC}=(6-3;-1+4)=(3;3)$ : $\overrightarrow{AB}=\overrightarrow{DC}$, ce qui confirme que $ABCD$ est bien un parallélogramme.

Le point $D$ a pour coordonnées $(3;-4)$.

### Pourquoi les autres réponses sont fausses

- **a)** On a pris l'ordre $ABDC$ en calculant $B + \overrightarrow{AC}$ : le point obtenu fait de $ABDC$ un parallélogramme, pas de $ABCD$.
- **b)** Ce sont les coordonnées du vecteur $\overrightarrow{ID}$, qu'on a prises pour celles du point $D$ en oubliant d'ajouter celles de $I$.
- **c)** On a calculé le symétrique de $I$ par rapport à $B$ au lieu du symétrique de $B$ par rapport à $I$.

</details>

Avis : 

---

## 49. `cqc-interpretation-graphique-moyenne-1` (séries BAC:D BAC:TI BEPC:)

**Énoncé :**

On donne le système suivant, où $(D_1)$ et $(D_2)$ sont deux droites du plan :

$$\begin{cases} 5x - 2y - 10 = 0 \\ 15x - 6y - 30 = 0 \end{cases}$$

Que peut-on dire des solutions de ce système et de la position relative des droites $(D_1)$ et $(D_2)$ ?

- a) Le système a une unique solution, $(2\,;\,0)$ : les droites sont sécantes en ce point.
- b) Le système n'a aucune solution : les droites sont strictement parallèles.
- c) Le système a une infinité de solutions : les droites sont confondues.
- d) Le système a une infinité de solutions : les droites sont strictement parallèles.

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsque les deux équations d'un système de droites sont proportionnelles terme à terme (coefficients de $x$, de $y$ et constante dans le même rapport), elles représentent en réalité la même droite : le système admet alors une infinité de solutions, et les deux droites sont confondues.

### Corrigé

On observe que $15x-6y-30 = 3\times(5x-2y-10)$ : les coefficients de $(D_2)$ s'obtiennent en multipliant ceux de $(D_1)$ par $3$ ($5\times3=15$, $-2\times3=-6$, $-10\times3=-30$).

$(D_1)$ et $(D_2)$ sont donc deux écritures de la même équation. Tout couple $(x\,;\,y)$ vérifiant la première équation vérifie automatiquement la seconde : le système admet une infinité de solutions (tous les points de la droite d'équation $5x-2y-10=0$).

Cela signifie que les droites $(D_1)$ et $(D_2)$ sont **confondues** : ce sont en réalité une seule et même droite.

### Pourquoi les autres réponses sont fausses

- **a)** Le couple $(2\,;\,0)$ est bien une solution, mais ce n'est pas la seule : tous les points de la droite conviennent.
- **b)** Les coefficients de $x$ et de $y$ sont proportionnels, mais la constante l'est aussi (même rapport $3$) : les droites ne sont pas strictement parallèles, elles sont confondues.
- **d)** Deux droites strictement parallèles n'ont aucun point commun, donc le système n'aurait aucune solution : les deux parties de la réponse se contredisent.

</details>

Avis : 

---

## 50. `cqc-losange-moyenne-0` (séries BAC:C BAC:E BEPC: PROBATOIRE:C PROBATOIRE:E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé $(O;I,J)$, on considère les points $A(1;1)$, $B(4;5)$, $C(7;1)$ et $D(4;-3)$.

Quelle est la nature la plus précise du quadrilatère $ABCD$ ?

- a) Un losange qui n'est pas un carré.
- b) Un carré.
- c) Un rectangle qui n'est pas un carré.
- d) Un parallélogramme qui n'est ni un losange ni un rectangle.

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour déterminer la nature d'un quadrilatère $ABCD$ à l'aide de coordonnées, on montre d'abord que c'est un parallélogramme (par exemple en vérifiant $\overrightarrow{AB} = \overrightarrow{DC}$), puis on compare les longueurs avec la formule $AB = \sqrt{(x_B-x_A)^2+(y_B-y_A)^2}$. Un parallélogramme ayant deux côtés consécutifs égaux est un losange ; un parallélogramme dont les diagonales ont la même longueur est un rectangle ; un carré est à la fois un losange et un rectangle.

### Corrigé

$\overrightarrow{AB}(4-1;5-1)$ soit $\overrightarrow{AB}(3;4)$, et $\overrightarrow{DC}(7-4;1-(-3))$ soit $\overrightarrow{DC}(3;4)$.

$\overrightarrow{AB} = \overrightarrow{DC}$ donc $ABCD$ est un parallélogramme.

$AB = \sqrt{3^2+4^2} = \sqrt{25} = 5$.

$\overrightarrow{BC}(7-4;1-5)$ soit $\overrightarrow{BC}(3;-4)$, donc $BC = \sqrt{3^2+(-4)^2} = \sqrt{25} = 5$.

$AB = BC = 5$ : le parallélogramme $ABCD$ a deux côtés consécutifs égaux, donc $ABCD$ est un losange.

Diagonales : $AC = \sqrt{(7-1)^2+(1-1)^2} = 6$ et $BD = \sqrt{(4-4)^2+(-3-5)^2} = 8$. Elles n'ont pas la même longueur, donc $ABCD$ n'est pas un rectangle, et donc pas un carré.

$ABCD$ est un losange qui n'est pas un carré.

### Pourquoi les autres réponses sont fausses

- **b)** Un carré aurait des diagonales de même longueur ; ici $AC = 6$ et $BD = 8$.
- **c)** Deux côtés consécutifs égaux ne donnent pas un angle droit ; de plus les diagonales $AC = 6$ et $BD = 8$ sont inégales, donc ce n'est pas un rectangle.
- **d)** On s'est arrêté au parallélogramme sans comparer les longueurs : $AB = BC = 5$ en fait un losange.

</details>

Avis : 

---

## 51. `cqc-mediatrice-elevee-5` (séries BAC:C BAC:D BAC:E BAC:TI BEPC: PROBATOIRE:C PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : au BEPC, calcul du centre par intersection de médiatrices en repère, faisable mais long pour un QCM.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé $(O;I,J)$, on considère le triangle $PQR$ avec $P(0\,;\,0)$, $Q(6\,;\,0)$ et $R(2\,;\,8)$.

Quelles sont les coordonnées du centre $\Omega$ du cercle circonscrit au triangle $PQR$ ?

- a) $\left(\dfrac83\,;\,\dfrac83\right)$
- b) $(4\,;\,4)$
- c) $(3\,;\,3{,}5)$
- d) $(2\,;\,1)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Le centre du cercle circonscrit à un triangle est le point d'intersection de ses médiatrices : il est équidistant des trois sommets. Pour l'obtenir, on écrit l'équation de deux médiatrices (un point $M$ est sur la médiatrice de $[PQ]$ si et seulement si $MP^2 = MQ^2$), puis on résout le système formé par ces deux équations. Il ne faut pas le confondre avec le centre de gravité (intersection des médianes) ni avec l'orthocentre (intersection des hauteurs).

### Corrigé

**Médiatrice de $[PQ]$.** Pour $M(x\,;\,y)$, l'égalité $MP^2 = MQ^2$ donne $x^2 + y^2 = (x-6)^2 + y^2$, soit $x^2 = x^2 - 12x + 36$, soit $12x = 36$, donc $x = 3$.

**Médiatrice de $[PR]$.** L'égalité $MP^2 = MR^2$ donne $x^2 + y^2 = x^2 - 4x + 4 + y^2 - 16y + 64$, soit $0 = -4x - 16y + 68$, soit $4x + 16y = 68$, donc $x + 4y = 17$.

**Intersection.** En remplaçant $x = 3$ dans $x + 4y = 17$ : $3 + 4y = 17$, donc $4y = 14$, donc $y = 3{,}5$. Donc $\Omega(3\,;\,3{,}5)$.

**Vérification de l'équidistance :**
$$\Omega P^2 = (3-0)^2 + (3{,}5-0)^2 = 9 + 12{,}25 = 21{,}25$$
$$\Omega Q^2 = (3-6)^2 + (3{,}5-0)^2 = 9 + 12{,}25 = 21{,}25$$
$$\Omega R^2 = (3-2)^2 + (3{,}5-8)^2 = 1 + 20{,}25 = 21{,}25$$

$\Omega$ est bien équidistant des trois sommets $P$, $Q$ et $R$ : c'est le centre du cercle circonscrit, de coordonnées $(3\,;\,3{,}5)$.

### Pourquoi les autres réponses sont fausses

- **a)** C'est le centre de gravité $G$, obtenu en faisant la moyenne des coordonnées des sommets : il est à l'intersection des médianes, pas des médiatrices.
- **b)** C'est le milieu du plus grand côté $[QR]$ : il n'est le centre du cercle circonscrit que si le triangle est rectangle, ce qui n'est pas le cas ici.
- **d)** C'est l'orthocentre, intersection des hauteurs (la hauteur issue de $R$ est la droite $x = 2$) : on a confondu hauteurs et médiatrices.

</details>

Avis : 

---

## 52. `cqc-rapport-faible-0` (séries BEPC: PROBATOIRE:C PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : image d'un point par une homothétie en coordonnées, à la limite haute du BEPC (souvent vue en Seconde) ; à vérifier au programme de 3e.

**Énoncé :**

Le plan est muni d'un repère orthonormé $(O ; \vec{i}, \vec{j})$. On considère l'homothétie $h$ de centre $\Omega(1\,;\,2)$ et de rapport $k = 2$.

Le point $A$ a pour coordonnées $A(4\,;\,3)$.

Quelles sont les coordonnées du point $A' = h(A)$ ?

- a) $A'(8\,;\,6)$
- b) $A'(6\,;\,2)$
- c) $A'\left(\dfrac52\,;\,\dfrac52\right)$
- d) $A'(7\,;\,4)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Si $h$ est l'homothétie de centre $\Omega$ et de rapport $k$, l'image $M'$ d'un point $M$ vérifie $\overrightarrow{\Omega M'} = k\,\overrightarrow{\Omega M}$. En coordonnées, cela donne $x_{M'} = x_\Omega + k(x_M - x_\Omega)$ et $y_{M'} = y_\Omega + k(y_M - y_\Omega)$.

### Corrigé

On calcule d'abord le vecteur $\overrightarrow{\Omega A}$ :
$$\overrightarrow{\Omega A} = (4 - 1\,;\, 3 - 2) = (3\,;\,1)$$

On applique le rapport $k=2$ :
$$\overrightarrow{\Omega A'} = 2\,\overrightarrow{\Omega A} = (6\,;\,2)$$

D'où les coordonnées de $A'$ :
$$x_{A'} = 1 + 6 = 7 \qquad y_{A'} = 2 + 2 = 4$$

Donc $A'(7\,;\,4)$.

Contrôle : la distance $\Omega A = \sqrt{3^2+1^2} = \sqrt{10}$ et $\Omega A' = \sqrt{6^2+2^2} = \sqrt{40} = 2\sqrt{10}$, soit exactement $k=2$ fois $\Omega A$. Le résultat est cohérent.

### Pourquoi les autres réponses sont fausses

- **a)** On a multiplié les coordonnées de $A$ par $2$, comme si le centre de l'homothétie était l'origine $O$.
- **b)** Ce sont les coordonnées du vecteur $\overrightarrow{\Omega A'}$ ; on a oublié d'ajouter celles de $\Omega$.
- **c)** On a divisé par le rapport au lieu de multiplier : $\overrightarrow{\Omega A'} = \dfrac12\,\overrightarrow{\Omega A}$.

</details>

Avis : 

---

## 53. `cqc-echelle-faible-0` (séries BAC:D BAC:TI BEPC: PROBATOIRE:C PROBATOIRE:E)

**Énoncé :**

Un plan de quartier est établi à l'échelle $\dfrac{1}{20\,000}$. La distance mesurée entre deux repères sur ce plan est de $5$ cm.

Quelle est la distance réelle correspondante, en kilomètres ?

- a) $10$ km
- b) $1$ km
- c) $0{,}1$ km
- d) $100$ km

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Une échelle $\dfrac{1}{k}$ signifie que $1$ cm mesuré sur le plan représente $k$ cm dans la réalité. Pour obtenir une distance réelle à partir d'une distance mesurée sur le plan, on multiplie cette distance par $k$, puis on convertit le résultat dans l'unité demandée.

### Corrigé

L'échelle est $\dfrac{1}{20\,000}$, donc $k = 20\,000$.

Distance réelle (en cm) $= 5 \times 20\,000 = 100\,000$ cm.

On convertit en mètres : $100\,000$ cm $= 1\,000$ m (on divise par $100$, puisque $1$ m $= 100$ cm).

On convertit en kilomètres : $1\,000$ m $= 1$ km (on divise par $1\,000$).

La distance réelle entre les deux repères est donc **$1$ km**.

### Pourquoi les autres réponses sont fausses

- **a)** On a divisé $100\,000$ cm par $10\,000$ au lieu de $100\,000$ : $1$ km $= 100\,000$ cm.
- **c)** On a divisé $100\,000$ cm par $1\,000\,000$, comme si $1$ km valait $1\,000\,000$ cm.
- **d)** On a divisé directement par $1\,000$, comme si la distance était en mètres et non en centimètres.

</details>

Avis : 

---

## 54. `cqc-classe-modale-elevee-0` (séries BAC:A BEPC: PROBATOIRE:A PROBATOIRE:D)

**Remarque du relecteur :** LIMITE : classe modale avec amplitudes inégales (densité/effectif corrigé), rarement traitée au BEPC.

**Énoncé :**

Une coopérative agricole a mesuré le rendement, en kilogrammes par parcelle, de 100 parcelles de maïs, et a regroupé les résultats dans le tableau suivant. L'effectif d'une des classes a été effacé par l'humidité, et les classes n'ont pas toutes la même amplitude :

| Rendement (kg/parcelle) | [200,260[ | [260,300[ | [300,340[ | [340,420[ |
|---|---|---|---|---|
| Nombre de parcelles $n_i$ | 18 | $n$ | 22 | 39 |

On sait que 100 parcelles ont été mesurées au total. Un technicien affirme que la classe modale est $[340\,;\,420[$, car c'est celle qui compte le plus grand nombre de parcelles.

Quelle est la véritable classe modale de cette série ?

- a) $[340\,;\,420[$
- b) $[260\,;\,300[$
- c) $[200\,;\,260[$
- d) $[300\,;\,340[$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand l'effectif d'une classe est inconnu mais que l'effectif total est donné, on le retrouve par soustraction : effectif manquant = effectif total $-$ somme des effectifs connus. Ensuite, dès que les classes n'ont pas toutes la même amplitude, la classe modale se détermine par la densité, $\text{densité}=\dfrac{\text{effectif}}{\text{amplitude}}$, et non par l'effectif brut : une classe large peut accumuler beaucoup d'individus sans être la plus concentrée.

### Corrigé
La somme des effectifs connus est $18+22+39=79$, donc l'effectif manquant est $n=100-79=21$.

Amplitudes : $60$, $40$, $40$ et $80$. Elles ne sont pas toutes égales : la comparaison des effectifs bruts n'est pas valable.

Densités :
$[200\,;\,260[$ : $\dfrac{18}{60}=0{,}3$ ; $[260\,;\,300[$ : $\dfrac{21}{40}=0{,}525$ ; $[300\,;\,340[$ : $\dfrac{22}{40}=0{,}55$ ; $[340\,;\,420[$ : $\dfrac{39}{80}=0{,}4875$.

La densité la plus élevée est $0{,}55$, atteinte par $[300\,;\,340[$. Le technicien a tort : $[340\,;\,420[$ doit son effectif élevé à sa grande amplitude ($80$ kg, le double des classes voisines). La classe modale est $[300\,;\,340[$ : réponse **d)**.

(Vérification : $18+21+22+39=100$.)

### Pourquoi les autres réponses sont fausses

- **a)** $[340\,;\,420[$ : c'est l'erreur du technicien, qui compare les effectifs bruts alors que les amplitudes diffèrent.
- **b)** $[260\,;\,300[$ : on a oublié un effectif connu en calculant $n$ ($n=100-(18+39)=43$), ce qui gonfle la densité de cette classe.
- **c)** $[200\,;\,260[$ : on a calculé le quotient à l'envers, $\dfrac{\text{amplitude}}{\text{effectif}}$, et retenu la plus grande valeur.

</details>

Avis : 

---

## 55. `cqc-homothetie-faible-0` (séries BAC:C BAC:D BAC:E BAC:TI BEPC: PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : effet d'une homothétie sur les aires (k²) au BEPC, à vérifier dans le programme de 3e ; coordonnées données mais inutiles.

**Énoncé :**

Dans le plan muni d'un repère orthonormé $(O;I,J)$, on considère les points $P(-1;3)$, $Q(5;3)$ et $R(2;7)$ ; l'aire du triangle $PQR$ vaut $12$ unités d'aire. Soit $h$ l'homothétie de centre $\Omega(1;1)$ et de rapport $k=2$, et $P'$, $Q'$, $R'$ les images respectives de $P$, $Q$ et $R$ par $h$.

Quelle est l'aire du triangle $P'Q'R'$ ?

- a) $48$ unités d'aire
- b) $24$ unités d'aire
- c) $96$ unités d'aire
- d) $12$ unités d'aire

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Une homothétie de centre $\Omega$ et de rapport $k$ associe à tout point $M$ le point $M'$ tel que $\overrightarrow{\Omega M'} = k\overrightarrow{\Omega M}$. Elle multiplie toutes les longueurs par $|k|$ et toutes les aires par $k^2$, tout en conservant la forme des figures.

### Corrigé
Une homothétie de rapport $k$ multiplie toute aire par $k^2$. Comme $k^2=4$ et l'aire de $PQR$ vaut $12$, l'aire de $P'Q'R'$ vaut $4\times 12=48$ unités d'aire : réponse **a)**.

Vérification par les coordonnées : $x'=1+2(x-1)$ et $y'=1+2(y-1)$ donnent $P'(-3;5)$, $Q'(9;5)$ et $R'(3;13)$. La base $P'Q'$ mesure $12$ et la hauteur issue de $R'$ mesure $13-5=8$, d'où une aire de $\dfrac{12\times 8}{2}=48$.

### Pourquoi les autres réponses sont fausses

- **b)** $24$ : on a multiplié l'aire par $k$ au lieu de $k^2$, comme pour une longueur.
- **c)** $96$ : on a multiplié par $k^3=8$, ce qui vaut pour les volumes et non pour les aires.
- **d)** $12$ : on a cru que l'homothétie conserve les aires, ce qui n'est vrai que si $k=1$ ou $k=-1$.

</details>

Avis : 

---

## 56. `cqc-inequations-moyenne-3` (séries BAC:C BAC:D BAC:E BAC:TI BEPC: PROBATOIRE:A PROBATOIRE:D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une coopérative agricole vend des sacs d'engrais à ses adhérents avec un tarif dégressif : pour une commande de $n$ sacs ($n$ entier naturel), le prix unitaire d'un sac, en francs CFA, est donné par $p(n) = 2000 + \dfrac{9000}{n+1}$.

Quel est le nombre minimal de sacs qu'un adhérent doit commander pour que le prix unitaire soit inférieur ou égal à $2900$ francs CFA ?

- a) $10$ sacs
- b) $8$ sacs
- c) $3$ sacs
- d) $9$ sacs

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On traduit la condition recherchée par une inéquation. Pour se débarrasser d'un dénominateur, on ne multiplie les deux membres par celui-ci qu'après avoir vérifié son signe : s'il est strictement positif, le sens de l'inégalité est conservé. On interprète ensuite l'ensemble solution en tenant compte des contraintes du problème, ici une variable entière.

### Corrigé

La condition est $p(n)\leqslant2900$, soit $2000+\dfrac{9000}{n+1}\leqslant2900$, c'est-à-dire $\dfrac{9000}{n+1}\leqslant900$.

Pour tout entier naturel $n$, $n+1\geqslant1>0$ : on peut multiplier les deux membres par $n+1$ sans changer le sens de l'inégalité :
$$9000\leqslant900(n+1) \iff 10\leqslant n+1 \iff n\geqslant9.$$

Vérification : $p(9)=2000+\dfrac{9000}{10}=2900$, qui convient ; $p(8)=2000+\dfrac{9000}{9}=3000$, qui ne convient pas.

Un adhérent doit donc commander au minimum $9$ sacs : réponse **d)**.

### Pourquoi les autres réponses sont fausses

- **a)** $10$ : on s'est arrêté à $n+1\geqslant10$ et on a donné la valeur de $n+1$ au lieu de celle de $n$.
- **b)** $8$ : erreur de soustraction, $2900-2000=1000$ au lieu de $900$, d'où $n+1\geqslant9$ ; or $p(8)=3000$ dépasse $2900$.
- **c)** $3$ : on a oublié le terme fixe $2000$ et résolu $\dfrac{9000}{n+1}\leqslant2900$.

</details>

Avis : 

---

## 57. `cqc-moyenne-ponderee-moyenne-0` (séries BAC:A BEPC: PROBATOIRE:A PROBATOIRE:C PROBATOIRE:E)

**Énoncé :**

Une salle de sport a relevé l'âge de ses 75 abonnés actifs. Les résultats sont regroupés en classes d'âge de même amplitude dans le tableau suivant :

| Âge (ans) | [15,20[ | [20,25[ | [25,30[ | [30,35[ | [35,40[ | [40,45[ |
|---|---|---|---|---|---|---|
| Nombre d'abonnés $n_i$ | 12 | 25 | 18 | 10 | 6 | 4 |

Quel est l'âge moyen $\bar x$ des abonnés de cette salle de sport ?

- a) $24$ ans
- b) $30$ ans
- c) $26{,}5$ ans
- d) $29$ ans

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour une série groupée en classes, on calcule le centre $c_i=\dfrac{a_i+b_i}{2}$ de chaque classe, puis on applique la formule de la moyenne pondérée $\bar x=\dfrac{\sum n_ic_i}{\sum n_i}$, en n'oubliant aucune classe dans le calcul de l'effectif total.

### Corrigé
Les centres de classes sont $c_i=17{,}5\,;\,22{,}5\,;\,27{,}5\,;\,32{,}5\,;\,37{,}5\,;\,42{,}5$.

L'effectif total est $N=12+25+18+10+6+4=75$.

$$\sum n_ic_i = 12\times17{,}5+25\times22{,}5+18\times27{,}5+10\times32{,}5+6\times37{,}5+4\times42{,}5$$
$$=210+562{,}5+495+325+225+170=1987{,}5$$

Donc $\bar x=\dfrac{1987{,}5}{75}=26{,}5$ (valeur exacte). L'âge moyen est de $26{,}5$ ans : réponse **c)**.

### Pourquoi les autres réponses sont fausses

- **a)** $24$ ans : on a pondéré les bornes inférieures des classes au lieu de leurs centres.
- **b)** $30$ ans : on a fait la moyenne des six centres sans tenir compte des effectifs.
- **d)** $29$ ans : on a pondéré les bornes supérieures des classes au lieu de leurs centres.

</details>

Avis : 

---

## 58. `cqc-pourcentages-moyenne-2` (séries BAC:A BAC:D BAC:TI BEPC: PROBATOIRE:A)

**Remarque du relecteur :** LIMITE : au BEPC, résoudre (1+t)²=1,21 suppose la racine carrée et des coefficients multiplicateurs successifs, faisable mais à la limite haute.

**Énoncé :**

Le chiffre d'affaires annuel d'une entreprise camerounaise de distribution est passé de $8\,000\,000$ F CFA à $9\,680\,000$ F CFA en deux ans, sous l'effet de deux augmentations annuelles successives et identiques.

Quel est le taux annuel de cette augmentation ?

- a) $10{,}5\,\%$
- b) $21\,\%$
- c) $1{,}1\,\%$
- d) $10\,\%$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'une grandeur subit deux évolutions successives au même taux inconnu $t$, le coefficient multiplicateur global est le carré du coefficient annuel : $(1+t)^2=\dfrac{\text{valeur finale}}{\text{valeur initiale}}$. Le coefficient annuel s'obtient donc en prenant la racine carrée de ce rapport.

### Corrigé

$$\dfrac{9\,680\,000}{8\,000\,000}=1{,}21 \qquad \text{donc} \qquad 1+t=\sqrt{1{,}21}=1{,}1$$

Le taux annuel d'augmentation est $t=10\,\%$ : réponse **d)**.

*Vérification :* $8\,000\,000\times1{,}1\times1{,}1=8\,000\,000\times1{,}21=9\,680\,000$.

### Pourquoi les autres réponses sont fausses

- **a)** $10{,}5\,\%$ : on a divisé l'augmentation globale de $21\,\%$ par $2$, comme si les pourcentages successifs s'additionnaient.
- **b)** $21\,\%$ : c'est le taux global sur les deux ans, pas le taux annuel.
- **c)** $1{,}1\,\%$ : on a confondu le coefficient multiplicateur $1{,}1$ avec le taux.

</details>

Avis : 

---

## 59. `cqc-rapport-faible-1` (séries BEPC: PROBATOIRE:C PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : homothétie de rapport négatif, à vérifier au programme BEPC (3e).

**Énoncé :**

On considère une homothétie $h$ de centre $I$ et de rapport $k = -\dfrac{1}{2}$. Soit $M$ un point tel que $IM = 6$ cm, et $M' = h(M)$.

Où se trouve le point $M'$ sur la droite $(IM)$, et quelle est la distance $IM'$ ?

- a) Du même côté de $I$ que $M$, avec $IM' = 3$ cm
- b) De l'autre côté de $I$ par rapport à $M$, avec $IM' = 12$ cm
- c) De l'autre côté de $I$ par rapport à $M$, avec $IM' = 3$ cm
- d) Du même côté de $I$ que $M$, avec $IM' = 12$ cm

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Le signe du rapport $k$ d'une homothétie indique la position de l'image par rapport au centre : si $k>0$, l'image $M'$ est du même côté du centre que $M$ ; si $k<0$, $M'$ est de l'autre côté, c'est-à-dire que le centre est situé entre $M$ et $M'$. La distance à l'image se calcule par $IM' = |k| \times IM$.

### Corrigé
Ici $k = -\dfrac12 < 0$ : $M'$ se trouve de l'autre côté de $I$ par rapport à $M$, le centre $I$ étant entre $M$ et $M'$.

$$IM' = \left|-\frac12\right| \times 6 = \frac12 \times 6 = 3 \text{ cm}$$

Donc $M'$ est à $3$ cm de $I$, du côté opposé à $M$ : réponse **c)**.

### Pourquoi les autres réponses sont fausses

- **a)** Même côté, $3$ cm : la distance est juste, mais on a ignoré le signe négatif du rapport.
- **b)** De l'autre côté, $12$ cm : on a divisé $6$ par $\dfrac12$ au lieu de le multiplier.
- **d)** Même côté, $12$ cm : on a cumulé les deux erreurs, oubli du signe et division par $\dfrac12$.

</details>

Avis : 

---

