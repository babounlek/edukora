# Maths Probatoire, vague 2 : questions a faire relire par l'enseignant (campagne B1)

Date : 2026-10-27. La vague 2 compte 93 QCM (series A, C, D, E) ; **aucun n'est en ligne**. 92 sur 93 sont en accord avec la cle chez un relecteur independant. Ce document ne retient que ce qu'un relecteur modele juge mal : les 19 questions signalees (limite du programme de Premiere, vocabulaire, doublons, methode remplacee) puis 12 questions tirees au hasard (graine fixe) pour mesurer le taux de rejet sur le reste. Le referentiel officiel (module 23 : geometrie analytique, barycentres, transformations affines, espaces vectoriels, matrices ; module 24 : geometrie dans l'espace) couvre les series C et E ; la serie D n'a que barycentres et transformations affines ; le theoreme de la mediane et le produit scalaire ne sont pas nommes.

Pour chaque question : **OK**, **a corriger** (dire quoi) ou **a retirer**.

## 1. `cqc-linearite-elevee-5` (series C/E)

**A regarder :** VOCABULAIRE : « endomorphisme de R² » est rare en Première ; un manuel dit plutôt « application linéaire du plan vectoriel » rapportée à une base.

**Enonce :**

Soit $f$ un endomorphisme de $\mathbb{R}^2$ tel que $f(1,1)=(3,2)$ et $f(1,-1)=(1,4)$. Quelle est l'expression de $f(x,y)$ pour tout $(x,y)\in\mathbb{R}^2$ ?

- a) $f(x,y)=(2x+3y,\;x-y)$
- b) $f(x,y)=(2x-y,\;3x+y)$
- c) $f(x,y)=(2x+y,\;3x-y)$
- d) $f(x,y)=(3x+y,\;2x+4y)$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Une application linéaire est entièrement déterminée par les images d'une base. On exprime la base canonique à l'aide des vecteurs dont l'image est connue, puis on applique la linéarité.

### Corrigé

Soit $e_1=(1,0)$, $e_2=(0,1)$, $a=(1,1)$, $b=(1,-1)$. On a $e_1=\tfrac12(a+b)$ et $e_2=\tfrac12(a-b)$.

Par linéarité :
$$f(e_1)=\tfrac12\big((3,2)+(1,4)\big)=(2,3),\qquad f(e_2)=\tfrac12\big((3,2)-(1,4)\big)=(1,-1).$$

Donc $f(x,y)=xf(e_1)+yf(e_2)=(2x+y,\;3x-y)$.

Vérification : $f(1,1)=(3,2)$ et $f(1,-1)=(1,4)$.

### Pourquoi les autres réponses sont fausses

- **a)** Les coordonnées de $f(e_1)=(2,3)$ et $f(e_2)=(1,-1)$ ont été rangées en lignes au lieu de colonnes : on obtiendrait $f(1,1)=(5,0)$.
- **b)** Erreur de signe : on a pris $e_2=\tfrac12(b-a)$, d'où $f(e_2)=(-1,1)$ ; on obtiendrait $f(1,1)=(1,4)$.
- **d)** On a pris $(3,2)$ et $(1,4)$ pour les images de $e_1$ et $e_2$, alors que $(1,1)$ et $(1,-1)$ ne sont pas les vecteurs de la base canonique.

</details>

Avis : 

---

## 2. `cqc-interets-composes-prob-d-elevee-5` (series D)

**A regarder :** LIMITE : suite arithmético-géométrique sans suite auxiliaire indiquée ; l'élève peut toutefois éliminer les choix en testant n=0, 1, 2.

**Enonce :**

On place $500\,000$ F à $6\ \%$ par an à intérêts composés et on ajoute $30\,000$ F à la fin de chaque année. On note $C_n$ le capital après $n$ années : $C_0=500\,000$ et $C_{n+1}=1{,}06\,C_n+30\,000$. Quelle est l'expression de $C_n$ en fonction de $n$ ?

- a) $C_n=500\,000\times1{,}06^n+30\,000\,n$
- b) $C_n=1\,000\,000\times1{,}06^n+500\,000$
- c) $C_n=500\,000\times1{,}06^n-500\,000$
- d) $C_n=1\,000\,000\times1{,}06^n-500\,000$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Pour une suite $C_{n+1}=aC_n+b$ avec $a\neq1$, on cherche le réel $\ell$ tel que $\ell=a\ell+b$ : ici $\ell=\dfrac{30\,000}{1-1{,}06}=-500\,000$. La suite $D_n=C_n-\ell=C_n+500\,000$ est alors géométrique de raison $1{,}06$.

### Corrigé

$D_{n+1}=C_{n+1}+500\,000=1{,}06C_n+530\,000=1{,}06\,(C_n+500\,000)=1{,}06\,D_n$ : suite géométrique de raison $1{,}06$ et de premier terme $D_0=C_0+500\,000=1\,000\,000$.

Donc $D_n=1\,000\,000\times1{,}06^n$ et $C_n=1\,000\,000\times1{,}06^n-500\,000$.

Vérification : $C_1=1{,}06\times500\,000+30\,000=560\,000$ et $1\,000\,000\times1{,}06-500\,000=560\,000$.
Par exemple, arrondi au franc : $C_5=1\,000\,000\times1{,}3382256-500\,000\approx838\,226$ F.

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié que les versements de $30\,000$ F rapportent eux aussi des intérêts : dès $n=2$, la formule donne $621\,800$ F au lieu de $623\,600$ F.
- **b)** Erreur de signe : $D_n=C_n+500\,000$ donne $C_n=D_n-500\,000$ ; ici $C_0$ vaudrait $1\,500\,000$ F.
- **c)** On a pris $D_0=C_0=500\,000$ au lieu de $D_0=C_0+500\,000$ : cette formule donne $C_0=0$.

</details>

Avis : 

---

## 3. `cqc-theoreme-de-la-mediane-prob-d-moyenne-4` (series D)

**A regarder :** LIMITE : relève du théorème de la médiane / produit scalaire (absent du référentiel, à signaler), mais résoluble en série D par le calcul analytique en coordonnées.

**Enonce :**

Dans un repère orthonormé, on donne $A(0\,;0)$ et $B(4\,;0)$. Pour un réel $k$, on note $E_k$ l'ensemble des points $M$ tels que $MA^2+MB^2=k$. Quelle discussion suivant les valeurs de $k$ est correcte ?

- a) Cercle de centre $I(2\,;0)$ si $k>16$, le point $I$ si $k=16$, ensemble vide si $k<16$
- b) Cercle de centre $I(2\,;0)$ si $k>4$, le point $I$ si $k=4$, ensemble vide si $k<4$
- c) Cercle de centre $I(2\,;0)$ si $k>8$, le point $I$ si $k=8$, ensemble vide si $k<8$
- d) Cercle de centre $I(2\,;0)$ si $k>0$, le point $I$ si $k=0$, ensemble vide si $k<0$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Avec $I(2\,;0)$ milieu de $[AB]$ : $MA^2+MB^2=2MI^2+\dfrac{AB^2}2=2MI^2+8$. L'équation $MI^2=\dfrac{k-8}2$ donne un cercle, un point ou l'ensemble vide selon le signe de $k-8$.

### Corrigé

$MA^2+MB^2=k\iff MI^2=\dfrac{k-8}2$.
- Si $k>8$ : cercle de centre $I(2\,;0)$ et de rayon $\sqrt{\dfrac{k-8}2}$ ;
- si $k=8$ : le seul point $I$ ;
- si $k<8$ : l'ensemble vide (par exemple pour $k=6$, il faudrait $MI^2=-1$).

