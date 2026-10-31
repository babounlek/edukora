# Vague 4a Maths Probatoire (séries C, D, E) : 82 QCM à faire relire par l'enseignant (campagne B1)

Date : 2026-10-31. Sur 103 QCM convertis (151 questions étudiées, 48 écartées ou retirées), **82** vous sont soumis : ceux que le relecteur aveugle a assortis d'une remarque, ceux dont la question ou la méthode a été modifiée, et un tirage de 10 autres. Aucun n'est en ligne. Les 119 résolutions à l'aveugle ont toutes donné la clé ; 6 questions ont ensuite été retirées (5 sur la distance d'un point à un plan, 1 de niveau Seconde) et 10 autres par application de votre avis sur les matrices.

Votre avis de la vague 2 est appliqué : matrices, applications linéaires et noyau hors programme de Première C (10 questions retirées, à réaffecter à la série E seule dans une opération de cursus à part). Le cursus des questions conservées est celui déjà en ligne : aucun changement de série.

## Points à trancher (nouveaux)

1. **Produit scalaire et distances :** la distance d'un point à une droite (2 questions) et les lignes de niveau $MA^2-MB^2$ ou barycentre (3 questions) se résolvent en coordonnées, mais leur méthode classique passe par le produit scalaire, absent du référentiel. Gardées en C et E : à confirmer.
2. **Distance d'un point à un plan de l'espace :** les 5 questions sont retirées (vecteur normal, produit scalaire dans l'espace). Confirmer qu'elles relèvent bien de la Terminale.
3. **Séries statistiques doubles :** la régression linéaire (covariance) est-elle au programme de Première C et E ? (1 question)
4. **Bases du plan vectoriel :** 3 questions de coordonnées dans une base sont gardées, la base d'un endomorphisme est retirée avec les matrices. Confirmer.
5. **Limites hautes :** formule $\cos 3a$ avec factorisation de degré 3 ; suite $u_{n+1}-1=(u_n-1)^2$ de terme général $2^{2^n}$ ; seuil $0{,}9^n$ sans logarithme (calculatrice).
6. **Contextes :** des notes sur 30 (écart-type) au lieu de 20 ; le thème « Tangente » porte une question qui calcule $\tan(\pi/8)$ par duplication (à reclasser).

Pour chaque question : **OK**, **à corriger** (dire quoi), **à retirer**, ou **retirer la série X**.

## 1. `cqc-limite-d-une-fonction-rationnelle-faible-0` (séries C/E)

**Énoncé :**

Que vaut $\displaystyle\lim_{x\to+\infty}\dfrac{3x^2-5x+1}{x^2+4}$ ?

- a) $3$
- b) $\dfrac14$
- c) $1$
- d) $+\infty$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

En $\pm\infty$, une fraction rationnelle a la même limite que le quotient de ses termes de plus haut degré.

### Corrigé

Les termes de plus haut degré sont $3x^2$ et $x^2$ :
$$\lim_{x\to+\infty}\dfrac{3x^2-5x+1}{x^2+4}=\lim_{x\to+\infty}\dfrac{3x^2}{x^2}=3.$$

### Pourquoi les autres réponses sont fausses

- **b)** on a fait le quotient des termes constants, qui ne comptent pas en $+\infty$.
- **c)** on a gardé $\dfrac{x^2}{x^2}$ en oubliant le coefficient $3$ du numérateur.
- **d)** le numérateur tend vers $+\infty$, mais le dénominateur aussi : à degrés égaux, la limite est finie.

</details>

Avis : 

---

## 2. `cqc-tangente-prob-c-elevee-5` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Pour tout réel $m$, on considère la courbe $(C_m)$ de la fonction $f_m(x)=x^2+mx+1$ et la droite $(D):\ y=2x-3$. Pour quelles valeurs de $m$ la droite $(D)$ est-elle tangente à $(C_m)$ ?

- a) $m=2$ ou $m=-6$
- b) $m=-2$ ou $m=6$
- c) $m=6$ seulement
- d) $m=0$ ou $m=4$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Une droite est tangente à la parabole si l'équation $f_m(x)=2x-3$ a une racine double (discriminant nul) : l'abscisse du point de contact est cette racine double, et la pente $f_m'$ y vaut la pente de la droite.

### Corrigé

$f_m(x)=2x-3\iff x^2+(m-2)x+4=0$. La droite est tangente si le discriminant est nul : $(m-2)^2-16=0\iff m-2=\pm4\iff m=6$ ou $m=-2$. L'abscisse du contact est $x=-\dfrac{m-2}2$.

- $m=6$ : $x=-2$, $f_6(-2)=4-12+1=-7$ (et $2(-2)-3=-7$) : point $(-2\,;-7)$ ;
- $m=-2$ : $x=2$, $f_{-2}(2)=4-4+1=1$ (et $2\times2-3=1$) : point $(2\,;1)$.

Vérification des pentes : $f_6'(-2)=2(-2)+6=2$ et $f_{-2}'(2)=4-2=2$, égales à la pente de $(D)$.

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe en passant $2x$ dans le premier membre : on a écrit $x^2+(m+2)x+4=0$.
- **c)** on a oublié la solution $m-2=-4$ de l'équation $(m-2)^2=16$.
- **d)** discriminant mal calculé : on a écrit $(m-2)^2-4$ au lieu de $(m-2)^2-4\times1\times4$.

</details>

Avis : 

---

## 3. `cqc-tangente-prob-c-moyenne-3` (séries C/D/E)

**Énoncé :**

Soit $f(x)=\dfrac{2x-1}{x+1}$. Quelle est une équation de la tangente à la courbe de $f$ au point d'abscisse $1$ ?

- a) $y=\dfrac34x-\dfrac14$
- b) $y=\dfrac54x-\dfrac34$
- c) $y=\dfrac32x-1$
- d) $y=\dfrac34x+\dfrac54$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule $f'$ avec la formule du quotient $\dfrac{u'v-uv'}{v^2}$, puis $f(1)$ et $f'(1)$, et on applique $y=f(a)+f'(a)(x-a)$.

### Corrigé

$f'(x)=\dfrac{2(x+1)-(2x-1)}{(x+1)^2}=\dfrac3{(x+1)^2}$. $f(1)=\dfrac12$ et $f'(1)=\dfrac34$.
$$y=\dfrac12+\dfrac34(x-1)=\dfrac34x-\dfrac14.$$

### Pourquoi les autres réponses sont fausses

- **b)** formule du quotient mal appliquée : on a additionné $u'v+uv'$, d'où $f'(1)=\dfrac54$.
- **c)** on a oublié le carré au dénominateur de $f'$ : $f'(1)=\dfrac32$.
- **d)** erreur de signe : on a écrit $(x+1)$ au lieu de $(x-1)$ dans l'équation de la tangente.

</details>

Avis : 

---

## 4. `cqc-tangente-prob-c-moyenne-4` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

En utilisant $\tan2a=\dfrac{2\tan a}{1-\tan^2a}$, quelle est la valeur exacte de $\tan\dfrac\pi8$ ?

- a) $-1-\sqrt2$
- b) $\sqrt2-1$
- c) $1+\sqrt2$
- d) $\dfrac12$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On pose $t=\tan\dfrac\pi8$. Comme $2\times\dfrac\pi8=\dfrac\pi4$ et $\tan\dfrac\pi4=1$, la formule de duplication donne une équation du second degré en $t$ dont on retient la racine positive.

### Corrigé

Avec $t=\tan\dfrac\pi8>0$ (car $\dfrac\pi8$ est entre $0$ et $\dfrac\pi2$) : $1=\tan\dfrac\pi4=\dfrac{2t}{1-t^2}$, donc $1-t^2=2t$, soit $t^2+2t-1=0$. Le discriminant est $4+4=8$ et les racines sont $\dfrac{-2\pm2\sqrt2}2=-1\pm\sqrt2$. Comme $t>0$ :
$$\tan\dfrac\pi8=\sqrt2-1.$$

### Pourquoi les autres réponses sont fausses

- **a)** c'est la racine négative de l'équation ; or $\tan\dfrac\pi8>0$.
- **c)** erreur de signe en écrivant l'équation : $t^2-2t-1=0$ au lieu de $t^2+2t-1=0$.
- **d)** on a divisé $\tan\dfrac\pi4$ par $2$, comme si la tangente était proportionnelle à l'angle.

</details>

Avis : 

---

## 5. `cqc-angle-oriente-prob-c-elevee-5` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé direct, on considère $A(1\,;0)$, $B\left(-\dfrac12\,;\dfrac{\sqrt3}2\right)$ et $C\left(-\dfrac12\,;-\dfrac{\sqrt3}2\right)$, points du cercle trigonométrique de centre $O$. Quelle est une mesure de l'angle orienté $(\overrightarrow{AB},\overrightarrow{AC})$ ?

- a) $\dfrac{2\pi}3$
- b) $-\dfrac\pi3$
- c) $\dfrac\pi3$
- d) $\dfrac{5\pi}6$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour un point $M(\cos\theta\,;\sin\theta)$ du cercle trigonométrique, $(\overrightarrow{OA},\overrightarrow{OM})=\theta$ avec $A(1\,;0)$. L'angle inscrit $(\overrightarrow{AB},\overrightarrow{AC})$ se calcule avec les directions des vecteurs $\overrightarrow{AB}$ et $\overrightarrow{AC}$ ; il vaut la moitié de l'angle au centre $(\overrightarrow{OB},\overrightarrow{OC})$, modulo $\pi$.

### Corrigé

$B=(\cos\dfrac{2\pi}3\,;\sin\dfrac{2\pi}3)$ et $C=(\cos\dfrac{4\pi}3\,;\sin\dfrac{4\pi}3)$. Donc $(\overrightarrow{OB},\overrightarrow{OC})=\dfrac{4\pi}3-\dfrac{2\pi}3=\dfrac{2\pi}3\ [2\pi]$.

$\overrightarrow{AB}\left(-\dfrac32\,;\dfrac{\sqrt3}2\right)$ a pour direction $\dfrac{5\pi}6$ (car $\cos=-\dfrac{\sqrt3}2$, $\sin=\dfrac12$) et $\overrightarrow{AC}\left(-\dfrac32\,;-\dfrac{\sqrt3}2\right)$ a pour direction $-\dfrac{5\pi}6$, soit $\dfrac{7\pi}6$. Donc
$$(\overrightarrow{AB},\overrightarrow{AC})=\dfrac{7\pi}6-\dfrac{5\pi}6=\dfrac\pi3\ [2\pi].$$
Contrôle : $2(\overrightarrow{AB},\overrightarrow{AC})=\dfrac{2\pi}3=(\overrightarrow{OB},\overrightarrow{OC})$ (l'angle au centre est le double de l'angle inscrit).

### Pourquoi les autres réponses sont fausses

- **a)** c'est l'angle au centre $(\overrightarrow{OB},\overrightarrow{OC})$, double de l'angle inscrit.
- **b)** on a calculé $(\overrightarrow{AC},\overrightarrow{AB})$ : l'ordre des vecteurs a été inversé.
- **d)** c'est seulement la direction de $\overrightarrow{AB}$, on n'a pas fait la différence avec celle de $\overrightarrow{AC}$.

</details>

Avis : 

---

## 6. `cqc-angle-oriente-prob-c-moyenne-2` (séries C/E)

**Remarque du relecteur :** VOCABULAIRE : la formule « angles orientés de sommet » est maladroite ; dire plutôt que les angles orientés (AB,AC), (BC,BA), (CA,CB) mesurent tous pi/3.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Le triangle $ABC$ est équilatéral direct, c'est-à-dire que $(\overrightarrow{AB},\overrightarrow{AC})=\dfrac\pi3\ [2\pi]$ et que les angles orientés $(\overrightarrow{AB},\overrightarrow{AC})$, $(\overrightarrow{BC},\overrightarrow{BA})$, $(\overrightarrow{CA},\overrightarrow{CB})$ sont égaux. Quelle est une mesure de $(\overrightarrow{AB},\overrightarrow{BC})$ ?

- a) $\dfrac\pi3$
- b) $-\dfrac\pi3$
- c) $-\dfrac{2\pi}3$
- d) $\dfrac{2\pi}3$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour un triangle équilatéral direct, chaque angle $(\overrightarrow{AB},\overrightarrow{AC})$, $(\overrightarrow{BC},\overrightarrow{BA})$, $(\overrightarrow{CA},\overrightarrow{CB})$ mesure $\dfrac\pi3$. On utilise ensuite $(\vec u,-\vec v)=(\vec u,\vec v)+\pi$ et la relation de Chasles.

### Corrigé

$(\overrightarrow{BC},\overrightarrow{BA})=\dfrac\pi3\ [2\pi]$, donc $(\overrightarrow{BA},\overrightarrow{BC})=-\dfrac\pi3$.

Comme $\overrightarrow{AB}=-\overrightarrow{BA}$, $(\overrightarrow{AB},\overrightarrow{BC})=(\overrightarrow{AB},\overrightarrow{BA})+(\overrightarrow{BA},\overrightarrow{BC})=\pi-\dfrac\pi3=\dfrac{2\pi}3\ [2\pi]$.

Vérification avec $A(0\,;0)$, $B(1\,;0)$, $C\left(\dfrac12\,;\dfrac{\sqrt3}2\right)$ : $\overrightarrow{AB}$ a pour direction $0$ et $\overrightarrow{BC}\left(-\dfrac12\,;\dfrac{\sqrt3}2\right)$ a pour direction $\dfrac{2\pi}3$.

### Pourquoi les autres réponses sont fausses

- **a)** on a confondu $(\overrightarrow{AB},\overrightarrow{BC})$ avec l'angle de sommet $B$, $(\overrightarrow{BC},\overrightarrow{BA})$.
- **b)** on a donné $(\overrightarrow{BA},\overrightarrow{BC})$ en oubliant le $\pi$ dû au changement de sens $\overrightarrow{AB}=-\overrightarrow{BA}$.
- **c)** erreur de signe : on a pris $(\overrightarrow{BA},\overrightarrow{BC})=\dfrac\pi3$, d'où $\pi+\dfrac\pi3=\dfrac{4\pi}3$, soit $-\dfrac{2\pi}3$.

</details>

Avis : 

---

## 7. `cqc-angle-oriente-prob-c-moyenne-3` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

$ABCD$ est un carré direct (ses sommets sont parcourus dans le sens trigonométrique). Quelle est une mesure de l'angle orienté $(\overrightarrow{BA},\overrightarrow{BD})$ ?

- a) $-\dfrac\pi4$
- b) $\dfrac\pi4$
- c) $\dfrac{3\pi}4$
- d) $\dfrac\pi2$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On place le carré dans un repère orthonormé direct, par exemple $A(0\,;0)$, $B(1\,;0)$, $C(1\,;1)$, $D(0\,;1)$, et on lit la direction (mesure de l'angle avec l'axe des abscisses) de chaque vecteur : $(\vec u,\vec v)$ est la différence des directions de $\vec v$ et de $\vec u$.

### Corrigé

Directions : $\overrightarrow{BA}(-1\,;0)$ : $\pi$ ; $\overrightarrow{BD}(-1\,;1)$ : $\dfrac{3\pi}4$.
$$(\overrightarrow{BA},\overrightarrow{BD})=\dfrac{3\pi}4-\pi=-\dfrac\pi4\ [2\pi].$$
De même, on trouverait $(\overrightarrow{AB},\overrightarrow{AC})=\dfrac\pi4$ et $(\overrightarrow{DA},\overrightarrow{DC})=\dfrac\pi2$.

### Pourquoi les autres réponses sont fausses

- **b)** on a calculé $(\overrightarrow{BD},\overrightarrow{BA})$ : l'ordre des vecteurs a été inversé.
- **c)** c'est seulement la direction de $\overrightarrow{BD}$, sans retrancher celle de $\overrightarrow{BA}$.
- **d)** on a confondu avec l'angle droit du carré de sommet $B$.

</details>

Avis : 

---

## 8. `cqc-angles-associes-prob-c-elevee-5` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Calculer $S=\cos\dfrac\pi6+\cos\dfrac{2\pi}6+\cos\dfrac{3\pi}6+\cdots+\cos\dfrac{11\pi}6$ (onze termes).

- a) $0$
- b) $1$
- c) $-1$
- d) $2\sqrt3+1$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On regroupe les angles associés : $\cos(\pi-a)=-\cos a$ (deux termes qui s'annulent) et $\cos(2\pi-a)=\cos a$ (deux termes égaux). Les regroupements font disparaître presque tous les termes.

### Corrigé

Écrivons $c_k=\cos\dfrac{k\pi}6$.
- Pour $k=1,\dots,5$ : $c_{6-k}=\cos\left(\pi-\dfrac{k\pi}6\right)=-c_k$, donc $c_1+c_5=0$, $c_2+c_4=0$, et $c_3=0$ : la somme $c_1+\cdots+c_5$ vaut $0$.
- $c_6=\cos\pi=-1$.
- Pour $k=7,\dots,11$ : $c_k=\cos\left(2\pi-\dfrac{(12-k)\pi}6\right)=c_{12-k}$, donc $c_7+\cdots+c_{11}=c_5+\cdots+c_1=0$.

$$S=0+(-1)+0=-1.$$

### Pourquoi les autres réponses sont fausses

- **a)** on a oublié le terme $c_6=\cos\pi$, ou on l'a cru nul.
- **b)** on a pris $\cos\pi=1$ au lieu de $-1$.
- **d)** on a utilisé $\cos(\pi-a)=\cos a$ (formule du sinus) : les termes ne s'annulent plus.

</details>

Avis : 

---

## 9. `cqc-angles-associes-prob-c-faible-0` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Que vaut $\sin\dfrac{5\pi}6$ ?

- a) $-\dfrac12$
- b) $\dfrac{\sqrt3}2$
- c) $-\dfrac{\sqrt3}2$
- d) $\dfrac12$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

$\sin(\pi-a)=\sin a$ et $\cos(\pi-a)=-\cos a$ : deux angles supplémentaires ont le même sinus et des cosinus opposés.

### Corrigé

$\dfrac{5\pi}6=\pi-\dfrac\pi6$, donc $\sin\dfrac{5\pi}6=\sin\dfrac\pi6=\dfrac12$.

### Pourquoi les autres réponses sont fausses

- **a)** on a appliqué au sinus la règle du cosinus, $\sin(\pi-a)=-\sin a$.
- **b)** on a confondu $\sin\dfrac\pi6$ et $\cos\dfrac\pi6$.
- **c)** c'est $\cos\dfrac{5\pi}6$ : on a calculé le cosinus au lieu du sinus.

</details>

Avis : 

---

## 10. `cqc-angles-associes-prob-c-moyenne-2` (séries C/E)

**Énoncé :**

Pour tout réel $x$, on pose $A(x)=\cos(\pi+x)+\sin\left(\dfrac\pi2+x\right)-\cos(-x)$. Quelle est la forme simplifiée de $A(x)$ ?

