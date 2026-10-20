r"""Section A (questions 1 a 8, 66 points, toutes obligatoires) de l'epreuve inedite GCE O Level Additional Mathematics Paper 2 n.1.

Le vrai sujet : « Answer ALL questions in SECTION A (Pure Mathematics) and ANY TWO questions from EITHER SECTION B (Mechanics) OR SECTION C
(Statistics and Probability) » ; la plateforme ne code pas ce choix, donc l'inedite contient les huit questions de A et DEUX de la Section B.
Chaque sous-question : barème exact (`pts`), grille `crit` (somme = pts), rappel, resolution, reponse finale `ans` (recalculee par
verifier_reponses_addmaths_p2.py), piege eventuel, figure de corrige (`fig`) ou d'enonce (`fig_enonce`). Chaines BRUTES.
"""


def S(num, text, themes, diff, pts, crit, rappel, sol, ans=None, piege=None, conseil=None, fig=None, fig_enonce=None):
    assert abs(sum(p for _, p in crit) - pts) < 1e-9, (num, text[:40], sum(p for _, p in crit), pts)
    return dict(num=num, text=text, themes=themes, diff=diff, pts=pts, crit=crit, rappel=rappel, sol=sol, ans=ans,
                piege=piege, conseil=conseil, fig=fig, fig_enonce=fig_enonce)


# Numerotation AFFICHEE : (exercice, numero de travail) -> (numero unique dans l'exercice, groupe_local). Le numero de travail garde la forme du vrai
# sujet (« i-a » = (i)(a)) ; la plateforme veut un numero unique par exercice et imprime le groupe local (« (i) ») une fois au-dessus de ses parties.
NUMEROS = {
    ("1", "i-a"): ("a", "(i)"), ("1", "i-b"): ("b", "(i)"), ("1", "ii-a"): ("c", "(ii)"), ("1", "ii-b"): ("d", "(ii)"),
    ("2", "i"): ("i", ""), ("2", "ii"): ("ii", ""),
    ("4", "i-a"): ("a", "(i)"), ("4", "i-b"): ("b", "(i)"), ("4", "ii"): ("ii", ""),
    ("6", "i"): ("i", ""), ("6", "ii-a"): ("a", "(ii)"), ("6", "ii-b"): ("b", "(ii)"), ("6", "ii-c"): ("c", "(ii)"),
    ("8", "i"): ("i", ""), ("8", "ii"): ("ii", ""),
    ("9", "i-a"): ("a", "(i)"), ("9", "i-b"): ("b", "(i)"), ("9", "ii-a"): ("c", "(ii)"), ("9", "ii-b"): ("d", "(ii)"),
    ("9", "iii-a"): ("e", "(iii)"), ("9", "iii-b"): ("f", "(iii)"), ("9", "iii-c"): ("g", "(iii)"),
    ("10", "i-a"): ("a", "(i)"), ("10", "i-b"): ("b", "(i)"), ("10", "i-c"): ("c", "(i)"), ("10", "ii"): ("d", "(ii)"),
    ("10", "iii-a"): ("e", "(iii)"), ("10", "iii-b"): ("f", "(iii)"), ("10", "iii-c"): ("g", "(iii)"),
}


def numero_affiche(ex, num):
    """Numero unique et groupe local imprimes pour la sous-question de travail `num` de l'exercice `ex` (lettres seules : a, b, c...)."""
    return NUMEROS.get((ex, num), (num, ""))


def sans_prefixe(texte):
    """Retire « (i)(a) », « (ii) »... en tete de l'enonce : le numero et le groupe local sont imprimes par la compilation."""
    import re
    return re.sub(r"^\((?:i|ii|iii)\)(?:\([a-c]\))?\s+", "", texte)


def E(num, groupe, pts, intro, subs):
    assert abs(sum(s["pts"] for s in subs) - pts) < 1e-9, (num, sum(s["pts"] for s in subs), pts)
    return dict(num=num, groupe=groupe, pts=pts, intro=intro, subs=subs)


