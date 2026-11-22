r"""Les 50 QCM de l'epreuve inedite GCE A Level Chemistry Paper 1 n.1 (50 x 1 point, 90 min).

Structure mesuree sur les Paper 1 reels 2024, 2025 et 2026 (un seul JSON de 50 questions chacun) : 35 questions a meilleure reponse (themes melanges),
10 questions de completion multiple (reponses numerotees 1 a 3, options FIXES « 1, 2 and 3 are all correct / 1 and 2 only / 2 and 3 only / 3 only »)
et 5 questions d'assertion-raison (deux enonces, quatre options FIXES A a D) ; la consigne imprimee est repetee dans l'enonce de chaque question du bloc.
Aucune donnee, aucun enonce, aucun jeu d'options repris d'un sujet reel. Chaque question : enonce, bonne option, trois distracteurs avec l'erreur type qui y mene,
rappel (un seul paragraphe), resolution, valeur de controle recalculee par verifier_reponses_chemistry_al_p1.py. Les lettres des cles des 35 premieres questions
sont placees par le GENERATEUR (13/13/12/12, jamais trois de suite) ; celles des blocs a options imposees decoulent du contenu.
Chaines BRUTES (r"...") : une commande LaTeX a backslash simple dans une chaine ordinaire devient un caractere de controle.
"""

MC_PLAGE = "36-45"
AR_PLAGE = "46-50"
OPTIONS_MC = ["1, 2 and 3 are all correct", "1 and 2 only are correct", "2 and 3 only are correct", "3 only is correct"]
OPTIONS_AR = [
    "Both statements are true and the second statement is a correct explanation of the first statement",
    "Both statements are true but the second statement is not a correct explanation of the first statement",
    "The first statement is true but the second statement is false",
    "The first statement is false but the second statement is true",
]
MC_SETS = [(1, 1, 1), (1, 1, 0), (0, 1, 1), (0, 0, 1)]  # correspondance option a-d / enonces corrects

INSTR_MC = (
    f"**Instructions (Questions {MC_PLAGE}):** for each of these questions, ONE or MORE of the responses numbered 1 to 3 is (are) correct. "
    "Decide which response(s) is (are) correct. Then choose: A. if 1, 2 and 3 are all correct; B. if 1 and 2 only are correct; "
    "C. if 2 and 3 only are correct; D. if 3 only is correct."
)
INSTR_AR = (
    f"**Instructions (Questions {AR_PLAGE}):** each question consists of a statement in the first column followed by a statement in the second column. "
    "Decide whether each statement is TRUE or FALSE, and whether the second statement, if true, is a correct explanation of the first. Then choose: "
    "A. if both statements are true and the second statement is a correct explanation of the first; "
    "B. if both statements are true but the second statement is NOT a correct explanation of the first; "
    "C. if the first statement is true but the second statement is false; D. if the first statement is false but the second statement is true."
)

QS = []


def Q(themes, diff, stem, key, dist, rappel, sol, val, conseil=None):
    assert len(dist) == 3 and all(len(d) == 2 for d in dist), stem[:40]
    texts = [key] + [d[0] for d in dist]
    assert len(set(texts)) == 4, ("options en double", stem[:50])
    assert "\n\n" not in rappel, "rappel : un seul paragraphe"
    QS.append(dict(kind="ba", themes=themes, diff=diff, stem=stem, key=key, dist=dist, rappel=rappel, sol=sol, val=val, conseil=conseil, tv=None))


def QM(themes, diff, lead, statements, tv, rappel, sol, conseil=None):
    """Completion multiple : 3 enonces numerotes ; tv = verite de chacun ; la cle decoule de tv."""
    assert len(statements) == 3 and tuple(tv) in MC_SETS, (lead[:40], tv)
    assert "\n\n" not in rappel
    stem = INSTR_MC + "\n\n" + lead + "\n\n" + "\n".join(f"{i}. {s}" for i, s in enumerate(statements, start=1))
    key = OPTIONS_MC[MC_SETS.index(tuple(tv))]
    QS.append(dict(kind="mc", themes=themes, diff=diff, stem=stem, key=key, dist=None, rappel=rappel, sol=sol, val=tuple(tv), conseil=conseil, tv=tuple(tv)))


def QA(themes, diff, first, second, t1, t2, expl, rappel, sol, conseil=None):
    """Assertion-raison : t1, t2 = verite des deux enonces ; expl = le second explique-t-il le premier (si les deux sont vrais)."""
    assert (t1 or t2) and "\n\n" not in rappel
    if t1 and t2:
        key = OPTIONS_AR[0] if expl else OPTIONS_AR[1]
    elif t1:
        key = OPTIONS_AR[2]
    else:
        key = OPTIONS_AR[3]
    stem = INSTR_AR + "\n\n| First statement | Second statement |\n|---|---|\n| " + first + " | " + second + " |"
    QS.append(dict(kind="ar", themes=themes, diff=diff, stem=stem, key=key, dist=None, rappel=rappel, sol=sol, val=(int(t1), int(t2), int(bool(expl))), conseil=conseil, tv=(int(t1), int(t2), int(bool(expl)))))


def questions():
    return QS


def raisons(q):
    """Raison de chaque option fausse (lettre -> texte) pour les questions a options imposees."""
    out = {}
    if q["kind"] == "mc":
        t = q["tv"]
        for lettre, s in zip("abcd", MC_SETS):
            if s == t:
                continue
            parts = []
            for i in range(3):
                if s[i] and not t[i]:
                    parts.append(f"counts statement {i + 1} as correct although it is false")
                elif t[i] and not s[i]:
                    parts.append(f"leaves out statement {i + 1}, which is correct")
            out[lettre] = " and ".join(parts)
    elif q["kind"] == "ar":
        t1, t2, ex = q["tv"]
        reel = (t1, t2, ex if (t1 and t2) else 0)
        cand = {"a": (1, 1, 1), "b": (1, 1, 0), "c": (1, 0, 0), "d": (0, 1, 0)}
        for lettre, (b1, b2, be) in cand.items():
            if (b1, b2, be) == reel:
                continue
            parts = []
            if b1 != t1:
                parts.append("judges the first statement " + ("true" if b1 else "false") + " although it is " + ("true" if t1 else "false"))
            if b2 != t2:
                parts.append("judges the second statement " + ("true" if b2 else "false") + " although it is " + ("true" if t2 else "false"))
            if not parts:
                parts.append("treats the second statement as " + ("a correct explanation" if be else "unrelated to the first") + " although it is " + ("not " if be else "") + "an explanation")
            out[lettre] = " and ".join(parts)
    return out


# ===================================================================== 1 a 35 : meilleure reponse
# 1
Q(["mole concept"], "faible",
  r"How many moles of nitrate ions are present in $250\ \mathrm{cm^{3}}$ of $0.40\ \mathrm{mol\ dm^{-3}}$ aluminium nitrate, $\mathrm{Al(NO_{3})_{3}}$?",
  r"$0.30\ \mathrm{mol}$",
  [(r"$0.10\ \mathrm{mol}$", r"counts the formula units of $\mathrm{Al(NO_{3})_{3}}$ and forgets that each one gives three nitrate ions"),
   (r"$1.2\ \mathrm{mol}$", r"multiplies the concentration by $3$ and forgets to use the volume of $0.250\ \mathrm{dm^{3}}$"),
   (r"$0.40\ \mathrm{mol}$", r"counts the aluminium ion as well and uses four ions per formula unit")],
  r"The amount of solute is $n=c\times V$ with $V$ in $\mathrm{dm^{3}}$, and the amount of an ion is the amount of the compound multiplied by the number of that ion in the formula.",
  r"$n(\mathrm{Al(NO_{3})_{3}})=0.40\times0.250=0.100\ \mathrm{mol}$. Each formula unit releases three nitrate ions, so $n(\mathrm{NO_{3}^{-}})=3\times0.100=0.30\ \mathrm{mol}$.",
  0.30)
