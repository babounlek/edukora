# Pilote Maths BAC : 20 QCM a faire relire par l'enseignant (campagne B1)

Date : 2026-10-27. Pilote de conversion de questions ouvertes de maths Probatoire en QCM (5 themes : exponentielle, derivee seconde, integrale, equation differentielle, esperance mathematique ; series A, C, D, E et TI). **Aucune de ces 23 questions n'est en ligne** : elles ne le seront qu'apres votre avis. Les 20 ont ete resolues a l'aveugle par un relecteur independant (19 accords sur 20). Il reste a juger : le niveau de la classe de Premiere pour chaque serie indiquee, le realisme des distracteurs et les conventions d'enseignement. La serie A suit un programme plus leger (equations, limites, derivees, primitives, logarithme, exponentielle, etudes de fonctions, statistiques, probabilites) : en particulier la convexite et les equations differentielles y figurent-elles ?

Pour chaque question : **OK**, **a corriger** (dire quoi) ou **a retirer**.

## 1. `cqc-exponentielle-elevee-0` (series A/C/D/TI)

**Enonce :**

On considère le système d'équations d'inconnues réelles $x$ et $y$ :
$$\begin{cases}2\ln(x+y)=\ln25\\ e^{x-y-1}=e^{2}\end{cases}$$
Quel est l'ensemble des solutions de ce système dans $\mathbb{R}^2$ ?

- a) $\{(4\,;\,1)\,;\,(-1\,;-4)\}$
- b) $\{(3\,;\,2)\}$
- c) $\{(4\,;\,1)\}$
- d) $\{(14\,;\,11)\}$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Une équation du type $n\ln(A)=\ln(k)$ se ramène à $\ln(A^n)=\ln(k)$, puis à $A^n=k$ grâce à l'équivalence $\ln a=\ln b \iff a=b$ (valable pour $a,b>0$). Attention : si $n$ est pair, l'équation $A^n=k$ admet en général deux solutions opposées pour $A$, mais une seule d'entre elles peut vérifier la condition d'existence $A>0$ imposée par le logarithme de départ. Il faut donc toujours revenir à cette condition avant de conclure.

### Corrigé

**Condition d'existence :** l'équation $2\ln(x+y)=\ln25$ exige $x+y>0$.

**Première équation :**
$$2\ln(x+y)=\ln25 \iff \ln\big((x+y)^2\big)=\ln25 \iff (x+y)^2=25 \iff x+y=5 \text{ ou } x+y=-5$$

La condition $x+y>0$ élimine $x+y=-5$. **Il reste $x+y=5$** $(1)$.

**Seconde équation :**
$$e^{x-y-1}=e^{2} \iff x-y-1=2 \iff x-y=3 \quad (2)$$

**Résolution du système formé par (1) et (2) :** en additionnant membre à membre, $2x=8$, donc $x=4$, puis $y=5-4=1$.

**Vérification :** $x+y=5>0$ ; $2\ln5=\ln25$ et $e^{4-1-1}=e^{2}$.

**L'ensemble des solutions est $\{(4\,;\,1)\}$.** La valeur $x+y=-5$ a été écartée par la condition d'existence $x+y>0$.

### Pourquoi les autres réponses sont fausses

- **a)** On a conservé $x+y=-5$ (qui donne $(-1\,;-4)$) sans vérifier la condition d'existence $x+y>0$.
- **b)** Erreur sur la seconde équation : $x-y-1=2$ a été transformée en $x-y=1$ au lieu de $x-y=3$.
- **d)** Le coefficient $2$ a été oublié : on a écrit $x+y=25$ au lieu de $(x+y)^2=25$.

</details>

Avis : 

---

## 2. `cqc-integrale-elevee-0` (series C/D/E)

**Enonce :**

Quelle est la valeur exacte de $I=\displaystyle\int_1^e x\ln x\,dx$ ?

- a) $\dfrac{e^2+1}{4}$
- b) $\dfrac{e^2-1}{4}$
- c) $\dfrac{e^2}{4}$
- d) $\dfrac{3e^2-1}{4}$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Quand l'intégrande est le produit d'un polynôme et de $\ln x$, on intègre par parties en dérivant $\ln x$ (dont la dérivée $\dfrac1x$ simplifie le produit) et en intégrant le polynôme.

### Corrigé

Posons $u(x)=\ln x$, $v'(x)=x$, d'où $u'(x)=\dfrac1x$ et $v(x)=\dfrac{x^2}{2}$.

$I=\Big[\dfrac{x^2}{2}\ln x\Big]_1^e-\displaystyle\int_1^e\dfrac{x^2}{2}\cdot\dfrac1x\,dx=\dfrac{e^2}{2}-\displaystyle\int_1^e\dfrac x2\,dx=\dfrac{e^2}{2}-\Big[\dfrac{x^2}{4}\Big]_1^e$

$=\dfrac{e^2}{2}-\dfrac{e^2}{4}+\dfrac14=\dfrac{e^2+1}{4}$.

**Donc $I=\dfrac{e^2+1}{4}$.**

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de signe sur la borne inférieure : $-\Big[\dfrac{x^2}{4}\Big]_1^e$ donne $-\dfrac{e^2}{4}+\dfrac14$, et non $-\dfrac{e^2}{4}-\dfrac14$.
- **c)** La valeur en $1$ de $\dfrac{x^2}{4}$ a été oubliée, ce qui fait perdre le terme $\dfrac14$.
- **d)** Erreur de signe dans la formule d'intégration par parties : l'intégrale $\displaystyle\int_1^e\dfrac x2\,dx$ a été ajoutée au lieu d'être retranchée.

</details>

Avis : 

---

## 3. `cqc-integrale-moyenne-1` (series C/D/E)

**Enonce :**

Quelle est la valeur exacte de $\displaystyle\int_0^1(x+1)e^{-x}\,dx$ ?

- a) $\dfrac3e-2$
- b) $1-\dfrac2e$
- c) $2-\dfrac2e$
- d) $2-\dfrac3e$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Intégration par parties : $\displaystyle\int_a^b u\,v'=\Big[uv\Big]_a^b-\int_a^b u'\,v$. On dérive le facteur polynomial et on intègre l'exponentielle, en faisant attention à la primitive de $e^{-x}$, qui est $-e^{-x}$.

