# Pilote Maths Probatoire : 23 QCM a faire relire par l'enseignant (campagne B1)

Date : 2026-10-27. Pilote de conversion de questions ouvertes de maths Probatoire en QCM (5 themes : derivee d'un polynome, signe d'un trinome, moyenne d'une serie groupee, limite d'une fonction rationnelle, tangente horizontale ; series A et C/E). **Aucune de ces 23 questions n'est en ligne** : elles ne le seront qu'apres votre avis. Les 23 ont ete resolues a l'aveugle par un relecteur independant (23 accords sur 23). Il reste a juger : le niveau de la classe de Premiere pour chaque serie indiquee, le realisme des distracteurs et les conventions d'enseignement. La serie A suit un programme plus leger (fonctions, denombrement, statistiques).

Pour chaque question : **OK**, **a corriger** (dire quoi) ou **a retirer**.

## 1. `cqc-derivee-d-un-polynome-prob-a-moyenne-5` (series A)

**Remarque du relecteur :** LIMITE : nombre dérivé et équation de tangente en série A, à la limite haute du programme allégé de cette série.

**Enonce :**

Soit $f(x)=x^2+x$. Quelle est l'équation de la tangente à la courbe de $f$ au point d'abscisse $1$ ?

- a) $y=3x+2$
- b) $y=2x+1$
- c) $y=3x-1$
- d) $y=3x-3$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

$y=f'(a)(x-a)+f(a)$.

### Corrigé

$f'(x)=2x+1$ donc $f'(1)=3$ ; $f(1)=2$. Tangente : $y=3(x-1)+2=3x-1$.

### Pourquoi les autres réponses sont fausses

- **a)** $y=3x+2$ : on a écrit $y=f'(a)x+f(a)$ en oubliant de remplacer $x$ par $x-a$.
- **b)** $y=2x+1$ : on a inversé les rôles de $f(1)=2$ et $f'(1)=3$, en prenant $2$ comme coefficient directeur.
- **d)** $y=3x-3$ : on a oublié d'ajouter $f(1)$, ce qui donne $y=3(x-1)$.

</details>

Avis : 

---

## 2. `cqc-derivee-d-un-polynome-prob-a-moyenne-3` (series A)

**Remarque du relecteur :** LIMITE : la série A doit dériver un polynôme de degré 3 et étudier le signe de la dérivée sans que celle-ci soit donnée (contrairement à d'autres items A) ; à confirmer au programme de Première A.

**Enonce :**

Soit $f(x)=-x^3+3x$ définie sur $\mathbb R$. Quel est le maximum local de $f$, et en quelle abscisse est-il atteint ?

- a) $2$, atteint en $x=1$
- b) $-2$, atteint en $x=-1$
- c) $4$, atteint en $x=1$
- d) $3$, atteint en $x=0$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

$f'(x)=-3x^2+3=3(1-x)(1+x)$ ; on étudie le signe de $f'$ pour dresser les variations.

### Corrigé

$f'>0\iff-1<x<1$. $f$ décroît sur $]-\infty\,;-1]$, croît sur $[-1\,;1]$, décroît sur $[1\,;+\infty[$. $f(-1)=1-3=-2$ (minimum local) et $f(1)=-1+3=2$ (maximum local).

Le maximum local vaut donc $2$, atteint en $x=1$.

### Pourquoi les autres réponses sont fausses

- **b)** Erreur sur le signe de $f'$ : on croit $f$ croissante puis décroissante autour de $-1$ ; or $f(-1)=-2$ est un minimum local.
- **c)** On a calculé $f(1)$ avec $+x^3$ au lieu de $-x^3$ : $1+3=4$.
- **d)** On a confondu $f$ et $f'$ : $3=f'(0)$ est la plus grande valeur de $f'$, pas un maximum de $f$.

</details>

Avis : 

---

## 3. `cqc-derivee-d-un-polynome-prob-a-faible-0` (series A)

**Remarque du relecteur :** LIMITE : lien signe de la dérivée / extremum en série A, à la limite haute du programme allégé de cette série.

**Enonce :**

Soit $f$ une fonction polynôme et $a$ un réel. On sait que $f'$ s'annule en $a$ en changeant de signe. Que peut-on en déduire ?

- a) $f(a)=0$
- b) $f$ change de signe en $a$
- c) la courbe de $f$ admet une tangente verticale au point d'abscisse $a$
- d) $f$ admet un extremum local en $a$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Le signe de $f'$ donne le sens de variation de $f$.

### Corrigé

