# Vague 2 Maths BAC : 48 QCM à faire relire par l'enseignant (campagne B1)

Date : 2026-10-31. Sur 90 QCM convertis (123 questions étudiées, 33 écartées), **48** vous sont soumis : ceux que le relecteur aveugle a assortis d'une remarque, ceux dont la méthode ou la question a été modifiée, et un tirage de 20 autres. Aucun n'est en ligne. Les 90 ont été résolus à l'aveugle (90 accords sur 91 ; le 91ᵉ, sous-espace de R⁴, a été retiré).

## Points généraux à trancher (valent pour plusieurs questions)

1. **Arithmétique en série E ?** Les congruences et équations diophantiennes ont été écartées pour la série E (arithmétique prise comme réservée à C et TI). Si elle est au programme de E, 6 questions redeviennent convertibles.
2. **Coniques en série D ?** Ellipse et excentricité écartées pour D. Même question.
3. **Similitudes indirectes en série C ?** Écartées : seules les similitudes directes sont au programme de C dans notre référentiel.
4. **Série A : fonction a^x (base 3), branches paraboliques, prolongement par continuité, loi binomiale à plusieurs termes ?** Plusieurs questions posées en série A utilisent ces notions : à garder ou à retirer de la série A ?
5. **« Produit mixte »** : le terme figure-t-il dans les manuels de Terminale C/E ?
6. **Endomorphismes de R³ (noyau, image)** en Terminale C.
7. **Équations différentielles du second ordre en série TI.**
8. **Items « forme algébrique d'un quotient »** (nombres complexes) : ils portent la série A alors qu'elle n'a pas de complexes : retirer A de leur cursus ?

Pour chaque question : **OK**, **à corriger** (dire quoi), **à retirer**, ou **retirer la série X**.

## 1. `cqc-arithmetique-dans-z-elevee-0` (séries C)

**Énoncé :**

Quelle liste donne exactement tous les couples $(a,b)$ d'entiers naturels non nuls, avec $a \leqslant b$, vérifiant simultanément $\mathrm{pgcd}(a,b) = 15$ et $\mathrm{ppcm}(a,b) = 1\,575$ ?

- a) $(15\,;\,105)$ seulement
- b) $(45\,;\,525)$, $(75\,;\,315)$ et $(105\,;\,225)$
- c) $(15\,;\,1\,575)$, $(45\,;\,525)$, $(75\,;\,315)$ et $(105\,;\,225)$
- d) $(1\,;\,105)$, $(3\,;\,35)$, $(5\,;\,21)$ et $(7\,;\,15)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsque $\mathrm{pgcd}(a,b) = d$, on peut écrire $a = da'$ et $b = db'$ avec $a'$ et $b'$ premiers entre eux. La relation $\mathrm{pgcd}(a,b) \times \mathrm{ppcm}(a,b) = a \times b$ devient alors $\mathrm{ppcm}(a,b) = d \times a' \times b'$. Trouver tous les couples de pgcd et de ppcm imposés revient donc à décomposer l'entier $\mathrm{ppcm}(a,b)/d$ en tous ses couples de facteurs premiers entre eux, à l'aide de sa décomposition en facteurs premiers.

### Corrigé

Posons $d = 15$, et écrivons $a = 15a'$, $b = 15b'$ avec $\mathrm{pgcd}(a',b') = 1$.

D'après la relation $\mathrm{pgcd}(a,b) \times \mathrm{ppcm}(a,b) = a \times b$, on a $\mathrm{ppcm}(a,b) = 15 \times a' \times b'$. Ainsi :
$$15 \times a' \times b' = 1\,575 \iff a' \times b' = \dfrac{1\,575}{15} = 105.$$

Or $105 = 3 \times 5 \times 7$ est un produit de trois facteurs premiers **distincts**, chacun à la puissance $1$. Deux facteurs $a'$ et $b'$ dont le produit vaut $105$ sont donc automatiquement premiers entre eux : un même facteur premier ne peut se retrouver des deux côtés.

Les diviseurs positifs de $105$ sont $1$, $3$, $5$, $7$, $15$, $21$, $35$ et $105$. En les groupant par paires $(a', b')$ avec $a' \leqslant b'$ et $a' \times b' = 105$ :
$$\{1\,;\,105\}, \quad \{3\,;\,35\}, \quad \{5\,;\,21\}, \quad \{7\,;\,15\}.$$

Les quatre couples $(a,b) = (15a'\,;\,15b')$ conviennent donc :
$$(15\,;\,1\,575), \quad (45\,;\,525), \quad (75\,;\,315), \quad (105\,;\,225).$$

Vérification pour $(75\,;\,315)$ : $315 = 4 \times 75 + 15$ puis $75 = 5 \times 15 + 0$, donc $\mathrm{pgcd}(75\,;\,315) = 15$ ; et $\mathrm{ppcm}(75\,;\,315) = \dfrac{75 \times 315}{15} = 1\,575$.

La bonne réponse est la liste des quatre couples $(15\,;\,1\,575)$, $(45\,;\,525)$, $(75\,;\,315)$ et $(105\,;\,225)$.

### Pourquoi les autres réponses sont fausses

- **a)** Confond le ppcm avec le produit $ab$ : $225\,a'b' = 1\,575$ donne $a'b' = 7$, d'où le seul couple $(15\,;\,105)$, dont le ppcm vaut $105$ et non $1\,575$.
- **b)** Oublie la décomposition $105 = 1 \times 105$ (cas $a' = 1$), donc le couple $(15\,;\,1\,575)$.
- **d)** Donne les couples $(a',b')$ sans les multiplier par $15$ : leur pgcd vaut $1$, et non $15$.

</details>

Avis : 

---

## 2. `cqc-existence-elevee-0` (séries C/D/E/TI)

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x) = x^3 - 3x - 1$.

Combien de solutions réelles l'équation $f(x) = 0$ admet-elle, et où sont-elles situées ?

- a) Exactement une solution, située dans $]1;+\infty[$
- b) Exactement trois solutions : une dans $]-\infty;-1[$, une dans $]-1;1[$ et une dans $]1;+\infty[$
- c) Exactement deux solutions : une dans $]-1;1[$ et une dans $]1;+\infty[$
- d) Exactement trois solutions, toutes dans $]0;+\infty[$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour dénombrer les solutions réelles d'une équation polynomiale, on étudie les variations de la fonction associée afin de repérer des intervalles de stricte monotonie, puis on applique le théorème de la bijection sur chacun de ces intervalles (continuité, stricte monotonie, changement de signe aux bornes, y compris aux limites infinies). Chaque intervalle vérifiant ces trois conditions fournit exactement une solution.

### Corrigé

La fonction $f$ est dérivable sur $\mathbb{R}$ comme fonction polynôme, et
$$f'(x) = 3x^2 - 3 = 3(x-1)(x+1)$$
On a $f'(x) > 0$ pour $x < -1$ ou $x > 1$, et $f'(x) < 0$ pour $-1 < x < 1$. La fonction $f$ est donc strictement croissante sur $]-\infty;-1]$, strictement décroissante sur $[-1;1]$, puis strictement croissante sur $[1;+\infty[$.

Valeurs remarquables :
$$f(-1) = -1+3-1 = 1, \qquad f(1) = 1-3-1 = -3$$
De plus, $\displaystyle\lim_{x\to-\infty} f(x) = -\infty$ et $\displaystyle\lim_{x\to+\infty} f(x) = +\infty$.

**Sur $]-\infty;-1]$** : $f$ est continue, strictement croissante, de $-\infty$ à $f(-1) = 1 > 0$ : une unique solution $\alpha_1 \in\, ]-\infty;-1[$.

**Sur $[-1;1]$** : $f$ est continue, strictement décroissante, de $f(-1) = 1 > 0$ à $f(1) = -3 < 0$ : une unique solution $\alpha_2 \in\, ]-1;1[$.

**Sur $[1;+\infty[$** : $f$ est continue, strictement croissante, de $f(1) = -3 < 0$ à $+\infty$ : une unique solution $\alpha_3 \in\, ]1;+\infty[$.

Ces trois intervalles étant disjoints, l'équation admet trois solutions distinctes, et pas davantage puisque $f$ est un polynôme de degré $3$. L'équation $f(x) = 0$ admet donc exactement trois solutions réelles : une dans $]-\infty;-1[$, une dans $]-1;1[$ et une dans $]1;+\infty[$.

### Pourquoi les autres réponses sont fausses

- **a)** Ne repère que le changement de signe entre $f(1) = -3$ et $+\infty$, sans étudier les variations de $f$ sur $]-\infty;1]$.
- **c)** Oublie l'intervalle $]-\infty;-1]$, sur lequel $f$ passe pourtant de $-\infty$ à $f(-1) = 1$.
- **d)** $f(-1) = 1 > 0$ et $f(0) = -1 < 0$ : une solution est négative (entre $-1$ et $0$), et $\alpha_1 < -1$ l'est aussi.

</details>

Avis : 

---

## 3. `cqc-factorisation-par-difference-de-carres-faible-0` (séries A)

**Remarque du relecteur :** Question de niveau collège, très facile pour un BAC A.

**Énoncé :**

On considère l'expression $A(x) = 25x^2 - 4$, définie pour tout nombre réel $x$.

Quelle est la factorisation de $A(x)$ en produit de deux facteurs du premier degré ?

- a) $(5x-2)^2$
- b) $(25x-2)(25x+2)$
- c) $(5x-2)(5x+2)$
- d) $(5x-4)(5x+4)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour factoriser une expression de la forme $a^2-b^2$ (une différence de deux carrés), on utilise l'identité remarquable $a^2-b^2=(a-b)(a+b)$. Il faut d'abord reconnaître chaque terme comme le carré d'une expression plus simple.

### Corrigé

On remarque que $25x^2=(5x)^2$ et que $4=2^2$. L'expression $A(x)$ est donc une différence de deux carrés, avec $a=5x$ et $b=2$ :
$$A(x)=25x^2-4=(5x)^2-2^2=(5x-2)(5x+2).$$

Vérification pour $x=3$ : $(15-2)(15+2)=13\times17=221$ et $25\times9-4=225-4=221$.

### Pourquoi les autres réponses sont fausses

- **a)** Confond avec l'identité $(a-b)^2=a^2-2ab+b^2$ : $(5x-2)^2=25x^2-20x+4$.
- **b)** Prend $25x^2$ pour le carré de $25x$ : $(25x-2)(25x+2)=625x^2-4$.
- **d)** Prend $4$ pour le carré de $4$ : $(5x-4)(5x+4)=25x^2-16$.

</details>

Avis : 

---

## 4. `cqc-involution-elevee-0` (séries C/E)

**Énoncé :**

Le plan est muni d'un repère $(O,\vec\imath,\vec\jmath)$. On considère la transformation ponctuelle $g$ qui, à tout point $M(x,y)$, associe le point $M'(x',y')$ défini par :
$$x' = \dfrac{-3x+4y}{5} - 2, \qquad y' = \dfrac{4x+3y}{5} + 1$$

Soit $B$ le point de coordonnées $(3\,;\,4)$. Quelles sont les coordonnées du point $P$ tel que $g(P) = B$ ?

- a) $\left(\dfrac{17}{5}\,;\,\dfrac{19}{5}\right)$
- b) $\left(\dfrac{7}{5}\,;\,\dfrac{24}{5}\right)$
- c) $\left(-\dfrac{3}{5}\,;\,\dfrac{19}{5}\right)$
- d) $\left(-\dfrac{3}{5}\,;\,\dfrac{29}{5}\right)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Lorsqu'une transformation ponctuelle $g$ est involutive ($g \circ g = \mathrm{id}$), elle est égale à sa propre réciproque : $g^{-1} = g$. Ainsi, si $g(P) = B$, alors $P = g^{-1}(B) = g(B)$ : il suffit d'appliquer les formules de $g$ au point $B$, sans résoudre le système linéaire qui donnerait $x,y$ en fonction de $x',y'$.

### Corrigé
**$g$ est involutive.** Soit $M(x,y)$, $M'(x',y') = g(M)$ et $M''(x'',y'') = g(M')$, donc $x'' = \dfrac{-3x'+4y'}{5}-2$ et $y'' = \dfrac{4x'+3y'}{5}+1$.
$$-3x'+4y' = \dfrac{9x-12y}{5}+6+\dfrac{16x+12y}{5}+4 = 5x+10, \quad \text{donc } x'' = x+2-2 = x.$$
$$4x'+3y' = \dfrac{-12x+16y}{5}-8+\dfrac{12x+9y}{5}+3 = 5y-5, \quad \text{donc } y'' = y-1+1 = y.$$
Ainsi $g \circ g = \mathrm{id}$, et $g^{-1}=g$.

**Détermination de $P$.** Comme $g(P)=B$, on a $P = g^{-1}(B) = g(B)$ :
$$x_P = \dfrac{-9+16}{5}-2 = \dfrac{7}{5}-2 = -\dfrac{3}{5}, \qquad y_P = \dfrac{12+12}{5}+1 = \dfrac{24}{5}+1 = \dfrac{29}{5}$$
Donc $P\left(-\dfrac{3}{5}\,;\,\dfrac{29}{5}\right)$.

**Vérification.** $x' = \dfrac{\frac{9}{5}+\frac{116}{5}}{5}-2 = 5-2 = 3$ et $y' = \dfrac{-\frac{12}{5}+\frac{87}{5}}{5}+1 = 3+1 = 4$ : on retrouve bien $g(P) = B$.

### Pourquoi les autres réponses sont fausses

- **a)** Applique la translation dans le mauvais sens ($+2$ et $-1$ au lieu de $-2$ et $+1$) : l'image de ce point par $g$ est $(-1\,;\,6)$, pas $B$.
- **b)** Oublie les termes constants $-2$ et $+1$ des formules de $g$ : l'image de ce point est $(1\,;\,5)$.
- **c)** Erreur de signe sur l'ordonnée seulement ($\frac{24}{5}-1$) : l'image de ce point est $\left(\frac{7}{5}\,;\,\frac{14}{5}\right)$.

</details>

Avis : 

---

## 5. `cqc-monotonie-faible-0` (séries C/D/E)

**Remarque du relecteur :** Item de niveau Première, très facile pour C/D/E.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=x^2-6x+5$. Quelle affirmation sur l'extremum de $f$ est exacte ?

- a) $f$ admet un maximum égal à $-4$, atteint en $x=3$
- b) $f$ admet un minimum égal à $-4$, atteint en $x=3$
- c) $f$ admet un minimum égal à $32$, atteint en $x=-3$
- d) $f$ admet un minimum égal à $5$, atteint en $x=0$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Le sens de variation d'une fonction dérivable se lit dans le signe de sa dérivée : $f'\geq 0$ sur un intervalle signifie $f$ croissante, $f'\leq 0$ signifie $f$ décroissante. Une fonction décroissante puis croissante admet un minimum au point où sa dérivée change de signe.

### Corrigé

$f'(x)=2x-6=2(x-3)$. Donc $f'(x)<0$ pour $x<3$ et $f'(x)>0$ pour $x>3$.

$f$ est strictement décroissante sur $]-\infty\,;3]$ et strictement croissante sur $[3\,;+\infty[$. Elle admet donc un minimum en $x=3$ : $f(3)=9-18+5=-4$.

### Pourquoi les autres réponses sont fausses

- **a)** Confond minimum et maximum : $f$ est décroissante puis croissante, donc $-4$ est un minimum ($f$ n'a pas de maximum, puisque $f(x)$ tend vers $+\infty$).
- **c)** Erreur de signe dans la résolution de $2x-6=0$ ($x=-3$), puis $f(-3)=9+18+5=32$.
- **d)** Prend la valeur en $0$ (le terme constant $5$) sans étudier les variations ; or $f(3)=-4<5$.

</details>

Avis : 

---

## 6. `cqc-monotonie-faible-1` (séries C/D/E)

**Énoncé :**

Soit $g(x)=x^3-12x$ définie sur $\mathbb{R}$. Quelle description des variations de $g$ est exacte ?

- a) $g$ croissante sur $]-\infty\,;-2]$, décroissante sur $[-2\,;2]$, croissante sur $[2\,;+\infty[$, avec $g(-2)=32$ et $g(2)=-16$
- b) $g$ décroissante sur $]-\infty\,;-2]$, croissante sur $[-2\,;2]$, décroissante sur $[2\,;+\infty[$, avec $g(-2)=-16$ et $g(2)=16$
- c) $g$ croissante sur $]-\infty\,;-2\sqrt3]$, décroissante sur $[-2\sqrt3\,;2\sqrt3]$, croissante sur $[2\sqrt3\,;+\infty[$, avec $g(-2\sqrt3)=g(2\sqrt3)=0$
- d) $g$ croissante sur $]-\infty\,;-2]$, décroissante sur $[-2\,;2]$, croissante sur $[2\,;+\infty[$, avec $g(-2)=16$ et $g(2)=-16$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule $g'$, on la factorise pour trouver ses racines, on étudie son signe puis on en déduit les variations et les valeurs de $g$ aux points où le sens de variation change.

### Corrigé

$g'(x)=3x^2-12=3(x^2-4)=3(x-2)(x+2)$, qui s'annule en $-2$ et en $2$ et est négative entre les racines (coefficient dominant positif).

$g$ est croissante sur $]-\infty\,;-2]$, décroissante sur $[-2\,;2]$, croissante sur $[2\,;+\infty[$.

$g(-2)=-8+24=16$ et $g(2)=8-24=-16$.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur le cube : $(-2)^3=-8$, et non $8$ ; donc $g(-2)=16$ et non $32$.
- **b)** Inverse le signe de $g'$ : un trinôme de coefficient dominant positif est négatif entre ses racines, positif à l'extérieur.
- **c)** Oublie de diviser par $3$ en résolvant $3x^2-12=0$ : on obtient $x^2=12$ au lieu de $x^2=4$.

