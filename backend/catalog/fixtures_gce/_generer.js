// Génère les JSON du pilote GCE (voir test_gce_papers.py). Les textes sont ceux des sujets du
// Cameroon GCE Board (O Level, juin 2019) ; corrigés rédigés pour l'essai, à relire avant toute publication.
// Usage : node _generer.js
const fs = require("fs");

const base = (o) => ({
  pays: "cm", examen: "gce_ol", serie: null, origine: "officiel", annee: "2019",
  nature_epreuve: null, variante_sujet: null, ...o,
});
const q = (numero, enonce, corrige, themes, extra = {}) => ({
  numero, enonce_markdown: enonce, corrige_markdown: corrige, themes,
  difficulte_estimee: "faible", type_reponse: "ouverte", choix: [], reponse_correcte: "", ...extra,
});
const mcq = (numero, enonce, options, bonne, corrige, themes) => q(numero, enonce, corrige, themes, {
  type_reponse: "qcm", reponse_correcte: bonne,
  choix: options.map((t, i) => ({ lettre: "abcd"[i], texte: t })),
});
const ecrire = (nom, data) => fs.writeFileSync(nom, JSON.stringify(data, null, 2) + "\n");

// ---- Mathematics 0570, Paper 1 (50 QCM, 1h30) : les 6 premieres questions
ecrire("gce_ol_maths_2019_p1_ex1.json", base({
  matiere: "Mathematics", epreuve_source: "GCE_OL_MATHS_2019_P1.pdf", numero_exercice: "1",
  numero_paper: 1, code_matiere: "0570", duree_epreuve: "1h30",
  introduction_markdown: "Multiple choice paper. Answer ALL 50 questions; all questions carry equal marks. Each question has four suggested answers A, B, C and D. Calculators are allowed.",
  enonce_intro_markdown: "**Multiple choice questions** - choose the one correct answer, A, B, C or D.",
  groupes: [], points: "", figures: [],
  incertitudes: ["Pilote : seules les questions 1 à 6 (sans figure) sont transcrites."],
  questions: [
    mcq("1", "When $\\frac{1}{2}$ of $6-\\left(\\frac{3}{2}\\times 4\\right)$ is evaluated, the result is", ["3", "6", "0", "-3"], "c",
      "Work from the inside out. $\\frac{3}{2}\\times 4 = 6$, so $6-6=0$. Half of $0$ is $0$. **Answer: C.**", ["order of operations", "fractions"]),
    mcq("2", "The value of the digit 8 in $24.86$ is", ["$8$", "$\\frac{8}{10}$", "$\\frac{8}{100}$", "$\\frac{9}{10}$"], "b",
      "The digit 8 is the first digit after the decimal point, so it stands for tenths: $\\frac{8}{10}$. **Answer: B.**", ["place value", "decimals"]),
    mcq("3", "Given $-5 < 2$, the symbol \"<\" means", ["Greater than", "Greater than or equal to", "Less than", "Less than or equal to"], "c",
      "The symbol $<$ reads \"is less than\": $-5$ is less than $2$. **Answer: C.**", ["inequalities"]),
    mcq("4", "Simplifying $\\frac{2}{7}+\\frac{2}{5}$ gives", ["$\\frac{4}{35}$", "$\\frac{12}{35}$", "$\\frac{4}{12}$", "$\\frac{24}{35}$"], "d",
      "Use the common denominator $35$: $\\frac{2}{7}=\\frac{10}{35}$ and $\\frac{2}{5}=\\frac{14}{35}$, so the sum is $\\frac{24}{35}$. Do not add numerators and denominators separately (that gives $\\frac{4}{12}$). **Answer: D.**", ["fractions", "addition of fractions"]),
    mcq("5", "The number $163.35\\times 10^{-3}$ expressed in standard form is", ["$1.6335\\times 10^{-1}$", "$16335\\times 10^{-2}$", "$1.6335\\times 10^{1}$", "$16.335\\times 10^{-2}$"], "a",
      "Standard form needs one non-zero digit before the point. $163.35 = 1.6335\\times 10^{2}$, so $163.35\\times 10^{-3}=1.6335\\times 10^{2-3}=1.6335\\times 10^{-1}$. **Answer: A.**", ["standard form", "indices"]),
    mcq("6", "Expressing $204{,}865$ to three significant figures gives", ["$205{,}000$", "$204{,}800$", "$204{,}900$", "$200{,}900$"], "a",
      "The first three significant figures are $2,0,4$. The next digit is $8$ (at least 5), so round up: $205$, then fill with zeros to keep the size: $205{,}000$. **Answer: A.**", ["significant figures", "rounding"]),
  ],
}));

