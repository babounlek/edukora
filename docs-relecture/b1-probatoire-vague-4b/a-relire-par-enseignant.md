# Vague 4b Maths Probatoire (questions incluant la série A) : 79 QCM à faire relire par l'enseignant (campagne B1)

Date : 2026-10-31. Sur 128 QCM convertis (142 questions étudiées, 14 écartées), **79** vous sont soumis : ceux que le relecteur aveugle a assortis d'une remarque, ceux dont la question ou la méthode a été modifiée, et un tirage de 10 autres. Le lot est prêt mais n'est pas en ligne tant que vous n'avez pas répondu. Les 128 résolutions à l'aveugle ont toutes donné la clé.

Chaque question a été adaptée au niveau de la série A, la plus légère des séries concernées (programme : fonctions, dénombrement, statistiques). Quand la question est aussi posée en C, D ou E, elle est la même pour toutes les séries.

## Points à trancher (nouveaux)

1. **Dérivation en série A :** dérivée d'un polynôme, équation de tangente, étude de variations par la dérivée, dérivée de $\frac1x$ et de $\sqrt x$. Sont-elles au programme de la Première A ? Sinon, indiquez les questions pour lesquelles il faut **retirer la série A**.
2. **Limites hautes en A :** factorisation d'un polynôme de degré 3 avec tableau de signes à trois facteurs ; système avec paramètre et déterminant ; relations somme-produit des racines ; fonction homographique avec limites à gauche et à droite.
3. **Géométrie analytique en A :** équation cartésienne d'une droite, coefficient directeur, droites parallèles : au programme de la série A ? (questions réduites au coefficient directeur et à l'équation réduite)
4. **Vecteurs et translations :** pour la série A, « translation de vecteur $(a\,;b)$ » est devenue « déplacement de $a$ unités vers la droite et $b$ vers le haut » dans les questions sur les fonctions associées. Confirmer ce choix de vocabulaire.
5. **Contextes :** des scores sur 40 (notes) au lieu de 20 : le mot « scores » remplace « notes » dans une question, à uniformiser ?
6. **Questions réduites :** de nombreuses questions à plusieurs sous-questions ont été réduites à une seule (signalées ci-dessous comme « modification de fond »).

Pour chaque question : **OK**, **à corriger** (dire quoi), **à retirer**, ou **retirer la série A**.

## 1. `cqc-resolution-par-substitution-prob-a-faible-0` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

On résout par substitution un système de deux équations à deux inconnues $x$ et $y$. Après avoir exprimé $y$ en fonction de $x$ à l'aide de la première équation, quelle est l'étape suivante ?

- a) On additionne membre à membre les deux équations.
- b) On remplace $y$ par cette expression dans la seconde équation.
- c) On remplace $y$ par cette expression dans la première équation.
- d) On choisit une valeur de $x$, par exemple $x=0$, et on en déduit $y$.

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On exprime une inconnue en fonction de l'autre dans une équation et on la remplace dans l'autre.

### Corrigé

1) Isoler une inconnue dans l'une des équations (ex. $y=\dots x\dots$) ; 2) la **substituer** dans l'autre équation, ce qui donne une équation à une seule inconnue ; 3) résoudre ; 4) reporter la valeur trouvée pour obtenir l'autre inconnue ; 5) vérifier. L'étape suivante est donc de remplacer $y$ par son expression dans la seconde équation.

### Pourquoi les autres réponses sont fausses

- **a)** C'est la méthode par combinaison (addition), pas la substitution.
- **c)** Remplacer $y$ dans l'équation d'où vient son expression donne une égalité toujours vraie (du type $0=0$), qui n'apprend rien.
- **d)** Le couple obtenu vérifie la première équation mais en général pas la seconde.

</details>

Avis : 

---

## 2. `cqc-resolution-par-substitution-prob-a-moyenne-2` (séries A)

**Énoncé :**

Quelle est la solution du système $\begin{cases}x+y=5\\2x-y=1\end{cases}$ ?

- a) $(3\,;2)$
- b) $(6\,;-1)$
- c) $(2\,;3)$
- d) $\left(-\dfrac43\,;\dfrac{19}3\right)$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

$y=5-x$ puis on remplace dans la seconde équation.

### Corrigé

$y=5-x$ ; $2x-(5-x)=1\Rightarrow3x-5=1\Rightarrow x=2$ ; $y=3$. Vérification : $2+3=5$ et $4-3=1$. Solution : $(2\,;3)$.

### Pourquoi les autres réponses sont fausses

- **a)** Inversion de $x$ et $y$ : $2\times3-2=4\ne1$.
- **b)** Parenthèses oubliées : $2x-5-x=1$ donne $x=6$.
- **d)** Erreur de signe : $3x-5=1$ transformé en $3x=1-5$.

</details>

Avis : 

---

## 3. `cqc-centre-de-classe-prob-a-moyenne-2` (séries A)

**Remarque du relecteur :** VOCABULAIRE : des « notes » sur [0;40[ surprennent (notes usuelles sur 20) ; préférer « scores » ou des notes sur 40 explicitement.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Les scores de $40$ élèves sont réparties ainsi : $[0\,;10[$ : $4$ élèves ; $[10\,;20[$ : $10$ ; $[20\,;30[$ : $16$ ; $[30\,;40[$ : $10$. Quelle est le score moyen, calculée à l'aide des centres de classe ?

- a) $20$
- b) $18$
- c) $23$
- d) $28$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Moyenne $=\dfrac{\sum n_ic_i}{N}$, où $c_i$ est le centre de la classe $i$.

### Corrigé

Centres : $5\,;15\,;25\,;35$. $\bar x=\dfrac{4\times5+10\times15+16\times25+10\times35}{40}=\dfrac{20+150+400+350}{40}=\dfrac{920}{40}=23$.

### Pourquoi les autres réponses sont fausses

- **a)** Moyenne des centres sans tenir compte des effectifs : $\dfrac{5+15+25+35}4=20$.
- **b)** Bornes inférieures prises à la place des centres : $\dfrac{720}{40}=18$.
- **d)** Bornes supérieures prises à la place des centres : $\dfrac{1120}{40}=28$.

</details>

Avis : 

---

## 4. `cqc-centre-de-classe-prob-a-moyenne-3` (séries A)

**Énoncé :**

Une classe d'une série statistique a pour centre $12{,}5$ et pour amplitude $5$. Quelle est cette classe ?

- a) $[12{,}5\,;17{,}5[$
- b) $[7{,}5\,;17{,}5[$
- c) $[7{,}5\,;12{,}5[$
- d) $[10\,;15[$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Les bornes sont à une demi-amplitude de part et d'autre du centre.

### Corrigé

$\dfrac52=2{,}5$ : bornes $12{,}5-2{,}5=10$ et $12{,}5+2{,}5=15$ : la classe est $[10\,;15[$.

### Pourquoi les autres réponses sont fausses

- **a)** Le centre a été pris comme borne inférieure.
- **b)** L'amplitude entière a été retirée et ajoutée au centre au lieu de la demi-amplitude (cette classe a pour amplitude $10$).
- **c)** Le centre a été pris comme borne supérieure.

</details>

Avis : 

---

## 5. `cqc-centre-de-classe-prob-a-moyenne-4` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

On considère les classes $[0\,;5[$, $[5\,;15[$ et $[15\,;30[$. Quelle affirmation est exacte ?

- a) Les centres sont $2{,}5$ ; $5$ ; $7{,}5$ et les amplitudes sont différentes.
- b) Les centres sont $2{,}5$ ; $10$ ; $22{,}5$ et les amplitudes sont différentes.
- c) Les centres sont $2{,}5$ ; $10$ ; $22{,}5$ et les classes ont toutes la même amplitude.
- d) Les centres sont $2{,}5$ ; $7{,}5$ ; $12{,}5$ et les classes ont toutes la même amplitude $5$.

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Centre $=\dfrac{a+b}2$ et amplitude $=b-a$.

### Corrigé

Centres : $2{,}5\,;10\,;22{,}5$. Amplitudes : $5$, $10$ et $15$ : elles sont différentes (classes d'amplitudes inégales).

### Pourquoi les autres réponses sont fausses

- **a)** La demi-amplitude $\dfrac{b-a}2$ a été prise pour le centre.
- **c)** Les centres sont justes mais les amplitudes valent $5$, $10$ et $15$.
- **d)** On a supposé toutes les classes d'amplitude $5$, comme la première.

</details>

Avis : 

---

## 6. `cqc-centre-de-classe-prob-a-moyenne-5` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Tailles (en cm) de $25$ élèves : $[150\,;160[$ : $5$ ; $[160\,;170[$ : $12$ ; $[170\,;180[$ : $8$. Quelle est la taille moyenne, calculée à l'aide des centres de classe ?

- a) $166{,}2$ cm
- b) $165$ cm
- c) $161{,}2$ cm
- d) $171{,}2$ cm

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Centres : $155$, $165$, $175$. Moyenne $=\dfrac{\sum n_ic_i}N$.

### Corrigé

$\bar x=\dfrac{5\times155+12\times165+8\times175}{25}=\dfrac{775+1980+1400}{25}=\dfrac{4155}{25}=166{,}2$ cm.

### Pourquoi les autres réponses sont fausses

- **b)** Moyenne des centres sans tenir compte des effectifs : $\dfrac{155+165+175}3=165$.
- **c)** Bornes inférieures prises à la place des centres : $\dfrac{4030}{25}=161{,}2$.
- **d)** Bornes supérieures prises à la place des centres : $\dfrac{4280}{25}=171{,}2$.

</details>

Avis : 

---

## 7. `cqc-courbe-representative-prob-a-moyenne-3` (séries A)

**Énoncé :**

Quels sont les points d'intersection de la courbe de $f(x)=x^2-4$ avec les axes du repère ?

- a) $(0\,;-4)$, $(-2\,;0)$ et $(2\,;0)$
- b) $(0\,;-4)$ et $(2\,;0)$
- c) $(-4\,;0)$, $(0\,;-2)$ et $(0\,;2)$
- d) $(0\,;4)$, $(-2\,;0)$ et $(2\,;0)$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Axe des ordonnées : $x=0$ ; axe des abscisses : $f(x)=0$.

### Corrigé

Avec l'axe des ordonnées : $f(0)=-4$, point $(0\,;-4)$. Avec l'axe des abscisses : $x^2=4\Rightarrow x=\pm2$, points $(-2\,;0)$ et $(2\,;0)$.

### Pourquoi les autres réponses sont fausses

- **b)** Oubli de la solution négative de $x^2=4$.
- **c)** Abscisses et ordonnées inversées dans l'écriture des points.
- **d)** Erreur de signe : $f(0)=-4$, pas $4$.

</details>

Avis : 

---

## 8. `cqc-derivee-d-une-fonction-polynome-prob-a-faible-0` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Quelle est la dérivée de la fonction $f$ définie sur $\mathbb R$ par $f(x)=3x^2-5x+1$ ?

- a) $6x-4$
- b) $3x-5$
- c) $6x-5$
- d) $6x^2-5$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On dérive terme à terme : $(k)'=0$ ; $(x)'=1$ ; $(x^n)'=nx^{n-1}$ ; $(ku)'=ku'$ ; $(u+v)'=u'+v'$.

### Corrigé

$(3x^2)'=6x$, $(-5x)'=-5$ et $(1)'=0$, donc $f'(x)=6x-5$.

### Pourquoi les autres réponses sont fausses

- **a)** La constante a été conservée : la dérivée de $1$ est $0$.
- **b)** Oubli du facteur $2$ : $(x^2)'=2x$, donc $(3x^2)'=6x$.
- **d)** L'exposant n'a pas été diminué : $(x^2)'=2x$, pas $2x^2$.

</details>

Avis : 

---

## 9. `cqc-derivee-d-une-fonction-polynome-prob-a-moyenne-2` (séries A)

**Remarque du relecteur :** LIMITE : dérivation pour la série A seule, à confirmer au programme de Première A.

**Énoncé :**

Quelle est la dérivée de $f(x)=3x^4-2x^3+5x-7$ ?

- a) $12x^3-6x^2-2$
- b) $12x^3-6x^2+5x$
- c) $12x^3+6x^2+5$
- d) $12x^3-6x^2+5$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On dérive chaque terme : $(3x^4)'=12x^3$, etc.

### Corrigé

$(3x^4)'=12x^3$, $(-2x^3)'=-6x^2$, $(5x)'=5$ et $(-7)'=0$, donc $f'(x)=12x^3-6x^2+5$.

### Pourquoi les autres réponses sont fausses

- **a)** La constante $-7$ a été conservée : sa dérivée est $0$.
- **b)** $5x$ n'a pas été dérivé : $(5x)'=5$.
- **c)** Erreur de signe : $(-2x^3)'=-6x^2$.

</details>

Avis : 

---

## 10. `cqc-derivee-d-une-fonction-polynome-prob-a-moyenne-3` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $f(x)=(x^2+1)(x-2)$. Quelle est l'expression de $f'(x)$ ?

- a) $3x^2-4x+1$
- b) $2x$
- c) $3x^2-4x$
- d) $3x^2-2x+1$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On développe d'abord : $(x^2+1)(x-2)=x^3-2x^2+x-2$.

### Corrigé

$f(x)=x^3-2x^2+x-2$ donc $f'(x)=3x^2-4x+1$.

### Pourquoi les autres réponses sont fausses

- **b)** La dérivée d'un produit n'est pas le produit des dérivées : $(x^2+1)'\times(x-2)'=2x\times1$.
- **c)** Développement incomplet : le terme $1\times x$ a été oublié.
- **d)** Erreur de dérivation : $(-2x^2)'=-4x$, pas $-2x$.

</details>

Avis : 

---

## 11. `cqc-derivee-d-une-fonction-polynome-prob-a-moyenne-4` (séries A)

**Remarque du relecteur :** LIMITE : dérivée et tangente pour la série A seule, à confirmer au programme de Première A.

**Énoncé :**

Soit $f(x)=x^3-3x$. En quels points de la courbe de $f$ la tangente est-elle horizontale ?

- a) Au point $(1\,;-2)$ seulement
- b) Aux points $(1\,;-2)$ et $(-1\,;2)$
- c) Aux points $(1\,;2)$ et $(-1\,;-2)$
- d) Aux points $(0\,;0)$, $(-\sqrt3\,;0)$ et $(\sqrt3\,;0)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La tangente est horizontale là où $f'(x)=0$ ; ici $f'(x)=3x^2-3$.

### Corrigé

$3x^2-3=0\iff x^2=1\iff x=\pm1$. $f(1)=-2$ et $f(-1)=2$. Tangentes horizontales aux points $(1\,;-2)$ et $(-1\,;2)$.