</details>

Avis : 

---

## 7. `cqc-monotonie-d-une-suite-faible-1` (séries C/D/E)

**Énoncé :**

Pour tout entier naturel $n$, on pose $u_n=\displaystyle\int_0^1(1-x)^n\,dx$.

Pour tout entier naturel $n$, que vaut $u_{n+1}-u_n$ ?

- a) $\dfrac{1}{(n+1)(n+2)}$
- b) $-\dfrac{1}{(n+2)(n+3)}$
- c) $-\dfrac{1}{(n+1)(n+2)}$
- d) $-\dfrac{1}{2n+3}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une suite définie par une intégrale $u_n=\displaystyle\int_a^b f_n(x)\,dx$ sur des bornes fixes, on peut écrire $u_{n+1}-u_n=\displaystyle\int_a^b\big(f_{n+1}(x)-f_n(x)\big)dx$ et étudier le signe de la fonction à intégrer ; lorsqu'une primitive est connue, on peut aussi calculer $u_n$ explicitement.

### Corrigé

Une primitive de $x\mapsto(1-x)^n$ est $x\mapsto-\dfrac{(1-x)^{n+1}}{n+1}$ (attention au facteur $-1$ venant de la dérivée de $1-x$). Donc :
$$u_n=\left[-\dfrac{(1-x)^{n+1}}{n+1}\right]_0^1=0-\left(-\dfrac{1}{n+1}\right)=\dfrac{1}{n+1}.$$

Par suite :
$$u_{n+1}-u_n=\dfrac{1}{n+2}-\dfrac{1}{n+1}=\dfrac{(n+1)-(n+2)}{(n+1)(n+2)}=-\dfrac{1}{(n+1)(n+2)}.$$

Ce résultat est cohérent avec l'étude directe du signe : $u_{n+1}-u_n=\displaystyle\int_0^1(1-x)^n\big[(1-x)-1\big]dx=-\int_0^1 x(1-x)^n\,dx$, et la fonction $x\mapsto x(1-x)^n$ est continue, positive et non identiquement nulle sur $[0;1]$, donc cette intégrale est strictement positive. La suite $(u_n)$ est strictement décroissante.

Vérification : $u_0=1$, $u_1=\dfrac12$, et $u_1-u_0=-\dfrac12=-\dfrac{1}{1\times2}$.

### Pourquoi les autres réponses sont fausses

- **a)** Oublie le signe $-$ dans la primitive : on trouve alors $u_n=-\dfrac{1}{n+1}$, et la différence change de signe.
- **b)** Se trompe d'exposant dans la primitive et obtient $u_n=\dfrac{1}{n+2}$.
- **d)** Réduit mal au même dénominateur, en additionnant les dénominateurs $(n+1)+(n+2)$ au lieu de les multiplier.

</details>

Avis : 

---

## 8. `cqc-produit-mixte-elevee-5` (séries C/E)

**Remarque du relecteur :** LIMITE : vérifier que l'expression « produit mixte » figure bien au programme de Terminale C/E ; sinon écrire « le nombre u·(w∧v) ».

**Énoncé :**

On considère les trois vecteurs $\vec u=(1;2;-1)$, $\vec v=(0;3;2)$ et $\vec w=(-2;1;1)$ dans un repère orthonormé direct de l'espace.

Que vaut le produit mixte $\vec u\cdot(\vec w\wedge\vec v)$ ?

- a) $-13$
- b) $-3$
- c) $1$
- d) $13$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Le produit mixte est invariant par permutation circulaire de ses trois vecteurs : $\vec u\cdot(\vec v\wedge\vec w)=\vec v\cdot(\vec w\wedge\vec u)=\vec w\cdot(\vec u\wedge\vec v)$. En revanche, l'échange de deux des trois vecteurs change le signe du produit mixte (antisymétrie), par exemple $\vec u\cdot(\vec w\wedge\vec v)=-\vec u\cdot(\vec v\wedge\vec w)$.

### Corrigé
$\vec v\wedge\vec w=(3\times1-2\times1; 2\times(-2)-0\times1; 0\times1-3\times(-2))=(1;-4;6)$.

$\vec u\cdot(\vec v\wedge\vec w)=1\times1+2\times(-4)+(-1)\times6=1-8-6=-13$.

Par antisymétrie, $\vec w\wedge\vec v=-(\vec v\wedge\vec w)=(-1;4;-6)$, donc :

$\vec u\cdot(\vec w\wedge\vec v)=1\times(-1)+2\times4+(-1)\times(-6)=-1+8+6=13$.

On obtient $13=-(-13)$ : l'échange des vecteurs $\vec v$ et $\vec w$ change le signe du produit mixte.

### Pourquoi les autres réponses sont fausses

- **a)** Calcule $\vec u\cdot(\vec v\wedge\vec w)$ en oubliant que l'échange de $\vec v$ et $\vec w$ change le signe.
- **b)** Erreur de signe sur la deuxième composante de $\vec w\wedge\vec v$ (écrite $-4$ au lieu de $4$) : $-1-8+6=-3$.
- **c)** Erreur de signe sur la troisième composante de $\vec w\wedge\vec v$ (écrite $6$ au lieu de $-6$) : $-1+8-6=1$.

</details>

Avis : 

---

## 9. `cqc-produit-mixte-faible-1` (séries C/E)

**Remarque du relecteur :** LIMITE : le terme « produit mixte » n'est pas toujours nommé dans les manuels de Terminale C/E ; le calcul (produit scalaire et produit vectoriel) reste au programme.

**Énoncé :**

Dans un repère orthonormé direct $(O;\vec i,\vec j,\vec k)$ de l'espace, on donne les points $A(2;1;0)$, $B(3;3;1)$, $C(2;0;2)$ et $D(4;6;0)$.

Que vaut le produit mixte $\vec{AB}\cdot(\vec{AC}\wedge\vec{AD})$, et que peut-on en conclure ?

- a) Il vaut $-16$ : les points ne sont pas coplanaires
- b) Il est nul : les points sont coplanaires
- c) Il vaut $20$ : les points ne sont pas coplanaires
- d) Il est nul : les points sont alignés

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Quatre points $A,B,C,D$ de l'espace sont coplanaires si et seulement si le produit mixte $\vec{AB}\cdot(\vec{AC}\wedge\vec{AD})$ est nul.

### Corrigé
$\vec{AB}=(1;2;1)$, $\vec{AC}=(0;-1;2)$, $\vec{AD}=(2;5;0)$.

Produit vectoriel : $\vec{AC}\wedge\vec{AD}=(-1\times0-2\times5; 2\times2-0\times0; 0\times5-(-1)\times2)=(-10;4;2)$.

Produit scalaire : $\vec{AB}\cdot(\vec{AC}\wedge\vec{AD})=1\times(-10)+2\times4+1\times2=-10+8+2=0$.

Vérification par le déterminant : $1\times(-1\times0-2\times5)-2\times(0\times0-2\times2)+1\times(0\times5-(-1)\times2)=-10+8+2=0$.

Le produit mixte étant nul, les points $A$, $B$, $C$ et $D$ sont coplanaires.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur la deuxième composante du produit vectoriel (écrite $-4$) : $-10-8+2=-16$.
- **c)** Erreur de signe sur la première composante du produit vectoriel (écrite $10$) : $10+8+2=20$.
- **d)** Confond coplanaires et alignés : un produit mixte nul ne dit pas que les points sont alignés, et ici $\vec{AB}\wedge\vec{AC}=(5;-2;-1)$ n'est pas nul, donc $A$, $B$, $C$ ne sont pas alignés.

</details>

Avis : 

---

## 10. `cqc-projecteur-faible-0` (séries C/E)

**Énoncé :**

On considère un espace vectoriel réel $E$ de dimension 2, muni d'une base $(\vec{u},\vec{v})$. Soit $f$ l'endomorphisme de $E$ défini par :

$$f(\vec{u})=\vec{u} \quad \text{et} \quad f(\vec{v})=\vec{u}.$$

Laquelle des égalités suivantes est vraie ?

- a) $f\circ f=Id$
- b) $f\circ f=0$
- c) $f\circ f=2f$
- d) $f\circ f=f$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour comparer $f\circ f$ à un endomorphisme donné, il suffit, grâce à la linéarité de $f$, de calculer $f\circ f$ sur les vecteurs d'une base de $E$, puis d'étendre le résultat à un vecteur quelconque par linéarité.

### Corrigé

$f\bigl(f(\vec{u})\bigr)=f(\vec{u})=\vec{u}$ et $f\bigl(f(\vec{v})\bigr)=f(\vec{u})=\vec{u}$.

Soit $\vec{x}=a\vec{u}+b\vec{v}$. Par linéarité de $f$ :
$$f(\vec{x})=a\,f(\vec{u})+b\,f(\vec{v})=(a+b)\vec{u}, \qquad f\bigl(f(\vec{x})\bigr)=(a+b)\,f(\vec{u})=(a+b)\vec{u}.$$

Donc $f\bigl(f(\vec{x})\bigr)=f(\vec{x})$ pour tout vecteur $\vec{x}$ de $E$ : $f\circ f=f$, et $f$ est un projecteur de $E$.

### Pourquoi les autres réponses sont fausses

- **a)** Généralise $f(\vec u)=\vec u$ à tous les vecteurs ; or $f\bigl(f(\vec v)\bigr)=\vec u\neq\vec v$.
- **b)** $f\bigl(f(\vec u)\bigr)=\vec u$ n'est pas le vecteur nul.
- **c)** Ajoute les images au lieu de composer : $f\bigl(f(\vec u)\bigr)=\vec u$, alors que $2f(\vec u)=2\vec u$.

</details>

Avis : 

---

## 11. `cqc-prolongement-par-continuite-elevee-0` (séries A/C/E)

**Remarque du relecteur :** LIMITE : la continuité / prolongement par continuité est à la limite du programme de la série A.

**Énoncé :**

Soit $f$ la fonction définie par :
$$f(x)=\dfrac{x^2-4}{x-2} \text{ si } x<2, \qquad f(x)=x^2-4x+8 \text{ si } x>2$$
Aucune des deux formules ne détermine la valeur de $f$ en $2$.

Peut-on choisir une valeur pour $f(2)$ de sorte que la fonction $f$ ainsi complétée soit continue sur $\mathbb{R}$ tout entier ? Si oui, laquelle ?

- a) Oui, en posant $f(2)=0$
- b) Oui, en posant $f(2)=20$
- c) Oui, en posant $f(2)=4$
- d) Non, aucune valeur ne convient

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une fonction définie par deux formules différentes de part et d'autre d'un point $x_0$ non couvert par l'une ni par l'autre, prolonger $f$ par continuité en $x_0$ exige de calculer séparément la limite à gauche et la limite à droite en $x_0$. Le prolongement ne réussit que si ces deux limites latérales sont toutes deux finies ET égales entre elles : on pose alors $f(x_0)$ égal à cette valeur commune.

### Corrigé

**Limite à gauche en $2$.** Pour $x<2$, la première formule donne en $2$ la forme indéterminée $\dfrac{0}{0}$. On factorise le numérateur, une différence de carrés : $x^2-4=(x-2)(x+2)$, donc, pour tout $x<2$ :
$$f(x)=\frac{(x-2)(x+2)}{x-2}=x+2, \qquad \lim_{x\to2^{-}}f(x)=4.$$

**Limite à droite en $2$.** Pour $x>2$, $f(x)=x^2-4x+8$ est une fonction polynôme, continue sur $\mathbb{R}$ :
$$\lim_{x\to2^{+}}f(x)=2^2-4\times2+8=4.$$

**Conclusion.** Les deux limites latérales sont finies et égales à $4$. En posant $f(2)=4$, $f$ est continue en $2$ ; comme chacune des deux formules est continue sur son intervalle, $f$ est continue sur $\mathbb{R}$ tout entier.

### Pourquoi les autres réponses sont fausses

- **a)** Remplace $x$ par $2$ dans le seul numérateur $x^2-4$, sans lever l'indétermination $\dfrac{0}{0}$.
- **b)** Erreur de signe dans le calcul de la limite à droite : $4+8+8=20$ au lieu de $4-8+8=4$.
- **d)** Croit que la forme $\dfrac{0}{0}$ interdit tout prolongement ; or la limite à gauche existe et vaut $4$, comme la limite à droite.

</details>

Avis : 

---

## 12. `cqc-prolongement-par-continuite-faible-0` (séries A/C/E)

**Remarque du relecteur :** LIMITE : le prolongement par continuité est à la limite haute du programme de la série A.

**Énoncé :**

Soit $f$ la fonction définie par $f(x) = \dfrac{x^2-25}{x-5}$ pour tout réel $x \neq 5$.

Quelle valeur faut-il attribuer à $f(5)$ pour que la fonction ainsi complétée soit continue en $5$ ?

- a) Aucune : $f$ ne peut pas être prolongée par continuité en $5$, car on obtient $\dfrac{0}{0}$
- b) $f(5)=0$
- c) $f(5)=10$
- d) $f(5)=5$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'une formule $f(x)$ n'est pas définie en un point $x_0$ (ici une division par $x-5$, nulle en $x=5$), on peut malgré tout prolonger $f$ par continuité en $x_0$ si la formule admet, quand $x\to x_0$, une limite FINIE $\ell$ : il suffit alors de poser $f(x_0)=\ell$, et la fonction ainsi complétée devient continue en $x_0$.

### Corrigé

En $x=5$, le numérateur et le dénominateur de $f(x)=\dfrac{x^2-25}{x-5}$ s'annulent tous les deux : $5^2-25=0$ et $5-5=0$. La formule prend donc la forme indéterminée $\dfrac{0}{0}$ : $5$ est une valeur interdite, exclue du domaine de définition de $f$.

Factorisons le numérateur, qui est une différence de carrés :
$$x^2-25=(x-5)(x+5)$$
Pour tout $x\neq5$, on peut donc simplifier le facteur commun $(x-5)$ :
$$f(x)=\frac{(x-5)(x+5)}{x-5}=x+5$$

On en déduit :
$$\lim_{x\to5}f(x)=\lim_{x\to5}(x+5)=10$$

Cette limite est finie. On peut donc prolonger $f$ par continuité en $5$ en posant $f(5)=10$. La fonction ainsi complétée est continue en $5$, puisque $\displaystyle\lim_{x\to5}f(x)=10=f(5)$.

### Pourquoi les autres réponses sont fausses

- **a)** La forme $\dfrac{0}{0}$ est indéterminée : elle n'interdit pas le prolongement, il faut lever l'indétermination avant de conclure.
- **b)** $0$ est la valeur du numérateur en $5$, pas la limite du quotient.
- **d)** $5$ provient d'une simplification erronée $f(x)=x$ : après simplification il reste $x+5$, qui vaut $10$ en $5$.

</details>

Avis : 

---

## 13. `cqc-prolongement-par-continuite-faible-1` (séries A/C/E)

**Remarque du relecteur :** LIMITE : le prolongement par continuité est à la limite haute du programme de la série A.

**Énoncé :**

Soit $g$ la fonction définie par $g(x) = \dfrac{x^2+x-6}{x-2}$ pour tout réel $x \neq 2$.

Quelle valeur faut-il attribuer à $g(2)$ pour que la fonction ainsi complétée soit continue en $2$ ?

- a) $g(2)=5$
- b) $g(2)=0$
- c) $g(2)=-1$
- d) Aucune : $g$ ne peut pas être prolongée par continuité en $2$, car on obtient $\dfrac{0}{0}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'une formule $g(x)$ n'est pas définie en un point $x_0$ à cause d'une division par une expression qui s'annule en $x_0$, on peut prolonger $g$ par continuité en $x_0$ à condition que la formule admette, quand $x\to x_0$, une limite FINIE $\ell$ : on pose alors $g(x_0)=\ell$, ce qui rend la fonction complétée continue en $x_0$.

### Corrigé

En $x=2$, le dénominateur $x-2$ s'annule, et le numérateur aussi : $2^2+2-6=0$. La formule prend la forme indéterminée $\dfrac{0}{0}$ : $2$ est une valeur interdite, exclue du domaine de définition de $g$.

