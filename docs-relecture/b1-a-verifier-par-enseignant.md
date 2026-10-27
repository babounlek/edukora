# Quiz de maths BEPC a verifier par un enseignant (campagne B1)

Trois echantillons, 48 questions au total, deja en ligne. Pour chacune : OK, a corriger (quoi), ou a retirer. Les corriges sont repliables.



# Vague 1 (112 QCM en ligne)

Date : 2026-10-26. 14 questions sur 112 : celles ou un sous-agent a change le fond (cle, methode, enonce) ou signale un doute de programme. Les 112 ont deja ete resolues a l'aveugle par un relecteur independant, avec accord total ; ce document sert a juger ce qu'un relecteur modele ne juge pas : le niveau 3e / BEPC, le realisme des distracteurs et les conventions d'enseignement.

Pour chaque question : **OK**, **a corriger** (dire quoi), ou **a retirer**.

### 1. `cqc-pgcd-moyenne-0`

**A regarder :** Partie Bezout (u et v) supprimee, seul le pgcd est demande.

**Enonce :**

On considère les entiers naturels $a = 1073$ et $b = 754$.

À l'aide de l'algorithme d'Euclide, déterminer $\mathrm{pgcd}(a,b)$.

- a) $87$
- b) $13$
- c) $58$
- d) $29$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

L'algorithme d'Euclide détermine le pgcd de deux entiers par divisions euclidiennes successives : on divise le plus grand par le plus petit, puis le diviseur par le reste, et ainsi de suite jusqu'à un reste nul ; le pgcd est le dernier reste non nul. En remontant ensuite ces divisions de la dernière à la première, on exprime ce pgcd comme une combinaison linéaire entière des deux nombres de départ (identité de Bézout).

### Corrigé

Divisions successives :
$$1073 = 1 \times 754 + 319$$
$$754 = 2 \times 319 + 116$$
$$319 = 2 \times 116 + 87$$
$$116 = 1 \times 87 + 29$$
$$87 = 3 \times 29 + 0$$

Le dernier reste non nul est $29$, donc $\mathrm{pgcd}(1073, 754) = 29$. Vérification : $1073 = 29 \times 37$ et $754 = 29 \times 26$.

La bonne réponse est **d)**.

### Pourquoi les autres réponses sont fausses

- **a)** $87$ est l'avant-dernier reste non nul : on s'est arrêté une division trop tôt ($87$ ne divise pas $1073$).
- **b)** $13$ divise $754 = 2 \times 13 \times 29$, mais pas $1073$ : ce n'est pas un diviseur commun.
- **c)** $58 = 2 \times 29$ divise $754$, mais pas $1073$, qui est impair.

</details>

Avis : 

---

### 2. `cqc-aire-d-un-triangle-moyenne-1`

**A regarder :** Methode du corrige remplacee : hauteur CH = AC sin 60 au lieu de la formule 1/2 ab sin C (hors programme).

**Enonce :**

Une entreprise de signalétique fabrique un panneau triangulaire $ABC$. Sur le plan de fabrication, on lit $AB = 8$ cm, $AC = 6$ cm et un angle $\widehat{BAC} = 60^{\circ}$ entre ces deux côtés. On note $H$ le pied de la hauteur issue de $C$ sur la droite $(AB)$. Quelle est l'aire de ce panneau ?

- a) $24\sqrt3$ cm²
- b) $12$ cm²
- c) $6\sqrt3$ cm²
- d) $12\sqrt3$ cm²

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Quand on connaît deux côtés d'un triangle et l'angle qu'ils forment entre eux, on calcule la hauteur grâce au sinus dans le triangle rectangle formé par cette hauteur, puis on applique $\mathcal A = \dfrac{\text{base} \times \text{hauteur}}{2}$. Cela revient à la formule $\mathcal A = \dfrac12 \times AB \times AC \times \sin(\widehat{BAC})$.

### Corrigé

Le triangle $AHC$ est rectangle en $H$, donc $\sin(\widehat{BAC}) = \dfrac{CH}{AC}$, d'où

$CH = AC \times \sin(60^{\circ}) = 6 \times \dfrac{\sqrt3}{2} = 3\sqrt3$ cm.

$\mathcal A = \dfrac{AB \times CH}{2} = \dfrac{8 \times 3\sqrt3}{2} = 12\sqrt3$

Autrement dit, $\mathcal A = \dfrac12 \times 8 \times 6 \times \sin(60^{\circ}) = 24 \times \dfrac{\sqrt3}{2} = 12\sqrt3$.

L'aire du panneau est $12\sqrt3$ cm², soit environ $20{,}8$ cm².

### Pourquoi les autres réponses sont fausses

- **a)** $24\sqrt3$ cm² : on a oublié de diviser par $2$ dans la formule de l'aire.
- **b)** $12$ cm² : on a pris $\sin(60^{\circ}) = \dfrac12$, valeur qui est celle de $\cos(60^{\circ})$.
- **c)** $6\sqrt3$ cm² : on a divisé par $2$ deux fois (hauteur prise égale à $\dfrac{3\sqrt3}{2}$ ou aire divisée par $4$).

</details>

Avis : 

---

### 3. `cqc-aire-d-un-triangle-moyenne-2`

**A regarder :** Methode du corrige remplacee : rectangle englobant au lieu du determinant (hors programme).

**Enonce :**

Dans un repère orthonormé du plan, on considère les points $A(-2\,;\,1)$, $B(3\,;\,4)$ et $C(1\,;\,-3)$. Quelle est l'aire du triangle $ABC$, en unités d'aire ?

- a) $14{,}5$
- b) $29$
- c) $35$
- d) $20{,}5$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Quand les sommets d'un triangle sont donnés par leurs coordonnées, on peut l'inscrire dans le rectangle à côtés parallèles aux axes qui l'enferme : l'aire du triangle est l'aire de ce rectangle moins celles des trois triangles rectangles qui l'entourent.

### Corrigé

Les abscisses vont de $-2$ à $3$ et les ordonnées de $-3$ à $4$ : le rectangle qui enferme $ABC$ mesure $5$ sur $7$, d'aire $35$.

Les trois triangles rectangles qui l'entourent :

- côté $[AB]$ : côtés de l'angle droit $3-(-2) = 5$ et $4-1 = 3$, aire $\dfrac{5 \times 3}{2} = 7{,}5$ ;
- côté $[BC]$ : côtés de l'angle droit $3-1 = 2$ et $4-(-3) = 7$, aire $\dfrac{2 \times 7}{2} = 7$ ;
- côté $[CA]$ : côtés de l'angle droit $1-(-2) = 3$ et $1-(-3) = 4$, aire $\dfrac{3 \times 4}{2} = 6$.

$\mathcal A = 35 - (7{,}5 + 7 + 6) = 35 - 20{,}5 = 14{,}5$

L'aire du triangle $ABC$ est $\dfrac{29}{2}$ unités d'aire, soit $14{,}5$ unités d'aire.

### Pourquoi les autres réponses sont fausses

- **b)** $29$ : c'est le double de l'aire, on a oublié la division par $2$.
- **c)** $35$ : c'est l'aire du rectangle qui enferme le triangle, on a oublié de retirer les trois triangles rectangles.
- **d)** $20{,}5$ : c'est la somme des aires des trois triangles à retirer, pas l'aire de $ABC$.

</details>

Avis : 

---

### 4. `cqc-amplitude-elevee-0`

**A regarder :** Consigne d'origine a plusieurs bonnes reponses, reformulee en 'lequel convient' avec une seule option valide.

**Enonce :**

On donne l'encadrement très précis $3{,}3166 < \sqrt{11} < 3{,}3167$. Parmi les encadrements suivants de $D = 2\sqrt{11} - 1$, lequel est correct et d'amplitude exactement $4 \times 10^{-3}$ ?

- a) $5{,}6332 < D < 5{,}6334$
- b) $5{,}629 < D < 5{,}633$
- c) $5{,}631 < D < 5{,}635$
- d) $6{,}631 < D < 6{,}635$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode
Quand l'encadrement obtenu directement par le calcul est plus précis (amplitude plus petite) que celui demandé, il faut l'élargir volontairement : on abaisse le minorant et on augmente le majorant jusqu'à obtenir exactement l'amplitude exigée, tout en vérifiant que le nouvel encadrement contient bien l'ancien.

### Corrigé

*Étape 1 : encadrer $D$ directement.* On multiplie l'encadrement de $\sqrt{11}$ par $2$ (positif, le sens est conservé), puis on soustrait $1$ (le sens est conservé) :

$$2 \times 3{,}3166 < 2\sqrt{11} < 2 \times 3{,}3167$$

$$6{,}6332 < 2\sqrt{11} < 6{,}6334$$

$$5{,}6332 < D < 5{,}6334$$

