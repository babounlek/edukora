r"""Les 50 QCM de l'epreuve inedite GCE A Level Pure Mathematics Paper 1 n.1 (50 x 1 point, 90 min), commune aux options Mechanics et Statistics.

Structure mesuree sur les Paper 1 reels 2024 a 2026 (50 questions, themes de mathematiques pures melanges, 4 options, 40 a 50 % de faibles) ; aucune donnee
reprise d'un sujet reel ni des 50 QCM de Further Mathematics Paper 1. Chaque question : enonce, bonne reponse `key`, trois distracteurs avec l'erreur qui y mene,
rappel, resolution, valeur de controle `val` (recalculee par verifier_reponses_pm_p1.py). Les lettres des cles sont placees par le GENERATEUR, jamais tapees ici.
Chaines BRUTES (pas de guillemets droits a l'interieur).
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
Q(["mappings and composite functions"], "faible", r"The functions $f$ and $g$ are defined by $f(x)=3x-2$ and $g(x)=x^{2}+1$. The function $(f\circ g)(x)$ is",
  r"$3x^{2}+1$",
  [(r"$9x^{2}-12x+5$", r"applies the functions in the wrong order and finds $(g\circ f)(x)$"),
   (r"$(3x-2)(x^{2}+1)$", r"multiplies the two functions instead of composing them"),
   (r"$3x^{2}-2$", r"replaces $x$ by $x^{2}$ only and forgets the $+1$ inside $g$")],
  r"$(f\circ g)(x)=f\big(g(x)\big)$: substitute the whole expression $g(x)$ in place of $x$ in $f$.",
  r"$f\big(g(x)\big)=3(x^{2}+1)-2=3x^{2}+1$. Check at $x=2$: $g(2)=5$ and $f(5)=13=3(2)^{2}+1$.",
  13)
# 2
Q(["mappings and composite functions"], "moyenne", r"The function $f$ is defined by $f(x)=\dfrac{2x+3}{x-1}$ for $x\neq1$. Then $f^{-1}(x)$ is",
  r"$\dfrac{x+3}{x-2}$",
  [(r"$\dfrac{x-3}{x-2}$", r"moves the $+3$ across with the wrong sign when collecting the terms in $x$"),
   (r"$\dfrac{x-1}{2x+3}$", r"takes the reciprocal of $f(x)$ instead of solving for $x$"),
   (r"$\dfrac{x+3}{x+2}$", r"writes $x(y+2)$ instead of $x(y-2)$ after collecting the terms in $x$")],
  r"To find $f^{-1}$, write $y=f(x)$, make $x$ the subject, then exchange the letters $x$ and $y$.",
  r"$y(x-1)=2x+3$ gives $xy-y=2x+3$, so $x(y-2)=y+3$ and $x=\dfrac{y+3}{y-2}$. Hence $f^{-1}(x)=\dfrac{x+3}{x-2}$. Check: $f\!\left(\dfrac83\right)=\dfrac{16/3+3}{5/3}=5$, which is the value at $x=5$.",
  8 / 3)
# 3
Q(["logarithms"], "moyenne", r"The solution of the equation $\log_{2}x+\log_{2}(x-2)=3$ is $x=$",
  r"$4$",
  [(r"$-2$", r"keeps the root $x=-2$ although $\log_{2}(x-2)$ is not defined there"),
   (r"$5$", r"adds the arguments, writing $x+(x-2)=2^{3}$ instead of multiplying them"),
   (r"$8$", r"solves $\log_{2}x=3$ and forgets the second logarithm")],
  r"$\log_{a}M+\log_{a}N=\log_{a}(MN)$, and every root must be tested against the domain of the logarithms.",
  r"$\log_{2}\big[x(x-2)\big]=3$ gives $x^{2}-2x=8$, so $(x-4)(x+2)=0$. The root $x=-2$ is rejected because $x-2<0$. Hence $x=4$.",
  4)
# 4
Q(["asymptotes of rational functions"], "moyenne", r"The oblique asymptote of the curve $y=\dfrac{x^{2}+x-3}{x-1}$ is",
  r"$y=x+2$",
  [(r"$y=x+1$", r"divides $x^{2}+x$ by $x$ instead of dividing by $x-1$"),
   (r"$y=x-2$", r"makes a sign error in the second step of the long division"),
   (r"$x=1$", r"gives the vertical asymptote instead of the oblique one")],
  r"When the degree of the numerator is one more than the degree of the denominator, divide: the quotient $mx+c$ gives the oblique asymptote $y=mx+c$.",
  r"$\dfrac{x^{2}+x-3}{x-1}=x+2-\dfrac{1}{x-1}$ because $(x-1)(x+2)=x^{2}+x-2$. As $x\to\pm\infty$ the last term tends to $0$, so $y=x+2$.",
  (1, 2))
# 5
Q(["asymptotes of rational functions"], "faible", r"The number of vertical asymptotes of the curve $y=\dfrac{x^{2}-4}{(x-2)(x+3)}$ is",
  r"$1$",
  [(r"$2$", r"counts the factor $x-2$ although it cancels and leaves only a hole at $x=2$"),
   (r"$0$", r"believes that a cancelled factor removes every asymptote"),
   (r"$3$", r"also counts $x=-2$, which is a zero of the numerator")],
  r"A vertical asymptote occurs where the denominator is $0$ after cancelling the common factors; a cancelled factor gives a hole.",
  r"$y=\dfrac{(x-2)(x+2)}{(x-2)(x+3)}=\dfrac{x+2}{x+3}$ for $x\neq2$. Only $x=-3$ makes the denominator $0$ without cancelling, so there is exactly one vertical asymptote.",
  1)
# 6
Q(["polynomial division and factor theorem"], "faible", r"Given that $(x+2)$ is a factor of $2x^{3}+x^{2}+kx-6$, the value of $k$ is",
  r"$-9$",
  [(r"$9$", r"makes a sign error when solving $-18-2k=0$"),
   (r"$-7$", r"evaluates the polynomial at $x=2$ instead of $x=-2$"),
   (r"$-11$", r"drops the $x^{2}$ term when substituting $x=-2$")],
  r"Factor theorem: $(x-a)$ is a factor of $p(x)$ if and only if $p(a)=0$. Here $a=-2$.",
  r"$p(-2)=2(-8)+4-2k-6=-18-2k=0$, so $k=-9$.",
  -9)
# 7
Q(["inequalities and modulus"], "moyenne", r"The inequality $|x+2|<2|x-1|$ is satisfied when",
  r"$x<0$ or $x>4$",
  [(r"$0<x<4$", r"reverses the final inequality after squaring"),
   (r"$x>4$", r"keeps only the branch $x+2<2x-2$ and loses the branch $x<0$"),
   (r"$x<-4$ or $x>0$", r"reads the critical values $0$ and $-4$ instead of $0$ and $4$")],
  r"For two modulus expressions, square both sides (both are non-negative): $|u|<|v|$ is equivalent to $u^{2}<v^{2}$. Then factorise and use a sign table.",
  r"$(x+2)^{2}<4(x-1)^{2}$ gives $x^{2}+4x+4<4x^{2}-8x+4$, so $3x^{2}-12x>0$ and $x(x-4)>0$. The solution is $x<0$ or $x>4$.",
  (1, 1, 1, 0, 0, 0, 1, 1))
# 8
Q(["inequalities and modulus"], "moyenne", r"The inequality $\dfrac{2x-3}{x+1}\le1$ holds for",
  r"$-1<x\le4$",
  [(r"$-1\le x\le4$", r"includes $x=-1$, where the expression is not defined"),
   (r"$x\le-1$ or $x\ge4$", r"takes the outside of the critical values instead of the inside"),
   (r"$x\le4$", r"multiplies both sides by $x+1$ without considering its sign")],
  r"Never multiply an inequality by an expression whose sign is unknown. Move every term to one side, combine into one fraction and use a sign table, excluding the values that make the denominator $0$.",
  r"$\dfrac{2x-3}{x+1}-1\le0$ gives $\dfrac{x-4}{x+1}\le0$. The fraction is negative or zero between $-1$ and $4$, and $x=-1$ is excluded, so $-1<x\le4$.",
  (0, 0, 1, 1, 1, 1, 0, 0))
# 9
Q(["limits and continuity"], "faible", r"$\displaystyle\lim_{x\to2}\dfrac{x^{3}-8}{x^{2}-4}$ is equal to",
  r"$3$",
  [(r"$0$", r"substitutes $x=2$ in the numerator only and ignores the zero of the denominator"),
   (r"$12$", r"differentiates the numerator and leaves the denominator unchanged"),
   (r"$2$", r"factorises $x^{3}-8$ as $(x-2)(x^{2}+4)$")],
  r"When direct substitution gives $\tfrac00$, factorise numerator and denominator, cancel the common factor, then substitute.",
  r"$\dfrac{(x-2)(x^{2}+2x+4)}{(x-2)(x+2)}=\dfrac{x^{2}+2x+4}{x+2}\to\dfrac{12}{4}=3$.",
  3)
# 10
Q(["limits and continuity"], "moyenne", r"$\displaystyle\lim_{x\to0}\dfrac{1-\cos2x}{x^{2}}$ is",
  r"$2$",
  [(r"$4$", r"uses $1-\cos u\approx u^{2}$ and forgets the factor $\tfrac12$"),
   (r"$\dfrac12$", r"uses $1-\cos u\approx\tfrac{u^{2}}{2}$ with $u=x$ instead of $u=2x$"),
   (r"$0$", r"substitutes $x=0$ in the numerator and ignores the denominator")],
  r"Use $1-\cos2x=2\sin^{2}x$ and the standard limit $\displaystyle\lim_{x\to0}\dfrac{\sin x}{x}=1$.",
  r"$\dfrac{1-\cos2x}{x^{2}}=\dfrac{2\sin^{2}x}{x^{2}}=2\left(\dfrac{\sin x}{x}\right)^{2}\to2\times1=2$.",
  2)
# 11
Q(["limits and continuity"], "elevee", r"As $x$ tends to infinity, $\sqrt{x^{2}+4x}-x$ tends to",
  r"$2$",
  [(r"$0$", r"treats $\sqrt{x^{2}+4x}$ as equal to $x$ for large $x$"),
   (r"$4$", r"forgets the factor $2$ in the denominator after multiplying by the conjugate"),
   (r"$\infty$", r"reads the limit as $\infty-\infty=\infty$")],
  r"For a difference of square roots or of a root and a term, multiply and divide by the conjugate, then divide numerator and denominator by the highest power of $x$.",
  r"$\sqrt{x^{2}+4x}-x=\dfrac{4x}{\sqrt{x^{2}+4x}+x}=\dfrac{4}{\sqrt{1+4/x}+1}\to\dfrac{4}{2}=2$.",
  2)
# 12
Q(["propositional logic"], "faible", r"The negation of the statement $p\Rightarrow q$ is",
  r"$p\wedge\neg q$",
  [(r"$\neg p\wedge q$", r"negates the wrong two parts of the implication"),
   (r"$\neg p\Rightarrow\neg q$", r"gives the inverse, which is not the negation"),
   (r"$q\Rightarrow p$", r"gives the converse, which is not the negation")],
  r"$p\Rightarrow q$ is false in exactly one case: $p$ true and $q$ false. So $\neg(p\Rightarrow q)\equiv p\wedge\neg q$.",
  r"The truth table of $p\Rightarrow q$ in the cases $(T,T),(T,F),(F,T),(F,F)$ is $T,F,T,T$. Its negation is $F,T,F,F$, which is the table of $p\wedge\neg q$.",
  (0, 1, 0, 0))
# 13
Q(["propositional logic"], "faible", r"The number of combinations of truth values of $p$, $q$ and $r$ for which $\neg p\vee(q\wedge r)$ is true is",
  r"$5$",
  [(r"$4$", r"counts only the cases where $\neg p$ is true"),
   (r"$6$", r"adds the $4$ cases of $\neg p$ and the $2$ cases of $q\wedge r$ without removing the case counted twice"),
   (r"$1$", r"reads the connective as $\neg p\wedge q\wedge r$")],
  r"A disjunction is true when at least one part is true. Count the cases for each part and remove the overlap.",
  r"There are $8$ combinations. $\neg p$ is true in $4$ of them. When $p$ is true, $q\wedge r$ is true only for $q=r=T$, which adds $1$ more case. Total $4+1=5$.",
  5)
# 14
Q(["binary relations"], "faible", r"On the set $S=\{1,2,3\}$, the relation $R=\{(1,1),(2,2),(3,3),(1,2),(2,1),(2,3),(3,2)\}$ is",
  r"reflexive and symmetric but not transitive",
  [(r"an equivalence relation", r"checks reflexivity and symmetry only and misses that $(1,2)$ and $(2,3)$ need $(1,3)$"),
   (r"reflexive and transitive but not symmetric", r"reads the pairs in one direction only"),
   (r"symmetric and transitive but not reflexive", r"overlooks the pairs $(1,1)$, $(2,2)$ and $(3,3)$")],
  r"A relation is reflexive if $(a,a)\in R$ for all $a$, symmetric if $(a,b)\in R\Rightarrow(b,a)\in R$, and transitive if $(a,b),(b,c)\in R\Rightarrow(a,c)\in R$.",
  r"All three pairs $(a,a)$ are present, so $R$ is reflexive. Each pair has its reverse, so $R$ is symmetric. But $(1,2)$ and $(2,3)$ are in $R$ while $(1,3)$ is not, so $R$ is not transitive.",
  (1, 1, 0))
# 15
Q(["lines and planes"], "faible", r"The Cartesian equation of the plane through the point $(1,2,-1)$ with normal vector $2\mathbf i-\mathbf j+3\mathbf k$ is",
  r"$2x-y+3z=-3$",
  [(r"$2x-y+3z=3$", r"takes $z=1$ instead of $z=-1$ when evaluating $\mathbf n\cdot\mathbf a$"),
   (r"$2x-y+3z=1$", r"changes the sign of the $y$ product and gets $2+2-3$"),
   (r"$2x-y+3z=4$", r"adds the components of the normal vector, $2-1+3$")],
  r"A plane through the point with position vector $\mathbf a$ and with normal $\mathbf n$ has equation $\mathbf r\cdot\mathbf n=\mathbf a\cdot\mathbf n$.",
  r"$\mathbf a\cdot\mathbf n=2(1)-1(2)+3(-1)=-3$, so the plane is $2x-y+3z=-3$.",
  -3)
# 16
Q(["lines and planes"], "moyenne", r"The line $\mathbf r=(\mathbf i+2\mathbf j)+\lambda(2\mathbf i+p\mathbf j+\mathbf k)$ is parallel to the plane $3x-2y+z=5$. The value of $p$ is",
  r"$\dfrac72$",
  [(r"$-\dfrac72$", r"sets $6+2p+1=0$, with the wrong sign on the $y$ term"),
   (r"$1$", r"sets the scalar product equal to $5$ instead of $0$"),
   (r"$3$", r"forgets the $z$ contribution and solves $6-2p=0$")],
  r"A line is parallel to a plane when its direction vector is perpendicular to the normal of the plane: $\mathbf d\cdot\mathbf n=0$.",
  r"$\mathbf d\cdot\mathbf n=2(3)+p(-2)+1(1)=7-2p=0$, so $p=\dfrac72$. The point $(1,2,0)$ gives $3-4=-1\neq5$, so the line is parallel to the plane and not contained in it.",
  3.5)
# 17
Q(["determinants and inverses"], "faible", r"The matrix $\begin{pmatrix}k&2\\3&k+1\end{pmatrix}$ is singular for",
  r"$k=2$ or $k=-3$",
  [(r"$k=-2$ or $k=3$", r"changes the sign of both roots after factorising $k^{2}+k-6$"),
   (r"$k=\pm\sqrt6$", r"reads the bottom right entry as $k$ instead of $k+1$"),
   (r"$k=6$ or $k=-1$", r"makes an error in the middle term and solves $k^{2}-5k-6=0$")],
  r"A square matrix is singular when its determinant is $0$. For $\begin{pmatrix}a&b\\c&d\end{pmatrix}$ the determinant is $ad-bc$.",
  r"$\det=k(k+1)-2\times3=k^{2}+k-6=(k-2)(k+3)$, which is $0$ for $k=2$ or $k=-3$.",
  (2, -3))
# 18
Q(["partial fractions"], "moyenne", r"$\dfrac{x^{2}+1}{x^{2}-1}$ is identically equal to",
  r"$1+\dfrac{1}{x-1}-\dfrac{1}{x+1}$",
  [(r"$1+\dfrac{1}{x-1}+\dfrac{1}{x+1}$", r"gets the sign of the second fraction wrong when evaluating at $x=-1$"),
   (r"$\dfrac{1}{x-1}-\dfrac{1}{x+1}$", r"omits the constant term that comes from equal degrees in numerator and denominator"),
   (r"$1+\dfrac{2}{x-1}-\dfrac{2}{x+1}$", r"forgets to halve the constants: they are $1$ and $-1$, not $2$ and $-2$")],
  r"When the numerator and denominator have the same degree, divide first to get a constant, then split the proper fraction that remains.",
  r"$\dfrac{x^{2}+1}{x^{2}-1}=1+\dfrac{2}{x^{2}-1}$ and $\dfrac{2}{(x-1)(x+1)}=\dfrac{1}{x-1}-\dfrac{1}{x+1}$. Check at $x=3$: $\dfrac{10}{8}=1+\dfrac12-\dfrac14$.",
  (1.25, -5 / 3, 17 / 15))
# 19
Q(["partial fractions"], "moyenne", r"In the partial fractions $\dfrac{4x-1}{(x+1)(x-2)^{2}}=\dfrac{A}{x+1}+\dfrac{B}{x-2}+\dfrac{C}{(x-2)^{2}}$, the value of $C$ is",
  r"$\dfrac73$",
  [(r"$7$", r"substitutes $x=2$ in the numerator but does not divide by the value of the other factor"),
   (r"$-\dfrac59$", r"gives the value of $A$ instead of $C$"),
   (r"$\dfrac53$", r"substitutes $x=-1$ into the numerator and divides by $x-2$")],
  r"For a repeated factor $(x-a)^{2}$, multiply the identity by $(x-a)^{2}$ and put $x=a$ to get the coefficient of $\dfrac{1}{(x-a)^{2}}$ directly.",
  r"Multiplying by $(x-2)^{2}$ and putting $x=2$: $C=\dfrac{4(2)-1}{2+1}=\dfrac73$.",
  7 / 3)
# 20
Q(["sum and product of roots"], "faible", r"The roots of $x^{2}-6x+4=0$ are $\alpha$ and $\beta$. Then $\alpha^{2}+\beta^{2}=$",
  r"$28$",
  [(r"$36$", r"uses $(\alpha+\beta)^{2}$ and forgets to subtract $2\alpha\beta$"),
   (r"$44$", r"adds $2\alpha\beta$ instead of subtracting it"),
   (r"$32$", r"subtracts $\alpha\beta$ instead of $2\alpha\beta$")],
  r"For $ax^{2}+bx+c=0$: $\alpha+\beta=-\dfrac ba$ and $\alpha\beta=\dfrac ca$. Then $\alpha^{2}+\beta^{2}=(\alpha+\beta)^{2}-2\alpha\beta$.",
  r"$\alpha+\beta=6$ and $\alpha\beta=4$, so $\alpha^{2}+\beta^{2}=36-8=28$. The roots are $3\pm\sqrt5$, and $(3+\sqrt5)^{2}+(3-\sqrt5)^{2}=2(9+5)=28$.",
  28)
# 21
Q(["indices and exponentials"], "faible", r"The solutions of $3^{2x}-4\cdot3^{x}+3=0$ are",
  r"$x=0$ and $x=1$",
  [(r"$x=1$ and $x=3$", r"solves for $3^{x}$ and forgets to return to $x$"),
   (r"$x=-1$ and $x=-3$", r"factorises as $(u+1)(u+3)$ with the signs wrong"),
   (r"$x=0$ and $x=3$", r"converts $3^{x}=1$ correctly but leaves $3^{x}=3$ as $x=3$")],
  r"Put $u=3^{x}$ to turn the equation into a quadratic in $u$, solve it, then solve $3^{x}=u$ for each root.",
  r"With $u=3^{x}$: $u^{2}-4u+3=0$, so $(u-1)(u-3)=0$. Then $3^{x}=1$ gives $x=0$ and $3^{x}=3$ gives $x=1$.",
  (0, 1))
# 22
Q(["indices and exponentials"], "faible", r"If $2^{x+1}\times4^{x}=32$, then $x=$",
  r"$\dfrac43$",
  [(r"$2$", r"treats $4^{x}$ as $2^{x}$"),
   (r"$\dfrac53$", r"forgets the $+1$ in the exponent of the first factor"),
   (r"$\dfrac{31}{3}$", r"equates the exponent $3x+1$ to $32$ instead of $5$")],
  r"Write every power with the same base, add the exponents in a product, then equate the exponents.",
  r"$4^{x}=2^{2x}$, so $2^{x+1}\cdot2^{2x}=2^{3x+1}=2^{5}$. Then $3x+1=5$ and $x=\dfrac43$.",
  4 / 3)
# 23
Q(["separation of variables"], "moyenne", r"Given that $\dfrac{dy}{dx}=\dfrac{x}{y}$ for $y>0$, and $y=2$ when $x=0$, then $y=$",
  r"$\sqrt{x^{2}+4}$",
  [(r"$\sqrt{x^{2}+2}$", r"puts $y=2$ into $\tfrac{y^{2}}{2}$ but forgets to double the constant"),
   (r"$\dfrac{x^{2}}{2}+2$", r"integrates $\tfrac xy$ with respect to $x$ as if $y$ were a constant"),
   (r"$\sqrt{2x^{2}+4}$", r"forgets the factor $\tfrac12$ when integrating $x\,dx$")],
  r"Separate the variables, $\displaystyle\int y\,dy=\int x\,dx$, integrate both sides and use the given condition to find the constant.",
  r"$\dfrac{y^{2}}{2}=\dfrac{x^{2}}{2}+c$. With $x=0$, $y=2$: $c=2$. So $y^{2}=x^{2}+4$ and $y=\sqrt{x^{2}+4}$ because $y>0$.",
  2.5)
# 24
Q(["first order differential equations"], "elevee", r"For $x>0$, the general solution of $x\dfrac{dy}{dx}-3y=x^{4}$ is",
  r"$y=x^{4}+Cx^{3}$",
  [(r"$y=\dfrac{x^{4}}{7}+\dfrac{C}{x^{3}}$", r"uses the integrating factor $x^{3}$ instead of $x^{-3}$"),
   (r"$y=x^{3}+Cx^{4}$", r"swaps the powers of $x$ in the particular and complementary parts"),
   (r"$y=x^{4}+C$", r"drops the term $-3y$ and integrates $\tfrac{dy}{dx}=x^{3}$")],
  r"Write the equation as $\dfrac{dy}{dx}+P(x)y=Q(x)$ and multiply by the integrating factor $e^{\int P\,dx}$, so that the left side becomes the derivative of a product.",
  r"Dividing by $x$: $\dfrac{dy}{dx}-\dfrac3xy=x^{3}$. The integrating factor is $e^{-3\ln x}=x^{-3}$, so $\dfrac{d}{dx}\left(x^{-3}y\right)=1$. Then $x^{-3}y=x+C$ and $y=x^{4}+Cx^{3}$.",
  (0, 0, 0),
  conseil=r"Check an answer by substituting it back: $y=x^{4}+Cx^{3}$ gives $x\,y'-3y=4x^{4}+3Cx^{3}-3x^{4}-3Cx^{3}=x^{4}$.")
# 25
Q(["circle geometry"], "faible", r"The equation of the tangent to the circle $x^{2}+y^{2}=25$ at the point $(3,4)$ is",
  r"$3x+4y=25$",
  [(r"$3x-4y=-7$", r"uses the gradient $+\tfrac34$ instead of $-\tfrac34$"),
   (r"$4x-3y=0$", r"gives the normal at $(3,4)$ instead of the tangent"),
   (r"$3x+4y=5$", r"writes $r$ instead of $r^{2}$ on the right-hand side")],
  r"The tangent at $(x_{1},y_{1})$ on $x^{2}+y^{2}=r^{2}$ is $xx_{1}+yy_{1}=r^{2}$; it is perpendicular to the radius.",
  r"The radius to $(3,4)$ has gradient $\dfrac43$, so the tangent has gradient $-\dfrac34$: $y-4=-\dfrac34(x-3)$, which gives $3x+4y=25$.",
  (5, 0))
# 26
Q(["circle geometry"], "moyenne", r"The points $A(1,2)$ and $B(7,10)$ are the ends of a diameter of a circle. The equation of the circle is",
  r"$(x-4)^{2}+(y-6)^{2}=25$",
  [(r"$(x-4)^{2}+(y-6)^{2}=100$", r"takes the length $AB=10$ as the radius"),
   (r"$(x-8)^{2}+(y-12)^{2}=25$", r"adds the coordinates of $A$ and $B$ instead of finding the midpoint"),
   (r"$(x+4)^{2}+(y+6)^{2}=25$", r"writes the centre with the signs reversed")],
  r"The centre is the midpoint of a diameter and the radius is half its length: $(x-a)^{2}+(y-b)^{2}=r^{2}$.",
  r"Centre $\left(\dfrac{1+7}{2},\dfrac{2+10}{2}\right)=(4,6)$. $AB=\sqrt{6^{2}+8^{2}}=10$, so $r=5$ and $r^{2}=25$.",
  (25, 25))
# 27
Q(["binomial expansion"], "faible", r"In the expansion of $(3-2x)^{6}$, the coefficient of $x^{3}$ is",
  r"$-4320$",
  [(r"$4320$", r"drops the minus sign of $(-2)^{3}$"),
   (r"$-1440$", r"uses $3^{2}$ instead of $3^{3}$"),
   (r"$2160$", r"uses $(-2)^{2}$ with the coefficient of $x^{3}$")],
  r"The term in $x^{r}$ of $(a+bx)^{n}$ is $\binom nr a^{n-r}b^{r}x^{r}$.",
  r"$\binom63\,3^{3}\,(-2)^{3}=20\times27\times(-8)=-4320$.",
  -4320)
# 28
Q(["trigonometric identities"], "faible", r"Given that $\sin\theta=\dfrac{5}{13}$ and $\theta$ is acute, $\cos2\theta$ equals",
  r"$\dfrac{119}{169}$",
  [(r"$\dfrac{120}{169}$", r"finds $\sin2\theta$ instead of $\cos2\theta$"),
   (r"$-\dfrac{119}{169}$", r"uses $2\sin^{2}\theta-1$ instead of $1-2\sin^{2}\theta$"),
   (r"$\dfrac{144}{169}$", r"finds $\cos^{2}\theta$ and does not use the double angle formula")],
  r"$\cos2\theta=1-2\sin^{2}\theta=2\cos^{2}\theta-1=\cos^{2}\theta-\sin^{2}\theta$.",
  r"$\cos2\theta=1-2\left(\dfrac{5}{13}\right)^{2}=1-\dfrac{50}{169}=\dfrac{119}{169}$.",
  119 / 169)
# 29
Q(["trigonometric equations"], "moyenne", r"The number of solutions of $2\sin^{2}x+\sin x-1=0$ for $0^{\circ}\le x\le360^{\circ}$ is",
  r"$3$",
  [(r"$2$", r"keeps only $\sin x=\tfrac12$ and rejects $\sin x=-1$"),
   (r"$4$", r"counts the solution $x=270^{\circ}$ twice"),
   (r"$1$", r"keeps only $\sin x=-1$ and rejects $\sin x=\tfrac12$")],
  r"Treat the equation as a quadratic in $\sin x$, factorise, and list every angle in the interval for each value of $\sin x$.",
  r"$(2\sin x-1)(\sin x+1)=0$. $\sin x=\tfrac12$ gives $30^{\circ}$ and $150^{\circ}$; $\sin x=-1$ gives $270^{\circ}$ only. Total $3$.",
  3)
# 30
Q(["harmonic form"], "moyenne", r"The maximum value of $5\cos x-12\sin x+3$ is",
  r"$16$",
  [(r"$13$", r"finds the amplitude $R=13$ and forgets the constant $3$"),
   (r"$20$", r"adds the coefficients $5+12+3$"),
   (r"$-4$", r"adds $5-12+3$ without finding the amplitude")],
  r"$a\cos x+b\sin x=R\cos(x-\alpha)$ with $R=\sqrt{a^{2}+b^{2}}$; its greatest value is $R$ and its least value is $-R$.",
  r"$R=\sqrt{5^{2}+12^{2}}=13$, so the expression lies between $3-13$ and $3+13$. The maximum is $16$.",
  16)
# 31
Q(["complex numbers"], "faible", r"Written in the form $a+bi$, $\dfrac{2+i}{1-3i}$ is",
  r"$-\dfrac{1}{10}+\dfrac{7}{10}i$",
  [(r"$\dfrac{5}{10}+\dfrac{7}{10}i$", r"replaces $i^{2}$ by $+1$ in the numerator"),
   (r"$\dfrac12-\dfrac12i$", r"multiplies the numerator by $1-3i$ but the denominator by its conjugate"),
   (r"$-\dfrac{1}{10}-\dfrac{7}{10}i$", r"gives the conjugate of the correct answer")],
  r"To divide complex numbers, multiply numerator and denominator by the conjugate of the denominator and use $i^{2}=-1$.",
  r"$\dfrac{(2+i)(1+3i)}{(1-3i)(1+3i)}=\dfrac{2+6i+i+3i^{2}}{10}=\dfrac{-1+7i}{10}$.",
  complex(-0.1, 0.7))
# 32
Q(["complex numbers"], "faible", r"The argument of the complex number $-\sqrt3+i$ is",
  r"$\dfrac{5\pi}{6}$",
  [(r"$\dfrac{\pi}{6}$", r"gives the reference angle and ignores the quadrant"),
   (r"$-\dfrac{\pi}{6}$", r"gives $\arctan\!\left(\dfrac{1}{-\sqrt3}\right)$ without correcting the quadrant"),
   (r"$\dfrac{7\pi}{6}$", r"places the number in the third quadrant")],
  r"Draw the Argand diagram: the argument is the angle from the positive real axis, so the quadrant decides which angle to take.",
  r"The point $(-\sqrt3,1)$ is in the second quadrant. The reference angle is $\arctan\dfrac{1}{\sqrt3}=\dfrac\pi6$, so the argument is $\pi-\dfrac\pi6=\dfrac{5\pi}{6}$.",
  5 * 3.141592653589793 / 6)
# 33
Q(["de moivre theorem"], "moyenne", r"The value of $\left(1+i\sqrt3\right)^{6}$ is",
  r"$64$",
  [(r"$-64$", r"uses the argument $\tfrac{\pi}{6}$ instead of $\tfrac{\pi}{3}$"),
   (r"$12$", r"multiplies the modulus by $6$ instead of raising it to the power $6$"),
   (r"$4096$", r"uses the modulus $4$ and forgets the square root in $\sqrt{1+3}$")],
  r"Write $z=r(\cos\theta+i\sin\theta)$; then $z^{n}=r^{n}(\cos n\theta+i\sin n\theta)$.",
  r"$|1+i\sqrt3|=2$ and the argument is $\dfrac\pi3$. So $z^{6}=2^{6}\left(\cos2\pi+i\sin2\pi\right)=64$.",
  64)
# 34
Q(["arithmetic progressions"], "faible", r"The 5th term of an arithmetic progression is $17$ and its 12th term is $38$. The sum of the first $20$ terms is",
  r"$670$",
  [(r"$610$", r"takes $a=17-5d=2$ instead of $a=17-4d=5$"),
   (r"$608$", r"sums only $19$ terms"),
   (r"$1340$", r"leaves out the factor $\tfrac12$ in $S_{n}=\tfrac n2\left[2a+(n-1)d\right]$")],
  r"$u_{n}=a+(n-1)d$ and $S_{n}=\dfrac n2\left[2a+(n-1)d\right]$.",
  r"$u_{12}-u_{5}=7d=21$, so $d=3$ and $a=17-4(3)=5$. Then $S_{20}=10\,(10+19\times3)=670$.",
  670)
# 35
Q(["geometric progressions"], "faible", r"The first term of a geometric progression is $12$ and its sum to infinity is $16$. The common ratio is",
  r"$\dfrac14$",
  [(r"$\dfrac34$", r"takes $r=\dfrac{a}{S_{\infty}}$"),
   (r"$\dfrac43$", r"takes $r=\dfrac{S_{\infty}}{a}$"),
   (r"$-\dfrac14$", r"uses $1+r$ instead of $1-r$ in the denominator")],
  r"For $|r|<1$, $S_{\infty}=\dfrac{a}{1-r}$.",
  r"$16=\dfrac{12}{1-r}$, so $1-r=\dfrac34$ and $r=\dfrac14$.",
  0.25)
# 36
Q(["definite integrals"], "faible", r"The area enclosed between the curve $y=x^{2}$ and the line $y=2x$ is",
  r"$\dfrac43$",
  [(r"$\dfrac83$", r"finds only the area under the curve $y=x^{2}$ from $0$ to $2$"),
   (r"$4$", r"finds only the area under the line from $0$ to $2$"),
   (r"$\dfrac{20}{3}$", r"adds the two areas instead of subtracting")],
  r"The area between two curves is $\displaystyle\int_{a}^{b}(y_{\text{upper}}-y_{\text{lower}})\,dx$, where $a$ and $b$ are the intersection points.",
  r"$x^{2}=2x$ gives $x=0$ or $x=2$, and the line is above the curve. Area $=\displaystyle\int_{0}^{2}(2x-x^{2})\,dx=\left[x^{2}-\dfrac{x^{3}}{3}\right]_{0}^{2}=4-\dfrac83=\dfrac43$.",
  4 / 3)
# 37
Q(["integration techniques"], "moyenne", r"The value of $\displaystyle\int_{0}^{1}xe^{2x}\,dx$ is",
  r"$\dfrac{e^{2}+1}{4}$",
  [(r"$\dfrac{e^{2}-1}{4}$", r"takes the lower-limit value $-\tfrac14$ as $+\tfrac14$"),
   (r"$\dfrac{e^{2}}{2}$", r"keeps only the term $\tfrac{xe^{2x}}{2}$"),
   (r"$\dfrac{e^{2}}{4}$", r"forgets to subtract the value at the lower limit")],
  r"Integration by parts: $\displaystyle\int u\,dv=uv-\int v\,du$. Choose $u$ so that it becomes simpler when differentiated.",
  r"With $u=x$ and $dv=e^{2x}dx$: $\displaystyle\int xe^{2x}dx=\dfrac{xe^{2x}}{2}-\dfrac{e^{2x}}{4}$. Between $0$ and $1$: $\left(\dfrac{e^{2}}{2}-\dfrac{e^{2}}{4}\right)-\left(0-\dfrac14\right)=\dfrac{e^{2}+1}{4}$.",
  (2.718281828459045 ** 2 + 1) / 4)
# 38
Q(["differentiation techniques"], "moyenne", r"The gradient of the curve $y=xe^{-2x}$ at the point where $x=1$ is",
  r"$-e^{-2}$",
  [(r"$3e^{-2}$", r"takes the derivative of $e^{-2x}$ as $2e^{-2x}$"),
   (r"$e^{-2}$", r"differentiates $x$ only and leaves $e^{-2x}$ unchanged"),
   (r"$2e^{-2}$", r"forgets the factor $-2$ from the chain rule in the second term")],
  r"Product rule: $(uv)'=u'v+uv'$, and the chain rule gives $\dfrac{d}{dx}e^{kx}=ke^{kx}$.",
  r"$\dfrac{dy}{dx}=e^{-2x}+x(-2)e^{-2x}=e^{-2x}(1-2x)$. At $x=1$: $e^{-2}(1-2)=-e^{-2}$.",
  -2.718281828459045 ** -2)
# 39
Q(["differentiation techniques", "curve sketching"], "faible", r"The curve $y=x^{3}-6x^{2}+9x+1$ has a local maximum at $x=$",
  r"$1$",
  [(r"$3$", r"identifies the local minimum instead of the local maximum"),
   (r"$2$", r"gives the point of inflection, where $\dfrac{d^{2}y}{dx^{2}}=0$"),
   (r"$0$", r"gives the point where the curve meets the $y$-axis")],
  r"Stationary points satisfy $\dfrac{dy}{dx}=0$; they are maxima where $\dfrac{d^{2}y}{dx^{2}}<0$.",
  r"$\dfrac{dy}{dx}=3x^{2}-12x+9=3(x-1)(x-3)$. $\dfrac{d^{2}y}{dx^{2}}=6x-12$ is $-6<0$ at $x=1$ (maximum) and $6>0$ at $x=3$ (minimum).",
  1)
# 40
Q(["matrix algebra"], "faible", r"If $\mathbf A=\begin{pmatrix}1&2\\0&1\end{pmatrix}$, then $\mathbf A^{3}=$",
  r"$\begin{pmatrix}1&6\\0&1\end{pmatrix}$",
  [(r"$\begin{pmatrix}1&8\\0&1\end{pmatrix}$", r"cubes each entry of $\mathbf A$ separately"),
   (r"$\begin{pmatrix}3&6\\0&3\end{pmatrix}$", r"computes $3\mathbf A$"),
   (r"$\begin{pmatrix}1&4\\0&1\end{pmatrix}$", r"stops after computing $\mathbf A^{2}$")],
  r"$\mathbf A^{3}=\mathbf A\cdot\mathbf A\cdot\mathbf A$ is a matrix product, not the cube of each entry.",
  r"$\mathbf A^{2}=\begin{pmatrix}1&4\\0&1\end{pmatrix}$ and $\mathbf A^{3}=\mathbf A^{2}\mathbf A=\begin{pmatrix}1&6\\0&1\end{pmatrix}$.",
  (1, 6, 0, 1))
# 41
Q(["matrix algebra", "determinants and inverses"], "faible", r"$\mathbf A$ and $\mathbf B$ are invertible $n\times n$ matrices. Then $(\mathbf{AB})^{-1}$ is equal to",
  r"$\mathbf B^{-1}\mathbf A^{-1}$",
  [(r"$\mathbf A^{-1}\mathbf B^{-1}$", r"keeps the original order of the factors"),
   (r"$\mathbf A^{-1}+\mathbf B^{-1}$", r"treats the inverse as if it distributed over a product like a sum"),
   (r"$\dfrac{1}{\mathbf A\mathbf B}$", r"writes a reciprocal, which does not exist for matrices")],
  r"The inverse of a product reverses the order: $(\mathbf{AB})^{-1}=\mathbf B^{-1}\mathbf A^{-1}$.",
  r"$(\mathbf{AB})\left(\mathbf B^{-1}\mathbf A^{-1}\right)=\mathbf A\left(\mathbf B\mathbf B^{-1}\right)\mathbf A^{-1}=\mathbf A\mathbf A^{-1}=\mathbf I$, so $\mathbf B^{-1}\mathbf A^{-1}$ is the inverse of $\mathbf{AB}$.",
  1)
# 42
Q(["scalar and vector products"], "moyenne", r"For $\mathbf a=2\mathbf i-\mathbf j+3\mathbf k$ and $\mathbf b=\mathbf i+4\mathbf j-2\mathbf k$, the vector product $\mathbf a\times\mathbf b$ equals",
  r"$-10\mathbf i+7\mathbf j+9\mathbf k$",
  [(r"$10\mathbf i-7\mathbf j-9\mathbf k$", r"finds $\mathbf b\times\mathbf a$"),
   (r"$-10\mathbf i-7\mathbf j+9\mathbf k$", r"forgets to reverse the sign of the $\mathbf j$ component"),
   (r"$-10\mathbf i+7\mathbf j-9\mathbf k$", r"reverses the sign of the $\mathbf k$ component")],
  r"$\mathbf a\times\mathbf b=(a_{2}b_{3}-a_{3}b_{2})\mathbf i+(a_{3}b_{1}-a_{1}b_{3})\mathbf j+(a_{1}b_{2}-a_{2}b_{1})\mathbf k$.",
  r"$\mathbf i$: $(-1)(-2)-3\times4=-10$. $\mathbf j$: $3\times1-2\times(-2)=7$. $\mathbf k$: $2\times4-(-1)\times1=9$. The result is perpendicular to both $\mathbf a$ and $\mathbf b$.",
  (-10, 7, 9))
# 43
Q(["scalar and vector products"], "moyenne", r"The angle $\theta$ between $\mathbf a=\mathbf i+2\mathbf j+2\mathbf k$ and $\mathbf b=2\mathbf i-3\mathbf j+6\mathbf k$ satisfies $\cos\theta=$",
  r"$\dfrac{8}{21}$",
  [(r"$\dfrac45$", r"adds the magnitudes $3+7$ in the denominator instead of multiplying them"),
   (r"$-\dfrac{16}{21}$", r"makes a sign error in the $\mathbf k$ product and gets $2-6-12$"),
   (r"$\dfrac{8}{441}$", r"divides by $|\mathbf a|^{2}|\mathbf b|^{2}$ instead of $|\mathbf a||\mathbf b|$")],
  r"$\cos\theta=\dfrac{\mathbf a\cdot\mathbf b}{|\mathbf a||\mathbf b|}$.",
  r"$\mathbf a\cdot\mathbf b=2-6+12=8$, $|\mathbf a|=3$ and $|\mathbf b|=7$. So $\cos\theta=\dfrac{8}{21}$.",
  8 / 21)
# 44
Q(["permutations and combinations"], "moyenne", r"The number of different arrangements of all the letters of the word $SEPTEMBER$ is",
  r"$60\,480$",
  [(r"$362\,880$", r"ignores the repeated letter $E$"),
   (r"$120\,960$", r"divides $9!$ by $3$ instead of $3!$"),
   (r"$30\,240$", r"also divides by $2!$ as if a second letter were repeated")],
  r"The number of arrangements of $n$ letters with repeats $p,q,\dots$ is $\dfrac{n!}{p!\,q!\cdots}$.",
  r"$SEPTEMBER$ has $9$ letters and the letter $E$ appears $3$ times, so the number is $\dfrac{9!}{3!}=\dfrac{362\,880}{6}=60\,480$.",
  60480)
# 45
Q(["newton raphson method"], "faible", r"The Newton-Raphson method is used to find a root of $x^{2}-7=0$ with first approximation $x_{0}=3$. The value of $x_{1}$ is",
  r"$\dfrac83$",
  [(r"$\dfrac{10}{3}$", r"adds $\dfrac{f(x_{0})}{f'(x_{0})}$ instead of subtracting it"),
   (r"$\dfrac52$", r"uses $f'(3)=4$ instead of $f'(3)=6$"),
   (r"$\dfrac73$", r"uses $\dfrac{7}{x_{0}}$ instead of the Newton-Raphson formula")],
  r"$x_{n+1}=x_{n}-\dfrac{f(x_{n})}{f'(x_{n})}$.",
  r"$f(x)=x^{2}-7$ and $f'(x)=2x$. $f(3)=2$ and $f'(3)=6$, so $x_{1}=3-\dfrac26=\dfrac83$.",
  8 / 3)
# 46
Q(["curve sketching"], "faible", r"The range of the function $f(x)=\dfrac{1}{x^{2}+1}$ for $x\in\mathbb R$ is",
  r"$0<f(x)\le1$",
  [(r"$0\le f(x)\le1$", r"includes $0$, which the function never reaches"),
   (r"$f(x)\ge1$", r"reverses the inequality and takes the maximum for a minimum"),
   (r"$f(x)>0$", r"ignores the upper bound reached at $x=0$")],
  r"To find a range, study the extreme values and the behaviour for large $|x|$.",
  r"$x^{2}+1\ge1$, so $\dfrac{1}{x^{2}+1}\le1$ with equality at $x=0$. The value $0$ is never reached because $\dfrac{1}{x^{2}+1}>0$ and it tends to $0$ as $|x|\to\infty$.",
  (1, 1))
# 47
Q(["parametric equations"], "faible", r"A curve is given by $x=t^{2}+1$ and $y=t^{3}-t$. The gradient of the curve at the point where $t=2$ is",
  r"$\dfrac{11}{4}$",
  [(r"$\dfrac{4}{11}$", r"inverts $\dfrac{dy/dt}{dx/dt}$"),
   (r"$11$", r"uses $\dfrac{dy}{dt}$ alone"),
   (r"$\dfrac65$", r"divides $y$ by $x$ at $t=2$")],
  r"$\dfrac{dy}{dx}=\dfrac{dy/dt}{dx/dt}$.",
  r"$\dfrac{dy}{dt}=3t^{2}-1=11$ and $\dfrac{dx}{dt}=2t=4$ at $t=2$. So the gradient is $\dfrac{11}{4}$.",
  2.75)
# 48
Q(["reduction to linear form"], "moyenne", r"Variables $x$ and $y$ are related by $y=ax^{b}$. A straight line is obtained by plotting $\ln y$ against $\ln x$, with gradient $3$ and vertical intercept $2$. Then",
  r"$a=e^{2}$ and $b=3$",
  [(r"$a=2$ and $b=3$", r"reads the intercept $2$ as $a$ instead of $\ln a$"),
   (r"$a=e^{3}$ and $b=2$", r"swaps the gradient and the intercept"),
   (r"$a=\ln2$ and $b=3$", r"takes the logarithm of the intercept instead of its exponential")],
  r"Take logarithms: $y=ax^{b}$ becomes $\ln y=b\ln x+\ln a$, a line with gradient $b$ and intercept $\ln a$.",
  r"$b=3$ and $\ln a=2$, so $a=e^{2}$. Check at $x=2$: $\ln y=3\ln2+2$, so $y=8e^{2}=ax^{b}$.",
  (3, 2))
# 49
Q(["quadratic equations and discriminant"], "moyenne", r"The equation $2x^{2}+kx+8=0$ has no real roots when",
  r"$-8 < k < 8$",
  [(r"$k<-8$ or $k>8$", r"gives the condition for two distinct real roots"),
   (r"$-4 < k < 4$", r"uses $k^{2}<ac$ and forgets the factor $4$ in $b^{2}-4ac$"),
   (r"$k<8$", r"solves $k^{2}<64$ as $k<8$ and loses the lower bound")],
  r"$ax^{2}+bx+c=0$ has no real roots when $b^{2}-4ac<0$.",
  r"$b^{2}-4ac=k^{2}-4(2)(8)=k^{2}-64<0$, so $k^{2}<64$ and $-8<k<8$.",
  (0, 0, 1, 1, 1, 0, 0))
# 50
Q(["permutations and combinations"], "moyenne", r"A committee of $4$ is chosen from $6$ men and $5$ women. The number of committees with at least $2$ women is",
  r"$215$",
  [(r"$150$", r"counts exactly $2$ women instead of at least $2$"),
   (r"$315$", r"subtracts only the committees with no woman and forgets those with exactly one woman"),
   (r"$230$", r"subtracts only the committees with exactly one woman and forgets those with no woman")],
  r"For 'at least', count the complement: all committees minus every unwanted case, and check that no unwanted case is forgotten.",
  r"Total $\binom{11}{4}=330$. No woman: $\binom64=15$. Exactly one woman: $5\times\binom63=100$. So $330-15-100=215$. Direct count: $\binom52\binom62+\binom53\binom61+\binom54=150+60+5=215$.",
  215)
