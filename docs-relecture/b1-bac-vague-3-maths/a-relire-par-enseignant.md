# Vague 3 Maths BAC : 93 QCM à faire relire par l'enseignant (campagne B1)

Date : 2026-10-31. Sur 124 QCM convertis (150 questions étudiées, 26 écartées), **93** vous sont soumis : ceux que le relecteur aveugle a assortis d'une remarque, ceux dont la question ou la méthode a été modifiée, ceux dont une série a été retirée, et un tirage de 10 autres. Aucun n'est en ligne. Les 125 résolutions à l'aveugle ont toutes donné la clé ; une question (PPCM de niveau collège) a été retirée ensuite pour être trop facile.

Vos arbitrages du 2026-10-31 sont appliqués (arithmétique en C, E et TI ; coniques et discriminant complexe pas en D ; similitudes indirectes pas en C ; série A sans a^x, branche parabolique, prolongement par continuité, somme de plusieurs termes d'une loi binomiale, complexes ; équation du 3e degré en A seulement avec indication ; équations différentielles du 2nd ordre en TI).

## Points à trancher (nouveaux)

1. **Trigonométrie en série A :** les primitives et dérivées avec $\sin x$ ou $\cos x$ sont-elles au programme de A ? Par prudence, la série A est retirée de « dérivée d'un produit moyenne-1 » et « primitives usuelles moyenne-4 ».
2. **Série A, limites hautes :** dérivée de $\ln(u)$ avec $u=x^2+1$ ; dérivée de $e^{u(x)}$ avec $u$ du second degré ; primitive de la forme $u'/u$ avec $u=1-x$ ; croissances comparées $x^n e^{-x}$. Gardés en A pour l'instant : à confirmer.
3. **Matrice 2x2 en série C** (composition d'endomorphismes moyenne-3) : le référentiel réserve les matrices à TI ; l'algèbre linéaire en dimension 2 est admise en C. Matrice acceptable en C ?
4. **Séries D et TI, équations différentielles du 2nd ordre :** racine double, solution générale avec second membre, solution particulière donnée. Confirmer qu'elles sont au programme de D et de TI.
5. **Barycentre et ligne de niveau de $\sum \alpha_i MA_i^2$** (réduction vectorielle) en série TI.
6. **Série A retirée par analogie avec vos décisions :** prolongement par continuité (3), branche parabolique (2), fonction exponentielle moyenne-1 (base 3), équiprobabilité moyenne-1 et -2 (combinaisons), événement contraire moyenne-2 (combinaisons), forme algébrique d'un quotient moyenne-1 et -2 (complexes), loi binomiale moyenne-4 (coefficient binomial). Série D retirée : discriminant complexe (2), ellipse (3), excentricité (2).
7. **« Exponentielle faible-0 » en série A :** la réponse est $\ln 3$ sans fonction $a^x$ : on garde A ?

Pour chaque question : **OK**, **à corriger** (dire quoi), **à retirer**, ou **retirer la série X**.

## 1. `cqc-nombres-complexes-equations-polynomiales-bac-ti-mat-elevee-2` (séries TI)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère l'équation $(E)$ : $z^3=27$, d'inconnue $z\in\mathbb{C}$.

Quel est l'ensemble des solutions de $(E)$ dans $\mathbb{C}$ ?

- a) $\left\{-3\,;\,\dfrac{3+3i\sqrt3}{2}\,;\,\dfrac{3-3i\sqrt3}{2}\right\}$
- b) $\left\{3\,;\,\dfrac{-3+3i\sqrt3}{2}\,;\,\dfrac{-3-3i\sqrt3}{2}\right\}$
- c) $\left\{3\,;\,\dfrac{3+3i\sqrt3}{2}\,;\,\dfrac{3-3i\sqrt3}{2}\right\}$
- d) $\left\{3\,;\,-3+3i\sqrt3\,;\,-3-3i\sqrt3\right\}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Une équation du troisième degré dont une factorisation est connue se résout par produit nul : on résout séparément chaque facteur. Pour un facteur du second degré à coefficients réels et de discriminant $\Delta<0$, les solutions sont deux nombres complexes conjugués, $z=\dfrac{-b\pm i\sqrt{-\Delta}}{2a}$.

### Corrigé
Le nombre $3$ est une solution évidente ($3^3=27$). On développe :

$$(z-3)(z^2+3z+9)=z^3+3z^2+9z-3z^2-9z-27=z^3-27.$$

L'équation $(E)$ équivaut donc à $(z-3)(z^2+3z+9)=0$, soit $z=3$ ou $z^2+3z+9=0$. Pour le trinôme :

$$\Delta=3^2-4\times1\times9=9-36=-27<0\qquad\text{et}\qquad\sqrt{-\Delta}=\sqrt{27}=3\sqrt3.$$

Les deux solutions non réelles sont $z_1=\dfrac{-3+3i\sqrt3}{2}$ et $z_2=\dfrac{-3-3i\sqrt3}{2}$. Ainsi :

$$\mathcal S=\left\{3\,;\,\dfrac{-3+3i\sqrt3}{2}\,;\,\dfrac{-3-3i\sqrt3}{2}\right\}.$$

Contrôle : la somme des trois solutions vaut $3+\dfrac{-6}{2}=0$ (coefficient de $z^2$ nul) et leur produit vaut $3\times z_1z_2=3\times\dfrac{9+27}{4}=27$ (terme constant $-27$). On vérifie aussi $z_1^2=\dfrac{-9-9i\sqrt3}{2}$ puis $z_1^3=\dfrac{(-9-9i\sqrt3)(-3+3i\sqrt3)}{4}=\dfrac{108}{4}=27$.

### Pourquoi les autres réponses sont fausses
- **a)** Erreur de signe dans la factorisation : $-3$ n'est pas solution, car $(-3)^3=-27$.
- **c)** Oubli du signe de $-b$ : $\dfrac{3\pm3i\sqrt3}{2}$ sont les racines de $z^2-3z+9$, pas de $z^2+3z+9$.
- **d)** Oubli de la division par $2a=2$ dans la formule des racines.

</details>

Avis : 

---

## 2. `cqc-racine-d-un-polynome-bac-ti-mat-elevee-2` (séries TI)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère le polynôme $P$, à coefficients réels, défini pour tout nombre complexe $z$ par $$P(z)=z^4-3z^3+6z^2+2z-60.$$

On admet que $1+3i$ est une racine de $P$. Quelles sont les quatre racines de $P$ dans $\mathbb{C}$ ?

- a) $1+3i$, $1-3i$, $-3$ et $2$
- b) $1+3i$, $-1-3i$, $3$ et $-2$
- c) $1+3i$, $1-3i$, $\dfrac{1+i\sqrt{23}}{2}$ et $\dfrac{1-i\sqrt{23}}{2}$
- d) $1+3i$, $1-3i$, $3$ et $-2$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Si tous les coefficients d'un polynôme $P$ sont réels, alors $P(\bar z)=\overline{P(z)}$ pour tout complexe $z$ : une racine non réelle est toujours accompagnée de sa conjuguée. Une factorisation par un trinôme connu se détermine en développant puis en identifiant les coefficients, et un polynôme de degré $n$ ne possède jamais plus de $n$ racines complexes.

### Corrigé
**Racine conjuguée.** Les coefficients de $P$ sont réels, donc $P(1-3i)=\overline{P(1+3i)}=\bar0=0$ : $1-3i$ est aussi racine. Par ailleurs :

$$(z-1-3i)(z-1+3i)=(z-1)^2-(3i)^2=z^2-2z+10.$$

**Factorisation.** On cherche $a$ et $b$ réels tels que $P(z)=(z^2-2z+10)(z^2+az+b)$. En développant :

$$(z^2-2z+10)(z^2+az+b)=z^4+(a-2)z^3+(b-2a+10)z^2+(10a-2b)z+10b.$$

En identifiant : $a-2=-3$, donc $a=-1$ ; $b-2a+10=6$, donc $b=6+2a-10=-6$ ; contrôles : $10a-2b=-10+12=2$ et $10b=-60$.

Ainsi $P(z)=(z^2-2z+10)(z^2-z-6)=(z-1-3i)(z-1+3i)(z-3)(z+2)$.

**Racines.** Les racines de $P$ sont $1+3i$, $1-3i$, $3$ et $-2$ ; elles sont distinctes et un polynôme de degré $4$ n'en a pas plus de quatre.

Contrôle : $P(-2)=16+24+24-4-60=0$, et en $z=1$ : $P(1)=-54=(1-2+10)(1-1-6)$.

### Pourquoi les autres réponses sont fausses
- **a)** Erreur de signe sur $a$ (on prend $a=1$) : on factorise alors $z^2+z-6=(z+3)(z-2)$, mais $P(2)=-40\neq0$.
- **b)** Confusion entre conjugué et opposé : $-1-3i$ n'est pas racine de $P$.
- **c)** Erreur de signe sur $b$ (on prend $b=6$) : le trinôme $z^2-z+6$ ne divise pas $P$, ses racines ne sont pas celles de $P$.

</details>

Avis : 

---

## 3. `cqc-racine-d-un-polynome-bac-ti-mat-moyenne-1` (séries TI)

**Remarque du relecteur :** La racine imaginaire pure n'est pas donnée : l'élève doit la chercher (iy) ; faisable en TI.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère le polynôme $Q$ défini, pour tout nombre complexe $z$, par $$Q(z)=z^3+(2-3i)z^2+(5-6i)z-15i.$$

Le polynôme $Q$ admet une unique racine imaginaire pure $z_0$, c'est-à-dire de la forme $z_0=iy$ avec $y$ réel. Laquelle des écritures suivantes est une factorisation correcte de $Q(z)$, valable pour tout complexe $z$ ?

- a) $Q(z)=(z-3i)\big(z^2+(2-6i)z+5\big)$
- b) $Q(z)=(z+3i)(z^2+2z+5)$
- c) $Q(z)=(z-3i)(z^2+2z+5)$
- d) $Q(z)=(z-3i)(z^2+2z+5-12i)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour chercher une racine imaginaire pure, on remplace $z$ par $iy$ avec $y$ réel, puis on sépare la partie réelle et la partie imaginaire de $Q(iy)$ : le résultat est nul seulement si ces deux parties s'annulent en même temps. Pour factoriser par $(z-z_0)$, on développe $(z-z_0)(z^2+az+b)$ et on identifie les coefficients de chaque puissance de $z$ avec ceux de $Q$.

### Corrigé
**Racine imaginaire pure.** Pour $y$ réel :

$$Q(iy)=\big(-2y^2+6y\big)+i\big(-y^3+3y^2+5y-15\big).$$

La partie réelle s'annule pour $y=0$ ou $y=3$. Pour $y=0$, la partie imaginaire vaut $-15\neq0$ ; pour $y=3$, elle vaut $-27+27+15-15=0$. Donc $z_0=3i$.

**Factorisation.** On développe :

$$(z-3i)(z^2+az+b)=z^3+(a-3i)z^2+(b-3ia)z-3ib.$$

En identifiant avec $Q(z)$ : $a-3i=2-3i$, donc $a=2$ ; $b-3ia=5-6i$, donc $b=5-6i+6i=5$ ; contrôle : $-3ib=-15i$.

Ainsi $Q(z)=(z-3i)(z^2+2z+5)$.

Contrôle : en $z=1$, $Q(1)=8-24i$ et $(1-3i)(1+2+5)=8-24i$.

### Pourquoi les autres réponses sont fausses
- **a)** Erreur dans l'identification du coefficient de $z^2$ : on a soustrait $3i$ au lieu de l'ajouter, d'où $a=2-6i$.
- **b)** Confusion entre $z-z_0$ et $z+z_0$ : $-3i$ n'est pas racine de $Q$.
- **d)** Erreur de signe sur le terme $-3ia$ : on obtient $b=5-12i$, qui ne redonne pas le terme constant $-15i$.

</details>

Avis : 

---

## 4. `cqc-affixe-bac-ti-mat-elevee-2` (séries TI)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $(O;\vec u,\vec v)$ un repère orthonormé direct du plan complexe. Les points $A$, $B$ et $C$ ont pour affixes $z_A=-5+2i$, $z_B=1-4i$ et $z_C=7+2i$.

Soit $G$ le barycentre des points $A$, $B$ et $C$ affectés respectivement des coefficients $-1$, $1$ et $1$. Quelle est l'affixe de $G$ ?

- a) $13-4i$
- b) $\dfrac{13}{3}-\dfrac{4}{3}i$
- c) $3$
- d) $13$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Le barycentre $G$ de points pondérés $(A_k\,;\alpha_k)$ dont la somme des poids n'est pas nulle a pour affixe $z_G=\dfrac{\sum\alpha_kz_{A_k}}{\sum\alpha_k}$. L'affixe du vecteur $\overrightarrow{MN}$ est $z_N-z_M$.

### Corrigé
La somme des poids vaut $-1+1+1=1\neq0$ : le barycentre $G$ existe. Son affixe est

$$z_G=\dfrac{-z_A+z_B+z_C}{1}=(5-2i)+(1-4i)+(7+2i)=13-4i.$$

Contrôle : la relation $-\overrightarrow{GA}+\overrightarrow{GB}+\overrightarrow{GC}=\vec0$ équivaut à $\overrightarrow{AG}=\overrightarrow{AB}+\overrightarrow{AC}$. Or $z_B-z_A=6-6i$ et $z_C-z_A=12$, d'où $z_G=z_A+18-6i=13-4i$. Le point $G$ est le quatrième sommet du parallélogramme $ABGC$ : les milieux de $[AG]$ et $[BC]$ ont tous deux pour affixe $4-i$.

### Pourquoi les autres réponses sont fausses
- **b)** On a divisé par $3$, le nombre de points, au lieu de la somme des poids $-1+1+1=1$.
- **c)** On a oublié le coefficient $-1$ et calculé $z_A+z_B+z_C=3$.
- **d)** Erreur de signe sur la partie imaginaire de $-z_A$ : on a pris $5+2i$ au lieu de $5-2i$.

</details>

Avis : 

---

## 5. `cqc-arguments-bac-ti-mat-elevee-2` (séries TI)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Le plan complexe étant muni d'un repère orthonormé direct, les points $A$, $B$ et $C$ ont pour affixes $z_A=4-i$, $z_B=1+3i$ et $z_C=-3$.

Quelles sont une mesure de l'angle orienté $(\overrightarrow{AB},\overrightarrow{AC})$ et la valeur du rapport $\dfrac{AC}{AB}$ ?

- a) $\dfrac{\pi}{4}$ et $2$
- b) $-\dfrac{\pi}{4}$ et $\dfrac{\sqrt2}{2}$
- c) $\dfrac{\pi}{4}$ et $\sqrt2$
- d) $\dfrac{\pi}{4}$ et $\dfrac{\sqrt2}{2}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour trois points distincts $A$, $B$, $C$, un argument du quotient $\dfrac{z_C-z_A}{z_B-z_A}$ mesure l'angle orienté $(\overrightarrow{AB},\overrightarrow{AC})$, et son module est le rapport $\dfrac{AC}{AB}$.

### Corrigé
On a $z_B-z_A=-3+4i$ et $z_C-z_A=-7+i$. On multiplie numérateur et dénominateur par le conjugué $-3-4i$ du dénominateur, qui devient $(-3)^{2}+4^{2}=25$ :

$$\dfrac{-7+i}{-3+4i}=\dfrac{(-7+i)(-3-4i)}{25}=\dfrac{21+28i-3i-4i^{2}}{25}=\dfrac{25+25i}{25}=1+i.$$

Or $1+i=\sqrt2\left(\cos\dfrac{\pi}{4}+i\sin\dfrac{\pi}{4}\right)$. Donc $(\overrightarrow{AB},\overrightarrow{AC})=\dfrac{\pi}{4}$ (à $2\pi$ près) et $\dfrac{AC}{AB}=\sqrt2$.

Contrôle : $AB=|-3+4i|=5$ et $AC=|-7+i|=\sqrt{50}=5\sqrt2$, d'où $\dfrac{AC}{AB}=\sqrt2$. De plus $\dfrac{z_C-z_B}{z_A-z_B}=-i$ : le triangle $ABC$ est rectangle isocèle en $B$, et son angle en $A$ mesure bien $\dfrac{\pi}{4}$.

### Pourquoi les autres réponses sont fausses
- **a)** Le module de $1+i$ est $\sqrt{1^2+1^2}=\sqrt2$, et non $1+1=2$.
- **b)** On a calculé le quotient inversé $\dfrac{z_B-z_A}{z_C-z_A}=\dfrac{1-i}{2}$, qui correspond à l'angle $(\overrightarrow{AC},\overrightarrow{AB})$ et au rapport $\dfrac{AB}{AC}$.
- **d)** L'angle est juste, mais le rapport est inversé : $\dfrac{\sqrt2}{2}$ est la valeur de $\dfrac{AB}{AC}$.

</details>

Avis : 

---

## 6. `cqc-arithmetique-dans-z-moyenne-1` (séries C)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère l'entier naturel $N=1\,800$. Combien $N$ possède-t-il de diviseurs positifs ?

- a) $12$
- b) $10$
- c) $35$
- d) $36$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Si un entier naturel $N$ se décompose en produit de facteurs premiers sous la forme $N=p_1^{\alpha_1}\times p_2^{\alpha_2}\times\cdots\times p_k^{\alpha_k}$, alors le nombre de diviseurs positifs de $N$ est le produit $(\alpha_1+1)(\alpha_2+1)\cdots(\alpha_k+1)$ : chaque diviseur correspond à un choix indépendant d'exposant entre $0$ et $\alpha_i$ pour chaque facteur premier.

### Corrigé
$1\,800\div2=900$, $900\div2=450$, $450\div2=225$ : on a extrait $2^3$. Puis $225\div3=75$, $75\div3=25$ : on a extrait $3^2$. Enfin $25=5^2$. Donc

$$1\,800=2^3\times3^2\times5^2.$$

Vérification : $8\times9\times25=72\times25=1\,800$.

Le nombre de diviseurs positifs de $N$ est

$$(3+1)(2+1)(2+1)=4\times3\times3=36.$$

### Pourquoi les autres réponses sont fausses
- **a)** On a multiplié les exposants $3\times2\times2$ sans ajouter $1$ à chacun (on oublie l'exposant $0$).
- **b)** On a additionné $(3+1)+(2+1)+(2+1)$ au lieu de faire le produit.
- **c)** On a oublié de compter le diviseur $1$ ou le nombre $N$ lui-même.

</details>

Avis : 

---

## 7. `cqc-branche-parabolique-moyenne-3` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $n$ la fonction définie sur $\,]0;+\infty[$ par
$$n(x)=\ln(x)+\dfrac{1}{x}.$$
Quelle est la nature des deux branches infinies de la courbe représentative de $n$ ?

- a) Asymptote verticale $x=0$ ; branche parabolique de direction $(Oy)$ en $+\infty$
- b) Asymptote verticale $x=0$ ; asymptote horizontale $y=0$ en $+\infty$
- c) Asymptote verticale $x=0$ ; branche parabolique de direction $(Ox)$ en $+\infty$
- d) Aucune asymptote en $0$ ; branche parabolique de direction $(Ox)$ en $+\infty$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Une fonction combinant un logarithme et un quotient peut présenter une forme indéterminée en un point : on lève l'indétermination en factorisant, à l'aide au besoin de la limite usuelle $\lim_{x\to0^{+}}x\ln(x)=0$. Une fois les limites établies, on applique le critère habituel : une limite infinie en un réel $a$ donne une asymptote verticale ; si $\lim f(x)$ est infinie en $+\infty$, on étudie $\frac{f(x)}{x}$ : une limite infinie donne une direction $(Oy)$, une limite nulle donne une direction $(Ox)$.

### Corrigé
**En $0^{+}$.** On obtient la forme indéterminée « $-\infty+\infty$ ». On factorise par $\dfrac{1}{x}$ :
$$n(x)=\dfrac{1}{x}\Big(1+x\ln(x)\Big).$$
Or $\lim_{x\to0^{+}}x\ln(x)=0$, donc $1+x\ln(x)\to1$, et comme $\dfrac{1}{x}\to+\infty$ :
$$\lim_{x\to0^{+}}n(x)=+\infty.$$
La droite d'équation $x=0$ est **asymptote verticale** à la courbe.

**En $+\infty$.** $\ln(x)\to+\infty$ et $\dfrac{1}{x}\to0$, donc $\lim_{x\to+\infty}n(x)=+\infty$. Puis
$$\dfrac{n(x)}{x}=\dfrac{\ln(x)}{x}+\dfrac{1}{x^{2}}\quad\text{et}\quad\lim_{x\to+\infty}\dfrac{n(x)}{x}=0$$
par croissances comparées. La courbe présente en $+\infty$ une **branche parabolique de direction $(Ox)$**.

### Pourquoi les autres réponses sont fausses
- **a)** Confusion du critère : une limite nulle de $\frac{n(x)}{x}$ donne la direction $(Ox)$, et non $(Oy)$.
- **b)** On a confondu $\lim\frac{n(x)}{x}=0$ avec $\lim n(x)=0$ : en $+\infty$, $n(x)$ tend vers $+\infty$, il n'y a pas d'asymptote horizontale.
- **d)** On s'est arrêté à la forme indéterminée en $0^{+}$ sans la lever : la limite y vaut $+\infty$, il y a bien une asymptote verticale.

</details>

Avis : 

---

## 8. `cqc-branche-parabolique-moyenne-4` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $q$ la fonction définie sur $[0;+\infty[$ par
$$q(x)=x-\sqrt{x}.$$
Quelle est la nature de la branche infinie de la courbe représentative de $q$ en $+\infty$ ?

- a) Une asymptote oblique d'équation $y=x$
- b) Une branche parabolique de direction $(Ox)$
- c) Une branche parabolique de direction $(Oy)$
- d) Une branche parabolique de direction la droite $y=x$, sans asymptote oblique

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand $\dfrac{f(x)}{x}$ tend vers un nombre fini non nul $a$, la courbe peut suivre la direction de la droite $y=ax$ ; ce n'est une asymptote oblique que si, en plus, $f(x)-ax$ tend vers un nombre fini $b$ (l'asymptote est alors $y=ax+b$). Si $f(x)-ax$ tend vers $+\infty$ ou $-\infty$, il n'y a pas d'asymptote oblique : la courbe présente une branche parabolique de direction $y=ax$.

### Corrigé
**Limite de $q$.** Pour $x>0$, $q(x)=\sqrt{x}\big(\sqrt{x}-1\big)$, donc $\lim_{x\to+\infty}q(x)=+\infty$.

**Limite de $\dfrac{q(x)}{x}$.**
$$\dfrac{q(x)}{x}=1-\dfrac{1}{\sqrt{x}}\quad\text{donc}\quad\lim_{x\to+\infty}\dfrac{q(x)}{x}=1.$$
Cette limite est finie et non nulle ($a=1$) : il reste à examiner $q(x)-x$.

**Limite de $q(x)-x$.** $q(x)-x=-\sqrt{x}$, donc $\lim_{x\to+\infty}\big(q(x)-x\big)=-\infty$.

**Conclusion.** La courbe de $q$ n'admet pas d'asymptote oblique en $+\infty$ : elle présente une **branche parabolique de direction la droite $y=x$**, en s'écartant indéfiniment en dessous de cette droite.

### Pourquoi les autres réponses sont fausses
- **a)** On s'est arrêté à $\lim\frac{q(x)}{x}=1$ sans étudier $q(x)-x$, qui tend vers $-\infty$ et non vers un nombre fini.
- **b)** Une direction $(Ox)$ correspondrait à $\lim\frac{q(x)}{x}=0$, or cette limite vaut $1$.
- **c)** Une direction $(Oy)$ correspondrait à une limite infinie de $\frac{q(x)}{x}$, or cette limite vaut $1$.

</details>

Avis : 

---

## 9. `cqc-calcul-d-aire-faible-0` (séries C/D/E)

**Énoncé :**

Dans un repère orthogonal où l'unité vaut $2$ cm sur l'axe des abscisses et $3$ cm sur l'axe des ordonnées, quelle est, en cm², l'aire du domaine limité par la courbe de $f(x)=x^2$, l'axe des abscisses et les droites $x=0$ et $x=3$ ?

- a) $54$ cm²
- b) $9$ cm²
- c) $18$ cm²
- d) $45$ cm²

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour $f\geq0$ sur $[a\,;b]$, l'aire en unités d'aire est $\displaystyle\int_a^bf(x)\,dx$ ; on la convertit en cm² en multipliant par l'aire d'un rectangle unité (ici $2\times3$ cm²).

### Corrigé
$\displaystyle\int_0^3x^2\,dx=\Big[\dfrac{x^3}{3}\Big]_0^3=9$ unités d'aire.

Une unité d'aire vaut $2\times3=6$ cm², donc l'aire vaut $9\times6=54$ cm².

### Pourquoi les autres réponses sont fausses
- **b)** $9$ est l'aire en unités d'aire : on a oublié la conversion en cm².
- **c)** On n'a multiplié que par l'unité de l'axe des abscisses ($9\times2$).
- **d)** On a additionné les unités ($2+3=5$) au lieu de les multiplier.

</details>

Avis : 

---

## 10. `cqc-composition-d-endomorphismes-tle-c-moyenne-3` (séries C)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $p$ l'endomorphisme de $\mathbb{R}^2$ de matrice $P=\begin{pmatrix}\frac12&\frac12\\[2pt]\frac12&\frac12\end{pmatrix}$ dans la base canonique. Quels sont le noyau et l'image de $p$ ?

- a) $\ker p$ est la droite $y=x$ et $\operatorname{Im}p$ est la droite $y=-x$
- b) $\ker p$ est la droite $y=-x$ et $\operatorname{Im}p$ est la droite $y=x$
- c) $\ker p=\{\vec0\}$ et $\operatorname{Im}p=\mathbb{R}^2$
- d) $\ker p$ est la droite $y=-x$ et $\operatorname{Im}p=\mathbb{R}^2$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Un endomorphisme $p$ tel que $p\circ p=p$ est un projecteur (ou projection vectorielle) : on le vérifie sur les matrices, $P^2=P$. Le noyau et l'image se lisent sur les équations et les colonnes de la matrice, et la somme de leurs dimensions vaut la dimension de l'espace.

### Corrigé
$P^2=\begin{pmatrix}\frac14+\frac14&\frac14+\frac14\\[2pt]\frac14+\frac14&\frac14+\frac14\end{pmatrix}=P$, donc $p\circ p=p$.

On a $p(x\,;y)=\left(\dfrac{x+y}2\,;\dfrac{x+y}2\right)$.
- Noyau : $x+y=0$, soit $\ker p=\operatorname{Vect}\big((1\,;-1)\big)$, la droite d'équation $y=-x$.
- Image : $\operatorname{Im}p=\operatorname{Vect}\big((1\,;1)\big)$, la droite d'équation $y=x$.

Un vecteur commun aux deux droites vérifierait $y=-x$ et $y=x$, donc $x=y=0$ : $\ker p\cap\operatorname{Im}p=\{\vec0\}$. Comme $\dim\ker p+\dim\operatorname{Im}p=2$, $p$ est la projection sur la droite $y=x$ parallèlement à la droite $y=-x$.

### Pourquoi les autres réponses sont fausses
- **a)** Le noyau et l'image sont échangés : $p(1\,;1)=(1\,;1)\neq\vec0$.
- **c)** La relation $p\circ p=p$ ne signifie pas que $p$ est bijective : $p(1\,;-1)=\vec0$, donc le noyau n'est pas réduit à $\{\vec0\}$.
- **d)** L'image est engendrée par les colonnes de $P$, toutes deux égales à $\left(\frac12\,;\frac12\right)$ : c'est une droite, et la somme des dimensions doit valoir $2$.

</details>

Avis : 

---

## 11. `cqc-condition-initiale-moyenne-4` (séries A/C/D/E/TI)

**Remarque du relecteur :** LIMITE : en série A, primitive de la forme u'/u avec u(x)=1-x (signe à gérer) est à la limite haute du programme.

**Énoncé :**

Soit $f$ la fonction définie sur l'intervalle $]-\infty;1[$ par $f(x)=\dfrac{5}{1-x}$.

Quelle est la primitive $F$ de $f$ sur cet intervalle telle que $F(-2)=8-5\ln 3$ ?

- a) $F(x)=-5\ln(1-x)+8$
- b) $F(x)=5\ln(1-x)+8-10\ln 3$
- c) $F(x)=-5\ln(1-x)+8-5\ln 3$
- d) $F(x)=5\ln(1-x)+8$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour une fonction de la forme $f(x)=\dfrac{k}{ax+b}$ avec $a\neq0$, une primitive sur un intervalle où $ax+b$ garde un signe constant est $F(x)=\dfrac{k}{a}\ln\lvert ax+b\rvert+C$ ; ici $a=-1$, ce qui introduit un signe négatif devant le logarithme qu'il ne faut pas oublier. La condition $F(x_0)=y_0$ détermine ensuite la constante.

### Corrigé
**Primitive générale.** Sur $]-\infty;1[$, $1-x>0$, donc une primitive de $f$ est :
$$F(x)=\dfrac{5}{-1}\ln(1-x)+C=-5\ln(1-x)+C,\quad C\in\mathbb{R}.$$

**Détermination de $C$.** $F(-2)=-5\ln 3+C$ et $F(-2)=8-5\ln 3$, donc $C=8$.

**Conclusion.** $F(x)=-5\ln(1-x)+8$.

**Vérification** : $F'(x)=-5\times\dfrac{-1}{1-x}=\dfrac{5}{1-x}=f(x)$, et $F(-2)=8-5\ln 3$.

### Pourquoi les autres réponses sont fausses
- **b)** Oubli du facteur $\dfrac{1}{a}=-1$ : la dérivée de $5\ln(1-x)$ est $-\dfrac{5}{1-x}$ ; la constante a ensuite été ajustée pour respecter $F(-2)$.
- **c)** La constante a été prise égale à la valeur imposée $8-5\ln 3$ : on obtient alors $F(-2)=8-10\ln 3$.
- **d)** Oubli du signe et de l'ajustement : cette fonction n'est pas une primitive de $f$ et vaut $8+5\ln 3$ en $-2$.

