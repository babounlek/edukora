# Vague « réécriture » (nouvelles questions à la place des écartées) : 161 QCM à faire relire par l'enseignant (campagne B1 maths)

Date : 2026-11-01. Les 433 questions de cette vague sont des **questions neuves**, écrites pour remplacer, sous le même identifiant, des questions ouvertes écartées aux vagues précédentes (trop faciles, démonstrations, notion hors programme d'une série). Même thème et même difficulté que l'ancienne question. 487 anciennes questions étudiées, 49 non réécrites (thème hors programme, cursus à revoir). Vous en voyez **161** : celles que le relecteur aveugle a assorties d'une remarque, celles dont des séries ont été retirées, et un tirage de 25 autres. Le lot est prêt mais n'est pas en ligne tant que vous n'avez pas répondu. Les 433 résolutions à l'aveugle donnent la clé, sauf 24 questions jugées hors niveau pour une série (série retirée ou déplacée).

## Séries retirées ou déplacées (à confirmer)

Appliqué selon vos avis (matrices et applications linéaires : série E seule au Probatoire ; similitudes, produit vectoriel, statistique à deux variables et variable aléatoire : Terminale ; coniques : pas en D ; complexes, suites, dérivée seconde : pas en A). Le détail par question est dans `series-retirees.json`. Quand une question n'avait plus de série, elle a été déplacée (Probatoire C/E vers BAC C/E, matrices vers Probatoire E).

## Points à trancher

1. **Dérivée, probabilités, somme et produit des racines en Probatoire A** : certaines nouvelles questions ont été écrites à ce niveau (polynômes, arbre pondéré) ; faut-il garder la série A ?
2. **Doublons** : deux questions identiques (produit vectoriel, parabole) ont été abandonnées ; deux autres sont voisines (aire d'un triangle rectangle).
3. **Trois questions sans série** ont été laissées ouvertes (somme et produit en Probatoire A, suite arithmétique en A).
4. **Limites hautes** (BEPC : rotation, diagonale du cube, histogramme à classes inégales ; Probatoire : matrice inverse 2x2, théorie des graphes).

Pour chaque question : **OK**, **à corriger** (dire quoi), **à retirer**, ou **retirer la série X**.

## 1. `cqc-ajustement-affine-faible-1` (séries BAC:A BAC:C BAC:D BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une coopérative agricole a relevé sa production de maïs $y$ (en tonnes) au cours de six années successives, numérotées par leur rang $x$ :

| Rang de l'année ($x$) | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Production en tonnes ($y$) | 3 | 6 | 6 | 10 | 12 | 11 |

On partage la série en deux groupes de trois points (les trois premières années, puis les trois dernières). Quelle est l'équation de la droite de Mayer de cette série ?

- a) $y=0{,}5x+4$
- b) $y=2x+1$
- c) $y=2x-1$
- d) $y=2x+7$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La droite de Mayer passe par les points moyens $G_1$ et $G_2$ des deux groupes. On calcule les coordonnées de chaque point moyen (moyenne des $x$, moyenne des $y$), puis le coefficient directeur $a=\dfrac{y_{G_2}-y_{G_1}}{x_{G_2}-x_{G_1}}$ et l'ordonnée à l'origine $b=y_{G_1}-a\,x_{G_1}$.

### Corrigé

Premier groupe : $x_{G_1}=\dfrac{1+2+3}{3}=2$ et $y_{G_1}=\dfrac{3+6+6}{3}=5$, donc $G_1(2\,;\,5)$.

Second groupe : $x_{G_2}=\dfrac{4+5+6}{3}=5$ et $y_{G_2}=\dfrac{10+12+11}{3}=11$, donc $G_2(5\,;\,11)$.

Coefficient directeur : $a=\dfrac{11-5}{5-2}=\dfrac{6}{3}=2$. Ordonnée à l'origine : $b=5-2\times2=1$.

La droite de Mayer a pour équation $y=2x+1$ (vérification avec $G_2$ : $2\times5+1=11$).

### Pourquoi les autres réponses sont fausses

- **a)** On a inversé le quotient : $\dfrac{5-2}{11-5}=0{,}5$ au lieu de $\dfrac{11-5}{5-2}$.
- **c)** Erreur de signe sur $b$ : on a calculé $a\,x_{G_1}-y_{G_1}=4-5$ au lieu de $y_{G_1}-a\,x_{G_1}$.
- **d)** On a mélangé les deux points : $b=y_{G_2}-a\,x_{G_1}=11-4=7$.

</details>

Avis : 

---

## 2. `cqc-covariance-prob-c-moyenne-4` (séries BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** LIMITE : covariance au Probatoire C/E, à vérifier au programme de 1re.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Un commerçant a relevé le prix de vente $x$ (en centaines de francs) d'un article et le nombre $y$ d'articles vendus (en dizaines) sur quatre semaines :

| Prix ($x$) | 2 | 4 | 6 | 8 |
|---|---|---|---|---|
| Ventes ($y$) | 5 | 4 | 2 | 1 |

Quelle est la covariance $\operatorname{cov}(x,y)$ de cette série double ?

- a) $3{,}5$
- b) $-3{,}5$
- c) $-14$
- d) $11{,}5$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La covariance d'une série double de $n$ couples est $\operatorname{cov}(x,y)=\dfrac1n\sum x_iy_i-\bar x\,\bar y$, ou de façon équivalente la moyenne des produits des écarts $(x_i-\bar x)(y_i-\bar y)$. Son signe indique le sens de variation conjoint des deux caractères.

### Corrigé

Moyennes : $\bar x=\dfrac{2+4+6+8}{4}=5$ et $\bar y=\dfrac{5+4+2+1}{4}=3$.

Moyenne des produits : $\dfrac{10+16+12+8}{4}=\dfrac{46}{4}=11{,}5$.

$$\operatorname{cov}(x,y)=11{,}5-5\times3=-3{,}5.$$
Vérification par les écarts : $\dfrac{(-3)(2)+(-1)(1)+(1)(-1)+(3)(-2)}{4}=\dfrac{-14}{4}=-3{,}5$. La covariance est négative : les ventes baissent quand le prix monte.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe : on a calculé $\bar x\,\bar y-\overline{xy}$.
- **c)** On a fait la somme des produits des écarts sans la diviser par l'effectif $4$.
- **d)** C'est la moyenne des produits $\overline{xy}$ : on a oublié de soustraire $\bar x\,\bar y$.

</details>

Avis : 

---

## 3. `cqc-denombrement-elevee-5` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : dénombrement à deux contraintes croisées (premier chiffre non nul et parité), exigeant pour Probatoire A.

**Énoncé :**

Un club attribue à chaque membre un numéro de badge formé de quatre chiffres. Ce numéro ne commence pas par $0$, ses quatre chiffres sont deux à deux distincts et il est pair.

Combien de numéros de badge différents peut-on former ?

- a) $2520$
- b) $2240$
- c) $2296$
- d) $2268$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand une contrainte porte sur une position (le dernier chiffre pair) et qu'une autre en dépend (le premier chiffre non nul), on sépare les cas selon le chiffre qui pose problème, ici $0$ en dernière position ou non, puis on applique le principe multiplicatif dans chaque cas et on additionne.

### Corrigé

**Cas 1 : le dernier chiffre est $0$.** Le premier chiffre se choisit parmi les $9$ chiffres non nuls, puis il reste $8$ choix pour le deuxième et $7$ pour le troisième : $9\times8\times7=504$ numéros.

**Cas 2 : le dernier chiffre est $2$, $4$, $6$ ou $8$** ($4$ choix). Le premier chiffre ne peut être ni $0$ ni le dernier chiffre : $8$ choix. Le deuxième : $8$ choix (on réintroduit $0$). Le troisième : $7$ choix. Soit $4\times8\times8\times7=1792$ numéros.

Les deux cas sont disjoints : $504+1792=2296$ numéros.

### Pourquoi les autres réponses sont fausses

- **a)** $5\times9\times8\times7$ : on a traité les cinq chiffres pairs de la même façon sans tenir compte de l'interdiction du $0$ en tête.
- **b)** $5\times8\times8\times7$ : on a appliqué à tous les chiffres pairs le décompte du cas 2, ce qui sous-compte le cas où le dernier chiffre est $0$.
- **d)** On a pris la moitié des $9\times9\times8\times7=4536$ numéros à chiffres distincts, comme si pairs et impairs étaient en nombre égal ; ce n'est pas vrai ici à cause du $0$.

</details>

Avis : 

---

## 4. `cqc-determinant-prob-c-faible-0` (séries PROBATOIRE:C PROBATOIRE:E)

**Énoncé :**

Dans un repère du plan, on donne les points $A(1\,;\,2)$, $B(4\,;\,-1)$ et $C(3\,;\,5)$.

Que vaut le déterminant $\det\big(\overrightarrow{AB},\overrightarrow{AC}\big)$ ?

- a) $15$
- b) $-15$
- c) $3$
- d) $23$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Le déterminant de deux vecteurs $\vec u(x\,;\,y)$ et $\vec v(x'\,;\,y')$, pris dans cet ordre, est $\det(\vec u,\vec v)=xy'-yx'$. On commence par calculer les coordonnées des vecteurs, $\overrightarrow{AB}(x_B-x_A\,;\,y_B-y_A)$, et non celles des points.

### Corrigé

$\overrightarrow{AB}(4-1\,;\,-1-2)=(3\,;\,-3)$ et $\overrightarrow{AC}(3-1\,;\,5-2)=(2\,;\,3)$.
$$\det\big(\overrightarrow{AB},\overrightarrow{AC}\big)=3\times3-(-3)\times2=9+6=15.$$
Ce déterminant étant non nul, les points $A$, $B$, $C$ ne sont pas alignés.

### Pourquoi les autres réponses sont fausses

- **b)** On a calculé $\det\big(\overrightarrow{AC},\overrightarrow{AB}\big)$ : échanger les deux vecteurs change le signe.
- **c)** On a additionné au lieu de soustraire : $xy'+yx'=9+(-6)=3$.
- **d)** On a utilisé les coordonnées des points $B$ et $C$ au lieu de celles des vecteurs : $4\times5-(-1)\times3=23$.

</details>

Avis : 

---

## 5. `cqc-forme-algebrique-d-un-quotient-moyenne-0` (séries BAC:A BAC:D)

**Séries modifiées :** retirées BAC:A.

**Remarque du relecteur :** Nombres complexes hors programme de la série A (BAC A listé) : retirer BAC:A des séries.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Quelle est la forme algébrique du nombre complexe
$$W=\dfrac{(2-i)^2}{1+i}\ ?$$

- a) $W=\dfrac72-\dfrac12\,i$
- b) $W=-\dfrac12-\dfrac72\,i$
- c) $W=\dfrac52-\dfrac52\,i$
- d) $W=\dfrac72-\dfrac72\,i$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On développe d'abord le numérateur sous forme algébrique (avec $i^2=-1$), puis on multiplie numérateur et dénominateur par le conjugué du dénominateur : $(a+bi)(a-bi)=a^2+b^2$.

### Corrigé

Numérateur : $(2-i)^2=4-4i+i^2=3-4i$.

Le conjugué de $1+i$ est $1-i$ et $(1+i)(1-i)=2$ :
$$W=\frac{(3-4i)(1-i)}{2}=\frac{3-3i-4i+4i^2}{2}=\frac{-1-7i}{2}=-\frac12-\frac72\,i.$$

### Pourquoi les autres réponses sont fausses

- **a)** On a multiplié par $1+i$ au lieu du conjugué $1-i$, tout en divisant par $2$.
- **c)** On a écrit $(2-i)^2=4+1=5$ en oubliant le double produit et en se trompant sur $i^2$.
- **d)** On a pris $i^2=+1$ dans le produit $(3-4i)(1-i)$.

</details>

Avis : 

---

## 6. `cqc-loi-de-probabilite-elevee-5` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D)

**Séries modifiées :** retirées PROBATOIRE:A, PROBATOIRE:C, PROBATOIRE:D.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une variable aléatoire $X$ prend les valeurs $0$, $1$, $2$ et $3$. Sa loi de probabilité est donnée par le tableau suivant, où $a$ et $b$ sont deux réels :

| $x_i$ | $0$ | $1$ | $2$ | $3$ |
|---|---|---|---|---|
| $P(X=x_i)$ | $a$ | $2a$ | $b$ | $0{,}1$ |

On sait de plus que l'espérance de $X$ vaut $E(X)=1{,}5$. Que vaut $P(X=2)$ ?

- a) $0{,}4$
- b) $0{,}675$
- c) $0{,}45$
- d) $0{,}15$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Deux informations donnent deux équations : la somme des probabilités d'une loi vaut $1$, et $E(X)=\sum x_i\,P(X=x_i)$. On résout le système obtenu, puis on vérifie que toutes les probabilités sont comprises entre $0$ et $1$.

### Corrigé

Somme des probabilités : $a+2a+b+0{,}1=1$, soit $3a+b=0{,}9$.

Espérance : $0\times a+1\times2a+2b+3\times0{,}1=1{,}5$, soit $2a+2b=1{,}2$, c'est-à-dire $a+b=0{,}6$.

Par soustraction : $2a=0{,}3$, donc $a=0{,}15$ et $b=0{,}6-0{,}15=0{,}45$.

Vérification : $0{,}15+0{,}3+0{,}45+0{,}1=1$ et $0{,}3+0{,}9+0{,}3=1{,}5$. Donc $P(X=2)=b=0{,}45$.

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié la probabilité $0{,}1$ dans la somme ($3a+b=1$), d'où $a=0{,}2$ et $b=0{,}4$ ; la somme totale vaudrait alors $1{,}1$.
- **b)** On a oublié le terme $3\times0{,}1$ dans l'espérance ($a+b=0{,}75$).
- **d)** C'est la valeur de $a=P(X=0)$, pas celle de $P(X=2)$.

</details>

Avis : 

---

## 7. `cqc-matrice-inverse-prob-c-elevee-5` (séries PROBATOIRE:C)

**Séries modifiées :** retirées PROBATOIRE:C ; ajoutées PROBATOIRE:E.

**Remarque du relecteur :** LIMITE : l'inverse d'une matrice 2x2 au Probatoire C est à confirmer selon le programme en vigueur.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On considère la matrice carrée d'ordre 2
$$A=\begin{pmatrix}3&-1\\5&-2\end{pmatrix}.$$
Quelle est sa matrice inverse $A^{-1}$ ?

- a) $\begin{pmatrix}-2&1\\-5&3\end{pmatrix}$
- b) $\begin{pmatrix}2&1\\5&-3\end{pmatrix}$
- c) $\begin{pmatrix}2&5\\-1&-3\end{pmatrix}$
- d) $\begin{pmatrix}2&-1\\5&-3\end{pmatrix}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour $A=\begin{pmatrix}a&b\\c&d\end{pmatrix}$ de déterminant $ad-bc\neq0$ :
$$A^{-1}=\frac{1}{ad-bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}.$$
On échange les termes de la diagonale, on change le signe des deux autres, puis on divise par le déterminant (attention à son signe). On vérifie en calculant $A\,A^{-1}$.

### Corrigé

$\det A=3\times(-2)-(-1)\times5=-6+5=-1\neq0$ : $A$ est inversible.
$$A^{-1}=\frac{1}{-1}\begin{pmatrix}-2&1\\-5&3\end{pmatrix}=\begin{pmatrix}2&-1\\5&-3\end{pmatrix}.$$
Vérification : $\begin{pmatrix}3&-1\\5&-2\end{pmatrix}\begin{pmatrix}2&-1\\5&-3\end{pmatrix}=\begin{pmatrix}6-5&-3+3\\10-10&-5+6\end{pmatrix}=\begin{pmatrix}1&0\\0&1\end{pmatrix}$.

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié de diviser par le déterminant, qui vaut $-1$ et non $1$.
- **b)** On a échangé la diagonale sans changer le signe des deux autres coefficients.
- **c)** On a transposé au lieu d'échanger la diagonale et de changer les signes : la place de $-b$ et $-c$ est inversée.

</details>

Avis : 

---

## 8. `cqc-nuage-de-points-faible-0` (séries BAC:A BAC:D BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Un commerçant a noté, sur cinq semaines, le nombre $x$ de messages publicitaires diffusés à la radio et le nombre $y$ de clients (en dizaines). La dernière valeur de $y$ a été effacée :

| Messages ($x$) | 1 | 2 | 4 | 6 | 7 |
|---|---|---|---|---|---|
| Clients ($y$) | 6 | 8 | 11 | 14 | $y_5$ |

On sait que le point moyen du nuage de points est $G(4\,;\,11)$. Quelle est la valeur de $y_5$ ?

- a) $11$
- b) $5$
- c) $55$
- d) $16$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Le point moyen $G(\bar x\,;\,\bar y)$ d'un nuage de $n$ points a pour coordonnées les moyennes des $x_i$ et des $y_i$. Connaître $\bar y$ revient à connaître la somme $\sum y_i=n\,\bar y$, ce qui permet de retrouver une valeur manquante.

### Corrigé

On vérifie d'abord $\bar x=\dfrac{1+2+4+6+7}{5}=\dfrac{20}{5}=4$. Le nuage compte $5$ points, donc $\sum y_i=5\times11=55$.

Or $6+8+11+14=39$, d'où $y_5=55-39=16$.

### Pourquoi les autres réponses sont fausses

- **a)** On a supposé que la valeur manquante est égale à la moyenne $\bar y$.
- **b)** On a divisé par $4$ au lieu de $5$ : $4\times11-39=5$.
- **c)** C'est la somme $\sum y_i$ : on a oublié de retirer les quatre valeurs connues.

</details>

Avis : 

---

## 9. `cqc-probabilites-moyenne-0` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PROBATOIRE:A)

**Remarque du relecteur :** LIMITE : formule des probabilités totales, à vérifier au programme de Probatoire A (listé).

**Énoncé :**

Un grossiste reçoit $70\,\%$ de ses sacs de riz de la coopérative $X$ et le reste de la coopérative $Y$. On sait que $4\,\%$ des sacs venant de $X$ et $10\,\%$ des sacs venant de $Y$ sont abîmés. On choisit un sac au hasard dans son entrepôt.

Quelle est la probabilité que ce sac soit abîmé ?

- a) $0{,}14$
- b) $0{,}07$
- c) $0{,}058$
- d) $0{,}028$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand la population se partage en plusieurs groupes de proportions connues, la probabilité d'un événement s'obtient avec un arbre pondéré : on multiplie les probabilités le long de chaque branche qui mène à l'événement, puis on additionne les branches (formule des probabilités totales).

### Corrigé

Notons $A$ l'événement « le sac est abîmé ». $P(X)=0{,}7$ et $P(Y)=1-0{,}7=0{,}3$.
$$P(A)=P(X)\times P_X(A)+P(Y)\times P_Y(A)=0{,}7\times0{,}04+0{,}3\times0{,}1=0{,}028+0{,}03=0{,}058.$$

### Pourquoi les autres réponses sont fausses

- **a)** On a additionné les deux pourcentages $4\,\%+10\,\%$ sans les pondérer par la part de chaque coopérative.
- **b)** On a fait la moyenne simple des deux pourcentages, comme si chaque coopérative fournissait la moitié des sacs.
- **d)** On n'a gardé que la branche de la coopérative $X$ ($0{,}7\times0{,}04$).

</details>

Avis : 

---

## 10. `cqc-racine-evidente-faible-1` (séries BAC:A BAC:C PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées BAC:A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On considère le polynôme $P(x)=x^3+x^2-5x+3$. On remarque que $P(1)=0$.

Quelle est la factorisation complète de $P(x)$ en produit de facteurs du premier degré ?

- a) $(x+1)^2(x-3)$
- b) $(x-1)(x+1)(x+3)$
- c) $(x-1)(x^2+2x+3)$
- d) $(x-1)^2(x+3)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Si $\alpha$ est racine d'un polynôme $P$, alors $P(x)=(x-\alpha)Q(x)$ où $Q$ s'obtient par division euclidienne ou par identification des coefficients. On factorise ensuite $Q$ (second degré) ; une racine peut apparaître deux fois.

### Corrigé

Comme $P(1)=1+1-5+3=0$, on cherche $P(x)=(x-1)(x^2+bx+c)$. En développant : $x^3+(b-1)x^2+(c-b)x-c$. Par identification, $b-1=1$ et $-c=3$, d'où $b=2$ et $c=-3$ (contrôle : $c-b=-5$).

$P(x)=(x-1)(x^2+2x-3)$. Le trinôme $x^2+2x-3$ a pour racines $1$ et $-3$ : $x^2+2x-3=(x-1)(x+3)$.

Donc $P(x)=(x-1)^2(x+3)$ : $1$ est racine double.

### Pourquoi les autres réponses sont fausses

- **a)** Erreurs de signe : $(x+1)^2(x-3)$ a pour racines $-1$ et $3$, or $P(-1)=8\neq0$.
- **b)** On a pris $-1$ pour seconde racine du trinôme sans vérifier ; en fait $1$ est racine double.
- **c)** Erreur de signe sur $c$ lors de l'identification ($c=3$ au lieu de $-3$) ; de plus ce n'est pas une factorisation en facteurs du premier degré.

</details>

Avis : 

---

## 11. `cqc-similitude-moyenne-2` (séries BAC:C BAC:E BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** Les similitudes directes en écriture complexe relèvent de la Terminale (C, E) ; hors programme pour le Probatoire C/E listé.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan complexe est muni d'un repère orthonormé direct. On considère la similitude directe $s$ de centre $\Omega$ d'affixe $1+i$, de rapport $2$ et d'angle $\dfrac{\pi}{2}$.

Quelle est l'écriture complexe de $s$ ?

- a) $z'=2iz+1+i$
- b) $z'=2iz+1-3i$
- c) $z'=iz+2$
- d) $z'=2iz+3-i$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

La similitude directe de centre $\Omega(\omega)$, de rapport $k$ et d'angle $\theta$ a pour écriture $z'-\omega=a(z-\omega)$ avec $a=k\,e^{i\theta}$. On développe pour obtenir la forme $z'=az+b$, et on vérifie que $\omega$ est invariant.

### Corrigé

Ici $a=2e^{i\pi/2}=2i$ et $\omega=1+i$ :
$$z'=2i\big(z-(1+i)\big)+1+i=2iz-2i-2i^2+1+i=2iz+3-i.$$
Vérification : $2i(1+i)+3-i=2i-2+3-i=1+i=\omega$.

### Pourquoi les autres réponses sont fausses

- **a)** On a écrit $z'=az+\omega$ en prenant le centre pour terme constant : $\omega$ n'est alors pas invariant.
- **b)** Erreur de signe : on a écrit $z'=a(z-\omega)-\omega$ au lieu de $+\omega$.
- **c)** On a pris $a=i$ en oubliant le rapport $2$.

</details>

Avis : 

---

## 12. `cqc-solution-particuliere-moyenne-4` (séries BAC:C BAC:D BAC:E BAC:TI)

**Énoncé :**

On considère l'équation différentielle
$$(E)\,:\ 2y'+3y=6x+1.$$
Quelle fonction affine est une solution particulière de $(E)$ sur $\mathbb{R}$ ?

- a) $x\mapsto2x-1$
- b) $x\mapsto2x+\dfrac13$
- c) $x\mapsto3x-\dfrac53$
- d) $x\mapsto2x+\dfrac53$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On cherche une solution de la forme $y_0(x)=ax+b$ : alors $y_0'(x)=a$. On remplace dans l'équation et on identifie les coefficients de $x$ et les termes constants des deux membres.

### Corrigé

Avec $y_0(x)=ax+b$ : $2a+3(ax+b)=6x+1$, soit $3ax+(2a+3b)=6x+1$.

Identification : $3a=6$ donc $a=2$ ; $2a+3b=1$ donc $3b=1-4=-3$ et $b=-1$.

$y_0(x)=2x-1$. Vérification : $2\times2+3(2x-1)=6x+1$.

### Pourquoi les autres réponses sont fausses

- **b)** On a oublié le terme $2a$ venant de $2y'$ : $3b=1$.
- **c)** On a divisé $6$ par le coefficient de $y'$ au lieu de celui de $y$ : $2a=6$.
- **d)** Erreur de signe en isolant $3b$ : $3b=1+2a$ au lieu de $1-2a$.

</details>

Avis : 

---

## 13. `cqc-variable-aleatoire-moyenne-4` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:C)

**Séries modifiées :** retirées PROBATOIRE:C.

**Remarque du relecteur :** Variable aléatoire : notion de Terminale, hors programme du Probatoire C listé.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On lance deux fois de suite un dé équilibré à quatre faces numérotées de $1$ à $4$. On note $X$ la variable aléatoire égale au plus grand des deux numéros obtenus (si les deux numéros sont égaux, $X$ est égal à ce numéro).

Que vaut $P(X=3)$ ?

- a) $\dfrac{5}{16}$
- b) $\dfrac14$
- c) $\dfrac{3}{16}$
- d) $\dfrac38$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour établir la loi d'une variable définie sur deux épreuves, on dresse le tableau à double entrée des issues, toutes équiprobables, et on compte celles qui donnent la valeur cherchée, sans oublier l'ordre des lancers ni compter deux fois une même issue.

### Corrigé

Il y a $4\times4=16$ issues équiprobables (couples ordonnés). $X=3$ lorsque les deux numéros sont au plus $3$ et que l'un au moins vaut $3$ :
$$(1;3),\ (2;3),\ (3;3),\ (3;1),\ (3;2).$$
Soit $5$ issues : $P(X=3)=\dfrac{5}{16}$. (Contrôle : $3^2-2^2=5$.)

### Pourquoi les autres réponses sont fausses

- **b)** On a supposé les quatre valeurs de $X$ équiprobables ; or $X=4$ est plus fréquent que $X=1$.
- **c)** On n'a compté que les couples où le premier lancer donne $3$, en oubliant l'ordre.
- **d)** On a compté le couple $(3;3)$ deux fois : $6$ issues au lieu de $5$.

</details>

Avis : 

---

## 14. `cqc-ajustement-affine-moyenne-0` (séries BAC:A BAC:C BAC:D BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une coopérative relève sa production de cacao pendant six années consécutives ($x$ : rang de l'année ; $y$ : production en tonnes).

| Rang $x$ | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Production $y$ | 10 | 15 | 17 | 20 | 22 | 27 |

On ajuste ce nuage par la méthode de Mayer, en formant deux groupes de trois points pris dans l'ordre des abscisses croissantes. Quelle est l'équation de la droite d'ajustement obtenue ?

- a) $y=3{,}4x+6{,}6$
- b) $y=3x+20$
- c) $y=\dfrac13x+\dfrac{40}{3}$
- d) $y=3x+8$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Méthode de Mayer : on partage la série, classée par abscisses croissantes, en deux groupes de même effectif ; on calcule le point moyen de chaque groupe, $G_1(\bar x_1;\bar y_1)$ et $G_2(\bar x_2;\bar y_2)$ ; la droite d'ajustement est $(G_1G_2)$, de coefficient directeur $a=\dfrac{\bar y_2-\bar y_1}{\bar x_2-\bar x_1}$, et l'ordonnée à l'origine se déduit de $\bar y_1=a\bar x_1+b$.

### Corrigé

Groupe 1 : $\bar x_1=\dfrac{1+2+3}{3}=2$ et $\bar y_1=\dfrac{10+15+17}{3}=14$, d'où $G_1(2;14)$.

Groupe 2 : $\bar x_2=\dfrac{4+5+6}{3}=5$ et $\bar y_2=\dfrac{20+22+27}{3}=23$, d'où $G_2(5;23)$.

Coefficient directeur : $a=\dfrac{23-14}{5-2}=\dfrac93=3$.

Ordonnée à l'origine : $14=3\times2+b$, donc $b=8$.

La droite de Mayer a pour équation $y=3x+8$. Contrôle avec $G_2$ : $3\times5+8=23$.

### Pourquoi les autres réponses sont fausses

- **a)** c'est la droite qui passe par le premier et le dernier point du tableau, $(1;10)$ et $(6;27)$, et non par les deux points moyens.
- **b)** erreur de signe dans le calcul de $b$ : $b=14-3\times2=8$ et non $14+6=20$.
- **c)** le coefficient directeur a été calculé à l'envers, $\dfrac{\bar x_2-\bar x_1}{\bar y_2-\bar y_1}=\dfrac13$.

</details>

Avis : 

---

## 15. `cqc-cube-moyenne-1` (séries BEPC:)

**Remarque du relecteur :** LIMITE : diagonale du cube par Pythagore appliqué deux fois, haut de programme BEPC.

**Énoncé :**

$ABCDEFGH$ est un cube d'arête $4$ cm : $ABCD$ est la face du dessous, $EFGH$ la face du dessus, et $E$, $F$, $G$, $H$ sont situés respectivement au-dessus de $A$, $B$, $C$, $D$.

Quelle est la longueur de la diagonale $[AG]$ du cube ?

- a) $4\sqrt3$ cm
- b) $4\sqrt2$ cm
- c) $48$ cm
- d) $12$ cm

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour calculer une longueur dans un solide, on cherche un triangle rectangle contenu dans un plan du solide et on applique le théorème de Pythagore, quitte à l'appliquer deux fois de suite (d'abord dans une face, puis dans un plan qui traverse le solide).

### Corrigé

Dans le carré $ABCD$, le triangle $ABC$ est rectangle en $B$ :
$$AC^2=AB^2+BC^2=16+16=32.$$

L'arête $[CG]$ est perpendiculaire à la face $ABCD$, donc à la droite $(AC)$ : le triangle $ACG$ est rectangle en $C$.
$$AG^2=AC^2+CG^2=32+16=48.$$

$$AG=\sqrt{48}=\sqrt{16\times3}=4\sqrt3\ \text{cm}\approx6{,}93\ \text{cm}.$$

### Pourquoi les autres réponses sont fausses

- **b)** $4\sqrt2$ cm est la diagonale $AC$ d'une face ; il manque la seconde application de Pythagore dans le triangle $ACG$.
- **c)** $48$ est la valeur de $AG^2$ : on a oublié de prendre la racine carrée.
- **d)** on a additionné trois arêtes ($4+4+4$) : le chemin qui suit les arêtes est plus long que la diagonale.

</details>

Avis : 

---

## 16. `cqc-derivee-d-un-quotient-tle-c-moyenne-2` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:A)

**Remarque du relecteur :** LIMITE : dérivée d'un quotient pour Probatoire A.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}\setminus\{1\}$ par
$$f(x)=\frac{x^2+1}{x-1}.$$

Quelle est l'expression de $f'(x)$ ?

- a) $f'(x)=2x$
- b) $f'(x)=\dfrac{x^2-2x-1}{(x-1)^2}$
- c) $f'(x)=\dfrac{3x^2-2x+1}{(x-1)^2}$
- d) $f'(x)=\dfrac{-x^2+2x+1}{(x-1)^2}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour $f=\dfrac uv$ avec $u$ et $v$ dérivables et $v$ non nulle, $f'=\dfrac{u'v-uv'}{v^2}$. L'ordre des termes au numérateur compte (signe moins), et on ne dérive pas séparément le numérateur et le dénominateur.

### Corrigé

On pose $u(x)=x^2+1$ et $v(x)=x-1$, d'où $u'(x)=2x$ et $v'(x)=1$.

$$f'(x)=\frac{2x(x-1)-(x^2+1)\times1}{(x-1)^2}=\frac{2x^2-2x-x^2-1}{(x-1)^2}=\frac{x^2-2x-1}{(x-1)^2}.$$

Contrôle numérique en $x=2$ : la formule donne $\dfrac{4-4-1}{1}=-1$, et le taux d'accroissement $\dfrac{f(2{,}001)-f(1{,}999)}{0{,}002}$ vaut environ $-1$.

### Pourquoi les autres réponses sont fausses

- **a)** on a dérivé séparément le numérateur ($2x$) et le dénominateur ($1$) puis fait le quotient : ce n'est pas la formule de dérivation d'un quotient.
- **c)** on a utilisé $u'v+uv'$ au lieu de $u'v-uv'$ (formule d'un produit).
- **d)** on a calculé $uv'-u'v$ : le numérateur a le mauvais signe.

</details>

Avis : 

---

## 17. `cqc-excentricite-faible-0` (séries BAC:C BAC:D BAC:E)

**Séries modifiées :** retirées BAC:D.

**Remarque du relecteur :** LIMITE : les coniques relèvent surtout des séries C et E ; vérifier leur présence au programme de la série D.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, la conique $(\Gamma)$ a pour équation
$$25x^2+9y^2=225.$$

Quelle est son excentricité ?

- a) $\dfrac35$
- b) $\dfrac43$
- c) $\dfrac{\sqrt{34}}{5}$
- d) $\dfrac45$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On met l'équation sous forme réduite $\dfrac{x^2}{\alpha^2}+\dfrac{y^2}{\beta^2}=1$. Le demi-grand axe $a$ est le plus grand des deux nombres $\alpha$ et $\beta$, le demi-petit axe $b$ le plus petit ; alors $c=\sqrt{a^2-b^2}$ et l'excentricité vaut $e=\dfrac ca$. Le grand axe n'est pas toujours porté par l'axe des abscisses.

### Corrigé

En divisant par $225$ :
$$\frac{x^2}{9}+\frac{y^2}{25}=1.$$

Ici $25>9$ : le grand axe est porté par l'axe des ordonnées, avec $a=5$ et $b=3$.

$$c=\sqrt{a^2-b^2}=\sqrt{25-9}=4,\qquad e=\frac ca=\frac45.$$

On a bien $0<e<1$ : $(\Gamma)$ est une ellipse.

### Pourquoi les autres réponses sont fausses

- **a)** $\dfrac35=\dfrac ba$ : on a pris le demi-petit axe à la place de $c$.
- **b)** on a pris pour $a$ le nombre $3$ associé à $x$ ; or le demi-grand axe vaut $5$ et il est porté par l'axe des ordonnées.
- **c)** on a calculé $c^2=a^2+b^2=34$, relation valable pour une hyperbole, pas pour une ellipse.

</details>

Avis : 

---

## 18. `cqc-forme-canonique-prob-c-moyenne-3` (séries PROBATOIRE:C PROBATOIRE:E)

**Énoncé :**

Quelle est la forme canonique du trinôme
$$f(x)=2x^2-12x+13\ ?$$

- a) $2(x-3)^2+4$
- b) $2(x-3)^2-5$
- c) $2(x+3)^2-5$
- d) $2(x-6)^2-59$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour $ax^2+bx+c$ avec $a\neq1$, on met d'abord $a$ en facteur dans les termes en $x^2$ et en $x$, puis on complète le carré : $x^2-2\alpha x=(x-\alpha)^2-\alpha^2$. Le terme $-\alpha^2$ se trouve à l'intérieur de la parenthèse multipliée par $a$ : il faut donc le multiplier par $a$ en développant.

### Corrigé

$$f(x)=2(x^2-6x)+13=2\big[(x-3)^2-9\big]+13=2(x-3)^2-18+13=2(x-3)^2-5.$$

Contrôle en $x=0$ : $2\times9-5=13=f(0)$ ; en $x=1$ : $2\times4-5=3$ et $f(1)=2-12+13=3$.

### Pourquoi les autres réponses sont fausses

- **a)** on a retranché $9$ au lieu de $2\times9=18$ : le $-9$ placé dans le crochet est multiplié par $2$.
- **c)** erreur de signe : $x^2-6x$ s'écrit $(x-3)^2-9$ et non $(x+3)^2-9$ (cette expression vaut $27$ en $x=1$, pas $3$).
- **d)** on a complété le carré à partir de $x^2-12x$ sans avoir mis $2$ en facteur ; $2(x-6)^2-59$ développé donne $2x^2-24x+13$.

</details>

Avis : 

---

## 19. `cqc-loi-de-probabilite-faible-1` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D)

**Séries modifiées :** retirées PROBATOIRE:A, PROBATOIRE:C, PROBATOIRE:D.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans un jeu, le gain $X$ d'un joueur (en centaines de F CFA, une valeur négative étant une perte) suit la loi de probabilité suivante, où $p$ est un réel :

| $x_i$ | $-2$ | $0$ | $3$ | $5$ |
|---|---|---|---|---|
| $P(X=x_i)$ | $0{,}2$ | $0{,}35$ | $p$ | $0{,}15$ |

Quelle est l'espérance mathématique $E(X)$ ?

- a) $0{,}35$
- b) $1{,}5$
- c) $1{,}25$
- d) $2{,}45$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

La somme des probabilités d'une loi de probabilité vaut $1$, ce qui permet de trouver une probabilité manquante. L'espérance est la moyenne des valeurs pondérée par leurs probabilités : $E(X)=\sum x_i\,P(X=x_i)$.

### Corrigé

Probabilité manquante : $p=1-(0{,}2+0{,}35+0{,}15)=1-0{,}7=0{,}3$.

$$E(X)=(-2)\times0{,}2+0\times0{,}35+3\times0{,}3+5\times0{,}15=-0{,}4+0+0{,}9+0{,}75=1{,}25.$$

En moyenne, le joueur gagne $1{,}25$ centaine de F CFA par partie, soit $125$ F CFA.

### Pourquoi les autres réponses sont fausses

- **a)** on a oublié le terme $3\times p$, faute d'avoir calculé la probabilité manquante.
- **b)** c'est la moyenne simple des quatre valeurs, sans tenir compte de leurs probabilités.
- **d)** on a pris $p=0{,}7$ (la somme des probabilités connues) au lieu de $p=1-0{,}7=0{,}3$.

</details>

Avis : 

---

## 20. `cqc-nuage-de-points-faible-1` (séries BAC:A BAC:D BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le tableau donne, pour quatre semaines consécutives (rang $x$), le nombre $y$ de commandes reçues par un petit atelier :

| $x$ | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| $y$ | 2 | 3 | 5 | 6 |

Quelle est la covariance $\text{cov}(x,y)$ de cette série à deux variables ?

- a) $11{,}75$
- b) $7$
- c) $\dfrac73$
- d) $1{,}75$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une série de $n$ couples $(x_i;y_i)$ de même poids, $\text{cov}(x,y)=\dfrac1n\sum x_iy_i-\bar x\,\bar y$, ce qui revient à $\dfrac1n\sum(x_i-\bar x)(y_i-\bar y)$. On divise par $n$, l'effectif total.

### Corrigé

$\bar x=\dfrac{1+2+3+4}{4}=2{,}5$ et $\bar y=\dfrac{2+3+5+6}{4}=4$.

$\displaystyle\sum x_iy_i=2+6+15+24=47$, d'où $\dfrac{47}{4}=11{,}75$.

$$\text{cov}(x,y)=11{,}75-2{,}5\times4=11{,}75-10=1{,}75.$$

Contrôle par les écarts : $(-1{,}5)(-2)+(-0{,}5)(-1)+(0{,}5)(1)+(1{,}5)(2)=3+0{,}5+0{,}5+3=7$, et $\dfrac74=1{,}75$.

### Pourquoi les autres réponses sont fausses

- **a)** $11{,}75$ est la moyenne des produits $x_iy_i$ ; on a oublié de retrancher $\bar x\,\bar y$.
- **b)** $7$ est la somme des produits des écarts ; on a oublié de la diviser par l'effectif $4$.
- **c)** on a divisé par $n-1=3$ au lieu de $n=4$.

</details>

Avis : 

---

## 21. `cqc-point-moyen-elevee-0` (séries BAC:A BAC:D BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une enquête porte sur $10$ ménages : $x$ est le nombre de personnes du ménage et $y$ la consommation d'eau mensuelle (en $\text{m}^3$). Les résultats sont regroupés ainsi :

