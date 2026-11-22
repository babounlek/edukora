r"""Les 50 QCM de l'epreuve inedite GCE A Level Further Mathematics Paper 1 n.1 (50 x 1 point, 90 min).

Structure mesuree sur les Paper 1 de 2025 et 2026 (50 questions, themes melanges, 4 options, difficulte 40-50 % faible) ; aucune donnee reprise d'un sujet
reel ni des Paper 2 et 3 de la session. Chaque question : enonce, bonne reponse `key`, trois distracteurs avec l'erreur qui y mene, rappel, resolution,
valeur de controle `val` (recalculee par verifier_reponses_furthermaths_p1.py). Les lettres des cles sont placees par le GENERATEUR, jamais tapees ici.
Chaines BRUTES.
"""

QS = []


def Q(themes, diff, stem, key, dist, rappel, sol, val, conseil=None):
    assert len(dist) == 3 and all(len(d) == 2 for d in dist), stem[:40]
    texts = [key] + [d[0] for d in dist]
    assert len(set(texts)) == 4, ("options en double", stem[:50])
    QS.append(dict(themes=themes, diff=diff, stem=stem, key=key, dist=dist, rappel=rappel, sol=sol, val=val, conseil=conseil))


def questions():
    return QS


# 1
Q(["partial fractions"], "faible", r"$\dfrac{3x+5}{(x+1)(x+2)}$ expressed in partial fractions is",
  r"$\dfrac{2}{x+1}+\dfrac{1}{x+2}$",
  [(r"$\dfrac{1}{x+1}+\dfrac{2}{x+2}$", r"swaps the two numerators"), (r"$\dfrac{3}{x+1}+\dfrac{5}{x+2}$", r"copies the coefficients of the numerator $3x+5$ over the factors"),
   (r"$\dfrac{2}{x+1}-\dfrac{1}{x+2}$", r"makes a sign error when evaluating at $x=-2$")],
  r"For distinct linear factors write $\dfrac{N(x)}{(x-a)(x-b)}=\dfrac{A}{x-a}+\dfrac{B}{x-b}$ and find each constant by substituting $x=a$ and $x=b$ in $N(x)=A(x-b)+B(x-a)$.",
  r"Write $3x+5=A(x+2)+B(x+1)$. At $x=-1$: $2=A$. At $x=-2$: $-1=-B$, so $B=1$. Check at $x=3$: $\dfrac{14}{20}=0.7$ and $\dfrac24+\dfrac15=0.7$.",
  0.7)
# 2
Q(["first order differential equations"], "faible", r"The integrating factor of $\dfrac{dy}{dx}+\dfrac{3}{x}y=x^{2}$, for $x>0$, is",
  r"$x^{3}$",
  [(r"$3x$", r"uses the coefficient $\tfrac3x$ itself instead of $e^{\int\tfrac3x dx}$"), (r"$e^{3x}$", r"integrates $\tfrac3x$ as $3x$"), (r"$\dfrac{1}{x^{3}}$", r"takes the exponent with the wrong sign")],
  r"For $\dfrac{dy}{dx}+P(x)y=Q(x)$ the integrating factor is $e^{\int P(x)\,dx}$.",
  r"$\int\dfrac3x\,dx=3\ln x$, so the integrating factor is $e^{3\ln x}=x^{3}$.",
  3)
# 3
Q(["hyperbolic functions"], "faible", r"The exact value of $\cosh(\ln3)$ is",
  r"$\dfrac53$",
  [(r"$\dfrac43$", r"computes $\sinh(\ln3)$ instead, subtracting $\tfrac13$"), (r"$\dfrac{10}{3}$", r"forgets to divide the sum by $2$"), (r"$3$", r"treats $\cosh(\ln3)$ as $e^{\ln3}$")],
  r"$\cosh x=\tfrac12\left(e^{x}+e^{-x}\right)$, and $e^{\ln a}=a$.",
  r"$\cosh(\ln3)=\tfrac12\left(3+\tfrac13\right)=\tfrac12\times\tfrac{10}{3}=\tfrac53$.",
  5 / 3)
# 4
Q(["modulus function"], "faible", r"The set of values of $x$ for which $|2x-3|<5$ is",
  r"$-1<x<4$",
  [(r"$x<-1$ or $x>4$", r"reverses the inequality, which is the solution of $|2x-3|>5$"), (r"$-4<x<1$", r"changes $2x-3$ into $2x+3$"), (r"$-1<x<1$", r"adds $3$ to one side only before dividing")],
  r"$|u|<a$ with $a>0$ is equivalent to $-a<u<a$; solve the double inequality for $x$.",
  r"$-5<2x-3<5$, so $-2<2x<8$ and $-1<x<4$.",
  (-1, 4))
# 5
Q(["taylor series"], "moyenne", r"The Taylor series of $\ln x$ about $x=1$ begins $(x-1)+a(x-1)^{2}+\cdots$. The value of $a$ is",
  r"$-\dfrac12$",
  [(r"$\dfrac12$", r"forgets that $f''(1)=-1$"), (r"$-1$", r"forgets to divide $f''(1)$ by $2!$"), (r"$1$", r"makes both errors at once")],
  r"The Taylor series of $f$ about $a$ is $f(a)+f'(a)(x-a)+\dfrac{f''(a)}{2!}(x-a)^{2}+\cdots$.",
  r"$f(x)=\ln x$, $f'(x)=\dfrac1x$, $f''(x)=-\dfrac{1}{x^{2}}$, so $f''(1)=-1$ and $a=\dfrac{f''(1)}{2!}=-\dfrac12$.",
  -0.5)