### Corrigé

Posons $u(x)=x+1$, $v'(x)=e^{-x}$, d'où $u'(x)=1$ et $v(x)=-e^{-x}$.

$\displaystyle\int_0^1(x+1)e^{-x}dx=\Big[-(x+1)e^{-x}\Big]_0^1+\int_0^1e^{-x}dx=\left(-2e^{-1}+1\right)+\Big[-e^{-x}\Big]_0^1$

$=-2e^{-1}+1+\left(-e^{-1}+1\right)=2-3e^{-1}=2-\dfrac3e$.

**La valeur cherchée est $2-\dfrac3e$.**

### Pourquoi les autres réponses sont fausses

- **a)** On a pris $v(x)=e^{-x}$ au lieu de $-e^{-x}$ comme primitive de $e^{-x}$ : tous les signes sont inversés.
- **b)** Le crochet a été calculé, mais l'intégrale restante $\displaystyle\int_0^1e^{-x}\,dx$ a été oubliée.
- **c)** Erreur dans le crochet : on a calculé $-e^{-1}+1$ au lieu de $-2e^{-1}+1$, en oubliant le facteur $x+1=2$ en $x=1$.

</details>

Avis : 

---

## 4. `cqc-integrale-faible-1` (series C/D/E)

**Enonce :**

Quelle est la valeur exacte de $\displaystyle\int_0^1 e^{2x}\,dx$ ?

- a) $2(e^2-1)$
- b) $\dfrac{e^2-1}{2}$
- c) $e^2-1$
- d) $\dfrac{e^2}{2}$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Une primitive de $x\mapsto e^{ax}$ est $x\mapsto\dfrac1a e^{ax}$ ($a\neq0$). On n'oublie pas la valeur de la primitive à la borne inférieure.

### Corrigé

$F(x)=\dfrac12 e^{2x}$, donc $\displaystyle\int_0^1 e^{2x}dx=\dfrac12e^{2}-\dfrac12e^{0}=\dfrac{e^2-1}{2}$.

### Pourquoi les autres réponses sont fausses

- **a)** On a dérivé au lieu d'intégrer : on a multiplié par $2$ au lieu de diviser par $2$.
- **c)** Le facteur $\dfrac12$ de la primitive a été oublié : $e^{2x}$ n'est pas une primitive de $e^{2x}$.
- **d)** La valeur de la primitive en $0$ a été oubliée : $\dfrac12e^{0}=\dfrac12$ n'est pas nul.

</details>

Avis : 

---

## 5. `cqc-equation-differentielle-moyenne-4` (series C/D/E/TI)

**Enonce :**

Un échantillon radioactif se désintègre selon l'équation différentielle
$$N'(t) = -0{,}08\,N(t),$$
où $N(t)$ désigne la masse restante de l'échantillon (en grammes) à l'instant $t$ (exprimé en années), avec $N(0) = 240$.

On considère que l'échantillon est devenu inoffensif lorsque sa masse restante est strictement inférieure à $24$ g. Quel est le plus petit nombre entier d'années $n$ tel que $N(n)<24$ ?

- a) $29$
- b) $28$
- c) $13$
- d) $125$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Une équation du type $y' = ky$ (avec $k$ constant) a pour solutions $y(t) = y(0)e^{kt}$. Pour déterminer un seuil, on résout l'inéquation correspondante en isolant l'exponentielle puis en appliquant le logarithme népérien, en prenant garde au sens de l'inégalité lorsqu'on divise par un nombre négatif.

### Corrigé

L'équation $N'(t) = -0{,}08\,N(t)$ est de la forme $y' = ky$ avec $k = -0{,}08$, donc
$$N(t) = 240\,e^{-0{,}08t}.$$

On cherche $t$ tel que $N(t) < 24$ :
$$240\,e^{-0{,}08t} < 24 \iff e^{-0{,}08t} < 0{,}1 \iff -0{,}08t < \ln(0{,}1) = -\ln(10) \iff t > \frac{\ln(10)}{0{,}08}.$$
Or $\dfrac{\ln(10)}{0{,}08} \approx 28{,}78$ (valeur arrondie au centième).

Le plus petit entier strictement supérieur à $28{,}78$ est $29$. Contrôle : $N(28)\approx 25{,}55>24$ et $N(29)\approx 23{,}59<24$.

**Le plus petit entier cherché est $n=29$.**

### Pourquoi les autres réponses sont fausses

- **b)** On a arrondi $28{,}78$ par défaut ; or $N(28)\approx25{,}55$ g, ce qui est encore supérieur à $24$ g.
- **c)** On a utilisé le logarithme décimal au lieu du logarithme népérien : $-0{,}08t<-1$ donne $t>12{,}5$.
- **d)** On a oublié le logarithme : $\dfrac{10}{0{,}08}=125$ au lieu de $\dfrac{\ln(10)}{0{,}08}$.

</details>

Avis : 

---

## 6. `cqc-equation-differentielle-moyenne-2` (series C/D/E/TI)

**Remarque du relecteur :** LIMITE : équation différentielle du second ordre à racines complexes, à vérifier au programme de la série TI.

**Enonce :**

On considère l'équation différentielle $(E) : y'' + 4y' + 13y = 0$, où $y$ est une fonction deux fois dérivable sur $\mathbb{R}$.

Quelle est la solution de $(E)$ qui vérifie $y(0) = 2$ et $y'(0) = -1$ ?

- a) $y(x)=e^{2x}\left(2\cos(3x)-\dfrac53\sin(3x)\right)$
- b) $y(x)=e^{-2x}\big(2\cos(3x)+\sin(3x)\big)$
- c) $y(x)=e^{-2x}\left(2\cos(3x)-\dfrac13\sin(3x)\right)$
- d) $y(x)=e^{-2x}\left(2\cos(6x)+\dfrac12\sin(6x)\right)$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Pour $y'' + ay' + by = 0$, si le discriminant de l'équation caractéristique $r^2 + ar + b = 0$ est strictement négatif, les racines sont complexes conjuguées $r = p \pm iq$, et la solution générale s'écrit $y = e^{px}(A\cos(qx) + B\sin(qx))$. On détermine $A$ et $B$ à l'aide des conditions initiales sur $y$ et $y'$.

