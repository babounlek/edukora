\
# -*- coding: utf-8 -*-
import json, re, os

OUT_DIR = "/sessions/brave-ecstatic-ritchie/mnt/Epreuves/json/cm/bac-c-d-anglais-2012-cameroun"
EPREUVE = "bac-c-d-anglais-2012-cameroun"

# ---------------------------------------------------------------------------
# EXERCICE 3 : SECTION C - COMPREHENSION
# ---------------------------------------------------------------------------

passage = (
    "**SECTION C: COMPREHENSION – 10 MARKS**\n\n"
    "Read the following passage carefully and answer the questions that follow. "
    "Use complete sentences and, as far as possible, your own words.\n\n"
    "Carnegie claims “the parent who leaves his son enormous wealth generally deadens "
    "the talents and energies of the son and tempts him to lead a less successful and "
    "less worthy life than he otherwise would”.\n\n"
    "Wealth thus leaves parents in what economists call the Samaritan’s dilemma. They "
    "want to make things better for their children’s lives in the short term; they "
    "underline their ability to look after themselves in the long run.\n\n"
    "In inheritance discourages work and decreases incomes, it is not surprising. Most "
    "people have the fear of poverty to force them out of bed on rainy mornings, to "
    "drive them to make urgent phone calls. But those who have inherited money and "
    "even those who know it is eventually coming their way, have to make do with that "
    "extra intensive and do not find the necessary drive within themselves. This is "
    "particularly hard for people in their twenties, a difficult stage in everybody’s "
    "life, when most people don’t really know what they want to do. And those who "
    "fail to establish themselves in a profession at this time may find it much harder "
    "to do so later in life. The problem does not lie just in the disasters of the "
    "drunks and the drug-addicts whose stories reach the gossip column. It is also "
    "that the idle rich can seem slightly lost.\n\n"
    "Earning money can be a source of self-esteem. A householder can say, observing "
    "his posh car, his beautiful home and his well-educated children: “I did that”. "
    "Does earned money bring more satisfaction than inherited cash? It is a fair bot "
    "that it does. And fi is through work, unpleasant and boring though it may be at "
    "times, that people find out what they are good at, their skills and identifies. "
    "Money may be the force that drives people to work; but once their careers are up "
    "and running, they tend to gain much more from the job than just cash.\n\n"
    "Furthermore, those who already have a large amount of money are deprived of the "
    "opportunity to aspire to it. The rich end up losing hope. The poor have the hope "
    "of becoming wealthy and then they will be happy. The rich have nothing left to "
    "hope for. There’s no drive.\n\n"
    "Inheritance can improve as well as damage relationships, perhaps because money "
    "can help the sharp edges of life. More money can buy more beautiful, more "
    "comfortable or better tasting things and therefore makes life more pleasant. "
    "That may explain why divorce rate is lower amongst the rich than the poor. Love "
    "is not enough. Some people who are obsessed with money and who try to get close "
    "to people with money invariably become disappointed later when they find out "
    "that money, after all, can do relatively little for one’s sense of happiness and "
    "contentment. Others don’t want to be seen as gold-diggers and find it a "
    "responsibility not to marry somebody with monkey.\n\n"
    "Though several people’s lives have been ruined by inheritance, many have been "
    "improved by it. The best off are those who have inherited money but stuck it "
    "out in the employment of others.\n\n"
    "*From the Economic Intelligent – Life, Autumn 2007*\n\n"
    "**Questions:**"
)

rappel_comprehension = (
    "En compréhension écrite, la réponse attendue n'est jamais une phrase recopiée telle "
    "quelle dans le texte : il faut d'abord repérer, dans le passage, l'endroit précis qui "
    "contient l'information demandée, puis reformuler cette information dans une phrase "
    "complète et autonome, qui a du sens même sans avoir le texte sous les yeux. Quand la "
    "question réclame un nombre précis d'éléments (« two disadvantages », « two reasons »...), "
    "il faut impérativement fournir ce nombre exact, ni plus ni moins, en s'appuyant sur des "
    "passages distincts du texte."
)

def rappel_block(text):
    return "### Rappel de méthode\n" + text