</details>

Avis : 

---

## 12. `cqc-congruences-faible-0` (séries C/E)

**Remarque du relecteur :** Le choix d) 13 est congru à 2 mais n'est pas un reste ; distracteur correct.

**Énoncé :**

On pose $N=10^{57}+3$. Quel est le reste de la division euclidienne de $N$ par $11$ ?

- a) $4$
- b) $10$
- c) $2$
- d) $13$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Lorsque la base d'une puissance est congrue à $-1$ modulo $m$, ses puissances successives valent alternativement $1$ (exposant pair) et $-1$ (exposant impair) modulo $m$ : il suffit de connaître la parité de l'exposant pour conclure.

### Corrigé
On remarque que $10\equiv-1\,[11]$. Donc, pour tout entier naturel $p$, $10^{p}\equiv(-1)^{p}\,[11]$.

Comme $57$ est impair, $10^{57}\equiv-1\equiv10\,[11]$.

Par suite, $N=10^{57}+3\equiv10+3=13\equiv2\,[11]$. Le reste est $2$.

Vérification sur un exposant impair plus petit : $10^{3}=1000=90\times11+10$, soit un reste de $10\equiv-1\,[11]$.

### Pourquoi les autres réponses sont fausses
- **a)** On a traité l'exposant comme pair : $10^{57}\equiv1$, d'où $1+3=4$.
- **b)** On a oublié d'ajouter $3$ : $10$ est le reste de $10^{57}$, pas celui de $N$.
- **d)** $13$ n'est pas réduit : un reste de division par $11$ est compris entre $0$ et $10$.

</details>

Avis : 

---

## 13. `cqc-congruences-moyenne-0` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Pour tout entier relatif $k$, on pose $a_k=5+40k$ et $b_k=1+9k$. Quelle affirmation sur $\mathrm{pgcd}(a_k,b_k)$ est exacte ?

- a) $\mathrm{pgcd}(a_k,b_k)=5$ si $k\equiv4\,[5]$, et $1$ sinon
- b) $\mathrm{pgcd}(a_k,b_k)=5$ si $k\equiv1\,[5]$, et $1$ sinon
- c) $\mathrm{pgcd}(a_k,b_k)=1$ pour tout entier $k$
- d) $\mathrm{pgcd}(a_k,b_k)=5$ pour tout entier $k$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour déterminer le pgcd de deux expressions dépendant d'un paramètre entier, on cherche une combinaison entière de ces deux expressions qui élimine le paramètre : si le résultat vaut $\pm1$, les deux expressions sont premières entre elles quel que soit le paramètre ; s'il reste un facteur commun évident, le pgcd se ramène à celui de ce facteur avec l'une des deux expressions.

### Corrigé
**Facteur $5$.** $a_k=5(1+8k)$. Posons $a'_k=1+8k$.

**Combinaison.** $9a'_k-8b_k=9+72k-8-72k=1$ : tout diviseur commun à $a'_k$ et $b_k$ divise $1$, donc $\mathrm{pgcd}(a'_k,b_k)=1$.

**Réduction.** Comme $a_k=5a'_k$ avec $a'_k$ premier avec $b_k$, on a $\mathrm{pgcd}(a_k,b_k)=\mathrm{pgcd}(5,b_k)$, qui vaut $5$ si $5\mid b_k$ et $1$ sinon.

**Condition.** $b_k\equiv1+4k\,[5]$, donc $5\mid b_k\iff4k\equiv-1\equiv4\,[5]$. Comme $4\times4\equiv1\,[5]$, en multipliant par $4$ : $k\equiv16\equiv1\,[5]$.

**Conclusion** : $\mathrm{pgcd}(a_k,b_k)=5$ si $k\equiv1\,[5]$, et $1$ sinon.

Vérification : pour $k=1$, $\mathrm{pgcd}(45,10)=5$ ; pour $k=2$, $\mathrm{pgcd}(85,19)=1$.

### Pourquoi les autres réponses sont fausses
- **a)** On s'est arrêté à $4k\equiv4\,[5]$ en lisant $k\equiv4$, sans simplifier par $4$ ; or pour $k=4$, $b_4=37$ n'est pas divisible par $5$.
- **c)** On a conclu de $\mathrm{pgcd}(a'_k,b_k)=1$ que $a_k$ et $b_k$ sont premiers entre eux, en oubliant le facteur $5$ de $a_k$ ; contre-exemple $k=1$.
- **d)** $5$ divise toujours $a_k$, mais pas toujours $b_k$ : pour $k=0$, $b_0=1$.

</details>

Avis : 

---

## 14. `cqc-croissances-comparees-elevee-5` (séries A/C/D/E/TI)

**Remarque du relecteur :** LIMITE : pour la série A, les croissances comparées x^n e^{-x} sont à la limite haute du programme.

**Énoncé :**

Soit $m$ la fonction définie sur $\mathbb{R}$ par $m(x)=\dfrac{e^x-2x^3}{e^x+5x^2}$.

Quelle est la limite de $m(x)$ quand $x$ tend vers $+\infty$ ?

- a) $-\infty$
- b) $-\dfrac{2}{5}$
- c) $1$
- d) $0$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Croissances comparées : pour tout entier naturel $n$, $\displaystyle\lim_{x\to+\infty}x^ne^{-x}=0$. Lorsqu'une expression mêle une exponentielle et des puissances de $x$ **ajoutées** au numérateur et au dénominateur, on factorise par le terme dominant $e^x$ pour se ramener à des produits de la forme $x^ne^{-x}$.

### Corrigé
Pour tout $x$, $e^x\neq0$ ; on factorise $e^x$ au numérateur et au dénominateur :
$$m(x)=\frac{e^x\left(1-2x^3e^{-x}\right)}{e^x\left(1+5x^2e^{-x}\right)}=\frac{1-2x^3e^{-x}}{1+5x^2e^{-x}}.$$
Par croissances comparées, $\displaystyle\lim_{x\to+\infty}x^3e^{-x}=0$ et $\displaystyle\lim_{x\to+\infty}x^2e^{-x}=0$. Le numérateur tend vers $1$ et le dénominateur vers $1$, donc
$$\lim_{x\to+\infty}m(x)=1.$$

### Pourquoi les autres réponses sont fausses
- **a)** On a gardé les termes polynomiaux comme s'ils dominaient : $\dfrac{-2x^3}{5x^2}=-\dfrac{2x}{5}\to-\infty$ ; c'est l'exponentielle qui l'emporte.
- **b)** On a fait le quotient des coefficients des puissances de $x$, $\dfrac{-2}{5}$, en ignorant $e^x$.
- **d)** On a cru que $e^x$ rendait le quotient nul, alors qu'il est présent au numérateur et au dénominateur.

</details>

Avis : 

---

## 15. `cqc-croissances-comparees-moyenne-2` (séries A/C/D/E/TI)

**Énoncé :**

Soit $h$ la fonction définie sur $\mathbb{R}$ par $h(x)=(2x^2-5x)e^{-x}$.

Que peut-on dire de $h(x)$ quand $x$ tend vers $+\infty$ ?

- a) $h(x)$ tend vers $+\infty$
- b) $h(x)$ tend vers $0$
- c) $h(x)$ n'a pas de limite, car on obtient une forme indéterminée
- d) $h(x)$ tend vers $2$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Croissances comparées : pour tout entier naturel $n$, $\displaystyle\lim_{x\to+\infty}x^ne^{-x}=0$. Quand une expression est une somme de termes de cette forme, on applique le théorème à chaque terme, puis on utilise la limite d'une somme.

### Corrigé
Le produit $(2x^2-5x)e^{-x}$ conduit à la forme indéterminée « $+\infty\times0$ ». On développe :
$$h(x)=2x^2e^{-x}-5xe^{-x}.$$
Par croissances comparées, $\displaystyle\lim_{x\to+\infty}x^2e^{-x}=0$ et $\displaystyle\lim_{x\to+\infty}xe^{-x}=0$. Donc
$$\lim_{x\to+\infty}h(x)=2\times0-5\times0=0.$$

### Pourquoi les autres réponses sont fausses
- **a)** On a cru que le polynôme l'emportait sur $e^{-x}$ ; c'est l'inverse : l'exponentielle l'emporte sur toute puissance de $x$.
- **c)** Une forme indéterminée ne signifie pas que la limite n'existe pas : il faut lever l'indétermination.
- **d)** On a retenu le coefficient dominant $2$ du polynôme, sans tenir compte de $e^{-x}$.

</details>

Avis : 

---

## 16. `cqc-discriminant-complexe-moyenne-0` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Quel est l'ensemble des solutions dans $\mathbb{C}$ de l'équation $$z^2-(3+i)z+4+3i=0\ ?$$

- a) $\{2-i\,;\,1+2i\}$
- b) $\{2+i\,;\,1-2i\}$
- c) $\{-2+i\,;\,-1-2i\}$
- d) $\{2+2i\,;\,1-i\}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour résoudre $az^2+bz+c=0$ à coefficients complexes, on calcule $\Delta=b^2-4ac$. Si $\Delta$ n'est pas un réel, on pose $\delta=x+iy$ (avec $x,y\in\mathbb R$) et on identifie parties réelle et imaginaire de $\delta^2=\Delta$ : $x^2-y^2=\mathrm{Re}(\Delta)$ et $2xy=\mathrm{Im}(\Delta)$. Les solutions sont ensuite $z=\dfrac{-b\pm\delta}{2a}$.

### Corrigé

Ici $a=1$, $b=-(3+i)$, $c=4+3i$.

$$\Delta=b^2-4ac=(3+i)^2-4(4+3i)=(9+6i-1)-16-12i=-8-6i.$$

On cherche $\delta=x+iy$ tel que $\delta^2=-8-6i$ :
$$x^2-y^2=-8, \qquad 2xy=-6 \ \Rightarrow\ xy=-3 \ \Rightarrow\ y=-\frac3x.$$

$x^2-\dfrac9{x^2}=-8 \Rightarrow x^4+8x^2-9=0$. Avec $X=x^2$ : $X^2+8X-9=(X+9)(X-1)=0$, donc $X=1$. Ainsi $x=1$, $y=-3$, $\delta=1-3i$.

Vérification : $(1-3i)^2=1-6i-9=-8-6i=\Delta$.

$$z=\frac{(3+i)\pm(1-3i)}2.$$

$z_1=\dfrac{4-2i}2=2-i$ et $z_2=\dfrac{2+4i}2=1+2i$.

Vérification : $z_1+z_2=3+i$ et $z_1z_2=(2-i)(1+2i)=2+4i-i-2i^2=4+3i$, conformément aux relations entre coefficients et racines.

$\mathcal S=\{2-i\,;\,1+2i\}$.

### Pourquoi les autres réponses sont fausses

- **b)** Ce sont les conjugués des solutions : l'équation n'est pas à coefficients réels, donc le conjugué d'une solution n'est pas solution (leur produit vaut $4-3i$, pas $4+3i$).
- **c)** Erreur de signe sur $b$ : on a calculé $\dfrac{b\pm\delta}{2}$ au lieu de $\dfrac{-b\pm\delta}{2}$, ce qui donne les opposés des solutions.
- **d)** Erreur de signe sur la racine carrée : $\delta=1+3i$ ne vérifie pas $\delta^2=\Delta$ (car $(1+3i)^2=-8+6i$).

</details>

Avis : 

---

## 17. `cqc-discriminant-complexe-moyenne-1` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère, dans $\mathbb C$, l'équation $(E) : z^3-z^2+(7+6i)z+9+6i=0$, dont $z_0=-1$ est une solution.

Quel est l'ensemble des solutions de $(E)$ dans $\mathbb C$ ?

- a) $\{-1\,;\,2+3i\,;\,-3i\}$
- b) $\{-1\,;\,-2+3i\,;\,-3i\}$
- c) $\{-1\,;\,4-6i\,;\,6i\}$
- d) $\{-1\,;\,2-3i\,;\,3i\}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'une équation polynomiale de degré 3 admet une racine évidente (ou vérifiée) $z_0$, on la factorise par $(z-z_0)$ : en développant $(z-z_0)(z^2+bz+c)$ et en identifiant terme à terme avec le polynôme de départ, on obtient les coefficients du facteur du second degré restant. On résout ensuite cette équation du second degré en calculant son discriminant complexe $\Delta$, puis une racine carrée $\delta$ de $\Delta$ par identification si $\Delta$ n'est pas réel.

### Corrigé

**1) Vérification.** Pour $z_0=-1$ :
$$(-1)^3-(-1)^2+(7+6i)(-1)+9+6i=-1-1-7-6i+9+6i=0.$$
$z_0=-1$ est bien solution de $(E)$.

**2) Factorisation.** On écrit $(E)=(z+1)(z^2+bz+c)$. En développant :
$$(z+1)(z^2+bz+c)=z^3+(b+1)z^2+(c+b)z+c.$$
Par identification avec $z^3-z^2+(7+6i)z+9+6i$ : $c=9+6i$ et $b+1=-1$, donc $b=-2$ (on vérifie sur le coefficient de $z$ : $c+b=9+6i-2=7+6i$, conforme).

Le facteur restant est $z^2-2z+9+6i=0$.

$$\Delta=(-2)^2-4(9+6i)=4-36-24i=-32-24i.$$

On cherche $\delta=x+iy$ tel que $\delta^2=-32-24i$ :
$$x^2-y^2=-32, \qquad 2xy=-24 \ \Rightarrow\ xy=-12 \ \Rightarrow\ y=-\frac{12}x.$$
$x^2-\dfrac{144}{x^2}=-32 \Rightarrow x^4+32x^2-144=0$. Avec $X=x^2$ : $X^2+32X-144=0$, $X=\dfrac{-32\pm\sqrt{1024+576}}2=\dfrac{-32\pm40}2$, donc $X=4$ (on rejette $X=-36$). Ainsi $x=2$, $y=-6$, $\delta=2-6i$.

Vérification : $(2-6i)^2=4-24i-36=-32-24i=\Delta$.

$$z=\frac{2\pm(2-6i)}2.$$

$z=2-3i$ ou $z=3i$.

**Bilan.** $\mathcal S=\{-1\,;\,2-3i\,;\,3i\}$. Vérification globale : la somme des trois racines vaut $-1+2-3i+3i=1$, égale à l'opposé du coefficient de $z^2$ dans $(E)$, soit $-(-1)=1$.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur la racine carrée : $\delta=2+6i$ ne vérifie pas $\delta^2=\Delta$ (car $(2+6i)^2=-32+24i$).
- **b)** Erreur de signe sur $b$ : on a calculé $\dfrac{-2\pm\delta}{2}$ au lieu de $\dfrac{2\pm\delta}{2}$ pour le facteur $z^2-2z+9+6i$.
- **c)** Oubli de la division par $2a=2$ dans la formule $z=\dfrac{-b\pm\delta}{2a}$.

</details>

Avis : 

---

## 18. `cqc-droite-de-mayer-moyenne-1` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Une vendeuse de tissus au marché central a relevé, pour 7 clientes reçues dans la matinée, la quantité de tissu achetée en mètres ($x$) et le montant total payé en milliers de FCFA ($y$), déjà triés par quantité croissante :

| Tissu acheté en mètres ($x$) | 1 | 3 | 5 | 7 | 9 | 11 | 13 |
|---|---|---|---|---|---|---|---|
| Montant payé en milliers de FCFA ($y$) | 9 | 13 | 19 | 27 | 30 | 39 | 45 |

La droite de Mayer associée à cette série a été établie en plaçant dans le premier sous-groupe les 4 plus petites abscisses et dans le second les 3 restantes ; son équation est $y = 3x + 5$.

Une cliente affirme : « la droite de Mayer ne passe jamais exactement par le point moyen de l'ensemble de la série ; seule la droite de régression par moindres carrés a cette propriété ».

Parmi les affirmations suivantes, laquelle est exacte ?

- a) $G(7;26)$ appartient à la droite de Mayer, et c'est vrai pour toute droite de Mayer : la cliente a tort.
- b) $G(7;26)$ appartient à la droite de Mayer, mais c'est une coïncidence propre à cet exemple : en général, la cliente a raison.
- c) Le point moyen est $G(7{,}5;27{,}5)$ ; il appartient à la droite de Mayer : la cliente a tort.
- d) Le point moyen est $G(7;27)$ ; il n'appartient pas à la droite de Mayer : la cliente a raison.

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Le point moyen $G$ d'une série complète se calcule comme la moyenne de TOUTES les abscisses de la série et la moyenne de TOUTES les ordonnées correspondantes, sans tenir compte du découpage en sous-groupes utilisé pour obtenir $G_1$ et $G_2$. Pour vérifier qu'un point appartient à une droite donnée, il suffit de substituer son abscisse dans l'équation et de comparer l'ordonnée obtenue à celle du point.

### Corrigé
**Calcul de $G$** : $\bar x=\dfrac{1+3+5+7+9+11+13}{7}=\dfrac{49}{7}=7$ ; $\bar y=\dfrac{9+13+19+27+30+39+45}{7}=\dfrac{182}{7}=26$. Donc $G(7;26)$.

**Vérification sur la droite donnée** : en $x=7$, $y=3\times7+5=26$. Le point $G(7;26)$ appartient bien à la droite de Mayer.

**La cliente a tort, et ce n'est pas une coïncidence.** Si le premier sous-groupe a un effectif $n_1$ et le second un effectif $n_2$ (ici $n_1=4$ et $n_2=3$), on a $\bar x=\dfrac{n_1\bar x_1+n_2\bar x_2}{n_1+n_2}$ et $\bar y=\dfrac{n_1\bar y_1+n_2\bar y_2}{n_1+n_2}$ : le point $G$ est le barycentre de $G_1$ et $G_2$ affectés des effectifs $n_1$ et $n_2$. Un barycentre de deux points est toujours sur la droite qui les relie : la droite de Mayer $(G_1G_2)$ passe donc TOUJOURS par le point moyen $G$, comme la droite de régression par moindres carrés.

Ici $G_1(4;17)$ et $G_2(11;38)$, et l'on vérifie que $\dfrac{4\times4+3\times11}{7}=7$ et $\dfrac{4\times17+3\times38}{7}=26$.

### Pourquoi les autres réponses sont fausses

- **b)** Le calcul est juste, mais la conclusion est fausse : l'appartenance de $G$ à la droite de Mayer est une propriété générale (barycentre de $G_1$ et $G_2$), pas un hasard propre à cet exemple.
- **c)** Le point $(7{,}5;27{,}5)$ est le milieu de $[G_1G_2]$, pas le point moyen : comme les sous-groupes n'ont pas le même effectif, $G$ n'est pas le milieu de $[G_1G_2]$.
- **d)** $27$ est la médiane des montants, pas leur moyenne ($\bar y=26$) : le point $(7;27)$ n'est pas le point moyen.

</details>

Avis : 

---

## 19. `cqc-derivee-d-un-produit-moyenne-1` (séries C/D/E/TI)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère la fonction $f$ définie sur $\mathbb{R}$ par $f(x) = e^{3x}\sin x$.

Laquelle des fonctions suivantes est une primitive de $f$ sur $\mathbb{R}$ ?

- a) $x\mapsto\dfrac{1}{10}e^{3x}(3\sin x+\cos x)$
- b) $x\mapsto\dfrac{1}{8}e^{3x}(3\sin x-\cos x)$
- c) $x\mapsto\dfrac{1}{10}e^{3x}(3\sin x-\cos x)$
- d) $x\mapsto-\dfrac{1}{3}e^{3x}\cos x$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour savoir si une fonction $F$ est une primitive de $f$, on calcule $F'$ (ici à l'aide de la dérivée d'un produit $(uv)'=u'v+uv'$) et on vérifie que l'expression obtenue est égale à $f$. On ne peut pas obtenir une primitive d'un produit en multipliant les primitives de chaque facteur.

### Corrigé

Pour $F(x)=\dfrac{1}{10}e^{3x}(3\sin x-\cos x)$, on pose $u(x)=\dfrac{1}{10}e^{3x}$ et $v(x)=3\sin x - \cos x$, dérivables sur $\mathbb{R}$, avec $u'(x)=\dfrac{3}{10}e^{3x}$ et $v'(x)=3\cos x+\sin x$.

$$F'(x) = u'(x)v(x)+u(x)v'(x) = \frac{3}{10}e^{3x}(3\sin x-\cos x) + \frac{1}{10}e^{3x}(3\cos x+\sin x)$$

En factorisant par $\dfrac{1}{10}e^{3x}$ :

$$F'(x) = \frac{1}{10}e^{3x}\big[9\sin x-3\cos x+3\cos x+\sin x\big] = \frac{1}{10}e^{3x}\times10\sin x = e^{3x}\sin x$$

On obtient $F'(x)=f(x)$ pour tout réel $x$ : $F$ est une primitive de $f$ sur $\mathbb{R}$.

### Pourquoi les autres réponses sont fausses

- **a)** Avec $+\cos x$, la dérivée vaut $\dfrac{1}{10}e^{3x}(8\sin x+6\cos x)$ : les termes en $\cos x$ ne s'éliminent plus.
- **b)** Le coefficient $\dfrac18$ vient d'un calcul $9-1$ au lieu de $9+1$ : la dérivée vaut alors $\dfrac{10}{8}e^{3x}\sin x$, pas $e^{3x}\sin x$.
- **d)** On a multiplié une primitive de $e^{3x}$ par une primitive de $\sin x$ : cette règle n'existe pas, et la dérivée de $-\dfrac13e^{3x}\cos x$ est $-e^{3x}\cos x+\dfrac13e^{3x}\sin x$.

</details>

Avis : 

---

## 20. `cqc-derivee-d-un-produit-moyenne-2` (séries A/C/D/E/TI)

**Énoncé :**

On considère la fonction $p$ définie sur $\mathbb{R}$ par $p(x) = (x^{2}-3x+2)e^{-x}$.

Quelle est l'expression de $p'(x)$ ?

- a) $p'(x)=(x^{2}-x-1)e^{-x}$
- b) $p'(x)=(-x^{2}-x-1)e^{-x}$
- c) $p'(x)=(-2x+3)e^{-x}$
- d) $p'(x)=(-x^{2}+5x-5)e^{-x}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour dériver un produit $u\times v$, on applique $(uv)'=u'v+uv'$ ; lorsque $v(x)=e^{-x}$, on a $v'(x)=-e^{-x}$. Une fois les deux termes obtenus, on peut les factoriser par le facteur exponentiel commun pour obtenir une écriture plus compacte.

### Corrigé

On pose $u(x)=x^{2}-3x+2$ et $v(x)=e^{-x}$, dérivables sur $\mathbb{R}$, avec $u'(x)=2x-3$ et $v'(x)=-e^{-x}$.

$$p'(x) = u'(x)v(x)+u(x)v'(x) = (2x-3)e^{-x} + (x^{2}-3x+2)\times(-e^{-x})$$

En factorisant par $e^{-x}$ :

$$p'(x) = e^{-x}\big[(2x-3)-(x^{2}-3x+2)\big] = e^{-x}\big[2x-3-x^{2}+3x-2\big] = e^{-x}(-x^{2}+5x-5)$$

On a donc $p'(x) = (-x^{2}+5x-5)e^{-x}$, soit $Q(x) = -x^{2}+5x-5$.

### Pourquoi les autres réponses sont fausses

- **a)** Oubli du signe de $v'(x)=-e^{-x}$ : on a ajouté $(x^2-3x+2)e^{-x}$ au lieu de le retrancher.
- **b)** Erreur de distributivité : le signe $-$ devant la parenthèse n'a été appliqué qu'au premier terme, ce qui donne $-x^2-3x+2$ au lieu de $-x^2+3x-2$.
- **c)** On a appliqué la règle fausse $(uv)'=u'v'$, soit $(2x-3)\times(-e^{-x})$.

</details>

Avis : 

---

## 21. `cqc-derivee-du-logarithme-bac-a-elevee-2` (séries A)

**Remarque du relecteur :** LIMITE : dérivée de ln(u) avec u=x²+1 en série A ; à confirmer au programme A.

**Énoncé :**

On considère la fonction $f$ définie pour tout réel $x$ par
$$f(x)=\ln(x^2+1)-x.$$

Quel est le sens de variation de $f$ sur $\mathbb{R}$ ?

- a) $f$ est décroissante sur $]-\infty;0]$ et croissante sur $[0;+\infty[$
- b) $f$ est décroissante sur $\mathbb{R}$
- c) $f$ est croissante sur $]-\infty;1]$ et décroissante sur $[1;+\infty[$
- d) $f$ est croissante sur $\mathbb{R}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour une fonction $u$ dérivable et strictement positive, $(\ln u)'=\dfrac{u'}{u}$ ; avec $u(x)=x^2+1$, on a $u'(x)=2x$. Le signe de la dérivée donne ensuite le sens de variation : une dérivée négative, ou nulle en un seul point sans changer de signe, impose une fonction décroissante.

### Corrigé
Pour tout réel $x$, $x^2+1\ge1>0$ : $f$ est définie et dérivable sur $\mathbb{R}$, et
$$f'(x)=\dfrac{2x}{x^2+1}-1=\dfrac{2x-(x^2+1)}{x^2+1}=\dfrac{-x^2+2x-1}{x^2+1}=\dfrac{-(x-1)^2}{x^2+1}.$$

Le dénominateur est strictement positif et $(x-1)^2\ge0$, donc $f'(x)\le0$ pour tout réel $x$, avec $f'(x)=0$ uniquement pour $x=1$, sans changement de signe. La fonction $f$ est donc décroissante sur $\mathbb{R}$.

Contrôle : $f(0)=0$, $f(1)=\ln2-1\approx-0{,}31$ et $f(2)=\ln5-2\approx-0{,}39$ (valeurs arrondies au centième) ; on a bien $f(0)>f(1)>f(2)$.

### Pourquoi les autres réponses sont fausses

- **a)** Oubli du terme $-1$ dans la dérivée : on a étudié le signe de $\dfrac{2x}{x^2+1}$, qui est celui de $x$.
- **c)** On a cru que l'annulation de $f'$ en $1$ signale un maximum : $f'$ s'annule en $1$ sans changer de signe, il n'y a pas d'extremum.
- **d)** Erreur de signe : $-(x-1)^2$ a été lu comme $(x-1)^2$, d'où une dérivée positive.

</details>

Avis : 

---

## 22. `cqc-derivee-exponentielle-moyenne-2` (séries A)

**Remarque du relecteur :** LIMITE : en série A, la dérivée de e^{u(x)} avec u polynôme du second degré est à la limite haute du programme.

**Énoncé :**

On considère la fonction $f$ définie sur $\mathbb{R}$ par $f(x) = e^{-x^2+2x+3}$.

Quelle est la valeur exacte du maximum de $f$ sur $\mathbb{R}$ ?

- a) $e^{3}$
- b) $1$
- c) $e^{6}$
- d) $e^{4}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour une fonction $f(x) = e^{u(x)}$, $f'(x) = u'(x)e^{u(x)}$ et, comme $e^{u(x)} > 0$ pour tout $x$, le signe de $f'$ est celui de $u'$. Quand $u$ est un polynôme du second degré, $u'$ est affine : son signe change une seule fois, ce qui donne à $f$ un unique extremum.

### Corrigé
**1. Dérivée.**
On pose $u(x) = -x^2 + 2x + 3$, donc $u'(x) = -2x + 2$.

$$f'(x) = u'(x)e^{u(x)} = (-2x+2)e^{-x^2+2x+3}$$

**2. Signe de $f'(x)$.**
Comme $e^{-x^2+2x+3} > 0$ pour tout $x$, le signe de $f'(x)$ est celui de $-2x + 2 = -2(x-1)$.

- $-2x+2 > 0 \iff x < 1$
- $-2x+2 = 0 \iff x = 1$
- $-2x+2 < 0 \iff x > 1$

Donc $f'(x) > 0$ sur $]-\infty,1[$, $f'(1)=0$, et $f'(x) < 0$ sur $]1,+\infty[$.

**3. Variations et maximum.**
$f$ est donc strictement croissante sur $]-\infty, 1]$, puis strictement décroissante sur $[1, +\infty[$. Elle admet donc un maximum en $x=1$.

$$f(1) = e^{-1^2+2\times 1+3} = e^{-1+2+3} = e^{4}$$

Le maximum de $f$ sur $\mathbb{R}$ vaut donc $e^4$.

### Pourquoi les autres réponses sont fausses

- **a)** $e^3$ est la valeur $f(0)$ : on a confondu le maximum avec l'image de $0$, sans étudier les variations.
- **b)** Erreur de signe dans la résolution de $-2x+2=0$, qui a donné $x=-1$ : or $f(-1)=e^{0}=1$ n'est pas le maximum.
- **c)** Erreur de priorité : $-1^2$ a été calculé comme $+1$, d'où $e^{1+2+3}=e^6$.

</details>

Avis : 

---

## 23. `cqc-ellipse-moyenne-0` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Le plan complexe est muni d'un repère orthonormé $(O;\vec u,\vec v)$. On note $(H)$ l'ensemble des points du plan dont l'affixe $z$ vérifie :
$$8z\bar z-(z+\bar z)^2+4(z+\bar z)-12=0$$
L'ensemble $(H)$ est une ellipse. Quelles sont les équations de ses directrices ?

- a) $x=-1+\sqrt2$ et $x=-1-\sqrt2$
- b) $x=-1+2\sqrt2$ et $x=-1-2\sqrt2$
- c) $x=2\sqrt2$ et $x=-2\sqrt2$
- d) $x=1+2\sqrt2$ et $x=1-2\sqrt2$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour une relation liant $z$ et $\bar z$, on pose $z=x+iy$ afin d'utiliser $z\bar z=x^2+y^2$ et $z+\bar z=2x$ : la relation se transforme alors en une équation cartésienne en $x,y$, que l'on réduit ensuite par complétion du carré pour obtenir la forme canonique $\dfrac{(x-\alpha)^2}{a^2}+\dfrac{(y-\beta)^2}{b^2}=1$.

