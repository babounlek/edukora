# Mini-inédites de maths écrites à la main : à faire relire par l'enseignant

Date : 2026-10-29. Quatre mini-inédites originales (BAC C, BAC D et TI, BAC E, Probatoire D et TI). Chacune compte **2 exercices de 20 minutes, 40 minutes au total, notées sur 10**. Elles sont publiées en local seulement : **aucune n'est en production**. Toutes les valeurs ont été recalculées par script et le barème a été contrôlé (somme des critères = points de la question, somme des questions = points de l'exercice).

Pour chaque mini-inédite, on vous demande de juger : (1) le **niveau** du cursus visé et le **programme** (chaque notion est-elle enseignée dans cette classe ?), (2) la **durée** : 20 minutes par exercice, est-ce réaliste ?, (3) la **grille de notation** (critères observables sur une copie), (4) les **corrigés**.

Pour chaque question : **OK**, **à corriger** (dire quoi) ou **à retirer**.

---

# 1. Mini-inédite Mathématiques BAC C n°1

**Cursus :** BAC C (Terminale C). **Identifiant :** `ep-cm-maths-bac-c-mini-1-2026-s1`.

**Points précis à juger :**

- Racine carrée d'un complexe donnée par la question a) : le discriminant `-8-6i = (1-3i)^2` est fourni, l'élève n'a pas à chercher la racine carrée seul. Est-ce assez simple pour 20 minutes, ou trop guidé pour un BAC C ?
- Quotient `a/b = i` puis carré `OACB` : niveau Terminale C correct ? Les arguments sont-ils attendus sous forme de module et d'argument, ou la simple écriture `a/b = i` suffit-elle ?
- Exercice 2 : croissances comparées, dérivée d'un produit, primitive de la forme `(ax+b)e^{-x}` donnée en indication. Trop guidée ? L'intégration par parties est-elle attendue à la place de l'identification des coefficients ?

**Avis général sur cette mini-inédite :** 

## Exercice 1 (5 points)

Le plan complexe est muni d'un repère orthonormé direct $(O\,;\vec{u},\vec{v})$.

### Question 1.1 (1.5 pts, difficulté moyenne)

**a)** Calculer $(1-3i)^2$.

**b)** Résoudre dans $\mathbb{C}$ l'équation $(E)$ : $z^2-(3+i)z+4+3i=0$.

**Grille de notation :**

- Calcule $(1-3i)^2=-8-6i$ (0.5 pt)
- Calcule le discriminant $\Delta=-8-6i$ et le reconnaît comme $(1-3i)^2$ (0.5 pt)
- Donne les deux solutions $2-i$ et $1+2i$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour résoudre $z^2+pz+q=0$ dans $\mathbb{C}$ avec $p$ et $q$ complexes, on calcule le discriminant $\Delta=p^2-4q$, on cherche un nombre complexe $\delta$ tel que $\delta^2=\Delta$, puis les solutions sont $z=\dfrac{-p\pm\delta}{2}$.

**a)** $(1-3i)^2=1-6i+9i^2=-8-6i$.

**b)** Le discriminant vaut $\Delta=(3+i)^2-4(4+3i)=(9+6i-1)-16-12i=-8-6i$. D'après la question a), $\Delta=(1-3i)^2$ : on prend $\delta=1-3i$. Les solutions sont donc

$$
z_1=\dfrac{3+i+1-3i}{2}=2-i
\qquad\text{et}\qquad
z_2=\dfrac{3+i-1+3i}{2}=1+2i.
$$

L'ensemble des solutions est $\{\,2-i\,;\,1+2i\,\}$.

### Piège à éviter
Chercher la racine carrée de $-8-6i$ à tâtons : la question a) donne directement $\delta$, il suffit de la reconnaître.

</details>

Avis : 

### Question 1.2 (1.5 pts, difficulté moyenne)

On note $A$ et $B$ les points d'affixes respectives $a=1+2i$ et $b=2-i$. Calculer $\dfrac{a}{b}$ sous forme algébrique, puis en déduire la nature du triangle $OAB$.

**Grille de notation :**

- Multiplie le numérateur et le dénominateur par $2+i$ (0.5 pt)
- Obtient $\dfrac{a}{b}=i$ (0.5 pt)
- Conclut : $OA=OB$ (module $1$) et angle droit (argument $\dfrac{\pi}{2}$), donc rectangle isocèle en $O$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
Le quotient $\dfrac{a}{b}$ de deux affixes se calcule en multipliant le numérateur et le dénominateur par le conjugué de $b$ ; son module donne le rapport $\dfrac{OA}{OB}$ et son argument donne l'angle $(\overrightarrow{OB},\overrightarrow{OA})$.

On multiplie par le conjugué de $b$ :

$$
\dfrac{a}{b}=\dfrac{(1+2i)(2+i)}{(2-i)(2+i)}=\dfrac{2+i+4i+2i^2}{5}=\dfrac{5i}{5}=i.
$$

Le module de $i$ est $1$, donc $OA=OB$. Son argument est $\dfrac{\pi}{2}$, donc l'angle $(\overrightarrow{OB},\overrightarrow{OA})$ est droit. Le triangle $OAB$ est rectangle et isocèle en $O$.

### Piège à éviter
Conclure « isocèle » seulement parce que $a$ et $b$ ont la même partie réelle ou la même partie imaginaire en valeur absolue : c'est le module de $\dfrac{a}{b}$, égal à $1$, qui prouve $OA=OB$.

</details>

Avis : 

### Question 1.3 (2 pts, difficulté moyenne)

Soit $C$ le point d'affixe $c=a+b$.

**a)** Donner l'affixe $c$.

**b)** Montrer que le quadrilatère $OACB$ est un carré.

**c)** Calculer son aire.

**Grille de notation :**