# 6
Q(["complex numbers"], "faible", r"The modulus of $\dfrac{3+4i}{1-2i}$ is",
  r"$\sqrt5$",
  [(r"$5$", r"takes the modulus of the numerator only"), (r"$\dfrac53$", r"takes $|1-2i|$ as $3$ by adding the coefficients"), (r"$5\sqrt5$", r"multiplies the two moduli instead of dividing")],
  r"The modulus of a quotient is the quotient of the moduli: $\left|\dfrac{z_{1}}{z_{2}}\right|=\dfrac{|z_{1}|}{|z_{2}|}$.",
  r"$|3+4i|=5$ and $|1-2i|=\sqrt5$, so the modulus is $\dfrac{5}{\sqrt5}=\sqrt5$.",
  5 ** 0.5)
# 7
Q(["propositional logic"], "faible", r"The contrapositive of the statement \"if $x$ is divisible by $6$, then $x$ is divisible by $3$\" is".replace('\\"', '"'),
  r"if $x$ is not divisible by $3$, then $x$ is not divisible by $6$",
  [(r"if $x$ is divisible by $3$, then $x$ is divisible by $6$", r"gives the converse, which swaps the two parts without negating them"), (r"if $x$ is not divisible by $6$, then $x$ is not divisible by $3$", r"gives the inverse, which negates the two parts without swapping them"),
   (r"$x$ is divisible by $6$ and $x$ is not divisible by $3$", r"gives the negation of the statement")],
  r"The contrapositive of $A\Rightarrow B$ is $\neg B\Rightarrow\neg A$; it has the same truth value as $A\Rightarrow B$, whereas the converse $B\Rightarrow A$ and the inverse $\neg A\Rightarrow\neg B$ do not.",
  r"Let $A$ be \"$x$ is divisible by $6$\" and $B$ be \"$x$ is divisible by $3$\". The contrapositive $\neg B\Rightarrow\neg A$ reads: if $x$ is not divisible by $3$, then $x$ is not divisible by $6$. A truth table confirms that $\neg B\Rightarrow\neg A$ and $A\Rightarrow B$ take the same values in all four cases.".replace('\\"', '"'),
  (1, 0, 1, 1))
# 8
Q(["reduction formulae"], "faible", r"Given that $I_{n}=\displaystyle\int_{0}^{\infty}x^{n}e^{-x}\,dx$ satisfies $I_{n}=nI_{n-1}$ for $n\ge1$, the value of $I_{4}$ is",
  r"$24$",
  [(r"$16$", r"squares $4$ instead of building the product $4\times3\times2\times1$"), (r"$12$", r"stops the recurrence at $I_{2}$, taking $I_{2}=1$"), (r"$4$", r"applies the recurrence only once")],
  r"Apply the reduction formula repeatedly until the starting value $I_{0}$ is reached, and evaluate $I_{0}$ directly.",
  r"$I_{0}=\displaystyle\int_{0}^{\infty}e^{-x}\,dx=1$. Then $I_{1}=1$, $I_{2}=2$, $I_{3}=6$ and $I_{4}=4\times6=24$.",
  24)
# 9
Q(["mean and root mean square values"], "faible", r"The mean value of $\sin^{2}x$ over the interval $[0,\pi]$ is",
  r"$\dfrac12$",
  [(r"$\dfrac{\pi}{2}$", r"gives the integral without dividing by the length $\pi$ of the interval"), (r"$1$", r"takes the maximum value of $\sin^{2}x$"), (r"$\dfrac1\pi$", r"divides by $\pi$ but forgets the value of the integral")],
  r"The mean value of $f$ over $[a,b]$ is $\dfrac{1}{b-a}\displaystyle\int_{a}^{b}f(x)\,dx$.",
  r"$\sin^{2}x=\tfrac12(1-\cos2x)$, so $\displaystyle\int_{0}^{\pi}\sin^{2}x\,dx=\tfrac12\left[x-\tfrac12\sin2x\right]_{0}^{\pi}=\tfrac{\pi}{2}$. The mean value is $\dfrac{\pi/2}{\pi}=\dfrac12$.",
  0.5)
# 10
Q(["polar coordinates"], "elevee", r"The area enclosed by the cardioid $r=2(1+\cos\theta)$ is",
  r"$6\pi$",
  [(r"$3\pi$", r"integrates over $0\le\theta\le\pi$ only, which is half of the curve"), (r"$4\pi$", r"drops the term in $\cos^{2}\theta$ when expanding the square"), (r"$12\pi$", r"forgets the factor $\tfrac12$ in the area formula")],
  r"The area enclosed by $r=f(\theta)$ for $\alpha\le\theta\le\beta$ is $\tfrac12\displaystyle\int_{\alpha}^{\beta}r^{2}\,d\theta$; a cardioid is traced for $0\le\theta\le2\pi$.",
  r"$A=\tfrac12\displaystyle\int_{0}^{2\pi}4(1+\cos\theta)^{2}d\theta=2\int_{0}^{2\pi}\left(1+2\cos\theta+\cos^{2}\theta\right)d\theta$. Since $\cos^{2}\theta=\tfrac12(1+\cos2\theta)$, the integral is $2\left[\tfrac32\theta+2\sin\theta+\tfrac14\sin2\theta\right]_{0}^{2\pi}=2\times3\pi=6\pi$.",
  6 * 3.141592653589793)
# 11
Q(["conic sections"], "faible", r"The eccentricity of the ellipse $\dfrac{x^{2}}{25}+\dfrac{y^{2}}{9}=1$ is",
  r"$\dfrac45$",
  [(r"$\dfrac35$", r"takes $b/a$ instead of $\sqrt{1-b^{2}/a^{2}}$"), (r"$\dfrac{16}{25}$", r"gives $e^{2}$ without the square root"), (r"$\dfrac43$", r"inverts the ratio $c/a$")],
  r"For $\dfrac{x^{2}}{a^{2}}+\dfrac{y^{2}}{b^{2}}=1$ with $a>b$, the eccentricity is $e=\sqrt{1-\dfrac{b^{2}}{a^{2}}}$.",
  r"$a^{2}=25$ and $b^{2}=9$, so $e=\sqrt{1-\dfrac{9}{25}}=\sqrt{\dfrac{16}{25}}=\dfrac45$.",
  0.8)
