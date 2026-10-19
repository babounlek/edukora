"""Questions de l'epreuve inedite GCE O Level Biology Paper 1 n.1 (50 QCM). Voir generer_biology_p1.py.

Q(id, themes, difficulte, enonce, bonne option, 3 distracteurs, rappel, resolution, piege, conseil, figure).
`{FIG}` dans un enonce est remplace par « Figure N » (numerotation continue dans l'ordre final des questions).
Themes : noms de Tag EXISTANTS pour le GCE O Level Biology (forme la plus frequente de chaque notion).
Les questions a donnees chiffrees ou a figure sont recalculees par verifier_reponses_biology_p1.py.
"""


def Q(qid, themes, diff, stem, ok, bad, rappel, sol, piege=None, conseil=None, fig=None):
    return dict(id=qid, themes=themes, diff=diff, stem=stem, ok=ok, bad=bad, rappel=rappel, sol=sol, piege=piege,
                conseil=conseil, fig=fig)


TABLE_POMMES = (
    "| Solution | P (distilled water) | Q ($0.2$ M) | R ($0.4$ M) | S ($0.8$ M) |\n|---|---|---|---|---|\n"
    "| Final mass of strip (g) | 11.4 | 10.5 | 10.0 | 8.7 |"
)
TABLE_TESTS = (
    "| Test | Observation |\n|---|---|\n| Benedict's solution, heated | Remained blue |\n"
    "| Iodine solution | Blue-black colour |\n| Biuret reagent | Remained blue |"
)
TABLE_AIR = (
    "| Gas | Inhaled air (%) | Exhaled air (%) |\n|---|---|---|\n| Oxygen | 21 | 16 |\n"
    "| Carbon dioxide | 0.04 | 4.00 |\n| Nitrogen | 78 | 78 |"
)


