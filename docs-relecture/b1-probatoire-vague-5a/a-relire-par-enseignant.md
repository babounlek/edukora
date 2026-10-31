# Vague 5a Maths Probatoire et BAC (questions communes aux deux examens) : 51 QCM à faire relire par l'enseignant (campagne B1)

Date : 2026-10-31. Sur 64 QCM convertis (108 questions étudiées, 44 écartées), **51** vous sont soumis : ceux que le relecteur aveugle a assortis d'une remarque, ceux dont la question ou la méthode a été modifiée ou dont des séries ont été retirées, et un tirage de 8 autres. Le lot est prêt mais n'est pas en ligne tant que vous n'avez pas répondu. Les 64 résolutions à l'aveugle ont toutes donné la clé.

Ces questions sont posées à la fois au Probatoire et au BAC (séries indiquées pour chacune). Elles sont adaptées au niveau de la plus faible des séries concernées, avec le programme de Première.

## Avis déjà rendus, appliqués par analogie (à confirmer)

- **Série A retirée** des questions sur les asymptotes (verticale, oblique) et sur la dérivée d'un quotient (8 questions), conformément à votre avis sur les limites de fonctions homographiques et les dérivées en série A.
- **Première C retirée** des questions sur le changement de base et sur les endomorphismes en dimension 3 (6 questions), conformément à votre avis sur les matrices et applications linéaires : elles restent pour le BAC C et E (et le Probatoire E pour les endomorphismes).

## Points à trancher (nouveaux)

1. **Dérivabilité par encadrement :** deux questions (`derivabilite-moyenne-1` et `derivabilite-elevee-0`) se résolvent avec la majoration $|\cos|\le 1$ ou un encadrement et le théorème des gendarmes. Au programme de Première C, D, E ?
2. **Dérivée de $\sqrt u$ :** une question en C, D, E (Probatoire). Au programme ?
3. **Distance d'un point à une droite** (formule de la valeur absolue sur la racine) : vue en Première C ? (liée au produit scalaire, absent du référentiel)
4. **Limite d'une suite géométrique de raison entre -1 et 1** en C et E : au programme de Première ?
5. **Statistiques à deux variables :** 4 questions sur la covariance et 4 sur l'ajustement affine ont été écartées (hors programme des séries à une variable). À confirmer.
6. **Probabilités :** 3 questions ont été écartées parce que la conversion en dénombrement aurait changé la clé.
7. **Dérivée d'un polynôme en série A** (3 questions qui restent, comme pour la vague 4b) : à confirmer.

Pour chaque question : **OK**, **à corriger** (dire quoi), **à retirer**, ou **retirer la série X**.

## 1. `cqc-lecture-graphique-prob-a-moyenne-4` (séries BAC:A PRO:A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le tableau de variations d'une fonction $f$ continue sur $[-3\,;5]$ indique : $f$ strictement croissante sur $[-3\,;1]$ de $-2$ à $4$, puis strictement décroissante sur $[1\,;5]$ de $4$ à $0$. Combien de solutions ont, sur $[-3\,;5]$, l'équation $f(x)=1$ d'une part et l'équation $f(x)=-1$ d'autre part ?

- a) $1$ solution et $1$ solution
- b) $2$ solutions et $2$ solutions
- c) $2$ solutions et $1$ solution
- d) $2$ solutions et aucune solution

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Sur chaque intervalle où $f$ est continue et strictement monotone, $f$ prend une fois et une seule chaque valeur comprise entre ses valeurs aux bornes. On regarde donc, intervalle par intervalle, si la valeur cherchée est atteinte.

### Corrigé

$f(x)=1$ : sur $[-3\,;1]$, $f$ passe de $-2$ à $4$ donc atteint $1$ une fois ; sur $[1\,;5]$, elle passe de $4$ à $0$ donc atteint $1$ une fois : **$2$ solutions**.

$f(x)=-1$ : atteint une fois sur $[-3\,;1]$ (de $-2$ à $4$) ; sur $[1\,;5]$, $f(x)\ge0$ donc $-1$ n'est pas atteint : **$1$ solution**.

Réponse : $2$ solutions et $1$ solution.

### Pourquoi les autres réponses sont fausses

- **a)** On n'a regardé que l'intervalle $[-3\,;1]$ pour $f(x)=1$, en oubliant la descente de $4$ à $0$ sur $[1\,;5]$.
- **b)** On a cru que $-1$ était aussi atteint sur $[1\,;5]$, alors que $f$ y prend seulement des valeurs entre $0$ et $4$.
- **d)** On a oublié que $f$ part de $-2$ en $x=-3$ : elle passe donc par $-1$ sur $[-3\,;1]$.

</details>

Avis : 

---

## 2. `cqc-lecture-graphique-prob-a-moyenne-5` (séries BAC:A PRO:A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Sur un graphique, on lit qu'une droite passe par les points $A(0\,;1)$ et $B(2\,;5)$. Quelle est l'équation réduite de cette droite ?

- a) $y=2x+1$
- b) $y=\dfrac{1}{2}x+1$
- c) $y=4x+1$
- d) $y=2x+5$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Le coefficient directeur est $a=\dfrac{y_B-y_A}{x_B-x_A}$ et $b$ est l'ordonnée à l'origine (ordonnée du point d'abscisse $0$).

### Corrigé

$a=\dfrac{5-1}{2-0}=\dfrac{4}{2}=2$. La droite coupe l'axe des ordonnées en $A(0\,;1)$ : $b=1$. Équation réduite : $y=2x+1$.

### Pourquoi les autres réponses sont fausses

- **b)** On a inversé le quotient : $\dfrac{x_B-x_A}{y_B-y_A}=\dfrac{1}{2}$.
- **c)** On a oublié de diviser la différence des ordonnées par la différence des abscisses.
- **d)** On a pris l'ordonnée de $B$ comme ordonnée à l'origine, alors que $B$ n'est pas sur l'axe des ordonnées.

</details>

Avis : 

---

## 3. `cqc-systemes-lineaires-faible-0` (séries BAC:A PRO:A)

**Énoncé :**

Quel est le triplet solution $(x\,;\,y\,;\,z)$ du système suivant ?

$$\begin{cases} x + y + z = 12 \\ y - z = 1 \\ x - z = 2 \end{cases}$$

- a) $(5\,;\,2\,;\,3)$
- b) $(1\,;\,4\,;\,3)$
- c) $(7\,;\,6\,;\,5)$
- d) $(5\,;\,4\,;\,3)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand deux équations isolent directement deux inconnues en fonction de la troisième, on les substitue dans la troisième équation : c'est la méthode par substitution directe.

### Corrigé
D'après (2) : $y = z+1$.

D'après (3) : $x = z+2$.

On remplace dans (1) : $(z+2)+(z+1)+z=12 \Rightarrow 3z+3=12 \Rightarrow z=3$.

On en déduit $y = 3+1=4$ et $x=3+2=5$.

Vérification :
- (1) : $5+4+3=12$ ;
- (2) : $4-3=1$ ;
- (3) : $5-3=2$.

$$\boxed{(x\,;\,y\,;\,z) = (5\,;\,4\,;\,3)}$$

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe dans (2) : on a écrit $y=z-1$ au lieu de $y=z+1$.
- **b)** Erreur de signe dans (3) : on a écrit $x=z-2$ au lieu de $x=z+2$.
- **c)** On a ajouté $3$ au lieu de le retrancher : $3z=12+3$ donne $z=5$, puis $y=6$ et $x=7$.

</details>

Avis : 

---

## 4. `cqc-systemes-lineaires-moyenne-0` (séries BAC:A PRO:A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Quel est le triplet solution $(x\,;\,y\,;\,z)$ du système suivant ?

$$\begin{cases} x - y + 2z = 13 \\ 2x + y - z = 0 \\ x + 2y + 3z = 11 \end{cases}$$

- a) $(3\,;\,2\,;\,4)$
- b) $(7\,;\,-2\,;\,4)$
- c) $(3\,;\,-2\,;\,4)$
- d) $(4\,;\,-2\,;\,3)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode
La méthode du pivot consiste à choisir une équation « pivot » (ici la première, où $x$ a pour coefficient 1) puis à l'utiliser pour éliminer $x$ dans les deux autres équations, ce qui donne un système triangulaire que l'on résout par remontée.

### Corrigé
On prend l'équation (1) comme pivot : $x - y + 2z = 13$.

**Élimination de $x$ dans (2)** : $(2) - 2\times(1)$ : $(2x+y-z) - 2(x-y+2z) = 0 - 2\times13$
$\Rightarrow 3y - 5z = -26$ (2')

**Élimination de $x$ dans (3)** : $(3) - (1)$ : $(x+2y+3z)-(x-y+2z)=11-13$
$\Rightarrow 3y + z = -2$ (3')

**Remontée** : $(2') - (3')$ : $(3y-5z)-(3y+z) = -26-(-2) \Rightarrow -6z=-24 \Rightarrow z=4$.

Dans (3') : $3y+4=-2 \Rightarrow y=-2$.

Dans (1) : $x-(-2)+2\times4=13 \Rightarrow x+2+8=13 \Rightarrow x=3$.

Vérification :
- (1) : $3-(-2)+8=13$ ;
- (2) : $6+(-2)-4=0$ ;
- (3) : $3+(-4)+12=11$.

$$\boxed{(x\,;\,y\,;\,z) = (3\,;\,-2\,;\,4)}$$

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe sur $y$ : $3y=-6$ donne $y=-2$, et non $y=2$ ; d'ailleurs $(3\,;\,2\,;\,4)$ ne vérifie pas (1).
- **b)** On a remplacé $-(-2)$ par $-2$ dans (1) : $x-2+8=13$ donne $x=7$.
- **d)** Les valeurs de $x$ et de $z$ ont été échangées dans le triplet.

</details>

Avis : 

---

## 5. `cqc-systemes-lineaires-moyenne-2` (séries BAC:A PRO:A)

**Énoncé :**

Une tontine partage une cagnotte commune de 2900 FCFA entre trois membres A, B et C. On note $x$, $y$ et $z$ les parts respectives (en FCFA) de A, B et C. On sait que :
- la part de A dépasse celle de B de 500 FCFA ;
- la part de C est le double de celle de B ;
- la somme des trois parts est 2900 FCFA.

$$\begin{cases} x + y + z = 2900 \\ x = y + 500 \\ z = 2y \end{cases}$$

Quel est le triplet $(x\,;\,y\,;\,z)$ des parts de A, B et C ?

- a) $(1300\,;\,800\,;\,1600)$
- b) $(1350\,;\,850\,;\,1700)$
- c) $(600\,;\,1100\,;\,1200)$
- d) $(1100\,;\,600\,;\,1200)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Lorsque deux équations expriment déjà directement deux inconnues en fonction de la troisième, il suffit de les substituer dans l'équation restante : c'est la méthode par substitution directe.

### Corrigé
Les équations (2) et (3) donnent directement $x$ et $z$ en fonction de $y$ : $x=y+500$ et $z=2y$.

On remplace dans (1) : $(y+500) + y + 2y = 2900 \Rightarrow 4y + 500 = 2900 \Rightarrow 4y = 2400 \Rightarrow y=600$.

On en déduit $x = 600+500=1100$ et $z=2\times600=1200$.

Vérification :
- (1) : $1100+600+1200=2900$ ;
- (2) : $1100=600+500$ ;
- (3) : $1200=2\times600$.

A reçoit 1100 FCFA, B reçoit 600 FCFA et C reçoit 1200 FCFA.

$$\boxed{(x\,;\,y\,;\,z) = (1100\,;\,600\,;\,1200)}$$

### Pourquoi les autres réponses sont fausses

- **a)** On a remplacé $z$ par $y$ au lieu de $2y$ : $3y+500=2900$ donne $y=800$.
- **b)** Erreur de signe en isolant $4y$ : $4y=2900+500=3400$ donne $y=850$.
- **c)** Les parts de A et de B ont été échangées dans le triplet.

</details>

Avis : 

---

## 6. `cqc-angle-faible-0` (séries BAC:D BAC:TI PRO:C PRO:E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $A$ un point du plan et $r$ la rotation de centre $A$ et d'angle $\dfrac{\pi}{3}$ qui transforme un point $M$ en un point $N$. On donne $AM = 6$ cm. Quel est le périmètre du triangle $AMN$ ?

- a) $12$ cm
- b) $12+6\sqrt{2}$ cm
- c) $18$ cm
- d) $12+6\sqrt{3}$ cm

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Une rotation conserve les distances : si $r$ a pour centre $A$, alors pour tout point $M$ d'image $N$, on a $AM = AN$, donc le triangle $AMN$ est isocèle en $A$. Par définition, la mesure de l'angle $\widehat{MAN}$ est l'angle de la rotation. Un triangle isocèle dont l'angle au sommet mesure $\dfrac{\pi}{3}$ a nécessairement ses trois angles égaux à $\dfrac{\pi}{3}$ : il est donc équilatéral.

### Corrigé

La rotation $r$ conserve les distances, donc $AM = AN = 6$ cm : le triangle $AMN$ est isocèle en $A$, et $\widehat{MAN} = \dfrac{\pi}{3}$.

