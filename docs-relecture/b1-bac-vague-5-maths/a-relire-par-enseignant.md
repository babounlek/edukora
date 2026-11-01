# Vague 5 Maths BAC (anciennes questions « Tle » par série) : 69 QCM à faire relire par l'enseignant (campagne B1)

Date : 2026-11-01. Ces questions BAC avaient été créées en août, sans fichier source ; elles ont été exportées de la base puis converties. Sur 303 QCM convertis (340 questions étudiées, 37 écartées), **69** vous sont soumis : ceux que le relecteur aveugle a assortis d'une remarque, ceux dont des séries ont été retirées, et un tirage de 15 autres. Le lot est prêt mais n'est pas en ligne tant que vous n'avez pas répondu. Les 303 résolutions à l'aveugle ont donné la clé, sauf 16 jugées hors niveau pour une série (retirée) ou ambiguës (corrigée).

## Avis déjà rendus, appliqués par analogie (à confirmer)

- **Série A retirée du BAC** de 14 questions : nombres complexes (5), calcul intégral par parties ou d'encadrement (3), suites et suites d'intégrales (3), primitives trigonométriques (2), dérivée seconde (1).
- **Série A retirée du Probatoire** de 2 questions (`tableau-de-variations-moyenne-2` exponentielle, `-moyenne-3` logarithme népérien), absents du programme de Première A.
- **Une question laissée ouverte** (`probabilites-tle-a-moyenne-3`, tirage simultané de paires, posée seulement en série A).

## Points à trancher (nouveaux)

1. **Calcul d'une intégrale en série A** : simple calcul par une primitive (`calcul-integral-faible-0` et `-faible-1`, `courbes-representatives`) : au programme ?
2. **Théorie des graphes en séries C, D, E** (degrés, coloration, chaînes) : au programme ?
3. **Similitude indirecte en TI**, **demi-tour de l'espace**, **noyau et image d'un endomorphisme de R³** : limites hautes.
4. **Équations différentielles du second ordre** (racine double, second membre non guidé) en D et TI.
5. **Arithmétique en TI** (équations diophantiennes, théorème de Gauss).
6. **Questions très faciles** (niveau collège) pour C/E.
7. **Corrigés conservés en entier** pour des questions réduites : ils contiennent les sous-questions non posées.

Pour chaque question : **OK**, **à corriger** (dire quoi), **à retirer**, ou **retirer la série X**.

## 1. `cqc-arithmetique-tle-c-moyenne-2` (séries BAC:C)

**Énoncé :**

Quel est l'ensemble des solutions dans $\mathbb{Z}\times\mathbb{Z}$ de l'équation $(E):9x-16y=5$ ?

- a) $x=-3+9k$ et $y=-2+16k$, avec $k\in\mathbb{Z}$
- b) $x=-3+16k$ et $y=-2+9k$, avec $k\in\mathbb{Z}$
- c) $x=-3+16k$ et $y=-2-9k$, avec $k\in\mathbb{Z}$
- d) $x=3+16k$ et $y=2+9k$, avec $k\in\mathbb{Z}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour résoudre une équation diophantienne $ax+by=c$, on vérifie d'abord que $\text{pgcd}(a,b)$ divise $c$ (condition d'existence), on cherche ensuite un couple particulier de solutions à l'aide de l'algorithme d'Euclide (identité de Bézout), puis on exprime la solution générale par différence avec la solution particulière et le théorème de Gauss.
### Corrigé
**Existence.** Calculons $\text{pgcd}(9,16)$ par l'algorithme d'Euclide :
$$16=1\times9+7\qquad9=1\times7+2\qquad7=3\times2+1\qquad2=2\times1+0$$

Donc $\text{pgcd}(9,16)=1$, qui divise $5$ : $(E)$ admet des solutions dans $\mathbb{Z}\times\mathbb{Z}$.
**Solution particulière.** On remonte l'algorithme d'Euclide :
$$1=7-3\times2$$
$$1=7-3\times(9-7)=4\times7-3\times9$$
$$1=4\times(16-9)-3\times9=4\times16-7\times9$$

Donc $9\times(-7)-16\times(-4)=1$. En multipliant par $5$ : $9\times(-35)-16\times(-20)=5$, ce qui donne un premier couple solution $(-35\,;\,-20)$. En ajoutant un multiple de $(16\,;\,9)$ à ce couple (ce qui laisse l'équation vérifiée, voir la solution générale ci-dessous), on obtient un couple plus simple : avec $k=2$, $x=-35+2\times16=-3$ et $y=-20+2\times9=-2$.
**Vérification** : $9\times(-3)-16\times(-2)=-27+32=5$.  **Le couple $(x_0;y_0)=(-3;-2)$ est bien une solution particulière.**

**Solution générale.** Soit $(x;y)$ une solution quelconque de $(E)$. Comme $9x_0-16y_0=5$, en soustrayant on obtient $9(x-x_0)=16(y-y_0)$. Puisque $\text{pgcd}(9,16)=1$, le théorème de Gauss donne $16\mid(x-x_0)$, donc $x-x_0=16k$ ($k\in\mathbb{Z}$), puis $y-y_0=9k$.
$$\boxed{x=-3+16k,\quad y=-2+9k,\quad k\in\mathbb{Z}}$$

**Vérification** : $9(-3+16k)-16(-2+9k)=-27+144k+32-144k=5$.

### Pourquoi les autres réponses sont fausses
- **a)** les pas sont permutés : $x$ varie de $16$ (coefficient de $y$) et $y$ de $9$ ; pour $k=1$, $9\times6-16\times14\neq5$.
- **c)** erreur de signe sur le pas de $y$ : pour $k=1$, $9\times13-16\times(-11)=293\neq5$.
- **d)** la solution particulière est mal choisie : $9\times3-16\times2=-5\neq5$.


</details>

Avis : 

---

## 2. `cqc-arithmetique-tle-ti-moyenne-3` (séries BAC:TI)

**Remarque du relecteur :** LIMITE : arithmétique (équations diophantiennes, théorème de Gauss) à vérifier au programme de Terminale TI.

**Énoncé :**

On considère l'équation $(E) : 7x-4y=1$, d'inconnue le couple $(x,y)\in\mathbb{Z}\times\mathbb{Z}$, qui intervient dans le réglage entier d'un rapport d'engrenages. On sait que le couple $(3\,;\,5)$ est une solution de $(E)$.

Quel est l'ensemble des solutions de $(E)$ dans $\mathbb{Z}\times\mathbb{Z}$ ?

- a) $x=3+7k$ et $y=5+4k$, avec $k\in\mathbb{Z}$
- b) $x=3+4k$ et $y=5+7k$, avec $k\in\mathbb{Z}$
- c) $x=3-4k$ et $y=5+7k$, avec $k\in\mathbb{Z}$
- d) $x=3+4k$ et $y=5-7k$, avec $k\in\mathbb{Z}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour résoudre une équation diophantienne $ax+by=c$ à partir d'une solution particulière $(x_0,y_0)$ connue, on soustrait membre à membre $ax_0+by_0=c$ à $ax+by=c$, ce qui donne une égalité du type $a(x-x_0)=b(y_0-y)$. Comme $\text{pgcd}(a,b)=1$, le théorème de Gauss permet de conclure que $b$ divise $(x-x_0)$, ce qui fournit la solution générale sous forme paramétrée.
### Corrigé

**1. Vérification du couple $(3\,;\,5)$.**
$$7\times3-4\times5=21-20=1$$
Le couple $(3\,;\,5)$ vérifie bien $(E)$ : c'est une solution particulière.
**2. Solution générale.** Soit $(x,y)$ une solution quelconque de $(E)$. On a simultanément :
$$7x-4y=1 \qquad\text{et}\qquad 7\times3-4\times5=1$$

En soustrayant membre à membre :
$$7(x-3)-4(y-5)=0 \iff 7(x-3)=4(y-5)$$

Comme $\text{pgcd}(7,4)=1$ ($7$ et $4$ sont premiers entre eux), le théorème de Gauss appliqué à $7(x-3)=4(y-5)$ donne : $4$ divise $(x-3)$. Il existe donc un entier relatif $k$ tel que :
$$x-3=4k \iff x=3+4k$$

En reportant dans $7(x-3)=4(y-5)$ : $7\times4k=4(y-5)\iff7k=y-5\iff y=5+7k$.
$$\boxed{x=3+4k,\quad y=5+7k,\quad k\in\mathbb{Z}}$$

**Vérification.** $7(3+4k)-4(5+7k)=21+28k-20-28k=1$, pour tout $k\in\mathbb{Z}$ : la famille de solutions trouvée vérifie bien $(E)$, quel que soit $k$.

### Pourquoi les autres réponses sont fausses
- **a)** les pas sont permutés : $x$ varie de $4$ (coefficient de $y$) et non de $7$.
- **c)** les deux pas n'ont pas le même sens de variation ; pour $k=1$, $7\times(-1)-4\times12=-55\neq1$.
- **d)** erreur de signe sur le pas de $y$ ; pour $k=1$, $7\times7-4\times(-2)=57\neq1$.


</details>

Avis : 

---

## 3. `cqc-arithmetique-tle-ti-elevee-5` (séries BAC:TI)

**Remarque du relecteur :** LIMITE : équation diophantienne 12a+17b=200 ; vérifier que l'arithmétique figure au programme de Terminale TI (sinon la question se résout seulement par essai des choix).

**Énoncé :**

Un électricien doit installer exactement $200\ \text{m}$ de gaine technique dans un atelier, en utilisant uniquement des rouleaux complets, sans découpe : des rouleaux de $12\ \text{m}$ et des rouleaux de $17\ \text{m}$.

Quel couple (nombre de rouleaux de $12\ \text{m}$ ; nombre de rouleaux de $17\ \text{m}$) convient ?

- a) $(4\,;\,11)$
- b) $(-6\,;\,16)$
- c) $(11\,;\,4)$
- d) $(28\,;\,-8)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
La longueur totale de gaine technique posée avec $x$ rouleaux de $12\ \text{m}$ et $y$ rouleaux de $17\ \text{m}$ vérifie l'équation diophantienne $12x+17y=200$, avec $x,y$ entiers naturels. On résout d'abord cette équation dans $\mathbb{Z}\times\mathbb{Z}$ par l'algorithme d'Euclide étendu (identité de Bézout) et le théorème de Gauss, puis on restreint la famille de solutions obtenue aux couples $(x,y)$ dont les deux coordonnées sont des entiers naturels, seule situation réellement réalisable sur le chantier.
### Corrigé

**Existence de solutions.** Calculons $\text{pgcd}(12,17)$ par l'algorithme d'Euclide :
$$17=1\times12+5$$
$$12=2\times5+2$$
$$5=2\times2+1$$
$$2=2\times1+0$$

Le dernier reste non nul est $1$, donc $\text{pgcd}(12,17)=1$. Comme $1$ divise $200$, l'équation $12x+17y=200$ admet des solutions dans $\mathbb{Z}\times\mathbb{Z}$.
**Solution particulière (identité de Bézout).** On remonte l'algorithme d'Euclide :
$$1=5-2\times2$$
$$1=5-2\times(12-2\times5)=5\times5-2\times12$$
$$1=5\times(17-12)-2\times12=5\times17-7\times12$$

Donc $12\times(-7)+17\times5=1$. En multipliant par $200$ :
$$12\times(-1400)+17\times1000=200$$

Un couple particulier est $(x_0\,;\,y_0)=(-1400\,;\,1000)$.
**Solution générale.** Soit $(x,y)$ une solution de $12x+17y=200$. Avec le couple particulier, $12x_0+17y_0=200$ ; en soustrayant :
$$12(x-x_0)+17(y-y_0)=0 \iff 12(x-x_0)=17(y_0-y)$$

Comme $\text{pgcd}(12,17)=1$, le théorème de Gauss donne $17\mid(x-x_0)$, donc $x-x_0=17k$ ($k\in\mathbb{Z}$), soit :
$$x=-1400+17k \qquad y=1000-12k,\quad k\in\mathbb{Z}$$

**Restriction aux solutions physiquement acceptables ($x\ge0$ et $y\ge0$).**
$$x\ge0 \iff -1400+17k\ge0 \iff k\ge\dfrac{1400}{17}\approx82{,}35 \iff k\ge83$$
$$y\ge0 \iff 1000-12k\ge0 \iff k\le\dfrac{1000}{12}\approx83{,}33 \iff k\le83$$

Les deux conditions imposent simultanément $k\ge83$ et $k\le83$, donc $k=83$ est l'unique valeur entière possible.
**Calcul du couple correspondant.**
$$x=-1400+17\times83=-1400+1411=11 \qquad y=1000-12\times83=1000-996=4$$

**Vérification.** $12\times11+17\times4=132+68=200$. La longueur totale correspond bien aux $200\ \text{m}$ annoncés, et $x=11\ge0$, $y=4\ge0$ sont bien des entiers naturels.
**L'électricien doit utiliser $11$ rouleaux de $12\ \text{m}$ et $4$ rouleaux de $17\ \text{m}$, et c'est la seule répartition possible sans découpe.**

### Pourquoi les autres réponses sont fausses
- **a)** les deux nombres de rouleaux sont inversés : $12\times4+17\times11=235\neq200$.
- **b)** c'est une solution de l'équation $12x+17y=200$ dans $\mathbb{Z}$, mais $x=-6$ n'est pas un nombre de rouleaux possible.
- **d)** c'est aussi une solution entière de $12x+17y=200$, mais $y=-8$ est négatif : le nombre de rouleaux doit être un entier naturel.


</details>

Avis : 

---

## 4. `cqc-coniques-tle-ce-elevee-5` (séries BAC:C BAC:E)

**Énoncé :**

Le plan est muni d'un repère orthonormé $(O;\vec\imath,\vec\jmath)$. L'ensemble $(\Gamma)$ des points $M(x;y)$ tels que $4x^2-9y^2-16x-54y-101=0$ est une hyperbole.

Quels sont son centre $\Omega$ et son excentricité $e$ ?

- a) $\Omega(2;-3)$ et $e=\dfrac{\sqrt{13}}3$
- b) $\Omega(-2;3)$ et $e=\dfrac{\sqrt{13}}3$
- c) $\Omega(2;-3)$ et $e=\dfrac{\sqrt5}3$
- d) $\Omega(2;-3)$ et $e=\dfrac{\sqrt{13}}2$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour reconnaître la nature d'une conique donnée par une équation générale comportant des termes du premier degré en $x$ et en $y$, on regroupe séparément les termes en $x$ et en $y$, puis on met chaque groupe sous forme canonique (carré parfait plus ou moins une constante) : cela fait apparaître un changement de repère qui ramène l'équation à une forme réduite centrée en un point $\Omega$ autre que l'origine.
### Corrigé
On regroupe les termes en $x$ et les termes en $y$ :
$$4x^2-16x-9y^2-54y-101=0$$

$$4(x^2-4x)-9(y^2+6y)=101$$

On met chaque parenthèse sous forme canonique :
$$x^2-4x=(x-2)^2-4\qquad y^2+6y=(y+3)^2-9$$

D'où :
$$4\big[(x-2)^2-4\big]-9\big[(y+3)^2-9\big]=101$$

$$4(x-2)^2-16-9(y+3)^2+81=101$$

$$4(x-2)^2-9(y+3)^2=101+16-81=36$$

En divisant par $36$ :
$$\dfrac{(x-2)^2}{9}-\dfrac{(y+3)^2}{4}=1$$

En posant $X=x-2$ et $Y=y+3$ (changement de repère de centre $\Omega(2;-3)$), on retrouve l'équation réduite $\dfrac{X^2}{9}-\dfrac{Y^2}{4}=1$ : $(\Gamma)$ est bien une **hyperbole**, de centre $\Omega(2;-3)$, avec $a^2=9$ (donc $a=3$) et $b^2=4$ (donc $b=2$), d'axe transverse parallèle à l'axe des abscisses (le terme en $X^2$ est positif).
**Foyers.** $c=\sqrt{a^2+b^2}=\sqrt{9+4}=\sqrt{13}$. Dans le repère $(\Omega;\vec\imath,\vec\jmath)$, les foyers sont en $(\pm c;0)$, soit dans le repère d'origine :
$$F\big(2+\sqrt{13}\,;\,-3\big)\qquad F'\big(2-\sqrt{13}\,;\,-3\big)$$

**Asymptotes.** Dans le repère $(\Omega;\vec\imath,\vec\jmath)$, elles ont pour équations $Y=\pm\dfrac{b}{a}X$, soit en revenant à $(x;y)$ :
$$y+3=\pm\dfrac23(x-2)$$

**Excentricité.**
$$e=\dfrac{c}{a}=\dfrac{\sqrt{13}}3\approx1{,}20$$

**Vérification.** On redéveloppe $4(x-2)^2-9(y+3)^2-36$ pour retrouver l'équation de départ :
$$4(x^2-4x+4)-9(y^2+6y+9)-36=4x^2-16x+16-9y^2-54y-81-36=4x^2-9y^2-16x-54y+(16-81-36)$$
et $16-81-36=-101$, donc on retombe exactement sur $4x^2-9y^2-16x-54y-101=0$.
$$\boxed{\Omega(2;-3),\ F\big(2+\sqrt{13};-3\big),\ F'\big(2-\sqrt{13};-3\big),\ y+3=\pm\dfrac23(x-2),\ e=\dfrac{\sqrt{13}}3}$$

### Piège à éviter
Oublier de recentrer les foyers et les asymptotes sur $\Omega(2;-3)$ après le changement de variable est l'erreur la plus fréquente : les formules $c=\sqrt{a^2+b^2}$ et $y=\pm\dfrac{b}{a}x$ s'appliquent dans le repère $(\Omega;X,Y)$, pas dans le repère d'origine $(O;x,y)$.

### Pourquoi les autres réponses sont fausses
- **b)** le centre est lu avec les signes opposés : $(x-2)^2$ et $(y+3)^2$ donnent $\Omega(2;-3)$.
- **c)** on utilise $c^2=a^2-b^2$ au lieu de $c^2=a^2+b^2$.
- **d)** l'excentricité est calculée par $\dfrac cb$ au lieu de $\dfrac ca$.


</details>

Avis : 

---

## 5. `cqc-fonction-logarithme-neperien-tle-d-moyenne-2` (séries BAC:D)

**Énoncé :**

Quel est l'ensemble des solutions dans $\mathbb{R}$ de l'inéquation $\ln(3x - 2) \leqslant \ln(x + 4)$ ?

- a) $]-\infty\,;3]$
- b) $\left[\dfrac23\,;3\right]$
- c) $[3\,;+\infty[$
- d) $\left]\dfrac23\,;3\right]$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour résoudre une inéquation faisant intervenir plusieurs logarithmes, on détermine d'abord le domaine où chaque argument est strictement positif, puis on exploite la stricte croissance de $\ln$ sur $\left]0~;~+\infty\right[$ : pour deux quantités strictement positives, $\ln(a) \leqslant \ln(b) \iff a \leqslant b$. La solution finale s'obtient en croisant cette comparaison avec le domaine trouvé au départ.

### Corrigé
**Conditions d'existence.** Pour que $\ln(3x-2)$ et $\ln(x+4)$ soient définis, il faut $3x-2>0$, soit $x > \dfrac{2}{3}$, et $x+4>0$, soit $x>-4$. Comme $\dfrac{2}{3} > -4$, la condition la plus restrictive est $x > \dfrac{2}{3}$ : c'est le domaine de travail.

**Résolution de l'inéquation.** La fonction $\ln$ est strictement croissante sur $\left]0~;~+\infty\right[$. Pour deux quantités strictement positives, l'ordre des logarithmes est donc le même que l'ordre des quantités : sous réserve du domaine,
$$\ln(3x-2) \leqslant \ln(x+4) \iff 3x - 2 \leqslant x + 4$$
$$\iff 2x \leqslant 6 \iff x \leqslant 3$$

**Intersection avec le domaine.** La solution doit vérifier à la fois $x > \dfrac{2}{3}$ et $x \leqslant 3$.

**Vérification aux bornes.** En $x = \dfrac{2}{3}$ : $3x-2=0$, $\ln(0)$ n'existe pas, la borne est donc exclue. En $x=3$ : $3x-2=7>0$ et $x+4=7>0$, et $\ln(7)\leqslant\ln(7)$ est vrai (égalité) : la borne $x=3$ est donc incluse.

**Conclusion** : $S = \left]\dfrac{2}{3}~;~3\right]$.

### Pourquoi les autres réponses sont fausses

- **a)** On oublie les conditions d'existence : il faut $3x-2>0$, donc $x>\dfrac23$.
- **b)** On inclut la borne $\dfrac23$, pour laquelle $\ln(3x-2)=\ln0$ n'est pas défini.
- **c)** On inverse le sens de l'inégalité en passant aux arguments, alors que $\ln$ est croissante.

</details>

Avis : 

---

## 6. `cqc-fonctions-exponentielles-et-fonctions-puissances-tle-ce-moyenne-2` (séries BAC:C BAC:E)

**Énoncé :**

Quelle est la solution, dans $]0;+\infty[$, de l'équation d'inconnue réelle $x$ suivante ?
$$x^{\ln 2}=16$$

- a) $x=4$
- b) $x=e^{4}$
- c) $x=16^{\ln 2}$
- d) $x=e^{16}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour résoudre une équation de la forme $x^{\alpha}=b$ où l'inconnue $x>0$ est cette fois en base et l'exposant $\alpha$ est fixe, on écrit $x^{\alpha}=e^{\alpha\ln x}$, on exprime $b$ sous la même forme exponentielle, puis l'injectivité de la fonction exponentielle permet d'identifier les exposants pour en tirer $\ln x$, donc $x$.

### Corrigé

Pour $x>0$, on utilise la forme exponentielle de la fonction puissance : $x^{\ln2}=e^{\ln2\times\ln x}$. Comme $16=2^{4}=e^{4\ln2}$, l'équation devient :
$$e^{\ln2\times\ln x}=e^{4\ln2}$$

Par stricte croissance (donc injectivité) de la fonction exponentielle sur $\mathbb{R}$ :
$$\ln2\times\ln x=4\ln2$$

Comme $\ln2\neq0$, on divise les deux membres par $\ln2$ :
$$\ln x=4 \iff x=e^{4}$$

**Vérification** : $(e^{4})^{\ln2}=e^{4\ln2}=\left(e^{\ln2}\right)^{4}=2^{4}=16$.

L'ensemble des solutions est $S=\{e^{4}\}$ (et $e^{4}>0$, donc cette solution appartient bien au domaine $]0;+\infty[$).

### Pourquoi les autres réponses sont fausses

- **a)** $x=4$ : on obtient $\ln x=4$ mais on conclut $x=4$ au lieu de $x=e^{4}$.
- **c)** $x=16^{\ln 2}$ : on élève $16$ à la puissance $\ln 2$ au lieu de l'élever à $\frac{1}{\ln 2}$.
- **d)** $x=e^{16}$ : on écrit $\ln x=16$ en oubliant que $16=e^{4\ln 2}$ et que $\ln 2$ se simplifie.

</details>

Avis : 

---

## 7. `cqc-fonctions-numeriques-dune-variable-reelle-tle-ce-moyenne-2` (séries BAC:C BAC:E)

**Énoncé :**

Soit $h$ la fonction définie sur $\mathbb{R}\setminus\{2\}$ par $h(x)=\dfrac{2x^2-5x+3}{x-2}$.
Quelle est l'équation de l'asymptote oblique à la courbe représentative de $h$ ?

- a) $y=2x-5$
- b) $y=2x-1$
- c) $y=2x+1$
- d) $y=2x+3$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour déterminer les asymptotes d'une fonction rationnelle dont le numérateur est de degré supérieur à celui du dénominateur, on effectue la division euclidienne du numérateur par le dénominateur afin d'écrire la fonction sous la forme partie affine $+$ reste sur dénominateur : la partie affine donne l'asymptote oblique (le reste tendant vers $0$ à l'infini), et l'annulation du dénominateur donne l'asymptote verticale.

### Corrigé

**1. Division euclidienne.** On effectue la division de $2x^2-5x+3$ par $x-2$ :
$$2x^2-5x+3=(x-2)(2x-1)+1$$

Vérification du développement : $(x-2)(2x-1)=2x^2-x-4x+2=2x^2-5x+2$, et $2x^2-5x+2+1=2x^2-5x+3$, ce qui correspond bien au numérateur de départ.

En divisant par $x-2$ (non nul car $x\neq2$) :
$$h(x)=\dfrac{(x-2)(2x-1)+1}{x-2}=2x-1+\dfrac1{x-2}$$

Donc $a=2$, $b=-1$, $c=1$.

**2. Asymptotes.**

*Asymptote verticale.* Quand $x\to2$, $\dfrac1{x-2}\to\pm\infty$ (le dénominateur tend vers $0$ tandis que le numérateur, $1$, ne s'annule pas), donc $h(x)\to\pm\infty$ : la droite d'équation $x=2$ est asymptote verticale à la courbe de $h$.

*Asymptote oblique.* Quand $x\to\pm\infty$, $\dfrac1{x-2}\to0$, donc :
$$\lim_{x\to\pm\infty}\big[h(x)-(2x-1)\big]=\lim_{x\to\pm\infty}\dfrac1{x-2}=0$$

La droite d'équation $y=2x-1$ est donc asymptote oblique à la courbe de $h$, à la fois en $-\infty$ et en $+\infty$.

$$\boxed{x=2 \text{ (asymptote verticale)} \quad\text{et}\quad y=2x-1 \text{ (asymptote oblique)}}$$

### Pourquoi les autres réponses sont fausses

- **a)** $y=2x-5$ : on lit le coefficient de $x$ au numérateur comme terme constant de la partie affine.
- **c)** $y=2x+1$ : erreur de signe dans la division : $(x-2)(2x+1)=2x^2-3x-2$ ne redonne pas $-5x$.
- **d)** $y=2x+3$ : on recopie le terme constant du numérateur au lieu d'effectuer la division.

</details>

Avis : 

---

## 8. `cqc-graphes-tle-d-elevee-5` (séries BAC:D)