- a) $A(x)=-\cos x$
- b) $A(x)=\cos x$
- c) $A(x)=-3\cos x$
- d) $A(x)=\sin x-2\cos x$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Angles associés : $\cos(\pi+x)=-\cos x$, $\sin\left(\dfrac\pi2+x\right)=\cos x$, $\cos(-x)=\cos x$. On remplace chaque terme puis on additionne.

### Corrigé

$$A(x)=-\cos x+\cos x-\cos x=-\cos x.$$

### Pourquoi les autres réponses sont fausses

- **b)** on a écrit $\cos(\pi+x)=\cos x$ (ou $\cos(-x)=-\cos x$), d'où une erreur de signe.
- **c)** on a écrit $\sin\left(\dfrac\pi2+x\right)=-\cos x$.
- **d)** on a écrit $\sin\left(\dfrac\pi2+x\right)=\sin x$ au lieu de $\cos x$.

</details>

Avis : 

---

## 11. `cqc-angles-associes-prob-c-moyenne-3` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Quelle liste donne, dans cet ordre, les valeurs exactes de $\sin\dfrac{7\pi}6$, $\cos\left(-\dfrac\pi3\right)$, $\cos\dfrac{2\pi}3$ et $\tan\dfrac{3\pi}4$ ?

- a) $\dfrac12\,;\ \dfrac12\,;\ -\dfrac12\,;\ -1$
- b) $-\dfrac12\,;\ \dfrac12\,;\ -\dfrac12\,;\ -1$
- c) $-\dfrac12\,;\ -\dfrac12\,;\ -\dfrac12\,;\ -1$
- d) $-\dfrac12\,;\ \dfrac12\,;\ -\dfrac12\,;\ 1$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On se ramène à un angle du premier quadrant avec $\sin(\pi+a)=-\sin a$, $\cos(-a)=\cos a$, $\cos(\pi-a)=-\cos a$ et $\tan(\pi-a)=-\tan a$.

### Corrigé

- $\sin\dfrac{7\pi}6=\sin\left(\pi+\dfrac\pi6\right)=-\sin\dfrac\pi6=-\dfrac12$.
- $\cos\left(-\dfrac\pi3\right)=\cos\dfrac\pi3=\dfrac12$.
- $\cos\dfrac{2\pi}3=\cos\left(\pi-\dfrac\pi3\right)=-\dfrac12$.
- $\tan\dfrac{3\pi}4=\tan\left(\pi-\dfrac\pi4\right)=-\tan\dfrac\pi4=-1$.

La liste est $-\dfrac12\,;\ \dfrac12\,;\ -\dfrac12\,;\ -1$.

### Pourquoi les autres réponses sont fausses

- **a)** on a écrit $\sin(\pi+a)=\sin a$ : le signe du premier terme est faux.
- **c)** on a écrit $\cos(-a)=-\cos a$, alors que le cosinus est pair.
- **d)** on a oublié le signe dans $\tan(\pi-a)=-\tan a$.

</details>

Avis : 

---

## 12. `cqc-asymptote-verticale-prob-c-elevee-5` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Pour tout réel $m$, on considère la fonction $f_m$ définie par $f_m(x)=\dfrac{x^2+mx+2}{x-1}$ (pour $x\neq1$). Pour quelles valeurs de $m$ la courbe de $f_m$ admet-elle la droite d'équation $x=1$ comme asymptote verticale ?

- a) Pour tout réel $m$
- b) Pour $m=-3$ seulement
- c) Pour tout réel $m\neq3$
- d) Pour tout réel $m\neq-3$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

La droite $x=1$ est asymptote verticale si le numérateur ne s'annule pas en $1$. S'il s'annule, on factorise par $(x-1)$ et on simplifie : il n'y a pas d'asymptote lorsque la limite obtenue est finie.

### Corrigé

Le numérateur en $x=1$ vaut $1+m+2=m+3$. Si $m\neq-3$, il ne s'annule pas, et comme $x-1\to0$ (de signe opposé de chaque côté de $1$), $f_m(x)\to\pm\infty$ : la droite $x=1$ est asymptote verticale.

Pour $m=-3$, $x^2-3x+2=(x-1)(x-2)$, donc $f_{-3}(x)=x-2$ pour $x\neq1$. La limite en $1$ est $-1$ (finie) : il n'y a pas d'asymptote verticale, la courbe est la droite $y=x-2$ privée du point $(1\,;-1)$.

La réponse est donc : pour tout $m\neq-3$.

### Pourquoi les autres réponses sont fausses

- **a)** on a regardé seulement le dénominateur ; pour $m=-3$, la fraction se simplifie et la limite en $1$ est finie.
- **b)** c'est exactement le cas où il n'y a pas d'asymptote : la conclusion a été inversée.
- **c)** erreur de signe en résolvant $m+3=0$.

</details>

Avis : 

---

## 13. `cqc-barycentre-prob-c-elevee-5` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, on donne $A(0\,;0)$, $B(2\,;0)$ et $C(0\,;4)$. Quel est l'ensemble des points $M$ du plan tels que $\left\|2\overrightarrow{MA}-\overrightarrow{MB}+3\overrightarrow{MC}\right\|=8$ ?

- a) Le cercle de centre $G\left(-\dfrac12\,;3\right)$ et de rayon $2$
- b) Le cercle de centre $G\left(-\dfrac12\,;3\right)$ et de rayon $8$
- c) Le cercle de centre $\left(\dfrac12\,;3\right)$ et de rayon $2$
- d) Le cercle de centre $\left(-\dfrac13\,;2\right)$ et de rayon $\dfrac43$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

La somme des coefficients doit être non nulle pour que le barycentre existe. La réduction $\sum\alpha_i\overrightarrow{MA_i}=\left(\sum\alpha_i\right)\overrightarrow{MG}$ (vraie pour tout $M$) ramène une norme de combinaison linéaire à une distance au barycentre : l'ensemble cherché est alors un cercle centré en $G$.

### Corrigé

$2-1+3=4\neq0$ : le barycentre $G$ de $(A,2)$, $(B,-1)$, $(C,3)$ existe. $x_G=\dfrac{2\times0-1\times2+3\times0}4=-\dfrac12$ et $y_G=\dfrac{0-0+3\times4}4=3$ : $G\left(-\dfrac12\,;3\right)$.

Pour tout $M$, $\overrightarrow{MA}=\overrightarrow{MG}+\overrightarrow{GA}$, etc. Alors
$$2\overrightarrow{MA}-\overrightarrow{MB}+3\overrightarrow{MC}=4\overrightarrow{MG}+\underbrace{\left(2\overrightarrow{GA}-\overrightarrow{GB}+3\overrightarrow{GC}\right)}_{=\vec0}=4\overrightarrow{MG}.$$

$\|4\overrightarrow{MG}\|=8\iff MG=2$. L'ensemble est le cercle de centre $G\left(-\dfrac12\,;3\right)$ et de rayon $2$.

### Pourquoi les autres réponses sont fausses

- **b)** on a oublié le facteur $4$ : $\|4\overrightarrow{MG}\|=8$ donne $MG=2$, pas $8$.
- **c)** on a oublié le signe du coefficient $-1$ de $B$ dans le calcul de $x_G$.
- **d)** on a divisé par $2+1+3=6$ (somme des valeurs absolues) au lieu de la somme des coefficients $4$.

</details>

Avis : 

---

## 14. `cqc-base-prob-c-moyenne-2` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans le plan vectoriel, $\vec e_1(1\,;2)$ et $\vec e_2(-1\,;1)$ forment une base. Quelles sont les coordonnées de $\vec u(3\,;3)$ dans cette base ?

- a) $(2\,;1)$
- b) $(-1\,;2)$
- c) $(2\,;-1)$
- d) $(1\,;-2)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On écrit $\vec u=a\vec e_1+b\vec e_2$, ce qui donne $\begin{cases}a-b=3\\2a+b=3\end{cases}$, système qu'on résout par addition.

### Corrigé

En additionnant les deux équations : $3a=6$, donc $a=2$ ; puis $b=a-3=-1$.
$\vec u=2\vec e_1-\vec e_2$, coordonnées $(2\,;-1)$. Vérification : $2(1\,;2)-(-1\,;1)=(2+1\,;4-1)=(3\,;3)$.

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe en tirant $b$ de $a-b=3$ : on a écrit $b=3-a$.
- **b)** on a écrit le système avec les lignes au lieu des colonnes : $a+2b=3$ et $-a+b=3$.
- **d)** ce couple ne vérifie que la première équation $a-b=3$ ; la seconde n'a pas été contrôlée.

</details>

Avis : 

---

## 15. `cqc-base-prob-c-moyenne-3` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Pour quelles valeurs du réel $m$ les vecteurs $\vec a(1\,;m)$ et $\vec b(m\,;4)$ ne forment-ils pas une base du plan vectoriel ?

- a) $m=2$ seulement
- b) $m=0$
- c) Aucune valeur de $m$
- d) $m=-2$ ou $m=2$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Deux vecteurs ne forment pas une base du plan si et seulement s'ils sont colinéaires, c'est-à-dire si $\det=0$. On résout cette condition pour trouver les valeurs du paramètre.

### Corrigé

Par exemple, $\vec u(1\,;-2)$ et $\vec v(-3\,;6)$ ne forment pas une base : $\det(\vec u,\vec v)=1\times6-(-2)\times(-3)=0$ ($\vec v=-3\vec u$).

Ici, $\det(\vec a,\vec b)=1\times4-m\times m=4-m^2=(2-m)(2+m)$. Il est nul pour $m=2$ ou $m=-2$ : dans ces cas $\vec a$ et $\vec b$ sont colinéaires et ne forment pas une base.

### Pourquoi les autres réponses sont fausses

- **a)** on a oublié la racine négative de $m^2=4$.
- **b)** déterminant mal calculé : on a fait $1\times m-m\times4=-3m$ au lieu de $1\times4-m\times m$.
- **c)** erreur de signe : on a écrit $\det=4+m^2$, qui ne s'annule jamais.

</details>

Avis : 

---

## 16. `cqc-base-prob-c-moyenne-4` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On admet que $\vec e_1(1\,;1)$ et $\vec e_2(1\,;2)$ forment une base du plan vectoriel. Quelle est l'expression de $\vec\imath$ dans cette base ?

- a) $\vec\imath=2\vec e_1-\vec e_2$
- b) $\vec\imath=-\vec e_1+\vec e_2$
- c) $\vec\imath=2\vec e_1+\vec e_2$
- d) $\vec\imath=-\vec e_1+2\vec e_2$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On vérifie que le déterminant est non nul, puis on résout $\vec\imath=a\vec e_1+b\vec e_2$ : l'équation vectorielle est un système $2\times2$.

### Corrigé

$\det(\vec e_1,\vec e_2)=2-1=1\neq0$ : c'est une base.
$\vec\imath=(1\,;0)$ : $a+b=1$ et $a+2b=0$ donnent $b=-1$, $a=2$ : $\vec\imath=2\vec e_1-\vec e_2$.
Vérification : $2(1\,;1)-(1\,;2)=(1\,;0)$.

De même, $\vec\jmath=-\vec e_1+\vec e_2$.

### Pourquoi les autres réponses sont fausses

- **b)** c'est l'expression de $\vec\jmath$, pas celle de $\vec\imath$.
- **c)** erreur de signe sur $b$ : $2(1\,;1)+(1\,;2)=(3\,;4)$.
- **d)** on a échangé les coefficients $a$ et $b$ ou mal lu les équations du système.

</details>

Avis : 

---

## 17. `cqc-calcul-de-termes-prob-c-elevee-5` (séries C/D/E)

**Remarque du relecteur :** LIMITE : la forme 2^(2^n) et la récurrence u_{n+1}-1=(u_n-1)^2 demandent une démonstration par récurrence peu courante en Première.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $(u_n)$ la suite définie par $u_0=3$ et, pour tout entier naturel $n$, $u_{n+1}=u_n^2-2u_n+2$. Quelle expression de $u_n$ est vraie pour tout entier naturel $n$ ?

- a) $u_n=1+2^{n+1}$
- b) $u_n=1+2^{2^n}$
- c) $u_n=2n+3$
- d) $u_n=1+2^{2n}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule les premiers termes et on repère une régularité (ici $u_n-1$ est une puissance de $2$). La démonstration par récurrence utilise la remarque $u_n^2-2u_n+2=(u_n-1)^2+1$, soit $u_{n+1}-1=(u_n-1)^2$, qui transforme la relation en une relation sur $u_n-1$.

### Corrigé

$u_1=9-6+2=5$, $u_2=25-10+2=17$, $u_3=289-34+2=257$.

Conjecture : $u_n-1$ vaut $2$, $4$, $16$, $256$, soit $2^{2^n}$ ; donc $u_n=1+2^{2^n}$.
- *Initialisation* : $u_0=1+2^{1}=3$.
- *Hérédité* : si $u_n=1+2^{2^n}$, alors $u_{n+1}-1=(u_n-1)^2=\left(2^{2^n}\right)^2=2^{2^{n+1}}$, donc $u_{n+1}=1+2^{2^{n+1}}$.

Pour tout $n$, $u_n=1+2^{2^n}$ (par exemple $u_4=1+2^{16}=65537$).

### Pourquoi les autres réponses sont fausses

- **a)** conjecture faite sur $u_0$ et $u_1$ seulement ; elle donne $u_2=9$ au lieu de $17$.
- **c)** conjecture d'une suite arithmétique à partir de $u_0=3$ et $u_1=5$ ; elle donne $u_2=7$.
- **d)** confusion entre $2^{2n}=4^n$ et $2^{2^n}$ : on obtient $u_0=2$ et $u_3=65$.

</details>

Avis : 

---

## 18. `cqc-calcul-de-termes-prob-c-moyenne-3` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $(u_n)$ la suite définie pour tout entier naturel $n$ par $u_n=\dfrac{2n+1}{n+2}$. Quelle liste donne, dans l'ordre, les termes $u_0$, $u_1$, $u_2$ et $u_3$ ?

- a) $1\,;\ \dfrac54\,;\ \dfrac75\,;\ \dfrac32$
- b) $\dfrac12\,;\ 1\,;\ \dfrac54\,;\ \dfrac75$
- c) $1\,;\ \dfrac43\,;\ \dfrac32\,;\ \dfrac85$
- d) $\dfrac12\,;\ \dfrac32\,;\ \dfrac52\,;\ \dfrac72$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule les premiers termes en remplaçant $n$ par $0$, $1$, $2$, $3$ dans la formule, au numérateur ET au dénominateur. Le premier terme est $u_0$ (et non $u_1$). Pour prouver la croissance d'une suite explicite, on étudierait le signe de $u_{n+1}-u_n$ ; ici on se contente de comparer les premiers termes.

### Corrigé

$u_0=\dfrac12$, $u_1=\dfrac33=1$, $u_2=\dfrac54$, $u_3=\dfrac75$.
En valeurs décimales : $0{,}5<1<1{,}25<1{,}4$ : la suite semble croissante (et $u_n=2-\dfrac3{n+2}$ se rapproche de $2$).

### Pourquoi les autres réponses sont fausses

- **a)** Ce sont $u_1$, $u_2$, $u_3$, $u_4$ : décalage d'indice, la suite commence à $u_0$.
- **c)** Le numérateur $2n+1$ a été remplacé par $2(n+1)$.
- **d)** $n$ n'a été remplacé qu'au numérateur, le dénominateur restant égal à $2$.

</details>

Avis : 

---

## 19. `cqc-cercle-trigonometrique-prob-c-faible-0` (séries C/D/E)

**Énoncé :**

Quelles sont les coordonnées du point $M$ du cercle trigonométrique associé au réel $\dfrac\pi6$ ?

- a) $\left(\dfrac{\sqrt3}2\,;\dfrac12\right)$
- b) $\left(\dfrac12\,;\dfrac{\sqrt3}2\right)$
- c) $\left(\dfrac{\sqrt2}2\,;\dfrac{\sqrt2}2\right)$
- d) $\left(\dfrac{\sqrt3}2\,;-\dfrac12\right)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Le point du cercle trigonométrique associé au réel $\theta$ a pour coordonnées $(\cos\theta\,;\sin\theta)$ : l'abscisse est le cosinus, l'ordonnée le sinus. On utilise les valeurs remarquables : $\cos\dfrac\pi6=\dfrac{\sqrt3}2$ et $\sin\dfrac\pi6=\dfrac12$.

### Corrigé

$M\left(\cos\dfrac\pi6\,;\sin\dfrac\pi6\right)=\left(\dfrac{\sqrt3}2\,;\dfrac12\right)$.

### Pourquoi les autres réponses sont fausses

- **b)** Cosinus et sinus sont inversés : ce sont les coordonnées du point associé à $\dfrac\pi3$.
- **c)** Ce sont les coordonnées du point associé à $\dfrac\pi4$.
- **d)** Le signe de l'ordonnée est faux : c'est le point associé à $-\dfrac\pi6$.

</details>

Avis : 

---

## 20. `cqc-convergence-prob-c-elevee-5` (séries C/E)

**Remarque du relecteur :** LIMITE : sans logarithme, la résolution passe par la calculatrice ou des essais successifs autour de n=54-55 ; le distracteur 54 est très proche, l'élève doit vérifier les deux valeurs.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $(u_n)$ la suite définie pour tout entier naturel $n$ par $u_n=2+3\times(0{,}9)^n$. Elle converge vers $2$. Quel est le plus petit entier $n$ tel que $|u_n-2|<0{,}01$ ?

- a) $44$
- b) $34$
- c) $54$
- d) $55$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour $q\in]0\,;1[$, $q^n\to0$ : la limite de $2+3q^n$ est $2$. Pour trouver le rang à partir duquel l'écart est inférieur à un seuil, on se ramène à une inéquation sur $q^n$ ; comme la suite $(q^n)$ est décroissante, on cherche à la calculatrice (table de valeurs) le premier rang qui convient et on vérifie le rang précédent.

### Corrigé

$0<0{,}9<1$ donc $0{,}9^n\to0$ et $u_n\to2$.

$|u_n-2|=3\times0{,}9^n$ et $3\times0{,}9^n<0{,}01\iff0{,}9^n<\dfrac1{300}$.
La suite $(3\times0{,}9^n)$ est décroissante. À la calculatrice : $3\times0{,}9^{54}\approx0{,}0101>0{,}01$ et $3\times0{,}9^{55}\approx0{,}0091<0{,}01$.
Le plus petit entier convenable est $n=55$.

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié le facteur $3$ en résolvant $0{,}9^n<0{,}01$ : ce n'est pas l'écart demandé.
- **b)** On a multiplié par $3$ au lieu de diviser, en résolvant $0{,}9^n<0{,}03$.
- **c)** Pour $n=54$, l'écart vaut environ $0{,}0101$, encore supérieur à $0{,}01$ : on s'est arrêté un rang trop tôt.