# 2
Q(["stoichiometry"], "moyenne",
  r"A piece of magnesium ribbon of mass $0.486\ \mathrm{g}$ reacts completely with excess dilute hydrochloric acid: $\mathrm{Mg(s)+2HCl(aq)\rightarrow MgCl_{2}(aq)+H_{2}(g)}$. What volume of hydrogen is produced at $25\ ^{\circ}\mathrm{C}$? ($A_{r}$: Mg $=24.3$; molar volume of a gas at $25\ ^{\circ}\mathrm{C}=24\ \mathrm{dm^{3}\ mol^{-1}}$)",
  r"$480\ \mathrm{cm^{3}}$",
  [(r"$240\ \mathrm{cm^{3}}$", r"takes two moles of magnesium for each mole of hydrogen"),
   (r"$960\ \mathrm{cm^{3}}$", r"takes two moles of hydrogen for each mole of magnesium, using the coefficient of the acid"),
   (r"$48.0\ \mathrm{cm^{3}}$", r"converts $\mathrm{dm^{3}}$ into $\mathrm{cm^{3}}$ with a factor of $100$ instead of $1000$")],
  r"Use the mole ratio of the balanced equation to go from the amount of the reactant to the amount of gas, then multiply by the molar volume.",
  r"$n(\mathrm{Mg})=\dfrac{0.486}{24.3}=0.0200\ \mathrm{mol}$. The ratio $\mathrm{Mg:H_{2}}$ is $1:1$, so $n(\mathrm{H_{2}})=0.0200\ \mathrm{mol}$ and $V=0.0200\times24=0.480\ \mathrm{dm^{3}}=480\ \mathrm{cm^{3}}$.",
  480.0)
# 3
Q(["stoichiometry"], "moyenne",
  r"Ethanol reacts with hydrogen bromide: $\mathrm{C_{2}H_{5}OH+HBr\rightarrow C_{2}H_{5}Br+H_{2}O}$. A mass of $4.60\ \mathrm{g}$ of ethanol ($M_{r}=46.0$) gives $8.72\ \mathrm{g}$ of bromoethane ($M_{r}=109.0$). What is the percentage yield of bromoethane?",
  r"$80.0\%$",
  [(r"$125\%$", r"inverts the ratio and divides the theoretical mass by the actual mass"),
   (r"$190\%$", r"divides the mass of bromoethane by the mass of ethanol"),
   (r"$40.0\%$", r"takes two moles of bromoethane for each mole of ethanol")],
  r"Percentage yield $=\dfrac{\text{actual yield}}{\text{theoretical yield}}\times100$, where the theoretical yield comes from the amount of the reactant that is not in excess and the mole ratio of the equation.",
  r"$n(\mathrm{C_{2}H_{5}OH})=\dfrac{4.60}{46.0}=0.100\ \mathrm{mol}$, so the theoretical amount of $\mathrm{C_{2}H_{5}Br}$ is $0.100\ \mathrm{mol}$, that is $0.100\times109.0=10.9\ \mathrm{g}$. The yield is $\dfrac{8.72}{10.9}\times100=80.0\%$.",
  80.0)
# 4
Q(["atomic structure"], "faible",
  r"How many protons, neutrons and electrons are present in one ion of $^{79}_{35}\mathrm{Br}^{-}$?",
  r"$35$ protons, $44$ neutrons, $36$ electrons",
  [(r"$35$ protons, $44$ neutrons, $34$ electrons", r"removes an electron instead of adding one to form the negative ion"),
   (r"$35$ protons, $44$ neutrons, $35$ electrons", r"ignores the charge of the ion"),
   (r"$44$ protons, $35$ neutrons, $36$ electrons", r"swaps the numbers of protons and neutrons")],
  r"For $^{A}_{Z}\mathrm{X}^{q}$ the number of protons is $Z$, the number of neutrons is $A-Z$ and the number of electrons is $Z-q$.",
  r"Protons: $Z=35$. Neutrons: $79-35=44$. Electrons: $35-(-1)=36$, because the ion carries one extra electron.",
  (35, 44, 36))
# 5
Q(["electronic configuration"], "moyenne",
  r"Which is the electronic configuration of the $\mathrm{Ni^{2+}}$ ion? (Proton number of nickel $=28$)",
  r"$\mathrm{1s^{2}2s^{2}2p^{6}3s^{2}3p^{6}3d^{8}}$",
  [(r"$\mathrm{1s^{2}2s^{2}2p^{6}3s^{2}3p^{6}3d^{6}4s^{2}}$", r"removes two electrons from the $\mathrm{3d}$ sub-shell and keeps the $\mathrm{4s}$ electrons"),
   (r"$\mathrm{1s^{2}2s^{2}2p^{6}3s^{2}3p^{6}3d^{7}4s^{1}}$", r"removes one $\mathrm{4s}$ electron and one $\mathrm{3d}$ electron, although both $\mathrm{4s}$ electrons leave first"),
   (r"$\mathrm{1s^{2}2s^{2}2p^{6}3s^{2}3p^{6}3d^{9}}$", r"removes only one electron, which gives $\mathrm{Ni^{+}}$")],
  r"The $\mathrm{4s}$ sub-shell is filled before $\mathrm{3d}$ in an atom, but the $\mathrm{4s}$ electrons are the first to be lost when a transition element forms a positive ion.",
  r"The nickel atom is $\mathrm{[Ar]3d^{8}4s^{2}}$. To form $\mathrm{Ni^{2+}}$, two electrons are removed, and they are the two $\mathrm{4s}$ electrons, which leaves $\mathrm{[Ar]3d^{8}}$ with $26$ electrons.",
  "3d8")
# 6
Q(["ionisation energy"], "moyenne",
  r"The first five successive ionisation energies of an element X, in $\mathrm{kJ\ mol^{-1}}$, are $590$, $1150$, $4910$, $6480$ and $8140$. In which group of the Periodic Table is X?",
  r"Group 2",
  [(r"Group 1", r"takes the rise from the first to the second value as the large jump"),
   (r"Group 3", r"counts the electrons up to the third value instead of stopping before the large jump"),
   (r"Group 5", r"counts all five values that are listed")],
  r"A very large rise between two successive ionisation energies shows that the next electron is removed from an inner shell, so the number of electrons removed before the jump equals the group number.",
  r"The ratios of successive values are $1150/590\approx1.9$, $4910/1150\approx4.3$, $6480/4910\approx1.3$ and $8140/6480\approx1.3$. The large jump comes after the second electron, so X has two outer electrons and is in Group 2.",
  2)
# 7
Q(["chemical bonding"], "faible",
  r"Which species contains a dative covalent (co-ordinate) bond?",
  r"$\mathrm{NH_{4}^{+}}$",
  [(r"$\mathrm{CH_{4}}$", r"believes that every bond to hydrogen is dative, although each atom supplies one electron to each bond"),
   (r"$\mathrm{NH_{3}}$", r"counts the lone pair of nitrogen as a bond, although it is not shared with another atom"),
   (r"$\mathrm{H_{2}O}$", r"counts the lone pairs of oxygen as bonds, although they are not shared")],
  r"A dative covalent bond is a shared pair of electrons in which both electrons come from the same atom; it appears when an atom forms more bonds than its usual valency.",
  r"Nitrogen normally forms three bonds. In $\mathrm{NH_{4}^{+}}$ it has four, and the fourth bond forms when the lone pair of $\mathrm{NH_{3}}$ is shared with an $\mathrm{H^{+}}$ ion, which has no electrons. $\mathrm{CH_{4}}$, $\mathrm{NH_{3}}$ and $\mathrm{H_{2}O}$ have only ordinary covalent bonds.",
  "NH4+")
# 8
Q(["molecular shapes"], "faible",
  r"Which molecule has an octahedral shape?",
  r"$\mathrm{SF_{6}}$",
  [(r"$\mathrm{PCl_{5}}$", r"gives the trigonal bipyramidal shape of five bonding pairs"),
   (r"$\mathrm{SiCl_{4}}$", r"gives the tetrahedral shape of four bonding pairs"),
   (r"$\mathrm{BCl_{3}}$", r"gives the trigonal planar shape of three bonding pairs")],
  r"The shape follows from the number of electron pairs round the central atom: two to six pairs with no lone pair give linear, trigonal planar, tetrahedral, trigonal bipyramidal and octahedral shapes.",
  r"Sulphur has six outer electrons and forms six bonds to fluorine, so there are six bonding pairs and no lone pair. The pairs point to the corners of an octahedron, with bond angles of $90^{\circ}$.",
  "SF6")
