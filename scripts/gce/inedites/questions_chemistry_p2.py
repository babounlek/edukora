r"""Questions de l'epreuve inedite GCE O Level Chemistry Paper 2 n.1 : Section A (4 questions de 10 points), Section B (2 questions de 20 points,
obligatoires) et Section C (2 questions de 20 points). Le vrai sujet donne 5 questions en A (« best 4 graded »), 2 en B et 3 en C (« ONLY TWO ») :
la plateforme ne code pas ces regles de choix, donc l'inedite ne contient que les questions A TRAITER (version « answer ALL »), soit 4 + 2 + 2.

Chaque sous-question : barème exact (`pts`), grille `crit` (somme = pts), rappel general, resolution, reponse chiffree `ans` quand il y a un
calcul (relue et recalculee par verifier_reponses_chemistry_p2.py). Chaines BRUTES (voir questions_chemistry_p1.py).
Masses atomiques relatives et volume molaire donnes dans l'enonce de chaque calcul. Les figures sont dans figs_chemistry_p2.py.
"""


def S(num, text, themes, diff, pts, crit, rappel, sol, ans=None, piege=None, conseil=None, fig=None, fig_enonce=None):
    assert abs(sum(p for _, p in crit) - pts) < 1e-9, (num, text[:40], sum(p for _, p in crit), pts)
    return dict(num=num, text=text, themes=themes, diff=diff, pts=pts, crit=crit, rappel=rappel, sol=sol, ans=ans, piege=piege,
                conseil=conseil, fig=fig, fig_enonce=fig_enonce)


def E(num, groupe, pts, intro, subs):
    assert abs(sum(s["pts"] for s in subs) - pts) < 1e-9, (num, sum(s["pts"] for s in subs), pts)
    return dict(num=num, groupe=groupe, pts=pts, intro=intro, subs=subs)


TABLE_BURETTE = r"""| | Rough | Titration 1 | Titration 2 | Titration 3 |
|---|---|---|---|---|
| Final burette reading ($\text{cm}^3$) | 25.20 | 25.10 | 24.70 | 25.70 |
| Initial burette reading ($\text{cm}^3$) | 0.00 | 0.50 | 0.20 | 1.00 |
| Volume of acid used ($\text{cm}^3$) | | | | |"""

TABLE_JKL = r"""| Substance | Melting point ($^\circ\text{C}$) | Conducts electricity as a solid | Conducts electricity as a liquid | Other property |
|---|---|---|---|---|
| J | 660 | yes | yes | Can be hammered into thin sheets |
| K | $-7$ | no | no | Evaporates easily; does not dissolve in water |
| L | 1710 | no | no | Very hard; does not dissolve in water |"""

TABLE_TESTS = r"""| Test | Observation |
|---|---|
| **Solid P** (pale green crystals) was dissolved in distilled water to give a pale green solution, which was divided into two portions. | |
| P1: To the first portion, aqueous sodium hydroxide was added drop by drop and then in excess. | A green precipitate formed. It did not dissolve in excess. On standing in air, the precipitate turned brown. |
| P2: To the second portion, barium chloride solution was added, followed by dilute hydrochloric acid. | A white precipitate formed. It did not dissolve in the acid. |
| **Solid Q** (white powder). Q1: Q was heated strongly in a dry test tube. | A colourless gas that turned lime water milky was given off. The residue was yellow while hot and white when cold. |
| Q2: Q was added to dilute nitric acid. | Effervescence; Q dissolved to give a colourless solution, which was divided into two portions. |
| Q3: To the first portion, aqueous sodium hydroxide was added drop by drop and then in excess. | A white precipitate formed. It dissolved in excess to give a colourless solution. |
| Q4: To the second portion, aqueous ammonia was added drop by drop and then in excess. | A white precipitate formed. It dissolved in excess to give a colourless solution. |"""


