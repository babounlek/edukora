# Campagne B1 maths : relectures en attente de l'enseignant

Date : 2026-11-01. Cinq lots dont l'avis de l'enseignant n'a pas encore été reçu : Probatoire vague 5b, BEPC vague 4, BEPC vague 5, BAC vague 4, BAC vague 5. Pour chaque question : OK, à corriger (dire quoi), à retirer, ou retirer la série X.


---

# Lot : b1-probatoire-vague-5b

## Vague 5b Maths Probatoire et BAC (questions communes aux deux examens) : 37 QCM à faire relire par l'enseignant (campagne B1)

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


---

# Lot : b1-bepc-vague-4

## Vague 4 Maths BEPC : 55 QCM à faire relire par l'enseignant (campagne B1)

Date : 2026-11-01. Sur 197 QCM convertis (235 questions BEPC sans figure étudiées, 38 écartées), **55** vous sont soumis : ceux que le relecteur aveugle a assortis d'une remarque et un tirage de 15 autres. Le lot est prêt mais n'est pas en ligne tant que vous n'avez pas répondu. Les 197 résolutions à l'aveugle ont donné la clé, après correction d'une ambiguïté (encadrement) et de 14 formulations. Beaucoup de questions à plusieurs sous-questions ont été réduites à une seule.

## Points à trancher

1. **Vecteur directeur** (`vecteur-directeur-faible-0`, `vecteur-directeur-moyenne-1`) et **norme d'un vecteur** : ces termes sont-ils au programme de la 3e ?
2. **Droites écrites sous la forme ax + by + c = 0** (`equation-reduite`) : à ramener à y = ax + b ; à garder ?
3. **Rapport d'une réduction au cube** (volumes, racine cubique de 27/64), **homothétie de rapport négatif**, **diagonale du cube** et **apothème** (Pythagore deux fois) : limites hautes de la 3e ?
4. **Développement d'un produit de trois facteurs** (`double-distributivite-elevee-0`), **valeur absolue d'une expression avec radical**.
5. **Incohérence d'origine** (`aire-d-un-rectangle-elevee-1`) : 4,5 m / 0,4 m = 11,25 carreaux, ils ne tombent pas pile ; la clé 180 vient du calcul par les aires. On garde ?
6. **Questions simples** à retirer éventuellement : divisions de fractions et droites horizontales faciles.

Pour chaque question : **OK**, **à corriger** (dire quoi) ou **à retirer**.

## 1. `cqc-tangente-moyenne-1` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : « le pied d'une caméra ... est situé à 15 m » est confus, écrire « le pied du poteau est situé à 15 m du point R ». Avec 0,70 on tombe pile sur 10,5 : un élève peut hésiter entre 10 et 11 ; mieux vaut donner tan 35° ≈ 0,7002 ou demander l'arrondi au dixième.

**Énoncé :**

Une caméra de surveillance est fixée au sommet d'un poteau. Le pied du poteau est situé à $15$ m d'un point de référence $R$ du sol. L'angle d'élévation entre ce point $R$ et le sommet du poteau, où est fixée la caméra, mesure $35°$. Sachant que $\tan(35°) \approx 0{,}70$, quelle est la hauteur du poteau, arrondie au mètre le plus proche ?

- a) $21$ m
- b) $10$ m
- c) $11$ m
- d) $14$ m

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand on connaît un angle et le côté adjacent dans un triangle rectangle, on retrouve le côté opposé avec $\tan(\alpha) = \dfrac{\text{opposé}}{\text{adjacent}}$, d'où $\text{opposé} = \text{adjacent} \times \tan(\alpha)$.

### Corrigé

Notons $h$ la hauteur du poteau (côté opposé à l'angle de $35°$) ; la distance au sol, $15$ m, est le côté adjacent :

$$\tan(35°) = \frac{h}{15} \quad \text{donc} \quad h = 15 \times \tan(35°) \approx 15 \times 0{,}70 = 10{,}5 \text{ m}$$

Arrondi au mètre le plus proche : $h \approx 11$ m.

**Vérification.** $\tan 35° < 1$, donc la hauteur doit être inférieure à la distance horizontale : $11 < 15$.

### Pourquoi les autres réponses sont fausses
- **a)** a divisé par $\tan(35°)$ au lieu de multiplier : $15 \div 0{,}70 \approx 21{,}4$.
- **b)** a tronqué $10{,}5$ au lieu de l'arrondir au plus proche.
- **d)** a soustrait $0{,}70$ à $15$ au lieu de multiplier par $\tan(35°)$.

</details>

Avis : 

---

## 2. `cqc-tangente-moyenne-2` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : préciser que le fil est tendu (rectiligne) et tenu au niveau du sol, sinon la hauteur de la main fausse le modèle.

**Énoncé :**

Un enfant fait voler un cerf-volant. Le fil du cerf-volant, tendu et tenu par l'enfant au niveau du sol, fait un angle de $40°$ avec le sol, et le cerf-volant se trouve à une hauteur de $18$ m au-dessus du sol, à la verticale d'un point $P$. Sachant que $\tan(40°) \approx 0{,}84$, quelle est la distance horizontale entre l'enfant et le point $P$, arrondie au mètre le plus proche ?

- a) $15$ m
- b) $21$ m
- c) $22$ m
- d) $17$ m

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand on connaît un angle et le côté opposé, on retrouve le côté adjacent avec $\tan(\alpha) = \dfrac{\text{opposé}}{\text{adjacent}}$, d'où $\text{adjacent} = \dfrac{\text{opposé}}{\tan(\alpha)}$.

### Corrigé

Notons $d$ la distance horizontale (côté adjacent à l'angle de $40°$) ; la hauteur $18$ m est le côté opposé. Le triangle formé par l'enfant, le point $P$ et le cerf-volant est rectangle en $P$ :

$$\tan(40°) = \frac{18}{d} \quad \text{donc} \quad d = \frac{18}{\tan(40°)} \approx \frac{18}{0{,}84} \approx 21{,}4 \text{ m}$$

Arrondi au mètre le plus proche : $d \approx 21$ m.

**Vérification.** $\tan 40° < 1$, donc le côté adjacent doit être plus grand que le côté opposé : $21 > 18$.

### Pourquoi les autres réponses sont fausses
- **a)** a multiplié $18$ par $\tan(40°)$ au lieu de diviser : $18 \times 0{,}84 \approx 15$.
- **c)** a arrondi $21{,}4$ par excès au lieu de l'arrondir au plus proche.
- **d)** a soustrait $0{,}84$ à $18$ au lieu de diviser par $\tan(40°)$.

</details>

Avis : 

---

## 3. `cqc-aire-d-un-rectangle-elevee-1` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : 4,5/0,4 = 11,25 n'est pas entier, des carreaux doivent être découpés ; « aucune perte » est peu réaliste, préférer une largeur de 4,4 m ou 4,8 m.

**Énoncé :**

Un carreleur doit carreler une pièce rectangulaire de $6{,}4$ m de longueur sur $4{,}5$ m de largeur, à l'aide de carreaux carrés de $40$ cm de côté. On suppose qu'il n'y a aucune perte de matériau. Combien de carreaux sont nécessaires ?

- a) $72$
- b) $18$
- c) $720$
- d) $180$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour déterminer combien de petites surfaces identiques recouvrent une grande surface, on calcule l'aire de chacune dans la même unité, puis on divise l'aire totale par l'aire d'une seule pièce.

### Corrigé

Aire de la pièce : $6{,}4 \times 4{,}5 = 28{,}8 \text{ m}^{2}$.

Côté d'un carreau en mètres : $40 \text{ cm} = 0{,}4 \text{ m}$, donc aire d'un carreau : $0{,}4 \times 0{,}4 = 0{,}16 \text{ m}^{2}$.

$$n = \frac{28{,}8}{0{,}16} = 180$$

Le carreleur a besoin de **180 carreaux**.

**Vérification.** $180 \times 0{,}16 = 28{,}8$ m² : on retrouve l'aire de la pièce.

### Pourquoi les autres réponses sont fausses
- **a)** a divisé l'aire de la pièce par le côté d'un carreau ($0{,}4$ m) au lieu de son aire.
- **b)** a calculé l'aire d'un carreau égale à $1{,}6$ m² au lieu de $0{,}16$ m² (erreur de virgule).
- **c)** a calculé l'aire d'un carreau égale à $0{,}04$ m² au lieu de $0{,}16$ m² (erreur de virgule).

</details>

Avis : 

---

## 4. `cqc-aire-d-un-rectangle-moyenne-2` (séries BEPC)

**Énoncé :**

Un mur rectangulaire de $5$ m de longueur et $2{,}5$ m de hauteur doit être peint. Il comporte une fenêtre rectangulaire de $1{,}2$ m de longueur sur $1$ m de hauteur qu'on ne peint pas. Quelle est l'aire de mur réellement à peindre ?

- a) $13{,}7 \text{ m}^{2}$
- b) $11{,}3 \text{ m}^{2}$
- c) $10{,}3 \text{ m}^{2}$
- d) $11{,}5 \text{ m}^{2}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour calculer l'aire d'une surface avec une partie non concernée, on calcule l'aire totale du rectangle, l'aire de la partie à exclure, puis on soustrait la seconde de la première.

### Corrigé

Aire totale du mur : $5 \times 2{,}5 = 12{,}5 \text{ m}^{2}$.

Aire de la fenêtre : $1{,}2 \times 1 = 1{,}2 \text{ m}^{2}$.

Aire à peindre : $12{,}5 - 1{,}2 = 11{,}3 \text{ m}^{2}$.

### Pourquoi les autres réponses sont fausses
- **a)** a additionné l'aire de la fenêtre à celle du mur au lieu de la soustraire.
- **c)** a soustrait $2{,}2$, c'est-à-dire la somme des dimensions de la fenêtre, au lieu de son aire.
- **d)** n'a retiré que $1$ (la hauteur de la fenêtre) au lieu de son aire $1{,}2$.

</details>

Avis : 

---

## 5. `cqc-angle-au-centre-elevee-5` (séries BEPC)

**Remarque du relecteur :** Énoncé indirect : il faut voir que W est le milieu de [YZ] et que le triangle XWY est isocèle ; la valeur 53,13° sert de leurre partiel (choix b).

**Énoncé :**

Le triangle $XYZ$ est rectangle en $X$. On donne $\sin(\widehat{XZY}) = 0{,}8$ ; une table trigonométrique associe à cette valeur l'angle $53{,}13°$. Le cercle circonscrit au triangle $XYZ$ a pour centre $W$. Quelle est la mesure de l'angle $\widehat{WXY}$ du triangle $XWY$ ?

- a) $73{,}74°$
- b) $53{,}13°$
- c) $36{,}87°$
- d) $26{,}565°$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
On retrouve un angle à partir de son sinus en lisant la table dans le sens inverse. L'angle au centre qui intercepte un arc mesure le double de l'angle inscrit interceptant ce même arc ; dans un triangle formé par deux rayons, les angles à la base sont égaux, et la somme des angles d'un triangle vaut $180°$.

### Corrigé

D'après la table, $\widehat{XZY} = 53{,}13°$.

L'angle inscrit $\widehat{XZY}$ et l'angle au centre $\widehat{XWY}$ interceptent le même arc $XY$ :

$$\widehat{XWY} = 2 \times 53{,}13° = 106{,}26°$$

Les segments $[WX]$ et $[WY]$ sont deux rayons du cercle circonscrit : le triangle $XWY$ est isocèle en $W$, donc $\widehat{WXY} = \widehat{WYX}$. La somme des angles du triangle vaut $180°$ :

$$\widehat{WXY} = \frac{180° - 106{,}26°}{2} = \frac{73{,}74°}{2} = 36{,}87°$$

### Pourquoi les autres réponses sont fausses
- **a)** a donné la somme des deux angles à la base sans la partager en deux.
- **b)** a repris la mesure de l'angle inscrit $\widehat{XZY}$ au lieu de calculer un angle à la base de $XWY$.
- **d)** a pris la moitié de l'angle inscrit au lieu de la moitié de $180° - 106{,}26°$.

</details>

Avis : 

---

## 6. `cqc-angle-au-centre-moyenne-4` (séries BEPC)

**Remarque du relecteur :** Le point D et l'angle ADB ne servent à rien ; donnée inutile mais pas trompeuse.

**Énoncé :**

Un cercle de centre $O$ passe par quatre points $A$, $B$, $C$ et $D$. Les angles inscrits $\widehat{ACB}$ et $\widehat{ADB}$ interceptent tous deux l'arc $AB$ ne contenant ni $C$ ni $D$. Sachant que $\widehat{ACB} = 27°$, quelle est la mesure de l'angle au centre $\widehat{AOB}$ qui intercepte ce même arc ?

- a) $27°$
- b) $13{,}5°$
- c) $54°$
- d) $126°$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Deux angles inscrits qui interceptent le même arc ont la même mesure. L'angle au centre qui intercepte ce même arc mesure le double de chacun d'eux.

### Corrigé

$\widehat{ACB}$ et $\widehat{ADB}$ interceptent le même arc $AB$, donc $\widehat{ADB} = \widehat{ACB} = 27°$.

L'angle au centre correspondant mesure

$$\widehat{AOB} = 2 \times \widehat{ACB} = 2 \times 27° = 54°$$

### Pourquoi les autres réponses sont fausses
- **a)** a pensé que l'angle au centre a la même mesure que l'angle inscrit.
- **b)** a pris la moitié de l'angle inscrit au lieu du double.
- **d)** a calculé $180° - 54°$ au lieu de s'arrêter au double de l'angle inscrit.

</details>

Avis : 

---

## 7. `cqc-apotheme-moyenne-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : calcul de l'apothème par Pythagore dans l'espace, à la limite haute de la 3e.

**Énoncé :**

Une pyramide régulière a une base carrée de côté $10$ cm et une hauteur de $12$ cm. Quelle est l'aire latérale totale de la pyramide (ses quatre faces) ?

- a) $260 \text{ cm}^{2}$
- b) $65 \text{ cm}^{2}$
- c) $520 \text{ cm}^{2}$
- d) $240 \text{ cm}^{2}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule d'abord l'apothème, hypoténuse du triangle rectangle formé par la hauteur de la pyramide et le demi-côté de la base : $a^{2} = h^{2} + \left(\dfrac{c}{2}\right)^{2}$. Cet apothème sert ensuite de hauteur pour l'aire de chaque face latérale, un triangle isocèle de base $c$.

### Corrigé

Le demi-côté vaut $5$ cm : $a^{2} = 12^{2} + 5^{2} = 144 + 25 = 169$, donc $a = 13$ cm.

Aire d'une face : $\dfrac{10 \times 13}{2} = 65 \ \text{cm}^{2}$.

Aire latérale totale : $4 \times 65 = 260 \ \text{cm}^{2}$.

### Pourquoi les autres réponses sont fausses
- **b)** a calculé l'aire d'une seule face latérale au lieu des quatre.
- **c)** a oublié de diviser par $2$ dans l'aire du triangle : $4 \times 10 \times 13$.
- **d)** a pris la hauteur de la pyramide ($12$ cm) à la place de l'apothème ($13$ cm) pour les faces.

</details>

Avis : 

---

## 8. `cqc-apotheme-moyenne-1` (séries BEPC)

**Remarque du relecteur :** LIMITE : deux étapes (apothème depuis l'aire latérale puis Pythagore dans le triangle apothème/demi-côté/hauteur).

**Énoncé :**

Une pyramide régulière à base carrée de côté $16$ cm a une aire latérale totale de $544$ cm². Quelle est la hauteur de cette pyramide ?

- a) $17$ cm
- b) $9$ cm
- c) $15$ cm
- d) $\sqrt{353}$ cm

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

L'aire latérale totale, divisée par le nombre de faces, donne l'aire d'une face. Chaque face est un triangle isocèle de base $c$ et de hauteur $a$ (l'apothème), d'où $a = \dfrac{2\mathcal{A}_{1}}{c}$. La hauteur de la pyramide s'obtient ensuite par le théorème de Pythagore : $h^{2} = a^{2} - \left(\dfrac{c}{2}\right)^{2}$.

### Corrigé

*Apothème.* Aire d'une face : $\mathcal{A}_{1} = \dfrac{544}{4} = 136 \ \text{cm}^{2}$, puis $a = \dfrac{2 \times 136}{16} = 17$ cm.

*Hauteur.* Le demi-côté vaut $8$ cm et l'apothème est l'hypoténuse : $h^{2} = 17^{2} - 8^{2} = 289 - 64 = 225$, donc $h = 15$ cm.

**Vérification.** $15^{2} + 8^{2} = 225 + 64 = 289 = 17^{2}$.

### Pourquoi les autres réponses sont fausses
- **a)** a donné l'apothème au lieu de la hauteur de la pyramide.
- **b)** a soustrait les longueurs ($17 - 8$) au lieu d'utiliser le théorème de Pythagore.
- **d)** a additionné les carrés ($17^{2} + 8^{2}$) alors que l'apothème est l'hypoténuse.

</details>

Avis : 

---

## 9. `cqc-application-numerique-faible-1` (séries BEPC)

**Énoncé :**

Un cylindre de révolution a pour rayon de base $r = 3$ cm et pour hauteur $h = 10$ cm. Quel est son volume $V$, sachant que $V = \pi r^{2} h$ (on prendra $\pi = 3{,}14$) ?

- a) $94{,}2 \text{ cm}^{3}$
- b) $282{,}6 \text{ cm}^{3}$
- c) $188{,}4 \text{ cm}^{3}$
- d) $1\,130{,}4 \text{ cm}^{3}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

L'application numérique consiste à remplacer chaque lettre par la valeur donnée, puis à effectuer les calculs dans l'ordre des priorités : la puissance d'abord, ensuite les produits.

### Corrigé

$$V = \pi r^{2} h = 3{,}14 \times 3^{2} \times 10 = 3{,}14 \times 9 \times 10 = 28{,}26 \times 10 = 282{,}6 \ \text{cm}^{3}$$

### Pourquoi les autres réponses sont fausses
- **a)** a oublié d'élever le rayon au carré : $3{,}14 \times 3 \times 10$.
- **c)** a calculé $3^{2}$ comme $3 \times 2 = 6$ : $3{,}14 \times 6 \times 10$.
- **d)** a doublé le rayon avant de l'élever au carré : $3{,}14 \times 6^{2} \times 10$.

</details>

Avis : 

---

## 10. `cqc-calcul-de-longueur-moyenne-2` (séries BEPC)

**Remarque du relecteur :** LIMITE : on doit mettre la proportion en équation avec AE = AC - 15, un cran au-dessus du Thalès direct.

**Énoncé :**

Dans le triangle $ABC$, le point $D$ appartient au segment $[AB]$ et le point $E$ appartient au segment $[AC]$, avec $(DE)$ parallèle à $(BC)$. On donne $AB = 16$ cm, $AD = 6$ cm et $EC = 15$ cm.

Calculer la longueur $AC$.

- a) $40$ cm
- b) $31$ cm
- c) $9$ cm
- d) $24$ cm

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand l'énoncé donne le segment $EC$ (et non $AE$ ou $AC$ directement), on exprime d'abord le rapport $\dfrac{EC}{AC}$ en fonction du rapport de Thalès connu $\dfrac{AD}{AB}$, puisque $EC = AC - AE$.

### Corrigé

$(DE) \parallel (BC)$, donc, d'après le théorème de Thalès appliqué au sommet $A$ :
$$\frac{AE}{AC} = \frac{AD}{AB} = \frac{6}{16} = \frac{3}{8}$$

*Rapport de $EC$.* Comme $EC = AC - AE$ :
$$\frac{EC}{AC} = 1 - \frac{AE}{AC} = 1 - \frac{3}{8} = \frac{5}{8}$$

*Calcul de $AC$.*
$$\frac{5}{8} = \frac{15}{AC} \quad \Longrightarrow \quad 5 \times AC = 8 \times 15 = 120 \quad \Longrightarrow \quad AC = \frac{120}{5} = 24 \text{ cm}$$

*Calcul de $AE$.*
$$AE = AC - EC = 24 - 15 = 9 \text{ cm}$$

*Contrôle.* $\dfrac{AE}{AC} = \dfrac{9}{24} = \dfrac{3}{8}$, ce qui correspond bien au rapport de départ.

### Pourquoi les autres réponses sont fausses

- **a)** on a écrit $\dfrac{EC}{AC} = \dfrac{AD}{AB}$, alors que ce rapport vaut $\dfrac{AE}{AC}$ ; $EC$ n'est pas dans la même proportion que $AD$.
- **b)** on a additionné $EC + AB$, sans utiliser le théorème de Thalès.
- **c)** c'est la longueur $AE$, et non $AC$.

</details>

Avis : 

---

## 11. `cqc-centre-de-classe-elevee-0` (séries BEPC)

**Remarque du relecteur :** Préciser que la moyenne se calcule avec les centres des classes.

**Énoncé :**

Un club cycliste a mesuré les distances (en km) parcourues par 40 membres lors d'une sortie, regroupées dans le tableau suivant, où $a$ et $b$ sont des effectifs inconnus.