### Pourquoi les autres réponses sont fausses

- **a)** On a écrit $MA^2+MB^2=2MI^2+AB^2$ en oubliant de diviser $AB^2$ par $2$, d'où le seuil $16$ au lieu de $8$.
- **b)** On a écrit $MA^2+MB^2=2MI^2+\dfrac{AB^2}4$ (confusion avec la formule de la médiane $MI^2$), d'où le seuil $4$.
- **d)** On a oublié le terme constant $\dfrac{AB^2}2$ : pour $k=6$ par exemple, aucun point ne convient, car $MA^2+MB^2\geqslant8$.

</details>

Avis : 

---

## 4. `cqc-relation-de-la-mediane-prob-c-faible-0` (series C)

**A regarder :** LIMITE : théorème de la médiane (lié au produit scalaire, absent du référentiel, à signaler) ; aucune méthode analytique n'est suggérée par l'énoncé.

**Enonce :**

Soit $[AB]$ un segment de longueur $6$ et $I$ son milieu. Pour un point $M$ tel que $MI=4$, que vaut $MA^2+MB^2$ ?

- a) $68$
- b) $34$
- c) $41$
- d) $50$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Théorème de la médiane : $MA^2+MB^2=2MI^2+\dfrac{AB^2}2$ où $I$ est le milieu de $[AB]$.

### Corrigé

$MA^2+MB^2=2\times16+\dfrac{36}2=32+18=50$.

### Pourquoi les autres réponses sont fausses

- **a)** $68=2\times16+36$ : on a oublié de diviser $AB^2$ par $2$.
- **b)** $34=16+18$ : on a oublié le coefficient $2$ devant $MI^2$.
- **c)** $41=32+9$ : on a divisé $AB^2$ par $4$ au lieu de $2$ (confusion avec $IA^2=\dfrac{AB^2}4$).

</details>

Avis : 

---

## 5. `cqc-matrice-inverse-prob-c-moyenne-4` (series C)

**A regarder :** LIMITE : matrices 2×2, déterminant et inversibilité, à confirmer au programme de Première C.

**Enonce :**

Pour $m$ réel, soit $A_m=\begin{pmatrix}m&2\\3&m+1\end{pmatrix}$. Pour quelles valeurs de $m$ la matrice $A_m$ n'est-elle pas inversible ?

- a) $m=-3$ et $m=2$
- b) $m=3$ et $m=-2$
- c) $m=-\sqrt6$ et $m=\sqrt6$
- d) Pour aucune valeur de $m$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

$A_m$ est inversible si et seulement si $\det A_m\neq0$ : on résout l'équation du second degré en $m$ obtenue en annulant le déterminant.

### Corrigé

$\det A_m=m(m+1)-2\times3=m^2+m-6=(m+3)(m-2)$. Il s'annule pour $m=-3$ et $m=2$ : ce sont les valeurs pour lesquelles $A_m$ n'est pas inversible.

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de signe sur les racines : $(m+3)(m-2)=0$ donne $m=-3$ ou $m=2$, et non $m=3$ ou $m=-2$.
- **c)** Le terme $m$ du produit $m(m+1)$ a été oublié : on a résolu $m^2-6=0$.
- **d)** Erreur de signe dans le déterminant : $m(m+1)+6=m^2+m+6$ n'a pas de racine réelle, mais le déterminant est $m(m+1)-6$.

</details>

Avis : 

---

## 6. `cqc-application-lineaire-prob-e-moyenne-3` (series E)

**A regarder :** LIMITE : noyau et image d'une application linéaire, et la notation Vect, sont à la limite haute de Première E ; écrire plutôt « droite vectorielle engendrée par » si Vect n'est pas utilisé dans le manuel.

**Enonce :**

Soit $f$ l'application linéaire de $\mathbb R^2$ dans $\mathbb R^2$ définie par $f(x\,;y)=(2x+y\,;4x+2y)$. Quelle affirmation décrit correctement son noyau $\ker f$ et son image $\operatorname{Im}f$ ?

- a) $\ker f=\operatorname{Vect}\big((1\,;2)\big)$ et $\operatorname{Im}f=\operatorname{Vect}\big((1\,;-2)\big)$
- b) $\ker f=\{(0\,;0)\}$ et $\operatorname{Im}f=\mathbb R^2$
- c) $\ker f=\operatorname{Vect}\big((1\,;-2)\big)$ et $\operatorname{Im}f=\mathbb R^2$
- d) $\ker f=\operatorname{Vect}\big((1\,;-2)\big)$ et $\operatorname{Im}f=\operatorname{Vect}\big((1\,;2)\big)$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Le noyau est l'ensemble des vecteurs d'image nulle ; l'image est l'ensemble de tous les vecteurs $f(x\,;y)$. On les décrit avec les équations obtenues.

### Corrigé

Noyau : $2x+y=0$ et $4x+2y=0$ sont équivalentes ; $y=-2x$, donc $\ker f=\operatorname{Vect}\big((1\,;-2)\big)$.
Image : $f(x\,;y)=(2x+y)\,(1\,;2)$, donc $\operatorname{Im}f=\operatorname{Vect}\big((1\,;2)\big)$.
$f$ n'est pas injective (noyau non réduit à $\{\vec0\}$) : ce n'est pas un isomorphisme.

### Pourquoi les autres réponses sont fausses

- **a)** Le noyau et l'image ont été inversés : $f(1\,;2)=(4\,;8)\neq(0\,;0)$, donc $(1\,;2)$ n'est pas dans le noyau.
- **b)** On a supposé $f$ bijective sans calculer : or $f(1\,;-2)=(0\,;0)$, le noyau n'est pas réduit à $\{(0\,;0)\}$.
- **c)** Le noyau est juste, mais l'image ne peut pas être $\mathbb R^2$ : toutes les images sont proportionnelles à $(1\,;2)$.

</details>

Avis : 

---

## 7. `cqc-linearite-moyenne-3` (series C/E)

**A regarder :** Remarque : Notation mêlée k(x,y) et k(0;0) : harmoniser avec le point-virgule.

**Enonce :**

On considère l'application $k:\mathbb{R}^2\to\mathbb{R}$ définie par $k(x,y)=xy$.

Quelle affirmation est exacte ?

- a) $k$ est linéaire, car $k(0\,;0)=0$.
- b) $k$ est linéaire, car $k(\lambda x,\lambda y)=\lambda\,k(x,y)$ pour tout réel $\lambda$.
- c) $k$ n'est pas linéaire, car $k(2\,;2)=4$ alors que $2\,k(1\,;1)=2$.
- d) $k$ n'est pas linéaire, car $k(0\,;0)\neq0$.

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Une application $f$ est linéaire si $f(\lambda u+\mu v)=\lambda f(u)+\mu f(v)$ pour tous vecteurs $u,v$ et tous réels $\lambda,\mu$ ; en particulier $f(0)=0$. La condition $f(0)=0$ est nécessaire mais pas suffisante.

### Corrigé

Pour réfuter la linéarité, il suffit d'exhiber un cas où l'égalité $f(\lambda u)=\lambda f(u)$ ou $f(u+v)=f(u)+f(v)$ est fausse.

Prenons $u=(1\,;1)$ : $k(u)=1$.

Avec $\lambda=2$ : $k(2u)=k(2\,;2)=4$, alors que $2k(u)=2$.

Comme $4\neq2$, $k$ n'est **pas** linéaire. Réponse **c)**.