# 9
Q(["intermolecular forces"], "moyenne",
  r"Which compound has the highest boiling point?",
  r"$\mathrm{CH_{3}CH_{2}CH_{2}CH_{2}OH}$ (butan-1-ol)",
  [(r"$\mathrm{CH_{3}CH_{2}OCH_{2}CH_{3}}$ (ethoxyethane)", r"relies on permanent dipoles only, although it has no hydrogen atom bonded to oxygen to form hydrogen bonds"),
   (r"$\mathrm{CH_{3}CH_{2}CH_{2}CHO}$ (butanal)", r"relies on dipole-dipole forces only, although the molecule cannot form hydrogen bonds with itself"),
   (r"$\mathrm{CH_{3}CH_{2}CH_{2}CH_{2}CH_{3}}$ (pentane)", r"relies on London forces only, which are the weakest forces in this set")],
  r"For molecules of similar relative molecular mass, the boiling point rises with the strength of the strongest intermolecular force: London forces, then permanent dipole-dipole forces, then hydrogen bonds.",
  r"The four compounds have relative molecular masses of $72$ to $74$, so London forces are of similar size. Only butan-1-ol has an O-H group and forms hydrogen bonds between its molecules, so it needs the most energy to separate them (boiling point about $390\ \mathrm{K}$).",
  "butan-1-ol")
# 10
Q(["crystal structure"], "faible",
  r"In the unit cell of sodium chloride the chloride ions are at the corners and at the centres of the faces of a cube, and the sodium ions are at the centres of the $12$ edges and at the centre of the cube. How many sodium ions belong to one unit cell?",
  r"$4$",
  [(r"$13$", r"counts every sodium ion that is drawn as a whole ion, without sharing the ions on the edges"),
   (r"$6$", r"gives the co-ordination number of the sodium ion"),
   (r"$8$", r"gives the number of corners of the cube")],
  r"An ion on a corner is shared by $8$ cells, on an edge by $4$ cells, on a face by $2$ cells, and an ion inside the cell belongs to it entirely.",
  r"Edge sites: $12\times\dfrac14=3$. Centre of the cube: $1$. Total $3+1=4$ sodium ions. For the chloride ions, $8\times\dfrac18+6\times\dfrac12=4$, so the ratio $\mathrm{Na^{+}:Cl^{-}}$ is $1:1$, as the formula $\mathrm{NaCl}$ requires.",
  4)
# 11
Q(["enthalpy changes", "hess's law"], "moyenne",
  r"The standard enthalpy changes of formation, in $\mathrm{kJ\ mol^{-1}}$, are $\mathrm{C_{2}H_{5}OH(l)}=-277$, $\mathrm{CO_{2}(g)}=-394$ and $\mathrm{H_{2}O(l)}=-286$. What is the standard enthalpy change of combustion of ethanol, $\mathrm{C_{2}H_{5}OH(l)+3O_{2}(g)\rightarrow2CO_{2}(g)+3H_{2}O(l)}$, in $\mathrm{kJ\ mol^{-1}}$?",
  r"$-1369$",
  [(r"$-1923$", r"adds the enthalpy of formation of ethanol instead of subtracting it"),
   (r"$-1646$", r"leaves out the enthalpy of formation of the reactant ethanol"),
   (r"$-403$", r"does not multiply the enthalpies of formation by the coefficients $2$ and $3$")],
  r"By Hess's law, $\Delta H_{c}=\sum\Delta H_{f}(\text{products})-\sum\Delta H_{f}(\text{reactants})$, each term being multiplied by its coefficient; the value for an element in its standard state is zero.",
  r"$\sum\Delta H_{f}(\text{products})=2(-394)+3(-286)=-788-858=-1646$. $\sum\Delta H_{f}(\text{reactants})=-277+0=-277$. So $\Delta H_{c}=-1646-(-277)=-1369\ \mathrm{kJ\ mol^{-1}}$.",
  -1369)
# 12
Q(["enthalpy changes", "hess's law"], "elevee",
  r"Use the data, in $\mathrm{kJ\ mol^{-1}}$, to calculate the lattice enthalpy of formation of sodium chloride: enthalpy of formation of $\mathrm{NaCl(s)}=-411$; enthalpy of atomisation of sodium $=+107$; first ionisation energy of sodium $=+496$; enthalpy of atomisation of chlorine, per mole of chlorine atoms, $=+122$; first electron affinity of chlorine $=-349$.",
  r"$-787\ \mathrm{kJ\ mol^{-1}}$",
  [(r"$+787\ \mathrm{kJ\ mol^{-1}}$", r"gives the lattice dissociation enthalpy, which has the opposite sign"),
   (r"$-1485\ \mathrm{kJ\ mol^{-1}}$", r"adds the electron affinity with the wrong sign when closing the cycle"),
   (r"$-909\ \mathrm{kJ\ mol^{-1}}$", r"uses $+244$, the energy for a whole $\mathrm{Cl_{2}}$ molecule, instead of the $+122$ needed for one mole of atoms")],
  r"In a Born-Haber cycle the enthalpy of formation equals the sum of the enthalpies of atomisation, ionisation, electron affinity and lattice formation, taken in the direction of the cycle.",
  r"$\Delta H_{f}=\Delta H_{at}(\mathrm{Na})+\mathrm{IE}(\mathrm{Na})+\Delta H_{at}(\mathrm{Cl})+\mathrm{EA}(\mathrm{Cl})+\Delta H_{\text{lattice}}$. So $-411=107+496+122-349+\Delta H_{\text{lattice}}=376+\Delta H_{\text{lattice}}$ and $\Delta H_{\text{lattice}}=-787\ \mathrm{kJ\ mol^{-1}}$.",
  -787)
# 13
Q(["enthalpy changes"], "moyenne",
  r"A mass of $0.600\ \mathrm{g}$ of propan-1-ol ($M_{r}=60.0$) is burned and all the heat produced raises the temperature of $200\ \mathrm{g}$ of water by $24.2\ \mathrm{K}$. The specific heat capacity of water is $4.18\ \mathrm{J\ g^{-1}\ K^{-1}}$. What is the enthalpy change of combustion of propan-1-ol, in $\mathrm{kJ\ mol^{-1}}$?",
  r"$-2020$",
  [(r"$+2020$", r"forgets that the reaction gives out heat, so the enthalpy change is negative"),
   (r"$-20.2$", r"gives the heat absorbed in kJ without dividing by the amount of propan-1-ol"),
   (r"$-2.02$", r"divides by $1000$ twice when converting joules into kilojoules")],
  r"The heat absorbed is $q=mc\Delta T$, and the molar enthalpy change is $\Delta H=-\dfrac{q}{n}$ for an exothermic reaction, with $q$ converted to kJ.",
  r"$q=200\times4.18\times24.2=20231\ \mathrm{J}=20.2\ \mathrm{kJ}$. $n=\dfrac{0.600}{60.0}=0.0100\ \mathrm{mol}$. $\Delta H=-\dfrac{20.2}{0.0100}=-2020\ \mathrm{kJ\ mol^{-1}}$.",
  -2020)
# 14
Q(["chemical equilibrium"], "moyenne",
  r"For the equilibrium $\mathrm{N_{2}O_{4}(g)\rightleftharpoons2NO_{2}(g)}$ at a fixed temperature, the equilibrium concentrations are $[\mathrm{N_{2}O_{4}}]=0.040\ \mathrm{mol\ dm^{-3}}$ and $[\mathrm{NO_{2}}]=0.12\ \mathrm{mol\ dm^{-3}}$. What is the value of $K_{c}$, in $\mathrm{mol\ dm^{-3}}$?",
  r"$0.36$",
  [(r"$2.8$", r"inverts the expression and puts the reactant over the product"),
   (r"$3.0$", r"does not square $[\mathrm{NO_{2}}]$ although its coefficient is $2$"),
   (r"$1.4$", r"multiplies $[\mathrm{NO_{2}}]$ by its coefficient and then squares it")],
  r"For $a\mathrm{A}\rightleftharpoons b\mathrm{B}$ the equilibrium constant is $K_{c}=\dfrac{[\mathrm{B}]^{b}}{[\mathrm{A}]^{a}}$, with each concentration raised to the power of its coefficient.",
  r"$K_{c}=\dfrac{[\mathrm{NO_{2}}]^{2}}{[\mathrm{N_{2}O_{4}}]}=\dfrac{(0.12)^{2}}{0.040}=\dfrac{0.0144}{0.040}=0.36\ \mathrm{mol\ dm^{-3}}$.",
  0.36)
