"""Questions de l'epreuve inedite GCE O Level Biology Paper 2 n.1 : cinq questions de 20 points, chacune en trois parties (a)(b)(c).
Section A : 3 questions obligatoires. Section B : 2 questions (le vrai sujet en propose 4 et demande d'en traiter 2 ; la plateforme ne
code pas ce choix, voir scripts/gce/INEDITES_GCE.md : version « answer ALL » limitee aux questions a traiter).

Chaque sous-question : barème exact (`pts`), grille `crit` (somme = pts, un critere = un element observable de la copie), rappel
general (une consigne de methode, jamais la reponse), reponse modele `sol`, piege et conseil facultatifs. Le tracé attendu
(reseau trophique de la question 4) n'est que dans le corrige.
"""


def S(num, text, themes, diff, pts, crit, rappel, sol, piege=None, conseil=None, fig=None, groupe_local=""):
    assert abs(sum(p for _, p in crit) - pts) < 1e-9, (num, text[:40], sum(p for _, p in crit), pts)
    return dict(num=num, text=text, themes=themes, diff=diff, pts=pts, crit=crit, rappel=rappel, sol=sol, piege=piege,
                conseil=conseil, fig=fig, groupe_local=groupe_local)


def E(num, groupe, pts, intro, subs):
    assert abs(sum(s["pts"] for s in subs) - pts) < 1e-9, (num, sum(s["pts"] for s in subs), pts)
    return dict(num=num, groupe=groupe, pts=pts, intro=intro, subs=subs)


TABLE_TESTS = (
    "| Test | Sample X | Sample Y | Sample Z |\n|---|---|---|---|\n"
    "| Benedict's solution, heated | Brick-red precipitate | Remained blue | Remained blue |\n"
    "| Iodine solution | Remained brown | Blue-black colour | Remained brown |\n"
    "| Biuret reagent | Remained blue | Remained blue | Purple colour |\n"
    "| Ethanol emulsion test | Remained clear | Remained clear | Cloudy white emulsion |"
)
TABLE_POTOMETRE = (
    "| Condition | Light | Air | Temperature | Distance moved by the bubble in $5$ minutes (mm) |\n|---|---|---|---|---|\n"
    "| A | Shade | Still | $20\\,^{\\circ}\\text{C}$ | 12 |\n"
    "| B | Bright | Still | $20\\,^{\\circ}\\text{C}$ | 30 |\n"
    "| C | Bright | Moving (fan) | $20\\,^{\\circ}\\text{C}$ | 46 |\n"
    "| D | Bright | Still | $30\\,^{\\circ}\\text{C}$ | 42 |"
)