# 12
Q(["scalar and vector products"], "moyenne", r"If $\mathbf a=(1,0,2)$ and $\mathbf b=(0,3,1)$, then $|\mathbf a\times\mathbf b|$ is",
  r"$\sqrt{46}$",
  [(r"$2$", r"calculates the scalar product $\mathbf a\cdot\mathbf b$ instead"), (r"$\sqrt{50}$", r"takes $|\mathbf a||\mathbf b|$, which assumes that the vectors are perpendicular"), (r"$\sqrt{26}$", r"drops one component of the vector product")],
  r"The vector product is $\mathbf a\times\mathbf b=(a_{2}b_{3}-a_{3}b_{2},\ a_{3}b_{1}-a_{1}b_{3},\ a_{1}b_{2}-a_{2}b_{1})$ and $|\mathbf a\times\mathbf b|$ is the square root of the sum of the squares of its components.",
  r"$\mathbf a\times\mathbf b=(0\times1-2\times3,\ 2\times0-1\times1,\ 1\times3-0\times0)=(-6,-1,3)$, so $|\mathbf a\times\mathbf b|=\sqrt{36+1+9}=\sqrt{46}$.",
  46 ** 0.5)
# 13
Q(["determinants and inverses"], "faible", r"The determinant of $\begin{pmatrix}2&1&0\\1&3&1\\0&1&2\end{pmatrix}$ is",
  r"$8$",
  [(r"$10$", r"forgets the second term of the expansion along the first row"), (r"$12$", r"multiplies the diagonal entries"), (r"$-8$", r"reverses the sign of the whole expansion")],
  r"Expand along a row: $\det=a_{11}M_{11}-a_{12}M_{12}+a_{13}M_{13}$, where $M_{ij}$ is the minor of $a_{ij}$ and the signs alternate.",
  r"Along the first row: $2(3\times2-1\times1)-1(1\times2-1\times0)+0=2\times5-2=8$.",
  8)
# 14
Q(["group theory"], "moyenne", r"In the group of non-zero residues modulo $7$ under multiplication, the order of the element $3$ is",
  r"$6$",
  [(r"$2$", r"stops at $3^{2}=9\equiv2$"), (r"$3$", r"takes the element itself as its order"), (r"$7$", r"takes the modulus as the order, although the group has only $6$ elements")],
  r"The order of an element $g$ is the least positive integer $k$ with $g^{k}=e$; list the successive powers until the identity appears.",
  r"$3^{1}=3$, $3^{2}=2$, $3^{3}=6$, $3^{4}=4$, $3^{5}=5$, $3^{6}=1\pmod 7$. The first power equal to $1$ is $3^{6}$, so the order is $6$ and $3$ generates the group.",
  6)
# 15
Q(["modular arithmetic"], "moyenne", r"The remainder when $3^{46}$ is divided by $7$ is",
  r"$4$",
  [(r"$1$", r"treats $46$ as a multiple of the cycle length $6$"), (r"$2$", r"stops at $3^{2}\equiv2$"), (r"$6$", r"reduces the exponent but uses $3^{3}$ instead of $3^{4}$")],
  r"If $a^{k}\equiv1\pmod n$ then powers of $a$ repeat with period $k$: reduce the exponent modulo $k$.",
  r"$3^{6}=729=104\times7+1\equiv1\pmod 7$. Since $46=6\times7+4$, $3^{46}\equiv3^{4}=81=11\times7+4\equiv4\pmod7$.",
  4)
# 16
Q(["curve asymptotes"], "moyenne", r"The curve $y=\dfrac{x-2}{x^{2}-5x+6}$ has, as vertical asymptote(s),",
  r"$x=3$ only",
  [(r"$x=2$ and $x=3$", r"takes both zeros of the denominator without cancelling the common factor $x-2$"), (r"$x=2$ only", r"keeps the cancelled factor and discards the other zero"), (r"$x=-2$ and $x=-3$", r"changes the signs of the roots of $x^{2}-5x+6$")],
  r"A vertical asymptote occurs at a zero of the denominator that is not cancelled by a factor of the numerator; a cancelled factor gives only a hole in the curve.",
  r"$x^{2}-5x+6=(x-2)(x-3)$, so $y=\dfrac{x-2}{(x-2)(x-3)}=\dfrac{1}{x-3}$ for $x\ne2$. As $x\to3$ the value of $y$ is unbounded, so $x=3$ is a vertical asymptote. As $x\to2$, $y\to-1$, a finite limit: the curve has a hole at $x=2$, not an asymptote.",
  (0, 1))
# 17
Q(["limits and continuity"], "faible", r"The function $f(x)=\dfrac{x^{2}-4}{x-2}$ for $x\ne2$, with $f(2)=k$, is continuous at $x=2$ when $k=$",
  r"$4$",
  [(r"$0$", r"substitutes $x=2$ in the numerator only"), (r"$2$", r"cancels the factor but keeps $x-2$"), (r"$-4$", r"takes the left value with the wrong sign")],
  r"A function is continuous at $a$ when $\displaystyle\lim_{x\to a}f(x)=f(a)$; factorise and cancel to find the limit.",
  r"For $x\ne2$, $f(x)=\dfrac{(x-2)(x+2)}{x-2}=x+2$, so $\displaystyle\lim_{x\to2}f(x)=4$. Continuity requires $k=4$.",
  4)