| $x$ | 1 | 2 | 4 |
|---|---|---|---|
| $y$ | 5 | 8 | 11 |
| Nombre de ménages | 2 | 3 | 5 |

Quelles sont les coordonnées du point moyen $G$ de cette série ?

- a) $G(2{,}8\,;\,8{,}9)$
- b) $G\left(\dfrac73\,;\,8\right)$
- c) $G\left(\dfrac{28}{3}\,;\,\dfrac{89}{3}\right)$
- d) $G(2{,}8\,;\,8)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Le point moyen $G(\bar x;\bar y)$ a pour coordonnées les moyennes des deux variables. Quand chaque couple est observé plusieurs fois, ce sont des moyennes **pondérées** par les effectifs, et l'on divise par l'effectif total $N$, pas par le nombre de colonnes du tableau.

### Corrigé

Effectif total : $N=2+3+5=10$.

$$\bar x=\frac{2\times1+3\times2+5\times4}{10}=\frac{28}{10}=2{,}8$$

$$\bar y=\frac{2\times5+3\times8+5\times11}{10}=\frac{89}{10}=8{,}9$$

Donc $G(2{,}8\,;\,8{,}9)$.

### Pourquoi les autres réponses sont fausses

- **b)** ce sont les moyennes simples des valeurs du tableau, sans tenir compte du nombre de ménages.
- **c)** les sommes pondérées sont justes, mais on les a divisées par $3$ (nombre de colonnes) au lieu de l'effectif total $10$.
- **d)** $\bar x$ est pondéré mais pas $\bar y$ ($\dfrac{5+8+11}{3}=8$) : la pondération doit s'appliquer aux deux variables.

</details>

Avis : 

---

## 22. `cqc-produit-vectoriel-elevee-5` (séries BAC:C BAC:E PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** LIMITE : au Probatoire C/E le produit vectoriel n'est pas au programme ; faisable par le produit scalaire (aire = 1/2*sqrt(AB²AC²-(AB.AC)²)), formule peu usuelle en Première.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans l'espace muni d'un repère orthonormé, on considère les points $A(1;0;2)$, $B(3;1;2)$ et $C(1;2;5)$.

Quelle est l'aire du triangle $ABC$ (en unités d'aire) ?

- a) $\sqrt{61}$
- b) $1$
- c) $\dfrac{\sqrt{61}}{2}$
- d) $\dfrac{\sqrt{65}}{2}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

L'aire du triangle $ABC$ vaut $\dfrac12\big\|\overrightarrow{AB}\wedge\overrightarrow{AC}\big\|$ : la norme du produit vectoriel est l'aire du parallélogramme construit sur les deux vecteurs, et le triangle en est la moitié. Pour $\vec u(x;y;z)$ et $\vec v(x';y';z')$, $\vec u\wedge\vec v=(yz'-zy'\,;\,zx'-xz'\,;\,xy'-yx')$.

### Corrigé

$\overrightarrow{AB}(2;1;0)$ et $\overrightarrow{AC}(0;2;3)$.

$$\overrightarrow{AB}\wedge\overrightarrow{AC}=(1\times3-0\times2\,;\,0\times0-2\times3\,;\,2\times2-1\times0)=(3\,;\,-6\,;\,4).$$

Contrôle : $(3;-6;4)\cdot(2;1;0)=6-6=0$ et $(3;-6;4)\cdot(0;2;3)=-12+12=0$.

$$\big\|\overrightarrow{AB}\wedge\overrightarrow{AC}\big\|=\sqrt{9+36+16}=\sqrt{61},\qquad \mathcal A=\frac{\sqrt{61}}{2}\approx3{,}91.$$

### Pourquoi les autres réponses sont fausses

- **a)** $\sqrt{61}$ est l'aire du parallélogramme construit sur $\overrightarrow{AB}$ et $\overrightarrow{AC}$ ; on a oublié le facteur $\dfrac12$.
- **b)** on a utilisé le produit scalaire ($\overrightarrow{AB}\cdot\overrightarrow{AC}=2$) au lieu du produit vectoriel.
- **d)** $\dfrac12AB\times AC=\dfrac{\sqrt5\times\sqrt{13}}{2}$ suppose le triangle rectangle en $A$, ce qui est faux ici.

</details>

Avis : 

---

## 23. `cqc-racine-evidente-moyenne-1` (séries BAC:A BAC:C PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées BAC:A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $Q$ le polynôme défini par $Q(x)=2x^3-3x^2-11x+6$.

Quel est l'ensemble des solutions réelles de l'équation $Q(x)=0$ ?

- a) $\left\{-2\,;\,\dfrac12\,;\,3\right\}$
- b) $\left\{2\,;\,-\dfrac12\,;\,-3\right\}$
- c) $\left\{\dfrac12\,;\,3\right\}$
- d) $\{-2\,;\,1\,;\,3\}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On cherche une racine évidente parmi des entiers simples ($\pm1$, $\pm2$, $\pm3$...). Si $r$ est racine, $Q(x)$ se factorise par $(x-r)$ : on écrit $Q(x)=(x-r)(ax^2+bx+c)$ et on trouve $a$, $b$, $c$ par identification. On résout ensuite l'équation du second degré restante, sans oublier la racine $r$.

### Corrigé

Essais : $Q(1)=-6$, $Q(-1)=12$, $Q(2)=-12$, $Q(-2)=-16-12+22+6=0$. Donc $-2$ est racine évidente.

On écrit $Q(x)=(x+2)(2x^2+bx+c)=2x^3+(b+4)x^2+(c+2b)x+2c$.

Identification : $b+4=-3$ donc $b=-7$ ; $2c=6$ donc $c=3$ ; contrôle : $c+2b=3-14=-11$.

$$Q(x)=(x+2)(2x^2-7x+3).$$

Pour $2x^2-7x+3$ : $\Delta=49-24=25$, racines $\dfrac{7-5}{4}=\dfrac12$ et $\dfrac{7+5}{4}=3$.

Ensemble des solutions : $\left\{-2\,;\,\dfrac12\,;\,3\right\}$.

### Pourquoi les autres réponses sont fausses

- **b)** on a changé le signe de toutes les racines (racine lue « $+2$ » dans le facteur $x+2$, etc.) ; par exemple $Q(2)=-12\neq0$.
- **c)** on a résolu seulement l'équation du second degré et oublié la racine évidente $-2$.
- **d)** le facteur $2x-1$ s'annule pour $x=\dfrac12$, pas pour $x=1$ ; d'ailleurs $Q(1)=-6\neq0$.

</details>

Avis : 

---

## 24. `cqc-rotation-elevee-5` (séries BAC:C BAC:D BAC:E BAC:TI BEPC: PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : au BEPC, calcul des coordonnées d'une image par rotation peu courant (faisable sur quadrillage).

**Énoncé :**

Dans un repère orthonormé, on considère les points $\Omega(1;2)$ et $A(4;3)$. Le point $A'$ est l'image de $A$ par le quart de tour de centre $\Omega$ dans le sens contraire des aiguilles d'une montre (rotation de centre $\Omega$ et d'angle $90°$).

Quelles sont les coordonnées de $A'$ ?

- a) $(2\,;\,-1)$
- b) $(-3\,;\,4)$
- c) $(0\,;\,5)$
- d) $(-1\,;\,3)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Une rotation se fait autour de son centre : on décrit le déplacement qui mène du centre au point, on fait tourner ce déplacement d'un quart de tour, puis on repart du centre. Sur un quadrillage, un déplacement « $a$ vers la droite, $b$ vers le haut » devient, après un quart de tour dans le sens contraire des aiguilles d'une montre, « $b$ vers la gauche, $a$ vers le haut ».

### Corrigé

Pour aller de $\Omega(1;2)$ à $A(4;3)$, on se déplace de $3$ vers la droite et de $1$ vers le haut.

Après le quart de tour dans le sens contraire des aiguilles d'une montre, ce déplacement devient : $1$ vers la gauche et $3$ vers le haut. En partant de $\Omega$ :
$$A'(1-1\,;\,2+3)=A'(0\,;\,5).$$

Contrôle : $\Omega A^2=3^2+1^2=10$, $\Omega A'^2=1^2+3^2=10$ et $AA'^2=4^2+2^2=20=\Omega A^2+\Omega A'^2$ ; d'après la réciproque du théorème de Pythagore, le triangle $A\Omega A'$ est rectangle et isocèle en $\Omega$.

### Pourquoi les autres réponses sont fausses

- **a)** c'est l'image par le quart de tour dans le sens des aiguilles d'une montre.
- **b)** on a fait tourner $A$ autour de l'origine du repère au lieu de $\Omega$.
- **d)** c'est le déplacement après rotation ; on a oublié de repartir du centre $\Omega$.

</details>

Avis : 

---

## 25. `cqc-similitude-directe-elevee-0` (séries BAC:C BAC:D BAC:E PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** Nombres complexes et similitudes : programme de Terminale, hors Probatoire C/E listé.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan complexe est muni d'un repère orthonormé direct $(O;\vec u,\vec v)$. On note $I$ le point d'affixe $1$, $A'$ le point d'affixe $3i$ et $B'$ le point d'affixe $1+4i$. La similitude directe $s$ transforme $O$ en $A'$ et $I$ en $B'$.

Quels sont le rapport, une mesure de l'angle et le centre $\Omega$ de $s$ ?

- a) rapport $\sqrt2$, angle $\dfrac\pi4$, $\Omega(0\,;\,3)$
- b) rapport $\sqrt2$, angle $\dfrac\pi4$, $\Omega(-3\,;\,0)$
- c) rapport $2$, angle $\dfrac\pi4$, $\Omega(-3\,;\,0)$
- d) rapport $\sqrt2$, angle $\dfrac\pi4$, $\Omega(3\,;\,0)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Une similitude directe s'écrit $z'=az+b$ avec $a\neq0$. Son rapport est $|a|$, son angle a pour mesure $\arg a$ et, si $a\neq1$, son centre est l'unique point invariant, d'affixe $\omega=\dfrac{b}{1-a}$. Les images de deux points distincts donnent $a$ puis $b$.

### Corrigé

$s(O)=A'$ donne $a\times0+b=3i$, donc $b=3i$.

$s(I)=B'$ donne $a+3i=1+4i$, donc $a=1+i$.

Rapport : $|1+i|=\sqrt{1^2+1^2}=\sqrt2$. Angle : $1+i=\sqrt2\left(\cos\dfrac\pi4+i\sin\dfrac\pi4\right)$, donc $\arg a=\dfrac\pi4$.

Centre : $\omega=\dfrac{3i}{1-(1+i)}=\dfrac{3i}{-i}=-3$, donc $\Omega(-3\,;\,0)$.

Contrôle : $(1+i)(-3)+3i=-3$, le point $\Omega$ est bien invariant.

### Pourquoi les autres réponses sont fausses

- **a)** $(0\,;\,3)$ est le point $A'$, image de $O$ ; ce n'est pas le point invariant : $s(A')=(1+i)\times3i+3i=-3+6i\neq3i$.
- **c)** on a calculé le module de $1+i$ comme $1+1=2$ au lieu de $\sqrt{1^2+1^2}$.
- **d)** erreur de signe : $1-(1+i)=-i$ et non $i$, d'où $\omega=-3$ et pas $3$.

</details>

Avis : 

---

## 26. `cqc-theoreme-de-la-mediane-prob-d-elevee-5` (séries PROBATOIRE:D)

**Remarque du relecteur :** VOCABULAIRE : écrire MA^2+MB^2=40 cm^2 pour l'homogénéité des unités.

**Énoncé :**

Soit $A$ et $B$ deux points du plan tels que $AB=4$ cm, et $I$ le milieu de $[AB]$.

Quel est l'ensemble des points $M$ du plan tels que $MA^2+MB^2=40$ ?

- a) le cercle de centre $I$ et de rayon $2\sqrt5$ cm
- b) le cercle de centre $I$ et de rayon $4\sqrt2$ cm
- c) le cercle de centre $I$ et de rayon $4$ cm
- d) le cercle de centre $I$ et de rayon $2\sqrt3$ cm

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Théorème de la médiane : si $I$ est le milieu de $[AB]$, alors pour tout point $M$, $MA^2+MB^2=2MI^2+\dfrac{AB^2}{2}$. On ramène ainsi la condition à une condition sur la seule distance $MI$.

### Corrigé

$$MA^2+MB^2=2MI^2+\frac{AB^2}{2}=2MI^2+\frac{16}{2}=2MI^2+8.$$

$$2MI^2+8=40 \iff MI^2=16 \iff MI=4.$$

L'ensemble cherché est le cercle de centre $I$ et de rayon $4$ cm.

### Pourquoi les autres réponses sont fausses

- **a)** on a oublié le terme $\dfrac{AB^2}{2}$ : $2MI^2=40$ donne $MI^2=20$.
- **b)** on a oublié le facteur $2$ devant $MI^2$ : $MI^2=40-8=32$.
- **d)** on a utilisé $AB^2$ au lieu de $\dfrac{AB^2}{2}$ : $2MI^2=40-16$ donne $MI^2=12$.

</details>

Avis : 

---

## 27. `cqc-tirage-successif-sans-remise-moyenne-2` (séries BAC:A BAC:C BAC:E PROBATOIRE:A)

**Remarque du relecteur :** LIMITE : tirages successifs sans remise (probabilités conditionnelles) pour le Probatoire A.

**Énoncé :**

Un panier contient $8$ mangues, dont $3$ sont abîmées. On prend au hasard une mangue, on ne la remet pas, puis on en prend une seconde.

Quelle est la probabilité qu'au moins une des deux mangues prises soit abîmée ?

- a) $\dfrac{39}{64}$
- b) $\dfrac9{14}$
- c) $\dfrac{15}{28}$
- d) $\dfrac3{28}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un tirage successif sans remise, la composition du panier change après le premier tirage : la seconde probabilité se calcule sur ce qui reste. Pour « au moins une », on passe par l'événement contraire « aucune ».

### Corrigé

Événement contraire : « les deux mangues sont saines ».

Première mangue saine : $\dfrac58$. Il reste alors $7$ mangues dont $4$ saines : seconde mangue saine avec la probabilité $\dfrac47$.

$$P(\text{deux saines})=\frac58\times\frac47=\frac{20}{56}=\frac5{14}.$$

$$P(\text{au moins une abîmée})=1-\frac5{14}=\frac9{14}.$$

### Pourquoi les autres réponses sont fausses

- **a)** $1-\left(\dfrac58\right)^2$ correspond à un tirage avec remise : on a oublié que le panier ne contient plus que $7$ mangues.
- **c)** $\dfrac{15}{28}$ est la probabilité d'avoir exactement une mangue abîmée ; « au moins une » inclut aussi le cas de deux mangues abîmées.
- **d)** $\dfrac38\times\dfrac27$ est la probabilité que les deux mangues soient abîmées.

</details>

Avis : 

---

## 28. `cqc-ajustement-affine-moyenne-1` (séries BAC:A BAC:C BAC:D BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** LIMITE : méthode de Mayer (séries doubles) au Probatoire C/E, à vérifier au programme de 1re.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une entreprise relève, sur six mois, ses dépenses de publicité $x$ (en centaines de milliers de francs CFA) et le nombre $y$ de produits vendus (en centaines) :

| $x$ | 2 | 4 | 6 | 8 | 10 | 12 |
|---|---|---|---|---|---|---|
| $y$ | 6 | 9 | 12 | 17 | 20 | 26 |

On ajuste ce nuage par la méthode de Mayer, en formant deux groupes de trois points pris dans l'ordre des abscisses croissantes. Quelle estimation de $y$ cette droite donne-t-elle pour $x=15$ ?

- a) $31$
- b) $14{,}5$
- c) $47$
- d) $30$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Méthode de Mayer : on partage la série, rangée par abscisses croissantes, en deux groupes de même effectif, on calcule le point moyen $G_1$ puis $G_2$ de chaque groupe, et la droite d'ajustement est $(G_1G_2)$. Son coefficient directeur est $a=\dfrac{y_{G_2}-y_{G_1}}{x_{G_2}-x_{G_1}}$ ; l'ordonnée à l'origine s'obtient en écrivant que $G_1$ est sur la droite.

### Corrigé

Groupe 1 : $x$ moyen $=\dfrac{2+4+6}{3}=4$ et $y$ moyen $=\dfrac{6+9+12}{3}=9$, donc $G_1(4\,;9)$.

Groupe 2 : $x$ moyen $=\dfrac{8+10+12}{3}=10$ et $y$ moyen $=\dfrac{17+20+26}{3}=21$, donc $G_2(10\,;21)$.

$a=\dfrac{21-9}{10-4}=\dfrac{12}{6}=2$ ; $9=2\times4+b$ donne $b=1$. La droite de Mayer est $y=2x+1$ (contrôle avec $G_2$ : $2\times10+1=21$).

Pour $x=15$ : $y=2\times15+1=31$, soit environ $3\,100$ produits vendus (extrapolation, à interpréter avec prudence).

### Pourquoi les autres réponses sont fausses

- **b)** le coefficient directeur a été calculé à l'envers, $\dfrac{\Delta x}{\Delta y}=0{,}5$, ce qui donne $y=0{,}5x+7$.
- **c)** erreur de signe sur l'ordonnée à l'origine : $b=9+8=17$ au lieu de $9-8=1$.
- **d)** l'ordonnée à l'origine a été oubliée : la droite $y=2x$ ne passe pas par $G_1$.

</details>

Avis : 

---

## 29. `cqc-derivee-d-un-quotient-tle-c-moyenne-3` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:A)

**Remarque du relecteur :** LIMITE : étude de la fonction rationnelle (x²+3)/(x-1) pour le Probatoire A, à vérifier.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}\setminus\{1\}$ par $f(x)=\dfrac{x^2+3}{x-1}$. Sur quel(s) intervalle(s) $f$ est-elle décroissante ?

- a) sur $[-1\,;3]$
- b) sur $]-\infty\,;-1]$ et sur $[3\,;+\infty[$
- c) sur aucun intervalle
- d) sur $[-1\,;1[$ et sur $]1\,;3]$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour $f=\dfrac uv$, $f'=\dfrac{u'v-uv'}{v^2}$. Le dénominateur $v^2$ étant positif, $f'$ a le signe de $u'v-uv'$. Une fonction n'est étudiée que sur son ensemble de définition : une valeur interdite coupe toujours un intervalle en deux.

### Corrigé

$u=x^2+3$, $u'=2x$, $v=x-1$, $v'=1$ :

$$f'(x)=\dfrac{2x(x-1)-(x^2+3)}{(x-1)^2}=\dfrac{x^2-2x-3}{(x-1)^2}=\dfrac{(x+1)(x-3)}{(x-1)^2}.$$

Le trinôme $(x+1)(x-3)$ est négatif entre ses racines $-1$ et $3$. Comme $1$ est une valeur interdite, $f'(x)\leqslant0$ sur $[-1\,;1[$ et sur $]1\,;3]$.

$f$ est décroissante sur $[-1\,;1[$ et sur $]1\,;3]$.

### Pourquoi les autres réponses sont fausses

- **a)** la valeur interdite $1$ a été oubliée : $f$ n'est pas définie en $1$, l'intervalle $[-1\,;3]$ ne convient pas.
- **b)** ce sont les intervalles où $f'(x)\geqslant0$, donc où $f$ est croissante.
- **c)** la formule a été écrite avec un signe plus, $u'v+uv'$, ce qui donne le numérateur $3x^2-2x+3$, toujours positif.

</details>

Avis : 

---

## 30. `cqc-excentricite-faible-1` (séries BAC:C BAC:D BAC:E)

**Séries modifiées :** retirées BAC:D.

**Remarque du relecteur :** LIMITE : les coniques (excentricité) relèvent surtout des séries C et E ; vérifier leur présence au programme de la série D.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, on considère la courbe $(\mathcal E)$ d'équation $25x^2+16y^2=400$. Quelle est l'excentricité de cette ellipse ?

- a) $\dfrac45$
- b) $\dfrac53$
- c) $\dfrac35$
- d) $\dfrac34$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On met d'abord l'équation sous forme réduite $\dfrac{x^2}{\alpha^2}+\dfrac{y^2}{\beta^2}=1$. Le demi-grand axe $a$ est le PLUS GRAND des deux nombres $\alpha$ et $\beta$ (il peut se trouver sous $y^2$), $b$ est le plus petit, $c=\sqrt{a^2-b^2}$ et l'excentricité est $e=\dfrac ca$, toujours comprise entre $0$ et $1$.

### Corrigé

En divisant par $400$ : $\dfrac{x^2}{16}+\dfrac{y^2}{25}=1$. Le grand axe est porté par l'axe des ordonnées : $a=5$ et $b=4$.

$c=\sqrt{25-16}=3$, d'où $e=\dfrac ca=\dfrac35$.

### Pourquoi les autres réponses sont fausses

- **a)** c'est le rapport $\dfrac ba$, et non $\dfrac ca$.
- **b)** le rapport a été inversé ($\dfrac ac$) ; une excentricité d'ellipse est inférieure à $1$.
- **d)** on a pris $a=4$ parce que $16$ est sous $x^2$ ; or le demi-grand axe est ici $5$, sur l'axe des ordonnées.

</details>

Avis : 

---

## 31. `cqc-loi-de-probabilite-moyenne-2` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D)

**Séries modifiées :** retirées PROBATOIRE:A, PROBATOIRE:C, PROBATOIRE:D.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans un jeu, le nombre $X$ de points obtenus par un joueur prend les valeurs $1$, $2$, $3$ ou $4$, et la probabilité d'obtenir $k$ points est proportionnelle à $k$ : $P(X=k)=k\,a$, où $a$ est un réel. Quelle est la probabilité $P(X\geqslant3)$ ?

- a) $\dfrac7{10}$
- b) $\dfrac12$
- c) $\dfrac3{10}$
- d) $\dfrac9{10}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On détermine d'abord la constante inconnue en écrivant que la somme des probabilités de toutes les valeurs vaut $1$. On additionne ensuite les probabilités des valeurs qui réalisent l'événement demandé (« au moins $3$ » contient $3$ ET $4$).

### Corrigé

$a+2a+3a+4a=1$, donc $10a=1$ et $a=\dfrac1{10}$.

$$P(X\geqslant3)=P(X=3)+P(X=4)=\dfrac3{10}+\dfrac4{10}=\dfrac7{10}.$$

### Pourquoi les autres réponses sont fausses

- **b)** les quatre valeurs ont été supposées équiprobables, ce que l'énoncé contredit.
- **c)** seule la valeur $3$ a été comptée, alors que « au moins $3$ » comprend aussi $4$.
- **d)** c'est $1-P(X=1)=P(X\geqslant2)$ : confusion entre « au moins $3$ » et « plus de $1$ ».

</details>

Avis : 

---

## 32. `cqc-matrice-inverse-prob-c-moyenne-2` (séries PROBATOIRE:C)

**Séries modifiées :** retirées PROBATOIRE:C ; ajoutées PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On considère la matrice $A=\begin{pmatrix}3&-2\\4&-1\end{pmatrix}$. Quelle est sa matrice inverse $A^{-1}$ ?

- a) $\dfrac15\begin{pmatrix}-1&-2\\4&3\end{pmatrix}$
- b) $\dfrac15\begin{pmatrix}-1&2\\-4&3\end{pmatrix}$
- c) $-\dfrac1{11}\begin{pmatrix}-1&2\\-4&3\end{pmatrix}$
- d) $\dfrac15\begin{pmatrix}-1&-4\\2&3\end{pmatrix}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

$A=\begin{pmatrix}a&b\\c&d\end{pmatrix}$ est inversible si $\det A=ad-bc\neq0$, et alors $A^{-1}=\dfrac1{ad-bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}$ : on échange les coefficients diagonaux et on change le signe des deux autres. On contrôle en calculant $AA^{-1}$.

### Corrigé

$\det A=3\times(-1)-(-2)\times4=-3+8=5\neq0$ : $A$ est inversible et
$$A^{-1}=\dfrac15\begin{pmatrix}-1&2\\-4&3\end{pmatrix}.$$
Contrôle : $A\begin{pmatrix}-1&2\\-4&3\end{pmatrix}=\begin{pmatrix}-3+8&6-6\\-4+4&8-3\end{pmatrix}=\begin{pmatrix}5&0\\0&5\end{pmatrix}$, puis on divise par $5$ : on obtient bien la matrice unité.

### Pourquoi les autres réponses sont fausses

- **a)** le signe des coefficients $b$ et $c$ n'a pas été changé.
- **c)** erreur de signe dans le déterminant : $-3-8=-11$ au lieu de $-3+8=5$.
- **d)** on a transposé la bonne réponse ($b$ et $c$ échangés de place) : le produit par $A$ ne donne pas la matrice unité.

</details>

Avis : 

---

## 33. `cqc-point-moyen-faible-0` (séries BAC:A BAC:D BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Un vendeur de jus relève, pour cinq prix de vente $x_i$ (en centaines de francs CFA), le nombre $y_i$ de bouteilles vendues dans la journée :

| $x_i$ | 1 | 2 | 4 | 7 | 11 |
|---|---|---|---|---|---|
| $y_i$ | 50 | 44 | 35 | 26 | 15 |

Quelles sont les coordonnées du point moyen $G$ de cette série statistique double ?

- a) $G(34\,;5)$
- b) $G(4\,;35)$
- c) $G(5\,;34)$
- d) $G(6{,}25\,;42{,}5)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Le point moyen d'une série double $(x_i\,;y_i)$ d'effectif $n$ est $G(\bar x\,;\bar y)$, avec $\bar x=\dfrac1n\sum x_i$ (abscisse) et $\bar y=\dfrac1n\sum y_i$ (ordonnée). Ce sont des MOYENNES, et non des médianes.

### Corrigé

Ici $n=5$.

$\bar x=\dfrac{1+2+4+7+11}{5}=\dfrac{25}{5}=5$ et $\bar y=\dfrac{50+44+35+26+15}{5}=\dfrac{170}{5}=34$.

Le point moyen est $G(5\,;34)$.

### Pourquoi les autres réponses sont fausses

- **a)** l'abscisse et l'ordonnée ont été inversées.
- **b)** ce sont les médianes des $x_i$ et des $y_i$, pas leurs moyennes.
- **d)** les sommes ont été divisées par $4$ au lieu de l'effectif $5$.

</details>

Avis : 

---

## 34. `cqc-produit-vectoriel-faible-0` (séries BAC:C BAC:E PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** Doublon de la n=26 (même énoncé, choix permutés) : en garder une.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans l'espace muni d'un repère orthonormé, on donne les points $A(1\,;0\,;2)$, $B(3\,;1\,;2)$ et $C(1\,;2\,;4)$. Quelle est l'aire du triangle $ABC$, en unités d'aire ?

- a) $3$
- b) $6$
- c) $1$
- d) $18$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

L'aire d'un triangle $ABC$ de l'espace est $\dfrac12\big\|\overrightarrow{AB}\wedge\overrightarrow{AC}\big\|$ : la norme du produit vectoriel est l'aire du parallélogramme construit sur les deux vecteurs, et le triangle en est la moitié.

### Corrigé

$\overrightarrow{AB}(2\,;1\,;0)$ et $\overrightarrow{AC}(0\,;2\,;2)$.

$$\overrightarrow{AB}\wedge\overrightarrow{AC}=\big(1\times2-0\times2\,;\,0\times0-2\times2\,;\,2\times2-1\times0\big)=(2\,;-4\,;4).$$

$\big\|\overrightarrow{AB}\wedge\overrightarrow{AC}\big\|=\sqrt{4+16+16}=\sqrt{36}=6$, donc l'aire du triangle est $\dfrac62=3$ unités d'aire.

### Pourquoi les autres réponses sont fausses

- **b)** c'est l'aire du parallélogramme : la division par $2$ a été oubliée.
- **c)** on a utilisé le produit scalaire $\overrightarrow{AB}\cdot\overrightarrow{AC}=2$ au lieu du produit vectoriel.
- **d)** on a pris le carré de la norme ($36$) au lieu de la norme ($6$).

</details>

Avis : 

---

## 35. `cqc-racine-evidente-moyenne-2` (séries BAC:A BAC:C PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées BAC:A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Quel est l'ensemble des solutions dans $\mathbb{R}$ de l'équation $2x^3-3x^2-11x+6=0$ ?

- a) $\{3\}$
- b) $\left\{-2\,;\,\dfrac12\,;\,3\right\}$
- c) $\left\{-\dfrac12\,;\,2\,;\,3\right\}$
- d) $\left\{\dfrac{-3-\sqrt{17}}{2}\,;\,\dfrac{-3+\sqrt{17}}{2}\,;\,3\right\}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On cherche une racine évidente parmi les petits entiers (diviseurs du terme constant), on factorise par $(x-\text{racine})$ en identifiant les coefficients du quotient (sans oublier le coefficient dominant), puis on résout le facteur du second degré.

### Corrigé

Pour $x=3$ : $2\times27-3\times9-33+6=54-27-33+6=0$, donc $3$ est racine.

On pose $2x^3-3x^2-11x+6=(x-3)(2x^2+bx+c)$. Par identification : $b-6=-3$ donc $b=3$, et $-3c=6$ donc $c=-2$ (contrôle du coefficient de $x$ : $c-3b=-2-9=-11$).

$2x^2+3x-2$ : $\Delta=9+16=25$, racines $\dfrac{-3-5}{4}=-2$ et $\dfrac{-3+5}{4}=\dfrac12$.

$$\mathcal S=\left\{-2\,;\,\dfrac12\,;\,3\right\}.$$

### Pourquoi les autres réponses sont fausses

- **a)** la résolution s'est arrêtée à la racine évidente ; le facteur du second degré a aussi deux racines.
- **c)** erreur de signe dans l'identification : le quotient a été pris égal à $2x^2-3x-2$.
- **d)** le coefficient dominant $2$ a été oublié dans le quotient, écrit $x^2+3x-2$.

</details>

Avis : 

---

## 36. `cqc-relations-coefficients-racines-elevee-0` (séries BAC:C BAC:D PROBATOIRE:A PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

L'équation $x^2-5x+3=0$ admet deux solutions réelles $x_1$ et $x_2$. Sans calculer ces solutions, déterminer la valeur de $x_1^3+x_2^3$.

- a) $125$
- b) $170$
- c) $80$
- d) $-80$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour $ax^2+bx+c=0$ de discriminant positif, la somme des solutions est $S=x_1+x_2=-\dfrac ba$ et leur produit $P=x_1x_2=\dfrac ca$. On exprime ensuite la quantité demandée en fonction de $S$ et $P$ : ici $x_1^3+x_2^3=(x_1+x_2)^3-3x_1x_2(x_1+x_2)=S^3-3PS$.

### Corrigé

$\Delta=25-12=13>0$ : les deux solutions existent.

$S=5$ et $P=3$. Comme $(x_1+x_2)^3=x_1^3+x_2^3+3x_1x_2(x_1+x_2)$ :

$$x_1^3+x_2^3=S^3-3PS=125-45=80.$$

### Pourquoi les autres réponses sont fausses

- **a)** on a écrit $x_1^3+x_2^3=(x_1+x_2)^3$, en oubliant les termes croisés.
- **b)** erreur de signe : $S^3+3PS$ au lieu de $S^3-3PS$.
- **d)** erreur de signe sur la somme, prise égale à $-5$ au lieu de $5$.

</details>

Avis : 

---

## 37. `cqc-rotation-moyenne-2` (séries BAC:C BAC:D BAC:E BAC:TI BEPC: PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : la rotation au BEPC est à vérifier selon le programme de 3e en vigueur.

**Énoncé :**

$ABCDEF$ est un hexagone régulier de centre $O$, dont les sommets sont nommés dans le sens inverse des aiguilles d'une montre. La rotation $r$ de centre $O$ transforme $A$ en $C$. Quelle est l'image du point $B$ par $r$ ?

- a) $C$
- b) $E$
- c) $F$
- d) $D$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un hexagone régulier de centre $O$, deux sommets consécutifs sont vus du centre sous un angle de $\dfrac{360°}{6}=60°$. Une rotation de centre $O$ fait tourner TOUS les points du même angle et dans le même sens.

### Corrigé

Pour passer de $A$ à $C$, on avance de deux sommets dans le sens inverse des aiguilles d'une montre : $r$ est la rotation de centre $O$ et d'angle $120°$ dans ce sens.

En appliquant la même rotation à $B$, on avance aussi de deux sommets : $r(B)=D$.

### Pourquoi les autres réponses sont fausses

- **a)** on n'a avancé que d'un sommet, comme si l'angle de la rotation était $60°$.
- **b)** on a avancé de trois sommets : c'est l'image par la symétrie centrale de centre $O$ (angle $180°$).
- **c)** on a tourné dans le mauvais sens (deux sommets dans le sens des aiguilles d'une montre).

</details>

Avis : 

---

## 38. `cqc-similitude-directe-faible-0` (séries BAC:C BAC:D BAC:E BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** Nombres complexes et similitudes : programme de Terminale, hors Probatoire C/E listé.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan complexe est muni d'un repère orthonormé direct. La similitude directe $s$ a pour écriture complexe $z'=(1-i\sqrt3)\,z+3$. Quels sont le rapport et une mesure de l'angle de $s$ ?

- a) rapport $2$, angle $-\dfrac\pi3$
- b) rapport $2$, angle $\dfrac\pi3$
- c) rapport $4$, angle $-\dfrac\pi3$
- d) rapport $2$, angle $-\dfrac\pi6$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Une similitude directe d'écriture $z'=az+b$ ($a\neq0$) a pour rapport $|a|$ et pour angle $\arg(a)$. On écrit $a=|a|(\cos\theta+i\sin\theta)$ et on identifie $\cos\theta$ et $\sin\theta$, en tenant compte du signe de la partie imaginaire.

### Corrigé

$a=1-i\sqrt3$ : $|a|=\sqrt{1+3}=2$.

$a=2\left(\dfrac12-i\dfrac{\sqrt3}{2}\right)$, donc $\cos\theta=\dfrac12$ et $\sin\theta=-\dfrac{\sqrt3}{2}$, d'où $\theta=-\dfrac\pi3$.

$s$ a pour rapport $2$ et pour angle $-\dfrac\pi3$.

### Pourquoi les autres réponses sont fausses

- **b)** le signe de la partie imaginaire $-\sqrt3$ a été ignoré.
- **c)** c'est $|a|^2=4$, la racine carrée a été oubliée.
- **d)** cosinus et sinus ont été confondus : $\cos\left(-\dfrac\pi6\right)=\dfrac{\sqrt3}{2}\neq\dfrac12$.

</details>

Avis : 

---

## 39. `cqc-theoreme-de-la-mediane-prob-d-faible-0` (séries PROBATOIRE:D)

**Énoncé :**

Le segment $[AB]$ mesure $6$ cm et $I$ est son milieu. Un point $M$ du plan est tel que $MI=4$ cm. Quelle est la valeur de $MA^2+MB^2$ ?

- a) $50$
- b) $68$
- c) $34$
- d) $26$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Théorème de la médiane : si $I$ est le milieu de $[AB]$, alors pour tout point $M$, $MA^2+MB^2=2MI^2+\dfrac{AB^2}{2}$. Il s'applique sans connaître la position exacte de $M$.

### Corrigé

$$MA^2+MB^2=2\times4^2+\dfrac{6^2}{2}=32+18=50.$$

$MA^2+MB^2=50$ cm². Contrôle sur un cas particulier : avec $A(-3\,;0)$, $B(3\,;0)$ et $M(0\,;4)$, on a $MI=4$ et $MA^2+MB^2=25+25=50$.

### Pourquoi les autres réponses sont fausses

- **b)** la division par $2$ de $AB^2$ a été oubliée : $32+36=68$.
- **c)** le coefficient $2$ devant $MI^2$ a été oublié : $16+18=34$.
- **d)** $MI$ n'a pas été élevé au carré : $2\times4+18=26$.

</details>

Avis : 

---

## 40. `cqc-excentricite-moyenne-0` (séries BAC:C BAC:D BAC:E)

**Séries modifiées :** retirées BAC:D.

**Remarque du relecteur :** LIMITE : coniques en série D, à vérifier au programme.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, la courbe $(\mathcal E)$ a pour équation $9x^{2}+25y^{2}=225$.

Quelle est l'excentricité de $(\mathcal E)$ ?

- a) $\dfrac35$
- b) $\dfrac45$
- c) $\dfrac{\sqrt{34}}{5}$
- d) $\dfrac54$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On écrit d'abord l'équation sous forme réduite $\dfrac{x^{2}}{a^{2}}+\dfrac{y^{2}}{b^{2}}=1$. Pour une ellipse avec $a>b>0$, la distance du centre à un foyer est $c=\sqrt{a^{2}-b^{2}}$ et l'excentricité vaut $e=\dfrac ca$, qui est strictement comprise entre $0$ et $1$.

### Corrigé

En divisant par $225$ :
$$\frac{x^{2}}{25}+\frac{y^{2}}{9}=1,\qquad a=5,\ b=3.$$
$(\mathcal E)$ est une ellipse de grand axe porté par $(Ox)$, et
$$c=\sqrt{a^{2}-b^{2}}=\sqrt{25-9}=4,\qquad e=\frac ca=\frac45.$$
On vérifie que $0<e<1$.

### Pourquoi les autres réponses sont fausses

- **a)** $\dfrac ba$ : on a divisé le demi-petit axe par le demi-grand axe au lieu de $c$ par $a$.
- **c)** On a pris $c^{2}=a^{2}+b^{2}$, relation de l'hyperbole ; une excentricité supérieure à $1$ ne peut pas être celle d'une ellipse.
- **d)** $\dfrac ac$ : rapport inversé ; une valeur supérieure à $1$ aurait dû alerter.

</details>

Avis : 

---

## 41. `cqc-fonction-homographique-prob-de-faible-0` (séries BAC:A PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Énoncé :**

Soit $f$ la fonction définie pour $x\neq3$ par $f(x)=\dfrac{2x+1}{x-3}$.

Pour quelle valeur de $x$ a-t-on $f(x)=3$ ?

- a) $x=4$
- b) $x=1$
- c) $x=10$
- d) $x=-10$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour résoudre $\dfrac{A(x)}{B(x)}=k$, on écarte la valeur interdite ($B(x)=0$), puis on multiplie les deux membres par $B(x)$ : $A(x)=k\,B(x)$. Le facteur $k$ multiplie **tout** le dénominateur. On vérifie enfin que la solution trouvée n'est pas la valeur interdite.

### Corrigé

Pour $x\neq3$ :
$$\frac{2x+1}{x-3}=3\iff 2x+1=3(x-3)\iff 2x+1=3x-9\iff x=10.$$
$10\neq3$, et $f(10)=\dfrac{21}{7}=3$ : la solution est $x=10$.

### Pourquoi les autres réponses sont fausses

- **a)** On a écrit $3(x-3)=3x-3$ : la distributivité n'a pas été appliquée au second terme.
- **b)** On a ignoré le dénominateur et résolu $2x+1=3$.
- **d)** Erreur de signe en isolant $x$ : $-x=-10$ donne $x=10$, pas $-10$.

</details>

Avis : 

---

## 42. `cqc-loi-de-probabilite-moyenne-3` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D)

**Séries modifiées :** retirées PROBATOIRE:A, PROBATOIRE:C, PROBATOIRE:D.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

À un jeu, le gain algébrique $X$ d'un joueur, en francs CFA, prend les valeurs $-100$, $0$ et $300$, avec la loi suivante, où $p$ est un réel :

