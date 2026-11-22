r"""Les 10 exercices de l'epreuve inedite GCE A Level Further Mathematics Paper 2 n.1 (100 marks, 3 h, tout obligatoire).

Structure mesuree sur les Paper 2 de 2025 et 2026 (10 exercices, 100 marks) ; aucune donnee reprise d'un sujet reel. Chaque sous-question :
bareme exact (`pts`), grille `crit` (somme = pts), rappel, resolution, reponse finale `ans` (recalculee par verifier_reponses_furthermaths_p2.py).
Chaines BRUTES. Numeros affiches : lettres a, b, c... (un numero unique par exercice).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_addmaths_p2_a import E, S  # noqa: E402,F401

G = ""  # pas de groupes : paper plat


def exercices():
    ex = []

    # ---- Exercice 1 : hyperbolic functions and integration (9) ----
    ex.append(E("1", G, 9, "", [
        S("a", r"Solve the equation $5\cosh x-3\sinh x=5$, giving your answers in exact form.",
          ["hyperbolic functions"], "moyenne", 4,
          [(r"You write $5\cosh x-3\sinh x=e^{x}+4e^{-x}$", 1), (r"You multiply by $e^{x}$ to obtain the quadratic $e^{2x}-5e^{x}+4=0$", 1),
           (r"You factorise: $(e^{x}-1)(e^{x}-4)=0$", 1), (r"You obtain $x=0$ and $x=\ln 4$", 1)],
          r"Replace $\cosh x$ and $\sinh x$ by their exponential definitions $\tfrac12(e^{x}\pm e^{-x})$; the equation becomes a quadratic in $e^{x}$.",
          r"$5\cosh x-3\sinh x=\tfrac52(e^{x}+e^{-x})-\tfrac32(e^{x}-e^{-x})=e^{x}+4e^{-x}$. The equation is $e^{x}+4e^{-x}=5$. Multiply by $e^{x}$: $e^{2x}-5e^{x}+4=0$, that is $(e^{x}-1)(e^{x}-4)=0$. So $e^{x}=1$ or $e^{x}=4$, which gives $x=0$ or $x=\ln 4$. Both values are valid because $e^{x}>0$ for every real $x$.",
          ans=r"$x=0$ or $x=\ln 4$",
          piege=r"Do not divide the equation by $e^{x}$ before factorising: the root $e^{x}=1$ would be kept only if you remember that the product is zero, not the factors."),
        S("b", r"Use the identity $\sinh^{2}x=\tfrac12(\cosh 2x-1)$ to show that $\displaystyle\int_{0}^{\ln 2}\sinh^{2}x\,dx=\dfrac{15}{32}-\dfrac12\ln 2$.",
          ["hyperbolic functions", "integration techniques"], "moyenne", 5,
          [(r"You rewrite the integrand as $\tfrac12(\cosh 2x-1)$", 1), (r"You integrate: $\tfrac14\sinh 2x-\tfrac12 x$", 2),
           (r"You evaluate $\sinh(2\ln 2)=\tfrac12\left(4-\tfrac14\right)=\tfrac{15}{8}$", 1), (r"You conclude $\tfrac{15}{32}-\tfrac12\ln 2$", 1)],
          r"To integrate an even power of $\sinh x$, convert it with a double-angle identity into $\cosh 2x$, whose integral is $\tfrac12\sinh 2x$. Evaluate at the limits using $e^{\ln a}=a$.",
          r"$\displaystyle\int_{0}^{\ln 2}\sinh^{2}x\,dx=\tfrac12\int_{0}^{\ln 2}(\cosh 2x-1)\,dx=\tfrac12\left[\tfrac12\sinh 2x-x\right]_{0}^{\ln 2}=\tfrac14\sinh(2\ln 2)-\tfrac12\ln 2$. Now $\sinh(2\ln 2)=\tfrac12\left(e^{2\ln 2}-e^{-2\ln 2}\right)=\tfrac12\left(4-\tfrac14\right)=\tfrac{15}{8}$. Hence the integral is $\tfrac14\times\tfrac{15}{8}-\tfrac12\ln 2=\tfrac{15}{32}-\tfrac12\ln 2$.",
          conseil=r"Keep $e^{2\ln 2}=4$ and $e^{-2\ln 2}=\tfrac14$ in mind: they turn every hyperbolic value at $\ln 2$ into a fraction."),
    ]))

    # ---- Exercice 2 : lines and planes (9) ----
    ex.append(E("2", G, 9, "", [
        S("a", r"The points $A(1,0,2)$, $B(3,1,1)$ and $C(2,3,0)$ lie in a plane $\Pi$. Find $\overrightarrow{AB}\times\overrightarrow{AC}$ and hence a Cartesian equation of $\Pi$.",
          ["scalar and vector products", "lines and planes"], "faible", 3,
          [(r"You find $\overrightarrow{AB}=(2,1,-1)$ and $\overrightarrow{AC}=(1,3,-2)$", 1), (r"You obtain $\overrightarrow{AB}\times\overrightarrow{AC}=(1,3,5)$", 1),
           (r"You write $x+3y+5z=11$ using the point $A$", 1)],
          r"The vector product of two vectors lying in a plane is normal to the plane; a normal $\mathbf n$ and one point $A$ give the equation $\mathbf n\cdot\mathbf r=\mathbf n\cdot\mathbf a$.",
          r"$\overrightarrow{AB}=(2,1,-1)$ and $\overrightarrow{AC}=(1,3,-2)$. Then $\overrightarrow{AB}\times\overrightarrow{AC}=(1\times(-2)-(-1)\times3,\ (-1)\times1-2\times(-2),\ 2\times3-1\times1)=(1,3,5)$. The plane is $x+3y+5z=d$ with $d=1+0+10=11$. Check with $B$: $3+3+5=11$, and with $C$: $2+9+0=11$.",
          ans=r"$x+3y+5z=11$"),
        S("b", r"Find the perpendicular distance from the point $D(2,-1,1)$ to the plane $\Pi$, and the coordinates of the foot of the perpendicular from $D$ to $\Pi$.",
          ["lines and planes"], "moyenne", 3,
          [(r"You write the line through $D$ normal to $\Pi$: $(2+t,-1+3t,1+5t)$", 1), (r"You substitute into the plane to find $t=\tfrac15$", 1),
           (r"You obtain the foot $\left(\tfrac{11}{5},-\tfrac25,2\right)$ and the distance $\tfrac{\sqrt{35}}{5}$", 1)],
          r"The shortest distance from a point to a plane is measured along the normal: write the line through the point in the direction of the normal and find where it meets the plane.",
          r"The line through $D$ with direction $(1,3,5)$ is $(2+t,\,-1+3t,\,1+5t)$. Substituting into $x+3y+5z=11$: $2+t-3+9t+5+25t=11$, so $4+35t=11$ and $t=\tfrac15$. The foot is $\left(\tfrac{11}{5},-\tfrac25,2\right)$. The distance is $|t|\,|(1,3,5)|=\tfrac15\sqrt{35}=\tfrac{\sqrt{35}}{5}\approx1.18$.",
          ans=r"foot $\left(\tfrac{11}{5},-\tfrac25,2\right)$ ; distance $\tfrac{\sqrt{35}}{5}$"),
        S("c", r"The line $M$ has equation $\mathbf r=(0,1,1)+s(2,-1,1)$. Find, to the nearest $0.1^{\circ}$, the acute angle between $M$ and the plane $\Pi$.",
          ["lines and planes", "scalar and vector products"], "moyenne", 3,
          [(r"You calculate the scalar product $(2,-1,1)\cdot(1,3,5)=4$", 1), (r"You write $\sin\theta=\dfrac{4}{\sqrt6\,\sqrt{35}}$", 1), (r"You obtain $\theta\approx16.0^{\circ}$", 1)],
          r"The angle $\theta$ between a line with direction $\mathbf d$ and a plane with normal $\mathbf n$ satisfies $\sin\theta=\dfrac{|\mathbf d\cdot\mathbf n|}{|\mathbf d||\mathbf n|}$ (sine, because $\mathbf n$ is perpendicular to the plane).",
          r"$\mathbf d\cdot\mathbf n=2-3+5=4$, $|\mathbf d|=\sqrt6$ and $|\mathbf n|=\sqrt{35}$. So $\sin\theta=\dfrac{4}{\sqrt{210}}\approx0.2760$ and $\theta\approx16.0^{\circ}$.",
          ans=r"$16.0^{\circ}$",
          piege=r"The formula with cosine gives the angle between the line and the normal, not between the line and the plane."),
    ]))

    # ---- Exercice 3 : first order differential equation (8) ----
    ex.append(E("3", G, 8, "", [
        S("a", r"Given that $x>0$, find the solution of the differential equation $x\dfrac{dy}{dx}+2y=x^{3}$ for which $y=1$ when $x=1$, giving $y$ in terms of $x$.",
          ["first order differential equations"], "moyenne", 5,
          [(r"You divide by $x$ and identify the integrating factor $x^{2}$", 1), (r"You write $\dfrac{d}{dx}\left(x^{2}y\right)=x^{4}$", 1),
           (r"You integrate: $x^{2}y=\tfrac15x^{5}+C$", 1), (r"You use $y(1)=1$ to find $C=\tfrac45$", 1), (r"You write $y=\tfrac15x^{3}+\dfrac{4}{5x^{2}}$", 1)],
          r"For $\dfrac{dy}{dx}+P(x)y=Q(x)$ multiply by the integrating factor $e^{\int P\,dx}$: the left side becomes $\dfrac{d}{dx}\left(\text{factor}\times y\right)$ and the equation can be integrated.",
          r"In standard form $\dfrac{dy}{dx}+\dfrac2x\,y=x^{2}$. The integrating factor is $e^{\int 2/x\,dx}=e^{2\ln x}=x^{2}$. Then $\dfrac{d}{dx}\left(x^{2}y\right)=x^{2}\cdot x^{2}=x^{4}$, so $x^{2}y=\tfrac15x^{5}+C$. With $y=1$ at $x=1$: $1=\tfrac15+C$, so $C=\tfrac45$. Therefore $y=\tfrac15x^{3}+\dfrac{4}{5x^{2}}$.",
          ans=r"$y=\tfrac15x^{3}+\dfrac{4}{5x^{2}}$",
          piege=r"The equation must be written with $\dfrac{dy}{dx}$ alone before reading $P(x)$: here $P(x)=\tfrac2x$, not $2$."),
        S("b", r"Find the value of $y$ when $x=2$, and the limit of $\dfrac{y}{x^{3}}$ as $x\to\infty$.",
          ["first order differential equations"], "faible", 3,
          [(r"You substitute $x=2$: $\tfrac85+\tfrac{4}{20}$", 1), (r"You obtain $y=\tfrac95$", 1), (r"You write $\dfrac{y}{x^{3}}=\tfrac15+\dfrac{4}{5x^{5}}\to\tfrac15$", 1)],
          r"Evaluate a particular solution by substitution; for a limit at infinity, divide by the dominant power and use the fact that $x^{-n}\to0$ for $n>0$.",
          r"At $x=2$: $y=\tfrac{8}{5}+\tfrac{4}{5\times4}=\tfrac85+\tfrac15=\tfrac95$. For the limit, $\dfrac{y}{x^{3}}=\tfrac15+\dfrac{4}{5x^{5}}$ and $\dfrac{4}{5x^{5}}\to0$ as $x\to\infty$, so the limit is $\tfrac15$.",
          ans=r"$y=\tfrac95$ ; limit $\tfrac15$"),
    ]))

    # ---- Exercice 4 : linear transformations and matrices (8) ----
    ex.append(E("4", G, 8, "", [
        S("a", r"The matrix $\mathbf M=\begin{pmatrix}4&-1\\2&1\end{pmatrix}$ represents a linear transformation $T$ of the plane. Find $\det\mathbf M$ and the area of the image under $T$ of the triangle with vertices $(0,0)$, $(4,0)$ and $(0,3)$.",
          ["matrix algebra", "linear transformations"], "faible", 3,
          [(r"You calculate $\det\mathbf M=4\times1-(-1)\times2=6$", 1), (r"You find the area of the triangle: $\tfrac12\times4\times3=6$", 1), (r"You multiply: image area $6\times6=36$", 1)],
          r"A linear transformation with matrix $\mathbf M$ multiplies every area by $|\det\mathbf M|$.",
          r"$\det\mathbf M=4\times1-(-1)\times2=6$. The triangle has area $\tfrac12\times4\times3=6$, so its image has area $6\times6=36$.",
          ans=r"$\det\mathbf M=6$ ; area $36$"),
        S("b", r"Find $\mathbf M^{-1}$ and hence the coordinates of the point whose image under $T$ is $(13,5)$.",
          ["matrix algebra"], "moyenne", 2,
          [(r"You write $\mathbf M^{-1}=\tfrac16\begin{pmatrix}1&1\\-2&4\end{pmatrix}$", 1), (r"You obtain the point $(3,-1)$", 1)],
          r"For $\begin{pmatrix}a&b\\c&d\end{pmatrix}$ the inverse is $\dfrac{1}{ad-bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}$; the original point is $\mathbf M^{-1}$ applied to the image.",
          r"$\mathbf M^{-1}=\tfrac16\begin{pmatrix}1&1\\-2&4\end{pmatrix}$. Then $\mathbf M^{-1}\begin{pmatrix}13\\5\end{pmatrix}=\tfrac16\begin{pmatrix}18\\-6\end{pmatrix}=\begin{pmatrix}3\\-1\end{pmatrix}$. Check: $\mathbf M\begin{pmatrix}3\\-1\end{pmatrix}=\begin{pmatrix}12+1\\6-1\end{pmatrix}=\begin{pmatrix}13\\5\end{pmatrix}$.",
          ans=r"$(3,-1)$"),
        S("c", r"Find the equations of the two lines through the origin that are mapped onto themselves by $T$.",
          ["linear transformations", "matrix algebra"], "moyenne", 3,
          [(r"You write the characteristic equation $\lambda^{2}-5\lambda+6=0$", 1), (r"You find $\lambda=2$ and $\lambda=3$", 1), (r"You obtain the lines $y=2x$ and $y=x$", 1)],
          r"A line through the origin is invariant when its direction vector is an eigenvector of $\mathbf M$; the eigenvalues solve $\det(\mathbf M-\lambda\mathbf I)=0$.",
          r"$\det(\mathbf M-\lambda\mathbf I)=(4-\lambda)(1-\lambda)+2=\lambda^{2}-5\lambda+6=(\lambda-2)(\lambda-3)$. For $\lambda=2$: $2x-y=0$, so the direction is $(1,2)$ and the line is $y=2x$. For $\lambda=3$: $x-y=0$, so the line is $y=x$.",
          ans=r"$y=2x$ and $y=x$"),
    ]))

    # ---- Exercice 5 : congruences and groups (9) ----
    ex.append(E("5", G, 9, "", [
        S("a", r"Solve the congruence $7x\equiv4\pmod{15}$.",
          ["linear congruences", "modular arithmetic"], "faible", 3,
          [(r"You find the inverse of $7$ modulo $15$: $7\times13=91\equiv1$", 1), (r"You multiply: $x\equiv4\times13=52$", 1), (r"You reduce: $x\equiv7\pmod{15}$", 1)],
          r"When $\gcd(a,n)=1$, the congruence $ax\equiv b\pmod n$ has exactly one solution modulo $n$, found by multiplying by the inverse of $a$ modulo $n$.",
          r"Since $7\times13=91=6\times15+1$, the inverse of $7$ modulo $15$ is $13$. Then $x\equiv13\times4=52\equiv7\pmod{15}$. Check: $7\times7=49=3\times15+4$.",
          ans=r"$x\equiv7\pmod{15}$"),
        S("b", r"Find the remainder when $5^{77}$ is divided by $13$.",
          ["modular arithmetic"], "moyenne", 3,
          [(r"You show $5^{4}=625\equiv1\pmod{13}$", 1), (r"You write $77=4\times19+1$", 1), (r"You conclude $5^{77}\equiv5$, remainder $5$", 1)],
          r"Find a power that is congruent to $1$ modulo the divisor: the powers then repeat in a cycle and the exponent can be reduced.",
          r"$5^{2}=25\equiv12\equiv-1\pmod{13}$, so $5^{4}\equiv1$. Since $77=4\times19+1$, $5^{77}=(5^{4})^{19}\times5\equiv1^{19}\times5=5\pmod{13}$. The remainder is $5$.",
          ans=r"$5$"),
        S("c", r"The set $G=\{1,2,4,7,8,11,13,14\}$ is a group under multiplication modulo $15$. Show that $G$ is not cyclic.",
          ["group theory"], "elevee", 3,
          [(r"You find that $4$, $11$ and $14$ have order $2$ because their squares are $1$ modulo $15$", 1), (r"You find that $2$, $7$, $8$ and $13$ have order $4$", 1),
           (r"You conclude: no element has order $8=|G|$, so $G$ has no generator", 1)],
          r"A finite group of order $n$ is cyclic exactly when it has an element of order $n$; so list the order of every element and compare it with $|G|$.",
          r"The identity is $1$. $4^{2}=16\equiv1$, $11^{2}=121\equiv1$, $14^{2}=196\equiv1$, so these three elements have order $2$. For $2$: $2,4,8,16\equiv1$, order $4$. For $7$: $7^{2}=49\equiv4$, $7^{4}\equiv16\equiv1$, order $4$. For $8$: $8^{2}=64\equiv4$, $8^{4}\equiv1$, order $4$. For $13$: $13^{2}=169\equiv4$, $13^{4}\equiv1$, order $4$. The largest order is $4$, but $|G|=8$, so no element generates $G$ and $G$ is not cyclic.",
          piege=r"Checking only one or two elements proves nothing: to show that a group is not cyclic every element must be eliminated, or a counting argument must be given."),
    ]))

    # ---- Exercice 6 : conics in polar coordinates (9) ----
    ex.append(E("6", G, 9, "", [
        S("a", r"A conic has polar equation $r=\dfrac{12}{3+2\cos\theta}$, where the pole is a focus. Find its eccentricity, say what type of conic it is, and give the equation of the corresponding directrix.",
          ["conic sections", "polar coordinates"], "moyenne", 3,
          [(r"You rewrite $r=\dfrac{4}{1+\tfrac23\cos\theta}$ and read $e=\tfrac23$ and $l=4$", 1), (r"You state that $e<1$ so the conic is an ellipse", 1), (r"You use $l=ed$ to obtain $d=6$: the directrix is $x=6$", 1)],
          r"A conic with a focus at the pole has equation $\dfrac{l}{r}=1+e\cos\theta$; the semi-latus rectum is $l=ed$ with $d$ the distance from the pole to the directrix, and the conic is an ellipse when $e<1$.",
          r"Dividing numerator and denominator by $3$: $r=\dfrac{4}{1+\tfrac23\cos\theta}$. So $e=\tfrac23$ and $l=4$. Since $e<1$ the conic is an ellipse. From $l=ed$: $d=\dfrac{4}{2/3}=6$, so the directrix is the line $x=6$ ($r\cos\theta=6$).",
          ans=r"$e=\tfrac23$, ellipse, directrix $x=6$"),
        S("b", r"Find the least and the greatest values of $r$, and hence the length of the major axis of the ellipse.",
          ["conic sections", "polar coordinates"], "moyenne", 3,
          [(r"You use $\cos\theta=1$: $r=\tfrac{12}{5}$ (least)", 1), (r"You use $\cos\theta=-1$: $r=12$ (greatest)", 1), (r"You add them: major axis $=\tfrac{12}{5}+12=\tfrac{72}{5}$", 1)],
          r"The denominator is largest when $\cos\theta=1$, which gives the least $r$, and smallest when $\cos\theta=-1$, which gives the greatest $r$; for an ellipse the two vertices on the axis through the focus are at these distances.",
          r"At $\theta=0$: $r=\dfrac{12}{5}=2.4$. At $\theta=\pi$: $r=\dfrac{12}{1}=12$. The two vertices are on opposite sides of the focus, so the major axis has length $2.4+12=14.4=\tfrac{72}{5}$. Check: $2a=\dfrac{2l}{1-e^{2}}=\dfrac{8}{5/9}=\dfrac{72}{5}$.",
          ans=r"least $\tfrac{12}{5}$, greatest $12$, major axis $\tfrac{72}{5}$"),
        S("c", r"Show that the Cartesian equation of the ellipse is $5x^{2}+48x+9y^{2}=144$.",
          ["polar coordinates", "conic sections"], "elevee", 3,
          [(r"You write $3r+2r\cos\theta=12$, that is $3r=12-2x$", 1), (r"You square and use $r^{2}=x^{2}+y^{2}$: $9(x^{2}+y^{2})=(12-2x)^{2}$", 1), (r"You expand and simplify to $5x^{2}+48x+9y^{2}=144$", 1)],
          r"To convert a polar equation to Cartesian form use $x=r\cos\theta$, $y=r\sin\theta$ and $r^{2}=x^{2}+y^{2}$; isolate $r$ before squaring.",
          r"From $r(3+2\cos\theta)=12$ we get $3r+2x=12$, so $3r=12-2x$. Squaring: $9r^{2}=(12-2x)^{2}$, that is $9x^{2}+9y^{2}=144-48x+4x^{2}$. Hence $5x^{2}+48x+9y^{2}=144$. Check with $\theta=0$, $x=2.4$: $5(5.76)+48(2.4)=28.8+115.2=144$.",
          piege=r"Squaring can add a branch with $12-2x<0$; here $x\le2.4$ on the ellipse is compatible with $12-2x>0$, so no extra points appear."),
    ]))

    # ---- Exercice 7 : complex numbers and De Moivre (10) ----
    ex.append(E("7", G, 10, "", [
        S("a", r"Express $z=\sqrt3-i$ in the form $r(\cos\theta+i\sin\theta)$ with $-\pi<\theta\le\pi$, and hence find $z^{5}$ in the form $a+ib$.",
          ["complex numbers", "de moivre theorem"], "moyenne", 3,
          [(r"You find $|z|=2$ and $\arg z=-\tfrac{\pi}{6}$", 1), (r"You apply De Moivre: $z^{5}=32\left(\cos\left(-\tfrac{5\pi}{6}\right)+i\sin\left(-\tfrac{5\pi}{6}\right)\right)$", 1),
           (r"You obtain $z^{5}=-16\sqrt3-16i$", 1)],
          r"Write $z$ in modulus-argument form $r(\cos\theta+i\sin\theta)$; De Moivre's theorem gives $z^{n}=r^{n}(\cos n\theta+i\sin n\theta)$.",
          r"$|z|=\sqrt{3+1}=2$ and $z$ lies in the fourth quadrant with $\tan\theta=-\tfrac{1}{\sqrt3}$, so $\theta=-\tfrac{\pi}{6}$: $z=2\left(\cos\tfrac{\pi}{6}-i\sin\tfrac{\pi}{6}\right)$. Then $z^{5}=32\left(\cos\left(-\tfrac{5\pi}{6}\right)+i\sin\left(-\tfrac{5\pi}{6}\right)\right)=32\left(-\tfrac{\sqrt3}{2}-\tfrac i2\right)=-16\sqrt3-16i$.",
          ans=r"$z=2\left(\cos\left(-\tfrac{\pi}{6}\right)+i\sin\left(-\tfrac{\pi}{6}\right)\right)$ ; $z^{5}=-16\sqrt3-16i$"),
        S("b", r"Use De Moivre's theorem to show that $\cos4\theta=8\cos^{4}\theta-8\cos^{2}\theta+1$.",
          ["de moivre theorem", "complex numbers"], "elevee", 4,
          [(r"You write $\cos4\theta+i\sin4\theta=(\cos\theta+i\sin\theta)^{4}$", 1), (r"You expand the binomial and take the real part: $c^{4}-6c^{2}s^{2}+s^{4}$", 1),
           (r"You replace $s^{2}=1-c^{2}$", 1), (r"You simplify to $8c^{4}-8c^{2}+1$", 1)],
          r"Expand $(\cos\theta+i\sin\theta)^{n}$ with the binomial theorem and equate real parts with $\cos n\theta$ (imaginary parts with $\sin n\theta$); then eliminate $\sin\theta$ with $\sin^{2}\theta=1-\cos^{2}\theta$.",
          r"Write $c=\cos\theta$ and $s=\sin\theta$. By De Moivre, $\cos4\theta+i\sin4\theta=(c+is)^{4}=c^{4}+4ic^{3}s-6c^{2}s^{2}-4ics^{3}+s^{4}$. The real part gives $\cos4\theta=c^{4}-6c^{2}s^{2}+s^{4}$. With $s^{2}=1-c^{2}$: $c^{4}-6c^{2}(1-c^{2})+(1-c^{2})^{2}=c^{4}-6c^{2}+6c^{4}+1-2c^{2}+c^{4}=8c^{4}-8c^{2}+1$.",
          conseil=r"Check the result at $\theta=0$: $8-8+1=1=\cos0$."),
        S("c", r"Find the three cube roots of $-8i$, giving each in the form $a+ib$.",
          ["complex numbers", "de moivre theorem"], "moyenne", 3,
          [(r"You write $-8i=8\left(\cos\left(-\tfrac{\pi}{2}\right)+i\sin\left(-\tfrac{\pi}{2}\right)\right)$", 1), (r"You write the roots $2\left(\cos\phi+i\sin\phi\right)$ with $\phi=-\tfrac{\pi}{6}+\tfrac{2k\pi}{3}$", 1),
           (r"You obtain $\sqrt3-i$, $2i$ and $-\sqrt3-i$", 1)],
          r"The $n$ nth roots of $r(\cos\alpha+i\sin\alpha)$ are $r^{1/n}\left(\cos\dfrac{\alpha+2k\pi}{n}+i\sin\dfrac{\alpha+2k\pi}{n}\right)$ for $k=0,1,\dots,n-1$.",
          r"$-8i$ has modulus $8$ and argument $-\tfrac{\pi}{2}$. The cube roots have modulus $8^{1/3}=2$ and arguments $\phi_k=\dfrac{-\pi/2+2k\pi}{3}$: $\phi_0=-\tfrac{\pi}{6}$, $\phi_1=\tfrac{\pi}{2}$, $\phi_2=\tfrac{7\pi}{6}$. The roots are $2\left(\cos\left(-\tfrac{\pi}{6}\right)+i\sin\left(-\tfrac{\pi}{6}\right)\right)=\sqrt3-i$, $2\left(\cos\tfrac{\pi}{2}+i\sin\tfrac{\pi}{2}\right)=2i$ and $2\left(\cos\tfrac{7\pi}{6}+i\sin\tfrac{7\pi}{6}\right)=-\sqrt3-i$.",
          ans=r"$\sqrt3-i$, $2i$, $-\sqrt3-i$"),
    ]))

    # ---- Exercice 8 : arc length, parametric curves and vectors (10) ----
    ex.append(E("8", G, 10, "", [
        S("a", r"A curve has parametric equations $x=t^{2}$, $y=\tfrac13t^{3}$ for $t\ge0$. Find $\dfrac{dy}{dx}$ in terms of $t$ and the equation of the tangent at the point where $t=1$.",
          ["parametric equations"], "faible", 3,
          [(r"You find $\dfrac{dx}{dt}=2t$ and $\dfrac{dy}{dt}=t^{2}$", 1), (r"You obtain $\dfrac{dy}{dx}=\tfrac t2$", 1), (r"You write the tangent at $\left(1,\tfrac13\right)$ with gradient $\tfrac12$: $3x-6y-1=0$", 1)],
          r"For parametric equations, $\dfrac{dy}{dx}=\dfrac{dy/dt}{dx/dt}$; the tangent at a point uses this gradient and the coordinates of the point.",
          r"$\dfrac{dx}{dt}=2t$ and $\dfrac{dy}{dt}=t^{2}$, so $\dfrac{dy}{dx}=\dfrac{t^{2}}{2t}=\dfrac t2$. At $t=1$ the point is $\left(1,\tfrac13\right)$ and the gradient is $\tfrac12$. The tangent is $y-\tfrac13=\tfrac12(x-1)$, that is $6y-2=3x-3$, or $3x-6y-1=0$.",
          ans=r"$\dfrac{dy}{dx}=\tfrac t2$ ; $3x-6y-1=0$"),
        S("b", r"Find the exact length of the arc of the curve from $t=0$ to $t=2$.",
          ["arc length", "parametric equations"], "moyenne", 4,
          [(r"You write $s=\displaystyle\int_{0}^{2}\sqrt{\left(\tfrac{dx}{dt}\right)^{2}+\left(\tfrac{dy}{dt}\right)^{2}}\,dt$", 1), (r"You simplify the integrand to $t\sqrt{4+t^{2}}$", 1),
           (r"You integrate: $\tfrac13\left(4+t^{2}\right)^{3/2}$", 1), (r"You evaluate: $\tfrac13\left(8^{3/2}-8\right)=\dfrac{16\sqrt2-8}{3}$", 1)],
          r"The length of a parametric arc is $\displaystyle\int\sqrt{\left(\dfrac{dx}{dt}\right)^{2}+\left(\dfrac{dy}{dt}\right)^{2}}\,dt$ between the two values of the parameter; a factor $t$ under the root often calls for the substitution $u=4+t^{2}$.",
          r"$\left(\dfrac{dx}{dt}\right)^{2}+\left(\dfrac{dy}{dt}\right)^{2}=4t^{2}+t^{4}=t^{2}(4+t^{2})$, and $t\ge0$, so the integrand is $t\sqrt{4+t^{2}}$. Then $s=\displaystyle\int_{0}^{2}t\sqrt{4+t^{2}}\,dt=\left[\tfrac13\left(4+t^{2}\right)^{3/2}\right]_{0}^{2}=\tfrac13\left(8^{3/2}-4^{3/2}\right)=\tfrac13\left(16\sqrt2-8\right)$. Numerically $s\approx4.88$.",
          ans=r"$\dfrac{16\sqrt2-8}{3}$",
          piege=r"The square root of $t^{2}(4+t^{2})$ is $t\sqrt{4+t^{2}}$ only because $t\ge0$ on the interval."),
        S("c", r"The points $P(1,2,0)$, $Q(3,-1,2)$ and $R(0,1,4)$ are vertices of a triangle. Use a vector product to find the area of triangle $PQR$.",
          ["scalar and vector products"], "moyenne", 3,
          [(r"You find $\overrightarrow{PQ}=(2,-3,2)$ and $\overrightarrow{PR}=(-1,-1,4)$", 1), (r"You obtain $\overrightarrow{PQ}\times\overrightarrow{PR}=(-10,-10,-5)$", 1), (r"You calculate the area $\tfrac12\times15=7.5$", 1)],
          r"The area of a triangle with sides $\mathbf a$ and $\mathbf b$ from one vertex is $\tfrac12|\mathbf a\times\mathbf b|$.",
          r"$\overrightarrow{PQ}=(2,-3,2)$ and $\overrightarrow{PR}=(-1,-1,4)$. Then $\overrightarrow{PQ}\times\overrightarrow{PR}=\big((-3)(4)-(2)(-1),\ (2)(-1)-(2)(4),\ (2)(-1)-(-3)(-1)\big)=(-10,-10,-5)$, whose modulus is $\sqrt{100+100+25}=15$. The area is $\tfrac12\times15=7.5$ square units.",
          ans=r"$7.5$ square units"),
    ]))

    # ---- Exercice 9 : study and sketch of a function (14) ----
    ex.append(E("9", G, 14, r"The function $f$ is defined for $x\ne1$ by $f(x)=\dfrac{x^{2}-x-6}{x-1}$.", [
        S("a", r"Find the equations of all the asymptotes of the curve $y=f(x)$.",
          ["curve asymptotes", "limits of functions"], "moyenne", 3,
          [(r"You divide to write $f(x)=x-\dfrac{6}{x-1}$", 1), (r"You identify the vertical asymptote $x=1$", 1), (r"You identify the oblique asymptote $y=x$ since $\dfrac{6}{x-1}\to0$", 1)],
          r"A rational function has a vertical asymptote where the denominator is zero and the numerator is not; when the numerator has degree one more than the denominator, division gives the oblique asymptote as the quotient.",
          r"$x^{2}-x-6=(x-1)x-6$, so $f(x)=x-\dfrac{6}{x-1}$. At $x=1$ the numerator is $-6\ne0$ and the denominator is zero, so $x=1$ is a vertical asymptote. As $x\to\pm\infty$, $\dfrac{6}{x-1}\to0$ and $f(x)-x\to0$, so $y=x$ is an oblique asymptote.",
          ans=r"$x=1$ and $y=x$"),
        S("b", r"Find the coordinates of the points where the curve meets the axes.",
          ["curve sketching"], "faible", 2,
          [(r"You solve $x^{2}-x-6=0$: $x=-2$ and $x=3$", 1), (r"You find $f(0)=6$", 1)],
          r"The curve meets the $x$-axis where the numerator is zero and the $y$-axis at $x=0$.",
          r"$f(x)=0$ when $x^{2}-x-6=(x-3)(x+2)=0$, so the curve meets the $x$-axis at $(-2,0)$ and $(3,0)$. At $x=0$: $f(0)=\dfrac{-6}{-1}=6$, so it meets the $y$-axis at $(0,6)$.",
          ans=r"$(-2,0)$, $(3,0)$, $(0,6)$"),
        S("c", r"Show that $f'(x)>0$ for all $x\ne1$, and deduce that the curve has no turning points.",
          ["curve sketching"], "moyenne", 3,
          [(r"You differentiate $f(x)=x-6(x-1)^{-1}$", 1), (r"You obtain $f'(x)=1+\dfrac{6}{(x-1)^{2}}$", 1), (r"You conclude: $f'(x)>1>0$ because $(x-1)^{2}>0$, so $f'(x)=0$ has no solution", 1)],
          r"Turning points occur where $f'(x)=0$; to prove that there are none, show that $f'(x)$ has a constant sign for every $x$ in the domain.",
          r"$f(x)=x-6(x-1)^{-1}$, so $f'(x)=1+6(x-1)^{-2}=1+\dfrac{6}{(x-1)^{2}}$. Since $(x-1)^{2}>0$ for $x\ne1$, $f'(x)>1>0$. The derivative is never zero, so there is no turning point, and $f$ is increasing on each of the intervals $x<1$ and $x>1$.",
          ans=r"$f'(x)=1+\dfrac{6}{(x-1)^{2}}>0$"),
        S("d", r"Describe the behaviour of $f(x)$ as $x\to1^{-}$ and as $x\to1^{+}$.",
          ["limits of functions", "curve asymptotes"], "moyenne", 2,
          [(r"You state that $f(x)\to+\infty$ as $x\to1^{-}$ because $x-1<0$ and $-\dfrac{6}{x-1}>0$", 1), (r"You state that $f(x)\to-\infty$ as $x\to1^{+}$", 1)],
          r"Near a vertical asymptote study the sign of the denominator on each side: a negative numerator over a small positive number tends to $-\infty$, over a small negative number to $+\infty$.",
          r"Use $f(x)=x-\dfrac{6}{x-1}$. As $x\to1^{-}$, $x-1$ is a small negative number, so $-\dfrac{6}{x-1}\to+\infty$ and $f(x)\to+\infty$. As $x\to1^{+}$, $x-1$ is a small positive number, so $-\dfrac{6}{x-1}\to-\infty$ and $f(x)\to-\infty$.",
          ans=r"$f(x)\to+\infty$ as $x\to1^{-}$ ; $f(x)\to-\infty$ as $x\to1^{+}$"),
        S("e", r"Sketch the curve $y=f(x)$, showing the asymptotes and the points found in part (b).",
          ["curve sketching"], "elevee", 4,
          [(r"You draw the two asymptotes $x=1$ and $y=x$ as dashed lines", 1), (r"You mark $(-2,0)$, $(3,0)$ and $(0,6)$", 1),
           (r"You draw the left branch rising to $+\infty$ along $x=1$ and passing through $(-2,0)$ and $(0,6)$", 1), (r"You draw the right branch rising from $-\infty$ along $x=1$, through $(3,0)$, and approaching $y=x$", 1)],
          r"A sketch uses the asymptotes, the intercepts and the direction of variation: draw the asymptotes first, place the points, then draw each branch without crossing a vertical asymptote.",
          r"Draw the dashed lines $x=1$ and $y=x$. Plot $(-2,0)$, $(0,6)$ and $(3,0)$. On the left of $x=1$ the function is increasing, passes through $(-2,0)$ and $(0,6)$ and tends to $+\infty$ as $x\to1^{-}$; for $x\to-\infty$ it approaches the line $y=x$ from above, since $f(x)-x=-\dfrac{6}{x-1}>0$ there. On the right of $x=1$ the function is increasing, comes from $-\infty$, crosses the axis at $(3,0)$ and approaches $y=x$ from below as $x\to+\infty$ since $f(x)-x<0$. The curve is shown in the figure below.",
          fig="courbe_f"),
    ]))

    # ---- Exercice 10 : recurrence relations and complex transformation (14) ----
    ex.append(E("10", G, 14, r"A sequence is defined by $u_{1}=1$ and $u_{n+1}=2u_{n}+3$ for $n\ge1$.", [
        S("a", r"Calculate $u_{2}$, $u_{3}$ and $u_{4}$.",
          ["recurrence relations"], "faible", 3,
          [(r"You calculate $u_{2}=5$", 1), (r"You calculate $u_{3}=13$", 1), (r"You calculate $u_{4}=29$", 1)],
          r"A recurrence relation gives each term from the previous one: substitute the known term and repeat.",
          r"$u_{2}=2(1)+3=5$, $u_{3}=2(5)+3=13$, $u_{4}=2(13)+3=29$.",
          ans=r"$u_{2}=5$, $u_{3}=13$, $u_{4}=29$"),
        S("b", r"Find a formula for $u_{n}$ in terms of $n$.",
          ["recurrence relations"], "moyenne", 4,
          [(r"You find the constant solution $k=2k+3$, so $k=-3$", 1), (r"You write the general solution $u_{n}=A\times2^{n}-3$", 1),
           (r"You use $u_{1}=1$ to find $A=2$", 1), (r"You conclude $u_{n}=2^{n+1}-3$", 1)],
          r"For $u_{n+1}=au_{n}+b$ with $a\ne1$, the general solution is $u_{n}=A\,a^{n}+k$ where $k$ is the constant solution of $k=ak+b$; the first term fixes $A$.",
          r"A constant solution satisfies $k=2k+3$, so $k=-3$. The general solution is $u_{n}=A\times2^{n}-3$. With $u_{1}=1$: $1=2A-3$, so $A=2$ and $u_{n}=2\times2^{n}-3=2^{n+1}-3$. Check: $u_{4}=2^{5}-3=29$.",
          ans=r"$u_{n}=2^{n+1}-3$"),
        S("c", r"Find $\displaystyle\lim_{n\to\infty}\dfrac{u_{n}}{2^{n}}$.",
          ["limits of sequences"], "faible", 3,
          [(r"You write $\dfrac{u_{n}}{2^{n}}=2-\dfrac{3}{2^{n}}$", 1), (r"You state that $\dfrac{3}{2^{n}}\to0$", 1), (r"You conclude that the limit is $2$", 1)],
          r"To find the limit of a ratio, divide each term by the dominant power and use $a^{-n}\to0$ when $a>1$.",
          r"$\dfrac{u_{n}}{2^{n}}=\dfrac{2^{n+1}-3}{2^{n}}=2-\dfrac{3}{2^{n}}$. Since $2^{n}\to\infty$, $\dfrac{3}{2^{n}}\to0$ and the limit is $2$.",
          ans=r"$2$"),
        S("d", r"A transformation $T$ of the Argand diagram is given by $w=\dfrac{z+1}{z-1}$ for $z\ne1$. Find the images under $T$ of the points $z=i$ and $z=-1$.",
          ["complex transformations"], "moyenne", 2,
          [(r"You rationalise: the image of $i$ is $\dfrac{i+1}{i-1}=-i$", 1), (r"You find that the image of $-1$ is $0$", 1)],
          r"To find the image of a point, substitute its value into the transformation; to simplify a complex fraction, multiply numerator and denominator by the conjugate of the denominator.",
          r"For $z=i$: $w=\dfrac{1+i}{-1+i}=\dfrac{(1+i)(-1-i)}{(-1+i)(-1-i)}=\dfrac{-1-2i-i^{2}}{1+1}=\dfrac{-2i}{2}=-i$. For $z=-1$: $w=\dfrac{0}{-2}=0$.",
          ans=r"$-i$ and $0$"),
        S("e", r"Find the invariant points of $T$, that is the values of $z$ for which $w=z$.",
          ["complex transformations"], "elevee", 2,
          [(r"You write $z(z-1)=z+1$, that is $z^{2}-2z-1=0$", 1), (r"You obtain $z=1\pm\sqrt2$", 1)],
          r"An invariant point satisfies $w=z$: clear the denominator and solve the resulting polynomial equation.",
          r"$z=\dfrac{z+1}{z-1}$ gives $z^{2}-z=z+1$, so $z^{2}-2z-1=0$ and $z=\dfrac{2\pm\sqrt{8}}{2}=1\pm\sqrt2$. Both are real and different from $1$, so there are two invariant points.",
          ans=r"$z=1+\sqrt2$ and $z=1-\sqrt2$"),
    ]))

    return ex