# 15
Q(["alcohols and carboxylic acids"], "faible",
  r"Which alcohol is oxidised by hot acidified potassium dichromate(VI) to a ketone?",
  r"$\mathrm{CH_{3}CH_{2}CH(OH)CH_{3}}$ (butan-2-ol)",
  [(r"$\mathrm{CH_{3}CH_{2}CH_{2}CH_{2}OH}$ (butan-1-ol)", r"is a primary alcohol, which gives an aldehyde and then a carboxylic acid"),
   (r"$\mathrm{(CH_{3})_{3}COH}$ (2-methylpropan-2-ol)", r"is a tertiary alcohol, which is not oxidised under these conditions"),
   (r"$\mathrm{(CH_{3})_{2}CHCH_{2}OH}$ (2-methylpropan-1-ol)", r"is a primary alcohol, which gives an aldehyde and then a carboxylic acid")],
  r"Primary alcohols are oxidised to aldehydes and then to carboxylic acids, secondary alcohols to ketones, and tertiary alcohols are not oxidised by acidified dichromate(VI).",
  r"A ketone forms only from a secondary alcohol, in which the carbon bearing the OH group carries one hydrogen atom and two alkyl groups. Butan-2-ol is $\mathrm{CH_{3}CH(OH)C_{2}H_{5}}$ and is oxidised to butanone.",
  "butan-2-ol")
# 16
Q(["pH calculations"], "faible",
  r"At $25\ ^{\circ}\mathrm{C}$, $K_{w}=1.00\times10^{-14}\ \mathrm{mol^{2}\ dm^{-6}}$. What is the pH of $0.0050\ \mathrm{mol\ dm^{-3}}$ barium hydroxide, $\mathrm{Ba(OH)_{2}}$?",
  r"$12.00$",
  [(r"$11.70$", r"takes $[\mathrm{OH^{-}}]$ equal to the concentration of $\mathrm{Ba(OH)_{2}}$ and forgets that each formula unit gives two hydroxide ions"),
   (r"$2.00$", r"gives the pOH instead of the pH"),
   (r"$2.30$", r"gives the pOH calculated with $[\mathrm{OH^{-}}]=0.0050\ \mathrm{mol\ dm^{-3}}$")],
  r"For a strong base, $[\mathrm{OH^{-}}]$ is the concentration of the base multiplied by the number of hydroxide ions per formula unit, and $\mathrm{pH}=-\log_{10}\left(\dfrac{K_{w}}{[\mathrm{OH^{-}}]}\right)$.",
  r"$[\mathrm{OH^{-}}]=2\times0.0050=0.010\ \mathrm{mol\ dm^{-3}}$. $[\mathrm{H^{+}}]=\dfrac{1.00\times10^{-14}}{0.010}=1.0\times10^{-12}\ \mathrm{mol\ dm^{-3}}$, so $\mathrm{pH}=12.00$.",
  12.0)
# 17
Q(["pH calculations"], "moyenne",
  r"A weak monobasic acid HA has $K_{a}=1.0\times10^{-5}\ \mathrm{mol\ dm^{-3}}$ at $25\ ^{\circ}\mathrm{C}$. What is the pH of a $0.100\ \mathrm{mol\ dm^{-3}}$ solution of HA?",
  r"$3.00$",
  [(r"$1.00$", r"treats the acid as fully ionised"),
   (r"$5.00$", r"gives the $\mathrm{p}K_{a}$ of the acid"),
   (r"$6.00$", r"takes $[\mathrm{H^{+}}]=K_{a}\times c$ and forgets the square root")],
  r"For a weak acid that is only slightly ionised, $K_{a}=\dfrac{[\mathrm{H^{+}}]^{2}}{[\mathrm{HA}]}$, so $[\mathrm{H^{+}}]=\sqrt{K_{a}c}$.",
  r"$[\mathrm{H^{+}}]=\sqrt{1.0\times10^{-5}\times0.100}=\sqrt{1.0\times10^{-6}}=1.0\times10^{-3}\ \mathrm{mol\ dm^{-3}}$, so $\mathrm{pH}=3.00$.",
  3.0)
# 18
Q(["pH calculations", "acids bases and salts"], "moyenne",
  r"A buffer solution contains $0.20\ \mathrm{mol\ dm^{-3}}$ ethanoic acid and $0.10\ \mathrm{mol\ dm^{-3}}$ sodium ethanoate. $K_{a}$ of ethanoic acid $=1.8\times10^{-5}\ \mathrm{mol\ dm^{-3}}$. What is the pH of the buffer?",
  r"$4.44$",
  [(r"$5.05$", r"inverts the ratio and puts the acid over the salt in the logarithm"),
   (r"$4.74$", r"assumes that the acid and its salt have equal concentrations, so the logarithm is zero"),
   (r"$2.72$", r"calculates the pH of the $0.20\ \mathrm{mol\ dm^{-3}}$ acid alone and ignores the salt")],
  r"In a buffer of a weak acid and its salt, $[\mathrm{H^{+}}]=K_{a}\dfrac{[\text{acid}]}{[\text{salt}]}$, so $\mathrm{pH}=\mathrm{p}K_{a}+\log_{10}\dfrac{[\text{salt}]}{[\text{acid}]}$.",
  r"$[\mathrm{H^{+}}]=1.8\times10^{-5}\times\dfrac{0.20}{0.10}=3.6\times10^{-5}\ \mathrm{mol\ dm^{-3}}$, so $\mathrm{pH}=-\log_{10}(3.6\times10^{-5})=4.44$.",
  4.44)
# 19
Q(["acids bases and salts"], "faible",
  r"A volume of $25.0\ \mathrm{cm^{3}}$ of sulphuric acid is neutralised by $20.0\ \mathrm{cm^{3}}$ of $0.150\ \mathrm{mol\ dm^{-3}}$ sodium hydroxide: $\mathrm{H_{2}SO_{4}+2NaOH\rightarrow Na_{2}SO_{4}+2H_{2}O}$. What is the concentration of the sulphuric acid?",
  r"$0.0600\ \mathrm{mol\ dm^{-3}}$",
  [(r"$0.120\ \mathrm{mol\ dm^{-3}}$", r"uses a $1:1$ ratio of acid to alkali"),
   (r"$0.240\ \mathrm{mol\ dm^{-3}}$", r"takes two moles of acid for each mole of alkali, which inverts the ratio"),
   (r"$0.0300\ \mathrm{mol\ dm^{-3}}$", r"halves the amount of acid a second time")],
  r"In a titration, find the amount of the known solution from $n=cV$, use the mole ratio of the equation to find the amount of the other reagent, then divide by its volume.",
  r"$n(\mathrm{NaOH})=0.0200\times0.150=3.00\times10^{-3}\ \mathrm{mol}$. The ratio $\mathrm{H_{2}SO_{4}:NaOH}$ is $1:2$, so $n(\mathrm{H_{2}SO_{4}})=1.50\times10^{-3}\ \mathrm{mol}$ and $c=\dfrac{1.50\times10^{-3}}{0.0250}=0.0600\ \mathrm{mol\ dm^{-3}}$.",
  0.06)