# 18
Q(["hyperbolic functions"], "moyenne", r"$\sinh^{-1}\left(\dfrac34\right)$ is equal to",
  r"$\ln2$",
  [(r"$\ln\dfrac32$", r"replaces $\sqrt{x^{2}+1}$ by $x$"), (r"$\ln\dfrac74$", r"replaces $\sqrt{x^{2}+1}$ by $1$"), (r"$\ln\dfrac54$", r"leaves out the term $x$ in $x+\sqrt{x^{2}+1}$")],
  r"$\sinh^{-1}x=\ln\left(x+\sqrt{x^{2}+1}\right)$ for every real $x$.",
  r"$\sinh^{-1}\left(\tfrac34\right)=\ln\left(\tfrac34+\sqrt{\tfrac{9}{16}+1}\right)=\ln\left(\tfrac34+\tfrac54\right)=\ln2$.",
  0.6931471805599453)
# 19
Q(["complex numbers", "de moivre theorem"], "moyenne", r"If $z=1+i$, then $z^{8}$ is equal to",
  r"$16$",
  [(r"$256$", r"takes the modulus of $z$ as $2$"), (r"$16i$", r"takes the argument of $z$ as $\tfrac{\pi}{16}$ and ends at a quarter turn"), (r"$-16$", r"takes the argument of $z$ as $\tfrac{\pi}{8}$, which gives a half turn")],
  r"Write $z=r(\cos\theta+i\sin\theta)$; then $z^{n}=r^{n}(\cos n\theta+i\sin n\theta)$.",
  r"$|z|=\sqrt2$ and $\arg z=\tfrac{\pi}{4}$, so $z^{8}=(\sqrt2)^{8}\left(\cos2\pi+i\sin2\pi\right)=16$.",
  16)
# 20
Q(["definite integrals"], "faible", r"$\displaystyle\int_{-2}^{2}\left(x^{3}+x^{2}\right)dx$ is equal to",
  r"$\dfrac{16}{3}$",
  [(r"$0$", r"treats the whole integrand as an odd function"), (r"$\dfrac83$", r"integrates over $[0,2]$ only"), (r"$\dfrac{32}{3}$", r"doubles the integral of the even part twice")],
  r"Over a symmetric interval $[-a,a]$ an odd function integrates to $0$ and an even function to twice its integral over $[0,a]$.",
  r"$x^{3}$ is odd, so its integral is $0$. $x^{2}$ is even: $\displaystyle\int_{-2}^{2}x^{2}dx=2\left[\tfrac{x^{3}}{3}\right]_{0}^{2}=\tfrac{16}{3}$.",
  16 / 3)
# 21
Q(["second order differential equations"], "faible", r"The general solution of $\dfrac{d^{2}x}{dt^{2}}+6\dfrac{dx}{dt}+9x=0$ is $x=$",
  r"$(p+qt)e^{-3t}$",
  [(r"$pe^{-3t}+qe^{3t}$", r"takes the roots as $\pm3$"), (r"$e^{-3t}(p\cos3t+q\sin3t)$", r"treats the roots as complex"), (r"$(p+qt)e^{3t}$", r"takes the repeated root with the wrong sign")],
  r"For $\ddot x+a\dot x+bx=0$, solve $m^{2}+am+b=0$: a repeated root $m$ gives $x=(p+qt)e^{mt}$.",
  r"The auxiliary equation $m^{2}+6m+9=(m+3)^{2}=0$ has the repeated root $m=-3$, so $x=(p+qt)e^{-3t}$.",
  (-3, 0))
# 22
Q(["mean and root mean square values"], "faible", r"The root mean square value of $f(x)=x$ over the interval $[0,3]$ is",
  r"$\sqrt3$",
  [(r"$\dfrac32$", r"gives the mean value instead of the root mean square value"), (r"$3$", r"takes the greatest value of $f$"), (r"$\sqrt{27}$", r"forgets to divide $\int x^{2}dx$ by the length of the interval")],
  r"The root mean square value of $f$ over $[a,b]$ is $\sqrt{\dfrac{1}{b-a}\displaystyle\int_{a}^{b}\left[f(x)\right]^{2}dx}$.",
  r"$\displaystyle\int_{0}^{3}x^{2}dx=9$, so the mean of the squares is $\tfrac93=3$ and the root mean square value is $\sqrt3$.",
  3 ** 0.5)
# 23
Q(["polar coordinates"], "moyenne", r"The polar curve $r=2\sin\theta$ is a circle with centre",
  r"$(0,1)$",
  [(r"$(1,0)$", r"swaps the coordinates"), (r"$(0,2)$", r"takes the centre at the greatest value of $r$"), (r"$(2,0)$", r"swaps the coordinates and takes the greatest value of $r$")],
  r"Multiply by $r$ and use $r^{2}=x^{2}+y^{2}$ and $y=r\sin\theta$ to convert a polar equation into Cartesian form.",
  r"$r^{2}=2r\sin\theta$ gives $x^{2}+y^{2}=2y$, that is $x^{2}+(y-1)^{2}=1$: a circle with centre $(0,1)$ and radius $1$.",
  (0, 1))
# 24
Q(["conic sections"], "faible", r"The focus of the parabola $y^{2}=12x$ is the point",
  r"$(3,0)$",
  [(r"$(12,0)$", r"takes the coefficient $12$ as the focal distance"), (r"$(6,0)$", r"takes $2a=12$ as $a=12/2$ and then doubles it"), (r"$(0,3)$", r"puts the focus on the $y$-axis")],
  r"The parabola $y^{2}=4ax$ has its focus at $(a,0)$.",
  r"$4a=12$ gives $a=3$, so the focus is $(3,0)$.",
  (3, 0))
