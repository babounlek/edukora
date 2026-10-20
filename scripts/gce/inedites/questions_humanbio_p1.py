r"""Questions de l'epreuve inedite GCE O Level Human Biology Paper 1 n.1 (50 QCM). Voir generer_humanbio_p1.py.

Q(id, themes, difficulte, enonce, bonne option, 3 distracteurs, rappel, resolution, piege, conseil, figure).
Chaines BRUTES (r"..."). `{FIG}` est remplace par « Figure N ». Ordre : celui du programme (cellule, squelette, systeme nerveux, hormones, digestion,
respiration, sang, immunite, reproduction, genetique, ecologie, sante), comme les vrais Paper 1 de Human Biology ; les questions des themes que le
Paper 2 de la session traite en grand (excretion, groupes sanguins et heredite ABO, vitamines et mineraux, pollution de l'air, VIH/SIDA) ne portent
que sur des faits que ses grilles ne reprennent pas.
"""


def Q(qid, themes, diff, stem, ok, bad, rappel, sol, piege=None, conseil=None, fig=None, cle_fixee=None):
    return dict(id=qid, themes=themes, diff=diff, stem=stem, ok=ok, bad=bad, rappel=rappel, sol=sol, piege=piege,
                conseil=conseil, fig=fig, cle_fixee=cle_fixee)