| Classe | $[0\,;\,10[$ | $[10\,;\,20[$ | $[20\,;\,30[$ | $[30\,;\,40[$ |
|---|---|---|---|---|
| Effectif | 6 | $a$ | $b$ | 4 |

Quelle expression donne la moyenne $M$ des distances parcourues, en fonction de $a$ et de $b$ (en utilisant les centres des classes) ?

- a) $M = \dfrac{120 + 10a + 20b}{40}$
- b) $M = \dfrac{170 + 15a + 25b}{4}$
- c) $M = \dfrac{40 + 15a + 25b}{40}$
- d) $M = \dfrac{170 + 15a + 25b}{40}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On remplace chaque classe par son centre, puis on écrit la moyenne pondérée $\bar{x} = \dfrac{\sum n_i c_i}{N}$, en gardant les effectifs inconnus sous forme littérale.

### Corrigé

*Centres des classes.*

| Classe | $[0;10[$ | $[10;20[$ | $[20;30[$ | $[30;40[$ |
|---|---|---|---|---|
| Centre | 5 | 15 | 25 | 35 |
| Effectif | 6 | $a$ | $b$ | 4 |

*Somme des produits centre × effectif.*

$$6 \times 5 + 15a + 25b + 4 \times 35 = 30 + 15a + 25b + 140 = 170 + 15a + 25b$$

*Moyenne.*

$$M = \frac{170 + 15a + 25b}{40}$$

### Pourquoi les autres réponses sont fausses

- **a)** on a utilisé les bornes inférieures des classes au lieu de leurs centres.
- **b)** on a divisé par $4$ (le nombre de classes) au lieu de diviser par l'effectif total $40$.
- **c)** on a oublié de multiplier les centres $5$ et $35$ par les effectifs $6$ et $4$ : seuls $a$ et $b$ ont été pondérés.

</details>

Avis : 

---

## 12. `cqc-centre-de-classe-faible-1` (séries BEPC)

**Remarque du relecteur :** Les quatre choix donnent la même classe : la première question de l'énoncé n'est pas évaluée.

**Énoncé :**

Le tableau ci-dessous regroupe les masses (en kg) de 20 sacs de café stockés dans un entrepôt.

| Classe | $[40\,;\,50[$ | $[50\,;\,60[$ | $[60\,;\,70[$ |
|---|---|---|---|
| Effectif | 5 | 9 | 6 |

Quel est le centre de la classe la plus représentée (celle qui a le plus grand effectif) ?

- a) $50$ kg
- b) $55$ kg
- c) $110$ kg
- d) $10$ kg

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La classe la plus représentée est celle dont l'effectif est le plus grand. Le centre d'une classe est la demi-somme de ses deux bornes.

### Corrigé

Les effectifs sont $5$, $9$ et $6$ : le plus grand est $9$, pour la classe $[50\,;\,60[$.

Centre de cette classe :

$$c = \frac{50 + 60}{2} = \frac{110}{2} = 55$$

La classe la plus représentée est $[50\,;\,60[$, de centre $55$ kg.

### Pourquoi les autres réponses sont fausses

- **a)** la bonne classe, mais $50$ est sa borne inférieure et non son centre.
- **c)** la bonne classe, mais on a additionné les bornes sans diviser par $2$.
- **d)** la bonne classe, mais $10$ est son amplitude et non son centre.

</details>

Avis : 

---

## 13. `cqc-centre-de-classe-moyenne-0` (séries BEPC)

**Remarque du relecteur :** Avec des classes, la moyenne obtenue par les centres est une valeur approchée ; on pourrait le préciser dans l'énoncé.

**Énoncé :**

Le tableau suivant donne les tailles (en cm) de 50 élèves d'un collège, regroupées en classes.

| Classe | $[140\,;\,150[$ | $[150\,;\,160[$ | $[160\,;\,170[$ | $[170\,;\,180[$ |
|---|---|---|---|---|
| Effectif | 8 | 14 | 20 | 8 |

Calcule la taille moyenne de ces élèves, en utilisant les centres des classes.

- a) $160$ cm
- b) $155{,}6$ cm
- c) $160{,}6$ cm
- d) $165{,}6$ cm

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une série groupée en classes, on remplace chaque classe par son centre (demi-somme des bornes), puis on applique la moyenne pondérée $\bar{x} = \dfrac{\sum n_i c_i}{N}$.

### Corrigé

*Centres des classes.*

| Classe | $[140;150[$ | $[150;160[$ | $[160;170[$ | $[170;180[$ |
|---|---|---|---|---|
| Centre | 145 | 155 | 165 | 175 |
| Effectif | 8 | 14 | 20 | 8 |

*Somme des produits centre × effectif.*

$$8 \times 145 = 1160 \quad ; \quad 14 \times 155 = 2170 \quad ; \quad 20 \times 165 = 3300 \quad ; \quad 8 \times 175 = 1400$$

$$\sum n_i c_i = 1160 + 2170 + 3300 + 1400 = 8030$$

*Moyenne.*

$$\bar{x} = \frac{8030}{50} = 160{,}6$$

La taille moyenne de ces élèves est de $160{,}6$ cm.

### Pourquoi les autres réponses sont fausses

- **a)** on a fait la moyenne simple des quatre centres, sans tenir compte des effectifs.
- **b)** on a pondéré les bornes inférieures des classes au lieu de leurs centres.
- **d)** on a pondéré les bornes supérieures des classes au lieu de leurs centres.

</details>

Avis : 

---

## 14. `cqc-centre-de-classe-moyenne-1` (séries BEPC)

**Remarque du relecteur :** Préciser qu'on calcule la moyenne à l'aide des centres des classes.

**Énoncé :**

Un standard téléphonique a enregistré les durées (en minutes) de 50 appels, regroupées dans le tableau suivant.

| Classe | $[0\,;\,5[$ | $[5\,;\,10[$ | $[10\,;\,15[$ | $[15\,;\,20[$ |
|---|---|---|---|---|
| Effectif | 12 | 18 | 15 | 5 |

Calcule la durée moyenne d'un appel, en utilisant les centres des classes.

- a) $8{,}8$ minutes
- b) $10$ minutes
- c) $6{,}3$ minutes
- d) $11{,}3$ minutes

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule le centre de chaque classe (demi-somme des bornes), puis la moyenne pondérée $\bar{x} = \dfrac{\sum n_i c_i}{N}$.

### Corrigé

*Centres des classes.*

| Classe | $[0;5[$ | $[5;10[$ | $[10;15[$ | $[15;20[$ |
|---|---|---|---|---|
| Centre | 2,5 | 7,5 | 12,5 | 17,5 |
| Effectif | 12 | 18 | 15 | 5 |

*Somme des produits centre × effectif.*

$$12 \times 2{,}5 = 30 \quad ; \quad 18 \times 7{,}5 = 135 \quad ; \quad 15 \times 12{,}5 = 187{,}5 \quad ; \quad 5 \times 17{,}5 = 87{,}5$$

$$\sum n_i c_i = 30 + 135 + 187{,}5 + 87{,}5 = 440$$

*Moyenne.*

$$\bar{x} = \frac{440}{50} = 8{,}8$$

La durée moyenne d'un appel est de $8{,}8$ minutes.

### Pourquoi les autres réponses sont fausses

- **b)** on a fait la moyenne simple des quatre centres, sans tenir compte des effectifs.
- **c)** on a pondéré les bornes inférieures des classes au lieu de leurs centres.
- **d)** on a pondéré les bornes supérieures des classes au lieu de leurs centres.

</details>

Avis : 

---

## 15. `cqc-cercle-circonscrit-faible-0` (séries BEPC)

**Énoncé :**

$ABC$ est un triangle rectangle en $A$ tel que $AB = 9$ cm et $AC = 12$ cm.

Calculer le rayon du cercle circonscrit au triangle $ABC$.

- a) $15$ cm
- b) $7{,}5$ cm
- c) $6$ cm
- d) $10{,}5$ cm

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un triangle rectangle, le cercle circonscrit a pour diamètre l'hypoténuse : son centre est le milieu de l'hypoténuse, et son rayon en vaut la moitié.

### Corrigé

*Calcul de l'hypoténuse $BC$ par Pythagore.*

$$BC^{2} = AB^{2} + AC^{2} = 9^{2} + 12^{2} = 81 + 144 = 225$$

$$BC = \sqrt{225} = 15 \ \text{cm}$$

*Rayon du cercle circonscrit.*

$$R = \frac{BC}{2} = \frac{15}{2} = 7{,}5$$

$$R = 7{,}5 \ \text{cm}$$

Le rayon du cercle circonscrit au triangle $ABC$ est de **7,5 cm**.

### Pourquoi les autres réponses sont fausses

- **a)** c'est le diamètre $BC$ du cercle, et non son rayon.
- **c)** c'est la moitié de $AC$ ; le rayon est la moitié de l'hypoténuse.
- **d)** on a pris la moitié de la somme des deux côtés de l'angle droit.

</details>

Avis : 

---

## 16. `cqc-configuration-en-papillon-faible-0` (séries BEPC)

**Énoncé :**

On considère un point $I$ et deux droites sécantes en $I$. Sur la première droite, les points $G$, $I$, $J$ sont alignés dans cet ordre (donc $I$ est entre $G$ et $J$). Sur la seconde droite, les points $H$, $I$, $K$ sont alignés dans cet ordre (donc $I$ est entre $H$ et $K$). Les droites $(GH)$ et $(JK)$ sont parallèles. On donne : $IG = 4$ cm, $IJ = 10$ cm et $IH = 6$ cm.

Calculer la longueur $IK$.

- a) $2{,}4$ cm
- b) $12$ cm
- c) $\dfrac{20}{3}$ cm
- d) $15$ cm

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsque deux droites sécantes en un point $I$ portent chacune deux points situés de part et d'autre de $I$ (configuration dite « en papillon »), et que les segments reliant les points les plus proches d'une part, et les points les plus éloignés d'autre part, sont parallèles, le théorème de Thalès s'applique exactement comme pour un triangle : les longueurs mesurées depuis $I$ restent proportionnelles.

### Corrigé

Les droites $(GJ)$ et $(HK)$ sont sécantes en $I$, et $(GH) \parallel (JK)$, donc, d'après le théorème de Thalès appliqué au sommet $I$ :

$$\frac{IG}{IJ} = \frac{IH}{IK}$$

$$\frac{4}{10} = \frac{6}{IK}$$

Par produit en croix :

$$4 \times IK = 10 \times 6 = 60$$

$$IK = \frac{60}{4} = 15 \text{ cm}$$

*Contrôle.* $\dfrac{4}{10} = 0{,}4$ et $\dfrac{6}{15} = 0{,}4$ : les deux rapports sont bien égaux.

### Pourquoi les autres réponses sont fausses

- **a)** on a écrit $\dfrac{IG}{IJ} = \dfrac{IK}{IH}$ : les rapports sont inversés d'une droite à l'autre.
- **b)** raisonnement additif : $IJ - IG = 6$, donc on a ajouté $6$ à $IH$ ; Thalès traduit une proportionnalité, pas une différence constante.
- **c)** on a calculé $\dfrac{IG \times IJ}{IH}$ au lieu de $\dfrac{IJ \times IH}{IG}$.

</details>

Avis : 

---

## 17. `cqc-cube-elevee-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : Pythagore appliqué deux fois dans l'espace (diagonale du cube), à la limite haute du programme de 3e.

**Énoncé :**

Un aquarium a la forme d'un cube d'arête $30$ cm.

Quelle est la valeur exacte de la longueur de la diagonale intérieure de cet aquarium (la distance entre un coin du fond et le coin du dessus le plus éloigné) ?

- a) $30\sqrt{2}$ cm
- b) $30\sqrt{3}$ cm
- c) $60$ cm
- d) $30 + 30\sqrt{2}$ cm

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La diagonale de l'espace d'un cube ne s'obtient pas en une seule étape : on calcule d'abord la diagonale d'une face carrée (par Pythagore, à partir de deux arêtes), puis on utilise cette diagonale comme côté d'un second triangle rectangle, avec la troisième arête, pour obtenir la diagonale de l'espace.

### Corrigé

**Étape 1 : diagonale d'une face.** Une face du cube est un carré de côté $a = 30$ cm. Sa diagonale $d_1$ est l'hypoténuse d'un triangle rectangle dont les deux côtés de l'angle droit mesurent chacun $30$ cm :

$$d_1^{2} = 30^{2} + 30^{2} = 900 + 900 = 1\,800$$

**Étape 2 : diagonale de l'espace.** La diagonale de l'espace $d$ est l'hypoténuse d'un second triangle rectangle, formé par la diagonale de la face $d_1$ (un côté de l'angle droit) et la troisième arête $a = 30$ cm (l'autre côté de l'angle droit) :

$$d^{2} = d_1^{2} + a^{2} = 1\,800 + 900 = 2\,700$$

$$d = \sqrt{2\,700} = \sqrt{900 \times 3} = 30\sqrt{3}$$

La valeur exacte de la diagonale est donc $d = 30\sqrt{3}$ cm.

**Valeur approchée.** Avec $\sqrt{3} \approx 1{,}732$ :

$$d \approx 30 \times 1{,}732 \approx 51{,}96$$

La diagonale intérieure de l'aquarium mesure $30\sqrt{3}$ cm, soit environ **52,0 cm**.

**Contrôle de vraisemblance.** Cette diagonale doit être strictement supérieure à l'arête ($30$ cm) et à la diagonale d'une face ($30\sqrt{2} \approx 42{,}4$ cm), puisqu'elle relie les deux coins les plus éloignés du cube : $52{,}0 > 42{,}4 > 30$, ce qui est cohérent.

### Pourquoi les autres réponses sont fausses

- **a)** c'est la diagonale d'une face carrée (première étape) ; il reste à la combiner avec la troisième arête.
- **c)** à la seconde étape, on a additionné $d_1^{2} + d_1^{2} = 3\,600$ au lieu de $d_1^{2} + 30^{2} = 2\,700$.
- **d)** on a additionné la diagonale d'une face et l'arête, alors qu'il faut appliquer le théorème de Pythagore.

</details>

Avis : 

---

## 18. `cqc-diagramme-semi-circulaire-elevee-0` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : écrire « semi-circulaire » en minuscules ; la mention « dont on ne connaît pas le nombre N » est superflue.

**Énoncé :**

Un village a fait tracer un diagramme semi-circulaire représentant la répartition de ses habitants actifs par secteur d'activité. Le secteur « Agriculture », dont l'angle mesure $60°$, compte $3\,000$ habitants actifs. Les deux autres secteurs mesurent : « Commerce » $72°$, et « Autres activités » (angle non indiqué).

Combien d'habitants actifs compte le secteur « Autres activités » ?

- a) $2\,400$
- b) $1\,200$
- c) $3\,600$
- d) $4\,800$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un diagramme semi-circulaire, chaque secteur est proportionnel à l'effectif qu'il représente : $\dfrac{\text{angle}}{180} = \dfrac{\text{effectif}}{N}$. Connaître le couple (angle, effectif) d'un seul secteur suffit donc à retrouver l'effectif total $N$ par produit en croix, avant d'appliquer la formule habituelle à chaque autre secteur ; un angle manquant s'obtient en complétant la somme des angles connus à $180°$.

### Corrigé

**Étape 1 : population active totale $N$.** Le secteur « Agriculture » a un angle de $60°$ pour un effectif de $3\,000$ habitants, donc par proportionnalité :

$$N = 3\,000 \times \frac{180}{60} = 3\,000 \times 3 = 9\,000 \ \text{habitants actifs}$$

**Étape 2 : angle du secteur « Autres activités ».**

$$180 - (60 + 72) = 180 - 132 = 48°$$

**Étape 3 : effectifs des deux autres secteurs.**

$$n_{\text{Commerce}} = \frac{72}{180} \times 9\,000 = 0{,}4 \times 9\,000 = 3\,600$$

$$n_{\text{Autres}} = \frac{48}{180} \times 9\,000 = 0{,}2\overline{6} \times 9\,000 = 2\,400$$

*Contrôle.* Les angles $60 + 72 + 48 = 180°$ recouvrent bien le demi-cercle entier, et les effectifs $3\,000 + 3\,600 + 2\,400 = 9\,000$ redonnent exactement la population active totale $N$ trouvée à l'étape 1.

Le village compte donc **9 000 habitants actifs**, répartis en $3\,000$ pour l'Agriculture, $3\,600$ pour le Commerce et $2\,400$ pour les Autres activités (angle de $48°$).

### Pourquoi les autres réponses sont fausses

- **b)** Utilise $360°$ pour le demi-cercle dans la dernière proportion : $\dfrac{48}{360}\times9\,000$.
- **c)** Donne l'effectif du secteur « Commerce » au lieu de celui de « Autres activités ».
- **d)** Utilise $360°$ pour trouver $N$ ($N=18\,000$), puis $\dfrac{48}{180}\times18\,000$.

</details>

Avis : 

---

## 19. `cqc-division-de-fractions-moyenne-0` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : « On donne le quotient… Quel est ce quotient » est maladroit ; écrire « Calcule le quotient de 7/10 par 14/15 ».

**Énoncé :**

Calcule le quotient de la fraction $\dfrac{7}{10}$ par la fraction $\dfrac{14}{15}$.

Quel est le résultat, sous forme de fraction irréductible ?

- a) $\dfrac{4}{3}$
- b) $\dfrac{49}{75}$
- c) $\dfrac{3}{4}$
- d) $\dfrac{3}{2}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

« Le quotient de $A$ par $B$ » désigne toujours $A \div B$ : $A$ est le dividende (le premier nombre cité), $B$ le diviseur (le second). Diviser par une fraction revient ensuite à multiplier par son inverse.

### Corrigé

Le quotient demandé est $\dfrac{7}{10} \div \dfrac{14}{15}$, dans cet ordre précis : inverser l'ordre des deux fractions donnerait un résultat différent.

On multiplie par l'inverse du diviseur :

$$\dfrac{7}{10} \div \dfrac{14}{15} = \dfrac{7}{10} \times \dfrac{15}{14}$$

On simplifie avant de multiplier : $7$ et $14$ sont tous deux divisibles par $7$, et $15$ et $10$ sont tous deux divisibles par $5$ :

$$\dfrac{7}{10} \times \dfrac{15}{14} = \dfrac{1}{2} \times \dfrac{3}{2} = \dfrac{3}{4}$$

$3$ et $4$ n'ont aucun facteur commun autre que $1$, donc $\dfrac{3}{4}$ est déjà irréductible.

Vérification numérique : $\dfrac{7}{10}=0{,}7$ et $\dfrac{14}{15}\approx0{,}933$ ; $0{,}7 \div 0{,}933 \approx 0{,}75$, ce qui correspond bien à $\dfrac{3}{4}=0{,}75$.

$$\dfrac{7}{10} \div \dfrac{14}{15} = \dfrac{3}{4}$$

### Pourquoi les autres réponses sont fausses

- **a)** Inverse l'ordre des deux fractions (calcule $\dfrac{14}{15}\div\dfrac{7}{10}$).
- **b)** Multiplie les deux fractions sans retourner la deuxième.
- **d)** Simplifie les numérateurs mais oublie le facteur $2$ du dénominateur : $\dfrac{1}{2}\times\dfrac{3}{2}$ devient $\dfrac{3}{2}$.

</details>

Avis : 

---

## 20. `cqc-double-distributivite-elevee-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : développer un produit de trois facteurs (degré 3) est à la limite haute du programme de 3e.

**Énoncé :**

Quel est le développement réduit de l'expression $G(x) = (x-2)(3x+1)(x+4)$ ?

- a) $3x^3+17x^2-22x-8$
- b) $3x^3+7x^2-22x-8$
- c) $3x^3+7x^2-20x-8$
- d) $3x^3+7x^2-22x+8$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour développer un produit de trois facteurs, on développe d'abord le produit de deux d'entre eux par double distributivité, $(a+b)(c+d)=ac+ad+bc+bd$, on réduit ce résultat intermédiaire, puis on distribue chaque terme du troisième facteur sur chaque terme obtenu, avant de réduire une dernière fois.

### Corrigé

**Étape 1 : on développe les deux premiers facteurs.**

$$(x-2)(3x+1) = 3x^2 + x - 6x - 2 = 3x^2 - 5x - 2$$

**Étape 2 : on multiplie ce résultat par le troisième facteur $(x+4)$.**

$$G(x) = (3x^2-5x-2)(x+4)$$

$$= 3x^2\times x + 3x^2\times 4 - 5x\times x - 5x\times 4 - 2\times x - 2\times 4$$

$$= 3x^3 + 12x^2 - 5x^2 - 20x - 2x - 8$$

**Étape 3 : on réduit les termes de même degré.**

$$G(x) = 3x^3 + 7x^2 - 22x - 8$$

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur $-5x\times x$ (écrit $+5x^2$) : $12x^2+5x^2=17x^2$.
- **c)** Oublie le terme $-2x$ : seul $-20x$ est conservé.
- **d)** Écrit $-2\times4=+8$ : erreur de signe sur le terme constant.

</details>

Avis : 

---

## 21. `cqc-double-distributivite-faible-1` (séries BEPC)

**Énoncé :**

Quel est le développement réduit de l'expression $C = (5-2x)(4+3x)$ ?

- a) $-6x^2+7x+20$
- b) $6x^2+7x+20$
- c) $-6x^2+23x+20$
- d) $-6x^2+15x+20$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour développer un produit de deux binômes $(a+b)(c+d)$, on distribue chaque terme du premier facteur sur chaque terme du second, selon la règle $(a+b)(c+d) = ac+ad+bc+bd$, puis on réduit les termes semblables. L'ordre dans lequel les termes apparaissent à l'intérieur de chaque facteur ne change rien à la méthode.

### Corrigé

$$C = (5-2x)(4+3x) = 5\times 4 + 5\times 3x + (-2x)\times 4 + (-2x)\times 3x$$

$$C = 20 + 15x - 8x - 6x^2$$

En réduisant les termes en $x$ :

$$C = -6x^2 + 7x + 20$$

### Pourquoi les autres réponses sont fausses

- **b)** Écrit $(-2x)\times3x=+6x^2$ : erreur de signe sur le terme en $x^2$.
- **c)** Écrit $(-2x)\times4=+8x$ : erreur de signe, d'où $15x+8x=23x$.
- **d)** Oublie le terme $(-2x)\times4=-8x$ : seul $15x$ est conservé.

</details>

Avis : 

---

## 22. `cqc-droite-horizontale-elevee-0` (séries BEPC)

**Remarque du relecteur :** Le point C ne sert pas à la question posée (il appartient sans doute à un exercice plus long) ; il est sans danger ici.

**Énoncé :**

Dans un repère orthonormé, on donne les trois sommets d'un triangle : $A(1\,;\,4)$, $B(6\,;\,4)$ et $C(3\,;\,-2)$.

Quelle est une équation de la droite $(AB)$ ?

- a) $x = 4$
- b) $y = 0$
- c) $y = -2$
- d) $y = 4$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Avant de calculer un coefficient directeur, il est utile de comparer directement les coordonnées des deux points : si leurs ordonnées sont égales, la droite qui les joint est horizontale, quelles que soient leurs abscisses respectives.

### Corrigé

On compare les ordonnées de $A$ et de $B$ : $y_A = 4$ et $y_B = 4$, ces deux ordonnées sont **égales**, bien que les abscisses $x_A=1$ et $x_B=6$ soient différentes.

La droite $(AB)$ est donc **horizontale**.

*Équation.* Comme tous les points de $(AB)$ ont pour ordonnée $4$ :

$$(AB) : y = 4$$

*Contrôle par le coefficient directeur.* Le calcul habituel donne :

$$a = \dfrac{y_B-y_A}{x_B-x_A} = \dfrac{4-4}{6-1} = \dfrac{0}{5} = 0$$

Un coefficient directeur nul confirme bien qu'il s'agit d'une droite horizontale.

*Remarque.* Le troisième sommet $C(3\,;\,-2)$ n'appartient pas à cette droite, puisque son ordonnée $-2$ est différente de $4$ : c'est cohérent, puisque $A$, $B$ et $C$ forment un triangle (trois points non alignés).

### Pourquoi les autres réponses sont fausses

- **a)** Confond droite horizontale et droite verticale : $x=4$ est la droite verticale passant par les points d'abscisse $4$.
- **b)** Confond le coefficient directeur ($0$) avec l'ordonnée à l'origine ($4$).
- **c)** Utilise l'ordonnée du point $C$, qui n'appartient pas à la droite $(AB)$.

</details>

Avis : 

---

## 23. `cqc-droite-horizontale-faible-1` (séries BEPC)

**Remarque du relecteur :** Préciser « parallèle à l'axe des abscisses » ou « dans un repère usuel » : « horizontale » est l'usage courant mais il est imprécis.

**Énoncé :**

On donne les équations de quatre droites :

$(D_1) : y = 6$ ; $(D_2) : x = 6$ ; $(D_3) : y = 6x$ ; $(D_4) : x + y = 6$.

Laquelle de ces quatre droites est parallèle à l'axe des abscisses ?

- a) $(D_2)$
- b) $(D_3)$
- c) $(D_1)$
- d) $(D_4)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Une droite horizontale a une équation de la forme $y = k$ (une constante, sans terme en $x$). Elle a toujours pour coefficient directeur $0$, puisqu'on peut l'écrire $y = 0 \times x + k$ : son ordonnée ne varie jamais lorsque $x$ varie.

### Corrigé

On examine chaque équation.

$(D_1) : y = 6$ est de la forme $y=k$ avec $k=6$, sans aucun terme en $x$ : c'est une droite horizontale.

$(D_2) : x = 6$ ne contient aucun terme en $y$ : c'est une droite verticale, pas horizontale.

$(D_3) : y = 6x$ est de la forme $y = ax$ avec $a=6 \neq 0$ : c'est une droite oblique passant par l'origine.

$(D_4) : x + y = 6$ s'écrit aussi $y = -x + 6$, de coefficient directeur $-1 \neq 0$ : c'est une droite oblique.

La droite horizontale est donc $(D_1)$, et son coefficient directeur vaut $0$ (on peut écrire $(D_1) : y = 0 \times x + 6$).

### Pourquoi les autres réponses sont fausses

- **a)** $x=6$ est l'équation d'une droite verticale.
- **b)** $y=6x$ est une droite oblique passant par l'origine, de coefficient directeur $6$.
- **d)** $x+y=6$ s'écrit $y=-x+6$ : droite oblique de coefficient directeur $-1$.

</details>

Avis : 

---

## 24. `cqc-duree-faible-1` (séries BEPC)

**Énoncé :**

Un match de football débute à $15\text{h}20$ et se termine à $17\text{h}05$. Quelle est la durée de ce match ?

- a) 2h15
- b) 1h45
- c) 2h45
- d) 1h25

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour calculer la durée écoulée entre deux heures, on soustrait l'heure de départ à l'heure de fin. Si les minutes de l'heure de fin sont inférieures à celles de l'heure de départ, on emprunte $60$ minutes à l'heure précédente avant de soustraire.

### Corrigé

On veut calculer $17\text{h}05 - 15\text{h}20$.

*Difficulté.* Les minutes de fin ($05$) sont inférieures aux minutes de départ ($20$) : on ne peut pas soustraire directement.

*Emprunt.* On transforme $17\text{h}05$ en empruntant une heure : $17\text{h}05 = 16\text{h}65$ (puisque $16\text{h} + 65\text{min} = 16\text{h} + 1\text{h}05 = 17\text{h}05$).

*Soustraction.*

$$\text{heures : } 16 - 15 = 1 \qquad ; \qquad \text{minutes : } 65 - 20 = 45$$

La durée du match est donc $1\text{h}45\text{min}$.

*Contrôle.* $15\text{h}20 + 1\text{h}45\text{min} = 16\text{h}65\text{min} = 17\text{h}05$

### Pourquoi les autres réponses sont fausses

- **a)** Soustrait les heures ($17-15=2$) puis les minutes dans l'autre sens ($20-05=15$).
- **c)** Oublie l'emprunt d'une heure : $17-15=2$ et $65-20=45$.
- **d)** Compte $20$ min au lieu de $40$ min de $15\text{h}20$ à $16\text{h}00$, puis ajoute $1\text{h}05$.

</details>

Avis : 

---

## 25. `cqc-duree-moyenne-0` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : le contexte (une équation qui fixe la durée d'attente) est artificiel.

**Énoncé :**

À l'entrée d'un stade, l'affluence des supporters est telle que la durée d'attente $T$, en minutes, d'un supporter avant d'entrer vérifie l'équation :

$$3T - 45 = 165$$

Sachant que ce supporter se présente au guichet à $18\text{h}50$, à quelle heure entre-t-il au stade ?

- a) 19h30
- b) 20h10
- c) 22h20
- d) 20h00

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On résout d'abord l'équation pour obtenir la durée en minutes. Une durée en minutes se convertit en heures et minutes par division euclidienne par $60$ : le quotient donne le nombre d'heures, le reste le nombre de minutes restantes. On ajoute enfin cette durée à l'heure de départ pour obtenir l'heure d'arrivée.

### Corrigé

*Résolution de l'équation.*

$$3T - 45 = 165$$

$$3T = 165 + 45 = 210$$

$$T = \dfrac{210}{3} = 70$$

La durée d'attente est donc $T = 70$ minutes.

*Conversion en heures et minutes.*

$$70 = 60 \times 1 + 10$$

soit $1$ heure et $10$ minutes.

*Heure d'entrée au stade.* Le supporter se présente à $18\text{h}50$ ; on ajoute $1\text{h}10\text{min}$ :

*Addition des minutes.* $50 + 10 = 60$ min $= 1$ heure exactement, sans minutes restantes.

*Addition des heures.* $18\text{h} + 1\text{h}$ (durée) $+ 1\text{h}$ (obtenue par la conversion des minutes) $= 20\text{h}$.

Le supporter entre donc au stade à **20h00**.

*Contrôle.* $18\text{h}50 + 1\text{h}10\text{min} = 19\text{h}60\text{min} = 20\text{h}00$

### Pourquoi les autres réponses sont fausses

- **a)** Résout mal l'équation : $3T=165-45=120$, d'où $T=40$ min.
- **b)** Compte deux fois les $10$ minutes de $18\text{h}50$ à $19\text{h}00$, puis ajoute $1\text{h}10$.
- **c)** Oublie de diviser par $3$ : prend $T=210$ min.

</details>

Avis : 

---

## 26. `cqc-encadrement-elevee-0` (séries BEPC)

**Remarque du relecteur :** Le choix b (-0,277 < … < -0,276) est aussi un encadrement VRAI (valeur ≈ -0,27671) à trois décimales : l'énoncé ne dit pas explicitement qu'il faut partir de l'encadrement donné de √3 ; préciser « en utilisant l'encadrement donné » ou remplacer b par un encadrement faux.

**Énoncé :**

Sachant que $1{,}732 < \sqrt{3} < 1{,}733$, quel est l'encadrement, obtenu en utilisant uniquement cet encadrement de $\sqrt{3}$, de $\dfrac{7 - 5\sqrt{3}}{6}$ dont les bornes sont écrites avec trois décimales (borne inférieure arrondie par défaut, borne supérieure arrondie par excès) ?

- a) $-0{,}278 < \dfrac{7 - 5\sqrt{3}}{6} < -0{,}276$
- b) $-0{,}277 < \dfrac{7 - 5\sqrt{3}}{6} < -0{,}276$
- c) $2{,}610 < \dfrac{7 - 5\sqrt{3}}{6} < 2{,}611$
- d) $-1{,}665 < \dfrac{7 - 5\sqrt{3}}{6} < -1{,}660$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans une expression comportant plusieurs opérations successives, on transforme l'encadrement pas à pas dans l'ordre des opérations : multiplication, puis passage à l'opposé (qui inverse le sens), puis addition, puis division. Chaque inversion de sens ne doit être appliquée qu'une seule fois, au bon endroit.

### Corrigé

*Encadrement de départ.*
$$1{,}732 < \sqrt{3} < 1{,}733$$

*Étape 1 - multiplier par $5$.*
$$8{,}660 < 5\sqrt{3} < 8{,}665$$

*Étape 2 - passer à l'opposé.* Le sens des inégalités s'inverse :
$$-8{,}665 < -5\sqrt{3} < -8{,}660$$

*Étape 3 - ajouter $7$.*
$$7 - 8{,}665 < 7 - 5\sqrt{3} < 7 - 8{,}660$$
$$-1{,}665 < 7 - 5\sqrt{3} < -1{,}660$$

*Étape 4 - diviser par $6$.*
$$\frac{-1{,}665}{6} < \frac{7 - 5\sqrt{3}}{6} < \frac{-1{,}660}{6}$$
$$-0{,}2775 < \frac{7 - 5\sqrt{3}}{6} < -0{,}27667$$

*Élargissement au millième (ordre 3).* On arrondit la borne inférieure vers le bas (plus négative) et la borne supérieure vers le haut (moins négative) :
$$-0{,}278 < \frac{7 - 5\sqrt{3}}{6} < -0{,}276$$

### Piège à éviter
Le passage à l'opposé n'a lieu qu'une seule fois, à l'étape 2 ; les étapes 3 et 4 conservent le sens des inégalités. Élargir un encadrement de nombres négatifs signifie rendre le minorant **plus négatif** et le majorant **moins négatif** : c'est l'inverse de l'intuition qu'on a avec des nombres positifs.

### Pourquoi les autres réponses sont fausses

- **b)** Arrondit la borne inférieure $-0{,}2775$ vers $-0{,}277$ (par excès) : cet encadrement ne contient pas toutes les valeurs possibles.
- **c)** Ne passe pas à l'opposé de $5\sqrt{3}$ et calcule en fait $\dfrac{7 + 5\sqrt{3}}{6}$.
- **d)** S'arrête à l'étape $7 - 5\sqrt{3}$ et oublie de diviser par $6$.

</details>

Avis : 

---

## 27. `cqc-facteur-commun-faible-1` (séries BEPC)

**Énoncé :**

Quelle est la forme factorisée de $C(x) = 5x(x+4) - 3(x+4)$ ?

- a) $C(x) = (x+4)(5x+3)$
- b) $C(x) = (x+4)(5x-12)$
- c) $C(x) = (x+4)(5x-3)$
- d) $C(x) = (x+4)(3-5x)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Un facteur commun peut être une simple parenthèse répétée dans deux termes, même si les coefficients qui l'accompagnent sont différents : on factorise cette parenthèse en gardant, dans le facteur restant, le signe de chaque terme d'origine.

### Corrigé

Le facteur $(x+4)$ apparaît dans les deux termes de $C(x)$, avec un signe $-$ devant le second.

$C(x) = (x+4)(5x - 3)$

Forme factorisée : $C(x) = (x+4)(5x-3)$.

### Pourquoi les autres réponses sont fausses

- **a)** Oublie le signe $-$ devant le second terme.
- **b)** Distribue le $-3$ sur la parenthèse $(x+4)$ avant de factoriser.
- **d)** Inverse l'ordre des termes du second facteur, ce qui change son signe.

</details>

Avis : 

---

## 28. `cqc-figures-superposables-moyenne-1` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : « deux sommets correspondants de deux parcelles triangulaires » n'a pas de sens ici et n'apporte rien ; simplifier le contexte.

**Énoncé :**

Dans un repère orthonormé $(O\,;\,\vec{i}\,;\,\vec{j})$ gradué en mètres, un géomètre relève deux points : $G(-4\,;\,2)$ et $G'(6\,;\,2)$. Quelle est une équation de la médiatrice du segment $[GG']$ ?

- a) $x = 2$
- b) $y = 2$
- c) $x = 1$
- d) $x = 5$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour trouver la médiatrice d'un segment, on cherche son milieu puis la perpendiculaire au segment passant par ce milieu. Si deux points ont la même ordonnée, le segment qui les joint est horizontal et sa médiatrice est la droite verticale passant par son milieu, d'équation $x = $ abscisse du milieu.

### Corrigé

