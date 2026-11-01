# Vague 5b Maths Probatoire et BAC (questions communes aux deux examens) : 37 QCM à faire relire par l'enseignant (campagne B1)

Date : 2026-11-01. Sur 88 QCM convertis (220 questions étudiées, 132 écartées), **37** vous sont soumis : ceux que le relecteur aveugle a assortis d'une remarque, ceux dont des séries ont été retirées, et un tirage de 12 autres. Le lot est prêt mais n'est pas en ligne tant que vous n'avez pas répondu. Les 88 résolutions à l'aveugle ont toutes donné la clé. Cinq formulations ont été corrigées après la relecture (dimension d'un terrain, « quels points », « modélisé par » pour deux suites, mur assez long).

Ces questions sont posées à la fois au Probatoire et au BAC (séries indiquées pour chacune). Elles sont adaptées au niveau de la plus faible des séries concernées, avec le programme de Première. Beaucoup de questions à plusieurs sous-questions ont été réduites à une seule.

## Avis déjà rendus, appliqués par analogie (à confirmer)

- **Probatoire C et E retirés** des 6 questions « limite d'une suite » (suite géométrique, arithmético-géométrique, somme télescopique), conformément à votre avis sur la limite d'une suite géométrique en vague 5a ; elles restent pour le BAC C, D et E.
- Les questions sur les matrices, le noyau et les applications linéaires (série E seulement), les similitudes, le produit vectoriel, les nombres complexes, les coniques, les probabilités, les covariances et l'ajustement affine ont été **écartées** (non converties, laissées ouvertes).

## Points à trancher (nouveaux)

1. **Nombre dérivé et taux d'accroissement en série A** (`taux-d-accroissement` faible-0 et faible-1, `nombre-derive-tle-c-faible-0`) : au programme de la Première A ?
2. **Éléments de symétrie d'une courbe en série A** (axe x = a, centre de symétrie) : au programme ?
3. **Suites homographiques avec suite auxiliaire** (`suite-auxiliaire` moyenne-0, moyenne-1, elevee-0) : à la limite haute pour C, D, E ; on garde ou on retire la série D ?
4. **Limite par q^n et suite arithmético-géométrique** pour le BAC : confirmer.
5. **Homothétie en D et TI** (`lieu-geometrique-moyenne-0`).

Pour chaque question : **OK**, **à corriger** (dire quoi), **à retirer**, ou **retirer la série X**.

## 1. `cqc-ensemble-de-definition-prob-c-moyenne-2` (séries BAC:A PRO:A PRO:C)

**Énoncé :**

Quel est l'ensemble de définition de la fonction $f(x)=\sqrt{x^2-x-6}$ ?

- a) $[-2\,;3]$
- b) $]-\infty\,;-2]\cup[3\,;+\infty[$
- c) $]-\infty\,;-2[\cup]3\,;+\infty[$
- d) $]-\infty\,;-3]\cup[2\,;+\infty[$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On cherche $x^2-x-6\ge0$. On factorise le trinôme et on dresse un tableau de signes (du signe de $a$ à l'extérieur des racines).

### Corrigé

$x^2-x-6=(x-3)(x+2)$, racines $-2$ et $3$. Le trinôme est positif à l'extérieur des racines :
$D_f=]-\infty\,;-2]\cup[3\,;+\infty[$.

### Pourquoi les autres réponses sont fausses

- **a)** On a pris l'intervalle situé entre les racines, alors que le trinôme (de coefficient dominant positif) est positif à l'extérieur des racines.
- **c)** Les bornes $-2$ et $3$ sont à tort exclues : en ces valeurs le radicande vaut $0$ et $\sqrt0$ existe.
- **d)** Erreur de signe sur les racines : $(x-3)(x+2)$ s'annule en $3$ et $-2$, pas en $-3$ et $2$.

</details>

Avis : 

---

## 2. `cqc-inequation-du-second-degre-moyenne-1` (séries BAC:A PRO:A PRO:C PRO:E)

**Énoncé :**

On considère les fonctions $f$ et $g$ définies sur $\mathbb{R}$ par $f(x)=\dfrac{x^2+1}{3}$ et $g(x)=\dfrac{5x-1}{6}$. Quel est l'ensemble solution, dans $\mathbb{R}$, de l'inéquation $f(x)\geqslant g(x)$ ?

- a) $\left[1\,;\dfrac32\right]$
- b) $\left]-\infty\,;1\right]\cup\left[\dfrac32\,;+\infty\right[$
- c) $\left]-\infty\,;1\right[\cup\left]\dfrac32\,;+\infty\right[$
- d) $\left]-\infty\,;\dfrac{5-\sqrt{17}}4\right]\cup\left[\dfrac{5+\sqrt{17}}4\,;+\infty\right[$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour résoudre une inéquation de la forme $f(x)\geqslant g(x)$, on étudie le signe de la différence $f(x)-g(x)$ : résoudre $f(x)\geqslant g(x)$ revient à résoudre $f(x)-g(x)\geqslant0$. Lorsque $f$ et $g$ comportent des dénominateurs numériques distincts, on réduit d'abord la différence au même dénominateur avant d'étudier le signe du numérateur.

### Corrigé

$f(x)-g(x) = \dfrac{x^2+1}{3}-\dfrac{5x-1}{6} = \dfrac{2(x^2+1)-(5x-1)}{6} = \dfrac{2x^2-5x+3}{6}$

Le dénominateur $6$ étant strictement positif, le signe de $f(x)-g(x)$ est celui du numérateur $2x^2-5x+3$. L'inéquation $f(x)\geqslant g(x)$ équivaut donc à $2x^2-5x+3\geqslant0$.

Ici $a=2$, $b=-5$, $c=3$.

$\Delta = (-5)^2-4\times2\times3 = 25-24 = 1$

Comme $\Delta=1>0$, le trinôme admet deux racines réelles distinctes :

$x_1=\dfrac{5-\sqrt{1}}{4}=\dfrac{4}{4}=1$ et $x_2=\dfrac{5+\sqrt{1}}{4}=\dfrac{6}{4}=\dfrac{3}{2}$

Comme $a=2>0$, le trinôme $2x^2-5x+3$ est positif ou nul à l'extérieur de l'intervalle $\left[1\,;\,\frac{3}{2}\right]$, et strictement négatif entre ces deux valeurs. L'inégalité étant large, les racines sont incluses.

Vérification : pour $x=1$, $f(1)=\dfrac{1+1}{3}=\dfrac{2}{3}$ et $g(1)=\dfrac{5-1}{6}=\dfrac{2}{3}$, donc $f(1)=g(1)$, la borne est bien incluse ; pour $x=1{,}25$ (entre les racines), $f(1{,}25)\approx0{,}854$ et $g(1{,}25)\approx0{,}875$, donc $f(1{,}25)<g(1{,}25)$, ce qui confirme bien que cette valeur est exclue.

L'ensemble solution est $S = \,\left]-\infty\,;\,1\right]\cup\left[\dfrac{3}{2}\,;\,+\infty\right[$.

### Pourquoi les autres réponses sont fausses

- **a)** Le signe du trinôme $2x^2-5x+3$ (positif à l'extérieur des racines car $a=2>0$) a été mal appliqué : on a pris l'intervalle entre les racines.
- **c)** L'inégalité est large : en $x=1$ et $x=\dfrac32$ on a $f(x)=g(x)$, ces valeurs sont solutions.
- **d)** Erreur de parenthèses : on a calculé $2(x^2+1)-5x-1$ au lieu de $2(x^2+1)-(5x-1)$, ce qui change le trinôme et ses racines.

</details>

Avis : 

---

## 3. `cqc-fonction-homographique-prob-de-moyenne-3` (séries BAC:A PRO:A PRO:C PRO:D PRO:E)

**Énoncé :**

Quel est l'ensemble solution, dans $\mathbb{R}$, de l'inéquation $\dfrac{x-2}{x+1}\geq0$ ?

- a) $]-\infty\,;-1[\cup[2\,;+\infty[$
- b) $]-\infty\,;-1]\cup[2\,;+\infty[$
- c) $[-1\,;2]$
- d) $]-1\,;2]$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On étudie le signe du quotient à l'aide d'un tableau de signes (numérateur, dénominateur) ; le quotient est nul là où le numérateur est nul, et défini seulement là où le dénominateur est non nul.

### Corrigé

Numérateur : nul en $2$, positif pour $x>2$. Dénominateur : nul en $-1$, positif pour $x>-1$.
- $x<-1$ : $(-)/(-)=+$ ;
- $-1<x<2$ : $(-)/(+)=-$ ;
- $x>2$ : $(+)/(+)=+$ ; et le quotient s'annule en $x=2$.

$\dfrac{x-2}{x+1}\geq0\iff x\in]-\infty\,;-1[\,\cup\,[2\,;+\infty[$ ($-1$ est exclu).

### Pourquoi les autres réponses sont fausses

- **b)** La valeur $x=-1$ annule le dénominateur : elle est interdite et doit être exclue.
- **c)** Le signe du quotient a été inversé : il est positif à l'extérieur des racines, négatif entre elles.
- **d)** On a retenu l'intervalle où le quotient est négatif (sauf en $2$ où il s'annule) : confusion de signe dans le tableau.

</details>

Avis : 

---

## 4. `cqc-inequation-du-second-degre-moyenne-0` (séries BAC:A PRO:A PRO:C PRO:E)

**Énoncé :**

Une association d'élèves fabrique et vend des tee-shirts personnalisés à l'occasion de la cérémonie de fin d'année. Le bénéfice $B(n)$, exprimé en milliers de francs CFA, pour la vente de $n$ tee-shirts ($n$ entier, $0\leqslant n\leqslant70$, capacité maximale de l'atelier de sérigraphie), est modélisé par $B(n)=-n^2+60n-500$. Quels sont le nombre minimal et le nombre maximal de tee-shirts que l'association doit vendre pour réaliser un bénéfice strictement positif ?

- a) Minimum $10$ et maximum $50$
- b) Minimum $11$ et maximum $50$
- c) Minimum $10$ et maximum $49$
- d) Minimum $11$ et maximum $49$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour un problème concret modélisé par un trinôme, on traduit d'abord la condition recherchée (ici, un bénéfice strictement positif) par une inéquation du second degré, qu'on résout par l'étude du signe du trinôme. On interprète ensuite l'ensemble solution obtenu en tenant compte des contraintes propres au contexte, notamment lorsque la variable doit être un nombre entier.

### Corrigé

Le bénéfice est strictement positif lorsque $B(n)>0$, soit $-n^2+60n-500>0$.

Ici $a=-1$, $b=60$, $c=-500$.

$\Delta = 60^2-4\times(-1)\times(-500) = 3600-2000 = 1600$

Comme $\Delta=1600>0$, l'équation associée admet deux racines réelles distinctes. $\sqrt{1600}=40$.

$n_1=\dfrac{-60-40}{2\times(-1)}=\dfrac{-100}{-2}=50$ et $n_2=\dfrac{-60+40}{-2}=\dfrac{-20}{-2}=10$