// ---- Mathematics 0570, Paper 2 (2h30) : Section A, questions 1 a 3
const p2 = (n, points, intro, qs) => base({
  matiere: "Mathematics", epreuve_source: "GCE_OL_MATHS_2019_P2.pdf", numero_exercice: n,
  numero_paper: 2, code_matiere: "0570", duree_epreuve: "2h30",
  introduction_markdown: "This paper has two sections, A and B. Answer ALL questions in Sections A and B. Section A: answer all 15 questions in the spaces provided; the mark allocation for each question is indicated. Section B: answer all four questions; each carries 15 marks. Show all steps in your working. Calculators are allowed.",
  enonce_intro_markdown: intro, groupes: ["SECTION A"], points, figures: [], questions: qs,
  incertitudes: ["Pilote : seules les questions 1 à 3 de la Section A sont transcrites."],
});
ecrire("gce_ol_maths_2019_p2_a1.json", p2("1", "4", "", [
  q("1", "Evaluate $15 - 12 \\div 4 \\times 16 + 2$. *[4 marks]*",
    "Apply the order of operations: division and multiplication from left to right, then addition and subtraction.\n\n$12\\div 4 = 3$, then $3\\times 16 = 48$.\n\n$15 - 48 + 2 = -31$.\n\n**Answer: $-31$.**", ["order of operations", "BODMAS"]),
]));
ecrire("gce_ol_maths_2019_p2_a2.json", p2("2", "6", "A household consumed 300 units of electricity where the first 220 units are billed at 50 FCFA per unit and the rest at 79 FCFA per unit.", [
  q("a", "Find the number of units to be paid at 79 FCFA.", "Units billed at 79 FCFA: $300 - 220 = 80$ units.", ["bills", "arithmetic problems"]),
  q("b", "Calculate the total amount paid by this household, in FCFA. *[6 marks for the whole question]*",
    "First 220 units: $220\\times 50 = 11\\,000$ FCFA.\n\nRemaining 80 units: $80\\times 79 = 6\\,320$ FCFA.\n\nTotal: $11\\,000 + 6\\,320 = 17\\,320$ FCFA.", ["bills", "arithmetic problems"]),
]));
ecrire("gce_ol_maths_2019_p2_a3.json", p2("3", "7", "Two cows and two goats cost 560,000 FCFA and one cow and three goats cost 400,000 FCFA.", [
  q("a", "Write two equations in two variables to represent the above statement.",
    "Let $c$ be the cost of a cow and $g$ the cost of a goat, in FCFA.\n\n$2c + 2g = 560\\,000$ and $c + 3g = 400\\,000$.", ["simultaneous equations", "forming equations"]),
  q("b", "Find the cost of each.",
    "Divide the first equation by 2: $c + g = 280\\,000$.\n\nSubtract it from $c + 3g = 400\\,000$: $2g = 120\\,000$, so $g = 60\\,000$.\n\nThen $c = 280\\,000 - 60\\,000 = 220\\,000$.\n\nA cow costs **220,000 FCFA** and a goat **60,000 FCFA**.", ["simultaneous equations"]),
  q("c", "Find the total cost of a goat and a cow. *[7 marks for the whole question]*",
    "$220\\,000 + 60\\,000 = 280\\,000$ FCFA (this is also $c+g$ found above).", ["simultaneous equations"]),
]));