Amplitude : $5{,}6334 - 5{,}6332 = 0{,}0002 = 2 \times 10^{-4}$, plus fine que celle demandée ($4 \times 10^{-3} = 0{,}004$) : il faut élargir.

*Étape 2 : élargir jusqu'à l'amplitude demandée.*

$$5{,}631 < D < 5{,}635$$

**Vérification.** $5{,}635 - 5{,}631 = 0{,}004$, et $5{,}631 < 5{,}6332$ et $5{,}6334 < 5{,}635$ : l'encadrement élargi contient bien l'encadrement précis, donc il contient $D$.

### Pourquoi les autres réponses sont fausses

- **a)** $5{,}6332 < D < 5{,}6334$ : encadrement juste, mais d'amplitude $2 \times 10^{-4}$, pas $4 \times 10^{-3}$.
- **b)** $5{,}629 < D < 5{,}633$ : l'amplitude vaut bien $0{,}004$, mais le majorant $5{,}633$ est inférieur à $5{,}6332$, donc $D$ n'est pas dans cet intervalle.
- **d)** $6{,}631 < D < 6{,}635$ : on a oublié de soustraire $1$ (c'est un encadrement de $2\sqrt{11}$).

</details>

Avis : 

---

### 5. `cqc-amplitude-moyenne-2`

**A regarder :** Idem, et une phrase fausse du corrige d'origine a ete corrigee (le minorant reste 12,7).

**Enonce :**

On donne l'encadrement $12{,}7 < x < 12{,}73$, d'amplitude $0{,}03$. Parmi les encadrements suivants, lequel est d'amplitude exactement $0{,}1$ et contient l'encadrement donné ?

- a) $12{,}6 < x < 12{,}7$
- b) $12{,}7 < x < 12{,}73$
- c) $12{,}7 < x < 12{,}8$
- d) $12{,}7 < x < 13{,}7$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode
Un encadrement peut toujours être élargi : il suffit d'abaisser le minorant (ou de le garder) et d'augmenter le majorant, tout en gardant les deux nouvelles bornes cohérentes avec le nombre encadré. Un encadrement plus large a une amplitude plus grande, donc une précision moindre.

### Corrigé

*Amplitude de l'encadrement donné.* $12{,}73 - 12{,}7 = 0{,}03$.

*Élargissement à une amplitude de $0{,}1$.* On garde le minorant $12{,}7$ et on augmente le majorant au dixième supérieur :

$$12{,}7 < x < 12{,}8$$

Son amplitude est $12{,}8 - 12{,}7 = 0{,}1$, comme demandé.

**Vérification.** $12{,}7 \leq 12{,}7$ et $12{,}73 < 12{,}8$ : tout nombre $x$ vérifiant $12{,}7 < x < 12{,}73$ vérifie aussi $12{,}7 < x < 12{,}8$.

### Pourquoi les autres réponses sont fausses

- **a)** $12{,}6 < x < 12{,}7$ : amplitude $0{,}1$, mais cet intervalle ne contient aucun nombre de l'encadrement donné (tous sont supérieurs à $12{,}7$).
- **b)** $12{,}7 < x < 12{,}73$ : c'est l'encadrement de départ, d'amplitude $0{,}03$.
- **d)** $12{,}7 < x < 13{,}7$ : il contient bien l'encadrement donné, mais son amplitude vaut $1$, pas $0{,}1$.

</details>

Avis : 

---

### 6. `cqc-appartenance-a-une-droite-faible-2`

**A regarder :** La cle a CHANGE : le point d'origine B(2 ; 3) n'est pas sur la droite, la bonne reponse est devenue B(2 ; 4).

**Enonce :**

La droite $(\Delta)$ a pour équation $y = -x + 6$.

Lequel des points suivants appartient à la droite $(\Delta)$ ?

- a) $B(2\,;\,8)$
- b) $B(2\,;\,-4)$
- c) $B(2\,;\,4)$
- d) $B(2\,;\,-8)$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Pour savoir si un point appartient à une droite d'équation $y = ax + b$, on remplace $x$ par l'abscisse du point : si l'on retrouve l'ordonnée du point, celui-ci appartient à la droite, sinon il n'y appartient pas.

### Corrigé

On remplace $x$ par $2$ dans l'équation de $(\Delta)$ :

$$y = -2 + 6 = 4$$

Le point d'abscisse $2$ de $(\Delta)$ a donc pour ordonnée $4$ : c'est $B(2\,;\,4)$. Par exemple, le point $(2\,;\,3)$ n'appartient **pas** à $(\Delta)$ puisque $4 \neq 3$.

### Pourquoi les autres réponses sont fausses

- **a)** Oubli du signe moins devant $x$ : on a calculé $2 + 6 = 8$.
- **b)** Erreur de signe sur le résultat : $-2 + 6 = 4$ et non $-4$.
- **d)** On a calculé $-2 - 6$ au lieu de $-2 + 6$.

</details>

Avis : 

---

### 7. `cqc-calcul-numerique-faible-1`

**A regarder :** Une question vrai/faux est devenue 'valeur de l'expression' (17/6).

**Enonce :**

Calcule, en respectant les priorités opératoires, le nombre suivant :

$$M = \frac{7}{2} - \frac{1}{2} \times \frac{4}{3}$$

Quelle est sa valeur ?

- a) $\dfrac{17}{6}$
- b) $4$
- c) $\dfrac{5}{6}$
- d) $\dfrac{1}{2}$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Dans une expression sans parenthèses, la multiplication se calcule avant la soustraction. On effectue donc d'abord le produit, puis la soustraction en mettant au même dénominateur.

### Corrigé

*Priorité à la multiplication.*

$$\frac{1}{2} \times \frac{4}{3} = \frac{4}{6} = \frac{2}{3}$$

*Soustraction, au même dénominateur (6).*

$$\frac{7}{2} - \frac{2}{3} = \frac{21}{6} - \frac{4}{6} = \frac{17}{6}$$

$$M = \frac{17}{6}$$

### Pourquoi les autres réponses sont fausses

- **b)** On a calculé de gauche à droite : $\left(\dfrac{7}{2} - \dfrac{1}{2}\right) \times \dfrac{4}{3} = 3 \times \dfrac{4}{3}$, sans respecter la priorité de la multiplication.
- **c)** On a écrit $\dfrac{7}{2} - \dfrac{2}{3} = \dfrac{7 - 2}{6}$ sans transformer les numérateurs lors de la mise au même dénominateur.
- **d)** On a écrit $\dfrac{7}{2} = \dfrac{7}{6}$ en oubliant de multiplier le numérateur par $3$ : $\dfrac{7}{6} - \dfrac{4}{6} = \dfrac{3}{6}$.

</details>

Avis : 

---

### 8. `cqc-carre-elevee-0`

**A regarder :** Reponse acceptee 'dans un ordre ou dans l'autre' (B et D echangeables).

**Enonce :**

Dans un repère orthonormé $(O,\vec{I},\vec{J})$, les points $A(2\;;\,1)$ et $C(6\;;\,5)$ sont deux sommets opposés (les extrémités d'une diagonale) d'un carré $ABCD$.

Quelles sont les coordonnées des deux autres sommets $B$ et $D$ (dans un ordre ou dans l'autre) ?

- a) $(5\;;\,2)$ et $(3\;;\,4)$
- b) $(8\;;\,-1)$ et $(0\;;\,7)$
- c) $(1\;;\,6)$ et $(5\;;\,2)$
- d) $(6\;;\,1)$ et $(2\;;\,5)$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Dans un carré, les diagonales ont la même longueur, se coupent perpendiculairement en leur milieu. Connaissant une diagonale, on trouve son milieu, sa longueur, puis on construit la seconde diagonale : même milieu, même longueur, mais dans une direction perpendiculaire.

### Corrigé

*Milieu des diagonales.*
$$O'\left(\frac{2+6}{2}\;;\,\frac{1+5}{2}\right) = O'(4\;;\,3)$$

*Vecteur et longueur de $[AC]$.*
$$\vec{AC}(6-2\;;\,5-1) = \vec{AC}(4\;;\,4) \qquad AC = \sqrt{4^2+4^2} = \sqrt{32} = 4\sqrt{2}$$

*Direction perpendiculaire.* Un vecteur perpendiculaire à $\vec{AC}(4\;;\,4)$ vérifie $4a + 4b = 0$, par exemple $\vec{v}(1\;;\,-1)$, de longueur $\sqrt{2}$.

