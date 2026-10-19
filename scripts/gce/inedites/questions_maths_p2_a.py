"""Section A (questions 1 a 10) de l'epreuve inedite GCE O Level Mathematics Paper 2 n.1.

Structure : E(numero, groupe, points, intro, sous-questions). Chaque sous-question S(...) porte son barème exact
(`pts`), sa grille (`crit` : liste de (critere, points) dont la somme vaut `pts`), un rappel general (un paragraphe),
la resolution, la reponse finale `ans` (relue et recalculee par verifier_reponses_maths_p2.py) et, si utile, un piege et
un conseil. Les figures sont inserees par generer_maths_p2.py (cle `fig`, `fig_intro`).
"""


def S(num, text, themes, diff, pts, crit, rappel, sol, ans, piege=None, conseil=None, fig=None, groupe_local=""):
    assert abs(sum(p for _, p in crit) - pts) < 1e-9, (num, text[:40], sum(p for _, p in crit), pts)
    return dict(num=num, text=text, themes=themes, diff=diff, pts=pts, crit=crit, rappel=rappel, sol=sol, ans=ans,
                piege=piege, conseil=conseil, fig=fig, groupe_local=groupe_local)


def E(num, groupe, pts, intro, subs, fig_intro=None):
    assert abs(sum(s["pts"] for s in subs) - pts) < 1e-9, (num, sum(s["pts"] for s in subs), pts)
    return dict(num=num, groupe=groupe, pts=pts, intro=intro, subs=subs, fig_intro=fig_intro)