def section_a():
    G = "SECTION A"
    ex = []

    ex.append(E("1", G, 10, r"Boron exists as two isotopes, $^{10}_{5}\mathrm{B}$ and $^{11}_{5}\mathrm{B}$. In a natural sample of boron, $20\%$ of the atoms are $^{10}_{5}\mathrm{B}$ and $80\%$ are $^{11}_{5}\mathrm{B}$.", [
        S("a", "(i) State the number of protons and the number of neutrons in an atom of $^{10}_{5}\\mathrm{B}$.\n\n(ii) Explain why the two isotopes of boron have the same chemical properties.", ["atomic structure"], "faible", 3,
          [("You state $5$ protons", 1), ("You state $5$ neutrons ($10-5$)", 1), ("You explain that the isotopes have the same number of electrons, so the same outer electrons which decide the chemical properties", 1)],
          r"The atomic number is the number of protons and the mass number is the number of protons plus neutrons. Chemical properties depend on the electrons, mainly the outer ones.",
          "(i) The atomic number is $5$, so there are **5 protons**. The number of neutrons is the mass number minus the atomic number: $10-5=$ **5 neutrons**.\n\n(ii) Both isotopes have $5$ protons, so a neutral atom of either has **5 electrons** with the same arrangement, $2, 3$. Chemical reactions involve the outer electrons, so the isotopes react in the same way. They differ only in the number of neutrons, which affects the mass and not the chemistry."),
        S("b", r"Calculate the relative atomic mass of boron in this sample. Show your working.", ["atomic structure", "mole concept"], "moyenne", 3,
          [("You use the abundances: $0.20\\times10$ and $0.80\\times11$", 1), ("You add the two contributions: $2.0+8.8$", 1), ("You obtain $10.8$", 1)],
          r"The relative atomic mass is the average of the mass numbers of the isotopes, weighted by their percentages.",
          r"$$\text{RAM}=\frac{(20\times10)+(80\times11)}{100}=\frac{200+880}{100}=\frac{1080}{100}=10.8$$ The relative atomic mass of boron is **10.8**, closer to $11$ because most atoms are $^{11}\mathrm{B}$.",
          ans=r"$10.8$", piege=r"The answer must lie between $10$ and $11$, and nearer $11$ because $80\%$ of the atoms are $^{11}\mathrm{B}$; $10.5$ would be the simple mean."),
        S("c", "An element D has the electronic configuration $2, 8, 3$.\n\n(i) State the group and the period of the Periodic Table to which D belongs.\n\n(ii) Write the formula of the ion formed by D and give its electronic configuration.\n\n(iii) The oxide of D reacts with both dilute hydrochloric acid and sodium hydroxide solution. What name is given to an oxide with this behaviour?",
          ["periodic table", "atomic structure"], "faible", 4,
          [("You state Group III and Period 3", 1), ("You write $\\mathrm{D^{3+}}$", 1), ("You give the configuration $2, 8$", 1), ("You name it an amphoteric oxide", 1)],
          r"The number of outer electrons gives the group and the number of occupied shells gives the period. A metal atom loses its outer electrons to form a positive ion.",
          r"(i) There are $3$ electrons in the outer shell, so D is in **Group III**; there are $3$ occupied shells, so it is in **Period 3**.\n\n(ii) D loses its three outer electrons to form **$\mathrm{D^{3+}}$** with the configuration **$2, 8$**.\n\n(iii) An oxide that reacts with both acids and alkalis is **amphoteric**.".replace("\\n", "\n")),
    ]))

    ex.append(E("2", G, 10, r"Ammonia is manufactured by the Haber process: $$\mathrm{N_2(g)+3H_2(g)\rightleftharpoons2NH_3(g)}\qquad\Delta H=-92\ \text{kJ/mol}$$", [
        S("a", r"State where the nitrogen and the hydrogen used in the process come from.", ["non-metals and their compounds"], "faible", 2,
          [("You state that nitrogen comes from the air, by fractional distillation of liquid air", 1), ("You state that hydrogen comes from natural gas (methane) reacting with steam, or from petroleum", 1)],
          r"The raw materials of an industrial process are cheap and plentiful: air is the source of nitrogen and natural gas is the usual source of hydrogen.",
          r"**Nitrogen** is obtained from the **air** (about $78\%$ nitrogen) by fractional distillation of liquid air. **Hydrogen** is obtained from **natural gas** (mainly methane), which reacts with steam: $\mathrm{CH_4+H_2O\rightarrow CO+3H_2}$ (it can also be obtained from petroleum fractions)."),
        S("b", "(i) Name the catalyst used.\n\n(ii) State the temperature and the pressure used in the process.\n\n(iii) Explain why a high pressure is used.", ["chemical equilibrium", "non-metals and their compounds"], "faible", 3,
          [("You name iron as the catalyst", 1), ("You give about $450\\,^\\circ\\text{C}$ (accept $400$ to $500\\,^\\circ\\text{C}$) and about $200$ atm (accept $150$ to $300$ atm)", 1),
           ("You explain that $4$ moles of gas form $2$ moles of gas, so a high pressure moves the equilibrium to the right and raises the yield", 1)],
          r"By Le Chatelier's principle an increase in pressure favours the side of the equation with fewer moles of gas.",
          r"(i) **Iron**.\n\n(ii) About **$450\,^\circ\text{C}$** and about **$200$ atmospheres**.\n\n(iii) The forward reaction changes $1+3=4$ moles of gas into $2$ moles of gas. A high pressure favours the side with fewer gas molecules, so the equilibrium moves to the right and more ammonia is formed. The rate is also higher.".replace("\\n", "\n"),
          piege=r"The catalyst does not change the yield; it only makes equilibrium arrive sooner."),
        S("c", r"Explain why a temperature of about $450\,^\circ\text{C}$ is used rather than a much lower or a much higher temperature.", ["chemical equilibrium", "rates of reaction"], "moyenne", 3,
          [("You say that a lower temperature gives a higher yield, because the forward reaction is exothermic, but the rate is too slow", 1),
           ("You say that a higher temperature gives a faster rate but a lower yield", 1), ("You conclude that $450\\,^\\circ\\text{C}$ is a compromise between an acceptable rate and an acceptable yield", 1)],
          r"For an exothermic reaction, a low temperature favours the products at equilibrium, but all reactions are slow when the temperature is low.",
          r"The forward reaction is **exothermic** ($\Delta H$ is negative), so a **low** temperature would give a **high yield** of ammonia. But at a low temperature the particles have less energy and the reaction is **too slow** to be useful. A **much higher** temperature would give a fast rate, but the equilibrium would move to the left and the **yield would be very low**. About $450\,^\circ\text{C}$ is a **compromise** that gives an acceptable rate and an acceptable yield."),
        S("d", r"$600\ \text{cm}^3$ of hydrogen react completely with nitrogen. Calculate the volume of ammonia formed, measured under the same conditions.", ["stoichiometry"], "faible", 2,
          [("You use the ratio $\\mathrm{H_2}:\\mathrm{NH_3}=3:2$", 1), ("You obtain $400\\ \\text{cm}^3$", 1)],
          r"Gas volumes measured under the same conditions are in the same ratio as the moles in the equation.",
          r"$3$ volumes of hydrogen give $2$ volumes of ammonia, so $V(\mathrm{NH_3})=600\times\dfrac{2}{3}=400\ \text{cm}^3$.", ans=r"$400\ \text{cm}^3$"),
    ]))

    ex.append(E("3", G, 10, "Copper is purified by electrolysis. The anode is a block of impure copper, the cathode is a thin sheet of pure copper, and the electrolyte is copper(II) sulphate solution.", [
        S("a", r"State which electrode is connected to the positive terminal of the supply and what happens to this electrode.", ["electrolysis"], "faible", 2,
          [("You state that it is the anode, the block of impure copper", 1), ("You state that it dissolves, because copper atoms change into copper(II) ions", 1)],
          r"The electrode connected to the positive terminal is the anode. In this process the anode is made of the metal that is being purified.",
          r"The **impure copper anode** is connected to the positive terminal. It **dissolves** (becomes smaller): copper atoms lose electrons and go into the solution as copper(II) ions."),
        S("b", r"Write the half-equation for the reaction at (i) the anode and (ii) the cathode, and state whether each reaction is oxidation or reduction.", ["electrolysis", "redox reactions"], "faible", 3,
          [("Anode: $\\mathrm{Cu\\rightarrow Cu^{2+}+2e^-}$", 1), ("Cathode: $\\mathrm{Cu^{2+}+2e^-\\rightarrow Cu}$", 1), ("Anode is oxidation and cathode is reduction", 1)],
          r"Oxidation is loss of electrons and takes place at the anode; reduction is gain of electrons and takes place at the cathode.",
          r"(i) Anode: $\mathrm{Cu(s)\rightarrow Cu^{2+}(aq)+2e^-}$, **oxidation** (electrons are lost).\n\n(ii) Cathode: $\mathrm{Cu^{2+}(aq)+2e^-\rightarrow Cu(s)}$, **reduction** (electrons are gained).".replace("\\n", "\n")),
        S("c", r"A current of $2.0\ \text{A}$ flows for $30$ minutes. Calculate the mass of copper deposited on the cathode. (Cu = 64; $1$ mole of electrons carries $96000\ \text{C}$)", ["electrolysis", "mole concept"], "moyenne", 3,
          [("You calculate the charge: $2.0\\times30\\times60=3600\\ \\text{C}$", 1), ("You calculate the moles of copper: $\\dfrac{3600}{96000}\\div2=0.01875\\ \\text{mol}$", 1), ("You obtain $1.2\\ \\text{g}$", 1)],
          r"Charge (coulombs) $=$ current (amperes) $\times$ time (seconds). The moles of electrons are the charge divided by $96000$, and copper(II) needs two electrons per atom.",
          r"$Q=It=2.0\times(30\times60)=3600\ \text{C}$. Moles of electrons $=\dfrac{3600}{96000}=0.0375\ \text{mol}$. Each copper atom needs $2$ electrons, so $n(\mathrm{Cu})=\dfrac{0.0375}{2}=0.01875\ \text{mol}$. Mass $=0.01875\times64=1.2\ \text{g}$.",
          ans=r"$1.2\ \text{g}$", piege=r"The time must be converted to seconds ($1800\ \text{s}$), and the moles of electrons divided by $2$."),
        S("d", r"State and explain what happens to the concentration of copper(II) ions in the electrolyte during the electrolysis.", ["electrolysis"], "moyenne", 2,
          [("You state that the concentration stays constant", 1), ("You explain that the copper(II) ions removed at the cathode are replaced by the copper that dissolves from the anode at the same rate", 1)],
          r"In the purification of copper the same number of electrons is exchanged at both electrodes, so the number of ions removed equals the number of ions formed.",
          r"The concentration **stays the same**, so the blue colour of the solution does not fade. For every copper(II) ion that is deposited as copper at the cathode, one copper atom from the anode dissolves as a copper(II) ion, and the two changes happen at the same rate."),
    ]))

    ex.append(E("4", G, 10, "The table gives some properties of three substances J, K and L.\n\n" + TABLE_JKL, [
        S("a", "Hydrogen chloride is formed when hydrogen reacts with chlorine.\n\n(i) State the type of bond in hydrogen chloride.\n\n(ii) Describe how the bond is formed, in terms of the outer electrons of the two atoms.", ["chemical bonding"], "faible", 3,
          [("You state that the bond is covalent", 1), ("You state that a hydrogen atom has $1$ outer electron and a chlorine atom has $7$", 1), ("You explain that each atom gives one electron to a shared pair, so that each atom has a full outer shell", 1)],
          r"A covalent bond forms between two non-metal atoms that share a pair of electrons so that each reaches a stable outer shell.",
          r"(i) The bond is **covalent**.\n\n(ii) A hydrogen atom has $1$ outer electron and a chlorine atom has $7$. Each atom contributes **one electron to a shared pair**. Hydrogen then has $2$ electrons in its shell (a full first shell) and chlorine has $8$ (a full outer shell).".replace("\\n", "\n")),
        S("b", "State the type of structure of each of J, K and L, choosing from: giant metallic, simple molecular, giant covalent.", ["chemical bonding"], "faible", 3,
          [("J is giant metallic", 1), ("K is simple molecular", 1), ("L is giant covalent", 1)],
          r"A metal conducts as a solid and as a liquid and can be hammered. Simple molecular substances have low melting points. A giant covalent substance has a very high melting point and does not conduct.",
          r"**J: giant metallic** (it conducts as a solid and as a liquid, and can be hammered into sheets). **K: simple molecular** (a low melting point of $-7\,^\circ\text{C}$, and it evaporates easily). **L: giant covalent** (a very high melting point, very hard, and no conduction)."),
        S("c", "(i) Explain why J conducts electricity as a solid.\n\n(ii) Explain why K has a low melting point.\n\n(iii) Explain why L has a very high melting point.", ["chemical bonding"], "moyenne", 4,
          [("(i) You say that J has delocalised electrons that are free to move through the metal", 1), ("(ii) You say that the forces between the molecules of K are weak and need little energy to overcome", 1),
           ("(iii) You say that L is a giant lattice of atoms joined by strong covalent bonds", 1), ("(iii) You say that a lot of energy is needed to break these bonds", 1)],
          r"Melting a simple molecular substance only needs the weak forces between molecules to be overcome; melting a giant covalent substance means breaking strong bonds throughout the lattice.",
          r"(i) In a metal the outer electrons are **delocalised**: they move freely through the lattice of positive ions and carry the current, even in the solid.\n\n(ii) K is made of separate molecules. The **forces between the molecules are weak**, so little energy is needed to separate them. The covalent bonds inside each molecule are not broken.\n\n(iii) L is a **giant lattice of atoms joined by strong covalent bonds** in all directions. **A great deal of energy** is needed to break so many strong bonds.".replace("\\n", "\n")),
    ]))
    return ex