### Pourquoi les autres réponses sont fausses

- **a)** $k(0\,;0)=0$ est vrai, mais cette condition seule ne prouve pas la linéarité.
- **b)** En réalité $k(\lambda x,\lambda y)=\lambda^2xy$, et non $\lambda xy$ : l'égalité annoncée est fausse.
- **d)** $k(0\,;0)=0\times0=0$ : la justification repose sur un calcul faux.

</details>

Avis : 

---

## 8. `cqc-interets-composes-prob-d-moyenne-4` (series D)

**A regarder :** VOCABULAIRE : « taux mensuel composé » est impropre ; écrire « au taux mensuel de 1,5 % à intérêts composés, remboursé en une seule fois au bout de 12 mois ».

**Enonce :**

On emprunte $1\,500\,000$ F à un taux mensuel composé de $1{,}5\ \%$. Quelle somme doit-on rembourser au bout de $12$ mois (résultat arrondi au franc) ?

- a) $1\,770\,000$ F
- b) $1\,766\,923$ F
- c) $1\,793\,427$ F
- d) $1\,527\,224$ F

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Avec un taux mensuel $t$, la somme est multipliée par $1+t$ chaque mois : après $n$ mois, $C_n=C_0(1+t)^n$.

### Corrigé

$C_{12}=1\,500\,000\times1{,}015^{12}\approx1\,500\,000\times1{,}195618\approx1\,793\,427$ F (arrondi au franc).

Les intérêts représentent environ $293\,427$ F, soit $19{,}56\ \%$ du capital : plus que $12\times1{,}5\ \%=18\ \%$ à cause de la capitalisation.

Réponse **c)**.

### Pourquoi les autres réponses sont fausses

- **a)** Intérêts simples : $1\,500\,000\times(1+12\times0{,}015)=1\,770\,000$ ; on oublie que les intérêts produisent eux-mêmes des intérêts.
- **b)** Exposant $11$ au lieu de $12$ : $1\,500\,000\times1{,}015^{11}\approx1\,766\,923$.
- **d)** Taux mal converti ($0{,}0015$ au lieu de $0{,}015$) : $1\,500\,000\times1{,}0015^{12}\approx1\,527\,224$.

</details>

Avis : 

---

## 9. `cqc-matrice-inverse-prob-c-moyenne-3` (series C)

**A regarder :** DRAPEAU hors niveau du relecteur : Le calcul matriciel (produit, matrice inverse) n'est pas au programme de Première C ; les systèmes 2x2 s'y résolvent par déterminant/Cramer ou combinaison. À reformuler sans matrice inverse.

**Enonce :**

On veut résoudre le système $\begin{cases}2x+y=5\\5x+3y=13\end{cases}$, qui s'écrit $AX=B$ avec $A=\begin{pmatrix}2&1\\5&3\end{pmatrix}$, $X=\begin{pmatrix}x\\y\end{pmatrix}$ et $B=\begin{pmatrix}5\\13\end{pmatrix}$. Quelle est la matrice inverse $A^{-1}$ ?

- a) $\begin{pmatrix}3&-1\\-5&2\end{pmatrix}$
- b) $\begin{pmatrix}2&-1\\-5&3\end{pmatrix}$
- c) $\begin{pmatrix}3&1\\5&2\end{pmatrix}$
- d) $\begin{pmatrix}3&-5\\-1&2\end{pmatrix}$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Pour $A=\begin{pmatrix}a&b\\c&d\end{pmatrix}$ avec $\det A=ad-bc\neq0$, on a $A^{-1}=\dfrac1{\det A}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}$ : on échange les coefficients diagonaux et on change le signe des deux autres. Le système $AX=B$ a alors pour solution $X=A^{-1}B$.

### Corrigé

$\det A=6-5=1$, donc $A^{-1}=\begin{pmatrix}3&-1\\-5&2\end{pmatrix}$ (on vérifie que $AA^{-1}=I_2$).
$$X=\begin{pmatrix}3&-1\\-5&2\end{pmatrix}\begin{pmatrix}5\\13\end{pmatrix}=\begin{pmatrix}15-13\\-25+26\end{pmatrix}=\begin{pmatrix}2\\1\end{pmatrix}.$$
La solution est $(x\,;y)=(2\,;1)$ (vérification : $4+1=5$ et $10+3=13$).

### Pourquoi les autres réponses sont fausses

- **b)** Les signes de $b$ et $c$ ont été changés mais les coefficients diagonaux n'ont pas été échangés.
- **c)** Les coefficients diagonaux ont été échangés mais on a oublié de changer le signe de $b$ et $c$.
- **d)** On a transposé la matrice au lieu d'échanger les coefficients diagonaux : le produit avec $A$ ne donne pas $I_2$.

</details>

Avis : 

---

## 10. `cqc-relation-de-la-mediane-prob-c-moyenne-4` (series C)

**A regarder :** LIMITE : le théorème de la médiane relève du produit scalaire, signalé comme absent du référentiel.

**Enonce :**

Dans un triangle $ABC$, $BC=6$, $AB=5$ et la médiane $AI$ (où $I$ est le milieu de $[BC]$) mesure $4$. Quelle est la longueur $AC$ ?

- a) $5$
- b) $4$
- c) $3$
- d) $\sqrt{10}$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Théorème de la médiane : $AB^2+AC^2=2AI^2+\dfrac{BC^2}2$ ; on isole $AC^2$.

### Corrigé

$25+AC^2=2\times16+\dfrac{36}2=50$, donc $AC^2=25$ et $AC=5$ : le triangle est isocèle en $A$.

### Pourquoi les autres réponses sont fausses

- **b)** $4$ : on a écrit $\dfrac{BC^2}4$ au lieu de $\dfrac{BC^2}2$, d'où $AC^2=32+9-25=16$.
- **c)** $3$ : on a oublié le facteur $2$ devant $AI^2$, d'où $AC^2=16+18-25=9$.
- **d)** $\sqrt{10}$ : on a utilisé $\dfrac{BC}2=3$ au lieu de $\dfrac{BC^2}2=18$, d'où $AC^2=32+3-25=10$.

</details>

Avis : 

---

## 11. `cqc-fonction-impaire-prob-d-moyenne-3` (series D)

**A regarder :** LIMITE : la parité de la dérivée suppose la dérivée de x↦f(-x), à la limite du programme de Première D.

**Enonce :**

Une fonction $f$ est impaire et dérivable sur $\mathbb{R}$ ; on sait que $f(3)=4$ et $f'(2)=1{,}5$. Que valent, dans cet ordre, $f(-3)$, $f(0)$ et $f'(-2)$ ?

- a) $-4$ ; $0$ ; $1{,}5$
- b) $-4$ ; $0$ ; $-1{,}5$
- c) $4$ ; $0$ ; $1{,}5$
- d) $-4$ ; $0$ ; on ne peut pas calculer $f'(-2)$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Si $f$ est impaire : $f(-x)=-f(x)$, donc $f(0)=0$. La dérivée de $x\mapsto f(-x)$ est $x\mapsto-f'(-x)$ (dérivée de $x\mapsto g(ax+b)$ : $x\mapsto a\,g'(ax+b)$) ; en dérivant $f(-x)=-f(x)$, on obtient $-f'(-x)=-f'(x)$, donc $f'$ est paire.

### Corrigé

$f(-3)=-f(3)=-4$. $f(0)=-f(0)$ donc $f(0)=0$. En dérivant $f(-x)=-f(x)$ : $-f'(-x)=-f'(x)$, soit $f'(-x)=f'(x)$, donc $f'(-2)=f'(2)=1{,}5$ : la dérivée d'une fonction impaire est paire.

### Pourquoi les autres réponses sont fausses

- **b)** On a cru que $f'$ est impaire comme $f$ ; en fait, la dérivée d'une fonction impaire est paire.
- **c)** On a utilisé la propriété d'une fonction paire ($f(-3)=f(3)$) au lieu de celle d'une fonction impaire.
- **d)** $f'(-2)$ se déduit de $f'(2)$, car $f'$ est paire : il n'est pas nécessaire de connaître l'expression de $f$.