# 25
Q(["lines and planes"], "moyenne", r"The distance from the point $(1,2,3)$ to the plane $2x-2y+z=3$ is",
  r"$\dfrac23$",
  [(r"$2$", r"forgets to divide by $\sqrt{2^{2}+(-2)^{2}+1^{2}}$"), (r"$\dfrac29$", r"divides by $9$ instead of its square root"), (r"$\dfrac43$", r"adds the constant $3$ instead of subtracting it")],
  r"The distance from $(x_{1},y_{1},z_{1})$ to the plane $ax+by+cz=d$ is $\dfrac{|ax_{1}+by_{1}+cz_{1}-d|}{\sqrt{a^{2}+b^{2}+c^{2}}}$.",
  r"$|2(1)-2(2)+3-3|=2$ and $\sqrt{4+4+1}=3$, so the distance is $\dfrac23$.",
  2 / 3)
# 26
Q(["matrix algebra", "determinants and inverses"], "moyenne", r"The inverse of $\begin{pmatrix}3&1\\5&2\end{pmatrix}$ is",
  r"$\begin{pmatrix}2&-1\\-5&3\end{pmatrix}$",
  [(r"$\begin{pmatrix}2&1\\5&3\end{pmatrix}$", r"swaps the diagonal but forgets to change the signs of the other entries"), (r"$\begin{pmatrix}-2&1\\5&-3\end{pmatrix}$", r"reverses the sign of the whole matrix"),
   (r"$\begin{pmatrix}3&-1\\-5&2\end{pmatrix}$", r"changes the signs of the other entries but forgets to swap the diagonal")],
  r"For $\begin{pmatrix}a&b\\c&d\end{pmatrix}$ the inverse is $\dfrac{1}{ad-bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}$.",
  r"The determinant is $3\times2-1\times5=1$, so the inverse is $\begin{pmatrix}2&-1\\-5&3\end{pmatrix}$.",
  (2, -1, -5, 3))
# 27
Q(["permutation groups"], "faible", r"The order of the permutation $(1\ 2\ 3)(4\ 5)$ in the symmetric group $S_{5}$ is",
  r"$6$",
  [(r"$5$", r"counts the points moved"), (r"$3$", r"takes the longest cycle"), (r"$2$", r"takes the shortest cycle")],
  r"The order of a permutation written as disjoint cycles is the least common multiple of the lengths of its cycles.",
  r"The cycles have lengths $3$ and $2$, so the order is $\mathrm{lcm}(3,2)=6$.",
  6)
# 28
Q(["complex numbers"], "moyenne", r"In the Argand diagram, the locus of the points $z$ such that $|z-2i|=|z+2|$ is the line",
  r"$y=-x$",
  [(r"$y=x$", r"makes a sign error when expanding $(y-2)^{2}$"), (r"$y=-x+1$", r"loses a factor $4$ when simplifying"), (r"$x=-1$", r"cancels the terms in $y$ by mistake")],
  r"Write $z=x+iy$ and square both sides: $|z-a|^{2}=(x-\text{Re}\,a)^{2}+(y-\text{Im}\,a)^{2}$.",
  r"$|z-2i|^{2}=x^{2}+(y-2)^{2}$ and $|z+2|^{2}=(x+2)^{2}+y^{2}$. Equating: $-4y+4=4x+4$, so $y=-x$.",
  (-1, 0))
# 29
Q(["simple harmonic motion of a particle"], "faible", r"A particle moves with simple harmonic motion given by $\ddot x=-16x$, with amplitude $0.5\ \text{m}$. Its maximum speed is",
  r"$2\ \text{m s}^{-1}$",
  [(r"$8\ \text{m s}^{-1}$", r"multiplies the amplitude by $\omega^{2}=16$, which is the maximum acceleration"), (r"$4\ \text{m s}^{-1}$", r"takes $\omega$ as the maximum speed"), (r"$0.125\ \text{m s}^{-1}$", r"divides the amplitude by $\omega$")],
  r"For $\ddot x=-\omega^{2}x$ with amplitude $A$, the maximum speed is $A\omega$ (at the centre) and the maximum acceleration is $A\omega^{2}$.",
  r"$\omega^{2}=16$, so $\omega=4$ and the maximum speed is $A\omega=0.5\times4=2\ \text{m s}^{-1}$.",
  2)
# 30
Q(["numerical solution of differential equations"], "faible", r"Euler's method with step $h=0.5$ is applied to $\dfrac{dy}{dx}=2xy$ with $y(0)=1$. The estimate of $y(1)$ is",
  r"$1.5$",
  [(r"$1$", r"stops after the first step"), (r"$2$", r"uses the slope at the end of the second step instead of its start"), (r"$1.25$", r"halves the step length in the second step")],
  r"Euler's method: $y_{n+1}=y_{n}+h\,f(x_{n},y_{n})$, with the slope evaluated at the start of the step.",
  r"$y_{1}=1+0.5\times f(0,1)=1+0.5\times0=1$ at $x=0.5$. Then $y_{2}=1+0.5\times f(0.5,1)=1+0.5\times1=1.5$ at $x=1$.",
  1.5)
# 31
Q(["maclaurin series"], "faible", r"In the Maclaurin series of $e^{2x}$ the coefficient of $x^{3}$ is",
  r"$\dfrac43$",
  [(r"$\dfrac16$", r"forgets the factor $2^{3}$"), (r"$\dfrac83$", r"divides by $3$ instead of $3!$"), (r"$8$", r"forgets to divide by $3!$")],
  r"The coefficient of $x^{n}$ in the Maclaurin series of $f$ is $\dfrac{f^{(n)}(0)}{n!}$; for $e^{kx}$ it is $\dfrac{k^{n}}{n!}$.",
  r"$f^{(3)}(x)=8e^{2x}$, so $f^{(3)}(0)=8$ and the coefficient is $\dfrac{8}{3!}=\dfrac43$.",
  4 / 3)