# 20
Q(["redox reactions"], "moyenne",
  r"In acidic solution, $\mathrm{MnO_{4}^{-}+8H^{+}+5Fe^{2+}\rightarrow Mn^{2+}+5Fe^{3+}+4H_{2}O}$. A volume of $25.0\ \mathrm{cm^{3}}$ of an iron(II) solution needs $20.0\ \mathrm{cm^{3}}$ of $0.0200\ \mathrm{mol\ dm^{-3}}$ potassium manganate(VII) for complete reaction. What is the concentration of $\mathrm{Fe^{2+}}$ in the solution?",
  r"$0.0800\ \mathrm{mol\ dm^{-3}}$",
  [(r"$0.0160\ \mathrm{mol\ dm^{-3}}$", r"uses a $1:1$ ratio of manganate(VII) to iron(II)"),
   (r"$0.128\ \mathrm{mol\ dm^{-3}}$", r"multiplies by $8$, the coefficient of $\mathrm{H^{+}}$, instead of by $5$"),
   (r"$0.00320\ \mathrm{mol\ dm^{-3}}$", r"divides by $5$ instead of multiplying by $5$")],
  r"In a redox titration the mole ratio comes from the balanced ionic equation: one mole of $\mathrm{MnO_{4}^{-}}$ reacts with five moles of $\mathrm{Fe^{2+}}$.",
  r"$n(\mathrm{MnO_{4}^{-}})=0.0200\times0.0200=4.00\times10^{-4}\ \mathrm{mol}$. $n(\mathrm{Fe^{2+}})=5\times4.00\times10^{-4}=2.00\times10^{-3}\ \mathrm{mol}$. $c=\dfrac{2.00\times10^{-3}}{0.0250}=0.0800\ \mathrm{mol\ dm^{-3}}$.",
  0.08)
# 21
Q(["halogens", "qualitative analysis"], "faible",
  r"A halide solution is acidified with dilute nitric acid and aqueous silver nitrate is added. A cream precipitate forms. It does not dissolve in dilute aqueous ammonia but it dissolves in concentrated aqueous ammonia. Which halide ion is present?",
  r"$\mathrm{Br^{-}}$",
  [(r"$\mathrm{Cl^{-}}$", r"gives a white precipitate that already dissolves in dilute aqueous ammonia"),
   (r"$\mathrm{I^{-}}$", r"gives a yellow precipitate that does not dissolve even in concentrated aqueous ammonia"),
   (r"$\mathrm{F^{-}}$", r"gives no precipitate, because silver fluoride is soluble in water")],
  r"The silver halides differ in colour and in solubility in ammonia: $\mathrm{AgCl}$ is white and soluble in dilute ammonia, $\mathrm{AgBr}$ is cream and soluble only in concentrated ammonia, $\mathrm{AgI}$ is yellow and insoluble in both.",
  r"A cream precipitate that dissolves in concentrated but not in dilute ammonia is silver bromide, $\mathrm{AgBr}$, so the halide ion is the bromide ion.",
  "Br-")
# 22
Q(["oxidation states"], "moyenne",
  r"In which reaction does hydrogen peroxide act as both an oxidising agent and a reducing agent (disproportionation)?",
  r"$\mathrm{2H_{2}O_{2}\rightarrow2H_{2}O+O_{2}}$",
  [(r"$\mathrm{H_{2}O_{2}+2I^{-}+2H^{+}\rightarrow I_{2}+2H_{2}O}$", r"shows oxygen only being reduced, from $-1$ to $-2$"),
   (r"$\mathrm{5H_{2}O_{2}+2MnO_{4}^{-}+6H^{+}\rightarrow2Mn^{2+}+8H_{2}O+5O_{2}}$", r"shows oxygen only being oxidised, from $-1$ to $0$"),
   (r"$\mathrm{H_{2}O_{2}+SO_{2}\rightarrow H_{2}SO_{4}}$", r"shows oxygen only being reduced, from $-1$ to $-2$")],
  r"Disproportionation is a redox reaction in which the same element is both oxidised and reduced, so its oxidation number rises in one product and falls in another.",
  r"In $\mathrm{H_{2}O_{2}}$ oxygen is $-1$. In $\mathrm{2H_{2}O_{2}\rightarrow2H_{2}O+O_{2}}$ it falls to $-2$ in water and rises to $0$ in $\mathrm{O_{2}}$, so the same element is reduced and oxidised. In the other three equations oxygen changes in one direction only.",
  "2H2O2")
# 23
Q(["electrode potentials"], "faible",
  r"$\mathrm{Fe^{3+}(aq)+e^{-}\rightleftharpoons Fe^{2+}(aq)}$, $E^{\ominus}=+0.77\ \mathrm{V}$. $\mathrm{Sn^{4+}(aq)+2e^{-}\rightleftharpoons Sn^{2+}(aq)}$, $E^{\ominus}=+0.15\ \mathrm{V}$. What is the standard cell potential of a cell made from these two half-cells?",
  r"$+0.62\ \mathrm{V}$",
  [(r"$+0.92\ \mathrm{V}$", r"adds the two electrode potentials instead of subtracting them"),
   (r"$-0.62\ \mathrm{V}$", r"subtracts in the wrong order, with the less positive half-cell as the positive electrode"),
   (r"$+1.39\ \mathrm{V}$", r"doubles $0.77\ \mathrm{V}$ because two electrons are transferred, then subtracts")],
  r"The standard cell potential is $E^{\ominus}_{\text{cell}}=E^{\ominus}_{\text{positive electrode}}-E^{\ominus}_{\text{negative electrode}}$, and it does not depend on the number of electrons or on the coefficients of the equation.",
  r"The $\mathrm{Fe^{3+}/Fe^{2+}}$ half-cell has the more positive potential, so it is the positive electrode: $E^{\ominus}_{\text{cell}}=+0.77-(+0.15)=+0.62\ \mathrm{V}$.",
  0.62)
# 24
Q(["electrode potentials"], "elevee",
  r"The potential of a metal ion/metal half-cell at $25\ ^{\circ}\mathrm{C}$ is $E=E^{\ominus}+\dfrac{0.0592}{n}\log_{10}[\mathrm{M}^{n+}]$. For $\mathrm{Cu^{2+}(aq)+2e^{-}\rightleftharpoons Cu(s)}$, $E^{\ominus}=+0.34\ \mathrm{V}$. What is the electrode potential when $[\mathrm{Cu^{2+}}]=0.010\ \mathrm{mol\ dm^{-3}}$?",
  r"$+0.28\ \mathrm{V}$",
  [(r"$+0.40\ \mathrm{V}$", r"gives the logarithm term the wrong sign"),
   (r"$+0.22\ \mathrm{V}$", r"forgets to divide $0.0592$ by $n=2$"),
   (r"$+0.31\ \mathrm{V}$", r"takes $\log_{10}(0.010)$ as $-1$ instead of $-2$")],
  r"Substitute $n$ and the concentration in the Nernst equation: a more dilute solution of the ion makes the electrode potential less positive.",
  r"$\log_{10}(0.010)=-2$ and $n=2$, so $E=0.34+\dfrac{0.0592}{2}\times(-2)=0.34-0.0592=+0.28\ \mathrm{V}$.",
  0.28)
# 25
Q(["chemical kinetics", "reaction mechanisms"], "moyenne",
  "The initial rate of a reaction between A and B was measured in three experiments.\n\n"
  "| Experiment | $[\\mathrm{A}]/\\mathrm{mol\\ dm^{-3}}$ | $[\\mathrm{B}]/\\mathrm{mol\\ dm^{-3}}$ | Initial rate$/\\mathrm{mol\\ dm^{-3}\\ s^{-1}}$ |\n|---|---|---|---|\n"
  "| 1 | $0.10$ | $0.10$ | $3.0\\times10^{-4}$ |\n| 2 | $0.20$ | $0.10$ | $6.0\\times10^{-4}$ |\n| 3 | $0.10$ | $0.30$ | $2.7\\times10^{-3}$ |\n\n"
  "What is the value of the rate constant $k$, with its unit?",
  r"$0.30\ \mathrm{dm^{6}\ mol^{-2}\ s^{-1}}$",
  [(r"$0.030\ \mathrm{dm^{3}\ mol^{-1}\ s^{-1}}$", r"takes the reaction as first order in B and second order overall"),
   (r"$3.0\ \mathrm{dm^{9}\ mol^{-3}\ s^{-1}}$", r"takes the reaction as second order in A as well as in B"),
   (r"$3.0\times10^{-3}\ \mathrm{s^{-1}}$", r"divides the rate by $[\mathrm{A}]$ only and ignores B")],
  r"Find each order by comparing two experiments in which one concentration changes, write the rate equation, then substitute one set of data to find $k$ and its unit.",
  r"Experiments 1 and 2: $[\mathrm{A}]$ doubles and the rate doubles, so the order in A is $1$. Experiments 1 and 3: $[\mathrm{B}]$ is multiplied by $3$ and the rate by $9$, so the order in B is $2$. Rate $=k[\mathrm{A}][\mathrm{B}]^{2}$, so $k=\dfrac{3.0\times10^{-4}}{0.10\times(0.10)^{2}}=0.30\ \mathrm{dm^{6}\ mol^{-2}\ s^{-1}}$.",
  0.30)