### Pourquoi les autres réponses sont fausses

- **a)** Oubli de la solution $x=-1$ de $x^2=1$.
- **c)** Erreur de signe dans le calcul des images : $f(1)=1-3=-2$.
- **d)** Confusion : on a résolu $f(x)=0$ au lieu de $f'(x)=0$.

</details>

Avis : 

---

## 12. `cqc-determination-de-coefficients-prob-a-faible-0` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $a$, $b$, $c$, $a'$, $b'$, $c'$ des réels. L'égalité $ax^2+bx+c=a'x^2+b'x+c'$ est vraie pour tout réel $x$ si et seulement si :

- a) $a+b+c=a'+b'+c'$
- b) $c=c'$
- c) $a=a'$
- d) $a=a'$, $b=b'$ et $c=c'$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Deux polynômes sont égaux pour tout $x$ si et seulement si leurs coefficients de même degré sont égaux.

### Corrigé

Si deux expressions polynomiales sont égales pour toutes les valeurs de $x$, alors les coefficients des termes de même degré sont égaux : $ax^2+bx+c=a'x^2+b'x+c'$ pour tout $x$ $\iff a=a',\ b=b',\ c=c'$. On obtient ainsi un système d'équations : c'est la méthode d'identification.

### Pourquoi les autres réponses sont fausses

- **a)** C'est seulement l'égalité pour $x=1$.
- **b)** C'est seulement l'égalité pour $x=0$.
- **c)** L'égalité des seuls coefficients de plus haut degré ne suffit pas.

</details>

Avis : 

---

## 13. `cqc-determination-de-coefficients-prob-a-moyenne-4` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Quel est le minimum de $x^2-4x+7$ sur $\mathbb R$, et pour quelle valeur de $x$ est-il atteint ?

- a) $3$, atteint en $x=-2$
- b) $11$, atteint en $x=2$
- c) $3$, atteint en $x=2$
- d) $7$, atteint en $x=0$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On écrit l'expression sous la forme $(x-2)^2+q$ en utilisant $(x-2)^2=x^2-4x+4$.

### Corrigé

$x^2-4x+7=(x^2-4x+4)+3=(x-2)^2+3$ : $q=3$. Comme $(x-2)^2\ge0$, le minimum vaut $3$, atteint en $x=2$.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe : $(x-2)^2$ s'annule pour $x=2$.
- **b)** Identité remarquable mal développée : $(x-2)^2=x^2-4x+4$, pas $x^2-4x-4$.
- **d)** $7$ est la valeur en $x=0$, pas le minimum ($2^2-4\times2+7=3<7$).

</details>

Avis : 

---

## 14. `cqc-determination-de-coefficients-prob-a-moyenne-5` (séries A)

**Énoncé :**

On cherche les réels $a$ et $b$ tels que $\dfrac{2x+3}{x+1}=a+\dfrac b{x+1}$ pour tout $x\ne-1$. Quelles sont leurs valeurs ?

- a) $a=2$ et $b=3$
- b) $a=2$ et $b=1$
- c) $a=2$ et $b=-1$
- d) $a=2$ et $b=5$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On réduit au même dénominateur : $a+\dfrac b{x+1}=\dfrac{a(x+1)+b}{x+1}$, puis on identifie les numérateurs.

### Corrigé

$a(x+1)+b=ax+(a+b)$ ; identification avec $2x+3$ : $a=2$ et $a+b=3$, donc $b=1$. Ainsi $\dfrac{2x+3}{x+1}=2+\dfrac1{x+1}$.

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié que le terme constant de $a(x+1)+b$ est $a+b$ et non $b$.
- **c)** Erreur de signe : on a écrit $b=a-3$ au lieu de $b=3-a$.
- **d)** On a écrit $b-a=3$ au lieu de $a+b=3$.

</details>

Avis : 

---

## 15. `cqc-effectif-total-prob-a-moyenne-4` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Dans une série statistique, une valeur a pour fréquence $0{,}15$ et pour effectif $6$. Quel est l'effectif d'une valeur de fréquence $0{,}35$ dans cette série ? (Résultat arrondi au dixième si nécessaire.)

- a) $14$
- b) $2{,}1$
- c) $40$
- d) $114{,}3$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule d'abord l'effectif total $N=\dfrac nf$, puis l'effectif cherché $n=f\times N$.

### Corrigé

$N=\dfrac{6}{0{,}15}=40$ ; $n=0{,}35\times40=14$ (valeur exacte, aucun arrondi nécessaire).

### Pourquoi les autres réponses sont fausses

- **b)** On a multiplié $0{,}35$ par l'effectif $6$ au lieu de l'effectif total $40$.
- **c)** C'est l'effectif total $N$, pas l'effectif de la valeur de fréquence $0{,}35$.
- **d)** On a divisé $40$ par $0{,}35$ au lieu de multiplier (arrondi au dixième).

</details>

Avis : 

---

## 16. `cqc-effectif-total-prob-a-moyenne-5` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Un tableau donne les fréquences $0{,}10\,;0{,}25\,;0{,}40\,;x$ des quatre valeurs d'une série d'effectif total $80$. Quel est l'effectif de la valeur de fréquence $x$ ?

- a) $25$
- b) $20$
- c) $60$
- d) $320$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La somme des fréquences vaut $1$ ; l'effectif d'une valeur est $n=f\times N$.

### Corrigé

$x=1-(0{,}10+0{,}25+0{,}40)=0{,}25$. Effectif : $0{,}25\times80=20$. (Effectifs des quatre valeurs : $8\,;20\,;32\,;20$, de somme $80$.)

### Pourquoi les autres réponses sont fausses

- **a)** On a confondu la fréquence $25\ \%$ avec l'effectif.
- **c)** On a pris $x=0{,}75$ (la somme des trois fréquences) au lieu de $1-0{,}75$.
- **d)** On a divisé $80$ par $0{,}25$ au lieu de multiplier.

</details>

Avis : 

---

## 17. `cqc-effectifs-cumules-prob-a-moyenne-2` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Les notes de $25$ élèves sont réparties ainsi : note $8$ : $4$ élèves ; note $10$ : $6$ élèves ; note $12$ : $10$ élèves ; note $15$ : $5$ élèves. Combien d'élèves ont une note inférieure ou égale à $10$ ?

- a) $10$
- b) $6$
- c) $4$
- d) $21$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On cumule les effectifs dans l'ordre croissant des notes ; l'effectif cumulé croissant en $10$ répond à la question.

### Corrigé

Effectifs cumulés croissants : $4\,;10\,;20\,;25$. Nombre d'élèves ayant une note $\le10$ : $10$.

### Pourquoi les autres réponses sont fausses

- **b)** C'est l'effectif de la seule note $10$ : on a oublié d'ajouter les $4$ élèves ayant $8$.
- **c)** C'est le nombre d'élèves ayant une note strictement inférieure à $10$.
- **d)** C'est le nombre d'élèves ayant au moins $10$ ($6+10+5$) : sens du cumul inversé.

</details>

Avis : 

---

## 18. `cqc-effectifs-cumules-prob-a-moyenne-3` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Les notes de $25$ élèves sont réparties ainsi : note $8$ : $4$ élèves ; note $10$ : $6$ élèves ; note $12$ : $10$ élèves ; note $15$ : $5$ élèves. Quelle est la médiane de cette série ?

- a) $10$
- b) $11{,}48$
- c) $12$
- d) $12{,}5$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

$N=25$ est impair : la médiane est la $13$e valeur de la série rangée dans l'ordre croissant. On la repère avec les effectifs cumulés croissants.

### Corrigé

Effectifs cumulés croissants : $4\,;10\,;20\,;25$. La $13$e valeur vérifie $10<13\le20$ : elle vaut $12$. La médiane est $12$.

### Pourquoi les autres réponses sont fausses

- **a)** On s'est arrêté au cumul $10$, qui ne contient que les $10$ premières valeurs : la $13$e n'y est pas.
- **b)** C'est la moyenne de la série ($\dfrac{287}{25}$), pas sa médiane.
- **d)** On a pris $\dfrac N2=12{,}5$, qui est un rang et non une valeur de la série.

</details>

Avis : 

---

## 19. `cqc-effectifs-cumules-prob-a-moyenne-4` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Les effectifs cumulés croissants d'une série à quatre valeurs sont $3\,;8\,;15\,;20$. Quels sont les effectifs de ces quatre valeurs ?

- a) $3\,;8\,;15\,;20$
- b) $3\,;11\,;26\,;46$
- c) $3\,;5\,;7\,;20$
- d) $3\,;5\,;7\,;5$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Chaque effectif est la différence de deux effectifs cumulés consécutifs : $n_i=N_i-N_{i-1}$, et $n_1=N_1$.

### Corrigé

$n_1=3$ ; $n_2=8-3=5$ ; $n_3=15-8=7$ ; $n_4=20-15=5$. Effectif total : $20$.

### Pourquoi les autres réponses sont fausses

- **a)** On a recopié les effectifs cumulés sans faire les différences.
- **b)** On a cumulé une seconde fois au lieu de soustraire.
- **c)** On a oublié de soustraire pour la dernière valeur : $20-15=5$.

</details>

Avis : 

---

## 20. `cqc-effectifs-cumules-croissants-prob-d-moyenne-2` (séries A/D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Les notes de $30$ élèves sont regroupées en classes : $[0\,;5[$ (effectif $4$), $[5\,;10[$ ($9$), $[10\,;15[$ ($12$), $[15\,;20]$ ($5$). Combien d'élèves ont une note strictement inférieure à $10$ ?

- a) $9$
- b) $25$
- c) $13$
- d) $17$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Les effectifs cumulés croissants se lisent aux bornes supérieures des classes : l'effectif cumulé en $b$ est le nombre d'observations strictement inférieures à $b$ (pour des classes $[a\,;b[$).

### Corrigé

Effectifs cumulés croissants : en $5$ : $4$ ; en $10$ : $4+9=13$ ; en $15$ : $13+12=25$ ; en $20$ : $25+5=30$. Moins de $10$ : $13$ élèves.

### Pourquoi les autres réponses sont fausses

- **a)** C'est l'effectif de la seule classe $[5\,;10[$ : on a oublié la classe $[0\,;5[$.
- **b)** C'est l'effectif cumulé en $15$ : on a lu la borne supérieure de la classe $[10\,;15[$.
- **d)** C'est le nombre d'élèves ayant au moins $10$ ($30-13$).

</details>

Avis : 

---

## 21. `cqc-effectifs-cumules-croissants-prob-d-moyenne-3` (séries A/D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Les notes de $30$ élèves sont regroupées en classes $[0\,;5[$, $[5\,;10[$, $[10\,;15[$, $[15\,;20]$ ; les effectifs cumulés croissants aux bornes $5$, $10$, $15$, $20$ sont $4$, $13$, $25$, $30$. Quelle est la fréquence cumulée croissante en $10$, en pourcentage arrondi au dixième ?

- a) $13\ \%$
- b) $43{,}3\ \%$
- c) $30\ \%$
- d) $56{,}7\ \%$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La fréquence cumulée croissante est l'effectif cumulé croissant divisé par l'effectif total, exprimée en pourcentage.

### Corrigé

$\dfrac{13}{30}\approx43{,}3\ \%$ (arrondi au dixième). Environ $43\ \%$ des élèves ont une note inférieure à $10$. (Les autres fréquences cumulées : $13{,}3\ \%$ ; $83{,}3\ \%$ ; $100\ \%$.)

### Pourquoi les autres réponses sont fausses

- **a)** On a confondu l'effectif cumulé $13$ avec un pourcentage.
- **c)** C'est la fréquence de la seule classe $[5\,;10[$ ($\dfrac9{30}$), sans cumul.
- **d)** C'est la proportion d'élèves ayant au moins $10$ ($\dfrac{17}{30}$).

</details>

Avis : 

---

## 22. `cqc-effectifs-cumules-croissants-prob-d-moyenne-4` (séries A/D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Les notes de $30$ élèves sont regroupées en classes $[0\,;5[$, $[5\,;10[$, $[10\,;15[$, $[15\,;20]$ d'effectifs $4$, $9$, $12$, $5$. Combien d'élèves ont une note comprise entre $5$ (inclus) et $15$ (exclu) ?

- a) $25$
- b) $12$
- c) $26$
- d) $21$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour compter les observations d'un intervalle $[a\,;b[$, on soustrait les effectifs cumulés croissants : $ECC(b)-ECC(a)$.

### Corrigé

$ECC(15)=25$ et $ECC(5)=4$. Nombre d'élèves dans $[5\,;15[$ : $25-4=21$ (c'est bien $9+12$).

### Pourquoi les autres réponses sont fausses

- **a)** C'est $ECC(15)$ : on a oublié de retirer les $4$ élèves de la classe $[0\,;5[$.
- **b)** On a calculé $ECC(15)-ECC(10)$ : seule la classe $[10\,;15[$ est comptée.
- **c)** On a calculé $ECC(20)-ECC(5)$ : la classe $[15\,;20]$ a été ajoutée à tort.

</details>

Avis : 

---

## 23. `cqc-effectifs-cumules-decroissants-prob-a-moyenne-3` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Une série de $50$ valeurs entières a pour effectif cumulé croissant $32$ en $10$, et la valeur qui suit $10$ dans la série est $11$. Quel est l'effectif cumulé décroissant en $11$ ?

- a) $18$
- b) $32$
- c) $19$
- d) $50$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Les valeurs inférieures ou égales à $10$ et les valeurs supérieures ou égales à $11$ se partagent toute la série.

### Corrigé

Les valeurs $\le10$ sont au nombre de $32$ ; les valeurs $\ge11$ sont donc $50-32=18$ : l'effectif cumulé décroissant en $11$ est $18$.

### Pourquoi les autres réponses sont fausses

- **b)** C'est l'effectif cumulé croissant en $10$, donné par l'énoncé.
- **c)** On a ajouté $1$ en pensant devoir compter la valeur $11$ en plus : elle est déjà dans les $18$.
- **d)** C'est l'effectif total, égal à l'effectif cumulé décroissant de la plus petite valeur seulement.

</details>

Avis : 

---

## 24. `cqc-effectifs-cumules-decroissants-prob-a-moyenne-4` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Dans une classe de $30$ élèves, $12$ ont obtenu au moins $14$ sur $20$. Combien d'élèves ont une note strictement inférieure à $14$, et quel pourcentage de la classe a obtenu au moins $14$ ?

- a) $12$ élèves ; $40\ \%$
- b) $18$ élèves ; $60\ \%$
- c) $18$ élèves ; $12\ \%$
- d) $18$ élèves ; $40\ \%$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pourcentage $=\dfrac{12}{30}\times100$ ; les autres élèves ont moins de $14$.

