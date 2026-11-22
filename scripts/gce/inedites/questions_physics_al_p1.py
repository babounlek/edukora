r"""Les 50 QCM de l'epreuve inedite GCE A Level Physics Paper 1 n.1 (50 x 1 point, 90 min).

Structure mesuree sur les Paper 1 reels de 2024 a 2026 (themes melanges : unites, mecanique, thermique, ondes, electricite, magnetisme, atomique ;
calculs chiffres, quelques questions conceptuelles, une quinzaine de figures par sujet) ; aucune donnee, aucun enonce, aucun jeu d'options repris d'un
sujet reel. Chaque question : enonce, bonne reponse `key`, trois distracteurs avec l'erreur qui y mene, rappel, resolution, valeur de controle `val`
(recalculee par verifier_reponses_physics_al_p1.py par une autre voie ; None pour une question conceptuelle). Les lettres des cles sont placees par
le GENERATEUR, jamais tapees ici. `{FIG}` devient « Figure N ». Chaines BRUTES (une commande LaTeX a backslash simple dans une chaine ordinaire est un piege).
"""

QS = []


def Q(themes, diff, stem, key, dist, rappel, sol, val, conseil=None, fig=None, conc=False):
    assert len(dist) == 3 and all(len(d) == 2 for d in dist), stem[:40]
    texts = [key] + [d[0] for d in dist]
    assert len(set(texts)) == 4, ("options en double", stem[:50])
    assert (fig is None) == ("{FIG}" not in stem), stem[:40]
    QS.append(dict(themes=themes, diff=diff, stem=stem, key=key, dist=dist, rappel=rappel, sol=sol, val=val, conseil=conseil, fig=fig, conc=conc))


def questions():
    return QS


# 1
Q(["physical quantities and units"], "faible", r"The pascal, expressed in SI base units, is",
  r"$\text{kg m}^{-1}\,\text{s}^{-2}$",
  [(r"$\text{kg m s}^{-2}$", r"gives the newton and forgets to divide by the area"), (r"$\text{kg m}^{2}\,\text{s}^{-2}$", r"gives the joule, a force multiplied by a length"),
   (r"$\text{kg m}^{-2}\,\text{s}^{-2}$", r"divides by $\text{m}^{2}$ without cancelling one metre of the newton")],
  r"A derived unit is rebuilt from its defining equation: pressure is force divided by area, and the newton is $\text{kg m s}^{-2}$.",
  r"$\text{Pa}=\dfrac{\text{N}}{\text{m}^{2}}=\dfrac{\text{kg m s}^{-2}}{\text{m}^{2}}=\text{kg m}^{-1}\,\text{s}^{-2}$.",
  (1, -1, -2))
# 2
Q(["dimensional analysis"], "moyenne",
  r"The speed $v$ of transverse waves on a stretched string is thought to depend on the tension $T$ in the string and on its mass per unit length $\mu$, "
  r"so that $v=kT^{a}\mu^{b}$, where $k$ is a dimensionless constant. The values of $a$ and $b$ are",
  r"$a=\tfrac12,\ b=-\tfrac12$",
  [(r"$a=\tfrac12,\ b=\tfrac12$", r"keeps both exponents positive, so the mass per unit length does not appear in the denominator"),
   (r"$a=1,\ b=-1$", r"balances the mass and the time but forgets that the speed is a first power of length over time, giving $T/\mu$ instead of its square root"),
   (r"$a=-\tfrac12,\ b=\tfrac12$", r"swaps the two signs, which gives the inverse of the speed")],
  r"Both sides of a physical equation must have the same dimensions. Write each quantity in base dimensions $[M]$, $[L]$, $[T]$ and equate the powers.",
  r"$[v]=\text{L T}^{-1}$, $[T]=\text{M L T}^{-2}$ and $[\mu]=\text{M L}^{-1}$. Mass: $a+b=0$. Time: $-2a=-1$, so $a=\tfrac12$ and $b=-\tfrac12$. Length: $a-b=1$ is also satisfied.",
  (0.5, -0.5))
# 3
Q(["scalar and vector quantities"], "faible", r"Two forces of $6.0\ \text{N}$ and $8.0\ \text{N}$ act at a point at right angles to each other. What are the magnitude of their resultant and its direction relative to the $8.0\ \text{N}$ force?",
  r"$10\ \text{N}$ at $37^{\circ}$",
  [(r"$14\ \text{N}$ at $37^{\circ}$", r"adds the magnitudes instead of combining the components at right angles"), (r"$10\ \text{N}$ at $53^{\circ}$", r"measures the angle from the $6.0\ \text{N}$ force instead of the $8.0\ \text{N}$ force"),
   (r"$7.0\ \text{N}$ at $37^{\circ}$", r"takes the mean of the two magnitudes")],
  r"Forces are vectors: for two perpendicular forces the resultant has magnitude $\sqrt{F_1^{2}+F_2^{2}}$ and makes an angle $\theta$ with $F_2$ such that $\tan\theta=\dfrac{F_1}{F_2}$.",
  r"$R=\sqrt{6.0^{2}+8.0^{2}}=10\ \text{N}$. The angle with the $8.0\ \text{N}$ force is $\tan^{-1}\dfrac{6.0}{8.0}=37^{\circ}$.",
  (10.0, 36.87))
# 4
Q(["motion"], "faible", r"A stone is thrown vertically upwards at $14\ \text{m s}^{-1}$ from ground level. Taking $g=9.8\ \text{m s}^{-2}$ and neglecting air resistance, the greatest height it reaches is",
  r"$10\ \text{m}$",
  [(r"$20\ \text{m}$", r"omits the factor $2$ in $v^{2}=2gh$"), (r"$1.4\ \text{m}$", r"calculates the time to the top, $v/g$, and quotes it as a height"),
   (r"$2.5\ \text{m}$", r"uses half of the launch speed in $v^{2}=2gh$")],
  r"For uniform acceleration $v^{2}=u^{2}+2as$. At the highest point $v=0$ and $a=-g$.",
  r"$0=14^{2}-2\times9.8\times h$, so $h=\dfrac{196}{19.6}=10\ \text{m}$.",
  10.0)