q1_corrige = rappel_block(rappel_comprehension) + "\n\n" + (
    "### Corrigé\n"
    "Le texte donne plusieurs inconvénients de l'héritage d'une fortune ; deux d'entre eux "
    "ressortent clairement du passage.\n\n"
    "Premièrement, l'héritage peut détruire les qualités personnelles de celui qui en "
    "bénéficie : selon la citation de Carnegie en ouverture du texte, « the parent who "
    "leaves his son enormous wealth generally deadens the talents and energies of the son "
    "and tempts him to lead a less successful and less worthy life than he otherwise would » "
    "- autrement dit, laisser une fortune énorme à son fils endort ses talents et son énergie, "
    "et le pousse vers une vie moins réussie et moins digne que celle qu'il aurait pu avoir.\n\n"
    "Deuxièmement, hériter d'argent, ou même savoir qu'on va en hériter, prive la personne de "
    "la motivation nécessaire pour travailler : le texte précise que ceux qui ont hérité "
    "d'argent « do not find the necessary drive within themselves », contrairement à la "
    "majorité des gens que la peur de la pauvreté pousse à sortir du lit et à chercher "
    "activement du travail.\n\n"
    "**Deux inconvénients de l'héritage : il peut détruire les talents et l'énergie de celui "
    "qui en bénéficie, et il prive la personne de la motivation (le « drive ») nécessaire pour "
    "travailler et réussir par elle-même.**\n\n"
    "### Piège à éviter\n"
    "Ne recopie jamais la phrase du texte mot pour mot comme réponse complète : la consigne "
    "demande explicitement d'utiliser tes propres mots autant que possible, et une simple "
    "citation sans reformulation est généralement pénalisée par le barème.\n\n"
    "### Conseil\n"
    "Quand la question demande « two » éléments, repère-les dans deux paragraphes différents "
    "du texte plutôt que dans la même phrase : c'est presque toujours ainsi que l'auteur "
    "répartit les idées, et cela t'évite de fournir deux fois la même idée reformulée "
    "différemment."
)

q2_corrige = rappel_block(rappel_comprehension) + "\n\n" + (
    "### Corrigé\n"
    "Le texte évoque explicitement les raisons qui poussent les gens à travailler.\n\n"
    "La première raison est la peur de la pauvreté : le texte affirme que « most people have "
    "the fear of poverty to force them out of bed on rainy mornings, to drive them to make "
    "urgent phone calls » - c'est cette crainte de manquer d'argent qui pousse la plupart des "
    "gens à se lever et à agir, même les jours où ils n'en ont pas envie.\n\n"
    "La seconde raison est la recherche de l'estime de soi : le texte indique que « earning "
    "money can be a source of self-esteem », et illustre cette idée par l'exemple du "
    "propriétaire qui peut dire, en observant sa belle voiture, sa maison et ses enfants bien "
    "éduqués : « I did that » - gagner son propre argent procure une fierté personnelle que "
    "l'argent hérité ne procure pas.\n\n"
    "**Deux raisons pour lesquelles les gens travaillent : la peur de la pauvreté, qui pousse "
    "à agir par nécessité, et le besoin de retirer de la fierté et de l'estime de soi de ce "
    "que l'on accomplit par son propre travail.**\n\n"
    "### Conseil\n"
    "Pour ce type de question, cherche d'abord les phrases du texte qui contiennent un verbe "
    "de motivation ou de sentiment (« fear », « drive », « self-esteem »...) : elles signalent "
    "presque toujours le passage qui répond à une question sur les raisons ou les causes."
)

q3_corrige = rappel_block(rappel_comprehension) + "\n\n" + (
    "### Corrigé\n"
    "Le texte précise ce que le travail permet de gagner, au-delà du simple salaire.\n\n"
    "D'une part, le travail permet de découvrir ses propres compétences : le texte affirme "
    "que c'est « through work... that people find out what they are good at, their skills and "
    "identifies » (leurs compétences et leur identité) - en travaillant, une personne apprend "
    "ce dans quoi elle excelle réellement.\n\n"
    "D'autre part, une fois la carrière lancée, les travailleurs retirent de leur emploi bien "
    "plus que de l'argent : le texte précise que « once their careers are up and running, "
    "they tend to gain much more from the job than just cash » - cela inclut la satisfaction "
    "personnelle et le sentiment d'accomplissement évoqués plus haut dans le texte à propos "
    "de l'estime de soi.\n\n"
    "**Deux choses que l'on peut gagner en travaillant : la connaissance de ses propres "
    "compétences et talents, et une satisfaction personnelle qui va bien au-delà du salaire "
    "perçu.**\n\n"
    "### Piège à éviter\n"
    "Ne réponds pas uniquement « de l'argent » : le texte insiste précisément sur le fait que "
    "le travail apporte « much more from the job than just cash » - l'argent n'est pas la "
    "réponse attendue ici, puisque la question porte sur ce qui vient s'ajouter au salaire."
)