</details>

Avis : 

---

## 12. `cqc-relation-de-la-mediane-prob-c-elevee-5` (series C)

**A regarder :** LIMITE : relation du parallélogramme issue du théorème de la médiane / produit scalaire, signalé comme absent du référentiel. Le distracteur d) 84 = BD² est un bon piège.

**Enonce :**

Un parallélogramme $ABCD$ a pour côtés $AB=5$ et $AD=7$ et sa diagonale $AC$ mesure $8$. Quelle est la longueur de l'autre diagonale $BD$ ?

- a) $2\sqrt{21}$
- b) $\sqrt{10}$
- c) $2\sqrt{37}$
- d) $84$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Les diagonales d'un parallélogramme se coupent en leur milieu $O$. Dans le triangle $ABD$, $AO$ est la médiane issue de $A$ : $AB^2+AD^2=2AO^2+\dfrac{BD^2}2$.

### Corrigé

Dans $ABD$, $O$ est le milieu de $[BD]$ et $AO=\dfrac{AC}2$ : $AB^2+AD^2=2\dfrac{AC^2}4+\dfrac{BD^2}2=\dfrac{AC^2+BD^2}2$. D'où $AC^2+BD^2=2(AB^2+AD^2)$.

Ainsi $64+BD^2=2(25+49)=148$, donc $BD^2=84$ et $BD=2\sqrt{21}\approx9{,}17$.

### Pourquoi les autres réponses sont fausses

- **b)** Le facteur $2$ a été oublié : $BD^2=25+49-64=10$.
- **c)** On a pris $BD^2=2(AB^2+AD^2)=148$ sans retrancher $AC^2$.
- **d)** $84$ est la valeur de $BD^2$ : la racine carrée a été oubliée.

</details>

Avis : 

---

## 13. `cqc-representation-parametrique-prob-c-elevee-5` (series C)

**A regarder :** LIMITE : representations parametriques de droites de l'espace, a verifier au programme de Premiere C.

**Enonce :**

Dans l'espace muni d'un repère, on donne les droites $D_1$ : $x=1+t$, $y=2t$, $z=-1+t$ ($t\in\mathbb R$) et $D_2$ : $x=4-2s$, $y=-1+3s$, $z=s-1$ ($s\in\mathbb R$). Quelle est la position relative de $D_1$ et $D_2$ ?

- a) Sécantes au point $(2\,;2\,;0)$
- b) Sécantes au point $(1\,;0\,;-1)$
- c) Sécantes au point $(4\,;-1\,;-1)$
- d) Non coplanaires

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Deux droites sont sécantes si leurs vecteurs directeurs ne sont pas colinéaires et si le système obtenu en égalant les coordonnées admet une solution. Si les vecteurs directeurs ne sont pas colinéaires et que le système n'a pas de solution, elles ne sont pas coplanaires.

### Corrigé

Les vecteurs directeurs $(1\,;2\,;1)$ et $(-2\,;3\,;1)$ ne sont pas colinéaires. On résout :
$1+t=4-2s$, $2t=-1+3s$, $-1+t=s-1$.
La troisième équation donne $t=s$. En reportant dans la première : $1+s=4-2s\Rightarrow s=1=t$. Vérification dans la deuxième : $2t=2$ et $-1+3s=2$, l'équation est satisfaite.
Pour $t=1$, le point de $D_1$ est $(2\,;2\,;0)$ (on retrouve le même point avec $s=1$ dans $D_2$).
$D_1$ et $D_2$ sont sécantes en $(2\,;2\,;0)$. Réponse **a)**.

### Pourquoi les autres réponses sont fausses

- **b)** $(1\,;0\,;-1)$ est le point de $D_1$ obtenu pour $t=0$ ; il n'appartient pas à $D_2$.
- **c)** $(4\,;-1\,;-1)$ est le point de $D_2$ obtenu pour $s=0$ ; il n'appartient pas à $D_1$.
- **d)** Le système admet une solution : conclure à des droites non coplanaires vient d'une erreur de calcul dans sa résolution.

</details>

Avis : 

---

## 14. `cqc-theoreme-de-la-mediane-prob-d-moyenne-2` (series D)

**A regarder :** Remarque : Doublon quasi exact de la question 17 (serie C), seuls les distracteurs changent.

**Enonce :**

Dans un repère orthonormé d'origine $O$, on donne $A(-2\,;0)$ et $B(2\,;0)$. Quel est l'ensemble des points $M$ du plan tels que $MA^2+MB^2=26$ ?

- a) Le cercle de centre $O$ et de rayon $9$
- b) Le cercle de centre $O$ et de rayon $3$
- c) Le cercle de centre $O$ et de rayon $\sqrt{13}$
- d) Le cercle de centre $O$ et de rayon $\sqrt5$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Avec $I$ milieu de $[AB]$ (ici $O$), le théorème de la médiane donne $MA^2+MB^2=2MI^2+\dfrac{AB^2}2$. L'équation devient $MO^2=$ constante : un cercle.

### Corrigé

$AB=4$, donc $MA^2+MB^2=2MO^2+\dfrac{16}2=2MO^2+8$. Alors $2MO^2+8=26\iff MO^2=9\iff MO=3$.

L'ensemble est le cercle de centre $O$ et de rayon $3$.

Vérification avec $M(3\,;0)$ : $MA^2=25$, $MB^2=1$ et $25+1=26$.

Réponse **b)**.

### Pourquoi les autres réponses sont fausses

- **a)** On a lu $MO^2=9$ comme $MO=9$ : oubli de la racine carrée.
- **c)** Oubli du terme $\dfrac{AB^2}2$ : $2MO^2=26$ donne $MO=\sqrt{13}$.
- **d)** Terme $AB^2$ au lieu de $\dfrac{AB^2}2$ : $2MO^2+16=26$ donne $MO=\sqrt5$.

</details>

Avis : 

---

## 15. `cqc-representation-parametrique-prob-c-moyenne-4` (series C)

**A regarder :** LIMITE : equation cartesienne de plan et representation parametrique de droite dans l'espace, a verifier au programme de Premiere C.

**Enonce :**

Dans l'espace muni d'un repère, quel est le point d'intersection de la droite de représentation paramétrique $x=1+t$, $y=2-t$, $z=3+2t$ ($t\in\mathbb{R}$) avec le plan d'équation $x+y+z=10$ ?

- a) $(3\,;0\,;7)$
- b) $(2\,;1\,;5)$
- c) $(3\,;4\,;7)$
- d) $(9\,;-6\,;19)$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

On remplace $x$, $y$, $z$ par leurs expressions en $t$ dans l'équation du plan, on résout en $t$, puis on calcule les coordonnées.

### Corrigé

$(1+t)+(2-t)+(3+2t)=6+2t=10\Rightarrow t=2$. Le point d'intersection est $(3\,;0\,;7)$ (vérification : $3+0+7=10$).

### Pourquoi les autres réponses sont fausses