### Corrigé
Avec $z=x+iy$, on a $z\bar z=x^2+y^2$ et $z+\bar z=2x$, donc $(z+\bar z)^2=4x^2$. La relation devient :
$8(x^2+y^2)-4x^2+4(2x)-12=0$
$8x^2+8y^2-4x^2+8x-12=0$
$4x^2+8y^2+8x-12=0$
En divisant par $4$ : $x^2+2y^2+2x-3=0$.
Or $x^2+2x=(x+1)^2-1$, donc :
$(x+1)^2-1+2y^2-3=0$
$(x+1)^2+2y^2=4$
En divisant par $4$ :
$$\dfrac{(x+1)^2}{4}+\dfrac{y^2}{2}=1$$
On a $a^2=4$ et $b^2=2$ avec $a=2>b=\sqrt2$, donc $(H)$ est une ellipse de centre $\Omega(-1;0)$, de grand axe horizontal.
$c=\sqrt{a^2-b^2}=\sqrt{4-2}=\sqrt2$.
Les foyers sont $F(-1+\sqrt2;0)$ et $F'(-1-\sqrt2;0)$.
L'excentricité vaut $e=\dfrac{c}{a}=\dfrac{\sqrt2}{2}$.
Les directrices ont pour équations $x=-1\pm\dfrac{a^2}{c}=-1\pm\dfrac{4}{\sqrt2}=-1\pm2\sqrt2$.

### Pourquoi les autres réponses sont fausses

- **a)** Ce sont les abscisses des foyers $-1\pm c=-1\pm\sqrt2$ : on a confondu foyers et directrices.
- **c)** Oubli du centre : $x=\pm\dfrac{a^2}{c}$ n'est valable que pour une ellipse centrée en $O$, alors qu'ici le centre est $\Omega(-1;0)$.
- **d)** Erreur de signe sur le centre : $(x+1)^2$ correspond à un centre d'abscisse $-1$, pas $1$.

</details>

Avis : 

---

## 24. `cqc-ellipse-moyenne-1` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans le plan muni d'un repère orthonormé, on considère le point $F(1;0)$ et la droite $(\Delta)$ d'équation $x=4$. On note $(C)$ l'ensemble des points $M$ du plan vérifiant :
$$MF=\dfrac{1}{2}\,d(M,(\Delta))$$
Quelle est une équation cartésienne de $(C)$ ?

- a) $\dfrac{x^2}{4}-\dfrac{y^2}{3}=1$
- b) $\dfrac{(x+2)^2}{18}+\dfrac{y^2}{9}=1$
- c) $\dfrac{x^2}{4}+\dfrac{y^2}{3}=1$
- d) $\dfrac{x^2}{3}+\dfrac{y^2}{4}=1$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
L'ensemble des points $M$ tels que $MF=e\cdot d(M,(\Delta))$, où $F$ est un point fixe, $(\Delta)$ une droite fixe et $e$ un réel constant, est une conique de foyer $F$, de directrice associée $(\Delta)$ et d'excentricité $e$ : c'est une ellipse lorsque $0<e<1$.

### Corrigé
Pour $M(x;y)$ : $MF=\sqrt{(x-1)^2+y^2}$ et $d(M,(\Delta))=|x-4|$. La condition $MF=\dfrac{1}{2}d(M,(\Delta))$ s'écrit, après élévation au carré (les deux membres étant positifs) :
$(x-1)^2+y^2=\dfrac{1}{4}(x-4)^2$
$4(x-1)^2+4y^2=(x-4)^2$
$4x^2-8x+4+4y^2=x^2-8x+16$
$3x^2+4y^2-12=0$
$3x^2+4y^2=12$
En divisant par $12$ :
$$\dfrac{x^2}{4}+\dfrac{y^2}{3}=1$$
On a $a^2=4$, $b^2=3$, donc $a=2>b=\sqrt3$ : $(C)$ est une ellipse de centre $O$, de grand axe horizontal.
$c=\sqrt{a^2-b^2}=\sqrt{4-3}=1$, ce qui redonne bien $F(1;0)$ comme foyer, l'autre foyer étant $F'(-1;0)$.
L'excentricité vaut $e=\dfrac{c}{a}=\dfrac{1}{2}$, conforme à la donnée de l'énoncé.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe en regroupant les termes : $4y^2$ est passé avec un signe $-$, ce qui donne l'équation d'une hyperbole, incompatible avec $e=\dfrac12<1$.
- **b)** Oubli d'élever au carré le coefficient $\dfrac12$ : on a écrit $(x-1)^2+y^2=\dfrac12(x-4)^2$ au lieu de $\dfrac14(x-4)^2$.
- **d)** Les dénominateurs ont été inversés : le grand axe serait alors vertical et les foyers sur l'axe des ordonnées, ce qui contredit le foyer $F(1;0)$.

</details>

Avis : 

---

## 25. `cqc-ellipse-moyenne-2` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère l'ensemble $(F)$ des points $M(x;y)$ du plan vérifiant :
$$2x^2+5y^2-12x-10y+13=0$$
L'ensemble $(F)$ est une ellipse. Quelle est son excentricité ?

- a) $e=\dfrac{\sqrt{15}}{5}$
- b) $e=\dfrac{3}{5}$
- c) $e=\dfrac{\sqrt{10}}{5}$
- d) $e=\dfrac{\sqrt{35}}{5}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Après réduction d'une équation développée $Ax^2+By^2+Cx+Dy+E=0$ ($A,B>0$, $A\neq B$) à la forme canonique $\dfrac{(x-\alpha)^2}{a^2}+\dfrac{(y-\beta)^2}{b^2}=1$ avec $a>b$, l'excentricité de l'ellipse obtenue vaut $e=c/a$ où $c=\sqrt{a^2-b^2}$.

### Corrigé
$2x^2-12x+5y^2-10y+13=0$
$2(x^2-6x)+5(y^2-2y)=-13$
Or $x^2-6x=(x-3)^2-9$ et $y^2-2y=(y-1)^2-1$, donc :
$2[(x-3)^2-9]+5[(y-1)^2-1]=-13$
$2(x-3)^2-18+5(y-1)^2-5=-13$
$2(x-3)^2+5(y-1)^2=10$
En divisant par $10$ :
$$\dfrac{(x-3)^2}{5}+\dfrac{(y-1)^2}{2}=1$$
On a $a^2=5$ et $b^2=2$, avec $a=\sqrt5>b=\sqrt2$, donc $(F)$ est bien une ellipse (centre $\Omega(3;1)$, grand axe horizontal).
$c=\sqrt{a^2-b^2}=\sqrt{5-2}=\sqrt3$.
L'excentricité vaut $e=\dfrac{c}{a}=\dfrac{\sqrt3}{\sqrt5}=\dfrac{\sqrt{15}}{5}$.

### Pourquoi les autres réponses sont fausses

- **b)** On a calculé $\dfrac{c^2}{a^2}=\dfrac35$, c'est-à-dire le carré de l'excentricité.
- **c)** On a calculé $\dfrac{b}{a}=\dfrac{\sqrt2}{\sqrt5}$ au lieu de $\dfrac{c}{a}$.
- **d)** On a utilisé $c=\sqrt{a^2+b^2}=\sqrt7$, relation valable pour une hyperbole : on obtient d'ailleurs un nombre supérieur à $1$, impossible pour une ellipse.

</details>

Avis : 

---

## 26. `cqc-excentricite-moyenne-1` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans le plan muni d'un repère orthonormé $(O,I,J)$ (unité : $10^6$ km), la trajectoire d'une comète lors de son survol du Soleil est modélisée par une conique $(C')$ de foyer $F(5\,;\,0)$, de directrice associée $(\Delta'): x=\dfrac{9}{5}$, et d'excentricité $e=\dfrac{5}{3}$.

Quelle est une équation cartésienne de $(C')$, et quelle est sa nature ?

- a) $\dfrac{x^2}{9}+\dfrac{y^2}{16}=1$ ; c'est une ellipse
- b) $\dfrac{x^2}{9}-\dfrac{y^2}{16}=1$ ; c'est une hyperbole
- c) $\dfrac{x^2}{16}-\dfrac{y^2}{9}=1$ ; c'est une hyperbole
- d) $\dfrac{x^2}{3}-\dfrac{y^2}{4}=1$ ; c'est une hyperbole

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Une conique de foyer $F$, de directrice $(\Delta')$ et d'excentricité $e$ est l'ensemble des points $M$ du plan vérifiant $MF=e\times d(M,(\Delta'))$. On établit son équation cartésienne en élevant au carré la relation $MF=e\times d(M,(\Delta'))$, puis en développant. La valeur de $e$ obtenue permet ensuite de conclure sur la nature de la courbe : $e>1$ signe une hyperbole.

### Corrigé

**1.** Soit $M(x\,;\,y)$. On a $MF=\sqrt{(x-5)^2+y^2}$ et $d(M,(\Delta'))=\left|x-\dfrac{9}{5}\right|$.

La relation $MF=e\times d(M,(\Delta'))$ s'écrit :
$$\sqrt{(x-5)^2+y^2}=\frac{5}{3}\left|x-\frac{9}{5}\right|$$

En élevant au carré :
$$(x-5)^2+y^2=\frac{25}{9}\left(x-\frac{9}{5}\right)^2$$

Membre de gauche :
$$x^2-10x+25+y^2$$

Membre de droite :
$$\frac{25}{9}\left(x^2-\frac{18}{5}x+\frac{81}{25}\right)=\frac{25}{9}x^2-10x+9$$

L'équation devient :
$$x^2-10x+25+y^2=\frac{25}{9}x^2-10x+9$$

Les termes en $-10x$ se simplifient :
$$x^2+25+y^2=\frac{25}{9}x^2+9$$
$$x^2-\frac{25}{9}x^2+y^2=-16$$
$$-\frac{16}{9}x^2+y^2=-16$$

En multipliant par $-1$ puis en divisant par $16$ :
$$\frac{x^2}{9}-\frac{y^2}{16}=1$$

**2.** Puisque $e=\dfrac{5}{3}\approx1{,}67$ vérifie $e>1$, $(C')$ est une hyperbole (ce que confirme la forme obtenue, avec un terme en $y^2$ négatif). Contrairement à une trajectoire elliptique fermée ($e<1$), une trajectoire hyperbolique n'est pas une courbe fermée : la comète s'éloigne indéfiniment après son passage au voisinage du Soleil, sans jamais revenir sur la même orbite.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe en regroupant les termes : on obtient l'équation d'une ellipse, incompatible avec $e=\dfrac53>1$.
- **c)** Les dénominateurs ont été inversés : avec $a^2=16$ et $c=5$, on aurait $e=\dfrac54$, et non $\dfrac53$.
- **d)** On a écrit $a=3$ et $b=4$ aux dénominateurs au lieu de $a^2=9$ et $b^2=16$.

</details>

Avis : 

---

## 27. `cqc-excentricite-moyenne-2` (séries C/E)

**Remarque du relecteur :** VOCABULAIRE : contexte physiquement inexact, le centre de la Terre doit être un foyer de l'orbite elliptique et non son centre ; reformuler le repère (origine en un foyer) ou retirer le satellite.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Un architecte modélise le contour d'une salle de forme elliptique par la conique $(C)$ d'équation, dans un repère orthonormé $(O,I,J)$ centré sur le centre de la salle (unité : $10$ m) :
$$5x^2+9y^2=45$$

Il utilise ensuite un second repère orthonormé $(\Omega,I,J)$, de même unité et de mêmes vecteurs que $(O,I,J)$, dont l'origine $\Omega$ a pour coordonnées $(1\,;\,-2)$ dans $(O,I,J)$ : un point de coordonnées $(x\,;\,y)$ dans $(O,I,J)$ a pour coordonnées $(X\,;\,Y)=(x-1\,;\,y+2)$ dans $(\Omega,I,J)$.

Quelles sont, dans le repère $(\Omega,I,J)$, les coordonnées du centre et des foyers de $(C)$ ?

- a) Centre $(1\,;\,-2)$, foyers $(3\,;\,-2)$ et $(-1\,;\,-2)$
- b) Centre $(-1\,;\,2)$, foyers $(-1\,;\,4)$ et $(-1\,;\,0)$
- c) Centre $(-1\,;\,2)$, foyers $(1\,;\,2)$ et $(-3\,;\,2)$
- d) Centre $(-1\,;\,2)$, foyers $(-1+\sqrt{14}\,;\,2)$ et $(-1-\sqrt{14}\,;\,2)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

L'excentricité $e=\dfrac{c}{a}$ d'une conique est un rapport de deux longueurs (distance centre-foyer sur demi-grand axe) : c'est une grandeur intrinsèque à la courbe, qui ne dépend pas du repère orthonormé choisi pour l'exprimer. Un changement d'origine (translation) déplace les coordonnées du centre et des foyers, mais conserve toutes les distances entre points, donc conserve $a$, $b$, $c$, et par conséquent $e$.

### Corrigé

**1.** On divise par $45$ : $\dfrac{x^2}{9}+\dfrac{y^2}{5}=1$, donc $a^2=9$ ($a=3$) et $b^2=5$ ($b=\sqrt5$).
$c^2=a^2-b^2=9-5=4$, donc $c=2$, et $e=\dfrac{c}{a}=\dfrac{2}{3}$.

**2.** Dans $(O,I,J)$ : le centre de $(C)$ est $O(0\,;\,0)$ et ses foyers sont $F(2\,;\,0)$ et $F'(-2\,;\,0)$ (les foyers sont sur l'axe des abscisses car $a>b$).

Dans $(\Omega,I,J)$, avec $X=x-1$ et $Y=y+2$ :
- centre : $(0-1\,;\,0+2)=(-1\,;\,2)$
- $F$ : $(2-1\,;\,0+2)=(1\,;\,2)$
- $F'$ : $(-2-1\,;\,0+2)=(-3\,;\,2)$

**3.** Les deux repères sont orthonormés et ont les mêmes vecteurs directeurs : le passage de l'un à l'autre est une translation, qui conserve toutes les distances. En particulier, la distance entre le centre et un foyer (c'est-à-dire $c$) et la longueur du demi-grand axe (c'est-à-dire $a$) sont inchangées, donc $e=\dfrac{c}{a}=\dfrac{2}{3}$ reste valable dans $(\Omega,I,J)$.

Vérification : dans $(\Omega,I,J)$, la distance entre le centre $(-1\,;\,2)$ et le foyer $F(1\,;\,2)$ vaut $\sqrt{(1-(-1))^2+(2-2)^2}=\sqrt{4}=2$, ce qui redonne bien $c=2$, identique à la valeur trouvée dans $(O,I,J)$.

### Pourquoi les autres réponses sont fausses

- **a)** La translation a été appliquée à l'envers : on a ajouté $1$ à l'abscisse et retranché $2$ à l'ordonnée, au lieu de l'inverse.
- **b)** Les foyers ont été placés sur l'axe vertical : comme $a^2=9>b^2=5$, le grand axe est horizontal et les foyers ont la même ordonnée que le centre.
- **d)** On a calculé $c=\sqrt{a^2+b^2}=\sqrt{14}$, relation valable pour une hyperbole, au lieu de $c=\sqrt{a^2-b^2}=2$.

</details>

Avis : 

---

## 28. `cqc-existence-moyenne-2` (séries C/D/E/TI)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Lequel des nombres complexes suivants vérifie $w^2 = 5 - 12i$ ?

- a) $w=3-2i$
- b) $w=3+2i$
- c) $w=2-3i$
- d) $w=-3-2i$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour démontrer l'existence d'une racine carrée d'un nombre complexe $Z = x+iy$, on pose $w = a+ib$ ($a,b$ réels) et on identifie les parties réelle et imaginaire de $w^2 = Z$, complétées par l'égalité des modules $|w|^2 = |Z|$. La résolution explicite du système obtenu fournit directement une solution, ce qui prouve l'existence par construction plutôt que par un argument théorique.

### Corrigé

On cherche $w = a+ib$ ($a,b \in \mathbb{R}$) tel que $w^2 = 5 - 12i$.

Comme $w^2 = a^2 - b^2 + 2abi$, l'identification des parties réelle et imaginaire donne :
$$a^2 - b^2 = 5 \quad \text{et} \quad 2ab = -12, \text{ soit } ab = -6$$

On ajoute l'égalité des modules : $|w|^2 = |w^2| = |5-12i| = \sqrt{5^2+12^2} = \sqrt{25+144} = \sqrt{169} = 13$, donc $a^2+b^2 = 13$.

En additionnant $a^2-b^2=5$ et $a^2+b^2=13$ : $2a^2 = 18$, donc $a^2 = 9$, soit $a = 3$ ou $a = -3$.
En soustrayant les deux mêmes égalités : $2b^2 = 8$, donc $b^2 = 4$, soit $b = 2$ ou $b = -2$.

Comme $ab = -6 < 0$, $a$ et $b$ sont de signes opposés : on retient le couple $a=3, b=-2$ (le couple opposé $a=-3,b=2$ convient également).

On pose donc $w = 3 - 2i$. Vérification :
$$w^2 = (3-2i)^2 = 9 - 12i + 4i^2 = 9 - 12i - 4 = 5 - 12i$$
On a ainsi exhibé explicitement un nombre complexe $w = 3-2i$ vérifiant $w^2 = 5-12i$ : un tel nombre existe donc bien.

### Pourquoi les autres réponses sont fausses

- **b)** Oubli de la condition $ab=-6<0$ : avec $a=3$ et $b=2$, on obtient $(3+2i)^2=5+12i$.
- **c)** Les parties réelle et imaginaire ont été échangées : $(2-3i)^2=4-12i-9=-5-12i$.
- **d)** $a$ et $b$ sont de même signe : $(-3-2i)^2=5+12i$.

</details>

Avis : 

---

## 29. `cqc-exponentielle-faible-0` (séries A/C/D/TI)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère la fonction $g$ définie par $g(x) = \dfrac{5}{3e^{2x}-27}$.

Quel est l'ensemble de définition $D_g$ de la fonction $g$ ?

- a) $D_g=\mathbb{R}$
- b) $D_g=\mathbb{R}\setminus\{\ln9\}$
- c) $D_g=\mathbb{R}\setminus\left\{\dfrac{\ln27}{2}\right\}$
- d) $D_g=\mathbb{R}\setminus\{\ln3\}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Une fonction définie par un quotient n'est pas définie aux valeurs de $x$ qui annulent son dénominateur. Quand ce dénominateur contient un terme exponentiel, on résout l'équation $e^{\alpha x} = k$ (avec $k>0$) en utilisant l'équivalence $e^{u}=k \iff u=\ln k$, valable parce que $e^u$ est toujours strictement positif.

### Corrigé

$g$ est définie pour tout réel $x$ tel que $3e^{2x}-27 \neq 0$.

$$3e^{2x}-27=0 \iff e^{2x}=\dfrac{27}{3}=9 \iff 2x=\ln 9 \iff x=\dfrac{\ln 9}{2}$$

Comme $9=3^2$, on a $\ln 9 = 2\ln 3$, donc $x = \dfrac{2\ln3}{2}=\ln3$.

**L'ensemble de définition de $g$ est $D_g = \mathbb{R}\setminus\{\ln3\}$.**

### Pourquoi les autres réponses sont fausses

- **a)** On a cru que le dénominateur ne s'annule jamais parce qu'une exponentielle est strictement positive : c'est $e^{2x}$ qui est positif, pas $3e^{2x}-27$.
- **b)** Oubli de la division par $2$ : $2x=\ln9$ donne $x=\dfrac{\ln9}{2}$, pas $x=\ln9$.
- **c)** Oubli de la division par $3$ : on a résolu $e^{2x}=27$ au lieu de $e^{2x}=9$.

</details>

Avis : 

---

## 30. `cqc-factorisation-par-difference-de-carres-moyenne-1` (séries A)

**Énoncé :**

Quel est l'ensemble des solutions dans $\mathbb R$ de l'équation
$$(2x-5)^2=(x+1)^2\ ?$$

- a) $\mathcal S=\{6\}$
- b) $\mathcal S=\left\{\dfrac43\,;\,4\right\}$
- c) $\mathcal S=\left\{\dfrac43\,;\,6\right\}$
- d) $\mathcal S=\left\{-6\,;\,-\dfrac43\right\}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Une équation de la forme $E_1^2=E_2^2$ ne doit pas être résolue en développant chaque carré : on la ramène directement à $E_1^2-E_2^2=0$, une différence de deux carrés que l'on factorise avec $a^2-b^2=(a-b)(a+b)$, en prenant $a=E_1$ et $b=E_2$. On obtient alors un produit de deux facteurs du premier degré, chacun beaucoup plus simple à annuler qu'une équation avec des carrés.

### Corrigé

L'équation $(2x-5)^2=(x+1)^2$ équivaut à :
$$(2x-5)^2-(x+1)^2=0.$$

En factorisant avec $a=2x-5$ et $b=x+1$ :
$$\big[(2x-5)-(x+1)\big]\big[(2x-5)+(x+1)\big]=0,$$
$$(x-6)(3x-4)=0.$$

Un produit de facteurs est nul si et seulement si l'un des facteurs est nul :
$$x-6=0 \ \text{ou}\ 3x-4=0 \Longleftrightarrow x=6 \ \text{ou}\ x=\dfrac43.$$

Vérification : pour $x=6$, $(2\times6-5)^2=7^2=49$ et $(6+1)^2=49$. Pour $x=\dfrac43$, $\left(2\times\dfrac43-5\right)^2=\left(-\dfrac73\right)^2=\dfrac{49}{9}$ et $\left(\dfrac43+1\right)^2=\left(\dfrac73\right)^2=\dfrac{49}{9}$.

$$\mathcal S=\left\{\dfrac43\,;\,6\right\}.$$

### Pourquoi les autres réponses sont fausses

- **a)** On a « simplifié » les carrés en écrivant $2x-5=x+1$ : on perd la possibilité $2x-5=-(x+1)$.
- **b)** Erreur de signe sur la parenthèse : $(2x-5)-(x+1)$ a été développé en $x-4$ au lieu de $x-6$.
- **d)** Erreur de signe dans les deux facteurs, qui donne les opposés des solutions.

</details>

Avis : 

---

## 31. `cqc-fonction-exponentielle-moyenne-1` (séries C/D/E/TI)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $g$ la fonction définie sur $\mathbb{R}$ par $g(x) = x \times 3^{x}$.

Quelle est l'expression de la dérivée $g'(x)$ ?

- a) $3^{x}(1+x)$
- b) $3^{x}(1+x\ln3)$
- c) $3^{x}\ln3$
- d) $3^{x}(x+\ln3)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour dériver un produit de deux fonctions dérivables $u$ et $v$, on utilise $(uv)'=u'v+uv'$. Lorsque $v(x)=a^{x}$ avec $a>0$, on écrit d'abord $a^{x}=e^{x\ln a}$ pour obtenir $v'(x) = \ln a \times a^{x}$.

### Corrigé

On pose $u(x)=x$ et $v(x)=3^{x}$, dérivables sur $\mathbb{R}$, avec $u'(x)=1$ et, en écrivant $3^{x}=e^{x\ln3}$, $v'(x) = \ln3\times3^{x}$.

$$g'(x) = u'(x)v(x)+u(x)v'(x) = 1\times3^{x} + x\times\ln3\times3^{x}$$

En factorisant par $3^{x}$ :

$$g'(x) = 3^{x}\big(1+x\ln3\big)$$

**On a donc $g'(x) = 3^{x}(1+x\ln3)$.**

### Pourquoi les autres réponses sont fausses

- **a)** On a dérivé $3^{x}$ comme si c'était $e^{x}$, en oubliant le facteur $\ln3$.
- **c)** On a multiplié les dérivées des deux facteurs ($1\times\ln3\times3^{x}$) au lieu d'appliquer $(uv)'=u'v+uv'$.
- **d)** Le facteur $\ln3$ a été placé sur le mauvais terme : il appartient à $uv'$, pas à $u'v$.

</details>

Avis : 

---

## 32. `cqc-fonction-exponentielle-moyenne-2` (séries A/C/D/E/TI)

**Remarque du relecteur :** VOCABULAIRE : « signal résiduel après un choc électrique appliqué à un circuit » est un contexte peu réaliste ; préférer par exemple « intensité du courant dans un circuit après fermeture de l'interrupteur ».

**Énoncé :**

Dans un circuit RLC série fonctionnant en régime critique, on ferme l'interrupteur à l'instant $t=0$. L'intensité $I(t)$ du courant (en milliampères), mesurée $t$ secondes après la fermeture, est modélisée par :
$$I(t) = 4t\,e^{-2t}, \quad t\geq0$$

Quelle est l'intensité maximale atteinte par le courant, et à quel instant est-elle atteinte ?

- a) $\dfrac{4}{e^{2}}$ mA, à l'instant $t=1$ s
- b) $\dfrac{2}{e^{2}}$ mA, à l'instant $t=\dfrac12$ s
- c) $\dfrac{4}{e}$ mA, à l'instant $t=\dfrac12$ s
- d) $\dfrac{2}{e}$ mA, à l'instant $t=\dfrac12$ s

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour dériver un produit de la forme $t\mapsto \lambda t\, e^{\mu t}$, on applique $(uv)'=u'v+uv'$ avec $u(t)=\lambda t$ et $v(t)=e^{\mu t}$ (donc $v'(t)=\mu e^{\mu t}$), puis on factorise le résultat par le facteur exponentiel, toujours strictement positif, pour en étudier le signe et en déduire les variations.

### Corrigé

**Dérivée.** On pose $u(t)=4t$ et $v(t)=e^{-2t}$, avec $u'(t)=4$ et $v'(t)=-2e^{-2t}$.

$$I'(t) = 4e^{-2t} + 4t\times(-2)e^{-2t} = 4e^{-2t}(1-2t)$$

**Signe et variations.** Pour tout $t\geq0$, $4e^{-2t}>0$ : le signe de $I'(t)$ est celui de $1-2t$. Donc $I'(t)>0$ sur $\left[0,\dfrac12\right[$, $I'\!\left(\dfrac12\right)=0$ et $I'(t)<0$ sur $\left]\dfrac12,+\infty\right[$ : $I$ est croissante sur $\left[0,\dfrac12\right]$ puis décroissante sur $\left[\dfrac12,+\infty\right[$.

**Maximum.** $I$ admet donc un maximum en $t=\dfrac12$, qui vaut :

$$I\!\left(\dfrac12\right) = 4\times\dfrac12\times e^{-2\times\frac12} = 2e^{-1} = \dfrac{2}{e}$$

**L'intensité maximale est $\dfrac{2}{e}$ mA, atteinte à l'instant $t=\dfrac12$ seconde.**

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié le facteur $-2$ en dérivant $e^{-2t}$ : on obtient $I'(t)=4e^{-2t}(1-t)$, donc un maximum (faux) en $t=1$.
- **b)** L'instant est juste, mais $e^{-2\times\frac12}$ a été calculé comme $e^{-2}$ au lieu de $e^{-1}$.
- **c)** L'instant est juste, mais on a oublié le facteur $t=\dfrac12$ dans le calcul de $I\!\left(\dfrac12\right)$.

</details>

Avis : 

---

## 33. `cqc-fonction-valeur-absolue-bac-a-elevee-2` (séries A)

**Remarque du relecteur :** Le tableau de signes de g n'est pas utile à la résolution, sans être trompeur.

**Énoncé :**

On considère le trinôme $g(x)=x^2-2x-3$ (pour tout réel $x$). Le signe de $g(x)$ est résumé dans le tableau suivant :

| $x$ | $-\infty$ | | $-1$ | | $3$ | | $+\infty$ |
|---|---|---|---|---|---|---|---|
| signe de $g(x)$ | | $+$ | $0$ | $-$ | $0$ | $+$ | |

Quel est l'ensemble des solutions dans $\mathbb{R}$ de l'équation $|g(x)|=5$ ?

- a) $\{-4\,;\,2\}$
- b) $\{4\}$
- c) $\{-2\,;\,4\}$
- d) $\{1-\sqrt3\,;\,1+\sqrt3\}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
On a $|u|=u$ là où $u\ge 0$ et $|u|=-u$ là où $u\le 0$ : le tableau de signes de $g$ indique donc, intervalle par intervalle, quelle expression remplace $|g(x)|$. L'équation est ensuite résolue dans chaque intervalle, et seules les solutions qui appartiennent à l'intervalle étudié sont conservées.

### Corrigé
**Expression sans valeur absolue.** D'après le tableau, $|g(x)|=x^2-2x-3$ sur $]-\infty\,;\,-1]$ et sur $[3\,;\,+\infty[$, et $|g(x)|=-x^2+2x+3$ sur $[-1\,;\,3]$.

**Dans $[-1\,;\,3]$.** $-x^2+2x+3=5\iff x^2-2x+2=0$. Le discriminant vaut $\Delta=4-8=-4<0$ : aucune solution.

**Hors de $]-1\,;\,3[$.** $x^2-2x-3=5\iff x^2-2x-8=0$. Le discriminant vaut $\Delta=4+32=36$, d'où $x=\dfrac{2-6}{2}=-2$ ou $x=\dfrac{2+6}{2}=4$. Comme $-2\in\,]-\infty\,;\,-1]$ et $4\in[3\,;\,+\infty[$, les deux valeurs conviennent.

**L'ensemble des solutions est $\{-2\,;\,4\}$.**

Vérification : $g(-2)=4+4-3=5$ et $g(4)=16-8-3=5$. Par ailleurs, sur $[-1\,;\,3]$, $|g(x)|=4-(x-1)^2\le 4<5$ : la valeur $5$ n'y est jamais atteinte.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe dans la formule des racines : $\dfrac{-2\pm6}{2}$ au lieu de $\dfrac{2\pm6}{2}$.
- **b)** La solution $-2$ a été rejetée à tort : elle appartient bien à $]-\infty\,;\,-1]$.
- **d)** En passant $5$ dans le premier membre, on a écrit $x^2-2x-2=0$ au lieu de $x^2-2x-8=0$.