*Ajustement de la longueur.* La diagonale $[BD]$ doit avoir la même longueur $4\sqrt{2}$, donc le vecteur $\vec{O'B}$ doit avoir pour longueur $\dfrac{4\sqrt{2}}{2} = 2\sqrt{2}$ (demi-diagonale). On multiplie $\vec{v}$ par $\dfrac{2\sqrt{2}}{\sqrt{2}} = 2$ :
$$\vec{O'B} = 2\,\vec{v} = (2\;;\,-2)$$

*Coordonnées de $B$ et $D$.*
$$B(4+2\;;\,3-2) = B(6\;;\,1) \qquad D(4-2\;;\,3+2) = D(2\;;\,5)$$

*Contrôle.* $\vec{AB}(6-2\;;\,1-1) = (4\;;\,0)$ et $\vec{BC}(6-6\;;\,5-1) = (0\;;\,4)$ : ces deux vecteurs ont la même longueur ($4$) et sont orthogonaux ($4\times 0 + 0\times 4 = 0$), ce qui confirme un carré de côté $4$.

### Remarque
Les noms $B$ et $D$ peuvent être échangés (l'autre choix, $B(2\;;\,5)$ et $D(6\;;\,1)$, donne le même carré parcouru dans l'autre sens).

### Pourquoi les autres réponses sont fausses

- **a)** On a reporté $\vec{v}(1\;;\,-1)$ depuis le centre sans l'ajuster : la demi-diagonale ne mesure alors que $\sqrt{2}$ au lieu de $2\sqrt{2}$.
- **b)** On a reporté depuis le centre la longueur de la diagonale entière ($4\sqrt{2}$) au lieu de la demi-diagonale ($2\sqrt{2}$).
- **c)** On a échangé abscisse et ordonnée des sommets trouvés : le côté de $A(2\;;\,1)$ à $(1\;;\,6)$ mesure $\sqrt{26}$ au lieu de $4$, ce n'est pas un carré.

</details>

Avis : 

---

### 9. `cqc-carre-faible-1`

**A regarder :** Une demonstration (Montrer que ... est un carre) est devenue : quelle justification suffit ?

**Enonce :**

Dans un repère orthonormé $(O,\vec{I},\vec{J})$, on donne les points $K(-2\;;\,-1)$, $L(2\;;\,-1)$, $M(2\;;\,3)$ et $N(-2\;;\,3)$.

Parmi les justifications suivantes, laquelle suffit à prouver que $KLMN$ est un carré ?

- a) $\vec{KL} = \vec{NM}$, $KL = KN = 4$ et $\vec{KL}$, $\vec{KN}$ sont orthogonaux
- b) $KL = KN = 4$
- c) $\vec{KL} = \vec{NM}$ et $\vec{KL}$, $\vec{KN}$ sont orthogonaux
- d) $\vec{KL} = \vec{NM}$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Pour montrer qu'un quadrilatère est un carré à partir des coordonnées de ses sommets, on établit successivement : qu'il s'agit d'un parallélogramme (côtés opposés portés par des vecteurs égaux), que ce parallélogramme est un losange (deux côtés consécutifs égaux), puis que l'un de ses angles est droit.

### Corrigé

*Étape 1 - parallélogramme.*
$$\vec{KL}(2-(-2)\;;\,-1-(-1)) = \vec{KL}(4\;;\,0) \qquad \vec{NM}(2-(-2)\;;\,3-3) = \vec{NM}(4\;;\,0)$$

$\vec{KL} = \vec{NM}$ : le quadrilatère $KLMN$ est un parallélogramme.

*Étape 2 - losange.*
$$KL = \sqrt{4^2+0^2} = 4 \qquad \vec{KN}(-2-(-2)\;;\,3-(-1)) = \vec{KN}(0\;;\,4) \quad \text{donc} \quad KN = \sqrt{0^2+4^2} = 4$$

$KL = KN$ : le parallélogramme est un losange.

*Étape 3 - angle droit.*
$$4 \times 0 + 0 \times 4 = 0$$

Les vecteurs $\vec{KL}(4\;;\,0)$ et $\vec{KN}(0\;;\,4)$ vérifient $xx' + yy' = 0$ : ils sont orthogonaux, l'angle en $K$ est droit.

Un losange ayant un angle droit est un carré. Le quadrilatère $KLMN$ est donc un **carré** de côté $4$.

### Pourquoi les autres réponses sont fausses

- **b)** Deux côtés consécutifs égaux ne suffisent pas : il faut aussi un parallélogramme et un angle droit.
- **c)** Cela prouve seulement que $KLMN$ est un rectangle : il manque l'égalité de deux côtés consécutifs.
- **d)** Cela prouve seulement que $KLMN$ est un parallélogramme.

</details>

Avis : 

---

### 10. `cqc-classes-moyenne-2`

**A regarder :** Le corrige d'origine disait a tort que [5 ; 10[ est 'ferme a droite' : corrige ici, la source en base est a corriger.

**Enonce :**

Voici la répartition de 90 employés d'une entreprise selon leur ancienneté (en années) :

$[0\,;\,5[$ : 20 employés ; $[5\,;\,10[$ : 25 employés ; $[10\,;\,15[$ : 30 employés ; $[15\,;\,20[$ : 15 employés.

Quel est le pourcentage des employés ayant une ancienneté strictement inférieure à 10 ans ?

- a) $45\,\%$
- b) environ $27{,}8\,\%$
- c) $50\,\%$
- d) environ $83{,}3\,\%$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Pour calculer un pourcentage cumulé, on identifie d'abord précisément quelles classes sont concernées en tenant compte du sens des crochets, puis on divise la somme de leurs effectifs par l'effectif total.

### Corrigé

*Classes concernées.* Une ancienneté « strictement inférieure à 10 ans » correspond aux classes $[0\,;\,5[$ et $[5\,;\,10[$, cette dernière étant ouverte en $10$ (la valeur $10$ est exclue) : elle est donc entièrement concernée. La classe $[10\,;\,15[$, qui commence à $10$ inclus, ne l'est pas.
$$20 + 25 = 45 \ \text{employés}$$

*Pourcentage.*
$$p = \frac{45}{90} \times 100 = 50$$

**50 %** des employés ont une ancienneté strictement inférieure à 10 ans.

*Contrôle.* L'effectif total est $20 + 25 + 30 + 15 = 90$, ce qui correspond bien à l'énoncé.

### Pourquoi les autres réponses sont fausses

- **a)** $45\,\%$ : $45$ est le nombre d'employés concernés, pas un pourcentage ; il faut le rapporter à $90$.
- **b)** environ $27{,}8\,\%$ : on n'a gardé que la classe $[5\,;\,10[$ ($25$ employés) en oubliant $[0\,;\,5[$.
- **d)** environ $83{,}3\,\%$ : on a ajouté à tort la classe $[10\,;\,15[$ ($75$ employés au total), qui correspond à $10$ ans et plus.

</details>

Avis : 

---

### 11. `cqc-comparaison-faible-1`

**A regarder :** Deux distracteurs ont la meme conclusion fausse avec des justifications differentes.

**Enonce :**

Comparer les nombres $-3{,}7$ et $-3{,}07$. Quelle affirmation est correcte ?

- a) $|-3{,}7| > |-3{,}07|$, donc $-3{,}7 > -3{,}07$
- b) $|-3{,}7| > |-3{,}07|$, donc $-3{,}7 < -3{,}07$
- c) $-3{,}7 = -3{,}07$
- d) $3{,}07 > 3{,}7$, donc $-3{,}07 < -3{,}7$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Pour comparer deux nombres négatifs, on compare d'abord leurs valeurs absolues : celui qui a la plus grande valeur absolue est en réalité le plus petit des deux nombres.

### Corrigé

*Valeurs absolues.*

$$|-3{,}7| = 3{,}7 \qquad\qquad |-3{,}07| = 3{,}07$$

Comme $3{,}7 > 3{,}07$, le nombre $-3{,}7$ a la plus grande valeur absolue : c'est donc lui le plus petit des deux.

$$-3{,}7 < -3{,}07$$

### Pourquoi les autres réponses sont fausses

- **a)** On a comparé les deux nombres comme s'ils étaient positifs : pour des nombres négatifs, la plus grande valeur absolue donne le plus petit nombre.
- **c)** $3{,}7 = 3{,}70$ et non $3{,}07$ : le zéro placé juste après la virgule change la valeur du nombre.
- **d)** $3{,}07 < 3{,}7$ (on compare $3{,}07$ et $3{,}70$) : un nombre qui a plus de chiffres après la virgule n'est pas forcément plus grand.

</details>

Avis : 

---

### 12. `cqc-conversion-faible-0`

**A regarder :** Contexte irrealiste remplace (bidon de 3,2 m3 devenu citerne).

**Enonce :**

Une citerne contient un volume de $3{,}2$ m³ d'huile végétale.

Quel est ce volume exprimé en litres ?

- a) $320$ L
- b) $32\,000$ L
- c) $0{,}0032$ L
- d) $3200$ L

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Pour convertir un volume de m³ en litres, on multiplie par $1000$, car $1$ m³ $= 1000$ L.