# 26
Q(["chemical kinetics"], "faible",
  r"The decomposition of a compound is first order, with a half-life of $12.0$ minutes. The initial concentration is $0.800\ \mathrm{mol\ dm^{-3}}$. What is the concentration after $48.0$ minutes?",
  r"$0.0500\ \mathrm{mol\ dm^{-3}}$",
  [(r"$0.200\ \mathrm{mol\ dm^{-3}}$", r"divides by $4$, the number of half-lives, instead of halving four times"),
   (r"$0.100\ \mathrm{mol\ dm^{-3}}$", r"counts only three half-lives"),
   (r"$0.0250\ \mathrm{mol\ dm^{-3}}$", r"counts five half-lives")],
  r"For a first-order reaction the half-life is constant, so after $m$ half-lives the concentration is the initial concentration divided by $2^{m}$.",
  r"The number of half-lives is $\dfrac{48.0}{12.0}=4$. The concentration is halved four times: $0.800\to0.400\to0.200\to0.100\to0.0500\ \mathrm{mol\ dm^{-3}}$.",
  0.05)
# 27
Q(["periodicity"], "faible",
  r"Which element of Period 3 has the highest melting point?",
  r"Silicon",
  [(r"Sodium", r"has weak metallic bonding, because each atom gives only one electron to the delocalised sea"),
   (r"Aluminium", r"has the strongest metallic bonding of the period, but less strong than the giant covalent lattice of silicon"),
   (r"Sulphur", r"forms simple $\mathrm{S_{8}}$ molecules held together by weak London forces")],
  r"Melting points across Period 3 rise from the metals to a maximum at the giant covalent element silicon, then fall sharply for the simple molecular non-metals.",
  r"Silicon has a giant covalent lattice in which every atom is bonded to four others, and many strong covalent bonds must be broken to melt it (about $1690\ \mathrm{K}$). The metals sodium and aluminium melt much lower, and phosphorus, sulphur and chlorine are simple molecules with weak forces between them.",
  "Si")
# 28
Q(["Group IV elements"], "faible",
  r"Which Group IV tetrachloride is NOT hydrolysed by water at room temperature?",
  r"$\mathrm{CCl_{4}}$",
  [(r"$\mathrm{SiCl_{4}}$", r"is hydrolysed, because silicon has vacant $\mathrm{3d}$ orbitals that accept a lone pair from water"),
   (r"$\mathrm{GeCl_{4}}$", r"is hydrolysed, because germanium has vacant $\mathrm{4d}$ orbitals"),
   (r"$\mathrm{SnCl_{4}}$", r"is hydrolysed, because tin has vacant $\mathrm{5d}$ orbitals")],
  r"The tetrachlorides of silicon, germanium and tin are hydrolysed by water because their central atoms have vacant d orbitals that can accept a lone pair from water; carbon has no d orbitals in its second shell.",
  r"Carbon is in the second period and has no vacant orbital of low energy, so a water molecule cannot attack the carbon atom of $\mathrm{CCl_{4}}$ and no reaction occurs. The other three tetrachlorides react, for example $\mathrm{SiCl_{4}+2H_{2}O\rightarrow SiO_{2}+4HCl}$.",
  "CCl4")
# 29
Q(["isomerism"], "moyenne",
  r"How many structural isomers have the molecular formula $\mathrm{C_{4}H_{9}Br}$?",
  r"$4$",
  [(r"$2$", r"considers only the straight carbon chain, with the bromine on carbon $1$ or $2$"),
   (r"$3$", r"forgets the tertiary isomer 2-bromo-2-methylpropane"),
   (r"$5$", r"counts the two optical isomers of 2-bromobutane as two structural isomers")],
  r"Structural isomers differ in the order in which the atoms are joined; list the carbon skeletons first, then the distinct positions of the substituent on each skeleton.",
  r"The skeleton of butane gives 1-bromobutane and 2-bromobutane. The skeleton of 2-methylpropane gives 1-bromo-2-methylpropane and 2-bromo-2-methylpropane. There are $4$ structural isomers; the two enantiomers of 2-bromobutane are stereoisomers, not structural isomers.",
  4)
# 30
Q(["mass spectrometry"], "moyenne",
  r"Chlorine has two isotopes, $^{35}\mathrm{Cl}$ and $^{37}\mathrm{Cl}$, in the abundance ratio $3:1$. In the mass spectrum of chlorine gas, $\mathrm{Cl_{2}}$, the molecular ion peaks are at $m/z=70$, $72$ and $74$. What are the relative heights of these three peaks?",
  r"$9:6:1$",
  [(r"$1:2:1$", r"assumes equal abundances of the two isotopes, as for bromine"),
   (r"$9:3:1$", r"forgets that the ion $^{35}\mathrm{Cl}^{37}\mathrm{Cl}$ can form in two ways"),
   (r"$1:6:9$", r"reverses the abundances and takes $^{37}\mathrm{Cl}$ as the more abundant isotope")],
  r"The probability of each combination of isotopes in a molecule is the product of the isotope abundances, and an unsymmetrical combination counts twice because either atom can carry the heavier isotope.",
  r"With abundances $\tfrac34$ and $\tfrac14$: $m/z=70$ ($^{35}\mathrm{Cl}_{2}$) $=\tfrac{9}{16}$; $m/z=72$ ($^{35}\mathrm{Cl}^{37}\mathrm{Cl}$) $=2\times\tfrac34\times\tfrac14=\tfrac{6}{16}$; $m/z=74$ ($^{37}\mathrm{Cl}_{2}$) $=\tfrac{1}{16}$. The heights are in the ratio $9:6:1$.",
  (9, 6, 1))
# 31
Q(["transition elements", "oxidation states"], "moyenne",
  r"What are the oxidation state of cobalt and its co-ordination number in the complex ion $[\mathrm{Co(NH_{3})_{5}Cl}]^{2+}$?",
  r"Oxidation state $+3$, co-ordination number $6$",
  [(r"Oxidation state $+2$, co-ordination number $6$", r"takes the charge of the complex ion as the oxidation state and forgets the chloride ligand"),
   (r"Oxidation state $+3$, co-ordination number $5$", r"counts only the five ammonia ligands"),
   (r"Oxidation state $+2$, co-ordination number $5$", r"makes both errors")],
  r"The oxidation state of the metal is the charge of the complex ion minus the sum of the charges of the ligands, and the co-ordination number is the number of coordinate bonds to the metal ion.",
  r"The ammonia molecules are neutral and the chloride ligand is $-1$, so $x+5(0)+(-1)=+2$ and $x=+3$. There are $5$ ammonia ligands and $1$ chloride ligand, each donating one lone pair, so the co-ordination number is $6$.",
  (3, 6))
# 32
Q(["qualitative analysis"], "faible",
  r"Aqueous sodium hydroxide is added dropwise to a colourless solution of a metal salt. A white precipitate forms that dissolves in excess alkali. Aqueous ammonia gives a white precipitate that does not dissolve in excess ammonia. Which cation is present?",
  r"$\mathrm{Al^{3+}}$",
  [(r"$\mathrm{Zn^{2+}}$", r"gives a white precipitate that also dissolves in excess ammonia, because it forms a soluble ammine complex"),
   (r"$\mathrm{Mg^{2+}}$", r"gives a white precipitate that does not dissolve in excess sodium hydroxide"),
   (r"$\mathrm{Ca^{2+}}$", r"gives no precipitate with aqueous ammonia")],
  r"Aluminium hydroxide is amphoteric, so it dissolves in excess sodium hydroxide, but it forms no ammine complex, so it stays undissolved in excess ammonia.",
  r"The precipitate that dissolves in excess alkali shows an amphoteric hydroxide: $\mathrm{Al^{3+}}$ or $\mathrm{Zn^{2+}}$. Zinc hydroxide dissolves in excess ammonia as well, but aluminium hydroxide does not. $\mathrm{Mg^{2+}}$ gives a precipitate that stays in excess alkali, and $\mathrm{Ca^{2+}}$ gives no precipitate with ammonia.",
  "Al3+")