- Donne $c=3+i$ (0.5 pt)
- Justifie le parallélogramme par $c=a+b$ (0.5 pt)
- Conclut au carré : côtés consécutifs égaux et perpendiculaires (question 2) (0.5 pt)
- Calcule l'aire $OA^2=5$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
Un quadrilatère $OACB$ est un parallélogramme lorsque $c=a+b$ ; c'est un carré si, de plus, deux côtés consécutifs ont la même longueur et sont perpendiculaires.

**a)** $c=(1+2i)+(2-i)=3+i$.

**b)** Comme $c=a+b$, on a $\overrightarrow{OC}=\overrightarrow{OA}+\overrightarrow{OB}$ : $OACB$ est un parallélogramme. D'après la question 2, $OA=OB$ et $(OA)\perp(OB)$ : deux côtés consécutifs sont égaux et perpendiculaires, donc $OACB$ est un carré.

**c)** L'aire d'un carré est le carré de son côté : $\mathcal{A}=OA^2=|a|^2=1^2+2^2=5$ unités d'aire.

### Piège à éviter
Écrire $OA=\sqrt{5}$ puis oublier d'élever au carré : l'aire est $OA^2=5$, pas $\sqrt{5}$.

</details>

Avis : 

## Exercice 2 (5 points)

On considère la fonction $f$ définie sur $\mathbb{R}$ par $f(x)=(x+2)e^{-x}$. On note $(\mathcal{C})$ sa courbe représentative dans un repère orthonormé.

### Question 2.1 (1.5 pts, difficulté moyenne)

Calculer les limites de $f$ en $+\infty$ et en $-\infty$. Interpréter graphiquement la limite en $+\infty$.

**Grille de notation :**

- Écrit $f(x)=x\,e^{-x}+2\,e^{-x}$ et invoque les croissances comparées (0.5 pt)
- Trouve la limite $0$ en $+\infty$ et l'asymptote $y=0$ (0.5 pt)
- Trouve la limite $-\infty$ en $-\infty$ (produit des limites) (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour lever une forme indéterminée du type $\infty\times 0$ avec l'exponentielle, on utilise les croissances comparées : $\lim_{x\to+\infty}x\,e^{-x}=0$ et $\lim_{x\to+\infty}e^{-x}=0$ ; une limite finie $\ell$ en $\pm\infty$ donne une asymptote horizontale d'équation $y=\ell$.

**En $+\infty$.** On écrit $f(x)=x\,e^{-x}+2\,e^{-x}$. Par croissances comparées, $x\,e^{-x}\to 0$, et $e^{-x}\to 0$. Donc $\displaystyle\lim_{x\to+\infty}f(x)=0$ : la droite d'équation $y=0$ (l'axe des abscisses) est asymptote horizontale à $(\mathcal{C})$ en $+\infty$.

**En $-\infty$.** Quand $x\to-\infty$, $x+2\to-\infty$ et $e^{-x}\to+\infty$. Le produit tend vers $-\infty$ : $\displaystyle\lim_{x\to-\infty}f(x)=-\infty$.

### Piège à éviter
Conclure $\infty\times0=0$ sans justification : $(x+2)e^{-x}$ est bien une forme indéterminée en $+\infty$, que seules les croissances comparées permettent de lever.

</details>

Avis : 

### Question 2.2 (1.5 pts, difficulté moyenne)

Montrer que, pour tout réel $x$, $f'(x)=-(x+1)e^{-x}$, puis dresser le tableau de variations de $f$.

**Grille de notation :**

- Dérive le produit : $e^{-x}-(x+2)e^{-x}$ (0.5 pt)
- Factorise et obtient $f'(x)=-(x+1)e^{-x}$ (0.5 pt)
- Étudie le signe de $f'$ et donne le tableau avec le maximum $f(-1)=e$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
La dérivée d'un produit est $(uv)'=u'v+uv'$ et $(e^{-x})'=-e^{-x}$ ; le signe de $f'$ donne les variations de $f$ : $f$ est croissante là où $f'>0$ et décroissante là où $f'<0$.

On pose $u(x)=x+2$ et $v(x)=e^{-x}$ : $u'(x)=1$ et $v'(x)=-e^{-x}$. Donc

$$
f'(x)=e^{-x}-(x+2)e^{-x}=\bigl(1-x-2\bigr)e^{-x}=-(x+1)e^{-x}.
$$

Comme $e^{-x}>0$, le signe de $f'(x)$ est celui de $-(x+1)$ : $f'(x)>0$ pour $x<-1$ et $f'(x)<0$ pour $x>-1$.

La fonction $f$ est croissante sur $]-\infty\,;-1]$ et décroissante sur $[-1\,;+\infty[$. Elle admet un maximum en $x=-1$ : $f(-1)=(-1+2)e^{1}=e$.

| $x$ | $-\infty$ | | $-1$ | | $+\infty$ |
|---|---|---|---|---|---|
| $f'(x)$ | | $+$ | $0$ | $-$ | |
| $f(x)$ | $-\infty$ | $\nearrow$ | $e$ | $\searrow$ | $0$ |

### Piège à éviter
Oublier le signe moins de $(e^{-x})'=-e^{-x}$ : on obtient alors $f'(x)=(x+3)e^{-x}$, ce qui change tout le tableau.

</details>

Avis : 

### Question 2.3 (2 pts, difficulté elevee)

**a)** Déterminer une primitive $F$ de $f$ sur $\mathbb{R}$, de la forme $F(x)=(ax+b)e^{-x}$ avec $a$ et $b$ réels.

**b)** En déduire la valeur exacte de $\displaystyle\int_0^1 f(x)\,dx$, puis son arrondi à $10^{-2}$.

**Grille de notation :**