# 5
Q(["motion"], "faible",
  r"{FIG} shows how the velocity of a train varies with time on a straight track. The train accelerates uniformly from rest to $12\ \text{m s}^{-1}$ in $5.0\ \text{s}$, "
  r"moves at constant velocity for the next $15\ \text{s}$ and then decelerates uniformly to rest in $10\ \text{s}$. The total distance travelled is",
  r"$270\ \text{m}$",
  [(r"$360\ \text{m}$", r"treats the whole $30\ \text{s}$ as travel at $12\ \text{m s}^{-1}$"), (r"$210\ \text{m}$", r"leaves out the area of the final triangle"),
   (r"$180\ \text{m}$", r"counts only the rectangle of constant velocity")],
  r"The area under a velocity-time graph is the displacement. Split the area into triangles and a rectangle.",
  r"Triangle 1: $\tfrac12\times5.0\times12=30\ \text{m}$. Rectangle: $15\times12=180\ \text{m}$. Triangle 2: $\tfrac12\times10\times12=60\ \text{m}$. Total $270\ \text{m}$.",
  270.0, fig="vt")
# 6
Q(["newton's laws of motion"], "faible", r"A car of mass $1200\ \text{kg}$ accelerates uniformly from $5.0\ \text{m s}^{-1}$ to $20\ \text{m s}^{-1}$ in $6.0\ \text{s}$. The resultant force on the car is",
  r"$3.0\times10^{3}\ \text{N}$",
  [(r"$4.0\times10^{3}\ \text{N}$", r"uses the final speed instead of the change in speed"), (r"$1.8\times10^{4}\ \text{N}$", r"multiplies the mass by the change in speed and forgets to divide by the time"),
   (r"$7.2\times10^{3}\ \text{N}$", r"multiplies the mass by the time")],
  r"The resultant force is the rate of change of momentum: $F=ma=m\dfrac{v-u}{t}$.",
  r"$a=\dfrac{20-5.0}{6.0}=2.5\ \text{m s}^{-2}$, so $F=1200\times2.5=3.0\times10^{3}\ \text{N}$.",
  3000.0)
# 7
Q(["equilibrium of forces"], "moyenne", r"A lamp of weight $40\ \text{N}$ hangs at rest from the midpoint of a light string. The two halves of the string each make an angle of $30^{\circ}$ with the horizontal. The tension in each half of the string is",
  r"$40\ \text{N}$",
  [(r"$20\ \text{N}$", r"shares the weight equally between the two halves and ignores the angle"), (r"$80\ \text{N}$", r"forgets that two strings share the vertical load, using $W/\sin30^{\circ}$"),
   (r"$23\ \text{N}$", r"uses $\cos30^{\circ}$ in place of $\sin30^{\circ}$")],
  r"At rest the forces balance. Resolve the tensions vertically: the sum of the vertical components equals the weight.",
  r"$2T\sin30^{\circ}=W$, so $T=\dfrac{40}{2\times0.50}=40\ \text{N}$. The horizontal components $T\cos30^{\circ}$ cancel.",
  40.0)
# 8
Q(["momentum"], "faible", r"A trolley of mass $2.0\ \text{kg}$ moving at $3.0\ \text{m s}^{-1}$ collides with a stationary trolley of mass $1.0\ \text{kg}$ and the two stick together. Their common speed just after the collision is",
  r"$2.0\ \text{m s}^{-1}$",
  [(r"$1.5\ \text{m s}^{-1}$", r"divides the initial speed by the number of trolleys"), (r"$1.0\ \text{m s}^{-1}$", r"divides the initial speed by the total mass"),
   (r"$6.0\ \text{m s}^{-1}$", r"forgets to divide the momentum by the total mass")],
  r"In a collision with no external force the total momentum is conserved: $m_1u_1+m_2u_2=(m_1+m_2)v$ when the bodies stick together.",
  r"$2.0\times3.0+0=(2.0+1.0)v$, so $v=\dfrac{6.0}{3.0}=2.0\ \text{m s}^{-1}$.",
  2.0)
# 9
Q(["momentum"], "moyenne", r"A ball of mass $0.15\ \text{kg}$ hits a wall at $12\ \text{m s}^{-1}$ at right angles and rebounds along the same line at $8.0\ \text{m s}^{-1}$. The contact lasts $0.020\ \text{s}$. The magnitude of the average force exerted by the wall on the ball is",
  r"$150\ \text{N}$",
  [(r"$30\ \text{N}$", r"subtracts the two speeds instead of adding them, since the direction reverses"), (r"$90\ \text{N}$", r"uses the incoming speed only"),
   (r"$60\ \text{N}$", r"uses the rebound speed only")],
  r"The average force is the change of momentum divided by the contact time. Momentum is a vector: a rebound reverses its sign.",
  r"Take the rebound direction as positive: $\Delta p=0.15\times8.0-0.15\times(-12)=3.0\ \text{kg m s}^{-1}$. Then $F=\dfrac{3.0}{0.020}=150\ \text{N}$.",
  150.0)
# 10
Q(["work energy and power"], "faible", r"A pump raises $600\ \text{kg}$ of water every minute through a vertical height of $15\ \text{m}$. Taking $g=9.8\ \text{m s}^{-2}$, the minimum useful power of the pump is",
  r"$1.5\times10^{3}\ \text{W}$",
  [(r"$8.8\times10^{4}\ \text{W}$", r"forgets to divide the work by the $60\ \text{s}$"), (r"$1.5\times10^{2}\ \text{W}$", r"leaves out $g$ and uses mass times height over time"),
   (r"$25\ \text{W}$", r"divides by $60$ twice")],
  r"Power is work done per unit time. Work done in lifting a mass $m$ through a height $h$ is $mgh$.",
  r"$P=\dfrac{mgh}{t}=\dfrac{600\times9.8\times15}{60}=1.47\times10^{3}\ \text{W}\approx1.5\times10^{3}\ \text{W}$.",
  1470.0)
# 11
Q(["work energy and power"], "faible", r"A car engine delivers a useful power of $40\ \text{kW}$ while the car moves at a steady $25\ \text{m s}^{-1}$ on a level road. The total resistive force on the car is",
  r"$1.6\times10^{3}\ \text{N}$",
  [(r"$1.0\times10^{6}\ \text{N}$", r"multiplies the power by the speed instead of dividing"), (r"$1.6\ \text{N}$", r"leaves the power in kilowatts"),
   (r"$6.3\times10^{-4}\ \text{N}$", r"divides the speed by the power")],
  r"For steady speed the driving force equals the resistive force, and $P=Fv$.",
  r"$F=\dfrac{P}{v}=\dfrac{40\times10^{3}}{25}=1.6\times10^{3}\ \text{N}$.",
  1600.0)
