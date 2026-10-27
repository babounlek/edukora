# Echantillon pour relecture par un enseignant de maths (B1, vague 3)

Date : 2026-10-27. Questions de la vague 3 (150 en ligne) ou une methode a ete remplacee, une donnee ajoutee ou une formulation est discutable. Les 150 ont ete resolues a l'aveugle par un relecteur independant (150 accords sur 150) ; ce document sert a juger ce qu'un relecteur modele ne juge pas : le niveau 3e / BEPC, le realisme des distracteurs et les conventions d'enseignement.

Pour chaque question : **OK**, **a corriger** (dire quoi), ou **a retirer**.

## 1. `cqc-rectangle-moyenne-0`

**A regarder :** La source concluait 'rectangle' ; le quadrilatere est en fait un carre (cotes egaux, diagonales perpendiculaires). La question demande maintenant la nature exacte, cle 'carre'.

**Enonce :**

Dans un repère orthonormé, $ABCD$ est un parallélogramme de centre $O(3\,;2)$, avec $A(0\,;0)$ et $B(5\,;-1)$. Quelle est la nature exacte du quadrilatère $ABCD$ ?

- a) Un rectangle qui n'est pas un carré
- b) Un carré
- c) Un losange qui n'est pas un carré
- d) Un parallélogramme qui n'est ni un rectangle ni un losange

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Le symétrique d'un point $M$ par rapport à un point $O$ a pour coordonnées $(2x_O - x_M\,;\,2y_O - y_M)$. Un parallélogramme dont les diagonales ont la même longueur est un rectangle ; un rectangle dont deux côtés consécutifs sont égaux est un carré.

### Corrigé

*Coordonnées de $C$ et de $D$.* $O$ est le milieu de $[AC]$ et de $[BD]$ :

$$C(2 \times 3 - 0\,;\,2 \times 2 - 0) = (6\,;\,4)$$

$$D(2 \times 3 - 5\,;\,2 \times 2 - (-1)) = (1\,;\,5)$$

*Longueurs des diagonales.*

$$AC = \sqrt{(6-0)^2 + (4-0)^2} = \sqrt{36+16} = \sqrt{52} = 2\sqrt{13}$$

$$BD = \sqrt{(1-5)^2 + (5-(-1))^2} = \sqrt{16+36} = \sqrt{52} = 2\sqrt{13}$$

Le parallélogramme $ABCD$ a des diagonales de même longueur : c'est un **rectangle**.

*Deux côtés consécutifs.*

$$AB = \sqrt{(5-0)^2 + (-1-0)^2} = \sqrt{25+1} = \sqrt{26}$$

$$AD = \sqrt{(1-0)^2 + (5-0)^2} = \sqrt{1+25} = \sqrt{26}$$

$AB = AD$ : le rectangle $ABCD$ a deux côtés consécutifs égaux. $ABCD$ est donc un **carré**.

### Pourquoi les autres réponses sont fausses

- **a)** Un rectangle qui n'est pas un carré : on s'est arrêté aux diagonales égales sans comparer deux côtés consécutifs, qui sont égaux ici.
- **c)** Un losange qui n'est pas un carré : $AB = AD$ fait bien un losange, mais les diagonales de même longueur en font aussi un rectangle, donc un carré.
- **d)** Un parallélogramme quelconque : on s'est contenté du centre commun des diagonales sans calculer leurs longueurs.

</details>

Avis : 

---

## 2. `cqc-quadrilatere-moyenne-2`

**A regarder :** 'Montrer que c'est un losange' devient 'nature precise ?' ; cle : losange qui n'est pas un carre (diagonales ajoutees au corrige).

**Enonce :**

On donne les points $V(0\,;\,0)$, $W(3\,;\,4)$, $X(8\,;\,4)$ et $Y(5\,;\,0)$.

Quelle est la nature précise du quadrilatère $VWXY$ ?

- a) Un losange qui n'est pas un carré
- b) Un carré
- c) Un rectangle qui n'est pas un carré
- d) Un parallélogramme qui n'est ni un rectangle ni un losange

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Un quadrilatère non croisé dont les quatre côtés sont de même longueur est un losange. Dans un repère, chaque longueur se calcule par $MN = \sqrt{(x_N-x_M)^2+(y_N-y_M)^2}$.

### Corrigé

*Côté $VW$.*

$$VW = \sqrt{(3-0)^2+(4-0)^2} = \sqrt{9+16} = \sqrt{25} = 5$$

*Côté $WX$.*

$$WX = \sqrt{(8-3)^2+(4-4)^2} = \sqrt{25} = 5$$

*Côté $XY$.*

$$XY = \sqrt{(5-8)^2+(0-4)^2} = \sqrt{9+16} = \sqrt{25} = 5$$

*Côté $YV$.*

$$YV = \sqrt{(0-5)^2+(0-0)^2} = \sqrt{25} = 5$$

Les quatre côtés valent $5$ : le quadrilatère $VWXY$ est un **losange**.

*Est-ce un carré ?* Un losange est un carré si et seulement si ses diagonales ont la même longueur. Or :

$$VX = \sqrt{(8-0)^2+(4-0)^2} = \sqrt{80} \quad\text{et}\quad WY = \sqrt{(5-3)^2+(0-4)^2} = \sqrt{20}$$

$VX \neq WY$ : le losange n'est pas un carré.

*Conclusion.* $VWXY$ est un **losange qui n'est pas un carré**.

### Pourquoi les autres réponses sont fausses

- **b)** On a conclu au carré dès l'égalité des quatre côtés, sans vérifier les diagonales : $\sqrt{80} \neq \sqrt{20}$.
- **c)** Un rectangle a des diagonales de même longueur, ce qui n'est pas le cas ici.
- **d)** On s'est arrêté au parallélogramme (par exemple $\overrightarrow{VW} = \overrightarrow{YX}$) sans remarquer que ses côtés consécutifs sont égaux.

</details>

Avis : 

---

## 3. `cqc-quadrilatere-elevee-1`

**A regarder :** 'Montrer que c'est un carre' devient 'nature precise ?' avec des choix exclusifs.

**Enonce :**

On donne les points $A(1\,;\,1)$, $B(4\,;\,2)$, $C(3\,;\,5)$ et $D(0\,;\,4)$.

Quelle est la nature précise du quadrilatère $ABCD$ ?