| $x_i$ | $-100$ | $0$ | $300$ |
|---|---|---|---|
| $P(X=x_i)$ | $2p$ | $0{,}4$ | $p$ |

Quelle est l'espérance mathématique de $X$ ?

- a) $100$
- b) $60$
- c) $20$
- d) $\dfrac{200}{3}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Une loi dépendant d'un paramètre se détermine d'abord par la condition « la somme des probabilités vaut $1$ » (en vérifiant ensuite que chaque probabilité est dans $[0\,;1]$). L'espérance est la somme des valeurs pondérées par leurs probabilités : $E(X)=\sum x_i\,P(X=x_i)$.

### Corrigé

**Paramètre.** $2p+0{,}4+p=1$, donc $3p=0{,}6$ et $p=0{,}2$. Les probabilités sont $0{,}4$ ; $0{,}4$ ; $0{,}2$, toutes dans $[0\,;1]$.

**Espérance.**
$$E(X)=-100\times0{,}4+0\times0{,}4+300\times0{,}2=-40+0+60=20.$$
En moyenne, sur un grand nombre de parties, le joueur gagne $20$ F CFA par partie.

### Pourquoi les autres réponses sont fausses

- **a)** On a échangé les probabilités de $-100$ et de $300$ : $-100\times0{,}2+300\times0{,}4=100$.
- **b)** On a pris $p=0{,}6$ (oubli de diviser par $3$) : $-100\times1{,}2+300\times0{,}6=60$, avec en plus une « probabilité » $1{,}2$ impossible.
- **d)** Moyenne simple des trois valeurs : les valeurs n'ont pas été pondérées par leurs probabilités.

</details>

Avis : 

---

## 43. `cqc-matrice-inverse-prob-c-moyenne-3` (séries PROBATOIRE:C)

**Séries modifiées :** retirées PROBATOIRE:C ; ajoutées PROBATOIRE:E.

**Remarque du relecteur :** LIMITE : l'inverse d'une matrice 2x2 au Probatoire C est à confirmer selon le programme en vigueur.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On considère la matrice $A=\begin{pmatrix}4&3\\3&2\end{pmatrix}$.

Quelle est la matrice inverse de $A$ ?

- a) $\begin{pmatrix}2&-3\\-3&4\end{pmatrix}$
- b) $\begin{pmatrix}-2&-3\\-3&-4\end{pmatrix}$
- c) $\begin{pmatrix}\frac14&\frac13\\[2pt]\frac13&\frac12\end{pmatrix}$
- d) $\begin{pmatrix}-2&3\\3&-4\end{pmatrix}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour $A=\begin{pmatrix}a&b\\c&d\end{pmatrix}$ de déterminant $\det A=ad-bc\neq0$ :
$$A^{-1}=\frac{1}{\det A}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}.$$
On échange les coefficients diagonaux, on change le signe des deux autres, puis on divise par le déterminant (avec son signe). On contrôle par le produit $A\,A^{-1}=I$.

### Corrigé

$\det A=4\times2-3\times3=8-9=-1\neq0$, donc $A$ est inversible et
$$A^{-1}=\frac{1}{-1}\begin{pmatrix}2&-3\\-3&4\end{pmatrix}=\begin{pmatrix}-2&3\\3&-4\end{pmatrix}.$$
Contrôle : $\begin{pmatrix}4&3\\3&2\end{pmatrix}\begin{pmatrix}-2&3\\3&-4\end{pmatrix}=\begin{pmatrix}-8+9&12-12\\-6+6&9-8\end{pmatrix}=\begin{pmatrix}1&0\\0&1\end{pmatrix}$.

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié de diviser par le déterminant, qui vaut $-1$ : le produit avec $A$ donne $-I$.
- **b)** On a divisé par $-1$ sans avoir changé au préalable le signe de $b$ et de $c$.
- **c)** On a inversé chaque coefficient séparément : l'inverse d'une matrice ne se calcule pas terme à terme.

</details>

Avis : 

---

## 44. `cqc-nuage-de-points-moyenne-2` (séries BAC:A BAC:D BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Un commerçant relève, pendant six semaines, la température moyenne $x$ (en °C) et le nombre $y$ de bouteilles d'eau vendues :

| $x$ (°C) | 22 | 25 | 27 | 30 | 32 | 34 |
|---|---|---|---|---|---|---|
| $y$ (bouteilles) | 120 | 170 | 210 | 250 | 290 | 320 |

Il veut représenter le nuage de points dans un repère d'origine $(0\,;0)$, et il dispose de 15 cm au plus pour l'axe des ordonnées. Parmi les échelles suivantes, laquelle permet de placer tous les points avec la plus grande précision possible sur l'axe des ordonnées ?

- a) 1 cm pour 10 bouteilles
- b) 1 cm pour 20 bouteilles
- c) 1 cm pour 25 bouteilles
- d) 1 cm pour 50 bouteilles

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

L'axe partant de l'origine, la longueur nécessaire est $\dfrac{\text{valeur maximale}}{\text{nombre d'unités par cm}}$. Une échelle convient si cette longueur ne dépasse pas la place disponible ; parmi les échelles qui conviennent, la plus précise est celle qui représente le moins d'unités par centimètre.

### Corrigé

La plus grande valeur de $y$ est $320$.

- 1 cm pour 10 : $\dfrac{320}{10}=32$ cm, trop long.
- 1 cm pour 20 : $\dfrac{320}{20}=16$ cm, trop long (16 cm > 15 cm).
- 1 cm pour 25 : $\dfrac{320}{25}=12{,}8$ cm, cela tient.
- 1 cm pour 50 : $\dfrac{320}{50}=6{,}4$ cm, cela tient aussi, mais avec moins de précision.

L'échelle qui convient avec la plus grande précision est **1 cm pour 25 bouteilles**.

### Pourquoi les autres réponses sont fausses

- **a)** Il faudrait 32 cm : on a choisi l'échelle la plus fine sans vérifier la place disponible.
- **b)** Il faudrait 16 cm, soit 1 cm de trop : on a raisonné sur l'étendue $320-120=200$ (10 cm) alors que l'axe part de l'origine.
- **d)** Tous les points tiennent, mais le nuage n'occupe que 6,4 cm : ce n'est pas l'échelle la plus précise possible.

</details>

Avis : 

---

## 45. `cqc-point-moyen-faible-1` (séries BAC:A BAC:D BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une série statistique double comporte quatre points :

| $x_i$ | 2 | 4 | 7 | $a$ |
|---|---|---|---|---|
| $y_i$ | 9 | 11 | 14 | 14 |

Son point moyen est $G(5\,;\,12)$. Quelle est la valeur de $a$ ?

- a) $a=2$
- b) $a=7$
- c) $a=20$
- d) $a=33$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Le point moyen d'une série double de $n$ points est $G(\bar x\,;\,\bar y)$, où $\bar x=\dfrac{x_1+\dots+x_n}{n}$ et $\bar y=\dfrac{y_1+\dots+y_n}{n}$. Connaissant $\bar x$, on écrit l'équation correspondante en divisant bien par le nombre **total** de points, y compris celui dont une coordonnée est inconnue.

### Corrigé

Il y a $n=4$ points, donc :
$$\bar x=\frac{2+4+7+a}{4}=5\iff 13+a=20\iff a=7.$$
Contrôle sur les ordonnées : $\bar y=\dfrac{9+11+14+14}{4}=\dfrac{48}{4}=12$, ce qui est cohérent avec $G$.

### Pourquoi les autres réponses sont fausses

- **a)** On a divisé par $3$ (les trois valeurs connues) au lieu de $4$ : $\dfrac{13+a}{3}=5$ donne $a=2$.
- **c)** On a oublié de retrancher $13$ : $20$ est la somme des quatre abscisses, pas $a$.
- **d)** Erreur de signe : on a ajouté $13$ à $4\times5$ au lieu de le retrancher.

</details>

Avis : 

---

## 46. `cqc-produit-vectoriel-faible-1` (séries BAC:C BAC:E PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** Le produit vectoriel est une notion de Terminale C/E ; seule voie de réponse, hors programme pour le Probatoire C/E listé.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans l'espace muni d'un repère orthonormé direct $(O;\vec\imath,\vec\jmath,\vec k)$, on donne les vecteurs $\vec a\,(1\,;\,2\,;\,-1)$ et $\vec b\,(3\,;\,0\,;\,2)$.

Quelles sont les coordonnées de $\vec a\wedge\vec b$ ?

- a) $(-4\,;\,5\,;\,6)$
- b) $(4\,;\,5\,;\,-6)$
- c) $(4\,;\,-5\,;\,-6)$
- d) $(3\,;\,0\,;\,-2)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour $\vec a(x\,;y\,;z)$ et $\vec b(x'\,;y'\,;z')$ dans un repère orthonormé direct :
$$\vec a\wedge\vec b=(yz'-zy'\,;\,zx'-xz'\,;\,xy'-yx').$$
La deuxième coordonnée est la plus souvent fausse (ordre $zx'-xz'$). Contrôle : le résultat est orthogonal à $\vec a$ et à $\vec b$.

### Corrigé

Avec $(x\,;y\,;z)=(1\,;2\,;-1)$ et $(x'\,;y'\,;z')=(3\,;0\,;2)$ :
- première coordonnée : $2\times2-(-1)\times0=4$ ;
- deuxième coordonnée : $(-1)\times3-1\times2=-5$ ;
- troisième coordonnée : $1\times0-2\times3=-6$.

$$\vec a\wedge\vec b=(4\,;\,-5\,;\,-6).$$
Contrôle : $\vec a\cdot(\vec a\wedge\vec b)=4-10+6=0$ et $\vec b\cdot(\vec a\wedge\vec b)=12+0-12=0$.

### Pourquoi les autres réponses sont fausses

- **a)** C'est $\vec b\wedge\vec a$ : l'ordre des vecteurs a été inversé, ce qui change le signe de toutes les coordonnées.
- **b)** Deuxième coordonnée calculée par $xz'-zx'=5$ au lieu de $zx'-xz'=-5$ : le vecteur obtenu n'est pas orthogonal à $\vec a$.
- **d)** On a multiplié les coordonnées une à une : ce n'est pas le produit vectoriel.

</details>

Avis : 

---

## 47. `cqc-relations-coefficients-racines-faible-0` (séries BAC:C BAC:D PROBATOIRE:A PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

L'équation $2x^{2}-7x+3=0$ admet $3$ pour solution.

Quelle est son autre solution ?

- a) $1$
- b) $\dfrac12$
- c) $4$
- d) $-\dfrac12$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Si l'équation $ax^{2}+bx+c=0$ ($a\neq0$) a deux solutions $x_1$ et $x_2$, alors $x_1+x_2=-\dfrac ba$ et $x_1x_2=\dfrac ca$. Connaissant une solution, l'une de ces relations donne l'autre sans calculer le discriminant. Il ne faut pas oublier de diviser par $a$.

### Corrigé

Le produit des solutions vaut $\dfrac ca=\dfrac32$. Avec $x_1=3$ :
$$3\,x_2=\frac32\iff x_2=\frac12.$$
Vérification par la somme : $3+\dfrac12=\dfrac72=-\dfrac{-7}{2}$. Et $2\times\dfrac14-\dfrac72+3=0$.

### Pourquoi les autres réponses sont fausses

- **a)** On a pris le produit égal à $c=3$ sans diviser par $a=2$.
- **c)** On a pris la somme égale à $7$ sans diviser par $a=2$.
- **d)** Erreur de signe : on a utilisé $x_1x_2=-\dfrac ca$.

</details>

Avis : 

---

## 48. `cqc-similitude-directe-faible-1` (séries BAC:C BAC:D BAC:E BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** Les similitudes directes en écriture complexe relèvent de la Terminale (C, E) ; hors programme pour le Probatoire C/E listé.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan complexe est muni d'un repère orthonormé direct. La similitude directe $s$ a pour écriture complexe $z'=(1+i)\,z+2$.

Quelle est l'affixe du centre de $s$ ?

- a) $-2i$
- b) $1-i$
- c) $2$
- d) $2i$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Le centre d'une similitude directe $z'=az+b$ (avec $a\neq1$) est son unique point invariant : son affixe $\omega$ vérifie $\omega=a\,\omega+b$, donc $\omega=\dfrac{b}{1-a}$.

### Corrigé

$\omega=(1+i)\,\omega+2\iff \omega-(1+i)\,\omega=2\iff -i\,\omega=2\iff \omega=\dfrac{2}{-i}=2i$ (car $\dfrac1i=-i$).

Vérification : $(1+i)\times2i+2=2i-2+2=2i$.

### Pourquoi les autres réponses sont fausses

- **a)** On a écrit $\omega=\dfrac{b}{a-1}=\dfrac2i$ : erreur de signe en regroupant les termes en $\omega$.
- **b)** On a résolu $a\,\omega=b$, en oubliant le terme $\omega$ du premier membre.
- **c)** $2$ est la partie « translation » $b$ de l'écriture, pas le point invariant : $(1+i)\times2+2=4+2i\neq2$.

</details>

Avis : 

---

## 49. `cqc-theoreme-des-gendarmes-faible-1` (séries BAC:C BAC:D BAC:E BAC:TI)

**Énoncé :**

Soit $(u_n)$ la suite définie pour tout entier naturel $n$ par
$$u_n=\frac{3n+\cos n}{n+1}.$$

Quelle est la limite de $(u_n)$ ?

- a) $0$
- b) $+\infty$
- c) $3$
- d) La suite n'a pas de limite, car $\cos n$ n'en a pas

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'un terme comme $\cos n$ ou $(-1)^{n}$ n'a pas de limite mais est **borné**, on l'encadre, on en déduit un encadrement de $u_n$ par deux suites de même limite, et on conclut par le théorème des gendarmes.

### Corrigé

Pour tout $n$, $-1\leqslant\cos n\leqslant1$, et $n+1>0$, donc
$$\frac{3n-1}{n+1}\leqslant u_n\leqslant\frac{3n+1}{n+1}.$$
Or $\dfrac{3n-1}{n+1}=\dfrac{3-\frac1n}{1+\frac1n}$ et $\dfrac{3n+1}{n+1}=\dfrac{3+\frac1n}{1+\frac1n}$ (pour $n\geqslant1$) tendent toutes deux vers $3$. D'après le théorème des gendarmes,
$$\lim_{n\to+\infty}u_n=3.$$

### Pourquoi les autres réponses sont fausses

- **a)** On a appliqué « borné divisé par une suite qui tend vers $+\infty$ » à toute la fraction, en oubliant le terme $3n$ du numérateur.
- **b)** On n'a regardé que le numérateur, qui tend vers $+\infty$, sans tenir compte du dénominateur.
- **d)** Un terme sans limite mais borné n'empêche pas la convergence : l'encadrement suffit.

</details>

Avis : 

---

## 50. `cqc-isometrie-prob-c-faible-0` (séries PROBATOIRE:C PROBATOIRE:E)

**Remarque du relecteur :** Quasi-doublon de la question 1.

**Énoncé :**

Dans un repère orthonormé, $s$ est la symétrie orthogonale d'axe la droite $(\Delta)$ d'équation $y=x+1$. Quelles sont les coordonnées de l'image $A'$ du point $A(3\,;0)$ par $s$ ?

- a) $A'(-1\,;4)$
- b) $A'(0\,;3)$
- c) $A'(1\,;2)$
- d) $A'(4\,;-1)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

$A'$ est le symétrique de $A$ par rapport à $(\Delta)$ si et seulement si le milieu de $[AA']$ appartient à $(\Delta)$ et $\overrightarrow{AA'}$ est orthogonal à un vecteur directeur de $(\Delta)$. On traduit ces deux conditions en un système d'équations.

### Corrigé

Notons $A'(x'\,;y')$. Un vecteur directeur de $(\Delta)$ est $\vec d(1\,;1)$.

- Orthogonalité : $\overrightarrow{AA'}\cdot\vec d=0$, soit $(x'-3)+y'=0$, donc $x'+y'=3$.
- Milieu $I\left(\dfrac{x'+3}{2}\,;\dfrac{y'}{2}\right)$ sur $(\Delta)$ : $\dfrac{y'}{2}=\dfrac{x'+3}{2}+1$, donc $y'=x'+5$.

En reportant : $x'+x'+5=3$, d'où $x'=-1$ et $y'=4$.

Donc $A'(-1\,;4)$. Contrôle : le milieu de $[AA']$ est $(1\,;2)$, qui vérifie bien $2=1+1$.

### Pourquoi les autres réponses sont fausses

- **b)** c'est l'image de $A$ par la symétrie d'axe $y=x$ : on a oublié le terme $+1$ de l'équation de l'axe.
- **c)** c'est le projeté orthogonal de $A$ sur $(\Delta)$ (milieu de $[AA']$), pas son symétrique.
- **d)** on a appliqué une translation de vecteur $(1\,;-1)$ au lieu de la symétrie.

</details>

Avis : 

---

## 51. `cqc-loi-de-probabilite-moyenne-4` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D)

**Séries modifiées :** retirées PROBATOIRE:A, PROBATOIRE:C, PROBATOIRE:D.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une variable aléatoire $X$ prend les valeurs $-2$, $0$, $1$ et $3$ avec les probabilités données ci-dessous, où $a$ est un nombre réel :

| $x_i$ | $-2$ | $0$ | $1$ | $3$ |
|---|---|---|---|---|
| $P(X=x_i)$ | $a$ | $2a$ | $0{,}3$ | $0{,}1$ |

Quelle est l'espérance mathématique $E(X)$ ?

- a) $E(X)=1$
- b) $E(X)=0{,}5$
- c) $E(X)=0$
- d) $E(X)=0{,}2$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

La somme des probabilités d'une loi est égale à $1$ : cette condition permet de trouver le paramètre inconnu. L'espérance est ensuite $E(X)=\sum x_i\,P(X=x_i)$, en gardant le signe de chaque valeur $x_i$.

### Corrigé

Somme des probabilités : $a+2a+0{,}3+0{,}1=1$, donc $3a=0{,}6$ et $a=0{,}2$.

La loi est donc : $P(X=-2)=0{,}2$, $P(X=0)=0{,}4$, $P(X=1)=0{,}3$, $P(X=3)=0{,}1$.

$$E(X)=(-2)\times0{,}2+0\times0{,}4+1\times0{,}3+3\times0{,}1=-0{,}4+0+0{,}3+0{,}3=0{,}2$$

### Pourquoi les autres réponses sont fausses

- **a)** le signe de la valeur $-2$ a été oublié : $0{,}4+0{,}3+0{,}3=1$.
- **b)** c'est la moyenne simple des quatre valeurs, sans tenir compte des probabilités.
- **c)** le coefficient $2$ de $2a$ a été oublié : $2a=0{,}6$ donne $a=0{,}3$ et une loi fausse.

</details>

Avis : 

---

## 52. `cqc-matrice-inverse-prob-c-moyenne-4` (séries PROBATOIRE:C)

**Séries modifiées :** retirées PROBATOIRE:C ; ajoutées PROBATOIRE:E.

**Remarque du relecteur :** LIMITE : inverse d'une matrice 2×2 en Probatoire C, à confirmer au programme.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On considère la matrice $A=\begin{pmatrix}3&-2\\4&-1\end{pmatrix}$. Quelle est la matrice inverse de $A$ ?

- a) $\dfrac15\begin{pmatrix}3&2\\-4&-1\end{pmatrix}$
- b) $\dfrac15\begin{pmatrix}-1&2\\-4&3\end{pmatrix}$
- c) $-\dfrac1{11}\begin{pmatrix}-1&2\\-4&3\end{pmatrix}$
- d) $\dfrac15\begin{pmatrix}-1&-4\\2&3\end{pmatrix}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour $A=\begin{pmatrix}a&b\\c&d\end{pmatrix}$, on calcule $\det A=ad-bc$. Si $\det A\neq0$, $A$ est inversible et $A^{-1}=\dfrac{1}{ad-bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}$ : on échange les coefficients de la diagonale principale et on change le signe des deux autres.

### Corrigé

$\det A=3\times(-1)-(-2)\times4=-3+8=5\neq0$ : $A$ est inversible.

$$A^{-1}=\frac15\begin{pmatrix}-1&2\\-4&3\end{pmatrix}$$

Vérification : $A\times\begin{pmatrix}-1&2\\-4&3\end{pmatrix}=\begin{pmatrix}-3+8&6-6\\-4+4&8-3\end{pmatrix}=\begin{pmatrix}5&0\\0&5\end{pmatrix}$, donc le produit par $\dfrac15$ donne bien la matrice unité.

### Pourquoi les autres réponses sont fausses

- **a)** on a changé le signe des coefficients hors diagonale sans échanger ceux de la diagonale principale.
- **c)** déterminant mal calculé : $-3-8=-11$ au lieu de $-3+8=5$.
- **d)** on a transposé la bonne matrice : les coefficients hors diagonale sont mal placés.

</details>

Avis : 

---

## 53. `cqc-ordonnee-a-lorigine-faible-1` (séries BEPC:)

**Énoncé :**

Une droite $(D)$ passe par les points $A(2\,;1)$ et $B(4\,;7)$. Quelle est son ordonnée à l'origine ?

- a) $5$
- b) $-2$
- c) $-5$
- d) $\dfrac13$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Une droite non parallèle à l'axe des ordonnées a une équation de la forme $y=ax+b$, où $b$ est l'ordonnée à l'origine. On calcule d'abord le coefficient directeur $a=\dfrac{y_B-y_A}{x_B-x_A}$, puis on trouve $b$ en écrivant que les coordonnées de $A$ vérifient l'équation.

### Corrigé

Coefficient directeur :

$$a=\frac{7-1}{4-2}=\frac62=3$$

$A$ appartient à $(D)$ : $1=3\times2+b$, donc $b=1-6=-5$.

Contrôle avec $B$ : $3\times4-5=7$. L'ordonnée à l'origine est $-5$.

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe en isolant $b$ : $b=1-6$ vaut $-5$.
- **b)** on a écrit $b=1-3$ en oubliant de multiplier le coefficient directeur par l'abscisse $2$ de $A$.
- **d)** le coefficient directeur a été calculé à l'envers ($\frac{4-2}{7-1}=\frac13$), ce qui fausse $b$.

</details>

Avis : 

---

## 54. `cqc-point-moyen-moyenne-0` (séries BAC:A BAC:D BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans un village, on a interrogé $10$ familles sur le nombre $x$ d'enfants de moins de cinq ans et le nombre $y$ de moustiquaires qu'elles possèdent. Les résultats sont regroupés ci-dessous :

| $x_i$ | 1 | 2 | 4 |
|---|---|---|---|
| $y_i$ | 1 | 2 | 3 |
| Nombre de familles | 3 | 5 | 2 |

Quelles sont les coordonnées du point moyen $G$ de cette série statistique double ?

- a) $G(2{,}1\,;1{,}9)$
- b) $G\left(\dfrac73\,;2\right)$
- c) $G\left(7\,;\dfrac{19}{3}\right)$
- d) $G(1{,}9\,;2{,}1)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Le point moyen $G(\bar x\,;\bar y)$ a pour coordonnées les moyennes des deux caractères. Quand chaque couple apparaît plusieurs fois, chaque valeur est pondérée par son effectif et on divise par l'effectif total $N$, et non par le nombre de colonnes.

### Corrigé

Effectif total : $N=3+5+2=10$.

$$\bar x=\frac{3\times1+5\times2+2\times4}{10}=\frac{21}{10}=2{,}1\qquad \bar y=\frac{3\times1+5\times2+2\times3}{10}=\frac{19}{10}=1{,}9$$

Donc $G(2{,}1\,;1{,}9)$.

### Pourquoi les autres réponses sont fausses

- **b)** moyennes simples des trois colonnes, sans tenir compte du nombre de familles.
- **c)** les sommes pondérées ont été divisées par le nombre de colonnes ($3$) au lieu de l'effectif total $10$.
- **d)** les deux coordonnées ont été échangées.

</details>

Avis : 

---

## 55. `cqc-produit-vectoriel-moyenne-2` (séries BAC:C BAC:E PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** LIMITE : au Probatoire, sans produit vectoriel, passer par 1/2*sqrt(AB²AC²-(AB.AC)²)=1/2*sqrt(49).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans l'espace muni d'un repère orthonormé (unité : le centimètre), on considère les points $A(1\,;0\,;0)$, $B(0\,;2\,;0)$ et $C(0\,;0\,;3)$. Quelle est l'aire du triangle $ABC$ ?

- a) $7$ cm²
- b) $\dfrac72$ cm²
- c) $\dfrac{49}{2}$ cm²
- d) $\dfrac12$ cm²

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

L'aire d'un triangle $ABC$ de l'espace vaut $\dfrac12\left\|\overrightarrow{AB}\wedge\overrightarrow{AC}\right\|$ : la norme du produit vectoriel est l'aire du parallélogramme construit sur les deux vecteurs, et le triangle en est la moitié.

### Corrigé

$\overrightarrow{AB}(-1\,;2\,;0)$ et $\overrightarrow{AC}(-1\,;0\,;3)$.

$$\overrightarrow{AB}\wedge\overrightarrow{AC}=\begin{pmatrix}2\times3-0\times0\\0\times(-1)-(-1)\times3\\(-1)\times0-2\times(-1)\end{pmatrix}=\begin{pmatrix}6\\3\\2\end{pmatrix}$$

$$\left\|\overrightarrow{AB}\wedge\overrightarrow{AC}\right\|=\sqrt{36+9+4}=\sqrt{49}=7$$

L'aire du triangle est $\dfrac72$ cm².

### Pourquoi les autres réponses sont fausses

- **a)** c'est l'aire du parallélogramme : le facteur $\dfrac12$ a été oublié.
- **c)** on a pris le carré de la norme ($49$) au lieu de la norme.
- **d)** confusion entre produit scalaire et produit vectoriel : $\overrightarrow{AB}\cdot\overrightarrow{AC}=1$.

</details>

Avis : 

---

## 56. `cqc-relations-coefficients-racines-faible-1` (séries BAC:C BAC:D PROBATOIRE:A PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

L'équation $2x^2-7x+3=0$ admet deux solutions réelles distinctes $x_1$ et $x_2$. Quelle est la valeur de $\dfrac1{x_1}+\dfrac1{x_2}$ ?

- a) $\dfrac37$
- b) $-\dfrac73$
- c) $\dfrac76$
- d) $\dfrac73$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Si l'équation $ax^2+bx+c=0$ admet deux solutions $x_1$ et $x_2$, leur somme vaut $S=-\dfrac ba$ et leur produit $P=\dfrac ca$. Une expression symétrique comme $\dfrac1{x_1}+\dfrac1{x_2}=\dfrac{x_1+x_2}{x_1x_2}=\dfrac SP$ se calcule alors sans résoudre l'équation.

### Corrigé

Ici $a=2$, $b=-7$, $c=3$ (le discriminant $49-24=25$ est positif).

$$S=-\frac{-7}{2}=\frac72\qquad P=\frac32$$

$$\frac1{x_1}+\frac1{x_2}=\frac{S}{P}=\frac{7/2}{3/2}=\frac73$$

Contrôle : les solutions sont $3$ et $\dfrac12$, et $\dfrac13+2=\dfrac73$.

### Pourquoi les autres réponses sont fausses

- **a)** on a calculé $\dfrac PS$ au lieu de $\dfrac SP$.
- **b)** erreur de signe sur la somme : on a pris $S=\dfrac ba$ au lieu de $-\dfrac ba$.
- **c)** on a pris le produit égal à $c=3$ en oubliant de diviser par $a=2$.

</details>

Avis : 

---

## 57. `cqc-rotation-moyenne-4` (séries BAC:C BAC:D BAC:E BAC:TI BEPC: PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : au BEPC la rotation se construit sur quadrillage ; calculer les coordonnées de l'image en repère est à la limite haute (faisable par lecture sur quadrillage du quart de tour).

**Énoncé :**

Dans un repère orthonormé, on considère les points $\Omega(1\,;1)$ et $A(4\,;2)$. On note $A'$ l'image de $A$ par la rotation de centre $\Omega$ et d'angle $90°$ dans le sens inverse des aiguilles d'une montre. Quelles sont les coordonnées de $A'$ ?

- a) $A'(2\,;-2)$
- b) $A'(0\,;4)$
- c) $A'(-1\,;3)$
- d) $A'(-2\,;0)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Une rotation d'un quart de tour de centre $\Omega$ transforme le déplacement de $\Omega$ vers $A$ en un déplacement de même longueur, tourné d'un quart de tour. Dans le sens inverse des aiguilles d'une montre, le déplacement « $p$ vers la droite, $q$ vers le haut » devient « $q$ vers la gauche, $p$ vers le haut ». On ajoute ensuite ce nouveau déplacement aux coordonnées du centre $\Omega$.

### Corrigé

Pour aller de $\Omega(1\,;1)$ à $A(4\,;2)$, on se déplace de $3$ vers la droite et de $1$ vers le haut.

Après un quart de tour dans le sens inverse des aiguilles d'une montre, ce déplacement devient : $1$ vers la gauche et $3$ vers le haut.

En partant de $\Omega$ : $A'(1-1\,;1+3)=A'(0\,;4)$.

Contrôle : $\Omega A^2=3^2+1^2=10$ et $\Omega A'^2=(-1)^2+3^2=10$, la rotation conserve bien la distance au centre.

### Pourquoi les autres réponses sont fausses

- **a)** la rotation a été faite dans le sens des aiguilles d'une montre.
- **c)** c'est le déplacement tourné, que l'on a oublié d'ajouter aux coordonnées du centre $\Omega$.
- **d)** c'est l'image par un demi-tour ($180°$) et non par un quart de tour.

</details>

Avis : 

---

## 58. `cqc-similitude-directe-moyenne-0` (séries BAC:C BAC:D BAC:E BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** Nombres complexes et similitudes : programme de Terminale C/E, hors Probatoire C/E listé.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans le plan complexe, la similitude directe $s$ a pour écriture complexe $z'=(1+i)z+2-i$. Quelle est l'affixe de son centre ?

- a) $-1-2i$
- b) $\dfrac{1-3i}{2}$
- c) $1+2i$
- d) $2-i$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Le centre d'une similitude directe $z'=az+b$ (avec $a\neq1$) est son unique point invariant : son affixe $\omega$ vérifie $\omega=a\omega+b$, soit $\omega=\dfrac{b}{1-a}$.

### Corrigé

On résout $\omega=(1+i)\omega+2-i$ :

$$\omega-(1+i)\omega=2-i\iff -i\,\omega=2-i\iff \omega=\frac{2-i}{-i}=\frac{(2-i)\,i}{1}=2i+1$$

L'affixe du centre est $1+2i$.

Vérification : $(1+i)(1+2i)+2-i=1+3i-2+2-i=1+2i$.

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe : on a résolu $(a-1)\omega=b$ au lieu de $(1-a)\omega=b$.
- **b)** on a calculé $\dfrac ba$ au lieu de $\dfrac{b}{1-a}$.
- **d)** on a pris pour centre le point d'affixe $b$, image de l'origine.

</details>

Avis : 

---

## 59. `cqc-etude-de-fonction-moyenne-0` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=-2x^2+8x-3$. Quelle est la valeur maximale de $f$ sur $\mathbb{R}$ ?

- a) $2$
- b) $5$
- c) $-3$
- d) $21$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une fonction polynôme du second degré $f(x)=ax^2+bx+c$ avec $a<0$, on l'écrit sous forme canonique $f(x)=a(x-\alpha)^2+\beta$ avec $\alpha=-\dfrac{b}{2a}$ et $\beta=f(\alpha)$. Comme $a(x-\alpha)^2\leq0$, la fonction admet un maximum égal à $\beta$, atteint en $x=\alpha$. On demande la valeur de ce maximum, pas l'endroit où il est atteint.

### Corrigé

$\alpha=-\dfrac{8}{2\times(-2)}=2$ et $\beta=f(2)=-2\times4+16-3=5$.

Forme canonique : $f(x)=-2(x-2)^2+5$. Pour tout réel $x$, $-2(x-2)^2\leq0$, donc $f(x)\leq5$, avec égalité pour $x=2$.

La valeur maximale de $f$ est $5$.

### Pourquoi les autres réponses sont fausses

- **a)** c'est l'abscisse $\alpha$ où le maximum est atteint, pas la valeur du maximum.
- **c)** c'est $f(0)$, l'ordonnée à l'origine, qui n'est pas le maximum.
- **d)** erreur de signe en calculant $f(2)$ : $-2\times2^2$ a été compté $+8$.

</details>

Avis : 

---

## 60. `cqc-identite-remarquable-elevee-0` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Énoncé :**

Soit $x$ un réel non nul tel que $x+\dfrac1x=3$.

Quelle est la valeur de $x^4+\dfrac{1}{x^4}$ ?

- a) $81$
- b) $49$
- c) $79$
- d) $47$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Avec l'identité remarquable $(a+b)^2=a^2+2ab+b^2$ et $a\times\dfrac1a=1$, on obtient $\left(a+\dfrac1a\right)^2=a^2+2+\dfrac1{a^2}$, donc $a^2+\dfrac1{a^2}=\left(a+\dfrac1a\right)^2-2$. On applique cette relation deux fois de suite, sans calculer $x$.

### Corrigé

Avec $a=x$ : $x^2+\dfrac1{x^2}=3^2-2=7$.

Avec $a=x^2$ : $x^4+\dfrac1{x^4}=\left(x^2+\dfrac1{x^2}\right)^2-2=7^2-2=47$.

Contrôle numérique : $x=\dfrac{3+\sqrt5}{2}\approx2{,}618$ vérifie $x+\dfrac1x=3$ et donne $x^4+\dfrac1{x^4}\approx47{,}000$.

### Pourquoi les autres réponses sont fausses

- **a)** On a écrit $\left(x+\dfrac1x\right)^4=x^4+\dfrac1{x^4}$ en oubliant tous les termes croisés.
- **b)** On a élevé $7$ au carré sans retrancher $2$ à la seconde étape.
- **c)** On a calculé $3^4-2$ : la relation $a^2+\dfrac1{a^2}=\left(a+\dfrac1a\right)^2-2$ porte sur un carré, pas sur une puissance quatrième.

</details>

Avis : 

---

## 61. `cqc-majoration-bac-ti-mat-moyenne-1` (séries BAC:TI)

**Remarque du relecteur :** LIMITE : majoration de |f'| préparatoire à l'inégalité des accroissements finis ; la question elle-même se traite par étude de fonction.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=(x-1)\,e^{-x}$.

Quel est le plus petit réel $M$ tel que, pour tout $x\in[3\,;5]$, $|f'(x)|\le M$ ?

- a) $e^{-3}$
- b) $3e^{-3}$
- c) $3e^{-5}$
- d) $2e^{-3}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Majorer chaque facteur séparément donne un majorant, mais pas toujours le plus petit. Le plus petit majorant de $|f'|$ sur un intervalle fermé est le maximum de $|f'|$ sur cet intervalle : on étudie les variations de la fonction $x\mapsto|f'(x)|$.

### Corrigé

$f'(x)=1\times e^{-x}+(x-1)\times\left(-e^{-x}\right)=(2-x)\,e^{-x}$.

Sur $[3\,;5]$, $2-x<0$, donc $|f'(x)|=(x-2)\,e^{-x}$. Posons $g(x)=(x-2)\,e^{-x}$ :
$$g'(x)=e^{-x}-(x-2)e^{-x}=(3-x)\,e^{-x}\le0\ \text{sur}\ [3\,;5].$$
$g$ est décroissante sur $[3\,;5]$ : son maximum est $g(3)=e^{-3}$.

Le plus petit majorant est $M=e^{-3}\approx0{,}0498$ (valeur arrondie au dix-millième).

### Pourquoi les autres réponses sont fausses

- **b)** $3e^{-3}$ vient de $x-2\le3$ et $e^{-x}\le e^{-3}$ majorés séparément : c'est un majorant, mais pas le plus petit, car les deux bornes ne sont pas atteintes pour la même valeur de $x$.
- **c)** $3e^{-5}=g(5)$ est le MINIMUM de $|f'|$ sur $[3\,;5]$ : confusion entre la borne où $g$ est maximale et celle où elle est minimale.
- **d)** $2e^{-3}=f(3)$ : on a travaillé sur $f$ au lieu de $f'$.

</details>

Avis : 

---

## 62. `cqc-point-moyen-moyenne-1` (séries BAC:A BAC:D BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une coopérative agricole a relevé, sur 8 parcelles, la surface $x$ (en hectares) et la récolte $y$ (en tonnes). Le point moyen de cette série est $G(5\,;12)$. On ajoute à la série une neuvième parcelle : $x=14$ et $y=30$.

Quelles sont les coordonnées du nouveau point moyen $G'$ ?

- a) $G'(6{,}75\,;15{,}75)$
- b) $G'(9{,}5\,;21)$
- c) $G'(5\,;12)$
- d) $G'(6\,;14)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Si une série de $n$ couples a pour point moyen $G(\bar{x}\,;\bar{y})$, la somme des $x_i$ vaut $n\bar{x}$ et celle des $y_i$ vaut $n\bar{y}$. Après ajout d'un couple, on ajoute ses coordonnées à ces sommes et on divise par le nouvel effectif $n+1$.

### Corrigé

Sommes des 8 premières valeurs : $\sum x_i=8\times5=40$ et $\sum y_i=8\times12=96$.

Avec la neuvième parcelle :
$$\bar{x}'=\dfrac{40+14}{9}=\dfrac{54}{9}=6\qquad\bar{y}'=\dfrac{96+30}{9}=\dfrac{126}{9}=14.$$

Le nouveau point moyen est $G'(6\,;14)$.

### Pourquoi les autres réponses sont fausses

- **a)** Les nouvelles sommes ont été divisées par $8$ au lieu de $9$ : $\dfrac{54}{8}=6{,}75$ et $\dfrac{126}{8}=15{,}75$.
- **b)** On a fait la moyenne de $G$ et du nouveau point, comme si $G$ ne représentait qu'une seule parcelle au lieu de huit.
- **c)** L'ajout d'un couple modifie en général le point moyen ; il ne reste inchangé que si le couple ajouté est égal à $G$.

</details>

Avis : 

---

## 63. `cqc-produit-vectoriel-moyenne-3` (séries BAC:C BAC:E PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** LIMITE : le produit vectoriel est de Terminale ; au Probatoire C/E, seule voie par le produit scalaire (aire=1/2 sqrt(AB^2 AC^2-(AB.AC)^2)).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

L'espace est muni d'un repère orthonormé direct. On considère les points $A(1\,;0\,;2)$, $B(3\,;1\,;0)$ et $C(0\,;2\,;1)$.

Quelle est l'aire du triangle $ABC$, en unités d'aire ?

- a) $\dfrac{5\sqrt2}{2}$
- b) $5\sqrt2$
- c) $\dfrac{\sqrt{34}}{2}$
- d) $25$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

L'aire du parallélogramme construit sur $\overrightarrow{AB}$ et $\overrightarrow{AC}$ est $\|\overrightarrow{AB}\wedge\overrightarrow{AC}\|$ ; le triangle $ABC$ en est la moitié : $\mathcal A=\dfrac12\|\overrightarrow{AB}\wedge\overrightarrow{AC}\|$. On contrôle le produit vectoriel en vérifiant qu'il est orthogonal aux deux vecteurs.

### Corrigé

$\overrightarrow{AB}(2\,;1\,;-2)$ et $\overrightarrow{AC}(-1\,;2\,;-1)$.

$$\overrightarrow{AB}\wedge\overrightarrow{AC}=\big(1\times(-1)-(-2)\times2\,;\,(-2)\times(-1)-2\times(-1)\,;\,2\times2-1\times(-1)\big)=(3\,;4\,;5).$$