### Corrigé

$\dfrac{12}{30}=0{,}4$, soit $40\ \%$ des élèves ont au moins $14$. Les élèves ayant une note strictement inférieure à $14$ sont $30-12=18$ : c'est l'effectif cumulé croissant de la dernière valeur inférieure à $14$.

### Pourquoi les autres réponses sont fausses

- **a)** $12$ est le nombre d'élèves ayant **au moins** $14$, pas moins de $14$.
- **b)** $60\ \%$ est la part des élèves ayant moins de $14$ ($\dfrac{18}{30}$).
- **c)** On a confondu l'effectif $12$ avec un pourcentage.

</details>

Avis : 

---

## 25. `cqc-factorielle-prob-a-faible-0` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Quelles sont, dans l'ordre, les valeurs de $0!$, $3!$ et $5!$ ?

- a) $0\,;6\,;120$
- b) $1\,;6\,;120$
- c) $1\,;6\,;15$
- d) $0\,;6\,;15$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

$n!$ est le produit des $n$ premiers entiers strictement positifs, et par convention $0!=1$.

### Corrigé

$n!=n\times(n-1)\times\dots\times2\times1$ pour $n\ge1$ et $0!=1$. Donc $0!=1$, $3!=6$ et $5!=120$. (Autres valeurs : $1!=1$, $2!=2$, $4!=24$, $6!=720$.)

### Pourquoi les autres réponses sont fausses

- **a)** Par convention $0!=1$ et non $0$.
- **c)** On a additionné $1+2+3+4+5$ au lieu de multiplier pour $5!$.
- **d)** Deux erreurs : $0!=1$, et $5!$ est un produit, pas une somme.

</details>

Avis : 

---

## 26. `cqc-factorielle-prob-a-moyenne-2` (séries A)

**Énoncé :**

Quelle est la valeur de $\dfrac{6!}{4!}$ ?

- a) $30$
- b) $2$
- c) $1{,}5$
- d) $120$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

$6!=6\times5\times4!$, ce qui permet de simplifier sans calculer chaque factorielle.

### Corrigé

$\dfrac{6!}{4!}=\dfrac{6\times5\times4!}{4!}=6\times5=30$.

### Pourquoi les autres réponses sont fausses

- **b)** On a « simplifié » en $(6-4)!=2!$ : on ne soustrait pas sous la factorielle.
- **c)** On a simplifié les points d'exclamation et calculé $\dfrac64$.
- **d)** On a écrit $6\times5\times4$ : le facteur $4$ est déjà dans $4!$.

</details>

Avis : 

---

## 27. `cqc-fonction-polynome-elevee-0` (séries A/C/E)

**Remarque du relecteur :** LIMITE : pour la série A, l'étude de variations d'un polynôme de degré 3 par la dérivée et la résolution d'une équation du second degré à racine irrationnelle sont à la limite haute du programme léger.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

On veut fabriquer une boîte sans couvercle à partir d'une plaque rectangulaire de carton de $30$ cm sur $20$ cm. On découpe un carré de côté $x$ cm dans chacun des quatre coins ($0 < x < 10$), puis on relève les bords. Le volume de la boîte, en cm³, est alors $V(x) = 4x^3 - 100x^2 + 600x$.

Quelle est la valeur **exacte** de $x$ qui rend le volume maximal ?

- a) $\dfrac{25 + 5\sqrt{7}}{3}$
- b) $\dfrac{50 - 10\sqrt{7}}{3}$
- c) $\dfrac{25 - 5\sqrt{7}}{3}$
- d) $\dfrac{25 - 5\sqrt{7}}{6}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour optimiser une grandeur modélisée par une fonction polynôme sur un intervalle, on traduit la situation par une fonction d'une seule variable (en précisant son domaine), on étudie le signe de sa dérivée, puis on retient la valeur du domaine où les variations passent de croissante à décroissante.

### Corrigé

Les coupes de côté $x$ doivent laisser des longueurs positives : $30 - 2x > 0$ et $20 - 2x > 0$, donc $x < 10$ ; et $x > 0$. La boîte a pour base un rectangle de dimensions $(30 - 2x)$ et $(20 - 2x)$, et pour hauteur $x$ : $V(x) = x(30 - 2x)(20 - 2x) = 4x^3 - 100x^2 + 600x$.

$V'(x) = 12x^2 - 200x + 600 = 4(3x^2 - 50x + 150)$. Pour $3x^2 - 50x + 150$ : $\Delta = 2500 - 1800 = 700 = 100\times 7$, donc les racines sont

$$x_1 = \dfrac{50 - 10\sqrt{7}}{6} = \dfrac{25 - 5\sqrt{7}}{3} \approx 3{,}92 \qquad \text{et} \qquad x_2 = \dfrac{25 + 5\sqrt{7}}{3} \approx 12{,}74.$$

Seule $x_1$ appartient à $]0\,;10[$. Le coefficient de $x^2$ étant positif, $V'$ est positive avant $x_1$ et négative entre $x_1$ et $10$ : $V$ croît puis décroît, elle est donc maximale en $x = \dfrac{25 - 5\sqrt{7}}{3} \approx 3{,}92$ cm (valeur approchée au centième). Le volume maximal vaut alors environ $1\,056$ cm³ (arrondi à l'unité).

### Pourquoi les autres réponses sont fausses

- **a)** $\dfrac{25 + 5\sqrt{7}}{3}\approx 12{,}74$ est l'autre racine de $V'$, mais elle n'appartient pas à $]0\,;10[$ : on a oublié la condition sur $x$.
- **b)** $\dfrac{50 - 10\sqrt{7}}{3}$ : on a divisé par $a=3$ au lieu de $2a=6$ dans la formule des racines.
- **d)** $\dfrac{25 - 5\sqrt{7}}{6}$ : on a simplifié le numérateur par $2$ sans simplifier le dénominateur.

</details>

Avis : 

---

## 28. `cqc-fonction-polynome-moyenne-2` (séries A/C/E)

**Remarque du relecteur :** LIMITE : factorisation d'un polynôme de degré 3 et tableau de signes à trois facteurs, à la limite haute pour la série A.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit le polynôme $P(x) = x^3 - 2x^2 - 5x + 6$, dont $1$ est une racine.

Quel est l'ensemble des solutions dans $\mathbb{R}$ de l'inéquation $P(x) > 0$ ?

- a) $]-2\,;1[\, \cup\, ]3\,;+\infty[$
- b) $]-\infty\,;-2[\, \cup\, ]1\,;3[$
- c) $]-3\,;1[\, \cup\, ]2\,;+\infty[$
- d) $]3\,;+\infty[$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Si un réel $a$ est racine d'un polynôme $P$, alors $P(x)$ est factorisable par $(x - a)$ ; on identifie le second facteur par développement et identification des coefficients, on factorise le trinôme obtenu, puis on dresse le tableau de signes du produit pour résoudre l'inéquation.

### Corrigé

$P(1) = 1 - 2 - 5 + 6 = 0$ : $1$ est bien racine de $P$.

Développons : $(x - 1)(x^2 + bx + c) = x^3 + (b - 1)x^2 + (c - b)x - c$. Par identification avec $x^3 - 2x^2 - 5x + 6$ : $b - 1 = -2$ donc $b = -1$ ; $-c = 6$ donc $c = -6$ ; contrôle : $c - b = -6 + 1 = -5$.

Ainsi $P(x) = (x - 1)(x^2 - x - 6)$. Pour le trinôme, $\Delta = 1 + 24 = 25$, d'où $x = \dfrac{1 - 5}{2} = -2$ ou $x = \dfrac{1 + 5}{2} = 3$. Donc $x^2 - x - 6 = (x + 2)(x - 3)$ et

$$P(x) = (x - 1)(x - 3)(x + 2).$$

Tableau de signes (racines rangées : $-2 < 1 < 3$) :

| $x$ | $-\infty$ | | $-2$ | | $1$ | | $3$ | | $+\infty$ |
|---|---|---|---|---|---|---|---|---|---|
| $x + 2$ | | $-$ | $0$ | $+$ | | $+$ | | $+$ | |
| $x - 1$ | | $-$ | | $-$ | $0$ | $+$ | | $+$ | |
| $x - 3$ | | $-$ | | $-$ | | $-$ | $0$ | $+$ | |
| $P(x)$ | | $-$ | $0$ | $+$ | $0$ | $-$ | $0$ | $+$ | |

Donc $P(x) > 0$ si et seulement si $x \in\, ]-2\,;1[\, \cup\, ]3\,;+\infty[$.

### Pourquoi les autres réponses sont fausses

- **b)** C'est l'ensemble où $P(x) < 0$ : les signes du tableau ont été inversés.
- **c)** On a pris $2$ et $-3$ pour racines du trinôme $x^2 - x - 6$ (erreur de signe dans $\dfrac{-b\pm\sqrt\Delta}{2a}$).
- **d)** On a oublié l'intervalle $]-2\,;1[$ où les deux facteurs négatifs donnent un produit positif.

</details>

Avis : 

---

## 29. `cqc-fonction-polynome-du-second-degre-prob-a-moyenne-2` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $f(x)=2x^2-8x+6$. Quelles sont les racines de $f$ et le sommet $S$ de sa courbe ?

- a) Racines $1$ et $3$ ; $S(2\,;6)$
- b) Racines $1$ et $3$ ; $S(4\,;6)$
- c) Racines $-1$ et $-3$ ; $S(-2\,;30)$
- d) Racines $1$ et $3$ ; $S(2\,;-2)$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

$\Delta=b^2-4ac$ ; sommet d'abscisse $x=-\dfrac b{2a}$.

### Corrigé

$\Delta=64-48=16$ ; racines $\dfrac{8\pm4}{4}$ : $1$ et $3$. Sommet : $x=-\dfrac{-8}{4}=2$, $f(2)=8-16+6=-2$ : $S(2\,;-2)$. $a=2>0$ : $f$ décroît sur $]-\infty\,;2]$ puis croît sur $[2\,;+\infty[$.

### Pourquoi les autres réponses sont fausses

- **a)** On a calculé $2\times2^2$ comme $(2\times2)^2=16$, d'où $f(2)=16-16+6=6$.
- **b)** On a pris $-\dfrac ba=4$ au lieu de $-\dfrac b{2a}=2$ pour l'abscisse du sommet.
- **c)** Erreur de signe sur les racines ($\dfrac{-8\pm4}{4}$) et sur l'abscisse du sommet.

</details>

Avis : 

---

## 30. `cqc-fonction-polynome-du-second-degre-prob-a-moyenne-3` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Quelle est la forme canonique de $x^2-6x+5$, et quel est son extremum ?

- a) $(x-3)^2-4$ ; minimum $-4$ atteint en $x=3$
- b) $(x+3)^2-4$ ; minimum $-4$ atteint en $x=-3$
- c) $(x-3)^2+14$ ; minimum $14$ atteint en $x=3$
- d) $(x-6)^2-31$ ; minimum $-31$ atteint en $x=6$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

$x^2-6x=(x-3)^2-9$.

### Corrigé

$x^2-6x+5=(x-3)^2-9+5=(x-3)^2-4$. Comme $(x-3)^2\ge0$, le minimum vaut $-4$, atteint en $x=3$.

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de signe : $x^2-6x$ commence le développement de $(x-3)^2$, pas de $(x+3)^2$.
- **c)** On a ajouté $9$ au lieu de le retrancher : $(x-3)^2=x^2-6x+9$, il faut donc enlever $9$.
- **d)** On a pris $6$ au lieu de sa moitié $3$ : $(x-6)^2=x^2-12x+36$ ne commence pas par $x^2-6x$.

</details>

Avis : 

---

## 31. `cqc-fonction-polynome-du-second-degre-prob-a-moyenne-4` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $f(x)=-x^2+2x+3$. Quel est l'ensemble des réels $x$ tels que $f(x)>0$ ?

- a) $[-1\,;3]$
- b) $]-\infty\,;-1[\,\cup\,]3\,;+\infty[$
- c) $]-3\,;1[$
- d) $]-1\,;3[$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Un trinôme est du signe de $a$ à l'extérieur des racines et du signe contraire entre les racines. Ici $a=-1<0$ : $f$ est positive entre les racines.

### Corrigé

$\Delta=4+12=16$ ; racines $\dfrac{-2\pm4}{-2}$ : $-1$ et $3$. Maximum en $x=1$ : $f(1)=-1+2+3=4$. $f(x)>0\iff x\in\,]-1\,;3[$.

### Pourquoi les autres réponses sont fausses

- **a)** Les bornes sont exclues : en $-1$ et en $3$, $f(x)=0$, ce qui n'est pas strictement positif.
- **b)** C'est l'ensemble où $f(x)<0$ : on a appliqué la règle comme si $a$ était positif.
- **c)** Erreur de signe dans le calcul des racines ($\dfrac{2\pm4}{-2}$ donne $-3$ et $1$).

</details>

Avis : 

---

## 32. `cqc-fonction-polynome-du-second-degre-prob-a-moyenne-5` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Pour quelles valeurs du réel $m$ l'équation $x^2-2x=m$ admet-elle exactement deux solutions distinctes ?

- a) $m\geqslant-1$
- b) $m>-1$
- c) $m<1$
- d) $m<-1$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On se ramène à $x^2-2x-m=0$ et on étudie le signe du discriminant.

### Corrigé

$\Delta=(-2)^2-4\times1\times(-m)=4+4m$. Si $m>-1$ : $\Delta>0$, deux solutions ; si $m=-1$ : $\Delta=0$, une solution double $x=1$ ; si $m<-1$ : aucune solution (le minimum de $x^2-2x$ vaut $-1$). Il y a donc exactement deux solutions distinctes si et seulement si $m>-1$.

### Pourquoi les autres réponses sont fausses

- **a)** Pour $m=-1$, $\Delta=0$ : il n'y a qu'une solution (double), pas deux.
- **c)** On a écrit $\Delta=4-4m$ en oubliant que $c=-m$.
- **d)** On a inversé le sens de l'inégalité en résolvant $4+4m>0$.

</details>

Avis : 

---

## 33. `cqc-fonctions-associees-prob-a-faible-0` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $f$ une fonction et $a$ un réel strictement positif. Comment obtient-on la courbe de la fonction $h$ définie par $h(x)=f(x+a)$ à partir de la courbe de $f$ ?

- a) On la déplace de $a$ unités vers la droite.
- b) On la déplace de $a$ unités vers le haut.
- c) On la déplace de $a$ unités vers la gauche.
- d) On la déplace de $a$ unités vers le bas.

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Ajouter une constante à la variable déplace la courbe horizontalement ; ajouter une constante à la fonction la déplace verticalement.