def questions():
    q = []
    a = q.append

    a(Q("h01", ["cell organelles"], "faible",
        r"Which organelle contains enzymes that digest worn-out cell parts and bacteria that the cell has engulfed?",
        r"Lysosome", [r"Ribosome", r"Golgi body", r"Centriole"],
        r"Lysosomes are small sacs filled with digestive enzymes. They break down old organelles and, in white blood cells, the bacteria that have been engulfed.",
        r"Ribosomes make proteins, the Golgi body packages and secretes substances, and centrioles organise the spindle during cell division. Only the lysosome holds digestive enzymes."))
    a(Q("h02", ["human sexual reproduction", "cell division"], "faible",
        r"A human egg cell and a human sperm cell each contain $23$ chromosomes. The number of chromosomes in the zygote formed when they fuse is",
        r"$46$", [r"$23$", r"$92$", r"$69$"],
        r"Gametes are made by meiosis and have half the chromosome number of the body cells. Fertilisation joins two gametes and restores the full number.",
        r"The zygote receives $23$ chromosomes from the egg and $23$ from the sperm: $23+23=46$, the number found in every human body cell. This is how the chromosome number stays constant from one generation to the next.",
        piege=r"$23$ is the number in each gamete, not in the zygote; $92$ would be the number after the zygote copied its chromosomes for its first division."))
    a(Q("h03", ["animal tissues"], "faible",
        r"The tissue that lines the inside of the mouth and covers the outer surface of the skin is",
        r"epithelial tissue", [r"connective tissue", r"muscular tissue", r"nervous tissue"],
        r"Epithelial tissue is made of closely packed cells that cover the body and line its cavities and tubes.",
        r"Epithelial cells form a continuous sheet that protects the surface it covers. Connective tissue supports and joins organs, muscular tissue contracts and nervous tissue carries impulses."))
    a(Q("h04", ["diffusion osmosis and active transport"], "moyenne",
        r"Red blood cells placed in distilled water swell and burst. The process that makes them swell is",
        r"osmosis", [r"active transport", r"filtration", r"evaporation"],
        r"Osmosis is the movement of water from a dilute solution to a more concentrated solution through a partially permeable membrane.",
        r"Distilled water is more dilute than the cytoplasm of the red cell, so water enters the cell through its membrane by osmosis. The cell has no wall to resist the pressure and it bursts. Active transport needs energy from the cell and moves substances against a gradient."))
    a(Q("h05", ["human skeleton and joints"], "faible",
        r"Which joint allows the thigh bone to move in all directions at the hip?",
        r"Ball-and-socket joint", [r"Hinge joint", r"Pivot joint", r"Gliding joint"],
        r"In a ball-and-socket joint the rounded head of one bone fits into a cup-shaped socket, which allows movement in all directions. The hip and the shoulder are examples.",
        r"The head of the femur fits into the socket of the pelvis. A hinge joint (elbow, knee) moves in one plane only, a pivot joint (top of the neck) allows rotation and a gliding joint allows sliding movements."))
    a(Q("h06", ["human skeleton and joints"], "faible",
        r"Which structures act as shock absorbers between the vertebrae of the backbone?",
        r"Intervertebral discs", [r"Ligaments", r"Tendons", r"Ribs"],
        r"Between neighbouring vertebrae there are discs of cartilage that absorb shocks and allow the backbone to bend a little.",
        r"The intervertebral discs are pads of cartilage: they cushion the vertebrae when we walk or jump. Ligaments hold the vertebrae together, tendons join muscles to bones and the ribs protect the chest."))
    a(Q("h07", ["muscle contraction"], "faible",
        r"Tendons are strong cords that join",
        r"muscles to bones", [r"bones to bones", r"muscles to muscles", r"skin to muscles"],
        r"A muscle pulls on a bone through its tendon, and one bone is held to another by a ligament.",
        r"A tendon is made of tough, inelastic fibres. When a muscle contracts it pulls on the tendon, and the tendon moves the bone. Bones are joined to bones by ligaments."))
    a(Q("h08", ["neurone structure"], "faible",
        r"Which part of a motor neurone carries nerve impulses away from the cell body?",
        r"Axon", [r"Dendrite", r"Myelin sheath", r"Nucleus"],
        r"A neurone has a cell body with short dendrites, which receive impulses, and a long axon, which carries impulses away.",
        r"The axon is the long extension of the neurone; in a motor neurone it carries the impulse to the muscle. The dendrites bring impulses towards the cell body and the myelin sheath only insulates the axon."))
    a(Q("h09", ["reflex action"], "moyenne",
        r"In a reflex arc, the neurone inside the spinal cord that connects the sensory neurone to the motor neurone is the",
        r"relay neurone", [r"receptor neurone", r"effector neurone", r"sensory neurone"],
        r"A reflex arc is made of a receptor, a sensory neurone, a relay neurone in the spinal cord, a motor neurone and an effector.",
        r"The relay (intermediate) neurone lies completely in the grey matter of the spinal cord and passes the impulse from the sensory to the motor neurone. The sensory neurone brings the impulse from the receptor, and the motor neurone takes it to the effector."))
    a(Q("h10", ["nervous system"], "faible",
        r"Which part of the brain coordinates balance and the smooth movement of muscles?",
        r"Cerebellum", [r"Cerebrum", r"Medulla oblongata", r"Hypothalamus"],
        r"The cerebellum, at the back of the brain, coordinates balance, posture and muscle movement.",
        r"The cerebrum controls thinking, memory and voluntary actions, the medulla controls breathing and heart rate, and the hypothalamus controls body temperature."))
    a(Q("h11", ["the human eye"], "faible",
        r"The coloured part of the eye that changes the size of the pupil is the",
        r"iris", [r"cornea", r"retina", r"lens"],
        r"The iris contains muscles that make the pupil smaller in bright light and larger in dim light.",
        r"The iris controls how much light enters the eye. The cornea refracts light, the lens focuses it and the retina contains the light-sensitive cells."))
    a(Q("h12", ["defects of vision"], "faible",
        r"A short-sighted person cannot see distant objects clearly. This defect is corrected by wearing spectacles with",
        r"concave lenses", [r"convex lenses", r"cylindrical lenses", r"bifocal lenses"],
        r"In short sight the image of a distant object forms in front of the retina; a diverging lens moves the image back onto the retina.",
        r"A concave lens spreads the rays a little before they enter the eye, so the focus falls on the retina. A convex lens is used for long sight, where the image forms behind the retina.",
        piege=r"Short sight (myopia) and long sight (hypermetropia) need opposite lenses: concave for short sight, convex for long sight."))
    a(Q("h13", ["endocrine system"], "faible",
        r"Which gland controls the activities of several other endocrine glands and is called the master gland?",
        r"Pituitary gland", [r"Thyroid gland", r"Pancreas", r"Adrenal gland"],
        r"The pituitary gland, at the base of the brain, secretes hormones that control the thyroid gland, the adrenal glands and the gonads.",
        r"The pituitary releases hormones that make other glands work, and so it is called the master gland. The thyroid, the pancreas and the adrenal glands are controlled by hormones or by blood levels."))
    a(Q("h14", ["blood sugar regulation"], "faible",
        r"After a meal rich in carbohydrates, which hormone is released to lower the blood glucose level?",
        r"Insulin", [r"Glucagon", r"Adrenaline", r"Thyroxine"],
        r"Insulin, made by the pancreas, makes the liver and muscles take up glucose and store it as glycogen. Glucagon has the opposite effect.",
        r"After a meal the blood glucose level rises. The pancreas releases insulin, which lowers it by converting glucose into glycogen. Glucagon raises the level when it is too low.",
        piege=r"Glucagon and insulin act in opposite directions: insulin lowers, glucagon raises the blood glucose level."))
    a(Q("h15", ["absorption in the ileum", "human digestive system"], "faible",
        r"Most of the digested food is absorbed into the blood in the",
        r"ileum", [r"stomach", r"oesophagus", r"colon"],
        r"The ileum is long, folded and lined with villi, which give it a very large surface area for absorption.",
        r"Digestion is completed in the small intestine and its last part, the ileum, absorbs most of the products. The stomach absorbs little (some alcohol), the oesophagus only carries food and the colon absorbs mainly water."))
    a(Q("h16", ["digestive secretions"], "faible",
        r"The enzyme in saliva that starts the digestion of starch in the mouth is",
        r"salivary amylase", [r"pepsin", r"lipase", r"trypsin"],
        r"Amylase breaks starch down into maltose. Pepsin and trypsin digest proteins, and lipase digests fats.",
        r"Salivary amylase acts on cooked starch in the mouth. Pepsin works in the stomach, trypsin in the small intestine, and lipase digests fats in the small intestine."))
    a(Q("h17", ["bile and fat digestion"], "faible",
        r"Bile helps the digestion of fats by",
        r"breaking large fat globules into tiny droplets", [r"changing fats into amino acids", r"digesting fats into fatty acids and glycerol", r"killing the bacteria in the mouth"],
        r"Bile is made in the liver and stored in the gall bladder. It contains no enzymes: it emulsifies fats.",
        r"Emulsification gives fat droplets a larger surface area, so that lipase can digest them more quickly. The digestion itself, into fatty acids and glycerol, is done by lipase, not by bile.",
        piege=r"Bile does not digest fats chemically; it contains no enzyme."))
    a(Q("h18", ["biochemical food tests"], "faible",
        r"A food sample is heated with Benedict's solution and the blue colour changes to brick-red. The sample contains",
        r"a reducing sugar", [r"starch", r"protein", r"fat"],
        r"Benedict's solution gives a brick-red precipitate when heated with a reducing sugar such as glucose. Iodine tests for starch, biuret for protein and ethanol for fat.",
        r"A brick-red precipitate after heating is a positive test for reducing sugars. Starch would turn iodine blue-black, protein would give a purple colour with biuret and fat would give a white emulsion with ethanol and water."))
    a(Q("h19", ["gaseous exchange in humans"], "moyenne",
        r"Which gas makes up the largest part of the air that a person breathes out?",
        r"Nitrogen", [r"Oxygen", r"Carbon dioxide", r"Water vapour"],
        r"Inhaled air is about $78\%$ nitrogen, $21\%$ oxygen and $0.04\%$ carbon dioxide. Exhaled air has less oxygen, more carbon dioxide and more water vapour, but nitrogen is still the main gas.",
        r"The body does not use nitrogen, so it passes through the lungs unchanged and makes up about $78\%$ of exhaled air. Exhaled air contains about $16\%$ oxygen and $4\%$ carbon dioxide.",
        piege=r"Carbon dioxide is the gas that increases most, but even in exhaled air it is only about $4\%$ of the total."))
    a(Q("h20", ["gaseous exchange in humans"], "faible",
        r"The walls of the alveoli are only one cell thick. This helps",
        r"oxygen and carbon dioxide to diffuse quickly", [r"to trap dust from the air", r"to warm the air before it reaches the blood", r"to produce mucus"],
        r"Alveoli are the gas exchange surface of the lungs: they are thin, moist and surrounded by blood capillaries, which makes diffusion fast.",
        r"A very short distance between the air and the blood speeds up the diffusion of oxygen into the blood and of carbon dioxide out of it. Dust is trapped by mucus and cilia in the air passages, not by the alveoli."))
    a(Q("h21", ["lung volumes", "breathing mechanism in mammals"], "moyenne",
        r"{FIG} shows the volume of air in the lungs of a resting person over $12$ seconds. If the person goes on breathing in the same way, the volume of air breathed in during one minute is",
        r"$7500\ \text{cm}^{3}$", [r"$1500\ \text{cm}^{3}$", r"$6000\ \text{cm}^{3}$", r"$3750\ \text{cm}^{3}$"],
        r"The volume of air breathed in with each breath is the tidal volume. The volume breathed in per minute is the tidal volume multiplied by the number of breaths per minute.",
        r"Each breath raises the volume from $2500\ \text{cm}^{3}$ to $3000\ \text{cm}^{3}$: the tidal volume is $500\ \text{cm}^{3}$. There are $3$ breaths in $12$ seconds, that is $15$ breaths in one minute. Volume per minute $=15\times500=7500\ \text{cm}^{3}$.",
        piege=r"$1500\ \text{cm}^{3}$ is the volume breathed in during the $12$ seconds of the trace only ($3\times500$): the question asks for one minute.",
        fig="spiro"))
    a(Q("h22", ["blood components and functions"], "faible",
        r"Which part of the blood carries dissolved digested food and hormones round the body?",
        r"Plasma", [r"Red blood cells", r"Platelets", r"White blood cells"],
        r"Plasma is the pale yellow liquid part of the blood. It carries dissolved food, hormones, carbon dioxide and urea.",
        r"Red blood cells carry oxygen, platelets help the blood to clot and white blood cells defend the body. The dissolved substances travel in the plasma."))
    a(Q("h23", ["mammalian heart"], "moyenne",
        r"Blood passes from the left atrium to the left ventricle through the",
        r"bicuspid valve", [r"tricuspid valve", r"aortic valve", r"pulmonary valve"],
        r"Valves keep the blood moving in one direction. The bicuspid (mitral) valve is on the left side of the heart and the tricuspid valve is on the right.",
        r"The valve between the left atrium and the left ventricle has two flaps and is called the bicuspid valve. The tricuspid valve is between the right atrium and the right ventricle; the aortic and pulmonary valves are at the exits of the ventricles."))
    a(Q("h24", ["blood vessels"], "faible",
        r"Which vessel carries deoxygenated blood from the heart to the lungs?",
        r"Pulmonary artery", [r"Pulmonary vein", r"Aorta", r"Vena cava"],
        r"An artery carries blood away from the heart. The pulmonary artery is the only artery that carries deoxygenated blood.",
        r"The right ventricle pumps deoxygenated blood into the pulmonary artery, which takes it to the lungs. The pulmonary vein brings oxygenated blood back, the aorta takes oxygenated blood to the body and the vena cava brings deoxygenated blood to the heart."))
    a(Q("h25", ["blood clotting"], "faible",
        r"The insoluble protein that forms a mesh of fibres over a wound when blood clots is",
        r"fibrin", [r"fibrinogen", r"haemoglobin", r"thrombin"],
        r"In blood clotting a soluble protein of the plasma, fibrinogen, is changed into insoluble fibrin threads, which trap blood cells and form a clot.",
        r"Fibrin is the insoluble protein of the clot. Fibrinogen is its soluble form in the plasma, thrombin is the enzyme that changes fibrinogen into fibrin, and haemoglobin carries oxygen.",
        piege=r"Fibrinogen is the soluble protein in the plasma; fibrin is the insoluble protein of the clot."))
    a(Q("h26", ["blood groups"], "moyenne",
        r"A person of blood group O (and Rhesus negative) can safely donate blood to",
        r"people of any of the ABO groups", [r"people of group O only", r"people of group AB only", r"people of groups A and B only"],
        r"Red cells of group O carry neither the A nor the B antigen, so the antibodies in the blood of the receiver cannot make them clump together.",
        r"Because group O red cells have no A or B antigen, they do not react with the anti-A and anti-B antibodies of any ABO group: group O is the universal donor. Group AB is the universal receiver."))
    a(Q("h27", ["mammalian heart", "human health and lifestyle"], "moyenne",
        r"{FIG} shows the pulse rate of a student after a run, taken every minute. By how many beats per minute did the pulse rate fall during the first $3$ minutes of recovery?",
        r"$40$", [r"$30$", r"$58$", r"$18$"],
        r"The fall in a quantity is its value at the start minus its value at the end of the period considered.",
        r"At $0$ minutes the pulse rate is $130$ beats per minute and at $3$ minutes it is $90$ beats per minute. The fall is $130-90=40$ beats per minute.",
        piege=r"$58$ is the fall over the whole recovery ($130-72$); the question asks only for the first $3$ minutes.",
        fig="pouls"))
    a(Q("h28", ["body temperature control"], "moyenne",
        r"Which response of the skin helps the body to lose heat on a very hot day?",
        r"Sweating and widening of the skin blood vessels", [r"Shivering and narrowing of the skin blood vessels", r"Standing of the body hairs and narrowing of the skin blood vessels", r"Releasing adrenaline and shivering"],
        r"To lose heat the skin produces sweat, which cools the body as it evaporates, and the arterioles of the skin widen so that more warm blood flows near the surface.",
        r"Sweating and vasodilation increase heat loss. Shivering, narrowing of the blood vessels and standing of the hairs are responses to cold: they reduce heat loss or make heat."))
    a(Q("h29", ["structure of mammalian skin"], "faible",
        r"The layer of the skin that contains the sweat glands, the hair follicles and the blood vessels is the",
        r"dermis", [r"epidermis", r"cuticle", r"keratin layer"],
        r"The skin has two main layers: a thin outer epidermis and a thicker inner dermis, below which there is a layer of fat.",
        r"The dermis is the living layer under the epidermis. It contains sweat glands, hair follicles, nerve endings and blood vessels. The epidermis has no blood vessels, and keratin is the tough protein of its outer cells."))
    a(Q("h30", ["lymphatic system"], "moyenne",
        r"The small swellings along the lymph vessels that filter out bacteria are the",
        r"lymph nodes", [r"lacteals", r"lymph capillaries", r"valves of the veins"],
        r"Lymph from the tissues passes through lymph nodes, which contain white blood cells that trap and destroy bacteria before the lymph returns to the blood.",
        r"Lymph nodes act as filters on the lymph vessels. Lacteals are lymph vessels in the villi that absorb fats; lymph capillaries collect the fluid from the tissues."))
    a(Q("h31", ["immunity and vaccines"], "moyenne",
        r"A baby receives antibodies from its mother's milk. This type of immunity is",
        r"natural passive immunity", [r"natural active immunity", r"artificial active immunity", r"artificial passive immunity"],
        r"Passive immunity is given by ready-made antibodies; active immunity is made by the person's own body. Natural immunity is acquired without medical help.",
        r"The baby does not make the antibodies itself (passive), and it gets them naturally through breast milk. Artificial immunity would be an injection of antibodies or a vaccine."))
    a(Q("h32", ["white blood cells"], "moyenne",
        r"Which cells of the blood protect the body by engulfing and digesting bacteria?",
        r"Phagocytes", [r"Red blood cells", r"Platelets", r"Lymphocytes"],
        r"White blood cells defend the body in two ways: some engulf and digest the microbes (phagocytosis) and others take part in the immune response.",
        r"Phagocytes are white blood cells that flow towards the place of an infection, engulf bacteria and digest them with the enzymes of their lysosomes. Red blood cells carry oxygen and platelets help blood to clot."))
    a(Q("h33", ["malaria and disease vectors"], "faible",
        r"Which organism carries the malaria parasite from one person to another?",
        r"Female Anopheles mosquito", [r"Female Aedes mosquito", r"Tsetse fly", r"Housefly"],
        r"Malaria is caused by a protozoan, Plasmodium. It is passed on by the bite of an infected female Anopheles mosquito.",
        r"The female Anopheles feeds on blood and transmits Plasmodium. The Aedes mosquito carries the viruses of yellow fever and dengue, the tsetse fly carries the parasite of sleeping sickness and the housefly spreads food-borne diseases."))
    a(Q("h34", ["human reproductive system"], "faible",
        r"In a man, sperm cells are produced in the",
        r"testes", [r"prostate gland", r"sperm duct", r"urethra"],
        r"The testes make sperm cells and the male hormone testosterone. The sperm duct carries the sperms and the prostate gland adds fluid to them.",
        r"Sperm cells are made in the seminiferous tubules of the testes. The sperm duct and the urethra only carry them, and the prostate gland adds a fluid that nourishes them."))
    a(Q("h35", ["menstrual cycle and hormones"], "moyenne",
        r"After ovulation, the follicle that released the egg develops into a structure that secretes progesterone. This structure is the",
        r"corpus luteum", [r"Graafian follicle", r"placenta", r"endometrium"],
        r"After ovulation the empty follicle becomes the corpus luteum, a yellow body which secretes progesterone to prepare the lining of the uterus for a possible pregnancy.",
        r"The corpus luteum forms from the follicle cells left behind in the ovary. The Graafian follicle is the follicle before ovulation, the placenta takes over the secretion of progesterone later in pregnancy, and the endometrium is the lining of the uterus."))
    a(Q("h36", ["human embryo and gestation"], "moyenne",
        r"The exchange of food, oxygen and wastes between the blood of the mother and the blood of the foetus takes place in the",
        r"placenta", [r"umbilical cord", r"amniotic sac", r"cervix"],
        r"The placenta is a spongy organ attached to the wall of the uterus. The blood of the mother and of the foetus come close together there but do not mix.",
        r"Substances diffuse across the thin walls of the villi of the placenta. The umbilical cord only carries the blood vessels to and from the foetus, and the amniotic sac holds the protective fluid."))
    a(Q("h37", ["gene mutations"], "faible",
        r"A sudden change in the structure of a gene or of a chromosome is called a",
        r"mutation", [r"crossing over", r"segregation", r"fertilisation"],
        r"A mutation is a sudden, random change in a gene or chromosome. It can be caused by mutagens such as ionising radiation.",
        r"Mutations are changes in the genetic material itself. Crossing over exchanges parts of chromosomes in meiosis, segregation separates the alleles into different gametes, and fertilisation joins two gametes."))
    a(Q("h38", ["genetics crosses", "monohybrid inheritance"], "moyenne",
        r"In humans the allele for brown eyes, $B$, is dominant over the allele for blue eyes, $b$. Two brown-eyed parents who are both $Bb$ have a child. The probability that the child is homozygous for brown eyes ($BB$) is",
        r"$25\%$", [r"$0\%$", r"$50\%$", r"$75\%$"],
        r"Each $Bb$ parent passes on $B$ or $b$ to a gamete with the same chance. Combine the gametes in a Punnett square to find each genotype.",
        r"The cross $Bb\times Bb$ gives $BB$, $Bb$, $Bb$ and $bb$ in the ratio $1:2:1$. Only one square in four is $BB$, so the probability is $\dfrac{1}{4}=25\%$.",
        piege=r"$75\%$ is the probability of a brown-eyed child ($BB$ or $Bb$), and $50\%$ is the probability of a heterozygous child."))
    a(Q("h39", ["sex-linked inheritance"], "moyenne",
        r"Colour blindness is caused by a recessive allele $X^{c}$ on the X chromosome. A colour-blind man, $X^{c}Y$, marries a woman who carries the allele, $X^{C}X^{c}$. The probability that a daughter of this couple is colour-blind is",
        r"$50\%$", [r"$0\%$", r"$25\%$", r"$100\%$"],
        r"A daughter receives one X chromosome from each parent and a son receives his X chromosome from his mother. Work out the daughters only, then give the probability among them.",
        r"Every daughter receives $X^{c}$ from her father. From her mother she receives $X^{C}$ or $X^{c}$ with the same chance. So half of the daughters are $X^{C}X^{c}$ (carriers) and half are $X^{c}X^{c}$ (colour-blind): $50\%$.",
        piege=r"$25\%$ is the probability that a child of the couple, whatever its sex, is a colour-blind daughter; the question is about daughters only."))
    a(Q("h40", ["sickle cell trait", "inherited blood disorders"], "elevee",
        r"In {FIG}, the healthy parents have one child with sickle cell anaemia, a condition caused by a recessive allele. Their second child is healthy. What is the probability that this healthy second child carries the sickle cell allele?",
        r"$\dfrac{2}{3}$", [r"$\dfrac{1}{2}$", r"$\dfrac{1}{3}$", r"$\dfrac{1}{4}$"],
        r"A child with a recessive disease has received the recessive allele from each parent: healthy parents of such a child are both carriers. For a healthy child, consider only the genotypes that are healthy.",
        r"Both parents are carriers, $Hb^{A}Hb^{S}$. Their children are $Hb^{A}Hb^{A}$, $Hb^{A}Hb^{S}$, $Hb^{A}Hb^{S}$ and $Hb^{S}Hb^{S}$ in equal numbers. The healthy children are the first three, and two of them are carriers: $\dfrac{2}{3}$.",
        piege=r"$\dfrac{1}{2}$ forgets that the child is already known to be healthy: the affected genotype $Hb^{S}Hb^{S}$ must be removed from the possibilities.",
        fig="pedigree"))
    a(Q("h41", ["birth control methods"], "moyenne",
        r"A vasectomy prevents pregnancy by",
        r"cutting and tying the sperm ducts", [r"removing the testes", r"blocking the fallopian tubes", r"stopping ovulation"],
        r"Vasectomy is a permanent method of birth control for men; tubal ligation is the equivalent for women.",
        r"In a vasectomy the sperm ducts are cut and tied, so that sperms cannot reach the penis, while the testes keep producing hormones. Blocking the fallopian tubes is tubal ligation, and stopping ovulation is the action of the contraceptive pill."))
    a(Q("h42", ["food chains and trophic levels"], "faible",
        r"In the food chain maize $\rightarrow$ grasshopper $\rightarrow$ toad $\rightarrow$ snake, all the toads die of a disease. What is the first change in the numbers of grasshoppers?",
        r"They increase.", [r"They decrease.", r"They stay the same.", r"They disappear."],
        r"In a food chain each organism is controlled by the one that feeds on it: if a consumer is removed, the numbers of its prey rise at first.",
        r"The toads eat the grasshoppers. With no toads, fewer grasshoppers are eaten and their numbers increase at first; later they may fall again because they eat too much maize. The snakes, which feed on the toads, are the ones that decrease."))
    a(Q("h43", ["nitrogen cycle"], "moyenne",
        r"Bacteria in the soil that change ammonium compounds into nitrates are called",
        r"nitrifying bacteria", [r"denitrifying bacteria", r"nitrogen-fixing bacteria", r"putrefying bacteria"],
        r"Nitrifying bacteria change ammonium compounds into nitrites and then into nitrates, which plants can absorb.",
        r"Nitrification is the step that makes nitrates for plants. Nitrogen-fixing bacteria change nitrogen gas into ammonium compounds, denitrifying bacteria change nitrates back to nitrogen gas and putrefying bacteria decompose proteins."))
    a(Q("h44", ["eutrophication", "water pollution"], "moyenne",
        r"Eutrophication of a lake is caused mainly by",
        r"nitrates and phosphates from fertilisers washing into the water", [r"oil spilled from boats", r"hot water from a factory", r"an increase in the oxygen dissolved in the water"],
        r"Eutrophication is the over-enrichment of water with nutrients. Algae grow quickly, die and are decomposed by bacteria that use up the oxygen of the water.",
        r"Fertiliser from the fields supplies nitrates and phosphates, so algae multiply (an algal bloom). When they die, the bacteria that decompose them use up the dissolved oxygen and fish die. Oil and hot water cause other forms of pollution."))
    a(Q("h45", ["water purification"], "faible",
        r"Which stage of water treatment is used to kill harmful microorganisms?",
        r"Chlorination", [r"Sedimentation", r"Screening", r"Aeration"],
        r"In a water works the water is screened, left to settle, filtered and finally treated with a small amount of chlorine to kill the germs that remain.",
        r"Chlorine is the disinfectant added at the end of the treatment. Screening removes large objects, sedimentation lets the solid particles settle and aeration adds oxygen."))
    a(Q("h46", ["first aid and emergency care"], "faible",
        r"The first action to take for a person with a deep wound that is bleeding heavily is to",
        r"press firmly on the wound with a clean pad", [r"wash the wound with soap and water for ten minutes", r"tie a rope tightly above the wound for several hours", r"give the person a hot drink"],
        r"Heavy bleeding must be controlled at once: direct pressure on the wound, preferably with a clean pad, raising the injured part and sending for help.",
        r"Firm pressure helps the blood to clot and slows the loss of blood. A rope left tight for hours can destroy the tissues below it, and a hot drink makes bleeding worse because it widens the blood vessels."))
    a(Q("h47", ["health care services"], "faible",
        r"A doctor who specialises in the diseases of the eye is called an",
        r"ophthalmologist", [r"cardiologist", r"dermatologist", r"paediatrician"],
        r"Medical specialists are named after the part of the body or the group of patients they treat.",
        r"An ophthalmologist treats the eyes, a cardiologist the heart, a dermatologist the skin and a paediatrician children."))
    a(Q("h48", ["social institutions and community life"], "faible",
        r"A social institution that takes care of children who have lost their parents is an",
        r"orphanage", [r"reformatory school", r"geriatric home", r"psychiatric home"],
        r"Social institutions give help to people with special needs: children without parents, the old, young offenders and people with mental illness.",
        r"An orphanage looks after children without parents. A reformatory school trains young offenders, a geriatric home cares for the elderly and a psychiatric home treats people with mental illness."))
    a(Q("h49", ["personal hygiene and health", "food-borne diseases"], "faible",
        r"Which disease can be spread by eating food prepared with unwashed hands?",
        r"Typhoid fever", [r"Malaria", r"Tetanus", r"Measles"],
        r"Food-borne diseases are spread when food or water is contaminated with the faeces of an infected person. Washing the hands with soap after using the toilet and before handling food stops this.",
        r"The bacteria of typhoid fever pass from the faeces of a carrier to the food by the hands. Malaria is spread by mosquitoes, tetanus enters wounds from the soil and measles is spread by droplets from the nose and mouth."))
    a(Q("h50", ["human health and lifestyle"], "faible",
        r"A diet that is rich in fats and sugars, combined with lack of exercise, can lead to",
        r"obesity", [r"malaria", r"cholera", r"tetanus"],
        r"Obesity is a condition in which too much fat is stored in the body. It increases the risk of heart disease and diabetes.",
        r"The body stores the energy that it does not use as fat, so a diet that gives more energy than the body needs leads to obesity. Malaria, cholera and tetanus are infectious diseases caused by parasites and bacteria."))
    return q
