r"""Questions de l'epreuve inedite GCE O Level Chemistry Paper 1 n.1 (50 QCM). Voir generer_chemistry_p1.py.

Q(id, themes, difficulte, enonce, bonne option, 3 distracteurs, rappel, resolution, piege, conseil, figure, cle_fixee, ordre).
Toutes les chaines sont BRUTES (r"..."): une commande LaTeX a backslash simple dans une chaine ordinaire devient un caractere de controle.
`{FIG}` est remplace par « Figure N ». `ordre` : liste de 4 options a ordre IMPOSE (questions de completion multiple et d'assertion-raison, comme
dans les vrais Paper 1 de Chemistry) ; la cle en decoule. Les questions chiffrees sont recalculees par verifier_reponses_chemistry_p1.py.
Masses atomiques relatives donnees dans chaque enonce chiffre ; volume molaire dans la consigne du paper.
Ordre du paper : melange par petites grappes d'un meme chapitre, comme les vrais Paper 1 de Chemistry (pas l'ordre du syllabus).
"""

MC_PLAGE = "27-29"
AR_PLAGE = "36-37"
OPTIONS_MC = ["1, 2 and 3 only", "1 and 3 only", "2 and 4 only", "4 only"]
OPTIONS_AR = [
    "If both statements are true and the second statement is a correct explanation of the first statement",
    "If both statements are true but the second statement is not a correct explanation of the first statement",
    "If the first statement is true but the second statement is false",
    "If the first statement is false but the second statement is true",
]
INSTR_MC = (
    f"**Instructions (Questions {MC_PLAGE}):** for each of these questions, ONE or MORE of the responses numbered 1 to 4 is (are) correct. "
    "Decide which response(s) is (are) correct. Then choose: A. if only 1, 2 and 3 are correct; B. if only 1 and 3 are correct; "
    "C. if only 2 and 4 are correct; D. if only 4 is correct."
)
INSTR_AR = (
    f"**Instructions (Questions {AR_PLAGE}):** each question consists of a statement in the left-hand column followed by another statement in the "
    "right-hand column. Decide whether each of the statements is TRUE or FALSE. Then choose: A. if both statements are true and the second "
    "statement is a correct explanation of the first statement; B. if both statements are true but the second statement is NOT a correct "
    "explanation of the first statement; C. if the first statement is true but the second statement is false; D. if the first statement is "
    "false but the second statement is true."
)


def Q(qid, themes, diff, stem, ok, bad, rappel, sol, piege=None, conseil=None, fig=None, cle_fixee=None, ordre=None):
    if ordre is not None:
        assert ok in ordre and len(ordre) == 4, qid
        cle_fixee = "abcd"[ordre.index(ok)]
        bad = [o for o in ordre if o != ok]
    return dict(id=qid, themes=themes, diff=diff, stem=stem, ok=ok, bad=bad, rappel=rappel, sol=sol, piege=piege,
                conseil=conseil, fig=fig, cle_fixee=cle_fixee, ordre=ordre)