# 32
Q(["recurrence relations"], "moyenne", r"The sequence defined by $u_{1}=2$ and $u_{n+1}=3u_{n}-2$ has the general term $u_{n}=$",
  r"$3^{n-1}+1$",
  [(r"$3^{n}+1$", r"does not adjust the constant to the first term"), (r"$2\times3^{n-1}$", r"ignores the constant $-2$ in the recurrence"), (r"$3^{n-1}-1$", r"takes the constant solution as $-1$")],
  r"For $u_{n+1}=au_{n}+b$ with $a\ne1$, write $u_{n}=Aa^{n}+k$ where $k=ak+b$, then use the first term to find $A$.",
  r"The constant solution satisfies $k=3k-2$, so $k=1$ and $u_{n}=A\times3^{n}+1$. From $u_{1}=2$: $3A+1=2$, so $A=\tfrac13$ and $u_{n}=3^{n-1}+1$. Check: $u_{2}=4=3\times2-2$.",
  82)
# 33
Q(["probability distributions", "expectation and variance"], "moyenne",
  r"The random variable $X$ is binomial with $n=8$ and $p=0.25$. Which of the following statements are true?" "\n\n" r"1. $E(X)=2$" "\n" r"2. $\mathrm{Var}(X)=1.5$" "\n" r"3. $P(X=0)=0.25^{8}$",
  r"1 and 2 only",
  [(r"2 and 3 only", r"accepts statement 3 but rejects the correct expectation in statement 1"), (r"1 and 3 only", r"treats $P(X=0)=p^{8}$ as correct and misses $\mathrm{Var}(X)=npq$"), (r"1, 2 and 3", r"accepts statement 3, which uses $p$ instead of $q=0.75$")],
  r"For $X\sim B(n,p)$: $E(X)=np$, $\mathrm{Var}(X)=np(1-p)$ and $P(X=0)=(1-p)^{n}$.",
  r"$E(X)=8\times0.25=2$, so statement 1 is true. $\mathrm{Var}(X)=8\times0.25\times0.75=1.5$, so statement 2 is true. $P(X=0)=0.75^{8}$, not $0.25^{8}$, so statement 3 is false. Only $1$ and $2$ are true.",
  (1, 1, 0))
# 34
Q(["normal distribution"], "faible", r"Given that $\Phi(1.2)=0.8849$, the probability that a standard normal variable $Z$ exceeds $1.2$ is",
  r"$0.1151$",
  [(r"$0.8849$", r"gives $P(Z<1.2)$ instead of $P(Z>1.2)$"), (r"$0.2302$", r"doubles the upper tail as for a two-sided probability"), (r"$0.3849$", r"subtracts $0.5$ from $\Phi(1.2)$")],
  r"For a standard normal variable $P(Z>z)=1-\Phi(z)$.",
  r"$P(Z>1.2)=1-\Phi(1.2)=1-0.8849=0.1151$.",
  0.1151)
# 35
Q(["limits of functions"], "moyenne", r"$\displaystyle\lim_{x\to0}\dfrac{1-\cos2x}{x^{2}}$ is equal to",
  r"$2$",
  [(r"$0$", r"substitutes $x=0$ and reads the numerator only"), (r"$\dfrac12$", r"uses $1-\cos u\approx\tfrac{u^{2}}{2}$ with $u=x$ instead of $u=2x$"), (r"$4$", r"drops the factor $\tfrac12$ of $1-\cos u\approx\tfrac{u^{2}}{2}$")],
  r"Near $0$, $1-\cos u\approx\dfrac{u^{2}}{2}$; here $u=2x$. Equivalently, apply l'Hôpital's rule twice.",
  r"$1-\cos2x\approx\dfrac{(2x)^{2}}{2}=2x^{2}$, so the quotient tends to $2$. By l'Hôpital: $\dfrac{2\sin2x}{2x}\to\dfrac{4\cos2x}{2}\to2$.",
  2)
# 36
Q(["arc length"], "elevee", r"The length of the curve $y=x^{3/2}$ from $x=0$ to $x=4$ is",
  r"$\dfrac{8}{27}\left(10^{3/2}-1\right)$",
  [(r"$\dfrac{8}{27}\times10^{3/2}$", r"omits the contribution of the lower limit"), (r"$\dfrac{4}{9}\left(10^{3/2}-1\right)$", r"uses the wrong constant factor when integrating $\sqrt{1+\tfrac94x}$"), (r"$\dfrac{2}{3}\left(10^{3/2}-1\right)$", r"forgets to divide by the derivative $\tfrac94$ of the inner function")],
  r"The length of the curve $y=f(x)$ from $x=a$ to $x=b$ is $\displaystyle\int_{a}^{b}\sqrt{1+\left(\dfrac{dy}{dx}\right)^{2}}\,dx$.",
  r"$\dfrac{dy}{dx}=\tfrac32x^{1/2}$, so $1+\left(\dfrac{dy}{dx}\right)^{2}=1+\tfrac94x$. Then $s=\displaystyle\int_{0}^{4}\sqrt{1+\tfrac94x}\,dx=\tfrac49\times\tfrac23\left[\left(1+\tfrac94x\right)^{3/2}\right]_{0}^{4}=\tfrac{8}{27}\left(10^{3/2}-1\right)\approx9.07$.",
  8 / 27 * (10 ** 1.5 - 1))
# 37
Q(["moments of inertia"], "faible", r"A uniform disc of mass $2\ \text{kg}$ and radius $0.3\ \text{m}$ rotates about the axis through its centre perpendicular to its plane. Its moment of inertia about this axis is",
  r"$0.09\ \text{kg m}^{2}$",
  [(r"$0.18\ \text{kg m}^{2}$", r"uses $MR^{2}$ instead of $\tfrac12MR^{2}$"), (r"$0.045\ \text{kg m}^{2}$", r"uses $\tfrac14MR^{2}$, the value for a diameter"), (r"$0.6\ \text{kg m}^{2}$", r"multiplies the mass by the radius")],
  r"For a uniform disc of mass $M$ and radius $R$, the moment of inertia about the axis through its centre perpendicular to its plane is $\tfrac12MR^{2}$.",
  r"$I=\tfrac12\times2\times0.3^{2}=0.09\ \text{kg m}^{2}$.",
  0.09)