$G(-4\,;\,2)$ et $G'(6\,;\,2)$ ont la même ordonnée : le segment $[GG']$ est horizontal. Son milieu a pour coordonnées $\left(\dfrac{-4+6}{2}\,;\,2\right) = (1\,;\,2)$. La médiatrice d'un segment horizontal est la droite verticale passant par son milieu : c'est la droite d'équation $x = 1$.

*Contrôle.* Le point $(1\,;\,2)$ est à $5$ unités de $G$ et de $G'$ ($1-(-4) = 5$ et $6-1 = 5$).

### Pourquoi les autres réponses sont fausses

- **a)** on a additionné les abscisses $-4$ et $6$ sans diviser par $2$ pour obtenir le milieu.
- **b)** c'est la droite (horizontale) qui contient $G$ et $G'$, et non leur médiatrice, qui est perpendiculaire à $(GG')$.
- **d)** $5$ est la demi-distance $GG'$ et non l'abscisse du milieu du segment.

</details>

Avis : 

---

## 29. `cqc-hauteur-moyenne-2` (séries BEPC)

**Énoncé :**

Une pyramide a pour base un rectangle de $8$ cm sur $5$ cm et pour volume $100$ cm³. Calcule sa hauteur.

- a) $2{,}5$ cm
- b) $7{,}5$ cm
- c) $12{,}5$ cm
- d) $20$ cm

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Le volume d'une pyramide vaut le tiers du produit de l'aire de sa base par sa hauteur : $V = \dfrac{\mathcal{B} \times h}{3}$, d'où $h = \dfrac{3V}{\mathcal{B}}$.

### Corrigé

*Aire de la base.* $$\mathcal{B} = 8 \times 5 = 40 \ \text{cm}^2$$

*Hauteur.*

$$h = \frac{3V}{\mathcal{B}} = \frac{3 \times 100}{40} = \frac{300}{40} = 7{,}5$$

$h = 7{,}5$ cm.

*Vérification.* $\dfrac{40 \times 7{,}5}{3} = \dfrac{300}{3} = 100$ cm³

### Pourquoi les autres réponses sont fausses

- **a)** le facteur $3$ a été oublié : $h = \dfrac{V}{\mathcal{B}}$ au lieu de $\dfrac{3V}{\mathcal{B}}$.
- **c)** on a divisé le volume par la longueur $8$ cm du rectangle au lieu de son aire.
- **d)** on a divisé le volume par la largeur $5$ cm du rectangle au lieu de son aire.

</details>

Avis : 

---

## 30. `cqc-hauteur-d-une-pyramide-elevee-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : tétraèdre régulier et centre de gravité de la base, rendus accessibles grâce aux résultats admis (GA et angle droit en G).

**Énoncé :**

$SABC$ est un tétraèdre régulier d'arête $6$ cm : ses six arêtes ont toutes la même longueur, $6$ cm. Le sommet $S$ se projette orthogonalement en $G$, centre de gravité du triangle équilatéral $ABC$. On admet que la distance de $G$ à un sommet de la base vaut $GA = \dfrac{a\sqrt{3}}{3}$, où $a$ est la longueur de l'arête, et que le triangle $SGA$ est rectangle en $G$.

Quelle est la hauteur $SG$ de ce tétraèdre, sous forme exacte simplifiée ?

- a) $4\sqrt{3}$ cm
- b) $2\sqrt{3}$ cm
- c) $6-2\sqrt{3}$ cm
- d) $2\sqrt{6}$ cm

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un tétraèdre régulier, le sommet se projette orthogonalement sur le centre de gravité de la face opposée. Le triangle formé par le sommet, ce centre de gravité et un sommet de la base est rectangle en ce centre de gravité : le théorème de Pythagore s'y applique, avec l'arête du tétraèdre comme hypoténuse.

### Corrigé

*Calcul de $GA$.*

$$GA = \frac{a\sqrt{3}}{3} = \frac{6\sqrt{3}}{3} = 2\sqrt{3} \ \text{cm} \qquad \Longrightarrow \qquad GA^2 = (2\sqrt{3})^2 = 4 \times 3 = 12$$

*Théorème de Pythagore dans le triangle $SGA$, rectangle en $G$, d'hypoténuse $[SA]$ (une arête du tétraèdre, donc $SA = 6$ cm).*

$$SA^2 = SG^2 + GA^2 \quad \Longrightarrow \quad SG^2 = SA^2 - GA^2 = 6^2 - 12 = 36 - 12 = 24$$

*Extraction et simplification du radical.*

$$SG = \sqrt{24} = \sqrt{4 \times 6} = \sqrt{4} \times \sqrt{6} = 2\sqrt{6}$$

La hauteur du tétraèdre vaut exactement $SG = 2\sqrt{6}$ cm, soit environ $2 \times 2{,}449 \approx 4{,}90$ cm.

*Contrôle de vraisemblance.* $4{,}90 < 6$ : la hauteur reste bien inférieure à l'arête, qui est l'hypoténuse du triangle $SGA$.

### Conseil
Cette relation, $SG = \dfrac{a\sqrt{6}}{3}$, redonne bien $\dfrac{6\sqrt{6}}{3} = 2\sqrt{6}$ : c'est la formule générale de la hauteur d'un tétraèdre régulier d'arête $a$, qu'on peut retrouver à chaque fois par le même raisonnement en triangle rectangle plutôt que de l'apprendre par cœur.

### Pourquoi les autres réponses sont fausses

- **a)** on a additionné les carrés ($36+12 = 48$) au lieu de les soustraire : l'arête $SA$ est l'hypoténuse, donc $SG^2 = SA^2 - GA^2$.
- **b)** c'est la distance $GA$, non la hauteur $SG$ : le calcul s'est arrêté avant l'application du théorème de Pythagore.
- **c)** on a soustrait les longueurs ($SA - GA$) au lieu de leurs carrés : le théorème de Pythagore porte sur les carrés.

</details>

Avis : 

---

## 31. `cqc-image-d-une-figure-moyenne-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : homothétie de rapport négatif, à vérifier selon le programme de 3e du pays.

**Énoncé :**

Le segment $[MN]$ mesure $8$ cm. Soit $h$ l'homothétie de centre $O$ (un point extérieur au segment $[MN]$) et de rapport $k = -\dfrac{3}{2}$. On note $M'$ et $N'$ les images respectives de $M$ et $N$ par $h$. Quelle est la longueur $M'N'$ ?

- a) $8$ cm
- b) $\dfrac{16}{3}$ cm
- c) $18$ cm
- d) $12$ cm

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans une homothétie de rapport $k$, toutes les longueurs sont multipliées par $|k|$, la valeur absolue du rapport. Le signe de $k$ n'agit pas sur les longueurs : il indique seulement de quel côté du centre se trouve l'image.

### Corrigé

$$M'N' = |k| \times MN = \left|-\frac{3}{2}\right| \times 8 = \frac{3}{2}\times 8 = 12 \text{ cm}$$

### Pourquoi les autres réponses sont fausses

- **a)** on a cru que l'homothétie conservait les longueurs, comme une symétrie : elle les multiplie par $|k|$.
- **b)** on a divisé par $|k|$ ($8\times\dfrac{2}{3}$) au lieu de multiplier : le rapport $\dfrac{3}{2}$ est supérieur à $1$, c'est un agrandissement.
- **c)** on a multiplié par $k^2 = \dfrac{9}{4}$, coefficient des aires, alors que les longueurs sont multipliées par $|k|$.

</details>

Avis : 

---

## 32. `cqc-nature-d-un-triangle-moyenne-0` (séries BEPC)

**Énoncé :**

Dans un repère orthonormé $(O, I, J)$ du plan, on donne les points $A(0\,;\,0)$, $B(4\,;\,0)$ et $C(2\,;\,2\sqrt{3})$.

Quelle est la nature exacte du triangle $ABC$ ?

- a) Isocèle en $C$, mais non équilatéral.
- b) Rectangle en $C$.
- c) Équilatéral.
- d) Quelconque.

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour déterminer la nature exacte d'un triangle à partir des coordonnées de ses sommets, on calcule les trois longueurs de ses côtés avec la formule de la distance $MN = \sqrt{(x_N-x_M)^2+(y_N-y_M)^2}$, puis on compare ces trois valeurs : trois côtés égaux signalent un triangle équilatéral.

### Corrigé

*Longueur $AB$.*

$$AB = \sqrt{(4-0)^2+(0-0)^2} = \sqrt{16} = 4$$

*Longueur $AC$.*

$$AC = \sqrt{(2-0)^2+(2\sqrt{3}-0)^2} = \sqrt{4 + 4\times3} = \sqrt{4+12} = \sqrt{16} = 4$$

*Longueur $BC$.*

$$BC = \sqrt{(2-4)^2+(2\sqrt{3}-0)^2} = \sqrt{4 + 12} = \sqrt{16} = 4$$

*Comparaison.*

$$AB = AC = BC = 4$$

Les trois côtés du triangle $ABC$ ont la même longueur : le triangle $ABC$ est donc **équilatéral**.

### Piège à éviter
Une fois les trois côtés reconnus égaux, la nature exacte est entièrement déterminée : un triangle équilatéral a nécessairement ses trois angles égaux à $60°$, donc aucun angle droit. Il est inutile (et incorrect) de chercher en plus une propriété de rectangle : les deux ne coexistent jamais.

### Pourquoi les autres réponses sont fausses

- **a)** on a calculé $(2\sqrt{3})^2 = 6$ au lieu de $12$ : on trouve alors $AC = BC = \sqrt{10} \neq AB$.
- **b)** les trois côtés valent $4$ : un triangle équilatéral a trois angles de $60°$, aucun n'est droit.
- **d)** les trois longueurs sont égales ($AB = AC = BC = 4$), le triangle a donc des propriétés particulières.

</details>

Avis : 

---

## 33. `cqc-norme-d-un-vecteur-moyenne-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : notation ||d|| et mot « norme » ; en 3e on parle surtout de distance AB dans un repère orthonormé.

**Énoncé :**

Un signal radar enregistre le déplacement d'un aéronef entre deux instants successifs. Dans un repère orthonormé, ce déplacement est modélisé par le vecteur $\vec{d}\,(6\,;\,10)$, coordonnées exprimées en kilomètres.

Quelle est la norme $\|\vec{d}\|$ de ce vecteur (valeur exacte, simplifiée au maximum) ?

- a) $4\sqrt{34}$ km
- b) $2\sqrt{34}$ km
- c) $16$ km
- d) $4$ km

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La norme d'un vecteur $\vec{u}\,(x\,;\,y)$ se calcule par $\|\vec{u}\| = \sqrt{x^{2}+y^{2}}$. Quand le résultat n'est pas un carré parfait, on le simplifie en extrayant le plus grand carré parfait possible du nombre sous la racine.

### Corrigé

$$\|\vec{d}\| = \sqrt{6^{2}+10^{2}} = \sqrt{36+100} = \sqrt{136}$$

*Simplification.* $136 = 4 \times 34$, et $4$ est le plus grand carré parfait qui divise $136$ :

$$\|\vec{d}\| = \sqrt{4 \times 34} = 2\sqrt{34}$$

La norme est la distance parcourue en ligne droite : environ $2 \times 5{,}83 \approx 11{,}66$ km.

### Pourquoi les autres réponses sont fausses

- **a)** on a sorti $4$ de la racine au lieu de $\sqrt{4}=2$ : $\sqrt{4\times34}=2\sqrt{34}$.
- **c)** on a additionné les coordonnées ($6+10$) au lieu d'appliquer $\sqrt{x^{2}+y^{2}}$.
- **d)** on a oublié les carrés et calculé $\sqrt{6+10}$ au lieu de $\sqrt{6^{2}+10^{2}}$.

</details>

Avis : 

---

## 34. `cqc-produit-en-croix-moyenne-1` (séries BEPC)

**Énoncé :**

Un groupe de 6 ouvriers construit un mur en 15 jours, tous en travaillant au même rythme. Combien de jours faudrait-il à 10 ouvriers, travaillant au même rythme, pour construire le même mur ?

- a) 9 jours
- b) 25 jours
- c) 11 jours
- d) 1,5 jour

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Deux grandeurs sont inversement proportionnelles quand leur produit reste constant : si l'une est multipliée par un facteur, l'autre est divisée par ce même facteur.

### Corrigé

Le nombre d'ouvriers et le nombre de jours nécessaires sont inversement proportionnels : plus il y a d'ouvriers, moins il faut de jours, et leur produit (le travail total, en ouvrier-jours) reste constant.

$$6 \times 15 = 90 \text{ (ouvrier-jours)}$$

Avec 10 ouvriers, en notant $d$ le nombre de jours cherché :
$$10 \times d = 90$$
$$d = \frac{90}{10} = 9$$

Il faudrait $9$ jours à 10 ouvriers.

*Contrôle.* 10 ouvriers travaillent plus vite que 6 : il est cohérent que $9$ jours soit inférieur à $15$ jours.

### Piège à éviter
N'écris pas $\dfrac{6}{15}=\dfrac{10}{d}$ comme pour une proportionnalité directe : plus d'ouvriers signifie moins de jours. C'est le produit $6\times15$ qui reste constant.

### Pourquoi les autres réponses sont fausses

- **b)** on a traité la situation comme une proportionnalité directe ($15\times10\div6$) : plus d'ouvriers donnerait plus de jours, ce qui est absurde.
- **c)** on a raisonné par différence : 4 ouvriers de plus donneraient 4 jours de moins, ce qui ne tient pas compte de la proportionnalité.
- **d)** on a divisé $15$ par $10$ sans tenir compte du nombre d'ouvriers de départ.

</details>

Avis : 

---

## 35. `cqc-relation-de-chasles-moyenne-2` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : imposer « la relation de Chasles » est artificiel, puisque le calcul direct D - A suffit et que B et C ne servent qu'à ce détour ; écrire par exemple « Calcule les coordonnées de AD ». Mettre aussi les flèches de vecteur dans les choix.

**Énoncé :**

Dans un repère, on considère quatre points $A(-2\,;\,1)$, $B(3\,;\,4)$, $C(6\,;\,-1)$ et $D(1\,;\,5)$.

En utilisant la relation de Chasles, quelles sont les coordonnées du vecteur $\overrightarrow{AD}$ ?

- a) $(3\,;\,-8)$
- b) $(13\,;\,4)$
- c) $(-3\,;\,-4)$
- d) $(3\,;\,4)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

La relation de Chasles s'applique plusieurs fois de suite lorsqu'un trajet comporte plusieurs étapes : $\overrightarrow{AB}+\overrightarrow{BC}+\overrightarrow{CD}=\overrightarrow{AD}$. Chaque vecteur intermédiaire se calcule par $\overrightarrow{MN}\,(x_N-x_M\,;\,y_N-y_M)$.

### Corrigé

$$\overrightarrow{AB}\,(5\,;\,3) \qquad \overrightarrow{BC}\,(3\,;\,-5) \qquad \overrightarrow{CD}\,(-5\,;\,6)$$

$$\overrightarrow{AD} = \overrightarrow{AB} + \overrightarrow{BC} + \overrightarrow{CD} = (5+3-5\,;\,3-5+6) = (3\,;\,4)$$

Vérification directe : $\overrightarrow{AD}\,(1-(-2)\,;\,5-1) = (3\,;\,4)$.

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe sur $\overrightarrow{CD}\,(-5\,;\,6)$ : on a retranché $6$ à l'ordonnée au lieu de l'ajouter.
- **b)** erreur de signe sur l'abscisse de $\overrightarrow{CD}$ : on a ajouté $5$ au lieu d'ajouter $-5$.
- **c)** ce sont les coordonnées du vecteur opposé $\overrightarrow{DA}$ : on a inversé l'origine et l'extrémité.

</details>

Avis : 

---

## 36. `cqc-repere-moyenne-1` (séries BEPC)

**Énoncé :**

On considère la droite $(D)$ d'équation $y = -3x + 1$. Lequel des points suivants appartient à la droite $(D)$ ?

- a) $L(-1\,;\,-2)$
- b) $M(-1\,;\,2)$
- c) $K(-1\,;\,4)$
- d) $N(4\,;\,-1)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour savoir si un point appartient à une droite d'équation $y = ax + b$, on remplace $x$ par l'abscisse du point dans l'équation et on compare le résultat obtenu à l'ordonnée du point. Le point appartient à la droite si et seulement si les deux valeurs sont égales.

### Corrigé

*Calcul de l'ordonnée attendue pour $x = -1$.*

$$y = -3 \times (-1) + 1$$

$$y = 3 + 1 = 4$$

*Comparaison.* L'ordonnée obtenue, $4$, est égale à l'ordonnée du point $K$, qui vaut aussi $4$.

$$4 = 4$$

Le point $K(-1\,;\,4)$ appartient donc bien à la droite $(D)$. Les autres points proposés ne vérifient pas l'équation.

### Pourquoi les autres réponses sont fausses

- **a)** Pour $x=-1$, $-3\times(-1)$ vaut $3$ et non $-3$ ; l'ordonnée attendue est $4$, pas $-2$.
- **b)** Tu as calculé $3 - 1$ : le terme $+1$ de l'équation est devenu $-1$ ; l'ordonnée attendue est $4$.
- **d)** Les coordonnées de $K$ sont inversées ; pour $x=4$, l'équation donne $y=-11$, et non $-1$.


</details>

Avis : 

---

## 37. `cqc-repere-moyenne-3` (séries BEPC)

**Remarque du relecteur :** Le choix a) porte le nom A' alors que les autres ne donnent que le couple : présentation hétérogène qui signale la bonne réponse.

**Énoncé :**

Dans un repère, on donne les points $A(5\,;\,-3)$ et $O(1\,;\,2)$. Quelles sont les coordonnées du point $A'$, symétrique du point $A$ par rapport au point $O$ ?

- a) $A'(-3\,;\,7)$
- b) $A'(-3\,;\,1)$
- c) $A'(-4\,;\,5)$
- d) $A'(3\,;\,-0{,}5)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Le point $A'$ est le symétrique de $A$ par rapport à $O$ si et seulement si $O$ est le milieu du segment $[AA']$. On retrouve donc les coordonnées de $A'$ en utilisant la formule du milieu à l'envers : $x_{A'} = 2x_O - x_A$ et $y_{A'} = 2y_O - y_A$.

### Corrigé

*Calcul de l'abscisse de $A'$.*

$$x_{A'} = 2 \times x_O - x_A = 2 \times 1 - 5 = 2 - 5 = -3$$

*Calcul de l'ordonnée de $A'$.*

$$y_{A'} = 2 \times y_O - y_A = 2 \times 2 - (-3) = 4 + 3 = 7$$

$$A'(-3\,;\,7)$$

*Contrôle.* $O$ doit être le milieu de $[AA']$ : $\dfrac{5 + (-3)}{2} = \dfrac{2}{2} = 1 = x_O$ et $\dfrac{-3 + 7}{2} = \dfrac{4}{2} = 2 = y_O$. Les deux coordonnées de $O$ sont retrouvées, le résultat est confirmé.

### Pourquoi les autres réponses sont fausses

- **b)** L'ordonnée est fausse : $2\times 2 - (-3) = 4 + 3 = 7$ ; tu as oublié que soustraire un nombre négatif revient à l'ajouter.
- **c)** Ce sont les coordonnées du vecteur $\overrightarrow{AO}$ (arrivée moins départ) ; elles ne donnent pas la position de $A'$.
- **d)** Ce sont les coordonnées du milieu de $[AO]$ ; or c'est $O$ qui doit être le milieu de $[AA']$.


</details>

Avis : 

---

## 38. `cqc-reciproque-du-theoreme-de-thales-faible-1` (séries BEPC)

**Remarque du relecteur :** La justification c) omet de citer la position des points (E sur [AB], F sur [AC], même ordre), condition de la réciproque de Thalès ; acceptable car donnée dans l'énoncé.

**Énoncé :**

$ABC$ est un triangle. $E$ est un point du segment $[AB]$ tel que $AE = 3$ cm et $AB = 8$ cm. $F$ est un point du segment $[AC]$ tel que $AF = 6$ cm et $AC = 16$ cm.

Les droites $(EF)$ et $(BC)$ sont-elles parallèles ? Quelle est la conclusion correctement justifiée ?

- a) Non, car $\dfrac{3}{8}$ et $\dfrac{6}{16}$ ont des numérateurs et des dénominateurs différents
- b) Non, car $AE \neq AF$
- c) Oui, car $\dfrac{AE}{AB} = \dfrac{3}{8}$ et $\dfrac{AF}{AC} = \dfrac{6}{16} = \dfrac{3}{8}$
- d) On ne peut pas conclure, car la longueur $BC$ n'est pas donnée

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

La réciproque du théorème de Thalès : si $E$ appartient à $[AB]$, $F$ appartient à $[AC]$, et si $\dfrac{AE}{AB} = \dfrac{AF}{AC}$, alors les droites $(EF)$ et $(BC)$ sont parallèles. Les deux rapports doivent impérativement être formés à partir du même sommet, ici $A$.

### Corrigé

*Premier rapport.*

$$\frac{AE}{AB} = \frac{3}{8}$$

*Second rapport.*

$$\frac{AF}{AC} = \frac{6}{16} = \frac{6 \div 2}{16 \div 2} = \frac{3}{8}$$

*Comparaison.*

$$\frac{AE}{AB} = \frac{AF}{AC} = \frac{3}{8}$$

De plus, $E$ appartient à $[AB]$ et $F$ appartient à $[AC]$ : les points $A$, $E$, $B$ d'une part et $A$, $F$, $C$ d'autre part sont alignés dans le même ordre à partir de $A$.

D'après la réciproque du théorème de Thalès, les droites $(EF)$ et $(BC)$ sont **parallèles**.

### Pourquoi les autres réponses sont fausses

- **a)** Deux fractions peuvent avoir des écritures différentes et être égales : $\dfrac{6}{16}$ se simplifie par $2$ en $\dfrac{3}{8}$.
- **b)** On ne compare pas des longueurs directement : ce sont les rapports $\dfrac{AE}{AB}$ et $\dfrac{AF}{AC}$ qui doivent être égaux.
- **d)** La réciproque du théorème de Thalès n'utilise pas $BC$ : il suffit de comparer les rapports sur les côtés $[AB]$ et $[AC]$.


</details>

Avis : 

---

## 39. `cqc-reduction-faible-1` (séries BEPC)

**Énoncé :**

Une pyramide de volume $V = 250\ \text{cm}^{3}$ est réduite dans le rapport $k = \dfrac{2}{5}$. Quel est le volume $v$ de la pyramide réduite ?

- a) $16\ \text{cm}^{3}$
- b) $100\ \text{cm}^{3}$
- c) $40\ \text{cm}^{3}$
- d) $12\ \text{cm}^{3}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans une réduction de rapport $k$, le volume du solide réduit s'obtient en multipliant le volume initial par $k^{3}$ : $v = k^{3}\times V$.

### Corrigé

*Calcul de $k^{3}$.*

$$k^{3} = \left(\frac{2}{5}\right)^{3} = \frac{2^{3}}{5^{3}} = \frac{8}{125}$$

*Volume réduit.*

$$v = \frac{8}{125}\times 250 = \frac{8\times 250}{125} = \frac{2\,000}{125}$$

$$v = 16\ \text{cm}^{3}$$

Le volume de la pyramide réduite est donc $v = 16\ \text{cm}^{3}$.

*Contrôle.* $250 \div 125 = 2$, puis $2\times 8 = 16$ : le calcul est cohérent.

### Conseil

Quand le rapport $k$ est une fraction, il est souvent plus simple de simplifier $\dfrac{V}{125}$ d'abord (ici $250\div 125 = 2$), puis de multiplier par le numérateur au cube : cela évite de manipuler de grands nombres.

### Pourquoi les autres réponses sont fausses

- **b)** Tu as multiplié le volume par $k$ seulement ; pour un volume, il faut multiplier par $k^{3}$.
- **c)** Tu as multiplié par $k^{2}=\dfrac{4}{25}$, le coefficient des aires, et non par $k^{3}$.
- **d)** Tu as calculé $k^{3}$ comme $\dfrac{2\times 3}{5^{3}}$ : élever $2$ au cube donne $8$, et non $2\times 3 = 6$.


</details>

Avis : 

---

## 40. `cqc-signe-d-une-expression-moyenne-2` (séries BEPC)

**Remarque du relecteur :** LIMITE : valeur absolue d'une expression avec radical, haut du programme de 3e.

**Énoncé :**

Quelle est l'écriture de $\left|5\sqrt{2} - 7\right|$ sans valeur absolue ? On ne demande aucune valeur approchée.

- a) $7 - 5\sqrt{2}$
- b) $5\sqrt{2} + 7$
- c) $5\sqrt{2} - 7$
- d) $2\sqrt{2}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Lever une valeur absolue exige de connaître au préalable le signe de l'expression qu'elle contient : si l'expression est positive, sa valeur absolue lui est égale ; si elle est négative, sa valeur absolue est son opposé. On détermine ce signe en comparant les carrés des deux termes, lorsqu'ils sont tous deux positifs.

### Corrigé

*Détermination du signe de $5\sqrt{2}-7$.* On compare $5\sqrt{2}$ et $7$, tous deux positifs, par leurs carrés :

$$(5\sqrt{2})^{2} = 25 \times 2 = 50 \qquad \qquad 7^{2} = 49$$

$50 > 49$, donc $5\sqrt{2} > 7$, c'est-à-dire

$$5\sqrt{2} - 7 > 0$$

*Levée de la valeur absolue.* L'expression $5\sqrt{2}-7$ étant positive, sa valeur absolue lui est égale :

$$\left|5\sqrt{2}-7\right| = 5\sqrt{2}-7$$

L'égalité $\left|5\sqrt{2}-7\right| = 7-5\sqrt{2}$ est donc **fausse** : $7-5\sqrt{2}$ est négatif et ne peut pas être égal à une valeur absolue, qui est toujours positive ou nulle.

*Contrôle numérique.* $5\sqrt{2}\approx7{,}071$, donc $5\sqrt{2}-7\approx0{,}071$ et $7-5\sqrt{2}\approx-0{,}071$ : seul le premier nombre, positif, peut être une valeur absolue.

### Pourquoi les autres réponses sont fausses

- **a)** C'est l'opposé de la bonne réponse : on a changé le signe alors que $5\sqrt{2}-7$ est déjà positif ($50>49$) ; $7-5\sqrt{2}$ est négatif et ne peut pas être une valeur absolue.
- **b)** La valeur absolue ne change pas un signe $-$ en signe $+$ au milieu de l'expression : elle laisse l'expression telle quelle si elle est positive.
- **d)** $5\sqrt{2}$ et $7$ ne sont pas des termes semblables : on ne peut pas les regrouper comme $(5-7)\sqrt{2}$.


</details>

Avis : 

---

## 41. `cqc-sinus-elevee-1` (séries BEPC)

**Remarque du relecteur :** Le cosinus donné est inutile (distracteur classique, acceptable).

**Énoncé :**

Un mât vertical de voilier est maintenu par un hauban (câble tendu) de $5$ m de longueur, fixé au sommet du mât et ancré sur le pont. Le hauban fait un angle de $65^\circ$ avec le pont, supposé horizontal. On donne $\sin 65^\circ \approx 0{,}906$ et $\cos 65^\circ \approx 0{,}423$.

Quelle est la hauteur du mât, arrondie au centième de mètre ?

- a) $2{,}12$ m
- b) $4{,}53$ m
- c) $5{,}52$ m
- d) $11{,}82$ m

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Le mât, le pont et le hauban forment un triangle rectangle dont le hauban est l'hypoténuse. La hauteur du mât est le côté opposé à l'angle de $65^\circ$ : $\sin\alpha = \dfrac{\text{opposé}}{\text{hypoténuse}}$.

### Corrigé

Le triangle formé par le pied du mât, le sommet du mât et le point d'ancrage est rectangle au pied du mât. Le hauban, de longueur $5$ m, est l'hypoténuse.

Hauteur du mât (côté opposé à l'angle de $65^\circ$) :

$$h = 5 \times \sin 65^\circ = 5 \times 0{,}906$$

$$h \approx 4{,}53\ \text{m}$$

*Contrôle.* La distance du pied du mât au point d'ancrage est $d = 5 \times \cos 65^\circ \approx 2{,}115$ m, et $h^{2} + d^{2} \approx 20{,}52 + 4{,}47 \approx 24{,}99$, quasiment égal à $5^{2} = 25$ (l'écart vient des arrondis) : le résultat est cohérent.