- a) Un parallélogramme qui n'est ni un rectangle ni un losange
- b) Un rectangle qui n'est pas un carré
- c) Un losange qui n'est pas un carré
- d) Un carré

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Un quadrilatère dont les diagonales se coupent en leur milieu est un parallélogramme. Si ses diagonales ont de plus la même longueur, c'est un rectangle ; si en outre ses côtés consécutifs sont égaux, c'est un carré.

### Corrigé

**1. Les diagonales se coupent en leur milieu.**

*Milieu de $[AC]$.* $$\left( \frac{1+3}{2} \,;\, \frac{1+5}{2} \right) = (2\,;\,3)$$

*Milieu de $[BD]$.* $$\left( \frac{4+0}{2} \,;\, \frac{2+4}{2} \right) = (2\,;\,3)$$

Les diagonales ont le même milieu $(2\,;\,3)$ : $ABCD$ est un **parallélogramme**.

**2. Les diagonales ont la même longueur.**

$$AC = \sqrt{(3-1)^2+(5-1)^2} = \sqrt{4+16} = \sqrt{20} = 2\sqrt{5}$$

$$BD = \sqrt{(0-4)^2+(4-2)^2} = \sqrt{16+4} = \sqrt{20} = 2\sqrt{5}$$

$AC = BD$ : le parallélogramme est aussi un **rectangle**.

**3. Deux côtés consécutifs sont égaux.**

$$AB = \sqrt{(4-1)^2+(2-1)^2} = \sqrt{9+1} = \sqrt{10}$$

$$BC = \sqrt{(3-4)^2+(5-2)^2} = \sqrt{1+9} = \sqrt{10}$$

$AB = BC$ : le rectangle a deux côtés consécutifs égaux, c'est donc aussi un **carré**.

**Conclusion.** Le quadrilatère $ABCD$ est un carré de côté $\sqrt{10}$.

*Contrôle.* La relation diagonale $=$ côté $\times \sqrt{2}$ se vérifie : $\sqrt{10} \times \sqrt{2} = \sqrt{20} = 2\sqrt{5}$.

### Pourquoi les autres réponses sont fausses

- **a)** On s'est arrêté au milieu commun des diagonales : $ABCD$ est bien un parallélogramme, mais ses diagonales sont égales et ses côtés consécutifs aussi, il est donc rectangle et losange.
- **b)** On a vérifié les diagonales égales sans comparer deux côtés consécutifs : or $AB=BC=\sqrt{10}$, le rectangle est un carré.
- **c)** On a vérifié l'égalité des côtés sans comparer les diagonales : or $AC=BD=2\sqrt{5}$, le losange est un carré.

</details>

Avis : 

---

## 4. `cqc-quadrilatere-faible-1`

**A regarder :** Question changee : on cherche D tel que ABCD soit un parallelogramme (reponse (0 ; -3)), au lieu de verifier une propriete.

**Enonce :**

On donne les points $A(-3\,;\,1)$, $B(2\,;\,4)$ et $C(5\,;\,0)$.

Quelles sont les coordonnées du point $D$ tel que le quadrilatère $ABCD$ soit un parallélogramme ?

- a) $(10\,;\,3)$
- b) $(0\,;\,-3)$
- c) $(0\,;\,3)$
- d) $(-6\,;\,5)$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Un quadrilatère $ABCD$ est un parallélogramme lorsque $\overrightarrow{AB} = \overrightarrow{DC}$, c'est-à-dire lorsque deux côtés opposés sont parallèles et de même longueur. On écrit cette égalité de vecteurs coordonnée par coordonnée pour trouver le point inconnu.

### Corrigé

*Coordonnées de $\overrightarrow{AB}$.*

$$\overrightarrow{AB}\begin{pmatrix} 2-(-3) \\ 4-1 \end{pmatrix} = \begin{pmatrix} 5 \\ 3 \end{pmatrix}$$

*Coordonnées de $\overrightarrow{DC}$, avec $D(x\,;\,y)$.*

$$\overrightarrow{DC}\begin{pmatrix} 5-x \\ 0-y \end{pmatrix}$$

*Égalité $\overrightarrow{AB} = \overrightarrow{DC}$.*

$$5-x = 5 \quad\text{et}\quad -y = 3, \quad\text{donc}\quad x = 0 \quad\text{et}\quad y = -3$$

*Conclusion.* Le point cherché est $D(0\,;\,-3)$.

*Contrôle.* $\overrightarrow{DC}\begin{pmatrix} 5-0 \\ 0-(-3) \end{pmatrix} = \begin{pmatrix} 5 \\ 3 \end{pmatrix} = \overrightarrow{AB}$ : les côtés $[AB]$ et $[DC]$ sont parallèles et de même longueur, $ABCD$ est bien un **parallélogramme**.

### Pourquoi les autres réponses sont fausses

- **a)** $(10\,;\,3)$ : on a écrit $\overrightarrow{AB} = \overrightarrow{CD}$, ce qui donne le parallélogramme $ABDC$ et non $ABCD$.
- **c)** $(0\,;\,3)$ : erreur de signe en résolvant $-y = 3$.
- **d)** $(-6\,;\,5)$ : on a écrit $\overrightarrow{AD} = \overrightarrow{CB}$, ce qui donne le parallélogramme $ADBC$ et non $ABCD$.

</details>

Avis : 

---

## 5. `cqc-quadrilatere-moyenne-3`

**A regarder :** Seule la valeur approchee au dixieme est demandee (18,0 cm) ; l'unite a ete ajoutee a l'enonce.

**Enonce :**

On donne le quadrilatère $ABCD$ avec $A(-2\,;\,-1)$, $B(3\,;\,2)$, $C(1\,;\,5)$ et $D(-3\,;\,3)$, l'unité de longueur étant le centimètre.

Quelle est la valeur approchée au dixième du périmètre du quadrilatère $ABCD$ ?

- a) $24$ cm
- b) environ $9{,}2$ cm
- c) environ $13{,}6$ cm
- d) environ $18{,}0$ cm

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Le périmètre d'un quadrilatère est la somme des longueurs de ses quatre côtés. Dans un repère, chaque longueur se calcule par la formule de la distance $MN = \sqrt{(x_N-x_M)^2+(y_N-y_M)^2}$.

### Corrigé

*Côté $AB$.*

$$AB = \sqrt{(3-(-2))^2+(2-(-1))^2} = \sqrt{25+9} = \sqrt{34} \approx 5{,}83$$

*Côté $BC$.*

$$BC = \sqrt{(1-3)^2+(5-2)^2} = \sqrt{4+9} = \sqrt{13} \approx 3{,}61$$

*Côté $CD$.*