Factorisons le numérateur, un trinôme du second degré admettant $2$ pour racine évidente :
$$x^2+x-6=(x-2)(x+3)$$
(on vérifie : $(x-2)(x+3)=x^2+3x-2x-6=x^2+x-6$). Pour tout $x\neq2$, on simplifie le facteur commun $(x-2)$ :
$$g(x)=\frac{(x-2)(x+3)}{x-2}=x+3$$

On en déduit :
$$\lim_{x\to2}g(x)=\lim_{x\to2}(x+3)=5$$

Cette limite est finie. On peut donc prolonger $g$ par continuité en $2$ en posant $g(2)=5$. La fonction ainsi complétée est continue en $2$, puisque $\displaystyle\lim_{x\to2}g(x)=5=g(2)$.

### Pourquoi les autres réponses sont fausses

- **b)** $0$ est la valeur du numérateur en $2$, pas la limite du quotient.
- **c)** $-1$ vient d'une factorisation fausse $(x-2)(x-3)$ : les racines du trinôme sont $2$ et $-3$, et non $2$ et $3$.
- **d)** La forme $\dfrac{0}{0}$ est indéterminée : elle n'interdit pas le prolongement, il faut d'abord simplifier.

</details>

Avis : 

---

## 14. `cqc-composition-d-endomorphismes-tle-c-elevee-5` (séries C)

**Remarque du relecteur :** LIMITE : endomorphismes de R^3 (noyau, image), à confirmer au programme de Terminale C ; l'hypothèse f∘f=f est une donnée inutile pour répondre.

**Énoncé :**

Soit $f$ l'endomorphisme de $\mathbb{R}^3$ défini par $f(x\,;y\,;z)=(x\,;y\,;x+y)$. On admet que $f\circ f=f$.

Quels sont le noyau $\ker f$ et l'image $\operatorname{Im}f$ de $f$ ?

- a) $\ker f$ est le plan d'équation $z=x+y$ et $\operatorname{Im}f=\operatorname{Vect}\big((0\,;0\,;1)\big)$
- b) $\ker f=\operatorname{Vect}\big((0\,;0\,;1)\big)$ et $\operatorname{Im}f$ est le plan d'équation $z=x+y$
- c) $\ker f=\{\vec 0\}$ et $\operatorname{Im}f=\mathbb{R}^3$
- d) $\ker f=\operatorname{Vect}\big((0\,;0\,;1)\big)$ et $\operatorname{Im}f$ est le plan d'équation $z=0$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Le noyau $\ker f$ est l'ensemble des vecteurs $\vec u$ tels que $f(\vec u)=\vec 0$ : on résout le système correspondant. L'image $\operatorname{Im}f$ est l'ensemble des vecteurs $f(\vec u)$ : on décrit la forme générale des images. Un endomorphisme vérifiant $f\circ f=f$ est un projecteur : $E=\ker f\oplus\operatorname{Im}f$, ce qui fournit un contrôle (les dimensions s'additionnent et l'intersection est réduite à $\{\vec 0\}$).

### Corrigé

On vérifie d'abord : $f(f(x\,;y\,;z))=f(x\,;y\,;x+y)=(x\,;y\,;x+y)=f(x\,;y\,;z)$ : $f\circ f=f$.

**Noyau.** $f(x\,;y\,;z)=\vec0\iff x=0,\ y=0,\ x+y=0\iff x=y=0$, $z$ étant quelconque. Donc $\ker f=\{(0\,;0\,;z)\}=\operatorname{Vect}\big((0\,;0\,;1)\big)$.

**Image.** Les images sont les vecteurs $(a\,;b\,;a+b)$ avec $a,b$ réels : $\operatorname{Im}f$ est le plan d'équation $z=x+y$.

**Contrôle.** Le vecteur $(0\,;0\,;1)$ n'est pas dans ce plan ($1\neq0+0$) : l'intersection est réduite à $\{\vec0\}$, et $1+2=3=\dim\mathbb{R}^3$, ce qui est conforme à $\mathbb{R}^3=\ker f\oplus\operatorname{Im}f$.

### Pourquoi les autres réponses sont fausses

- **a)** Noyau et image sont inversés : $f(0\,;0\,;1)=(0\,;0\,;0)$, donc la droite dirigée par $(0\,;0\,;1)$ est dans le noyau, pas dans l'image.
- **c)** $f$ n'est pas injective (elle « oublie » $z$) : son noyau n'est donc pas réduit à $\{\vec0\}$, et elle n'est pas surjective.
- **d)** La troisième coordonnée d'une image vaut $x+y$, et non $0$ : par exemple $f(1\,;0\,;0)=(1\,;0\,;1)$ n'est pas dans le plan $z=0$.

</details>

Avis : 

---

## 15. `cqc-composition-d-endomorphismes-tle-c-moyenne-2` (séries C)

**Modification de fond lors de la conversion** (question réduite ou méthode remplacée) : à examiner de près.

**Énoncé :**

Soit $f$ et $g$ les endomorphismes de $\mathbb{R}^2$ définis par $f(x\,;y)=(x+2y\,;\,y)$ et $g(x\,;y)=(y\,;\,x)$.

Laquelle des affirmations suivantes est vraie ?

- a) $(f\circ g)(x\,;y)=(2x+y\,;\,x)$ et $f\circ g\neq g\circ f$
- b) $(f\circ g)(x\,;y)=(y\,;\,x+2y)$ et $f\circ g\neq g\circ f$
- c) $(f\circ g)(x\,;y)=(2x+y\,;\,y)$ et $f\circ g\neq g\circ f$
- d) $(f\circ g)(x\,;y)=(2x+y\,;\,x)$ et $f\circ g=g\circ f$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

$(f\circ g)(\vec u)=f\big(g(\vec u)\big)$ : on applique d'abord $g$, puis $f$. En général, $f\circ g$ et $g\circ f$ sont différentes : la composition n'est pas commutative, il faut donc calculer les deux pour comparer.

### Corrigé

$$(f\circ g)(x\,;y)=f(y\,;x)=(y+2x\,;\,x)=(2x+y\,;\,x),$$
$$(g\circ f)(x\,;y)=g(x+2y\,;\,y)=(y\,;\,x+2y).$$
Par exemple, $(f\circ g)(1\,;0)=(2\,;1)$ alors que $(g\circ f)(1\,;0)=(0\,;1)$ : $f\circ g\neq g\circ f$.

### Pourquoi les autres réponses sont fausses

- **b)** $(y\,;\,x+2y)$ est l'expression de $g\circ f$ : l'ordre de composition a été inversé.
- **c)** La seconde coordonnée de $f(X\,;Y)$ est $Y$, qui vaut ici $x$ : on a gardé $y$ sans faire la substitution.
- **d)** L'expression de $f\circ g$ est juste, mais la conclusion est fausse : on ne peut pas supposer la composition commutative, et le calcul de $g\circ f$ le dément.

</details>

Avis : 

---

## 16. `cqc-discriminant-complexe-elevee-0` (séries C/D/E)

**Énoncé :**

On considère, dans $\mathbb C$, l'équation $(E) : z^3-(3-i)z^2+(12+3i)z-10i=0$, dont on sait que $z_0=1+2i$ est solution.

Quel est l'ensemble $\mathcal S$ des solutions de $(E)$ dans $\mathbb C$ ?

- a) $\{1+2i\,;\,1-2i\,;\,1-i\}$
- b) $\{1+2i\,;\,-2+4i\,;\,-i\}$
- c) $\{1+2i\,;\,2+i\,;\,-4i\}$
- d) $\{1+2i\,;\,2-4i\,;\,i\}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On factorise un polynôme de degré 3 par $(z-z_0)$ dès qu'une racine $z_0$ est connue ou vérifiée, y compris lorsque $z_0$ et les coefficients du polynôme sont eux-mêmes complexes : on développe $(z-z_0)(z^2+bz+c)$ et on identifie chaque coefficient, y compris le terme constant, ce qui peut demander de diviser par $z_0$ en multipliant par son conjugué. On résout ensuite le facteur du second degré obtenu comme toute équation à discriminant complexe, en identifiant une racine carrée $\delta$ de $\Delta$.

### Corrigé

**Vérification.** Pour $z_0=1+2i$ : $z_0^2=-3+4i$ et $z_0^3=-11-2i$. Avec $(3-i)(-3+4i)=-5+15i$ et $(12+3i)(1+2i)=6+27i$ :
$$(-11-2i)+(5-15i)+(6+27i)-10i=0.$$

**Factorisation.** On écrit $(E)=(z-z_0)(z^2+bz+c)$. En identifiant le coefficient de $z^2$ :
$$b-z_0=-(3-i) \ \Rightarrow\ b=(1+2i)-(3-i)=-2+3i.$$
Pour le terme constant : $-z_0c=-10i \ \Rightarrow\ c=\dfrac{10i}{1+2i}=\dfrac{10i(1-2i)}{(1+2i)(1-2i)}=\dfrac{20+10i}5=4+2i.$

Le facteur restant est $z^2-(2-3i)z+4+2i=0$.

$$\Delta=(2-3i)^2-4(4+2i)=(4-12i-9)-16-8i=-21-20i.$$

On cherche $\delta=x+iy$ tel que $\delta^2=-21-20i$ : $x^2-y^2=-21$ et $xy=-10$, d'où $x^4+21x^2-100=0$, soit $x^2=4$ (on rejette $-25$). Ainsi $x=2$, $y=-5$, $\delta=2-5i$. Vérification : $(2-5i)^2=4-20i-25=-21-20i$.

$$z=\frac{(2-3i)\pm(2-5i)}2,\qquad z_1=2-4i,\qquad z_2=i.$$

**Bilan.** $\mathcal S=\{1+2i\,;\,2-4i\,;\,i\}$. Contrôle : la somme des trois racines vaut $3-i$, opposé du coefficient de $z^2$ dans $(E)$.

### Pourquoi les autres réponses sont fausses

- **a)** Les coefficients de $(E)$ ne sont pas réels : le conjugué $1-2i$ d'une racine n'est donc pas forcément racine (et en effet il ne l'est pas).
- **b)** Erreur de signe dans la formule $z=\dfrac{-b\pm\delta}{2}$ : on a pris $-b=-(2-3i)$ au lieu de $2-3i$.
- **c)** Mauvaise racine carrée : $(2+5i)^2=-21+20i\neq\Delta$, le signe de la partie imaginaire n'a pas été contrôlé.

</details>

Avis : 

---

## 17. `cqc-derivee-d-un-produit-moyenne-0` (séries A/C/D/E/TI)

**Remarque du relecteur :** LIMITE : dérivée de a^x pour la série A.

**Modification de fond lors de la conversion** (question réduite ou méthode remplacée) : à examiner de près.

**Énoncé :**

On considère la fonction $h$ définie sur $\mathbb{R}$ par $h(x) = (2x-1)\times 3^{x}$.

Quelle est l'expression de $h'(x)$ ?

- a) $h'(x)=3^{x}(2x+1)$
- b) $h'(x)=3^{x}\big(2+(2x-1)\ln3\big)$
- c) $h'(x)=2\times3^{x}+x(2x-1)\,3^{x-1}$
- d) $h'(x)=(2x-1)(\ln3)\,3^{x}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour dériver un produit $u\times v$, on utilise $(uv)'=u'v+uv'$. Lorsque $v(x)=a^{x}$ (avec $a>0$), on réécrit d'abord $v(x)=e^{x\ln a}$ pour obtenir $v'(x)=(\ln a)\,e^{x\ln a} = (\ln a)\,a^{x}$, avant d'appliquer la formule du produit.

### Corrigé

On pose $u(x)=2x-1$ et $v(x)=3^{x}$. Comme $3^{x}=e^{x\ln3}$, on a $v'(x)=(\ln3)e^{x\ln3}=(\ln3)\times3^{x}$. Par ailleurs, $u'(x)=2$.

$$h'(x) = u'(x)v(x)+u(x)v'(x) = 2\times3^{x} + (2x-1)\times(\ln3)\times3^{x}$$

En factorisant par $3^{x}$ :

$$h'(x) = 3^{x}\big(2+(2x-1)\ln3\big)$$

### Pourquoi les autres réponses sont fausses

- **a)** On a dérivé $3^x$ en $3^x$, en oubliant le facteur $\ln3$ (cela n'est vrai que pour $e^x$).
- **c)** On a dérivé $3^x$ comme une puissance $x^n$ : $x\times3^{x-1}$ ; ici c'est l'exposant qui varie.
- **d)** On a oublié le terme $u'v=2\times3^x$ de la formule du produit.

</details>

Avis : 

---

## 18. `cqc-derivee-exponentielle-elevee-0` (séries A)

**Remarque du relecteur :** LIMITE : dérivée de e^{u(x)} et équation de tangente, à vérifier pour la série A.

**Énoncé :**

On considère la fonction $f$ définie sur $\mathbb{R}$ par $f(x) = e^{3x-6}$, de courbe représentative $(C)$ dans un repère.

Quelle est une équation de la tangente à $(C)$ au point d'abscisse $2$ ?

- a) $y=3x-6$
- b) $y=x+1$
- c) $y=3x-5$
- d) $y=3x+1$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
La dérivée de $x \mapsto e^{u(x)}$ vaut $u'(x)e^{u(x)}$. L'équation de la tangente à la courbe d'une fonction $f$ dérivable en un point d'abscisse $a$ est donnée par $y = f'(a)(x-a) + f(a)$ : il faut donc calculer $f(a)$ et $f'(a)$ avant d'appliquer cette formule.

### Corrigé
**Dérivée.** On pose $u(x) = 3x - 6$, donc $u'(x) = 3$ et $f'(x) = 3e^{3x-6}$.

**Valeurs en $x=2$.**

$$f(2) = e^{0} = 1,\qquad f'(2) = 3e^0 = 3$$

**Équation de la tangente.**

$$y = f'(2)(x-2) + f(2) = 3(x-2) + 1 = 3x - 5$$

La tangente à $(C)$ au point d'abscisse $2$ a donc pour équation $y = 3x - 5$.

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié d'ajouter $f(2)=1$ : la tangente ne passerait pas par le point $(2\,;1)$ de la courbe.
- **b)** On a confondu les rôles de $f(2)$ et $f'(2)$ : le coefficient directeur est $f'(2)=3$, et non $f(2)=1$.
- **d)** On a écrit $y=f'(a)\,x+f(a)$ en oubliant le décalage $(x-a)$.

</details>

Avis : 

---

## 19. `cqc-derivee-exponentielle-faible-0` (séries A)

**Énoncé :**

On considère la fonction $f$ définie sur $\mathbb{R}$ par $f(x) = e^{2x-3} + 5$.

Quelle est l'expression de $f'(x)$ ?

- a) $f'(x)=2e^{2x-3}$
- b) $f'(x)=e^{2x-3}$
- c) $f'(x)=2e^{2x-3}+5$
- d) $f'(x)=(2x-3)e^{2x-4}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour dériver une fonction de la forme $x \mapsto e^{u(x)}$, on applique la formule $(e^{u})' = u' \times e^{u}$, où $u'$ désigne la dérivée de $u$. La dérivée d'une constante ajoutée est nulle.

### Corrigé
Ici, $f(x) = e^{u(x)} + 5$ avec $u(x) = 2x - 3$, donc $u'(x) = 2$.

On a donc :

$$f'(x) = u'(x) \times e^{u(x)} = 2e^{2x-3}$$

(la dérivée de la constante $5$ étant nulle).

### Pourquoi les autres réponses sont fausses

- **b)** On a oublié le facteur $u'(x)=2$ : $(e^{u})'=u'e^{u}$, et non $e^{u}$.
- **c)** On a conservé la constante $5$, alors que sa dérivée est nulle.
- **d)** On a dérivé $e^{u}$ comme une puissance ($u\,e^{u-1}$), ce qui n'a pas de sens pour l'exponentielle.

</details>

Avis : 

---

## 20. `cqc-branche-parabolique-elevee-5` (séries A/C/D/E)

**Remarque du relecteur :** LIMITE : branche parabolique de direction oblique, haut du programme de la série A.

**Énoncé :**

Soit $r$ la fonction définie sur $\mathbb{R}$ par
$$r(x) = x + \ln(x^{2}+1).$$
Quelle est la nature des branches infinies de la courbe représentative de $r$ en $+\infty$ et en $-\infty$ ?