Si $f'(x)>0$ sur un intervalle, $f$ est strictement **croissante** ; si $f'(x)<0$, elle est strictement **décroissante**. Quand $f'$ s'annule en $a$ en changeant de signe, $f$ change de sens de variation en $a$ : $f$ admet un **extremum local** en $a$.

### Pourquoi les autres réponses sont fausses

- **a)** C'est $f'(a)$ qui est nul, pas $f(a)$ : on a confondu $f$ et sa dérivée.
- **b)** Le signe de $f'$ renseigne sur les variations de $f$, pas sur le signe de $f$.
- **c)** $f'(a)=0$ signifie que la tangente en $a$ est horizontale, pas verticale.

</details>

Avis : 

---

## 4. `cqc-signe-d-un-trinome-prob-a-moyenne-4` (series A)

**Enonce :**

Quel est le signe du trinôme $x^2+2x+5$ selon les valeurs du réel $x$ ?

- a) négatif sur $]-1-\sqrt6\,;-1+\sqrt6[$ et positif à l'extérieur
- b) strictement positif pour tout réel $x$
- c) strictement négatif pour tout réel $x$
- d) nul en $-1$ et strictement positif pour $x\neq-1$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

On calcule le discriminant et on applique la règle du signe.

### Corrigé

$\Delta=4-20=-16<0$ et $a=1>0$ : le trinôme est du signe de $a$ pour tout $x$, donc $x^2+2x+5>0$ pour tout $x$ (aussi : $x^2+2x+5=(x+1)^2+4\ge4$).

### Pourquoi les autres réponses sont fausses

- **a)** On a calculé $\Delta=4+20=24$ (erreur de signe sur $-4ac$), d'où deux racines $-1\pm\sqrt6$ qui n'existent pas.
- **c)** Quand $\Delta<0$, le trinôme est du signe de $a$, et non du signe contraire de $a$.
- **d)** On a confondu $x^2+2x+5$ avec $(x+1)^2$, qui s'annule en $-1$ ; ici $(x+1)^2+4\ge4$ ne s'annule jamais.

</details>

Avis : 

---

## 5. `cqc-signe-d-un-trinome-prob-a-moyenne-2` (series A)

**Enonce :**

Quel est le signe du trinôme $x^2-5x+6$ selon les valeurs du réel $x$ ?

- a) positif sur $]2\,;3[$ et négatif pour $x<2$ ou $x>3$
- b) négatif sur $]-3\,;-2[$ et positif pour $x<-3$ ou $x>-2$
- c) négatif sur $]2\,;3[$ et positif pour $x<2$ ou $x>3$
- d) négatif sur $]1\,;6[$ et positif pour $x<1$ ou $x>6$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

On cherche les racines : $\Delta=b^2-4ac$.

### Corrigé

$\Delta=25-24=1>0$ ; racines $x_1=\dfrac{5-1}2=2$ et $x_2=\dfrac{5+1}2=3$. Comme $a=1>0$ : positif pour $x<2$ ou $x>3$, négatif pour $2<x<3$, nul en $2$ et $3$.

### Pourquoi les autres réponses sont fausses

- **a)** Règle inversée : le trinôme est du signe de $a$ à l'extérieur des racines et du signe contraire entre elles.
- **b)** Erreur de signe sur les racines ($-2$ et $-3$ au lieu de $2$ et $3$) : on a oublié le signe de $-b$.
- **d)** $1$ et $6$ ont bien pour produit $6$, mais leur somme vaut $7$ et non $5$ : ce ne sont pas les racines.

</details>

Avis : 

---

## 6. `cqc-moyenne-d-une-serie-groupee-prob-a-moyenne-3` (series A)

**Enonce :**