</details>

Avis : 

---

## 34. `cqc-fonction-valeur-absolue-bac-a-moyenne-1` (séries A)

**Remarque du relecteur :** Le distracteur b) piège l'oubli de la condition de domaine, c'est voulu.

**Énoncé :**

À tout réel $x$, on associe le nombre

$$f(x)=|x+3|-2x.$$

Quel est l'ensemble des solutions dans $\mathbb{R}$ de l'équation $f(x)=4$ ?

- a) $\{-1\}$
- b) $\left\{-\dfrac73\,;\,-1\right\}$
- c) $\left\{-\dfrac73\right\}$
- d) $\{1\}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour une expression $u$, on a $|u|=u$ lorsque $u\ge 0$ et $|u|=-u$ lorsque $u<0$. Ici $u=x+3$ change de signe en $x=-3$ : on réécrit $f$ sur chacun des deux intervalles, on résout l'équation dans chacun, puis on ne garde que les solutions situées dans l'intervalle correspondant.

### Corrigé
**Écriture sans valeur absolue.**

- Si $x\ge -3$, alors $|x+3|=x+3$, d'où $f(x)=3-x$.
- Si $x<-3$, alors $|x+3|=-(x+3)$, d'où $f(x)=-3x-3$.

**Résolution de $f(x)=4$.**

- Cas $x\ge -3$ : $3-x=4\iff x=-1$. Comme $-1\ge -3$, cette valeur est une solution.
- Cas $x<-3$ : $-3x-3=4\iff x=-\dfrac{7}{3}$. Or $-\dfrac{7}{3}\approx -2{,}33$ n'est pas strictement inférieur à $-3$ : cette valeur est rejetée.

**L'ensemble des solutions est $\{-1\}$.**

Vérification : $f(-1)=2+2=4$, tandis que $f\left(-\dfrac{7}{3}\right)=\dfrac{2}{3}+\dfrac{14}{3}=\dfrac{16}{3}\neq 4$.

### Pourquoi les autres réponses sont fausses

- **b)** On a oublié de vérifier que $-\dfrac73$ appartient à l'intervalle $x<-3$ : ce n'est pas le cas.
- **c)** On a gardé la valeur du mauvais cas et rejeté la bonne solution $-1$.
- **d)** Erreur de signe : $3-x=4$ donne $x=-1$, et non $x=1$ (d'ailleurs $f(1)=2$).

</details>

Avis : 

---

## 35. `cqc-forme-algebrique-d-un-quotient-moyenne-1` (séries D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On donne les nombres complexes $u=2-i$ et $v=-3+4i$. Quelle est la forme algébrique du nombre complexe $$V=\dfrac{u+v}{u-v}\ ?$$

- a) $-\dfrac45+\dfrac25i$
- b) $-\dfrac25+\dfrac15i$
- c) $\dfrac15+\dfrac25i$
- d) $-2-i$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'un quotient fait intervenir une somme ou une différence de deux complexes au numérateur et/ou au dénominateur, on calcule d'abord entièrement cette somme ou cette différence sous forme algébrique, avant de multiplier par le conjugué du dénominateur obtenu.

### Corrigé

On calcule d'abord le numérateur et le dénominateur :
$$u+v=-1+3i, \qquad u-v=(2-i)-(-3+4i)=5-5i.$$

Le conjugué de $5-5i$ est $5+5i$, et $(5-5i)(5+5i)=5^2+5^2=50$.

$$V=\frac{(-1+3i)(5+5i)}{50}=\frac{-5-5i+15i+15i^2}{50}=\frac{-20+10i}{50}.$$

**D'où $V=-\dfrac25+\dfrac15i$.**

Vérification : $(5-5i)\left(-\dfrac25+\dfrac15i\right)=-2+i+2i-i^2=-1+3i=u+v$.

### Pourquoi les autres réponses sont fausses

- **a)** Le dénominateur $(5-5i)(5+5i)$ a été pris égal à $25$ au lieu de $5^2+5^2=50$.
- **c)** Le numérateur a été multiplié par $5-5i$ (le dénominateur lui-même) au lieu de son conjugué $5+5i$.
- **d)** Numérateur et dénominateur ont été inversés : c'est la forme algébrique de $\dfrac{u-v}{u+v}$.

</details>

Avis : 

---

## 36. `cqc-forme-algebrique-d-un-quotient-moyenne-2` (séries D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On donne les nombres complexes $z_1=2-3i$ et $z_2=\dfrac35+\dfrac45i$. Quelle est la forme algébrique du nombre complexe $$Z=\dfrac{z_1}{z_2}\ ?$$

- a) $\dfrac{18}5-\dfrac15i$
- b) $\dfrac{18}5-\dfrac{17}5i$
- c) $-\dfrac65-\dfrac{17}5i$
- d) $\dfrac{10}3-\dfrac{15}4i$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour écrire un quotient sous forme algébrique, on multiplie numérateur et dénominateur par le conjugué du dénominateur. Lorsque le dénominateur $z_2=a+ib$ vérifie $a^2+b^2=1$ (son module vaut alors $1$), le produit $z_2\bar z_2$ vaut $1$ : il suffit de multiplier le numérateur par $\bar z_2$.

### Corrigé

On remarque que $\left(\dfrac35\right)^2+\left(\dfrac45\right)^2=\dfrac9{25}+\dfrac{16}{25}=1$, donc $z_2\bar z_2=1$.

Le conjugué de $z_2$ est $\bar z_2=\dfrac35-\dfrac45i$, donc :
$$Z=z_1\bar z_2=(2-3i)\left(\frac35-\frac45i\right)=\frac65-\frac85i-\frac95i+\frac{12}5i^2=\frac65-\frac{17}5i-\frac{12}5.$$

**D'où $Z=-\dfrac65-\dfrac{17}5i$.**

Vérification : $z_2\times Z=\left(-\dfrac{18}{25}+\dfrac{68}{25}\right)+\left(-\dfrac{51}{25}-\dfrac{24}{25}\right)i=2-3i=z_1$.

### Pourquoi les autres réponses sont fausses

- **a)** On a multiplié $z_1$ par $z_2$ au lieu de son conjugué $\bar z_2$.
- **b)** On a remplacé $i^2$ par $1$ au lieu de $-1$ : la partie réelle devient $\dfrac65+\dfrac{12}5$.
- **d)** On a divisé séparément les parties réelles et les parties imaginaires, ce qui n'est pas une règle de calcul valable.

</details>

Avis : 

---

## 37. `cqc-forme-indeterminee-bac-a-faible-0` (séries A)

**Énoncé :**

Quelle est la valeur de

$$\lim_{x\to+\infty}\dfrac{5x^3-2x+1}{1-4x^3}\ ?$$

- a) $-\dfrac54$
- b) $\dfrac54$
- c) $-\dfrac45$
- d) $1$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Le quotient de deux polynômes en $\pm\infty$ conduit à une forme indéterminée du type $\dfrac{\infty}{\infty}$. On la lève en factorisant, au numérateur et au dénominateur, la puissance de $x$ de plus haut degré, puis en simplifiant : les termes de la forme $\dfrac{1}{x^k}$ (avec $k\ge 1$) tendent alors vers $0$.

### Corrigé
Quand $x\to+\infty$, le numérateur tend vers $+\infty$ et le dénominateur vers $-\infty$ : forme indéterminée $\dfrac{\infty}{\infty}$.

Pour $x\neq 0$, on factorise $x^3$ en haut et en bas :

$$\frac{5x^3-2x+1}{1-4x^3}=\frac{5-\dfrac{2}{x^2}+\dfrac{1}{x^3}}{\dfrac{1}{x^3}-4}.$$

Le numérateur tend vers $5$ et le dénominateur vers $-4$ :

$$\lim_{x\to+\infty}\dfrac{5x^3-2x+1}{1-4x^3}=-\dfrac{5}{4}.$$

Vérification : pour $x=10\,000$, le quotient vaut environ $-1{,}2500000$.

### Pourquoi les autres réponses sont fausses

- **b)** Le signe du coefficient $-4$ du terme de plus haut degré du dénominateur a été oublié.
- **c)** On a fait le quotient des coefficients dans le mauvais ordre (dénominateur sur numérateur).
- **d)** On a fait le quotient des termes constants $\dfrac11$, ce qui donnerait la limite en $0$, pas en $+\infty$.

</details>

Avis : 

---

## 38. `cqc-imaginaire-pur-bac-ti-mat-elevee-2` (séries TI)

**Énoncé :**

Pour tout réel $m$, on pose $Z=\dfrac{m+i}{1+mi}$.

Quel est l'ensemble des réels $m$ pour lesquels $Z$ est un nombre réel ?

- a) $\{0\}$
- b) $\{-1\,;\,1\}$
- c) $\{1\}$
- d) $\{-1\,;\,0\,;\,1\}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Un nombre complexe $z$ est réel si et seulement si $\operatorname{Im}z=0$, et imaginaire pur si et seulement si $\operatorname{Re}z=0$. Pour lire ces parties, on écrit $z$ sous forme algébrique en multipliant numérateur et dénominateur par le conjugué du dénominateur.

### Corrigé
Le dénominateur $1+mi$ a une partie réelle égale à $1$ : il n'est jamais nul. On multiplie par le conjugué $1-mi$ ; le dénominateur devient $1+m^{2}$ et le numérateur

$$(m+i)(1-mi)=m-m^{2}i+i-mi^{2}=2m+(1-m^{2})i.$$

Donc $Z=\dfrac{2m}{1+m^{2}}+\dfrac{1-m^{2}}{1+m^{2}}\,i$.

$Z$ est réel si et seulement si $\dfrac{1-m^{2}}{1+m^{2}}=0$, soit $m^{2}=1$ (car $1+m^{2}>0$), donc $m=1$ ou $m=-1$.

**L'ensemble cherché est $\{-1\,;\,1\}$** (on obtient alors $Z=1$ pour $m=1$ et $Z=-1$ pour $m=-1$).

Vérification : pour $m=-1$, $Z=\dfrac{-1+i}{1-i}=-1$ ; pour $m=2$, $Z=\dfrac45-\dfrac35i$ n'est pas réel.

### Pourquoi les autres réponses sont fausses

- **a)** Confusion entre réel et imaginaire pur : pour $m=0$, $Z=i$ est imaginaire pur.
- **c)** On a oublié la solution négative de l'équation $m^{2}=1$.
- **d)** On a réuni les valeurs rendant $Z$ réel et celle rendant $Z$ imaginaire pur ; or $m=0$ donne $Z=i$, qui n'est pas réel.

</details>

Avis : 

---

## 39. `cqc-involution-moyenne-1` (séries C/E)

**Énoncé :**

Le plan vectoriel $E$ est muni d'une base $(\vec\imath,\vec\jmath)$. Pour tous réels $a$ et $b$, on note $g_{a,b}$ l'application linéaire de $E$ dans $E$ qui, au vecteur de coordonnées $(x\,;y)$, associe le vecteur de coordonnées $(ax+by\,;\,-ay)$.

Pour quels couples $(a\,;b)$ de réels $g_{a,b}$ est-elle une involution de $E$, c'est-à-dire vérifie $g_{a,b}\circ g_{a,b}=\mathrm{id}_E$ ?

- a) $(1\,;0)$ et $(-1\,;0)$ seulement
- b) $a=1$ et $b$ réel quelconque
- c) aucun couple
- d) $a\in\{-1\,;1\}$ et $b$ réel quelconque

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Une application $g$ est une involution si et seulement si $g\circ g=\mathrm{id}$. On calcule l'expression analytique de $g\circ g$ et on identifie ses coefficients à ceux de l'identité ; il faut ensuite lire avec soin quels paramètres restent libres.

### Corrigé
L'image par $g_{a,b}$ du vecteur de coordonnées $(ax+by\,;\,-ay)$ a pour coordonnées :
$$\big(a(ax+by)+b(-ay)\,;\,-a(-ay)\big)=\big(a^2x+(ab-ab)y\,;\,a^2y\big)=\big(a^2x\,;\,a^2y\big).$$

Donc $g_{a,b}\circ g_{a,b}=a^2\,\mathrm{id}_E$ : le paramètre $b$ disparaît.

$g_{a,b}\circ g_{a,b}=\mathrm{id}_E \iff a^2=1 \iff a=1 \text{ ou } a=-1$, quel que soit $b$.

**Les solutions sont tous les couples $(a\,;b)$ avec $a\in\{-1\,;1\}$ et $b$ réel quelconque.**

Contrôle : pour $(a\,;b)=(1\,;5)$, $g(x\,;y)=(x+5y\,;-y)$ et $g(x+5y\,;-y)=(x+5y-5y\,;\,y)=(x\,;y)$.

### Pourquoi les autres réponses sont fausses

- **a)** On a calculé le coefficient de $y$ dans la première coordonnée comme $ab+ab=2ab$ au lieu de $ab-ab=0$, d'où la condition parasite $b=0$.
- **b)** On a oublié la solution $a=-1$ de l'équation $a^2=1$.
- **c)** Erreur de signe : $-a\times(-ay)=a^2y$, et non $-a^2y$ ; l'équation $a^2=1$ a bien des solutions.

</details>

Avis : 

---

## 40. `cqc-inequation-exponentielle-moyenne-2` (séries A/C/E)

**Énoncé :**

Quel est l'ensemble des solutions dans $\mathbb{R}$ de l'inéquation
$$e^{2x}-3e^{x}-10\geqslant0\ ?$$

- a) $[5\,;\,+\infty[$
- b) $]-\infty\,;\,\ln5]$
- c) $]\ln5\,;\,+\infty[$
- d) $[\ln5\,;\,+\infty[$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour résoudre une inéquation combinant $e^{2x}$ et $e^{x}$, on pose $X=e^{x}>0$, ce qui ramène l'inéquation à une inéquation du second degré en $X$. Après avoir déterminé le signe du trinôme selon le sens de l'inégalité, on ne conserve que les valeurs de $X$ strictement positives avant de revenir à $x$ par $x=\ln X$, fonction strictement croissante qui conserve le sens des inégalités.

### Corrigé

On pose $X=e^{x}$, avec $X>0$. L'inéquation devient $X^2-3X-10\geqslant0$.

Le discriminant vaut $\Delta=9+40=49$, donc $X=\dfrac{3-7}{2}=-2$ ou $X=\dfrac{3+7}{2}=5$.

Comme $a=1>0$, le trinôme est positif ou nul à l'extérieur des racines, racines incluses : $X\leqslant-2$ ou $X\geqslant5$.

**Filtrage :** la condition $X=e^x>0$ élimine la branche $X\leqslant-2$. Il reste $X\geqslant5$, soit $x\geqslant\ln5$.

**Vérification :** pour $x=\ln5$, $25-15-10=0$, borne incluse ; pour $x=1$, $e^2-3e-10\approx-10{,}77<0$, valeur exclue.

**L'ensemble solution est $S=[\ln5\,;\,+\infty[$.**

### Pourquoi les autres réponses sont fausses

- **a)** Ce sont les solutions en $X$ : on a oublié de revenir à la variable $x$.
- **b)** On a pris l'intérieur des racines, alors que le trinôme ($a>0$) est positif à l'extérieur de ses racines.
- **c)** L'inégalité est large : la borne $\ln5$, qui annule le premier membre, doit être incluse.

</details>

Avis : 

---

## 41. `cqc-inequation-logarithmique-bac-a-elevee-2` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère la fonction $f$ définie pour tout $x>0$ par
$$f(x)=2(\ln x)^2-3\ln x-2.$$
Quel est l'ensemble des solutions de l'inéquation $f(x)<0$ ?

- a) $\left]-\dfrac12\,;2\right[$
- b) $\left]e^{-1/2}\,;e^{2}\right[$
- c) $\left]0\,;e^{-1/2}\right[\cup\left]e^{2}\,;+\infty\right[$
- d) $\left]e^{-2}\,;e^{1/2}\right[$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Une inéquation où $x$ n'intervient qu'à travers $\ln x$ se ramène, par le changement $t=\ln x$, à une inéquation polynomiale en $t$ ; on la résout, puis on revient à $x$ grâce à la croissance de l'exponentielle : $a<\ln x<b\iff e^{a}<x<e^{b}$.

### Corrigé
$\ln x$ n'est défini que pour $x>0$, donc on résout dans $]0\,;+\infty[$. Avec $t=\ln x$ :
$$f(x)<0\iff 2t^2-3t-2<0.$$

Pour le trinôme $2t^2-3t-2$, le discriminant vaut $\Delta=9+16=25$, soit $\sqrt{\Delta}=5$ ; les racines sont
$$t_1=\dfrac{3-5}{4}=-\dfrac12\qquad\text{et}\qquad t_2=\dfrac{3+5}{4}=2.$$
Le coefficient de $t^2$ est positif : le trinôme est strictement négatif entre ses racines. Donc $-\dfrac12<t<2$.

On revient à $x$ : $-\dfrac12<\ln x<2\iff e^{-1/2}<x<e^{2}$. Ces bornes sont strictement positives, donc compatibles avec le domaine :
$$S=\left]e^{-1/2}\,;e^{2}\right[.$$

Vérification : $f(1)=-2<0$ avec $e^{-1/2}<1<e^{2}$ ; $f(10)\approx2\times(2{,}303)^2-3\times2{,}303-2\approx1{,}70>0$ avec $10>e^{2}\approx7{,}389$.

### Pourquoi les autres réponses sont fausses
- **a)** $\left]-\dfrac12\,;2\right[$ est l'ensemble des solutions en $t$ : on a oublié de revenir à $x$ par $x=e^{t}$.
- **c)** C'est l'ensemble où $f(x)>0$ : on a pris le signe du trinôme à l'extérieur des racines au lieu de l'intérieur.
- **d)** Les racines $-2$ et $\dfrac12$ sont celles de $2t^2+3t-2$ : erreur de signe sur $b$ dans la formule $\dfrac{-b\pm\sqrt{\Delta}}{2a}$.

</details>

Avis : 

---

## 42. `cqc-loi-binomiale-moyenne-3` (séries A/C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un jeu télévisé, un candidat doit répondre au hasard aux 4 dernières questions d'un quiz. Chaque question propose 5 réponses possibles, une seule étant correcte, et le candidat choisit sa réponse indépendamment d'une question à l'autre. On note $X$ le nombre de bonnes réponses données par le candidat parmi ces 4 questions.

Le gain final $G$ du candidat, en francs CFA, est donné par $G=2000X-500$ (chaque bonne réponse rapporte 2000 F, mais une mise initiale de 500 F est retenue quel que soit le résultat).

Quelle est la probabilité que le candidat reparte avec un gain strictement positif ?

- a) $0{,}5904$
- b) $0{,}4096$
- c) $0{,}9984$
- d) $0{,}8$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Répéter $n$ fois, de façon indépendante, une même épreuve à deux issues de probabilités $p$ et $1-p$ définit un schéma de Bernoulli. La probabilité de n'obtenir aucun succès est $(1-p)^{n}$, et celle d'obtenir au moins un succès s'obtient par l'événement contraire : $1-(1-p)^{n}$.

### Corrigé
Chaque question est une épreuve à deux issues : « bonne réponse » (probabilité $p=\dfrac15$) ou « mauvaise réponse » (probabilité $\dfrac45$), et les 4 questions sont traitées de façon indépendante. Ainsi $X$ prend ses valeurs dans $\{0\,;1\,;2\,;3\,;4\}$.

$G>0 \iff 2000X-500>0 \iff X>0{,}25 \iff X\geqslant1$ (car $X$ est entier).

L'événement contraire de « $X\geqslant1$ » est « $X=0$ » : les 4 réponses sont fausses, ce qui a pour probabilité $\left(\dfrac45\right)^{4}=\dfrac{256}{625}=0{,}4096$. Donc
$$P(G>0)=P(X\geqslant1)=1-0{,}4096=0{,}5904.$$

Le candidat a une probabilité de $0{,}5904$ (valeur exacte) de repartir avec un gain strictement positif, soit environ 59 % de chances.

### Pourquoi les autres réponses sont fausses
- **b)** $0{,}4096$ est la probabilité de n'avoir aucune bonne réponse : on a oublié de passer à l'événement contraire.
- **c)** $0{,}9984=1-\left(\dfrac15\right)^{4}$ : on a confondu la probabilité d'un échec avec celle d'un succès dans l'événement contraire.
- **d)** $0{,}8=4\times\dfrac15$ : on a additionné les probabilités de succès des 4 questions, comme si les événements étaient incompatibles.

</details>

Avis : 

---

## 43. `cqc-loi-binomiale-moyenne-4` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On lance $6$ fois de suite une pièce de monnaie parfaitement équilibrée, les lancers étant effectués indépendamment les uns des autres. On note $X$ le nombre de fois où l'on obtient « pile » parmi les $6$ lancers.

Quelle est la probabilité $P(X=2)$ d'obtenir exactement deux fois « pile » ?

- a) $\dfrac{1}{64}$
- b) $\dfrac{3}{32}$
- c) $\dfrac{15}{32}$
- d) $\dfrac{15}{64}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Répéter $n$ fois, de façon indépendante, une même épreuve à deux issues de probabilités $p$ et $1-p$ définit un schéma de Bernoulli ; le nombre de succès suit alors une loi binomiale $\mathcal B(n,p)$ avec $P(X=k)=\binom{n}{k}p^{k}(1-p)^{n-k}$.

### Corrigé
Chaque lancer est une épreuve à deux issues : « pile » (succès, probabilité $p=\dfrac12$, la pièce étant équilibrée) ou « face » (probabilité $\dfrac12$). Les $6$ lancers sont identiques et indépendants, donc $X\sim\mathcal B\left(6,\dfrac12\right)$.

Pour $n$ lancers, $P(X=2)=\binom{n}{2}\left(\dfrac12\right)^{2}\left(\dfrac12\right)^{n-2}=\dfrac{n(n-1)}{2}\times\dfrac{1}{2^{n}}=\dfrac{n(n-1)}{2^{n+1}}$.

Pour $n=6$ :
$$P(X=2)=\binom{6}{2}\left(\dfrac12\right)^{6}=15\times\dfrac{1}{64}=\dfrac{15}{64}\approx0{,}234.$$

Contrôle avec la formule littérale : $\dfrac{6\times5}{2^{7}}=\dfrac{30}{128}=\dfrac{15}{64}$.

### Pourquoi les autres réponses sont fausses
- **a)** $\dfrac{1}{64}$ est la probabilité d'UNE suite précise de lancers : on a oublié le nombre $\binom{6}{2}=15$ de positions possibles des deux « pile ».
- **b)** $\dfrac{3}{32}=\dfrac{6}{64}$ : on a remplacé $\binom{6}{2}$ par $6$.
- **c)** $\dfrac{15}{32}=\dfrac{30}{64}$ : on a pris $\binom{6}{2}=6\times5=30$ en oubliant de diviser par $2$.

</details>

Avis : 

---

## 44. `cqc-majoration-bac-ti-mat-elevee-2` (séries TI)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un modèle de saturation d'un capteur, le taux de réponse associé à une grandeur réelle $x$ vaut
$$f(x)=\dfrac{e^{x}}{e^{x}+2},$$
cette expression ayant un sens pour tout réel $x$. On note $f'$ la dérivée de $f$.

Laquelle des affirmations suivantes est vraie ?

- a) Pour tout réel $x$, $0<f'(x)\le\dfrac29$, avec égalité seulement en $x=0$.
- b) Pour tout réel $x$, $0<f'(x)\le\dfrac14$, avec égalité seulement en $x=\ln2$.
- c) Pour tout réel $x$, $0<f'(x)<\dfrac14$ : la valeur $\dfrac14$ n'est jamais atteinte.
- d) Pour tout réel $x$, $0<f'(x)\le\dfrac14$, avec égalité seulement en $x=2$.

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour établir une inégalité entre deux expressions, on étudie le signe de leur différence en la ramenant à un seul quotient dont le numérateur se factorise ou se réduit à un carré. L'égalité n'a lieu que lorsque ce carré est nul.

### Corrigé
On écrit $f=\dfrac uv$ avec $u(x)=e^{x}$ et $v(x)=e^{x}+2$, qui ne s'annule pas ; $u'(x)=v'(x)=e^{x}$. Donc
$$f'(x)=\dfrac{e^{x}\left(e^{x}+2\right)-e^{x}\times e^{x}}{\left(e^{x}+2\right)^{2}}=\dfrac{2e^{x}}{\left(e^{x}+2\right)^{2}}>0.$$

En réduisant au même dénominateur,
$$\dfrac14-f'(x)=\dfrac{\left(e^{x}+2\right)^{2}-8e^{x}}{4\left(e^{x}+2\right)^{2}}=\dfrac{\left(e^{x}-2\right)^{2}}{4\left(e^{x}+2\right)^{2}}\ge0,$$
car $\left(e^{x}+2\right)^{2}-8e^{x}=e^{2x}-4e^{x}+4=\left(e^{x}-2\right)^{2}$. Ainsi $0<f'(x)\le\dfrac14$ pour tout réel $x$, et l'égalité n'a lieu que si $e^{x}=2$, c'est-à-dire $x=\ln2$.

Contrôle : $f'(0)=\dfrac29\approx0{,}222$, $f'(\ln2)=\dfrac{4}{16}=\dfrac14$ et $f'(\ln3)=\dfrac{6}{25}=0{,}24$.

### Pourquoi les autres réponses sont fausses
- **a)** $f'(0)=\dfrac29$ n'est pas le maximum : $f'(\ln2)=\dfrac14>\dfrac29$. Calculer la dérivée en $0$ ne suffit pas à la majorer.
- **c)** La majoration par $\dfrac14$ est atteinte : en $x=\ln2$, $f'(\ln2)=\dfrac14$, l'inégalité n'est donc pas stricte.
- **d)** De $e^{x}=2$ on a déduit $x=2$ au lieu de $x=\ln2$ : en fait $f'(2)\approx0{,}17<\dfrac14$.

</details>

Avis : 

---

## 45. `cqc-majoration-geometrique-bac-ti-mat-elevee-2` (séries TI)

**Remarque du relecteur :** Le contexte (u0, alpha, inégalité de contraction) ne sert pas à répondre ; la question se réduit à résoudre 0,3^n < 10^-3.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Un logiciel de calibrage d'un capteur fournit des valeurs successives $u_0,u_1,u_2,\dots$ pour approcher une tension d'équilibre $\alpha$, exprimée en volts et comprise entre $1$ et $3$. On sait que $u_0=2$ et que l'inégalité
$$|u_{n+1}-\alpha|\le0{,}3\,|u_n-\alpha|$$
est vraie quel que soit l'entier naturel $n$. On admet que, pour tout entier naturel $n$, $|u_n-\alpha|\le(0{,}3)^{n}$.

On donne $\ln10\approx2{,}303$ et $\ln0{,}3\approx-1{,}204$. Quel est le plus petit entier $n_0$ tel que $(0{,}3)^{n_0}<10^{-3}$ ?

- a) $n_0=3$
- b) $n_0=4$
- c) $n_0=5$
- d) $n_0=6$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Si l'écart à $\alpha$ est multiplié au plus par un réel $k\in]0\,;1[$ à chaque étape, une récurrence donne $|u_n-\alpha|\le k^{n}|u_0-\alpha|$. Le rang d'une précision $10^{-p}$ se déduit de l'inéquation $k^{n}<10^{-p}$, résolue avec le logarithme en renversant l'inégalité puisque $\ln k<0$.

### Corrigé
De $1\le\alpha\le3$ on tire $|u_0-\alpha|=|2-\alpha|\le1$ ; une récurrence immédiate donne $|u_n-\alpha|\le(0{,}3)^{n}|u_0-\alpha|\le(0{,}3)^{n}$.

On résout :
$$(0{,}3)^{n}<10^{-3}\iff n\ln0{,}3<-3\ln10\iff n>\dfrac{3\ln10}{-\ln0{,}3}\approx\dfrac{6{,}909}{1{,}204}\approx5{,}74,$$
l'inégalité changeant de sens à la division par $\ln0{,}3<0$. Le plus petit entier convenable est $n_0=6$.

Contrôle direct : $(0{,}3)^{5}=0{,}00243>10^{-3}$ et $(0{,}3)^{6}=0{,}000729<10^{-3}$.

Interprétation : $|u_6-\alpha|\le(0{,}3)^{6}<10^{-3}$, donc $u_6$ est une valeur approchée de $\alpha$ à $10^{-3}$ volt près (rang garanti par la majoration).

### Pourquoi les autres réponses sont fausses
- **a)** On a écrit $\ln\left(10^{-3}\right)=-3$ en oubliant le facteur $\ln10$ : $n>\dfrac{3}{1{,}204}\approx2{,}49$ ; or $(0{,}3)^{3}=0{,}027>10^{-3}$.
- **b)** On a mal compté les zéros : $(0{,}3)^{4}=0{,}0081$ et non $0{,}00081$, donc $(0{,}3)^{4}>10^{-3}$.
- **c)** On a pris la partie entière de $5{,}74$ au lieu de l'entier suivant : $(0{,}3)^{5}=0{,}00243>10^{-3}$.

</details>

Avis : 

---

## 46. `cqc-module-bac-ti-mat-elevee-2` (séries TI)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

En électricité, l'impédance d'un dipôle en régime sinusoïdal est un nombre complexe $Z$ (en ohms) ; la tension efficace $U$ aux bornes du dipôle et l'intensité efficace $I$ qui le traverse vérifient $U=|Z|\,I$. Deux dipôles d'impédances $Z_1=5+12i$ et $Z_2=8-15i$ sont montés en dérivation sous la tension efficace $U=221$ V. L'impédance équivalente est $Z_p=\dfrac{Z_1Z_2}{Z_1+Z_2}$ et l'intensité efficace totale vaut $I=\dfrac{U}{|Z_p|}$.

Quelle est la valeur de $I$, arrondie à $0{,}01$ A près ?