def section_b():
    G = "SECTION B"
    ex = []

    ex.append(E("5", G, 20, r"A student titrated $25.0\ \text{cm}^3$ portions of potassium hydroxide solution with hydrochloric acid of concentration $0.100\ \text{mol/dm}^3$, using methyl orange as indicator. The burette readings are in the table." + "\n\n" + TABLE_BURETTE, [
        S("a", "(i) Name the piece of apparatus used to measure $25.0\\ \\text{cm}^3$ of the potassium hydroxide solution accurately.\n\n(ii) Name the piece of apparatus used to add the acid.\n\n(iii) State the colour change of methyl orange at the end-point.", ["apparatus and experiments", "acids bases and salts"], "faible", 3,
          [("You name the pipette", 1), ("You name the burette", 1), ("You state that methyl orange changes from yellow to orange (or red)", 1)],
          r"A fixed volume is measured with a pipette; a variable volume is delivered from a burette. An indicator is chosen for its colour in the alkali and in the acid.",
          r"(i) A **pipette** (with a pipette filler).\n\n(ii) A **burette**.\n\n(iii) Methyl orange is **yellow** in the alkali and turns **orange** (red in excess acid) at the end-point.".replace("\\n", "\n")),
        S("b", "(i) Complete the last row of the table.\n\n(ii) Explain why the rough titration is not used to calculate the mean volume.\n\n(iii) Calculate the mean volume of acid used.", ["apparatus and experiments", "acids bases and salts"], "moyenne", 4,
          [("You calculate the four volumes: $25.20$, $24.60$, $24.50$ and $24.70\\ \\text{cm}^3$", 1), ("You explain that the rough titration finds the approximate end-point and the acid is added quickly, so it is not accurate", 1),
           ("You use the three accurate titres, $24.60$, $24.50$ and $24.70$", 1), ("You obtain $24.60\\ \\text{cm}^3$", 1)],
          r"The volume of acid used is the final reading minus the initial reading. The mean is calculated only from titres that agree closely (concordant results).",
          "(i) Volume $=$ final $-$ initial: rough $25.20-0.00=25.20$; titration 1: $25.10-0.50=24.60$; titration 2: $24.70-0.20=24.50$; titration 3: $25.70-1.00=24.70$ (all in $\\text{cm}^3$).\n\n(ii) The rough titration is done quickly to find roughly where the end-point is; the acid is added fast and the end-point is overshot, so the volume is too large and not accurate. It is also not within $0.20\\ \\text{cm}^3$ of the others.\n\n(iii) $\\text{mean}=\\dfrac{24.60+24.50+24.70}{3}=24.60\\ \\text{cm}^3$.",
          ans=r"$24.60\ \text{cm}^3$"),
        S("c", "Calculate:\n\n(i) the number of moles of hydrochloric acid used in the mean titration;\n\n(ii) the number of moles of potassium hydroxide in $25.0\\ \\text{cm}^3$ of solution;\n\n(iii) the concentration of the potassium hydroxide solution in $\\text{mol/dm}^3$.", ["mole concept", "acids bases and salts"], "moyenne", 4,
          [("You calculate $n(\\mathrm{HCl})=0.100\\times\\dfrac{24.60}{1000}=2.46\\times10^{-3}\\ \\text{mol}$", 1), ("You use the $1:1$ ratio of the equation to find the same number of moles of KOH", 1),
           ("You divide by the volume: $\\dfrac{2.46\\times10^{-3}}{0.0250}$", 1), ("You obtain $0.0984\\ \\text{mol/dm}^3$", 1)],
          r"Moles $=$ concentration $\times$ volume in $\text{dm}^3$. The equation ratio links the moles of acid and alkali, and concentration is moles divided by volume.",
          r"(i) $n(\mathrm{HCl})=0.100\times\dfrac{24.60}{1000}=2.46\times10^{-3}\ \text{mol}$.\n\n(ii) $\mathrm{KOH+HCl\rightarrow KCl+H_2O}$, a $1:1$ ratio, so $n(\mathrm{KOH})=2.46\times10^{-3}\ \text{mol}$.\n\n(iii) $c(\mathrm{KOH})=\dfrac{2.46\times10^{-3}}{25.0/1000}=0.0984\ \text{mol/dm}^3$.".replace("\\n", "\n"),
          ans=r"$0.0984\ \text{mol/dm}^3$", piege=r"The volumes must be changed to $\text{dm}^3$ (divide by $1000$) before they are used with a concentration in $\text{mol/dm}^3$."),
        S("d", "(i) Write the equation for the reaction between potassium hydroxide and hydrochloric acid.\n\n(ii) Describe how pure, dry crystals of potassium chloride could be obtained from these two solutions.", ["acids bases and salts", "apparatus and experiments"], "faible", 4,
          [("You write $\\mathrm{KOH+HCl\\rightarrow KCl+H_2O}$", 1), ("You repeat the titration without the indicator, using the mean volume of acid", 1),
           ("You evaporate the solution to about one third of its volume (the point of crystallisation) and leave it to cool", 1), ("You filter off the crystals, wash them with a little cold distilled water and dry them", 1)],
          r"A soluble salt is made by neutralisation, and the indicator is left out so that the crystals are pure. The crystals are obtained by partial evaporation and cooling.",
          r"(i) $\mathrm{KOH(aq)+HCl(aq)\rightarrow KCl(aq)+H_2O(l)}$.\n\n(ii) Measure $25.0\ \text{cm}^3$ of the alkali into a flask and add exactly $24.60\ \text{cm}^3$ of the acid **without indicator**. Evaporate the solution to about one third of its volume, then leave it to cool so that crystals form. **Filter** off the crystals, wash them with a little cold distilled water and **dry** them between filter papers.".replace("\\n", "\n")),
        S("e", r"In a second experiment the pH of the mixture was recorded as the acid was added to $25.0\ \text{cm}^3$ of the same potassium hydroxide solution. The results are shown in {FIG}." + "\n\n(i) State the pH of the potassium hydroxide solution before any acid is added.\n\n(ii) State the pH of the solution at the end-point.\n\n(iii) Use {FIG} to find the volume of acid at which the pH changes suddenly. How does it compare with your answer to part (b)?",
          ["acids bases and salts", "graphs"], "moyenne", 3,
          [("You read a pH of $13$", 1), ("You state that the pH at the end-point is $7$ (neutral)", 1), ("You read about $24.6\\ \\text{cm}^3$ (accept $24$ to $25\\ \\text{cm}^3$), which agrees with the mean titre", 1)],
          r"A graph of pH against volume of acid has a very steep part at the end-point of a strong acid-strong alkali titration; the pH there is $7$.",
          r"(i) The curve starts at **pH $13$** (a strong alkali).\n\n(ii) At the end-point, when the acid has exactly neutralised the alkali, the pH is **$7$**.\n\n(iii) The pH falls suddenly at about **$24.6\ \text{cm}^3$**, which agrees with the mean titre of $24.60\ \text{cm}^3$ obtained in part (b).".replace("\\n", "\n"),
          fig_enonce="ph"),
        S("f", "State two precautions that the student should take in order to obtain accurate results in a titration.", ["apparatus and experiments"], "faible", 2,
          [("You state a first correct precaution", 1), ("You state a second correct precaution", 1)],
          r"Accurate titrations need clean, correctly filled apparatus, careful reading of the burette and a slow approach to the end-point.",
          r"Any two of: rinse the burette with the acid before filling it; fill the jet of the burette and remove the funnel; read the bottom of the meniscus at eye level; place a white tile under the flask to see the colour change; swirl the flask while adding the acid; add the acid drop by drop near the end-point; repeat until two results agree within $0.20\ \text{cm}^3$."),
    ]))

    ex.append(E("6", G, 20, "Two solids P and Q were examined. The tests and the observations are in the table.\n\n" + TABLE_TESTS, [
        S("a", "Using tests P1 and P2:\n\n(i) Identify the cation in P and state the observation that shows it.\n\n(ii) Write the ionic equation for the formation of the precipitate in P1.\n\n(iii) Identify the anion in P and write the ionic equation for the formation of the precipitate in P2.\n\n(iv) Name P.", ["qualitative analysis"], "moyenne", 5,
          [("You identify $\\mathrm{Fe^{2+}}$ from the green precipitate that turns brown", 1), ("You write $\\mathrm{Fe^{2+}+2OH^-\\rightarrow Fe(OH)_2}$", 1), ("You identify the sulphate ion", 1),
           ("You write $\\mathrm{Ba^{2+}+SO_4^{2-}\\rightarrow BaSO_4}$", 1), ("You name P as iron(II) sulphate", 1)],
          r"A green precipitate with aqueous sodium hydroxide that turns brown in air shows iron(II) ions. A white precipitate with barium ions that is not dissolved by acid shows sulphate ions.",
          r"(i) The cation is **iron(II), $\mathrm{Fe^{2+}}$**: sodium hydroxide gives a **green precipitate that does not dissolve in excess and turns brown on standing**, because iron(II) hydroxide is oxidised to iron(III) hydroxide.\n\n(ii) $\mathrm{Fe^{2+}(aq)+2OH^-(aq)\rightarrow Fe(OH)_2(s)}$.\n\n(iii) The anion is **sulphate, $\mathrm{SO_4^{2-}}$**: barium chloride gives a white precipitate that does not dissolve in dilute hydrochloric acid (barium carbonate and barium sulphite would dissolve). $\mathrm{Ba^{2+}(aq)+SO_4^{2-}(aq)\rightarrow BaSO_4(s)}$.\n\n(iv) P is **iron(II) sulphate**, $\mathrm{FeSO_4}$.".replace("\\n", "\n")),
        S("b", "Using tests Q1 to Q4:\n\n(i) Identify the gas given off in Q1 and the anion in Q.\n\n(ii) What does the colour of the residue in Q1 suggest about the cation in Q?\n\n(iii) Tests Q3 and Q4 together identify the cation in Q. Name this cation and explain why test Q3 alone is not enough to identify it.\n\n(iv) Name Q and write the equation for the reaction in Q1.", ["qualitative analysis"], "elevee", 6,
          [("You identify the gas as carbon dioxide", 1), ("You identify the anion as carbonate", 1), ("You say the residue, yellow when hot and white when cold, is zinc oxide, which suggests zinc", 1),
           ("You identify the cation as $\\mathrm{Zn^{2+}}$ and say that Q3 alone is not enough, because aluminium ions also give a white precipitate that dissolves in excess sodium hydroxide", 1), ("You say that in Q4 the precipitate of aluminium hydroxide would NOT dissolve in excess ammonia, while that of zinc dissolves", 1),
           ("You name Q as zinc carbonate and write $\\mathrm{ZnCO_3\\rightarrow ZnO+CO_2}$", 1)],
          r"Carbonates give carbon dioxide with acids and on strong heating. Zinc hydroxide dissolves in excess sodium hydroxide and in excess ammonia; aluminium hydroxide dissolves only in excess sodium hydroxide.",
          r"(i) The gas that turns lime water milky is **carbon dioxide**, so the anion is the **carbonate ion, $\mathrm{CO_3^{2-}}$** (effervescence with dilute nitric acid confirms it).\n\n(ii) Zinc oxide is **yellow when hot and white when cold**, so the residue suggests that Q contains **zinc**.\n\n(iii) The cation is the **zinc ion, $\mathrm{Zn^{2+}}$**. Aluminium ions also give a white precipitate with sodium hydroxide that dissolves in excess, so Q3 does not separate $\mathrm{Zn^{2+}}$ from $\mathrm{Al^{3+}}$. In Q4 the precipitate **dissolves in excess ammonia**: aluminium hydroxide does not dissolve in excess ammonia, so the cation is $\mathrm{Zn^{2+}}$.\n\n(iv) Q is **zinc carbonate**: $\mathrm{ZnCO_3(s)\rightarrow ZnO(s)+CO_2(g)}$.".replace("\\n", "\n")),
        S("c", "Ammonium chloride was warmed with sodium hydroxide solution and a gas R was given off.\n\n(i) Name R.\n\n(ii) Describe two tests that identify R, and state the result of each.\n\n(iii) Write the ionic equation for the formation of R.", ["qualitative analysis", "non-metals and their compounds"], "faible", 4,
          [("You name R as ammonia", 1), ("You state that damp red litmus paper turns blue", 1), ("You state that a rod dipped in concentrated hydrochloric acid gives dense white fumes", 1), ("You write $\\mathrm{NH_4^++OH^-\\rightarrow NH_3+H_2O}$", 1)],
          r"Ammonium salts release ammonia when warmed with a strong alkali. Ammonia is the only common alkaline gas.",
          r"(i) R is **ammonia, $\mathrm{NH_3}$**.\n\n(ii) Test 1: it turns **damp red litmus paper blue** (it is an alkaline gas). Test 2: a glass rod dipped in **concentrated hydrochloric acid** gives **dense white fumes** of ammonium chloride.\n\n(iii) $\mathrm{NH_4^+(aq)+OH^-(aq)\rightarrow NH_3(g)+H_2O(l)}$.".replace("\\n", "\n")),
        S("d", r"A mass of $6.25\ \text{g}$ of Q is heated strongly until there is no further change. (Zn = 65, C = 12, O = 16; $1$ mole of gas occupies $24000\ \text{cm}^3$ at r.t.p.)" + "\n\n(i) Calculate the number of moles of Q.\n\n(ii) Calculate the mass of the residue.\n\n(iii) Calculate the volume of gas given off, measured at r.t.p.",
          ["mole concept", "stoichiometry"], "moyenne", 5,
          [("You calculate $M(\\mathrm{ZnCO_3})=125$ and $n=0.050\\ \\text{mol}$", 1), ("You use $M(\\mathrm{ZnO})=81$", 1), ("You obtain $4.05\\ \\text{g}$", 1), ("You use the $1:1$ ratio for $\\mathrm{CO_2}$", 1), ("You obtain $1200\\ \\text{cm}^3$", 1)],
          r"Convert the mass to moles, use the ratio in the equation, then convert the moles of the product to a mass or a volume.",
          r"(i) $M(\mathrm{ZnCO_3})=65+12+3(16)=125\ \text{g/mol}$, so $n=\dfrac{6.25}{125}=0.050\ \text{mol}$.\n\n(ii) $\mathrm{ZnCO_3\rightarrow ZnO+CO_2}$ is a $1:1:1$ ratio, so $n(\mathrm{ZnO})=0.050\ \text{mol}$. $M(\mathrm{ZnO})=65+16=81\ \text{g/mol}$, so the mass of residue $=0.050\times81=4.05\ \text{g}$.\n\n(iii) $n(\mathrm{CO_2})=0.050\ \text{mol}$, so $V=0.050\times24000=1200\ \text{cm}^3$.".replace("\\n", "\n"),
          ans=r"$4.05\ \text{g}$ and $1200\ \text{cm}^3$"),
    ]))
    return ex