Les âges de $35$ personnes sont répartis ainsi : $[10\,;20[$ : $8$ ; $[20\,;30[$ : $12$ ; $[30\,;40[$ : $10$ ; $[40\,;50[$ : $5$. Quel est l'âge moyen, arrondi au dixième ?

- a) $23{,}4$ ans
- b) $33{,}4$ ans
- c) $30$ ans
- d) $28{,}4$ ans

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

On remplace chaque classe par son centre : $15$, $25$, $35$, $45$.

### Corrigé

$\bar x=\dfrac{8\times15+12\times25+10\times35+5\times45}{35}=\dfrac{120+300+350+225}{35}=\dfrac{995}{35}\approx28{,}4$ ans (arrondi au dixième).

### Pourquoi les autres réponses sont fausses

- **a)** On a pris les bornes inférieures $10$, $20$, $30$, $40$ au lieu des centres : $\dfrac{820}{35}\approx23{,}4$.
- **b)** On a pris les bornes supérieures $20$, $30$, $40$, $50$ : $\dfrac{1170}{35}\approx33{,}4$.
- **c)** On a fait la moyenne des quatre centres sans tenir compte des effectifs : $\dfrac{15+25+35+45}{4}=30$.

</details>

Avis : 

---

## 7. `cqc-moyenne-d-une-serie-groupee-prob-a-faible-0` (series A)

**Enonce :**

Une série statistique est regroupée en $p$ classes d'effectifs $n_1,\dots,n_p$, d'effectif total $N$. On note $c_i$ le centre de la classe numéro $i$. Quelle formule donne la moyenne (approchée) $\bar x$ de la série ?

- a) $\bar x=\dfrac{n_1c_1+\dots+n_pc_p}{p}$
- b) $\bar x=\dfrac{n_1c_1+\dots+n_pc_p}{N}$
- c) $\bar x=\dfrac{c_1+\dots+c_p}{p}$
- d) $\bar x=\dfrac{n_1+\dots+n_p}{p}$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

On remplace chaque classe par son centre.

### Corrigé

On associe à chaque classe son **centre** $c_i$ puis $\bar x=\dfrac{n_1c_1+n_2c_2+\dots+n_pc_p}{N}$. C'est une valeur **approchée** de la moyenne réelle (on suppose les valeurs réparties uniformément dans la classe).

### Pourquoi les autres réponses sont fausses

- **a)** On divise par le nombre de classes $p$ au lieu de l'effectif total $N$.
- **c)** On oublie de pondérer les centres par les effectifs : chaque classe compterait autant, quel que soit son effectif.
- **d)** On divise la somme des effectifs par $p$ : c'est l'effectif moyen par classe, pas la moyenne de la série.

</details>

Avis : 

---

## 8. `cqc-limite-d-une-fonction-rationnelle-moyenne-4` (series C/E)

**Enonce :**

Quelle est la valeur de $\displaystyle\lim_{x\to-\infty}\dfrac{x^3+2x}{2x^2-1}$ ?

- a) $-\infty$
- b) $+\infty$
- c) $\dfrac12$
- d) $0$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

En $\pm\infty$, une fraction rationnelle a la même limite que le quotient de ses termes de plus haut degré.

### Corrigé

Termes de plus haut degré : $x^3$ et $2x^2$, d'où $\dfrac{x^3}{2x^2}=\dfrac x2$.

Or $\dfrac x2\to-\infty$ quand $x\to-\infty$, donc
$$\lim_{x\to-\infty}\dfrac{x^3+2x}{2x^2-1}=-\infty.$$

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de signe : $\dfrac x2$ tend vers $-\infty$, pas vers $+\infty$, quand $x\to-\infty$.
- **c)** $\dfrac12$ serait le quotient des coefficients dominants si les degrés étaient égaux ; ici $3>2$.
- **d)** La limite vaut $0$ quand le degré du numérateur est le plus petit ; ici c'est l'inverse.

</details>

Avis : 

---

## 9. `cqc-limite-d-une-fonction-rationnelle-moyenne-2` (series C/E)

**Enonce :**

Quelle est la valeur de $\displaystyle\lim_{x\to2}\dfrac{x^2-4}{x^2-5x+6}$ ?

- a) $4$
- b) $0$
- c) $-4$
- d) $-\dfrac14$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Si numérateur et dénominateur s'annulent en $a$, on lève l'indétermination $\frac00$ en factorisant par $(x-a)$ puis en simplifiant.

### Corrigé

En $x=2$ : numérateur $=0$ et dénominateur $=4-10+6=0$ : forme indéterminée $\frac00$.

$x^2-4=(x-2)(x+2)$ et $x^2-5x+6=(x-2)(x-3)$, donc pour $x\neq2$ :
$$\dfrac{x^2-4}{x^2-5x+6}=\dfrac{x+2}{x-3}\xrightarrow[x\to2]{}\dfrac{4}{-1}=-4.$$

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe : $2-3=-1$ et non $1$.
- **b)** On a conclu que la limite est nulle parce que le numérateur s'annule, en oubliant que le dénominateur s'annule aussi.
- **d)** On a inversé numérateur et dénominateur : $\dfrac{-1}{4}$ au lieu de $\dfrac{4}{-1}$.

</details>

Avis : 

---

## 10. `cqc-tangente-horizontale-prob-c-elevee-5` (series C)

