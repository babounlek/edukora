# Vague 4 Maths BEPC : 55 QCM à faire relire par l'enseignant (campagne B1)

Date : 2026-11-01. Sur 197 QCM convertis (235 questions BEPC sans figure étudiées, 38 écartées), **55** vous sont soumis : ceux que le relecteur aveugle a assortis d'une remarque et un tirage de 15 autres. Le lot est prêt mais n'est pas en ligne tant que vous n'avez pas répondu. Les 197 résolutions à l'aveugle ont donné la clé, après correction d'une ambiguïté (encadrement) et de 14 formulations. Beaucoup de questions à plusieurs sous-questions ont été réduites à une seule.

## Points à trancher

1. **Vecteur directeur** (`vecteur-directeur-faible-0`, `vecteur-directeur-moyenne-1`) et **norme d'un vecteur** : ces termes sont-ils au programme de la 3e ?
2. **Droites écrites sous la forme ax + by + c = 0** (`equation-reduite`) : à ramener à y = ax + b ; à garder ?
3. **Rapport d'une réduction au cube** (volumes, racine cubique de 27/64), **homothétie de rapport négatif**, **diagonale du cube** et **apothème** (Pythagore deux fois) : limites hautes de la 3e ?
4. **Développement d'un produit de trois facteurs** (`double-distributivite-elevee-0`), **valeur absolue d'une expression avec radical**.
5. **Incohérence d'origine** (`aire-d-un-rectangle-elevee-1`) : 4,5 m / 0,4 m = 11,25 carreaux, ils ne tombent pas pile ; la clé 180 vient du calcul par les aires. On garde ?
6. **Questions simples** à retirer éventuellement : divisions de fractions et droites horizontales faciles.

Pour chaque question : **OK**, **à corriger** (dire quoi) ou **à retirer**.

## 1. `cqc-tangente-moyenne-1` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : « le pied d'une caméra ... est situé à 15 m » est confus, écrire « le pied du poteau est situé à 15 m du point R ». Avec 0,70 on tombe pile sur 10,5 : un élève peut hésiter entre 10 et 11 ; mieux vaut donner tan 35° ≈ 0,7002 ou demander l'arrondi au dixième.

**Énoncé :**

Une caméra de surveillance est fixée au sommet d'un poteau. Le pied du poteau est situé à $15$ m d'un point de référence $R$ du sol. L'angle d'élévation entre ce point $R$ et le sommet du poteau, où est fixée la caméra, mesure $35°$. Sachant que $\tan(35°) \approx 0{,}70$, quelle est la hauteur du poteau, arrondie au mètre le plus proche ?

- a) $21$ m
- b) $10$ m
- c) $11$ m
- d) $14$ m

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand on connaît un angle et le côté adjacent dans un triangle rectangle, on retrouve le côté opposé avec $\tan(\alpha) = \dfrac{\text{opposé}}{\text{adjacent}}$, d'où $\text{opposé} = \text{adjacent} \times \tan(\alpha)$.

### Corrigé

Notons $h$ la hauteur du poteau (côté opposé à l'angle de $35°$) ; la distance au sol, $15$ m, est le côté adjacent :

$$\tan(35°) = \frac{h}{15} \quad \text{donc} \quad h = 15 \times \tan(35°) \approx 15 \times 0{,}70 = 10{,}5 \text{ m}$$

Arrondi au mètre le plus proche : $h \approx 11$ m.

**Vérification.** $\tan 35° < 1$, donc la hauteur doit être inférieure à la distance horizontale : $11 < 15$.

### Pourquoi les autres réponses sont fausses
- **a)** a divisé par $\tan(35°)$ au lieu de multiplier : $15 \div 0{,}70 \approx 21{,}4$.
- **b)** a tronqué $10{,}5$ au lieu de l'arrondir au plus proche.
- **d)** a soustrait $0{,}70$ à $15$ au lieu de multiplier par $\tan(35°)$.

</details>

Avis : 

---

## 2. `cqc-tangente-moyenne-2` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : préciser que le fil est tendu (rectiligne) et tenu au niveau du sol, sinon la hauteur de la main fausse le modèle.

**Énoncé :**

Un enfant fait voler un cerf-volant. Le fil du cerf-volant, tendu et tenu par l'enfant au niveau du sol, fait un angle de $40°$ avec le sol, et le cerf-volant se trouve à une hauteur de $18$ m au-dessus du sol, à la verticale d'un point $P$. Sachant que $\tan(40°) \approx 0{,}84$, quelle est la distance horizontale entre l'enfant et le point $P$, arrondie au mètre le plus proche ?

- a) $15$ m
- b) $21$ m
- c) $22$ m
- d) $17$ m

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand on connaît un angle et le côté opposé, on retrouve le côté adjacent avec $\tan(\alpha) = \dfrac{\text{opposé}}{\text{adjacent}}$, d'où $\text{adjacent} = \dfrac{\text{opposé}}{\tan(\alpha)}$.

### Corrigé

Notons $d$ la distance horizontale (côté adjacent à l'angle de $40°$) ; la hauteur $18$ m est le côté opposé. Le triangle formé par l'enfant, le point $P$ et le cerf-volant est rectangle en $P$ :

$$\tan(40°) = \frac{18}{d} \quad \text{donc} \quad d = \frac{18}{\tan(40°)} \approx \frac{18}{0{,}84} \approx 21{,}4 \text{ m}$$

Arrondi au mètre le plus proche : $d \approx 21$ m.

**Vérification.** $\tan 40° < 1$, donc le côté adjacent doit être plus grand que le côté opposé : $21 > 18$.

### Pourquoi les autres réponses sont fausses
- **a)** a multiplié $18$ par $\tan(40°)$ au lieu de diviser : $18 \times 0{,}84 \approx 15$.
- **c)** a arrondi $21{,}4$ par excès au lieu de l'arrondir au plus proche.
- **d)** a soustrait $0{,}84$ à $18$ au lieu de diviser par $\tan(40°)$.

</details>

Avis : 

---

## 3. `cqc-aire-d-un-rectangle-elevee-1` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : 4,5/0,4 = 11,25 n'est pas entier, des carreaux doivent être découpés ; « aucune perte » est peu réaliste, préférer une largeur de 4,4 m ou 4,8 m.

**Énoncé :**

Un carreleur doit carreler une pièce rectangulaire de $6{,}4$ m de longueur sur $4{,}5$ m de largeur, à l'aide de carreaux carrés de $40$ cm de côté. On suppose qu'il n'y a aucune perte de matériau. Combien de carreaux sont nécessaires ?

- a) $72$
- b) $18$
- c) $720$
- d) $180$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour déterminer combien de petites surfaces identiques recouvrent une grande surface, on calcule l'aire de chacune dans la même unité, puis on divise l'aire totale par l'aire d'une seule pièce.

### Corrigé

Aire de la pièce : $6{,}4 \times 4{,}5 = 28{,}8 \text{ m}^{2}$.

Côté d'un carreau en mètres : $40 \text{ cm} = 0{,}4 \text{ m}$, donc aire d'un carreau : $0{,}4 \times 0{,}4 = 0{,}16 \text{ m}^{2}$.

$$n = \frac{28{,}8}{0{,}16} = 180$$

Le carreleur a besoin de **180 carreaux**.

**Vérification.** $180 \times 0{,}16 = 28{,}8$ m² : on retrouve l'aire de la pièce.

### Pourquoi les autres réponses sont fausses
- **a)** a divisé l'aire de la pièce par le côté d'un carreau ($0{,}4$ m) au lieu de son aire.
- **b)** a calculé l'aire d'un carreau égale à $1{,}6$ m² au lieu de $0{,}16$ m² (erreur de virgule).
- **c)** a calculé l'aire d'un carreau égale à $0{,}04$ m² au lieu de $0{,}16$ m² (erreur de virgule).

</details>

Avis : 

---

## 4. `cqc-aire-d-un-rectangle-moyenne-2` (séries BEPC)

**Énoncé :**

Un mur rectangulaire de $5$ m de longueur et $2{,}5$ m de hauteur doit être peint. Il comporte une fenêtre rectangulaire de $1{,}2$ m de longueur sur $1$ m de hauteur qu'on ne peint pas. Quelle est l'aire de mur réellement à peindre ?

- a) $13{,}7 \text{ m}^{2}$
- b) $11{,}3 \text{ m}^{2}$
- c) $10{,}3 \text{ m}^{2}$
- d) $11{,}5 \text{ m}^{2}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour calculer l'aire d'une surface avec une partie non concernée, on calcule l'aire totale du rectangle, l'aire de la partie à exclure, puis on soustrait la seconde de la première.

### Corrigé

Aire totale du mur : $5 \times 2{,}5 = 12{,}5 \text{ m}^{2}$.

Aire de la fenêtre : $1{,}2 \times 1 = 1{,}2 \text{ m}^{2}$.

Aire à peindre : $12{,}5 - 1{,}2 = 11{,}3 \text{ m}^{2}$.

### Pourquoi les autres réponses sont fausses
- **a)** a additionné l'aire de la fenêtre à celle du mur au lieu de la soustraire.
- **c)** a soustrait $2{,}2$, c'est-à-dire la somme des dimensions de la fenêtre, au lieu de son aire.
- **d)** n'a retiré que $1$ (la hauteur de la fenêtre) au lieu de son aire $1{,}2$.

</details>

Avis : 

---

## 5. `cqc-angle-au-centre-elevee-5` (séries BEPC)

**Remarque du relecteur :** Énoncé indirect : il faut voir que W est le milieu de [YZ] et que le triangle XWY est isocèle ; la valeur 53,13° sert de leurre partiel (choix b).

**Énoncé :**

Le triangle $XYZ$ est rectangle en $X$. On donne $\sin(\widehat{XZY}) = 0{,}8$ ; une table trigonométrique associe à cette valeur l'angle $53{,}13°$. Le cercle circonscrit au triangle $XYZ$ a pour centre $W$. Quelle est la mesure de l'angle $\widehat{WXY}$ du triangle $XWY$ ?

- a) $73{,}74°$
- b) $53{,}13°$
- c) $36{,}87°$
- d) $26{,}565°$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
On retrouve un angle à partir de son sinus en lisant la table dans le sens inverse. L'angle au centre qui intercepte un arc mesure le double de l'angle inscrit interceptant ce même arc ; dans un triangle formé par deux rayons, les angles à la base sont égaux, et la somme des angles d'un triangle vaut $180°$.

### Corrigé

D'après la table, $\widehat{XZY} = 53{,}13°$.

L'angle inscrit $\widehat{XZY}$ et l'angle au centre $\widehat{XWY}$ interceptent le même arc $XY$ :

$$\widehat{XWY} = 2 \times 53{,}13° = 106{,}26°$$

Les segments $[WX]$ et $[WY]$ sont deux rayons du cercle circonscrit : le triangle $XWY$ est isocèle en $W$, donc $\widehat{WXY} = \widehat{WYX}$. La somme des angles du triangle vaut $180°$ :

$$\widehat{WXY} = \frac{180° - 106{,}26°}{2} = \frac{73{,}74°}{2} = 36{,}87°$$

### Pourquoi les autres réponses sont fausses
- **a)** a donné la somme des deux angles à la base sans la partager en deux.
- **b)** a repris la mesure de l'angle inscrit $\widehat{XZY}$ au lieu de calculer un angle à la base de $XWY$.
- **d)** a pris la moitié de l'angle inscrit au lieu de la moitié de $180° - 106{,}26°$.

</details>

Avis : 

---

## 6. `cqc-angle-au-centre-moyenne-4` (séries BEPC)

**Remarque du relecteur :** Le point D et l'angle ADB ne servent à rien ; donnée inutile mais pas trompeuse.

**Énoncé :**

Un cercle de centre $O$ passe par quatre points $A$, $B$, $C$ et $D$. Les angles inscrits $\widehat{ACB}$ et $\widehat{ADB}$ interceptent tous deux l'arc $AB$ ne contenant ni $C$ ni $D$. Sachant que $\widehat{ACB} = 27°$, quelle est la mesure de l'angle au centre $\widehat{AOB}$ qui intercepte ce même arc ?

- a) $27°$
- b) $13{,}5°$
- c) $54°$
- d) $126°$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
Deux angles inscrits qui interceptent le même arc ont la même mesure. L'angle au centre qui intercepte ce même arc mesure le double de chacun d'eux.

### Corrigé

$\widehat{ACB}$ et $\widehat{ADB}$ interceptent le même arc $AB$, donc $\widehat{ADB} = \widehat{ACB} = 27°$.

L'angle au centre correspondant mesure

$$\widehat{AOB} = 2 \times \widehat{ACB} = 2 \times 27° = 54°$$

### Pourquoi les autres réponses sont fausses
- **a)** a pensé que l'angle au centre a la même mesure que l'angle inscrit.
- **b)** a pris la moitié de l'angle inscrit au lieu du double.
- **d)** a calculé $180° - 54°$ au lieu de s'arrêter au double de l'angle inscrit.

</details>

Avis : 

---

## 7. `cqc-apotheme-moyenne-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : calcul de l'apothème par Pythagore dans l'espace, à la limite haute de la 3e.

**Énoncé :**

Une pyramide régulière a une base carrée de côté $10$ cm et une hauteur de $12$ cm. Quelle est l'aire latérale totale de la pyramide (ses quatre faces) ?

- a) $260 \text{ cm}^{2}$
- b) $65 \text{ cm}^{2}$
- c) $520 \text{ cm}^{2}$
- d) $240 \text{ cm}^{2}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule d'abord l'apothème, hypoténuse du triangle rectangle formé par la hauteur de la pyramide et le demi-côté de la base : $a^{2} = h^{2} + \left(\dfrac{c}{2}\right)^{2}$. Cet apothème sert ensuite de hauteur pour l'aire de chaque face latérale, un triangle isocèle de base $c$.

### Corrigé

Le demi-côté vaut $5$ cm : $a^{2} = 12^{2} + 5^{2} = 144 + 25 = 169$, donc $a = 13$ cm.

Aire d'une face : $\dfrac{10 \times 13}{2} = 65 \ \text{cm}^{2}$.

Aire latérale totale : $4 \times 65 = 260 \ \text{cm}^{2}$.

### Pourquoi les autres réponses sont fausses
- **b)** a calculé l'aire d'une seule face latérale au lieu des quatre.
- **c)** a oublié de diviser par $2$ dans l'aire du triangle : $4 \times 10 \times 13$.
- **d)** a pris la hauteur de la pyramide ($12$ cm) à la place de l'apothème ($13$ cm) pour les faces.

