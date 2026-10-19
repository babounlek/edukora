r"""Questions de l'epreuve inedite GCE O Level Physics Paper 2 n.1 : Section I (6 questions courtes, 40 points, toutes obligatoires) et
Section II (3 questions de 20 points). Le vrai sujet propose, en Section II, « EITHER a, b, c OR d, e, f » pour chaque question : la plateforme
ne code pas ce choix, donc l'inedite ne contient que UN des deux triplets par question (version « answer ALL »).

Chaque sous-question : barème exact (`pts`), grille `crit` (somme = pts), rappel general, resolution, reponse chiffree `ans` quand il y a un
calcul (relue et recalculee par verifier_reponses_physics_p2.py). Chaines BRUTES (voir questions_physics_p1.py). g = 10 m/s^2.
"""


def S(num, text, themes, diff, pts, crit, rappel, sol, ans=None, piege=None, conseil=None, fig=None, fig_enonce=None):
    assert abs(sum(p for _, p in crit) - pts) < 1e-9, (num, text[:40], sum(p for _, p in crit), pts)
    return dict(num=num, text=text, themes=themes, diff=diff, pts=pts, crit=crit, rappel=rappel, sol=sol, ans=ans, piege=piege,
                conseil=conseil, fig=fig, fig_enonce=fig_enonce)


def E(num, groupe, pts, intro, subs):
    assert abs(sum(s["pts"] for s in subs) - pts) < 1e-9, (num, sum(s["pts"] for s in subs), pts)
    return dict(num=num, groupe=groupe, pts=pts, intro=intro, subs=subs)


TABLE_HOOKE = (
    "| Force (N) | 0 | 2 | 4 | 6 | 8 | 10 | 12 |\n|---|---|---|---|---|---|---|---|\n"
    "| Extension (cm) | 0 | 1.0 | 2.1 | 3.0 | 4.1 | 5.0 | 6.2 |"
)