- a) $13{,}34$ A
- b) $16{,}56$ A
- c) $30{,}00$ A
- d) $178{,}00$ A

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour des complexes $u$ et $v$ avec $v\neq0$ : $|uv|=|u|\,|v|$ et $\left|\dfrac{u}{v}\right|=\dfrac{|u|}{|v|}$. Pour une somme, il faut au contraire écrire d'abord $u+v$ sous forme algébrique, puis prendre le module $\sqrt{a^{2}+b^{2}}$ du résultat : en général $|u+v|\neq|u|+|v|$.

### Corrigé
$|Z_1|=\sqrt{25+144}=13$ et $|Z_2|=\sqrt{64+225}=17$, donc $|Z_1Z_2|=13\times17=221$.

$Z_1+Z_2=13-3i$, donc $|Z_1+Z_2|=\sqrt{169+9}=\sqrt{178}$. Par le module d'un quotient,
$$|Z_p|=\dfrac{221}{\sqrt{178}}\approx16{,}56\text{ ohms}.$$

Alors
$$I=\dfrac{U}{|Z_p|}=221\times\dfrac{\sqrt{178}}{221}=\sqrt{178}\approx13{,}34\text{ A (arrondi à }0{,}01\text{ près)}.$$

Contrôle : $Z_1Z_2=(5+12i)(8-15i)=220+21i$, de module $\sqrt{48\,841}=221$. On remarque que $I_1+I_2=\dfrac{221}{13}+\dfrac{221}{17}=30$ A est très différent de $I$ : les deux courants ne sont pas en phase.

### Pourquoi les autres réponses sont fausses
- **b)** $16{,}56$ est $|Z_p|$ en ohms : on a confondu l'impédance et l'intensité.
- **c)** $30$ A suppose $|Z_1+Z_2|=|Z_1|+|Z_2|=30$ : le module d'une somme n'est pas la somme des modules.
- **d)** $178$ A vient de l'oubli de la racine carrée dans $|13-3i|=\sqrt{178}$.

</details>

Avis : 

---

## 47. `cqc-monotonie-moyenne-0` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $h(x)=\dfrac{x^2+1}{x}$ définie sur $]0\,;+\infty[$. Laquelle des affirmations suivantes est vraie ?

- a) $h$ est décroissante sur $]0\,;1]$, croissante sur $[1\,;+\infty[$, et son minimum vaut $1$.
- b) $h$ est décroissante sur $]0\,;1]$, croissante sur $[1\,;+\infty[$, et son minimum vaut $2$.
- c) $h$ est croissante sur $]0\,;+\infty[$ et n'admet pas de minimum.
- d) $h$ est croissante sur $]0\,;1]$, décroissante sur $[1\,;+\infty[$, et son maximum vaut $2$.

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour un quotient $\dfrac{u}{v}$, $\left(\dfrac{u}{v}\right)'=\dfrac{u'v-uv'}{v^2}$ ; le dénominateur étant positif, le signe de la dérivée est celui du numérateur.

### Corrigé
$h'(x)=\dfrac{2x\cdot x-(x^2+1)\cdot 1}{x^2}=\dfrac{x^2-1}{x^2}=\dfrac{(x-1)(x+1)}{x^2}$.

Sur $]0\,;+\infty[$, $x+1>0$ et $x^2>0$, donc $h'(x)$ a le signe de $x-1$ : $h$ est décroissante sur $]0\,;1]$ et croissante sur $[1\,;+\infty[$.

Le minimum est $h(1)=\dfrac{1+1}{1}=2$, atteint en $x=1$.

### Pourquoi les autres réponses sont fausses
- **a)** Le minimum est atteint en $x=1$, mais sa valeur est $h(1)=2$ et non $1$ : on a confondu l'abscisse et la valeur du minimum.
- **c)** On a écrit le numérateur de la dérivée $u'v+uv'=3x^2+1>0$ : la formule du quotient comporte un signe moins.
- **d)** On a écrit le numérateur $uv'-u'v=1-x^2$ : signe inversé, d'où des variations à l'envers.

</details>

Avis : 

---

## 48. `cqc-monotonie-moyenne-1` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $f(x)=(2x-1)e^{-x}$ définie sur $\mathbb{R}$. On admet que $f$ admet un maximum sur $\mathbb{R}$. Quelle est la valeur exacte de ce maximum ?

- a) $2e^{-3/2}$
- b) $0$
- c) $-2e^{1/2}$
- d) $2e^{3/2}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour un produit, $(uv)'=u'v+uv'$, et la dérivée de $e^{-x}$ est $-e^{-x}$ ; comme $e^{-x}>0$, on factorise par $e^{-x}$ et le signe de la dérivée est celui du facteur restant.

### Corrigé
$f'(x)=2e^{-x}+(2x-1)(-e^{-x})=e^{-x}(2-2x+1)=(3-2x)e^{-x}$.

Comme $e^{-x}>0$, $f'(x)$ a le signe de $3-2x$ : positive pour $x<\dfrac32$, négative ensuite. $f$ est croissante sur $\left]-\infty\,;\dfrac32\right]$ et décroissante sur $\left[\dfrac32\,;+\infty\right[$.

Son maximum est $f\!\left(\dfrac32\right)=(3-1)e^{-3/2}=2e^{-3/2}$.

### Pourquoi les autres réponses sont fausses
- **b)** En développant $-(2x-1)$ en $-2x-1$, on obtient $f'(x)=(1-2x)e^{-x}$, qui s'annule en $\dfrac12$, et $f\!\left(\dfrac12\right)=0$.
- **c)** En prenant $e^{-x}$ comme dérivée de $e^{-x}$, on obtient $f'(x)=(2x+1)e^{-x}$, qui s'annule en $-\dfrac12$, et $f\!\left(-\dfrac12\right)=-2e^{1/2}$.
- **d)** L'abscisse $\dfrac32$ est juste, mais on a oublié le signe moins de l'exposant : $e^{-3/2}$ et non $e^{3/2}$.

</details>

Avis : 

---

## 49. `cqc-monotonie-moyenne-2` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $f(x)=x-2\ln x$ définie sur $]0\,;+\infty[$. Quelle est la valeur du minimum de $f$ sur $]0\,;+\infty[$ ?

- a) $1$
- b) $2-2\ln2$
- c) $\dfrac12+2\ln2$
- d) $2-\ln2$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
On étudie le signe de $f'$ pour obtenir les variations ; si le minimum d'une fonction est strictement positif, la fonction est strictement positive partout.

### Corrigé
$f'(x)=1-\dfrac2x=\dfrac{x-2}{x}$. Sur $]0\,;+\infty[$, $x>0$ : $f'$ a le signe de $x-2$.

$f$ est décroissante sur $]0\,;2]$ et croissante sur $[2\,;+\infty[$ ; son minimum est $f(2)=2-2\ln 2=2(1-\ln 2)$.

Comme $\ln 2\approx 0{,}69<1$, ce minimum est strictement positif : $f(x)>0$ pour tout $x>0$.

### Pourquoi les autres réponses sont fausses
- **a)** $f(1)=1$ : on a supposé, sans étudier $f'$, que le minimum est atteint en $1$ (là où $\ln x$ s'annule) ; or $f(2)\approx0{,}61<1$.
- **c)** On a résolu $\dfrac2x=1$ en $x=\dfrac12$ au lieu de $x=2$ : $f\!\left(\dfrac12\right)=\dfrac12+2\ln2$ n'est pas le minimum.
- **d)** L'abscisse $2$ est juste, mais on a oublié le coefficient $2$ devant $\ln x$ en calculant $f(2)$.

</details>

Avis : 

---

## 50. `cqc-monotonie-d-une-suite-moyenne-0` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Pour tout entier naturel $n\geq1$, on pose $u_n=\dfrac{1\times3\times5\times\cdots\times(2n-1)}{2\times4\times6\times\cdots\times(2n)}$ (le numérateur est le produit des $n$ premiers entiers impairs, le dénominateur le produit des $n$ premiers entiers pairs). Ainsi $u_1=\dfrac12$ et $u_2=\dfrac{1\times3}{2\times4}=\dfrac38$.

Laquelle des affirmations suivantes est vraie pour tout entier $n\geq1$ ?

- a) $\dfrac{u_{n+1}}{u_n}=\dfrac{2n+2}{2n+1}$, donc $(u_n)$ est strictement croissante.
- b) $\dfrac{u_{n+1}}{u_n}=\dfrac{2n-1}{2n}$, donc $(u_n)$ est strictement décroissante.
- c) $\dfrac{u_{n+1}}{u_n}=\dfrac{2n+1}{2n+2}$, donc $(u_n)$ est strictement décroissante.
- d) $\dfrac{u_{n+1}}{u_n}=\dfrac{2n+1}{2n+3}$, donc $(u_n)$ est strictement décroissante.

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour une suite à termes strictement positifs définie comme un produit de $n$ facteurs, passer de $u_n$ à $u_{n+1}$ revient à multiplier par le facteur supplémentaire introduit par le rang $n+1$ : cela donne directement le rapport $\dfrac{u_{n+1}}{u_n}$, qu'il suffit de comparer à $1$.

### Corrigé
Chaque facteur est un entier strictement positif, donc $u_n>0$ pour tout $n\geq1$.

En passant de $u_n$ à $u_{n+1}$, le numérateur gagne le facteur impair suivant, $2(n+1)-1=2n+1$, et le dénominateur le facteur pair suivant, $2(n+1)=2n+2$ :
$$\dfrac{u_{n+1}}{u_n}=\dfrac{2n+1}{2n+2}.$$

Comme $0<2n+1<2n+2$, ce rapport est strictement inférieur à $1$ ; avec $u_n>0$, on obtient $u_{n+1}<u_n$ : la suite est strictement décroissante.

Vérification : $u_1=0{,}5$, $u_2=0{,}375$, $u_3=\dfrac{15}{48}=0{,}3125$, et $\dfrac{u_2}{u_1}=0{,}75=\dfrac{3}{4}$.

### Pourquoi les autres réponses sont fausses
- **a)** On a inversé le rapport : $\dfrac{2n+2}{2n+1}$ est $\dfrac{u_n}{u_{n+1}}$, d'où une conclusion de croissance fausse.
- **b)** $\dfrac{2n-1}{2n}$ est le dernier facteur de $u_n$, pas le facteur ajouté au rang $n+1$ : pour $n=1$ il donnerait $\dfrac{u_2}{u_1}=\dfrac12$ au lieu de $\dfrac34$.
- **d)** On a pris $2n+3$ comme pair suivant : le facteur pair ajouté est $2(n+1)=2n+2$.

</details>

Avis : 

---

## 51. `cqc-monotonie-d-une-suite-moyenne-1` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Pour tout entier naturel $n\geq1$, on pose $u_n=\displaystyle\int_n^{n+1}\dfrac{dx}{x}$. Laquelle des affirmations suivantes est vraie ?

- a) $u_n=0$ pour tout $n\geq1$, donc $(u_n)$ est constante.
- b) $u_n=\ln\left(1+\dfrac1n\right)$, donc $(u_n)$ est croissante.
- c) $u_n=\ln\left(1+\dfrac1n\right)$, donc $(u_n)$ est décroissante.
- d) $u_n=\dfrac{1}{n(n+1)}$, donc $(u_n)$ est décroissante.

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Une primitive de $x\mapsto\dfrac1x$ sur $]0\,;+\infty[$ est $x\mapsto\ln x$, et $\ln a-\ln b=\ln\dfrac ab$. Pour étudier le sens de variation de $(u_n)$, on peut aussi encadrer $u_n$ grâce à la décroissance de $x\mapsto\dfrac1x$ : $\dfrac{1}{n+1}\leq u_n\leq\dfrac1n$, d'où $u_{n+1}\leq\dfrac{1}{n+1}\leq u_n$.

### Corrigé
Pour $n\geq1$ :
$$u_n=\Big[\ln x\Big]_n^{n+1}=\ln(n+1)-\ln n=\ln\left(\dfrac{n+1}{n}\right)=\ln\left(1+\dfrac1n\right).$$

La suite $n\mapsto1+\dfrac1n$ est strictement décroissante et la fonction $\ln$ est strictement croissante, donc $(u_n)$ est strictement décroissante.

Autre méthode (sans calculer $u_n$) : $x\mapsto\dfrac1x$ est décroissante sur $[n\,;n+1]$, donc $\dfrac{1}{n+1}\leq u_n\leq\dfrac1n$ ; au rang $n+1$, $u_{n+1}\leq\dfrac{1}{n+1}$, d'où $u_{n+1}\leq\dfrac{1}{n+1}\leq u_n$.

Vérification numérique : $u_1=\ln2\approx0{,}693$, $u_2=\ln\dfrac32\approx0{,}405$, $u_3=\ln\dfrac43\approx0{,}288$.

### Pourquoi les autres réponses sont fausses
- **a)** On a écrit $\ln(n+1)-\ln n=\ln\big((n+1)-n\big)=\ln1$ : la différence de deux logarithmes est le logarithme du quotient, pas de la différence.
- **b)** L'expression est juste, mais on a conclu à la croissance parce que $\ln$ est croissante, en oubliant que $1+\dfrac1n$ diminue quand $n$ augmente.
- **d)** On a pris $-\dfrac1x$ comme primitive de $\dfrac1x$ (c'est une primitive de $\dfrac{1}{x^2}$) : $\left[-\dfrac1x\right]_n^{n+1}=\dfrac{1}{n(n+1)}$ n'est pas $u_n$.

</details>

Avis : 

---

## 52. `cqc-monotonie-d-une-suite-moyenne-2` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Pour tout entier naturel $n$, on pose $u_n=\displaystyle\int_0^1(2-x)^n\,dx$. Laquelle des affirmations suivantes est vraie ?

- a) $u_n=\dfrac{2^{n+1}-1}{n+1}$, donc $(u_n)$ est strictement croissante.
- b) $u_n=\dfrac{1-2^{n+1}}{n+1}$, donc $(u_n)$ est strictement décroissante.
- c) $u_n=\dfrac{2^{n+1}-1}{n+1}$, donc $(u_n)$ est strictement décroissante.
- d) $u_n=2^{n+1}-1$, donc $(u_n)$ est strictement croissante.

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Une primitive de $x\mapsto(ax+b)^n$ est $x\mapsto\dfrac{(ax+b)^{n+1}}{a(n+1)}$ : ici $a=-1$, ce qui introduit un signe moins. Pour le sens de variation, on peut aussi calculer $u_{n+1}-u_n=\displaystyle\int_0^1(2-x)^n(1-x)\,dx$ et utiliser la positivité de l'intégrale.

### Corrigé
Une primitive de $x\mapsto(2-x)^n$ est $x\mapsto-\dfrac{(2-x)^{n+1}}{n+1}$, donc
$$u_n=\left[-\dfrac{(2-x)^{n+1}}{n+1}\right]_0^1=-\dfrac{1}{n+1}+\dfrac{2^{n+1}}{n+1}=\dfrac{2^{n+1}-1}{n+1}.$$

Sens de variation : pour tout entier naturel $n$,
$$u_{n+1}-u_n=\int_0^1\Big[(2-x)^{n+1}-(2-x)^n\Big]dx=\int_0^1(2-x)^n(1-x)\,dx.$$
Sur $[0\,;1]$, $(2-x)^n>0$ et $1-x\geq0$ ; la fonction intégrée est continue, positive et non identiquement nulle (elle vaut $2^n$ en $0$), donc son intégrale est strictement positive. Ainsi $u_{n+1}>u_n$ : la suite est strictement croissante.

Vérification : $u_0=1$, $u_1=1{,}5$, $u_2=\dfrac73\approx2{,}333$.

### Pourquoi les autres réponses sont fausses
- **b)** On a oublié le signe moins dû à la dérivée de $2-x$ : on obtient des termes négatifs, alors que $u_n$ est l'intégrale d'une fonction positive.
- **c)** L'expression est juste, mais on a conclu à la décroissance parce que le dénominateur $n+1$ augmente, sans voir que $2^{n+1}$ augmente beaucoup plus vite.
- **d)** On a oublié de diviser par $n+1$ en primitivant : par exemple $u_1=1{,}5$ et non $3$.

</details>

Avis : 

---

## 53. `cqc-moyenne-arithmetique-bac-a-elevee-2` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Une coopérative de planteurs de café de l'Ouest du Cameroun regroupe deux groupes de producteurs. Le groupe Nord compte $12$ planteurs, dont la récolte moyenne de la saison est de $450$ kg par planteur. Le groupe Sud compte $18$ planteurs, dont la récolte moyenne est de $550$ kg par planteur.

Lors d'un contrôle, il apparaît que la récolte d'un planteur du groupe Nord, inscrite pour $380$ kg, était en réalité de $500$ kg. Après correction, quelle est la récolte moyenne par planteur de l'ensemble des $30$ planteurs de la coopérative ?

- a) $505$ kg
- b) $506$ kg
- c) $514$ kg
- d) $520$ kg

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour deux groupes d'effectifs $n_1$ et $n_2$ et de moyennes $\bar{x}_1$ et $\bar{x}_2$, la somme des valeurs de chaque groupe vaut $n_1\,\bar{x}_1$ et $n_2\,\bar{x}_2$. La moyenne de l'ensemble est la somme totale divisée par l'effectif total : $\bar{x}=\dfrac{n_1\bar{x}_1+n_2\bar{x}_2}{n_1+n_2}$. Elle est comprise entre $\bar{x}_1$ et $\bar{x}_2$.

### Corrigé
Récoltes totales avant correction : groupe Nord $12\times 450=5\,400$ kg, groupe Sud $18\times 550=9\,900$ kg, soit $15\,300$ kg et une moyenne de $\dfrac{15\,300}{30}=510$ kg.

La valeur corrigée dépasse l'ancienne de $500-380=120$ kg. La récolte totale du groupe Nord devient $5\,400+120=5\,520$ kg, d'où $\bar{x}_{\text{Nord}}=\dfrac{5\,520}{12}=460$ kg. Pour l'ensemble :
$$\bar{x}=\dfrac{12\times 460+18\times 550}{30}=\dfrac{5\,520+9\,900}{30}=\dfrac{15\,420}{30}=514.$$

La récolte moyenne de la coopérative est de $514$ kg par planteur.

Contrôle : la hausse de $120$ kg, répartie sur $30$ planteurs, relève la moyenne de $\dfrac{120}{30}=4$ kg : $510+4=514$. De plus $460\leq 514\leq 550$, et $514$ est plus proche de $550$, le groupe Sud étant plus nombreux.

### Pourquoi les autres réponses sont fausses
- **a)** $505=\dfrac{460+550}{2}$ : on a fait la moyenne des deux moyennes sans tenir compte des effectifs différents des groupes.
- **b)** $506=510-4$ : on a calculé l'écart dans le mauvais sens ($380-500=-120$ kg), comme si la correction diminuait la récolte.
- **d)** $520=510+\dfrac{120}{12}$ : on a réparti la hausse sur les $12$ planteurs du groupe Nord au lieu des $30$ planteurs de la coopérative.

</details>

Avis : 

---

## 54. `cqc-moyenne-arithmetique-bac-a-moyenne-1` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Mireille a obtenu les notes suivantes, sur $20$, aux quatre premières évaluations de mathématiques de l'année : $11$ ; $14$ ; $9$ ; $12$. À la cinquième évaluation, elle obtient exactement la note qui porte sa moyenne sur les cinq évaluations à $12$. Elle obtient ensuite la note $6$ à la sixième évaluation. Enfin, le professeur annule l'évaluation où Mireille avait obtenu $9$.

Quelle est la moyenne des notes restantes de Mireille ?

- a) $9{,}5$
- b) $10{,}75$
- c) $11{,}1$
- d) $11{,}4$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
La moyenne arithmétique de $n$ valeurs est leur somme divisée par $n$ : la somme des valeurs vaut donc $n\,\bar{x}$. Pour viser une moyenne donnée avec une valeur supplémentaire, on calcule la somme totale exigée, puis on la compare à la somme déjà acquise. Ajouter ou retirer une valeur modifie à la fois la somme et l'effectif : la moyenne se recalcule toujours avec le nouvel effectif.

### Corrigé
**Cinquième note.** Les quatre premières notes totalisent $11+14+9+12=46$ points. Pour une moyenne de $12$ sur $5$ évaluations, il faut une somme de $5\times 12=60$, donc la cinquième note vaut $60-46=14$.

**Six notes.** Les notes sont $11$ ; $14$ ; $9$ ; $12$ ; $14$ ; $6$, de somme $66$ et de moyenne $\dfrac{66}{6}=11$.

**Annulation du $9$.** La somme devient $66-9=57$ et il reste $5$ notes ($11$ ; $14$ ; $12$ ; $14$ ; $6$) :
$$\bar{x}=\dfrac{57}{5}=11{,}4.$$

La moyenne passe de $11$ à $11{,}4$ : la note retirée était inférieure à la moyenne, la retirer la fait remonter.

### Pourquoi les autres réponses sont fausses
- **a)** $9{,}5=\dfrac{57}{6}$ : on a retiré la note de la somme mais divisé encore par $6$ au lieu de $5$.
- **b)** $10{,}75=\dfrac{43}{4}$ : on a oublié la cinquième note ($14$) dans la liste des notes restantes.
- **c)** $11{,}1$ vient d'une cinquième note de $12{,}5$, obtenue en résolvant $\dfrac{11{,}5+x}{2}=12$, comme si l'ancienne moyenne et la nouvelle note avaient le même poids.

</details>

Avis : 

---

## 55. `cqc-methode-de-mayer-moyenne-2` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Le service qualité d'une usine textile relève, chaque semaine, le nombre de pièces défectueuses pour 1000 pièces produites sur une chaîne de production, après la mise en place d'un nouveau protocole de contrôle. Après avoir classé les relevés par semaines croissantes et appliqué la méthode de Mayer, on obtient les points moyens $G_1(2;45)$ et $G_2(8;15)$, où $x$ désigne le rang de la semaine et $y$ le nombre de pièces défectueuses pour 1000 pièces produites.

Quelle est une équation de la droite de Mayer $(G_1G_2)$ ?

- a) $y=-0{,}2x+45{,}4$
- b) $y=-5x+55$
- c) $y=-5x+35$
- d) $y=5x+35$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Lorsque $G_1$ et $G_2$ sont connus, le coefficient directeur de la droite de Mayer est $a=\dfrac{\bar y_2-\bar y_1}{\bar x_2-\bar x_1}$ ; on obtient l'ordonnée à l'origine $b$ en écrivant que $G_1$ appartient à la droite. Son signe renseigne sur le sens d'évolution de $y$ lorsque $x$ augmente.

### Corrigé
$a=\dfrac{15-45}{8-2}=\dfrac{-30}{6}=-5$.

Avec $G_1(2;45)$ : $45=-5\times2+b$, donc $b=45+10=55$. D'où
$$y=-5x+55.$$

Vérification avec $G_2$ : $-5\times8+55=15$, conforme.

Interprétation : le coefficient directeur est négatif ; chaque semaine supplémentaire correspond en moyenne à environ 5 pièces défectueuses de moins pour 1000 pièces produites.

### Pourquoi les autres réponses sont fausses
- **a)** On a calculé $\dfrac{\Delta x}{\Delta y}=\dfrac{6}{-30}=-0{,}2$ au lieu de $\dfrac{\Delta y}{\Delta x}$ : cette droite passe par $G_1$ mais pas par $G_2$.
- **c)** Le coefficient $-5$ est juste, mais on a calculé $b=45-10$ en se trompant de signe : la droite ne passe ni par $G_1$ ni par $G_2$.
- **d)** On a perdu le signe de $-30$ : avec $a=5$, on trouve $b=35$ et la droite passe par $G_1$ mais pas par $G_2$ ($5\times8+35=75\neq15$) ; une pente positive contredit d'ailleurs la baisse de $45$ à $15$.

</details>

Avis : 

---

## 56. `cqc-position-relative-courbe-asymptote-bac-a-elevee-2` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère la fonction $f$ définie pour tout réel $x$ par
$$f(x)=\dfrac{4x^2-3x+13}{x^2+1}$$
et sa courbe représentative $(C)$ dans un repère. La droite $(\Delta)$ d'équation $y=4$ est admise comme asymptote horizontale à $(C)$ en $+\infty$ et en $-\infty$.

Quelle est la position relative de $(C)$ et de $(\Delta)$ ?

- a) $(C)$ est en dessous de $(\Delta)$ sur $]-\infty\,;3[$ et au-dessus sur $]3\,;+\infty[$ ; point commun $A(3\,;4)$.
- b) $(C)$ est au-dessus de $(\Delta)$ sur $]-\infty\,;-3[$ et en dessous sur $]-3\,;+\infty[$ ; point commun $A(-3\,;4)$.
- c) $(C)$ est au-dessus de $(\Delta)$ sur $]-\infty\,;3[$ et en dessous sur $]3\,;+\infty[$ ; point commun $A(3\,;4)$.
- d) $(C)$ est au-dessus de $(\Delta)$ sur $\left]-\infty\,;\dfrac{13}{3}\right[$ et en dessous sur $\left]\dfrac{13}{3}\,;+\infty\right[$ ; point commun $A\left(\dfrac{13}{3}\,;4\right)$.

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Situer une courbe par rapport à son asymptote horizontale $y=\ell$ revient à mettre $f(x)-\ell$ sur un dénominateur commun, à factoriser le numérateur, puis à dresser le signe du quotient ; les valeurs qui annulent l'écart fournissent les points communs.

### Corrigé
Le dénominateur $x^2+1$ est strictement positif pour tout réel $x$. Pour tout réel $x$ :
$$f(x)-4=\dfrac{4x^2-3x+13-4(x^2+1)}{x^2+1}=\dfrac{-3x+9}{x^2+1}=\dfrac{-3(x-3)}{x^2+1}.$$

Le signe de $f(x)-4$ est celui de $-3(x-3)$ : positif pour $x<3$, nul en $3$, négatif pour $x>3$.

| $x$ | $-\infty$ | | $3$ | | $+\infty$ |
|---|---|---|---|---|---|
| signe de $f(x)-4$ | | $+$ | $0$ | $-$ | |

Conclusion : $(C)$ est au-dessus de $(\Delta)$ sur $]-\infty\,;3[$, en dessous sur $]3\,;+\infty[$, et le seul point commun est $A(3\,;4)$.

Vérification : $f(0)=13>4$, $f(3)=\dfrac{40}{10}=4$, $f(5)=\dfrac{49}{13}\approx3{,}77<4$.

### Pourquoi les autres réponses sont fausses
- **a)** On a oublié le signe du facteur $-3$ : $-3(x-3)$ est positif quand $x<3$, pas négatif.
- **b)** On a résolu $-3x+9=0$ en $x=-3$ au lieu de $x=3$ : par exemple $f(-2)=\dfrac{35}{5}=7>4$, alors que cette réponse place la courbe en dessous.
- **d)** On a oublié de multiplier le $1$ du dénominateur par $4$ (numérateur $-3x+13$) : par exemple $f(4)=\dfrac{65}{17}\approx3{,}82<4$, alors que cette réponse place la courbe au-dessus.

</details>

Avis : 

---

## 57. `cqc-position-relative-courbe-asymptote-bac-a-moyenne-1` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Une coopérative de producteurs de cacao de Mbalmayo estime que le coût moyen de production, en F CFA par kilogramme, pour une quantité de $q$ centaines de kilogrammes ($q>0$), est donné par
$$C(q)=\dfrac{200q+1500}{q+5}.$$
On note $(\Gamma)$ la courbe représentative de $C$ et $(\Delta)$ la droite d'équation $y=200$, que l'on admet être asymptote horizontale à $(\Gamma)$ en $+\infty$.

Laquelle des affirmations suivantes est vraie pour tout $q>0$ ?

- a) $C(q)-200=\dfrac{2500}{q+5}$, donc $(\Gamma)$ est au-dessus de $(\Delta)$.
- b) $C(q)-200=\dfrac{1495}{q+5}$, donc $(\Gamma)$ est au-dessus de $(\Delta)$.
- c) $C(q)-200=\dfrac{500}{q+5}$, donc $(\Gamma)$ est au-dessus de $(\Delta)$.
- d) $C(q)-200=\dfrac{-500}{q+5}$, donc $(\Gamma)$ est en dessous de $(\Delta)$.

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
On situe une courbe par rapport à son asymptote en étudiant le signe de l'écart vertical entre elles, c'est-à-dire de la fonction diminuée de l'ordonnée de la droite ; si cet écart n'est jamais nul, la courbe et la droite n'ont aucun point commun.

### Corrigé
Pour tout $q>0$ :
$$C(q)-200=\dfrac{200q+1500-200(q+5)}{q+5}=\dfrac{200q+1500-200q-1000}{q+5}=\dfrac{500}{q+5}.$$

Pour $q>0$, $q+5>0$ et $500>0$, donc $C(q)-200>0$ : la courbe $(\Gamma)$ est au-dessus de $(\Delta)$ sur $]0\,;+\infty[$, et comme le numérateur $500$ n'est jamais nul, elle ne coupe jamais $(\Delta)$.

Interprétation : le coût moyen reste toujours supérieur à $200$ F CFA par kilogramme ; il s'en rapproche quand la production augmente, sans jamais l'atteindre.

Contrôle : $C(5)=\dfrac{2500}{10}=250$ et $\dfrac{500}{5+5}=50=250-200$.

### Pourquoi les autres réponses sont fausses
- **a)** On a écrit $-200(q+5)=-200q+1000$ : erreur de signe dans la distribution, d'où $2500$ au lieu de $500$ (contrôle : en $q=5$, cela donnerait $250$ d'écart au lieu de $50$).
- **b)** On a écrit $200(q+5)=200q+5$ en ne multipliant pas le $5$ par $200$, d'où le numérateur $1495$.
- **d)** On a calculé $200-C(q)$ au lieu de $C(q)-200$ : le signe est inversé, et la position avec.

</details>

Avis : 

---

## 58. `cqc-primitives-usuelles-moyenne-4` (séries C)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur l'intervalle $]0;+\infty[$ par $f(x) = \dfrac{2}{x} + 3\cos x - 5x^{4}$.

Laquelle des fonctions suivantes est une primitive de $f$ sur cet intervalle ?