</details>

Avis : 

---

## 8. `cqc-apotheme-moyenne-1` (séries BEPC)

**Remarque du relecteur :** LIMITE : deux étapes (apothème depuis l'aire latérale puis Pythagore dans le triangle apothème/demi-côté/hauteur).

**Énoncé :**

Une pyramide régulière à base carrée de côté $16$ cm a une aire latérale totale de $544$ cm². Quelle est la hauteur de cette pyramide ?

- a) $17$ cm
- b) $9$ cm
- c) $15$ cm
- d) $\sqrt{353}$ cm

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

L'aire latérale totale, divisée par le nombre de faces, donne l'aire d'une face. Chaque face est un triangle isocèle de base $c$ et de hauteur $a$ (l'apothème), d'où $a = \dfrac{2\mathcal{A}_{1}}{c}$. La hauteur de la pyramide s'obtient ensuite par le théorème de Pythagore : $h^{2} = a^{2} - \left(\dfrac{c}{2}\right)^{2}$.

### Corrigé

*Apothème.* Aire d'une face : $\mathcal{A}_{1} = \dfrac{544}{4} = 136 \ \text{cm}^{2}$, puis $a = \dfrac{2 \times 136}{16} = 17$ cm.

*Hauteur.* Le demi-côté vaut $8$ cm et l'apothème est l'hypoténuse : $h^{2} = 17^{2} - 8^{2} = 289 - 64 = 225$, donc $h = 15$ cm.

**Vérification.** $15^{2} + 8^{2} = 225 + 64 = 289 = 17^{2}$.

### Pourquoi les autres réponses sont fausses
- **a)** a donné l'apothème au lieu de la hauteur de la pyramide.
- **b)** a soustrait les longueurs ($17 - 8$) au lieu d'utiliser le théorème de Pythagore.
- **d)** a additionné les carrés ($17^{2} + 8^{2}$) alors que l'apothème est l'hypoténuse.

</details>

Avis : 

---

## 9. `cqc-application-numerique-faible-1` (séries BEPC)

**Énoncé :**

Un cylindre de révolution a pour rayon de base $r = 3$ cm et pour hauteur $h = 10$ cm. Quel est son volume $V$, sachant que $V = \pi r^{2} h$ (on prendra $\pi = 3{,}14$) ?

- a) $94{,}2 \text{ cm}^{3}$
- b) $282{,}6 \text{ cm}^{3}$
- c) $188{,}4 \text{ cm}^{3}$
- d) $1\,130{,}4 \text{ cm}^{3}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

L'application numérique consiste à remplacer chaque lettre par la valeur donnée, puis à effectuer les calculs dans l'ordre des priorités : la puissance d'abord, ensuite les produits.

### Corrigé

$$V = \pi r^{2} h = 3{,}14 \times 3^{2} \times 10 = 3{,}14 \times 9 \times 10 = 28{,}26 \times 10 = 282{,}6 \ \text{cm}^{3}$$

### Pourquoi les autres réponses sont fausses
- **a)** a oublié d'élever le rayon au carré : $3{,}14 \times 3 \times 10$.
- **c)** a calculé $3^{2}$ comme $3 \times 2 = 6$ : $3{,}14 \times 6 \times 10$.
- **d)** a doublé le rayon avant de l'élever au carré : $3{,}14 \times 6^{2} \times 10$.

</details>

Avis : 

---

## 10. `cqc-calcul-de-longueur-moyenne-2` (séries BEPC)

**Remarque du relecteur :** LIMITE : on doit mettre la proportion en équation avec AE = AC - 15, un cran au-dessus du Thalès direct.

**Énoncé :**

Dans le triangle $ABC$, le point $D$ appartient au segment $[AB]$ et le point $E$ appartient au segment $[AC]$, avec $(DE)$ parallèle à $(BC)$. On donne $AB = 16$ cm, $AD = 6$ cm et $EC = 15$ cm.

Calculer la longueur $AC$.

- a) $40$ cm
- b) $31$ cm
- c) $9$ cm
- d) $24$ cm

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand l'énoncé donne le segment $EC$ (et non $AE$ ou $AC$ directement), on exprime d'abord le rapport $\dfrac{EC}{AC}$ en fonction du rapport de Thalès connu $\dfrac{AD}{AB}$, puisque $EC = AC - AE$.

### Corrigé

$(DE) \parallel (BC)$, donc, d'après le théorème de Thalès appliqué au sommet $A$ :
$$\frac{AE}{AC} = \frac{AD}{AB} = \frac{6}{16} = \frac{3}{8}$$

*Rapport de $EC$.* Comme $EC = AC - AE$ :
$$\frac{EC}{AC} = 1 - \frac{AE}{AC} = 1 - \frac{3}{8} = \frac{5}{8}$$

*Calcul de $AC$.*
$$\frac{5}{8} = \frac{15}{AC} \quad \Longrightarrow \quad 5 \times AC = 8 \times 15 = 120 \quad \Longrightarrow \quad AC = \frac{120}{5} = 24 \text{ cm}$$

*Calcul de $AE$.*
$$AE = AC - EC = 24 - 15 = 9 \text{ cm}$$

*Contrôle.* $\dfrac{AE}{AC} = \dfrac{9}{24} = \dfrac{3}{8}$, ce qui correspond bien au rapport de départ.

### Pourquoi les autres réponses sont fausses

- **a)** on a écrit $\dfrac{EC}{AC} = \dfrac{AD}{AB}$, alors que ce rapport vaut $\dfrac{AE}{AC}$ ; $EC$ n'est pas dans la même proportion que $AD$.
- **b)** on a additionné $EC + AB$, sans utiliser le théorème de Thalès.
- **c)** c'est la longueur $AE$, et non $AC$.

</details>

Avis : 

---

## 11. `cqc-centre-de-classe-elevee-0` (séries BEPC)

**Remarque du relecteur :** Préciser que la moyenne se calcule avec les centres des classes.

**Énoncé :**

Un club cycliste a mesuré les distances (en km) parcourues par 40 membres lors d'une sortie, regroupées dans le tableau suivant, où $a$ et $b$ sont des effectifs inconnus.