# 38
Q(["coefficient of restitution"], "moyenne", r"A ball is dropped from a height of $2\ \text{m}$ onto a horizontal floor. The coefficient of restitution between the ball and the floor is $0.5$. The height of the first rebound is",
  r"$0.5\ \text{m}$",
  [(r"$1\ \text{m}$", r"multiplies the height by $e$ instead of $e^{2}$"), (r"$0.25\ \text{m}$", r"gives $e^{2}$ without multiplying by the height"), (r"$0.125\ \text{m}$", r"applies the factor $e^{2}$ twice, as for the second rebound")],
  r"The speed after a bounce is $e$ times the speed before; heights are proportional to the square of the speed, so a rebound height is $e^{2}h$.",
  r"The speed just before impact is $v=\sqrt{2gh}$ and the speed after is $ev$. The rebound height is $\dfrac{(ev)^{2}}{2g}=e^{2}h=0.25\times2=0.5\ \text{m}$.",
  0.5)
# 39
Q(["motion in a resisting medium"], "faible", r"A particle of mass $2\ \text{kg}$ falls through a medium that exerts a resistance of $0.5v$ newtons, where $v\ \text{m s}^{-1}$ is its speed. Taking $g=9.8\ \text{m s}^{-2}$, the terminal speed is",
  r"$39.2\ \text{m s}^{-1}$",
  [(r"$9.8\ \text{m s}^{-1}$", r"takes the acceleration of free fall as the speed"), (r"$19.6\ \text{m s}^{-1}$", r"gives the weight without dividing by $0.5$"), (r"$4.9\ \text{m s}^{-1}$", r"multiplies the weight by $0.5$ instead of dividing")],
  r"At terminal speed the acceleration is zero, so the resistance equals the weight: $kv=mg$.",
  r"$0.5v=2\times9.8$, so $v=\dfrac{19.6}{0.5}=39.2\ \text{m s}^{-1}$.",
  39.2)
# 40
Q(["systems of forces"], "faible", r"Two forces of magnitudes $3\ \text{N}$ and $4\ \text{N}$ act at a point at right angles to each other. The magnitude of their resultant is",
  r"$5\ \text{N}$",
  [(r"$7\ \text{N}$", r"adds the magnitudes, which is the case of forces in the same direction"), (r"$1\ \text{N}$", r"subtracts the magnitudes, which is the case of opposite forces"), (r"$\sqrt7\ \text{N}$", r"subtracts the squares instead of adding them")],
  r"The resultant of two perpendicular forces has magnitude $\sqrt{F_{1}^{2}+F_{2}^{2}}$ by Pythagoras.",
  r"$R=\sqrt{3^{2}+4^{2}}=\sqrt{25}=5\ \text{N}$.",
  5)
# 41
Q(["probability distributions"], "faible", r"The discrete random variable $X$ takes the values $1,2,4$ with $P(X=x)=\dfrac{c}{x}$. The value of $c$ is",
  r"$\dfrac47$",
  [(r"$\dfrac13$", r"gives equal probabilities to the three values"), (r"$\dfrac74$", r"inverts the sum of the terms"), (r"$\dfrac{1}{7}$", r"forgets the denominators $x$ in the sum")],
  r"The probabilities of all the values of a discrete random variable add up to $1$, which fixes the constant.",
  r"$c\left(1+\tfrac12+\tfrac14\right)=1$, so $c\times\tfrac74=1$ and $c=\tfrac47$.",
  4 / 7)
# 42
Q(["hyperbolic functions"], "faible", r"$\dfrac{d}{dx}\left(\tanh2x\right)$ is equal to",
  r"$2\,\mathrm{sech}^{2}2x$",
  [(r"$\mathrm{sech}^{2}2x$", r"forgets the chain rule factor $2$"), (r"$2\cosh^{2}2x$", r"confuses $\mathrm{sech}$ with $\cosh$"), (r"$-2\,\mathrm{sech}^{2}2x$", r"inserts a minus sign, as in the derivative of $\coth$")],
  r"$\dfrac{d}{dx}\tanh u=\mathrm{sech}^{2}u\,\dfrac{du}{dx}$.",
  r"With $u=2x$: $\dfrac{d}{dx}\tanh2x=\mathrm{sech}^{2}(2x)\times2=2\,\mathrm{sech}^{2}2x$.",
  0.3)
# 43
Q(["integration techniques"], "faible", r"$\displaystyle\int_{0}^{1}xe^{x^{2}}\,dx$ is equal to",
  r"$\dfrac{e-1}{2}$",
  [(r"$e-1$", r"forgets the factor $\tfrac12$ from the substitution $u=x^{2}$"), (r"$\dfrac{e}{2}$", r"omits the lower limit"), (r"$\dfrac{e+1}{2}$", r"adds the lower limit value instead of subtracting it")],
  r"Substitute $u=x^{2}$, so $du=2x\,dx$ and the limits become $u=0$ and $u=1$.",
  r"$\displaystyle\int_{0}^{1}xe^{x^{2}}dx=\tfrac12\int_{0}^{1}e^{u}du=\tfrac12(e-1)$.",
  (2.718281828459045 - 1) / 2)