### Corrigé

L'équation caractéristique est $r^2 + 4r + 13 = 0$ : $\Delta = 16 - 52 = -36 < 0$, $\sqrt{-\Delta} = 6$, donc $r = \dfrac{-4 \pm 6i}{2} = -2 \pm 3i$.

La solution générale est
$$y(x) = e^{-2x}\big(A\cos(3x) + B\sin(3x)\big), \quad (A,B) \in \mathbb{R}^2.$$

On dérive :
$$y'(x) = -2e^{-2x}\big(A\cos(3x)+B\sin(3x)\big) + e^{-2x}\big(-3A\sin(3x)+3B\cos(3x)\big).$$
En $x=0$ : $y(0) = A$ et $y'(0) = -2A + 3B$, d'où
$$\begin{cases} A = 2 \\ -2A + 3B = -1 \end{cases} \implies -4 + 3B = -1 \implies B = 1.$$

**La solution cherchée est $y(x) = e^{-2x}\big(2\cos(3x) + \sin(3x)\big)$.**

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur la partie réelle des racines ($2\pm3i$ au lieu de $-2\pm3i$) : cette fonction n'est pas solution de $(E)$.
- **c)** La dérivée du facteur $e^{-2x}$ a été oubliée : on a écrit $y'(0)=3B$, ce qui donne $B=-\dfrac13$ et $y'(0)=-5$, non $-1$.
- **d)** On a pris $q=\sqrt{-\Delta}=6$ au lieu de $q=\dfrac{\sqrt{-\Delta}}{2}=3$ : cette fonction n'est pas solution de $(E)$.

</details>

Avis : 

---

## 7. `cqc-esperance-mathematique-elevee-5` (series A/C/D/E)

**Enonce :**

Une loterie de quartier propose des billets à gratter vendus $300$ francs CFA l'unité. Chaque billet permet de gagner un lot dont la valeur dépend d'un symbole révélé par grattage. Le tableau suivant donne la valeur du lot gagné (en francs CFA) et la probabilité associée, pour un billet acheté :

| Valeur du lot | $10\,000$ | $2\,000$ | $500$ | $100$ | $0$ |
|---|---|---|---|---|---|
| Probabilité | $0{,}01$ | $0{,}04$ | $0{,}10$ | $0{,}25$ | $0{,}60$ |

On note $X$ le gain algébrique net d'un joueur pour un billet acheté, c'est-à-dire la valeur du lot gagné diminuée du prix d'achat du billet.

Quelles sont l'espérance $E(X)$ et l'écart-type $\sigma(X)$ (arrondi à l'unité), en francs CFA ?

- a) $E(X)=255$ et $\sigma(X)\approx1\,059$
- b) $E(X)=-45$ et $\sigma(X)\approx1\,060$
- c) $E(X)=-45$ et $\sigma(X)\approx1\,059$
- d) $E(X)=-45$ et $\sigma(X)\approx1\,089$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Quand un gain net s'obtient en retranchant un coût fixe $c$ à une valeur brute aléatoire, la variable nette $X$ prend les valeurs (valeur brute $- c$), avec les mêmes probabilités. On calcule ensuite $E(X)=\sum x_i P(X=x_i)$, puis $V(X)=E(X^2)-[E(X)]^2$ et $\sigma(X)=\sqrt{V(X)}$. Le signe de $E(X)$ indique si le jeu est en moyenne favorable ($E(X)>0$) ou défavorable ($E(X)<0$) au joueur.

### Corrigé

**Vérification préalable.** $0{,}01+0{,}04+0{,}10+0{,}25+0{,}60 = 1$.

**Loi de $X$.** En retranchant $300$ à chaque valeur de lot :

| $x_i$ | $9\,700$ | $1\,700$ | $200$ | $-200$ | $-300$ |
|---|---|---|---|---|---|
| $P(X=x_i)$ | $0{,}01$ | $0{,}04$ | $0{,}10$ | $0{,}25$ | $0{,}60$ |

**Espérance.**
$$E(X) = 97 + 68 + 20 - 50 - 180 = -45$$
Le jeu est en moyenne défavorable au joueur : il perd en moyenne $45$ francs CFA par billet.

**Variance et écart-type.**
$$E(X^2) = 940\,900 + 115\,600 + 4\,000 + 10\,000 + 54\,000 = 1\,124\,500$$
$$V(X) = 1\,124\,500 - (-45)^2 = 1\,124\,500 - 2\,025 = 1\,122\,475$$
$$\sigma(X) = \sqrt{1\,122\,475} \approx 1\,059 \text{ (arrondi à l'unité)}$$

**Donc $E(X)=-45$ et $\sigma(X)\approx1\,059$ francs CFA.**

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié de retrancher le prix du billet : $255$ est l'espérance de la valeur du lot, pas celle du gain net.
- **b)** On a pris $\sigma(X)=\sqrt{E(X^2)}$ en oubliant de retrancher $[E(X)]^2$.
- **d)** $E(X^2)$ a été calculée avec les valeurs des lots au lieu des gains nets, puis mélangée avec $E(X)=-45$.

</details>

Avis : 

---

## 8. `cqc-esperance-mathematique-moyenne-3` (series A/C/D/E)

**Enonce :**

Un lot destiné au contrôle qualité contient $8$ composants électroniques indiscernables à l'œil nu, parmi lesquels $3$ sont défectueux et $5$ sont conformes. Un technicien prélève simultanément et au hasard $3$ composants de ce lot pour les tester. On note $X$ le nombre de composants défectueux parmi les $3$ prélevés.

Quelle est l'espérance mathématique $E(X)$ ?

- a) $\dfrac32$
- b) $\dfrac67$
- c) $\dfrac{3}{16}$
- d) $\dfrac98$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Lorsqu'on prélève simultanément $k$ éléments parmi $n$, le nombre total de prélèvements possibles est $\binom{n}{k}$, tous équiprobables. Pour compter les prélèvements réalisant un événement donné, on choisit séparément le nombre voulu d'éléments dans chaque catégorie et on multiplie les combinaisons obtenues. L'espérance se calcule ensuite par $E(X)=\sum x_i P(X=x_i)$.