### Corrigé

La courbe de $g(x)=f(x)+k$ s'obtient en déplaçant celle de $f$ verticalement de $k$ unités. Celle de $h(x)=f(x+a)$ s'obtient en déplaçant celle de $f$ horizontalement de $a$ unités vers la **gauche** : le point d'abscisse $x_0$ de la courbe de $f$ correspond au point d'abscisse $x_0-a$ de la courbe de $h$, car $h(x_0-a)=f(x_0)$. Les variations sont conservées (décalées).

### Pourquoi les autres réponses sont fausses

- **a)** Confusion de sens : c'est $f(x-a)$ qui déplace la courbe de $a$ unités vers la droite.
- **b)** Confusion avec $f(x)+a$, qui déplace la courbe verticalement.
- **d)** Double confusion : déplacement vertical, et de plus dans le mauvais sens.

</details>

Avis : 

---

## 34. `cqc-fonctions-associees-prob-a-moyenne-2` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

On pose $f(x)=x^2$ et $g(x)=f(x-3)+1$. Quels sont le sommet de la courbe de $g$ et le sens de variation de $g$ ?

- a) $S(3\,;1)$ ; $g$ décroissante sur $]-\infty\,;3]$ et croissante sur $[3\,;+\infty[$
- b) $S(-3\,;1)$ ; $g$ décroissante sur $]-\infty\,;-3]$ et croissante sur $[-3\,;+\infty[$
- c) $S(1\,;3)$ ; $g$ décroissante sur $]-\infty\,;1]$ et croissante sur $[1\,;+\infty[$
- d) $S(3\,;1)$ ; $g$ croissante sur $]-\infty\,;3]$ et décroissante sur $[3\,;+\infty[$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

$g(x)=(x-3)^2+1$ : la courbe de $g$ s'obtient en déplaçant celle de $x^2$ de $3$ unités vers la droite et de $1$ unité vers le haut.

### Corrigé

$g(x)=(x-3)^2+1$ : sommet $S(3\,;1)$. $g$ est décroissante sur $]-\infty\,;3]$ et croissante sur $[3\,;+\infty[$ (mêmes variations que $x^2$ décalées) ; minimum $1$.

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de sens : $f(x-3)$ décale la courbe vers la droite, pas vers la gauche.
- **c)** Les coordonnées du sommet ont été inversées.
- **d)** Les variations ont été inversées : comme $x^2$, $g$ décroît avant son sommet et croît après.

</details>

Avis : 

---

## 35. `cqc-fonctions-associees-prob-a-moyenne-4` (séries A)

**Énoncé :**

Soit $f(x)=x^2-4x$ et $g(x)=f(x)+4$. Quel est le minimum de $g$ ?

- a) Minimum $4$, atteint en $x=2$
- b) Minimum $-4$, atteint en $x=2$
- c) Minimum $0$, atteint en $x=-2$
- d) Minimum $0$, atteint en $x=2$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

$x^2-4x+4$ est une identité remarquable.

### Corrigé

$g(x)=x^2-4x+4=(x-2)^2\ge0$ avec égalité pour $x=2$ : minimum $0$ atteint en $x=2$. La courbe de $g$ est celle de $f$ déplacée de $4$ unités vers le haut.

### Pourquoi les autres réponses sont fausses

- **a)** On a pris la constante ajoutée, $4$, pour le minimum.
- **b)** $-4$ est le minimum de $f$ (atteint en $x=2$), pas celui de $g=f+4$.
- **c)** Erreur de signe : $(x-2)^2$ s'annule en $x=2$, pas en $x=-2$.

</details>

Avis : 

---

## 36. `cqc-fonctions-associees-prob-a-moyenne-5` (séries A)

**Remarque du relecteur :** Attention : la seule réponse exacte est b) ; si la clé prévue est c) (symétrie par rapport à l'origine), elle est fausse, car la symétrie centrale envoie C_f sur elle-même.

**Énoncé :**

Soit $f(x)=x^3$ et $k(x)=f(-x)$. Laquelle des affirmations suivantes est exacte ?

- a) $k(x)=x^3$ : les courbes de $f$ et de $k$ sont confondues.
- b) $k(x)=-x^3$ : les courbes de $f$ et de $k$ sont symétriques par rapport à l'axe des ordonnées et aussi par rapport à l'axe des abscisses.
- c) $k(x)=-x^3$ : les courbes de $f$ et de $k$ sont symétriques par rapport à l'origine du repère.
- d) $k(x)=-x^3$ : les courbes de $f$ et de $k$ sont symétriques par rapport à la droite d'équation $y=x$.

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

$k(x)=f(-x)=(-x)^3$ ; un cube conserve le signe.

### Corrigé

$k(x)=(-x)^3=-x^3$. Les courbes de $f$ et de $k$ sont symétriques par rapport à l'axe des ordonnées (car $k(x)=f(-x)$) ; comme $f$ est impaire, $k=-f$ et elles sont aussi symétriques par rapport à l'axe des abscisses.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe : $(-x)^3=-x^3$ et non $x^3$ (un exposant impair conserve le signe).
- **c)** Le symétrique par rapport à l'origine du point $(x\,;x^3)$ est $(-x\,;-x^3)$, qui est sur la courbe de $f$ elle-même, pas sur celle de $k$ (sauf en $0$).
- **d)** Confusion avec une autre symétrie : le symétrique de la courbe de $f$ par rapport à la droite $y=x$ n'est pas la courbe de $-x^3$.

</details>

Avis : 

---

## 37. `cqc-image-d-un-reel-par-une-fonction-prob-a-faible-0` (séries A)

**Remarque du relecteur :** Formulation à resserrer : « un réel x de l'ensemble de définition a une seule image ; un réel y peut avoir plusieurs antécédents » (dans a, le même « réel » joue les deux rôles).

**Énoncé :**

Soit $f$ une fonction. Laquelle des affirmations suivantes est exacte ?

- a) Un réel $x$ de l'ensemble de définition a une seule image par $f$, mais un réel $y$ peut avoir plusieurs antécédents.
- b) Un réel peut avoir plusieurs images par $f$.
- c) Tout réel a au moins un antécédent par $f$.
- d) Si $y=f(x)$, alors $y$ est un antécédent de $x$.

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Une fonction associe à chaque réel $x$ de son ensemble de définition un unique réel $f(x)$.

### Corrigé

$y$ est l'image de $x$ si $y=f(x)$ : chaque $x$ a **au plus une** image. Alors $x$ est **un antécédent** de $y$ : un réel $y$ peut avoir plusieurs antécédents, un seul ou aucun.

### Pourquoi les autres réponses sont fausses

- **b)** Par définition d'une fonction, un réel a au plus une image.
- **c)** Un réel peut n'avoir aucun antécédent (par exemple $-1$ n'a pas d'antécédent par $x\mapsto x^2$).
- **d)** Les rôles sont inversés : si $y=f(x)$, c'est $x$ qui est un antécédent de $y$.

</details>

Avis : 

---

## 38. `cqc-parabole-prob-c-moyenne-2` (séries A/C/E)

**Énoncé :**

Quelle est la forme canonique de $f(x)=2x^2-8x+3$, et quel est l'extremum de $f$ ?

- a) $f(x)=2(x-2)^2-1$ ; minimum $-1$ atteint en $x=2$
- b) $f(x)=2(x-2)^2-5$ ; minimum $-5$ atteint en $x=2$
- c) $f(x)=2(x+2)^2-5$ ; minimum $-5$ atteint en $x=-2$
- d) $f(x)=2(x-4)^2-29$ ; minimum $-29$ atteint en $x=4$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

La forme canonique est $f(x)=a(x-\alpha)^2+\beta$ avec $\alpha=-\dfrac b{2a}$ et $\beta=f(\alpha)$. Le sommet de la parabole est $S(\alpha\,;\beta)$ ; $f$ a un minimum si $a>0$ et un maximum si $a<0$.

### Corrigé

$\alpha=-\dfrac{-8}4=2$ et $\beta=f(2)=8-16+3=-5$.
$$f(x)=2(x-2)^2-5.$$
Le sommet est $S(2\,;-5)$ et, comme $a=2>0$, $f$ admet un minimum égal à $-5$ atteint en $x=2$.

### Pourquoi les autres réponses sont fausses

- **a)** On a écrit $2(x^2-4x)=2\bigl[(x-2)^2-4\bigr]$ puis oublié de multiplier $-4$ par $2$ : $2(x-2)^2-4+3$.
- **c)** Erreur de signe sur $\alpha$ : $\alpha=-\dfrac b{2a}=2$, pas $-2$.
- **d)** On a complété le carré sur $x^2-8x$ en oubliant de mettre $2$ en facteur : $(x-4)^2-16$, puis $2(x-4)^2-32+3$.

</details>

Avis : 

---

## 39. `cqc-pourcentage-prob-d-moyenne-2` (séries A/D)

**Remarque du relecteur :** Question double (deux calculs indépendants dans un même item) ; acceptable mais à scinder de préférence.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Dans une classe de $40$ élèves, $14$ ont une note supérieure ou égale à $12$. Quel est le pourcentage d'élèves dans ce cas, et combien d'élèves représentent $15\ \%$ de la classe ?

- a) $14\ \%$ et $6$ élèves
- b) $65\ \%$ et $6$ élèves
- c) $35\ \%$ et $6$ élèves
- d) $35\ \%$ et $15$ élèves

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Le pourcentage d'une partie dans un ensemble est $\dfrac{\text{partie}}{\text{total}}\times100$ ; inversement, $t\ \%$ d'un total $N$ vaut $N\times\dfrac t{100}$.

### Corrigé

$\dfrac{14}{40}\times100=35\ \%$. Et $15\ \%$ de $40$ : $40\times0{,}15=6$ élèves.

### Pourquoi les autres réponses sont fausses

- **a)** Confond l'effectif ($14$ élèves) avec le pourcentage : $14$ sur $40$ ne fait pas $14\ \%$.
- **b)** $65\ \%$ est le pourcentage des élèves ayant moins de $12$ ($26$ sur $40$), pas celui demandé.
- **d)** Confond $15\ \%$ de la classe avec $15$ élèves : il faut calculer $40\times0{,}15$.

</details>

Avis : 

---

## 40. `cqc-pourcentage-prob-d-moyenne-3` (séries A/D)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Après une hausse de $25\ \%$, un produit coûte $10\,000$ F. Quel était son prix initial ? (Arrondir au franc près si nécessaire.)

- a) $7\,500$ F
- b) $12\,500$ F
- c) $13\,333$ F
- d) $8\,000$ F

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Augmenter de $t\ \%$ revient à multiplier par le coefficient multiplicateur $1+\dfrac t{100}$. Pour retrouver une valeur initiale, on divise donc la valeur finale par ce coefficient (et non en retranchant naïvement le pourcentage de la valeur finale).

### Corrigé

Coefficient multiplicateur : $1+0{,}25=1{,}25$. Prix initial : $\dfrac{10\,000}{1{,}25}=8\,000$ F (résultat exact, aucun arrondi au franc n'est nécessaire).
Vérification : $8\,000\times1{,}25=10\,000$ F.

### Pourquoi les autres réponses sont fausses

- **a)** $10\,000-25\ \%\times10\,000=7\,500$ F : le pourcentage a été calculé sur le prix final au lieu du prix initial ($7\,500\times1{,}25=9\,375$ F).
- **b)** $10\,000\times1{,}25=12\,500$ F : on a appliqué une nouvelle hausse au lieu de remonter au prix initial.
- **c)** $\dfrac{10\,000}{0{,}75}\approx13\,333$ F : on a utilisé le coefficient d'une baisse de $25\ \%$.

</details>

Avis : 

---

## 41. `cqc-probleme-concret-prob-a-moyenne-4` (séries A)

**Remarque du relecteur :** VOCABULAIRE : x est un nombre d'objets (entier) ; « 10<x<30 » se lit alors sur les entiers 11 à 29, sans conséquence sur la clé.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Le bénéfice d'une entreprise pour la vente de $x$ objets est $B(x)=-x^2+40x-300$. Pour quelles valeurs de $x$ le bénéfice est-il strictement positif, et quel est le bénéfice maximal ?

- a) $x<10$ ou $x>30$ ; bénéfice maximal $100$
- b) $10<x<30$ ; bénéfice maximal $20$
- c) $10<x<30$ ; bénéfice maximal $900$
- d) $10<x<30$ ; bénéfice maximal $100$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Un trinôme est du signe de $a$ à l'extérieur de ses racines et du signe contraire entre elles. Le maximum (pour $a<0$) est atteint au sommet $x=-\dfrac b{2a}$.

### Corrigé

$\Delta=1600-1200=400$ ; racines $\dfrac{-40\pm20}{-2}$, soit $10$ et $30$. Comme $a<0$, $B(x)>0\iff10<x<30$. Maximum en $x=-\dfrac{40}{-2}=20$ : $B(20)=-400+800-300=100$.

### Pourquoi les autres réponses sont fausses

- **a)** Applique la règle du signe comme si $a>0$ : entre les racines, $B$ est du signe contraire de $a=-1$, donc positif.
- **b)** Donne l'abscisse du sommet ($x=20$) au lieu de la valeur du bénéfice $B(20)$.
- **c)** Erreur de signe sur $-x^2$ : $-20^2=-400$ et non $+400$.

</details>

Avis : 

---

## 42. `cqc-reduction-au-meme-denominateur-prob-a-faible-0` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $a$, $b$, $c$, $d$ des réels avec $b\ne0$ et $d\ne0$. À quoi est égale la somme $\dfrac ab+\dfrac cd$ ?

- a) $\dfrac{a+c}{b+d}$
- b) $\dfrac{a+c}{bd}$
- c) $\dfrac{ad+bc}{bd}$
- d) $\dfrac{ac+bd}{bd}$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour additionner deux fractions, on les réduit au même dénominateur (multiple commun des dénominateurs), puis on additionne les numérateurs.

### Corrigé

Avec le dénominateur commun $bd$ : $\dfrac ab=\dfrac{ad}{bd}$ et $\dfrac cd=\dfrac{bc}{bd}$, donc $\dfrac ab+\dfrac cd=\dfrac{ad+bc}{bd}$. Pour des fractions algébriques, on multiplie de même numérateur et dénominateur par les facteurs manquants.
Exemple : $\dfrac12+\dfrac13=\dfrac{3+2}6=\dfrac56$.

### Pourquoi les autres réponses sont fausses

