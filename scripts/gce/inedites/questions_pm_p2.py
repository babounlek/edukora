r"""Les 10 exercices de l'epreuve inedite GCE A Level Pure Mathematics Paper 2 n.1 (100 marks, 3 h, tout obligatoire).

Le meme contenu sert les DEUX matieres « Pure Mathematics with Mechanics » et « Pure Mathematics with Statistics » (les vrais Paper 2 des deux
options sont identiques ; une epreuve n'a qu'une matiere, donc generer_pm_p2.py ecrit deux epreuves a partir de ces questions).

Structure mesuree sur les Paper 2 de 2024 et 2026 (10 exercices, de 1 a 5 sous-questions, notions : polynomes, racines, fractions partielles,
trigonometrie, progressions, complexes, equations differentielles, forme lineaire, fonction rationnelle, integration) ; aucune donnee reprise d'un
sujet reel ni de l'epreuve Further Mathematics. Chaque sous-question : bareme exact (`pts`), grille `crit` (somme = pts), rappel, resolution,
reponse finale `ans` (recalculee par verifier_reponses_pm_p2.py). Chaines BRUTES. Numeros affiches : lettres a, b, c... (unique par exercice).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_addmaths_p2_a import E, S  # noqa: E402,F401

G = ""  # pas de groupes : paper plat


def exercices():
    ex = []

    # ---- Exercice 1 : polynomials (10) ----
    ex.append(E("1", G, 10, "", [
        S("a", r"The polynomial $f(x)=x^{3}+ax^{2}+bx+6$, where $a$ and $b$ are constants, has $(x-1)$ as a factor and leaves a remainder of $-4$ when divided by $(x-2)$. Find the values of $a$ and $b$.",
          ["polynomial division and factor theorem"], "faible", 4,
          [(r"You use the factor theorem: $f(1)=0$ gives $a+b=-7$", 1), (r"You use the remainder theorem: $f(2)=-4$ gives $2a+b=-9$", 1),
           (r"You solve the two equations to obtain $a=-2$", 1), (r"You obtain $b=-5$", 1)],
          r"The factor theorem says that $(x-c)$ is a factor of $f(x)$ exactly when $f(c)=0$, and the remainder theorem says that dividing $f(x)$ by $(x-c)$ leaves the remainder $f(c)$; each condition therefore gives one linear equation in the unknown coefficients.",
          r"$f(1)=1+a+b+6=0$, so $a+b=-7$. $f(2)=8+4a+2b+6=-4$, so $4a+2b=-18$, that is $2a+b=-9$. Subtracting the first equation from the second gives $a=-2$, and then $b=-5$. Check: $f(x)=x^{3}-2x^{2}-5x+6$ gives $f(1)=0$ and $f(2)=8-8-10+6=-4$.",
          ans=r"$a=-2$ and $b=-5$"),
        S("b", r"Using these values of $a$ and $b$, factorise $f(x)$ completely and hence solve the equation $f(x)=0$.",
          ["polynomial division and factor theorem"], "faible", 2,
          [(r"You divide $f(x)$ by $(x-1)$ to obtain the quotient $x^{2}-x-6$", 1), (r"You factorise $f(x)=(x-1)(x-3)(x+2)$ and state the roots $1$, $3$ and $-2$", 1)],
          r"Once one linear factor is known, divide the polynomial by it (long division or comparison of coefficients) to obtain a quadratic quotient, then factorise the quotient.",
          r"Dividing $x^{3}-2x^{2}-5x+6$ by $(x-1)$ gives $x^{2}-x-6$, since $(x-1)(x^{2}-x-6)=x^{3}-x^{2}-6x-x^{2}+x+6=x^{3}-2x^{2}-5x+6$. Then $x^{2}-x-6=(x-3)(x+2)$, so $f(x)=(x-1)(x-3)(x+2)$ and $f(x)=0$ when $x=1$, $x=3$ or $x=-2$.",
          ans=r"$f(x)=(x-1)(x-3)(x+2)$ ; $x=1$, $x=3$ or $x=-2$"),
        S("c", r"Find the set of values of the constant $k$ for which the equation $x^{2}+kx+(k+3)=0$ has no real roots.",
          ["quadratic equations and discriminant"], "moyenne", 4,
          [(r"You write the discriminant $\Delta=k^{2}-4(k+3)$", 1), (r"You state that no real roots means $k^{2}-4k-12<0$", 1),
           (r"You factorise $(k-6)(k+2)<0$", 1), (r"You conclude $-2<k<6$", 1)],
          r"A quadratic $ax^{2}+bx+c=0$ has no real roots when its discriminant $b^{2}-4ac$ is negative; this gives a quadratic inequality in $k$, solved by finding the critical values and checking the sign between them.",
          r"The discriminant is $\Delta=k^{2}-4(k+3)=k^{2}-4k-12=(k-6)(k+2)$. There are no real roots when $\Delta<0$, that is $(k-6)(k+2)<0$. The product of the two factors is negative between the critical values, so $-2<k<6$. Check with $k=0$: $x^{2}+3=0$ has no real root.",
          ans=r"$-2<k<6$",
          piege=r"The set is the interval between the critical values. The statement $k<-2$ or $k>6$ describes the opposite case, two distinct real roots."),
    ]))

    # ---- Exercice 2 : roots of equations (10) ----
    ex.append(E("2", G, 10, "", [
        S("a", r"The roots of the equation $2x^{2}-9x+3=0$ are $\alpha$ and $\beta$. Write down the values of $\alpha+\beta$ and $\alpha\beta$, and find the value of $\alpha^{2}+\beta^{2}$.",
          ["sum and product of roots"], "faible", 3,
          [(r"You state $\alpha+\beta=\tfrac92$ and $\alpha\beta=\tfrac32$", 1), (r"You use $\alpha^{2}+\beta^{2}=(\alpha+\beta)^{2}-2\alpha\beta$", 1), (r"You obtain $\tfrac{69}{4}$", 1)],
          r"For $ax^{2}+bx+c=0$ the sum of the roots is $-\dfrac ba$ and the product is $\dfrac ca$; a symmetric expression such as $\alpha^{2}+\beta^{2}$ is rewritten with $(\alpha+\beta)^{2}$ and $\alpha\beta$, so the roots themselves are never needed.",
          r"$\alpha+\beta=-\dfrac{-9}{2}=\tfrac92$ and $\alpha\beta=\tfrac32$. Then $\alpha^{2}+\beta^{2}=(\alpha+\beta)^{2}-2\alpha\beta=\tfrac{81}{4}-3=\tfrac{69}{4}$.",
          ans=r"$\alpha+\beta=\tfrac92$, $\alpha\beta=\tfrac32$, $\alpha^{2}+\beta^{2}=\tfrac{69}{4}$"),
        S("b", r"Find the quadratic equation, with integer coefficients, whose roots are $\dfrac{\alpha}{\beta}$ and $\dfrac{\beta}{\alpha}$.",
          ["sum and product of roots", "quadratic equations and discriminant"], "moyenne", 3,
          [(r"You write the sum of the new roots $\dfrac{\alpha^{2}+\beta^{2}}{\alpha\beta}=\tfrac{23}{2}$", 1), (r"You write the product of the new roots $=1$", 1),
           (r"You form $x^{2}-\tfrac{23}{2}x+1=0$ and clear the fraction: $2x^{2}-23x+2=0$", 1)],
          r"To build an equation from new roots, compute their sum $S$ and product $P$ in terms of $\alpha+\beta$ and $\alpha\beta$, write $x^{2}-Sx+P=0$, then multiply by the common denominator to obtain integer coefficients.",
          r"Sum: $\dfrac{\alpha}{\beta}+\dfrac{\beta}{\alpha}=\dfrac{\alpha^{2}+\beta^{2}}{\alpha\beta}=\dfrac{69/4}{3/2}=\tfrac{23}{2}$. Product: $\dfrac{\alpha}{\beta}\times\dfrac{\beta}{\alpha}=1$. The equation is $x^{2}-\tfrac{23}{2}x+1=0$; multiplying by $2$ gives $2x^{2}-23x+2=0$.",
          ans=r"$2x^{2}-23x+2=0$"),
        S("c", r"The cubic equation $x^{3}-14x^{2}+px-64=0$, where $p$ is a constant, has three real roots which are in geometric progression. Show that one of the roots is $4$, and find the value of $p$ and the other two roots.",
          ["polynomial equations", "geometric progressions"], "moyenne", 4,
          [(r"You write the roots as $\dfrac ar$, $a$ and $ar$ and use the product of the roots: $a^{3}=64$", 1), (r"You obtain $a=4$, so $4$ is a root", 1),
           (r"You use the sum of the roots: $4\left(\dfrac1r+1+r\right)=14$, so $2r^{2}-5r+2=0$ and $r=2$ or $r=\tfrac12$", 1),
           (r"You find the roots $2$, $4$, $8$ and $p=2\times4+2\times8+4\times8=56$", 1)],
          r"For a cubic $x^{3}+ux^{2}+vx+w=0$ with roots $r_{1},r_{2},r_{3}$ the sum of the roots is $-u$, the sum of the products in pairs is $v$ and the product of the three roots is $-w$; roots in geometric progression are written $\dfrac ar$, $a$ and $ar$ so that their product depends on $a$ alone.",
          r"Let the roots be $\dfrac ar$, $a$, $ar$. Their product is $a^{3}=64$, so $a=4$: one root is $4$. Their sum is $4\left(\dfrac1r+1+r\right)=14$, so $r+\dfrac1r=\tfrac52$, that is $2r^{2}-5r+2=0$, $(2r-1)(r-2)=0$ and $r=2$ or $r=\tfrac12$. Either value gives the roots $2$, $4$ and $8$. The sum of the products in pairs is $p=2\times4+2\times8+4\times8=8+16+32=56$.",
          ans=r"one root is $4$ ; $p=56$ ; the other roots are $2$ and $8$"),
    ]))

    # ---- Exercice 3 : partial fractions and integration (10) ----
    ex.append(E("3", G, 10, r"The function $f$ is defined by $f(x)=\dfrac{x^{2}+10x+7}{(x-1)(x+2)^{2}}$ for $x>1$.", [
        S("a", r"Express $f(x)$ in partial fractions.",
          ["partial fractions"], "moyenne", 4,
          [(r"You write the form $\dfrac{A}{x-1}+\dfrac{B}{x+2}+\dfrac{C}{(x+2)^{2}}$", 1), (r"You use $x=1$ to find $A=2$", 1),
           (r"You use $x=-2$ to find $C=3$", 1), (r"You compare the coefficients of $x^{2}$: $A+B=1$, so $B=-1$", 1)],
          r"A repeated linear factor $(x+a)^{2}$ in the denominator needs two terms, $\dfrac{B}{x+a}$ and $\dfrac{C}{(x+a)^{2}}$; multiply by the denominator, then substitute the roots of each factor and compare coefficients for the remaining constant.",
          r"Write $\dfrac{x^{2}+10x+7}{(x-1)(x+2)^{2}}\equiv\dfrac{A}{x-1}+\dfrac{B}{x+2}+\dfrac{C}{(x+2)^{2}}$, so $x^{2}+10x+7\equiv A(x+2)^{2}+B(x-1)(x+2)+C(x-1)$. Put $x=1$: $18=9A$, so $A=2$. Put $x=-2$: $4-20+7=-9=-3C$, so $C=3$. The coefficient of $x^{2}$ gives $1=A+B$, so $B=-1$. Hence $f(x)=\dfrac{2}{x-1}-\dfrac{1}{x+2}+\dfrac{3}{(x+2)^{2}}$.",
          ans=r"$f(x)=\dfrac{2}{x-1}-\dfrac{1}{x+2}+\dfrac{3}{(x+2)^{2}}$"),
        S("b", r"Hence show that $\displaystyle\int_{2}^{4}f(x)\,dx=\ln6+\dfrac14$.",
          ["integration of rational functions", "partial fractions"], "moyenne", 4,
          [(r"You integrate the first two terms: $2\ln(x-1)-\ln(x+2)$", 1), (r"You integrate the third term: $-\dfrac{3}{x+2}$", 1),
           (r"You substitute the limits $4$ and $2$", 1), (r"You combine the logarithms: $\ln\dfrac{9\times4}{6}=\ln6$, and the constants give $\tfrac14$", 1)],
          r"Integrate each partial fraction separately: $\dfrac{1}{x+a}$ gives $\ln|x+a|$ and $\dfrac{1}{(x+a)^{2}}$ gives $-\dfrac{1}{x+a}$; combine the logarithms with $\ln p-\ln q=\ln\dfrac pq$ after substituting the limits.",
          r"$\displaystyle\int_{2}^{4}f(x)\,dx=\left[2\ln(x-1)-\ln(x+2)-\dfrac{3}{x+2}\right]_{2}^{4}$. At $x=4$: $2\ln3-\ln6-\tfrac12$. At $x=2$: $0-\ln4-\tfrac34$. The difference is $2\ln3-\ln6+\ln4-\tfrac12+\tfrac34=\ln\dfrac{9\times4}{6}+\tfrac14=\ln6+\tfrac14$.",
          piege=r"The integral of $\dfrac{3}{(x+2)^{2}}$ is $-\dfrac{3}{x+2}$, not a logarithm: only the terms with a single power of $(x+2)$ give logarithms."),
        S("c", r"Show that $\displaystyle\int_{0}^{1}\dfrac{4x+2}{x^{2}+x+1}\,dx=2\ln3$.",
          ["integration of rational functions"], "faible", 2,
          [(r"You write $4x+2=2(2x+1)$, twice the derivative of the denominator", 1), (r"You integrate to $2\ln(x^{2}+x+1)$ and evaluate between $0$ and $1$ to obtain $2\ln3$", 1)],
          r"When the numerator of a fraction is a constant multiple of the derivative of its denominator, the integral is that multiple of the natural logarithm of the denominator.",
          r"The derivative of $x^{2}+x+1$ is $2x+1$ and $4x+2=2(2x+1)$. So $\displaystyle\int_{0}^{1}\dfrac{4x+2}{x^{2}+x+1}\,dx=\Big[2\ln(x^{2}+x+1)\Big]_{0}^{1}=2\ln3-2\ln1=2\ln3$.",
          ),
    ]))

    # ---- Exercice 4 : trigonometry (10) ----
    ex.append(E("4", G, 10, "", [
        S("a", r"Express $8\sin\theta+15\cos\theta$ in the form $R\sin(\theta+\alpha)$, where $R>0$ and $0^{\circ}<\alpha<90^{\circ}$. Give $\alpha$ to $2$ decimal places.",
          ["harmonic form"], "faible", 3,
          [(r"You expand $R\sin(\theta+\alpha)$ and equate: $R\cos\alpha=8$ and $R\sin\alpha=15$", 1), (r"You obtain $R=\sqrt{8^{2}+15^{2}}=17$", 1), (r"You obtain $\tan\alpha=\tfrac{15}{8}$, so $\alpha=61.93^{\circ}$", 1)],
          r"To write $a\sin\theta+b\cos\theta$ as $R\sin(\theta+\alpha)$, expand $R\sin(\theta+\alpha)=R\cos\alpha\sin\theta+R\sin\alpha\cos\theta$ and equate coefficients: $R=\sqrt{a^{2}+b^{2}}$ and $\tan\alpha=\dfrac ba$.",
          r"$R\sin(\theta+\alpha)=R\cos\alpha\sin\theta+R\sin\alpha\cos\theta$, so $R\cos\alpha=8$ and $R\sin\alpha=15$. Then $R^{2}=64+225=289$, $R=17$, and $\tan\alpha=\dfrac{15}{8}$, so $\alpha=61.93^{\circ}$ (both $\cos\alpha$ and $\sin\alpha$ are positive, so $\alpha$ is acute).",
          ans=r"$8\sin\theta+15\cos\theta=17\sin(\theta+61.93^{\circ})$"),
        S("b", r"Hence solve the equation $8\sin\theta+15\cos\theta=10$ for $0^{\circ}\le\theta\le360^{\circ}$, giving your answers to $1$ decimal place.",
          ["harmonic form", "trigonometric equations"], "moyenne", 3,
          [(r"You write $\sin(\theta+61.93^{\circ})=\dfrac{10}{17}$ and the range $61.93^{\circ}\le\theta+61.93^{\circ}\le421.93^{\circ}$", 1),
           (r"You find $\theta+61.93^{\circ}=143.97^{\circ}$ and $396.03^{\circ}$", 1), (r"You obtain $\theta=82.0^{\circ}$ and $\theta=334.1^{\circ}$", 1)],
          r"Replace the expression by its harmonic form, solve for the whole angle $\theta+\alpha$ using both solutions of the sine equation, and list the values of that angle that lie in the interval obtained by shifting the range of $\theta$ by $\alpha$.",
          r"The equation becomes $17\sin(\theta+61.93^{\circ})=10$, so $\sin(\theta+61.93^{\circ})=\tfrac{10}{17}$ with $61.93^{\circ}\le\theta+61.93^{\circ}\le421.93^{\circ}$. The calculator gives $36.03^{\circ}$, which is below the range; the angles in the range are $180^{\circ}-36.03^{\circ}=143.97^{\circ}$ and $360^{\circ}+36.03^{\circ}=396.03^{\circ}$. Hence $\theta=143.97^{\circ}-61.93^{\circ}=82.0^{\circ}$ and $\theta=396.03^{\circ}-61.93^{\circ}=334.1^{\circ}$.",
          ans=r"$\theta=82.0^{\circ}$ or $\theta=334.1^{\circ}$",
          piege=r"The calculator value $36.03^{\circ}$ cannot be used directly: after subtracting $\alpha$ it would give a negative $\theta$, so the angle must first be shifted into the range $61.93^{\circ}$ to $421.93^{\circ}$."),
        S("c", r"Prove the identity $\dfrac{\sin2\theta}{1+\cos2\theta}\equiv\tan\theta$, and hence solve $\dfrac{\sin2\theta}{1+\cos2\theta}=3$ for $0^{\circ}\le\theta\le180^{\circ}$.",
          ["trigonometric identities", "trigonometric equations"], "moyenne", 4,
          [(r"You use $\sin2\theta=2\sin\theta\cos\theta$ and $1+\cos2\theta=2\cos^{2}\theta$", 1), (r"You simplify the fraction to $\dfrac{\sin\theta}{\cos\theta}=\tan\theta$", 1),
           (r"You write $\tan\theta=3$", 1), (r"You obtain $\theta=71.6^{\circ}$", 1)],
          r"Rewrite double angles with $\sin2\theta=2\sin\theta\cos\theta$ and $\cos2\theta=2\cos^{2}\theta-1$ (which gives $1+\cos2\theta=2\cos^{2}\theta$); cancel common factors, then use the simpler identity to turn the equation into one in $\tan\theta$.",
          r"$\dfrac{\sin2\theta}{1+\cos2\theta}=\dfrac{2\sin\theta\cos\theta}{2\cos^{2}\theta}=\dfrac{\sin\theta}{\cos\theta}=\tan\theta$. The equation becomes $\tan\theta=3$, so $\theta=\tan^{-1}3=71.6^{\circ}$ to $1$ decimal place. The tangent has period $180^{\circ}$, so there is no other solution in the interval.",
          ans=r"$\theta=71.6^{\circ}$"),
    ]))

    # ---- Exercice 5 : progressions and binomial expansion (10) ----
    ex.append(E("5", G, 10, "", [
        S("a", r"An athlete in Buea trains for a mountain race. On the first day she runs $2.4$ km and on each following day she runs $0.3$ km more than on the day before. Find (i) the first day on which she runs more than $6$ km, (ii) the total distance she has run in the first $14$ days.",
          ["arithmetic progressions"], "faible", 3,
          [(r"You write the distance on day $n$: $2.4+0.3(n-1)$", 1), (r"You solve $2.4+0.3(n-1)>6$ to obtain $n>13$, so day $14$", 1), (r"You use $S_{14}=\tfrac{14}{2}(2\times2.4+13\times0.3)=60.9$ km", 1)],
          r"The daily distances form an arithmetic progression with first term $a$ and common difference $d$: the $n$th term is $a+(n-1)d$ and the sum of the first $n$ terms is $\tfrac n2\left(2a+(n-1)d\right)$.",
          r"The distance on day $n$ is $u_{n}=2.4+0.3(n-1)$. (i) $u_{n}>6$ gives $0.3(n-1)>3.6$, so $n-1>12$ and $n>13$: the first such day is day $14$ (on day $13$ she runs exactly $6$ km). (ii) $S_{14}=\tfrac{14}{2}\left(2\times2.4+13\times0.3\right)=7\times8.7=60.9$ km.",
          ans=r"day $14$ ; $60.9$ km",
          piege=r"On day $13$ the distance is exactly $6$ km, not more than $6$ km: the strict inequality gives $n=14$."),
        S("b", r"A geometric progression has first term $24$ and sum to infinity $72$. Find the common ratio, and the sum of the first $6$ terms as an exact fraction.",
          ["geometric progressions"], "faible", 3,
          [(r"You write $\dfrac{24}{1-r}=72$", 1), (r"You obtain $r=\tfrac23$", 1), (r"You calculate $S_{6}=24\times\dfrac{1-(2/3)^{6}}{1/3}=\dfrac{5320}{81}$", 1)],
          r"The sum to infinity of a geometric progression with $|r|<1$ is $\dfrac{a}{1-r}$, and the sum of the first $n$ terms is $\dfrac{a(1-r^{n})}{1-r}$.",
          r"$\dfrac{24}{1-r}=72$ gives $1-r=\tfrac13$, so $r=\tfrac23$. Then $S_{6}=\dfrac{24\left(1-\left(\tfrac23\right)^{6}\right)}{1-\tfrac23}=72\left(1-\tfrac{64}{729}\right)=72\times\dfrac{665}{729}=\dfrac{5320}{81}\approx65.7$.",
          ans=r"$r=\tfrac23$ ; $S_{6}=\dfrac{5320}{81}$"),
        S("c", r"Find the first three terms, in ascending powers of $x$, of the binomial expansion of $(2-3x)^{5}$. Hence find the coefficient of $x^{2}$ in the expansion of $(1+2x)(2-3x)^{5}$.",
          ["binomial expansion"], "faible", 4,
          [(r"You use the binomial coefficients $\binom51=5$ and $\binom52=10$", 1), (r"You obtain $32-240x+720x^{2}$", 1),
           (r"You pick the two products that give $x^{2}$: $1\times720x^{2}+2x\times(-240x)$", 1), (r"You obtain the coefficient $240$", 1)],
          r"Write the expansion of $(a+b)^{n}$ as $\sum\binom nk a^{n-k}b^{k}$ with $b=-3x$; for a product of two expansions, collect every pair of terms whose powers of $x$ add up to the required power.",
          r"$(2-3x)^{5}=2^{5}+\binom51 2^{4}(-3x)+\binom52 2^{3}(-3x)^{2}+\dots=32-240x+720x^{2}+\dots$. In $(1+2x)(2-3x)^{5}$ the terms in $x^{2}$ come from $1\times720x^{2}$ and from $2x\times(-240x)=-480x^{2}$. The coefficient is $720-480=240$.",
          ans=r"$32-240x+720x^{2}$ ; coefficient of $x^{2}$ is $240$"),
    ]))

    # ---- Exercice 6 : complex numbers (10) ----
    ex.append(E("6", G, 10, "", [
        S("a", r"Express $w=\dfrac{5+5i}{2-i}$ in the form $a+ib$, where $a$ and $b$ are real.",
          ["complex numbers"], "faible", 3,
          [(r"You multiply numerator and denominator by the conjugate $2+i$", 1), (r"You expand the numerator: $(5+5i)(2+i)=5+15i$", 1), (r"You obtain the denominator $5$, so $w=1+3i$", 1)],
          r"To write a quotient of complex numbers in the form $a+ib$, multiply the numerator and the denominator by the conjugate of the denominator, which makes the denominator real, and use $i^{2}=-1$.",
          r"$w=\dfrac{(5+5i)(2+i)}{(2-i)(2+i)}=\dfrac{10+5i+10i+5i^{2}}{4+1}=\dfrac{5+15i}{5}=1+3i$.",
          ans=r"$w=1+3i$"),
        S("b", r"The complex number $z$ is $-1+i$. Express $z$ in modulus-argument form and use De Moivre's theorem to show that $z^{6}=8i$.",
          ["complex numbers", "de moivre theorem"], "faible", 3,
          [(r"You find $|z|=\sqrt2$", 1), (r"You find $\arg z=\tfrac{3\pi}{4}$ because $z$ lies in the second quadrant", 1),
           (r"You apply De Moivre: $z^{6}=8\left(\cos\tfrac{9\pi}{2}+i\sin\tfrac{9\pi}{2}\right)=8i$", 1)],
          r"Write $z$ as $r(\cos\theta+i\sin\theta)$ with $r=|z|$ and $\theta$ in the quadrant of $z$; De Moivre's theorem then gives $z^{n}=r^{n}(\cos n\theta+i\sin n\theta)$.",
          r"$|z|=\sqrt{1+1}=\sqrt2$. The point $(-1,1)$ is in the second quadrant with $\tan\theta=-1$, so $\theta=\tfrac{3\pi}{4}$ and $z=\sqrt2\left(\cos\tfrac{3\pi}{4}+i\sin\tfrac{3\pi}{4}\right)$. Then $z^{6}=(\sqrt2)^{6}\left(\cos\tfrac{18\pi}{4}+i\sin\tfrac{18\pi}{4}\right)=8\left(\cos\tfrac{9\pi}{2}+i\sin\tfrac{9\pi}{2}\right)=8(0+i)=8i$. Check: $z^{2}=-2i$ and $(-2i)^{3}=8i$.",
          ),
        S("c", r"Find the four fourth roots of $-16$, giving each in the form $a+ib$.",
          ["de moivre theorem", "complex numbers"], "moyenne", 4,
          [(r"You write $-16=16(\cos\pi+i\sin\pi)$", 1), (r"You write the roots with modulus $16^{1/4}=2$ and arguments $\dfrac{\pi+2k\pi}{4}$", 1),
           (r"You list the arguments $\tfrac{\pi}{4}$, $\tfrac{3\pi}{4}$, $\tfrac{5\pi}{4}$, $\tfrac{7\pi}{4}$ for $k=0,1,2,3$", 1), (r"You obtain $\sqrt2+i\sqrt2$, $-\sqrt2+i\sqrt2$, $-\sqrt2-i\sqrt2$ and $\sqrt2-i\sqrt2$", 1)],
          r"Write the number in polar form $r(\cos\alpha+i\sin\alpha)$; its $n$th roots have modulus $r^{1/n}$ and arguments $\dfrac{\alpha+2k\pi}{n}$ for $k=0,1,\dots,n-1$, equally spaced on a circle.",
          r"$-16=16(\cos\pi+i\sin\pi)$. The fourth roots have modulus $16^{1/4}=2$ and arguments $\dfrac{\pi+2k\pi}{4}$, that is $\tfrac{\pi}{4},\tfrac{3\pi}{4},\tfrac{5\pi}{4},\tfrac{7\pi}{4}$. Since $\cos\tfrac{\pi}{4}=\sin\tfrac{\pi}{4}=\tfrac{\sqrt2}{2}$, the roots are $2\left(\pm\tfrac{\sqrt2}{2}\pm i\tfrac{\sqrt2}{2}\right)=\pm\sqrt2\pm i\sqrt2$.",
          ans=r"$\sqrt2+i\sqrt2$, $-\sqrt2+i\sqrt2$, $-\sqrt2-i\sqrt2$, $\sqrt2-i\sqrt2$"),
    ]))

    # ---- Exercice 7 : differential equations (10) ----
    ex.append(E("7", G, 10, "", [
        S("a", r"Given that $y>0$, find the solution of the differential equation $(x^{2}+1)\,y\dfrac{dy}{dx}=4x$ for which $y=2$ when $x=0$. Give $y$ in terms of $x$.",
          ["first order differential equations", "separation of variables"], "moyenne", 5,
          [(r"You separate the variables: $\displaystyle\int y\,dy=\int\dfrac{4x}{x^{2}+1}\,dx$", 1), (r"You integrate the left side: $\tfrac12y^{2}$", 1),
           (r"You integrate the right side: $2\ln(x^{2}+1)+C$", 1), (r"You use $y=2$ at $x=0$ to find $C=2$", 1), (r"You write $y=2\sqrt{1+\ln(x^{2}+1)}$", 1)],
          r"When the variables can be separated, move every $y$ to one side with $dy$ and every $x$ to the other with $dx$, integrate both sides, and use the given condition to find the constant before solving for $y$.",
          r"Separating the variables: $y\,dy=\dfrac{4x}{x^{2}+1}\,dx$. Integrating, $\tfrac12y^{2}=2\ln(x^{2}+1)+C$. With $y=2$ at $x=0$: $2=2\ln1+C$, so $C=2$. Then $y^{2}=4\ln(x^{2}+1)+4$ and, since $y>0$, $y=2\sqrt{1+\ln(x^{2}+1)}$.",
          ans=r"$y=2\sqrt{1+\ln(x^{2}+1)}$"),
        S("b", r"Find the solution of the differential equation $\cos x\dfrac{dy}{dx}+y\sin x=\cos^{2}x$, for $0\le x<\dfrac{\pi}{2}$, given that $y=2$ when $x=0$.",
          ["first order differential equations"], "moyenne", 5,
          [(r"You divide by $\cos x$ to write $\dfrac{dy}{dx}+y\tan x=\cos x$", 1), (r"You find the integrating factor $e^{\int\tan x\,dx}=\sec x$", 1),
           (r"You write $\dfrac{d}{dx}\left(y\sec x\right)=\cos x\sec x=1$", 1), (r"You integrate: $y\sec x=x+C$", 1), (r"You use $y(0)=2$ to find $C=2$ and write $y=(x+2)\cos x$", 1)],
          r"For $\dfrac{dy}{dx}+P(x)y=Q(x)$ multiply by the integrating factor $e^{\int P\,dx}$, so that the left side becomes the derivative of (factor $\times\,y$); integrate and use the condition to fix the constant.",
          r"In standard form $\dfrac{dy}{dx}+(\tan x)\,y=\cos x$. The integrating factor is $e^{\int\tan x\,dx}=e^{\ln\sec x}=\sec x$ (valid because $\sec x>0$ on the interval). Then $\dfrac{d}{dx}\left(y\sec x\right)=\sec x\cos x=1$, so $y\sec x=x+C$. With $y=2$ at $x=0$: $2\times1=0+C$, so $C=2$ and $y=(x+2)\cos x$.",
          ans=r"$y=(x+2)\cos x$",
          piege=r"The equation must be divided by $\cos x$ before reading $P(x)$: here $P(x)=\tan x$, not $\sin x$."),
    ]))

    # ---- Exercice 8 : reduction to linear form (9) ----
    ex.append(E("8", G, 9, "", [
        S("a", r"The variables $x$ and $y$ are related by $y=ax^{b}$, where $a$ and $b$ are constants. A graph of $\lg y$ against $\lg x$ is a straight line passing through the points $(0.2,\,0.9)$ and $(0.8,\,2.4)$. Show that the relation can be written in the form $\lg y=b\lg x+\lg a$, and find the values of $a$ and $b$.",
          ["reduction to linear form", "logarithms"], "faible", 4,
          [(r"You take logarithms to base $10$ to obtain $\lg y=\lg a+b\lg x$", 1), (r"You identify the gradient as $b$ and calculate $b=\dfrac{2.4-0.9}{0.8-0.2}=2.5$", 1),
           (r"You use a point to find the intercept: $\lg a=0.9-2.5\times0.2=0.4$", 1), (r"You obtain $a=10^{0.4}\approx2.51$", 1)],
          r"A power law $y=ax^{b}$ becomes linear when logarithms are taken: $\lg y=b\lg x+\lg a$ is a straight line in the variables $X=\lg x$ and $Y=\lg y$, with gradient $b$ and intercept $\lg a$.",
          r"Taking $\lg$ of both sides: $\lg y=\lg a+b\lg x$, which is of the form $Y=bX+\lg a$. The gradient is $b=\dfrac{2.4-0.9}{0.8-0.2}=2.5$. At $(0.2,0.9)$: $0.9=\lg a+2.5\times0.2$, so $\lg a=0.4$ and $a=10^{0.4}=2.51$ to $3$ significant figures.",
          ans=r"$b=2.5$ ; $a=10^{0.4}\approx2.51$"),
        S("b", r"The value $V$, in thousands of FCFA, of a motorcycle used for taxi work in Yaounde is modelled by $V=Ak^{t}$, where $t$ is the number of years after purchase. The value is $640$ when $t=1$ and $409.6$ when $t=3$. Find $A$ and $k$, and find the least whole number of years after which the motorcycle is worth less than $200$ thousand FCFA.",
          ["reduction to linear form", "logarithms"], "moyenne", 5,
          [(r"You take logarithms: $\lg V=\lg A+t\lg k$", 1), (r"You divide the two conditions: $k^{2}=\dfrac{409.6}{640}=0.64$", 1), (r"You obtain $k=0.8$ and $A=800$", 1),
           (r"You solve $800\times0.8^{t}<200$ by logarithms: $t>\dfrac{\lg0.25}{\lg0.8}\approx6.21$", 1), (r"You conclude that the least whole number of years is $7$", 1)],
          r"An exponential model $V=Ak^{t}$ becomes linear with $\lg V=\lg A+t\lg k$; to find the constants, divide the two equations to eliminate $A$, and to solve an inequality with $t$ in the exponent take logarithms of both sides, remembering to reverse the inequality when dividing by a negative logarithm.",
          r"Taking logarithms: $\lg V=\lg A+t\lg k$. From $Ak=640$ and $Ak^{3}=409.6$, dividing gives $k^{2}=0.64$, so $k=0.8$ ($k>0$) and $A=\dfrac{640}{0.8}=800$. Now $800\times0.8^{t}<200$ means $0.8^{t}<0.25$, so $t\lg0.8<\lg0.25$. Since $\lg0.8<0$, dividing reverses the inequality: $t>\dfrac{\lg0.25}{\lg0.8}=6.21$. The least whole number of years is $7$.",
          ans=r"$A=800$, $k=0.8$ ; $7$ years",
          piege=r"Dividing both sides of $t\lg0.8<\lg0.25$ by the negative number $\lg0.8$ reverses the inequality sign."),
    ]))

    # ---- Exercice 9 : study of a rational function (11) ----
    ex.append(E("9", G, 11, r"The function $f$ is defined for $x\in\mathbb R$, $x\ne\pm1$, by $f(x)=\dfrac{x^{2}-4}{x^{2}-1}$.", [
        S("a", r"Find the equations of all the asymptotes of the curve $y=f(x)$.",
          ["asymptotes of rational functions"], "faible", 3,
          [(r"You state that the denominator is zero at $x=\pm1$ while the numerator equals $-3$, so $x=1$ and $x=-1$ are vertical asymptotes", 1),
           (r"You write $f(x)=1-\dfrac{3}{x^{2}-1}$ (or divide numerator and denominator by $x^{2}$)", 1), (r"You state that $f(x)\to1$ as $x\to\pm\infty$: the horizontal asymptote is $y=1$", 1)],
          r"A rational function has a vertical asymptote where the denominator is zero and the numerator is not; when numerator and denominator have the same degree the horizontal asymptote is the ratio of the leading coefficients, found by dividing out the highest power of $x$.",
          r"At $x=\pm1$ the denominator is $0$ and the numerator is $1-4=-3\ne0$, so $x=1$ and $x=-1$ are vertical asymptotes. Also $f(x)=\dfrac{x^{2}-1-3}{x^{2}-1}=1-\dfrac{3}{x^{2}-1}$, and $\dfrac{3}{x^{2}-1}\to0$ as $x\to\pm\infty$, so $y=1$ is a horizontal asymptote.",
          ans=r"$x=1$, $x=-1$ and $y=1$"),
        S("b", r"Find the coordinates of the points where the curve meets the axes.",
          ["curve sketching"], "faible", 2,
          [(r"You solve $x^{2}-4=0$ to find $(-2,0)$ and $(2,0)$", 1), (r"You find $f(0)=\dfrac{-4}{-1}=4$, so the point $(0,4)$", 1)],
          r"The curve meets the $x$-axis where the numerator is zero (and the denominator is not) and the $y$-axis at $x=0$.",
          r"$f(x)=0$ when $x^{2}-4=0$, that is $x=\pm2$: the points $(-2,0)$ and $(2,0)$. At $x=0$: $f(0)=\dfrac{-4}{-1}=4$, the point $(0,4)$.",
          ans=r"$(-2,0)$, $(2,0)$, $(0,4)$"),
        S("c", r"Show that $f'(x)=\dfrac{6x}{(x^{2}-1)^{2}}$, and find the coordinates of the stationary point of the curve, determining its nature.",
          ["curve sketching", "differentiation techniques"], "moyenne", 3,
          [(r"You differentiate $f(x)=1-3(x^{2}-1)^{-1}$ to obtain $f'(x)=\dfrac{6x}{(x^{2}-1)^{2}}$", 1), (r"You solve $f'(x)=0$: only $x=0$, so the point is $(0,4)$", 1),
           (r"You state that $f'(x)<0$ for $x<0$ and $f'(x)>0$ for $x>0$, so it is a minimum", 1)],
          r"Differentiate by writing the function as a constant plus a power, or by the quotient rule; stationary points satisfy $f'(x)=0$, and their nature follows from the sign of $f'(x)$ on each side.",
          r"$f(x)=1-3(x^{2}-1)^{-1}$, so $f'(x)=-3\times(-1)(x^{2}-1)^{-2}\times2x=\dfrac{6x}{(x^{2}-1)^{2}}$. The denominator is positive, so $f'(x)=0$ only when $x=0$, giving the point $(0,f(0))=(0,4)$. For $x<0$ the gradient is negative and for $x>0$ it is positive, so the point $(0,4)$ is a minimum.",
          ans=r"stationary point $(0,4)$, a minimum"),
        S("d", r"Sketch the curve $y=f(x)$, showing the asymptotes, the points found in parts (b) and (c), and the behaviour near each asymptote.",
          ["curve sketching", "asymptotes of rational functions"], "elevee", 3,
          [(r"You draw the dashed asymptotes $x=-1$, $x=1$ and $y=1$ and mark $(-2,0)$, $(2,0)$ and $(0,4)$", 1),
           (r"You draw the central branch with its minimum at $(0,4)$, rising to $+\infty$ on both sides along $x=\pm1$", 1),
           (r"You draw the two outer branches, each coming from $-\infty$ along $x=\pm1$, crossing the $x$-axis at $\pm2$ and approaching $y=1$ from below", 1)],
          r"A sketch uses the asymptotes, the intercepts and the stationary point: draw the asymptotes first, place the points, then study the sign of $f(x)$ in each interval cut by the vertical asymptotes to decide whether each branch goes to $+\infty$ or $-\infty$.",
          r"The curve is symmetric about the $y$-axis because $f(-x)=f(x)$. For $-1<x<1$ both $x^{2}-4$ and $x^{2}-1$ are negative, so $f(x)>0$: the central branch has its minimum at $(0,4)$ and tends to $+\infty$ as $x\to\pm1$. For $x>1$, $f(x)=1-\dfrac{3}{x^{2}-1}$ is below $1$; it tends to $-\infty$ as $x\to1^{+}$, crosses the axis at $(2,0)$ and approaches $y=1$ from below. The branch for $x<-1$ is the mirror image. The curve is shown in the figure below.",
          fig="courbe_f"),
    ]))

    # ---- Exercice 10 : integration and differentiation (10) ----
    ex.append(E("10", G, 10, "", [
        S("a", r"Given that $y=\dfrac{\ln x}{x^{2}}$ for $x>0$, find $\dfrac{dy}{dx}$ and the exact coordinates of the stationary point of the curve.",
          ["differentiation techniques"], "faible", 4,
          [(r"You apply the quotient rule with $u=\ln x$ and $v=x^{2}$", 1), (r"You obtain $\dfrac{dy}{dx}=\dfrac{1-2\ln x}{x^{3}}$", 1),
           (r"You solve $\ln x=\tfrac12$ to obtain $x=\sqrt e$", 1), (r"You obtain $y=\dfrac{1}{2e}$", 1)],
          r"The quotient rule gives $\dfrac{d}{dx}\left(\dfrac uv\right)=\dfrac{u'v-uv'}{v^{2}}$; a stationary point is where the derivative is zero, so set the numerator equal to zero and substitute the solution back into the function.",
          r"With $u=\ln x$ and $v=x^{2}$: $\dfrac{dy}{dx}=\dfrac{\frac1x\cdot x^{2}-\ln x\cdot2x}{x^{4}}=\dfrac{x-2x\ln x}{x^{4}}=\dfrac{1-2\ln x}{x^{3}}$. This is zero when $\ln x=\tfrac12$, so $x=e^{1/2}=\sqrt e$. Then $y=\dfrac{1/2}{e}=\dfrac{1}{2e}$.",
          ans=r"$\dfrac{dy}{dx}=\dfrac{1-2\ln x}{x^{3}}$ ; stationary point $\left(\sqrt e,\ \dfrac{1}{2e}\right)$"),
        S("b", r"Use the substitution $u=x+1$ to show that $\displaystyle\int_{0}^{3}\dfrac{x}{\sqrt{x+1}}\,dx=\dfrac83$.",
          ["integration by substitution", "definite integrals"], "moyenne", 3,
          [(r"You change the variable and the limits: $x=u-1$, $dx=du$, limits $u=1$ to $u=4$", 1), (r"You write the integrand $\dfrac{u-1}{\sqrt u}=u^{1/2}-u^{-1/2}$ and integrate: $\tfrac23u^{3/2}-2u^{1/2}$", 1),
           (r"You evaluate: $\left(\tfrac{16}{3}-4\right)-\left(\tfrac23-2\right)=\tfrac83$", 1)],
          r"In a definite integral, a substitution must change the limits as well as the integrand: express $x$ and $dx$ in terms of the new variable, split the fraction into powers, integrate, and evaluate between the new limits.",
          r"With $u=x+1$: $x=u-1$, $dx=du$; when $x=0$, $u=1$ and when $x=3$, $u=4$. So $\displaystyle\int_{0}^{3}\dfrac{x}{\sqrt{x+1}}\,dx=\int_{1}^{4}\dfrac{u-1}{\sqrt u}\,du=\int_{1}^{4}\left(u^{1/2}-u^{-1/2}\right)du=\left[\tfrac23u^{3/2}-2u^{1/2}\right]_{1}^{4}$. At $u=4$: $\tfrac{16}{3}-4=\tfrac43$. At $u=1$: $\tfrac23-2=-\tfrac43$. The value is $\tfrac43+\tfrac43=\tfrac83$.",
          ),
        S("c", r"Use integration by parts to find the exact value of $\displaystyle\int_{0}^{1}x\,e^{2x}\,dx$.",
          ["definite integrals"], "moyenne", 3,
          [(r"You choose $u=x$ and $v'=e^{2x}$, so $v=\tfrac12e^{2x}$", 1), (r"You write $\left[\tfrac12xe^{2x}\right]_{0}^{1}-\tfrac12\displaystyle\int_{0}^{1}e^{2x}\,dx$", 1),
           (r"You evaluate to obtain $\dfrac{e^{2}+1}{4}$", 1)],
          r"Integration by parts uses $\displaystyle\int u\,v'\,dx=uv-\int u'v\,dx$; choose $u$ as the factor that becomes simpler when differentiated (here $x$) and $v'$ as the factor that is easy to integrate.",
          r"With $u=x$, $v'=e^{2x}$: $u'=1$, $v=\tfrac12e^{2x}$. Then $\displaystyle\int_{0}^{1}xe^{2x}\,dx=\left[\tfrac12xe^{2x}\right]_{0}^{1}-\tfrac12\int_{0}^{1}e^{2x}\,dx=\tfrac12e^{2}-\tfrac12\left[\tfrac12e^{2x}\right]_{0}^{1}=\tfrac12e^{2}-\tfrac14\left(e^{2}-1\right)=\dfrac{e^{2}+1}{4}$.",
          ans=r"$\dfrac{e^{2}+1}{4}$"),
    ]))

    return ex