### Corrigé

**Valeurs possibles :** $X(\Omega)=\{0,1,2,3\}$. Le nombre total de prélèvements est $\binom{8}{3}=56$.

- $P(X=0) = \dfrac{\binom{3}{0}\binom{5}{3}}{56} = \dfrac{10}{56}$
- $P(X=1) = \dfrac{\binom{3}{1}\binom{5}{2}}{56} = \dfrac{30}{56}$
- $P(X=2) = \dfrac{\binom{3}{2}\binom{5}{1}}{56} = \dfrac{15}{56}$
- $P(X=3) = \dfrac{\binom{3}{3}\binom{5}{0}}{56} = \dfrac{1}{56}$

Vérification : $\dfrac{10+30+15+1}{56}=1$.

$$E(X) = 0\times\dfrac{10}{56} + 1\times\dfrac{30}{56} + 2\times\dfrac{15}{56} + 3\times\dfrac{1}{56} = \dfrac{63}{56} = \dfrac{9}{8}$$

**Donc $E(X)=\dfrac98$** : en moyenne, un prélèvement de $3$ composants contient $1{,}125$ composant défectueux.

### Pourquoi les autres réponses sont fausses

- **a)** On a supposé les quatre valeurs $0$, $1$, $2$, $3$ équiprobables, ce qui est faux.
- **b)** Erreur de dénombrement pour $X=1$ : on a pris $\binom{5}{1}$ conformes au lieu de $\binom{5}{2}$, soit $15$ cas au lieu de $30$.
- **c)** On a compté les tirages ordonnés au dénominateur ($8\times7\times6=336$) tout en gardant des combinaisons au numérateur.

</details>

Avis : 

---

## 9. `cqc-esperance-mathematique-faible-1` (series A/C/D/E)

**Remarque du relecteur :** Le choix b (0,84) est la variance : bon distracteur.

**Enonce :**

Un centre d'appel étudie le nombre d'appels abandonnés (raccrochés par le client avant toute réponse) durant chaque tranche de $5$ minutes d'activité. On note $X$ cette variable aléatoire, dont la loi de probabilité est donnée par le tableau suivant :

| $x_i$ | $0$ | $1$ | $2$ | $3$ |
|---|---|---|---|---|
| $P(X=x_i)$ | $\dfrac{1}{10}$ | $\dfrac{2}{5}$ | $\dfrac{3}{10}$ | $\dfrac{1}{5}$ |

Quelle est la valeur approchée à $10^{-2}$ près de l'écart-type $\sigma(X)$ ?

- a) $0{,}92$
- b) $0{,}84$
- c) $1{,}84$
- d) $1{,}34$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Pour une variable aléatoire $X$ à valeurs $x_1,\ldots,x_n$, l'espérance est $E(X)=\sum x_i P(X=x_i)$. La variance se calcule par la formule de König-Huygens $V(X) = E(X^2) - [E(X)]^2$, où $E(X^2)=\sum x_i^2 P(X=x_i)$ ; l'écart-type est $\sigma(X)=\sqrt{V(X)}$.

### Corrigé

**Vérification préalable.** $\dfrac{1}{10}+\dfrac{4}{10}+\dfrac{3}{10}+\dfrac{2}{10}=1$.

**Espérance.**
$$E(X) = 0 + \dfrac{4}{10} + \dfrac{6}{10} + \dfrac{6}{10} = \dfrac{16}{10} = \dfrac{8}{5} = 1{,}6$$

**Variance et écart-type.**
$$E(X^2) = 0 + \dfrac{4}{10} + \dfrac{12}{10} + \dfrac{18}{10} = \dfrac{34}{10} = \dfrac{17}{5}$$
$$V(X) = \dfrac{17}{5} - \left(\dfrac{8}{5}\right)^2 = \dfrac{85}{25} - \dfrac{64}{25} = \dfrac{21}{25}$$
$$\sigma(X) = \sqrt{\dfrac{21}{25}} = \dfrac{\sqrt{21}}{5} \approx 0{,}92 \text{ (valeur approchée à } 10^{-2} \text{ près)}$$

### Pourquoi les autres réponses sont fausses

- **b)** $0{,}84=\dfrac{21}{25}$ est la variance : on a oublié de prendre la racine carrée.
- **c)** On a calculé $\sqrt{E(X^2)}$ en oubliant de retrancher $[E(X)]^2$.
- **d)** On a retranché $E(X)$ au lieu de $[E(X)]^2$ : $\sqrt{3{,}4-1{,}6}\approx1{,}34$.

</details>

Avis : 

---

## 10. `cqc-exponentielle-moyenne-2` (series A/C/D/TI)

**Enonce :**

Soit $s$ la fonction définie par $s(x) = \ln\!\left(\dfrac{4}{3e^{4x}-6}\right)$.

Quel est l'ensemble de définition $D_s$ de la fonction $s$ ?

- a) $D_s=\left]\ln2\,;\,+\infty\right[$
- b) $D_s=\left]\dfrac{\ln2}{4}\,;\,+\infty\right[$
- c) $D_s=\left]-\infty\,;\,\dfrac{\ln2}{4}\right[$
- d) $D_s=\mathbb{R}\setminus\left\{\dfrac{\ln2}{4}\right\}$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Une expression de la forme $\ln(A(x))$ n'est définie que là où $A(x)>0$. Lorsque $A(x)$ est un quotient dont le numérateur est une constante strictement positive, le signe de $A(x)$ est celui de son dénominateur : il suffit donc de résoudre l'inéquation associée à ce dénominateur, en utilisant que $e^{\alpha x}>k \iff \alpha x>\ln k$ (pour $k>0$), la fonction $x\mapsto e^{\alpha x}$ étant strictement croissante lorsque $\alpha>0$.

### Corrigé

$s(x)$ est définie si et seulement si $\dfrac{4}{3e^{4x}-6}>0$. Comme le numérateur $4$ est strictement positif, cette fraction est strictement positive si et seulement si son dénominateur l'est :