| Classe | $[0\,;\,10[$ | $[10\,;\,20[$ | $[20\,;\,30[$ | $[30\,;\,40[$ |
|---|---|---|---|---|
| Effectif | 6 | $a$ | $b$ | 4 |

Quelle expression donne la moyenne $M$ des distances parcourues, en fonction de $a$ et de $b$ (en utilisant les centres des classes) ?

- a) $M = \dfrac{120 + 10a + 20b}{40}$
- b) $M = \dfrac{170 + 15a + 25b}{4}$
- c) $M = \dfrac{40 + 15a + 25b}{40}$
- d) $M = \dfrac{170 + 15a + 25b}{40}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On remplace chaque classe par son centre, puis on écrit la moyenne pondérée $\bar{x} = \dfrac{\sum n_i c_i}{N}$, en gardant les effectifs inconnus sous forme littérale.

### Corrigé

*Centres des classes.*

| Classe | $[0;10[$ | $[10;20[$ | $[20;30[$ | $[30;40[$ |
|---|---|---|---|---|
| Centre | 5 | 15 | 25 | 35 |
| Effectif | 6 | $a$ | $b$ | 4 |

*Somme des produits centre × effectif.*

$$6 \times 5 + 15a + 25b + 4 \times 35 = 30 + 15a + 25b + 140 = 170 + 15a + 25b$$

*Moyenne.*

$$M = \frac{170 + 15a + 25b}{40}$$

### Pourquoi les autres réponses sont fausses

- **a)** on a utilisé les bornes inférieures des classes au lieu de leurs centres.
- **b)** on a divisé par $4$ (le nombre de classes) au lieu de diviser par l'effectif total $40$.
- **c)** on a oublié de multiplier les centres $5$ et $35$ par les effectifs $6$ et $4$ : seuls $a$ et $b$ ont été pondérés.

</details>

Avis : 

---

## 12. `cqc-centre-de-classe-faible-1` (séries BEPC)

**Remarque du relecteur :** Les quatre choix donnent la même classe : la première question de l'énoncé n'est pas évaluée.

**Énoncé :**

Le tableau ci-dessous regroupe les masses (en kg) de 20 sacs de café stockés dans un entrepôt.

| Classe | $[40\,;\,50[$ | $[50\,;\,60[$ | $[60\,;\,70[$ |
|---|---|---|---|
| Effectif | 5 | 9 | 6 |

Quel est le centre de la classe la plus représentée (celle qui a le plus grand effectif) ?

- a) $50$ kg
- b) $55$ kg
- c) $110$ kg
- d) $10$ kg

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La classe la plus représentée est celle dont l'effectif est le plus grand. Le centre d'une classe est la demi-somme de ses deux bornes.

### Corrigé

Les effectifs sont $5$, $9$ et $6$ : le plus grand est $9$, pour la classe $[50\,;\,60[$.

Centre de cette classe :

$$c = \frac{50 + 60}{2} = \frac{110}{2} = 55$$

La classe la plus représentée est $[50\,;\,60[$, de centre $55$ kg.

### Pourquoi les autres réponses sont fausses

- **a)** la bonne classe, mais $50$ est sa borne inférieure et non son centre.
- **c)** la bonne classe, mais on a additionné les bornes sans diviser par $2$.
- **d)** la bonne classe, mais $10$ est son amplitude et non son centre.

</details>

Avis : 

---

## 13. `cqc-centre-de-classe-moyenne-0` (séries BEPC)

**Remarque du relecteur :** Avec des classes, la moyenne obtenue par les centres est une valeur approchée ; on pourrait le préciser dans l'énoncé.

**Énoncé :**

Le tableau suivant donne les tailles (en cm) de 50 élèves d'un collège, regroupées en classes.

| Classe | $[140\,;\,150[$ | $[150\,;\,160[$ | $[160\,;\,170[$ | $[170\,;\,180[$ |
|---|---|---|---|---|
| Effectif | 8 | 14 | 20 | 8 |

Calcule la taille moyenne de ces élèves, en utilisant les centres des classes.

- a) $160$ cm
- b) $155{,}6$ cm
- c) $160{,}6$ cm
- d) $165{,}6$ cm

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une série groupée en classes, on remplace chaque classe par son centre (demi-somme des bornes), puis on applique la moyenne pondérée $\bar{x} = \dfrac{\sum n_i c_i}{N}$.

### Corrigé

*Centres des classes.*

| Classe | $[140;150[$ | $[150;160[$ | $[160;170[$ | $[170;180[$ |
|---|---|---|---|---|
| Centre | 145 | 155 | 165 | 175 |
| Effectif | 8 | 14 | 20 | 8 |

*Somme des produits centre × effectif.*

$$8 \times 145 = 1160 \quad ; \quad 14 \times 155 = 2170 \quad ; \quad 20 \times 165 = 3300 \quad ; \quad 8 \times 175 = 1400$$

$$\sum n_i c_i = 1160 + 2170 + 3300 + 1400 = 8030$$

*Moyenne.*

$$\bar{x} = \frac{8030}{50} = 160{,}6$$

La taille moyenne de ces élèves est de $160{,}6$ cm.

### Pourquoi les autres réponses sont fausses

- **a)** on a fait la moyenne simple des quatre centres, sans tenir compte des effectifs.
- **b)** on a pondéré les bornes inférieures des classes au lieu de leurs centres.
- **d)** on a pondéré les bornes supérieures des classes au lieu de leurs centres.

</details>

Avis : 

---

## 14. `cqc-centre-de-classe-moyenne-1` (séries BEPC)

**Remarque du relecteur :** Préciser qu'on calcule la moyenne à l'aide des centres des classes.

**Énoncé :**

Un standard téléphonique a enregistré les durées (en minutes) de 50 appels, regroupées dans le tableau suivant.

| Classe | $[0\,;\,5[$ | $[5\,;\,10[$ | $[10\,;\,15[$ | $[15\,;\,20[$ |
|---|---|---|---|---|
| Effectif | 12 | 18 | 15 | 5 |

Calcule la durée moyenne d'un appel, en utilisant les centres des classes.

- a) $8{,}8$ minutes
- b) $10$ minutes
- c) $6{,}3$ minutes
- d) $11{,}3$ minutes

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule le centre de chaque classe (demi-somme des bornes), puis la moyenne pondérée $\bar{x} = \dfrac{\sum n_i c_i}{N}$.

### Corrigé

*Centres des classes.*

| Classe | $[0;5[$ | $[5;10[$ | $[10;15[$ | $[15;20[$ |
|---|---|---|---|---|
| Centre | 2,5 | 7,5 | 12,5 | 17,5 |
| Effectif | 12 | 18 | 15 | 5 |

*Somme des produits centre × effectif.*

$$12 \times 2{,}5 = 30 \quad ; \quad 18 \times 7{,}5 = 135 \quad ; \quad 15 \times 12{,}5 = 187{,}5 \quad ; \quad 5 \times 17{,}5 = 87{,}5$$

$$\sum n_i c_i = 30 + 135 + 187{,}5 + 87{,}5 = 440$$

*Moyenne.*

$$\bar{x} = \frac{440}{50} = 8{,}8$$

La durée moyenne d'un appel est de $8{,}8$ minutes.

### Pourquoi les autres réponses sont fausses

- **b)** on a fait la moyenne simple des quatre centres, sans tenir compte des effectifs.
- **c)** on a pondéré les bornes inférieures des classes au lieu de leurs centres.
- **d)** on a pondéré les bornes supérieures des classes au lieu de leurs centres.

</details>

Avis : 

---

## 15. `cqc-cercle-circonscrit-faible-0` (séries BEPC)

**Énoncé :**

$ABC$ est un triangle rectangle en $A$ tel que $AB = 9$ cm et $AC = 12$ cm.

Calculer le rayon du cercle circonscrit au triangle $ABC$.

- a) $15$ cm
- b) $7{,}5$ cm
- c) $6$ cm
- d) $10{,}5$ cm

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un triangle rectangle, le cercle circonscrit a pour diamètre l'hypoténuse : son centre est le milieu de l'hypoténuse, et son rayon en vaut la moitié.

### Corrigé

*Calcul de l'hypoténuse $BC$ par Pythagore.*

$$BC^{2} = AB^{2} + AC^{2} = 9^{2} + 12^{2} = 81 + 144 = 225$$

$$BC = \sqrt{225} = 15 \ \text{cm}$$

*Rayon du cercle circonscrit.*

$$R = \frac{BC}{2} = \frac{15}{2} = 7{,}5$$

$$R = 7{,}5 \ \text{cm}$$

Le rayon du cercle circonscrit au triangle $ABC$ est de **7,5 cm**.

### Pourquoi les autres réponses sont fausses

- **a)** c'est le diamètre $BC$ du cercle, et non son rayon.
- **c)** c'est la moitié de $AC$ ; le rayon est la moitié de l'hypoténuse.
- **d)** on a pris la moitié de la somme des deux côtés de l'angle droit.

</details>

Avis : 

---

## 16. `cqc-configuration-en-papillon-faible-0` (séries BEPC)

**Énoncé :**

On considère un point $I$ et deux droites sécantes en $I$. Sur la première droite, les points $G$, $I$, $J$ sont alignés dans cet ordre (donc $I$ est entre $G$ et $J$). Sur la seconde droite, les points $H$, $I$, $K$ sont alignés dans cet ordre (donc $I$ est entre $H$ et $K$). Les droites $(GH)$ et $(JK)$ sont parallèles. On donne : $IG = 4$ cm, $IJ = 10$ cm et $IH = 6$ cm.

Calculer la longueur $IK$.

- a) $2{,}4$ cm
- b) $12$ cm
- c) $\dfrac{20}{3}$ cm
- d) $15$ cm

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsque deux droites sécantes en un point $I$ portent chacune deux points situés de part et d'autre de $I$ (configuration dite « en papillon »), et que les segments reliant les points les plus proches d'une part, et les points les plus éloignés d'autre part, sont parallèles, le théorème de Thalès s'applique exactement comme pour un triangle : les longueurs mesurées depuis $I$ restent proportionnelles.

### Corrigé

Les droites $(GJ)$ et $(HK)$ sont sécantes en $I$, et $(GH) \parallel (JK)$, donc, d'après le théorème de Thalès appliqué au sommet $I$ :

$$\frac{IG}{IJ} = \frac{IH}{IK}$$

$$\frac{4}{10} = \frac{6}{IK}$$

Par produit en croix :

$$4 \times IK = 10 \times 6 = 60$$

$$IK = \frac{60}{4} = 15 \text{ cm}$$

*Contrôle.* $\dfrac{4}{10} = 0{,}4$ et $\dfrac{6}{15} = 0{,}4$ : les deux rapports sont bien égaux.

### Pourquoi les autres réponses sont fausses

- **a)** on a écrit $\dfrac{IG}{IJ} = \dfrac{IK}{IH}$ : les rapports sont inversés d'une droite à l'autre.
- **b)** raisonnement additif : $IJ - IG = 6$, donc on a ajouté $6$ à $IH$ ; Thalès traduit une proportionnalité, pas une différence constante.
- **c)** on a calculé $\dfrac{IG \times IJ}{IH}$ au lieu de $\dfrac{IJ \times IH}{IG}$.

</details>

Avis : 

---

## 17. `cqc-cube-elevee-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : Pythagore appliqué deux fois dans l'espace (diagonale du cube), à la limite haute du programme de 3e.

**Énoncé :**

Un aquarium a la forme d'un cube d'arête $30$ cm.

Quelle est la valeur exacte de la longueur de la diagonale intérieure de cet aquarium (la distance entre un coin du fond et le coin du dessus le plus éloigné) ?

- a) $30\sqrt{2}$ cm
- b) $30\sqrt{3}$ cm
- c) $60$ cm
- d) $30 + 30\sqrt{2}$ cm

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La diagonale de l'espace d'un cube ne s'obtient pas en une seule étape : on calcule d'abord la diagonale d'une face carrée (par Pythagore, à partir de deux arêtes), puis on utilise cette diagonale comme côté d'un second triangle rectangle, avec la troisième arête, pour obtenir la diagonale de l'espace.

### Corrigé

**Étape 1 : diagonale d'une face.** Une face du cube est un carré de côté $a = 30$ cm. Sa diagonale $d_1$ est l'hypoténuse d'un triangle rectangle dont les deux côtés de l'angle droit mesurent chacun $30$ cm :

$$d_1^{2} = 30^{2} + 30^{2} = 900 + 900 = 1\,800$$

**Étape 2 : diagonale de l'espace.** La diagonale de l'espace $d$ est l'hypoténuse d'un second triangle rectangle, formé par la diagonale de la face $d_1$ (un côté de l'angle droit) et la troisième arête $a = 30$ cm (l'autre côté de l'angle droit) :

$$d^{2} = d_1^{2} + a^{2} = 1\,800 + 900 = 2\,700$$

$$d = \sqrt{2\,700} = \sqrt{900 \times 3} = 30\sqrt{3}$$

La valeur exacte de la diagonale est donc $d = 30\sqrt{3}$ cm.

**Valeur approchée.** Avec $\sqrt{3} \approx 1{,}732$ :

$$d \approx 30 \times 1{,}732 \approx 51{,}96$$

La diagonale intérieure de l'aquarium mesure $30\sqrt{3}$ cm, soit environ **52,0 cm**.

**Contrôle de vraisemblance.** Cette diagonale doit être strictement supérieure à l'arête ($30$ cm) et à la diagonale d'une face ($30\sqrt{2} \approx 42{,}4$ cm), puisqu'elle relie les deux coins les plus éloignés du cube : $52{,}0 > 42{,}4 > 30$, ce qui est cohérent.

### Pourquoi les autres réponses sont fausses

- **a)** c'est la diagonale d'une face carrée (première étape) ; il reste à la combiner avec la troisième arête.
- **c)** à la seconde étape, on a additionné $d_1^{2} + d_1^{2} = 3\,600$ au lieu de $d_1^{2} + 30^{2} = 2\,700$.
- **d)** on a additionné la diagonale d'une face et l'arête, alors qu'il faut appliquer le théorème de Pythagore.

</details>

Avis : 

---

## 18. `cqc-diagramme-semi-circulaire-elevee-0` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : écrire « semi-circulaire » en minuscules ; la mention « dont on ne connaît pas le nombre N » est superflue.

**Énoncé :**

Un village a fait tracer un diagramme semi-circulaire représentant la répartition de ses habitants actifs par secteur d'activité. Le secteur « Agriculture », dont l'angle mesure $60°$, compte $3\,000$ habitants actifs. Les deux autres secteurs mesurent : « Commerce » $72°$, et « Autres activités » (angle non indiqué).

Combien d'habitants actifs compte le secteur « Autres activités » ?

- a) $2\,400$
- b) $1\,200$
- c) $3\,600$
- d) $4\,800$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un diagramme semi-circulaire, chaque secteur est proportionnel à l'effectif qu'il représente : $\dfrac{\text{angle}}{180} = \dfrac{\text{effectif}}{N}$. Connaître le couple (angle, effectif) d'un seul secteur suffit donc à retrouver l'effectif total $N$ par produit en croix, avant d'appliquer la formule habituelle à chaque autre secteur ; un angle manquant s'obtient en complétant la somme des angles connus à $180°$.

### Corrigé

**Étape 1 : population active totale $N$.** Le secteur « Agriculture » a un angle de $60°$ pour un effectif de $3\,000$ habitants, donc par proportionnalité :

$$N = 3\,000 \times \frac{180}{60} = 3\,000 \times 3 = 9\,000 \ \text{habitants actifs}$$

**Étape 2 : angle du secteur « Autres activités ».**

$$180 - (60 + 72) = 180 - 132 = 48°$$

**Étape 3 : effectifs des deux autres secteurs.**

$$n_{\text{Commerce}} = \frac{72}{180} \times 9\,000 = 0{,}4 \times 9\,000 = 3\,600$$

$$n_{\text{Autres}} = \frac{48}{180} \times 9\,000 = 0{,}2\overline{6} \times 9\,000 = 2\,400$$

*Contrôle.* Les angles $60 + 72 + 48 = 180°$ recouvrent bien le demi-cercle entier, et les effectifs $3\,000 + 3\,600 + 2\,400 = 9\,000$ redonnent exactement la population active totale $N$ trouvée à l'étape 1.

Le village compte donc **9 000 habitants actifs**, répartis en $3\,000$ pour l'Agriculture, $3\,600$ pour le Commerce et $2\,400$ pour les Autres activités (angle de $48°$).

### Pourquoi les autres réponses sont fausses

- **b)** Utilise $360°$ pour le demi-cercle dans la dernière proportion : $\dfrac{48}{360}\times9\,000$.
- **c)** Donne l'effectif du secteur « Commerce » au lieu de celui de « Autres activités ».
- **d)** Utilise $360°$ pour trouver $N$ ($N=18\,000$), puis $\dfrac{48}{180}\times18\,000$.

</details>

Avis : 

---

## 19. `cqc-division-de-fractions-moyenne-0` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : « On donne le quotient… Quel est ce quotient » est maladroit ; écrire « Calcule le quotient de 7/10 par 14/15 ».

**Énoncé :**

Calcule le quotient de la fraction $\dfrac{7}{10}$ par la fraction $\dfrac{14}{15}$.

Quel est le résultat, sous forme de fraction irréductible ?

- a) $\dfrac{4}{3}$
- b) $\dfrac{49}{75}$
- c) $\dfrac{3}{4}$
- d) $\dfrac{3}{2}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

« Le quotient de $A$ par $B$ » désigne toujours $A \div B$ : $A$ est le dividende (le premier nombre cité), $B$ le diviseur (le second). Diviser par une fraction revient ensuite à multiplier par son inverse.

### Corrigé

Le quotient demandé est $\dfrac{7}{10} \div \dfrac{14}{15}$, dans cet ordre précis : inverser l'ordre des deux fractions donnerait un résultat différent.

On multiplie par l'inverse du diviseur :

$$\dfrac{7}{10} \div \dfrac{14}{15} = \dfrac{7}{10} \times \dfrac{15}{14}$$

On simplifie avant de multiplier : $7$ et $14$ sont tous deux divisibles par $7$, et $15$ et $10$ sont tous deux divisibles par $5$ :

$$\dfrac{7}{10} \times \dfrac{15}{14} = \dfrac{1}{2} \times \dfrac{3}{2} = \dfrac{3}{4}$$

$3$ et $4$ n'ont aucun facteur commun autre que $1$, donc $\dfrac{3}{4}$ est déjà irréductible.

Vérification numérique : $\dfrac{7}{10}=0{,}7$ et $\dfrac{14}{15}\approx0{,}933$ ; $0{,}7 \div 0{,}933 \approx 0{,}75$, ce qui correspond bien à $\dfrac{3}{4}=0{,}75$.

$$\dfrac{7}{10} \div \dfrac{14}{15} = \dfrac{3}{4}$$

### Pourquoi les autres réponses sont fausses

- **a)** Inverse l'ordre des deux fractions (calcule $\dfrac{14}{15}\div\dfrac{7}{10}$).
- **b)** Multiplie les deux fractions sans retourner la deuxième.
- **d)** Simplifie les numérateurs mais oublie le facteur $2$ du dénominateur : $\dfrac{1}{2}\times\dfrac{3}{2}$ devient $\dfrac{3}{2}$.

</details>

Avis : 

---

## 20. `cqc-double-distributivite-elevee-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : développer un produit de trois facteurs (degré 3) est à la limite haute du programme de 3e.

**Énoncé :**

Quel est le développement réduit de l'expression $G(x) = (x-2)(3x+1)(x+4)$ ?

- a) $3x^3+17x^2-22x-8$
- b) $3x^3+7x^2-22x-8$
- c) $3x^3+7x^2-20x-8$
- d) $3x^3+7x^2-22x+8$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour développer un produit de trois facteurs, on développe d'abord le produit de deux d'entre eux par double distributivité, $(a+b)(c+d)=ac+ad+bc+bd$, on réduit ce résultat intermédiaire, puis on distribue chaque terme du troisième facteur sur chaque terme obtenu, avant de réduire une dernière fois.

### Corrigé

**Étape 1 : on développe les deux premiers facteurs.**

$$(x-2)(3x+1) = 3x^2 + x - 6x - 2 = 3x^2 - 5x - 2$$

**Étape 2 : on multiplie ce résultat par le troisième facteur $(x+4)$.**

$$G(x) = (3x^2-5x-2)(x+4)$$

$$= 3x^2\times x + 3x^2\times 4 - 5x\times x - 5x\times 4 - 2\times x - 2\times 4$$

$$= 3x^3 + 12x^2 - 5x^2 - 20x - 2x - 8$$

**Étape 3 : on réduit les termes de même degré.**

$$G(x) = 3x^3 + 7x^2 - 22x - 8$$

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur $-5x\times x$ (écrit $+5x^2$) : $12x^2+5x^2=17x^2$.
- **c)** Oublie le terme $-2x$ : seul $-20x$ est conservé.
- **d)** Écrit $-2\times4=+8$ : erreur de signe sur le terme constant.

</details>

Avis : 

---

## 21. `cqc-double-distributivite-faible-1` (séries BEPC)

**Énoncé :**

Quel est le développement réduit de l'expression $C = (5-2x)(4+3x)$ ?

- a) $-6x^2+7x+20$
- b) $6x^2+7x+20$
- c) $-6x^2+23x+20$
- d) $-6x^2+15x+20$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour développer un produit de deux binômes $(a+b)(c+d)$, on distribue chaque terme du premier facteur sur chaque terme du second, selon la règle $(a+b)(c+d) = ac+ad+bc+bd$, puis on réduit les termes semblables. L'ordre dans lequel les termes apparaissent à l'intérieur de chaque facteur ne change rien à la méthode.

### Corrigé

$$C = (5-2x)(4+3x) = 5\times 4 + 5\times 3x + (-2x)\times 4 + (-2x)\times 3x$$

$$C = 20 + 15x - 8x - 6x^2$$

En réduisant les termes en $x$ :

$$C = -6x^2 + 7x + 20$$

### Pourquoi les autres réponses sont fausses

- **b)** Écrit $(-2x)\times3x=+6x^2$ : erreur de signe sur le terme en $x^2$.
- **c)** Écrit $(-2x)\times4=+8x$ : erreur de signe, d'où $15x+8x=23x$.
- **d)** Oublie le terme $(-2x)\times4=-8x$ : seul $15x$ est conservé.

</details>

Avis : 

---

## 22. `cqc-droite-horizontale-elevee-0` (séries BEPC)

**Remarque du relecteur :** Le point C ne sert pas à la question posée (il appartient sans doute à un exercice plus long) ; il est sans danger ici.