Contrôle : $2\times3+1\times4-2\times5=0$ et $-3+8-5=0$.

$\|\overrightarrow{AB}\wedge\overrightarrow{AC}\|=\sqrt{9+16+25}=\sqrt{50}=5\sqrt2$, donc
$$\mathcal A=\dfrac{5\sqrt2}{2}.$$

### Pourquoi les autres réponses sont fausses

- **b)** C'est l'aire du parallélogramme : on a oublié le facteur $\dfrac12$.
- **c)** Erreur de signe sur la deuxième coordonnée du produit vectoriel ($2-2=0$ au lieu de $2+2=4$), d'où une norme $\sqrt{34}$.
- **d)** On a pris $\dfrac12\|\overrightarrow{AB}\wedge\overrightarrow{AC}\|^2=\dfrac{50}{2}$ en oubliant la racine carrée de la norme.

</details>

Avis : 

---

## 64. `cqc-relations-coefficients-racines-moyenne-0` (séries BAC:C BAC:D PROBATOIRE:A PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

L'équation $2x^2-7x+3=0$ admet deux solutions réelles $x_1$ et $x_2$.

Quelle est la valeur de $\dfrac{1}{x_1}+\dfrac{1}{x_2}$ ?

- a) $-\dfrac73$
- b) $\dfrac73$
- c) $\dfrac37$
- d) $\dfrac72$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Si l'équation $ax^2+bx+c=0$ a deux solutions $x_1$ et $x_2$, leur somme est $S=x_1+x_2=-\dfrac{b}{a}$ et leur produit $P=x_1x_2=\dfrac{c}{a}$. On exprime la quantité demandée à l'aide de $S$ et $P$ : $\dfrac1{x_1}+\dfrac1{x_2}=\dfrac{x_1+x_2}{x_1x_2}=\dfrac{S}{P}$.

### Corrigé

Le discriminant vaut $49-24=25>0$ : il y a bien deux solutions réelles, non nulles car $P\ne0$.

$S=-\dfrac{-7}{2}=\dfrac72$ et $P=\dfrac32$.
$$\dfrac1{x_1}+\dfrac1{x_2}=\dfrac{S}{P}=\dfrac{7/2}{3/2}=\dfrac73.$$

Contrôle : les solutions sont $3$ et $\dfrac12$, et $\dfrac13+2=\dfrac73$.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur la somme : on a pris $S=\dfrac{b}{a}=-\dfrac72$ au lieu de $-\dfrac{b}{a}$.
- **c)** On a calculé $\dfrac{P}{S}$ au lieu de $\dfrac{S}{P}$.
- **d)** C'est la somme $S=x_1+x_2$ : on a confondu la somme des inverses avec la somme des solutions.

</details>

Avis : 

---

## 65. `cqc-similitude-directe-moyenne-1` (séries BAC:C BAC:D BAC:E BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** Nombres complexes et similitudes : programme de Terminale, hors Probatoire C/E listé.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan complexe est muni d'un repère orthonormé direct. On considère la similitude directe $s$ d'écriture complexe $z'=(1+i)z+2-i$.

Quels sont le rapport et l'affixe du centre de $s$ ?

- a) Rapport $2$, centre d'affixe $1+2i$
- b) Rapport $\sqrt2$, centre d'affixe $-1-2i$
- c) Rapport $\sqrt2$, centre d'affixe $1+2i$
- d) Rapport $\sqrt2$, centre d'affixe $2-i$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une similitude directe d'écriture $z'=az+b$ avec $a\ne1$ : le rapport est $|a|$, une mesure de l'angle est un argument de $a$, et le centre est l'unique point invariant, d'affixe $\omega$ solution de $\omega=a\omega+b$, soit $\omega=\dfrac{b}{1-a}$.

### Corrigé

Rapport : $|1+i|=\sqrt{1^2+1^2}=\sqrt2$ (et un argument de $1+i$ est $\dfrac\pi4$).

Centre : $\omega=(1+i)\omega+2-i\iff-i\,\omega=2-i\iff\omega=\dfrac{2-i}{-i}=\dfrac{(2-i)\,i}{-i\times i}=2i+1$.

Vérification : $(1+i)(1+2i)+2-i=(-1+3i)+2-i=1+2i$.

Le rapport est $\sqrt2$ et le centre a pour affixe $1+2i$.

### Pourquoi les autres réponses sont fausses

- **a)** On a pris $|1+i|^2=2$ au lieu de $|1+i|=\sqrt2$.
- **b)** Erreur de signe en isolant $\omega$ : on a écrit $\omega=\dfrac{b}{a-1}$ au lieu de $\dfrac{b}{1-a}$.
- **d)** On a pris le terme constant $b=2-i$ pour l'affixe du centre ; or $(1+i)(2-i)+2-i=5\ne2-i$, ce point n'est pas invariant.

</details>

Avis : 

---

## 66. `cqc-triplet-pythagoricien-elevee-5` (séries BAC:C BAC:E BEPC:)

**Remarque du relecteur :** LIMITE : au BEPC l'équation du second degré n'est pas au programme ; la résolution passe par l'essai des choix avec Pythagore ou une factorisation guidée.

**Énoncé :**

Un menuisier fabrique un gabarit en forme de triangle rectangle dont les côtés mesurent, en décimètres, $n$, $n+7$ et $n+8$, où $n$ est un entier naturel non nul. Le plus long côté est l'hypoténuse.

Quelle est la valeur de $n$ ?

- a) $5$
- b) $3$
- c) $8$
- d) $15$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un triangle rectangle, le carré de l'hypoténuse est égal à la somme des carrés des deux autres côtés (théorème de Pythagore). On traduit cette égalité par une équation en $n$, on la ramène à une équation produit grâce aux identités remarquables, puis on ne garde que les solutions positives et on vérifie.

### Corrigé

Le théorème de Pythagore donne $n^2+(n+7)^2=(n+8)^2$, soit
$$n^2+n^2+14n+49=n^2+16n+64\iff n^2-2n-15=0.$$

Or $n^2-2n-15=(n-1)^2-16=(n-1-4)(n-1+4)=(n-5)(n+3)$. L'équation produit donne $n=5$ ou $n=-3$ ; comme $n>0$, $n=5$.

Vérification : les côtés mesurent $5$, $12$ et $13$ dm, et $5^2+12^2=25+144=169=13^2$.

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de signe sur la solution $n=-3$ de l'équation produit ; avec $n=3$, les côtés $3$, $10$, $11$ donnent $9+100=109\ne121$.
- **c)** $8$, $15$, $17$ est bien un triangle rectangle, mais ici les côtés seraient $8$, $15$ et $n+8=16$, et $64+225=289\ne256$.
- **d)** $15$ est le terme constant de l'équation $n^2-2n-15=0$, pas une solution ; les côtés $15$, $22$, $23$ donnent $225+484=709\ne529$.

</details>

Avis : 

---

## 67. `cqc-vecteur-normal-prob-c-moyenne-4` (séries PROBATOIRE:C PROBATOIRE:E)

**Énoncé :**

Dans un repère orthonormé du plan, la droite $(D)$ passe par le point $A(2\,;-1)$ et admet $\vec n(3\,;-4)$ pour vecteur normal.

Quelle est une équation cartésienne de $(D)$ ?

- a) $3x-4y+10=0$
- b) $4x+3y-5=0$
- c) $3x-4y-10=0$
- d) $3x-4y-2=0$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Un point $M(x\,;y)$ appartient à la droite passant par $A$ de vecteur normal $\vec n(a\,;b)$ si et seulement si $\overrightarrow{AM}\cdot\vec n=0$. L'équation est donc de la forme $ax+by+c=0$, où $(a\,;b)$ sont les coordonnées de $\vec n$ (et non d'un vecteur directeur) ; on obtient $c$ en écrivant que $A$ vérifie l'équation.

### Corrigé

$(D)$ a une équation de la forme $3x-4y+c=0$. Comme $A(2\,;-1)\in(D)$ :
$$3\times2-4\times(-1)+c=0\iff6+4+c=0\iff c=-10.$$

Une équation de $(D)$ est $3x-4y-10=0$.

Contrôle : $\overrightarrow{AM}(x-2\,;y+1)$ et $\overrightarrow{AM}\cdot\vec n=3(x-2)-4(y+1)=3x-4y-10$.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur $c$ : avec $3x-4y+10=0$, le point $A$ donne $6+4+10=20\ne0$.
- **b)** On a traité $\vec n$ comme un vecteur directeur : cette droite passe bien par $A$, mais elle est perpendiculaire à $(D)$.
- **d)** Le produit $-4\times(-1)$ a été compté $-4$ : $c=-(6-4)=-2$ ; or $A$ donne $6+4-2=8\ne0$.

</details>

Avis : 

---

## 68. `cqc-derivee-seconde-faible-0` (séries BAC:A BAC:C BAC:D)

**Séries modifiées :** retirées BAC:A.

**Remarque du relecteur :** LIMITE : dérivée seconde en série A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $]0\,;+\infty[$ par $f(x)=2x^3-3x^2+\dfrac{1}{x}$. Quelle est la valeur de $f''(1)$ ?

- a) $8$
- b) $4$
- c) $-1$
- d) $6$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

La dérivée seconde $f''$ est la dérivée de $f'$. Pour la fonction inverse : $\left(\dfrac1x\right)'=-\dfrac{1}{x^2}$, puis $\left(-\dfrac{1}{x^2}\right)'=\dfrac{2}{x^3}$. Les signes changent à chaque dérivation : c'est le point à surveiller.

### Corrigé

$f'(x)=6x^2-6x-\dfrac{1}{x^2}$, puis $f''(x)=12x-6+\dfrac{2}{x^3}$.

Donc $f''(1)=12-6+2=8$.

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de signe sur la dérivée de $-\dfrac{1}{x^2}$ : on a écrit $-\dfrac{2}{x^3}$, d'où $12-6-2=4$.
- **c)** C'est $f'(1)=6-6-1$ : on s'est arrêté à la dérivée première.
- **d)** On a oublié le terme $\dfrac1x$ en dérivant deux fois (comme s'il s'agissait d'une constante).

</details>

Avis : 

---

## 69. `cqc-isometrie-tle-c-faible-0` (séries BAC:C BAC:E)

**Énoncé :**

Dans le plan complexe, laquelle des transformations suivantes, données par leur écriture complexe, est une isométrie ?

- a) $z'=(1+i)z+1$
- b) $z'=\dfrac{3-4i}{5}z+2i$
- c) $z'=2iz$
- d) $z'=\dfrac{1+i}{2}z$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Une transformation d'écriture $z'=az+b$ ($a\neq0$) multiplie toutes les distances par $|a|$ : $|z'_2-z'_1|=|a|\,|z_2-z_1|$. C'est une isométrie si et seulement si $|a|=1$. Il faut donc calculer le module de $a$, et non regarder seulement s'il est réel ou s'il contient $i$.

### Corrigé

Pour $z'=\dfrac{3-4i}{5}z+2i$ : $\left|\dfrac{3-4i}{5}\right|=\dfrac{\sqrt{9+16}}{5}=\dfrac55=1$.

Cette transformation conserve donc les distances : c'est une isométrie (une rotation).

### Pourquoi les autres réponses sont fausses

- **a)** $|1+i|=\sqrt2\neq1$ : les distances sont multipliées par $\sqrt2$.
- **c)** $|2i|=2$ : les distances sont multipliées par $2$ ; la présence de $i$ n'en fait pas une rotation.
- **d)** $\left|\dfrac{1+i}{2}\right|=\dfrac{\sqrt2}{2}\neq1$ : les distances sont multipliées par $\dfrac{\sqrt2}{2}$.

</details>

Avis : 

---

## 70. `cqc-matrice-prob-c-elevee-5` (séries PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans le plan muni d'une base $(\vec\imath,\vec\jmath)$, on considère l'application linéaire $f$ de matrice
$$M=\begin{pmatrix}3&-6\\1&-2\end{pmatrix}.$$
Quelle est la nature de $f$ ?

- a) La projection sur la droite dirigée par $(2\,;1)$, parallèlement à la droite dirigée par $(3\,;1)$
- b) La symétrie par rapport à la droite dirigée par $(3\,;1)$, parallèlement à la droite dirigée par $(2\,;1)$
- c) La projection sur la droite dirigée par $(1\,;3)$, parallèlement à la droite dirigée par $(2\,;1)$
- d) La projection sur la droite dirigée par $(3\,;1)$, parallèlement à la droite dirigée par $(2\,;1)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Une application linéaire $f$ du plan est une projection si et seulement si $f\circ f=f$, c'est-à-dire $M^2=M$. C'est alors la projection sur son image (droite engendrée par les colonnes de $M$) parallèlement à son noyau (ensemble des vecteurs d'image nulle). Une symétrie vérifierait $M^2=I$.

### Corrigé

$$M^2=\begin{pmatrix}9-6&-18+12\\3-2&-6+4\end{pmatrix}=\begin{pmatrix}3&-6\\1&-2\end{pmatrix}=M,$$
donc $f\circ f=f$ : $f$ est une projection.

Noyau : $f(x\,;y)=\vec0\iff 3x-6y=0$ et $x-2y=0\iff x=2y$ : c'est la droite dirigée par $(2\,;1)$.

Image : les colonnes $(3\,;1)$ et $(-6\,;-2)=-2(3\,;1)$ sont colinéaires : c'est la droite dirigée par $(3\,;1)$.

**Vérification** : $f(2\,;1)=(6-6\,;2-2)=(0\,;0)$ et $f(3\,;1)=(9-6\,;3-2)=(3\,;1)$.

$f$ est la projection sur la droite dirigée par $(3\,;1)$, parallèlement à la droite dirigée par $(2\,;1)$.

### Pourquoi les autres réponses sont fausses

- **a)** On a inversé les rôles : $f(2\,;1)=\vec0$, donc $(2\,;1)$ donne la direction de projection, pas la droite sur laquelle on projette.
- **b)** Une symétrie vérifierait $M^2=I$ ; ici $M^2=M\neq I$ (et $\det M=0$, alors qu'une symétrie est bijective).
- **c)** On a lu l'image sur une ligne de $M$ au lieu d'une colonne : $f(1\,;3)=(-15\,;-5)$ n'est pas colinéaire à $(1\,;3)$.

</details>

Avis : 

---

## 71. `cqc-parabole-tle-c-faible-0` (séries BAC:C BAC:E PROBATOIRE:A)

**Remarque du relecteur :** Doublon exact de la question 15 (même équation, mêmes choix).

**Énoncé :**

Dans un repère orthonormé, quelles sont les coordonnées du sommet de la parabole d'équation $y=-2x^2+8x-5$ ?

- a) $(2\,;3)$
- b) $(-2\,;-29)$
- c) $(4\,;-5)$
- d) $(2\,;19)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

La parabole d'équation $y=ax^2+bx+c$ ($a\neq0$) a pour sommet le point d'abscisse $x_S=-\dfrac{b}{2a}$ et d'ordonnée $y_S=ax_S^2+bx_S+c$. On peut aussi passer par la forme canonique $a(x-x_S)^2+y_S$.

### Corrigé

Ici $a=-2$, $b=8$, $c=-5$ : $x_S=-\dfrac{8}{2\times(-2)}=2$ et $y_S=-2\times4+8\times2-5=-8+16-5=3$.

**Vérification par la forme canonique** : $-2(x-2)^2+3=-2x^2+8x-8+3=-2x^2+8x-5$.

Le sommet est $S(2\,;3)$.

### Pourquoi les autres réponses sont fausses

- **b)** Oubli du signe dans $-\dfrac{b}{2a}$ : on a pris $x_S=\dfrac{b}{2a}=-2$, d'où $y=-8-16-5=-29$.
- **c)** On a utilisé $-\dfrac ba=4$ au lieu de $-\dfrac{b}{2a}$ : le point $(4\,;-5)$ est sur la parabole mais n'en est pas le sommet.
- **d)** Erreur de signe sur $-2\times2^2$, compté $+8$ : $8+16-5=19$.

</details>

Avis : 

---

## 72. `cqc-relations-coefficients-racines-moyenne-1` (séries BAC:C BAC:D PROBATOIRE:A PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:A.

**Remarque du relecteur :** LIMITE : somme et produit des racines pour le Probatoire A, à vérifier au programme de 1re A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

L'équation $3x^2-5x-4=0$ admet deux racines réelles $x_1$ et $x_2$. Sans calculer ces racines, quelle est la valeur de $x_1^2+x_2^2$ ?

- a) $\dfrac{1}{9}$
- b) $33$
- c) $\dfrac{37}{9}$
- d) $\dfrac{49}{9}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour $ax^2+bx+c=0$ ($a\neq0$) admettant deux racines $x_1$ et $x_2$ : $S=x_1+x_2=-\dfrac ba$ et $P=x_1x_2=\dfrac ca$. On exprime ensuite la quantité demandée à l'aide de $S$ et $P$ ; par exemple $x_1^2+x_2^2=(x_1+x_2)^2-2x_1x_2=S^2-2P$.

### Corrigé

$\Delta=25+48=73>0$ : les deux racines existent.

$S=\dfrac{5}{3}$ et $P=-\dfrac{4}{3}$.

$$x_1^2+x_2^2=S^2-2P=\dfrac{25}{9}+\dfrac{8}{3}=\dfrac{25}{9}+\dfrac{24}{9}=\dfrac{49}{9}.$$

### Pourquoi les autres réponses sont fausses

- **a)** On a écrit $S^2+2P$ (erreur de signe dans l'identité), d'où $\dfrac{25}{9}-\dfrac{8}{3}=\dfrac19$.
- **b)** On a oublié de diviser par $a=3$ : avec $S=5$ et $P=-4$, on obtient $25+8=33$.
- **c)** On a écrit $S^2-P$ au lieu de $S^2-2P$.

</details>

Avis : 

---

## 73. `cqc-recurrence-tle-c-faible-0` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI)

**Séries modifiées :** retirées BAC:A.

**Remarque du relecteur :** Suites et récurrence hors programme de la série A (BAC:A listé) ; correct pour C, D, E, TI.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On considère la suite $(u_n)$ définie par $u_0=1$ et, pour tout entier naturel $n$, $u_{n+1}=2u_n+1$. Quelle expression de $u_n$ peut-on démontrer par récurrence pour tout entier naturel $n$ ?

- a) $u_n=2^{n+1}-1$
- b) $u_n=2^{n}-1$
- c) $u_n=2n+1$
- d) $u_n=3^{n}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Avant de lancer une récurrence, on calcule plusieurs termes pour conjecturer une formule, et on vérifie la conjecture sur **tous** ces termes : deux termes ne suffisent pas à distinguer des formules différentes. On démontre ensuite l'initialisation et l'hérédité.

### Corrigé

$u_0=1$, $u_1=3$, $u_2=7$, $u_3=15$, $u_4=31$ : ce sont les nombres $2^{n+1}-1$.

**Initialisation** : $2^{0+1}-1=1=u_0$.

**Hérédité** : si $u_n=2^{n+1}-1$, alors $u_{n+1}=2(2^{n+1}-1)+1=2^{n+2}-2+1=2^{n+2}-1$.

**Conclusion** : pour tout entier naturel $n$, $u_n=2^{n+1}-1$.

### Pourquoi les autres réponses sont fausses

- **b)** Décalage d'indice : cette formule donne $0$ pour $n=0$, alors que $u_0=1$.
- **c)** Elle convient pour $u_0=1$ et $u_1=3$, mais donne $5$ pour $n=2$ alors que $u_2=7$.
- **d)** Elle convient aussi pour $u_0$ et $u_1$, mais donne $9$ pour $n=2$.

</details>

Avis : 

---

## 74. `cqc-similitude-directe-moyenne-2` (séries BAC:C BAC:D BAC:E BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** Similitudes directes et écriture complexe relèvent de la Terminale ; hors programme pour le Probatoire C/E listé.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans le plan complexe, la similitude directe $s$ a pour écriture complexe $z'=\left(1-i\sqrt3\right)z+2$. Quels sont son rapport $k$ et une mesure de son angle $\theta$ ?

- a) $k=2$ et $\theta=\dfrac{\pi}{3}$
- b) $k=2$ et $\theta=-\dfrac{\pi}{3}$
- c) $k=4$ et $\theta=-\dfrac{\pi}{3}$
- d) $k=2$ et $\theta=-\dfrac{\pi}{6}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Une similitude directe d'écriture $z'=az+b$ ($a\neq0$, $a\neq1$) a pour rapport $k=|a|$ et pour angle $\theta=\arg(a)$. On écrit $a$ sous forme trigonométrique en mettant son module en facteur.

### Corrigé

$a=1-i\sqrt3$ : $|a|=\sqrt{1+3}=2$, et $a=2\left(\dfrac12-i\dfrac{\sqrt3}{2}\right)=2\left(\cos\left(-\dfrac\pi3\right)+i\sin\left(-\dfrac\pi3\right)\right)$.

Donc $k=2$ et $\theta=-\dfrac{\pi}{3}$.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur l'argument : la partie imaginaire de $a$ est négative, donc l'angle est $-\dfrac\pi3$.
- **c)** On a oublié la racine carrée dans le module : $1+3=4$ est $|a|^2$, pas $|a|$.
- **d)** Confusion entre $\cos$ et $\sin$ : $\cos\theta=\dfrac12$ et $\sin\theta=-\dfrac{\sqrt3}{2}$ donnent $-\dfrac\pi3$, pas $-\dfrac\pi6$.

</details>

Avis : 

---

## 75. `cqc-derivee-seconde-moyenne-0` (séries BAC:A BAC:C BAC:D)

**Séries modifiées :** retirées BAC:A.

**Remarque du relecteur :** LIMITE : la dérivée seconde et les points d'inflexion sont à la limite du programme de la série A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=x^{4}-6x^{2}+1$, de courbe $(C)$.

Quels sont les points d'inflexion de $(C)$ ?

- a) $(-\sqrt3\,;-8)$ et $(\sqrt3\,;-8)$
- b) $(-1\,;-4)$ et $(1\,;-4)$
- c) $(1\,;-4)$ seulement
- d) $(-1\,;0)$ et $(1\,;0)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Un point d'inflexion est un point de la courbe où la dérivée seconde $f''$ s'annule EN CHANGEANT DE SIGNE. On résout $f''(x)=0$, on vérifie le changement de signe, puis on calcule l'ordonnée avec $f$ (et non avec $f''$).

### Corrigé

$f'(x)=4x^{3}-12x$ et $f''(x)=12x^{2}-12=12(x-1)(x+1)$.

$f''$ s'annule en $-1$ et en $1$ en changeant de signe (positive à l'extérieur des racines, négative entre elles).

$f(1)=1-6+1=-4$ et $f(-1)=1-6+1=-4$.

Les points d'inflexion sont $(-1\,;-4)$ et $(1\,;-4)$.

### Pourquoi les autres réponses sont fausses

- **a)** Ce sont les points où $f'$ s'annule (minimums de $f$) : on a confondu extremum et point d'inflexion.
- **c)** On a oublié la racine négative de l'équation $x^{2}=1$.
- **d)** On a pris pour ordonnée la valeur de $f''$ (nulle) au lieu de celle de $f$.

</details>

Avis : 

---

## 76. `cqc-matrice-prob-c-faible-0` (séries PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan vectoriel est muni d'une base $(\vec\imath,\vec\jmath)$. $f$ est l'endomorphisme de matrice
$$M=\begin{pmatrix}1&2\\3&-1\end{pmatrix}$$
dans cette base. On pose $\vec u=2\vec\imath-\vec\jmath$.

Quelles sont les coordonnées de $f(\vec u)$ dans la base $(\vec\imath,\vec\jmath)$ ?

- a) $(-1\,;5)$
- b) $(0\,;7)$
- c) $(4\,;5)$
- d) $(2\,;1)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Les colonnes de la matrice de $f$ sont les coordonnées des images des vecteurs de base : la première colonne donne $f(\vec\imath)$, la seconde $f(\vec\jmath)$. Par linéarité, $f(x\vec\imath+y\vec\jmath)=x\,f(\vec\imath)+y\,f(\vec\jmath)$.

### Corrigé

Lecture des colonnes : $f(\vec\imath)=\vec\imath+3\vec\jmath$ et $f(\vec\jmath)=2\vec\imath-\vec\jmath$.

Par linéarité :
$$f(\vec u)=2f(\vec\imath)-f(\vec\jmath)=2(\vec\imath+3\vec\jmath)-(2\vec\imath-\vec\jmath)=0\,\vec\imath+7\vec\jmath.$$

$f(\vec u)$ a pour coordonnées $(0\,;7)$. On retrouve ce résultat par le produit $M\begin{pmatrix}2\\-1\end{pmatrix}=\begin{pmatrix}2-2\\6+1\end{pmatrix}$.

### Pourquoi les autres réponses sont fausses

- **a)** On a lu les lignes au lieu des colonnes : $f(\vec\imath)=(1\,;2)$ et $f(\vec\jmath)=(3\,;-1)$ donnent $(-1\,;5)$.
- **c)** Erreur de signe : on a calculé $2f(\vec\imath)+f(\vec\jmath)$ au lieu de $2f(\vec\imath)-f(\vec\jmath)$.
- **d)** On a multiplié chaque coordonnée de $\vec u$ par le coefficient diagonal correspondant ($2\times1$ et $-1\times(-1)$), comme si la matrice était diagonale.

</details>

Avis : 

---

## 77. `cqc-position-relative-courbe-droite-faible-1` (séries BAC:A)

**Énoncé :**

Soit $f$ une fonction définie sur $]-1\,;+\infty[$, de courbe $(C)$, et $(D)$ la droite d'équation $y=2x+1$. Un calcul déjà effectué donne, pour tout $x>-1$ :
$$f(x)-(2x+1)=\dfrac{x-3}{x+1}.$$

Sur quel ensemble la courbe $(C)$ est-elle strictement au-dessus de $(D)$ ?

- a) $]-1\,;3[$
- b) $]3\,;+\infty[$
- c) $]-\infty\,;-1[\,\cup\,]3\,;+\infty[$
- d) $]-3\,;+\infty[$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

$(C)$ est strictement au-dessus de $(D)$ là où la différence $f(x)-(2x+1)$ est strictement positive. On étudie le signe de cette différence (tableau de signes d'un quotient) en se limitant à l'ensemble de définition de $f$.

### Corrigé

Sur $]-1\,;+\infty[$, le dénominateur $x+1$ est strictement positif. Le signe de la différence est donc celui de $x-3$ :
- négatif sur $]-1\,;3[$ : $(C)$ est en dessous de $(D)$ ;
- nul en $3$ : $(C)$ et $(D)$ se coupent au point d'abscisse $3$ ;
- positif sur $]3\,;+\infty[$ : $(C)$ est au-dessus de $(D)$.

$(C)$ est strictement au-dessus de $(D)$ sur $]3\,;+\infty[$.

### Pourquoi les autres réponses sont fausses

- **a)** C'est l'ensemble où la différence est négative : $(C)$ y est en dessous de $(D)$ ; le signe a été inversé.
- **c)** Le signe du quotient sur $\mathbb{R}$ a été étudié sans tenir compte de l'ensemble de définition $]-1\,;+\infty[$ de $f$.
- **d)** Erreur de signe sur la racine du numérateur : $x-3=0$ donne $x=3$ et non $x=-3$.

</details>

Avis : 

---

## 78. `cqc-relations-coefficients-racines-moyenne-2` (séries BAC:C BAC:D PROBATOIRE:A PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

L'équation $2x^{2}-6x-5=0$ admet deux solutions réelles $x_1$ et $x_2$.

Sans calculer $x_1$ ni $x_2$, que vaut $x_1^{2}+x_2^{2}$ ?

- a) $14$
- b) $4$
- c) $9$
- d) $\dfrac{23}{2}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une équation $ax^{2}+bx+c=0$ de solutions $x_1$ et $x_2$ : $S=x_1+x_2=-\dfrac{b}{a}$ et $P=x_1x_2=\dfrac{c}{a}$. Toute expression symétrique en $x_1$ et $x_2$ s'écrit à l'aide de $S$ et $P$ ; en particulier $x_1^{2}+x_2^{2}=(x_1+x_2)^{2}-2x_1x_2=S^{2}-2P$.

### Corrigé

$\Delta=36+40=76>0$ : les deux solutions existent bien.

$S=-\dfrac{-6}{2}=3$ et $P=\dfrac{-5}{2}$.
$$x_1^{2}+x_2^{2}=S^{2}-2P=9-2\times\left(-\dfrac52\right)=9+5=14.$$

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de signe : on a calculé $S^{2}+2P=9-5$ au lieu de $S^{2}-2P$.
- **c)** On a pris $x_1^{2}+x_2^{2}=(x_1+x_2)^{2}$ en oubliant le double produit $2x_1x_2$.
- **d)** On a oublié le facteur $2$ : $S^{2}-P=9+\dfrac52$.

</details>

Avis : 

---

## 79. `cqc-recurrence-tle-c-moyenne-2` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI)

**Séries modifiées :** retirées BAC:A.

**Remarque du relecteur :** Raisonnement par récurrence (suites) hors programme de la série A (BAC:A listé) ; correct pour C, D, E, TI.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On veut démontrer par récurrence une inégalité de la forme « pour tout entier $n\geq n_0$, $2^{n}>n^{2}$ ».

Quel est le plus petit entier naturel $n_0$ pour lequel cette propriété est vraie pour TOUS les entiers $n\geq n_0$ ?

- a) $0$
- b) $5$
- c) $3$
- d) $4$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Une démonstration par récurrence exige une initialisation au rang $n_0$ ET une hérédité valable pour tout $n\geq n_0$. Une inégalité peut être vraie pour quelques petits entiers, fausse ensuite, puis vraie à nouveau : on teste les premiers rangs, puis on vérifie que l'hérédité fonctionne à partir du rang choisi.

### Corrigé

Premiers rangs : $n=0$ : $1>0$ vrai ; $n=1$ : $2>1$ vrai ; $n=2$ : $4>4$ faux ; $n=3$ : $8>9$ faux ; $n=4$ : $16>16$ faux ; $n=5$ : $32>25$ vrai.

**Initialisation** au rang $5$ : $32>25$.

**Hérédité** pour $n\geq5$ : si $2^{n}>n^{2}$, alors $2^{n+1}>2n^{2}$. Or $2n^{2}-(n+1)^{2}=n^{2}-2n-1=(n-1)^{2}-2>0$ pour $n\geq3$, donc $2^{n+1}>(n+1)^{2}$.

La propriété est vraie pour tout $n\geq5$, et fausse pour $n=4$ : $n_0=5$.

### Pourquoi les autres réponses sont fausses

- **a)** L'inégalité est vraie en $0$ et en $1$, mais fausse pour $n=2$, $3$ et $4$ : l'initialisation seule ne suffit pas.
- **c)** Pour $n=3$ : $2^{3}=8$ et $3^{2}=9$, l'inégalité est fausse.
- **d)** Pour $n=4$ : $2^{4}=16=4^{2}$, l'inégalité stricte est fausse.

</details>

Avis : 

---

## 80. `cqc-asymptote-oblique-elevee-0` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : asymptote oblique et position relative d'une fonction rationnelle, à la limite haute pour la série A.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}\setminus\{-1\}$ par
$$f(x)=\dfrac{2x^2-3x+4}{x+1}$$
et $(\mathcal{C})$ sa courbe représentative dans un repère. Quelle affirmation est exacte ?

- a) $(\mathcal{C})$ admet la droite d'équation $y=2x-5$ pour asymptote oblique et elle est en dessous de cette droite sur $]-1\,;+\infty[$
- b) $(\mathcal{C})$ admet la droite d'équation $y=2x-5$ pour asymptote oblique et elle est au-dessus de cette droite sur $]-1\,;+\infty[$
- c) $(\mathcal{C})$ admet la droite d'équation $y=2x-3$ pour asymptote oblique et elle est au-dessus de cette droite sur $]-1\,;+\infty[$
- d) $(\mathcal{C})$ admet la droite d'équation $y=2x-1$ pour asymptote oblique et elle est au-dessus de cette droite sur $]-1\,;+\infty[$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une fonction rationnelle dont le numérateur a un degré de plus que le dénominateur, on effectue la division euclidienne pour écrire $f(x)=ax+b+\dfrac{r}{x-c}$. Si $\dfrac{r}{x-c}$ tend vers $0$ en $\pm\infty$, la droite $y=ax+b$ est asymptote oblique ; le signe de $f(x)-(ax+b)$ donne la position de la courbe par rapport à cette droite.

### Corrigé

**Division euclidienne.** $(x+1)(2x-5)=2x^2-3x-5$, donc $2x^2-3x+4=(x+1)(2x-5)+9$ et, pour $x\neq-1$,
$$f(x)=2x-5+\dfrac{9}{x+1}.$$

**Asymptote.** $\lim\limits_{x\to\pm\infty}\dfrac{9}{x+1}=0$, donc la droite $(\Delta):\ y=2x-5$ est asymptote oblique à $(\mathcal{C})$ en $-\infty$ et en $+\infty$.

**Position.** $f(x)-(2x-5)=\dfrac{9}{x+1}$. Sur $]-1\,;+\infty[$, $x+1>0$, donc cette différence est strictement positive : $(\mathcal{C})$ est au-dessus de $(\Delta)$ sur $]-1\,;+\infty[$ (et en dessous sur $]-\infty\,;-1[$).

### Pourquoi les autres réponses sont fausses

- **a)** L'asymptote est la bonne, mais le signe de $\dfrac{9}{x+1}$ est mal lu : il est positif sur $]-1\,;+\infty[$.
- **c)** La droite $y=2x-3$ recopie les coefficients du numérateur sans effectuer la division ; $f(x)-(2x-3)=\dfrac{7-2x}{x+1}$ tend vers $-2$ et non vers $0$.
- **d)** Erreur de signe dans la division : en soustrayant $2x^2+2x$, on obtient $-3x-2x=-5x$ et non $-x$, d'où $2x-5$ et non $2x-1$.

</details>

Avis : 

---

## 81. `cqc-distance-tle-c-faible-0` (séries BAC:C BAC:D BAC:TI PROBATOIRE:C)

**Énoncé :**

Dans un repère orthonormé, on considère le point $A(-1\,;2)$ et la droite $(D)$ d'équation
$$3x-4y+5=0.$$
Quelle est la distance du point $A$ à la droite $(D)$ ?

- a) $\dfrac65$
- b) $-\dfrac65$
- c) $6$
- d) $\dfrac{6}{25}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un repère orthonormé, la distance d'un point $A(x_A\,;y_A)$ à la droite d'équation $ax+by+c=0$ est
$$d(A,(D))=\dfrac{|ax_A+by_A+c|}{\sqrt{a^2+b^2}}.$$
Une distance est toujours positive ou nulle.

### Corrigé

$$d(A,(D))=\dfrac{|3\times(-1)-4\times2+5|}{\sqrt{3^2+(-4)^2}}=\dfrac{|-3-8+5|}{\sqrt{25}}=\dfrac{|-6|}{5}=\dfrac65.$$
La distance cherchée vaut $\dfrac65=1{,}2$.

### Pourquoi les autres réponses sont fausses

- **b)** On a oublié la valeur absolue : une distance ne peut pas être négative.
- **c)** On a oublié de diviser par $\sqrt{a^2+b^2}=5$.
- **d)** On a divisé par $a^2+b^2=25$ au lieu de $\sqrt{a^2+b^2}=5$.

</details>

Avis : 

---

## 82. `cqc-derivee-seconde-moyenne-2` (séries BAC:A BAC:C BAC:D)

**Séries modifiées :** retirées BAC:A.

**Remarque du relecteur :** Convexité (signe de f'') hors programme de la série A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par
$$f(x)=x^3-6x^2+9x+1.$$
Sur quel intervalle la fonction $f$ est-elle convexe ?

- a) $]-\infty\,;2]$
- b) $[2\,;+\infty[$
- c) $]-\infty\,;1]\cup[3\,;+\infty[$
- d) $\mathbb{R}$ tout entier

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Une fonction deux fois dérivable est convexe sur un intervalle où sa dérivée seconde est positive ou nulle, et concave là où elle est négative ou nulle. Il ne faut pas confondre le signe de $f''$ (convexité) avec celui de $f'$ (sens de variation).

### Corrigé

$f'(x)=3x^2-12x+9$, puis $f''(x)=6x-12=6(x-2)$.

$f''(x)\geq0\iff x\geq2$. La fonction $f$ est donc convexe sur $[2\,;+\infty[$ (et concave sur $]-\infty\,;2]$ ; le point d'abscisse $2$ est un point d'inflexion).

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de sens : sur $]-\infty\,;2]$, $f''\leq0$ et $f$ y est concave.
- **c)** C'est l'ensemble où $f'(x)=3(x-1)(x-3)\geq0$, c'est-à-dire où $f$ est croissante : on a étudié $f'$ au lieu de $f''$.
- **d)** Un coefficient de $x^3$ positif ne rend pas la fonction convexe partout : $f''$ change de signe en $2$.

</details>

Avis : 

---

## 83. `cqc-matrice-prob-c-moyenne-2` (séries PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan vectoriel est rapporté à une base $(\vec\imath,\vec\jmath)$. L'application linéaire $f$ a pour matrice dans cette base
$$M=\begin{pmatrix}2&-1\\-4&2\end{pmatrix}.$$
Quel est l'ensemble des vecteurs $\vec u$ du plan tels que $f(\vec u)=\vec0$ ?

- a) Le seul vecteur nul $\vec0$
- b) La droite vectorielle dirigée par le vecteur de coordonnées $(2\,;-1)$
- c) La droite vectorielle dirigée par le vecteur de coordonnées $(1\,;2)$
- d) La droite vectorielle dirigée par le vecteur de coordonnées $(1\,;-2)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Le vecteur $\vec u(x\,;y)$ vérifie $f(\vec u)=\vec0$ si et seulement si $M\begin{pmatrix}x\\y\end{pmatrix}=\begin{pmatrix}0\\0\end{pmatrix}$. Si $\det M=ad-bc\neq0$, seul $\vec0$ convient ; si $\det M=0$, les deux équations du système sont proportionnelles et les solutions forment une droite vectorielle, que l'on décrit par un vecteur directeur.

### Corrigé

$\det M=2\times2-(-1)\times(-4)=4-4=0$.

Le système s'écrit
$$\begin{cases}2x-y=0\\-4x+2y=0\end{cases}$$
La seconde équation vaut $-2$ fois la première : le système se réduit à $y=2x$. Les solutions sont les vecteurs $(x\,;2x)=x(1\,;2)$, $x\in\mathbb{R}$ : c'est la droite vectorielle dirigée par le vecteur de coordonnées $(1\,;2)$.

**Contrôle** : $M\begin{pmatrix}1\\2\end{pmatrix}=\begin{pmatrix}2-2\\-4+4\end{pmatrix}=\begin{pmatrix}0\\0\end{pmatrix}$.

### Pourquoi les autres réponses sont fausses

- **a)** On a calculé le déterminant avec un signe faux ($ad+bc=4+4=8\neq0$) et conclu à tort que seul $\vec0$ convient.
- **b)** On a pris pour vecteur directeur les coefficients de la première ligne : $f(2\,;-1)=(5\,;-10)\neq\vec0$.
- **d)** Erreur de signe en résolvant $2x-y=0$ (on a écrit $y=-2x$) : $f(1\,;-2)=(4\,;-8)\neq\vec0$.

</details>

Avis : 

---

## 84. `cqc-nombres-complexes-faible-0` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI)