- a) Une asymptote oblique d'équation $y=x$ en $+\infty$ et en $-\infty$
- b) Une branche parabolique de direction $y=x$ en $+\infty$ et en $-\infty$
- c) Une branche parabolique de direction $y=x$ en $+\infty$, et une asymptote oblique d'équation $y=x$ en $-\infty$
- d) Une branche parabolique de direction $(Ox)$ en $+\infty$ et en $-\infty$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand $\dfrac{f(x)}{x}$ tend vers un nombre fini non nul $a$ mais que $f(x)-ax$ diverge (tend vers $+\infty$ ou $-\infty$ au lieu d'un nombre fini), la courbe présente une branche parabolique de direction $y=ax$ : elle suit approximativement cette pente sans jamais s'approcher de la droite elle-même. Ce critère s'applique de la même façon en $+\infty$ et en $-\infty$, et rien n'empêche les deux bornes de donner la même direction.

### Corrigé
**En $+\infty$.** Le domaine de $r$ est $\mathbb{R}$ tout entier, car $x^{2}+1>0$. Par somme, $\lim_{x\to+\infty} r(x) = +\infty$.

Pour $\dfrac{r(x)}{x} = 1 + \dfrac{\ln(x^{2}+1)}{x}$, on encadre le logarithme : pour $x\geqslant1$, $x^{2}+1\leqslant 2x^{2}$, donc
$$0 \leqslant \dfrac{\ln(x^{2}+1)}{x} \leqslant \dfrac{\ln(2)}{x} + \dfrac{2\ln(x)}{x}.$$
Par croissances comparées, $\dfrac{\ln(x)}{x}\to0$ ; par encadrement, $\dfrac{\ln(x^{2}+1)}{x}\to0$, d'où $\lim_{x\to+\infty} \dfrac{r(x)}{x} = 1$.

Enfin $r(x)-x=\ln(x^{2}+1)\to+\infty$. Cette limite étant infinie, il n'y a **pas d'asymptote oblique** en $+\infty$ : la courbe présente une **branche parabolique de direction $y=x$**.

**En $-\infty$.** Posons $x=-t$ avec $t\to+\infty$ : $r(-t) = -t\left(1 - \dfrac{\ln(t^{2}+1)}{t}\right)\to-\infty$, et
$$\dfrac{r(-t)}{-t} = 1 - \dfrac{\ln(t^{2}+1)}{t} \to 1.$$
Mais $r(x)-x=\ln(t^{2}+1)\to+\infty$.

**Conclusion.** Dans les deux directions, $\dfrac{r(x)}{x}\to1$ mais $r(x)-x\to+\infty$ : la courbe de $r$ présente une **branche parabolique de direction $y=x$, à la fois en $+\infty$ et en $-\infty$**, au-dessus de cette droite puisque $\ln(x^2+1)\geqslant0$.

### Pourquoi les autres réponses sont fausses

- **a)** $\dfrac{r(x)}{x}\to1$ ne suffit pas pour une asymptote oblique : il faut aussi que $r(x)-x$ ait une limite finie, or elle vaut $+\infty$.
- **c)** On a cru que le terme $\ln(x^2+1)$ devenait négligeable en $-\infty$ : comme $x^2+1\to+\infty$ aussi en $-\infty$, $r(x)-x\to+\infty$ des deux côtés.
- **d)** La direction $(Ox)$ correspond à $\dfrac{r(x)}{x}\to0$ ; ici c'est seulement $\dfrac{\ln(x^2+1)}{x}$ qui tend vers $0$, et $\dfrac{r(x)}{x}\to1$.

</details>

Avis : 

---

## 21. `cqc-branche-parabolique-faible-1` (séries A/C/D/E)

**Remarque du relecteur :** LIMITE : la notion de branche parabolique est à la limite haute du programme de la série A.

**Énoncé :**

Soit $h$ la fonction définie sur $\,]0;+\infty[$ par
$$h(x) = 1 + \ln(x).$$
Quelle est la nature de la branche infinie de la courbe représentative de $h$ au voisinage de $+\infty$ ?

- a) Une branche parabolique de direction $(Ox)$
- b) Une branche parabolique de direction $(Oy)$
- c) Une asymptote horizontale d'équation $y=1$
- d) Une branche parabolique de direction la droite d'équation $y=x$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Lorsque $\lim f(x) = \pm\infty$ mais que $\dfrac{f(x)}{x} \to 0$, la courbe s'élève (ou descend) beaucoup plus lentement qu'une droite quelconque : la branche infinie a alors pour direction l'axe des abscisses $(Ox)$.

### Corrigé
Quand $x\to+\infty$, $\ln(x)\to+\infty$, donc par somme :
$$\lim_{x\to+\infty} h(x) = +\infty.$$

On calcule ensuite
$$\dfrac{h(x)}{x} = \dfrac{1}{x} + \dfrac{\ln(x)}{x}.$$
Or $\dfrac{1}{x}\to 0$ et, par croissances comparées, $\dfrac{\ln(x)}{x}\to 0$ quand $x\to+\infty$. Donc :
$$\lim_{x\to+\infty} \dfrac{h(x)}{x} = 0.$$

La fonction $h$ tend vers $+\infty$ alors que $\dfrac{h(x)}{x}$ tend vers $0$ : la courbe représentative de $h$ présente donc, au voisinage de $+\infty$, une **branche parabolique de direction $(Ox)$**.

### Pourquoi les autres réponses sont fausses

- **b)** La direction $(Oy)$ correspond à $\dfrac{h(x)}{x}\to\pm\infty$, cas d'une croissance plus rapide qu'une droite (comme $e^x$), pas du logarithme.
- **c)** Une asymptote horizontale exige une limite finie de $h$ ; or $h(x)\to+\infty$ (le $1$ ne fixe pas la limite).
- **d)** Une direction $y=x$ exigerait $\dfrac{h(x)}{x}\to1$ ; ici cette limite vaut $0$.

</details>

Avis : 

---

## 22. `cqc-branche-parabolique-moyenne-2` (séries A/C/D/E)

**Remarque du relecteur :** LIMITE : branches paraboliques et limite x e^x en -inf pour la série A.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par
$$f(x) = x\,e^{x}.$$
Quelle est la nature des deux branches infinies de la courbe représentative de $f$ ?

- a) Asymptote horizontale $y=0$ en $-\infty$, branche parabolique de direction $(Ox)$ en $+\infty$
- b) Branche parabolique de direction $(Oy)$ en $-\infty$ et en $+\infty$
- c) Asymptote horizontale $y=0$ en $-\infty$, branche parabolique de direction $(Oy)$ en $+\infty$
- d) Asymptote horizontale $y=0$ en $-\infty$, asymptote oblique $y=x$ en $+\infty$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour préciser la nature d'une branche infinie, on étudie d'abord $\lim f(x)$ : si elle est finie, on obtient une asymptote horizontale. Si elle est infinie, on étudie $\dfrac{f(x)}{x}$ : une limite infinie donne une branche parabolique de direction $(Oy)$, une limite nulle donne la direction $(Ox)$, une limite finie non nulle $a$ oriente vers une éventuelle direction $y=ax$.

### Corrigé
**En $+\infty$.** $x\to+\infty$ et $e^{x}\to+\infty$, donc par produit $\lim_{x\to+\infty} f(x) = +\infty$.
On calcule $\dfrac{f(x)}{x} = e^{x}$ pour $x\neq0$, donc $\lim_{x\to+\infty} \dfrac{f(x)}{x} = +\infty$.
Cette limite étant infinie, la courbe de $f$ présente une **branche parabolique de direction $(Oy)$** au voisinage de $+\infty$.

**En $-\infty$.** Posons $t=-x$, avec $t\to+\infty$ quand $x\to-\infty$ :
$$f(x) = -t\,e^{-t} = -\dfrac{t}{e^{t}}.$$
Par croissances comparées, $\dfrac{t}{e^{t}}\to 0$, donc $\lim_{x\to-\infty} f(x) = 0$.
Cette limite étant finie, la droite d'équation $y=0$ (l'axe des abscisses) est **asymptote horizontale** à la courbe de $f$ au voisinage de $-\infty$.

**Conclusion.** Asymptote horizontale $y=0$ en $-\infty$, branche parabolique de direction $(Oy)$ en $+\infty$.

### Pourquoi les autres réponses sont fausses

- **a)** Règle inversée : $\dfrac{f(x)}{x}\to+\infty$ donne la direction $(Oy)$, et non $(Ox)$.
- **b)** En $-\infty$, la forme $(-\infty)\times0$ est indéterminée : on ne peut pas conclure $f\to-\infty$ ; les croissances comparées donnent $f\to0$.
- **d)** Une asymptote oblique $y=x$ exigerait $\dfrac{f(x)}{x}\to1$ ; ici cette limite est infinie.

</details>

Avis : 

---

## 23. `cqc-equiprobabilite-faible-0` (séries A/D)

**Remarque du relecteur :** Question de niveau Seconde, très facile pour le BAC.

**Énoncé :**

On lance un dé cubique équilibré. Quelle est la probabilité d'obtenir un nombre pair supérieur ou égal à $3$ ?

- a) $\dfrac12$
- b) $\dfrac13$
- c) $\dfrac23$
- d) $\dfrac56$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

En situation d'équiprobabilité, $P(A)=\dfrac{\text{nombre de cas favorables}}{\text{nombre de cas possibles}}$. Un nombre « pair supérieur ou égal à $3$ » doit vérifier les DEUX conditions à la fois.

### Corrigé

Cas possibles : $6$. Cas favorables : $\{4\,;6\}$, soit $2$ ($2$ est pair mais inférieur à $3$).

$P=\dfrac26=\dfrac13$.

### Pourquoi les autres réponses sont fausses

- **a)** On n'a tenu compte que de la parité ($\{2\,;4\,;6\}$), en oubliant la condition « supérieur ou égal à $3$ ».
- **c)** On n'a tenu compte que de la condition « supérieur ou égal à $3$ » ($\{3\,;4\,;5\,;6\}$).
- **d)** On a compté les nombres pairs OU supérieurs ou égaux à $3$ ($\{2\,;3\,;4\,;5\,;6\}$), au lieu de ceux qui vérifient les deux conditions.

</details>

Avis : 

---

## 24. `cqc-fonction-exponentielle-elevee-0` (séries A/C/D/E/TI)

**Remarque du relecteur :** LIMITE : fonction exponentielle de base 3 et raisonnement par monotonie, haut du programme de la série A.

**Énoncé :**

Soit $k$ la fonction définie sur $\mathbb{R}$ par $k(x) = 3^{x-1} + 2x - 3$.

Quel est l'ensemble des réels $x$ pour lesquels $k(x)>0$ ?

- a) $]1\,;\,+\infty[$
- b) $]-\infty\,;\,1[$
- c) $\left]\dfrac32\,;\,+\infty\right[$
- d) $[1\,;\,+\infty[$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'une expression n'est pas factorisable directement, on peut déterminer son signe en étudiant les variations de la fonction associée : on calcule sa dérivée, on établit son signe, on en déduit le sens de variation, puis on localise un zéro évident de la fonction. Si la fonction est strictement monotone sur tout son ensemble de définition, ce zéro unique sépare alors l'intervalle en deux parties de signes opposés.

### Corrigé

**Recherche d'un zéro évident.**

$$k(1) = 3^{1-1}+2\times1-3 = 3^{0}+2-3 = 1+2-3=0$$

**Dérivée.**
En écrivant $3^{x-1}=e^{(x-1)\ln3}$, on obtient $\left(3^{x-1}\right)' = \ln3\times3^{x-1}$. La dérivée de $2x-3$ vaut $2$. Donc :

$$k'(x) = \ln3\times3^{x-1}+2$$

**Signe de $k'(x)$.**
Pour tout réel $x$, $3^{x-1}>0$ et $\ln3>0$ (car $3>1$), donc $\ln3\times3^{x-1}>0$. En ajoutant $2>0$, on obtient :

$$k'(x) = \underbrace{\ln3\times3^{x-1}}_{>0} + \underbrace{2}_{>0} > 0 \quad \text{pour tout } x\in\mathbb{R}$$

$k'$ est donc strictement positive sur $\mathbb{R}$ tout entier : **$k$ est strictement croissante sur $\mathbb{R}$.**

**Conclusion sur le signe de $k$.**
Comme $k$ est strictement croissante sur $\mathbb{R}$ et que $k(1)=0$ :

- pour $x<1$ : $k(x) < k(1) = 0$, donc $k(x)<0$ ;
- pour $x=1$ : $k(x)=0$ ;
- pour $x>1$ : $k(x) > k(1) = 0$, donc $k(x)>0$.

**$k(x)$ est donc négatif sur $]-\infty,1[$, nul en $x=1$, et positif sur $]1,+\infty[$.**

L'ensemble cherché est donc $]1\,;\,+\infty[$.

### Pourquoi les autres réponses sont fausses

- **b)** c'est l'ensemble où $k(x)<0$ : on a inversé le sens de variation (ou le signe) de part et d'autre du zéro $x=1$.
- **c)** on n'a étudié que le signe de $2x-3$ en oubliant le terme $3^{x-1}$, qui est strictement positif ; par exemple $k(1{,}2)>0$ alors que $1{,}2<\dfrac32$.
- **d)** le crochet est fermé en $1$ alors que $k(1)=0$ : l'inégalité demandée est stricte.

</details>

Avis : 

---

## 25. `cqc-fonction-exponentielle-faible-0` (séries A/C/D/E/TI)

**Remarque du relecteur :** LIMITE : écriture a^x=e^{x ln a} pour la série A.

**Modification de fond lors de la conversion** (question réduite ou méthode remplacée) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x) = 3^{2x-1}$. Laquelle des écritures suivantes est égale à $f(x)$ pour tout réel $x$ ?

- a) $e^{(2\ln3)x+\ln3}$
- b) $e^{(2\ln3)x-\ln3}$
- c) $e^{2x\ln3-1}$
- d) $e^{2x-\ln3}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une base $a>0$ différente de $e$, on utilise la conversion $a^{x} = e^{x\ln a}$, valable pour tout réel $x$ (car $a=e^{\ln a}$, donc $a^{x}=(e^{\ln a})^{x}=e^{x\ln a}$). Cette écriture permet de retrouver, pour une base quelconque, toutes les propriétés déjà connues des fonctions exponentielles de base $e$.

### Corrigé

On applique la conversion $3=e^{\ln3}$ :

$$f(x) = 3^{2x-1} = \left(e^{\ln3}\right)^{2x-1} = e^{(2x-1)\ln3} = e^{(2\ln3)x-\ln3}$$

On a donc $f(x)=e^{\alpha x+\beta}$ avec $\alpha=2\ln3$ et $\beta=-\ln3$.

Contrôle : $f(0)=3^{-1}=\dfrac13$ et $e^{-\ln3}=\dfrac13$ ; $f(3)=3^{5}=243$ et $e^{6\ln3-\ln3}=e^{5\ln3}=3^5=243$.

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe en développant $(2x-1)\ln3$ : le terme constant vaut $-\ln3$.
- **c)** on n'a multiplié par $\ln3$ que le terme $2x$ ; c'est tout l'exposant $2x-1$ qui est multiplié par $\ln 3$.
- **d)** on a oublié le facteur $\ln3$ devant $2x$ ; par exemple en $x=1$ on obtiendrait $\dfrac{e^2}{3}$ au lieu de $3$.

</details>

Avis : 

---

## 26. `cqc-fonction-exponentielle-moyenne-0` (séries A/C/D/E/TI)

**Remarque du relecteur :** LIMITE : les fonctions x↦a^x sont à la limite du programme de la série A (à écrire e^{x ln a} si besoin).

**Énoncé :**

Deux cultures de bactéries sont observées en laboratoire à partir d'un même instant initial $x=0$ (exprimé en heures). La première culture compte une population (en milliers d'individus) modélisée par $P(x) = 2^{x}$, et la seconde par $Q(x) = 5^{x}$, pour tout $x \geqslant 0$.

Quel est l'ensemble des solutions, dans $[0\,;\,+\infty[$, de l'inéquation $Q(x) > P(x)$ ?

- a) $[0\,;\,+\infty[$
- b) $]\ln5-\ln2\,;\,+\infty[$
- c) $]0\,;\,+\infty[$
- d) $\left]\dfrac{\ln2}{\ln5}\,;\,+\infty\right[$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour comparer deux fonctions exponentielles de bases différentes $a^{x}$ et $b^{x}$, on les convertit toutes deux en base $e$ grâce à $a^{x}=e^{x\ln a}$ et $b^{x}=e^{x\ln b}$. Comme la fonction exponentielle de base $e$ est strictement croissante, l'inégalité entre $e^{x\ln a}$ et $e^{x\ln b}$ équivaut à l'inégalité entre les exposants $x\ln a$ et $x\ln b$, ce qui ramène la comparaison à l'étude du signe de $x(\ln a-\ln b)$.

### Corrigé

On veut résoudre $5^{x} > 2^{x}$, soit, en écrivant chaque membre en base $e$ :

$$e^{x\ln5} > e^{x\ln2}$$

La fonction exponentielle (de base $e$) étant strictement croissante sur $\mathbb{R}$, cette inégalité équivaut à :

$$x\ln5 > x\ln2 \iff x(\ln5-\ln2) > 0$$

Or $\ln5 > \ln2$ (la fonction $\ln$ est strictement croissante et $5>2$), donc $\ln5-\ln2>0$. En divisant les deux membres par ce réel strictement positif, le sens de l'inégalité est conservé :

$$x > 0$$

**La seconde culture dépasse strictement la première dès que $x>0$**, c'est-à-dire pour toute durée strictement positive après l'instant initial (à $x=0$, les deux cultures sont égales : $P(0)=Q(0)=1$).

L'ensemble des solutions est donc $]0\,;\,+\infty[$.

### Pourquoi les autres réponses sont fausses

- **a)** en $x=0$, $P(0)=Q(0)=1$ : l'inégalité stricte n'est pas vérifiée, $0$ doit être exclu.
- **b)** on a transformé $x(\ln5-\ln2)>0$ en $x>\ln5-\ln2$ au lieu de diviser par $\ln5-\ln2$.
- **d)** on a « divisé » les deux membres de $x\ln5>x\ln2$ comme dans une équation affine ; or $x$ est en facteur des deux côtés et le second membre est nul après regroupement.