- Pose $F(x)=(ax+b)e^{-x}$ et calcule $F'(x)$ (0.5 pt)
- Identifie $a=-1$ et $b=-3$ (0.5 pt)
- Calcule $F(1)-F(0)=3-\dfrac{4}{e}$ (0.5 pt)
- Donne l'arrondi $1{,}53$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour déterminer une primitive de la forme $(ax+b)e^{-x}$, on dérive cette expression puis on identifie les coefficients avec ceux de $f$ ; l'intégrale s'obtient ensuite par $\displaystyle\int_a^b f(x)\,dx=F(b)-F(a)$.

**a)** Si $F(x)=(ax+b)e^{-x}$, alors $F'(x)=a\,e^{-x}-(ax+b)e^{-x}=(-ax+a-b)e^{-x}$. On veut $F'(x)=(x+2)e^{-x}$ : il faut $-a=1$ et $a-b=2$, donc $a=-1$ et $b=-3$. Une primitive de $f$ est $F(x)=-(x+3)e^{-x}$.

**b)** $\displaystyle\int_0^1 f(x)\,dx=F(1)-F(0)=-4e^{-1}+3=3-\dfrac{4}{e}$. Une valeur approchée est $1{,}53$.

### Piège à éviter
Calculer $F(1)-F(0)$ avec $F(0)=-3e^{0}=-3$ : le signe moins devant $F(0)$ transforme $-(-3)$ en $+3$, c'est la source de la plupart des erreurs de signe.

</details>

Avis : 

---

# 2. Mini-inédite Mathématiques BAC D et TI n°1

**Cursus :** BAC D et TI (Terminale D et TI). **Identifiant :** `ep-cm-maths-bac-d-ti-mini-1-2026-s1`.

**Points précis à juger :**

- Loi binomiale `B(10 ; 0,08)` : au programme de Terminale D **et** de Terminale TI ? La question 3b (plus petit `n` tel que `1 - 0,92^n >= 0,9`, par le logarithme) est-elle de leur niveau ?
- Fonction `2x - 3 ln x` : limites, dérivée, minimum positif parce que `3/2 < e`, puis `∫₁ᵉ f = e² - 4` avec la primitive de `ln` donnée. Niveau correct pour D et TI ?
- La limite `ln x / x → 0` est utilisée sans démonstration : est-elle admise à ce niveau ?

**Avis général sur cette mini-inédite :** 

## Exercice 1 (5 points)

Une usine de Bafoussam fabrique des ampoules LED. Une ampoule prélevée au hasard est défectueuse avec la probabilité $0{,}08$. Le stock est assez grand pour que les prélèvements successifs soient assimilés à des tirages indépendants. On prélève $10$ ampoules et on note $X$ le nombre d'ampoules défectueuses parmi elles.

### Question 1.1 (1.5 pts, difficulté faible)

Justifier que $X$ suit une loi binomiale dont on précisera les paramètres, puis calculer $P(X=0)$, arrondie à $10^{-3}$.

**Grille de notation :**

- Identifie $10$ épreuves identiques et indépendantes à deux issues (0.5 pt)
- Donne les paramètres $n=10$ et $p=0{,}08$ (0.5 pt)
- Calcule $P(X=0)=0{,}92^{10}\approx0{,}434$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
Une variable aléatoire $X$ qui compte les succès de $n$ épreuves identiques et indépendantes, chacune de probabilité de succès $p$, suit la loi binomiale $\mathcal{B}(n\,;p)$ : $P(X=k)=\dbinom{n}{k}p^k(1-p)^{n-k}$.

On répète $10$ fois la même épreuve, de façon indépendante : prélever une ampoule. Elle a deux issues, « défectueuse » (succès, de probabilité $p=0{,}08$) ou non. Donc $X$ suit la loi binomiale $\mathcal{B}(10\,;0{,}08)$.

$$
P(X=0)=\dbinom{10}{0}\times0{,}08^0\times0{,}92^{10}=0{,}92^{10}\approx 0{,}434.
$$

### Piège à éviter
Écrire $0{,}08^{10}$ : c'est la probabilité que les $10$ ampoules soient toutes défectueuses, pas qu'aucune ne le soit.

</details>

Avis : 

### Question 1.2 (1.5 pts, difficulté moyenne)

Calculer la probabilité d'obtenir au moins deux ampoules défectueuses, arrondie à $10^{-3}$.

**Grille de notation :**

- Passe par l'événement contraire $1-P(X=0)-P(X=1)$ (0.5 pt)
- Calcule $P(X=1)=10\times0{,}08\times0{,}92^9\approx0{,}378$ (0.5 pt)
- Donne $P(X\geqslant2)\approx0{,}188$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour une probabilité du type « au moins $k$ succès », on passe par l'événement contraire : $P(X\geqslant 2)=1-P(X=0)-P(X=1)$.

On a $P(X=0)=0{,}92^{10}\approx0{,}4344$ et $P(X=1)=\dbinom{10}{1}\times0{,}08\times0{,}92^{9}=10\times0{,}08\times0{,}92^{9}\approx0{,}3777$. Donc

$$
P(X\geqslant 2)=1-0{,}4344-0{,}3777\approx 0{,}188.
$$

### Piège à éviter
Calculer $1-P(X=1)$ : cela donne la probabilité d'avoir zéro ou au moins deux ampoules défectueuses, pas seulement au moins deux.

</details>

Avis : 

### Question 1.3 (2 pts, difficulté elevee)

**a)** Calculer l'espérance de $X$.

**b)** On prélève maintenant $n$ ampoules. Quel est le plus petit entier $n$ pour que la probabilité d'obtenir au moins une ampoule défectueuse soit supérieure ou égale à $0{,}9$ ?

**Grille de notation :**