Les angles à la base d'un triangle isocèle sont égaux ; comme la somme des angles du triangle vaut $\pi$ :
$$2\,\widehat{AMN} = \pi - \dfrac{\pi}{3} = \dfrac{2\pi}{3} \quad\Longrightarrow\quad \widehat{AMN} = \widehat{ANM} = \dfrac{\pi}{3}$$

Le triangle $AMN$ est donc équilatéral : $MN = AM = AN = 6$ cm.

Le périmètre vaut $3 \times 6 = 18$ cm.

### Pourquoi les autres réponses sont fausses

- **a)** On n'a additionné que $AM$ et $AN$, en oubliant le troisième côté $MN$.
- **b)** On a raisonné comme pour une rotation d'angle $\dfrac{\pi}{2}$ (triangle rectangle isocèle, $MN=6\sqrt{2}$).
- **d)** On a pris $MN=6\sqrt{3}$, valeur qui correspondrait à un angle au sommet de $\dfrac{2\pi}{3}$.

</details>

Avis : 

---

## 7. `cqc-angle-moyenne-2` (séries BAC:D BAC:TI PRO:C PRO:E)

**Remarque du relecteur :** VOCABULAIRE : « une rotation du plan a pour mesure d'angle orienté » est maladroit ; écrire « l'angle d'une rotation a pour mesure 13pi/4 » ou simplement « un angle orienté a pour mesure ».

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une rotation du plan a pour mesure d'angle orienté $\dfrac{13\pi}{4}$ radians. Quelle est la mesure principale de cet angle orienté, c'est-à-dire l'unique mesure appartenant à l'intervalle $]-\pi\,;\,\pi]$ ?

- a) $\dfrac{5\pi}{4}$
- b) $-\dfrac{3\pi}{4}$
- c) $\dfrac{3\pi}{4}$
- d) $\dfrac{\pi}{4}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Un angle orienté n'est défini qu'à un multiple de $2\pi$ près : pour retrouver sa mesure principale, on ajoute ou on retranche des multiples de $2\pi$ jusqu'à obtenir une valeur appartenant à $]-\pi\,;\,\pi]$.

### Corrigé

On retranche $2\pi = \dfrac{8\pi}{4}$ à $\dfrac{13\pi}{4}$ :
$$\dfrac{13\pi}{4} - \dfrac{8\pi}{4} = \dfrac{5\pi}{4}$$

Cette valeur n'appartient pas encore à $]-\pi\,;\,\pi]$ car $\dfrac{5\pi}{4} > \pi$ ; on retranche donc encore $2\pi$ :
$$\dfrac{5\pi}{4} - \dfrac{8\pi}{4} = -\dfrac{3\pi}{4}$$

Cette valeur appartient bien à $]-\pi\,;\,\pi]$ : la mesure principale est $-\dfrac{3\pi}{4}$ rad (l'angle géométrique associé mesure $\dfrac{3\pi}{4}$ rad).

### Pourquoi les autres réponses sont fausses

- **a)** On s'est arrêté après une seule soustraction de $2\pi$ : $\dfrac{5\pi}{4}$ dépasse $\pi$.
- **c)** On a oublié le signe : $\dfrac{3\pi}{4}$ est l'angle géométrique, pas la mesure principale de l'angle orienté.
- **d)** On a retranché $3\pi$, qui n'est pas un multiple de $2\pi$ : la mesure obtenue ne représente pas le même angle orienté.

</details>

Avis : 

---

## 8. `cqc-angle-moyenne-3` (séries BAC:D BAC:TI PRO:C PRO:E)

**Énoncé :**

Dans un triangle $RST$ isocèle de sommet principal $R$ (donc $RS = RT$), chaque angle à la base dépasse de $30°$ l'angle au sommet $\widehat{SRT}$. Quelles sont les mesures respectives des angles $\widehat{SRT}$, $\widehat{RST}$ et $\widehat{RTS}$ ?

- a) $40°$, $70°$ et $70°$
- b) $50°$, $80°$ et $80°$
- c) $80°$, $50°$ et $50°$
- d) $30°$, $75°$ et $75°$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans tout triangle, la somme des mesures des trois angles vaut $180°$. Dans un triangle isocèle, les deux angles à la base (opposés aux côtés de même longueur) sont égaux entre eux. On traduit l'énoncé par une relation entre l'angle au sommet et l'angle à la base, puis on résout l'équation obtenue.

### Corrigé

Notons $x$ la mesure de l'angle au sommet $\widehat{SRT}$. Les angles à la base $\widehat{RST}$ et $\widehat{RTS}$ sont égaux ; d'après l'énoncé, chacun mesure $x + 30°$.

La somme des angles du triangle vaut $180°$ :
$$x + (x+30°) + (x+30°) = 180°$$
$$3x + 60° = 180°$$
$$3x = 120° \quad\Longrightarrow\quad x = 40°$$

L'angle au sommet mesure donc $40°$, et chacun des deux angles à la base mesure $40° + 30° = 70°$.

Contrôle : $40° + 70° + 70° = 180°$.

### Pourquoi les autres réponses sont fausses

- **b)** On n'a compté qu'une fois les $30°$ : $3x+30°=180°$ donne $x=50°$ (somme $210°$).
- **c)** On a inversé la relation : c'est l'angle au sommet qui dépasserait de $30°$ chaque angle à la base.
- **d)** On a pris $30°$ pour la mesure de l'angle au sommet, puis partagé le reste en deux.

</details>

Avis : 

---

## 9. `cqc-angle-moyenne-4` (séries BAC:D BAC:TI PRO:C PRO:E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

$ABC$ est un triangle isocèle en $A$ (donc $AB = AC$) tel que $\widehat{BAC} = \dfrac{2\pi}{5}$ radians. Quelle est la mesure, en radians, de chacun des deux angles à la base de ce triangle ?

- a) $\dfrac{3\pi}{5}$
- b) $\dfrac{\pi}{10}$
- c) $\dfrac{\pi}{3}$
- d) $\dfrac{3\pi}{10}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un triangle isocèle, les angles à la base sont égaux, et la somme des trois angles du triangle vaut $\pi$ radians.

### Corrigé

Le triangle $ABC$ est isocèle en $A$, donc les angles à la base $\widehat{ABC}$ et $\widehat{ACB}$ sont égaux. Comme la somme des angles du triangle vaut $\pi$ :
$$2\,\widehat{ABC} = \pi - \dfrac{2\pi}{5} = \dfrac{5\pi}{5} - \dfrac{2\pi}{5} = \dfrac{3\pi}{5}$$
$$\widehat{ABC} = \widehat{ACB} = \dfrac{3\pi}{10}$$

Contrôle : $\dfrac{2\pi}{5} + \dfrac{3\pi}{10} + \dfrac{3\pi}{10} = \dfrac{4\pi}{10} + \dfrac{6\pi}{10} = \pi$.

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié de diviser par $2$ : $\dfrac{3\pi}{5}$ est la somme des deux angles à la base.
- **b)** On a divisé seulement $\pi$ par $2$ : $\dfrac{\pi}{2}-\dfrac{2\pi}{5}=\dfrac{\pi}{10}$, au lieu de diviser toute la différence $\pi-\dfrac{2\pi}{5}$.
- **c)** On a cru le triangle équilatéral, alors que l'angle au sommet ne vaut pas $\dfrac{\pi}{3}$.

</details>

Avis : 

---

## 10. `cqc-arrangements-faible-0` (séries BAC:A PRO:A PRO:D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Un sac contient 11 fiches numérotées de 1 à 11. Un élève tire successivement et sans remise 3 fiches de ce sac, en notant l'ordre dans lequel elles sortent. Combien de tirages ordonnés sont possibles ?

- a) $165$
- b) $990$
- c) $1\,331$
- d) $33$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Lorsqu'on tire successivement et sans remise $p$ éléments parmi $n$, en tenant compte de l'ordre de sortie, chaque tirage possible est un arrangement de $p$ éléments parmi $n$. Leur nombre est $A_n^p = n\times(n-1)\times\cdots\times(n-p+1)$.

### Corrigé

Ici $n = 11$ fiches et $p = 3$ tirages successifs sans remise, avec ordre pris en compte.

Le nombre de tirages ordonnés possibles est :
$$A_{11}^3 = 11\times10\times9 = 990$$

Il y a donc **990** tirages ordonnés possibles.

### Pourquoi les autres réponses sont fausses

- **a)** $165 = C_{11}^3$ : c'est le nombre de combinaisons, qui ne tient pas compte de l'ordre de sortie.
- **c)** $1\,331 = 11^3$ : ce serait le nombre de tirages avec remise, où une même fiche peut ressortir.
- **d)** $33 = 11\times3$ : multiplier le nombre de fiches par le nombre de tirages ne correspond à aucun dénombrement.

</details>

Avis : 

---

## 11. `cqc-arrangements-faible-1` (séries BAC:A PRO:A PRO:D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Un conseil d'établissement compte 7 délégués d'élèves élus. Il doit désigner, parmi ces 7 délégués, un délégué titulaire et un délégué adjoint, ces deux fonctions étant distinctes et ne pouvant pas être occupées par la même personne. Combien de désignations différentes sont possibles ?

- a) $21$
- b) $14$
- c) $49$
- d) $42$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand on attribue des fonctions distinctes (ici « titulaire » et « adjoint ») à des personnes différentes choisies parmi un groupe, l'ordre d'attribution compte : désigner X comme titulaire et Y comme adjoint est différent de désigner Y comme titulaire et X comme adjoint. C'est donc un arrangement, et non une combinaison : $A_n^p = n\times(n-1)\times\cdots\times(n-p+1)$.

### Corrigé

Ici $n = 7$ délégués et $p = 2$ fonctions distinctes à pourvoir, sans répétition possible d'une même personne.

Le nombre de désignations possibles est :
$$A_7^2 = 7\times6 = 42$$

Il y a donc **42** désignations différentes possibles. (Si les deux postes n'étaient pas distingués, il faudrait utiliser la combinaison $C_7^2 = 21$, deux fois moins nombreuse, car elle ne différencierait pas qui est titulaire de qui est adjoint.)

### Pourquoi les autres réponses sont fausses

- **a)** $21 = C_7^2$ : on a oublié que les deux fonctions sont distinctes, donc que l'ordre compte.
- **b)** $14 = 7\times2$ : multiplier le nombre de délégués par le nombre de postes ne dénombre rien.
- **c)** $49 = 7^2$ : on a autorisé la même personne à occuper les deux fonctions.

</details>

Avis : 

---

## 12. `cqc-arrangements-moyenne-1` (séries BAC:A PRO:A PRO:D)

**Remarque du relecteur :** VOCABULAIRE : « valeur exacte sous forme décimale » est lourd ; « on donne le résultat sous forme décimale » suffit.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le digicode d'un immeuble demande de composer un code à 3 chiffres, chaque chiffre étant choisi parmi 0, 1, 2, ..., 9 (un même chiffre peut être répété dans le code). Parmi tous les codes à 3 chiffres possibles, quelle proportion de codes ont leurs 3 chiffres deux à deux distincts ? (On donne la valeur exacte sous forme décimale.)

- a) $0{,}12$
- b) $0{,}28$
- c) $0{,}72$
- d) $0{,}504$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

La proportion d'éléments d'un ensemble fini ayant une propriété se calcule par $\dfrac{\text{nombre d'éléments ayant la propriété}}{\text{nombre total d'éléments}}$. Quand les éléments retenus imposent que des chiffres choisis successivement soient tous distincts, leur nombre se calcule avec un arrangement $A_n^p$, alors que le nombre total s'obtient en autorisant les répétitions.

### Corrigé

Nombre total de codes à 3 chiffres, répétitions autorisées : chaque chiffre a 10 possibilités, donc il y a $10^3 = 1\,000$ codes.

Nombre de codes à 3 chiffres deux à deux distincts : c'est un arrangement de 3 chiffres parmi 10,
$$A_{10}^3 = 10\times9\times8 = 720.$$

La proportion cherchée, donnée sous forme décimale exacte, est donc :
$$\dfrac{720}{1\,000} = \dfrac{18}{25} = 0{,}72$$

### Pourquoi les autres réponses sont fausses

- **a)** $0{,}12 = \dfrac{120}{1\,000}$ : on a compté les combinaisons $C_{10}^3 = 120$, en oubliant que l'ordre des chiffres compte dans un code.
- **b)** $0{,}28 = 1 - 0{,}72$ : c'est la proportion des codes ayant au moins deux chiffres égaux, la propriété contraire.
- **d)** $0{,}504 = \dfrac{9\times8\times7}{1\,000}$ : on a oublié le chiffre 0 parmi les chiffres possibles du code.

</details>

Avis : 

---

## 13. `cqc-asymptote-oblique-faible-0` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PRO:C PRO:D PRO:E)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A, PRO:A.

**Remarque du relecteur :** LIMITE : asymptote oblique d'une fonction rationnelle, à la limite haute pour la série A (BAC:A).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}\setminus\{1\}$ par $$f(x) = \dfrac{3x^2 - 5x + 4}{x - 1}.$$ La courbe représentative de $f$ admet une asymptote oblique en $+\infty$ et en $-\infty$. Quelle est son équation ?

