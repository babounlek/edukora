r"""Questions de l'epreuve inedite GCE O Level Physics Paper 1 n.1 (50 QCM). Voir generer_physics_p1.py.

Q(id, themes, difficulte, enonce, bonne option, 3 distracteurs, rappel, resolution, piege, conseil, figure, cle_fixee).
Toutes les chaines sont BRUTES (r"..."): une commande LaTeX a backslash simple dans une chaine ordinaire devient un caractere de controle.
`{FIG}` est remplace par « Figure N ». `cle_fixee` : lettre imposee quand les options designent les panneaux A a D d'une figure.
La plupart des questions sont des calculs : verifier_reponses_physics_p1.py les recalcule a partir des donnees.
Les valeurs : g = 10 m/s^2 quand l'enonce le dit.
"""


def Q(qid, themes, diff, stem, ok, bad, rappel, sol, piege=None, conseil=None, fig=None, cle_fixee=None):
    return dict(id=qid, themes=themes, diff=diff, stem=stem, ok=ok, bad=bad, rappel=rappel, sol=sol, piege=piege,
                conseil=conseil, fig=fig, cle_fixee=cle_fixee)


def questions():
    q = []
    a = q.append

    a(Q("p01", ["measurement"], "faible",
        r"Which of the following is a base SI unit?",
        r"Kilogram.", [r"Newton.", r"Joule.", r"Watt."],
        r"The SI base units for mechanics are the metre, the kilogram and the second; other units, such as the newton, the joule and the watt, are derived from them.",
        r"The kilogram is the base unit of mass. The newton, the joule and the watt are derived units: $\text{N}=\text{kg m/s}^{2}$, $\text{J}=\text{N m}$ and $\text{W}=\text{J/s}$."))
    a(Q("p02", ["measurement"], "moyenne",
        r"The main scale of a micrometer screw gauge reads $2.5\ \text{mm}$ and the thimble reads $34$ divisions, each division being $0.01\ \text{mm}$. The diameter of the wire is",
        r"$2.84\ \text{mm}$", [r"$2.534\ \text{mm}$", r"$0.34\ \text{mm}$", r"$28.4\ \text{mm}$"],
        r"A micrometer reading is the main scale reading plus the thimble reading, where the thimble reading is the number of divisions multiplied by $0.01\ \text{mm}$.",
        r"Thimble reading: $34\times0.01=0.34\ \text{mm}$. Diameter: $2.5+0.34=2.84\ \text{mm}$.",
        piege=r"$34$ divisions of $0.01\ \text{mm}$ make $0.34\ \text{mm}$, not $0.034\ \text{mm}$."))

    a(Q("p03", ["density"], "faible",
        r"A block has a mass of $540\ \text{g}$ and a volume of $200\ \text{cm}^{3}$. Its density is",
        r"$2.7\ \text{g/cm}^{3}$", [r"$0.37\ \text{g/cm}^{3}$", r"$27\ \text{g/cm}^{3}$", r"$340\ \text{g/cm}^{3}$"],
        r"Density is mass divided by volume: $\rho=\dfrac{m}{V}$.",
        r"$\rho=\dfrac{540}{200}=2.7\ \text{g/cm}^{3}$.",
        piege=r"$0.37\ \text{g/cm}^{3}$ comes from dividing the volume by the mass, the inverse of the density."))

    a(Q("p04", ["motion"], "faible",
        r"A car covers a distance of $150\ \text{km}$ in $2.5$ hours. Its average speed is",
        r"$60\ \text{km/h}$", [r"$375\ \text{km/h}$", r"$6\ \text{km/h}$", r"$152.5\ \text{km/h}$"],
        r"Average speed is the total distance divided by the total time taken.",
        r"$\text{speed}=\dfrac{150}{2.5}=60\ \text{km/h}$."))

    a(Q("p05", ["velocity-time graphs"], "moyenne",
        r"{FIG} shows the velocity-time graph of a car. The distance travelled by the car in the first $10\ \text{s}$ is",
        r"$84\ \text{m}$", [r"$120\ \text{m}$", r"$72\ \text{m}$", r"$36\ \text{m}$"],
        r"On a velocity-time graph, the distance travelled is the area between the graph and the time axis.",
        r"From $0$ to $6\ \text{s}$ the area is a triangle: $\dfrac{1}{2}\times6\times12=36\ \text{m}$. From $6$ to $10\ \text{s}$ it is a rectangle: $4\times12=48\ \text{m}$. The total is $36+48=84\ \text{m}$.",
        piege=r"$120\ \text{m}$ is $12\times10$, which assumes the car moved at $12\ \text{m/s}$ for the whole time.",
        fig="vt"))

    a(Q("p06", ["motion"], "faible",
        r"A cyclist increases her velocity from $4\ \text{m/s}$ to $16\ \text{m/s}$ in $3\ \text{s}$. Her acceleration is",
        r"$4\ \text{m/s}^{2}$", [r"$6.7\ \text{m/s}^{2}$", r"$12\ \text{m/s}^{2}$", r"$36\ \text{m/s}^{2}$"],
        r"Acceleration is the change in velocity divided by the time taken: $a=\dfrac{v-u}{t}$.",
        r"$a=\dfrac{16-4}{3}=4\ \text{m/s}^{2}$.",
        piege=r"Subtract the velocities before dividing: $\dfrac{20}{3}\approx6.7$ comes from adding them."))

    a(Q("p07", ["forces and Newton's laws"], "faible",
        r"A resultant force of $30\ \text{N}$ acts on a trolley of mass $6\ \text{kg}$. The acceleration of the trolley is",
        r"$5\ \text{m/s}^{2}$", [r"$180\ \text{m/s}^{2}$", r"$0.2\ \text{m/s}^{2}$", r"$24\ \text{m/s}^{2}$"],
        r"Newton's second law: resultant force $=$ mass $\times$ acceleration, so $a=\dfrac{F}{m}$.",
        r"$a=\dfrac{30}{6}=5\ \text{m/s}^{2}$.",
        piege=r"$0.2\ \text{m/s}^{2}$ is the mass divided by the force."))

    a(Q("p08", ["mass and weight"], "faible",
        r"The gravitational field strength on the Moon is $1.6\ \text{N/kg}$. The weight of a $12\ \text{kg}$ body on the Moon is",
        r"$19.2\ \text{N}$", [r"$120\ \text{N}$", r"$7.5\ \text{N}$", r"$12\ \text{N}$"],
        r"Weight is mass multiplied by the gravitational field strength: $W=mg$.",
        r"$W=12\times1.6=19.2\ \text{N}$. The mass stays $12\ \text{kg}$ everywhere, but the weight depends on $g$.",
        piege=r"$120\ \text{N}$ would be the weight on Earth, where $g=10\ \text{N/kg}$."))

    a(Q("p09", ["linear momentum"], "moyenne",
        r"A trolley of mass $2\ \text{kg}$ moving at $3\ \text{m/s}$ collides with a stationary trolley of mass $1\ \text{kg}$ and the two stick together. Their common velocity is",
        r"$2\ \text{m/s}$", [r"$3\ \text{m/s}$", r"$1\ \text{m/s}$", r"$6\ \text{m/s}$"],
        r"In a collision with no external force, the total momentum before equals the total momentum after.",
        r"Momentum before: $2\times3+1\times0=6\ \text{kg m/s}$. After the collision the total mass is $3\ \text{kg}$, so $3v=6$ and $v=2\ \text{m/s}$."))

    a(Q("p10", ["forces and their effects"], "faible",
        r"Which of the following forces acts without the objects touching each other?",
        r"Gravitational force.", [r"Friction.", r"Tension in a rope.", r"Air resistance."],
        r"Contact forces need the objects to touch, while gravitational, magnetic and electrostatic forces act at a distance.",
        r"The Earth attracts a falling stone without touching it. Friction, tension and air resistance all act through contact."))

    a(Q("p11", ["moments and equilibrium"], "moyenne",
        r"{FIG} shows a uniform metre rule balanced on a pivot at the $50\ \text{cm}$ mark. A weight of $4\ \text{N}$ hangs at the $20\ \text{cm}$ mark. A weight of $6\ \text{N}$ must be hung at which mark for the rule to balance?",
        r"$70\ \text{cm}$", [r"$80\ \text{cm}$", r"$65\ \text{cm}$", r"$60\ \text{cm}$"],
        r"A body is balanced when the sum of the clockwise moments equals the sum of the anticlockwise moments about the pivot, where moment $=$ force $\times$ perpendicular distance.",
        r"Anticlockwise moment of the $4\ \text{N}$ weight: $4\times(50-20)=120\ \text{N cm}$. For the $6\ \text{N}$ weight at distance $d$: $6d=120$, so $d=20\ \text{cm}$ from the pivot, which is the $70\ \text{cm}$ mark.",
        piege=r"The distance $d$ is measured from the pivot, not from the end of the rule: $20\ \text{cm}$ from the pivot is the $70\ \text{cm}$ mark.",
        fig="regle"))

    a(Q("p12", ["elasticity and Hooke's law"], "faible",
        r"A spring extends by $4\ \text{cm}$ when a load of $10\ \text{N}$ is hung from it. Within the elastic limit, a load of $25\ \text{N}$ produces an extension of",
        r"$10\ \text{cm}$", [r"$6.25\ \text{cm}$", r"$100\ \text{cm}$", r"$29\ \text{cm}$"],
        r"Hooke's law: within the elastic limit the extension is directly proportional to the load.",
        r"The load is multiplied by $\dfrac{25}{10}=2.5$, so the extension is $4\times2.5=10\ \text{cm}$."))

    a(Q("p13", ["pressure"], "faible",
        r"A force of $600\ \text{N}$ acts normally on an area of $0.03\ \text{m}^{2}$. The pressure on the surface is",
        r"$20\,000\ \text{Pa}$", [r"$18\ \text{Pa}$", r"$200\ \text{Pa}$", r"$2\,000\ \text{Pa}$"],
        r"Pressure is force divided by the area on which it acts: $P=\dfrac{F}{A}$.",
        r"$P=\dfrac{600}{0.03}=20\,000\ \text{Pa}$.",
        piege=r"$18\ \text{Pa}$ comes from multiplying the force by the area."))

    a(Q("p14", ["pressure in fluids"], "moyenne",
        r"The density of water is $1\,000\ \text{kg/m}^{3}$ and $g=10\ \text{m/s}^{2}$. The pressure due to the water at a depth of $15\ \text{m}$ is",
        r"$1.5\times10^{5}\ \text{Pa}$", [r"$1.5\times10^{4}\ \text{Pa}$", r"$1.5\times10^{3}\ \text{Pa}$", r"$1.5\times10^{6}\ \text{Pa}$"],
        r"The pressure due to a liquid column is $P=h\rho g$, where $h$ is the depth.",
        r"$P=15\times1\,000\times10=150\,000=1.5\times10^{5}\ \text{Pa}$."))

    a(Q("p15", ["simple machines"], "moyenne",
        r"A machine with a velocity ratio of $5$ needs an effort of $50\ \text{N}$ to raise a load of $200\ \text{N}$. Its efficiency is",
        r"$80\%$", [r"$125\%$", r"$20\%$", r"$4\%$"],
        r"Efficiency $=\dfrac{\text{mechanical advantage}}{\text{velocity ratio}}\times100\%$, and mechanical advantage $=\dfrac{\text{load}}{\text{effort}}$.",
        r"Mechanical advantage: $\dfrac{200}{50}=4$. Efficiency: $\dfrac{4}{5}\times100=80\%$.",
        piege=r"An efficiency can never exceed $100\%$: $125\%$ comes from inverting the ratio."))

    a(Q("p16", ["work energy and power"], "faible",
        r"A force of $50\ \text{N}$ moves a body through $4\ \text{m}$ in the direction of the force. The work done is",
        r"$200\ \text{J}$", [r"$12.5\ \text{J}$", r"$54\ \text{J}$", r"$46\ \text{J}$"],
        r"Work done is the force multiplied by the distance moved in the direction of the force.",
        r"$W=50\times4=200\ \text{J}$."))

    a(Q("p17", ["work energy and power"], "moyenne",
        r"A pump raises $200\ \text{kg}$ of water through a height of $6\ \text{m}$ in $20\ \text{s}$. Taking $g=10\ \text{m/s}^{2}$, the power of the pump is",
        r"$600\ \text{W}$", [r"$12\,000\ \text{W}$", r"$60\ \text{W}$", r"$6\,000\ \text{W}$"],
        r"Power is the work done divided by the time taken, and the work done in lifting is $mgh$.",
        r"Work: $200\times10\times6=12\,000\ \text{J}$. Power: $\dfrac{12\,000}{20}=600\ \text{W}$.",
        piege=r"$12\,000$ is the work in joules: it must still be divided by the time."))

    a(Q("p18", ["work energy and power"], "faible",
        r"A body of mass $4\ \text{kg}$ moves at a speed of $5\ \text{m/s}$. Its kinetic energy is",
        r"$50\ \text{J}$", [r"$100\ \text{J}$", r"$10\ \text{J}$", r"$20\ \text{J}$"],
        r"Kinetic energy is $\dfrac{1}{2}mv^{2}$: the speed is squared, and there is a factor $\dfrac{1}{2}$.",
        r"$\text{KE}=\dfrac{1}{2}\times4\times5^{2}=\dfrac{1}{2}\times4\times25=50\ \text{J}$.",
        piege=r"Leaving out the factor $\dfrac{1}{2}$ gives $100\ \text{J}$."))

    a(Q("p19", ["energy conversions"], "faible",
        r"In a hydroelectric power station, the energy changes take place in the order",
        r"Gravitational potential, kinetic, electrical.", [r"Kinetic, gravitational potential, electrical.", r"Electrical, kinetic, gravitational potential.", r"Chemical, kinetic, electrical."],
        r"Follow the energy from its source: water stored high up has gravitational potential energy, flowing water has kinetic energy, and the generator produces electrical energy.",
        r"The water of the dam, high up, has gravitational potential energy. As it falls through the pipes it gains kinetic energy, which turns the turbine and the generator that produces electrical energy."))

    a(Q("p20", ["thermal physics"], "moyenne",
        r"The specific heat capacity of water is $4\,200\ \text{J/kg K}$. The heat needed to raise the temperature of $2\ \text{kg}$ of water from $20\,^{\circ}\text{C}$ to $70\,^{\circ}\text{C}$ is",
        r"$420\,000\ \text{J}$", [r"$168\,000\ \text{J}$", r"$588\,000\ \text{J}$", r"$8\,400\ \text{J}$"],
        r"The heat needed to change the temperature of a body is $Q=mc\Delta\theta$, where $\Delta\theta$ is the change in temperature.",
        r"$\Delta\theta=70-20=50\ \text{K}$, so $Q=2\times4\,200\times50=420\,000\ \text{J}$.",
        piege=r"Use the temperature change, $50\ \text{K}$, not the final temperature $70\,^{\circ}\text{C}$."))

    a(Q("p21", ["change of state"], "moyenne",
        r"The specific latent heat of fusion of ice is $336\,000\ \text{J/kg}$. The energy needed to melt $0.5\ \text{kg}$ of ice at $0\,^{\circ}\text{C}$ is",
        r"$168\,000\ \text{J}$", [r"$672\,000\ \text{J}$", r"$336\,000\ \text{J}$", r"$16\,800\ \text{J}$"],
        r"The energy needed to change the state of a mass $m$ at constant temperature is $Q=ml$.",
        r"$Q=0.5\times336\,000=168\,000\ \text{J}$. The temperature stays at $0\,^{\circ}\text{C}$ while the ice melts.",
        piege=r"$672\,000\ \text{J}$ comes from dividing by the mass, $\dfrac{336\,000}{0.5}$."))

    a(Q("p22", ["thermometers and temperature scales"], "moyenne",
        r"The mercury thread of a thermometer is $4\ \text{cm}$ long at the ice point and $24\ \text{cm}$ long at the steam point. When the thread is $10\ \text{cm}$ long, the temperature is",
        r"$30\,^{\circ}\text{C}$", [r"$40\,^{\circ}\text{C}$", r"$25\,^{\circ}\text{C}$", r"$60\,^{\circ}\text{C}$"],
        r"The temperature is proportional to the length of the thread above the ice point: $\theta=\dfrac{l-l_{0}}{l_{100}-l_{0}}\times100$.",
        r"$\theta=\dfrac{10-4}{24-4}\times100=\dfrac{6}{20}\times100=30\,^{\circ}\text{C}$.",
        piege=r"Subtract the length at the ice point, $4\ \text{cm}$, before dividing: $\dfrac{10}{25}\times100=40$ is wrong."))

    a(Q("p23", ["heat transfer"], "faible",
        r"Which method of heat transfer can take place through a vacuum?",
        r"Radiation.", [r"Conduction.", r"Convection.", r"Evaporation."],
        r"Conduction and convection need particles of matter to carry the heat, while radiation travels as electromagnetic waves.",
        r"The heat of the Sun reaches the Earth through the vacuum of space by radiation."))

    a(Q("p24", ["change of state"], "faible",
        r"{FIG} is a heating curve of a substance that is solid at point A. Between which two points is the substance boiling?",
        r"D and E.", [r"B and C.", r"A and B.", r"E and F."],
        r"During a change of state the temperature stays constant although heat is supplied: the curve is flat, at the melting point for melting and at the boiling point for boiling.",
        r"There are two flat parts. The lower one, B to C at $0\,^{\circ}\text{C}$, is the melting. The upper one, D to E at $100\,^{\circ}\text{C}$, is the boiling.",
        piege=r"B to C is also flat, but at the lower temperature: it shows the solid melting.",
        fig="chauffe"))

    a(Q("p25", ["waves"], "faible",
        r"A wave of frequency $25\ \text{Hz}$ has a wavelength of $12\ \text{m}$. The speed of the wave is",
        r"$300\ \text{m/s}$", [r"$0.48\ \text{m/s}$", r"$37\ \text{m/s}$", r"$2.1\ \text{m/s}$"],
        r"The wave equation is $v=f\lambda$: speed is frequency multiplied by wavelength.",
        r"$v=25\times12=300\ \text{m/s}$."))

    a(Q("p26", ["sound"], "moyenne",
        r"A ship sends an ultrasonic pulse to the sea bed and receives the echo after $0.8\ \text{s}$. The speed of sound in water is $1\,500\ \text{m/s}$. The depth of the sea is",
        r"$600\ \text{m}$", [r"$1\,200\ \text{m}$", r"$300\ \text{m}$", r"$1\,875\ \text{m}$"],
        r"An echo travels to the reflecting surface and back, so the distance to the surface is half of $\text{speed}\times\text{time}$.",
        r"Total distance: $1\,500\times0.8=1\,200\ \text{m}$. The depth is half of it: $600\ \text{m}$.",
        piege=r"$1\,200\ \text{m}$ is the distance there and back: the depth is only half of it."))

    a(Q("p27", ["sound"], "faible",
        r"Sound waves cannot travel through",
        r"A vacuum.", [r"Steel.", r"Water.", r"Air."],
        r"Sound is a mechanical wave: it needs a material medium whose particles vibrate.",
        r"In a vacuum there are no particles to pass on the vibration, so no sound can travel."))

    a(Q("p28", ["electromagnetic spectrum"], "faible",
        r"Which electromagnetic waves are used in the remote control of a television set?",
        r"Infrared waves.", [r"Ultraviolet waves.", r"X-rays.", r"Gamma rays."],
        r"Each part of the electromagnetic spectrum has its uses: radio waves for broadcasting, infrared for heating and remote controls, X-rays for medical images.",
        r"A remote control sends pulses of infrared radiation to the receiver of the television. Ultraviolet waves, X-rays and gamma rays are much more energetic and are not used for this purpose."))

    a(Q("p29", ["light and reflection"], "moyenne",
        r"{FIG} shows a ray of light striking a plane mirror. The angle between the incident ray and the reflected ray is",
        r"$70^{\circ}$", [r"$35^{\circ}$", r"$55^{\circ}$", r"$110^{\circ}$"],
        r"Angles in reflection are measured from the normal, and the angle of reflection equals the angle of incidence.",
        r"The angle of incidence is $35^{\circ}$, so the angle of reflection is also $35^{\circ}$. The angle between the two rays is $35^{\circ}+35^{\circ}=70^{\circ}$.",
        piege=r"$55^{\circ}$ is the angle between the incident ray and the mirror surface, not between the two rays.",
        fig="reflexion"))

    a(Q("p30", ["refraction and lenses"], "moyenne",
        r"An object is placed $30\ \text{cm}$ from a converging lens of focal length $10\ \text{cm}$. The image distance is",
        r"$15\ \text{cm}$", [r"$7.5\ \text{cm}$", r"$20\ \text{cm}$", r"$30\ \text{cm}$"],
        r"For a lens, $\dfrac{1}{f}=\dfrac{1}{u}+\dfrac{1}{v}$, where $u$ is the object distance and $v$ the image distance.",
        r"$\dfrac{1}{v}=\dfrac{1}{10}-\dfrac{1}{30}=\dfrac{3-1}{30}=\dfrac{2}{30}$, so $v=15\ \text{cm}$.",
        piege=r"Subtract the reciprocals before inverting: do not subtract $f-u$ directly."))

    a(Q("p31", ["refraction of light"], "moyenne",
        r"A ray of light enters glass at an angle of incidence of $45^{\circ}$ and is refracted at an angle of $30^{\circ}$. The refractive index of the glass is",
        r"$1.4$", [r"$0.7$", r"$1.5$", r"$0.5$"],
        r"Snell's law: the refractive index is $n=\dfrac{\sin i}{\sin r}$, using the sines of the angles.",
        r"$n=\dfrac{\sin45^{\circ}}{\sin30^{\circ}}=\dfrac{0.707}{0.5}=1.41\approx1.4$.",
        piege=r"Use the sines, not the angles: $\dfrac{45}{30}=1.5$ is wrong, and $0.7$ comes from inverting the ratio."))

    a(Q("p32", ["total internal reflection"], "elevee",
        r"The refractive index of a piece of glass is $1.5$. The critical angle of the glass is closest to",
        r"$42^{\circ}$", [r"$48^{\circ}$", r"$56^{\circ}$", r"$34^{\circ}$"],
        r"The critical angle $c$ satisfies $\sin c=\dfrac{1}{n}$, the light going from the glass into air.",
        r"$\sin c=\dfrac{1}{1.5}=0.667$, so $c=\sin^{-1}(0.667)\approx41.8^{\circ}$, which is closest to $42^{\circ}$.",
        conseil=r"A glass with a higher refractive index has a smaller critical angle: for $n=1.5$ the angle is less than $45^{\circ}$."))

    a(Q("p33", ["electrostatics"], "faible",
        r"Two small charged spheres repel each other. This shows that they carry",
        r"Charges of the same sign.", [r"Charges of opposite signs.", r"No charge at all.", r"One charged sphere and one uncharged sphere."],
        r"Like charges repel each other and unlike charges attract each other, while a charged body can also attract an uncharged one.",
        r"A force of repulsion is only possible between two charges of the same sign, both positive or both negative. A charged sphere only attracts an uncharged one, and opposite charges attract."))

    a(Q("p34", ["current electricity"], "faible",
        r"A current of $3\ \text{A}$ flows through a lamp for $2$ minutes. The charge that passes through the lamp is",
        r"$360\ \text{C}$", [r"$6\ \text{C}$", r"$180\ \text{C}$", r"$40\ \text{C}$"],
        r"Charge is current multiplied by time, $Q=It$, with the time in seconds.",
        r"$2\ \text{minutes}=120\ \text{s}$, so $Q=3\times120=360\ \text{C}$.",
        piege=r"$6\ \text{C}$ comes from using $2$ minutes as $2\ \text{s}$."))

    a(Q("p35", ["current electricity"], "faible",
        r"A potential difference of $12\ \text{V}$ across a resistor produces a current of $0.4\ \text{A}$. The resistance of the resistor is",
        r"$30\ \Omega$", [r"$4.8\ \Omega$", r"$0.033\ \Omega$", r"$12.4\ \Omega$"],
        r"Resistance is the potential difference divided by the current: $R=\dfrac{V}{I}$.",
        r"$R=\dfrac{12}{0.4}=30\ \Omega$."))

    a(Q("p36", ["electric circuits"], "moyenne",
        r"In the circuit of {FIG}, the reading of the ammeter is",
        r"$2\ \text{A}$", [r"$1\ \text{A}$", r"$3\ \text{A}$", r"$12\ \text{A}$"],
        r"For resistors in parallel, $\dfrac{1}{R}=\dfrac{1}{R_{1}}+\dfrac{1}{R_{2}}$; the resistance of the parallel part is then added to the series resistances, and $I=\dfrac{V}{R}$.",
        r"The $6\ \Omega$ and $3\ \Omega$ resistors in parallel: $\dfrac{1}{R}=\dfrac{1}{6}+\dfrac{1}{3}=\dfrac{1}{2}$, so $R=2\ \Omega$. Total resistance: $4+2=6\ \Omega$. Current: $\dfrac{12}{6}=2\ \text{A}$.",
        piege=r"$\dfrac{12}{13}\approx1\ \text{A}$ comes from adding the three resistances as if they were all in series.",
        fig="circuit"))

    a(Q("p37", ["electrical energy and power"], "moyenne",
        r"A lamp rated $60\ \text{W}$ is used for $5$ hours. The energy it uses, in kilowatt-hours, is",
        r"$0.3\ \text{kWh}$", [r"$300\ \text{kWh}$", r"$12\ \text{kWh}$", r"$3\ \text{kWh}$"],
        r"Energy in kilowatt-hours is the power in kilowatts multiplied by the time in hours.",
        r"$60\ \text{W}=0.06\ \text{kW}$, so the energy is $0.06\times5=0.3\ \text{kWh}$.",
        piege=r"$60\times5=300$ is in watt-hours: divide by $1\,000$ to get kilowatt-hours."))

    a(Q("p38", ["domestic electricity"], "faible",
        r"In a domestic electrical circuit, the fuse is placed in the",
        r"Live wire.", [r"Neutral wire.", r"Earth wire.", r"Plug casing."],
        r"A fuse is placed in the live wire so that, when it melts, the appliance is cut off from the high voltage.",
        r"If the fuse were in the neutral wire, the appliance would stay connected to the live wire after the fuse blows, and could still give an electric shock."))

    a(Q("p39", ["electromagnetism"], "faible",
        r"The direction of the force on a current-carrying conductor in a magnetic field is given by",
        r"Fleming's left-hand rule.", [r"Fleming's right-hand rule.", r"Lenz's law.", r"Ohm's law."],
        r"Fleming's left-hand rule is for the motor effect (force on a conductor), and the right-hand rule is for the generator effect (induced current).",
        r"The first finger gives the field, the second finger the current, and the thumb the direction of the force: this is the left-hand rule."))

    a(Q("p40", ["transformers"], "faible",
        r"A transformer has $200$ turns on its primary coil and $50$ turns on its secondary coil. The primary coil is connected to a $240\ \text{V}$ a.c. supply. The voltage across the secondary coil is",
        r"$60\ \text{V}$", [r"$960\ \text{V}$", r"$48\ \text{V}$", r"$190\ \text{V}$"],
        r"For a transformer, $\dfrac{V_{s}}{V_{p}}=\dfrac{N_{s}}{N_{p}}$: the voltage is in the same ratio as the number of turns.",
        r"$V_{s}=240\times\dfrac{50}{200}=60\ \text{V}$. It is a step-down transformer.",
        piege=r"$960\ \text{V}$ comes from inverting the ratio of turns."))

    a(Q("p41", ["magnetism"], "faible",
        r"The core of an electromagnet is made of soft iron because soft iron",
        r"Is easily magnetised and demagnetised.", [r"Is a good conductor of electricity.", r"Keeps its magnetism permanently.", r"Is not attracted by magnets."],
        r"Soft iron gains and loses its magnetism quickly, while steel keeps its magnetism and is used for permanent magnets.",
        r"The magnetism of an electromagnet must switch on and off with the current: soft iron is magnetised when the current flows and loses its magnetism when the current stops."))

    a(Q("p42", ["electronics and semiconductors"], "faible",
        r"A p-type semiconductor is obtained by doping pure silicon with",
        r"A trivalent element such as boron.", [r"A pentavalent element such as phosphorus.", r"A tetravalent element such as carbon.", r"A noble gas such as argon."],
        r"A trivalent impurity (three outer electrons) makes a p-type semiconductor with holes, and a pentavalent impurity (five outer electrons) makes an n-type with free electrons.",
        r"Boron has three outer electrons, one fewer than silicon needs for its bonds, so each boron atom creates a hole: the charge carriers are positive holes."))

    a(Q("p43", ["electronics and semiconductors"], "faible",
        r"A semiconductor diode allows current to flow",
        r"In one direction only.", [r"In both directions equally.", r"Only when it is heated.", r"Only when no voltage is applied."],
        r"A diode has a low resistance in the forward direction and a very high resistance in the reverse direction.",
        r"This one-way property is used to change alternating current to direct current (rectification)."))

    a(Q("p44", ["radioactive decay"], "moyenne",
        r"A radioactive source has a half-life of $6$ hours. The fraction of the original radioactive nuclei left after $24$ hours is",
        r"$\dfrac{1}{16}$", [r"$\dfrac{1}{4}$", r"$\dfrac{1}{8}$", r"$\dfrac{1}{32}$"],
        r"After each half-life the number of undecayed nuclei is halved: after $n$ half-lives the fraction left is $\left(\dfrac{1}{2}\right)^{n}$.",
        r"$24\div6=4$ half-lives, so the fraction left is $\left(\dfrac{1}{2}\right)^{4}=\dfrac{1}{16}$.",
        piege=r"$\dfrac{1}{4}$ is the fraction after $2$ half-lives: count the half-lives first."))

    a(Q("p45", ["atomic and nuclear physics"], "moyenne",
        r"A nucleus of uranium-238, $^{238}_{92}\text{U}$, emits an alpha particle. The daughter nucleus has",
        r"Mass number $234$ and atomic number $90$.", [r"Mass number $234$ and atomic number $92$.", r"Mass number $238$ and atomic number $91$.", r"Mass number $242$ and atomic number $94$."],
        r"An alpha particle is a helium nucleus, $^{4}_{2}\text{He}$: the mass number falls by $4$ and the atomic number falls by $2$.",
        r"Mass number: $238-4=234$. Atomic number: $92-2=90$. The daughter nucleus is thorium-234, $^{234}_{90}\text{Th}$.",
        piege=r"Beta emission, not alpha emission, leaves the mass number unchanged and raises the atomic number by $1$."))

    a(Q("p46", ["atomic and nuclear physics"], "faible",
        r"Which of the following radiations has the greatest penetrating power?",
        r"Gamma rays.", [r"Alpha particles.", r"Beta particles.", r"Visible light."],
        r"The penetrating power of the nuclear radiations increases from alpha particles, to beta particles, to gamma rays.",
        r"Alpha particles are stopped by paper, beta particles by a few millimetres of aluminium, and gamma rays need thick lead or concrete."))

    a(Q("p47", ["atomic and nuclear physics"], "faible",
        r"The number of neutrons in a nucleus of $^{27}_{13}\text{Al}$ is",
        r"$14$", [r"$13$", r"$27$", r"$40$"],
        r"The number of neutrons is the mass number minus the atomic (proton) number: $N=A-Z$.",
        r"$N=27-13=14$.",
        piege=r"$13$ is the number of protons and $27$ is the number of nucleons, protons and neutrons together."))

    a(Q("p48", ["atomic and nuclear physics"], "faible",
        r"Which of the following is a use of gamma rays?",
        r"Sterilising surgical instruments.", [r"Heating food in a microwave oven.", r"Sending radio signals.", r"Detecting forged banknotes."],
        r"Gamma rays are very penetrating and ionising: they kill bacteria and are used in medicine and industry.",
        r"Instruments sealed in their packages are exposed to gamma rays that kill all the germs. Microwaves heat food, radio waves carry signals and ultraviolet light shows forged banknotes."))

    a(Q("p49", ["practical physics"], "moyenne",
        r"A pupil times $20$ complete oscillations of a simple pendulum and finds that they take $36\ \text{s}$. The period of the pendulum is",
        r"$1.8\ \text{s}$", [r"$0.56\ \text{s}$", r"$720\ \text{s}$", r"$16\ \text{s}$"],
        r"The period is the time for one complete oscillation: the total time divided by the number of oscillations.",
        r"$T=\dfrac{36}{20}=1.8\ \text{s}$. Timing many oscillations gives a more accurate period than timing one.",
        piege=r"$0.56\ \text{s}$ is the frequency in hertz, not the period."))

    a(Q("p50", ["graph plotting"], "moyenne",
        r"{FIG} shows four graphs of the force $F$ against the extension for a spring. Which graph shows that the force is directly proportional to the extension?",
        r"C.", [r"A.", r"B.", r"D."],
        r"Two quantities are directly proportional when their graph is a straight line that passes through the origin.",
        r"Graph C is a straight line through the origin. Graph A is a straight line but it does not pass through the origin, graph B is a curve and graph D is horizontal.",
        piege=r"A straight line that does not pass through the origin shows a linear relation, not direct proportionality.",
        fig="graphes", cle_fixee="c"))

    return q