def section_a():
    A = "SECTION A"
    ex = []

    ex.append(E("1", A, 4, "", [S(
        "1", r"Evaluate $\left(1\dfrac{1}{2}\right)^{2}\div\dfrac{3}{8}$.",
        ["common fractions", "order of operations"], "faible", 4,
        [("You write $1\\dfrac{1}{2}$ as the improper fraction $\\dfrac{3}{2}$", 1), ("You square the fraction: $\\dfrac{9}{4}$", 1),
         ("You multiply by the reciprocal $\\dfrac{8}{3}$", 1), ("You simplify to the final value", 1)],
        r"A mixed number is first written as an improper fraction, and dividing by a fraction means multiplying by its reciprocal.",
        r"Write the mixed number as an improper fraction: $1\dfrac{1}{2}=\dfrac{3}{2}$. Square it: $\left(\dfrac{3}{2}\right)^{2}=\dfrac{9}{4}$. Dividing by $\dfrac{3}{8}$ is the same as multiplying by $\dfrac{8}{3}$, so $\dfrac{9}{4}\times\dfrac{8}{3}=\dfrac{72}{12}=6$.",
        r"$6$",
        piege=r"Squaring only the whole part, $1^{2}+\dfrac{1}{2}$, changes the number: the whole mixed number $\dfrac{3}{2}$ is squared.")]))

    ex.append(E("2", A, 5, r"Consider the expression $\dfrac{8^{2}\times2^{-3}}{4^{3}}$.", [
        S("a", r"Write $8^{2}$ and $4^{3}$ as powers of $2$.", ["laws of indices"], "faible", 2,
          [("You write $8=2^{3}$ and $4=2^{2}$", 1), ("You obtain $8^{2}=2^{6}$ and $4^{3}=2^{6}$", 1)],
          r"To combine powers, write every base as a power of the same prime number, then use $(a^{m})^{n}=a^{mn}$.",
          r"$8=2^{3}$, so $8^{2}=(2^{3})^{2}=2^{6}$. $4=2^{2}$, so $4^{3}=(2^{2})^{3}=2^{6}$.",
          r"$8^{2}=2^{6}$ and $4^{3}=2^{6}$"),
        S("b", r"Hence simplify the expression, leaving your answer as a power of $2$.", ["laws of indices"], "moyenne", 2,
          [("You combine the numerator: $2^{6}\\times2^{-3}=2^{3}$", 1), ("You divide: $2^{3}\\div2^{6}=2^{-3}$", 1)],
          r"When multiplying powers of the same base add the indices, and when dividing subtract them.",
          r"The numerator is $2^{6}\times2^{-3}=2^{6+(-3)}=2^{3}$. Then $\dfrac{2^{3}}{2^{6}}=2^{3-6}=2^{-3}$.",
          r"$2^{-3}$",
          piege=r"Subtract the indices in the right order: numerator minus denominator, $3-6=-3$, not $6-3$."),
        S("c", r"Write your answer to part b as a fraction in its simplest form.", ["laws of indices"], "faible", 1,
          [("You use $a^{-n}=\\dfrac{1}{a^{n}}$ to obtain $\\dfrac{1}{8}$", 1)],
          r"A negative index means the reciprocal: $a^{-n}=\dfrac{1}{a^{n}}$.",
          r"$2^{-3}=\dfrac{1}{2^{3}}=\dfrac{1}{8}$.", r"$\dfrac{1}{8}$"),
    ]))

    ex.append(E("3", A, 4, "", [S(
        "1", r"Make $l$ the subject of the formula $T=2\pi\sqrt{\dfrac{l}{g}}$.",
        ["change of subject"], "moyenne", 4,
        [("You divide both sides by $2\\pi$", 1), ("You square both sides", 1), ("You multiply both sides by $g$", 1),
         ("You write the final formula for $l$", 1)],
        r"To change the subject, undo the operations around the new subject in reverse order: divide, then remove the root by squaring, then multiply.",
        r"Divide both sides by $2\pi$: $\dfrac{T}{2\pi}=\sqrt{\dfrac{l}{g}}$. Square both sides: $\dfrac{T^{2}}{4\pi^{2}}=\dfrac{l}{g}$. Multiply both sides by $g$: $l=\dfrac{gT^{2}}{4\pi^{2}}$.",
        r"$l=\dfrac{gT^{2}}{4\pi^{2}}$",
        piege=r"When squaring $\dfrac{T}{2\pi}$ the factor $2\pi$ is squared too: $(2\pi)^{2}=4\pi^{2}$, not $2\pi^{2}$.")]))

    ex.append(E("4", A, 5,
                r"The universal set is $\xi=\{x:\ x\text{ is an integer},\ 1\leq x\leq12\}$. The set $A$ is the set of multiples of $3$ and the set $B$ is the set of factors of $12$.",
                [S("a", r"List the elements of $A$.", ["set theory"], "faible", 1, [("You list $3,\\ 6,\\ 9,\\ 12$", 1)],
                   r"Multiples of $3$ are found by counting in threes, staying inside the universal set.",
                   r"Counting in threes up to $12$: $A=\{3,\ 6,\ 9,\ 12\}$.", r"$A=\{3,\ 6,\ 9,\ 12\}$"),
                 S("b", r"List the elements of $B$.", ["set theory"], "faible", 1, [("You list all six factors of $12$", 1)],
                   r"The factors of a number are all the whole numbers that divide it exactly, found in pairs.",
                   r"$12=1\times12=2\times6=3\times4$, so $B=\{1,\ 2,\ 3,\ 4,\ 6,\ 12\}$.", r"$B=\{1,\ 2,\ 3,\ 4,\ 6,\ 12\}$"),
                 S("c", r"Find $A\cap B$.", ["set theory"], "faible", 1, [("You keep only the elements found in both sets", 1)],
                   r"$A\cap B$ contains the elements that belong to both $A$ and $B$.",
                   r"The elements of $A$ that are also factors of $12$ are $3$, $6$ and $12$.", r"$A\cap B=\{3,\ 6,\ 12\}$"),
                 S("d", r"Find $A'\cap B$.", ["set theory"], "faible", 1, [("You remove from $B$ the elements of $A$", 1)],
                   r"$A'\cap B$ contains the elements of $B$ that are not in $A$.",
                   r"Remove $3$, $6$ and $12$ from $B$: the elements left are $1$, $2$ and $4$.", r"$A'\cap B=\{1,\ 2,\ 4\}$",
                   piege=r"$A'$ is the complement of $A$ in $\xi$: it is not the same as $B\cap A$."),
                 S("e", r"Find $n(A\cup B)$.", ["set theory"], "faible", 1, [("You list $A\\cup B$ without repeating $3$, $6$, $12$ and count $7$", 1)],
                   r"$A\cup B$ contains every element of $A$ or $B$, each counted once.",
                   r"$A\cup B=\{1,\ 2,\ 3,\ 4,\ 6,\ 9,\ 12\}$, which has $7$ elements. Check: $n(A)+n(B)-n(A\cap B)=4+6-3=7$.",
                   r"$n(A\cup B)=7$")]))

    ex.append(E("5", A, 5, r"Given that $\begin{pmatrix}x&2\\3&y\end{pmatrix}+\begin{pmatrix}1&-4\\2&5\end{pmatrix}=\begin{pmatrix}6&-2\\5&9\end{pmatrix}$.", [
        S("a", r"Find the values of $x$ and $y$.", ["matrix operations"], "faible", 3,
          [("You add the matrices entry by entry on the left-hand side", 1), ("You write $x+1=6$ and $y+5=9$", 1), ("You obtain $x=5$ and $y=4$", 1)],
          r"Two matrices are equal when their corresponding entries are equal; matrices of the same order are added entry by entry.",
          r"The left-hand side is $\begin{pmatrix}x+1&-2\\5&y+5\end{pmatrix}$. Equating entries: $x+1=6$ so $x=5$, and $y+5=9$ so $y=4$. The other two entries, $-2$ and $5$, already match.",
          r"$x=5,\ y=4$"),
        S("b", r"Hence find the determinant of the matrix $\begin{pmatrix}x&2\\3&y\end{pmatrix}$.", ["matrix operations"], "moyenne", 2,
          [("You write $\\det=xy-2\\times3$ with $x=5$ and $y=4$", 1), ("You obtain $14$", 1)],
          r"The determinant of $\begin{pmatrix}a&b\\c&d\end{pmatrix}$ is $ad-bc$.",
          r"With $x=5$ and $y=4$ the matrix is $\begin{pmatrix}5&2\\3&4\end{pmatrix}$, so the determinant is $5\times4-2\times3=20-6=14$.",
          r"$14$",
          piege=r"The determinant is the product of the main diagonal minus the product of the other diagonal, not the sum."),
    ]))

    ex.append(E("6", A, 5, "Figure 1 shows a network of four towns $W$, $X$, $Y$ and $Z$ joined by roads. Use it to answer the questions below.", [
        S("a", r"State the number of vertices.", ["graph theory (networks)"], "faible", 1, [("You count the four towns", 1)],
          r"In a network the vertices (nodes) are the points where arcs meet.", r"The vertices are $W$, $X$, $Y$ and $Z$.", r"$4$"),
        S("b", r"State the number of arcs.", ["graph theory (networks)"], "faible", 1, [("You count both arcs between $W$ and $X$: six arcs in all", 1)],
          r"Every road is one arc, and two roads between the same pair of towns count as two arcs.",
          r"$WX$ has two arcs, and $XY$, $YZ$, $ZW$ and $XZ$ have one arc each: $2+4=6$.", r"$6$"),
        S("c", r"Use Euler's formula to find the number of regions, including the outer region.", ["graph theory (networks)"], "moyenne", 1,
          [("You substitute in $V-E+R=2$ and obtain $R=4$", 1)],
          r"For a connected network drawn without crossings, $V-E+R=2$.",
          r"$4-6+R=2$ gives $R=4$. In the figure: the narrow region between the two arcs $WX$, the triangle $WXZ$, the triangle $XYZ$ and the outer region.",
          r"$4$"),
        S("d", r"State the number of even vertices.", ["graph theory (networks)"], "faible", 1, [("You find the degrees $3,\\ 4,\\ 2,\\ 3$ and state $2$", 1)],
          r"The degree of a vertex is the number of arcs that meet there; it is even when this number is even.",
          r"Degrees: $W$ has $3$ (two arcs to $X$ and one to $Z$), $X$ has $4$, $Y$ has $2$ and $Z$ has $3$. The even vertices are $X$ and $Y$.",
          r"$2$"),
        S("e", r"State, giving a reason, whether the network is traversable.", ["graph theory (networks)"], "faible", 1,
          [("You say it is traversable because exactly two vertices, $W$ and $Z$, are odd", 1)],
          r"A network is traversable if it has $0$ or $2$ odd vertices; with $2$ odd vertices the route starts at one and ends at the other.",
          r"The odd vertices are $W$ and $Z$: there are exactly two. The network is traversable, with a route that starts at $W$ and ends at $Z$.",
          r"Traversable: exactly two odd vertices ($W$ and $Z$)"),
    ], fig_intro="reseau"))

    ex.append(E("7", A, 4, r"$O$ is the origin, $\overrightarrow{OA}=\mathbf{a}$ and $\overrightarrow{OB}=\mathbf{b}$. The point $C$ lies on $AB$ such that $AC:CB=1:2$.", [
        S("a", r"Express $\overrightarrow{AB}$ in terms of $\mathbf{a}$ and $\mathbf{b}$.", ["vectors"], "faible", 1,
          [("You write $\\overrightarrow{AB}=\\mathbf{b}-\\mathbf{a}$", 1)],
          r"$\overrightarrow{AB}=\overrightarrow{AO}+\overrightarrow{OB}=\mathbf{b}-\mathbf{a}$: go from $A$ to $O$, then from $O$ to $B$.",
          r"$\overrightarrow{AB}=\overrightarrow{AO}+\overrightarrow{OB}=-\mathbf{a}+\mathbf{b}=\mathbf{b}-\mathbf{a}$.", r"$\overrightarrow{AB}=\mathbf{b}-\mathbf{a}$"),
        S("b", r"Express $\overrightarrow{AC}$ in terms of $\mathbf{a}$ and $\mathbf{b}$.", ["vectors"], "moyenne", 1,
          [("You use $AC=\\dfrac{1}{3}AB$ to write $\\dfrac{1}{3}(\\mathbf{b}-\\mathbf{a})$", 1)],
          r"If $AC:CB=m:n$ then $AC=\dfrac{m}{m+n}AB$.",
          r"$AC:CB=1:2$, so $AC$ is $\dfrac{1}{1+2}=\dfrac{1}{3}$ of $AB$. Hence $\overrightarrow{AC}=\dfrac{1}{3}(\mathbf{b}-\mathbf{a})$.",
          r"$\overrightarrow{AC}=\dfrac{1}{3}(\mathbf{b}-\mathbf{a})$",
          piege=r"$\dfrac{1}{3}$, not $\dfrac{1}{2}$: the ratio $1:2$ has three parts in all."),
        S("c", r"Hence express $\overrightarrow{OC}$ in terms of $\mathbf{a}$ and $\mathbf{b}$, in its simplest form.", ["vectors"], "moyenne", 2,
          [("You write $\\overrightarrow{OC}=\\overrightarrow{OA}+\\overrightarrow{AC}$", 1), ("You simplify to $\\dfrac{1}{3}(2\\mathbf{a}+\\mathbf{b})$", 1)],
          r"A position vector is reached by a path from the origin: $\overrightarrow{OC}=\overrightarrow{OA}+\overrightarrow{AC}$.",
          r"$\overrightarrow{OC}=\mathbf{a}+\dfrac{1}{3}(\mathbf{b}-\mathbf{a})=\dfrac{3\mathbf{a}+\mathbf{b}-\mathbf{a}}{3}=\dfrac{2\mathbf{a}+\mathbf{b}}{3}$.",
          r"$\overrightarrow{OC}=\dfrac{1}{3}(2\mathbf{a}+\mathbf{b})$"),
    ]))

    ex.append(E("8", A, 4, "Three pens and two notebooks cost $1\\,450$ FCFA. Two pens and five notebooks cost $2\\,250$ FCFA. Let $p$ be the price of a pen and $n$ the price of a notebook, both in FCFA.", [
        S("a", r"Write down two equations in $p$ and $n$.", ["simultaneous equations"], "faible", 2,
          [("You write $3p+2n=1\\,450$", 1), ("You write $2p+5n=2\\,250$", 1)],
          r"Translate each sentence into an equation: the number of items times their price, added, equals the total cost.",
          r"Three pens and two notebooks: $3p+2n=1\,450$. Two pens and five notebooks: $2p+5n=2\,250$.",
          r"$3p+2n=1\,450$ and $2p+5n=2\,250$"),
        S("b", r"Solve the equations to find the price of a pen and the price of a notebook.", ["simultaneous equations"], "moyenne", 2,
          [("You eliminate one unknown correctly", 1), ("You find $p=250$ and $n=350$ FCFA", 1)],
          r"Multiply the equations so that one unknown has the same coefficient, subtract, solve for the other unknown and substitute back.",
          r"Multiply the first equation by $5$ and the second by $2$: $15p+10n=7\,250$ and $4p+10n=4\,500$. Subtract: $11p=2\,750$, so $p=250$. Then $3(250)+2n=1\,450$ gives $2n=700$, so $n=350$. Check: $2(250)+5(350)=500+1\,750=2\,250$.",
          r"A pen costs $250$ FCFA and a notebook costs $350$ FCFA",
          conseil=r"Always check the second equation: it was not used to find $n$."),
    ]))

    ex.append(E("9", A, 4, "", [
        S("a", r"Solve the inequality $3(x-2)\geq5x+4$.", ["inequalities"], "moyenne", 3,
          [("You expand: $3x-6\\geq5x+4$", 1), ("You collect the terms: $-2x\\geq10$", 1), ("You divide by $-2$ and reverse the sign: $x\\leq-5$", 1)],
          r"Solve an inequality like an equation, but reverse the inequality sign when multiplying or dividing by a negative number.",
          r"Expand: $3x-6\geq5x+4$. Subtract $5x$ and add $6$: $-2x\geq10$. Divide by $-2$ and reverse the sign: $x\leq-5$.",
          r"$x\leq-5$",
          piege=r"Dividing by $-2$ reverses the sign: $x\geq-5$ is the most common wrong answer."),
        S("b", r"Show the solution on a number line.", ["inequalities"], "faible", 1,
          [("You draw a solid dot at $-5$ and a line going to the left", 1)],
          r"A solid dot shows that the end value is included ($\leq$ or $\geq$), and the line goes towards the values that satisfy the inequality.",
          r"The values $x\leq-5$ include $-5$ itself (solid dot) and all the numbers to its left. See the figure below.",
          r"Solid dot at $-5$, line towards the left", fig="droite"),
    ]))

    ex.append(E("10", A, 5, "A card is chosen at random from $20$ cards numbered $1$ to $20$. Find the probability that the number on the card is", [
        S("a", r"a multiple of $4$.", ["probability"], "faible", 1, [("You find $5$ favourable cards and write $\\dfrac{5}{20}=\\dfrac{1}{4}$", 1)],
          r"Probability $=\dfrac{\text{number of favourable outcomes}}{\text{total number of outcomes}}$.",
          r"The multiples of $4$ are $4,\ 8,\ 12,\ 16,\ 20$: $5$ cards. $P=\dfrac{5}{20}=\dfrac{1}{4}$.", r"$\dfrac{1}{4}$"),
        S("b", r"a prime number.", ["probability"], "faible", 2,
          [("You list the primes $2,\\ 3,\\ 5,\\ 7,\\ 11,\\ 13,\\ 17,\\ 19$", 1), ("You write $\\dfrac{8}{20}=\\dfrac{2}{5}$", 1)],
          r"A prime number has exactly two factors, $1$ and itself; $1$ is not prime.",
          r"The primes up to $20$ are $2,\ 3,\ 5,\ 7,\ 11,\ 13,\ 17,\ 19$: $8$ cards. $P=\dfrac{8}{20}=\dfrac{2}{5}$.", r"$\dfrac{2}{5}$",
          piege=r"$1$ is not a prime number, and $2$ is: do not leave out the only even prime."),
        S("c", r"not a perfect square.", ["probability"], "faible", 2,
          [("You list the squares $1,\\ 4,\\ 9,\\ 16$", 1), ("You write $1-\\dfrac{4}{20}=\\dfrac{4}{5}$", 1)],
          r"$P(\text{not }A)=1-P(A)$: it is often quicker to count the cards that do not qualify.",
          r"The perfect squares are $1,\ 4,\ 9,\ 16$: $4$ cards, so $P(\text{square})=\dfrac{4}{20}=\dfrac{1}{5}$. Then $P(\text{not a square})=1-\dfrac{1}{5}=\dfrac{4}{5}$.",
          r"$\dfrac{4}{5}$"),
    ]))

    return ex