### Pourquoi les autres réponses sont fausses

- **a)** Tu as utilisé le cosinus ($5\times 0{,}423$) : c'est la distance entre le pied du mât et l'ancrage, côté adjacent à l'angle.
- **c)** Tu as divisé $5$ par $0{,}906$ ; la hauteur est le côté opposé, on multiplie l'hypoténuse par le sinus (et la hauteur ne peut pas dépasser la longueur du hauban).
- **d)** Tu as divisé $5$ par $0{,}423$ en utilisant le cosinus ; la hauteur se calcule avec le sinus, par multiplication, et ne peut pas dépasser $5$ m.


</details>

Avis : 

---

## 42. `cqc-sinus-moyenne-2` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : le contexte de la voile est décoratif et flou (quel angle ?), une formulation directe suffit.

**Énoncé :**

Un angle aigu $\theta$ est tel que $\cos \theta = 0{,}8$. Quelle est la valeur de $\sin \theta$ ?

- a) $0{,}2$
- b) $0{,}36$
- c) $0{,}6$
- d) $0{,}64$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour tout angle aigu, la relation fondamentale $\cos^{2}\theta + \sin^{2}\theta = 1$ permet de retrouver l'un des deux rapports à partir de l'autre, en n'oubliant pas qu'un sinus d'angle aigu est toujours positif.

### Corrigé

$$\cos^{2}\theta + \sin^{2}\theta = 1$$

$$\sin^{2}\theta = 1 - \cos^{2}\theta = 1 - 0{,}8^{2} = 1 - 0{,}64 = 0{,}36$$

$$\sin\theta = \sqrt{0{,}36} = 0{,}6$$

(on prend la racine positive car $\theta$ est un angle aigu, donc $\sin\theta > 0$)

*Contrôle.* $\cos^{2}\theta + \sin^{2}\theta = 0{,}64 + 0{,}36 = 1$.

### Pourquoi les autres réponses sont fausses

- **a)** Tu as calculé $1-0{,}8$ ; la relation porte sur les carrés : $\sin^{2}\theta = 1-\cos^{2}\theta$.
- **b)** C'est la valeur de $\sin^{2}\theta$ ; il faut encore prendre la racine carrée pour obtenir $\sin\theta$.
- **d)** C'est la valeur de $\cos^{2}\theta$ ; tu as calculé $0{,}8^{2}$ sans l'utiliser pour trouver $\sin\theta$.


</details>

Avis : 

---

## 43. `cqc-sinus-moyenne-3` (séries BEPC)

**Remarque du relecteur :** La donnée « sin 30° = 0,5 » est inutile au calcul ; préciser que les 2 m sont mesurés dans le sens de la pente.

**Énoncé :**

Un panneau solaire rectangulaire, dont la longueur de $2$ m est mesurée le long de la pente, est fixé sur un toit et incliné d'un angle $\alpha$ par rapport à l'horizontale, tel que $\sin \alpha = 0{,}5$. On sait que $\sin 30^\circ = 0{,}5$.

Quelle hauteur le bord supérieur du panneau atteint-il au-dessus du bord inférieur ?

- a) $4$ m
- b) $1$ m
- c) $2{,}5$ m
- d) $0{,}25$ m

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Les valeurs remarquables du sinus (pour $30^\circ$, $45^\circ$, $60^\circ$) sont à connaître par cœur. Une fois l'angle identifié, la hauteur atteinte par un côté incliné de longueur $L$ s'obtient par $h = L \times \sin \alpha$.

### Corrigé

$\sin \alpha = 0{,}5 = \sin 30^\circ$, donc $\alpha = 30^\circ$.

Le panneau, sa hauteur verticale et sa projection horizontale forment un triangle rectangle où le panneau (longueur $2$ m) est l'hypoténuse et la hauteur cherchée est le côté opposé à $\alpha$.

$$h = L \times \sin \alpha = 2 \times \sin 30^\circ = 2 \times 0{,}5$$

$$h = 1\ \text{m}$$

*Contrôle de vraisemblance.* La hauteur ($1$ m) est bien inférieure à la longueur du panneau ($2$ m), comme il se doit pour un côté opposé face à l'hypoténuse.

### Pourquoi les autres réponses sont fausses

- **a)** Tu as divisé $2$ par $0{,}5$ ; la hauteur se calcule en multipliant l'hypoténuse par le sinus, et elle ne peut pas dépasser la longueur du panneau.
- **c)** Tu as additionné $2$ et $0{,}5$ ; le sinus est un rapport, la hauteur se calcule par $2\times 0{,}5$.
- **d)** Tu as divisé $0{,}5$ par $2$ ; il faut multiplier la longueur du panneau par le sinus de l'angle.


</details>

Avis : 

---

## 44. `cqc-solide-compose-moyenne-0` (séries BEPC)

**Énoncé :**

Un artisan fabrique un socle de trophée sportif. La base du socle est un bloc rectangulaire plein de $12$ cm de longueur, $12$ cm de largeur et $4$ cm d'épaisseur. Sur le centre de la face supérieure de ce bloc repose, bien centrée et verticale, une colonne pleine à section circulaire, de rayon $3$ cm et de hauteur $15$ cm, sur laquelle sera fixée la coupe du trophée.

On prendra $\pi \approx 3{,}14$.

Quel est le volume total du socle, en cm³ ?

- a) $999{,}9$ cm³
- b) $2271{,}6$ cm³
- c) $717{,}3$ cm³
- d) $858{,}6$ cm³

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour un solide composé décrit uniquement par un texte, on repère d'abord les solides usuels qui le composent (forme de la base, section constante ou non), on choisit la formule de volume de chacun, puis on additionne les volumes puisque le solide est obtenu par assemblage.

### Corrigé

Le bloc rectangulaire plein est un **pavé droit** ; la colonne pleine à section circulaire est un **cylindre de révolution**. Le socle est la réunion des deux.

Volume du pavé droit :
$$V_{pave} = 12\times 12\times 4 = 576\ \text{cm}^3$$

Volume du cylindre :
$$V_{cyl} = \pi\times 3^2\times 15 = 3{,}14\times 9\times 15 = 423{,}9\ \text{cm}^3$$

Volume total :
$$V_{total} = 576+423{,}9 = 999{,}9\ \text{cm}^3$$

Le socle a donc un volume total de $999{,}9$ cm³.

### Pourquoi les autres réponses sont fausses

- **b)** Le diamètre ($6$ cm) a été utilisé à la place du rayon ($3$ cm) dans la formule du volume du cylindre.
- **c)** Le rayon n'a pas été élevé au carré dans le volume du cylindre ($\pi\times 3\times 15$ au lieu de $\pi\times 3^2\times 15$).
- **d)** L'aire latérale du cylindre ($2\pi r h$) a été utilisée à la place de son volume ($\pi r^2 h$).

</details>

Avis : 

---

## 45. `cqc-solides-semblables-moyenne-3` (séries BEPC)

**Remarque du relecteur :** LIMITE : effet d'une réduction sur les volumes (k^3) et racine cubique de 27/64, haut du programme de 3e.

**Énoncé :**

Un chocolatier utilise un moule conique, pointe vers le bas, de hauteur totale $20$ cm, pour fabriquer une décoration en chocolat. Il remplit le moule à ras bord de chocolat fondu, puis retire délicatement du chocolat par le haut jusqu'à ce qu'il n'en reste plus que $\dfrac{27}{64}$ du volume initial. Le chocolat restant occupe alors, au fond du moule, un volume ayant la forme d'un cône semblable au moule entier (même sommet, pointe en bas).

Quelle est la hauteur du chocolat restant, mesurée depuis la pointe du moule ?

- a) $8{,}4375$ cm
- b) $15$ cm
- c) $11{,}25$ cm
- d) $5$ cm

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Si le rapport entre deux volumes de solides semblables est connu, on retrouve le rapport de réduction des longueurs $k$ en cherchant le nombre dont le cube est ce rapport de volumes, puisque $V_{petit} = k^3 \times V_{grand}$. Ici, on repère les cubes $27 = 3^3$ et $64 = 4^3$.

### Corrigé

$k^3 = \dfrac{27}{64}$. Or $27 = 3^3$ et $64 = 4^3$, donc $k^3 = \left(\dfrac{3}{4}\right)^3$ et $k = \dfrac{3}{4}$.

Le cône de chocolat restant a même sommet (la pointe) que le moule entier, donc sa hauteur depuis la pointe est :

$h_{restant} = k \times h_{moule} = \dfrac{3}{4} \times 20 = 15$ cm

Le chocolat restant atteint une hauteur de **15 cm** depuis la pointe du moule.

### Pourquoi les autres réponses sont fausses

- **a)** La hauteur a été obtenue en multipliant par le rapport des volumes $\dfrac{27}{64}$ au lieu du rapport des longueurs $k$.
- **c)** Le rapport $\dfrac{9}{16}$ ($k^2$) a été utilisé à la place de $k$.
- **d)** On a calculé la hauteur de chocolat retirée ($20 \times (1-k)$) au lieu de la hauteur restante.

</details>

Avis : 

---

## 46. `cqc-symetrie-orthogonale-faible-1` (séries BEPC)

**Remarque du relecteur :** Le cercle et le rayon sont des données inutiles, mais elles servent de distracteur légitime.

**Énoncé :**

Un cercle $(C)$ a pour centre $O$ et pour rayon $4$ cm. Un point $M$ appartient à $(C)$ : on a donc $OM = 4$ cm. On considère la symétrie orthogonale d'axe la droite $(OM)$.

Quel est le symétrique du point $M$ par cette symétrie ?

- a) Le point diamétralement opposé à $M$ sur le cercle $(C)$
- b) Le centre $O$ du cercle
- c) Le point $M$ lui-même
- d) Un autre point du cercle $(C)$, distinct de $M$ et situé hors de la droite $(OM)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

La droite $(OM)$ passe par le centre $O$ du cercle : c'est donc un axe de symétrie de $(C)$. Une symétrie orthogonale laisse invariant tout point situé sur son axe : un tel point est son propre symétrique.

### Corrigé

Le point $M$ appartient à la droite $(OM)$, qui est précisément l'axe de la symétrie considérée. Un point situé sur l'axe d'une symétrie orthogonale est invariant : son image est lui-même.

Le symétrique de $M$ par cette symétrie est donc **$M$ lui-même**.

*Remarque.* Tous les points de la droite $(OM)$, y compris $O$ et le point diamétralement opposé à $M$ sur $(C)$, sont eux aussi invariants.

### Pourquoi les autres réponses sont fausses

- **a)** C'est l'image de $M$ par la symétrie centrale de centre $O$, pas par la symétrie orthogonale d'axe $(OM)$.
- **b)** On a confondu symétrique d'un point et milieu : $O$ est invariant lui aussi, mais il est différent de $M$ ($OM = 4$ cm).
- **d)** Ce point n'est pas sur l'axe : l'axe $(OM)$ contient $M$, qui reste donc à sa place.

</details>

Avis : 

---

## 47. `cqc-theoreme-des-milieux-faible-0` (séries BEPC)

**Énoncé :**

Dans un triangle $RST$, le point $M$ est le milieu du segment $[RS]$ et le point $N$ est le milieu du segment $[RT]$. On donne $ST = 7{,}4$ cm.

Quelle est la longueur $MN$ ?

- a) $3{,}7$ cm
- b) $14{,}8$ cm
- c) $7{,}4$ cm
- d) $1{,}85$ cm

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un triangle, si un point est le milieu d'un côté et qu'un second point est le milieu d'un deuxième côté, alors le segment qui les joint est parallèle au troisième côté et sa longueur est égale à la moitié de celle du troisième côté (théorème des milieux).

### Corrigé

Dans le triangle $RST$, $M$ est le milieu de $[RS]$ et $N$ est le milieu de $[RT]$. D'après le théorème des milieux, $(MN) \parallel (ST)$ et :
$$MN = \frac{ST}{2} = \frac{7{,}4}{2} = 3{,}7 \text{ cm}$$

La longueur $MN$ est donc égale à $3{,}7$ cm.

### Pourquoi les autres réponses sont fausses

- **b)** La longueur $ST$ a été doublée au lieu d'être divisée par $2$.
- **c)** On a pris $MN = ST$ : le segment qui joint les milieux est parallèle à $[ST]$ mais deux fois plus court.
- **d)** La longueur a été divisée par $4$ au lieu de $2$.

</details>

Avis : 

---

## 48. `cqc-trapeze-rectangle-elevee-0` (séries BEPC)

**Remarque du relecteur :** La construction du point T ne sert pas au calcul (donnée superflue mais non trompeuse).

**Énoncé :**

Un jardin a la forme d'un trapèze rectangle $UVWZ$, dont les côtés $[UV]$ et $[ZW]$ sont parallèles, avec des angles droits en $U$ et en $Z$. On sait que $UZ = 12$ m (la hauteur du trapèze), que la petite base $ZW = 20$ m, et que l'aire totale du jardin est de $354$ m². On abaisse la perpendiculaire à $(UV)$ issue du point $W$ ; elle coupe $(UV)$ en un point $T$.

Quelle est la longueur de la grande base $UV$ ?

- a) $29{,}5$ m
- b) $19$ m
- c) $39$ m
- d) $59$ m

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un trapèze rectangle, la perpendiculaire abaissée du sommet de la petite base sur la grande base le décompose en un rectangle et un triangle rectangle accolés. L'aire totale est la somme de ces deux aires : connaître l'aire totale et celle du rectangle donne l'aire du triangle, puis, avec la formule de l'aire du triangle, une longueur inconnue.

### Corrigé

Le quadrilatère $UTWZ$ a trois angles droits (en $U$, en $Z$ et en $T$) : c'est un **rectangle**, avec $UT = ZW = 20$ m et $TW = UZ = 12$ m.

$$\text{Aire}(UTWZ) = 20 \times 12 = 240 \text{ m}^2$$

$$\text{Aire}(TVW) = 354 - 240 = 114 \text{ m}^2$$

Le triangle $TVW$ est rectangle en $T$ : $\dfrac{TV \times TW}{2} = 114$, donc $TV \times 6 = 114$ et $TV = 19$ m.

$$UV = UT + TV = 20 + 19 = 39 \text{ m}$$

*Contrôle par la formule de l'aire du trapèze.*
$$\mathcal{A} = \frac{(39 + 20) \times 12}{2} = \frac{708}{2} = 354 \text{ m}^2$$

### Pourquoi les autres réponses sont fausses

- **a)** Dans l'aire du triangle, le facteur $\dfrac{1}{2}$ a été oublié ($TV = 114 \div 12 = 9{,}5$ m).
- **b)** On a donné la longueur $TV$ et oublié d'y ajouter $UT = 20$ m pour obtenir $UV$.
- **d)** C'est la somme des deux bases ($UV + ZW$, issue de la formule de l'aire) : on a oublié de retrancher $ZW = 20$ m.

</details>

Avis : 

---

## 49. `cqc-vecteur-directeur-faible-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : lien coefficient directeur / vecteur directeur, à vérifier selon le programme de 3e retenu.

**Énoncé :**

La droite $(D)$ a pour équation $y = 5x - 2$.

Quel est un vecteur directeur de $(D)$ ?

- a) $\vec{u}\,(5\,;\,1)$
- b) $\vec{u}\,(1\,;\,-2)$
- c) $\vec{u}\,(-5\,;\,1)$
- d) $\vec{u}\,(1\,;\,5)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une droite d'équation $y = ax + b$, le vecteur $\vec{u}\,(1\,;\,a)$ est un vecteur directeur de cette droite : en avançant de $1$ en abscisse, on avance de $a$ en ordonnée.

### Corrigé

Le coefficient directeur de $(D)$ est $a = 5$. Un vecteur directeur de $(D)$ est donc

$$\vec{u}\,(1\,;\,5)$$

*Vérification.* Le point $A(0\,;\,-2)$ appartient à $(D)$. Le point $B = A + \vec{u}$ a pour coordonnées $(1\,;\,3)$ et $5 \times 1 - 2 = 3$, donc $B$ appartient aussi à $(D)$.

### Pourquoi les autres réponses sont fausses

- **a)** Les deux coordonnées ont été permutées : le coefficient directeur $5$ est l'ordonnée du vecteur $(1\,;\,5)$, pas son abscisse.
- **b)** On a utilisé l'ordonnée à l'origine $-2$ à la place du coefficient directeur $5$.
- **c)** Ce vecteur dirige une droite de coefficient directeur $-\dfrac{1}{5}$, pas $5$.

</details>

Avis : 

---

## 50. `cqc-vecteur-directeur-moyenne-1` (séries BEPC)

**Remarque du relecteur :** LIMITE : vecteur directeur d'une droite, à vérifier selon le programme de 3e retenu.

**Énoncé :**

La droite $(D)$ a pour équation $x = 5$ (droite verticale, parallèle à l'axe des ordonnées).

Lequel de ces vecteurs est un vecteur directeur de $(D)$ ?

- a) $\vec{u}\,(3\,;\,0)$
- b) $\vec{u}\,(5\,;\,0)$
- c) $\vec{u}\,(0\,;\,3)$
- d) $\vec{u}\,(1\,;\,5)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Le coefficient directeur d'une droite d'équation $y = ax+b$ n'est défini que si la droite n'est pas verticale : le rapport de la variation des ordonnées par la variation des abscisses n'a pas de sens quand la variation des abscisses est nulle. Une droite verticale n'a donc pas de coefficient directeur, mais elle possède tout de même des vecteurs directeurs, que l'on obtient à partir des coordonnées de deux de ses points.

### Corrigé

Tous les points de $(D)$ ont pour abscisse $5$, quelle que soit leur ordonnée. Deux points de $(D)$ sont par exemple $P(5\,;\,0)$ et $Q(5\,;\,3)$ :

$$\vec{PQ}\,(5-5\,;\,3-0) = (0\,;\,3)$$

Un vecteur directeur de $(D)$ a donc une abscisse nulle et une ordonnée non nulle : $\vec{u}\,(0\,;\,3)$ convient.

*Vérification.* En partant de $P(5\,;\,0)$ et en ajoutant $\vec{u}$, on obtient le point $(5\,;\,3)$, qui appartient bien à $(D)$ (son abscisse est $5$).

### Pourquoi les autres réponses sont fausses

- **a)** Ce vecteur est horizontal : il dirige une droite parallèle à l'axe des abscisses, d'équation du type $y = k$.
- **b)** On a repris le nombre $5$ de l'équation comme abscisse, mais ce vecteur est horizontal, donc il ne dirige pas une droite verticale.
- **d)** Ce vecteur a un coefficient directeur égal à $5$ : il dirige une droite oblique, pas la droite verticale $x = 5$.

</details>

Avis : 

---

## 51. `cqc-volume-d-un-cylindre-faible-0` (séries BEPC)

**Remarque du relecteur :** « arrondie au centième » superflu : avec π=3,14 la valeur est exacte au centième.

**Énoncé :**

Une boîte de conserve a la forme d'un cylindre de révolution. Son rayon de base mesure $R = 4$ cm et sa hauteur mesure $h = 11$ cm.

Quelle est la valeur approchée de son volume, en cm³, ? (On prendra $\pi \approx 3{,}14$.)

- a) $552{,}64$ cm³
- b) $138{,}16$ cm³
- c) $276{,}32$ cm³
- d) $184{,}21$ cm³

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Le volume d'un cylindre de révolution de rayon de base $R$ et de hauteur $h$ se calcule par la formule $V = \pi R^2 h$ : on multiplie l'aire du disque de base, $\pi R^2$, par la hauteur $h$.

### Corrigé

$$V = \pi R^2 h = \pi\times 4^2\times 11 = \pi\times 16\times 11 = 176\pi$$

Le volume de la boîte de conserve est donc $176\pi$ cm³.

Avec $\pi \approx 3{,}14$ :
$$V \approx 176\times 3{,}14 = 552{,}64$$

Le volume approché de la boîte de conserve est donc environ $552{,}64$ cm³.

### Pourquoi les autres réponses sont fausses

- **b)** On a multiplié par $R = 4$ au lieu de $R^2 = 16$ : le rayon n'a pas été élevé au carré.
- **c)** On a calculé $R^2$ comme $2R = 8$ au lieu de $4\times 4 = 16$.
- **d)** On a divisé par $3$, ce qui est la formule du volume d'une pyramide ou d'un cône, pas celle d'un cylindre.

</details>

Avis : 

---

## 52. `cqc-volume-d-un-cylindre-moyenne-3` (séries BEPC)

**Énoncé :**

Une citerne cylindrique doit avoir un volume de $6{,}28$ m³. Son rayon de base est fixé à $1$ m.

Quelle doit être la hauteur de cette citerne, en mètres ? (On prendra $\pi \approx 3{,}14$.)

- a) $1$ m
- b) $6$ m
- c) $2$ m
- d) $19{,}72$ m

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand le volume $V$ et le rayon de base $R$ d'un cylindre sont connus, on retrouve la hauteur $h$ en isolant $h$ dans la formule $V = \pi R^2 h$, ce qui donne $h = \dfrac{V}{\pi R^2}$.

### Corrigé

Avec $V = 6{,}28$ m³ et $R = 1$ m, donc $R^2 = 1$ :

$$h = \frac{V}{\pi R^2} = \frac{6{,}28}{\pi\times 1} = \frac{6{,}28}{\pi}$$

Avec $\pi \approx 3{,}14$ :
$$h \approx \frac{6{,}28}{3{,}14} = 2$$

La citerne doit donc avoir une hauteur de $2$ m.

### Pourquoi les autres réponses sont fausses

- **a)** On a divisé par $2\pi R$ (périmètre du cercle de base) au lieu de $\pi R^2$ (aire du disque de base).
- **b)** On a multiplié par $3$ avant de diviser, comme dans la formule d'un volume de pyramide ou de cône, qui ne s'applique pas à un cylindre.
- **d)** On a multiplié le volume par $\pi$ au lieu de le diviser.

</details>

Avis : 

---

## 53. `cqc-equation-reduite-elevee-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : droites données sous la forme ax − y + c = 0 avec paramètre m ; l'élève de 3e doit d'abord se ramener à y = ax + b.

**Énoncé :**

On considère la droite $(D)$ d'équation $5x - y + 1 = 0$ et la droite $(D_m)$ d'équation $mx - y + 7 = 0$, où $m$ est un nombre réel.

Pour quelle valeur de $m$ les droites $(D)$ et $(D_m)$ sont-elles parallèles ?

- a) $m = -5$
- b) $m = \dfrac{1}{5}$
- c) $m = 7$
- d) $m = 5$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour déterminer une équation réduite contenant un paramètre, on isole $y$ comme dans le cas général : le coefficient directeur s'exprime alors en fonction du paramètre. La condition de parallélisme entre deux droites (coefficients directeurs égaux) devient une équation vérifiée par ce paramètre.

### Corrigé

*Équation réduite de $(D)$.*

$$5x - y + 1 = 0 \quad \Longleftrightarrow \quad y = 5x + 1$$

Le coefficient directeur de $(D)$ est $5$.

*Équation réduite de $(D_m)$.*

$$mx - y + 7 = 0 \quad \Longleftrightarrow \quad y = mx + 7$$

Le coefficient directeur de $(D_m)$ est $m$.

*Condition de parallélisme.* $(D)$ et $(D_m)$ sont parallèles lorsque leurs coefficients directeurs sont égaux :

$$m = 5$$

Pour $m=5$, l'équation réduite de $(D_m)$ devient $y = 5x + 7$. Son ordonnée à l'origine est $7$, alors que celle de $(D)$ est $1$ : les deux droites sont parallèles mais distinctes.

*Conclusion.* $m = 5$.

### Pourquoi les autres réponses sont fausses

- **a)** Une erreur de signe a été faite en isolant $y$ : on a écrit $y = -5x - 1$, alors que $5x - y + 1 = 0$ donne $y = 5x + 1$.
- **b)** On a pris l'inverse du coefficient directeur de $(D)$ ; deux droites parallèles ont des coefficients directeurs égaux, non inverses.
- **c)** On a repris l'ordonnée à l'origine $7$ de $(D_m)$ au lieu de comparer les coefficients directeurs.

</details>

Avis : 

---

## 54. `cqc-equation-reduite-faible-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : équations de droites données sous la forme ax+by+c = 0 ; à vérifier que cette écriture figure dans le manuel de 3e utilisé (sinon donner directement y = ax+b).

**Énoncé :**

On considère les droites $(D_1)$ et $(D_2)$ d'équations respectives $3x - y + 5 = 0$ et $3x - y - 2 = 0$.

Laquelle de ces affirmations est exacte ?

- a) $(D_1) : y = 3x + 5$ et $(D_2) : y = 3x - 2$ ; les deux droites sont parallèles.
- b) $(D_1) : y = 3x + 5$ et $(D_2) : y = 3x - 2$ ; les deux droites ne sont pas parallèles.
- c) $(D_1) : y = -3x - 5$ et $(D_2) : y = -3x + 2$ ; les deux droites sont parallèles.
- d) $(D_1) : y = 3x + 5$ et $(D_2) : y = -3x - 2$ ; les deux droites ne sont pas parallèles.

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

L'équation réduite d'une droite non parallèle à l'axe des ordonnées s'écrit sous la forme $y = ax + b$, où $a$ est le coefficient directeur. On l'obtient à partir d'une équation de la forme $ax + by + c = 0$ en isolant $y$. Deux droites sont parallèles si et seulement si elles ont le même coefficient directeur.

### Corrigé

*Équation réduite de $(D_1)$.*

$$3x - y + 5 = 0 \quad \Longleftrightarrow \quad y = 3x + 5$$

$$a_1 = 3$$

*Équation réduite de $(D_2)$.*

$$3x - y - 2 = 0 \quad \Longleftrightarrow \quad y = 3x - 2$$

$$a_2 = 3$$

*Conclusion.*

$$a_1 = a_2 = 3$$

Les droites $(D_1)$ et $(D_2)$ ont le même coefficient directeur : elles sont donc **parallèles**. Elles sont de plus distinctes, puisque leurs ordonnées à l'origine diffèrent ($5$ et $-2$).

### Pourquoi les autres réponses sont fausses

- **b)** Les équations réduites sont justes, mais la conclusion est fausse : les ordonnées à l'origine différentes n'empêchent pas le parallélisme, seuls comptent les coefficients directeurs, ici égaux.
- **c)** Le signe des coefficients est faux : en passant $3x$ de l'autre côté il reste $-y = -3x - 5$, d'où $y = 3x + 5$, pas $-3x - 5$.
- **d)** Le coefficient directeur de $(D_2)$ est faux : $3x - y - 2 = 0$ donne $y = 3x - 2$, et non $y = -3x - 2$.

</details>

Avis : 

---

## 55. `cqc-equation-reduite-moyenne-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : équations sous la forme ax + by + c = 0, à ramener à y = ax + b.

**Énoncé :**

On donne trois droites : $(D_1) : 4x - 2y + 6 = 0$ ; $(D_2) : x - 2y + 8 = 0$ ; $(D_3) : 2x - y - 3 = 0$.

Lesquelles de ces droites sont parallèles entre elles ?

- a) $(D_1)$ et $(D_2)$ seulement
- b) $(D_1)$ et $(D_3)$ seulement
- c) $(D_2)$ et $(D_3)$ seulement
- d) aucune de ces droites n'est parallèle à une autre

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

L'équation réduite d'une droite s'obtient en isolant $y$, ce qui fait apparaître son coefficient directeur $a$. Deux droites sont parallèles si et seulement si elles ont le même coefficient directeur ; pour comparer plusieurs droites entre elles, on réduit donc chacune d'elles avant de comparer les coefficients obtenus deux à deux.

### Corrigé

*Équation réduite de $(D_1)$.*

$$4x - 2y + 6 = 0 \quad \Longleftrightarrow \quad -2y = -4x - 6 \quad \Longleftrightarrow \quad y = 2x + 3$$

$$a_1 = 2$$

*Équation réduite de $(D_2)$.*

$$x - 2y + 8 = 0 \quad \Longleftrightarrow \quad -2y = -x - 8 \quad \Longleftrightarrow \quad y = \frac{1}{2}x + 4$$

$$a_2 = \frac{1}{2}$$

*Équation réduite de $(D_3)$.*

$$2x - y - 3 = 0 \quad \Longleftrightarrow \quad -y = -2x + 3 \quad \Longleftrightarrow \quad y = 2x - 3$$

$$a_3 = 2$$

*Comparaison des coefficients directeurs.* $a_1 = a_3 = 2$, tandis que $a_2 = \dfrac{1}{2}$ est différent des deux autres.