**Séries modifiées :** retirées BAC:A.

**Remarque du relecteur :** Nombres complexes hors programme de la série A (BAC:A listé).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Quel est le module du nombre complexe
$$z=\dfrac{3+4i}{1-i}\ ?$$

- a) $\dfrac52$
- b) $5$
- c) $\dfrac{5\sqrt2}{2}$
- d) $5\sqrt2$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Le module d'un quotient est le quotient des modules : $\left|\dfrac{z_1}{z_2}\right|=\dfrac{|z_1|}{|z_2|}$. Le module de $a+ib$ vaut $\sqrt{a^2+b^2}$ ; il ne faut pas oublier la racine carrée. Il est inutile de mettre $z$ sous forme algébrique.

### Corrigé

$|3+4i|=\sqrt{9+16}=5$ et $|1-i|=\sqrt{1^2+(-1)^2}=\sqrt2$, donc
$$|z|=\dfrac{5}{\sqrt2}=\dfrac{5\sqrt2}{2}.$$

**Contrôle** : $z=\dfrac{(3+4i)(1+i)}{2}=\dfrac{-1+7i}{2}$ et $|z|=\dfrac{\sqrt{1+49}}{2}=\dfrac{\sqrt{50}}{2}=\dfrac{5\sqrt2}{2}$.

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié la racine carrée dans le module du dénominateur : $|1-i|=\sqrt2$, et non $2$.
- **b)** On n'a pris que le module du numérateur, sans diviser par $|1-i|$.
- **d)** On a multiplié les modules au lieu de les diviser.

</details>

Avis : 

---

## 85. `cqc-pourcentage-prob-d-faible-0` (séries PROBATOIRE:A PROBATOIRE:D)

**Énoncé :**

Après une augmentation de $15\ \%$, le prix d'un sac est de $34\,500$ F.

Quel était le prix de ce sac avant l'augmentation ?

- a) $29\,325$ F
- b) $39\,675$ F
- c) $23\,000$ F
- d) $30\,000$ F

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Augmenter un prix de $t\ \%$ revient à le multiplier par le coefficient $1+\dfrac{t}{100}$. Pour retrouver le prix de départ, on divise le nouveau prix par ce coefficient. Retirer $t\ \%$ du nouveau prix ne redonne pas le prix de départ, car le pourcentage portait sur l'ancien prix.

### Corrigé

Si $P$ est le prix de départ : $P\times1{,}15=34\,500$, donc
$$P=\dfrac{34\,500}{1{,}15}=30\,000 \text{ F}.$$

**Contrôle** : $30\,000\times1{,}15=34\,500$.

### Pourquoi les autres réponses sont fausses

- **a)** $34\,500\times0{,}85=29\,325$ : on a retiré $15\ \%$ du nouveau prix, alors que l'augmentation portait sur l'ancien prix.
- **b)** $34\,500\times1{,}15=39\,675$ : on a appliqué une seconde fois l'augmentation au lieu de l'annuler.
- **c)** $34\,500\div1{,}5=23\,000$ : on a confondu le coefficient $1{,}15$ avec $1{,}5$.

</details>

Avis : 

---

## 86. `cqc-graphes-tle-d-faible-0` (séries BAC:D BAC:TI)

**Remarque du relecteur :** LIMITE : théorie des graphes, à confirmer au programme BAC D.

**Énoncé :**

Parmi les listes suivantes, laquelle peut être la liste des degrés des sommets d'un graphe simple non orienté à $5$ sommets ?

- a) $3\,;3\,;2\,;2\,;1$
- b) $4\,;4\,;4\,;1\,;1$
- c) $2\,;2\,;2\,;2\,;2$
- d) $5\,;3\,;2\,;2\,;2$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un graphe simple (sans boucle ni arête multiple) à $n$ sommets, chaque sommet a un degré au plus égal à $n-1$, et la somme des degrés est égale au double du nombre d'arêtes, donc paire. Ces deux conditions ne suffisent pas toujours : il faut aussi vérifier que les arêtes demandées par les sommets de grand degré sont compatibles avec les petits degrés.

### Corrigé

- $3\,;3\,;2\,;2\,;1$ : la somme vaut $11$, nombre impair. Or la somme des degrés vaut le double du nombre d'arêtes : impossible.
- $5\,;3\,;2\,;2\,;2$ : avec $5$ sommets, un sommet est relié au plus aux $4$ autres, donc un degré $5$ est impossible dans un graphe simple.
- $4\,;4\,;4\,;1\,;1$ : la somme vaut $14$, paire, mais chacun des trois sommets de degré $4$ est relié à tous les autres sommets ; les deux derniers sommets ont alors au moins $3$ voisins, et non $1$ : impossible.
- $2\,;2\,;2\,;2\,;2$ : la somme vaut $10$, soit $5$ arêtes, et le cycle $A-B-C-D-E-A$ réalise exactement ces degrés.

La seule liste possible est donc $2\,;2\,;2\,;2\,;2$.

### Pourquoi les autres réponses sont fausses

- **a)** La somme des degrés, $11$, est impaire, alors qu'elle doit être le double du nombre d'arêtes.
- **b)** La somme est bien paire, mais trois sommets reliés à tous les autres imposent un degré au moins $3$ aux deux derniers sommets.
- **d)** Un sommet d'un graphe simple à $5$ sommets a au plus $4$ voisins : le degré $5$ est impossible.

</details>

Avis : 

---

## 87. `cqc-asymptote-oblique-moyenne-0` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}\setminus\{-1\}$ par
$$f(x)=\dfrac{x^2+3x-2}{x+1}.$$
Quelle est l'équation de l'asymptote oblique à la courbe de $f$ en $+\infty$ ?

- a) $y=x+3$
- b) $y=x+2$
- c) $y=x$
- d) $x=-1$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une fonction rationnelle dont le numérateur a un degré de plus que le dénominateur, on écrit $f(x)=ax+b+\dfrac{c}{x+d}$ (division euclidienne ou identification). Comme $\dfrac{c}{x+d}$ tend vers $0$ en $+\infty$, la droite $y=ax+b$ est asymptote oblique.

### Corrigé

On cherche $a$, $b$, $c$ tels que $x^2+3x-2=(x+1)(ax+b)+c$. En développant : $(x+1)(ax+b)+c=ax^2+(a+b)x+b+c$. Par identification : $a=1$, $a+b=3$ donc $b=2$, et $b+c=-2$ donc $c=-4$.
$$f(x)=x+2-\dfrac{4}{x+1}.$$
Alors $f(x)-(x+2)=-\dfrac{4}{x+1}$ tend vers $0$ quand $x$ tend vers $+\infty$ : la droite d'équation $y=x+2$ est asymptote oblique à la courbe en $+\infty$.

### Pourquoi les autres réponses sont fausses

- **a)** On a recopié le coefficient $3$ du numérateur sans tenir compte du $+1$ du dénominateur ; la division donne $x+2$.
- **c)** On n'a gardé que le quotient des termes de plus haut degré $\dfrac{x^2}{x}$ ; or $f(x)-x$ tend vers $2$ et non vers $0$.
- **d)** La droite $x=-1$ est une asymptote verticale (valeur interdite), pas l'asymptote oblique.

</details>

Avis : 

---

## 88. `cqc-derivee-moyenne-2` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PROBATOIRE:A)

**Remarque du relecteur :** LIMITE : tangente pour Probatoire A.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=x^2-4x+1$. Quelle est l'équation de la tangente à la courbe de $f$ au point d'abscisse $3$ ?

- a) $y=2x+4$
- b) $y=2x-8$
- c) $y=-2x+8$
- d) $y=2x-6$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La tangente à la courbe de $f$ au point d'abscisse $x_0$ a pour équation $y=f'(x_0)(x-x_0)+f(x_0)$ : il faut calculer à la fois le nombre dérivé $f'(x_0)$ (coefficient directeur) et l'image $f(x_0)$.

### Corrigé

$f'(x)=2x-4$, donc $f'(3)=2$. De plus $f(3)=9-12+1=-2$.
$$y=2(x-3)+(-2)=2x-8.$$
Contrôle : pour $x=3$, $y=6-8=-2=f(3)$, le point de contact est bien sur la droite.

### Pourquoi les autres réponses sont fausses

- **a)** On a écrit $2(x+3)-2$ : erreur de signe dans $x-x_0$.
- **c)** On a échangé les rôles de $f(3)$ et $f'(3)$ en prenant $-2$ comme coefficient directeur.
- **d)** On a oublié d'ajouter $f(3)=-2$ : la droite obtenue ne passe pas par le point de contact.

</details>

Avis : 

---

## 89. `cqc-ellipse-elevee-0` (séries BAC:C BAC:D BAC:E)

**Séries modifiées :** retirées BAC:D.

**Remarque du relecteur :** LIMITE : coniques en série D, à vérifier au programme.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, on considère la courbe $(\Gamma)$ d'équation
$$25x^2+16y^2-100x-300=0.$$
On admet que $(\Gamma)$ est une ellipse. Quels sont ses foyers ?

- a) $F(2\,;3)$ et $F'(2\,;-3)$
- b) $F(5\,;0)$ et $F'(-1\,;0)$
- c) $F(2\,;5)$ et $F'(2\,;-5)$
- d) $F(0\,;3)$ et $F'(0\,;-3)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On met l'équation sous forme réduite $\dfrac{(x-x_0)^2}{\alpha^2}+\dfrac{(y-y_0)^2}{\beta^2}=1$ en complétant le carré. Le grand axe est porté par la direction du plus grand dénominateur ; si $a$ et $b$ désignent le demi-grand axe et le demi-petit axe, $c=\sqrt{a^2-b^2}$ et les foyers sont sur le grand axe, à la distance $c$ du centre.

### Corrigé

$$25(x^2-4x)+16y^2=300\iff25(x-2)^2-100+16y^2=300\iff25(x-2)^2+16y^2=400.$$
En divisant par $400$ :
$$\dfrac{(x-2)^2}{16}+\dfrac{y^2}{25}=1.$$
Le centre est $\Omega(2\,;0)$. Le plus grand dénominateur ($25$) est sous $y^2$ : le grand axe est vertical, $a=5$, $b=4$, $c=\sqrt{25-16}=3$.

Les foyers sont sur la droite $x=2$, à la distance $3$ de $\Omega$ : $F(2\,;3)$ et $F'(2\,;-3)$.

Contrôle : le point $(6\,;0)$ de $(\Gamma)$ est à la distance $5$ de chaque foyer, et $5+5=10=2a$.

### Pourquoi les autres réponses sont fausses

- **b)** On a placé les foyers sur l'axe horizontal, sans voir que le plus grand dénominateur est sous $y^2$.
- **c)** Ce sont les sommets du grand axe (distance $a=5$ du centre), pas les foyers (distance $c=3$).
- **d)** On a oublié la translation : le centre est $\Omega(2\,;0)$ et non l'origine.

</details>

Avis : 

---

## 90. `cqc-matrice-prob-c-moyenne-3` (séries PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On donne les matrices $A=\begin{pmatrix}2&1\\-1&3\end{pmatrix}$ et $B=\begin{pmatrix}1&0\\2&-1\end{pmatrix}$. Quelle est la matrice produit $AB$ ?

- a) $\begin{pmatrix}2&0\\-2&-3\end{pmatrix}$
- b) $\begin{pmatrix}2&1\\5&-1\end{pmatrix}$
- c) $\begin{pmatrix}4&5\\-1&-3\end{pmatrix}$
- d) $\begin{pmatrix}4&-1\\5&-3\end{pmatrix}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Le coefficient de la ligne $i$ et de la colonne $j$ de $AB$ s'obtient en multipliant la ligne $i$ de $A$ par la colonne $j$ de $B$ (somme des produits terme à terme). Le produit n'est pas commutatif : $AB$ et $BA$ sont en général différents.

### Corrigé

- Ligne $1$ de $A$, colonnes de $B$ : $2\times1+1\times2=4$ et $2\times0+1\times(-1)=-1$.
- Ligne $2$ de $A$, colonnes de $B$ : $-1\times1+3\times2=5$ et $-1\times0+3\times(-1)=-3$.
$$AB=\begin{pmatrix}4&-1\\5&-3\end{pmatrix}.$$

### Pourquoi les autres réponses sont fausses

- **a)** On a multiplié les coefficients de même position, ce qui n'est pas le produit matriciel.
- **b)** C'est le produit $BA$ : l'ordre des facteurs a été inversé.
- **c)** On a rangé les résultats colonne par ligne : c'est la transposée de $AB$.

</details>

Avis : 

---

## 91. `cqc-noyau-elevee-0` (séries BAC:C BAC:E PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan vectoriel est muni d'une base $(\vec{e_1},\vec{e_2})$. Pour un réel $m$, on considère l'endomorphisme $f$ défini par
$$f(\vec{e_1})=2\vec{e_1}+m\,\vec{e_2}\qquad\text{et}\qquad f(\vec{e_2})=3\vec{e_1}+6\vec{e_2}.$$
Pour quelle valeur de $m$ le noyau de $f$ n'est-il pas réduit à $\{\vec0\}$, et quel est alors ce noyau ?

- a) $m=4$ et $\operatorname{Ker}f=\operatorname{Vect}(\vec{e_1}+2\vec{e_2})$
- b) $m=9$ et $\operatorname{Ker}f=\operatorname{Vect}(3\vec{e_1}-2\vec{e_2})$
- c) $m=4$ et $\operatorname{Ker}f=\operatorname{Vect}(3\vec{e_1}-2\vec{e_2})$
- d) $m=-4$ et $\operatorname{Ker}f=\operatorname{Vect}(3\vec{e_1}+2\vec{e_2})$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On écrit $f(x\vec{e_1}+y\vec{e_2})$ en coordonnées. Le noyau est l'ensemble des solutions du système homogène obtenu ; il n'est pas réduit à $\{\vec0\}$ exactement lorsque le déterminant du système est nul. On résout alors le système pour obtenir une base du noyau, sans le confondre avec l'image.

### Corrigé

$f(x\vec{e_1}+y\vec{e_2})=(2x+3y)\vec{e_1}+(mx+6y)\vec{e_2}$. Le noyau est l'ensemble des solutions de
$$\begin{cases}2x+3y=0\\mx+6y=0\end{cases}$$
de déterminant $2\times6-3m=12-3m$. Il est nul pour $m=4$.

Pour $m=4$, la seconde équation est le double de la première ; il reste $2x+3y=0$, vérifiée par $x=3$, $y=-2$. Donc $\operatorname{Ker}f=\operatorname{Vect}(3\vec{e_1}-2\vec{e_2})$.

Contrôle : $f(3\vec{e_1}-2\vec{e_2})=3(2\vec{e_1}+4\vec{e_2})-2(3\vec{e_1}+6\vec{e_2})=\vec0$.

### Pourquoi les autres réponses sont fausses

- **a)** $\vec{e_1}+2\vec{e_2}$ dirige l'image de $f$ (colinéaire à $f(\vec{e_1})=2\vec{e_1}+4\vec{e_2}$), pas son noyau.
- **b)** Déterminant mal calculé ($2m-3\times6$) ; pour $m=9$, $f(3\vec{e_1}-2\vec{e_2})=15\vec{e_2}\neq\vec0$.
- **d)** Erreur de signe dans le déterminant ; pour $m=-4$, le déterminant vaut $24\neq0$ et le noyau est réduit à $\{\vec0\}$.

</details>

Avis : 

---

## 92. `cqc-parallelisme-faible-0` (séries BEPC:)

**Énoncé :**

$ABC$ est un triangle. Le point $M$ appartient au segment $[AB]$ et le point $N$ au segment $[AC]$, avec $AM=3$ cm, $AB=7{,}5$ cm, $AN=2$ cm et $AC=5$ cm. Que peut-on dire des droites $(MN)$ et $(BC)$ ?

- a) Elles ne sont pas parallèles, car $\dfrac{AM}{MB}=\dfrac23$ est différent de $\dfrac{AN}{AC}=\dfrac25$.
- b) Elles sont parallèles, car $\dfrac{AM}{AB}=\dfrac{AN}{AC}=0{,}4$.
- c) Elles ne sont pas parallèles, car $AM\neq AN$.
- d) On ne peut pas conclure sans connaître les longueurs $MN$ et $BC$.

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Réciproque du théorème de Thalès : si $A$, $M$, $B$ d'une part et $A$, $N$, $C$ d'autre part sont alignés dans le même ordre, et si $\dfrac{AM}{AB}=\dfrac{AN}{AC}$, alors $(MN)$ et $(BC)$ sont parallèles. Il faut comparer des rapports formés de la même façon (petit segment sur grand segment, tous deux issus de $A$).

### Corrigé

Les points $A$, $M$, $B$ et $A$, $N$, $C$ sont alignés dans le même ordre ($M\in[AB]$, $N\in[AC]$).
$$\dfrac{AM}{AB}=\dfrac{3}{7{,}5}=0{,}4\qquad\text{et}\qquad\dfrac{AN}{AC}=\dfrac25=0{,}4.$$
Les rapports sont égaux : d'après la réciproque du théorème de Thalès, $(MN)$ et $(BC)$ sont parallèles.

### Pourquoi les autres réponses sont fausses

- **a)** On a comparé deux rapports de nature différente ($\dfrac{AM}{MB}$ et $\dfrac{AN}{AC}$) : il faut comparer $\dfrac{AM}{AB}$ et $\dfrac{AN}{AC}$.
- **c)** Le parallélisme ne demande pas des longueurs égales mais des rapports égaux.
- **d)** La réciproque du théorème de Thalès n'utilise que les longueurs sur les deux côtés issus de $A$.

</details>

Avis : 

---

## 93. `cqc-primitives-usuelles-elevee-5` (séries BAC:A BAC:C)

**Remarque du relecteur :** LIMITE : pour la série A, primitive de u'/u avec changement de signe du dénominateur, à la limite haute.

**Énoncé :**

Soit $f$ la fonction définie sur l'intervalle $\left]\dfrac12\,;+\infty\right[$ par
$$f(x)=3x^2+e^x-\dfrac{4}{1-2x}.$$
Laquelle des fonctions suivantes est une primitive de $f$ sur cet intervalle ?

- a) $F(x)=x^3+e^x-2\ln(2x-1)$
- b) $F(x)=x^3+e^x+2\ln(2x-1)$
- c) $F(x)=x^3+e^x+2\ln(1-2x)$
- d) $F(x)=x^3+e^x+8\ln(2x-1)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On primitive terme à terme. Pour un terme $\dfrac{k}{ax+b}$, une primitive est $\dfrac ka\ln|ax+b|$ ; on retire la valeur absolue en tenant compte du signe de $ax+b$ sur l'intervalle donné. On vérifie en dérivant.

### Corrigé

- Une primitive de $3x^2$ est $x^3$ ; une primitive de $e^x$ est $e^x$.
- Pour $-\dfrac{4}{1-2x}$ : $k=-4$, $a=-2$, donc une primitive est $\dfrac{-4}{-2}\ln|1-2x|=2\ln|1-2x|$. Sur $\left]\dfrac12\,;+\infty\right[$, $1-2x<0$, donc $|1-2x|=2x-1$.

Une primitive de $f$ est donc $F(x)=x^3+e^x+2\ln(2x-1)$.

Vérification : $F'(x)=3x^2+e^x+\dfrac{4}{2x-1}=3x^2+e^x-\dfrac{4}{1-2x}=f(x)$.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur le quotient $\dfrac{k}{a}=\dfrac{-4}{-2}=2$ ; la dérivée donne $-\dfrac{4}{2x-1}$, soit $+\dfrac{4}{1-2x}$.
- **c)** Sur $\left]\dfrac12\,;+\infty\right[$, $1-2x<0$ : $\ln(1-2x)$ n'y est pas défini.
- **d)** On a multiplié par le coefficient $a$ au lieu de diviser : $(-4)\times(-2)=8$.

</details>

Avis : 

---

## 94. `cqc-theoreme-du-rang-tle-c-faible-0` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : suppose connu le théorème du rang et la notation rg.

**Énoncé :**

Soit $f:\mathbb{R}^3\to\mathbb{R}^2$ une application linéaire dont le noyau est une droite vectorielle. Que peut-on affirmer ?

- a) $\operatorname{rg}f=2$ et $f$ est surjective.
- b) $\operatorname{rg}f=1$ et $f$ n'est pas surjective.
- c) $\operatorname{rg}f=2$ et $f$ est bijective.
- d) $\operatorname{rg}f=2$ mais $f$ n'est pas surjective, car son noyau n'est pas réduit à $\{\vec0\}$.

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Théorème du rang : pour une application linéaire $f:E\to F$ avec $E$ de dimension finie, $\dim E=\dim\operatorname{Ker}f+\operatorname{rg}f$. L'application $f$ est surjective si et seulement si $\operatorname{rg}f=\dim F$, et injective si et seulement si $\operatorname{Ker}f=\{\vec0\}$ : un noyau non nul empêche l'injectivité, pas la surjectivité.

### Corrigé

Le noyau est une droite, donc $\dim\operatorname{Ker}f=1$. Par le théorème du rang :
$$\operatorname{rg}f=\dim\mathbb{R}^3-\dim\operatorname{Ker}f=3-1=2.$$
Comme $\dim\mathbb{R}^2=2$, l'image de $f$ est $\mathbb{R}^2$ tout entier : $f$ est surjective (mais pas injective).

### Pourquoi les autres réponses sont fausses

- **b)** On a calculé $\dim\mathbb{R}^2-\dim\operatorname{Ker}f$ ; le théorème du rang porte sur la dimension de l'espace de départ, $3$.
- **c)** Le noyau n'est pas réduit à $\{\vec0\}$ : $f$ n'est pas injective, donc pas bijective.
- **d)** Un noyau non nul empêche l'injectivité, pas la surjectivité : le rang $2$ égale la dimension de l'espace d'arrivée.

</details>

Avis : 

---

## 95. `cqc-asymptote-oblique-moyenne-1` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}\setminus\{-1\}$ par $f(x)=\dfrac{2x^2+3x-1}{x+1}$.

Quelle droite est asymptote oblique à la courbe représentative de $f$ en $+\infty$ ?

- a) $y=2x+1$
- b) $y=2x$
- c) $y=2x+3$
- d) $y=2x-2$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour trouver l'asymptote oblique d'une fonction rationnelle dont le numérateur a un degré de plus que le dénominateur, on écrit $f(x)=ax+b+\dfrac{c}{x+1}$ (division euclidienne ou identification). Comme $\dfrac{c}{x+1}\to0$ en $+\infty$, la droite $y=ax+b$ est asymptote oblique.

### Corrigé

On cherche $a$, $b$, $c$ tels que $2x^2+3x-1=(x+1)(ax+b)+c$. En développant : $ax^2+(a+b)x+b+c$. Par identification : $a=2$, $a+b=3$ donc $b=1$, $b+c=-1$ donc $c=-2$.

Ainsi $f(x)=2x+1-\dfrac{2}{x+1}$, et $f(x)-(2x+1)=-\dfrac{2}{x+1}\to0$ quand $x\to+\infty$.

La droite d'équation $y=2x+1$ est asymptote oblique en $+\infty$.

### Pourquoi les autres réponses sont fausses

- **b)** $y=2x$ : on n'a gardé que le quotient des termes de plus haut degré ; $f(x)-2x$ tend vers $1$, pas vers $0$.
- **c)** $y=2x+3$ : on a divisé $2x^2+3x$ par $x$ en oubliant le $+1$ du dénominateur ; $f(x)-(2x+3)$ tend vers $-2$.
- **d)** $y=2x-2$ : on a pris le reste $c=-2$ pour l'ordonnée à l'origine ; $f(x)-(2x-2)$ tend vers $3$.

</details>

Avis : 

---

## 96. `cqc-ellipse-faible-0` (séries BAC:C BAC:D BAC:E)

**Séries modifiées :** retirées BAC:D.

**Remarque du relecteur :** Les coniques (ellipse, foyers) sont au programme de Terminale C et E, pas de Terminale D : à retirer de BAC:D.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans le plan muni d'un repère orthonormé, on considère l'ellipse $(E)$ d'équation $\dfrac{x^2}{25}+\dfrac{y^2}{9}=1$.

Quels sont les foyers de $(E)$ ?

- a) $(-\sqrt{34}\,;\,0)$ et $(\sqrt{34}\,;\,0)$
- b) $(0\,;\,-4)$ et $(0\,;\,4)$
- c) $(-5\,;\,0)$ et $(5\,;\,0)$
- d) $(-4\,;\,0)$ et $(4\,;\,0)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour l'ellipse $\dfrac{x^2}{a^2}+\dfrac{y^2}{b^2}=1$ avec $a>b>0$, le grand axe est porté par $(Ox)$, et les foyers sont $F(c\,;\,0)$ et $F'(-c\,;\,0)$ avec $c^2=a^2-b^2$.

### Corrigé

$a^2=25$ et $b^2=9$, donc $a=5>b=3$ : le grand axe est sur $(Ox)$.

$c^2=a^2-b^2=25-9=16$, donc $c=4$.

Les foyers sont $(-4\,;\,0)$ et $(4\,;\,0)$.

### Pourquoi les autres réponses sont fausses

- **a)** $\pm\sqrt{34}$ : on a utilisé $c^2=a^2+b^2$, relation propre à l'hyperbole.
- **b)** Foyers sur $(Oy)$ : le grand axe est porté par l'axe où le dénominateur est le plus grand, ici $(Ox)$.
- **c)** $(\pm5\,;\,0)$ : ce sont les sommets du grand axe, pas les foyers.

</details>

Avis : 

---

## 97. `cqc-linearite-elevee-5` (séries PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ un endomorphisme de $\mathbb{R}^2$ tel que $f(1\,;\,2)=(5\,;\,1)$ et $f(0\,;\,1)=(2\,;\,-1)$.

Quelle est l'expression de $f(x,y)$ pour tout $(x,y)\in\mathbb{R}^2$ ?

- a) $f(x,y)=(5x+2y,\;x-y)$
- b) $f(x,y)=(9x+2y,\;-x-y)$
- c) $f(x,y)=(x+3y,\;2x-y)$
- d) $f(x,y)=(x+2y,\;3x-y)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Une application linéaire est entièrement déterminée par les images des vecteurs d'une base. On exprime les vecteurs de la base canonique à l'aide des vecteurs dont on connaît l'image, puis on applique la linéarité : $f(x,y)=x\,f(1\,;\,0)+y\,f(0\,;\,1)$.

### Corrigé

$(1\,;\,0)=(1\,;\,2)-2(0\,;\,1)$, donc par linéarité :
$$f(1,0)=f(1,2)-2f(0,1)=(5,1)-2(2,-1)=(1,3).$$
Avec $f(0\,;\,1)=(2\,;\,-1)$ :
$$f(x,y)=x(1,3)+y(2,-1)=(x+2y,\;3x-y).$$
Vérification : $f(1\,;\,2)=(1+4,\;3-2)=(5\,;\,1)$ et $f(0\,;\,1)=(2\,;\,-1)$.

### Pourquoi les autres réponses sont fausses

- **a)** On a pris $f(1\,;\,2)$ pour $f(1\,;\,0)$, alors que $(1\,;\,2)$ n'est pas un vecteur de la base canonique.
- **b)** On a écrit $(1\,;\,0)=(1\,;\,2)+2(0\,;\,1)$ (erreur de signe), d'où $f(1\,;\,0)=(9\,;\,-1)$.
- **c)** On a placé les images des vecteurs de base en lignes au lieu de colonnes : $f(1\,;\,2)$ donnerait $(7\,;\,0)$.

</details>

Avis : 

---

## 98. `cqc-matrice-prob-c-moyenne-4` (séries PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On considère la matrice $A=\begin{pmatrix}2&1\\0&2\end{pmatrix}$.

Quelle est la matrice $A^3$ ?

- a) $\begin{pmatrix}8&12\\0&8\end{pmatrix}$
- b) $\begin{pmatrix}8&1\\0&8\end{pmatrix}$
- c) $\begin{pmatrix}8&8\\0&8\end{pmatrix}$
- d) $\begin{pmatrix}8&6\\0&8\end{pmatrix}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

La puissance d'une matrice se calcule par produits successifs : $A^2=A\times A$, puis $A^3=A^2\times A$, chaque coefficient étant obtenu par le produit « ligne par colonne ». On ne peut pas élever chaque coefficient à la puissance.

### Corrigé

$$A^2=\begin{pmatrix}2&1\\0&2\end{pmatrix}\begin{pmatrix}2&1\\0&2\end{pmatrix}=\begin{pmatrix}4&2+2\\0&4\end{pmatrix}=\begin{pmatrix}4&4\\0&4\end{pmatrix}$$
$$A^3=A^2\times A=\begin{pmatrix}4&4\\0&4\end{pmatrix}\begin{pmatrix}2&1\\0&2\end{pmatrix}=\begin{pmatrix}8&4+8\\0&8\end{pmatrix}=\begin{pmatrix}8&12\\0&8\end{pmatrix}$$

### Pourquoi les autres réponses sont fausses

- **b)** On a élevé chaque coefficient au cube, ce qui n'est pas le produit matriciel.
- **c)** On a calculé $A^3=2A^2$ comme si $A$ était égale à $2I$, en oubliant le coefficient $1$.
- **d)** Erreur dans le coefficient en haut à droite : $3\times2\times1=6$ au lieu de $3\times2^2\times1=12$.

</details>

Avis : 

---

## 99. `cqc-noyau-faible-0` (séries BAC:C BAC:E PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Remarque du relecteur :** LIMITE : endomorphisme et noyau pour le Probatoire C/E, à vérifier au programme de 1re.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $r$ l'endomorphisme de $\mathbb{R}^2$ défini par $r(x,y)=(x-2y,\;-3x+6y)$.

Quel est le noyau de $r$ ?

- a) $\{(0\,;\,0)\}$
- b) $\operatorname{Vect}\big((2\,;\,1)\big)$
- c) $\operatorname{Vect}\big((1\,;\,2)\big)$
- d) $\operatorname{Vect}\big((1\,;\,-3)\big)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Le noyau de $r$ est l'ensemble des vecteurs $(x,y)$ tels que $r(x,y)=(0\,;\,0)$. On résout le système linéaire homogène obtenu, puis on donne un vecteur directeur de l'ensemble des solutions.

### Corrigé

$r(x,y)=(0\,;\,0)\iff\begin{cases}x-2y=0\\-3x+6y=0\end{cases}$

La seconde équation est $-3$ fois la première : le système équivaut à $x=2y$.

Les solutions sont les $(2y,\,y)=y(2\,;\,1)$ avec $y\in\mathbb{R}$ : le noyau est $\operatorname{Vect}\big((2\,;\,1)\big)$.

Vérification : $r(2\,;\,1)=(2-2,\;-6+6)=(0\,;\,0)$.

### Pourquoi les autres réponses sont fausses

- **a)** $\{(0\,;\,0)\}$ : les deux équations sont proportionnelles, le système a une infinité de solutions ; $r$ n'est pas injectif.
- **c)** $(1\,;\,2)$ : on a inversé les rôles de $x$ et $y$ ; $r(1\,;\,2)=(-3\,;\,9)\neq(0\,;\,0)$.
- **d)** $(1\,;\,-3)$ : c'est $r(1\,;\,0)$, qui dirige l'image de $r$, pas son noyau.

</details>

Avis : 

---

## 100. `cqc-projete-orthogonal-prob-c-moyenne-4` (séries PROBATOIRE:C PROBATOIRE:E)

**Énoncé :**

Dans le plan muni d'un repère orthonormé d'origine $O$, on considère la droite $(D)$ passant par $O$ et de vecteur directeur $\vec u(1\,;\,2)$, et le point $A(4\,;\,3)$.

Quelles sont les coordonnées du projeté orthogonal $H$ de $A$ sur $(D)$ ?

- a) $(10\,;\,20)$
- b) $(2\sqrt5\,;\,4\sqrt5)$
- c) $\left(\dfrac{11}{5}\,;\,\dfrac{22}{5}\right)$
- d) $(2\,;\,4)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Le projeté orthogonal $H$ de $A$ sur la droite passant par $O$ et dirigée par $\vec u$ s'écrit $\overrightarrow{OH}=k\,\vec u$, avec $k=\dfrac{\overrightarrow{OA}\cdot\vec u}{\|\vec u\|^2}$ ; cette valeur traduit la condition $\overrightarrow{AH}\cdot\vec u=0$.

### Corrigé

$\overrightarrow{OA}\cdot\vec u=4\times1+3\times2=10$ et $\|\vec u\|^2=1^2+2^2=5$, donc $k=\dfrac{10}{5}=2$.

$\overrightarrow{OH}=2\vec u$, d'où $H(2\,;\,4)$.

Vérification : $\overrightarrow{AH}(-2\,;\,1)$ et $\overrightarrow{AH}\cdot\vec u=-2+2=0$.

### Pourquoi les autres réponses sont fausses

- **a)** On a pris $k=\overrightarrow{OA}\cdot\vec u=10$ en oubliant de diviser par $\|\vec u\|^2$.
- **b)** On a divisé par $\|\vec u\|=\sqrt5$ au lieu de $\|\vec u\|^2=5$.
- **c)** On a croisé les coordonnées dans le produit scalaire : $4\times2+3\times1=11$ au lieu de $10$.

</details>

Avis : 

---

## 101. `cqc-asymptotes-faible-1` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Énoncé :**

On considère la fonction $g$ définie sur $\mathbb{R}\setminus\{-3\}$ par $g(x)=\dfrac{2x-1}{x+3}$.

Quelles sont les asymptotes à la courbe représentative de $g$ ?

- a) $x=3$ et $y=2$
- b) $x=-3$ et $y=-\dfrac13$
- c) $y=2$ seulement
- d) $x=-3$ et $y=2$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Si $\lim\limits_{x\to a}g(x)=\pm\infty$ (en général en une valeur interdite $a$), la droite $x=a$ est asymptote verticale. Si $\lim\limits_{x\to\pm\infty}g(x)=\ell$ (fini), la droite $y=\ell$ est asymptote horizontale. Pour un quotient de deux fonctions affines, la limite à l'infini est le quotient des coefficients de $x$.

### Corrigé

**En $\pm\infty$ :** $g(x)=\dfrac{x\left(2-\frac1x\right)}{x\left(1+\frac3x\right)}=\dfrac{2-\frac1x}{1+\frac3x}\to\dfrac21=2$. La droite $y=2$ est asymptote horizontale en $-\infty$ et en $+\infty$.

**En $-3$ :** le numérateur tend vers $2\times(-3)-1=-7\neq0$ et le dénominateur tend vers $0$, donc $|g(x)|\to+\infty$. La droite $x=-3$ est asymptote verticale.

Les asymptotes sont les droites d'équations $x=-3$ et $y=2$.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur la valeur interdite : $x+3=0$ donne $x=-3$, pas $x=3$.
- **b)** On a fait le quotient des termes constants $\dfrac{-1}{3}$ au lieu du quotient des coefficients de $x$.
- **c)** On a oublié l'asymptote verticale en la valeur interdite $-3$.

</details>

Avis : 

---

## 102. `cqc-ellipse-faible-1` (séries BAC:C BAC:D BAC:E)

**Séries modifiées :** retirées BAC:D.

**Remarque du relecteur :** LIMITE : coniques (ellipse, excentricité), à confirmer au programme BAC D.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, une ellipse de centre $O$ a pour foyers $F(3\,;0)$ et $F'(-3\,;0)$, et elle passe par le point $B(0\,;4)$.

Quelle est son excentricité ?

- a) $\dfrac34$
- b) $\dfrac35$
- c) $\dfrac45$
- d) $\dfrac{3\sqrt7}{7}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une ellipse de centre $O$ dont les foyers sont sur l'axe des abscisses, on note $a$ le demi-grand axe, $b$ le demi-petit axe et $c$ la distance du centre à un foyer : $a^2=b^2+c^2$ et l'excentricité vaut $e=\dfrac ca$ (avec $0<e<1$). Un point de l'ellipse situé sur l'axe des ordonnées est un sommet du petit axe, donc il donne $b$.

### Corrigé

Les foyers donnent $c=3$. Le point $B(0\,;4)$ est un sommet du petit axe, donc $b=4$.

$a^2=b^2+c^2=16+9=25$, donc $a=5$.

$e=\dfrac ca=\dfrac35$.

### Pourquoi les autres réponses sont fausses

- **a)** On a divisé $c$ par $b$ au lieu de diviser par $a$.
- **c)** On a calculé $\dfrac ba$ au lieu de $\dfrac ca$.
- **d)** On a écrit $a^2=b^2-c^2=7$, d'où $a=\sqrt7$ et $e=\dfrac{3}{\sqrt7}$, valeur supérieure à $1$, impossible pour une ellipse.

</details>

Avis : 

---

## 103. `cqc-linearite-faible-0` (séries PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Remarque du relecteur :** LIMITE : application linéaire de R^2 au Probatoire C/E, à vérifier au programme de 1re.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ une application linéaire de $\mathbb{R}^2$ dans $\mathbb{R}^2$ telle que $f(1\,;0)=(2\,;-1)$ et $f(0\,;1)=(3\,;4)$.

Quelle est l'image par $f$ du vecteur $(-2\,;5)$ ?

- a) $(11\,;22)$
- b) $(4\,;-13)$
- c) $(11\,;18)$
- d) $(-4\,;20)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On écrit le vecteur comme combinaison des vecteurs dont on connaît l'image, puis on utilise la linéarité : $f(\lambda u+\mu v)=\lambda f(u)+\mu f(v)$.

### Corrigé

$(-2\,;5)=-2(1\,;0)+5(0\,;1)$, donc
$$f(-2\,;5)=-2f(1\,;0)+5f(0\,;1)=-2(2\,;-1)+5(3\,;4)=(-4+15\,;2+20)=(11\,;22).$$

### Pourquoi les autres réponses sont fausses

- **b)** On a échangé les rôles des deux images : $-2f(0\,;1)+5f(1\,;0)$.
- **c)** Erreur de signe : $-2\times(-1)$ a été compté $-2$ au lieu de $+2$.
- **d)** On a multiplié composante par composante ($-2\times2$ et $5\times4$) au lieu d'utiliser la linéarité.

</details>

Avis : 

---

## 104. `cqc-matrice-d-un-endomorphisme-tle-c-elevee-5` (séries BAC:C BAC:E PROBATOIRE:C)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ un endomorphisme de $\mathbb{R}^2$ et $(\vec\imath,\vec\jmath)$ la base canonique. On sait que $f(\vec\imath+\vec\jmath)=(4\,;1)$ et $f(\vec\imath-\vec\jmath)=(2\,;-3)$.

Quelle est la matrice de $f$ dans la base $(\vec\imath,\vec\jmath)$ ?

- a) $\begin{pmatrix}3&-1\\1&2\end{pmatrix}$
- b) $\begin{pmatrix}6&2\\-2&4\end{pmatrix}$
- c) $\begin{pmatrix}1&3\\2&-1\end{pmatrix}$
- d) $\begin{pmatrix}3&1\\-1&2\end{pmatrix}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

La matrice d'un endomorphisme dans une base a pour colonnes les coordonnées des images des vecteurs de cette base, dans l'ordre. Ici, on obtient $f(\vec\imath)$ et $f(\vec\jmath)$ par linéarité, en additionnant puis en soustrayant les deux données et en divisant par $2$.

### Corrigé