**Remarque du relecteur :** LIMITE : vérifier que la théorie des graphes (degrés, réalisabilité d'une suite de degrés) est au programme de Terminale D.

**Énoncé :**

Parmi les suites de cinq nombres suivantes, laquelle peut être la suite des degrés des cinq sommets d'un graphe simple (sans boucle ni arête multiple) ?

- a) $(4\,;3\,;3\,;2\,;1)$
- b) $(5\,;3\,;3\,;2\,;1)$
- c) $(4\,;4\,;3\,;3\,;0)$
- d) $(4\,;3\,;3\,;2\,;2)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour qu'une suite de nombres soit la suite des degrés d'un graphe simple, il faut d'abord que leur somme soit paire (lemme des poignées de main : la somme des degrés est égale à $2\times$ le nombre d'arêtes). Il faut aussi que chaque degré soit au plus égal à $n-1$ pour un graphe d'ordre $n$, et que les degrés soient compatibles entre eux (un sommet de degré $n-1$ est relié à tous les autres, donc aucun sommet n'a un degré nul). Si ces conditions sont satisfaites, on tente une construction explicite.

### Corrigé

- $(4\,;3\,;3\,;2\,;1)$ : somme $=13$, impaire, donc impossible.
- $(5\,;3\,;3\,;2\,;1)$ : somme $=14$, mais $5>4$ : un sommet ne peut pas avoir plus de $4$ voisins dans un graphe d'ordre $5$.
- $(4\,;4\,;3\,;3\,;0)$ : somme $=14$, mais les deux sommets de degré $4$ sont reliés à tous les autres, donc le sommet de degré $0$ ne peut pas exister.
- $(4\,;3\,;3\,;2\,;2)$ : somme $=14$, soit $7$ arêtes. Avec les sommets $A$, $B$, $C$, $D$, $E$ de degrés respectifs $4\,;3\,;3\,;2\,;2$, les arêtes $AB$, $AC$, $AD$, $AE$, $BC$, $BD$, $CE$ conviennent :

| Sommet | Voisins | Degré |
|---|---|---|
| $A$ | $B, C, D, E$ | $4$ |
| $B$ | $A, C, D$ | $3$ |
| $C$ | $A, B, E$ | $3$ |
| $D$ | $A, B$ | $2$ |
| $E$ | $A, C$ | $2$ |

La bonne réponse est donc $(4\,;3\,;3\,;2\,;2)$.

### Pourquoi les autres réponses sont fausses

- **a)** $(4\,;3\,;3\,;2\,;1)$ : la somme des degrés vaut $13$, qui est impaire : elle devrait être le double du nombre d'arêtes.
- **b)** $(5\,;3\,;3\,;2\,;1)$ : la somme est paire ($14$) mais un sommet de degré $5$ aurait $5$ voisins, alors que le graphe n'a que $4$ autres sommets.
- **c)** $(4\,;4\,;3\,;3\,;0)$ : la somme est paire ($14$) mais un sommet de degré $4$ est relié aux quatre autres, ce qui interdit l'existence d'un sommet de degré $0$.

</details>

Avis : 

---

## 9. `cqc-graphes-tle-d-faible-1` (séries BAC:D BAC:TI)

**Remarque du relecteur :** LIMITE : la théorie des graphes est-elle bien au programme de Terminale D ? À vérifier pour la série D.

**Énoncé :**

On modélise un petit réseau informatique par un graphe simple non orienté $H$ dont les sommets sont quatre serveurs $P$, $Q$, $R$, $S$. Une arête relie deux serveurs lorsqu'ils sont connectés par un câble direct. Le tableau suivant indique par un $1$ que deux serveurs sont directement reliés et par un $0$ qu'ils ne le sont pas :

| | $P$ | $Q$ | $R$ | $S$ |
|---|---|---|---|---|
| $P$ | $0$ | $1$ | $1$ | $0$ |
| $Q$ | $1$ | $0$ | $1$ | $1$ |
| $R$ | $1$ | $1$ | $0$ | $1$ |
| $S$ | $0$ | $1$ | $1$ | $0$ |

Combien d'arêtes le graphe $H$ compte-t-il ?

- a) $5$
- b) $10$
- c) $6$
- d) $4$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un tableau d'adjacence d'un graphe simple non orienté, le tableau est symétrique par rapport à la diagonale et chaque arête correspond à deux $1$ symétriques. Il suffit donc de compter les $1$ situés d'un seul côté de la diagonale. On peut aussi vérifier avec le lemme des poignées de main : la somme des degrés (somme des $1$ du tableau) est le double du nombre d'arêtes.

### Corrigé

Les $1$ au-dessus de la diagonale sont : $PQ$, $PR$, $QR$, $QS$, $RS$ (la paire $PS$ vaut $0$). Le graphe compte donc $5$ arêtes.

Vérification : les degrés sont $2$, $3$, $3$ et $2$, de somme $10=2\times5$.

### Pourquoi les autres réponses sont fausses

- **b)** $10$ : chaque arête apparaît deux fois dans le tableau (symétrique) et on compte tous les $1$.
- **c)** $6$ : c'est le nombre d'arêtes d'un graphe complet d'ordre $4$ : on ne remarque pas le $0$ entre $P$ et $S$.
- **d)** $4$ : on donne l'ordre du graphe (nombre de sommets) au lieu du nombre d'arêtes.

</details>

Avis : 

---

## 10. `cqc-graphes-tle-d-moyenne-2` (séries BAC:D BAC:TI)

**Remarque du relecteur :** LIMITE : la théorie des graphes est au programme de TI ; vérifier qu'elle figure bien au programme de Terminale D.

**Énoncé :**

Une compagnie de transport dessert six localités notées $A$, $B$, $C$, $D$, $E$, $F$. On modélise son réseau de liaisons directes (assurées dans les deux sens) par un graphe simple non orienté dont l'ensemble des arêtes est $\{AB, BC, CD, DE, BE, EF\}$.
Parmi les séquences de sommets suivantes, laquelle est un cycle de ce graphe ?

- a) $A-B-E-F-A$
- b) $B-C-D-E-B$
- c) $B-C-D-E-F$
- d) $B-C-D-C-B$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Une chaîne est une suite de sommets consécutivement reliés par une arête. Un cycle est une chaîne fermée (le sommet d'arrivée est le sommet de départ) qui n'emprunte jamais deux fois la même arête.

### Corrigé

La séquence $B-C-D-E-B$ utilise les arêtes $BC$, $CD$, $DE$ et $EB$, qui existent toutes dans le graphe et sont deux à deux distinctes. Elle est fermée : c'est un cycle de longueur $4$.

### Pourquoi les autres réponses sont fausses

- **a)** $A-B-E-F-A$ : la séquence se ferme sur $A$ mais $FA$ n'est pas une arête du graphe.
- **c)** $B-C-D-E-F$ : c'est une chaîne mais elle n'est pas fermée : le sommet d'arrivée diffère du sommet de départ.
- **d)** $B-C-D-C-B$ : la séquence est fermée mais elle emprunte deux fois l'arête $BC$ : ce n'est pas un cycle.

</details>

Avis : 

---

## 11. `cqc-graphes-tle-d-moyenne-3` (séries BAC:D BAC:TI)

**Remarque du relecteur :** LIMITE : coloration de graphes (Welsh-Powell), à confirmer au programme de Terminale D.

**Énoncé :**

On considère un graphe simple non orienté $G$ dont l'ensemble des sommets est $\{A, B, C, D, E, F\}$ et dont l'ensemble des arêtes est $\{AB, AC, AD, BC, BE, CD, CF, DE, EF\}$.
On applique l'algorithme de Welsh-Powell : les sommets sont rangés par degré décroissant (à degré égal, par ordre alphabétique), puis on remplit une couleur après l'autre.
Quelle est la répartition des sommets obtenue ?

- a) $\{C,F\}$, $\{A,E\}$, $\{B,D\}$
- b) $\{C,E\}$, $\{A,B\}$, $\{D,F\}$
- c) $\{C,E\}$, $\{A,F\}$, $\{B,D\}$
- d) $\{C,E\}$, $\{A,D\}$, $\{B,F\}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
L'algorithme de Welsh-Powell colore un graphe de proche en proche : on range d'abord les sommets par degré décroissant. On attribue une première couleur au premier sommet de la liste, puis, en parcourant le reste de la liste dans l'ordre, on attribue cette même couleur à tout sommet non encore coloré qui n'est adjacent à aucun sommet déjà affecté à cette couleur. On recommence ensuite avec une nouvelle couleur pour les sommets encore non colorés, et ainsi de suite jusqu'à ce que tous les sommets soient colorés.

### Corrigé

**1. Degrés des sommets.**

| Sommet | Arêtes incidentes | Degré |
|---|---|---|
| $A$ | $AB, AC, AD$ | $3$ |
| $B$ | $AB, BC, BE$ | $3$ |
| $C$ | $AC, BC, CD, CF$ | $4$ |
| $D$ | $AD, CD, DE$ | $3$ |
| $E$ | $BE, DE, EF$ | $3$ |
| $F$ | $CF, EF$ | $2$ |

**Vérification.** Somme des degrés $=3+3+4+3+3+2=18$ ; le graphe compte $9$ arêtes, donc $2\times9=18$. $\checkmark$

**2. Classement par degré décroissant.** $C(4)$, puis $A$, $B$, $D$, $E$ (degré $3$, classés par ordre alphabétique à égalité), puis $F(2)$ :
$$C,\ A,\ B,\ D,\ E,\ F$$

**Application de l'algorithme.**

*Couleur 1.* On attribue la couleur 1 à $C$. On parcourt ensuite $A$, $B$, $D$, $E$, $F$ : $A$, $B$ et $D$ sont chacun reliés à $C$ (arêtes $AC$, $BC$, $CD$), ils ne peuvent pas recevoir la couleur 1. $E$ n'est relié à $C$ par aucune arête : on lui attribue la couleur 1. $F$ est relié à $C$ (arête $CF$) : il ne peut pas recevoir la couleur 1.
$$\text{Couleur 1}=\{C, E\}$$

*Couleur 2.* Sommets restants, dans l'ordre : $A$, $B$, $D$, $F$. On attribue la couleur 2 à $A$. $B$ est relié à $A$ (arête $AB$) : refusé. $D$ est relié à $A$ (arête $AD$) : refusé. $F$ n'est relié à $A$ par aucune arête : on lui attribue la couleur 2.
$$\text{Couleur 2}=\{A, F\}$$

*Couleur 3.* Sommets restants : $B$, $D$. On attribue la couleur 3 à $B$. $D$ n'est relié à $B$ par aucune arête (les voisins de $B$ sont $A$, $C$, $E$) : on lui attribue aussi la couleur 3.
$$\text{Couleur 3}=\{B, D\}$$

**Vérification de la coloration obtenue.** Aucune arête ne relie deux sommets de même couleur : $C$-$E$ (couleur 1) n'est pas une arête de $G$ $\checkmark$ ; $A$-$F$ (couleur 2) n'est pas une arête de $G$ $\checkmark$ ; $B$-$D$ (couleur 3) n'est pas une arête de $G$ $\checkmark$. La coloration est donc valide.

**3. Nombre de couleurs utilisées.** L'algorithme utilise $3$ couleurs :
$$\boxed{3\text{ couleurs : }\{C,E\},\ \{A,F\},\ \{B,D\}}$$

### Pourquoi les autres réponses sont fausses

- **a)** $\{C,F\}$, $\{A,E\}$, $\{B,D\}$ : $C$ et $F$ sont reliés par l'arête $CF$ : ils ne peuvent pas avoir la même couleur.
- **b)** $\{C,E\}$, $\{A,B\}$, $\{D,F\}$ : $A$ et $B$ sont reliés par l'arête $AB$ : ils ne peuvent pas avoir la même couleur.
- **d)** $\{C,E\}$, $\{A,D\}$, $\{B,F\}$ : $A$ et $D$ sont reliés par l'arête $AD$ : ils ne peuvent pas avoir la même couleur.

</details>

Avis : 

---

## 12. `cqc-graphes-tle-d-moyenne-4` (séries BAC:D BAC:TI)

**Remarque du relecteur :** VOCABULAIRE : « couples » désigne en maths des paires ordonnées, ce qui donnerait 14 (choix c présent) ; écrire « paires d'équipes » ou « combien de matchs restent à jouer ». Les graphes ne sont pas au programme de Terminale D, mais la question se résout par simple dénombrement.

**Énoncé :**

Dans un tournoi de football, six équipes $E_1,\dots,E_6$ participent. Voici la liste des rencontres déjà disputées :

| Équipe 1 | Équipe 2 |
|---|---|
| $E_1$ | $E_3$ |
| $E_1$ | $E_5$ |
| $E_2$ | $E_4$ |
| $E_2$ | $E_5$ |
| $E_3$ | $E_4$ |
| $E_3$ | $E_6$ |
| $E_4$ | $E_5$ |
| $E_5$ | $E_6$ |

On modélise la situation par un graphe non orienté dont les sommets sont les équipes, deux sommets étant reliés si les équipes se sont déjà rencontrées. Combien de paires d'équipes ne se sont pas encore affrontés ?

- a) $8$
- b) $15$
- c) $14$
- d) $7$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Chaque rencontre déjà jouée est une arête du graphe. Pour $n$ sommets, le nombre de couples de sommets distincts est $\dfrac{n(n-1)}{2}$ ; les couples qui ne sont pas reliés par une arête correspondent aux rencontres qui n'ont pas encore eu lieu.

### Corrigé

Le graphe a $6$ sommets, donc $\dfrac{6\times5}{2}=15$ couples possibles. Le tableau liste $8$ rencontres, c'est-à-dire $8$ arêtes. Le nombre de couples non encore affrontés est :
$$15-8=7$$

(Par exemple $E_1$ et $E_2$ ne se sont pas encore rencontrées.)

### Pourquoi les autres réponses sont fausses

- **a)** $8$ : c'est le nombre de rencontres déjà jouées, c'est-à-dire le nombre d'arêtes du graphe.
- **b)** $15$ : c'est le nombre total de couples possibles : on ne retranche pas les rencontres déjà jouées.
- **c)** $14$ : on compte des couples ordonnés : chaque couple non rencontré est compté deux fois.

</details>

Avis : 

---

## 13. `cqc-matrices-et-applications-lineaires-tle-ti-moyenne-2` (séries BAC:TI)

**Remarque du relecteur :** Le sens (direct) de la rotation est implicite ; préciser « dans le sens direct » serait plus rigoureux.

**Énoncé :**

Dans la commande numérique d'une machine-outil, on programme une rotation vectorielle d'angle $\dfrac{\pi}{3}$ dans le plan de travail. Quelle est la matrice $R$ de cette rotation dans la base canonique $(\vec\imath,\vec\jmath)$ ?

- a) $\begin{pmatrix}\dfrac12&\dfrac{\sqrt3}{2}\\-\dfrac{\sqrt3}{2}&\dfrac12\end{pmatrix}$
- b) $\begin{pmatrix}\dfrac12&-\dfrac{\sqrt3}{2}\\\dfrac{\sqrt3}{2}&\dfrac12\end{pmatrix}$
- c) $\begin{pmatrix}\dfrac{\sqrt3}{2}&-\dfrac12\\\dfrac12&\dfrac{\sqrt3}{2}\end{pmatrix}$
- d) $\begin{pmatrix}\dfrac12&\dfrac{\sqrt3}{2}\\\dfrac{\sqrt3}{2}&\dfrac12\end{pmatrix}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
La rotation vectorielle d'angle $\theta$ transforme $\vec\imath$ en le vecteur de coordonnées $(\cos\theta\,;\,\sin\theta)$, et $\vec\jmath$ en le vecteur de coordonnées $(-\sin\theta\,;\,\cos\theta)$. Sa matrice dans la base canonique $(\vec\imath,\vec\jmath)$ est donc, de façon générale :
$$R_\theta=\begin{pmatrix}\cos\theta&-\sin\theta\\\sin\theta&\cos\theta\end{pmatrix}$$

### Corrigé
Pour $\theta=\dfrac{\pi}{3}$, on a $\cos\dfrac{\pi}{3}=\dfrac12$ et $\sin\dfrac{\pi}{3}=\dfrac{\sqrt3}{2}$. En remplaçant dans la formule générale :
$$R=\begin{pmatrix}\dfrac12&-\dfrac{\sqrt3}{2}\\[4pt]\dfrac{\sqrt3}{2}&\dfrac12\end{pmatrix}$$

**Vérification.** Le déterminant d'une matrice de rotation doit toujours valoir $1$ :
$$\det(R)=\dfrac12\times\dfrac12-\left(-\dfrac{\sqrt3}{2}\right)\times\dfrac{\sqrt3}{2}=\dfrac14+\dfrac34=1$$
Le résultat est conforme : $R$ est bien une matrice de rotation.

$$\boxed{R=\begin{pmatrix}\dfrac12&-\dfrac{\sqrt3}{2}\\[4pt]\dfrac{\sqrt3}{2}&\dfrac12\end{pmatrix}}$$

### Pourquoi les autres réponses sont fausses

- **a)** $\begin{pmatrix}\dfrac12&\dfrac{\sqrt3}{2}\\-\dfrac{\sqrt3}{2}&\dfrac12\end{pmatrix}$ : les signes sont inversés : on obtient la rotation d'angle $-\frac{\pi}{3}$.
- **c)** $\begin{pmatrix}\dfrac{\sqrt3}{2}&-\dfrac12\\\dfrac12&\dfrac{\sqrt3}{2}\end{pmatrix}$ : le cosinus et le sinus sont échangés : on obtient la rotation d'angle $\frac{\pi}{6}$.
- **d)** $\begin{pmatrix}\dfrac12&\dfrac{\sqrt3}{2}\\\dfrac{\sqrt3}{2}&\dfrac12\end{pmatrix}$ : la structure de la matrice d'une rotation est mal retenue : le signe $-$ du coefficient en haut à droite est oublié.

</details>

Avis : 

---

## 14. `cqc-matrices-et-applications-lineaires-tle-ti-moyenne-4` (séries BAC:TI)

**Remarque du relecteur :** VOCABULAIRE : le contexte du « capteur qui perd de l'information » est artificiel ; un énoncé purement matriciel serait plus net.

**Énoncé :**

Un capteur optique de positionnement applique, dans le plan de mesure, une transformation linéaire $f$ dont la matrice dans la base canonique $(\vec\imath,\vec\jmath)$ dépend d'un paramètre de réglage réel $m$ :
$$M(m)=\begin{pmatrix}m&2\\3&m-1\end{pmatrix}$$
Le capteur perd de l'information (deux positions distinctes peuvent alors renvoyer la même mesure) exactement lorsque $f$ n'est pas bijective. Pour quelles valeurs de $m$ l'application $f$ n'est-elle pas bijective ?

- a) $m=-2$ ou $m=3$
- b) $m=2$ ou $m=-3$
- c) Aucune valeur de $m$
- d) $m=\sqrt7$ ou $m=-\sqrt7$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Une application linéaire $f$ du plan vectoriel dans lui-même, de matrice $M$, est bijective si et seulement si $\det(M)\neq0$. Elle n'est donc pas bijective si et seulement si $\det(M)=0$.

### Corrigé
$$\det\big(M(m)\big)=m\times(m-1)-2\times3=m^2-m-6$$

On cherche les valeurs de $m$ pour lesquelles ce déterminant s'annule :
$$m^2-m-6=0$$

Le discriminant de ce trinôme est $\Delta=(-1)^2-4\times1\times(-6)=1+24=25=5^2$. Les racines sont :
$$m_1=\dfrac{1-5}{2}=-2 \qquad m_2=\dfrac{1+5}{2}=3$$

Donc $m^2-m-6=(m+2)(m-3)$, qui s'annule si et seulement si $m=-2$ ou $m=3$.

**Vérification pour $m=3$.** $M(3)=\begin{pmatrix}3&2\\3&2\end{pmatrix}$ : les deux lignes sont identiques, donc $\det=3\times2-2\times3=0$. Conforme.

**Vérification pour $m=-2$.** $M(-2)=\begin{pmatrix}-2&2\\3&-3\end{pmatrix}$ : $\det=(-2)\times(-3)-2\times3=6-6=0$. Conforme.

$$\boxed{f\ \text{n'est pas bijective si et seulement si}\ m=-2\ \text{ou}\ m=3}$$

### Pourquoi les autres réponses sont fausses
- **b)** Les racines de $m^2-m-6$ sont prises avec le signe opposé : $m=2$ et $m=-3$ donnent $\det=-4$ et $\det=6$, pas $0$.
- **c)** Le déterminant est calculé avec $+2\times3$ au lieu de $-2\times3$ : $m^2-m+6$ a un discriminant négatif, d'où la fausse conclusion qu'il n'y a aucune valeur.
- **d)** Le produit $m(m-1)$ est développé en $m^2-1$ : on obtient $m^2-7=0$, ce qui est faux.

</details>

Avis : 

---

## 15. `cqc-nombres-complexes-approche-algebrique-tle-ce-faible-1` (séries BAC:C BAC:E)

**Remarque du relecteur :** VOCABULAIRE : pour une équation dans C, l'inconnue se note plutôt z que x.

**Énoncé :**

Quel est l'ensemble des solutions dans $\mathbb{C}$ de l'équation $x^2-6x+13=0$, écrites sous forme algébrique ?

- a) $\{3-4i\,;\,3+4i\}$
- b) $\{-3-2i\,;\,-3+2i\}$
- c) $\{3-2i\,;\,3+2i\}$
- d) $\{6-4i\,;\,6+4i\}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour résoudre dans $\mathbb{C}$ une équation du second degré à coefficients réels dont le discriminant $\Delta$ est strictement négatif, on détermine une racine carrée complexe $\delta$ de $\Delta$ (purement imaginaire, $\delta^2=\Delta$), puis on applique la même formule des racines $x=\dfrac{-b\pm\delta}{2a}$ que dans le cas d'un discriminant positif.

### Corrigé

Le discriminant de l'équation est :
$$\Delta = (-6)^2 - 4\times1\times13 = 36 - 52 = -16$$

Comme $\Delta < 0$, l'équation n'a pas de solution réelle mais admet deux solutions complexes conjuguées. Une racine carrée complexe de $\Delta$ est $\delta = 4i$ (car $(4i)^2 = 16i^2 = -16 = \Delta$).

Les solutions sont :
$$x_1 = \dfrac{6 - 4i}{2} = 3 - 2i \qquad x_2 = \dfrac{6+4i}{2}=3+2i$$

$$\boxed{S = \{3-2i;\ 3+2i\}}$$

### Pourquoi les autres réponses sont fausses
- **a)** La partie imaginaire $\delta=4i$ n'est pas divisée par $2a=2$ (seule la partie réelle l'est).
- **b)** Le signe de $-b$ est oublié : on écrit $-6$ au lieu de $+6$ au numérateur.
- **d)** Le numérateur $6\pm4i$ n'est pas divisé par $2a=2$.

</details>

Avis : 

---

## 16. `cqc-nombres-complexes-approche-algebrique-tle-ce-moyenne-2` (séries BAC:C BAC:E)

**Énoncé :**

Quel est le nombre complexe $z$, écrit sous forme algébrique, qui vérifie $z+2\bar z=9+i$ ?

- a) $z=3+i$
- b) $z=3-i$
- c) $z=3+\dfrac13\,i$
- d) $z=9-i$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour résoudre une équation reliant un complexe $z$ à son conjugué $\bar z$, on pose $z=x+iy$ avec $x,y$ réels, on exprime $\bar z=x-iy$, on développe l'égalité, puis on identifie séparément les parties réelle et imaginaire des deux membres pour obtenir un système linéaire en $x$ et $y$.

### Corrigé

Posons $z = x + iy$ avec $x, y \in \mathbb{R}$, de sorte que $\bar z = x - iy$. Alors :
$$z + 2\bar z = (x+iy) + 2(x-iy) = 3x - iy$$

L'égalité $3x - iy = 9+i$ entraîne, par identification des parties réelle et imaginaire :
$$3x = 9 \quad\text{et}\quad -y = 1$$
$$x = 3 \quad\text{et}\quad y = -1$$

**Vérification** : $\bar z = 3+i$, donc $z+2\bar z = (3-i)+2(3+i) = 3-i+6+2i = 9+i$.

$$\boxed{z = 3 - i}$$

### Pourquoi les autres réponses sont fausses
- **a)** La partie imaginaire de $2\bar z$ est comptée avec le mauvais signe, et l'égalité $-y=1$ est lue $y=1$.
- **c)** Le conjugué est mal appliqué : $z+2\bar z$ est calculé comme $3x+3iy$, d'où $y=\frac13$.
- **d)** L'équation $3x=9$ est résolue en $x=9$ (division par $3$ oubliée).

</details>

Avis : 

---

## 17. `cqc-nombres-complexes-approche-algebrique-tle-d-moyenne-2` (séries BAC:D BAC:TI)

**Remarque du relecteur :** VOCABULAIRE : inconnue complexe notée x plutôt que z, inhabituel.

**Énoncé :**

Quel est l'ensemble des solutions dans $\mathbb{C}$ de l'équation $x^2-4x+13=0$ ?

- a) $\{-2-3i\,;\,-2+3i\}$
- b) $\{4-6i\,;\,4+6i\}$
- c) $\{2-6i\,;\,2+6i\}$
- d) $\{2-3i\,;\,2+3i\}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour résoudre dans $\mathbb{C}$ une équation du second degré à coefficients réels dont le discriminant $\Delta$ est strictement négatif, on sait que l'équation n'admet pas de racine réelle, mais deux racines complexes conjuguées. On les obtient en remplaçant $\sqrt\Delta$ par $i\sqrt{|\Delta|}$ dans la formule usuelle $\dfrac{-b\pm\sqrt\Delta}{2a}$.

### Corrigé

Le discriminant de l'équation est :
$$\Delta = (-4)^2-4\times1\times13 = 16-52=-36$$

Comme $\Delta<0$, l'équation n'admet pas de solution réelle mais deux solutions complexes conjuguées. Une racine carrée complexe de $\Delta$ est $\delta=6i$ (car $(6i)^2=36i^2=-36=\Delta$).

Les solutions sont :
$$x_1=\dfrac{4-6i}{2}=2-3i \qquad x_2=\dfrac{4+6i}{2}=2+3i$$

$$\boxed{S=\{2-3i;\ 2+3i\}}$$

### Pourquoi les autres réponses sont fausses
- **a)** Le signe de $-b$ est oublié : la partie réelle devient $-2$ au lieu de $2$.
- **b)** Le numérateur $4\pm6i$ n'est pas divisé par $2a=2$.
- **c)** Seule la partie réelle est divisée par $2$ : la partie imaginaire $\delta=6i$ reste entière.

</details>

Avis : 

---

## 18. `cqc-primitives-dune-fonction-continue-sur-un-intervalle-tle-ce-faible-0` (séries BAC:C BAC:E)

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=6x^2-4x+7$. Quelle est la primitive $F$ de $f$ sur $\mathbb{R}$ telle que $F(0)=5$ ?