- a) $y=3x-2$
- b) $y=3x-5$
- c) $y=3x+2$
- d) $y=3x-8$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Une droite d'équation $y=ax+b$ est asymptote oblique à la courbe de $f$ en $+\infty$ (respectivement en $-\infty$) lorsque $\displaystyle\lim_{x\to+\infty}\big[f(x)-(ax+b)\big] = 0$ (respectivement en $-\infty$). Pour une fraction rationnelle dont le degré du numérateur dépasse d'exactement 1 celui du dénominateur, on effectue la division euclidienne du numérateur par le dénominateur pour obtenir cette écriture.

### Corrigé
On divise $3x^2-5x+4$ par $x-1$ :
$$3x^2 - 5x + 4 = (x-1)(3x-2) + 2.$$
Donc, pour tout $x\neq 1$ :
$$f(x) = 3x - 2 + \dfrac{2}{x-1}.$$
Ainsi $f(x) - (3x-2) = \dfrac{2}{x-1}$.

Or $\displaystyle\lim_{x\to+\infty}\dfrac{2}{x-1} = 0$ et $\displaystyle\lim_{x\to-\infty}\dfrac{2}{x-1} = 0$.

On conclut que $\displaystyle\lim_{x\to\pm\infty}\big[f(x)-(3x-2)\big] = 0$ : la droite d'équation $y = 3x-2$ est asymptote oblique à la courbe de $f$ en $+\infty$ et en $-\infty$.

### Pourquoi les autres réponses sont fausses

- **b)** $y=3x-5$ : on a divisé $3x^2-5x$ par $x$ au lieu de diviser le numérateur par $x-1$ ; alors $f(x)-(3x-5)$ tend vers $3$, pas vers $0$.
- **c)** $y=3x+2$ : erreur de signe dans la division ; $-5x-(-3x)=-2x$ donne le terme $-2$ du quotient, pas $+2$.
- **d)** $y=3x-8$ : on a ajouté $-3x$ au lieu de soustraire $3x(x-1)=3x^2-3x$, ce qui donne $-8x$ au lieu de $-2x$.

</details>

Avis : 

---

## 14. `cqc-asymptote-oblique-faible-1` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PRO:C PRO:D PRO:E)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A, PRO:A.

**Remarque du relecteur :** LIMITE : asymptote oblique, limite haute pour la série A (BAC:A).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $C$ la fonction définie sur $]0\,;+\infty[$ par $$C(x) = \dfrac{x^{2}+3x-1}{x+1}.$$ La courbe représentative de $C$ admet une asymptote oblique lorsque $x$ tend vers $+\infty$. Quelle est son équation ?

- a) $y=x+3$
- b) $y=x+4$
- c) $y=x$
- d) $y=x+2$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour une fonction rationnelle $f(x)=\dfrac{P(x)}{Q(x)}$ dont le degré de $P$ dépasse d'exactement 1 celui de $Q$, on écrit $f(x) = ax+b+\dfrac{r}{Q(x)}$ grâce à la division euclidienne de $P$ par $Q$. La droite $y=ax+b$ est alors asymptote oblique dès que $\dfrac{r}{Q(x)}$ tend vers $0$.

### Corrigé
On divise $x^2+3x-1$ par $x+1$ :
$$x^2+3x-1 = (x+1)(x+2) - 3.$$
Donc, pour tout $x > 0$ :
$$C(x) = x+2 - \dfrac{3}{x+1}.$$
Par conséquent :
$$C(x) - (x+2) = -\dfrac{3}{x+1}.$$
Quand $x\to+\infty$, $-\dfrac{3}{x+1}\to 0$, donc $\displaystyle\lim_{x\to+\infty}\big[C(x)-(x+2)\big]=0$.

La courbe représentative de $C$ admet donc pour asymptote oblique, en $+\infty$, la droite d'équation $y = x+2$.

### Pourquoi les autres réponses sont fausses

- **a)** $y=x+3$ : on a divisé $x^2+3x$ par $x$ en oubliant le $+1$ du dénominateur ; $C(x)-(x+3)$ tend vers $-1$.
- **b)** $y=x+4$ : erreur de signe dans la division, on a ajouté $x$ à $3x$ au lieu de soustraire $x(x+1)=x^2+x$.
- **c)** $y=x$ : on n'a gardé que le quotient des termes de plus haut degré $\dfrac{x^2}{x}$, en oubliant l'ordonnée à l'origine.

</details>

Avis : 

---

## 15. `cqc-asymptote-verticale-prob-c-faible-0` (séries BAC:A PRO:A PRO:C PRO:D PRO:E)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A, PRO:A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}\setminus\{3\}$ par $f(x)=\dfrac1{x-3}$. Quelles sont les limites de $f$ en $3^-$ et en $3^+$ ?

- a) $\lim\limits_{x\to3^-}f(x)=+\infty$ et $\lim\limits_{x\to3^+}f(x)=-\infty$
- b) $\lim\limits_{x\to3^-}f(x)=-\infty$ et $\lim\limits_{x\to3^+}f(x)=+\infty$
- c) $\lim\limits_{x\to3^-}f(x)=+\infty$ et $\lim\limits_{x\to3^+}f(x)=+\infty$
- d) $\lim\limits_{x\to3^-}f(x)=-\infty$ et $\lim\limits_{x\to3^+}f(x)=-\infty$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Si $\lim\limits_{x\to a^\pm}f(x)=\pm\infty$, la droite d'équation $x=a$ est asymptote verticale à la courbe. On détermine le signe du dénominateur de chaque côté de $a$.

### Corrigé

Pour $x<3$, $x-3<0$ et $x-3\to0^-$ : $f(x)\to-\infty$. Pour $x>3$, $x-3\to0^+$ : $f(x)\to+\infty$.
$$\lim_{x\to3^-}f(x)=-\infty,\qquad\lim_{x\to3^+}f(x)=+\infty.$$
La droite d'équation $x=3$ est asymptote verticale à la courbe de $f$.

### Pourquoi les autres réponses sont fausses

- **a)** Les signes sont inversés : à gauche de $3$, le dénominateur $x-3$ est négatif, donc la limite est $-\infty$.
- **c)** On a oublié que $x-3$ change de signe en $3$ : à gauche, il est négatif.
- **d)** On a oublié qu'à droite de $3$, $x-3$ est positif, donc la limite est $+\infty$.

</details>

Avis : 

---

## 16. `cqc-asymptote-verticale-prob-c-moyenne-2` (séries BAC:A PRO:A PRO:C PRO:D PRO:E)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A, PRO:A.

**Remarque du relecteur :** LIMITE : pour la série A (PRO:A), limites infinies et asymptotes de fonctions rationnelles avec simplification sont à la limite haute du programme allégé.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}\setminus\{-1\,;2\}$ par $f(x)=\dfrac{x^2-1}{x^2-x-2}$. Quelles sont les asymptotes verticales de la courbe de $f$ ?

- a) Les droites d'équations $x=-1$ et $x=2$
- b) La droite d'équation $x=-1$ seulement
- c) La droite d'équation $x=2$ seulement
- d) Aucune asymptote verticale

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand le numérateur et le dénominateur s'annulent tous deux en $a$, on factorise et on simplifie par $(x-a)$ avant de calculer la limite : il n'y a alors pas d'asymptote en $a$ si la limite est finie (la courbe a un « trou »).

### Corrigé

$x^2-1=(x-1)(x+1)$ et $x^2-x-2=(x-2)(x+1)$. Pour $x\neq-1$ et $x\neq2$ : $f(x)=\dfrac{x-1}{x-2}$.

- En $x=-1$ : $\lim\limits_{x\to-1}f(x)=\dfrac{-2}{-3}=\dfrac23$, limite finie : **pas d'asymptote** (la courbe présente un point manquant $\left(-1\,;\dfrac23\right)$).
- En $x=2$ : le numérateur $x-1\to1>0$ et $x-2\to0$ : $\lim\limits_{x\to2^-}f(x)=-\infty$ et $\lim\limits_{x\to2^+}f(x)=+\infty$ : **asymptote verticale** d'équation $x=2$.

La courbe de $f$ admet donc une seule asymptote verticale, la droite d'équation $x=2$.

### Pourquoi les autres réponses sont fausses

- **a)** On a conclu à une asymptote à chaque valeur interdite, sans simplifier la fraction : en $-1$, la limite est finie.
- **b)** C'est l'inverse de la situation réelle : en $-1$, numérateur et dénominateur s'annulent et la limite vaut $\dfrac23$.
- **d)** La simplification par $x+1$ ne supprime pas la valeur interdite $2$, où la limite est infinie.

</details>

Avis : 

---

## 17. `cqc-asymptote-verticale-prob-c-moyenne-3` (séries BAC:A PRO:A PRO:C PRO:D PRO:E)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A, PRO:A.

**Remarque du relecteur :** LIMITE : limites infinies d'une fonction rationnelle, limite haute pour la série A (PRO:A).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}\setminus\{1\}$ par $f(x)=\dfrac{2x+3}{(x-1)^2}$. Quelles sont les limites de $f$ en $1^-$ et en $1^+$ ?

- a) $\lim\limits_{x\to1^-}f(x)=+\infty$ et $\lim\limits_{x\to1^+}f(x)=+\infty$
- b) $\lim\limits_{x\to1^-}f(x)=-\infty$ et $\lim\limits_{x\to1^+}f(x)=+\infty$
- c) $\lim\limits_{x\to1^-}f(x)=-\infty$ et $\lim\limits_{x\to1^+}f(x)=-\infty$
- d) $\lim\limits_{x\to1^-}f(x)=+\infty$ et $\lim\limits_{x\to1^+}f(x)=-\infty$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Quand le dénominateur est un carré, il reste positif de chaque côté de la valeur interdite : la limite a alors le même signe des deux côtés, déterminé par le signe du numérateur en cette valeur.

### Corrigé

En $x=1$ : le numérateur $2x+3$ tend vers $5>0$ et $(x-1)^2\to0^+$ des deux côtés (un carré est positif). Donc
$$\lim_{x\to1^-}f(x)=\lim_{x\to1^+}f(x)=+\infty.$$
La droite d'équation $x=1$ est asymptote verticale ; la courbe reste du même côté, vers le haut, à gauche et à droite.

### Pourquoi les autres réponses sont fausses

- **b)** On a raisonné comme si le dénominateur était $x-1$, négatif à gauche de $1$ : or $(x-1)^2$ est positif des deux côtés.
- **c)** On s'est trompé sur le signe du numérateur : en $1$, $2x+3$ vaut $5$, qui est positif.
- **d)** On a inversé les signes comme pour un dénominateur $1-x$, alors qu'un carré ne change pas de signe.

</details>

Avis : 

---

## 18. `cqc-asymptote-verticale-prob-c-moyenne-4` (séries BAC:A PRO:A PRO:C PRO:D PRO:E)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A, PRO:A.

**Remarque du relecteur :** LIMITE : pour la série A, limite d'une fonction avec racine carrée et notion d'asymptote verticale en haut du programme allégé.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $]2\,;+\infty[$ par $f(x)=\dfrac1{\sqrt{x-2}}$. Que vaut $\lim\limits_{x\to2^+}f(x)$, et quelle interprétation graphique en donne-t-on ?

- a) La limite vaut $0$ ; la droite d'équation $y=0$ est asymptote horizontale
- b) La limite vaut $+\infty$ ; la droite d'équation $y=2$ est asymptote horizontale
- c) La limite vaut $-\infty$ ; la droite d'équation $x=2$ est asymptote verticale
- d) La limite vaut $+\infty$ ; la droite d'équation $x=2$ est asymptote verticale

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour $x>2$, $x-2>0$ et $\sqrt{x-2}\to0^+$ quand $x\to2^+$ : l'inverse d'un nombre positif qui tend vers $0$ tend vers $+\infty$. La courbe admet alors une asymptote verticale.

### Corrigé

Quand $x\to2^+$, $x-2\to0^+$, donc $\sqrt{x-2}\to0^+$ et
$$\lim_{x\to2^+}f(x)=+\infty.$$
La droite d'équation $x=2$ est asymptote verticale à la courbe de $f$ (la fonction n'est définie que pour $x>2$ : on n'étudie que la limite à droite).

### Pourquoi les autres réponses sont fausses

- **a)** On a calculé la limite de $\sqrt{x-2}$, qui vaut $0$, en oubliant de prendre l'inverse.
- **b)** La limite est juste, mais une limite infinie en $2$ donne une asymptote verticale $x=2$, pas une asymptote horizontale.
- **c)** Une racine carrée est toujours positive : $\sqrt{x-2}$ tend vers $0^+$, donc la limite est $+\infty$ et non $-\infty$.

</details>

Avis : 

---

## 19. `cqc-barycentre-prob-c-faible-0` (séries BAC:TI PRO:C PRO:D PRO:E)

**Énoncé :**

Dans un repère du plan, on donne $A(1\,;2)$ et $B(6\,;7)$. Quelles sont les coordonnées du barycentre $G$ des points pondérés $(A\,;2)$ et $(B\,;3)$ ?

- a) $G(3\,;4)$
- b) $G(4\,;5)$
- c) $G\left(\dfrac72\,;\dfrac92\right)$
- d) $G(20\,;25)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Le barycentre de $(A,\alpha)$ et $(B,\beta)$ avec $\alpha+\beta\neq0$ a pour coordonnées $x_G=\dfrac{\alpha x_A+\beta x_B}{\alpha+\beta}$ et $y_G=\dfrac{\alpha y_A+\beta y_B}{\alpha+\beta}$.

### Corrigé