def questions():
    q = []
    a = q.append

    a(Q("b01", ["plant cell structure"], "faible",
        "Which structure is found in plant cells but not in animal cells?",
        "Cell wall.", ["Nucleus.", "Cell membrane.", "Cytoplasm."],
        "A plant cell differs from an animal cell by its cellulose cell wall, its chloroplasts and its large permanent vacuole.",
        "The cell wall is made of cellulose and surrounds the cell membrane of plant cells only. Nucleus, cell membrane and cytoplasm are present in both kinds of cell."))

    a(Q("b02", ["cell structure"], "moyenne",
        "Which cell organelle is the main site of aerobic respiration?",
        "Mitochondrion.", ["Ribosome.", "Golgi body.", "Chloroplast."],
        "Match each organelle to its job: mitochondria release energy, ribosomes make proteins, chloroplasts carry out photosynthesis.",
        "Aerobic respiration releases energy from glucose using oxygen, and most of its steps take place in the mitochondria.",
        piege="The chloroplast is the site of photosynthesis, not of respiration."))

    a(Q("b03", ["practical biology"], "moyenne",
        "A student draws a cell so that it is $45$ mm long. The real cell is $0.03$ mm long. The magnification of the drawing is",
        "$\\times1\\,500$", ["$\\times150$", "$\\times15\\,000$", "$\\times1.5$"],
        "Magnification $=\\dfrac{\\text{size of the drawing}}{\\text{actual size}}$, with both lengths in the same unit.",
        "$\\dfrac{45}{0.03}=1\\,500$, so the drawing is magnified $1\\,500$ times.",
        piege="A magnification has no unit: $45$ divided by $0.03$ already uses millimetres for both sizes."))

    a(Q("b04", ["unicellular organisms"], "faible",
        "Which of the following organisms is unicellular?",
        "Amoeba.", ["Spirogyra.", "Mucor.", "Mosquito."],
        "A unicellular organism is made of one cell that carries out all the life processes.",
        "Amoeba is a single-celled protozoan. Spirogyra is a filamentous alga, Mucor is a fungus with hyphae and a mosquito is an insect."))

    a(Q("b05", ["structure of algae"], "faible",
        "The cells of Spirogyra contain a ribbon-shaped, spiral",
        "Chloroplast.", ["Nucleus.", "Vacuole.", "Mitochondrion."],
        "Spirogyra is a green alga whose cells have chloroplasts of characteristic shape.",
        "Each cell of Spirogyra has a spiral chloroplast that holds the chlorophyll for photosynthesis."))

    a(Q("b06", ["bread mould"], "faible",
        "The fine threads that make up the body of the bread mould Mucor are called",
        "Hyphae.", ["Spores.", "Sporangia.", "Stomata."],
        "The body of a fungus such as Mucor is a network of threads called hyphae, together forming a mycelium.",
        "Hyphae grow over and into the bread and absorb food. Spores and sporangia are reproductive structures, and stomata are pores in leaves."))

    a(Q("b08", ["osmosis in cells"], "moyenne",
        "Four potato strips, each of mass $10.0$ g, were left for one hour in four solutions. Their final masses are shown below.\n\n" + TABLE_POMMES +
        "\n\nWhich solution had the same concentration as the cell sap of the potato?",
        "R.", ["P.", "Q.", "S."],
        "Cells gain mass in a solution more dilute than their sap, lose mass in a more concentrated one, and keep the same mass in a solution of equal concentration.",
        "Only strip R kept its original mass of $10.0$ g, so no net movement of water took place: solution R was as concentrated as the cell sap. P and Q made the strips gain water, and S made the strip lose water.",
        piege="The distilled water P gave the largest change in mass, but a large change shows a big difference in concentration, not equality."))

    a(Q("b09", ["osmosis in cells"], "faible",
        "A red blood cell is placed in distilled water. It will",
        "Swell and burst.", ["Shrink.", "Remain unchanged.", "Become flaccid."],
        "Water enters a cell by osmosis when the surrounding solution is more dilute than the cell contents.",
        "Distilled water is more dilute than the cytoplasm, so water enters the red blood cell. It has no cell wall to resist the swelling, so it bursts.",
        piege="A plant cell does not burst in water because its cell wall resists, but an animal cell has no wall."))

    a(Q("b10", ["biochemical food tests"], "moyenne",
        "A student tested a food sample and recorded the results below.\n\n" + TABLE_TESTS + "\n\nThe sample contains",
        "Starch only.", ["Reducing sugar only.", "Protein only.", "Starch and protein."],
        "Read each test separately: blue-black with iodine means starch, brick-red with heated Benedict's solution means a reducing sugar, and purple with biuret means protein.",
        "The iodine test is positive (starch). Benedict's solution stayed blue, so there is no reducing sugar, and the biuret reagent stayed blue, so there is no protein.",
        piege="Do not mix the tests: a blue colour after Benedict's or biuret is a negative result."))

    a(Q("b11", ["biochemical food tests"], "faible",
        "Sudan III solution is used to test for",
        "Lipids.", ["Starch.", "Proteins.", "Reducing sugars."],
        "Each food test has its reagent: iodine for starch, Benedict's for reducing sugars, biuret for proteins, Sudan III for lipids.",
        "Sudan III dissolves in fats and oils and stains them red, so it shows the presence of lipids."))

    a(Q("b12", ["enzyme action"], "moyenne",
        "{FIG} shows the effect of temperature on the rate of reaction of an enzyme. At $60\\,^{\\circ}\\text{C}$ the enzyme",
        "Is denatured and stops working.", ["Works at its fastest rate.", "Is digested by the substrate.", "Combines with more substrate."],
        "An enzyme works best at its optimum temperature; at high temperatures its shape is destroyed (it is denatured) and it stops working.",
        "The graph shows that the rate is highest at $40\\,^{\\circ}\\text{C}$ and falls to zero near $60\\,^{\\circ}\\text{C}$. At that temperature the structure of the enzyme has changed permanently: it is denatured.",
        fig="enzyme"))

    a(Q("b14", ["digestive secretions"], "faible",
        "The function of bile in digestion is to",
        "Emulsify fats.", ["Digest proteins.", "Digest starch.", "Absorb water."],
        "Bile is made in the liver, stored in the gall bladder, and contains no enzymes.",
        "Bile breaks large fat droplets into tiny droplets (emulsification), which gives lipase a bigger surface to act on."))

    a(Q("b16", ["mineral salts and deficiency diseases"], "faible",
        "A diet that lacks iron may lead to",
        "Anaemia.", ["Rickets.", "Scurvy.", "Goitre."],
        "Learn each deficiency disease with its missing nutrient: iron and anaemia, vitamin C and scurvy, vitamin D and rickets, iodine and goitre.",
        "Iron is needed to make haemoglobin, so a lack of iron reduces the oxygen carried by the blood: anaemia."))

    a(Q("b17", ["photosynthesis process"], "faible",
        "The raw materials for photosynthesis are",
        "Carbon dioxide and water.", ["Oxygen and glucose.", "Carbon dioxide and oxygen.", "Water and glucose."],
        "Photosynthesis uses carbon dioxide and water, with light energy absorbed by chlorophyll, to make glucose and oxygen.",
        "Carbon dioxide enters through the stomata and water comes from the soil. Glucose and oxygen are the products."))

    a(Q("b18", ["photosynthesis process"], "moyenne",
        "{FIG} shows the effect of light intensity on the rate of photosynthesis of a plant. Beyond point P, a greater light intensity does not increase the rate because",
        "Another factor, such as carbon dioxide concentration, is limiting.", ["The chlorophyll has been destroyed.", "Light is no longer needed.", "The leaf has stopped respiring."],
        "A limiting factor is the factor in shortest supply: when it is the limit, increasing another factor gives no further increase in the rate.",
        "Up to P the rate rises with light, so light is limiting. After P the curve is flat: light is no longer the limit and another factor, for example the carbon dioxide concentration or the temperature, now limits the rate.",
        fig="lumiere"))

    a(Q("b19", ["photosynthesis process"], "faible",
        "Chlorophyll absorbs mainly which two colours of light?",
        "Red and blue.", ["Green and yellow.", "Green and red.", "Yellow and blue."],
        "Photosynthesis uses light energy absorbed by chlorophyll, which absorbs mainly red and blue light and reflects green light.",
        "A leaf looks green because chlorophyll reflects the green light and absorbs most of the red and the blue light, whose energy is used to make glucose.",
        piege="Green is the colour that leaves reflect, so green light is the least useful to photosynthesis."))

    a(Q("b22", ["gas tests and absorbents"], "moyenne",
        "Potassium hydroxide solution is placed in a respiration experiment in order to",
        "Absorb carbon dioxide.", ["Absorb oxygen.", "Release oxygen.", "Absorb water vapour."],
        "Know the common absorbents: potassium hydroxide (or soda lime) absorbs carbon dioxide, and anhydrous calcium chloride absorbs water vapour.",
        "Potassium hydroxide is an alkali that reacts with carbon dioxide, so the carbon dioxide released by the organism is removed from the air of the apparatus."))

    a(Q("b23", ["transport in plants"], "faible",
        "Water and mineral salts are carried up the stem in the",
        "Xylem.", ["Phloem.", "Cambium.", "Epidermis."],
        "Xylem carries water and mineral salts upwards from the roots, and phloem carries manufactured food (sucrose) to all parts of the plant.",
        "Xylem vessels are dead, hollow tubes with strong walls. They form a continuous pathway from the roots to the leaves."))

    a(Q("b24", ["transport in plants"], "faible",
        "The movement of manufactured food, such as sucrose, from the leaves to other parts of a plant is called",
        "Translocation.", ["Transpiration.", "Osmosis.", "Diffusion."],
        "Translocation is the transport of manufactured food in the phloem, and transpiration is the loss of water vapour from the leaves.",
        "Sucrose made in the leaves is carried in the phloem to the growing points and the storage organs.",
        piege="Transpiration is a loss of water, while translocation is a movement of food."))

    a(Q("b25", ["transpiration"], "faible",
        "{FIG} shows the rate of transpiration of a plant during one day. The rate of transpiration is highest at",
        "$13{:}00$.", ["$09{:}00$.", "$11{:}00$.", "$16{:}00$."],
        "To read a maximum on a graph, find the highest point of the curve and read the value on the horizontal axis below it.",
        "The curve rises to its highest point at $13{:}00$, where the rate is $7.0$ g per hour, and then falls.",
        fig="transpiration"))

    a(Q("b28", ["plant tropisms"], "faible",
        "The growth of a shoot towards a source of light is called",
        "Positive phototropism.", ["Negative phototropism.", "Positive geotropism.", "Negative geotropism."],
        "A tropism is a growth response to a stimulus: it is positive when growth is towards the stimulus and negative when away from it.",
        "Light is the stimulus and the shoot grows towards it: positive phototropism."))

    a(Q("b29", ["flower structure"], "faible",
        "The male reproductive organ of a flower is the",
        "Stamen.", ["Carpel.", "Sepal.", "Petal."],
        "A flower has two sets of reproductive organs: the stamens (male) and the carpels (female).",
        "A stamen is made of an anther, which produces pollen grains, and a filament that holds it up."))

    a(Q("b30", ["pollination and fertilization in plants"], "faible",
        "The transfer of pollen from an anther to a stigma is called",
        "Pollination.", ["Fertilisation.", "Germination.", "Dispersal."],
        "Pollination is the transfer of pollen from anther to stigma, and fertilisation is the fusion of the male and female gametes.",
        "Pollen is carried by insects or by wind. Fertilisation happens later, after the pollen tube has grown down to the ovule."))

    a(Q("b31", ["seed germination"], "faible",
        "Which of the following is not needed for the germination of a bean seed?",
        "Light.", ["Water.", "Oxygen.", "A suitable temperature."],
        "A seed needs water, oxygen and warmth to germinate; light is needed later, for photosynthesis by the seedling.",
        "Many seeds germinate in the dark, underground, using the food stored in their cotyledons."))

    a(Q("b33", ["cell respiration"], "moyenne",
        "When yeast respires anaerobically, it produces",
        "Ethanol and carbon dioxide.", ["Lactic acid and carbon dioxide.", "Water and carbon dioxide.", "Ethanol and oxygen."],
        "Anaerobic respiration releases energy without oxygen: yeast makes ethanol and carbon dioxide, while muscle cells make lactic acid.",
        "Fermentation by yeast gives glucose $\\rightarrow$ ethanol + carbon dioxide + a little energy.",
        piege="Lactic acid is the product of anaerobic respiration in animal muscles, not in yeast."))

    a(Q("b35", ["gaseous exchange in humans"], "faible",
        "Gaseous exchange in the lungs takes place in the",
        "Alveoli.", ["Bronchi.", "Trachea.", "Bronchioles."],
        "The air sacs, the alveoli, have thin walls and a rich blood supply, so gases diffuse quickly between air and blood.",
        "Oxygen diffuses from the alveolar air into the blood, and carbon dioxide diffuses the other way. The trachea, bronchi and bronchioles are only air passages."))

    a(Q("b36", ["gaseous exchange in humans"], "moyenne",
        "During inhalation, the",
        "Diaphragm contracts and flattens.", ["Diaphragm relaxes and curves upwards.", "Ribs move downwards and inwards.", "Volume of the thorax decreases."],
        "In inhalation the diaphragm and the external intercostal muscles contract, the volume of the thorax increases and the air pressure inside falls.",
        "The lower pressure in the lungs draws air in. In exhalation the opposite happens: the diaphragm relaxes and domes up, and the ribs move down and in."))

    a(Q("b37", ["gaseous exchange in humans"], "moyenne",
        "The table shows the composition of inhaled and exhaled air.\n\n" + TABLE_AIR +
        "\n\nThe percentage of carbon dioxide in exhaled air is greater than in inhaled air by a factor of",
        "$100$.", ["$10$.", "$4$.", "$1\\,000$."],
        "To compare two values, divide the larger by the smaller: here the percentage in exhaled air divided by the percentage in inhaled air.",
        "$\\dfrac{4.00}{0.04}=100$, so exhaled air contains $100$ times more carbon dioxide than inhaled air.",
        piege="The difference between the two percentages, $3.96$, is not the factor asked for."))

    a(Q("b38", ["blood circulation"], "faible",
        "Which blood vessel carries oxygenated blood from the lungs to the heart?",
        "Pulmonary vein.", ["Pulmonary artery.", "Aorta.", "Vena cava."],
        "Arteries carry blood away from the heart and veins carry blood to the heart; the pulmonary vessels are the only ones where this does not match the oxygen content.",
        "The pulmonary vein brings oxygenated blood from the lungs to the left atrium. The pulmonary artery carries deoxygenated blood to the lungs."))

    a(Q("b39", ["mammalian heart"], "faible",
        "The valve that prevents blood from flowing back from the left ventricle into the left atrium is the",
        "Bicuspid valve.", ["Tricuspid valve.", "Semilunar valve.", "Pulmonary valve."],
        "The valve between the left atrium and the left ventricle has two flaps (bicuspid); the one on the right side has three (tricuspid).",
        "The bicuspid valve closes when the left ventricle contracts, so blood is forced into the aorta and not back into the atrium."))

    a(Q("b41", ["mammalian heart"], "moyenne",
        "{FIG} shows the heart rate of a student after exercise. The resting heart rate is $70$ beats per minute. The heart rate first returned to its resting value after",
        "$6$ minutes.", ["$4$ minutes.", "$8$ minutes.", "$2$ minutes."],
        "Read a value on a graph by following the gridlines from the axis to the curve, and look for the first point that reaches the value asked for.",
        "The curve falls from $150$ beats per minute and first reaches $70$ at $6$ minutes. It stays at $70$ afterwards, so $8$ minutes is not the first time.",
        fig="coeur"))

    a(Q("b42", ["the human eye"], "faible",
        "The part of the eye that controls the amount of light entering is the",
        "Iris.", ["Cornea.", "Retina.", "Lens."],
        "The iris is a ring of muscle whose opening, the pupil, becomes smaller in bright light and larger in dim light.",
        "The cornea and lens refract the light, and the retina contains the light-sensitive cells."))

    a(Q("b48", ["nervous system"], "moyenne",
        "Which of the following shows the correct pathway of a nerve impulse in a reflex arc?",
        "Receptor, sensory neurone, relay neurone, motor neurone, effector.",
        ["Receptor, motor neurone, relay neurone, sensory neurone, effector.", "Effector, sensory neurone, relay neurone, motor neurone, receptor.", "Receptor, relay neurone, sensory neurone, motor neurone, effector."],
        "In a reflex arc the impulse goes from the receptor, along the sensory neurone to the spinal cord, then to a relay neurone, a motor neurone and the effector.",
        "The receptor detects the stimulus. The sensory neurone carries the impulse to the spinal cord, the relay neurone passes it on, and the motor neurone carries it to the effector, a muscle or a gland, which responds."))

    a(Q("b44", ["body temperature control"], "faible",
        "Which response helps to lower body temperature on a hot day?",
        "Sweating.", ["Shivering.", "Hair standing erect.", "Constriction of skin arterioles."],
        "To cool down, the body loses heat by sweating and by widening the skin arterioles (vasodilation).",
        "Sweat evaporates from the skin and takes heat from the body. Shivering, erect hairs and constriction of arterioles all help to keep heat in."))

    a(Q("b46", ["endocrine system"], "faible",
        "Which hormone prepares the body for 'fight or flight'?",
        "Adrenaline.", ["Insulin.", "Thyroxine.", "Oestrogen."],
        "Adrenaline, released by the adrenal glands, quickly raises the heart rate, blood glucose and blood flow to the muscles.",
        "Insulin lowers blood glucose, thyroxine controls the metabolic rate and oestrogen is a female sex hormone."))

    a(Q("b47", ["nervous system"], "faible",
        "The part of the brain that coordinates balance and muscular movement is the",
        "Cerebellum.", ["Cerebrum.", "Medulla oblongata.", "Hypothalamus."],
        "Link each brain region to its role: the cerebrum to thinking and memory, the cerebellum to balance, the medulla to heartbeat and breathing.",
        "The cerebellum receives information from the ears and muscles and coordinates smooth movements and balance."))

    a(Q("b49", ["excretory system"], "moyenne",
        "The main nitrogenous waste product excreted by humans is",
        "Urea.", ["Uric acid.", "Ammonia.", "Glucose."],
        "Excess amino acids are broken down in the liver, and the nitrogen-containing part is converted to urea, which the kidneys remove.",
        "Urea is made in the liver and carried by the blood to the kidneys, where it leaves the body in urine. Healthy kidneys reabsorb all the glucose, so it is not excreted."))

    a(Q("b50", ["kidney and nephron"], "moyenne",
        "Ultrafiltration of the blood in the kidney takes place in the",
        "Glomerulus.", ["Loop of Henle.", "Collecting duct.", "Bladder."],
        "In the nephron, ultrafiltration happens between the glomerulus and the Bowman's capsule, and the filtrate then passes along the tubule.",
        "High pressure in the glomerulus forces water, glucose, salts and urea out of the blood into the capsule, while blood cells and large proteins stay in the blood."))

    a(Q("b51", ["human reproductive system"], "faible",
        "In humans, fertilisation normally takes place in the",
        "Oviduct.", ["Uterus.", "Vagina.", "Ovary."],
        "The sperm swim up through the uterus and meet the egg cell in the oviduct, where fertilisation occurs.",
        "The fertilised egg then travels down the oviduct and implants in the wall of the uterus."))

    a(Q("b52", ["monohybrid inheritance"], "moyenne",
        "In pea plants the allele for tall stems $(T)$ is dominant to the allele for dwarf stems $(t)$. A heterozygous tall plant is crossed with a dwarf plant. The percentage of dwarf plants expected in the offspring is",
        "$50\\%$", ["$25\\%$", "$75\\%$", "$100\\%$"],
        "Write the genotypes of the parents, list the gametes of each, and combine them in a Punnett square to count the offspring.",
        "$Tt\\times tt$: the gametes are $T$ or $t$ from the first parent and only $t$ from the second. The offspring are $Tt$ (tall) and $tt$ (dwarf) in equal numbers: $50\\%$ dwarf.",
        piege="A heterozygous parent gives $T$ or $t$ with equal chance, so the result is $1:1$, not $3:1$."))

    a(Q("b62", ["human skeleton and joints"], "faible",
        "The elbow joint is an example of a",
        "Hinge joint.", ["Ball-and-socket joint.", "Pivot joint.", "Fixed joint."],
        "Joints are named by the movement they allow: hinge joints move in one plane, ball-and-socket joints move in all directions.",
        "The elbow lets the forearm bend and straighten in one direction only, like a door hinge. The shoulder and the hip are ball-and-socket joints."))

    a(Q("b54", ["food chains and food webs"], "elevee",
        "In the food web in {FIG}, the number of different food chains that end with the hawk is",
        "$5$.", ["$3$.", "$4$.", "$6$."],
        "Follow each arrow from a producer to the top consumer, and count every different path from start to end.",
        "The chains are: grass, rat, hawk; maize, rat, hawk; grass, rat, snake, hawk; maize, rat, snake, hawk; and grass, grasshopper, toad, snake, hawk. That gives $5$ chains.",
        piege="The rat is eaten by both the snake and the hawk, and it eats both grass and maize, so it belongs to four of the chains.",
        fig="reseau"))

    a(Q("b55", ["food chains and food webs"], "faible",
        r"In the food chain grass $\rightarrow$ grasshopper $\rightarrow$ toad $\rightarrow$ snake, the toad is a",
        "Secondary consumer.", ["Primary consumer.", "Producer.", "Tertiary consumer."],
        "Count the trophic levels from the producer: the producer is first, the primary consumer eats the producer, the secondary consumer eats the primary consumer.",
        "Grass is the producer and the grasshopper, which eats grass, is the primary consumer. The toad eats the grasshopper, so it is the secondary consumer."))

    a(Q("b57", ["nitrogen cycle"], "moyenne",
        "Nitrogen-fixing bacteria living in the root nodules of leguminous plants",
        "Convert nitrogen gas into ammonium compounds.", ["Convert nitrates into nitrogen gas.", "Convert ammonia into carbon dioxide.", "Convert proteins into starch."],
        "Nitrogen fixation turns nitrogen gas of the air into compounds that plants can use; denitrifying bacteria do the opposite.",
        "Bacteria such as Rhizobium, which live in the nodules of beans and groundnuts, fix atmospheric nitrogen into ammonium compounds and nitrates, which the plant absorbs.",
        piege="Denitrifying bacteria convert nitrates to nitrogen gas: that is the reverse change."))

    a(Q("b58", ["carbon cycle"], "faible",
        "Which process does not return carbon dioxide to the atmosphere?",
        "Photosynthesis.", ["Respiration.", "Combustion.", "Decay of dead organisms."],
        "In the carbon cycle, photosynthesis removes carbon dioxide from the air, while respiration, burning and decay return it.",
        "Green plants use carbon dioxide to make glucose, so photosynthesis takes carbon dioxide out of the atmosphere."))

    a(Q("b59", ["air pollution"], "moyenne",
        "Which pollutant in vehicle exhaust fumes combines with haemoglobin and reduces the oxygen carried by the blood?",
        "Carbon monoxide.", ["Carbon dioxide.", "Sulphur dioxide.", "Nitrogen dioxide."],
        "Know the effect of each air pollutant: carbon monoxide is poisonous, sulphur dioxide and nitrogen dioxide cause acid rain, carbon dioxide causes global warming.",
        "Carbon monoxide binds to haemoglobin much more strongly than oxygen does, so the blood carries less oxygen and the person may suffocate.",
        piege="Carbon dioxide is not poisonous in this way: its main effect as a pollutant is to increase global warming."))

    a(Q("b60", ["malaria and disease vectors"], "faible",
        "Malaria is spread from person to person by the",
        "Female Anopheles mosquito.", ["Female Culex mosquito.", "Tsetse fly.", "Housefly."],
        "A vector is an organism that carries a pathogen from one host to another; the vector of malaria is the female Anopheles mosquito.",
        "The mosquito injects the parasite Plasmodium into the blood when it feeds. The tsetse fly spreads sleeping sickness and the housefly spreads cholera and typhoid."))

    a(Q("b61", ["genetic engineering"], "moyenne",
        "In genetic engineering, a gene is cut out of DNA with a",
        "Restriction enzyme.", ["Ligase.", "Amylase.", "Catalase."],
        "Restriction enzymes cut DNA at specific sites, and ligase joins DNA pieces together.",
        "The gene is cut out with a restriction enzyme and then joined into a plasmid by ligase.",
        piege="Ligase is the enzyme that joins DNA fragments, so it is used after the cutting."))

    a(Q("b63", ["mammalian skin"], "faible",
        "Which layer of the mammalian skin contains the sweat glands and blood vessels?",
        "Dermis.", ["Epidermis.", "Cornified layer.", "Malpighian layer."],
        "The skin has two main layers: a thin outer epidermis without blood vessels and a thicker dermis beneath it.",
        "The dermis contains sweat glands, blood capillaries, sensory receptors, hair follicles and sebaceous glands."))

    a(Q("b66", ["human embryo and gestation"], "faible",
        "The function of the placenta during pregnancy is to",
        "Supply the foetus with oxygen and nutrients.", ["Produce egg cells.", "Digest food for the foetus.", "Store urine."],
        "The placenta is the organ where the blood of the mother and the blood of the foetus pass close together without mixing.",
        "Oxygen, glucose and other nutrients diffuse from the mother's blood into the foetal blood, and carbon dioxide and urea diffuse the other way."))

    return q