# 12
Q(["gravitational fields"], "faible", r"Which statement about the gravitational potential at a point in the field of an isolated planet is correct?",
  r"It is negative, and it increases towards zero as the distance from the planet increases.",
  [(r"It is positive, and it decreases as the distance from the planet increases.", r"gives the sign of the gravitational potential energy of a mass the wrong way round"),
   (r"It is zero at the surface of the planet and negative outside it.", r"takes the surface as the zero of potential, which is not the convention"),
   (r"It is negative, and it becomes more negative as the distance from the planet increases.", r"reverses the trend: the potential rises towards zero at infinity")],
  r"The gravitational potential at distance $r$ from a point mass $M$ is $V=-\dfrac{GM}{r}$, with $V=0$ at infinity.",
  r"$V=-\dfrac{GM}{r}$ is negative everywhere and tends to $0$ as $r\to\infty$, so it increases as $r$ increases. Only the first statement agrees.",
  None, conc=True)
# 13
Q(["circular motion"], "faible", r"A stone of mass $0.50\ \text{kg}$ is whirled on a smooth horizontal table at a steady speed of $4.0\ \text{m s}^{-1}$ in a circle of radius $0.80\ \text{m}$ by a light string. The tension in the string is",
  r"$10\ \text{N}$",
  [(r"$2.5\ \text{N}$", r"uses $mv/r$ instead of $mv^{2}/r$"), (r"$6.4\ \text{N}$", r"multiplies by the radius instead of dividing"), (r"$8.0\ \text{N}$", r"forgets to divide by the radius")],
  r"The centripetal force needed for circular motion is $F=\dfrac{mv^{2}}{r}$; here it is supplied by the tension.",
  r"$T=\dfrac{0.50\times4.0^{2}}{0.80}=\dfrac{8.0}{0.80}=10\ \text{N}$.",
  10.0)
# 14
Q(["gravitational fields", "circular motion"], "moyenne", r"Two satellites move in circular orbits around the same planet. Satellite X has an orbital radius $r$ and a period of $8.0\ \text{h}$. Satellite Y has an orbital radius $4r$. The period of Y is",
  r"$64\ \text{h}$",
  [(r"$32\ \text{h}$", r"takes the period proportional to the radius"), (r"$128\ \text{h}$", r"takes the period proportional to the square of the radius"),
   (r"$16\ \text{h}$", r"takes the period proportional to the square root of the radius")],
  r"For circular orbits about the same body, Kepler's third law gives $T^{2}\propto r^{3}$.",
  r"$\dfrac{T_Y}{T_X}=\left(\dfrac{4r}{r}\right)^{3/2}=4^{3/2}=8$, so $T_Y=8\times8.0=64\ \text{h}$.",
  64.0)
# 15
Q(["simple harmonic motion"], "faible", r"A particle moves with simple harmonic motion given by $x=0.050\sin(12t)$, where $x$ is in metres and $t$ in seconds. Its maximum speed is",
  r"$0.60\ \text{m s}^{-1}$",
  [(r"$7.2\ \text{m s}^{-1}$", r"quotes $\omega^{2}A$, the maximum acceleration, as a speed"), (r"$4.2\times10^{-3}\ \text{m s}^{-1}$", r"divides the amplitude by $\omega$"),
   (r"$0.050\ \text{m s}^{-1}$", r"takes the amplitude as the speed")],
  r"For $x=A\sin\omega t$ the velocity is $v=A\omega\cos\omega t$, so its maximum is $v_{\max}=A\omega$.",
  r"$A=0.050\ \text{m}$ and $\omega=12\ \text{rad s}^{-1}$, so $v_{\max}=0.050\times12=0.60\ \text{m s}^{-1}$.",
  0.60)
# 16
Q(["simple harmonic motion"], "faible", r"A mass of $0.40\ \text{kg}$ hangs from a light spring of force constant $64\ \text{N m}^{-1}$ and oscillates vertically with a small amplitude. The period of the oscillation is",
  r"$0.50\ \text{s}$",
  [(r"$0.079\ \text{s}$", r"leaves out the factor $2\pi$"), (r"$2.0\ \text{s}$", r"quotes the frequency in hertz as if it were the period"),
   (r"$13\ \text{s}$", r"quotes the angular frequency $\sqrt{k/m}$ as the period")],
  r"A mass on a spring has $T=2\pi\sqrt{\dfrac{m}{k}}$.",
  r"$T=2\pi\sqrt{\dfrac{0.40}{64}}=2\pi\times0.0791=0.50\ \text{s}$.",
  0.4967)
# 17
Q(["gravitational fields"], "moyenne", r"The gravitational field strength at the surface of the Earth is $9.8\ \text{N kg}^{-1}$. Its value at a height above the surface equal to half of the Earth's radius is",
  r"$4.4\ \text{N kg}^{-1}$",
  [(r"$6.5\ \text{N kg}^{-1}$", r"uses an inverse law in the distance instead of an inverse square law"), (r"$2.9\ \text{N kg}^{-1}$", r"uses an inverse cube law"),
   (r"$39\ \text{N kg}^{-1}$", r"takes the distance from the centre to be $0.5R$ instead of $1.5R$")],
  r"Outside a spherical planet the field strength follows an inverse square law: $g\propto\dfrac{1}{r^{2}}$, where $r$ is measured from the centre.",
  r"The distance from the centre is $R+0.5R=1.5R$. Then $g=\dfrac{9.8}{1.5^{2}}=4.36\approx4.4\ \text{N kg}^{-1}$.",
  4.356)
# 18
Q(["gravitational fields"], "elevee", r"The escape speed from the surface of the Earth is $11\ \text{km s}^{-1}$. A planet has a mass $8$ times that of the Earth and a radius $2$ times that of the Earth. What is the escape speed from its surface?",
  r"$22\ \text{km s}^{-1}$",
  [(r"$44\ \text{km s}^{-1}$", r"multiplies by the ratio $8/2=4$ instead of its square root"), (r"$31\ \text{km s}^{-1}$", r"multiplies by $\sqrt8$ and ignores the larger radius"),
   (r"$16\ \text{km s}^{-1}$", r"takes the square root of the ratio of the radii only")],
  r"The escape speed is $v=\sqrt{\dfrac{2GM}{R}}$, so $v\propto\sqrt{M/R}$.",
  r"$\dfrac{v}{v_E}=\sqrt{\dfrac{8}{2}}=2$, so $v=2\times11=22\ \text{km s}^{-1}$.",
  22.0)