- a) $F(x)=2x^3-2x^2+7x$
- b) $F(x)=2x^3-2x^2+7x+5$
- c) $F(x)=6x^3-4x^2+7x+5$
- d) $F(x)=12x-4$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour déterminer les primitives d'une fonction polynôme, on primitive chaque monôme séparément : une primitive de $ax^n$ est $\dfrac{a}{n+1}x^{n+1}$. On obtient ainsi une famille de primitives dépendant d'une constante $C$, que l'on détermine ensuite grâce à la condition initiale $F(x_0)=y_0$ fournie par l'énoncé.

### Corrigé
Les primitives sur $\mathbb{R}$ d'une somme de fonctions puissances s'obtiennent en primitivant terme à terme : une primitive de $6x^2$ est $2x^3$, une primitive de $-4x$ est $-2x^2$, une primitive de $7$ est $7x$. Les primitives de $f$ sur $\mathbb{R}$ sont donc les fonctions :
$$F(x)=2x^3-2x^2+7x+C,\qquad C\in\mathbb{R}$$

La condition $F(0)=5$ donne $C=5$ (puisque $2\times0^3-2\times0^2+7\times0+C=C$).

$$\boxed{F(x)=2x^3-2x^2+7x+5}$$

**Vérification** : $F'(x)=6x^2-4x+7=f(x)$ pour tout $x$, et $F(0)=5$. Les deux conditions demandées sont satisfaites.

### Pourquoi les autres réponses sont fausses
- **a)** La constante est oubliée : cette fonction vérifie $F(0)=0$ et non $F(0)=5$.
- **c)** Les monômes sont primitivés sans diviser par le nouvel exposant : $6x^2$ donne $6x^3$ au lieu de $2x^3$.
- **d)** On dérive $f$ au lieu de la primitiver.

</details>

Avis : 

---

## 19. `cqc-probabilites-tle-a-elevee-5` (séries BAC:A)

**Remarque du relecteur :** VOCABULAIRE : la question se termine par un point au lieu d'un point d'interrogation.

**Énoncé :**

Une boîte contient $4$ boules blanches et $6$ boules noires, indiscernables au toucher. On tire successivement et sans remise deux boules de la boîte (à chaque tirage, chaque boule restant dans la boîte a la même chance d'être tirée).

Quelle est la probabilité que les deux boules tirées soient de couleurs différentes.

- a) $\dfrac{4}{15}$
- b) $\dfrac{12}{25}$
- c) $\dfrac{8}{15}$
- d) $\dfrac{2}{5}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour un tirage successif sans remise, on multiplie les probabilités à chaque étape (la seconde probabilité tenant compte du résultat du premier tirage) ; quand un événement peut se réaliser selon plusieurs ordres différents et incompatibles entre eux, on additionne les probabilités de chaque ordre.

### Corrigé
La boîte contient $4+6=10$ boules au premier tirage.

**Cas 1 : blanche puis noire.** La probabilité de tirer une boule blanche au premier tirage est $\dfrac{4}{10}$. Il reste alors $9$ boules dans la boîte, dont $6$ noires, donc la probabilité de tirer ensuite une boule noire est $\dfrac69$. La probabilité de cet enchaînement est :
$$\dfrac{4}{10}\times\dfrac69=\dfrac{24}{90}=\dfrac{4}{15}$$

**Cas 2 : noire puis blanche.** De même :
$$\dfrac{6}{10}\times\dfrac49=\dfrac{24}{90}=\dfrac{4}{15}$$

Ces deux cas sont incompatibles (on ne peut pas obtenir « blanche puis noire » et « noire puis blanche » lors du même tirage) et ils couvrent exactement l'événement « les deux boules sont de couleurs différentes », donc on additionne leurs probabilités :
$$P(\text{couleurs différentes})=\dfrac{4}{15}+\dfrac{4}{15}=\dfrac{8}{15}$$

Ainsi **$P(\text{couleurs différentes})=\dfrac{8}{15}$** (soit environ $0{,}53$).

### Pourquoi les autres réponses sont fausses

- **a)** on ne compte qu'un seul des deux ordres (blanche puis noire) et on oublie « noire puis blanche ».
- **b)** on utilise $\dfrac{4}{10}$ et $\dfrac{6}{10}$ aux deux tirages, comme si la boule était remise dans la boîte.
- **d)** c'est la probabilité que la première boule soit blanche, qui ne répond pas à la question.


</details>

Avis : 

---

## 20. `cqc-probabilites-tle-d-faible-1` (séries BAC:D BAC:TI)

**Énoncé :**

Un gardien de but s'entraîne à arrêter des tirs au but. Lors de cet entraînement, il arrête chaque tir avec une probabilité de $0{,}75$, indépendamment des tirs précédents. Il affronte $3$ tirs au but consécutifs.

Quelle est la probabilité qu'il arrête les $3$ tirs ?

- a) $\dfrac{3}{4}$
- b) $\dfrac{9}{16}$
- c) $\dfrac{27}{64}$
- d) $\dfrac{1}{64}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Lorsque plusieurs expériences sont indépendantes, la probabilité que tous les résultats souhaités se produisent simultanément est le produit des probabilités de chaque résultat pris isolément.

### Corrigé
Les $3$ tirs sont indépendants les uns des autres, et la probabilité d'arrêter un tir donné vaut $0{,}75=\dfrac{3}{4}$ à chaque fois. La probabilité d'arrêter les $3$ tirs est donc le produit des $3$ probabilités :
$$P=\left(\dfrac{3}{4}\right)^3=\dfrac{3\times3\times3}{4\times4\times4}=\dfrac{27}{64}$$

**La probabilité que le gardien arrête les $3$ tirs est $\dfrac{27}{64}$, soit $0{,}421875$ (environ $42{,}2\%$).**

### Pourquoi les autres réponses sont fausses

- **a)** c'est la probabilité d'arrêter un seul tir : on n'a pas tenu compte des $3$ tirs.
- **b)** c'est $\left(\dfrac34\right)^2$, la probabilité d'arrêter seulement $2$ tirs consécutifs.
- **d)** c'est $\left(\dfrac14\right)^3$, la probabilité de manquer les $3$ tirs (événement contraire).


</details>

Avis : 

---

## 21. `cqc-probabilites-tle-ti-elevee-0` (séries BAC:TI)

**Remarque du relecteur :** VOCABULAIRE : une « mesure de température codée 1, 2 ou 4 » et la somme des codes de deux capteurs n'ont pas de sens physique ; contexte artificiel.

**Énoncé :**

Deux capteurs de température identiques, installés sur deux lignes de production indépendantes, renvoient chacun une mesure codée $1$, $2$ ou $4$ (en unités de l'automate), avec les probabilités respectives $0{,}5$ ; $0{,}3$ et $0{,}2$. On note $Y$ la variable aléatoire égale à la somme des deux codes renvoyés par les deux capteurs.

Quelle est la probabilité que la somme des deux codes soit supérieure ou égale à $5$ ?

- a) $0{,}64$
- b) $0{,}32$
- c) $0{,}16$
- d) $0{,}36$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Les deux capteurs fonctionnant indépendamment, la probabilité d'un couple de mesures $(a,b)$ vaut $P(a)\times P(b)$. Plusieurs couples distincts pouvant donner la même somme, on liste systématiquement tous les couples possibles, on calcule leur probabilité, puis on regroupe ceux qui donnent la même valeur de $Y$.

### Corrigé
Notons $p_1=0{,}5$, $p_2=0{,}3$, $p_4=0{,}2$ les probabilités des codes $1$, $2$, $4$ pour un capteur. Les sommes supérieures ou égales à $5$ sont obtenues avec les couples $(1,4)$, $(4,1)$ (somme $5$), $(2,4)$, $(4,2)$ (somme $6$) et $(4,4)$ (somme $8$) :

$$P(Y=5)=2\times p_1p_4=2\times0{,}5\times0{,}2=0{,}20$$
$$P(Y=6)=2\times p_2p_4=2\times0{,}3\times0{,}2=0{,}12$$
$$P(Y=8)=p_4\times p_4=0{,}2\times0{,}2=0{,}04$$

$$P(Y\geqslant5)=0{,}20+0{,}12+0{,}04=0{,}36$$

**Vérification** : les autres sommes ont pour probabilités $P(Y=2)=0{,}25$, $P(Y=3)=0{,}30$, $P(Y=4)=0{,}09$, et $0{,}25+0{,}30+0{,}09+0{,}36=1$.

**$P(Y\geqslant5)=0{,}36$.**

### Pourquoi les autres réponses sont fausses

- **a)** c'est $P(Y\leqslant4)=0{,}25+0{,}30+0{,}09$, la probabilité de l'événement contraire.
- **b)** on a oublié la somme $8$ (couple $(4,4)$, probabilité $0{,}04$).
- **c)** c'est $P(Y>5)=0{,}12+0{,}04$ : on a pris l'inégalité stricte et omis la somme $5$.


</details>

Avis : 

---

## 22. `cqc-produit-vectoriel-tle-ce-moyenne-2` (séries BAC:C BAC:E)

**Remarque du relecteur :** Le contexte (dessinateur, mètres) est décoratif mais sans effet sur le calcul.

**Énoncé :**

Dans un repère orthonormé de l'espace $(O,\vec\imath,\vec\jmath,\vec k)$, un dessinateur industriel repère trois points d'ancrage d'une charpente métallique : $A(2;0;-1)$, $B(5;1;1)$ et $C(1;-2;-3)$, les coordonnées étant exprimées en mètres. Quelles sont les coordonnées de $\vec{AB}\wedge\vec{AC}$ ?

- a) $(-2;-4;5)$
- b) $(2;4;-5)$
- c) $(2;-4;-5)$
- d) $(-3;-2;-4)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Trois points $A$, $B$, $C$ sont alignés si et seulement si les vecteurs $\vec{AB}$ et $\vec{AC}$ sont colinéaires, ce qui équivaut à $\vec{AB}\wedge\vec{AC}=\vec 0$. Si ce produit vectoriel est non nul, les points ne sont pas alignés.

### Corrigé

**1. Vecteurs $\vec{AB}$ et $\vec{AC}$.**
$$\vec{AB}=B-A=(5-2;1-0;1-(-1))=(3;1;2)$$
$$\vec{AC}=C-A=(1-2;-2-0;-3-(-1))=(-1;-2;-2)$$

**2. Produit vectoriel.**
$$\vec{AB}\wedge\vec{AC}=\begin{pmatrix}1\times(-2)-2\times(-2)\\2\times(-1)-3\times(-2)\\3\times(-2)-1\times(-1)\end{pmatrix}=\begin{pmatrix}-2+4\\-2+6\\-6+1\end{pmatrix}=\begin{pmatrix}2\\4\\-5\end{pmatrix}$$

**$\vec{AB}\wedge\vec{AC}(2;4;-5)$.**

### Pourquoi les autres réponses sont fausses

- **a)** c'est $\vec{AC}\wedge\vec{AB}$ : l'ordre des vecteurs est inversé.
- **c)** erreur de signe sur la deuxième composante : elle vaut $2\times(-1)-3\times(-2)=-2+6=4$, et non $-4$.
- **d)** on a multiplié les coordonnées une à une (produit composante par composante), ce qui n'est pas le produit vectoriel.


</details>

Avis : 

---

## 23. `cqc-produit-vectoriel-tle-ce-moyenne-3` (séries BAC:C BAC:E)

**Remarque du relecteur :** VOCABULAIRE : la phrase « Pour deux points B et C distincts de A » est maladroite (B et C sont déjà donnés) ; écrire « On rappelle que l'aire du triangle ABC est... ».

**Énoncé :**

Dans l'espace muni d'un repère orthonormé $(O,\vec\imath,\vec\jmath,\vec k)$, on considère les points $A(1;0;0)$, $B(0;2;0)$ et $C(0;0;3)$, les coordonnées étant exprimées dans une même unité de longueur. Pour deux points $B$ et $C$ distincts de $A$, l'aire du triangle $ABC$ est donnée par $\mathcal{A}=\dfrac12\left\|\vec{AB}\wedge\vec{AC}\right\|$. Quelle est l'aire du triangle $ABC$ ?

- a) $\dfrac72$
- b) $7$
- c) $\dfrac{49}{2}$
- d) $\dfrac{11}{2}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

L'aire d'un triangle $ABC$ se déduit du produit vectoriel de deux de ses côtés issus d'un même sommet, par la formule $\mathcal{A}=\dfrac12\left\|\vec{AB}\wedge\vec{AC}\right\|$. On calcule donc d'abord les coordonnées de $\vec{AB}\wedge\vec{AC}$, puis la norme euclidienne de ce vecteur, avant de diviser le résultat par 2.

### Corrigé

**1. Produit vectoriel.**
$$\vec{AB}=B-A=(-1;2;0)\qquad \vec{AC}=C-A=(-1;0;3)$$

$$\vec{AB}\wedge\vec{AC}=\begin{pmatrix}2\times3-0\times0\\0\times(-1)-(-1)\times3\\(-1)\times0-2\times(-1)\end{pmatrix}=\begin{pmatrix}6-0\\0+3\\0+2\end{pmatrix}=\begin{pmatrix}6\\3\\2\end{pmatrix}$$

**2. Aire du triangle $ABC$.** La norme du produit vectoriel est :
$$\left\|\vec{AB}\wedge\vec{AC}\right\|=\sqrt{6^2+3^2+2^2}=\sqrt{36+9+4}=\sqrt{49}=7$$

D'où :
$$\mathcal{A}=\dfrac12\times7=\dfrac72=3{,}5$$

**L'aire du triangle $ABC$ est $\dfrac72$ (soit $3{,}5$) unités d'aire.**

### Pourquoi les autres réponses sont fausses

- **b)** on a oublié le facteur $\dfrac12$ de la formule : $7$ est l'aire du parallélogramme construit sur $\vec{AB}$ et $\vec{AC}$.
- **c)** on a oublié la racine carrée : $49=\left\|\vec{AB}\wedge\vec{AC}\right\|^2$ et non la norme.
- **d)** on a additionné les coordonnées $6+3+2=11$ au lieu de calculer la norme $\sqrt{6^2+3^2+2^2}$.


</details>

Avis : 

---

## 24. `cqc-similitudes-directes-du-plan-tle-d-moyenne-0` (séries BAC:D BAC:TI)

**Remarque du relecteur :** LIMITE : vérifier que les similitudes directes figurent bien au programme de Terminale D.

**Énoncé :**

Soit $s$ une similitude directe du plan telle que $s(A)=C$ et $s(B)=D$, où $A$, $B$, $C$, $D$ ont pour affixes respectives $z_A=-1$, $z_B=1$, $z_C=2$, $z_D=2+4i$. Quelle est l'écriture complexe de $s$ ?

- a) $z'=2iz+2-2i$
- b) $z'=4iz+2+4i$
- c) $z'=-2iz+2-2i$
- d) $z'=2iz+2+2i$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

L'écriture complexe d'une similitude directe est $z'=az+b$. Chaque relation $s(P)=P'$ donne $az_P+b=z_{P'}$ ; on soustrait les deux équations pour éliminer $b$, puis on reporte pour trouver $b$.

### Corrigé

$s(A)=C$ donne $-a+b=2$ et $s(B)=D$ donne $a+b=2+4i$.

En soustrayant : $2a=4i$, donc $a=2i$. Puis $b=(2+4i)-2i=2+2i$.

**L'écriture complexe de $s$ est $z'=2iz+2+2i$.**

Contrôle : $s(A)=-2i+2+2i=2=z_C$ et $s(B)=2i+2+2i=2+4i=z_D$.

### Pourquoi les autres réponses sont fausses

- **a)** $z'=2iz+2-2i$ : une erreur de signe sur $b$ : de $-a+b=2$ on tire $b=2+a=2+2i$.
- **b)** $z'=4iz+2+4i$ : la différence $4i$ n'a pas été divisée par $z_B-z_A=2$.
- **c)** $z'=-2iz+2-2i$ : la soustraction a été faite dans le mauvais ordre, ce qui donne $a=-2i$.

</details>

Avis : 

---

## 25. `cqc-similitudes-du-plan-tle-ti-elevee-5` (séries BAC:TI)

**Remarque du relecteur :** LIMITE : similitude indirecte, notion surtout traitée en C/E, à confirmer au programme TI.

**Énoncé :**

Le plan complexe est muni d'un repère orthonormé direct $(O;\vec u,\vec v)$. On considère la similitude plane indirecte $\sigma$ qui, à tout point $M$ d'affixe $z$, associe le point $M'$ d'affixe $z'=(1-i\sqrt3)\,\bar z+4$. Quelle est l'affixe de l'unique point invariant $\Omega$ de $\sigma$ (point tel que $\sigma(\Omega)=\Omega$) ?

- a) $-\dfrac{4\sqrt3}{3}\,i$
- b) $-\dfrac83-\dfrac{4\sqrt3}{3}\,i$
- c) $-\dfrac83+\dfrac{4\sqrt3}{3}\,i$
- d) $\dfrac{4\sqrt3}{3}-\dfrac83\,i$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Une transformation d'écriture $z'=a\bar z+b$ avec $a\in\mathbb C^*$ est une similitude plane indirecte. Pour chercher un point invariant, on pose $z=x+iy$ avec $x,y$ réels, on remplace $\bar z$ par $x-iy$ et on identifie parties réelle et imaginaire : la formule $\dfrac{b}{1-a}$ des similitudes directes ne s'applique pas ici.

### Corrigé

On cherche $z=x+iy$ tel que $z=(1-i\sqrt3)(x-iy)+4$. Or
$$(1-i\sqrt3)(x-iy)=(x-\sqrt3y)+i(-y-\sqrt3x)$$

L'identification donne :
$$x=x-\sqrt3y+4\quad\text{(I)}\qquad y=-y-\sqrt3x\quad\text{(II)}$$

De (I) : $y=\dfrac4{\sqrt3}=\dfrac{4\sqrt3}3$. De (II) : $x=-\dfrac{2y}{\sqrt3}=-\dfrac{2}{\sqrt3}\times\dfrac{4\sqrt3}{3}=-\dfrac83$.

**Le point invariant est $\Omega$ d'affixe $-\dfrac83+\dfrac{4\sqrt3}{3}\,i$.**

Contrôle : $(1-i\sqrt3)\left(-\dfrac83-\dfrac{4\sqrt3}3i\right)+4=-\dfrac{20}3+\dfrac{4\sqrt3}3i+4=-\dfrac83+\dfrac{4\sqrt3}3i$.

### Pourquoi les autres réponses sont fausses

- **a)** $-\dfrac{4\sqrt3}{3}\,i$ : on a utilisé la formule $\dfrac{b}{1-a}$ des similitudes directes, valable seulement pour $z'=az+b$.
- **b)** $-\dfrac83-\dfrac{4\sqrt3}{3}\,i$ : le signe de la partie imaginaire est faux : de (I), $y=+\dfrac{4}{\sqrt3}$.
- **d)** $\dfrac{4\sqrt3}{3}-\dfrac83\,i$ : les valeurs de $x$ et de $y$ ont été échangées lors de l'écriture de l'affixe.

</details>

Avis : 

---

## 26. `cqc-similitudes-du-plan-tle-ti-faible-0` (séries BAC:TI)

**Remarque du relecteur :** LIMITE : vérifier que les similitudes directes figurent bien au programme de Terminale TI.

**Énoncé :**

Une similitude plane directe $s$ a pour écriture complexe $z' = (\sqrt{3}+i)\,z - 2i$. Quel est le rapport de $s$ et une mesure de son angle ?

- a) rapport $4$ et angle $\dfrac{\pi}{6}$
- b) rapport $2$ et angle $\dfrac{\pi}{3}$
- c) rapport $2$ et angle $-\dfrac{\pi}{6}$
- d) rapport $2$ et angle $\dfrac{\pi}{6}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une similitude plane directe d'écriture $z'=az+b$ (avec $a\in\mathbb{C}^*$), le rapport est le module $|a|$ et une mesure de l'angle est un argument de $a$.

### Corrigé

Ici $a=\sqrt3+i$.

**Rapport.** $|a|=\sqrt{(\sqrt3)^2+1^2}=\sqrt4=2$.

**Angle.** $\cos\theta=\dfrac{\sqrt3}{2}$ et $\sin\theta=\dfrac12$, ce qui donne $\theta=\dfrac{\pi}{6}$.

**$s$ a pour rapport $2$ et pour angle $\dfrac\pi6$** (à $2\pi$ près).

### Pourquoi les autres réponses sont fausses

- **a)** rapport $4$ et angle $\dfrac{\pi}{6}$ : le rapport est $|a|=2$ ; $4$ est le carré du module.
- **b)** rapport $2$ et angle $\dfrac{\pi}{3}$ : cosinus et sinus ont été échangés.
- **c)** rapport $2$ et angle $-\dfrac{\pi}{6}$ : le signe de l'angle est faux : la partie imaginaire de $a$ est positive, donc l'argument aussi.

</details>

Avis : 

---

## 27. `cqc-similitudes-du-plan-tle-ti-faible-1` (séries BAC:TI)

**Énoncé :**

Un atelier de dessin technique agrandit un plan à l'aide d'une similitude plane. Un segment de $4\ \text{cm}$ sur le plan d'origine est représenté par un segment de $10\ \text{cm}$ sur l'agrandissement. Un cercle de rayon $3{,}5\ \text{cm}$ sur le plan d'origine a pour image, par cette même similitude, un cercle. Quel est son rayon ?

- a) $8{,}75\ \text{cm}$
- b) $1{,}4\ \text{cm}$
- c) $9{,}5\ \text{cm}$
- d) $35\ \text{cm}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Une similitude plane de rapport $k$ multiplie toutes les longueurs par $k$ : le rapport se lit en comparant une longueur et son image, et l'image d'un cercle de rayon $r$ est un cercle de rayon $k\times r$.

### Corrigé

Le segment de $4\ \text{cm}$ devient un segment de $10\ \text{cm}$, donc $k=\dfrac{10}{4}=2{,}5$.

Le rayon image vaut $2{,}5\times3{,}5=8{,}75\ \text{cm}$.

**Le cercle image a pour rayon $8{,}75\ \text{cm}$.**

### Pourquoi les autres réponses sont fausses

- **b)** $1{,}4\ \text{cm}$ : le rapport a été inversé : on a multiplié par $\dfrac{4}{10}$ au lieu de $\dfrac{10}{4}$.
- **c)** $9{,}5\ \text{cm}$ : on a ajouté l'écart de $6\ \text{cm}$ au lieu de multiplier par le rapport.
- **d)** $35\ \text{cm}$ : on a multiplié par $10$, la longueur image, au lieu du rapport $2{,}5$.

</details>

Avis : 

---

## 28. `cqc-statistiques-tle-d-moyenne-1` (séries BAC:D BAC:TI)

**Énoncé :**

Une pépinière forestière a mesuré la taille de $50$ jeunes plants d'eucalyptus (en cm), regroupée dans le tableau de classes suivant :

| Taille (cm) | $[10;20[$ | $[20;30[$ | $[30;40[$ | $[40;50[$ |
|---|---|---|---|---|
| Effectif $n_i$ | 8 | 20 | 16 | 6 |

En prenant le centre de chaque classe comme valeur représentative, quelle est la valeur exacte de l'écart-type $\sigma$ de cette série ?

- a) $80\ \text{cm}$
- b) $4\sqrt5\ \text{cm}$
- c) $5\sqrt5\ \text{cm}$
- d) $\sqrt{921}\ \text{cm}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une série groupée en classes, chaque classe est représentée par son centre. On calcule $\bar x=\dfrac1n\sum n_ix_i$, puis $V(x)=\dfrac1n\sum n_ix_i^2-\bar x^2$ et $\sigma=\sqrt{V(x)}$.

### Corrigé

Centres : $15$, $25$, $35$, $45$ ; effectif total $n=50$.

$\sum n_ix_i=120+500+560+270=1\,450$, donc $\bar x=29$.

$\sum n_ix_i^2=1\,800+12\,500+19\,600+12\,150=46\,050$, donc $V(x)=\dfrac{46\,050}{50}-29^2=921-841=80$.

$$\sigma=\sqrt{80}=4\sqrt5\approx8{,}94$$

**L'écart-type vaut $4\sqrt5\ \text{cm}$** (environ $8{,}94\ \text{cm}$).

### Pourquoi les autres réponses sont fausses

- **a)** $80\ \text{cm}$ : on a donné la variance, sans prendre la racine carrée.
- **c)** $5\sqrt5\ \text{cm}$ : les effectifs ont été ignorés : les quatre centres ont été traités comme s'ils avaient tous le même poids.
- **d)** $\sqrt{921}\ \text{cm}$ : on a oublié de retrancher le carré de la moyenne : $V(x)=\dfrac1n\sum n_ix_i^2-\bar x^2$.

</details>

Avis : 

---

## 29. `cqc-suites-numeriques-tle-ce-moyenne-2` (séries BAC:C BAC:E)

**Énoncé :**

Un chercheur modélise l'évolution du nombre de poissons (en milliers d'individus) dans un lac artificiel par la suite $(p_n)$ définie par $p_0 = 2$ et, pour tout entier naturel $n$ :
$$p_{n+1} = 0{,}5\,p_n + 3$$

Quelle est l'expression de $p_n$ en fonction de $n$ ?

- a) $p_n = 6 + 4\times(0{,}5)^n$
- b) $p_n = 2\times(0{,}5)^n + 3$
- c) $p_n = 6 - 2\times(0{,}5)^n$
- d) $p_n = 6 - 4\times(0{,}5)^n$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Face à une suite définie par une récurrence affine $u_{n+1} = au_n + b$ avec $a \neq 1$, on introduit une suite auxiliaire $v_n = u_n - \ell$, où $\ell = \dfrac{b}{1-a}$ est le point fixe de la relation, pour se ramener à une suite géométrique de raison $a$. On calcule $v_{n+1}$ en fonction de $v_n$ pour établir cette nature avant d'en déduire l'expression explicite de $u_n$.

### Corrigé

**a) Nature de $(q_n)$.** Pour tout entier naturel $n$ :
$$q_{n+1} = p_{n+1} - 6 = (0{,}5\,p_n + 3) - 6 = 0{,}5\,p_n - 3 = 0{,}5\,(p_n - 6) = 0{,}5\,q_n$$

Le rapport $\dfrac{q_{n+1}}{q_n} = 0{,}5$ est constant : $(q_n)$ est donc une **suite géométrique de raison $0{,}5$**, de premier terme :
$$q_0 = p_0 - 6 = 2 - 6 = -4$$