### Corrigé

$$3{,}2 \times 1000 = 3200$$

La citerne contient $3200$ litres d'huile.

### Pourquoi les autres réponses sont fausses

- **a)** On a multiplié par $100$ au lieu de $1000$ (confusion avec les unités d'aire).
- **b)** On a multiplié par $10\,000$ : un zéro de trop.
- **c)** On a divisé par $1000$ au lieu de multiplier : le m³ est une unité plus grande que le litre.

</details>

Avis : 

---

### 13. `cqc-coordonnees-d-un-vecteur-elevee-0`

**A regarder :** Le corrige d'origine utilise xx' + yy' = 0 (produit scalaire) comme verification : au programme de 3e ?

**Enonce :**

Dans un repère orthonormé, on donne les points $X(-1\,;\,-2)$, $Y(5\,;\,0)$ et $Z(0\,;\,-5)$. On admet que le triangle $XYZ$ est rectangle en $X$ (on peut le vérifier avec la réciproque du théorème de Pythagore).

Quelle est l'aire du triangle $XYZ$, en unités d'aire ?

- a) $20$
- b) $25$
- c) $200$
- d) $10$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Les coordonnées d'un vecteur $\overrightarrow{MN}$ s'obtiennent par $\overrightarrow{MN}\,(x_N - x_M\,;\,y_N - y_M)$. Dans un repère orthonormé, la longueur au carré d'un côté est la somme des carrés des coordonnées du vecteur correspondant. Pour montrer qu'un triangle est rectangle, on vérifie la réciproque du théorème de Pythagore. Lorsque le triangle est rectangle, son aire est la moitié du produit des deux côtés de l'angle droit.

### Corrigé

**Coordonnées des vecteurs.**

$$\overrightarrow{XY}\,(5-(-1)\,;\,0-(-2)) = (6\,;\,2)$$

$$\overrightarrow{XZ}\,(0-(-1)\,;\,-5-(-2)) = (1\,;\,-3)$$

$$\overrightarrow{YZ}\,(0-5\,;\,-5-0) = (-5\,;\,-5)$$

**Le triangle est rectangle en $X$.**

$$XY^2 = 6^2 + 2^2 = 40, \quad XZ^2 = 1^2 + (-3)^2 = 10, \quad YZ^2 = (-5)^2 + (-5)^2 = 50$$

$$XY^2 + XZ^2 = 40 + 10 = 50 = YZ^2$$

L'égalité de Pythagore est vérifiée, donc le triangle $XYZ$ est rectangle en $X$.

**Aire du triangle $XYZ$.**

Les côtés de l'angle droit sont $[XY]$ et $[XZ]$, de longueurs $XY = \sqrt{40}$ et $XZ = \sqrt{10}$ :
$$\text{Aire} = \frac{XY \times XZ}{2} = \frac{\sqrt{40} \times \sqrt{10}}{2} = \frac{\sqrt{400}}{2} = \frac{20}{2} = 10$$

L'aire du triangle $XYZ$ est de **10 unités d'aire**.

### Pourquoi les autres réponses sont fausses
- **a)** $20$ est le produit $XY \times XZ$ : on a oublié de diviser par 2.
- **b)** $25$ vient de $\dfrac{XY^2 + XZ^2}{2} = \dfrac{50}{2}$ : on a utilisé la somme des carrés des côtés au lieu du produit des longueurs.
- **c)** $200$ vient de $\dfrac{40 \times 10}{2}$ : on a multiplié les carrés des longueurs au lieu des longueurs elles-mêmes.

</details>

Avis : 

---

### 14. `cqc-coordonnees-d-un-vecteur-moyenne-2`

**A regarder :** La condition d'orthogonalite xx' + yy' = 0 apparait en prolongement : est-elle au programme de 3e ?

**Enonce :**

Dans un repère orthonormé, on donne les points $R(0\,;\,1)$, $S(4\,;\,3)$ et $T(1\,;\,-1)$.

Quelles sont les coordonnées des vecteurs $\overrightarrow{RS}$ et $\overrightarrow{RT}$ ?

- a) $\overrightarrow{RS}\,(4\,;\,2)$ et $\overrightarrow{RT}\,(1\,;\,0)$
- b) $\overrightarrow{RS}\,(4\,;\,2)$ et $\overrightarrow{RT}\,(1\,;\,-2)$
- c) $\overrightarrow{RS}\,(-4\,;\,-2)$ et $\overrightarrow{RT}\,(-1\,;\,2)$
- d) $\overrightarrow{RS}\,(4\,;\,4)$ et $\overrightarrow{RT}\,(1\,;\,0)$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Les coordonnées d'un vecteur $\overrightarrow{MN}$ s'obtiennent en retranchant les coordonnées du point de départ à celles du point d'arrivée : $\overrightarrow{MN}\,(x_N - x_M\,;\,y_N - y_M)$. Dans un repère orthonormé, deux vecteurs $\overrightarrow{u}\,(x\,;\,y)$ et $\overrightarrow{v}\,(x'\,;\,y')$ sont orthogonaux lorsque $xx' + yy'$ est nul.

### Corrigé

*Coordonnées de $\overrightarrow{RS}$.*
$$\overrightarrow{RS}\,(4-0\,;\,3-1) = (4\,;\,2)$$

*Coordonnées de $\overrightarrow{RT}$.*
$$\overrightarrow{RT}\,(1-0\,;\,-1-1) = (1\,;\,-2)$$

*Prolongement.* $4 \times 1 + 2 \times (-2) = 4 - 4 = 0$ : les vecteurs $\overrightarrow{RS}$ et $\overrightarrow{RT}$ sont orthogonaux.

### Pourquoi les autres réponses sont fausses
- **a)** $\overrightarrow{RT}\,(1\,;\,0)$ vient d'une erreur de signe : $-1 - 1 = -2$ et non $0$.
- **c)** $(-4\,;\,-2)$ et $(-1\,;\,2)$ sont les coordonnées de $\overrightarrow{SR}$ et $\overrightarrow{TR}$ : on a soustrait dans le mauvais ordre.
- **d)** $\overrightarrow{RS}\,(4\,;\,4)$ et $\overrightarrow{RT}\,(1\,;\,0)$ viennent de l'addition des ordonnées ($3 + 1$ et $-1 + 1$) au lieu de leur soustraction.

</details>

Avis : 

---



# Vague 2 (106 QCM en ligne)

Date : 2026-10-27. Questions de la vague 2 ou une methode a ete remplacee, une formulation est discutable ou une precision a ete ajoutee. Les 106 questions ont ete resolues a l'aveugle par un relecteur independant (106 accords sur 106) ; ce document sert a juger ce qu'un relecteur modele ne juge pas : le niveau 3e / BEPC, le realisme des distracteurs et les conventions d'enseignement.

Pour chaque question : **OK**, **a corriger** (dire quoi), ou **a retirer**.

### 1. `cqc-mesure-d-angle-moyenne-0`

**A regarder :** 'A 1 degre pres par exces' donne 54 (cle) alors que l'arrondi donne 53, qui est aussi un choix : cette convention d'examen est-elle bien celle du BEPC ?

**Enonce :**

Dans un triangle $HBC$ rectangle en $H$, on donne $BH = 12$ cm et $HC = 9$ cm.

Quelle est la mesure de l'angle $\widehat{HCB}$ à $1°$ près par excès ?

- a) $53°$
- b) $54°$
- c) $37°$
- d) $42°$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Dans un triangle rectangle, la tangente d'un angle aigu est le quotient du côté opposé par le côté adjacent. « À $1°$ près par excès » signifie que l'on retient le plus petit entier supérieur ou égal à la valeur obtenue, et non l'entier le plus proche.

### Corrigé

Le triangle $HBC$ est rectangle en $H$. Vu du sommet $C$, le côté opposé est $[BH]$ et le côté adjacent est $[HC]$.
$$\tan(\widehat{HCB}) = \frac{BH}{HC} = \frac{12}{9} = \frac{4}{3} \approx 1{,}333$$

*Recherche de l'angle.*
$$\widehat{HCB} = \tan^{-1}\left(\frac{4}{3}\right) \approx 53{,}13°$$

*Arrondi par excès à $1°$ près.* On cherche le plus petit entier supérieur ou égal à $53{,}13$ :
$$53 < 53{,}13 < 54 \quad \Longrightarrow \quad \widehat{HCB} \approx 54°$$

Réponse **b)**.

### Piège à éviter
« Par excès » n'est pas « au plus proche » : l'entier le plus proche de $53{,}13$ est $53$, mais la consigne impose de majorer. La réponse est bien $54°$, pas $53°$.

### Pourquoi les autres réponses sont fausses