Par linéarité, $f(\vec\imath+\vec\jmath)+f(\vec\imath-\vec\jmath)=2f(\vec\imath)$, donc
$$f(\vec\imath)=\dfrac12\big[(4\,;1)+(2\,;-3)\big]=(3\,;-1).$$
De même $f(\vec\imath+\vec\jmath)-f(\vec\imath-\vec\jmath)=2f(\vec\jmath)$, donc
$$f(\vec\jmath)=\dfrac12\big[(4\,;1)-(2\,;-3)\big]=(1\,;2).$$
Les colonnes sont $f(\vec\imath)$ puis $f(\vec\jmath)$ :
$$\begin{pmatrix}3&1\\-1&2\end{pmatrix}.$$
Vérification : $f(\vec\imath)+f(\vec\jmath)=(4\,;1)$ et $f(\vec\imath)-f(\vec\jmath)=(2\,;-3)$.

### Pourquoi les autres réponses sont fausses

- **a)** On a écrit les images en lignes au lieu de les écrire en colonnes.
- **b)** On a oublié de diviser par $2$ : ce sont les coordonnées de $2f(\vec\imath)$ et $2f(\vec\jmath)$.
- **c)** On a placé $f(\vec\jmath)$ en première colonne et $f(\vec\imath)$ en seconde.

</details>

Avis : 

---

## 105. `cqc-noyau-faible-1` (séries BAC:C BAC:E PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ l'endomorphisme de $\mathbb{R}^2$ défini par $f(x\,;y)=(3x-6y\,;\,-x+2y)$.

Quel est le noyau de $f$ ?

- a) $\{(0\,;0)\}$
- b) $\mathrm{Vect}\big((2\,;1)\big)$
- c) $\mathrm{Vect}\big((1\,;2)\big)$
- d) $\mathrm{Vect}\big((-2\,;1)\big)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Le noyau de $f$ est l'ensemble des vecteurs $(x\,;y)$ tels que $f(x\,;y)=(0\,;0)$. On résout le système homogène obtenu en annulant chaque coordonnée ; si les deux équations sont proportionnelles, le noyau est une droite vectorielle, que l'on décrit par un vecteur directeur.

### Corrigé

$(x\,;y)\in\ker f\iff\begin{cases}3x-6y=0\\-x+2y=0\end{cases}$

La première équation équivaut à $x=2y$ ; la seconde aussi (elle est égale à la première multipliée par $-\dfrac13$). Donc
$$\ker f=\{(2y\,;y),\ y\in\mathbb{R}\}=\mathrm{Vect}\big((2\,;1)\big).$$
Vérification : $f(2\,;1)=(6-6\,;-2+2)=(0\,;0)$.

### Pourquoi les autres réponses sont fausses

- **a)** On a conclu trop vite que seul le vecteur nul convient, sans voir que les deux équations sont proportionnelles.
- **c)** On a inversé $x$ et $y$ : $f(1\,;2)=(-9\,;3)\neq(0\,;0)$.
- **d)** Erreur de signe en résolvant $3x-6y=0$ : $f(-2\,;1)=(-12\,;4)\neq(0\,;0)$.

</details>

Avis : 

---

## 106. `cqc-raisonnement-par-l-absurde-tle-c-moyenne-3` (séries BAC:C BAC:E)

**Remarque du relecteur :** Le choix a) prend p,q naturels non nuls sans dire que r>0 (vrai car 2^r=3>1) ; une demi-ligne de justification serait plus rigoureuse.

**Énoncé :**

On veut démontrer par l'absurde qu'il n'existe aucun nombre rationnel $r$ tel que $2^r=3$.

Laquelle des rédactions suivantes est correcte ?

- a) On suppose $2^r=3$ avec $r=\dfrac pq$, $p,q$ entiers naturels non nuls ; alors $2^p=3^q$, impossible car $2^p$ est pair et $3^q$ impair.
- b) On suppose $2^r=3$ avec $r=\dfrac pq$, $p,q$ entiers naturels non nuls ; alors $2p=3q$, ce qui est impossible.
- c) On suppose $2^r=3$ avec $r=\dfrac pq$, $p,q$ entiers naturels non nuls ; alors $2^q=3^p$, impossible car $2^q$ est pair et $3^p$ impair.
- d) On suppose que $r$ n'est pas rationnel et l'on montre que $2^r\neq3$.

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un raisonnement par l'absurde, on suppose vraie la NÉGATION de ce que l'on veut démontrer, on en tire des conséquences exactes, et l'on aboutit à une impossibilité. Pour une égalité entre puissances, on élève à une puissance entière pour ne garder que des entiers, puis on utilise une propriété des entiers (ici la parité).

### Corrigé

Supposons qu'il existe un rationnel $r$ tel que $2^r=3$. Comme $3>1$, on a $r>0$, et l'on écrit $r=\dfrac pq$ avec $p,q$ entiers naturels non nuls. En élevant à la puissance $q$ : $\left(2^{p/q}\right)^q=3^q$, soit $2^p=3^q$.

Or $2^p$ est pair (car $p\geq1$) et $3^q$ est impair (produit de nombres impairs) : contradiction. Donc aucun rationnel $r$ ne vérifie $2^r=3$.

C'est la rédaction **a)**.

### Pourquoi les autres réponses sont fausses

- **b)** On a confondu $2^p$ avec $2p$ ; de plus $2p=3q$ n'est pas impossible ($p=3$, $q=2$ convient).
- **c)** Erreur sur les exposants : de $2^{p/q}=3$ on tire $2^p=3^q$, pas $2^q=3^p$ ; la conclusion repose sur une égalité fausse.
- **d)** On a supposé le contraire de l'hypothèse au lieu de supposer la négation de la conclusion : ce n'est pas un raisonnement par l'absurde et cela ne démontre rien.

</details>

Avis : 

---

## 107. `cqc-reflexion-moyenne-0` (séries BAC:C BAC:E PROBATOIRE:C PROBATOIRE:E)

**Remarque du relecteur :** Quasi-doublon de la question 10 (même axe).

**Énoncé :**

Dans un repère orthonormé, on considère la droite $(D)$ d'équation $y=x+1$ et le point $A(4\,;1)$.

Quelles sont les coordonnées de l'image $A'$ de $A$ par la réflexion d'axe $(D)$ ?

- a) $(1\,;4)$
- b) $(2\,;3)$
- c) $(0\,;5)$
- d) $(1\,;5)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

$A'$ est l'image de $A$ par la réflexion d'axe $(D)$ si et seulement si $(D)$ est la médiatrice de $[AA']$ : le milieu de $[AA']$ appartient à $(D)$ et le vecteur $\overrightarrow{AA'}$ est orthogonal à un vecteur directeur de $(D)$. On traduit ces deux conditions par un système de deux équations.

### Corrigé

On note $A'(x\,;y)$. Un vecteur directeur de $(D)$ est $\vec u(1\,;1)$.

- Orthogonalité : $\overrightarrow{AA'}(x-4\,;y-1)\cdot\vec u=0$, soit $x+y=5$.
- Milieu $\left(\dfrac{x+4}{2}\,;\dfrac{y+1}{2}\right)$ sur $(D)$ : $\dfrac{y+1}{2}=\dfrac{x+4}{2}+1$, soit $y=x+5$.

En reportant : $x+x+5=5$, donc $x=0$ et $y=5$. Ainsi $A'(0\,;5)$.

Vérification : le milieu de $[AA']$ est $(2\,;3)$, et $3=2+1$ ; $\overrightarrow{AA'}(-4\,;4)$ est bien orthogonal à $(1\,;1)$.

### Pourquoi les autres réponses sont fausses

- **a)** On a appliqué la réflexion d'axe $y=x$ (échange des coordonnées) en oubliant que l'axe est $y=x+1$.
- **b)** C'est le projeté orthogonal de $A$ sur $(D)$, c'est-à-dire le milieu de $[AA']$, pas l'image $A'$.
- **d)** Formule incomplète : on a pris $(y\,;x+1)$ au lieu de $(y-1\,;x+1)$.

</details>

Avis : 

---

## 108. `cqc-similitude-elevee-0` (séries BAC:C BAC:E PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** Similitudes directes et écriture complexe : programme de Terminale C/E, pas du Probatoire.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan complexe est muni d'un repère orthonormé direct. Une similitude directe $s$ transforme le point $O$ d'affixe $0$ en le point $A$ d'affixe $2-i$, et le point $I$ d'affixe $1$ en le point $B$ d'affixe $3$.

Quels sont le centre, le rapport et l'angle de $s$ ?

- a) Centre d'affixe $-1-2i$, rapport $\sqrt2$, angle $\dfrac\pi4$
- b) Centre d'affixe $1+2i$, rapport $2$, angle $\dfrac\pi4$
- c) Centre d'affixe $1+2i$, rapport $\sqrt2$, angle $-\dfrac\pi4$
- d) Centre d'affixe $1+2i$, rapport $\sqrt2$, angle $\dfrac\pi4$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Une similitude directe a une écriture complexe $z'=az+b$ avec $a\neq0$. Les images de deux points donnent un système qui fournit $a$ et $b$. Si $a\neq1$, le centre $\Omega$ est l'unique point invariant : $\omega=a\omega+b$, soit $\omega=\dfrac{b}{1-a}$ ; le rapport est $|a|$ et l'angle est un argument de $a$.

### Corrigé

$s(O)=A$ donne $b=2-i$. $s(I)=B$ donne $a+b=3$, donc $a=3-(2-i)=1+i$.

Centre : $\omega=\dfrac{b}{1-a}=\dfrac{2-i}{-i}=\dfrac{(2-i)\,i}{-i\times i}=\dfrac{2i+1}{1}=1+2i$.

Vérification : $(1+i)(1+2i)+2-i=1+2i+i-2+2-i=1+2i$.

Rapport : $|a|=\sqrt{1^2+1^2}=\sqrt2$. Angle : $a=\sqrt2\left(\dfrac{\sqrt2}{2}+i\dfrac{\sqrt2}{2}\right)$, donc $\arg a=\dfrac\pi4$.

$s$ a pour centre le point d'affixe $1+2i$, pour rapport $\sqrt2$ et pour angle $\dfrac\pi4$.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur le centre : on a calculé $\dfrac{b}{a-1}$ au lieu de $\dfrac{b}{1-a}$.
- **b)** On a pris $|a|^2=2$ pour le rapport au lieu de $|a|=\sqrt2$.
- **c)** Erreur sur l'argument : $1+i$ a une partie imaginaire positive, son argument est $\dfrac\pi4$ et non $-\dfrac\pi4$.

</details>

Avis : 

---

## 109. `cqc-sous-espace-vectoriel-moyenne-2` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : notion de sous-espace vectoriel de R², à vérifier au programme de Terminale C/E.

**Énoncé :**

Laquelle des parties suivantes de $\mathbb{R}^2$ est un sous-espace vectoriel de $\mathbb{R}^2$ ?

- a) $\{(x\,;y)\in\mathbb{R}^2\,:\,x+y=1\}$
- b) $\{(x\,;y)\in\mathbb{R}^2\,:\,y=x^2\}$
- c) $\{(x\,;y)\in\mathbb{R}^2\,:\,2x-3y=0\}$
- d) $\{(x\,;y)\in\mathbb{R}^2\,:\,x\geq0\}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Une partie $F$ de $\mathbb{R}^2$ est un sous-espace vectoriel si elle contient le vecteur nul et si elle est stable par combinaison linéaire : pour tous $u,v\in F$ et tous réels $\lambda,\mu$, $\lambda u+\mu v\in F$. Un seul contre-exemple suffit pour montrer qu'une partie n'en est pas un ; une équation linéaire homogène $ax+by=0$ définit toujours un sous-espace.

### Corrigé

- $\{(x\,;y)\,:\,x+y=1\}$ ne contient pas $(0\,;0)$ : ce n'est pas un sous-espace.
- $\{(x\,;y)\,:\,y=x^2\}$ contient $(1\,;1)$ mais pas $2(1\,;1)=(2\,;2)$, car $2\neq4$.
- $\{(x\,;y)\,:\,2x-3y=0\}$ : elle contient $(0\,;0)$ ; si $2x-3y=0$ et $2x'-3y'=0$, alors $2(\lambda x+\mu x')-3(\lambda y+\mu y')=\lambda\times0+\mu\times0=0$. C'est un sous-espace vectoriel (la droite vectorielle dirigée par $(3\,;2)$).
- $\{(x\,;y)\,:\,x\geq0\}$ contient $(1\,;0)$ mais pas $-1\times(1\,;0)=(-1\,;0)$.

La bonne réponse est **c)**.

### Pourquoi les autres réponses sont fausses

- **a)** C'est une droite qui ne passe pas par l'origine : elle ne contient pas le vecteur nul.
- **b)** Elle contient le vecteur nul, mais n'est pas stable par multiplication par un réel : $(1\,;1)$ y est, $(2\,;2)$ non.
- **d)** Elle est stable par addition, mais pas par multiplication par un réel négatif : $(1\,;0)$ y est, $(-1\,;0)$ non.

</details>

Avis : 

---

## 110. `cqc-tirage-simultane-prob-a-moyenne-3` (séries BAC:A BAC:TI PROBATOIRE:A)

**Séries modifiées :** retirées BAC:A, PROBATOIRE:A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Un sac contient $3$ jetons rouges et $2$ jetons verts, indiscernables au toucher. On prend au hasard, en une seule fois, $2$ jetons du sac.

Quelle est la probabilité d'obtenir deux jetons de couleurs différentes ?

- a) $\dfrac35$
- b) $\dfrac{12}{25}$
- c) $\dfrac{3}{10}$
- d) $\dfrac25$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand on prend plusieurs objets en une seule fois, l'ordre ne compte pas et un même jeton ne peut pas être pris deux fois. Avec peu d'objets, on numérote les jetons et on dresse la liste de toutes les paires possibles, qui sont équiprobables ; la probabilité est alors $\dfrac{\text{nombre de paires favorables}}{\text{nombre de paires possibles}}$.

### Corrigé

On numérote les jetons $R_1$, $R_2$, $R_3$, $V_1$, $V_2$. Les paires possibles sont :

$\{R_1,R_2\}$, $\{R_1,R_3\}$, $\{R_2,R_3\}$, $\{R_1,V_1\}$, $\{R_1,V_2\}$, $\{R_2,V_1\}$, $\{R_2,V_2\}$, $\{R_3,V_1\}$, $\{R_3,V_2\}$, $\{V_1,V_2\}$ : il y en a $10$.

Les paires de couleurs différentes sont celles formées d'un rouge et d'un vert : $3\times2=6$.

$P=\dfrac{6}{10}=\dfrac35$.

### Pourquoi les autres réponses sont fausses

- **b)** On a raisonné comme si le premier jeton était remis dans le sac : $2\times\dfrac35\times\dfrac25=\dfrac{12}{25}$.
- **c)** On n'a compté que l'ordre « rouge puis vert » : $\dfrac35\times\dfrac24=\dfrac3{10}$, en oubliant « vert puis rouge ».
- **d)** C'est la probabilité de l'événement contraire, obtenir deux jetons de même couleur : $\dfrac{4}{10}=\dfrac25$.

</details>

Avis : 

---

## 111. `cqc-variable-aleatoire-elevee-5` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:C)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

À une kermesse, un joueur mise $500$ F CFA puis lance un dé cubique équilibré. S'il obtient $6$, il reçoit $3\,000$ F CFA ; s'il obtient $4$ ou $5$, il reçoit $500$ F CFA ; sinon il ne reçoit rien. On note $G$ le gain algébrique du joueur (somme reçue moins la mise).

Quelle est l'espérance mathématique de $G$, en F CFA (valeur exacte) ?

- a) $\dfrac{2000}{3}$
- b) $\dfrac{500}{3}$
- c) $\dfrac{1000}{3}$
- d) $0$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On commence par dresser la loi de la variable aléatoire : ses valeurs (ici somme reçue moins mise, éventuellement négatives ou nulles) et leurs probabilités, dont la somme doit valoir $1$. L'espérance est ensuite $E(G)=\sum x_i\,P(G=x_i)$.

### Corrigé

Valeurs de $G$ :

- obtenir $6$ : $G=3000-500=2500$, avec probabilité $\dfrac16$ ;
- obtenir $4$ ou $5$ : $G=500-500=0$, avec probabilité $\dfrac26$ ;
- obtenir $1$, $2$ ou $3$ : $G=-500$, avec probabilité $\dfrac36$.

Contrôle : $\dfrac16+\dfrac26+\dfrac36=1$.

$$E(G)=2500\times\dfrac16+0\times\dfrac26+(-500)\times\dfrac36=\dfrac{2500-1500}{6}=\dfrac{1000}{6}=\dfrac{500}{3}.$$
L'espérance vaut $\dfrac{500}{3}$ F CFA, soit environ $166{,}67$ F CFA (arrondi au centième) : le jeu est favorable au joueur.

### Pourquoi les autres réponses sont fausses

- **a)** On a calculé l'espérance de la somme reçue, en oubliant de retrancher la mise : $\dfrac{3000+2\times500}{6}=\dfrac{2000}{3}$.
- **c)** On a compté un gain de $500$ pour les faces $4$ et $5$, en confondant la somme reçue et le gain : $\dfrac{2500+1000-1500}{6}=\dfrac{1000}{3}$.
- **d)** On a compté les faces $4$ et $5$ comme une perte de $500$ : $\dfrac{2500-5\times500}{6}=0$.

</details>

Avis : 

---

## 112. `cqc-changement-de-base-tle-c-elevee-5` (séries BAC:C BAC:E PROBATOIRE:C)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan vectoriel est muni d'une base $(\vec\imath,\vec\jmath)$. On pose $\vec e_1=2\vec\imath+\vec\jmath$ et $\vec e_2=-\vec\imath+3\vec\jmath$, qui forment une base du plan. Quelles sont les coordonnées du vecteur $\vec w=4\vec\imath+9\vec\jmath$ dans la base $(\vec e_1,\vec e_2)$ ?

- a) $(2\,;3)$
- b) $\left(\dfrac37\,;\dfrac{22}7\right)$
- c) $(-1\,;31)$
- d) $(3\,;2)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Chercher les coordonnées $(a\,;b)$ de $\vec w$ dans la base $(\vec e_1,\vec e_2)$, c'est trouver les réels $a$ et $b$ tels que $\vec w=a\vec e_1+b\vec e_2$. On exprime tout dans l'ancienne base $(\vec\imath,\vec\jmath)$ et on identifie les coordonnées, ce qui donne un système de deux équations. On vérifie toujours en recalculant $a\vec e_1+b\vec e_2$.

### Corrigé

$\det(\vec e_1,\vec e_2)=2\times3-1\times(-1)=7\neq0$ : $(\vec e_1,\vec e_2)$ est bien une base.

$a\vec e_1+b\vec e_2=(2a-b)\vec\imath+(a+3b)\vec\jmath$. On résout
$$\begin{cases}2a-b=4\\a+3b=9\end{cases}$$
La première équation donne $b=2a-4$ ; en reportant : $a+6a-12=9$, soit $a=3$, puis $b=2$.

Vérification : $3\vec e_1+2\vec e_2=(6-2)\vec\imath+(3+6)\vec\jmath=4\vec\imath+9\vec\jmath=\vec w$.

Les coordonnées de $\vec w$ dans $(\vec e_1,\vec e_2)$ sont $(3\,;2)$.

### Pourquoi les autres réponses sont fausses

- **a)** $(2\,;3)$ : bonnes valeurs mais dans le mauvais ordre ; $2\vec e_1+3\vec e_2=\vec\imath+11\vec\jmath\neq\vec w$.
- **b)** $\left(\dfrac37\,;\dfrac{22}7\right)$ : on a lu $\vec e_1(2\,;-1)$ et $\vec e_2(1\,;3)$ en échangeant lignes et colonnes, ce qui donne le système $2a+b=4$, $-a+3b=9$.
- **c)** $(-1\,;31)$ : on a calculé $4\vec e_1+9\vec e_2$, c'est-à-dire qu'on a utilisé les anciennes coordonnées comme coefficients au lieu de les chercher.

</details>

Avis : 

---

## 113. `cqc-encadrement-faible-0` (séries BAC:A BAC:C BAC:E BAC:TI)

**Remarque du relecteur :** Le choix b est un encadrement mal ordonné (borne inf > borne sup), distracteur peu sérieux.

**Énoncé :**

On sait que $2{,}449<\sqrt6<2{,}450$. Quel encadrement du nombre $A=10-3\sqrt6$ en déduit-on ?

- a) $7{,}347<A<7{,}350$
- b) $2{,}653<A<2{,}650$
- c) $2{,}650<A<2{,}653$
- d) $17{,}347<A<17{,}350$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Multiplier les trois membres d'un encadrement par un nombre positif conserve le sens des inégalités ; multiplier par un nombre négatif (ou prendre l'opposé) l'inverse. Ici, on encadre d'abord $3\sqrt6$, puis $-3\sqrt6$ (le sens change), puis on ajoute $10$.

### Corrigé

$$2{,}449<\sqrt6<2{,}450\ \Rightarrow\ 7{,}347<3\sqrt6<7{,}350\ \Rightarrow\ -7{,}350<-3\sqrt6<-7{,}347.$$
En ajoutant $10$ : $2{,}650<10-3\sqrt6<2{,}653$.

Donc $2{,}650<A<2{,}653$ (contrôle : $A\approx2{,}6515$).

### Pourquoi les autres réponses sont fausses

- **a)** C'est l'encadrement de $3\sqrt6$ : on s'est arrêté avant de prendre l'opposé et d'ajouter $10$.
- **b)** On a calculé $10-3\times2{,}449$ et $10-3\times2{,}450$ sans changer le sens des inégalités : la borne de gauche est plus grande que celle de droite, l'écriture est fausse.
- **d)** C'est l'encadrement de $10+3\sqrt6$ : on a perdu le signe moins.

</details>

Avis : 

---

## 114. `cqc-extrapolation-elevee-0` (séries BAC:A BAC:D BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une coopérative de pêche suit chaque année ses prises annuelles de poisson (en tonnes). En notant $x$ le rang de l'année ($x=1$ pour 2016) et à partir des relevés des années de rang $1$ à $9$, elle a obtenu la droite d'ajustement suivante (déjà déterminée) :
$$y=-1{,}6x+47{,}5.$$
En utilisant ce modèle, quel est le rang de la première année pour laquelle les prises seraient strictement inférieures à $20$ tonnes ?

- a) $17$
- b) $13$
- c) $43$
- d) $18$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On résout l'inéquation $-1{,}6x+47{,}5<20$. En divisant par un nombre négatif, on change le sens de l'inégalité. Comme $x$ est un rang entier, on prend le plus petit entier qui vérifie l'inéquation et on contrôle les deux entiers voisins. Un rang situé hors de la plage observée ($1$ à $9$) relève d'une extrapolation : le résultat est à interpréter avec prudence.

### Corrigé

$$-1{,}6x+47{,}5<20\iff-1{,}6x<-27{,}5\iff x>\frac{27{,}5}{1{,}6}=17{,}1875.$$
Contrôle : pour $x=17$, $y=-27{,}2+47{,}5=20{,}3$, pas encore sous $20$ ; pour $x=18$, $y=-28{,}8+47{,}5=18{,}7<20$.

Le premier rang est $x=18$ (année 2033). Ce rang est très loin de la plage observée : c'est une extrapolation, qui suppose que la baisse reste régulière pendant de nombreuses années.

### Pourquoi les autres réponses sont fausses

- **a)** $17$ : on a arrondi $17{,}1875$ par défaut, or pour $x=17$ on a encore $y=20{,}3\geq20$.
- **b)** $13$ : on a calculé $\dfrac{20}{1{,}6}=12{,}5$ en oubliant l'ordonnée à l'origine $47{,}5$.
- **c)** $43$ : on a ajouté $20$ et $47{,}5$ au lieu de les soustraire : $\dfrac{67{,}5}{1{,}6}\approx42{,}2$.

</details>

Avis : 

---

## 115. `cqc-linearite-faible-1` (séries PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Remarque du relecteur :** VOCABULAIRE : le choix a) nomme l'application h alors que les autres s'appellent f, ce qui trahit la bonne réponse ; uniformiser les noms.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une seule des applications suivantes de $\mathbb R^2$ dans $\mathbb R^2$ est linéaire. Laquelle ?

- a) $f(x,y)=(x+y,\;2y)$
- b) $f(x,y)=(x^2,\;y)$
- c) $f(x,y)=(x,\;y+1)$
- d) $f(x,y)=(xy,\;x)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Une application $f$ est linéaire si $f(\lambda u+\mu v)=\lambda f(u)+\mu f(v)$ pour tous vecteurs $u,v$ et tous réels $\lambda,\mu$. Chaque coordonnée de l'image doit être une combinaison linéaire de $x$ et $y$, sans constante, sans carré ni produit $xy$. Un contre-exemple suffit pour montrer qu'une application n'est pas linéaire (par exemple $f(0\,;0)\neq(0\,;0)$ ou $f(2u)\neq2f(u)$).

### Corrigé

$f(x,y)=(x+y,\;2y)$ : chaque coordonnée est de la forme $ax+by$. Pour $u=(x,y)$, $v=(x',y')$ et $\lambda,\mu$ réels, $h(\lambda u+\mu v)=(\lambda(x+y)+\mu(x'+y'),\;2\lambda y+2\mu y')=\lambda h(u)+\mu h(v)$ : $h$ est linéaire.

### Pourquoi les autres réponses sont fausses

- **b)** $(x^2,\;y)$ : $f(2\,;0)=(4\,;0)$ alors que $2f(1\,;0)=(2\,;0)$, le carré détruit la linéarité.
- **c)** $(x,\;y+1)$ : $f(0\,;0)=(0\,;1)\neq(0\,;0)$, la constante $1$ détruit la linéarité.
- **d)** $(xy,\;x)$ : $f(2\,;2)=(4\,;2)$ alors que $2f(1\,;1)=(2\,;2)$, le produit $xy$ détruit la linéarité.

</details>

Avis : 

---

## 116. `cqc-matrice-d-un-endomorphisme-tle-c-faible-0` (séries BAC:C BAC:E PROBATOIRE:C)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ l'endomorphisme de $\mathbb R^2$ défini par $f(x\,;y)=(4y-x\,;2x)$. Quelle est sa matrice dans la base canonique $(\vec\imath,\vec\jmath)$ ?

- a) $\begin{pmatrix}4&-1\\2&0\end{pmatrix}$
- b) $\begin{pmatrix}-1&4\\2&0\end{pmatrix}$
- c) $\begin{pmatrix}-1&2\\4&0\end{pmatrix}$
- d) $\begin{pmatrix}-1&4\\0&2\end{pmatrix}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La matrice d'un endomorphisme dans une base a pour colonnes les coordonnées des images des vecteurs de la base : première colonne $f(\vec\imath)$, deuxième colonne $f(\vec\jmath)$. Il faut lire les coefficients de $x$ et de $y$ dans cet ordre, même si l'expression est écrite dans un autre ordre, et ne pas oublier les coefficients nuls.

### Corrigé

$f(\vec\imath)=f(1\,;0)=(4\times0-1\,;2\times1)=(-1\,;2)$ et $f(\vec\jmath)=f(0\,;1)=(4\,;0)$.

$$\begin{pmatrix}-1&4\\2&0\end{pmatrix}.$$

### Pourquoi les autres réponses sont fausses

- **a)** On a recopié la première ligne dans l'ordre d'écriture $4y-x$ : le coefficient de $x$ doit venir en premier.
- **c)** C'est la transposée : on a placé $f(\vec\imath)$ et $f(\vec\jmath)$ en lignes au lieu de colonnes.
- **d)** On a mal placé le coefficient nul de la deuxième ligne : $2x$ s'écrit $2x+0y$, donc la ligne est $(2\;\;0)$.

</details>

Avis : 

---

## 117. `cqc-noyau-moyenne-0` (séries BAC:C BAC:E PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Remarque du relecteur :** LIMITE : noyau d'un endomorphisme de R^3 et notation Vect pour le Probatoire C/E ; préférer « la droite vectorielle engendrée par ».

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ l'endomorphisme de $\mathbb R^3$ défini par
$$f(x\,;y\,;z)=(x+z\,;\;2x-y\,;\;3x-y+z).$$
Quel est le noyau de $f$ ?

- a) $\operatorname{Vect}\big((1\,;0\,;1)\big)$
- b) $\operatorname{Vect}\big((1\,;2\,;-1)\big)$
- c) $\operatorname{Vect}\big((1\,;-2\,;-1)\big)$
- d) $\{\vec0\}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Le noyau est l'ensemble des vecteurs dont l'image est nulle : on résout le système linéaire homogène $f(x\,;y\,;z)=(0\,;0\,;0)$. Si une équation est combinaison des autres, le système a une infinité de solutions, que l'on exprime à l'aide d'un paramètre. On vérifie en calculant l'image du vecteur trouvé.

### Corrigé

$$\begin{cases}x+z=0\\2x-y=0\\3x-y+z=0\end{cases}$$
La troisième équation est la somme des deux premières. Les deux premières donnent $z=-x$ et $y=2x$. En posant $x=t$ : $(x\,;y\,;z)=t(1\,;2\,;-1)$.

Vérification : $f(1\,;2\,;-1)=(1-1\,;2-2\,;3-2-1)=(0\,;0\,;0)$.

$\operatorname{Ker}f=\operatorname{Vect}\big((1\,;2\,;-1)\big)$.

### Pourquoi les autres réponses sont fausses

- **a)** $(1\,;0\,;1)$ est formé des coefficients de la première équation ; $f(1\,;0\,;1)=(2\,;2\,;4)\neq\vec0$.
- **c)** Erreur de signe sur $y$ : $f(1\,;-2\,;-1)=(0\,;4\,;4)\neq\vec0$.
- **d)** Le noyau n'est pas réduit au vecteur nul, car la troisième équation n'apporte aucune condition nouvelle.

</details>

Avis : 

---

## 118. `cqc-prevision-statistique-moyenne-0` (séries BAC:A)

**Énoncé :**

Une régie d'eau suit le nombre de ménages raccordés à son réseau (en milliers). En notant $x$ le rang de l'année ($x=1$ pour 2016) et à partir des relevés de 2016 à 2023, elle a obtenu la droite d'ajustement suivante (déjà déterminée) :
$$y=2{,}45x+31{,}8.$$
Selon ce modèle, combien de milliers de ménages seront raccordés en 2027 ?

- a) $58{,}75$
- b) $63{,}65$
- c) $61{,}2$
- d) $34{,}25$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une prévision, on remplace $x$ par le rang de l'année visée dans l'équation de la droite d'ajustement. Le piège est le calcul du rang : si l'année de départ a le rang $1$, l'année $N$ a le rang $N-2016+1$.

### Corrigé

Rang de 2027 : $x=2027-2016+1=12$.

$$y=2{,}45\times12+31{,}8=29{,}4+31{,}8=61{,}2.$$

Le modèle prévoit environ $61{,}2$ milliers de ménages raccordés en 2027 (c'est une extrapolation, au-delà des relevés de 2016 à 2023).

### Pourquoi les autres réponses sont fausses

- **a)** $58{,}75$ : on a pris $x=11=2027-2016$, en oubliant que 2016 a le rang $1$ et non $0$.
- **b)** $63{,}65$ : on a pris $x=13$, en ajoutant une année de trop.
- **d)** $34{,}25$ : c'est la valeur pour $x=1$, c'est-à-dire l'année 2016.

</details>

Avis : 

---

## 119. `cqc-similitude-faible-0` (séries BAC:C BAC:E BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** Similitudes directes en écriture complexe : programme de Terminale, hors niveau pour le Probatoire C et E listés.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan complexe est muni d'un repère orthonormé direct. On considère la similitude directe $s$ d'écriture complexe
$$z'=\left(-1+i\sqrt3\right)z+4-2i.$$
Quels sont le rapport et une mesure de l'angle de $s$ ?

- a) Rapport $2$, angle $\dfrac\pi3$
- b) Rapport $4$, angle $\dfrac{2\pi}{3}$
- c) Rapport $2$, angle $\dfrac{2\pi}{3}$
- d) Rapport $2$, angle $-\dfrac\pi3$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Une similitude directe d'écriture $z'=az+b$ (avec $a\neq0$) a pour rapport $|a|$ et pour angle $\arg(a)$. Pour l'argument, on utilise à la fois $\cos\theta$ et $\sin\theta$, afin de placer l'angle dans le bon quadrant.

### Corrigé

$a=-1+i\sqrt3$ : $|a|=\sqrt{1+3}=2$. Avec $\theta=\arg(a)$ : $\cos\theta=-\dfrac12$ et $\sin\theta=\dfrac{\sqrt3}{2}$, donc $\theta=\dfrac{2\pi}{3}$.

$s$ a pour rapport $2$ et pour angle $\dfrac{2\pi}{3}$.

### Pourquoi les autres réponses sont fausses

- **a)** $\dfrac\pi3$ : on a oublié le signe de $\cos\theta=-\dfrac12$, ce qui place l'angle dans le mauvais quadrant.
- **b)** Rapport $4$ : on a pris $|a|^2=1+3$ sans la racine carrée.
- **d)** $-\dfrac\pi3$ : on a seulement utilisé $\tan\theta=\dfrac{\sqrt3}{-1}=-\sqrt3$, qui ne distingue pas $\dfrac{2\pi}{3}$ de $-\dfrac\pi3$ ; or $\sin\theta>0$.

</details>

Avis : 

---

## 120. `cqc-suites-numeriques-moyenne-2` (séries BAC:C PROBATOIRE:D)

**Remarque du relecteur :** La suite (v_n) est introduite sans être exploitée dans l'énoncé (pas de question intermédiaire) ; acceptable en QCM.

**Énoncé :**

On considère la suite $(u_n)$ définie par $u_0=10$ et, pour tout entier naturel $n$, $u_{n+1}=0{,}5\,u_n+2$. On pose $v_n=u_n-4$. Quelle est l'expression de $u_n$ en fonction de $n$ ?

- a) $u_n=4+6\times0{,}5^n$
- b) $u_n=4+10\times0{,}5^n$
- c) $u_n=6\times0{,}5^n$
- d) $u_n=4+6\times0{,}5^{n+1}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On montre que la suite auxiliaire $(v_n)$ est géométrique en exprimant $v_{n+1}$ en fonction de $v_n$. On écrit alors $v_n=v_0\,q^n$, puis on revient à $u_n=v_n+4$. Le premier terme à utiliser est $v_0$, pas $u_0$.

### Corrigé

$v_{n+1}=u_{n+1}-4=0{,}5\,u_n+2-4=0{,}5\,u_n-2=0{,}5\,(u_n-4)=0{,}5\,v_n$.

$(v_n)$ est géométrique de raison $0{,}5$ et de premier terme $v_0=10-4=6$, donc $v_n=6\times0{,}5^n$ et
$$u_n=4+6\times0{,}5^n.$$

Contrôle : $u_1=0{,}5\times10+2=7$ et $4+6\times0{,}5=7$ ; $u_2=5{,}5$ et $4+6\times0{,}25=5{,}5$.

### Pourquoi les autres réponses sont fausses

- **b)** On a pris $u_0=10$ comme premier terme de $(v_n)$ au lieu de $v_0=6$ ; pour $n=0$ on obtiendrait $14$.
- **c)** C'est l'expression de $v_n$ : on a oublié de revenir à $u_n=v_n+4$.
- **d)** Décalage d'indice : l'exposant $n+1$ correspond à une suite qui commencerait au rang $1$ ; pour $n=0$ on obtiendrait $7$.

</details>

Avis : 

---

## 121. `cqc-tirage-simultane-prob-a-moyenne-5` (séries BAC:A BAC:TI PROBATOIRE:A)

**Séries modifiées :** retirées BAC:A, PROBATOIRE:A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une urne contient $5$ boules rouges et $3$ boules vertes, indiscernables au toucher. On tire simultanément $3$ boules au hasard. Quelle est la probabilité d'obtenir exactement $2$ boules rouges ?

- a) $\dfrac{5}{28}$
- b) $\dfrac{225}{512}$
- c) $\dfrac57$
- d) $\dfrac{15}{28}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Lors d'un tirage simultané, un résultat est une partie de $3$ boules parmi $8$ : il y a $C_8^3$ résultats équiprobables. Pour compter les tirages favorables, on choisit séparément les boules de chaque couleur et on multiplie (principe multiplicatif).

### Corrigé

Nombre de tirages possibles : $C_8^3=56$.

Tirages avec exactement $2$ rouges : on choisit $2$ rouges parmi $5$ et $1$ verte parmi $3$, soit $C_5^2\times C_3^1=10\times3=30$.

$$P=\frac{30}{56}=\frac{15}{28}.$$

### Pourquoi les autres réponses sont fausses

- **a)** $\dfrac{5}{28}=\dfrac{10}{56}$ : on a compté le choix des $2$ rouges sans choisir la troisième boule verte.
- **b)** $\dfrac{225}{512}=3\times\left(\dfrac58\right)^2\times\dfrac38$ : ce calcul correspond à des tirages avec remise, pas à un tirage simultané.
- **c)** $\dfrac57=\dfrac{30+10}{56}$ : c'est la probabilité d'obtenir au moins $2$ rouges, on a ajouté le cas de $3$ rouges.

</details>

Avis : 

---

## 122. `cqc-variable-aleatoire-faible-0` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:C)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

À une kermesse, un joueur paie une mise et peut perdre ou gagner de l'argent. On note $X$ son gain algébrique (en francs CFA), dont la loi de probabilité est :

| $x_i$ | $-100$ | $0$ | $200$ | $500$ |
|---|---|---|---|---|
| $P(X=x_i)$ | $0{,}5$ | $0{,}3$ | $0{,}15$ | $0{,}05$ |

Quelle est l'espérance mathématique de $X$ ?

- a) $5$ F CFA
- b) $105$ F CFA
- c) $150$ F CFA
- d) $1{,}25$ F CFA

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

L'espérance mathématique d'une variable aléatoire est la moyenne de ses valeurs pondérée par leurs probabilités : $E(X)=\sum x_i\,P(X=x_i)$. On garde le signe des valeurs négatives (pertes) et on ne divise pas par le nombre de valeurs, puisque les probabilités ont pour somme $1$.

### Corrigé

$$E(X)=-100\times0{,}5+0\times0{,}3+200\times0{,}15+500\times0{,}05=-50+0+30+25=5.$$

En moyenne, sur un grand nombre de parties, le joueur gagne $5$ francs CFA par partie.

### Pourquoi les autres réponses sont fausses

- **b)** $105$ : on a compté la perte $-100\times0{,}5$ comme un gain $+50$.
- **c)** $150$ : c'est la moyenne simple des quatre valeurs $\dfrac{-100+0+200+500}{4}$, sans tenir compte des probabilités.
- **d)** $1{,}25$ : on a divisé la somme pondérée par $4$, comme pour une moyenne simple.

</details>

Avis : 

---

## 123. `cqc-asymptotes-moyenne-4` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PROBATOIRE:A PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Remarque du relecteur :** LIMITE : asymptote oblique d'une fonction rationnelle pour les séries A (Probatoire A, BAC A), à vérifier au programme.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb R\setminus\{2\}$ par
$$f(x)=\frac{2x^2-3x+1}{x-2}.$$
La courbe représentative de $f$ admet en $+\infty$ une asymptote oblique. Quelle est son équation ?

- a) $y=2x$
- b) $y=2x+1$
- c) $y=2x-3$
- d) $y=2x-7$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une fonction rationnelle dont le numérateur a un degré de plus que le dénominateur, on écrit $f(x)=ax+b+\dfrac{c}{x-d}$ (division euclidienne ou identification). Comme $\dfrac{c}{x-d}\to0$ en $+\infty$, on a $f(x)-(ax+b)\to0$ : la droite d'équation $y=ax+b$ est asymptote oblique.