**b) Expression de $p_n$.** Pour une suite géométrique de premier terme $q_0$ et de raison $0{,}5$, on a $q_n = q_0 \times (0{,}5)^n$ pour tout $n \in \mathbb{N}$ :
$$q_n = -4 \times (0{,}5)^n$$

Comme $p_n = q_n + 6$, on obtient :
$$p_n = 6 - 4 \times (0{,}5)^n$$

*Vérification* : pour $n = 0$, $p_0 = 6 - 4 \times 1 = 2$, conforme à la donnée. Pour $n = 1$, $p_1 = 6 - 4 \times 0{,}5 = 6 - 2 = 4$, ce qui correspond bien à $p_1 = 0{,}5 \times 2 + 3 = 4$ calculé directement à partir de la relation de récurrence.

**c) Convergence et limite.** Comme $-1 < 0{,}5 < 1$, on a $\displaystyle\lim_{n \to +\infty}(0{,}5)^n = 0$, donc :
$$\lim_{n \to +\infty} p_n = 6 - 4 \times 0 = 6$$

**Interprétation** : la suite $(p_n)$ converge vers $6$. Dans le contexte de l'exercice, la population de poissons du lac tend à se stabiliser autour de $6\,000$ individus sur le long terme, quel que soit l'effectif initial observé.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur le premier terme de la suite auxiliaire $q_n=p_n-6$ (on a pris $q_0=+4$ au lieu de $-4$).
- **b)** On a ajouté la constante $3$ à une suite géométrique de premier terme $p_0$ : la relation de récurrence ne se résout pas ainsi.
- **c)** Mauvais premier terme : on a pris $q_0=-p_0$ au lieu de $q_0=p_0-6$.

</details>

Avis : 

---

## 30. `cqc-theorie-des-graphes-tle-ce-faible-0` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : vérifier que la notion de graphe et de degré figure au programme de Terminale C et E.

**Énoncé :**

On considère un graphe simple non orienté $G$ dont l'ensemble des sommets est $\{A, B, C, D, E\}$ et dont l'ensemble des arêtes est $\{AB, AC, AD, BC, CD, DE\}$ (chaque paire de lettres désigne une arête unique reliant les deux sommets correspondants, sans orientation ni arête multiple).

Quels sont les degrés des sommets $A$, $B$, $C$, $D$, $E$, dans cet ordre ?

- a) $3\,;\,2\,;\,3\,;\,2\,;\,1$
- b) $2\,;\,2\,;\,2\,;\,3\,;\,1$
- c) $3\,;\,2\,;\,3\,;\,3\,;\,1$
- d) $3\,;\,2\,;\,3\,;\,3\,;\,2$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un graphe simple non orienté, l'ordre désigne le nombre de sommets, et le degré d'un sommet est le nombre d'arêtes qui lui sont incidentes. Le lemme des poignées de main affirme que la somme des degrés de tous les sommets est toujours égale au double du nombre d'arêtes, puisque chaque arête est comptée une fois à chacune de ses deux extrémités.

### Corrigé

**1. Ordre de $G$.** L'ordre d'un graphe est son nombre de sommets. Ici $G$ possède les cinq sommets $A$, $B$, $C$, $D$, $E$, donc l'ordre de $G$ est $5$.

**2. Degré de chaque sommet.** Le degré d'un sommet est le nombre d'arêtes qui lui sont incidentes. En reprenant la liste des arêtes $\{AB, AC, AD, BC, CD, DE\}$ :

| Sommet | Arêtes incidentes | Degré |
|---|---|---|
| $A$ | $AB$, $AC$, $AD$ | $3$ |
| $B$ | $AB$, $BC$ | $2$ |
| $C$ | $AC$, $BC$, $CD$ | $3$ |
| $D$ | $AD$, $CD$, $DE$ | $3$ |
| $E$ | $DE$ | $1$ |

**3. Vérification de la relation somme des degrés = 2 × nombre d'arêtes.**

Somme des degrés :
$$3+2+3+3+1=12$$

Le graphe $G$ possède $6$ arêtes ($AB$, $AC$, $AD$, $BC$, $CD$, $DE$), donc :
$$2\times6=12$$

On retrouve bien la même valeur : $12=12$. La relation est vérifiée, ce qui est cohérent avec le théorème (parfois appelé « lemme des poignées de main ») selon lequel, dans tout graphe, la somme des degrés des sommets est égale au double du nombre d'arêtes, chaque arête étant comptée deux fois (une fois pour chacune de ses deux extrémités).

### Pourquoi les autres réponses sont fausses

- **a)** L'arête $DE$ n'a été comptée que pour $E$ : chaque arête compte pour ses deux extrémités.
- **b)** L'arête $AC$ a été oubliée : elle compte pour $A$ et pour $C$.
- **d)** L'arête $DE$ a été comptée deux fois pour $E$.

</details>

Avis : 

---

## 31. `cqc-theorie-des-graphes-tle-ce-moyenne-2` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : la théorie des graphes (chaînes) n'est pas présente dans tous les programmes de Terminale C/E d'Afrique francophone ; vérifier qu'elle figure au programme visé.

**Énoncé :**

Une société de messagerie exploite quatre centres de tri, notés $A$, $B$, $C$, $D$. On modélise son réseau par un graphe simple non orienté $G$ dont les sommets sont ces quatre centres et dont les arêtes, correspondant aux liaisons routières directement exploitées entre deux centres, sont : $AB$, $AC$, $BC$, $BD$, $CD$ (il n'existe aucune autre liaison directe que celles-ci).

Combien existe-t-il de chaînes de longueur $2$ reliant $A$ à $D$ dans $G$ ?

- a) $2$
- b) $1$
- c) $3$
- d) $0$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Une chaîne de longueur $2$ reliant deux sommets passe par exactement un sommet intermédiaire, relié à chacun des deux par une arête. On énumère donc les sommets adjacents à la fois au départ et à l'arrivée.

### Corrigé

Les voisins de $A$ sont $B$ et $C$ ; les voisins de $D$ sont $B$ et $C$. Les sommets intermédiaires possibles sont donc $B$ et $C$ :
- $A-B-D$ (arêtes $AB$ puis $BD$) ;
- $A-C-D$ (arêtes $AC$ puis $CD$).

Il y a exactement $2$ chaînes de longueur $2$ reliant $A$ à $D$.

### Pourquoi les autres réponses sont fausses

- **b)** Une des deux chaînes a été oubliée : $A-B-D$ et $A-C-D$ sont toutes deux valides.
- **c)** On a compté la chaîne $A-B-C-D$, qui est de longueur $3$ et non $2$.
- **d)** $A$ et $D$ ne sont pas reliés directement, mais ils le sont par un sommet intermédiaire.

</details>

Avis : 

---

## 32. `cqc-theorie-des-graphes-tle-ce-moyenne-3` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : nombre chromatique d'un graphe, à confirmer au programme de Terminale C et E.

**Énoncé :**

Un établissement scolaire doit programmer les épreuves de $5$ matières - Mathématiques ($M$), Physique ($P$), Anglais ($A$), Français ($F$) et Histoire ($H$) - sur des créneaux horaires d'examen. Deux matières ne peuvent pas être programmées sur le même créneau si un même groupe d'élèves les prépare toutes les deux (on dit alors qu'elles sont « en conflit »). On modélise la situation par un graphe simple non orienté $G$ dont les sommets sont les cinq matières et dont les arêtes relient deux matières en conflit. Les arêtes de $G$ sont exactement : $MP$, $MA$, $PA$, $PF$, $AF$, $FH$ (il n'existe aucune autre paire de matières en conflit).

Quel est le nombre chromatique de $G$, c'est-à-dire le nombre minimal de créneaux nécessaires ?

- a) $2$
- b) $4$
- c) $5$
- d) $3$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Colorer un graphe consiste à attribuer une couleur à chaque sommet de sorte que deux sommets reliés par une arête reçoivent toujours des couleurs différentes ; le nombre chromatique est le plus petit nombre de couleurs permettant une telle coloration. Un sous-graphe complet à $k$ sommets (une clique, où tous les sommets sont reliés deux à deux) impose à lui seul $k$ couleurs distinctes, ce qui fournit une minoration du nombre chromatique ; exhiber ensuite une coloration effective utilisant ce nombre de couleurs permet d'établir la valeur exacte.

### Corrigé

**1. Minoration du nombre chromatique.** Les arêtes $MP$, $MA$ et $PA$ sont toutes les trois présentes dans $G$ : les sommets $M$, $P$, $A$ sont donc reliés deux à deux, ils forment un sous-graphe complet à $3$ sommets (un « triangle »). Dans un tel triangle, les trois sommets doivent nécessairement recevoir trois couleurs (créneaux) deux à deux distinctes, puisque chacun est en conflit avec les deux autres. Colorer $G$ demande donc au moins $3$ couleurs : le nombre chromatique de $G$ est supérieur ou égal à $3$.

**2. Coloration explicite en $3$ créneaux.** On propose :

| Créneau | Matières |
|---|---|
| $1$ | $M$, $F$ |
| $2$ | $P$, $H$ |
| $3$ | $A$ |

Vérifions qu'aucune arête de $G$ ne relie deux matières d'un même créneau :
- Créneau $1$ ($M$, $F$) : $MF$ n'est **pas** une arête de $G$ - pas de conflit.
- Créneau $2$ ($P$, $H$) : $PH$ n'est **pas** une arête de $G$ - pas de conflit.
- Créneau $3$ ($A$ seul) : pas de conflit possible.
- Vérification des arêtes existantes : $MP$ (créneaux $1\ne2$ ), $MA$ ($1\ne3$ ), $PA$ ($2\ne3$ ), $PF$ ($2\ne1$ ), $AF$ ($3\ne1$ ), $FH$ ($1\ne2$ ). Les six arêtes relient bien à chaque fois deux créneaux différents.

Cette répartition en $3$ créneaux est donc valide. Combinée à la minoration de la question 1 (au moins $3$ créneaux nécessaires), on conclut que le nombre chromatique de $G$ vaut exactement :
$$\boxed{\chi(G)=3}$$

### Pourquoi les autres réponses sont fausses

- **a)** Le triangle $M$, $P$, $A$ (trois matières deux à deux en conflit) interdit de se contenter de deux créneaux.
- **b)** On a pris le degré maximal augmenté de $1$ ($3+1$) : cette borne est valable mais pas minimale ; une coloration en $3$ créneaux existe.
- **c)** On a attribué un créneau différent à chaque matière : c'est possible mais loin d'être minimal.

</details>

Avis : 

---

## 33. `cqc-calcul-integral-elevee-5` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** Série A : le calcul exige une intégration par parties (ou une primitive de x ln x non usuelle), hors du programme léger de Terminale A ; à retirer de la série A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Calculer, en donnant la valeur exacte, l'intégrale $M = \displaystyle\int_{1}^{\mathrm{e}} x\ln x\,\mathrm{d}x$.

Quelle est la valeur de $M$ ?

- a) $\dfrac{\mathrm{e}^{2}-1}{4}$
- b) $\dfrac{\mathrm{e}^{2}}{4}$
- c) $\dfrac{\mathrm{e}^{2}+1}{2}$
- d) $\dfrac{\mathrm{e}^{2}+1}{4}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand l'intégrande contient un logarithme, l'intégration par parties s'impose en posant $u = \ln x$ : c'est le seul choix qui fasse **disparaître** le logarithme, puisque $u' = \dfrac{1}{x}$. Le prendre pour $v'$ conduirait au contraire à devoir primitiver $\ln x$, c'est-à-dire à un problème plus difficile que celui de départ.

### Corrigé

**Étape 1 - choix des fonctions.**

$$u(x) = \ln x \quad \Longrightarrow \quad u'(x) = \frac{1}{x}$$
$$v'(x) = x \quad \Longrightarrow \quad v(x) = \frac{x^{2}}{2}$$

Sur $[1\,;\mathrm{e}]$, on a $x > 0$ : les deux fonctions sont dérivables à dérivées continues.

**Étape 2 - application de la formule.**

$$M = \left[\frac{x^{2}}{2}\ln x\right]_{1}^{\mathrm{e}} - \int_{1}^{\mathrm{e}} \frac{x^{2}}{2} \times \frac{1}{x}\,\mathrm{d}x$$

**Étape 3 - terme tout intégré.** Avec $\ln \mathrm{e} = 1$ et $\ln 1 = 0$ :

$$\left[\frac{x^{2}}{2}\ln x\right]_{1}^{\mathrm{e}} = \frac{\mathrm{e}^{2}}{2} \times 1 - \frac{1}{2} \times 0 = \frac{\mathrm{e}^{2}}{2}$$

**Étape 4 - intégrale restante.** La simplification $\dfrac{x^2}{2} \times \dfrac{1}{x} = \dfrac{x}{2}$ est le bénéfice du choix fait à l'étape 1 :

$$\int_{1}^{\mathrm{e}} \frac{x}{2}\,\mathrm{d}x = \left[\frac{x^{2}}{4}\right]_{1}^{\mathrm{e}} = \frac{\mathrm{e}^{2}}{4} - \frac{1}{4}$$

**Étape 5 - conclusion.**

$$M = \frac{\mathrm{e}^{2}}{2} - \left(\frac{\mathrm{e}^{2}}{4} - \frac{1}{4}\right) = \frac{2\mathrm{e}^{2}}{4} - \frac{\mathrm{e}^{2}}{4} + \frac{1}{4}$$

$$\boxed{M = \frac{\mathrm{e}^{2} + 1}{4}}$$

**Vérification numérique.** $\mathrm{e}^2 \approx 7{,}39$, donc $M \approx \dfrac{8{,}39}{4} \approx 2{,}10$. Sur $[1\,;\mathrm{e}]$, la fonction $x \mapsto x\ln x$ croît de $0$ à $\mathrm{e} \approx 2{,}72$, sur un intervalle de longueur $\mathrm{e}-1 \approx 1{,}72$ : une aire d'environ $2{,}1$ est cohérente.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur la borne inférieure : le terme $-\left(-\dfrac14\right)$ vaut $+\dfrac14$.
- **b)** Oubli de la contribution de la borne inférieure $x=1$ dans l'intégrale restante.
- **c)** Mauvaise primitive de $\dfrac{x}{2}$ : on a pris $\dfrac{x^2}{2}$ au lieu de $\dfrac{x^2}{4}$.

</details>

Avis : 

---

## 34. `cqc-calcul-integral-faible-0` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI)

**Remarque du relecteur :** LIMITE : la série A figure dans les séries ; le calcul d'intégrale n'est pas cité dans le programme léger de A (seules les primitives le sont), à confirmer par l'enseignant.

**Énoncé :**

Quelle est la valeur de l'intégrale $I = \displaystyle\int_{0}^{2}\left(3x^2 - 2x\right)\mathrm{d}x$ ?

- a) $12$
- b) $0$
- c) $4$
- d) $8$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour calculer une intégrale définie, on détermine d'abord une primitive $F$ de la fonction intégrée, puis on applique $\displaystyle\int_a^b f(x)\,\mathrm{d}x = F(b) - F(a)$. La constante d'intégration est inutile ici : elle se simplifie dans la soustraction, ce qui permet de choisir la primitive la plus simple.

### Corrigé

**Étape 1 - primitive.** En primitivant terme à terme :

$$F(x) = 3 \times \frac{x^3}{3} - 2 \times \frac{x^2}{2} = x^3 - x^2$$

**Étape 2 - évaluation aux bornes.**

$$I = \left[x^3 - x^2\right]_{0}^{2} = \left(2^3 - 2^2\right) - \left(0^3 - 0^2\right)$$

$$I = (8 - 4) - 0 = 4$$

**Conclusion.**

$$\boxed{I = 4}$$

**Contrôle de vraisemblance.** Sur $[0\,;2]$, la fonction $x \mapsto 3x^2-2x$ s'annule en $0$ et en $\dfrac{2}{3}$, est négative entre les deux puis positive ensuite. La partie positive l'emporte largement, donc un résultat positif était attendu.

### Pourquoi les autres réponses sont fausses

- **a)** On a évalué la dérivée $6x-2$ aux bornes au lieu d'une primitive.
- **b)** Mauvaise primitive de $2x$ : on a pris $2x^2$ au lieu de $x^2$, d'où $2^3-2\times2^2=0$.
- **d)** Oubli du terme $-2x$ : seule la primitive $x^3$ de $3x^2$ a été utilisée.

</details>

Avis : 

---

## 35. `cqc-calcul-integral-faible-1` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI)

**Remarque du relecteur :** LIMITE : la série A est indiquée ; vérifier que le calcul d'intégrale (et pas seulement de primitive) est au programme de Terminale A.

**Énoncé :**

Quelle est la valeur de l'intégrale $J = \displaystyle\int_{1}^{\mathrm{e}} \frac{3}{x}\,\mathrm{d}x$ ?

- a) $3(\mathrm{e}-1)$
- b) $3$
- c) $3-\dfrac{3}{\mathrm{e}}$
- d) $0$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Une primitive de $\dfrac{1}{x}$ sur $]0\,;+\infty[$ est $\ln x$. Un facteur constant se sort de l'intégrale sans précaution, et les deux valeurs $\ln 1 = 0$ et $\ln \mathrm{e} = 1$ sont à connaître par cœur : ce sont elles qui rendent ce type de calcul immédiat.

### Corrigé

**Étape 1 - sortir la constante.**

$$J = 3\int_{1}^{\mathrm{e}} \frac{1}{x}\,\mathrm{d}x$$

**Étape 2 - primitive.** Sur $[1\,;\mathrm{e}]$, on a $x > 0$, donc une primitive de $\dfrac{1}{x}$ est $\ln x$ (sans valeur absolue).

$$J = 3\left[\ln x\right]_{1}^{\mathrm{e}} = 3\left(\ln \mathrm{e} - \ln 1\right)$$

**Étape 3 - valeurs remarquables.** $\ln \mathrm{e} = 1$ et $\ln 1 = 0$, donc

$$J = 3(1 - 0) = 3$$

**Conclusion.**

$$\boxed{J = 3}$$

### Pourquoi les autres réponses sont fausses

- **a)** On a primitivé $\dfrac{3}{x}$ comme la constante $3$, en oubliant le logarithme.
- **c)** On a pris $-\dfrac{1}{x}$ pour primitive de $\dfrac{1}{x}$ (c'est la dérivée de $\dfrac{1}{x}$ au signe près).
- **d)** Confusion des valeurs $\ln\mathrm{e}=1$ et $\ln 1=0$ : on a obtenu $3\times(1-1)$.

</details>

Avis : 

---

## 36. `cqc-calcul-integral-moyenne-2` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** L'intégration par parties (et le calcul intégral) n'est pas au programme de Terminale A : retirer la série BAC:A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

À l'aide d'une intégration par parties, calculer $K = \displaystyle\int_{0}^{1} x\,\mathrm{e}^{x}\,\mathrm{d}x$.

Quelle est la valeur de $K$ ?

- a) $1$
- b) $\mathrm{e}$
- c) $\mathrm{e}-1$
- d) $2\mathrm{e}-1$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

L'intégration par parties repose sur $\displaystyle\int_a^b u(x)v'(x)\,\mathrm{d}x = \left[u(x)v(x)\right]_a^b - \int_a^b u'(x)v(x)\,\mathrm{d}x$. On choisit pour $u$ le facteur qui **se simplifie en dérivant** (ici le polynôme, dont la dérivée est constante) et pour $v'$ celui dont on sait primitiver, sans quoi l'intégrale restante serait plus compliquée que celle de départ.

### Corrigé

**Étape 1 - choix des fonctions.**

$$u(x) = x \quad \Longrightarrow \quad u'(x) = 1$$
$$v'(x) = \mathrm{e}^{x} \quad \Longrightarrow \quad v(x) = \mathrm{e}^{x}$$

Les deux fonctions sont dérivables, de dérivées continues sur $[0\,;1]$ : la formule s'applique.

**Étape 2 - application de la formule.**

$$K = \left[x\,\mathrm{e}^{x}\right]_{0}^{1} - \int_{0}^{1} 1 \times \mathrm{e}^{x}\,\mathrm{d}x$$

**Étape 3 - calcul du terme tout intégré.**

$$\left[x\,\mathrm{e}^{x}\right]_{0}^{1} = 1 \times \mathrm{e}^{1} - 0 \times \mathrm{e}^{0} = \mathrm{e}$$

**Étape 4 - calcul de l'intégrale restante.**

$$\int_{0}^{1} \mathrm{e}^{x}\,\mathrm{d}x = \left[\mathrm{e}^{x}\right]_{0}^{1} = \mathrm{e} - 1$$

**Étape 5 - conclusion.**

$$K = \mathrm{e} - (\mathrm{e} - 1) = 1$$

$$\boxed{K = 1}$$

**Contrôle de vraisemblance.** Sur $[0\,;1]$, la fonction $x \mapsto x\mathrm{e}^x$ varie de $0$ à $\mathrm{e} \approx 2{,}72$ en croissant. L'aire sous la courbe est donc comprise entre $0$ et $\mathrm{e}$ : la valeur $1$ est plausible.

### Pourquoi les autres réponses sont fausses

- **b)** Oubli de l'intégrale restante : on n'a gardé que le terme tout intégré $\left[x\mathrm{e}^x\right]_0^1$.
- **c)** On a pris pour résultat l'intégrale restante $\int_0^1\mathrm{e}^x\,\mathrm{d}x$ seule, sans le terme tout intégré.
- **d)** Erreur de signe devant l'intégrale restante : la formule est $\left[uv\right]-\int u'v$, pas $\left[uv\right]+\int u'v$.

</details>

Avis : 

---

## 37. `cqc-calcul-integral-moyenne-3` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** La série BAC:A est indiquée : les fonctions trigonométriques et leurs primitives (forme u'u^n avec cos) ne sont pas au programme de Terminale A ; retirer A, sans problème pour C, D, E, TI.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Quelle est la valeur de l'intégrale $L = \displaystyle\int_{0}^{\frac{\pi}{2}} \sin x\,\cos^{2} x\,\mathrm{d}x$ ?

- a) $-\dfrac{1}{3}$
- b) $1$
- c) $\dfrac{1}{2}$
- d) $\dfrac{1}{3}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand l'intégrande est de la forme $u'(x)\left[u(x)\right]^{n}$, on reconnaît directement la primitive $\dfrac{\left[u(x)\right]^{n+1}}{n+1}$, sans linéarisation ni changement de variable explicite. Le signe est le point délicat : la dérivée de $\cos x$ vaut $-\sin x$, il faut donc faire apparaître ce signe moins.

### Corrigé

**Étape 1 - reconnaître la forme.** Posons $u(x) = \cos x$. Alors $u'(x) = -\sin x$, donc

$$\sin x\,\cos^{2} x = -\left(-\sin x\right)\cos^{2}x = -\,u'(x)\left[u(x)\right]^{2}$$

**Étape 2 - primitive.** Une primitive de $u'u^{2}$ est $\dfrac{u^{3}}{3}$, donc une primitive de $-u'u^{2}$ est $-\dfrac{u^{3}}{3}$ :

$$F(x) = -\frac{\cos^{3} x}{3}$$

**Étape 3 - évaluation aux bornes.** Avec $\cos\dfrac{\pi}{2} = 0$ et $\cos 0 = 1$ :

$$L = \left[-\frac{\cos^{3}x}{3}\right]_{0}^{\frac{\pi}{2}} = -\frac{0^{3}}{3} - \left(-\frac{1^{3}}{3}\right) = 0 + \frac{1}{3}$$

**Conclusion.**

$$\boxed{L = \frac{1}{3}}$$

**Contrôle de signe.** Sur $\left[0\,;\dfrac{\pi}{2}\right]$, $\sin x \geq 0$ et $\cos^2 x \geq 0$ : l'intégrande est positive, l'intégrale doit donc l'être aussi. Un résultat négatif aurait signalé une erreur de signe à l'étape 1.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe : la primitive est $-\dfrac{\cos^3 x}{3}$ (et non $\dfrac{\cos^3 x}{3}$), car $(\cos x)'=-\sin x$.
- **b)** Oubli du facteur $\dfrac13$ de la primitive d'une puissance $u'u^2$.
- **c)** On a calculé $\int_0^{\pi/2}\sin x\cos x\,\mathrm{d}x$, en oubliant la puissance $2$ de $\cos x$.

</details>

Avis : 

---

## 38. `cqc-composition-de-transformations-elevee-5` (séries BAC:C BAC:D)

**Énoncé :**

Dans le plan complexe, on considère les transformations $f : z \longmapsto 2z + 1$ et $g : z \longmapsto iz$.

La transformation $g \circ f$ admet un unique point invariant, d'affixe $\omega$. Que vaut $\omega$ ?

- a) $\omega = \dfrac{1+2i}{5}$
- b) $\omega = \dfrac{2+i}{5}$
- c) $\omega = \dfrac{-2+i}{5}$
- d) $\omega = \dfrac{2-i}{5}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une transformation $z' = az + b$ avec $a \neq 1$, la nature se lit sur $a$ - module pour le rapport, argument pour l'angle - et le centre s'obtient en résolvant $z = az+b$, soit $z = \dfrac{b}{1-a}$. Comparer deux composées demande de mener ce travail **deux fois** : des transformations de même nature peuvent différer par leur centre.

### Corrigé

**1. Écritures complexes.**

Pour $f \circ g$, c'est $g$ qui agit d'abord :

$$z \longmapsto iz \longmapsto 2(iz) + 1 = 2iz + 1$$

Pour $g \circ f$, c'est $f$ qui agit d'abord :

$$z \longmapsto 2z+1 \longmapsto i(2z+1) = 2iz + i$$

**2. Nature et éléments caractéristiques.**

Dans les deux cas, le coefficient de $z$ vaut $a = 2i$, de module

$$|2i| = 2$$

et d'argument $\arg(2i) = \dfrac{\pi}{2}$. Les deux composées sont donc des **similitudes directes de rapport $2$ et d'angle $\dfrac{\pi}{2}$**.

*Centre de $f \circ g$* :

$$z = 2iz + 1 \quad \Longrightarrow \quad z(1 - 2i) = 1 \quad \Longrightarrow \quad z = \frac{1}{1-2i} = \frac{1+2i}{(1-2i)(1+2i)} = \frac{1+2i}{5}$$

*Centre de $g \circ f$* :

$$z = 2iz + i \quad \Longrightarrow \quad z(1-2i) = i \quad \Longrightarrow \quad z = \frac{i(1+2i)}{5} = \frac{i + 2i^{2}}{5} = \frac{-2+i}{5}$$

