r"""Questions de l'epreuve inedite GCE O Level Human Biology Paper 2 n.1 : cinq questions de 20 points, chacune en trois parties (a)(b)(c).
Section A : 3 questions (le vrai sujet en propose 5 et demande d'en traiter 3). Section B : 2 questions (le vrai sujet en propose 4 et demande d'en
traiter 2). La plateforme ne code pas ce choix, voir scripts/gce/INEDITES_GCE.md : version « answer ALL » limitee aux questions a traiter.

Chaque sous-question : barème exact (`pts`), grille `crit` (somme = pts, un critere = un element observable de la copie), rappel general (une
consigne de methode, jamais la reponse), reponse modele `sol`. Aucune figure : le dessin que le vrai sujet propose (« Draw ... OR Describe ... »)
est garde sous sa forme « OR » et le corrige decrit ce que le dessin doit montrer, partie par partie.

Sujets choisis APRES comparaison avec les 8 vrais Paper 2 (2019-2026) : le nephron, la peau, la pollution de l'air et sa lutte, les termes
« allele » et « codominance », l'incineration et le compostage etaient deja des sujets reels et ont ete ecartes ; l'inedite traite les dents et
la carie, un tableau de nutriments, le croisement ABO, la decharge controlee et le VIH.
"""


def S(num, text, themes, diff, pts, crit, rappel, sol, piege=None, conseil=None, fig=None):
    assert abs(sum(p for _, p in crit) - pts) < 1e-9, (num, text[:40], sum(p for _, p in crit), pts)
    return dict(num=num, text=text, themes=themes, diff=diff, pts=pts, crit=crit, rappel=rappel, sol=sol, piege=piege, conseil=conseil, fig=fig)


def E(num, groupe, pts, intro, subs):
    assert abs(sum(s["pts"] for s in subs) - pts) < 1e-9, (num, sum(s["pts"] for s in subs), pts)
    return dict(num=num, groupe=groupe, pts=pts, intro=intro, subs=subs)


TABLE_NUTRIMENTS = (
    "| Nutrient | One function in the body | Deficiency disease or effect |\n|---|---|---|\n"
    "| Vitamin D | | |\n| Vitamin K | | |\n| Vitamin B$_1$ (thiamine) | | |\n| Iron | | |\n| Iodine | | |\n| Sodium | | |"
)