# 33
Q(["liquid mixtures"], "moyenne",
  r"Liquids A and B form an ideal mixture. At a given temperature the vapour pressures of pure A and pure B are $60\ \mathrm{kPa}$ and $20\ \mathrm{kPa}$. What is the total vapour pressure above a mixture of $0.40\ \mathrm{mol}$ of A and $0.60\ \mathrm{mol}$ of B?",
  r"$36\ \mathrm{kPa}$",
  [(r"$40\ \mathrm{kPa}$", r"takes the mean of the two vapour pressures of the pure liquids"),
   (r"$24\ \mathrm{kPa}$", r"gives the partial pressure of A only"),
   (r"$44\ \mathrm{kPa}$", r"swaps the two mole fractions")],
  r"By Raoult's law the partial pressure of each component is its mole fraction multiplied by the vapour pressure of the pure liquid, and the total vapour pressure is the sum of the partial pressures.",
  r"$x_{\mathrm{A}}=0.40$ and $x_{\mathrm{B}}=0.60$. $p_{\mathrm{A}}=0.40\times60=24\ \mathrm{kPa}$ and $p_{\mathrm{B}}=0.60\times20=12\ \mathrm{kPa}$. The total is $24+12=36\ \mathrm{kPa}$.",
  36.0)
# 34
Q(["reaction mechanisms", "alkanes and alkenes"], "faible",
  r"Methane reacts with chlorine in ultraviolet light by a free-radical chain mechanism. Which equation represents a propagation step?",
  r"$\mathrm{CH_{4}+Cl^{\bullet}\rightarrow{}^{\bullet}CH_{3}+HCl}$",
  [(r"$\mathrm{Cl_{2}\rightarrow2Cl^{\bullet}}$", r"is the initiation step, in which radicals are first formed"),
   (r"$\mathrm{{}^{\bullet}CH_{3}+Cl^{\bullet}\rightarrow CH_{3}Cl}$", r"is a termination step, in which two radicals combine"),
   (r"$\mathrm{2Cl^{\bullet}\rightarrow Cl_{2}}$", r"is a termination step, in which two radicals combine")],
  r"In a free-radical chain reaction, initiation makes radicals, propagation uses one radical and makes another so the chain continues, and termination removes two radicals.",
  r"In $\mathrm{CH_{4}+Cl^{\bullet}\rightarrow{}^{\bullet}CH_{3}+HCl}$ one radical is used and one radical is formed, so the chain goes on. The second step of the chain is $\mathrm{{}^{\bullet}CH_{3}+Cl_{2}\rightarrow CH_{3}Cl+Cl^{\bullet}}$.",
  "propagation")
# 35
Q(["halogenoalkanes"], "faible",
  r"Which compound is hydrolysed most rapidly by hot aqueous sodium hydroxide?",
  r"1-iodobutane",
  [(r"1-chlorobutane", r"relies on the polarity of the C-Cl bond, but the rate depends on how easily the carbon-halogen bond breaks"),
   (r"1-bromobutane", r"has a C-Br bond that is stronger than the C-I bond"),
   (r"1-fluorobutane", r"has the most polar bond, but also by far the strongest carbon-halogen bond")],
  r"The rate of hydrolysis of halogenoalkanes depends on the strength of the carbon-halogen bond, which falls in the order C-F, C-Cl, C-Br, C-I, so the iodoalkane reacts fastest.",
  r"The four compounds differ only in the halogen. The C-I bond is the longest and weakest, with a bond enthalpy near $240\ \mathrm{kJ\ mol^{-1}}$, so it breaks most easily and 1-iodobutane is hydrolysed fastest, even though the C-F bond is the most polar.",
  "iodo")

# ===================================================================== 36 a 45 : completion multiple
# 36
QM(["alkanes and alkenes"], "faible", r"Which statements about ethene, $\mathrm{C_{2}H_{4}}$, are correct?",
   [r"The two carbon atoms are joined by one $\sigma$ bond and one $\pi$ bond.", r"All six atoms lie in the same plane.", r"It reacts with bromine by addition."],
   (1, 1, 1),
   r"In an alkene the C=C double bond is one $\sigma$ bond plus one $\pi$ bond, the carbon atoms are $\mathrm{sp^{2}}$ hybridised and planar, and the $\pi$ bond makes addition reactions possible.",
   r"1. Correct: the double bond is one $\sigma$ bond and one $\pi$ bond. 2. Correct: each carbon is trigonal planar and the two planes coincide, so all six atoms are in one plane. 3. Correct: the $\pi$ electrons attack bromine to give 1,2-dibromoethane. All three are correct: A.")
# 37
QM(["halogenoalkanes"], "moyenne", r"Which statements about 2-bromopropane, $\mathrm{CH_{3}CHBrCH_{3}}$, are correct?",
   [r"Warming with aqueous sodium hydroxide gives propan-1-ol as the main product.", r"Warming with ethanolic sodium hydroxide gives propene.", r"It is a secondary halogenoalkane."],
   (0, 1, 1),
   r"Aqueous alkali substitutes the halogen by OH at the same carbon atom, ethanolic alkali removes HBr to form an alkene, and the class of a halogenoalkane is given by the number of carbon atoms attached to the carbon bearing the halogen.",
   r"1. Wrong: substitution keeps OH on the same carbon, so the product is propan-2-ol. 2. Correct: elimination of HBr gives propene. 3. Correct: the carbon bearing bromine is bonded to two other carbon atoms. Statements 2 and 3 only: C.")
# 38
QM(["aldehydes and ketones"], "moyenne", r"Which statements about the reaction of propanone with hydrogen cyanide, with a trace of cyanide ions as catalyst, are correct?",
   [r"The mechanism is nucleophilic addition.", r"The product is 2-hydroxy-2-methylpropanenitrile.", r"The product shows optical isomerism."],
   (1, 1, 0),
   r"The carbonyl carbon is attacked by the cyanide ion, a nucleophile, in an addition reaction; a molecule shows optical isomerism only if it has a carbon atom bonded to four different groups.",
   r"1. Correct: $\mathrm{CN^{-}}$ adds to the $\delta+$ carbon of $\mathrm{C=O}$. 2. Correct: the product is $\mathrm{(CH_{3})_{2}C(OH)CN}$. 3. Wrong: the central carbon carries two identical methyl groups, so there is no chiral centre. Statements 1 and 2 only: B.")
# 39
QM(["arenes"], "moyenne", r"Which statements about benzene are correct?",
   [r"It decolourises bromine water at room temperature.", r"The six carbon-carbon bonds have two different lengths.", r"The enthalpy change of hydrogenation of benzene is less exothermic than three times that of cyclohexene."],
   (0, 0, 1),
   r"The delocalised $\pi$ electron system makes benzene more stable than a ring with three localised double bonds, so its C-C bonds are all equal and it resists addition reactions.",
   r"1. Wrong: benzene does not react with bromine water without a catalyst, so the water stays orange. 2. Wrong: all six bonds are equal in length, between a single and a double bond. 3. Correct: hydrogenating benzene releases less energy than three times the value for cyclohexene because the delocalisation energy has to be overcome. Statement 3 only: D.")
# 40
QM(["chemical equilibrium"], "faible", r"For the equilibrium $\mathrm{2SO_{2}(g)+O_{2}(g)\rightleftharpoons2SO_{3}(g)}$, $\Delta H=-197\ \mathrm{kJ\ mol^{-1}}$. Which statements are correct?",
   [r"Increasing the pressure at constant temperature increases the equilibrium yield of $\mathrm{SO_{3}}$.", r"Lowering the temperature increases the value of $K_{c}$.", r"Adding a catalyst increases the equilibrium yield of $\mathrm{SO_{3}}$."],
   (1, 1, 0),
   r"Le Chatelier's principle: a rise in pressure favours the side with fewer gas molecules, a fall in temperature favours the exothermic direction and changes $K_{c}$, and a catalyst speeds up both directions equally.",
   r"1. Correct: three moles of gas on the left and two on the right, so a higher pressure shifts the equilibrium to the right. 2. Correct: the forward reaction is exothermic, so a lower temperature increases $K_{c}$. 3. Wrong: a catalyst only brings the system to equilibrium faster. Statements 1 and 2 only: B.")