**3. Comparaison.**

Les deux composées ont **le même rapport et le même angle**, mais des **centres distincts** :

$$\omega_1 = \frac{1+2i}{5} = \frac{1}{5} + \frac{2}{5}i \qquad \text{contre} \qquad \omega_2 = \frac{-2+i}{5} = -\frac{2}{5} + \frac{1}{5}i$$

Donc $f \circ g \neq g \circ f$ : **la composition n'est pas commutative**.

**Pourquoi les rapports et angles coïncident.** Le coefficient de $z$ dans une composée est le **produit** des coefficients, et la multiplication des complexes est commutative : $2 \times i = i \times 2$. Rapport et angle sont donc nécessairement identiques dans les deux ordres. En revanche, le terme constant, lui, dépend de l'ordre - et c'est lui qui fixe le centre.

**Ce qu'il faut en retenir.** Deux transformations peuvent avoir exactement les mêmes « caractéristiques métriques » sans être égales : l'emplacement du centre les distingue. C'est pourquoi une réponse du type « similitude de rapport 2 et d'angle $\dfrac{\pi}{2}$ » reste incomplète tant que le centre n'est pas précisé.

### Pourquoi les autres réponses sont fausses

- **a)** Ce point invariant est celui de $f\circ g$ : l'ordre de composition a été inversé.
- **b)** Erreur de signe : on a résolu $z=-2iz+i$ au lieu de $z=2iz+i$.
- **d)** Erreur de signe sur le terme constant : on a résolu $z=2iz-i$ au lieu de $z=2iz+i$.

</details>

Avis : 

---

## 39. `cqc-demi-tour-moyenne-3` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : composition d'isométries de l'espace (demi-tours), à vérifier selon le programme C/E en vigueur.

**Énoncé :**

L'espace est rapporté à un repère orthonormé. On note $r_1$ le demi-tour d'axe $(Ox)$ et $r_2$ le demi-tour d'axe $(Oy)$.

Quelle est la nature de la composée $r_2 \circ r_1$ ?

- a) Le demi-tour d'axe $(Oz)$
- b) La symétrie centrale de centre $O$
- c) L'identité
- d) Le demi-tour d'axe $(Oy)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour identifier une composée donnée par des expressions analytiques, on applique successivement les deux transformations à un point quelconque et l'on identifie l'expression obtenue. Il faut respecter l'ordre : dans $r_2 \circ r_1$, c'est $r_1$ qui agit **en premier**.

### Corrigé

**Étape 1 - expressions analytiques des deux demi-tours.**

Le demi-tour d'axe $(Ox)$ conserve $x$ et change le signe des deux autres coordonnées :

$$r_1 : (x\,;y\,;z) \longmapsto (x\,;-y\,;-z)$$

De même, le demi-tour d'axe $(Oy)$ conserve $y$ :

$$r_2 : (x\,;y\,;z) \longmapsto (-x\,;y\,;-z)$$

**Étape 2 - composition.**

Soit $M(x\,;y\,;z)$. Appliquons d'abord $r_1$ :

$$M_1\,(x\,;-y\,;-z)$$

Puis $r_2$ à ce point - on change le signe de sa première et de sa troisième coordonnée :

$$M'\,\left(-x\,;\,-y\,;\,-(-z)\right) = (-x\,;-y\,;z)$$

**Étape 3 - identification.**

L'expression obtenue,

$$\begin{cases} x' = -x \\ y' = -y \\ z' = z \end{cases}$$

est exactement celle du demi-tour d'axe $(Oz)$ : deux coordonnées changent de signe, la troisième reste inchangée.

**Conclusion.**

$$\boxed{r_2 \circ r_1 = \text{demi-tour d'axe } (Oz)}$$

**Résultat général.** La composée de deux demi-tours d'axes **perpendiculaires et sécants** est le demi-tour autour de la perpendiculaire commune passant par leur point d'intersection. On retrouve ici ce résultat avec les trois axes du repère.

**Sur la commutativité.** Calculons $r_1 \circ r_2$ : $(x\,;y\,;z) \mapsto (-x\,;y\,;-z) \mapsto (-x\,;-y\,;z)$. On obtient le même résultat. Ces deux demi-tours **commutent** exceptionnellement, ce qui n'est pas le cas général de la composition de rotations - c'est une particularité des axes deux à deux perpendiculaires.

### Pourquoi les autres réponses sont fausses

- **b)** on trouve $(x\,;y\,;z)\mapsto(-x\,;-y\,;z)$ : la troisième coordonnée ne change pas de signe.
- **c)** on a cru que deux demi-tours se compensent ; cela n'est vrai que pour deux demi-tours de même axe.
- **d)** on a retenu l'axe du dernier demi-tour appliqué ; la composée fixe $(Oz)$, pas $(Oy)$.

</details>

Avis : 

---

## 40. `cqc-demi-tour-moyenne-4` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : demi-tour (rotation d'angle π) de l'espace, à vérifier au programme ; le point A(0;0;1) décrit simplement l'axe (Oz).

**Énoncé :**

L'espace est rapporté à un repère orthonormé. On considère le demi-tour $r$ d'axe la droite $(D)$ passant par le point $A(0\,;0\,;1)$ et de vecteur directeur $\vec{k}\,(0\,;0\,;1)$.

Quelle est l'image du point $B(3\,;4\,;7)$ par $r$ ?

- a) $B'(-3\,;-4\,;-7)$
- b) $B'(-3\,;-4\,;-5)$
- c) $B'(3\,;4\,;-7)$
- d) $B'(-3\,;-4\,;7)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsque l'axe est parallèle à un axe du repère sans lui être confondu, il reste dirigé par le même vecteur : le demi-tour agit donc de la même façon sur les coordonnées, **à condition que l'axe passe par l'origine du plan perpendiculaire**. Ici l'axe est la droite $x=0$, $y=0$ - c'est-à-dire $(Oz)$ lui-même, le point $A$ n'étant qu'un point particulier de cette droite.

### Corrigé

**Étape 1 - identifier l'axe.**

La droite $(D)$ passe par $A(0\,;0\,;1)$ et est dirigée par $\vec{k}\,(0\,;0\,;1)$. Ses points sont donc de la forme

$$(0\,;0\,;1+t), \quad t \in \mathbb{R}$$

c'est-à-dire tous les points de coordonnées $(0\,;0\,;z)$ avec $z$ quelconque : $(D)$ **est** l'axe $(Oz)$.

**Étape 2 - image de $B$.**

Le demi-tour d'axe $(Oz)$ change le signe des deux premières coordonnées :

$$B'(-3\,;-4\,;7)$$

**Étape 3 - distances à l'axe.**

La distance d'un point à l'axe $(Oz)$ est la distance de son projeté sur le plan $(xOy)$ à l'origine, soit $\sqrt{x^{2}+y^{2}}$.

Pour $B$ :

$$\sqrt{3^{2} + 4^{2}} = \sqrt{9+16} = \sqrt{25} = 5$$

Pour $B'$ :

$$\sqrt{(-3)^{2} + (-4)^{2}} = \sqrt{9+16} = 5$$

Les deux distances sont égales : la distance à l'axe est bien **conservée**.

**Pourquoi c'était prévisible.** Un demi-tour est une rotation, donc une isométrie qui laisse l'axe fixe point par point. Tout point décrit un cercle centré sur l'axe : son rayon, c'est-à-dire sa distance à l'axe, ne peut pas changer. La vérification numérique ne fait que confirmer une propriété structurelle.

**Le piège du point $A$.** Il était tentant de croire que l'axe, passant par $A(0\,;0\,;1)$, différait de $(Oz)$ et qu'il fallait translater les calculs. Vérifier la nature exacte de la droite avant de calculer évite ce détour inutile - et, dans un cas où l'axe serait réellement décalé, éviterait une erreur bien réelle.

### Pourquoi les autres réponses sont fausses

- **a)** c'est l'image par la symétrie centrale de centre $O$ ; un demi-tour laisse la cote inchangée.
- **b)** c'est l'image par la symétrie centrale de centre $A$ ; la droite $(D)$ est l'axe $(Oz)$ et la cote de $B$ ne change pas.
- **c)** on a changé le signe de la seule cote ; le demi-tour fixe la cote et change le signe des deux autres coordonnées.

</details>

Avis : 

---

## 41. `cqc-encadrement-elevee-5` (séries BAC:A BAC:C BAC:E)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** La série A est indiquée : suites d'intégrales hors programme de Terminale A (suites exclues). Correct pour C et E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Pour tout entier naturel $n$, on pose

$$I_n = \int_{0}^{1} x^{n}\,\mathrm{e}^{-x}\,\mathrm{d}x.$$

Quelle est la limite de $I_n$ quand $n$ tend vers $+\infty$ ?

- a) $1-\mathrm{e}^{-1}$
- b) $1$
- c) $0$
- d) $\mathrm{e}^{-1}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand une intégrale dépend d'un entier $n$ et qu'on ne sait pas la calculer, la méthode standard consiste à encadrer l'intégrande par des fonctions dont on connaît les primitives, à intégrer l'encadrement, puis à conclure par le **théorème des gendarmes** si les deux bornes ont la même limite.

### Corrigé

**1. Encadrement de l'intégrande.**

Sur $[0\,;1]$, on a $-1 \leq -x \leq 0$. La fonction exponentielle étant croissante :

$$\mathrm{e}^{-1} \leq \mathrm{e}^{-x} \leq \mathrm{e}^{0} = 1$$

En particulier $0 < \mathrm{e}^{-x} \leq 1$. Par ailleurs $x^{n} \geq 0$ sur $[0\,;1]$. En multipliant l'encadrement par $x^{n}$, qui est **positif** (le sens est donc conservé) :

$$0 \leq x^{n}\mathrm{e}^{-x} \leq x^{n}$$

**2. Encadrement de l'intégrale.**

L'intégration conservant l'ordre sur $[0\,;1]$ :

$$\int_{0}^{1} 0\,\mathrm{d}x \;\leq\; I_n \;\leq\; \int_{0}^{1} x^{n}\,\mathrm{d}x$$

La borne de gauche vaut $0$. Celle de droite se calcule :

$$\int_{0}^{1} x^{n}\,\mathrm{d}x = \left[\frac{x^{n+1}}{n+1}\right]_{0}^{1} = \frac{1}{n+1}$$

D'où

$$0 \leq I_n \leq \frac{1}{n+1}$$

**3. Limite.**

Quand $n \to +\infty$, $\dfrac{1}{n+1} \to 0$. La suite $(I_n)$ est encadrée par deux suites qui tendent toutes deux vers $0$ ; d'après le théorème des gendarmes :

$$\boxed{\lim_{n \to +\infty} I_n = 0}$$

**Interprétation.** Sur $[0\,;1]$, la fonction $x \mapsto x^{n}$ s'écrase vers $0$ partout sauf en $x = 1$ à mesure que $n$ grandit : l'aire sous la courbe s'annule à la limite. Le facteur $\mathrm{e}^{-x}$, borné entre $\mathrm{e}^{-1}$ et $1$, ne change rien à ce comportement - c'est précisément ce que l'encadrement de la question 1 permet d'affirmer sans calcul supplémentaire.

### Pourquoi les autres réponses sont fausses

- **a)** c'est la valeur de $I_0$ ; on a remplacé $x^n$ par $1$, alors que $x^n$ tend vers $0$ sur $[0\,;1[$.
- **b)** on a supposé que l'intégrande tend vers $1$ ; or $0\leq x^n\mathrm{e}^{-x}\leq x^n$ donne $I_n\leq\frac{1}{n+1}$.
- **d)** on a pris la valeur de l'intégrande en $x=1$ ; la limite de l'intégrale n'est pas la valeur à la borne.

</details>

Avis : 

---

## 42. `cqc-encadrement-moyenne-3` (séries BAC:A BAC:C BAC:E BAC:TI)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** Le calcul intégral et l'intégration d'un encadrement ne figurent pas au programme léger de la série A, qui est la plus faible des séries indiquées. Retirer BAC:A ; l'item convient pour C, E et TI.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On pose $I = \displaystyle\int_{0}^{1} \frac{x}{1+x}\,\mathrm{d}x$. On admet que, pour tout $x$ de $[0\,;1]$,

$$\frac{x}{2} \leq \frac{x}{1+x} \leq x.$$

Quel encadrement de $I$ obtient-on en intégrant cet encadrement entre $0$ et $1$ ?

- a) $\dfrac{1}{2} \leq I \leq 1$
- b) $\dfrac{1}{4} \leq I \leq \dfrac{1}{2}$
- c) $\dfrac{1}{3} \leq I \leq \dfrac{1}{2}$
- d) $\dfrac{1}{8} \leq I \leq \dfrac{1}{4}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

L'intégration **conserve l'ordre** : si $f \leq g$ sur $[a\,;b]$ avec $a < b$, alors $\displaystyle\int_a^b f \leq \int_a^b g$. C'est ce qui permet d'encadrer une intégrale que l'on ne sait pas - ou que l'on ne veut pas - calculer, à partir d'un encadrement de la fonction intégrée.

### Corrigé

**1. Encadrement de la fonction.**

Pour $x \in [0\,;1]$, on a $1 \leq 1+x \leq 2$, toutes ces quantités étant strictement positives. Le passage à l'inverse renverse l'ordre :

$$\frac{1}{2} \leq \frac{1}{1+x} \leq 1$$

Multiplions maintenant les trois membres par $x$, qui est **positif** sur $[0\,;1]$ - le sens des inégalités est donc conservé :

$$\frac{x}{2} \leq \frac{x}{1+x} \leq x$$

**2. Encadrement de l'intégrale.**

En intégrant cet encadrement entre $0$ et $1$ :

$$\int_{0}^{1}\frac{x}{2}\,\mathrm{d}x \;\leq\; I \;\leq\; \int_{0}^{1} x\,\mathrm{d}x$$

Calculons les deux intégrales encadrantes :

$$\int_{0}^{1}\frac{x}{2}\,\mathrm{d}x = \left[\frac{x^{2}}{4}\right]_{0}^{1} = \frac{1}{4} \qquad ; \qquad \int_{0}^{1} x\,\mathrm{d}x = \left[\frac{x^{2}}{2}\right]_{0}^{1} = \frac{1}{2}$$

**Conclusion.**

$$\boxed{\frac{1}{4} \leq I \leq \frac{1}{2}}$$

**Contrôle.** La valeur exacte est $I = \left[x - \ln(1+x)\right]_0^1 = 1 - \ln 2 \approx 0{,}307$, qui appartient bien à $\left[0{,}25\,;0{,}5\right]$. L'encadrement est correct, et suffisamment serré pour être utile.

**Point de vigilance.** La multiplication par $x$ à la question 1 n'est licite que parce que $x \geq 0$ sur l'intervalle considéré. Sur un intervalle contenant des valeurs négatives, il aurait fallu séparer les cas.

### Pourquoi les autres réponses sont fausses

- **a)** on a pris pour primitive de $x$ la fonction $x$ au lieu de $\frac{x^{2}}{2}$, ce qui double les deux bornes.
- **c)** la primitive de $\frac{x}{2}$ a été prise égale à $\frac{x^{2}}{3}$ au lieu de $\frac{x^{2}}{4}$.
- **d)** les deux bornes ont été divisées par $2$ une fois de trop (facteur $\frac12$ appliqué deux fois).

</details>

Avis : 

---

## 43. `cqc-encadrement-moyenne-4` (séries BAC:A BAC:C BAC:E BAC:TI)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** Les suites ne sont pas au programme de Terminale A : retirer la série BAC:A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $(u_n)$ la suite définie pour tout entier naturel $n$ par

$$u_n = \frac{3n+2}{n+1}.$$

Quelle affirmation est exacte ?

- a) La suite $(u_n)$ est strictement croissante et majorée par $3$ : elle converge vers $3$.
- b) La suite $(u_n)$ est décroissante et minorée par $2$ : elle converge vers $2$.
- c) La suite $(u_n)$ est bornée, mais comme elle n'atteint jamais $3$, elle diverge.
- d) La suite $(u_n)$ tend vers $+\infty$ car $3n+2$ tend vers $+\infty$.

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour encadrer une suite définie par un quotient, on met d'abord l'expression sous une forme où $n$ n'apparaît qu'une fois, par division du numérateur par le dénominateur. L'encadrement devient alors immédiat. Une suite bornée n'est pas nécessairement convergente : il faut lui adjoindre la **monotonie** pour conclure.

### Corrigé

**1. Encadrement.**

**Étape 1 - transformer l'écriture.** Écrivons le numérateur en fonction du dénominateur :

$$3n + 2 = 3(n+1) - 1$$

d'où

$$u_n = \frac{3(n+1) - 1}{n+1} = 3 - \frac{1}{n+1}$$

**Étape 2 - encadrer le terme variable.** Pour $n \geq 0$, on a $n + 1 \geq 1 > 0$, donc

$$0 < \frac{1}{n+1} \leq 1$$

**Étape 3 - conclure.** En multipliant par $-1$ (ce qui renverse l'ordre) puis en ajoutant $3$ :

$$-1 \leq -\frac{1}{n+1} < 0 \quad \Longrightarrow \quad 2 \leq 3 - \frac{1}{n+1} < 3$$

soit $2 \leq u_n < 3$ pour tout entier naturel $n$.

**2. Convergence.**

La suite est bornée, mais cela ne suffit pas à conclure. Étudions sa monotonie :

$$u_{n+1} - u_n = \left(3 - \frac{1}{n+2}\right) - \left(3 - \frac{1}{n+1}\right) = \frac{1}{n+1} - \frac{1}{n+2} = \frac{(n+2)-(n+1)}{(n+1)(n+2)} = \frac{1}{(n+1)(n+2)}$$

Cette différence est strictement positive : la suite est **strictement croissante**.

Étant croissante et majorée par $3$, la suite $(u_n)$ **converge** d'après le théorème de la convergence monotone. Sa limite se lit d'ailleurs directement sur l'écriture transformée : $\dfrac{1}{n+1} \to 0$, donc $u_n \to 3$.

**Remarque.** La borne $3$ n'est jamais atteinte, ce qui est cohérent avec l'inégalité **stricte** obtenue à la question 1 : c'est la limite, pas un maximum.

### Pourquoi les autres réponses sont fausses

- **b)** $2$ est le premier terme $u_0$ et non la limite ; la suite est croissante, car $u_{n+1}-u_n=\frac{1}{(n+1)(n+2)}>0$.
- **c)** une borne non atteinte n'empêche pas la convergence ; ici la limite est justement $3$.
- **d)** le dénominateur $n+1$ tend aussi vers $+\infty$ ; en écrivant $u_n=3-\frac{1}{n+1}$ on voit que la limite est finie.

</details>

Avis : 

---

## 44. `cqc-image-faible-0` (séries BAC:C BAC:E)

**Remarque du relecteur :** VOCABULAIRE : « endomorphisme de R^2 » et la notation Vect sont plutôt du supérieur ; un manuel de Terminale dirait « application linéaire du plan vectoriel » et « droite vectorielle dirigée par (1;2) ».

**Énoncé :**

Soit $f$ l'endomorphisme de $\mathbb{R}^{2}$ défini, pour tout vecteur $u = (x\,;y)$, par

$$f(u) = (x + y\,;\, 2x + 2y).$$

Quelle est l'image de $f$ ?

- a) $\operatorname{Vect}\{(1\,;-1)\}$
- b) $\operatorname{Vect}\{(1\,;2)\}$
- c) $\mathbb{R}^{2}$
- d) $\operatorname{Vect}\{(1\,;1)\}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

L'image d'une application linéaire est l'ensemble des vecteurs atteints : $\operatorname{Im} f = \{f(u)\}$. Elle est engendrée par les images des vecteurs d'une base de l'espace de départ ; il suffit donc de calculer ces images, puis d'en extraire une famille libre. Le rang est par définition la dimension de l'image.

### Corrigé

**Étape 1 - images des vecteurs de la base canonique.**

Soit $(e_1\,;e_2)$ la base canonique de $\mathbb{R}^{2}$, avec $e_1 = (1\,;0)$ et $e_2 = (0\,;1)$ :

$$f(e_1) = (1 + 0\,;\,2 + 0) = (1\,;2)$$
$$f(e_2) = (0 + 1\,;\,0 + 2) = (1\,;2)$$

**Étape 2 - famille génératrice.** L'image est engendrée par ces deux vecteurs :

$$\operatorname{Im} f = \operatorname{Vect}\left\{(1\,;2)\,;\,(1\,;2)\right\} = \operatorname{Vect}\left\{(1\,;2)\right\}$$

Les deux images étant **égales**, la famille se réduit à un seul vecteur.

**Étape 3 - base et rang.** Le vecteur $(1\,;2)$ est non nul, donc la famille $\left\{(1\,;2)\right\}$ est libre : c'est une base de $\operatorname{Im} f$.

$$\operatorname{rg}(f) = \dim\left(\operatorname{Im} f\right) = 1$$

**Contrôle par le théorème du rang.** $\dim \mathbb{R}^{2} = \dim\left(\operatorname{Ker} f\right) + \operatorname{rg}(f)$, soit $2 = \dim\left(\operatorname{Ker} f\right) + 1$, d'où $\dim\left(\operatorname{Ker} f\right) = 1$. On le vérifie directement : $f(u) = 0$ équivaut à $x + y = 0$, équation d'une droite vectorielle, de dimension $1$. Cohérent.

### Pourquoi les autres réponses sont fausses

- **a)** c'est le noyau de $f$ (solutions de $x+y=0$) et non son image.
- **c)** les images des vecteurs de base sont égales à $(1\,;2)$ : elles n'engendrent qu'une droite, le rang vaut $1$.
- **d)** on a lu les coefficients de la première ligne ; les images de la base canonique sont $(1\,;2)$.

</details>

Avis : 

---

## 45. `cqc-image-moyenne-3` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : noyau/image d'un endomorphisme de R³, haut du programme C/E.

**Énoncé :**

Soit $g$ l'endomorphisme de $\mathbb{R}^{3}$ défini, pour tout vecteur $u = (x\,;y\,;z)$, par

$$g(u) = (x - z\,;\, 0\,;\, x - z).$$

Quelle affirmation est exacte ?

- a) $\operatorname{Ker} g = \operatorname{Im} g$, ces deux sous-espaces étant de dimension $1$.
- b) $\operatorname{Ker} g \subset \operatorname{Im} g$, avec $\dim \operatorname{Ker} g=1$ et $\dim \operatorname{Im} g=2$.
- c) $\operatorname{Im} g \subset \operatorname{Ker} g$, avec $\dim \operatorname{Ker} g=2$ et $\dim \operatorname{Im} g=1$.
- d) $\operatorname{Ker} g$ et $\operatorname{Im} g$ sont supplémentaires dans $\mathbb{R}^{3}$.

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Le noyau se détermine en résolvant $g(u) = 0$, l'image en décrivant l'ensemble des vecteurs atteints. Comparer les deux exige de raisonner par **double inclusion**, ou d'exhiber pour chacun une base et de constater qu'elles engendrent le même sous-espace - l'égalité des dimensions ne suffit jamais à conclure à l'égalité des sous-espaces.

### Corrigé

**1. Noyau et image.**

**Noyau.** $g(u) = 0$ équivaut au système

$$\begin{cases} x - z = 0 \\ 0 = 0 \\ x - z = 0 \end{cases} \quad \Longleftrightarrow \quad x = z$$

Un vecteur du noyau s'écrit donc $(x\,;y\,;x)$ avec $x$ et $y$ quelconques, soit

$$u = x(1\,;0\,;1) + y(0\,;1\,;0)$$

$$\operatorname{Ker} g = \operatorname{Vect}\left\{(1\,;0\,;1)\,;\,(0\,;1\,;0)\right\}$$

Ces deux vecteurs sont non colinéaires, donc libres : $\dim\left(\operatorname{Ker} g\right) = 2$.

**Image.** Posons $t = x - z$. Quand $u$ décrit $\mathbb{R}^{3}$, le réel $t$ décrit $\mathbb{R}$ tout entier, et

$$g(u) = (t\,;0\,;t) = t\,(1\,;0\,;1)$$

$$\operatorname{Im} g = \operatorname{Vect}\left\{(1\,;0\,;1)\right\} \qquad \text{de dimension } 1$$

**2. Comparaison.**

Les dimensions diffèrent ($2$ contre $1$), donc les deux sous-espaces ne sont pas égaux. En revanche, le vecteur générateur de l'image, $(1\,;0\,;1)$, figure parmi les générateurs du noyau : on a l'inclusion stricte

$$\operatorname{Im} g \subsetneq \operatorname{Ker} g$$

**Interprétation.** Cette inclusion signifie que $g \circ g = 0$ : appliquer $g$ deux fois annule tout vecteur. Vérifions-le sur un vecteur quelconque - $g(u) = (t\,;0\,;t)$, dont l'image vaut $g(t\,;0\,;t) = (t - t\,;0\,;t-t) = (0\,;0\,;0)$. C'est bien le cas.

**Contrôle par le théorème du rang.** $\dim \mathbb{R}^{3} = 3 = \dim\left(\operatorname{Ker} g\right) + \operatorname{rg}(g) = 2 + 1$. Cohérent.

### Pourquoi les autres réponses sont fausses

- **a)** le noyau est le plan d'équation $x=z$, de dimension $2$ ; il contient strictement l'image.
- **b)** les dimensions sont inversées : $\dim\operatorname{Im}g=1$ et $\dim\operatorname{Ker}g=2$ (théorème du rang).
- **d)** $2+1=3$ ne suffit pas : leur intersection est $\operatorname{Im}g\neq\{0\}$ car $(1\,;0\,;1)$ est dans les deux.

</details>

Avis : 

---

## 46. `cqc-image-moyenne-4` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : noyau/image d'un endomorphisme de R^3, à la limite haute du programme de Terminale C/E.

**Énoncé :**

Soit $h$ l'endomorphisme de $\mathbb{R}^{3}$ défini, pour tout vecteur $u = (x\,;y\,;z)$, par

$$h(u) = (x + y\,;\, y + z\,;\, x - z).$$

Quelle famille est une base de $\operatorname{Im} h$ ?