# 44
Q(["complex numbers", "de moivre theorem"], "moyenne", r"$(-1+i)^{6}$ is equal to",
  r"$8i$",
  [(r"$-8i$", r"takes the argument as $-\tfrac{3\pi}{4}$ for this point of the second quadrant"), (r"$8$", r"ends the argument $\tfrac{9\pi}{2}$ on the real axis"), (r"$64i$", r"takes the modulus as $2$")],
  r"Convert to modulus-argument form, raise the modulus to the power and multiply the argument by the power.",
  r"$-1+i=\sqrt2\left(\cos\tfrac{3\pi}{4}+i\sin\tfrac{3\pi}{4}\right)$, so $(-1+i)^{6}=(\sqrt2)^{6}\left(\cos\tfrac{9\pi}{2}+i\sin\tfrac{9\pi}{2}\right)=8\left(\cos\tfrac{\pi}{2}+i\sin\tfrac{\pi}{2}\right)=8i$.",
  complex(0, 8))
# 45
Q(["curve sketching"], "faible", r"The stationary point of the curve $y=xe^{-x}$ is",
  r"$\left(1,\dfrac1e\right)$",
  [(r"$(1,e)$", r"evaluates $e^{-x}$ as $e^{x}$ at the stationary point"), (r"$(0,0)$", r"takes the point where the curve meets the axes"), (r"$\left(-1,-e\right)$", r"solves $1+x=0$ because of a sign slip in the derivative")],
  r"A stationary point satisfies $\dfrac{dy}{dx}=0$; use the product rule for $xe^{-x}$.",
  r"$\dfrac{dy}{dx}=e^{-x}-xe^{-x}=(1-x)e^{-x}$, which is zero only at $x=1$. Then $y=e^{-1}=\tfrac1e$: the stationary point is $\left(1,\tfrac1e\right)$.",
  (1, 0.36787944117144233))
# 46
Q(["linear transformations"], "faible", r"The linear transformation with matrix $\begin{pmatrix}0&-1\\1&0\end{pmatrix}$ maps the point $(2,1)$ to",
  r"$(-1,2)$",
  [(r"$(1,-2)$", r"applies the matrix of the opposite rotation"), (r"$(1,2)$", r"changes only one sign"), (r"$(-2,1)$", r"changes the first coordinate only")],
  r"The image of the point $(x,y)$ is $\begin{pmatrix}a&b\\c&d\end{pmatrix}\begin{pmatrix}x\\y\end{pmatrix}=\begin{pmatrix}ax+by\\cx+dy\end{pmatrix}$.",
  r"$\begin{pmatrix}0&-1\\1&0\end{pmatrix}\begin{pmatrix}2\\1\end{pmatrix}=\begin{pmatrix}0\times2-1\times1\\1\times2+0\times1\end{pmatrix}=\begin{pmatrix}-1\\2\end{pmatrix}$: a quarter turn anticlockwise.",
  (-1, 2))
# 47
Q(["propositional logic"], "moyenne", r"The statement $p\wedge(p\Rightarrow q)$ is logically equivalent to",
  r"$p\wedge q$",
  [(r"$p\vee q$", r"confuses conjunction and disjunction"), (r"$q$", r"forgets that the statement is false when $p$ is false"), (r"$p\Rightarrow q$", r"drops the conjunct $p$")],
  r"Build the truth table: $p\Rightarrow q$ is false only when $p$ is true and $q$ is false; $p\wedge A$ is true only when both $p$ and $A$ are true.",
  r"If $p$ is false, the statement is false. If $p$ is true, $p\Rightarrow q$ has the value of $q$, so the statement has the value of $q$. The statement is true exactly when $p$ and $q$ are both true, which is $p\wedge q$.",
  (1, 0, 0, 0))
# 48
Q(["group theory"], "moyenne", r"The number of generators of a cyclic group of order $12$ is",
  r"$4$",
  [(r"$12$", r"counts every element of the group"), (r"$6$", r"takes half of the elements"), (r"$2$", r"counts the prime factors with their multiplicity")],
  r"In a cyclic group of order $n$ generated by $g$, the element $g^{k}$ is a generator exactly when $\gcd(k,n)=1$, so there are $\varphi(n)$ generators.",
  r"The generators are $g^{k}$ with $\gcd(k,12)=1$, that is $k=1,5,7,11$. There are $4$ of them.",
  4)
# 49
Q(["series convergence"], "faible", r"$\displaystyle\sum_{n=1}^{\infty}\dfrac{2}{3^{n}}$ is equal to",
  r"$1$",
  [(r"$3$", r"starts the sum at $n=0$"), (r"$\dfrac23$", r"gives the first term only"), (r"$2$", r"uses the numerator as the sum")],
  r"A geometric series with first term $a$ and common ratio $|r|<1$ has sum to infinity $\dfrac{a}{1-r}$.",
  r"The first term is $\tfrac23$ and the common ratio is $\tfrac13$, so the sum is $\dfrac{2/3}{1-1/3}=1$.",
  1)
# 50
Q(["second order differential equations"], "elevee", r"A particular integral of $\dfrac{d^{2}x}{dt^{2}}+4x=\cos2t$ is",
  r"$\dfrac{t}{4}\sin2t$",
  [(r"$\dfrac14\cos2t$", r"tries a multiple of the right-hand side, which already solves the homogeneous equation and gives $0$"), (r"$\dfrac{t}{4}\cos2t$", r"multiplies by $t$ but keeps the wrong trigonometric function"), (r"$\dfrac{t}{8}\sin2t$", r"loses a factor $2$ when differentiating $t\sin2t$ twice")],
  r"When the right-hand side is part of the complementary function, try a particular integral multiplied by $t$: here $x_{p}=t\,(a\cos2t+b\sin2t)$.",
  r"The complementary function contains $\cos2t$ and $\sin2t$, so try $x=t(a\cos2t+b\sin2t)$. Then $\ddot x=2(-2a\sin2t+2b\cos2t)+t\left(-4a\cos2t-4b\sin2t\right)$, so $\ddot x+4x=-4a\sin2t+4b\cos2t$. Equating with $\cos2t$: $a=0$ and $b=\tfrac14$, so $x_{p}=\dfrac{t}{4}\sin2t$.",
  0.25)
assert len(QS) == 50, len(QS)
