# Echantillon pour relecture par un enseignant de maths (B1, vague 2)

Date : 2026-10-27. Questions de la vague 2 ou une methode a ete remplacee, une formulation est discutable ou une precision a ete ajoutee. Les 106 questions ont ete resolues a l'aveugle par un relecteur independant (106 accords sur 106) ; ce document sert a juger ce qu'un relecteur modele ne juge pas : le niveau 3e / BEPC, le realisme des distracteurs et les conventions d'enseignement.

Pour chaque question : **OK**, **a corriger** (dire quoi), ou **a retirer**.

## 1. `cqc-mesure-d-angle-moyenne-0`

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

## 2. `cqc-geometrie-analytique-moyenne-2`

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

## 3. `cqc-forme-reduite-moyenne-3`

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

## 4. `cqc-droite-moyenne-4`

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

## 5. `cqc-diagonales-moyenne-0`

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

## 6. `cqc-diagonales-moyenne-1`

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

## 7. `cqc-droite-faible-0`

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

## 8. `cqc-droites-perpendiculaires-elevee-5`

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

## 9. `cqc-droites-perpendiculaires-moyenne-3`

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

## 10. `cqc-parallelisme-moyenne-2`

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

## 11. `cqc-geometrie-analytique-moyenne-1`

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

## 12. `cqc-geometrie-analytique-moyenne-3`

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

## 13. `cqc-parallelogramme-moyenne-2`

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

## 14. `cqc-parallelogramme-faible-0`

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