$\alpha+\beta=5$. $x_G=\dfrac{2\times1+3\times6}{5}=\dfrac{20}5=4$ et $y_G=\dfrac{2\times2+3\times7}{5}=\dfrac{25}5=5$. Donc $G(4\,;5)$.

### Pourquoi les autres réponses sont fausses

- **a)** $(3\,;4)$ : on a interverti les coefficients, en affectant $3$ à $A$ et $2$ à $B$.
- **c)** $\left(\dfrac72\,;\dfrac92\right)$ : c'est le milieu de $[AB]$, on n'a pas tenu compte des coefficients.
- **d)** $(20\,;25)$ : on a oublié de diviser par la somme des coefficients $\alpha+\beta=5$.

</details>

Avis : 

---

## 20. `cqc-barycentre-prob-c-moyenne-3` (séries BAC:TI PRO:C PRO:D PRO:E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $ABC$ un triangle, $I$ le milieu de $[BC]$ et $G$ le barycentre de $(A,2)$, $(B,1)$ et $(C,1)$. Quelle relation vérifie le point $G$ ?

- a) $\overrightarrow{AG}=\dfrac23\overrightarrow{AI}$
- b) $\overrightarrow{AG}=\dfrac13\overrightarrow{AI}$
- c) $\overrightarrow{AG}=\dfrac12\overrightarrow{AI}$
- d) $\overrightarrow{AG}=\dfrac14\overrightarrow{AI}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Propriété d'associativité : on peut remplacer des points pondérés par leur barycentre partiel affecté de la somme de leurs coefficients sans changer le barycentre. Ici $I$ est le barycentre de $(B,1)$ et $(C,1)$.

### Corrigé

$I$ est le milieu de $[BC]$, donc le barycentre de $(B,1)$ et $(C,1)$. Par associativité, $G$ est le barycentre de $(A,2)$ et $(I,1+1)=(I,2)$. Les deux coefficients sont égaux : $G$ est l'isobarycentre de $A$ et $I$, c'est-à-dire le milieu de $[AI]$, soit $\overrightarrow{AG}=\dfrac12\overrightarrow{AI}$.
Vérification avec $A(0\,;0)$, $B(4\,;0)$, $C(0\,;4)$ : $I(2\,;2)$ et $G\left(\dfrac{0+4+0}4\,;\dfrac{0+0+4}4\right)=(1\,;1)$, qui est bien le milieu de $[AI]$.

### Pourquoi les autres réponses sont fausses

- **a)** C'est la position du centre de gravité du triangle (isobarycentre de $A$, $B$, $C$) : on a oublié que $A$ est affecté du coefficient $2$.
- **b)** On a affecté $I$ du coefficient $1$ au lieu de $1+1=2$ : $G$ serait le barycentre de $(A,2)$ et $(I,1)$.
- **d)** On a divisé le seul coefficient de $B$ par la somme $4$ au lieu de regrouper $B$ et $C$ en $(I,2)$.

</details>

Avis : 

---

## 21. `cqc-calcul-d-image-prob-a-moyenne-2` (séries BAC:A PRO:A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb R$ par $f(x)=x^2-3x+2$. Que vaut $f(-1)$ ?

- a) $6$
- b) $4$
- c) $0$
- d) $-2$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On remplace $x$ par la valeur, en plaçant les nombres négatifs entre parenthèses : $(-1)^2=1$ et $-3\times(-1)=3$.

### Corrigé

$f(-1)=(-1)^2-3\times(-1)+2=1+3+2=6$.

(Pour mémoire : $f(0)=2$ et $f\left(\dfrac12\right)=\dfrac14-\dfrac32+2=\dfrac34$.)

### Pourquoi les autres réponses sont fausses

- **b)** On a écrit $(-1)^2=-1$ : $-1+3+2=4$.
- **c)** On a écrit $-3\times(-1)=-3$ : $1-3+2=0$.
- **d)** Les deux erreurs de signe à la fois : $-1-3+2=-2$.

</details>

Avis : 

---

## 22. `cqc-calcul-d-image-prob-a-moyenne-3` (séries BAC:A PRO:A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie par $f(x)=\dfrac{x+1}{x-2}$. Quelle proposition donne à la fois la valeur de $f(0)$ et l'ensemble de définition $D_f$ de $f$ ?

- a) $f(0)=-2$ et $D_f=\mathbb R\setminus\{2\}$
- b) $f(0)=-\dfrac12$ et $D_f=\mathbb R\setminus\{-1\}$
- c) $f(0)=\dfrac12$ et $D_f=\mathbb R\setminus\{2\}$
- d) $f(0)=-\dfrac12$ et $D_f=\mathbb R\setminus\{2\}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On remplace $x$ par la valeur. Un quotient n'existe que si son dénominateur ne s'annule pas : les valeurs qui annulent le dénominateur sont exclues de l'ensemble de définition.

### Corrigé

$f(0)=\dfrac{0+1}{0-2}=\dfrac1{-2}=-\dfrac12$ (de même $f(3)=\dfrac41=4$). Pour $x=2$, le dénominateur est nul : $f(2)$ n'existe pas ; $2$ est une valeur interdite et $D_f=\mathbb R\setminus\{2\}$.

### Pourquoi les autres réponses sont fausses

- **a)** On a renversé la fraction : $\dfrac{-2}{1}=-2$ au lieu de $\dfrac1{-2}$.
- **b)** On a exclu la valeur qui annule le numérateur ; or seul le dénominateur ne doit pas s'annuler ($f(-1)=0$ existe).
- **c)** Erreur de signe sur le dénominateur : $0-2=-2$, pas $2$.

</details>

Avis : 

---

## 23. `cqc-calcul-d-image-prob-a-moyenne-4` (séries BAC:A PRO:A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie par $f(x)=\sqrt{x+1}$. Quel est l'ensemble de définition $D_f$ de $f$ ?

- a) $]-1\,;+\infty[$
- b) $[-1\,;+\infty[$
- c) $[1\,;+\infty[$
- d) $]-\infty\,;-1]$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Une racine carrée n'existe que si le nombre sous le radical est positif ou nul : il faut $x+1\ge0$.

### Corrigé

$x+1\ge0\iff x\ge-1$, donc $D_f=[-1\,;+\infty[$. La borne $-1$ est incluse : $f(-1)=\sqrt0=0$. Par exemple $f(3)=\sqrt4=2$ et $f(8)=\sqrt9=3$.

### Pourquoi les autres réponses sont fausses

- **a)** On a exclu $-1$, alors que $\sqrt0=0$ existe : l'inégalité est large.
- **c)** Erreur de signe en résolvant $x+1\ge0$.
- **d)** On a renversé l'inégalité : ce sont les $x$ pour lesquels $x+1\le0$.

</details>

Avis : 

---

## 24. `cqc-calcul-d-image-prob-a-moyenne-5` (séries BAC:A PRO:A)

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb R$ par $f(x)=3x-1$. Quel est l'antécédent de $8$ par $f$ ?

- a) $23$
- b) $\dfrac73$
- c) $3$
- d) $9$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Chercher l'antécédent $a$ de $8$, c'est résoudre l'équation $f(a)=8$ (et non calculer $f(8)$, qui est l'image de $8$).

### Corrigé

$3a-1=8\iff3a=9\iff a=3$. Le réel $3$ est l'**antécédent** de $8$ par $f$ : vérification, $f(3)=9-1=8$.

### Pourquoi les autres réponses sont fausses

- **a)** C'est l'image de $8$ : $f(8)=24-1=23$ ; confusion entre image et antécédent.
- **b)** Erreur de signe en isolant $3a$ : $3a=8-1$ au lieu de $3a=8+1$.
- **d)** On s'est arrêté à $3a=9$ sans diviser par $3$.

</details>

Avis : 

---

## 25. `cqc-changement-de-base-tle-c-faible-0` (séries BAC:C BAC:E PRO:C)

**Série(s) retirée(s) par analogie avec vos avis :** PRO:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans $\mathbb{R}^2$ muni de la base canonique, on considère $\vec e_1=(1\,;2)$ et $\vec e_2=(0\,;1)$. Quelles sont les coordonnées du vecteur $\vec u=(3\,;8)$ dans la base $B'=(\vec e_1,\vec e_2)$ ?

- a) $(3\,;2)$
- b) $(2\,;3)$
- c) $(3\,;14)$
- d) $(3\,;5)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Trouver les coordonnées $(a\,;b)$ de $\vec u$ dans la base $(\vec e_1,\vec e_2)$, c'est résoudre $\vec u=a\vec e_1+b\vec e_2$, ce qui revient à un petit système linéaire.

### Corrigé

$a\vec e_1+b\vec e_2=(a\,;2a+b)$. Il faut donc $a=3$ et $2a+b=8$, soit $b=2$.

Dans $B'$, $\vec u$ a pour coordonnées $(3\,;2)$. Vérification : $3(1\,;2)+2(0\,;1)=(3\,;8)$.

### Pourquoi les autres réponses sont fausses

- **b)** Bonnes valeurs mais dans le mauvais ordre : la première coordonnée est celle de $\vec e_1$.
- **c)** Sens inversé : on a calculé $3\vec e_1+8\vec e_2=(3\,;14)$, comme si $(3\,;8)$ étaient déjà les coordonnées dans $B'$.
- **d)** On a oublié le coefficient $2$ dans $2a+b=8$ : $b=8-3$.

</details>

Avis : 

---

## 26. `cqc-changement-de-base-tle-c-moyenne-2` (séries BAC:C BAC:E PRO:C)

**Série(s) retirée(s) par analogie avec vos avis :** PRO:C.

**Remarque du relecteur :** LIMITE : changement de base dans R^2 (vocabulaire « base canonique »), limite haute du programme de Première C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans $\mathbb{R}^2$ muni de la base canonique $B$, on considère $\vec e_1'=(1\,;1)$ et $\vec e_2'=(-1\,;2)$, qui forment une base $B'$. Le vecteur $\vec u$ a pour coordonnées $(4\,;5)$ dans $B$. Quelles sont ses coordonnées dans $B'$ ?

- a) $(-1\,;14)$
- b) $(13\,;1)$
- c) $(1\,;3)$
- d) $\left(\dfrac{13}3\,;\dfrac13\right)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Les coordonnées $(a\,;b)$ de $\vec u$ dans $B'$ vérifient $\vec u=a\vec e_1'+b\vec e_2'$ : on égalise les coordonnées et on résout le système obtenu. Avec la matrice de passage $P$ de $B$ à $B'$, cela s'écrit $X=PX'$, donc $X'=P^{-1}X$ avec $P^{-1}=\dfrac1{ad-bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}$.

### Corrigé

$\det(\vec e_1',\vec e_2')=1\times2-1\times(-1)=3\neq0$ : c'est bien une base. On résout $a\vec e_1'+b\vec e_2'=\vec u$ :
$$\begin{cases}a-b=4\\a+2b=5\end{cases}$$
En soustrayant : $3b=1$, donc $b=\dfrac13$ et $a=4+\dfrac13=\dfrac{13}3$. (Avec la matrice : $P=\begin{pmatrix}1&-1\\1&2\end{pmatrix}$, $P^{-1}=\dfrac13\begin{pmatrix}2&1\\-1&1\end{pmatrix}$ et $P^{-1}\begin{pmatrix}4\\5\end{pmatrix}=\dfrac13\begin{pmatrix}13\\1\end{pmatrix}$.)
Vérification : $\dfrac{13}{3}(1\,;1)+\dfrac13(-1\,;2)=\left(\dfrac{12}3\,;\dfrac{15}3\right)=(4\,;5)$.

### Pourquoi les autres réponses sont fausses

- **a)** Sens inversé : on a calculé $4\vec e_1'+5\vec e_2'$ (soit $PX$ au lieu de $P^{-1}X$).
- **b)** On a oublié de diviser par le déterminant $3$.
- **c)** Erreur de signes dans l'inverse de $P$ ; on vérifie que $1\vec e_1'+3\vec e_2'=(-2\,;7)\neq(4\,;5)$.

</details>

Avis : 

---

## 27. `cqc-changement-de-base-tle-c-moyenne-3` (séries BAC:C BAC:E PRO:C)

**Série(s) retirée(s) par analogie avec vos avis :** PRO:C.

**Remarque du relecteur :** LIMITE : matrice d'un endomorphisme dans une nouvelle base (changement de base), haut du programme de Première C ; « endomorphisme » à vérifier dans le manuel de Première

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ l'endomorphisme de $\mathbb{R}^2$ de matrice $A=\begin{pmatrix}1&2\\0&3\end{pmatrix}$ dans la base canonique. On pose $\vec e_1=(1\,;0)$ et $\vec e_2=(1\,;1)$, qui forment une base de $\mathbb{R}^2$. Quelle est la matrice de $f$ dans la base $(\vec e_1,\vec e_2)$ ?

- a) $\begin{pmatrix}1&3\\0&3\end{pmatrix}$
- b) $\begin{pmatrix}1&0\\0&3\end{pmatrix}$
- c) $\begin{pmatrix}1&4\\0&3\end{pmatrix}$
- d) $\begin{pmatrix}3&0\\0&1\end{pmatrix}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Les colonnes de la matrice de $f$ dans une base sont les coordonnées, dans cette même base, des images des vecteurs de la base. Avec la matrice de passage $P$ de l'ancienne base à la nouvelle, cette matrice vaut aussi $A'=P^{-1}AP$.