# 19
Q(["stress and strain"], "moyenne", r"A steel wire of length $2.0\ \text{m}$ and diameter $0.50\ \text{mm}$ carries a load of $40\ \text{N}$. The Young modulus of steel is $2.0\times10^{11}\ \text{Pa}$. The extension of the wire is",
  r"$2.0\ \text{mm}$",
  [(r"$0.51\ \text{mm}$", r"uses the diameter as the radius in the area"), (r"$8.1\ \text{mm}$", r"uses a quarter of the diameter as the radius"),
   (r"$1.6\ \text{mm}$", r"takes the area as $d^{2}$ instead of $\pi d^{2}/4$")],
  r"Young modulus $E=\dfrac{\text{stress}}{\text{strain}}=\dfrac{F/A}{e/L}$, so $e=\dfrac{FL}{AE}$ with $A=\pi\left(\dfrac d2\right)^{2}$.",
  r"$A=\pi(0.25\times10^{-3})^{2}=1.96\times10^{-7}\ \text{m}^{2}$, so $e=\dfrac{40\times2.0}{1.96\times10^{-7}\times2.0\times10^{11}}=2.0\times10^{-3}\ \text{m}$.",
  2.04e-3)
# 20
Q(["stress and strain"], "moyenne",
  r"{FIG} is the force-extension graph of a spring that obeys Hooke's law. The force reaches $12\ \text{N}$ when the extension is $4.0\ \text{cm}$. The elastic potential energy stored in the spring at this extension is",
  r"$0.24\ \text{J}$",
  [(r"$0.48\ \text{J}$", r"uses $Fx$ instead of $\tfrac12Fx$"), (r"$24\ \text{J}$", r"leaves the extension in centimetres"), (r"$2.4\ \text{J}$", r"converts $4.0\ \text{cm}$ to $0.40\ \text{m}$")],
  r"The energy stored in a stretched spring is the area under the force-extension graph: $E=\tfrac12Fx$ while Hooke's law holds.",
  r"$E=\tfrac12\times12\times0.040=0.24\ \text{J}$.",
  0.24, fig="force")
# 21
Q(["specific heat capacity"], "faible", r"A heater of power $500\ \text{W}$ is switched on for $3.0$ minutes to warm $1.5\ \text{kg}$ of a liquid in a well-insulated container. The temperature of the liquid rises by $12\ \text{K}$. The specific heat capacity of the liquid is",
  r"$5.0\times10^{3}\ \text{J kg}^{-1}\text{K}^{-1}$",
  [(r"$83\ \text{J kg}^{-1}\text{K}^{-1}$", r"uses the time in minutes instead of seconds"), (r"$7.5\times10^{3}\ \text{J kg}^{-1}\text{K}^{-1}$", r"forgets to divide by the mass"),
   (r"$6.0\times10^{4}\ \text{J kg}^{-1}\text{K}^{-1}$", r"forgets to divide by the temperature rise")],
  r"Electrical energy $Pt$ supplied equals thermal energy gained, $Q=mc\Delta\theta$, when there are no losses.",
  r"$Pt=500\times180=9.0\times10^{4}\ \text{J}$. Then $c=\dfrac{Pt}{m\Delta\theta}=\dfrac{9.0\times10^{4}}{1.5\times12}=5.0\times10^{3}\ \text{J kg}^{-1}\text{K}^{-1}$.",
  5000.0)
# 22
Q(["stationary waves"], "faible", r"Which statement about a stationary wave on a stretched string fixed at both ends is correct?",
  r"All points between two adjacent nodes oscillate in phase with one another.",
  [(r"Every point on the string oscillates with the same amplitude.", r"the amplitude is zero at a node and largest at an antinode"),
   (r"Energy is carried along the string from one end to the other.", r"a stationary wave transfers no net energy along the string"),
   (r"Points on either side of a node oscillate in phase with each other.", r"points on either side of a node are in antiphase")],
  r"A stationary wave has nodes of zero amplitude and antinodes of maximum amplitude; the phase is constant between adjacent nodes and changes by $\pi$ across a node.",
  r"Between two adjacent nodes the string moves up together or down together, so those points are in phase. The amplitude varies along the string, no net energy flows and the points across a node are in antiphase.",
  None, conc=True)
# 23
Q(["kinetic theory of gases"], "faible", r"The temperature of a fixed mass of ideal gas is raised from $27^{\circ}\text{C}$ to $927^{\circ}\text{C}$. By what factor does the root mean square speed of its molecules increase?",
  r"$2.0$",
  [(r"$4.0$", r"takes the factor on the speed to be the ratio of the absolute temperatures"), (r"$5.9$", r"takes the square root of the ratio of the Celsius values"),
   (r"$34$", r"takes the ratio of the Celsius values")],
  r"The mean kinetic energy of a molecule is proportional to the thermodynamic temperature, so $c_{\text{rms}}\propto\sqrt{T}$ with $T$ in kelvin.",
  r"$T_1=300\ \text{K}$ and $T_2=1200\ \text{K}$. Then $\dfrac{c_2}{c_1}=\sqrt{\dfrac{1200}{300}}=2.0$.",
  2.0)
# 24
Q(["kinetic theory of gases"], "moyenne", r"A fixed mass of $0.50\ \text{mol}$ of ideal gas is held in a rigid vessel of volume $2.0$ litres at a temperature of $77^{\circ}\text{C}$. Taking the molar gas constant as $8.31\ \text{J mol}^{-1}\text{K}^{-1}$, the pressure of the gas is",
  r"$7.3\times10^{5}\ \text{Pa}$",
  [(r"$7.3\times10^{2}\ \text{Pa}$", r"uses $2.0$ as a volume in cubic metres instead of $2.0\times10^{-3}\ \text{m}^{3}$"), (r"$1.5\times10^{6}\ \text{Pa}$", r"forgets the amount of gas"),
   (r"$1.6\times10^{5}\ \text{Pa}$", r"uses $77$ as a temperature in kelvin")],
  r"For an ideal gas $pV=nRT$, with $T$ in kelvin and $V$ in cubic metres ($1\ \text{litre}=10^{-3}\ \text{m}^{3}$).",
  r"$T=77+273=350\ \text{K}$. Then $p=\dfrac{nRT}{V}=\dfrac{0.50\times8.31\times350}{2.0\times10^{-3}}=7.3\times10^{5}\ \text{Pa}$.",
  7.27e5)