*Conclusion.* Les droites $(D_1)$ et $(D_3)$ ont le même coefficient directeur : elles sont **parallèles entre elles** (et distinctes, puisque leurs ordonnées à l'origine diffèrent : $3$ et $-3$). La droite $(D_2)$, de coefficient directeur différent, n'est parallèle à aucune des deux autres.

### Pourquoi les autres réponses sont fausses

- **a)** Ces deux droites ont le même coefficient de $y$ ($-2$), mais ce sont les coefficients directeurs $2$ et $\dfrac{1}{2}$ qu'il faut comparer.
- **c)** On a mal isolé $y$ dans $(D_2)$ : $y = \dfrac{1}{2}x + 4$ a pour coefficient directeur $\dfrac{1}{2}$, pas $2$.
- **d)** Les équations n'ont pas été réduites : en isolant $y$, $(D_1)$ et $(D_3)$ ont toutes deux pour coefficient directeur $2$.

</details>

Avis : 

---


---

# Lot : b1-bepc-vague-5

## Vague 5 Maths BEPC (questions au thème renommé) : 19 QCM à faire relire par l'enseignant (campagne B1)

Date : 2026-11-01. Sur 69 QCM convertis (76 questions BEPC étudiées, 7 écartées), **19** vous sont soumis : ceux que le relecteur aveugle a assortis d'une remarque et un tirage de 10 autres. Le lot est prêt mais n'est pas en ligne tant que vous n'avez pas répondu. Les 69 résolutions à l'aveugle ont donné la clé ; six formulations ont été corrigées après la relecture.

## Points à trancher

1. **Rapport d'agrandissement ou de réduction et volumes** (`coefficient-moyenne-3`, k³ = 1/125) : limite haute de la 3e ?
2. **Questions faciles gardées** (`priorites-operatoires-faible-0` et `faible-1`) : on garde pour le piège d'ordre des opérations, ou on retire ?
3. **Questions écartées** parce que hors programme : `orthogonalite` (vecteur normal, équation cartésienne).

Pour chaque question : **OK**, **à corriger** (dire quoi) ou **à retirer**.

## 1. `cqc-aire-du-disque-elevee-0` (séries BEPC)

**Énoncé :**

La circonférence d'un disque métallique mesure $62{,}8$ cm (on prendra $\pi \approx 3{,}14$). Quelle est l'aire de ce disque, arrondie au cm² près (au plus proche) ?

- a) $1\,256$ cm²
- b) $628$ cm²
- c) $314$ cm²
- d) $197$ cm²

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand on connaît le périmètre (la circonférence) d'un disque plutôt que son rayon, on retrouve d'abord ce rayon à l'aide de la formule $C = 2\pi r$, avant de pouvoir appliquer la formule de l'aire $\mathcal{A} = \pi r^{2}$.

### Corrigé

*Étape 1 - retrouver le rayon à partir de la circonférence.*

$$C = 2\pi r \quad \Longrightarrow \quad r = \frac{C}{2\pi}$$

$$r = \frac{62{,}8}{2 \times 3{,}14} = \frac{62{,}8}{6{,}28}$$

$$r = 10 \text{ cm}$$

*Étape 2 - calculer l'aire du disque à partir de ce rayon.*

$$\mathcal{A} = \pi r^{2} = 3{,}14 \times 10^{2} = 3{,}14 \times 100$$

$$\mathcal{A} = 314 \text{ cm}^{2}$$

**Conclusion.** L'aire du disque est de $314$ cm² (le résultat est exact : l'arrondi au cm² près ne change rien).

**Vérification.** Avec ce rayon de $10$ cm, la circonférence vaut $2 \times 3{,}14 \times 10 = 62{,}8$ cm, exactement la valeur de l'énoncé.

**Piège évité.** Ne confonds pas la formule de la circonférence ($2\pi r$, une longueur) avec celle de l'aire ($\pi r^{2}$, une surface).

### Pourquoi les autres réponses sont fausses
- **a)** on trouve $r = 20$ cm en oubliant le $2$ de $2\pi r$ ($r = \dfrac{62{,}8}{3{,}14}$), puis $3{,}14 \times 20^{2} = 1\,256$.
- **b)** on utilise $2\pi r^{2}$, mélange des formules de la circonférence et de l'aire : $2 \times 3{,}14 \times 10^{2} = 628$.
- **d)** on multiplie directement la circonférence par $\pi$ sans passer par le rayon : $3{,}14 \times 62{,}8 \approx 197$.

</details>

Avis : 

---

## 2. `cqc-aire-du-disque-moyenne-1` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : un pâtissier ne vend pas en général de pizzas ; préférer « un pizzaiolo » ou « un restaurant ».

**Énoncé :**

Un pizzaiolo vend deux pizzas rondes : la petite a un rayon de $12$ cm, la grande a un rayon de $36$ cm, soit trois fois plus grand. Par quel nombre l'aire de la grande pizza est-elle multipliée par rapport à l'aire de la petite ?

- a) $3$
- b) $6$
- c) $9$
- d) $27$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Dans la formule $\mathcal{A} = \pi r^{2}$, l'aire dépend du CARRÉ du rayon. Si le rayon est multiplié par un nombre $k$, l'aire est donc multipliée par $k^{2}$, et non par $k$.

### Corrigé

*Raisonnement par le facteur d'échelle.* Le rayon de la grande pizza est $3$ fois celui de la petite ($36 = 3 \times 12$). L'aire d'un disque étant proportionnelle au carré du rayon, l'aire de la grande pizza est multipliée par $3^{2} = 9$ par rapport à celle de la petite.

*Vérification par le calcul direct des deux aires.*

$$\mathcal{A}_{1} = \pi \times 12^{2} = 144\pi \text{ cm}^{2} \qquad \mathcal{A}_{2} = \pi \times 36^{2} = 1\,296\pi \text{ cm}^{2}$$

$$\frac{\mathcal{A}_{2}}{\mathcal{A}_{1}} = \frac{1\,296\pi}{144\pi} = 9$$

**Conclusion.** L'aire de la grande pizza est $9$ fois celle de la petite : tripler le rayon multiplie l'aire par $3^{2} = 9$.

### Pourquoi les autres réponses sont fausses
- **a)** on pense que l'aire est multipliée comme le rayon, par $k = 3$, en oubliant que l'aire dépend du carré du rayon.
- **b)** on calcule $2 \times 3$ en confondant $k^{2}$ avec $2k$.
- **d)** on utilise $k^{3}$, règle des volumes, au lieu de $k^{2}$, règle des aires.

</details>

Avis : 

---

## 3. `cqc-valeur-numerique-faible-1` (séries BEPC)

**Énoncé :**

Quelle est la valeur numérique de l'expression $E = 3x^{2} - 5x + 1$ pour $x = -2$ ?

- a) $-1$
- b) $3$
- c) $47$
- d) $23$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Calculer la valeur numérique d'une expression littérale, c'est remplacer la lettre par le nombre donné, puis effectuer les calculs en respectant les priorités opératoires : d'abord les puissances, puis les multiplications, enfin les additions et soustractions.

### Corrigé
$$E = 3x^{2} - 5x + 1$$

On remplace $x$ par $-2$ :

$$E = 3 \times (-2)^{2} - 5 \times (-2) + 1$$

*Calcul du carré.*

$$(-2)^{2} = 4$$

*Calcul des produits.*

$$3 \times 4 = 12 \qquad \text{et} \qquad -5 \times (-2) = 10$$

*Somme finale.*

$$E = 12 + 10 + 1 = 23$$

$$E = 23$$

### Pourquoi les autres réponses sont fausses
- **a)** on calcule $(-2)^{2}$ comme $-4$, donc $3 \times (-4) = -12$, puis $-12 + 10 + 1 = -1$.
- **b)** on se trompe sur le signe de $-5 \times (-2)$ en écrivant $-10$ : $12 - 10 + 1 = 3$.
- **c)** on calcule $(3 \times (-2))^{2} = 36$ au lieu de $3 \times (-2)^{2}$ : $36 + 10 + 1 = 47$.

</details>

Avis : 

---

## 4. `cqc-valeur-numerique-moyenne-2` (séries BEPC)

**Énoncé :**

Quelle est la valeur numérique de $G = \sqrt{2x+3}$ pour $x = 11$ ?

- a) $5$
- b) $25$
- c) $\sqrt{22}+3$
- d) $12{,}5$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour calculer la valeur numérique d'une expression contenant une racine carrée, on calcule d'abord l'expression sous le radical, puis on en extrait la racine carrée si le résultat est un carré parfait.

### Corrigé
$$G = \sqrt{2x+3}$$

On remplace $x$ par $11$ :

$$G = \sqrt{2 \times 11 + 3} = \sqrt{22+3} = \sqrt{25}$$

$25$ est un carré parfait ($5^{2} = 25$), donc :

$$G = 5$$

### Pourquoi les autres réponses sont fausses
- **b)** on calcule $2 \times 11 + 3 = 25$ mais on oublie d'extraire la racine carrée.
- **c)** on applique la racine seulement à $2x$ et on laisse $+3$ à l'extérieur.
- **d)** on confond racine carrée et moitié : $\dfrac{25}{2} = 12{,}5$.

</details>

Avis : 

---

## 5. `cqc-longueur-moyenne-0` (séries BEPC)

**Remarque du relecteur :** AO et AT sont donnés sans être nécessaires (cohérents : 15/6 = 10/4) ; donnée inutile mais non trompeuse.

**Énoncé :**

Les droites $(ND)$ et $(OT)$ se coupent en $A$, avec $N$, $D$ de part et d'autre de $A$, et $O$, $T$ de part et d'autre de $A$ ; $(NO) \parallel (DT)$. On donne $AN = 4$ cm, $AD = 10$ cm, $AO = 6$ cm, $AT = 15$ cm, et $NO = 5{,}5$ cm.

Quelle est la longueur $DT$ ?

- a) $2{,}2$ cm
- b) $22$ cm
- c) $13{,}75$ cm
- d) $8{,}25$ cm

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans une configuration de Thalès en papillon, l'égalité des rapports s'étend au troisième côté, celui porté par les parallèles : $\dfrac{AN}{AD} = \dfrac{AO}{AT} = \dfrac{NO}{DT}$.

### Corrigé

D'après le théorème de Thalès :

$$\frac{AN}{AD} = \frac{NO}{DT}$$

$$\frac{4}{10} = \frac{5{,}5}{DT}$$

Par produit en croix :

$$4 \times DT = 10 \times 5{,}5 = 55$$

$$DT = \frac{55}{4} = 13{,}75 \text{ cm}$$

*Vérification par un second rapport.* On retrouve le même rapport avec $\dfrac{AO}{AT}$ :

$$\frac{AO}{AT} = \frac{6}{15} = 0{,}4 \qquad \text{et} \qquad \frac{AN}{AD} = \frac{4}{10} = 0{,}4$$

Les trois rapports valent bien $0{,}4$, car $\dfrac{NO}{DT} = \dfrac{5{,}5}{13{,}75} = 0{,}4$.

### Pourquoi les autres réponses sont fausses
- **a)** rapports inversés : $DT = 5{,}5 \times \dfrac{4}{10}$ au lieu de $5{,}5 \times \dfrac{10}{4}$.
- **b)** on multiplie $NO$ par $AN$ sans diviser par $AD$ : $4 \times 5{,}5 = 22$.
- **d)** on mélange deux rapports qui ne se correspondent pas : $5{,}5 \times \dfrac{15}{10}$.

</details>

Avis : 

---

## 6. `cqc-coefficient-moyenne-1` (séries BEPC)

**Énoncé :**

Une pyramide de hauteur $12$ cm est réduite par un plan parallèle à sa base. La pyramide réduite obtenue a une hauteur de $4$ cm.

Quel est le coefficient de réduction $k$ ?

- a) $3$
- b) $\dfrac{1}{3}$
- c) $8$
- d) $\dfrac{1}{4}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Le coefficient de réduction $k$ est le rapport entre une longueur de la petite figure et la longueur correspondante de la grande figure : $k = \dfrac{\text{longueur réduite}}{\text{longueur d'origine}}$.

### Corrigé

Les hauteurs étant des longueurs, elles sont dans le rapport $k$ :

$$k = \frac{4}{12} = \frac{1}{3}$$

Le coefficient de réduction vaut donc $k = \dfrac{1}{3}$.

### Pourquoi les autres réponses sont fausses
- **a)** rapport inversé : on divise la grande hauteur par la petite ($\dfrac{12}{4}$), ce qui donnerait un coefficient d'agrandissement.
- **c)** on calcule la différence des hauteurs $12 - 4$ au lieu de leur rapport.
- **d)** on divise la petite hauteur par la somme des deux : $\dfrac{4}{12 + 4}$.

</details>

Avis : 

---

## 7. `cqc-effectif-cumule-moyenne-0` (séries BEPC)

**Énoncé :**

Une entreprise a analysé l'ancienneté, en années, de ses 90 employés, regroupée en classes :

| Classe | $[0\,;\,5[$ | $[5\,;\,10[$ | $[10\,;\,15[$ | $[15\,;\,20[$ | $[20\,;\,25[$ |
|---|---|---|---|---|---|
| Effectif | 20 | 25 | 22 | 15 | 8 |

Quel est l'effectif cumulé croissant à la borne $15$ ?

- a) $74{,}4$ employés
- b) $67$ employés
- c) $82$ employés
- d) $45$ employés

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

L'effectif cumulé croissant est un NOMBRE d'individus, obtenu en additionnant les effectifs des classes jusqu'à la borne considérée. La fréquence cumulée croissante, elle, est ce même résultat exprimé en pourcentage de l'effectif total : $f = \dfrac{\text{effectif cumulé}}{N} \times 100$. Ce sont deux grandeurs différentes, même si elles se calculent à partir des mêmes données.

### Corrigé

*Effectif total.*

$$N = 20+25+22+15+8 = 90$$

*Effectif cumulé croissant à la borne $15$.* On additionne les effectifs des classes jusqu'à $15$ (soit $[0\,;\,5[$, $[5\,;\,10[$ et $[10\,;\,15[$) :

$$20+25+22 = 67$$

*Pour information, en fréquence.*

$$\dfrac{67}{90} \times 100 \approx 74{,}4\,\%$$

L'effectif cumulé croissant à la borne $15$ est donc **67 employés** (soit environ $74{,}4\,\%$ de l'effectif total).

### Pourquoi les autres réponses sont fausses
- **a)** c'est la fréquence cumulée en pourcentage ($\dfrac{67}{90} \times 100$) : on la prend pour un nombre d'employés.
- **c)** on inclut la classe $[15\,;\,20[$ qui est au-delà de la borne $15$ : $67 + 15$.
- **d)** on s'arrête à la borne $10$ ($20 + 25$) et on oublie la classe $[10\,;\,15[$.

</details>

Avis : 

---

## 8. `cqc-expression-conjuguee-moyenne-1` (séries BEPC)

**Énoncé :**

Quelle est l'écriture du nombre $D=\dfrac{\sqrt6-\sqrt2}{\sqrt6+\sqrt2}$ sous la forme $p+q\sqrt3$, où $p$ et $q$ sont des entiers relatifs ?

- a) $D=2+\sqrt3$
- b) $D=2-\sqrt3$
- c) $D=8-4\sqrt3$
- d) $D=4-2\sqrt3$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsque le numérateur contient lui aussi des radicaux, on multiplie quand même numérateur et dénominateur par le conjugué du dénominateur : le dénominateur se simplifie grâce à $(\sqrt a+\sqrt b)(\sqrt a-\sqrt b)=a-b$, et le numérateur, lui, se développe comme un carré $(\sqrt a-\sqrt b)^2=a+b-2\sqrt{ab}$.

### Corrigé

Le conjugué de $\sqrt6+\sqrt2$ est $\sqrt6-\sqrt2$.

$D=\dfrac{\sqrt6-\sqrt2}{\sqrt6+\sqrt2}=\dfrac{(\sqrt6-\sqrt2)(\sqrt6-\sqrt2)}{(\sqrt6+\sqrt2)(\sqrt6-\sqrt2)}=\dfrac{(\sqrt6-\sqrt2)^2}{6-2}$

Au numérateur : $(\sqrt6-\sqrt2)^2=6-2\sqrt{6\times2}+2=8-2\sqrt{12}=8-2\times2\sqrt3=8-4\sqrt3$

Donc $D=\dfrac{8-4\sqrt3}{4}=2-\sqrt3$, avec $p=2$ et $q=-1$.

*Vérification numérique* : $\sqrt6\approx2{,}449$ et $\sqrt2\approx1{,}414$, donc $D\approx(2{,}449-1{,}414)/(2{,}449+1{,}414)\approx1{,}035/3{,}864\approx0{,}268$. D'autre part, $2-\sqrt3\approx2-1{,}732=0{,}268$. Cohérent.

### Pourquoi les autres réponses sont fausses

- **a)** Le signe du double produit a été mal géré dans $(\sqrt6-\sqrt2)^2$ : on a trouvé $8+4\sqrt3$.
- **c)** On a oublié de diviser le numérateur par le dénominateur $6-2=4$.
- **d)** Le dénominateur a été calculé $\sqrt{6-2}=2$ au lieu de $6-2=4$.

</details>

Avis : 

---

## 9. `cqc-intervalles-moyenne-1` (séries BEPC)

**Énoncé :**

Quel est l'ensemble des solutions, sous forme d'intervalle, de l'inéquation $5x - 3 > 2x + 9$ dans $\mathbb{R}$ ?

- a) $]4\,;\rightarrow[$
- b) $[4\,;\rightarrow[$
- c) $]\leftarrow\,;4[$
- d) $]2\,;\rightarrow[$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Résoudre une inéquation du premier degré consiste à isoler $x$ d'un côté, comme pour une équation, en regroupant les termes en $x$ d'un côté et les nombres de l'autre. Diviser par un nombre positif conserve le sens de l'inégalité.

### Corrigé

$$5x-3 > 2x+9$$

On regroupe les termes en $x$ à gauche, en retranchant $2x$ aux deux membres, et les constantes à droite, en ajoutant $3$ aux deux membres :

$$5x - 2x > 9 + 3$$

$$3x > 12$$

On divise les deux membres par $3$, nombre positif : le sens de l'inégalité est conservé :

$$x > 4$$

L'ensemble des solutions est donc l'intervalle ouvert
$$S = \,]4\,;\rightarrow[$$

*Contrôle.* Pour $x=5$ (solution) : $5\times5-3=22$ et $2\times5+9=19$, et $22>19$. Pour $x=4$ (la borne, exclue) : $5\times4-3=17$ et $2\times4+9=17$ : l'inégalité stricte $17>17$ est fausse, donc $4$ n'est pas solution, ce qui confirme le crochet ouvert.

### Pourquoi les autres réponses sont fausses

- **b)** L'inégalité est stricte : la borne $4$ doit être exclue.
- **c)** Le sens de l'inégalité a été inversé alors qu'on divise par $3$, nombre positif.
- **d)** Une erreur de signe a été faite : on a ajouté $-3$ au lieu de $+3$ du côté droit, d'où $3x>6$.

</details>

Avis : 

---

## 10. `cqc-placement-de-points-faible-1` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : « Quels sont les coordonnées » à corriger en « Quelles sont les coordonnées ».

**Énoncé :**

Dans un repère orthonormé $(O,\vec{I},\vec{J})$, on donne le point $E(4\;;\,-7)$. Quelles sont les coordonnées de $E'$, symétrique de $E$ par rapport à l'axe des abscisses, de $E''$, symétrique de $E$ par rapport à l'axe des ordonnées, et de $E'''$, symétrique de $E$ par rapport à l'origine $O$ ?

- a) $E'(-4\;;\,-7)$, $E''(4\;;\,7)$ et $E'''(-4\;;\,7)$
- b) $E'(4\;;\,7)$, $E''(-4\;;\,-7)$ et $E'''(4\;;\,-7)$
- c) $E'(4\;;\,7)$, $E''(-4\;;\,-7)$ et $E'''(-4\;;\,7)$
- d) $E'(4\;;\,7)$, $E''(-4\;;\,-7)$ et $E'''(-4\;;\,-7)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Le symétrique d'un point $(x\;;\,y)$ par rapport à l'axe des abscisses est $(x\;;\,-y)$ (l'abscisse est conservée, l'ordonnée change de signe). Par rapport à l'axe des ordonnées, c'est $(-x\;;\,y)$. Par rapport à l'origine $O$, les deux coordonnées changent de signe : $(-x\;;\,-y)$.

### Corrigé

*Symétrique par rapport à l'axe des abscisses.* L'ordonnée change de signe :
$$E'(4\;;\,7)$$

*Symétrique par rapport à l'axe des ordonnées.* L'abscisse change de signe :
$$E''(-4\;;\,-7)$$

*Symétrique par rapport à l'origine $O$.* Les deux coordonnées changent de signe :
$$E'''(-4\;;\,7)$$

### Pourquoi les autres réponses sont fausses

- **a)** Les deux axes ont été confondus : le symétrique par rapport à l'axe des abscisses change le signe de l'ordonnée, pas de l'abscisse.
- **b)** Pour la symétrie centrale, aucune coordonnée n'a été changée : $E'''$ serait confondu avec $E$.
- **d)** Pour la symétrie centrale, une seule coordonnée a été changée de signe, alors qu'il faut changer les deux.

</details>

Avis : 

---

## 11. `cqc-placement-de-points-moyenne-0` (séries BEPC)

**Énoncé :**

Dans un repère orthonormé $(O,\vec{I},\vec{J})$, on donne les points $F(2\;;\,3)$ et $G(-6\;;\,-1)$. Quelles sont les coordonnées du milieu $K$ du segment $[FG]$ et celles du vecteur $\vec{FG}$ ?

- a) $K(-4\;;\,2)$ et $\vec{FG}(-8\;;\,-4)$
- b) $K(-2\;;\,1)$ et $\vec{FG}(-8\;;\,-4)$
- c) $K(-2\;;\,1)$ et $\vec{FG}(8\;;\,4)$
- d) $K(4\;;\,1)$ et $\vec{FG}(-8\;;\,-4)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Les coordonnées du milieu d'un segment $[FG]$ sont la moyenne des coordonnées de $F$ et de $G$. Les coordonnées du vecteur $\vec{FG}$ s'obtiennent en soustrayant les coordonnées de $F$ à celles de $G$.

### Corrigé

*Coordonnées du milieu $K$.*
$$x_K = \frac{x_F + x_G}{2} = \frac{2 + (-6)}{2} = \frac{-4}{2} = -2$$
$$y_K = \frac{y_F + y_G}{2} = \frac{3 + (-1)}{2} = \frac{2}{2} = 1$$
$$K(-2\;;\,1)$$

*Coordonnées du vecteur $\vec{FG}$.*
$$\vec{FG}(x_G - x_F\;;\,y_G - y_F) = \vec{FG}(-6 - 2\;;\,-1 - 3) = \vec{FG}(-8\;;\,-4)$$

### Pourquoi les autres réponses sont fausses

- **a)** Pour le milieu, on a oublié de diviser les sommes par $2$.
- **c)** Les coordonnées du vecteur ont été calculées dans le mauvais sens : $F-G$ au lieu de $G-F$.
- **d)** Pour l'abscisse du milieu, on a calculé $2-(-6)=8$ puis divisé par $2$, au lieu d'additionner $2+(-6)$.

</details>

Avis : 

---

## 12. `cqc-placement-de-points-moyenne-1` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : « le vecteur qui permet de ramener M' sur M » est flou ; écrire « le vecteur de la translation qui transforme M' en M ».

**Énoncé :**

Dans un repère orthonormé $(O,\vec{I},\vec{J})$, on donne le point $M(-3\;;\,2)$ et le vecteur $\vec{u}(5\;;\,-4)$. On note $M'$ l'image de $M$ par la translation de vecteur $\vec{u}$. Quelles sont les coordonnées de $M'$ et celles du vecteur de la translation qui transforme $M'$ en $M$ ?

- a) $M'(-8\;;\,6)$ et vecteur $(-5\;;\,4)$
- b) $M'(2\;;\,-2)$ et vecteur $(5\;;\,-4)$
- c) $M'(2\;;\,-2)$ et vecteur $(-5\;;\,4)$
- d) $M'(2\;;\,6)$ et vecteur $(-5\;;\,4)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

L'image d'un point $M(x\;;\,y)$ par la translation de vecteur $\vec{u}(a\;;\,b)$ est le point $M'(x+a\;;\,y+b)$ : on ajoute simplement les coordonnées du vecteur à celles du point. La translation qui ramène $M'$ sur $M$ est celle de vecteur $-\vec{u}$.

### Corrigé

*Coordonnées de $M'$.*
$$M'(-3 + 5\;;\,2 + (-4)) = M'(2\;;\,-2)$$

*Vecteur ramenant $M'$ sur $M$.* C'est le vecteur opposé à $\vec{u}$ :
$$-\vec{u}(-5\;;\,4)$$

*Contrôle.* $M'(2\;;\,-2)$ translaté par $-\vec{u}(-5\;;\,4)$ donne $(2-5\;;\,-2+4) = (-3\;;\,2)$, qui est bien le point $M$ de départ.

### Pourquoi les autres réponses sont fausses

- **a)** Pour $M'$, on a soustrait les coordonnées de $\vec{u}$ au lieu de les ajouter.
- **b)** On a donné le vecteur $\vec{u}$ lui-même : pour revenir en arrière il faut son opposé.
- **d)** Pour l'ordonnée de $M'$, on a calculé $2-(-4)=6$ : le signe de $-4$ a été mal géré.

</details>

Avis : 

---

## 13. `cqc-point-d-intersection-elevee-1` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : « 2 000 F de location, plus 500 F par heure » ; préférer « un forfait de 2 000 F, plus 500 F par heure », la location désignant déjà le tout.

**Énoncé :**

Une entreprise de location de vélos propose deux formules pour une journée de vélo électrique. Formule $C$ : un forfait de $2\,000$ F, plus $500$ F par heure d'utilisation. Formule $D$ : un forfait de $800$ F, plus $900$ F par heure d'utilisation.

Un client utilise le vélo pendant $2$ heures de plus que la durée pour laquelle les deux formules coûtent le même prix. Quelle affirmation est exacte pour cette durée ?

- a) La formule $D$ est la moins chère, de $800$ F.
- b) La formule $D$ est la moins chère, de $400$ F.
- c) La formule $C$ est la moins chère, de $2\,000$ F.
- d) La formule $C$ est la moins chère, de $800$ F.

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Deux formules coûtent le même prix lorsque leurs expressions sont égales : on résout cette équation pour trouver la durée commune. Au-delà de cette durée, c'est la formule au tarif horaire le plus bas qui devient la plus avantageuse.

### Corrigé

Pour $x$ heures, les prix sont $c(x) = 2\,000 + 500x$ et $d(x) = 800 + 900x$.

*Durée où les prix sont égaux.*
$$2\,000 + 500x = 800 + 900x$$
$$1\,200 = 400x \qquad \Longrightarrow \qquad x = 3$$

Vérification : $c(3) = 3\,500$ F et $d(3) = 3\,500$ F.

*Durée du client.* $3 + 2 = 5$ heures.
$$c(5) = 2\,000 + 500 \times 5 = 4\,500 \qquad d(5) = 800 + 900 \times 5 = 5\,300$$

*Différence.* $5\,300 - 4\,500 = 800$.

À $5$ heures, la formule $D$ coûte $800$ F de plus que la formule $C$ : la formule $C$ est la plus avantageuse, de $800$ F.

### Pourquoi les autres réponses sont fausses

- **a)** Sens inversé : $c(5) = 4\,500$ est inférieur à $d(5) = 5\,300$, donc c'est $C$ la moins chère.
- **b)** On a pris $x = 2$ au lieu de $3 + 2 = 5$ : on oublie de partir de la durée commune. Alors $c(2) = 3\,000$, $d(2) = 2\,600$, d'où $D$ moins chère de $400$ F.
- **c)** On a oublié les frais fixes : $5 \times (900 - 500) = 2\,000$ F, alors que la différence des frais fixes ($1\,200$ F) joue aussi.


</details>

Avis : 

---

## 14. `cqc-point-d-intersection-moyenne-2` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : « frais de développement » pour un tirage ; on parle plutôt de « frais fixes » ou de « frais de dossier ».

**Énoncé :**

Un photographe propose deux formules de tirage de photos. Formule $A$ : $150$ F la photo, sans frais fixe. Formule $B$ : $90$ F la photo, plus $3\,600$ F de frais fixes.