$$3e^{4x}-6>0 \iff e^{4x}>2 \iff 4x>\ln2 \iff x>\dfrac{\ln2}{4}$$

(on a utilisé que $x\mapsto e^{4x}$ est strictement croissante sur $\mathbb{R}$, donc l'inégalité entre exponentielles équivaut à l'inégalité entre les exposants).

**L'ensemble de définition de $s$ est $D_s = \left]\dfrac{\ln2}{4}\,;\,+\infty\right[$.**

### Pourquoi les autres réponses sont fausses

- **a)** $\left]\ln2\,;\,+\infty\right[$ : on a oublié de diviser par $4$ en passant de $4x>\ln2$ à $x>\dfrac{\ln2}{4}$.
- **c)** $\left]-\infty\,;\,\dfrac{\ln2}{4}\right[$ : le sens de l'inégalité est inversé ; pour ces valeurs le dénominateur est négatif et le quotient aussi.
- **d)** $\mathbb{R}\setminus\left\{\dfrac{\ln2}{4}\right\}$ : on a seulement exigé que le dénominateur ne s'annule pas, en oubliant que le logarithme exige un nombre strictement positif.

</details>

Avis : 

---

## 11. `cqc-exponentielle-moyenne-0` (series A/C/D/TI)

**Enonce :**

On considère le système d'équations d'inconnues réelles $x$ et $y$ :
$$\begin{cases}\ln(2x+y)-\ln(x-1)=\ln3\\ e^{x-2}\times e^{y+1}=1\end{cases}$$
Quel est l'ensemble des solutions de ce système dans $\mathbb{R}^2$ ?

- a) $\left\{\left(\dfrac52\,;\,-\dfrac12\right)\right\}$
- b) $\{(1\,;\,0)\}$
- c) $\{(2\,;\,-1)\}$
- d) Le système n'a pas de solution.

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Pour résoudre un système mêlant logarithmes et exponentielles, on ramène chaque équation à une expression plus simple à l'aide des propriétés usuelles : $\ln a - \ln b = \ln\!\left(\dfrac{a}{b}\right)$ et $\ln a = \ln b \iff a=b$ (lorsque $a>0$ et $b>0$) d'une part, $e^{u}\times e^{v}=e^{u+v}$ et $e^{u}=1\iff u=0$ d'autre part. On obtient ainsi un système linéaire classique en $x$ et $y$, qu'il faut résoudre puis confronter aux conditions d'existence des logarithmes de départ.

### Corrigé

**Conditions d'existence :** l'équation $\ln(2x+y)-\ln(x-1)=\ln3$ exige $2x+y>0$ et $x-1>0$, c'est-à-dire $x>1$.

**Première équation :**
$$\ln(2x+y)-\ln(x-1)=\ln3 \iff \ln\!\left(\dfrac{2x+y}{x-1}\right)=\ln3 \iff \dfrac{2x+y}{x-1}=3$$
(l'équivalence est valide car $x-1>0$ et $3>0$), d'où :
$$2x+y=3(x-1) \iff 2x+y=3x-3 \iff y=x-3 \quad (1)$$

**Seconde équation :**
$$e^{x-2}\times e^{y+1}=1 \iff e^{(x-2)+(y+1)}=1 \iff e^{x+y-1}=1 \iff x+y-1=0 \iff x+y=1 \quad (2)$$

**Résolution du système linéaire :** en substituant (1) dans (2) :
$$x+(x-3)=1 \iff 2x-3=1 \iff 2x=4 \iff x=2$$
puis $y=x-3=2-3=-1$.

**Vérification des conditions d'existence :** $x-1=2-1=1>0$ et $2x+y=4-1=3>0$. Les deux conditions sont respectées.

**Vérification dans les équations de départ :** $\ln(3)-\ln(1)=\ln3-0=\ln3$, et $e^{0}\times e^{0}=1\times1=1$.

**Le système admet donc une unique solution : $(x\,;\,y)=(2\,;\,-1)$.**

### Pourquoi les autres réponses sont fausses

- **a)** $\left\{\left(\dfrac52\,;\,-\dfrac12\right)\right\}$ : on a écrit $e^{x+y-1}=1 \iff x+y-1=1$, en confondant $e^{u}=1$ avec $u=1$ au lieu de $u=0$.
- **b)** $\{(1\,;\,0)\}$ : on a développé $3(x-1)$ en $3x-1$ ; de plus ce couple donne $x-1=0$, donc $\ln(x-1)$ n'existe pas : l'oubli de la vérification des conditions d'existence le laisse passer.
- **d)** Le système n'a pas de solution : on a cru que $\ln(2x+y)-\ln(x-1)=\ln\big((2x+y)-(x-1)\big)$, ce qui conduit à $x+y=2$, incompatible avec $x+y=1$.

</details>

Avis : 

---

## 12. `cqc-derivee-seconde-elevee-0` (series A/C/D)

**Remarque du relecteur :** LIMITE : point d'inflexion (dérivée seconde) en série A, à la limite haute du programme léger.

**Enonce :**

Soit $f(x)=xe^{-x}$ définie sur $\mathbb{R}$. La courbe de $f$ admet un unique point d'inflexion. Quelle est l'équation de la tangente à la courbe de $f$ en ce point ?

- a) $y=e^{-1}$
- b) $y=-e^{-2}x$
- c) $y=-e^{2}(x+4)$
- d) $y=e^{-2}(4-x)$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Un point d'inflexion correspond à une annulation de $f''$ avec changement de signe ; la tangente en $x_0$ a pour équation $y=f'(x_0)(x-x_0)+f(x_0)$.

### Corrigé

$f'(x)=e^{-x}-xe^{-x}=(1-x)e^{-x}$.

$f''(x)=-e^{-x}-(1-x)e^{-x}=(x-2)e^{-x}$.

Comme $e^{-x}>0$, $f''$ a le signe de $x-2$ : elle s'annule en $2$ en passant du négatif au positif. La courbe a donc un unique point d'inflexion, d'abscisse $2$ et d'ordonnée $f(2)=2e^{-2}$.

$f'(2)=-e^{-2}$, d'où la tangente $y=-e^{-2}(x-2)+2e^{-2}=e^{-2}(4-x)$.