# 25
Q(["first law of thermodynamics"], "faible", r"A gas expands at a constant pressure of $2.0\times10^{5}\ \text{Pa}$ from $1.0\times10^{-3}\ \text{m}^{3}$ to $4.0\times10^{-3}\ \text{m}^{3}$ while it absorbs $900\ \text{J}$ of thermal energy. The increase in internal energy of the gas is",
  r"$300\ \text{J}$",
  [(r"$1500\ \text{J}$", r"adds the work done by the gas to the thermal energy absorbed"), (r"$600\ \text{J}$", r"gives the work done by the gas, not the change in internal energy"),
   (r"$-300\ \text{J}$", r"subtracts the heat from the work, which reverses the sign")],
  r"First law: $\Delta U=Q-W$, where $Q$ is the thermal energy supplied to the gas and $W=p\Delta V$ is the work done by the gas.",
  r"$W=2.0\times10^{5}\times(4.0-1.0)\times10^{-3}=600\ \text{J}$, so $\Delta U=900-600=300\ \text{J}$.",
  300.0)
# 26
Q(["first law of thermodynamics"], "moyenne", r"An ideal gas expands slowly and isothermally. Which statement is correct?",
  r"The gas absorbs thermal energy equal to the work it does on its surroundings.",
  [(r"The internal energy of the gas falls by the amount of work it does.", r"ignores the thermal energy that flows in to keep the temperature constant"),
   (r"No thermal energy is exchanged because the temperature does not change.", r"confuses a constant temperature with the absence of heat flow"),
   (r"The work done by the gas is zero because the temperature is constant.", r"confuses the constant temperature with a constant volume")],
  r"The internal energy of an ideal gas depends only on its temperature. First law: $\Delta U=Q-W$.",
  r"At constant temperature $\Delta U=0$, so $Q=W$: the gas must take in thermal energy equal to the work it does as it expands.",
  None, conc=True)
# 27
Q(["waves"], "faible", r"A progressive wave on a rope has a frequency of $50\ \text{Hz}$ and a wavelength of $0.80\ \text{m}$. The speed of the wave along the rope is",
  r"$40\ \text{m s}^{-1}$",
  [(r"$63\ \text{m s}^{-1}$", r"divides the frequency by the wavelength"), (r"$0.016\ \text{m s}^{-1}$", r"divides the wavelength by the frequency"),
   (r"$51\ \text{m s}^{-1}$", r"adds the frequency and the wavelength")],
  r"The wave equation is $v=f\lambda$.",
  r"$v=50\times0.80=40\ \text{m s}^{-1}$.",
  40.0)
# 28
Q(["simple harmonic motion"], "faible",
  "Which of the following statements about a particle moving with simple harmonic motion is/are correct?\n\n"
  "1. Its acceleration is always directed towards the equilibrium position.\n\n"
  "2. Its speed is greatest when it passes through the equilibrium position.\n\n"
  "3. Its total energy is zero at the position of maximum displacement.",
  r"1 and 2 only",
  [(r"1 only", r"misses that the speed is greatest at the equilibrium position"), (r"2 and 3 only", r"believes the total energy vanishes at the turning point, where it is all potential"),
   (r"1, 2 and 3", r"accepts the false statement about the total energy")],
  r"In SHM $a=-\omega^{2}x$, the speed is $v=\omega\sqrt{A^{2}-x^{2}}$ and the total energy $\tfrac12m\omega^{2}A^{2}$ is constant.",
  r"Statement 1 is true because $a=-\omega^{2}x$ points to the equilibrium position. Statement 2 is true because $v$ is largest at $x=0$. Statement 3 is false: at maximum displacement the energy is entirely potential and equals the total energy, which is constant.",
  None, conc=True)
# 29
Q(["interference of waves"], "moyenne", r"Monochromatic light of wavelength $600\ \text{nm}$ illuminates a double slit whose slits are $0.50\ \text{mm}$ apart. The fringes are seen on a screen $2.0\ \text{m}$ from the slits. The fringe spacing is",
  r"$2.4\ \text{mm}$",
  [(r"$24\ \text{mm}$", r"reads the slit separation as $0.050\ \text{mm}$"), (r"$1.2\ \text{mm}$", r"doubles the slit separation"), (r"$4.8\ \text{mm}$", r"halves the slit separation")],
  r"In a double-slit experiment the fringe spacing is $x=\dfrac{\lambda D}{a}$.",
  r"$x=\dfrac{600\times10^{-9}\times2.0}{0.50\times10^{-3}}=2.4\times10^{-3}\ \text{m}=2.4\ \text{mm}$.",
  2.4e-3)
# 30
Q(["interference of waves"], "moyenne", r"Light of wavelength $600\ \text{nm}$ falls normally on a diffraction grating with $300$ lines per millimetre. At what angle to the normal is the second-order maximum?",
  r"$21^{\circ}$",
  [(r"$10^{\circ}$", r"uses the first order"), (r"$0.36^{\circ}$", r"quotes the value of $\sin\theta$ as an angle in degrees"), (r"$46^{\circ}$", r"uses a grating of $600$ lines per millimetre")],
  r"For a diffraction grating $d\sin\theta=n\lambda$, where $d$ is the distance between adjacent slits.",
  r"$d=\dfrac{1}{300\times10^{3}}=3.33\times10^{-6}\ \text{m}$. Then $\sin\theta=\dfrac{2\times600\times10^{-9}}{3.33\times10^{-6}}=0.36$, so $\theta=21^{\circ}$.",
  21.1)
# 31
Q(["stationary waves"], "moyenne",
  r"{FIG} shows a stationary wave on a string of length $1.20\ \text{m}$ that is fixed at both ends and vibrates in a pattern of three loops. The wavelength of the waves on the string is",
  r"$0.80\ \text{m}$",
  [(r"$2.4\ \text{m}$", r"gives the wavelength of the fundamental, one loop"), (r"$0.40\ \text{m}$", r"divides the length of the string by three"), (r"$1.2\ \text{m}$", r"takes the wavelength to be the length of the string")],
  r"Each loop of a stationary wave is half a wavelength long, so a string of length $L$ with $n$ loops has $L=n\dfrac{\lambda}{2}$.",
  r"Three loops give $1.20=3\times\dfrac{\lambda}{2}$, so $\lambda=0.80\ \text{m}$.",
  0.80, fig="corde")