- **a)** $53°$ est l'arrondi à l'entier le plus proche, pas l'arrondi par excès demandé.
- **c)** On a inversé côté opposé et côté adjacent : $\tan^{-1}\left(\frac{9}{12}\right) \approx 36{,}87°$, d'où $37°$ par excès, qui est l'angle en $B$.
- **d)** On a pris $BH = 12$ cm pour l'hypoténuse et utilisé $\cos^{-1}\left(\frac{9}{12}\right) \approx 41{,}4°$, alors que l'hypoténuse est $[BC]$.

</details>

Avis : 

---

### 2. `cqc-geometrie-analytique-moyenne-2`

**A regarder :** L'enonce ne disait pas que le repere est orthonorme : precision ajoutee apres la relecture aveugle. Cle et calcul inchanges.

**Enonce :**

Dans un repère orthonormé, on donne les points $P(1\,;\,1)$, $Q(2\,;\,3)$ et $R(7\,;\,-2)$.

Que peut-on dire du triangle $PQR$ ?

- a) Il est rectangle en $Q$.
- b) Il est rectangle en $R$.
- c) Il n'est pas rectangle.
- d) Il est rectangle en $P$.

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

La réciproque du théorème de Pythagore permet de démontrer qu'un triangle est rectangle à partir des coordonnées de ses sommets : si le carré du plus grand côté est égal à la somme des carrés des deux autres, le triangle est rectangle, l'angle droit étant au sommet opposé au plus grand côté.

### Corrigé

*Calcul de $PQ^2$.*

$$PQ^2 = (2-1)^2 + (3-1)^2 = 1 + 4 = 5$$

*Calcul de $PR^2$.*

$$PR^2 = (7-1)^2 + (-2-1)^2 = 36 + 9 = 45$$

*Calcul de $QR^2$.*

$$QR^2 = (7-2)^2 + (-2-3)^2 = 25 + 25 = 50$$

*Comparaison.* $QR$ est le plus grand côté ($QR^2 = 50$).

$$PQ^2 + PR^2 = 5 + 45 = 50 = QR^2$$

D'après la réciproque du théorème de Pythagore, le triangle $PQR$ est **rectangle en $P$**, le sommet opposé au plus grand côté $[QR]$.

### Pourquoi les autres réponses sont fausses

- **a)** Rectangle en $Q$ : $Q$ est une extrémité de l'hypoténuse $[QR]$, alors que l'angle droit est au sommet opposé.
- **b)** Rectangle en $R$ : même confusion, $R$ est l'autre extrémité de l'hypoténuse $[QR]$.
- **c)** Non rectangle : la relation $PQ^2 + PR^2 = QR^2$ est vérifiée ; cette conclusion vient d'une erreur de signe dans $(-2-1)^2$ ou $(-2-3)^2$, ou d'une comparaison avec le mauvais côté.

</details>

Avis : 

---

### 3. `cqc-forme-reduite-moyenne-3`

**A regarder :** Equation cartesienne et critere a x a' = -1 : au programme de 3e dans tous les cas ? Terme 'cartesienne' plutot de Seconde.

**Enonce :**

On considère les droites $(D_1)$ d'équation cartésienne $x + 3y - 6 = 0$ et $(D_2)$ d'équation $y = 3x - 5$.

Quelle affirmation est exacte ?

- a) La pente de $(D_1)$ est $-\dfrac{1}{3}$, donc $(D_1)$ et $(D_2)$ sont perpendiculaires.
- b) La pente de $(D_1)$ est $-1$, donc $(D_1)$ et $(D_2)$ sont sécantes sans être perpendiculaires.
- c) La pente de $(D_1)$ est $\dfrac{1}{3}$, donc $(D_1)$ et $(D_2)$ sont sécantes sans être perpendiculaires.
- d) La pente de $(D_1)$ est $3$, donc $(D_1)$ et $(D_2)$ sont parallèles.

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Deux droites non verticales, de pentes respectives $m_1$ et $m_2$, sont perpendiculaires si et seulement si le produit de leurs pentes vaut $-1$ : $m_1 \times m_2 = -1$.

### Corrigé

*Mise sous forme réduite de $(D_1)$.* On isole $y$ dans $x + 3y - 6 = 0$ :

$$3y = -x + 6$$

$$y = -\dfrac{1}{3}x + 2$$

$(D_1)$ a donc pour pente $m_1 = -\dfrac{1}{3}$.

*Pente de $(D_2)$.* $(D_2)$ est déjà sous forme réduite $y = 3x - 5$, donc $m_2 = 3$.

*Produit des pentes.*

$$m_1 \times m_2 = -\frac{1}{3} \times 3 = -1$$

Le produit des pentes vaut $-1$, donc les droites $(D_1)$ et $(D_2)$ sont perpendiculaires.

### Pourquoi les autres réponses sont fausses

- **b)** On a oublié de diviser par $3$ en isolant $y$ : $3y = -x + 6$ donne $y = -\dfrac{1}{3}x + 2$, pas $y = -x + 6$.
- **c)** Erreur de signe : en faisant passer $x$ dans l'autre membre, il devient $-x$, donc la pente est $-\dfrac{1}{3}$ et non $\dfrac{1}{3}$.
- **d)** On a pris le coefficient de $y$ dans l'équation cartésienne pour la pente ; la pente ne se lit qu'une fois l'équation mise sous la forme $y = mx + p$.

</details>

Avis : 

---

### 4. `cqc-droite-moyenne-4`

**A regarder :** Methode remplacee : produit scalaire remplace par le produit des coefficients directeurs ; consigne 'justifie' retiree.

**Enonce :**

Dans un repère orthonormé, la droite $(D_1)$ a pour vecteur directeur $\vec{u}(4\,;\,6)$ et la droite $(D_2)$ a pour vecteur directeur $\vec{v}(3\,;\,-2)$.

Quelle est la position relative des droites $(D_1)$ et $(D_2)$ ?

- a) Parallèles
- b) Confondues
- c) Sécantes mais pas perpendiculaires
- d) Perpendiculaires

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Deux droites de vecteurs directeurs $\vec{u}(a_1\,;\,b_1)$ et $\vec{v}(a_2\,;\,b_2)$ sont parallèles si et seulement si $\vec{u}$ et $\vec{v}$ sont colinéaires, c'est-à-dire $a_1b_2 - a_2b_1 = 0$. Une droite de vecteur directeur $(a\,;\,b)$ avec $a \neq 0$ a pour coefficient directeur $\dfrac{b}{a}$ ; dans un repère orthonormé, deux droites sont perpendiculaires si et seulement si le produit de leurs coefficients directeurs vaut $-1$.

### Corrigé

*Test de colinéarité (parallélisme).*

$$a_1b_2 - a_2b_1 = 4\times(-2) - 3\times6 = -8-18=-26 \neq 0$$

Le résultat n'est pas nul : $\vec{u}$ et $\vec{v}$ ne sont pas colinéaires, donc $(D_1)$ et $(D_2)$ ne sont pas parallèles (ni confondues) : elles sont sécantes.

*Test de perpendicularité.* Coefficient directeur de $(D_1)$ : $m_1 = \dfrac{6}{4} = \dfrac{3}{2}$. Coefficient directeur de $(D_2)$ : $m_2 = \dfrac{-2}{3}$.

$$m_1 \times m_2 = \frac{3}{2} \times \left(-\frac{2}{3}\right) = -1$$

Le produit vaut $-1$ : les droites sont perpendiculaires.

**Conclusion** : $(D_1)$ et $(D_2)$ ne sont pas parallèles, mais elles sont perpendiculaires.

### Pourquoi les autres réponses sont fausses
- **a)** Le test de colinéarité donne $-26 \neq 0$ : les vecteurs ne sont pas colinéaires, donc les droites ne sont pas parallèles.
- **b)** Des droites confondues sont en particulier parallèles, ce qui est exclu par le même test.
- **c)** On s'est arrêté au test de parallélisme sans vérifier la perpendicularité : $m_1 \times m_2 = -1$.

</details>

Avis : 

---

### 5. `cqc-diagonales-moyenne-0`

**A regarder :** Methode remplacee : produit scalaire remplace par une comparaison de longueurs (cotes et diagonales).

**Enonce :**

Le plan est muni d'un repère orthonormé. On considère les points $K(2\,;-1)$, $M(0\,;3)$ et $N(5\,;1)$. Le point $M'$ est le symétrique de $M$ par rapport à $K$, et le point $N'$ est le symétrique de $N$ par rapport à $K$.

Quelle est la nature la plus précise du quadrilatère $MNM'N'$ ?

- a) Un carré
- b) Un losange qui n'est pas un rectangle
- c) Un parallélogramme qui n'est ni un rectangle ni un losange
- d) Un rectangle qui n'est pas un losange

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Un quadrilatère dont les diagonales ont le même milieu est un parallélogramme. Ce parallélogramme est un losange si deux côtés consécutifs ont la même longueur, et un rectangle si ses diagonales ont la même longueur.