def section_1():
    G = "SECTION I"
    ex = []

    ex.append(E("1", G, 8, r"A machine has a velocity ratio of $6$. It is used to raise a load of $450\ \text{N}$ through a height of $2\ \text{m}$ by applying an effort of $100\ \text{N}$.", [
        S("a", r"Define the efficiency of a machine.", ["simple machines"], "faible", 2,
          [("You state that the efficiency is the ratio of the useful work output to the work input", 1), ("You say that it is expressed as a percentage", 1)],
          r"A definition of a ratio names the two quantities and says which one is divided by which.",
          r"The **efficiency** of a machine is the **ratio of the useful work done by the machine (the work output) to the work put into it (the work input)**, usually written as a percentage: $\text{efficiency}=\dfrac{\text{work output}}{\text{work input}}\times100\%$."),
        S("b", r"Calculate the mechanical advantage of the machine.", ["simple machines"], "faible", 1,
          [("You calculate $\\dfrac{450}{100}=4.5$", 1)],
          r"Mechanical advantage is the load divided by the effort, so it is a ratio of two forces and has no unit.",
          r"$\text{MA}=\dfrac{\text{load}}{\text{effort}}=\dfrac{450}{100}=4.5$.", ans=r"$4.5$"),
        S("c", r"Calculate the work done on the load.", ["work energy and power"], "faible", 2,
          [("You use work done $=$ force $\\times$ distance with the load and the height", 1), ("You obtain $900\\ \\text{J}$", 1)],
          r"The work done in lifting a load is the load (its weight in newtons) multiplied by the height through which it is raised.",
          r"$W=450\times2=900\ \text{J}$.", ans=r"$900\ \text{J}$"),
        S("d", r"Calculate the efficiency of the machine.", ["simple machines"], "moyenne", 2,
          [("You write efficiency $=\\dfrac{\\text{MA}}{\\text{VR}}\\times100\\%$ (or output over input)", 1), ("You obtain $75\\%$", 1)],
          r"Efficiency $=\dfrac{\text{mechanical advantage}}{\text{velocity ratio}}\times100\%$, which equals the work output over the work input.",
          r"$\text{efficiency}=\dfrac{4.5}{6}\times100=75\%$. Check with the work: the effort moves $6\times2=12\ \text{m}$, so the work input is $100\times12=1\,200\ \text{J}$, and $\dfrac{900}{1\,200}\times100=75\%$.",
          ans=r"$75\%$"),
        S("e", r"State one reason why the efficiency of the machine is less than $100\%$.", ["simple machines"], "faible", 1,
          [("You give friction in the moving parts, or the weight of the moving parts of the machine", 1)],
          r"A real machine wastes some of the work put in, because energy is lost as heat or used to move parts of the machine itself.",
          r"Part of the work done by the effort is used to overcome **friction** in the moving parts, which produces heat, and to lift the **moving parts** of the machine, for example the lower pulley. This work is not useful, so the output is less than the input."),
    ]))

    ex.append(E("2", G, 7, r"A uniform seesaw $6\ \text{m}$ long is pivoted at its centre. A boy of weight $400\ \text{N}$ sits $2\ \text{m}$ from the pivot. A girl of weight $320\ \text{N}$ sits on the other side of the pivot, so that the seesaw is balanced and horizontal.", [
        S("a", r"State the principle of moments.", ["moments and equilibrium"], "faible", 2,
          [("You state that for a body in equilibrium the sum of the clockwise moments equals the sum of the anticlockwise moments", 2)],
          r"State a law in one sentence with its condition: the body is in equilibrium, and the moments are about the same point.",
          r"The **principle of moments** states that, for a body in equilibrium, the **sum of the clockwise moments about any point is equal to the sum of the anticlockwise moments about the same point**."),
        S("b", r"Calculate the distance of the girl from the pivot.", ["moments and equilibrium"], "moyenne", 3,
          [("You write the moment of the boy: $400\\times2=800\\ \\text{N m}$", 1), ("You equate it to the moment of the girl: $320\\times d=800$", 1), ("You obtain $d=2.5\\ \\text{m}$", 1)],
          r"A moment is force multiplied by the perpendicular distance from the pivot; at balance the two moments are equal.",
          r"Clockwise moment of the girl equals the anticlockwise moment of the boy: $320\times d=400\times2$, so $d=\dfrac{800}{320}=2.5\ \text{m}$. This is less than $3\ \text{m}$, so she sits on the seesaw.",
          ans=r"$2.5\ \text{m}$"),
        S("c", r"State two conditions that must be satisfied for a body to be in equilibrium.", ["moments and equilibrium"], "faible", 2,
          [("You state that the resultant force on the body is zero", 1), ("You state that the resultant moment about any point is zero", 1)],
          r"A body is in equilibrium when it has neither a resultant force nor a resultant turning effect.",
          r"1. The **resultant force** on the body is **zero** (the forces up balance the forces down, and so on).\n2. The **resultant moment** about any point is **zero**: the clockwise moments equal the anticlockwise moments.".replace("\\n", "\n")),
    ]))

    ex.append(E("3", G, 9, "", [
        S("a", r"A balloon that has been rubbed on a woollen jumper is charged negatively. It sticks to an uncharged wall when it is held against it. Explain why the balloon is attracted by the wall.", ["electrostatics"], "moyenne", 3,
          [("You say that the negative charge of the balloon repels the electrons of the wall surface, so they move away", 1), ("You say that the surface of the wall next to the balloon is left with a positive charge (charge by induction)", 1),
           ("You say that the unlike charges are closer and attract more strongly than the like charges repel, so there is a net attraction", 1)],
          r"A charged body attracts an uncharged one by induction: it separates the charges of the second body, and the nearer charges win.",
          r"The negatively charged balloon **repels the electrons** in the surface of the wall, which move away from it. The surface of the wall nearest to the balloon is therefore left with a **positive charge**: this is **charging by induction**. The positive charges on the wall are **nearer** to the balloon than the negative charges that were pushed away, so the **force of attraction** between unlike charges is **stronger** than the force of repulsion between like charges. The result is a net attraction, and the balloon sticks to the wall."),
        S("b", "Figure 1 shows an electric circuit. Calculate the total resistance of the circuit.", ["electric circuits"], "moyenne", 3,
          [("You find the resistance of the parallel pair: $\\dfrac{1}{R}=\\dfrac{1}{12}+\\dfrac{1}{4}$ so $R=3\\ \\Omega$", 2), ("You add the $5\\ \\Omega$ resistor in series and obtain $8\\ \\Omega$", 1)],
          r"Resistors in parallel combine by $\dfrac{1}{R}=\dfrac{1}{R_{1}}+\dfrac{1}{R_{2}}$, and the result is then added to the resistances in series.",
          r"The $12\ \Omega$ and $4\ \Omega$ resistors are in parallel: $\dfrac{1}{R_{p}}=\dfrac{1}{12}+\dfrac{1}{4}=\dfrac{1}{12}+\dfrac{3}{12}=\dfrac{4}{12}$, so $R_{p}=3\ \Omega$. This pair is in series with the $5\ \Omega$ resistor: $R=5+3=8\ \Omega$.",
          ans=r"$8\ \Omega$", fig_enonce="circuit"),
        S("c", r"Calculate the reading of the ammeter.", ["electric circuits"], "faible", 2,
          [("You use $I=\\dfrac{V}{R}$ with the total resistance", 1), ("You obtain $3\\ \\text{A}$", 1)],
          r"The ammeter is in series with the battery, so it reads the total current, $I=\dfrac{V}{R}$.",
          r"$I=\dfrac{24}{8}=3\ \text{A}$.", ans=r"$3\ \text{A}$"),
        S("d", r"Calculate the potential difference across the $12\ \Omega$ resistor.", ["electric circuits"], "moyenne", 1,
          [("You obtain $9\\ \\text{V}$", 1)],
          r"Resistors in parallel have the same potential difference, equal to the current times the resistance of the parallel pair.",
          r"The potential difference across the parallel pair is $V=IR_{p}=3\times3=9\ \text{V}$. It is the same across the $12\ \Omega$ resistor. Check: the $5\ \Omega$ resistor takes $3\times5=15\ \text{V}$, and $24-15=9\ \text{V}$.",
          ans=r"$9\ \text{V}$"),
    ]))

    ex.append(E("4", G, 5, r"Iodine-131 is a radioactive isotope that is used in medicine. It has a half-life of $8$ days.", [
        S("a", r"Define half-life.", ["radioactive decay"], "faible", 2,
          [("You state that it is the time taken for half of the radioactive nuclei of a sample to decay", 2)],
          r"A definition of half-life names what is halved: the number of undecayed nuclei, or the activity of the sample.",
          r"The **half-life** of a radioactive substance is the **time taken for half of the radioactive nuclei in a sample to decay** (equivalently, the time taken for the activity to fall to half of its value)."),
        S("b", r"A sample contains $80\ \text{g}$ of iodine-131. Calculate the mass of iodine-131 left after $24$ days.", ["radioactive decay"], "moyenne", 3,
          [("You find the number of half-lives: $24\\div8=3$", 1), ("You halve the mass three times: $80\\to40\\to20\\to10$", 1), ("You obtain $10\\ \\text{g}$", 1)],
          r"Divide the time by the half-life to find the number of half-lives, then halve the quantity that number of times.",
          r"$24\div8=3$ half-lives. After $8$ days: $40\ \text{g}$. After $16$ days: $20\ \text{g}$. After $24$ days: $10\ \text{g}$. (Also $80\times\left(\dfrac{1}{2}\right)^{3}=10\ \text{g}$.)",
          ans=r"$10\ \text{g}$"),
    ]))

    ex.append(E("5", G, 6, r"A ray of light passes from air into water. The angle of incidence is $48^{\circ}$ and the angle of refraction is $34^{\circ}$.", [
        S("a", r"State Snell's law.", ["refraction of light"], "faible", 2,
          [("You state that for a ray passing from one medium to another the ratio $\\dfrac{\\sin i}{\\sin r}$ is constant", 2)],
          r"Snell's law links the angles with a ratio of sines that depends only on the two media.",
          r"**Snell's law:** for a ray of light passing from one medium into another, the ratio $\dfrac{\sin i}{\sin r}$ is **constant** ($i$ is the angle of incidence and $r$ the angle of refraction, both measured from the normal). The constant is the refractive index."),
        S("b", r"Calculate the refractive index of water.", ["refraction of light"], "moyenne", 2,
          [("You write $n=\\dfrac{\\sin48^{\\circ}}{\\sin34^{\\circ}}$", 1), ("You obtain $1.33$", 1)],
          r"The refractive index of the second medium is $n=\dfrac{\sin i}{\sin r}$, using the sines of the angles.",
          r"$n=\dfrac{\sin48^{\circ}}{\sin34^{\circ}}=\dfrac{0.743}{0.559}=1.33$.", ans=r"$1.33$"),
        S("c", r"Calculate the critical angle for light travelling from water to air.", ["total internal reflection"], "elevee", 2,
          [("You write $\\sin c=\\dfrac{1}{n}=\\dfrac{1}{1.33}$", 1), ("You obtain $c\\approx49^{\\circ}$", 1)],
          r"The critical angle $c$ satisfies $\sin c=\dfrac{1}{n}$: it is the angle of incidence in the denser medium that gives an angle of refraction of $90^{\circ}$.",
          r"$\sin c=\dfrac{1}{1.33}=0.752$, so $c=\sin^{-1}(0.752)\approx49^{\circ}$.", ans=r"$49^{\circ}$"),
    ]))

    ex.append(E("6", G, 5, r"A student stands $85\ \text{m}$ from a large wall and claps her hands once. The speed of sound in air is $340\ \text{m/s}$.", [
        S("a", r"What is an echo?", ["sound"], "faible", 1,
          [("You say that an echo is sound reflected by a surface and heard again after the original sound", 1)],
          r"An echo is a reflected sound that arrives at least about $0.1\ \text{s}$ after the original sound.",
          r"An **echo** is the sound that is **reflected** by a hard surface, such as a wall, and heard again after the original sound."),
        S("b", r"Calculate the time between the clap and the echo.", ["sound"], "moyenne", 2,
          [("You use the distance there and back, $2\\times85=170\\ \\text{m}$", 1), ("You obtain $\\dfrac{170}{340}=0.5\\ \\text{s}$", 1)],
          r"The sound travels to the wall and back, so the distance covered is twice the distance to the wall; time is distance divided by speed.",
          r"Distance covered by the sound: $2\times85=170\ \text{m}$. Time: $\dfrac{170}{340}=0.5\ \text{s}$.", ans=r"$0.5\ \text{s}$",
          piege=r"The distance there and back is $170\ \text{m}$: using $85\ \text{m}$ gives $0.25\ \text{s}$, which is wrong."),
        S("c", r"State how the speed of sound in air changes when the temperature of the air rises.", ["sound"], "faible", 1,
          [("You state that the speed of sound increases", 1)],
          r"Sound travels faster in warmer air, because the air particles move faster and pass on the vibration more quickly.",
          r"The speed of sound in air **increases** when the temperature rises."),
        S("d", r"Name one use of echoes.", ["sound"], "faible", 1,
          [("You name a use such as sonar, to find the depth of the sea or shoals of fish", 1)],
          r"Echoes are used wherever a distance can be found from the time taken by a reflected pulse.",
          r"**Sonar** (echo-sounding): a ship sends a pulse of ultrasound to the sea bed and measures the time of the echo, which gives the depth of the sea. Echoes are also used to locate shoals of fish and in the ultrasound scanning of the body."),
    ]))
    return ex