- a) $\left((1\,;0\,;1)\,;\,(1\,;1\,;0)\,;\,(0\,;1\,;-1)\right)$
- b) $\left((1\,;0\,;1)\,;\,(1\,;1\,;0)\right)$
- c) $\left((1\,;-1\,;1)\right)$
- d) $\left((1\,;0\,;0)\,;\,(0\,;1\,;0)\,;\,(0\,;0\,;1)\right)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule les images des vecteurs de la base canonique : elles engendrent l'image. La famille obtenue n'étant pas toujours libre, il faut ensuite tester la liberté - et lorsqu'une relation de dépendance apparaît, elle indique précisément quel vecteur retirer pour obtenir une base.

### Corrigé

**Étape 1 - images de la base canonique.**

$$h(1\,;0\,;0) = (1\,;0\,;1) \qquad h(0\,;1\,;0) = (1\,;1\,;0) \qquad h(0\,;0\,;1) = (0\,;1\,;-1)$$

$$\operatorname{Im} h = \operatorname{Vect}\left\{(1\,;0\,;1)\,;\,(1\,;1\,;0)\,;\,(0\,;1\,;-1)\right\}$$

**Étape 2 - recherche d'une relation de dépendance.** Observons que

$$(1\,;1\,;0) - (1\,;0\,;1) = (0\,;1\,;-1)$$

Le troisième vecteur est donc la différence des deux premiers : la famille n'est **pas libre**, et le troisième vecteur est superflu.

$$\operatorname{Im} h = \operatorname{Vect}\left\{(1\,;0\,;1)\,;\,(1\,;1\,;0)\right\}$$

**Étape 3 - liberté des deux vecteurs restants.** Soient $a$ et $b$ réels tels que $a(1\,;0\,;1) + b(1\,;1\,;0) = (0\,;0\,;0)$. En écrivant composante par composante :

$$\begin{cases} a + b = 0 \\ b = 0 \\ a = 0 \end{cases}$$

D'où $a = b = 0$ : la famille est libre.

**Conclusion.** Une base de $\operatorname{Im} h$ est $\left\{(1\,;0\,;1)\,;\,(1\,;1\,;0)\right\}$, et

$$\operatorname{rg}(h) = 2$$

**Contrôle par le théorème du rang.** On doit avoir $\dim\left(\operatorname{Ker} h\right) = 3 - 2 = 1$. Résolvons $h(u) = 0$ : le système $x + y = 0$, $y + z = 0$, $x - z = 0$ donne $y = -x$, $z = -y = x$, et la troisième équation $x - z = 0$ est alors automatiquement satisfaite. Le noyau est donc $\operatorname{Vect}\left\{(1\,;-1\,;1)\right\}$, de dimension $1$. Cohérent.

### Pourquoi les autres réponses sont fausses

- **a)** ces trois vecteurs sont les images de la base canonique, mais ils sont liés : $(1\,;1\,;0)-(1\,;0\,;1)=(0\,;1\,;-1)$.
- **c)** ce vecteur engendre le noyau de $h$ ($h(1\,;-1\,;1)=0$), pas l'image.
- **d)** c'est la base canonique de l'espace de départ ; l'image est de dimension $2$ seulement.

</details>

Avis : 

---

## 47. `cqc-modelisation-faible-1` (séries BAC:A BAC:C BAC:E)

**Remarque du relecteur :** Question de niveau collège (système 2x2), très en dessous du BAC C et E.

**Énoncé :**

Un champ rectangulaire a un périmètre de $70\ \mathrm{m}$. Sa longueur dépasse sa largeur de $5\ \mathrm{m}$.

Quelle est l'aire du champ, en $\mathrm{m}^{2}$ ?

- a) $1\,218{,}75\ \mathrm{m}^{2}$
- b) $306{,}25\ \mathrm{m}^{2}$
- c) $300\ \mathrm{m}^{2}$
- d) $500\ \mathrm{m}^{2}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un problème géométrique, on traduit chaque donnée par une équation reliant les dimensions cherchées : le périmètre d'un rectangle vaut $2(L + \ell)$, et une phrase du type « dépasse de » se traduit par une différence. On vérifie toujours à la fin que les valeurs obtenues sont des longueurs **positives** et compatibles entre elles.

### Corrigé

**1. Dimensions.**

**Choix des inconnues.** Soit $\ell$ la largeur et $L$ la longueur, en mètres.

**Mise en équations.**

$$\begin{cases} 2(L + \ell) = 70 \\ L = \ell + 5 \end{cases}$$

La première équation se simplifie en $L + \ell = 35$.

**Résolution.** En reportant $L = \ell + 5$ :

$$(\ell + 5) + \ell = 35 \quad \Longrightarrow \quad 2\ell = 30 \quad \Longrightarrow \quad \ell = 15$$

Puis $L = 15 + 5 = 20$.

Le champ mesure donc $20\ \mathrm{m}$ de long et $15\ \mathrm{m}$ de large.

**2. Aire.**

$$\mathcal{A} = L \times \ell = 20 \times 15 = 300\ \mathrm{m}^{2}$$

**Vérification.** Périmètre : $2(20 + 15) = 70\ \mathrm{m}$. La longueur dépasse bien la largeur de $5\ \mathrm{m}$. Les deux dimensions sont positives, et la longueur est supérieure à la largeur, comme le veut le vocabulaire.

### Pourquoi les autres réponses sont fausses

- **a)** on a écrit $L+\ell=70$ au lieu de $2(L+\ell)=70$ (demi-périmètre oublié).
- **b)** on a ignoré l'écart de $5\ \mathrm{m}$ : champ carré de côté $17{,}5\ \mathrm{m}$.
- **d)** on a écrit le périmètre $2L+\ell=70$ (un côté compté une seule fois), d'où $L=25$ et $\ell=20$.

</details>

Avis : 

---

## 48. `cqc-modelisation-moyenne-3` (séries BAC:A BAC:C BAC:E)

**Remarque du relecteur :** Question de niveau collège pour des séries C et E.

**Énoncé :**

Dans une ville, un taxi facture une prise en charge fixe de $500$ FCFA, puis $150$ FCFA par kilomètre parcouru. Une compagnie concurrente ne facture aucune prise en charge, mais $200$ FCFA par kilomètre.

Pour quelle distance les deux compagnies facturent-elles le même montant ?

- a) $10\ \mathrm{km}$
- b) $\dfrac{5}{2}\ \mathrm{km}$
- c) $\dfrac{10}{3}\ \mathrm{km}$
- d) $\dfrac{10}{7}\ \mathrm{km}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Une tarification composée d'une part fixe et d'une part proportionnelle se modélise par une fonction **affine** $C(d) = a\,d + b$, où $b$ est la part fixe et $a$ le tarif unitaire. Comparer deux offres revient à comparer deux fonctions affines : on cherche d'abord leur point d'intersection, qui partage l'axe en deux zones où l'avantage change de camp.

### Corrigé

**1. Modélisation.**

Pour la première compagnie, au forfait de $500$ FCFA s'ajoutent $150$ FCFA par kilomètre :

$$C_1(d) = 150d + 500$$

Pour la seconde, sans part fixe :

$$C_2(d) = 200d$$

**2. Égalité des tarifs.**

$$C_1(d) = C_2(d) \iff 150d + 500 = 200d \iff 500 = 50d \iff d = 10$$

Les deux compagnies facturent le même montant pour un trajet de $10\ \mathrm{km}$ - soit $2\,000$ FCFA de part et d'autre.

**3. Trajet de 20 km.**

$$C_1(20) = 150 \times 20 + 500 = 3\,000 + 500 = 3\,500\ \text{FCFA}$$
$$C_2(20) = 200 \times 20 = 4\,000\ \text{FCFA}$$

La **première compagnie** est plus avantageuse pour ce trajet, avec une économie de $500$ FCFA.

**Interprétation générale.** Au-delà de $10\ \mathrm{km}$, la première compagnie est toujours moins chère : son tarif kilométrique plus faible finit par compenser sa prise en charge. En deçà, c'est l'inverse - pour un court trajet, le forfait pèse trop lourd. C'est le comportement typique de deux droites de pentes différentes : celle qui monte le moins vite finit par passer sous l'autre.

### Pourquoi les autres réponses sont fausses

- **b)** on a résolu $500=200\,d$ en oubliant le tarif kilométrique de la première compagnie.
- **c)** on a résolu $500=150\,d$ en oubliant le tarif kilométrique de la seconde compagnie.
- **d)** on a additionné les tarifs ($150+200$) au lieu de les soustraire : $500=350\,d$.

</details>

Avis : 

---

## 49. `cqc-nombres-complexes-elevee-5` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** Série A incluse : nombres complexes et similitudes hors programme de Terminale A ; retirer A des séries.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan complexe est muni d'un repère orthonormé direct. On considère la similitude directe $s$ qui, à tout point $M$ d'affixe $z$, associe le point $M'$ d'affixe

$$z' = \left(1 + i\sqrt{3}\right)z + 2.$$

Quelle est l'affixe du centre de $s$ ?

- a) $2$
- b) $-\dfrac{2\sqrt{3}}{3}\,i$
- c) $\dfrac{2\sqrt{3}}{3}\,i$
- d) $\dfrac{2\sqrt{3}}{3}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Toute transformation d'écriture $z' = az + b$ avec $a \neq 0$ et $a \neq 1$ est une **similitude directe** : son rapport est $|a|$, son angle $\arg(a)$, et son centre l'unique point invariant. Les cas particuliers se lisent sur $a$ : réel donne une homothétie, de module $1$ donne une rotation. On calcule donc toujours module et argument de $a$ **avant** de conclure.

### Corrigé

**Étape 1 - identification du coefficient.**

$$a = 1 + i\sqrt{3} \qquad ; \qquad b = 2$$

**Étape 2 - module de $a$ (le rapport).**

$$|a| = \sqrt{1^{2} + \left(\sqrt{3}\right)^{2}} = \sqrt{4} = 2$$

**Étape 3 - argument de $a$ (l'angle).** En factorisant par le module :

$$a = 2\left(\frac{1}{2} + i\frac{\sqrt{3}}{2}\right)$$

d'où $\cos\theta = \dfrac{1}{2}$ et $\sin\theta = \dfrac{\sqrt{3}}{2}$, donc $\arg(a) = \dfrac{\pi}{3}$.

Comme $|a| = 2 \neq 1$ et que $a$ n'est pas réel, il s'agit d'une **similitude directe** qui n'est ni une rotation ni une homothétie.

**Étape 4 - centre (point invariant).** On résout $z = \left(1+i\sqrt{3}\right)z + 2$ :

$$z - \left(1+i\sqrt{3}\right)z = 2 \quad \Longrightarrow \quad z\left(1 - 1 - i\sqrt{3}\right) = 2 \quad \Longrightarrow \quad -i\sqrt{3}\,z = 2$$

$$z = \frac{2}{-i\sqrt{3}}$$

On multiplie numérateur et dénominateur par $i$ :

$$z = \frac{2i}{-i^{2}\sqrt{3}} = \frac{2i}{\sqrt{3}} = \frac{2\sqrt{3}}{3}\,i$$

**Conclusion.** $s$ est la similitude directe de centre $\Omega$ d'affixe $\omega = \dfrac{2\sqrt{3}}{3}i$, de rapport $2$ et d'angle $\dfrac{\pi}{3}$.

**Vérification du centre.** Calculons l'image de $\Omega$ :

$$\left(1+i\sqrt{3}\right) \times \frac{2i}{\sqrt{3}} + 2 = \frac{2i}{\sqrt{3}} + \frac{2i^{2}\sqrt{3}}{\sqrt{3}} + 2 = \frac{2i}{\sqrt{3}} - 2 + 2 = \frac{2i}{\sqrt{3}}$$

On retrouve bien $\omega$ : le point est invariant, le centre est correct.

**Piège à éviter.** Le coefficient $b = 2$ n'est **pas** l'affixe du centre. Confondre les deux est l'erreur la plus fréquente : le centre se calcule toujours en résolvant l'équation du point invariant, jamais en lisant directement le terme constant.

### Pourquoi les autres réponses sont fausses

- **a)** on a lu le terme constant $b=2$ comme affixe du centre ; le centre est le point invariant, solution de $z=az+b$.
- **b)** erreur de signe en résolvant $-i\sqrt{3}\,z=2$ : on a $z=\frac{2}{-i\sqrt3}=\frac{2i}{\sqrt3}$.
- **d)** le facteur $i$ a été perdu : l'affixe du centre est imaginaire pure.

</details>

Avis : 

---

## 50. `cqc-nombres-complexes-faible-1` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** Série A incluse : les nombres complexes ne sont pas au programme de Terminale A ; retirer BAC:A des séries.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Quelle est la forme trigonométrique du nombre complexe $z = 1 + i\sqrt{3}$ ?

- a) $2\left(\cos\left(-\dfrac{\pi}{3}\right) + i\sin\left(-\dfrac{\pi}{3}\right)\right)$
- b) $2\left(\cos\dfrac{\pi}{3} + i\sin\dfrac{\pi}{3}\right)$
- c) $2\left(\cos\dfrac{\pi}{6} + i\sin\dfrac{\pi}{6}\right)$
- d) $4\left(\cos\dfrac{\pi}{3} + i\sin\dfrac{\pi}{3}\right)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La forme trigonométrique d'un complexe non nul s'écrit $z = r\left(\cos\theta + i\sin\theta\right)$ avec $r = |z|$. On calcule d'abord le module, puis on factorise par ce module : les deux nombres qui apparaissent alors entre parenthèses sont exactement $\cos\theta$ et $\sin\theta$, ce qui permet d'identifier $\theta$ sans ambiguïté - c'est le **couple** des deux valeurs qui détermine l'argument, jamais le cosinus seul.

### Corrigé

**Étape 1 - module.**

$$|z| = \sqrt{1^{2} + \left(\sqrt{3}\right)^{2}} = \sqrt{1 + 3} = \sqrt{4} = 2$$

**Étape 2 - factorisation par le module.**

$$z = 2\left(\frac{1}{2} + i\,\frac{\sqrt{3}}{2}\right)$$

**Étape 3 - identification de l'argument.** On cherche $\theta$ tel que

$$\cos\theta = \frac{1}{2} \qquad \text{et} \qquad \sin\theta = \frac{\sqrt{3}}{2}$$

Les deux valeurs étant positives, $\theta$ appartient au premier quadrant, et ces valeurs remarquables donnent $\theta = \dfrac{\pi}{3}$.

**Conclusion.**

$$\boxed{z = 2\left(\cos\frac{\pi}{3} + i\sin\frac{\pi}{3}\right)}$$

**Piège à éviter.** Se contenter de $\cos\theta = \dfrac{1}{2}$ laisserait deux possibilités, $\dfrac{\pi}{3}$ et $-\dfrac{\pi}{3}$. C'est le signe du sinus qui tranche : ici positif, donc $\theta = \dfrac{\pi}{3}$.

### Pourquoi les autres réponses sont fausses

- **a)** seul le cosinus a été regardé ; comme $\sin\theta=\frac{\sqrt3}{2}>0$, l'argument est $\frac{\pi}{3}$ et non $-\frac{\pi}{3}$.
- **c)** confusion entre $\cos\frac\pi3=\frac12$ et $\cos\frac\pi6=\frac{\sqrt3}{2}$ : les rôles de $1$ et $\sqrt3$ sont inversés.
- **d)** le module est $\sqrt{1+3}=2$ ; on a oublié la racine carrée en prenant $1^2+(\sqrt3)^2=4$.

</details>

Avis : 

---

## 51. `cqc-nombres-complexes-moyenne-2` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** Les nombres complexes ne sont pas au programme de la série A. Retirer BAC:A ; l'item convient pour C, D, E et TI.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Quel est l'ensemble des solutions dans $\mathbb{C}$ de l'équation

$$z^{2} - 4z + 13 = 0\ ?$$

- a) $\{2+3i\,;\,2-3i\}$
- b) $\{4+6i\,;\,4-6i\}$
- c) $\{-2+3i\,;\,-2-3i\}$
- d) Aucune solution, car $\Delta<0$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Une équation du second degré à coefficients **réels** dont le discriminant est négatif admet deux solutions complexes conjuguées, données par $z = \dfrac{-b \pm i\sqrt{|\Delta|}}{2a}$. Deux nombres conjugués ont des images symétriques par rapport à l'axe des abscisses, puisqu'ils ne diffèrent que par le signe de leur partie imaginaire.

### Corrigé

**Étape 1 - discriminant.** Ici $a = 1$, $b = -4$, $c = 13$ :

$$\Delta = b^{2} - 4ac = (-4)^{2} - 4 \times 1 \times 13 = 16 - 52 = -36$$

Le discriminant est strictement négatif : l'équation n'a pas de solution réelle, mais deux solutions complexes conjuguées.

**Étape 2 - racines carrées du discriminant.** On écrit $-36 = 36 \times (-1) = (6i)^{2}$, donc les racines carrées de $\Delta$ sont $\pm 6i$.

**Étape 3 - solutions.**

$$z_1 = \frac{4 + 6i}{2} = 2 + 3i \qquad ; \qquad z_2 = \frac{4 - 6i}{2} = 2 - 3i$$

**Étape 4 - interprétation géométrique.** Les images sont les points $A(2\,;3)$ et $B(2\,;-3)$. Ils ont la même abscisse et des ordonnées opposées : ils sont **symétriques par rapport à l'axe des réels**, ce qui est la traduction géométrique de la conjugaison.

**Vérification.** Somme des racines : $z_1 + z_2 = 4 = -\dfrac{b}{a}$. Produit : $z_1 z_2 = (2+3i)(2-3i) = 4 - 9i^{2} = 4 + 9 = 13 = \dfrac{c}{a}$. Les deux relations coefficients-racines sont vérifiées.

### Pourquoi les autres réponses sont fausses

- **b)** la division par $2a=2$ a été oubliée : $z=\frac{4\pm6i}{2}$.
- **c)** erreur de signe sur $-b$ : ici $-b=4>0$, donc la partie réelle est $+2$.
- **d)** $\Delta<0$ interdit seulement les solutions réelles ; dans $\mathbb{C}$ il y a deux solutions conjuguées.

</details>

Avis : 

---

## 52. `cqc-nombres-complexes-moyenne-3` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** La série BAC:A est indiquée : les nombres complexes et les transformations du plan complexe ne sont pas au programme de Terminale A ; retirer A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan complexe est muni d'un repère orthonormé direct. À tout point $M$ d'affixe $z$, on associe le point $M'$ d'affixe

$$z' = 2z - 1 + i.$$

Quelle est la nature de cette transformation ?

- a) L'homothétie de centre le point d'affixe $-1+i$ et de rapport $2$
- b) L'homothétie de centre le point d'affixe $1+i$ et de rapport $2$
- c) La translation de vecteur d'affixe $-1+i$
- d) L'homothétie de centre le point d'affixe $1-i$ et de rapport $2$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Une transformation d'écriture $z' = a z + b$ avec $a$ réel différent de $0$ et de $1$ est une **homothétie** de rapport $a$. Son centre est l'unique point invariant, obtenu en résolvant $z = az + b$. Quand $a$ n'est pas réel, la transformation est une rotation (si $|a| = 1$) ou plus généralement une similitude directe.

### Corrigé

**1. Point invariant.**

Un point est invariant lorsque son image est lui-même, c'est-à-dire $z' = z$ :

$$z = 2z - 1 + i$$

$$z - 2z = -1 + i \quad \Longrightarrow \quad -z = -1 + i \quad \Longrightarrow \quad z = 1 - i$$

Il existe donc un unique point invariant $\Omega$, d'affixe $\omega = 1 - i$.

**2. Nature et éléments caractéristiques.**

Le coefficient de $z$ vaut $a = 2$ : c'est un **réel**, différent de $0$ et de $1$. La transformation est donc l'**homothétie de centre $\Omega(1 - i)$ et de rapport $2$**.

**Justification par l'écriture réduite.** En retranchant $\omega$ des deux côtés :

$$z' - \omega = 2z - 1 + i - (1 - i) = 2z - 2 + 2i = 2\left(z - 1 + i\right) = 2\left(z - \omega\right)$$

On obtient $z' - \omega = 2(z - \omega)$, soit $\overrightarrow{\Omega M'} = 2\,\overrightarrow{\Omega M}$ : c'est exactement la définition d'une homothétie de centre $\Omega$ et de rapport $2$.

**Contrôle.** Le rapport valant $2 > 1$, les distances au centre doublent. Vérifions sur un point : $M$ d'affixe $0$ a pour image $z' = -1 + i$. On a $|0 - \omega| = |{-1} + i| = \sqrt{2}$ et $|z' - \omega| = |-1 + i - 1 + i| = |-2 + 2i| = 2\sqrt{2}$, soit bien le double.

### Pourquoi les autres réponses sont fausses

- **a)** on a lu le terme constant $b=-1+i$ comme affixe du centre ; le centre est solution de $z=2z-1+i$, soit $z=1-i$.
- **b)** erreur de signe sur la partie imaginaire en résolvant $-z=-1+i$ : on obtient $z=1-i$.
- **c)** une translation s'écrit $z'=z+b$ ; ici le coefficient de $z$ vaut $2\neq1$ et il existe un point invariant.

</details>

Avis : 

---

## 53. `cqc-nombres-complexes-moyenne-4` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** La série A est indiquée : nombres complexes et transformations du plan hors programme de Terminale A. Correct pour C, D, E, TI.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans le plan complexe rapporté à un repère orthonormé direct, on associe à tout point $M$ d'affixe $z$ le point $M'$ d'affixe

$$z' = iz + 2.$$

Quelle est la nature de cette transformation ?

- a) La rotation de centre le point d'affixe $2$ et d'angle $\dfrac{\pi}{2}$
- b) La rotation de centre le point d'affixe $1-i$ et d'angle $\dfrac{\pi}{2}$
- c) La rotation de centre le point d'affixe $1+i$ et d'angle $\dfrac{\pi}{2}$
- d) La rotation de centre le point d'affixe $1+i$ et d'angle $-\dfrac{\pi}{2}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour séparer partie réelle et partie imaginaire, on remplace $z$ par $x + iy$, on développe, puis on utilise $i^{2} = -1$ avant de regrouper - c'est cette substitution de $i^2$ qui fait migrer un terme de la partie imaginaire vers la partie réelle. Pour la nature de la transformation, on regarde le coefficient $a$ de $z$ : si $|a| = 1$ sans que $a$ soit réel, il s'agit d'une rotation d'angle $\arg(a)$.

### Corrigé

**1. Parties réelle et imaginaire.**

$$z' = i(x + iy) + 2 = ix + i^{2}y + 2 = ix - y + 2$$

En regroupant :

$$z' = \underbrace{(2 - y)}_{\text{partie réelle}} + i\underbrace{\,x\,}_{\text{partie imaginaire}}$$

Donc $\mathrm{Re}(z') = 2 - y$ et $\mathrm{Im}(z') = x$.

**2. Point invariant.**

On résout $z = iz + 2$ :

$$z - iz = 2 \quad \Longrightarrow \quad z(1 - i) = 2 \quad \Longrightarrow \quad z = \frac{2}{1-i}$$

On multiplie numérateur et dénominateur par le conjugué $1 + i$ :

$$z = \frac{2(1+i)}{(1-i)(1+i)} = \frac{2(1+i)}{1 - i^{2}} = \frac{2(1+i)}{2} = 1 + i$$

Le point invariant $\Omega$ a pour affixe $\omega = 1 + i$.

**3. Nature de la transformation.**

Le coefficient de $z$ est $a = i$, dont le module vaut $|i| = 1$ et l'argument $\arg(i) = \dfrac{\pi}{2}$. Comme $|a| = 1$ et que $a$ n'est pas réel, la transformation est la **rotation de centre $\Omega(1+i)$ et d'angle $\dfrac{\pi}{2}$**.

**Justification par l'écriture réduite.**

$$z' - \omega = iz + 2 - (1+i) = iz + 1 - i = i\left(z + \frac{1-i}{i}\right)$$

Or $\dfrac{1-i}{i} = \dfrac{(1-i)\times(-i)}{i \times (-i)} = \dfrac{-i + i^{2}}{1} = -1 - i = -\omega$. Donc

$$z' - \omega = i\left(z - \omega\right)$$

ce qui caractérise bien la rotation de centre $\Omega$ et d'angle $\dfrac{\pi}{2}$.

**Contrôle.** Une rotation conserve les distances : $|z' - \omega| = |i|\times|z - \omega| = |z-\omega|$. La transformation ne déforme donc pas les figures, contrairement à l'homothétie.

### Pourquoi les autres réponses sont fausses

- **a)** le terme constant $b=2$ n'est pas l'affixe du centre ; le centre est le point invariant, solution de $z=iz+2$.
- **b)** erreur dans le calcul de $\frac{2}{1-i}=\frac{2(1+i)}{2}=1+i$ : le conjugué a été mal appliqué.
- **d)** l'angle est l'argument du coefficient $i$, c'est-à-dire $+\frac{\pi}{2}$.

</details>

Avis : 

---

## 54. `cqc-points-invariants-elevee-5` (séries BAC:C BAC:E)

**Énoncé :**

L'espace est rapporté à un repère orthonormé. On considère la transformation $g$ définie analytiquement par

$$\begin{cases} x' = -x \\ y' = -y \\ z' = z \end{cases}$$

Quelle est la nature de $g$ ?