- **a)** Additionne numérateurs et dénominateurs entre eux : $\dfrac12+\dfrac13$ donnerait $\dfrac25$, faux.
- **b)** Prend bien le dénominateur $bd$ mais oublie de multiplier les numérateurs : $\dfrac12+\dfrac13$ donnerait $\dfrac26$.
- **d)** Mélange les produits ($ac$ au lieu de $ad$) : $\dfrac12+\dfrac13$ donnerait $\dfrac96$.

</details>

Avis : 

---

## 43. `cqc-reduction-au-meme-denominateur-prob-a-moyenne-3` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Pour $x\ne1$ et $x\ne-2$, quelle est l'écriture de $\dfrac2{x-1}-\dfrac3{x+2}$ sous la forme d'une seule fraction ?

- a) $\dfrac{-x+1}{(x-1)(x+2)}$
- b) $\dfrac{-1}{(x-1)(x+2)}$
- c) $\dfrac{5x+1}{(x-1)(x+2)}$
- d) $\dfrac{-x+7}{(x-1)(x+2)}$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Dénominateur commun : $(x-1)(x+2)$. Attention au signe moins devant la seconde fraction, qui porte sur tout son numérateur.

### Corrigé

$\dfrac{2(x+2)-3(x-1)}{(x-1)(x+2)}=\dfrac{2x+4-3x+3}{(x-1)(x+2)}=\dfrac{-x+7}{(x-1)(x+2)}$.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe : $-3(x-1)=-3x+3$ et non $-3x-3$.
- **b)** Soustrait les numérateurs $2-3$ sans les multiplier par les facteurs manquants.
- **c)** Oublie le signe moins : calcule $2(x+2)+3(x-1)$.

</details>

Avis : 

---

## 44. `cqc-reduction-au-meme-denominateur-prob-a-moyenne-4` (séries A)

**Énoncé :**

Pour $x\ne0$, quelle est l'écriture de $x-\dfrac1x$ sous la forme d'une seule fraction ?

- a) $\dfrac{x-1}x$
- b) $\dfrac{1-x^2}x$
- c) $\dfrac{x^2-1}x$
- d) $\dfrac{(x-1)^2}x$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On écrit $x=\dfrac{x^2}x$ pour avoir le même dénominateur.

### Corrigé

$x-\dfrac1x=\dfrac{x^2}x-\dfrac1x=\dfrac{x^2-1}x=\dfrac{(x-1)(x+1)}x$.

### Pourquoi les autres réponses sont fausses

- **a)** Oublie de multiplier $x$ par le dénominateur $x$ : écrit $x=\dfrac xx$.
- **b)** Inverse l'ordre de la soustraction : on obtient l'opposé du résultat.
- **d)** Confond $x^2-1$ avec l'identité remarquable $(x-1)^2=x^2-2x+1$.

</details>

Avis : 

---

## 45. `cqc-resolution-de-systeme-prob-a-moyenne-2` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Quelle est la solution du système $\begin{cases}2x-y=3\\x+2y=4\end{cases}$ ?

- a) $(2\,;-1)$
- b) $(2\,;1)$
- c) $(1\,;2)$
- d) $\left(\dfrac75\,;-\dfrac15\right)$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Méthode par combinaison : on multiplie la première équation par $2$ pour éliminer $y$ en additionnant.

### Corrigé

$4x-2y=6$ ; en additionnant à $x+2y=4$ : $5x=10\Rightarrow x=2$, puis $y=2\times2-3=1$. Solution : $(2\,;1)$. Vérification : $2+2\times1=4$.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe en isolant $y$ : $y=2x-3=1$ et non $3-2x$.
- **c)** Inverse $x$ et $y$ : $2\times1-2=0\ne3$.
- **d)** Multiplie seulement le membre de gauche par $2$ ($4x-2y=3$) : les deux membres doivent être multipliés.

</details>

Avis : 

---

## 46. `cqc-signe-d-une-fonction-affine-prob-a-faible-0` (séries A)

**Remarque du relecteur :** L'hypothèse b non nul est inutile mais sans effet sur la réponse.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $a$ et $b$ deux réels non nuls avec $a<0$. Pour quelles valeurs de $x$ l'expression $ax+b$ est-elle strictement positive ?

- a) $x<-\dfrac ba$
- b) $x>-\dfrac ba$
- c) $x<\dfrac ba$
- d) $x>\dfrac ba$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

$ax+b$ s'annule en $x_0=-\dfrac ba$ et elle est du signe de $a$ à droite de cette racine.

### Corrigé

$ax+b$ s'annule en $x_0=-\dfrac ba$. Si $a>0$ : négatif à gauche de $x_0$ et positif à droite. Si $a<0$ : positif à gauche et négatif à droite. Ici $a<0$, donc $ax+b>0\iff x<-\dfrac ba$.
Exemple : $-2x+4>0\iff x<2$.

### Pourquoi les autres réponses sont fausses

- **b)** Applique la règle du cas $a>0$ : à droite de la racine, $ax+b$ est du signe de $a$, donc négatif.
- **c)** Erreur de signe sur la racine : $ax+b=0\iff x=-\dfrac ba$ et non $\dfrac ba$.
- **d)** Cumule l'erreur sur la racine et la règle du cas $a>0$ ; avec $-2x+4$, cela donnerait $x>-2$.

</details>

Avis : 

---

## 47. `cqc-signe-d-une-fonction-affine-prob-a-moyenne-2` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Quel est l'ensemble des solutions de l'inéquation $-3x+9\ge0$ ?

- a) $[3\,;+\infty[$
- b) $]-\infty\,;-3]$
- c) $]-\infty\,;3]$
- d) $[-3\,;+\infty[$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

$-3x+9$ s'annule en $x=3$ et, comme $a=-3<0$, elle est positive à gauche de sa racine et négative à droite.

### Corrigé

$-3x+9$ est positif pour $x<3$, nul en $3$ et négatif pour $x>3$. Donc $-3x+9\ge0\iff x\le3$, soit $S=]-\infty\,;3]$.

### Pourquoi les autres réponses sont fausses

- **a)** Oublie de changer le sens de l'inégalité en divisant par $-3$ (ou applique la règle du cas $a>0$).
- **b)** Erreur de signe sur la racine ($-3$ au lieu de $3$).
- **d)** Cumule les deux erreurs : mauvaise racine et sens de l'inégalité non changé.

</details>

Avis : 

---

## 48. `cqc-signe-d-une-fonction-affine-prob-a-moyenne-3` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Quel est l'ensemble des solutions de l'inéquation $(x-1)(3-x)>0$ ?

- a) $]-\infty\,;1[\cup]3\,;+\infty[$
- b) $]1\,;3[$
- c) $[1\,;3]$
- d) $]-3\,;-1[$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On étudie le signe de chaque facteur affine (tableau de signes), puis on applique la règle des signes d'un produit.

### Corrigé

$x-1$ : négatif avant $1$, positif après. $3-x$ : positif avant $3$, négatif après. Produit : négatif si $x<1$, positif si $1<x<3$, négatif si $x>3$. Donc $(x-1)(3-x)>0\iff x\in]1\,;3[$.

### Pourquoi les autres réponses sont fausses

- **a)** Traite le facteur $3-x$ comme $x-3$ : on obtient le signe de $(x-1)(x-3)$, qui est l'opposé.
- **c)** Inclut les bornes : en $1$ et en $3$ le produit est nul, donc pas strictement positif.
- **d)** Erreur de signe sur les racines ($-1$ et $-3$ au lieu de $1$ et $3$).

</details>

Avis : 

---

## 49. `cqc-signe-d-une-fonction-affine-prob-a-moyenne-4` (séries A)

**Énoncé :**

Quel est l'ensemble des solutions de l'inéquation $\dfrac{2x+4}{x-1}\ge0$ ?

- a) $]-\infty\,;-2]\cup]1\,;+\infty[$
- b) $]-\infty\,;-2]\cup[1\,;+\infty[$
- c) $[-2\,;1[$
- d) $]-\infty\,;-2[\cup]1\,;+\infty[$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Valeur interdite : $x=1$. On étudie le signe du numérateur et du dénominateur dans un tableau de signes, puis on garde les intervalles où le quotient est positif ou nul ; la valeur interdite est toujours exclue.

### Corrigé

Numérateur nul en $-2$, dénominateur nul en $1$ (interdit). Tableau : $x<-2$ : $(-)/(-)=+$ ; $-2<x<1$ : $(+)/(-)=-$ ; $x>1$ : $+$. En $x=-2$ le quotient vaut $0$, ce qui convient. Solutions : $x\in]-\infty\,;-2]\cup]1\,;+\infty[$.

### Pourquoi les autres réponses sont fausses

- **b)** Le crochet fermé en $1$ oublie que $1$ est une valeur interdite.
- **c)** C'est l'intervalle où le quotient est négatif : les signes du tableau ont été inversés.
- **d)** Le crochet ouvert en $-2$ oublie que le quotient y vaut $0$, ce qui vérifie $\ge0$.

</details>

Avis : 

---

## 50. `cqc-somme-et-produit-de-deux-nombres-prob-a-moyenne-4` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Sans calculer les racines de l'équation $2x^2-6x+4=0$, donner leur somme $S$ et leur produit $P$.

- a) $S=3$ et $P=2$
- b) $S=-3$ et $P=2$
- c) $S=6$ et $P=4$
- d) $S=3$ et $P=\dfrac12$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

$S=-\dfrac ba$ et $P=\dfrac ca$.

### Corrigé

$S=\dfrac62=3$ et $P=\dfrac42=2$. Les racines de somme $3$ et de produit $2$ sont $1$ et $2$ ; vérification : $2\times1-6+4=0$ et $2\times4-12+4=0$.

### Pourquoi les autres réponses sont fausses

- **b)** Le signe moins de $S=-\dfrac ba$ a été oublié.
- **c)** On a oublié de diviser par $a=2$.
- **d)** Le produit a été inversé : $\dfrac ac$ au lieu de $\dfrac ca$.

</details>

Avis : 

---

## 51. `cqc-somme-et-produit-de-deux-nombres-prob-a-moyenne-5` (séries A)

**Remarque du relecteur :** LIMITE : relations somme-produit des racines pour la série A.

**Énoncé :**

Pour quelle valeur du réel $m$ l'équation $x^2-5x+m=0$ a-t-elle deux racines dont l'une est le double de l'autre ?

- a) $m=\dfrac{25}9$
- b) $m=\dfrac{25}2$
- c) $m=\dfrac{50}9$
- d) $m=-\dfrac{50}9$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On note les racines $r$ et $2r$ : leur somme donne $3r=5$ et leur produit donne $m=r\times2r$.

### Corrigé

$3r=5\Rightarrow r=\dfrac53$ ; les racines sont $\dfrac53$ et $\dfrac{10}3$. $m=2r^2=\dfrac{50}9$. Vérification : $\Delta=25-\dfrac{200}9=\dfrac{25}9>0$.

### Pourquoi les autres réponses sont fausses

- **a)** On a pris $m=r^2$ en oubliant le facteur $2$ du produit $r\times2r$.
- **b)** On a écrit la somme $2r=5$ au lieu de $r+2r=5$.
- **d)** Erreur de signe : le produit vaut $\dfrac ca=m$, pas $-m$.

</details>

Avis : 

---

## 52. `cqc-symetrie-par-rapport-a-l-axe-des-abscisses-prob-a-moyenne-3` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

On note $\mathcal C$ la courbe de la fonction $f(x)=x^2-1$. La symétrique de $\mathcal C$ par rapport à l'axe des abscisses est la courbe d'une fonction $g$. Quelle est l'expression de $g(x)$ ?

- a) $g(x)=1-x^2$
- b) $g(x)=-x^2-1$
- c) $g(x)=x^2-1$
- d) $g(x)=x^2+1$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Le symétrique de $(x\,;y)$ par rapport à l'axe des abscisses est $(x\,;-y)$, donc $g(x)=-f(x)$.

### Corrigé

$g(x)=-(x^2-1)=1-x^2$. Les zéros sont inchangés : $x=\pm1$ (les points de la courbe sur l'axe restent fixes). Le minimum $-1$ de $f$ devient le maximum $1$ de $g$.

### Pourquoi les autres réponses sont fausses

- **b)** Le signe moins n'a été appliqué qu'au premier terme : $-(x^2-1)\ne-x^2-1$.
- **c)** Confusion avec la symétrie par rapport à l'axe des ordonnées, $f(-x)=x^2-1$, qui laisse ici la courbe inchangée.
- **d)** On a changé le signe du seul terme constant.

</details>

Avis : 

---

## 53. `cqc-symetrie-par-rapport-a-l-axe-des-abscisses-prob-a-moyenne-5` (séries A)

**Remarque du relecteur :** « croissante » (sens large) donne « décroissante » (sens large) ; cohérent.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $f$ une fonction croissante sur un intervalle $I$ (par exemple $f(x)=x^2$ sur $[0\,;+\infty[$). Que peut-on dire du sens de variation de la fonction $-f$ sur $I$ ?

- a) $-f$ est croissante sur $I$
- b) $-f$ est croissante si $f$ est positive, décroissante sinon
- c) $-f$ est décroissante sur $I$
- d) On ne peut rien dire sans connaître l'expression de $f$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Multiplier les deux membres d'une inégalité par $-1$ inverse son sens.

### Corrigé

Si $a<b$ dans $I$, alors $f(a)\le f(b)$, donc $-f(a)\ge-f(b)$ : $-f$ est décroissante sur $I$. Les fonctions $f$ et $-f$ ont des variations opposées. Sur $[0\,;+\infty[$, $x^2$ est croissante donc $-x^2$ est décroissante.

### Pourquoi les autres réponses sont fausses

- **a)** On a oublié que multiplier par $-1$ change le sens des inégalités.
- **b)** Le signe de $f$ n'intervient pas : seul l'ordre des images compte.
- **d)** On peut conclure dans tous les cas grâce à la règle des inégalités.

</details>

Avis : 

---

## 54. `cqc-systemes-d-equations-lineaires-prob-a-faible-0` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

À quelle condition le système $\begin{cases}ax+by=c\\a'x+b'y=c'\end{cases}$ admet-il une solution unique ?

- a) $ab'-a'b=0$
- b) $ab-a'b'\ne0$
- c) $c\ne0$ et $c'\ne0$
- d) $ab'-a'b\ne0$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Le déterminant $D=ab'-a'b$ du système décide du nombre de solutions.

### Corrigé

Il admet une **solution unique** si et seulement si $D=ab'-a'b\ne0$. On la trouve alors par substitution ou par combinaison (élimination d'une inconnue). Si $D=0$, il n'y a aucune solution ou une infinité.

### Pourquoi les autres réponses sont fausses

- **a)** C'est la condition inverse : si $D=0$, il n'y a jamais de solution unique.
- **b)** On a multiplié les mauvais coefficients : le déterminant croise les coefficients des deux équations.
- **c)** Les seconds membres $c$ et $c'$ n'interviennent pas dans l'unicité de la solution.