$$CD = \sqrt{(-3-1)^2+(3-5)^2} = \sqrt{16+4} = \sqrt{20} = 2\sqrt{5} \approx 4{,}47$$

*Côté $DA$.*

$$DA = \sqrt{(-2-(-3))^2+(-1-3)^2} = \sqrt{1+16} = \sqrt{17} \approx 4{,}12$$

*Périmètre.*

$$\mathcal{P} = AB + BC + CD + DA = \sqrt{34} + \sqrt{13} + 2\sqrt{5} + \sqrt{17}$$

$$\mathcal{P} \approx 5{,}83 + 3{,}61 + 4{,}47 + 4{,}12 \approx 18{,}0$$

Le périmètre de $ABCD$ vaut $\sqrt{34} + \sqrt{13} + 2\sqrt{5} + \sqrt{17}$ cm, soit environ **$18{,}0$ cm**.

### Pourquoi les autres réponses sont fausses

- **a)** $24$ cm : on a additionné les écarts de coordonnées ($5+3$, $2+3$, $4+2$, $1+4$) sans appliquer la formule de la distance.
- **b)** environ $9{,}2$ cm : on a pris une seule racine, $\sqrt{34+13+20+17}=\sqrt{84}$, au lieu de la somme des quatre racines ; or $\sqrt{a}+\sqrt{b}\neq\sqrt{a+b}$.
- **c)** environ $13{,}6$ cm : erreur de signe dans $AB$, calculé avec $3-2$ et $2-1$ au lieu de $3-(-2)$ et $2-(-1)$, d'où $AB=\sqrt{2}$.

</details>

Avis : 

---

## 6. `cqc-symetrie-axiale-elevee-0`

**A regarder :** Donnee BC = 6 cm AJOUTEE par le generateur ; la question devient MM' = 2 cm (Thales).

**Enonce :**

$ABC$ est un triangle isocèle en $A$, avec $AB = AC = 9$ cm et $BC = 6$ cm. On note $(\Delta)$ la bissectrice de l'angle $\widehat{BAC}$. $M$ est le point du segment $[AB]$ tel que $AM = 3$ cm, et $M'$ est le symétrique de $M$ par rapport à $(\Delta)$.

Quelle est la longueur $MM'$ ?

- a) $3$ cm
- b) $4$ cm
- c) $2$ cm
- d) $6$ cm

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode
Dans un triangle isocèle, la bissectrice de l'angle au sommet est aussi la médiatrice de la base : elle est donc perpendiculaire à la base en son milieu, ce qui correspond exactement au critère de symétrie axiale. Une symétrie orthogonale fixe tout point de son axe et conserve les distances ; et si deux points pris sur deux droites issues d'un même point découpent des rapports de longueurs égaux, la droite qui les joint est parallèle à la troisième (réciproque du théorème de Thalès).

### Corrigé
$ABC$ est isocèle en $A$, donc la bissectrice $(\Delta)$ de l'angle $\widehat{BAC}$ est aussi la médiatrice de $[BC]$ : $B$ et $C$ sont symétriques par rapport à $(\Delta)$.

$A$ appartient à $(\Delta)$, donc $A$ est invariant. La symétrie envoie $B$ sur $C$ et fixe $A$, elle envoie donc le segment $[AB]$ sur le segment $[AC]$ : $M'$ appartient à $[AC]$ et $AM' = AM = 3$ cm.

On a $\dfrac{AM}{AB} = \dfrac{3}{9} = \dfrac{1}{3}$ et $\dfrac{AM'}{AC} = \dfrac{3}{9} = \dfrac{1}{3}$. D'après la réciproque du théorème de Thalès, $(MM')$ est parallèle à $(BC)$. Le théorème de Thalès donne alors :
$$\dfrac{MM'}{BC} = \dfrac{AM}{AB} = \dfrac{1}{3}, \quad \text{donc} \quad MM' = \dfrac{6}{3} = 2 \text{ cm}.$$

### Pourquoi les autres réponses sont fausses
- **a)** $3$ cm : on a utilisé le rapport $\dfrac{AM}{MB} = \dfrac{3}{6}$ au lieu de $\dfrac{AM}{AB}$.
- **b)** $4$ cm : on a utilisé le rapport $\dfrac{MB}{AB} = \dfrac{2}{3}$, qui correspond à la distance depuis $B$, pas depuis $A$.
- **d)** $6$ cm : on a cru que $MM'$ était égal à $BC$, alors que $[MM']$ n'est pas l'image de $[BC]$ par la symétrie.

</details>

Avis : 

---

## 7. `cqc-symetrie-axiale-faible-1`

**A regarder :** Donnee MP = 6 cm AJOUTEE ; la question devient MQ = 5 cm (symetrie puis Pythagore).

**Enonce :**

$MNPQ$ est un losange dont les diagonales $[MP]$ et $[NQ]$ se coupent en un point $O$. On rappelle que dans un losange, les diagonales sont perpendiculaires et se coupent en leur milieu commun. On donne $MP = 6$ cm et $NQ = 8$ cm.

Quelle est la longueur $MQ$ ?

- a) $10$ cm
- b) $7$ cm
- c) $4$ cm
- d) $5$ cm

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode
Deux points sont symétriques par rapport à une droite $(D)$ lorsque le segment qui les joint est perpendiculaire à $(D)$ et que son milieu appartient à $(D)$. Un point de l'axe est invariant, donc les distances entre ce point et deux points symétriques sont égales. Dans un triangle rectangle, on calcule l'hypoténuse avec le théorème de Pythagore.

### Corrigé
Les diagonales du losange sont perpendiculaires, donc $(NQ) \perp (MP)$, et $O$, milieu de $[NQ]$, appartient à $(MP)$ : $N$ et $Q$ sont symétriques par rapport à $(MP)$. Donc $ON = OQ = \dfrac{8}{2} = 4$ cm, et de même $OM = \dfrac{6}{2} = 3$ cm.

$M$ appartient à l'axe $(MP)$, donc $M$ est invariant ; la symétrie envoie $N$ sur $Q$ et conserve les distances, donc $MQ = MN$.

Le triangle $MOQ$ est rectangle en $O$. D'après le théorème de Pythagore :
$$MQ^2 = OM^2 + OQ^2 = 3^2 + 4^2 = 9 + 16 = 25, \quad \text{donc} \quad MQ = 5 \text{ cm}.$$