- Calcule $E(X)=np=0{,}8$ (0.5 pt)
- Traduit la condition par $0{,}92^n\leqslant0{,}1$ (0.5 pt)
- Passe au logarithme et change le sens de l'inégalité : $n\geqslant\dfrac{\ln0{,}1}{\ln0{,}92}$ (0.5 pt)
- Conclut $n=28$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
L'espérance d'une loi binomiale $\mathcal{B}(n\,;p)$ vaut $np$ ; pour résoudre $a^n\leqslant c$ avec $0<a<1$, on prend le logarithme népérien des deux membres et on divise par $\ln a$, qui est négatif, ce qui change le sens de l'inégalité.

**a)** $E(X)=np=10\times0{,}08=0{,}8$ : en moyenne, $0{,}8$ ampoule défectueuse par prélèvement de $10$.

**b)** La probabilité d'avoir au moins une défectueuse est $1-0{,}92^n$. On veut $1-0{,}92^n\geqslant0{,}9$, soit $0{,}92^n\leqslant0{,}1$. On prend le logarithme népérien : $n\ln0{,}92\leqslant\ln0{,}1$. Comme $\ln0{,}92<0$, on divise en changeant le sens :

$$
n\geqslant\dfrac{\ln0{,}1}{\ln0{,}92}\approx 27{,}6.
$$

Le plus petit entier convenable est $n=28$.

### Piège à éviter
Oublier de changer le sens de l'inégalité en divisant par $\ln0{,}92$, qui est négatif : on trouverait $n\leqslant 27{,}6$.

</details>

Avis : 

## Exercice 2 (5 points)

On considère la fonction $f$ définie sur $]0\,;+\infty[$ par $f(x)=2x-3\ln x$. On rappelle qu'une primitive de la fonction $\ln$ sur $]0\,;+\infty[$ est $x\mapsto x\ln x-x$.

### Question 2.1 (1.5 pts, difficulté moyenne)

Calculer les limites de $f$ en $0$ et en $+\infty$.

**Grille de notation :**

- Limite $+\infty$ en $0^+$ justifiée par $\ln x\to-\infty$ (0.5 pt)
- Met $x$ en facteur : $x\left(2-3\dfrac{\ln x}{x}\right)$ (0.5 pt)
- Conclut $+\infty$ en $+\infty$ avec $\dfrac{\ln x}{x}\to0$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour une limite avec $\ln x$ en $+\infty$, on met $x$ en facteur et on utilise $\displaystyle\lim_{x\to+\infty}\dfrac{\ln x}{x}=0$ ; en $0^+$, on utilise $\displaystyle\lim_{x\to0^+}\ln x=-\infty$.

**En $0^+$.** $2x\to0$ et $-3\ln x\to+\infty$, donc $\displaystyle\lim_{x\to0^+}f(x)=+\infty$.

**En $+\infty$.** On factorise : $f(x)=x\left(2-3\,\dfrac{\ln x}{x}\right)$. Comme $\dfrac{\ln x}{x}\to0$, la parenthèse tend vers $2$, et $x\to+\infty$. Donc $\displaystyle\lim_{x\to+\infty}f(x)=+\infty$.

### Piège à éviter
Écrire « $2x\to+\infty$ et $-3\ln x\to-\infty$, donc $f$ a une forme indéterminée sans conclure » : en $+\infty$, il faut mettre $x$ en facteur pour lever l'indétermination.

</details>

Avis : 

### Question 2.2 (1.5 pts, difficulté moyenne)

Calculer $f'(x)$ pour tout $x>0$, puis dresser le tableau de variations de $f$.

**Grille de notation :**

- Dérive : $f'(x)=2-\dfrac{3}{x}$ (0.5 pt)
- Étudie le signe de $\dfrac{2x-3}{x}$ sur $]0\,;+\infty[$ (0.5 pt)
- Donne le tableau et le minimum $3-3\ln\dfrac{3}{2}$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
On dérive terme à terme avec $(\ln x)'=\dfrac{1}{x}$ ; le signe de $f'$ donne les variations de $f$, et la valeur de $f$ au point où $f'$ s'annule donne un extremum.

Pour tout $x>0$, $f'(x)=2-\dfrac{3}{x}=\dfrac{2x-3}{x}$.

Comme $x>0$, le signe de $f'(x)$ est celui de $2x-3$ : $f'(x)<0$ pour $x<\dfrac{3}{2}$ et $f'(x)>0$ pour $x>\dfrac{3}{2}$. La fonction $f$ est décroissante sur $\left]0\,;\dfrac{3}{2}\right]$, croissante sur $\left[\dfrac{3}{2}\,;+\infty\right[$, et son minimum est $f\!\left(\dfrac{3}{2}\right)=3-3\ln\dfrac{3}{2}$.

| $x$ | $0$ | | $\dfrac{3}{2}$ | | $+\infty$ |
|---|---|---|---|---|---|
| $f'(x)$ | | $-$ | $0$ | $+$ | |
| $f(x)$ | $+\infty$ | $\searrow$ | $3-3\ln\dfrac{3}{2}$ | $\nearrow$ | $+\infty$ |

### Piège à éviter
Dériver $\ln x$ en $\ln x$ ou en $x$ : $(\ln x)'=\dfrac{1}{x}$, et le coefficient $3$ reste devant.

</details>

Avis : 

### Question 2.3 (2 pts, difficulté elevee)

**a)** Montrer que $f(x)>0$ pour tout $x>0$.

**b)** Calculer $\displaystyle\int_1^e f(x)\,dx$. Donner la valeur exacte puis l'arrondi à $10^{-2}$.

**Grille de notation :**