# 32
Q(["stationary waves"], "faible", r"A pipe $0.30\ \text{m}$ long is closed at one end and open at the other. The speed of sound in air is $340\ \text{m s}^{-1}$. The frequency of the fundamental note is",
  r"$283\ \text{Hz}$",
  [(r"$567\ \text{Hz}$", r"treats the pipe as open at both ends"), (r"$1130\ \text{Hz}$", r"uses $v/L$ with a wavelength equal to the length of the pipe"), (r"$850\ \text{Hz}$", r"gives the frequency of the third harmonic of the closed pipe")],
  r"A closed pipe has a node at the closed end and an antinode at the open end, so the fundamental has $\lambda=4L$ and $f=\dfrac{v}{4L}$.",
  r"$f=\dfrac{340}{4\times0.30}=283\ \text{Hz}$.",
  283.3)
# 33
Q(["refraction of light"], "moyenne", r"Light travels in glass of refractive index $1.60$ towards a boundary with water of refractive index $1.33$. The critical angle for this boundary is",
  r"$56^{\circ}$",
  [(r"$34^{\circ}$", r"uses the cosine instead of the sine"), (r"$39^{\circ}$", r"uses the critical angle for a glass-air boundary"), (r"$0.83^{\circ}$", r"quotes the value of $\sin C$ as an angle in degrees")],
  r"At the critical angle the refracted ray travels along the boundary: $n_1\sin C=n_2\sin90^{\circ}$.",
  r"$\sin C=\dfrac{1.33}{1.60}=0.831$, so $C=56^{\circ}$.",
  56.2)
# 34
Q(["electronics and semiconductors"], "faible", r"Which statement about an n-type semiconductor is correct?",
  r"Its majority charge carriers are electrons, and the material as a whole is electrically neutral.",
  [(r"Its majority charge carriers are electrons, so the material carries a net negative charge.", r"believes the extra free electrons charge the crystal, but the donor nuclei balance them"),
   (r"Its majority charge carriers are holes, created by pentavalent donor atoms.", r"pentavalent donors supply electrons, not holes"),
   (r"Its majority charge carriers are holes, and the material as a whole carries a net positive charge.", r"mixes up n-type and p-type material")],
  r"Doping with pentavalent atoms (donors) adds free electrons; doping with trivalent atoms (acceptors) adds holes. Doped material stays electrically neutral.",
  r"Each donor atom gives one free electron and leaves a fixed positive ion, so the number of positive and negative charges is equal and the crystal is neutral, with electrons as the majority carriers.",
  None, conc=True)
# 35
Q(["electric fields"], "faible", r"Two large parallel metal plates are $4.0\ \text{cm}$ apart in a vacuum with a potential difference of $600\ \text{V}$ between them. An electron ($e=1.6\times10^{-19}\ \text{C}$) is released between the plates. The electric force on the electron is",
  r"$2.4\times10^{-15}\ \text{N}$",
  [(r"$2.4\times10^{-17}\ \text{N}$", r"uses the plate separation in centimetres"), (r"$3.8\times10^{-18}\ \text{N}$", r"multiplies the potential difference by the separation"),
   (r"$1.5\times10^{4}\ \text{N}$", r"gives the field strength in $\text{N C}^{-1}$ and forgets the charge")],
  r"Between parallel plates the field is uniform with $E=\dfrac{V}{d}$, and the force on a charge $q$ is $F=qE$.",
  r"$E=\dfrac{600}{0.040}=1.5\times10^{4}\ \text{V m}^{-1}$, so $F=eE=1.6\times10^{-19}\times1.5\times10^{4}=2.4\times10^{-15}\ \text{N}$.",
  2.4e-15)
# 36
Q(["radioactive decay"], "faible", r"A nucleus of carbon-14 decays into a nucleus of nitrogen-14: $^{14}_{6}\text{C}\to{}^{14}_{7}\text{N}+X$. Which particles make up $X$?",
  r"A beta-minus particle and an antineutrino",
  [(r"A beta-minus particle and a neutrino", r"forgets that lepton number must be conserved, so the electron needs an antineutrino"), (r"A beta-plus particle and a neutrino", r"takes a positron, which would lower the proton number"),
   (r"An alpha particle", r"an alpha particle would lower the nucleon number by $4$")],
  r"In beta-minus decay a neutron changes into a proton: $n\to p+e^{-}+\bar{\nu}_e$. The nucleon number is unchanged, the proton number rises by $1$, and charge and lepton number are conserved.",
  r"The nucleon number stays $14$ and the proton number rises from $6$ to $7$, so one unit of positive charge appears and an electron (a beta-minus particle) must be emitted. The electron has lepton number $+1$, so an antineutrino of lepton number $-1$ is emitted with it.",
  None, conc=True)
# 37
Q(["capacitors"], "elevee", r"A $470\ \mu\text{F}$ capacitor charged to $9.0\ \text{V}$ discharges through a $22\ \text{k}\Omega$ resistor. What is the potential difference across the capacitor $20\ \text{s}$ after the discharge begins?",
  r"$1.3\ \text{V}$",
  [(r"$7.7\ \text{V}$", r"uses the charging law $V_0(1-e^{-t/RC})$"), (r"$4.7\ \text{V}$", r"divides $V_0$ by $t/RC$ instead of using an exponential"),
   (r"$1.9\times10^{-8}\ \text{V}$", r"leaves out the time constant, using $V_0e^{-t}$")],
  r"During discharge $V=V_0e^{-t/RC}$, where $RC$ is the time constant.",
  r"$RC=470\times10^{-6}\times22\times10^{3}=10.3\ \text{s}$. Then $V=9.0\,e^{-20/10.3}=9.0\times0.145=1.3\ \text{V}$.",
  1.30)
# 38
Q(["capacitors"], "faible", r"The energy stored in a $100\ \mu\text{F}$ capacitor charged to a potential difference of $50\ \text{V}$ is",
  r"$0.125\ \text{J}$",
  [(r"$0.25\ \text{J}$", r"uses $CV^{2}$ and forgets the factor $\tfrac12$"), (r"$2.5\times10^{-3}\ \text{J}$", r"uses $\tfrac12CV$"), (r"$125\ \text{J}$", r"treats microfarads as millifarads")],
  r"The energy stored in a capacitor is $E=\tfrac12CV^{2}$.",
  r"$E=\tfrac12\times100\times10^{-6}\times50^{2}=0.125\ \text{J}$.",
  0.125)