</details>

Avis : 

---

## 21. `cqc-covariance-prob-c-elevee-5` (séries C/E)

**Remarque du relecteur :** LIMITE : la régression linéaire des séries doubles est à la limite du programme de Première C/E ; à confirmer.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Pour une série statistique double $(X\,;Y)$, on donne $\bar x=10$, $\bar y=20$, $V(X)=16$, $V(Y)=25$ et $\operatorname{cov}(X,Y)=12$. Quelle est l'équation de la droite de régression de $Y$ en $X$ ?

- a) $y=0{,}75x+12{,}5$
- b) $y=0{,}48x+15{,}2$
- c) $y=0{,}75x+27{,}5$
- d) $y=3x-10$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Droite de $Y$ en $X$ : $y-\bar y=\dfrac{\operatorname{cov}(X,Y)}{V(X)}(x-\bar x)$. C'est la variance de $X$ (et non celle de $Y$, ni l'écart type) qui figure au dénominateur ; la droite passe par le point moyen $(\bar x\,;\bar y)$.

### Corrigé

$a=\dfrac{12}{16}=0{,}75$ : $y-20=0{,}75(x-10)$, soit $y=0{,}75x+12{,}5$.
Contrôle : pour $x=10$, $0{,}75\times10+12{,}5=20=\bar y$, la droite passe bien par le point moyen $(10\,;20)$.

Remarque : la droite de régression de $X$ en $Y$ est $x-10=0{,}48(y-20)$, soit $x=0{,}48y+0{,}4$, et $r=\dfrac{12}{4\times5}=0{,}6$ ; on a bien $0{,}75\times0{,}48=0{,}36=r^2$.

### Pourquoi les autres réponses sont fausses

- **b)** La pente $\dfrac{12}{25}=0{,}48$ utilise $V(Y)$ au lieu de $V(X)$.
- **c)** Erreur de signe en développant : $20+0{,}75\times10=27{,}5$ au lieu de $20-7{,}5=12{,}5$.
- **d)** La pente $\dfrac{12}4=3$ divise la covariance par l'écart type $\sigma_X=4$ au lieu de la variance.

</details>

Avis : 

---

## 22. `cqc-distance-point-droite-prob-c-elevee-5` (séries C/E)

**Remarque du relecteur :** LIMITE : la formule de la distance d'un point à une droite (bissectrices) est au plafond de la Première C/E et s'établit par le produit scalaire, absent du référentiel (à signaler).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, on considère les droites $(d_1):\ x-y=0$ et $(d_2):\ x+y-2=0$. Quel est l'ensemble des points $M$ équidistants de $(d_1)$ et de $(d_2)$ ?

- a) la droite d'équation $y=1$
- b) le seul point $(1\,;1)$
- c) la réunion des droites d'équations $y=1$ et $x=1$
- d) la réunion des droites d'équations $y=1$ et $x=-1$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Dire que $M$ est équidistant de deux droites sécantes s'écrit $\dfrac{|x-y|}{\sqrt2}=\dfrac{|x+y-2|}{\sqrt2}$ ; on lève les valeurs absolues en distinguant les deux cas $x-y=\pm(x+y-2)$ : l'ensemble est formé des deux bissectrices des droites.

### Corrigé

$d(M,(d_1))=\dfrac{|x-y|}{\sqrt2}$ et $d(M,(d_2))=\dfrac{|x+y-2|}{\sqrt2}$. L'égalité équivaut à $|x-y|=|x+y-2|$, soit
- $x-y=x+y-2\iff y=1$ ;
- ou $x-y=-(x+y-2)\iff2x=2\iff x=1$.

L'ensemble est la réunion des deux droites d'équations $y=1$ et $x=1$ (les bissectrices de $(d_1)$ et $(d_2)$), qui se coupent en $(1\,;1)$, point commun de $(d_1)$ et $(d_2)$.

### Pourquoi les autres réponses sont fausses

- **a)** Seul le cas $x-y=x+y-2$ a été traité ; $|A|=|B|$ donne aussi $A=-B$.
- **b)** Le point $(1\,;1)$ est équidistant (distance nulle), mais il n'est pas le seul : par exemple $(1\,;5)$ convient aussi.
- **d)** Erreur de signe dans $-(x+y-2)=-x-y+2$, qui conduit à $x=-1$.

</details>

Avis : 

---

## 23. `cqc-distance-point-droite-prob-c-faible-0` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, quelle est la distance du point $A(1\,;2)$ à la droite $(d):\ 3x+4y-2=0$ ?

- a) $\dfrac9{25}$
- b) $\dfrac95$
- c) $\dfrac97$
- d) $\dfrac{13}5$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La distance du point $M(x_0\,;y_0)$ à la droite $ax+by+c=0$ est $d=\dfrac{|ax_0+by_0+c|}{\sqrt{a^2+b^2}}$.

### Corrigé

$3\times1+4\times2-2=9$ et $\sqrt{3^2+4^2}=5$, donc $d=\dfrac95$.

### Pourquoi les autres réponses sont fausses

- **a)** On a divisé par $a^2+b^2=25$ en oubliant la racine carrée.
- **c)** On a divisé par $|a|+|b|=7$ au lieu de $\sqrt{a^2+b^2}$.
- **d)** Le terme constant a été pris avec le mauvais signe : $3+8+2=13$.

</details>

Avis : 

---

## 24. `cqc-distance-point-droite-prob-c-moyenne-2` (séries C/E)

**Remarque du relecteur :** La formule de la distance d'un point à une droite découle du produit scalaire, absent du référentiel : à signaler.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, un cercle de centre $\Omega(2\,;1)$ et de rayon $2$ est tangent à la droite $(d):\ 3x-4y+c=0$. Quelles sont les valeurs possibles du réel $c$ ?

- a) $c=8$ ou $c=-12$
- b) $c=8$
- c) $c=0$ ou $c=-4$
- d) $c=12$ ou $c=-8$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Un cercle est tangent à une droite si et seulement si la distance de son centre à la droite est égale à son rayon : on écrit $d(\Omega,(d))=r$ et on résout l'équation avec valeur absolue, qui a en général deux solutions.

### Corrigé

$d(\Omega,(d))=\dfrac{|3\times2-4\times1+c|}{5}=\dfrac{|2+c|}5=2\iff|2+c|=10\iff c=8\ \text{ou}\ c=-12.$
Il y a deux droites tangentes (situées de part et d'autre du centre) : $3x-4y+8=0$ et $3x-4y-12=0$.

### Pourquoi les autres réponses sont fausses

- **b)** Seule la solution positive de $|2+c|=10$ a été gardée ; $2+c=-10$ convient aussi.
- **c)** On a oublié de diviser par $\sqrt{3^2+(-4)^2}=5$, en résolvant $|2+c|=2$.
- **d)** Erreur de signe dans le numérateur, $|c-2|=10$ au lieu de $|2+c|=10$.

</details>

Avis : 

---

## 25. `cqc-distance-point-droite-prob-c-moyenne-3` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, on donne $A(1\,;1)$, $B(7\,;3)$ et $C(2\,;6)$. Quelle est l'aire du triangle $ABC$, en unités d'aire ?

- a) $8$
- b) $18$
- c) $14$
- d) $28$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On trouve l'équation de $(AB)$ à partir d'un vecteur normal (orthogonal au vecteur directeur $\overrightarrow{AB}$), puis la distance de $C$ à cette droite est la hauteur issue de $C$ : $\mathcal A=\dfrac12\,AB\times d(C,(AB))$.

### Corrigé

$\overrightarrow{AB}(6\,;2)$ : un vecteur normal est $(1\,;-3)$, donc $(AB):\ x-3y+c=0$ ; avec $A$ : $1-3+c=0$, soit $c=2$ : $(AB):\ x-3y+2=0$ (vérifiée par $B$ : $7-9+2=0$).
$d(C,(AB))=\dfrac{|2-18+2|}{\sqrt{10}}=\dfrac{14}{\sqrt{10}}$ et $AB=\sqrt{36+4}=2\sqrt{10}$.
$$\mathcal A=\dfrac12\times2\sqrt{10}\times\dfrac{14}{\sqrt{10}}=14.$$

### Pourquoi les autres réponses sont fausses

- **a)** Le vecteur directeur $(3\,;1)$ a été pris comme vecteur normal : la droite obtenue $3x+y-4=0$ n'est pas $(AB)$.
- **b)** Erreur de signe sur la constante ($c=-2$) : la droite $x-3y-2=0$ ne passe pas par $A$.
- **d)** Le facteur $\dfrac12$ de la formule de l'aire du triangle a été oublié.

</details>

Avis : 

---

## 26. `cqc-distance-point-droite-prob-c-moyenne-4` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, quel est l'ensemble des points $M$ situés à la distance $2$ de la droite $(d):\ x-2y+1=0$ ?

- a) la réunion des droites d'équations $x-2y+1-2=0$ et $x-2y+1+2=0$
- b) la réunion des droites d'équations $x-2y+1-10=0$ et $x-2y+1+10=0$
- c) la droite d'équation $x-2y+1-2\sqrt5=0$
- d) la réunion des droites d'équations $x-2y+1-2\sqrt5=0$ et $x-2y+1+2\sqrt5=0$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Dire que $d(M,(d))=2$ revient à $|x-2y+1|=2\sqrt{1+4}=2\sqrt5$, ce qui donne deux équations de droites parallèles à $(d)$, situées de part et d'autre.

### Corrigé

$d(M,(d))=\dfrac{|x-2y+1|}{\sqrt5}=2\iff|x-2y+1|=2\sqrt5\iff x-2y+1=2\sqrt5$ ou $x-2y+1=-2\sqrt5$.
L'ensemble est la réunion des deux droites parallèles à $(d)$ d'équations $x-2y+1-2\sqrt5=0$ et $x-2y+1+2\sqrt5=0$.

### Pourquoi les autres réponses sont fausses

- **a)** Le dénominateur $\sqrt5$ de la formule de la distance a été oublié.
- **b)** On a divisé par $1^2+(-2)^2=5$ sans prendre la racine carrée.
- **c)** Seul un des deux cas de la valeur absolue a été retenu ; il y a une droite de chaque côté de $(d)$.

</details>

Avis : 

---

## 27. `cqc-derivee-prob-c-elevee-5` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans une feuille de carton carrée de $12$ cm de côté, on découpe aux quatre coins des carrés de côté $x$ cm ($0<x<6$), puis on relève les bords pour former une boîte sans couvercle. Pour quelle valeur de $x$ le volume de la boîte est-il maximal ?

- a) $x=4$
- b) $x=6$
- c) $x=2$
- d) $x=3$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On exprime le volume comme fonction de $x$ (base carrée de côté $12-2x$, hauteur $x$), on dérive, on étudie le signe de la dérivée et on en déduit le maximum sur l'intervalle $]0\,;6[$.

### Corrigé

La base est un carré de côté $12-2x$ et la hauteur vaut $x$ : $V(x)=x(12-2x)^2$.

$V'(x)=(12-2x)^2+x\times2\times(-2)(12-2x)=(12-2x)(12-2x-4x)=(12-2x)(12-6x)=12(6-x)(2-x)$.
Sur $]0\,;6[$, $6-x>0$ : $V'(x)$ est du signe de $2-x$. $V$ croît sur $]0\,;2]$ et décroît sur $[2\,;6[$.

Le volume est maximal pour $x=2$ cm : $V(2)=2\times8^2=128\ \text{cm}^3$.

### Pourquoi les autres réponses sont fausses

- **a)** La base a été prise de côté $12-x$ au lieu de $12-2x$ (un seul coin retiré par côté).
- **b)** $x=6$ annule bien $V'$, mais n'appartient pas à $]0\,;6[$ et donne une boîte de volume nul.
- **d)** Le maximum n'est pas au milieu de l'intervalle : $V(3)=108<V(2)=128$.

</details>

Avis : 

---

## 28. `cqc-derivee-d-un-quotient-prob-c-elevee-5` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $[0\,;2\pi]$ par $f(x)=\dfrac{\sin x}{2+\cos x}$. Quelle est la valeur maximale de $f$ sur $[0\,;2\pi]$ ?

- a) $\dfrac12$
- b) $\dfrac{\sqrt3}5$
- c) $\dfrac{\sqrt3}2$
- d) $\dfrac{\sqrt3}3$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On applique la formule du quotient avec $u=\sin x$ et $v=2+\cos x$, puis on utilise $\sin^2x+\cos^2x=1$ pour simplifier. Le dénominateur est strictement positif ($2+\cos x\geq1$), le signe de $f'$ est celui de $2\cos x+1$.

### Corrigé

$u=\sin x$, $u'=\cos x$, $v=2+\cos x$, $v'=-\sin x$ :
$$f'(x)=\dfrac{\cos x\,(2+\cos x)-\sin x\times(-\sin x)}{(2+\cos x)^2}=\dfrac{2\cos x+\cos^2x+\sin^2x}{(2+\cos x)^2}=\dfrac{2\cos x+1}{(2+\cos x)^2}.$$

$f'(x)$ est du signe de $2\cos x+1$. $2\cos x+1>0\iff\cos x>-\dfrac12\iff x\in\left[0\,;\dfrac{2\pi}3\right[\,\cup\,\left]\dfrac{4\pi}3\,;2\pi\right]$.
Valeurs : $f(0)=0$, $f\left(\dfrac{2\pi}3\right)=\dfrac{\frac{\sqrt3}2}{2-\frac12}=\dfrac{\sqrt3}3$, $f\left(\dfrac{4\pi}3\right)=-\dfrac{\sqrt3}3$, $f(2\pi)=0$.

$f$ croît de $0$ à $\dfrac{\sqrt3}3$ sur $\left[0\,;\dfrac{2\pi}3\right]$, décroît de $\dfrac{\sqrt3}3$ à $-\dfrac{\sqrt3}3$ sur $\left[\dfrac{2\pi}3\,;\dfrac{4\pi}3\right]$, puis croît de $-\dfrac{\sqrt3}3$ à $0$ sur $\left[\dfrac{4\pi}3\,;2\pi\right]$. Le maximum de $f$ est $\dfrac{\sqrt3}3$.

### Pourquoi les autres réponses sont fausses

- **a)** On a placé le maximum de $f$ là où $\sin x$ est maximal ($x=\dfrac\pi2$) : $f\left(\dfrac\pi2\right)=\dfrac12<\dfrac{\sqrt3}3$.
- **b)** On a résolu $\cos x=\dfrac12$ au lieu de $\cos x=-\dfrac12$ : $f\left(\dfrac\pi3\right)=\dfrac{\sqrt3}5$.
- **c)** On a oublié de diviser par $2+\cos\dfrac{2\pi}3=\dfrac32$ : $\dfrac{\sqrt3}2$ n'est que $\sin\dfrac{2\pi}3$.

</details>

Avis : 

---

## 29. `cqc-effectifs-cumules-croissants-prob-d-elevee-5` (séries D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Les $40$ salaires d'une entreprise sont regroupés en classes (en milliers de F) : $[10\,;20[$ (effectif $6$), $[20\,;30[$ (effectif $x$), $[30\,;40[$ (effectif $2x$) et $[40\,;50[$ (effectif $4$). Quel est le pourcentage de salaires inférieurs à $30$ milliers de F ?

- a) $40\ \%$
- b) $25\ \%$
- c) $15\ \%$
- d) $90\ \%$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

La somme des effectifs est l'effectif total : on écrit $6+x+2x+4=40$ pour trouver $x$. Le pourcentage de salaires inférieurs à $30$ est $\dfrac{ECC(30)}{N}\times100$, où $ECC(30)$ est l'effectif cumulé croissant en $30$.

### Corrigé

$6+x+2x+4=40\iff3x=30\iff x=10$. Les effectifs sont $6$, $10$, $20$, $4$.

Effectifs cumulés croissants : $6$ (en $20$), $16$ (en $30$), $36$ (en $40$), $40$ (en $50$).
Salaires inférieurs à $30$ milliers de F : $16$ salaires sur $40$, soit $\dfrac{16}{40}=40\ \%$.

### Pourquoi les autres réponses sont fausses

- **b)** Seule la classe $[20\,;30[$ a été comptée ($10$ salaires), sans cumuler la classe $[10\,;20[$.
- **c)** Seule la première classe a été comptée ($6$ salaires sur $40$).
- **d)** On a lu l'effectif cumulé en $40$ ($36$) au lieu de celui en $30$.

</details>

Avis : 

---

## 30. `cqc-ensemble-de-definition-prob-c-elevee-5` (séries C)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $g(x)=\sqrt{x^2+mx+4}$ où $m$ est un réel. Pour quelles valeurs de $m$ la fonction $g$ est-elle définie sur $\mathbb R$ ?

- a) $m\in]-4\,;4[$
- b) $m\in[-4\,;4]$
- c) $m\in[-2\,;2]$
- d) $m\in]-\infty\,;-4]\cup[4\,;+\infty[$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

$g$ est définie sur $\mathbb R$ si et seulement si $x^2+mx+4\ge0$ pour tout $x$ : le coefficient dominant étant positif, le discriminant doit être négatif ou nul.

### Corrigé

$\Delta=m^2-4\times1\times4=m^2-16$. La condition $\Delta\le0$ s'écrit $m^2\le16$, soit $m\in[-4\,;4]$.

(Pour $m=\pm4$, le trinôme est un carré parfait, positif ou nul : $g$ est bien définie sur $\mathbb R$. Par exemple, pour $m=5$, $x^2+5x+4=(x+1)(x+4)$ est négatif entre $-4$ et $-1$.)

### Pourquoi les autres réponses sont fausses

- **a)** on a exigé $\Delta<0$ : pour $m=\pm4$ le trinôme s'annule une fois mais reste positif ou nul, donc ces valeurs conviennent.
- **c)** discriminant mal calculé ($\Delta=m^2-4$ au lieu de $m^2-16$, oubli du facteur $4ac$).
- **d)** c'est la condition $\Delta\ge0$ : le trinôme a alors des racines et devient négatif entre elles (sauf pour $m=\pm4$).

</details>

Avis : 

---

## 31. `cqc-extremum-prob-c-elevee-5` (séries C)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $f(x)=x+\dfrac4x$ sur $]0\,;+\infty[$. Pour quelles valeurs du réel $m$ l'équation $x+\dfrac4x=m$ admet-elle exactement deux solutions dans $]0\,;+\infty[$ ?

- a) $m\ge4$
- b) $m>2$
- c) $m>4$
- d) $m<4$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On étudie les variations de $f$ : $f'(x)=1-\dfrac4{x^2}=\dfrac{x^2-4}{x^2}$, du signe de $x^2-4$ pour $x>0$. Le nombre de solutions de $f(x)=m$ se lit sur le tableau de variations.