**Enonce :**

Soit $f(x)=x^3+ax^2+bx$, où $a$ et $b$ sont des réels. La courbe de $f$ admet des tangentes horizontales aux points d'abscisses $-1$ et $2$. Quelles sont les équations de ces deux tangentes ?

- a) $y=2$ et $y=-16$
- b) $y=\dfrac12$ et $y=2$
- c) $x=-1$ et $x=2$
- d) $y=\dfrac72$ et $y=-10$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

$f'(x)=3x^2+2ax+b$. Si $f'$ s'annule en $-1$ et en $2$, alors $f'(x)=3(x+1)(x-2)$ : on identifie les coefficients.

### Corrigé

$f'(x)=3(x+1)(x-2)=3x^2-3x-6$. Par identification : $2a=-3\Rightarrow a=-\dfrac32$ et $b=-6$.
$f(x)=x^3-\dfrac32x^2-6x$.

$f(-1)=-1-\dfrac32+6=\dfrac72$ et $f(2)=8-6-12=-10$.
Les tangentes ont pour équations $y=\dfrac72$ (en $x=-1$) et $y=-10$ (en $x=2$).

### Pourquoi les autres réponses sont fausses

- **a)** On a identifié $a=-3$ en oubliant le facteur $2$ de $2a$ ; on obtient alors $f(-1)=2$ et $f(2)=-16$.
- **b)** On a écrit $f'(x)=(x+1)(x-2)$ sans le facteur $3$, d'où $a=-\dfrac12$, $b=-2$, puis $f(-1)=\dfrac12$ et $f(2)=2$.
- **c)** Les droites d'équations $x=-1$ et $x=2$ sont verticales ; une tangente horizontale a une équation de la forme $y=k$.

</details>

Avis : 

---

## 11. `cqc-tangente-horizontale-prob-c-moyenne-3` (series C)

**Enonce :**

Soit $f(x)=\dfrac{x^2+1}x$, définie pour $x\neq0$. Quelles sont les tangentes horizontales à sa courbe ?

- a) $y=1$ et $y=-1$
- b) $y=2$ et $y=-2$
- c) seulement $y=2$
- d) aucune tangente horizontale

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

$f'(x)=\dfrac{x^2-1}{x^2}$ s'annule quand $x^2-1=0$ (valeur $x=0$ exclue du domaine).

### Corrigé

$f'(x)=\dfrac{x^2-1}{x^2}=0\iff x=\pm1$. $f(1)=2$ et $f(-1)=-2$.
Tangentes horizontales : $y=2$ au point $(1\,;2)$ et $y=-2$ au point $(-1\,;-2)$.

### Pourquoi les autres réponses sont fausses

- **a)** On a donné les abscisses $\pm1$ au lieu des ordonnées $f(\pm1)=\pm2$.
- **c)** On a oublié la solution $x=-1$ de $x^2=1$.
- **d)** On a dérivé le quotient avec $u'v+uv'$ au lieu de $u'v-uv'$ : $\dfrac{3x^2+1}{x^2}$ ne s'annule jamais.

</details>

Avis : 

---

## 12. `cqc-tangente-horizontale-prob-c-faible-0` (series C)

**Enonce :**

Soit $f(x)=x^2-2x+3$. En quel point la courbe de $f$ admet-elle une tangente horizontale, et quelle est l'équation de cette tangente ?

- a) au point $(1\,;2)$, tangente $y=2$
- b) au point $(1\,;2)$, tangente $x=1$
- c) au point $(-1\,;6)$, tangente $y=6$
- d) au point $(0\,;3)$, tangente $y=3$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

La tangente en $a$ est horizontale si $f'(a)=0$ ; son équation est alors $y=f(a)$.

### Corrigé

$f'(x)=2x-2=0\iff x=1$. $f(1)=1-2+3=2$. La tangente horizontale au point $(1\,;2)$ a pour équation $y=2$.

### Pourquoi les autres réponses sont fausses

- **b)** La droite d'équation $x=1$ est verticale ; une tangente horizontale a une équation $y=f(a)$.
- **c)** Erreur de signe : $2x-2=0$ donne $x=1$ et non $x=-1$ (et $f(-1)=6$).
- **d)** On a pris le point d'abscisse $0$ (ordonnée à l'origine $f(0)=3$), où $f'(0)=-2\neq0$.

</details>

Avis : 

---

## 13. `cqc-derivee-d-un-polynome-prob-a-moyenne-4` (series A)