**La tangente au point d'inflexion a pour équation $y=e^{-2}(4-x)$.**

### Pourquoi les autres réponses sont fausses

- **a)** $y=e^{-1}$ : c'est la tangente au point d'abscisse $1$, où $f'$ s'annule ; on a confondu le point d'inflexion (annulation de $f''$) avec un extremum (annulation de $f'$).
- **b)** $y=-e^{-2}x$ : on a utilisé la formule erronée $y=f'(x_0)(x+x_0)+f(x_0)$.
- **c)** $y=-e^{2}(x+4)$ : on a dérivé $e^{-x}$ en $e^{-x}$ (oubli du signe moins), d'où $f''(x)=(x+2)e^{-x}$ et un faux point d'inflexion d'abscisse $-2$.

</details>

Avis : 

---

## 13. `cqc-derivee-seconde-moyenne-1` (series A/C/D)

**Remarque du relecteur :** La convexité (signe de f'') ne figure pas au programme léger de Terminale A ; acceptable pour C et D seulement.

**Enonce :**

Soit $f(x)=(x^2+1)e^x$ définie sur $\mathbb{R}$. Sur quel(s) intervalle(s) la fonction $f$ est-elle convexe ?

- a) Sur $]-\infty\,;-3]$ et sur $[-1\,;+\infty[$
- b) Sur $[-3\,;-1]$
- c) Sur $[-1\,;+\infty[$ seulement
- d) Sur $\mathbb{R}$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

On dérive deux fois avec $(uv)'=u'v+uv'$, en factorisant par $e^x$ à chaque étape ; comme $e^x>0$, le signe de $f''$ est celui du trinôme restant. La fonction est convexe là où $f''\geqslant0$.

### Corrigé

$f'(x)=2xe^x+(x^2+1)e^x=(x^2+2x+1)e^x$.

$f''(x)=(2x+2)e^x+(x^2+2x+1)e^x=(x^2+4x+3)e^x=(x+1)(x+3)e^x$.

Le trinôme $(x+1)(x+3)$ est positif à l'extérieur des racines $-3$ et $-1$ : $f$ est convexe sur $]-\infty\,;-3]$ et sur $[-1\,;+\infty[$, concave sur $[-3\,;-1]$.

### Pourquoi les autres réponses sont fausses

- **b)** Sur $[-3\,;-1]$ : c'est l'intervalle où $f''\leqslant0$, donc où $f$ est concave ; on a inversé convexité et concavité.
- **c)** Sur $[-1\,;+\infty[$ seulement : on a oublié la règle du produit lors de la seconde dérivation, en écrivant $f''(x)=(2x+2)e^x$.
- **d)** Sur $\mathbb{R}$ : on a étudié le signe de $f'(x)=(x+1)^2e^x\geqslant0$, qui donne le sens de variation de $f$ et non sa convexité.

</details>

Avis : 

---

## 14. `cqc-derivee-seconde-faible-1` (series A/C/D)

**Enonce :**

Soit $f(x)=e^{2x}-x^2$ définie sur $\mathbb{R}$. Quelle est l'expression de la dérivée seconde $f''(x)$ ?

- a) $f''(x)=2e^{2x}-2$
- b) $f''(x)=4e^{2x}-2$
- c) $f''(x)=4e^{2x}-2x$
- d) $f''(x)=2e^{2x}-2x$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

$(e^{ax})'=ae^{ax}$ : dériver deux fois $e^{2x}$ multiplie par $2$ à chaque fois.

### Corrigé

$f'(x)=2e^{2x}-2x$.

$f''(x)=4e^{2x}-2$.

### Pourquoi les autres réponses sont fausses

- **a)** $2e^{2x}-2$ : on a multiplié par $2$ une seule fois, en dérivant $2e^{2x}$ comme si c'était $2e^{x}$.
- **c)** $4e^{2x}-2x$ : on a dérivé deux fois $e^{2x}$ mais une seule fois $x^2$.
- **d)** $2e^{2x}-2x$ : c'est la dérivée première $f'(x)$, pas la dérivée seconde.

</details>

Avis : 

---

## 15. `cqc-integrale-moyenne-2` (series C/D/E)

**Enonce :**

Quelle est la valeur moyenne de la fonction $f(x)=3x^2-x$ sur l'intervalle $[1\,;3]$ ?

- a) $22$
- b) $9$
- c) $11$
- d) $13$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

La valeur moyenne d'une fonction $f$ continue sur $[a\,;b]$ est $\mu=\dfrac1{b-a}\displaystyle\int_a^bf(x)\,dx$.

### Corrigé

Une primitive de $f$ est $F(x)=x^3-\dfrac{x^2}{2}$.

$\displaystyle\int_1^3f(x)dx=F(3)-F(1)=\left(27-\dfrac92\right)-\left(1-\dfrac12\right)=\dfrac{45}{2}-\dfrac12=22$.

$\mu=\dfrac{1}{3-1}\times22=11$.

### Pourquoi les autres réponses sont fausses

- **a)** $22$ : c'est la valeur de l'intégrale ; on a oublié de la multiplier par $\dfrac{1}{b-a}=\dfrac12$.
- **b)** $9$ : on a pris $x^2$ comme primitive de $x$ (au lieu de $\dfrac{x^2}{2}$), d'où $F(x)=x^3-x^2$ et une intégrale égale à $18$.
- **d)** $13$ : on a fait la moyenne des valeurs extrêmes $\dfrac{f(1)+f(3)}{2}=\dfrac{2+24}{2}$, ce qui ne donne pas la valeur moyenne d'une fonction non affine.

</details>

Avis : 

---

## 16. `cqc-integrale-moyenne-0` (series C/D/E)

**Enonce :**

Quelle est la valeur de $\displaystyle\int_0^1\dfrac{2x+1}{x^2+x+1}\,dx$ ?