def section_a():
    G = "SECTION A"
    ex = []

    # ------------------------------------------------------------------ 1 : les dents
    ex.append(E("1", G, 20, "", [
        S("a", "Draw a large and neatly labelled diagram of a longitudinal section through a human molar tooth.\n\n**OR**\n\nDescribe the structure of a human molar tooth.", ["human teeth"], "moyenne", 6,
          [("You show or describe the enamel as the hard, white outer covering of the crown", 1), ("You show or describe the dentine, a bone-like layer under the enamel", 1),
           ("You show or describe the pulp cavity containing blood vessels and nerves", 1), ("You show or describe the cement that fixes the root in the jaw bone", 1),
           ("You distinguish the crown, the neck and the roots", 1), ("You show or describe the gum and the jaw bone around the roots", 1)],
          "Go from the outside to the inside of the tooth: covering, hard layer, central cavity; then say how the tooth is held in the jaw.",
          "A **molar** is a back tooth with a broad crown and two or three roots. It has three parts: the **crown**, above the gum; the **neck**, at the gum line; and the **roots**, fixed in sockets of the jaw bone.\n\n"
          "1. The **enamel** is the hard, white covering of the crown; it is the hardest tissue of the body and has no living cells.\n2. The **dentine** is a yellowish, bone-like layer under the enamel and the cement.\n"
          "3. The **pulp cavity** in the centre contains blood vessels, which bring food and oxygen, and nerve endings, which make the tooth sensitive.\n4. The **cement** is a thin layer that covers the roots and fixes the tooth in the socket by fibres.\n5. The **gum** surrounds the neck of the tooth and the **jaw bone** holds the roots.\n\n"
          "In the **drawing**, the enamel, the dentine, the pulp cavity with its blood vessel and nerve, the cement, the gum and the jaw bone must be drawn large, with each label written horizontally and joined to its part by a ruled line.",
          conseil="Draw the pulp cavity narrowing towards the root tips: it is where the blood vessels and the nerve enter the tooth."),
        S("b", "Explain how dental decay develops, from the first attack on the tooth to toothache.", ["human teeth", "personal hygiene and health"], "moyenne", 8,
          [("You say that food particles, especially sugary foods, stay on and between the teeth", 1), ("You say that bacteria in the plaque feed on the sugar", 1),
           ("You say that the bacteria change the sugar into acids", 1), ("You say that the acid dissolves the calcium salts of the enamel", 1),
           ("You say that a hole (cavity) forms in the enamel", 1), ("You say that the decay then spreads into the soft dentine, which decays faster", 1),
           ("You say that when it reaches the pulp cavity the nerve endings are stimulated and cause toothache", 1), ("You say that bacteria may infect the pulp and the jaw and, if untreated, the tooth is lost", 1)],
          "Describe the decay in the order in which it happens: the food, the bacteria, the acid, the damage to each layer of the tooth.",
          "Dental decay develops in the following stages.\n\n1. **Sugary food** and other food particles stay on and between the teeth after a meal.\n2. **Bacteria** in the sticky layer of plaque on the teeth feed on the sugar.\n3. They change the sugar into **acids**.\n"
          "4. The acids **dissolve the calcium salts of the enamel**, and a small hole, or cavity, forms.\n5. The decay spreads to the **dentine**, which is softer than the enamel, so it decays faster.\n"
          "6. When the hole reaches the **pulp cavity** the nerve endings are stimulated, which causes **toothache**.\n7. The bacteria can then infect the pulp and the jaw (an abscess) and, if the tooth is not treated, it is lost.",
          piege="The bacteria do not drill holes: it is the acid that they make which dissolves the enamel."),
        S("c", "Suggest SIX ways of caring for the teeth.", ["human teeth", "personal hygiene and health", "human health and lifestyle"], "faible", 6,
          [("You suggest brushing the teeth at least twice a day, after meals and before sleeping", 1), ("You suggest using a toothpaste with fluoride", 1), ("You suggest avoiding too many sugary foods and drinks between meals", 1),
           ("You suggest eating food rich in calcium and vitamins, and raw fruits and vegetables", 1), ("You suggest visiting a dentist regularly", 1), ("You suggest not using the teeth to crack hard objects or to open bottles", 1)],
          "One way, one mark: use six different ways and say what to do, not only “hygiene”.",
          "1. **Brush the teeth** at least twice a day, after meals and before sleeping, to remove the plaque.\n2. Use a **toothpaste that contains fluoride**, which makes the enamel harder.\n3. **Avoid too many sugary foods and drinks**, especially between meals.\n"
          "4. Eat a **balanced diet** that contains calcium and vitamins, and chew **raw fruits and vegetables**, which clean the teeth.\n5. **Visit a dentist regularly** so that decay is found and treated early.\n6. **Do not use the teeth to crack hard objects or to open bottles**, which can chip the enamel."),
    ]))

    # ------------------------------------------------------------------ 2 : genetique, groupes sanguins
    ex.append(E("2", G, 20, "", [
        S("a", "Explain the following terms:\n\n(i) genotype\n\n(ii) dominant allele\n\n(iii) recessive allele\n\n(iv) gene.", ["genetics terminology", "dominant and recessive alleles"], "faible", 4,
          [("You explain a genotype as the combination of alleles that an organism has for a characteristic", 1),
           ("You explain a dominant allele as one whose effect shows even when only one copy is present", 1),
           ("You explain a recessive allele as one whose effect is hidden when the dominant allele is present", 1),
           ("You explain a gene as a length of DNA on a chromosome that carries the instructions for one characteristic", 1)],
          "Define each term in one sentence and, when it helps, add a short example.",
          "(i) The **genotype** is the combination of alleles that an organism has for a characteristic, for example $I^{A}i$.\n\n"
          "(ii) A **dominant allele** is an allele whose effect shows even when only one copy is present, for example $I^{A}$ over $i$.\n\n"
          "(iii) A **recessive allele** is an allele whose effect is hidden when the dominant allele is present: it shows only when two copies are present, for example $i$ in blood group O.\n\n"
          "(iv) A **gene** is a length of DNA on a chromosome that carries the instructions for making one characteristic of the body, such as the blood group."),
        S("b", "In humans the ABO blood groups are controlled by three alleles. The alleles $I^{A}$ and $I^{B}$ are codominant, and both are dominant to the allele $i$. A woman of blood group A, who is heterozygous, marries a man of blood group B, who is heterozygous.\n\n(i) State the genotypes of the woman and of the man.\n\n(ii) Use a genetic cross to show the possible genotypes and phenotypes of their children.\n\n(iii) State the probability that their first child will have blood group O.",
          ["blood group inheritance", "genetics crosses"], "moyenne", 10,
          [("(i) You give the genotype of the woman as $I^{A}i$", 1), ("(i) You give the genotype of the man as $I^{B}i$", 1),
           ("(ii) You give the gametes of the woman, $I^{A}$ and $i$", 1), ("(ii) You give the gametes of the man, $I^{B}$ and $i$", 1),
           ("(ii) You combine the gametes correctly to give $I^{A}I^{B}$, $I^{A}i$, $I^{B}i$ and $ii$", 2), ("(ii) You give the phenotypes AB, A, B and O", 2),
           ("(iii) You state that one of the four equally likely genotypes is $ii$", 1), ("(iii) You give the probability $\\dfrac{1}{4}$ (or $25\\%$)", 1)],
          "Write the gametes first, then fill a Punnett square, then read the phenotype of every genotype from the dominance relations.",
          "(i) A woman of group A who is heterozygous has the genotype **$I^{A}i$**. A man of group B who is heterozygous has the genotype **$I^{B}i$**.\n\n"
          "(ii) Parents: $I^{A}i\\times I^{B}i$. Gametes of the woman: $I^{A}$ and $i$. Gametes of the man: $I^{B}$ and $i$.\n\n"
          "| | $I^{B}$ | $i$ |\n|---|---|---|\n| **$I^{A}$** | $I^{A}I^{B}$ | $I^{A}i$ |\n| **$i$** | $I^{B}i$ | $ii$ |\n\n"
          "The children may be $I^{A}I^{B}$ (blood group **AB**), $I^{A}i$ (group **A**), $I^{B}i$ (group **B**) or $ii$ (group **O**), in equal numbers.\n\n"
          "(iii) One of the four genotypes is $ii$, so the probability that the first child is of group O is $\\dfrac{1}{4}$, that is **$25\\%$**.",
          piege="The allele $i$ is recessive: group O needs two copies of it, one from each parent, so both parents must be able to give $i$."),
        S("c", "A baby of blood group AB is born to a woman of blood group A. A man of blood group O says that he is the father. Do you agree? Give reasons, and state the two blood groups that the father of the baby could have.",
          ["blood group inheritance", "blood groups"], "elevee", 6,
          [("You do not agree: a man of group O cannot be the father", 1), ("You say that a man of group O has the genotype $ii$ and can give only the allele $i$", 1),
           ("You say that the baby has the allele $I^{B}$, which cannot come from the mother, of group A", 1), ("You say that the baby must therefore have received $I^{B}$ from the father", 1),
           ("You give blood group B as a possible group of the father", 1), ("You give blood group AB as the other possible group of the father", 1)],
          "Write the genotype of the baby and ask which alleles came from the mother and which must have come from the father.",
          "The baby of group AB has the genotype $I^{A}I^{B}$. The woman, of group A, can give $I^{A}$ or $i$ but never $I^{B}$, so the baby must have received **$I^{B}$ from its father**.\n\n"
          "A man of group O has the genotype $ii$ and can give only $i$. He therefore **cannot be the father**: I do not agree with him.\n\n"
          "The father must have the allele $I^{B}$: he is of **blood group B** ($I^{B}I^{B}$ or $I^{B}i$) or of **blood group AB** ($I^{A}I^{B}$)."),
    ]))

    # ------------------------------------------------------------------ 3 : alimentation, vitamines et mineraux
    ex.append(E("3", G, 20, "", [
        S("a", "What is a balanced diet?", ["chemical composition of food", "organic nutrients"], "faible", 2,
          [("You say that it contains all the classes of food: carbohydrates, proteins, fats, vitamins, mineral salts, water and fibre", 1), ("You say that they are in the right quantities and proportions for the needs of the person", 1)],
          "A definition names what the diet contains and says what it must suit.",
          "A **balanced diet** is a diet that contains all the classes of food (carbohydrates, proteins, fats, vitamins, mineral salts, water and fibre) **in the right quantities and proportions** for the age, sex, activity and state of health of the person."),
        S("b", "Copy and complete the table below, giving ONE function and the deficiency disease or effect for each nutrient.\n\n" + TABLE_NUTRIMENTS,
          ["vitamin deficiency diseases", "mineral salts and deficiency diseases", "dietary minerals"], "moyenne", 12,
          [("Vitamin D: it helps the body to absorb calcium and phosphorus for bones and teeth", 1), ("Vitamin D: rickets (soft, bent bones in children)", 1),
           ("Vitamin K: it is needed to make the substances of blood clotting (prothrombin)", 1), ("Vitamin K: prolonged bleeding of wounds", 1),
           ("Vitamin B$_1$: it helps to release energy from carbohydrates and keeps the nerves healthy", 1), ("Vitamin B$_1$: beriberi", 1),
           ("Iron: it is part of haemoglobin, which carries oxygen", 1), ("Iron: anaemia", 1),
           ("Iodine: it is needed to make the hormone thyroxine", 1), ("Iodine: goitre (swelling of the neck)", 1),
           ("Sodium: it is needed for nerve impulses and for the water balance of the body", 1), ("Sodium: muscle cramps and weakness (dehydration)", 1)],
          "For every nutrient give one function that explains the disease: the deficiency disease is the result of the missing function.",
          "| Nutrient | One function in the body | Deficiency disease or effect |\n|---|---|---|\n"
          "| Vitamin D | Helps the absorption of calcium and phosphorus for the bones and teeth | **Rickets**: soft, bent bones in children |\n"
          "| Vitamin K | Needed to make prothrombin and other substances for blood clotting | Prolonged **bleeding** of wounds |\n"
          "| Vitamin B$_1$ (thiamine) | Releases energy from carbohydrates; keeps the nerves healthy | **Beriberi** |\n"
          "| Iron | Part of **haemoglobin**, which carries oxygen in the red blood cells | **Anaemia** |\n"
          "| Iodine | Needed to make the hormone **thyroxine** | **Goitre** (swelling of the neck) |\n"
          "| Sodium (in salt) | Needed for the transmission of nerve impulses and for the water balance of the body | **Muscle cramps** and weakness, and dehydration |",
          piege="Beriberi (vitamin B$_1$) and rickets (vitamin D) are often confused with scurvy (vitamin C): name the vitamin in the row before the disease."),
        S("c", "Explain why a pregnant woman needs a diet that is richer in each of the following:\n\n(i) protein\n\n(ii) iron\n\n(iii) calcium.", ["antenatal and postnatal care", "dietary minerals", "organic nutrients"], "moyenne", 6,
          [("(i) Protein is needed for the growth of the tissues of the foetus and for the placenta and the uterus", 2), ("(ii) Iron is needed to make haemoglobin for the extra blood of the mother and for the blood of the foetus", 2),
           ("(iii) Calcium is needed for the formation of the bones and teeth of the foetus", 2)],
          "For each nutrient say what the foetus or the mother builds with it.",
          "(i) **Protein**: the foetus is growing, and proteins are needed to build its new cells and tissues, and also the placenta and the walls of the uterus.\n\n(ii) **Iron**: the mother's volume of blood increases and the foetus makes its own red blood cells, so iron is needed to make more haemoglobin; a lack of it causes anaemia.\n\n"
          "(iii) **Calcium**: it is needed to build the bones and teeth of the foetus; if the diet is poor the mother's own bones lose calcium."),
    ]))
    return ex