</details>

Avis : 

---

## 27. `cqc-integration-par-parties-elevee-0` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite ou méthode remplacée) : à examiner de près.

**Énoncé :**

Quelle est la valeur exacte de l'intégrale $$L=\int_0^1 x^{2}e^{-x}\,dx\ ?$$

- a) $1-\dfrac{3}{e}$
- b) $2-\dfrac{3}{e}$
- c) $2-\dfrac{4}{e}$
- d) $2-\dfrac{5}{e}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand le polynôme est de degré $2$, une seule intégration par parties ne suffit pas : on l'applique une première fois pour abaisser le degré du polynôme de $2$ à $1$, puis une seconde fois pour l'abaisser de $1$ à $0$. Chaque étape suit $\int_a^b u(x)v'(x)\,dx=\big[u(x)v(x)\big]_a^b-\int_a^b u'(x)v(x)\,dx$, avec $u$ égal au facteur polynomial.

### Corrigé
**Première intégration par parties.** On pose $u(x)=x^2$ et $v'(x)=e^{-x}$, d'où $u'(x)=2x$ et $v(x)=-e^{-x}$.
$$L=\big[-x^{2}e^{-x}\big]_0^1+2\int_0^1 xe^{-x}\,dx=-e^{-1}+2M,\qquad M=\int_0^1 xe^{-x}\,dx.$$
**Seconde intégration par parties** (sur $M$). On pose $u(x)=x$ et $v'(x)=e^{-x}$, d'où $u'(x)=1$ et $v(x)=-e^{-x}$.
$$M=\big[-xe^{-x}\big]_0^1+\int_0^1 e^{-x}\,dx=-e^{-1}+\big[-e^{-x}\big]_0^1=-e^{-1}+\big(-e^{-1}+1\big)=1-2e^{-1}.$$
**Conclusion.**
$$L=-e^{-1}+2\big(1-2e^{-1}\big)=2-5e^{-1}=2-\dfrac{5}{e}.$$

### Pourquoi les autres réponses sont fausses

- **a)** on a oublié le facteur $2$ (venant de $u'(x)=2x$) devant la seconde intégrale : $L=-e^{-1}+M$ au lieu de $-e^{-1}+2M$.
- **b)** dans le calcul de $M$, on a oublié le crochet $\big[-xe^{-x}\big]_0^1=-e^{-1}$, d'où $M=1-e^{-1}$ au lieu de $1-2e^{-1}$.
- **c)** on a oublié le crochet de la première intégration par parties, $\big[-x^2e^{-x}\big]_0^1=-e^{-1}$, et gardé seulement $2M$.

</details>

Avis : 

---

## 28. `cqc-integration-par-parties-faible-0` (séries C/D/E)

**Énoncé :**

Quelle est la valeur exacte de l'intégrale $$I=\int_0^1 x\,e^{2x}\,dx\ ?$$

- a) $\dfrac{e^{2}+1}{4}$
- b) $\dfrac{e^{2}-1}{4}$
- c) $e^{2}+1$
- d) $\dfrac{3e^{2}-1}{4}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
La formule d'intégration par parties s'écrit $\displaystyle\int_a^b u(x)v'(x)\,dx=\big[u(x)v(x)\big]_a^b-\int_a^b u'(x)v(x)\,dx$. Quand l'intégrande est un produit d'un polynôme et d'une exponentielle, on choisit $u$ égal au polynôme, dont la dérivée simplifie le degré, et $v'$ égal à la fonction exponentielle, dont une primitive est immédiate.

### Corrigé
On pose $u(x)=x$ et $v'(x)=e^{2x}$, d'où $u'(x)=1$ et $v(x)=\dfrac{1}{2}e^{2x}$.
$$I=\Big[\dfrac{x}{2}e^{2x}\Big]_0^1-\int_0^1\dfrac12e^{2x}\,dx=\dfrac12e^{2}-\Big[\dfrac14e^{2x}\Big]_0^1=\dfrac12e^{2}-\Big(\dfrac14e^{2}-\dfrac14\Big)=\dfrac14e^{2}+\dfrac14.$$
Donc $I=\dfrac{e^{2}+1}{4}$.

### Pourquoi les autres réponses sont fausses

- **b)** erreur de signe en retranchant $\Big[\dfrac14e^{2x}\Big]_0^1=\dfrac14e^2-\dfrac14$ : le terme $-\left(-\dfrac14\right)$ donne $+\dfrac14$.
- **c)** on a pris $v(x)=2e^{2x}$, c'est-à-dire la dérivée de $e^{2x}$ au lieu d'une primitive $\dfrac12e^{2x}$.
- **d)** on a ajouté l'intégrale $\displaystyle\int_0^1\dfrac12e^{2x}\,dx$ au lieu de la retrancher dans la formule d'intégration par parties.

</details>

Avis : 

---

## 29. `cqc-inequation-exponentielle-elevee-0` (séries A/C/E)

**Énoncé :**

Quel est l'ensemble des solutions dans $\mathbb{R}$ de l'inéquation $$e^{3x}+2e^{2x}-48e^{x}\geqslant0\ ?$$

- a) $]-\infty\,;\,\ln6]$
- b) $]\ln6\,;\,+\infty[$
- c) $[\ln6\,;\,+\infty[$
- d) $[\ln8\,;\,+\infty[$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsque l'inéquation combine $e^{3x}$, $e^{2x}$ et $e^{x}$, le changement de variable $X=e^{x}>0$ ne conduit pas directement à une inéquation du second degré, mais à une inéquation du troisième degré en $X$. Il faut alors factoriser cette expression par la puissance commune de $X$ - jamais nulle, puisque $X=e^x$ est toujours strictement positif - pour se ramener à l'étude du signe d'un trinôme du second degré ; multiplier ou diviser une inégalité par une quantité strictement positive, comme $X$ ici, ne change jamais son sens.

### Corrigé

On pose $X=e^{x}$, avec $X>0$. Comme $e^{3x}=X^3$, $e^{2x}=X^2$ et $e^{x}=X$, l'inéquation devient :

$$X^3+2X^2-48X\geqslant0$$

On factorise par $X$ :

$$X\left(X^2+2X-48\right)\geqslant0$$

Comme $X=e^x>0$ pour tout réel $x$, le facteur $X$ est toujours strictement positif : le signe du produit est donc exactement celui du second facteur, et l'inéquation équivaut à :

$$X^2+2X-48\geqslant0$$

Le discriminant vaut $\Delta=2^2-4\times1\times(-48)=4+192=196$, donc $\sqrt{\Delta}=14$ et :

$$X=\dfrac{-2-14}{2}=-8 \quad \text{ou} \quad X=\dfrac{-2+14}{2}=6$$

Comme $a=1>0$, le trinôme $X^2+2X-48$ est positif ou nul à l'extérieur des racines. L'inégalité étant large, les racines sont incluses : l'ensemble solution en $X$ est $X\leqslant-8$ ou $X\geqslant6$.

**Filtrage des solutions :** la condition $X=e^x>0$ élimine entièrement la branche $X\leqslant-8$. Seule $X\geqslant6$ est recevable.

**Retour à $x$ :** $\ln$ étant strictement croissante, $X\geqslant6 \iff x\geqslant\ln6$.

**Vérification :** pour $x=\ln6$ (borne), $e^x=6$, $e^{2x}=36$, $e^{3x}=216$, donc $216+2\times36-48\times6=216+72-288=0$, qui vérifie bien l'inégalité large : la borne est incluse ; pour $x=2$ (à l'extérieur, $>\ln6\approx1{,}792$), $e^2\approx7{,}389$, $e^4\approx54{,}598$, $e^6\approx403{,}429$, donc $403{,}429+2\times54{,}598-48\times7{,}389\approx403{,}429+109{,}196-354{,}672=157{,}953\geqslant0$ ; pour $x=0$ (à l'intérieur, $<\ln6$), $1+2\times1-48\times1=1+2-48=-45$, qui n'est pas $\geqslant0$, ce qui confirme bien que cette valeur est exclue.

**L'ensemble solution est $S=[\ln6\,;\,+\infty[$.**

### Pourquoi les autres réponses sont fausses

- **a)** on a retenu l'intervalle situé du mauvais côté de la racine : le trinôme $X^2+2X-48$ (de coefficient $a=1>0$) est positif à l'extérieur des racines.
- **b)** l'inégalité est large : en $x=\ln6$ l'expression vaut $0$, donc $\ln6$ est solution.
- **d)** erreur de signe dans les racines (on a trouvé $8$ et $-6$ au lieu de $6$ et $-8$) ; en $x=\ln 7$ par exemple l'inégalité est vérifiée.

</details>

Avis : 

---

## 30. `cqc-logarithme-neperien-elevee-0` (séries A/C)

**Énoncé :**

Quelle est la solution, dans $\left]0\,;\,+\infty\right[^3$, du système d'équations d'inconnues $x$, $y$, $z$ suivant ?
$$\begin{cases} \ln x + \ln y + \ln z = 6 \\ \ln x - \ln y + 2\ln z = 7 \\ 2\ln x + \ln y - \ln z = 2 \end{cases}$$

- a) $x=2$, $y=1$, $z=3$
- b) $x=e^{2}$, $y=e$, $z=e^{3}$
- c) $x=\ln2$, $y=0$, $z=\ln3$
- d) $x=e^{2}$, $y=1$, $z=e^{3}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Face à un système où les inconnues $x$, $y$, $z$ n'apparaissent qu'à travers $\ln x$, $\ln y$, $\ln z$, on pose le changement de variable $X = \ln x$, $Y = \ln y$, $Z = \ln z$ : le système devient un système linéaire classique en $X$, $Y$, $Z$, que l'on résout par substitution ou combinaison. Une fois $X$, $Y$, $Z$ obtenus, on revient aux inconnues d'origine par $x = e^{X}$, $y = e^{Y}$, $z = e^{Z}$ ; ces valeurs sont automatiquement strictement positives puisque l'exponentielle ne prend que des valeurs positives.

### Corrigé

**Changement de variable** : on pose $X = \ln x$, $Y = \ln y$, $Z = \ln z$. Le système devient :
$$\begin{cases} X + Y + Z = 6 \\ X - Y + 2Z = 7 \\ 2X + Y - Z = 2 \end{cases}$$

On note (1), (2) et (3) respectivement la première, la deuxième et la troisième équation de ce système.

De (1) : $X = 6 - Y - Z$.

En remplaçant dans (2) :
$$(6 - Y - Z) - Y + 2Z = 7 \iff 6 - 2Y + Z = 7 \iff Z = 1 + 2Y$$

En remplaçant dans (3) :
$$2(6 - Y - Z) + Y - Z = 2 \iff 12 - 2Y - 2Z + Y - Z = 2 \iff Y + 3Z = 10$$

En substituant $Z = 1 + 2Y$ dans $Y + 3Z = 10$ :
$$Y + 3(1 + 2Y) = 10 \iff Y + 3 + 6Y = 10 \iff 7Y = 7 \iff Y = 1$$

D'où $Z = 1 + 2 \times 1 = 3$, puis $X = 6 - 1 - 3 = 2$.

**Retour aux inconnues d'origine** :
$$x = e^{X} = e^{2} \qquad y = e^{Y} = e^{1} = e \qquad z = e^{Z} = e^{3}$$

Ces trois valeurs sont strictement positives : elles appartiennent bien à $\left]0\,;\,+\infty\right[$, la solution est donc valable.

**Vérification** : $\ln(e^2) + \ln(e) + \ln(e^3) = 2+1+3 = 6$ ; $\ln(e^2) - \ln(e) + 2\ln(e^3) = 2-1+6=7$ ; $2\ln(e^2)+\ln(e)-\ln(e^3) = 4+1-3=2$.

Le système admet donc pour unique solution : $x = e^{2}$, $y = e$, $z = e^{3}$.

### Pourquoi les autres réponses sont fausses

- **a)** ce sont les valeurs de $X=\ln x$, $Y=\ln y$, $Z=\ln z$ : on a oublié de revenir aux inconnues par $x=e^X$, $y=e^Y$, $z=e^Z$.
- **c)** on est revenu aux inconnues avec $x=\ln X$ au lieu de $x=e^X$ ; de plus $y=0$ n'est pas dans $]0\,;\,+\infty[$.
- **d)** on a confondu $e^{1}=e$ avec $e^{0}=1$ ; avec $y=1$ on aurait $\ln y=0$ et la première équation donnerait $5$ au lieu de $6$.

</details>

Avis : 

---

## 31. `cqc-loi-binomiale-elevee-5` (séries A/C/D/E)

**Remarque du relecteur :** LIMITE : loi binomiale avec somme de trois termes pour la série A.

**Énoncé :**

Un laboratoire médical analyse 6 échantillons sanguins prélevés sur des patients différents, de façon indépendante les uns des autres. On admet que, pour des raisons épidémiologiques, chaque échantillon a une probabilité $p=0{,}3$ d'être positif à un test donné, cette probabilité étant la même pour les 6 échantillons. On note $X$ le nombre d'échantillons positifs parmi les 6 analysés.

Quelle est la probabilité, arrondie à $10^{-3}$ près, qu'entre 2 et 4 échantillons (bornes incluses) soient positifs ?

- a) $0{,}569$
- b) $0{,}185$
- c) $0{,}580$
- d) $0{,}035$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Répéter $n$ fois, de façon indépendante, une même épreuve à deux issues de probabilité $p$ et $1-p$ définit un schéma de Bernoulli ; le nombre de succès suit alors une loi binomiale $\mathcal B(n,p)$ avec $P(X=k)=\binom{n}{k}p^{k}(1-p)^{n-k}$. Une probabilité du type $P(a\leqslant X\leqslant b)$ se calcule en sommant les probabilités ponctuelles incompatibles $P(X=a)+P(X=a+1)+\cdots+P(X=b)$.

### Corrigé

**1. Identification du schéma.** Chaque analyse est une épreuve à deux issues : « échantillon positif » (succès, probabilité $p=0{,}3$) ou « échantillon négatif » (échec, probabilité $0{,}7$), cette probabilité étant supposée identique pour les 6 échantillons (donnée par l'énoncé). Les analyses sont indépendantes les unes des autres, puisque prélevées sur des patients différents (donné par l'énoncé). On a donc un schéma de Bernoulli répété $n=6$ fois de paramètre $p=0{,}3$, soit $X\sim\mathcal B(6;0{,}3)$.

**2. Calcul de $P(2\leqslant X\leqslant4)$.**
$$P(2\leqslant X\leqslant4)=P(X=2)+P(X=3)+P(X=4)$$

$P(X=2)=\binom{6}{2}\times0{,}3^{2}\times0{,}7^{4}=15\times0{,}09\times0{,}2401=0{,}324135$

$P(X=3)=\binom{6}{3}\times0{,}3^{3}\times0{,}7^{3}=20\times0{,}027\times0{,}343=0{,}18522$

$P(X=4)=\binom{6}{4}\times0{,}3^{4}\times0{,}7^{2}=15\times0{,}0081\times0{,}49=0{,}059535$

$$P(2\leqslant X\leqslant4)=0{,}324135+0{,}18522+0{,}059535=0{,}568890$$

**Vérification numérique.** En calculant aussi $P(X=0)=0{,}7^{6}=0{,}117649$, $P(X=1)=\binom{6}{1}\times0{,}3\times0{,}7^{5}=0{,}302526$, $P(X=5)=\binom{6}{5}\times0{,}3^{5}\times0{,}7=0{,}010206$ et $P(X=6)=0{,}3^{6}=0{,}000729$, la somme des sept probabilités vaut $0{,}117649+0{,}302526+0{,}324135+0{,}18522+0{,}059535+0{,}010206+0{,}000729=1$, ce qui confirme la cohérence de l'ensemble du calcul.

Arrondie à $10^{-3}$ près, il y a donc une probabilité de $0{,}569$ que le nombre d'échantillons positifs parmi les 6 soit compris entre 2 et 4, soit environ 56,9 % de chances.

### Pourquoi les autres réponses sont fausses

- **b)** c'est $P(X=3)$ seul : on a exclu les bornes $2$ et $4$, alors qu'elles sont incluses.
- **c)** c'est $P(X\geqslant2)$ : on a oublié de s'arrêter à $4$ et ajouté $P(X=5)$ et $P(X=6)$.
- **d)** on a oublié les coefficients binomiaux $\binom{6}{k}$ dans chaque terme.

</details>

Avis : 

---

## 32. `cqc-loi-binomiale-faible-0` (séries A/C/D/E)