Pour quel nombre de photos les deux formules coûtent-elles le même prix, et quel est ce prix commun ?

- a) $40$ photos, $6\,000$ F CFA
- b) $60$ photos, $9\,000$ F CFA
- c) $15$ photos, $2\,250$ F CFA
- d) $60$ photos, $5\,400$ F CFA

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Deux formules coûtent le même prix lorsque leurs expressions sont égales. On écrit cette égalité, on regroupe les termes en $x$ d'un côté et les nombres de l'autre, puis on isole $x$.

### Corrigé

Pour $x$ photos : $p(x) = 150x$ et $q(x) = 90x + 3\,600$.
$$150x = 90x + 3\,600 \qquad 60x = 3\,600 \qquad x = 60$$

*Prix commun.* $p(60) = 150 \times 60 = 9\,000$.

Vérification : $q(60) = 90 \times 60 + 3\,600 = 5\,400 + 3\,600 = 9\,000$.

Les deux formules coûtent le même prix pour $60$ photos, soit $9\,000$ F CFA.

### Pourquoi les autres réponses sont fausses

- **a)** $40$ photos, $6\,000$ F : on a divisé $3\,600$ par $90$ au lieu de $150 - 90 = 60$.
- **c)** $15$ photos, $2\,250$ F : on a additionné les prix unitaires ($150 + 90 = 240$) au lieu de les soustraire.
- **d)** $60$ photos, $5\,400$ F : le nombre de photos est juste, mais le prix donné oublie les frais de développement de la formule $B$ ($90 \times 60 = 5\,400$ seulement).


</details>

Avis : 

---

## 15. `cqc-point-d-intersection-moyenne-3` (séries BEPC)

**Remarque du relecteur :** Les choix b et d citent des points de la droite (0;1) et (-2;0) : ce sont de bons distracteurs, mais « sécantes en » est faux puisque les droites sont confondues.

**Énoncé :**

On donne les droites $(D_5)$ d'équation $y = \dfrac{1}{2}x + 1$ et $(D_6)$ d'équation $2x - 4y + 4 = 0$.

Quelle est la position relative de ces deux droites ?

- a) Elles sont strictement parallèles.
- b) Elles sont sécantes au point $(0\,;\,1)$.
- c) Elles sont confondues.
- d) Elles sont sécantes au point $(-2\,;\,0)$.

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Un système de deux équations de droites admet une unique solution si les droites sont sécantes, aucune solution si elles sont strictement parallèles, et une infinité de solutions si elles sont confondues. Pour comparer deux droites, on les met toutes deux sous la forme $y = ax + b$.

### Corrigé

*Mise sous forme réduite de $(D_6)$.*
$$2x - 4y + 4 = 0 \quad \Longleftrightarrow \quad -4y = -2x - 4 \quad \Longleftrightarrow \quad y = \frac{1}{2}x + 1$$

*Comparaison.* $(D_5)$ a pour équation $y = \dfrac{1}{2}x + 1$ et $(D_6)$, une fois réduite, a exactement la même équation.

Les deux droites ont le même coefficient directeur et la même ordonnée à l'origine : ce sont deux équations de la même droite. $(D_5)$ et $(D_6)$ sont donc confondues.

### Pourquoi les autres réponses sont fausses

- **a)** Strictement parallèles : on a bien trouvé le même coefficient directeur, mais on a mal calculé l'ordonnée à l'origine de $(D_6)$ (par exemple $-1$ au lieu de $1$ après une erreur de signe).
- **b)** Sécantes au point $(0\,;\,1)$ : ce point est commun aux deux droites, mais il n'est pas le seul, puisque tous leurs points sont communs.
- **d)** Sécantes au point $(-2\,;\,0)$ : ce point est l'intersection de $(D_5)$ avec l'axe des abscisses, et non un point d'intersection des deux droites entre elles.


</details>

Avis : 

---

## 16. `cqc-priorites-operatoires-elevee-0` (séries BEPC)

**Énoncé :**

Calculer le nombre $D$ défini par $D = \dfrac{5^2 - 3 \times 6}{2 \times (7 - 4) - 1}$.

- a) $\dfrac{7}{5}$
- b) $21$
- c) $\dfrac{7}{9}$
- d) $-\dfrac{8}{5}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans une expression fractionnaire, la barre de fraction joue le rôle d'une parenthèse : tout le numérateur doit être réduit à un seul nombre, et tout le dénominateur aussi, chacun en respectant l'ordre habituel des opérations (puissances, puis multiplications, puis additions et soustractions). La division se fait ensuite entre ces deux nombres.

### Corrigé

*Numérateur :* $5^2 = 25$, puis $3 \times 6 = 18$, donc le numérateur vaut $25 - 18 = 7$.

*Dénominateur :* $7 - 4 = 3$ (parenthèse), puis $2 \times 3 = 6$, donc le dénominateur vaut $6 - 1 = 5$.

*Division :* $D = \dfrac{7}{5}$.

### Pourquoi les autres réponses sont fausses

- **b)** $21$ : on a divisé seulement $18$ par $6$ (en croyant que la barre ne regroupe que les termes voisins) : $25 - 3 - 1 = 21$.
- **c)** $\dfrac{7}{9}$ : au dénominateur, on a oublié la priorité de la multiplication sur la parenthèse : $2 \times 7 - 4 - 1 = 9$.
- **d)** $-\dfrac{8}{5}$ : on a calculé $5^2$ comme $5 \times 2 = 10$, d'où $10 - 18 = -8$ au numérateur.


</details>

Avis : 

---

## 17. `cqc-priorites-operatoires-moyenne-2` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : le contexte est peu cohérent. Les sacs abîmés sont comptés comme vendus et donnent en plus lieu à une indemnisation « versée par la coopérative » ; préciser qui indemnise qui, par exemple une remise de 1 500 F accordée à l'acheteur par sac abîmé.

**Énoncé :**

Une coopérative agricole vend des sacs de cacao à 2 500 F CFA le sac. Sur une récolte de 18 sacs, 3 sacs invendus doivent être retirés du décompte, et 4 sacs ont été abîmés pendant le transport, chacun donnant lieu à une remise de 1 500 F CFA accordée à l'acheteur. La recette nette $R$, en francs CFA, est donnée par $R = 2500 \times (18 - 3) - 4 \times 1500$. Calculer $R$.

- a) 37 500 F CFA
- b) 39 000 F CFA
- c) 31 500 F CFA
- d) 27 500 F CFA

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans une expression combinant une parenthèse, des multiplications et une soustraction, on calcule d'abord le contenu de la parenthèse, puis les multiplications, et seulement en dernier la soustraction.

### Corrigé

Parenthèse, nombre de sacs vendus : $18 - 3 = 15$.

Multiplications : $2500 \times 15 = 37500$ (recette sur les sacs vendus) et $4 \times 1500 = 6000$ (indemnités versées).

Soustraction : $R = 37500 - 6000 = 31500$.

La recette nette de la coopérative est donc de 31 500 F CFA.

### Pourquoi les autres réponses sont fausses

- **a)** 37 500 F CFA : on a oublié de retrancher les indemnités versées pour les sacs abîmés.
- **b)** 39 000 F CFA : on a oublié de retirer les 3 sacs invendus : $45\,000 - 6\,000$.
- **d)** 27 500 F CFA : on a retiré les 4 sacs abîmés du nombre de sacs vendus ($18 - 3 - 4 = 11$) au lieu de payer l'indemnité de 1 500 F CFA par sac.


</details>

Avis : 

---

## 18. `cqc-denominateur-rationnel-moyenne-0` (séries BEPC)

**Énoncé :**

Quelle est l'écriture du nombre $\dfrac{3}{2 + \sqrt{5}}$ sans radical au dénominateur ?

- a) $6 - 3\sqrt{5}$
- b) $\dfrac{2 - \sqrt{5}}{3}$
- c) $3\sqrt{5} - 6$
- d) $6 + 3\sqrt{5}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour rendre rationnel un dénominateur de la forme $p + \sqrt{n}$, on multiplie le numérateur et le dénominateur par l'expression conjuguée $p - \sqrt{n}$ : l'identité $(a-b)(a+b) = a^{2} - b^{2}$ élimine alors le radical du dénominateur.

### Corrigé

$$\frac{3}{2 + \sqrt{5}} = \frac{3(2 - \sqrt{5})}{(2 + \sqrt{5})(2 - \sqrt{5})}$$

*Dénominateur :* $2^{2} - (\sqrt{5})^{2} = 4 - 5 = -1$.

*Numérateur :* $3(2 - \sqrt{5}) = 6 - 3\sqrt{5}$.

$$\frac{3}{2 + \sqrt{5}} = \frac{6 - 3\sqrt{5}}{-1} = -6 + 3\sqrt{5} = 3\sqrt{5} - 6$$

### Pourquoi les autres réponses sont fausses

- **a)** $6 - 3\sqrt{5}$ : on a oublié que le dénominateur vaut $-1$ et non $1$, donc le signe n'a pas été changé.
- **b)** $\dfrac{2 - \sqrt{5}}{3}$ : on a calculé le dénominateur comme $4 + 5 = 9$ au lieu de $4 - 5 = -1$.
- **d)** $6 + 3\sqrt{5}$ : en divisant par $-1$, on n'a changé que le signe du premier terme.


</details>

Avis : 

---

## 19. `cqc-denominateur-rationnel-moyenne-2` (séries BEPC)

**Remarque du relecteur :** LIMITE : rationalisation avec un dénominateur √3 + 4 et un développement du numérateur ; reste dans le programme de 3e.

**Énoncé :**

On donne $A = \dfrac{2 - x}{x + 4}$.

Quelle est la valeur exacte de $A$ pour $x = \sqrt{3}$, écrite sous la forme d'une fraction dont le dénominateur est un nombre entier ?

- a) $\dfrac{11 - 6\sqrt{3}}{13}$
- b) $\dfrac{11 - 6\sqrt{3}}{19}$
- c) $\dfrac{5 - 6\sqrt{3}}{13}$
- d) $\dfrac{8 - 6\sqrt{3}}{13}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour calculer la valeur numérique d'une expression contenant un radical, on remplace d'abord la variable par sa valeur, puis on rend le dénominateur rationnel en multipliant par l'expression conjuguée.

### Corrigé

*Substitution :* $A = \dfrac{2 - \sqrt{3}}{\sqrt{3} + 4}$.

*Rationalisation.* On multiplie les deux termes par l'expression conjuguée $4 - \sqrt{3}$ :
$$A = \frac{(2 - \sqrt{3})(4 - \sqrt{3})}{(4 + \sqrt{3})(4 - \sqrt{3})}$$

*Dénominateur :* $4^{2} - (\sqrt{3})^{2} = 16 - 3 = 13$.

*Numérateur :* $(2 - \sqrt{3})(4 - \sqrt{3}) = 8 - 2\sqrt{3} - 4\sqrt{3} + (\sqrt{3})^{2} = 8 - 6\sqrt{3} + 3 = 11 - 6\sqrt{3}$.

$$A = \frac{11 - 6\sqrt{3}}{13}$$

### Pourquoi les autres réponses sont fausses

- **b)** $\dfrac{11 - 6\sqrt{3}}{19}$ : on a calculé le dénominateur comme $16 + 3 = 19$ au lieu de $16 - 3 = 13$.
- **c)** $\dfrac{5 - 6\sqrt{3}}{13}$ : dans le numérateur, $(-\sqrt{3}) \times (-\sqrt{3})$ a été compté $-3$ au lieu de $+3$.
- **d)** $\dfrac{8 - 6\sqrt{3}}{13}$ : le terme $(\sqrt{3})^{2} = 3$ du développement a été oublié.


</details>

Avis : 

---


---

# Lot : b1-bac-vague-4-maths

## Vague 4 Maths BAC (questions posées au BAC seulement) : 35 QCM à faire relire par l'enseignant (campagne B1)

Date : 2026-11-01. Sur 116 QCM convertis (151 questions BAC étudiées, 35 écartées), **35** vous sont soumis : ceux que le relecteur aveugle a assortis d'une remarque, ceux dont des séries ont été retirées, et un tirage de 12 autres. Le lot est prêt mais n'est pas en ligne tant que vous n'avez pas répondu. Les 116 résolutions à l'aveugle ont donné la clé, sauf trois questions jugées hors niveau pour la série A, dont la série A a été retirée.

## Avis déjà rendus, appliqués par analogie (à confirmer)

- **Série A retirée** de `forme-algebrique-bac-a-faible-0` (nombres complexes) et de `recurrence-tle-c-moyenne-3` et `-moyenne-4` (récurrence, suites, divisibilité), conformément à la liste des notions hors programme de la série A.

## Points à trancher (nouveaux)

1. **Primitives de u'/u et de u'e^u en série A** (`primitives`) : au programme ?
2. **Série C et similitudes indirectes** (`point-fixe-moyenne-4` : z' = i·conj(z) + 1 - i, symétrie) : à garder en C ?
3. **Récurrence et divisibilité** (`recurrence-tle-c-moyenne-4`) : arithmétique en série D ?
4. **Formule de Héron et R = abc/4S** (`cercle-circonscrit-tle-c-moyenne-4`) en D et TI.
5. **Questions très faciles** gardées pour la série C/E (niveau Seconde) : à retirer ?
6. **Algèbre linéaire C/E** : coordonnées dans une base de polynômes, déterminant 3x3 avec paramètre, noyau d'un endomorphisme, équation différentielle avec second membre non guidé.
7. **Questions dont l'énoncé a changé de fond** (démonstration réduite à un résultat, hypothèses admises, méthode remplacée) : à examiner de près.

Pour chaque question : **OK**, **à corriger** (dire quoi), **à retirer**, ou **retirer la série X**.

## 1. `cqc-base-tle-c-elevee-5` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : la notation R_2[X] et les coordonnées dans une base de polynômes relèvent de l'algèbre linéaire, à vérifier au programme de Terminale C/E.

**Énoncé :**

On note $\mathbb{R}_2[X]$ l'espace vectoriel des polynômes de degré au plus $2$. La famille $\big(1,\ X-1,\ (X-1)^2\big)$ est une base de $\mathbb{R}_2[X]$.

Quelles sont les coordonnées du polynôme $P=X^2+X+1$ dans cette base ?

- a) $(1\,;1\,;1)$
- b) $(-1\,;-1\,;1)$
- c) $(3\,;3\,;1)$
- d) $(0\,;3\,;1)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans une base, tout vecteur s'écrit de façon unique comme combinaison linéaire des vecteurs de la base. Pour les polynômes, on développe les puissances de $X-1$ puis on identifie les coefficients.

### Corrigé

On cherche $a,b,c$ tels que $X^2+X+1=a+b(X-1)+c(X-1)^2=cX^2+(b-2c)X+(a-b+c)$. Par identification : $c=1$, $b-2c=1$ donc $b=3$, et $a-b+c=1$ donc $a=1+3-1=3$.
$$P=3+3(X-1)+(X-1)^2.$$
Les coordonnées de $P$ sont $(3\,;3\,;1)$. Vérification en $X=2$ : $P(2)=7$ et $3+3\times1+1=7$.

### Pourquoi les autres réponses sont fausses

- **a)** ce sont les coefficients de $P$ dans la base $(1,X,X^2)$, pas dans la base donnée.
- **b)** $(X-1)^2$ a été développé en $X^2+2X+1$ au lieu de $X^2-2X+1$.
- **d)** le terme constant $-b$ de $b(X-1)$ a été oublié dans l'identification.

</details>

Avis : 

---

## 2. `cqc-base-tle-c-moyenne-2` (séries BAC:C BAC:E)

**Énoncé :**

Soit $F=\{(x\,;y\,;z)\in\mathbb{R}^3\mid x+y-z=0\}$, qui est un plan vectoriel de $\mathbb{R}^3$.

Laquelle de ces familles est une base de $F$ ?

- a) $\big((1\,;0\,;1),(0\,;1\,;1)\big)$
- b) $\big((1\,;0\,;-1),(0\,;1\,;-1)\big)$
- c) $\big((1\,;0\,;0),(0\,;1\,;0)\big)$
- d) $\big((1\,;-1\,;0),(2\,;-2\,;0)\big)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour trouver une base d'un sous-espace défini par des équations, on exprime ses éléments à l'aide de paramètres libres : on obtient une famille génératrice ; si elle est libre, c'est une base et son nombre de vecteurs donne la dimension.

### Corrigé

Un vecteur de $F$ vérifie $z=x+y$, donc s'écrit $(x\,;y\,;x+y)=x\,(1\,;0\,;1)+y\,(0\,;1\,;1)$. La famille $\big((1\,;0\,;1),(0\,;1\,;1)\big)$ engendre donc $F$. Elle est libre : $\alpha(1\,;0\,;1)+\beta(0\,;1\,;1)=\vec0$ donne $(\alpha\,;\beta\,;\alpha+\beta)=(0\,;0\,;0)$, soit $\alpha=\beta=0$.

C'est une base de $F$, qui est donc de dimension $2$ : un plan vectoriel.

### Pourquoi les autres réponses sont fausses

- **b)** le signe de $z$ a été inversé en écrivant $z=-(x+y)$ ; ces vecteurs ne vérifient pas $x+y-z=0$.
- **c)** la variable $z$ a été oubliée : ces vecteurs sont libres mais n'appartiennent pas à $F$.
- **d)** ces vecteurs sont bien dans $F$ mais colinéaires : la famille est liée, elle n'engendre qu'une droite.

</details>

Avis : 

---

## 3. `cqc-cercle-circonscrit-tle-c-moyenne-2` (séries BAC:C BAC:D BAC:E BAC:TI)

**Énoncé :**

Dans un repère orthonormé, on donne $A(0\,;0)$, $B(4\,;0)$ et $C(1\,;3)$.

Quels sont le centre $\Omega$ et le rayon $R$ du cercle circonscrit au triangle $ABC$ ?

- a) $\Omega(2\,;1)$ et $R=5$
- b) $\Omega(1\,;2)$ et $R=\sqrt5$
- c) $\Omega(2\,;0)$ et $R=2$
- d) $\Omega(2\,;1)$ et $R=\sqrt5$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Le centre $\Omega$ est le point équidistant de $A$, $B$ et $C$ : on écrit $\Omega A^2=\Omega B^2$ et $\Omega A^2=\Omega C^2$, ce qui donne deux équations du premier degré (les carrés s'éliminent).

### Corrigé

Soit $\Omega(x\,;y)$. $\Omega A^2=\Omega B^2$ donne $x^2+y^2=(x-4)^2+y^2$, soit $x=2$.
$\Omega A^2=\Omega C^2$ donne $x^2+y^2=(x-1)^2+(y-3)^2$, soit $0=-2x+1-6y+9$, c'est-à-dire $2x+6y=10$ ; avec $x=2$ : $y=1$.

Le centre est $\Omega(2\,;1)$ et $R^2=\Omega A^2=4+1=5$, donc $R=\sqrt5$. Vérification : $\Omega B^2=4+1=5$ et $\Omega C^2=1+4=5$.

### Pourquoi les autres réponses sont fausses

- **a)** $R^2=5$ a été confondu avec $R$ : le rayon est $\sqrt5$.
- **b)** les coordonnées du centre ont été permutées ; ce point est bien à la distance $\sqrt5$ de $A$ mais pas de $B$.
- **c)** le centre a été pris au milieu de $[AB]$ (comme si $[AB]$ était un diamètre) ; ce point n'est pas à la distance $2$ de $C$.

</details>

Avis : 

---

## 4. `cqc-cercle-circonscrit-tle-c-moyenne-4` (séries BAC:C BAC:D BAC:E BAC:TI)

**Remarque du relecteur :** LIMITE : nécessite la formule de Héron ou Al-Kashi puis la loi des sinus (a/sin A=2R), relations métriques peu travaillées en Terminale D/TI.

**Énoncé :**

Un triangle a pour côtés $13$, $14$ et $15$ (dans la même unité de longueur).

Quel est le rayon $R$ de son cercle circonscrit ?

- a) $\dfrac{65}{4}$
- b) $\dfrac{65}{2}$
- c) $\dfrac{65}{8}$
- d) $4$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule l'aire $S$ avec la formule de Héron $S=\sqrt{p(p-a)(p-b)(p-c)}$ où $p$ est le demi-périmètre, puis le rayon du cercle circonscrit avec $R=\dfrac{abc}{4S}$.

### Corrigé

Demi-périmètre : $p=\dfrac{13+14+15}{2}=21$.
$$S=\sqrt{21\times(21-13)\times(21-14)\times(21-15)}=\sqrt{21\times8\times7\times6}=\sqrt{7056}=84.$$
$$R=\dfrac{13\times14\times15}{4\times84}=\dfrac{2730}{336}=\dfrac{65}{8}=8{,}125.$$

### Pourquoi les autres réponses sont fausses

- **a)** la formule $R=\dfrac{abc}{2S}$ a été utilisée au lieu de $R=\dfrac{abc}{4S}$.
- **b)** le demi-périmètre $21$ a été utilisé à la place de l'aire $84$ au dénominateur : $\dfrac{2730}{4\times21}$.
- **d)** c'est le rayon du cercle inscrit $\dfrac Sp=\dfrac{84}{21}$, et non celui du cercle circonscrit.

</details>

Avis : 

---

## 5. `cqc-continuite-tle-c-elevee-5` (séries BAC:C BAC:E)

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=x\sin\left(\dfrac1x\right)$ pour $x\neq0$ et $f(0)=0$.

Laquelle de ces affirmations est exacte ?

- a) $f$ est continue et dérivable en $0$, avec $f'(0)=0$.
- b) $f$ est continue en $0$ mais n'est pas dérivable en $0$.
- c) $f$ n'est pas continue en $0$, car $\sin\dfrac1x$ n'a pas de limite en $0$.
- d) $f$ est dérivable en $0$, avec $f'(0)=1$.

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour la continuité en $0$, on encadre $|f(x)|$ en utilisant $|\sin t|\leq1$ et on applique le théorème des gendarmes. Pour la dérivabilité, on étudie la limite du taux d'accroissement $\dfrac{f(x)-f(0)}{x}$ ; si elle n'existe pas, $f$ n'est pas dérivable.

### Corrigé

**Continuité.** Pour $x\neq0$, $|f(x)|=|x|\left|\sin\dfrac1x\right|\leq|x|$. Comme $|x|\to0$ quand $x\to0$, le théorème des gendarmes donne $\lim\limits_{x\to0}f(x)=0=f(0)$ : $f$ est continue en $0$.

**Dérivabilité.** Le taux d'accroissement en $0$ est, pour $x\neq0$, $\dfrac{f(x)-f(0)}{x}=\sin\dfrac1x$. En prenant $x_n=\dfrac{1}{\frac\pi2+2n\pi}\to0$ on obtient $\sin\dfrac1{x_n}=1$, tandis qu'avec $x_n'=\dfrac1{\frac{3\pi}2+2n\pi}\to0$ on obtient $-1$. Le taux n'a pas de limite.

$f$ est donc continue en $0$ mais non dérivable en $0$.

### Pourquoi les autres réponses sont fausses

- **a)** le taux d'accroissement est $\sin\dfrac1x$, qui n'a pas de limite en $0$ ; ce n'est pas $x\sin\dfrac1x\to0$.
- **c)** c'est le facteur $x$ qui impose la limite $0$ : $|f(x)|\leq|x|$ et le théorème des gendarmes donnent la continuité.
- **d)** la limite $\lim\limits_{t\to0}\dfrac{\sin t}{t}=1$ a été confondue avec le taux $\sin\dfrac1x$, qui n'a pas de limite en $0$.

</details>

Avis : 

---

## 6. `cqc-determinant-elevee-5` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : bases et déterminant dans R^3, à vérifier au programme de Terminale C/E.

**Énoncé :**

Pour tout réel $m$, on considère les vecteurs $\vec a(1\,;1\,;1)$, $\vec b(1\,;m\,;m)$ et $\vec c(1\,;m\,;m^2)$ de $\mathbb{R}^3$.

Pour quelles valeurs de $m$ la famille $(\vec a,\vec b,\vec c)$ est-elle une base de $\mathbb{R}^3$ ?

- a) $m\neq0$ et $m\neq1$
- b) $m\neq0$ seulement
- c) $m\neq1$ seulement
- d) $m\neq0$ et $m\neq-1$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule le déterminant $3\times3$ des coordonnées en développant selon une ligne, puis on le factorise. Une famille de trois vecteurs de $\mathbb{R}^3$ est une base si et seulement si ce déterminant est non nul.

### Corrigé

Développons selon la première ligne :
$$\det(\vec a,\vec b,\vec c)=1\begin{vmatrix}m&m\\m&m^2\end{vmatrix}-1\begin{vmatrix}1&m\\1&m^2\end{vmatrix}+1\begin{vmatrix}1&m\\1&m\end{vmatrix}=(m^3-m^2)-(m^2-m)+(m-m).$$
$$\det(\vec a,\vec b,\vec c)=m^3-2m^2+m=m(m-1)^2.$$
La famille est une base si et seulement si $m(m-1)^2\neq0$, c'est-à-dire pour $m\notin\{0\,;1\}$.

### Pourquoi les autres réponses sont fausses

- **b)** la racine double $m=1$ a été oubliée : pour $m=1$ les trois vecteurs sont égaux à $(1\,;1\,;1)$, la famille est liée.
- **c)** la racine $m=0$ a été oubliée : pour $m=0$, $\vec b=(1\,;0\,;0)$ et $\vec c=(1\,;0\,;0)$ sont égaux, la famille est liée.
- **d)** la factorisation a été faite avec $(m+1)^2$ au lieu de $(m-1)^2$ ; $m^3-2m^2+m=m(m-1)^2$.

</details>

Avis : 

---

## 7. `cqc-determinant-moyenne-3` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : déterminant 3x3 dans R^3, à vérifier au programme de Terminale C/E.

**Énoncé :**

Dans $\mathbb{R}^3$ muni de sa base canonique, on considère les vecteurs $\vec u_1=(1\,;0\,;1)$, $\vec u_2=(2\,;1\,;0)$ et $\vec u_3=(0\,;1\,;3)$.

Quelle est la valeur du déterminant des coordonnées de $(\vec u_1,\vec u_2,\vec u_3)$ ?

- a) $1$
- b) $3$
- c) $-5$
- d) $5$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Trois vecteurs de $\mathbb{R}^3$ forment une base si et seulement si le déterminant de leurs coordonnées (rangées en colonnes) est non nul. On le calcule en développant selon une ligne ou une colonne, en respectant l'alternance des signes $+,-,+$.

### Corrigé

Le déterminant dont les colonnes sont $\vec u_1,\vec u_2,\vec u_3$ est
$$\begin{vmatrix}1&2&0\\0&1&1\\1&0&3\end{vmatrix}.$$
Développons selon la première ligne :
$$1\times\begin{vmatrix}1&1\\0&3\end{vmatrix}-2\times\begin{vmatrix}0&1\\1&3\end{vmatrix}+0=1\times3-2\times(-1)=5.$$
Le déterminant vaut $5\neq0$ : les trois vecteurs forment une base de $\mathbb{R}^3$.

### Pourquoi les autres réponses sont fausses

- **a)** l'alternance des signes a été oubliée : $3-2\times1$ au lieu de $3-2\times(-1)$.
- **b)** seul le premier terme du développement a été conservé.
- **c)** le signe global a été inversé (cofacteurs pris avec les signes $-,+,-$).

</details>

Avis : 

---

## 8. `cqc-determinant-tle-c-moyenne-2` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : applications linéaires de R^2, à vérifier au programme de Terminale C/E.

**Énoncé :**

Pour tout réel $m$, on note $f_m$ l'application linéaire de $\mathbb{R}^2$ dans $\mathbb{R}^2$ définie par $$f_m(x\,;y)=\big(mx+2y\,;\,3x+(m-1)y\big).$$ Pour quelles valeurs de $m$ l'application $f_m$ n'est-elle pas bijective ?

- a) $m=-3$ ou $m=2$
- b) $m=3$ ou $m=-2$
- c) aucune valeur de $m$
- d) $m=0$ ou $m=1$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Une application linéaire $(x\,;y)\mapsto(ax+by\,;cx+dy)$ du plan dans lui-même est bijective si et seulement si son déterminant $ad-bc$ est non nul. Avec un paramètre, on résout donc $ad-bc=0$ ; les autres valeurs de $m$ donnent une bijection.

### Corrigé

Ici $a=m$, $b=2$, $c=3$, $d=m-1$, donc $\det f_m=m(m-1)-2\times3=m^2-m-6=(m-3)(m+2)$.