On range les racines dans l'ordre croissant : $10$ et $50$. Comme $a=-1<0$, le trinôme $-n^2+60n-500$ est strictement négatif à l'extérieur de l'intervalle $[10\,;\,50]$, et strictement positif entre ces deux valeurs. L'inégalité étant stricte, les bornes sont exclues.

En restant dans le domaine d'étude $0\leqslant n\leqslant70$, l'ensemble solution de l'inéquation est $S = \,]10\,;\,50[$.

Vérification : pour $n=30$ (entre les racines), $B(30)=-900+1800-500=400>0$, le bénéfice est bien positif ; pour $n=10$, $B(10)=-100+600-500=0$, qui n'est pas strictement positif, la borne est donc bien exclue.

Comme $n$ désigne un nombre entier de tee-shirts, l'association doit en vendre au minimum $11$ et au maximum $49$ pour réaliser un bénéfice strictement positif.

### Pourquoi les autres réponses sont fausses

- **a)** Les bornes $10$ et $50$ donnent $B(n)=0$ : le bénéfice est nul, pas strictement positif.
- **b)** La borne $50$ est mal traitée : $B(50)=0$, le bénéfice n'est pas strictement positif, il faut s'arrêter à $49$.
- **c)** La borne $10$ est mal traitée : $B(10)=0$, le bénéfice n'est pas strictement positif, il faut commencer à $11$.

</details>

Avis : 

---

## 5. `cqc-lieu-geometrique-moyenne-0` (séries BAC:C BAC:D BAC:E BAC:TI PRO:C PRO:D PRO:E)

**Remarque du relecteur :** LIMITE : l'homothétie est rappelée dans l'énoncé mais n'est pas nécessaire ; vérifier qu'elle est connue en Première D et TI.

**Énoncé :**

Dans le plan muni d'un repère orthonormé $(O, I, J)$, on considère les points fixes $A(1\,;\,1)$ et $B(4\,;\,-1)$. À tout point $M(x\,;\,y)$ du plan distinct de $A$, on associe le point $M'$ défini par $\overrightarrow{BM'} = 2\overrightarrow{BM}$ ($M'$ est donc l'image de $M$ par l'homothétie de centre $B$ et de rapport $2$). Quel est l'ensemble $(T)$ des points $M$ distincts de $A$ tels que $A$, $M$ et $M'$ soient alignés ?

- a) La droite d'équation $2x+3y-5=0$, privée du point $A$
- b) La droite d'équation $y=1$, privée du point $A$
- c) La droite d'équation $y=x$, privée du point $A$
- d) Le plan tout entier, privé du point $A$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Trois points $A$, $M$, $M'$ sont alignés si et seulement si les vecteurs $\overrightarrow{AM}$ et $\overrightarrow{AM'}$ sont colinéaires, c'est-à-dire si leur déterminant est nul. Lorsque $M'$ est défini à partir de $M$ par une relation vectorielle simple (ici une homothétie), on exprime d'abord les coordonnées de $M'$ en fonction de celles de $M$, avant de traduire la colinéarité par un calcul de déterminant.

### Corrigé

La relation $\overrightarrow{BM'}=2\overrightarrow{BM}$ donne $M'-B=2(M-B)$, soit $M'=2M-B$. Avec $B(4\,;\,-1)$ et $M(x\,;\,y)$ :
$$M'(2x-4\,;\,2y+1)$$

On a alors $\overrightarrow{AM}=(x-1\,;\,y-1)$ et $\overrightarrow{AM'}=(2x-4-1\,;\,2y+1-1)=(2x-5\,;\,2y)$.

$A$, $M$, $M'$ sont alignés si et seulement si $\overrightarrow{AM}$ et $\overrightarrow{AM'}$ sont colinéaires :
$$(x-1)(2y) - (y-1)(2x-5) = 0$$
$$2xy-2y - \big(2xy-5y-2x+5\big) = 0$$
$$2xy-2y-2xy+5y+2x-5=0$$
$$2x+3y-5=0$$

L'ensemble $(T)$ est donc **la droite d'équation $2x+3y-5=0$, privée du point $A$** : en $M=A$, le vecteur $\overrightarrow{AM}$ est nul et l'alignement n'est plus défini.

### Pourquoi les autres réponses sont fausses

- **b)** Les coordonnées de $M'$ ont été obtenues avec $M'=2M+B$ au lieu de $2M-B$ : on trouve alors une autre droite, $y=1$.
- **c)** Le centre $B$ a été oublié (on a pris $M'=2M$, homothétie de centre $O$) : cela donne la droite $y=x$.
- **d)** On a confondu avec l'homothétie de centre $A$, pour laquelle $A$, $M$ et $M'$ sont toujours alignés ; ici le centre est $B$.

</details>

Avis : 

---

## 6. `cqc-lieu-geometrique-moyenne-2` (séries BAC:C BAC:D BAC:E BAC:TI PRO:C PRO:D PRO:E)

**Remarque du relecteur :** Formulation « ensemble réduit au seul point » un peu lourde pour une simple translation, mais correcte.

**Énoncé :**

Dans le plan muni d'un repère orthonormé $(O, I, J)$, on considère les points fixes $A(3\,;\,-2)$, $B(0\,;\,6)$, $C(-4\,;\,1)$ et $D(5\,;\,-3)$. On pose $\vec u = 2\overrightarrow{AB} - \overrightarrow{AC}$. Quel est l'ensemble des points $M$ du plan tels que $\overrightarrow{DM} = \vec u$ ?

- a) L'ensemble réduit au seul point $M(-8\,;16)$
- b) L'ensemble réduit au seul point $M(4\,;-16)$
- c) L'ensemble réduit au seul point $M(6\,;10)$
- d) L'ensemble réduit au seul point $M(13\,;7)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'un point $M$ doit vérifier une égalité vectorielle du type $\overrightarrow{DM}=\vec u$ avec $D$ fixe et $\vec u$ un vecteur fixe (indépendant de $M$), l'égalité de deux vecteurs équivaut à l'égalité de leurs coordonnées : elle détermine alors un unique point $M$, obtenu en ajoutant les coordonnées de $\vec u$ à celles de $D$.

### Corrigé

On calcule d'abord $\vec u$. $\overrightarrow{AB}=B-A=(0-3\,;\,6-(-2))=(-3\,;\,8)$ et $\overrightarrow{AC}=C-A=(-4-3\,;\,1-(-2))=(-7\,;\,3)$.

$$\vec u = 2\overrightarrow{AB}-\overrightarrow{AC} = 2(-3\,;\,8)-(-7\,;\,3) = (-6\,;\,16)-(-7\,;\,3) = (1\,;\,13)$$

L'égalité $\overrightarrow{DM}=\vec u$ s'écrit, pour $M(x\,;\,y)$ et $D(5\,;\,-3)$ :
$$(x-5\,;\,y-(-3)) = (1\,;\,13)$$

D'où $x-5=1$, soit $x=6$, et $y+3=13$, soit $y=10$.

L'ensemble cherché est donc réduit à **un unique point**, $M(6\,;\,10)$.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur $\overrightarrow{AC}$ : on a calculé $2\overrightarrow{AB}+\overrightarrow{AC}$ au lieu de $2\overrightarrow{AB}-\overrightarrow{AC}$.
- **b)** Le sens de l'égalité est inversé : on a calculé $D-\vec u$ au lieu de $D+\vec u$ (il faut $M=D+\vec u$ puisque $\overrightarrow{DM}=\vec u$).
- **d)** Le coefficient $2$ a été appliqué aux deux vecteurs : on a calculé $2(\overrightarrow{AB}-\overrightarrow{AC})$ au lieu de $2\overrightarrow{AB}-\overrightarrow{AC}$.

</details>

Avis : 

---

## 7. `cqc-limite-d-une-suite-elevee-0` (séries BAC:C BAC:D BAC:E PRO:C PRO:E)

**Série(s) retirée(s) par analogie avec vos avis :** PRO:C, PRO:E.

**Remarque du relecteur :** LIMITE : limite d'une suite via q^n -> 0 pour |q|<1, à la limite haute du programme de Première.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On considère la suite $(U_n)$ définie pour tout entier naturel $n$ par

$$U_n = \dfrac{3^{\,n+1}-2^{\,n}}{3^{\,n}+2^{\,n+1}}$$

Quelle est la limite de $(U_n)$ lorsque $n$ tend vers $+\infty$ ?

- a) $1$
- b) $3$
- c) $-\dfrac12$
- d) $+\infty$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour calculer la limite d'un quotient combinant plusieurs puissances $a^n$ de bases différentes, on factorise le numérateur et le dénominateur par la puissance de plus grande base (celle qui « domine » les autres à l'infini), ce qui fait apparaître des quotients de la forme $q^n$ avec $|q|<1$, dont la limite est $0$.

### Corrigé

On réécrit le numérateur et le dénominateur en isolant $3^n$ :

$$3^{\,n+1}-2^{\,n} = 3\times3^{\,n}-2^{\,n} \qquad\text{et}\qquad 3^{\,n}+2^{\,n+1} = 3^{\,n}+2\times2^{\,n}$$

On factorise ces deux expressions par $3^n$, la puissance de plus grande base (car $3>2$) :

$$3\times3^{\,n}-2^{\,n} = 3^{\,n}\left(3-\left(\dfrac23\right)^{n}\right) \qquad\text{et}\qquad 3^{\,n}+2\times2^{\,n} = 3^{\,n}\left(1+2\left(\dfrac23\right)^{n}\right)$$

En simplifiant par $3^n$ (non nul) :

$$U_n = \dfrac{3-\left(\dfrac23\right)^{n}}{1+2\left(\dfrac23\right)^{n}}$$

Comme $0<\dfrac23<1$, $\displaystyle\lim_{n\to+\infty}\left(\dfrac23\right)^{n}=0$, donc par quotient des limites (le dénominateur tendant vers $1\neq0$) :

$$\lim_{n\to+\infty} U_n = \dfrac{3-0}{1+2\times0} = \dfrac{3}{1} = 3$$

Vérification numérique : pour $n=5$, $3^6=729$, $2^5=32$, $3^5=243$, $2^6=64$, donc $U_5=\dfrac{729-32}{243+64}=\dfrac{697}{307}\approx2{,}270$ ; pour $n=10$, $3^{11}=177\,147$, $2^{10}=1\,024$, $3^{10}=59\,049$, $2^{11}=2\,048$, donc $U_{10}=\dfrac{177\,147-1\,024}{59\,049+2\,048}=\dfrac{176\,123}{61\,097}\approx2{,}883$, une valeur qui se rapproche bien de $3$.

### Pourquoi les autres réponses sont fausses

