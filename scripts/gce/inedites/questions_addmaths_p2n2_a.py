r"""Section A (questions 1 a 8, 66 points, toutes obligatoires) de l'epreuve inedite GCE O Level Additional Mathematics Paper 2 n.2.

Session n.2 : donnees neuves par rapport au Paper 2 n.1 et aux vrais sujets. Le vrai sujet : « Answer ALL questions in SECTION A and ANY TWO questions from
EITHER SECTION B (Mechanics) OR SECTION C (Statistics and Probability) » ; cette inedite garde la Section A en entier et DEUX questions de la Section C
(voir questions_addmaths_p2n2_c.py). Meme forme que questions_addmaths_p2_a.py (S, E, crit, rappel, sol, ans). Chaines BRUTES.
"""
import re

from questions_addmaths_p2_a import E, S  # noqa: F401  (memes constructeurs que le Paper 2 n.1)

# Numerotation AFFICHEE : (exercice, numero de travail) -> (numero unique dans l'exercice, groupe_local).
NUMEROS = {
    ("1", "i-a"): ("a", "(i)"), ("1", "i-b"): ("b", "(i)"), ("1", "ii-a"): ("c", "(ii)"), ("1", "ii-b"): ("d", "(ii)"),
    ("2", "i"): ("i", ""), ("2", "ii"): ("ii", ""),
    ("4", "i-a"): ("a", "(i)"), ("4", "i-b"): ("b", "(i)"), ("4", "ii"): ("ii", ""),
    ("6", "i"): ("i", ""), ("6", "ii-a"): ("a", "(ii)"), ("6", "ii-b"): ("b", "(ii)"),
    ("8", "i"): ("i", ""), ("8", "ii"): ("ii", ""),
    ("10", "i-a"): ("a", "(i)"), ("10", "i-b"): ("b", "(i)"), ("10", "i-c"): ("c", "(i)"), ("10", "i-d"): ("d", "(i)"),
    ("10", "ii-a"): ("e", "(ii)"), ("10", "ii-b"): ("f", "(ii)"), ("10", "ii-c"): ("g", "(ii)"),
}


def numero_affiche(ex, num):
    return NUMEROS.get((ex, num), (num, ""))


def sans_prefixe(texte):
    return re.sub(r"^\((?:i|ii|iii)\)(?:\([a-h]\))?\s+", "", texte)


TABLE_GROUPE = r"""| $*$ | 1 | 2 | 4 | 8 |
|---|---|---|---|---|
| **1** | 1 | 2 | 4 | 8 |
| **2** | 2 | 4 | 8 | |
| **4** | 4 | 8 | | |
| **8** | 8 | 1 | 2 | |"""

TABLE_GROUPE_COMPLETE = r"""| $*$ | 1 | 2 | 4 | 8 |
|---|---|---|---|---|
| **1** | 1 | 2 | 4 | 8 |
| **2** | 2 | 4 | 8 | 1 |
| **4** | 4 | 8 | 1 | 2 |
| **8** | 8 | 1 | 2 | 4 |"""