### Corrigé

On cherche $a$, $b$, $c$ tels que $2x^2-3x+1=(ax+b)(x-2)+c$. En développant : $(ax+b)(x-2)+c=ax^2+(b-2a)x+(c-2b)$.

Par identification : $a=2$, $b-2a=-3$ donc $b=1$, et $c-2b=1$ donc $c=3$. Ainsi
$$f(x)=2x+1+\frac{3}{x-2}.$$
Vérification : $(2x+1)(x-2)+3=2x^2-3x-2+3=2x^2-3x+1$.

Comme $\displaystyle\lim_{x\to+\infty}\frac{3}{x-2}=0$, on a $\displaystyle\lim_{x\to+\infty}\big(f(x)-(2x+1)\big)=0$.

La droite d'équation $\boxed{y=2x+1}$ est asymptote oblique à la courbe en $+\infty$.

### Pourquoi les autres réponses sont fausses

- **a)** $y=2x$ : on n'a gardé que le quotient des termes de plus haut degré $\dfrac{2x^2}{x}$ ; or $f(x)-2x$ tend vers $1$, pas vers $0$.
- **c)** $y=2x-3$ : on a recopié les deux premiers coefficients du numérateur sans faire la division ; $f(x)-(2x-3)$ tend vers $4$.
- **d)** $y=2x-7$ : on a divisé par $x+2$ au lieu de $x-2$ (erreur de signe) ; $f(x)-(2x-7)$ tend vers $8$.

</details>

Avis : 

---

## 124. `cqc-covariance-prob-c-faible-0` (séries BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** VOCABULAIRE : l'énoncé nomme les variables x et y puis demande la covariance du couple (X;Y) ; harmoniser.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une étude relève, sur quatre parcelles, la quantité d'engrais $x$ (en kg) et le rendement $y$ (en quintaux). On obtient les couples $(1\,;3)$, $(2\,;5)$, $(4\,;4)$ et $(5\,;8)$. Quelle est la covariance du couple $(X\,;Y)$ ?

- a) $-2{,}25$
- b) $2{,}5$
- c) $2{,}25$
- d) $17{,}25$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

La covariance d'une série statistique double de $n$ couples est la moyenne des produits moins le produit des moyennes :
$$\operatorname{cov}(X,Y)=\overline{xy}-\bar x\,\bar y=\frac1n\sum x_iy_i-\bar x\,\bar y.$$

### Corrigé

Moyennes : $\bar x=\dfrac{1+2+4+5}{4}=3$ et $\bar y=\dfrac{3+5+4+8}{4}=5$.

Moyenne des produits : $\overline{xy}=\dfrac{1\times3+2\times5+4\times4+5\times8}{4}=\dfrac{3+10+16+40}{4}=\dfrac{69}{4}=17{,}25$.

$$\operatorname{cov}(X,Y)=17{,}25-3\times5=2{,}25$$

### Pourquoi les autres réponses sont fausses

- **a)** $-2{,}25$ : on a calculé $\bar x\,\bar y-\overline{xy}$, la différence est prise dans le mauvais sens.
- **b)** $2{,}5$ est la variance de $X$ : $\dfrac{1+4+16+25}{4}-3^2=11{,}5-9$ ; on a confondu covariance et variance.
- **d)** $17{,}25$ est la moyenne des produits : on a oublié de retrancher $\bar x\,\bar y$.

</details>

Avis : 

---

## 125. `cqc-endomorphisme-moyenne-0` (séries BAC:C BAC:E PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Remarque du relecteur :** LIMITE : endomorphisme au Probatoire C/E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan vectoriel $E$ est muni d'une base $(\vec\imath,\vec\jmath)$. On considère l'endomorphisme $f$ de $E$ tel que
$$f(\vec\imath)=\vec\imath+2\vec\jmath\qquad\text{et}\qquad f(\vec\jmath)=3\vec\imath+\vec\jmath.$$
Quel est le vecteur $\vec u$ de $E$ tel que $f(\vec u)=5\vec\imath+5\vec\jmath$ ?

- a) $20\vec\imath+15\vec\jmath$
- b) $2\vec\imath+\vec\jmath$
- c) $\vec\imath+2\vec\jmath$
- d) aucun vecteur : $5\vec\imath+5\vec\jmath$ n'a pas d'antécédent par $f$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Par linéarité, l'image du vecteur $x\vec\imath+y\vec\jmath$ est $x\,f(\vec\imath)+y\,f(\vec\jmath)$. Chercher un antécédent revient donc à résoudre un système linéaire de deux équations à deux inconnues ; si ce système a un déterminant non nul, l'antécédent existe et il est unique.

### Corrigé

Pour $\vec u=x\vec\imath+y\vec\jmath$ :
$$f(\vec u)=x(\vec\imath+2\vec\jmath)+y(3\vec\imath+\vec\jmath)=(x+3y)\vec\imath+(2x+y)\vec\jmath.$$
$f(\vec u)=5\vec\imath+5\vec\jmath$ équivaut à
$$\begin{cases}x+3y=5\\2x+y=5\end{cases}$$
Le déterminant du système vaut $1\times1-3\times2=-5\neq0$ : la solution est unique. La seconde équation donne $y=5-2x$, puis $x+15-6x=5$, donc $x=2$ et $y=1$.

Vérification : $f(2\vec\imath+\vec\jmath)=2(\vec\imath+2\vec\jmath)+(3\vec\imath+\vec\jmath)=5\vec\imath+5\vec\jmath$.

$$\boxed{\vec u=2\vec\imath+\vec\jmath}$$

### Pourquoi les autres réponses sont fausses

- **a)** $20\vec\imath+15\vec\jmath$ est l'image $f(5\vec\imath+5\vec\jmath)$ : on a calculé une image au lieu d'un antécédent.
- **c)** $\vec\imath+2\vec\jmath$ vient d'un système écrit avec les coordonnées des images en lignes au lieu de colonnes ($x+2y=5$, $3x+y=5$) ; son image est $7\vec\imath+4\vec\jmath$.
- **d)** Le déterminant du système n'est pas nul : $f$ est bijectif et tout vecteur a un antécédent.

</details>

Avis : 

---

## 126. `cqc-extrapolation-faible-0` (séries BAC:A BAC:D BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

La consommation d'eau d'une petite ville était de $1\,200\ \text{m}^3$ par jour en 2018 et de $1\,440\ \text{m}^3$ par jour en 2022. On ne dispose d'aucun relevé après 2022. On admet que, sur cette période, la consommation journalière évolue de façon affine en fonction de l'année, et on utilise ce modèle pour estimer la consommation journalière en 2025.

Quelle est l'estimation obtenue, et de quel type d'estimation s'agit-il ?

- a) $1\,620\ \text{m}^3$ par jour ; c'est une interpolation
- b) $1\,680\ \text{m}^3$ par jour ; c'est une extrapolation
- c) $1\,380\ \text{m}^3$ par jour ; c'est une extrapolation
- d) $1\,620\ \text{m}^3$ par jour ; c'est une extrapolation

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Avec un modèle affine, l'augmentation est la même chaque année : on calcule l'augmentation annuelle (le coefficient directeur), puis on l'applique au nombre d'années écoulées. Une estimation faite à l'intérieur de la période observée est une interpolation ; une estimation faite en dehors de cette période est une extrapolation, à interpréter avec prudence.

### Corrigé

Augmentation annuelle : $\dfrac{1\,440-1\,200}{2022-2018}=\dfrac{240}{4}=60\ \text{m}^3$ par an.

De 2022 à 2025, il s'écoule $3$ ans : $1\,440+3\times60=1\,620\ \text{m}^3$ par jour.

L'année 2025 est en dehors de la période observée $[2018\,;2022]$ : c'est une **extrapolation**.

Réponse : **$1\,620\ \text{m}^3$ par jour, extrapolation**.

### Pourquoi les autres réponses sont fausses

- **a)** La valeur est juste, mais 2025 n'est pas dans la période des relevés : ce n'est pas une interpolation.
- **b)** $1\,680$ : on a ajouté toute l'augmentation des quatre années ($240$) au lieu de trois fois l'augmentation annuelle.
- **c)** $1\,380$ : on est parti de la valeur de 2018 au lieu de celle de 2022 ($1\,200+3\times60$).

</details>

Avis : 

---

## 127. `cqc-linearite-moyenne-2` (séries PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Pour un réel $m$, on considère l'application $h_m:\mathbb R^2\to\mathbb R^2$ définie par
$$h_m(x,y)=\left(x+my+m^2-m\,,\;2x-y+m-1\right).$$
Pour quelle(s) valeur(s) de $m$ l'application $h_m$ est-elle linéaire ?

- a) $m=1$
- b) $m\in\{0\,;1\}$
- c) $m=0$
- d) pour tout réel $m$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Une application linéaire envoie toujours le vecteur nul sur le vecteur nul : $h(0,0)=(0,0)$ est une condition nécessaire. Une application dont chaque coordonnée est une combinaison linéaire de $x$ et $y$, sans terme constant, est linéaire. On vérifie donc que **tous** les termes constants s'annulent.

### Corrigé

$h_m(0,0)=\left(m^2-m\,,\;m-1\right)$. Pour que $h_m$ soit linéaire, il faut $m^2-m=0$ et $m-1=0$.

- $m^2-m=m(m-1)=0$ donne $m=0$ ou $m=1$ ;
- $m-1=0$ donne $m=1$.

La seule valeur possible est $m=1$. Réciproquement, $h_1(x,y)=(x+y\,,\;2x-y)$ : chaque coordonnée est une combinaison linéaire de $x$ et $y$, donc $h_1$ est linéaire.

$$\boxed{m=1}$$

### Pourquoi les autres réponses sont fausses

- **b)** On n'a annulé que le terme constant de la première coordonnée ; pour $m=0$, $h_0(0,0)=(0\,,-1)\neq(0,0)$.
- **c)** Pour $m=0$, le terme constant $m-1=-1$ de la seconde coordonnée n'est pas nul.
- **d)** On a cru que les termes constants n'empêchaient pas la linéarité ; or $h_m(0,0)$ doit être nul.

</details>

Avis : 

---

## 128. `cqc-matrice-d-un-endomorphisme-tle-c-moyenne-2` (séries BAC:C BAC:E PROBATOIRE:C)

**Séries modifiées :** retirées PROBATOIRE:C.

**Remarque du relecteur :** LIMITE : matrice d'une composée au Probatoire C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan vectoriel est muni d'une base $(\vec\imath,\vec\jmath)$. Soit $f$ l'endomorphisme tel que $f(\vec\imath)=2\vec\imath-\vec\jmath$ et $f(\vec\jmath)=\vec\imath+3\vec\jmath$.

Quelle est la matrice de $f\circ f$ dans la base $(\vec\imath,\vec\jmath)$ ?

- a) $\begin{pmatrix}4&1\\1&9\end{pmatrix}$
- b) $\begin{pmatrix}3&-5\\5&8\end{pmatrix}$
- c) $\begin{pmatrix}4&2\\-2&6\end{pmatrix}$
- d) $\begin{pmatrix}3&5\\-5&8\end{pmatrix}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans la matrice d'un endomorphisme, chaque **colonne** contient les coordonnées de l'image d'un vecteur de la base. La matrice de $f\circ f$ est le produit $A\times A=A^2$, calculé ligne par colonne ; on ne l'obtient pas en élevant chaque coefficient au carré.

### Corrigé

Les colonnes de la matrice de $f$ sont les coordonnées de $f(\vec\imath)$ et de $f(\vec\jmath)$ :
$$A=\begin{pmatrix}2&1\\-1&3\end{pmatrix}.$$
$$A^2=\begin{pmatrix}2\times2+1\times(-1)&2\times1+1\times3\\(-1)\times2+3\times(-1)&(-1)\times1+3\times3\end{pmatrix}=\begin{pmatrix}3&5\\-5&8\end{pmatrix}.$$
Vérification directe : $f(f(\vec\imath))=f(2\vec\imath-\vec\jmath)=2(2\vec\imath-\vec\jmath)-(\vec\imath+3\vec\jmath)=3\vec\imath-5\vec\jmath$, qui est bien la première colonne.

### Pourquoi les autres réponses sont fausses

- **a)** On a élevé chaque coefficient au carré : ce n'est pas un produit de matrices.
- **b)** On a placé les images en lignes au lieu de colonnes ; on obtient alors la transposée du bon résultat.
- **c)** On a calculé $2A$ au lieu de $A\times A$.

</details>

Avis : 

---

## 129. `cqc-noyau-moyenne-1` (séries BAC:C BAC:E PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Remarque du relecteur :** LIMITE : endomorphisme et noyau au Probatoire C/E, à vérifier au programme de Première.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan vectoriel est muni d'une base $(\vec\imath,\vec\jmath)$. Pour un réel $m$, on considère l'endomorphisme $f_m$ défini par
$$f_m(x\vec\imath+y\vec\jmath)=(x+my)\vec\imath+(2x+4y)\vec\jmath.$$
Pour quelle valeur de $m$ le noyau de $f_m$ n'est-il pas réduit au vecteur nul, et quel est alors ce noyau ?

- a) $m=2$ et le noyau est $\mathrm{Vect}(\vec\imath+2\vec\jmath)$
- b) $m=-2$ et le noyau est $\mathrm{Vect}(2\vec\imath+\vec\jmath)$
- c) $m=2$ et le noyau est $\mathrm{Vect}(2\vec\imath-\vec\jmath)$
- d) $m=2$ et le noyau est $\mathrm{Vect}(2\vec\imath+\vec\jmath)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Le noyau s'obtient en résolvant $f_m(\vec u)=\vec 0$, c'est-à-dire un système linéaire homogène. Ce système admet d'autres solutions que $(0,0)$ exactement quand son déterminant est nul ; on résout alors le système pour trouver un vecteur directeur du noyau. Il ne faut pas confondre le noyau avec l'image, engendrée par $f_m(\vec\imath)$ et $f_m(\vec\jmath)$.

### Corrigé

$f_m(x\vec\imath+y\vec\jmath)=\vec 0$ équivaut à
$$\begin{cases}x+my=0\\2x+4y=0\end{cases}$$
Le déterminant vaut $1\times4-m\times2=4-2m$ ; il est nul si et seulement si $m=2$.

Pour $m=2$, les deux équations se ramènent à $x=-2y$ : $\ker f_2=\{-2y\vec\imath+y\vec\jmath,\ y\in\mathbb R\}=\mathrm{Vect}(-2\vec\imath+\vec\jmath)=\mathrm{Vect}(2\vec\imath-\vec\jmath)$.

Vérification : $f_2(2\vec\imath-\vec\jmath)=(2-2)\vec\imath+(4-4)\vec\jmath=\vec 0$.

Réponse : **$m=2$ et $\ker f_2=\mathrm{Vect}(2\vec\imath-\vec\jmath)$**.

### Pourquoi les autres réponses sont fausses

- **a)** $\mathrm{Vect}(\vec\imath+2\vec\jmath)$ est l'image de $f_2$ (engendrée par $f_2(\vec\imath)=\vec\imath+2\vec\jmath$) : on a confondu noyau et image.
- **b)** Erreur de signe dans le déterminant ($4+2m=0$) ; pour $m=-2$, le déterminant vaut $8$ et le noyau est réduit à $\{\vec 0\}$.
- **d)** Erreur de signe sur le vecteur directeur : $f_2(2\vec\imath+\vec\jmath)=4\vec\imath+8\vec\jmath\neq\vec 0$.

</details>

Avis : 

---

## 130. `cqc-produit-scalaire-prob-c-faible-0` (séries PROBATOIRE:C PROBATOIRE:D PROBATOIRE:E)

**Énoncé :**

Dans un repère orthonormé du plan, on considère les vecteurs $\vec u(3\,;-2)$ et $\vec v(m\,;6)$, où $m$ est un réel. Pour quelle valeur de $m$ les vecteurs $\vec u$ et $\vec v$ sont-ils orthogonaux ?

- a) $m=-4$
- b) $m=4$
- c) $m=-9$
- d) $m=9$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un repère orthonormé, le produit scalaire de $\vec u(x\,;y)$ et $\vec v(x'\,;y')$ est $\vec u\cdot\vec v=xx'+yy'$. Deux vecteurs sont orthogonaux si et seulement si leur produit scalaire est nul. Il ne faut pas confondre cette condition avec celle de colinéarité, $xy'-yx'=0$.

### Corrigé

$$\vec u\cdot\vec v=3\times m+(-2)\times6=3m-12.$$
$\vec u\cdot\vec v=0$ équivaut à $3m=12$, soit $\boxed{m=4}$.

Vérification : $\vec v(4\,;6)$ et $3\times4+(-2)\times6=12-12=0$.

### Pourquoi les autres réponses sont fausses

- **a)** $m=-4$ : erreur de signe sur le produit $(-2)\times6$, on a résolu $3m+12=0$.
- **c)** $m=-9$ : on a écrit la condition de colinéarité $3\times6-(-2)\times m=0$ au lieu de l'orthogonalité.
- **d)** $m=9$ : on a croisé les coordonnées, $3\times6+(-2)\times m=0$.

</details>

Avis : 

---

## 131. `cqc-similitude-faible-1` (séries BAC:C BAC:E BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** Similitudes directes : programme de Terminale C/E, pas du Probatoire C/E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une similitude directe $s$ transforme les points $A$ et $B$ en $A'$ et $B'$, avec $AB=4$ cm et $A'B'=6$ cm. Elle transforme un triangle $ABC$ d'aire $12\ \text{cm}^2$ en un triangle $A'B'C'$.

Quelle est l'aire du triangle $A'B'C'$ ?

- a) $18\ \text{cm}^2$
- b) $8\ \text{cm}^2$
- c) $\dfrac{16}{3}\ \text{cm}^2$
- d) $27\ \text{cm}^2$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Le rapport $k$ d'une similitude est le quotient de la longueur d'une image par la longueur de l'objet : $k=\dfrac{A'B'}{AB}$. Une similitude de rapport $k$ multiplie les longueurs par $k$ et les **aires par $k^2$**.

### Corrigé

$$k=\frac{A'B'}{AB}=\frac64=\frac32.$$
$$\mathcal A(A'B'C')=k^2\times\mathcal A(ABC)=\frac94\times12=27\ \text{cm}^2.$$

### Pourquoi les autres réponses sont fausses

- **a)** $18$ : on a multiplié l'aire par $k$ au lieu de $k^2$.
- **b)** $8$ : on a divisé l'aire par $k$ (rapport pris à l'envers, et sans carré).
- **c)** $\dfrac{16}{3}$ : on a divisé l'aire par $k^2$ au lieu de la multiplier.

</details>

Avis : 

---

## 132. `cqc-sous-espace-vectoriel-moyenne-4` (séries BAC:C BAC:E)

**Remarque du relecteur :** LIMITE : dimension d'un sous-espace vectoriel de R^3, à confirmer au programme BAC C/E.

**Énoncé :**

On considère le sous-ensemble $F$ de $\mathbb R^3$ défini par
$$F=\left\{(x,y,z)\in\mathbb R^3\ :\ x-2y+z=0\ \text{et}\ 2x-4y+2z=0\right\}.$$
$F$ est un sous-espace vectoriel de $\mathbb R^3$. Quelle est sa dimension ?

- a) $1$
- b) $2$
- c) $3$
- d) $0$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Avant de compter les équations, on vérifie si elles sont indépendantes : deux équations proportionnelles n'en font qu'une. On exprime ensuite une inconnue en fonction des autres et on écrit $F$ comme l'ensemble des combinaisons linéaires de vecteurs ; le nombre de vecteurs d'une famille libre et génératrice est la dimension.

### Corrigé

La seconde équation est le double de la première : $2x-4y+2z=2(x-2y+z)$. Donc $F=\{(x,y,z)\ :\ x=2y-z\}$.

Tout vecteur de $F$ s'écrit
$$(2y-z\,,\,y\,,\,z)=y\,(2,1,0)+z\,(-1,0,1).$$
Les vecteurs $(2,1,0)$ et $(-1,0,1)$ ne sont pas colinéaires (la deuxième coordonnée de l'un est nulle, pas celle de l'autre) : ils forment une famille libre et génératrice de $F$.

$$\boxed{\dim F=2}$$

### Pourquoi les autres réponses sont fausses

- **a)** $1$ : on a retiré une dimension par équation sans voir que les deux équations sont proportionnelles.
- **c)** $3$ : $F$ n'est pas $\mathbb R^3$ tout entier ; par exemple $(1,0,0)$ n'appartient pas à $F$.
- **d)** $0$ : $F$ n'est pas réduit au vecteur nul, puisqu'il contient $(2,1,0)$.

</details>

Avis : 

---

## 133. `cqc-tirage-successif-sans-remise-elevee-0` (séries BAC:A BAC:C BAC:E PROBATOIRE:A)

**Énoncé :**

Une urne contient $6$ boules numérotées : $4$ rouges et $2$ vertes. On tire successivement et sans remise $3$ boules, en notant l'ordre de sortie ; un tirage est donc une liste ordonnée de $3$ boules distinctes.

Combien de tirages comportent **exactement une** boule verte ?

- a) $24$
- b) $96$
- c) $72$
- d) $36$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour dénombrer des tirages successifs sans remise vérifiant une condition, on décompose la construction en étapes : choix de la place de la boule particulière, choix de cette boule, puis remplissage ordonné des autres places, en diminuant de $1$ le nombre de boules disponibles à chaque tirage. On multiplie les nombres de choix (principe multiplicatif).

### Corrigé

- Place de la boule verte dans la liste : $3$ choix (1er, 2e ou 3e tirage).
- Boule verte : $2$ choix.
- Les deux autres places reçoivent des boules rouges, dans l'ordre et sans remise : $4\times3=12$ choix.

$$3\times2\times12=72\ \text{tirages}$$

Contrôle : il y a $6\times5\times4=120$ tirages en tout ; $4\times3\times2=24$ n'ont aucune verte et $3\times2\times4=24$ en ont deux : $72+24+24=120$.

### Pourquoi les autres réponses sont fausses

- **a)** $24=2\times4\times3$ : on a oublié de choisir la place de la boule verte (on l'a toujours mise en premier).
- **b)** $96=120-24$ est le nombre de tirages comportant **au moins une** boule verte.
- **d)** $36=3\times2\times6$ : on n'a pas tenu compte de l'ordre des deux boules rouges.

</details>

Avis : 

---

## 134. `cqc-variable-aleatoire-faible-1` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:C)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On lance un dé cubique équilibré dont les faces sont numérotées de $1$ à $6$. Si l'on obtient $6$, on marque $4$ points ; si l'on obtient $4$ ou $5$, on marque $1$ point ; sinon, on perd $1$ point. On note $X$ le nombre de points marqués (compté négativement en cas de perte).

Quelle est l'espérance mathématique de $X$ ?

- a) $\dfrac43$
- b) $\dfrac12$
- c) $\dfrac23$
- d) $\dfrac32$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On établit d'abord la loi de $X$ : ses valeurs possibles et la probabilité de chacune, en comptant les issues favorables. L'espérance est la somme des valeurs pondérées par leurs probabilités : $E(X)=\sum x_i\,P(X=x_i)$. Une perte se compte avec un signe « moins ».

### Corrigé

Loi de $X$ :
- $X=4$ pour la face $6$ : $P(X=4)=\dfrac16$ ;
- $X=1$ pour les faces $4$ et $5$ : $P(X=1)=\dfrac26$ ;
- $X=-1$ pour les faces $1$, $2$, $3$ : $P(X=-1)=\dfrac36$.

$$E(X)=4\times\frac16+1\times\frac26+(-1)\times\frac36=\frac{4+2-3}{6}=\frac36=\frac12.$$

### Pourquoi les autres réponses sont fausses

- **a)** $\dfrac43$ : on a fait la moyenne des trois valeurs $4$, $1$ et $-1$ sans tenir compte de leurs probabilités.
- **c)** $\dfrac23$ : on a affecté la probabilité $\dfrac16$ à chaque valeur, en oubliant que $1$ correspond à deux faces et $-1$ à trois.
- **d)** $\dfrac32$ : on a compté la perte positivement, $\dfrac{4+2+3}{6}$.

</details>

Avis : 

---

## 135. `cqc-aire-d-un-triangle-rectangle-faible-1` (séries BEPC:)

**Remarque du relecteur :** Doublon quasi identique de la question 3 de ce lot (mêmes données 8 et 17, aire 60).

**Énoncé :**

$KLM$ est un triangle rectangle en $K$, avec $KL=8$ cm et $LM=17$ cm. Quelle est l'aire du triangle $KLM$ ?

- a) $68\ \text{cm}^2$
- b) $136\ \text{cm}^2$
- c) $60\ \text{cm}^2$
- d) $120\ \text{cm}^2$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

L'aire d'un triangle rectangle est le demi-produit des deux côtés de l'angle droit. Si l'un d'eux n'est pas donné, on le calcule d'abord avec le théorème de Pythagore ; l'hypoténuse (côté opposé à l'angle droit) n'intervient pas directement dans la formule de l'aire.

### Corrigé

Le triangle est rectangle en $K$ : les côtés de l'angle droit sont $[KL]$ et $[KM]$, et $[LM]$ est l'hypoténuse.

Théorème de Pythagore : $LM^2=KL^2+KM^2$, donc $KM^2=17^2-8^2=289-64=225$ et $KM=15$ cm.

$$\mathcal{A}=\frac{KL\times KM}{2}=\frac{8\times15}{2}=60\ \text{cm}^2.$$

### Pourquoi les autres réponses sont fausses

- **a)** On a pris l'hypoténuse $LM$ comme côté de l'angle droit : $\dfrac{8\times17}{2}=68$.
- **b)** On a pris l'hypoténuse et oublié de diviser par $2$ : $8\times17=136$.
- **d)** Le côté $KM=15$ est juste, mais on a oublié de diviser par $2$.

</details>

Avis : 

---

## 136. `cqc-covariance-prob-c-moyenne-2` (séries BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On considère la série statistique double de trois points $(x_i\,;y_i)$ : $(1\,;2)$, $(3\,;4)$ et $(5\,;9)$.

Quelle est la covariance de cette série ?

- a) $14$
- b) $\dfrac{14}{3}$
- c) $\dfrac{59}{3}$
- d) $\dfrac{8}{3}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La covariance d'une série de $n$ points est $\operatorname{cov}(X,Y)=\dfrac1n\displaystyle\sum_{i=1}^{n}x_iy_i-\bar x\,\bar y$, ce qui revient à la moyenne des produits $(x_i-\bar x)(y_i-\bar y)$. Il ne faut oublier ni la division par $n$, ni la soustraction du produit des moyennes.

### Corrigé

$\bar x=\dfrac{1+3+5}{3}=3$ et $\bar y=\dfrac{2+4+9}{3}=5$.

$\dfrac13\sum x_iy_i=\dfrac{2+12+45}{3}=\dfrac{59}{3}$.

$$\operatorname{cov}(X,Y)=\frac{59}{3}-3\times5=\frac{59-45}{3}=\frac{14}{3}.$$

Contrôle : $\sum(x_i-\bar x)(y_i-\bar y)=(-2)(-3)+0\times(-1)+2\times4=14$, et $\dfrac{14}{3}$ est bien la moyenne de ces produits.

### Pourquoi les autres réponses sont fausses

- **a)** C'est la somme des produits $(x_i-\bar x)(y_i-\bar y)$ : on a oublié de diviser par l'effectif $3$.
- **c)** C'est la moyenne des produits $x_iy_i$ : on a oublié de retrancher $\bar x\,\bar y=15$.
- **d)** C'est la variance de $X$, et non la covariance de $X$ et $Y$.

</details>

Avis : 

---

## 137. `cqc-endomorphisme-moyenne-2` (séries BAC:C BAC:E PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Remarque du relecteur :** LIMITE : image d'un endomorphisme au Probatoire C/E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan vectoriel est muni d'une base $(\vec\imath,\vec\jmath)$. On considère l'endomorphisme $f$ défini par $f(\vec\imath)=2\vec\imath-\vec\jmath$ et $f(\vec\jmath)=-4\vec\imath+2\vec\jmath$.

Quel est l'ensemble des vecteurs $x\vec\imath+y\vec\jmath$ qui constituent l'image de $f$ ?

- a) La droite d'équation $x-2y=0$
- b) La droite d'équation $2x+y=0$
- c) Le plan tout entier
- d) La droite d'équation $x+2y=0$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

L'image d'un endomorphisme est engendrée par les images des vecteurs de la base. Si ces images sont colinéaires (et non toutes nulles), l'image est une droite vectorielle, dont on écrit une équation à partir d'un vecteur directeur. Il ne faut pas confondre l'image (ensemble des $f(\vec u)$) et le noyau (ensemble des $\vec u$ tels que $f(\vec u)=\vec 0$).

### Corrigé

$f(\vec\jmath)=-4\vec\imath+2\vec\jmath=-2(2\vec\imath-\vec\jmath)=-2f(\vec\imath)$ : les deux images sont colinéaires, donc $\mathrm{Im}\,f=\mathrm{Vect}(2\vec\imath-\vec\jmath)$ est une droite vectorielle.

Un vecteur $x\vec\imath+y\vec\jmath$ est colinéaire à $2\vec\imath-\vec\jmath$ si et seulement si $x\times(-1)-y\times2=0$, soit $x+2y=0$.

Pour comparaison, le noyau : $f(x\vec\imath+y\vec\jmath)=(2x-4y)\vec\imath+(-x+2y)\vec\jmath=\vec 0$ équivaut à $x=2y$, donc $\ker f$ est la droite d'équation $x-2y=0$.

$\mathrm{Im}\,f$ est la droite d'équation $x+2y=0$.

### Pourquoi les autres réponses sont fausses

- **a)** C'est le noyau de $f$ (vecteurs envoyés sur $\vec 0$), pas son image.
- **b)** Les coordonnées du vecteur directeur $2\vec\imath-\vec\jmath$ ont été permutées : $2\vec\imath-\vec\jmath$ ne vérifie pas $2x+y=0$.
- **c)** $f(\vec\imath)$ et $f(\vec\jmath)$ sont colinéaires : $f$ n'est pas bijectif et son image n'est qu'une droite.

</details>

Avis : 

---

## 138. `cqc-extrapolation-moyenne-0` (séries BAC:A BAC:D BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une coopérative relève sa production annuelle de cacao de 2015 à 2022. On note $x$ le rang de l'année ($x=1$ pour 2015, $x=2$ pour 2016, etc.) et $y$ la production en tonnes. L'ajustement affine retenu pour ces données est $y=2{,}5x+14$.

En supposant que cette tendance se poursuive, en quelle année la production dépassera-t-elle $50$ tonnes pour la première fois ?

- a) 2030
- b) 2029
- c) 2028
- d) 2034

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une extrapolation, on utilise l'équation de la droite d'ajustement en dehors de la période observée. On traduit la condition sur $y$ par une inéquation en $x$, on prend le plus petit rang entier qui la vérifie, puis on convertit ce rang en année en tenant compte de la correspondance choisie ($x=1$ pour la première année).

### Corrigé

On résout $2{,}5x+14>50$ : $2{,}5x>36$, soit $x>14{,}4$. Le plus petit rang entier est $x=15$.

Contrôle : pour $x=14$, $y=2{,}5\times14+14=49$ (moins de $50$) ; pour $x=15$, $y=51{,}5$.

Le rang $x=1$ correspond à 2015, donc le rang $15$ correspond à $2015+14=2029$.

La production dépassera $50$ tonnes pour la première fois en 2029 (estimation par extrapolation, à prendre avec prudence puisque 2029 est loin de la période observée).

### Pourquoi les autres réponses sont fausses

- **a)** On a ajouté le rang à 2015 ($2015+15$), alors que le rang $1$ correspond déjà à 2015.
- **c)** On a arrondi $14{,}4$ à $14$ : pour $x=14$, la production n'est que de $49$ tonnes.
- **d)** On a oublié l'ordonnée à l'origine : $2{,}5x>50$ donne $x>20$, ce qui est faux.

</details>

Avis : 

---

## 139. `cqc-forme-algebrique-d-un-quotient-elevee-0` (séries BAC:A BAC:D)

**Séries modifiées :** retirées BAC:A.

**Remarque du relecteur :** Nombres complexes hors programme de la série A (BAC:A listé) ; correct pour BAC D.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $a$ un nombre réel et $Z=\dfrac{2+ai}{3+i}$.

Pour quelle valeur de $a$ le nombre complexe $Z$ est-il imaginaire pur ?

- a) $a=6$
- b) $a=\dfrac23$
- c) $a=-6$
- d) Aucune valeur de $a$ ne convient

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour écrire un quotient sous forme algébrique, on multiplie numérateur et dénominateur par le conjugué du dénominateur, en remplaçant $i^2$ par $-1$. Un nombre $x+iy$ est imaginaire pur lorsque sa partie réelle $x$ est nulle (il est réel lorsque $y=0$).

### Corrigé

Le conjugué de $3+i$ est $3-i$, et $(3+i)(3-i)=9+1=10$.
$$Z=\frac{(2+ai)(3-i)}{10}=\frac{6-2i+3ai-ai^2}{10}=\frac{(6+a)+(3a-2)i}{10}.$$
$Z$ est imaginaire pur si et seulement si $6+a=0$, soit $a=-6$.

Vérification : pour $a=-6$, $Z=\dfrac{-20i}{10}=-2i$, qui est bien imaginaire pur.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur sur $i^2$ : on a écrit $-ai^2=-a$, d'où une partie réelle $6-a$.
- **b)** On a annulé la partie imaginaire $3a-2$ : pour $a=\dfrac23$, $Z$ est réel, pas imaginaire pur.
- **d)** La partie réelle $\dfrac{6+a}{10}$ s'annule bien pour $a=-6$.

</details>

Avis : 

---

## 140. `cqc-linearite-moyenne-3` (séries PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Laquelle des applications suivantes, de $\mathbb{R}^2$ dans $\mathbb{R}^2$, est linéaire ?

- a) $(x,y)\mapsto(2x-y\,;x+3)$
- b) $(x,y)\mapsto(x^2\,;x-y)$
- c) $(x,y)\mapsto(3y\,;x-2y)$
- d) $(x,y)\mapsto(xy\,;y)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Une application $f$ est linéaire si $f(\lambda\vec u+\mu\vec v)=\lambda f(\vec u)+\mu f(\vec v)$ pour tous vecteurs et tous réels. En pratique, les coordonnées de $f(x,y)$ doivent être des combinaisons $ax+by$, sans constante ajoutée, sans carré et sans produit $xy$. Un test rapide : une application linéaire vérifie toujours $f(0\,;0)=(0\,;0)$.

### Corrigé

$f(x,y)=(3y\,;x-2y)$ : chaque coordonnée est de la forme $ax+by$. Pour tous vecteurs $(x,y)$, $(x',y')$ et tous réels $\lambda,\mu$ :
$$f(\lambda x+\mu x',\lambda y+\mu y')=\big(3(\lambda y+\mu y')\,;(\lambda x+\mu x')-2(\lambda y+\mu y')\big)=\lambda f(x,y)+\mu f(x',y').$$
Cette application est linéaire.

Les trois autres ne le sont pas : $(2x-y\,;x+3)$ donne $(0\,;3)$ en $(0\,;0)$ ; pour $(x^2\,;x-y)$ et $(xy\,;y)$, l'image de $2(1\,;1)$ a pour première coordonnée $4$, alors que le double de l'image de $(1\,;1)$ a pour première coordonnée $2$.

### Pourquoi les autres réponses sont fausses

- **a)** La constante $+3$ empêche la linéarité : l'image de $(0\,;0)$ est $(0\,;3)\neq(0\,;0)$ (l'application est affine).
- **b)** Le carré $x^2$ n'est pas linéaire : l'image de $(2\,;2)$ a pour première coordonnée $4$ et non $2\times1$.
- **d)** Le produit $xy$ n'est pas linéaire : l'image de $(2\,;2)$ a pour première coordonnée $4$ et non $2\times1$.

</details>

Avis : 

---

## 141. `cqc-matrice-d-un-endomorphisme-tle-c-moyenne-3` (séries BAC:C BAC:E PROBATOIRE:C)

**Séries modifiées :** retirées PROBATOIRE:C.

**Remarque du relecteur :** LIMITE : matrice d'endomorphisme au Probatoire C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan vectoriel est muni d'une base $(\vec\imath,\vec\jmath)$. Un endomorphisme $f$ vérifie
$$f(\vec\imath+\vec\jmath)=4\vec\imath+2\vec\jmath\qquad\text{et}\qquad f(\vec\imath-\vec\jmath)=2\vec\imath-4\vec\jmath.$$
Quelle est la matrice de $f$ dans la base $(\vec\imath,\vec\jmath)$ ?

- a) $\begin{pmatrix}3&-1\\1&3\end{pmatrix}$
- b) $\begin{pmatrix}3&1\\-1&3\end{pmatrix}$
- c) $\begin{pmatrix}4&2\\2&-4\end{pmatrix}$
- d) $\begin{pmatrix}3&-1\\-1&-3\end{pmatrix}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La matrice de $f$ dans la base $(\vec\imath,\vec\jmath)$ a pour première colonne les coordonnées de $f(\vec\imath)$ et pour deuxième colonne celles de $f(\vec\jmath)$. Lorsque l'on connaît les images d'autres vecteurs, on retrouve $f(\vec\imath)$ et $f(\vec\jmath)$ grâce à la linéarité, en exprimant $\vec\imath$ et $\vec\jmath$ à partir de ces vecteurs.

### Corrigé

On a $\vec\imath=\dfrac12\big[(\vec\imath+\vec\jmath)+(\vec\imath-\vec\jmath)\big]$ et $\vec\jmath=\dfrac12\big[(\vec\imath+\vec\jmath)-(\vec\imath-\vec\jmath)\big]$. Par linéarité :
$$f(\vec\imath)=\frac12\big[(4\vec\imath+2\vec\jmath)+(2\vec\imath-4\vec\jmath)\big]=3\vec\imath-\vec\jmath,$$
$$f(\vec\jmath)=\frac12\big[(4\vec\imath+2\vec\jmath)-(2\vec\imath-4\vec\jmath)\big]=\vec\imath+3\vec\jmath.$$
En rangeant ces coordonnées en colonnes :
$$\begin{pmatrix}3&1\\-1&3\end{pmatrix}.$$

### Pourquoi les autres réponses sont fausses

- **a)** Les coordonnées de $f(\vec\imath)$ et $f(\vec\jmath)$ ont été rangées en lignes au lieu de colonnes.
- **c)** On a rangé directement les coordonnées de $f(\vec\imath+\vec\jmath)$ et $f(\vec\imath-\vec\jmath)$, comme si $\vec\imath+\vec\jmath$ et $\vec\imath-\vec\jmath$ étaient $\vec\imath$ et $\vec\jmath$.
- **d)** Erreur d'ordre dans la soustraction : on a calculé $f(\vec\jmath)$ comme $\dfrac12\big[f(\vec\imath-\vec\jmath)-f(\vec\imath+\vec\jmath)\big]=-\vec\imath-3\vec\jmath$.

</details>

Avis : 

---

## 142. `cqc-noyau-moyenne-2` (séries BAC:C BAC:E PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Remarque du relecteur :** LIMITE : noyau d'un endomorphisme de l'espace de dimension 3, à vérifier au programme de Première C/E (relève plutôt de Terminale C/E).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

