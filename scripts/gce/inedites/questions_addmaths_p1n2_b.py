r"""Questions 26 a 50 de l'epreuve inedite GCE O Level Additional Mathematics Paper 1 n.2 (voir generer_addmaths_p1n2.py).

Geometrie analytique, inequations, fonctions, matrices, groupes, vecteurs, derivation et integration. Chaines BRUTES (r"...").
"""
from questions_addmaths_p1n2_a import Q


def questions():
    qs = []
    a = qs.append

    a(Q(26, ["coordinate geometry of straight lines"], "moyenne",
        r"The perpendicular bisector of the line joining $A(0,2)$ and $B(6,-2)$ has the equation",
        r"$3x-2y=9$", [r"$3x+2y=9$", r"$2x+3y=6$", r"$3x-2y=3$"],
        r"The perpendicular bisector passes through the midpoint of $AB$ and its gradient is the negative reciprocal of the gradient of $AB$.",
        r"The midpoint is $(3,0)$. The gradient of $AB$ is $\dfrac{-2-2}{6-0}=-\dfrac{2}{3}$, so the gradient of the bisector is $\dfrac{3}{2}$. $y-0=\dfrac{3}{2}(x-3)$ gives $2y=3x-9$, that is $3x-2y=9$.",
        r"$2x+3y=6$ is the line through $A$ and $B$ turned round: its gradient is $-\dfrac{2}{3}$, the gradient of $AB$ itself."))
    a(Q(27, ["modulus functions and inequalities"], "moyenne",
        r"The solution of the inequality $|2x+1|<5$ is",
        r"$-3<x<2$", [r"$x<-3$ or $x>2$", r"$-2<x<3$", r"$x<-2$ or $x>3$"],
        r"$|A|<k$ with $k>0$ means $-k<A<k$.",
        r"$-5<2x+1<5$. Subtract $1$: $-6<2x<4$. Divide by $2$: $-3<x<2$.",
        r"$x<-3$ or $x>2$ is the solution of $|2x+1|>5$."))
    a(Q(28, ["linear and quadratic inequalities"], "moyenne",
        r"The solution of the inequality $x^{2}-5x+4\geq0$ is",
        r"$x\leq1$ or $x\geq4$", [r"$1\leq x\leq4$", r"$x\leq-1$ or $x\geq4$", r"$-4\leq x\leq-1$"],
        r"Factorise to find the critical values, then use the shape of the parabola: it is positive outside its roots when the coefficient of $x^{2}$ is positive.",
        r"$x^{2}-5x+4=(x-1)(x-4)$, with roots $1$ and $4$. The parabola opens upwards, so $(x-1)(x-4)\geq0$ outside the roots, including them: $x\leq1$ or $x\geq4$.",
        r"$1\leq x\leq4$ is the solution of $x^{2}-5x+4\leq0$."))
    a(Q(29, ["modulus functions and inequalities"], "elevee",
        r"The solution of the equation $|x-3|=2x$ is",
        r"$x=1$ only", [r"$x=-3$ only", r"$x=1$ and $x=-3$", r"$x=3$ only"],
        r"Solve the two equations $A=k$ and $A=-k$, then check each answer in the original equation: $|A|$ is never negative, so $k$ must be positive.",
        r"$x-3=2x$ gives $x=-3$, but then $2x=-6<0$ and $|-3-3|=6\neq-6$: rejected. $3-x=2x$ gives $x=1$, and $|1-3|=2=2(1)$: accepted. The only solution is $x=1$.",
        r"A value of $x$ found from $|A|=k$ must be checked: here $2x$ must be positive for the equation to have a solution."))
    a(Q(30, ["linear programming and inequality regions"], "faible",
        r"A club has $x$ boys and $y$ girls. There are at least $10$ members, and the number of girls is at most twice the number of boys. This is represented by",
        r"$x+y\geq10,\ y\leq2x$", [r"$x+y\leq10,\ y\leq2x$", r"$x+y\geq10,\ y\geq2x$", r"$x+y\geq10,\ x\leq2y$"],
        r"“At least” means $\geq$ and “at most” means $\leq$. Translate each statement separately.",
        r"The total number of members is $x+y$, which is at least $10$: $x+y\geq10$. The girls, $y$, are at most twice the boys: $y\leq2x$.",
        r"“The number of girls is at most twice the number of boys” is $y\leq2x$; $x\leq2y$ says it the other way round."))
    a(Q(31, ["linear programming and inequality regions"], "moyenne",
        r"The shaded region $R$ in {FIG} is bounded by the $y$-axis and the lines $y=2$ and $x+y=6$, and it includes its boundaries. Which set of inequalities defines $R$?",
        r"$x\geq0,\ y\geq2,\ x+y\leq6$", [r"$x\geq0,\ y\leq2,\ x+y\leq6$", r"$x\geq0,\ y\geq2,\ x+y\geq6$", r"$x\leq0,\ y\geq2,\ x+y\leq6$"],
        r"To test an inequality, take a point inside the shaded region and check that it satisfies it.",
        r"Take the point $(1,3)$ in $R$. It is on the right of the $y$-axis ($x\geq0$), above the line $y=2$ ($y\geq2$) and below the line $x+y=6$, since $1+3=4\leq6$ ($x+y\leq6$).",
        r"The region lies on the side of the line $x+y=6$ that contains the origin: the sum $x+y$ is smaller than $6$.",
        fig="region"))
    a(Q(32, ["composite and inverse functions"], "faible",
        r"The functions $f$ and $g$ are defined by $f(x)=x+4$ and $g(x)=x^{2}$. The value of $fg(3)$ is",
        r"$13$", [r"$49$", r"$25$", r"$19$"],
        r"$fg(x)$ means $f(g(x))$: apply $g$ first, then $f$.",
        r"$g(3)=3^{2}=9$ and $f(9)=9+4=13$.",
        r"$49$ is $gf(3)=g(7)$: the order of the functions is reversed."))
    a(Q(33, ["composite and inverse functions"], "moyenne",
        r"The function $f$ is defined by $f(x)=\dfrac{3x+1}{x-2}$, $x\neq2$. The value of $f^{-1}(4)$ is",
        r"$9$", [r"$\dfrac{13}{2}$", r"$-7$", r"$\dfrac{1}{9}$"],
        r"$f^{-1}(4)$ is the value of $x$ for which $f(x)=4$.",
        r"Solve $\dfrac{3x+1}{x-2}=4$: $3x+1=4x-8$, so $x=9$. Check: $f(9)=\dfrac{28}{7}=4$.",
        r"$f(4)=\dfrac{13}{2}$ is the image of $4$, not its preimage: $f^{-1}(4)$ needs the equation $f(x)=4$ to be solved."))
    a(Q(34, ["piecewise defined functions"], "faible",
        r"The function $f$ is defined by $f(x)=\begin{cases}2x,&x\leq1\\x^{2}+1,&x>1\end{cases}$. The value of $f(0)+f(2)$ is",
        r"$5$", [r"$6$", r"$4$", r"$9$"],
        r"For a piecewise function, decide first which rule applies to each value of $x$.",
        r"$0\leq1$, so $f(0)=2(0)=0$. $2>1$, so $f(2)=2^{2}+1=5$. The sum is $0+5=5$.",
        r"Using $x^{2}+1$ for $x=0$ gives $1$, which is wrong because $0$ is not in the range $x>1$."))
    a(Q(35, ["matrices and inverses (additional maths)"], "faible",
        r"The determinant of the matrix $\begin{pmatrix}4&-1\\2&3\end{pmatrix}$ is",
        r"$14$", [r"$10$", r"$12$", r"$-14$"],
        r"The determinant of $\begin{pmatrix}a&b\\c&d\end{pmatrix}$ is $ad-bc$.",
        r"$4\times3-(-1)\times2=12+2=14$.",
        r"Subtracting a negative product adds it: $10=12-2$ is the sign slip."))
    a(Q(36, ["matrix transformations (additional maths)"], "faible",
        r"If $A=\begin{pmatrix}1&0\\2&1\end{pmatrix}$ and $B=\begin{pmatrix}3&1\\0&2\end{pmatrix}$, then $AB$ is",
        r"$\begin{pmatrix}3&1\\6&4\end{pmatrix}$", [r"$\begin{pmatrix}5&1\\4&2\end{pmatrix}$", r"$\begin{pmatrix}3&0\\0&2\end{pmatrix}$", r"$\begin{pmatrix}4&1\\2&3\end{pmatrix}$"],
        r"To multiply two matrices, multiply the rows of the first by the columns of the second. The order matters: $AB\neq BA$ in general.",
        r"Row $1$: $(1\times3+0\times0,\ 1\times1+0\times2)=(3,1)$. Row $2$: $(2\times3+1\times0,\ 2\times1+1\times2)=(6,4)$. So $AB=\begin{pmatrix}3&1\\6&4\end{pmatrix}$.",
        r"$\begin{pmatrix}5&1\\4&2\end{pmatrix}$ is $BA$, the product in the opposite order."))
    a(Q(37, ["matrix transformations (additional maths)"], "moyenne",
        r"The matrix that represents an anticlockwise rotation of $90^{\circ}$ about the origin is",
        r"$\begin{pmatrix}0&-1\\1&0\end{pmatrix}$", [r"$\begin{pmatrix}0&1\\-1&0\end{pmatrix}$", r"$\begin{pmatrix}1&0\\0&-1\end{pmatrix}$", r"$\begin{pmatrix}-1&0\\0&1\end{pmatrix}$"],
        r"The columns of the matrix of a transformation are the images of the points $(1,0)$ and $(0,1)$.",
        r"An anticlockwise rotation of $90^{\circ}$ sends $(1,0)$ to $(0,1)$ and $(0,1)$ to $(-1,0)$. The columns are $\begin{pmatrix}0\\1\end{pmatrix}$ and $\begin{pmatrix}-1\\0\end{pmatrix}$, so the matrix is $\begin{pmatrix}0&-1\\1&0\end{pmatrix}$.",
        r"$\begin{pmatrix}0&1\\-1&0\end{pmatrix}$ is the clockwise rotation: it sends $(1,0)$ to $(0,-1)$."))
    a(Q(38, ["binary operations and groups"], "faible",
        r"A binary operation $*$ is defined on the real numbers by $x*y=xy-x$. The value of $3*4$ is",
        r"$9$", [r"$12$", r"$3$", r"$15$"],
        r"To evaluate a binary operation, replace $x$ and $y$ by the numbers in the rule.",
        r"$3*4=(3)(4)-3=12-3=9$.",
        r"$12$ forgets the term $-x$; $15$ adds it instead of subtracting it."))
    a(Q(39, ["binary operations and groups"], "faible",
        r"A binary operation $*$ is defined by $x*y=(2x+3y)\pmod{6}$. The value of $4*5$ is",
        r"$5$", [r"$23$", r"$3$", r"$2$"],
        r"A result “modulo $n$” is the remainder on division by $n$.",
        r"$4*5=(2\times4+3\times5)\pmod{6}=23\pmod{6}=5$, because $23=3\times6+5$.",
        r"$23$ is the value before the remainder is taken."))
    a(Q(40, ["binary operations and groups"], "elevee",
        r"The set $G=\{1,2,4,5,7,8\}$ forms a group under multiplication modulo $9$. A subgroup of $G$ is",
        r"$\{1,4,7\}$", [r"$\{1,2,4\}$", r"$\{1,5,8\}$", r"$\{2,4,8\}$"],
        r"A subgroup contains the identity, is closed under the operation and contains the inverse of each of its elements. The identity here is $1$.",
        r"$\{2,4,8\}$ has no identity. In $\{1,2,4\}$, $2\times4=8$ is not in the set. In $\{1,5,8\}$, $5\times5=25\equiv7$ is not in the set. In $\{1,4,7\}$: $4\times4=16\equiv7$, $4\times7=28\equiv1$ and $7\times7=49\equiv4$ are all in the set, and $4$ and $7$ are inverses of each other: it is a subgroup.",
        r"A set that contains the identity can still fail to be closed: multiply every pair of its elements."))
    a(Q(41, ["vector geometry (additional maths)"], "faible",
        r"The unit vector in the direction of $8\mathbf{i}+15\mathbf{j}$ is",
        r"$\dfrac{8}{17}\mathbf{i}+\dfrac{15}{17}\mathbf{j}$", [r"$\dfrac{8}{23}\mathbf{i}+\dfrac{15}{23}\mathbf{j}$", r"$\dfrac{15}{17}\mathbf{i}+\dfrac{8}{17}\mathbf{j}$", r"$8\mathbf{i}+15\mathbf{j}$"],
        r"A unit vector in the direction of $\mathbf{v}$ is $\dfrac{\mathbf{v}}{|\mathbf{v}|}$.",
        r"$|8\mathbf{i}+15\mathbf{j}|=\sqrt{8^{2}+15^{2}}=\sqrt{289}=17$, so the unit vector is $\dfrac{1}{17}(8\mathbf{i}+15\mathbf{j})=\dfrac{8}{17}\mathbf{i}+\dfrac{15}{17}\mathbf{j}$.",
        r"The magnitude is $\sqrt{64+225}=17$, not $8+15=23$."))
    a(Q(42, ["vector geometry (additional maths)"], "moyenne",
        r"A line has vector equation $\mathbf{r}=-\mathbf{i}+4\mathbf{j}+t(3\mathbf{i}-2\mathbf{j})$. The position vector of the point on the line for which $t=3$ is",
        r"$8\mathbf{i}-2\mathbf{j}$", [r"$2\mathbf{i}+2\mathbf{j}$", r"$9\mathbf{i}-6\mathbf{j}$", r"$8\mathbf{i}-3\mathbf{j}$"],
        r"A value of the parameter gives one point of the line: substitute it in $\mathbf{r}=\mathbf{a}+t\mathbf{d}$.",
        r"$\mathbf{r}=-\mathbf{i}+4\mathbf{j}+3(3\mathbf{i}-2\mathbf{j})=(-1+9)\mathbf{i}+(4-6)\mathbf{j}=8\mathbf{i}-2\mathbf{j}$.",
        r"$9\mathbf{i}-6\mathbf{j}$ is $3\mathbf{d}$ only: the starting point $-\mathbf{i}+4\mathbf{j}$ must be added."))
    a(Q(43, ["scalar product"], "moyenne",
        r"The cosine of the angle between the vectors $3\mathbf{i}+4\mathbf{j}$ and $5\mathbf{i}-12\mathbf{j}$ is",
        r"$-\dfrac{33}{65}$", [r"$\dfrac{33}{65}$", r"$-\dfrac{63}{65}$", r"$\dfrac{16}{65}$"],
        r"$\cos\theta=\dfrac{\mathbf{a}\cdot\mathbf{b}}{|\mathbf{a}||\mathbf{b}|}$.",
        r"$\mathbf{a}\cdot\mathbf{b}=3(5)+4(-12)=15-48=-33$, $|\mathbf{a}|=5$ and $|\mathbf{b}|=13$. $\cos\theta=\dfrac{-33}{65}$.",
        r"A negative scalar product means that the angle is obtuse: the cosine is negative."))
    a(Q(44, ["derivatives of standard functions"], "faible",
        r"$\dfrac{d}{dx}\left(x^{3/2}\right)=$",
        r"$\dfrac{3}{2}x^{1/2}$", [r"$\dfrac{2}{3}x^{1/2}$", r"$\dfrac{3}{2}x^{3/2}$", r"$x^{1/2}$"],
        r"$\dfrac{d}{dx}(x^{n})=nx^{n-1}$, including when $n$ is a fraction.",
        r"$\dfrac{d}{dx}\left(x^{3/2}\right)=\dfrac{3}{2}x^{\frac{3}{2}-1}=\dfrac{3}{2}x^{1/2}$.",
        r"The index goes down by $1$, and the old index becomes the coefficient."))
    a(Q(45, ["differentiation techniques (additional maths)"], "faible",
        r"If $y=x^{2}(x+1)$, then $\dfrac{dy}{dx}=$",
        r"$3x^{2}+2x$", [r"$2x$", r"$x^{2}+2x$", r"$3x^{2}$"],
        r"Expand the product, or use the product rule $\dfrac{d}{dx}(uv)=u\dfrac{dv}{dx}+v\dfrac{du}{dx}$.",
        r"$y=x^{3}+x^{2}$, so $\dfrac{dy}{dx}=3x^{2}+2x$. Check with the product rule: $x^{2}(1)+(x+1)(2x)=x^{2}+2x^{2}+2x=3x^{2}+2x$.",
        r"The derivative of a product is not the product of the derivatives: $2x\times1=2x$ is wrong."))
    a(Q(46, ["applications of differentiation"], "moyenne",
        r"The gradient of the normal to the curve $y=x^{2}-3x$ at the point where $x=2$ is",
        r"$-1$", [r"$1$", r"$2$", r"$-2$"],
        r"The gradient of the normal is the negative reciprocal of the gradient of the tangent: $m_{\text{normal}}=-\dfrac{1}{m_{\text{tangent}}}$.",
        r"$\dfrac{dy}{dx}=2x-3$, which is $1$ at $x=2$. The gradient of the normal is $-\dfrac{1}{1}=-1$.",
        r"$1$ is the gradient of the tangent, not of the normal."))
    a(Q(47, ["integration of polynomials"], "faible",
        r"Integrating $4x^{3}-\dfrac{2}{x^{2}}$ with respect to $x$ gives, with $k$ the constant of integration,",
        r"$x^{4}+\dfrac{2}{x}+k$", [r"$x^{4}-\dfrac{2}{x}+k$", r"$12x^{2}+\dfrac{4}{x^{3}}+k$", r"$x^{4}-\dfrac{2}{x^{3}}+k$"],
        r"Write $\dfrac{2}{x^{2}}$ as $2x^{-2}$ and use $\int x^{n}dx=\dfrac{x^{n+1}}{n+1}$.",
        r"$\int4x^{3}dx=x^{4}$ and $\int-2x^{-2}dx=-2\times\dfrac{x^{-1}}{-1}=2x^{-1}=\dfrac{2}{x}$. So the integral is $x^{4}+\dfrac{2}{x}+k$.",
        r"Integrating $x^{-2}$ gives $\dfrac{x^{-1}}{-1}$: the two minus signs make a plus."))
    a(Q(48, ["integration and area"], "faible",
        r"Integrating $\sin x+3$ with respect to $x$ gives, with $k$ the constant of integration,",
        r"$-\cos x+3x+k$", [r"$\cos x+3x+k$", r"$-\cos x+3+k$", r"$\cos x+3x^{2}+k$"],
        r"$\int\sin x\,dx=-\cos x+k$ and the integral of a constant $c$ is $cx$.",
        r"$\int(\sin x+3)\,dx=-\cos x+3x+k$.",
        r"The integral of $\sin x$ is $-\cos x$, and the integral of $3$ is $3x$, not $3$."))
    a(Q(49, ["integration and area"], "moyenne",
        r"$\displaystyle\int_{1}^{3}(3x^{2}-4x+2)\,dx=$",
        r"$14$", [r"$15$", r"$16$", r"$17$"],
        r"For a definite integral, integrate, then substitute the upper limit and subtract the value at the lower limit.",
        r"$\displaystyle\int_{1}^{3}(3x^{2}-4x+2)\,dx=\Big[x^{3}-2x^{2}+2x\Big]_{1}^{3}=(27-18+6)-(1-2+2)=15-1=14$.",
        r"$15$ is the value at the upper limit only; $16$ adds the two values instead of subtracting; $17$ is the value of the integrand at $x=3$."))
    a(Q(50, ["integration and area"], "moyenne",
        r"The area enclosed between the curves $y=x$ and $y=x^{2}$ is",
        r"$\dfrac{1}{6}$", [r"$\dfrac{1}{2}$", r"$\dfrac{1}{3}$", r"$\dfrac{5}{6}$"],
        r"First find where the curves meet: they are the limits of integration. The area between two curves is the integral of the upper curve minus the lower curve.",
        r"$x=x^{2}$ gives $x=0$ and $x=1$. Between $0$ and $1$ the line $y=x$ is above the parabola. Area $=\displaystyle\int_{0}^{1}(x-x^{2})\,dx=\Big[\dfrac{x^{2}}{2}-\dfrac{x^{3}}{3}\Big]_{0}^{1}=\dfrac{1}{2}-\dfrac{1}{3}=\dfrac{1}{6}$.",
        r"$\dfrac{1}{2}$ and $\dfrac{1}{3}$ are the areas under the line and under the parabola alone."))
    return qs