### Pourquoi les autres réponses sont fausses
- **a)** $10$ cm : on a appliqué Pythagore avec les diagonales entières ($6^2 + 8^2 = 100$) au lieu de leurs moitiés.
- **b)** $7$ cm : on a additionné $OM$ et $OQ$ au lieu d'appliquer le théorème de Pythagore.
- **c)** $4$ cm : on a confondu $MQ$ avec $OQ$, la demi-diagonale.

</details>

Avis : 

---

## 8. `cqc-symetrie-axiale-moyenne-0`

**A regarder :** Produit scalaire (hors programme) remplace par le produit des coefficients directeurs = -1 ; symetrique de A(2 ; 6) par rapport a y = x.

**Enonce :**

Le plan est muni d'un repère orthonormé $(O, I, J)$. On donne le point $A(2\,;\,6)$ et la droite $(\Delta)$ d'équation $y = x$.

Quelles sont les coordonnées du point $B$, symétrique de $A$ par rapport à $(\Delta)$ ?

- a) $(-2\,;\,-6)$
- b) $(6\,;\,2)$
- c) $(2\,;\,-6)$
- d) $(-2\,;\,6)$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode
Pour montrer que deux points sont symétriques par rapport à une droite $(D)$, on vérifie les deux conditions du critère : le segment qui les joint est perpendiculaire à $(D)$, et son milieu appartient à $(D)$. Deux droites de coefficients directeurs $a$ et $a'$ sont perpendiculaires lorsque $a \times a' = -1$. La droite d'équation $y = x$ a pour coefficient directeur $1$.

### Corrigé
On vérifie que $B(6\,;\,2)$ convient.

- Le milieu $K$ de $[AB]$ a pour coordonnées $\left(\dfrac{2+6}{2}\,;\,\dfrac{6+2}{2}\right) = (4\,;\,4)$. Comme $4 = 4$, $K$ vérifie $y = x$ : $K$ appartient à $(\Delta)$.
- Le coefficient directeur de $(AB)$ est $\dfrac{2-6}{6-2} = \dfrac{-4}{4} = -1$. Celui de $(\Delta)$ est $1$, et $(-1) \times 1 = -1$ : donc $(AB) \perp (\Delta)$.

Les deux conditions du critère sont réunies : le symétrique de $A$ par rapport à $(\Delta)$ est $B(6\,;\,2)$. On retient que la symétrie d'axe $y = x$ échange l'abscisse et l'ordonnée.

### Pourquoi les autres réponses sont fausses
- **a)** $(-2\,;\,-6)$ : c'est le symétrique de $A$ par rapport au point $O$ (symétrie centrale), pas par rapport à $(\Delta)$.
- **c)** $(2\,;\,-6)$ : c'est le symétrique de $A$ par rapport à l'axe des abscisses.
- **d)** $(-2\,;\,6)$ : c'est le symétrique de $A$ par rapport à l'axe des ordonnées.

</details>

Avis : 

---

## 9. `cqc-symetrie-axiale-moyenne-2`

**A regarder :** Question de synthese 'affirmation toujours vraie' (trapeze de bases 8 et 5 cm) : formulation et niveau a juger.

**Enonce :**

$ABCD$ est un trapèze tel que $(AB)$ soit parallèle à $(CD)$, avec $AB = 8$ cm et $CD = 5$ cm. On considère une symétrie orthogonale $s$ d'axe une droite $(\Delta)$ quelconque du plan, et on note $A'$, $B'$, $C'$, $D'$ les images respectives de $A$, $B$, $C$, $D$ par $s$.

Quelle affirmation est toujours vraie, quel que soit l'axe $(\Delta)$ ?

- a) $A'B'C'D'$ est un trapèze isocèle de bases $8$ cm et $5$ cm
- b) $A'B'C'D'$ n'a aucun côté parallèle à un autre, car la symétrie ne conserve pas le parallélisme
- c) $A'B'C'D'$ est un trapèze avec $A'B' = 8$ cm et $C'D' = 5$ cm
- d) $A'B'C'D'$ est un trapèze dont le côté $(A'B')$ est parallèle à $(AB)$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode
Une symétrie orthogonale est une isométrie : elle conserve les distances. Elle conserve également le parallélisme : les images de deux droites parallèles sont deux droites parallèles. En revanche, l'image d'une droite n'est en général pas parallèle à cette droite.

### Corrigé
La symétrie conserve les distances, donc $A'B' = AB = 8$ cm et $C'D' = CD = 5$ cm.

$(AB)$ est parallèle à $(CD)$. La symétrie conservant le parallélisme, $(A'B')$ est parallèle à $(C'D')$.

$A'B'C'D'$ a donc deux côtés parallèles : c'est un trapèze de bases $A'B' = 8$ cm et $C'D' = 5$ cm.

### Pourquoi les autres réponses sont fausses
- **a)** Trapèze isocèle : rien n'indique que $ABCD$ est isocèle ; la symétrie conserve la forme de la figure, elle ne la rend pas isocèle.
- **b)** Pas de côtés parallèles : on a cru que la symétrie détruisait le parallélisme, alors qu'elle le conserve.
- **d)** $(A'B')$ parallèle à $(AB)$ : c'est vrai pour une translation, mais pas pour une symétrie d'axe quelconque (seulement si l'axe est parallèle ou perpendiculaire à $(AB)$).

</details>

Avis : 

---

## 10. `cqc-triangle-rectangle-isocele-moyenne-1`

**A regarder :** Demonstration devenue 'nature du triangle EFG' ; produit scalaire remplace par distances et reciproque de Pythagore.

**Enonce :**

Dans un repère orthonormé, on considère les points $E(1\,;4)$, $F(-2\,;1)$ et $G(4\,;1)$. Quelle est la nature du triangle $EFG$ ?

- a) isocèle en $E$ mais pas rectangle
- b) équilatéral
- c) rectangle et isocèle en $E$
- d) rectangle en $F$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Dans un repère orthonormé, la distance entre $A(x_A\,;y_A)$ et $B(x_B\,;y_B)$ vérifie $AB^2 = (x_B - x_A)^2 + (y_B - y_A)^2$. On compare les longueurs pour l'isocèle, puis on applique la réciproque du théorème de Pythagore pour l'angle droit.

### Corrigé

*Carrés des longueurs.*

$$EF^2 = (-2-1)^2 + (1-4)^2 = 9 + 9 = 18$$

$$EG^2 = (4-1)^2 + (1-4)^2 = 9 + 9 = 18$$

$$FG^2 = (4-(-2))^2 + (1-1)^2 = 36 + 0 = 36$$

