r"""Questions 1 a 25 de l'epreuve inedite GCE O Level Additional Mathematics Paper 1 n.1 (voir generer_addmaths_p1.py).

Chaines BRUTES (r"..."): une commande LaTeX a backslash simple dans une chaine ordinaire devient un caractere de controle.
Ordre du syllabus 0575 comme les sept vrais Paper 1 2019-2026 : indices, logarithmes, polynomes, suites, denombrement,
trigonometrie, geometrie analytique.
"""


def Q(n, themes, diff, stem, ok, bad, rappel, sol, piege=None, conseil=None, fig=None):
    return dict(n=n, themes=themes, diff=diff, stem=stem, ok=ok, bad=bad, rappel=rappel, sol=sol,
                piege=piege, conseil=conseil, fig=fig)


def questions():
    qs = []
    a = qs.append

    a(Q(1, ["indices and surds"], "faible",
        r"The value of $\left(\dfrac{2}{5}\right)^{-2}$ is",
        r"$\dfrac{25}{4}$", [r"$\dfrac{4}{25}$", r"$-\dfrac{4}{25}$", r"$\dfrac{5}{2}$"],
        r"A negative index means the reciprocal: $\left(\dfrac{a}{b}\right)^{-n}=\left(\dfrac{b}{a}\right)^{n}$.",
        r"$\left(\dfrac{2}{5}\right)^{-2}=\left(\dfrac{5}{2}\right)^{2}=\dfrac{25}{4}$.",
        r"$\dfrac{4}{25}$ squares the fraction but forgets to turn it upside down; $\dfrac{5}{2}$ turns it upside down but forgets the square."))

    a(Q(2, ["indices and surds"], "moyenne",
        r"Rationalising the denominator, $\dfrac{6}{\sqrt{3}+1}$ is equal to",
        r"$3\sqrt{3}-3$", [r"$3\sqrt{3}+3$", r"$6\sqrt{3}-6$", r"$\sqrt{3}-1$"],
        r"To rationalise a denominator of the form $\sqrt{a}+b$, multiply the top and the bottom by the conjugate $\sqrt{a}-b$, so that the bottom becomes a rational number.",
        r"$\dfrac{6}{\sqrt{3}+1}\times\dfrac{\sqrt{3}-1}{\sqrt{3}-1}=\dfrac{6(\sqrt{3}-1)}{3-1}=\dfrac{6(\sqrt{3}-1)}{2}=3\sqrt{3}-3$.",
        r"The denominator $(\sqrt{3}+1)(\sqrt{3}-1)=3-1=2$, not $1$: forgetting to divide by $2$ gives $6\sqrt{3}-6$."))

    a(Q(3, ["logarithms and exponential equations"], "faible",
        r"The value of $\log_{10}20+\log_{10}5$ is",
        r"$2$", [r"$25$", r"$1$", r"$4$"],
        r"The sum of two logarithms of the same base is the logarithm of the product: $\log a+\log b=\log(ab)$.",
        r"$\log_{10}20+\log_{10}5=\log_{10}(20\times5)=\log_{10}100=2$, because $10^{2}=100$.",
        r"$\log a+\log b$ is not $\log(a+b)$: $\log_{10}25$ is not the answer."))

    a(Q(4, ["relations between roots and coefficients"], "moyenne",
        r"The roots of the equation $2x^{2}-5x-8=0$ are $\alpha$ and $\beta$. The value of $\alpha+\beta+\alpha\beta$ is",
        r"$-\dfrac{3}{2}$", [r"$\dfrac{3}{2}$", r"$-\dfrac{13}{2}$", r"$\dfrac{13}{2}$"],
        r"For $ax^{2}+bx+c=0$ with roots $\alpha$ and $\beta$: $\alpha+\beta=-\dfrac{b}{a}$ and $\alpha\beta=\dfrac{c}{a}$.",
        r"Here $a=2$, $b=-5$, $c=-8$. $\alpha+\beta=-\dfrac{-5}{2}=\dfrac{5}{2}$ and $\alpha\beta=\dfrac{-8}{2}=-4$. So $\alpha+\beta+\alpha\beta=\dfrac{5}{2}-4=-\dfrac{3}{2}$.",
        r"The sum of the roots is $-\dfrac{b}{a}$: the sign of $b$ changes. Using $\alpha+\beta=-\dfrac{5}{2}$ gives $-\dfrac{13}{2}$."))

    a(Q(5, ["quadratic functions and discriminant"], "moyenne",
        r"The equation $x^{2}+kx+9=0$ has no real roots when",
        r"$-6<k<6$", [r"$k<-6$ or $k>6$", r"$-3<k<3$", r"$k<6$"],
        r"A quadratic equation $ax^{2}+bx+c=0$ has no real roots when its discriminant is negative: $b^{2}-4ac<0$.",
        r"$b^{2}-4ac=k^{2}-4(1)(9)=k^{2}-36$. We need $k^{2}-36<0$, that is $(k-6)(k+6)<0$, so $-6<k<6$.",
        r"$k<-6$ or $k>6$ is the condition for two distinct real roots ($b^{2}-4ac>0$)."))

    a(Q(6, ["remainder and factor theorem"], "faible",
        r"When the polynomial $x^{3}-3x+4$ is divided by $(x+2)$, the remainder is",
        r"$2$", [r"$6$", r"$-6$", r"$10$"],
        r"When a polynomial $f(x)$ is divided by $(x-a)$, the remainder is $f(a)$. For $(x+2)$ take $a=-2$.",
        r"$f(-2)=(-2)^{3}-3(-2)+4=-8+6+4=2$.",
        r"$f(2)=8-6+4=6$ is the remainder on division by $(x-2)$, not by $(x+2)$."))

    a(Q(7, ["remainder and factor theorem"], "moyenne",
        r"Given that $(x-3)$ is a factor of $x^{3}-px^{2}+x-3$, the value of $p$ is",
        r"$3$", [r"$-3$", r"$9$", r"$\dfrac{1}{3}$"],
        r"If $(x-a)$ is a factor of $f(x)$, then $f(a)=0$.",
        r"$f(3)=27-9p+3-3=27-9p=0$, so $p=3$.",
        r"The term $-px^{2}$ gives $-p\times9$: the minus sign belongs to $p$, so $27-9p=0$ and not $27+9p=0$."))

    a(Q(8, ["arithmetic and geometric progressions"], "faible",
        r"The first term of an arithmetic progression is $7$ and the common difference is $-3$. The $5^{\text{th}}$ term is",
        r"$-5$", [r"$5$", r"$-8$", r"$-12$"],
        r"The $n^{\text{th}}$ term of an arithmetic progression is $T_n=a+(n-1)d$.",
        r"$T_{5}=7+(5-1)(-3)=7-12=-5$.",
        r"$-8$ comes from $7+5(-3)$: the number of steps from the first term to the fifth term is $4$, not $5$."))

    a(Q(9, ["arithmetic and geometric progressions"], "faible",
        r"The sum of the first $12$ terms of an arithmetic progression with first term $3$ and common difference $4$ is",
        r"$300$", [r"$600$", r"$150$", r"$276$"],
        r"The sum of the first $n$ terms of an arithmetic progression is $S_n=\dfrac{n}{2}\left[2a+(n-1)d\right]$.",
        r"$S_{12}=\dfrac{12}{2}\left[2(3)+(12-1)(4)\right]=6\left[6+44\right]=6\times50=300$.",
        r"$600$ forgets the factor $\dfrac{n}{2}$ (it uses $n$); $276$ uses $(n-2)d$ instead of $(n-1)d$."))

    a(Q(10, ["arithmetic and geometric progressions"], "moyenne",
        r"The second term of a geometric progression is $6$ and the fifth term is $162$. The common ratio is",
        r"$3$", [r"$4$", r"$9$", r"$27$"],
        r"In a geometric progression with ratio $r$, going from one term to the term $k$ places later multiplies by $r^{k}$.",
        r"From the second term to the fifth term there are $3$ steps, so $6r^{3}=162$, $r^{3}=27$ and $r=3$.",
        r"$27$ is $r^{3}$, not $r$: take the cube root."))

    a(Q(11, ["arithmetic and geometric progressions"], "moyenne",
        r"The sum to infinity of a geometric progression with first term $8$ and common ratio $\dfrac{1}{4}$ is",
        r"$\dfrac{32}{3}$", [r"$32$", r"$6$", r"$\dfrac{8}{3}$"],
        r"A geometric progression with $|r|<1$ has a sum to infinity $S_{\infty}=\dfrac{a}{1-r}$.",
        r"$S_{\infty}=\dfrac{8}{1-\frac{1}{4}}=\dfrac{8}{\frac{3}{4}}=8\times\dfrac{4}{3}=\dfrac{32}{3}$.",
        r"$32=\dfrac{8}{r}$ divides by $r$ instead of $1-r$."))

    a(Q(12, ["binomial expansion (additional maths)"], "faible",
        r"The coefficient of $x^{2}$ in the expansion of $(2+x)^{5}$ is",
        r"$80$", [r"$40$", r"$10$", r"$160$"],
        r"The term in $x^{r}$ in $(a+x)^{n}$ is $\dbinom{n}{r}a^{n-r}x^{r}$.",
        r"For $x^{2}$: $\dbinom{5}{2}\,2^{3}x^{2}=10\times8\,x^{2}=80x^{2}$.",
        r"The power of the number $2$ is $n-r=3$, not $r=2$: $10\times2^{2}=40$ is a common slip."))

    a(Q(13, ["binomial expansion (additional maths)"], "moyenne",
        r"The first three terms in the expansion of $(1-2x)^{4}$ in ascending powers of $x$ are",
        r"$1-8x+24x^{2}$", [r"$1+8x+24x^{2}$", r"$1-8x+6x^{2}$", r"$1-2x+4x^{2}$"],
        r"$(1+y)^{n}=1+ny+\dfrac{n(n-1)}{2}y^{2}+\ldots$ with $y=-2x$: the whole of $-2x$ is raised to each power.",
        r"With $y=-2x$ and $n=4$: $1+4(-2x)+\dfrac{4\times3}{2}(-2x)^{2}=1-8x+6\times4x^{2}=1-8x+24x^{2}$.",
        r"$(-2x)^{2}=4x^{2}$: forgetting to square the $2$ gives $6x^{2}$."))

    a(Q(14, ["permutations and combinations (additional maths)"], "moyenne",
        r"The number of different arrangements of the letters of the word LEVEL is",
        r"$30$", [r"$120$", r"$60$", r"$10$"],
        r"The number of arrangements of $n$ letters in which one letter is repeated $p$ times and another $q$ times is $\dfrac{n!}{p!\,q!}$.",
        r"LEVEL has $5$ letters, with L twice and E twice. The number of arrangements is $\dfrac{5!}{2!\,2!}=\dfrac{120}{4}=30$.",
        r"$120=5!$ treats the repeated letters as different; $60=\dfrac{5!}{2!}$ only corrects one of the two repeated letters."))

    a(Q(15, ["permutations and combinations (additional maths)"], "faible",
        r"In how many ways can a committee of $3$ people be chosen from $8$ people?",
        r"$56$", [r"$336$", r"$24$", r"$112$"],
        r"The order does not matter in a committee, so the number of ways is the combination $\dbinom{n}{r}=\dfrac{n!}{r!\,(n-r)!}$.",
        r"$\dbinom{8}{3}=\dfrac{8\times7\times6}{3\times2\times1}=\dfrac{336}{6}=56$.",
        r"$336=8\times7\times6$ counts the committees in order (a permutation): each committee is counted $3!=6$ times."))

    a(Q(16, ["trigonometric ratios and quadrants"], "faible",
        r"If $\sin\theta<0$ and $\cos\theta>0$, then $\theta$ lies in the",
        r"fourth quadrant", [r"first quadrant", r"second quadrant", r"third quadrant"],
        r"By the CAST rule, $\sin$ is positive in the first and second quadrants and $\cos$ is positive in the first and fourth quadrants.",
        r"$\sin\theta<0$ means the third or the fourth quadrant. $\cos\theta>0$ means the first or the fourth quadrant. Both are true only in the fourth quadrant."))

    a(Q(17, ["trigonometric ratios and quadrants"], "faible",
        r"Without a calculator, $\cos150^{\circ}$ is equal to",
        r"$-\dfrac{\sqrt{3}}{2}$", [r"$\dfrac{\sqrt{3}}{2}$", r"$-\dfrac{1}{2}$", r"$\dfrac{1}{2}$"],
        r"Use the acute reference angle and the sign of the ratio in the quadrant: $\cos(180^{\circ}-\theta)=-\cos\theta$.",
        r"$150^{\circ}$ is in the second quadrant, where $\cos$ is negative. The reference angle is $30^{\circ}$, so $\cos150^{\circ}=-\cos30^{\circ}=-\dfrac{\sqrt{3}}{2}$.",
        r"$-\dfrac{1}{2}$ is $-\sin30^{\circ}$ or $\cos120^{\circ}$: the reference angle of $150^{\circ}$ is $30^{\circ}$, and $\cos30^{\circ}=\dfrac{\sqrt{3}}{2}$."))

    a(Q(18, ["trigonometric identities and equations"], "faible",
        r"$\dfrac{\sin2A}{2\sin A}$ is identical to",
        r"$\cos A$", [r"$\sin A$", r"$2\cos A$", r"$\tan A$"],
        r"The double angle formula is $\sin2A=2\sin A\cos A$.",
        r"$\dfrac{\sin2A}{2\sin A}=\dfrac{2\sin A\cos A}{2\sin A}=\cos A$."))

    a(Q(19, ["trigonometric identities and equations"], "moyenne",
        r"The values of $x$, for $0^{\circ}\leq x\leq360^{\circ}$, which satisfy $2\sin x=1$ are",
        r"$30^{\circ}$ and $150^{\circ}$", [r"$30^{\circ}$ and $330^{\circ}$", r"$60^{\circ}$ and $120^{\circ}$", r"$30^{\circ}$ and $210^{\circ}$"],
        r"Isolate $\sin x$, find the acute angle, then use the symmetry of the sine curve: $\sin x>0$ in the first and second quadrants, with solutions $\alpha$ and $180^{\circ}-\alpha$.",
        r"$\sin x=\dfrac{1}{2}$, so the acute angle is $30^{\circ}$. The second solution is $180^{\circ}-30^{\circ}=150^{\circ}$.",
        r"$330^{\circ}$ and $210^{\circ}$ have a negative sine: they are solutions of $\sin x=-\dfrac{1}{2}$."))

    a(Q(20, ["radian measure and sectors"], "faible",
        r"A sector of a circle of radius $6$ cm subtends an angle of $1.5$ radians at the centre. The area of the sector is",
        r"$27\ \text{cm}^{2}$", [r"$54\ \text{cm}^{2}$", r"$9\ \text{cm}^{2}$", r"$13.5\ \text{cm}^{2}$"],
        r"With $\theta$ in radians, the area of a sector is $\dfrac{1}{2}r^{2}\theta$ and the arc length is $r\theta$.",
        r"$\text{area}=\dfrac{1}{2}\times6^{2}\times1.5=\dfrac{1}{2}\times36\times1.5=27\ \text{cm}^{2}$.",
        r"$9\ \text{cm}$ is the arc length $r\theta$, and $54=r^{2}\theta$ forgets the factor $\dfrac{1}{2}$."))

    a(Q(21, ["trigonometric graphs and maximum values"], "moyenne",
        r"The least value taken by the expression $4-3\cos x$ is",
        r"$1$", [r"$7$", r"$-1$", r"$4$"],
        r"$\cos x$ takes every value from $-1$ to $1$. The minimum of $y$ occurs when the term $-3\cos x$ is as small as possible, that is when $\cos x$ is at its maximum.",
        r"The smallest value of $4-3\cos x$ is obtained when $\cos x=1$: $4-3(1)=1$. (The maximum, $4-3(-1)=7$, occurs when $\cos x=-1$.)",
        r"$7$ is the maximum value, reached when $\cos x=-1$."))

    a(Q(22, ["sine and cosine rules"], "moyenne",
        r"In {FIG}, triangle $ABC$ has $\hat{A}=30^{\circ}$, $\hat{B}=45^{\circ}$ and $BC=10$ cm. The length of $AC$ is",
        r"$10\sqrt{2}$ cm", [r"$5\sqrt{2}$ cm", r"$20$ cm", r"$10\sqrt{3}$ cm"],
        r"The sine rule: $\dfrac{a}{\sin A}=\dfrac{b}{\sin B}=\dfrac{c}{\sin C}$, where each side is opposite the angle with the same letter.",
        r"$BC=a$ is opposite $\hat{A}$ and $AC=b$ is opposite $\hat{B}$. So $\dfrac{b}{\sin45^{\circ}}=\dfrac{10}{\sin30^{\circ}}$, and $b=\dfrac{10\sin45^{\circ}}{\sin30^{\circ}}=\dfrac{10\times\frac{\sqrt{2}}{2}}{\frac{1}{2}}=10\sqrt{2}$ cm.",
        r"$5\sqrt{2}$ comes from inverting the ratio ($\dfrac{10\sin30^{\circ}}{\sin45^{\circ}}$): the side to find is opposite the angle $45^{\circ}$.",
        fig="triangle"))

    a(Q(23, ["sine and cosine rules"], "moyenne",
        r"In triangle $ABC$, $AB=8$ cm, $AC=9$ cm and $BC=7$ cm. The value of $\cos B\hat{A}C$ is",
        r"$\dfrac{2}{3}$", [r"$\dfrac{2}{7}$", r"$\dfrac{3}{4}$", r"$\dfrac{1}{3}$"],
        r"The cosine rule: $a^{2}=b^{2}+c^{2}-2bc\cos A$, so $\cos A=\dfrac{b^{2}+c^{2}-a^{2}}{2bc}$, where $a$ is the side opposite angle $A$.",
        r"The side opposite $\hat{A}$ is $BC=7$. $\cos B\hat{A}C=\dfrac{8^{2}+9^{2}-7^{2}}{2\times8\times9}=\dfrac{96}{144}=\dfrac{2}{3}$.",
        r"$\dfrac{2}{7}=\dfrac{8^{2}+7^{2}-9^{2}}{2\times8\times7}$ is the cosine of the angle at $B$, opposite $AC$."))

    a(Q(24, ["coordinate geometry of straight lines"], "faible",
        r"The coordinates of the midpoint of the line joining $P(-3,5)$ and $Q(7,-1)$ are",
        r"$(2,2)$", [r"$(4,4)$", r"$(5,2)$", r"$(2,3)$"],
        r"The midpoint of $(x_{1},y_{1})$ and $(x_{2},y_{2})$ is $\left(\dfrac{x_{1}+x_{2}}{2},\dfrac{y_{1}+y_{2}}{2}\right)$.",
        r"$\left(\dfrac{-3+7}{2},\dfrac{5+(-1)}{2}\right)=(2,2)$.",
        r"$(4,4)$ forgets to divide by $2$."))

    a(Q(25, ["coordinate geometry of straight lines"], "moyenne",
        r"The line $L$ in {FIG} cuts the $y$-axis at $(0,4)$ and the $x$-axis at $(6,0)$. The equation of $L$ is",
        r"$2x+3y=12$", [r"$3x+2y=12$", r"$2x-3y=12$", r"$2x+3y=6$"],
        r"A line with intercepts $(a,0)$ and $(0,b)$ has the equation $\dfrac{x}{a}+\dfrac{y}{b}=1$. Another way is to find the gradient and use $y=mx+c$.",
        r"The gradient is $\dfrac{0-4}{6-0}=-\dfrac{2}{3}$ and the $y$-intercept is $4$, so $y=-\dfrac{2}{3}x+4$. Multiplying by $3$: $3y=-2x+12$, that is $2x+3y=12$. Check with $(6,0)$: $12+0=12$.",
        r"A line that goes down to the right has a negative gradient; $2x-3y=12$ has a positive gradient $\dfrac{2}{3}$.",
        fig="droite"))
    return qs