</details>

Avis : 

---

## 55. `cqc-systemes-d-equations-lineaires-prob-a-moyenne-3` (séries A)

**Énoncé :**

Que peut-on dire des solutions du système $\begin{cases}3x+2y=7\\6x+4y=14\end{cases}$ ?

- a) Le système n'a aucune solution car $D=0$
- b) Le système a une solution unique : $(1\,;2)$
- c) Une infinité de solutions : les couples $\left(x\,;\dfrac{7-3x}2\right)$, $x\in\mathbb R$
- d) Une infinité de solutions : les couples $\left(x\,;\dfrac{7-2x}3\right)$, $x\in\mathbb R$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule le déterminant $D=3\times4-6\times2$ ; s'il est nul, on compare les deux équations.

### Corrigé

$D=12-12=0$ ; la seconde équation est le double de la première : le système est équivalent à $3x+2y=7$. Il admet **une infinité de solutions** : les couples $\left(x\,;\dfrac{7-3x}2\right)$, $x\in\mathbb R$.

### Pourquoi les autres réponses sont fausses

- **a)** $D=0$ ne signifie pas forcément « aucune solution » : ici les deux équations sont équivalentes.
- **b)** $(1\,;2)$ est bien une solution, mais ce n'est pas la seule.
- **d)** On a isolé $y$ en échangeant les coefficients : $3x+2y=7$ donne $y=\dfrac{7-3x}2$.

</details>

Avis : 

---

## 56. `cqc-systemes-d-equations-lineaires-prob-a-moyenne-4` (séries A)

**Remarque du relecteur :** LIMITE : système paramétré et déterminant en série A, plutôt niveau C/E.

**Énoncé :**

Pour quelles valeurs du réel $m$ le système $\begin{cases}x+my=1\\mx+y=2\end{cases}$ n'admet-il pas de solution unique ?

- a) $m=1$ seulement
- b) $m=0$
- c) $m\ne-1$ et $m\ne1$
- d) $m=-1$ ou $m=1$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Le système admet une solution unique si et seulement si $D=1\times1-m\times m\ne0$.

### Corrigé

$D=1-m^2=(1-m)(1+m)=0\iff m=1$ ou $m=-1$. Pour ces valeurs, il n'y a pas de solution unique (ici : aucune solution ; par exemple pour $m=1$ on aurait $x+y=1$ et $x+y=2$).

### Pourquoi les autres réponses sont fausses

- **a)** La solution $m=-1$ de $m^2=1$ a été oubliée.
- **b)** Pour $m=0$, $D=1\ne0$ : le système a la solution unique $(1\,;2)$.
- **c)** Ce sont au contraire les valeurs pour lesquelles la solution est unique.

</details>

Avis : 

---

## 57. `cqc-serie-groupee-en-classes-prob-a-moyenne-2` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Les notes de $30$ élèves vont de $12$ à $48$. On veut les regrouper en $6$ classes de même amplitude, de la note minimale à la note maximale. Quelle amplitude faut-il choisir ?

- a) $8$
- b) $2$
- c) $6$
- d) $7{,}2$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Étendue $=$ maximum $-$ minimum ; amplitude $=\dfrac{\text{étendue}}{\text{nombre de classes}}$.

### Corrigé

Étendue : $48-12=36$. Amplitude $\dfrac{36}{6}=6$ : classes $[12\,;18[$, $[18\,;24[$, $[24\,;30[$, $[30\,;36[$, $[36\,;42[$, $[42\,;48]$ (la dernière fermée pour contenir la valeur $48$).

### Pourquoi les autres réponses sont fausses

- **a)** On a divisé la note maximale par $6$ au lieu de l'étendue.
- **b)** On a divisé la note minimale par $6$.
- **d)** On a divisé l'étendue par $5$ au lieu du nombre de classes $6$.

</details>

Avis : 

---

## 58. `cqc-serie-groupee-en-classes-prob-a-moyenne-5` (séries A)

**Remarque du relecteur :** VOCABULAIRE : si les notes sont sur 40, la dernière classe devrait être [30;40] (fermée) pour inclure la note 40, comme dans la question 2.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Les notes de $40$ élèves sont réparties en classes : $[0\,;10[$ : $4$ élèves ; $[10\,;20[$ : $10$ ; $[20\,;30[$ : $16$ ; $[30\,;40]$ : $10$. Quel pourcentage d'élèves a une note strictement inférieure à $20$, et quel pourcentage a une note supérieure ou égale à $30$ ?

- a) $75\ \%$ et $25\ \%$
- b) $35\ \%$ et $25\ \%$
- c) $35\ \%$ et $65\ \%$
- d) $10\ \%$ et $25\ \%$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule les fréquences en pourcentage ($\dfrac{n_i}{40}\times100$), puis on additionne celles des classes concernées.

### Corrigé

Fréquences : $10\ \%$ ; $25\ \%$ ; $40\ \%$ ; $25\ \%$. Notes $<20$ : classes $[0\,;10[$ et $[10\,;20[$ : $10+25=35\ \%$. Notes $\ge30$ : classe $[30\,;40]$ : $25\ \%$.

### Pourquoi les autres réponses sont fausses

- **a)** La classe $[20\,;30[$ a été comptée parmi les notes inférieures à $20$.
- **c)** La classe $[20\,;30[$ a été comptée parmi les notes supérieures ou égales à $30$.
- **d)** Seule la première classe a été comptée pour les notes inférieures à $20$.

</details>

Avis : 

---

## 59. `cqc-tableau-de-variation-prob-c-faible-0` (séries A/C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=x^2-4x+1$. Quel énoncé décrit correctement ses variations ?

- a) Croissante sur $]-\infty\,;2]$, décroissante sur $[2\,;+\infty[$, maximum $-3$ en $x=2$
- b) Décroissante sur $]-\infty\,;-2]$, croissante sur $[-2\,;+\infty[$, minimum $13$ en $x=-2$
- c) Décroissante sur $]-\infty\,;2]$, croissante sur $[2\,;+\infty[$, minimum $1$ en $x=2$
- d) Décroissante sur $]-\infty\,;2]$, croissante sur $[2\,;+\infty[$, minimum $-3$ en $x=2$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour dresser un tableau de variation, on calcule la dérivée $f'$, on étudie son signe, puis on en déduit le sens de variation de $f$ et les valeurs aux points où $f'$ change de signe.

### Corrigé

$f'(x)=2x-4=2(x-2)$, négative pour $x<2$ et positive pour $x>2$. $f(2)=4-8+1=-3$. (On le retrouve avec la forme $f(x)=(x-2)^2-3$.)

| $x$ | $-\infty$ | | $2$ | | $+\infty$ |
|---|---|---|---|---|---|
| $f'(x)$ | | $-$ | $0$ | $+$ | |
| $f(x)$ | $+\infty$ | $\searrow$ | $-3$ | $\nearrow$ | $+\infty$ |

$f$ est décroissante sur $]-\infty\,;2]$, croissante sur $[2\,;+\infty[$ et admet un minimum $-3$ en $x=2$.

### Pourquoi les autres réponses sont fausses

- **a)** Le signe de $f'$ a été inversé : le coefficient de $x^2$ est positif, la courbe est tournée vers le haut.
- **b)** Erreur de signe sur la valeur qui annule $f'$ : $2x-4=0$ donne $x=2$, pas $-2$.
- **d)** $1=f(0)$ est l'ordonnée à l'origine, pas la valeur du minimum $f(2)$.

</details>

Avis : 

---

## 60. `cqc-tableau-de-variation-prob-c-moyenne-2` (séries A/C/D/E)

**Remarque du relecteur :** LIMITE : pour la série A, l'étude d'un polynôme de degré 3 par la dérivée est à la limite haute du programme.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}$ par $f(x)=x^3-3x^2+2$. Quels sont ses extremums locaux ?

- a) Maximum local $2$ en $x=0$ et minimum local $-2$ en $x=2$
- b) Maximum local $-2$ en $x=2$ et minimum local $2$ en $x=0$
- c) Maximum local $2$ en $x=0$ et minimum local $4$ en $x=2$
- d) Aucun extremum local : $2$ et $-2$ sont le maximum et le minimum de $f$ sur $\mathbb R$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On factorise $f'$ pour étudier son signe. Les limites en $\pm\infty$ d'un polynôme sont celles de son terme de plus haut degré. On calcule les valeurs de $f$ aux points où $f'$ s'annule en changeant de signe pour obtenir les extremums locaux.

### Corrigé

$f'(x)=3x^2-6x=3x(x-2)$, positif pour $x<0$ ou $x>2$, négatif pour $0<x<2$.
Valeurs : $f(0)=2$ et $f(2)=8-12+2=-2$. Limites : $\lim\limits_{x\to-\infty}f(x)=-\infty$ et $\lim\limits_{x\to+\infty}f(x)=+\infty$.

| $x$ | $-\infty$ | | $0$ | | $2$ | | $+\infty$ |
|---|---|---|---|---|---|---|---|
| $f'(x)$ | | $+$ | $0$ | $-$ | $0$ | $+$ | |
| $f(x)$ | $-\infty$ | $\nearrow$ | $2$ | $\searrow$ | $-2$ | $\nearrow$ | $+\infty$ |

Maximum local $f(0)=2$ et minimum local $f(2)=-2$.

### Pourquoi les autres réponses sont fausses

- **b)** Maximum et minimum ont été échangés : $f$ croît avant $0$ et décroît après, donc $0$ donne un maximum.
- **c)** Calcul faux de $f(2)$ : $3\times2^2=12$, pas $3\times2=6$.
- **d)** Les extremums ne sont pas absolus : $f$ tend vers $-\infty$ et vers $+\infty$ aux bornes.

</details>

Avis : 

---

## 61. `cqc-tableau-de-variation-prob-c-moyenne-3` (séries A/C/D/E)

**Remarque du relecteur :** LIMITE : limites aux bornes et étude d'une fonction homographique, à la limite haute pour la série A (programme allégé).

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $\mathbb{R}\setminus\{-3\}$ par $f(x)=\dfrac{2x-1}{x+3}$. Quelle affirmation décrit correctement les variations de $f$ et ses limites aux bornes de son ensemble de définition ?

- a) $f$ est strictement décroissante sur $]-\infty\,;-3[$ et sur $]-3\,;+\infty[$ ; $\lim\limits_{x\to\pm\infty}f(x)=2$, $\lim\limits_{x\to-3^-}f(x)=-\infty$ et $\lim\limits_{x\to-3^+}f(x)=+\infty$
- b) $f$ est strictement croissante sur $]-\infty\,;-3[$ et sur $]-3\,;+\infty[$ ; $\lim\limits_{x\to\pm\infty}f(x)=2$, $\lim\limits_{x\to-3^-}f(x)=+\infty$ et $\lim\limits_{x\to-3^+}f(x)=-\infty$
- c) $f$ est strictement croissante sur $]-\infty\,;-3[$ et sur $]-3\,;+\infty[$ ; $\lim\limits_{x\to\pm\infty}f(x)=2$, $\lim\limits_{x\to-3^-}f(x)=-\infty$ et $\lim\limits_{x\to-3^+}f(x)=+\infty$
- d) $f$ est strictement croissante sur $]-\infty\,;-3[$ et sur $]-3\,;+\infty[$ ; $\lim\limits_{x\to\pm\infty}f(x)=-\dfrac13$, $\lim\limits_{x\to-3^-}f(x)=+\infty$ et $\lim\limits_{x\to-3^+}f(x)=-\infty$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour un quotient, on calcule $f'$ avec $\left(\dfrac uv\right)'=\dfrac{u'v-uv'}{v^2}$ ; le dénominateur $v^2$ étant positif, le signe de $f'$ est celui du numérateur. Les limites en $\pm\infty$ sont le rapport des coefficients dominants ; en la valeur interdite, on étudie le signe de chaque côté.

### Corrigé

$f'(x)=\dfrac{2(x+3)-(2x-1)\times1}{(x+3)^2}=\dfrac{7}{(x+3)^2}>0$ : $f$ est strictement croissante sur $]-\infty\,;-3[$ et sur $]-3\,;+\infty[$.

Limites : $\lim\limits_{x\to\pm\infty}f(x)=2$ (rapport des coefficients de $x$). En $-3$ : le numérateur $2x-1$ tend vers $-7<0$ ; le dénominateur $x+3$ tend vers $0$ par valeurs négatives à gauche et positives à droite. Donc $\lim\limits_{x\to-3^-}f(x)=+\infty$ et $\lim\limits_{x\to-3^+}f(x)=-\infty$.

| $x$ | $-\infty$ | | $-3$ | | $+\infty$ |
|---|---|---|---|---|---|
| $f'(x)$ | | $+$ | interdite | $+$ | |
| $f(x)$ | $2$ | $\nearrow$ | $+\infty$ (à gauche) ; $-\infty$ (à droite) | $\nearrow$ | $2$ |

### Pourquoi les autres réponses sont fausses

- **a)** Le numérateur de $f'$ a été écrit $uv'-u'v$ au lieu de $u'v-uv'$ : on obtient $-7$, d'où un sens de variation et des limites en $-3$ inversés.
- **c)** Le signe du numérateur en $-3$ ($-7<0$) a été oublié : les limites à gauche et à droite de $-3$ sont échangées.
- **d)** Les limites en $\pm\infty$ ont été prises comme le rapport des termes constants $\dfrac{-1}{3}$ au lieu du rapport des coefficients de $x$.

</details>

Avis : 

---

## 62. `cqc-tableau-de-variation-prob-c-moyenne-4` (séries A/C/D/E)

**Remarque du relecteur :** LIMITE : pour la série A, la dérivée de √x et l'étude de variations correspondante sont à la limite haute du programme.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $f$ la fonction définie sur $[0\,;+\infty[$ par $f(x)=x-2\sqrt x$. Quel est le minimum de $f$ sur $[0\,;+\infty[$, et en quelle valeur de $x$ est-il atteint ?