### Corrigé

$f'(x)=\dfrac{(x-2)(x+2)}{x^2}$ : $f$ décroît sur $]0\,;2]$ et croît sur $[2\,;+\infty[$. Minimum $f(2)=2+2=4$. De plus $f$ tend vers $+\infty$ en $0$ et en $+\infty$.

$f$ décroît de $+\infty$ à $4$ puis croît de $4$ à $+\infty$ :
- $m<4$ : aucune solution ;
- $m=4$ : une solution ($x=2$) ;
- $m>4$ : deux solutions.

Réponse : $m>4$.

### Pourquoi les autres réponses sont fausses

- **a)** pour $m=4$, l'équation n'a qu'une solution ($x=2$), le minimum étant atteint une seule fois.
- **b)** confusion entre l'abscisse du minimum ($2$) et la valeur du minimum ($f(2)=4$).
- **d)** sens inversé : en dessous du minimum, l'équation n'a aucune solution.

</details>

Avis : 

---

## 32. `cqc-fonction-homographique-prob-de-elevee-5` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $f(x)=\dfrac{2x+1}{x-1}$ et $(C)$ sa courbe dans un repère orthonormé. Quelle est l'équation de la tangente à $(C)$ au point d'abscisse $2$ ?

- a) $y=-3x+11$
- b) $y=3x-1$
- c) $y=-3x+5$
- d) $y=7x-9$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

La tangente au point d'abscisse $x_0$ est $y=f(x_0)+f'(x_0)(x-x_0)$. On peut écrire $f(x)=2+\dfrac k{x-1}$, ce qui donne $f'(x)=\dfrac{-k}{(x-1)^2}$.

### Corrigé

$2x+1=2(x-1)+3$, donc $f(x)=2+\dfrac3{x-1}$ ($k=3$) et $f'(x)=-\dfrac3{(x-1)^2}$.

$f(2)=5$ et $f'(2)=-3$ :
$$y=5-3(x-2)=-3x+11.$$

### Pourquoi les autres réponses sont fausses

- **b)** oubli du signe moins dans la dérivée : $f'(2)=3$ donne $y=5+3(x-2)$.
- **c)** on a écrit $y=f(2)+f'(2)\,x$ en oubliant de remplacer $x$ par $x-2$.
- **d)** dérivée d'un quotient avec un « $+$ » au numérateur : $\dfrac{2(x-1)+(2x+1)}{(x-1)^2}$ donne $f'(2)=7$.

</details>

Avis : 

---

## 33. `cqc-fonction-rationnelle-prob-c-elevee-5` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie par $f(x)=\dfrac{2x^2+bx+c}{x-2}$, où $b$ et $c$ sont deux réels. Sa courbe $(C)$ admet la droite $y=2x+1$ pour asymptote oblique et passe par le point $A(0\,;-2)$. Quelles sont les valeurs de $b$ et $c$ ?

- a) $b=1$ et $c=4$
- b) $b=5$ et $c=4$
- c) $b=-3$ et $c=-4$
- d) $b=-3$ et $c=4$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On écrit $f(x)=2x+p+\dfrac q{x-2}$ en fonction de $b$ et $c$ (division euclidienne) : l'asymptote oblique est $y=2x+p$, ce qui donne $b$. La condition sur le point $A$ donne $c$.

### Corrigé

$2x^2+bx+c=(x-2)(2x+4+b)+(c+8+2b)$, donc $f(x)=2x+4+b+\dfrac{c+8+2b}{x-2}$. L'asymptote oblique est $y=2x+4+b$ : $4+b=1$ donne $b=-3$. Puis $f(0)=\dfrac c{-2}=-2$ donne $c=4$.
$$f(x)=\dfrac{2x^2-3x+4}{x-2}=2x+1+\dfrac6{x-2}.$$

### Pourquoi les autres réponses sont fausses

- **a)** on a lu l'asymptote directement sur le numérateur ($y=2x+b$), sans faire la division par $x-2$.
- **b)** erreur de signe dans la division : quotient $2x+b-4$ au lieu de $2x+b+4$.
- **c)** erreur de signe en résolvant $\dfrac c{-2}=-2$.

</details>

Avis : 

---

## 34. `cqc-forme-canonique-prob-c-elevee-5` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $f(x)=-3x^2+6x+1$. Quel est l'ensemble des solutions de l'inéquation $f(x)\geq1$ ?

- a) $[0\,;2]$
- b) $]0\,;2[$
- c) $]-\infty\,;0]\cup[2\,;+\infty[$
- d) $\left[1-\dfrac{\sqrt{15}}3\,;1+\dfrac{\sqrt{15}}3\right]$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Avec un coefficient dominant négatif, la forme canonique $a(x-\alpha)^2+\beta$ donne un maximum $\beta$. Une inéquation se ramène à une inégalité sur le carré $(x-\alpha)^2$, qu'on résout avec des racines carrées.

### Corrigé

$f(x)=-3\left(x^2-2x\right)+1=-3\left[(x-1)^2-1\right]+1=-3(x-1)^2+4$ (maximum $4$, atteint en $x=1$).

$f(x)\geq1\iff-3(x-1)^2+4\geq1\iff(x-1)^2\leq1\iff-1\leq x-1\leq1\iff0\leq x\leq2$.
L'ensemble des solutions est $[0\,;2]$. Vérification : $f(0)=1$ et $f(2)=-12+12+1=1$.

### Pourquoi les autres réponses sont fausses

- **b)** inégalité large : $0$ et $2$ vérifient $f(x)=1$, donc ils sont solutions.
- **c)** sens de l'inégalité non inversé en divisant par $-3$.
- **d)** erreur de signe en isolant le carré : $3(x-1)^2\leq4+1$ au lieu de $3(x-1)^2\leq4-1$.

</details>

Avis : 

---

## 35. `cqc-forme-canonique-prob-c-moyenne-2` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Quel est le minimum sur $\mathbb R$ de la fonction $f(x)=2x^2-12x+7$ ?

- a) $-2$
- b) $3$
- c) $-11$
- d) $-25$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On met le coefficient dominant en facteur : $ax^2+bx+c=a\left[\left(x+\dfrac b{2a}\right)^2-\dfrac{b^2-4ac}{4a^2}\right]$. Si $a>0$, le minimum est le terme constant de la forme canonique.

### Corrigé

$f(x)=2\left(x^2-6x\right)+7=2\left[(x-3)^2-9\right]+7=2(x-3)^2-18+7=2(x-3)^2-11.$
Comme $(x-3)^2\geq0$, $f(x)\geq-11$, avec égalité pour $x=3$ : le minimum de $f$ est $-11$, atteint en $x=3$.

### Pourquoi les autres réponses sont fausses

- **a)** on a oublié de multiplier le $-9$ par le facteur $2$ : $-9+7=-2$.
- **b)** c'est l'abscisse du point où le minimum est atteint, pas la valeur du minimum.
- **d)** erreur de signe sur la constante : $-18-7$ au lieu de $-18+7$.

</details>

Avis : 

---

## 36. `cqc-formule-de-duplication-prob-c-elevee-5` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On admet que, pour tout réel $x$, $\cos3x=4\cos^3x-3\cos x$. De quelle équation le nombre $t=\cos\dfrac\pi9$ est-il solution ?

- a) $8t^3-6t+1=0$
- b) $8t^3-6t-1=0$
- c) $4t^3-3t-1=0$
- d) $8t^3-6t-\sqrt3=0$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La formule s'obtient en écrivant $\cos3x=\cos(2x+x)$ avec $\cos(a+b)=\cos a\cos b-\sin a\sin b$, puis les formules de duplication. Ici on choisit $x$ tel que $3x$ soit un angle remarquable.

### Corrigé

Rappel de la démonstration : $\cos3x=\cos2x\cos x-\sin2x\sin x=(2\cos^2x-1)\cos x-2\sin^2x\cos x$, et avec $\sin^2x=1-\cos^2x$ on obtient $4\cos^3x-3\cos x$.

Pour $x=\dfrac\pi9$ : $\cos3x=\cos\dfrac\pi3=\dfrac12$. Donc $4t^3-3t=\dfrac12$, soit $8t^3-6t-1=0$.
Vérification numérique : $t=\cos20^\circ\approx0{,}9397$ donne $8t^3-6t-1\approx0$.

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe en passant $\dfrac12$ dans l'autre membre (ou $\cos\dfrac\pi3$ pris égal à $-\dfrac12$).
- **c)** on a pris $\cos\dfrac\pi3=1$ au lieu de $\dfrac12$.
- **d)** confusion entre $\cos\dfrac\pi3=\dfrac12$ et $\sin\dfrac\pi3=\dfrac{\sqrt3}2$.

</details>

Avis : 

---

## 37. `cqc-formule-de-duplication-prob-c-moyenne-2` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Quelle est la valeur exacte de $\cos\dfrac\pi8$ ?

- a) $\dfrac{\sqrt{2-\sqrt2}}2$
- b) $\dfrac{2+\sqrt2}4$
- c) $\dfrac{\sqrt{2+\sqrt2}}2$
- d) $-\dfrac{\sqrt{2+\sqrt2}}2$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On linéarise : $\cos^2a=\dfrac{1+\cos2a}2$ et $\sin^2a=\dfrac{1-\cos2a}2$. Avec $a=\dfrac\pi8$, $2a=\dfrac\pi4$ dont le cosinus est connu. Comme $\dfrac\pi8\in\left]0\,;\dfrac\pi2\right[$, cosinus et sinus y sont positifs.

### Corrigé

$\cos\dfrac\pi4=\dfrac{\sqrt2}2$, donc
$$\cos^2\dfrac\pi8=\dfrac{1+\frac{\sqrt2}2}2=\dfrac{2+\sqrt2}4,\qquad\sin^2\dfrac\pi8=\dfrac{1-\frac{\sqrt2}2}2=\dfrac{2-\sqrt2}4.$$
Comme $\cos\dfrac\pi8>0$ : $\cos\dfrac\pi8=\dfrac{\sqrt{2+\sqrt2}}2\approx0{,}924$.

### Pourquoi les autres réponses sont fausses

- **a)** c'est $\sin\dfrac\pi8$ : on a utilisé la formule $\dfrac{1-\cos2a}2$.
- **b)** c'est $\cos^2\dfrac\pi8$ : on a oublié de prendre la racine carrée.
- **d)** mauvais signe : $\dfrac\pi8$ est dans $\left]0\,;\dfrac\pi2\right[$, où le cosinus est positif.

</details>

Avis : 

---

## 38. `cqc-formule-de-duplication-prob-c-moyenne-3` (séries C/D/E)

**Énoncé :**

Quel est l'ensemble des solutions dans $[0\,;2\pi]$ de l'équation $\cos2x=\cos x$ ?

- a) $\left\{0\,;\dfrac{\pi}3\,;\dfrac{5\pi}3\,;2\pi\right\}$
- b) $\left\{0\,;\dfrac{2\pi}3\,;\dfrac{4\pi}3\right\}$
- c) $\left\{\dfrac{2\pi}3\,;\dfrac{4\pi}3\right\}$
- d) $\left\{0\,;\dfrac{2\pi}3\,;\dfrac{4\pi}3\,;2\pi\right\}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On écrit $\cos2x=2\cos^2x-1$ pour obtenir une équation du second degré en $\cos x$ ; on pose $c=\cos x$, on résout en $c$, puis on résout chaque équation $\cos x=c$ sur l'intervalle donné.

### Corrigé

$\cos2x=\cos x\iff2\cos^2x-\cos x-1=0\iff(2\cos x+1)(\cos x-1)=0$.
- $\cos x=1$ : $x=0$ ou $x=2\pi$.
- $\cos x=-\dfrac12$ : $x=\dfrac{2\pi}3$ ou $x=\dfrac{4\pi}3$.

Ensemble des solutions : $\left\{0\,;\dfrac{2\pi}3\,;\dfrac{4\pi}3\,;2\pi\right\}$.

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe dans la factorisation : on a résolu $\cos x=\dfrac12$ au lieu de $\cos x=-\dfrac12$.
- **b)** oubli de $2\pi$, qui appartient à l'intervalle fermé $[0\,;2\pi]$ et vérifie $\cos x=1$.
- **c)** oubli du facteur $\cos x-1$ : les solutions de $\cos x=1$ sont perdues.

</details>

Avis : 

---

## 39. `cqc-formule-de-duplication-prob-c-moyenne-4` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Sachant que $\tan x=2$ et $x\in\left]0\,;\dfrac\pi2\right[$, que vaut $\cos2x$ ?

- a) $-\dfrac35$
- b) $\dfrac35$
- c) $-\dfrac43$
- d) $\dfrac45$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On retrouve $\cos x$ et $\sin x$ avec $\cos^2x=\dfrac1{1+\tan^2x}$ et $\sin x=\tan x\cos x$, puis on applique $\cos2x=\cos^2x-\sin^2x$.

### Corrigé

$\cos^2x=\dfrac1{1+4}=\dfrac15$, donc $\cos x=\dfrac1{\sqrt5}$ (positif sur $\left]0\,;\dfrac\pi2\right[$) et $\sin x=2\cos x=\dfrac2{\sqrt5}$. Alors
$$\cos2x=\cos^2x-\sin^2x=\dfrac15-\dfrac45=-\dfrac35.$$
Vérification : $\sin2x=2\times\dfrac2{\sqrt5}\times\dfrac1{\sqrt5}=\dfrac45$ et $\dfrac{\sin2x}{\cos2x}=-\dfrac43=\dfrac{2\tan x}{1-\tan^2x}$.

### Pourquoi les autres réponses sont fausses

- **b)** formule inversée : $\sin^2x-\cos^2x$ au lieu de $\cos^2x-\sin^2x$.
- **c)** c'est $\tan2x=\dfrac{2\tan x}{1-\tan^2x}$, pas $\cos2x$.
- **d)** c'est $\sin2x=2\sin x\cos x$, pas $\cos2x$.

</details>

Avis : 

---

## 40. `cqc-interpolation-lineaire-prob-d-elevee-5` (séries D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Les $40$ valeurs d'une série sont regroupées en classes : $[0\,;4[$ (effectif $6$), $[4\,;8[$ ($10$), $[8\,;12[$ ($16$), $[12\,;16[$ ($8$). Quelle est la médiane obtenue par interpolation linéaire ?

- a) $10$
- b) $9$
- c) $10{,}5$
- d) $8{,}25$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule les effectifs cumulés croissants : $6$, $16$, $32$, $40$. On repère la classe qui contient le rang $\dfrac N2$ et on interpole linéairement dans cette classe (méthode valable aussi pour $Q_1$ et $Q_3$ avec les rangs $\dfrac N4$ et $\dfrac{3N}4$).

### Corrigé

$\dfrac N2=20$ est entre $ECC(8)=16$ et $ECC(12)=32$ : la classe médiane est $[8\,;12[$, d'amplitude $4$.
$$Me\approx8+\dfrac{20-16}{32-16}\times4=8+1=9.$$
(De même, $Q_1\approx5{,}6$ et $Q_3\approx11{,}5$, d'où un écart interquartile de $5{,}9$.)

### Pourquoi les autres réponses sont fausses

- **a)** c'est le centre de la classe médiane : on n'a pas interpolé.
- **c)** on a oublié de retrancher l'effectif cumulé $16$ : $8+\dfrac{20}{32}\times4$.
- **d)** oubli de la multiplication par l'amplitude $4$ de la classe : $8+\dfrac4{16}$.

</details>

Avis : 

---

## 41. `cqc-isometrie-prob-c-moyenne-4` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans le plan orienté, soit $r_1$ la rotation de centre $O$ et d'angle $\dfrac\pi3$ et $r_2$ la rotation de centre $O$ et d'angle $\dfrac\pi6$. Quelle est la nature de $r_2\circ r_1$ ?

- a) La rotation de centre $O$ et d'angle $\dfrac\pi2$
- b) La rotation de centre $O$ et d'angle $\dfrac\pi6$
- c) La rotation de centre $O$ et d'angle $\dfrac{\pi^2}{18}$
- d) La symétrie centrale de centre $O$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

La composée de deux rotations de même centre $O$, d'angles $\theta_1$ et $\theta_2$, est la rotation de centre $O$ et d'angle $\theta_1+\theta_2$ : si $M_1=r_1(M)$ et $M'=r_2(M_1)$, alors $OM'=OM_1=OM$ et, par la relation de Chasles sur les angles orientés, $(\overrightarrow{OM},\overrightarrow{OM'})=(\overrightarrow{OM},\overrightarrow{OM_1})+(\overrightarrow{OM_1},\overrightarrow{OM'})$.

### Corrigé

Pour tout point $M$ distinct de $O$, $OM'=OM$ et $(\overrightarrow{OM},\overrightarrow{OM'})=\dfrac\pi3+\dfrac\pi6=\dfrac\pi2$ ; de plus $O$ est fixe.
$r_2\circ r_1$ est la rotation de centre $O$ et d'angle $\dfrac\pi2$ (rotation d'un quart de tour).

### Pourquoi les autres réponses sont fausses

- **b)** on a soustrait les angles au lieu de les additionner.
- **c)** on a multiplié les angles au lieu de les additionner.
- **d)** une symétrie centrale correspond à un angle total de $\pi$, or $\dfrac\pi3+\dfrac\pi6=\dfrac\pi2$.

</details>

Avis : 

---

## 42. `cqc-ligne-de-niveau-prob-c-elevee-5` (séries C/E)

**Remarque du relecteur :** Barycentre et ligne de niveau : faisable en coordonnées ; la méthode vectorielle passe par le produit scalaire, absent du référentiel (à signaler).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, on donne $A(0\,;0)$ et $B(3\,;0)$. Quel est l'ensemble des points $M$ du plan tels que $2MA^2+MB^2=15$ ?

- a) Le cercle de centre $G(1\,;0)$ et de rayon $3$
- b) Le cercle de centre $(2\,;0)$ et de rayon $\sqrt3$
- c) Le cercle de centre $G(1\,;0)$ et de rayon $\sqrt5$
- d) Le cercle de centre $G(1\,;0)$ et de rayon $\sqrt3$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On introduit le barycentre $G$ de $(A,2)$ et $(B,1)$ : l'ensemble cherché est une ligne de niveau centrée en $G$. En coordonnées, avec $M(x\,;y)$, on remplace $MA^2$ et $MB^2$ par leurs expressions puis on complète le carré.

### Corrigé

$x_G=\dfrac{2\times0+1\times3}3=1$, $y_G=0$ : $G(1\,;0)$.