- a) $F(x)=2\ln x-3\sin x-x^{5}$
- b) $F(x)=-\dfrac{2}{x^{2}}+3\sin x-x^{5}$
- c) $F(x)=2\ln x+3\sin x-\dfrac{5x^{5}}{4}$
- d) $F(x)=2\ln x+3\sin x-x^{5}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Le formulaire usuel donne, sur $]0;+\infty[$, une primitive $\ln x$ pour $\dfrac1x$, $\sin x$ pour $\cos x$ et $\dfrac{x^{n+1}}{n+1}$ pour $x^{n}$. Chaque terme d'une somme se primitive indépendamment par la formule qui lui correspond.

### Corrigé
On primitive $f$ terme à terme sur $]0;+\infty[$ :
- une primitive de $\dfrac{2}{x}$ est $2\ln x$ (car $x>0$) ;
- une primitive de $3\cos x$ est $3\sin x$ ;
- une primitive de $-5x^{4}$ est $-5\times\dfrac{x^{5}}{5} = -x^{5}$.

Une primitive de $f$ sur $]0;+\infty[$ est donc $F(x) = 2\ln x + 3\sin x - x^{5}$ (les autres s'en déduisent en ajoutant une constante).

Vérification : $F'(x) = \dfrac{2}{x} + 3\cos x - 5x^{4} = f(x)$.

### Pourquoi les autres réponses sont fausses
- **a)** On a pris $-\sin x$ comme primitive de $\cos x$ : c'est la dérivée de $\cos x$, pas une primitive.
- **b)** On a dérivé $\dfrac2x$ au lieu de le primitiver, ce qui donne $-\dfrac{2}{x^2}$.
- **c)** On a divisé par l'ancien exposant $4$ au lieu du nouvel exposant $5$ : la dérivée de $-\dfrac{5x^{5}}{4}$ est $-\dfrac{25x^{4}}{4}$, pas $-5x^{4}$.

</details>

Avis : 

---

## 59. `cqc-probabilites-totales-bac-ti-mat-elevee-2` (séries TI)

**Remarque du relecteur :** Le choix b) (0,0956) est donné au dix-millième alors que l'énoncé demande un arrondi au millième : distracteur reconnaissable à sa forme ; l'harmoniser.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans le centre de données d'un opérateur de télécommunications à Douala, un serveur choisi au hasard est défaillant avec la probabilité $0{,}04$. Un test automatique déclenche une alarme avec la probabilité $0{,}95$ lorsque le serveur est défaillant, et avec la probabilité $0{,}06$ lorsqu'il fonctionne normalement. Un serveur est choisi au hasard puis soumis au test. On note $D$ l'événement « le serveur est défaillant » et $A$ l'événement « l'alarme se déclenche ».

L'alarme vient de se déclencher. Quelle est la probabilité que le serveur soit réellement défaillant ? (Valeur arrondie au millième.)

- a) $0{,}397$
- b) $0{,}096$
- c) $0{,}038$
- d) $0{,}95$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Si $D$ et $\overline{D}$ forment une partition, alors $P(A)=P(D)\,P_D(A)+P(\overline{D})\,P_{\overline{D}}(A)$. La probabilité conditionnelle « inverse » se déduit ensuite de la définition $P_A(D)=\dfrac{P(A\cap D)}{P(A)}$, avec $P(A\cap D)=P(D)\,P_D(A)$.

### Corrigé

Un serveur est soit défaillant, soit sain : $D$ et $\overline{D}$ forment une partition de l'univers, avec $P(D)=0{,}04$ et $P(\overline{D})=0{,}96$.

D'après la formule des probabilités totales :

$$P(A)=0{,}04\times0{,}95+0{,}96\times0{,}06=0{,}038+0{,}0576=0{,}0956.$$

On a $P(A\cap D)=P(D)\,P_D(A)=0{,}04\times0{,}95=0{,}038$, donc :

$$P_A(D)=\dfrac{P(A\cap D)}{P(A)}=\dfrac{0{,}038}{0{,}0956}\approx0{,}397\ \text{(arrondi au millième)}.$$

Vérification sur un parc de $10\,000$ serveurs : $400$ défaillants dont $380$ avec alarme, $9\,600$ sains dont $576$ avec alarme ; la proportion de vraies pannes parmi les $956$ alarmes est $\dfrac{380}{956}\approx0{,}397$.

Interprétation : lorsqu'une alarme se déclenche, le serveur n'est réellement défaillant que dans environ $39{,}7\,\%$ des cas ; la majorité des alarmes sont de fausses alarmes, car les pannes sont rares.

### Pourquoi les autres réponses sont fausses

- **b)** $0{,}096$ est $P(A)=0{,}0956$ arrondi au millième, la probabilité qu'une alarme se déclenche, et non la probabilité conditionnelle demandée.
- **c)** $0{,}038$ est $P(A\cap D)$ : on a oublié de diviser par $P(A)$.
- **d)** $0{,}95$ est $P_D(A)$ : on a confondu $P_A(D)$ avec $P_D(A)$.

</details>

Avis : 

---

## 60. `cqc-produit-mixte-moyenne-2` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé $(O;\vec i,\vec j,\vec k)$ de l'espace, on considère le tétraèdre $ABCD$ avec $A(-1;2;1)$, $B(2;3;-1)$, $C(0;-1;4)$ et $D(3;1;2)$.

Quel est le volume du tétraèdre $ABCD$, en unités de volume ?

- a) $11$
- b) $\dfrac{11}{6}$
- c) $\dfrac{11}{3}$
- d) $\dfrac{11}{2}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Le volume du tétraèdre $ABCD$ est donné par $V=\dfrac{1}{6}\left|\vec{AB}\cdot(\vec{AC}\wedge\vec{AD})\right|$. Le nombre $\vec{AB}\cdot(\vec{AC}\wedge\vec{AD})$ se calcule soit en deux étapes (produit vectoriel puis produit scalaire), soit directement comme déterminant des coordonnées des trois vecteurs.

### Corrigé
On calcule $\vec{AB}=(3;1;-2)$, $\vec{AC}=(1;-3;3)$, $\vec{AD}=(4;-1;1)$.

Produit vectoriel : $\vec{AC}\wedge\vec{AD}=(-3\times1-3\times(-1); 3\times4-1\times1; 1\times(-1)-(-3)\times4)=(0;11;11)$.

Produit scalaire : $\vec{AB}\cdot(\vec{AC}\wedge\vec{AD})=3\times0+1\times11+(-2)\times11=0+11-22=-11$.

Vérification par le déterminant direct : $3\times(-3\times1-3\times(-1))-1\times(1\times1-3\times4)+(-2)\times(1\times(-1)-(-3)\times4)=0+11-22=-11$. Les deux méthodes concordent.

Le volume du tétraèdre est $V=\dfrac{|-11|}{6}=\dfrac{11}{6}$ unités de volume.

### Pourquoi les autres réponses sont fausses

- **a)** $11$ est la valeur absolue de $\vec{AB}\cdot(\vec{AC}\wedge\vec{AD})$ : c'est le volume du parallélépipède, on a oublié le facteur $\dfrac16$.
- **c)** $\dfrac{11}{3}$ vient de la formule $\dfrac13\times$ base $\times$ hauteur appliquée à tort avec ce nombre, au lieu du facteur $\dfrac16$.
- **d)** $\dfrac{11}{2}$ vient du facteur $\dfrac12$ de l'aire d'un triangle, confondue avec le volume.

</details>

Avis : 

---

## 61. `cqc-produit-mixte-moyenne-3` (séries C/E)

**Remarque du relecteur :** LIMITE : volume du tétraèdre par produit mixte (produit vectoriel puis scalaire) ; au programme C/E mais exigeant.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé $(O;\vec i,\vec j,\vec k)$ de l'espace, on donne les points $A(1;-1;2)$, $B(3;0;1)$, $C(2;2;0)$ et $D(0;1;3)$.

Parmi les affirmations suivantes, laquelle est exacte ?

- a) Les points $A$, $B$, $C$, $D$ sont coplanaires.
- b) Les points ne sont pas coplanaires et le volume de $ABCD$ vaut $10$ unités de volume.
- c) Les points ne sont pas coplanaires et le volume de $ABCD$ vaut $\dfrac53$ unités de volume.
- d) Les points ne sont pas coplanaires et le volume de $ABCD$ vaut $\dfrac{10}{3}$ unités de volume.

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Quatre points $A,B,C,D$ de l'espace sont coplanaires si et seulement si le nombre $\vec{AB}\cdot(\vec{AC}\wedge\vec{AD})$ est nul. S'il est non nul, les points définissent un tétraèdre de volume $V=\dfrac{1}{6}\left|\vec{AB}\cdot(\vec{AC}\wedge\vec{AD})\right|$.

### Corrigé
On calcule $\vec{AB}=(2;1;-1)$, $\vec{AC}=(1;3;-2)$, $\vec{AD}=(-1;2;1)$.

Produit vectoriel : $\vec{AC}\wedge\vec{AD}=(3\times1-(-2)\times2; (-2)\times(-1)-1\times1; 1\times2-3\times(-1))=(7;1;5)$.

Produit scalaire : $\vec{AB}\cdot(\vec{AC}\wedge\vec{AD})=2\times7+1\times1+(-1)\times5=14+1-5=10$.

Vérification par le déterminant direct : $2\times(3\times1-(-2)\times2)-1\times(1\times1-(-2)\times(-1))+(-1)\times(1\times2-3\times(-1))=14+1-5=10$. Les deux méthodes concordent.

Ce nombre vaut $10\neq0$ : les points $A$, $B$, $C$ et $D$ ne sont pas coplanaires. Le volume du tétraèdre est $V=\dfrac{|10|}{6}=\dfrac{5}{3}$ unités de volume.

### Pourquoi les autres réponses sont fausses

- **a)** Les points ne sont pas coplanaires, puisque $\vec{AB}\cdot(\vec{AC}\wedge\vec{AD})=10\neq0$ ; conclure à la coplanarité vient d'une erreur de calcul sur une coordonnée de $\vec{AC}\wedge\vec{AD}$ ou d'une conclusion tirée sans calcul.
- **b)** $10$ est la valeur absolue de $\vec{AB}\cdot(\vec{AC}\wedge\vec{AD})$ : on a oublié le facteur $\dfrac16$.
- **d)** $\dfrac{10}{3}$ vient du facteur $\dfrac13$ utilisé à la place de $\dfrac16$.

</details>

Avis : 

---

## 62. `cqc-projecteur-moyenne-0` (séries C/E)

**Remarque du relecteur :** LIMITE : endomorphisme d'un espace de dimension 3 et noyau, haut du programme C/E ; la donnée p∘p=p est inutile pour la réponse.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $E$ un espace vectoriel réel de dimension 3, muni d'une base $(e_1,e_2,e_3)$. On définit l'endomorphisme $p$ de $E$ par :

$$p(e_1)=e_1,\qquad p(e_2)=e_2,\qquad p(e_3)=e_1+e_2.$$

On admet que $p\circ p=p$. Quel est le noyau $\ker(p)$ ?

- a) $\mathrm{Vect}(e_3)$
- b) $\mathrm{Vect}(e_1+e_2)$
- c) $\mathrm{Vect}(e_1+e_2+e_3)$
- d) $\mathrm{Vect}(e_1+e_2-e_3)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour un projecteur $p$ d'un espace vectoriel $E$, $\mathrm{Im}(p)$ est l'ensemble des vecteurs invariants par $p$ (ceux qui vérifient $p(x)=x$), et $\ker(p)$ s'obtient en résolvant l'équation $p(x)=0$ pour un vecteur quelconque $x$ écrit dans la base.

### Corrigé

Soit $x=ae_1+be_2+ce_3\in E$. Par linéarité :
$$p(x)=a\,e_1+b\,e_2+c\,(e_1+e_2)=(a+c)e_1+(b+c)e_2.$$

$x\in\ker(p) \iff (a+c)e_1+(b+c)e_2=0 \iff a+c=0 \text{ et } b+c=0 \iff a=-c \text{ et } b=-c$.

Donc $x=-c\,e_1-c\,e_2+c\,e_3=-c\,(e_1+e_2-e_3)$, $c\in\mathbb{R}$. Ainsi :
$$\ker(p)=\mathrm{Vect}(e_1+e_2-e_3), \quad \dim\ker(p)=1.$$

Contrôle : $p(e_1+e_2-e_3)=e_1+e_2-(e_1+e_2)=0$. Par ailleurs $\mathrm{Im}(p)=\mathrm{Vect}(e_1,e_2)$ et $E=\ker(p)\oplus\mathrm{Im}(p)$.

### Pourquoi les autres réponses sont fausses

- **a)** $\mathrm{Vect}(e_3)$ : $p(e_3)=e_1+e_2\neq0$, donc $e_3$ n'est pas dans le noyau ; on a confondu « vecteur qui n'est pas invariant » et « vecteur d'image nulle ».
- **b)** $\mathrm{Vect}(e_1+e_2)$ est contenu dans l'image : $p(e_1+e_2)=e_1+e_2\neq0$ ; on a confondu le noyau avec $p(e_3)$.
- **c)** $\mathrm{Vect}(e_1+e_2+e_3)$ vient d'une erreur de signe : $p(e_1+e_2+e_3)=2e_1+2e_2\neq0$.

</details>

Avis : 

---

## 63. `cqc-projecteur-moyenne-1` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $E$ un espace vectoriel réel et $f$ un endomorphisme de $E$ vérifiant la relation (admise) :

$$f\circ f = 5f - 6\,Id,$$

où $Id$ désigne l'endomorphisme identité de $E$. On pose $s=f-2\,Id$.

Exprimer $s\circ s$ en fonction de $f$ et de $Id$.

- a) $f-2\,Id$
- b) $9f-2\,Id$
- c) $f-10\,Id$
- d) $3f-2\,Id$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'un endomorphisme $f$ vérifie une relation admise du type $f\circ f=\alpha f+\beta\,Id$, on développe le carré d'une combinaison de $f$ et $Id$ à l'aide de la bilinéarité de la composition (les termes croisés comptent deux fois, puisque $f\circ Id=Id\circ f=f$), puis on substitue la relation admise à $f\circ f$ dès qu'elle apparaît.

### Corrigé

$$s\circ s=(f-2\,Id)\circ(f-2\,Id)=f\circ f-2f-2f+4\,Id=f\circ f-4f+4\,Id.$$
En remplaçant $f\circ f$ par $5f-6\,Id$ :
$$s\circ s=(5f-6\,Id)-4f+4\,Id=f-2\,Id=s.$$
Donc $s\circ s=s$ : $s$ est un projecteur. De même, $t=3\,Id-f$ vérifie $t\circ t=t$, et $s+t=Id$ : $s$ et $t$ sont deux projecteurs complémentaires.

### Pourquoi les autres réponses sont fausses

- **b)** $9f-2\,Id$ vient d'une erreur de signe sur les termes croisés : $f\circ f+4f+4\,Id$ au lieu de $f\circ f-4f+4\,Id$.
- **c)** $f-10\,Id$ vient d'une erreur de signe sur le terme constant : $(-2\,Id)\circ(-2\,Id)=+4\,Id$ et non $-4\,Id$.
- **d)** $3f-2\,Id$ vient de l'oubli du double produit : on a écrit $f\circ f-2f+4\,Id$ au lieu de $f\circ f-4f+4\,Id$.

</details>

Avis : 

---

## 64. `cqc-projecteur-moyenne-2` (séries C/E)

**Remarque du relecteur :** LIMITE : projecteur d'un espace vectoriel réel quelconque, noyau et image d'endomorphisme : formulation abstraite à la limite haute du programme de Terminale C/E (habituellement en dimension 2 ou 3).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $E$ un espace vectoriel réel et $p$ un projecteur de $E$, c'est-à-dire un endomorphisme vérifiant $p\circ p=p$. On pose $q=Id-p$, où $Id$ est l'endomorphisme identité de $E$.

Parmi les égalités suivantes, laquelle est toujours vraie ?

- a) $\mathrm{Im}(q)=\mathrm{Im}(p)$
- b) $\mathrm{Im}(q)=\ker(p)$
- c) $\ker(q)=\ker(p)$
- d) $\mathrm{Im}(q)=E$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour montrer qu'une combinaison d'endomorphismes est un projecteur, on développe son carré à l'aide de la bilinéarité de la composition et on utilise $p\circ p=p$. Pour établir l'égalité de deux sous-espaces vectoriels comme $\mathrm{Im}(q)$ et $\ker(p)$, on procède par double inclusion.

### Corrigé

On a $q\circ q=Id-2p+p\circ p=Id-p=q$, et $p\circ q=p-p\circ p=0$.

*Inclusion $\mathrm{Im}(q)\subset\ker(p)$ :* soit $y=q(x)$ avec $x\in E$. Alors $p(y)=(p\circ q)(x)=0$, donc $y\in\ker(p)$.

*Inclusion $\ker(p)\subset\mathrm{Im}(q)$ :* soit $y\in\ker(p)$. Alors $q(y)=y-p(y)=y$, donc $y=q(y)\in\mathrm{Im}(q)$.

On conclut : $\mathrm{Im}(q)=\ker(p)$.

### Pourquoi les autres réponses sont fausses

- **a)** $\mathrm{Im}(q)=\mathrm{Im}(p)$ est faux : un vecteur $y$ de $\mathrm{Im}(p)$ vérifie $p(y)=y$, donc $q(y)=0$ ; les deux images n'ont en commun que le vecteur nul.
- **c)** $\ker(q)=\ker(p)$ est faux : $q(x)=0$ équivaut à $p(x)=x$, donc $\ker(q)=\mathrm{Im}(p)$, et non $\ker(p)$.
- **d)** $\mathrm{Im}(q)=E$ n'est vrai que si $p$ est l'endomorphisme nul ; c'est la confusion entre $q=Id-p$ et $Id$.

</details>

Avis : 

---

## 65. `cqc-prolongement-par-continuite-moyenne-0` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $h$ la fonction définie par $h(x) = \dfrac{\sqrt{x+1}-2}{x-3}$ pour tout réel $x \geqslant -1$, $x \neq 3$.

Parmi les affirmations suivantes, laquelle est exacte ?

- a) $h$ se prolonge par continuité en $3$ en posant $h(3)=0$.
- b) $h$ se prolonge par continuité en $3$ en posant $h(3)=\dfrac12$.
- c) $h$ se prolonge par continuité en $3$ en posant $h(3)=\dfrac14$.
- d) $h$ ne peut pas être prolongée par continuité en $3$, car la formule donne $\dfrac00$.

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'une formule fait intervenir une racine carrée et prend la forme indéterminée $\dfrac{0}{0}$ en un point $x_0$, on multiplie le numérateur et le dénominateur par la quantité conjuguée de l'expression radicale : cela fait apparaître un facteur commun $(x-x_0)$ qui se simplifie, et permet souvent d'obtenir une limite finie en $x_0$.

### Corrigé

En $x=3$, le dénominateur s'annule, et le numérateur aussi : $\sqrt{3+1}-2=0$. La formule prend la forme indéterminée $\dfrac{0}{0}$.

Multiplions numérateur et dénominateur par la quantité conjuguée $\sqrt{x+1}+2$ :
$$h(x)=\frac{(x+1)-4}{(x-3)(\sqrt{x+1}+2)}=\frac{x-3}{(x-3)(\sqrt{x+1}+2)}=\frac{1}{\sqrt{x+1}+2}.$$

Cette dernière expression est continue en $3$ (son dénominateur vaut au moins $2$), donc :
$$\lim_{x\to3}h(x)=\frac{1}{\sqrt4+2}=\frac14.$$

La limite est finie : on prolonge $h$ par continuité en $3$ en posant $h(3)=\dfrac14$.

### Pourquoi les autres réponses sont fausses

- **a)** Le numérateur tend vers $0$, mais le dénominateur aussi : la forme $\dfrac00$ n'impose pas une limite nulle.
- **b)** $\dfrac12$ vient de l'oubli du terme $2$ au dénominateur après simplification : $\dfrac{1}{\sqrt{x+1}}$ au lieu de $\dfrac{1}{\sqrt{x+1}+2}$.
- **d)** Une forme indéterminée $\dfrac00$ n'empêche pas le prolongement : il faut lever l'indétermination avant de conclure.

</details>

Avis : 

---

## 66. `cqc-prolongement-par-continuite-moyenne-1` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $k$ la fonction définie par $k(x) = (x-1)\ln|x-1|$ pour tout réel $x \neq 1$.

Parmi les affirmations suivantes, laquelle est exacte ?

- a) $k$ ne peut pas être prolongée par continuité en $1$, car $\ln|x-1|$ tend vers $-\infty$.
- b) $k$ ne peut pas être prolongée par continuité en $1$, car ses limites à gauche et à droite de $1$ sont différentes.
- c) $k$ se prolonge par continuité en $1$ en posant $k(1)=1$.
- d) $k$ se prolonge par continuité en $1$ en posant $k(1)=0$.

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On rappelle la limite de référence $\lim_{u\to0}u\ln|u|=0$ (croissances comparées), valable aussi bien quand $u$ tend vers $0$ par valeurs positives que par valeurs négatives. Face à une expression de la forme $(x-x_0)\ln|x-x_0|$, on pose $u=x-x_0$ pour se ramener à cette limite usuelle.

### Corrigé

En $x=1$, $\ln|x-1|$ n'est pas défini : la formule prend la forme indéterminée $0\times(-\infty)$.

Posons $u=x-1$ : $k(x)=u\ln|u|$.

**Si $x\to1^{+}$** : $u\to0^{+}$ et $\displaystyle\lim_{u\to0^{+}}u\ln u=0$.

**Si $x\to1^{-}$** : $u\to0^{-}$ ; en posant $v=-u>0$, $u\ln|u|=-v\ln v$, qui tend vers $0$.

Les deux limites latérales valent $0$, donc $\displaystyle\lim_{x\to1}k(x)=0$ : on prolonge $k$ par continuité en $1$ en posant $k(1)=0$.

### Pourquoi les autres réponses sont fausses

- **a)** $\ln|x-1|$ tend bien vers $-\infty$, mais il est multiplié par $x-1$, qui tend vers $0$ : c'est une forme indéterminée, et le facteur $x-1$ l'emporte.
- **b)** Les limites à gauche et à droite sont toutes deux nulles ; on a oublié la valeur absolue en croyant que $\ln(x-1)$ n'existe pas à gauche.
- **c)** $1$ vient d'une confusion avec $\lim_{u\to0}\dfrac{\ln(1+u)}{u}=1$.

</details>

Avis : 

---

## 67. `cqc-prolongement-par-continuite-moyenne-2` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $p$ la fonction définie par $p(x) = \dfrac{e^x-1}{x}$ pour tout réel $x \neq 0$.

Parmi les affirmations suivantes, laquelle est exacte ?

- a) $p$ se prolonge par continuité en $0$ en posant $p(0)=1$.
- b) $p$ se prolonge par continuité en $0$ en posant $p(0)=0$.
- c) $p$ se prolonge par continuité en $0$ en posant $p(0)=e$.
- d) $p$ ne peut pas être prolongée par continuité en $0$, car la formule donne $\dfrac00$.

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Un taux d'accroissement $\dfrac{\varphi(x)-\varphi(x_0)}{x-x_0}$ tend, quand $x\to x_0$, vers le nombre dérivé $\varphi'(x_0)$, à condition que $\varphi$ soit dérivable en $x_0$. Reconnaître une formule comme un taux d'accroissement déguisé permet de calculer sa limite à partir d'une dérivée déjà connue.

### Corrigé

En $x=0$, le dénominateur s'annule, et le numérateur aussi puisque $e^0-1=0$ : forme indéterminée $\dfrac{0}{0}$.

Posons $\varphi(x)=e^x$. Comme $\varphi(0)=1$, pour tout $x\neq0$ :
$$p(x)=\frac{\varphi(x)-\varphi(0)}{x-0}.$$
Or $\varphi$ est dérivable sur $\mathbb{R}$, de dérivée $\varphi'(x)=e^x$, donc :
$$\lim_{x\to0}p(x)=\varphi'(0)=e^0=1.$$

La limite est finie : on prolonge $p$ par continuité en $0$ en posant $p(0)=1$.

### Pourquoi les autres réponses sont fausses

- **b)** Le numérateur tend vers $0$, mais le dénominateur aussi : la forme $\dfrac00$ n'impose pas une limite nulle.
- **c)** $e$ vient d'une confusion entre $\varphi'(0)=e^0$ et $\varphi'(1)=e^1$.
- **d)** Une forme indéterminée $\dfrac00$ n'empêche pas le prolongement : il faut lever l'indétermination avant de conclure.

</details>

Avis : 

---

## 68. `cqc-proprietes-du-logarithme-moyenne-0` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère la fonction $\varphi$ définie sur $\left]0\,;\,+\infty\right[$ par $\varphi(x) = 2 + 5\ln(x)$.

Quelle est l'expression de $\varphi(4\sqrt{2})$ en fonction de $\ln 2$ ?

- a) $2+10\ln2$
- b) $2+\dfrac{25}{2}\ln2$
- c) $2+5\ln2$
- d) $2+\dfrac{15}{2}\ln2$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour exprimer une valeur de fonction en fonction d'un seul $\ln k$, on réécrit l'argument comme une puissance de $k$, y compris une puissance fractionnaire pour une racine carrée, puisque $\sqrt{k} = k^{1/2}$, puis on applique $\ln(a^{n}) = n\ln a$ (ou $\ln(ab)=\ln a+\ln b$).

### Corrigé

On écrit $4\sqrt{2} = 2^{2} \times 2^{1/2} = 2^{5/2}$, donc $\ln(4\sqrt{2}) = \dfrac{5}{2}\ln 2$. On retrouve ce résultat avec $\ln(4\sqrt2)=\ln4+\ln\sqrt2=2\ln2+\dfrac12\ln2$. Donc :
$$\varphi(4\sqrt{2}) = 2 + 5\times \dfrac{5}{2}\ln 2 = 2 + \dfrac{25}{2}\ln 2.$$

De la même façon : $\varphi(2) = 2+5\ln2$, $\varphi(\sqrt2) = 2+\dfrac{5}{2}\ln2$ et $\varphi\left(\dfrac{1}{4}\right) = 2-10\ln2$.

### Pourquoi les autres réponses sont fausses

- **a)** $2+10\ln2$ vient de $\ln(4\sqrt2)=\ln 4=2\ln2$ : on a oublié le facteur $\sqrt2$.
- **c)** $2+5\ln2$ vient de la multiplication des exposants ($2\times\dfrac12=1$) au lieu de leur addition.
- **d)** $2+\dfrac{15}{2}\ln2$ vient de l'écriture fausse $4=2^1$, d'où $4\sqrt2=2^{3/2}$.

</details>

Avis : 

---

## 69. `cqc-proprietes-du-logarithme-moyenne-1` (séries A)

**Énoncé :**

Quelle est la valeur exacte du réel suivant ?
$$C = \ln\left(\dfrac{1}{e^{-3}} + \dfrac{1}{e^{-1}}\right) - \ln\left(1+e^{2}\right)$$

- a) $-3$
- b) $0$
- c) $1$
- d) $4-\ln\left(1+e^{2}\right)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Avant de factoriser une somme de puissances de $e$ cachée derrière des quotients, on simplifie chaque quotient à l'aide de $\dfrac{1}{a^{-n}} = a^{n}$, afin de faire apparaître des puissances positives de $e$ que l'on peut factoriser, puis simplifier avec $\ln(ab)=\ln a+\ln b$ et $\ln(e)=1$.

### Corrigé

On simplifie les deux quotients : $\dfrac{1}{e^{-3}} = e^{3}$ et $\dfrac{1}{e^{-1}} = e$. L'expression entre parenthèses devient $e^{3} + e = e\left(e^{2}+1\right)$.

D'où :
$$\ln\left(e^{3}+e\right) = \ln(e) + \ln\left(e^{2}+1\right) = 1 + \ln\left(e^{2}+1\right).$$

On remplace dans $C$ :
$$C = \left[1+\ln\left(e^{2}+1\right)\right] - \ln\left(1+e^{2}\right) = 1.$$

### Pourquoi les autres réponses sont fausses

- **a)** $-3$ vient de l'erreur $\dfrac{1}{e^{-3}}=e^{-3}$ (et $\dfrac{1}{e^{-1}}=e^{-1}$) : on obtient alors $\ln\left(e^{-3}(1+e^2)\right)-\ln(1+e^2)=-3$.
- **b)** $0$ vient de l'oubli du facteur $e$ mis en évidence : on a cru que les deux logarithmes s'annulaient entièrement.
- **d)** $4-\ln(1+e^2)$ vient de la règle fausse $\ln(e^3+e)=\ln(e^3)+\ln(e)=3+1$ : le logarithme d'une somme n'est pas la somme des logarithmes.

</details>

Avis : 

---

## 70. `cqc-racine-double-moyenne-1` (séries C/D/E/TI)

**Remarque du relecteur :** LIMITE : pour les séries D et TI, le cas de la racine double de l'équation caractéristique est à la limite haute du programme d'équations différentielles du second ordre.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère l'équation différentielle $(E_4) : y'' - 10y' + 25y = 0$, où $y$ est une fonction deux fois dérivable sur $\mathbb{R}$.

Quelle est la solution de $(E_4)$ vérifiant $y(0) = 2$ et $y'(0) = 3$ ?

- a) $y(x)=(2+3x)e^{5x}$
- b) $y(x)=(2-7x)e^{5x}$
- c) $y(x)=(2+13x)e^{-5x}$
- d) $y(x)=(2+7x)e^{5x}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Lorsque l'équation caractéristique admet une racine double $r_0$, la solution générale $y = (C_1+C_2x)e^{r_0x}$ est un produit de deux fonctions de $x$ : il faut donc dériver avec la règle du produit pour obtenir $y'$, avant d'exploiter les conditions initiales sur $y(0)$ et $y'(0)$, qui forment alors un système linéaire en $C_1$ et $C_2$.