- a) La symétrie centrale de centre $O$
- b) Le demi-tour d'axe $(Oz)$
- c) La symétrie orthogonale par rapport au plan $(xOy)$
- d) Le demi-tour d'axe $(Ox)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans l'espace, un ensemble de points invariants réduit à une **droite** oriente vers un demi-tour, c'est-à-dire une rotation d'angle $\pi$ autour de cette droite. Pour le confirmer, on vérifie les deux propriétés caractéristiques : la droite est la médiatrice de chaque segment $[MM']$ - autrement dit elle passe par son milieu et lui est orthogonale.

### Corrigé

**1. Points invariants.**

Un point $M(x\,;y\,;z)$ est invariant si et seulement si

$$\begin{cases} x = -x \\ y = -y \\ z = z \end{cases} \quad \Longleftrightarrow \quad \begin{cases} 2x = 0 \\ 2y = 0 \\ \text{toujours vrai} \end{cases} \quad \Longleftrightarrow \quad \begin{cases} x = 0 \\ y = 0 \end{cases}$$

La troisième équation n'impose rien : $z$ reste libre. L'ensemble des points invariants est donc la droite

$$(D) = \left\{(0\,;0\,;z),\ z \in \mathbb{R}\right\}$$

c'est-à-dire l'**axe $(Oz)$**, de vecteur directeur $\vec{k}\,(0\,;0\,;1)$.

**2. Propriétés du segment $[MM']$.**

Soit $M(x\,;y\,;z)$ quelconque, d'image $M'(-x\,;-y\,;z)$.

**Le milieu.** Ses coordonnées sont

$$\left(\frac{x + (-x)}{2}\,;\,\frac{y + (-y)}{2}\,;\,\frac{z+z}{2}\right) = (0\,;0\,;z)$$

Ses deux premières coordonnées étant nulles, ce point appartient bien à $(D)$.

**L'orthogonalité.**

$$\overrightarrow{MM'}\,(-2x\,;-2y\,;0)$$

Son produit scalaire avec le vecteur directeur $\vec{k}$ de $(D)$ vaut

$$(-2x) \times 0 + (-2y) \times 0 + 0 \times 1 = 0$$

Le vecteur $\overrightarrow{MM'}$ est donc orthogonal à $(D)$.

**3. Nature de $g$.**

La droite $(D)$ est fixe point par point, et chaque point $M$ hors de $(D)$ a une image $M'$ telle que $(D)$ passe par le milieu de $[MM']$ en lui étant orthogonale. Cela caractérise le **demi-tour d'axe $(Oz)$**, c'est-à-dire la rotation d'angle $\pi$ autour de cet axe.

**Contrôle par l'involutivité.** Appliquons $g$ deux fois : $(x\,;y\,;z) \mapsto (-x\,;-y\,;z) \mapsto (x\,;y\,;z)$. On retrouve le point de départ, donc $g \circ g = \mathrm{Id}$ - propriété attendue d'un demi-tour, puisqu'une rotation de $\pi$ répétée donne une rotation de $2\pi$.

**À ne pas confondre.** Dans le **plan**, les relations $x'=-x$ et $y'=-y$ définiraient la symétrie de centre $O$. Dans l'**espace**, la troisième coordonnée étant inchangée, il s'agit d'un demi-tour autour d'un axe et non d'une symétrie centrale - laquelle changerait aussi le signe de $z$.

### Pourquoi les autres réponses sont fausses

- **a)** elle changerait aussi le signe de $z$ ; ici $z$ est inchangé et les points de l'axe $(Oz)$ sont invariants.
- **c)** elle ne changerait que $z$, alors que $x$ et $y$ changent de signe ; les points invariants forment une droite et non un plan.
- **d)** l'axe est l'ensemble des points invariants : $x=0$ et $y=0$, c'est-à-dire $(Oz)$.

</details>

Avis : 

---

## 55. `cqc-primitive-elevee-5` (séries BAC:A BAC:C BAC:D BAC:E)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** La série A est indiquée : primitives de fonctions trigonométriques et formule de duplication hors programme de Terminale A. Correct pour C, D, E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x) = \cos^2 x$. On rappelle que $\cos(2x) = 2\cos^2 x - 1$.

Quelle est la primitive $F$ de $f$ sur $\mathbb{R}$ qui s'annule en $0$ ?

- a) $F(x) = \dfrac{x}{2} + \dfrac{\sin(2x)}{2}$
- b) $F(x) = \dfrac{x}{2} - \dfrac{\sin(2x)}{4}$
- c) $F(x) = \dfrac{\cos^3 x}{3} - \dfrac{1}{3}$
- d) $F(x) = \dfrac{x}{2} + \dfrac{\sin(2x)}{4}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Aucune formule ne donne directement une primitive d'un carré de fonction trigonométrique : il faut d'abord **linéariser**, c'est-à-dire transformer la puissance en somme de cosinus ou de sinus d'arcs multiples, à l'aide des formules de duplication. Une fois la puissance éliminée, on retombe sur des primitives usuelles.

### Corrigé

**1. Linéarisation.**

La formule fournie s'écrit $\cos(2x) = 2\cos^2 x - 1$. On l'inverse pour isoler $\cos^2 x$ :

$$2\cos^2 x = 1 + \cos(2x) \qquad \Longrightarrow \qquad \cos^2 x = \frac{1 + \cos(2x)}{2}$$

D'où

$$f(x) = \frac{1}{2} + \frac{1}{2}\cos(2x)$$

**2. Primitives.**

**Étape 1 - primitiver terme à terme.** Une primitive de la constante $\dfrac{1}{2}$ est $\dfrac{x}{2}$. Une primitive de $\cos(2x)$ est $\dfrac{\sin(2x)}{2}$, donc une primitive de $\dfrac{1}{2}\cos(2x)$ est $\dfrac{1}{2} \times \dfrac{\sin(2x)}{2} = \dfrac{\sin(2x)}{4}$.

$$F(x) = \frac{x}{2} + \frac{\sin(2x)}{4} + C$$

**Étape 2 - condition $F(0) = 0$.** Avec $\sin 0 = 0$ :

$$F(0) = 0 + 0 + C = C$$

donc $C = 0$.

**Conclusion.**

$$\boxed{F(x) = \frac{x}{2} + \frac{\sin(2x)}{4}}$$

**Vérification.** En dérivant :

$$F'(x) = \frac{1}{2} + \frac{2\cos(2x)}{4} = \frac{1}{2} + \frac{\cos(2x)}{2} = \frac{1 + \cos(2x)}{2} = \cos^2 x = f(x)$$

**Contrôle de cohérence.** $f$ étant positive sur $\mathbb{R}$ (un carré), sa primitive doit être croissante : c'est bien le cas, puisque $F' = f \geq 0$. Par ailleurs $F$ croît en moyenne comme $\dfrac{x}{2}$, ce qui correspond à la valeur moyenne $\dfrac{1}{2}$ de $\cos^2$ sur une période.

### Pourquoi les autres réponses sont fausses

- **a)** on primitive $\cos(2x)$ en $\dfrac{\sin(2x)}{2}$ mais on oublie le facteur $\dfrac{1}{2}$ devant $\cos(2x)$.
- **b)** erreur de signe sur le terme trigonométrique (la dérivée de $-\dfrac{\sin(2x)}{4}$ vaut $-\dfrac{\cos(2x)}{2}$).
- **c)** on applique la règle des puissances $\dfrac{u^3}{3}$ sans tenir compte de la dérivée de $\cos x$ ; la dérivée obtenue est $-\cos^2 x \sin x$.

</details>

Avis : 

---

## 56. `cqc-primitive-moyenne-3` (séries BAC:A BAC:C BAC:D BAC:E)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** Les fonctions trigonométriques et leurs primitives ne figurent pas au programme léger de la série A, qui fait partie des séries visées.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x) = 4\cos(2x) + \sin(3x)$.

Quelle est la primitive $F$ de $f$ sur $\mathbb{R}$ qui s'annule en $0$ ?

- a) $F(x) = 4\sin(2x) - \cos(3x) + 1$
- b) $F(x) = 2\sin(2x) + \dfrac{1}{3}\cos(3x) - \dfrac{1}{3}$
- c) $F(x) = 2\sin(2x) - \dfrac{1}{3}\cos(3x) - \dfrac{1}{3}$
- d) $F(x) = 2\sin(2x) - \dfrac{1}{3}\cos(3x) + \dfrac{1}{3}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Une primitive de $\cos(ax)$ est $\dfrac{\sin(ax)}{a}$, et une primitive de $\sin(ax)$ est $-\dfrac{\cos(ax)}{a}$. Le coefficient $a$ apparaît au **dénominateur** parce que la dérivation d'une fonction composée le fait sortir en facteur : c'est l'oubli de ce $\dfrac{1}{a}$, et le signe moins du cosinus, qui provoquent l'essentiel des erreurs.

### Corrigé

**Étape 1 - primitiver terme à terme.**

Pour $4\cos(2x)$ : une primitive de $\cos(2x)$ est $\dfrac{\sin(2x)}{2}$, donc une primitive de $4\cos(2x)$ est $4 \times \dfrac{\sin(2x)}{2} = 2\sin(2x)$.

Pour $\sin(3x)$ : une primitive est $-\dfrac{\cos(3x)}{3}$.

D'où la forme générale :

$$F(x) = 2\sin(2x) - \frac{1}{3}\cos(3x) + C$$

**Étape 2 - utiliser la condition $F(0) = 0$.**

Avec $\sin 0 = 0$ et $\cos 0 = 1$ :

$$F(0) = 2 \times 0 - \frac{1}{3} \times 1 + C = -\frac{1}{3} + C$$

On veut $-\dfrac{1}{3} + C = 0$, d'où $C = \dfrac{1}{3}$.

**Conclusion.**

$$\boxed{F(x) = 2\sin(2x) - \frac{1}{3}\cos(3x) + \frac{1}{3}}$$

**Vérification.** En dérivant :

$$F'(x) = 2 \times 2\cos(2x) - \frac{1}{3} \times \left(-3\sin(3x)\right) = 4\cos(2x) + \sin(3x) = f(x)$$

et $F(0) = 0 - \dfrac{1}{3} + \dfrac{1}{3} = 0$.

### Pourquoi les autres réponses sont fausses

- **a)** on oublie de diviser par le coefficient de $x$ dans chaque argument ($2$ puis $3$).
- **b)** une primitive de $\sin(3x)$ est $-\dfrac{\cos(3x)}{3}$ : le signe moins est oublié.
- **c)** erreur de signe sur la constante : $F(0) = -\dfrac{1}{3} + C = 0$ donne $C = \dfrac{1}{3}$.

</details>

Avis : 

---

## 57. `cqc-tableau-de-variations-faible-0` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PRO:A)

**Remarque du relecteur :** PRO:A figure dans les séries alors que la consigne porte sur la Terminale : vérifier que la dérivation des polynômes du 3e degré est au programme de Première A.

**Énoncé :**

Soit $h$ la fonction définie sur $\mathbb{R}$ par $h(x) = x^3 - 6x^2 + 9x + 1$.

Le tableau de variations de $h$ fait apparaître un maximum local et un minimum local. Lesquels ?

- a) Maximum local $1$ atteint en $x = 3$ et minimum local $5$ atteint en $x = 1$
- b) Maximum local $5$ atteint en $x = 1$ et minimum local $1$ atteint en $x = 3$
- c) Maximum local $4$ atteint en $x = 1$ et minimum local $0$ atteint en $x = 3$
- d) Maximum local $-107$ atteint en $x = -3$ et minimum local $-15$ atteint en $x = -1$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour dresser le tableau de variations d'une fonction polynôme, on calcule sa dérivée, on la factorise pour lire directement le signe de chaque facteur, puis on reporte ce signe et les limites aux bornes du domaine dans un tableau. Le sens de variation se déduit du signe de la dérivée : positive, la fonction croît ; négative, elle décroît.

### Corrigé

**Étape 1 - dérivée.** $h$ est un polynôme, donc dérivable sur $\mathbb{R}$ :

$$h'(x) = 3x^2 - 12x + 9 = 3\left(x^2 - 4x + 3\right) = 3(x-1)(x-3)$$

**Étape 2 - signe de la dérivée.** Le coefficient dominant $3$ est positif, donc le trinôme est positif à l'extérieur de ses racines $1$ et $3$, négatif entre elles :

- $h'(x) > 0$ sur $]-\infty\,;1[$ et sur $]3\,;+\infty[$ ;
- $h'(x) < 0$ sur $]1\,;3[$ ;
- $h'(1) = h'(3) = 0$.

**Étape 3 - limites aux bornes.** Pour un polynôme, la limite en l'infini est celle de son terme de plus haut degré :

$$\lim_{x \to -\infty} h(x) = \lim_{x \to -\infty} x^3 = -\infty \qquad ; \qquad \lim_{x \to +\infty} h(x) = \lim_{x \to +\infty} x^3 = +\infty$$

**Étape 4 - valeurs aux points critiques.**

$$h(1) = 1 - 6 + 9 + 1 = 5 \qquad ; \qquad h(3) = 27 - 54 + 27 + 1 = 1$$

**Étape 5 - tableau de variations.**

$$
\begin{array}{|c|ccccccc|}
\hline
x & -\infty & & 1 & & 3 & & +\infty \\
\hline
h'(x) & & + & 0 & - & 0 & + & \\
\hline
 & & & 5 & & & & +\infty \\
h(x) & & \nearrow & & \searrow & & \nearrow & \\
 & -\infty & & & & 1 & & \\
\hline
\end{array}
$$

**Conclusion.** $h$ est croissante sur $]-\infty\,;1]$, décroissante sur $[1\,;3]$ et croissante sur $[3\,;+\infty[$. Elle admet un maximum local $h(1)=5$ et un minimum local $h(3)=1$.

### Pourquoi les autres réponses sont fausses

- **a)** on inverse le signe de $h'$ : le polynôme est croissant, puis décroissant, puis croissant.
- **c)** on oublie le terme constant $+1$ dans le calcul de $h(1)$ et $h(3)$.
- **d)** erreur de factorisation : $3x^2 - 12x + 9$ a pour racines $1$ et $3$, non $-3$ et $-1$.

</details>

Avis : 

---

## 58. `cqc-tableau-de-variations-moyenne-2` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PRO:A)

**Série(s) retirée(s) par analogie avec vos avis :** PRO:A.

**Remarque du relecteur :** La série PRO:A (Probatoire, classe de Première A) figure dans la liste : la fonction exponentielle n'est pas au programme de Première A ; à retirer de PRO:A (correct pour les séries BAC).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $g$ la fonction définie sur $\mathbb{R}$ par $g(x) = x^2 e^{-x}$.

Quelle est la valeur du maximum local de $g$ ?

- a) $4e^{-2}$
- b) $4e^{2}$
- c) $2e^{-2}$
- d) $e^{-1}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour dériver un produit $uv$, on applique $(uv)' = u'v + uv'$, puis on **factorise** l'expression obtenue. C'est la factorisation qui rend le signe lisible : l'exponentielle étant strictement positive quel que soit son exposant, le signe de la dérivée se lit sur le seul facteur polynomial.

### Corrigé

**Étape 1 - dérivée.** Avec $u(x) = x^2$ ($u'(x) = 2x$) et $v(x) = e^{-x}$ ($v'(x) = -e^{-x}$) :

$$g'(x) = 2x\,e^{-x} + x^2 \times \left(-e^{-x}\right) = e^{-x}\left(2x - x^2\right) = x\,e^{-x}(2 - x)$$

**Étape 2 - signe.** Pour tout réel $x$, $e^{-x} > 0$. Le signe de $g'(x)$ est donc celui du produit $x(2-x)$, trinôme de racines $0$ et $2$ dont le coefficient dominant est $-1 < 0$ : il est positif entre les racines, négatif à l'extérieur.

- $g'(x) < 0$ sur $]-\infty\,;0[$ ;
- $g'(x) > 0$ sur $]0\,;2[$ ;
- $g'(x) < 0$ sur $]2\,;+\infty[$.

**Étape 3 - limites.**

En $-\infty$ : $x^2 \to +\infty$ et $e^{-x} \to +\infty$ (car $-x \to +\infty$), donc par produit

$$\lim_{x \to -\infty} g(x) = +\infty$$

En $+\infty$, la limite est celle admise par l'énoncé : $\displaystyle\lim_{x \to +\infty} g(x) = 0$. C'est un cas de croissances comparées - l'exponentielle $e^{-x}$ tend vers $0$ plus vite que $x^2$ ne tend vers $+\infty$.

**Étape 4 - valeurs remarquables.**

$$g(0) = 0 \qquad ; \qquad g(2) = 4e^{-2} = \frac{4}{e^2} \approx 0{,}54$$

**Étape 5 - tableau de variations.**

$$
\begin{array}{|c|ccccccc|}
\hline
x & -\infty & & 0 & & 2 & & +\infty \\
\hline
g'(x) & & - & 0 & + & 0 & - & \\
\hline
 & +\infty & & & & 4e^{-2} & & \\
g(x) & & \searrow & & \nearrow & & \searrow & \\
 & & & 0 & & & & 0 \\
\hline
\end{array}
$$

**Conclusion.** $g$ admet un minimum local $g(0) = 0$ et un maximum local $g(2) = \dfrac{4}{e^2}$. La courbe admet l'axe des abscisses comme asymptote horizontale en $+\infty$.

### Pourquoi les autres réponses sont fausses

- **b)** erreur sur la dérivée de $e^{-x}$ (le signe moins est oublié) : on trouve $g'(x) = x(2+x)e^{-x}$, donc le point $x = -2$ au lieu de $x = 2$.
- **c)** on évalue $2e^{-x}$ au lieu de $x^2 e^{-x}$, en oubliant d'élever $x = 2$ au carré.
- **d)** on calcule $g(1)$ : la dérivée s'annule en $x = 2$, non en $x = 1$.

</details>

Avis : 

---

## 59. `cqc-tableau-de-variations-moyenne-3` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PRO:A)

**Série(s) retirée(s) par analogie avec vos avis :** PRO:A.

**Remarque du relecteur :** Série PRO:A (Première A) incluse : le logarithme népérien n'est pas au programme de Première A ; retirer PRO:A, l'item convient aux séries BAC.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie par $f(x) = \ln\left(x^2 - 4\right)$.

Parmi les intervalles suivants, lequel est contenu dans l'ensemble de définition de $f$ et sur lequel $f$ est strictement croissante ?

- a) $\left]-\infty\,;-2\right[$
- b) $\left]0\,;+\infty\right[$
- c) $\left]2\,;+\infty\right[$
- d) $\left]-2\,;2\right[$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Une fonction $\ln(u)$ n'est définie que là où $u(x) > 0$ **strictement** : on résout donc cette inéquation avant toute chose. Sa dérivée vaut $\dfrac{u'(x)}{u(x)}$ ; comme on se place déjà là où $u(x) > 0$, le signe de la dérivée se réduit à celui du numérateur $u'(x)$.

### Corrigé

**1. Ensemble de définition.**

Il faut $x^2 - 4 > 0$, soit $(x-2)(x+2) > 0$. Ce trinôme de coefficient dominant positif est positif à l'extérieur de ses racines $-2$ et $2$ :

$$D_f = \left]-\infty\,;-2\right[ \;\cup\; \left]2\,;+\infty\right[$$

**2. Variations.**

**Étape 1 - dérivée.** Avec $u(x) = x^2 - 4$ et $u'(x) = 2x$ :

$$f'(x) = \frac{2x}{x^2 - 4}$$

**Étape 2 - signe.** Sur $D_f$, le dénominateur $x^2 - 4$ est strictement positif par construction. Le signe de $f'(x)$ est donc celui de $2x$, c'est-à-dire celui de $x$ :

- sur $]-\infty\,;-2[$, on a $x < 0$ donc $f'(x) < 0$ : $f$ est décroissante ;
- sur $]2\,;+\infty[$, on a $x > 0$ donc $f'(x) > 0$ : $f$ est croissante.

**Étape 3 - limites.**

En $-\infty$ : $x^2 - 4 \to +\infty$, donc $f(x) \to +\infty$.

En $-2^-$ : $x^2 - 4 \to 0^+$, et $\ln$ tend vers $-\infty$ en $0^+$, donc $f(x) \to -\infty$.

En $2^+$ : de même $x^2 - 4 \to 0^+$, donc $f(x) \to -\infty$.

En $+\infty$ : $x^2 - 4 \to +\infty$, donc $f(x) \to +\infty$.

**Étape 4 - tableau de variations.**

$$
\begin{array}{|c|ccccccc|}
\hline
x & -\infty & & -2 & \quad & 2 & & +\infty \\
\hline
f'(x) & & - & \| & & \| & + & \\
\hline
 & +\infty & & \| & & \| & & +\infty \\
f(x) & & \searrow & \| & & \| & \nearrow & \\
 & & -\infty & \| & & \| & -\infty & \\
\hline
\end{array}
$$

Les droites d'équations $x = -2$ et $x = 2$ sont asymptotes verticales à la courbe.

**Vérification par la parité.** $f(-x) = \ln\left((-x)^2 - 4\right) = \ln(x^2-4) = f(x)$ : $f$ est paire, et son domaine est bien symétrique par rapport à $0$. Le tableau obtenu est cohérent avec cette symétrie - décroissance à gauche, croissance à droite, avec le même comportement aux deux bornes.

### Pourquoi les autres réponses sont fausses

- **a)** sur cet intervalle, $f'(x) = \dfrac{2x}{x^2-4}$ est négative : $f$ y est décroissante.
- **b)** on étudie le signe de $2x$ sans tenir compte de l'ensemble de définition : $f$ n'est pas définie sur $]0\,;2]$.
- **d)** ces valeurs sont celles où $x^2 - 4 < 0$ : le logarithme n'y est pas défini.

</details>

Avis : 

---

## 60. `cqc-tableau-de-variations-moyenne-4` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PRO:A)

**Remarque du relecteur :** Le champ series contient PRO:A (Probatoire) dans un lot BAC : à vérifier.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}\setminus\{1\}$ par $f(x) = x + 1 + \dfrac{4}{x-1}$.

Quelle est la valeur du minimum local de $f$ sur l'intervalle $]1\,;+\infty[$ ?

- a) $-2$
- b) $6$
- c) $\dfrac{16}{3}$
- d) $8$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand une fonction est écrite comme la somme d'une partie affine et d'un terme en $\dfrac{k}{x-a}$, il est inutile de repasser par la formule du quotient : on dérive terme à terme. La dérivée obtenue se met ensuite au même dénominateur, puis se factorise - c'est cette factorisation qui donne le signe.

### Corrigé

**Étape 1 - dérivée.** La dérivée de $x+1$ vaut $1$, celle de $\dfrac{4}{x-1}$ vaut $-\dfrac{4}{(x-1)^2}$ :

$$f'(x) = 1 - \frac{4}{(x-1)^2} = \frac{(x-1)^2 - 4}{(x-1)^2}$$

**Étape 2 - factorisation du numérateur.** On reconnaît une différence de deux carrés, $A^2 - B^2 = (A-B)(A+B)$ avec $A = x-1$ et $B = 2$ :

$$(x-1)^2 - 4 = (x-1-2)(x-1+2) = (x-3)(x+1)$$

d'où

$$f'(x) = \frac{(x-3)(x+1)}{(x-1)^2}$$

**Étape 3 - signe.** Le dénominateur $(x-1)^2$ est strictement positif pour $x \neq 1$. Le signe de $f'$ est donc celui du trinôme $(x-3)(x+1)$, de racines $-1$ et $3$ et de coefficient dominant positif : positif à l'extérieur des racines, négatif entre elles.

- $f'(x) > 0$ sur $]-\infty\,;-1[$ et sur $]3\,;+\infty[$ ;
- $f'(x) < 0$ sur $]-1\,;1[$ et sur $]1\,;3[$.

**Étape 4 - limites.**

En $\pm\infty$ : $\dfrac{4}{x-1} \to 0$, donc $f(x)$ se comporte comme $x+1$ :

$$\lim_{x \to -\infty} f(x) = -\infty \qquad ; \qquad \lim_{x \to +\infty} f(x) = +\infty$$

En $1$ : le terme $x+1$ tend vers $2$, et $\dfrac{4}{x-1}$ domine :

- si $x \to 1^-$, alors $x-1 \to 0^-$ donc $\dfrac{4}{x-1} \to -\infty$ et $f(x) \to -\infty$ ;
- si $x \to 1^+$, alors $x-1 \to 0^+$ donc $f(x) \to +\infty$.

**Étape 5 - valeurs aux extrema.**

$$f(-1) = -1 + 1 + \frac{4}{-2} = -2 \qquad ; \qquad f(3) = 3 + 1 + \frac{4}{2} = 6$$

**Étape 6 - tableau de variations.**

$$
\begin{array}{|c|ccccccccc|}
\hline
x & -\infty & & -1 & & 1 & & 3 & & +\infty \\
\hline
f'(x) & & + & 0 & - & \| & - & 0 & + & \\
\hline
 & & & -2 & & \| & +\infty & & & +\infty \\
f(x) & & \nearrow & & \searrow & \| & & \searrow & \nearrow & \\
 & -\infty & & & -\infty & \| & & & 6 & \\
\hline
\end{array}
$$

**Conclusion.** $f$ admet un maximum local $f(-1) = -2$ sur $]-\infty\,;1[$ et un minimum local $f(3) = 6$ sur $]1\,;+\infty[$. Comme $\dfrac{4}{x-1} \to 0$ en $\pm\infty$, la droite d'équation $y = x+1$ est asymptote oblique à la courbe.

### Pourquoi les autres réponses sont fausses

- **a)** c'est la valeur $f(-1)$, maximum local sur $]-\infty\,;1[$ : on mélange les deux intervalles.
- **c)** on calcule $f(3)$ en écrivant $\dfrac{4}{x-1}$ comme $\dfrac{4}{3}$, sans retrancher $1$ au dénominateur.
- **d)** on calcule $f(3)$ en oubliant de diviser $4$ par $x - 1 = 2$.

</details>

Avis : 

---

## 61. `cqc-theoreme-des-gendarmes-elevee-5` (séries BAC:C BAC:D BAC:E)

**Remarque du relecteur :** LIMITE : dérivabilité en 0 par encadrement d'une fonction oscillante, exercice classique mais exigeant pour la série D.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par

$$f(x) = \begin{cases} x^{2}\sin\left(\dfrac{1}{x}\right) & \text{si } x \neq 0 \\[2mm] 0 & \text{si } x = 0 \end{cases}$$

Laquelle de ces affirmations est vraie ?

- a) $f$ est continue en $0$ mais n'est pas dérivable en $0$, car $\sin\left(\dfrac{1}{x}\right)$ n'a pas de limite en $0$
- b) $f$ n'est pas continue en $0$, donc n'est pas dérivable en $0$
- c) $f$ est dérivable en $0$ et $f'(0) = 1$
- d) $f$ est dérivable en $0$ et $f'(0) = 0$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

La dérivabilité en un point se démontre par définition, en étudiant la limite du **taux d'accroissement** $\dfrac{f(x) - f(0)}{x - 0}$. Quand ce taux contient un facteur oscillant sans limite, on l'encadre au lieu de chercher à le calculer : le théorème des gendarmes conclut alors sur l'existence de la limite, donc sur la dérivabilité.

### Corrigé

**Étape 1 - écrire le taux d'accroissement.**

Pour $x \neq 0$, avec $f(0) = 0$ :

$$\tau(x) = \frac{f(x) - f(0)}{x - 0} = \frac{x^{2}\sin\left(\frac{1}{x}\right)}{x} = x\sin\left(\frac{1}{x}\right)$$

**Étape 2 - encadrer.**

Quel que soit $x \neq 0$, le sinus reste borné :

$$-1 \leq \sin\left(\frac{1}{x}\right) \leq 1$$

En multipliant par $|x| \geq 0$, puis en repassant par la valeur absolue pour éviter toute discussion de signe :