Avec $M(x\,;y)$ : $MA^2=x^2+y^2$ et $MB^2=(x-3)^2+y^2$. Alors
$$2MA^2+MB^2=3x^2-6x+3y^2+9.$$
$2MA^2+MB^2=15\iff3x^2-6x+3y^2=6\iff x^2-2x+y^2=2\iff(x-1)^2+y^2=3.$
On retrouve la relation $2MA^2+MB^2=3MG^2+6$, et l'ensemble est le cercle de centre $G(1\,;0)$ et de rayon $\sqrt3$.
(Pour la valeur $6$ on obtiendrait le seul point $G$, et pour une valeur inférieure à $6$, l'ensemble vide.)

### Pourquoi les autres réponses sont fausses

- **a)** confusion entre $MG^2=3$ et $MG=3$.
- **b)** barycentre mal placé : les coefficients de $A$ et $B$ ont été échangés.
- **c)** on a oublié la constante $6$ : $3MG^2=15$ donnerait $MG^2=5$.

</details>

Avis : 

---

## 43. `cqc-ligne-de-niveau-prob-c-faible-0` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, on donne $A(1\,;0)$ et $B(5\,;2)$. Quelle est une équation de l'ensemble des points $M$ tels que $MA=MB$ ?

- a) $x-2y-1=0$
- b) $2x+y-7=0$
- c) $2x+y-2=0$
- d) $2x+y-5=0$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

L'ensemble des points équidistants de deux points distincts $A$ et $B$ est la médiatrice du segment $[AB]$ : droite perpendiculaire à $(AB)$ passant par son milieu. On l'obtient en écrivant $MA^2=MB^2$.

### Corrigé

Avec $M(x\,;y)$ : $MA^2=(x-1)^2+y^2$ et $MB^2=(x-5)^2+(y-2)^2$.
$$(x-1)^2+y^2=(x-5)^2+(y-2)^2\iff-2x+1=-10x+25-4y+4\iff8x+4y=28\iff2x+y=7.$$
L'ensemble est la médiatrice de $[AB]$, d'équation $2x+y-7=0$ ; elle passe par le milieu $I(3\,;1)$ ($6+1=7$).

### Pourquoi les autres réponses sont fausses

- **a)** c'est l'équation de la droite $(AB)$ elle-même, pas de sa médiatrice.
- **c)** droite perpendiculaire à $(AB)$ passant par $A$ au lieu du milieu de $[AB]$.
- **d)** milieu mal calculé : on a pris $\left(\dfrac{x_B-x_A}2\,;\dfrac{y_B-y_A}2\right)=(2\,;1)$.

</details>

Avis : 

---

## 44. `cqc-ligne-de-niveau-prob-c-moyenne-2` (séries C/E)

**Remarque du relecteur :** La méthode passe par le produit scalaire (théorème de la médiane), absent du référentiel : à signaler.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, on donne $A(0\,;0)$ et $B(4\,;0)$. Quel est l'ensemble $(\Gamma)$ des points $M$ tels que $MA^2+MB^2=20$ ?

- a) Le cercle de centre $I(2\,;0)$ et de rayon $\sqrt{12}$
- b) Le cercle de centre $I(2\,;0)$ et de rayon $\sqrt{10}$
- c) Le cercle de centre $I(2\,;0)$ et de rayon $\sqrt6$
- d) Le cercle de centre $I(2\,;0)$ et de rayon $\sqrt2$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Avec $I$ milieu de $[AB]$, la relation de la médiane donne $MA^2+MB^2=2MI^2+\dfrac{AB^2}2$. L'équation devient alors $MI^2=$ constante : un cercle de centre $I$ (ou un point, ou l'ensemble vide selon la constante).

### Corrigé

$I(2\,;0)$ et $AB^2=16$. $MA^2+MB^2=2MI^2+\dfrac{16}2=2MI^2+8$. Donc
$$MA^2+MB^2=20\iff2MI^2=12\iff MI^2=6.$$
$(\Gamma)$ est le cercle de centre $I(2\,;0)$ et de rayon $\sqrt6$.
Vérification en coordonnées : $x^2+y^2+(x-4)^2+y^2=20\iff2x^2-8x+2y^2-4=0\iff(x-2)^2+y^2=6$.

### Pourquoi les autres réponses sont fausses

- **a)** on a oublié de diviser par $2$ : $2MI^2=12$ donne $MI^2=6$.
- **b)** on a oublié le terme $\dfrac{AB^2}2=8$ de la relation de la médiane.
- **d)** on a retranché $AB^2=16$ au lieu de $\dfrac{AB^2}2=8$.

</details>

Avis : 

---

## 45. `cqc-ligne-de-niveau-prob-c-moyenne-3` (séries C/E)

**Remarque du relecteur :** Ligne de niveau MA^2-MB^2, faisable en coordonnées ; la méthode classique passe par le produit scalaire, absent du référentiel (à signaler).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, on donne $A(0\,;0)$ et $B(4\,;0)$. Quel est l'ensemble des points $M$ tels que $MA^2-MB^2=8$ ?

- a) La droite d'équation $x=3$
- b) La droite d'équation $x=1$
- c) La droite d'équation $x=-1$
- d) La droite d'équation $y=3$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

La différence $MA^2-MB^2$ est une fonction affine des coordonnées de $M$ (les termes en $x^2+y^2$ se compensent) : l'ensemble est une droite, perpendiculaire à $(AB)$.

### Corrigé

$MA^2-MB^2=x^2+y^2-\left[(x-4)^2+y^2\right]=8x-16$. L'égalité $8x-16=8$ donne $x=3$.
L'ensemble est la droite d'équation $x=3$, perpendiculaire à $(AB)$. Vérification avec $M(3\,;5)$ : $MA^2=9+25=34$, $MB^2=1+25=26$ et $34-26=8$.

### Pourquoi les autres réponses sont fausses

- **b)** on a oublié le terme $-16$ du développement : $8x=8$.
- **c)** erreur de signe dans $-(x-4)^2$ : on obtient $8x+16=8$.
- **d)** confusion des axes : la droite cherchée est perpendiculaire à $(AB)$, qui est l'axe des abscisses.

</details>

Avis : 

---

## 46. `cqc-optimisation-prob-d-elevee-5` (séries D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Le coût total de fabrication de $x$ articles (en milliers de F) est $C(x)=x^2+16x+400$ pour $x>0$. Le coût moyen est $M(x)=\dfrac{C(x)}x$. Combien d'articles faut-il fabriquer pour que le coût moyen soit minimal, et quel est ce coût moyen minimal ?

- a) $20$ articles ; coût moyen de $56$ milliers de F par article
- b) $20$ articles ; coût moyen de $36$ milliers de F par article
- c) $200$ articles ; coût moyen de $218$ milliers de F par article
- d) $20$ articles ; coût moyen de $1\,120$ milliers de F par article

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On divise chaque terme de $C(x)$ par $x$, on dérive $M$ et on étudie le signe de $M'$ : le minimum de $M$ est atteint où $M'$ s'annule en passant du négatif au positif.

### Corrigé

$M(x)=x+16+\dfrac{400}x$. $M'(x)=1-\dfrac{400}{x^2}=\dfrac{x^2-400}{x^2}$, négative pour $0<x<20$ et positive pour $x>20$ : $M$ décroît sur $]0\,;20]$ puis croît sur $[20\,;+\infty[$.
Le coût moyen est minimal pour $x=20$ articles : $M(20)=20+16+20=56$ milliers de F par article, soit $56\,000$ F.

### Pourquoi les autres réponses sont fausses

- **b)** Le terme $\dfrac{400}{20}=20$ a été oublié dans le calcul de $M(20)$.
- **c)** De $x^2=400$ on a tiré $x=200$ au lieu de $x=20$.
- **d)** $1\,120$ est le coût total $C(20)$, pas le coût moyen par article.

</details>

Avis : 

---

## 47. `cqc-parabole-prob-c-elevee-5` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Pour tout réel $m$, on considère la parabole $(P_m)$ d'équation $y=x^2-2mx+m$ et on note $S_m$ son sommet. Lorsque $m$ décrit $\mathbb R$, quelle est l'équation de la courbe décrite par $S_m$ ?

- a) $y=x^2-x$
- b) $y=3x^2-x$
- c) $y=-x^2-x$
- d) $y=-x^2+x$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Le sommet a pour abscisse $-\dfrac b{2a}$ ; son ordonnée s'obtient en remplaçant $x$ par cette abscisse. Pour trouver le lieu, on élimine le paramètre $m$ entre les deux coordonnées du sommet.

### Corrigé

$x_S=\dfrac{2m}2=m$ et $y_S=m^2-2m\times m+m=-m^2+m$. Donc $S_m(m\,;m-m^2)$.
En posant $x=m$, $y=x-x^2$ : $S_m$ décrit la parabole d'équation $y=-x^2+x$.
(Pour information, $(P_m)$ coupe l'axe des abscisses en deux points distincts si et seulement si $\Delta'=m^2-m>0$, soit $m<0$ ou $m>1$.)

### Pourquoi les autres réponses sont fausses

- **a)** On a pris $y_S=\dfrac{\Delta}{4a}=m^2-m$ au lieu de $-\dfrac{\Delta}{4a}$ : erreur de signe.
- **b)** On a pris $x_S=-m$ (signe oublié dans $-\dfrac b{2a}$), d'où $y_S=3m^2+m$ et $y=3x^2-x$.
- **c)** L'ordonnée $m-m^2$ est juste, mais on a substitué $m=-x$ en croyant $x_S=-m$.

</details>

Avis : 

---

## 48. `cqc-point-fixe-prob-c-moyenne-2` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $f(x)=\dfrac{x+6}{x+2}$ pour $x>0$ et $(u_n)$ la suite définie par $u_0=1$ et $u_{n+1}=f(u_n)$. Quels sont le point fixe positif $\alpha$ de $f$ et la valeur exacte de $u_2$ ?

- a) $\alpha=3$ et $u_2=\dfrac{25}{13}$
- b) $\alpha=2$ et $u_2=\dfrac73$
- c) $\alpha=2$ et $u_2=\dfrac{25}{13}$
- d) $\alpha=2$ et $u_2=\dfrac{103}{51}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On résout $f(x)=x$ en multipliant par le dénominateur ; on garde la solution compatible avec l'énoncé (ici positive). On calcule les termes un par un : $u_1=f(u_0)$, puis $u_2=f(u_1)$.

### Corrigé

$\dfrac{x+6}{x+2}=x\iff x+6=x^2+2x\iff x^2+x-6=0\iff(x-2)(x+3)=0$. Le point fixe positif est $\alpha=2$ (vérification : $f(2)=\dfrac84=2$).
$u_1=f(1)=\dfrac73$, $u_2=\dfrac{7/3+6}{7/3+2}=\dfrac{25/3}{13/3}=\dfrac{25}{13}$, et $u_3=\dfrac{103}{51}$.
Les termes alternent autour de $2$ en s'en rapprochant.

### Pourquoi les autres réponses sont fausses

- **a)** Mauvaise factorisation $(x+2)(x-3)$ : $3$ n'est pas solution, car $f(3)=\dfrac95\neq3$.
- **b)** $\dfrac73$ est $u_1$ : décalage d'indice.
- **d)** $\dfrac{103}{51}$ est $u_3$ : décalage d'indice.

</details>

Avis : 

---

## 49. `cqc-point-fixe-prob-c-moyenne-3` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $(u_n)$ la suite définie par $u_0=5$ et $u_{n+1}=0{,}8\,u_n+3$. Pour tout entier naturel $n$, quelle est l'expression de $u_n$ en fonction de $n$ ?

- a) $u_n=15-10\times0{,}8^n$
- b) $u_n=15+10\times0{,}8^n$
- c) $u_n=15+5\times0{,}8^n$
- d) $u_n=15-10\times0{,}2^n$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Le point fixe $\ell$ de $f(x)=0{,}8x+3$ vérifie $\ell=0{,}8\ell+3$. En soustrayant $\ell$, la suite $v_n=u_n-\ell$ est géométrique de raison égale au coefficient de $u_n$ ; on revient ensuite à $u_n=v_n+\ell$.

### Corrigé

$\ell=0{,}8\ell+3\iff0{,}2\ell=3\iff\ell=15$.
$v_{n+1}=u_{n+1}-15=0{,}8u_n-12=0{,}8(u_n-15)=0{,}8v_n$ : $(v_n)$ est géométrique de raison $0{,}8$ et de premier terme $v_0=5-15=-10$. Donc $v_n=-10\times0{,}8^n$ et
$$u_n=15-10\times0{,}8^n.$$
Comme $0{,}8^n\to0$, $u_n\to15$ (le point fixe). Vérification : $u_1=0{,}8\times5+3=7=15-8$.

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de signe sur le premier terme : $v_0=5-15=-10$ et non $10$ (on aurait $u_0=25$).
- **c)** On a pris $v_0=u_0=5$ au lieu de $v_0=u_0-\ell$ (on aurait $u_0=20$).
- **d)** On a pris pour raison $1-0{,}8=0{,}2$ au lieu du coefficient $0{,}8$ (on aurait $u_1=13$ au lieu de $7$).

</details>

Avis : 

---

## 50. `cqc-point-fixe-prob-c-moyenne-4` (séries C/E)

**Énoncé :**

Quels sont les points d'intersection de la courbe de $f(x)=x^2-3x+3$ et de la droite d'équation $y=x$ ?

- a) $(1\,;0)$ et $(3\,;0)$
- b) Il n'y a aucun point d'intersection
- c) $(-1\,;-1)$ et $(-3\,;-3)$
- d) $(1\,;1)$ et $(3\,;3)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Les points d'intersection de la courbe de $f$ et de la droite $y=x$ ont pour abscisses les solutions de $f(x)=x$, c'est-à-dire les points fixes de $f$ ; leur ordonnée est égale à leur abscisse.

### Corrigé

$x^2-3x+3=x\iff x^2-4x+3=0\iff(x-1)(x-3)=0$, donc $x=1$ ou $x=3$. Les points d'intersection sont $(1\,;1)$ et $(3\,;3)$.
Les abscisses $1$ et $3$ sont les points fixes de $f$ : $f(1)=1$ et $f(3)=9-9+3=3$.

### Pourquoi les autres réponses sont fausses

- **a)** Les abscisses sont justes, mais les points sont sur la droite $y=x$, pas sur l'axe des abscisses.
- **b)** On a résolu $f(x)=0$ (discriminant $-3<0$) au lieu de $f(x)=x$.
- **c)** Erreur de signe dans les racines de $x^2-4x+3$ : $-1$ et $-3$ ne vérifient pas l'équation.

</details>

Avis : 

---

## 51. `cqc-pourcentage-prob-d-elevee-5` (séries D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Un article coûte $80\,000$ F hors taxe. La TVA est de $19{,}25\ \%$. Le commerçant accorde ensuite une remise de $10\ \%$ sur le prix TTC. Quels sont le prix final et son écart en pourcentage par rapport au prix hors taxe ?

- a) $87\,400$ F, soit une hausse de $9{,}25\ \%$
- b) $85\,860$ F, soit une hausse de $7{,}325\ \%$
- c) $85\,860$ F, soit une hausse de $9{,}25\ \%$
- d) $72\,000$ F, soit une baisse de $10\ \%$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Le prix TTC est le prix HT multiplié par $1+\dfrac{\text{TVA}}{100}$. Une remise de $10\ \%$ multiplie par $0{,}9$. Le taux global par rapport au prix HT est le produit des deux coefficients moins $1$ : les pourcentages successifs ne s'ajoutent pas. Les valeurs ci-dessous sont exactes, sans arrondi.

### Corrigé

Prix TTC : $80\,000\times1{,}1925=95\,400$ F.
Prix final : $95\,400\times0{,}9=85\,860$ F. Par rapport au prix HT : $\dfrac{85\,860}{80\,000}=1{,}07325$, soit une **hausse de $7{,}325\ \%$** (coefficient global $1{,}1925\times0{,}9=1{,}07325$).

### Pourquoi les autres réponses sont fausses

- **a)** On a ajouté les pourcentages ($19{,}25-10=9{,}25$) au lieu de multiplier les coefficients.
- **c)** Le prix est juste, mais l'écart a été obtenu en ajoutant les pourcentages au lieu de calculer $\dfrac{85\,860}{80\,000}$.
- **d)** La TVA a été oubliée : seule la remise a été appliquée au prix HT.

</details>

Avis : 

---

## 52. `cqc-projete-orthogonal-prob-c-elevee-5` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, on donne $A(0\,;0)$, $B(6\,;0)$ et $C(2\,;4)$. Quelles sont les coordonnées du projeté orthogonal $H$ de $A$ sur la droite $(BC)$ ?

- a) $H(3\,;3)$
- b) $H(3\,;-3)$
- c) $H(4\,;2)$
- d) $H(2\,;0)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Le projeté orthogonal $H$ de $A$ sur $(BC)$ est le point d'intersection de $(BC)$ et de la perpendiculaire à $(BC)$ passant par $A$. Dans un repère orthonormé, deux droites de coefficients directeurs $a$ et $a'$ sont perpendiculaires si et seulement si $aa'=-1$.

### Corrigé

Coefficient directeur de $(BC)$ : $\dfrac{4-0}{2-6}=-1$, et $(BC)$ passe par $B(6\,;0)$ : $(BC):\ y=-x+6$.
La perpendiculaire passant par $A(0\,;0)$ a pour coefficient directeur $1$ : $y=x$.
Intersection : $x=-x+6$, donc $x=3$ et $y=3$ : $H(3\,;3)$.
Vérification par l'aire : avec la base $AB=6$ et la hauteur issue de $C$ (ordonnée $4$), $\mathcal A=\dfrac12\times6\times4=12$ ; avec la base $BC=\sqrt{32}=4\sqrt2$ et la hauteur $AH=\sqrt{18}=3\sqrt2$, $\mathcal A=\dfrac12\times4\sqrt2\times3\sqrt2=12$. Les deux résultats coïncident.

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de signe sur le coefficient directeur de $(BC)$ (pris égal à $1$) : on obtient $y=x-6$ et $y=-x$.
- **c)** $(4\,;2)$ est le milieu de $[BC]$ : on a confondu la hauteur et la médiane issues de $A$.
- **d)** $(2\,;0)$ est le projeté orthogonal de $C$ sur $(AB)$, pas celui de $A$ sur $(BC)$.

</details>

Avis : 

---

## 53. `cqc-projete-orthogonal-prob-c-moyenne-2` (séries C/E)

**Remarque du relecteur :** Faisable avec les pentes de droites perpendiculaires ; sinon, il faut le produit scalaire, absent du référentiel (à signaler).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, on donne le point $A(0\,;5)$ et la droite $(d):\ 2x-y+1=0$. Quelles sont les coordonnées du projeté orthogonal $H$ de $A$ sur $(d)$ ?

- a) $H(1\,;3)$
- b) $H\left(\dfrac83\,;\dfrac{19}3\right)$
- c) $H\left(\dfrac85\,;\dfrac{21}5\right)$
- d) $H(0\,;1)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Le projeté orthogonal $H$ de $A$ sur $(d)$ est le point d'intersection de $(d)$ et de la perpendiculaire à $(d)$ passant par $A$. Dans un repère orthonormé, deux droites de coefficients directeurs $a$ et $a'$ sont perpendiculaires si et seulement si $aa'=-1$.