### Corrigé

*Coordonnées.* $K$ est le milieu de $[MM']$, donc $x_{M'} = 2x_K - x_M$ et $y_{M'} = 2y_K - y_M$ :

$$M'(2 \times 2 - 0\,;\,2 \times (-1) - 3) = (4\,;\,-5)$$

De même, $K$ est le milieu de $[NN']$ :

$$N'(2 \times 2 - 5\,;\,2 \times (-1) - 1) = (-1\,;\,-3)$$

*Parallélogramme.* Les diagonales $[MM']$ et $[NN']$ ont le même milieu $K$ : $MNM'N'$ est un **parallélogramme**.

*Losange ?* On compare deux côtés consécutifs :

$$MN = \sqrt{(5-0)^2+(1-3)^2} = \sqrt{25+4} = \sqrt{29}$$
$$NM' = \sqrt{(4-5)^2+(-5-1)^2} = \sqrt{1+36} = \sqrt{37}$$

$MN \neq NM'$ : ce n'est **pas** un losange.

*Rectangle ?* On compare les diagonales :

$$MM' = \sqrt{(4-0)^2+(-5-3)^2} = \sqrt{16+64} = \sqrt{80}$$
$$NN' = \sqrt{(-1-5)^2+(-3-1)^2} = \sqrt{36+16} = \sqrt{52}$$

$MM' \neq NN'$ : ce n'est **pas** un rectangle.

$MNM'N'$ est un parallélogramme qui n'est ni un rectangle ni un losange.

### Pourquoi les autres réponses sont fausses

- **a)** Un carré devrait avoir des côtés consécutifs égaux et des diagonales égales, or $\sqrt{29} \neq \sqrt{37}$ et $\sqrt{80} \neq \sqrt{52}$.
- **b)** Les côtés consécutifs $MN = \sqrt{29}$ et $NM' = \sqrt{37}$ sont différents : ce n'est pas un losange.
- **d)** Les diagonales $MM' = \sqrt{80}$ et $NN' = \sqrt{52}$ sont différentes : ce n'est pas un rectangle.

</details>

Avis : 

---

### 6. `cqc-diagonales-moyenne-1`

**A regarder :** La source parlait d'un losange alors que les diagonales egales en font un carre ; unite 'centimetre' ajoutee a l'enonce.

**Enonce :**

Le plan est muni d'un repère orthonormé (unité : le centimètre). Un cerf-volant a la forme d'un losange $WXYZ$ dont les diagonales sont $[WY]$ et $[XZ]$. On donne $W(-3\,;0)$, $Y(5\,;0)$, $X(1\,;4)$ et $Z(1\,;-4)$.

Quelle est l'aire de ce cerf-volant ?

- a) $64 \ \text{cm}^{2}$
- b) $16 \ \text{cm}^{2}$
- c) $16\sqrt{2} \ \text{cm}^{2}$
- d) $32 \ \text{cm}^{2}$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Dans un losange, les diagonales se coupent en leur milieu et sont perpendiculaires ; son aire vaut la moitié du produit de ses deux diagonales.

### Corrigé

*Longueurs des diagonales.* $W$ et $Y$ ont la même ordonnée : $WY = |5 - (-3)| = 8$. $X$ et $Z$ ont la même abscisse : $XZ = |4 - (-4)| = 8$.

*Milieu commun.* Milieu de $[WY]$ : $\left(\dfrac{-3+5}{2}\,;\,\dfrac{0+0}{2}\right) = (1\,;0)$. Milieu de $[XZ]$ : $\left(\dfrac{1+1}{2}\,;\,\dfrac{4+(-4)}{2}\right) = (1\,;0)$. Les deux diagonales ont bien le même milieu.

*Perpendicularité.* $[WY]$ est horizontale et $[XZ]$ est verticale : elles sont perpendiculaires, ce qui confirme la forme de losange (ses diagonales étant de plus de même longueur, c'est même un carré).

*Aire.* $$\mathcal{A} = \frac{WY \times XZ}{2} = \frac{8 \times 8}{2} = \frac{64}{2} = 32$$

L'aire du cerf-volant vaut $32 \ \text{cm}^{2}$.

### Pourquoi les autres réponses sont fausses

- **a)** $64 \ \text{cm}^{2}$ est le produit des diagonales : on a oublié de diviser par $2$.
- **b)** $16 \ \text{cm}^{2}$ vient du produit des demi-diagonales $4 \times 4$ : on a divisé deux fois par $2$.
- **c)** $16\sqrt{2}$ est le périmètre du losange (côté $\sqrt{4^2+4^2} = 4\sqrt{2}$), pas son aire.

</details>

Avis : 

---

### 7. `cqc-droite-faible-0`

**A regarder :** Question oui/non 'sont-ils alignes ?' reformulee en 'trouver k tel que AC = k AB' (k = 2).

**Enonce :**

On donne les points $A(1\,;\,2)$, $B(3\,;\,6)$ et $C(5\,;\,10)$ dans un repère.

Ces trois points sont alignés. Quel est le réel $k$ tel que $\vec{AC} = k\,\vec{AB}$ ?

- a) $k = \dfrac{1}{2}$
- b) $k = 4$
- c) $k = -2$
- d) $k = 2$

**Cle :** d

<details><summary>Corrige</summary>

### Rappel de méthode

Trois points $A$, $B$ et $C$ sont alignés si et seulement si les vecteurs $\vec{AB}$ et $\vec{AC}$ sont colinéaires, c'est-à-dire si leurs coordonnées respectives $(x_1\,;\,y_1)$ et $(x_2\,;\,y_2)$ vérifient $x_1y_2 - x_2y_1 = 0$. Il existe alors un réel $k$ tel que $\vec{AC} = k\,\vec{AB}$, que l'on obtient en comparant les coordonnées.

### Corrigé

*Coordonnées des vecteurs.*

$$\vec{AB}\,(x_B - x_A\,;\,y_B - y_A) = \vec{AB}\,(3-1\,;\,6-2) = \vec{AB}\,(2\,;\,4)$$

$$\vec{AC}\,(x_C - x_A\,;\,y_C - y_A) = \vec{AC}\,(5-1\,;\,10-2) = \vec{AC}\,(4\,;\,8)$$

*Test de colinéarité.*

$$2 \times 8 - 4 \times 4 = 16 - 16 = 0$$

Le résultat est nul : les vecteurs $\vec{AB}$ et $\vec{AC}$ sont colinéaires, donc $A$, $B$ et $C$ sont alignés.

*Valeur de $k$.* $4 = k \times 2$ et $8 = k \times 4$ donnent toutes deux $k = 2$.

**Conclusion** : $\vec{AC} = 2\,\vec{AB}$, donc $k = 2$.

### Pourquoi les autres réponses sont fausses
- **a)** Rapport inversé : $\dfrac{1}{2}$ est le réel tel que $\vec{AB} = \dfrac{1}{2}\,\vec{AC}$.
- **b)** On a pris l'abscisse de $\vec{AC}$ ($4$) au lieu du rapport des coordonnées.
- **c)** Erreur de sens : $\vec{AC}$ et $\vec{AB}$ ont des coordonnées de même signe, donc $k$ est positif.

</details>

Avis : 

---

### 8. `cqc-droites-perpendiculaires-elevee-5`

**A regarder :** Critere xx' + yy' = 0 (produit scalaire) remplace par la reciproque de Pythagore ; question reduite a l'aire (12,5).

**Enonce :**

Dans un repère orthonormé, on donne les points $A(4\;;\,6)$, $B(1\;;\,2)$ et $C(5\;;\,-1)$. Quelle est l'aire du triangle $ABC$, en unités d'aire ?

- a) $25$
- b) $10$
- c) $12{,}5$
- d) $\dfrac{25\sqrt{2}}{2}$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

La distance entre deux points $P(x_P\;;\,y_P)$ et $Q(x_Q\;;\,y_Q)$ d'un repère orthonormé vaut $PQ = \sqrt{(x_Q - x_P)^2 + (y_Q - y_P)^2}$. Si $AB^2 + BC^2 = AC^2$, la réciproque du théorème de Pythagore montre que le triangle est rectangle en $B$. Son aire s'obtient alors avec les deux côtés de l'angle droit : $\text{Aire} = \dfrac{1}{2} \times \text{côté}_1 \times \text{côté}_2$.

### Corrigé

*Carrés des longueurs des côtés.*

$$BA^2 = (4 - 1)^2 + (6 - 2)^2 = 9 + 16 = 25$$

$$BC^2 = (5 - 1)^2 + (-1 - 2)^2 = 16 + 9 = 25$$