$f_m$ n'est pas bijective si et seulement si $\det f_m=0$, soit $m=3$ ou $m=-2$.

Contrôle : pour $m=0$, $\det f_0=-6\neq0$, donc $f_0$ est bijective.

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe en factorisant : $(m+3)(m-2)=m^2+m-6$ n'est pas le déterminant.
- **c)** on a additionné $2\times3$ au lieu de le soustraire : $m^2-m+6$ ne s'annule jamais, mais ce n'est pas le déterminant.
- **d)** on a oublié le terme $-bc=-6$ : $m(m-1)=0$ ne donne pas le déterminant.

</details>

Avis : 

---

## 9. `cqc-encadrement-faible-1` (séries BAC:A BAC:C BAC:E BAC:TI)

**Remarque du relecteur :** Niveau collège, très facile pour une Terminale.

**Énoncé :**

Soit $Y=-\dfrac{15}{4}$. Quel est l'unique entier relatif $n$ tel que $n<Y<n+1$ ?

- a) $n=-3$
- b) $n=3$
- c) $n=-4$
- d) $n=-5$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Encadrer un nombre par deux entiers consécutifs revient à repérer entre quels entiers il se situe, en écrivant d'abord sa valeur décimale. Avec un nombre négatif, on reste attentif au sens de l'encadrement : $-4$ est plus petit que $-3$.

### Corrigé

On écrit $Y=-\dfrac{15}{4}=-3{,}75$.

Le nombre $-3{,}75$ est compris entre $-4$ et $-3$, deux entiers consécutifs :
$$-4<-3{,}75<-3.$$
Donc $n=-4$.

### Pourquoi les autres réponses sont fausses

- **a)** on a gardé la partie entière $3$ en la lisant comme pour un positif ; or $-3>-3{,}75$, donc $-3$ est le plus grand des deux entiers, pas le plus petit.
- **b)** oubli du signe : on a encadré $3{,}75$ au lieu de $-3{,}75$.
- **d)** on a retranché une unité de trop : $-5<-3{,}75$ mais $-5+1=-4<-3{,}75$, donc $-3{,}75$ n'est pas inférieur à $n+1$.

</details>

Avis : 

---

## 10. `cqc-encadrement-moyenne-2` (séries BAC:A BAC:C BAC:E BAC:TI)

**Remarque du relecteur :** Niveau collège/seconde, très facile pour une Terminale.

**Énoncé :**

Quel est l'ensemble des réels $x$ vérifiant $-7 \leq 3x + 2 \leq 8$ ?

- a) $[-3\,;2]$
- b) $\left[-\dfrac73\,;\dfrac83\right]$
- c) $[-9\,;6]$
- d) $]-3\,;2[$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Un encadrement du type $p \leq ax + b \leq q$ se résout en isolant $x$ au centre : on retranche la constante aux trois membres, puis on divise par le coefficient de $x$. Diviser par un nombre positif conserve le sens des inégalités.

### Corrigé

$$-7 \leq 3x + 2 \leq 8$$
On soustrait $2$ aux trois membres : $-9 \leq 3x \leq 6$.

On divise par $3$ (positif, le sens est conservé) : $-3 \leq x \leq 2$.

Les inégalités sont larges, donc les bornes sont incluses : l'ensemble des solutions est $[-3\,;2]$.

Contrôle : pour $x=-3$, $3\times(-3)+2=-7$ ; pour $x=2$, $3\times2+2=8$.

### Pourquoi les autres réponses sont fausses

- **b)** on a oublié de soustraire $2$ et on a seulement divisé par $3$.
- **c)** on a soustrait $2$ mais oublié de diviser par $3$.
- **d)** les inégalités de départ sont larges : les bornes $-3$ et $2$ sont atteintes et donc incluses.

</details>

Avis : 

---

## 11. `cqc-forme-algebrique-bac-a-faible-0` (séries BAC:A BAC:TI)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** Nombres complexes hors programme de la série A (série la plus faible indiquée) ; retirer BAC:A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On donne les nombres complexes $z_1=3-2i$ et $z_2=-1+4i$. Quelle est la forme algébrique de $z_1z_2$ ?

- a) $-11+14i$
- b) $5+10i$
- c) $-3-8i$
- d) $5+14i$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour un produit de deux nombres complexes, on développe comme pour deux binômes, puis on remplace $i^{2}$ par $-1$. La partie imaginaire de $a+ib$ est le réel $b$.

### Corrigé

$$z_1z_2=(3-2i)(-1+4i)=-3+12i+2i-8i^{2}=-3+14i+8=5+14i.$$
La forme algébrique est $5+14i$ (partie réelle $5$, partie imaginaire $14$).

Contrôle : en permutant les facteurs, $(-1+4i)(3-2i)=-3+2i+12i-8i^{2}=5+14i$.

### Pourquoi les autres réponses sont fausses

- **a)** on a pris $i^{2}=+1$ : le terme $-8i^{2}$ devient $-8$ au lieu de $+8$.
- **b)** on a soustrait $2i$ de $12i$ au lieu de les additionner : $12i+2i=14i$.
- **c)** on a multiplié les parties réelles entre elles et les parties imaginaires entre elles, sans les termes croisés.

</details>

Avis : 

---

## 12. `cqc-integration-d-une-inegalite-tle-c-elevee-5` (séries BAC:C BAC:E)

**Énoncé :**

Pour tout entier naturel $n$, on pose $I_n=\displaystyle\int_0^1\dfrac{x^n}{1+x}\,dx$. Que vaut $I_n+I_{n+1}$ ?

- a) $\dfrac1{n+1}$
- b) $\dfrac1{n+2}$
- c) $\dfrac1{n+1}+\dfrac1{n+2}$
- d) $\dfrac1{2(n+1)}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Avant d'intégrer, on regroupe les deux fonctions sous un même signe somme : si le numérateur se factorise par $1+x$, la fraction se simplifie. On utilise ensuite $\displaystyle\int_0^1x^n\,dx=\dfrac1{n+1}$.

### Corrigé

$$I_n+I_{n+1}=\int_0^1\dfrac{x^n+x^{n+1}}{1+x}\,dx=\int_0^1\dfrac{x^n(1+x)}{1+x}\,dx=\int_0^1x^n\,dx=\dfrac1{n+1}.$$

Contrôle pour $n=0$ : $I_0=\ln2\approx0{,}693$, $I_1=1-\ln2\approx0{,}307$ et $I_0+I_1=1=\dfrac1{0+1}$.

### Pourquoi les autres réponses sont fausses

- **b)** on a seulement intégré $x^{n+1}$ en oubliant le terme $x^n$ (ou l'inverse).
- **c)** on a additionné $\displaystyle\int_0^1x^n\,dx$ et $\displaystyle\int_0^1x^{n+1}\,dx$ sans simplifier par $1+x$ : on a oublié le dénominateur.
- **d)** on a remplacé $\dfrac1{1+x}$ par son minorant $\dfrac12$ : cela donne un encadrement, pas la valeur exacte.

</details>

Avis : 

---

## 13. `cqc-isometrie-tle-c-moyenne-4` (séries BAC:C BAC:E)

**Énoncé :**

Le plan complexe est rapporté à un repère orthonormé direct. On donne $A(0)$, $B(2)$, $A'(1+i)$ et $B'(1+3i)$. Il existe une unique rotation $r$ telle que $r(A)=A'$ et $r(B)=B'$. Quelle est son écriture complexe ?

- a) $z'=iz+1+i$
- b) $z'=-iz+1+i$
- c) $z'=iz+1-i$
- d) $z'=z+1+i$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Une rotation s'écrit $z'=az+b$ avec $|a|=1$. Si $A\mapsto A'$ et $B\mapsto B'$, alors $a=\dfrac{z_{B'}-z_{A'}}{z_B-z_A}$ et $b=z_{A'}-az_A$.

### Corrigé

On calcule $a=\dfrac{z_{B'}-z_{A'}}{z_B-z_A}=\dfrac{2i}{2}=i$, de module $1$. Puis $b=z_{A'}-a\,z_A=1+i$. L'écriture complexe est
$$z'=iz+1+i.$$
Vérification : $r(B)=2i+1+i=1+3i=z_{B'}$. C'est une rotation d'angle $\dfrac\pi2$.

### Pourquoi les autres réponses sont fausses

- **b)** on a inversé le quotient pour calculer $a$ : on trouve $a=\dfrac{2}{2i}=-i$, et alors $r(B)=1-i\neq B'$.
- **c)** erreur de signe sur $b$ : alors $r(A)=1-i\neq A'$.
- **d)** c'est une translation ($a=1$) : elle envoie $B$ sur $3+i$ et non sur $B'$.

</details>

Avis : 

---

## 14. `cqc-point-fixe-moyenne-4` (séries BAC:C BAC:D BAC:E BAC:TI)

**Remarque du relecteur :** LIMITE : transformation z -> i z̄ + b (antidéplacement) pour la série TI, à vérifier au programme TI.

**Énoncé :**

Le plan complexe est rapporté à un repère orthonormé direct. On considère la transformation $t$ qui à tout point $M$ d'affixe $z$ associe le point $M'$ d'affixe $z'=i\bar z+1-i$. Quel est l'ensemble des points fixes de $t$ ?

- a) la droite d'équation $y=x+1$
- b) la droite d'équation $y=x-1$
- c) la droite d'équation $y=1-x$
- d) le seul point d'affixe $1$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On écrit $z=x+iy$ et $z'=x'+iy'$ puis on résout $z'=z$ en identifiant parties réelle et imaginaire.

### Corrigé

Avec $z=x+iy$ : $\bar z=x-iy$, donc $i\bar z=ix+y$ et
$$z'=(y+1)+i\,(x-1).$$
$M$ est fixe si et seulement si $x=y+1$ et $y=x-1$. Ces deux équations sont équivalentes : l'ensemble des points fixes est la droite $(\Delta)$ d'équation $y=x-1$.
Vérification avec un point de $(\Delta)$, par exemple $z=1$ : $z'=i+1-i=1$. Avec $z=0$ (hors de la droite) : $z'=1-i\neq0$.

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe en isolant $y$ dans $x=y+1$ ; le point $i$ n'est pas fixe : $t(i)=2-i$.
- **c)** on a confondu pente $1$ et pente $-1$ ; le point $2-i$ n'est pas fixe.
- **d)** on a vérifié que $1$ est fixe sans voir que les deux équations sont équivalentes : tous les points de la droite le sont, par exemple $-i$.

</details>

Avis : 

---

## 15. `cqc-position-relative-courbe-droite-moyenne-2` (séries BAC:A)

**Énoncé :**

Soit $h$ une fonction définie sur l'intervalle $]-\infty\,;2[$, de courbe représentative $(C_h)$. On note $(D')$ la droite d'équation $y = -3x+2$. Un calcul déjà effectué donne, pour tout $x$ de $]-\infty\,;2[$ :

$$h(x) - (-3x+2) = \dfrac{6}{2-x}$$

Quelle est la position relative de $(C_h)$ et de $(D')$ sur cet intervalle ?

- a) $(C_h)$ est strictement au-dessus de $(D')$ sur tout l'intervalle $]-\infty\,;2[$
- b) $(C_h)$ est strictement en dessous de $(D')$ sur tout l'intervalle $]-\infty\,;2[$
- c) $(C_h)$ et $(D')$ se coupent au point d'abscisse $2$
- d) $(C_h)$ est en dessous de $(D')$ sur $]-\infty\,;0[$ et au-dessus de $(D')$ sur $]0\,;2[$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand la fonction n'est définie que sur un intervalle restreint, on utilise cette information sur $x$ pour déterminer le signe du dénominateur, avant de conclure sur le signe global du quotient.

### Corrigé

Sur l'intervalle $]-\infty\,;2[$, tout réel $x$ vérifie $x < 2$, donc $2-x > 0$ : le dénominateur est strictement positif sur tout cet intervalle.

Le numérateur $6$ est une constante strictement positive. Un quotient de deux nombres strictement positifs est strictement positif, donc :
$$h(x) - (-3x+2) = \dfrac{6}{2-x} > 0 \text{ pour tout } x \in\, ]-\infty\,;2[$$

c'est-à-dire $h(x) > -3x+2$ sur tout cet intervalle.

**Conclusion** : sur $]-\infty\,;2[$, la courbe $(C_h)$ est toujours strictement au-dessus de la droite $(D')$. En dehors de cet intervalle, $h$ n'est pas définie : la question ne se pose pas.

### Pourquoi les autres réponses sont fausses

- **b)** on a cru que $2-x$ est négatif ; or $x<2$ donne $2-x>0$.
- **c)** $2$ est une valeur interdite : $h$ n'est pas définie en $2$ et la différence ne s'annule jamais.
- **d)** on a confondu le signe de la différence avec celui de $x$ ; le quotient reste strictement positif sur tout l'intervalle.

</details>

Avis : 

---

## 16. `cqc-primitives-elevee-5` (séries BAC:A BAC:C BAC:D BAC:E)

**Remarque du relecteur :** LIMITE : primitive de u'/u avec u affine (ln(3x+7)) pour la série A.

**Énoncé :**

Soit $f$ la fonction définie sur l'intervalle $\left]-\dfrac73;+\infty\right[$ par $f(x) = 2x + 3 + \dfrac{6}{3x+7}$. Quelle est la primitive $F$ de $f$ sur cet intervalle telle que $F(-2) = 5$ ?

- a) $F(x)=x^2+3x+2\ln(3x+7)+5$
- b) $F(x)=x^2+3x+6\ln(3x+7)+7$
- c) $F(x)=x^2+3x+2\ln(3x+7)+3$
- d) $F(x)=x^2+3x+2\ln(3x+7)+7$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On détermine d'abord la primitive générale $F_0(x)+C$ de $f$, en primitivant chaque terme par les formules usuelles. Puis, si l'énoncé impose une condition $F(x_0)=y_0$, on remplace $x$ par $x_0$ dans cette expression générale, on pose le résultat égal à $y_0$, et on résout l'équation du premier degré obtenue en $C$.

### Corrigé

**Primitive générale.** On primitive $f$ terme à terme sur $\left]-\dfrac73;+\infty\right[$, intervalle sur lequel $3x+7>0$.

Une primitive de $2x$ est $x^2$.

Une primitive de $3$ est $3x$.

Pour $\dfrac{6}{3x+7}$ : en posant $u(x)=3x+7$, on a $u'(x)=3$, donc $\dfrac{6}{3x+7}=2\times\dfrac{u'(x)}{u(x)}$, dont une primitive est $2\ln\lvert u(x)\rvert=2\ln(3x+7)$ (positif sur l'intervalle considéré).

La primitive générale de $f$ est donc :

$$F_0(x) = x^2+3x+2\ln(3x+7)+C, \quad C \in \mathbb{R}$$

**Détermination de $C$.** Le point $x_0=-2$ appartient bien à l'intervalle $\left]-\dfrac73;+\infty\right[$ puisque $-2>-\dfrac73\approx-2{,}33$. On calcule :

$$F(-2) = (-2)^2+3\times(-2)+2\ln\big(3\times(-2)+7\big)+C = 4-6+2\ln(1)+C = -2+C$$

car $\ln(1)=0$. Comme $F(-2)=5$ :

$$-2+C=5 \iff C=7$$

**Conclusion.** La primitive cherchée est :

$$F(x) = x^2+3x+2\ln(3x+7)+7$$

**Vérification** : $F'(x) = 2x+3+2\times\dfrac{3}{3x+7} = 2x+3+\dfrac{6}{3x+7} = f(x)$, et $F(-2)=4-6+2\ln1+7=4-6+0+7=5$. Conforme.

### Pourquoi les autres réponses sont fausses

- **a)** la valeur imposée $5$ a été prise pour la constante, sans calculer $F(-2)=-2+C$.
- **b)** on a primitivé $\dfrac{6}{3x+7}$ en $6\ln(3x+7)$ sans diviser par $3$ (dérivée de $3x+7$) ; sa dérivée n'est pas $f$.
- **c)** erreur de signe en résolvant $-2+C=5$ : on a écrit $C=5-2$.

</details>

Avis : 

---

## 17. `cqc-primitives-moyenne-2` (séries BAC:A BAC:C BAC:D BAC:E)

**Remarque du relecteur :** LIMITE : primitive de u'/u pour la série A.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x) = \dfrac{6x-5}{3x^2-5x+7}$ (le dénominateur ne s'annule jamais sur $\mathbb{R}$). Laquelle de ces fonctions est une primitive de $f$ sur $\mathbb{R}$ ?

- a) $F(x)=\ln(6x-5)$
- b) $F(x)=(6x-5)\ln(3x^2-5x+7)$
- c) $F(x)=\ln(3x^2-5x+7)$
- d) $F(x)=-\dfrac{1}{3x^2-5x+7}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'une fonction a la forme $\dfrac{u'}{u}$, où $u$ est une fonction dérivable ne s'annulant pas sur un intervalle $I$, une primitive sur $I$ est $\ln\lvert u\rvert$ (ou simplement $\ln u$ si $u$ reste positive sur $I$). Il faut toujours vérifier que le numérateur est exactement la dérivée du dénominateur avant d'appliquer cette formule.

### Corrigé

Posons $u(x) = 3x^2-5x+7$. Son discriminant vaut $\Delta = (-5)^2 - 4\times3\times7 = 25-84=-59 < 0$ et le coefficient dominant $3$ est positif, donc $u(x)>0$ pour tout $x$ réel. On calcule $u'(x) = 6x-5$, ce qui est exactement le numérateur de $f$. Donc $f = \dfrac{u'}{u}$, et comme $u$ reste strictement positive sur $\mathbb{R}$, une primitive de $f$ sur $\mathbb{R}$ est
$$F(x) = \ln(3x^2-5x+7).$$
Vérification : $F'(x) = \dfrac{6x-5}{3x^2-5x+7} = f(x)$.

### Pourquoi les autres réponses sont fausses

- **a)** on a pris le logarithme du seul numérateur ; de plus cette fonction n'est pas définie sur tout $\mathbb{R}$ (elle l'est seulement pour $x>\dfrac56$).
- **b)** on a multiplié le numérateur par le logarithme du dénominateur ; sa dérivée contient un terme en $\ln$ qui n'est pas dans $f$.
- **d)** c'est la primitive de $\dfrac{u'}{u^2}$ : on a confondu $\dfrac{u'}{u}$ avec $\dfrac{u'}{u^2}$.

</details>

Avis : 

---

## 18. `cqc-primitives-moyenne-3` (séries BAC:A BAC:C BAC:D BAC:E)

**Remarque du relecteur :** LIMITE : primitive de u'e^u pour la série A.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x) = (10x-1)e^{5x^2-x}$. Laquelle de ces fonctions est une primitive de $f$ sur $\mathbb{R}$ ?

- a) $F(x)=(10x-1)e^{5x^2-x}$
- b) $F(x)=e^{5x^2-x}$
- c) $F(x)=\dfrac{e^{5x^2-x}}{10x-1}$
- d) $F(x)=(5x^2-x)\,e^{5x^2-x}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'une fonction a la forme $u'e^u$, où $u$ est une fonction dérivable, une primitive est $e^u$ : il suffit de reconnaître, dans le facteur qui multiplie l'exponentielle, la dérivée exacte de l'exposant.

### Corrigé

Posons $u(x) = 5x^2-x$, donc $u'(x) = 10x-1$. On reconnaît alors :

$$f(x) = u'(x)\,e^{u(x)}$$

Une primitive de $f$ sur $\mathbb{R}$ est donc :

$$F(x) = e^{5x^2-x} + C, \quad C \in \mathbb{R}$$

**Vérification** : en dérivant $F$ comme une composée, $F'(x) = (10x-1)e^{5x^2-x} = f(x)$. Conforme.

### Pourquoi les autres réponses sont fausses

- **a)** c'est la fonction $f$ elle-même : l'exponentielle a été conservée telle quelle sans primitiver.
- **c)** on a appliqué la règle $\dfrac{e^{ax+b}}{a}$ des exponentielles affines, qui ne vaut pas pour un exposant du second degré.
- **d)** on a multiplié l'exponentielle par son exposant ; la dérivée de cette fonction contient un terme en $(5x^2-x)(10x-1)$ qui n'est pas dans $f$.

</details>

Avis : 

---

## 19. `cqc-probabilite-moyenne-0` (séries BAC:C BAC:D BAC:E)

**Remarque du relecteur :** La loi de E3 ne sert pas (z libre sur la droite) ; distracteur voulu, acceptable.

**Énoncé :**

Trois capteurs électroniques $E_1$, $E_2$, $E_3$ fonctionnent de manière indépendante et fournissent chacun, au hasard, la valeur $1$ ou la valeur $0$, avec :
$$P(E_1 = 1) = \frac{1}{5}, \qquad P(E_2 = 1) = \frac{1}{4}, \qquad P(E_3 = 1) = \frac{1}{3}$$
(et la valeur $0$ avec la probabilité complémentaire, dans chaque cas).

Dans un repère orthonormé de l'espace, on considère le point $M(E_1 + 1,\ E_2 + 2,\ E_3 - 1)$, dont les coordonnées dépendent ainsi du résultat des trois capteurs. Soit $(D)$ la droite passant par le point $A(1, 2, -1)$ et de vecteur directeur $\vec{u}(0, 0, 1)$.

Quelle est la probabilité que le point $M$ appartienne à la droite $(D)$ ?

- a) $\dfrac{1}{20}$
- b) $\dfrac{2}{5}$
- c) $\dfrac{3}{5}$
- d) $\dfrac{9}{20}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Un point $M(x, y, z)$ appartient à une droite $(D)$ passant par un point $A(x_A, y_A, z_A)$ et de vecteur directeur $\vec{u}(\alpha, \beta, \gamma)$ si et seulement si le vecteur $\overrightarrow{AM}$ est colinéaire à $\vec{u}$, c'est-à-dire s'il existe un réel $t$ tel que $x = x_A + \alpha t$, $y = y_A + \beta t$, $z = z_A + \gamma t$. Lorsqu'une composante de $\vec{u}$ est nulle, la coordonnée correspondante de $M$ est nécessairement égale à celle de $A$ ; lorsqu'une composante est non nulle, la coordonnée correspondante de $M$ est libre, car $t$ peut toujours être choisi pour l'atteindre.

### Corrigé

Le vecteur directeur de $(D)$ est $\vec{u}(0, 0, 1)$ : ses deux premières composantes sont nulles, la troisième ne l'est pas. D'après le rappel, $M(x, y, z)$ appartient à $(D)$ si et seulement si :
$$x = 1 \quad \text{et} \quad y = 2$$
la coordonnée $z$ pouvant prendre n'importe quelle valeur réelle (le paramètre $t$ s'ajuste toujours en conséquence).

Or $M = (E_1 + 1,\ E_2 + 2,\ E_3 - 1)$, donc :
- $x = 1 \iff E_1 + 1 = 1 \iff E_1 = 0$
- $y = 2 \iff E_2 + 2 = 2 \iff E_2 = 0$
- $z = E_3 - 1$ : aucune condition sur $E_3$, quelle que soit sa valeur.

L'événement « $M \in (D)$ » équivaut donc exactement à « $E_1 = 0$ et $E_2 = 0$ », les capteurs $E_1$ et $E_2$ étant indépendants. On a :
$$P(E_1 = 0) = 1 - \frac{1}{5} = \frac{4}{5}, \qquad P(E_2 = 0) = 1 - \frac{1}{4} = \frac{3}{4}$$

La probabilité cherchée est donc :
$$P(M \in (D)) = P(E_1 = 0) \times P(E_2 = 0) = \frac{4}{5} \times \frac{3}{4} = \frac{3}{5}$$

**Vérification** : le résultat $\dfrac{3}{5} = 0{,}6$ ne dépend logiquement que de $E_1$ et $E_2$, $E_3$ n'intervenant pas dans la condition ; en recalculant séparément $\left(1-\frac{1}{5}\right)$ et $\left(1-\frac{1}{4}\right)$ puis leur produit, on retrouve bien $\frac{4}{5}\times\frac{3}{4}=\frac{3}{5}$, ce qui confirme la cohérence du résultat.

### Pourquoi les autres réponses sont fausses

- **a)** on a multiplié $P(E_1=1)$ et $P(E_2=1)$ au lieu des probabilités de $E_1=0$ et $E_2=0$.
- **b)** on a ajouté la condition $E_3=0$ (probabilité $\dfrac23$), alors que la troisième coordonnée est libre.
- **d)** on a additionné les probabilités $\dfrac15+\dfrac14$ au lieu de multiplier celles de deux événements indépendants.

</details>

Avis : 

---

## 20. `cqc-produit-scalaire-tle-c-elevee-5` (séries BAC:C BAC:E)

**Énoncé :**

Dans l'espace muni d'un repère orthonormé direct, on donne $A(0\,;0\,;0)$, $B(1\,;2\,;2)$ et $C(2\,;1\,;-2)$. Quel est le produit vectoriel $\overrightarrow{AB}\wedge\overrightarrow{AC}$ ?

- a) $(-6\,;6\,;-3)$
- b) $(6\,;-6\,;3)$
- c) $(-6\,;-6\,;-3)$
- d) $(2\,;2\,;-4)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Un vecteur orthogonal à deux vecteurs non colinéaires s'obtient par leur produit vectoriel : $(a\,;b\,;c)\wedge(a'\,;b'\,;c')=(bc'-cb'\,;\,ca'-ac'\,;\,ab'-ba')$. On le vérifie avec deux produits scalaires nuls.

### Corrigé

$\overrightarrow{AB}(1\,;2\,;2)$ et $\overrightarrow{AC}(2\,;1\,;-2)$.
$$\overrightarrow{AB}\wedge\overrightarrow{AC}=(2\times(-2)-2\times1\,;\,2\times2-1\times(-2)\,;\,1\times1-2\times2)=(-6\,;6\,;-3).$$
Vérification : $(-6)\times1+6\times2+(-3)\times2=0$ et $(-6)\times2+6\times1+(-3)\times(-2)=0$. De plus $\overrightarrow{AB}\cdot\overrightarrow{AC}=0$, $AB=AC=3$ et $\left\lVert\overrightarrow{AB}\wedge\overrightarrow{AC}\right\rVert=\sqrt{36+36+9}=9$, soit le double de l'aire $\dfrac92$ du triangle rectangle isocèle $ABC$.

### Pourquoi les autres réponses sont fausses

- **b)** on a calculé $\overrightarrow{AC}\wedge\overrightarrow{AB}$ : le produit vectoriel change de signe quand on échange les facteurs.
- **c)** on a oublié le signe moins de la composante centrale, qui est $ca'-ac'$ et non $ac'-ca'$.
- **d)** on a multiplié les coordonnées une à une, ce qui n'est pas la formule du produit vectoriel (ce vecteur n'est pas orthogonal à $\overrightarrow{AB}$).

</details>

Avis : 

---

## 21. `cqc-recurrence-tle-c-moyenne-3` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** Série A indiquée : suites et raisonnement par récurrence hors programme de la série A ; correct pour C, D, E, TI.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $(u_n)$ la suite définie par $u_0=1$ et $u_{n+1}=3u_n+2$. Pour démontrer par récurrence que $u_n=2\times3^n-1$ pour tout entier naturel $n$, on suppose, pour un entier $n$ fixé, que $u_n=2\times3^n-1$. En utilisant la relation de récurrence, quelle expression obtient-on pour $u_{n+1}$ ?

- a) $2\times3^{n+1}+1$
- b) $2\times3^{n+1}-1$
- c) $6^{n+1}-1$
- d) $2\times3^{n+1}-5$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On démontre une formule explicite par récurrence : l'initialisation vérifie la formule au rang $0$ ; l'hérédité remplace $u_n$ par la formule dans la relation de récurrence et vérifie que le résultat a la forme attendue au rang $n+1$.

### Corrigé

**Initialisation.** $2\times3^0-1=2-1=1=u_0$ : la formule est vraie au rang $0$.

**Hérédité.** Si $u_n=2\times3^n-1$, alors
$$u_{n+1}=3u_n+2=3\left(2\times3^n-1\right)+2=2\times3^{n+1}-3+2=2\times3^{n+1}-1,$$
c'est la forme attendue au rang $n+1$.

**Conclusion.** Pour tout entier naturel $n$, $u_n=2\times3^n-1$.

### Pourquoi les autres réponses sont fausses