### Corrigé

$(d):\ y=2x+1$, de coefficient directeur $2$. La perpendiculaire passant par $A(0\,;5)$ a pour coefficient directeur $-\dfrac12$ : $y=-\dfrac12x+5$.
Intersection : $2x+1=-\dfrac12x+5$, soit $\dfrac52x=4$ et $x=\dfrac85$, puis $y=2\times\dfrac85+1=\dfrac{21}5$.
$$H\left(\dfrac85\,;\dfrac{21}5\right).$$
Distance : $AH=\sqrt{\left(\dfrac85\right)^2+\left(\dfrac{21}5-5\right)^2}=\sqrt{\dfrac{80}{25}}=\dfrac{4\sqrt5}5$.
Vérification : $2\times\dfrac85-\dfrac{21}5+1=\dfrac{16-21+5}5=0$, donc $H\in(d)$.

### Pourquoi les autres réponses sont fausses

- **a)** On a pris pour la perpendiculaire le coefficient directeur $-2$ (opposé) au lieu de $-\dfrac12$ (opposé de l'inverse).
- **b)** On a pris le coefficient directeur $\dfrac12$ (inverse sans le signe moins) : la droite obtenue n'est pas perpendiculaire à $(d)$.
- **d)** $(0\,;1)$ est le point de $(d)$ de même abscisse que $A$ : $(AH)$ serait verticale, donc non perpendiculaire à $(d)$.

</details>

Avis : 

---

## 54. `cqc-raison-prob-c-elevee-5` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $(u_n)$ la suite définie par $u_0=2$ et $u_{n+1}=\dfrac{4u_n-1}{u_n+2}$. On pose $v_n=\dfrac1{u_n-1}$. Pour tout entier naturel $n$, quelle est l'expression de $u_n$ en fonction de $n$ ?

- a) $u_n=\dfrac{3n+2}{3n+1}$
- b) $u_n=\dfrac3{n+3}$
- c) $u_n=\dfrac{6-n}{3-n}$
- d) $u_n=\dfrac{n+6}{n+3}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand la définition de $u_{n+1}$ est un quotient, on cherche à exprimer $v_{n+1}=\dfrac1{u_{n+1}-1}$ à l'aide de $u_n$ pour faire apparaître $v_n$ : on met $u_{n+1}-1$ sur un même dénominateur, puis on inverse.

### Corrigé

$u_{n+1}-1=\dfrac{4u_n-1-(u_n+2)}{u_n+2}=\dfrac{3u_n-3}{u_n+2}=\dfrac{3(u_n-1)}{u_n+2}$. Donc
$$v_{n+1}=\dfrac{u_n+2}{3(u_n-1)}=\dfrac{(u_n-1)+3}{3(u_n-1)}=\dfrac13+\dfrac1{u_n-1}=v_n+\dfrac13.$$
$(v_n)$ est arithmétique de raison $\dfrac13$ et de premier terme $v_0=\dfrac1{2-1}=1$.
$v_n=1+\dfrac n3=\dfrac{n+3}3$, donc $u_n-1=\dfrac1{v_n}=\dfrac3{n+3}$ et
$$u_n=1+\dfrac3{n+3}=\dfrac{n+6}{n+3}.$$
Vérification : $u_1=\dfrac{4\times2-1}{2+2}=\dfrac74$ et $\dfrac{1+6}{1+3}=\dfrac74$.

### Pourquoi les autres réponses sont fausses

- **a)** On a pris une raison $3$ au lieu de $\dfrac13$ ($v_n=1+3n$), ce qui donne $u_1=\dfrac54$ au lieu de $\dfrac74$.
- **b)** On a oublié d'ajouter $1$ en revenant à $u_n$ : $\dfrac3{n+3}$ est $u_n-1$ (on aurait $u_0=1$).
- **c)** Erreur de signe sur la raison ($-\dfrac13$), ce qui donne $u_1=\dfrac52$.

</details>

Avis : 

---

## 55. `cqc-relation-de-chasles-prob-c-elevee-5` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $ABCD$ un quadrilatère quelconque et $I$, $J$, $K$, $L$ les milieux respectifs de $[AB]$, $[BC]$, $[CD]$, $[DA]$. Quelle est la nature du quadrilatère $IJKL$, quelle que soit la forme de $ABCD$ ?

- a) un rectangle
- b) un parallélogramme
- c) un losange
- d) un carré

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour un milieu $I$ de $[AB]$, $\overrightarrow{AI}=\dfrac12\overrightarrow{AB}$ et $\overrightarrow{IB}=\dfrac12\overrightarrow{AB}$. On exprime $\overrightarrow{IJ}$ avec la relation de Chasles à travers $B$, et de même $\overrightarrow{LK}$ à travers $D$ : les demi-vecteurs se regroupent en $\dfrac12\overrightarrow{AC}$.

### Corrigé

**1.** $\overrightarrow{IJ}=\overrightarrow{IB}+\overrightarrow{BJ}=\dfrac12\overrightarrow{AB}+\dfrac12\overrightarrow{BC}=\dfrac12\left(\overrightarrow{AB}+\overrightarrow{BC}\right)=\dfrac12\overrightarrow{AC}$.

**2.** $\overrightarrow{LK}=\overrightarrow{LD}+\overrightarrow{DK}=\dfrac12\overrightarrow{AD}+\dfrac12\overrightarrow{DC}=\dfrac12\left(\overrightarrow{AD}+\overrightarrow{DC}\right)=\dfrac12\overrightarrow{AC}$.

**3.** $\overrightarrow{IJ}=\overrightarrow{LK}$ : le quadrilatère $IJKL$ est un parallélogramme, quelle que soit la forme de $ABCD$.

### Pourquoi les autres réponses sont fausses

- **a)** $IJKL$ n'a des angles droits que si les diagonales $(AC)$ et $(BD)$ sont perpendiculaires, ce qui n'est pas toujours le cas.
- **c)** $IJKL$ n'a ses quatre côtés égaux que si $AC=BD$, ce qui n'est pas toujours le cas.
- **d)** il faudrait à la fois $(AC)\perp(BD)$ et $AC=BD$ : c'est un cas très particulier.

</details>

Avis : 

---

## 56. `cqc-relation-de-chasles-prob-c-moyenne-2` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $ABCD$ un parallélogramme. Quelle est l'expression de $\overrightarrow{BD}$ en fonction de $\overrightarrow{AB}$ et $\overrightarrow{AD}$ ?

- a) $\overrightarrow{AB}-\overrightarrow{AD}$
- b) $\overrightarrow{AB}+\overrightarrow{AD}$
- c) $-\overrightarrow{AB}-\overrightarrow{AD}$
- d) $\overrightarrow{AD}-\overrightarrow{AB}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Un parallélogramme $ABCD$ vérifie $\overrightarrow{BC}=\overrightarrow{AD}$ (et $\overrightarrow{DC}=\overrightarrow{AB}$). On introduit un sommet intermédiaire avec la relation de Chasles pour décomposer chaque vecteur.

### Corrigé

$\overrightarrow{AC}=\overrightarrow{AB}+\overrightarrow{BC}=\overrightarrow{AB}+\overrightarrow{AD}$ (car $\overrightarrow{BC}=\overrightarrow{AD}$).
$\overrightarrow{BD}=\overrightarrow{BA}+\overrightarrow{AD}=-\overrightarrow{AB}+\overrightarrow{AD}=\overrightarrow{AD}-\overrightarrow{AB}$.

### Pourquoi les autres réponses sont fausses

- **a)** c'est $\overrightarrow{DB}$ : on a confondu $\overrightarrow{BA}$ avec $\overrightarrow{AB}$, d'où une erreur de signe.
- **b)** c'est l'expression de l'autre diagonale $\overrightarrow{AC}$.
- **c)** seul $\overrightarrow{BA}=-\overrightarrow{AB}$ change de signe ; $\overrightarrow{AD}$ garde le sien.

</details>

Avis : 

---

## 57. `cqc-signe-de-la-derivee-prob-c-elevee-5` (séries C)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Pour $m$ réel, on pose $f_m(x)=x^3-3mx$ pour tout réel $x$. Pour $m=4$, quels sont les extremums locaux de $f_4$ ?

- a) un maximum local $16$ atteint en $x=-2$ et un minimum local $-16$ atteint en $x=2$
- b) un maximum local $16$ atteint en $x=2$ et un minimum local $-16$ atteint en $x=-2$
- c) un maximum local $16$ atteint en $x=4$ et un minimum local $-16$ atteint en $x=-4$
- d) aucun extremum : $f_4$ est croissante sur $\mathbb R$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

$f_m'(x)=3x^2-3m=3(x^2-m)$. Le signe dépend de $m$ : si $m\le0$, $x^2-m\ge0$ pour tout $x$ ; si $m>0$, on factorise avec $\sqrt m$.

### Corrigé

$f_m'(x)=3(x^2-m)$.
- Si $m\le0$ : $f_m'(x)\ge0$ pour tout $x$, donc $f_m$ est croissante sur $\mathbb R$ (aucun extremum).
- Si $m>0$ : $f_m'(x)=3(x-\sqrt m)(x+\sqrt m)$ ; $f_m$ croît sur $]-\infty\,;-\sqrt m]$, décroît sur $[-\sqrt m\,;\sqrt m]$, croît sur $[\sqrt m\,;+\infty[$.

Pour $m=4$ : $f_4(x)=x^3-12x$, $\sqrt m=2$. Maximum local $f_4(-2)=-8+24=16$, minimum local $f_4(2)=8-24=-16$.

Ainsi, pour $m=4$ : maximum local $16$ en $x=-2$, minimum local $-16$ en $x=2$.

### Pourquoi les autres réponses sont fausses

- **b)** on a lu le tableau à l'envers : $f_4(2)=-16$ et $f_4(-2)=16$, la fonction croît puis décroît autour de $-2$.
- **c)** $f_4'$ s'annule en $\pm\sqrt4=\pm2$ et non en $\pm4$ : on a oublié la racine carrée.
- **d)** c'est le cas $m\le0$ ; pour $m=4>0$, $f_4'$ change de signe en $-2$ et en $2$.

</details>

Avis : 

---

## 58. `cqc-suite-arithmetique-prob-d-elevee-5` (séries C/D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $(u_n)$ une suite arithmétique telle que $u_5=17$ et $u_3+u_8=41$. À partir de quel rang $n$ a-t-on $u_n>1000$ ?

- a) $n=145$
- b) $n=146$
- c) $n=147$
- d) $n=143$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On exprime tous les termes en fonction de $u_5$ et de la raison : $u_3=u_5-2r$ et $u_8=u_5+3r$. La condition $u_n>1000$ se traduit par une inéquation du premier degré en $n$, dont on retient le plus petit entier solution.

### Corrigé

**1.** $u_3=17-2r$ et $u_8=17+3r$, donc $u_3+u_8=34+r=41$ et $r=7$. Puis $u_0=u_5-5r=17-35=-18$ : $u_n=-18+7n$.

**2.** $-18+7n>1000\iff7n>1018\iff n>\dfrac{1018}7\approx145{,}4$. Le plus petit entier est $n=146$ : $u_{146}=-18+1022=1004>1000$, alors que $u_{145}=997<1000$.

### Pourquoi les autres réponses sont fausses

- **a)** on a arrondi $\dfrac{1018}7\approx145{,}4$ par défaut ; or $u_{145}=997<1000$.
- **c)** décalage d'indice : on a utilisé $u_n=u_0+(n-1)r$ au lieu de $u_n=u_0+nr$.
- **d)** on a oublié le premier terme $u_0=-18$ en résolvant $7n>1000$.

</details>

Avis : 

---

## 59. `cqc-suite-arithmetique-prob-d-faible-0` (séries C/D)

**Énoncé :**

Soit $(u_n)$ la suite arithmétique de premier terme $u_0=7$ et de raison $-2$. Que vaut $u_{12}$ ?

- a) $31$
- b) $-15$
- c) $-17$
- d) $-19$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une suite arithmétique de raison $r$, $u_n=u_0+nr$ : chaque terme s'obtient en ajoutant $r$ au précédent.

### Corrigé

$$u_{12}=7+12\times(-2)=7-24=-17.$$

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe sur la raison : on a ajouté $24$ au lieu de le retrancher.
- **b)** décalage d'indice : $7+11\times(-2)$ correspond à la formule $u_0+(n-1)r$, valable seulement si le premier terme est $u_1$.
- **d)** on a compté $13$ pas au lieu de $12$ entre $u_0$ et $u_{12}$.

</details>

Avis : 

---

## 60. `cqc-suite-arithmetique-prob-d-moyenne-2` (séries C/D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Un employé gagne $150\,000$ F par mois la première année ($n=0$) et son salaire augmente de $6\,000$ F chaque année. On note $S_n$ le salaire mensuel pendant l'année $n$. Que vaut la somme $S_0+S_1+\dots+S_{10}$ ?

- a) $1\,800\,000$ F
- b) $3\,960\,000$ F
- c) $2\,310\,000$ F
- d) $1\,980\,000$ F

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Une augmentation d'un montant fixe chaque année définit une suite arithmétique : $S_n=S_0+nr$. La somme de $N$ termes consécutifs vaut $N\times\dfrac{\text{premier}+\text{dernier}}2$.

### Corrigé

**1.** $(S_n)$ est arithmétique de premier terme $150\,000$ et de raison $6\,000$ : $S_n=150\,000+6\,000\,n$. Pour $n=10$ : $S_{10}=210\,000$ F.

**2.** Il y a $11$ termes :
$$S_0+\dots+S_{10}=11\times\dfrac{150\,000+210\,000}2=11\times180\,000=1\,980\,000.$$

### Pourquoi les autres réponses sont fausses

- **a)** on a compté $10$ termes au lieu de $11$ (de $S_0$ à $S_{10}$).
- **b)** on a oublié de diviser par $2$ dans la formule $N\times\dfrac{\text{premier}+\text{dernier}}2$.
- **c)** on a multiplié le nombre de termes par le dernier terme $210\,000$ au lieu de la moyenne du premier et du dernier.

</details>

Avis : 

---

## 61. `cqc-suite-arithmetique-prob-d-moyenne-4` (séries C/D)

**Remarque du relecteur :** La notation V_n est introduite mais pas utilisée ; sans gravité.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Un commerçant emprunte $2\,000\,000$ F à un taux d'intérêt simple de $8\ \%$ par an (les intérêts sont calculés chaque année sur le capital initial). On note $V_n$ la somme due après $n$ années. Quelle somme doit-il rembourser après $5$ ans ?

- a) environ $2\,938\,656$ F
- b) $2\,800\,000$ F
- c) $800\,000$ F
- d) $2\,160\,000$ F

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

En intérêt simple, chaque année s'ajoute le même montant $I=\text{capital}\times\text{taux}$ : la somme due est une suite arithmétique de raison $I$.

### Corrigé

**1.** L'intérêt annuel est $2\,000\,000\times0{,}08=160\,000$ F, ajouté chaque année : $V_{n+1}=V_n+160\,000$ avec $V_0=2\,000\,000$. La suite $(V_n)$ est arithmétique de raison $160\,000$.

**2.** $V_5=2\,000\,000+5\times160\,000=2\,800\,000$ F.

### Pourquoi les autres réponses sont fausses

- **a)** c'est le calcul en intérêts composés $2\,000\,000\times1{,}08^5$ ; en intérêt simple, l'intérêt annuel est toujours calculé sur le capital initial.
- **c)** ce sont seulement les intérêts des $5$ années : il faut y ajouter le capital emprunté.
- **d)** c'est la somme due après une seule année ($V_1$).

</details>

Avis : 

---

## 62. `cqc-suite-recurrente-prob-c-elevee-5` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $(u_n)$ la suite définie par $u_0=0$ et $u_{n+1}=\dfrac12u_n+n$. On pose $v_n=u_n-2n+4$. Quelle est l'expression de $u_n$ en fonction de $n$ ?

- a) $u_n=-2n+4+4\left(\dfrac12\right)^n$
- b) $u_n=2n-4+4\times2^n$
- c) $u_n=2n-4+4\left(\dfrac12\right)^n$
- d) $u_n=2n-4+4\left(\dfrac12\right)^{n+1}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand la relation de récurrence contient un terme en $n$, on cherche une suite auxiliaire de la forme $v_n=u_n-an-b$ qui soit géométrique. Ici l'énoncé la donne : on exprime $v_{n+1}$ en fonction de $u_n$ puis on fait apparaître $v_n$.

### Corrigé

**1.** $v_{n+1}=u_{n+1}-2(n+1)+4=\dfrac12u_n+n-2n-2+4=\dfrac12u_n-n+2=\dfrac12\left(u_n-2n+4\right)=\dfrac12v_n.$
$(v_n)$ est géométrique de raison $\dfrac12$ et de premier terme $v_0=0-0+4=4$.

**2.** $v_n=4\left(\dfrac12\right)^n$, donc
$$u_n=v_n+2n-4=2n-4+4\left(\dfrac12\right)^n.$$
Vérification : $u_1=0+0=0$ et $2-4+2=0$ ; $u_2=\dfrac12\times0+1=1$ et $4-4+1=1$.

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe en isolant $u_n$ : $u_n=v_n+2n-4$ et non $v_n-2n+4$.
- **b)** la raison de $(v_n)$ est $\dfrac12$ et non $2$ : $v_{n+1}=\dfrac12v_n$.
- **d)** décalage d'exposant : $v_n=v_0q^n$, avec l'exposant $n$ et non $n+1$.

</details>

Avis : 

---

## 63. `cqc-suite-recurrente-prob-c-faible-0` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $(u_n)$ la suite définie par $u_0=2$ et $u_{n+1}=u_n^2-1$. Que vaut $u_3$ ?

- a) $8$
- b) $9$
- c) $65$
- d) $63$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Une suite définie par récurrence se calcule de proche en proche : on remplace $u_n$ par la valeur du terme précédent.

### Corrigé

$u_1=2^2-1=3$, $u_2=3^2-1=8$, $u_3=8^2-1=63$.

### Pourquoi les autres réponses sont fausses

- **a)** c'est $u_2$ : on a calculé un terme de moins.
- **b)** on a doublé $u_n$ au lieu de l'élever au carré (calcul de $2u_n-1$).
- **c)** erreur de signe : $8^2-1=63$ et non $8^2+1$.

</details>

Avis : 

---

## 64. `cqc-suite-recurrente-prob-c-moyenne-3` (séries C/D/E)