### Corrigé
L'équation caractéristique associée à $(E_4)$ est $r^2 - 10r + 25 = 0$, de discriminant $\Delta = 100 - 100 = 0$ : racine double $r_0 = \dfrac{10}{2} = 5$.
La solution générale de $(E_4)$ sur $\mathbb{R}$ est donc $y(x) = (C_1 + C_2x)e^{5x}$, $(C_1, C_2) \in \mathbb{R}^2$.

On dérive : $y'(x) = C_2e^{5x} + 5(C_1+C_2x)e^{5x}$.
Les conditions initiales donnent $y(0) = C_1 = 2$ et $y'(0) = 5C_1 + C_2 = 3$, soit $C_2 = 3-10 = -7$.

La solution cherchée est donc :
$$y(x) = (2 - 7x)e^{5x}.$$

### Pourquoi les autres réponses sont fausses

- **a)** $(2+3x)e^{5x}$ vient de l'oubli de la règle du produit : on a pris $y'(0)=C_2$ ; en réalité cette fonction vérifie $y'(0)=13$.
- **c)** $(2+13x)e^{-5x}$ vient d'une erreur de signe sur la racine ($r_0=-5$) : cette fonction n'est pas solution de $(E_4)$.
- **d)** $(2+7x)e^{5x}$ vient d'une erreur de signe dans $3-10$ : cette fonction vérifie $y'(0)=17$.

</details>

Avis : 

---

## 71. `cqc-racine-double-moyenne-2` (séries C/D/E/TI)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Un ingénieur modélise l'amortissement d'un composant mécanique par l'équation différentielle $(E_5) : y'' + my' + 9y = 0$, où $y(t)$ désigne l'écart du composant par rapport à sa position d'équilibre à l'instant $t$, et où $m$ est un réel strictement positif représentant le coefficient d'amortissement du système. Le régime du composant est dit critique lorsque l'équation caractéristique associée à $(E_5)$ admet une racine double.

Dans le régime critique, quelle est la solution générale de $(E_5)$ sur $\mathbb{R}$ ($C_1$ et $C_2$ désignant des constantes réelles) ?

- a) $y(t)=(C_1+C_2t)e^{3t}$
- b) $y(t)=C_1e^{-3t}+C_2e^{3t}$
- c) $y(t)=(C_1+C_2t)e^{-3t}$
- d) $y(t)=(C_1+C_2t)e^{-6t}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Lorsqu'un coefficient d'une équation $y'' + ay' + by = 0$ dépend d'un paramètre, on retrouve la condition de racine double en écrivant que le discriminant $\Delta$ de l'équation caractéristique s'annule. On applique ensuite la formule $y = (C_1+C_2t)e^{r_0t}$, avec $r_0=-\dfrac{a}{2}$.

### Corrigé
L'équation caractéristique associée à $(E_5)$ est $r^2 + mr + 9 = 0$, de discriminant $\Delta = m^2 - 36$.
Le régime est critique lorsque $\Delta = 0$, soit $m = 6$ ou $m = -6$. Comme $m$ est strictement positif, $m = 6$.

Pour $m = 6$, l'équation caractéristique devient $r^2 + 6r + 9 = 0$, de racine double $r_0 = -\dfrac{6}{2} = -3$.
La solution générale de $(E_5)$ sur $\mathbb{R}$ est donc
$$y(t) = (C_1 + C_2t)e^{-3t}, \quad (C_1, C_2) \in \mathbb{R}^2.$$

### Pourquoi les autres réponses sont fausses

- **a)** $(C_1+C_2t)e^{3t}$ vient d'une erreur de signe : la racine double de $r^2+6r+9$ est $-3$, et non $3$.
- **b)** $C_1e^{-3t}+C_2e^{3t}$ mélange les deux valeurs $m=\pm6$ et applique la formule des racines distinctes, alors que la racine est double.
- **d)** $(C_1+C_2t)e^{-6t}$ vient de l'oubli de la division par $2$ : $r_0=-\dfrac{m}{2}$ et non $-m$.

</details>

Avis : 

---

## 72. `cqc-reduction-vectorielle-bac-ti-mat-elevee-2` (séries TI)

**Remarque du relecteur :** LIMITE : barycentre et ligne de niveau de M ↦ ΣαiMAi² en série TI, à confirmer au programme TI.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Le plan est muni d'un repère orthonormé. On considère les points $A(-2\,;1)$, $B(4\,;1)$ et $C(1\,;7)$.

Quel est l'ensemble $\Gamma$ des points $M$ du plan tels que $MA^2+MB^2+2MC^2=94$ ?

- a) Le cercle de centre $G(1\,;4)$ et de rayon $10$
- b) Le cercle de centre $G(1\,;4)$ et de rayon $\sqrt{40}$
- c) Le cercle de centre $G(1\,;4)$ et de rayon $\sqrt{\dfrac{47}{2}}$
- d) Le cercle de centre $G(1\,;4)$ et de rayon $\sqrt{10}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour des points pondérés $(A_i\,;\lambda_i)$ de somme $\lambda\neq0$ et de barycentre $G$, on a $\sum\lambda_i\overrightarrow{MA_i}=\lambda\overrightarrow{MG}$ et, d'après la formule de Leibniz, $\sum\lambda_iMA_i^2=\lambda MG^2+\sum\lambda_iGA_i^2$. Une somme de carrés de distances se ramène ainsi à une condition sur $MG^2$.

### Corrigé

La somme des coefficients est $1+1+2=4\neq0$ : le barycentre $G$ de $(A\,;1)$, $(B\,;1)$, $(C\,;2)$ existe, et
$$x_G=\dfrac{-2+4+2}{4}=1,\qquad y_G=\dfrac{1+1+14}{4}=4,$$
donc $G(1\,;4)$.

On calcule $GA^2=9+9=18$, $GB^2=9+9=18$ et $GC^2=0+9=9$. En écrivant $\overrightarrow{MA}=\overrightarrow{MG}+\overrightarrow{GA}$ (et de même pour $B$ et $C$), puis en développant avec les coefficients $1$, $1$ et $2$, le terme $2\,\overrightarrow{MG}\cdot\left(\overrightarrow{GA}+\overrightarrow{GB}+2\overrightarrow{GC}\right)$ est nul, d'où :
$$MA^2+MB^2+2MC^2=4MG^2+18+18+2\times9=4MG^2+54.$$

Alors $4MG^2+54=94\iff MG^2=10\iff MG=\sqrt{10}$.

L'ensemble $\Gamma$ est le cercle de centre $G(1\,;4)$ et de rayon $\sqrt{10}$.

Vérification avec $M=O(0\,;0)$ : $OA^2+OB^2+2OC^2=5+17+100=122$ et $4OG^2+54=4\times17+54=122$.

### Pourquoi les autres réponses sont fausses

- **a)** Le rayon $10$ vient de l'oubli de la racine carrée : $MG^2=10$ donne $MG=\sqrt{10}$.
- **b)** Le rayon $\sqrt{40}$ vient de l'oubli du coefficient $4$ devant $MG^2$ : on a écrit $MG^2=94-54$.
- **c)** Le rayon $\sqrt{\dfrac{47}{2}}$ vient de l'oubli de la constante $54$ : on a écrit $4MG^2=94$.

</details>

Avis : 

---

## 73. `cqc-reduction-vectorielle-bac-ti-mat-moyenne-1` (séries TI)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Le plan est muni d'un repère orthonormé. On considère les points $A(3\,;5)$, $B(1\,;1)$ et $C(3\,;3)$. Pour tout point $M$ du plan, on pose $\vec w=\overrightarrow{MA}-3\overrightarrow{MB}+2\overrightarrow{MC}$.

Quel est l'ensemble des points $M$ du plan vérifiant $\|\vec w\|=10$ ?

- a) Le plan tout entier
- b) Le cercle de centre $B$ et de rayon $10$
- c) L'ensemble vide
- d) Le cercle de centre $C$ et de rayon $5$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand la somme des coefficients d'une combinaison $\alpha\overrightarrow{MA}+\beta\overrightarrow{MB}+\gamma\overrightarrow{MC}$ est nulle, on exprime chaque vecteur issu de $M$ à partir d'un point fixe grâce à la relation de Chasles : les vecteurs en $M$ s'annulent entre eux et il reste un vecteur constant. Une condition sur sa norme est alors vraie pour tout point $M$ ou pour aucun.

### Corrigé

La somme des coefficients est $1-3+2=0$. Avec la relation de Chasles, $\overrightarrow{MA}=\overrightarrow{MB}+\overrightarrow{BA}$ et $\overrightarrow{MC}=\overrightarrow{MB}+\overrightarrow{BC}$, donc :

$$\vec w=(1-3+2)\overrightarrow{MB}+\overrightarrow{BA}+2\overrightarrow{BC}=\overrightarrow{BA}+2\overrightarrow{BC}.$$

Le vecteur $\vec w$ ne dépend pas de $M$. On a $\overrightarrow{BA}\,(2\,;4)$ et $\overrightarrow{BC}\,(2\,;2)$, donc $\vec w\,(6\,;8)$ et $\|\vec w\|=\sqrt{36+64}=10$.

Contrôle avec $M=O(0\,;0)$ : $\overrightarrow{OA}-3\overrightarrow{OB}+2\overrightarrow{OC}=(3-3+6\,;5-3+6)=(6\,;8)$.

La condition $\|\vec w\|=10$ est donc vérifiée par tous les points : l'ensemble cherché est le plan tout entier.

### Pourquoi les autres réponses sont fausses

- **b)** On a traité la combinaison comme si elle valait un multiple de $\overrightarrow{MB}$ ; or la somme des coefficients est nulle, $\vec w$ ne dépend pas de $M$ et il n'y a pas de cercle.
- **c)** L'ensemble vide correspond à une erreur de calcul de $\vec w$ (norme différente de $10$) ; ici $\|\vec w\|=10$ pour tout $M$.
- **d)** On a cherché un barycentre en ne gardant que le terme $2\overrightarrow{MC}$ ; aucun barycentre n'existe quand la somme des coefficients est nulle.

</details>

Avis : 

---

## 74. `cqc-repetition-d-epreuves-independantes-moyenne-3` (séries A/D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Un site internet affiche une bannière publicitaire à chaque visite. On admet qu'à chaque visite, indépendamment des autres, la probabilité qu'un visiteur clique sur cette bannière est $p=0{,}04$. On considère 20 visites effectuées par des internautes différents, dans les mêmes conditions et indépendamment les unes des autres.

Quelle est la probabilité qu'au moins un des 20 visiteurs clique sur la bannière ? (Valeur arrondie à $10^{-3}$ près.)

- a) $0{,}442$
- b) $0{,}558$
- c) $0{,}800$
- d) $1{,}000$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'une épreuve à deux issues, de probabilité $p$ pour l'événement considéré, est répétée $n$ fois de façon identique et indépendante, la probabilité qu'il ne se produise jamais est $(1-p)^n$ ; celle qu'il se produise au moins une fois s'obtient en passant à l'événement contraire : $P(\text{au moins une fois})=1-(1-p)^n$.

### Corrigé

Chaque visite est une épreuve à deux issues : « le visiteur clique » (probabilité $0{,}04$) ou « le visiteur ne clique pas » (probabilité $0{,}96$). Les 20 visites sont identiques et indépendantes.

« Aucun des 20 visiteurs ne clique » a pour probabilité $0{,}96^{20}\approx0{,}442$.

L'événement « au moins un clic » est le contraire de « aucun clic » :
$$P(\text{au moins un clic})=1-0{,}96^{20}\approx1-0{,}442002\approx0{,}558\ \text{(arrondi à }10^{-3}\text{ près)}.$$

### Pourquoi les autres réponses sont fausses

- **a)** $0{,}442$ est la probabilité qu'aucun visiteur ne clique : on a oublié de passer à l'événement contraire.
- **c)** $0{,}800$ vient de l'addition $20\times0{,}04$ : les probabilités ne s'additionnent pas pour des événements qui ne sont pas incompatibles.
- **d)** $1{,}000$ vient de la confusion entre $p$ et $1-p$ : on a calculé $1-0{,}04^{20}$ au lieu de $1-0{,}96^{20}$.

</details>

Avis : 

---

## 75. `cqc-repetition-d-epreuves-independantes-moyenne-4` (séries A/D)

**Énoncé :**

Une tombola locale propose des billets dont la probabilité de faire gagner un lot est $p=0{,}1$ pour chaque billet acheté, indépendamment des autres billets. Un client achète $n$ billets, dans les mêmes conditions et indépendamment les uns des autres.

Quel est le plus petit entier $n$ tel que la probabilité de gagner au moins un lot parmi les $n$ billets soit supérieure ou égale à $0{,}9$ ?

- a) $21$
- b) $9$
- c) $22$
- d) $1$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour un événement de probabilité $p$ répété $n$ fois de façon identique et indépendante, $P(\text{au moins une fois})=1-(1-p)^n$. Déterminer le plus petit $n$ tel que cette probabilité atteigne un seuil revient à résoudre $(1-p)^n\leqslant 1-\text{seuil}$, puis à passer au logarithme népérien ; comme $1-p\in\,]0;1[$, on a $\ln(1-p)<0$, donc diviser par $\ln(1-p)$ inverse le sens de l'inégalité.

### Corrigé

La probabilité de ne gagner aucun lot parmi les $n$ billets est $0{,}9^n$, donc celle de gagner au moins un lot est $1-0{,}9^n$. On cherche le plus petit entier $n$ tel que :
$$1-0{,}9^n\geqslant 0{,}9 \iff 0{,}9^n\leqslant 0{,}1 \iff n\ln(0{,}9)\leqslant \ln(0{,}1).$$

Comme $\ln(0{,}9)<0$, diviser par $\ln(0{,}9)$ inverse le sens de l'inégalité :
$$n\geqslant \dfrac{\ln(0{,}1)}{\ln(0{,}9)}\approx21{,}85.$$

Le plus petit entier convenable est $n=22$.

Vérification : $0{,}9^{21}\approx0{,}109>0{,}1$, donc $n=21$ ne convient pas ; $0{,}9^{22}\approx0{,}098\leqslant0{,}1$, donc $n=22$ convient.

### Pourquoi les autres réponses sont fausses

- **a)** $21$ vient de la troncature de $21{,}85$ (ou de l'oubli du changement de sens de l'inégalité) : $n=21$ donne une probabilité d'environ $0{,}891<0{,}9$.
- **b)** $9$ vient de l'addition des probabilités ($n\times0{,}1\geqslant0{,}9$), qui n'est pas valable ici.
- **d)** $1$ vient de la confusion entre $p$ et $1-p$ : on a résolu $0{,}1^n\leqslant0{,}1$ au lieu de $0{,}9^n\leqslant0{,}1$.

</details>

Avis : 

---

## 76. `cqc-solution-generale-bac-ti-mat-elevee-2` (séries TI)

**Remarque du relecteur :** LIMITE : équation différentielle du second ordre avec second membre, solution particulière fournie ; à confirmer au programme TI.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère l'équation différentielle $(E)$ : $y''-2y'-8y=16x-4$, dont l'inconnue $y$ est une fonction deux fois dérivable sur $\mathbb{R}$, ainsi que la fonction $f$ : $x\mapsto-2x+1$, définie sur $\mathbb{R}$, dont on admet qu'elle est solution de $(E)$.

Quel est l'ensemble des solutions de $(E)$ sur $\mathbb{R}$ ? (Dans chaque proposition, $A$ et $B$ désignent des réels quelconques.)

- a) $y(x)=Ae^{-4x}+Be^{2x}-2x+1$
- b) $y(x)=Ae^{4x}+Be^{-2x}-2x+1$
- c) $y(x)=Ae^{4x}+Be^{-2x}$
- d) $y(x)=Ae^{4x}+Be^{-2x}+2x-1$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
La dérivation est linéaire : si $f$ est une solution connue de l'équation complète $(E)$, alors une fonction $y$ est solution de $(E)$ si et seulement si $y-f$ est solution de l'équation homogène $(E_0)$ : $y''-2y'-8y=0$. L'ensemble des solutions de $(E)$ s'obtient donc en ajoutant $f$ à la solution générale de $(E_0)$, laquelle se déduit des racines de l'équation caractéristique.

### Corrigé
**Vérification de $f$.** On a $f'(x)=-2$ et $f''(x)=0$, donc $f''(x)-2f'(x)-8f(x)=0+4-8(-2x+1)=16x-4$ : $f$ est bien solution de $(E)$.

**Réduction à l'équation homogène.** Pour une fonction $y$ deux fois dérivable, la linéarité de la dérivation donne :

$$(y-f)''-2(y-f)'-8(y-f)=\big(y''-2y'-8y\big)-(16x-4).$$

Cette expression est nulle si et seulement si $y''-2y'-8y=16x-4$. Ainsi $y$ est solution de $(E)$ si et seulement si $y-f$ est solution de $(E_0)$.

**Résolution de $(E_0)$.** L'équation caractéristique est $r^2-2r-8=0$ ; son discriminant vaut $\Delta=4+32=36=6^2$. Ses racines sont $r_1=\dfrac{2-6}{2}=-2$ et $r_2=\dfrac{2+6}{2}=4$. Les solutions de $(E_0)$ sont les fonctions $h(x)=Ae^{4x}+Be^{-2x}$, avec $A,B\in\mathbb{R}$.

**Conclusion.** Les solutions de $(E)$ sont les fonctions :

$$y(x)=Ae^{4x}+Be^{-2x}-2x+1,\qquad A,B\in\mathbb{R}.$$

Contrôle : pour $A=1$ et $B=3$, la fonction $g(x)=e^{4x}+3e^{-2x}-2x+1$ vérifie $g''-2g'-8g=(16-8-8)e^{4x}+(12+12-24)e^{-2x}+16x+4-8=16x-4$.

### Pourquoi les autres réponses sont fausses
- **a)** Les exposants ont le mauvais signe : $-4$ et $2$ sont les racines de $r^2+2r-8=0$, pas de l'équation caractéristique $r^2-2r-8=0$.
- **c)** C'est seulement la solution générale de l'équation homogène $(E_0)$ : on a oublié d'ajouter la solution particulière $f$.
- **d)** On a retranché $f$ au lieu de l'ajouter : $y-f=h$ donne $y=h+f$, et non $y=h-f$.

</details>

Avis : 

---

## 77. `cqc-solution-particuliere-moyenne-3` (séries C/D/E/TI)

**Remarque du relecteur :** LIMITE : équation différentielle du second ordre évoquée pour les séries D et TI ; la solution générale est donnée et seul un système 2×2 est à résoudre.

**Énoncé :**

On considère une fonction $g$, deux fois dérivable sur $\mathbb{R}$, solution d'une équation différentielle du second ordre $(E)$. On admet que la solution générale de $(E)$ s'écrit sous la forme
$$g(x) = A\,e^{3x} + B\,e^{-x},$$
où $A$ et $B$ sont deux réels à déterminer. On sait de plus que $g(0) = 4$ et $g'(0) = 0$.

Quelles sont les valeurs de $A$ et de $B$ ?

- a) $A=3$ et $B=1$
- b) $A=-2$ et $B=6$
- c) $A=1$ et $B=3$
- d) $A=2$ et $B=2$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand la solution générale d'une équation différentielle est déjà connue sous une forme dépendant de constantes réelles (ici $A$ et $B$), il n'est plus nécessaire de résoudre l'équation elle-même : il suffit d'exploiter les conditions initiales données (valeurs de $g$ et de $g'$ en un point) pour obtenir un système d'équations linéaires en $A$ et $B$, puis de le résoudre.

### Corrigé
On dérive $g$ : $g'(x) = 3A\,e^{3x} - B\,e^{-x}$.

La condition $g(0) = 4$ donne $A + B = 4$. La condition $g'(0) = 0$ donne $3A - B = 0$, soit $B = 3A$.

En remplaçant dans la première équation : $4A = 4$, donc $A = 1$, puis $B = 3$.

On a donc $A = 1$ et $B = 3$, c'est-à-dire $g(x) = e^{3x} + 3e^{-x}$.

Vérification : $g(0) = 1+3 = 4$ et $g'(0) = 3-3 = 0$.

### Pourquoi les autres réponses sont fausses
- **a)** Les valeurs de $A$ et de $B$ sont échangées : avec $A=3$ et $B=1$, on obtient $g'(0)=9-1=8\neq0$.
- **b)** Erreur de dérivation : la dérivée de $e^{-x}$ est $-e^{-x}$ ; en écrivant $g'(x)=3Ae^{3x}+Be^{-x}$, on résout $A+B=4$ et $3A+B=0$, ce qui donne $A=-2$ et $B=6$.
- **d)** Le facteur $3$ a été oublié en dérivant $e^{3x}$ : le système $A+B=4$ et $A-B=0$ donne $A=B=2$, mais alors $g'(0)=6-2=4\neq0$.

</details>

Avis : 

---

## 78. `cqc-stabilite-d-intervalle-bac-ti-mat-elevee-2` (séries TI)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Pour tout réel $x$, on pose $f(x)=1+e^{-x}$, et l'on note $I=[1\,;2]$.

Quelle est l'image $f(I)$ de l'intervalle $I$ par $f$ ?

- a) $[e^{-2}\,;e^{-1}]$
- b) $[1+e\,;1+e^{2}]$
- c) $[1+e^{-1}\,;1+e^{-2}]$
- d) $[1+e^{-2}\,;1+e^{-1}]$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand $f$ est décroissante sur $[a\,;b]$, l'image de cet intervalle est $[f(b)\,;f(a)]$ : les images des bornes sont échangées. La stabilité $f(I)\subset I$ exige alors $f(b)\ge a$ et $f(a)\le b$ ; une fois l'inclusion établie, un premier terme dans $I$ entraîne, par récurrence, que tous les termes d'une suite définie par $u_{n+1}=f(u_n)$ restent dans $I$.

### Corrigé
Pour tout réel $x$, $f'(x)=-e^{-x}<0$ : la fonction $f$ est strictement décroissante sur $\mathbb{R}$, et elle est continue.

Par conséquent :

$$f(I)=[f(2)\,;f(1)]=\left[1+e^{-2}\,;1+e^{-1}\right].$$

Avec $e^{-2}\approx0{,}135$ et $e^{-1}\approx0{,}368$, on obtient $f(I)\approx[1{,}135\,;1{,}368]$. Comme $1+e^{-2}>1$ et $1+e^{-1}<2$, on a $f(I)\subset I$ : l'intervalle $I$ est stable par $f$. Ainsi, pour la suite définie par $u_0=2$ et $u_{n+1}=f(u_n)$, une récurrence immédiate montre que $u_n\in I$ pour tout entier naturel $n$ ; par exemple $u_1=f(2)=1+e^{-2}\approx1{,}135$ est la borne inférieure de $f(I)$.

### Pourquoi les autres réponses sont fausses
- **a)** On a oublié la constante $1$ : $e^{-2}$ et $e^{-1}$ sont les images des bornes par $x\mapsto e^{-x}$, pas par $f$.
- **b)** Le signe moins de l'exposant a été perdu : $f(1)=1+e^{-1}$, et non $1+e$.
- **c)** Les bornes n'ont pas été échangées : $f$ étant décroissante, $f(1)=1+e^{-1}$ est la plus grande des deux images, et l'écriture $[1+e^{-1}\,;1+e^{-2}]$ ne désigne pas l'intervalle cherché.

</details>

Avis : 

---

## 79. `cqc-stabilite-d-intervalle-bac-ti-mat-moyenne-1` (séries TI)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On pose $f(x)=\ln(x+4)$ pour tout réel $x>-4$. On rappelle que $e\approx2{,}718$ et $e^{2}\approx7{,}389$. On dit qu'un intervalle $K$ inclus dans $]-4\,;+\infty[$ est stable par $f$ lorsque $f(K)\subset K$.

Parmi les intervalles suivants, lequel est stable par $f$ ?

- a) $[1\,;2]$
- b) $[0\,;1]$
- c) $[2\,;3]$
- d) $[-3\,;0]$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand $f$ est croissante sur $[a\,;b]$, l'image de cet intervalle est $[f(a)\,;f(b)]$ : l'inclusion $f([a\,;b])\subset[a\,;b]$ équivaut donc aux DEUX conditions $f(a)\ge a$ et $f(b)\le b$. Il faut vérifier les deux : une seule ne suffit pas.

### Corrigé
Pour tout $x>-4$, $f'(x)=\dfrac{1}{x+4}>0$ : la fonction $f$ est strictement croissante sur $]-4\,;+\infty[$.

Pour $[1\,;2]$ : $f([1\,;2])=[\ln5\,;\ln6]$. Or $5>e$, donc $\ln5>\ln e=1$ ; et $6<e^{2}\approx7{,}389$, donc $\ln6<\ln e^{2}=2$. Ainsi

$$f([1\,;2])=[\ln5\,;\ln6]\subset[1\,;2],$$

et l'intervalle $[1\,;2]$ est stable par $f$. Par récurrence, la suite définie par $u_0=1$ et $u_{n+1}=f(u_n)$ reste donc dans $[1\,;2]$ (contrôle : $u_1=\ln5\approx1{,}609$ et $u_2=\ln(u_1+4)\approx1{,}724$).

Pour les autres intervalles, une des deux conditions est en défaut :
- $[0\,;1]$ : $f(1)=\ln5>1$ ;
- $[2\,;3]$ : $f(2)=\ln6<2$ ;
- $[-3\,;0]$ : $f(0)=\ln4>0$ (car $4>1$).

### Pourquoi les autres réponses sont fausses
- **b)** Seule la condition sur la borne gauche est vérifiée ($f(0)=\ln4\ge0$) ; on a oublié de contrôler la borne droite : $f(1)=\ln5>1$.
- **c)** Seule la condition sur la borne droite est vérifiée ($f(3)=\ln7\le3$) ; mais $f(2)=\ln6<2$, donc $f([2\,;3])$ déborde à gauche de $[2\,;3]$.
- **d)** On a seulement remarqué que $f(-3)=\ln1=0\ge-3$ ; or $f(0)=\ln4>0$, donc $f([-3\,;0])=[0\,;\ln4]$ n'est pas inclus dans $[-3\,;0]$.

</details>

Avis : 

---

## 80. `cqc-statistique-a-deux-variables-moyenne-2` (séries A)

**Remarque du relecteur :** Calcul long sans calculatrice statistique pour un QCM ; la corrélation quasi nulle est cohérente avec le contexte.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Le service informatique d'une entreprise a relevé, sur 5 mois, la température moyenne extérieure, en °C ($x$), et le nombre de pannes signalées sur les ordinateurs de bureau ce mois-là ($y$) :

| Température moyenne, en °C ($x$) | 18 | 22 | 26 | 30 | 34 |
|---|---|---|---|---|---|
| Pannes informatiques signalées ($y$) | 12 | 7 | 14 | 6 | 11 |

Quelle est la valeur du coefficient de corrélation linéaire $r$ entre $x$ et $y$, arrondie au centième ?

- a) $-0{,}26$
- b) $0{,}14$
- c) $-0{,}14$
- d) $-0{,}70$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Le coefficient de corrélation linéaire se calcule par $r=\dfrac{\sum(x_i-\bar x)(y_i-\bar y)}{\sqrt{\sum(x_i-\bar x)^2\times\sum(y_i-\bar y)^2}}$ ; il prend des valeurs entre $-1$ et $1$. Quand $|r|$ est proche de $0$, la relation entre les deux variables n'est pas linéaire, ou n'existe pas : chercher un ajustement affine n'a alors pas de sens.

### Corrigé
$\bar x=\dfrac{18+22+26+30+34}{5}=\dfrac{130}{5}=26$ et $\bar y=\dfrac{12+7+14+6+11}{5}=\dfrac{50}{5}=10$.

Tableau d'écarts :

| $x_i$ | $x_i-\bar x$ | $y_i$ | $y_i-\bar y$ | $(x_i-\bar x)(y_i-\bar y)$ | $(x_i-\bar x)^2$ | $(y_i-\bar y)^2$ |
|---|---|---|---|---|---|---|
| 18 | -8 | 12 | 2 | -16 | 64 | 4 |
| 22 | -4 | 7 | -3 | 12 | 16 | 9 |
| 26 | 0 | 14 | 4 | 0 | 0 | 16 |
| 30 | 4 | 6 | -4 | -16 | 16 | 16 |
| 34 | 8 | 11 | 1 | 8 | 64 | 1 |
| Somme | | | | -12 | 160 | 46 |

$$r=\dfrac{-12}{\sqrt{160\times46}}=\dfrac{-12}{\sqrt{7360}}\approx\dfrac{-12}{85{,}79}\approx-0{,}14\quad\text{(arrondi au centième)}.$$

Avec $r\approx-0{,}14$, très proche de $0$, il n'existe pratiquement aucune corrélation linéaire entre la température du mois et le nombre de pannes : un ajustement affine ne serait pas pertinent pour prévoir les pannes.

### Pourquoi les autres réponses sont fausses
- **a)** On a divisé $-12$ par la seule somme $\sum(y_i-\bar y)^2=46$, sans racine carrée ni produit : $-\dfrac{12}{46}\approx-0{,}26$.
- **b)** Erreur de signe : la somme des produits d'écarts vaut $-12$, donc $r$ est négatif.
- **d)** On a mélangé sommes et moyennes : la somme $-12$ (non divisée par $5$) est divisée par le produit des écarts types $\sqrt{32}\times\sqrt{9{,}2}\approx17{,}16$, ce qui donne $\approx-0{,}70$.

</details>

Avis : 

---

## 81. `cqc-equation-differentielle-faible-0` (séries C/D/E/TI)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère l'équation différentielle $(E) : y'' - 3y' + 2y = 0$, où $y$ est une fonction deux fois dérivable sur $\mathbb{R}$.

Quelle est la solution de $(E)$ vérifiant $y(0) = 3$ et $y'(0) = 4$ ?