- Justifie $\ln\dfrac{3}{2}<1$ car $\dfrac{3}{2}<e$ (0.5 pt)
- Conclut $f>0$ sur $]0\,;+\infty[$ grâce au minimum positif (0.5 pt)
- Donne une primitive $x^2-3(x\ln x-x)$ (0.5 pt)
- Calcule $e^2-4\approx3{,}39$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour montrer qu'une fonction est positive, on compare son minimum à $0$ ; l'intégrale se calcule par $\displaystyle\int_a^b f(x)\,dx=F(b)-F(a)$ avec une primitive $F$ de $f$.

**a)** Le minimum de $f$ est $f\!\left(\dfrac{3}{2}\right)=3\left(1-\ln\dfrac{3}{2}\right)$. Comme $\dfrac{3}{2}<e$, on a $\ln\dfrac{3}{2}<1$, donc ce minimum est strictement positif. Ainsi $f(x)>0$ pour tout $x>0$.

**b)** Une primitive de $f$ est $F(x)=x^2-3\,(x\ln x-x)=x^2-3x\ln x+3x$. Alors $F(e)=e^2-3e+3e=e^2$ et $F(1)=1-0+3=4$. Donc

$$
\int_1^e f(x)\,dx=F(e)-F(1)=e^2-4\approx 3{,}39.
$$

### Piège à éviter
Prendre $x\ln x-x$ comme primitive de $3\ln x$ : il faut la multiplier par $3$ avant de soustraire.

</details>

Avis : 

---

# 3. Mini-inédite Mathématiques BAC E n°1

**Cursus :** BAC E (Terminale E). **Identifiant :** `ep-cm-maths-bac-e-mini-1-2026-s1`.

**Points précis à juger :**

- Théorème de Gauss, équation diophantienne `5x + 7y = 1` dans Z² : au programme de Terminale E ? (Le référentiel officiel de Première cite l'arithmétique pour la série TI ; pour la série E, le programme de Terminale n'est pas dans nos fichiers.)
- Congruences : période des restes de `3^n` modulo 7 et reste de `3^2026`. Notation `≡ [7]` ou `(mod 7)` : laquelle est celle des manuels ?
- Statistique à deux variables : la variance `V(x) = 35/12` est donnée dans l'énoncé, et `σx`, `σy` à la question 3. Cela allège-t-il trop le calcul pour un BAC E ?

**Avis général sur cette mini-inédite :** 

## Exercice 1 (5 points)

On étudie les puissances de $3$ modulo $7$.

### Question 1.1 (1.5 pts, difficulté faible)

Recopier et compléter le tableau suivant, où $r_n$ est le reste de la division euclidienne de $3^n$ par $7$. Que remarque-t-on ?

| $n$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| $r_n$ | | | | | | | |

**Grille de notation :**

- Complète $r_0$ à $r_3$ correctement : $1$, $3$, $2$, $6$ (0.5 pt)
- Complète $r_4$ à $r_6$ correctement : $4$, $5$, $1$ (0.5 pt)
- Remarque que les restes sont périodiques de période $6$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour étudier les restes de $a^n$ modulo $m$, on calcule les puissances de proche en proche en réduisant modulo $m$ à chaque étape, jusqu'à retrouver le reste $1$ : la suite des restes est alors périodique.

On calcule en réduisant modulo $7$ à chaque étape : $3^0=1$, $3^1\equiv3$, $3^2=9\equiv2$, $3^3\equiv2\times3=6$, $3^4\equiv6\times3=18\equiv4$, $3^5\equiv4\times3=12\equiv5$, $3^6\equiv5\times3=15\equiv1$.

| $n$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| $r_n$ | 1 | 3 | 2 | 6 | 4 | 5 | 1 |

On retrouve le reste $1$ pour $n=6$ : les restes se répètent avec la période $6$.

### Piège à éviter
Réduire à chaque étape : calculer directement $3^5=243$ puis diviser par $7$ fonctionne, mais devient impraticable pour de grands exposants.

</details>

Avis : 

### Question 1.2 (1.5 pts, difficulté moyenne)

Déterminer le reste de la division euclidienne de $3^{2026}$ par $7$. En déduire que $3^{2026}+3$ est divisible par $7$.

**Grille de notation :**

- Écrit $2026=6\times337+4$ (0.5 pt)
- Conclut que le reste est $4$ (0.5 pt)
- Montre $3^{2026}+3\equiv0\pmod7$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
Si les restes de $a^n$ modulo $m$ se répètent avec la période $p$, le reste de $a^N$ est celui de $a^r$ où $r$ est le reste de la division euclidienne de $N$ par $p$.

La période est $6$. On divise $2026$ par $6$ : $2026=6\times337+4$. Donc $3^{2026}=\left(3^{6}\right)^{337}\times3^4\equiv1^{337}\times3^4=81\equiv4\pmod 7$. Le reste est $4$.

Alors $3^{2026}+3\equiv4+3=7\equiv0\pmod 7$ : le nombre $3^{2026}+3$ est divisible par $7$.

### Piège à éviter
Diviser $2026$ par $7$ au lieu de $6$ : c'est la période des restes, pas le modulo, qui sert de diviseur.

</details>

Avis : 

### Question 1.3 (2 pts, difficulté elevee)

**a)** Vérifier que le couple $(3\,;-2)$ est solution de l'équation $(E)$ : $5x+7y=1$.

**b)** Résoudre dans $\mathbb{Z}^2$ l'équation $(E)$.

**Grille de notation :**

- Vérifie $5\times3+7\times(-2)=1$ (0.5 pt)
- Obtient $5(x-3)=-7(y+2)$ (0.5 pt)
- Applique le théorème de Gauss : $x=3+7k$ (0.5 pt)
- Donne les solutions $(3+7k\,;-2-5k)$ et vérifie la réciproque (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour résoudre $ax+by=c$ dans $\mathbb{Z}^2$, on part d'une solution particulière $(x_0\,;y_0)$, on soustrait pour obtenir $a(x-x_0)=-b(y-y_0)$, puis le théorème de Gauss donne toutes les solutions lorsque $a$ et $b$ sont premiers entre eux.

**a)** $5\times3+7\times(-2)=15-14=1$ : le couple $(3\,;-2)$ est bien solution.