def section_2():
    G = "SECTION II"
    ex = []

    ex.append(E("7", G, 20, "A student hung a spiral spring from a stand and added loads to it. The force applied to the spring and the corresponding extension were recorded in the table.\n\n" + TABLE_HOOKE, [
        S("a", r"State Hooke's law.", ["elasticity and Hooke's law"], "faible", 2,
          [("You state that the extension is directly proportional to the force applied", 1), ("You add the condition: provided the elastic limit is not exceeded", 1)],
          r"A law has a statement and its limit of validity: here the elastic limit.",
          r"**Hooke's law:** the extension of a spring (or of an elastic material) is **directly proportional to the force applied to it**, provided the **elastic limit** is not exceeded: $F=ke$."),
        S("b", r"Plot a graph of force (on the vertical axis) against extension (on the horizontal axis), using $1\ \text{cm}$ to represent $1\ \text{cm}$ of extension and $1\ \text{cm}$ to represent $1\ \text{N}$ of force. Draw the line of best fit.", ["graph plotting"], "moyenne", 4,
          [("You label both axes with the quantity and its unit and use the stated scales", 1), ("You plot all seven points accurately", 2), ("You draw a straight line of best fit through the origin and the points", 1)],
          r"In a graph, label the axes with their units, choose the stated scale, plot every point with a small cross, and draw one straight line that passes as close as possible to all the points.",
          r"Draw the horizontal axis from $0$ to $7\ \text{cm}$ and the vertical axis from $0$ to $14\ \text{N}$ with the stated scales, label them 'Extension (cm)' and 'Force (N)', and plot the points $(0,\ 0)$, $(1.0,\ 2)$, $(2.1,\ 4)$, $(3.0,\ 6)$, $(4.1,\ 8)$, $(5.0,\ 10)$ and $(6.2,\ 12)$. The points lie on a straight line through the origin: draw this line with a ruler so that the points are evenly spread on both sides. The expected graph is shown in the figure after part d.",
          ans=None, piege="A line of best fit does not join the points one by one: some points lie slightly above it and some slightly below."),
        S("c", r"Use the graph to calculate the gradient of the line, and state what it represents.", ["elasticity and Hooke's law"], "moyenne", 3,
          [("You choose two points far apart on the line and read the force and the extension", 1), ("You calculate the gradient $\\dfrac{\\Delta F}{\\Delta e}\\approx2.0\\ \\text{N/cm}$, accepting values from $1.9$ to $2.0\\ \\text{N/cm}$", 1),
           ("You state that it is the force constant of the spring, $200\\ \\text{N/m}$", 1)],
          r"The gradient of a force-extension graph is $\dfrac{\Delta F}{\Delta e}$, the force needed per unit of extension: the spring constant.",
          r"Take the origin and a point far along the line, for example $e=6.0\ \text{cm}$ where $F\approx11.8\ \text{N}$ on the line. Gradient $=\dfrac{11.8-0}{6.0-0}\approx1.96\approx2.0\ \text{N/cm}$. In SI units $2.0\ \text{N/cm}=200\ \text{N/m}$. The gradient is the **spring constant** (force constant) $k$: the force needed to produce a unit of extension.",
          ans=r"$\approx2.0\ \text{N/cm}\ (\approx200\ \text{N/m})$"),
        S("d", r"Use the graph to find the load that produces an extension of $3.5\ \text{cm}$.", ["elasticity and Hooke's law"], "faible", 2,
          [("You draw a vertical line at $3.5\\ \\text{cm}$ to the line of best fit and then across to the force axis", 1), ("You read a force of $6.9\\ \\text{N}$, accepting values from $6.8$ to $7.0\\ \\text{N}$", 1)],
          r"To read from a graph, go up from the given value on one axis to the line, then across to the other axis.",
          r"From $3.5\ \text{cm}$ go up to the line of best fit and across to the force axis: $F\approx6.9\ \text{N}$. Check with the gradient: $1.96\times3.5\approx6.9\ \text{N}$.",
          ans=r"$\approx6.9\ \text{N}$", fig="hooke"),
        S("e", r"Define pressure.", ["pressure"], "faible", 2,
          [("You state that pressure is the force acting normally on a surface per unit area", 2)],
          r"Pressure is a force spread over an area: name the force as normal (perpendicular) to the surface.",
          r"**Pressure** is the **force acting normally (perpendicularly) per unit area** of a surface: $P=\dfrac{F}{A}$. Its SI unit is the pascal, $1\ \text{Pa}=1\ \text{N/m}^{2}$."),
        S("f", r"A block of mass $60\ \text{kg}$ rests on a base of area $0.2\ \text{m}^{2}$. Taking $g=10\ \text{m/s}^{2}$, calculate the pressure that the block exerts on the ground.", ["pressure"], "moyenne", 2,
          [("You find the weight $60\\times10=600\\ \\text{N}$", 1), ("You calculate $\\dfrac{600}{0.2}=3\\,000\\ \\text{Pa}$", 1)],
          r"The force of a resting block on the ground is its weight $mg$, and the pressure is this force divided by the area in contact.",
          r"Weight: $W=mg=60\times10=600\ \text{N}$. Pressure: $P=\dfrac{600}{0.2}=3\,000\ \text{Pa}$.", ans=r"$3\,000\ \text{Pa}$",
          piege=r"The force in $P=\dfrac{F}{A}$ is the weight in newtons, not the mass in kilograms."),
        S("g", r"Define density.", ["density"], "faible", 1,
          [("You state that density is the mass per unit volume", 1)],
          r"Density is a ratio: mass divided by volume.",
          r"**Density** is the **mass per unit volume** of a substance: $\rho=\dfrac{m}{V}$."),
        S("h", r"A rectangular block measures $10\ \text{cm}$ by $5\ \text{cm}$ by $4\ \text{cm}$ and has a mass of $780\ \text{g}$. Calculate its density in $\text{g/cm}^{3}$.", ["density"], "moyenne", 3,
          [("You calculate the volume $10\\times5\\times4=200\\ \\text{cm}^{3}$", 1), ("You write $\\rho=\\dfrac{780}{200}$", 1), ("You obtain $3.9\\ \\text{g/cm}^{3}$", 1)],
          r"For a regular solid, find the volume from its dimensions, then divide the mass by the volume.",
          r"Volume: $10\times5\times4=200\ \text{cm}^{3}$. Density: $\rho=\dfrac{780}{200}=3.9\ \text{g/cm}^{3}$ (which is $3\,900\ \text{kg/m}^{3}$).", ans=r"$3.9\ \text{g/cm}^{3}$"),
        S("i", r"The density of water is $1.0\ \text{g/cm}^{3}$. State, with a reason, whether the block will float in water.", ["density"], "faible", 1,
          [("You state that it sinks because its density is greater than that of water", 1)],
          r"A body floats in a liquid when its density is less than the density of the liquid.",
          r"The block will **sink**, because its density, $3.9\ \text{g/cm}^{3}$, is greater than the density of water, $1.0\ \text{g/cm}^{3}$."),
    ]))

    ex.append(E("8", G, 20, "", [
        S("a", r"Define the specific heat capacity of a substance.", ["specific heat capacity"], "faible", 2,
          [("You state that it is the heat needed to raise the temperature of $1\\ \\text{kg}$ of the substance", 1), ("You add by $1\\ \\text{K}$ (or $1\\,^{\\circ}\\text{C}$)", 1)],
          r"A specific quantity is defined per unit mass and per unit temperature change.",
          r"The **specific heat capacity** of a substance is the **quantity of heat needed to raise the temperature of $1\ \text{kg}$ of the substance by $1\ \text{K}$ (or $1\,^{\circ}\text{C}$)**: $c=\dfrac{Q}{m\Delta\theta}$. Its unit is $\text{J/kg K}$."),
        S("b", r"Describe an experiment to measure the specific heat capacity of a metal block using an electrical heater. State the apparatus, the measurements that you take and how you use them.", ["specific heat capacity"], "moyenne", 4,
          [("You name the apparatus: metal block with two holes, immersion heater, thermometer, joulemeter or ammeter, voltmeter and stop-watch, lagging", 1),
           ("You describe the procedure: heater and thermometer in the holes, a little oil for contact, block lagged, heater switched on for a measured time", 1),
           ("You state the measurements: mass of the block, initial and final temperatures, voltage, current and time", 1),
           ("You explain the calculation: $c=\\dfrac{VIt}{m\\Delta\\theta}$", 1)],
          r"In an experiment question, give the apparatus, the steps in order, what is measured, and the formula that turns the measurements into the result.",
          r"**Apparatus:** a metal block of known mass with two holes, an electrical immersion heater, a thermometer, a low-voltage supply, an ammeter, a voltmeter, a stop-watch, a balance and a lagging of cotton wool or felt.\n\n**Method:** find the mass $m$ of the block. Put the heater and the thermometer in the holes with a few drops of oil for good thermal contact, and wrap the block in lagging to reduce the heat lost. Record the initial temperature $\theta_{1}$. Switch on the heater and the stop-watch, and read the voltage $V$ and the current $I$. After a measured time $t$ (for example $5$ minutes) switch off and record the highest temperature $\theta_{2}$.\n\n**Calculation:** the electrical energy supplied is $Q=VIt$ and the rise in temperature is $\Delta\theta=\theta_{2}-\theta_{1}$, so $c=\dfrac{VIt}{m\,\Delta\theta}$. Repeat the experiment and take the mean.".replace("\\n", "\n"),
          piege="A block that is not lagged loses heat to the air, so the value of c obtained is too large."),
        S("c", r"In such an experiment a $1.0\ \text{kg}$ block of aluminium was heated by a $50\ \text{W}$ heater for $5$ minutes. Its temperature rose from $20\,^{\circ}\text{C}$ to $35\,^{\circ}\text{C}$. Assuming no heat is lost, calculate the specific heat capacity of aluminium.", ["specific heat capacity"], "moyenne", 2,
          [("You calculate the energy supplied $50\\times300=15\\,000\\ \\text{J}$", 1), ("You obtain $c=\\dfrac{15\\,000}{1.0\\times15}=1\\,000\\ \\text{J/kg K}$", 1)],
          r"The energy supplied by a heater is its power multiplied by the time in seconds, and then $c=\dfrac{Q}{m\Delta\theta}$.",
          r"Time: $5\times60=300\ \text{s}$. Energy: $Q=Pt=50\times300=15\,000\ \text{J}$. Temperature rise: $35-20=15\ \text{K}$. $c=\dfrac{15\,000}{1.0\times15}=1\,000\ \text{J/kg K}$.",
          ans=r"$1\,000\ \text{J/kg K}$"),
        S("d", r"Differentiate between conduction and radiation.", ["heat transfer"], "faible", 2,
          [("You say that conduction needs a material medium and passes by the vibration of particles and free electrons", 1), ("You say that radiation needs no medium and travels as electromagnetic waves, even through a vacuum", 1)],
          r"To differentiate, state for each term what carries the heat and whether a material is needed.",
          r"**Conduction** is the transfer of heat through a material, mainly a solid, by the vibration of its particles and the movement of free electrons, **without the material moving**; it needs a medium. **Radiation** is the transfer of heat by **infrared electromagnetic waves**; it **needs no medium** and can pass through a vacuum."),
        S("e", r"Explain how a vacuum flask keeps a hot drink hot for a long time.", ["heat transfer"], "moyenne", 4,
          [("You say that the vacuum between the double walls stops heat loss by conduction and convection", 1), ("You say that the silvered surfaces reflect heat radiation back into the liquid", 1),
           ("You say that the glass walls and the stopper are poor conductors, and that the stopper reduces heat loss by convection and evaporation", 1), ("You link each feature to the heat transfer it prevents", 1)],
          r"A flask question is answered by taking the three ways of losing heat in turn, conduction, convection and radiation, and giving the feature that blocks each one.",
          r"The flask has **double glass walls with a vacuum** between them: there are no particles, so heat cannot pass by **conduction or convection**. The surfaces facing the vacuum are **silvered**, so they **reflect** the infrared **radiation** back into the liquid (and a silvered outer wall emits little). Glass is a **poor conductor**, and the **stopper**, made of an insulating material such as cork or plastic, stops heat loss by convection and evaporation at the top."),
        S("f", r"Define the specific latent heat of fusion.", ["change of state"], "faible", 2,
          [("You state that it is the heat needed to change $1\\ \\text{kg}$ of a solid to a liquid", 1), ("You add at its melting point without a change of temperature", 1)],
          r"A latent heat is defined per kilogram and at a constant temperature, during a change of state.",
          r"The **specific latent heat of fusion** is the **quantity of heat needed to change $1\ \text{kg}$ of a solid into a liquid at its melting point, without any change of temperature**: $l=\dfrac{Q}{m}$. Its unit is $\text{J/kg}$."),
        S("g", r"Calculate the energy needed to change $0.2\ \text{kg}$ of ice at $0\,^{\circ}\text{C}$ into water at $25\,^{\circ}\text{C}$. The specific latent heat of fusion of ice is $336\,000\ \text{J/kg}$ and the specific heat capacity of water is $4\,200\ \text{J/kg K}$.", ["change of state"], "moyenne", 4,
          [("You calculate the energy to melt the ice: $0.2\\times336\\,000=67\\,200\\ \\text{J}$", 1), ("You calculate the energy to warm the water: $0.2\\times4\\,200\\times25=21\\,000\\ \\text{J}$", 2), ("You add: $88\\,200\\ \\text{J}$", 1)],
          r"Split the change into two stages, melting at constant temperature then heating the water, and add the two quantities of energy.",
          r"Stage 1, melting: $Q_{1}=ml=0.2\times336\,000=67\,200\ \text{J}$. Stage 2, heating the water from $0\,^{\circ}\text{C}$ to $25\,^{\circ}\text{C}$: $Q_{2}=mc\Delta\theta=0.2\times4\,200\times25=21\,000\ \text{J}$. Total: $Q=67\,200+21\,000=88\,200\ \text{J}$.",
          ans=r"$88\,200\ \text{J}$", piege=r"The melting stage needs no change in temperature: do not multiply $l$ by a temperature."),
    ]))

    ex.append(E("9", G, 20, r"A step-down transformer has $1\,000$ turns on its primary coil and $50$ turns on its secondary coil. The primary coil is connected to a $230\ \text{V}$ a.c. supply and the secondary coil supplies a current of $4\ \text{A}$ to a lamp. Assume that the transformer is $100\%$ efficient.", [
        S("a", r"Calculate the voltage across the secondary coil.", ["transformers"], "faible", 2,
          [("You use $\\dfrac{V_{s}}{V_{p}}=\\dfrac{N_{s}}{N_{p}}$", 1), ("You obtain $11.5\\ \\text{V}$", 1)],
          r"In a transformer the voltages are in the same ratio as the numbers of turns: $\dfrac{V_{s}}{V_{p}}=\dfrac{N_{s}}{N_{p}}$.",
          r"$V_{s}=230\times\dfrac{50}{1\,000}=11.5\ \text{V}$.", ans=r"$11.5\ \text{V}$"),
        S("b", r"Calculate the power delivered by the secondary coil.", ["transformers"], "faible", 2,
          [("You use $P=VI$ with the secondary values", 1), ("You obtain $46\\ \\text{W}$", 1)],
          r"Electrical power is the potential difference multiplied by the current: $P=VI$.",
          r"$P_{s}=V_{s}I_{s}=11.5\times4=46\ \text{W}$.", ans=r"$46\ \text{W}$"),
        S("c", r"Calculate the current in the primary coil.", ["transformers"], "moyenne", 2,
          [("You state that the input power equals the output power for a $100\\%$ efficient transformer", 1), ("You obtain $I_{p}=\\dfrac{46}{230}=0.2\\ \\text{A}$", 1)],
          r"A transformer that is $100\%$ efficient has the same power in the primary and in the secondary, so $V_{p}I_{p}=V_{s}I_{s}$.",
          r"$V_{p}I_{p}=46\ \text{W}$, so $I_{p}=\dfrac{46}{230}=0.2\ \text{A}$. The current is smaller in the coil with more turns.", ans=r"$0.2\ \text{A}$"),
        S("d", r"Explain why a transformer does not work when it is connected to a direct current supply.", ["transformers"], "moyenne", 2,
          [("You say that a transformer works by a changing magnetic field in the core", 1), ("You say that a direct current gives a steady field, so no emf is induced in the secondary", 1)],
          r"A transformer depends on electromagnetic induction, and induction needs a changing magnetic field.",
          r"The primary coil produces a magnetic field in the iron core, and the secondary coil gets an emf **only when this field changes**. A d.c. supply gives a **constant current and a constant magnetic field**, so there is no change of flux in the secondary coil and no emf is induced. An a.c. supply produces a continually changing field."),
        S("e", r"State Faraday's law of electromagnetic induction.", ["electromagnetic induction"], "faible", 2,
          [("You state that the induced emf is proportional to the rate of change of magnetic flux (or the rate of cutting of field lines)", 2)],
          r"Faraday's law links the induced emf to how fast the magnetic flux linked with the circuit changes.",
          r"**Faraday's law:** the **magnitude of the emf induced** in a circuit is **directly proportional to the rate of change of the magnetic flux** linked with the circuit (the rate at which the conductor cuts the magnetic field lines)."),
        S("f", r"Describe how a simple a.c. generator produces an emf, and state two ways of increasing the emf produced.", ["electromagnetic induction"], "moyenne", 4,
          [("You describe a coil rotating between the poles of a magnet", 1), ("You say that the coil cuts the magnetic field lines, so an emf is induced, which changes direction every half turn (a.c.)", 1), ("You state two ways: a faster rotation, more turns, a stronger magnet or a larger coil", 2)],
          r"For a generator, describe the moving part, what it cuts, and why the emf alternates; then name factors that increase the rate of cutting.",
          r"A rectangular **coil** is rotated by a handle or a turbine between the poles of a strong **magnet**. The sides of the coil **cut the magnetic field lines**, so an emf is induced in the coil. The sides move up and then down through the field in successive half turns, so the **emf changes direction every half turn**: the output is alternating. The emf is taken to the circuit through **slip rings and carbon brushes**.\n\nThe emf is increased by: rotating the coil **faster**, using a coil with **more turns**, using a **stronger magnet**, or using a coil with a **larger area**.".replace("\\n", "\n")),
        S("g", r"A kettle is rated $2\ \text{kW}$ and works on a $240\ \text{V}$ supply. Calculate the current that it takes.", ["domestic electricity"], "faible", 2,
          [("You use $I=\\dfrac{P}{V}$ with the power in watts", 1), ("You obtain $8.3\\ \\text{A}$", 1)],
          r"Power is $P=IV$, so the current is $I=\dfrac{P}{V}$, with the power in watts.",
          r"$I=\dfrac{2\,000}{240}=8.33\ \text{A}$.", ans=r"$8.3\ \text{A}$"),
        S("h", r"The kettle is fitted with a plug that has a fuse. Which of the following fuses is the most suitable: $3\ \text{A}$, $5\ \text{A}$ or $13\ \text{A}$? Give a reason.", ["domestic electricity"], "moyenne", 2,
          [("You choose the $13\\ \\text{A}$ fuse", 1), ("You give the reason: its rating is just above the normal current of $8.3\\ \\text{A}$, so the fuse does not melt in normal use but melts if the current becomes too large", 1)],
          r"A fuse must have a rating slightly above the normal working current of the appliance.",
          r"The most suitable fuse is **$13\ \text{A}$**. The kettle takes $8.3\ \text{A}$, so a $3\ \text{A}$ or $5\ \text{A}$ fuse would melt as soon as the kettle was switched on. The $13\ \text{A}$ fuse is the one with the nearest rating **above** the working current: it protects the kettle if a fault makes the current larger."),
        S("i", r"Calculate the cost of using the kettle for $15$ minutes if the cost of electrical energy is $100$ FCFA per kilowatt-hour.", ["electrical energy and power"], "moyenne", 2,
          [("You calculate the energy $2\\ \\text{kW}\\times0.25\\ \\text{h}=0.5\\ \\text{kWh}$", 1), ("You obtain a cost of $50$ FCFA", 1)],
          r"Energy in kilowatt-hours is the power in kilowatts multiplied by the time in hours; the cost is the energy multiplied by the price per kilowatt-hour.",
          r"$15\ \text{min}=0.25\ \text{h}$. Energy: $2\times0.25=0.5\ \text{kWh}$. Cost: $0.5\times100=50$ FCFA.", ans=r"$50$ FCFA"),
    ]))
    return ex