def questions():
    q = []
    a = q.append

    # 1 --------------------------------------------------------------------------------------------- etats de la matiere, atome
    a(Q("c01", ["states of matter"], "faible",
        r"Which statement describes the arrangement and movement of the particles in a liquid?",
        r"The particles are close together and slide over one another.",
        [r"The particles are far apart and move freely in all directions.", r"The particles are in fixed positions and only vibrate.",
         r"The particles are far apart and only vibrate."],
        r"In a solid the particles are packed in fixed positions and vibrate; in a liquid they are still close together but can move past one another; in a gas they are far apart and move at random.",
        r"A liquid has a fixed volume but no fixed shape, because its particles touch each other (fixed volume) and slide over one another (no fixed shape). The other options describe a gas or a solid."))
    a(Q("c02", ["atomic structure"], "faible",
        r"The ion $^{24}_{12}\mathrm{Mg}^{2+}$ contains",
        r"12 protons, 12 neutrons and 10 electrons",
        [r"12 protons, 12 neutrons and 14 electrons", r"10 protons, 12 neutrons and 10 electrons", r"12 protons, 24 neutrons and 10 electrons"],
        r"The atomic number is the number of protons; the mass number is the number of protons plus neutrons. A positive ion has lost electrons: its charge is the number of protons minus the number of electrons.",
        r"Protons $=12$ (the subscript). Neutrons $=24-12=12$. A $2+$ ion has lost two electrons from the neutral atom, which has $12$: electrons $=12-2=10$.",
        piege=r"A positive ion has fewer electrons than protons; $14$ electrons would be an ion with a $2-$ charge."))
    a(Q("c03", ["atomic structure"], "moyenne",
        r"The atomic number of sulphur is $16$. What is the electronic configuration of the sulphide ion, $\mathrm{S^{2-}}$?",
        r"2, 8, 8", [r"2, 8, 6", r"2, 8, 4", r"2, 8, 10"],
        r"A negative ion forms when an atom gains electrons, usually until its outer shell holds eight electrons. Shells fill $2, 8, 8, \ldots$ in this order.",
        r"A sulphur atom has $16$ electrons arranged $2, 8, 6$. The ion $\mathrm{S^{2-}}$ has gained two electrons: $18$ electrons arranged $2, 8, 8$, the configuration of argon.",
        piege=r"$2, 8, 6$ is the configuration of the sulphur atom, not of its ion."))
    a(Q("c04", ["periodic table"], "faible",
        r"Going across Period 3 of the Periodic Table from sodium to chlorine, which property decreases?",
        r"Metallic character",
        [r"The number of electrons in the outer shell", r"The nuclear charge", r"The number of occupied electron shells"],
        r"Across a period the number of protons and of outer electrons increases by one at each element, while the number of occupied shells stays the same. The elements change from metals to non-metals.",
        r"The nuclear charge and the number of outer electrons both increase from $1$ (sodium) to $7$ (chlorine). The number of occupied shells stays at $3$. Metallic character decreases because atoms hold their outer electrons more strongly, so they lose them less easily.",
        piege=r"The number of shells does not change across a period, so it does not decrease; it is the number of shells that increases down a group."))
    a(Q("c05", ["chemical bonding"], "faible",
        r"Which of the following compounds contains ionic bonds?",
        r"$\mathrm{MgCl_2}$", [r"$\mathrm{NH_3}$", r"$\mathrm{CCl_4}$", r"$\mathrm{SiO_2}$"],
        r"A metal combined with a non-metal forms an ionic compound (electrons are transferred); two non-metals form a covalent compound (electrons are shared).",
        r"Magnesium is a metal and chlorine is a non-metal, so $\mathrm{MgCl_2}$ is ionic: $\mathrm{Mg^{2+}}$ and $\mathrm{Cl^-}$ ions. $\mathrm{NH_3}$, $\mathrm{CCl_4}$ and $\mathrm{SiO_2}$ are made of non-metals only and are covalent."))

    # 6-11 ------------------------------------------------------------------------------------------ mole, stoechiometrie, gaz
    a(Q("c06", ["mole concept"], "faible",
        r"How many moles are present in $4.9\ \text{g}$ of sulphuric acid, $\mathrm{H_2SO_4}$? (H = 1, S = 32, O = 16)",
        r"$0.05\ \text{mol}$", [r"$20\ \text{mol}$", r"$0.5\ \text{mol}$", r"$480.2\ \text{mol}$"],
        r"The number of moles is the mass divided by the molar mass: $n=\dfrac{m}{M}$.",
        r"$M(\mathrm{H_2SO_4})=2(1)+32+4(16)=98\ \text{g/mol}$, so $n=\dfrac{4.9}{98}=0.05\ \text{mol}$.",
        piege=r"$20\ \text{mol}$ comes from dividing the molar mass by the mass, the inverse of the correct fraction."))
    a(Q("c07", ["mole concept"], "moyenne",
        r"Calcium carbonate decomposes on strong heating: $\mathrm{CaCO_3 \rightarrow CaO + CO_2}$. What volume of carbon dioxide, measured at r.t.p., is produced from $10.0\ \text{g}$ of calcium carbonate? (Ca = 40, C = 12, O = 16)",
        r"$2400\ \text{cm}^{3}$", [r"$240\ \text{cm}^{3}$", r"$4800\ \text{cm}^{3}$", r"$24000\ \text{cm}^{3}$"],
        r"Convert the mass to moles, use the equation ratio, then multiply the moles of gas by the molar volume ($24000\ \text{cm}^3$ per mole at r.t.p.).",
        r"$M(\mathrm{CaCO_3})=40+12+3(16)=100\ \text{g/mol}$, so $n=\dfrac{10.0}{100}=0.100\ \text{mol}$. The equation shows $1$ mol of $\mathrm{CO_2}$ for $1$ mol of $\mathrm{CaCO_3}$, so $0.100\ \text{mol}$ of gas forms: $V=0.100\times24000=2400\ \text{cm}^3$.",
        piege=r"$24000\ \text{cm}^{3}$ is the volume of one mole: here only a tenth of a mole of gas forms."))
    a(Q("c08", ["stoichiometry"], "moyenne",
        r"What mass of magnesium oxide is formed when $4.8\ \text{g}$ of magnesium burns completely in oxygen? (Mg = 24, O = 16) $\quad 2\mathrm{Mg}+\mathrm{O_2}\rightarrow2\mathrm{MgO}$",
        r"$8.0\ \text{g}$", [r"$4.0\ \text{g}$", r"$12.0\ \text{g}$", r"$20.8\ \text{g}$"],
        r"Moles of the given substance $\rightarrow$ moles of the product from the equation ratio $\rightarrow$ mass of the product.",
        r"$n(\mathrm{Mg})=\dfrac{4.8}{24}=0.20\ \text{mol}$. The ratio is $2:2$, so $n(\mathrm{MgO})=0.20\ \text{mol}$. $M(\mathrm{MgO})=24+16=40\ \text{g/mol}$, so the mass is $0.20\times40=8.0\ \text{g}$. Check: the magnesium gained $8.0-4.8=3.2\ \text{g}$ of oxygen, that is $0.10\ \text{mol}$ of $\mathrm{O_2}$ for $0.20\ \text{mol}$ of Mg.",
        piege=r"$20.8\ \text{g}$ adds the mass of magnesium to the mass of one mole of oxygen atoms instead of using the equation ratio."))
    a(Q("c09", ["mole concept", "acids bases and salts"], "elevee",
        r"$25.0\ \text{cm}^3$ of sodium hydroxide solution of concentration $0.20\ \text{mol/dm}^3$ is exactly neutralised by $20.0\ \text{cm}^3$ of dilute sulphuric acid. What is the concentration of the acid? $\quad 2\mathrm{NaOH}+\mathrm{H_2SO_4}\rightarrow\mathrm{Na_2SO_4}+2\mathrm{H_2O}$",
        r"$0.125\ \text{mol/dm}^3$", [r"$0.25\ \text{mol/dm}^3$", r"$0.50\ \text{mol/dm}^3$", r"$0.16\ \text{mol/dm}^3$"],
        r"Moles of solute $=$ concentration $\times$ volume in $\text{dm}^3$. Find the moles of the known solution, use the equation ratio, then divide by the volume of the other solution.",
        r"$n(\mathrm{NaOH})=0.20\times\dfrac{25.0}{1000}=0.0050\ \text{mol}$. The ratio $\mathrm{NaOH}:\mathrm{H_2SO_4}$ is $2:1$, so $n(\mathrm{H_2SO_4})=0.0025\ \text{mol}$. Concentration $=\dfrac{0.0025}{0.0200}=0.125\ \text{mol/dm}^3$.",
        piege=r"$0.25\ \text{mol/dm}^3$ assumes a $1:1$ ratio; $0.16\ \text{mol/dm}^3$ comes from $0.20\times\dfrac{20}{25}$, which swaps the two volumes."))
    a(Q("c10", ["stoichiometry"], "moyenne",
        r"A hydrocarbon contains $80\%$ carbon and $20\%$ hydrogen by mass. What is its empirical formula? (C = 12, H = 1)",
        r"$\mathrm{CH_3}$", [r"$\mathrm{CH_2}$", r"$\mathrm{CH_4}$", r"$\mathrm{C_2H_6}$"],
        r"Divide each percentage by the relative atomic mass, then divide by the smaller result to obtain the simplest whole-number ratio.",
        r"Moles in $100\ \text{g}$: $\text{C}=\dfrac{80}{12}=6.67$ and $\text{H}=\dfrac{20}{1}=20$. Dividing by $6.67$ gives $\text{C}:\text{H}=1:3$. The empirical formula is $\mathrm{CH_3}$.",
        piege=r"$\mathrm{C_2H_6}$ has the same ratio but is a molecular formula; an empirical formula is the simplest ratio."))
    a(Q("c11", ["gas laws"], "moyenne",
        r"A fixed mass of gas occupies $200\ \text{cm}^3$ at $27\,^\circ\text{C}$. What volume will it occupy at $127\,^\circ\text{C}$ at the same pressure?",
        r"$267\ \text{cm}^{3}$", [r"$300\ \text{cm}^{3}$", r"$150\ \text{cm}^{3}$", r"$941\ \text{cm}^{3}$"],
        r"At constant pressure the volume of a fixed mass of gas is proportional to its temperature in kelvin (Charles' law): $\dfrac{V_1}{T_1}=\dfrac{V_2}{T_2}$.",
        r"$T_1=27+273=300\ \text{K}$ and $T_2=127+273=400\ \text{K}$. $V_2=200\times\dfrac{400}{300}=267\ \text{cm}^3$.",
        piege=r"$941\ \text{cm}^3$ uses the temperatures in degrees Celsius ($200\times\frac{127}{27}$); $150\ \text{cm}^3$ inverts the ratio; $300\ \text{cm}^3$ adds the rise of $100\,^\circ\text{C}$ to the volume. The temperatures must be in kelvin."))

    # 12-17 ------------------------------------------------------------------------------------------ solubilite, sels, analyse
    a(Q("c12", ["solubility"], "moyenne",
        r"{FIG} shows how the solubility of a salt X in water changes with temperature. A saturated solution of X containing $100\ \text{g}$ of water at $60\,^\circ\text{C}$ is cooled to $20\,^\circ\text{C}$. What mass of X crystallises?",
        r"$80\ \text{g}$", [r"$120\ \text{g}$", r"$40\ \text{g}$", r"$160\ \text{g}$"],
        r"The solubility of a salt is the mass that dissolves in $100\ \text{g}$ of water to give a saturated solution. When a saturated solution is cooled, the difference between the two solubilities comes out as crystals.",
        r"At $60\,^\circ\text{C}$ the graph gives $120\ \text{g}$ per $100\ \text{g}$ of water; at $20\,^\circ\text{C}$ it gives $40\ \text{g}$. Mass crystallising $=120-40=80\ \text{g}$.",
        piege=r"$120\ \text{g}$ is the amount dissolved at the higher temperature; some of it stays in solution at $20\,^\circ\text{C}$.",
        fig="solubilite"))
    a(Q("c13", ["acids bases and salts"], "faible",
        r"Which method is used to prepare lead(II) sulphate, an insoluble salt?",
        r"Mixing solutions of lead(II) nitrate and sodium sulphate, then filtering",
        [r"Adding excess lead to dilute sulphuric acid, then filtering and crystallising",
         r"Titrating lead(II) hydroxide with dilute sulphuric acid using an indicator",
         r"Heating lead(II) nitrate solution with dilute hydrochloric acid"],
        r"An insoluble salt is prepared by precipitation: mix a solution of a soluble salt that contains its cation with a solution of a soluble salt that contains its anion, then filter, wash and dry the solid.",
        r"Lead(II) nitrate and sodium sulphate are both soluble. When their solutions are mixed, lead(II) sulphate precipitates: $\mathrm{Pb^{2+}(aq)+SO_4^{2-}(aq)\rightarrow PbSO_4(s)}$. The solid is filtered off, washed with distilled water and dried. Titration and crystallisation are used for soluble salts."))
    a(Q("c14", ["acids bases and salts"], "faible",
        r"Excess black copper(II) oxide is added to warm dilute hydrochloric acid. What is observed?",
        r"The black solid dissolves, giving a blue solution.", [r"The black solid dissolves, giving a colourless solution.",
                                                              r"Bubbles of a colourless gas form and the solution turns green.",
                                                              r"A white precipitate forms and the solid remains black."],
        r"A metal oxide is a base: it reacts with an acid to form a salt and water, without any gas. Copper(II) salts in solution are blue.",
        r"$\mathrm{CuO+2HCl\rightarrow CuCl_2+H_2O}$. The black oxide dissolves and the copper(II) ions give a blue solution. No gas forms, because a base reacting with an acid does not release a gas.",
        piege=r"Bubbles would show a carbonate or a reactive metal, not an oxide."))
    a(Q("c15", ["qualitative analysis"], "moyenne",
        r"Solution T gives a white precipitate with a few drops of aqueous sodium hydroxide, which dissolves in excess. With aqueous ammonia it gives a white precipitate that does not dissolve in excess. With aqueous potassium iodide T gives a yellow precipitate. Which cation is present in T?",
        r"$\mathrm{Pb^{2+}}$", [r"$\mathrm{Al^{3+}}$", r"$\mathrm{Mg^{2+}}$", r"$\mathrm{Ca^{2+}}$"],
        r"Sodium hydroxide and ammonia separate several white-precipitate cations; an extra test tells apart those that behave alike. Lead(II) iodide is a yellow precipitate.",
        r"A white precipitate that dissolves in excess sodium hydroxide but not in excess ammonia fits $\mathrm{Pb^{2+}}$ and $\mathrm{Al^{3+}}$. Only lead(II) ions give a yellow precipitate of lead(II) iodide with potassium iodide: $\mathrm{Pb^{2+}+2I^-\rightarrow PbI_2}$. The precipitates of $\mathrm{Mg^{2+}}$ and $\mathrm{Ca^{2+}}$ do not dissolve in excess sodium hydroxide.",
        piege=r"$\mathrm{Al^{3+}}$ gives the same two precipitates; the potassium iodide test is what separates the two ions."))
    a(Q("c16", ["qualitative analysis"], "faible",
        r"A colourless solution gives a white precipitate with acidified silver nitrate solution. The precipitate dissolves when dilute aqueous ammonia is added. Which anion is present?",
        r"Chloride", [r"Bromide", r"Iodide", r"Sulphate"],
        r"Halide ions are tested with acidified silver nitrate: chloride gives a white precipitate, bromide a cream one and iodide a yellow one. Silver chloride dissolves in dilute ammonia.",
        r"$\mathrm{Ag^+(aq)+Cl^-(aq)\rightarrow AgCl(s)}$, a white precipitate that dissolves in dilute ammonia. Silver bromide is cream and iodide is yellow, and neither dissolves in dilute ammonia. Sulphate gives no precipitate with acidified silver nitrate."))
    a(Q("c17", ["qualitative analysis", "acids bases and salts"], "moyenne",
        r"What is observed when aqueous ammonia is added drop by drop, and then in excess, to copper(II) sulphate solution?",
        r"A pale blue precipitate forms, then dissolves to give a deep blue solution.",
        [r"A pale blue precipitate forms and remains in excess ammonia.", r"A white precipitate forms, then dissolves to give a colourless solution.",
         r"A green precipitate forms and turns brown on standing."],
        r"Copper(II) ions give a pale blue precipitate of the hydroxide with aqueous ammonia; the precipitate dissolves in excess ammonia to give a deep blue solution of a complex ion.",
        r"$\mathrm{Cu^{2+}+2OH^-\rightarrow Cu(OH)_2}$ is the pale blue precipitate. In excess ammonia it forms the soluble deep blue complex $\mathrm{[Cu(NH_3)_4]^{2+}}$. The pale blue precipitate that stays in excess is given with aqueous sodium hydroxide, not with ammonia.",
        piege=r"Sodium hydroxide and ammonia differ for copper(II): only ammonia dissolves the precipitate in excess."))

    # 18-26 ------------------------------------------------------------------------------------------ non-metaux, halogenes, groupe I, metaux
    a(Q("c18", ["non-metals and their compounds"], "faible",
        r"A gas turns acidified potassium dichromate(VI) paper from orange to green. The gas is",
        r"sulphur dioxide", [r"carbon dioxide", r"hydrogen chloride", r"ammonia"],
        r"Sulphur dioxide is a reducing agent: it changes the orange dichromate(VI) ion into the green chromium(III) ion.",
        r"Only sulphur dioxide reduces acidified dichromate(VI) from orange to green. Carbon dioxide turns lime water milky, hydrogen chloride turns blue litmus red and gives white fumes with ammonia, and ammonia turns damp red litmus blue.",
        piege=r"Do not confuse this test with the lime water test, which is a test for carbon dioxide."))
    a(Q("c19", ["non-metals and their compounds"], "faible",
        r"Which substance is used as the catalyst in the Contact process for the manufacture of sulphuric acid?",
        r"Vanadium(V) oxide", [r"Nickel", r"Manganese(IV) oxide", r"Copper"],
        r"In the Contact process sulphur dioxide is oxidised to sulphur trioxide, $\mathrm{2SO_2+O_2\rightleftharpoons2SO_3}$, over a solid catalyst.",
        r"The catalyst of the Contact process is vanadium(V) oxide, $\mathrm{V_2O_5}$. Nickel is the catalyst for hydrogenation of alkenes and manganese(IV) oxide is the catalyst for the decomposition of hydrogen peroxide."))
    a(Q("c20", ["non-metals and their compounds"], "faible",
        r"When concentrated sulphuric acid is added to blue hydrated copper(II) sulphate crystals, the crystals turn white. The acid is acting as a",
        r"dehydrating agent", [r"oxidising agent", r"reducing agent", r"catalyst"],
        r"Concentrated sulphuric acid has a strong attraction for water. It removes water of crystallisation from hydrated salts and removes the elements of water from sugar.",
        r"$\mathrm{CuSO_4\cdot5H_2O\rightarrow CuSO_4+5H_2O}$: the acid takes up the water of crystallisation and the blue hydrated crystals become white anhydrous copper(II) sulphate. No electron transfer is involved, so the acid is not an oxidising or a reducing agent."))
    a(Q("c21", ["non-metals and their compounds"], "faible",
        r"Carbon monoxide is poisonous because it",
        r"combines with haemoglobin and stops the blood from carrying oxygen",
        [r"is acidic and burns the lining of the lungs", r"reacts with the oxygen of the air to give carbon dioxide inside the lungs",
         r"dissolves in blood and lowers its pH"],
        r"Carbon monoxide is a colourless, odourless gas formed by incomplete combustion of carbon-containing fuels.",
        r"Carbon monoxide binds to haemoglobin in red blood cells far more strongly than oxygen does, so the blood can no longer carry oxygen to the body. It is a neutral oxide and does not burn the lungs."))
    a(Q("c22", ["halogens"], "moyenne",
        r"Chlorine water is added to a colourless solution of potassium bromide. What is observed?",
        r"The solution turns orange-brown.", [r"A white precipitate forms.", r"The solution turns purple.", r"There is no visible change."],
        r"A more reactive halogen displaces a less reactive one from a solution of its halide. Chlorine is more reactive than bromine.",
        r"$\mathrm{Cl_2+2KBr\rightarrow2KCl+Br_2}$. Bromine forms and colours the solution orange-brown. Chlorine is more reactive than bromine, so a reaction does occur.",
        piege=r"A purple colour is typical of iodine vapour or of iodine dissolved in an organic solvent, not of bromine in water."))
    a(Q("c23", ["halogens", "periodic table"], "moyenne",
        r"Why does the reactivity of the halogens decrease down Group VII?",
        r"The atoms gain an electron less easily because the outer shell is further from the nucleus.",
        [r"The atoms lose electrons more easily as the nuclear charge increases.", r"The number of outer-shell electrons decreases down the group.",
         r"The molecules become smaller down the group."],
        r"A halogen reacts by gaining one electron to complete its outer shell. The easier this is, the more reactive the halogen.",
        r"Down the group each atom has an extra electron shell, so the outer shell is further from the nucleus and more shielded. The incoming electron is attracted less strongly, so the atom gains it less easily. All halogens have seven outer electrons, and the molecules become larger down the group.",
        piege=r"Halogens react by gaining electrons; losing electrons is how Group I metals react."))
    a(Q("c24", ["Group I elements"], "faible",
        r"What is observed when a small piece of potassium is placed on water?",
        r"It moves on the surface, melts into a ball and burns with a lilac flame.",
        [r"It sinks slowly and produces a few bubbles.", r"It floats without moving and slowly dissolves.", r"It sinks and a blue solution forms."],
        r"Group I metals react with cold water to give hydrogen and a metal hydroxide; the reaction becomes more vigorous down the group.",
        r"$\mathrm{2K+2H_2O\rightarrow2KOH+H_2}$. Potassium is less dense than water, so it floats. The reaction is so exothermic that the metal melts, and the hydrogen burns with a lilac flame (the colour of potassium ions)."))
    a(Q("c25", ["metals and extraction"], "faible",
        r"Which metal is extracted by the electrolysis of its oxide dissolved in molten cryolite?",
        r"Aluminium", [r"Iron", r"Copper", r"Zinc"],
        r"The method of extraction depends on the position of the metal in the reactivity series: very reactive metals are extracted by electrolysis, less reactive ones by reduction with carbon.",
        r"Aluminium is above carbon in the reactivity series, so it cannot be obtained by heating with carbon. Aluminium oxide is dissolved in molten cryolite, which lowers its melting point, and electrolysed. Iron and zinc are obtained by reduction with carbon or carbon monoxide; copper is obtained from its sulphide ore by roasting and electrolytic refining."))
    a(Q("c26", ["metals and extraction"], "moyenne",
        r"Metal X does not react with cold water. It reacts with dilute hydrochloric acid and it displaces copper from copper(II) sulphate solution. Metal X is most likely",
        r"zinc", [r"copper", r"sodium", r"silver"],
        r"A metal displaces from solution any metal below it in the reactivity series, and a metal above hydrogen reacts with a dilute acid.",
        r"X is above hydrogen (it reacts with the acid) and above copper (it displaces it). Zinc fits: $\mathrm{Zn+CuSO_4\rightarrow ZnSO_4+Cu}$, and zinc does not react with cold water. Sodium reacts with cold water; copper and silver do not react with dilute hydrochloric acid."))

    # 27-29 : completion multiple -------------------------------------------------------------------------------------------------
    a(Q("c27", ["redox reactions"], "moyenne",
        INSTR_MC + "\n\nIn which of the following changes does **oxidation** take place?\n\n"
        r"1. $\mathrm{Fe^{2+}\rightarrow Fe^{3+}+e^-}$" + "\n"
        r"2. $\mathrm{Cl_2+2e^-\rightarrow2Cl^-}$" + "\n"
        r"3. $\mathrm{2Br^-\rightarrow Br_2+2e^-}$" + "\n"
        r"4. $\mathrm{Cu^{2+}+2e^-\rightarrow Cu}$",
        "1 and 3 only", None,
        r"Oxidation is loss of electrons; reduction is gain of electrons (OIL RIG). The electrons appear on the right-hand side of an oxidation half-equation.",
        r"1. The iron(II) ion loses an electron: **oxidation**. 2. Chlorine gains electrons: reduction. 3. Bromide ions lose electrons to form bromine: **oxidation**. 4. The copper(II) ion gains electrons: reduction. Only 1 and 3 are correct.",
        ordre=OPTIONS_MC))
    a(Q("c28", ["alkanes and alkenes"], "faible",
        INSTR_MC + "\n\nWhich of the following statements about alkanes are correct?\n\n"
        r"1. Their general formula is $\mathrm{C_nH_{2n+2}}$." + "\n"
        "2. They burn completely in excess oxygen to give carbon dioxide and water.\n"
        "3. They react with chlorine in sunlight by substitution.\n"
        "4. They dissolve readily in water.",
        "1, 2 and 3 only", None,
        r"Alkanes are saturated hydrocarbons with only single bonds. They are fairly unreactive: they burn, and they react with halogens only in sunlight.",
        r"1. Correct: methane $\mathrm{CH_4}$, ethane $\mathrm{C_2H_6}$. 2. Correct: $\mathrm{CH_4+2O_2\rightarrow CO_2+2H_2O}$. 3. Correct: $\mathrm{CH_4+Cl_2\rightarrow CH_3Cl+HCl}$ in sunlight. 4. Wrong: alkane molecules are non-polar and do not mix with the polar molecules of water, so alkanes are insoluble in water.",
        ordre=OPTIONS_MC))
    a(Q("c29", ["chemical bonding"], "faible",
        INSTR_MC + "\n\nWhich of the following is (are) properties of ionic compounds?\n\n"
        "1. They have low melting points.\n"
        "2. They conduct electricity when solid.\n"
        "3. They dissolve readily in hexane, an organic solvent.\n"
        "4. They conduct electricity when molten.",
        "4 only", None,
        r"An ionic compound is a giant lattice of ions held by strong electrostatic attraction. It conducts only when its ions are free to move.",
        r"1. Wrong: the strong attraction between the ions gives high melting points. 2. Wrong: in the solid the ions are held in fixed positions. 3. Wrong: ionic compounds do not dissolve in organic solvents. 4. Correct: when molten the ions are free to move and carry the current. Only 4 is correct.",
        ordre=OPTIONS_MC))

    # 30-35 ------------------------------------------------------------------------------------------ corrosion, electrolyse, redox, vitesse
    a(Q("c30", ["metals and extraction"], "faible",
        r"Which method protects the iron hull of a ship by sacrificial protection?",
        r"Attaching blocks of magnesium to the hull", [r"Painting the hull", r"Coating the hull with grease", r"Plating the hull with tin"],
        r"In sacrificial protection a more reactive metal is attached to the iron. It corrodes instead of the iron because it loses electrons more easily.",
        r"Magnesium is above iron in the reactivity series, so it is oxidised in preference to iron and the hull is protected even where the block does not cover it. Paint, grease and tin only keep air and water away from the iron; if the layer is damaged, the iron rusts.",
        piege=r"Tin plating is a barrier, not a sacrificial method: scratched tin plate rusts faster than bare iron."))
    a(Q("c31", ["electrolysis"], "faible",
        r"What is formed at the cathode when molten lead(II) bromide is electrolysed using inert electrodes?",
        r"Lead", [r"Bromine", r"Hydrogen", r"Oxygen"],
        r"In the electrolysis of a molten ionic compound the metal ions move to the cathode and the non-metal ions move to the anode.",
        r"The cathode is negative and attracts the positive lead(II) ions, which gain electrons: $\mathrm{Pb^{2+}+2e^-\rightarrow Pb}$. Bromine forms at the anode. Hydrogen and oxygen come from water, which is absent in a molten compound."))
    a(Q("c32", ["electrolysis"], "moyenne",
        r"Dilute sulphuric acid is electrolysed using platinum electrodes. What is the ratio of the volume of hydrogen to the volume of oxygen collected?",
        r"$2:1$", [r"$1:2$", r"$1:1$", r"$4:1$"],
        r"The electrolysis of dilute sulphuric acid with inert electrodes is the electrolysis of water: hydrogen forms at the cathode and oxygen at the anode.",
        r"Cathode: $\mathrm{4H^++4e^-\rightarrow2H_2}$. Anode: $\mathrm{4OH^-\rightarrow O_2+2H_2O+4e^-}$. The same four electrons give two molecules of hydrogen and one of oxygen, so the volumes are in the ratio $2:1$, as in water, $\mathrm{H_2O}$.",
        piege=r"The gas collected in the larger volume is hydrogen, at the cathode."))
    a(Q("c33", ["redox reactions"], "moyenne",
        r"What is the oxidation state of manganese in potassium manganate(VII), $\mathrm{KMnO_4}$?",
        r"$+7$", [r"$+6$", r"$+4$", r"$+2$"],
        r"The oxidation states in a neutral compound add up to zero. Potassium is $+1$ and oxygen is $-2$ in this compound.",
        r"Let the oxidation state of Mn be $x$: $(+1)+x+4(-2)=0$, so $x=+7$. The number in the name, manganate(VII), gives the same value.",
        piege=r"$+4$ is the oxidation state of manganese in $\mathrm{MnO_2}$, the common brown oxide."))
    a(Q("c34", ["rates of reaction", "graphs"], "moyenne",
        r"{FIG} shows the volume of hydrogen collected when excess dilute hydrochloric acid reacts with magnesium ribbon. What is the average rate of reaction during the first $2$ minutes?",
        r"$25\ \text{cm}^3/\text{min}$", [r"$50\ \text{cm}^3/\text{min}$", r"$30\ \text{cm}^3/\text{min}$", r"$44\ \text{cm}^3/\text{min}$"],
        r"The average rate of a reaction is the volume of gas formed divided by the time taken. On a volume-time graph the rate is the gradient: the steeper the curve, the faster the reaction.",
        r"After $2$ minutes the graph shows $50\ \text{cm}^3$ of gas. Average rate $=\dfrac{50}{2}=25\ \text{cm}^3/\text{min}$.",
        piege=r"$50$ is the volume, not the rate; $30$ is the volume after one minute, not the average over two minutes.",
        fig="gaz"))
    a(Q("c35", ["rates of reaction"], "faible",
        r"Manganese(IV) oxide is added to hydrogen peroxide solution and oxygen is given off much faster. Which statement about the manganese(IV) oxide at the end of the reaction is correct?",
        r"Its mass and chemical composition are unchanged.", [r"Its mass is less because it has been used up.", r"It has changed into manganese metal.",
                                                               r"Its mass is greater because it has combined with oxygen."],
        r"A catalyst changes the rate of a reaction without being used up: at the end of the reaction it has the same mass and the same chemical composition as at the start.",
        r"Manganese(IV) oxide speeds up $\mathrm{2H_2O_2\rightarrow2H_2O+O_2}$, and it does not appear in the equation. After filtering, washing and drying, the same mass of the same black solid is recovered. A catalyst is neither used up nor does it combine with the products.",
        piege=r"A catalyst does not change the amount of product formed; it only changes how fast the reaction goes."))

    # 36-37 : assertion-raison -----------------------------------------------------------------------------------------------
    a(Q("c36", ["non-metals and their compounds", "apparatus and experiments"], "moyenne",
        INSTR_AR + "\n\n| First statement | Second statement |\n|---|---|\n"
        "| Concentrated sulphuric acid is suitable for drying ammonia gas | Concentrated sulphuric acid is a strong dehydrating agent |",
        OPTIONS_AR[3], None,
        r"A drying agent must not react with the gas to be dried: an acidic drying agent cannot dry a basic gas.",
        r"The first statement is **false**: ammonia is a basic gas and reacts with the acid, $\mathrm{2NH_3+H_2SO_4\rightarrow(NH_4)_2SO_4}$, so the gas would be absorbed. The second statement is **true**: the acid removes water strongly. The answer is D.",
        ordre=OPTIONS_AR))
    a(Q("c37", ["halogens"], "faible",
        INSTR_AR + "\n\n| First statement | Second statement |\n|---|---|\n"
        "| Chlorine is added to drinking water | Chlorine is a yellow-green gas at room temperature |",
        OPTIONS_AR[1], None,
        r"Chlorine kills bacteria in water, which makes the water safe to drink. A statement can be true without being the reason for the first.",
        r"Both statements are **true**: chlorine is added to kill bacteria, and it is a yellow-green gas. But the colour or state of chlorine does not explain why it is added; the reason is that it kills disease-causing microbes. The answer is B.",
        ordre=OPTIONS_AR))

    # 38-50 ------------------------------------------------------------------------------------------ energie, equilibre, organique, divers
    a(Q("c38", ["energy changes"], "faible",
        r"Which process is exothermic?",
        r"The neutralisation of an acid by an alkali",
        [r"The thermal decomposition of calcium carbonate", r"The evaporation of water", r"Dissolving ammonium nitrate in water"],
        r"An exothermic process gives out heat to the surroundings, so the temperature of the surroundings rises. An endothermic process takes in heat.",
        r"Neutralisation releases heat: the temperature of the mixture rises. Decomposition of limestone needs continuous heating, evaporation takes in heat from the liquid, and ammonium nitrate dissolving makes the solution colder, so these three are endothermic."))
    a(Q("c39", ["energy changes", "graphs"], "moyenne",
        r"{FIG} is an energy profile for a reaction. What is the energy change, $\Delta H$, for the forward reaction?",
        r"$-60\ \text{kJ}$", [r"$+60\ \text{kJ}$", r"$-90\ \text{kJ}$", r"$-240\ \text{kJ}$"],
        r"$\Delta H$ is the energy of the products minus the energy of the reactants. It is negative for an exothermic reaction, because the products are lower in energy. The activation energy is the height of the peak above the reactants.",
        r"$\Delta H=90-150=-60\ \text{kJ}$: the products are lower than the reactants, so the reaction is exothermic. The activation energy is $240-150=90\ \text{kJ}$.",
        piege=r"$-90\ \text{kJ}$ is the activation energy with a minus sign added: the activation energy is never the energy change.",
        fig="profil"))
    a(Q("c40", ["chemical equilibrium"], "moyenne",
        r"Blue hydrated copper(II) sulphate crystals turn white when they are heated. A few drops of water are then added to the white solid. What is observed?",
        r"The solid turns blue and the temperature rises.", [r"The solid stays white and the temperature rises.", r"The solid turns blue and the temperature falls.",
                                                           r"The solid turns black and gives off a gas."],
        r"A reversible reaction can go in either direction when the conditions are changed: $\mathrm{CuSO_4\cdot5H_2O\rightleftharpoons CuSO_4+5H_2O}$. The direction that takes in heat when it goes forward gives out the same amount of heat when it goes backward.",
        r"Heating drives the water off, which takes in heat: blue crystals $\rightarrow$ white solid. Adding water reverses the change: the white anhydrous copper(II) sulphate combines with the water to give the blue hydrated salt, and heat is given out, so the temperature rises. This is used as a test for water.",
        piege=r"The change is reversible, so the colour returns to blue; a fall in temperature would mean that the reverse change is also endothermic, which is impossible."))
    a(Q("c41", ["alkanes and alkenes"], "faible",
        r"Which of the following is the molecular formula of an alkene with four carbon atoms?",
        r"$\mathrm{C_4H_8}$", [r"$\mathrm{C_4H_{10}}$", r"$\mathrm{C_4H_6}$", r"$\mathrm{C_4H_4}$"],
        r"Alkenes have one carbon-carbon double bond and the general formula $\mathrm{C_nH_{2n}}$.",
        r"For $n=4$: $\mathrm{C_4H_{2\times4}}=\mathrm{C_4H_8}$ (butene). $\mathrm{C_4H_{10}}$ is butane, an alkane, and $\mathrm{C_4H_6}$ fits an alkyne or a compound with two double bonds."))
    a(Q("c42", ["alkanes and alkenes", "stoichiometry"], "moyenne",
        r"$100\ \text{cm}^3$ of propane, $\mathrm{C_3H_8}$, is burnt completely in oxygen. What volume of oxygen is needed, with all volumes measured under the same conditions? $\quad\mathrm{C_3H_8+5O_2\rightarrow3CO_2+4H_2O}$",
        r"$500\ \text{cm}^{3}$", [r"$300\ \text{cm}^{3}$", r"$400\ \text{cm}^{3}$", r"$250\ \text{cm}^{3}$"],
        r"At the same temperature and pressure, equal volumes of gases contain equal numbers of molecules, so the coefficients of gases in an equation give volume ratios.",
        r"The equation gives $1$ volume of propane for $5$ volumes of oxygen, so $100\ \text{cm}^3$ of propane needs $5\times100=500\ \text{cm}^3$ of oxygen.",
        piege=r"$300$ and $400$ are the volumes of carbon dioxide and of water vapour formed, read from the wrong coefficient."))
    a(Q("c43", ["alkanes and alkenes"], "faible",
        r"What is produced when a long-chain alkane is cracked?",
        r"A mixture of shorter alkanes and alkenes",
        [r"Only shorter alkanes", r"Longer-chain alkenes and water", r"Carbon dioxide and water only"],
        r"Cracking breaks large hydrocarbon molecules into smaller, more useful ones, by heat and a catalyst. The products always include an alkene.",
        r"For example, $\mathrm{C_{10}H_{22}\rightarrow C_8H_{18}+C_2H_4}$: a shorter alkane and an alkene. Cracking is used because small alkenes are the raw material for plastics and because there is more demand for petrol than for the long-chain fractions."))
    a(Q("c44", ["alcohols and carboxylic acids"], "faible",
        r"Ethanol is heated under reflux with an excess of acidified potassium dichromate(VI) solution. The organic product is",
        r"ethanoic acid", [r"ethene", r"ethane", r"ethyl ethanoate"],
        r"Acidified potassium dichromate(VI) is an oxidising agent. A primary alcohol is oxidised to a carboxylic acid; the colour of the mixture changes from orange to green.",
        r"$\mathrm{CH_3CH_2OH+2[O]\rightarrow CH_3COOH+H_2O}$. Ethanol is oxidised to ethanoic acid. Ethene would need dehydration with concentrated acid; ethyl ethanoate needs ethanoic acid and ethanol with an acid catalyst."))
    a(Q("c45", ["alcohols and carboxylic acids"], "faible",
        r"Which pair of compounds reacts, with a few drops of concentrated sulphuric acid, to form the ester ethyl propanoate?",
        r"Ethanol and propanoic acid", [r"Propanol and ethanoic acid", r"Ethanol and ethanoic acid", r"Ethene and propanoic acid"],
        r"An ester is named from two parts: the alkyl part comes from the alcohol and the second part comes from the acid. Alcohol $+$ carboxylic acid $\rightleftharpoons$ ester $+$ water.",
        r"Ethyl propanoate: ethyl comes from **ethanol** and propanoate comes from **propanoic acid**. Propanol with ethanoic acid gives propyl ethanoate, and ethanol with ethanoic acid gives ethyl ethanoate."))
    a(Q("c46", ["polymers"], "faible",
        r"Poly(chloroethene), also known as PVC, is made from the monomer",
        r"chloroethene", [r"chloroethane", r"ethene", r"tetrafluoroethene"],
        r"A polymer is named after its monomer: the word poly is put in front of the name of the monomer, written in brackets when the name has more than one word.",
        r"The monomer of poly(chloroethene) is chloroethene, $\mathrm{CH_2{=}CHCl}$. Poly(ethene) is named after ethene and PTFE comes from tetrafluoroethene. Chloroethane has a different formula, $\mathrm{C_2H_5Cl}$, and gives a different compound."))
    a(Q("c47", ["soaps and detergents"], "faible",
        r"Soap is made by heating a vegetable oil or an animal fat with",
        r"concentrated sodium hydroxide solution", [r"dilute hydrochloric acid", r"distilled water only", r"ethanol only"],
        r"Fats and oils are esters. Heating them with a strong alkali is alkaline hydrolysis, called saponification.",
        r"$\text{fat or oil}+\text{sodium hydroxide}\rightarrow\text{soap (sodium salt of a fatty acid)}+\text{glycerol}$. An acid would not give a salt of the fatty acid, and water or ethanol alone do not hydrolyse the ester."))
    a(Q("c48", ["water, air and pollution"], "faible",
        r"Which gas, released when fuels containing sulphur are burnt, is mainly responsible for acid rain?",
        r"Sulphur dioxide", [r"Carbon monoxide", r"Methane", r"Nitrogen"],
        r"Acid rain forms when acidic gases dissolve in rain water. The main gases responsible are sulphur dioxide and oxides of nitrogen.",
        r"Burning a fuel that contains sulphur forms sulphur dioxide, which dissolves in water to give sulphurous acid and is oxidised further to sulphuric acid. Carbon monoxide is poisonous, methane is a greenhouse gas, and nitrogen is a harmless gas that makes up most of the air."))
    a(Q("c49", ["apparatus and experiments"], "faible",
        r"Which method is used to separate ethanol (boiling point $78\,^\circ\text{C}$) from a mixture of ethanol and water (boiling point $100\,^\circ\text{C}$)?",
        r"Fractional distillation", [r"Filtration", r"Evaporation to dryness", r"Crystallisation"],
        r"Fractional distillation separates miscible liquids that have different boiling points. The liquid with the lower boiling point distils over first.",
        r"Ethanol and water mix completely, so filtration cannot be used, and evaporating to dryness would lose the ethanol. When the mixture is heated, the vapour is richer in ethanol, which has the lower boiling point; it rises up the fractionating column, is condensed and is collected."))
    a(Q("c50", ["apparatus and experiments"], "faible",
        r"Which technique is used to separate the coloured dyes in black ink?",
        r"Chromatography", [r"Filtration", r"Simple distillation", r"Sublimation"],
        r"Chromatography separates substances that dissolve in a solvent, because they move at different speeds over a paper.",
        r"A spot of black ink is placed on chromatography paper that stands in a solvent. The solvent rises through the paper and carries each dye at its own speed, so the dyes separate into coloured spots. Filtration separates a solid from a liquid, distillation separates liquids, and sublimation separates a solid that turns to gas."))
    return q