**Remarque du relecteur :** LIMITE : le passage à la limite dans la relation de récurrence (continuité de x↦1/(1+x)) est admis implicitement ; acceptable puisque la convergence est admise.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $(u_n)$ la suite définie par $u_0=1$ et $u_{n+1}=\dfrac1{1+u_n}$. On admet que cette suite converge vers un réel $\ell$ strictement positif. Quelle est la valeur de $\ell$ ?

- a) $\dfrac{\sqrt5-1}2$
- b) $\dfrac{-1-\sqrt5}2$
- c) $\dfrac{1+\sqrt5}2$
- d) $\dfrac58$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Si $u_{n+1}=f(u_n)$ converge vers $\ell$ et que $f$ est continue en $\ell$, alors $\ell=f(\ell)$ : on résout l'équation du point fixe et on garde la solution compatible avec le signe des termes.

### Corrigé

**1.** $u_1=\dfrac12$, $u_2=\dfrac1{1+\frac12}=\dfrac23$, $u_3=\dfrac1{1+\frac23}=\dfrac35$, $u_4=\dfrac1{1+\frac35}=\dfrac58$. Les termes valent $1$, $0{,}5$, $0{,}667$, $0{,}6$, $0{,}625$ : ils alternent de part et d'autre d'une valeur voisine de $0{,}62$.

**2.** $\ell=\dfrac1{1+\ell}\iff\ell^2+\ell-1=0$, de discriminant $5$ et de racines $\dfrac{-1\pm\sqrt5}2$. Comme $\ell>0$ : $\ell=\dfrac{\sqrt5-1}2\approx0{,}618$.

### Pourquoi les autres réponses sont fausses

- **b)** c'est l'autre racine de $\ell^2+\ell-1=0$, mais elle est négative, alors que $\ell>0$.
- **c)** erreur de signe : c'est une racine de $\ell^2-\ell-1=0$ et non de $\ell^2+\ell-1=0$.
- **d)** c'est seulement $u_4$, une valeur approchée : la limite n'est pas un terme de la suite.

</details>

Avis : 

---

## 65. `cqc-symetrie-centrale-prob-c-elevee-5` (séries C/E)

**Remarque du relecteur :** VOCABULAIRE : seul le choix b) porte un nom de point (I), ce qui désigne la bonne réponse ; uniformiser l'écriture des choix.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=x^3-3x^2+2x$ et $(C)$ sa courbe dans un repère orthonormé. Quel point est centre de symétrie de $(C)$ ?

- a) $(2\,;0)$
- b) $(1\,;0)$
- c) $(0\,;0)$
- d) $(-1\,;0)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Un point $I(a\,;b)$ est centre de symétrie de la courbe de $f$ si, pour tout $x$, le symétrique du point $(x\,;f(x))$ par rapport à $I$, c'est-à-dire $(2a-x\,;2b-f(x))$, appartient à la courbe : $f(2a-x)=2b-f(x)$.

### Corrigé

**1.** $f(2-x)=(2-x)^3-3(2-x)^2+2(2-x)$. Développons : $(2-x)^3=8-12x+6x^2-x^3$ et $-3(2-x)^2=-12+12x-3x^2$ et $2(2-x)=4-2x$. La somme vaut
$$-x^3+3x^2-2x=-\left(x^3-3x^2+2x\right)=-f(x).$$

**2.** Pour tout $x$, $f(2-x)=-f(x)=2\times0-f(x)$ : le symétrique par rapport à $I(1\,;0)$ du point $M(x\,;f(x))$, à savoir $M'(2-x\,;-f(x))$, appartient à $(C)$. Donc $I(1\,;0)$ est centre de symétrie de $(C)$.

### Pourquoi les autres réponses sont fausses

- **a)** il faudrait $f(4-x)=-f(x)$ pour tout $x$ ; or pour $x=0$, $f(4)=24$ alors que $-f(0)=0$.
- **c)** $f$ n'est pas impaire : $f(-1)=-6$ alors que $-f(1)=0$.
- **d)** un centre $(a\,;b)$ avec $a$ dans l'ensemble de définition vérifie $f(a)=b$ ; or $f(-1)=-6\neq0$.

</details>

Avis : 

---

## 66. `cqc-symetrie-centrale-prob-c-faible-0` (séries C/E)

**Remarque du relecteur :** VOCABULAIRE : seul le choix c porte le nom « A' », ce qui désigne la bonne réponse ; uniformiser l'écriture des quatre choix.

**Énoncé :**

Dans un repère, quelle est l'image du point $A(3\,;-2)$ par la symétrie centrale de centre $I(1\,;1)$ ?

- a) $\left(2\,;-\dfrac12\right)$
- b) $(5\,;-5)$
- c) $(-1\,;4)$
- d) $(-1\,;0)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

La symétrie centrale de centre $I$ envoie $M$ sur $M'$ tel que $I$ soit le milieu de $[MM']$, c'est-à-dire $\overrightarrow{IM'}=-\overrightarrow{IM}$ ou $M'=2I-M$.

### Corrigé

$x'=2\times1-3=-1$ et $y'=2\times1-(-2)=4$. L'image est $A'(-1\,;4)$.
Vérification : le milieu de $[AA']$ est $\left(\dfrac{3-1}2\,;\dfrac{-2+4}2\right)=(1\,;1)=I$.

### Pourquoi les autres réponses sont fausses

- **a)** c'est le milieu de $[AI]$ : c'est $I$ qui doit être le milieu de $[AA']$.
- **b)** on a calculé $2A-I$ au lieu de $2I-A$.
- **d)** erreur de signe sur l'ordonnée : $2\times1-(-2)=4$ et non $2\times1-2=0$.

</details>

Avis : 

---

## 67. `cqc-symetrie-centrale-prob-c-moyenne-3` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, on considère la droite $(d):\ x-2y+3=0$. Quelle est une équation de l'image de $(d)$ par la symétrie centrale de centre $I(1\,;1)$ ?

- a) $x-2y+5=0$
- b) $x-2y+1=0$
- c) $x-2y+3=0$
- d) $x-2y-1=0$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

L'image d'une droite par une symétrie centrale est une droite parallèle. On l'obtient en écrivant qu'un point $M'(x'\,;y')$ est sur l'image si et seulement si son antécédent $M(2-x'\,;2-y')$ vérifie l'équation de $(d)$.

### Corrigé

$M(2-x'\,;2-y')\in(d)$ équivaut à $(2-x')-2(2-y')+3=0$, soit $-x'+2y'+1=0$, ou encore $x'-2y'-1=0$.
L'image de $(d)$ est la droite d'équation $x-2y-1=0$, parallèle à $(d)$ (mêmes coefficients de $x$ et de $y$, donc même vecteur directeur $(2\,;1)$).
Vérification : $A(-3\,;0)\in(d)$ a pour image $(5\,;2)$ et $5-4-1=0$.

### Pourquoi les autres réponses sont fausses

- **a)** on a pris pour antécédent $(x'-2\,;y'-2)$ au lieu de $(2-x'\,;2-y')$.
- **b)** on a pris pour antécédent $(2+x'\,;2+y')$ au lieu de $(2-x'\,;2-y')$.
- **c)** l'image est bien parallèle à $(d)$, mais $(d)$ n'est pas invariante car $I$ n'est pas sur $(d)$ : $1-2+3=2\neq0$.

</details>

Avis : 

---

## 68. `cqc-symetrie-centrale-prob-c-moyenne-4` (séries C/E)

**Remarque du relecteur :** VOCABULAIRE : seul le choix a) porte un nom de point (B'), ce qui désigne la bonne réponse ; uniformiser l'écriture des choix.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère, une symétrie centrale $s$ envoie $A(4\,;1)$ sur $A'(-2\,;5)$. Quelle est l'image du point $B(0\,;0)$ par $s$ ?

- a) $(2\,;6)$
- b) $(1\,;3)$
- c) $(6\,;-4)$
- d) $(-2\,;-6)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Le centre de la symétrie est le milieu de $[AA']$ : $I=\left(\dfrac{x_A+x_{A'}}2\,;\dfrac{y_A+y_{A'}}2\right)$. Ensuite $s(M)=2I-M$.

### Corrigé

$I=\left(\dfrac{4-2}2\,;\dfrac{1+5}2\right)=(1\,;3)$. Image de $B(0\,;0)$ : $B'(2\times1-0\,;2\times3-0)=(2\,;6)$.
Vérification : le milieu de $[BB']$ est $(1\,;3)=I$.

### Pourquoi les autres réponses sont fausses

- **b)** c'est le centre $I$ de la symétrie, pas l'image de $B$.
- **c)** le centre a été calculé avec une demi-différence $(3\,;-2)$ au lieu du milieu $(1\,;3)$ de $[AA']$.
- **d)** erreur de signe : on a calculé $B-2I$ au lieu de $2I-B$.

</details>

Avis : 

---

## 69. `cqc-tableau-de-variation-prob-c-elevee-5` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $[0\,;\pi]$ par $f(x)=2\sin x+\sin(2x)$. Quel est le maximum de $f$ sur $[0\,;\pi]$, et en quelle valeur de $x$ est-il atteint ?

- a) $2$, atteint en $x=\dfrac\pi2$
- b) $\dfrac{3\sqrt3}2$, atteint en $x=\dfrac\pi3$
- c) $\sqrt3$, atteint en $x=\dfrac\pi3$
- d) $1+\dfrac{\sqrt3}2$, atteint en $x=\dfrac\pi6$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On dérive avec $(\sin ax)'=a\cos ax$, puis on utilise $\cos2x=2\cos^2x-1$ pour factoriser $f'$. Le signe de chaque facteur se lit sur le cercle trigonométrique ou avec les valeurs remarquables du cosinus.

### Corrigé

**1.** $f'(x)=2\cos x+2\cos(2x)=2\cos x+2(2\cos^2x-1)=2\left(2\cos^2x+\cos x-1\right)$. Comme $2c^2+c-1=(2c-1)(c+1)$ (avec $c=\cos x$), $f'(x)=2(2\cos x-1)(\cos x+1)$.

**2.** Sur $[0\,;\pi]$ : $\cos x+1\geq0$ (nul seulement en $\pi$). Et $2\cos x-1>0\iff\cos x>\dfrac12\iff x<\dfrac\pi3$. Donc $f'>0$ sur $\left[0\,;\dfrac\pi3\right[$ et $f'<0$ sur $\left]\dfrac\pi3\,;\pi\right[$.

Valeurs : $f(0)=0$, $f\left(\dfrac\pi3\right)=2\times\dfrac{\sqrt3}2+\dfrac{\sqrt3}2=\dfrac{3\sqrt3}2\approx2{,}60$, $f(\pi)=0$.
$f$ croît de $0$ à $\dfrac{3\sqrt3}2$ sur $\left[0\,;\dfrac\pi3\right]$, puis décroît de $\dfrac{3\sqrt3}2$ à $0$ sur $\left[\dfrac\pi3\,;\pi\right]$.

Le maximum de $f$ sur $[0\,;\pi]$ est donc $\dfrac{3\sqrt3}2$, atteint en $x=\dfrac\pi3$.

### Pourquoi les autres réponses sont fausses

- **a)** $\sin x$ est maximal en $\dfrac\pi2$, mais pas $f$ : $f'\left(\dfrac\pi2\right)=-2<0$.
- **c)** bonne abscisse, mais on a oublié le coefficient $2$ devant $\sin x$ : $f\left(\dfrac\pi3\right)=2\times\dfrac{\sqrt3}2+\dfrac{\sqrt3}2$.
- **d)** confusion : $\cos x=\dfrac12$ donne $x=\dfrac\pi3$ et non $\dfrac\pi6$ (c'est $\sin x$ qui vaut $\dfrac12$ en $\dfrac\pi6$).

</details>

Avis : 

---

## 70. `cqc-terme-general-prob-c-elevee-5` (séries C/D/E)

**Remarque du relecteur :** VOCABULAIRE : préciser « francs CFA » (FCFA) plutôt que « F » ; montants peu réalistes (100 F par an).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On place $1000$ FCFA sur un compte et on y ajoute $100$ FCFA à la fin de chaque année. Le compte rapporte $5\ \%$ d'intérêts par an (les intérêts sont ajoutés avant le versement). On note $C_n$ le capital après $n$ années : $C_0=1000$ et $C_{n+1}=1{,}05\,C_n+100$. Quelle est la valeur de $C_{10}$, arrondie au dixième de FCFA ?

- a) $4886{,}7$ FCFA
- b) $2628{,}9$ FCFA
- c) $2886{,}7$ FCFA
- d) $2654{,}0$ FCFA

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour $C_{n+1}=aC_n+b$ ($a\neq1$), on soustrait le point fixe $\ell=\dfrac b{1-a}$ ; ici $\ell=\dfrac{100}{1-1{,}05}=-2000$ : $D_n=C_n+2000$ est géométrique de raison $a=1{,}05$.

### Corrigé

**1.** $D_{n+1}=C_{n+1}+2000=1{,}05C_n+2100=1{,}05\,(C_n+2000)=1{,}05\,D_n$. $(D_n)$ est géométrique de raison $1{,}05$ et de premier terme $D_0=3000$.

**2.** $D_n=3000\times1{,}05^n$, donc $C_n=3000\times1{,}05^n-2000$.
$$C_{10}=3000\times1{,}05^{10}-2000\approx3000\times1{,}6289-2000\approx2886{,}7\ \text{F}.$$
Vérification : $C_1=1{,}05\times1000+100=1150$ et $3000\times1{,}05-2000=1150$.

Arrondi au dixième de FCFA : $C_{10}\approx2886{,}7$ FCFA.

### Pourquoi les autres réponses sont fausses

- **a)** on a calculé $D_{10}=3000\times1{,}05^{10}$ en oubliant de retrancher $2000$.
- **b)** on a appliqué les intérêts au seul dépôt initial ($1000\times1{,}05^{10}$) et ajouté les $10$ versements sans intérêts.
- **d)** décalage d'exposant : $3000\times1{,}05^9-2000$ est $C_9$ et non $C_{10}$.

</details>

Avis : 

---

## 71. `cqc-terme-general-prob-c-moyenne-2` (séries C/D/E)

**Énoncé :**

Soit $(u_n)$ une suite arithmétique de premier terme $u_0=4$ et de raison $3$. Que vaut la somme $S=u_0+u_1+\dots+u_{19}$ ?

- a) $650$
- b) $1300$
- c) $620$
- d) $617{,}5$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

La somme de $N$ termes consécutifs d'une suite arithmétique vaut $N\times\dfrac{\text{premier terme}+\text{dernier terme}}2$.

### Corrigé

$u_{19}=4+19\times3=61$ et il y a $20$ termes :
$$S=20\times\dfrac{4+61}2=10\times65=650.$$

### Pourquoi les autres réponses sont fausses

- **b)** on a oublié de diviser par $2$ dans $N\times\dfrac{\text{premier}+\text{dernier}}2$.
- **c)** le dernier terme est $u_{19}=4+19\times3=61$, et non $4+18\times3=58$.
- **d)** il y a $20$ termes de $u_0$ à $u_{19}$, et non $19$.

</details>

Avis : 

---

## 72. `cqc-terme-general-prob-c-moyenne-4` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $(u_n)$ la suite définie par $u_0=3$ et, pour tout entier naturel $n$, $u_{n+1}=2u_n-1$. On pose $v_n=u_n-1$. Quelle est l'expression de $u_n$ en fonction de $n$ ?

- a) $u_n=1+2^{n+1}$
- b) $u_n=1+2^n$
- c) $u_n=2^{n+1}-1$
- d) $u_n=1+3\times2^n$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On soustrait le point fixe $\ell$ ($\ell=2\ell-1$, soit $\ell=1$) pour obtenir une suite géométrique de même raison que le facteur de $u_n$, dont on connaît le terme général.

### Corrigé

$v_{n+1}=u_{n+1}-1=2u_n-2=2(u_n-1)=2v_n$ : $(v_n)$ est géométrique de raison $2$ et de premier terme $v_0=3-1=2$.

Donc $v_n=2\times2^n=2^{n+1}$, puis $u_n=v_n+1=1+2^{n+1}$.
Vérification : $u_1=2\times3-1=5$ et $1+2^2=5$.

La bonne réponse est **a)**.

### Pourquoi les autres réponses sont fausses

- **b)** $1+2^n$ : on a pris $v_0=1$ au lieu de $v_0=u_0-1=2$.
- **c)** $2^{n+1}-1$ : on a écrit $u_n=v_n-1$ au lieu de $u_n=v_n+1$.
- **d)** $1+3\times2^n$ : on a utilisé $u_0=3$ comme premier terme de $(v_n)$ au lieu de $v_0=2$.

</details>

Avis : 

---

## 73. `cqc-trace-de-courbe-prob-c-elevee-5` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}\setminus\{2\}$ par $f(x)=\dfrac{x^2-4x+3}{x-2}$. Parmi les écritures suivantes, laquelle est égale à $f(x)$ pour tout $x\neq2$ ?

- a) $x-2+\dfrac1{x-2}$
- b) $x-2-\dfrac1{x-2}$
- c) $x+2-\dfrac1{x-2}$
- d) $x-2+\dfrac3{x-2}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On fait apparaître $(x-2)$ au numérateur (ici avec $x^2-4x+3=(x-2)^2-1$) pour obtenir la forme « partie affine + reste », qui donne l'asymptote oblique.

### Corrigé

$x^2-4x+3=(x-2)^2-4+3=(x-2)^2-1$, donc
$$f(x)=\dfrac{(x-2)^2-1}{x-2}=x-2-\dfrac1{x-2}.$$
On en déduit que, comme $-\dfrac1{x-2}\to0$ en $\pm\infty$, la droite $y=x-2$ est asymptote oblique à la courbe de $f$, et la droite $x=2$ est asymptote verticale.

La bonne réponse est **b)**.

### Pourquoi les autres réponses sont fausses

- **a)** $x-2+\dfrac1{x-2}$ : erreur de signe, on a écrit $x^2-4x+3=(x-2)^2+1$.
- **c)** $x+2-\dfrac1{x-2}$ : erreur de signe sur la partie affine ; $(x+2)(x-2)-1=x^2-5$, ce n'est pas le numérateur.
- **d)** $x-2+\dfrac3{x-2}$ : on a cru que $x^2-4x=(x-2)^2$ en oubliant le $-4$ du développement.

</details>

Avis : 

---

## 74. `cqc-valeur-exacte-prob-c-elevee-5` (séries C/E)

**Remarque du relecteur :** LIMITE : nécessite la formule cos3a=4cos^3a-3cos a et une factorisation de degré 3, exigeant pour un QCM.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On note $c=\cos\dfrac{2\pi}5$. Sachant que $\cos\dfrac{6\pi}5=\cos\dfrac{4\pi}5$, quelle est la valeur exacte de $c$ ?