def section_a():
    A = "SECTION A"
    ex = []

    # ------------------------------------------------------------------ 1 : nutrition, digestion, absorption
    ex.append(E("1", A, 20, "A student tested three food samples, X, Y and Z, with four food tests. The results are shown in the table.\n\n" + TABLE_TESTS, [
        S("a", "Name the nutrient or nutrients present in each sample and state the evidence for each.", ["biochemical food tests"], "faible", 6,
          [("You identify sample X as containing a reducing sugar (brick-red precipitate with Benedict's solution)", 2),
           ("You identify sample Y as containing starch (blue-black colour with iodine)", 2),
           ("You identify sample Z as containing protein (purple with biuret) and a lipid (cloudy emulsion)", 2)],
          "Read each test separately and name the nutrient only from its own positive result, giving the colour that proves it.",
          "| Sample | Nutrient(s) present | Evidence |\n|---|---|---|\n"
          "| X | A reducing sugar (for example glucose) | Benedict's solution gave a brick-red precipitate when heated; all other tests were negative |\n"
          "| Y | Starch | Iodine solution turned blue-black; Benedict's solution and biuret stayed blue |\n"
          "| Z | Protein and lipid (fat or oil) | Biuret reagent turned purple, and the ethanol emulsion test gave a cloudy white emulsion |",
          piege="Do not give a nutrient for a negative test: sample Z remained blue with Benedict's solution, so it contains no reducing sugar.",
          groupe_local="(a) Food tests"),
        S("b", "Describe how the ileum (small intestine) is adapted for the absorption of digested food.", ["absorption in the ileum"], "faible", 7,
          [("The ileum is long and its wall is folded into villi, with microvilli on the cells, which give a very large surface area", 2),
           ("The epithelium of a villus is only one cell thick, so the diffusion distance is short", 1),
           ("A dense network of blood capillaries carries the absorbed glucose and amino acids away, which keeps a steep concentration gradient", 2),
           ("A lacteal in each villus absorbs fatty acids and glycerol into the lymph", 1),
           ("Muscles in the villi and peristalsis keep the food mixed and moving", 1)],
          "When asked to describe an adaptation, give the feature and then the way it helps the function; one feature with its effect earns one mark.",
          "1. The ileum is **long**, and its inner wall is folded into thousands of finger-like **villi**; the cells of the villi carry **microvilli**. This gives a very **large surface area** for absorption.\n"
          "2. The wall of each villus is **one cell thick** (a single layer of epithelium), so digested food has only a **short distance** to diffuse.\n"
          "3. Each villus has a dense network of **blood capillaries**. The blood carries away the absorbed glucose and amino acids, so a **steep concentration gradient** is maintained.\n"
          "4. Each villus contains a **lacteal**, a lymph vessel that absorbs **fatty acids and glycerol**.\n"
          "5. **Muscle fibres** in the villi make them move, and **peristalsis** in the wall of the ileum mixes the food with the digestive juices and brings fresh food to the absorbing surface.",
          conseil="Name the feature and its effect in the same sentence: 'thin wall, so a short diffusion distance'.",
          groupe_local="(b) Absorption"),
        S("c", "Describe an experiment to show that saliva contains an enzyme that digests starch.", ["enzyme action"], "moyenne", 7,
          [("You mix starch solution with saliva in one test tube and keep it at about $37\\,^{\\circ}\\text{C}$ in a water bath", 2),
           ("You set up a control with boiled saliva (or water) in place of fresh saliva", 1),
           ("You test samples from each tube with iodine solution at regular intervals", 2),
           ("You state the result: iodine stays brown in the fresh saliva tube and turns blue-black in the control", 1),
           ("You conclude that an enzyme in saliva, amylase, has digested the starch", 1)],
          "To describe an experiment, state the materials, the set-up with its control, what you measure or observe, the result, and the conclusion.",
          "**Materials:** starch solution, fresh saliva (collected in a clean beaker), boiled and cooled saliva, two test tubes, a water bath at about $37\\,^{\\circ}\\text{C}$, a white tile, iodine solution, droppers and a stop-watch.\n\n"
          "**Method:** Put $5$ cm$^{3}$ of starch solution in each of two test tubes. Add $1$ cm$^{3}$ of fresh saliva to tube 1 and $1$ cm$^{3}$ of boiled saliva to tube 2 (the **control**). Place both tubes in the water bath at $37\\,^{\\circ}\\text{C}$. Every minute, take a drop from each tube with a dropper and add it to a drop of iodine solution on the white tile.\n\n"
          "**Results:** with fresh saliva the iodine solution gradually stays **brown** (no starch left) after a few minutes. In the control the drop stays **blue-black** throughout, because boiling destroyed the enzyme.\n\n"
          "**Conclusion:** saliva contains an enzyme, **salivary amylase**, which digests starch to maltose.",
          piege="Without the boiled-saliva control you cannot show that it is the enzyme, and not the water or the temperature, that digested the starch.",
          groupe_local="(c) Enzyme experiment"),
    ]))

    # ------------------------------------------------------------------ 2 : transpiration, transport, photosynthesis
    ex.append(E("2", A, 20, "A student used a potometer to measure the rate at which a leafy shoot takes up water. The experiment was repeated under four different conditions, A to D, and the results are shown in the table.\n\n" + TABLE_POTOMETRE, [
        S("a", "Calculate the rate of water uptake, in mm of bubble movement per minute, for conditions A and C. Then explain the difference in the rate between (i) conditions B and C and (ii) conditions B and D.", ["transpiration"], "moyenne", 6,
          [("You calculate $\\dfrac{12}{5}=2.4$ mm per minute for A and $\\dfrac{46}{5}=9.2$ mm per minute for C", 2),
           ("You explain that moving air removes the water vapour around the leaf, so the diffusion gradient is steeper and transpiration is faster in C", 2),
           ("You explain that the higher temperature makes water evaporate faster, so transpiration and uptake are faster in D", 2)],
          "Divide the distance by the time to get a rate, and explain a difference by naming the factor that changes and how it acts on transpiration.",
          "**Rates:** condition A: $\\dfrac{12}{5}=2.4$ mm per minute. Condition C: $\\dfrac{46}{5}=9.2$ mm per minute.\n\n"
          "**(i) B and C:** the only change is the moving air. The fan blows away the humid air next to the leaf, so the concentration of water vapour outside stays low and the **diffusion gradient** from the leaf to the air is steeper. Transpiration, and therefore uptake of water, is faster in C.\n\n"
          "**(ii) B and D:** the only change is the temperature. At $30\\,^{\\circ}\\text{C}$ the water in the leaf **evaporates faster** and water vapour diffuses out more quickly, so more water is pulled up the stem and the bubble moves further in D.",
          piege="Explain a change in the rate from the one factor that differs between the two conditions, not from all the conditions together.",
          groupe_local="(a) Potometer results"),
        S("b", "Describe the path taken by a molecule of water from the soil to the atmosphere through a plant.", ["transport in plants"], "faible", 7,
          [("Water enters a root hair cell from the soil by osmosis", 1),
           ("It crosses the cortex cell by cell, and enters the xylem vessels of the root", 2),
           ("It moves up the xylem of the stem to the leaf, pulled by transpiration, in a continuous column of water", 2),
           ("It passes from the xylem to the mesophyll cells and evaporates into the air spaces", 1),
           ("Water vapour diffuses out through the stomata", 1)],
          "For a pathway, list the structures in the order the water meets them, and say how the water moves at each stage.",
          "1. Water enters a **root hair cell** from the soil by **osmosis**, because the cell sap has a lower water potential than the soil water.\n"
          "2. It moves across the **cortex** from cell to cell by osmosis, and also along the cell walls, until it reaches the **endodermis** and enters the **xylem vessels** in the centre of the root.\n"
          "3. It rises in the **xylem** of the stem as a continuous column, pulled upwards by the loss of water from the leaves (**transpiration pull**) and helped by the attraction between water molecules.\n"
          "4. In the leaf it leaves the xylem and enters the **mesophyll cells**, where it **evaporates** from the wet cell walls into the air spaces.\n"
          "5. The water vapour **diffuses** through the **stomata** into the atmosphere.",
          groupe_local="(b) Path of water"),
        S("c", "Describe an experiment to show that carbon dioxide is necessary for photosynthesis.", ["photosynthesis process"], "moyenne", 7,
          [("You destarch two potted plants by keeping them in the dark for $24$ to $48$ hours", 1),
           ("You enclose one plant with a dish of potassium hydroxide (absorbs carbon dioxide) and the other with a dish of water, as a control", 2),
           ("You leave both plants in bright light for several hours", 1),
           ("You test a leaf from each plant for starch: boil in water, then in hot ethanol, then add iodine solution", 2),
           ("You state that the control leaf turns blue-black but the leaf without carbon dioxide stays brown, so carbon dioxide is needed", 1)],
          "A fair experiment changes one factor only: write the test, the control, the variable that is the same, the result and the conclusion.",
          "**Principle:** a plant cannot make starch without carbon dioxide. Starch in a leaf is used as the sign that photosynthesis took place.\n\n"
          "**Method:** (1) **Destarch** two similar potted plants by leaving them in a dark cupboard for $24$ to $48$ hours. (2) Cover each plant, and its pot, with a clear polythene bag sealed round the stem. Put a dish of **potassium hydroxide** solution, which absorbs carbon dioxide, inside the bag of plant 1. Put a dish of **water** inside the bag of plant 2 (the **control**). (3) Place both plants in **bright light** for several hours. (4) Pick a leaf from each plant, boil it in water to kill it, boil it in **ethanol** in a water bath to remove the chlorophyll, rinse it, and add **iodine solution**.\n\n"
          "**Results:** the leaf from plant 2 (control) turns **blue-black**, so starch is present. The leaf from plant 1 stays **brown**, so no starch was made.\n\n"
          "**Conclusion:** photosynthesis needs carbon dioxide.",
          piege="Ethanol is flammable: it is heated in a water bath, never over a flame.",
          groupe_local="(c) Photosynthesis experiment"),
    ]))

    # ------------------------------------------------------------------ 3 : genetique et variation
    ex.append(E("3", A, 20, "", [
        S("a", "Define each of the following terms: (i) allele, (ii) genotype, (iii) phenotype.", ["genetics terminology"], "faible", 6,
          [("You define an allele as one of the alternative forms of a gene", 2), ("You define the genotype as the genetic make-up of an organism, the alleles it carries", 2),
           ("You define the phenotype as the observable characteristics of an organism, resulting from its genotype and the environment", 2)],
          "A definition states what the term is in one precise sentence, using the key word of the term's meaning.",
          "(i) An **allele** is one of the alternative forms of a gene, found at the same position (locus) on a pair of homologous chromosomes, for example the alleles for tall and dwarf stems.\n\n"
          "(ii) The **genotype** is the genetic make-up of an organism: the combination of alleles that it carries for a characteristic, for example $Tt$.\n\n"
          "(iii) The **phenotype** is the observable characteristic of an organism, produced by its genotype together with the effect of the environment, for example a tall plant.",
          groupe_local="(a) Terms"),
        S("b", "In maize, purple kernels $(P)$ are dominant to yellow kernels $(p)$. A homozygous purple plant is crossed with a plant that has yellow kernels. Two of the offspring (the $F_{1}$) are then crossed together. (i) State the genotype and the phenotype of the $F_{1}$. (ii) Show, with a genetic diagram, the cross between two $F_{1}$ plants. (iii) State the ratio of the phenotypes of the $F_{2}$ and the number of yellow kernels expected among $480$ kernels.",
          ["monohybrid inheritance"], "moyenne", 8,
          [("You state that the $F_{1}$ are $Pp$ and all purple", 2), ("You write the gametes of each $F_{1}$ parent: $P$ or $p$", 2), ("You complete the Punnett square: $PP$, $Pp$, $Pp$, $pp$", 2),
           ("You state the ratio $3$ purple : $1$ yellow and $120$ yellow kernels out of $480$", 2)],
          "In a genetic cross write the parents, their gametes, a Punnett square for the offspring, then state the genotypes, the phenotypes and the ratio.",
          "**(i)** $PP\\times pp$: all the $F_{1}$ plants receive $P$ from one parent and $p$ from the other. Their genotype is **$Pp$** and, since $P$ is dominant, all are **purple**.\n\n"
          "**(ii)** Cross $Pp\\times Pp$. Gametes of each parent: $P$ and $p$.\n\n"
          "| | $P$ | $p$ |\n|---|---|---|\n| $P$ | $PP$ | $Pp$ |\n| $p$ | $Pp$ | $pp$ |\n\n"
          "**(iii)** Genotypes: $1\\,PP:2\\,Pp:1\\,pp$. Phenotypes: **$3$ purple : $1$ yellow**. The fraction of yellow kernels is $\\dfrac{1}{4}$, so among $480$ kernels about $\\dfrac{1}{4}\\times480=120$ are yellow.",
          piege="A heterozygous plant is purple: only the homozygous recessive genotype $pp$ gives yellow kernels.",
          groupe_local="(b) Genetic cross"),
        S("c", "Differentiate between continuous variation and discontinuous variation, giving one example of each.", ["meiosis and variation"], "faible", 6,
          [("You state that continuous variation shows a range of values between two extremes with no clear groups, and give an example such as height or mass", 3),
           ("You state that discontinuous variation shows distinct groups with no intermediate values, and give an example such as blood groups or tongue rolling", 3)],
          "To differentiate, write a comparison point by point, pairing each feature of one term with the same feature of the other.",
          "| Continuous variation | Discontinuous variation |\n|---|---|\n"
          "| Individuals show a **whole range of values** between two extremes | Individuals fall into **clear, separate groups** |\n"
          "| There are **intermediate forms** | There are **no intermediate forms** |\n"
          "| Controlled by **many genes** and strongly affected by the environment | Controlled by **one or a few genes**, little affected by the environment |\n"
          "| Example: **height** or body mass in humans | Example: **blood groups** (A, B, AB, O) |",
          conseil="Always give the example the question asks for: it is usually worth a mark.",
          groupe_local="(c) Variation"),
    ]))
    return ex