- **a)** On traite $3^{n+1}$ comme $3^n$ et $2^{n+1}$ comme $2^n$, ce qui donne $\dfrac{3^n-2^n}{3^n+2^n}\to1$ : on oublie les facteurs $3$ et $2$ du décalage d'indice.
- **c)** On ne garde que les termes en $2^n$ : $\dfrac{-2^n}{2\times2^n}=-\dfrac12$, alors que $3^n$ l'emporte sur $2^n$.
- **d)** On voit un numérateur « plus grand » sans remarquer que le dénominateur tend aussi vers $+\infty$ : c'est une forme indéterminée qu'il faut lever en factorisant.

</details>

Avis : 

---

## 8. `cqc-limite-d-une-suite-faible-0` (séries BAC:C BAC:D BAC:E PRO:C PRO:E)

**Série(s) retirée(s) par analogie avec vos avis :** PRO:C, PRO:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Pour tout entier naturel $n\geq1$, on pose

$$S_n = 1+2+3+\cdots+n \quad\text{et}\quad U_n = \dfrac{S_n}{3n^2-1}$$

Quelle est la limite de $(U_n)$ lorsque $n$ tend vers $+\infty$ ?

- a) $\dfrac13$
- b) $\dfrac12$
- c) $0$
- d) $\dfrac16$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'une suite est définie par une somme dont le nombre de termes dépend de $n$, on commence par remplacer cette somme par son expression close, ici donnée par la formule de Gauss $\displaystyle\sum_{i=1}^n i = \dfrac{n(n+1)}2$. On obtient alors un quotient de polynômes en $n$, dont la limite s'obtient en divisant numérateur et dénominateur par la plus haute puissance de $n$ présente au dénominateur.

### Corrigé

D'après la formule de Gauss, pour tout entier naturel $n\geq1$ :

$$S_n = 1+2+\cdots+n = \dfrac{n(n+1)}{2}$$

On a donc :

$$U_n = \dfrac{S_n}{3n^2-1} = \dfrac{\dfrac{n(n+1)}2}{3n^2-1} = \dfrac{n(n+1)}{2(3n^2-1)} = \dfrac{n^2+n}{6n^2-2}$$

En divisant numérateur et dénominateur par $n^2$ (la plus haute puissance de $n$ présente) :

$$U_n = \dfrac{1+\dfrac1n}{6-\dfrac2{n^2}}$$

Quand $n\to+\infty$, $\dfrac1n\to0$ et $\dfrac2{n^2}\to0$, donc :

$$\lim_{n\to+\infty} U_n = \dfrac{1+0}{6-0} = \dfrac16$$

Vérification numérique : pour $n=10$, $S_{10}=\dfrac{10\times11}2=55$, donc $U_{10}=\dfrac{55}{299}\approx0{,}184$ ; pour $n=100$, $S_{100}=\dfrac{100\times101}2=5050$, donc $U_{100}=\dfrac{5050}{29\,999}\approx0{,}1683$, une valeur qui se rapproche bien de $\dfrac16\approx0{,}1667$.

### Pourquoi les autres réponses sont fausses

- **a)** On oublie le facteur $\dfrac12$ de la formule de Gauss : $\dfrac{n(n+1)}{3n^2-1}\to\dfrac13$.
- **b)** On ne garde que $\dfrac{n^2}{2}$ au numérateur et on oublie le $3$ du dénominateur : $\dfrac{n^2/2}{n^2}\to\dfrac12$.
- **c)** On croit que $S_n$ est de degré $1$ (« $n$ termes ») : le quotient serait alors de degré $1$ sur degré $2$, mais $S_n$ est de degré $2$.

</details>

Avis : 

---

## 9. `cqc-limite-d-une-suite-faible-1` (séries BAC:C BAC:D BAC:E PRO:C PRO:E)

**Série(s) retirée(s) par analogie avec vos avis :** PRO:C, PRO:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On considère la suite $(U_n)$ définie pour tout entier naturel $n$ par $U_n = -2n^2+7n-1$.

Quelle est la limite de $(U_n)$ lorsque $n$ tend vers $+\infty$ ?

- a) $-\infty$
- b) $+\infty$
- c) $-2$
- d) $0$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour calculer la limite d'une suite définie par un polynôme en $n$, on factorise par le monôme de plus haut degré : celui-ci impose son comportement à l'infini, car tous les autres termes deviennent négligeables devant lui.

### Corrigé

Pour tout entier naturel $n\geq1$, on factorise par $n^2$ (le monôme de plus haut degré) :

$$U_n = -2n^2+7n-1 = n^2\left(-2+\dfrac7n-\dfrac1{n^2}\right)$$

Quand $n\to+\infty$, $\dfrac7n\to0$ et $\dfrac1{n^2}\to0$, donc le facteur entre parenthèses tend vers $-2$. Par ailleurs, $n^2\to+\infty$.

On a donc un produit dont un facteur tend vers $+\infty$ et l'autre vers une constante strictement négative ($-2$) : par la règle du produit des limites, ce produit tend vers $-\infty$.

$$\lim_{n\to+\infty} U_n = -\infty$$

Vérification numérique : $U_{10}=-200+70-1=-131$ ; $U_{100}=-20\,000+700-1=-19\,301$ ; $U_{1000}=-2\,000\,000+7\,000-1=-1\,993\,001$. La suite décroît bien sans borne, ce qui confirme une limite $-\infty$.

### Pourquoi les autres réponses sont fausses

- **b)** On oublie le signe du coefficient $-2$ de $n^2$.
- **c)** On confond la limite du facteur entre parenthèses ($-2$) avec celle de la suite : on oublie que $n^2$ tend vers $+\infty$.
- **d)** On croit que tous les termes disparaissent, par confusion avec les limites de $\dfrac1n$ et de $\dfrac1{n^2}$.

</details>

Avis : 

---

## 10. `cqc-limite-d-une-suite-moyenne-0` (séries BAC:C BAC:D BAC:E PRO:C PRO:E)

**Série(s) retirée(s) par analogie avec vos avis :** PRO:C, PRO:E.

**Remarque du relecteur :** LIMITE : demande la limite d'une suite arithmético-géométrique (convergence de q^n avec |q|<1), notion en haut du programme de Première, formulée sans le mot limite.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Un bassin de pisciculture contient initialement $500$ kg de poissons. Chaque mois, du fait de la pêche, on prélève $30\%$ de la biomasse présente, puis un élevage complémentaire y ajoute $84$ kg de nouveaux poissons. On note $U_n$ la biomasse (en kg) présente dans le bassin au bout de $n$ mois, avec $U_0=500$, et on admet que, pour tout entier naturel $n$, $U_{n+1}=0{,}7\,U_n+84$.

Vers quelle valeur (en kg) la biomasse $U_n$ se rapproche-t-elle quand $n$ devient très grand ?

- a) $120$
- b) $500$
- c) $280$
- d) $84$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Une suite arithmético-géométrique $U_{n+1}=aU_n+b$ (avec $a\neq1$) se ramène à une suite géométrique en posant $V_n=U_n-\ell$, où $\ell$ vérifie $\ell=a\ell+b$ ; $(V_n)$ est alors géométrique de raison $a$, ce qui donne une expression explicite de $U_n$ et permet d'en déterminer la limite : si $|a|<1$, $a^n\to0$ et $U_n$ tend vers $\ell$.

### Corrigé

On pose, pour tout entier naturel $n$, $V_n=U_n-280$ (où $280$ vérifie $\ell=0{,}7\ell+84$). Pour tout entier naturel $n$ :

$$V_{n+1}=U_{n+1}-280=(0{,}7\,U_n+84)-280=0{,}7\,U_n-196=0{,}7\,(U_n-280)=0{,}7\,V_n$$

Donc, pour tout entier naturel $n$, $V_{n+1}=0{,}7\,V_n$ : $(V_n)$ est géométrique de raison $q=0{,}7$, de premier terme $V_0=U_0-280=500-280=220$.

Pour tout entier naturel $n$, $V_n=V_0\times q^n=220\times0{,}7^{\,n}$, donc :

$$U_n=V_n+280=280+220\times0{,}7^{\,n}$$

Vérification : $U_1=280+220\times0{,}7=280+154=434$ ; directement, $U_1=0{,}7\times500+84=350+84=434$, ce qui concorde.

Comme $0<0{,}7<1$, $\displaystyle\lim_{n\to+\infty}0{,}7^{\,n}=0$, donc :

$$\lim_{n\to+\infty} U_n = 280+220\times0=280$$

La biomasse du bassin tend donc à se stabiliser autour de $280$ kg, quel que soit le nombre de mois écoulés.

### Pourquoi les autres réponses sont fausses

- **a)** On résout $\ell=0{,}7\ell+84$ en écrivant $\ell=\dfrac{84}{0{,}7}$ au lieu de $\ell=\dfrac{84}{1-0{,}7}$.
- **b)** On pense que la biomasse reste égale à sa valeur initiale.
- **d)** On prend l'apport mensuel de $84$ kg pour la valeur limite.

</details>

Avis : 

---

## 11. `cqc-limite-d-une-suite-moyenne-1` (séries BAC:C BAC:D BAC:E PRO:C PRO:E)

**Série(s) retirée(s) par analogie avec vos avis :** PRO:C, PRO:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On considère la suite $(U_n)$ définie pour tout entier naturel $n\geq1$ par

$$U_n = n\times\left(\dfrac13\right)^{n} + \dfrac{2n+5}{n}$$

On admet que $\displaystyle\lim_{n\to+\infty} n\left(\dfrac13\right)^{n} = 0$.

Quelle est la limite de $(U_n)$ lorsque $n$ tend vers $+\infty$ ?

- a) $2$
- b) $0$
- c) $+\infty$
- d) $7$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour calculer la limite d'une somme de deux termes, on détermine séparément la limite de chaque terme, puis on additionne les résultats obtenus (théorème sur la limite d'une somme), à condition qu'aucune des deux limites ne conduise à une forme indéterminée du type $\infty-\infty$. Un résultat de croissance comparée comme $n\,q^n\to0$ pour $|q|<1$ est souvent admis et directement réutilisable dans ce genre de calcul.

### Corrigé

On étudie séparément les deux termes de $U_n$.

**Premier terme.** Par hypothèse, $\displaystyle\lim_{n\to+\infty} n\left(\dfrac13\right)^{n} = 0$.

**Second terme.** Pour tout entier naturel $n\geq1$ :

$$\dfrac{2n+5}{n} = 2+\dfrac5n$$

Quand $n\to+\infty$, $\dfrac5n\to0$, donc $\displaystyle\lim_{n\to+\infty}\dfrac{2n+5}{n} = 2$.

**Somme.** Par somme des limites :

$$\lim_{n\to+\infty} U_n = 0+2 = 2$$

Vérification numérique : pour $n=10$, $10\times\left(\frac13\right)^{10}\approx0{,}00017$, et $\dfrac{25}{10}=2{,}5$, donc $U_{10}\approx2{,}500$ ; pour $n=20$, le premier terme est encore plus proche de $0$ et $\dfrac{45}{20}=2{,}25$, donc $U_{20}\approx2{,}25$ : la suite se rapproche bien de $2$.

### Pourquoi les autres réponses sont fausses