- a) $y(x)=2e^{2x}+e^{x}$
- b) $y(x)=10e^{-x}-7e^{-2x}$
- c) $y(x)=5e^{x}-e^{2x}$
- d) $y(x)=e^{2x}+2e^{x}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour une équation $y'' + ay' + by = 0$ à coefficients constants, on forme l'équation caractéristique $r^2 + ar + b = 0$. Si le discriminant est strictement positif, elle admet deux racines réelles distinctes $r_1$ et $r_2$, et la solution générale s'écrit $y = A e^{r_1 x} + B e^{r_2 x}$. Les constantes $A$ et $B$ se déterminent ensuite grâce aux conditions initiales sur $y$ et $y'$.

### Corrigé
L'équation caractéristique associée à $(E)$ est $r^2 - 3r + 2 = 0$. Son discriminant vaut $\Delta = (-3)^2 - 4\times 1\times 2 = 1 > 0$. Les racines sont $r_1 = \dfrac{3-1}{2} = 1$ et $r_2 = \dfrac{3+1}{2} = 2$.

La solution générale de $(E)$ est donc $y(x) = A e^{2x} + B e^{x}$, avec $(A, B) \in \mathbb{R}^2$.

On a $y'(x) = 2A e^{2x} + B e^{x}$. Les conditions initiales donnent le système :
$$\begin{cases} A + B = 3 \\ 2A + B = 4 \end{cases}$$
En soustrayant la première équation à la seconde : $A = 1$, d'où $B = 2$.

La solution cherchée est :
$$y(x) = e^{2x} + 2e^{x}.$$

### Pourquoi les autres réponses sont fausses
- **a)** Les coefficients ont été attribués aux mauvaises exponentielles : $y(x)=2e^{2x}+e^{x}$ donne $y'(0)=4+1=5\neq4$.
- **b)** L'équation caractéristique a été écrite $r^2+3r+2=0$ (erreur de signe), de racines $-1$ et $-2$ ; cette fonction vérifie bien les conditions initiales mais n'est pas solution de $(E)$.
- **c)** Les deux conditions ont été échangées : cette fonction vérifie $y(0)=4$ et $y'(0)=3$.

</details>

Avis : 

---

## 82. `cqc-equation-diophantienne-elevee-0` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère l'équation
$$(E): 137x-44y=15,$$
où $x$ et $y$ désignent des entiers relatifs.

Quel est l'ensemble des couples $(x;y)$ d'entiers relatifs solutions de $(E)$ ? (Dans chaque proposition, $k$ décrit $\mathbb Z$.)

- a) $\{(3+44k\,;\,9+137k)\}$
- b) $\{(3+137k\,;\,9+44k)\}$
- c) $\{(3-44k\,;\,9+137k)\}$
- d) $\{(9+44k\,;\,3+137k)\}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
La résolution complète d'une équation $ax-by=c$ suit toujours le même schéma : calcul de $\mathrm{pgcd}(a;b)$ par l'algorithme d'Euclide (qui doit diviser $c$ pour garantir l'existence de solutions), remontée de cet algorithme pour obtenir une égalité de Bézout puis un couple particulier par multiplication, et enfin application du théorème de Gauss pour établir la solution générale, dont les deux composantes sont liées par un même paramètre entier $k$.

### Corrigé
**Calcul du pgcd.** Algorithme d'Euclide :
$$137=3\times44+5,\qquad 44=8\times5+4,\qquad 5=1\times4+1,\qquad 4=4\times1+0.$$
Le dernier reste non nul est $1$, donc $\mathrm{pgcd}(137;44)=1$. Comme $1$ divise $15$, l'équation $(E)$ admet des solutions entières.

**Remontée de l'algorithme (Bézout).**
$$1=5-4=5-(44-8\times5)=9\times5-44=9\times(137-3\times44)-44=9\times137-28\times44.$$
En multipliant par $15$ : $137\times135-44\times420=15$. Le couple $(135;420)$ est une solution particulière ; en retranchant $3\times44$ à $135$ et $3\times137$ à $420$, on obtient le couple plus simple $(x_0;y_0)=(3;9)$. Vérification : $137\times3-44\times9=411-396=15$.

**Solution générale.** $(x;y)$ est solution de $(E)$ si et seulement si $137(x-3)=44(y-9)$. Comme $\mathrm{pgcd}(137;44)=1$, le théorème de Gauss donne : $44$ divise $x-3$, donc $x=3+44k$ avec $k\in\mathbb Z$. En reportant : $137\times44k=44(y-9)$, donc $y=9+137k$.

Réciproquement, pour tout $k\in\mathbb Z$ : $137(3+44k)-44(9+137k)=411-396=15$.

L'ensemble des solutions de $(E)$ est donc $\{(3+44k\,;\,9+137k),\ k\in\mathbb Z\}$.

### Pourquoi les autres réponses sont fausses
- **b)** Les périodes sont échangées : dans $137(x-3)=44(y-9)$, c'est $44$ qui divise $x-3$ (Gauss), et non $137$.
- **c)** Erreur de signe : en reportant $x-3=-44k$, il faut aussi $y-9=-137k$ ; les deux paramètres doivent varier dans le même sens, comme le montre l'égalité $137(x-3)=44(y-9)$.
- **d)** Les composantes de la solution particulière sont inversées : $137\times9-44\times3=1101\neq15$.

</details>

Avis : 

---

## 83. `cqc-equation-diophantienne-faible-0` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On admet l'égalité suivante liant les entiers $45$ et $13$ :
$$7\times13-2\times45=1.$$
On considère l'équation $(E): 45u+13v=4$, où $u$ et $v$ désignent des entiers relatifs.

Parmi les couples suivants, lequel est solution de $(E)$ ?

- a) $(-2\,;7)$
- b) $(-8\,;28)$
- c) $(28\,;-8)$
- d) $(8\,;-28)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Lorsqu'une égalité de Bézout $a\alpha+b\beta=1$ entre deux entiers $a$ et $b$ est déjà établie, il est inutile de refaire l'algorithme d'Euclide pour résoudre $au+bv=c$ : il suffit de multiplier chaque membre de l'égalité par $c$. Le couple $(c\alpha;c\beta)$ obtenu est alors une solution particulière immédiate de l'équation. Attention à l'ordre : $\alpha$ est le coefficient de $a$, $\beta$ celui de $b$.

### Corrigé
L'égalité admise, $7\times13-2\times45=1$, se réécrit en faisant apparaître $45$ et $13$ dans l'ordre de $(E)$ :
$$45\times(-2)+13\times7=1.$$
On multiplie les deux membres par $4$ :
$$45\times(-8)+13\times28=4.$$
Le couple $(u_0;v_0)=(-8;28)$ est donc solution de $(E)$.

Vérification : $45\times(-8)+13\times28=-360+364=4$.

### Pourquoi les autres réponses sont fausses
- **a)** On a oublié de multiplier par $4$ : $45\times(-2)+13\times7=1\neq4$.
- **c)** Les composantes sont dans le mauvais ordre : $28$ est le coefficient associé à $13$, pas à $45$ ; on trouve $45\times28+13\times(-8)=1156\neq4$.
- **d)** Erreur de signe en réécrivant l'égalité : $45\times8+13\times(-28)=-4$.

</details>

Avis : 

---

## 84. `cqc-equation-diophantienne-faible-1` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère l'équation $(E): 9x-4y=5$, où $x$ et $y$ désignent des entiers relatifs.

Quel est l'ensemble des couples $(x;y)$ d'entiers relatifs solutions de $(E)$ ? (Dans chaque proposition, $k$ décrit $\mathbb Z$.)

- a) $\{(1+9k\,;\,1+4k)\}$
- b) $\{(1+4k\,;\,1-9k)\}$
- c) $\{(1+4k\,;\,1+9k)\}$
- d) $\{(1+4k\,;\,-1+9k)\}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand les coefficients d'une équation $ax-by=c$ sont petits, il est souvent plus rapide de chercher une solution particulière par tâtonnement (en testant quelques valeurs de $x$ comprises entre $0$ et $b-1$) plutôt que de dérouler tout l'algorithme d'Euclide. Une fois un couple particulier connu, la solution générale s'obtient par soustraction membre à membre, puis par le théorème de Gauss.

### Corrigé
**Existence.** $9=2\times4+1$, puis $4=4\times1+0$ : $\mathrm{pgcd}(9;4)=1$, qui divise $5$, donc $(E)$ admet des solutions entières.

**Couple particulier.** Pour $x=1$ : $9-4y=5\iff y=1$. Le couple $(x_0;y_0)=(1;1)$ est solution : $9\times1-4\times1=5$.

**Solution générale.** $(x;y)$ est solution de $(E)$ si et seulement si $9(x-1)=4(y-1)$. Comme $\mathrm{pgcd}(9;4)=1$, le théorème de Gauss donne : $4$ divise $x-1$, donc $x=1+4k$ avec $k\in\mathbb Z$. En reportant, $9\times4k=4(y-1)$, donc $y=1+9k$.

Réciproquement, pour tout $k\in\mathbb Z$ : $9(1+4k)-4(1+9k)=9-4=5$.

L'ensemble des solutions de $(E)$ est donc $\{(1+4k\,;\,1+9k),\ k\in\mathbb Z\}$.

### Pourquoi les autres réponses sont fausses
- **a)** Les périodes sont échangées : dans $9(x-1)=4(y-1)$, c'est $4$ qui divise $x-1$, pas $9$.
- **b)** Erreur de signe : de $9\times4k=4(y-1)$ on tire $y-1=9k$, et non $-9k$.
- **d)** La solution particulière est fausse : $9\times1-4\times(-1)=13\neq5$.

</details>

Avis : 

---

## 85. `cqc-equation-diophantienne-moyenne-0` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère l'équation $(E): 41x-15y=5$, où $x$ et $y$ désignent des entiers relatifs.

Quel est l'ensemble des couples $(x;y)$ d'entiers relatifs solutions de $(E)$ ? (Dans chaque proposition, $k$ décrit $\mathbb Z$.)

- a) $\{(10+41k\,;\,27+15k)\}$
- b) $\{(20+15k\,;\,55+41k)\}$
- c) $\{(10+15k\,;\,27-41k)\}$
- d) $\{(10+15k\,;\,27+41k)\}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour résoudre $ax-by=c$ : on calcule $\mathrm{pgcd}(a;b)$ par l'algorithme d'Euclide, qui doit diviser $c$ pour que $(E)$ ait des solutions ; on remonte ensuite cet algorithme pour obtenir une égalité de Bézout, que l'on multiplie par $c/\mathrm{pgcd}(a;b)$ pour obtenir un couple particulier ; enfin, le théorème de Gauss permet d'établir la solution générale.

### Corrigé
**Calcul du pgcd.**
$$41=2\times15+11,\quad 15=1\times11+4,\quad 11=2\times4+3,\quad 4=1\times3+1,\quad 3=3\times1+0.$$
Donc $\mathrm{pgcd}(41;15)=1$, qui divise $5$ : $(E)$ admet des solutions entières.

**Remontée (Bézout).**
$$1=4-3=3\times4-11=3\times15-4\times11=11\times15-4\times41,$$
soit $41\times(-4)-15\times(-11)=1$. En multipliant par $5$ : $41\times(-20)-15\times(-55)=5$. En ajoutant deux fois $15$ à $-20$ et deux fois $41$ à $-55$, on obtient le couple plus simple $(x_0;y_0)=(10;27)$. Vérification : $41\times10-15\times27=410-405=5$.

**Solution générale.** $(x;y)$ est solution de $(E)$ si et seulement si $41(x-10)=15(y-27)$. Comme $\mathrm{pgcd}(41;15)=1$, le théorème de Gauss donne : $15$ divise $x-10$, donc $x=10+15k$, $k\in\mathbb Z$, puis $y=27+41k$.

Réciproquement, pour tout $k\in\mathbb Z$ : $41(10+15k)-15(27+41k)=410-405=5$.

L'ensemble des solutions de $(E)$ est donc $\{(10+15k\,;\,27+41k),\ k\in\mathbb Z\}$.

### Pourquoi les autres réponses sont fausses
- **a)** Les périodes sont échangées : c'est $15$ qui divise $x-10$, et $41$ qui divise $y-27$.
- **b)** Erreur de signe dans l'égalité de Bézout : le couple $(20;55)$ vérifie $41\times20-15\times55=-5$, et non $5$.
- **c)** Erreur de signe : les deux composantes doivent varier dans le même sens, puisque $41(x-10)=15(y-27)$.

</details>

Avis : 

---

## 86. `cqc-equation-diophantienne-moyenne-1` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère l'équation $(E): x^2=8y+4$, où $x$ et $y$ désignent des entiers relatifs.

Quel est l'ensemble des couples $(x;y)$ d'entiers relatifs solutions de $(E)$ ? (Dans chaque proposition, $k$ décrit $\mathbb Z$.)

- a) $\{(4k+2\,;\,2k(k+1))\}$
- b) $\{(4k+2\,;\,2k^2)\}$
- c) $\{(8k+2\,;\,8k^2+4k)\}$
- d) $\{(4k+2\,;\,4k^2+4k)\}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Une équation de la forme $x^2=my+r$ se résout en traduisant l'égalité par une congruence $x^2\equiv r\,[m]$, puis en déterminant, par disjonction des restes possibles, la ou les classes de $x$ qui vérifient cette congruence. On paramètre ensuite $x$ par un entier $k$ et on calcule $y$ en fonction de $k$, en vérifiant que l'expression obtenue est toujours entière.

### Corrigé
**Congruence.** $(E)$ s'écrit $x^2-4=8y$, c'est-à-dire $x^2\equiv4\,[8]$.

On écrit $x=4m+r$ avec $r\in\{0\,;1\,;2\,;3\}$ ; alors $x^2=16m^2+8mr+r^2\equiv r^2\,[8]$ :
- $x\equiv0\,[4]$ : $x^2\equiv0\,[8]$ ;
- $x\equiv1\,[4]$ : $x^2\equiv1\,[8]$ ;
- $x\equiv2\,[4]$ : $x^2\equiv4\,[8]$ ;
- $x\equiv3\,[4]$ : $x^2\equiv9\equiv1\,[8]$.

Donc $(E)\iff x\equiv2\,[4]$.

**Expression de $y$.** Posons $x=4k+2$, $k\in\mathbb Z$. Alors $x^2=16k^2+16k+4$, donc
$$y=\frac{x^2-4}{8}=\frac{16k^2+16k}{8}=2k^2+2k=2k(k+1),$$
qui est bien un entier pour tout $k$.

L'ensemble des solutions de $(E)$ est $\{(4k+2\,;\,2k(k+1)),\ k\in\mathbb Z\}$. Vérification : $8\times2k(k+1)+4=16k^2+16k+4=(4k+2)^2$.

### Pourquoi les autres réponses sont fausses
- **b)** Le double produit a été oublié dans le développement : $(4k+2)^2=16k^2+16k+4$, et non $16k^2+4$.
- **c)** On n'a retenu que $x\equiv2\,[8]$ et oublié les entiers $x\equiv6\,[8]$, eux aussi solutions : par exemple $(6;4)$ vérifie $36=8\times4+4$ mais n'est pas de cette forme.
- **d)** On a divisé $x^2-4$ par $4$ au lieu de $8$ : pour $k=1$, on obtient $(6;8)$, or $8\times8+4=68\neq36$.

</details>

Avis : 

---

## 87. `cqc-equation-diophantienne-moyenne-2` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On admet l'égalité suivante entre les entiers $58$ et $21$ :
$$4\times58-11\times21=1.$$
On considère l'équation $(E): 58u+21v=6$, où $u$ et $v$ désignent des entiers relatifs.

Quel est l'ensemble des couples $(u;v)$ d'entiers relatifs solutions de $(E)$ ? (Dans chaque proposition, $k$ décrit $\mathbb Z$.)

- a) $\{(24+58k\,;\,-66-21k)\}$
- b) $\{(24+21k\,;\,-66-58k)\}$
- c) $\{(24+21k\,;\,-66+58k)\}$
- d) $\{(4+21k\,;\,-11-58k)\}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand une égalité de Bézout entre deux entiers est déjà connue, on l'exploite directement par multiplication pour obtenir une solution particulière de $au+bv=c$, sans refaire l'algorithme d'Euclide. La solution générale s'obtient ensuite en soustrayant l'égalité particulière à $(E)$, puis en appliquant le théorème de Gauss (les deux coefficients étant premiers entre eux).

### Corrigé
**Couple particulier.** L'égalité admise se réécrit $58\times4+21\times(-11)=1$. En multipliant par $6$ :
$$58\times24+21\times(-66)=6.$$
Le couple $(u_0;v_0)=(24;-66)$ est solution de $(E)$ : $1392-1386=6$.

**Solution générale.** $(u;v)$ est solution de $(E)$ si et seulement si $58(u-24)=21(-66-v)$. L'égalité de Bézout admise montre que $\mathrm{pgcd}(58;21)=1$ ; le théorème de Gauss donne alors : $21$ divise $u-24$, donc $u=24+21k$ avec $k\in\mathbb Z$. En reportant : $58\times21k=21(-66-v)$, donc $v=-66-58k$.

Réciproquement, pour tout $k\in\mathbb Z$ : $58(24+21k)+21(-66-58k)=1392-1386=6$.

L'ensemble des solutions de $(E)$ est donc $\{(24+21k\,;\,-66-58k),\ k\in\mathbb Z\}$.

### Pourquoi les autres réponses sont fausses
- **a)** Les périodes sont échangées : c'est $21$ qui divise $u-24$, et $58$ qui intervient dans $v$.
- **c)** Erreur de signe : pour l'équation $58u+21v=6$ (avec un signe plus), quand $u$ augmente de $21$, $v$ doit diminuer de $58$.
- **d)** On a oublié de multiplier l'égalité de Bézout par $6$ : le couple $(4;-11)$ vérifie $58u+21v=1$, et non $6$.

</details>

Avis : 

---

## 88. `cqc-equation-logarithmique-moyenne-1` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère l'équation, d'inconnue $x\in\left]0\,;\,+\infty\right[$ :
$$(\ln x)^3 - 5(\ln x)^2 + 2\ln x + 8 = 0.$$
On pose $t=\ln x$, et l'on admet que $t=-1$ est une racine du polynôme $t^3-5t^2+2t+8$.

Quel est l'ensemble des solutions de cette équation ?

- a) $S=\{-1\,;\,2\,;\,4\}$
- b) $S=\left\{e^{2}\,;\,e^{4}\right\}$
- c) $S=\left\{e^{-1}\,;\,e^{2}\,;\,e^{4}\right\}$
- d) $S=\left\{e\,;\,e^{-2}\,;\,e^{-4}\right\}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour une équation ne faisant intervenir $x$ qu'à travers $\ln x$, on pose $t=\ln x$ pour obtenir un polynôme en $t$. Lorsque ce polynôme est de degré 3 et qu'une racine est connue, on le factorise par le facteur linéaire correspondant, puis on résout le facteur du second degré par le discriminant. Chaque racine $t$ redonne ensuite une solution $x=e^{t}$, automatiquement strictement positive.

### Corrigé
Avec $t=\ln x$, l'équation devient $t^3 - 5t^2 + 2t + 8 = 0$.

Pour $t=-1$ : $-1-5-2+8=0$, donc $(t+1)$ divise le polynôme. Par identification des coefficients :
$$t^3-5t^2+2t+8 = (t+1)(t^2-6t+8).$$

Pour $t^2-6t+8$ : $\Delta = 36-32=4$, d'où $t = \dfrac{6-2}{2} = 2$ ou $t = \dfrac{6+2}{2} = 4$.

Les trois racines sont $t \in \{-1\,;\,2\,;\,4\}$. On revient à $x$ par $x=e^{t}$ :

$$S=\left\{e^{-1}\,;\,e^{2}\,;\,e^{4}\right\}.$$

### Pourquoi les autres réponses sont fausses
- **a)** Ce sont les valeurs de $t=\ln x$ : on a oublié de revenir à l'inconnue $x$ par $x=e^{t}$.
- **b)** La solution $e^{-1}$ a été rejetée à tort : $t=-1$ est négatif, mais $x=e^{-1}$ est bien strictement positif.
- **d)** Erreur de signe dans la factorisation (facteur $t-1$ au lieu de $t+1$) : $t=1$, $t=-2$ et $t=-4$ ne sont pas racines du polynôme.

</details>

Avis : 

---

## 89. `cqc-equation-logarithmique-moyenne-2` (séries A)

**Remarque du relecteur :** LIMITE : division d'un polynôme de degré 3 par (t+2) en série A, faisable mais exigeante.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On considère l'équation, d'inconnue $x\in\left]0\,;\,+\infty\right[$ :
$$(\ln x)^3 - 6(\ln x)^2 - \ln x + 30 = 0.$$
On pose $t=\ln x$, et l'on admet que $t=-2$ est une racine du polynôme $t^3-6t^2-t+30$.

Quel est l'ensemble des solutions de cette équation ?

- a) $S=\left\{e^{-2}\,;\,e^{3}\,;\,e^{5}\right\}$
- b) $S=\{-2\,;\,3\,;\,5\}$
- c) $S=\left\{e^{2}\,;\,e^{-3}\,;\,e^{-5}\right\}$
- d) $S=\left\{e^{3}\,;\,e^{5}\right\}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour une équation ne faisant intervenir $x$ qu'à travers $\ln x$, on pose $t=\ln x$ pour obtenir un polynôme en $t$. Face à un polynôme de degré 3 dont une racine est connue, on le factorise par le facteur linéaire correspondant, puis on résout le facteur du second degré par le discriminant. Chaque racine $t$ redonne une solution $x=e^{t}$, valable sans condition supplémentaire.

### Corrigé
Avec $t=\ln x$, l'équation devient $t^3 - 6t^2 - t + 30 = 0$.

Pour $t=-2$ : $-8-24+2+30=0$, donc $(t+2)$ divise le polynôme. Par identification des coefficients :
$$t^3-6t^2-t+30 = (t+2)(t^2-8t+15).$$

Pour $t^2-8t+15$ : $\Delta = 64-60=4$, d'où $t = \dfrac{8-2}{2} = 3$ ou $t = \dfrac{8+2}{2} = 5$.

Les trois racines sont $t \in \{-2\,;\,3\,;\,5\}$. On revient à $x$ par $x=e^{t}$ :

$$S=\left\{e^{-2}\,;\,e^{3}\,;\,e^{5}\right\}.$$

### Pourquoi les autres réponses sont fausses
- **b)** Ce sont les valeurs de $t=\ln x$ : on a oublié de revenir à $x$ par $x=e^{t}$.
- **c)** Erreur de signe dans la factorisation (facteur $t-2$ au lieu de $t+2$) : $t=2$ n'est pas racine, car $8-24-2+30=12\neq0$.
- **d)** La solution $e^{-2}$ a été rejetée à tort : $t=-2$ est négatif, mais $x=e^{-2}$ est bien strictement positif.

</details>

Avis : 

---

## 90. `cqc-equiprobabilite-moyenne-1` (séries D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Une urne contient $5$ boules blanches et $4$ boules noires. On tire simultanément $3$ boules, chaque tirage ayant la même probabilité. Quelle est la probabilité d'obtenir exactement $2$ boules blanches ?

- a) $\dfrac{5}{42}$
- b) $\dfrac{10}{63}$
- c) $\dfrac{100}{243}$
- d) $\dfrac{10}{21}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Un tirage simultané de $k$ objets parmi $n$ compte $\dbinom{n}{k}$ issues équiprobables ; on multiplie les choix indépendants pour compter les cas favorables.

### Corrigé
Cas possibles : $\dbinom93=84$.

Cas favorables (2 blanches parmi 5 et 1 noire parmi 4) : $\dbinom52\times\dbinom41=10\times4=40$.

$$P=\dfrac{40}{84}=\dfrac{10}{21}.$$

### Pourquoi les autres réponses sont fausses
- **a)** On a oublié de choisir la boule noire : $\dfrac{10}{84}=\dfrac{5}{42}$.
- **b)** On a calculé la probabilité d'un seul ordre (blanche, blanche, noire) : $\dfrac59\times\dfrac48\times\dfrac47=\dfrac{10}{63}$, en oubliant les $3$ positions possibles de la boule noire.
- **c)** On a traité le tirage comme s'il était avec remise : $3\times\left(\dfrac59\right)^2\times\dfrac49=\dfrac{100}{243}$.

</details>

Avis : 

---

## 91. `cqc-equiprobabilite-moyenne-2` (séries D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans une classe de $30$ élèves dont $12$ filles, on choisit au hasard deux délégués, chaque paire d'élèves ayant la même probabilité d'être choisie. Quelle est la probabilité qu'il y ait au moins une fille parmi eux ?

- a) $\dfrac{94}{145}$
- b) $\dfrac{51}{145}$
- c) $\dfrac{16}{25}$
- d) $\dfrac{72}{145}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour « au moins un », il est souvent plus simple de passer par l'événement contraire : $P(A)=1-P(\bar A)$.

### Corrigé
Cas possibles : $\dbinom{30}2=435$.

Événement contraire (aucune fille, donc deux garçons parmi $18$) : $\dbinom{18}2=153$ cas.

$$P=1-\dfrac{153}{435}=\dfrac{282}{435}=\dfrac{94}{145}.$$

### Pourquoi les autres réponses sont fausses
- **b)** C'est la probabilité de l'événement contraire (deux garçons) : on a oublié de la retrancher à $1$.
- **c)** On a raisonné comme si le même élève pouvait être choisi deux fois : $1-\left(\dfrac{18}{30}\right)^2=\dfrac{16}{25}$.
- **d)** C'est la probabilité d'avoir exactement une fille ($\dfrac{12\times18}{435}=\dfrac{72}{145}$) : on a oublié le cas de deux filles.

</details>

Avis : 

---

## 92. `cqc-evenement-contraire-moyenne-2` (séries D/TI)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Une urne contient 8 jetons indiscernables au toucher : 3 jetons marqués « 20 » et 5 jetons marqués « 50 ». On tire simultanément 3 jetons de cette urne, chaque tirage ayant la même probabilité, et on note $T$ la somme des valeurs inscrites sur les jetons tirés. Selon la composition du tirage, $T$ ne peut prendre que l'une des quatre valeurs 60, 90, 120 ou 150. Quelle est la probabilité que $T$ soit strictement inférieure à 150 ?

- a) $\dfrac{5}{28}$
- b) $\dfrac{23}{28}$
- c) $\dfrac{3}{4}$
- d) $\dfrac{387}{512}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand un événement porte sur une inégalité stricte au sein d'un ensemble fini de valeurs possibles, on identifie les valeurs EXCLUES par l'inégalité, qui forment l'événement contraire, puis on calcule $P = 1 - P(\text{valeurs exclues})$. Ici, une seule des quatre valeurs possibles de $T$ ne vérifie pas « $T<150$ » : c'est $T=150$.

### Corrigé
Le nombre total de tirages simultanés de 3 jetons parmi les 8 est
$$\binom{8}{3} = \dfrac{8\times7\times6}{3\times2\times1} = 56.$$

L'événement contraire de « $T<150$ » est « $T=150$ », c'est-à-dire que les 3 jetons tirés portent tous la valeur 50 :
$$\binom{5}{3} = 10, \qquad P(T=150) = \dfrac{10}{56} = \dfrac{5}{28}.$$

$$P(T<150) = 1 - \dfrac{5}{28} = \dfrac{23}{28} \approx 0{,}821.$$

### Pourquoi les autres réponses sont fausses
- **a)** C'est la probabilité de l'événement contraire $T=150$ : on a oublié de la retrancher à $1$.
- **c)** On a supposé les quatre valeurs de $T$ équiprobables ($3$ valeurs favorables sur $4$) : c'est faux, elles ne correspondent pas au même nombre de tirages.
- **d)** On a traité le tirage comme s'il était avec remise : $1-\left(\dfrac58\right)^3=\dfrac{387}{512}$.

</details>

Avis : 

---

## 93. `cqc-evenements-incompatibles-bac-a-elevee-2` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un lycée, $200$ élèves sont inscrits aux activités du mercredi : $70$ fréquentent le club de théâtre, $60$ le club de musique, et $24$ fréquentent les deux clubs. On choisit un élève au hasard parmi ces $200$, chaque élève ayant la même probabilité d'être choisi.

Quelle est la probabilité que l'élève choisi ne fréquente aucun des deux clubs ?

- a) $0{,}35$
- b) $0{,}53$
- c) $0{,}88$
- d) $0{,}47$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Deux événements sont incompatibles lorsque leur intersection est vide ; sinon, $P(A\cup B)=P(A)+P(B)-P(A\cap B)$. L'événement contraire de $E$ a pour probabilité $1-P(E)$.

### Corrigé
On note $T$ l'événement « l'élève fréquente le club de théâtre » et $M$ l'événement « l'élève fréquente le club de musique ». Chaque élève ayant la même probabilité d'être choisi, la probabilité d'un événement est son effectif divisé par $200$ :

$$P(T)=\dfrac{70}{200}=0{,}35,\qquad P(M)=\dfrac{60}{200}=0{,}30,\qquad P(T\cap M)=\dfrac{24}{200}=0{,}12.$$

Comme $24$ élèves fréquentent les deux clubs, $T$ et $M$ ne sont pas incompatibles ; on retranche donc l'intersection :

$$P(T\cup M)=0{,}35+0{,}30-0{,}12=0{,}53.$$

L'événement « aucun des deux clubs » est le contraire de $T\cup M$ :

$$P=1-0{,}53=0{,}47,$$

soit $94$ élèves sur $200$. Contrôle par les effectifs : $46$ élèves font seulement du théâtre, $36$ seulement de la musique, $24$ les deux, et $200-46-36-24=94$.

### Pourquoi les autres réponses sont fausses
- **a)** On a traité $T$ et $M$ comme incompatibles en oubliant de retrancher l'intersection : $1-(0{,}35+0{,}30)=0{,}35$.
- **b)** C'est la probabilité de $T\cup M$ (au moins un des deux clubs) : on a oublié de passer à l'événement contraire.
- **c)** On a pris le contraire de l'intersection, $1-0{,}12=0{,}88$, qui est la probabilité de ne pas fréquenter les deux clubs à la fois.

</details>

Avis : 

---