- a) $-\dfrac34$, atteint en $x=\dfrac14$
- b) $0$, atteint en $x=0$
- c) $-1$, atteint en $x=1$
- d) $f$ n'admet pas de minimum, car $\lim\limits_{x\to+\infty}f(x)=-\infty$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour $x\geqslant0$, on a $x=\left(\sqrt x\right)^2$. On peut donc écrire $f(x)$ sous la forme d'un carré plus une constante (comme pour la forme canonique d'un trinôme) : un carré est toujours positif ou nul, et il s'annule seulement quand ce qui est au carré est nul.

### Corrigé

Pour $x\geqslant0$ : $f(x)=\left(\sqrt x\right)^2-2\sqrt x=\left(\sqrt x-1\right)^2-1$.
Comme $\left(\sqrt x-1\right)^2\geqslant0$, on a $f(x)\geqslant-1$, avec égalité seulement si $\sqrt x=1$, c'est-à-dire $x=1$. Le minimum de $f$ est donc $f(1)=1-2=-1$, atteint en $x=1$.

Valeurs : $f(0)=0$, $f(1)=-1$, et $f(x)=x\left(1-\dfrac2{\sqrt x}\right)\to+\infty$ quand $x\to+\infty$. $f$ est décroissante sur $[0\,;1]$ (de $0$ à $-1$) et croissante sur $[1\,;+\infty[$ (de $-1$ à $+\infty$).

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de calcul de la dérivée : $f'(x)=1-\dfrac1{2\sqrt x}$ au lieu de $1-\dfrac1{\sqrt x}$ (oubli du facteur $2$ devant $\sqrt x$), qui s'annule en $x=\dfrac14$ ; or $f\left(\dfrac14\right)=-\dfrac34>-1$.
- **b)** $f(0)=0$ est la valeur à la borne, mais $f$ prend des valeurs plus petites ($f(1)=-1<0$) : $f$ commence par décroître.
- **d)** Erreur de limite : quand $x$ devient grand, $x$ l'emporte sur $2\sqrt x$, car $f(x)=x\left(1-\dfrac2{\sqrt x}\right)$ et $1-\dfrac2{\sqrt x}\to1$ ; donc $f(x)\to+\infty$, et $f$ admet bien un minimum.

</details>

Avis : 

---

## 63. `cqc-transformation-de-courbe-prob-a-faible-0` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $f$ une fonction définie sur $\mathbb{R}$ et $\mathcal C$ sa courbe représentative dans un repère orthogonal. Comment obtient-on la courbe de la fonction $g$ définie par $g(x)=f(-x)$ à partir de $\mathcal C$ ?

- a) Par la symétrie par rapport à l'axe des abscisses
- b) En gardant les parties de $\mathcal C$ situées au-dessus de l'axe des abscisses et en prenant le symétrique des parties situées en dessous
- c) Par la symétrie par rapport à l'origine $O$ du repère
- d) Par la symétrie par rapport à l'axe des ordonnées

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Ce sont des symétries de la courbe de $f$ (ou une transformation apparentée) : il faut repérer si c'est l'abscisse ou l'ordonnée qui change de signe.

### Corrigé

Pour $g(x)=f(-x)$, le point $M(x\,;f(x))$ de $\mathcal C$ correspond au point $M'(-x\,;f(x))$ de la courbe de $g$ : l'ordonnée est conservée et l'abscisse change de signe. La courbe de $g$ est donc la symétrique de $\mathcal C$ par rapport à l'axe des **ordonnées**.

À retenir aussi : la courbe de $-f$ est la symétrique de $\mathcal C$ par rapport à l'axe des **abscisses** ; la courbe de $|f|$ s'obtient en gardant les parties de $\mathcal C$ situées au-dessus de l'axe des abscisses et en prenant le symétrique des parties situées en dessous.

### Pourquoi les autres réponses sont fausses

- **a)** C'est la construction de la courbe de $-f$ (l'ordonnée change de signe), pas celle de $x\mapsto f(-x)$.
- **b)** C'est la construction de la courbe de $|f|$.
- **c)** La symétrie par rapport à l'origine donne la courbe de $x\mapsto-f(-x)$ : les deux coordonnées changent de signe.

</details>

Avis : 

---

## 64. `cqc-transformation-de-courbe-prob-a-moyenne-2` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $f(x)=x^2-2x$. Quelles sont les coordonnées du sommet de la courbe de la fonction $-f$, et de quelle nature est l'extremum de $-f$ ?

- a) $S'(1\,;1)$ ; c'est un maximum
- b) $S'(1\,;-1)$ ; c'est un minimum
- c) $S'(-1\,;1)$ ; c'est un maximum
- d) $S'(1\,;1)$ ; c'est un minimum

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Sommet de la courbe de $f$ : $x=1$, $f(1)=-1$. La courbe de $-f$ est la symétrique de celle de $f$ par rapport à l'axe des abscisses : son sommet est le symétrique de celui de $f$, et un minimum devient un maximum.

### Corrigé

$-f(x)=-x^2+2x$. Le sommet de la courbe de $f$ est $S(1\,;-1)$ (minimum) ; celui de la courbe de $-f$ est $S'(1\,;1)$ : c'est un **maximum**.

### Pourquoi les autres réponses sont fausses

- **b)** C'est le sommet de la courbe de $f$, pas de $-f$ : on a oublié de changer le signe de l'ordonnée.
- **c)** L'abscisse a été changée de signe au lieu de l'ordonnée (confusion avec la symétrie par rapport à l'axe des ordonnées) : $-f(-1)=-3\neq1$.
- **d)** Le sommet est juste, mais le changement de signe transforme un minimum en maximum : $-x^2+2x$ a un coefficient de $x^2$ négatif.

</details>

Avis : 

---

## 65. `cqc-transformation-de-courbe-prob-a-moyenne-3` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $f(x)=x+2$ et $g$ la fonction définie par $g(x)=f(-x)$. Quelle affirmation est exacte ?

- a) $g(x)=-x-2$ ; les deux droites sont symétriques par rapport à l'axe des abscisses
- b) $g(x)=x-2$ ; les deux droites sont symétriques par rapport à l'axe des ordonnées
- c) $g(x)=-x+2$ ; les deux droites se coupent en $(0\,;2)$ et sont symétriques par rapport à l'axe des ordonnées
- d) $g(x)=-x+2$ ; les deux droites se coupent en $(2\,;0)$ et sont symétriques par rapport à l'axe des abscisses

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On remplace $x$ par $-x$ dans l'expression de $f$ ; la courbe de $x\mapsto f(-x)$ est la symétrique de celle de $f$ par rapport à l'axe des ordonnées.

### Corrigé

$g(x)=-x+2$. Les droites $y=x+2$ et $y=-x+2$ se coupent au point $(0\,;2)$ (même ordonnée à l'origine) et sont symétriques par rapport à l'axe des ordonnées.

### Pourquoi les autres réponses sont fausses

- **a)** $-x-2$ est l'expression de $-f(x)$, pas de $f(-x)$ : on a changé le signe de toute l'expression.
- **b)** Le signe a été appliqué à la constante au lieu de $x$ ; de plus deux droites de même coefficient directeur sont parallèles, pas symétriques.
- **d)** L'expression est juste, mais les deux droites se coupent en $(0\,;2)$ (pour $x=0$, les deux valent $2$) et la symétrie est par rapport à l'axe des ordonnées.

</details>

Avis : 

---

## 66. `cqc-transformation-de-courbe-prob-a-moyenne-4` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $f(x)=x^2$. On définit $g(x)=f(2x)$ et $h(x)=2f(x)$. Quelles sont les expressions de $g(x)$ et de $h(x)$ ?

- a) $g(x)=2x^2$ et $h(x)=2x^2$
- b) $g(x)=4x^2$ et $h(x)=2x^2$
- c) $g(x)=2x^2$ et $h(x)=4x^2$
- d) $g(x)=4x^2$ et $h(x)=4x^2$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour $g$, on remplace $x$ par $2x$ dans $f$ : $g(x)=(2x)^2$. Pour $h$, on multiplie la valeur $f(x)$ par $2$ : $h(x)=2x^2$.

### Corrigé

$g(x)=(2x)^2=4x^2$ et $h(x)=2x^2$. En $x=1$ : $f(1)=1$, $g(1)=4$, $h(1)=2$. Les deux fonctions sont donc différentes : la courbe de $h$ s'obtient en multipliant par $2$ les ordonnées des points de la courbe de $f$, celle de $g$ en divisant leurs abscisses par $2$.

### Pourquoi les autres réponses sont fausses

- **a)** Le carré n'a pas été appliqué au facteur $2$ : $(2x)^2=4x^2$ et non $2x^2$.
- **c)** Les deux expressions sont échangées.
- **d)** Le facteur $2$ de $h$ a été mis au carré : $2f(x)=2x^2$, seul $x$ est au carré.

</details>

Avis : 

---

## 67. `cqc-transformation-de-courbe-prob-a-moyenne-5` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $f(x)=x^2-1$. Que peut-on dire des valeurs de $x$ qui annulent $f$ et de celles qui annulent la fonction $2f$ ?

- a) $f$ s'annule en $-1$ et $1$, et $2f$ s'annule en $-2$ et $2$
- b) $f$ s'annule en $-1$ et $1$, et $2f$ s'annule en $-\dfrac12$ et $\dfrac12$
- c) $f$ et $2f$ s'annulent seulement en $1$
- d) $f$ et $2f$ s'annulent pour les mêmes valeurs : $-1$ et $1$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Multiplier une fonction par $2$ ne change pas les valeurs qui l'annulent : $2f(x)=0\iff f(x)=0$.

### Corrigé

$f(x)=0\iff x^2=1\iff x=-1$ ou $x=1$ ; $2f(x)=2x^2-2=0\iff x=\pm1$. Les zéros sont identiques ; seule change l'échelle verticale (les ordonnées sont multipliées par $2$).

### Pourquoi les autres réponses sont fausses

- **a)** On a multiplié les zéros par $2$ : c'est la valeur de la fonction qui est doublée, pas $x$.
- **b)** On a divisé les zéros par $2$ (confusion avec $x\mapsto f(2x)$, dont les zéros sont bien $\pm\dfrac12$).
- **c)** La solution négative de $x^2=1$ a été oubliée.

</details>

Avis : 

---

## 68. `cqc-translation-de-courbe-prob-a-faible-0` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $f$ une fonction, $a$ et $b$ deux réels strictement positifs, et $g$ la fonction définie par $g(x)=f(x-a)+b$. Comment obtient-on la courbe de $g$ à partir de celle de $f$ ?

- a) En la déplaçant de $a$ unités vers la droite et de $b$ unités vers le haut
- b) En la déplaçant de $a$ unités vers la gauche et de $b$ unités vers le haut
- c) En la déplaçant de $b$ unités vers la droite et de $a$ unités vers le haut
- d) En la déplaçant de $a$ unités vers la droite et de $b$ unités vers le bas

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On décale la courbe horizontalement de $a$ et verticalement de $b$ : remplacer $x$ par $x-a$ agit sur les abscisses, ajouter $b$ agit sur les ordonnées.

### Corrigé

Si $M(x\,;y)$ est un point de la courbe de $f$, alors $M'(x+a\,;y+b)$ est un point de la courbe de $g$, car $g(x+a)=f(x)+b=y+b$. La courbe de $g$ s'obtient donc en déplaçant celle de $f$ de $a$ unités **vers la droite** et de $b$ unités **vers le haut**.

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de signe classique : le « $-a$ » dans $f(x-a)$ fait déplacer la courbe vers la droite, pas vers la gauche.
- **c)** Le rôle de $a$ et de $b$ est inversé : $a$ agit sur les abscisses, $b$ sur les ordonnées.
- **d)** Ajouter $b>0$ à toutes les ordonnées fait monter la courbe, pas descendre.

</details>

Avis : 

---

## 69. `cqc-translation-de-courbe-prob-a-moyenne-2` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Soit $f(x)=x^2$ et $g(x)=x^2-4x+3$. Comment obtient-on la courbe de $g$ à partir de celle de $f$ ?

- a) En la déplaçant de $2$ unités vers la gauche et de $1$ unité vers le bas
- b) En la déplaçant de $2$ unités vers la droite et de $3$ unités vers le haut
- c) En la déplaçant de $2$ unités vers la droite et de $1$ unité vers le bas
- d) En la déplaçant de $2$ unités vers la droite et de $1$ unité vers le haut

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

On met $g(x)$ sous forme canonique : $x^2-4x+3=(x-2)^2-1$, puis on reconnaît $g(x)=f(x-a)+b$ : la courbe de $f$ est déplacée de $a$ horizontalement et de $b$ verticalement.

### Corrigé

$g(x)=(x-2)^2-1=f(x-2)-1$ : on déplace la courbe de $f$ de $2$ unités vers la droite et de $1$ unité vers le bas. Le sommet passe de $O(0\,;0)$ à $S(2\,;-1)$.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de signe : $(x-2)^2$ correspond à un déplacement vers la droite, pas vers la gauche.
- **b)** Le terme constant $3$ de $g(x)$ a été lu directement, sans passer par la forme canonique : $(x-2)^2=x^2-4x+4$, donc $g(x)=(x-2)^2-1$.
- **d)** Le signe de la constante $-1$ de la forme canonique a été inversé.

</details>

Avis : 

---

## 70. `cqc-ecart-type-prob-c-faible-0` (séries A/C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Quel est l'écart-type de la série statistique $2\,;4\,;4\,;4\,;5\,;5\,;7\,;9$ ? (Résultat arrondi au centième si nécessaire.)

- a) $4$
- b) $2$
- c) $1{,}5$
- d) $2{,}14$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Moyenne : $\bar x=\dfrac1N\sum x_i$. Variance : $V=\dfrac1N\sum(x_i-\bar x)^2$ (moyenne des carrés des écarts à la moyenne). Écart-type : $\sigma=\sqrt V$.

### Corrigé

Effectif $N=8$, somme $=40$, donc $\bar x=5$. Les écarts à la moyenne sont $-3\,;-1\,;-1\,;-1\,;0\,;0\,;2\,;4$ et leurs carrés $9\,;1\,;1\,;1\,;0\,;0\,;4\,;16$, de somme $32$.
$$V=\dfrac{32}8=4,\qquad\sigma=\sqrt4=2.$$
La valeur est exacte, aucun arrondi au centième n'est nécessaire.

### Pourquoi les autres réponses sont fausses

- **a)** $4$ est la variance : on a oublié de prendre la racine carrée.
- **c)** $1{,}5$ est la moyenne des écarts sans les carrés (moyenne des distances à la moyenne $\dfrac{12}8$), ce n'est pas l'écart-type.
- **d)** On a divisé la somme des carrés par $N-1=7$ au lieu de $N=8$ : $\sqrt{\dfrac{32}7}\approx2{,}14$.

</details>

Avis : 

---

## 71. `cqc-ecart-type-prob-c-moyenne-2` (séries A/C/D/E)

**Remarque du relecteur :** Le distracteur c donne la variance à la place de l'écart-type : bon piège ; la mention « arrondis au centième » est sans objet (1,4 exact), sans gêne.

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Une série a pour valeurs $10$, $12$ et $14$ avec les effectifs respectifs $2$, $5$ et $3$. Quels sont sa moyenne $\bar x$ et son écart-type $\sigma$ ? (Résultats arrondis au centième si nécessaire.)