**Enonce :**

On considère la fonction $f$ définie sur $\mathbb{R}$ par $f(x)=x^3-6x^2+9x$, dont la dérivée est $f'(x)=3(x-1)(x-3)$. Sur quel intervalle la fonction $f$ est-elle décroissante ?

- a) $[0\,;3]$
- b) $[1\,;3]$
- c) $]-\infty\,;1]$ et $[3\,;+\infty[$
- d) $[-3\,;-1]$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

On étudie le signe du trinôme $3(x-1)(x-3)$ : il est du signe de $3$ (positif) à l'extérieur des racines $1$ et $3$, négatif entre elles. La fonction est décroissante là où sa dérivée est négative.

### Corrigé

$f'(x)>0$ pour $x<1$ ou $x>3$, $f'(x)<0$ pour $1<x<3$. Donc $f$ croît jusqu'à $f(1)=1-6+9=4$, décroît sur $[1\,;3]$ jusqu'à $f(3)=27-54+27=0$, puis croît.

La fonction $f$ est décroissante sur $[1\,;3]$.

### Pourquoi les autres réponses sont fausses

- **a)** $0$ et $3$ sont les racines de $f(x)=x(x-3)^2$, pas celles de $f'(x)$ : on a confondu le signe de $f$ et celui de $f'$.
- **c)** Sur ces intervalles $f'(x)>0$ : la fonction y est croissante, pas décroissante.
- **d)** Erreur de signe sur les racines de $f'$ : $3(x-1)(x-3)$ s'annule en $1$ et $3$, pas en $-1$ et $-3$.

</details>

Avis : 

---

## 14. `cqc-derivee-d-un-polynome-prob-a-moyenne-2` (series A)

**Enonce :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=x^2-6x+5$. Laquelle des affirmations suivantes décrit correctement les variations de $f$ ?

- a) $f$ est croissante sur $]-\infty\,;3]$, décroissante sur $[3\,;+\infty[$ et admet un maximum égal à $-4$.
- b) $f$ est décroissante sur $]-\infty\,;-3]$, croissante sur $[-3\,;+\infty[$ et admet un minimum égal à $32$.
- c) $f$ est décroissante sur $]-\infty\,;3]$, croissante sur $[3\,;+\infty[$ et admet un minimum égal à $-4$.
- d) $f$ est décroissante sur $]-\infty\,;3]$, croissante sur $[3\,;+\infty[$ et admet un minimum égal à $5$.

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

On calcule la dérivée $f'(x)=2x-6$, on étudie son signe, puis on calcule la valeur de $f$ là où $f'$ s'annule en changeant de signe.

### Corrigé

$f'(x)=2(x-3)$ : négative pour $x<3$, positive pour $x>3$. Donc $f$ est décroissante sur $]-\infty\,;3]$ puis croissante sur $[3\,;+\infty[$ ; elle admet un minimum $f(3)=9-18+5=-4$.

### Pourquoi les autres réponses sont fausses

- **a)** Le sens de variation est inversé : pour $x<3$, $f'(x)<0$, donc $f$ décroît ; $-4$ est un minimum, pas un maximum.
- **b)** Erreur de signe sur la racine de $f'$ : $2x-6=0$ donne $x=3$, pas $x=-3$ (et $f(-3)=32$).
- **d)** $5=f(0)$ est l'ordonnée à l'origine, pas la valeur du minimum, qui est atteint en $x=3$.

</details>

Avis : 

---

## 15. `cqc-signe-d-un-trinome-prob-a-moyenne-5` (series A)

**Enonce :**

Quel est l'ensemble des solutions dans $\mathbb{R}$ de l'inéquation $x^2-2x-8\le0$ ?

- a) $]-\infty\,;-2]\cup[4\,;+\infty[$
- b) $[-4\,;2]$
- c) $]-2\,;4[$
- d) $[-2\,;4]$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

On calcule le discriminant pour trouver les racines ; le trinôme est du signe de $a$ à l'extérieur des racines et du signe contraire entre elles.

### Corrigé

$\Delta=4+32=36$ ; racines $\dfrac{2-6}2=-2$ et $\dfrac{2+6}2=4$. Comme $a=1>0$, le trinôme est négatif ou nul entre ses racines (bornes comprises) : $x^2-2x-8\le0\iff x\in[-2\,;4]$.

### Pourquoi les autres réponses sont fausses

