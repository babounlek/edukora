# Vague 4 Maths BAC (questions posées au BAC seulement) : 35 QCM à faire relire par l'enseignant (campagne B1)

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