**b)** Soit $(x\,;y)$ une solution. En soustrayant $5\times3+7\times(-2)=1$, on obtient $5(x-3)+7(y+2)=0$, soit $5(x-3)=-7(y+2)$. Donc $7$ divise $5(x-3)$. Comme $7$ et $5$ sont premiers entre eux, le théorème de Gauss donne : $7$ divise $x-3$, donc $x=3+7k$ avec $k\in\mathbb{Z}$. En remplaçant, $5\times7k=-7(y+2)$, d'où $y=-2-5k$.

Réciproquement, $5(3+7k)+7(-2-5k)=1$ pour tout $k$. L'ensemble des solutions est $\{(3+7k\,;-2-5k)\ ;\ k\in\mathbb{Z}\}$.

### Piège à éviter
Donner seulement le couple $(3\,;-2)$ : une équation diophantienne a une infinité de solutions, qu'il faut décrire toutes avec un paramètre $k$.

</details>

Avis : 

## Exercice 2 (5 points)

La gérante d'une boutique de Garoua relève, pendant six mois, le nombre $x_i$ de clients (en centaines) et le chiffre d'affaires $y_i$ (en millions de francs CFA).

| Mois | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| $x_i$ | 1 | 2 | 3 | 4 | 5 | 6 |
| $y_i$ | 2,0 | 3,1 | 3,9 | 5,2 | 5,8 | 7,0 |

### Question 2.1 (1.5 pts, difficulté faible)

Déterminer les coordonnées du point moyen $G$ du nuage, puis calculer la covariance $\mathrm{cov}(x,y)$, arrondie à $10^{-2}$.

**Grille de notation :**

- Calcule $\bar{x}=3{,}5$ et $\bar{y}=4{,}5$ (0.5 pt)
- Calcule $\sum x_iy_i=111{,}7$ (0.5 pt)
- Obtient $\mathrm{cov}(x,y)\approx2{,}87$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
Le point moyen est $G(\bar{x}\,;\bar{y})$ et la covariance vaut $\mathrm{cov}(x,y)=\dfrac{1}{n}\displaystyle\sum x_iy_i-\bar{x}\,\bar{y}$.

$\bar{x}=\dfrac{1+2+3+4+5+6}{6}=3{,}5$ et $\bar{y}=\dfrac{2{,}0+3{,}1+3{,}9+5{,}2+5{,}8+7{,}0}{6}=\dfrac{27}{6}=4{,}5$, donc $G(3{,}5\,;4{,}5)$.

On a $\sum x_iy_i=2+6{,}2+11{,}7+20{,}8+29+42=111{,}7$. Donc

$$
\mathrm{cov}(x,y)=\dfrac{111{,}7}{6}-3{,}5\times4{,}5\approx18{,}62-15{,}75\approx 2{,}87.
$$

### Piège à éviter
Oublier de retrancher $\bar{x}\,\bar{y}$ : $\dfrac{1}{n}\sum x_iy_i$ seul n'est pas la covariance.

</details>

Avis : 

### Question 2.2 (1.5 pts, difficulté moyenne)

Donner une équation de la droite de régression de $y$ en $x$, sous la forme $y=ax+b$, avec $a$ et $b$ arrondis à $10^{-3}$ (on rappelle que $V(x)=\dfrac{35}{12}$).

**Grille de notation :**

- Calcule $a=\dfrac{\mathrm{cov}(x,y)}{V(x)}\approx0{,}983$ (0.5 pt)
- Calcule $b=\bar{y}-a\bar{x}\approx1{,}060$ (0.5 pt)
- Écrit l'équation $y=0{,}983x+1{,}060$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
La droite de régression de $y$ en $x$ a pour équation $y=ax+b$ avec $a=\dfrac{\mathrm{cov}(x,y)}{V(x)}$ et $b=\bar{y}-a\bar{x}$ : elle passe par le point moyen.

$a=\dfrac{\mathrm{cov}(x,y)}{V(x)}=\dfrac{2{,}8667}{2{,}9167}\approx0{,}983$. Puis $b=\bar{y}-a\bar{x}=4{,}5-0{,}983\times3{,}5\approx1{,}060$.

La droite de régression de $y$ en $x$ a pour équation $y\approx0{,}983\,x+1{,}060$.

### Piège à éviter
Calculer $b$ avec un $a$ très arrondi : garde au moins trois décimales pour $a$, sinon $b$ s'écarte de la bonne valeur.

</details>

Avis : 

### Question 2.3 (2 pts, difficulté elevee)

**a)** Calculer le coefficient de corrélation linéaire $r$, arrondi à $10^{-3}$, sachant que $\sigma_x\approx1{,}708$ et $\sigma_y\approx1{,}683$. Le résultat justifie-t-il un ajustement affine ?

**b)** Estimer le chiffre d'affaires pour $800$ clients.

**Grille de notation :**

- Calcule $r\approx0{,}997$ (0.5 pt)
- Conclut que l'ajustement affine est justifié (proche de $1$) (0.5 pt)
- Traduit $800$ clients par $x=8$ (0.5 pt)
- Estime $y\approx8{,}92$ millions de francs CFA (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
Le coefficient de corrélation linéaire est $r=\dfrac{\mathrm{cov}(x,y)}{\sigma_x\,\sigma_y}$ ; plus $|r|$ est proche de $1$, plus l'ajustement affine est justifié, et on prévoit une valeur en remplaçant $x$ dans l'équation de la droite.

**a)** $r=\dfrac{\mathrm{cov}(x,y)}{\sigma_x\sigma_y}\approx\dfrac{2{,}8667}{1{,}708\times1{,}683}\approx0{,}997$. Cette valeur est très proche de $1$ : le nuage est presque aligné, l'ajustement affine est justifié.