**Énoncé :**

Dans un repère orthonormé, on donne les trois sommets d'un triangle : $A(1\,;\,4)$, $B(6\,;\,4)$ et $C(3\,;\,-2)$.

Quelle est une équation de la droite $(AB)$ ?

- a) $x = 4$
- b) $y = 0$
- c) $y = -2$
- d) $y = 4$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Avant de calculer un coefficient directeur, il est utile de comparer directement les coordonnées des deux points : si leurs ordonnées sont égales, la droite qui les joint est horizontale, quelles que soient leurs abscisses respectives.

### Corrigé

On compare les ordonnées de $A$ et de $B$ : $y_A = 4$ et $y_B = 4$, ces deux ordonnées sont **égales**, bien que les abscisses $x_A=1$ et $x_B=6$ soient différentes.

La droite $(AB)$ est donc **horizontale**.

*Équation.* Comme tous les points de $(AB)$ ont pour ordonnée $4$ :

$$(AB) : y = 4$$

*Contrôle par le coefficient directeur.* Le calcul habituel donne :

$$a = \dfrac{y_B-y_A}{x_B-x_A} = \dfrac{4-4}{6-1} = \dfrac{0}{5} = 0$$

Un coefficient directeur nul confirme bien qu'il s'agit d'une droite horizontale.

*Remarque.* Le troisième sommet $C(3\,;\,-2)$ n'appartient pas à cette droite, puisque son ordonnée $-2$ est différente de $4$ : c'est cohérent, puisque $A$, $B$ et $C$ forment un triangle (trois points non alignés).

### Pourquoi les autres réponses sont fausses

- **a)** Confond droite horizontale et droite verticale : $x=4$ est la droite verticale passant par les points d'abscisse $4$.
- **b)** Confond le coefficient directeur ($0$) avec l'ordonnée à l'origine ($4$).
- **c)** Utilise l'ordonnée du point $C$, qui n'appartient pas à la droite $(AB)$.

</details>

Avis : 

---

## 23. `cqc-droite-horizontale-faible-1` (séries BEPC)

**Remarque du relecteur :** Préciser « parallèle à l'axe des abscisses » ou « dans un repère usuel » : « horizontale » est l'usage courant mais il est imprécis.

**Énoncé :**

On donne les équations de quatre droites :

$(D_1) : y = 6$ ; $(D_2) : x = 6$ ; $(D_3) : y = 6x$ ; $(D_4) : x + y = 6$.

Laquelle de ces quatre droites est parallèle à l'axe des abscisses ?

- a) $(D_2)$
- b) $(D_3)$
- c) $(D_1)$
- d) $(D_4)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Une droite horizontale a une équation de la forme $y = k$ (une constante, sans terme en $x$). Elle a toujours pour coefficient directeur $0$, puisqu'on peut l'écrire $y = 0 \times x + k$ : son ordonnée ne varie jamais lorsque $x$ varie.

### Corrigé

On examine chaque équation.

$(D_1) : y = 6$ est de la forme $y=k$ avec $k=6$, sans aucun terme en $x$ : c'est une droite horizontale.

$(D_2) : x = 6$ ne contient aucun terme en $y$ : c'est une droite verticale, pas horizontale.

$(D_3) : y = 6x$ est de la forme $y = ax$ avec $a=6 \neq 0$ : c'est une droite oblique passant par l'origine.

$(D_4) : x + y = 6$ s'écrit aussi $y = -x + 6$, de coefficient directeur $-1 \neq 0$ : c'est une droite oblique.

La droite horizontale est donc $(D_1)$, et son coefficient directeur vaut $0$ (on peut écrire $(D_1) : y = 0 \times x + 6$).

### Pourquoi les autres réponses sont fausses

- **a)** $x=6$ est l'équation d'une droite verticale.
- **b)** $y=6x$ est une droite oblique passant par l'origine, de coefficient directeur $6$.
- **d)** $x+y=6$ s'écrit $y=-x+6$ : droite oblique de coefficient directeur $-1$.

</details>

Avis : 

---

## 24. `cqc-duree-faible-1` (séries BEPC)

**Énoncé :**

Un match de football débute à $15\text{h}20$ et se termine à $17\text{h}05$. Quelle est la durée de ce match ?

- a) 2h15
- b) 1h45
- c) 2h45
- d) 1h25

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour calculer la durée écoulée entre deux heures, on soustrait l'heure de départ à l'heure de fin. Si les minutes de l'heure de fin sont inférieures à celles de l'heure de départ, on emprunte $60$ minutes à l'heure précédente avant de soustraire.

### Corrigé

On veut calculer $17\text{h}05 - 15\text{h}20$.

*Difficulté.* Les minutes de fin ($05$) sont inférieures aux minutes de départ ($20$) : on ne peut pas soustraire directement.

*Emprunt.* On transforme $17\text{h}05$ en empruntant une heure : $17\text{h}05 = 16\text{h}65$ (puisque $16\text{h} + 65\text{min} = 16\text{h} + 1\text{h}05 = 17\text{h}05$).

*Soustraction.*

$$\text{heures : } 16 - 15 = 1 \qquad ; \qquad \text{minutes : } 65 - 20 = 45$$

La durée du match est donc $1\text{h}45\text{min}$.

*Contrôle.* $15\text{h}20 + 1\text{h}45\text{min} = 16\text{h}65\text{min} = 17\text{h}05$

### Pourquoi les autres réponses sont fausses

- **a)** Soustrait les heures ($17-15=2$) puis les minutes dans l'autre sens ($20-05=15$).
- **c)** Oublie l'emprunt d'une heure : $17-15=2$ et $65-20=45$.
- **d)** Compte $20$ min au lieu de $40$ min de $15\text{h}20$ à $16\text{h}00$, puis ajoute $1\text{h}05$.

</details>

Avis : 

---

## 25. `cqc-duree-moyenne-0` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : le contexte (une équation qui fixe la durée d'attente) est artificiel.

**Énoncé :**

À l'entrée d'un stade, l'affluence des supporters est telle que la durée d'attente $T$, en minutes, d'un supporter avant d'entrer vérifie l'équation :

$$3T - 45 = 165$$

Sachant que ce supporter se présente au guichet à $18\text{h}50$, à quelle heure entre-t-il au stade ?

- a) 19h30
- b) 20h10
- c) 22h20
- d) 20h00

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On résout d'abord l'équation pour obtenir la durée en minutes. Une durée en minutes se convertit en heures et minutes par division euclidienne par $60$ : le quotient donne le nombre d'heures, le reste le nombre de minutes restantes. On ajoute enfin cette durée à l'heure de départ pour obtenir l'heure d'arrivée.

### Corrigé

*Résolution de l'équation.*

$$3T - 45 = 165$$

$$3T = 165 + 45 = 210$$

$$T = \dfrac{210}{3} = 70$$

La durée d'attente est donc $T = 70$ minutes.

*Conversion en heures et minutes.*

$$70 = 60 \times 1 + 10$$

soit $1$ heure et $10$ minutes.

*Heure d'entrée au stade.* Le supporter se présente à $18\text{h}50$ ; on ajoute $1\text{h}10\text{min}$ :

*Addition des minutes.* $50 + 10 = 60$ min $= 1$ heure exactement, sans minutes restantes.

*Addition des heures.* $18\text{h} + 1\text{h}$ (durée) $+ 1\text{h}$ (obtenue par la conversion des minutes) $= 20\text{h}$.

Le supporter entre donc au stade à **20h00**.

*Contrôle.* $18\text{h}50 + 1\text{h}10\text{min} = 19\text{h}60\text{min} = 20\text{h}00$

### Pourquoi les autres réponses sont fausses

- **a)** Résout mal l'équation : $3T=165-45=120$, d'où $T=40$ min.
- **b)** Compte deux fois les $10$ minutes de $18\text{h}50$ à $19\text{h}00$, puis ajoute $1\text{h}10$.
- **c)** Oublie de diviser par $3$ : prend $T=210$ min.

</details>

Avis : 

---

## 26. `cqc-encadrement-elevee-0` (séries BEPC)

**Remarque du relecteur :** Le choix b (-0,277 < … < -0,276) est aussi un encadrement VRAI (valeur ≈ -0,27671) à trois décimales : l'énoncé ne dit pas explicitement qu'il faut partir de l'encadrement donné de √3 ; préciser « en utilisant l'encadrement donné » ou remplacer b par un encadrement faux.

**Énoncé :**

Sachant que $1{,}732 < \sqrt{3} < 1{,}733$, quel est l'encadrement, obtenu en utilisant uniquement cet encadrement de $\sqrt{3}$, de $\dfrac{7 - 5\sqrt{3}}{6}$ dont les bornes sont écrites avec trois décimales (borne inférieure arrondie par défaut, borne supérieure arrondie par excès) ?

- a) $-0{,}278 < \dfrac{7 - 5\sqrt{3}}{6} < -0{,}276$
- b) $-0{,}277 < \dfrac{7 - 5\sqrt{3}}{6} < -0{,}276$
- c) $2{,}610 < \dfrac{7 - 5\sqrt{3}}{6} < 2{,}611$
- d) $-1{,}665 < \dfrac{7 - 5\sqrt{3}}{6} < -1{,}660$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans une expression comportant plusieurs opérations successives, on transforme l'encadrement pas à pas dans l'ordre des opérations : multiplication, puis passage à l'opposé (qui inverse le sens), puis addition, puis division. Chaque inversion de sens ne doit être appliquée qu'une seule fois, au bon endroit.

### Corrigé

*Encadrement de départ.*
$$1{,}732 < \sqrt{3} < 1{,}733$$

*Étape 1 - multiplier par $5$.*
$$8{,}660 < 5\sqrt{3} < 8{,}665$$

*Étape 2 - passer à l'opposé.* Le sens des inégalités s'inverse :
$$-8{,}665 < -5\sqrt{3} < -8{,}660$$

*Étape 3 - ajouter $7$.*
$$7 - 8{,}665 < 7 - 5\sqrt{3} < 7 - 8{,}660$$
$$-1{,}665 < 7 - 5\sqrt{3} < -1{,}660$$

*Étape 4 - diviser par $6$.*
$$\frac{-1{,}665}{6} < \frac{7 - 5\sqrt{3}}{6} < \frac{-1{,}660}{6}$$
$$-0{,}2775 < \frac{7 - 5\sqrt{3}}{6} < -0{,}27667$$

*Élargissement au millième (ordre 3).* On arrondit la borne inférieure vers le bas (plus négative) et la borne supérieure vers le haut (moins négative) :
$$-0{,}278 < \frac{7 - 5\sqrt{3}}{6} < -0{,}276$$

### Piège à éviter
Le passage à l'opposé n'a lieu qu'une seule fois, à l'étape 2 ; les étapes 3 et 4 conservent le sens des inégalités. Élargir un encadrement de nombres négatifs signifie rendre le minorant **plus négatif** et le majorant **moins négatif** : c'est l'inverse de l'intuition qu'on a avec des nombres positifs.

### Pourquoi les autres réponses sont fausses

- **b)** Arrondit la borne inférieure $-0{,}2775$ vers $-0{,}277$ (par excès) : cet encadrement ne contient pas toutes les valeurs possibles.
- **c)** Ne passe pas à l'opposé de $5\sqrt{3}$ et calcule en fait $\dfrac{7 + 5\sqrt{3}}{6}$.
- **d)** S'arrête à l'étape $7 - 5\sqrt{3}$ et oublie de diviser par $6$.

</details>

Avis : 

---

## 27. `cqc-facteur-commun-faible-1` (séries BEPC)

**Énoncé :**

Quelle est la forme factorisée de $C(x) = 5x(x+4) - 3(x+4)$ ?

- a) $C(x) = (x+4)(5x+3)$
- b) $C(x) = (x+4)(5x-12)$
- c) $C(x) = (x+4)(5x-3)$
- d) $C(x) = (x+4)(3-5x)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Un facteur commun peut être une simple parenthèse répétée dans deux termes, même si les coefficients qui l'accompagnent sont différents : on factorise cette parenthèse en gardant, dans le facteur restant, le signe de chaque terme d'origine.

### Corrigé

Le facteur $(x+4)$ apparaît dans les deux termes de $C(x)$, avec un signe $-$ devant le second.

$C(x) = (x+4)(5x - 3)$

Forme factorisée : $C(x) = (x+4)(5x-3)$.

### Pourquoi les autres réponses sont fausses

- **a)** Oublie le signe $-$ devant le second terme.
- **b)** Distribue le $-3$ sur la parenthèse $(x+4)$ avant de factoriser.
- **d)** Inverse l'ordre des termes du second facteur, ce qui change son signe.

</details>

Avis : 

---

## 28. `cqc-figures-superposables-moyenne-1` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : « deux sommets correspondants de deux parcelles triangulaires » n'a pas de sens ici et n'apporte rien ; simplifier le contexte.

**Énoncé :**

Dans un repère orthonormé $(O\,;\,\vec{i}\,;\,\vec{j})$ gradué en mètres, un géomètre relève deux points : $G(-4\,;\,2)$ et $G'(6\,;\,2)$. Quelle est une équation de la médiatrice du segment $[GG']$ ?

- a) $x = 2$
- b) $y = 2$
- c) $x = 1$
- d) $x = 5$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour trouver la médiatrice d'un segment, on cherche son milieu puis la perpendiculaire au segment passant par ce milieu. Si deux points ont la même ordonnée, le segment qui les joint est horizontal et sa médiatrice est la droite verticale passant par son milieu, d'équation $x = $ abscisse du milieu.

### Corrigé

$G(-4\,;\,2)$ et $G'(6\,;\,2)$ ont la même ordonnée : le segment $[GG']$ est horizontal. Son milieu a pour coordonnées $\left(\dfrac{-4+6}{2}\,;\,2\right) = (1\,;\,2)$. La médiatrice d'un segment horizontal est la droite verticale passant par son milieu : c'est la droite d'équation $x = 1$.

*Contrôle.* Le point $(1\,;\,2)$ est à $5$ unités de $G$ et de $G'$ ($1-(-4) = 5$ et $6-1 = 5$).

### Pourquoi les autres réponses sont fausses

- **a)** on a additionné les abscisses $-4$ et $6$ sans diviser par $2$ pour obtenir le milieu.
- **b)** c'est la droite (horizontale) qui contient $G$ et $G'$, et non leur médiatrice, qui est perpendiculaire à $(GG')$.
- **d)** $5$ est la demi-distance $GG'$ et non l'abscisse du milieu du segment.

