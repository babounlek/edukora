# Vague 5 Maths BEPC (questions au thème renommé) : 19 QCM à faire relire par l'enseignant (campagne B1)

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