- **b)** On pense que $\dfrac{2n+5}{n}$ tend aussi vers $0$, par confusion avec $\dfrac5n$.
- **c)** Le numérateur $2n+5$ tend vers $+\infty$, on en conclut que le quotient aussi, sans diviser par $n$.
- **d)** On additionne les coefficients $2$ et $5$ en oubliant que $\dfrac5n$ tend vers $0$.

</details>

Avis : 

---

## 12. `cqc-limite-d-une-suite-moyenne-2` (séries BAC:C BAC:D BAC:E PRO:C PRO:E)

**Série(s) retirée(s) par analogie avec vos avis :** PRO:C, PRO:E.

**Remarque du relecteur :** LIMITE : notation Sigma et somme télescopique, à la limite haute pour la Première.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Pour tout entier naturel $n$, on pose $b_n = 4\times\left(\dfrac25\right)^{n}$, et pour tout entier naturel $n\geq1$ :

$$S_n = \sum_{k=0}^{n-1}\left(b_k-b_{k+1}\right)$$

Quelle est la limite de $(S_n)$ lorsque $n$ tend vers $+\infty$ ?

- a) $0$
- b) $\dfrac{20}{3}$
- c) $\dfrac{12}{5}$
- d) $4$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans une somme télescopique $\displaystyle\sum_{k=0}^{n-1}(b_k-b_{k+1})$, chaque terme intermédiaire $b_1, b_2, \ldots, b_{n-1}$ apparaît une fois avec le signe $+$ (comme terme $b_k$) et une fois avec le signe $-$ (comme terme $b_{k+1}$ du rang précédent) : ces termes s'annulent deux à deux, et il ne reste que le tout premier terme $b_0$ et le tout dernier $-b_n$. Si $(b_n)$ est explicite, notamment géométrique de raison $|q|<1$, on en déduit directement la limite de la somme.

### Corrigé

En écrivant les premiers termes de la somme :

$$S_n = (b_0-b_1)+(b_1-b_2)+(b_2-b_3)+\cdots+(b_{n-1}-b_n)$$

Chaque terme $b_1$, $b_2$, ..., $b_{n-1}$ apparaît une fois avec le signe $+$ et une fois avec le signe $-$ : ces termes s'annulent deux à deux, et il ne reste que $b_0$ (avec le signe $+$) et $b_n$ (avec le signe $-$). Donc $S_n=b_0-b_n$. Comme $b_n=4\times\left(\dfrac25\right)^{n}$, on a $b_0=4\times\left(\dfrac25\right)^{0}=4$, donc :

$$S_n = 4-4\times\left(\dfrac25\right)^{n}$$

Comme $0<\dfrac25<1$, $\displaystyle\lim_{n\to+\infty}\left(\dfrac25\right)^{n}=0$, donc :

$$\lim_{n\to+\infty} S_n = 4-4\times0 = 4$$

Vérification numérique : $b_0=4$, $b_1=4\times0{,}4=1{,}6$, $b_2=4\times0{,}16=0{,}64$. Donc $S_2=(b_0-b_1)+(b_1-b_2)=b_0-b_2=4-0{,}64=3{,}36$, ce qui coïncide avec la formule $S_2=4-4\times(0{,}4)^2=4-0{,}64=3{,}36$ ; cette valeur se rapproche progressivement de $4$ quand $n$ augmente.

### Pourquoi les autres réponses sont fausses

- **a)** On pense que, chaque terme $b_k-b_{k+1}$ tendant vers $0$, la somme tend vers $0$ : on oublie que le nombre de termes augmente.
- **b)** On applique la somme d'une suite géométrique, $\dfrac{4}{1-\frac25}$, alors que la somme n'est pas celle des $b_k$ mais celle des différences.
- **c)** On ne retient que le premier terme de la somme : $b_0-b_1=4-\dfrac85=\dfrac{12}{5}$.

</details>

Avis : 

---

## 13. `cqc-nombre-derive-tle-c-faible-0` (séries BAC:A BAC:C BAC:D BAC:E PRO:A PRO:C)

**Remarque du relecteur :** LIMITE : nombre dérivé par limite du taux d'accroissement en série A, à confirmer au programme de Première A.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=x^2-3x$. À l'aide de la définition du nombre dérivé (limite du taux d'accroissement), quel est le nombre dérivé de $f$ en $2$ ?

- a) $-2$
- b) $4$
- c) $1$
- d) $7$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Le nombre dérivé de $f$ en $a$ est la limite, si elle existe et est finie, du taux d'accroissement : $f'(a)=\lim\limits_{h\to0}\dfrac{f(a+h)-f(a)}{h}$.

### Corrigé

$f(2)=4-6=-2$ et $f(2+h)=(2+h)^2-3(2+h)=4+4h+h^2-6-3h=-2+h+h^2$.

$$\dfrac{f(2+h)-f(2)}{h}=\dfrac{h+h^2}{h}=1+h\xrightarrow[h\to0]{}1.$$
Donc $f$ est dérivable en $2$ et $f'(2)=1$. (On retrouve $f'(x)=2x-3$ et $f'(2)=1$.)

### Pourquoi les autres réponses sont fausses

- **a)** On donne la valeur $f(2)=-2$ au lieu de la limite du taux d'accroissement.
- **b)** On oublie le terme $-3x$ : on obtient la dérivée de $x^2$ seule, $2\times2=4$.
- **d)** Erreur de signe : on écrit $f'(x)=2x+3$ au lieu de $2x-3$.

</details>

Avis : 

---

## 14. `cqc-optimisation-prob-d-moyenne-2` (séries BAC:TI PRO:D)

**Remarque du relecteur :** VOCABULAIRE : le minimum est atteint pour un carré, la « largeur » x n'est alors plus distincte de la longueur ; préciser « l'une des dimensions ».

**Énoncé :**

Une coopérative veut clôturer un terrain rectangulaire d'aire $200\ \text{m}^2$ avec la longueur de clôture la plus petite possible. On note $x$ l'une des dimensions du terrain (en m) et $P(x)$ son périmètre. Pour quelle valeur de $x$ le périmètre $P(x)$ est-il minimal ?

- a) $100$
- b) $20$
- c) $10$
- d) $10\sqrt2$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Avec l'aire fixée, la longueur vaut $\dfrac{200}x$ : le périmètre est $P(x)=2x+\dfrac{400}x$. On dérive et on étudie le signe de $P'$ pour trouver le minimum.

### Corrigé

$P(x)=2\left(x+\dfrac{200}x\right)=2x+\dfrac{400}x$ pour $x>0$. $P'(x)=2-\dfrac{400}{x^2}=\dfrac{2(x^2-200)}{x^2}$, négative pour $x<\sqrt{200}$ et positive ensuite : le minimum est en $x=\sqrt{200}=10\sqrt2\approx14{,}14$ m.
La longueur vaut alors $\dfrac{200}{10\sqrt2}=10\sqrt2$ : le terrain optimal est un **carré** de côté $10\sqrt2$ m, avec un périmètre minimal $P=40\sqrt2\approx56{,}6$ m.

### Pourquoi les autres réponses sont fausses

- **a)** On résout $x^2=200$ en écrivant $x=\dfrac{200}{2}$ : on oublie la racine carrée.
- **b)** On résout $x^2=400$ (on garde le numérateur $400$ de $\dfrac{400}{x}$ sans le diviser par $2$).
- **c)** On résout $x^2=100$ : on prend la moitié de l'aire au lieu de l'aire entière.

</details>

Avis : 

---

## 15. `cqc-optimisation-prob-d-moyenne-4` (séries BAC:TI PRO:D)

**Remarque du relecteur :** On suppose implicitement le mur assez long (au moins 30 m) ; on pourrait le préciser.

**Énoncé :**

Un agriculteur dispose de $60$ m de grillage pour clôturer un enclos rectangulaire adossé à un mur (le mur, assez long, remplace un des côtés). Quelle est l'aire maximale de l'enclos, en $\text{m}^2$ ?

- a) $225$
- b) $900$
- c) $450$
- d) $400$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Si $x$ est la longueur des deux côtés perpendiculaires au mur, le côté parallèle au mur mesure $60-2x$ : l'aire est $A(x)=x(60-2x)$. On cherche son maximum.

### Corrigé

$A(x)=x(60-2x)=-2x^2+60x$ pour $0<x<30$. Maximum en $x=-\dfrac{60}{2\times(-2)}=15$ : $A(15)=15\times30=450\ \text{m}^2$.
L'enclos optimal mesure $15$ m (côtés perpendiculaires au mur) sur $30$ m (côté parallèle au mur).

### Pourquoi les autres réponses sont fausses

- **a)** On clôture les quatre côtés : le carré de côté $15$ m a pour aire $225\ \text{m}^2$, mais le mur remplace un côté.
- **b)** On prend un carré de côté $30$ m, ce qui exigerait $90$ m de grillage.
- **d)** On prend trois côtés égaux de $20$ m, ce qui n'est pas la répartition qui rend l'aire maximale.

</details>

Avis : 

---

## 16. `cqc-principe-multiplicatif-prob-a-moyenne-4` (séries BAC:TI PRO:A)

**Énoncé :**

Une plaque d'immatriculation est formée de $2$ lettres (parmi $26$) suivies de $2$ chiffres. Les lettres et les chiffres peuvent se répéter. Combien de plaques peut-on former ?

- a) $58\,500$
- b) $6\,760$
- c) $776$
- d) $67\,600$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Quatre étapes : $26$ choix pour chaque lettre, $10$ pour chaque chiffre.

### Corrigé

$26\times26\times10\times10=67\,600$ plaques.

### Pourquoi les autres réponses sont fausses

- **a)** $58\,500=26\times25\times10\times9$ suppose à tort que les lettres et les chiffres ne peuvent pas se répéter.
- **b)** $6\,760=26\times26\times10$ oublie une des quatre étapes (un seul chiffre au lieu de deux).
- **c)** $776=26^2+10^2$ additionne les possibilités au lieu de les multiplier.

</details>

Avis : 

---

## 17. `cqc-repere-orthogonal-faible-0` (séries BAC:C BAC:D BAC:E BAC:TI PRO:C PRO:E)

**Remarque du relecteur :** Parler d'orthonormé pour des axes de grandeurs différentes (mois, francs) est un peu artificiel, mais la réponse attendue reste claire.

**Énoncé :**

Pour représenter, dans un repère du plan, l'évolution du chiffre d'affaires mensuel d'une boutique, une élève trace deux axes perpendiculaires. Sur l'axe des abscisses, elle choisit $1\text{ cm}$ pour représenter $1$ mois. Sur l'axe des ordonnées, elle choisit $1\text{ cm}$ pour représenter $50\,000$ francs CFA.

Quelle affirmation est exacte pour le repère ainsi construit ?