def section_c():
    G = "SECTION C"
    ex = []

    ex.append(E("7", G, 20, r"A student added $0.50\ \text{g}$ of marble chips (calcium carbonate) to excess dilute hydrochloric acid at $25\,^\circ\text{C}$ (Experiment 1) and measured the volume of carbon dioxide produced. The experiment was repeated with $0.50\ \text{g}$ of powdered marble, all the other conditions being unchanged (Experiment 2). The volumes of gas, measured at r.t.p., are shown in {FIG}.", [
        S("a", "(i) Write the equation for the reaction between calcium carbonate and hydrochloric acid.\n\n(ii) Name a piece of apparatus that can be used to measure the volume of gas produced.", ["rates of reaction", "apparatus and experiments"], "faible", 3,
          [("You write the correct formulas for reactants and products", 1), ("You balance the equation: $\\mathrm{CaCO_3+2HCl\\rightarrow CaCl_2+H_2O+CO_2}$", 1), ("You name a gas syringe (or an inverted measuring cylinder filled with water)", 1)],
          r"A carbonate reacts with an acid to give a salt, water and carbon dioxide. A gas can be collected in a gas syringe or over water.",
          r"(i) $\mathrm{CaCO_3(s)+2HCl(aq)\rightarrow CaCl_2(aq)+H_2O(l)+CO_2(g)}$.\n\n(ii) A **gas syringe**, or a **measuring cylinder or burette filled with water and inverted in a trough of water**.".replace("\\n", "\n"),
          fig_enonce="gaz2"),
        S("b", "Use the curve for Experiment 1 in {FIG}.\n\n(i) At what time did the reaction stop?\n\n(ii) Calculate the average rate of reaction during the first $40$ seconds, in $\\text{cm}^3/\\text{s}$.\n\n(iii) Explain why the rate of reaction decreases as the reaction proceeds.", ["rates of reaction", "graphs"], "moyenne", 4,
          [("You read $160\\ \\text{s}$ (the volume stops changing)", 1), ("You read $60\\ \\text{cm}^3$ at $40\\ \\text{s}$", 1), ("You obtain $1.5\\ \\text{cm}^3/\\text{s}$", 1),
           ("You explain that the acid is used up, so its concentration falls and there are fewer collisions per second", 1)],
          r"The average rate is the volume of gas formed divided by the time taken. On a volume-time graph the reaction is over when the curve becomes horizontal.",
          r"(i) The curve becomes horizontal at **$160\ \text{s}$**: no more gas is formed after that.\n\n(ii) At $40\ \text{s}$ the volume is $60\ \text{cm}^3$, so the average rate is $\dfrac{60}{40}=1.5\ \text{cm}^3/\text{s}$.\n\n(iii) As the reaction proceeds the acid particles are used up and the marble chips become smaller, so the **concentration of the acid falls** and there are **fewer collisions per second** between the reacting particles. The curve becomes less steep.".replace("\\n", "\n"),
          ans=r"$160\ \text{s}$ and $1.5\ \text{cm}^3/\text{s}$"),
        S("c", "Which curve in {FIG} was obtained with the powdered marble? Explain why the powder reacts at a different rate, using the idea of colliding particles.", ["rates of reaction"], "moyenne", 4,
          [("You identify Experiment 2 as the powder", 1), ("You say that the powder has a larger surface area", 1), ("You say that more particles of calcium carbonate are exposed to the acid", 1), ("You say that this gives more frequent collisions between particles, so a faster reaction", 1)],
          r"A reaction can only happen when particles collide. The rate increases when there are more collisions per second.",
          r"The powder gives **Experiment 2**, the steeper curve. A powder has a **much larger surface area** than chips of the same mass, so **more calcium carbonate particles are exposed** to the acid at the same time. The acid particles collide with calcium carbonate particles **more often**, so more successful collisions occur per second and the reaction is faster."),
        S("d", r"Experiment 1 is repeated at $45\,^\circ\text{C}$ instead of $25\,^\circ\text{C}$. State two ways in which the curve would differ from the curve of Experiment 1, and explain the effect of the temperature on the rate.", ["rates of reaction"], "elevee", 4,
          [("You say that the curve would be steeper (the reaction would finish sooner)", 1), ("You say that the final volume would be the same, $120\\ \\text{cm}^3$, because the mass of marble is the same", 1),
           ("You say that at a higher temperature the particles have more kinetic energy and move faster, so they collide more often", 1), ("You say that more particles have an energy greater than or equal to the activation energy, so more collisions are successful", 1)],
          r"A temperature rise increases the rate by increasing both the frequency of collisions and the proportion of collisions that have enough energy. It does not change the amount of product.",
          r"The curve would be **steeper**, reaching its maximum sooner, but it would level off at **the same final volume, $120\ \text{cm}^3$**, because the same mass of marble is used and the acid is in excess. At $45\,^\circ\text{C}$ the particles have **more kinetic energy and move faster**, so they collide **more often**. A **greater proportion of the collisions has energy equal to or greater than the activation energy**, so more of them lead to a reaction."),
        S("e", r"(The molar volume of a gas is $24000\ \text{cm}^3$ at r.t.p.; Ca = 40, C = 12, O = 16.)" + "\n\n(i) Calculate the number of moles of carbon dioxide collected in Experiment 1.\n\n(ii) Calculate the mass of calcium carbonate that reacted, and show that it agrees with the mass used.\n\n(iii) The acid used was $25.0\\ \\text{cm}^3$ of hydrochloric acid of concentration $0.50\\ \\text{mol/dm}^3$. Show that the acid was in excess.",
          ["mole concept", "stoichiometry"], "moyenne", 5,
          [("You calculate $n(\\mathrm{CO_2})=\\dfrac{120}{24000}=0.0050\\ \\text{mol}$", 1), ("You use the $1:1$ ratio to find $0.0050\\ \\text{mol}$ of calcium carbonate", 1), ("You obtain $0.50\\ \\text{g}$, which equals the mass used", 1),
           ("You calculate the acid available: $0.50\\times0.0250=0.0125\\ \\text{mol}$", 1), ("You compare it with the $0.0100\\ \\text{mol}$ needed ($2\\times0.0050$) and conclude that the acid was in excess", 1)],
          r"Moles of gas $=$ volume divided by the molar volume. The equation shows how many moles of each substance take part; a reagent is in excess when more of it is present than the equation requires.",
          r"(i) The final volume is $120\ \text{cm}^3$, so $n(\mathrm{CO_2})=\dfrac{120}{24000}=0.0050\ \text{mol}$.\n\n(ii) The ratio $\mathrm{CaCO_3}:\mathrm{CO_2}$ is $1:1$, so $n(\mathrm{CaCO_3})=0.0050\ \text{mol}$. $M(\mathrm{CaCO_3})=100\ \text{g/mol}$, so the mass is $0.0050\times100=0.50\ \text{g}$. This is the mass of marble used, so **all the marble reacted**.\n\n(iii) Acid available: $n(\mathrm{HCl})=0.50\times\dfrac{25.0}{1000}=0.0125\ \text{mol}$. Acid needed: $2\times0.0050=0.0100\ \text{mol}$. Since $0.0125>0.0100$, the **acid was in excess**.".replace("\\n", "\n"),
          ans=r"$0.0050\ \text{mol}$; $0.50\ \text{g}$; $0.0125\ \text{mol}$ against $0.0100\ \text{mol}$"),
    ]))

    ex.append(E("8", G, 20, r"Ethene, $\mathrm{C_2H_4}$, is the first member of the alkene series.", [
        S("a", "(i) Explain why ethene is described as unsaturated.\n\n(ii) Describe a chemical test that distinguishes ethene from ethane, giving the result with each gas.\n\n(iii) Draw the structural formula of ethene, showing all the bonds.", ["alkanes and alkenes"], "faible", 4,
          [("You say that ethene has a carbon-carbon double bond", 1), ("You give bromine water as the reagent and state that ethene decolourises it (orange to colourless)", 1), ("You state that ethane gives no change", 1),
           ("You draw $\\mathrm{H_2C{=}CH_2}$ with all four C-H bonds", 1)],
          r"An unsaturated hydrocarbon has at least one double bond between carbon atoms, so it can add other atoms. Alkenes decolourise bromine water; alkanes do not.",
          r"(i) Ethene has a **carbon-carbon double bond**: its carbon atoms are not joined to the greatest possible number of hydrogen atoms, so more atoms can be added across the bond.\n\n(ii) Shake each gas with **bromine water**. **Ethene** turns the orange-brown solution **colourless**; **ethane** causes **no change**.\n\n(iii) The drawing shows **two carbon atoms joined by a double bond** (two lines between them), with **two hydrogen atoms joined by single bonds to each carbon atom**: $\mathrm{H_2C{=}CH_2}$, a flat molecule with four C-H bonds in all.".replace("\\n", "\n")),
        S("b", "Ethene reacts with steam and with bromine.\n\n(i) Write an equation for the reaction of ethene with steam, name the product and state the conditions.\n\n(ii) Write an equation for the reaction of ethene with bromine and name the product.\n\n(iii) Name the type of reaction in (i) and (ii).", ["alkanes and alkenes", "alcohols and carboxylic acids"], "faible", 5,
          [("You write $\\mathrm{C_2H_4+H_2O\\rightarrow C_2H_5OH}$ and name ethanol", 1), ("You give the conditions: phosphoric acid catalyst, about $300\\,^\\circ\\text{C}$ and a high pressure", 1),
           ("You write $\\mathrm{C_2H_4+Br_2\\rightarrow C_2H_4Br_2}$", 1), ("You name the product 1,2-dibromoethane", 1), ("You name the reactions addition reactions", 1)],
          r"In an addition reaction a small molecule adds across the double bond and the product is saturated.",
          r"(i) $\mathrm{C_2H_4+H_2O\rightarrow C_2H_5OH}$. The product is **ethanol**. The conditions are a **phosphoric acid catalyst, about $300\,^\circ\text{C}$ and about $60$ atmospheres**.\n\n(ii) $\mathrm{C_2H_4+Br_2\rightarrow CH_2BrCH_2Br}$. The product is **1,2-dibromoethane**.\n\n(iii) Both are **addition** reactions.".replace("\\n", "\n")),
        S("c", "Ethene can be changed into poly(ethene).\n\n(i) Explain what is meant by addition polymerisation.\n\n(ii) Draw the repeat unit of poly(ethene).\n\n(iii) State one use of poly(ethene).", ["polymers", "alkanes and alkenes"], "moyenne", 5,
          [("You say that many small unsaturated molecules (monomers) join together", 1), ("You say that the double bond opens and no other product is formed", 1), ("You draw the repeat unit $-\\mathrm{CH_2-CH_2-}$ with open bonds at both ends", 1),
           ("You show $n$ units, $\\left(-\\mathrm{CH_2-CH_2-}\\right)_n$", 1), ("You state one use, for example plastic bags or insulation for wires", 1)],
          r"In addition polymerisation the double bonds of many identical monomers open and the monomers join end to end to give a long saturated chain.",
          r"(i) **Addition polymerisation** is the joining of **many small unsaturated molecules (monomers)** into one long molecule (a polymer). The **double bond of each monomer opens** and the monomers add to one another; **no other substance is formed**.\n\n(ii) The repeat unit is $\mathrm{-CH_2-CH_2-}$, written $\left(\mathrm{-CH_2-CH_2-}\right)_n$.\n\n(iii) Poly(ethene) is used for **plastic bags**, bottles and the insulation of electric cables.".replace("\\n", "\n")),
        S("d", r"A mass of $2.8\ \text{g}$ of ethene burns completely in oxygen: $\mathrm{C_2H_4+3O_2\rightarrow2CO_2+2H_2O}$. (C = 12, H = 1, O = 16; $1$ mole of gas occupies $24000\ \text{cm}^3$ at r.t.p.)" + "\n\n(i) Calculate the number of moles of ethene burnt.\n\n(ii) Calculate the volume of oxygen, at r.t.p., needed to burn it.\n\n(iii) Calculate the mass of carbon dioxide formed.\n\n(iv) Explain why burning ethene and other fuels adds to global warming.",
          ["stoichiometry", "mole concept", "alkanes and alkenes"], "moyenne", 6,
          [("You calculate $M(\\mathrm{C_2H_4})=28$ and $n=0.10\\ \\text{mol}$", 1), ("You use the ratio $1:3$ to find $0.30\\ \\text{mol}$ of oxygen", 1), ("You obtain $7200\\ \\text{cm}^3$", 1),
           ("You use the ratio $1:2$ to find $0.20\\ \\text{mol}$ of carbon dioxide", 1), ("You obtain $8.8\\ \\text{g}$", 1), ("You state that carbon dioxide is a greenhouse gas that traps heat in the atmosphere", 1)],
          r"Moles come from mass divided by molar mass; the equation then gives the moles of oxygen and of carbon dioxide, which are converted to a volume or a mass.",
          r"(i) $M(\mathrm{C_2H_4})=2(12)+4(1)=28\ \text{g/mol}$, so $n=\dfrac{2.8}{28}=0.10\ \text{mol}$.\n\n(ii) The ratio $\mathrm{C_2H_4}:\mathrm{O_2}$ is $1:3$, so $n(\mathrm{O_2})=0.30\ \text{mol}$ and $V=0.30\times24000=7200\ \text{cm}^3$.\n\n(iii) The ratio $\mathrm{C_2H_4}:\mathrm{CO_2}$ is $1:2$, so $n(\mathrm{CO_2})=0.20\ \text{mol}$. $M(\mathrm{CO_2})=44\ \text{g/mol}$, so the mass is $0.20\times44=8.8\ \text{g}$.\n\n(iv) The combustion of a fuel that contains carbon forms **carbon dioxide**, a **greenhouse gas**: it absorbs heat that the Earth radiates and keeps it in the atmosphere, so the burning of more fuel raises the average temperature of the Earth.".replace("\\n", "\n"),
          ans=r"$0.10\ \text{mol}$; $7200\ \text{cm}^3$; $8.8\ \text{g}$"),
    ]))
    return ex