- a) $\ln3$
- b) $\ln3-1$
- c) $-\ln3$
- d) $\dfrac{12}{11}$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Une fonction de la forme $\dfrac{u'}{u}$ avec $u>0$ a pour primitive $\ln u$.

### Corrigé

Posons $u(x)=x^2+x+1$ ; $u'(x)=2x+1$ et $u(x)>0$ pour tout $x$ (discriminant $-3<0$).

$\displaystyle\int_0^1\dfrac{u'(x)}{u(x)}dx=\Big[\ln(x^2+x+1)\Big]_0^1=\ln3-\ln1=\ln 3$.

### Pourquoi les autres réponses sont fausses

- **b)** $\ln3-1$ : on a confondu $\ln1$ avec $1$, alors que $\ln1=0$.
- **c)** $-\ln3$ : on a calculé $F(0)-F(1)$ au lieu de $F(1)-F(0)$.
- **d)** $\dfrac{12}{11}$ : on a divisé l'intégrale du numérateur ($2$) par celle du dénominateur ($\dfrac{11}{6}$), ce qui n'est pas une règle de calcul intégral.

</details>

Avis : 

---

## 17. `cqc-equation-differentielle-elevee-5` (series C/D/E/TI)

**Remarque du relecteur :** LIMITE : équation du second ordre avec second membre (solution particulière admise) ; vérifier qu'elle est au programme de D et TI, souvent limité à l'équation homogène.

**Enonce :**

On considère l'équation différentielle
$$(E) : y'' - 5y' + 6y = 6x - 7,$$
où $y$ est une fonction deux fois dérivable sur $\mathbb{R}$. On admet que $(E)$ admet une solution particulière de la forme $y_p(x)=ax+b$, où $a$ et $b$ sont des réels.

Quelle est la solution de $(E)$ vérifiant $y(0) = 3$ et $y'(0) = 8$ ?

- a) $y(x)=\dfrac43e^{3x}+2e^{2x}+x-\dfrac13$
- b) $y(x)=e^{3x}+2e^{2x}+x-\dfrac13$
- c) $y(x)=-3e^{3x}+8e^{2x}+x-2$
- d) $y(x)=\dfrac13e^{3x}+3e^{2x}+x-\dfrac13$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode
Pour une équation avec second membre $y'' + ay' + by = g(x)$, on résout d'abord l'équation homogène associée, puis on cherche une solution particulière de la forme suggérée par $g(x)$ (ici un polynôme du premier degré). La solution générale de $(E)$ est la somme de la solution homogène et de la solution particulière ; les constantes s'ajustent ensuite avec les conditions initiales.

### Corrigé
**Équation homogène.** L'équation caractéristique est $r^2 - 5r + 6 = 0$.
$\Delta = 25 - 24 = 1 > 0$, racines $r_1 = \dfrac{5-1}{2} = 2$ et $r_2 = \dfrac{5+1}{2} = 3$.
La solution homogène est donc $y_h(x) = Ae^{3x} + Be^{2x}$.

**Solution particulière.** Pour $y_p(x) = ax+b$, on a $y_p'(x) = a$ et $y_p''(x) = 0$. En substituant dans $(E)$ :
$$0 - 5a + 6(ax+b) = 6x - 7 \iff 6a\,x + (6b - 5a) = 6x - 7.$$
Par identification : $6a = 6 \Rightarrow a = 1$, puis $6b - 5 = -7 \Rightarrow b = -\dfrac{1}{3}$.
Donc $y_p(x) = x - \dfrac{1}{3}$.

**Solution générale.**
$$y(x) = Ae^{3x} + Be^{2x} + x - \frac13, \quad (A,B)\in\mathbb{R}^2.$$

**Conditions initiales.** On a $y'(x) = 3Ae^{3x} + 2Be^{2x} + 1$. Les conditions initiales donnent :
$$\begin{cases} y(0) = A+B-\dfrac13 = 3 \\ y'(0) = 3A+2B+1 = 8 \end{cases} \iff \begin{cases} A+B = \dfrac{10}{3} \\ 3A+2B = 7 \end{cases}$$
De la première équation, $B = \dfrac{10}{3} - A$. En reportant dans la seconde :
$$3A + 2\left(\frac{10}{3}-A\right) = 7 \iff A + \frac{20}{3} = 7 \iff A = \frac{1}{3}.$$
D'où $B = \dfrac{10}{3} - \dfrac13 = 3$.

La solution cherchée est donc :
$$y(x) = \frac13 e^{3x} + 3e^{2x} + x - \frac13.$$

### Pourquoi les autres réponses sont fausses

- **a)** $\dfrac43e^{3x}+2e^{2x}+x-\dfrac13$ : on a oublié le terme $+1$ provenant de $y_p'$ dans $y'(0)$, d'où $3A+2B=8$.
- **b)** $e^{3x}+2e^{2x}+x-\dfrac13$ : on a oublié le terme $-\dfrac13$ dans $y(0)$, d'où $A+B=3$.
- **c)** $-3e^{3x}+8e^{2x}+x-2$ : erreur de signe dans l'identification ($6b+5=-7$), d'où $b=-2$ et des constantes fausses.

</details>

Avis : 

---

## 18. `cqc-equation-differentielle-faible-1` (series C/D/E/TI)

**Enonce :**

On considère l'équation différentielle $(E) : y' + 2y = 6$, où $y$ est une fonction dérivable sur $\mathbb{R}$. Quelle est la solution de $(E)$ vérifiant $y(0) = 5$ ?

- a) $y(x)=2e^{2x}+3$
- b) $y(x)=5e^{-2x}+3$
- c) $y(x)=2e^{-2x}+3$
- d) $y(x)=-e^{-2x}+6$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode
Pour résoudre $y' + ay = b$ (avec $a \neq 0$, $b$ constant), on résout d'abord l'équation homogène associée $y' + ay = 0$, dont les solutions sont $y = Ce^{-ax}$. On ajoute ensuite une solution particulière constante $y_p = \dfrac{b}{a}$. La solution générale est la somme des deux, et la constante $C$ se fixe avec la condition initiale.

### Corrigé
L'équation homogène $y' + 2y = 0$ a pour solutions $y(x) = Ce^{-2x}$, $C \in \mathbb{R}$.

Pour $y_p(x) = 3$, on a $y_p'(x) = 0$, donc $y_p' + 2y_p = 0 + 2\times 3 = 6$ : la fonction constante $y_p = 3$ est une solution particulière de $(E)$.