- a) Le repère est orthogonal, mais il n'est pas orthonormé.
- b) Le repère est orthonormé, car les deux axes sont perpendiculaires.
- c) Le repère n'est ni orthogonal ni orthonormé, car les unités sont différentes sur les deux axes.
- d) Le repère est orthonormé, car chaque axe est gradué avec une unité régulière.

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Un repère est **orthogonal** dès que ses deux axes sont perpendiculaires, quelles que soient les unités choisies sur chacun. Il est **orthonormé** si, en plus, la même longueur sur le papier représente la même valeur sur les deux axes (même unité graphique).

### Corrigé
Les deux axes sont perpendiculaires par construction : le repère est **orthogonal**.

Les unités diffèrent d'un axe à l'autre : $1\text{ cm}$ représente $1$ en abscisse et $50\,000$ en ordonnée. Ces valeurs ne sont pas égales : le repère n'est **pas orthonormé**.

Le repère est orthogonal, mais pas orthonormé.

### Pourquoi les autres réponses sont fausses
- **b)** on confond orthonormé et orthogonal : la perpendicularité des axes ne suffit pas pour un repère orthonormé.
- **c)** on croit que des unités différentes détruisent l'orthogonalité, alors que celle-ci ne dépend que de l'angle entre les axes.
- **d)** une graduation régulière sur chaque axe ne suffit pas : il faut la même unité graphique sur les deux axes.

</details>

Avis : 

---

## 18. `cqc-resolution-d-equation-prob-a-moyenne-3` (séries BAC:A PRO:A)

**Énoncé :**

On considère dans $\mathbb R$ les deux équations $(E_1)$ : $x^2-9=0$ et $(E_2)$ : $x^2=-4$. Quelle affirmation est exacte ?

- a) $(E_1)$ a pour ensemble de solutions $\{3\}$ et $(E_2)$ n'a aucune solution réelle.
- b) $(E_1)$ a pour ensemble de solutions $\{-3\,;3\}$ et $(E_2)$ a pour ensemble de solutions $\{-2\,;2\}$.
- c) $(E_1)$ a pour ensemble de solutions $\{-3\,;3\}$ et $(E_2)$ n'a aucune solution réelle.
- d) $(E_1)$ a pour ensemble de solutions $\{-9\,;9\}$ et $(E_2)$ n'a aucune solution réelle.

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
$x^2-9=(x-3)(x+3)$ ; un carré est toujours positif ou nul.

### Corrigé
$x^2-9=0\iff(x-3)(x+3)=0\iff x=3$ ou $x=-3$. Donc $S_1=\{-3\,;3\}$.

$x^2=-4$ n'a **aucune solution réelle**, car un carré ne peut pas être négatif.

### Pourquoi les autres réponses sont fausses
- **a)** on oublie la solution négative $-3$ de $x^2=9$.
- **b)** on traite $x^2=-4$ comme $x^2=4$ en ignorant le signe : un carré n'est jamais négatif.
- **d)** on prend $9$ pour la racine au lieu de $\sqrt9=3$ : $x^2=9$ donne $x=\pm3$.

</details>

Avis : 

---

## 19. `cqc-signe-elevee-5` (séries BAC:D PRO:C PRO:E)

**Remarque du relecteur :** Le distracteur a) (oubli de x = 2) est bien choisi.

**Énoncé :**

On considère l'expression $U(x) = \dfrac{(x-2)^2(3-x)}{x+5}$, définie pour tout réel $x \neq -5$.

Quel est l'ensemble des réels $x$ pour lesquels $U(x)\geq0$ ?

- a) $]-5\,;2[\,\cup\,]2\,;3]$
- b) $]-\infty\,;-5[\,\cup\,[3\,;+\infty[$
- c) $]-5\,;3]$
- d) $[-5\,;3]$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour étudier le signe d'un quotient, on étudie le signe de chaque facteur puis on les combine. Un carré comme $(x-2)^2$ est positif ou nul : il ne change pas de signe, mais il s'annule en $x=2$. La valeur qui annule le dénominateur est exclue.

### Corrigé
**Signes des facteurs.** $(x-2)^2\geq0$, nul seulement en $2$. $3-x>0$ pour $x<3$, nul en $3$, négatif au-delà. $x+5>0$ pour $x>-5$ et $x+5<0$ pour $x<-5$.

**Signe de $U(x)$.**
- $x<-5$ : numérateur positif, dénominateur négatif, donc $U(x)<0$ ;
- $-5<x<2$ ou $2<x<3$ : numérateur positif, dénominateur positif, donc $U(x)>0$ ;
- $x=2$ et $x=3$ : $U(x)=0$ ;
- $x>3$ : numérateur négatif, dénominateur positif, donc $U(x)<0$.

Ainsi $U(x)\geq0\iff x\in\,]-5\,;3]$ (les valeurs $2$ et $3$ annulent $U$ et conviennent pour $\geq$).

### Pourquoi les autres réponses sont fausses
- **a)** on exclut $x=2$ en croyant que le carré rend le quotient non défini ou strictement positif ; or $U(2)=0$ convient pour $\geq$.
- **b)** on prend l'ensemble où $U(x)\leq0$ (signes inversés) au lieu de celui où $U(x)\geq0$.
- **d)** on inclut la valeur interdite $-5$, où l'expression n'est pas définie.

</details>

Avis : 

---

## 20. `cqc-signe-moyenne-2` (séries BAC:D PRO:C PRO:E)

**Énoncé :**

On considère l'expression $R(x) = \dfrac{-5x+10}{x^2+7}$, définie pour tout réel $x$.

Quel est l'ensemble des réels $x$ pour lesquels $R(x)\geq0$ ?

- a) $[2\,;+\infty[$
- b) $]-\infty\,;2[$
- c) $]-\infty\,;-2]$
- d) $]-\infty\,;2]$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour le signe d'un quotient, on étudie séparément le numérateur et le dénominateur. Ici le dénominateur $x^2+7\geq7>0$ ne s'annule jamais et reste strictement positif : le signe du quotient est celui du numérateur.

### Corrigé
**Dénominateur.** Pour tout réel $x$, $x^2\geq0$ donc $x^2+7>0$.

**Numérateur.** $-5x+10=0\iff x=2$ ; le coefficient de $x$ est négatif, donc $-5x+10>0$ pour $x<2$ et $-5x+10<0$ pour $x>2$.

**Conclusion.** $R(x)>0$ pour $x<2$, $R(2)=0$, $R(x)<0$ pour $x>2$. Donc $R(x)\geq0\iff x\in\,]-\infty\,;2]$.

### Pourquoi les autres réponses sont fausses
- **a)** on se trompe de sens : le coefficient de $x$ au numérateur est négatif, donc l'expression est positive avant $2$ et non après.
- **b)** on oublie que $R(2)=0$ convient pour l'inégalité large $\geq$.
- **c)** on résout $-5x+10=0$ avec une erreur de signe et on trouve $x=-2$ au lieu de $x=2$.

</details>

Avis : 

---

## 21. `cqc-suite-auxiliaire-elevee-0` (séries BAC:C BAC:D BAC:E PRO:C PRO:D PRO:E)

**Remarque du relecteur :** LIMITE : suite homographique avec suite auxiliaire, à la limite haute (surtout pour la série D). Formulation « pour tout n tel que U_n != -1 » maladroite : mieux vaut admettre que la suite est bien définie.

**Énoncé :**

On considère la suite $(U_n)$ définie par $U_0=2$ et, pour tout entier naturel $n$ tel que $U_n\neq-1$, $U_{n+1} = \dfrac{3U_n+24}{U_n+1}$. Soient $\alpha$ et $\beta$ (avec $\alpha>\beta$) les deux solutions de l'équation $x=\dfrac{3x+24}{x+1}$. On pose $V_n = \dfrac{U_n-\alpha}{U_n-\beta}$ et on admet que $(V_n)$ est une suite géométrique. Quelles sont sa raison $q$ et son premier terme $V_0$ ?

- a) $q=\dfrac37$ et $V_0=-\dfrac23$
- b) $q=-\dfrac37$ et $V_0=-\dfrac23$
- c) $q=-\dfrac37$ et $V_0=\dfrac23$
- d) $q=-\dfrac73$ et $V_0=-\dfrac32$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On cherche d'abord les deux réels $\alpha$ et $\beta$ en réduisant l'équation $x=\dfrac{3x+24}{x+1}$ au même dénominateur (équation du second degré). On calcule ensuite $U_{n+1}-\alpha$ et $U_{n+1}-\beta$ à partir de la récurrence : les deux expressions ont le même dénominateur $U_n+1$, qui se simplifie dans le quotient $V_{n+1}$.

### Corrigé

**Valeurs de $\alpha$ et $\beta$.** $x(x+1)=3x+24 \iff x^2-2x-24=0$. Le discriminant vaut $\Delta=4+96=100$, d'où $x=\dfrac{2\pm10}{2}$, soit $x=6$ ou $x=-4$. Avec $\alpha>\beta$ : $\alpha=6$, $\beta=-4$ et $V_n=\dfrac{U_n-6}{U_n+4}$.

**Raison.**
$$U_{n+1}-6=\dfrac{3U_n+24-6(U_n+1)}{U_n+1}=\dfrac{-3(U_n-6)}{U_n+1},\qquad U_{n+1}+4=\dfrac{3U_n+24+4(U_n+1)}{U_n+1}=\dfrac{7(U_n+4)}{U_n+1}.$$
Donc $V_{n+1}=\dfrac{-3(U_n-6)}{7(U_n+4)}=-\dfrac37\,V_n$ : la raison est $q=-\dfrac37$.

**Premier terme.** $V_0=\dfrac{U_0-6}{U_0+4}=\dfrac{2-6}{2+4}=-\dfrac23$.

Réponse : $q=-\dfrac37$ et $V_0=-\dfrac23$.

### Pourquoi les autres réponses sont fausses
- **a)** le signe de $-3$ dans $U_{n+1}-6=\dfrac{-3(U_n-6)}{U_n+1}$ a été perdu, ce qui donne une raison positive.
- **c)** la raison est correcte mais $V_0$ est calculé avec une erreur de signe : $U_0-6=2-6=-4$, et non $4$.
- **d)** $\alpha$ et $\beta$ ont été intervertis, ce qui revient à considérer l'inverse de $V_n$ : raison et premier terme sont alors inversés.

</details>

Avis : 

---

## 22. `cqc-suite-auxiliaire-moyenne-0` (séries BAC:C BAC:D BAC:E PRO:C PRO:D PRO:E)

**Remarque du relecteur :** LIMITE : suite homographique avec suite auxiliaire, haut du programme de Première C/E ; plutôt calculatoire pour un QCM.

**Énoncé :**

On considère la suite $(U_n)$ définie par $U_0 = 1$ et, pour tout entier naturel $n$, $U_{n+1} = \dfrac{3U_n+8}{U_n+1}$. On admet que $4$ et $-2$ sont les deux solutions de l'équation $x=\dfrac{3x+8}{x+1}$ et on introduit la suite $(V_n)$ définie par $V_n = \dfrac{U_n-4}{U_n+2}$. Quelle est l'expression de $U_n$ en fonction de $n$ ?