</details>

Avis : 

---

## 29. `cqc-hauteur-moyenne-2` (séries BEPC)

**Énoncé :**

Une pyramide a pour base un rectangle de $8$ cm sur $5$ cm et pour volume $100$ cm³. Calcule sa hauteur.

- a) $2{,}5$ cm
- b) $7{,}5$ cm
- c) $12{,}5$ cm
- d) $20$ cm

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Le volume d'une pyramide vaut le tiers du produit de l'aire de sa base par sa hauteur : $V = \dfrac{\mathcal{B} \times h}{3}$, d'où $h = \dfrac{3V}{\mathcal{B}}$.

### Corrigé

*Aire de la base.* $$\mathcal{B} = 8 \times 5 = 40 \ \text{cm}^2$$

*Hauteur.*

$$h = \frac{3V}{\mathcal{B}} = \frac{3 \times 100}{40} = \frac{300}{40} = 7{,}5$$

$h = 7{,}5$ cm.

*Vérification.* $\dfrac{40 \times 7{,}5}{3} = \dfrac{300}{3} = 100$ cm³

### Pourquoi les autres réponses sont fausses

- **a)** le facteur $3$ a été oublié : $h = \dfrac{V}{\mathcal{B}}$ au lieu de $\dfrac{3V}{\mathcal{B}}$.
- **c)** on a divisé le volume par la longueur $8$ cm du rectangle au lieu de son aire.
- **d)** on a divisé le volume par la largeur $5$ cm du rectangle au lieu de son aire.

</details>

Avis : 

---

## 30. `cqc-hauteur-d-une-pyramide-elevee-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : tétraèdre régulier et centre de gravité de la base, rendus accessibles grâce aux résultats admis (GA et angle droit en G).

**Énoncé :**

$SABC$ est un tétraèdre régulier d'arête $6$ cm : ses six arêtes ont toutes la même longueur, $6$ cm. Le sommet $S$ se projette orthogonalement en $G$, centre de gravité du triangle équilatéral $ABC$. On admet que la distance de $G$ à un sommet de la base vaut $GA = \dfrac{a\sqrt{3}}{3}$, où $a$ est la longueur de l'arête, et que le triangle $SGA$ est rectangle en $G$.

Quelle est la hauteur $SG$ de ce tétraèdre, sous forme exacte simplifiée ?

- a) $4\sqrt{3}$ cm
- b) $2\sqrt{3}$ cm
- c) $6-2\sqrt{3}$ cm
- d) $2\sqrt{6}$ cm

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un tétraèdre régulier, le sommet se projette orthogonalement sur le centre de gravité de la face opposée. Le triangle formé par le sommet, ce centre de gravité et un sommet de la base est rectangle en ce centre de gravité : le théorème de Pythagore s'y applique, avec l'arête du tétraèdre comme hypoténuse.

### Corrigé

*Calcul de $GA$.*

$$GA = \frac{a\sqrt{3}}{3} = \frac{6\sqrt{3}}{3} = 2\sqrt{3} \ \text{cm} \qquad \Longrightarrow \qquad GA^2 = (2\sqrt{3})^2 = 4 \times 3 = 12$$

*Théorème de Pythagore dans le triangle $SGA$, rectangle en $G$, d'hypoténuse $[SA]$ (une arête du tétraèdre, donc $SA = 6$ cm).*

$$SA^2 = SG^2 + GA^2 \quad \Longrightarrow \quad SG^2 = SA^2 - GA^2 = 6^2 - 12 = 36 - 12 = 24$$

*Extraction et simplification du radical.*

$$SG = \sqrt{24} = \sqrt{4 \times 6} = \sqrt{4} \times \sqrt{6} = 2\sqrt{6}$$

La hauteur du tétraèdre vaut exactement $SG = 2\sqrt{6}$ cm, soit environ $2 \times 2{,}449 \approx 4{,}90$ cm.

*Contrôle de vraisemblance.* $4{,}90 < 6$ : la hauteur reste bien inférieure à l'arête, qui est l'hypoténuse du triangle $SGA$.

### Conseil
Cette relation, $SG = \dfrac{a\sqrt{6}}{3}$, redonne bien $\dfrac{6\sqrt{6}}{3} = 2\sqrt{6}$ : c'est la formule générale de la hauteur d'un tétraèdre régulier d'arête $a$, qu'on peut retrouver à chaque fois par le même raisonnement en triangle rectangle plutôt que de l'apprendre par cœur.

### Pourquoi les autres réponses sont fausses

- **a)** on a additionné les carrés ($36+12 = 48$) au lieu de les soustraire : l'arête $SA$ est l'hypoténuse, donc $SG^2 = SA^2 - GA^2$.
- **b)** c'est la distance $GA$, non la hauteur $SG$ : le calcul s'est arrêté avant l'application du théorème de Pythagore.
- **c)** on a soustrait les longueurs ($SA - GA$) au lieu de leurs carrés : le théorème de Pythagore porte sur les carrés.

</details>

Avis : 

---

## 31. `cqc-image-d-une-figure-moyenne-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : homothétie de rapport négatif, à vérifier selon le programme de 3e du pays.

**Énoncé :**

Le segment $[MN]$ mesure $8$ cm. Soit $h$ l'homothétie de centre $O$ (un point extérieur au segment $[MN]$) et de rapport $k = -\dfrac{3}{2}$. On note $M'$ et $N'$ les images respectives de $M$ et $N$ par $h$. Quelle est la longueur $M'N'$ ?

- a) $8$ cm
- b) $\dfrac{16}{3}$ cm
- c) $18$ cm
- d) $12$ cm

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans une homothétie de rapport $k$, toutes les longueurs sont multipliées par $|k|$, la valeur absolue du rapport. Le signe de $k$ n'agit pas sur les longueurs : il indique seulement de quel côté du centre se trouve l'image.

### Corrigé

$$M'N' = |k| \times MN = \left|-\frac{3}{2}\right| \times 8 = \frac{3}{2}\times 8 = 12 \text{ cm}$$

### Pourquoi les autres réponses sont fausses

- **a)** on a cru que l'homothétie conservait les longueurs, comme une symétrie : elle les multiplie par $|k|$.
- **b)** on a divisé par $|k|$ ($8\times\dfrac{2}{3}$) au lieu de multiplier : le rapport $\dfrac{3}{2}$ est supérieur à $1$, c'est un agrandissement.
- **c)** on a multiplié par $k^2 = \dfrac{9}{4}$, coefficient des aires, alors que les longueurs sont multipliées par $|k|$.

</details>

Avis : 

---

## 32. `cqc-nature-d-un-triangle-moyenne-0` (séries BEPC)

**Énoncé :**

Dans un repère orthonormé $(O, I, J)$ du plan, on donne les points $A(0\,;\,0)$, $B(4\,;\,0)$ et $C(2\,;\,2\sqrt{3})$.

Quelle est la nature exacte du triangle $ABC$ ?

- a) Isocèle en $C$, mais non équilatéral.
- b) Rectangle en $C$.
- c) Équilatéral.
- d) Quelconque.

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour déterminer la nature exacte d'un triangle à partir des coordonnées de ses sommets, on calcule les trois longueurs de ses côtés avec la formule de la distance $MN = \sqrt{(x_N-x_M)^2+(y_N-y_M)^2}$, puis on compare ces trois valeurs : trois côtés égaux signalent un triangle équilatéral.

### Corrigé

*Longueur $AB$.*

$$AB = \sqrt{(4-0)^2+(0-0)^2} = \sqrt{16} = 4$$

*Longueur $AC$.*

$$AC = \sqrt{(2-0)^2+(2\sqrt{3}-0)^2} = \sqrt{4 + 4\times3} = \sqrt{4+12} = \sqrt{16} = 4$$

*Longueur $BC$.*

$$BC = \sqrt{(2-4)^2+(2\sqrt{3}-0)^2} = \sqrt{4 + 12} = \sqrt{16} = 4$$

*Comparaison.*

$$AB = AC = BC = 4$$

Les trois côtés du triangle $ABC$ ont la même longueur : le triangle $ABC$ est donc **équilatéral**.

### Piège à éviter
Une fois les trois côtés reconnus égaux, la nature exacte est entièrement déterminée : un triangle équilatéral a nécessairement ses trois angles égaux à $60°$, donc aucun angle droit. Il est inutile (et incorrect) de chercher en plus une propriété de rectangle : les deux ne coexistent jamais.

### Pourquoi les autres réponses sont fausses

- **a)** on a calculé $(2\sqrt{3})^2 = 6$ au lieu de $12$ : on trouve alors $AC = BC = \sqrt{10} \neq AB$.
- **b)** les trois côtés valent $4$ : un triangle équilatéral a trois angles de $60°$, aucun n'est droit.
- **d)** les trois longueurs sont égales ($AB = AC = BC = 4$), le triangle a donc des propriétés particulières.

</details>

Avis : 

---

## 33. `cqc-norme-d-un-vecteur-moyenne-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : notation ||d|| et mot « norme » ; en 3e on parle surtout de distance AB dans un repère orthonormé.

**Énoncé :**

Un signal radar enregistre le déplacement d'un aéronef entre deux instants successifs. Dans un repère orthonormé, ce déplacement est modélisé par le vecteur $\vec{d}\,(6\,;\,10)$, coordonnées exprimées en kilomètres.

Quelle est la norme $\|\vec{d}\|$ de ce vecteur (valeur exacte, simplifiée au maximum) ?

- a) $4\sqrt{34}$ km
- b) $2\sqrt{34}$ km
- c) $16$ km
- d) $4$ km

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La norme d'un vecteur $\vec{u}\,(x\,;\,y)$ se calcule par $\|\vec{u}\| = \sqrt{x^{2}+y^{2}}$. Quand le résultat n'est pas un carré parfait, on le simplifie en extrayant le plus grand carré parfait possible du nombre sous la racine.

### Corrigé

$$\|\vec{d}\| = \sqrt{6^{2}+10^{2}} = \sqrt{36+100} = \sqrt{136}$$

*Simplification.* $136 = 4 \times 34$, et $4$ est le plus grand carré parfait qui divise $136$ :

$$\|\vec{d}\| = \sqrt{4 \times 34} = 2\sqrt{34}$$

La norme est la distance parcourue en ligne droite : environ $2 \times 5{,}83 \approx 11{,}66$ km.

### Pourquoi les autres réponses sont fausses

- **a)** on a sorti $4$ de la racine au lieu de $\sqrt{4}=2$ : $\sqrt{4\times34}=2\sqrt{34}$.
- **c)** on a additionné les coordonnées ($6+10$) au lieu d'appliquer $\sqrt{x^{2}+y^{2}}$.
- **d)** on a oublié les carrés et calculé $\sqrt{6+10}$ au lieu de $\sqrt{6^{2}+10^{2}}$.

</details>

Avis : 

---

## 34. `cqc-produit-en-croix-moyenne-1` (séries BEPC)

**Énoncé :**

Un groupe de 6 ouvriers construit un mur en 15 jours, tous en travaillant au même rythme. Combien de jours faudrait-il à 10 ouvriers, travaillant au même rythme, pour construire le même mur ?

- a) 9 jours
- b) 25 jours
- c) 11 jours
- d) 1,5 jour

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Deux grandeurs sont inversement proportionnelles quand leur produit reste constant : si l'une est multipliée par un facteur, l'autre est divisée par ce même facteur.

### Corrigé

Le nombre d'ouvriers et le nombre de jours nécessaires sont inversement proportionnels : plus il y a d'ouvriers, moins il faut de jours, et leur produit (le travail total, en ouvrier-jours) reste constant.

$$6 \times 15 = 90 \text{ (ouvrier-jours)}$$

Avec 10 ouvriers, en notant $d$ le nombre de jours cherché :
$$10 \times d = 90$$
$$d = \frac{90}{10} = 9$$

Il faudrait $9$ jours à 10 ouvriers.

*Contrôle.* 10 ouvriers travaillent plus vite que 6 : il est cohérent que $9$ jours soit inférieur à $15$ jours.

### Piège à éviter
N'écris pas $\dfrac{6}{15}=\dfrac{10}{d}$ comme pour une proportionnalité directe : plus d'ouvriers signifie moins de jours. C'est le produit $6\times15$ qui reste constant.

### Pourquoi les autres réponses sont fausses

- **b)** on a traité la situation comme une proportionnalité directe ($15\times10\div6$) : plus d'ouvriers donnerait plus de jours, ce qui est absurde.
- **c)** on a raisonné par différence : 4 ouvriers de plus donneraient 4 jours de moins, ce qui ne tient pas compte de la proportionnalité.
- **d)** on a divisé $15$ par $10$ sans tenir compte du nombre d'ouvriers de départ.

</details>

Avis : 

---

## 35. `cqc-relation-de-chasles-moyenne-2` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : imposer « la relation de Chasles » est artificiel, puisque le calcul direct D - A suffit et que B et C ne servent qu'à ce détour ; écrire par exemple « Calcule les coordonnées de AD ». Mettre aussi les flèches de vecteur dans les choix.

**Énoncé :**

Dans un repère, on considère quatre points $A(-2\,;\,1)$, $B(3\,;\,4)$, $C(6\,;\,-1)$ et $D(1\,;\,5)$.

En utilisant la relation de Chasles, quelles sont les coordonnées du vecteur $\overrightarrow{AD}$ ?

- a) $(3\,;\,-8)$
- b) $(13\,;\,4)$
- c) $(-3\,;\,-4)$
- d) $(3\,;\,4)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

La relation de Chasles s'applique plusieurs fois de suite lorsqu'un trajet comporte plusieurs étapes : $\overrightarrow{AB}+\overrightarrow{BC}+\overrightarrow{CD}=\overrightarrow{AD}$. Chaque vecteur intermédiaire se calcule par $\overrightarrow{MN}\,(x_N-x_M\,;\,y_N-y_M)$.

### Corrigé

$$\overrightarrow{AB}\,(5\,;\,3) \qquad \overrightarrow{BC}\,(3\,;\,-5) \qquad \overrightarrow{CD}\,(-5\,;\,6)$$

$$\overrightarrow{AD} = \overrightarrow{AB} + \overrightarrow{BC} + \overrightarrow{CD} = (5+3-5\,;\,3-5+6) = (3\,;\,4)$$

Vérification directe : $\overrightarrow{AD}\,(1-(-2)\,;\,5-1) = (3\,;\,4)$.