- **b)** Le $-t$ de $y$ a été compté comme $+t$ : $6+4t=10$ donne $t=1$, et le point $(2\,;1\,;5)$ n'est pas dans le plan ($2+1+5=8$).
- **c)** Bonne valeur $t=2$, mais erreur de signe sur $y$ : $y=2-2=0$, et non $4$.
- **d)** Erreur de transposition : $2t=10+6$ donne $t=8$ au lieu de $2t=10-6$.

</details>

Avis : 

---

## 16. `cqc-relation-de-la-mediane-prob-c-moyenne-3` (series C)

**A regarder :** Remarque : Doublon quasi exact de la question 2 (serie D).

**Enonce :**

Dans un repère orthonormé d'origine $O$, on donne $A(-2\,;0)$ et $B(2\,;0)$. Quel est l'ensemble des points $M$ du plan tels que $MA^2+MB^2=26$ ?

- a) Le cercle de centre $O$ et de rayon $\sqrt{13}$
- b) Le cercle de centre $O$ et de rayon $3$
- c) Le cercle de centre $O$ et de rayon $3\sqrt2$
- d) Le cercle de centre $O$ et de rayon $\sqrt{11}$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Avec $O$ milieu de $[AB]$ et $AB=4$, la relation de la médiane donne : $MA^2+MB^2=2MO^2+\dfrac{AB^2}2=2MO^2+8$.

### Corrigé

$2MO^2+8=26\Rightarrow MO^2=9\Rightarrow MO=3$ : c'est le cercle de centre $O$ et de rayon $3$, d'équation $x^2+y^2=9$.
Vérification directe : $(x+2)^2+y^2+(x-2)^2+y^2=2x^2+2y^2+8=26\iff x^2+y^2=9$. Réponse **b)**.

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié le terme $\dfrac{AB^2}2$ : $2MO^2=26$ donne $MO=\sqrt{13}$.
- **c)** On a oublié de diviser par $2$ : $MO^2=26-8=18$.
- **d)** On a écrit $\dfrac{AB^2}4=4$ au lieu de $\dfrac{AB^2}2=8$, d'où $2MO^2=22$ et $MO=\sqrt{11}$.

</details>

Avis : 

---

## 17. `cqc-systeme-homogene-prob-c-elevee-5` (series C)

**A regarder :** LIMITE : vocabulaire « application linéaire de R³ dans R², matrice, noyau » à vérifier au programme de Première C ; la question reste soluble par simple résolution du système.

**Enonce :**

On considère l'application linéaire $f$ de $\mathbb R^3$ dans $\mathbb R^2$ de matrice $\begin{pmatrix}1&1&1\\1&-1&1\end{pmatrix}$, c'est-à-dire $f(x,y,z)=(x+y+z\,;\,x-y+z)$. Quel est le noyau de $f$, autrement dit l'ensemble des solutions dans $\mathbb R^3$ du système $\begin{cases}x+y+z=0\\x-y+z=0\end{cases}$ ?

- a) $\{(0\,;0\,;0)\}$
- b) $\{k(1\,;0\,;1),\ k\in\mathbb R\}$
- c) $\{k(1\,;0\,;-1),\ k\in\mathbb R\}$
- d) $\{k(1\,;-1\,;0),\ k\in\mathbb R\}$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Trois inconnues pour deux équations : on ajoute et soustrait les équations pour exprimer deux inconnues en fonction de la troisième (paramètre). Le noyau de $f$ est l'ensemble des vecteurs dont l'image est le vecteur nul, c'est-à-dire l'ensemble des solutions du système.

### Corrigé

En additionnant : $2x+2z=0\Rightarrow z=-x$. En soustrayant : $2y=0\Rightarrow y=0$.
Les solutions sont $(x\,;0\,;-x)$, $x\in\mathbb R$, c'est-à-dire $(k\,;0\,;-k)=k(1\,;0\,;-1)$.
Le noyau de l'application est la droite vectorielle engendrée par $\vec u(1\,;0\,;-1)$ (de dimension $1$).

### Pourquoi les autres réponses sont fausses

- **a)** Un système homogène à trois inconnues et deux équations n'a pas que la solution nulle : $(1\,;0\,;-1)$ en est une autre.
- **b)** Erreur de signe : $(1\,;0\,;1)$ donne $1+0+1=2\neq0$ ; l'addition des équations donne $z=-x$ et non $z=x$.
- **d)** $(1\,;-1\,;0)$ vérifie la première équation mais pas la seconde ($1+1+0=2\neq0$) : il faut vérifier les deux équations.

</details>

Avis : 

---

## 18. `cqc-linearite-faible-1` (series C/E)

**Question tiree au hasard.**

**Enonce :**

On considère l'application $g:\mathbb{R}^2\to\mathbb{R}^2$ définie par $g(x\,;y)=(x+1\,;y)$. Laquelle des affirmations suivantes est exacte ?

- a) $g$ est linéaire, car ses deux composantes sont des expressions du premier degré en $x$ et $y$.
- b) $g$ n'est pas linéaire, car $g(0\,;0)=(1\,;0)$.
- c) $g$ est linéaire, car $g(0\,;0)=(0\,;0)$.
- d) $g$ n'est pas linéaire, car $g(0\,;0)=(1\,;1)$.

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Une application $f$ est linéaire si $f(\lambda u+\mu v)=\lambda f(u)+\mu f(v)$ pour tous vecteurs $u,v$ et tous réels $\lambda,\mu$ ; en particulier $f(0)=0$.

### Corrigé

Une application linéaire envoie le vecteur nul sur le vecteur nul.

Or $g(0\,;0)=(1\,;0)\neq(0\,;0)$.

Donc $g$ n'est **pas** linéaire.

### Pourquoi les autres réponses sont fausses

- **a)** Avoir des composantes du premier degré ne suffit pas : le terme constant $+1$ empêche la linéarité.
- **c)** Erreur de calcul : $g(0\,;0)=(0+1\,;0)=(1\,;0)$ et non $(0\,;0)$.
- **d)** Erreur de calcul sur la seconde composante : elle vaut $y=0$, donc $g(0\,;0)=(1\,;0)$ et non $(1\,;1)$.

</details>

Avis : 

---

## 19. `cqc-valeurs-remarquables-prob-c-moyenne-3` (series C)

**Question tiree au hasard.**

**Enonce :**

Quelle est la valeur exacte de $A=\sin\dfrac\pi3\cos\dfrac\pi6+\cos\dfrac\pi3\sin\dfrac\pi6$ ?

- a) $\dfrac{\sqrt3}2$
- b) $\dfrac12$
- c) $1$
- d) $\dfrac34$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

$\sin(a+b)=\sin a\cos b+\cos a\sin b$ : on remplace par les valeurs remarquables et on vérifie avec la formule.

### Corrigé

$A=\dfrac{\sqrt3}2\times\dfrac{\sqrt3}2+\dfrac12\times\dfrac12=\dfrac34+\dfrac14=1$.
C'est $\sin\left(\dfrac\pi3+\dfrac\pi6\right)=\sin\dfrac\pi2=1$, ce qui confirme le calcul.

### Pourquoi les autres réponses sont fausses

- **a)** $\dfrac{\sqrt3}2$ : on a interverti $\cos\dfrac\pi6$ et $\sin\dfrac\pi6$ (en prenant $\cos\dfrac\pi6=\dfrac12$ et $\sin\dfrac\pi6=\dfrac{\sqrt3}2$).
- **b)** $\dfrac12$ : on a reconnu à tort $\sin\left(\dfrac\pi3-\dfrac\pi6\right)=\sin\dfrac\pi6$, alors que la formule de $\sin(a-b)$ comporte un signe moins.
- **d)** $\dfrac34$ : on a oublié le second produit $\cos\dfrac\pi3\sin\dfrac\pi6=\dfrac14$.