*Isocèle.* $EF = EG = \sqrt{18} = 3\sqrt{2}$ : le triangle est isocèle en $E$.

*Rectangle.* Le plus long côté est $[FG]$ et

$$EF^2 + EG^2 = 18 + 18 = 36 = FG^2$$

D'après la réciproque du théorème de Pythagore, le triangle est rectangle en $E$.

*Conclusion.* Le triangle $EFG$ est **rectangle et isocèle en $E$**.

### Pourquoi les autres réponses sont fausses
- **a)** « Isocèle en $E$ mais pas rectangle » oublie de tester la réciproque de Pythagore, qui est pourtant vérifiée : $18 + 18 = 36$.
- **b)** « Équilatéral » est faux car $FG = 6$ alors que $EF = EG = 3\sqrt{2} \approx 4{,}24$.
- **d)** « Rectangle en $F$ » se trompe de sommet : l'angle droit est opposé au plus long côté $[FG]$, donc en $E$.

</details>

Avis : 

---

## 11. `cqc-reciproque-du-theoreme-de-pythagore-faible-2`

**A regarder :** 'Montrer que non rectangle' devient 'quelle justification est correcte ?' : les 4 choix concluent 'pas rectangle', seul le calcul differe.

**Enonce :**

Un triangle $MNP$ a pour côtés $MN = 5$ cm, $NP = 6$ cm et $MP = 7$ cm. Quelle justification permet de conclure correctement sur la nature de ce triangle ?

- a) $NP^2=36$ et $MN^2+MP^2=74$, donc le triangle n'est pas rectangle.
- b) $MP^2=49$ et $MN^2+NP^2=61$, donc le triangle n'est pas rectangle.
- c) $2\times7=14$ et $2\times5+2\times6=22$, donc le triangle n'est pas rectangle.
- d) $MP^2=49$ et $(MN+NP)^2=121$, donc le triangle n'est pas rectangle.

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

La réciproque du théorème de Pythagore sert aussi à prouver qu'un triangle n'est pas rectangle : on compare le carré du **plus grand** côté à la somme des carrés des deux autres ; s'ils sont différents, le triangle n'est pas rectangle.

### Corrigé

*Identification du plus grand côté.* Le plus grand est $[MP]$.

$$MP^{2} = 7^{2} = 49 \qquad MN^{2} + NP^{2} = 25 + 36 = 61$$

Ces deux nombres sont différents : $49 \neq 61$. D'après la réciproque du théorème de Pythagore, le triangle $MNP$ n'est **pas rectangle**.

### Pourquoi les autres réponses sont fausses
- **a)** On a pris $[NP]$ au lieu du plus grand côté : cette comparaison montre seulement que l'angle en $M$ n'est pas droit, elle ne suffit pas à conclure.
- **c)** On a confondu « carré » et « double » : $7^2$ n'est pas $2\times7$.
- **d)** On a élevé la somme au carré : $(MN+NP)^2$ n'est pas égal à $MN^2+NP^2$.

</details>

Avis : 

---

## 12. `cqc-reciproque-du-theoreme-de-pythagore-moyenne-3`

**A regarder :** Meme transformation : le bon choix doit tester le plus grand cote.

**Enonce :**

Un champ a la forme d'un triangle dont les côtés mesurent $30$ m, $40$ m et $41$ m. Le fermier veut savoir si ce champ possède un angle droit. Quel calcul lui permet de conclure correctement ?

- a) $41^2=1681$ et $(30+40)^2=4900$, donc pas d'angle droit.
- b) $2\times41=82$ et $2\times30+2\times40=140$, donc pas d'angle droit.
- c) $41^2=1681$ et $30^2+40^2=2500$, donc pas d'angle droit.
- d) $40^2=1600$ et $30^2+41^2=2581$, donc pas d'angle droit.

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Pour vérifier l'affirmation d'un angle droit à partir des trois côtés d'un triangle, on applique la réciproque du théorème de Pythagore : on compare le carré du **plus grand** côté à la somme des carrés des deux autres.

### Corrigé

*Identification du plus grand côté.* Le plus grand est $41$ m.

$$41^{2} = 1681 \qquad 30^{2} + 40^{2} = 900 + 1600 = 2500$$

$1681 \neq 2500$ : d'après la réciproque du théorème de Pythagore, ce triangle n'est **pas rectangle**, le champ ne possède pas d'angle droit.

### Piège à éviter
Ce triangle ressemble au triplet pythagoricien $(30\,;\,40\,;\,50)$, mais son troisième côté vaut ici $41$ et non $50$ : ce petit écart suffit à casser l'égalité. Il ne faut jamais se fier à une simple ressemblance avec un triplet connu, mais toujours vérifier par le calcul.

### Pourquoi les autres réponses sont fausses
- **a)** On a élevé la somme au carré : $(30+40)^2$ n'est pas égal à $30^2+40^2$.
- **b)** On a confondu « carré » et « double ».
- **d)** On a pris $40$ m au lieu du plus grand côté : cette comparaison montre seulement que l'angle opposé au côté de $40$ m n'est pas droit, elle ne suffit pas à conclure.

</details>

Avis : 

---

## 13. `cqc-rotation-faible-0`

**A regarder :** Formule en cos/sin remplacee par la regle du quart de tour (x ; y) -> (-y ; x). Coordonnees d'une rotation : au programme de 3e ?

**Enonce :**

Dans le plan muni d'un repère orthonormé $(O;I,J)$, on considère le point $A(4;-2)$. Soit $r$ la rotation de centre $O$ et d'angle $90°$ dans le sens direct (sens inverse des aiguilles d'une montre). Quelles sont les coordonnées du point $A'$, image de $A$ par $r$ ?

- a) $(-2;-4)$
- b) $(2;4)$
- c) $(-2;4)$
- d) $(-4;2)$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode
Par la rotation de centre $O$ et d'angle $90°$ dans le sens direct (quart de tour), l'image du point $M(x;y)$ est le point $M'(-y;x)$ : on échange les coordonnées et on change le signe de la nouvelle abscisse. On le contrôle ainsi : $OM'=OM$, les droites $(OM)$ et $(OM')$ sont perpendiculaires, et on tourne bien dans le sens inverse des aiguilles d'une montre. Une rotation conserve les longueurs.

### Corrigé
Pour $A(4;-2)$ : $x'=-(-2)=2$ et $y'=4$, donc $A'(2;4)$.

Vérification : $OA=\sqrt{4^2+(-2)^2}=\sqrt{20}$ et $OA'=\sqrt{2^2+4^2}=\sqrt{20}$, donc $OA'=OA$. De plus $4\times2+(-2)\times4=0$, ce qui traduit que $(OA)\perp(OA')$. Enfin, $A$ est sous l'axe des abscisses, à droite, et $A'$ est au-dessus, à droite : on a bien tourné d'un quart de tour dans le sens direct.

**Réponse : $A'(2;4)$.**

### Pourquoi les autres réponses sont fausses
- **a)** $(-2;-4)$ est l'image par le quart de tour dans le sens indirect (sens des aiguilles d'une montre), qui donne $(y;-x)$.
- **c)** $(-2;4)$ : on a échangé les coordonnées mais mal placé le changement de signe ; on a $OA'=OA$ mais $(OA)$ et $(OA')$ ne sont pas perpendiculaires.
- **d)** $(-4;2)$ est l'image par la symétrie de centre $O$ (rotation de $180°$), pas par un quart de tour.