### Corrigé

$\det(\vec e_1,\vec e_2)=1\times1-1\times0=1\neq0$ : c'est une base.

$f(\vec e_1)=A\begin{pmatrix}1\\0\end{pmatrix}=\begin{pmatrix}1\\0\end{pmatrix}=\vec e_1$, de coordonnées $(1\,;0)$ dans la nouvelle base ; $f(\vec e_2)=A\begin{pmatrix}1\\1\end{pmatrix}=\begin{pmatrix}3\\3\end{pmatrix}=3\vec e_2$, de coordonnées $(0\,;3)$.
$$A'=\begin{pmatrix}1&0\\0&3\end{pmatrix}.$$
Vérification avec $P=\begin{pmatrix}1&1\\0&1\end{pmatrix}$, $P^{-1}=\begin{pmatrix}1&-1\\0&1\end{pmatrix}$ : $AP=\begin{pmatrix}1&3\\0&3\end{pmatrix}$ et $P^{-1}(AP)=\begin{pmatrix}1&0\\0&3\end{pmatrix}$.

### Pourquoi les autres réponses sont fausses

- **a)** C'est $AP$ : les images $f(\vec e_1)$ et $f(\vec e_2)$ écrites dans la base canonique, sans les exprimer dans la nouvelle base (oubli de $P^{-1}$).
- **c)** C'est $PAP^{-1}$ : formule de changement de base appliquée à l'envers.
- **d)** Colonnes dans le mauvais ordre : la première colonne correspond à $f(\vec e_1)=\vec e_1$.

</details>

Avis : 

---

## 28. `cqc-changement-de-base-tle-c-moyenne-4` (séries BAC:C BAC:E PRO:C)

**Série(s) retirée(s) par analogie avec vos avis :** PRO:C.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans $\mathbb{R}^3$ muni de la base canonique, on considère $\vec e_1=(1\,;1\,;0)$, $\vec e_2=(0\,;1\,;1)$ et $\vec e_3=(1\,;0\,;1)$, qui forment une base $B'$ de $\mathbb{R}^3$. Quelles sont les coordonnées du vecteur $\vec v=(2\,;3\,;1)$ dans $B'$ ?

- a) $(2\,;3\,;1)$
- b) $(5\,;4\,;3)$
- c) $(2\,;1\,;0)$
- d) $(0\,;1\,;2)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Les coordonnées de $\vec v$ dans $B'$ sont les réels $(a,b,c)$ tels que $\vec v=a\vec e_1+b\vec e_2+c\vec e_3$, solution d'un système $3\times3$.

### Corrigé

On résout $a\vec e_1+b\vec e_2+c\vec e_3=\vec v$, c'est-à-dire
$$\begin{cases}a+c=2\\a+b=3\\b+c=1\end{cases}$$
En additionnant : $2(a+b+c)=6$, donc $a+b+c=3$. Alors $b=3-(a+c)=1$, $c=3-(a+b)=0$ et $a=3-(b+c)=2$.

Dans $B'$, $\vec v$ a pour coordonnées $(2\,;1\,;0)$. Vérification : $2(1\,;1\,;0)+1(0\,;1\,;1)+0(1\,;0\,;1)=(2\,;3\,;1)$.

### Pourquoi les autres réponses sont fausses

- **a)** Ce sont les coordonnées dans la base canonique : $2\vec e_1+3\vec e_2+\vec e_3=(3\,;5\,;4)\neq\vec v$.
- **b)** On a pris $a+b+c=6$ en oubliant de diviser la somme des équations par $2$.
- **d)** Bonnes valeurs dans l'ordre inverse : $0\vec e_1+1\vec e_2+2\vec e_3=(2\,;1\,;3)\neq\vec v$.

</details>

Avis : 

---

## 29. `cqc-combinaison-lineaire-elevee-0` (séries BAC:C BAC:E PRO:C PRO:E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

L'espace est muni d'un repère $(O\,;\,\vec\imath\,,\,\vec\jmath\,,\,\vec k)$. On considère les vecteurs $\vec u(1\,;\,2\,;\,-1)$, $\vec v(2\,;\,-1\,;\,3)$ et $\vec w(m\,;\,8\,;\,-9)$, où $m$ est un réel. Pour quelle valeur de $m$ existe-t-il des réels $a$ et $b$ tels que $\vec w=a\vec u+b\vec v$ ?

- a) $m=-1$
- b) $m=7$
- c) $m=1$
- d) $m=4$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Écrire $\vec w=a\vec u+b\vec v$ revient à égaliser les coordonnées de $\vec w$ à celles de $a\vec u+b\vec v$ : on obtient trois égalités, une par coordonnée, pour seulement deux inconnues $a$ et $b$. On résout d'abord le sous-système formé par les deux égalités qui ne contiennent pas le paramètre, puis on reporte les valeurs de $a$ et $b$ trouvées dans la troisième égalité : la valeur du paramètre qui la rend vraie est celle qui rend $\vec w$ combinaison linéaire de $\vec u$ et $\vec v$ (les trois vecteurs sont alors coplanaires).

### Corrigé

L'égalité $\vec w=a\vec u+b\vec v$ équivaut au système :
$$\begin{cases} a+2b=m & (1)\\ 2a-b=8 & (2) \\ -a+3b=-9 & (3)\end{cases}$$

Les équations (2) et (3) ne contiennent pas $m$ : on les résout d'abord. De (2) : $b=2a-8$. En reportant dans (3) : $-a+3(2a-8)=-9 \Rightarrow 5a=15 \Rightarrow a=3$. D'où $b=2\times3-8=-2$.

On reporte dans (1) : $m=a+2b=3+2\times(-2)=-1$.

Vérification : $3\vec u-2\vec v=(3-4\,;\,6+2\,;\,-3-6)=(-1\,;\,8\,;\,-9)$. La valeur cherchée est $m=-1$, avec $\vec w=3\vec u-2\vec v$.

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de signe sur $b$ : avec $b=2$, on obtient $3+4=7$.
- **c)** On a oublié le coefficient $2$ de $b$ dans l'équation (1) : $m=a+b=1$.
- **d)** On a pris les coordonnées de $\vec u$ et $\vec v$ dans le désordre : $m=2a+b=4$.

</details>

Avis : 

---

## 30. `cqc-combinaison-lineaire-faible-1` (séries BAC:C BAC:E PRO:C PRO:E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Le plan est muni d'un repère $(O\,;\,\vec\imath\,,\,\vec\jmath)$. On donne les points $A(1\,;\,2)$, $B(5\,;\,-4)$ et $C(-1\,;\,5)$, qui sont alignés.

Quel est le réel $k$ tel que $\vec{AC}=k\vec{AB}$ ?

- a) $-2$
- b) $-\dfrac12$
- c) $\dfrac12$
- d) $2$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Trois points $A$, $B$, $C$ sont alignés si et seulement si les vecteurs $\vec{AB}$ et $\vec{AC}$ sont colinéaires, c'est-à-dire s'il existe un réel $k$ tel que $\vec{AC}=k\vec{AB}$. On calcule les coordonnées des deux vecteurs, puis on vérifie que le même réel $k$ convient pour chacune des deux coordonnées.

### Corrigé

$\vec{AB}$ a pour coordonnées $(5-1\,;\,-4-2)=(4\,;\,-6)$ et $\vec{AC}$ a pour coordonnées $(-1-1\,;\,5-2)=(-2\,;\,3)$.

Sur la première coordonnée, $-2=4k$ donne $k=-\dfrac12$ ; sur la seconde, $3=-6k$ donne aussi $k=-\dfrac12$. Donc $\vec{AC}=-\dfrac12\vec{AB}$ : les vecteurs sont colinéaires et les points $A$, $B$, $C$ sont bien alignés.

### Pourquoi les autres réponses sont fausses

- **a)** $-2$ : c'est le réel $k'$ tel que $\vec{AB}=k'\vec{AC}$ ; on a inversé le rôle des deux vecteurs.
- **c)** $\dfrac12$ : le signe est oublié ; $\dfrac12\vec{AB}$ a pour coordonnées $(2\,;\,-3)$ et non $(-2\,;\,3)$.
- **d)** $2$ : on a inversé les vecteurs et oublié le signe.

</details>

Avis : 

---

## 31. `cqc-combinaison-lineaire-moyenne-0` (séries BAC:C BAC:E PRO:C PRO:E)

**Énoncé :**

L'espace est muni d'un repère $(O\,;\,\vec\imath\,,\,\vec\jmath\,,\,\vec k)$. On donne les points $A(1\,;\,0\,;\,2)$, $B(4\,;\,3\,;\,-1)$ et $C(-2\,;\,6\,;\,5)$. On définit le point $G$ par la relation vectorielle :
$$\vec{AG}=\frac13\vec{AB}+\frac23\vec{AC}$$

Déterminer les coordonnées du point $G$.

- a) $(-1\,;\,5\,;\,1)$
- b) $(2\,;\,4\,;\,1)$
- c) $(0\,;\,5\,;\,3)$
- d) $(2\,;\,-5\,;\,1)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour obtenir un point $G$ défini par $\vec{AG}=\alpha\vec{AB}+\beta\vec{AC}$, on calcule les coordonnées de $\vec{AB}$ et $\vec{AC}$, on en déduit celles de $\vec{AG}$ coordonnée par coordonnée, puis on ajoute celles de $\vec{AG}$ à celles de $A$ (car $\vec{AG}=\vec{OG}-\vec{OA}$).

### Corrigé

$\vec{AB}=(3\,;\,3\,;\,-3)$ et $\vec{AC}=(-3\,;\,6\,;\,3)$.

$\vec{AG}=\frac13\vec{AB}+\frac23\vec{AC}$ a pour coordonnées $(1-2\,;\,1+4\,;\,-1+2)=(-1\,;\,5\,;\,1)$.

$$G=(1+(-1)\,;\,0+5\,;\,2+1)=(0\,;\,5\,;\,3).$$

### Pourquoi les autres réponses sont fausses

- **a)** $(-1\,;\,5\,;\,1)$ : ce sont les coordonnées du vecteur $\vec{AG}$ ; on a oublié d'ajouter celles de $A$.
- **b)** $(2\,;\,4\,;\,1)$ : on a échangé les coefficients $\frac13$ et $\frac23$.
- **d)** $(2\,;\,-5\,;\,1)$ : on a calculé $A-\vec{AG}$ au lieu de $A+\vec{AG}$.

</details>

Avis : 

---

## 32. `cqc-combinaison-lineaire-moyenne-2` (séries BAC:C BAC:E PRO:C PRO:E)

**Remarque du relecteur :** VOCABULAIRE : parler de coordonnées « dans la base (i, j) » plutôt que « dans le repère (O ; i, j) » pour un vecteur.

**Énoncé :**

Soit $f$ une application linéaire du plan telle que $f(\vec\imath)=2\vec\imath-\vec\jmath$ et $f(\vec\jmath)=-\vec\imath+3\vec\jmath$. On considère le vecteur $\vec w=4\vec\imath-3\vec\jmath$.

Déterminer les coordonnées de $f(\vec w)$ dans le repère $(O\,;\,\vec\imath\,,\,\vec\jmath)$.

- a) $(11\,;\,-13)$
- b) $(5\,;\,5)$
- c) $(5\,;\,-13)$
- d) $(11\,;\,5)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Une application linéaire $f$ vérifie $f(\alpha\vec u+\beta\vec v)=\alpha f(\vec u)+\beta f(\vec v)$. Pour calculer l'image d'un vecteur exprimé à l'aide des vecteurs de base dont on connaît les images, il suffit d'appliquer cette propriété.

### Corrigé

$$f(\vec w)=4f(\vec\imath)-3f(\vec\jmath)=(8\vec\imath-4\vec\jmath)+(3\vec\imath-9\vec\jmath)=11\vec\imath-13\vec\jmath.$$
Les coordonnées de $f(\vec w)$ sont donc $(11\,;\,-13)$.

### Pourquoi les autres réponses sont fausses

- **b)** $(5\,;\,5)$ : on a calculé $4f(\vec\imath)+3f(\vec\jmath)$ en oubliant le signe du coefficient $-3$.
- **c)** $(5\,;\,-13)$ : erreur de signe sur $(-3)\times(-1)$, compté $-3$ au lieu de $+3$ dans la première coordonnée.
- **d)** $(11\,;\,5)$ : erreur de signe sur $(-3)\times 3$, compté $+9$ au lieu de $-9$ dans la seconde coordonnée.

</details>

Avis : 

---

## 33. `cqc-combinaisons-faible-1` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PRO:A PRO:C PRO:D PRO:E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Quelle est la valeur exacte du coefficient binomial $\binom{15}{13}$ ?

- a) $210$
- b) $455$
- c) $105$
- d) $30$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour $0\le k\le n$, on a la propriété de symétrie $\binom{n}{k}=\binom{n}{n-k}$ : choisir les $k$ éléments retenus revient à choisir les $n-k$ éléments écartés. Elle permet de remplacer un calcul portant sur un grand $k$ par un calcul portant sur un petit $n-k$.

### Corrigé

Ici $n-k=15-13=2$, donc $$\binom{15}{13}=\binom{15}{2}=\dfrac{15\times14}{2}=105.$$