$$AC^2 = (5 - 4)^2 + (-1 - 6)^2 = 1 + 49 = 50$$

*Nature du triangle.* $BA^2 + BC^2 = 25 + 25 = 50 = AC^2$ : d'après la réciproque du théorème de Pythagore, le triangle $ABC$ est **rectangle en $B$**, et $[AC]$ est l'hypoténuse.

*Longueurs des côtés de l'angle droit.* $BA = \sqrt{25} = 5$ et $BC = \sqrt{25} = 5$.

*Calcul de l'aire.*

$$\text{Aire} = \frac{1}{2} \times BA \times BC = \frac{1}{2} \times 5 \times 5 = \frac{25}{2} = 12{,}5$$

L'aire du triangle $ABC$ vaut $12{,}5$ unités d'aire : réponse **c)**.

*Contrôle.* $BA = BC = 5$ : le triangle est rectangle et isocèle en $B$, et l'hypoténuse vaut bien $AC = \sqrt{50} = 5\sqrt{2}$.

### Pourquoi les autres réponses sont fausses

- **a)** $25$ : c'est le produit $BA \times BC$, on a oublié de le diviser par $2$.
- **b)** $10$ : c'est la somme $BA + BC$, qui n'est pas une aire.
- **d)** $\dfrac{25\sqrt{2}}{2}$ : on a pris l'hypoténuse $AC = 5\sqrt{2}$ comme côté de l'angle droit, au lieu de $BC$.

</details>

Avis : 

---

### 9. `cqc-droites-perpendiculaires-moyenne-3`

**A regarder :** Critere xx' + yy' = 0 remplace par le produit des coefficients directeurs = -1.

**Enonce :**

Dans un repère orthonormé, le vecteur $\vec{u}\,(3\;;\,-2)$ dirige la droite $(D_1)$ et le vecteur $\vec{v}\,(4\;;\,6)$ dirige la droite $(D_2)$. On note $a_1$ et $a_2$ les coefficients directeurs de $(D_1)$ et $(D_2)$. Quelle est la valeur du produit $a_1 \times a_2$ ?

- a) $1$
- b) $\dfrac{5}{6}$
- c) $-1$
- d) $-\dfrac{4}{9}$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Une droite dirigée par un vecteur $\vec{w}\,(x\;;\,y)$ avec $x \neq 0$ a pour coefficient directeur $a = \dfrac{y}{x}$ (quand on avance de $x$ en abscisse, on monte de $y$ en ordonnée). Deux droites sont perpendiculaires si et seulement si le produit de leurs coefficients directeurs vaut $-1$.

### Corrigé

*Coefficients directeurs.*

$$a_1 = \frac{-2}{3} = -\frac{2}{3} \qquad a_2 = \frac{6}{4} = \frac{3}{2}$$

*Produit.*

$$a_1 \times a_2 = -\frac{2}{3} \times \frac{3}{2} = -\frac{6}{6} = -1$$

Le produit vaut $-1$ : réponse **c)**. Les droites $(D_1)$ et $(D_2)$ sont donc **perpendiculaires**.

### Pourquoi les autres réponses sont fausses

- **a)** $1$ : on a oublié le signe moins de $-2$ et pris $a_1 = \dfrac{2}{3}$.
- **b)** $\dfrac{5}{6}$ : c'est la somme $a_1 + a_2 = -\dfrac{2}{3} + \dfrac{3}{2}$, pas le produit.
- **d)** $-\dfrac{4}{9}$ : pour $\vec{v}$, on a calculé $\dfrac{x}{y} = \dfrac{4}{6} = \dfrac{2}{3}$ au lieu de $\dfrac{y}{x}$.

</details>

Avis : 

---

### 10. `cqc-parallelisme-moyenne-2`

**A regarder :** Methode du determinant remplacee par l'egalite des coefficients directeurs (reponse 9 inchangee).

**Enonce :**

Dans un repère orthonormé, on donne $A(1\,;2)$, $B(4\,;8)$, $C(-2\,;-1)$ et $D(3\,;y)$. Quelle valeur de $y$ rend les droites $(AB)$ et $(CD)$ parallèles ?

- a) $9$
- b) $1{,}5$
- c) $10$
- d) $1$

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Deux droites non parallèles à l'axe des ordonnées sont parallèles si et seulement si elles ont le même coefficient directeur. Le coefficient directeur de la droite $(AB)$ est $\dfrac{y_B - y_A}{x_B - x_A}$.

### Corrigé

*Coefficient directeur de $(AB)$.* $$\frac{8 - 2}{4 - 1} = \frac{6}{3} = 2$$

*Coefficient directeur de $(CD)$.* $$\frac{y - (-1)}{3 - (-2)} = \frac{y + 1}{5}$$

*Condition de parallélisme.* $$\frac{y + 1}{5} = 2 \quad \Longleftrightarrow \quad y + 1 = 10 \quad \Longleftrightarrow \quad y = 9$$

*Vérification.* Avec $D(3\,;9)$ : $\dfrac{9 - (-1)}{3 - (-2)} = \dfrac{10}{5} = 2$. Les droites $(AB)$ et $(CD)$ ont le même coefficient directeur : elles sont **parallèles**.

### Pourquoi les autres réponses sont fausses

- **b)** $1{,}5$ : on a pris l'inverse du coefficient directeur ($\dfrac{3}{6} = \dfrac{1}{2}$ au lieu de $2$).
- **c)** $10$ : on a résolu $y + 1 = 10$ en oubliant de retrancher $1$.
- **d)** $1$ : erreur de signe sur l'abscisse, $3 + (-2) = 1$ au lieu de $3 - (-2) = 5$.

</details>

Avis : 

---

### 11. `cqc-geometrie-analytique-moyenne-1`

**A regarder :** 'Montrer l'alignement' devient 'quel k verifie AC = k AB ?' ; test de colinearite remplace par la proportionnalite des coordonnees.

**Enonce :**

On donne les points $A(-2\,;\,1)$, $B(1\,;\,4)$ et $C(3\,;\,6)$. Ces trois points sont alignés.

Quel est le réel $k$ tel que $\overrightarrow{AC} = k\,\overrightarrow{AB}$ ?

- a) $k = \dfrac{3}{5}$
- b) $k = \dfrac{5}{3}$
- c) $k = \dfrac{2}{3}$
- d) $k = -\dfrac{5}{3}$

**Cle :** b

<details><summary>Corrige</summary>

### Rappel de méthode

Trois points $A$, $B$, $C$ sont alignés si et seulement si les vecteurs $\overrightarrow{AB}$ et $\overrightarrow{AC}$ sont colinéaires, c'est-à-dire si leurs coordonnées sont proportionnelles. Le coefficient de proportionnalité $k$ vérifie $\overrightarrow{AC} = k\,\overrightarrow{AB}$ : on l'obtient en divisant une coordonnée de $\overrightarrow{AC}$ par la coordonnée correspondante de $\overrightarrow{AB}$.

### Corrigé

*Coordonnées de $\overrightarrow{AB}$.*

$$\overrightarrow{AB}\begin{pmatrix} 1 - (-2) \\ 4 - 1 \end{pmatrix} = \begin{pmatrix} 3 \\ 3 \end{pmatrix}$$

*Coordonnées de $\overrightarrow{AC}$.*

$$\overrightarrow{AC}\begin{pmatrix} 3 - (-2) \\ 6 - 1 \end{pmatrix} = \begin{pmatrix} 5 \\ 5 \end{pmatrix}$$

*Coefficient de proportionnalité.*

$$\frac{5}{3} = \frac{5}{3}$$

Les coordonnées sont proportionnelles : $\overrightarrow{AC} = \dfrac{5}{3}\,\overrightarrow{AB}$. Les vecteurs sont colinéaires, ce qui confirme que $A$, $B$ et $C$ sont **alignés**, $C$ se trouvant sur la droite $(AB)$, au-delà de $B$.

Donc $k = \dfrac{5}{3}$.

### Pourquoi les autres réponses sont fausses

- **a)** $\dfrac{3}{5}$ : on a divisé les coordonnées de $\overrightarrow{AB}$ par celles de $\overrightarrow{AC}$, ce qui donne $\overrightarrow{AB} = \dfrac{3}{5}\,\overrightarrow{AC}$.
- **c)** $\dfrac{2}{3}$ : on a utilisé $\overrightarrow{BC}(2\,;\,2)$ au lieu de $\overrightarrow{AC}$.
- **d)** $-\dfrac{5}{3}$ : on a calculé $\overrightarrow{BA}(-3\,;\,-3)$ au lieu de $\overrightarrow{AB}$.

</details>

Avis : 

---

### 12. `cqc-geometrie-analytique-moyenne-3`

**A regarder :** 'Montrer que le triangle est isocele' devient 'quelle est la nature du triangle ?' (isocele non rectangle).