</details>

Avis : 

---

## 14. `cqc-equation-cartesienne-elevee-0`

**A regarder :** Question oui/non remplacee par 'T(3 ; y) : quelle valeur de y rend R, S, T alignes ?' (9). Terme 'cartesienne' au programme ?

**Enonce :**

On donne les points $R(-2\,;\,-1)$, $S(1\,;\,5)$ et $T(3\,;\,y)$.

Pour quelle valeur de $y$ les points $R$, $S$ et $T$ sont-ils alignés ?

- a) $1$
- b) $7$
- c) $1{,}5$
- d) $9$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Trois points sont alignés lorsque le troisième appartient à la droite passant par les deux premiers. On détermine donc une équation de la droite $(RS)$, puis on cherche l'ordonnée du point de cette droite qui a pour abscisse $3$.

### Corrigé

*Coefficient directeur de $(RS)$.*
$$a = \frac{y_S - y_R}{x_S - x_R} = \frac{5 - (-1)}{1 - (-2)} = \frac{6}{3} = 2$$

*Ordonnée à l'origine.* L'équation s'écrit $y = 2x + b$, et $R(-2\,;\,-1)$ appartient à la droite :
$$-1 = 2 \times (-2) + b = -4 + b \quad \Longrightarrow \quad b = 3$$

$$y = 2x + 3 \qquad \text{ou encore} \qquad 2x - y + 3 = 0$$

Vérification avec $S$ : $2 \times 1 - 5 + 3 = 0$ ✔

*Point d'abscisse 3.* $T$ est aligné avec $R$ et $S$ si et seulement si $T$ appartient à $(RS)$, c'est-à-dire :
$$y = 2 \times 3 + 3 = 9$$

Contrôle : $2 \times 3 - 9 + 3 = 6 - 9 + 3 = 0$ ✔. Les points sont alignés pour **$y = 9$**.

### Pourquoi les autres réponses sont fausses

- **a)** $1$ : erreur de signe en calculant $b$ ($b = -1 - 4 = -5$ au lieu de $b = -1 + 4 = 3$), d'où $y = 2x - 5$.
- **b)** $7$ : on a ajouté le coefficient directeur une seule fois à l'ordonnée de $S$, alors que l'abscisse augmente de $2$ entre $S$ et $T$.
- **c)** $1{,}5$ : on a inversé le quotient ($\dfrac{\Delta x}{\Delta y} = \dfrac{1}{2}$ au lieu de $\dfrac{\Delta y}{\Delta x} = 2$).

</details>

Avis : 

---

## 15. `cqc-simplification-moyenne-2`

**A regarder :** Methode du discriminant (hors programme) remplacee par une factorisation par groupement.

**Enonce :**

Pour tout réel $x\neq -2$ et $x\neq2$, on considère l'expression rationnelle
$$K(x) = \dfrac{2x^2-3x-2}{x^2-4}$$
Quelle est l'écriture simplifiée de $K(x)$ ?

- a) $K(x) = \dfrac{2x-1}{x+2}$
- b) $K(x) = \dfrac{2x-1}{x-2}$
- c) $K(x) = \dfrac{x+1}{x+2}$
- d) $K(x) = \dfrac{2x+1}{x+2}$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Pour simplifier une fraction rationnelle, on factorise le numérateur et le dénominateur. Pour un numérateur comme $2x^2-3x-2$, on peut décomposer le terme en $x$ ($-3x = -4x + x$) afin de faire apparaître un facteur commun par groupement ; on repère ensuite le facteur commun avec le dénominateur et on le supprime.

### Corrigé

*Numérateur.* On écrit $-3x = -4x + x$ :
$$2x^2-3x-2 = 2x^2-4x+x-2 = 2x(x-2)+(x-2) = (x-2)(2x+1)$$

(on vérifie en développant : $(2x+1)(x-2)=2x^2-4x+x-2=2x^2-3x-2$, ce qui redonne bien le numérateur de départ.)

*Dénominateur.* Identité remarquable : $x^2-4=(x-2)(x+2)$.

*Simplification.*
$$K(x) = \dfrac{(2x+1)(x-2)}{(x-2)(x+2)} = \dfrac{2x+1}{x+2}$$

Le dénominateur de départ $(x-2)(x+2)$ s'annule en $x=2$ et en $x=-2$ : ces deux valeurs restent exclues, exactement comme annoncé dans l'énoncé.

Vérification numérique : pour $x=4$, $K(4)=\dfrac{2\times16-12-2}{16-4}=\dfrac{18}{12}=\dfrac32$ ; avec la forme simplifiée, $\dfrac{2\times4+1}{4+2}=\dfrac{9}{6}=\dfrac32$ : les deux calculs coïncident.

**Pour tout $x\neq2$ et $x\neq-2$, $K(x) = \dfrac{2x+1}{x+2}$.**

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe dans la factorisation du numérateur : $(x-2)(2x-1) = 2x^2-5x+2$, ce n'est pas le numérateur.
- **b)** Numérateur mal factorisé en $(2x-1)(x+2) = 2x^2+3x-2$, puis simplification par $(x+2)$ : le signe du terme en $x$ est faux.
- **c)** Le coefficient $2$ a été oublié : $(x-2)(x+1) = x^2-x-2$, ce n'est pas le numérateur.

</details>

Avis : 

---

## 16. `cqc-simplification-elevee-0`

**A regarder :** Produit telescopique ecrit en clair (25/49) : niveau defi, limite haute du BEPC ?

**Enonce :**