### Pourquoi les autres réponses sont fausses

- **a)** $210$ : on a calculé $15\times14$ en oubliant de diviser par $2!$.
- **b)** $455$ : c'est $\binom{15}{3}$ ; on s'est trompé sur $n-k$, qui vaut $2$ et non $3$.
- **d)** $30$ : $15\times2$ confond le coefficient binomial avec un simple produit.

</details>

Avis : 

---

## 34. `cqc-combinaisons-moyenne-0` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PRO:A PRO:C PRO:D PRO:E)

**Énoncé :**

Le conseil de gestion d'un établissement doit compter 5 membres, choisis parmi 8 enseignants et 6 parents d'élèves candidats. On souhaite que ce conseil comporte au moins 3 enseignants. Combien de compositions différentes du conseil sont possibles ?

- a) $1316$
- b) $840$
- c) $1260$
- d) $3080$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Avec une contrainte « au moins », on décompose en cas exclusifs selon le nombre exact d'éléments de la catégorie retenus, on dénombre chaque cas par un produit de combinaisons, puis on additionne.

### Corrigé

« Au moins 3 enseignants » parmi 5 membres : exactement 3, 4 ou 5 enseignants.

- 3 enseignants et 2 parents : $\binom{8}{3}\binom{6}{2}=56\times15=840$
- 4 enseignants et 1 parent : $\binom{8}{4}\binom{6}{1}=70\times6=420$
- 5 enseignants et 0 parent : $\binom{8}{5}\binom{6}{0}=56\times1=56$

Total : $$840+420+56=1316.$$

### Pourquoi les autres réponses sont fausses

- **b)** $840$ : seul le cas « exactement 3 enseignants » a été compté.
- **c)** $1260$ : on a oublié le cas où les 5 membres sont des enseignants.
- **d)** $3080$ : $\binom{8}{3}\binom{11}{2}$ (3 enseignants puis 2 personnes quelconques) compte plusieurs fois les mêmes conseils.

</details>

Avis : 

---

## 35. `cqc-convergence-prob-c-moyenne-3` (séries BAC:TI PRO:C PRO:E)

**Remarque du relecteur :** LIMITE : la limite d'une suite géométrique de raison comprise entre -1 et 1 est en haut du programme de Première C/E ; préciser « pour tout entier naturel n ».

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Pour tout entier $n$, on pose $S_n=1+\dfrac12+\dfrac14+\cdots+\dfrac1{2^n}$. Quelle est l'expression de $S_n$ en fonction de $n$, et quelle est la limite de $S_n$ ?

- a) $S_n=2-\dfrac1{2^{n-1}}$ et $\lim S_n=2$
- b) $S_n=1-\dfrac1{2^{n+1}}$ et $\lim S_n=1$
- c) $S_n=2-\dfrac1{2^n}$ et $\lim S_n=2$
- d) $S_n=2-\dfrac1{2^{n+1}}$ et $\lim S_n=2$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

$S_n$ est la somme de $n+1$ termes consécutifs d'une suite géométrique de premier terme $1$ et de raison $q=\dfrac12$ : $S_n=\text{premier terme}\times\dfrac{1-q^{n+1}}{1-q}$. Comme $-1<q<1$, $q^{n+1}\to0$.

### Corrigé

$$S_n=1\times\dfrac{1-\left(\frac12\right)^{n+1}}{1-\frac12}=2\left(1-\dfrac1{2^{n+1}}\right)=2-\dfrac1{2^n}.$$
Comme $\dfrac1{2^n}\to0$, $S_n\to2$. Contrôle : $S_0=1=2-1$ et $S_1=\dfrac32=2-\dfrac12$.

### Pourquoi les autres réponses sont fausses

- **a)** $S_n=2-\dfrac1{2^{n-1}}$ : on a compté $n$ termes au lieu de $n+1$ (exposant $n$ au lieu de $n+1$ dans la formule) ; pour $n=0$ on trouverait $0$ au lieu de $1$.
- **b)** $S_n=1-\dfrac1{2^{n+1}}$ : on a oublié de diviser par $1-q=\dfrac12$.
- **d)** $S_n=2-\dfrac1{2^{n+1}}$ : on a appliqué le facteur $2$ au seul terme $1$ et pas à $\left(\frac12\right)^{n+1}$ ; pour $n=0$ on trouverait $\dfrac32$ au lieu de $1$.

</details>

Avis : 

---

## 36. `cqc-discriminant-faible-0` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PRO:A PRO:C PRO:D PRO:E)

**Remarque du relecteur :** VOCABULAIRE : un « coût » défini sur tout R avec un « paramètre de réglage » quelconque est un contexte artificiel ; le contexte n'est d'aucune utilité pour répondre.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Une entreprise modélise le coût de fabrication (en milliers de francs CFA) d'une pièce mécanique par la fonction $C$ définie sur $\mathbb{R}$ par $C(x) = 3x^2 - 6x + 10$, où $x$ désigne un paramètre de réglage de la machine. Laquelle des affirmations suivantes est exacte ?

- a) $\Delta=-84<0$ et $a>0$, donc $C(x)>0$ pour tout réel $x$
- b) $\Delta=156>0$, donc $C(x)$ change de signe sur $\mathbb{R}$
- c) $\Delta=-84<0$, donc $C(x)<0$ pour tout réel $x$
- d) $C(x)\geq 10$ pour tout réel $x$, la valeur $10$ étant atteinte en $x=0$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour un trinôme $ax^2+bx+c$ (avec $a\neq 0$), si le discriminant $\Delta = b^2-4ac$ est strictement négatif, le trinôme ne s'annule jamais : il garde alors un signe constant sur $\mathbb{R}$, celui de son coefficient dominant $a$.

### Corrigé

Ici $a=3$, $b=-6$, $c=10$.

$\Delta = (-6)^2 - 4\times 3\times 10 = 36 - 120 = -84$

Comme $\Delta = -84 < 0$, le trinôme $C(x)$ ne s'annule jamais et garde un signe constant sur $\mathbb{R}$. Comme $a=3>0$, ce signe constant est positif : $C(x) > 0$ pour tout réel $x$.

Vérification par la forme canonique : $C(x) = 3(x^2-2x) + 10 = 3\left[(x-1)^2 - 1\right] + 10 = 3(x-1)^2 + 7$. Comme $(x-1)^2 \geq 0$, on a $C(x) \geq 7 > 0$ pour tout réel $x$.

La bonne réponse est **a)**.

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de signe dans $-4ac$ : on a calculé $36+120$ au lieu de $36-120$.
- **c)** Le discriminant est juste, mais lorsque $\Delta<0$ le trinôme a le signe de $a=3$, donc il est positif, pas négatif.
- **d)** Le terme constant $10$ n'est pas le minimum : $C(1)=7<10$ ; le minimum $7$ se lit sur la forme canonique.

</details>

Avis : 

---

## 37. `cqc-discriminant-faible-1` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PRO:A PRO:C PRO:D PRO:E)

**Énoncé :**

On considère l'équation du second degré, d'inconnue réelle $x$ : $5x^2 - 2x + 3 = 0$. Combien de solutions réelles admet-elle ?

- a) Deux solutions : $1$ et $-\dfrac{3}{5}$
- b) Une solution double : $\dfrac{1}{5}$
- c) Aucune solution réelle
- d) Deux solutions : $-1$ et $\dfrac{3}{5}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour une équation $ax^2+bx+c=0$ (avec $a\neq 0$), le signe du discriminant $\Delta=b^2-4ac$ suffit à connaître le nombre de solutions réelles, sans les calculer : deux solutions distinctes si $\Delta>0$, une solution double si $\Delta=0$, aucune solution réelle si $\Delta<0$.

### Corrigé

Ici $a=5$, $b=-2$, $c=3$.

$\Delta = (-2)^2 - 4\times 5\times 3 = 4 - 60 = -56$

Comme $\Delta = -56 < 0$, l'équation $5x^2-2x+3=0$ n'admet aucune solution réelle.

Vérification : le coefficient dominant $a=5$ est positif et $\Delta<0$, donc le trinôme $5x^2-2x+3$ reste strictement positif sur $\mathbb{R}$ : il ne s'annule jamais.

La bonne réponse est **c)**.

### Pourquoi les autres réponses sont fausses

- **a)** Ce sont les solutions de $5x^2-2x-3=0$ : le signe de $c$ a été changé, ce qui donne $\Delta=4+60=64$.
- **b)** $x=\dfrac{1}{5}=-\dfrac{b}{2a}$ n'est solution double que si $\Delta=0$, ce qui n'est pas le cas ici.
- **d)** Ce sont les solutions de $5x^2+2x-3=0$ : erreurs de signe sur $b$ et sur $c$.

</details>

Avis : 

---

## 38. `cqc-discriminant-moyenne-0` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PRO:A PRO:C PRO:D PRO:E)

**Remarque du relecteur :** VOCABULAIRE : contexte irréaliste, une quantité d'objets vendus définie sur R (valeurs négatives, non entières) et une marge toujours négative ; prendre un contexte neutre ou définir M sur [0;+inf[ avec un trinôme cohérent.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Un artisan modélise sa marge journalière (en milliers de francs CFA) en fonction de la quantité $x$ d'objets vendus par la fonction $M$ définie sur $\mathbb{R}$ par $M(x) = -3x^2 + 2x - 5$. Laquelle des affirmations suivantes est exacte ?

- a) $\Delta=64>0$, donc $M(x)$ change de signe sur $\mathbb{R}$
- b) $\Delta=-56<0$ et $a<0$, donc $M(x)<0$ pour tout réel $x$
- c) $\Delta=-56<0$, donc $M(x)>0$ pour tout réel $x$
- d) $M(x)\leq -5$ pour tout réel $x$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour un trinôme $ax^2+bx+c$ (avec $a\neq 0$), si $\Delta=b^2-4ac$ est strictement négatif, le trinôme garde un signe constant sur $\mathbb{R}$ : ce signe est celui du coefficient dominant $a$, que celui-ci soit positif ou négatif.

### Corrigé

Ici $a=-3$, $b=2$, $c=-5$.

$\Delta = 2^2 - 4\times(-3)\times(-5) = 4 - 60 = -56$

Comme $\Delta = -56 < 0$, le trinôme $M(x)$ ne s'annule jamais et garde un signe constant sur $\mathbb{R}$. Comme $a=-3<0$, ce signe constant est négatif : $M(x) < 0$ pour tout réel $x$.

Vérification par la forme canonique : $M(x) = -3\left(x-\dfrac{1}{3}\right)^2 - \dfrac{14}{3}$, donc $M(x) \leq -\dfrac{14}{3} < 0$ pour tout réel $x$.

La bonne réponse est **b)**.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe : $4\times(-3)\times(-5)=60$ est positif, il faut donc le soustraire, ce qui donne $4-60$ et non $4+60$.
- **c)** Le discriminant est juste, mais le signe constant est celui de $a=-3$, donc négatif.
- **d)** Le terme constant $-5$ n'est pas le maximum : $M\left(\dfrac{1}{3}\right)=-\dfrac{14}{3}>-5$.

</details>

Avis : 

---

## 39. `cqc-discriminant-moyenne-2` (séries BAC:A BAC:C BAC:D BAC:E BAC:TI PRO:A PRO:C PRO:D PRO:E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans le plan muni d'un repère, on considère la parabole $(P)$ d'équation $y = x^2 - x - 1$ et la droite $(D)$ d'équation $y = 3x - 4$. Laquelle des affirmations suivantes sur les points communs à $(D)$ et à $(P)$ est exacte ?

- a) Elles n'ont aucun point commun
- b) Elles ont un seul point commun, d'abscisse $2$
- c) Elles ont deux points communs, d'abscisses $-1$ et $-3$
- d) Elles ont deux points communs, d'abscisses $1$ et $3$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Les points d'intersection entre une droite et une parabole sont les points dont l'abscisse vérifie l'équation obtenue en égalant les deux expressions de $y$. Cette équation est du second degré : le signe de son discriminant $\Delta$ donne le nombre de points d'intersection (deux points si $\Delta>0$, un seul si $\Delta=0$, aucun si $\Delta<0$), et ses solutions en donnent les abscisses.

### Corrigé

Un point appartient à la fois à $(D)$ et à $(P)$ si et seulement si son abscisse $x$ vérifie $x^2 - x - 1 = 3x - 4$, ce qui donne, après regroupement, $x^2 - 4x + 3 = 0$.

Ici $a=1$, $b=-4$, $c=3$.

$\Delta = (-4)^2 - 4\times 1\times 3 = 16 - 12 = 4$

Comme $\Delta = 4 > 0$, l'équation admet deux solutions distinctes : $x_1=\dfrac{4-2}{2}=1$ et $x_2=\dfrac{4+2}{2}=3$.

Vérification : $1^2-1-1=-1=3\times1-4$ et $3^2-3-1=5=3\times3-4$.

La droite $(D)$ et la parabole $(P)$ se coupent donc en deux points distincts, d'abscisses $1$ et $3$ : la bonne réponse est **d)**.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de regroupement : passer $3x-4$ du côté gauche en ajoutant $3x$ et en retranchant $4$ donne $x^2+2x+3=0$ et $\Delta=-8$.
- **b)** $x=2=-\dfrac{b}{2a}$ est l'abscisse du sommet du trinôme, pas une solution : $\Delta\neq 0$.
- **c)** Erreur de signe dans les solutions : on a pris $\dfrac{-4\pm2}{2}$ au lieu de $\dfrac{4\pm2}{2}$.