# 41
QM(["transition elements"], "moyenne", r"Which statements about transition elements are correct?",
   [r"Zinc is a transition element because it is in the d-block.", r"A $\mathrm{Cu^{2+}}$ ion has a completely filled $\mathrm{3d}$ sub-shell.", r"The colour of an aqueous transition metal ion is caused by the promotion of a d electron to a higher d level when light is absorbed."],
   (0, 0, 1),
   r"A transition element forms at least one ion with a partly filled d sub-shell, and the colour of its ions comes from the absorption of visible light by d electrons.",
   r"1. Wrong: the $\mathrm{Zn^{2+}}$ ion is $\mathrm{3d^{10}}$, so zinc has no ion with a partly filled d sub-shell. 2. Wrong: $\mathrm{Cu^{2+}}$ is $\mathrm{3d^{9}}$. 3. Correct: the split d orbitals allow a d electron to absorb light and move up. Statement 3 only: D.")
# 42
QM(["isomerism"], "faible", r"Which statements about but-2-ene, $\mathrm{CH_{3}CH{=}CHCH_{3}}$, are correct?",
   [r"It shows optical isomerism.", r"It shows cis-trans isomerism.", r"It is a structural isomer of cyclobutane."],
   (0, 1, 1),
   r"Cis-trans isomerism needs a C=C bond with two different groups on each carbon, optical isomerism needs a carbon bonded to four different groups, and structural isomers have the same molecular formula but different structural formulas.",
   r"1. Wrong: no carbon atom has four different groups. 2. Correct: each carbon of the double bond carries $\mathrm{H}$ and $\mathrm{CH_{3}}$, so there are cis and trans forms. 3. Correct: both are $\mathrm{C_{4}H_{8}}$ with different structures. Statements 2 and 3 only: C.")
# 43
QM(["periodicity"], "faible", r"Which statements are correct for the elements from magnesium to barium on descending Group 2?",
   [r"The atomic radius increases.", r"The first ionisation energy decreases.", r"The carbonates become more stable to heat."],
   (1, 1, 1),
   r"Down a group the outer electrons are in shells that are further from the nucleus, so the radius increases and the ionisation energy falls, while the larger cations polarise the carbonate ion less, so the carbonates resist decomposition better.",
   r"1. Correct: each element has one more electron shell. 2. Correct: the outer electrons are further from the nucleus and better shielded. 3. Correct: the thermal stability of the carbonates rises from $\mathrm{MgCO_{3}}$ to $\mathrm{BaCO_{3}}$. All three are correct: A.")
# 44
QM(["acids bases and salts"], "moyenne", r"A volume of $25.0\ \mathrm{cm^{3}}$ of $0.100\ \mathrm{mol\ dm^{-3}}$ ethanoic acid is compared with $25.0\ \mathrm{cm^{3}}$ of $0.100\ \mathrm{mol\ dm^{-3}}$ hydrochloric acid. Which statements are correct?",
   [r"Ethanoic acid is ionised to a smaller extent.", r"The ethanoic acid solution has the higher pH.", r"Ethanoic acid needs a smaller volume of $0.100\ \mathrm{mol\ dm^{-3}}$ sodium hydroxide for complete neutralisation."],
   (1, 1, 0),
   r"A weak acid is only partly ionised in water, so at equal concentration it gives a lower $[\mathrm{H^{+}}]$ and a higher pH than a strong acid, but equal amounts of two monobasic acids need equal amounts of alkali.",
   r"1. Correct: ethanoic acid is a weak acid. 2. Correct: $[\mathrm{H^{+}}]$ is lower, so the pH is higher. 3. Wrong: both solutions contain $2.50\times10^{-3}\ \mathrm{mol}$ of acid that can react, and the weak acid is ionised further as the alkali removes $\mathrm{H^{+}}$, so the volumes are equal. Statements 1 and 2 only: B.")
# 45
QM(["mass spectrometry"], "faible", r"Which statements about mass spectrometry are correct?",
   [r"Gaseous molecules are deflected by the magnetic field before they are ionised.", r"For ions with the same charge, the heavier ions are deflected more than the lighter ions.", r"The molecular ion peak of a compound that forms singly charged ions gives the relative molecular mass of the compound."],
   (0, 0, 1),
   r"In a mass spectrometer the sample is vaporised, ionised, accelerated, deflected by a magnetic field in proportion to the charge and inversely to the mass, and detected, and the molecular ion peak gives the relative molecular mass.",
   r"1. Wrong: only ions are deflected, so ionisation comes first. 2. Wrong: lighter ions are deflected more. 3. Correct: for a singly charged molecular ion $m/z$ equals the relative molecular mass. Statement 3 only: D.")

# ===================================================================== 46 a 50 : assertion-raison
# 46
QA(["crystal structure", "chemical bonding"], "moyenne",
   r"Magnesium oxide has a higher melting point than sodium chloride.", r"Both magnesium oxide and sodium chloride have giant ionic lattices.",
   True, True, False,
   r"The melting point of an ionic compound depends on the strength of the electrostatic attraction between its ions, which rises with the charges of the ions and falls with their radii.",
   r"The first statement is true: $\mathrm{Mg^{2+}}$ and $\mathrm{O^{2-}}$ carry double charges, so the attraction is much stronger than in $\mathrm{Na^{+}Cl^{-}}$. The second statement is also true, but it does not explain the difference, since both compounds have the same kind of lattice. The answer is B.")
# 47
QA(["chemical kinetics"], "faible",
   r"The rate constant of a reaction increases when the temperature is raised.", r"At a higher temperature a greater proportion of colliding molecules have energy equal to or greater than the activation energy.",
   True, True, True,
   r"The Arrhenius equation links the rate constant to the fraction of molecules whose energy reaches the activation energy, and that fraction increases with the temperature.",
   r"Both statements are true. The larger fraction of molecules with energy at or above the activation energy means more successful collisions each second, which is why $k$ increases, so the second statement explains the first. The answer is A.")
# 48
QA(["reaction mechanisms", "halogenoalkanes"], "moyenne",
   r"Tertiary halogenoalkanes are hydrolysed mainly by an $\mathrm{S_{N}2}$ mechanism.", r"The carbocation formed from a tertiary halogenoalkane is stabilised by the electron-releasing effect of its three alkyl groups.",
   False, True, False,
   r"Tertiary halogenoalkanes react by an $\mathrm{S_{N}1}$ mechanism through a carbocation intermediate, while primary halogenoalkanes react mainly by $\mathrm{S_{N}2}$.",
   r"The first statement is false: the three alkyl groups crowd the carbon atom, which blocks the attack of a nucleophile from the back, so the main route is $\mathrm{S_{N}1}$. The second statement is true. The answer is D.")
# 49
QA(["alcohols and carboxylic acids"], "faible",
   r"A carboxylic acid reacts with an alcohol in the presence of concentrated sulphuric acid to form an ester.", r"The esterification reaction goes to completion.",
   True, False, False,
   r"Esterification is a reversible reaction, so the mixture reaches an equilibrium that contains the ester, water and the unreacted acid and alcohol.",
   r"The first statement is true, for example $\mathrm{CH_{3}COOH+C_{2}H_{5}OH\rightleftharpoons CH_{3}COOC_{2}H_{5}+H_{2}O}$. The second statement is false because the reaction is reversible and stops at equilibrium. The answer is C.")
# 50
QA(["Group IV elements"], "faible",
   r"Carbon dioxide is a gas at room temperature, whereas silicon dioxide is a solid.", r"Carbon dioxide is an acidic oxide.",
   True, True, False,
   r"Carbon dioxide forms small simple molecules with weak forces between them, and silicon dioxide forms a giant covalent lattice; the acidic character of an oxide is a separate property.",
   r"The first statement is true because $\mathrm{CO_{2}}$ is simple molecular and $\mathrm{SiO_{2}}$ is giant covalent. The second statement is also true, since $\mathrm{CO_{2}}$ reacts with alkalis to give carbonates, but it does not explain the difference in state. The answer is B.")

assert len(QS) == 50, len(QS)
assert [q["kind"] for q in QS] == ["ba"] * 35 + ["mc"] * 10 + ["ar"] * 5