On considère le produit
$$P = \left(1-\dfrac{1}{2^2}\right)\times\left(1-\dfrac{1}{3^2}\right)\times\left(1-\dfrac{1}{4^2}\right)\times\cdots\times\left(1-\dfrac{1}{49^2}\right)$$
Quelle est la valeur exacte de $P$, sous forme de fraction irréductible ?

- a) $\dfrac{1}{49}$
- b) $25$
- c) $\dfrac{51}{100}$
- d) $\dfrac{25}{49}$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Quand chaque facteur d'un produit se présente comme $1$ moins l'inverse d'un carré, on écrit $1-\dfrac{1}{m^2}=\dfrac{m^2-1}{m^2}=\dfrac{(m-1)(m+1)}{m^2}$ (différence de deux carrés au numérateur). Chaque facteur devient alors le produit de deux fractions $\dfrac{m-1}{m}\times\dfrac{m+1}{m}$, et l'on sépare le produit global en deux produits « en cascade » où presque tout se simplifie.

### Corrigé

*Transformation de chaque facteur.* Pour tout entier $m$ de $2$ à $49$ :
$$1-\dfrac{1}{m^2} = \dfrac{m^2-1}{m^2} = \dfrac{(m-1)(m+1)}{m^2} = \dfrac{m-1}{m}\times\dfrac{m+1}{m}$$

(on vérifie pour $m=2$ : $1-\dfrac14=\dfrac34$, et $\dfrac12\times\dfrac32=\dfrac34$ : cela coïncide.)

*Premier produit.* $\dfrac12\times\dfrac23\times\dfrac34\times\cdots\times\dfrac{48}{49}$. Chaque numérateur (à partir de $2$) simplifie le dénominateur du facteur précédent : il ne reste que le numérateur $1$ du premier facteur et le dénominateur $49$ du dernier, donc ce produit vaut $\dfrac{1}{49}$.

*Second produit.* $\dfrac32\times\dfrac43\times\dfrac54\times\cdots\times\dfrac{50}{49}$. De la même manière, tous les termes intermédiaires se simplifient et il ne reste que le premier dénominateur, $2$, et le dernier numérateur, $50$, donc ce produit vaut $\dfrac{50}{2}=25$.

*Conclusion.*
$$P = \dfrac{1}{49}\times25 = \dfrac{25}{49}$$

Vérification sur un cas réduit : $\left(1-\dfrac14\right)\left(1-\dfrac19\right)\left(1-\dfrac{1}{16}\right) = \dfrac34\times\dfrac89\times\dfrac{15}{16} = \dfrac58$, et la méthode donne $\dfrac14\times\dfrac52=\dfrac58$ : cela coïncide.

**$P = \dfrac{25}{49}$.**

### Pourquoi les autres réponses sont fausses

- **a)** Seul le premier produit $\dfrac12\times\dfrac23\times\cdots\times\dfrac{48}{49}$ a été pris en compte ; le second produit, égal à $25$, a été oublié.
- **b)** Seul le second produit a été pris en compte ; le premier, égal à $\dfrac{1}{49}$, a été oublié.
- **c)** Erreur sur le dernier facteur : $\dfrac{51}{100}$ correspond à un produit qui irait jusqu'à $1-\dfrac{1}{50^2}$.

</details>

Avis : 

---

## 17. `cqc-simplification-de-racines-faible-1`

**A regarder :** Un distracteur (3 racine(20)) a la MEME VALEUR que la bonne reponse 6 racine(5) : faux seulement parce que l'enonce demande la forme la plus simple.

**Enonce :**

Quelle est l'écriture du nombre $\sqrt{180}$ sous la forme $a\sqrt{b}$, où $a$ et $b$ sont des entiers naturels et $b$ le plus petit possible ?

- a) $6\sqrt{5}$
- b) $3\sqrt{20}$
- c) $36\sqrt{5}$
- d) $6\sqrt{30}$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Pour simplifier un radical, on décompose le nombre sous la racine en un produit faisant apparaître le plus grand carré parfait possible, puis on sort ce carré du radical : $\sqrt{k^{2} \times n} = k\sqrt{n}$.

### Corrigé

*Décomposition de $180$.* On cherche le plus grand carré parfait qui divise $180$ :

$$180 = 36 \times 5$$

Or $36 = 6^{2}$ est un carré parfait, donc

$$\sqrt{180} = \sqrt{36 \times 5} = \sqrt{36} \times \sqrt{5} = 6\sqrt{5}$$

En identifiant avec la forme $a\sqrt{b}$ : $a = 6$ et $b = 5$.

*Contrôle numérique.* $\sqrt{180} \approx 13{,}42$ et $6\sqrt{5} \approx 6 \times 2{,}236 = 13{,}42$.

### Pourquoi les autres réponses sont fausses

- **b)** $3\sqrt{20}$ : la valeur est juste ($9 \times 20 = 180$), mais $20 = 4 \times 5$ contient encore le carré parfait $4$ ; $b$ n'est donc pas le plus petit possible.
- **c)** $36\sqrt{5}$ : on a sorti $36$ du radical sans prendre sa racine carrée ; or $\sqrt{36} = 6$.
- **d)** $6\sqrt{30}$ : on a écrit $180 = 6 \times 30$ et sorti $6$ du radical, alors que $6$ n'est pas un carré parfait ($\sqrt{6} \neq 6$).

</details>

Avis : 

---

## 18. `cqc-volume-elevee-0`

**A regarder :** Seule la question 'nombre de bidons' est gardee ; 74,88 bidons -> 75 : arrondi par exces, 'bidons pleins' maladroit ?

**Enonce :**

Un bloc de béton plein a la forme d'un pavé droit de dimensions $2$ m sur $1{,}5$ m sur $1$ m. On y creuse une cavité, elle aussi en forme de pavé droit, de dimensions $1{,}8$ m sur $1{,}3$ m sur $0{,}8$ m, destinée à recevoir de l'eau ($1 \ \text{m}^{3} = 1\,000$ L).

On remplit la cavité à l'aide de bidons de $25$ L chacun. Combien de bidons pleins faut-il au minimum pour la remplir complètement ?

- a) $74$ bidons
- b) $75$ bidons
- c) $120$ bidons
- d) $46$ bidons

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Le volume d'un pavé droit est le produit de ses trois dimensions. Pour convertir un volume de m³ en litres, on multiplie par $1\,000$. Lorsqu'on répartit un volume en récipients de capacité fixe, le nombre de récipients pleins nécessaires s'obtient en divisant le volume total par la capacité d'un récipient, puis en arrondissant à l'entier supérieur si le quotient n'est pas entier.

