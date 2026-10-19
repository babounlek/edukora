"""Questions 26 a 50 de l'epreuve inedite GCE O Level Mathematics Paper 1 n.1 (voir generer_maths_p1.py)."""
from questions_maths_p1_a import Q


def questions():
    qs = []
    a = qs.append

    a(Q(26, ["coordinate geometry", "linear equations"], "faible",
        r"The gradient and the $y$-intercept of the line $2y+6x=8$ are respectively",
        r"$-3$ and $4$", [r"$3$ and $4$", r"$-6$ and $8$", r"$-3$ and $8$"],
        r"Rearrange the equation into the form $y=mx+c$: then $m$ is the gradient and $c$ is the $y$-intercept.",
        r"$2y=-6x+8$, so $y=-3x+4$. The gradient is $-3$ and the $y$-intercept is $4$.",
        r"$-6$ and $8$ are read before dividing by the coefficient of $y$. The term $6x$ also changes sign when it crosses the equals sign."))

    a(Q(27, ["graphs", "quadratic equations"], "moyenne",
        r"Figure 7 shows the graph of $y=x^{2}-2x-3$. The coordinates of the turning point are",
        r"$(1,\ -4)$", [r"$(-1,\ 0)$", r"$(3,\ 0)$", r"$(0,\ -3)$"],
        r"The turning point of a parabola lies on its axis of symmetry, which is midway between the two points where the curve meets the $x$-axis.",
        r"The curve cuts the $x$-axis at $x=-1$ and $x=3$, so the axis of symmetry is $x=\dfrac{-1+3}{2}=1$. At $x=1$, $y=1-2-3=-4$. The turning point, the lowest point of the curve, is $(1,\ -4)$.",
        r"$(-1,\ 0)$ and $(3,\ 0)$ are the $x$-intercepts and $(0,\ -3)$ is the $y$-intercept. None of them is the lowest point of the curve.",
        fig="parabole"))

    a(Q(28, ["algebraic expressions"], "moyenne",
        r"Factorising $x^{2}-5x-24$ gives",
        r"$(x-8)(x+3)$", [r"$(x+8)(x-3)$", r"$(x-6)(x+4)$", r"$(x-12)(x+2)$"],
        r"To factorise $x^{2}+bx+c$, find two numbers whose product is $c$ and whose sum is $b$.",
        r"We need two numbers with product $-24$ and sum $-5$: they are $-8$ and $3$. So $x^{2}-5x-24=(x-8)(x+3)$. Check: $(x-8)(x+3)=x^{2}+3x-8x-24$.",
        r"$(x+8)(x-3)$ has the right product but gives $+5x$ as the middle term. Always expand to check the sign of the middle term."))

    a(Q(29, ["algebraic expressions"], "faible",
        r"Given that $a=-3$ and $b=2$, the value of $a^{2}-2ab$ is",
        r"$21$", [r"$-3$", r"$3$", r"$-21$"],
        r"When substituting, put negative numbers in brackets, square before multiplying, and remember that subtracting a negative number means adding.",
        r"$a^{2}=(-3)^{2}=9$ and $2ab=2\times(-3)\times2=-12$. So $a^{2}-2ab=9-(-12)=9+12=21$.",
        r"$(-3)^{2}$ is $9$, not $-9$ (which would give $3$), and subtracting $-12$ adds $12$ (forgetting this gives $-3$)."))

    a(Q(30, ["linear equations"], "moyenne",
        r"Solving $\dfrac{x+1}{2}-\dfrac{x-2}{3}=2$ gives $x=$",
        r"$5$", [r"$-5$", r"$7$", r"$13$"],
        r"Multiply every term by the lowest common multiple of the denominators to clear the fractions, then collect the like terms.",
        r"Multiply each term by $6$: $3(x+1)-2(x-2)=12$. Expanding, $3x+3-2x+4=12$, so $x+7=12$ and $x=5$. Check: $\dfrac{6}{2}-\dfrac{3}{3}=3-1=2$.",
        r"The minus sign before the second fraction applies to the whole bracket: $-2(x-2)=-2x+4$. Writing $-2x-4$ leads to $x=13$, and forgetting to multiply the right-hand side by $6$ gives $-5$."))

    a(Q(31, ["laws of indices", "algebraic expressions"], "moyenne",
        r"Simplifying $\dfrac{(3a^{2}b)^{3}}{9a^{4}b}$ gives",
        r"$3a^{2}b^{2}$", [r"$a^{2}b^{2}$", r"$3a^{10}b^{2}$", r"$3a^{2}b^{3}$"],
        r"Raise every factor inside the bracket to the power outside, then divide by subtracting the powers of each base.",
        r"$(3a^{2}b)^{3}=27a^{6}b^{3}$. Then $\dfrac{27a^{6}b^{3}}{9a^{4}b}=3a^{6-4}b^{3-1}=3a^{2}b^{2}$.",
        r"$3^{3}=27$, not $9$ (using $9$ gives $a^{2}b^{2}$). When dividing, powers are subtracted: adding them gives $a^{10}$."))

    a(Q(32, ["change of subject"], "faible",
        r"Making $s$ the subject of the formula $v^{2}=u^{2}+2as$ gives $s=$",
        r"$\dfrac{v^{2}-u^{2}}{2a}$", [r"$\dfrac{v^{2}+u^{2}}{2a}$", r"$v^{2}-u^{2}-2a$", r"$\dfrac{(v-u)^{2}}{2a}$"],
        r"To change the subject, undo the operations around the new subject in reverse order, doing the same thing to both sides.",
        r"Subtract $u^{2}$ from both sides: $v^{2}-u^{2}=2as$. Divide both sides by $2a$: $s=\dfrac{v^{2}-u^{2}}{2a}$.",
        r"$v^{2}-u^{2}$ is not $(v-u)^{2}$. Also, $2a$ multiplies $s$, so it must be divided out, not subtracted."))

    a(Q(33, ["simultaneous equations"], "moyenne",
        r"The solution of the simultaneous equations $3x+2y=16$ and $x-y=2$ is",
        r"$x=4,\ y=2$", [r"$x=6,\ y=4$", r"$x=2,\ y=5$", r"$x=0,\ y=-2$"],
        r"Eliminate one unknown by substitution or by adding or subtracting multiples of the equations, solve for the other, then substitute back and check in both equations.",
        r"From $x-y=2$, $x=y+2$. Substituting in the first equation: $3(y+2)+2y=16$, so $5y+6=16$ and $y=2$. Then $x=4$. Check: $3(4)+2(2)=16$ and $4-2=2$.",
        r"$(6,\ 4)$ satisfies $x-y=2$ only, $(2,\ 5)$ satisfies $3x+2y=16$ only and $(0,\ -2)$ satisfies $x-y=2$ only. A solution must satisfy both equations.",
        r"Test each option in the equation that is easier to check, $x-y=2$, to remove wrong choices quickly."))

    a(Q(34, ["sequences and series"], "faible",
        r"The $20$th term of the sequence $3,\ 7,\ 11,\ 15,\ \dots$ is",
        r"$79$", [r"$83$", r"$80$", r"$77$"],
        r"In an arithmetic sequence the $n$th term is $a+(n-1)d$, where $a$ is the first term and $d$ is the common difference.",
        r"$a=3$ and $d=7-3=4$. So $T_{20}=3+(20-1)\times4=3+76=79$.",
        r"Using $n\times d$ instead of $(n-1)\times d$ gives $3+80=83$, which is the $21$st term."))

    a(Q(35, ["direct and inverse variation"], "moyenne",
        r"$y$ varies inversely as the square of $x$. Given that $y=9$ when $x=2$, the value of $y$ when $x=6$ is",
        r"$1$", [r"$3$", r"$27$", r"$81$"],
        r"The statement '$y$ varies inversely as the square of $x$' means $y=\dfrac{k}{x^{2}}$: find $k$ from the given pair of values, then substitute the new value of $x$.",
        r"$9=\dfrac{k}{2^{2}}$ gives $k=36$. When $x=6$, $y=\dfrac{36}{6^{2}}=\dfrac{36}{36}=1$.",
        r"Inverse variation with $x$ alone ($y=\dfrac{k}{x}$) gives $3$, and direct variation with $x^{2}$ gives $81$. The words 'inversely' and 'square' both matter."))

    a(Q(36, ["inequalities"], "faible",
        r"The inequality represented on the number line in Figure 8 is",
        r"$-2\leq x<3$", [r"$-2<x\leq3$", r"$-2\leq x\leq3$", r"$x\leq-2\ \text{or}\ x>3$"],
        r"On a number line, a solid dot means that the value is included ($\leq$ or $\geq$) and an open circle means that it is excluded ($<$ or $>$).",
        r"At $-2$ the dot is solid, so $-2$ is included: $-2\leq x$. At $3$ the circle is open, so $3$ is excluded: $x<3$. Together, $-2\leq x<3$.",
        r"Reading the two ends the wrong way round gives $-2<x\leq3$. Look at each end separately.",
        fig="droite"))

    a(Q(37, ["quadratic equations"], "moyenne",
        r"The solutions of $2x^{2}-5x-3=0$ are",
        r"$x=3$ or $x=-\dfrac{1}{2}$", [r"$x=-3$ or $x=\dfrac{1}{2}$", r"$x=3$ or $x=\dfrac{1}{2}$", r"$x=-3$ or $x=-\dfrac{1}{2}$"],
        r"Factorise the quadratic, set each factor equal to zero and solve each linear equation; then check the answers by substitution.",
        r"$2x^{2}-5x-3=(2x+1)(x-3)$, because $2x\times(-3)+1\times x=-5x$. Then $2x+1=0$ gives $x=-\dfrac{1}{2}$ and $x-3=0$ gives $x=3$. Check: $2(9)-15-3=0$.",
        r"The solution of a bracket has the opposite sign to the number inside it: $(x-3)$ gives $x=+3$."))

    a(Q(38, ["graph theory (networks)"], "faible",
        r"Figure 9 shows a network with $5$ vertices. The number of odd vertices (vertices of odd degree) is",
        r"$2$", [r"$0$", r"$3$", r"$4$"],
        r"The degree of a vertex is the number of arcs that meet at it, and a network can be traced without lifting the pencil only if it has $0$ or $2$ odd vertices.",
        r"The degrees are: $A$ has $2$ ($AB$, $AC$), $B$ has $4$ ($BA$, $BC$, $BD$, $BE$), $C$ has $3$ ($CA$, $CB$, $CE$), $D$ has $2$ ($DB$, $DE$) and $E$ has $3$ ($EB$, $EC$, $ED$). The odd vertices are $C$ and $E$, so there are $2$.",
        r"Count the arcs at each vertex, not the arcs in the whole network. The number of odd vertices in any network is always even, so $3$ cannot be right.",
        fig="reseau"))

    a(Q(39, ["trigonometry"], "faible",
        r"In Figure 10, triangle $PQR$ has a right angle at $Q$, with $PQ=8$ cm, $QR=15$ cm and $PR=17$ cm. The value of $\tan\theta$, where $\theta=\angle PRQ$, is",
        r"$\dfrac{8}{15}$", [r"$\dfrac{15}{8}$", r"$\dfrac{8}{17}$", r"$\dfrac{15}{17}$"],
        r"In a right-angled triangle, $\sin\theta=\dfrac{\text{opposite}}{\text{hypotenuse}}$, $\cos\theta=\dfrac{\text{adjacent}}{\text{hypotenuse}}$ and $\tan\theta=\dfrac{\text{opposite}}{\text{adjacent}}$.",
        r"Seen from the angle $\theta$ at $R$, the opposite side is $PQ=8$ and the adjacent side is $QR=15$. So $\tan\theta=\dfrac{8}{15}$.",
        r"$\dfrac{8}{17}$ is $\sin\theta$ and $\dfrac{15}{17}$ is $\cos\theta$, while $\dfrac{15}{8}$ is $\dfrac{1}{\tan\theta}$. Name the sides from the angle $\theta$ before choosing a ratio.",
        fig="triangle"))

    a(Q(40, ["trigonometry"], "moyenne",
        r"A ladder $6$ m long leans against a vertical wall and makes an angle of $65^\circ$ with the horizontal ground. The height reached on the wall, correct to $1$ decimal place, is",
        r"$5.4$ m", [r"$2.5$ m", r"$6.6$ m", r"$12.9$ m"],
        r"Choose the ratio that links the known side and the required side to the given angle, then rearrange to find the unknown.",
        r"The ladder is the hypotenuse and the height reached is opposite the $65^\circ$ angle, so $\sin65^\circ=\dfrac{h}{6}$. Hence $h=6\sin65^\circ=6\times0.9063=5.44\approx5.4$ m.",
        r"$6\cos65^\circ\approx2.5$ m is the distance from the foot of the ladder to the wall. $6\div\sin65^\circ\approx6.6$ m and $6\tan65^\circ\approx12.9$ m come from the wrong ratio.",
        r"The height can never exceed the length of the ladder, $6$ m, so $6.6$ and $12.9$ are ruled out immediately."))

    a(Q(41, ["bearings"], "faible",
        r"A boat sails from $P$ to $Q$ on a bearing of $072^\circ$, as shown in Figure 11. The bearing of $P$ from $Q$ is",
        r"$252^\circ$", [r"$108^\circ$", r"$162^\circ$", r"$288^\circ$"],
        r"A back bearing differs from the forward bearing by $180^\circ$: add $180^\circ$ when the bearing is less than $180^\circ$, and subtract $180^\circ$ otherwise.",
        r"The north lines at $P$ and $Q$ are parallel, so the angle between $QP$ and the line pointing south from $Q$ is also $72^\circ$ (alternate angles). Measured clockwise from north, the direction $QP$ is $180^\circ+72^\circ=252^\circ$.",
        r"$108^\circ=180^\circ-72^\circ$ and $288^\circ=360^\circ-72^\circ$ are common slips: a bearing is always measured clockwise from north.",
        r"Quick check: $P$ lies south-west of $Q$, so the bearing of $P$ from $Q$ must be between $180^\circ$ and $270^\circ$.",
        fig="bearing"))

    a(Q(42, ["vectors"], "moyenne",
        r"Given that $\mathbf{p}=\begin{pmatrix}3\\5\end{pmatrix}$ and $\mathbf{q}=\begin{pmatrix}-1\\2\end{pmatrix}$, the magnitude of $2\mathbf{p}+\mathbf{q}$ is",
        r"$13$", [r"$7$", r"$17$", r"$169$"],
        r"Combine the vectors component by component; the magnitude of $\begin{pmatrix}x\\y\end{pmatrix}$ is $\sqrt{x^{2}+y^{2}}$.",
        r"$2\mathbf{p}+\mathbf{q}=\begin{pmatrix}6\\10\end{pmatrix}+\begin{pmatrix}-1\\2\end{pmatrix}=\begin{pmatrix}5\\12\end{pmatrix}$. Its magnitude is $\sqrt{5^{2}+12^{2}}=\sqrt{169}=13$.",
        r"Adding the components gives $5+12=17$, which is not the magnitude, and $169$ is the value before taking the square root."))

    a(Q(43, ["vectors"], "faible",
        r"The points $A$ and $B$ have coordinates $(2,\ -3)$ and $(-4,\ 5)$. The column vector $\overrightarrow{AB}$ is",
        r"$\begin{pmatrix}-6\\8\end{pmatrix}$", [r"$\begin{pmatrix}6\\-8\end{pmatrix}$", r"$\begin{pmatrix}-2\\2\end{pmatrix}$", r"$\begin{pmatrix}-6\\-8\end{pmatrix}$"],
        r"$\overrightarrow{AB}=\mathbf{b}-\mathbf{a}$: subtract the coordinates of the starting point from those of the end point.",
        r"$\overrightarrow{AB}=\begin{pmatrix}-4-2\\5-(-3)\end{pmatrix}=\begin{pmatrix}-6\\8\end{pmatrix}$.",
        r"$\begin{pmatrix}6\\-8\end{pmatrix}$ is $\overrightarrow{BA}$, the vector in the opposite direction, and adding the coordinates gives $\begin{pmatrix}-2\\2\end{pmatrix}$."))

    a(Q(44, ["matrix operations"], "moyenne",
        r"Given $A=\begin{pmatrix}2&-1\\3&4\end{pmatrix}$ and $B=\begin{pmatrix}1&0\\-2&5\end{pmatrix}$, the product $AB$ is",
        r"$\begin{pmatrix}4&-5\\-5&20\end{pmatrix}$",
        [r"$\begin{pmatrix}2&-1\\11&22\end{pmatrix}$", r"$\begin{pmatrix}2&0\\-6&20\end{pmatrix}$", r"$\begin{pmatrix}3&-1\\1&9\end{pmatrix}$"],
        r"To multiply two matrices, multiply each row of the first by each column of the second and add the products; the order of the matrices matters.",
        r"Row 1 by column 1: $2(1)+(-1)(-2)=4$. Row 1 by column 2: $2(0)+(-1)(5)=-5$. Row 2 by column 1: $3(1)+4(-2)=-5$. Row 2 by column 2: $3(0)+4(5)=20$. So $AB=\begin{pmatrix}4&-5\\-5&20\end{pmatrix}$.",
        r"$BA$ is not equal to $AB$ in general: the first option is $BA$. Multiplying entry by entry, the second option, is not matrix multiplication, and the last option is $A+B$."))

    a(Q(45, ["matrix operations"], "elevee",
        r"The inverse of the matrix $M=\begin{pmatrix}4&3\\2&2\end{pmatrix}$ is",
        r"$\dfrac{1}{2}\begin{pmatrix}2&-3\\-2&4\end{pmatrix}$",
        [r"$\dfrac{1}{2}\begin{pmatrix}4&-3\\-2&2\end{pmatrix}$", r"$2\begin{pmatrix}2&-3\\-2&4\end{pmatrix}$", r"$\dfrac{1}{2}\begin{pmatrix}2&3\\2&4\end{pmatrix}$"],
        r"For $\begin{pmatrix}a&b\\c&d\end{pmatrix}$ the inverse is $\dfrac{1}{ad-bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}$: swap the entries of the main diagonal, change the signs of the other two entries and divide by the determinant.",
        r"The determinant is $4\times2-3\times2=2$. Swap $4$ and $2$, then change the signs of $3$ and $2$: $M^{-1}=\dfrac{1}{2}\begin{pmatrix}2&-3\\-2&4\end{pmatrix}$. Check the first entry of $MM^{-1}$: $\dfrac{1}{2}\left(4\times2+3\times(-2)\right)=1$.",
        r"Leaving the diagonal entries in place gives the first wrong option, multiplying by the determinant instead of dividing gives the second one, and forgetting the sign changes gives the last one.",
        r"After finding an inverse, multiply one row of $M$ by one column of your answer: the diagonal entries of the product must equal $1$."))

    a(Q(46, ["geometric transformations"], "moyenne",
        r"The point $A(2,\ 3)$ is reflected in the line $y=x$ and its image is then translated by the vector $\begin{pmatrix}-1\\4\end{pmatrix}$. The final image of $A$ is",
        r"$(2,\ 6)$", [r"$(1,\ 1)$", r"$(-3,\ 7)$", r"$(1,\ 7)$"],
        r"A reflection in the line $y=x$ swaps the coordinates, $(x,y)\to(y,x)$, and a translation adds the components of the vector to the coordinates; apply the transformations in the order given.",
        r"Reflection in $y=x$: $(2,\ 3)\to(3,\ 2)$. Translation by $\begin{pmatrix}-1\\4\end{pmatrix}$: $(3-1,\ 2+4)=(2,\ 6)$.",
        r"Reflecting in the $x$-axis or the $y$-axis instead of $y=x$ gives $(1,\ 1)$ or $(-3,\ 7)$, and skipping the reflection gives $(1,\ 7)$."))

    a(Q(47, ["statistics"], "moyenne",
        "The table shows the marks obtained by $20$ learners in a short test.\n\n"
        "| Mark | 1 | 2 | 3 | 4 | 5 |\n|---|---|---|---|---|---|\n| Number of learners | 2 | 5 | 8 | 4 | 1 |\n\n"
        "The mean mark is",
        r"$2.85$", [r"$3$", r"$11.4$", r"$57$"],
        r"The mean of a frequency table is $\dfrac{\sum fx}{\sum f}$: multiply each value by its frequency, add the results and divide by the total frequency.",
        r"$\sum f=2+5+8+4+1=20$ and $\sum fx=1(2)+2(5)+3(8)+4(4)+5(1)=2+10+24+16+5=57$. The mean is $\dfrac{57}{20}=2.85$.",
        r"$57$ is $\sum fx$ before dividing, and $\dfrac{57}{5}=11.4$ divides by the number of different marks instead of the number of learners.",
        r"Marks lie between $1$ and $5$, so their mean must lie between $1$ and $5$: this rules out $57$ and $11.4$ at once."))

    a(Q(48, ["statistics"], "moyenne",
        r"The bar chart in Figure 12 shows the number of brothers and sisters of each of $35$ learners. The median number of brothers and sisters is",
        r"$2$", [r"$1$", r"$3$", r"$8$"],
        r"The median is the middle value of the ordered data; with $n$ values it is the $\dfrac{n+1}{2}$th value, found from the cumulative frequencies.",
        r"The total is $4+10+8+9+4=35$, so the median is the $\dfrac{35+1}{2}=18$th value. The cumulative frequencies are $4$ (up to $0$), $14$ (up to $1$) and $22$ (up to $2$). The $18$th value falls in the group whose value is $2$.",
        r"The tallest bar gives the mode, $1$, not the median. The height of the middle bar, $8$, is a frequency and not a value of the data.",
        fig="barres"))

    a(Q(49, ["statistics"], "moyenne",
        r"In a pie chart showing the favourite sports of a group of learners, the sector for football measures $120^\circ$ and represents $48$ learners. The sector for volleyball measures $75^\circ$. The number of learners who chose volleyball is",
        r"$30$", [r"$10$", r"$36$", r"$144$"],
        r"In a pie chart the angle of a sector is proportional to its frequency, so one degree stands for the same number of learners in every sector.",
        r"$120^\circ$ stands for $48$ learners, so $1^\circ$ stands for $\dfrac{48}{120}=0.4$ learner. Volleyball: $75\times0.4=30$ learners.",
        r"$144$ is the total number of learners ($360\times0.4$). Taking $\dfrac{75}{360}$ of $48$ gives $10$, which applies the fraction to football instead of to the total."))

    a(Q(50, ["probability"], "elevee",
        r"A bag contains $5$ red beads and $3$ blue beads. Two beads are drawn at random, one after the other, without replacement. The probability that the two beads have the same colour is",
        r"$\dfrac{13}{28}$", [r"$\dfrac{15}{28}$", r"$\dfrac{17}{32}$", r"$\dfrac{5}{14}$"],
        r"For draws without replacement the probabilities of the second draw change; multiply along each branch of the tree and add the branches that give the required outcome.",
        r"Both red: $\dfrac{5}{8}\times\dfrac{4}{7}=\dfrac{20}{56}$. Both blue: $\dfrac{3}{8}\times\dfrac{2}{7}=\dfrac{6}{56}$. Same colour: $\dfrac{20+6}{56}=\dfrac{26}{56}=\dfrac{13}{28}$.",
        r"$\dfrac{5}{14}=\dfrac{20}{56}$ counts red-red only, $\dfrac{17}{32}$ comes from putting the first bead back, and $\dfrac{15}{28}$ is the probability of two different colours.",
        r"The probabilities of the event and its opposite must add up to $1$: $\dfrac{13}{28}+\dfrac{15}{28}=1$."))

    return qs