**b)** $800$ clients correspondent à $x=8$ (en centaines). Alors $y\approx0{,}983\times8+1{,}060\approx8{,}92$. Le chiffre d'affaires estimé est d'environ $8{,}92$ millions de francs CFA.

### Piège à éviter
Remplacer $x$ par $800$ : l'unité de $x$ est la centaine de clients, donc $800$ clients correspondent à $x=8$.

</details>

Avis : 

---

# 4. Mini-inédite Mathématiques Probatoire D et TI n°1

**Cursus :** Probatoire D et TI (Première D et TI). **Identifiant :** `ep-cm-maths-probatoire-d-ti-mini-1-2026-s1`.

**Points précis à juger :**

- Suites arithmétique et géométrique, sans logarithme : le seuil de la question 1.3c se trouve par essais à la calculatrice (`0,9^6`, puis `0,9^7`). Est-ce la démarche attendue en Première ?
- Fonction polynôme de degré 3 : tangente en un point et points à tangente parallèle à une droite donnée. Niveau de Première D et TI ?
- Un seul énoncé pour deux séries (D et TI) : le niveau convient-il aux deux ?

**Avis général sur cette mini-inédite :** 

## Exercice 1 (5 points)

### Question 1.1 (1.5 pts, difficulté faible)

Un artisan de Bafoussam fabrique $12$ tabourets la première semaine, puis $4$ tabourets de plus chaque semaine que la semaine précédente. On note $u_n$ le nombre de tabourets fabriqués la semaine $n$ (avec $n\geqslant1$), donc $u_1=12$. Montrer que la suite $(u_n)$ est arithmétique, donner sa raison, puis exprimer $u_n$ en fonction de $n$.

**Grille de notation :**

- Écrit $u_{n+1}=u_n+4$ et conclut : suite arithmétique de raison $4$ (0.5 pt)
- Applique $u_n=u_1+(n-1)r$ (0.5 pt)
- Obtient $u_n=4n+8$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
Une suite $(u_n)$ est arithmétique de raison $r$ si $u_{n+1}-u_n=r$ pour tout $n$ ; son terme général est $u_n=u_p+(n-p)\,r$.

Chaque semaine, l'artisan fabrique $4$ tabourets de plus : $u_{n+1}=u_n+4$ pour tout $n\geqslant1$. La suite $(u_n)$ est donc arithmétique de raison $r=4$.

Son premier terme est $u_1=12$, donc $u_n=u_1+(n-1)\times4=12+4n-4=4n+8$.

### Piège à éviter
Écrire $u_n=12+4n$ : le premier terme est $u_1$ et non $u_0$, donc il y a $n-1$ augmentations jusqu'à la semaine $n$.

</details>

Avis : 

### Question 1.2 (1.5 pts, difficulté moyenne)

Calculer le nombre de tabourets fabriqués la semaine $20$, puis le nombre total de tabourets fabriqués pendant les $20$ premières semaines.

**Grille de notation :**

- Calcule $u_{20}=88$ (0.5 pt)
- Compte correctement $20$ termes (0.5 pt)
- Calcule la somme $20\times\dfrac{12+88}{2}=1\,000$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
La somme de $p$ termes consécutifs d'une suite arithmétique vaut $p\times\dfrac{\text{premier terme}+\text{dernier terme}}{2}$ ; il faut donc compter avec soin le nombre de termes.

La semaine $20$ : $u_{20}=4\times20+8=88$ tabourets.

Pendant les $20$ premières semaines, il y a $20$ termes, du premier $u_1=12$ au dernier $u_{20}=88$ :

$$
S=20\times\dfrac{12+88}{2}=20\times50=1\,000.
$$

L'artisan fabrique $1\,000$ tabourets en $20$ semaines.

### Piège à éviter
Compter $21$ termes ou utiliser $\dfrac{20}{2}\times(u_0+u_{20})$ : la suite commence à $u_1$, il y a exactement $20$ termes de $u_1$ à $u_{20}$.

</details>

Avis : 

### Question 1.3 (2 pts, difficulté elevee)

Une machine achetée $2\,000\,000$ F perd $10\,\%$ de sa valeur chaque année. On note $v_n$ sa valeur, en francs, après $n$ années.

**a)** Montrer que $(v_n)$ est une suite géométrique et exprimer $v_n$ en fonction de $n$.

**b)** Calculer la valeur de la machine après $5$ ans.

**c)** À l'aide de la calculatrice, déterminer le nombre d'années à partir duquel la machine vaut moins de $1\,000\,000$ F.

**Grille de notation :**

- Montre $v_{n+1}=0{,}9\,v_n$ et donne $v_n=2\,000\,000\times0{,}9^n$ (0.5 pt)
- Calcule $v_5=1\,180\,980$ F (0.5 pt)
- Calcule $v_6$ et $v_7$ à la calculatrice (0.5 pt)
- Conclut : à partir de la $7^{\text{e}}$ année (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
Une suite $(v_n)$ est géométrique de raison $q$ si $v_{n+1}=q\,v_n$ pour tout $n$ ; son terme général est $v_n=v_0\,q^n$. Une baisse de $t\,\%$ revient à multiplier par $1-\dfrac{t}{100}$.

**a)** Perdre $10\,\%$ revient à multiplier par $0{,}9$ : $v_{n+1}=0{,}9\,v_n$. La suite $(v_n)$ est géométrique de raison $q=0{,}9$ et de premier terme $v_0=2\,000\,000$, donc $v_n=2\,000\,000\times0{,}9^n$.

**b)** $v_5=2\,000\,000\times0{,}9^5=2\,000\,000\times0{,}59049=1\,180\,980$ F.