- **a)** C'est l'ensemble où le trinôme est positif ou nul : on a oublié que, pour $a>0$, il est négatif entre les racines.
- **b)** Erreur de signe dans le calcul des racines : $\dfrac{-b\pm\sqrt\Delta}{2a}$ avec $b=-2$ donne $-2$ et $4$, pas $-4$ et $2$.
- **c)** L'inégalité est large ($\le$) : les racines $-2$ et $4$, où le trinôme vaut $0$, sont solutions.

</details>

Avis : 

---

## 16. `cqc-signe-d-un-trinome-prob-a-moyenne-3` (series A)

**Enonce :**

Quel est l'ensemble des solutions dans $\mathbb{R}$ de l'inéquation $-x^2+4x-3>0$ ?

- a) $]1\,;3[$
- b) $]-\infty\,;1[\cup]3\,;+\infty[$
- c) $[1\,;3]$
- d) $]-3\,;-1[$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

$a=-1<0$ : le trinôme est négatif à l'extérieur de ses racines et positif entre elles.

### Corrigé

$\Delta=16-12=4$ ; racines $\dfrac{-4-2}{-2}=3$ et $\dfrac{-4+2}{-2}=1$. Comme $a<0$, le trinôme est positif entre les racines : $-x^2+4x-3>0\iff x\in]1\,;3[$.

### Pourquoi les autres réponses sont fausses

- **b)** On a appliqué la règle valable pour $a>0$ : ici $a=-1<0$, le trinôme est négatif à l'extérieur des racines.
- **c)** L'inégalité est stricte ($>$) : en $1$ et en $3$ le trinôme vaut $0$, ces valeurs ne sont pas solutions.
- **d)** Erreur de signe sur les racines : $-x^2+4x-3$ s'annule en $1$ et $3$, pas en $-1$ et $-3$.

</details>

Avis : 

---

## 17. `cqc-signe-d-un-trinome-prob-a-faible-0` (series A)

**Enonce :**

On considère un trinôme $ax^2+bx+c$ avec $a<0$ et dont le discriminant $\Delta=b^2-4ac$ est strictement positif. On note $x_1<x_2$ ses deux racines. Quel est le signe de ce trinôme ?

- a) Il est négatif pour tout réel $x$.
- b) Il est négatif entre $x_1$ et $x_2$ et positif à l'extérieur.
- c) Il est positif entre $x_1$ et $x_2$ et négatif à l'extérieur.
- d) Il est positif pour tout réel $x$.

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Le signe du trinôme dépend du signe de $a$ et de la position de $x$ par rapport aux racines :
- si $\Delta<0$ : le trinôme est du signe de $a$ pour tout $x$ ;
- si $\Delta=0$ : il est du signe de $a$ sauf en la racine double, où il s'annule ;
- si $\Delta>0$ : il est du signe de $a$ à l'extérieur des racines, du signe contraire entre les racines.

### Corrigé

Ici $\Delta>0$ et $a<0$ : le trinôme est négatif à l'extérieur de $[x_1\,;x_2]$ et positif entre $x_1$ et $x_2$ (il s'annule en $x_1$ et $x_2$). Par exemple, $-x^2+4x-3$ a pour racines $1$ et $3$ et vaut $1>0$ en $x=2$.

### Pourquoi les autres réponses sont fausses

- **a)** « Du signe de $a$ pour tout $x$ » est la règle du cas $\Delta<0$ ; ici le trinôme a deux racines et change de signe.
- **b)** C'est la règle pour $a>0$ : on a oublié que le signe de $a$ s'applique à l'extérieur des racines.
- **d)** On a confondu le signe de $\Delta$ avec celui du trinôme : $\Delta>0$ ne signifie pas que le trinôme est positif.

</details>

Avis : 

---

## 18. `cqc-moyenne-d-une-serie-groupee-prob-a-moyenne-2` (series A)

**Enonce :**

Une série statistique est regroupée en classes : $[0\,;4[$ : effectif $6$ ; $[4\,;8[$ : effectif $10$ ; $[8\,;12[$ : effectif $4$. En utilisant les centres des classes, quelle est la moyenne de cette série ?

- a) $3{,}6$
- b) $5{,}6$
- c) $6$
- d) $7{,}6$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

On remplace chaque classe par son centre (demi-somme des bornes), puis on calcule la moyenne pondérée par les effectifs. Centres : $2$, $6$, $10$ ; effectif total $20$.

### Corrigé

$\bar x=\dfrac{6\times2+10\times6+4\times10}{20}=\dfrac{12+60+40}{20}=\dfrac{112}{20}=5{,}6$.

### Pourquoi les autres réponses sont fausses

- **a)** On a utilisé les bornes inférieures $0$, $4$, $8$ au lieu des centres : $\dfrac{72}{20}=3{,}6$.
- **c)** On a fait la moyenne simple des trois centres, $\dfrac{2+6+10}{3}=6$, sans tenir compte des effectifs.
- **d)** On a utilisé les bornes supérieures $4$, $8$, $12$ au lieu des centres : $\dfrac{152}{20}=7{,}6$.