- a) $U_n=\dfrac{4+2\left(-\frac15\right)^n}{1-\left(-\frac15\right)^n}$
- b) $U_n=\dfrac{4-2\left(-\frac15\right)^n}{1-\left(-\frac15\right)^n}$
- c) $U_n=\dfrac{4+2\left(-\frac15\right)^n}{1+\left(-\frac15\right)^n}$
- d) $U_n=\dfrac{4-2\left(-\frac15\right)^n}{1+\left(-\frac15\right)^n}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule $U_{n+1}-4$ et $U_{n+1}+2$ en réduisant au même dénominateur $U_n+1$ : le quotient donne $V_{n+1}=q\,V_n$, donc $(V_n)$ est géométrique. On écrit alors $V_n=V_0\,q^n$, puis on résout $V_n=\dfrac{U_n-4}{U_n+2}$ par rapport à $U_n$.

### Corrigé

$$U_{n+1}-4=\dfrac{-(U_n-4)}{U_n+1},\qquad U_{n+1}+2=\dfrac{5(U_n+2)}{U_n+1}$$
donc $V_{n+1}=-\dfrac15\,V_n$ : $(V_n)$ est géométrique de raison $-\dfrac15$, avec $V_0=\dfrac{1-4}{1+2}=-1$. Ainsi $V_n=-\left(-\dfrac15\right)^n$.

De $V_n(U_n+2)=U_n-4$ on tire $U_n(V_n-1)=-4-2V_n$, c'est-à-dire $U_n=\dfrac{4+2V_n}{1-V_n}$. En remplaçant $V_n$ :
$$U_n=\dfrac{4-2\left(-\frac15\right)^n}{1+\left(-\frac15\right)^n}.$$
Contrôle : $n=0$ donne $\dfrac{4-2}{1+1}=1=U_0$.

### Pourquoi les autres réponses sont fausses
- **a)** $V_n$ a été pris égal à $+\left(-\frac15\right)^n$ au lieu de $-\left(-\frac15\right)^n$ (signe de $V_0=-1$ oublié). Cette expression n'est même pas définie pour $n=0$.
- **b)** erreur de signe au dénominateur lors de la résolution : $1-V_n$ devient $1-\left(-\frac15\right)^n$ au lieu de $1+\left(-\frac15\right)^n$.
- **c)** signe faux au numérateur : $2V_n=-2\left(-\frac15\right)^n$, donc le numérateur est $4-2\left(-\frac15\right)^n$ et non $4+2\left(-\frac15\right)^n$.

</details>

Avis : 

---

## 23. `cqc-suite-auxiliaire-moyenne-1` (séries BAC:C BAC:D BAC:E PRO:C PRO:D PRO:E)

**Remarque du relecteur :** LIMITE : suite homographique avec suite auxiliaire, haut de programme pour la série D ; U_n ne vaut jamais 3 (il faudrait V_n=-1/2), la suite est donc bien définie.

**Énoncé :**

On considère la suite $(U_n)$ définie par $U_0 = 6$ et, pour tout entier naturel $n$ tel que $U_n\neq3$, $U_{n+1} = \dfrac{U_n+5}{U_n-3}$. On admet que $5$ et $-1$ sont les deux solutions de l'équation $x=\dfrac{x+5}{x-3}$ et on introduit la suite $(V_n)$ définie par $V_n = \dfrac{U_n-5}{U_n+1}$. On admet que $(V_n)$ est géométrique. Quelles sont sa raison $q$ et son premier terme $V_0$ ?

- a) $q=-2$ et $V_0=\dfrac17$
- b) $q=2$ et $V_0=\dfrac17$
- c) $q=-2$ et $V_0=7$
- d) $q=-\dfrac12$ et $V_0=\dfrac17$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule $U_{n+1}-5$ et $U_{n+1}+1$ séparément à partir de la récurrence : les deux expressions ont le même dénominateur $U_n-3$, qui disparaît dans le quotient $V_{n+1}=\dfrac{U_{n+1}-5}{U_{n+1}+1}$.

### Corrigé

$$U_{n+1}-5=\dfrac{U_n+5-5(U_n-3)}{U_n-3}=\dfrac{-4(U_n-5)}{U_n-3},\qquad U_{n+1}+1=\dfrac{U_n+5+(U_n-3)}{U_n-3}=\dfrac{2(U_n+1)}{U_n-3}.$$
Donc $V_{n+1}=\dfrac{-4(U_n-5)}{2(U_n+1)}=-2\,V_n$ : la raison est $q=-2$.

Premier terme : $V_0=\dfrac{6-5}{6+1}=\dfrac17$.

Réponse : $q=-2$ et $V_0=\dfrac17$.

### Pourquoi les autres réponses sont fausses
- **b)** le signe de $-4$ dans $U_{n+1}-5=\dfrac{-4(U_n-5)}{U_n-3}$ a été perdu : la raison est négative.
- **c)** $V_0$ a été calculé en inversant le quotient : $\dfrac{U_0+1}{U_0-5}=7$ au lieu de $\dfrac{U_0-5}{U_0+1}=\dfrac17$.
- **d)** le quotient des coefficients a été inversé : $\dfrac{-4}{2}=-2$ et non $\dfrac{2}{-4}=-\dfrac12$.

</details>

Avis : 

---

## 24. `cqc-suite-auxiliaire-moyenne-2` (séries BAC:C BAC:D BAC:E PRO:C PRO:D PRO:E)

**Remarque du relecteur :** LIMITE : suite récurrente avec terme en 3^n et suite particulière à identifier, méthode guidée mais exigeante pour la Première.

**Énoncé :**

On considère la suite $(U_n)$ définie par $U_0=2$ et, pour tout entier naturel $n$, $U_{n+1} = 2U_n + 3^n + 5$. On admet qu'il existe deux réels $b$ et $c$ tels que la suite $(a_n)$ définie par $a_n = b\times3^n+c$ vérifie, pour tout entier naturel $n$, la même relation $a_{n+1}=2a_n+3^n+5$. Quelle est l'expression de $U_n$ en fonction de $n$ ?

- a) $U_n=6\times2^n+3^n+5$
- b) $U_n=6\times2^n+3^n-5$
- c) $U_n=2\times2^n+3^n-5$
- d) $U_n=8\times2^n-3^n-5$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On détermine $b$ et $c$ en écrivant que $a_n=b\times3^n+c$ vérifie la même relation que $(U_n)$ et en identifiant les coefficients de $3^n$ et les termes constants. La suite $V_n=U_n-a_n$ vérifie alors une relation sans second membre, donc elle est géométrique.

### Corrigé

$a_{n+1}=3b\times3^n+c$ et $2a_n+3^n+5=(2b+1)\times3^n+2c+5$. Par identification : $3b=2b+1$, soit $b=1$, et $c=2c+5$, soit $c=-5$. Donc $a_n=3^n-5$.

$V_{n+1}=U_{n+1}-a_{n+1}=2(U_n-a_n)=2V_n$ : $(V_n)$ est géométrique de raison $2$, avec $V_0=U_0-a_0=2-(1-5)=6$. Donc $V_n=6\times2^n$ et
$$U_n=V_n+a_n=6\times2^n+3^n-5.$$
Contrôle : $U_1=2\times2+1+5=10$ et $6\times2+3-5=10$.

### Pourquoi les autres réponses sont fausses
- **a)** la constante $c$ a été prise égale à $+5$ au lieu de $-5$ (l'équation $c=2c+5$ donne $c=-5$).
- **c)** on a pris $V_0=U_0=2$ en oubliant de retrancher $a_0=-4$ : on a bien $V_0=2-(-4)=6$.
- **d)** le coefficient $b$ a été pris égal à $-1$ au lieu de $1$ (signe faux dans $3b=2b+1$), ce qui fausse $a_n$ et $V_0$.

</details>

Avis : 

---

## 25. `cqc-suite-geometrique-elevee-0` (séries BAC:C BAC:D BAC:E BAC:TI PRO:C PRO:D PRO:E)

**Remarque du relecteur :** VOCABULAIRE : le modèle donne des nombres d'arbres non entiers dès U_4 = 482,4 ; préciser « modélisé par » ou « valeur approchée ».

**Énoncé :**

Une ONG de reforestation entretient une réserve forestière. Au début du projet (année 0), la réserve compte 700 arbres vivants. Chaque année, 40 % des arbres de la réserve meurent, mais l'ONG plante 180 nouveaux arbres. On modélise par $U_n$ le nombre d'arbres vivants l'année $n$, avec $U_0=700$, et on admet que, pour tout entier naturel $n$, $U_{n+1}=0{,}6\,U_n+180$. Quelle est l'expression de $U_n$ en fonction de $n$ ?

- a) $U_n=450+700\times0{,}6^{\,n}$
- b) $U_n=300+400\times0{,}6^{\,n}$
- c) $U_n=450+250\times0{,}6^{\,n}$
- d) $U_n=450-250\times0{,}6^{\,n}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Une suite $U_{n+1}=aU_n+b$ (avec $a\neq1$) se ramène à une suite géométrique : on cherche la solution $\ell$ de $\ell=a\ell+b$, puis on pose $V_n=U_n-\ell$. La suite $(V_n)$ est géométrique de raison $a$, et $U_n=V_n+\ell$.

### Corrigé

$\ell=0{,}6\,\ell+180 \iff 0{,}4\,\ell=180 \iff \ell=450$.

Avec $V_n=U_n-450$ : $V_{n+1}=0{,}6\,U_n+180-450=0{,}6\,(U_n-450)=0{,}6\,V_n$. La suite $(V_n)$ est géométrique de raison $0{,}6$, de premier terme $V_0=700-450=250$. Donc $V_n=250\times0{,}6^{\,n}$ et
$$U_n=450+250\times0{,}6^{\,n}.$$
Contrôle : $U_1=0{,}6\times700+180=600$ et $450+250\times0{,}6=600$.

### Pourquoi les autres réponses sont fausses
- **a)** on a pris $V_0=U_0=700$ au lieu de $U_0-\ell=250$ : cette expression donne $U_0=1150$.
- **b)** $\ell$ a été calculé par $\dfrac{180}{0{,}6}=300$ en oubliant le terme $0{,}6\,\ell$ de l'autre côté : on a $\ell=\dfrac{180}{1-0{,}6}=450$.
- **d)** signe de $V_0$ faux : $V_0=700-450=+250$. Cette expression donne $U_0=200$.

</details>

Avis : 

---

## 26. `cqc-suite-geometrique-faible-1` (séries BAC:C BAC:D BAC:E BAC:TI PRO:C PRO:D PRO:E)

**Énoncé :**

Juste après une injection intraveineuse, un patient reçoit une dose de 1024 mg d'un principe actif. On considère que, chaque heure, l'organisme élimine un quart de la quantité de principe actif présente dans le sang, si bien que les trois quarts restants demeurent. On note $U_n$ la quantité de principe actif (en mg) présente dans le sang $n$ heures après l'injection, avec $U_0=1024$. Quelle quantité de principe actif reste-t-il dans le sang 5 heures après l'injection ?