$$\left|\tau(x)\right| = |x| \times \left|\sin\left(\frac{1}{x}\right)\right| \leq |x|$$

soit

$$-|x| \leq \tau(x) \leq |x|$$

**Étape 3 - passage à la limite.**

$$\lim_{x \to 0} \left(-|x|\right) = 0 \qquad ; \qquad \lim_{x \to 0} |x| = 0$$

D'après le théorème des gendarmes, le taux d'accroissement admet une limite finie en $0$ :

$$\lim_{x \to 0} \tau(x) = 0$$

**Conclusion.** $f$ est **dérivable en $0$** et

$$\boxed{f'(0) = 0}$$

**Pourquoi la valeur absolue est utile.** Le signe de $x$ change de part et d'autre de $0$ : multiplier l'encadrement de $\sin$ par $x$ directement obligerait à distinguer $x>0$ et $x<0$, car les inégalités s'inverseraient. Passer par $\left|\tau(x)\right| \leq |x|$ traite les deux cas d'un coup.

**Le contre-exemple à connaître.** Si l'on remplaçait $x^{2}$ par $x$, le taux d'accroissement deviendrait $\sin\left(\dfrac{1}{x}\right)$, qui oscille sans limite : la fonction serait continue en $0$ mais **pas dérivable**. C'est le carré, et lui seul, qui écrase assez l'oscillation pour que la limite existe.

### Pourquoi les autres réponses sont fausses

- **a)** on confond avec $x \sin\left(\dfrac{1}{x}\right)$ : le taux d'accroissement est ici $x\sin\left(\dfrac{1}{x}\right)$, qui tend vers $0$ grâce au facteur $x$.
- **b)** $|f(x)| \leq x^{2}$ tend vers $0$ : $f$ est bien continue en $0$.
- **c)** on remplace $\sin\left(\dfrac{1}{x}\right)$ par $1$ au lieu de l'encadrer : le taux d'accroissement est encadré par $-|x|$ et $|x|$.

</details>

Avis : 

---

## 62. `cqc-theoreme-des-gendarmes-moyenne-4` (séries BAC:C BAC:D BAC:E BAC:TI)

**Énoncé :**

Soit $(P_n)$ une suite de réels vérifiant, pour tout entier naturel $n$,

$$\left|P_n - 5\right| \leq \left(\frac{2}{3}\right)^{n}.$$

Que peut-on affirmer sur $(P_n)$ ?

- a) $(P_n)$ converge vers $0$
- b) $(P_n)$ converge vers $5$
- c) $(P_n)$ converge vers $\dfrac{2}{3}$
- d) On ne peut rien affirmer sur $(P_n)$, car on ne connaît pas son expression

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Un encadrement portant sur une **valeur absolue** se déplie en un encadrement classique : $|A| \leq B$ équivaut à $-B \leq A \leq B$. On applique ensuite le théorème des gendarmes à la quantité $A$, ici l'écart entre la suite et sa limite présumée. Il faut aussi connaître le comportement d'une suite géométrique : $q^{n} \to 0$ dès que $|q| < 1$.

### Corrigé

**Étape 1 - déplier la valeur absolue.**

$$\left|P_n - 5\right| \leq \left(\frac{2}{3}\right)^{n} \quad \Longleftrightarrow \quad -\left(\frac{2}{3}\right)^{n} \leq P_n - 5 \leq \left(\frac{2}{3}\right)^{n}$$

**Étape 2 - limite de la suite géométrique.**

La raison vaut $q = \dfrac{2}{3}$, avec $0 < q < 1$, donc $|q| < 1$ et

$$\lim_{n \to +\infty} \left(\frac{2}{3}\right)^{n} = 0$$

Par conséquent $-\left(\dfrac{2}{3}\right)^{n} \to 0$ également.

**Étape 3 - théorème des gendarmes.**

La suite $\left(P_n - 5\right)$ est encadrée par deux suites de limite $0$, donc

$$\lim_{n \to +\infty} \left(P_n - 5\right) = 0$$

**Conclusion.** La suite $(P_n)$ converge, et

$$\boxed{\lim_{n \to +\infty} P_n = 5}$$

**Lecture de l'énoncé.** L'inégalité fournie signifie que l'écart entre $P_n$ et $5$ est contrôlé par une quantité qui s'annule : c'est exactement la définition intuitive de la convergence vers $5$. La suite géométrique joue ici le rôle de « majorant de l'erreur », et sa décroissance rapide indique en outre que la convergence est **géométrique**, donc très rapide - dès $n = 10$, l'écart est inférieur à $0{,}02$.

### Pourquoi les autres réponses sont fausses

- **a)** on confond la limite de la suite géométrique majorante, $0$, avec celle de $(P_n)$ : c'est $P_n - 5$ qui tend vers $0$.
- **c)** on prend la raison de la suite géométrique pour la limite de $(P_n)$.
- **d)** l'encadrement $-\left(\dfrac{2}{3}\right)^{n} \leq P_n - 5 \leq \left(\dfrac{2}{3}\right)^{n}$ suffit pour conclure avec le théorème des gendarmes.

</details>

Avis : 

---

## 63. `cqc-variations-elevee-5` (séries BAC:A BAC:C BAC:E)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** LIMITE : la série A est indiquée ; l'usage de la dérivée seconde pour étudier le signe de g' est à la limite haute du programme de Terminale A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $g$ la fonction définie sur $\mathbb{R}$ par $g(x)=\mathrm{e}^{x}-\dfrac{x^{2}}{2}-x-1$. On veut établir que $g(x)\geq 0$ pour tout $x\geq 0$. Quel enchaînement de déductions est correct ?

- a) $g''(x)=\mathrm{e}^{x}-1\geq 0$ sur $[0\,;+\infty[$, donc $g'$ est croissante ; comme $g'(0)=0$, on a $g'\geq 0$, donc $g$ est croissante ; comme $g(0)=0$, on a $g\geq 0$.
- b) $g''\geq 0$ sur $[0\,;+\infty[$, donc $g$ est croissante ; comme $g(0)=0$, on a $g\geq 0$.
- c) $g''\geq 0$, donc $g'$ est croissante ; comme $g'(0)=0$, on a $g'\geq 0$, donc $g$ est décroissante ; comme $g(0)=0$, on a $g\leq 0$.
- d) $g''\geq 0$, donc $g'$ est croissante ; comme $g'(0)=0$, on a $g'\geq 0$, donc $g$ est croissante ; comme $g(0)=1$, on a $g\geq 1$.

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand le signe d'une dérivée n'est pas lisible directement, on **redérive** : le signe de $g''$ donne les variations de $g'$, dont on déduit le signe de $g'$ à l'aide d'une valeur particulière, puis les variations de $g$, et enfin son signe. Cette cascade à deux étages est la méthode standard dès qu'une exponentielle est mêlée à un polynôme.

### Corrigé

**1. Dérivées successives.**

$$g'(x) = \mathrm{e}^{x} - x - 1$$

$$g''(x) = \mathrm{e}^{x} - 1$$

**2. Signe de $g''$ et conséquences.**

Sur $\left[0\,;+\infty\right[$, on a $x \geq 0$ donc $\mathrm{e}^{x} \geq \mathrm{e}^{0} = 1$, d'où

$$g''(x) = \mathrm{e}^{x} - 1 \geq 0$$

$g'$ est donc **croissante** sur $\left[0\,;+\infty\right[$. Or

$$g'(0) = \mathrm{e}^{0} - 0 - 1 = 0$$

Une fonction croissante qui vaut $0$ en $0$ reste positive après $0$ :

$$g'(x) \geq g'(0) = 0 \qquad \text{pour tout } x \geq 0$$

**3. Signe de $g$.**

$g'$ étant positive sur $\left[0\,;+\infty\right[$, la fonction $g$ y est **croissante**. Or

$$g(0) = \mathrm{e}^{0} - 0 - 0 - 1 = 1 - 1 = 0$$

Donc, pour tout $x \geq 0$ :

$$g(x) \geq g(0) = 0 \quad \Longleftrightarrow \quad \boxed{\mathrm{e}^{x} \geq 1 + x + \frac{x^{2}}{2}}$$

**Interprétation.** On vient de démontrer que l'exponentielle domine son développement polynomial d'ordre $2$. En poursuivant la cascade - trois dérivations, puis quatre - on obtiendrait de la même façon $\mathrm{e}^{x} \geq 1 + x + \dfrac{x^{2}}{2} + \dfrac{x^{3}}{6}$, et ainsi de suite. C'est le mécanisme qui explique pourquoi l'exponentielle l'emporte sur **toute** puissance de $x$ en $+\infty$.

**Attention à la restriction.** Le raisonnement n'est valable que sur $\left[0\,;+\infty\right[$ : pour $x < 0$, $g''$ devient négative et la cascade s'inverse. L'inégalité finale reste vraie pour $x<0$, mais elle demanderait une étude séparée.

### Pourquoi les autres réponses sont fausses

- **b)** le signe de $g''$ donne les variations de $g'$ et non celles de $g$ : il manque une étape.
- **c)** une dérivée positive donne une fonction croissante, et non décroissante.
- **d)** $g(0)=\mathrm{e}^{0}-0-0-1=0$ et non $1$ : le terme $-1$ a été oublié.


</details>

Avis : 

---

## 64. `cqc-equations-differentielles-tle-ce-elevee-5` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : avec un second membre 5 sin x, il faut trouver soi-même la solution particulière, alors qu'au BAC sa forme est en général donnée. L'item est long pour un QCM.

**Énoncé :**

On considère l'équation différentielle $(E) : y''-y'-2y=5\sin x$. Quelle est la solution $f$ de $(E)$ vérifiant $f(0)=0$ et $f'(0)=0$ ?

- a) $f(x)=\dfrac13\mathrm{e}^{2x}-\dfrac56\mathrm{e}^{-x}+\dfrac12\cos x-\dfrac32\sin x$
- b) $f(x)=-\dfrac23\mathrm{e}^{2x}+\dfrac16\mathrm{e}^{-x}+\dfrac12\cos x+\dfrac32\sin x$
- c) $f(x)=-\dfrac16\mathrm{e}^{2x}-\dfrac13\mathrm{e}^{-x}+\dfrac12\cos x-\dfrac32\sin x$
- d) $f(x)=-\dfrac23\mathrm{e}^{-2x}+\dfrac16\mathrm{e}^{x}+\dfrac12\cos x-\dfrac32\sin x$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour résoudre $y''+py'+qy=f(x)$ avec $f(x)=m\cos x+n\sin x$, on cherche une solution particulière de la même forme $g(x)=a\cos x+b\sin x$, on calcule $g'$ et $g''$, on remplace dans l'équation, puis on identifie les coefficients de $\cos x$ et de $\sin x$. La solution générale de l'équation complète s'obtient ensuite en ajoutant cette solution particulière à la solution générale de l'équation homogène associée ; les constantes de cette dernière se déterminent enfin à l'aide des conditions initiales.

### Corrigé

**1) Solution particulière.** Avec $g(x) = a\cos x + b\sin x$ :
$$g'(x) = -a\sin x + b\cos x \qquad g''(x) = -a\cos x - b\sin x$$

On remplace dans $(E)$ :
$$g'' - g' - 2g = (-a\cos x - b\sin x) - (-a\sin x + b\cos x) - 2(a\cos x + b\sin x)$$
$$= (-a - b - 2a)\cos x + (a - b - 2b)\sin x = (-3a - b)\cos x + (a - 3b)\sin x$$

En identifiant à $5\sin x = 0\times\cos x + 5\sin x$ :
$$\begin{cases} -3a - b = 0 \\ a - 3b = 5 \end{cases}$$

De la première équation : $b = -3a$. En substituant dans la seconde : $a - 3(-3a) = a + 9a = 10a = 5$, donc $a = \dfrac12$, puis $b = -3\times\dfrac12 = -\dfrac32$.

$$a = \dfrac12, \quad b = -\dfrac32 \qquad\text{soit } g(x) = \dfrac12\cos x - \dfrac32\sin x$$

**2) Solution générale.** L'équation caractéristique de l'équation homogène associée $y''-y'-2y=0$ est :
$$r^2 - r - 2 = 0 \iff (r-2)(r+1) = 0 \iff r=2 \text{ ou } r=-1$$

Discriminant positif ($\Delta=1+8=9$), racines réelles distinctes, donc la solution générale de l'équation homogène est $y_h(x) = Ae^{2x} + Be^{-x}$, $A,B\in\mathbb{R}$.

La solution générale de $(E)$ est :
$$y(x) = Ae^{2x} + Be^{-x} + \dfrac12\cos x - \dfrac32\sin x, \quad A, B \in \mathbb{R}$$

**3) Détermination de $A$ et $B$ avec les conditions initiales.**

$$y'(x) = 2Ae^{2x} - Be^{-x} - \dfrac12\sin x - \dfrac32\cos x$$

- $f(0) = A + B + \dfrac12 = 0 \ \Longrightarrow\ A + B = -\dfrac12$
- $f'(0) = 2A - B - \dfrac32 = 0 \ \Longrightarrow\ 2A - B = \dfrac32$

En additionnant les deux équations : $3A = 1$, donc $A = \dfrac13$. On en déduit $B = -\dfrac12 - \dfrac13 = -\dfrac56$.

**Conclusion :**
$$f(x) = \dfrac13 e^{2x} - \dfrac56 e^{-x} + \dfrac12\cos x - \dfrac32\sin x$$

**Vérification** : $f(0) = \dfrac13 - \dfrac56 + \dfrac12 = \dfrac{2}{6}-\dfrac{5}{6}+\dfrac{3}{6} = 0$ . $f'(0) = 2\times\dfrac13 - \left(-\dfrac56\right) - \dfrac32 = \dfrac23 + \dfrac56 - \dfrac32 = \dfrac{4}{6}+\dfrac{5}{6}-\dfrac{9}{6} = 0$ . Les deux conditions initiales sont bien vérifiées.

### Pourquoi les autres réponses sont fausses

- **b)** erreur de signe sur $b$ : la solution particulière est $\dfrac12\cos x-\dfrac32\sin x$.
- **c)** la dérivée de la solution particulière a été oubliée dans la condition $f'(0)=0$.
- **d)** les racines de $r^{2}-r-2=0$ sont $2$ et $-1$ et non $-2$ et $1$.


</details>

Avis : 

---

## 65. `cqc-equations-differentielles-tle-d-moyenne-3` (séries BAC:D BAC:TI)

**Remarque du relecteur :** LIMITE : équation du second ordre avec racine double, à confirmer au programme de Terminale D et TI.

**Énoncé :**

Quelle est la solution générale sur $\mathbb{R}$ de l'équation différentielle $(E) : y''-6y'+9y=0$ ($A$ et $B$ désignant des réels) ?

- a) $y(x)=(Ax+B)\mathrm{e}^{3x}$
- b) $y(x)=A\mathrm{e}^{3x}+B\mathrm{e}^{-3x}$
- c) $y(x)=(Ax+B)\mathrm{e}^{-3x}$
- d) $y(x)=A\mathrm{e}^{3x}+B\mathrm{e}^{3x}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour résoudre une équation différentielle linéaire du second ordre à coefficients constants et sans second membre $ay''+by'+cy=0$, on forme l'équation caractéristique $ar^2+br+c=0$. Si celle-ci admet une racine double $r_0$ (discriminant nul), la solution générale de l'équation différentielle est $y(x) = (Ax+B)e^{r_0x}$, avec $A,B$ constantes réelles.

### Corrigé
L'équation caractéristique associée à $(E)$ est :
$$r^2 - 6r + 9 = 0$$

Son discriminant est $\Delta = (-6)^2 - 4\times1\times9 = 36-36=0$.

Comme $\Delta=0$, l'équation caractéristique admet une racine double :
$$r_0 = \dfrac{-(-6)}{2\times1} = \dfrac{6}{2} = 3$$

**On vérifie** : $(r-3)^2 = r^2-6r+9$, ce qui confirme la racine double $r_0=3$.

La solution générale de $(E)$ sur $\mathbb{R}$ est donc :
$$\boxed{y(x) = (Ax+B)e^{3x}, \quad A, B \in \mathbb{R}}$$

### Pourquoi les autres réponses sont fausses

- **b)** $-3$ n'est pas racine de $r^{2}-6r+9=0$ ; la racine double est $3$.
- **c)** la racine double vaut $\dfrac{6}{2}=3$ et non $-3$.
- **d)** cette expression se réduit à $(A+B)\mathrm{e}^{3x}$ : il manque la seconde solution $x\mathrm{e}^{3x}$ d'une racine double.


</details>

Avis : 

---

## 66. `cqc-equations-differentielles-tle-d-moyenne-4` (séries BAC:D BAC:TI)

**Remarque du relecteur :** LIMITE : équation différentielle du second ordre ; vérifier sa présence au programme de Terminale TI.

**Énoncé :**

On considère l'équation différentielle $(E) : y''+2y'+y=0$. Quelle est la solution $f$ de $(E)$ dont la courbe coupe l'axe des ordonnées au point d'ordonnée $3$ avec une tangente de coefficient directeur $-1$ en ce point ?

- a) $f(x)=(-x+3)\mathrm{e}^{-x}$
- b) $f(x)=(2x+3)\mathrm{e}^{-x}$
- c) $f(x)=(-4x+3)\mathrm{e}^{-x}$
- d) $f(x)=(-4x+3)\mathrm{e}^{x}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour déterminer la solution particulière d'une équation différentielle du second ordre vérifiant des conditions initiales (valeur en un point, coefficient directeur de la tangente en ce point), on part de la solution générale, puis on substitue les conditions - portant sur $y$ et sur $y'$ - pour obtenir un système de deux équations aux deux constantes inconnues.

### Corrigé
**Solution générale de $(E)$.** L'équation caractéristique est $r^2+2r+1=0$, de discriminant $\Delta = 2^2-4\times1\times1=4-4=0$. Racine double : $r_0=\dfrac{-2}{2}=-1$ (on vérifie : $(r+1)^2=r^2+2r+1$).

La solution générale de $(E)$ est donc $y(x) = (Ax+B)e^{-x}$, $A,B\in\mathbb{R}$, de dérivée :
$$y'(x) = Ae^{-x} - (Ax+B)e^{-x} = \big[A-(Ax+B)\big]e^{-x} = (A-Ax-B)e^{-x}$$

**Condition 1 : la courbe coupe l'axe des ordonnées au point d'ordonnée $3$**, c'est-à-dire $f(0)=3$ :
$$f(0) = (A\times0+B)e^0 = B = 3$$

**Condition 2 : la tangente en ce point a pour coefficient directeur $-1$**, c'est-à-dire $f'(0)=-1$ :
$$f'(0) = (A-A\times0-B)e^0 = A-B = -1$$

Avec $B=3$ : $A-3=-1 \Longrightarrow A=2$.

**Conclusion** : la solution particulière cherchée est :
$$\boxed{f(x) = (2x+3)e^{-x}}$$

**Vérification** : $f(0)=(0+3)e^0=3$ . $f'(x) = 2e^{-x}-(2x+3)e^{-x} = (2-2x-3)e^{-x} = (-2x-1)e^{-x}$, donc $f'(0) = -1$ .

### Pourquoi les autres réponses sont fausses

- **a)** $f'(0)=A-B$ et non $A$ : la dérivée de l'exponentielle a été oubliée.
- **c)** $f'(0)=A-B$ et non $A+B$ : $A-3=-1$ donne $A=2$.
- **d)** la racine double de $r^{2}+2r+1=0$ est $-1$ et non $1$.


</details>

Avis : 

---

## 67. `cqc-equations-differentielles-tle-ti-faible-1` (séries BAC:TI)

**Énoncé :**

Quelle est la solution générale sur $\mathbb{R}$ de l'équation différentielle $(E) : y''+9y=0$ ($A$ et $B$ désignant des réels) ?

- a) $y(x)=A\cos(3x)+B\sin(3x)$
- b) $y(x)=A\cos(9x)+B\sin(9x)$
- c) $y(x)=A\mathrm{e}^{3x}+B\mathrm{e}^{-3x}$
- d) $y(x)=A\cos\left(\dfrac{x}{3}\right)+B\sin\left(\dfrac{x}{3}\right)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Toute solution de l'équation différentielle $y'' + \omega^2 y = 0$ (avec $\omega > 0$ donné) est de la forme $y(x) = A\cos(\omega x) + B\sin(\omega x)$, où $A$ et $B$ sont deux constantes réelles.

### Corrigé
L'équation $(E) : y'' + 9y = 0$ est de la forme $y'' + \omega^2 y = 0$ avec $\omega^2 = 9$, donc $\omega = 3$ (on choisit la valeur positive de $\omega$).

La solution générale de $(E)$ est donc :
$$y(x) = A\cos(3x) + B\sin(3x), \quad (A,B) \in \mathbb{R}^2$$

**Vérification.** Pour $y(x) = A\cos(3x)+B\sin(3x)$ : $y'(x) = -3A\sin(3x)+3B\cos(3x)$ et $y''(x) = -9A\cos(3x)-9B\sin(3x) = -9y(x)$. On a bien $y''(x)+9y(x) = -9y(x)+9y(x) = 0$ pour tout réel $x$ : $(E)$ est vérifiée quelles que soient les constantes $A$ et $B$.

### Pourquoi les autres réponses sont fausses

- **b)** $\omega^{2}=9$ donne $\omega=3$ : la valeur $9$ est $\omega^{2}$ et non $\omega$.
- **c)** ces exponentielles sont solutions de $y''-9y=0$ ; avec $+9y$, l'équation caractéristique $r^{2}+9=0$ n'a pas de racine réelle.
- **d)** la pulsation est $\omega=3$ et non $\dfrac13$.


</details>

Avis : 

---

## 68. `cqc-equations-inequations-et-systemes-tle-a-faible-0` (séries BAC:A)

**Remarque du relecteur :** Niveau très inférieur au BAC (équation du premier degré de collège).

**Énoncé :**

Un chauffeur de moto-taxi facture une prise en charge de $150$ FCFA, puis $50$ FCFA par kilomètre parcouru. Un client paie $850$ FCFA. Quelle distance a-t-il parcourue ?

- a) $14$ km
- b) $20$ km
- c) $17$ km
- d) $700$ km

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour traduire une situation de tarification comportant un montant fixe et un montant proportionnel à une quantité inconnue $x$, on écrit une équation du premier degré de la forme $\text{montant fixe}+\text{taux}\times x=\text{montant total}$. On résout ensuite cette équation en isolant $x$, c'est-à-dire en effectuant les mêmes opérations sur les deux membres jusqu'à obtenir $x=\ldots$

### Corrigé

**1. Mise en équation.** Le prix payé est la somme de la prise en charge fixe et du coût des $x$ kilomètres parcourus à $50$ FCFA le kilomètre :
$$150+50x=850$$

**2. Résolution.** On isole le terme en $x$ :
$$50x=850-150$$
$$50x=700$$
$$x=\dfrac{700}{50}$$
$$x=14$$

**Vérification.** Pour $x=14$ : $150+50\times14=150+700=850$, ce qui correspond bien au prix payé.

**3. Conclusion.** Le client a parcouru $14$ kilomètres.

### Pourquoi les autres réponses sont fausses

- **b)** la prise en charge doit être retranchée du prix, et non ajoutée : $850-150=700$.
- **c)** la prise en charge de $150$ FCFA a été oubliée : $\dfrac{850}{50}=17$ ne tient pas compte du montant fixe.
- **d)** $700$ est le montant payé pour les kilomètres : il reste à le diviser par $50$ FCFA par kilomètre.


</details>

Avis : 

---

## 69. `cqc-etude-des-fonctions-tle-a-moyenne-3` (séries BAC:A)

**Remarque du relecteur :** Le choix a) 1/(3x-6) est un piège classique bien construit ; une seule bonne réponse.

**Énoncé :**

Soit $k$ la fonction définie sur $]2\,;+\infty[$ par $k(x)=\ln(3x-6)$. Quelle est l'expression de $k'(x)$ ?

- a) $k'(x)=\dfrac{1}{3x-6}$
- b) $k'(x)=\dfrac{1}{x-2}$
- c) $k'(x)=\dfrac{3}{x-2}$
- d) $k'(x)=-\dfrac{3}{(3x-6)^{2}}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Une expression $\ln(u(x))$ n'est définie que lorsque $u(x)>0$, ce qui détermine l'ensemble de définition. Les limites s'obtiennent ensuite par composition, à l'aide des limites de référence $\ln(t)\to-\infty$ quand $t\to0^+$ et $\ln(t)\to+\infty$ quand $t\to+\infty$. La dérivée de $\ln(u)$ vaut $\dfrac{u'}{u}$, dont le signe donne le sens de variation.

### Corrigé

**1. Ensemble de définition.** Une expression $\ln(u)$ n'est définie que lorsque $u>0$ :
$$3x-6>0 \iff x>2$$
$$D_k=\;]2;+\infty[$$

**2. Limites et asymptote.**

Quand $x\to2^+$, on a $3x-6\to0^+$, et $\ln(t)\to-\infty$ quand $t\to0^+$ (limite de référence). Par composition :
$$\lim_{x\to2^+}k(x)=-\infty$$

La droite d'équation $x=2$ est donc asymptote verticale à la courbe de $k$.

Quand $x\to+\infty$, on a $3x-6\to+\infty$, et $\ln(t)\to+\infty$ quand $t\to+\infty$. Donc :
$$\lim_{x\to+\infty}k(x)=+\infty$$

$k$ n'a pas de limite finie en $+\infty$ : il n'y a pas d'asymptote horizontale de ce côté.

**3. Dérivée et variations.** $k(x)=\ln(u(x))$ avec $u(x)=3x-6$, donc $k'(x)=\dfrac{u'(x)}{u(x)}$ :
$$k'(x)=\dfrac{3}{3x-6}=\dfrac{1}{x-2}$$

Pour tout $x\in D_k=\,]2;+\infty[$, on a $x-2>0$, donc $k'(x)>0$ : **$k$ est strictement croissante sur $]2;+\infty[$.**

### Pourquoi les autres réponses sont fausses

- **a)** la dérivée de $\ln(u)$ est $\dfrac{u'}{u}$ : le facteur $u'=3$ a été oublié.
- **c)** $\dfrac{u'}{u}=\dfrac{3}{3x-6}=\dfrac{1}{x-2}$ : le facteur $3$ a été compté deux fois.
- **d)** cette expression est la dérivée de $\dfrac{1}{3x-6}$ ; la dérivée de $\ln(u)$ est $\dfrac{u'}{u}$.


</details>

Avis : 

---