</details>

Avis : 

---

## 40. `cqc-distance-tle-c-elevee-5` (séries BAC:C PRO:C)

**Remarque du relecteur :** Le choix a) (11/4) est la valeur de AM², piège volontaire mais légitime.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans un repère orthonormé, on considère la parabole $(P)$ d'équation $y=x^2$ et le point $A(0\,;3)$. Pour tout réel $x$, on note $M_x(x\,;x^2)$ le point de $(P)$ d'abscisse $x$. Quelle est la plus petite valeur de la distance $AM_x$ lorsque $x$ décrit $\mathbb{R}$ ?

- a) $\dfrac{11}{4}$
- b) $3$
- c) $\dfrac{\sqrt{11}}{2}$
- d) $\dfrac{\sqrt{10}}{2}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour minimiser une distance, on minimise son carré (la racine carrée est croissante sur $[0\,;+\infty[$), ce qui donne une fonction polynôme plus simple à dériver. On étudie le signe de la dérivée pour trouver le minimum, puis on n'oublie pas de reprendre la racine carrée.

### Corrigé

On pose $d(x)=AM_x^2=x^2+(x^2-3)^2=x^4-5x^2+9$.

$d'(x)=4x^3-10x=2x(2x^2-5)$. $d'$ s'annule en $x=0$ et $x=\pm\sqrt{\dfrac52}$. Signe : $d'(x)<0$ pour $x<-\sqrt{\frac52}$, $d'(x)>0$ sur $\left]-\sqrt{\frac52}\,;0\right[$, $d'(x)<0$ sur $\left]0\,;\sqrt{\frac52}\right[$, $d'(x)>0$ au-delà.

$d$ décroît, croît, décroît, puis croît : les minimums sont atteints en $x=\pm\sqrt{\dfrac52}$, avec
$$d\left(\pm\sqrt{\tfrac52}\right)=\dfrac{25}4-\dfrac{25}2+9=\dfrac{25-50+36}4=\dfrac{11}4.$$
En $x=0$, $d(0)=9$ est un maximum local. La distance minimale de $A$ à la parabole est donc $\sqrt{\dfrac{11}4}=\dfrac{\sqrt{11}}2$, atteinte aux deux points $\left(\pm\sqrt{\dfrac52}\,;\dfrac52\right)$.

La bonne réponse est **c)**.

### Pourquoi les autres réponses sont fausses

- **a)** $\dfrac{11}{4}$ est le minimum du carré $AM_x^2$ : on a oublié de prendre la racine carrée.
- **b)** $3=\sqrt{d(0)}$ correspond au point $O$, qui donne un maximum local de $d$ et non le minimum.
- **d)** $\dfrac{\sqrt{10}}{2}=\sqrt{\dfrac52}$ est l'abscisse du point où le minimum est atteint, pas la distance.

</details>

Avis : 

---

## 41. `cqc-distance-tle-c-moyenne-2` (séries BAC:C BAC:D BAC:TI PRO:C)

**Remarque du relecteur :** LIMITE : formule de distance d'un point à une droite, liée au produit scalaire (absent du référentiel, à signaler)

**Énoncé :**

Dans un repère orthonormé, quelle est la distance du point $M(2\,;-1)$ à la droite $(D)$ d'équation $3x-4y+5=0$ ?

- a) $3$
- b) $\dfrac{7}{5}$
- c) $\dfrac{3}{5}$
- d) $\dfrac{15}{7}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Dans un repère orthonormé, la distance du point $M(x_0\,;y_0)$ à la droite d'équation $ax+by+c=0$ est $\dfrac{|ax_0+by_0+c|}{\sqrt{a^2+b^2}}$.

### Corrigé

$3\times2-4\times(-1)+5=6+4+5=15$ et $\sqrt{3^2+(-4)^2}=\sqrt{25}=5$, donc
$$d(M,(D))=\dfrac{|15|}{5}=3.$$

La bonne réponse est **a)**.

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de signe : $-4\times(-1)$ vaut $+4$ et non $-4$, ce qui donnait $\dfrac{|6-4+5|}{5}=\dfrac{7}{5}$.
- **c)** On a divisé par $a^2+b^2=25$ en oubliant la racine carrée.
- **d)** On a divisé par $|a|+|b|=7$ au lieu de $\sqrt{a^2+b^2}$.

</details>

Avis : 

---

## 42. `cqc-distance-tle-c-moyenne-4` (séries BAC:C BAC:D BAC:TI PRO:C)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Dans l'espace muni d'un repère orthonormé, on donne $A(1\,;2\,;0)$ et $B(0\,;-1\,;3)$. Quel est le point $M$ de l'axe $(Oz)$ équidistant de $A$ et de $B$ ?

- a) $M\left(0\,;0\,;\dfrac{2}{3}\right)$
- b) $M\left(0\,;0\,;\dfrac{5}{6}\right)$
- c) $M\left(0\,;0\,;-\dfrac{5}{6}\right)$
- d) $M\left(0\,;0\,;\dfrac{1}{2}\right)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Un point de l'axe $(Oz)$ a pour coordonnées $(0\,;0\,;z)$. Dire qu'il est équidistant de $A$ et $B$ revient à écrire $MA^2=MB^2$, ce qui évite les racines carrées.

### Corrigé

$M(0\,;0\,;z)$ : $MA^2=1^2+2^2+z^2=5+z^2$ et $MB^2=0^2+(-1)^2+(z-3)^2=z^2-6z+10$.

$MA^2=MB^2\iff5=-6z+10\iff z=\dfrac56$.

Le point cherché est $M\left(0\,;0\,;\dfrac56\right)$. Vérification : $MA^2=5+\dfrac{25}{36}=\dfrac{205}{36}$ et $MB^2=\left(\dfrac56-3\right)^2+1=\dfrac{169}{36}+1=\dfrac{205}{36}$.

La bonne réponse est **b)**.

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié le terme $(-1)^2=1$ dans $MB^2$, ce qui donne $5=-6z+9$.
- **c)** Erreur dans l'identité remarquable : $(z-3)^2=z^2-6z+9$ et non $z^2+6z+9$.
- **d)** On a écrit $(-1)^2=-1$, ce qui donne $5=-6z+8$.

</details>

Avis : 

---

## 43. `cqc-derivabilite-elevee-0` (séries BAC:C BAC:D BAC:E PRO:C PRO:D PRO:E)

**Remarque du relecteur :** LIMITE : encadrement admis puis théorème des gendarmes, en haut du programme de Première C/D/E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On admet que pour tout réel $t$, on a l'encadrement :
$$\dfrac{t^2}{2}-\dfrac{t^4}{24}\leqslant1-\cos t\leqslant\dfrac{t^2}{2}.$$

On définit la fonction $k$ sur $\mathbb{R}$ par :
$$k(x) = \dfrac{1-\cos(x-2)}{x-2} \text{ si } x\neq2, \qquad k(2) = 0.$$

Que peut-on dire de la dérivabilité de $k$ en $2$ ?

- a) $k$ est dérivable en $2$ et $k'(2)=0$
- b) $k$ est dérivable en $2$ et $k'(2)=\dfrac{1}{2}$
- c) $k$ n'est pas dérivable en $2$
- d) $k$ est dérivable en $2$ et $k'(2)=-\dfrac{1}{2}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
On étudie la limite en $2$ du taux d'accroissement $\tau(x)=\dfrac{k(x)-k(2)}{x-2}$. Lorsqu'un encadrement comporte deux bornes non constantes, il faut vérifier que ces DEUX bornes tendent vers la même limite finie avant d'appliquer le théorème des gendarmes.

### Corrigé
**Taux d'accroissement.** Comme $k(2)=0$, pour $x\neq2$ :
$$\tau(x) = \dfrac{k(x)}{x-2} = \dfrac{1-\cos(x-2)}{(x-2)^2}.$$

**Encadrement.** Posons $t=x-2$ ; comme $x\neq2$, on a $t\neq0$. En divisant les trois membres de l'encadrement admis par $t^2>0$ :
$$\dfrac12-\dfrac{t^2}{24}\leqslant\dfrac{1-\cos t}{t^2}\leqslant\dfrac12,$$
soit
$$\dfrac12-\dfrac{(x-2)^2}{24}\leqslant\tau(x)\leqslant\dfrac12.$$
Quand $x\to2$, $(x-2)^2\to0$ : la borne inférieure tend vers $\dfrac12$, et la borne supérieure vaut constamment $\dfrac12$.

**Conclusion.** Par le théorème des gendarmes, $\displaystyle\lim_{x\to2}\tau(x)=\dfrac12$. Cette limite étant finie, $k$ est dérivable en $2$, avec $k'(2)=\dfrac12$.

La bonne réponse est **b)**.

### Pourquoi les autres réponses sont fausses

- **a)** $0$ est la limite de $k(x)$ quand $x\to2$ (ce qui prouve la continuité), pas celle du taux d'accroissement : on a oublié de diviser encore par $x-2$.
- **c)** Les deux bornes de l'encadrement ont la même limite $\dfrac12$ : le théorème des gendarmes s'applique et la limite du taux est finie.
- **d)** Erreur de signe : on a encadré $\cos t-1$ au lieu de $1-\cos t$.

</details>

Avis : 

---

## 44. `cqc-derivabilite-faible-1` (séries BAC:C BAC:D BAC:E PRO:C PRO:D PRO:E)

**Remarque du relecteur :** LIMITE : dérivée de √u (fonction composée), haut du programme de Première

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $g$ la fonction définie sur $\mathbb{R}$ par $g(x) = \sqrt{x^2+4}$. On admet que $g$ est dérivable sur $\mathbb{R}$. Quelle est l'expression de $g'(x)$ pour tout réel $x$ ?

- a) $g'(x)=\dfrac{1}{2\sqrt{x^2+4}}$
- b) $g'(x)=\dfrac{x}{\sqrt{x^2+4}}$
- c) $g'(x)=\dfrac{2x}{\sqrt{x^2+4}}$
- d) $g'(x)=\dfrac{x}{2\sqrt{x^2+4}}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
Une fonction de la forme $\sqrt{u(x)}$ est dérivable en tout point où $u(x)>0$ strictement, avec $\left(\sqrt{u}\right)'=\dfrac{u'}{2\sqrt{u}}$. Si $u(x)$ ne s'annule jamais sur $\mathbb{R}$, aucun point n'est à isoler : $\sqrt{u}$ est dérivable sur $\mathbb{R}$ tout entier.

### Corrigé
Ici $u(x)=x^2+4$. Comme $x^2\geqslant0$ pour tout réel $x$, on a $u(x)\geqslant4>0$ : $u$ ne s'annule jamais, donc $g$ est définie et dérivable sur $\mathbb{R}$ tout entier.

Pour tout réel $x$ :
$$g'(x) = \dfrac{u'(x)}{2\sqrt{u(x)}} = \dfrac{2x}{2\sqrt{x^2+4}} = \dfrac{x}{\sqrt{x^2+4}}.$$

La bonne réponse est **b)**.

### Pourquoi les autres réponses sont fausses
- **a)** On a oublié de multiplier par la dérivée $u'(x)=2x$ de la fonction sous la racine.
- **c)** On a oublié le facteur $2$ du dénominateur de la formule $\dfrac{u'}{2\sqrt{u}}$.
- **d)** On a simplifié $2x$ par $2$ tout en gardant le $2$ au dénominateur : le facteur $2$ a été utilisé deux fois.

</details>

Avis : 

---

## 45. `cqc-derivabilite-moyenne-1` (séries BAC:C BAC:D BAC:E PRO:C PRO:D PRO:E)

**Remarque du relecteur :** LIMITE : nécessite la majoration |cos|<=1 et le théorème des gendarmes (limite par comparaison), en haut du programme de Première C/D/E.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

On définit la fonction $m$ sur $\mathbb{R}$ par :
$$m(x) = (x-1)^2\cos\left(\dfrac{1}{x-1}\right) \text{ si } x\neq1, \qquad m(1) = 0.$$

Que peut-on affirmer sur la dérivabilité de $m$ en $1$ ?

- a) $m$ est dérivable en $1$ et $m'(1)=0$.
- b) $m$ n'est pas dérivable en $1$, car $\cos\left(\dfrac{1}{x-1}\right)$ n'a pas de limite quand $x$ tend vers $1$.
- c) $m$ est dérivable en $1$ et $m'(1)=1$.
- d) $m$ n'est pas continue en $1$, donc elle n'est pas dérivable en $1$.

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode
Quand un taux d'accroissement contient un terme oscillant comme $\cos$ ou $\sin$ d'une expression qui devient infinie au point étudié, sa limite ne se calcule pas directement (le terme oscillant seul n'a pas de limite). On encadre ce terme entre $-1$ et $1$, ce qui permet de majorer et de minorer tout le taux d'accroissement par deux expressions simples : si ces deux bornes tendent vers la même limite finie, le théorème des gendarmes donne la limite du taux d'accroissement.

### Corrigé
**Taux d'accroissement.** Comme $m(1)=0$, pour $x\neq1$ :
$$\tau(x) = \dfrac{m(x)-m(1)}{x-1} = \dfrac{(x-1)^2\cos\left(\frac{1}{x-1}\right)}{x-1} = (x-1)\cos\left(\dfrac{1}{x-1}\right).$$

**Encadrement.** Pour tout $x\neq1$, $\left|\cos\left(\frac{1}{x-1}\right)\right|\leqslant1$, d'où $|\tau(x)|\leqslant |x-1|$, soit $-|x-1|\leqslant\tau(x)\leqslant|x-1|$. Quand $x\to1$, les deux bornes tendent vers $0$.

**Conclusion.** Par le théorème des gendarmes, $\displaystyle\lim_{x\to1}\tau(x)=0$. Cette limite étant finie, $m$ est dérivable en $1$, avec $m'(1)=0$.

La bonne réponse est **a)**.