**Remarque du relecteur :** La variable X est définie mais inutilisée dans la question ; on peut la retirer ou l'utiliser (P(X>=1)).

**Modification de fond lors de la conversion** (question réduite ou méthode remplacée) : à examiner de près.

**Énoncé :**

On dispose d'un jeu de 32 cartes contenant exactement 4 rois. On tire une carte au hasard, on note sa valeur, puis on la remet dans le jeu avant de mélanger et de tirer à nouveau. On répète cette expérience 3 fois de suite, dans les mêmes conditions et indépendamment les unes des autres. On note $X$ le nombre de tirages ayant donné un roi parmi les 3 tirages effectués.

Quelle est la probabilité qu'au moins un des 3 tirages donne un roi, c'est-à-dire $P(X\geqslant 1)$ ?

- a) $\dfrac{147}{512}$
- b) $\dfrac{169}{512}$
- c) $\dfrac{3}{8}$
- d) $\dfrac{511}{512}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Répéter $n$ fois, de façon indépendante, une même épreuve à deux issues de probabilité $p$ et $1-p$ définit un schéma de Bernoulli ; le nombre de succès suit alors une loi binomiale $\mathcal B(n,p)$, et pour tout entier $k$ compris entre $0$ et $n$, $P(X=k)=\binom{n}{k}p^{k}(1-p)^{n-k}$. L'événement « au moins un succès » a pour contraire « aucun succès », d'où $P(X\geqslant1)=1-P(X=0)$.

### Corrigé

**Identification du schéma de Bernoulli.**
Chaque tirage constitue une épreuve à deux issues : « obtenir un roi » (succès, probabilité $p=\dfrac{4}{32}=\dfrac18$) ou « ne pas obtenir un roi » (échec, probabilité $1-p=\dfrac78$). La carte tirée étant remise dans le jeu avant le tirage suivant, la composition du jeu est identique à chaque tirage, et la remise et le mélange rendent les 3 tirages **indépendants**. On a donc $X\sim\mathcal B\left(3,\dfrac18\right)$.

**Calcul.**
$$P(X=0)=\binom{3}{0}\left(\dfrac18\right)^{0}\left(\dfrac78\right)^{3}=\dfrac{343}{512}$$

$$P(X\geqslant1)=1-P(X=0)=1-\dfrac{343}{512}=\dfrac{169}{512}\approx0{,}330$$

**Vérification.** Avec la loi complète, $P(X=1)=\dfrac{147}{512}$, $P(X=2)=\dfrac{21}{512}$, $P(X=3)=\dfrac{1}{512}$, et $147+21+1=169$.

### Pourquoi les autres réponses sont fausses

- **a)** c'est $P(X=1)$, la probabilité d'obtenir exactement un roi ; « au moins un » inclut aussi $X=2$ et $X=3$.
- **c)** on a additionné $3$ fois la probabilité $\dfrac18$ d'un roi, comme si les événements « roi au tirage $i$ » étaient incompatibles.
- **d)** c'est $1-P(X=3)$ : on a pris pour contraire « trois rois » au lieu de « aucun roi ».

</details>

Avis : 

---

## 33. `cqc-primitive-avec-logarithme-elevee-5` (séries D)

**Modification de fond lors de la conversion** (question réduite ou méthode remplacée) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x) = \dfrac{6e^{x}}{3e^{x}+1} - \dfrac{e^{x}}{e^{x}+2}$. On admet que $f$ est positive sur $[0\,;\,\ln 2]$. Quelle est la valeur exacte de l'aire $\mathcal{A}$, en unités d'aire, du domaine plan délimité par la courbe de $f$, l'axe des abscisses et les droites d'équations $x=0$ et $x=\ln 2$ ?

- a) $\ln\left(\dfrac{21}{16}\right)$
- b) $\ln\left(\dfrac{49}{12}\right)$
- c) $\ln\left(\dfrac{64}{147}\right)$
- d) $\ln\left(\dfrac{147}{64}\right)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand une fonction est la différence de deux termes de la forme $\dfrac{u'}{u}$, on primitive chaque terme séparément en $\ln(u)$, puis on soustrait les deux résultats. Si le numérateur d'un terme n'est pas exactement la dérivée du dénominateur, il faut d'abord le factoriser pour faire apparaître le bon coefficient multiplicatif devant $\dfrac{u'}{u}$.

### Corrigé

**Premier terme.** Posons $u_1(x) = 3e^{x}+1$, donc $u_1'(x) = 3e^{x}$. Le numérateur du premier terme est $6e^{x} = 2\times 3e^{x} = 2\,u_1'(x)$ : il faut donc factoriser $6e^x$ par $2$ pour faire apparaître $u_1'$. Comme $u_1(x)=3e^x+1>0$ sur $\mathbb{R}$ :

$$\dfrac{6e^{x}}{3e^{x}+1} = 2\times\dfrac{u_1'(x)}{u_1(x)} \quad\Longrightarrow\quad \text{primitive} = 2\ln(3e^{x}+1)$$

**Second terme.** Posons $u_2(x) = e^{x}+2$, donc $u_2'(x) = e^{x}$, qui est exactement le numérateur du second terme. Comme $u_2(x)=e^x+2>0$ sur $\mathbb{R}$ :

$$\dfrac{e^{x}}{e^{x}+2} = \dfrac{u_2'(x)}{u_2(x)} \quad\Longrightarrow\quad \text{primitive} = \ln(e^{x}+2)$$

**Primitive de $f$.** Par différence :

$$F(x) = 2\ln(3e^{x}+1) - \ln(e^{x}+2)$$

**Calcul de l'aire.** Comme $f$ est positive sur $[0\,;\,\ln 2]$ (donnée admise), l'aire est directement $\mathcal{A} = F(\ln 2) - F(0)$.

En $x=\ln 2$, $e^{x}=2$ :

$$F(\ln 2) = 2\ln(3\times2+1) - \ln(2+2) = 2\ln 7 - \ln 4$$

En $x=0$, $e^{x}=1$ :

$$F(0) = 2\ln(3\times1+1) - \ln(1+2) = 2\ln 4 - \ln 3$$

D'où :

$$\mathcal{A} = \big(2\ln 7 - \ln 4\big) - \big(2\ln 4 - \ln 3\big) = 2\ln 7 - 3\ln 4 + \ln 3$$

**Simplification.** En remplaçant $3\ln 4 = 3\times2\ln2=6\ln2=\ln(2^{6})=\ln 64$ et $2\ln7=\ln49$ :

$$\mathcal{A} = \ln 49 - \ln 64 + \ln 3 = \ln\!\left(\dfrac{49\times3}{64}\right) = \ln\!\left(\dfrac{147}{64}\right)$$

L'aire cherchée est donc $\mathcal{A} = \ln\!\left(\dfrac{147}{64}\right)$ unités d'aire, soit environ $\mathcal{A} \approx 0{,}83$ u.a.

**Vérification** : $F'(x) = 2\times\dfrac{3e^{x}}{3e^{x}+1} - \dfrac{e^{x}}{e^{x}+2} = \dfrac{6e^{x}}{3e^{x}+1} - \dfrac{e^{x}}{e^{x}+2} = f(x)$. Conforme.

### Pourquoi les autres réponses sont fausses

- **a)** on a oublié le coefficient $2$ : $6e^x=2\times3e^x$, donc une primitive du premier terme est $2\ln(3e^x+1)$ et non $\ln(3e^x+1)$.
- **b)** erreur de signe en retranchant $F(0)=2\ln4-\ln3$ : on a écrit $-2\ln4-\ln3$ au lieu de $-2\ln4+\ln3$.
- **c)** on a calculé $F(0)-F(\ln2)$ ; une aire est positive et vaut $F(\ln2)-F(0)$ quand $f\geqslant0$.

</details>

Avis : 

---

## 34. `cqc-primitive-avec-logarithme-moyenne-2` (séries D)

**Énoncé :**

Soit $f$ la fonction définie sur $]0\,;\,+\infty[$ par $f(x) = \ln(x)$. Quelle est la valeur exacte de l'aire $\mathcal{A}$, en unités d'aire, du domaine plan délimité par la courbe de $f$, l'axe des abscisses et les droites d'équations $x=1$ et $x=4$ ?

- a) $8\ln 2-5$
- b) $8\ln 2-3$
- c) $8\ln 2$
- d) $8\ln 2-4$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La primitive de $\ln(x)$ ne fait pas partie du formulaire usuel : elle s'obtient par intégration par parties, en posant $u(x)=\ln x$ (donc $u'(x)=\dfrac1x$) et $v'(x)=1$ (donc $v(x)=x$). La formule $\displaystyle\int uv' = \big[uv\big] - \displaystyle\int u'v$ donne alors $\displaystyle\int \ln x\,dx = x\ln x - x + C$.

### Corrigé

**Signe de $f$ sur $[1\,;\,4]$.** Pour $x\geqslant 1$, $\ln(x)\geqslant 0$ (le logarithme népérien s'annule en $1$ et croît ensuite). Donc $f(x)\geqslant 0$ sur $[1\,;\,4]$, et l'aire est directement donnée par l'intégrale de $f$.

**Primitive par IPP.** Posons $u(x) = \ln x$ et $v'(x) = 1$, donc $u'(x) = \dfrac1x$ et $v(x) = x$.

$$\int \ln(x)\,dx = x\ln x - \int x\times\dfrac1x\,dx = x\ln x - \int 1\,dx = x\ln x - x + C$$

Une primitive de $f$ sur $]0\,;\,+\infty[$ est donc $F(x) = x\ln x - x$.

**Calcul de l'aire.**

$$\mathcal{A} = \int_{1}^{4} \ln(x)\,dx = \Big[x\ln x - x\Big]_{1}^{4} = \big(4\ln 4 - 4\big) - \big(1\times\ln 1 - 1\big) = \big(4\ln 4-4\big) - (0-1)$$

$$\mathcal{A} = 4\ln 4 - 3 = 8\ln 2 - 3$$

L'aire cherchée est donc $\mathcal{A} = 8\ln 2 - 3$ unités d'aire (soit environ $2{,}55$ u.a.).

**Vérification** : $F'(x) = \ln x + x\times\dfrac1x - 1 = \ln x + 1 - 1 = \ln x = f(x)$. Conforme.

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe à la borne $1$ : $F(1)=1\times\ln1-1=-1$, et retrancher $-1$ revient à ajouter $1$.
- **c)** on a pris $x\ln x$ comme primitive de $\ln x$ en oubliant le terme $-x$ ; la dérivée de $x\ln x$ est $\ln x+1$.
- **d)** on a oublié de retrancher la valeur de la primitive en $1$, $F(1)=-1$, qui n'est pas nulle.

</details>

Avis : 

---

## 35. `cqc-racine-double-elevee-0` (séries C/D/E/TI)

**Énoncé :**

On considère l'équation différentielle $(E_6) : y'' - 2y' + y = 0$, où $y$ est une fonction deux fois dérivable sur $\mathbb{R}$.

Quelle est la solution $g$ de $(E_6)$ vérifiant $g(0) = -1$ et $g'(0) = 4$ ?

- a) $g(x)=(-1+5x)e^{x}$
- b) $g(x)=(-1+4x)e^{x}$
- c) $g(x)=(-1+3x)e^{x}$
- d) $g(x)=(-1+3x)e^{-x}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Une fonction $f_\beta : x \mapsto e^{\beta x}$ est solution de $y'' + ay' + by = 0$ si et seulement si $\beta$ vérifie l'équation caractéristique $r^2 + ar + b = 0$ elle-même : en substituant $f_\beta$ et ses dérivées dans l'équation, on peut toujours factoriser par $e^{\beta x}$ (jamais nul), ce qui ramène le problème à résoudre cette équation du second degré en $\beta$. Lorsque son discriminant est nul, une seule valeur de $\beta$ convient, et il faut alors introduire un facteur $x$ supplémentaire pour obtenir une deuxième solution indépendante : $y = (C_1+C_2x)e^{\beta x}$.

### Corrigé
**1.** Soit $\beta \in \mathbb{R}$ et $f_\beta(x) = e^{\beta x}$. Alors $f_\beta'(x) = \beta e^{\beta x}$ et $f_\beta''(x) = \beta^2 e^{\beta x}$.
$f_\beta$ est solution de $(E_6)$ si et seulement si, pour tout $x \in \mathbb{R}$ :
$$\beta^2e^{\beta x} - 2\beta e^{\beta x} + e^{\beta x} = 0 \iff \big(\beta^2 - 2\beta + 1\big)e^{\beta x} = 0.$$
Comme $e^{\beta x} \neq 0$ pour tout $x$, cela équivaut à $\beta^2 - 2\beta + 1 = 0$, soit $(\beta - 1)^2 = 0$, d'où $\beta = 1$ : c'est l'unique valeur possible.

**2.** L'équation caractéristique associée à $(E_6)$ est précisément $r^2 - 2r + 1 = 0$, l'équation trouvée pour $\beta$ ci-dessus : elle admet donc l'unique racine double $r_0 = 1$, ce que confirme le calcul direct $\Delta = (-2)^2 - 4\times 1\times 1 = 4-4=0$. Le discriminant étant nul, la solution générale de $(E_6)$ sur $\mathbb{R}$ est bien
$$y(x) = (C_1 + C_2x)e^{x}, \quad (C_1, C_2) \in \mathbb{R}^2.$$

**3.** On a $g(x) = (C_1+C_2x)e^{x}$, donc $g'(x) = C_2e^{x} + (C_1+C_2x)e^{x} = \big(C_1+C_2+C_2x\big)e^{x}$.
Les conditions initiales donnent :
$$g(0) = C_1 = -1, \qquad g'(0) = C_1 + C_2 = 4.$$
De la seconde égalité : $-1 + C_2 = 4$, soit $C_2 = 5$.

La solution cherchée est donc :
$$g(x) = (-1 + 5x)e^{x}.$$

### Pourquoi les autres réponses sont fausses

- **b)** on a pris $g'(0)=C_2$ en oubliant que la dérivée de $(C_1+C_2x)e^x$ fait aussi apparaître $C_1$ : $g'(0)=C_1+C_2$.
- **c)** erreur de signe dans la dérivée du produit : on a écrit $g'(0)=C_2-C_1$ au lieu de $C_1+C_2$.
- **d)** on a pris la racine double $r_0=-1$ au lieu de $r_0=1$ ; cette fonction n'est pas solution de $(E_6)$.

</details>

Avis : 

---

## 36. `cqc-racine-double-moyenne-0` (séries C/D/E/TI)

**Remarque du relecteur :** LIMITE : équation différentielle du second ordre, à confirmer au programme de la série TI.

**Énoncé :**

On considère l'équation différentielle $(E_3) : y'' + 2y' + y = 0$, où $y$ est une fonction deux fois dérivable sur $\mathbb{R}$.

Quelle est la solution de $(E_3)$ dont la courbe représentative admet une tangente horizontale au point d'abscisse $0$ et qui prend la valeur $2$ en ce point ?

- a) $y(x)=2e^{-x}$
- b) $y(x)=(2-2x)e^{-x}$
- c) $y(x)=(2+2x)e^{-x}$
- d) $y(x)=(2+2x)e^{x}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour résoudre une équation $y'' + ay' + by = 0$, il faut toujours calculer soi-même le discriminant $\Delta$ de l'équation caractéristique $r^2+ar+b=0$ avant de conclure sur la forme de la solution générale - rien n'autorise à supposer sa nature sans ce calcul. Une tangente horizontale au point d'abscisse $x_0$ se traduit par la condition $y'(x_0) = 0$, qui s'ajoute à une éventuelle condition sur $y(x_0)$ pour déterminer entièrement les constantes.

### Corrigé
**1.** L'équation caractéristique associée à $(E_3)$ est $r^2 + 2r + 1 = 0$.
$\Delta = 2^2 - 4\times 1\times 1 = 4 - 4 = 0$.
Le discriminant est nul : $(E_3)$ admet donc une racine double $r_0 = -\dfrac{2}{2} = -1$.

**2.** Le discriminant étant nul, la solution générale de $(E_3)$ sur $\mathbb{R}$ est
$$y(x) = (C_1 + C_2x)e^{-x}, \quad (C_1, C_2) \in \mathbb{R}^2.$$

**3.** On dérive : $y'(x) = C_2e^{-x} - (C_1+C_2x)e^{-x} = \big(C_2 - C_1 - C_2x\big)e^{-x}$.
La condition « $y$ prend la valeur $2$ en $0$ » donne $y(0) = C_1 = 2$.
La condition « tangente horizontale en $0$ » donne $y'(0) = C_2 - C_1 = 0$, soit $C_2 = C_1 = 2$.

La solution cherchée est donc :
$$y(x) = (2 + 2x)e^{-x} = 2(1+x)e^{-x}.$$

### Pourquoi les autres réponses sont fausses

- **a)** on a traduit la tangente horizontale par $C_2=0$ en oubliant le terme $-C_1$ dans $y'(0)=C_2-C_1$ ; ici $y'(0)=-2\neq0$.
- **b)** erreur de signe dans la dérivée du produit : on a écrit $y'(0)=C_2+C_1$, d'où $C_2=-2$.
- **d)** on a pris la racine $r_0=1$ au lieu de $r_0=-1$ ; cette fonction n'est pas solution de $(E_3)$.