L'espace vectoriel de dimension 3 est muni d'une base $(\vec{e_1},\vec{e_2},\vec{e_3})$. On considère l'endomorphisme $\varphi$ défini par
$$\varphi(x\vec{e_1}+y\vec{e_2}+z\vec{e_3})=(x+2y-z)\vec{e_1}+(2x+y+z)\vec{e_2}+(x-y+2z)\vec{e_3}.$$
Quel est le noyau de $\varphi$ ?

- a) $\{\vec 0\}$
- b) $\mathrm{Vect}(\vec{e_1}+\vec{e_2}+\vec{e_3})$
- c) Le plan d'équation $x+2y-z=0$
- d) $\mathrm{Vect}(\vec{e_1}-\vec{e_2}-\vec{e_3})$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Le noyau est l'ensemble des vecteurs dont l'image est le vecteur nul : on résout le système linéaire homogène obtenu en annulant chaque coordonnée de l'image, en tenant compte des TROIS équations. Si une équation est conséquence des autres, le noyau n'est pas réduit au vecteur nul.

### Corrigé

$x\vec{e_1}+y\vec{e_2}+z\vec{e_3}\in\ker\varphi$ si et seulement si
$$\begin{cases}x+2y-z=0\\2x+y+z=0\\x-y+2z=0\end{cases}$$
La première équation donne $z=x+2y$. En reportant dans la deuxième : $2x+y+x+2y=3x+3y=0$, donc $y=-x$, puis $z=x-2x=-x$. La troisième devient $x+x-2x=0$ : elle est toujours vérifiée.

Les solutions sont les triplets $(x\,;-x\,;-x)$, donc
$$\ker\varphi=\mathrm{Vect}(\vec{e_1}-\vec{e_2}-\vec{e_3}).$$
Vérification : $\varphi(\vec{e_1}-\vec{e_2}-\vec{e_3})=(1-2+1)\vec{e_1}+(2-1-1)\vec{e_2}+(1+1-2)\vec{e_3}=\vec 0$.

### Pourquoi les autres réponses sont fausses

- **a)** Le système admet des solutions non nulles, par exemple $(1\,;-1\,;-1)$ : la troisième équation est conséquence des deux premières.
- **b)** Erreur de signe : $\varphi(\vec{e_1}+\vec{e_2}+\vec{e_3})=2\vec{e_1}+4\vec{e_2}+2\vec{e_3}\neq\vec 0$.
- **c)** On n'a utilisé que la première équation ; les deux autres réduisent ce plan à une droite.

</details>

Avis : 

---

## 143. `cqc-point-fixe-elevee-5` (séries BAC:C BAC:E)

**Remarque du relecteur :** Le choix entre 2 et 3 exige de majorer u_n par 2 (récurrence) : piège assumé, pas une ambiguïté.

**Énoncé :**

Soit $(u_n)$ la suite définie par $u_0=1$ et, pour tout entier naturel $n$, $u_{n+1}=\dfrac{u_n^2+6}{5}$. On admet que $(u_n)$ est convergente.

Quelle est sa limite ?

- a) $2$
- b) $3$
- c) $-2$
- d) $+\infty$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Si $u_{n+1}=g(u_n)$ avec $g$ continue et si $(u_n)$ converge vers $\ell$, alors $\ell$ est un point fixe de $g$ : $g(\ell)=\ell$. Lorsque $g$ a plusieurs points fixes, il faut choisir le bon : on cherche un intervalle stable qui contient $u_0$ et un seul point fixe, ou l'on utilise le sens de variation de la suite.

### Corrigé

Points fixes de $g(x)=\dfrac{x^2+6}{5}$ : $\dfrac{x^2+6}{5}=x\iff x^2-5x+6=0\iff(x-2)(x-3)=0$, donc $\ell=2$ ou $\ell=3$.

$g$ est croissante sur $[0\,;+\infty[$, avec $g(1)=\dfrac75$ et $g(2)=2$. Par récurrence : si $1\leq u_n\leq2$, alors $\dfrac75\leq u_{n+1}\leq2$ ; comme $u_0=1$, on a $1\leq u_n\leq2$ pour tout $n$. De plus $u_1=\dfrac75>u_0$, et la croissance de $g$ transmet l'inégalité : $u_{n+1}\geq u_n$ pour tout $n$.

La suite est croissante et majorée par $2$, et sa limite $\ell$ vérifie $\ell\leq2$ : la seule valeur possible est $\ell=2$.

### Pourquoi les autres réponses sont fausses

- **b)** $3$ est aussi un point fixe, mais la suite reste majorée par $2$ : elle ne peut pas l'atteindre.
- **c)** Erreur de signe dans la résolution de $x^2-5x+6=0$, dont les racines sont $2$ et $3$ ; de plus $u_n\geq1$ pour tout $n$.
- **d)** Une suite croissante n'est pas forcément divergente : celle-ci est majorée par $2$, et l'énoncé admet sa convergence.

</details>

Avis : 

---

## 144. `cqc-probabilites-elevee-0` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PROBATOIRE:A)

**Remarque du relecteur :** LIMITE : probabilité conditionnelle « inversée » (formule de Bayes) pour le Probatoire A, à la limite haute.

**Énoncé :**

Dans un lycée, $60\,\%$ des élèves viennent en bus et les autres à pied. Parmi les élèves venant en bus, $10\,\%$ arrivent en retard ; parmi ceux venant à pied, $25\,\%$ arrivent en retard.

On choisit au hasard un élève arrivé en retard. Quelle est la probabilité qu'il soit venu en bus ?

- a) $0{,}1$
- b) $0{,}06$
- c) $0{,}375$
- d) $0{,}16$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On représente la situation par un arbre pondéré (événements $B$ : « venir en bus » et $R$ : « être en retard »). La probabilité de $R$ s'obtient par la formule des probabilités totales, en additionnant les probabilités des branches qui mènent à $R$. La probabilité cherchée est une probabilité conditionnelle « sachant $R$ » : $P_R(B)=\dfrac{P(B\cap R)}{P(R)}$, à ne pas confondre avec $P_B(R)$.

### Corrigé

$P(B)=0{,}6$, $P(\overline B)=0{,}4$, $P_B(R)=0{,}1$ et $P_{\overline B}(R)=0{,}25$.

$P(B\cap R)=0{,}6\times0{,}1=0{,}06$ et $P(\overline B\cap R)=0{,}4\times0{,}25=0{,}1$.

Probabilités totales : $P(R)=0{,}06+0{,}1=0{,}16$.
$$P_R(B)=\frac{P(B\cap R)}{P(R)}=\frac{0{,}06}{0{,}16}=0{,}375.$$

### Pourquoi les autres réponses sont fausses

- **a)** C'est $P_B(R)$, la probabilité d'être en retard sachant que l'élève vient en bus : le conditionnement est inversé.
- **b)** C'est $P(B\cap R)$ : on a oublié de diviser par $P(R)$, alors que l'on sait déjà que l'élève est en retard.
- **d)** C'est $P(R)$, la probabilité qu'un élève quelconque soit en retard.

</details>

Avis : 

---

## 145. `cqc-racine-evidente-elevee-0` (séries BAC:A BAC:C PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées BAC:A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Quel est l'ensemble des solutions réelles de l'équation $2x^3-3x^2-11x+6=0$ ?

- a) $\{-4\,;1\,;3\}$
- b) $\left\{-2\,;\dfrac12\,;3\right\}$
- c) $\left\{-\dfrac12\,;2\,;3\right\}$
- d) $\{3\}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On cherche une racine évidente en testant de petites valeurs entières (diviseurs du terme constant). Si $a$ est racine, le polynôme se factorise par $(x-a)$ : on trouve l'autre facteur par identification des coefficients, puis on résout ce facteur du second degré avec le discriminant, sans oublier le dénominateur $2a$ dans la formule des racines.

### Corrigé

Notons $P(x)=2x^3-3x^2-11x+6$. On teste : $P(1)=-6$, $P(2)=-12$, $P(3)=54-27-33+6=0$. Donc $3$ est racine.

On écrit $P(x)=(x-3)(2x^2+bx+c)=2x^3+(b-6)x^2+(c-3b)x-3c$. Par identification : $b-6=-3$ donc $b=3$ ; $-3c=6$ donc $c=-2$ ; contrôle : $c-3b=-2-9=-11$.

Pour $2x^2+3x-2=0$ : $\Delta=9+16=25$, d'où $x=\dfrac{-3-5}{4}=-2$ et $x=\dfrac{-3+5}{4}=\dfrac12$.

$$\mathcal S=\left\{-2\,;\dfrac12\,;3\right\}.$$

### Pourquoi les autres réponses sont fausses

- **a)** Les racines du facteur $2x^2+3x-2$ ont été calculées en divisant par $2$ au lieu de $2a=4$.
- **c)** Erreur de signe dans la factorisation : on a obtenu $2x^2-3x-2$ au lieu de $2x^2+3x-2$.
- **d)** On s'est arrêté à la racine évidente : le facteur du second degré a lui aussi deux racines réelles ($\Delta=25>0$).

</details>

Avis : 

---

## 146. `cqc-similitude-moyenne-0` (séries BAC:C BAC:E BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** Similitude directe et écriture complexe : Terminale C/E, pas au programme du Probatoire C/E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan complexe est muni d'un repère orthonormé direct. On considère la similitude directe $s$ d'écriture complexe $z'=(1+i)z+2$.

Quels sont le rapport, l'angle et le centre de $s$ ?

- a) Rapport $2$, angle $\dfrac\pi4$, centre d'affixe $2i$
- b) Rapport $\sqrt2$, angle $\dfrac\pi4$, centre d'affixe $2i$
- c) Rapport $\sqrt2$, angle $\dfrac\pi4$, centre d'affixe $-2i$
- d) Rapport $\sqrt2$, angle $\dfrac\pi4$, centre d'affixe $-1+i$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une similitude directe d'écriture $z'=az+b$ avec $a\neq1$ : le rapport est $|a|$, une mesure de l'angle est $\arg a$, et le centre $\Omega$ est l'unique point invariant, dont l'affixe $\omega$ vérifie $\omega=a\omega+b$, soit $\omega=\dfrac{b}{1-a}$.

### Corrigé

Ici $a=1+i$ et $b=2$.

Rapport : $|1+i|=\sqrt{1^2+1^2}=\sqrt2$. Angle : $1+i=\sqrt2\left(\dfrac{\sqrt2}2+i\dfrac{\sqrt2}2\right)$, donc $\arg(1+i)=\dfrac\pi4$.

Centre : $\omega=(1+i)\omega+2\iff-i\omega=2\iff\omega=\dfrac{2}{-i}=2i$.

Vérification : $(1+i)\times2i+2=2i-2+2=2i$.

$s$ est la similitude de rapport $\sqrt2$, d'angle $\dfrac\pi4$ et de centre le point d'affixe $2i$.

### Pourquoi les autres réponses sont fausses

- **a)** Le module de $1+i$ est $\sqrt{1^2+1^2}=\sqrt2$, et non $1+1=2$.
- **c)** Erreur de signe en isolant $\omega$ : on a écrit $i\omega=2$ au lieu de $-i\omega=2$.
- **d)** On a pris $\omega=\dfrac{-b}{a}=\dfrac{-2}{1+i}=-1+i$ (antécédent de $0$) au lieu de résoudre $\omega=a\omega+b$.

</details>

Avis : 

---

## 147. `cqc-symetrie-centrale-faible-1` (séries BAC:C BAC:E)

**Énoncé :**

Dans un repère du plan, on donne les points $A(3\,;-1)$ et $\Omega(1\,;2)$. Quelles sont les coordonnées du point $A'$, image de $A$ par la symétrie centrale de centre $\Omega$ ?

- a) $(2\,;0{,}5)$
- b) $(-3\,;1)$
- c) $(5\,;-4)$
- d) $(-1\,;5)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Par la symétrie de centre $\Omega$, le point $A'$ est tel que $\Omega$ est le milieu de $[AA']$, c'est-à-dire $\overrightarrow{\Omega A'}=-\overrightarrow{\Omega A}$. On en déduit $x_{A'}=2x_\Omega-x_A$ et $y_{A'}=2y_\Omega-y_A$.

### Corrigé

$\Omega$ est le milieu de $[AA']$ :
$$x_{A'}=2\times1-3=-1,\qquad y_{A'}=2\times2-(-1)=5.$$
Contrôle : le milieu de $[AA']$ est $\left(\dfrac{3+(-1)}{2}\,;\dfrac{-1+5}{2}\right)=(1\,;2)=\Omega$.

$A'(-1\,;5)$.

### Pourquoi les autres réponses sont fausses

- **a)** Ce sont les coordonnées du milieu de $[A\Omega]$, pas celles du symétrique de $A$.
- **b)** C'est le symétrique de $A$ par rapport à l'origine $O$, et non par rapport à $\Omega$.
- **c)** Les rôles de $A$ et $\Omega$ ont été échangés : on a calculé $2x_A-x_\Omega$ et $2y_A-y_\Omega$ (symétrique de $\Omega$ par rapport à $A$).

</details>

Avis : 

---

## 148. `cqc-tangente-a-une-courbe-moyenne-2` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:A)

**Remarque du relecteur :** LIMITE : tangente pour Probatoire A.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=x^2-4x+1$, de courbe représentative $(C)$.

Quelle est l'équation de la tangente à $(C)$ parallèle à la droite d'équation $y=2x+5$ ?

- a) $y=2x-6$
- b) $y=2x-8$
- c) $y=2x+4$
- d) $y=-2x+4$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Deux droites non verticales sont parallèles si et seulement si elles ont le même coefficient directeur. Le coefficient directeur de la tangente au point d'abscisse $a$ est $f'(a)$ : on résout $f'(a)=2$, puis on écrit $y=f'(a)(x-a)+f(a)$.

### Corrigé

$f'(x)=2x-4$. On résout $f'(a)=2$ : $2a-4=2$, donc $a=3$. Puis $f(3)=9-12+1=-2$.

$$y=f'(3)(x-3)+f(3)=2(x-3)-2=2x-8.$$

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié d'ajouter $f(3)=-2$ : $y=2(x-3)$ ne passe pas par le point de contact $(3\,;-2)$.
- **c)** Erreur de signe dans $x-a$ : on a écrit $2(x+3)-2$ au lieu de $2(x-3)-2$.
- **d)** On a pris $f(3)=-2$ comme coefficient directeur à la place de $f'(3)=2$.

</details>

Avis : 

---

## 149. `cqc-variable-aleatoire-moyenne-2` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:C)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On lance un dé équilibré à six faces. Si l'on obtient $6$, on gagne $3$ points ; si l'on obtient $4$ ou $5$, on gagne $1$ point ; sinon, on perd $1$ point. On note $X$ le gain algébrique (en points).

Quelle est l'espérance mathématique de $X$ ?

- a) $1$
- b) $\dfrac56$
- c) $\dfrac13$
- d) $\dfrac16$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On établit d'abord la loi de $X$ : la liste de ses valeurs possibles et la probabilité de chacune, en comptant le nombre de faces qui donnent chaque valeur. L'espérance est la somme des produits « valeur $\times$ probabilité » : $E(X)=\sum x_i\,P(X=x_i)$. Ce n'est pas la moyenne simple des valeurs possibles.

### Corrigé

Loi de $X$ : $P(X=3)=\dfrac16$ (face $6$), $P(X=1)=\dfrac26$ (faces $4$ et $5$), $P(X=-1)=\dfrac36$ (faces $1$, $2$, $3$). Contrôle : $\dfrac16+\dfrac26+\dfrac36=1$.
$$E(X)=3\times\frac16+1\times\frac26+(-1)\times\frac36=\frac{3+2-3}{6}=\frac26=\frac13.$$

### Pourquoi les autres réponses sont fausses

- **a)** C'est la moyenne simple des trois valeurs $\dfrac{3+1-1}{3}$ : on n'a pas tenu compte de leurs probabilités.
- **b)** On a oublié la perte : seuls les gains $\dfrac36+\dfrac26$ ont été comptés.
- **d)** On a affecté la probabilité $\dfrac16$ à « $4$ ou $5$ » alors que deux faces conviennent : $\dfrac26$.

</details>

Avis : 

---

## 150. `cqc-ajustement-affine-elevee-0` (séries BAC:A BAC:C BAC:D BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** L'énoncé ne dit pas de ranger les points par abscisses croissantes ; en coupant dans l'ordre du tableau on obtient y=8x-8 et 64, qui figure au choix b. Ajouter « après avoir rangé les points par valeurs croissantes de x ».

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une coopérative a relevé, sur six mois, ses dépenses de publicité $x$ (en centaines de milliers de francs CFA) et son chiffre d'affaires $y$ (en millions de francs CFA) :

| Dépenses de publicité ($x$) | 4 | 1 | 6 | 2 | 5 | 3 |
|---|---|---|---|---|---|---|
| Chiffre d'affaires ($y$) | 23 | 11 | 30 | 14 | 25 | 17 |

On ajuste ce nuage par la droite de Mayer, en rangeant d'abord les points par valeurs croissantes de $x$, puis en partageant la série en deux groupes de trois points.

Quelle estimation du chiffre d'affaires cette droite donne-t-elle pour des dépenses de publicité $x=9$ ?

- a) $42$ millions
- b) $64$ millions
- c) $41{,}4$ millions
- d) $36$ millions

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour la méthode de Mayer, on range d'abord les points dans l'ordre croissant des $x$, puis on partage la série en deux groupes de même effectif. On calcule les points moyens $G_1$ et $G_2$ de chaque groupe ; la droite de Mayer est la droite $(G_1G_2)$, d'équation $y=ax+b$ avec $a=\dfrac{y_{G_2}-y_{G_1}}{x_{G_2}-x_{G_1}}$ et $b=y_{G_1}-a\,x_{G_1}$.

### Corrigé

Points rangés selon $x$ croissant : $(1;11)$, $(2;14)$, $(3;17)$ | $(4;23)$, $(5;25)$, $(6;30)$.

$G_1\left(\dfrac{1+2+3}{3};\dfrac{11+14+17}{3}\right)=(2;14)$ et $G_2\left(\dfrac{4+5+6}{3};\dfrac{23+25+30}{3}\right)=(5;26)$.

$$a=\dfrac{26-14}{5-2}=\dfrac{12}{3}=4,\qquad b=14-4\times2=6.$$

La droite de Mayer a pour équation $y=4x+6$. Pour $x=9$ : $y=4\times9+6=42$.

**On estime le chiffre d'affaires à $42$ millions de francs CFA** (estimation par extrapolation, puisque $x=9$ dépasse les valeurs observées).

### Pourquoi les autres réponses sont fausses

- **b)** $64$ millions : les groupes ont été formés dans l'ordre du tableau, sans ranger les $x$ ; on obtient alors la droite $y=8x-8$.
- **c)** $41{,}4$ millions : c'est la droite passant par les deux points extrêmes $(1;11)$ et $(6;30)$, qui n'est pas la droite de Mayer.
- **d)** $36$ millions : l'ordonnée à l'origine $b=6$ a été oubliée ($4\times9=36$).

</details>

Avis : 

---

## 151. `cqc-covariance-prob-c-moyenne-3` (séries BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Un agronome étudie quatre parcelles de maïs. Il note $x$ la quantité d'engrais apportée (en sacs) et $y$ le rendement obtenu (en tonnes) :

| $x$ | 2 | 4 | 6 | 8 |
|---|---|---|---|---|
| $y$ | 5 | 4 | 7 | 8 |

Quelle est la covariance $\operatorname{cov}(x,y)$ de cette série ?

- a) $12$
- b) $33$
- c) $3$
- d) $4$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une série de $n$ couples, $\operatorname{cov}(x,y)=\dfrac1n\sum x_iy_i-\bar x\,\bar y$ : c'est la moyenne des produits, diminuée du produit des moyennes.

### Corrigé

$\bar x=\dfrac{2+4+6+8}{4}=5$ et $\bar y=\dfrac{5+4+7+8}{4}=6$.

$\sum x_iy_i=10+16+42+64=132$, donc $\dfrac1n\sum x_iy_i=\dfrac{132}{4}=33$.

$$\operatorname{cov}(x,y)=33-5\times6=3.$$

**La covariance vaut $3$.**

### Pourquoi les autres réponses sont fausses

- **a)** $12=132-4\times30$ : on a oublié de diviser la somme des écarts par l'effectif $n=4$.
- **b)** $33$ est la moyenne des produits $x_iy_i$ ; il manque la soustraction de $\bar x\,\bar y=30$.
- **d)** $4=\dfrac{12}{3}$ : on a divisé par $n-1$ au lieu de $n$.

</details>

Avis : 

---

## 152. `cqc-determinant-prob-c-elevee-5` (séries PROBATOIRE:C PROBATOIRE:E)

**Énoncé :**

Soit $m$ un réel. On considère le système d'inconnues réelles $x$ et $y$ :
$$\begin{cases} mx+2y=1\\ 8x+my=2\end{cases}$$
Pour quelle(s) valeur(s) de $m$ ce système n'admet-il **aucune** solution ?

- a) $m=4$
- b) $m=-4$
- c) $m\in\{-4\,;4\}$
- d) Pour aucune valeur de $m$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Un système linéaire de deux équations à deux inconnues admet une solution unique si et seulement si son déterminant est non nul. Quand le déterminant est nul, les deux équations ont des premiers membres proportionnels : le système a soit une infinité de solutions (seconds membres dans le même rapport), soit aucune solution (seconds membres dans un autre rapport). Il faut donc examiner chaque valeur qui annule le déterminant.

### Corrigé

Le déterminant du système est $\begin{vmatrix} m&2\\8&m\end{vmatrix}=m^2-16$ ; il s'annule pour $m=4$ ou $m=-4$.

- Pour $m=4$ : le système s'écrit $4x+2y=1$ et $8x+4y=2$. La seconde équation est le double de la première : infinité de solutions.
- Pour $m=-4$ : $-4x+2y=1$ et $8x-4y=2$. En multipliant la première par $-2$, on obtient $8x-4y=-2$, incompatible avec $8x-4y=2$ : aucune solution.

Pour $m\neq\pm4$, la solution est unique.

**Le système n'a aucune solution pour $m=-4$ seulement.**

### Pourquoi les autres réponses sont fausses

- **a)** pour $m=4$, les deux équations sont équivalentes : il y a une infinité de solutions, pas zéro.
- **c)** un déterminant nul ne suffit pas à conclure à l'absence de solution : il faut examiner les seconds membres pour chaque valeur.
- **d)** « aucune valeur » vient d'un déterminant mal calculé ($m^2+16$, qui ne s'annule jamais).

</details>

Avis : 

---

## 153. `cqc-forme-algebrique-d-un-quotient-faible-0` (séries BAC:A BAC:D)

**Séries modifiées :** retirées BAC:A.

**Remarque du relecteur :** Nombres complexes hors programme de la série A (BAC A listé).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On considère les nombres complexes $z_1=2+3i$ et $z_2=1-i$.

Quelle est la forme algébrique du nombre complexe $Z=\dfrac{z_1}{z_2}$ ?

- a) $Z=2-3i$
- b) $Z=\dfrac52+\dfrac52i$
- c) $Z=-1+5i$
- d) $Z=-\dfrac12+\dfrac52i$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour mettre un quotient sous forme algébrique, on multiplie le numérateur et le dénominateur par le conjugué du dénominateur : $z_2\,\bar z_2=|z_2|^2$ est un réel strictement positif. On n'oublie pas que $i^2=-1$.

### Corrigé

$\bar z_2=1+i$ et $z_2\bar z_2=1^2+1^2=2$.

$$Z=\dfrac{(2+3i)(1+i)}{(1-i)(1+i)}=\dfrac{2+2i+3i+3i^2}{2}=\dfrac{2+5i-3}{2}=\dfrac{-1+5i}{2}.$$

Vérification : $z_2\times Z=(1-i)\left(-\dfrac12+\dfrac52i\right)=-\dfrac12+\dfrac52i+\dfrac12i+\dfrac52=2+3i=z_1$.

**$Z=-\dfrac12+\dfrac52i$.**

### Pourquoi les autres réponses sont fausses

- **a)** $2-3i$ divise partie réelle par partie réelle et partie imaginaire par partie imaginaire, ce qui n'a pas de sens pour un quotient.
- **b)** $\dfrac52+\dfrac52i$ vient de $3i^2$ compté comme $+3$ : on a oublié que $i^2=-1$.
- **c)** $-1+5i$ est le numérateur $(2+3i)(1+i)$ ; on a oublié de diviser par $z_2\bar z_2=2$.

</details>

Avis : 

---

## 154. `cqc-linearite-moyenne-4` (séries PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan vectoriel est muni d'une base $(\vec\imath,\vec\jmath)$. Une application linéaire $f$ du plan vectoriel dans lui-même vérifie
$$f(\vec\imath)=2\vec\imath+\vec\jmath\qquad\text{et}\qquad f(\vec\jmath)=-\vec\imath+3\vec\jmath.$$
Quelles sont les coordonnées de $f(3\vec\imath-2\vec\jmath)$ ?

- a) $(4\,;9)$
- b) $(8\,;-3)$
- c) $(6\,;-6)$
- d) $(1\,;4)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Par linéarité, $f(\lambda\vec u+\mu\vec v)=\lambda f(\vec u)+\mu f(\vec v)$. Il suffit donc de connaître les images des vecteurs de la base pour obtenir l'image de n'importe quel vecteur, en gardant les coefficients et leurs signes.

### Corrigé

$$f(3\vec\imath-2\vec\jmath)=3f(\vec\imath)-2f(\vec\jmath)=3(2\vec\imath+\vec\jmath)-2(-\vec\imath+3\vec\jmath)=6\vec\imath+3\vec\jmath+2\vec\imath-6\vec\jmath=8\vec\imath-3\vec\jmath.$$

**$f(3\vec\imath-2\vec\jmath)$ a pour coordonnées $(8\,;-3)$.**

### Pourquoi les autres réponses sont fausses

- **a)** $(4\,;9)$ : le signe de $-2$ a été mal distribué, $-2\times(-1)$ compté comme $-2$ et $-2\times3$ compté comme $+6$.
- **c)** $(6\,;-6)$ multiplie coordonnée par coordonnée au lieu d'utiliser la linéarité.
- **d)** $(1\,;4)$ est $f(\vec\imath)+f(\vec\jmath)$ : les coefficients $3$ et $-2$ ont été oubliés.

</details>

Avis : 

---

## 155. `cqc-matrice-d-un-endomorphisme-tle-c-moyenne-4` (séries BAC:C BAC:E PROBATOIRE:C)

**Séries modifiées :** retirées PROBATOIRE:C.

**Remarque du relecteur :** LIMITE : matrice d'une composée d'applications linéaires, à vérifier au programme de Première C (plutôt Terminale C/E).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan vectoriel est rapporté à sa base canonique. Soit $f$ l'application linéaire définie par
$$f(x\,;y)=(2x-y\,;\,3x+4y).$$
Quelle est la matrice de $f\circ f$ dans la base canonique ?

- a) $\begin{pmatrix}4&1\\9&16\end{pmatrix}$
- b) $\begin{pmatrix}4&-2\\6&8\end{pmatrix}$
- c) $\begin{pmatrix}1&-6\\18&13\end{pmatrix}$
- d) $\begin{pmatrix}1&18\\-6&13\end{pmatrix}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Les colonnes de la matrice $M$ de $f$ sont les coordonnées de $f(\vec\imath)$ et de $f(\vec\jmath)$. La matrice de $f\circ f$ est le produit $M\times M$, calculé ligne par colonne (et non coefficient par coefficient).

### Corrigé

$f(\vec\imath)=f(1;0)=(2;3)$ et $f(\vec\jmath)=f(0;1)=(-1;4)$, donc
$$M=\begin{pmatrix}2&-1\\3&4\end{pmatrix}.$$

$$M^2=\begin{pmatrix}2\times2+(-1)\times3 & 2\times(-1)+(-1)\times4\\ 3\times2+4\times3 & 3\times(-1)+4\times4\end{pmatrix}=\begin{pmatrix}1&-6\\18&13\end{pmatrix}.$$

Vérification : $f(1;2)=(0;11)$ puis $f(0;11)=(-11;44)$, et $M^2\begin{pmatrix}1\\2\end{pmatrix}=\begin{pmatrix}1-12\\18+26\end{pmatrix}=\begin{pmatrix}-11\\44\end{pmatrix}$.

**La matrice de $f\circ f$ est $\begin{pmatrix}1&-6\\18&13\end{pmatrix}$.**

### Pourquoi les autres réponses sont fausses

- **a)** élever chaque coefficient au carré ne donne pas le produit de matrices $M\times M$.
- **b)** $2M$ correspond à $2f$, pas à la composée $f\circ f$.
- **d)** c'est la transposée du bon résultat : les images des vecteurs de base ont été écrites en lignes au lieu de colonnes.

</details>

Avis : 

---

## 156. `cqc-nuage-de-points-elevee-0` (séries BAC:A BAC:D BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Un agronome étudie un nuage de $8$ points $(x_i\,;y_i)$, où $x$ est la quantité d'eau d'irrigation et $y$ le rendement de $8$ parcelles. Pour les $3$ parcelles de la zone Nord, le point moyen est $G_1(2\,;5)$ ; pour les $5$ parcelles de la zone Sud, le point moyen est $G_2(10\,;13)$.

Quelles sont les coordonnées du point moyen $G$ du nuage des $8$ points ?

- a) $(7\,;10)$
- b) $(6\,;9)$
- c) $(5\,;8)$
- d) $(56\,;80)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Le point moyen d'un nuage a pour coordonnées $(\bar x\,;\bar y)$. Si le nuage est formé de deux groupes d'effectifs $n_1$ et $n_2$, de points moyens $G_1$ et $G_2$, alors $\bar x=\dfrac{n_1x_{G_1}+n_2x_{G_2}}{n_1+n_2}$ (et de même pour $\bar y$) : chaque groupe pèse selon son effectif.

### Corrigé

La somme des abscisses du groupe Nord est $3\times2=6$ et celle du groupe Sud est $5\times10=50$ :
$$\bar x=\dfrac{6+50}{8}=7.$$
De même pour les ordonnées : $3\times5=15$ et $5\times13=65$, donc
$$\bar y=\dfrac{15+65}{8}=10.$$

**$G(7\,;10)$.**

### Pourquoi les autres réponses sont fausses

- **b)** $(6\,;9)$ est le milieu de $[G_1G_2]$ : on a oublié que les deux groupes n'ont pas le même effectif.
- **c)** $(5\,;8)$ inverse les effectifs, en affectant le poids $5$ à $G_1$ et le poids $3$ à $G_2$.
- **d)** $(56\,;80)$ donne les sommes des coordonnées, sans diviser par l'effectif total $8$.

</details>

Avis : 

---

## 157. `cqc-probabilites-faible-0` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PROBATOIRE:A)

**Remarque du relecteur :** LIMITE : événements indépendants pour le Probatoire A, notion plutôt de Terminale.

**Énoncé :**

Un cultivateur sème deux graines de haricot. Chaque graine germe avec la probabilité $0{,}8$, indépendamment de l'autre.

Quelle est la probabilité qu'au moins une des deux graines germe ?

- a) $0{,}64$
- b) $0{,}96$
- c) $0{,}32$
- d) $0{,}04$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour « au moins une », on passe par l'événement contraire « aucune » : $P(\text{au moins une})=1-P(\text{aucune})$. Pour des événements indépendants, la probabilité qu'ils se réalisent tous deux est le produit de leurs probabilités.

### Corrigé

Chaque graine ne germe pas avec la probabilité $1-0{,}8=0{,}2$. Par indépendance :
$$P(\text{aucune ne germe})=0{,}2\times0{,}2=0{,}04.$$
Donc
$$P(\text{au moins une germe})=1-0{,}04=0{,}96.$$

**La probabilité cherchée est $0{,}96$.**

### Pourquoi les autres réponses sont fausses

- **a)** $0{,}64=0{,}8\times0{,}8$ est la probabilité que les DEUX graines germent.
- **c)** $0{,}32=2\times0{,}8\times0{,}2$ est la probabilité qu'EXACTEMENT une graine germe ; il manque le cas où les deux germent.
- **d)** $0{,}04$ est la probabilité qu'aucune ne germe, c'est-à-dire de l'événement contraire.

</details>

Avis : 

---

## 158. `cqc-racine-evidente-faible-0` (séries BAC:A BAC:C PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées BAC:A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On considère le polynôme $P(x)=2x^3-3x^2-11x+6$. On sait que $P$ admet une racine entière comprise entre $-2$ et $2$.

Laquelle des écritures suivantes est une factorisation de $P(x)$ ?

- a) $(x+2)(2x^2-7x+3)$
- b) $(x-2)(2x^2+x-3)$
- c) $(x+2)(2x^2+x-3)$
- d) $(x+2)(2x^2-7x-3)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On cherche une racine évidente $a$ en testant les entiers proposés : si $P(a)=0$, alors $P(x)=(x-a)Q(x)$ avec $Q$ du second degré. On trouve $Q$ par identification des coefficients (ou division), et on contrôle en redéveloppant.

### Corrigé

$P(1)=2-3-11+6=-6$, $P(-1)=-2-3+11+6=12$, $P(2)=16-12-22+6=-12$, $P(-2)=-16-12+22+6=0$.

$-2$ est racine : $P(x)=(x+2)(ax^2+bx+c)$. En développant : $ax^3+(b+2a)x^2+(c+2b)x+2c$. Par identification : $a=2$, $b+4=-3$ donc $b=-7$, $2c=6$ donc $c=3$ (et $c+2b=3-14=-11$ convient).

**$P(x)=(x+2)(2x^2-7x+3)$.**

### Pourquoi les autres réponses sont fausses

- **b)** $2$ n'est pas racine ($P(2)=-12$) ; d'ailleurs ce produit vaut $2x^3-3x^2-5x+6$.
- **c)** erreur dans l'identification du coefficient de $x^2$ : ce produit vaut $2x^3+5x^2-x-6$.
- **d)** erreur de signe sur le terme constant : ce produit vaut $2x^3-3x^2-17x-6$.

</details>

Avis : 

---

## 159. `cqc-similitude-moyenne-1` (séries BAC:C BAC:E BAC:TI PROBATOIRE:C PROBATOIRE:E)

**Séries modifiées :** retirées PROBATOIRE:C, PROBATOIRE:E.

**Remarque du relecteur :** Similitudes directes en écriture complexe : programme de Terminale, hors niveau pour le Probatoire C et E listés.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan complexe est rapporté à un repère orthonormé direct. On considère la similitude directe $s$ qui, au point d'affixe $z$, associe le point d'affixe
$$z'=(1+i)z+2-i.$$
Quelle est l'affixe $\omega$ du centre de $s$ ?

- a) $\omega=1+2i$
- b) $\omega=-1-2i$
- c) $\omega=2-i$
- d) $\omega=\dfrac35-\dfrac45i$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Le centre d'une similitude directe $z'=az+b$ (avec $a\neq1$) est son unique point invariant : son affixe $\omega$ vérifie $\omega=a\omega+b$, soit $\omega=\dfrac{b}{1-a}$.

### Corrigé

$$\omega=(1+i)\omega+2-i\iff -i\,\omega=2-i\iff\omega=\dfrac{2-i}{-i}=\dfrac{(2-i)\times i}{-i\times i}=\dfrac{2i+1}{1}=1+2i.$$

Vérification : $(1+i)(1+2i)+2-i=1+2i+i-2+2-i=1+2i$.

**$\omega=1+2i$** (la similitude a pour rapport $|1+i|=\sqrt2$ et pour angle $\dfrac\pi4$).

### Pourquoi les autres réponses sont fausses

- **b)** $-1-2i=\dfrac{-b}{1-a}$ : erreur de signe en isolant $\omega$.
- **c)** $2-i$ est le coefficient $b$, c'est-à-dire l'image du point $O$, pas le centre.
- **d)** $\dfrac35-\dfrac45i=\dfrac{b}{1+a}$ : on a écrit $\omega+a\omega=b$ au lieu de $\omega-a\omega=b$.

</details>

Avis : 

---

## 160. `cqc-variable-aleatoire-moyenne-3` (séries BAC:A BAC:C BAC:D BAC:E PROBATOIRE:C)

**Séries modifiées :** retirées PROBATOIRE:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

À une kermesse, un joueur paie $200$ F pour lancer un dé équilibré à six faces. S'il obtient $6$, il reçoit $1\,500$ F ; s'il obtient $4$ ou $5$, il reçoit $300$ F ; sinon il ne reçoit rien. On note $X$ le gain algébrique du joueur (somme reçue moins la mise).

Quelle est l'espérance mathématique $E(X)$ ?

- a) $350$ F
- b) $150$ F
- c) $400$ F
- d) $250$ F

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On détermine d'abord les valeurs prises par la variable aléatoire (ici en tenant compte de la mise dans CHAQUE cas, y compris quand le joueur perd), puis sa loi de probabilité ; enfin $E(X)=\sum x_i\,P(X=x_i)$.

### Corrigé

- Obtenir $6$ : $X=1\,500-200=1\,300$, avec la probabilité $\dfrac16$.
- Obtenir $4$ ou $5$ : $X=300-200=100$, avec la probabilité $\dfrac26$.
- Obtenir $1$, $2$ ou $3$ : $X=-200$, avec la probabilité $\dfrac36$.

$$E(X)=1\,300\times\dfrac16+100\times\dfrac26-200\times\dfrac36=\dfrac{1\,300+200-600}{6}=\dfrac{900}{6}=150.$$

**$E(X)=150$ F** : en moyenne, sur un grand nombre de parties, le joueur gagne $150$ F par partie.

### Pourquoi les autres réponses sont fausses

- **a)** $350$ F est l'espérance de la somme REÇUE ; on a oublié de retrancher la mise de $200$ F.
- **c)** $400$ F est la moyenne simple des trois valeurs $1\,300$, $100$ et $-200$, sans tenir compte de leurs probabilités.
- **d)** $250$ F compte un gain nul au lieu de $-200$ F lorsque le joueur ne reçoit rien.

</details>

Avis : 

---

## 161. `cqc-equation-du-premier-degre-faible-0` (séries BAC:A BEPC: PROBATOIRE:A PROBATOIRE:C PROBATOIRE:E)

**Énoncé :**

Une mère a aujourd'hui quatre fois l'âge de sa fille. Dans $20$ ans, elle n'aura plus que le double de l'âge de sa fille.

Quel est l'âge actuel de la fille ?

- a) $20$ ans
- b) $40$ ans
- c) $10$ ans
- d) $30$ ans

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On choisit l'inconnue, on exprime chaque âge AUJOURD'HUI puis DANS $20$ ans (les deux personnes vieillissent de $20$ ans), on traduit la phrase par une équation du premier degré, on la résout, puis on vérifie dans l'énoncé.

### Corrigé

Notons $x$ l'âge actuel de la fille ; la mère a $4x$ ans. Dans $20$ ans, la fille aura $x+20$ ans et la mère $4x+20$ ans :
$$4x+20=2(x+20)\iff4x+20=2x+40\iff2x=20\iff x=10.$$

Vérification : aujourd'hui $10$ ans et $40$ ans ; dans $20$ ans, $30$ ans et $60$ ans, et $60=2\times30$.

**La fille a $10$ ans.**

### Pourquoi les autres réponses sont fausses

- **a)** $20$ ans vient de l'équation $4x=2(x+20)$ : on a oublié que la mère vieillit aussi de $20$ ans.
- **b)** $40$ ans est l'âge actuel de la MÈRE, pas celui de la fille.
- **d)** $30$ ans vient d'une erreur de signe : $2x=40+20$ au lieu de $2x=40-20$.

</details>

Avis : 

---