TABLE_GROUPE = r"""| $*$ | 1 | 3 | 7 | 9 |
|---|---|---|---|---|
| **1** | 1 | 3 | | 9 |
| **3** | 3 | | 1 | 7 |
| **7** | 7 | 1 | 9 | |
| **9** | | 7 | 3 | 1 |"""


def section_a():
    G = "SECTION A"
    ex = []

    ex.append(E("1", G, 8, "", [
        S("i-a", r"(i)(a) The polynomial $f(x)=x^{3}+kx^{2}-4x-12$ has $(x-2)$ as a factor. Find the value of the constant $k$.",
          ["remainder and factor theorem"], "faible", 2,
          [("You write $f(2)=0$ and substitute: $8+4k-8-12=0$", 1), ("You solve to obtain $k=3$", 1)],
          r"If $(x-a)$ is a factor of $f(x)$ then $f(a)=0$.",
          r"Since $(x-2)$ is a factor, $f(2)=0$: $2^{3}+k(2)^{2}-4(2)-12=8+4k-8-12=4k-12=0$, so $k=3$.",
          ans=r"$k=3$"),
        S("i-b", r"(i)(b) With this value of $k$, factorise $f(x)$ completely.", ["factor theorem and factorising cubics"], "faible", 2,
          [("You divide by $(x-2)$ or group the terms to find the quadratic factor $x^{2}+5x+6$ (or equivalent)", 1), ("You factorise completely: $(x-2)(x+2)(x+3)$", 1)],
          r"Divide the cubic by the known linear factor to obtain a quadratic, then factorise the quadratic.",
          r"$f(x)=x^{3}+3x^{2}-4x-12=x^{2}(x+3)-4(x+3)=(x+3)(x^{2}-4)=(x+3)(x-2)(x+2)$. Check: $f(-2)=-8+12+8-12=0$ and $f(-3)=-27+27+12-12=0$.",
          ans=r"$(x-2)(x+2)(x+3)$"),
        S("ii-a", r"(ii)(a) The roots of the equation $2x^{2}-6x+3=0$ are $\alpha$ and $\beta$. State the values of $\alpha+\beta$ and $\alpha\beta$.",
          ["relations between roots and coefficients"], "faible", 1,
          [("You state $\\alpha+\\beta=3$ and $\\alpha\\beta=\\dfrac{3}{2}$", 1)],
          r"For $ax^{2}+bx+c=0$: $\alpha+\beta=-\dfrac{b}{a}$ and $\alpha\beta=\dfrac{c}{a}$.",
          r"$a=2$, $b=-6$, $c=3$, so $\alpha+\beta=-\dfrac{-6}{2}=3$ and $\alpha\beta=\dfrac{3}{2}$.",
          ans=r"$\alpha+\beta=3$, $\alpha\beta=\dfrac{3}{2}$"),
        S("ii-b", r"(ii)(b) For the same equation, find a quadratic equation, with integer coefficients, whose roots are $\dfrac{1}{\alpha}$ and $\dfrac{1}{\beta}$.",
          ["relations between roots and coefficients", "sum and product of roots (additional maths)"], "moyenne", 3,
          [("You find the sum of the new roots: $\\dfrac{1}{\\alpha}+\\dfrac{1}{\\beta}=\\dfrac{\\alpha+\\beta}{\\alpha\\beta}=2$", 1), ("You find their product: $\\dfrac{1}{\\alpha\\beta}=\\dfrac{2}{3}$", 1),
           ("You form $x^{2}-2x+\\dfrac{2}{3}=0$, that is $3x^{2}-6x+2=0$", 1)],
          r"A quadratic with roots $p$ and $q$ is $x^{2}-(p+q)x+pq=0$. Find the sum and the product of the new roots from $\alpha+\beta$ and $\alpha\beta$.",
          r"Sum of the new roots: $\dfrac{1}{\alpha}+\dfrac{1}{\beta}=\dfrac{\beta+\alpha}{\alpha\beta}=\dfrac{3}{\frac{3}{2}}=2$. Product: $\dfrac{1}{\alpha}\times\dfrac{1}{\beta}=\dfrac{1}{\alpha\beta}=\dfrac{2}{3}$. The equation is $x^{2}-2x+\dfrac{2}{3}=0$; multiplying by $3$ gives $3x^{2}-6x+2=0$.",
          ans=r"$3x^{2}-6x+2=0$",
          piege=r"$\dfrac{1}{\alpha}+\dfrac{1}{\beta}$ is not $\dfrac{1}{\alpha+\beta}$: add the fractions over the common denominator $\alpha\beta$."),
    ]))

    ex.append(E("2", G, 8, "", [
        S("i", r"(i) A committee of $6$ people is to be chosen from $7$ men and $5$ women. Find the number of committees that contain at least $4$ men.",
          ["permutations and combinations (additional maths)"], "moyenne", 4,
          [("You identify the three cases: $4$ men and $2$ women, $5$ men and $1$ woman, $6$ men", 1), ("You calculate $\\dbinom{7}{4}\\dbinom{5}{2}=350$ and $\\dbinom{7}{5}\\dbinom{5}{1}=105$", 1),
           ("You calculate $\\dbinom{7}{6}=7$", 1), ("You add the three cases: $462$", 1)],
          r"“At least” means that several cases are possible: count each case with combinations, multiply the choices within a case and add the cases.",
          r"There are three cases. $4$ men and $2$ women: $\dbinom{7}{4}\times\dbinom{5}{2}=35\times10=350$. $5$ men and $1$ woman: $\dbinom{7}{5}\times\dbinom{5}{1}=21\times5=105$. $6$ men and no woman: $\dbinom{7}{6}=7$. The total is $350+105+7=462$.",
          ans=r"$462$",
          piege=r"The choices inside one case are multiplied; the different cases are added."),
        S("ii", r"(ii) Find the term in $x^{3}$ in the expansion of $\left(2x+\dfrac{1}{x}\right)^{7}$.",
          ["binomial expansion (additional maths)"], "moyenne", 4,
          [("You write the general term $\\dbinom{7}{r}(2x)^{7-r}\\left(\\dfrac{1}{x}\\right)^{r}$", 1), ("You find the power of $x$: $x^{7-2r}$, so $7-2r=3$ and $r=2$", 1),
           ("You evaluate $\\dbinom{7}{2}\\times2^{5}=21\\times32$", 1), ("You obtain $672x^{3}$", 1)],
          r"The general term of $(a+b)^{n}$ is $\dbinom{n}{r}a^{n-r}b^{r}$. Collect the powers of $x$ in the general term and solve for $r$.",
          r"General term: $T_{r+1}=\dbinom{7}{r}(2x)^{7-r}\left(\dfrac{1}{x}\right)^{r}=\dbinom{7}{r}2^{7-r}x^{7-r}x^{-r}=\dbinom{7}{r}2^{7-r}x^{7-2r}$. For $x^{3}$: $7-2r=3$, so $r=2$. The term is $\dbinom{7}{2}2^{5}x^{3}=21\times32\,x^{3}=672x^{3}$.",
          ans=r"$672x^{3}$",
          piege=r"The factor $2$ belongs to $2x$ and is raised to the power $7-r=5$; the power of $x$ is $7-r-r$."),
    ]))

    ex.append(E("3", G, 8, r"A farmer plants trees in rows. The first row has $5$ trees and each row after it has $3$ more trees than the row before.", [
        S("a", r"Find the number of trees in the $12^{\text{th}}$ row.", ["arithmetic and geometric progressions"], "faible", 3,
          [("You recognise an arithmetic progression with $a=5$ and $d=3$", 1), ("You use $T_{n}=a+(n-1)d$ with $n=12$", 1), ("You obtain $38$ trees", 1)],
          r"The numbers of trees form an arithmetic progression: $T_{n}=a+(n-1)d$.",
          r"$a=5$, $d=3$, so $T_{12}=5+(12-1)\times3=5+33=38$ trees.",
          ans=r"$38$"),
        S("b", r"Find the total number of trees in the first $12$ rows.", ["arithmetic and geometric progressions"], "moyenne", 3,
          [("You use $S_{n}=\\dfrac{n}{2}(a+l)$ or $S_{n}=\\dfrac{n}{2}[2a+(n-1)d]$", 1), ("You substitute: $\\dfrac{12}{2}(5+38)$", 1), ("You obtain $258$ trees", 1)],
          r"The sum of the first $n$ terms of an arithmetic progression is $S_{n}=\dfrac{n}{2}(a+l)$, where $l$ is the last term.",
          r"$S_{12}=\dfrac{12}{2}(5+38)=6\times43=258$ trees.",
          ans=r"$258$"),
        S("c", r"The farmer wants a row to have more than $60$ trees. Find the number of the first row which does.", ["arithmetic and geometric progressions"], "moyenne", 2,
          [("You solve the inequality $5+3(n-1)>60$ to get $n>19.3$", 1), ("You state that the first such row is the $20^{\\text{th}}$", 1)],
          r"Write the condition as an inequality in $n$, solve it, then take the smallest whole number that satisfies it.",
          r"$5+3(n-1)>60$ gives $3(n-1)>55$, so $n-1>18.3$ and $n>19.3$. The first whole number is $n=20$. Check: $T_{20}=5+57=62>60$ and $T_{19}=5+54=59<60$.",
          ans=r"$20^{\text{th}}$ row",
          piege=r"The answer must be a whole number of rows: $19.3$ rows does not exist, and $n=19$ gives $59$ trees, not more than $60$."),
    ]))

    ex.append(E("4", G, 10, "", [
        S("i-a", "(i)(a) An operation $*$ is defined on the set $S=\\{1,3,7,9\\}$ by $x*y=xy\\pmod{10}$, that is, the remainder when $xy$ is divided by $10$. Copy and complete the table below.\n\n" + TABLE_GROUPE,
          ["group axioms and operation tables"], "faible", 2,
          [("You find $1*7=7$ and $3*3=9$", 1), ("You find $7*9=3$ and $9*1=9$", 1)],
          r"Multiply the two numbers, then take the remainder on division by $10$.",
          "$1*7=7$; $3*3=9$; $7*9=63\\equiv3$; $9*1=9$.\n\n| $*$ | 1 | 3 | 7 | 9 |\n|---|---|---|---|---|\n| **1** | 1 | 3 | 7 | 9 |\n| **3** | 3 | 9 | 1 | 7 |\n| **7** | 7 | 1 | 9 | 3 |\n| **9** | 9 | 7 | 3 | 1 |",
          ans=r"completed table: $1*7=7$, $3*3=9$, $7*9=3$, $9*1=9$"),
        S("i-b", r"(i)(b) Show that $S$ forms a group under $*$. [Assume that $*$ is associative.]", ["group axioms and operation tables", "binary operations and groups"], "moyenne", 4,
          [("Closure: every entry of the table belongs to $S$", 1), ("Identity: $1$, because the row and the column of $1$ repeat the headings", 1),
           ("Inverses: $1^{-1}=1$, $3^{-1}=7$, $7^{-1}=3$ and $9^{-1}=9$, each found by locating $1$ in the table", 1), ("You conclude that $S$ is a group under $*$", 1)],
          r"A set with an operation is a group when it is closed, associative, has an identity element and every element has an inverse.",
          r"**Closure:** every entry in the table is $1$, $3$, $7$ or $9$, so $x*y\in S$ for all $x$ and $y$. **Identity:** the row of $1$ is $1,3,7,9$ and the column of $1$ is $1,3,7,9$, so $1$ is the identity. **Inverses:** $1*1=1$, $3*7=1$, $7*3=1$ and $9*9=1$, so $1^{-1}=1$, $3^{-1}=7$, $7^{-1}=3$, $9^{-1}=9$. Associativity is assumed. All the axioms hold, so $(S,*)$ is a group.",
          ans=r"$S$ is a group under $*$",
          piege=r"Check that the identity appears in every row: an element has an inverse only if $1$ appears in its row."),
        S("ii", r"(ii) A point $P$ is mapped to the point $(7,12)$ by the transformation $T:(x,y)\mapsto(3x+y,\ 5x+2y)$. Find the coordinates of $P$.",
          ["matrix transformations (additional maths)"], "moyenne", 4,
          [("You write the matrix of $T$: $\\begin{pmatrix}3&1\\\\5&2\\end{pmatrix}$", 1), ("You find the inverse: determinant $1$, inverse $\\begin{pmatrix}2&-1\\\\-5&3\\end{pmatrix}$", 1),
           ("You multiply the inverse by $\\begin{pmatrix}7\\\\12\\end{pmatrix}$", 1), ("You obtain the point $(2,1)$", 1)],
          r"If $T$ is represented by $M$ and the image of $\begin{pmatrix}x\\y\end{pmatrix}$ is $\begin{pmatrix}p\\q\end{pmatrix}$, then $\begin{pmatrix}x\\y\end{pmatrix}=M^{-1}\begin{pmatrix}p\\q\end{pmatrix}$.",
          r"$M=\begin{pmatrix}3&1\\5&2\end{pmatrix}$ with $\det M=3\times2-1\times5=1$, so $M^{-1}=\begin{pmatrix}2&-1\\-5&3\end{pmatrix}$. Then $\begin{pmatrix}x\\y\end{pmatrix}=\begin{pmatrix}2&-1\\-5&3\end{pmatrix}\begin{pmatrix}7\\12\end{pmatrix}=\begin{pmatrix}14-12\\-35+36\end{pmatrix}=\begin{pmatrix}2\\1\end{pmatrix}$. Check: $T(2,1)=(6+1,\ 10+2)=(7,12)$.",
          ans=r"$(2,1)$"),
    ]))

    ex.append(E("5", G, 8, r"A school buys $x$ bags of rice at $12000$ FCFA each and $y$ bags of beans at $9000$ FCFA each. The total cost must not exceed $132000$ FCFA, and the number of bags of rice must be at least twice the number of bags of beans.", [
        S("a", r"Show that $4x+3y\leq44$.", ["linear inequalities and optimisation"], "faible", 2,
          [("You write the cost: $12000x+9000y\\leq132000$", 1), ("You divide by $3000$ to obtain $4x+3y\\leq44$", 1)],
          r"Write the condition in words as an inequality, then divide by a common factor.",
          r"The cost of $x$ bags of rice and $y$ bags of beans is $12000x+9000y$ FCFA, and it is at most $132000$: $12000x+9000y\leq132000$. Dividing every term by $3000$ gives $4x+3y\leq44$.",
          ans=None),
        S("b", r"Write down another inequality, in terms of $x$ and $y$, which satisfies the condition on the number of bags.", ["linear inequalities and optimisation"], "faible", 1,
          [("You write $x\\geq2y$", 1)],
          r"“At least twice” means greater than or equal to two times.",
          r"The number of bags of rice is at least twice the number of bags of beans: $x\geq2y$.",
          ans=r"$x\geq2y$"),
        S("c", r"On graph paper, taking $1$ cm to represent $1$ unit on both axes, draw the lines $4x+3y=44$ and $x=2y$, and shade the region $R$ in which all the conditions are satisfied. (Remember that $x\geq0$ and $y\geq0$.)",
          ["linear inequalities and optimisation", "linear programming and inequality regions"], "moyenne", 3,
          [("You draw the line $4x+3y=44$ through $(11,0)$ and $(5,8)$ (or equivalent points)", 1), ("You draw the line $x=2y$ through the origin and $(8,4)$", 1),
           ("You shade the triangle with vertices $(0,0)$, $(11,0)$ and $(8,4)$", 1)],
          r"Draw each boundary line from two points, then test a point to decide which side satisfies each inequality. The region satisfying all the inequalities lies on the correct side of every line.",
          r"$4x+3y=44$ passes through $(11,0)$ and $(5,8)$. $x=2y$ passes through $(0,0)$ and $(8,4)$. Test $(5,1)$: $4(5)+3(1)=23\leq44$ and $5\geq2(1)$, so the region contains $(5,1)$: it is the triangle below the line $4x+3y=44$, below the line $x=2y$ and above the $x$-axis. The lines meet at $(8,4)$, because $4(2y)+3y=44$ gives $y=4$ and $x=8$.",
          ans=None, fig="region"),
        S("d", r"Hence find the greatest total number of bags, of rice and beans together, that the school can buy.", ["linear inequalities and optimisation"], "moyenne", 2,
          [("You test the points of the region with whole-number coordinates, in particular the vertex $(8,4)$", 1), ("You find that the greatest total is $8+4=12$ bags", 1)],
          r"The bags are counted in whole numbers: examine the corner points and the whole-number points near them, and compare the values of $x+y$.",
          r"At the vertices, $x+y$ takes the values $0$ at $(0,0)$, $11$ at $(11,0)$ and $12$ at $(8,4)$, which has whole-number coordinates and lies in $R$. No whole-number point of $R$ gives more: for example $(9,3)$ gives $4(9)+3(3)=45>44$ and $(9,2)$ only gives $11$. The greatest total is $12$ bags (8 of rice and 4 of beans).",
          ans=r"$12$ bags"),
    ]))

    ex.append(E("6", G, 9, "", [
        S("i", r"(i) Show that $\cos^{4}A-\sin^{4}A\equiv\cos2A$.", ["trigonometric identities and equations"], "faible", 3,
          [("You factorise the difference of squares: $(\\cos^{2}A-\\sin^{2}A)(\\cos^{2}A+\\sin^{2}A)$", 1), ("You use $\\cos^{2}A+\\sin^{2}A=1$", 1), ("You use $\\cos^{2}A-\\sin^{2}A=\\cos2A$", 1)],
          r"Factorise as a difference of two squares, then use $\cos^{2}A+\sin^{2}A=1$ and the double angle formula $\cos2A=\cos^{2}A-\sin^{2}A$.",
          r"$\cos^{4}A-\sin^{4}A=(\cos^{2}A)^{2}-(\sin^{2}A)^{2}=(\cos^{2}A-\sin^{2}A)(\cos^{2}A+\sin^{2}A)=(\cos^{2}A-\sin^{2}A)\times1=\cos2A$.",
          ans=None),
        S("ii-a", r"(ii)(a) State the amplitude and the period of the function $f(x)=3\cos2x$.", ["trigonometric graphs and maximum values"], "faible", 2,
          [("You state the amplitude $3$", 1), ("You state the period $\\pi$ (or $180^{\\circ}$)", 1)],
          r"For $y=a\cos bx$: the amplitude is $|a|$ and the period is $\dfrac{2\pi}{b}$.",
          r"Here $a=3$ and $b=2$. The amplitude is $3$ and the period is $\dfrac{2\pi}{2}=\pi$.",
          ans=r"amplitude $3$, period $\pi$"),
        S("ii-b", r"(ii)(b) Sketch the graph of $y=3\cos2x$ for $0\leq x\leq\pi$, showing the coordinates of the maximum points, the minimum point and the points where the curve meets the $x$-axis.",
          ["trigonometric graphs and maximum values", "trigonometric graph plotting"], "moyenne", 3,
          [("You draw one smooth cosine curve with two complete half-periods on $[0,\\pi]$", 1), ("You show the maximum points $(0,3)$ and $(\\pi,3)$ and the minimum point $\\left(\\dfrac{\\pi}{2},-3\\right)$", 1),
           ("You show the zeros at $x=\\dfrac{\\pi}{4}$ and $x=\\dfrac{3\\pi}{4}$", 1)],
          r"Mark the key points of one period: maximum at the start, zero at a quarter period, minimum at half a period, zero at three quarters, maximum at the end of the period.",
          r"The period is $\pi$. The curve starts at its maximum $(0,3)$, crosses the $x$-axis at $x=\dfrac{\pi}{4}$, reaches its minimum $\left(\dfrac{\pi}{2},-3\right)$, crosses the $x$-axis again at $x=\dfrac{3\pi}{4}$ and returns to its maximum at $(\pi,3)$.",
          ans=None, fig="trig"),
        S("ii-c", r"(ii)(c) Use your sketch to state the number of solutions of the equation $3\cos2x=2$ for $0\leq x\leq\pi$.", ["trigonometric graphs and maximum values"], "moyenne", 1,
          [("You state that there are $2$ solutions", 1)],
          r"The solutions of $f(x)=k$ are the points where the horizontal line $y=k$ cuts the graph.",
          r"The line $y=2$ lies between the minimum $-3$ and the maximum $3$. It cuts the curve once on the decreasing part from $(0,3)$ to $\left(\dfrac{\pi}{2},-3\right)$ and once on the increasing part from $\left(\dfrac{\pi}{2},-3\right)$ to $(\pi,3)$: $2$ solutions ($x\approx0.42$ and $x\approx2.72$).",
          ans=r"$2$ solutions"),
    ]))

    ex.append(E("7", G, 8, r"The vector equations of two lines $l_{1}$ and $l_{2}$ are $$l_{1}:\ \mathbf{r}=2\mathbf{i}+\mathbf{j}+s(\mathbf{i}+3\mathbf{j})\qquad\text{and}\qquad l_{2}:\ \mathbf{r}=-\mathbf{i}+3\mathbf{j}+t(5\mathbf{i}+4\mathbf{j}),$$ where $s$ and $t$ are parameters.", [
        S("a", r"The lines intersect. Find the values of the parameters $s$ and $t$ at the point of intersection.", ["vector geometry (additional maths)"], "moyenne", 4,
          [("You equate the $\\mathbf{i}$-components: $2+s=-1+5t$", 1), ("You equate the $\\mathbf{j}$-components: $1+3s=3+4t$", 1), ("You eliminate one parameter: $11t=11$", 1), ("You obtain $t=1$ and $s=2$", 1)],
          r"At the point of intersection the two position vectors are equal: equate the $\mathbf{i}$-components and the $\mathbf{j}$-components to get two simultaneous equations in $s$ and $t$.",
          r"$2\mathbf{i}+\mathbf{j}+s(\mathbf{i}+3\mathbf{j})=-\mathbf{i}+3\mathbf{j}+t(5\mathbf{i}+4\mathbf{j})$. $\mathbf{i}$: $2+s=-1+5t$, so $s=5t-3$. $\mathbf{j}$: $1+3s=3+4t$. Substituting: $1+3(5t-3)=3+4t$, so $15t-8=3+4t$, $11t=11$ and $t=1$. Then $s=5(1)-3=2$.",
          ans=r"$s=2$ and $t=1$"),
        S("b", r"Find the position vector of the point of intersection.", ["vector geometry (additional maths)"], "faible", 2,
          [("You substitute $s=2$ into the equation of $l_{1}$ (or $t=1$ into $l_{2}$)", 1), ("You obtain $4\\mathbf{i}+7\\mathbf{j}$", 1)],
          r"Substitute the value of the parameter into the equation of either line; both must give the same vector.",
          r"$l_{1}$ with $s=2$: $2\mathbf{i}+\mathbf{j}+2(\mathbf{i}+3\mathbf{j})=4\mathbf{i}+7\mathbf{j}$. Check with $l_{2}$ and $t=1$: $-\mathbf{i}+3\mathbf{j}+5\mathbf{i}+4\mathbf{j}=4\mathbf{i}+7\mathbf{j}$.",
          ans=r"$4\mathbf{i}+7\mathbf{j}$"),
        S("c", r"Find the cosine of the acute angle between the lines $l_{1}$ and $l_{2}$.", ["vector geometry (additional maths)", "scalar product"], "moyenne", 2,
          [("You use the direction vectors $\\mathbf{i}+3\\mathbf{j}$ and $5\\mathbf{i}+4\\mathbf{j}$ in $\\cos\\theta=\\dfrac{\\mathbf{d}_{1}\\cdot\\mathbf{d}_{2}}{|\\mathbf{d}_{1}||\\mathbf{d}_{2}|}$", 1), ("You obtain $\\dfrac{17}{\\sqrt{410}}\\approx0.84$", 1)],
          r"The angle between two lines is the angle between their direction vectors: $\cos\theta=\dfrac{\mathbf{d}_{1}\cdot\mathbf{d}_{2}}{|\mathbf{d}_{1}|\,|\mathbf{d}_{2}|}$.",
          r"$\mathbf{d}_{1}=\mathbf{i}+3\mathbf{j}$ and $\mathbf{d}_{2}=5\mathbf{i}+4\mathbf{j}$. $\mathbf{d}_{1}\cdot\mathbf{d}_{2}=1(5)+3(4)=17$, $|\mathbf{d}_{1}|=\sqrt{10}$ and $|\mathbf{d}_{2}|=\sqrt{41}$. So $\cos\theta=\dfrac{17}{\sqrt{10}\sqrt{41}}=\dfrac{17}{\sqrt{410}}\approx0.84$.",
          ans=r"$\dfrac{17}{\sqrt{410}}\approx0.84$"),
    ]))

    ex.append(E("8", G, 7, "", [
        S("i", r"(i) Given that $y=x^{2}\sqrt{1+2x}$, find $\dfrac{dy}{dx}$, simplifying your answer.", ["differentiation techniques (additional maths)"], "faible", 3,
          [("You use the product rule with $u=x^{2}$ and $v=(1+2x)^{\\frac{1}{2}}$", 1), ("You differentiate $v$ by the chain rule: $\\dfrac{dv}{dx}=(1+2x)^{-\\frac{1}{2}}$", 1), ("You combine and simplify to $\\dfrac{5x^{2}+2x}{\\sqrt{1+2x}}$", 1)],
          r"The product rule: $\dfrac{d}{dx}(uv)=u\dfrac{dv}{dx}+v\dfrac{du}{dx}$; the chain rule gives $\dfrac{d}{dx}(1+2x)^{\frac{1}{2}}=\dfrac{1}{2}(1+2x)^{-\frac{1}{2}}\times2$.",
          r"$u=x^{2}$, $\dfrac{du}{dx}=2x$; $v=(1+2x)^{\frac{1}{2}}$, $\dfrac{dv}{dx}=\dfrac{1}{2}(1+2x)^{-\frac{1}{2}}\times2=\dfrac{1}{\sqrt{1+2x}}$. $\dfrac{dy}{dx}=x^{2}\times\dfrac{1}{\sqrt{1+2x}}+\sqrt{1+2x}\times2x=\dfrac{x^{2}+2x(1+2x)}{\sqrt{1+2x}}=\dfrac{5x^{2}+2x}{\sqrt{1+2x}}$.",
          ans=r"$\dfrac{5x^{2}+2x}{\sqrt{1+2x}}$",
          piege=r"The derivative of the bracket $2$ is a factor of the chain rule: $\dfrac{d}{dx}(1+2x)^{\frac{1}{2}}=\dfrac{1}{2}(1+2x)^{-\frac{1}{2}}\times2$, not $\dfrac{1}{2}(1+2x)^{-\frac{1}{2}}$."),
        S("ii", r"(ii) Evaluate $\displaystyle\int_{1}^{4}\left(3\sqrt{x}+\dfrac{2}{x^{2}}\right)dx$.", ["integration and area"], "elevee", 4,
          [("You rewrite as powers: $3x^{\\frac{1}{2}}+2x^{-2}$", 1), ("You integrate: $2x^{\\frac{3}{2}}-\\dfrac{2}{x}$", 1), ("You substitute the limits $4$ and $1$ and subtract", 1), ("You obtain $\\dfrac{31}{2}$", 1)],
          r"Write roots and fractions as powers of $x$, integrate with $\int x^{n}dx=\dfrac{x^{n+1}}{n+1}$, then substitute the upper limit and subtract the value at the lower limit.",
          r"$\displaystyle\int_{1}^{4}\left(3x^{\frac{1}{2}}+2x^{-2}\right)dx=\Big[2x^{\frac{3}{2}}-2x^{-1}\Big]_{1}^{4}=\left(2\times8-\dfrac{2}{4}\right)-\left(2-2\right)=\dfrac{31}{2}-0=\dfrac{31}{2}$.",
          ans=r"$\dfrac{31}{2}$"),
    ]))
    return ex
