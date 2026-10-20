r"""Questions 26 a 50 de l'epreuve inedite GCE O Level Additional Mathematics Paper 1 n.1 (voir generer_addmaths_p1.py).

Inequations, fonctions, matrices, groupes, vecteurs, derivation et integration. Chaines BRUTES (r"...").
"""
from questions_addmaths_p1_a import Q


def questions():
    qs = []
    a = qs.append

    a(Q(26, ["coordinate geometry of straight lines"], "moyenne",
        r"The shortest distance from the point $(3,1)$ to the line $3x+4y-20=0$ is",
        r"$\dfrac{7}{5}$", [r"$7$", r"$\dfrac{7}{25}$", r"$\dfrac{33}{5}$"],
        r"The perpendicular distance from $(x_{1},y_{1})$ to the line $ax+by+c=0$ is $\dfrac{|ax_{1}+by_{1}+c|}{\sqrt{a^{2}+b^{2}}}$.",
        r"$\dfrac{|3(3)+4(1)-20|}{\sqrt{3^{2}+4^{2}}}=\dfrac{|-7|}{5}=\dfrac{7}{5}$.",
        r"The denominator is $\sqrt{a^{2}+b^{2}}=5$, not $a^{2}+b^{2}=25$. $\dfrac{33}{5}$ comes from the sign slip $9+4+20$."))

    a(Q(27, ["linear and quadratic inequalities"], "faible",
        r"The solution of the double inequality $-3\leq2x-1<7$ is",
        r"$-1\leq x<4$", [r"$-2\leq x<3$", r"$-1<x\leq4$", r"$-2<x\leq3$"],
        r"Do the same operation on all three parts of a double inequality. Adding to or dividing by a positive number keeps the direction of the signs.",
        r"Add $1$ to each part: $-2\leq2x<8$. Divide by $2$: $-1\leq x<4$.",
        r"The signs stay where they are: the lower bound keeps $\leq$ and the upper bound keeps $<$."))

    a(Q(28, ["linear and quadratic inequalities"], "faible",
        r"The solution of the inequality $x^{2}-x-6<0$ is",
        r"$-2<x<3$", [r"$x<-2$ or $x>3$", r"$-3<x<2$", r"$x<-3$ or $x>2$"],
        r"Factorise to find the critical values, then decide from the shape of the parabola: $(x-p)(x-q)<0$ between the roots when the coefficient of $x^{2}$ is positive.",
        r"$x^{2}-x-6=(x-3)(x+2)$, with roots $-2$ and $3$. The parabola opens upwards, so the expression is negative between the roots: $-2<x<3$.",
        r"$x<-2$ or $x>3$ is the solution of $x^{2}-x-6>0$."))

    a(Q(29, ["modulus functions and inequalities"], "moyenne",
        r"The equation $|3x-2|=7$ has the solutions",
        r"$3$ and $-\dfrac{5}{3}$", [r"$3$ and $\dfrac{5}{3}$", r"$-3$ and $\dfrac{5}{3}$", r"$-3$ and $-\dfrac{5}{3}$"],
        r"$|A|=k$ with $k>0$ means $A=k$ or $A=-k$: solve both equations.",
        r"$3x-2=7$ gives $x=3$. $3x-2=-7$ gives $3x=-5$, so $x=-\dfrac{5}{3}$.",
        r"Check both values in $|3x-2|$: $|3(3)-2|=7$ and $\left|3\left(-\dfrac{5}{3}\right)-2\right|=|-7|=7$."))

    a(Q(30, ["linear programming and inequality regions"], "faible",
        r"A trader buys $x$ chairs at $8000$ FCFA each and $y$ tables at $20000$ FCFA each. She spends at most $160000$ FCFA. This is represented by the inequality",
        r"$2x+5y\leq40$", [r"$2x+5y\geq40$", r"$5x+2y\leq40$", r"$2x+5y<40$"],
        r"“At most” means $\leq$. Write the total cost as an inequality, then divide by a common factor.",
        r"The total cost is $8000x+20000y\leq160000$. Dividing every term by $4000$: $2x+5y\leq40$.",
        r"“At most” includes the case where she spends exactly $160000$ FCFA, so the sign is $\leq$ and not $<$."))

    a(Q(31, ["linear programming and inequality regions"], "moyenne",
        r"The shaded region $R$ in {FIG} is bounded by the lines $x=1$, $y=4$ and $y=x$, and it includes its boundaries. Which set of inequalities defines $R$?",
        r"$x\geq1,\ y\leq4,\ y\geq x$", [r"$x\leq1,\ y\leq4,\ y\geq x$", r"$x\geq1,\ y\geq4,\ y\leq x$", r"$x\geq1,\ y\leq4,\ y\leq x$"],
        r"To test an inequality, take a point inside the shaded region and check that it satisfies the inequality.",
        r"Take the point $(2,3)$ inside $R$. It lies to the right of $x=1$ ($x\geq1$), below $y=4$ ($y\leq4$) and above the line $y=x$, since $3>2$ ($y\geq x$). All three signs are confirmed.",
        r"Above the line $y=x$ means $y\geq x$, not $y\leq x$: test a point to be sure.",
        fig="region"))

    a(Q(32, ["composite and inverse functions"], "faible",
        r"The functions $f$ and $g$ are defined by $f(x)=2x-1$ and $g(x)=x^{2}+3$. The value of $gf(2)$ is",
        r"$12$", [r"$13$", r"$8$", r"$9$"],
        r"$gf(x)$ means $g(f(x))$: apply $f$ first, then $g$.",
        r"$f(2)=2(2)-1=3$ and $g(3)=3^{2}+3=12$.",
        r"$13$ is $fg(2)=f(7)$: the order of the functions is reversed."))

    a(Q(33, ["composite and inverse functions"], "faible",
        r"The function $f$ is defined by $f(x)=\dfrac{2x-3}{5}$. The value of $f^{-1}(3)$ is",
        r"$9$", [r"$\dfrac{3}{5}$", r"$6$", r"$15$"],
        r"$f^{-1}(3)$ is the value of $x$ for which $f(x)=3$.",
        r"Solve $\dfrac{2x-3}{5}=3$: $2x-3=15$, so $2x=18$ and $x=9$. Check: $f(9)=\dfrac{18-3}{5}=3$.",
        r"$\dfrac{3}{5}=f(3)$ is the image of $3$, not the number whose image is $3$."))

    a(Q(34, ["piecewise defined functions"], "faible",
        r"The function $f$ is defined by $f(x)=\begin{cases}x^{2}-1,&x\geq2\\3-x,&x<2\end{cases}$. The value of $f(-1)+f(3)$ is",
        r"$12$", [r"$10$", r"$4$", r"$14$"],
        r"For a piecewise function, first decide which rule applies to the given value of $x$.",
        r"$-1<2$, so $f(-1)=3-(-1)=4$. $3\geq2$, so $f(3)=3^{2}-1=8$. The sum is $4+8=12$.",
        r"Using $x^{2}-1$ for $x=-1$ gives $0$, which is wrong because $-1$ is not in the range $x\geq2$."))

    a(Q(35, ["matrices and inverses (additional maths)"], "faible",
        r"The determinant of the matrix $\begin{pmatrix}3&-2\\4&5\end{pmatrix}$ is",
        r"$23$", [r"$7$", r"$-23$", r"$20$"],
        r"The determinant of $\begin{pmatrix}a&b\\c&d\end{pmatrix}$ is $ad-bc$.",
        r"$3\times5-(-2)\times4=15+8=23$.",
        r"Subtracting a negative product adds it: $-(-8)=+8$. $7$ comes from $15-8$."))

    a(Q(36, ["matrices and inverses (additional maths)"], "faible",
        r"The matrix $\begin{pmatrix}k&3\\2&4\end{pmatrix}$ has no inverse. The value of $k$ is",
        r"$\dfrac{3}{2}$", [r"$\dfrac{2}{3}$", r"$6$", r"$-\dfrac{3}{2}$"],
        r"A square matrix has an inverse only if its determinant is not zero. A matrix with determinant $0$ is called singular and has no inverse.",
        r"The determinant is $k\times4-3\times2=4k-6$. There is no inverse when $4k-6=0$, so $k=\dfrac{6}{4}=\dfrac{3}{2}$.",
        r"Set the determinant equal to zero, not the matrix: $4k-6=0$ gives $k=\dfrac{3}{2}$, and $\dfrac{2}{3}$ comes from inverting the fraction."))
    a(Q(37, ["matrix transformations (additional maths)"], "faible",
        r"The image of the point $(2,-1)$ under the transformation represented by the matrix $\begin{pmatrix}1&2\\3&-1\end{pmatrix}$ is",
        r"$(0,7)$", [r"$(7,0)$", r"$(0,5)$", r"$(4,7)$"],
        r"The image of $(x,y)$ is found by multiplying the matrix by the column vector $\begin{pmatrix}x\\y\end{pmatrix}$: each row of the matrix gives one coordinate.",
        r"$\begin{pmatrix}1&2\\3&-1\end{pmatrix}\begin{pmatrix}2\\-1\end{pmatrix}=\begin{pmatrix}1(2)+2(-1)\\3(2)+(-1)(-1)\end{pmatrix}=\begin{pmatrix}0\\7\end{pmatrix}$.",
        r"The first row gives the $x$-coordinate of the image: $(7,0)$ has the rows in the wrong order."))

    a(Q(38, ["binary operations and groups"], "faible",
        r"A binary operation $*$ is defined on the real numbers by $x*y=x+y-xy$. The value of $3*2$ is",
        r"$-1$", [r"$1$", r"$11$", r"$5$"],
        r"To evaluate a binary operation, replace $x$ and $y$ by the given numbers in the rule.",
        r"$3*2=3+2-(3)(2)=5-6=-1$.",
        r"$xy$ means $x\times y=6$, and it is subtracted: $5-6=-1$."))

    a(Q(39, ["binary operations and groups"], "faible",
        r"A binary operation $*$ is defined by $x*y=(3x+y)\pmod{5}$. The value of $4*3$ is",
        r"$0$", [r"$15$", r"$3$", r"$2$"],
        r"A result “modulo $n$” is the remainder on division by $n$.",
        r"$4*3=(3\times4+3)\pmod{5}=15\pmod{5}=0$, because $15=3\times5$.",
        r"$15$ is the value before the remainder is taken."))

    a(Q(40, ["binary operations and groups"], "elevee",
        "The set $G=\\{1,3,5,7\\}$ forms a group under multiplication modulo $8$, with the table below.\n\n"
        "| $\\times_{8}$ | 1 | 3 | 5 | 7 |\n|---|---|---|---|---|\n| **1** | 1 | 3 | 5 | 7 |\n| **3** | 3 | 1 | 7 | 5 |\n"
        "| **5** | 5 | 7 | 1 | 3 |\n| **7** | 7 | 5 | 3 | 1 |\n\nA subgroup of $G$ is",
        r"$\{1,3\}$", [r"$\{3,5\}$", r"$\{5,7\}$", r"$\{3,7\}$"],
        r"A subgroup is a subset that is itself a group under the same operation: it must contain the identity, be closed under the operation and contain the inverse of each of its elements.",
        r"The identity of $G$ is $1$, and a subgroup must contain it. Only $\{1,3\}$ contains $1$. It is closed ($3\times_{8}3=1$) and each element is its own inverse. The other three sets do not contain the identity; for example $3\times_{8}5=7\notin\{3,5\}$.",
        r"A set can look closed and still fail to be a subgroup: always check that the identity $1$ belongs to it."))

    a(Q(41, ["vector geometry (additional maths)"], "faible",
        r"The points $A$ and $B$ have position vectors $2\mathbf{i}+7\mathbf{j}$ and $6\mathbf{i}+\mathbf{j}$ respectively. The vector $\overrightarrow{AB}$ is",
        r"$4\mathbf{i}-6\mathbf{j}$", [r"$-4\mathbf{i}+6\mathbf{j}$", r"$8\mathbf{i}+8\mathbf{j}$", r"$4\mathbf{i}+6\mathbf{j}$"],
        r"$\overrightarrow{AB}=\mathbf{b}-\mathbf{a}$: the position vector of the end point minus that of the start point.",
        r"$\overrightarrow{AB}=(6\mathbf{i}+\mathbf{j})-(2\mathbf{i}+7\mathbf{j})=4\mathbf{i}-6\mathbf{j}$.",
        r"$-4\mathbf{i}+6\mathbf{j}$ is $\overrightarrow{BA}$, and $8\mathbf{i}+8\mathbf{j}$ is the sum of the two position vectors."))

    a(Q(42, ["vector geometry (additional maths)"], "moyenne",
        r"A line has vector equation $\mathbf{r}=2\mathbf{i}-\mathbf{j}+t(5\mathbf{i}+3\mathbf{j})$. The position vector of the point on the line for which $t=2$ is",
        r"$12\mathbf{i}+5\mathbf{j}$", [r"$7\mathbf{i}+2\mathbf{j}$", r"$10\mathbf{i}+6\mathbf{j}$", r"$12\mathbf{i}+6\mathbf{j}$"],
        r"In $\mathbf{r}=\mathbf{a}+t\mathbf{d}$, $\mathbf{a}$ is a point on the line and $\mathbf{d}$ is the direction vector. A value of $t$ gives one point.",
        r"$\mathbf{r}=2\mathbf{i}-\mathbf{j}+2(5\mathbf{i}+3\mathbf{j})=(2+10)\mathbf{i}+(-1+6)\mathbf{j}=12\mathbf{i}+5\mathbf{j}$.",
        r"The $\mathbf{j}$-component is $-1+6=5$, not $6$: do not forget the starting point $2\mathbf{i}-\mathbf{j}$."))

    a(Q(43, ["scalar product"], "faible",
        r"For which value of $p$ are the vectors $\mathbf{a}=2\mathbf{i}+3\mathbf{j}$ and $\mathbf{b}=6\mathbf{i}+p\mathbf{j}$ at right angles to each other?",
        r"$-4$", [r"$4$", r"$-18$", r"$9$"],
        r"Two non-zero vectors are perpendicular when their scalar product is zero: $(a_{1}\mathbf{i}+a_{2}\mathbf{j})\cdot(b_{1}\mathbf{i}+b_{2}\mathbf{j})=a_{1}b_{1}+a_{2}b_{2}=0$.",
        r"$\mathbf{a}\cdot\mathbf{b}=2(6)+3p=12+3p=0$, so $p=-4$.",
        r"$12+3p=0$ gives $3p=-12$: the $12$ moves to the other side with a minus sign."))

    a(Q(44, ["derivatives of standard functions"], "moyenne",
        r"The derivative of $\dfrac{3}{x^{2}}$ with respect to $x$ is",
        r"$-\dfrac{6}{x^{3}}$", [r"$\dfrac{6}{x^{3}}$", r"$-\dfrac{3}{x^{3}}$", r"$\dfrac{3}{2x}$"],
        r"Write the expression as a power of $x$ and use $\dfrac{d}{dx}(x^{n})=nx^{n-1}$.",
        r"$\dfrac{3}{x^{2}}=3x^{-2}$, so $\dfrac{d}{dx}(3x^{-2})=3(-2)x^{-3}=-6x^{-3}=-\dfrac{6}{x^{3}}$.",
        r"The new power is $-2-1=-3$ and the coefficient is multiplied by the old power $-2$: $-\dfrac{3}{x^{3}}$ forgets to multiply."))

    a(Q(45, ["differentiation techniques (additional maths)"], "moyenne",
        r"If $y=(2x+1)^{4}$, then $\dfrac{dy}{dx}=$",
        r"$8(2x+1)^{3}$", [r"$4(2x+1)^{3}$", r"$2(2x+1)^{3}$", r"$(2x+1)^{3}$"],
        r"The chain rule: $\dfrac{d}{dx}\left[f(x)\right]^{n}=n\left[f(x)\right]^{n-1}\times f'(x)$.",
        r"Let $u=2x+1$, so $y=u^{4}$. $\dfrac{dy}{du}=4u^{3}$ and $\dfrac{du}{dx}=2$. Then $\dfrac{dy}{dx}=4u^{3}\times2=8(2x+1)^{3}$.",
        r"$4(2x+1)^{3}$ forgets to multiply by the derivative of the bracket, $2$."))

    a(Q(46, ["applications of differentiation"], "moyenne",
        r"The minimum value of $y=x^{2}-8x+3$ is",
        r"$-13$", [r"$4$", r"$3$", r"$19$"],
        r"At a stationary point $\dfrac{dy}{dx}=0$. Substitute the value of $x$ found into $y$ to obtain the minimum value of $y$ (not the value of $x$).",
        r"$\dfrac{dy}{dx}=2x-8=0$ gives $x=4$. Then $y=4^{2}-8(4)+3=16-32+3=-13$. The second derivative $2>0$ confirms a minimum.",
        r"$4$ is the value of $x$ at which the minimum occurs, not the minimum value of $y$."))

    a(Q(47, ["integration of polynomials"], "faible",
        r"Integrating $6x^{2}-4x$ with respect to $x$ gives, with $k$ the constant of integration,",
        r"$2x^{3}-2x^{2}+k$", [r"$12x-4+k$", r"$6x^{3}-4x^{2}+k$", r"$2x^{3}-4x^{2}+k$"],
        r"$\int ax^{n}\,dx=\dfrac{a\,x^{n+1}}{n+1}+k$: raise the power by one and divide by the new power.",
        r"$\int6x^{2}\,dx=\dfrac{6x^{3}}{3}=2x^{3}$ and $\int4x\,dx=\dfrac{4x^{2}}{2}=2x^{2}$. So the integral is $2x^{3}-2x^{2}+k$.",
        r"$12x-4$ is the derivative of $6x^{2}-4x$, not its integral."))

    a(Q(48, ["integration and area"], "faible",
        r"Integrating $\cos3x+2x$ with respect to $x$ gives, with $k$ the constant of integration,",
        r"$\dfrac{1}{3}\sin3x+x^{2}+k$", [r"$-\dfrac{1}{3}\sin3x+x^{2}+k$", r"$3\sin3x+x^{2}+k$", r"$\dfrac{1}{3}\sin3x+2x^{2}+k$"],
        r"$\int\cos ax\,dx=\dfrac{1}{a}\sin ax+k$ and $\int x^{n}\,dx=\dfrac{x^{n+1}}{n+1}+k$: integrate each term separately.",
        r"$\int\cos3x\,dx=\dfrac{1}{3}\sin3x$ and $\int2x\,dx=x^{2}$. Check by differentiating: $\dfrac{d}{dx}\left(\dfrac{1}{3}\sin3x+x^{2}\right)=\cos3x+2x$.",
        r"The factor in front of $\sin3x$ is $\dfrac{1}{3}$ (divide by the coefficient of $x$), not $3$; and $\int2x\,dx=x^{2}$, not $2x^{2}$."))

    a(Q(49, ["integration and area"], "faible",
        r"$\displaystyle\int_{1}^{3}(2x+1)\,dx=$",
        r"$10$", [r"$12$", r"$8$", r"$14$"],
        r"For a definite integral, find the integral, then subtract its value at the lower limit from its value at the upper limit.",
        r"$\displaystyle\int_{1}^{3}(2x+1)\,dx=\Big[x^{2}+x\Big]_{1}^{3}=(9+3)-(1+1)=12-2=10$.",
        r"$12$ is only the value at the upper limit: do not forget to subtract the value at the lower limit."))

    a(Q(50, ["integration and area"], "elevee",
        r"The area enclosed by the curve $y=4-x^{2}$ and the $x$-axis is",
        r"$\dfrac{32}{3}$", [r"$16$", r"$\dfrac{16}{3}$", r"$\dfrac{8}{3}$"],
        r"First find where the curve cuts the $x$-axis: these are the limits of integration. The area is the definite integral of $y$ between them.",
        r"$4-x^{2}=0$ gives $x=-2$ and $x=2$. $\displaystyle\int_{-2}^{2}(4-x^{2})\,dx=\Big[4x-\dfrac{x^{3}}{3}\Big]_{-2}^{2}=\left(8-\dfrac{8}{3}\right)-\left(-8+\dfrac{8}{3}\right)=16-\dfrac{16}{3}=\dfrac{32}{3}$.",
        r"$\dfrac{16}{3}$ is the area from $x=0$ to $x=2$, only half of the region: the curve is symmetric, so the whole area is twice this value."))
    return qs