# 39
Q(["current electricity"], "faible", r"A copper wire $2.0\ \text{m}$ long has a diameter of $0.40\ \text{mm}$. The resistivity of copper is $1.7\times10^{-8}\ \Omega\,\text{m}$. The resistance of the wire is",
  r"$0.27\ \Omega$",
  [(r"$0.068\ \Omega$", r"uses the diameter as the radius"), (r"$1.1\ \Omega$", r"uses a quarter of the diameter as the radius"), (r"$0.21\ \Omega$", r"takes the area as $d^{2}$")],
  r"The resistance of a uniform wire is $R=\dfrac{\rho L}{A}$ with $A=\pi\left(\dfrac d2\right)^{2}$.",
  r"$A=\pi(0.20\times10^{-3})^{2}=1.26\times10^{-7}\ \text{m}^{2}$, so $R=\dfrac{1.7\times10^{-8}\times2.0}{1.26\times10^{-7}}=0.27\ \Omega$.",
  0.2706)
# 40
Q(["emf and internal resistance"], "faible", r"A cell of emf $6.0\ \text{V}$ and internal resistance $0.50\ \Omega$ is connected to a resistor so that a current of $1.0\ \text{A}$ flows. The potential difference across the terminals of the cell is",
  r"$5.5\ \text{V}$",
  [(r"$6.0\ \text{V}$", r"gives the emf and ignores the lost volts"), (r"$0.50\ \text{V}$", r"gives the lost volts, $Ir$, instead of the terminal p.d."), (r"$6.5\ \text{V}$", r"adds the lost volts to the emf")],
  r"The terminal potential difference is $V=\mathcal{E}-Ir$.",
  r"$V=6.0-1.0\times0.50=5.5\ \text{V}$.",
  5.5)
# 41
Q(["electric circuits"], "moyenne",
  r"In the circuit in {FIG} the battery of emf $24\ \text{V}$ has negligible internal resistance. It is in series with an ammeter and a $5.0\ \Omega$ resistor, followed by a $12\ \Omega$ resistor and a $4.0\ \Omega$ resistor connected in parallel. What is the potential difference across the $12\ \Omega$ resistor?",
  r"$9.0\ \text{V}$",
  [(r"$15\ \text{V}$", r"gives the potential difference across the $5.0\ \Omega$ resistor"), (r"$24\ \text{V}$", r"gives the emf of the battery"), (r"$3.0\ \text{V}$", r"gives the ammeter reading, in amperes, as a voltage")],
  r"Combine the parallel resistors with $\dfrac{1}{R_p}=\dfrac{1}{R_2}+\dfrac{1}{R_3}$, find the current from the total resistance, then use $V=IR_p$ across the parallel pair.",
  r"$\dfrac{1}{R_p}=\dfrac1{12}+\dfrac14=\dfrac13$, so $R_p=3.0\ \Omega$. The total is $8.0\ \Omega$ and $I=\dfrac{24}{8.0}=3.0\ \text{A}$. Then $V=3.0\times3.0=9.0\ \text{V}$.",
  9.0, fig="circuit")
# 42
Q(["electric circuits", "current electricity"], "elevee",
  r"In {FIG} a $12\ \text{V}$ battery of negligible internal resistance is connected across a $4.0\ \text{k}\Omega$ resistor in series with a $2.0\ \text{k}\Omega$ resistor. A voltmeter of resistance $2.0\ \text{k}\Omega$ is connected across the $2.0\ \text{k}\Omega$ resistor. What does the voltmeter read?",
  r"$2.4\ \text{V}$",
  [(r"$4.0\ \text{V}$", r"treats the voltmeter as ideal, with an infinite resistance"), (r"$6.0\ \text{V}$", r"splits the battery voltage equally because two of the resistances are equal"),
   (r"$8.0\ \text{V}$", r"gives the potential difference across the $4.0\ \text{k}\Omega$ resistor")],
  r"A voltmeter of finite resistance is in parallel with the component it measures and lowers the resistance of that branch. Replace the pair by their equivalent resistance, then share the voltage in proportion to the resistances.",
  r"The voltmeter and the $2.0\ \text{k}\Omega$ resistor in parallel make $1.0\ \text{k}\Omega$. The total is $5.0\ \text{k}\Omega$, so the voltmeter reads $12\times\dfrac{1.0}{5.0}=2.4\ \text{V}$.",
  2.4, fig="diviseur")
# 43
Q(["magnetic fields"], "moyenne",
  r"An electron moving at $2.0\times10^{7}\ \text{m s}^{-1}$ enters a uniform magnetic field of flux density $1.0\ \text{mT}$ at right angles to the field, as in {FIG}. The electron has mass $9.11\times10^{-31}\ \text{kg}$ and charge of magnitude $1.60\times10^{-19}\ \text{C}$. What is the radius of its circular path?",
  r"$0.11\ \text{m}$",
  [(r"$1.1\times10^{-4}\ \text{m}$", r"uses $1.0\ \text{mT}$ as $1.0\ \text{T}$"), (r"$0.23\ \text{m}$", r"gives the diameter of the circle"), (r"$5.7\times10^{-2}\ \text{m}$", r"uses $mv/(2eB)$")],
  r"The magnetic force supplies the centripetal force: $Bqv=\dfrac{mv^{2}}{r}$, so $r=\dfrac{mv}{Bq}$.",
  r"$r=\dfrac{9.11\times10^{-31}\times2.0\times10^{7}}{1.0\times10^{-3}\times1.60\times10^{-19}}=0.114\ \text{m}\approx0.11\ \text{m}$.",
  0.1139, fig="champ")
# 44
Q(["electromagnetic induction"], "moyenne", r"The north pole of a bar magnet is pushed towards one end of a stationary coil that is connected to a sensitive voltmeter. Which statement is correct?",
  r"The induced current makes the end of the coil nearest the magnet a north pole, so a force must be applied to keep the magnet moving.",
  [(r"The induced current makes the end of the coil nearest the magnet a south pole, so the coil pulls the magnet in.", r"gives the induced pole the wrong way round, against Lenz's law"),
   (r"No force acts on the magnet because the coil is stationary and no conductor is moving.", r"overlooks that the flux linkage of the coil changes"),
   (r"The induced emf is zero while the magnet moves at constant speed.", r"confuses constant speed with constant flux linkage")],
  r"Faraday's law gives the size of the induced emf from the rate of change of flux linkage; Lenz's law says the induced current opposes the change that produces it.",
  r"As the north pole approaches, the flux linkage grows. The induced current opposes this by repelling the magnet, which means the near end of the coil becomes a north pole and work must be done to push the magnet on.",
  None, conc=True)