</details>

Avis : 

---

## 19. `cqc-limite-d-une-fonction-rationnelle-elevee-5` (series C/E)

**Enonce :**

On considère la fonction $f$ définie sur $\mathbb{R}\setminus\{-1\}$ par $f(x)=\dfrac{2x^2-x+3}{x+1}$. Quelle droite est asymptote oblique à la courbe de $f$ en $+\infty$ et en $-\infty$ ?

- a) $y=2x$
- b) $y=2x-1$
- c) $y=2x+1$
- d) $y=2x-3$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Pour une asymptote oblique, on écrit $f(x)=ax+b+\dfrac{c}{x+1}$ par division euclidienne du numérateur par le dénominateur, puis on montre que $f(x)-(ax+b)$ tend vers $0$.

### Corrigé

En $\pm\infty$, $f(x)$ se comporte comme $\dfrac{2x^2}{x}=2x$, donc $\lim_{x\to+\infty}f(x)=+\infty$ et $\lim_{x\to-\infty}f(x)=-\infty$ : une asymptote oblique est possible.

Comme $(x+1)(2x-3)=2x^2-x-3$, on a $2x^2-x+3=(x+1)(2x-3)+6$, d'où
$$f(x)=2x-3+\dfrac{6}{x+1}.$$
Alors $f(x)-(2x-3)=\dfrac6{x+1}\to0$ en $\pm\infty$ : la droite d'équation $y=2x-3$ est asymptote oblique. (La droite $x=-1$ est par ailleurs asymptote verticale.)

### Pourquoi les autres réponses sont fausses

- **a)** On n'a gardé que le quotient des termes de plus haut degré, $\dfrac{2x^2}{x}=2x$ ; or $f(x)-2x$ tend vers $-3$, pas vers $0$.
- **b)** On a divisé seulement $2x^2-x$ par $x$ en négligeant le $1$ du dénominateur ; la division complète par $x+1$ donne $-3$ et non $-1$.
- **c)** On a divisé par $x-1$ au lieu de $x+1$ : $2x^2-x+3=(x-1)(2x+1)+4$.

</details>

Avis : 

---

## 20. `cqc-limite-d-une-fonction-rationnelle-moyenne-3` (series C/E)

**Enonce :**

Soit $f$ la fonction définie sur $\mathbb{R}\setminus\{1\}$ par $f(x)=\dfrac{2x+3}{x-1}$. Quelles sont les limites de $f$ en $1$, à droite et à gauche ?

- a) $\displaystyle\lim_{x\to1^+}f(x)=+\infty$ et $\displaystyle\lim_{x\to1^-}f(x)=-\infty$
- b) $\displaystyle\lim_{x\to1^+}f(x)=-\infty$ et $\displaystyle\lim_{x\to1^-}f(x)=+\infty$
- c) $\displaystyle\lim_{x\to1^+}f(x)=+\infty$ et $\displaystyle\lim_{x\to1^-}f(x)=+\infty$
- d) $\displaystyle\lim_{x\to1^+}f(x)=5$ et $\displaystyle\lim_{x\to1^-}f(x)=5$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Quand le dénominateur tend vers $0$ et le numérateur vers un réel non nul, la limite est infinie ; on conclut par le signe du numérateur et du dénominateur de chaque côté.

### Corrigé

En $x=1$, le numérateur tend vers $2\times1+3=5>0$ et le dénominateur vers $0$.

- Si $x\to1^+$ : $x-1>0$, donc $f(x)\to+\infty$.
- Si $x\to1^-$ : $x-1<0$, donc $f(x)\to-\infty$.

La droite d'équation $x=1$ est asymptote verticale à la courbe.

### Pourquoi les autres réponses sont fausses

- **b)** Les signes sont inversés : à droite de $1$, $x-1>0$ et le quotient est positif.
- **c)** On a oublié que le dénominateur $x-1$ change de signe en $1$ : il est négatif à gauche.
- **d)** On a confondu la limite du numérateur ($5$) avec celle du quotient ; un dénominateur qui tend vers $0$ donne une limite infinie.

