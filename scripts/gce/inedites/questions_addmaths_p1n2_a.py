r"""Questions 1 a 25 de l'epreuve inedite GCE O Level Additional Mathematics Paper 1 n.2 (voir generer_addmaths_p1n2.py).

Session n.2 : DONNEES NEUVES par rapport au Paper 1 n.1 et aux vrais sujets (aucune matrice, aucun point, aucune fonction repris).
Chaines BRUTES (r"..."). Ordre du syllabus 0575.
"""


def Q(n, themes, diff, stem, ok, bad, rappel, sol, piege=None, conseil=None, fig=None):
    return dict(n=n, themes=themes, diff=diff, stem=stem, ok=ok, bad=bad, rappel=rappel, sol=sol, piege=piege, conseil=conseil, fig=fig)


def questions():
    qs = []
    a = qs.append

    a(Q(1, ["indices and surds"], "faible",
        r"The value of $\left(\dfrac{27}{8}\right)^{-\frac{1}{3}}$ is",
        r"$\dfrac{2}{3}$", [r"$\dfrac{3}{2}$", r"$-\dfrac{2}{3}$", r"$\dfrac{4}{9}$"],
        r"A negative index gives the reciprocal, and an index $\dfrac{1}{n}$ is an $n^{\text{th}}$ root: $a^{-\frac{1}{3}}=\dfrac{1}{\sqrt[3]{a}}$.",
        r"$\left(\dfrac{27}{8}\right)^{-\frac{1}{3}}=\left(\dfrac{8}{27}\right)^{\frac{1}{3}}=\dfrac{\sqrt[3]{8}}{\sqrt[3]{27}}=\dfrac{2}{3}$.",
        r"$\dfrac{3}{2}$ ignores the negative sign of the index, which only turns the fraction upside down."))
    a(Q(2, ["indices and surds"], "faible",
        r"$\sqrt{75}-\sqrt{12}$ is equal to",
        r"$3\sqrt{3}$", [r"$\sqrt{63}$", r"$7\sqrt{3}$", r"$3$"],
        r"Write each surd with the largest square factor taken out, then collect the like surds.",
        r"$\sqrt{75}=\sqrt{25\times3}=5\sqrt{3}$ and $\sqrt{12}=\sqrt{4\times3}=2\sqrt{3}$. So $5\sqrt{3}-2\sqrt{3}=3\sqrt{3}$.",
        r"$\sqrt{75}-\sqrt{12}$ is not $\sqrt{75-12}=\sqrt{63}$: the square root of a difference is not the difference of square roots."))
    a(Q(3, ["logarithms and exponential equations"], "faible",
        r"The value of $\log_{2}40-\log_{2}5$ is",
        r"$3$", [r"$8$", r"$35$", r"$2$"],
        r"The difference of two logarithms of the same base is the logarithm of the quotient: $\log a-\log b=\log\dfrac{a}{b}$.",
        r"$\log_{2}40-\log_{2}5=\log_{2}\dfrac{40}{5}=\log_{2}8=3$, because $2^{3}=8$.",
        r"$8$ is the value of the quotient $\dfrac{40}{5}$, not of its logarithm."))
    a(Q(4, ["relations between roots and coefficients"], "moyenne",
        r"The roots of the equation $x^{2}-7x+5=0$ are $\alpha$ and $\beta$. The value of $\alpha^{2}+\beta^{2}$ is",
        r"$39$", [r"$49$", r"$59$", r"$29$"],
        r"Write the required expression with the sum and the product of the roots: $\alpha^{2}+\beta^{2}=(\alpha+\beta)^{2}-2\alpha\beta$.",
        r"$\alpha+\beta=7$ and $\alpha\beta=5$. $\alpha^{2}+\beta^{2}=7^{2}-2(5)=49-10=39$.",
        r"$49$ is $(\alpha+\beta)^{2}$ only; the term $-2\alpha\beta$ is needed."))
    a(Q(5, ["quadratic functions and discriminant"], "faible",
        r"The equation $kx^{2}-4x+1=0$ has equal roots. The value of $k$ is",
        r"$4$", [r"$1$", r"$2$", r"$16$"],
        r"A quadratic equation has equal roots when its discriminant is zero: $b^{2}-4ac=0$.",
        r"$(-4)^{2}-4(k)(1)=16-4k=0$, so $k=4$.",
        r"$16$ is $b^{2}$: the discriminant is $16-4k$, and it is $16-4k$ that equals zero."))
    a(Q(6, ["remainder and factor theorem"], "moyenne",
        r"The remainder when $4x^{3}-3x+5$ is divided by $(2x-1)$ is",
        r"$4$", [r"$6$", r"$31$", r"$5$"],
        r"The remainder on division of $f(x)$ by $(ax-b)$ is $f\left(\dfrac{b}{a}\right)$: it is found by substituting the value of $x$ that makes the divisor zero.",
        r"The divisor $2x-1$ is zero for $x=\dfrac{1}{2}$. $f\left(\dfrac{1}{2}\right)=4\left(\dfrac{1}{8}\right)-\dfrac{3}{2}+5=\dfrac{1}{2}-\dfrac{3}{2}+5=4$.",
        r"$f(1)=6$ and $f(2)=31$ are the remainders on division by $(x-1)$ and by $(x-2)$: the divisor $2x-1$ vanishes for $x=\dfrac{1}{2}$."))
    a(Q(7, ["remainder and factor theorem"], "moyenne",
        r"The cubic $x^{3}-2x^{2}+px+6$ is exactly divisible by $(x-3)$. The value of the constant $p$ is",
        r"$-5$", [r"$5$", r"$-15$", r"$15$"],
        r"If $(x-a)$ is a factor of $f(x)$ then $f(a)=0$. For the factor $(x-3)$ take $a=3$.",
        r"$f(3)=27-18+3p+6=15+3p=0$, so $p=-5$.",
        r"$15+3p=0$ gives $3p=-15$: the value $-15$ forgets to divide by the coefficient $3$ of $p$."))
    a(Q(8, ["arithmetic and geometric progressions"], "faible",
        r"The $10^{\text{th}}$ term of the arithmetic progression $4,\ 9,\ 14,\ \ldots$ is",
        r"$49$", [r"$54$", r"$44$", r"$45$"],
        r"The $n^{\text{th}}$ term of an arithmetic progression is $T_{n}=a+(n-1)d$.",
        r"$a=4$ and $d=5$. $T_{10}=4+9(5)=49$.",
        r"$54$ is $4+10(5)$: there are $9$ steps from the first term to the tenth, not $10$."))
    a(Q(9, ["arithmetic and geometric progressions"], "moyenne",
        r"The first term of an arithmetic progression is $2$ and the $20^{\text{th}}$ term is $59$. The sum of the first $20$ terms is",
        r"$610$", [r"$1220$", r"$305$", r"$590$"],
        r"The sum of the first $n$ terms is $S_{n}=\dfrac{n}{2}(a+l)$, where $l$ is the last term.",
        r"$S_{20}=\dfrac{20}{2}(2+59)=10\times61=610$.",
        r"$1220$ forgets the factor $\dfrac{1}{2}$ of the formula; $305$ divides by $2$ twice."))
    a(Q(10, ["arithmetic and geometric progressions"], "moyenne",
        r"The sum of the first $8$ terms of the geometric progression $3,\ 6,\ 12,\ \ldots$ is",
        r"$765$", [r"$768$", r"$384$", r"$1533$"],
        r"The sum of the first $n$ terms of a geometric progression is $S_{n}=\dfrac{a(r^{n}-1)}{r-1}$ for $r>1$.",
        r"$a=3$ and $r=2$. $S_{8}=\dfrac{3(2^{8}-1)}{2-1}=3\times255=765$.",
        r"$384$ is only the $8^{\text{th}}$ term ($3\times2^{7}$); $1533$ is the sum of $9$ terms."))
    a(Q(11, ["arithmetic and geometric progressions"], "moyenne",
        r"The sum to infinity of a geometric progression with first term $10$ and common ratio $-\dfrac{1}{4}$ is",
        r"$8$", [r"$\dfrac{40}{3}$", r"$40$", r"$5$"],
        r"For $|r|<1$ the sum to infinity is $S_{\infty}=\dfrac{a}{1-r}$.",
        r"$S_{\infty}=\dfrac{10}{1-\left(-\frac{1}{4}\right)}=\dfrac{10}{\frac{5}{4}}=10\times\dfrac{4}{5}=8$.",
        r"$1-r=1-\left(-\dfrac{1}{4}\right)=\dfrac{5}{4}$: the minus sign of the ratio turns into a plus. $\dfrac{40}{3}$ uses $1-\dfrac{1}{4}$."))
    a(Q(12, ["binomial expansion (additional maths)"], "moyenne",
        r"The coefficient of $x^{3}$ in the expansion of $(3-x)^{5}$ is",
        r"$-90$", [r"$90$", r"$-270$", r"$270$"],
        r"The term in $x^{r}$ of $(a+b)^{n}$ is $\dbinom{n}{r}a^{n-r}b^{r}$. Here $a=3$ and $b=-x$.",
        r"$\dbinom{5}{3}(3)^{2}(-x)^{3}=10\times9\times(-x^{3})=-90x^{3}$.",
        r"The power $(-x)^{3}$ is negative, and the number $3$ is raised to the power $5-3=2$, not $3$ ($\pm270$)."))
    a(Q(13, ["binomial expansion (additional maths)"], "moyenne",
        r"The first three terms in the expansion of $\left(1+\dfrac{x}{2}\right)^{6}$ in ascending powers of $x$ are",
        r"$1+3x+\dfrac{15}{4}x^{2}$", [r"$1+3x+15x^{2}$", r"$1+6x+15x^{2}$", r"$1+3x+\dfrac{15}{2}x^{2}$"],
        r"$(1+y)^{n}=1+ny+\dfrac{n(n-1)}{2}y^{2}+\ldots$ with $y=\dfrac{x}{2}$: the whole of $\dfrac{x}{2}$ is raised to each power.",
        r"$1+6\left(\dfrac{x}{2}\right)+15\left(\dfrac{x}{2}\right)^{2}=1+3x+\dfrac{15}{4}x^{2}$.",
        r"$\left(\dfrac{x}{2}\right)^{2}=\dfrac{x^{2}}{4}$: forgetting to square the $2$ gives $15x^{2}$."))
    a(Q(14, ["permutations and combinations (additional maths)"], "faible",
        r"The number of different arrangements of the letters of the word BANANA is",
        r"$60$", [r"$720$", r"$120$", r"$30$"],
        r"If a letter appears $p$ times and another $q$ times among $n$ letters, the number of arrangements is $\dfrac{n!}{p!\,q!}$.",
        r"BANANA has $6$ letters with A three times and N twice. $\dfrac{6!}{3!\,2!}=\dfrac{720}{12}=60$.",
        r"$720=6!$ counts the repeated letters as if they were different."))
    a(Q(15, ["permutations and combinations (additional maths)"], "moyenne",
        r"A team of $4$ students is chosen from $10$ students. The number of teams that contain two particular students is",
        r"$28$", [r"$210$", r"$70$", r"$56$"],
        r"If some members are already chosen, only the other places remain to be filled from the other people.",
        r"The two particular students are in the team, so $2$ more students are chosen from the other $8$: $\dbinom{8}{2}=28$.",
        r"$210=\dbinom{10}{4}$ counts all the teams, with or without the two students."))
    a(Q(16, ["trigonometric ratios and quadrants"], "faible",
        r"Given that $\theta$ is acute and $\sin\theta=\dfrac{3}{5}$, the value of $\tan(180^{\circ}-\theta)$ is",
        r"$-\dfrac{3}{4}$", [r"$\dfrac{3}{4}$", r"$-\dfrac{4}{3}$", r"$\dfrac{4}{3}$"],
        r"$\tan(180^{\circ}-\theta)=-\tan\theta$, because the tangent is negative in the second quadrant.",
        r"In a right-angled triangle with hypotenuse $5$ and opposite side $3$ the adjacent side is $4$, so $\tan\theta=\dfrac{3}{4}$. Then $\tan(180^{\circ}-\theta)=-\dfrac{3}{4}$.",
        r"$-\dfrac{4}{3}$ comes from the cotangent: $\tan\theta$ is opposite over adjacent."))
    a(Q(17, ["trigonometric ratios and quadrants"], "moyenne",
        r"The exact value of $\cos150^{\circ}+\sin30^{\circ}$ is",
        r"$\dfrac{1-\sqrt{3}}{2}$", [r"$\dfrac{1+\sqrt{3}}{2}$", r"$\dfrac{\sqrt{3}-1}{2}$", r"$-\dfrac{1+\sqrt{3}}{2}$"],
        r"$150^{\circ}$ is in the second quadrant, where the cosine is negative, and its reference angle is $180^{\circ}-150^{\circ}=30^{\circ}$.",
        r"$\cos150^{\circ}=-\cos30^{\circ}=-\dfrac{\sqrt{3}}{2}$ and $\sin30^{\circ}=\dfrac{1}{2}$. So $\cos150^{\circ}+\sin30^{\circ}=\dfrac{1}{2}-\dfrac{\sqrt{3}}{2}=\dfrac{1-\sqrt{3}}{2}$.",
        r"$\dfrac{1+\sqrt{3}}{2}$ takes the cosine of $150^{\circ}$ as positive: the cosine is negative in the second quadrant."))
    a(Q(18, ["trigonometric identities and equations"], "faible",
        r"$\dfrac{1-\cos2A}{2}$ is identical to",
        r"$\sin^{2}A$", [r"$\cos^{2}A$", r"$\sin A$", r"$\tan^{2}A$"],
        r"The double angle formula $\cos2A=1-2\sin^{2}A$ can be rearranged to give $\sin^{2}A$.",
        r"$\cos2A=1-2\sin^{2}A$, so $1-\cos2A=2\sin^{2}A$ and $\dfrac{1-\cos2A}{2}=\sin^{2}A$."))
    a(Q(19, ["trigonometric identities and equations"], "moyenne",
        r"The values of $x$, for $0^{\circ}\leq x\leq360^{\circ}$, which satisfy $\tan x=1$ are",
        r"$45^{\circ}$ and $225^{\circ}$", [r"$45^{\circ}$ and $135^{\circ}$", r"$45^{\circ}$ and $315^{\circ}$", r"$135^{\circ}$ and $315^{\circ}$"],
        r"The tangent has a period of $180^{\circ}$: the solutions of $\tan x=k$ are $\alpha$ and $\alpha+180^{\circ}$.",
        r"The acute angle is $45^{\circ}$. The next solution is $45^{\circ}+180^{\circ}=225^{\circ}$.",
        r"$135^{\circ}$ and $315^{\circ}$ are the solutions of $\tan x=-1$."))
    a(Q(20, ["radian measure and sectors"], "faible",
        r"The arc of a sector of a circle of radius $8$ cm subtends an angle of $0.75$ radians at the centre. The length of the arc is",
        r"$6$ cm", [r"$3$ cm", r"$12$ cm", r"$48$ cm"],
        r"With $\theta$ in radians the length of an arc is $r\theta$.",
        r"$r\theta=8\times0.75=6$ cm.",
        r"$24\ \text{cm}^{2}$ would be the area $\dfrac{1}{2}r^{2}\theta$; $3$ is $\dfrac{1}{2}r\theta$."))
    a(Q(21, ["trigonometric graphs and maximum values"], "faible",
        r"The period of the function $y=2\sin3x$ is",
        r"$120^{\circ}$", [r"$360^{\circ}$", r"$60^{\circ}$", r"$240^{\circ}$"],
        r"The period of $y=a\sin bx$ is $\dfrac{360^{\circ}}{b}$ (or $\dfrac{2\pi}{b}$ radians).",
        r"Here $b=3$, so the period is $\dfrac{360^{\circ}}{3}=120^{\circ}$.",
        r"$2$ is the amplitude and has no effect on the period."))
    a(Q(22, ["sine and cosine rules"], "faible",
        r"In {FIG}, triangle $ABC$ has $\hat{A}=60^{\circ}$, $\hat{B}=45^{\circ}$ and $BC=9$ cm. The length of $AC$ is",
        r"$3\sqrt{6}$ cm", [r"$\dfrac{9\sqrt{6}}{2}$ cm", r"$9\sqrt{2}$ cm", r"$3\sqrt{3}$ cm"],
        r"The sine rule: $\dfrac{a}{\sin A}=\dfrac{b}{\sin B}$, where each side is opposite the angle with the same letter.",
        r"$BC=a$ is opposite $\hat{A}$ and $AC=b$ is opposite $\hat{B}$. $b=\dfrac{9\sin45^{\circ}}{\sin60^{\circ}}=\dfrac{9\times\frac{\sqrt{2}}{2}}{\frac{\sqrt{3}}{2}}=\dfrac{9\sqrt{2}}{\sqrt{3}}=3\sqrt{6}$ cm.",
        r"$\dfrac{9\sqrt{6}}{2}$ comes from inverting the ratio: $AC$ is opposite the angle $45^{\circ}$.",
        fig="triangle"))
    a(Q(23, ["sine and cosine rules"], "moyenne",
        r"The sides of a triangle are $5$ cm, $6$ cm and $7$ cm. The cosine of the angle opposite the side of $7$ cm is",
        r"$\dfrac{1}{5}$", [r"$\dfrac{5}{7}$", r"$\dfrac{19}{35}$", r"$\dfrac{2}{5}$"],
        r"The cosine rule: $\cos A=\dfrac{b^{2}+c^{2}-a^{2}}{2bc}$, where $a$ is the side opposite the angle $A$.",
        r"$\cos A=\dfrac{5^{2}+6^{2}-7^{2}}{2\times5\times6}=\dfrac{12}{60}=\dfrac{1}{5}$.",
        r"$\dfrac{5}{7}$ and $\dfrac{19}{35}$ are the cosines of the angles opposite the sides of $5$ cm and $6$ cm."))
    a(Q(24, ["coordinate geometry of straight lines"], "faible",
        r"The gradient of the line through the points $(-2,3)$ and $(4,-9)$ is",
        r"$-2$", [r"$2$", r"$-\dfrac{1}{2}$", r"$\dfrac{1}{2}$"],
        r"The gradient through $(x_{1},y_{1})$ and $(x_{2},y_{2})$ is $\dfrac{y_{2}-y_{1}}{x_{2}-x_{1}}$.",
        r"$\dfrac{-9-3}{4-(-2)}=\dfrac{-12}{6}=-2$.",
        r"$-\dfrac{1}{2}$ is the gradient of a perpendicular line, or of the line with the coordinates inverted."))
    a(Q(25, ["coordinate geometry of straight lines"], "moyenne",
        r"The line $M$ in {FIG} cuts the $x$-axis at $(4,0)$ and the $y$-axis at $(0,-3)$. The equation of $M$ is",
        r"$3x-4y=12$", [r"$4x-3y=12$", r"$3x+4y=12$", r"$3x-4y=-12$"],
        r"The gradient is the change in $y$ divided by the change in $x$; the line cuts the $y$-axis at its intercept $c$ in $y=mx+c$.",
        r"The gradient is $\dfrac{0-(-3)}{4-0}=\dfrac{3}{4}$ and the $y$-intercept is $-3$, so $y=\dfrac{3}{4}x-3$. Multiplying by $4$: $4y=3x-12$, that is $3x-4y=12$. Check with $(4,0)$: $12-0=12$.",
        r"The line goes up to the right, so its gradient is positive: $3x+4y=12$ has a negative gradient.",
        fig="droite"))
    return qs