</details>

Avis : 

---

## 20. `cqc-formule-d-addition-prob-de-faible-0` (series D/E)

**Question tiree au hasard.**

**Enonce :**

Quelle est la valeur exacte de $\cos\dfrac{5\pi}{12}$ ?

- a) $\dfrac{\sqrt6+\sqrt2}4$
- b) $\dfrac{\sqrt2-\sqrt6}4$
- c) $\dfrac{\sqrt6-\sqrt2}2$
- d) $\dfrac{\sqrt6-\sqrt2}4$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

On écrit $\dfrac{5\pi}{12}=\dfrac\pi4+\dfrac\pi6$ et on utilise $\cos(a+b)=\cos a\cos b-\sin a\sin b$ avec les valeurs remarquables de $\dfrac\pi4$ et $\dfrac\pi6$.

### Corrigé

$$\cos\dfrac{5\pi}{12}=\cos\dfrac\pi4\cos\dfrac\pi6-\sin\dfrac\pi4\sin\dfrac\pi6=\dfrac{\sqrt2}2\times\dfrac{\sqrt3}2-\dfrac{\sqrt2}2\times\dfrac12=\dfrac{\sqrt6-\sqrt2}4.$$

Réponse **d)**.

### Pourquoi les autres réponses sont fausses

- **a)** Mauvais signe dans la formule ($+\sin a\sin b$) : c'est la valeur de $\cos\dfrac{\pi}{12}$.
- **b)** Valeurs de $\cos\dfrac\pi6$ et $\sin\dfrac\pi6$ échangées : on obtient un nombre négatif, impossible puisque $\dfrac{5\pi}{12}$ est entre $0$ et $\dfrac\pi2$.
- **c)** Erreur sur les dénominateurs : $\dfrac{\sqrt2}2\times\dfrac{\sqrt3}2=\dfrac{\sqrt6}4$ et non $\dfrac{\sqrt6}2$.

</details>

Avis : 

---

## 21. `cqc-espace-moyenne-1` (series C/E)

**Question tiree au hasard.**

**Enonce :**

Dans l'espace, on considère quatre points $M$, $N$, $P$, $Q$, non nécessairement coplanaires. On note $I$ le barycentre du système de points pondérés $\{(M,2);(N,3)\}$ et $K$ le barycentre du système $\{(P,2);(Q,3)\}$.

Quelle égalité est toujours vraie ?

- a) $2\vec{MP} + 3\vec{NQ} = 5\vec{IK}$
- b) $2\vec{PM} + 3\vec{QN} = 5\vec{IK}$
- c) $3\vec{MP} + 2\vec{NQ} = 5\vec{IK}$
- d) $2\vec{MP} + 3\vec{NQ} = \vec{IK}$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Si $I$ est le barycentre du système $\{(M,a);(N,b)\}$, alors pour tout point $X$ de l'espace, $a\vec{XM} + b\vec{XN} = (a+b)\vec{XI}$, c'est-à-dire $\vec{XI} = \dfrac{a\,\vec{XM}+b\,\vec{XN}}{a+b}$. Cette écriture, valable quel que soit le point $X$, permet de faire apparaître des différences de vecteurs.

### Corrigé

Soit $X$ un point quelconque de l'espace.

Puisque $I$ est le barycentre de $\{(M,2);(N,3)\}$ :
$$\vec{XI} = \frac{2\vec{XM} + 3\vec{XN}}{5}$$

Puisque $K$ est le barycentre de $\{(P,2);(Q,3)\}$ :
$$\vec{XK} = \frac{2\vec{XP} + 3\vec{XQ}}{5}$$

On en déduit :
$$\vec{IK} = \vec{XK} - \vec{XI} = \frac{2(\vec{XP}-\vec{XM}) + 3(\vec{XQ}-\vec{XN})}{5}$$

Or $\vec{XP} - \vec{XM} = \vec{MP}$ et $\vec{XQ} - \vec{XN} = \vec{NQ}$ (relation de Chasles), donc $5\vec{IK} = 2\vec{MP} + 3\vec{NQ}$.

Réponse **a)**.

### Pourquoi les autres réponses sont fausses

- **b)** Erreur d'orientation : $\vec{PM}=-\vec{MP}$, cette somme vaut $-5\vec{IK}=5\vec{KI}$.
- **c)** Coefficients échangés : le poids $2$ est attaché à $M$ et à $P$, donc au vecteur $\vec{MP}$.
- **d)** Oubli de la division par la somme des poids $2+3=5$.

</details>

Avis : 

---

## 22. `cqc-resolution-dans-un-intervalle-prob-c-moyenne-2` (series C)

**Question tiree au hasard.**

**Enonce :**

Quel est l'ensemble des solutions dans $[0\,;2\pi]$ de l'équation $\cos x=\dfrac12$ ?

- a) $\left\{\dfrac\pi3\,;\dfrac{2\pi}3\right\}$
- b) $\left\{\dfrac\pi3\,;\dfrac{5\pi}3\right\}$
- c) $\left\{\dfrac\pi3\right\}$
- d) $\left\{-\dfrac\pi3\,;\dfrac\pi3\right\}$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

On repère la solution de référence de $\cos x=\dfrac12$ (ici $\dfrac\pi3$) puis on cherche les autres solutions de l'intervalle par symétrie sur le cercle trigonométrique (deux angles opposés ont le même cosinus).

### Corrigé

$\cos x=\cos\dfrac\pi3\iff x=\dfrac\pi3+2k\pi$ ou $x=-\dfrac\pi3+2k\pi$ ($k$ entier). Dans $[0\,;2\pi]$ : $x=\dfrac\pi3$ ou $x=-\dfrac\pi3+2\pi=\dfrac{5\pi}3$.

### Pourquoi les autres réponses sont fausses

- **a)** $\left\{\dfrac\pi3\,;\dfrac{2\pi}3\right\}$ : on a utilisé la symétrie du sinus ($\pi-x$) au lieu de celle du cosinus ($-x$) ; d'ailleurs $\cos\dfrac{2\pi}3=-\dfrac12$.
- **c)** $\left\{\dfrac\pi3\right\}$ : on a oublié la seconde famille de solutions.
- **d)** $\left\{-\dfrac\pi3\,;\dfrac\pi3\right\}$ : $-\dfrac\pi3$ n'appartient pas à $[0\,;2\pi]$, il fallait ajouter $2\pi$.

</details>

Avis : 

---

## 23. `cqc-extremum-local-prob-c-faible-0` (series C)

**Question tiree au hasard.**

**Enonce :**

Soit $f$ dérivable sur $\mathbb R$ avec $f'(x)=(x-1)(x-3)$. Quelle affirmation est exacte ?

- a) $f$ admet un minimum local en $1$ et un maximum local en $3$.
- b) $f$ admet un maximum local en $1$ et un minimum local en $3$.
- c) $f$ admet un maximum local en $-1$ et un minimum local en $-3$.
- d) $f$ admet un seul extremum local, en $2$.

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Une fonction dérivable admet un extremum local en $a$ si $f'$ s'annule en $a$ en changeant de signe : maximum si $f'$ passe de positive à négative, minimum dans le cas contraire.

### Corrigé