- a) $\bar x=12{,}2$ et $\sigma=1{,}4$
- b) $\bar x=12$ et $\sigma\approx1{,}63$
- c) $\bar x=12{,}2$ et $\sigma=1{,}96$
- d) $\bar x=12{,}2$ et $\sigma\approx1{,}48$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

Avec des effectifs $n_i$ : $\bar x=\dfrac{\sum n_ix_i}{N}$ et $V=\dfrac{\sum n_ix_i^2}N-\bar x^2$ (la variance est la moyenne des carrés moins le carré de la moyenne). Écart-type : $\sigma=\sqrt V$.

### Corrigé

$N=10$. $\bar x=\dfrac{2\times10+5\times12+3\times14}{10}=\dfrac{122}{10}=12{,}2$.
$\dfrac{\sum n_ix_i^2}N=\dfrac{2\times100+5\times144+3\times196}{10}=\dfrac{1508}{10}=150{,}8$, donc
$$V=150{,}8-12{,}2^2=150{,}8-148{,}84=1{,}96,\qquad\sigma=\sqrt{1{,}96}=1{,}4.$$
Les valeurs sont exactes, aucun arrondi au centième n'est nécessaire.

### Pourquoi les autres réponses sont fausses

- **b)** Les effectifs ont été ignorés : on a traité la série $10\,;12\,;14$, de moyenne $12$ et d'écart-type $\sqrt{\dfrac83}\approx1{,}63$.
- **c)** $1{,}96$ est la variance : on a oublié la racine carrée.
- **d)** La somme $\sum n_i(x_i-\bar x)^2=19{,}6$ a été divisée par $N-1=9$ au lieu de $N=10$ : $\sqrt{\dfrac{19{,}6}9}\approx1{,}48$.

</details>

Avis : 

---

## 72. `cqc-ecart-type-prob-c-moyenne-3` (séries A/C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Deux séries ont la même moyenne $10$ : $A=(8\,;10\,;12)$ et $B=(4\,;10\,;16)$. Quelle affirmation est exacte ? (Écarts-types arrondis au centième.)

- a) $\sigma_A=\sigma_B$ car les deux séries ont la même moyenne : elles sont aussi dispersées l'une que l'autre
- b) $\sigma_A\approx1{,}63$ et $\sigma_B\approx4{,}90$ : la série $A$ est la plus dispersée
- c) $\sigma_A=2$ et $\sigma_B=6$ : la série $B$ est la plus dispersée
- d) $\sigma_A\approx1{,}63$ et $\sigma_B\approx4{,}90$ : la série $B$ est la plus dispersée

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

L'écart-type est $\sigma=\sqrt V$ avec $V=\dfrac1N\sum(x_i-\bar x)^2$. À moyenne égale, la série dont l'écart-type est le plus grand est la plus dispersée : ses valeurs s'éloignent davantage de la moyenne.

### Corrigé

Série $A$ : écarts $-2\,;0\,;2$, carrés $4\,;0\,;4$, donc $V_A=\dfrac83$ et $\sigma_A=\sqrt{\dfrac83}\approx1{,}63$ (arrondi au centième).
Série $B$ : écarts $-6\,;0\,;6$, carrés $36\,;0\,;36$, donc $V_B=24$ et $\sigma_B=\sqrt{24}\approx4{,}90$ (arrondi au centième).

$\sigma_B>\sigma_A$ : la série $B$ est beaucoup plus dispersée autour de la moyenne que la série $A$.

### Pourquoi les autres réponses sont fausses

- **a)** Une même moyenne ne dit rien de la dispersion : les valeurs de $B$ sont bien plus éloignées de $10$.
- **b)** Les écarts-types sont justes, mais l'interprétation est inversée : le plus grand écart-type correspond à la série la plus dispersée.
- **c)** On a divisé la somme des carrés par $N-1=2$ au lieu de $N=3$ : $\sqrt{\dfrac82}=2$ et $\sqrt{\dfrac{72}2}=6$.

</details>

Avis : 

---

## 73. `cqc-ecart-type-prob-c-moyenne-4` (séries A/C/D/E)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Une série $X$ a pour moyenne $12$ et pour écart-type $3$. On pose $Y=2X+5$ (chaque valeur est doublée puis augmentée de $5$). Quels sont la moyenne et l'écart-type de $Y$ ?

- a) Moyenne $29$ et écart-type $11$
- b) Moyenne $29$ et écart-type $12$
- c) Moyenne $29$ et écart-type $3$
- d) Moyenne $29$ et écart-type $6$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

Pour $Y=aX+b$ : $\bar y=a\bar x+b$ et $\sigma_Y=|a|\,\sigma_X$ (ajouter une constante ne change pas la dispersion ; multiplier par $a$ multiplie l'écart-type par $|a|$).

### Corrigé

$\bar y=2\times12+5=29$ et $\sigma_Y=2\times3=6$ (la variance est multipliée par $a^2=4$, de $9$ à $36$).

### Pourquoi les autres réponses sont fausses

- **a)** On a appliqué la transformation entière à l'écart-type ($2\times3+5$) : ajouter $5$ à toutes les valeurs ne change pas leur dispersion.
- **b)** On a multiplié l'écart-type par $a^2=4$ ; c'est la variance qui est multipliée par $a^2$, l'écart-type est multiplié par $|a|=2$.
- **c)** On a cru que l'écart-type ne change pas ; seule l'addition de $5$ le laisse inchangé, pas la multiplication par $2$.

</details>

Avis : 

---

## 74. `cqc-equation-cartesienne-prob-a-faible-0` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Une droite $(d)$ a pour équation cartésienne $ax+by+c=0$, avec $b\neq0$. Quel est le coefficient directeur de $(d)$ ?

- a) $\dfrac ab$
- b) $-\dfrac ab$
- c) $-\dfrac ba$
- d) $a$

**Clé :** b

<details><summary>Corrigé</summary>

### Rappel de méthode

Une droite du plan a une équation de la forme $ax+by+c=0$ avec $(a\,;b)\neq(0\,;0)$. Si $b\neq0$, on isole $y$ pour obtenir l'équation réduite $y=mx+p$ : $m$ est le coefficient directeur.

### Corrigé

$ax+by+c=0$ est une équation cartésienne de la droite (elle n'est pas unique : on peut multiplier par un réel non nul). Si $b\neq0$ : $by=-ax-c$, donc $y=-\dfrac abx-\dfrac cb$. Le coefficient directeur est $m=-\dfrac ab$.

### Pourquoi les autres réponses sont fausses

- **a)** Le signe a été oublié en faisant passer $ax$ de l'autre côté de l'égalité.
- **c)** On a divisé par $a$ au lieu de $b$ (on a isolé $x$ au lieu de $y$).
- **d)** On a pris le coefficient de $x$ sans diviser par $b$ : on obtient $-\dfrac ab=a$ seulement dans le cas particulier $b=-1$.

</details>

Avis : 

---

## 75. `cqc-equation-cartesienne-prob-a-moyenne-2` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Dans un repère, on donne $A(1\,;2)$ et $B(3\,;6)$. Laquelle des équations suivantes est une équation cartésienne de la droite $(AB)$ ?

- a) $x-2y+3=0$
- b) $2x-y+2=0$
- c) $2x+y-4=0$
- d) $2x-y=0$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

On calcule le coefficient directeur $m=\dfrac{y_B-y_A}{x_B-x_A}$, puis l'ordonnée à l'origine $p$ en écrivant que $A$ est sur la droite d'équation $y=mx+p$. On vérifie enfin que les deux points satisfont l'équation trouvée.

### Corrigé

$m=\dfrac{6-2}{3-1}=2$ ; $y=2x+p$ avec $2=2\times1+p\Rightarrow p=0$ : $y=2x$, soit $2x-y=0$.
Vérification : $2\times1-2=0$ et $2\times3-6=0$.

### Pourquoi les autres réponses sont fausses

- **a)** Le coefficient directeur a été calculé à l'envers, $\dfrac{x_B-x_A}{y_B-y_A}=\dfrac12$ : la droite passe par $A$ mais pas par $B$ ($3-12+3=-6\neq0$).
- **b)** L'ordonnée à l'origine a été prise égale à l'ordonnée de $A$ ($y=2x+2$) : la droite ne passe ni par $A$ ni par $B$.
- **c)** Erreur de signe sur le coefficient directeur ($m=-2$) : la droite passe par $A$ mais pas par $B$ ($6+6-4=8\neq0$).

</details>

Avis : 

---

## 76. `cqc-equation-cartesienne-prob-a-moyenne-3` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Quelle est l'équation réduite de la droite $(d)$ d'équation cartésienne $3x+2y-6=0$ ?

- a) $y=-\dfrac32x+3$
- b) $y=\dfrac32x-3$
- c) $y=-3x+6$
- d) $y=-\dfrac23x+2$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

On isole $y$ : on fait passer les termes en $x$ et les constantes de l'autre côté, puis on divise par le coefficient de $y$. On peut contrôler avec les points d'intersection avec les axes (axe des abscisses : $y=0$ ; axe des ordonnées : $x=0$).

### Corrigé

$2y=-3x+6$, donc $y=-\dfrac32x+3$.
Contrôle : avec $y=0$ on trouve $x=2$, point $(2\,;0)$ ; avec $x=0$ on trouve $y=3$, point $(0\,;3)$ ; ces deux points vérifient bien $y=-\dfrac32x+3$.

### Pourquoi les autres réponses sont fausses

- **b)** Erreur de signe en faisant passer $3x$ et $-6$ de l'autre côté de l'égalité.
- **c)** On a oublié de diviser par le coefficient $2$ de $y$.
- **d)** On a divisé par $3$ (coefficient de $x$) au lieu de $2$, en isolant $x$ puis en échangeant les rôles.

</details>

Avis : 

---

## 77. `cqc-equation-cartesienne-prob-a-moyenne-5` (séries A)

**Modification de fond lors de la conversion** (question réduite, méthode remplacée ou vocabulaire adapté à la série A) : à examiner de près.

**Énoncé :**

Quelle est une équation cartésienne de la droite parallèle à la droite d'équation $2x+3y-1=0$ et passant par le point $A(1\,;1)$ ?

- a) $3x-2y-1=0$
- b) $2x+3y-1=0$
- c) $2x+3y-5=0$
- d) $2x+3y+5=0$

**Clé :** c

<details><summary>Corrigé</summary>

### Rappel de méthode

Deux droites parallèles ont le même coefficient directeur : leurs équations peuvent s'écrire avec les mêmes coefficients de $x$ et de $y$, sous la forme $2x+3y+c=0$. On détermine $c$ en écrivant que $A$ est sur la droite.

### Corrigé

$2\times1+3\times1+c=0\Rightarrow c=-5$ : la droite parallèle a pour équation $2x+3y-5=0$.

### Pourquoi les autres réponses sont fausses

- **a)** Les coefficients $a$ et $b$ ont été échangés (avec un changement de signe) : cette droite passe par $A$ mais n'est pas parallèle à la droite donnée (son coefficient directeur est $\dfrac32$ au lieu de $-\dfrac23$).
- **b)** C'est l'équation de la droite de départ : elle ne passe pas par $A$ ($2+3-1=4\neq0$).
- **d)** Erreur de signe sur $c$ : $2+3+5=10\neq0$, la droite ne passe pas par $A$.

</details>

Avis : 

---

## 78. `cqc-equation-de-tangente-prob-a-moyenne-3` (séries A)

**Remarque du relecteur :** LIMITE : tangente à une courbe de fonction cubique (nombre dérivé, dérivée de x^3) en série A, à la limite haute du programme léger de A.

**Énoncé :**

Quelle est l'équation de la tangente à la courbe de la fonction $f(x)=x^3-2x$ au point d'abscisse $1$ ?

- a) $y=3x-4$
- b) $y=x-1$
- c) $y=x$
- d) $y=x-2$

**Clé :** d

<details><summary>Corrigé</summary>

### Rappel de méthode

La tangente au point d'abscisse $a$ a pour équation $y=f'(a)(x-a)+f(a)$. Ici $f'(x)=3x^2-2$.

### Corrigé

$f(1)=1-2=-1$ ; $f'(1)=3-2=1$. Tangente : $y=1\times(x-1)+(-1)=x-2$.

### Pourquoi les autres réponses sont fausses

- **a)** Erreur de dérivation : la dérivée de $-2x$ (qui vaut $-2$) a été oubliée, d'où $f'(1)=3$ et $y=3(x-1)-1=3x-4$.
- **b)** On a écrit $y=f'(a)\,x+f(a)$ en oubliant le « $-a$ » : $y=x-1$, droite qui ne passe pas par le point $(1\,;-1)$.
- **c)** On a pris $f(1)=1$ au lieu de $-1$ (erreur de signe) : $y=(x-1)+1=x$.

</details>

Avis : 

---

## 79. `cqc-equation-de-tangente-prob-a-moyenne-4` (séries A)

**Remarque du relecteur :** LIMITE : dérivée de 1/x et équation de tangente en série A, à vérifier contre le programme allégé de Première A.

**Énoncé :**

Quelle est l'équation de la tangente à la courbe de la fonction $f(x)=\dfrac1x$ au point d'abscisse $2$ ?

- a) $y=-\dfrac14x+1$
- b) $y=\dfrac14x$
- c) $y=-\dfrac12x+\dfrac32$
- d) $y=-\dfrac14x+\dfrac12$

**Clé :** a

<details><summary>Corrigé</summary>

### Rappel de méthode

La tangente au point d'abscisse $a$ a pour équation $y=f'(a)(x-a)+f(a)$. Ici $f'(x)=-\dfrac1{x^2}$ pour $x\neq0$.

### Corrigé

$f(2)=\dfrac12$ ; $f'(2)=-\dfrac14$. Tangente : $y=-\dfrac14(x-2)+\dfrac12=-\dfrac14x+1$.

### Pourquoi les autres réponses sont fausses

- **b)** Le signe de la dérivée a été oublié ($f'(x)=\dfrac1{x^2}$) : $y=\dfrac14(x-2)+\dfrac12=\dfrac14x$.
- **c)** Mauvaise dérivée $f'(x)=-\dfrac1x$, d'où $f'(2)=-\dfrac12$ et $y=-\dfrac12(x-2)+\dfrac12=-\dfrac12x+\dfrac32$.
- **d)** Le « $-a$ » a été oublié : $y=-\dfrac14x+\dfrac12$, droite qui ne passe pas par le point $\left(2\,;\dfrac12\right)$.

</details>

Avis : 

---