### Pourquoi les autres réponses sont fausses
- **b)** Le cosinus n'a pas de limite, mais il est multiplié par $x-1$, qui tend vers $0$ : le produit, borné par $|x-1|$, tend vers $0$.
- **c)** On a remplacé $\cos\left(\frac{1}{x-1}\right)$ par $\cos 0=1$, comme si $\frac{1}{x-1}$ tendait vers $0$ ; or cette quantité devient infinie quand $x$ tend vers $1$.
- **d)** $|m(x)|\leqslant(x-1)^2$, qui tend vers $0=m(1)$ : $m$ est continue en $1$, et elle y est même dérivable.

</details>

Avis : 

---

## 46. `cqc-derivee-prob-c-faible-0` (séries BAC:A PRO:A PRO:C PRO:D PRO:E)

**Remarque du relecteur :** LIMITE : dérivation pour la série A, à confirmer au programme de Première A

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=x^3-5x^2+2x-1$. Quelle est l'expression de $f'(x)$ ?

- a) $f'(x)=3x^2-5x+2$
- b) $f'(x)=3x^2-10x+1$
- c) $f'(x)=3x^2-10x$
- d) $f'(x)=3x^2-10x+2$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On dérive terme à terme avec $(x^n)'=nx^{n-1}$, $(kx)'=k$ et $(\text{constante})'=0$.

### Corrigé

$$f'(x)=3x^2-5\times2x+2-0=3x^2-10x+2.$$

La bonne réponse est **d)**.

### Pourquoi les autres réponses sont fausses
- **a)** On a oublié de multiplier par l'exposant $2$ dans la dérivée de $-5x^2$, qui vaut $-10x$.
- **b)** On a gardé une partie de la constante : la dérivée de $2x-1$ est $2$, la constante $-1$ disparaît sans modifier le $2$.
- **c)** On a pris la dérivée de $2x$ égale à $0$, alors que $(kx)'=k$, donc $(2x)'=2$.

</details>

Avis : 

---

## 47. `cqc-derivee-prob-c-moyenne-2` (séries BAC:A PRO:A PRO:C PRO:D PRO:E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=(3x-1)^2$. Quelle est l'expression de $f'(x)$ ?

- a) $f'(x)=6x-2$
- b) $f'(x)=18x-6$
- c) $f'(x)=18x$
- d) $f'(x)=18x+6$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Dérivée d'une puissance : $(u^n)'=n\,u'\,u^{n-1}$. On dérive la « fonction du dedans » $u$ et on multiplie par $n\,u^{n-1}$. On peut aussi développer d'abord le carré, puis dériver le polynôme obtenu.

### Corrigé

Avec $u=3x-1$ et $u'=3$ :
$$f'(x)=2\times3\times(3x-1)=6(3x-1)=18x-6.$$
Vérification en développant : $f(x)=9x^2-6x+1$, donc $f'(x)=18x-6$.

La bonne réponse est **b)**.

### Pourquoi les autres réponses sont fausses
- **a)** On a oublié de multiplier par la dérivée $u'=3$ de la fonction du dedans : $2(3x-1)=6x-2$.
- **c)** On a développé $(3x-1)^2$ en $9x^2+1$ en oubliant le double produit $-6x$.
- **d)** Erreur de signe : le double produit de $(3x-1)^2$ est $-6x$, pas $+6x$.

</details>

Avis : 

---

## 48. `cqc-derivee-d-un-quotient-prob-c-faible-0` (séries BAC:A PRO:A PRO:C PRO:E)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A, PRO:A.

**Remarque du relecteur :** LIMITE : dérivée d'un quotient pour la série A, à confirmer au programme de Première A

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}\setminus\{2\}$ par $f(x)=\dfrac{x+1}{x-2}$. Quelle est l'expression de $f'(x)$ ?

- a) $f'(x)=\dfrac{-3}{(x-2)^2}$
- b) $f'(x)=\dfrac{3}{(x-2)^2}$
- c) $f'(x)=\dfrac{-1}{(x-2)^2}$
- d) $f'(x)=\dfrac{-3}{x-2}$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

$\left(\dfrac uv\right)'=\dfrac{u'v-uv'}{v^2}$ : on dérive le numérateur, on garde le dénominateur, on retranche le numérateur multiplié par la dérivée du dénominateur, le tout sur le carré du dénominateur.

### Corrigé

$u=x+1$, $v=x-2$, $u'=v'=1$ :
$$f'(x)=\dfrac{1\times(x-2)-(x+1)\times1}{(x-2)^2}=\dfrac{x-2-x-1}{(x-2)^2}=\dfrac{-3}{(x-2)^2}.$$

La bonne réponse est **a)**.

### Pourquoi les autres réponses sont fausses
- **b)** On a inversé l'ordre de la formule en calculant $uv'-u'v$ au numérateur, ce qui change le signe.
- **c)** Erreur de signe en développant $-(x+1)$ en $-x+1$ : le numérateur devient $x-2-x+1=-1$.
- **d)** On a oublié d'élever le dénominateur au carré.

</details>

Avis : 

---

## 49. `cqc-derivee-d-un-quotient-tle-c-faible-0` (séries BAC:A BAC:C BAC:D BAC:E PRO:A)

**Série(s) retirée(s) par analogie avec vos avis :** BAC:A, PRO:A.

**Remarque du relecteur :** LIMITE : dérivée d'un quotient (fonction homographique) pour la série A, à la limite haute de son programme allégé.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}\setminus\{1\}$ par $f(x)=\dfrac{2x+3}{x-1}$. Quelle est l'expression de $f'(x)$ ?

- a) $f'(x)=\dfrac{5}{(x-1)^2}$
- b) $f'(x)=\dfrac{1}{(x-1)^2}$
- c) $f'(x)=\dfrac{-5}{(x-1)^2}$
- d) $f'(x)=2$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

$\left(\dfrac uv\right)'=\dfrac{u'v-uv'}{v^2}$ : on dérive le numérateur, on garde le dénominateur, puis on retranche le numérateur multiplié par la dérivée du dénominateur, le tout sur $v^2$.

### Corrigé

Avec $u=2x+3$, $v=x-1$, $u'=2$, $v'=1$ :
$$f'(x)=\dfrac{2(x-1)-(2x+3)\times1}{(x-1)^2}=\dfrac{2x-2-2x-3}{(x-1)^2}=\dfrac{-5}{(x-1)^2}.$$
$f'$ est donc strictement négative : $f$ est décroissante sur chaque intervalle de son ensemble de définition.

La bonne réponse est **c)**.

### Pourquoi les autres réponses sont fausses
- **a)** On a inversé l'ordre de la formule en calculant $uv'-u'v$ au numérateur, ce qui change le signe.
- **b)** Erreur de signe en développant $-(2x+3)$ en $-2x+3$ : le numérateur devient $2x-2-2x+3=1$.
- **d)** On a divisé la dérivée du numérateur par celle du dénominateur ($\frac{2}{1}$) : la dérivée d'un quotient n'est pas le quotient des dérivées.

</details>

Avis : 

---

## 50. `cqc-endomorphisme-elevee-0` (séries BAC:C BAC:E PRO:C PRO:E)

**Série(s) retirée(s) par analogie avec vos avis :** PRO:C.

**Remarque du relecteur :** LIMITE : endomorphisme d'un espace vectoriel de dimension 3 et noyau, en haut du programme de Première C/E (souvent traité en dimension 2) ; à confirmer par l'enseignant.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $E$ un espace vectoriel réel de dimension 3, muni d'une base $(\vec\alpha,\vec\beta,\vec\gamma)$. On considère l'endomorphisme $m$ de $E$ défini par $m(\vec\alpha)=\vec\beta$, $m(\vec\beta)=\vec\gamma$, $m(\vec\gamma)=\vec\beta+\vec\gamma$. Laquelle des affirmations suivantes est exacte ?

- a) $(\vec\alpha)$ est une base de $\ker m$.
- b) $(-\vec\alpha+\vec\beta+\vec\gamma)$ est une base de $\ker m$.
- c) $\ker m=\{\vec 0\}$, c'est-à-dire que $m$ est injective.
- d) $(-\vec\alpha-\vec\beta+\vec\gamma)$ est une base de $\ker m$.

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode
Pour déterminer le noyau d'un endomorphisme, on calcule l'image d'un vecteur quelconque $x\vec\alpha+y\vec\beta+z\vec\gamma$ par linéarité, puis on résout le système obtenu en écrivant que toutes ses coordonnées sont nulles. Les solutions s'expriment à l'aide d'un ou plusieurs paramètres, ce qui fournit une base du noyau.

### Corrigé
Pour $\vec u=x\vec\alpha+y\vec\beta+z\vec\gamma$, $m(\vec u)=x\vec\beta+y\vec\gamma+z(\vec\beta+\vec\gamma)=(x+z)\vec\beta+(y+z)\vec\gamma$.

$m(\vec u)=\vec 0 \iff x+z=0 \text{ et } y+z=0 \iff x=-z \text{ et } y=-z$. En posant $z=1$, une base de $\ker m$ est $\big(-\vec\alpha-\vec\beta+\vec\gamma\big)$, donc $\dim\ker m=1$.

Vérification : $m(-\vec\alpha-\vec\beta+\vec\gamma)=-\vec\beta-\vec\gamma+\vec\beta+\vec\gamma=\vec 0$.

La bonne réponse est **d)**.

### Pourquoi les autres réponses sont fausses
- **a)** On a confondu lignes et colonnes de la matrice de $m$ ; en réalité $m(\vec\alpha)=\vec\beta\neq\vec 0$.
- **b)** Erreur de signe dans la résolution ($y=z$ au lieu de $y=-z$) : $m(-\vec\alpha+\vec\beta+\vec\gamma)=2\vec\gamma\neq\vec 0$.
- **c)** Le système n'a que deux équations pour trois inconnues : il admet des solutions non nulles, donc $m$ n'est pas injective.

</details>

Avis : 

---

## 51. `cqc-endomorphisme-faible-0` (séries BAC:C BAC:E PRO:C PRO:E)

**Série(s) retirée(s) par analogie avec vos avis :** PRO:C.

**Remarque du relecteur :** LIMITE : endomorphisme d'un espace vectoriel de dimension 3 et sa matrice, à la limite haute du programme de Première C/E (souvent vu en dimension 2).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou contexte adapté) : à examiner de près.

**Énoncé :**

Soit $E$ un espace vectoriel réel de dimension 3, muni d'une base $(\vec u,\vec v,\vec w)$. On considère l'endomorphisme $f$ de $E$ défini par $f(\vec u)=2\vec u-\vec w$, $f(\vec v)=\vec v+3\vec w$, $f(\vec w)=-\vec u+\vec v$. Quelle est la matrice de $f$ dans la base $(\vec u,\vec v,\vec w)$ ?

- a) $\begin{pmatrix}2&0&-1\\0&1&3\\-1&1&0\end{pmatrix}$
- b) $\begin{pmatrix}2&0&-1\\0&1&1\\-1&3&0\end{pmatrix}$
- c) $\begin{pmatrix}2&0&-1\\-1&1&1\\0&3&0\end{pmatrix}$
- d) $\begin{pmatrix}2&0&-1\\0&1&1\\1&3&0\end{pmatrix}$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode
La matrice d'un endomorphisme dans une base donnée se construit colonne par colonne : la $k$-ième colonne contient les coordonnées de l'image du $k$-ième vecteur de base, exprimées dans cette même base.

### Corrigé
On lit les coordonnées de chaque image dans la base $(\vec u,\vec v,\vec w)$ : $f(\vec u)=2\vec u+0\vec v-\vec w$ donne la colonne $(2\,;0\,;-1)$, $f(\vec v)=0\vec u+\vec v+3\vec w$ donne la colonne $(0\,;1\,;3)$, et $f(\vec w)=-\vec u+\vec v+0\vec w$ donne la colonne $(-1\,;1\,;0)$.

$$M=\begin{pmatrix}2&0&-1\\0&1&1\\-1&3&0\end{pmatrix}$$

La bonne réponse est **b)**.

### Pourquoi les autres réponses sont fausses
- **a)** On a rangé les coordonnées des images en lignes au lieu de colonnes : c'est la transposée de la bonne matrice.
- **c)** On a oublié le coefficient nul de $\vec v$ dans $f(\vec u)=2\vec u-\vec w$ : la première colonne doit être $(2\,;0\,;-1)$ et non $(2\,;-1\,;0)$.
- **d)** Erreur de signe sur la coordonnée de $\vec w$ dans $f(\vec u)$, qui vaut $-1$ et non $1$.

</details>

Avis : 

---