$f'$ s'annule en $1$ et $3$ et change de signe en chacun : $f'>0$ avant $1$, $f'<0$ entre $1$ et $3$, $f'>0$ après $3$. Il y a un maximum local en $x=1$ et un minimum local en $x=3$.

### Pourquoi les autres réponses sont fausses

- **a)** Les rôles sont inversés : $f$ croît puis décroît autour de $1$ (maximum), décroît puis croît autour de $3$ (minimum).
- **c)** Erreur de signe sur les racines : $(x-1)(x-3)$ s'annule en $1$ et $3$, pas en $-1$ et $-3$.
- **d)** $2$ est le milieu des racines, où $f'$ atteint son minimum ; $f'(2)=-1\neq0$, donc ce n'est pas un extremum de $f$.

</details>

Avis : 

---

## 24. `cqc-matrice-inverse-prob-c-faible-0` (series C)

**Question tiree au hasard.**

**Enonce :**

Quelle est l'inverse de la matrice $A=\begin{pmatrix}5&2\\7&3\end{pmatrix}$ ?

- a) $\begin{pmatrix}5&-2\\-7&3\end{pmatrix}$
- b) $\begin{pmatrix}3&2\\7&5\end{pmatrix}$
- c) $\begin{pmatrix}3&-7\\-2&5\end{pmatrix}$
- d) $\begin{pmatrix}3&-2\\-7&5\end{pmatrix}$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Si $ad-bc\neq0$, l'inverse de $\begin{pmatrix}a&b\\c&d\end{pmatrix}$ est $\dfrac1{ad-bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}$.

### Corrigé

$\det A=15-14=1$, donc $A^{-1}=\begin{pmatrix}3&-2\\-7&5\end{pmatrix}$.

Vérification : $AA^{-1}=\begin{pmatrix}15-14&-10+10\\21-21&-14+15\end{pmatrix}=\begin{pmatrix}1&0\\0&1\end{pmatrix}$.

### Pourquoi les autres réponses sont fausses

- **a)** Les signes de $b$ et $c$ ont été changés, mais $a$ et $d$ n'ont pas été échangés.
- **b)** $a$ et $d$ ont été échangés, mais les signes de $b$ et $c$ n'ont pas été changés.
- **c)** Les coefficients $-b$ et $-c$ ont été placés à la mauvaise position (transposition).

</details>

Avis : 

---

## 25. `cqc-droites-perpendiculaires-prob-c-moyenne-4` (series C)

**Question tiree au hasard.**

**Enonce :**

Dans un repère orthonormé, on donne $A(1\,;2)$ et $B(5\,;4)$. Quelle est une équation de la médiatrice du segment $[AB]$ ?

- a) $x-2y+3=0$
- b) $2x+y-4=0$
- c) $2x-y-3=0$
- d) $2x+y-9=0$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

La médiatrice de $[AB]$ est l'ensemble des points $M$ équidistants de $A$ et de $B$ : $MA^2=MB^2$. C'est aussi la droite perpendiculaire à $(AB)$ passant par le milieu $I$ de $[AB]$.

### Corrigé

Pour $M(x\,;y)$ : $MA^2=MB^2\iff(x-1)^2+(y-2)^2=(x-5)^2+(y-4)^2$.

En développant : $-2x+1-4y+4=-10x+25-8y+16$, soit $8x+4y-36=0$, c'est-à-dire $2x+y-9=0$.

Vérification : le milieu $I(3\,;3)$ vérifie $6+3-9=0$, et la droite a pour coefficient directeur $-2$, alors que $(AB)$ a pour coefficient directeur $\dfrac{4-2}{5-1}=\dfrac12$ ; comme $-2\times\dfrac12=-1$, les deux droites sont perpendiculaires.

### Pourquoi les autres réponses sont fausses

- **a)** $x-2y+3=0$ est l'équation de la droite $(AB)$ elle-même, pas de sa perpendiculaire.
- **b)** $2x+y-4=0$ est bien perpendiculaire à $(AB)$ mais passe par $A$ au lieu du milieu de $[AB]$.
- **c)** $2x-y-3=0$ passe par $I$ mais a pour coefficient directeur $2$ : on a pris l'inverse de $\dfrac12$ en oubliant le signe moins.

</details>

Avis : 

---

## 26. `cqc-equation-cartesienne-d-un-cercle-prob-d-faible-0` (series D)

**Question tiree au hasard.**

**Enonce :**

Dans un repère orthonormé, quelle est une équation cartésienne du cercle de centre $\Omega(2\,;-1)$ et de rayon $3$ ?

- a) $(x+2)^2+(y-1)^2=9$
- b) $(x-2)^2+(y+1)^2=3$
- c) $(x-2)^2+(y-1)^2=9$
- d) $(x-2)^2+(y+1)^2=9$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Le cercle de centre $\Omega(a\,;b)$ et de rayon $R$ est l'ensemble des points $M(x\,;y)$ tels que $\Omega M=R$, soit $(x-a)^2+(y-b)^2=R^2$.

### Corrigé

Ici $a=2$, $b=-1$ et $R=3$ :
$$(x-2)^2+(y+1)^2=9.$$

### Pourquoi les autres réponses sont fausses

- **a)** Les deux signes sont inversés : c'est le cercle de centre $(-2\,;1)$.
- **b)** Le rayon n'a pas été élevé au carré : c'est le cercle de rayon $\sqrt3$.
- **c)** Erreur de signe sur l'ordonnée : $y-(-1)=y+1$ ; c'est le cercle de centre $(2\,;1)$.

</details>

Avis : 

---

## 27. `cqc-extremum-local-prob-c-elevee-5` (series C)

**Question tiree au hasard.**

**Enonce :**

Soit $f(x)=x^3+ax^2+bx$ où $a$ et $b$ sont des réels. La fonction $f$ admet un extremum local en $x=1$ et $f(1)=-2$. Quelles sont les valeurs de $a$ et $b$, et quel est le maximum local de $f$ ?

- a) $a=0$, $b=-3$ ; maximum local $-2$ atteint en $x=1$
- b) $a=0$, $b=-3$ ; maximum local $2$ atteint en $x=-1$
- c) $a=-4$, $b=5$ ; maximum local $2$ atteint en $x=1$
- d) $a=-3$, $b=0$ ; maximum local $0$ atteint en $x=0$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Un extremum local en $1$ impose $f'(1)=0$. Avec $f(1)=-2$, on obtient un système de deux équations d'inconnues $a$ et $b$. Il faut ensuite vérifier que $f'$ change bien de signe et étudier les variations.

### Corrigé

$f'(x)=3x^2+2ax+b$. $f'(1)=0$ : $3+2a+b=0$. $f(1)=-2$ : $1+a+b=-2$.
En soustrayant la seconde équation de la première : $2+a=2$, donc $a=0$, puis $b=-3$ (car $1+0+b=-2$).

$f(x)=x^3-3x$, $f'(x)=3(x-1)(x+1)$. $f$ croît sur $]-\infty\,;-1]$, décroît sur $[-1\,;1]$, croît sur $[1\,;+\infty[$.
Maximum local $f(-1)=-1+3=2$ ; minimum local $f(1)=-2$ (le changement de signe de $f'$ est bien vérifié).

### Pourquoi les autres réponses sont fausses

- **a)** $a$ et $b$ sont justes, mais $f(1)=-2$ est un minimum local ($f'$ passe de négative à positive en $1$) ; le maximum local est atteint en $-1$.
- **c)** Erreur de signe : on a écrit $f(1)=2$ au lieu de $-2$, d'où $a=-4$ et $b=5$, qui ne vérifient pas $f(1)=-2$.
- **d)** Les valeurs de $a$ et $b$ ont été inversées : avec $a=-3$ et $b=0$, $f'(1)=-3\neq0$, donc $f$ n'a pas d'extremum en $1$.