La solution générale de $(E)$ est donc
$$y(x) = Ce^{-2x} + 3, \quad C \in \mathbb{R}.$$
La condition $y(0) = 5$ donne $C + 3 = 5$, soit $C = 2$.

La solution cherchée est :
$$y(x) = 2e^{-2x} + 3.$$

### Pourquoi les autres réponses sont fausses

- **a)** $2e^{2x}+3$ : erreur de signe dans l'exposant ; les solutions de $y'+2y=0$ sont $Ce^{-2x}$ et non $Ce^{2x}$.
- **b)** $5e^{-2x}+3$ : on a pris $C=y(0)=5$ en oubliant la solution particulière ; cette fonction vaut $8$ en $0$.
- **d)** $-e^{-2x}+6$ : on a pris $b=6$ comme solution particulière au lieu de $\dfrac{b}{a}=3$.

</details>

Avis : 

---

## 19. `cqc-esperance-mathematique-moyenne-4` (series A/C/D/E)

**Enonce :**

Un jeu de belote comporte $32$ cartes, dont $4$ as. On tire successivement et sans remise $2$ cartes de ce jeu. On note $X$ le nombre d'as obtenus parmi les $2$ cartes tirées. Quelle est l'espérance mathématique $E(X)$ ?

- a) $\dfrac{17}{124}$
- b) $\dfrac14$
- c) $\dfrac{59}{248}$
- d) $1$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Pour un tirage successif sans remise, on raisonne à l'aide de probabilités conditionnelles : la probabilité de la deuxième carte dépend du résultat de la première, car une carte retirée n'est pas remise dans le jeu. On distingue les différents ordres possibles conduisant au même événement (par exemple « as puis non-as » et « non-as puis as » donnent tous deux un seul as au total), et on additionne leurs probabilités. Une fois la loi établie, l'espérance se calcule normalement par $E(X)=\sum x_i P(X=x_i)$.

### Corrigé

**1. Valeurs possibles.** Sur $2$ cartes tirées, le nombre d'as obtenus vaut $0$, $1$ ou $2$. Donc $X(\Omega)=\{0\,;\,1\,;\,2\}$.

**2. Loi de probabilité.** Le jeu contient $4$ as et $28$ non-as.

- $P(X=0)$ : les deux cartes sont des non-as. $P(X=0) = \dfrac{28}{32}\times\dfrac{27}{31} = \dfrac{756}{992} = \dfrac{189}{248}$.
- $P(X=2)$ : les deux cartes sont des as. $P(X=2) = \dfrac{4}{32}\times\dfrac{3}{31} = \dfrac{12}{992} = \dfrac{3}{248}$.
- $P(X=1)$ : un as et un non-as, dans l'un ou l'autre ordre. $P(X=1) = 2\times\dfrac{4}{32}\times\dfrac{28}{31} = 2\times\dfrac{112}{992} = \dfrac{224}{992} = \dfrac{7}{31} = \dfrac{56}{248}$.

Vérification : $\dfrac{189+56+3}{248} = \dfrac{248}{248}=1$.

**3. Espérance.**
$$E(X) = 0\times\dfrac{189}{248} + 1\times\dfrac{56}{248} + 2\times\dfrac{3}{248} = \dfrac{0+56+6}{248} = \dfrac{62}{248} = \dfrac{1}{4}$$

En moyenne, un tirage de $2$ cartes contient $\dfrac{1}{4}=0{,}25$ as.

### Pourquoi les autres réponses sont fausses

- **a)** $\dfrac{17}{124}$ : on a oublié les deux ordres possibles pour obtenir un seul as, d'où $P(X=1)=\dfrac{28}{248}$ au lieu de $\dfrac{56}{248}$.
- **c)** $\dfrac{59}{248}$ : on a additionné $P(X=1)$ et $P(X=2)$ sans multiplier chaque probabilité par la valeur correspondante de $X$.
- **d)** $1$ : on a supposé les valeurs $0$, $1$ et $2$ équiprobables, ce qui donne $\dfrac{0+1+2}{3}$.

</details>

Avis : 

---

## 20. `cqc-esperance-mathematique-moyenne-2` (series A/C/D/E)

**Enonce :**

Dans un jeu de hasard, le gain algébrique $X$ d'un joueur, exprimé en milliers de francs CFA, suit la loi de probabilité suivante, où $p$ est un réel tel que $0 < p < \dfrac{1}{2}$ :

| $x_i$ | $-1$ | $1$ | $4$ |
|---|---|---|---|
| $P(X=x_i)$ | $p$ | $p$ | $1-2p$ |

Quelle est l'expression de l'espérance mathématique $E(X)$ en fonction de $p$ ?

- a) $E(X)=4-6p$
- b) $E(X)=4-2p$
- c) $E(X)=\dfrac{4-8p}{3}$
- d) $E(X)=4-8p$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Pour calculer $E(X)=\sum x_i P(X=x_i)$ en fonction d'un paramètre, on développe la somme littéralement puis on réduit les termes semblables : il arrive que les termes contenant le paramètre s'annulent partiellement, ce qui simplifie l'expression finale.

### Corrigé

Pour $0 < p < \dfrac{1}{2}$, les trois probabilités sont strictement positives et leur somme vaut $p+p+(1-2p)=1$ : le tableau définit bien une loi de probabilité.

$$E(X) = (-1)\times p + 1\times p + 4\times(1-2p)$$
$$E(X) = -p + p + 4 - 8p$$

Les deux termes en $p$ issus des valeurs $-1$ et $1$ s'annulent ($-p+p=0$), il reste :
$$E(X) = 4 - 8p$$

L'espérance mathématique de $X$ est donc $E(X) = 4-8p$ (en milliers de francs CFA).

### Pourquoi les autres réponses sont fausses

- **a)** $4-6p$ : erreur de signe sur le premier terme, $(-1)\times p$ remplacé par $+p$.
- **b)** $4-2p$ : on a mal développé $4\times(1-2p)$ en $4-2p$.
- **c)** $\dfrac{4-8p}{3}$ : on a divisé la somme par le nombre de valeurs, comme pour une moyenne simple ; les probabilités jouent déjà le rôle de coefficients.

</details>

Avis : 

---