</details>

Avis : 

---

## 21. `cqc-limite-d-une-fonction-rationnelle-faible-1` (series C/E)

**Enonce :**

Que vaut $\displaystyle\lim_{x\to+\infty}\dfrac{2x+1}{x^2-3}$ ?

- a) $2$
- b) $+\infty$
- c) $0$
- d) $-\dfrac13$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

En $\pm\infty$, une fonction rationnelle a la même limite que le quotient de ses termes de plus haut degré.

### Corrigé

Termes de plus haut degré : $2x$ et $x^2$, d'où $\dfrac{2x}{x^2}=\dfrac2x\to0$.
$$\lim_{x\to+\infty}\dfrac{2x+1}{x^2-3}=0.$$

### Pourquoi les autres réponses sont fausses

- **a)** On a fait le quotient des coefficients $\dfrac21$ sans tenir compte des degrés : cette règle ne vaut que si les degrés sont égaux.
- **b)** Le numérateur tend bien vers $+\infty$, mais le dénominateur, de degré plus élevé, croît plus vite : le quotient tend vers $0$.
- **d)** $-\dfrac13$ est la valeur de la fonction en $x=0$ (quotient des termes constants), pas sa limite en $+\infty$.

</details>

Avis : 

---

## 22. `cqc-tangente-horizontale-prob-c-moyenne-4` (series C)

**Enonce :**

On cherche les réels $b$ et $c$ tels que la parabole d'équation $y=x^2+bx+c$ passe par le point $A(0\,;5)$ et admette une tangente horizontale au point d'abscisse $2$. Quelles sont les valeurs de $b$ et $c$, et quelle est alors l'équation de cette tangente ?

- a) $b=-4$, $c=5$ ; tangente $y=1$
- b) $b=4$, $c=5$ ; tangente $y=17$
- c) $b=-4$, $c=5$ ; tangente $x=2$
- d) $b=-2$, $c=5$ ; tangente $y=5$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

On note $f(x)=x^2+bx+c$. $A$ appartient à la courbe, ce qui donne $c=f(0)$. La tangente horizontale en $2$ impose $f'(2)=0$ avec $f'(x)=2x+b$. La tangente horizontale au point d'abscisse $2$ a pour équation $y=f(2)$.

### Corrigé

$c=f(0)=5$. $f'(2)=4+b=0\Rightarrow b=-4$. Donc $f(x)=x^2-4x+5$ et $f(2)=4-8+5=1$.
La tangente au point d'abscisse $2$ est la droite $y=1$ : c'est la tangente au sommet de la parabole.

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de signe : $4+b=0$ donne $b=-4$, pas $b=4$ ; avec $b=4$, on obtiendrait $f(2)=17$.
- **c)** Une tangente horizontale a une équation de la forme $y=k$ ; $x=2$ est une droite verticale.
- **d)** Mauvaise dérivée : la dérivée de $x^2$ est $2x$, pas $x$ ; on obtient alors $2+b=0$, soit $b=-2$ à tort.

</details>

Avis : 

---

## 23. `cqc-tangente-horizontale-prob-c-moyenne-2` (series C)

**Enonce :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=x^3-3x^2+1$. En quels points de sa courbe représentative la tangente est-elle horizontale ?

- a) Uniquement au point $(2\,;-3)$
- b) Aux points $(0\,;1)$ et $(3\,;1)$
- c) Aux points $(0\,;1)$ et $(-2\,;-19)$
- d) Aux points $(0\,;1)$ et $(2\,;-3)$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

La tangente est horizontale là où le nombre dérivé est nul : on résout $f'(x)=0$, puis on calcule $f$ en chaque solution pour obtenir l'ordonnée du point.

### Corrigé

$f'(x)=3x^2-6x=3x(x-2)=0\iff x=0$ ou $x=2$.
$f(0)=1$ et $f(2)=8-12+1=-3$. Points : $(0\,;1)$ (tangente $y=1$) et $(2\,;-3)$ (tangente $y=-3$).

### Pourquoi les autres réponses sont fausses

- **a)** On a simplifié $3x^2-6x=0$ par $x$ et perdu la solution $x=0$.
- **b)** On a résolu $f(x)=1$ (c'est-à-dire $x^3-3x^2=0$) au lieu de $f'(x)=0$ ; en $x=3$, $f'(3)=9\neq0$.
- **c)** Erreur de signe dans la factorisation : $3x^2-6x=3x(x-2)$, pas $3x(x+2)$.

</details>

Avis : 

---