# 45
Q(["electromagnetic induction"], "faible", r"A coil of $200$ turns is linked by a magnetic flux that falls uniformly from $5.0\times10^{-3}\ \text{Wb}$ to $1.0\times10^{-3}\ \text{Wb}$ in $0.020\ \text{s}$. The magnitude of the induced emf is",
  r"$40\ \text{V}$",
  [(r"$0.20\ \text{V}$", r"forgets the number of turns"), (r"$60\ \text{V}$", r"adds the two flux values instead of taking the change"), (r"$10\ \text{V}$", r"uses the final flux instead of the change in flux")],
  r"Faraday's law: $|\mathcal{E}|=N\dfrac{\Delta\Phi}{\Delta t}$.",
  r"$\mathcal{E}=200\times\dfrac{(5.0-1.0)\times10^{-3}}{0.020}=40\ \text{V}$.",
  40.0)
# 46
Q(["alternating current"], "faible", r"A sinusoidal alternating voltage of peak value $100\ \text{V}$ is applied across a $50\ \Omega$ resistor. The mean power dissipated in the resistor is",
  r"$100\ \text{W}$",
  [(r"$200\ \text{W}$", r"uses the peak voltage as if it were a steady voltage, $V_0^{2}/R$"), (r"$141\ \text{W}$", r"divides by $\sqrt2$ once instead of using the square of the r.m.s. voltage"),
   (r"$50\ \text{W}$", r"divides by $2$ twice")],
  r"The r.m.s. voltage is $V_{\text{rms}}=\dfrac{V_0}{\sqrt2}$ and the mean power is $P=\dfrac{V_{\text{rms}}^{2}}{R}=\dfrac{V_0^{2}}{2R}$.",
  r"$P=\dfrac{100^{2}}{2\times50}=100\ \text{W}$.",
  100.0)
# 47
Q(["transformers"], "faible", r"An ideal transformer is connected to a $230\ \text{V}$ supply. The secondary coil delivers a current of $4.0\ \text{A}$ at $12\ \text{V}$. The current in the primary coil is",
  r"$0.21\ \text{A}$",
  [(r"$77\ \text{A}$", r"inverts the ratio of the voltages"), (r"$4.0\ \text{A}$", r"assumes the primary current equals the secondary current"), (r"$0.052\ \text{A}$", r"uses the ratio of voltages and forgets the secondary current")],
  r"For an ideal transformer the power in equals the power out: $I_pV_p=I_sV_s$.",
  r"$I_p=\dfrac{I_sV_s}{V_p}=\dfrac{4.0\times12}{230}=0.21\ \text{A}$.",
  0.2087)
# 48
Q(["photoelectric effect"], "moyenne",
  r"Light of wavelength $400\ \text{nm}$ falls on a metal of work function $2.3\ \text{eV}$. Take $h=6.63\times10^{-34}\ \text{J s}$, $c=3.00\times10^{8}\ \text{m s}^{-1}$ and $1\ \text{eV}=1.60\times10^{-19}\ \text{J}$. The maximum kinetic energy of the emitted photoelectrons is",
  r"$0.81\ \text{eV}$",
  [(r"$5.4\ \text{eV}$", r"adds the work function to the photon energy"), (r"$3.1\ \text{eV}$", r"gives the photon energy and ignores the work function"),
   (r"$1.3\ \text{eV}$", r"quotes the energy in units of $10^{-19}\ \text{J}$ as electronvolts")],
  r"Einstein's equation: $hf=\phi+E_{k,\max}$, with $f=\dfrac{c}{\lambda}$.",
  r"$E=\dfrac{hc}{\lambda}=\dfrac{6.63\times10^{-34}\times3.00\times10^{8}}{400\times10^{-9}}=4.97\times10^{-19}\ \text{J}=3.11\ \text{eV}$. Then $E_{k,\max}=3.11-2.3=0.81\ \text{eV}$.",
  0.808)
# 49
Q(["atomic energy levels"], "moyenne",
  r"{FIG} shows three energy levels of an atom, at $-8.0\ \text{eV}$, $-3.0\ \text{eV}$ and $-1.2\ \text{eV}$. Take $h=6.63\times10^{-34}\ \text{J s}$, $c=3.00\times10^{8}\ \text{m s}^{-1}$ and $1\ \text{eV}=1.60\times10^{-19}\ \text{J}$. "
  r"What is the longest wavelength that the atom can emit in transitions between these three levels?",
  r"$6.9\times10^{-7}\ \text{m}$",
  [(r"$2.5\times10^{-7}\ \text{m}$", r"uses the largest-but-one gap, from $-3.0\ \text{eV}$ to $-8.0\ \text{eV}$"), (r"$1.8\times10^{-7}\ \text{m}$", r"uses the largest gap, from $-1.2\ \text{eV}$ to $-8.0\ \text{eV}$"),
   (r"$4.1\times10^{-7}\ \text{m}$", r"uses the energy of the middle level, $3.0\ \text{eV}$, as the photon energy")],
  r"A photon emitted in a transition carries $\Delta E=hf=\dfrac{hc}{\lambda}$. The longest wavelength comes from the smallest energy gap.",
  r"The smallest gap is $-1.2$ to $-3.0$, that is $1.8\ \text{eV}=2.88\times10^{-19}\ \text{J}$. Then $\lambda=\dfrac{hc}{\Delta E}=\dfrac{1.989\times10^{-25}}{2.88\times10^{-19}}=6.9\times10^{-7}\ \text{m}$.",
  6.906e-7, fig="niveaux")
# 50
Q(["radioactive decay"], "faible",
  r"{FIG} shows the activity of a radioactive sample. The activity is $800\ \text{Bq}$ at time zero and $100\ \text{Bq}$ after $36\ \text{h}$. The half-life of the sample is",
  r"$12\ \text{h}$",
  [(r"$4.5\ \text{h}$", r"divides the time by the ratio of the activities, $8$"), (r"$18\ \text{h}$", r"divides the time by $2$"), (r"$9.0\ \text{h}$", r"counts four values of the activity, $800$, $400$, $200$, $100$, as four half-lives")],
  r"The activity halves in each half-life: $A=A_0\left(\tfrac12\right)^{t/T_{1/2}}$.",
  r"$\dfrac{800}{100}=8=2^{3}$, so three half-lives take $36\ \text{h}$ and $T_{1/2}=\dfrac{36}{3}=12\ \text{h}$.",
  12.0, fig="activite")