### Corrigé

*Volume de la cavité.* Seules les dimensions de la cavité comptent :

$$V = 1{,}8 \times 1{,}3 \times 0{,}8$$

$1{,}8 \times 1{,}3 = 2{,}34$, puis $2{,}34 \times 0{,}8 = 1{,}872$.

$$V = 1{,}872 \ \text{m}^{3}$$

En litres :

$$V = 1{,}872 \times 1\,000 = 1\,872 \ \text{L}$$

*Nombre de bidons.*

$$\frac{1\,872}{25} = 74{,}88$$

Comme $74{,}88$ n'est pas un nombre entier, $74$ bidons ne suffisent pas ($74 \times 25 = 1\,850$ L, ce qui est inférieur à $1\,872$ L). Il faut donc un bidon de plus :

$$75 \times 25 = 1\,875 \ \text{L} \geqslant 1\,872 \ \text{L}$$

Il faut au minimum **75 bidons** pour remplir complètement la cavité.

### Pourquoi les autres réponses sont fausses
- **a)** On a tronqué $74{,}88$ à $74$ : avec $74$ bidons on n'a que $1\,850$ L, la cavité n'est pas pleine.
- **c)** On a calculé avec les dimensions du bloc entier ($3 \ \text{m}^{3} = 3\,000$ L) au lieu de celles de la cavité.
- **d)** On a calculé le volume de béton restant ($3\,000 - 1\,872 = 1\,128$ L) au lieu du volume de la cavité.

</details>

Avis : 

---

## 19. `cqc-volume-d-un-cone-elevee-0`

**A regarder :** Question reduite au nombre de bidons (994, arrondi par defaut). Convention d'arrondi a verifier.

**Enonce :**

Un réservoir d'eau est formé d'un cylindre de rayon $1{,}2$ m et de hauteur $3$ m, surmonté d'un cône de même rayon et de hauteur $0{,}9$ m (on prendra $\pi = 3{,}14$ et $1 \ \text{m}^3 = 1000$ litres).

Ce réservoir plein est utilisé pour remplir des bidons de $15$ litres chacun. Quel est le nombre maximum de bidons pleins que l'on peut obtenir ?

- a) $995$
- b) $994$
- c) $904$
- d) $1175$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Le volume d'un réservoir formé d'un cylindre surmonté d'un cône de même base est la somme du volume du cylindre et de celui du cône. Une fois le volume converti en litres, le nombre de récipients que l'on peut remplir s'obtient en divisant ce volume par la contenance d'un récipient ; comme on ne peut pas remplir une fraction de bidon, on ne retient que la partie entière du quotient.

### Corrigé

*Volume de la partie cylindrique.* Rayon $r = 1{,}2$ m, hauteur $H = 3$ m :
$$V_1 = \pi r^2 H = 3{,}14 \times 1{,}2^2 \times 3 = 3{,}14 \times 1{,}44 \times 3 = 13{,}5648 \ \text{m}^3$$

*Volume de la partie conique.* Même rayon, hauteur $h = 0{,}9$ m :
$$V_2 = \frac{\pi r^2 h}{3} = \frac{3{,}14 \times 1{,}44 \times 0{,}9}{3} = \frac{4{,}06944}{3} = 1{,}35648 \ \text{m}^3$$

*Volume total.*
$$V = V_1 + V_2 = 13{,}5648 + 1{,}35648 = 14{,}92128 \ \text{m}^3$$

*Conversion en litres.*
$$V = 14{,}92128 \times 1000 = 14\,921{,}28 \ \text{litres}$$

*Nombre de bidons.*
$$\frac{14\,921{,}28}{15} \approx 994{,}75$$

On ne peut remplir qu'un nombre entier de bidons : le réservoir plein permet donc de remplir **994 bidons** de $15$ litres ($994 \times 15 = 14\,910$ litres utilisés, il reste $11{,}28$ litres, moins qu'un bidon).

*Contrôle.* $V = \pi r^2 \left(H + \dfrac{h}{3}\right) = 3{,}14 \times 1{,}44 \times 3{,}3 = 14{,}92128 \ \text{m}^3$ ✔

### Pourquoi les autres réponses sont fausses

- **a)** $995$ : on a arrondi $994{,}75$ au nombre entier le plus proche, mais le 995e bidon ne peut pas être rempli entièrement.
- **c)** $904$ : on a oublié le volume du cône et compté seulement le cylindre ($13\,564{,}8$ litres).
- **d)** $1175$ : on a calculé le volume du cône sans diviser par $3$ ($\pi r^2 h$ au lieu de $\dfrac{\pi r^2 h}{3}$).

</details>

Avis : 

---

## 20. `cqc-probleme-concret-faible-0`

**A regarder :** 'Caution non remboursable' est contradictoire (une caution est remboursable) : a reformuler en frais fixes ?

**Enonce :**

Un centre de loisirs loue des vélos aux visiteurs. Le tarif comprend une caution non remboursable de 1500 F, à laquelle s'ajoutent 250 F par heure d'utilisation. Paul a payé 3250 F au total pour la location d'un vélo.

Combien d'heures Paul a-t-il gardé le vélo ?

- a) 13 heures
- b) 19 heures
- c) 7 heures
- d) 2 heures

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Dans un problème concret, on nomme l'inconnue avec son unité, on traduit l'énoncé par une équation, puis on résout et on revient au contexte pour vérifier que la réponse a un sens. Une somme payée une seule fois (une caution) devient un terme constant ; un tarif horaire devient un coefficient multiplicateur de l'inconnue.

### Corrigé

Notons $x$ le nombre d'heures pendant lesquelles Paul a gardé le vélo.

La caution de 1500 F est payée une seule fois, et 250 F s'ajoutent pour chaque heure :
$$250x + 1500 = 3250$$

On résout :
$$250x = 3250 - 1500 = 1750$$
$$x = \frac{1750}{250} = 7$$

*Vérification.* $250 \times 7 + 1500 = 1750 + 1500 = 3250$ F ✔, et $7$ heures est bien une durée positive.

Paul a gardé le vélo pendant **7 heures**.

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié la caution : $3250 \div 250 = 13$.
- **b)** On a ajouté la caution au lieu de la retrancher : $(3250 + 1500) \div 250 = 19$.
- **d)** On a inversé les rôles des deux montants : $1500x + 250 = 3250$ donne $x = 2$.

</details>

Avis : 

---