// ---- Chemistry 0515, Paper 2 : Section A, question 1 + regles de choix
ecrire("gce_ol_chimie_2019_p2_a1.json", base({
  matiere: "Chemistry", epreuve_source: "GCE_OL_CHIMIE_2019_P2.pdf", numero_exercice: "A1",
  numero_paper: 2, code_matiere: "0515", duree_epreuve: "2h30",
  introduction_markdown: "This paper is arranged in three sections, A, B and C. Section A: answer 4 questions out of 5. Section B: answer 2 questions out of 3. Section C: answer both questions. Show all steps in calculations. Calculators are allowed.\n\n**Useful data:** relative atomic masses H = 1.0, C = 12.0, O = 16.0, Cu = 64.0; 1 faraday = 96000 coulombs; molar volume of a gas at r.t.p. = 24000 cm$^3$; specific heat capacity of water = 4.2 J g$^{-1}$ $^\\circ$C$^{-1}$; Avogadro number = $6.02\\times10^{23}$; $0^\\circ$C = 273 K.",
  regles_choix: [
    { type: "parmi", portee: "SECTION A", repondre: 4, sur: 5 },
    { type: "parmi", portee: "SECTION B", repondre: 2, sur: 3 },
    { type: "parmi", portee: "SECTION C", repondre: 2, sur: 2 },
  ],
  enonce_intro_markdown: "This question concerns the first four elements in Group I of the periodic table.\n\n| Element | Lithium (Li) | Sodium (Na) | Potassium (K) | Rubidium (Rb) |\n|---|---|---|---|---|\n| Atomic number | 3 | 11 | 19 | 37 |",
  groupes: ["SECTION A"], points: "10", figures: [],
  incertitudes: [
    "Le sujet se contredit : l'en-tête demande 4 questions sur 5 en Section A, mais le titre de la section dit « Answer ALL questions in this section ». La règle de l'en-tête est retenue.",
    "Points imprimés 3 + 3 + 3 + 3 = 12, pour « Total = 10 marks » : recopiés tels quels.",
    "Pilote : seule la question 1 de la Section A est transcrite.",
  ],
  questions: [
    q("a", "(i) Why are they classified as Group I elements?\n\n(ii) Which element is the least reactive?\n\n(iii) Write the electronic configuration of potassium (K). *[3 marks]*",
      "(i) Each has **one electron in its outer shell**, so they sit in the same group.\n\n(ii) **Lithium** - reactivity increases down the group as the outer electron is lost more easily.\n\n(iii) Potassium has 19 electrons: **2, 8, 8, 1**.", ["Group I elements", "electronic configuration"], { points: 3 }),
    q("b", "(i) These elements are usually stored under paraffin. Explain.\n\n(ii) Write an equation for the reaction between sodium and water. *[3 marks]*",
      "(i) They are very reactive and react quickly with oxygen and moisture in the air; paraffin keeps air and water away.\n\n(ii) $2\\mathrm{Na} + 2\\mathrm{H_2O} \\rightarrow 2\\mathrm{NaOH} + \\mathrm{H_2}$", ["Group I elements", "reactivity", "chemical equations"], { points: 3 }),
    q("c", "Lithium, though in Group I, resembles magnesium in Group II in its chemical properties.\n\n(i) What name is given to this resemblance?\n\n(ii) State the products formed when the carbonates of Li and Na are strongly heated: $\\mathrm{Li_2CO_3}$ and $\\mathrm{Na_2CO_3}$. *[3 marks]*",
      "(i) A **diagonal relationship**.\n\n(ii) $\\mathrm{Li_2CO_3}$ decomposes: $\\mathrm{Li_2CO_3} \\rightarrow \\mathrm{Li_2O} + \\mathrm{CO_2}$. $\\mathrm{Na_2CO_3}$ does **not** decompose at Bunsen temperatures: no products.", ["diagonal relationship", "thermal decomposition"], { points: 3 }),
    q("d", "State the type of compound formed when Group I elements combine with non-metals. *[3 marks]*",
      "**Ionic compounds**: the metal atom loses its outer electron to form a positive ion, which bonds electrostatically with the negative ion of the non-metal.", ["ionic bonding"], { points: 3 }),
  ],
}));