- a) $243$ mg
- b) $1$ mg
- c) $324$ mg
- d) $182{,}25$ mg

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'une grandeur perd à intervalles réguliers une proportion $p$ de sa valeur, il en reste une proportion $1-p$ : la suite des valeurs est géométrique de raison $q=1-p$, et $U_n=U_0\times q^{\,n}$.

### Corrigé

Chaque heure, les trois quarts restent : $U_{n+1}=0{,}75\,U_n$. La suite est géométrique de raison $q=0{,}75$ et $U_n=1024\times0{,}75^{\,n}$.

Comme $1024=4^5$ et $0{,}75=\dfrac34$ : $U_5=4^5\times\dfrac{3^5}{4^5}=3^5=243$.

Il reste donc $243$ mg de principe actif dans le sang après 5 heures.

### Pourquoi les autres réponses sont fausses
- **b)** la raison a été prise égale à $\dfrac14$ (la proportion éliminée) au lieu de $\dfrac34$ (la proportion qui reste).
- **c)** c'est $U_4$ : l'exposant est faux (4 au lieu de 5).
- **d)** c'est $U_6$ : l'exposant est faux (6 au lieu de 5).

</details>

Avis : 

---

## 27. `cqc-suite-geometrique-moyenne-0` (séries BAC:C BAC:D BAC:E BAC:TI PRO:C PRO:D PRO:E)

**Remarque du relecteur :** Résolution par essais successifs à la calculatrice (pas de logarithme en Première), ce qui reste au programme.

**Énoncé :**

Une usine rejette accidentellement un polluant dans une rivière. Juste après l'incident, la concentration de polluant est de 800 mg/L. Grâce à la dilution naturelle du courant, et en l'absence de tout nouvel apport, cette concentration diminue de 35 % chaque jour par rapport à la veille. On note $U_n$ la concentration (en mg/L) $n$ jours après l'incident, avec $U_0=800$. Quel est le plus petit entier naturel $n$ tel que $U_n<50$ ?

- a) $n=6$
- b) $n=7$
- c) $n=8$
- d) $n=5$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Une diminution de $p\ \%$ revient à multiplier par $1-\dfrac{p}{100}$ : la suite est géométrique décroissante. Pour trouver le premier rang où elle passe sous un seuil, on calcule les termes successifs et on vérifie que le terme précédent ne convenait pas encore.

### Corrigé

Une baisse de 35 % revient à multiplier par $0{,}65$ : $U_n=800\times0{,}65^{\,n}$.

$U_0=800$ ; $U_1=520$ ; $U_2=338$ ; $U_3=219{,}7$ ; $U_4\approx142{,}81$ ; $U_5\approx92{,}83$ ; $U_6\approx60{,}34$ ; $U_7\approx39{,}22$.

$U_6\approx60{,}34\geq50$ alors que $U_7\approx39{,}22<50$. Le plus petit entier cherché est $n=7$.

### Pourquoi les autres réponses sont fausses
- **a)** $U_6\approx60{,}34$ est encore supérieur à $50$ : le seuil n'est franchi qu'au rang suivant.
- **c)** $U_8\approx25{,}5$ est bien inférieur à $50$, mais ce n'est pas le plus petit rang : $U_7\approx39{,}22<50$ déjà.
- **d)** $U_5\approx92{,}83$ est encore bien supérieur à $50$ : la baisse de $35\ \%$ par jour est plus lente que ce qu'on imagine.

</details>

Avis : 

---

## 28. `cqc-suites-numeriques-moyenne-1` (séries BAC:C PRO:D)

**Remarque du relecteur :** VOCABULAIRE : le modèle donne des nombres de bus non entiers dès U_3 = 248,8 ; préciser « modélisé par ».

**Énoncé :**

Une compagnie de transport interurbain possède 200 bus en circulation au début de l'année 2024. Chaque année, elle retire du parc 20 % des bus en circulation (usure, réforme) puis met en service 60 bus neufs. On modélise par $U_n$ le nombre de bus en circulation l'année $(2024+n)$, avec $U_0=200$. Quelle est l'expression de $U_n$ en fonction de $n$ ?

- a) $U_n=300+100\times0{,}8^{\,n}$
- b) $U_n=75+125\times0{,}2^{\,n}$
- c) $U_n=300-100\times0{,}2^{\,n}$
- d) $U_n=300-100\times0{,}8^{\,n}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Une suite $U_{n+1}=aU_n+b$ (avec $a\neq1$) se ramène à une suite géométrique en posant $V_n=U_n-\ell$, où $\ell$ est la solution de $\ell=a\ell+b$. La suite $(V_n)$ est géométrique de raison $a$.

### Corrigé

Chaque année, $80\ \%$ du parc reste en circulation (facteur $0{,}8$) puis on ajoute $60$ bus : $U_{n+1}=0{,}8\,U_n+60$.

$\ell=0{,}8\,\ell+60 \iff 0{,}2\,\ell=60 \iff \ell=300$. En posant $V_n=U_n-300$ : $V_{n+1}=0{,}8\,U_n-240=0{,}8\,V_n$, donc $(V_n)$ est géométrique de raison $0{,}8$, de premier terme $V_0=200-300=-100$.

Donc $V_n=-100\times0{,}8^{\,n}$ et $U_n=300-100\times0{,}8^{\,n}$.

Contrôle : $U_1=0{,}8\times200+60=220$ et $300-100\times0{,}8=220$. Comme $0<0{,}8<1$, $U_n$ tend vers $300$ : le parc se stabilise autour de $300$ bus.

### Pourquoi les autres réponses sont fausses
- **a)** signe de $V_0$ faux : $V_0=U_0-300=-100$. Cette expression donne $U_0=400$.
- **b)** la raison a été prise égale à $0{,}2$ (la part retirée) au lieu de $0{,}8$ (la part conservée), ce qui change $\ell=\dfrac{60}{0{,}8}=75$ et la suite.
- **c)** la limite $300$ est bonne mais la raison est $0{,}2$ au lieu de $0{,}8$ : $U_1$ vaudrait $280$ alors que $U_1=220$.

</details>

Avis : 

---

## 29. `cqc-symetrie-de-courbe-prob-a-faible-0` (séries BAC:A PRO:A)

**Remarque du relecteur :** LIMITE : éléments de symétrie d'une courbe en série A, à confirmer au programme de Première A.

**Énoncé :**

Soit $f$ une fonction d'ensemble de définition $D_f$. À quelles conditions la courbe de $f$ admet-elle un axe de symétrie vertical d'équation $x=a$, et un centre de symétrie $\Omega(a\,;b)$ ? (Dans les deux cas, on suppose que $2a-x$ appartient à $D_f$ pour tout $x$ de $D_f$.)

- a) Axe : $f(2a-x)=f(x)$ ; centre : $f(2a-x)+f(x)=2b$
- b) Axe : $f(a-x)=f(x)$ ; centre : $f(a-x)+f(x)=2b$
- c) Axe : $f(2a-x)=-f(x)$ ; centre : $f(2a-x)=f(x)$
- d) Axe : $f(2a-x)=f(x)$ ; centre : $f(2a-x)+f(x)=b$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On exprime la symétrie à l'aide de $f(2a-x)$ : le point d'abscisse $2a-x$ est le symétrique de celui d'abscisse $x$ par rapport à la droite $x=a$ (ou au point d'abscisse $a$).

### Corrigé

Axe de symétrie $x=a$ : pour tout $x$ de l'ensemble de définition, $f(2a-x)=f(x)$. Centre de symétrie $\Omega(a\,;b)$ : pour tout $x$ de l'ensemble de définition, $f(2a-x)+f(x)=2b$. Cas particuliers : fonction **paire** ($a=0$, axe des ordonnées) et fonction **impaire** (centre $O$).

### Pourquoi les autres réponses sont fausses
- **b)** le symétrique de $x$ par rapport à $a$ est $2a-x$, et non $a-x$ (cette dernière écriture correspond à une symétrie par rapport à $\dfrac a2$).
- **c)** les deux conditions ont été échangées : l'égalité $f(2a-x)=f(x)$ traduit l'axe, la somme égale à $2b$ traduit le centre.
- **d)** la somme doit valoir $2b$ et non $b$ : le point d'ordonnée $b$ est le milieu des deux ordonnées $f(x)$ et $f(2a-x)$.

</details>

Avis : 

---

## 30. `cqc-symetrie-de-courbe-prob-a-moyenne-4` (séries BAC:A PRO:A)

**Énoncé :**

La courbe de la fonction $f(x)=\dfrac{1}{x-1}+2$ (définie pour $x\neq1$) admet un centre de symétrie. Quelles sont ses coordonnées ?

- a) $\Omega(-1\,;2)$
- b) $\Omega(1\,;-2)$
- c) $\Omega(2\,;1)$
- d) $\Omega(1\,;2)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Un point $\Omega(a\,;b)$ est centre de symétrie si $f(2a-x)+f(x)=2b$ pour tout $x$ de l'ensemble de définition (avec $2a-x$ dans cet ensemble).

### Corrigé

L'ensemble de définition est symétrique par rapport à $1$, donc on essaie $a=1$ : $f(2-x)=\dfrac{1}{(2-x)-1}+2=\dfrac{1}{1-x}+2=-\dfrac{1}{x-1}+2$.

Donc $f(2-x)+f(x)=\left(-\dfrac{1}{x-1}+2\right)+\left(\dfrac{1}{x-1}+2\right)=4=2\times2$ : le centre de symétrie est $\Omega(1\,;2)$.

### Pourquoi les autres réponses sont fausses
- **a)** erreur de signe sur l'abscisse : la valeur interdite est $x=1$ (car $x-1=0$), le centre est donc d'abscisse $1$.
- **b)** erreur de signe sur l'ordonnée : la somme $f(2-x)+f(x)$ vaut $+4$, donc $b=+2$.
- **c)** les coordonnées sont échangées : l'abscisse est la valeur interdite $1$ et l'ordonnée est la constante $2$ ajoutée.

</details>

Avis : 

---

## 31. `cqc-serie-statistique-double-moyenne-0` (séries BAC:A PRO:C PRO:E)

**Remarque du relecteur :** Les classes « Moins de 5000 », « Entre 5000 et 15000 », « Plus de 15000 » laissent les bornes 5000 et 15000 non attribuées ; sans effet sur la réponse.

**Énoncé :**

Une enquête a été menée auprès de 70 clients d'un magasin, croisant leur mode de paiement et le montant de leur achat. Le tableau à double entrée suivant donne, dans chaque case, l'effectif conjoint correspondant :

| Mode de paiement / Montant de l'achat | Moins de 5000 F | Entre 5000 et 15000 F | Plus de 15000 F |
|---|---|---|---|
| Espèces | 14 | 9 | 2 |
| Mobile Money | 6 | 18 | 7 |
| Carte bancaire | 1 | 5 | 8 |

Combien de clients ont fait un achat de montant « Entre 5000 et 15000 F », tous modes de paiement confondus ?

- a) $32$ clients
- b) $31$ clients
- c) $27$ clients
- d) $23$ clients

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

