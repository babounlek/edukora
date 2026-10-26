# Echantillon pour relecture par un enseignant de maths (B1, vague 1)

Date : 2026-10-26. 14 questions sur 112 : celles ou un sous-agent a change le fond (cle, methode, enonce) ou signale un doute de programme. Les 112 ont deja ete resolues a l'aveugle par un relecteur independant, avec accord total ; ce document sert a juger ce qu'un relecteur modele ne juge pas : le niveau 3e / BEPC, le realisme des distracteurs et les conventions d'enseignement.

Pour chaque question : **OK**, **a corriger** (dire quoi), ou **a retirer**.

## 1. `cqc-pgcd-moyenne-0`

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

## 2. `cqc-aire-d-un-triangle-moyenne-1`

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

## 3. `cqc-aire-d-un-triangle-moyenne-2`

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

## 4. `cqc-amplitude-elevee-0`

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

## 5. `cqc-amplitude-moyenne-2`

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

## 6. `cqc-appartenance-a-une-droite-faible-2`

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

## 7. `cqc-calcul-numerique-faible-1`

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

## 8. `cqc-carre-elevee-0`

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

## 9. `cqc-carre-faible-1`

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

## 10. `cqc-classes-moyenne-2`

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

## 11. `cqc-comparaison-faible-1`

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

## 12. `cqc-conversion-faible-0`

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

## 13. `cqc-coordonnees-d-un-vecteur-elevee-0`

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

## 14. `cqc-coordonnees-d-un-vecteur-moyenne-2`

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