- **a)** le facteur $3$ n'est distribué que sur le premier terme de la parenthèse : on obtient $-1+2=+1$ au lieu de $-3+2=-1$.
- **c)** on multiplie les bases $3$ et $2$ au lieu de multiplier seulement les coefficients : $3\times2\times3^n=2\times3^{n+1}$, et non $6^{n+1}$.
- **d)** erreur de signe : on écrit $-3-2$ au lieu de $-3+2$.

</details>

Avis : 

---

## 22. `cqc-recurrence-tle-c-moyenne-4` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A.

**Remarque du relecteur :** Série A indiquée : raisonnement par récurrence et divisibilité (arithmétique) hors programme de la série A ; correct pour C, D, E, TI.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Pour démontrer par récurrence que, pour tout entier naturel $n$, le nombre $7^n-1$ est divisible par $6$, on suppose, pour un entier $n$ fixé, que $7^n-1=6k$ avec $k$ entier. Quelle est l'expression de $7^{n+1}-1$ en fonction de $k$ ?

- a) $42k-1$
- b) $6(k+1)$
- c) $6(7k+1)$
- d) $6(7k-1)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une propriété de divisibilité, on écrit l'hypothèse de récurrence sous la forme « $\ldots=6k$ avec $k$ entier », puis on exprime le terme du rang $n+1$ à l'aide du terme du rang $n$ pour faire apparaître un multiple de $6$.

### Corrigé

**Initialisation.** $7^0-1=0=6\times0$ : la propriété est vraie au rang $0$.

**Hérédité.** Si $7^n-1=6k$, alors $7^n=6k+1$ et
$$7^{n+1}-1=7\times7^n-1=7(6k+1)-1=42k+6=6(7k+1).$$
Comme $7k+1$ est un entier, $7^{n+1}-1$ est divisible par $6$.

**Conclusion.** Pour tout entier naturel $n$, $7^n-1$ est divisible par $6$.

### Pourquoi les autres réponses sont fausses

- **a)** on remplace $7^n$ par $6k$ au lieu de $6k+1$ (on oublie que $7^n=6k+1$).
- **b)** on ajoute simplement $6$ au rang suivant, comme dans une suite arithmétique, au lieu de multiplier par $7$.
- **d)** erreur de signe : $7(6k+1)-1=42k+6$, et non $42k-6$.

</details>

Avis : 

---

## 23. `cqc-suite-recurrente-tle-c-elevee-5` (séries BAC:C BAC:E)

**Énoncé :**

Soit $f$ la fonction définie sur $[0\,;+\infty[$ par $f(x)=\dfrac{2x+3}{x+2}$ et $(u_n)$ la suite définie par $u_0=0$ et $u_{n+1}=f(u_n)$. On admet que la suite $(u_n)$ converge. Quelle est sa limite ?

- a) $\sqrt3$
- b) $3$
- c) $2$
- d) $-\sqrt3$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Si une suite définie par $u_{n+1}=f(u_n)$ converge vers $\ell$ et si $f$ est continue en $\ell$, alors $\ell=f(\ell)$ : la limite est un point fixe de $f$. Les termes de la suite appartenant à $[0\,;+\infty[$, la limite est positive ou nulle.

### Corrigé

La suite converge vers un réel $\ell\geq0$ (ses termes sont positifs) et $f$ est continue sur $[0\,;+\infty[$, donc $\ell=f(\ell)$, soit $\ell(\ell+2)=2\ell+3$, c'est-à-dire $\ell^2=3$. Comme $\ell\geq0$, $\ell=\sqrt3$.

Vérification : $f(\sqrt3)=\dfrac{2\sqrt3+3}{\sqrt3+2}=\dfrac{\sqrt3(2+\sqrt3)}{\sqrt3+2}=\sqrt3$. Par ailleurs $f(x)=2-\dfrac1{x+2}$ est croissante, $u_0=0\leq\sqrt3$ entraîne $u_n\leq\sqrt3$ pour tout $n$, et $u_{n+1}-u_n=\dfrac{3-u_n^2}{u_n+2}\geq0$ : la suite est croissante et majorée, donc elle converge bien.

### Pourquoi les autres réponses sont fausses

- **b)** on lit « $\ell^2=3$ » comme « $\ell=3$ » ; or $f(3)=\dfrac95\neq3$, donc $3$ n'est pas un point fixe.
- **c)** on confond la limite de la suite avec la limite de $f$ en $+\infty$, qui vaut $2$ ; mais $f(2)=\dfrac74\neq2$.
- **d)** c'est l'autre solution de $\ell^2=3$, mais tous les termes de la suite sont positifs, donc sa limite est positive ou nulle.

</details>

Avis : 

---

## 24. `cqc-symetrie-centrale-faible-0` (séries BAC:C BAC:E)

**Remarque du relecteur :** Niveau Seconde, très facile pour une Terminale C/E.

**Énoncé :**

Dans un repère orthonormé, on donne le point $A(3\,;\,-2)$ et le point $K(1\,;\,4)$. Quelles sont les coordonnées du point $D$, symétrique du point $A$ par rapport au point $K$ ?

- a) $D(2\,;\,1)$
- b) $D(-1\,;\,10)$
- c) $D(-2\,;\,6)$
- d) $D(5\,;\,-8)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Dire que $D$ est le symétrique de $A$ par rapport à $K$ signifie que $K$ est le milieu du segment $[AD]$. On en tire les formules $x_D=2x_K-x_A$ et $y_D=2y_K-y_A$.

### Corrigé

*Abscisse de $D$.*
$$x_D=2x_K-x_A=2\times1-3=-1$$

*Ordonnée de $D$.*
$$y_D=2y_K-y_A=2\times4-(-2)=8+2=10$$

$$D(-1\,;\,10)$$

*Vérification.* Le milieu de $[AD]$ a pour coordonnées $\left(\dfrac{3+(-1)}{2}\,;\,\dfrac{-2+10}{2}\right)=(1\,;\,4)$, ce qui est bien $K$.

### Pourquoi les autres réponses sont fausses

- **a)** c'est le milieu de $[AK]$ : on confond le symétrique avec le milieu de $A$ et $K$.
- **c)** ce sont les coordonnées du vecteur $\overrightarrow{AK}$ ; il faut ajouter ce vecteur au point $K$ pour atteindre $D$.
- **d)** on a permuté les rôles de $A$ et $K$ (symétrique de $K$ par rapport à $A$) en calculant $2x_A-x_K$ et $2y_A-y_K$.

</details>

Avis : 

---

## 25. `cqc-theoreme-des-valeurs-intermediaires-tle-c-moyenne-2` (séries BAC:C BAC:D BAC:E)

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=x^3-3x+1$. L'équation $f(x)=0$ admet trois solutions réelles distinctes. Laquelle de ces propositions localise chacune des trois solutions dans un intervalle de longueur $1$ ?

- a) une dans $]-2\,;-1[$, une dans $]0\,;1[$ et une dans $]1\,;2[$
- b) une dans $]-1\,;0[$, une dans $]0\,;1[$ et une dans $]1\,;2[$
- c) une dans $]-2\,;-1[$, une dans $]-1\,;0[$ et une dans $]1\,;2[$
- d) une dans $]-2\,;-1[$, une dans $]0\,;1[$ et une dans $]2\,;3[$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On applique le théorème des valeurs intermédiaires sur plusieurs intervalles où $f$ change de signe, ce qui donne au moins une solution dans chacun. Un polynôme de degré $3$ ayant au plus $3$ racines, ces solutions sont les seules.

### Corrigé

$f$ est continue sur $\mathbb{R}$. Calculons quelques valeurs : $f(-2)=-1$, $f(-1)=3$, $f(0)=1$, $f(1)=-1$, $f(2)=3$.

- $f(-2)<0<f(-1)$ : une solution dans $]-2\,;-1[$.
- $f(0)>0>f(1)$ : une solution dans $]0\,;1[$.
- $f(1)<0<f(2)$ : une solution dans $]1\,;2[$.

Ces trois intervalles sont disjoints et l'équation a au plus trois solutions : chacune est dans l'un d'eux.

### Pourquoi les autres réponses sont fausses

- **b)** $f(-1)=3$ et $f(0)=1$ sont tous deux positifs : $f$ ne change pas de signe sur $]-1\,;0[$.
- **c)** $f(-1)=3$ et $f(0)=1$ sont tous deux positifs : aucune solution dans $]-1\,;0[$, alors que $f$ change de signe sur $]0\,;1[$.
- **d)** $f(2)=3$ et $f(3)=19$ sont tous deux positifs : aucune solution dans $]2\,;3[$, alors que $f$ change de signe sur $]1\,;2[$.

</details>

Avis : 

---

## 26. `cqc-theoreme-des-valeurs-intermediaires-tle-c-moyenne-3` (séries BAC:C BAC:D BAC:E)

**Remarque du relecteur :** VOCABULAIRE : la fonction g est introduite mais l'équation est posée sous la forme cos x = x ; écrire « l'équation g(x)=0 » pour la cohérence.

**Énoncé :**

Soit $g(x)=\cos x-x$ sur $[0\,;1]$ (l'angle est en radians). On admet que l'équation $\cos x=x$ admet une unique solution $\alpha$ dans $[0\,;1]$. Quel est l'encadrement de $\alpha$ d'amplitude $0{,}1$ ?

- a) $0{,}6<\alpha<0{,}7$
- b) $0{,}8<\alpha<0{,}9$
- c) $0{,}9<\alpha<1$
- d) $0{,}7<\alpha<0{,}8$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

$g$ est strictement décroissante sur $[0\,;1]$ : l'unique solution se situe entre deux valeurs consécutives où $g$ change de signe. On affine l'encadrement par dichotomie, la calculatrice étant réglée en radians.

### Corrigé

$g(0{,}7)=\cos0{,}7-0{,}7\approx0{,}765-0{,}7=0{,}065>0$ et $g(0{,}8)=\cos0{,}8-0{,}8\approx0{,}697-0{,}8=-0{,}103<0$. Comme $g$ est strictement décroissante, elle change de signe entre $0{,}7$ et $0{,}8$ : $0{,}7<\alpha<0{,}8$.

### Pourquoi les autres réponses sont fausses

- **a)** $g(0{,}6)$ et $g(0{,}7)$ sont tous deux positifs : $g$ ne change pas de signe sur cet intervalle.
- **b)** $g(0{,}8)$ et $g(0{,}9)$ sont tous deux négatifs : $g$ ne change pas de signe sur cet intervalle.
- **c)** résultat obtenu avec une calculatrice réglée en degrés ($\cos0{,}9^\circ\approx1$), alors que l'énoncé précise que l'angle est en radians.

</details>

Avis : 

---

## 27. `cqc-theoreme-du-rang-tle-c-elevee-5` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : endomorphisme de R^3 et déterminant 3x3 avec paramètre, à vérifier selon le programme C/E en vigueur.

**Énoncé :**

Pour tout réel $m$, on note $f_m$ l'endomorphisme de $\mathbb{R}^3$ défini par $f_m(x\,;y\,;z)=(x+y+mz\,;\,x+my+z\,;\,mx+y+z)$. Pour quelles valeurs de $m$ l'endomorphisme $f_m$ n'est-il pas bijectif ?

- a) $m=1$ ou $m=2$
- b) $m=-1$ ou $m=2$
- c) $m=1$ ou $m=-2$
- d) $m=1$ uniquement

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Un endomorphisme de $\mathbb{R}^3$ est bijectif si et seulement si son rang vaut $3$, c'est-à-dire si et seulement si le déterminant des vecteurs $f_m(\vec\imath)$, $f_m(\vec\jmath)$, $f_m(\vec k)$ est non nul. Le théorème du rang ($\dim\ker f_m+\operatorname{rg}f_m=3$) permet ensuite de préciser le noyau.

### Corrigé

Les vecteurs images de la base canonique sont $f_m(\vec\imath)=(1\,;1\,;m)$, $f_m(\vec\jmath)=(1\,;m\,;1)$ et $f_m(\vec k)=(m\,;1\,;1)$. Leur déterminant est
$$D_m=\begin{vmatrix}1&1&m\\1&m&1\\m&1&1\end{vmatrix}=1\,(m-1)-1\,(1-m)+m\,(1-m^2)=(m-1)\big[2-m(m+1)\big]=-(m-1)^2(m+2).$$
$f_m$ n'est pas bijectif si et seulement si $D_m=0$, soit $m=1$ ou $m=-2$.

Pour préciser : si $m=1$, les trois coordonnées de $f_1(x\,;y\,;z)$ valent toutes $x+y+z$, donc $\operatorname{rg}f_1=1$ et $\dim\ker f_1=2$ ; si $m=-2$, $\operatorname{rg}f_{-2}=2$ et $\ker f_{-2}$ est la droite engendrée par $(1\,;1\,;1)$.

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe sur le facteur $(m+2)$ : le déterminant s'annule pour $m=-2$, et non pour $m=2$ (pour $m=2$, $D_2=-4\neq0$).
- **b)** les deux racines sont prises de signe contraire : $D_{-1}=-4\neq0$ et $D_2=-4\neq0$, donc $f_{-1}$ et $f_2$ sont bijectifs.
- **d)** on ne retient que la racine double $m=1$ du facteur $(m-1)^2$ et on oublie le facteur $(m+2)$, qui s'annule pour $m=-2$.

</details>

Avis : 

---

## 28. `cqc-theoreme-du-rang-tle-c-moyenne-2` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : endomorphisme de R^3 et noyau, à vérifier selon le programme C/E en vigueur.

**Énoncé :**

Soit $f$ l'endomorphisme de $\mathbb{R}^3$ défini par $f(x\,;y\,;z)=(x+y\,;\,y+z\,;\,x-z)$. Quel vecteur engendre le noyau de $f$ ?

- a) $(1\,;1\,;1)$
- b) $(1\,;-1\,;1)$
- c) $(1\,;-1\,;-1)$
- d) $(1\,;1\,;-1)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Le noyau est l'ensemble des vecteurs $(x\,;y\,;z)$ dont l'image est nulle : on résout le système $f(x\,;y\,;z)=(0\,;0\,;0)$. Le théorème du rang permet ensuite de contrôler le résultat : $\dim\ker f+\operatorname{rg}f=3$.

### Corrigé

$f(x\,;y\,;z)=(0\,;0\,;0)$ équivaut à $x+y=0$, $y+z=0$, $x-z=0$, soit $y=-x$ et $z=-y=x$ (la troisième équation en découle). Le noyau est $\{(x\,;-x\,;x)\}=\operatorname{Vect}\big((1\,;-1\,;1)\big)$ : c'est une droite, de dimension $1$.

Contrôle : $f(1\,;-1\,;1)=(0\,;0\,;0)$, et l'image est un plan, $1+2=3=\dim\mathbb{R}^3$.

### Pourquoi les autres réponses sont fausses

- **a)** $f(1\,;1\,;1)=(2\,;2\,;0)\neq(0\,;0\,;0)$ : erreur de signe en résolvant $x+y=0$ et $y+z=0$.
- **c)** $f(1\,;-1\,;-1)=(0\,;-2\,;2)\neq(0\,;0\,;0)$ : on a mal reporté $z=-y$ dans l'équation $x-z=0$.
- **d)** $f(1\,;1\,;-1)=(2\,;0\,;2)\neq(0\,;0\,;0)$ : la première équation $x+y=0$ n'est pas vérifiée.

</details>

Avis : 

---

## 29. `cqc-theoreme-du-rang-tle-c-moyenne-3` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : endomorphisme et noyau, à vérifier selon le programme C/E en vigueur.

**Énoncé :**

Soit $f$ l'endomorphisme de $\mathbb{R}^2$ défini par $f(x\,;y)=(x-2y\,;\,-2x+4y)$. Quel vecteur engendre le noyau de $f$ ?

- a) $(2\,;1)$
- b) $(1\,;-2)$
- c) $(1\,;2)$
- d) $(2\,;-1)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Les vecteurs du noyau sont ceux dont l'image est nulle : on résout $f(x\,;y)=(0\,;0)$. L'image est engendrée par $f(\vec\imath)$ et $f(\vec\jmath)$.

### Corrigé

Les équations $x-2y=0$ et $-2x+4y=0$ sont la même équation $x=2y$ : $\ker f=\operatorname{Vect}\big((2\,;1)\big)$, de dimension $1$.

Par ailleurs $f(\vec\imath)=(1\,;-2)$ et $f(\vec\jmath)=(-2\,;4)=-2f(\vec\imath)$, donc l'image est la droite engendrée par $(1\,;-2)$ : $\operatorname{rg}f=1$ et $1+1=2=\dim\mathbb{R}^2$ (théorème du rang).

### Pourquoi les autres réponses sont fausses

- **b)** ce vecteur engendre l'image de $f$ (c'est $f(\vec\imath)$), pas le noyau : $f(1\,;-2)=(5\,;-10)\neq(0\,;0)$.
- **c)** on échange les coordonnées en résolvant $x=2y$ : $f(1\,;2)=(-3\,;6)\neq(0\,;0)$.
- **d)** erreur de signe : $f(2\,;-1)=(4\,;-8)\neq(0\,;0)$, car $x=2y$ impose des coordonnées de même signe.

</details>

Avis : 

---

## 30. `cqc-vecteurs-colineaires-tle-c-moyenne-2` (séries BAC:C BAC:E)

**Remarque du relecteur :** Niveau Seconde, très facile pour une Terminale C/E.

**Énoncé :**

Dans un repère du plan, on donne $A(-1\,;2)$, $B(1\,;3)$ et le point $D(m\,;7)$, où $m$ est un réel. Pour quelle valeur de $m$ les points $A$, $B$ et $D$ sont-ils alignés ?

- a) $m=11$
- b) $m=9$
- c) $m=\dfrac32$
- d) $m=-9$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Trois points $A$, $B$, $D$ sont alignés si et seulement si les vecteurs $\overrightarrow{AB}$ et $\overrightarrow{AD}$ sont colinéaires, c'est-à-dire si leur déterminant est nul. Ici l'inconnue apparaît de façon linéaire dans ce déterminant.

### Corrigé

$\overrightarrow{AB}(2\,;1)$ et $\overrightarrow{AD}(m+1\,;5)$.
$$\det(\overrightarrow{AB},\overrightarrow{AD})=2\times5-1\times(m+1)=9-m.$$
Ce déterminant est nul si et seulement si $m=9$, soit $D(9\,;7)$.
Contrôle : la droite $(AB)$ a pour coefficient directeur $\dfrac12$ et $3+\dfrac12\times(9-1)=7$.

### Pourquoi les autres réponses sont fausses

- **a)** $\overrightarrow{AD}$ a été calculé avec $m-1$ au lieu de $m+1$ (oubli du signe de l'abscisse de $A$), ce qui donne $11-m=0$.
- **c)** les produits en croix du déterminant sont écrits dans le mauvais sens : $2(m+1)-1\times5=0$ donne $m=\dfrac32$.
- **d)** erreur de signe en résolvant $9-m=0$ : on écrit $9+m=0$.

</details>

Avis : 

---

## 31. `cqc-vecteurs-colineaires-tle-c-moyenne-4` (séries BAC:C BAC:E)

**Remarque du relecteur :** Niveau Seconde, très facile pour une Terminale C/E.

**Énoncé :**

Dans un repère orthonormé du plan, on donne $A(0\,;0)$, $B(3\,;1)$, $C(1\,;2)$ et $D(7\,;4)$. Quelle est la position relative des droites $(AB)$ et $(CD)$ ?

- a) Les droites sont parallèles et distinctes.
- b) Les droites sont confondues.
- c) Les droites sont sécantes et perpendiculaires.
- d) Les droites sont sécantes et non perpendiculaires.

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Deux droites sont parallèles si leurs vecteurs directeurs sont colinéaires. Elles sont confondues si de plus un point de l'une appartient à l'autre, ce qu'on teste avec un déterminant supplémentaire.

### Corrigé

$\overrightarrow{AB}(3\,;1)$ et $\overrightarrow{CD}(6\,;2)=2\overrightarrow{AB}$ : les vecteurs directeurs sont colinéaires, donc $(AB)\parallel(CD)$.

Elles ne sont pas confondues : $\overrightarrow{AC}(1\,;2)$ et $\det(\overrightarrow{AB},\overrightarrow{AC})=3\times2-1\times1=5\neq0$, donc $C\notin(AB)$. Les droites sont parallèles et distinctes.

### Pourquoi les autres réponses sont fausses

- **b)** les droites sont bien parallèles, mais $C$ n'appartient pas à $(AB)$ puisque $\det(\overrightarrow{AB},\overrightarrow{AC})=5\neq0$ : le test d'appartenance a été oublié.
- **c)** la colinéarité de $\overrightarrow{AB}$ et $\overrightarrow{CD}$ est confondue avec l'orthogonalité ; or $\overrightarrow{AB}\cdot\overrightarrow{CD}=3\times6+1\times2=20\neq0$.
- **d)** comme $\overrightarrow{CD}=2\overrightarrow{AB}$, les vecteurs directeurs sont colinéaires et les droites ne peuvent pas être sécantes.

</details>

Avis : 

---

## 32. `cqc-ecriture-complexe-tle-c-faible-0` (séries BAC:C BAC:D BAC:E BAC:TI)

**Énoncé :**

Le plan complexe est rapporté à un repère orthonormé direct. Quelle est l'écriture complexe $z'=az+b$ de l'homothétie $h$ de centre $\Omega(1+i)$ et de rapport $2$ ?

- a) $z'=2z+1+i$
- b) $z'=2z+2+2i$
- c) $z'=2z-1-i$
- d) $z'=2z-3-3i$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

L'homothétie de centre $\Omega$ d'affixe $\omega$ et de rapport $k$ est caractérisée par $z'-\omega=k(z-\omega)$. On développe pour obtenir la forme $z'=kz+(1-k)\omega$.

### Corrigé

$z'-(1+i)=2\big(z-(1+i)\big)$, donc
$$z'=2z-2(1+i)+(1+i)=2z-1-i.$$
Contrôle : le centre est invariant, car $2(1+i)-1-i=1+i$.

### Pourquoi les autres réponses sont fausses

- **a)** le terme constant est calculé avec $(k-1)\omega$ au lieu de $(1-k)\omega$ : le centre de cette homothétie serait $-1-i$ et non $1+i$.
- **b)** le terme constant est pris égal à $k\omega$ : on oublie de retrancher $\omega$ dans $z'-\omega=k(z-\omega)$ ; le centre serait $-2-2i$.
- **d)** le terme constant est pris égal à $-(k+1)\omega$ : erreur de signe dans le développement ; le centre serait $3+3i$.

</details>

Avis : 

---

## 33. `cqc-equation-cartesienne-d-un-plan-tle-c-faible-0` (séries BAC:C BAC:E)

**Énoncé :**

Dans l'espace muni d'un repère orthonormé, quelle est une équation cartésienne du plan $(P)$ passant par $A(1\,;0\,;0)$ et de vecteur normal $\vec n(2\,;-1\,;3)$ ?

- a) $2x-y+3z+2=0$
- b) $2x-y+3z=0$
- c) $2x-y+3z-2=0$
- d) $2x-y+3z-1=0$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Un plan de vecteur normal $\vec n(a\,;b\,;c)$ a une équation de la forme $ax+by+cz+d=0$. On détermine $d$ en écrivant que le point donné appartient au plan.

### Corrigé

Une équation de $(P)$ est $2x-y+3z+d=0$. Comme $A(1\,;0\,;0)\in(P)$ : $2\times1-0+0+d=0$, donc $d=-2$.
$$(P):\ 2x-y+3z-2=0.$$

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe sur $d$ : en remplaçant les coordonnées de $A$ on trouve $2+d=0$, donc $d=-2$ et non $2$ ($A$ ne vérifie pas cette équation).
- **b)** le terme constant $d$ est oublié : le plan passe alors par l'origine et non par $A$.
- **d)** l'abscisse de $A$ est utilisée sans le coefficient $2$ : on écrit $1+d=0$ au lieu de $2\times1+d=0$.

</details>

Avis : 

---

## 34. `cqc-equation-differentielle-lineaire-tle-c-elevee-5` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : second membre non nul sans indication sur la forme de la solution particulière ; faisable par vérification des choix, mais au bord du programme (habituellement guidé).

**Énoncé :**

On considère l'équation différentielle $(E):\ y''-y'-2y=4x$. Quelle est la solution de $(E)$ vérifiant $y(0)=0$ et $y'(0)=1$ ?

- a) $y(x)=\dfrac23e^{2x}-\dfrac53e^{-x}-2x+1$
- b) $y(x)=\dfrac43e^{2x}-\dfrac13e^{-x}-2x-1$
- c) $y(x)=-e^{-x}-2x+1$
- d) $y(x)=-\dfrac43e^{-2x}+\dfrac13e^{x}-2x+1$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

La solution générale d'une équation linéaire avec second membre est la somme d'une solution particulière et de la solution générale de l'équation homogène. Pour un second membre polynomial de degré $1$, on cherche une solution particulière polynomiale de degré $1$ et on identifie les coefficients.

### Corrigé

L'équation caractéristique $r^2-r-2=0$ se factorise en $(r-2)(r+1)=0$ : les solutions de l'équation homogène sont $Ae^{2x}+Be^{-x}$.

Pour $y_p=ax+b$ : $y_p'=a$ et $y_p''=0$, donc $y_p''-y_p'-2y_p=-a-2ax-2b$. Pour que ce soit égal à $4x$ : $-2a=4$ et $-a-2b=0$, soit $a=-2$ et $b=1$. Donc $y_p(x)=-2x+1$.
Contrôle : $0-(-2)-2(-2x+1)=2+4x-2=4x$.

La solution générale de $(E)$ est $y(x)=Ae^{2x}+Be^{-x}-2x+1$. Avec $y(0)=0$ : $A+B+1=0$. Avec $y'(x)=2Ae^{2x}-Be^{-x}-2$ et $y'(0)=1$ : $2A-B-2=1$, soit $2A-B=3$. En additionnant $A+B=-1$ et $2A-B=3$ : $3A=2$, donc $A=\dfrac23$ et $B=-\dfrac53$.
$$y(x)=\dfrac23e^{2x}-\dfrac53e^{-x}-2x+1.$$

### Pourquoi les autres réponses sont fausses

- **b)** la solution particulière est prise égale à $-2x-1$ (erreur de signe sur $b$ dans $-a-2b=0$) : ce n'est pas une solution de $(E)$.
- **c)** le terme $-2$ provenant de la dérivée de la solution particulière est oublié dans $y'(0)$ : on écrit $2A-B=1$, d'où $A=0$ et $B=-1$ ; mais la fonction obtenue a pour dérivée en $0$ : $1-2=-1\neq1$.
- **d)** les racines de l'équation caractéristique sont prises avec le mauvais signe ($-2$ et $1$ au lieu de $2$ et $-1$) : la fonction proposée ne vérifie pas $(E)$.

</details>

Avis : 

---

## 35. `cqc-equation-differentielle-lineaire-tle-c-faible-0` (séries BAC:C BAC:E)

**Énoncé :**

On considère l'équation différentielle $(E):\ y'+2y=0$ sur $\mathbb{R}$. Quelle est la solution de $(E)$ vérifiant $y(0)=3$ ?

- a) $y(x)=3e^{2x}$
- b) $y(x)=3e^{-2x}$
- c) $y(x)=3e^{-x/2}$
- d) $y(x)=e^{-2x}+2$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Les solutions de $y'=ay$ sur $\mathbb{R}$ sont les fonctions $y(x)=Ce^{ax}$ avec $C\in\mathbb{R}$. La condition initiale $y(x_0)=y_0$ détermine la constante $C$.

### Corrigé

$y'+2y=0\iff y'=-2y$ : les solutions sont $y(x)=Ce^{-2x}$, $C\in\mathbb{R}$. La condition $y(0)=3$ donne $C=3$ :
$$y(x)=3e^{-2x}.$$

### Pourquoi les autres réponses sont fausses

- **a)** le signe de l'exposant est oublié : $y'=-2y$ et non $y'=2y$ ; la fonction $3e^{2x}$ vérifie $y'-2y=0$.
- **c)** l'exposant est calculé comme $-\dfrac12x$ au lieu de $-2x$ (le coefficient est divisé au lieu d'être conservé).
- **d)** une constante additive remplace le facteur : $e^{-2x}+2$ prend la valeur $3$ en $0$, mais ne vérifie pas $y'+2y=0$ (on obtient $4$).

</details>

Avis : 

---


---

# Lot : b1-bac-vague-5-maths

## Vague 5 Maths BAC (anciennes questions « Tle » par série) : 69 QCM à faire relire par l'enseignant (campagne B1)

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