</details>

Avis : 

---

## 28. `cqc-image-d-un-cercle-prob-e-moyenne-4` (series E)

**Question tiree au hasard.**

**Enonce :**

Dans un repère orthonormé, le cercle $(\mathcal C)$ a pour équation $x^2+y^2=4$. Quelle est une équation de son image par la translation de vecteur $\vec u(1\,;2)$ ?

- a) $(x-1)^2+(y-2)^2=4$
- b) $(x+1)^2+(y+2)^2=4$
- c) $x^2+y^2-2x-4y=4$
- d) $x^2+y^2-2x-4y-1=0$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Un point $M'(x'\,;y')$ est sur l'image si et seulement si son antécédent $M(x'-1\,;y'-2)$ vérifie l'équation de $(\mathcal C)$.

### Corrigé

$M(x'-1\,;y'-2)\in(\mathcal C)\iff(x'-1)^2+(y'-2)^2=4$.
L'image est le cercle d'équation $(x-1)^2+(y-2)^2=4$ : centre $(1\,;2)$ et rayon $2$. Sous forme développée : $x^2+y^2-2x-4y+1=0$.

### Pourquoi les autres réponses sont fausses

- **b)** $(x+1)^2+(y+2)^2=4$ : on a remplacé $M$ par $M'+\vec u$ au lieu de $M'-\vec u$ ; ce cercle a pour centre $(-1\,;-2)$.
- **c)** $x^2+y^2-2x-4y=4$ : en développant, on a oublié les constantes $1$ et $4$ des carrés.
- **d)** $x^2+y^2-2x-4y-1=0$ : erreur de signe en transposant, on a calculé $4-5$ au lieu de $5-4$.

</details>

Avis : 

---

## 29. `cqc-application-lineaire-prob-e-elevee-5` (series E)

**Question tiree au hasard.**

**Enonce :**

Soit $f$ une application linéaire du plan telle que $f(1\,;1)=(3\,;1)$ et $f(1\,;-1)=(1\,;5)$.

Que vaut $f(2\,;-3)$ ?

- a) $(7\,;0)$
- b) $(1\,;12)$
- c) $(2\,;24)$
- d) $(-5\,;8)$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

On exprime $(1\,;0)$ et $(0\,;1)$ comme combinaisons de $(1\,;1)$ et $(1\,;-1)$ : $(1\,;0)=\dfrac12\big[(1\,;1)+(1\,;-1)\big]$ et $(0\,;1)=\dfrac12\big[(1\,;1)-(1\,;-1)\big]$. La linéarité de $f$ donne les images, puis l'expression de $f(x\,;y)$.

### Corrigé

$f(1\,;0)=\dfrac12\big[(3\,;1)+(1\,;5)\big]=(2\,;3)$ et $f(0\,;1)=\dfrac12\big[(3\,;1)-(1\,;5)\big]=(1\,;-2)$.

$f(x\,;y)=x\,f(1\,;0)+y\,f(0\,;1)=(2x+y\,;3x-2y)$. Vérification : $f(1\,;1)=(3\,;1)$ et $f(1\,;-1)=(1\,;5)$.

$f(2\,;-3)=(4-3\,;6+6)=(1\,;12)$.

Réponse **b)**.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur $f(0\,;1)$, calculé comme $\dfrac12\big[(1\,;5)-(3\,;1)\big]=(-1\,;2)$ : on obtient $f(x\,;y)=(2x-y\,;3x+2y)$.
- **c)** Oubli du facteur $\dfrac12$ : $f(1\,;0)$ et $f(0\,;1)$ sont doublés, donc le résultat aussi.
- **d)** Confusion lignes/colonnes : on a pris $f(x\,;y)=(2x+3y\,;x-2y)$.

</details>

Avis : 

---

## 30. `cqc-droites-perpendiculaires-prob-c-moyenne-3` (series C)

**A regarder :** Methode remplacee : vecteurs normaux remplaces par le produit des coefficients directeurs.

**Enonce :**

Dans un repère orthonormé, pour quelle valeur du réel $m$ les droites $(D):\ (m+1)x+2y-3=0$ et $(D'):\ 3x+(m-1)y+1=0$ sont-elles perpendiculaires ?

- a) $m=\dfrac15$
- b) $m=-5$
- c) $m=\sqrt7$ ou $m=-\sqrt7$
- d) $m=-\dfrac15$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Dans un repère orthonormé, deux droites non parallèles aux axes, de coefficients directeurs $p$ et $p'$, sont perpendiculaires si et seulement si $p\times p'=-1$. On examine à part le cas où une droite est parallèle à l'axe des ordonnées.

### Corrigé

Si $m=1$, $(D')$ a pour équation $x=-\dfrac13$ (parallèle à l'axe des ordonnées) ; il faudrait alors $(D)$ parallèle à l'axe des abscisses, c'est-à-dire $m+1=0$, ce qui est incompatible avec $m=1$.

Pour $m\neq1$ : $(D)$ a pour coefficient directeur $p=-\dfrac{m+1}2$ et $(D')$ a pour coefficient directeur $p'=-\dfrac3{m-1}$.
$$p\times p'=\dfrac{3(m+1)}{2(m-1)}=-1\iff3m+3=-2m+2\iff5m=-1\iff m=-\dfrac15.$$

### Pourquoi les autres réponses sont fausses

- **a)** $m=\dfrac15$ : erreur de signe en résolvant $5m+1=0$.
- **b)** $m=-5$ : on a écrit $p\times p'=1$ au lieu de $-1$.
- **c)** $m=\pm\sqrt7$ : c'est la condition de parallélisme $(m+1)(m-1)-2\times3=0$, pas celle de perpendicularité.

</details>

Avis : 

---

## 31. `cqc-interets-composes-prob-d-moyenne-3` (series D)

**A regarder :** Methode remplacee : logarithme neperien remplace par les puissances successives de 1,08.

**Enonce :**

Un capital est placé à $8\ \%$ par an à intérêts composés (les intérêts de chaque année s'ajoutent au capital). Au bout de combien d'années entières le capital aura-t-il, pour la première fois, au moins doublé ?

- a) $9$ ans
- b) $10$ ans
- c) $12$ ans
- d) $13$ ans

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Chaque année, le capital est multiplié par $1{,}08$ : après $n$ années, le capital $C_0$ devient $C_0\times1{,}08^n$ (suite géométrique de raison $1{,}08$). On cherche le plus petit entier $n$ tel que $1{,}08^n\geq2$, en calculant les puissances successives à la calculatrice.

### Corrigé

À la calculatrice (valeurs arrondies au millième) : $1{,}08^9\approx1{,}999<2$ et $1{,}08^{10}\approx2{,}159\geq2$. La suite $(1{,}08^n)$ étant croissante, le plus petit entier convenable est $n=10$ : le capital a doublé au bout de $10$ ans.

### Pourquoi les autres réponses sont fausses

- **a)** $1{,}08^9\approx1{,}999$ s'arrondit à $2$, mais reste strictement inférieur à $2$ : le capital n'a pas encore doublé.
- **c)** Raisonnement en intérêts simples ($8n\geq100$ donne $n\geq12{,}5$), avec en plus un arrondi par défaut.
- **d)** Raisonnement en intérêts simples ($8n\geq100$, donc $n=13$) : les intérêts ne sont pas réinvestis.

</details>

Avis : 

---