def section_b():
    G = "SECTION B"
    ex = []

    # ------------------------------------------------------------------ 4 : ordures menageres
    ex.append(E("4", G, 20, "", [
        S("a", "What is refuse? Name THREE types of refuse that are produced in a home.", ["refuse disposal methods"], "faible", 4,
          [("You say that refuse is the solid waste (rubbish) that people throw away", 1), ("You name a first type of refuse, for example kitchen waste or food scraps", 1),
           ("You name a second type, for example paper, plastic or glass", 1), ("You name a third type, for example ashes, rags, tins or broken pots", 1)],
          "Define refuse in a sentence, then give three precise examples taken from a home.",
          "**Refuse** is the solid waste, or rubbish, that people throw away. Three types produced in a home: **kitchen waste** (food scraps and peelings), **paper and plastic** (packets, bags and bottles) and **ashes, rags, tins and broken glass or pots**."),
        S("b", "(i) Describe how a sanitary landfill site is prepared and used for the disposal of refuse.\n\n(ii) State TWO advantages and TWO disadvantages of burning refuse in an incinerator.", ["refuse disposal methods", "human impact on environment"], "moyenne", 10,
          [("(i) You say that the site is chosen away from houses, water sources and flooded land", 1), ("(i) You say that a large hole or trench is dug", 1), ("(i) You say that the refuse is tipped in thin layers and compacted", 1),
           ("(i) You say that each layer is covered with soil every day", 1), ("(i) You say that the site is closed with a thick layer of soil when it is full, and later planted with grass or trees", 2),
           ("(ii) You state two advantages, for example it kills the germs, it reduces the bulk of the refuse and it needs little land", 2), ("(ii) You state two disadvantages, for example it pollutes the air with smoke, it is expensive and it wastes the useful materials", 2)],
          "Part (i) follows the life of a landfill in order: choice of the site, preparation, filling, covering, closing. Part (ii) asks for two points on each side, so give four separate points.",
          "**(i) Sanitary landfill.** A site is chosen **away from houses, rivers, wells and flooded land**. A **large hole or trench** is dug. The refuse is **tipped in thin layers and compacted** by a bulldozer, and each day's refuse is **covered with a layer of soil**, which keeps away flies, rats and bad smells. When the site is full it is **closed with a thick layer of soil** and may be planted with grass or trees.\n\n"
          "**(ii) Incineration.** *Advantages*: it kills the germs in the refuse; it greatly reduces the volume of the refuse; it needs little land. *Disadvantages*: the smoke and gases pollute the air; the incinerator is expensive to build and to run; it wastes materials that could be recycled."),
        S("c", "State SIX health problems or hazards that result when refuse is badly disposed of.", ["refuse disposal methods", "pollution and the environment", "human health and lifestyle"], "faible", 6,
          [("You state that flies, rats and cockroaches breed in the refuse", 1), ("You state that they spread diseases such as cholera, typhoid and dysentery", 1), ("You state that refuse blocks the drains and causes floods and stagnant water in which mosquitoes breed", 1),
           ("You state that rotting refuse gives a bad smell", 1), ("You state that burning refuse in the open pollutes the air and causes breathing problems", 1), ("You state that refuse pollutes streams and wells, or that broken glass and tins cause injuries", 1)],
          "Give six different hazards and, where you can, name the disease or the harm that results.",
          "1. **Flies, rats and cockroaches breed** in heaps of refuse.\n2. They **spread diseases** such as cholera, typhoid fever and dysentery.\n3. Refuse **blocks drains and gutters**, causing floods and pools of stagnant water in which **mosquitoes breed**.\n4. Rotting refuse produces **bad smells**.\n"
          "5. **Burning refuse in the open** pollutes the air and causes breathing problems.\n6. Refuse **pollutes streams and wells**, and **broken glass, tins and needles cause injuries**."),
    ]))

    # ------------------------------------------------------------------ 5 : VIH / SIDA
    ex.append(E("5", G, 20, "", [
        S("a", "State what the following abbreviations stand for:\n\n(i) HIV\n\n(ii) AIDS.", ["sexually transmitted infections", "disease terminology"], "faible", 4,
          [("You write that HIV is the Human Immunodeficiency Virus", 2), ("You write that AIDS is the Acquired Immune Deficiency Syndrome", 2)],
          "Write each abbreviation in full, with every word.",
          "(i) **HIV**: **H**uman **I**mmunodeficiency **V**irus.\n\n(ii) **AIDS**: **A**cquired **I**mmune **D**eficiency **S**yndrome."),
        S("b", "(i) Describe how HIV is transmitted from one person to another.\n\n(ii) Explain how infection with HIV leads to AIDS.", ["sexually transmitted infections", "human infectious diseases"], "moyenne", 8,
          [("(i) You state transmission by unprotected sexual intercourse with an infected person", 1), ("(i) You state transmission by transfusion of infected blood or by organ transplant", 1),
           ("(i) You state transmission by sharing needles, razor blades or other skin-piercing instruments", 1), ("(i) You state transmission from an infected mother to her child during pregnancy, birth or breastfeeding", 1),
           ("(ii) You state that the virus infects and destroys the white blood cells (helper lymphocytes) of the body", 1), ("(ii) You state that the body then makes fewer antibodies and its immune system fails", 1),
           ("(ii) You state that the person can no longer fight infections", 1), ("(ii) You state that infections such as tuberculosis and pneumonia (opportunistic diseases) then attack the body and may cause death", 1)],
          "Part (i) lists the ways in which body fluids pass from one person to another; part (ii) follows the virus from the first infection to the disease.",
          "**(i) Transmission.** HIV passes from one person to another through body fluids: (1) **unprotected sexual intercourse** with an infected person; (2) **transfusion of infected blood** or an organ transplant; (3) **sharing needles, razor blades and other skin-piercing instruments**; (4) **from an infected mother to her child** during pregnancy, at birth or through breast milk.\n\n"
          "**(ii) From HIV to AIDS.** The virus enters the white blood cells (the helper lymphocytes) and destroys them. As their number falls, the body makes fewer antibodies and its **immune system fails**, so the person can no longer fight infections. Ordinary infections that a healthy person resists, such as tuberculosis and pneumonia, then attack the body (**opportunistic diseases**), and the person may die of them. This final stage is called AIDS.",
          piege="HIV is the virus and AIDS is the disease: a person can carry HIV for years before developing AIDS."),
        S("c", "Suggest FOUR measures that can prevent the spread of HIV, and explain how each measure works.", ["sexually transmitted infections", "social vices and health", "health care services"], "faible", 8,
          [("You suggest abstaining from sex before marriage, or being faithful to one uninfected partner, and explain that the virus cannot then pass between partners", 2),
           ("You suggest using a condom correctly and explain that it stops body fluids from passing from one partner to the other", 2),
           ("You suggest testing donated blood and sterilising or using new needles and instruments, and explain that this stops the virus from entering the blood", 2),
           ("You suggest testing and treating pregnant women, or avoiding breastfeeding by an infected mother, and explain that this protects the baby", 2)],
          "Name the measure first, then say in one sentence what stops the virus: a measure without its explanation earns one mark only.",
          "1. **Abstinence or faithfulness to one uninfected partner**: if neither partner carries the virus there is nothing to pass on.\n2. **Using a condom correctly**: it acts as a barrier, so semen and vaginal fluids do not pass from one partner to the other.\n"
          "3. **Testing all donated blood and using sterile needles and instruments**: the virus cannot enter the blood of a patient from infected blood or from a used needle.\n4. **Testing and treating pregnant women** (and advising on feeding): the drugs lower the amount of virus in the blood, so fewer babies are infected before and at birth."),
    ]))
    return ex