### Pourquoi les autres réponses sont fausses

- **a)** erreur de signe sur $\overrightarrow{CD}\,(-5\,;\,6)$ : on a retranché $6$ à l'ordonnée au lieu de l'ajouter.
- **b)** erreur de signe sur l'abscisse de $\overrightarrow{CD}$ : on a ajouté $5$ au lieu d'ajouter $-5$.
- **c)** ce sont les coordonnées du vecteur opposé $\overrightarrow{DA}$ : on a inversé l'origine et l'extrémité.

</details>

Avis : 

---

## 36. `cqc-repere-moyenne-1` (séries BEPC)

**Énoncé :**

On considère la droite $(D)$ d'équation $y = -3x + 1$. Lequel des points suivants appartient à la droite $(D)$ ?

- a) $L(-1\,;\,-2)$
- b) $M(-1\,;\,2)$
- c) $K(-1\,;\,4)$
- d) $N(4\,;\,-1)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour savoir si un point appartient à une droite d'équation $y = ax + b$, on remplace $x$ par l'abscisse du point dans l'équation et on compare le résultat obtenu à l'ordonnée du point. Le point appartient à la droite si et seulement si les deux valeurs sont égales.

### Corrigé

*Calcul de l'ordonnée attendue pour $x = -1$.*

$$y = -3 \times (-1) + 1$$

$$y = 3 + 1 = 4$$

*Comparaison.* L'ordonnée obtenue, $4$, est égale à l'ordonnée du point $K$, qui vaut aussi $4$.

$$4 = 4$$

Le point $K(-1\,;\,4)$ appartient donc bien à la droite $(D)$. Les autres points proposés ne vérifient pas l'équation.

### Pourquoi les autres réponses sont fausses

- **a)** Pour $x=-1$, $-3\times(-1)$ vaut $3$ et non $-3$ ; l'ordonnée attendue est $4$, pas $-2$.
- **b)** Tu as calculé $3 - 1$ : le terme $+1$ de l'équation est devenu $-1$ ; l'ordonnée attendue est $4$.
- **d)** Les coordonnées de $K$ sont inversées ; pour $x=4$, l'équation donne $y=-11$, et non $-1$.


</details>

Avis : 

---

## 37. `cqc-repere-moyenne-3` (séries BEPC)

**Remarque du relecteur :** Le choix a) porte le nom A' alors que les autres ne donnent que le couple : présentation hétérogène qui signale la bonne réponse.

**Énoncé :**

Dans un repère, on donne les points $A(5\,;\,-3)$ et $O(1\,;\,2)$. Quelles sont les coordonnées du point $A'$, symétrique du point $A$ par rapport au point $O$ ?

- a) $A'(-3\,;\,7)$
- b) $A'(-3\,;\,1)$
- c) $A'(-4\,;\,5)$
- d) $A'(3\,;\,-0{,}5)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Le point $A'$ est le symétrique de $A$ par rapport à $O$ si et seulement si $O$ est le milieu du segment $[AA']$. On retrouve donc les coordonnées de $A'$ en utilisant la formule du milieu à l'envers : $x_{A'} = 2x_O - x_A$ et $y_{A'} = 2y_O - y_A$.

### Corrigé

*Calcul de l'abscisse de $A'$.*

$$x_{A'} = 2 \times x_O - x_A = 2 \times 1 - 5 = 2 - 5 = -3$$

*Calcul de l'ordonnée de $A'$.*

$$y_{A'} = 2 \times y_O - y_A = 2 \times 2 - (-3) = 4 + 3 = 7$$

$$A'(-3\,;\,7)$$

*Contrôle.* $O$ doit être le milieu de $[AA']$ : $\dfrac{5 + (-3)}{2} = \dfrac{2}{2} = 1 = x_O$ et $\dfrac{-3 + 7}{2} = \dfrac{4}{2} = 2 = y_O$. Les deux coordonnées de $O$ sont retrouvées, le résultat est confirmé.

### Pourquoi les autres réponses sont fausses

- **b)** L'ordonnée est fausse : $2\times 2 - (-3) = 4 + 3 = 7$ ; tu as oublié que soustraire un nombre négatif revient à l'ajouter.
- **c)** Ce sont les coordonnées du vecteur $\overrightarrow{AO}$ (arrivée moins départ) ; elles ne donnent pas la position de $A'$.
- **d)** Ce sont les coordonnées du milieu de $[AO]$ ; or c'est $O$ qui doit être le milieu de $[AA']$.


</details>

Avis : 

---

## 38. `cqc-reciproque-du-theoreme-de-thales-faible-1` (séries BEPC)

**Remarque du relecteur :** La justification c) omet de citer la position des points (E sur [AB], F sur [AC], même ordre), condition de la réciproque de Thalès ; acceptable car donnée dans l'énoncé.

**Énoncé :**

$ABC$ est un triangle. $E$ est un point du segment $[AB]$ tel que $AE = 3$ cm et $AB = 8$ cm. $F$ est un point du segment $[AC]$ tel que $AF = 6$ cm et $AC = 16$ cm.

Les droites $(EF)$ et $(BC)$ sont-elles parallèles ? Quelle est la conclusion correctement justifiée ?

- a) Non, car $\dfrac{3}{8}$ et $\dfrac{6}{16}$ ont des numérateurs et des dénominateurs différents
- b) Non, car $AE \neq AF$
- c) Oui, car $\dfrac{AE}{AB} = \dfrac{3}{8}$ et $\dfrac{AF}{AC} = \dfrac{6}{16} = \dfrac{3}{8}$
- d) On ne peut pas conclure, car la longueur $BC$ n'est pas donnée

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

La réciproque du théorème de Thalès : si $E$ appartient à $[AB]$, $F$ appartient à $[AC]$, et si $\dfrac{AE}{AB} = \dfrac{AF}{AC}$, alors les droites $(EF)$ et $(BC)$ sont parallèles. Les deux rapports doivent impérativement être formés à partir du même sommet, ici $A$.

### Corrigé

*Premier rapport.*

$$\frac{AE}{AB} = \frac{3}{8}$$

*Second rapport.*

$$\frac{AF}{AC} = \frac{6}{16} = \frac{6 \div 2}{16 \div 2} = \frac{3}{8}$$

*Comparaison.*

$$\frac{AE}{AB} = \frac{AF}{AC} = \frac{3}{8}$$

De plus, $E$ appartient à $[AB]$ et $F$ appartient à $[AC]$ : les points $A$, $E$, $B$ d'une part et $A$, $F$, $C$ d'autre part sont alignés dans le même ordre à partir de $A$.

D'après la réciproque du théorème de Thalès, les droites $(EF)$ et $(BC)$ sont **parallèles**.

### Pourquoi les autres réponses sont fausses

- **a)** Deux fractions peuvent avoir des écritures différentes et être égales : $\dfrac{6}{16}$ se simplifie par $2$ en $\dfrac{3}{8}$.
- **b)** On ne compare pas des longueurs directement : ce sont les rapports $\dfrac{AE}{AB}$ et $\dfrac{AF}{AC}$ qui doivent être égaux.
- **d)** La réciproque du théorème de Thalès n'utilise pas $BC$ : il suffit de comparer les rapports sur les côtés $[AB]$ et $[AC]$.


</details>

Avis : 

---

## 39. `cqc-reduction-faible-1` (séries BEPC)

**Énoncé :**

Une pyramide de volume $V = 250\ \text{cm}^{3}$ est réduite dans le rapport $k = \dfrac{2}{5}$. Quel est le volume $v$ de la pyramide réduite ?

- a) $16\ \text{cm}^{3}$
- b) $100\ \text{cm}^{3}$
- c) $40\ \text{cm}^{3}$
- d) $12\ \text{cm}^{3}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans une réduction de rapport $k$, le volume du solide réduit s'obtient en multipliant le volume initial par $k^{3}$ : $v = k^{3}\times V$.

### Corrigé

*Calcul de $k^{3}$.*

$$k^{3} = \left(\frac{2}{5}\right)^{3} = \frac{2^{3}}{5^{3}} = \frac{8}{125}$$

*Volume réduit.*

$$v = \frac{8}{125}\times 250 = \frac{8\times 250}{125} = \frac{2\,000}{125}$$

$$v = 16\ \text{cm}^{3}$$

Le volume de la pyramide réduite est donc $v = 16\ \text{cm}^{3}$.

*Contrôle.* $250 \div 125 = 2$, puis $2\times 8 = 16$ : le calcul est cohérent.

### Conseil

Quand le rapport $k$ est une fraction, il est souvent plus simple de simplifier $\dfrac{V}{125}$ d'abord (ici $250\div 125 = 2$), puis de multiplier par le numérateur au cube : cela évite de manipuler de grands nombres.

### Pourquoi les autres réponses sont fausses

- **b)** Tu as multiplié le volume par $k$ seulement ; pour un volume, il faut multiplier par $k^{3}$.
- **c)** Tu as multiplié par $k^{2}=\dfrac{4}{25}$, le coefficient des aires, et non par $k^{3}$.
- **d)** Tu as calculé $k^{3}$ comme $\dfrac{2\times 3}{5^{3}}$ : élever $2$ au cube donne $8$, et non $2\times 3 = 6$.


</details>

Avis : 

---

## 40. `cqc-signe-d-une-expression-moyenne-2` (séries BEPC)

**Remarque du relecteur :** LIMITE : valeur absolue d'une expression avec radical, haut du programme de 3e.

**Énoncé :**

Quelle est l'écriture de $\left|5\sqrt{2} - 7\right|$ sans valeur absolue ? On ne demande aucune valeur approchée.

- a) $7 - 5\sqrt{2}$
- b) $5\sqrt{2} + 7$
- c) $5\sqrt{2} - 7$
- d) $2\sqrt{2}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Lever une valeur absolue exige de connaître au préalable le signe de l'expression qu'elle contient : si l'expression est positive, sa valeur absolue lui est égale ; si elle est négative, sa valeur absolue est son opposé. On détermine ce signe en comparant les carrés des deux termes, lorsqu'ils sont tous deux positifs.

### Corrigé

*Détermination du signe de $5\sqrt{2}-7$.* On compare $5\sqrt{2}$ et $7$, tous deux positifs, par leurs carrés :

$$(5\sqrt{2})^{2} = 25 \times 2 = 50 \qquad \qquad 7^{2} = 49$$

$50 > 49$, donc $5\sqrt{2} > 7$, c'est-à-dire

$$5\sqrt{2} - 7 > 0$$

*Levée de la valeur absolue.* L'expression $5\sqrt{2}-7$ étant positive, sa valeur absolue lui est égale :

$$\left|5\sqrt{2}-7\right| = 5\sqrt{2}-7$$

L'égalité $\left|5\sqrt{2}-7\right| = 7-5\sqrt{2}$ est donc **fausse** : $7-5\sqrt{2}$ est négatif et ne peut pas être égal à une valeur absolue, qui est toujours positive ou nulle.

*Contrôle numérique.* $5\sqrt{2}\approx7{,}071$, donc $5\sqrt{2}-7\approx0{,}071$ et $7-5\sqrt{2}\approx-0{,}071$ : seul le premier nombre, positif, peut être une valeur absolue.

### Pourquoi les autres réponses sont fausses

- **a)** C'est l'opposé de la bonne réponse : on a changé le signe alors que $5\sqrt{2}-7$ est déjà positif ($50>49$) ; $7-5\sqrt{2}$ est négatif et ne peut pas être une valeur absolue.
- **b)** La valeur absolue ne change pas un signe $-$ en signe $+$ au milieu de l'expression : elle laisse l'expression telle quelle si elle est positive.
- **d)** $5\sqrt{2}$ et $7$ ne sont pas des termes semblables : on ne peut pas les regrouper comme $(5-7)\sqrt{2}$.


</details>

Avis : 

---

## 41. `cqc-sinus-elevee-1` (séries BEPC)

**Remarque du relecteur :** Le cosinus donné est inutile (distracteur classique, acceptable).

**Énoncé :**

Un mât vertical de voilier est maintenu par un hauban (câble tendu) de $5$ m de longueur, fixé au sommet du mât et ancré sur le pont. Le hauban fait un angle de $65^\circ$ avec le pont, supposé horizontal. On donne $\sin 65^\circ \approx 0{,}906$ et $\cos 65^\circ \approx 0{,}423$.

Quelle est la hauteur du mât, arrondie au centième de mètre ?

- a) $2{,}12$ m
- b) $4{,}53$ m
- c) $5{,}52$ m
- d) $11{,}82$ m

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Le mât, le pont et le hauban forment un triangle rectangle dont le hauban est l'hypoténuse. La hauteur du mât est le côté opposé à l'angle de $65^\circ$ : $\sin\alpha = \dfrac{\text{opposé}}{\text{hypoténuse}}$.

### Corrigé

Le triangle formé par le pied du mât, le sommet du mât et le point d'ancrage est rectangle au pied du mât. Le hauban, de longueur $5$ m, est l'hypoténuse.

Hauteur du mât (côté opposé à l'angle de $65^\circ$) :

$$h = 5 \times \sin 65^\circ = 5 \times 0{,}906$$

$$h \approx 4{,}53\ \text{m}$$

*Contrôle.* La distance du pied du mât au point d'ancrage est $d = 5 \times \cos 65^\circ \approx 2{,}115$ m, et $h^{2} + d^{2} \approx 20{,}52 + 4{,}47 \approx 24{,}99$, quasiment égal à $5^{2} = 25$ (l'écart vient des arrondis) : le résultat est cohérent.

### Pourquoi les autres réponses sont fausses

- **a)** Tu as utilisé le cosinus ($5\times 0{,}423$) : c'est la distance entre le pied du mât et l'ancrage, côté adjacent à l'angle.
- **c)** Tu as divisé $5$ par $0{,}906$ ; la hauteur est le côté opposé, on multiplie l'hypoténuse par le sinus (et la hauteur ne peut pas dépasser la longueur du hauban).
- **d)** Tu as divisé $5$ par $0{,}423$ en utilisant le cosinus ; la hauteur se calcule avec le sinus, par multiplication, et ne peut pas dépasser $5$ m.


</details>

Avis : 

---

## 42. `cqc-sinus-moyenne-2` (séries BEPC)

**Remarque du relecteur :** VOCABULAIRE : le contexte de la voile est décoratif et flou (quel angle ?), une formulation directe suffit.

**Énoncé :**

Un angle aigu $\theta$ est tel que $\cos \theta = 0{,}8$. Quelle est la valeur de $\sin \theta$ ?