L'effectif marginal d'une modalité est la somme des effectifs conjoints de la colonne (ou de la ligne) associée à cette modalité. La somme de tous les effectifs marginaux d'un même caractère est égale à l'effectif total.

### Corrigé

Effectif marginal de « Entre 5000 et 15000 F » : $9+18+5=32$.

Vérification avec la distribution marginale complète du montant : $21+32+17=70$, égal à l'effectif total de l'enquête.

Il y a donc **32 clients**.

### Pourquoi les autres réponses sont fausses
- **b)** c'est le total de la ligne « Mobile Money » ($6+18+7$) : on a additionné une ligne au lieu d'une colonne.
- **c)** on a oublié la case « Carte bancaire » de la colonne : $9+18=27$.
- **d)** on a oublié la case « Espèces » de la colonne : $18+5=23$.

</details>

Avis : 

---

## 32. `cqc-serie-statistique-double-moyenne-2` (séries BAC:A PRO:C PRO:E)

**Énoncé :**

Une entreprise emploie 60 salariés. On a croisé, pour chacun d'eux, le mode de transport utilisé pour se rendre au travail et le temps de trajet domicile-travail (regroupé en classes, en minutes). Le tableau à double entrée suivant donne, dans chaque case, l'effectif conjoint correspondant :

| Temps de trajet / Mode de transport | Bus | Moto | Voiture |
|---|---|---|---|
| [0 ; 15[ minutes | 3 | 8 | 4 |
| [15 ; 30[ minutes | 5 | 10 | 6 |
| [30 ; 45[ minutes | 2 | 6 | 9 |
| [45 ; 60[ minutes | 1 | 3 | 3 |

Quelle est la moyenne du temps de trajet domicile-travail de l'ensemble des 60 salariés, tous modes de transport confondus ? On prend pour chaque classe la valeur centrale de l'intervalle.

- a) $19$ minutes
- b) $26{,}5$ minutes
- c) $34$ minutes
- d) $30$ minutes

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour calculer la moyenne d'un caractère quantitatif regroupé en classes à partir d'un tableau à double entrée, on établit d'abord sa distribution marginale (somme des effectifs conjoints de chaque ligne), puis on pondère la valeur centrale de chaque classe par son effectif marginal, on additionne et on divise par l'effectif total.

### Corrigé

Distribution marginale du temps de trajet : $[0;15[$ : $3+8+4=15$ ; $[15;30[$ : $5+10+6=21$ ; $[30;45[$ : $2+6+9=17$ ; $[45;60[$ : $1+3+3=7$. Vérification : $15+21+17+7=60$.

Valeurs centrales : $7{,}5$ ; $22{,}5$ ; $37{,}5$ ; $52{,}5$.

$$\bar{x}=\dfrac{15\times7{,}5+21\times22{,}5+17\times37{,}5+7\times52{,}5}{60}=\dfrac{1590}{60}=26{,}5.$$

Le temps de trajet moyen est de **26,5 minutes**.

### Pourquoi les autres réponses sont fausses
- **a)** on a pris la borne inférieure de chaque classe ($0$, $15$, $30$, $45$) au lieu de la valeur centrale.
- **c)** on a pris la borne supérieure de chaque classe ($15$, $30$, $45$, $60$) au lieu de la valeur centrale.
- **d)** on a fait la moyenne simple des quatre valeurs centrales, sans tenir compte des effectifs de chaque classe.

</details>

Avis : 

---

## 33. `cqc-taux-d-accroissement-faible-0` (séries BAC:A BAC:C PRO:C PRO:E)

**Remarque du relecteur :** LIMITE : nombre dérivé comme limite du taux d'accroissement, à vérifier pour la série A (programme allégé) où la dérivation peut ne pas figurer.

**Énoncé :**

On modélise par $T(t) = -t^2+4t+10$ (en °C) la température relevée dans un local d'expérimentation, $t$ heures après le début du relevé, pour $t\in[0;4]$. Que vaut, en °C par heure, $\displaystyle\lim_{t\to1} \dfrac{T(t)-T(1)}{t-1}$ ?

- a) $3$
- b) $2$
- c) $-2$
- d) $13$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Le taux d'accroissement d'une fonction $f$ entre $x_0$ et $x$ est le quotient $\dfrac{f(x)-f(x_0)}{x-x_0}$. Lorsque $f$ est dérivable en $x_0$, ce quotient admet une limite finie quand $x\to x_0$ : cette limite est le nombre dérivé $f'(x_0)$, qui représente la vitesse instantanée de variation de $f$ au point $x_0$.

### Corrigé
$T(1) = -1+4+10=13$. Pour $t\neq1$ :
$$T(t)-T(1) = -t^2+4t-3 = -(t-1)(t-3).$$
Donc :
$$\dfrac{T(t)-T(1)}{t-1} = -(t-3) = 3-t.$$
$$\lim_{t\to1} \dfrac{T(t)-T(1)}{t-1} = \lim_{t\to1}(3-t) = 3-1=2.$$
Une heure après le début du relevé, la température augmente donc à la vitesse de $2$ °C par heure (le signe positif indique une hausse).

### Pourquoi les autres réponses sont fausses

- **a)** on garde $3$ en oubliant le terme $-t$ du taux simplifié $3-t$ (ou on évalue ce taux en $t=0$ au lieu de $t=1$).
- **c)** erreur de signe en simplifiant : on obtient $t-3$ au lieu de $3-t$, d'où $1-3=-2$.
- **d)** $13$ est la valeur $T(1)$ de la fonction, pas la limite du taux d'accroissement.

</details>

Avis : 

---

## 34. `cqc-taux-d-accroissement-faible-1` (séries BAC:A BAC:C PRO:C PRO:E)

**Remarque du relecteur :** LIMITE : limite d'un taux d'accroissement (coût marginal) en série A, à confirmer au programme de Première A.

**Énoncé :**

Une coopérative agricole estime le coût total de production $C(x)$ (en milliers de francs CFA) de $x$ sacs de maïs par $C(x) = 2x^2+x$, $x\geqslant0$. Que vaut, en milliers de francs CFA par sac, $\displaystyle\lim_{x\to3} \dfrac{C(x)-C(3)}{x-3}$ ?

- a) $12$
- b) $21$
- c) $13$
- d) $7$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Le taux d'accroissement $\dfrac{f(x)-f(x_0)}{x-x_0}$ mesure une variation moyenne entre $x_0$ et $x$. Quand $f$ est dérivable en $x_0$, la limite de ce taux quand $x\to x_0$ donne le nombre dérivé $f'(x_0)$ : en économie, c'est le coût marginal instantané, c'est-à-dire le coût supplémentaire d'une unité de production de plus, évalué au niveau $x_0$.

### Corrigé
$C(3)=2\times9+3=21$. Pour $x\neq3$ :
$$C(x)-C(3) = 2x^2+x-21 = (x-3)(2x+7)$$
(on vérifie : $(x-3)(2x+7)=2x^2+7x-6x-21=2x^2+x-21$). Donc :
$$\dfrac{C(x)-C(3)}{x-3} = 2x+7 \quad\text{et}\quad \lim_{x\to3}(2x+7) = 2\times3+7=13.$$
Autour de $3$ sacs, produire un sac de plus coûte environ $13$ milliers de francs CFA.

### Pourquoi les autres réponses sont fausses

- **a)** on ne tient pas compte du terme $x$ de $C(x)$ : on obtient $4\times3=12$.
- **b)** $21$ est la valeur $C(3)$ du coût, pas la limite du taux d'accroissement.
- **d)** on oublie le facteur $2$ en passant de $2x^2$ à $2x$ : on obtient $2x+1=7$ en $x=3$.

</details>

Avis : 

---

## 35. `cqc-variance-prob-c-faible-0` (séries BAC:A PRO:A PRO:C PRO:D PRO:E)

**Énoncé :**

Quelle est la variance de la série $1\,;3\,;5$ ?

- a) $4$
- b) $8$
- c) $\dfrac83$
- d) $\dfrac43$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

$V=\dfrac1N\sum(x_i-\bar x)^2$ : on calcule la moyenne, puis la moyenne des carrés des écarts à la moyenne.

### Corrigé

$\bar x=\dfrac{1+3+5}3=3$. Écarts : $-2\,;0\,;2$ ; carrés : $4\,;0\,;4$.
$$V=\dfrac{4+0+4}3=\dfrac83.$$

### Pourquoi les autres réponses sont fausses

- **a)** on divise par $N-1=2$ au lieu de $N=3$.
- **b)** on s'arrête à la somme des carrés des écarts, sans diviser par $N$.
- **d)** $\frac43$ est la moyenne des valeurs absolues des écarts : on a oublié de les élever au carré.

</details>

Avis : 

---

## 36. `cqc-equation-de-droite-prob-a-moyenne-2` (séries BAC:A PRO:A)

**Énoncé :**

Quelle est l'équation réduite de la droite $(AB)$ avec $A(1\,;2)$ et $B(3\,;8)$ ?

- a) $y=3x+1$
- b) $y=6x-4$
- c) $y=\dfrac13x+\dfrac53$
- d) $y=3x-1$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule $m$ puis on détermine $p$ avec un des points.

### Corrigé

$m=\dfrac{8-2}{3-1}=3$ ; $2=3\times1+p\Rightarrow p=-1$. Équation : $y=3x-1$. Vérification avec $B$ : $3\times3-1=8$.

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe sur l'ordonnée à l'origine : $2=3+p$ donne $p=-1$ et non $1$.
- **b)** on prend pour coefficient directeur la différence des ordonnées $8-2=6$ sans diviser par $3-1$.
- **c)** on inverse le quotient : $m=\dfrac{3-1}{8-2}=\dfrac13$.

</details>

Avis : 

---

## 37. `cqc-equation-de-droite-prob-a-moyenne-5` (séries BAC:A PRO:A)

**Remarque du relecteur :** VOCABULAIRE : « Lequel de ces points » suppose un seul point alors que les choix proposent « les deux » ou « aucun » ; écrire « Quel(s) point(s) ».

**Énoncé :**

On considère la droite d'équation $y=2x+1$ et les points $C(4\,;9)$ et $D(3\,;8)$. Parmi ces points, lesquels appartiennent à la droite ?

- a) $D$ seulement
- b) les deux points $C$ et $D$
- c) $C$ seulement
- d) aucun des deux points

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On remplace les coordonnées dans l'équation.

### Corrigé

$C$ : $2\times4+1=9$ : $C$ appartient à la droite. $D$ : $2\times3+1=7\ne8$ : $D$ n'appartient pas à la droite.

### Pourquoi les autres réponses sont fausses

- **a)** on se trompe de point : $2\times3+1=7$, qui n'est pas l'ordonnée $8$ de $D$.
- **b)** on ne vérifie pas $D$ : $2\times3+1=7\neq8$.
- **d)** on se trompe sur $C$ : $2\times4+1=9$, qui est bien son ordonnée.

</details>

Avis : 

---