</details>

Avis : 

---

## 37. `cqc-repetition-d-epreuves-independantes-moyenne-2` (séries A/D)

**Remarque du relecteur :** VOCABULAIRE : le choix a) 0,3 n'est pas arrondi à 10^-3 comme demandé ; préférer « 0,300 ».

**Modification de fond lors de la conversion** (question réduite ou méthode remplacée) : à examiner de près.

**Énoncé :**

Un opérateur de messagerie annonce un taux de réussite de livraison de 98 % pour chaque SMS envoyé : à chaque envoi, indépendamment des autres, la probabilité qu'un SMS échoue à être livré est donc de 2 %. Un utilisateur envoie 15 SMS dans la journée, dans des conditions identiques et indépendantes les unes des autres.

Quelle est la probabilité qu'au moins un des 15 SMS envoyés échoue à être livré ? On arrondira à $10^{-3}$ près.

- a) $0{,}300$
- b) $0{,}261$
- c) $0{,}739$
- d) $0{,}226$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'une épreuve à deux issues, de probabilité $p$ pour l'événement considéré, est répétée $n$ fois de façon identique et indépendante, l'événement contraire de « l'événement se produit au moins une fois » est « l'événement ne se produit jamais », de probabilité $(1-p)^n$. On en déduit $P(\text{au moins une fois})=1-(1-p)^n$.

### Corrigé

Le taux de réussite annoncé de 98 % signifie qu'à chaque envoi, la probabilité qu'un SMS échoue à être livré est $p=0{,}02$, et la probabilité qu'il soit livré avec succès est $1-p=0{,}98$. Les 15 envois sont effectués dans des conditions identiques et indépendantes les unes des autres (donné par l'énoncé).

L'événement contraire de « au moins un échec parmi les 15 SMS » est « aucun échec », c'est-à-dire que les 15 SMS sont tous livrés avec succès :
$$P(\text{jamais})=(1-p)^{15}=0{,}98^{15}\approx0{,}738569$$

On en déduit :
$$P(\text{au moins un échec de livraison})=1-0{,}738569=0{,}261431\approx0{,}261$$

Arrondie à $10^{-3}$ près, l'utilisateur a donc une probabilité de $0{,}261$, soit environ 26,1 %, qu'au moins un de ses 15 SMS échoue à être livré.

### Pourquoi les autres réponses sont fausses

- **a)** on a calculé $15\times0{,}02$, comme si les échecs des différents SMS étaient incompatibles.
- **c)** c'est la probabilité que les 15 SMS soient tous livrés : on a oublié de passer à l'événement contraire.
- **d)** c'est la probabilité qu'exactement un SMS échoue ; « au moins un » inclut aussi plusieurs échecs.

</details>

Avis : 

---

## 38. `cqc-solution-particuliere-moyenne-2` (séries C/D/E/TI)

**Énoncé :**

Soit $(E)$ l'équation différentielle du second ordre définie sur $\mathbb{R}$ par
$$y'' - y' - 2y = 6e^{x} - 8.$$
On admet que $(E)$ possède une solution particulière de la forme $h(x) = p\,e^{x} + q$, où $p$ et $q$ sont deux réels.

Quelle est cette solution particulière $h$ ?

- a) $h(x)=3e^{x}-4$
- b) $h(x)=-3e^{x}-4$
- c) $h(x)=-3e^{x}+4$
- d) $h(x)=-2e^{x}+4$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une équation différentielle du second ordre dont le second membre combine une exponentielle $e^{\lambda x}$ et une constante, on cherche encore une solution particulière $h(x) = p\,e^{\lambda x} + q$, à condition que $\lambda$ ne soit pas racine de l'équation caractéristique associée. On calcule $h'$ et $h''$, on substitue les trois termes dans l'équation, puis on identifie le coefficient de l'exponentielle et le terme constant.

### Corrigé

Avec $h(x) = p\,e^{x} + q$, on a $h'(x) = p\,e^{x}$ et $h''(x) = p\,e^{x}$.

En remplaçant dans $(E)$ :
$$h''(x) - h'(x) - 2h(x) = p\,e^{x} - p\,e^{x} - 2\big(p\,e^{x}+q\big) = -2p\,e^{x} - 2q.$$

Par identification avec $6e^{x} - 8$ :
$$-2p = 6 \quad\Rightarrow\quad p = -3, \qquad\qquad -2q = -8 \quad\Rightarrow\quad q = 4.$$

La solution particulière est donc :
$$h(x) = -3e^{x} + 4.$$

Vérification : $h'(x)=h''(x)=-3e^x$, donc $h''(x)-h'(x)-2h(x) = -3e^x-(-3e^x)-2(-3e^x+4) = -3e^x+3e^x+6e^x-8 = 6e^x-8$, ce qui correspond bien au second membre de $(E)$.

### Pourquoi les autres réponses sont fausses

- **a)** Les deux équations $-2p=6$ et $-2q=-8$ ont été résolues en oubliant le signe du coefficient $-2$.
- **b)** Erreur de signe sur le terme constant : $-2q=-8$ donne $q=4$, et non $q=-4$.
- **d)** Le terme $h''(x)=p\,e^{x}$ a été oublié : on a écrit $-p\,e^{x}-2p\,e^{x}=-3p\,e^{x}$, d'où $p=-2$.

</details>

Avis : 

---

## 39. `cqc-equation-logarithmique-elevee-0` (séries A)

**Remarque du relecteur :** LIMITE : équation du 3e degré à factoriser (racine évidente) pour la série A ; une indication (vérifier que 1 est solution) serait bienvenue.

**Énoncé :**

Résoudre dans $\left]0\,;\,+\infty\right[$ l'équation :
$$(\ln x)^3 + 2(\ln x)^2 = 13\ln x - 10$$

Quel est l'ensemble des solutions de cette équation ?

- a) $\left\{e^{-5}\,;\,e\,;\,e^{2}\right\}$
- b) $\left\{e^{5}\,;\,e\,;\,e^{-2}\right\}$
- c) $\left\{e\,;\,e^{2}\right\}$
- d) $\left\{-5\,;\,1\,;\,2\right\}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'une équation ne fait intervenir $x$ qu'à travers $\ln x$, on pose $t=\ln x$ après avoir, si nécessaire, ramené tous les termes du même côté pour obtenir un polynôme égal à zéro. Face à un polynôme de degré 3, on vérifie qu'une valeur candidate en est racine, on divise alors par le facteur linéaire correspondant pour obtenir un facteur du second degré, résolu par discriminant. Chaque racine $t$ redonne une solution $x=e^{t}$, automatiquement strictement positive.

### Corrigé

On pose $t = \ln x$ (avec $x>0$). En regroupant tous les termes à gauche, l'équation $t^3+2t^2 = 13t-10$ devient :
$$t^3 + 2t^2 - 13t + 10 = 0$$

**Racine évidente** : pour $t=1$, on a $1+2-13+10 = 0$. Donc $t=1$ est bien racine, et $(t-1)$ divise le polynôme.

**Division** : on obtient, par identification des coefficients :
$$t^3+2t^2-13t+10 = (t-1)(t^2+3t-10)$$

**Résolution du facteur du second degré** : $\Delta = 3^2-4\times1\times(-10) = 9+40=49=7^2$, d'où :
$$t = \dfrac{-3-7}{2} = -5 \qquad \text{ou} \qquad t = \dfrac{-3+7}{2} = 2$$

Les trois racines sont $t \in \{-5\,;\,1\,;\,2\}$.

**Vérification** : $-125+50+65+10=0$ pour $t=-5$ ; $8+8-26+10=0$ pour $t=2$.

On revient à $x$ par $x=e^{t}$ :
$$x=e^{-5}, \qquad x=e^{1}=e, \qquad x=e^{2}$$

L'équation admet donc trois solutions : $x \in \left\{e^{-5}\,;\,e\,;\,e^{2}\right\}$.

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de signe dans les racines du trinôme $t^2+3t-10$ : on a calculé $\dfrac{3\pm7}{2}$ au lieu de $\dfrac{-3\pm7}{2}$.
- **c)** La racine $t=-5$ a été rejetée à tort : $\ln x$ peut être négatif, et $x=e^{-5}$ est bien strictement positif.
- **d)** Ce sont les valeurs de $t=\ln x$ : on a oublié de revenir à $x=e^{t}$ (et $-5$ n'est même pas dans l'intervalle).

</details>

Avis : 

---

## 40. `cqc-equation-logarithmique-moyenne-0` (séries A)

**Remarque du relecteur :** Contrairement à l'item 1, la factorisation n'est pas donnée : l'élève de série A doit trouver la racine évidente t=1, faisable mais à signaler.

**Énoncé :**

Résoudre dans $\left]0\,;\,+\infty\right[$ l'équation :
$$(\ln x)^3 - 3(\ln x)^2 - 13\ln x + 15 = 0$$

Quel est l'ensemble des solutions de cette équation ?

- a) $\left\{e\,;\,e^{5}\right\}$
- b) $\left\{e^{3}\,;\,e\,;\,e^{-5}\right\}$
- c) $\left\{e^{-3}\,;\,e\,;\,e^{5}\right\}$
- d) $\left\{e^{-3}\,;\,e^{5}\right\}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une équation ne faisant intervenir $x$ qu'à travers $\ln x$, on pose $t=\ln x$ pour obtenir un polynôme en $t$. Si ce polynôme est de degré 3, on cherche d'abord une racine évidente en testant une valeur candidate, puis on effectue la division du polynôme cubique par le facteur linéaire correspondant afin d'obtenir un facteur du second degré, que l'on résout ensuite par discriminant. Toutes les racines en $t$ redonnent des solutions $x=e^{t}$ valables, car $\ln x$ parcourt tout $\mathbb{R}$.

### Corrigé

On pose $t = \ln x$ (avec $x>0$). L'équation devient :
$$t^3 - 3t^2 - 13t + 15 = 0$$

**Racine évidente** : pour $t=1$, on a $1^3 - 3\times1^2 - 13\times1 + 15 = 1-3-13+15 = 0$. Donc $t=1$ est bien racine, et $(t-1)$ divise le polynôme.

**Division** : en effectuant la division de $t^3-3t^2-13t+15$ par $(t-1)$ (par identification des coefficients), on obtient :
$$t^3-3t^2-13t+15 = (t-1)(t^2-2t-15)$$

**Résolution du facteur du second degré** : $\Delta = (-2)^2-4\times1\times(-15) = 4+60=64=8^2$, d'où :
$$t = \dfrac{2-8}{2} = -3 \qquad \text{ou} \qquad t = \dfrac{2+8}{2} = 5$$

Les trois racines sont $t \in \{-3\,;\,1\,;\,5\}$.

**Vérification** : $(-3)^3-3(-3)^2-13(-3)+15 = -27-27+39+15=0$ ; $1-3-13+15=0$ ; $125-75-65+15=0$.

On revient à $x$ par $x=e^{t}$ :
$$x=e^{-3}, \qquad x=e^{1}=e, \qquad x=e^{5}$$

L'équation admet donc trois solutions : $x \in \left\{e^{-3}\,;\,e\,;\,e^{5}\right\}$.

### Pourquoi les autres réponses sont fausses

- **a)** La racine $t=-3$ a été rejetée à tort : $\ln x$ peut être négatif, et $e^{-3}>0$ convient.
- **b)** Erreur de signe dans les racines de $t^2-2t-15$ : on a calculé $\dfrac{-2\pm8}{2}$ au lieu de $\dfrac{2\pm8}{2}$.
- **d)** Seul le facteur du second degré a été résolu : la racine évidente $t=1$, donc $x=e$, a été perdue.

</details>

Avis : 

---

## 41. `cqc-evenement-contraire-faible-0` (séries A/D/TI)

**Énoncé :**

Un atelier de maintenance dispose d'un lot de 12 pièces mécaniques fraîchement usinées, parmi lesquelles 4 présentent un défaut de calibrage. Un technicien prélève simultanément et au hasard 2 pièces de ce lot pour un contrôle. Quelle est la probabilité qu'au moins une des deux pièces prélevées soit défectueuse ? (On donnera la valeur exacte.)

- a) $\dfrac{14}{33}$
- b) $\dfrac{16}{33}$
- c) $\dfrac59$
- d) $\dfrac{19}{33}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand un événement est formulé « au moins un... », le dénombrer directement oblige à distinguer plusieurs situations qui se chevauchent (une seule pièce défectueuse OU les deux le sont), ce qui multiplie les calculs. Il est presque toujours plus simple de passer par l'événement contraire, ici « aucune pièce défectueuse », qui correspond à une seule situation nette et se dénombre en un seul calcul ; on obtient ensuite la probabilité cherchée par $P = 1 - P(\text{contraire})$.

### Corrigé

Le lot compte 12 pièces, dont 4 défectueuses et $12-4=8$ conformes. Le nombre total de prélèvements possibles de 2 pièces parmi les 12 est
$$\binom{12}{2} = \dfrac{12\times11}{2} = 66.$$

L'événement contraire de « au moins une pièce défectueuse » est « aucune pièce défectueuse », c'est-à-dire que les 2 pièces prélevées proviennent uniquement des 8 pièces conformes :
$$\binom{8}{2} = \dfrac{8\times7}{2} = 28.$$

$$P(\text{aucune défectueuse}) = \dfrac{28}{66} = \dfrac{14}{33}$$

$$P(\text{au moins une défectueuse}) = 1 - \dfrac{14}{33} = \dfrac{19}{33}$$

### Pourquoi les autres réponses sont fausses

- **a)** C'est la probabilité qu'aucune pièce ne soit défectueuse : on a oublié de calculer $1-P$.
- **b)** C'est la probabilité d'avoir exactement une pièce défectueuse ($\dfrac{4\times8}{66}$) : le cas des deux pièces défectueuses est oublié.
- **c)** On a raisonné comme pour deux tirages successifs avec remise, $1-\left(\dfrac{8}{12}\right)^2$, alors que le prélèvement est simultané.

</details>

Avis : 

---

## 42. `cqc-condition-initiale-elevee-5` (séries A/C/D/E/TI)

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x) = 4x - 3 + 6e^{2x}$.

Déterminer la primitive $F$ de $f$ sur $\mathbb{R}$ telle que $F(2) = 3e^4 + 10$.

- a) $F(x)=2x^2-3x+3e^{2x}+12$
- b) $F(x)=4x^2-3x+3e^{2x}$
- c) $F(x)=2x^2-3x+3e^{2x}+8$
- d) $F(x)=2x^2-3x+6e^{2x}+8-3e^4$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Lorsqu'une primitive combine un terme polynomial et un terme exponentiel, on primitive chaque terme indépendamment par la formule qui lui correspond ($x^n \to \dfrac{x^{n+1}}{n+1}$ pour le polynôme, $e^{ax} \to \dfrac1a e^{ax}$ pour l'exponentielle), avant de rassembler le tout sous une seule constante $k$. On détermine ensuite $k$ grâce à la condition $F(x_0)=y_0$, quitte à laisser une valeur exponentielle non simplifiée (comme $e^4$) dans le résultat final.

### Corrigé
**Primitive générale.** On primitive $f$ terme à terme sur $\mathbb{R}$.

Une primitive de $4x$ est $2x^2$.

Une primitive de $-3$ (constante) est $-3x$.

Une primitive de $6e^{2x}$ est $6 \times \dfrac12 e^{2x} = 3e^{2x}$.

La primitive générale de $f$ sur $\mathbb{R}$ est donc :
$$F(x) = 2x^2 - 3x + 3e^{2x} + k, \quad k \in \mathbb{R}$$

**Détermination de $k$.** On calcule :
$$F(2) = 2(2)^2 - 3(2) + 3e^{2(2)} + k = 8 - 6 + 3e^4 + k = 2 + 3e^4 + k$$
Comme $F(2) = 3e^4 + 10$ :
$$2 + 3e^4 + k = 3e^4 + 10 \iff k = 8$$

**Conclusion.** La primitive cherchée est :
$$F(x) = 2x^2 - 3x + 3e^{2x} + 8$$

**Vérification** : $F'(x) = 4x - 3 + 6e^{2x} = f(x)$, et $F(2) = 8-6+3e^4+8 = 3e^4+10$. Conforme.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur dans la résolution de $2+3e^4+k=3e^4+10$ : on a ajouté $2$ au lieu de le soustraire.
- **b)** Une primitive de $4x$ est $2x^2$, pas $4x^2$ ; l'erreur fausse ensuite la valeur de $k$.
- **d)** Le facteur $\dfrac12$ a été oublié : une primitive de $6e^{2x}$ est $3e^{2x}$, pas $6e^{2x}$.

</details>

Avis : 

---

## 43. `cqc-division-euclidienne-polynomiale-elevee-0` (séries A)

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}\setminus\{3\}$ par $$f(x) = \dfrac{x^3-4x^2+x+9}{x-3}.$$