- a) $0{,}2$
- b) $0{,}36$
- c) $0{,}6$
- d) $0{,}64$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour tout angle aigu, la relation fondamentale $\cos^{2}\theta + \sin^{2}\theta = 1$ permet de retrouver l'un des deux rapports à partir de l'autre, en n'oubliant pas qu'un sinus d'angle aigu est toujours positif.

### Corrigé

$$\cos^{2}\theta + \sin^{2}\theta = 1$$

$$\sin^{2}\theta = 1 - \cos^{2}\theta = 1 - 0{,}8^{2} = 1 - 0{,}64 = 0{,}36$$

$$\sin\theta = \sqrt{0{,}36} = 0{,}6$$

(on prend la racine positive car $\theta$ est un angle aigu, donc $\sin\theta > 0$)

*Contrôle.* $\cos^{2}\theta + \sin^{2}\theta = 0{,}64 + 0{,}36 = 1$.

### Pourquoi les autres réponses sont fausses

- **a)** Tu as calculé $1-0{,}8$ ; la relation porte sur les carrés : $\sin^{2}\theta = 1-\cos^{2}\theta$.
- **b)** C'est la valeur de $\sin^{2}\theta$ ; il faut encore prendre la racine carrée pour obtenir $\sin\theta$.
- **d)** C'est la valeur de $\cos^{2}\theta$ ; tu as calculé $0{,}8^{2}$ sans l'utiliser pour trouver $\sin\theta$.


</details>

Avis : 

---

## 43. `cqc-sinus-moyenne-3` (séries BEPC)

**Remarque du relecteur :** La donnée « sin 30° = 0,5 » est inutile au calcul ; préciser que les 2 m sont mesurés dans le sens de la pente.

**Énoncé :**

Un panneau solaire rectangulaire, dont la longueur de $2$ m est mesurée le long de la pente, est fixé sur un toit et incliné d'un angle $\alpha$ par rapport à l'horizontale, tel que $\sin \alpha = 0{,}5$. On sait que $\sin 30^\circ = 0{,}5$.

Quelle hauteur le bord supérieur du panneau atteint-il au-dessus du bord inférieur ?

- a) $4$ m
- b) $1$ m
- c) $2{,}5$ m
- d) $0{,}25$ m

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Les valeurs remarquables du sinus (pour $30^\circ$, $45^\circ$, $60^\circ$) sont à connaître par cœur. Une fois l'angle identifié, la hauteur atteinte par un côté incliné de longueur $L$ s'obtient par $h = L \times \sin \alpha$.

### Corrigé

$\sin \alpha = 0{,}5 = \sin 30^\circ$, donc $\alpha = 30^\circ$.

Le panneau, sa hauteur verticale et sa projection horizontale forment un triangle rectangle où le panneau (longueur $2$ m) est l'hypoténuse et la hauteur cherchée est le côté opposé à $\alpha$.

$$h = L \times \sin \alpha = 2 \times \sin 30^\circ = 2 \times 0{,}5$$

$$h = 1\ \text{m}$$

*Contrôle de vraisemblance.* La hauteur ($1$ m) est bien inférieure à la longueur du panneau ($2$ m), comme il se doit pour un côté opposé face à l'hypoténuse.

### Pourquoi les autres réponses sont fausses

- **a)** Tu as divisé $2$ par $0{,}5$ ; la hauteur se calcule en multipliant l'hypoténuse par le sinus, et elle ne peut pas dépasser la longueur du panneau.
- **c)** Tu as additionné $2$ et $0{,}5$ ; le sinus est un rapport, la hauteur se calcule par $2\times 0{,}5$.
- **d)** Tu as divisé $0{,}5$ par $2$ ; il faut multiplier la longueur du panneau par le sinus de l'angle.


</details>

Avis : 

---

## 44. `cqc-solide-compose-moyenne-0` (séries BEPC)

**Énoncé :**

Un artisan fabrique un socle de trophée sportif. La base du socle est un bloc rectangulaire plein de $12$ cm de longueur, $12$ cm de largeur et $4$ cm d'épaisseur. Sur le centre de la face supérieure de ce bloc repose, bien centrée et verticale, une colonne pleine à section circulaire, de rayon $3$ cm et de hauteur $15$ cm, sur laquelle sera fixée la coupe du trophée.

On prendra $\pi \approx 3{,}14$.

Quel est le volume total du socle, en cm³ ?

- a) $999{,}9$ cm³
- b) $2271{,}6$ cm³
- c) $717{,}3$ cm³
- d) $858{,}6$ cm³

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour un solide composé décrit uniquement par un texte, on repère d'abord les solides usuels qui le composent (forme de la base, section constante ou non), on choisit la formule de volume de chacun, puis on additionne les volumes puisque le solide est obtenu par assemblage.

### Corrigé

Le bloc rectangulaire plein est un **pavé droit** ; la colonne pleine à section circulaire est un **cylindre de révolution**. Le socle est la réunion des deux.

Volume du pavé droit :
$$V_{pave} = 12\times 12\times 4 = 576\ \text{cm}^3$$

Volume du cylindre :
$$V_{cyl} = \pi\times 3^2\times 15 = 3{,}14\times 9\times 15 = 423{,}9\ \text{cm}^3$$

Volume total :
$$V_{total} = 576+423{,}9 = 999{,}9\ \text{cm}^3$$

Le socle a donc un volume total de $999{,}9$ cm³.

### Pourquoi les autres réponses sont fausses

- **b)** Le diamètre ($6$ cm) a été utilisé à la place du rayon ($3$ cm) dans la formule du volume du cylindre.
- **c)** Le rayon n'a pas été élevé au carré dans le volume du cylindre ($\pi\times 3\times 15$ au lieu de $\pi\times 3^2\times 15$).
- **d)** L'aire latérale du cylindre ($2\pi r h$) a été utilisée à la place de son volume ($\pi r^2 h$).

</details>

Avis : 

---

## 45. `cqc-solides-semblables-moyenne-3` (séries BEPC)

**Remarque du relecteur :** LIMITE : effet d'une réduction sur les volumes (k^3) et racine cubique de 27/64, haut du programme de 3e.

**Énoncé :**

Un chocolatier utilise un moule conique, pointe vers le bas, de hauteur totale $20$ cm, pour fabriquer une décoration en chocolat. Il remplit le moule à ras bord de chocolat fondu, puis retire délicatement du chocolat par le haut jusqu'à ce qu'il n'en reste plus que $\dfrac{27}{64}$ du volume initial. Le chocolat restant occupe alors, au fond du moule, un volume ayant la forme d'un cône semblable au moule entier (même sommet, pointe en bas).

Quelle est la hauteur du chocolat restant, mesurée depuis la pointe du moule ?

- a) $8{,}4375$ cm
- b) $15$ cm
- c) $11{,}25$ cm
- d) $5$ cm

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Si le rapport entre deux volumes de solides semblables est connu, on retrouve le rapport de réduction des longueurs $k$ en cherchant le nombre dont le cube est ce rapport de volumes, puisque $V_{petit} = k^3 \times V_{grand}$. Ici, on repère les cubes $27 = 3^3$ et $64 = 4^3$.

### Corrigé

$k^3 = \dfrac{27}{64}$. Or $27 = 3^3$ et $64 = 4^3$, donc $k^3 = \left(\dfrac{3}{4}\right)^3$ et $k = \dfrac{3}{4}$.

Le cône de chocolat restant a même sommet (la pointe) que le moule entier, donc sa hauteur depuis la pointe est :

$h_{restant} = k \times h_{moule} = \dfrac{3}{4} \times 20 = 15$ cm

Le chocolat restant atteint une hauteur de **15 cm** depuis la pointe du moule.

### Pourquoi les autres réponses sont fausses

- **a)** La hauteur a été obtenue en multipliant par le rapport des volumes $\dfrac{27}{64}$ au lieu du rapport des longueurs $k$.
- **c)** Le rapport $\dfrac{9}{16}$ ($k^2$) a été utilisé à la place de $k$.
- **d)** On a calculé la hauteur de chocolat retirée ($20 \times (1-k)$) au lieu de la hauteur restante.

</details>

Avis : 

---

## 46. `cqc-symetrie-orthogonale-faible-1` (séries BEPC)

**Remarque du relecteur :** Le cercle et le rayon sont des données inutiles, mais elles servent de distracteur légitime.

**Énoncé :**

Un cercle $(C)$ a pour centre $O$ et pour rayon $4$ cm. Un point $M$ appartient à $(C)$ : on a donc $OM = 4$ cm. On considère la symétrie orthogonale d'axe la droite $(OM)$.

Quel est le symétrique du point $M$ par cette symétrie ?

- a) Le point diamétralement opposé à $M$ sur le cercle $(C)$
- b) Le centre $O$ du cercle
- c) Le point $M$ lui-même
- d) Un autre point du cercle $(C)$, distinct de $M$ et situé hors de la droite $(OM)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

La droite $(OM)$ passe par le centre $O$ du cercle : c'est donc un axe de symétrie de $(C)$. Une symétrie orthogonale laisse invariant tout point situé sur son axe : un tel point est son propre symétrique.

### Corrigé

Le point $M$ appartient à la droite $(OM)$, qui est précisément l'axe de la symétrie considérée. Un point situé sur l'axe d'une symétrie orthogonale est invariant : son image est lui-même.

Le symétrique de $M$ par cette symétrie est donc **$M$ lui-même**.

*Remarque.* Tous les points de la droite $(OM)$, y compris $O$ et le point diamétralement opposé à $M$ sur $(C)$, sont eux aussi invariants.

### Pourquoi les autres réponses sont fausses

- **a)** C'est l'image de $M$ par la symétrie centrale de centre $O$, pas par la symétrie orthogonale d'axe $(OM)$.
- **b)** On a confondu symétrique d'un point et milieu : $O$ est invariant lui aussi, mais il est différent de $M$ ($OM = 4$ cm).
- **d)** Ce point n'est pas sur l'axe : l'axe $(OM)$ contient $M$, qui reste donc à sa place.

</details>

Avis : 

---

## 47. `cqc-theoreme-des-milieux-faible-0` (séries BEPC)

**Énoncé :**

Dans un triangle $RST$, le point $M$ est le milieu du segment $[RS]$ et le point $N$ est le milieu du segment $[RT]$. On donne $ST = 7{,}4$ cm.

Quelle est la longueur $MN$ ?

- a) $3{,}7$ cm
- b) $14{,}8$ cm
- c) $7{,}4$ cm
- d) $1{,}85$ cm

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un triangle, si un point est le milieu d'un côté et qu'un second point est le milieu d'un deuxième côté, alors le segment qui les joint est parallèle au troisième côté et sa longueur est égale à la moitié de celle du troisième côté (théorème des milieux).

### Corrigé

Dans le triangle $RST$, $M$ est le milieu de $[RS]$ et $N$ est le milieu de $[RT]$. D'après le théorème des milieux, $(MN) \parallel (ST)$ et :
$$MN = \frac{ST}{2} = \frac{7{,}4}{2} = 3{,}7 \text{ cm}$$

La longueur $MN$ est donc égale à $3{,}7$ cm.

### Pourquoi les autres réponses sont fausses

- **b)** La longueur $ST$ a été doublée au lieu d'être divisée par $2$.
- **c)** On a pris $MN = ST$ : le segment qui joint les milieux est parallèle à $[ST]$ mais deux fois plus court.
- **d)** La longueur a été divisée par $4$ au lieu de $2$.

</details>

Avis : 

---

## 48. `cqc-trapeze-rectangle-elevee-0` (séries BEPC)

**Remarque du relecteur :** La construction du point T ne sert pas au calcul (donnée superflue mais non trompeuse).

**Énoncé :**

Un jardin a la forme d'un trapèze rectangle $UVWZ$, dont les côtés $[UV]$ et $[ZW]$ sont parallèles, avec des angles droits en $U$ et en $Z$. On sait que $UZ = 12$ m (la hauteur du trapèze), que la petite base $ZW = 20$ m, et que l'aire totale du jardin est de $354$ m². On abaisse la perpendiculaire à $(UV)$ issue du point $W$ ; elle coupe $(UV)$ en un point $T$.

Quelle est la longueur de la grande base $UV$ ?

- a) $29{,}5$ m
- b) $19$ m
- c) $39$ m
- d) $59$ m

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un trapèze rectangle, la perpendiculaire abaissée du sommet de la petite base sur la grande base le décompose en un rectangle et un triangle rectangle accolés. L'aire totale est la somme de ces deux aires : connaître l'aire totale et celle du rectangle donne l'aire du triangle, puis, avec la formule de l'aire du triangle, une longueur inconnue.

### Corrigé

Le quadrilatère $UTWZ$ a trois angles droits (en $U$, en $Z$ et en $T$) : c'est un **rectangle**, avec $UT = ZW = 20$ m et $TW = UZ = 12$ m.

$$\text{Aire}(UTWZ) = 20 \times 12 = 240 \text{ m}^2$$

$$\text{Aire}(TVW) = 354 - 240 = 114 \text{ m}^2$$

Le triangle $TVW$ est rectangle en $T$ : $\dfrac{TV \times TW}{2} = 114$, donc $TV \times 6 = 114$ et $TV = 19$ m.

$$UV = UT + TV = 20 + 19 = 39 \text{ m}$$

*Contrôle par la formule de l'aire du trapèze.*
$$\mathcal{A} = \frac{(39 + 20) \times 12}{2} = \frac{708}{2} = 354 \text{ m}^2$$

### Pourquoi les autres réponses sont fausses

- **a)** Dans l'aire du triangle, le facteur $\dfrac{1}{2}$ a été oublié ($TV = 114 \div 12 = 9{,}5$ m).
- **b)** On a donné la longueur $TV$ et oublié d'y ajouter $UT = 20$ m pour obtenir $UV$.
- **d)** C'est la somme des deux bases ($UV + ZW$, issue de la formule de l'aire) : on a oublié de retrancher $ZW = 20$ m.

</details>

Avis : 

---

## 49. `cqc-vecteur-directeur-faible-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : lien coefficient directeur / vecteur directeur, à vérifier selon le programme de 3e retenu.

**Énoncé :**

La droite $(D)$ a pour équation $y = 5x - 2$.

Quel est un vecteur directeur de $(D)$ ?