**Enonce :**

On donne les points $A(0\,;\,0)$, $B(6\,;\,2)$ et $C(2\,;\,6)$.

Quelle est la nature du triangle $ABC$ ?

- a) Rectangle isocèle en $A$
- b) Équilatéral
- c) Isocèle en $A$, non rectangle
- d) Quelconque

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Pour déterminer la nature d'un triangle dans un repère, on calcule les longueurs de ses trois côtés à l'aide de la formule de la distance, $MN = \sqrt{(x_N - x_M)^2 + (y_N - y_M)^2}$, puis on compare ces longueurs (côtés égaux) et leurs carrés (réciproque du théorème de Pythagore).

### Corrigé

*Longueur $AB$.*

$$AB = \sqrt{(6-0)^2 + (2-0)^2} = \sqrt{36 + 4} = \sqrt{40} = 2\sqrt{10}$$

*Longueur $AC$.*

$$AC = \sqrt{(2-0)^2 + (6-0)^2} = \sqrt{4 + 36} = \sqrt{40} = 2\sqrt{10}$$

*Longueur $BC$.*

$$BC = \sqrt{(2-6)^2 + (6-2)^2} = \sqrt{16 + 16} = \sqrt{32} = 4\sqrt{2}$$

*Conclusion.*

$$AB = AC = 2\sqrt{10} \quad \text{et} \quad BC = 4\sqrt{2} \neq 2\sqrt{10}$$

Le triangle a deux côtés égaux issus de $A$ : il est **isocèle en $A$**. De plus, $AB^2 + AC^2 = 80 \neq 32$ et $AB^2 = 40 \neq AC^2 + BC^2 = 72$ : aucune relation de Pythagore n'est vérifiée, il n'est pas rectangle.

### Pourquoi les autres réponses sont fausses

- **a)** Rectangle isocèle en $A$ : il faudrait $AB^2 + AC^2 = BC^2$, or $40 + 40 = 80 \neq 32$.
- **b)** Équilatéral : $BC = 4\sqrt{2}$ est différent de $AB = AC = 2\sqrt{10}$.
- **d)** Quelconque : on a oublié de comparer $AB$ et $AC$, qui sont égaux.

</details>

Avis : 

---

### 13. `cqc-parallelogramme-moyenne-2`

**A regarder :** Nature la plus precise (rectangle) : calcul des cotes ajoute pour exclure losange et carre.

**Enonce :**

Dans un repère orthonormé, on considère le quadrilatère $WXYZ$ de sommets $W(-2;-6)$, $X(2;-3)$, $Y(-4;5)$ et $Z(-8;2)$. Quelle est la nature la plus précise de $WXYZ$ ?

- a) Un rectangle
- b) Un losange
- c) Un carré
- d) Un parallélogramme quelconque

**Cle :** a

<details><summary>Corrige</summary>

### Rappel de méthode

Un quadrilatère est un parallélogramme lorsque ses deux diagonales ont le même milieu. Un parallélogramme est un rectangle lorsque ses diagonales ont la même longueur, et un losange lorsque deux côtés consécutifs ont la même longueur ; un carré est à la fois rectangle et losange. Les longueurs se calculent avec $\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}$.

### Corrigé

*Parallélogramme.* Les diagonales sont $[WY]$ et $[XZ]$.

Milieu de $[WY]$ : $\left(\dfrac{-2+(-4)}{2};\dfrac{-6+5}{2}\right)=(-3;-0{,}5)$.

Milieu de $[XZ]$ : $\left(\dfrac{2+(-8)}{2};\dfrac{-3+2}{2}\right)=(-3;-0{,}5)$.

Les diagonales ont le même milieu, donc $WXYZ$ est un parallélogramme.

*Diagonales.*

$WY=\sqrt{(-4-(-2))^2+(5-(-6))^2}=\sqrt{4+121}=\sqrt{125}=5\sqrt{5}$

$XZ=\sqrt{(-8-2)^2+(2-(-3))^2}=\sqrt{100+25}=\sqrt{125}=5\sqrt{5}$

Les diagonales ont la même longueur : $WXYZ$ est un rectangle.

*Côtés consécutifs.*

$WX=\sqrt{(2-(-2))^2+(-3-(-6))^2}=\sqrt{16+9}=5$

$XY=\sqrt{(-4-2)^2+(5-(-3))^2}=\sqrt{36+64}=10$

$WX \neq XY$ : ce n'est pas un losange, donc pas un carré. $WXYZ$ est un **rectangle**.

### Pourquoi les autres réponses sont fausses

- **b)** Losange : il faudrait deux côtés consécutifs égaux, or $WX = 5$ et $XY = 10$.
- **c)** Carré : un carré est aussi un losange, ce qui est exclu puisque $WX \neq XY$.
- **d)** Parallélogramme quelconque : on s'est arrêté aux milieux sans comparer les diagonales, qui sont égales.

</details>

Avis : 

---

### 14. `cqc-parallelogramme-faible-0`

**A regarder :** Le parallelogramme est maintenant donne dans l'enonce ; la question porte sur le centre (1 ; -1).

**Enonce :**

Dans un repère orthonormé $(O;I,J)$, le quadrilatère $IJKL$ de sommets $I(-4;1)$, $J(2;5)$, $K(6;-3)$ et $L(0;-7)$ est un parallélogramme. Quelles sont les coordonnées du point d'intersection de ses diagonales ?

- a) $(2;-2)$
- b) $(-1;3)$
- c) $(1;-1)$
- d) $(5;-2)$

**Cle :** c

<details><summary>Corrige</summary>

### Rappel de méthode

Le milieu d'un segment d'extrémités $(x_1;y_1)$ et $(x_2;y_2)$ a pour coordonnées $\left(\dfrac{x_1+x_2}{2};\dfrac{y_1+y_2}{2}\right)$. Dans un parallélogramme, les diagonales se coupent en leur milieu commun : c'est le centre du parallélogramme.

### Corrigé

Les diagonales du quadrilatère $IJKL$ sont $[IK]$ et $[JL]$.

Milieu de $[IK]$ : $\left(\dfrac{-4+6}{2};\dfrac{1+(-3)}{2}\right)=(1;-1)$.

Milieu de $[JL]$ : $\left(\dfrac{2+0}{2};\dfrac{5+(-7)}{2}\right)=(1;-1)$.

Les deux diagonales $[IK]$ et $[JL]$ ont le même milieu $(1;-1)$ : elles se coupent en ce point, ce qui confirme que $IJKL$ est un parallélogramme.

### Pourquoi les autres réponses sont fausses

- **a)** $(2;-2)$ : on a additionné les coordonnées sans diviser par $2$.
- **b)** $(-1;3)$ : c'est le milieu de $[IJ]$, un côté et non une diagonale.
- **d)** $(5;-2)$ : on a fait la demi-différence des coordonnées au lieu de la demi-somme.

</details>

Avis : 

---



# Vague 3 (150 QCM en ligne)

Date : 2026-10-27. Questions de la vague 3 (150 en ligne) ou une methode a ete remplacee, une donnee ajoutee ou une formulation est discutable. Les 150 ont ete resolues a l'aveugle par un relecteur independant (150 accords sur 150) ; ce document sert a juger ce qu'un relecteur modele ne juge pas : le niveau 3e / BEPC, le realisme des distracteurs et les conventions d'enseignement.

Pour chaque question : **OK**, **a corriger** (dire quoi), ou **a retirer**.

### 1. `cqc-rectangle-moyenne-0`

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

### 2. `cqc-quadrilatere-moyenne-2`

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

### 3. `cqc-quadrilatere-elevee-1`

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

### 4. `cqc-quadrilatere-faible-1`

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

### 5. `cqc-quadrilatere-moyenne-3`

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

### 6. `cqc-symetrie-axiale-elevee-0`

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

### 7. `cqc-symetrie-axiale-faible-1`

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

### 8. `cqc-symetrie-axiale-moyenne-0`

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

### 9. `cqc-symetrie-axiale-moyenne-2`

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

### 10. `cqc-triangle-rectangle-isocele-moyenne-1`

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

### 11. `cqc-reciproque-du-theoreme-de-pythagore-faible-2`

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

### 12. `cqc-reciproque-du-theoreme-de-pythagore-moyenne-3`

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

### 13. `cqc-rotation-faible-0`

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

### 14. `cqc-equation-cartesienne-elevee-0`

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

### 15. `cqc-simplification-moyenne-2`

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

### 16. `cqc-simplification-elevee-0`

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

### 17. `cqc-simplification-de-racines-faible-1`

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

### 18. `cqc-volume-elevee-0`

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

### 19. `cqc-volume-d-un-cone-elevee-0`

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

### 20. `cqc-probleme-concret-faible-0`

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