On écrit $f(x)$ sous la forme $Q(x)+\dfrac{r}{x-3}$, où $Q$ est un polynôme du second degré et $r$ un réel. Quelle est cette écriture ?

- a) $f(x)=x^2-x-2-\dfrac{3}{x-3}$
- b) $f(x)=x^2-x-2+\dfrac{3}{x-3}$
- c) $f(x)=x^2-x-2+\dfrac{15}{x-3}$
- d) $f(x)=x^2-7x+22-\dfrac{57}{x-3}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
La division euclidienne d'un polynôme de degré $3$ par un polynôme de degré $1$ se mène terme par terme, comme pour un diviseur de degré $1$ classique, mais le quotient obtenu est alors de degré $2$. À chaque étape, on divise le terme dominant du reste partiel par le terme dominant du diviseur, on multiplie tout le diviseur par ce terme, puis on soustrait ; on répète l'opération jusqu'à obtenir un reste de degré strictement inférieur à celui du diviseur.

### Corrigé
**1)** On effectue la division euclidienne de $x^3-4x^2+x+9$ par $x-3$.

**Étape 1.** $\dfrac{x^3}{x}=x^2$. On multiplie : $(x-3)\times x^2 = x^3-3x^2$. On soustrait :
$$(x^3-4x^2+x+9)-(x^3-3x^2) = -x^2+x+9.$$

**Étape 2.** $\dfrac{-x^2}{x}=-x$. On multiplie : $(x-3)\times(-x) = -x^2+3x$. On soustrait :
$$(-x^2+x+9)-(-x^2+3x) = -2x+9.$$

**Étape 3.** $\dfrac{-2x}{x}=-2$. On multiplie : $(x-3)\times(-2) = -2x+6$. On soustrait :
$$(-2x+9)-(-2x+6) = 3.$$

Le reste obtenu, $3$, est de degré $0$ : strictement inférieur au degré $1$ du diviseur, donc la division s'arrête ici.

Le quotient est $Q(x)=x^2-x-2$ et le reste est $r=3$.

**2)** Vérification :
$$(x-3)(x^2-x-2) = x^3-x^2-2x-3x^2+3x+6 = x^3-4x^2+x+6.$$
En ajoutant le reste : $x^3-4x^2+x+6+3 = x^3-4x^2+x+9$, ce qui correspond exactement au polynôme de départ. L'égalité $$x^3-4x^2+x+9=(x-3)(x^2-x-2)+3$$ est donc confirmée.

**3)** En divisant les deux membres par $(x-3)$, on obtient, pour tout $x\neq 3$ :
$$f(x) = x^2-x-2+\dfrac{3}{x-3}.$$

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe dans la dernière soustraction : $(-2x+9)-(-2x+6)=3$, et non $-3$.
- **c)** Erreur dans le produit $(x-3)\times(-2)$, qui vaut $-2x+6$ et non $-2x-6$.
- **d)** La division a été menée comme une division par $x+3$ (on a utilisé $-3$ au lieu de $3$).

</details>

Avis : 

---

## 44. `cqc-methode-de-mayer-elevee-0` (séries A)

**Énoncé :**

Une ONG suit chaque mois le nombre de nouvelles inscriptions (en dizaines) à son programme d'alphabétisation pour adultes, durant les 7 premiers mois de la campagne :

| Mois ($x$) | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| Inscriptions en dizaines ($y$) | 8 | 10 | 12 | 10 | 20 | 24 | 28 |

On partage la série, déjà classée par mois croissants, de sorte que le premier sous-groupe reçoive les 4 valeurs d'abscisses les plus petites et le second les 3 valeurs restantes. Quelle est une équation de la droite de Mayer $(G_1G_2)$ ?

- a) $y=3x+4$
- b) $y=3{,}5x+3$
- c) $y=4x+10$
- d) $y=4x$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand l'effectif d'une série est impair, on ne peut pas former deux sous-groupes strictement égaux : l'énoncé précise alors lequel des deux reçoit une valeur de plus, et cette convention doit être respectée sans ambiguïté. Le calcul des points moyens et du coefficient directeur suit ensuite exactement la même démarche que pour un effectif pair, y compris lorsque les moyennes obtenues ne sont pas des nombres entiers.

### Corrigé
1. La série, déjà classée par mois croissants, est : (1;8), (2;10), (3;12), (4;10), (5;20), (6;24), (7;28).
   - Groupe 1 (mois 1 à 4, 4 valeurs) : $\bar x_1=\dfrac{1+2+3+4}{4}=\dfrac{10}{4}=2{,}5$, $\bar y_1=\dfrac{8+10+12+10}{4}=\dfrac{40}{4}=10$, donc $G_1(2{,}5;10)$.
   - Groupe 2 (mois 5 à 7, 3 valeurs) : $\bar x_2=\dfrac{5+6+7}{3}=6$, $\bar y_2=\dfrac{20+24+28}{3}=\dfrac{72}{3}=24$, donc $G_2(6;24)$.
2. Coefficient directeur : $a=\dfrac{24-10}{6-2{,}5}=\dfrac{14}{3{,}5}=4$.
   Équation de $(G_1G_2)$ : avec $G_2(6;24)$, $24=4\times6+b \Rightarrow b=24-24=0$.
   D'où $y=4x$.
   Vérification avec $G_1$ : $4\times2{,}5=10$, conforme.

### Pourquoi les autres réponses sont fausses

- **a)** Le partage a été inversé (3 valeurs dans le premier groupe, 4 dans le second), contrairement à la convention de l'énoncé.
- **b)** On a pris $\bar x_1=2$ (la valeur du milieu de $1;2;3$) au lieu de $\bar x_1=\dfrac{1+2+3+4}{4}=2{,}5$, ce qui fausse $\Delta x$.
- **c)** On a pris pour ordonnée à l'origine l'ordonnée $\bar y_1=10$ de $G_1$, au lieu de résoudre $10=4\times2{,}5+b$.

</details>

Avis : 

---

## 45. `cqc-methode-de-mayer-moyenne-1` (séries A)

**Remarque du relecteur :** VOCABULAIRE : « nombre cumulé de nouveaux abonnés » est lourd ; dire « nombre total d'abonnés ». Piège des dizaines (choix a = 195) bien construit.

**Modification de fond lors de la conversion** (question réduite ou méthode remplacée) : à examiner de près.

**Énoncé :**

Une chaîne culturelle sur une plateforme de vidéos en ligne suit le nombre total d'abonnés, mois après mois, depuis sa création. Après avoir classé les relevés par mois croissants et calculé les points moyens des deux sous-groupes selon la méthode de Mayer, on obtient $G_1(3;40)$ pour le premier sous-groupe et $G_2(9;70)$ pour le second, où $x$ désigne le rang du mois depuis la création de la chaîne et $y$ le nombre d'abonnés, en dizaines.

Si la tendance donnée par la droite de Mayer $(G_1G_2)$ se poursuit, à quel rang de mois la chaîne atteindra-t-elle 1000 abonnés ?

- a) Au 195ᵉ mois
- b) Au 12ᵉ mois
- c) Au 15ᵉ mois
- d) Au 20ᵉ mois

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Lorsque les points moyens $G_1$ et $G_2$ d'une méthode de Mayer sont déjà connus, il n'est plus nécessaire de repartir des données brutes : le coefficient directeur s'obtient directement par $a=\dfrac{\bar y_2-\bar y_1}{\bar x_2-\bar x_1}$, puis l'équation $y=ax+b$ se détermine en remplaçant $x$ et $y$ par les coordonnées de l'un des deux points. Cette équation sert ensuite à estimer un rang de mois pour une valeur de $y$ donnée, en résolvant l'équation d'inconnue $x$, sans oublier l'unité dans laquelle $y$ est exprimé.

### Corrigé
Coefficient directeur : $a=\dfrac{70-40}{9-3}=\dfrac{30}{6}=5$.

Avec $G_1(3;40)$ : $40=5\times3+b \Rightarrow b=40-15=25$. D'où $y=5x+25$. Vérification avec $G_2$ : $5\times9+25=45+25=70$, conforme.

1000 abonnés correspondent à $y=100$ (en dizaines). On résout $100=5x+25$, soit $5x=75$, donc $x=15$.

Selon ce modèle, la chaîne atteindra 1000 abonnés au 15ᵉ mois.

### Pourquoi les autres réponses sont fausses

- **a)** On a remplacé $y$ par $1000$ alors que $y$ est exprimé en dizaines : 1000 abonnés correspondent à $y=100$.
- **b)** On a pris pour ordonnée à l'origine $b=40$ (l'ordonnée de $G_1$) au lieu de $b=25$.
- **d)** On a oublié l'ordonnée à l'origine en résolvant $5x=100$ au lieu de $5x+25=100$.

</details>

Avis : 

---

## 46. `cqc-statistique-a-deux-variables-faible-0` (séries A)

**Énoncé :**

Une bibliothèque scolaire a relevé, pour 5 mois consécutifs, le nombre d'ateliers de lecture organisés ($x$) et le nombre de livres empruntés ce mois-là par les élèves, en dizaines ($y$) :

| Mois | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Ateliers de lecture organisés ($x$) | 1 | 2 | 3 | 4 | 5 |
| Livres empruntés, en dizaines ($y$) | 10 | 14 | 15 | 19 | 22 |

On donne les écarts-types de cette série, déjà calculés : $\sigma_x \approx 1{,}414$ et $\sigma_y \approx 4{,}147$. Le coefficient de corrélation linéaire $r$ étant arrondi au centième, quelle affirmation est exacte ?

- a) $r\approx0{,}99$ : la corrélation linéaire est très forte, un ajustement affine est justifié.
- b) $r\approx0{,}17$ : la corrélation linéaire est faible, un ajustement affine n'est pas justifié.
- c) $r\approx0{,}99$ : un ajustement affine n'est pas justifié, car il faudrait $r=1$ exactement.
- d) $r\approx1{,}04$ : la corrélation linéaire est parfaite, un ajustement affine est justifié.

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Le coefficient de corrélation linéaire $r$ mesure la qualité d'un ajustement affine entre deux variables statistiques : il se calcule à partir de la covariance $\text{cov}(x,y) = \dfrac1n\sum(x_i-\bar x)(y_i-\bar y)$ et des écarts-types $\sigma_x$, $\sigma_y$, par la formule $r = \dfrac{\text{cov}(x,y)}{\sigma_x \times \sigma_y}$. On a toujours $-1\leqslant r\leqslant1$ ; plus $|r|$ est proche de 1, plus un ajustement affine est justifié, sans qu'il soit nécessaire que $r$ soit exactement égal à 1.

### Corrigé
$\bar x = \dfrac{15}{5} = 3$ et $\bar y = \dfrac{10+14+15+19+22}{5} = \dfrac{80}{5} = 16$.

| $x_i$ | $x_i-\bar x$ | $y_i$ | $y_i-\bar y$ | $(x_i-\bar x)(y_i-\bar y)$ |
|---|---|---|---|---|
| 1 | -2 | 10 | -6 | 12 |
| 2 | -1 | 14 | -2 | 2 |
| 3 | 0 | 15 | -1 | 0 |
| 4 | 1 | 19 | 3 | 3 |
| 5 | 2 | 22 | 6 | 12 |
| Somme | | | | 29 |

$\text{cov}(x,y) = \dfrac{29}{5} = 5{,}8$, puis
$$r = \dfrac{5{,}8}{1{,}414 \times 4{,}147} \approx \dfrac{5{,}8}{5{,}864} \approx 0{,}99 \quad\text{(arrondi au centième)}$$

Une valeur de $r$ aussi proche de 1 traduit une corrélation linéaire positive très forte : un ajustement affine est pleinement justifié pour cette série.

### Pourquoi les autres réponses sont fausses

- **b)** On a divisé la covariance par le produit des variances ($2\times17{,}2$) au lieu du produit des écarts-types.
- **c)** La valeur de $r$ est juste, mais un ajustement affine est justifié dès que $|r|$ est proche de 1 ; $r=1$ correspondrait à des points parfaitement alignés.
- **d)** On a divisé par la somme $\sigma_x+\sigma_y$ au lieu du produit $\sigma_x\times\sigma_y$ ; un coefficient de corrélation ne dépasse jamais 1.

</details>

Avis : 

---

## 47. `cqc-statistique-a-deux-variables-moyenne-0` (séries A)

**Modification de fond lors de la conversion** (question réduite ou méthode remplacée) : à examiner de près.

**Énoncé :**

Sur une parcelle expérimentale, un agronome a testé cinq doses différentes d'engrais et a mesuré le rendement en cacao séché obtenu :

| Engrais utilisé, en kg ($x$) | 5 | 10 | 15 | 20 | 25 |
|---|---|---|---|---|---|
| Rendement, en sacs de cacao séché ($y$) | 35 | 60 | 50 | 75 | 70 |

Quelle est la valeur du coefficient de corrélation linéaire $r$ de cette série, arrondie au centième ?

- a) $r\approx0{,}70$
- b) $r\approx0{,}88$
- c) $r\approx0{,}41$
- d) $r\approx0{,}84$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Le coefficient de corrélation linéaire $r = \dfrac{\sum(x_i-\bar x)(y_i-\bar y)}{\sqrt{\sum(x_i-\bar x)^2 \times \sum(y_i-\bar y)^2}}$ se calcule à l'aide d'un tableau d'écarts complet ; il faut surveiller le signe de chaque produit d'écarts. Plus $|r|$ est proche de 1, plus les points du nuage sont proches d'être alignés et plus un ajustement affine est pertinent.

### Corrigé
$\bar x = \dfrac{75}{5}=15$ et $\bar y=\dfrac{35+60+50+75+70}{5}=\dfrac{290}{5}=58$.

| $x_i$ | $x_i-\bar x$ | $y_i$ | $y_i-\bar y$ | $(x_i-\bar x)(y_i-\bar y)$ | $(x_i-\bar x)^2$ | $(y_i-\bar y)^2$ |
|---|---|---|---|---|---|---|
| 5 | -10 | 35 | -23 | 230 | 100 | 529 |
| 10 | -5 | 60 | 2 | -10 | 25 | 4 |
| 15 | 0 | 50 | -8 | 0 | 0 | 64 |
| 20 | 5 | 75 | 17 | 85 | 25 | 289 |
| 25 | 10 | 70 | 12 | 120 | 100 | 144 |
| Somme | | | | 425 | 250 | 1030 |

$$r=\dfrac{425}{\sqrt{250\times1030}}=\dfrac{425}{\sqrt{257500}}\approx\dfrac{425}{507{,}44}\approx0{,}84 \quad\text{(arrondi au centième)}$$

Avec $r\approx0{,}84$, la corrélation linéaire entre la dose d'engrais et le rendement est forte et positive, sans être parfaite : un ajustement affine est raisonnablement justifié, d'autres facteurs (pluviométrie, qualité du sol, ensoleillement) intervenant probablement aussi.

### Pourquoi les autres réponses sont fausses

- **a)** C'est $r^2$, et non $r$ : on a oublié de prendre la racine carrée, ou élevé le résultat au carré.
- **b)** Erreur de signe dans le tableau : le produit $(-5)\times2$ vaut $-10$, et non $+10$, ce qui donne une somme de $425$ et non $445$.
- **c)** On a divisé $425$ par $\sum(y_i-\bar y)^2=1030$ seulement, au lieu de $\sqrt{250\times1030}$.

</details>

Avis : 

---

## 48. `cqc-equation-exponentielle-faible-1` (séries A/D)

**Énoncé :**

Résoudre dans $\mathbb{R}$ l'équation d'inconnue $x$ suivante :
$$(5x-15)e^{-2x+4}=0$$

Quel est l'ensemble des solutions ?

- a) $S=\{2\,;\,3\}$
- b) $S=\{2\}$
- c) $S=\{3\}$
- d) $S=\{-3\}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Un produit de facteurs est nul si et seulement si l'un au moins de ses facteurs est nul. Or une exponentielle $e^{u(x)}$ ne s'annule jamais, quelle que soit la valeur réelle de $u(x)$ : dans un produit contenant un facteur exponentiel, seule l'annulation de l'autre facteur peut donc annuler le produit.

### Corrigé

Pour tout réel $x$, $e^{-2x+4}>0$ : ce facteur ne s'annule jamais. Donc :

$$(5x-15)e^{-2x+4}=0 \iff 5x-15=0 \iff x=3$$

**Vérification :** $(5\times3-15)\times e^{-2\times3+4} = 0\times e^{-2} = 0$.

**L'équation admet une unique solution : $S=\{3\}$.**

### Pourquoi les autres réponses sont fausses

- **a)** On a cru que le facteur exponentiel pouvait s'annuler ($-2x+4=0$), alors que $e^{-2x+4}>0$ pour tout réel $x$.
- **b)** On a annulé l'exposant au lieu du facteur $5x-15$ : une exponentielle ne s'annule jamais.
- **d)** Erreur de signe en résolvant $5x-15=0$ : $5x=15$ donne $x=3$.

</details>

Avis : 

---