- a) $\vec{u}\,(5\,;\,1)$
- b) $\vec{u}\,(1\,;\,-2)$
- c) $\vec{u}\,(-5\,;\,1)$
- d) $\vec{u}\,(1\,;\,5)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une droite d'équation $y = ax + b$, le vecteur $\vec{u}\,(1\,;\,a)$ est un vecteur directeur de cette droite : en avançant de $1$ en abscisse, on avance de $a$ en ordonnée.

### Corrigé

Le coefficient directeur de $(D)$ est $a = 5$. Un vecteur directeur de $(D)$ est donc

$$\vec{u}\,(1\,;\,5)$$

*Vérification.* Le point $A(0\,;\,-2)$ appartient à $(D)$. Le point $B = A + \vec{u}$ a pour coordonnées $(1\,;\,3)$ et $5 \times 1 - 2 = 3$, donc $B$ appartient aussi à $(D)$.

### Pourquoi les autres réponses sont fausses

- **a)** Les deux coordonnées ont été permutées : le coefficient directeur $5$ est l'ordonnée du vecteur $(1\,;\,5)$, pas son abscisse.
- **b)** On a utilisé l'ordonnée à l'origine $-2$ à la place du coefficient directeur $5$.
- **c)** Ce vecteur dirige une droite de coefficient directeur $-\dfrac{1}{5}$, pas $5$.

</details>

Avis : 

---

## 50. `cqc-vecteur-directeur-moyenne-1` (séries BEPC)

**Remarque du relecteur :** LIMITE : vecteur directeur d'une droite, à vérifier selon le programme de 3e retenu.

**Énoncé :**

La droite $(D)$ a pour équation $x = 5$ (droite verticale, parallèle à l'axe des ordonnées).

Lequel de ces vecteurs est un vecteur directeur de $(D)$ ?

- a) $\vec{u}\,(3\,;\,0)$
- b) $\vec{u}\,(5\,;\,0)$
- c) $\vec{u}\,(0\,;\,3)$
- d) $\vec{u}\,(1\,;\,5)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Le coefficient directeur d'une droite d'équation $y = ax+b$ n'est défini que si la droite n'est pas verticale : le rapport de la variation des ordonnées par la variation des abscisses n'a pas de sens quand la variation des abscisses est nulle. Une droite verticale n'a donc pas de coefficient directeur, mais elle possède tout de même des vecteurs directeurs, que l'on obtient à partir des coordonnées de deux de ses points.

### Corrigé

Tous les points de $(D)$ ont pour abscisse $5$, quelle que soit leur ordonnée. Deux points de $(D)$ sont par exemple $P(5\,;\,0)$ et $Q(5\,;\,3)$ :

$$\vec{PQ}\,(5-5\,;\,3-0) = (0\,;\,3)$$

Un vecteur directeur de $(D)$ a donc une abscisse nulle et une ordonnée non nulle : $\vec{u}\,(0\,;\,3)$ convient.

*Vérification.* En partant de $P(5\,;\,0)$ et en ajoutant $\vec{u}$, on obtient le point $(5\,;\,3)$, qui appartient bien à $(D)$ (son abscisse est $5$).

### Pourquoi les autres réponses sont fausses

- **a)** Ce vecteur est horizontal : il dirige une droite parallèle à l'axe des abscisses, d'équation du type $y = k$.
- **b)** On a repris le nombre $5$ de l'équation comme abscisse, mais ce vecteur est horizontal, donc il ne dirige pas une droite verticale.
- **d)** Ce vecteur a un coefficient directeur égal à $5$ : il dirige une droite oblique, pas la droite verticale $x = 5$.

</details>

Avis : 

---

## 51. `cqc-volume-d-un-cylindre-faible-0` (séries BEPC)

**Remarque du relecteur :** « arrondie au centième » superflu : avec π=3,14 la valeur est exacte au centième.

**Énoncé :**

Une boîte de conserve a la forme d'un cylindre de révolution. Son rayon de base mesure $R = 4$ cm et sa hauteur mesure $h = 11$ cm.

Quelle est la valeur approchée de son volume, en cm³, ? (On prendra $\pi \approx 3{,}14$.)

- a) $552{,}64$ cm³
- b) $138{,}16$ cm³
- c) $276{,}32$ cm³
- d) $184{,}21$ cm³

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Le volume d'un cylindre de révolution de rayon de base $R$ et de hauteur $h$ se calcule par la formule $V = \pi R^2 h$ : on multiplie l'aire du disque de base, $\pi R^2$, par la hauteur $h$.

### Corrigé

$$V = \pi R^2 h = \pi\times 4^2\times 11 = \pi\times 16\times 11 = 176\pi$$

Le volume de la boîte de conserve est donc $176\pi$ cm³.

Avec $\pi \approx 3{,}14$ :
$$V \approx 176\times 3{,}14 = 552{,}64$$

Le volume approché de la boîte de conserve est donc environ $552{,}64$ cm³.

### Pourquoi les autres réponses sont fausses

- **b)** On a multiplié par $R = 4$ au lieu de $R^2 = 16$ : le rayon n'a pas été élevé au carré.
- **c)** On a calculé $R^2$ comme $2R = 8$ au lieu de $4\times 4 = 16$.
- **d)** On a divisé par $3$, ce qui est la formule du volume d'une pyramide ou d'un cône, pas celle d'un cylindre.

</details>

Avis : 

---

## 52. `cqc-volume-d-un-cylindre-moyenne-3` (séries BEPC)

**Énoncé :**

Une citerne cylindrique doit avoir un volume de $6{,}28$ m³. Son rayon de base est fixé à $1$ m.

Quelle doit être la hauteur de cette citerne, en mètres ? (On prendra $\pi \approx 3{,}14$.)

- a) $1$ m
- b) $6$ m
- c) $2$ m
- d) $19{,}72$ m

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand le volume $V$ et le rayon de base $R$ d'un cylindre sont connus, on retrouve la hauteur $h$ en isolant $h$ dans la formule $V = \pi R^2 h$, ce qui donne $h = \dfrac{V}{\pi R^2}$.

### Corrigé

Avec $V = 6{,}28$ m³ et $R = 1$ m, donc $R^2 = 1$ :

$$h = \frac{V}{\pi R^2} = \frac{6{,}28}{\pi\times 1} = \frac{6{,}28}{\pi}$$

Avec $\pi \approx 3{,}14$ :
$$h \approx \frac{6{,}28}{3{,}14} = 2$$

La citerne doit donc avoir une hauteur de $2$ m.

### Pourquoi les autres réponses sont fausses

- **a)** On a divisé par $2\pi R$ (périmètre du cercle de base) au lieu de $\pi R^2$ (aire du disque de base).
- **b)** On a multiplié par $3$ avant de diviser, comme dans la formule d'un volume de pyramide ou de cône, qui ne s'applique pas à un cylindre.
- **d)** On a multiplié le volume par $\pi$ au lieu de le diviser.

</details>

Avis : 

---

## 53. `cqc-equation-reduite-elevee-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : droites données sous la forme ax − y + c = 0 avec paramètre m ; l'élève de 3e doit d'abord se ramener à y = ax + b.

**Énoncé :**

On considère la droite $(D)$ d'équation $5x - y + 1 = 0$ et la droite $(D_m)$ d'équation $mx - y + 7 = 0$, où $m$ est un nombre réel.

Pour quelle valeur de $m$ les droites $(D)$ et $(D_m)$ sont-elles parallèles ?

- a) $m = -5$
- b) $m = \dfrac{1}{5}$
- c) $m = 7$
- d) $m = 5$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour déterminer une équation réduite contenant un paramètre, on isole $y$ comme dans le cas général : le coefficient directeur s'exprime alors en fonction du paramètre. La condition de parallélisme entre deux droites (coefficients directeurs égaux) devient une équation vérifiée par ce paramètre.

### Corrigé

*Équation réduite de $(D)$.*

$$5x - y + 1 = 0 \quad \Longleftrightarrow \quad y = 5x + 1$$

Le coefficient directeur de $(D)$ est $5$.

*Équation réduite de $(D_m)$.*

$$mx - y + 7 = 0 \quad \Longleftrightarrow \quad y = mx + 7$$

Le coefficient directeur de $(D_m)$ est $m$.

*Condition de parallélisme.* $(D)$ et $(D_m)$ sont parallèles lorsque leurs coefficients directeurs sont égaux :

$$m = 5$$

Pour $m=5$, l'équation réduite de $(D_m)$ devient $y = 5x + 7$. Son ordonnée à l'origine est $7$, alors que celle de $(D)$ est $1$ : les deux droites sont parallèles mais distinctes.

*Conclusion.* $m = 5$.

### Pourquoi les autres réponses sont fausses

- **a)** Une erreur de signe a été faite en isolant $y$ : on a écrit $y = -5x - 1$, alors que $5x - y + 1 = 0$ donne $y = 5x + 1$.
- **b)** On a pris l'inverse du coefficient directeur de $(D)$ ; deux droites parallèles ont des coefficients directeurs égaux, non inverses.
- **c)** On a repris l'ordonnée à l'origine $7$ de $(D_m)$ au lieu de comparer les coefficients directeurs.

</details>

Avis : 

---

## 54. `cqc-equation-reduite-faible-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : équations de droites données sous la forme ax+by+c = 0 ; à vérifier que cette écriture figure dans le manuel de 3e utilisé (sinon donner directement y = ax+b).

**Énoncé :**

On considère les droites $(D_1)$ et $(D_2)$ d'équations respectives $3x - y + 5 = 0$ et $3x - y - 2 = 0$.

Laquelle de ces affirmations est exacte ?

- a) $(D_1) : y = 3x + 5$ et $(D_2) : y = 3x - 2$ ; les deux droites sont parallèles.
- b) $(D_1) : y = 3x + 5$ et $(D_2) : y = 3x - 2$ ; les deux droites ne sont pas parallèles.
- c) $(D_1) : y = -3x - 5$ et $(D_2) : y = -3x + 2$ ; les deux droites sont parallèles.
- d) $(D_1) : y = 3x + 5$ et $(D_2) : y = -3x - 2$ ; les deux droites ne sont pas parallèles.

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

L'équation réduite d'une droite non parallèle à l'axe des ordonnées s'écrit sous la forme $y = ax + b$, où $a$ est le coefficient directeur. On l'obtient à partir d'une équation de la forme $ax + by + c = 0$ en isolant $y$. Deux droites sont parallèles si et seulement si elles ont le même coefficient directeur.

### Corrigé

*Équation réduite de $(D_1)$.*

$$3x - y + 5 = 0 \quad \Longleftrightarrow \quad y = 3x + 5$$

$$a_1 = 3$$

*Équation réduite de $(D_2)$.*

$$3x - y - 2 = 0 \quad \Longleftrightarrow \quad y = 3x - 2$$

$$a_2 = 3$$

*Conclusion.*

$$a_1 = a_2 = 3$$

Les droites $(D_1)$ et $(D_2)$ ont le même coefficient directeur : elles sont donc **parallèles**. Elles sont de plus distinctes, puisque leurs ordonnées à l'origine diffèrent ($5$ et $-2$).

### Pourquoi les autres réponses sont fausses

- **b)** Les équations réduites sont justes, mais la conclusion est fausse : les ordonnées à l'origine différentes n'empêchent pas le parallélisme, seuls comptent les coefficients directeurs, ici égaux.
- **c)** Le signe des coefficients est faux : en passant $3x$ de l'autre côté il reste $-y = -3x - 5$, d'où $y = 3x + 5$, pas $-3x - 5$.
- **d)** Le coefficient directeur de $(D_2)$ est faux : $3x - y - 2 = 0$ donne $y = 3x - 2$, et non $y = -3x - 2$.

</details>

Avis : 

---

## 55. `cqc-equation-reduite-moyenne-0` (séries BEPC)

**Remarque du relecteur :** LIMITE : équations sous la forme ax + by + c = 0, à ramener à y = ax + b.

**Énoncé :**

On donne trois droites : $(D_1) : 4x - 2y + 6 = 0$ ; $(D_2) : x - 2y + 8 = 0$ ; $(D_3) : 2x - y - 3 = 0$.

Lesquelles de ces droites sont parallèles entre elles ?

- a) $(D_1)$ et $(D_2)$ seulement
- b) $(D_1)$ et $(D_3)$ seulement
- c) $(D_2)$ et $(D_3)$ seulement
- d) aucune de ces droites n'est parallèle à une autre

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

L'équation réduite d'une droite s'obtient en isolant $y$, ce qui fait apparaître son coefficient directeur $a$. Deux droites sont parallèles si et seulement si elles ont le même coefficient directeur ; pour comparer plusieurs droites entre elles, on réduit donc chacune d'elles avant de comparer les coefficients obtenus deux à deux.

### Corrigé

*Équation réduite de $(D_1)$.*

$$4x - 2y + 6 = 0 \quad \Longleftrightarrow \quad -2y = -4x - 6 \quad \Longleftrightarrow \quad y = 2x + 3$$

$$a_1 = 2$$

*Équation réduite de $(D_2)$.*

$$x - 2y + 8 = 0 \quad \Longleftrightarrow \quad -2y = -x - 8 \quad \Longleftrightarrow \quad y = \frac{1}{2}x + 4$$

$$a_2 = \frac{1}{2}$$

*Équation réduite de $(D_3)$.*

$$2x - y - 3 = 0 \quad \Longleftrightarrow \quad -y = -2x + 3 \quad \Longleftrightarrow \quad y = 2x - 3$$

$$a_3 = 2$$

*Comparaison des coefficients directeurs.* $a_1 = a_3 = 2$, tandis que $a_2 = \dfrac{1}{2}$ est différent des deux autres.

*Conclusion.* Les droites $(D_1)$ et $(D_3)$ ont le même coefficient directeur : elles sont **parallèles entre elles** (et distinctes, puisque leurs ordonnées à l'origine diffèrent : $3$ et $-3$). La droite $(D_2)$, de coefficient directeur différent, n'est parallèle à aucune des deux autres.

### Pourquoi les autres réponses sont fausses

- **a)** Ces deux droites ont le même coefficient de $y$ ($-2$), mais ce sont les coefficients directeurs $2$ et $\dfrac{1}{2}$ qu'il faut comparer.
- **c)** On a mal isolé $y$ dans $(D_2)$ : $y = \dfrac{1}{2}x + 4$ a pour coefficient directeur $\dfrac{1}{2}$, pas $2$.
- **d)** Les équations n'ont pas été réduites : en isolant $y$, $(D_1)$ et $(D_3)$ ont toutes deux pour coefficient directeur $2$.

</details>

Avis : 

---