def section_b():
    B = "SECTION B"
    ex = []

    # ------------------------------------------------------------------ 4 : ecologie
    ex.append(E("4", B, 20, "A pond contains the following organisms: algae, water lilies, tadpoles, snails, dragonfly larvae, small fish and a heron. The tadpoles feed on algae and the snails feed on water lilies. The dragonfly larvae feed on tadpoles. The small fish feed on dragonfly larvae and on snails. The heron feeds on small fish.", [
        S("a", "(i) Draw a food web for the organisms of this pond. (ii) Name the producers, the primary consumers and the top carnivore.", ["food chains and food webs"], "faible", 7,
          [("You draw the food web with all seven organisms, and with the arrows pointing from the organism eaten to the organism that eats it", 3),
           ("You show that the small fish are fed on by the heron and feed on two organisms (dragonfly larvae and snails)", 1),
           ("You name the algae and the water lilies as producers", 1), ("You name the tadpoles and the snails as primary consumers", 1), ("You name the heron as the top carnivore", 1)],
          "In a food web the arrows show the direction of energy flow: each arrow starts at the organism that is eaten and ends at the organism that eats it.",
          "**(i)** Feeding links, each arrow from the organism eaten to its consumer: algae $\\rightarrow$ tadpoles; water lilies $\\rightarrow$ snails; tadpoles $\\rightarrow$ dragonfly larvae; dragonfly larvae $\\rightarrow$ small fish; snails $\\rightarrow$ small fish; small fish $\\rightarrow$ heron. The expected food web is shown in the figure below.\n\n"
          "**(ii)** **Producers:** algae and water lilies (they make food by photosynthesis). **Primary consumers:** tadpoles and snails (they feed on producers). **Top carnivore:** the heron (nothing in the pond eats it).",
          piege="An arrow that points from the heron to the fish shows the wrong direction: the arrow always points towards the feeder.",
          fig="reseau_etang", groupe_local="(a) Food web"),
        S("b", "Describe the effects on the pond when large amounts of fertiliser from nearby farms are washed into it.", ["water pollution"], "moyenne", 6,
          [("The nitrates and phosphates make the algae grow very quickly (an algal bloom)", 1), ("The algae cover the surface and cut off the light, so submerged plants die", 1),
           ("Dead plants and algae are decomposed by bacteria that multiply", 2), ("The bacteria use up the dissolved oxygen, so fish and other animals die", 1),
           ("The number of species falls and the water becomes foul and unfit for use", 1)],
          "To describe the effects of a pollutant, write them in the order in which they happen, linking each to the one before.",
          "1. The fertiliser adds **nitrates and phosphates** to the water, which makes the **algae multiply rapidly** and form a thick green layer on the surface (an **algal bloom**).\n"
          "2. The algae block the **light**, so submerged plants cannot photosynthesise and **die**.\n"
          "3. The dead algae and plants are broken down by **decomposing bacteria**, which multiply very quickly.\n"
          "4. The bacteria use up the **dissolved oxygen** in the water for respiration, so the fish, tadpoles and other animals **suffocate and die**.\n"
          "5. **Biodiversity falls** and the water becomes foul-smelling and unfit to drink: this process is called **eutrophication**.",
          groupe_local="(b) Pollution"),
        S("c", "In a food chain the producers fix $60\\,000$ kJ of energy. (i) Calculate the energy available to the tertiary consumers if only $10\\%$ of the energy passes from one trophic level to the next. (ii) Explain why only about $10\\%$ of the energy is passed on. (iii) Explain why food chains rarely have more than five trophic levels.", ["energy flow in ecosystems"], "moyenne", 7,
          [("You calculate $60\\,000\\times\\dfrac{10}{100}=6\\,000$ kJ for the primary consumers and $600$ kJ for the secondary consumers", 1), ("You obtain $60$ kJ for the tertiary consumers", 1),
           ("You explain that energy is lost as heat in respiration and in movement", 1), ("You explain that some parts of the food are not eaten or are not digested and are lost as faeces", 1),
           ("You state that some of the organism dies without being eaten and goes to the decomposers", 1),
           ("You explain that so much energy is lost at each level that too little energy remains to support further levels", 2)],
          "In an energy calculation write each step, multiplying by the percentage that passes on, and show the unit with the answer.",
          "**(i)** Primary consumers receive $\\dfrac{10}{100}\\times60\\,000=6\\,000$ kJ. Secondary consumers receive $\\dfrac{10}{100}\\times6\\,000=600$ kJ. Tertiary consumers receive $\\dfrac{10}{100}\\times600=\\mathbf{60}$ **kJ**.\n\n"
          "**(ii)** At each level most of the energy is lost: it is released as **heat** in **respiration** and used for **movement and body processes**; some parts of the food, such as bones and cellulose, are **not eaten or not digested** and leave as **faeces**; and some organisms die and pass their energy to **decomposers**.\n\n"
          "**(iii)** Because about $90\\%$ of the energy is lost at each step, after four or five levels the energy left is **too small to support another population** of consumers.",
          piege="$10\\%$ of $60\\,000$ kJ is the energy of the primary consumers, not the tertiary ones: apply the step three times.",
          groupe_local="(c) Energy flow"),
    ]))

    # ------------------------------------------------------------------ 5 : l'oeil
    ex.append(E("5", B, 20, "", [
        S("a", "Draw a large labelled diagram of a vertical section through the human eye.", ["the human eye"], "moyenne", 8,
          [("Your diagram is large, neat and has a title and a clear outline", 2), ("Your diagram shows the cornea, the iris with the pupil, the lens, the vitreous humour and the retina in the correct positions", 3),
           ("Your diagram shows the optic nerve, the sclera and the choroid, and the aqueous humour in front of the lens", 1), ("You use at least five correct label lines that touch the parts", 2)],
          "A biological drawing is large, drawn with a sharp pencil in clear continuous lines, and labelled with ruled lines that touch the part.",
          "**Diagram to draw:** a large **vertical section through the human eye**, with the title 'Vertical section of the human eye', drawn as a nearly round eyeball.\n\n"
          "What to draw, from front to back: at the front, the transparent **cornea** bulging forward. Behind it the **aqueous humour**, a watery space, and the **iris**, a coloured ring with the opening of the **pupil** in the middle. Directly behind the pupil, the **lens**, a biconvex disc held at its edges by the **suspensory ligaments**, which join the **ciliary body (ciliary muscles)**. Behind the lens, the large space filled with **vitreous humour**. The wall of the eyeball has three layers: the tough outer **sclera**, the dark **choroid** and the inner **retina**. At the back, the **optic nerve** leaves the eye, and the **blind spot** is where it leaves the retina.\n\n"
          "Label lines are drawn with a ruler, do not cross each other and touch the part named.",
          piege="The label lines must touch the part itself, and arrows are not needed: a line that ends in the middle of the eyeball is marked wrong.",
          conseil="Draw the outline lightly first, then the lens and the iris, and add the labels last.",
          groupe_local="(a) Diagram"),
        S("b", "Explain how the eye focuses (i) on a near object and (ii) on a distant object.", ["the human eye"], "moyenne", 6,
          [("You state that for a near object the ciliary muscles contract and the suspensory ligaments slacken", 1), ("You state that the lens becomes thicker and bends light rays more strongly, so the image falls on the retina", 2),
           ("You state that for a distant object the ciliary muscles relax and the suspensory ligaments are pulled tight", 1), ("You state that the lens becomes thinner and bends the light less, so the image falls on the retina", 2)],
          "To explain a process in the body, give the order of events, naming the structure that changes and the effect on the image.",
          "**(i) Near object.** The light rays from a near object are strongly diverging. The **ciliary muscles contract**, so the tension on the **suspensory ligaments** is released (they slacken). The elastic lens becomes **thicker and more curved** and **bends the rays more strongly**, so a sharp image falls on the **retina**.\n\n"
          "**(ii) Distant object.** The rays from a distant object are almost parallel. The **ciliary muscles relax**, the **suspensory ligaments are pulled tight** by the pressure of the eyeball, and the lens is **pulled thinner**. It bends the rays less, and a sharp image falls on the retina.\n\n"
          "This adjustment of the lens is called **accommodation**.",
          piege="Do not mix the two: the ciliary muscles contract for near vision, and relax for distant vision.",
          groupe_local="(b) Focusing"),
        S("c", "For each of the defects of vision, short sight and long sight, state what the person cannot see clearly and how the defect is corrected.", ["defects of vision"], "faible", 6,
          [("You state that a person with short sight cannot see distant objects clearly, and the cause: the eyeball is too long or the lens too strong, so the image forms in front of the retina", 2),
           ("You state that short sight is corrected with a concave (diverging) lens", 1),
           ("You state that a person with long sight cannot see near objects clearly, and the cause: the eyeball is too short or the lens too weak, so the image forms behind the retina", 2),
           ("You state that long sight is corrected with a convex (converging) lens", 1)],
          "For each defect give three things: what cannot be seen clearly, why, and which lens corrects it.",
          "| | Short sight (myopia) | Long sight (hypermetropia) |\n|---|---|---|\n"
          "| What cannot be seen clearly | **Distant** objects | **Near** objects |\n"
          "| Cause | The eyeball is **too long**, or the lens is too strong: the image forms **in front of** the retina | The eyeball is **too short**, or the lens is too weak: the image forms **behind** the retina |\n"
          "| Correction | A **concave (diverging)** lens spreads the rays before they enter the eye | A **convex (converging)** lens makes the rays converge before they enter the eye |",
          groupe_local="(c) Defects"),
    ]))
    return ex
