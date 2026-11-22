r"""Les 8 exercices de l'epreuve inedite GCE A Level Further Mathematics Paper 3 n.1 (100 marks, 2 h 30, tout obligatoire).

Structure mesuree sur les Paper 3 de 2025 et 2026 (8 exercices, 100 marks, mecanique puis statistiques) ; aucune donnee reprise d'un sujet reel ni du Paper 2
de la session. Chaque sous-question : bareme exact (`pts`), grille `crit` (somme = pts), rappel, resolution, reponse finale `ans` (recalculee par
verifier_reponses_furthermaths_p3.py). Chaines BRUTES. Numeros affiches : lettres a, b, c...
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_addmaths_p2_a import E, S  # noqa: E402,F401

G = ""


def exercices():
    ex = []

    # ---- Exercice 1 : systems of forces, moments and work (13) ----
    ex.append(E("1", G, 13, r"In this question forces are in newtons and distances in metres.", [
        S("a", r"Three forces $\mathbf F_{1}=(3,-2,1)$, $\mathbf F_{2}=(-1,4,2)$ and $\mathbf F_{3}=(2,1,-5)$ act on a particle. Find their resultant and its magnitude.",
          ["systems of forces"], "faible", 3,
          [(r"You add the components: $\mathbf R=(4,3,-2)$", 2), (r"You find $|\mathbf R|=\sqrt{29}\approx5.39\ \text{N}$", 1)],
          r"The resultant of several forces is their vector sum, found component by component; its magnitude is the square root of the sum of the squares of the components.",
          r"$\mathbf R=\mathbf F_{1}+\mathbf F_{2}+\mathbf F_{3}=(3-1+2,\ -2+4+1,\ 1+2-5)=(4,3,-2)$. Then $|\mathbf R|=\sqrt{16+9+4}=\sqrt{29}\approx5.39\ \text{N}$.",
          ans=r"$\mathbf R=(4,3,-2)\ \text{N}$ ; $|\mathbf R|=\sqrt{29}\approx5.39\ \text{N}$"),
        S("b", r"The force $\mathbf F=(2,-3,1)$ acts at the point $A$ with position vector $(1,2,-1)$. Find its vector moment about the origin $O$.",
          ["vector moment of a force"], "moyenne", 4,
          [(r"You write $\mathbf M_{O}=\mathbf r\times\mathbf F$ with $\mathbf r=(1,2,-1)$", 1), (r"You compute the first component $2\times1-(-1)(-3)=-1$", 1),
           (r"You compute the other components $-3$ and $-7$", 1), (r"You state $\mathbf M_{O}=(-1,-3,-7)\ \text{N m}$", 1)],
          r"The moment about a point of a force $\mathbf F$ acting at position $\mathbf r$ (measured from that point) is the vector product $\mathbf r\times\mathbf F$.",
          r"$\mathbf M_{O}=\mathbf r\times\mathbf F=\big(2\times1-(-1)(-3),\ (-1)(2)-1\times1,\ 1\times(-3)-2\times2\big)=(2-3,\ -2-1,\ -3-4)=(-1,-3,-7)\ \text{N m}$.",
          ans=r"$\mathbf M_{O}=(-1,-3,-7)\ \text{N m}$",
          piege=r"The order matters: $\mathbf F\times\mathbf r=-\mathbf r\times\mathbf F$, which would reverse the sense of the moment."),
        S("c", r"The point of application of $\mathbf F$ moves from $A(1,2,-1)$ to $B(4,0,2)$. Find the work done by $\mathbf F$.",
          ["work done by a force"], "faible", 3,
          [(r"You find the displacement $\overrightarrow{AB}=(3,-2,3)$", 1), (r"You write $W=\mathbf F\cdot\overrightarrow{AB}=6+6+3$", 1), (r"You obtain $W=15\ \text{J}$", 1)],
          r"The work done by a constant force is the scalar product of the force and the displacement of its point of application, $W=\mathbf F\cdot\mathbf d$.",
          r"$\overrightarrow{AB}=(4-1,\ 0-2,\ 2-(-1))=(3,-2,3)$. Then $W=(2,-3,1)\cdot(3,-2,3)=6+6+3=15\ \text{J}$.",
          ans=r"$15\ \text{J}$"),
        S("d", r"Find the vector moment of $\mathbf F$, acting at $A$, about the point $P(0,1,1)$, and verify that it is perpendicular to $\mathbf F$.",
          ["vector moment of a force"], "moyenne", 3,
          [(r"You find $\overrightarrow{PA}=(1,1,-2)$", 1), (r"You obtain $\overrightarrow{PA}\times\mathbf F=(-5,-5,-5)$", 1), (r"You show that the scalar product with $\mathbf F$ is $-10+15-5=0$", 1)],
          r"The moment about $P$ uses the vector from $P$ to the point of application. A vector product is always perpendicular to both of its factors, which gives a quick check.",
          r"$\overrightarrow{PA}=(1-0,\ 2-1,\ -1-1)=(1,1,-2)$. Then $\overrightarrow{PA}\times\mathbf F=\big(1\times1-(-2)(-3),\ (-2)(2)-1\times1,\ 1\times(-3)-1\times2\big)=(-5,-5,-5)$. Check: $(-5,-5,-5)\cdot(2,-3,1)=-10+15-5=0$, so the moment is perpendicular to $\mathbf F$.",
          ans=r"$(-5,-5,-5)\ \text{N m}$"),
    ]))

    # ---- Exercice 2 : numerical methods (11) ----
    ex.append(E("2", G, 11, r"", [
        S("a", r"Given that $\dfrac{dy}{dx}=x+y^{2}$ and $y=1$ when $x=0$, use Euler's method with a step length $h=0.1$ to estimate $y$ when $x=0.2$.",
          ["numerical solution of differential equations"], "faible", 4,
          [(r"You state the formula $y_{n+1}=y_{n}+hf(x_{n},y_{n})$", 1), (r"You obtain $y_{1}=1+0.1(0+1)=1.1$", 1), (r"You calculate $f(0.1,1.1)=0.1+1.21=1.31$", 1), (r"You obtain $y_{2}=1.1+0.131=1.231$", 1)],
          r"Euler's method replaces the curve by its tangent over each step: $y_{n+1}=y_{n}+h\,f(x_{n},y_{n})$ with $x_{n+1}=x_{n}+h$.",
          r"With $f(x,y)=x+y^{2}$: $y_{1}=y_{0}+hf(0,1)=1+0.1(1)=1.1$ at $x=0.1$. Then $f(0.1,1.1)=0.1+1.21=1.31$ and $y_{2}=1.1+0.1(1.31)=1.231$ at $x=0.2$.",
          ans=r"$y(0.2)\approx1.231$"),
        S("b", r"Use the improved Euler method with $h=0.1$ to obtain a better estimate of $y$ when $x=0.1$ for the same differential equation and initial condition.",
          ["numerical solution of differential equations"], "moyenne", 3,
          [(r"You find the predictor $y_{1}^{*}=1.1$", 1), (r"You apply the corrector $y_{1}=1+0.05\big(1+f(0.1,1.1)\big)$", 1), (r"You obtain $y_{1}=1.1155$", 1)],
          r"The improved Euler method first predicts $y_{n+1}^{*}=y_{n}+hf(x_{n},y_{n})$, then corrects with the average slope: $y_{n+1}=y_{n}+\tfrac h2\big[f(x_{n},y_{n})+f(x_{n+1},y_{n+1}^{*})\big]$.",
          r"The predictor is $y_{1}^{*}=1.1$. Then $f(0,1)=1$ and $f(0.1,1.1)=1.31$, so $y_{1}=1+\tfrac{0.1}{2}(1+1.31)=1+0.05\times2.31=1.1155$.",
          ans=r"$y(0.1)\approx1.1155$"),
        S("c", r"Use Simpson's rule with four strips to estimate $\displaystyle\int_{0}^{1}\dfrac{dx}{1+x^{2}}$ to $4$ decimal places, and hence estimate $\pi$.",
          ["numerical integration"], "moyenne", 4,
          [(r"You tabulate $f(x)=\dfrac{1}{1+x^{2}}$ at $x=0,0.25,0.5,0.75,1$", 1), (r"You apply $\tfrac h3\big[f_{0}+f_{4}+4(f_{1}+f_{3})+2f_{2}\big]$ with $h=0.25$", 1),
           (r"You obtain $0.7854$ to $4$ decimal places", 1), (r"You deduce $\pi\approx4\times0.78539=3.1416$", 1)],
          r"Simpson's rule with an even number $n$ of strips of width $h$ is $\dfrac h3\big[f_{0}+f_{n}+4(f_{1}+f_{3}+\dots)+2(f_{2}+f_{4}+\dots)\big]$.",
          r"With $h=0.25$: $f(0)=1$, $f(0.25)=0.941176$, $f(0.5)=0.8$, $f(0.75)=0.64$, $f(1)=0.5$. The estimate is $\tfrac{0.25}{3}\big[1+0.5+4(0.941176+0.64)+2(0.8)\big]=\tfrac{0.25}{3}\times9.424706=0.78539\approx0.7854$. Since $\displaystyle\int_{0}^{1}\dfrac{dx}{1+x^{2}}=\tfrac{\pi}{4}$, $\pi\approx4\times0.78539=3.1416$.",
          ans=r"$0.7854$ ; $\pi\approx3.1416$",
          conseil=r"Write the table of values with at least six decimal places before applying the formula; rounding early costs the fourth decimal place."),
    ]))

    # ---- Exercice 3 : harmonic motion (12) ----
    ex.append(E("3", G, 12, r"", [
        S("a", r"A particle $P$ moves on a straight line with simple harmonic motion about a fixed point $O$, with amplitude $0.4\ \text{m}$ and angular frequency $3\ \text{rad s}^{-1}$. Find the maximum speed of $P$, its maximum acceleration, and its speed when it is $0.2\ \text{m}$ from $O$.",
          ["simple harmonic motion of a particle"], "faible", 4,
          [(r"You find the maximum speed $A\omega=1.2\ \text{m s}^{-1}$", 1), (r"You find the maximum acceleration $A\omega^{2}=3.6\ \text{m s}^{-2}$", 1),
           (r"You use $v^{2}=\omega^{2}(A^{2}-x^{2})$ with $x=0.2$", 1), (r"You obtain $v=3\sqrt{0.12}\approx1.04\ \text{m s}^{-1}$", 1)],
          r"For simple harmonic motion $\ddot x=-\omega^{2}x$ with amplitude $A$: $v^{2}=\omega^{2}(A^{2}-x^{2})$, the speed is greatest at the centre, $A\omega$, and the acceleration is greatest at the ends, $A\omega^{2}$.",
          r"Maximum speed: $A\omega=0.4\times3=1.2\ \text{m s}^{-1}$. Maximum acceleration: $A\omega^{2}=0.4\times9=3.6\ \text{m s}^{-2}$. At $x=0.2$: $v^{2}=9(0.16-0.04)=1.08$, so $v=\sqrt{1.08}=3\sqrt{0.12}\approx1.04\ \text{m s}^{-1}$.",
          ans=r"$1.2\ \text{m s}^{-1}$ ; $3.6\ \text{m s}^{-2}$ ; $1.04\ \text{m s}^{-1}$"),
        S("b", r"Find the time taken by $P$ to travel directly from $O$ to the point $0.2\ \text{m}$ from $O$.",
          ["simple harmonic motion of a particle"], "moyenne", 3,
          [(r"You write $x=0.4\sin3t$ for motion starting at $O$", 1), (r"You solve $\sin3t=\tfrac12$ to get $3t=\tfrac{\pi}{6}$", 1), (r"You obtain $t=\tfrac{\pi}{18}\approx0.175\ \text{s}$", 1)],
          r"When timing is measured from the centre, the displacement is $x=A\sin\omega t$; solve for the first positive $t$ at which $x$ takes the required value.",
          r"Taking $t=0$ at $O$: $x=0.4\sin3t$. Then $0.2=0.4\sin3t$, so $\sin3t=\tfrac12$ and, for the first time, $3t=\tfrac{\pi}{6}$. Hence $t=\tfrac{\pi}{18}\approx0.175\ \text{s}$.",
          ans=r"$\tfrac{\pi}{18}\approx0.175\ \text{s}$"),
        S("c", r"The displacement $x$ metres of another particle satisfies $\dfrac{d^{2}x}{dt^{2}}+4\dfrac{dx}{dt}+13x=0$, with $x=2$ and $\dfrac{dx}{dt}=0$ when $t=0$. Find $x$ in terms of $t$, say what kind of damping is present, and give the period of the oscillations.",
          ["damped harmonic motion"], "elevee", 5,
          [(r"You solve the auxiliary equation $m^{2}+4m+13=0$: $m=-2\pm3i$", 1), (r"You write $x=e^{-2t}(A\cos3t+B\sin3t)$", 1), (r"You use the conditions to find $A=2$ and $B=\tfrac43$", 1),
           (r"You state that the damping is light because the roots are complex", 1), (r"You give the period $\tfrac{2\pi}{3}\approx2.09\ \text{s}$", 1)],
          r"For $\ddot x+2k\dot x+n^{2}x=0$, complex roots $m=-k\pm i\omega$ (light damping) give $x=e^{-kt}(A\cos\omega t+B\sin\omega t)$, whose oscillations have period $\dfrac{2\pi}{\omega}$.",
          r"The auxiliary equation $m^{2}+4m+13=0$ has $m=\dfrac{-4\pm\sqrt{16-52}}{2}=-2\pm3i$, so $x=e^{-2t}(A\cos3t+B\sin3t)$. From $x(0)=2$: $A=2$. Differentiating, $\dot x=e^{-2t}\big[(-2A+3B)\cos3t+(-2B-3A)\sin3t\big]$, and $\dot x(0)=0$ gives $-4+3B=0$, so $B=\tfrac43$. Hence $x=e^{-2t}\left(2\cos3t+\tfrac43\sin3t\right)$. The roots are complex, so the damping is light: the particle oscillates with decreasing amplitude, with period $\tfrac{2\pi}{3}\approx2.09\ \text{s}$.",
          ans=r"$x=e^{-2t}\left(2\cos3t+\tfrac43\sin3t\right)$ ; light damping ; period $\tfrac{2\pi}{3}\ \text{s}$",
          piege=r"The factor $e^{-2t}$ must also be differentiated when the condition on $\dfrac{dx}{dt}$ is used: forgetting it gives $B=0$."),
    ]))

    # ---- Exercice 4 : motion in a resisting medium (12) ----
    ex.append(E("4", G, 12, r"A small stone of mass $0.2\ \text{kg}$ is released from rest and falls vertically through a viscous liquid. The resistance of the liquid is $0.08v$ newtons when the speed of the stone is $v\ \text{m s}^{-1}$. Take $g=9.8\ \text{m s}^{-2}$ and ignore any upthrust.", [
        S("a", r"Show that $\dfrac{dv}{dt}=9.8-0.4v$ and hence that $v=24.5\left(1-e^{-0.4t}\right)$, where $t$ seconds is the time since release.",
          ["motion in a resisting medium", "first order differential equations"], "moyenne", 4,
          [(r"You apply Newton's second law: $0.2\dfrac{dv}{dt}=0.2g-0.08v$", 1), (r"You simplify to $\dfrac{dv}{dt}=9.8-0.4v$", 1),
           (r"You separate the variables and integrate: $-\tfrac{1}{0.4}\ln(9.8-0.4v)=t+C$", 1), (r"You use $v=0$ at $t=0$ to obtain $v=24.5\left(1-e^{-0.4t}\right)$", 1)],
          r"Write Newton's second law along the direction of motion, then separate the variables of the resulting first order equation and use the initial condition to find the constant.",
          r"Taking downwards as positive: $0.2\dfrac{dv}{dt}=0.2\times9.8-0.08v$, so $\dfrac{dv}{dt}=9.8-0.4v$. Separating: $\displaystyle\int\dfrac{dv}{9.8-0.4v}=\int dt$, so $-\dfrac{1}{0.4}\ln(9.8-0.4v)=t+C$. At $t=0$, $v=0$: $C=-\dfrac{\ln9.8}{0.4}$. Therefore $\ln\dfrac{9.8-0.4v}{9.8}=-0.4t$, that is $9.8-0.4v=9.8e^{-0.4t}$ and $v=24.5\left(1-e^{-0.4t}\right)$.",
          piege=r"Keep the minus sign in front of the logarithm: the integral of $\dfrac{1}{9.8-0.4v}$ with respect to $v$ is $-\dfrac{1}{0.4}\ln(9.8-0.4v)$."),
        S("b", r"Find the terminal speed of the stone, and the time taken for its speed to reach half of the terminal speed.",
          ["motion in a resisting medium"], "faible", 4,
          [(r"You state the terminal speed $24.5\ \text{m s}^{-1}$ as $t\to\infty$ (or from $\dfrac{dv}{dt}=0$)", 1), (r"You write $12.25=24.5\left(1-e^{-0.4t}\right)$", 1),
           (r"You find $e^{-0.4t}=\tfrac12$", 1), (r"You obtain $t=\dfrac{\ln2}{0.4}\approx1.73\ \text{s}$", 1)],
          r"The terminal speed is reached when the acceleration is zero, or as $t\to\infty$ since $e^{-kt}\to0$; a given fraction of it is found by solving for $e^{-kt}$ and taking logarithms.",
          r"As $t\to\infty$, $e^{-0.4t}\to0$ and $v\to24.5\ \text{m s}^{-1}$; equivalently $\dfrac{dv}{dt}=0$ gives $v=\dfrac{9.8}{0.4}=24.5$. Half of this is $12.25$: $12.25=24.5\left(1-e^{-0.4t}\right)$, so $e^{-0.4t}=\tfrac12$ and $t=\dfrac{\ln2}{0.4}\approx1.73\ \text{s}$.",
          ans=r"$24.5\ \text{m s}^{-1}$ ; $\dfrac{\ln2}{0.4}\approx1.73\ \text{s}$"),
        S("c", r"Find the distance fallen by the stone in the time found in part (b).",
          ["motion in a resisting medium"], "moyenne", 4,
          [(r"You integrate $v$: $x=24.5\left(t+\dfrac{e^{-0.4t}}{0.4}\right)+C$", 1), (r"You use $x=0$ at $t=0$ to write $x=24.5\left(t+\dfrac{e^{-0.4t}-1}{0.4}\right)$", 1),
           (r"You substitute $t=\dfrac{\ln2}{0.4}$ and $e^{-0.4t}=\tfrac12$", 1), (r"You obtain $x\approx11.8\ \text{m}$", 1)],
          r"The distance travelled is the integral of the speed with respect to time, starting from the initial position.",
          r"$x=\displaystyle\int_{0}^{t}24.5\left(1-e^{-0.4s}\right)ds=24.5\left[s+\dfrac{e^{-0.4s}}{0.4}\right]_{0}^{t}=24.5\left(t+\dfrac{e^{-0.4t}-1}{0.4}\right)$. At $t=\dfrac{\ln2}{0.4}\approx1.7329$, $e^{-0.4t}=\tfrac12$, so $x=24.5\left(1.7329-1.25\right)=24.5\times0.4829\approx11.8\ \text{m}$.",
          ans=r"$\approx11.8\ \text{m}$"),
    ]))

    # ---- Exercice 5 : oblique impact (13) ----
    ex.append(E("5", G, 13, r"All the spheres in this question are smooth and the surfaces are smooth.", [
        S("a", r"A sphere strikes a fixed vertical wall with speed $10\ \text{m s}^{-1}$, its direction of motion making an angle of $60^{\circ}$ with the wall. The coefficient of restitution between the sphere and the wall is $0.6$. Find the speed of the sphere after the impact and the angle its direction makes with the wall.",
          ["oblique impact of smooth spheres", "coefficient of restitution"], "moyenne", 4,
          [(r"You resolve: component along the wall $10\cos60^{\circ}=5$, component normal to the wall $10\sin60^{\circ}=5\sqrt3$", 1), (r"You use the law of restitution: new normal component $0.6\times5\sqrt3=3\sqrt3$", 1),
           (r"You find the speed $\sqrt{25+27}=\sqrt{52}\approx7.21\ \text{m s}^{-1}$", 1), (r"You find the angle with the wall $\arctan\dfrac{3\sqrt3}{5}\approx46.1^{\circ}$", 1)],
          r"A smooth wall exerts an impulse only along its normal: the component of velocity parallel to the wall is unchanged, and the normal component is reversed and multiplied by the coefficient of restitution $e$.",
          r"Parallel to the wall the component is unchanged: $10\cos60^{\circ}=5\ \text{m s}^{-1}$. Normal to the wall the approach speed is $10\sin60^{\circ}=5\sqrt3$ and the speed of rebound is $0.6\times5\sqrt3=3\sqrt3\approx5.20$. The speed after impact is $\sqrt{5^{2}+(3\sqrt3)^{2}}=\sqrt{52}\approx7.21\ \text{m s}^{-1}$. The angle $\phi$ with the wall satisfies $\tan\phi=\dfrac{3\sqrt3}{5}$, so $\phi\approx46.1^{\circ}$.",
          ans=r"$\sqrt{52}\approx7.21\ \text{m s}^{-1}$ ; $46.1^{\circ}$ with the wall"),
        S("b", r"Two identical spheres $A$ and $B$, each of mass $0.5\ \text{kg}$, lie on a smooth horizontal table. $A$ moves with speed $8\ \text{m s}^{-1}$ and strikes $B$, which is at rest. At the instant of impact the direction of motion of $A$ makes an angle of $30^{\circ}$ with the line of centres. The coefficient of restitution between the spheres is $0.5$. Find the speed of $B$ after the impact and the speed of $A$ after the impact.",
          ["oblique impact of smooth spheres", "coefficient of restitution"], "elevee", 5,
          [(r"You resolve the velocity of $A$: $8\cos30^{\circ}=4\sqrt3$ along the line of centres and $8\sin30^{\circ}=4$ perpendicular to it", 1),
           (r"You apply conservation of momentum along the line of centres: $v_{A}+v_{B}=4\sqrt3$", 1), (r"You apply the law of restitution: $v_{B}-v_{A}=0.5\times4\sqrt3$", 1),
           (r"You solve: $v_{B}=3\sqrt3\approx5.20\ \text{m s}^{-1}$ and $v_{A}=\sqrt3$ along the line of centres", 1), (r"You keep the perpendicular component of $A$ unchanged at $4$ and find the speed of $A$: $\sqrt{19}\approx4.36\ \text{m s}^{-1}$", 1)],
          r"In an oblique impact of smooth spheres the impulse acts along the line of centres only: momentum is conserved along that line, Newton's law of restitution links the speeds along it, and each sphere keeps its component perpendicular to it.",
          r"Along the line of centres $A$ approaches with $4\sqrt3$ and $B$ is at rest. Conservation of momentum (equal masses) gives $v_{A}+v_{B}=4\sqrt3$. The law of restitution gives $v_{B}-v_{A}=0.5\times4\sqrt3=2\sqrt3$. Adding: $2v_{B}=6\sqrt3$, so $v_{B}=3\sqrt3\approx5.20\ \text{m s}^{-1}$, and $v_{A}=\sqrt3$ along the line of centres. $B$ has no perpendicular component, so its speed is $3\sqrt3\approx5.20\ \text{m s}^{-1}$. $A$ keeps its perpendicular component $4\ \text{m s}^{-1}$, so its speed after impact is $\sqrt{(\sqrt3)^{2}+4^{2}}=\sqrt{19}\approx4.36\ \text{m s}^{-1}$.",
          ans=r"$B$: $3\sqrt3\approx5.20\ \text{m s}^{-1}$ ; $A$: $\sqrt{19}\approx4.36\ \text{m s}^{-1}$",
          piege=r"Restitution applies to the components along the line of centres only; applying it to the full speeds gives wrong values."),
        S("c", r"Find the kinetic energy lost in the collision between $A$ and $B$.",
          ["oblique impact of smooth spheres"], "moyenne", 4,
          [(r"You find the initial kinetic energy $\tfrac12(0.5)(8^{2})=16\ \text{J}$", 1), (r"You find the final kinetic energy of $A$: $\tfrac12(0.5)(19)=4.75\ \text{J}$", 1),
           (r"You find the final kinetic energy of $B$: $\tfrac12(0.5)(27)=6.75\ \text{J}$", 1), (r"You obtain the loss $16-11.5=4.5\ \text{J}$", 1)],
          r"The kinetic energy lost is the kinetic energy of the system before the impact minus the kinetic energy afterwards, each computed from the full speeds.",
          r"Before: $\tfrac12\times0.5\times8^{2}=16\ \text{J}$. After: $A$ has $\tfrac12\times0.5\times19=4.75\ \text{J}$ and $B$ has $\tfrac12\times0.5\times27=6.75\ \text{J}$, a total of $11.5\ \text{J}$. The loss is $16-11.5=4.5\ \text{J}$.",
          ans=r"$4.5\ \text{J}$"),
    ]))

    # ---- Exercice 6 : motion in polar coordinates (12) ----
    ex.append(E("6", G, 12, r"A particle $P$ moves in a plane so that, at time $t$ seconds, its polar coordinates are $r=4t$ metres and $\theta=t^{2}$ radians, relative to a fixed pole $O$ and initial line.", [
        S("a", r"Find the radial and transverse components of the velocity of $P$ when $t=1$, and its speed.",
          ["motion in polar coordinates", "radial and transverse acceleration"], "faible", 4,
          [(r"You write $v_{r}=\dot r=4$", 1), (r"You write $v_{\theta}=r\dot\theta=4t\times2t=8t^{2}$", 1), (r"You evaluate at $t=1$: $v_{r}=4$ and $v_{\theta}=8$", 1), (r"You find the speed $\sqrt{80}=4\sqrt5\approx8.94\ \text{m s}^{-1}$", 1)],
          r"In polar coordinates the velocity has radial component $\dot r$ and transverse component $r\dot\theta$; the speed is the square root of the sum of their squares.",
          r"$\dot r=4$, $\dot\theta=2t$, so $v_{r}=4$ and $v_{\theta}=r\dot\theta=4t\times2t=8t^{2}$. At $t=1$: $v_{r}=4\ \text{m s}^{-1}$ and $v_{\theta}=8\ \text{m s}^{-1}$. The speed is $\sqrt{16+64}=\sqrt{80}=4\sqrt5\approx8.94\ \text{m s}^{-1}$.",
          ans=r"$v_{r}=4$, $v_{\theta}=8$ ; speed $4\sqrt5\approx8.94\ \text{m s}^{-1}$"),
        S("b", r"Find the radial and transverse components of the acceleration of $P$ when $t=1$, and the magnitude of the acceleration.",
          ["radial and transverse acceleration", "motion in polar coordinates"], "moyenne", 5,
          [(r"You state $a_{r}=\ddot r-r\dot\theta^{2}$ and $a_{\theta}=r\ddot\theta+2\dot r\dot\theta$", 1), (r"You find $\ddot r=0$ and $\ddot\theta=2$", 1), (r"You obtain $a_{r}=-4t\times4t^{2}=-16t^{3}=-16$ at $t=1$", 1),
           (r"You obtain $a_{\theta}=4t\times2+2\times4\times2t=24t=24$ at $t=1$", 1), (r"You find the magnitude $\sqrt{256+576}=\sqrt{832}\approx28.8\ \text{m s}^{-2}$", 1)],
          r"The radial and transverse components of the acceleration are $a_{r}=\ddot r-r\dot\theta^{2}$ and $a_{\theta}=r\ddot\theta+2\dot r\dot\theta=\dfrac1r\dfrac{d}{dt}\left(r^{2}\dot\theta\right)$.",
          r"With $r=4t$, $\dot r=4$, $\ddot r=0$, $\dot\theta=2t$ and $\ddot\theta=2$: $a_{r}=0-4t(2t)^{2}=-16t^{3}$ and $a_{\theta}=4t\times2+2\times4\times2t=24t$. At $t=1$: $a_{r}=-16\ \text{m s}^{-2}$ and $a_{\theta}=24\ \text{m s}^{-2}$. The magnitude is $\sqrt{16^{2}+24^{2}}=\sqrt{832}\approx28.8\ \text{m s}^{-2}$.",
          ans=r"$a_{r}=-16$, $a_{\theta}=24$ ; magnitude $\sqrt{832}\approx28.8\ \text{m s}^{-2}$",
          piege=r"The term $-r\dot\theta^{2}$ is part of the radial acceleration even when $\ddot r=0$: the particle is not moving in a straight line."),
        S("c", r"Find the angle between the velocity of $P$ and the radius vector $OP$ when $t=1$.",
          ["motion in polar coordinates"], "faible", 3,
          [(r"You state that the angle $\psi$ satisfies $\tan\psi=\dfrac{v_{\theta}}{v_{r}}$", 1), (r"You calculate $\tan\psi=\dfrac84=2$", 1), (r"You obtain $\psi\approx63.4^{\circ}$", 1)],
          r"The velocity makes an angle $\psi$ with the radius vector where $\tan\psi=\dfrac{\text{transverse component}}{\text{radial component}}$.",
          r"At $t=1$, $v_{r}=4$ and $v_{\theta}=8$, so $\tan\psi=2$ and $\psi=\arctan2\approx63.4^{\circ}$.",
          ans=r"$63.4^{\circ}$"),
    ]))

    # ---- Exercice 7 : moments of inertia and the compound pendulum (12) ----
    ex.append(E("7", G, 12, r"A uniform rod $AB$ has mass $0.9\ \text{kg}$ and length $1\ \text{m}$. Take $g=9.8\ \text{m s}^{-2}$.", [
        S("a", r"Given that the moment of inertia of the rod about a perpendicular axis through its centre is $\tfrac{1}{12}Ml^{2}$, use the parallel axes theorem to find its moment of inertia about a perpendicular axis through $A$.",
          ["moments of inertia", "parallel axes theorem"], "faible", 3,
          [(r"You find $I_{G}=\tfrac{1}{12}(0.9)(1)^{2}=0.075\ \text{kg m}^{2}$", 1), (r"You apply $I_{A}=I_{G}+Mh^{2}$ with $h=0.5$", 1), (r"You obtain $I_{A}=0.3\ \text{kg m}^{2}$", 1)],
          r"The parallel axes theorem states that $I=I_{G}+Md^{2}$, where $I_{G}$ is the moment of inertia about the parallel axis through the centre of mass and $d$ is the distance between the two axes.",
          r"$I_{G}=\tfrac{1}{12}\times0.9\times1^{2}=0.075\ \text{kg m}^{2}$. The axis through $A$ is at distance $0.5\ \text{m}$ from the centre, so $I_{A}=0.075+0.9\times0.5^{2}=0.075+0.225=0.3\ \text{kg m}^{2}$.",
          ans=r"$0.3\ \text{kg m}^{2}$"),
        S("b", r"The rod can swing freely in a vertical plane about a smooth horizontal axis through $A$. Find the period of small oscillations of the rod.",
          ["compound pendulum"], "moyenne", 4,
          [(r"You write the equation of motion $I_{A}\ddot\theta=-Mgh\sin\theta$ with $h=0.5$", 1), (r"You use $\sin\theta\approx\theta$ to obtain simple harmonic motion with $\omega^{2}=\dfrac{Mgh}{I_{A}}$", 1),
           (r"You calculate $\omega^{2}=\dfrac{0.9\times9.8\times0.5}{0.3}=14.7$", 1), (r"You obtain $T=\dfrac{2\pi}{\omega}\approx1.64\ \text{s}$", 1)],
          r"For a rigid body of mass $M$ swinging about a horizontal axis with moment of inertia $I$ about that axis, with its centre of mass at distance $h$ from the axis, small oscillations have $\omega^{2}=\dfrac{Mgh}{I}$ and period $2\pi\sqrt{\dfrac{I}{Mgh}}$.",
          r"The torque of the weight about $A$ gives $I_{A}\ddot\theta=-Mgh\sin\theta$ with $h=0.5\ \text{m}$. For small angles $\sin\theta\approx\theta$, so $\ddot\theta=-\omega^{2}\theta$ with $\omega^{2}=\dfrac{0.9\times9.8\times0.5}{0.3}=14.7$. The period is $T=\dfrac{2\pi}{\sqrt{14.7}}\approx1.64\ \text{s}$.",
          ans=r"$T\approx1.64\ \text{s}$"),
        S("c", r"A particle of mass $0.3\ \text{kg}$ is now attached to the rod at $B$. Find the new period of small oscillations about the axis through $A$.",
          ["compound pendulum", "moments of inertia"], "elevee", 5,
          [(r"You find the new moment of inertia $0.3+0.3\times1^{2}=0.6\ \text{kg m}^{2}$", 1), (r"You find the total mass $1.2\ \text{kg}$", 1), (r"You find the distance of the centre of mass from $A$: $\dfrac{0.9\times0.5+0.3\times1}{1.2}=0.625\ \text{m}$", 1),
           (r"You write $\omega^{2}=\dfrac{1.2\times9.8\times0.625}{0.6}=12.25$", 1), (r"You obtain $T=\dfrac{2\pi}{3.5}=\dfrac{4\pi}{7}\approx1.80\ \text{s}$", 1)],
          r"For a composite body add the moments of inertia about the same axis, add the masses, and locate the centre of mass with the weighted mean of the positions before applying $\omega^{2}=\dfrac{Mgh}{I}$.",
          r"The particle contributes $0.3\times1^{2}=0.3\ \text{kg m}^{2}$, so $I=0.3+0.3=0.6\ \text{kg m}^{2}$. The total mass is $1.2\ \text{kg}$ and the centre of mass is at $h=\dfrac{0.9\times0.5+0.3\times1}{1.2}=\dfrac{0.75}{1.2}=0.625\ \text{m}$ from $A$. Then $\omega^{2}=\dfrac{1.2\times9.8\times0.625}{0.6}=12.25$, so $\omega=3.5$ and $T=\dfrac{2\pi}{3.5}=\dfrac{4\pi}{7}\approx1.80\ \text{s}$.",
          ans=r"$\dfrac{4\pi}{7}\approx1.80\ \text{s}$",
          piege=r"Do not use the distance $1\ \text{m}$ of the particle as $h$: $h$ is the distance of the centre of mass of the whole system from the axis."),
    ]))

    # ---- Exercice 8 : probability distributions (15) ----
    ex.append(E("8", G, 15, r"", [
        S("a", r"The discrete random variable $X$ takes the values $0,1,2,3,4$ with $P(X=x)=k(x+1)$. Find the value of $k$.",
          ["probability distributions"], "faible", 3,
          [(r"You write $\sum P(X=x)=1$", 1), (r"You sum: $k(1+2+3+4+5)=15k$", 1), (r"You obtain $k=\tfrac{1}{15}$", 1)],
          r"The probabilities of all the possible values of a discrete random variable add up to $1$.",
          r"$k(1+2+3+4+5)=15k=1$, so $k=\tfrac{1}{15}$.",
          ans=r"$k=\tfrac{1}{15}$"),
        S("b", r"Find $E(X)$.",
          ["expectation and variance"], "faible", 3,
          [(r"You write $E(X)=\sum xP(X=x)$", 1), (r"You compute $\dfrac{0+2+6+12+20}{15}$", 1), (r"You obtain $E(X)=\tfrac{8}{3}$", 1)],
          r"The expectation of a discrete random variable is $E(X)=\sum x\,P(X=x)$.",
          r"$E(X)=\dfrac{1}{15}\left(0\times1+1\times2+2\times3+3\times4+4\times5\right)=\dfrac{40}{15}=\dfrac83$.",
          ans=r"$E(X)=\tfrac83$"),
        S("c", r"Find $\mathrm{Var}(X)$.",
          ["expectation and variance"], "moyenne", 3,
          [(r"You use $\mathrm{Var}(X)=E(X^{2})-[E(X)]^{2}$", 1), (r"You compute $E(X^{2})=\dfrac{0+2+12+36+80}{15}=\tfrac{26}{3}$", 1), (r"You obtain $\mathrm{Var}(X)=\tfrac{26}{3}-\tfrac{64}{9}=\tfrac{14}{9}$", 1)],
          r"The variance is $\mathrm{Var}(X)=E(X^{2})-[E(X)]^{2}$ where $E(X^{2})=\sum x^{2}P(X=x)$.",
          r"$E(X^{2})=\dfrac{1}{15}\left(0+1\times2+4\times3+9\times4+16\times5\right)=\dfrac{130}{15}=\dfrac{26}{3}$. Then $\mathrm{Var}(X)=\dfrac{26}{3}-\left(\dfrac83\right)^{2}=\dfrac{78-64}{9}=\dfrac{14}{9}$.",
          ans=r"$\mathrm{Var}(X)=\tfrac{14}{9}$"),
        S("d", r"The mass of rice in a bag filled by a machine is normally distributed with mean $50\ \text{kg}$ and standard deviation $0.8\ \text{kg}$. Find the probability that a bag chosen at random contains less than $49\ \text{kg}$.",
          ["normal distribution"], "moyenne", 3,
          [(r"You standardise: $z=\dfrac{49-50}{0.8}=-1.25$", 1), (r"You write $P(Z<-1.25)=1-\Phi(1.25)$", 1), (r"You obtain $1-0.8944=0.1056$", 1)],
          r"To find a probability for a normal variable $X\sim N(\mu,\sigma^{2})$, standardise with $Z=\dfrac{X-\mu}{\sigma}$ and use the table of $\Phi$, using $\Phi(-z)=1-\Phi(z)$ for a negative value.",
          r"$z=\dfrac{49-50}{0.8}=-1.25$. $P(X<49)=\Phi(-1.25)=1-\Phi(1.25)=1-0.8944=0.1056$.",
          ans=r"$0.1056$"),
        S("e", r"A farmer packs cocoa beans in bags, and each bag independently has a probability $0.1$ of being underweight. Find the probability that, in a sample of $10$ bags, at least $2$ are underweight.",
          ["probability distributions"], "moyenne", 3,
          [(r"You identify the binomial distribution $B(10,0.1)$", 1), (r"You write $P(X\ge2)=1-P(X=0)-P(X=1)$ with $0.9^{10}=0.3487$ and $10(0.1)(0.9)^{9}=0.3874$", 1), (r"You obtain $0.2639$", 1)],
          r"For $n$ independent trials with the same probability $p$ of success, the number of successes is binomial with $P(X=r)=\dbinom{n}{r}p^{r}(1-p)^{n-r}$; for at least a given number use the complement.",
          r"Let $X$ be the number of underweight bags, so $X\sim B(10,0.1)$. $P(X=0)=0.9^{10}=0.3487$ and $P(X=1)=10\times0.1\times0.9^{9}=0.3874$. Then $P(X\ge2)=1-0.3487-0.3874=0.2639$.",
          ans=r"$0.2639$"),
    ]))

    return ex
