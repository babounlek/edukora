r"""Les 8 exercices de l'epreuve inedite GCE A Level Pure Mathematics with Mechanics Paper 3 n.1 (100 marks, 3 h, tout obligatoire).

Structure mesuree sur les Paper 3 de 2024, 2025 et 2026 (8 exercices de 2 a 6 sous-questions courtes, mecanique seule) ; aucune donnee, aucun contexte
ni jeu de nombres repris d'un sujet reel. Chaque sous-question : bareme exact (`pts`), grille `crit` (somme = pts), rappel, resolution, reponse finale
`ans` (recalculee par verifier_reponses_pm_mechanics_p3.py). Chaines BRUTES. Numeros affiches : lettres a, b, c...
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_addmaths_p2_a import E, S  # noqa: E402,F401

G = ""


def exercices():
    ex = []

    # ---- Exercice 1 : vector kinematics (13) ----
    ex.append(E("1", G, 13, r"In this question $\mathbf i$ and $\mathbf j$ are unit vectors in the directions of the $x$-axis and the $y$-axis, distances are in metres and times are in seconds. Position vectors are measured from a fixed origin $O$. Take $g=9.8\ \text{m s}^{-2}$ throughout the paper where a value of $g$ is needed.", [
        S("a", r"A drone $P$ is flown over a sports ground in Douala. At time $t$ seconds its position vector is $\mathbf r=\left[(t^{3}-6t)\,\mathbf i+(4t-t^{2})\,\mathbf j\right]\ \text{m}$, for $t\ge0$. Find the velocity and the acceleration of $P$ when $t=2$, and the speed of $P$ at that instant.",
          ["vector kinematics mechanics"], "faible", 3,
          [(r"You differentiate to obtain $\mathbf v=(3t^{2}-6)\,\mathbf i+(4-2t)\,\mathbf j$", 1), (r"You differentiate again to obtain $\mathbf a=6t\,\mathbf i-2\,\mathbf j$", 1),
           (r"You evaluate at $t=2$: $\mathbf v=6\,\mathbf i$, $\mathbf a=12\,\mathbf i-2\,\mathbf j$, and the speed is $6\ \text{m s}^{-1}$", 1)],
          r"The velocity is the derivative of the position vector and the acceleration is the derivative of the velocity, each taken component by component; the speed is the magnitude of the velocity.",
          r"$\mathbf v=\dfrac{d\mathbf r}{dt}=(3t^{2}-6)\,\mathbf i+(4-2t)\,\mathbf j$ and $\mathbf a=\dfrac{d\mathbf v}{dt}=6t\,\mathbf i-2\,\mathbf j$. When $t=2$: $\mathbf v=(12-6)\,\mathbf i+(4-4)\,\mathbf j=6\,\mathbf i$ and $\mathbf a=12\,\mathbf i-2\,\mathbf j$. The speed is $|\mathbf v|=6\ \text{m s}^{-1}$.",
          ans=r"$\mathbf v=6\,\mathbf i\ \text{m s}^{-1}$ ; $\mathbf a=(12\,\mathbf i-2\,\mathbf j)\ \text{m s}^{-2}$ ; speed $6\ \text{m s}^{-1}$"),
        S("b", r"Find the value of $t$ for which $P$ is moving parallel to $\mathbf j$, and find the speed of $P$ at that time.",
          ["vector kinematics mechanics"], "faible", 3,
          [(r"You set the $\mathbf i$ component of the velocity to zero: $3t^{2}-6=0$", 1), (r"You obtain $t=\sqrt2\approx1.41\ \text{s}$", 1), (r"You find the speed $4-2\sqrt2\approx1.17\ \text{m s}^{-1}$", 1)],
          r"A particle moves parallel to a given axis when the component of its velocity in the perpendicular direction is zero.",
          r"$P$ moves parallel to $\mathbf j$ when the $\mathbf i$ component of $\mathbf v$ vanishes: $3t^{2}-6=0$, so $t^{2}=2$ and $t=\sqrt2\approx1.41\ \text{s}$ (the negative root is rejected). Then $\mathbf v=(4-2\sqrt2)\,\mathbf j$, and the speed is $4-2\sqrt2\approx1.17\ \text{m s}^{-1}$.",
          ans=r"$t=\sqrt2\approx1.41\ \text{s}$ ; speed $4-2\sqrt2\approx1.17\ \text{m s}^{-1}$"),
        S("c", r"A boat $B$ on the Wouri river has acceleration $\left(2t\,\mathbf i-3\,\mathbf j\right)\ \text{m s}^{-2}$. When $t=0$ the boat is at the point with position vector $10\,\mathbf j\ \text{m}$ and has velocity $\left(3\,\mathbf i+6\,\mathbf j\right)\ \text{m s}^{-1}$. Find the velocity of $B$ at time $t$ and its position vector when $t=3$.",
          ["vector kinematics mechanics"], "moyenne", 4,
          [(r"You integrate the acceleration and use the initial velocity: $\mathbf v=(t^{2}+3)\,\mathbf i+(6-3t)\,\mathbf j$", 1), (r"You integrate the velocity: $\mathbf r=\left(\tfrac{t^{3}}{3}+3t\right)\mathbf i+\left(6t-\tfrac32t^{2}\right)\mathbf j+\mathbf C$", 1),
           (r"You use the initial position to find $\mathbf C=10\,\mathbf j$", 1), (r"You evaluate at $t=3$: $\mathbf r=(18\,\mathbf i+14.5\,\mathbf j)\ \text{m}$", 1)],
          r"Integrating the acceleration gives the velocity and integrating the velocity gives the position vector; each integration introduces a constant vector, fixed by the initial conditions.",
          r"$\mathbf v=\displaystyle\int(2t\,\mathbf i-3\,\mathbf j)\,dt=t^{2}\,\mathbf i-3t\,\mathbf j+\mathbf C_{1}$. At $t=0$, $\mathbf v=3\,\mathbf i+6\,\mathbf j$, so $\mathbf C_{1}=3\,\mathbf i+6\,\mathbf j$ and $\mathbf v=(t^{2}+3)\,\mathbf i+(6-3t)\,\mathbf j$. Integrating again, $\mathbf r=\left(\tfrac{t^{3}}{3}+3t\right)\mathbf i+\left(6t-\tfrac32t^{2}\right)\mathbf j+\mathbf C_{2}$, and $\mathbf r=10\,\mathbf j$ at $t=0$ gives $\mathbf C_{2}=10\,\mathbf j$. When $t=3$: $\mathbf r=(9+9)\,\mathbf i+(18-13.5+10)\,\mathbf j=18\,\mathbf i+14.5\,\mathbf j$.",
          ans=r"$\mathbf v=\left[(t^{2}+3)\,\mathbf i+(6-3t)\,\mathbf j\right]\ \text{m s}^{-1}$ ; $\mathbf r=(18\,\mathbf i+14.5\,\mathbf j)\ \text{m}$ when $t=3$",
          piege=r"Each constant of integration is a vector: the initial velocity and the initial position vector both have two components."),
        S("d", r"Show that $B$ is moving parallel to $\mathbf i$ when $t=2$, and find the distance of $B$ from $O$ at that instant.",
          ["vector kinematics mechanics"], "faible", 3,
          [(r"You show that the $\mathbf j$ component of $\mathbf v$, $6-3t$, is zero at $t=2$", 1), (r"You find $\mathbf r(2)=\tfrac{26}{3}\,\mathbf i+16\,\mathbf j$", 1), (r"You obtain the distance $\sqrt{\tfrac{676}{9}+256}\approx18.2\ \text{m}$", 1)],
          r"The distance of a particle from the origin is the magnitude of its position vector at that instant.",
          r"When $t=2$, $\mathbf v=7\,\mathbf i+0\,\mathbf j$, so $B$ moves parallel to $\mathbf i$. Then $\mathbf r=\left(\tfrac{8}{3}+6\right)\mathbf i+(12-6+10)\,\mathbf j=\tfrac{26}{3}\,\mathbf i+16\,\mathbf j$. The distance from $O$ is $\sqrt{\left(\tfrac{26}{3}\right)^{2}+16^{2}}=\sqrt{\tfrac{676}{9}+256}\approx18.2\ \text{m}$.",
          ans=r"$\approx18.2\ \text{m}$"),
    ]))

    # ---- Exercice 2 : motion with constant acceleration (12) ----
    ex.append(E("2", G, 12, r"", [
        S("a", r"A taxi moving along a straight road with constant acceleration passes a kilometre post $A$ with speed $8\ \text{m s}^{-1}$ and passes a second post $B$, $150\ \text{m}$ further on, with speed $22\ \text{m s}^{-1}$. Find the acceleration of the taxi and the time it takes to travel from $A$ to $B$.",
          ["constant acceleration mechanics"], "faible", 3,
          [(r"You use $v^{2}=u^{2}+2as$ with $s=150$", 1), (r"You obtain $a=1.4\ \text{m s}^{-2}$", 1), (r"You use $v=u+at$ to obtain $t=10\ \text{s}$", 1)],
          r"For constant acceleration the five quantities $u$, $v$, $a$, $s$ and $t$ are linked by $v=u+at$, $s=\tfrac12(u+v)t$, $v^{2}=u^{2}+2as$ and $s=ut+\tfrac12at^{2}$; choose the equation that contains the unknown and three known quantities.",
          r"$v^{2}=u^{2}+2as$ gives $22^{2}=8^{2}+2a(150)$, so $484-64=300a$ and $a=1.4\ \text{m s}^{-2}$. Then $v=u+at$ gives $22=8+1.4t$, so $t=\dfrac{14}{1.4}=10\ \text{s}$.",
          ans=r"$a=1.4\ \text{m s}^{-2}$ ; $t=10\ \text{s}$"),
        S("b", r"A bus starts from rest at a stop and accelerates uniformly at $0.8\ \text{m s}^{-2}$ for $15$ seconds. It then travels at constant speed for $60$ seconds and finally decelerates uniformly to rest in $10$ seconds. Sketch the speed-time graph of the journey and find the greatest speed, the total distance travelled and the average speed for the whole journey.",
          ["kinematics and motion graphs", "constant acceleration mechanics"], "faible", 4,
          [(r"You sketch a trapezium with times $0$, $15$, $75$ and $85$ seconds on the horizontal axis", 1), (r"You find the greatest speed $0.8\times15=12\ \text{m s}^{-1}$", 1),
           (r"You find the total distance as the area under the graph: $90+720+60=870\ \text{m}$", 1), (r"You find the average speed $\dfrac{870}{85}\approx10.2\ \text{m s}^{-1}$", 1)],
          r"On a speed-time graph the gradient gives the acceleration and the area under the graph gives the distance travelled; the average speed is the total distance divided by the total time.",
          r"The graph rises in a straight line from $(0,0)$ to $(15,12)$, stays level until $t=75$, then falls in a straight line to $(85,0)$. The greatest speed is $0.8\times15=12\ \text{m s}^{-1}$. The area is $\tfrac12\times15\times12+60\times12+\tfrac12\times10\times12=90+720+60=870\ \text{m}$. The total time is $15+60+10=85\ \text{s}$, so the average speed is $\dfrac{870}{85}\approx10.2\ \text{m s}^{-1}$.",
          ans=r"$12\ \text{m s}^{-1}$ ; $870\ \text{m}$ ; $\approx10.2\ \text{m s}^{-1}$"),
        S("c", r"A lorry passes a checkpoint $A$ on a straight road at a constant speed of $20\ \text{m s}^{-1}$. Eight seconds later a police motorcycle starts from rest at $A$, accelerates at $3\ \text{m s}^{-2}$ until it reaches a speed of $30\ \text{m s}^{-1}$, and then keeps that speed until it overtakes the lorry. Find the distance from $A$ at which the motorcycle overtakes the lorry.",
          ["constant acceleration mechanics", "kinematics and motion graphs"], "elevee", 5,
          [(r"You find that the motorcycle reaches $30\ \text{m s}^{-1}$ after $10\ \text{s}$, having travelled $150\ \text{m}$", 1), (r"You show that the lorry is still ahead at that moment ($20\times18=360\ \text{m}$ from $A$)", 1),
           (r"You write the distances $s$ seconds after the motorcycle starts: lorry $20(s+8)$, motorcycle $150+30(s-10)$", 1), (r"You equate and solve to obtain $s=31\ \text{s}$", 1), (r"You find the distance $780\ \text{m}$ from $A$", 1)],
          r"Measure every time from one instant, write the position of each vehicle as a function of that time, and equate the positions at the overtaking instant; check which phase of the motion the faster vehicle is in at that instant before choosing its formula.",
          r"The motorcycle reaches $30\ \text{m s}^{-1}$ after $\dfrac{30}{3}=10\ \text{s}$ and has then covered $\tfrac12\times3\times10^{2}=150\ \text{m}$. At that moment the lorry has travelled for $18\ \text{s}$, that is $20\times18=360\ \text{m}$, so the motorcycle has not yet caught it and the overtaking takes place in the constant speed phase. Let $s$ be the time in seconds since the motorcycle started ($s>10$). Lorry: $20(s+8)$. Motorcycle: $150+30(s-10)$. Equating, $20s+160=30s-150$, so $10s=310$ and $s=31\ \text{s}$. The distance from $A$ is $20\times39=780\ \text{m}$ (check: $150+30\times21=780\ \text{m}$).",
          ans=r"$780\ \text{m}$ from $A$",
          piege=r"Do not use $s=\tfrac12at^{2}$ for the whole motion of the motorcycle: it stops accelerating after $10\ \text{s}$."),
    ]))

    # ---- Exercice 3 : connected particles and friction (12) ----
    ex.append(E("3", G, 12, r"A box $A$ of mass $4\ \text{kg}$ rests on a rough horizontal table. It is attached to a bucket $B$ of mass $3\ \text{kg}$ by a light inextensible string which passes over a smooth pulley fixed at the edge of the table. The part of the string between $A$ and the pulley is horizontal, $B$ hangs freely at $1.5\ \text{m}$ above the floor, and the coefficient of friction between $A$ and the table is $0.2$. The system is released from rest with the string taut. Treat $A$ and $B$ as particles.", [
        S("a", r"Calculate the common acceleration of $A$ and $B$ and the force that the string exerts on each of them during the descent of $B$.",
          ["connected particles mechanics", "friction"], "moyenne", 5,
          [(r"You find the normal reaction $4g$ and the friction $0.2\times4\times9.8=7.84\ \text{N}$", 1), (r"You write Newton's second law for $A$: $T-7.84=4a$", 1), (r"You write Newton's second law for $B$: $3\times9.8-T=3a$", 1),
           (r"You solve to obtain $a=3.08\ \text{m s}^{-2}$", 1), (r"You obtain $T=20.16\ \text{N}$", 1)],
          r"Apply Newton's second law to each particle separately along its line of motion, with the same acceleration and the same tension in the two equations; the friction on a sliding body is $\mu R$ with $R$ found from the vertical equilibrium.",
          r"For $A$, $R=4g=39.2\ \text{N}$ and the friction is $F=0.2\times39.2=7.84\ \text{N}$, so $T-7.84=4a$. For $B$: $29.4-T=3a$. Adding the two equations, $29.4-7.84=7a$, so $a=\dfrac{21.56}{7}=3.08\ \text{m s}^{-2}$. Then $T=7.84+4\times3.08=20.16\ \text{N}$.",
          ans=r"$a=3.08\ \text{m s}^{-2}$ ; $T=20.16\ \text{N}$"),
        S("b", r"Find the speed of $B$ at the instant it reaches the floor.",
          ["connected particles mechanics"], "faible", 3,
          [(r"You use $v^{2}=u^{2}+2as$ with $u=0$, $a=3.08$ and $s=1.5$", 1), (r"You obtain $v^{2}=9.24$", 1), (r"You obtain $v\approx3.04\ \text{m s}^{-1}$", 1)],
          r"While the string is taut both particles have the same speed and the same constant acceleration, so the constant acceleration equations apply to $B$ over the distance it falls.",
          r"$v^{2}=0+2\times3.08\times1.5=9.24$, so $v=\sqrt{9.24}\approx3.04\ \text{m s}^{-1}$.",
          ans=r"$\approx3.04\ \text{m s}^{-1}$"),
        S("c", r"$B$ comes to rest on the floor without rebounding, and $A$ does not reach the pulley. Find the total distance travelled by $A$ from the instant of release until it comes to rest.",
          ["friction", "connected particles mechanics"], "moyenne", 4,
          [(r"You state that the string goes slack and $A$ decelerates at $\mu g=1.96\ \text{m s}^{-2}$", 1), (r"You use the speed of $A$ at that moment, $v^{2}=9.24$", 1),
           (r"You find the further distance $\dfrac{9.24}{2\times1.96}\approx2.36\ \text{m}$", 1), (r"You add the first $1.5\ \text{m}$ to obtain $\approx3.86\ \text{m}$", 1)],
          r"Once the hanging particle stops, the string slackens and the friction alone decelerates the other particle; treat the two stages of the motion separately and add the distances.",
          r"When $B$ stops, $A$ has speed $\sqrt{9.24}$ and has travelled $1.5\ \text{m}$. The string is now slack, so the only horizontal force on $A$ is the friction $7.84\ \text{N}$, giving a deceleration $\dfrac{7.84}{4}=1.96\ \text{m s}^{-2}$. Then $0=9.24-2\times1.96\,d$, so $d=\dfrac{9.24}{3.92}\approx2.36\ \text{m}$. The total distance is $1.5+2.357\approx3.86\ \text{m}$.",
          ans=r"$\approx3.86\ \text{m}$",
          piege=r"After $B$ lands the tension is zero: if the acceleration $3.08\ \text{m s}^{-2}$ is kept, $A$ appears to go on speeding up instead of slowing down."),
    ]))

    # ---- Exercice 4 : projectiles (12) ----
    ex.append(E("4", G, 12, r"A stone is thrown from a window $8.1\ \text{m}$ above level ground in Buea. It is projected with a speed of $20\ \text{m s}^{-1}$ at an angle $\alpha$ above the horizontal, where $\tan\alpha=\dfrac34$. The stone moves freely under gravity in a vertical plane, and air resistance is ignored.", [
        S("a", r"Find the time taken by the stone to reach the ground and the horizontal distance from the window at which it lands.",
          ["projectile motion mechanics"], "moyenne", 4,
          [(r"You find the components of the initial velocity: $16\ \text{m s}^{-1}$ horizontally and $12\ \text{m s}^{-1}$ vertically", 1), (r"You write $-8.1=12t-4.9t^{2}$", 1),
           (r"You solve $4.9t^{2}-12t-8.1=0$ and reject the negative root: $t=3\ \text{s}$", 1), (r"You obtain the horizontal distance $16\times3=48\ \text{m}$", 1)],
          r"Resolve the initial velocity into horizontal and vertical components, then treat the two directions separately: constant velocity horizontally and constant acceleration $g$ downwards vertically, with time linking them.",
          r"Since $\tan\alpha=\tfrac34$, $\sin\alpha=0.6$ and $\cos\alpha=0.8$, so the components are $20\cos\alpha=16$ and $20\sin\alpha=12$. Taking upwards as positive, the vertical displacement on reaching the ground is $-8.1$: $-8.1=12t-4.9t^{2}$, that is $4.9t^{2}-12t-8.1=0$. Then $t=\dfrac{12\pm\sqrt{144+158.76}}{9.8}=\dfrac{12\pm17.4}{9.8}$, so $t=3$ (the negative root is rejected). The horizontal distance is $16\times3=48\ \text{m}$.",
          ans=r"$t=3\ \text{s}$ ; $48\ \text{m}$"),
        S("b", r"Find the speed of the stone as it hits the ground, and the angle its direction of motion then makes with the horizontal.",
          ["projectile motion mechanics"], "faible", 4,
          [(r"You find the vertical component $12-9.8\times3=-17.4\ \text{m s}^{-1}$", 1), (r"You use the horizontal component $16\ \text{m s}^{-1}$ to write the speed $\sqrt{16^{2}+17.4^{2}}$", 1),
           (r"You obtain $\approx23.6\ \text{m s}^{-1}$", 1), (r"You obtain the angle $\arctan\dfrac{17.4}{16}\approx47.4^{\circ}$ below the horizontal", 1)],
          r"At any instant the speed is the magnitude of the vector made by the horizontal and vertical components of the velocity, and the angle with the horizontal is the inverse tangent of vertical over horizontal.",
          r"At $t=3$ the vertical component is $v_{y}=12-9.8\times3=-17.4\ \text{m s}^{-1}$ (downwards) and the horizontal component is $v_{x}=16\ \text{m s}^{-1}$. The speed is $\sqrt{16^{2}+17.4^{2}}=\sqrt{558.76}\approx23.6\ \text{m s}^{-1}$, and the stone is moving at $\arctan\dfrac{17.4}{16}\approx47.4^{\circ}$ below the horizontal.",
          ans=r"$\approx23.6\ \text{m s}^{-1}$ ; $\approx47.4^{\circ}$ below the horizontal"),
        S("c", r"A boundary wall $12\ \text{m}$ high stands on the level ground, $32\ \text{m}$ horizontally from the window and in the plane of the motion. Show that the stone passes over the wall and find the vertical distance by which it clears the top of the wall.",
          ["projectile motion mechanics"], "moyenne", 4,
          [(r"You find the time to travel $32\ \text{m}$ horizontally: $t=\dfrac{32}{16}=2\ \text{s}$", 1), (r"You write the height of the stone above the ground $8.1+12t-4.9t^{2}$", 1),
           (r"You obtain a height of $12.5\ \text{m}$ at $t=2$", 1), (r"You conclude that the stone clears the wall by $0.5\ \text{m}$", 1)],
          r"To test whether a projectile clears an obstacle, find the time at which it is at the horizontal distance of the obstacle, then compare the height of the projectile at that time with the height of the obstacle.",
          r"The stone is at the horizontal distance $32\ \text{m}$ when $16t=32$, that is $t=2\ \text{s}$. Its height above the ground is then $8.1+12\times2-4.9\times2^{2}=8.1+24-19.6=12.5\ \text{m}$. Since $12.5>12$, the stone passes over the wall, clearing the top by $0.5\ \text{m}$.",
          ans=r"it clears the wall by $0.5\ \text{m}$"),
    ]))

    # ---- Exercice 5 : momentum and impacts (13) ----
    ex.append(E("5", G, 13, r"Two smooth spheres $A$ and $B$, of masses $3\ \text{kg}$ and $2\ \text{kg}$ respectively, move on a smooth horizontal table along the same straight line, in the same direction, with $A$ behind $B$. Their speeds are $6\ \text{m s}^{-1}$ for $A$ and $2\ \text{m s}^{-1}$ for $B$. The spheres collide directly, and the coefficient of restitution between them is $0.5$.", [
        S("a", r"Find the speed of $A$ and the speed of $B$ just after they collide, and state whether $A$ is still moving in its original direction.",
          ["coefficient of restitution", "conservation of momentum mechanics"], "moyenne", 5,
          [(r"You state the conservation of momentum: $3\times6+2\times2=3v_{A}+2v_{B}$", 1), (r"You simplify to $3v_{A}+2v_{B}=22$", 1), (r"You write Newton's law of restitution: $v_{B}-v_{A}=0.5\times(6-2)=2$", 1),
           (r"You solve to obtain $v_{A}=3.6\ \text{m s}^{-1}$", 1), (r"You obtain $v_{B}=5.6\ \text{m s}^{-1}$", 1)],
          r"In a direct collision the total momentum is conserved, and Newton's law of restitution states that the speed of separation equals $e$ times the speed of approach; the two equations are solved together for the two final velocities.",
          r"Conservation of momentum: $3\times6+2\times2=3v_{A}+2v_{B}$, so $3v_{A}+2v_{B}=22$. Restitution: $v_{B}-v_{A}=0.5(6-2)=2$. Substituting $v_{B}=v_{A}+2$: $3v_{A}+2v_{A}+4=22$, so $v_{A}=3.6\ \text{m s}^{-1}$ and $v_{B}=5.6\ \text{m s}^{-1}$. Both spheres are still moving in the original direction.",
          ans=r"$v_{A}=3.6\ \text{m s}^{-1}$ ; $v_{B}=5.6\ \text{m s}^{-1}$ ; yes, $A$ keeps its original direction",
          piege=r"The speed of approach is $6-2=4$, not $6+2$: the spheres move in the same direction."),
        S("b", r"Calculate, in joules, the kinetic energy of the two spheres before they collide and the part of it that is lost at the impact.",
          ["kinetic energy loss in collisions"], "faible", 4,
          [(r"You find the kinetic energy before: $\tfrac12\times3\times6^{2}+\tfrac12\times2\times2^{2}=58\ \text{J}$", 1), (r"You find the kinetic energy of $A$ after: $\tfrac12\times3\times3.6^{2}=19.44\ \text{J}$", 1),
           (r"You find the kinetic energy of $B$ after: $\tfrac12\times2\times5.6^{2}=31.36\ \text{J}$", 1), (r"You obtain the loss $58-50.8=7.2\ \text{J}$", 1)],
          r"The kinetic energy lost in a collision is the total kinetic energy of the spheres before the impact minus the total afterwards, each found from $\tfrac12mv^{2}$.",
          r"Before: $\tfrac12\times3\times36+\tfrac12\times2\times4=54+4=58\ \text{J}$. After: $\tfrac12\times3\times3.6^{2}=19.44\ \text{J}$ for $A$ and $\tfrac12\times2\times5.6^{2}=31.36\ \text{J}$ for $B$, a total of $50.8\ \text{J}$. The loss is $58-50.8=7.2\ \text{J}$.",
          ans=r"$58\ \text{J}$ before ; $7.2\ \text{J}$ lost"),
        S("c", r"Sphere $B$ then strikes a fixed smooth vertical wall at right angles and rebounds with a speed of $2.8\ \text{m s}^{-1}$. Find the coefficient of restitution between $B$ and the wall, and the magnitude of the impulse exerted by the wall on $B$.",
          ["coefficient of restitution"], "faible", 4,
          [(r"You use $e=\dfrac{\text{speed of rebound}}{\text{speed of approach}}$ with the speed of approach $5.6\ \text{m s}^{-1}$", 1), (r"You obtain $e=0.5$", 1),
           (r"You write the impulse as the change of momentum: $2(5.6+2.8)$", 1), (r"You obtain $16.8\ \text{N s}$", 1)],
          r"For a collision with a fixed wall the coefficient of restitution is the speed of rebound divided by the speed of approach, and the impulse is the change in momentum, remembering that the velocity reverses.",
          r"The speed of approach is $5.6\ \text{m s}^{-1}$ and the speed of rebound is $2.8\ \text{m s}^{-1}$, so $e=\dfrac{2.8}{5.6}=0.5$. Taking the direction of the rebound as positive, the impulse is $I=2\times2.8-2\times(-5.6)=2\times8.4=16.8\ \text{N s}$, directed away from the wall.",
          ans=r"$e=0.5$ ; $16.8\ \text{N s}$",
          piege=r"The velocity changes sign at the wall: the change of momentum is $m(v+u)$, not $m(v-u)$, with $u$ and $v$ the two speeds."),
    ]))

    # ---- Exercice 6 : work, energy and power (12) ----
    ex.append(E("6", G, 12, r"A lorry of total mass $5000\ \text{kg}$, carrying cocoa from Kumba to Douala, has an engine working at a constant rate of $60\ \text{kW}$ when it is moving under power. The resistance to motion of the lorry is constant and equal to $2000\ \text{N}$ on every road in this question.", [
        S("a", r"Find the greatest speed of the lorry on a straight horizontal road, and its acceleration when its speed on that road is $15\ \text{m s}^{-1}$.",
          ["power of an engine", "motion of a vehicle with resistance"], "faible", 3,
          [(r"You use $P=Fv$ with $F=2000$ at the greatest speed: $v=\dfrac{60000}{2000}=30\ \text{m s}^{-1}$", 1), (r"You find the driving force at $15\ \text{m s}^{-1}$: $\dfrac{60000}{15}=4000\ \text{N}$", 1),
           (r"You apply Newton's second law: $a=\dfrac{4000-2000}{5000}=0.4\ \text{m s}^{-2}$", 1)],
          r"The power of an engine is the driving force times the speed, $P=Fv$; at the greatest speed the acceleration is zero so the driving force equals the resistance, and otherwise Newton's second law gives $F-R=ma$.",
          r"At the greatest speed $a=0$, so $F=R=2000\ \text{N}$ and $v=\dfrac{P}{F}=\dfrac{60000}{2000}=30\ \text{m s}^{-1}$. At $15\ \text{m s}^{-1}$ the driving force is $F=\dfrac{60000}{15}=4000\ \text{N}$ and $4000-2000=5000a$, so $a=0.4\ \text{m s}^{-2}$.",
          ans=r"$30\ \text{m s}^{-1}$ ; $0.4\ \text{m s}^{-2}$"),
        S("b", r"The lorry now climbs a straight road inclined at an angle $\theta$ to the horizontal, where $\sin\theta=\dfrac{1}{20}$. Find the power needed to climb at a constant speed of $12\ \text{m s}^{-1}$, and the greatest speed of the lorry up this road when the engine works at $60\ \text{kW}$.",
          ["power of an engine", "motion of a vehicle with resistance"], "moyenne", 4,
          [(r"You write the equilibrium along the slope: $F=2000+5000\times9.8\times\tfrac{1}{20}$", 1), (r"You obtain $F=4450\ \text{N}$", 1), (r"You obtain the power $4450\times12=53400\ \text{W}=53.4\ \text{kW}$", 1),
           (r"You obtain the greatest speed $\dfrac{60000}{4450}\approx13.5\ \text{m s}^{-1}$", 1)],
          r"On a slope the engine must also balance the component of the weight along the road, $mg\sin\theta$; at constant speed the driving force equals the resistance plus this component, and then $P=Fv$.",
          r"At constant speed $F=2000+mg\sin\theta=2000+5000\times9.8\times\tfrac{1}{20}=2000+2450=4450\ \text{N}$. The power needed at $12\ \text{m s}^{-1}$ is $4450\times12=53400\ \text{W}=53.4\ \text{kW}$. With $60\ \text{kW}$ the greatest speed corresponds to the same driving force $4450\ \text{N}$, so $v=\dfrac{60000}{4450}\approx13.5\ \text{m s}^{-1}$.",
          ans=r"$53.4\ \text{kW}$ ; $\approx13.5\ \text{m s}^{-1}$",
          piege=r"Do not forget the weight component $mg\sin\theta$ on the slope: using only the $2000\ \text{N}$ resistance gives the horizontal-road power."),
        S("c", r"The lorry is travelling up the same road at $12\ \text{m s}^{-1}$ when the engine is switched off. Use the work-energy principle to find how far the lorry travels up the road before it comes to rest.",
          ["work energy and power mechanics", "motion of a vehicle with resistance"], "faible", 3,
          [(r"You find the loss of kinetic energy $\tfrac12\times5000\times12^{2}=360000\ \text{J}$", 1), (r"You equate it to the work done against resistance and weight: $(2000+2450)d$", 1), (r"You obtain $d\approx80.9\ \text{m}$", 1)],
          r"The work-energy principle says that the change in kinetic energy equals the work done by the forces; with the engine off, the resistance and the weight component along the slope do negative work over the distance travelled.",
          r"The kinetic energy lost is $\tfrac12\times5000\times12^{2}=360000\ \text{J}$. The forces opposing the motion are the resistance $2000\ \text{N}$ and $mg\sin\theta=2450\ \text{N}$, so $360000=(2000+2450)\,d$ and $d=\dfrac{360000}{4450}\approx80.9\ \text{m}$.",
          ans=r"$\approx80.9\ \text{m}$"),
        S("d", r"Find the time taken by the lorry to come to rest after the engine is switched off.",
          ["motion of a vehicle with resistance"], "faible", 2,
          [(r"You find the deceleration $\dfrac{4450}{5000}=0.89\ \text{m s}^{-2}$", 1), (r"You obtain $t=\dfrac{12}{0.89}\approx13.5\ \text{s}$", 1)],
          r"With the engine off, the resultant force opposing the motion is constant, so the deceleration is constant and $v=u+at$ gives the time.",
          r"The deceleration is $a=\dfrac{2000+2450}{5000}=0.89\ \text{m s}^{-2}$. From $0=12-0.89t$, $t=\dfrac{12}{0.89}\approx13.5\ \text{s}$. Check with part (c): $d=\tfrac12\times12\times13.48\approx80.9\ \text{m}$.",
          ans=r"$\approx13.5\ \text{s}$"),
    ]))

    # ---- Exercice 7 : centre of mass and equilibrium (13) ----
    ex.append(E("7", G, 13, r"", [
        S("a", r"A uniform lamina is made from a rectangular sheet $OABC$ with $OA=12\ \text{cm}$ and $OC=8\ \text{cm}$ by cutting out a rectangle in the corner $B$, with sides of length $6\ \text{cm}$ along $BC$ and $4\ \text{cm}$ along $BA$. Find the distance of the centre of mass of the lamina from $OC$ and from $OA$.",
          ["centre of mass of composite bodies"], "moyenne", 4,
          [(r"You find the areas: whole sheet $96\ \text{cm}^{2}$, removed piece $24\ \text{cm}^{2}$, lamina $72\ \text{cm}^{2}$", 1), (r"You take moments about $OC$ using the centres $(6,4)$ and $(9,6)$: $72\bar x=96\times6-24\times9$", 1),
           (r"You obtain $\bar x=5\ \text{cm}$", 1), (r"You obtain $\bar y=\dfrac{96\times4-24\times6}{72}=\dfrac{10}{3}\approx3.33\ \text{cm}$", 1)],
          r"A composite lamina is treated as the whole shape minus the removed part, each with its weight proportional to its area at its own centre; the moment of the whole about an axis equals the sum of the moments of its parts, the removed part counting negatively.",
          r"Take $O$ as origin, $OA$ along the $x$-axis and $OC$ along the $y$-axis. The whole sheet has area $96$ and centre $(6,4)$; the removed rectangle $[6,12]\times[4,8]$ has area $24$ and centre $(9,6)$; the lamina has area $72$. Then $72\bar x=96\times6-24\times9=360$, so $\bar x=5\ \text{cm}$ from $OC$, and $72\bar y=96\times4-24\times6=240$, so $\bar y=\dfrac{10}{3}\approx3.33\ \text{cm}$ from $OA$.",
          ans=r"$5\ \text{cm}$ from $OC$ ; $\dfrac{10}{3}\approx3.33\ \text{cm}$ from $OA$",
          piege=r"The removed part has a negative weight in the moment equation: adding it instead of subtracting it gives the centre of mass of the wrong body."),
        S("b", r"The lamina is freely suspended from the corner $C$ and hangs in equilibrium. Find the angle between $CO$ and the vertical.",
          ["centre of mass of composite bodies", "equilibrium of rigid bodies"], "moyenne", 4,
          [(r"You locate $G$ at $5\ \text{cm}$ horizontally and $8-\tfrac{10}{3}=\tfrac{14}{3}\ \text{cm}$ vertically below $C$", 1), (r"You state that $CG$ is vertical in equilibrium", 1),
           (r"You write $\tan\phi=\dfrac{5}{14/3}=\dfrac{15}{14}$ for the angle $\phi$ between $CO$ and $CG$", 1), (r"You obtain $\phi\approx47.0^{\circ}$", 1)],
          r"A lamina freely suspended from a point rests with its centre of mass vertically below that point, so the line from the point of suspension to the centre of mass is vertical and the angle sought is found from the right-angled triangle formed with the given edge.",
          r"$G$ is $5\ \text{cm}$ from $OC$ and $\tfrac{10}{3}\ \text{cm}$ above $OA$, hence $8-\tfrac{10}{3}=\tfrac{14}{3}\ \text{cm}$ below the level of $C$. In equilibrium $CG$ is vertical, and $CO$ runs straight down the face of the lamina from $C$ to $O$. Therefore $\tan\phi=\dfrac{5}{14/3}=\dfrac{15}{14}$ and $\phi=\arctan\dfrac{15}{14}\approx47.0^{\circ}$.",
          ans=r"$\approx47.0^{\circ}$"),
        S("c", r"A uniform ladder $PQ$ of mass $20\ \text{kg}$ and length $5\ \text{m}$ rests with its end $P$ on rough horizontal ground and its end $Q$ against a smooth vertical wall, in a vertical plane perpendicular to the wall. $P$ is $3\ \text{m}$ from the wall and $Q$ is $4\ \text{m}$ above the ground. A painter of mass $70\ \text{kg}$ stands on the ladder at a point $2\ \text{m}$ from $P$, measured along the ladder, and the ladder is on the point of slipping. Find the force exerted by the wall on the ladder and the coefficient of friction between the ladder and the ground.",
          ["equilibrium of rigid bodies"], "elevee", 5,
          [(r"You resolve vertically: $R=(20+70)\times9.8=882\ \text{N}$", 1), (r"You take moments about $P$ with the horizontal distances $1.5\ \text{m}$ and $1.2\ \text{m}$", 1),
           (r"You obtain $4S=196\times1.5+686\times1.2$ and $S=279.3\ \text{N}$", 1), (r"You resolve horizontally and use limiting friction: $F=S$ and $F=\mu R$", 1), (r"You obtain $\mu=\dfrac{279.3}{882}\approx0.317$", 1)],
          r"For a rigid body in equilibrium the forces resolve to zero in two perpendicular directions and the moments about any point add to zero; take moments about the point where two unknown forces meet, and use $F=\mu R$ when the body is on the point of slipping.",
          r"The wall is smooth, so its force $S$ is horizontal. Vertically $R=(20+70)g=882\ \text{N}$. Horizontally $F=S$. The ladder makes an angle with the ground with $\cos=\tfrac35$, so the horizontal distance from $P$ is $2.5\times\tfrac35=1.5\ \text{m}$ for the centre of the ladder and $2\times\tfrac35=1.2\ \text{m}$ for the painter. Moments about $P$: $S\times4=196\times1.5+686\times1.2=294+823.2=1117.2$, so $S=279.3\ \text{N}$. The ladder is on the point of slipping, so $F=\mu R$ gives $\mu=\dfrac{279.3}{882}\approx0.317$.",
          ans=r"$S=279.3\ \text{N}$ (horizontal) ; $\mu\approx0.317$",
          conseil=r"Take moments about $P$, where the unknown friction and the normal reaction both act: they disappear from the equation."),
    ]))

    # ---- Exercice 8 : circular motion and elastic strings (13) ----
    ex.append(E("8", G, 13, r"", [
        S("a", r"A particle of mass $0.4\ \text{kg}$ is attached to one end of a light inextensible string of length $1\ \text{m}$, the other end being fixed at a point $O$. The particle moves with constant speed in a horizontal circle, with the string taut and making an angle $\theta$ with the downward vertical, where $\cos\theta=0.8$. Find the tension in the string and the angular speed of the particle.",
          ["circular motion mechanics"], "moyenne", 4,
          [(r"You resolve vertically: $T\cos\theta=0.4\times9.8$", 1), (r"You obtain $T=4.9\ \text{N}$", 1), (r"You write the horizontal equation $T\sin\theta=m\omega^{2}r$ with $r=1\times0.6=0.6\ \text{m}$", 1), (r"You obtain $\omega=3.5\ \text{rad s}^{-1}$", 1)],
          r"For a particle moving in a horizontal circle the vertical forces balance, while the horizontal component of the resultant force is the centripetal force $m\omega^{2}r$ directed towards the centre of the circle.",
          r"Vertically: $T\cos\theta=mg$, so $T=\dfrac{0.4\times9.8}{0.8}=4.9\ \text{N}$. The radius of the circle is $r=1\times\sin\theta=0.6\ \text{m}$. Horizontally: $T\sin\theta=m\omega^{2}r$, so $4.9\times0.6=0.4\times\omega^{2}\times0.6$, which gives $\omega^{2}=12.25$ and $\omega=3.5\ \text{rad s}^{-1}$.",
          ans=r"$T=4.9\ \text{N}$ ; $\omega=3.5\ \text{rad s}^{-1}$"),
        S("b", r"A second particle of mass $0.4\ \text{kg}$ is attached to a light inextensible string of length $0.9\ \text{m}$ and moves in a complete vertical circle about the fixed end of the string. Its speed at the lowest point is $8\ \text{m s}^{-1}$. Find the tension in the string when the particle is at the highest point.",
          ["circular motion mechanics"], "elevee", 4,
          [(r"You apply conservation of energy between the lowest and highest points: $\tfrac12m(8^{2})=\tfrac12mv^{2}+mg(1.8)$", 1), (r"You obtain $v^{2}=28.72$", 1),
           (r"You apply Newton's second law at the top: $T+mg=\dfrac{mv^{2}}{0.9}$", 1), (r"You obtain $T\approx8.84\ \text{N}$", 1)],
          r"In a vertical circle the speed changes with height, so use conservation of energy to find the speed at the point required, then apply Newton's second law along the radius with the net force towards the centre equal to $mv^{2}/r$.",
          r"The highest point is $2\times0.9=1.8\ \text{m}$ above the lowest. Energy: $\tfrac12\times0.4\times64=\tfrac12\times0.4\,v^{2}+0.4\times9.8\times1.8$, so $v^{2}=64-35.28=28.72$. At the top both the tension and the weight act towards the centre: $T+0.4\times9.8=\dfrac{0.4\times28.72}{0.9}$, so $T=12.764-3.92\approx8.84\ \text{N}$.",
          ans=r"$\approx8.84\ \text{N}$",
          piege=r"At the highest point the weight acts towards the centre of the circle, so it is added to $T$ on the left of the equation, not subtracted."),
        S("c", r"A light elastic string has natural length $0.5\ \text{m}$ and modulus of elasticity $19.6\ \text{N}$. One end is attached to a fixed point $O$ on a ceiling and a particle of mass $0.5\ \text{kg}$ is attached to the other end. Find the extension of the string when the particle hangs in equilibrium.",
          ["elastic strings and potential energy mechanics"], "faible", 2,
          [(r"You write Hooke's law $T=\dfrac{\lambda e}{l}$ and $T=mg=4.9\ \text{N}$", 1), (r"You obtain $e=\dfrac{4.9\times0.5}{19.6}=0.125\ \text{m}$", 1)],
          r"The tension in an elastic string is $T=\dfrac{\lambda e}{l}$, where $\lambda$ is the modulus of elasticity, $e$ the extension and $l$ the natural length; in equilibrium it balances the weight.",
          r"In equilibrium $T=mg=0.5\times9.8=4.9\ \text{N}$ and $T=\dfrac{19.6\,e}{0.5}$, so $e=\dfrac{4.9\times0.5}{19.6}=0.125\ \text{m}$.",
          ans=r"$0.125\ \text{m}$"),
        S("d", r"The particle is now held at $O$ and released from rest, so that the string is slack at first. Find the greatest extension of the string in the motion that follows.",
          ["elastic strings and potential energy mechanics"], "moyenne", 3,
          [(r"You write the energy equation $mg(l+x)=\dfrac{\lambda x^{2}}{2l}$ with $x$ the greatest extension", 1), (r"You obtain the quadratic $8x^{2}-2x-1=0$", 1), (r"You solve it: $x=0.5\ \text{m}$ (rejecting the negative root)", 1)],
          r"With no resistance, the loss of gravitational potential energy equals the gain of elastic energy $\dfrac{\lambda x^{2}}{2l}$ when the particle is momentarily at rest at the lowest point, the fall being the natural length plus the extension.",
          r"At the lowest point the particle is momentarily at rest and has fallen $l+x=0.5+x$. Then $0.5\times9.8\,(0.5+x)=\dfrac{19.6\,x^{2}}{2\times0.5}$, that is $4.9(0.5+x)=19.6x^{2}$. Dividing by $2.45$: $2(0.5+x)=8x^{2}$, so $8x^{2}-2x-1=0$, that is $(4x+1)(2x-1)=0$. The positive root is $x=0.5$, so the greatest extension is $0.5\ \text{m}$.",
          ans=r"$0.5\ \text{m}$",
          piege=r"The particle falls the natural length plus the extension before it stops: using only $x$ for the loss of potential energy gives a wrong equation."),
    ]))

    return ex