// ---- Physics 0580, Paper 2 : Section II, question 7 (EITHER a-c OR d-f)
ecrire("gce_ol_physique_2019_p2_ii7.json", base({
  matiere: "Physics", epreuve_source: "GCE_OL_PHYSIQUE_2019_P2.pdf", numero_exercice: "7",
  numero_paper: 2, code_matiere: "0580", duree_epreuve: "2h30",
  introduction_markdown: "Answer ALL questions. Section I is designed to be answered in 1 hour and Section II in 1 hour 30 minutes; divide your time accordingly. In Section II, answer EITHER parts a, b and c OR parts d, e and f of each question. The approximate mark for each part is indicated in brackets. Where necessary, assume $g = 10\\,\\mathrm{m\\,s^{-2}}$, $c = 3\\times10^{8}\\,\\mathrm{m\\,s^{-1}}$ and $e = 1.6\\times10^{-19}\\,\\mathrm{C}$. Calculators are allowed.",
  regles_choix: [{ type: "ou", portee: "SECTION II", options: [["a", "b", "c"], ["d", "e", "f"]] }],
  enonce_intro_markdown: "**Answer EITHER 7 a, b and c OR 7 d, e and f.**",
  groupes: ["SECTION II"], points: "20", figures: [],
  incertitudes: ["Pilote : seule la question 7 de la Section II est transcrite ; les figures des parties (c)(ii) et (f)(ii) sont à produire."],
  questions: [
    q("a", "(i) Define density and state its unit. *[2 marks]*\n\n(ii) Describe an experiment to determine the density of a piece of stone (irregularly shaped object). Include in your description: a list of apparatus needed, a diagram of the set-up, the procedure you will use to collect data, how the data is used to obtain the density of the stone, and any precaution taken to minimize error. *[6 marks]*",
      "(i) Density is the **mass per unit volume** of a substance, $\\rho = \\dfrac{m}{V}$. Unit: $\\mathrm{kg\\,m^{-3}}$ (or $\\mathrm{g\\,cm^{-3}}$).\n\n(ii) **Apparatus:** electronic balance, measuring cylinder, water, thread.\n\n**Set-up:** a measuring cylinder holding water, the stone hanging from a thread, to be lowered in.\n\n**Procedure:** 1. Measure the mass $m$ of the stone on the balance. 2. Pour water in the cylinder and read the volume $V_1$. 3. Tie the stone to the thread, lower it fully into the water without splashing and read the new volume $V_2$.\n\n**Calculation:** volume of the stone $V = V_2 - V_1$; density $\\rho = \\dfrac{m}{V_2 - V_1}$.\n\n**Precautions:** read the meniscus at eye level; make sure no air bubbles cling to the stone; use enough water to cover it completely; repeat and average.",
      ["density", "measuring volume by displacement", "experiment description"], { points: 8, difficulte_estimee: "moyenne" }),
    q("b", "(i) Define pressure. *[1 mark]*\n\nA rectangular block $0.01\\,\\mathrm{m}$ by $0.02\\,\\mathrm{m}$ by $0.04\\,\\mathrm{m}$ has a mass of $0.064\\,\\mathrm{kg}$. Calculate:\n\n(ii) the area of the largest face of the block; (iii) the weight of the block; (iv) the pressure the block will exert on a surface when lying on its largest face. *[2 + 2 + 2 marks]*",
      "(i) Pressure is the **force acting normally per unit area**: $P = \\dfrac{F}{A}$.\n\n(ii) Largest face: $0.02\\times 0.04 = 8\\times10^{-4}\\,\\mathrm{m^2}$.\n\n(iii) Weight $= mg = 0.064\\times 10 = 0.64\\,\\mathrm{N}$.\n\n(iv) $P = \\dfrac{0.64}{8\\times10^{-4}} = 800\\,\\mathrm{Pa}$.", ["pressure", "weight", "area"], { points: 7 }),
    q("c", "(i) Define elastic limit. *[2 marks]*\n\n(ii) A copper wire is stretched by a force which is gradually increased in magnitude until the wire breaks. Sketch a force-extension graph for the wire. On your graph indicate the elastic limit. *[3 marks]*",
      "(i) The elastic limit is the **maximum force (or extension) up to which a material returns to its original length when the force is removed**.\n\n(ii) The graph is a straight line through the origin (extension proportional to force) up to the elastic limit, then it curves towards the extension axis until the wire breaks. Mark the elastic limit where the line stops being straight. *(Figure to be produced.)*", ["elastic limit", "Hooke's law", "force-extension graph"], { points: 5 }),
    q("d", "(i) Define a longitudinal wave and give an example. *[2 marks]*\n\n(ii) Describe an experiment to determine the speed of sound in air. Include: a list of apparatus needed, a diagram of the set-up, the procedure you will use to collect data, how the data is used to obtain the speed of sound, and any precaution taken to minimize error. *[6 marks]*",
      "(i) A longitudinal wave is one in which the particles of the medium **vibrate parallel to the direction in which the wave travels**. Example: sound.\n\n(ii) **Echo method.** Apparatus: a tape measure or trundle wheel, a stopwatch, a large flat wall, a hand clapper or a starting gun.\n\n**Procedure:** stand a measured distance $d$ from the wall; clap and start the stopwatch, stop it when the echo returns; repeat several times and take the mean time $t$.\n\n**Calculation:** the sound travels $2d$ in time $t$, so $v = \\dfrac{2d}{t}$.\n\n**Precautions:** stand far enough (at least 50 m) so the echo is distinct; repeat and average; time from the clap, not from the movement of the hands.",
      ["longitudinal waves", "speed of sound", "experiment description"], { points: 8, difficulte_estimee: "moyenne" }),
    q("e", "(i) Define wavelength. *[1 mark]*\n\nPlane waves generated on the surface of a ripple tank are found to travel $0.74\\,\\mathrm{m}$ in $1.6\\,\\mathrm{s}$. The distance between a crest and an adjacent trough is $0.06\\,\\mathrm{m}$. Calculate: (ii) the average speed of the wave; (iii) the wavelength of the wave; (iv) the frequency of the wave. *[2 + 2 + 2 marks]*",
      "(i) Wavelength is the **distance between two successive crests (or troughs)**, that is, one complete wave.\n\n(ii) $v = \\dfrac{0.74}{1.6} = 0.4625 \\approx 0.46\\,\\mathrm{m\\,s^{-1}}$.\n\n(iii) A crest and the adjacent trough are **half** a wavelength apart: $\\lambda = 2\\times 0.06 = 0.12\\,\\mathrm{m}$.\n\n(iv) $f = \\dfrac{v}{\\lambda} = \\dfrac{0.4625}{0.12} \\approx 3.9\\,\\mathrm{Hz}$.", ["wavelength", "wave speed", "frequency", "wave equation"], { points: 7 }),
    q("f", "(i) Define the principal focus of a converging lens. *[2 marks]*\n\n(ii) Draw a ray diagram to show how a converging lens is used as a magnifying glass. *[3 marks]*",
      "(i) The principal focus is the **point on the principal axis to which rays travelling parallel to the axis converge after refraction** through the lens.\n\n(ii) Place the object **between the lens and its principal focus**. Draw one ray from the top of the object parallel to the axis, refracted through the focus on the far side; draw a second ray through the optical centre, undeviated. The refracted rays diverge, so trace them back: they meet behind the object, giving a **virtual, upright, magnified image**. *(Figure to be produced.)*", ["converging lens", "principal focus", "magnifying glass", "ray diagram"], { points: 5 }),
  ],
}));