**c)** On calcule les valeurs successives : $v_6=2\,000\,000\times0{,}9^6\approx1\,062\,882$ F, encore supérieure à $1\,000\,000$ F, puis $v_7=2\,000\,000\times0{,}9^7\approx956\,594$ F, inférieure à $1\,000\,000$ F. La machine vaut moins de $1\,000\,000$ F à partir de la $7^{\text{e}}$ année.

### Piège à éviter
Multiplier par $0{,}1$ au lieu de $0{,}9$ : une baisse de $10\,\%$ garde $90\,\%$ de la valeur, donc on multiplie par $0{,}9$.

</details>

Avis : 

## Exercice 2 (5 points)

On considère la fonction $f$ définie sur $\mathbb{R}$ par $f(x)=x^3-6x^2+9x+1$, et on note $(\mathcal{C})$ sa courbe représentative dans un repère orthonormé.

### Question 2.1 (1.5 pts, difficulté faible)

Calculer les limites de $f$ en $-\infty$ et en $+\infty$.

**Grille de notation :**

- Met $x^3$ en facteur (0.5 pt)
- Trouve $+\infty$ en $+\infty$ (0.5 pt)
- Trouve $-\infty$ en $-\infty$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
En $\pm\infty$, la limite d'une fonction polynôme est celle de son terme de plus haut degré ; on peut aussi mettre ce terme en facteur : $x^3\left(1-\dfrac{6}{x}+\dfrac{9}{x^2}+\dfrac{1}{x^3}\right)$.

Pour $x\neq0$, $f(x)=x^3\left(1-\dfrac{6}{x}+\dfrac{9}{x^2}+\dfrac{1}{x^3}\right)$. La parenthèse tend vers $1$ quand $x$ tend vers $\pm\infty$.

Donc $\displaystyle\lim_{x\to+\infty}f(x)=+\infty$ et $\displaystyle\lim_{x\to-\infty}f(x)=-\infty$, puisque $x^3$ tend vers $+\infty$ en $+\infty$ et vers $-\infty$ en $-\infty$.

### Piège à éviter
Conclure « $+\infty-\infty$ » en voyant $x^3-6x^2$ : c'est une forme indéterminée, qu'on lève en factorisant par le terme de plus haut degré.

</details>

Avis : 

### Question 2.2 (1.5 pts, difficulté moyenne)

Calculer $f'(x)$, vérifier que $f'(x)=3(x-1)(x-3)$, puis dresser le tableau de variations de $f$.

**Grille de notation :**

- Dérive correctement : $f'(x)=3x^2-12x+9$ (0.5 pt)
- Vérifie la forme factorisée $3(x-1)(x-3)$ (0.5 pt)
- Donne le tableau avec $f(1)=5$ et $f(3)=1$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
On dérive terme à terme avec $(x^n)'=nx^{n-1}$ ; le signe de $f'$ donne les variations de $f$ : croissante là où $f'>0$, décroissante là où $f'<0$.

Pour tout réel $x$, $f'(x)=3x^2-12x+9$. En développant, $3(x-1)(x-3)=3(x^2-4x+3)=3x^2-12x+9$ : on retrouve bien $f'(x)=3(x-1)(x-3)$.

Le trinôme $3(x-1)(x-3)$ est positif à l'extérieur des racines $1$ et $3$, négatif entre elles. On a $f(1)=1-6+9+1=5$ et $f(3)=27-54+27+1=1$.

| $x$ | $-\infty$ | | $1$ | | $3$ | | $+\infty$ |
|---|---|---|---|---|---|---|---|
| $f'(x)$ | | $+$ | $0$ | $-$ | $0$ | $+$ | |
| $f(x)$ | $-\infty$ | $\nearrow$ | $5$ | $\searrow$ | $1$ | $\nearrow$ | $+\infty$ |

### Piège à éviter
Se tromper de signe entre les racines : un trinôme $ax^2+bx+c$ avec $a>0$ est négatif entre ses racines, positif à l'extérieur.

</details>

Avis : 

### Question 2.3 (2 pts, difficulté elevee)

**a)** Déterminer une équation de la tangente à $(\mathcal{C})$ au point d'abscisse $0$.

**b)** Déterminer les points de $(\mathcal{C})$ où la tangente est parallèle à la droite $(D)$ d'équation $y=9x$.

**Grille de notation :**

- Calcule $f(0)=1$ et $f'(0)=9$ (0.5 pt)
- Écrit la tangente $y=9x+1$ (0.5 pt)
- Résout $f'(x)=9$ : $x=0$ ou $x=4$ (0.5 pt)
- Donne les points $(0\,;1)$ et $(4\,;5)$ (0.5 pt)

<details><summary>Corrigé</summary>

### Rappel de méthode
L'équation de la tangente à $(\mathcal{C})$ au point d'abscisse $a$ est $y=f'(a)(x-a)+f(a)$ ; deux droites sont parallèles lorsqu'elles ont le même coefficient directeur, donc les points où la tangente a pour pente $m$ sont les solutions de $f'(x)=m$.

**a)** $f(0)=1$ et $f'(0)=3\times(-1)\times(-3)=9$. La tangente au point d'abscisse $0$ a pour équation $y=9(x-0)+1$, soit $y=9x+1$.

**b)** La droite $(D)$ a pour coefficient directeur $9$. On cherche donc les réels $x$ tels que $f'(x)=9$ :

$$
3x^2-12x+9=9\iff3x^2-12x=0\iff3x(x-4)=0\iff x=0\ \text{ou}\ x=4.
$$

On a $f(0)=1$ et $f(4)=64-96+36+1=5$. Les points cherchés sont $(0\,;1)$ et $(4\,;5)$.

### Piège à éviter
Garder $y=9x$ pour la tangente en $0$ : elle est parallèle à $(D)$ mais ne passe pas par l'origine, car $f(0)=1\neq0$.

</details>

Avis : 