def section_a():
    G = "SECTION A"
    ex = []

    ex.append(E("1", G, 8, "", [
        S("i-a", r"(i)(a) The polynomial $f(x)=x^{3}+kx^{2}+11x+6$ has $(x+1)$ as a factor. Find the value of the constant $k$.",
          ["remainder and factor theorem"], "faible", 2,
          [(r"You write $f(-1)=0$ and substitute: $-1+k-11+6=0$", 1), (r"You solve to obtain $k=6$", 1)],
          r"If $(x-a)$ is a factor of $f(x)$ then $f(a)=0$; for the factor $(x+1)$, $a=-1$.",
          r"Since $(x+1)$ is a factor, $f(-1)=0$: $(-1)^{3}+k(-1)^{2}+11(-1)+6=-1+k-11+6=k-6=0$, so $k=6$.",
          ans=r"$k=6$"),
        S("i-b", r"(i)(b) With this value of $k$, factorise $f(x)$ completely.", ["factor theorem and factorising cubics"], "faible", 2,
          [(r"You divide by $(x+1)$ to find the quadratic factor $x^{2}+5x+6$ (or equivalent)", 1), (r"You factorise completely: $(x+1)(x+2)(x+3)$", 1)],
          r"Divide the cubic by the known linear factor to obtain a quadratic, then factorise the quadratic.",
          r"$f(x)=x^{3}+6x^{2}+11x+6=(x+1)(x^{2}+5x+6)=(x+1)(x+2)(x+3)$. Check: $f(-2)=-8+24-22+6=0$ and $f(-3)=-27+54-33+6=0$.",
          ans=r"$(x+1)(x+2)(x+3)$"),
        S("ii-a", r"(ii)(a) The roots of the equation $x^{2}-8x+k=0$ are $\alpha$ and $3\alpha$. By considering the sum of the roots, find the value of $\alpha$.",
          ["relations between roots and coefficients"], "faible", 2,
          [(r"You write the sum of the roots: $\alpha+3\alpha=8$", 1), (r"You solve to obtain $\alpha=2$", 1)],
          r"For $x^{2}+bx+c=0$ the sum of the roots is $-b$ and their product is $c$.",
          r"The sum of the roots is $-(-8)=8$, so $\alpha+3\alpha=4\alpha=8$ and $\alpha=2$. The roots are $2$ and $6$.",
          ans=r"$\alpha=2$"),
        S("ii-b", r"(ii)(b) Hence find the value of $k$.", ["relations between roots and coefficients", "sum and product of roots (additional maths)"], "faible", 2,
          [(r"You write the product of the roots: $\alpha\times3\alpha=k$", 1), (r"You obtain $k=3\times2^{2}=12$", 1)],
          r"The product of the roots of $x^{2}+bx+c=0$ is the constant term $c$; here it is $k$.",
          r"$k=\alpha\times3\alpha=3\alpha^{2}=3\times2^{2}=12$. Check: $x^{2}-8x+12=(x-2)(x-6)$, with roots $2$ and $6=3\times2$.",
          ans=r"$k=12$",
          piege=r"The condition “$\alpha$ and $3\alpha$” is used twice: first in the sum of the roots, then in their product.".replace(r"“", "“").replace(r"”", "”")),
    ]))

    ex.append(E("2", G, 8, "", [
        S("i", r"(i) Find how many even four-digit numbers can be formed from the digits $1,2,3,4,5,6$ if no digit may be used more than once.",
          ["permutations and combinations (additional maths)"], "moyenne", 4,
          [(r"You state that the last digit must be even: $2$, $4$ or $6$, that is $3$ choices", 1), (r"You count the choices of the other digits: $5\times4\times3=60$", 1),
           (r"You multiply the choices: $3\times60$", 1), (r"You obtain $180$", 1)],
          r"Fill first the place that has a restriction, then count the choices left for the other places: the numbers of choices are multiplied.",
          r"The last digit is even, so it is $2$, $4$ or $6$: $3$ choices. The first digit then has $5$ choices (any of the other digits), the second $4$ and the third $3$. The total is $3\times5\times4\times3=180$.",
          ans=r"$180$",
          piege=r"Start with the restricted place (the units digit): if the first digit is chosen first, the number of choices for the last digit depends on it."),
        S("ii", r"(ii) Expand $(1+2x)^{6}$ in ascending powers of $x$ up to and including the term in $x^{3}$. Use your expansion, with a suitable value of $x$, to estimate $1.02^{6}$ correct to $4$ decimal places.",
          ["binomial expansion (additional maths)"], "moyenne", 4,
          [(r"You find the terms $1+12x$", 1), (r"You find the terms $60x^{2}+160x^{3}$", 1), (r"You take $x=0.01$: $1+0.12+0.006+0.00016$", 1), (r"You obtain $1.1262$ to $4$ decimal places", 1)],
          r"The term in $x^{r}$ of $(1+y)^{n}$ is $\dbinom{n}{r}y^{r}$, here with $y=2x$. To estimate a power such as $1.02^{6}$, write $1.02=1+2(0.01)$ and substitute $x=0.01$.",
          r"$(1+2x)^{6}=1+\dbinom{6}{1}(2x)+\dbinom{6}{2}(2x)^{2}+\dbinom{6}{3}(2x)^{3}+\ldots=1+12x+60x^{2}+160x^{3}+\ldots$ Since $1.02=1+2(0.01)$, take $x=0.01$: $1.02^{6}\approx1+0.12+0.006+0.00016=1.12616\approx1.1262$.",
          ans=r"$1+12x+60x^{2}+160x^{3}$ ; $1.1262$",
          piege=r"The coefficients include the powers of $2$: $\dbinom{6}{2}\times2^{2}=60$ and $\dbinom{6}{3}\times2^{3}=160$."),
    ]))

    ex.append(E("3", G, 8, r"A ball is dropped from a height of $8$ m onto horizontal ground. After each bounce it rises to $60\%$ of the height from which it has just fallen.", [
        S("a", r"Find the height to which the ball rises after the $4^{\text{th}}$ bounce.", ["arithmetic and geometric progressions"], "faible", 3,
          [(r"You find the first rebound height $4.8$ m and recognise a geometric progression with $r=0.6$", 1), (r"You use $T_{n}=ar^{n-1}$ with $n=4$: $4.8\times0.6^{3}$", 1), (r"You obtain $1.0368$ m ($1.04$ m)", 1)],
          r"The rebound heights form a geometric progression: $T_{n}=ar^{n-1}$, where $a$ is the first rebound height and $r$ the common ratio.",
          r"The first rebound height is $0.6\times8=4.8$ m, so $a=4.8$ and $r=0.6$. After the $4^{\text{th}}$ bounce: $T_{4}=4.8\times0.6^{3}=4.8\times0.216=1.0368$ m, that is about $1.04$ m.",
          ans=r"$1.0368$ m"),
        S("b", r"Find the total distance travelled by the ball from the moment it is dropped until it comes to rest.", ["geometric progression sum to infinity", "arithmetic and geometric progressions"], "elevee", 3,
          [(r"You find the sum of the rebound heights to infinity: $\dfrac{4.8}{1-0.6}=12$ m", 1), (r"You count each rebound twice (up and down): $2\times12=24$ m", 1), (r"You add the first fall of $8$ m: $32$ m", 1)],
          r"After each bounce the ball travels the rebound height upwards and the same height downwards; the first fall of $8$ m is travelled only once.",
          r"Total of the rebound heights: $\dfrac{a}{1-r}=\dfrac{4.8}{1-0.6}=\dfrac{4.8}{0.4}=12$ m. Each rebound is travelled twice, up then down: $2\times12=24$ m. Adding the first fall: $8+24=32$ m.",
          ans=r"$32$ m",
          piege=r"The first fall of $8$ m is not a rebound: it is counted once, while every rebound height is counted twice."),
        S("c", r"The ball is said to have stopped bouncing when it rises less than $0.5$ m. Find the number of the first bounce after which the ball rises less than $0.5$ m.", ["arithmetic and geometric progressions"], "moyenne", 2,
          [(r"You solve $8\times0.6^{n}<0.5$ (or $4.8\times0.6^{n-1}<0.5$), for example with logarithms: $n>5.4$", 1), (r"You state that the $6^{\text{th}}$ bounce is the first", 1)],
          r"Write the condition as an inequality in $n$; to solve $r^{n}<c$ with $0<r<1$ take logarithms and reverse the inequality, because $\log r<0$.",
          r"After the $n^{\text{th}}$ bounce the height is $8\times0.6^{n}$. $8\times0.6^{n}<0.5$ gives $0.6^{n}<0.0625$, so $n\log0.6<\log0.0625$ and $n>\dfrac{\log0.0625}{\log0.6}=5.43$. The first whole number is $n=6$. Check: $8\times0.6^{5}=0.622>0.5$ and $8\times0.6^{6}=0.373<0.5$.",
          ans=r"the $6^{\text{th}}$ bounce",
          piege=r"Dividing by $\log0.6$, which is negative, reverses the inequality sign."),
    ]))

    ex.append(E("4", G, 10, "", [
        S("i-a", "(i)(a) An operation $*$ is defined on the set $S=\\{1,2,4,8\\}$ by $x*y=xy\\pmod{15}$, that is, the remainder when $xy$ is divided by $15$. Copy and complete the table below.\n\n" + TABLE_GROUPE,
          ["group axioms and operation tables"], "faible", 2,
          [(r"You find $2*8=1$ and $4*4=1$", 1), (r"You find $4*8=2$ and $8*8=4$", 1)],
          r"Multiply the two numbers, then take the remainder on division by $15$.",
          "$2*8=16\\equiv1$; $4*4=16\\equiv1$; $4*8=32\\equiv2$; $8*8=64\\equiv4$.\n\n" + TABLE_GROUPE_COMPLETE,
          ans=r"completed table: $2*8=1$, $4*4=1$, $4*8=2$, $8*8=4$"),
        S("i-b", r"(i)(b) Show that $S$ forms a group under $*$. [Assume that $*$ is associative.]", ["group axioms and operation tables", "binary operations and groups"], "moyenne", 4,
          [(r"Closure: every entry of the table belongs to $S$", 1), (r"Identity: $1$, because the row and the column of $1$ repeat the headings", 1),
           (r"Inverses: $1^{-1}=1$, $2^{-1}=8$, $4^{-1}=4$ and $8^{-1}=2$, each found by locating $1$ in the table", 1), (r"You conclude that $S$ is a group under $*$", 1)],
          r"A set with an operation is a group when it is closed, associative, has an identity element and every element has an inverse.",
          r"**Closure:** every entry in the table is $1$, $2$, $4$ or $8$, so $x*y\in S$ for all $x$ and $y$. **Identity:** the row of $1$ is $1,2,4,8$ and the column of $1$ is $1,2,4,8$, so $1$ is the identity. **Inverses:** $1*1=1$, $2*8=1$, $8*2=1$ and $4*4=1$, so $1^{-1}=1$, $2^{-1}=8$, $8^{-1}=2$, $4^{-1}=4$. Associativity is assumed. All the axioms hold, so $(S,*)$ is a group.",
          ans=r"$S$ is a group under $*$",
          piege=r"The element $4$ is its own inverse, because $4*4=1$: the inverse of an element is not always a different element."),
        S("ii", r"(ii) The matrix $M=\begin{pmatrix}2&1\\3&2\end{pmatrix}$. Find $M^{-1}$ and hence solve the simultaneous equations $2x+y=5$ and $3x+2y=8$.",
          ["matrices and inverses (additional maths)"], "moyenne", 4,
          [(r"You find the determinant: $2\times2-1\times3=1$", 1), (r"You write the inverse: $M^{-1}=\begin{pmatrix}2&-1\\-3&2\end{pmatrix}$", 1),
           (r"You multiply: $\begin{pmatrix}x\\y\end{pmatrix}=M^{-1}\begin{pmatrix}5\\8\end{pmatrix}$", 1), (r"You obtain $x=2$ and $y=1$", 1)],
          r"The system $M\begin{pmatrix}x\\y\end{pmatrix}=\begin{pmatrix}p\\q\end{pmatrix}$ has the solution $\begin{pmatrix}x\\y\end{pmatrix}=M^{-1}\begin{pmatrix}p\\q\end{pmatrix}$, where $M^{-1}=\dfrac{1}{ad-bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}$.",
          r"$\det M=2\times2-1\times3=1$, so $M^{-1}=\begin{pmatrix}2&-1\\-3&2\end{pmatrix}$. The equations are $M\begin{pmatrix}x\\y\end{pmatrix}=\begin{pmatrix}5\\8\end{pmatrix}$, so $\begin{pmatrix}x\\y\end{pmatrix}=\begin{pmatrix}2&-1\\-3&2\end{pmatrix}\begin{pmatrix}5\\8\end{pmatrix}=\begin{pmatrix}10-8\\-15+16\end{pmatrix}=\begin{pmatrix}2\\1\end{pmatrix}$. Check: $2(2)+1=5$ and $3(2)+2(1)=8$.",
          ans=r"$x=2$ and $y=1$",
          piege=r"The inverse is multiplied on the left of the column of constants: $M^{-1}\begin{pmatrix}5\\8\end{pmatrix}$, not $\begin{pmatrix}5\\8\end{pmatrix}M^{-1}$."),
    ]))

    ex.append(E("5", G, 8, r"A tailor makes $x$ shirts and $y$ pairs of trousers in a week. A shirt takes $2$ hours to make and a pair of trousers takes $3$ hours. The tailor works for at most $36$ hours in a week. He makes at least as many shirts as pairs of trousers, and at least $3$ pairs of trousers. The profit is $6000$ FCFA on each shirt and $5000$ FCFA on each pair of trousers.", [
        S("a", r"Show that $2x+3y\leq36$ and write down two other inequalities, in terms of $x$ and $y$, which satisfy the conditions of the problem.", ["linear inequalities and optimisation"], "faible", 3,
          [(r"You write the time $2x+3y\leq36$", 1), (r"You write $x\geq y$", 1), (r"You write $y\geq3$", 1)],
          r"Translate each condition into an inequality: “at most” is $\leq$ and “at least” is $\geq$.".replace(r"“", "“").replace(r"”", "”"),
          r"The $x$ shirts take $2x$ hours and the $y$ pairs of trousers take $3y$ hours, so the time is $2x+3y\leq36$. At least as many shirts as pairs of trousers: $x\geq y$. At least $3$ pairs of trousers: $y\geq3$.",
          ans=None),
        S("b", r"On graph paper, taking $1$ cm to represent $1$ unit on both axes, draw the lines $2x+3y=36$, $x=y$ and $y=3$, and shade the region $R$ in which all the conditions are satisfied.",
          ["linear inequalities and optimisation", "linear programming and inequality regions"], "moyenne", 3,
          [(r"You draw the line $2x+3y=36$ through $(18,0)$ and $(0,12)$ (or equivalent points)", 1), (r"You draw the lines $x=y$ and $y=3$", 1),
           (r"You shade the triangle with vertices $(3,3)$, $(13.5,3)$ and $(7.2,7.2)$", 1)],
          r"Draw each boundary line from two points, then test a point to decide which side satisfies each inequality. The region satisfying all the inequalities lies on the correct side of every line.",
          r"$2x+3y=36$ passes through $(18,0)$ and $(0,12)$; $x=y$ passes through the origin and $(10,10)$; $y=3$ is horizontal. Test $(5,4)$: $2(5)+3(4)=22\leq36$, $5\geq4$ and $4\geq3$, so the region contains $(5,4)$. The vertices are $(3,3)$ (lines $y=3$ and $x=y$), $(13.5,3)$ (lines $y=3$ and $2x+3y=36$) and $(7.2,7.2)$ (lines $x=y$ and $2x+3y=36$).",
          ans=None, fig="region_a5"),
        S("c", r"Find the greatest weekly profit that the tailor can make, and the number of shirts and of pairs of trousers that give it.", ["linear inequalities and optimisation"], "elevee", 2,
          [(r"You test the whole-number points of $R$ near the vertex $(13.5,3)$: $(13,3)$ gives a profit of $93000$ FCFA", 1), (r"You compare with $(12,4)$, which gives $92000$ FCFA, and state the greatest profit: $93000$ FCFA with $13$ shirts and $3$ pairs of trousers", 1)],
          r"The numbers of items are whole numbers: the best point of the region may not be a vertex, so test the whole-number points near the vertices and compare the profits $6000x+5000y$.",
          r"The vertex $(13.5,3)$ is not a whole-number point. $(13,3)$ lies in $R$ ($2(13)+3(3)=35\leq36$) and gives $6000(13)+5000(3)=93000$ FCFA. $(12,4)$ lies in $R$ ($24+12=36$) and gives $72000+20000=92000$ FCFA. The points $(11,4)$, $(10,5)$ and $(9,6)$ give less. The greatest weekly profit is $93000$ FCFA, with $13$ shirts and $3$ pairs of trousers.",
          ans=r"$93000$ FCFA, with $13$ shirts and $3$ pairs of trousers",
          piege=r"The vertex $(13.5,3)$ would give a larger profit but half a shirt cannot be made: the answer must be a whole-number point of the region."),
    ]))

    ex.append(E("6", G, 9, "", [
        S("i", r"(i) Solve the equation $2\cos^{2}x-\sin x-1=0$ for $0^{\circ}\leq x\leq360^{\circ}$.", ["trigonometric identities and equations"], "moyenne", 4,
          [(r"You replace $\cos^{2}x$ by $1-\sin^{2}x$", 1), (r"You obtain $2\sin^{2}x+\sin x-1=0$", 1), (r"You factorise: $(2\sin x-1)(\sin x+1)=0$", 1), (r"You obtain $x=30^{\circ}$, $150^{\circ}$ and $270^{\circ}$", 1)],
          r"Use $\cos^{2}x+\sin^{2}x=1$ to write the equation with a single trigonometric function, then solve the quadratic in that function.",
          r"$2(1-\sin^{2}x)-\sin x-1=0$ gives $2\sin^{2}x+\sin x-1=0$, that is $(2\sin x-1)(\sin x+1)=0$. So $\sin x=\dfrac{1}{2}$, giving $x=30^{\circ}$ or $150^{\circ}$, or $\sin x=-1$, giving $x=270^{\circ}$.",
          ans=r"$x=30^{\circ}$, $150^{\circ}$, $270^{\circ}$",
          piege=r"The value $\sin x=-1$ gives one solution only: $270^{\circ}$."),
        S("ii-a", r"(ii)(a) Show that $\dfrac{\sin2\theta}{\sin\theta}-\dfrac{\cos2\theta}{\cos\theta}\equiv\dfrac{1}{\cos\theta}$.", ["trigonometric identities and equations", "double angle identities"], "moyenne", 3,
          [(r"You use $\sin2\theta=2\sin\theta\cos\theta$ to simplify the first fraction: $2\cos\theta$", 1), (r"You use $\cos2\theta=2\cos^{2}\theta-1$ and the common denominator $\cos\theta$", 1), (r"You simplify to $\dfrac{1}{\cos\theta}$", 1)],
          r"Double angle formulae: $\sin2\theta=2\sin\theta\cos\theta$ and $\cos2\theta=2\cos^{2}\theta-1$.",
          r"$\dfrac{\sin2\theta}{\sin\theta}=\dfrac{2\sin\theta\cos\theta}{\sin\theta}=2\cos\theta$. So the left-hand side is $2\cos\theta-\dfrac{2\cos^{2}\theta-1}{\cos\theta}=\dfrac{2\cos^{2}\theta-(2\cos^{2}\theta-1)}{\cos\theta}=\dfrac{1}{\cos\theta}$.",
          ans=None),
        S("ii-b", r"(ii)(b) Hence solve the equation $\dfrac{\sin2\theta}{\sin\theta}-\dfrac{\cos2\theta}{\cos\theta}=2$ for $0^{\circ}<\theta<90^{\circ}$.", ["trigonometric identities and equations", "double angle identities"], "elevee", 2,
          [(r"You use the identity to write $\dfrac{1}{\cos\theta}=2$, that is $\cos\theta=\dfrac{1}{2}$", 1), (r"You obtain $\theta=60^{\circ}$", 1)],
          r"Replace the left-hand side by the result of part (a), then solve the simple equation in $\cos\theta$ in the given range.",
          r"By part (a) the equation is $\dfrac{1}{\cos\theta}=2$, so $\cos\theta=\dfrac{1}{2}$ and, for $0^{\circ}<\theta<90^{\circ}$, $\theta=60^{\circ}$. Check: $\dfrac{\sin120^{\circ}}{\sin60^{\circ}}-\dfrac{\cos120^{\circ}}{\cos60^{\circ}}=1-(-1)=2$.",
          ans=r"$\theta=60^{\circ}$",
          piege=r"Take the reciprocal carefully: $\dfrac{1}{\cos\theta}=2$ gives $\cos\theta=\dfrac{1}{2}$, not $\cos\theta=2$."),
    ]))

    ex.append(E("7", G, 8, r"The position vectors of the points $A$ and $B$, relative to the origin $O$, are $3\mathbf{i}+\mathbf{j}$ and $\mathbf{i}+5\mathbf{j}$ respectively.", [
        S("a", r"Find the position vector of the midpoint of $AB$ and the length of $AB$, leaving your answer for the length as a surd in its simplest form.", ["vector geometry (additional maths)"], "faible", 3,
          [(r"You find the midpoint: $\dfrac{1}{2}\left[(3\mathbf{i}+\mathbf{j})+(\mathbf{i}+5\mathbf{j})\right]=2\mathbf{i}+3\mathbf{j}$", 1), (r"You find $\overrightarrow{AB}=-2\mathbf{i}+4\mathbf{j}$", 1), (r"You find $|AB|=\sqrt{20}=2\sqrt{5}$", 1)],
          r"The midpoint of $AB$ has position vector $\dfrac{1}{2}(\mathbf{a}+\mathbf{b})$, and $\overrightarrow{AB}=\mathbf{b}-\mathbf{a}$.",
          r"Midpoint: $\dfrac{1}{2}(3\mathbf{i}+\mathbf{j}+\mathbf{i}+5\mathbf{j})=\dfrac{1}{2}(4\mathbf{i}+6\mathbf{j})=2\mathbf{i}+3\mathbf{j}$. $\overrightarrow{AB}=\mathbf{b}-\mathbf{a}=(\mathbf{i}+5\mathbf{j})-(3\mathbf{i}+\mathbf{j})=-2\mathbf{i}+4\mathbf{j}$, so $|AB|=\sqrt{(-2)^{2}+4^{2}}=\sqrt{20}=2\sqrt{5}$.",
          ans=r"$2\mathbf{i}+3\mathbf{j}$ and $2\sqrt{5}$"),
        S("b", r"Find a vector equation of the line $AB$.", ["vector equations of lines", "vector geometry (additional maths)"], "faible", 2,
          [(r"You use a point and the direction vector $\overrightarrow{AB}$ (or a multiple of it)", 1), (r"You write $\mathbf{r}=3\mathbf{i}+\mathbf{j}+t(-2\mathbf{i}+4\mathbf{j})$ (or equivalent)", 1)],
          r"A line through the point with position vector $\mathbf{a}$ and with direction $\mathbf{d}$ has the equation $\mathbf{r}=\mathbf{a}+t\mathbf{d}$.",
          r"The line passes through $A$ and has direction $\overrightarrow{AB}=-2\mathbf{i}+4\mathbf{j}$. So $\mathbf{r}=3\mathbf{i}+\mathbf{j}+t(-2\mathbf{i}+4\mathbf{j})$, or, with the direction $-\mathbf{i}+2\mathbf{j}$, $\mathbf{r}=3\mathbf{i}+\mathbf{j}+\lambda(-\mathbf{i}+2\mathbf{j})$.",
          ans=r"$\mathbf{r}=3\mathbf{i}+\mathbf{j}+t(-2\mathbf{i}+4\mathbf{j})$"),
        S("c", r"The point $P$ lies on the line $AB$ and $OP$ is perpendicular to $AB$. Find the position vector of $P$.", ["scalar product", "vector geometry (additional maths)"], "elevee", 3,
          [(r"You write $\overrightarrow{OP}=(3-2t)\mathbf{i}+(1+4t)\mathbf{j}$ for a point of the line", 1), (r"You use the scalar product $\overrightarrow{OP}\cdot\overrightarrow{AB}=0$: $-2(3-2t)+4(1+4t)=0$", 1), (r"You obtain $t=0.1$ and $\overrightarrow{OP}=2.8\mathbf{i}+1.4\mathbf{j}$", 1)],
          r"Two non-zero vectors are perpendicular when their scalar product is zero: $\mathbf{a}\cdot\mathbf{b}=0$.",
          r"A point of the line has position vector $(3-2t)\mathbf{i}+(1+4t)\mathbf{j}$. $OP\perp AB$ means $\overrightarrow{OP}\cdot\overrightarrow{AB}=0$: $-2(3-2t)+4(1+4t)=-6+4t+4+16t=20t-2=0$, so $t=0.1$. Then $\overrightarrow{OP}=(3-0.2)\mathbf{i}+(1+0.4)\mathbf{j}=2.8\mathbf{i}+1.4\mathbf{j}$.",
          ans=r"$2.8\mathbf{i}+1.4\mathbf{j}$"),
    ]))

    ex.append(E("8", G, 7, "", [
        S("i", r"(i) Find the coordinates of the stationary points of the curve $y=x^{3}-6x^{2}+9x+1$ and determine their nature.", ["applications of differentiation"], "moyenne", 4,
          [(r"You differentiate: $\dfrac{dy}{dx}=3x^{2}-12x+9$", 1), (r"You solve $\dfrac{dy}{dx}=0$: $x=1$ and $x=3$", 1), (r"You find the coordinates $(1,5)$ and $(3,1)$", 1),
           (r"You use $\dfrac{d^{2}y}{dx^{2}}=6x-12$: $(1,5)$ is a maximum and $(3,1)$ is a minimum", 1)],
          r"At a stationary point $\dfrac{dy}{dx}=0$. The second derivative decides the nature: $\dfrac{d^{2}y}{dx^{2}}<0$ for a maximum and $\dfrac{d^{2}y}{dx^{2}}>0$ for a minimum.",
          r"$\dfrac{dy}{dx}=3x^{2}-12x+9=3(x^{2}-4x+3)=3(x-1)(x-3)$, which is zero for $x=1$ and $x=3$. $x=1$: $y=1-6+9+1=5$; $x=3$: $y=27-54+27+1=1$. $\dfrac{d^{2}y}{dx^{2}}=6x-12$: at $x=1$ it is $-6<0$, a maximum; at $x=3$ it is $6>0$, a minimum.",
          ans=r"maximum at $(1,5)$ and minimum at $(3,1)$",
          piege=r"The values $x=1$ and $x=3$ are substituted in the equation of the curve, not in the derivative, to find $y$."),
        S("ii", r"(ii) The gradient of a curve is given by $\dfrac{dy}{dx}=4x-6$. The curve passes through the point $(3,5)$. Find the equation of the curve.", ["integration of polynomials"], "faible", 3,
          [(r"You integrate: $y=2x^{2}-6x+c$", 1), (r"You substitute $(3,5)$: $5=18-18+c$, so $c=5$", 1), (r"You write $y=2x^{2}-6x+5$", 1)],
          r"Integrate the gradient function to find $y$, then use the point on the curve to find the constant of integration.",
          r"$y=\displaystyle\int(4x-6)\,dx=2x^{2}-6x+c$. The point $(3,5)$ is on the curve: $5=2(3)^{2}-6(3)+c=18-18+c$, so $c=5$. The equation of the curve is $y=2x^{2}-6x+5$.",
          ans=r"$y=2x^{2}-6x+5$",
          piege=r"Do not forget the constant of integration: without $c$ the curve cannot pass through the given point."),
    ]))
    return ex