q4_corrige = rappel_block(rappel_comprehension) + "\n\n" + (
    "### Corrigé\n"
    "Le texte propose une solution concrète pour qu'un enfant riche ne soit pas détruit par "
    "son héritage : elle se trouve dans la toute dernière phrase du passage, qui joue le rôle "
    "de conclusion. Le texte affirme que « the best off are those who have inherited money "
    "but stuck it out in the employment of others » : autrement dit, ceux qui s'en sortent le "
    "mieux sont ceux qui, malgré leur héritage, ont quand même choisi de continuer à "
    "travailler pour quelqu'un d'autre plutôt que de vivre uniquement de leur fortune.\n\n"
    "**Pour que son héritage ne le détruise pas, un enfant riche doit continuer à travailler, "
    "par exemple au service d'un employeur, plutôt que de vivre dans l'oisiveté grâce à "
    "l'argent hérité.**\n\n"
    "### Conseil\n"
    "Quand une question porte sur une solution ou une recommandation, pense d'abord à "
    "regarder la conclusion du texte : c'est souvent là, plutôt qu'au milieu du "
    "développement, que l'auteur formule sa réponse la plus synthétique au problème qu'il a "
    "posé."
)

q5_corrige = rappel_block(rappel_comprehension) + "\n\n" + (
    "### Corrigé\n"
    "Le texte ne présente pas le travail comme une activité toujours agréable. Il précise "
    "explicitement que c'est « through work, unpleasant and boring though it may be at "
    "times » que les gens découvrent leurs compétences : cette formulation reconnaît noir sur "
    "blanc que le travail peut être, par moments, désagréable et ennuyeux.\n\n"
    "La réponse est donc négative : non, nous n'apprécions pas toujours notre travail. Le "
    "texte justifie malgré tout l'intérêt de continuer à travailler même dans ces moments-là, "
    "puisque c'est justement à travers ces périodes peu plaisantes que l'on apprend à se "
    "connaître et que l'on développe des compétences utiles pour la suite.\n\n"
    "**Non, nous n'apprécions pas toujours notre travail : le texte reconnaît lui-même qu'il "
    "peut être « unpleasant and boring » par moments, mais souligne que c'est précisément à "
    "travers ces moments difficiles que l'on découvre ses véritables compétences.**\n\n"
    "### Conseil\n"
    "Pour une question de type « Justify your answer », ta réponse doit toujours comporter "
    "deux parties clairement identifiables : d'abord la réponse elle-même (oui/non, ou une "
    "position claire), puis au moins un élément du texte qui la justifie explicitement - une "
    "réponse sans justification textuelle perd la moitié des points, même si elle est "
    "correcte sur le fond."
)

def make_rappel(idx_suffix, numero, corrige_text, cours_id):
    return [{
        "id": f"rdm-{EPREUVE}-ex3-q{numero}-0",
        "competence": "Compréhension écrite : repérer et reformuler l'information (reading comprehension)",
        "contenu_markdown": rappel_comprehension,
        "cours_genere": True,
        "cours_id": cours_id
    }]