- a) $\dfrac{-1-\sqrt5}4$
- b) $\dfrac{1+\sqrt5}4$
- c) $\dfrac{\sqrt5-1}2$
- d) $\dfrac{\sqrt5-1}4$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On utilise $\cos3a=4\cos^3a-3\cos a$ et $\cos2a=2\cos^2a-1$ avec $a=\dfrac{2\pi}5$. On factorise ensuite le polynôme obtenu en remarquant qu'il admet la racine évidente $1$, puis on choisit la racine selon le signe de $c$.

### Corrigé

$\cos\dfrac{6\pi}5=\cos\dfrac{4\pi}5$ s'écrit $\cos3a=\cos2a$ pour $a=\dfrac{2\pi}5$. Ainsi $4c^3-3c=2c^2-1$, soit $4c^3-2c^2-3c+1=0$.

$1$ est racine : $4-2-3+1=0$. Donc $4c^3-2c^2-3c+1=(c-1)(4c^2+2c-1)$. Comme $c\neq1$, on a $4c^2+2c-1=0$, de discriminant $4+16=20$ et de racines $\dfrac{-2\pm2\sqrt5}8=\dfrac{-1\pm\sqrt5}4$. Puisque $\dfrac{2\pi}5\in\left]0\,;\dfrac\pi2\right[$, $c>0$ :
$$\cos\dfrac{2\pi}5=\dfrac{\sqrt5-1}4\approx0{,}309.$$
La bonne réponse est **d)**.

### Pourquoi les autres réponses sont fausses

- **a)** $\dfrac{-1-\sqrt5}4$ : c'est l'autre racine, négative ; on a oublié que $c>0$.
- **b)** $\dfrac{1+\sqrt5}4$ : erreur de signe sur $-b$ dans la formule des racines (cette valeur est $\cos\dfrac\pi5$).
- **c)** $\dfrac{\sqrt5-1}2$ : on a divisé par $4$ au lieu de $2a=8$ dans la formule des racines.

</details>

Avis : 

---

## 75. `cqc-valeur-exacte-prob-c-moyenne-2` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Quelle est la valeur exacte de $\cos\dfrac\pi{12}$ ?

- a) $\dfrac{\sqrt6-\sqrt2}4$
- b) $\dfrac{\sqrt2+\sqrt6}2$
- c) $\dfrac{\sqrt2+\sqrt6}4$
- d) $\dfrac{1-\sqrt2}2$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Formule d'addition : $\cos(a-b)=\cos a\cos b+\sin a\sin b$. On l'applique avec $\dfrac\pi{12}=\dfrac\pi3-\dfrac\pi4$.

### Corrigé

$$\cos\dfrac\pi{12}=\cos\dfrac\pi3\cos\dfrac\pi4+\sin\dfrac\pi3\sin\dfrac\pi4=\dfrac12\times\dfrac{\sqrt2}2+\dfrac{\sqrt3}2\times\dfrac{\sqrt2}2=\dfrac{\sqrt2+\sqrt6}4.$$
(Valeur approchée : $0{,}966$.)

La bonne réponse est **c)**.

### Pourquoi les autres réponses sont fausses

- **a)** $\dfrac{\sqrt6-\sqrt2}4$ : on a écrit $\cos(a-b)=\cos a\cos b-\sin a\sin b$ (signe de la formule inversé) ; c'est la valeur de $\sin\dfrac\pi{12}$.
- **b)** $\dfrac{\sqrt2+\sqrt6}2$ : on a oublié un facteur $\dfrac12$ dans les produits ; ce nombre est supérieur à $1$, impossible pour un cosinus.
- **d)** $\dfrac{1-\sqrt2}2$ : on a cru que $\cos(a-b)=\cos a-\cos b$.

</details>

Avis : 

---

## 76. `cqc-valeur-exacte-prob-c-moyenne-3` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

On admet que $\cos\dfrac\pi{12}=\dfrac{\sqrt6+\sqrt2}4$ et $\sin\dfrac\pi{12}=\dfrac{\sqrt6-\sqrt2}4$. Quelle est la valeur exacte de $\tan\dfrac\pi{12}$ ?

- a) $2+\sqrt3$
- b) $1-\dfrac{\sqrt3}2$
- c) $2-\dfrac{\sqrt3}2$
- d) $2-\sqrt3$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

$\tan a=\dfrac{\sin a}{\cos a}$. Pour simplifier un quotient contenant des radicaux, on multiplie le numérateur et le dénominateur par l'expression conjuguée du dénominateur.

### Corrigé

$$\tan\dfrac\pi{12}=\dfrac{\sqrt6-\sqrt2}{\sqrt6+\sqrt2}=\dfrac{(\sqrt6-\sqrt2)^2}{(\sqrt6+\sqrt2)(\sqrt6-\sqrt2)}=\dfrac{6+2-2\sqrt{12}}{6-2}=\dfrac{8-4\sqrt3}4=2-\sqrt3.$$
Vérification : $2-\sqrt3\approx0{,}268$, qui est bien la valeur approchée de $\tan\dfrac\pi{12}$.

La bonne réponse est **d)**.

### Pourquoi les autres réponses sont fausses

- **a)** $2+\sqrt3$ : on a calculé $\dfrac{\cos}{\sin}$ au lieu de $\dfrac{\sin}{\cos}$.
- **b)** $1-\dfrac{\sqrt3}2$ : on a calculé le dénominateur $6+2=8$ au lieu de $(\sqrt6)^2-(\sqrt2)^2=6-2=4$.
- **c)** $2-\dfrac{\sqrt3}2$ : on a oublié le facteur $2$ du double produit dans $(\sqrt6-\sqrt2)^2$.

</details>

Avis : 

---

## 77. `cqc-variance-prob-c-elevee-5` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Un premier groupe de $10$ élèves a une moyenne de $12$ et une variance de $4$ ; un second groupe de $30$ élèves a une moyenne de $16$ et une variance de $9$. Quelle est la variance de l'ensemble des $40$ élèves ?

- a) $10{,}75$
- b) $7{,}75$
- c) $6{,}5$
- d) $39{,}75$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour regrouper deux séries : la moyenne totale est la moyenne pondérée des moyennes ; la variance totale se calcule avec $V=\dfrac{\sum n_j\left(V_j+\bar x_j^2\right)}{N}-\bar x^2$, car pour chaque groupe la moyenne des carrés vaut $V_j+\bar x_j^2$.

### Corrigé

Moyenne : $\bar x=\dfrac{10\times12+30\times16}{40}=\dfrac{600}{40}=15$.

Moyenne des carrés de chaque groupe : $4+12^2=148$ et $9+16^2=265$. Pour l'ensemble :
$$\overline{x^2}=\dfrac{10\times148+30\times265}{40}=\dfrac{9430}{40}=235{,}75.$$
$$V=235{,}75-15^2=235{,}75-225=10{,}75.$$
La bonne réponse est **a)**.

### Pourquoi les autres réponses sont fausses

- **b)** $7{,}75$ : c'est la moyenne pondérée des deux variances ; on a oublié l'écart entre les moyennes des deux groupes.
- **c)** $6{,}5$ : c'est la moyenne simple des deux variances, sans pondération ni écart entre les moyennes.
- **d)** $39{,}75$ : on a pris pour moyenne totale $\dfrac{12+16}2=14$ (moyenne non pondérée) au lieu de $15$.

</details>

Avis : 

---

## 78. `cqc-vecteur-normal-prob-c-moyenne-3` (séries C/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, on considère les droites $(d_1):\ 2x+3y-1=0$ et $(d_2):\ 3x-2y+5=0$. Quelles sont les coordonnées de leur point d'intersection ?

- a) $\left(1\,;-\dfrac13\right)$
- b) $(-1\,;1)$
- c) $\left(-1\,;-\dfrac13\right)$
- d) $(1\,;-1)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Le point d'intersection de deux droites sécantes est la solution du système formé par leurs deux équations. On peut le résoudre par combinaison linéaire. (Ici les droites sont d'ailleurs perpendiculaires : leurs coefficients directeurs $-\dfrac23$ et $\dfrac32$ ont pour produit $-1$.)

### Corrigé

On résout $\begin{cases}2x+3y=1\\3x-2y=-5\end{cases}$. En multipliant la première par $2$ et la seconde par $3$ : $4x+6y=2$ et $9x-6y=-15$. En additionnant : $13x=-13$, donc $x=-1$, puis $y=\dfrac{1-2x}{3}=1$.

Le point d'intersection est $(-1\,;1)$. Vérification : $-2+3=1$ et $-3-2=-5$.

La bonne réponse est **b)**.

### Pourquoi les autres réponses sont fausses

- **a)** $\left(1\,;-\dfrac13\right)$ : erreur de signe en passant $5$ de l'autre côté ($3x-2y=5$), d'où $13x=13$ ; ce point ne vérifie pas l'équation de $(d_2)$.
- **c)** $\left(-1\,;-\dfrac13\right)$ : $x$ est juste mais $y$ a été calculé avec $y=\dfrac{1+2x}3$ (erreur de signe).
- **d)** $(1\,;-1)$ : on a changé le signe des deux coordonnées de la solution ; ce point ne vérifie aucune des deux équations.

</details>

Avis : 

---

## 79. `cqc-ecart-type-prob-c-elevee-5` (séries C/D/E)

**Remarque du relecteur :** Le distracteur a) (49) est la variance : bon piège. Des notes sur 30 sont peu usuelles (notes sur 20 au Cameroun), contexte à revoir éventuellement.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Les notes d'une classe de $20$ élèves sont regroupées en classes : $[0\,;10[$ (effectif $4$), $[10\,;20[$ (effectif $10$) et $[20\,;30[$ (effectif $6$). En prenant les centres des classes, quel est l'écart-type de la série (arrondi au centième si nécessaire) ?

- a) $49$
- b) $17$
- c) $7$
- d) $8{,}16$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une série regroupée en classes, on remplace chaque classe par son centre ($\dfrac{\text{borne inf.}+\text{borne sup.}}{2}$) puis on applique les formules avec effectifs : $V=\dfrac{\sum n_ix_i^2}N-\bar x^2$ et $\sigma=\sqrt V$.

### Corrigé

Centres : $5$, $15$, $25$ avec les effectifs $4$, $10$, $6$ ($N=20$).
$$\bar x=\dfrac{4\times5+10\times15+6\times25}{20}=\dfrac{320}{20}=16.$$
$$\dfrac{\sum n_ix_i^2}N=\dfrac{4\times25+10\times225+6\times625}{20}=\dfrac{6100}{20}=305,$$
$$V=305-16^2=305-256=49,\qquad\sigma=\sqrt{49}=7.$$
La valeur est exacte, aucun arrondi au centième n'est nécessaire.

La bonne réponse est **c)**.

### Pourquoi les autres réponses sont fausses

- **a)** $49$ : c'est la variance ; on a oublié de prendre la racine carrée.
- **b)** $17$ : on a retranché $\bar x=16$ au lieu de $\bar x^2=256$ : $\sqrt{305-16}=17$.
- **d)** $8{,}16$ : on a oublié les effectifs et fait la moyenne simple sur les trois centres (arrondi au centième).

</details>

Avis : 

---

## 80. `cqc-equation-trigonometrique-elevee-5` (séries C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou série retirée) : à examiner de près.

**Énoncé :**

Quel est l'ensemble des solutions dans $[0\,;2\pi[$ de l'inéquation $2\sin^2x+3\cos x\geq0$ ?

- a) $\left[0\,;\dfrac{2\pi}3\right]\cup\left[\dfrac{4\pi}3\,;2\pi\right[$
- b) $\left[\dfrac{2\pi}3\,;\dfrac{4\pi}3\right]$
- c) $\left[0\,;\dfrac\pi3\right]\cup\left[\dfrac{5\pi}3\,;2\pi\right[$
- d) $\left[0\,;\dfrac{2\pi}3\right]$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand une expression mêle $\sin^2x$ et $\cos x$, on utilise $\sin^2x=1-\cos^2x$ pour tout exprimer en $\cos x$, on étudie le signe en $t=\cos x$ ($t\in[-1;1]$), puis on lit les solutions sur le cercle trigonométrique.

### Corrigé

Avec $\sin^2x=1-\cos^2x$ : $2\sin^2x+3\cos x=-2t^2+3t+2=-(2t^2-3t-2)$ avec $t=\cos x$.

$\Delta=9+16=25$ : les racines de $2t^2-3t-2$ sont $t=2$ et $t=-\dfrac12$, d'où $2\sin^2x+3\cos x=-(t-2)(2t+1)$.

Comme $t-2<0$ (car $|\cos x|\leq1$), l'expression est $\geq0$ si et seulement si $2t+1\geq0$, soit $\cos x\geq-\dfrac12$.

Or $\cos x=-\dfrac12$ pour $x=\dfrac{2\pi}3$ ou $x=\dfrac{4\pi}3$. Dans $[0\,;2\pi[$ :
$$S=\left[0\,;\dfrac{2\pi}3\right]\cup\left[\dfrac{4\pi}3\,;2\pi\right[.$$
La bonne réponse est **a)**.

### Pourquoi les autres réponses sont fausses

- **b)** $\left[\dfrac{2\pi}3\,;\dfrac{4\pi}3\right]$ : c'est la zone où $\cos x\leq-\dfrac12$ ; on a oublié que le facteur $t-2<0$ change le sens de l'inégalité.
- **c)** $\left[0\,;\dfrac\pi3\right]\cup\left[\dfrac{5\pi}3\,;2\pi\right[$ : on a résolu $\cos x\geq\dfrac12$ au lieu de $\cos x\geq-\dfrac12$ (erreur de signe sur la racine).
- **d)** $\left[0\,;\dfrac{2\pi}3\right]$ : on a oublié le second arc, entre $\dfrac{4\pi}3$ et $2\pi$, où l'on a aussi $\cos x\geq-\dfrac12$.

</details>

Avis : 

---

## 81. `cqc-equation-trigonometrique-faible-0` (séries C/D/E)

**Énoncé :**

Quel est l'ensemble des solutions dans $[0\,;2\pi[$ de l'équation $\cos x=\dfrac12$ ?

- a) $\left\{\dfrac\pi3,\;\dfrac{2\pi}3\right\}$
- b) $\left\{-\dfrac\pi3,\;\dfrac\pi3\right\}$
- c) $\left\{\dfrac\pi6,\;\dfrac{11\pi}6\right\}$
- d) $\left\{\dfrac\pi3,\;\dfrac{5\pi}3\right\}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On ramène l'équation à une équation élémentaire ($\cos x=\cos a$, $\sin x=\sin a$, $\tan x=\tan a$), dont les solutions générales sont : $x=\pm a+2k\pi$ pour $\cos$, $x=a+2k\pi$ ou $x=\pi-a+2k\pi$ pour $\sin$ ; on retient ensuite celles de l'intervalle demandé.

### Corrigé

$\dfrac12=\cos\dfrac\pi3$, donc $x=\dfrac\pi3+2k\pi$ ou $x=-\dfrac\pi3+2k\pi$, $k\in\mathbb{Z}$.

Dans $[0\,;2\pi[$ : $S=\left\{\dfrac\pi3,\;\dfrac{5\pi}3\right\}$ (avec $k=1$, $-\dfrac\pi3+2\pi=\dfrac{5\pi}3$).

La bonne réponse est **d)**.

### Pourquoi les autres réponses sont fausses

- **a)** $\left\{\dfrac\pi3,\;\dfrac{2\pi}3\right\}$ : on a utilisé la règle du sinus ($x=\pi-a$) au lieu de celle du cosinus ($x=-a$).
- **b)** $\left\{-\dfrac\pi3,\;\dfrac\pi3\right\}$ : $-\dfrac\pi3$ n'appartient pas à $[0\,;2\pi[$ ; il fallait ajouter $2\pi$.
- **c)** $\left\{\dfrac\pi6,\;\dfrac{11\pi}6\right\}$ : confusion des valeurs remarquables, $\cos\dfrac\pi6=\dfrac{\sqrt3}2$ et non $\dfrac12$.

</details>

Avis : 

---

## 82. `cqc-equation-trigonometrique-moyenne-3` (séries C/D/E)

**Énoncé :**

Quel est l'ensemble des solutions dans $]-\pi\,;\pi]$ de l'équation $\sin 2x=\sin\left(x+\dfrac\pi3\right)$ ?

- a) $\left\{\dfrac{2\pi}9,\;\dfrac\pi3\right\}$
- b) $\left\{-\dfrac{8\pi}9,\;-\dfrac{2\pi}9,\;\dfrac\pi3,\;\dfrac{4\pi}9\right\}$
- c) $\left\{\dfrac{2\pi}9,\;\dfrac\pi3,\;\dfrac{8\pi}9\right\}$
- d) $\left\{-\dfrac{4\pi}9,\;\dfrac{2\pi}9,\;\dfrac\pi3,\;\dfrac{8\pi}9\right\}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On ramène l'équation à une équation élémentaire ($\cos x=\cos a$, $\sin x=\sin a$, $\tan x=\tan a$), dont les solutions générales sont : $x=\pm a+2k\pi$ pour $\cos$, $x=a+2k\pi$ ou $x=\pi-a+2k\pi$ pour $\sin$ ; on retient ensuite celles de l'intervalle demandé.

### Corrigé

$\sin A=\sin B$ équivaut à $A=B+2k\pi$ ou $A=\pi-B+2k\pi$.

- $2x=x+\dfrac\pi3+2k\pi\iff x=\dfrac\pi3+2k\pi$.
- $2x=\pi-x-\dfrac\pi3+2k\pi\iff 3x=\dfrac{2\pi}3+2k\pi\iff x=\dfrac{2\pi}9+\dfrac{2k\pi}3$.

Dans $]-\pi\,;\pi]$ : première famille $\to\dfrac\pi3$ ; seconde famille ($k=-1$, $k=0$ et $k=1$) $\to-\dfrac{4\pi}9,\ \dfrac{2\pi}9,\ \dfrac{8\pi}9$.

$S=\left\{-\dfrac{4\pi}9,\;\dfrac{2\pi}9,\;\dfrac\pi3,\;\dfrac{8\pi}9\right\}$.

La bonne réponse est **d)**.

### Pourquoi les autres réponses sont fausses

- **a)** $\left\{\dfrac{2\pi}9,\;\dfrac\pi3\right\}$ : on a gardé $2k\pi$ au lieu de $\dfrac{2k\pi}3$ en divisant par $3$, ce qui fait perdre deux solutions.
- **b)** $\left\{-\dfrac{8\pi}9,\;-\dfrac{2\pi}9,\;\dfrac\pi3,\;\dfrac{4\pi}9\right\}$ : erreur de signe dans $\pi-B$ (on a écrit $\pi-x+\dfrac\pi3$).
- **c)** $\left\{\dfrac{2\pi}9,\;\dfrac\pi3,\;\dfrac{8\pi}9\right\}$ : on a oublié la valeur $k=-1$, qui donne $-\dfrac{4\pi}9\in\,]-\pi\,;\pi]$.

</details>

Avis : 

---