ex3_questions = [
    {
        "numero": "1",
        "enonce_markdown": "1) Give two disadvantages of inheriting wealth.",
        "corrige_markdown": q1_corrige,
        "themes": ["reading comprehension", "text-based inference", "inheritance"],
        "difficulte_estimee": "moyenne",
        "type_reponse": "ouverte",
        "choix": [],
        "reponse_correcte": "",
        "rappels_de_methode": make_rappel("1", "1", q1_corrige, "cours_comprehension-ecrite-reperer-et-reformuler-linformation")
    },
    {
        "numero": "2",
        "enonce_markdown": "2) Give two reasons why people go out to work.",
        "corrige_markdown": q2_corrige,
        "themes": ["reading comprehension", "text-based inference", "motivation to work"],
        "difficulte_estimee": "moyenne",
        "type_reponse": "ouverte",
        "choix": [],
        "reponse_correcte": "",
        "rappels_de_methode": make_rappel("2", "2", q2_corrige, "cours_comprehension-ecrite-reperer-et-reformuler-linformation-2")
    },
    {
        "numero": "3",
        "enonce_markdown": "3) What two things can we gain from working?",
        "corrige_markdown": q3_corrige,
        "themes": ["reading comprehension", "text-based inference", "benefits of work"],
        "difficulte_estimee": "moyenne",
        "type_reponse": "ouverte",
        "choix": [],
        "reponse_correcte": "",
        "rappels_de_methode": make_rappel("3", "3", q3_corrige, "cours_comprehension-ecrite-reperer-et-reformuler-linformation-3")
    },
    {
        "numero": "4",
        "enonce_markdown": "4) What can a wealthy child do with his inheritance so that it does not destroy him?",
        "corrige_markdown": q4_corrige,
        "themes": ["reading comprehension", "text-based inference", "conclusion of a passage"],
        "difficulte_estimee": "faible",
        "type_reponse": "ouverte",
        "choix": [],
        "reponse_correcte": "",
        "rappels_de_methode": make_rappel("4", "4", q4_corrige, "cours_comprehension-ecrite-reperer-et-reformuler-linformation-4")
    },
    {
        "numero": "5",
        "enonce_markdown": "5) Do we always enjoy work? Justify your answer.",
        "corrige_markdown": q5_corrige,
        "themes": ["reading comprehension", "justified opinion", "text-based inference"],
        "difficulte_estimee": "moyenne",
        "type_reponse": "ouverte",
        "choix": [],
        "reponse_correcte": "",
        "rappels_de_methode": make_rappel("5", "5", q5_corrige, "cours_comprehension-ecrite-reperer-et-reformuler-linformation-5")
    },
]

ex3 = {
    "epreuve_source": f"{EPREUVE}.pdf",
    "numero_exercice": "3",
    "matiere": "Anglais",
    "serie": "C/D",
    "examen": "bac",
    "origine": "officiel",
    "etablissement": None,
    "annee": 2012,
    "duree_epreuve": None,
    "coefficient": None,
    "points": "10",
    "figures": [],
    "enonce_intro_markdown": passage,
    "questions": ex3_questions,
    "mots_cles_recherche": [
        "anglais", "reading comprehension", "inheritance", "wealth", "work motivation",
        "text-based questions", "BAC C D"
    ],
    "incertitudes": [
        "L'en-tete du sujet indique «BACCALAUREAT «C & D»» : l'epreuve s'adresse identiquement aux deux series C et D. Le champ serie a ete renseigne «C/D» faute de code combine dans le referentiel, par coherence avec les exercices 1 et 2 de la meme epreuve.",
        "Le passage source contient plusieurs coquilles typographiques manifestes, reproduites fidelement dans enonce_intro_markdown conformement a la regle de fidelite : « In inheritance discourages work » (tres probablement « If inheritance discourages work »), « that extra intensive » (tres probablement « that extra incentive »), « It is a fair bot that it does » (tres probablement « It is a fair bet that it does »), « And fi is through work » (tres probablement « And it is through work »), « their skills and identifies » (tres probablement « their skills and identities »), et « not to marry somebody with monkey » (tres probablement « not to marry somebody with money »). Ces coquilles sont interpretees selon leur sens le plus probable dans le corrige de chaque sous-question concernee.",
        "Les cinq sous-questions de l'Exercice 3 (questions 1 a 5, comprehension) partagent la meme competence transferable (reperer et reformuler l'information d'un texte) : un seul cours complet a ete genere (cours_comprehension-ecrite-reperer-et-reformuler-linformation), les quatre autres rappels de methode identiques renvoient au meme titre de cours via un squelette de rattachement (-2 a -5), suivant la meme convention que les exercices 1 et 2 de cette epreuve."
    ],
    "statut": "brouillon"
}

with open(os.path.join(OUT_DIR, f"{EPREUVE}_exercice_3.json"), "w", encoding="utf-8") as f:
    json.dump(ex3, f, ensure_ascii=False, indent=2)

print("exercice_3 written")

# verbatim check
for q in ex3_questions:
    for r in q["rappels_de_methode"]:
        assert r["contenu_markdown"] in q["corrige_markdown"], f"MISMATCH {q['numero']}"
print("ex3 verbatim OK")
