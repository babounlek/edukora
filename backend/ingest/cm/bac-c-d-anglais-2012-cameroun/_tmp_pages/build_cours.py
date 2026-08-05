\
# -*- coding: utf-8 -*-
import json, os

OUT_DIR = "/sessions/brave-ecstatic-ritchie/mnt/Epreuves/json/cm/bac-c-d-anglais-2012-cameroun"
EPREUVE = "bac-c-d-anglais-2012-cameroun"
EPREUVE_ID = "BAC-C-D-ANGLAIS-2012-CAMEROUN"
EPREUVE_TITRE = "Baccalaureat C & D - Anglais - Session 2012 (Cameroun)"

def base_meta(titre, sous_theme, duree, tags):
    return {
        "titre": titre,
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": sous_theme,
        "duree_estimee_min": duree,
        "tags": tags,
        "statut": "brouillon"
    }

def base_source(exercice_numero, rappel_id, rappels_lies=None):
    return {
        "epreuve_id": EPREUVE_ID,
        "epreuve_titre": EPREUVE_TITRE,
        "exercice_numero": exercice_numero,
        "rappel_id": rappel_id,
        "rappels_lies": rappels_lies or [],
        "correction_id": None
    }

def full_course(cours_id, titre, sous_theme, duree, tags, exercice_numero, rappel_id,
                 accroche, prerequis, regle_titre, regle_contenu, formule_principale,
                 exemple_enonce, etapes, exemple_conclusion,
                 erreurs, exercices, synthese, rappels_lies=None):
    sections = [
        {"type": "accroche", "contenu_markdown": accroche},
        {"type": "prerequis", "items": prerequis},
        {"type": "regle", "titre": regle_titre, "contenu_markdown": regle_contenu, **({"formule_principale": formule_principale} if formule_principale else {})},
        {"type": "exemple_resolu", "enonce_markdown": exemple_enonce, "epreuve_source": True,
         "etapes": etapes, "conclusion_markdown": exemple_conclusion},
        {"type": "erreurs_classiques", "items": erreurs},
        {"type": "exercices_application", "items": exercices},
        {"type": "synthese", "items_markdown": synthese},
    ]
    return {
        "cours_id": cours_id,
        "meta": base_meta(titre, sous_theme, duree, tags),
        "source": base_source(exercice_numero, rappel_id, rappels_lies),
        "sections": sections
    }

def skeleton_course(cours_id, titre, exercice_numero, rappel_id):
    return {
        "cours_id": cours_id,
        "meta": {
            "titre": titre,
            "matiere": "Anglais",
            "serie": None,
            "sous_theme": None,
            "duree_estimee_min": None,
            "tags": [],
            "statut": "brouillon"
        },
        "source": base_source(exercice_numero, rappel_id),
        "sections": []
    }

def etape(n, action, justification, resultat):
    return {"numero": n, "action": action, "justification": justification, "resultat_markdown": resultat}

def erreur(e, pourquoi, correction):
    return {"erreur_markdown": e, "pourquoi_faux": pourquoi, "correction_markdown": correction}

def exo(n, diff, enonce, solution):
    return {"numero": n, "difficulte": diff, "enonce_markdown": enonce, "solution_markdown": solution}

courses = []

# =====================================================================
# COURS 1 : Fonctions communicatives de base en anglais (FULL)
# =====================================================================
courses.append(("cours_fonctions-communicatives-de-base-en-anglais.json", full_course(
    cours_id="cours_fonctions-communicatives-de-base-en-anglais",
    titre="Fonctions communicatives de base en anglais (situational language)",
    sous_theme="Situational language / functions",
    duree=20,
    tags=["situational language", "functions", "dialogue completion", "politeness"],
    exercice_numero="1",
    rappel_id="rdm-bac-c-d-anglais-2012-cameroun-ex1-q1a-0",
    accroche=(
        "Au BAC, un exercice très fréquent te présente un dialogue à trous : deux personnages "
        "échangent quelques répliques, et il te manque une phrase pour que l'échange ait du "
        "sens. Ce n'est pas un exercice de grammaire pure - c'est un test de ta capacité à "
        "reconnaître, dans une situation sociale donnée (remercier, s'excuser, présenter "
        "quelqu'un, demander une information), l'expression toute faite qu'un anglophone "
        "utiliserait spontanément. Ce cours te donne les réflexes pour reconnaître ces "
        "situations et produire la bonne formule, sans jamais traduire mot à mot depuis le "
        "français."
    ),
    prerequis=[
        "Vocabulaire de base de la politesse en anglais (thank you, sorry, please...)",
        "Structure de la phrase interrogative simple (auxiliaire + sujet + verbe)",
        "Distinction entre les registres formel et informel en anglais",
    ],
    regle_titre="Identifier la fonction communicative avant de rédiger",
    regle_contenu=(
        "Une fonction communicative (ou « situational language ») est une expression figée "
        "associée à une situation sociale précise : remercier, s'excuser, saluer, présenter "
        "quelqu'un, demander une information, exprimer un besoin médical... Ces expressions ne "
        "se déduisent pas de la grammaire : elles se mémorisent comme des blocs de sens "
        "entiers, exactement comme le ferait un locuteur natif.\n\n"
        "La méthode se déroule toujours en deux temps :\n\n"
        "1. Identifier la situation à partir du contexte donné (qui parle ? à qui ? pourquoi ?) "
        "et surtout à partir de la réplique de réponse quand elle est fournie - elle révèle "
        "presque toujours la fonction attendue.\n"
        "2. Produire l'expression figée correspondant à cette fonction, jamais une traduction "
        "mot à mot d'une formule française.\n\n"
        "Quelques fonctions communicatives fréquentes au BAC et leurs formules associées :\n"
        "- Remercier : *Thank you (very much) for...*, *I am very grateful for...*\n"
        "- Répondre à un remerciement : *You're welcome*, *Not at all*, *My pleasure*\n"
        "- Présenter quelqu'un : *I'd like you to meet...*, *This is...* → réponse : "
        "*Nice/Pleased to meet you*\n"
        "- Demander une quantité dénombrable : *How many + nom pluriel...?*\n"
        "- Demander une quantité indénombrable : *How much + nom singulier...?*\n"
        "- S'enquérir d'un problème de santé : *What's the matter with you?*, *What's wrong?*"
    ),
    formule_principale=None,
    exemple_enonce=(
        "Complète cet échange avec la question manquante :\n\n"
        "Teacher: ... students are in class today?\n\nStudents: There are only five of us, sir."
    ),
    etapes=[
        etape(1, "Lire la réponse fournie",
              "La réponse donne toujours un indice décisif sur la fonction attendue dans l'espace vide.",
              "La réponse « There are only five of us, sir » donne un nombre précis d'élèves : la question porte donc sur une quantité."),
        etape(2, "Déterminer si le nom concerné est comptable ou indénombrable",
              "Le choix entre how many et how much dépend uniquement de cette distinction.",
              "« Students » est un nom comptable, qui a un pluriel visible (student → students)."),
        etape(3, "Choisir la structure interrogative correspondante",
              "Devant un nom comptable pluriel, la structure correcte est How many + nom pluriel + verbe.",
              "**How many students are in class today?**"),
    ],
    exemple_conclusion=(
        "L'échange complet est : « Teacher: How many students are in class today? Students: "
        "There are only five of us, sir. » - la question comptable (how many) correspond "
        "exactement à une réponse chiffrée sur un nom comptable."
    ),
    erreurs=[
        erreur("Utiliser how much devant un nom comptable pluriel, ex. *How much students are in class?*",
               "How much s'utilise uniquement devant un nom indénombrable (singulier par nature, comme water ou money) ; students a un pluriel visible et est donc comptable, ce qui impose how many.",
               "How many students are in class today?"),
        erreur("Traduire littéralement une formule de politesse française, ex. dire *I thank you for* au lieu de *Thank you for*",
               "En anglais courant, la formule figée est *Thank you for + nom/gérondif*, sans pronom sujet répété comme en français ; *I thank you* sonne artificiel et trop cérémonieux dans un dialogue courant.",
               "Thank you very much for the valuable assistance you gave me."),
        erreur("Répondre à une présentation par un simple *Hello* suivi du prénom, sans formule de plaisir de connaître",
               "Dans une présentation, un anglophone ajoute presque toujours *nice/pleased to meet you* ; un simple *Hello* seul est perçu comme incomplet, voire froid.",
               "Hello Sama, nice to meet you."),
    ],
    exercices=[
        exo(1, "facile",
            "Complète : A: 'I'm sorry I broke your pen.' B: '……………..'",
            "La réplique de A exprime des excuses (« I'm sorry »). La réponse attendue de B doit accepter ces excuses, avec une formule figée telle que « That's all right », « Never mind » ou « Don't worry about it ». Réponse : **B: That's all right, don't worry about it.**"),
        exo(2, "moyen",
            "Complète la question manquante : Waiter: '... sugar do you want in your tea?' Customer: 'Just a little, thank you.'",
            "La réponse « Just a little » indique une petite quantité d'un nom indénombrable : sugar n'a pas de pluriel dénombrable naturel dans ce sens. Il faut donc how much, pas how many. Réponse : **Waiter: How much sugar do you want in your tea?**"),
        exo(3, "approfondissement",
            "Reconstitue les deux répliques manquantes dans ce dialogue : A: 'I'd like you to introduce you to my colleague, Mr Eto'o.' B: '……………' A (later, leaving): 'Well, …………… for your time today.' B: 'You're welcome.'",
            "La première réplique manquante suit une présentation : elle appelle la formule figée de plaisir de connaître, « Nice to meet you, Mr Eto'o. » La seconde réplique manquante précède « You're welcome », qui ne répond qu'à un remerciement : elle appelle donc une formule de remerciement, « thank you very much for your time today. » Réponses : **B: Nice to meet you, Mr Eto'o.** puis **A: Well, thank you very much for your time today.**"),
    ],
    synthese=[
        "Une fonction communicative se reconnaît à la situation décrite, jamais à une simple traduction du français.",
        "La réponse fournie dans un dialogue à trous est presque toujours l'indice le plus fiable pour deviner la fonction attendue.",
        "How many s'utilise avec un nom comptable pluriel, how much avec un nom indénombrable : vérifie toujours si le nom a un pluriel visible.",
        "Une présentation appelle une réponse de plaisir de connaître (nice/pleased to meet you), jamais un simple salut isolé.",
        "Ce type de question tombe systématiquement en Section A (Grammar) du BAC anglais, sous forme de dialogue à trous à compléter avec tes propres mots.",
    ],
)))

# =====================================================================
# COURS 2 : Le troisieme conditionnel (FULL)
# =====================================================================
courses.append(("cours_le-troisieme-conditionnel.json", full_course(
    cours_id="cours_le-troisieme-conditionnel",
    titre="Le troisième conditionnel (third conditional)",
    sous_theme="Conditionnels",
    duree=25,
    tags=["third conditional", "past perfect", "grammar", "conditionals"],
    exercice_numero="1",
    rappel_id="rdm-bac-c-d-anglais-2012-cameroun-ex1-q2a-0",
    accroche=(
        "Beaucoup d'élèves confondent les trois conditionnels anglais et appliquent la "
        "mauvaise structure au mauvais contexte. Le troisième conditionnel a pourtant un "
        "usage bien précis : il sert à regretter ou à imaginer ce qui aurait pu se passer "
        "dans le passé si les choses avaient été différentes. Ce cours te montre comment le "
        "repérer à coup sûr, à partir du temps déjà présent dans la phrase, sans avoir "
        "besoin de deviner le sens exact."
    ),
    prerequis=[
        "Le prétérit simple (past simple)",
        "Le present perfect",
        "La formation du participe passé des verbes réguliers et irréguliers",
    ],
    regle_titre="Structure et emploi du troisième conditionnel",
    regle_contenu=(
        "Le troisième conditionnel exprime une condition irréelle dans le passé et sa "
        "conséquence imaginaire, également dans le passé : on l'utilise pour parler d'un "
        "événement qui ne s'est PAS produit, et de ce qui en aurait résulté s'il s'était "
        "produit.\n\n"
        "Sa structure est fixe :\n\n"
        "If + sujet + had + participe passé (past perfect), sujet + would have + participe "
        "passé\n\n"
        "Le repère le plus fiable pour identifier ce conditionnel n'est pas le mot *if* "
        "lui-même, mais le temps déjà écrit dans la partie non manquante de la phrase : si tu "
        "vois *would have + participe passé* dans la proposition principale, la subordonnée "
        "en *if* doit obligatoirement être au past perfect."
    ),
    formule_principale="If + had + participe passé, would have + participe passé",
    exemple_enonce=(
        "Complète : If these governments …. weapons of mass destruction, the Allied Forces "
        "wouldn't have invaded them. (hadn't developed / wouldn't develop / couldn't develop "
        "/ haven't developed)"
    ),
    etapes=[
        etape(1, "Repérer le temps déjà présent dans la proposition principale",
              "C'est ce temps qui impose la structure de toute la phrase.",
              "« the Allied Forces wouldn't have invaded them » est au conditionnel passé (would have + participe passé)."),
        etape(2, "En déduire le temps attendu dans la subordonnée en if",
              "Would have + participe passé dans la principale n'est compatible qu'avec if + past perfect dans la subordonnée (règle du troisième conditionnel).",
              "La subordonnée doit être au past perfect : had + participe passé."),
        etape(3, "Déterminer la forme affirmative ou négative",
              "Le sens de la phrase indique que ces gouvernements n'ont pas développé d'armes dans la réalité, on imagine donc l'inverse : la subordonnée doit être négative.",
              "hadn't developed (forme négative du past perfect)"),
    ],
    exemple_conclusion=(
        "If these governments hadn't developed weapons of mass destruction, the Allied Forces "
        "wouldn't have invaded them. - la phrase respecte bien la structure If + had + "
        "participe passé, would have + participe passé."
    ),
    erreurs=[
        erreur("Utiliser le deuxième conditionnel (would + base verbale) au lieu du troisième, ex. *If these governments wouldn't develop weapons...*",
               "Le deuxième conditionnel imagine une situation présente ou future irréelle, pas une situation passée révolue ; ici la principale est déjà au conditionnel passé (would have invaded), ce qui exige le past perfect, pas le conditionnel simple.",
               "If these governments hadn't developed weapons of mass destruction..."),
        erreur("Confondre past perfect et present perfect dans la subordonnée, ex. *If these governments haven't developed...*",
               "Le present perfect relie le passé au présent ; le troisième conditionnel parle d'un fait entièrement clos dans le passé, ce qui impose le past perfect (had + participe passé), pas le present perfect.",
               "If these governments hadn't developed weapons of mass destruction..."),
        erreur("Oublier d'accorder la forme négative entre la subordonnée et le sens voulu de la phrase",
               "Le sens de la phrase (les gouvernements n'ont réellement pas développé d'armes) impose une subordonnée négative ; une subordonnée affirmative inverserait complètement le sens de la condition irréelle.",
               "Vérifier toujours le sens réel des événements avant de choisir la forme affirmative ou négative de la subordonnée."),
    ],
    exercices=[
        exo(1, "facile",
            "Mets le verbe entre parenthèses au temps qui convient : If I (know) about the meeting, I would have come.",
            "La principale « I would have come » est au conditionnel passé (would have + participe passé), ce qui impose le past perfect dans la subordonnée. Le verbe know devient had known. Réponse : **If I had known about the meeting, I would have come.**"),
        exo(2, "moyen",
            "Transforme cette phrase en troisième conditionnel : She didn't study, so she failed the exam. (Reformule avec If...)",
            "Dans la réalité, elle n'a pas étudié (négatif) et a échoué (affirmatif). Pour le troisième conditionnel, on inverse chaque polarité : la subordonnée devient affirmative (had studied) et la principale devient négative (wouldn't have failed). Réponse : **If she had studied, she wouldn't have failed the exam.**"),
        exo(3, "approfondissement",
            "Combine ces deux phrases réelles en une seule phrase au troisième conditionnel, à la forme qui convient : Reality: The driver was speeding. The driver caused an accident.",
            "Dans la réalité, le conducteur roulait trop vite (affirmatif) et a causé un accident (affirmatif). Pour imaginer l'inverse au troisième conditionnel, les deux propositions doivent passer à la forme négative : la subordonnée devient hadn't been speeding, et la principale devient wouldn't have caused an accident. Réponse : **If the driver hadn't been speeding, he wouldn't have caused an accident.**"),
    ],
    synthese=[
        "Le troisième conditionnel parle d'un passé qui ne s'est pas produit ainsi : il sert à regretter ou à imaginer autrement ce qui est déjà arrivé.",
        "Repère toujours le temps déjà écrit dans la phrase avant de choisir ta réponse : would have + participe passé impose had + participe passé dans la subordonnée en if.",
        "Ne confonds jamais past perfect (troisième conditionnel) et present perfect : le present perfect n'a pas sa place dans ce type de phrase.",
        "Vérifie le sens réel des événements pour choisir entre forme affirmative et négative : le conditionnel inverse presque toujours ce qui s'est réellement passé.",
        "Ce point de grammaire est un classique du BAC anglais, souvent testé sous forme de QCM à choix multiple dans la section Grammar.",
    ],
)))

# =====================================================================
# COURS 3 : Les tag questions (FULL)
# =====================================================================
courses.append(("cours_les-tag-questions.json", full_course(
    cours_id="cours_les-tag-questions",
    titre="Les tag questions (question tags)",
    sous_theme="Structures interrogatives",
    duree=20,
    tags=["tag questions", "past simple", "grammar"],
    exercice_numero="1",
    rappel_id="rdm-bac-c-d-anglais-2012-cameroun-ex1-q2b-0",
    accroche=(
        "Une tag question est cette petite question ajoutée à la fin d'une phrase pour "
        "demander confirmation, l'équivalent du « n'est-ce pas ? » français. Elle semble "
        "simple, mais elle piège régulièrement les candidats qui se laissent influencer par "
        "le sens de la phrase plutôt que par sa construction grammaticale stricte. Ce cours "
        "te donne la méthode pour ne plus jamais te tromper."
    ),
    prerequis=[
        "Les auxiliaires anglais (be, have, do) et leurs formes conjuguées",
        "La formation de la forme négative contractée (isn't, didn't, hasn't...)",
        "Le prétérit simple et le present perfect",
    ],
    regle_titre="La règle d'opposition affirmatif/négatif",
    regle_contenu=(
        "Une tag question se construit toujours en deux temps : on reprend l'auxiliaire (ou "
        "une forme de do/does/did) du temps employé dans la phrase, puis on inverse la "
        "polarité de la phrase de base.\n\n"
        "Règle stricte : si la phrase de base est affirmative, le tag est négatif ; si la "
        "phrase de base est négative, le tag est affirmatif.\n\n"
        "Le piège principal ne porte pas sur la polarité mais sur l'auxiliaire à reprendre : "
        "il faut identifier le verbe conjugué principal de la phrase et son temps, puis "
        "reprendre l'auxiliaire correspondant à CE temps précis - jamais un autre auxiliaire, "
        "même s'il semble grammaticalement possible dans l'absolu."
    ),
    formule_principale="phrase affirmative, tag négatif ? / phrase négative, tag affirmatif ?",
    exemple_enonce="Complète : The convicted manager pleaded not guilty ………..he? (did / hadn't / didn't / hasn't)",
    etapes=[
        etape(1, "Isoler le verbe conjugué principal et son temps",
              "C'est ce verbe, pas le sens de la phrase, qui détermine l'auxiliaire du tag.",
              "Le verbe conjugué est *pleaded*, au prétérit simple (past simple)."),
        etape(2, "Déterminer si la phrase de base est grammaticalement affirmative ou négative",
              "Le tag doit avoir la polarité opposée à la phrase de base.",
              "Aucun auxiliaire négatif (didn't) ne précède *pleaded* : la phrase est grammaticalement affirmative, même si « not guilty » a un sens négatif."),
        etape(3, "Choisir l'auxiliaire du tag, à la forme contractée négative puisque la phrase est affirmative",
              "Le prétérit simple à la forme affirmative se reprend avec l'auxiliaire did ; la polarité opposée impose la forme négative didn't.",
              "**didn't**"),
    ],
    exemple_conclusion=(
        "The convicted manager pleaded not guilty, didn't he? - la phrase reste "
        "grammaticalement affirmative malgré son sens négatif, ce qui impose un tag négatif "
        "au prétérit : didn't."
    ),
    erreurs=[
        erreur("Se laisser influencer par le sens négatif de « not guilty » et choisir un tag affirmatif, ex. *did he?*",
               "La polarité d'une tag question dépend de la construction grammaticale de la phrase (présence ou non d'un auxiliaire négatif avant le verbe), pas du sens lexical des mots qui la composent.",
               "The convicted manager pleaded not guilty, didn't he?"),
        erreur("Reprendre un auxiliaire d'un autre temps, ex. *hasn't he?* ou *hadn't he?*",
               "Hasn't appartient au present perfect et hadn't au past perfect ; la phrase est au prétérit simple (pleaded), qui se reprend uniquement avec did/didn't.",
               "The convicted manager pleaded not guilty, didn't he?"),
        erreur("Oublier d'inverser le sujet par un pronom dans le tag, ex. écrire *didn't the manager?* au lieu de *didn't he?*",
               "Le tag reprend toujours le sujet sous forme de pronom, jamais le groupe nominal complet répété.",
               "didn't he?"),
    ],
    exercices=[
        exo(1, "facile",
            "Complète le tag : You are coming to the party, ………?",
            "Le verbe conjugué est are (present simple de be), à la forme affirmative. Le tag doit donc être négatif et reprendre le même auxiliaire be. Réponse : **You are coming to the party, aren't you?**"),
        exo(2, "moyen",
            "Complète le tag : She hasn't finished her homework, ………?",
            "La phrase est au present perfect (hasn't finished), à la forme négative. Le tag doit donc être affirmatif et reprendre le même auxiliaire has. Réponse : **She hasn't finished her homework, has she?**"),
        exo(3, "approfondissement",
            "Complète le tag, en faisant attention au sujet particulier : I am late, ………?",
            "Le verbe conjugué est am (present simple de be, première personne du singulier), à la forme affirmative : le tag doit donc être négatif. Le cas de 'I am' est irrégulier en anglais : on n'utilise jamais *amn't I?*, mais la forme figée *aren't I?*. Réponse : **I am late, aren't I?**"),
    ],
    synthese=[
        "La polarité du tag dépend de la grammaire de la phrase (présence d'un auxiliaire négatif), jamais du sens des mots.",
        "Le tag reprend toujours l'auxiliaire du même temps que le verbe conjugué principal, jamais un autre temps.",
        "Le tag utilise toujours un pronom sujet, jamais le groupe nominal complet.",
        "Le cas de 'I am' est irrégulier : le tag correct est 'aren't I?', pas 'amn't I?'.",
        "Les tag questions sont un classique récurrent du BAC anglais, testées aussi bien en Grammar qu'à l'oral en dialogue.",
    ],
)))

# =====================================================================
# COURS 4 : Les verbes a preposition fixe (FULL)
# =====================================================================
courses.append(("cours_les-verbes-a-preposition-fixe.json", full_course(
    cours_id="cours_les-verbes-a-preposition-fixe",
    titre="Les verbes suivis de prépositions fixes (depend on)",
    sous_theme="Prepositional verbs",
    duree=20,
    tags=["prepositional verbs", "depend on", "vocabulary"],
    exercice_numero="1",
    rappel_id="rdm-bac-c-d-anglais-2012-cameroun-ex1-q2c-0",
    accroche=(
        "Certains verbes anglais s'associent toujours à la même préposition, quel que soit le "
        "contexte - et cette préposition ne se devine jamais à partir du français. C'est un "
        "terrain glissant pour les francophones, qui traduisent souvent la préposition "
        "française et se trompent systématiquement. Ce cours te donne la méthode pour "
        "mémoriser ces couples verbe-préposition efficacement."
    ),
    prerequis=[
        "Vocabulaire de base des verbes courants en anglais",
        "Notion de préposition (on, at, for, from, of...)",
    ],
    regle_titre="Le verbe et sa préposition forment un bloc lexical indissociable",
    regle_contenu=(
        "Certains verbes anglais imposent une préposition fixe, indépendamment du sens de la "
        "phrase : depend on, listen to, look for, wait for, apologise for, arrive at/in, "
        "believe in, rely on, insist on... Cette préposition doit être mémorisée avec le "
        "verbe comme une unité lexicale unique, jamais déduite d'une traduction française.\n\n"
        "Le piège le plus fréquent vient justement de la traduction : le français « dépendre "
        "DE » pousse à écrire *depend FROM* ou *depend OF*, deux erreurs classiques. La seule "
        "façon fiable d'éviter ce piège est de mémoriser le verbe et sa préposition ensemble, "
        "comme s'il s'agissait d'un seul mot composé (« dependon »), et non comme deux mots "
        "séparés qu'on pourrait recombiner librement."
    ),
    formule_principale=None,
    exemple_enonce="Complète : Modern women don't necessarily depend ___ their husbands nowadays. (from / on / over / for)",
    etapes=[
        etape(1, "Identifier le verbe de la phrase",
              "C'est le verbe, pas le sens général de la phrase, qui impose la préposition.",
              "Le verbe est *depend*."),
        etape(2, "Associer le verbe à sa préposition fixe mémorisée",
              "Depend se construit toujours avec la même préposition, quel que soit le contexte.",
              "depend + on (jamais from, of ou for)."),
        etape(3, "Éliminer les trois autres options par élimination",
              "Aucune des trois autres prépositions ne peut suivre depend en anglais standard.",
              "from, over et for sont incorrects après depend."),
    ],
    exemple_conclusion=(
        "Modern women don't necessarily depend on their husbands nowadays. - depend impose "
        "systématiquement la préposition on, quelle que soit la phrase dans laquelle il "
        "apparaît."
    ),
    erreurs=[
        erreur("Traduire littéralement le français « dépendre de » et écrire *depend from* ou *depend of*",
               "La préposition anglaise associée à un verbe ne correspond presque jamais exactement à la préposition française équivalente ; depend impose on, un choix qui n'a aucun lien logique avec le français « de ».",
               "depend on"),
        erreur("Appliquer la même préposition à tous les verbes de sens proche, ex. utiliser *rely for* par analogie avec listen to",
               "Chaque verbe a sa propre préposition fixe, indépendamment des verbes de sens voisin ; rely s'associe à on (rely on), pas à for.",
               "rely on quelqu'un, mais wait FOR quelqu'un - chaque couple doit être appris séparément."),
        erreur("Oublier la préposition dans une phrase orale ou écrite rapide, ex. *I depend my parents*",
               "Depend est un verbe intransitif indirect : il ne peut jamais être suivi directement d'un complément sans préposition.",
               "I depend ON my parents."),
    ],
    exercices=[
        exo(1, "facile",
            "Complète avec la préposition correcte : Please listen ___ me carefully.",
            "Listen se construit toujours avec la préposition to (listen to somebody/something), jamais directement avec un complément. Réponse : **Please listen to me carefully.**"),
        exo(2, "moyen",
            "Complète avec la préposition correcte : The company apologised ___ the delay in delivery.",
            "Apologise se construit avec for pour désigner la cause de l'excuse (apologise FOR something) ; la préposition to sert uniquement à désigner le destinataire de l'excuse (apologise TO somebody). Ici, l'espace porte sur la cause. Réponse : **The company apologised for the delay in delivery.**"),
        exo(3, "approfondissement",
            "Complète les deux prépositions manquantes dans cette phrase, en justifiant chaque choix : She insisted ___ paying for the meal, but I told her to wait ___ me at the entrance instead.",
            "Insist se construit toujours avec on (insist on doing something) : premier espace = on. Wait se construit toujours avec for devant un complément de personne ou de chose attendue (wait for somebody) : second espace = for. Réponse : **She insisted on paying for the meal, but I told her to wait for me at the entrance instead.**"),
    ],
    synthese=[
        "Un verbe à préposition fixe forme un bloc indissociable : apprends-le toujours comme une seule unité, jamais séparément.",
        "Ne traduis jamais une préposition anglaise à partir du français : les deux langues associent rarement la même préposition au même verbe.",
        "Dresse-toi une liste personnelle des verbes à préposition les plus piégeux (depend on, listen to, look for, wait for, apologise for, insist on, rely on) et révise-la régulièrement.",
        "Ces questions sont des QCM à réponse binaire (juste ou faux) : elles rapportent des points rapides si la préposition est connue par cœur, ou en font perdre si elle est devinée.",
        "Ce type de question apparaît systématiquement dans la section Grammar ou Vocabulary du BAC anglais.",
    ],
)))

# =====================================================================
# COURS 5 : Le superlatif en anglais (FULL)
# =====================================================================
courses.append(("cours_le-superlatif-en-anglais.json", full_course(
    cours_id="cours_le-superlatif-en-anglais",
    titre="Le superlatif en anglais (comparative and superlative forms)",
    sous_theme="Adjectifs : comparatif et superlatif",
    duree=20,
    tags=["superlative", "comparative", "adjectives"],
    exercice_numero="1",
    rappel_id="rdm-bac-c-d-anglais-2012-cameroun-ex1-q2d-0",
    accroche=(
        "Comparer deux éléments ou comparer un élément à tout un groupe ne suit pas la même "
        "règle en anglais - et c'est justement cette distinction que le BAC aime tester. Ce "
        "cours te montre comment reconnaître en un coup d'œil s'il faut un comparatif ou un "
        "superlatif, à partir d'un seul indice dans la phrase."
    ),
    prerequis=[
        "Formation des adjectifs courts et longs en anglais",
        "Le comparatif de supériorité (more... than / -er... than)",
    ],
    regle_titre="Comparatif (deux éléments) vs superlatif (un groupe entier)",
    regle_contenu=(
        "Pour comparer un élément à l'ensemble d'un groupe (plusieurs éléments, une catégorie "
        "entière), on utilise le superlatif, introduit par *the* et suivi de *most + adjectif "
        "long* (ou de la terminaison *-est* pour les adjectifs courts d'une ou deux "
        "syllabes).\n\n"
        "Le comparatif, lui, ne compare que deux éléments entre eux et n'est jamais précédé de "
        "*the* dans cette fonction : *more + adjectif long + than* (ou *-er + than* pour les "
        "adjectifs courts).\n\n"
        "L'indice le plus fiable pour choisir entre les deux est le complément qui suit "
        "l'adjectif : s'il désigne un groupe entier (« in Yaoundé », « in the class », « in "
        "the world », « of all »), c'est un superlatif ; s'il compare à un seul autre élément "
        "nommé (« than the Mont-Fébé Hotel »), c'est un comparatif."
    ),
    formule_principale="the most/-est + adjectif (superlatif) vs more/-er + adjectif + than (comparatif)",
    exemple_enonce="Complète : Hilton still remains the …… comfortable hotel in Yaoundé. (much / more / most / many)",
    etapes=[
        etape(1, "Repérer le complément qui suit l'adjectif",
              "Ce complément indique si la comparaison porte sur un groupe entier ou sur un seul autre élément.",
              "« in Yaoundé » désigne l'ensemble des hôtels de Yaoundé, un groupe entier, pas un seul autre hôtel nommé."),
        etape(2, "Vérifier la présence de l'article the devant l'espace vide",
              "The devant un adjectif de comparaison est le marqueur systématique du superlatif.",
              "L'article the est déjà présent juste avant l'espace : « the …… comfortable hotel »."),
        etape(3, "Choisir la forme du superlatif selon la longueur de l'adjectif",
              "Comfortable est un adjectif de plus de deux syllabes ; son superlatif se forme avec most, jamais avec la terminaison -est.",
              "**most**"),
    ],
    exemple_conclusion=(
        "Hilton still remains the most comfortable hotel in Yaoundé. - la comparaison porte "
        "sur l'ensemble des hôtels de la ville, ce qui impose le superlatif the most "
        "comfortable, jamais le comparatif more comfortable."
    ),
    erreurs=[
        erreur("Utiliser more après the, ex. *the more comfortable hotel*",
               "More s'utilise pour comparer seulement deux éléments (more comfortable THAN...) ; il n'est jamais précédé de the dans une comparaison à un groupe entier.",
               "the most comfortable hotel in Yaoundé"),
        erreur("Former le superlatif d'un adjectif long avec la terminaison -est, ex. *comfortablest*",
               "Seuls les adjectifs courts (une syllabe, ou deux syllabes terminés en -y comme happy) prennent la terminaison -est ; comfortable, adjectif de trois syllabes, doit obligatoirement passer par most.",
               "the most comfortable"),
        erreur("Oublier the devant un superlatif",
               "The est obligatoire devant tout superlatif en anglais, contrairement au français où l'article peut varier (le plus, la plus...) ; son absence rend la phrase incorrecte.",
               "the most comfortable hotel"),
    ],
    exercices=[
        exo(1, "facile",
            "Complète : Mount Cameroon is (high) mountain in West Africa.",
            "High est un adjectif court d'une syllabe : son superlatif se forme avec la terminaison -est, précédée de the. Réponse : **Mount Cameroon is the highest mountain in West Africa.**"),
        exo(2, "moyen",
            "Complète : This exercise is (difficult) than the previous one.",
            "La comparaison porte sur seulement deux éléments (this exercise / the previous one), reliés par than : c'est un comparatif, pas un superlatif. Difficult est un adjectif long, son comparatif se forme avec more. Réponse : **This exercise is more difficult than the previous one.**"),
        exo(3, "approfondissement",
            "Complète les deux comparaisons dans ce texte, en justifiant chaque choix : Of all the students in the class, Paul is (intelligent) student, but Marie is (hardworking) than him.",
            "« Of all the students in the class » désigne un groupe entier : c'est un superlatif, avec the most intelligent student (adjectif long). « than him » compare seulement deux personnes (Marie et Paul) : c'est un comparatif, avec more hardworking than (adjectif long). Réponse : **Paul is the most intelligent student, but Marie is more hardworking than him.**"),
    ],
    synthese=[
        "Compare à un groupe entier -> superlatif (the most/-est) ; compare à un seul autre élément -> comparatif (more/-er... than).",
        "Repère le complément après l'adjectif : 'in the world', 'of all', 'in the class' signalent presque toujours un superlatif.",
        "The est obligatoire devant un superlatif, jamais devant un comparatif employé seul.",
        "Les adjectifs courts (1-2 syllabes) prennent -er/-est ; les adjectifs longs (3 syllabes et plus) passent par more/most.",
        "Ce point de grammaire revient très régulièrement au BAC, en Grammar comme en Vocabulary, souvent sous forme de QCM à quatre choix.",
    ],
)))

# =====================================================================
# COURS 6 : Les connecteurs logiques de consequence (FULL)
# =====================================================================
courses.append(("cours_les-connecteurs-logiques-de-consequence.json", full_course(
    cours_id="cours_les-connecteurs-logiques-de-consequence",
    titre="Les connecteurs logiques de conséquence (otherwise, unless...)",
    sous_theme="Connecteurs logiques",
    duree=20,
    tags=["linking words", "otherwise", "unless", "connectors"],
    exercice_numero="1",
    rappel_id="rdm-bac-c-d-anglais-2012-cameroun-ex1-q2e-0",
    accroche=(
        "Otherwise, unless, however : ces connecteurs se ressemblent tous un peu dans leur "
        "usage, mais chacun impose une construction grammaticale précise et différente. "
        "Confondre l'un avec l'autre change complètement le sens - ou rend la phrase "
        "grammaticalement incorrecte. Ce cours t'apprend à les distinguer à coup sûr."
    ),
    prerequis=[
        "La proposition subordonnée en anglais",
        "Les connecteurs logiques de base (and, but, so)",
    ],
    regle_titre="Distinguer otherwise, unless et however selon la construction de la phrase",
    regle_contenu=(
        "*Otherwise* introduit la conséquence négative qui se produirait si une "
        "recommandation ou une condition énoncée juste avant n'était pas respectée : il "
        "équivaut à « sinon » et relie deux phrases indépendantes, chacune complète avec son "
        "propre sujet et son propre verbe conjugué.\n\n"
        "*Unless* introduit une condition (« à moins que ») et fusionne les deux propositions "
        "en UNE SEULE phrase grammaticale : *Unless + sujet + verbe, sujet + verbe*.\n\n"
        "*However* introduit une opposition ou une nuance (« cependant »), pas une "
        "conséquence.\n\n"
        "La clé pour choisir entre otherwise et unless est de vérifier si la phrase après le "
        "connecteur est grammaticalement complète et indépendante : si oui, penser d'abord à "
        "otherwise, however ou therefore ; si les deux propositions doivent être fusionnées en "
        "une seule phrase, c'est unless qu'il faut utiliser."
    ),
    formule_principale=None,
    exemple_enonce="Complète : University lecturers must be well paid, ……. these will be s considerable brain drain. (however / unless / as soon as / otherwise)",
    etapes=[
        etape(1, "Identifier la relation logique entre les deux parties de la phrase",
              "La première partie est une recommandation (bien payer les enseignants), la seconde annonce ce qui arrivera si elle n'est pas suivie.",
              "Recommandation, puis conséquence négative en cas de non-respect : c'est la structure typique introduite par otherwise."),
        etape(2, "Vérifier que la phrase après l'espace est grammaticalement complète et indépendante",
              "Otherwise relie deux phrases indépendantes, contrairement à unless qui fusionne les deux propositions.",
              "« there will be a considerable brain drain » a son propre sujet (there) et son propre verbe conjugué (will be) : c'est une phrase indépendante complète."),
        etape(3, "Éliminer les trois autres connecteurs",
              "Chacun impose un sens ou une construction incompatible avec cette phrase.",
              "However introduirait une opposition, pas une conséquence ; unless et as soon as exigent une proposition subordonnée fusionnée avec sujet et verbe juste après, ce qui n'est pas la construction ici."),
    ],
    exemple_conclusion=(
        "University lecturers must be well paid, otherwise there will be a considerable brain "
        "drain. - otherwise relie deux phrases indépendantes pour exprimer la conséquence "
        "d'une recommandation non suivie."
    ),
    erreurs=[
        erreur("Confondre unless et otherwise et les utiliser indifféremment, ex. *University lecturers must be well paid, unless there will be a brain drain*",
               "Unless fusionne les deux propositions en une seule phrase grammaticale (Unless + sujet + verbe, sujet + verbe) ; ici la seconde partie est déjà une phrase indépendante complète avec son propre sujet (there) et son verbe (will be), ce qui exige otherwise, pas unless.",
               "University lecturers must be well paid, otherwise there will be a considerable brain drain."),
        erreur("Utiliser however pour exprimer une conséquence",
               "However introduit une opposition ou une nuance, jamais une relation de cause à conséquence ; il ne peut pas remplacer otherwise dans ce contexte.",
               "otherwise there will be a considerable brain drain"),
        erreur("Utiliser as soon as pour exprimer une menace ou une conséquence",
               "As soon as introduit un repère temporel (« dès que »), pas une relation de conséquence ; la phrase n'a aucun sens temporel ici.",
               "otherwise there will be a considerable brain drain"),
    ],
    exercices=[
        exo(1, "facile",
            "Complète avec otherwise ou unless : Take an umbrella, ……. you will get wet.",
            "« you will get wet » est une phrase indépendante complète (sujet you, verbe will get) : c'est otherwise qu'il faut utiliser, pas unless. Réponse : **Take an umbrella, otherwise you will get wet.**"),
        exo(2, "moyen",
            "Complète avec otherwise ou unless : ……. you study harder, you will fail the exam.",
            "Les deux propositions doivent être fusionnées en une seule phrase introduite par le connecteur, avec la condition en tête : c'est la construction typique de unless. Réponse : **Unless you study harder, you will fail the exam.**"),
        exo(3, "approfondissement",
            "Choisis le bon connecteur parmi (however / otherwise / unless) pour chacun des deux espaces de ce texte, en justifiant : The team played well. ……. (1), they lost the match. They must train harder, ……. (2) they will lose again next week.",
            "(1) Le premier espace exprime une opposition entre bien jouer et pourtant perdre : c'est however. (2) Le second espace exprime la conséquence négative d'une recommandation non suivie, avec une phrase indépendante après (they will lose) : c'est otherwise. Réponse : **(1) However, they lost the match. (2) ...otherwise they will lose again next week.**"),
    ],
    synthese=[
        "Otherwise relie deux phrases indépendantes pour exprimer la conséquence négative d'une recommandation non suivie.",
        "Unless fusionne les deux propositions en une seule phrase et introduit une condition, pas une simple conséquence.",
        "However exprime une opposition, jamais une relation de cause à conséquence.",
        "Vérifie toujours si la phrase après le connecteur est grammaticalement complète et indépendante : cela détermine immédiatement le bon choix entre otherwise et unless.",
        "Ces connecteurs sont un grand classique du BAC anglais, testés en Grammar sous forme de QCM à quatre choix.",
    ],
)))

# =====================================================================
# COURS 7 : Choix lexical approprie en contexte (FULL)
# =====================================================================
courses.append(("cours_choix-lexical-approprie-en-contexte.json", full_course(
    cours_id="cours_choix-lexical-approprie-en-contexte",
    titre="Choix lexical approprié en contexte (vocabulary in context)",
    sous_theme="Vocabulaire en contexte",
    duree=20,
    tags=["vocabulary in context", "cloze", "word choice"],
    exercice_numero="2",
    rappel_id="rdm-bac-c-d-anglais-2012-cameroun-ex2-q1a-0",
    accroche=(
        "Un exercice de vocabulaire en contexte ne demande jamais de connaître LE mot exact "
        "attendu par le correcteur : il demande de comprendre la situation dans son ensemble "
        "et de proposer un mot dont le sens ET la nature grammaticale conviennent. Ce cours "
        "te montre la méthode pour ne jamais te tromper de catégorie de mot, même quand "
        "plusieurs réponses sont possibles."
    ),
    prerequis=[
        "Vocabulaire courant de la vie quotidienne en anglais",
        "Distinction entre nom, verbe, adjectif (catégories grammaticales de base)",
    ],
    regle_titre="Comprendre avant de choisir : sens et catégorie grammaticale",
    regle_contenu=(
        "Ce type d'exercice de vocabulaire en contexte demande de déduire le mot manquant à "
        "partir du sens global de la phrase, jamais à partir d'une liste fermée de "
        "possibilités. La méthode se déroule toujours en deux étapes :\n\n"
        "1. Comprendre la situation décrite dans son ensemble - qui fait quoi, dans quel "
        "contexte, avec quelle conséquence.\n"
        "2. Choisir un mot dont le sens ET la catégorie grammaticale (nom, verbe, adjectif...) "
        "conviennent exactement à l'espace vide, en observant les indices grammaticaux autour "
        "de l'espace (article, préposition, terminaison verbale attendue).\n\n"
        "Beaucoup de ces questions acceptent plusieurs réponses valables : ce qui compte "
        "n'est pas de deviner LE mot unique attendu par le correcteur, mais de proposer un "
        "mot cohérent avec le sens ET correct grammaticalement."
    ),
    formule_principale=None,
    exemple_enonce="Complète : George is interested in money. When he leaves school he might be a …………….",
    etapes=[
        etape(1, "Repérer l'indice de sens dans la phrase précédente",
              "La première phrase donne toujours le contexte nécessaire pour comprendre ce qui est attendu dans la seconde.",
              "« George is interested in money » indique que le métier recherché doit être en lien direct avec la finance."),
        etape(2, "Identifier la catégorie grammaticale attendue par la structure de la phrase",
              "L'article indéfini a juste avant l'espace impose un nom singulier comptable.",
              "« he might be a …… » appelle un nom de métier, singulier, précédé de l'article a."),
        etape(3, "Proposer un mot cohérent avec le sens et la catégorie grammaticale",
              "Plusieurs métiers liés à l'argent conviennent : il suffit d'en choisir un qui a du sens et qui respecte la structure grammaticale.",
              "**banker** (ou accountant, businessman, economist)"),
    ],
    exemple_conclusion=(
        "When he leaves school he might be a banker. - le mot choisi respecte à la fois le "
        "sens de la phrase (lien avec l'argent) et sa structure grammaticale (nom de métier "
        "singulier après l'article a)."
    ),
    erreurs=[
        erreur("Chercher LE mot unique attendu par le correcteur plutôt qu'un mot cohérent",
               "La plupart de ces questions acceptent toute réponse cohérente avec le sens et correcte grammaticalement ; se bloquer en cherchant un mot précis fait perdre un temps précieux le jour de l'épreuve.",
               "Propose n'importe quel mot dont le sens ET la catégorie grammaticale conviennent : banker, accountant, businessman sont tous acceptables pour George intéressé par l'argent."),
        erreur("Choisir un mot dont le sens convient mais dont la catégorie grammaticale ne correspond pas à la structure de la phrase, ex. *he might be a rich* (adjectif à la place d'un nom)",
               "Après l'article a, seul un nom singulier peut apparaître ; un adjectif seul comme rich ne peut pas occuper cette position.",
               "he might be a rich businessman (ajout du nom manquant) ou simplement a banker"),
        erreur("Ignorer les indices grammaticaux autour de l'espace vide (article, préposition, terminaison verbale)",
               "Ces indices réduisent immédiatement le champ des réponses possibles ; les ignorer conduit à proposer un mot grammaticalement incompatible même si son sens semble correct.",
               "Observe toujours ce qui précède et suit l'espace vide avant de choisir ton mot."),
    ],
    exercices=[
        exo(1, "facile",
            "Complète avec un mot approprié : It was raining, so she took her ……… before leaving the house.",
            "Le contexte (« it was raining ») appelle un objet que l'on prend pour se protéger de la pluie ; la structure « her ……… » attend un nom singulier. Réponse : **umbrella** - It was raining, so she took her umbrella before leaving the house."),
        exo(2, "moyen",
            "Complète avec un mot approprié : The thief was arrested because a ……… saw him leaving the shop with stolen goods.",
            "L'espace est le sujet du verbe saw : il faut donc un nom de personne, singulier, capable d'avoir vu la scène. Réponse : **witness** - The thief was arrested because a witness saw him leaving the shop with stolen goods."),
        exo(3, "approfondissement",
            "Complète les deux espaces de cette phrase avec des mots de catégories grammaticales différentes, en justifiant chaque choix : The ……… (1) doctor examined the patient carefully before ……… (2) him some medicine.",
            "(1) L'espace se situe entre l'article the et le nom doctor : il attend un adjectif qualificatif (ex. young, experienced). (2) L'espace suit before, qui appelle un verbe en -ing (avant de faire quelque chose) : il attend un verbe comme giving ou prescribing. Réponse : **The experienced doctor examined the patient carefully before prescribing him some medicine.**"),
    ],
    synthese=[
        "Comprends toujours la situation globale avant de chercher un mot précis : le sens général guide le choix bien plus qu'une liste de vocabulaire isolée.",
        "Vérifie la catégorie grammaticale attendue (nom, verbe, adjectif) à partir des indices autour de l'espace vide (article, préposition, terminaison).",
        "La plupart de ces questions acceptent plusieurs réponses valables : ne perds pas de temps à chercher LE mot unique attendu.",
        "Un mot dont le sens est juste mais la catégorie grammaticale fausse reste une réponse incorrecte.",
        "Ce type d'exercice constitue une part importante de la section Vocabulary du BAC anglais, souvent sous forme de phrases à trous indépendantes.",
    ],
)))

# =====================================================================
# COURS 8 : Collocations et expressions figees (FULL)
# =====================================================================
courses.append(("cours_collocations-et-expressions-figees-en-anglais.json", full_course(
    cours_id="cours_collocations-et-expressions-figees-en-anglais",
    titre="Collocations et expressions figées en anglais (lexical sets)",
    sous_theme="Collocations et expressions idiomatiques",
    duree=20,
    tags=["collocations", "idioms", "matching exercise"],
    exercice_numero="2",
    rappel_id="rdm-bac-c-d-anglais-2012-cameroun-ex2-q2-0",
    accroche=(
        "En anglais, certains mots s'attirent : ils forment des paires quasi obligatoires, "
        "des collocations, qu'aucune règle de grammaire ne prédit et qu'aucune traduction "
        "mot à mot du français ne permet de deviner. Un exercice d'appariement (matching "
        "exercise) teste précisément cette connaissance. Ce cours te montre comment "
        "mémoriser ces blocs lexicaux efficacement plutôt que mot par mot."
    ),
    prerequis=[
        "Vocabulaire de base sur l'environnement et l'actualité (recyclage, pollution, catastrophes)",
        "Compréhension du principe d'appariement (matching) dans un exercice",
    ],
    regle_titre="Les collocations se mémorisent en blocs, jamais mot par mot",
    regle_contenu=(
        "Une collocation est une association de mots qui se combinent de façon fixe et "
        "prévisible en anglais, sans que leur sens se devine par simple traduction mot à mot "
        "du français : *oil slicks* (marées noires), *a bone of contention* (une pomme de "
        "discorde), *natural disasters* (catastrophes naturelles), *recycled materials* "
        "(matériaux recyclés), *amputation of the limbs* (amputation des membres).\n\n"
        "Pour réussir un exercice d'appariement de ce type, il faut connaître chaque "
        "expression comme un bloc lexical entier, pas seulement le sens isolé de chaque mot "
        "pris séparément. La méthode consiste à tester mentalement chaque association "
        "proposée en te demandant : « est-ce que cette expression existe telle quelle en "
        "anglais, avec ce sens précis ? », plutôt que de traduire chaque mot du français vers "
        "l'anglais indépendamment."
    ),
    formule_principale=None,
    exemple_enonce="Associe chaque mot de la colonne A à l'expression correspondante de la colonne B : 2) A bone of → d) Contention",
    etapes=[
        etape(1, "Lire l'élément de la colonne A isolément",
              "Pris seul, 'a bone of' n'a aucun sens complet en anglais : c'est le signal qu'il s'agit d'une expression figée à compléter.",
              "« A bone of » est le début d'une expression figée, pas un groupe de mots au sens autonome."),
        etape(2, "Chercher dans la colonne B le mot qui complète une expression figée réellement existante",
              "La bonne réponse doit former une collocation attestée en anglais, pas seulement un groupe de mots grammaticalement possible.",
              "« a bone of contention » est une expression idiomatique attestée signifiant « une source de désaccord »."),
        etape(3, "Vérifier le sens global de l'expression reconstituée",
              "Une fois l'expression reconstituée, son sens doit être cohérent et connu, ce qui confirme le bon appariement.",
              "« a bone of contention » = un sujet de discorde, un point de désaccord récurrent entre deux parties."),
    ],
    exemple_conclusion=(
        "2) A bone of → d) Contention. « A bone of contention » est une expression figée à "
        "mémoriser comme un bloc entier, sans chercher à traduire « bone » (os) littéralement."
    ),
    erreurs=[
        erreur("Traduire littéralement une expression figée, ex. comprendre 'a bone of contention' comme 'un os de discorde'",
               "Une expression idiomatique ne se traduit jamais mot à mot : son sens global (ici, un sujet de désaccord) n'a aucun rapport logique avec la traduction littérale de chacun de ses mots.",
               "Mémorise 'a bone of contention' comme un bloc entier signifiant 'un sujet de discorde', sans passer par la traduction littérale."),
        erreur("Associer deux mots uniquement parce qu'ils semblent grammaticalement compatibles, sans vérifier que l'expression existe réellement",
               "Une association grammaticalement correcte n'est pas forcément une collocation attestée en anglais ; seules les expressions réellement utilisées par les locuteurs natifs sont acceptées.",
               "Vérifie que chaque expression reconstituée existe réellement en anglais courant, pas seulement qu'elle est grammaticalement possible."),
        erreur("Répéter un élément de la colonne B déjà utilisé pour un autre appariement",
               "La consigne précise toujours 'use each item only once' : chaque élément ne peut servir qu'à un seul appariement, et une répétition invalide automatiquement au moins une des deux réponses.",
               "Élimine au fur et à mesure les éléments déjà utilisés de la colonne B pour éviter toute répétition."),
    ],
    exercices=[
        exo(1, "facile",
            "Associe : 'Heavy' → (a) rain / (b) sun / (c) wind. Quelle est la collocation correcte ?",
            "En anglais, on dit toujours « heavy rain » pour désigner une pluie forte ; « heavy sun » et « heavy wind » ne sont pas des collocations attestées (on dirait plutôt strong wind, hot sun). Réponse : **heavy rain**."),
        exo(2, "moyen",
            "Associe chaque mot de la colonne A à la colonne B : 1) Make 2) Do → a) a mistake b) homework",
            "Make et do sont deux verbes proches en français (« faire ») mais qui se distribuent différemment en anglais : on fait une erreur avec make (make a mistake) et un devoir avec do (do homework). Réponse : **1) Make → a) a mistake ; 2) Do → b) homework.**"),
        exo(3, "approfondissement",
            "Reconstitue les trois expressions figées suivantes en associant chaque début de la colonne A à sa fin dans la colonne B, en justifiant chaque choix : A: 1) Take 2) Keep 3) Break B: a) a promise b) an eye on c) a decision",
            "Take se combine avec decision (take a decision, prendre une décision) ; keep se combine avec « an eye on » (keep an eye on, surveiller) ; break se combine avec promise (break a promise, rompre une promesse). Réponse : **1) Take → c) a decision ; 2) Keep → b) an eye on ; 3) Break → a) a promise.**"),
    ],
    synthese=[
        "Une collocation se mémorise comme un bloc lexical entier, jamais mot par mot ni par traduction littérale du français.",
        "Teste chaque appariement proposé en te demandant si l'expression reconstituée existe réellement en anglais courant.",
        "Élimine au fur et à mesure les éléments déjà utilisés dans un exercice d'appariement : la consigne interdit presque toujours la répétition.",
        "Constitue-toi des listes de collocations par thème (make/do, take/keep/break + nom) : elles reviennent très régulièrement au BAC.",
        "Ce type d'exercice teste ta richesse lexicale réelle en anglais, au-delà du simple vocabulaire isolé - il est très valorisé dans la section Vocabulary du BAC.",
    ],
)))

# =====================================================================
# COURS 9 : Completion lexicale a partir d'une liste de mots (FULL)
# =====================================================================
courses.append(("cours_completion-lexicale-a-partir-dune-liste-de-mots.json", full_course(
    cours_id="cours_completion-lexicale-a-partir-dune-liste-de-mots",
    titre="Complétion lexicale à partir d'une liste de mots (word bank cloze)",
    sous_theme="Texte a trous avec liste fermee",
    duree=20,
    tags=["word bank cloze", "vocabulary", "reading"],
    exercice_numero="2",
    rappel_id="rdm-bac-c-d-anglais-2012-cameroun-ex2-q3-0",
    accroche=(
        "Un texte à trous accompagné d'une liste fermée de mots semble plus facile qu'un "
        "texte à trous libre - et pourtant, beaucoup d'élèves perdent des points en plaçant "
        "les mots dans le mauvais ordre. Ce cours te donne une méthode rigoureuse, par "
        "élimination progressive, pour ne jamais te tromper de mot ni en utiliser un deux "
        "fois par erreur."
    ),
    prerequis=[
        "Catégories grammaticales de base (nom, verbe)",
        "Lecture attentive d'un texte court en anglais",
    ],
    regle_titre="Méthode par élimination progressive",
    regle_contenu=(
        "Dans un texte à trous avec une liste de mots fermée, il faut d'abord repérer la "
        "catégorie grammaticale et le sens attendus par chaque espace (lieu, personne, "
        "action, activité...), puis éliminer au fur et à mesure les mots de la liste déjà "
        "utilisés ailleurs dans le texte, puisque la consigne interdit toute répétition.\n\n"
        "La méthode se déroule en trois temps :\n\n"
        "1. Lire le texte en entier une première fois, sans essayer de remplir les espaces, "
        "pour comprendre le sens global.\n"
        "2. Traiter en premier les espaces dont la réponse est évidente et non ambiguë : "
        "chaque mot placé élimine une option pour les espaces restants.\n"
        "3. Terminer par les espaces les plus difficiles, en t'appuyant sur les mots qu'il te "
        "reste dans la liste - à ce stade, l'élimination progressive a souvent déjà réduit tes "
        "choix à une seule possibilité logique."
    ),
    formule_principale=None,
    exemple_enonce=(
        "Complète ce texte avec les mots de la liste (research, factories, laboratories, "
        "scientists, experiments), chaque mot une seule fois : In (1) …… all round the world "
        "(2) ….... carry out many (3) …... and do important (4) …….. on ways of improving "
        "technology. Machinery has already replaced large numbers of workers in many (5) ……."
    ),
    etapes=[
        etape(1, "Lire le texte en entier pour comprendre le sens global",
              "Comprendre le fil du texte évite de placer un mot correct grammaticalement mais absurde dans le contexte.",
              "Le texte décrit des scientifiques qui font des expériences et de la recherche dans des laboratoires, avant de mentionner l'impact des machines sur les usines."),
        etape(2, "Traiter l'espace (2), sujet du verbe carry out",
              "Le sujet d'un verbe d'action comme carry out doit être une personne ou un groupe de personnes, pas un lieu ni une activité.",
              "(2) = scientists (les seules personnes de la liste)."),
        etape(3, "Traiter les espaces (1) et (5), qui désignent chacun un lieu",
              "Une fois scientists placé, il reste deux lieux possibles dans la liste (laboratories, factories) pour les deux espaces désignant un lieu.",
              "(1) = laboratories (lieu où travaillent les scientifiques, 'all round the world') ; (5) = factories (lieu où travaillent les ouvriers remplacés par les machines)."),
        etape(4, "Traiter les espaces (3) et (4), compléments respectifs de carry out et de do",
              "Carry out s'associe à experiments (mener des expériences) ; do s'associe à research (faire de la recherche) - les deux derniers mots restants de la liste.",
              "(3) = experiments ; (4) = research."),
    ],
    exemple_conclusion=(
        "In laboratories all round the world scientists carry out many experiments and do "
        "important research on ways of improving technology. Machinery has already replaced "
        "large numbers of workers in many factories... - chacun des cinq mots de la liste a "
        "été utilisé exactement une fois, dans l'ordre logique dicté par le sens et la "
        "grammaire du texte."
    ),
    erreurs=[
        erreur("Remplir les espaces dans l'ordre du texte sans tenir compte des mots déjà utilisés",
               "Traiter les espaces dans l'ordre linéaire, sans stratégie d'élimination, conduit souvent à utiliser un mot évident trop tôt et à se retrouver bloqué sur un espace plus tard, sans mot restant qui convienne.",
               "Traite d'abord les espaces les plus évidents, quel que soit leur ordre dans le texte, pour réduire progressivement les mots restants."),
        erreur("Placer research comme sujet d'un verbe d'action alors que c'est une activité, pas une personne",
               "Research est un nom abstrait désignant une activité, pas un acteur humain capable de 'carry out' quelque chose ; seul scientists peut être le sujet d'un tel verbe.",
               "Réserve les noms de personnes (scientists) aux emplacements de sujet d'un verbe d'action, et les noms d'activité (research, experiments) aux emplacements de complément."),
        erreur("Répéter un mot de la liste déjà utilisé pour un autre espace",
               "La consigne 'do not use any word twice' est stricte : réutiliser un mot invalide automatiquement au moins une des deux réponses concernées.",
               "Raye mentalement (ou sur le brouillon) chaque mot de la liste au fur et à mesure que tu l'utilises."),
    ],
    exercices=[
        exo(1, "facile",
            "Complète avec les mots de la liste (bread, bakery, baker), chaque mot une seule fois : The (1) …… works every morning in a small (2) …… where he makes fresh (3) …… for the whole village.",
            "(1) est le sujet du verbe works : c'est une personne, donc baker. (2) suit 'in a small' : c'est un lieu, donc bakery. (3) est le complément de makes, le produit fabriqué : donc bread. Réponse : **The baker works every morning in a small bakery where he makes fresh bread for the whole village.**"),
        exo(2, "moyen",
            "Complète avec les mots de la liste (farmers, harvest, tractors, fields), chaque mot une seule fois : Every year, (1) …… use modern (2) …… to work in their (3) …… and prepare for the (4) …… season.",
            "(1) est le sujet de use : des personnes, donc farmers. (2) est un outil utilisé par les fermiers : tractors. (3) suit 'in their' et désigne un lieu de travail agricole : fields. (4) est un événement saisonnier attendu : harvest. Réponse : **Every year, farmers use modern tractors to work in their fields and prepare for the harvest season.**"),
        exo(3, "approfondissement",
            "Complète ce texte plus long avec les mots de la liste (pollution, factories, government, laws, environment), chaque mot une seule fois, en justifiant chaque choix : Many (1) …… release harmful gases that damage the (2) …… . To fight (3) …… , the (4) …… has passed strict (5) …… .",
            "(1) est le sujet de release, un lieu de production industrielle au pluriel : factories. (2) est ce qui est endommagé par les gaz, un nom abstrait global : environment. (3) suit 'to fight', un problème abstrait à combattre : pollution. (4) est le sujet de has passed, une institution : government. (5) est le complément de has passed, un instrument juridique au pluriel : laws. Réponse : **Many factories release harmful gases that damage the environment. To fight pollution, the government has passed strict laws.**"),
    ],
    synthese=[
        "Lis toujours le texte en entier avant de remplir le moindre espace : le sens global oriente chaque choix.",
        "Traite en premier les espaces les moins ambigus : chaque mot placé élimine une option pour les espaces restants.",
        "Distingue les catégories de mots de la liste (personnes, lieux, activités, objets) avant de les placer : cela évite la plupart des erreurs.",
        "Ne réutilise jamais un mot de la liste : raye-le mentalement dès que tu l'as utilisé.",
        "Ce format d'exercice (word bank cloze) est fréquent dans la section Vocabulary du BAC anglais et récompense la méthode autant que le vocabulaire.",
    ],
)))

# =====================================================================
# COURS 10 : Comprehension ecrite (FULL)
# =====================================================================
courses.append(("cours_comprehension-ecrite-reperer-et-reformuler-linformation.json", full_course(
    cours_id="cours_comprehension-ecrite-reperer-et-reformuler-linformation",
    titre="Compréhension écrite : repérer et reformuler l'information (reading comprehension)",
    sous_theme="Comprehension ecrite",
    duree=25,
    tags=["reading comprehension", "text-based questions", "reformulation"],
    exercice_numero="3",
    rappel_id="rdm-bac-c-d-anglais-2012-cameroun-ex3-q1-0",
    accroche=(
        "Face à un texte de compréhension, la tentation est de recopier directement la "
        "phrase du texte qui semble répondre à la question. C'est pourtant l'une des façons "
        "les plus sûres de perdre des points au BAC, où la consigne exige explicitement des "
        "réponses avec tes propres mots. Ce cours te donne la méthode pour repérer "
        "l'information juste et la reformuler efficacement."
    ),
    prerequis=[
        "Lecture globale d'un texte en anglais de niveau Terminale",
        "Vocabulaire courant lié au thème du texte (ici, argent et travail)",
    ],
    regle_titre="Repérer, puis reformuler - jamais recopier",
    regle_contenu=(
        "La réponse attendue en compréhension écrite n'est jamais une phrase recopiée telle "
        "quelle dans le texte : il faut d'abord repérer, dans le passage, l'endroit précis "
        "qui contient l'information demandée, puis reformuler cette information dans une "
        "phrase complète et autonome, qui a du sens même sans avoir le texte sous les yeux.\n\n"
        "Quand la question réclame un nombre précis d'éléments (« two disadvantages », « two "
        "reasons »...), il faut impérativement fournir ce nombre exact, ni plus ni moins, en "
        "s'appuyant sur des passages distincts du texte plutôt que sur la même idée "
        "reformulée deux fois.\n\n"
        "Pour les questions de type « Justify your answer », la réponse doit toujours "
        "comporter deux parties : une prise de position claire, puis au moins un élément du "
        "texte qui la justifie explicitement."
    ),
    formule_principale=None,
    exemple_enonce="À partir d'un texte sur l'héritage et le travail : Give two disadvantages of inheriting wealth.",
    etapes=[
        etape(1, "Repérer dans le texte les passages qui évoquent un inconvénient de l'héritage",
              "La question porte sur des inconvénients : il faut chercher les passages à connotation négative liés à l'héritage.",
              "Deux passages distincts conviennent : la citation de Carnegie sur les talents 'deadened', et le passage sur l'absence de 'drive' chez ceux qui héritent."),
        etape(2, "Reformuler le premier passage repéré avec ses propres mots",
              "La consigne interdit de recopier le texte tel quel.",
              "L'héritage peut détruire les talents et l'énergie du bénéficiaire, le poussant vers une vie moins réussie."),
        etape(3, "Reformuler le second passage repéré, distinct du premier",
              "La question demande deux éléments distincts, pas la même idée répétée sous une autre forme.",
              "L'héritage prive la personne de la motivation nécessaire pour travailler et réussir par elle-même."),
    ],
    exemple_conclusion=(
        "Deux inconvénients de l'héritage : il peut détruire les talents et l'énergie de "
        "celui qui en bénéficie, et il prive la personne de la motivation nécessaire pour "
        "travailler et réussir par elle-même - deux idées reformulées, chacune appuyée sur un "
        "passage distinct du texte."
    ),
    erreurs=[
        erreur("Recopier mot pour mot la phrase du texte comme réponse finale",
               "La consigne demande explicitement d'utiliser tes propres mots autant que possible ; une citation brute sans reformulation est généralement pénalisée par le barème, même si elle contient la bonne information.",
               "Reformule toujours l'idée repérée dans le texte avec ta propre phrase, en gardant le sens mais pas la formulation exacte."),
        erreur("Fournir deux fois la même idée reformulée différemment quand la question demande deux éléments",
               "Le correcteur attend deux idées réellement distinctes, appuyées sur deux passages différents du texte, pas une seule idée reformulée deux fois de manière à donner l'illusion de deux réponses.",
               "Vérifie que tes deux réponses s'appuient sur deux passages clairement différents du texte."),
        erreur("Répondre à une question de type 'Justify your answer' sans aucune justification textuelle",
               "Une position sans élément du texte pour l'appuyer n'est qu'une opinion personnelle, pas une réponse de compréhension ; le barème récompense explicitement la justification, pas seulement la position choisie.",
               "Accompagne toujours ta réponse d'au moins une citation ou reformulation d'un passage du texte qui la justifie."),
    ],
    exercices=[
        exo(1, "facile",
            "Dans un texte qui affirme 'Exercise improves both physical health and mental well-being', reformule cette idée avec tes propres mots pour répondre à la question 'What are the benefits of exercise mentioned in the text?'",
            "Il faut éviter de recopier la phrase telle quelle et reformuler avec d'autres mots tout en gardant le sens. Réponse : **L'exercice physique améliore à la fois la santé du corps et l'équilibre mental.**"),
        exo(2, "moyen",
            "Un texte affirme : 'Farmers in the region often lose their entire harvest because of irregular rainfall and a lack of proper storage facilities.' Réponds en donnant deux raisons distinctes pour lesquelles les agriculteurs perdent leur récolte.",
            "Le texte donne deux causes clairement distinctes reliées par 'and' : il faut les séparer en deux réponses reformulées, pas les fusionner en une seule idée. Réponse : **Première raison : les pluies sont irrégulières et imprévisibles. Deuxième raison : les agriculteurs ne disposent pas d'installations de stockage adéquates pour conserver leur récolte.**"),
        exo(3, "approfondissement",
            "Un texte conclut : 'Those who save a portion of their income every month, however small, are far better prepared to face unexpected expenses than those who spend everything they earn.' Réponds à la question 'Do all workers manage their money wisely? Justify your answer.'",
            "La réponse doit comporter deux parties : une position claire, puis une justification appuyée sur le texte. Le texte oppose implicitement deux catégories de travailleurs (ceux qui épargnent et ceux qui dépensent tout), ce qui montre que tous ne gèrent pas leur argent avec la même prudence. Réponse : **Non, tous les travailleurs ne gèrent pas leur argent avec sagesse. Le texte oppose ceux qui mettent de côté une partie de leur revenu chaque mois, même modeste, à ceux qui dépensent la totalité de ce qu'ils gagnent ; seuls les premiers sont réellement préparés à faire face à des dépenses imprévues.**"),
    ],
    synthese=[
        "Repère d'abord l'information dans le texte, puis reformule-la : ne recopie jamais la phrase source telle quelle.",
        "Quand la question demande plusieurs éléments, appuie chacun sur un passage distinct du texte, jamais la même idée répétée.",
        "Pour une question 'Justify your answer', construis toujours ta réponse en deux parties : la position, puis la justification textuelle.",
        "Une réponse juste sur le fond mais copiée mot pour mot reste pénalisée : la reformulation fait partie de la compétence évaluée.",
        "La compréhension écrite représente une part importante et récurrente du BAC anglais (Section C), toujours construite sur ce même schéma texte + questions.",
    ],
)))

# =====================================================================
# COURS 11 : Redaction d'un essai d'opinion (FULL)
# =====================================================================
courses.append(("cours_redaction-dun-essai-dopinion-en-anglais.json", full_course(
    cours_id="cours_redaction-dun-essai-dopinion-en-anglais",
    titre="Rédaction d'un essai d'opinion en anglais (opinion essay)",
    sous_theme="Production ecrite : essai d'opinion",
    duree=30,
    tags=["opinion essay", "essay writing", "production ecrite"],
    exercice_numero="4",
    rappel_id="rdm-bac-c-d-anglais-2012-cameroun-ex4-q1-0",
    accroche=(
        "Un essai d'opinion au BAC n'est pas un texte libre : il obéit à une structure "
        "précise que les correcteurs recherchent activement, indépendamment de la position "
        "défendue. Ce cours te montre comment construire un essai équilibré, argumenté et "
        "dans la bonne fourchette de mots, quel que soit le sujet imposé."
    ),
    prerequis=[
        "Vocabulaire de connecteurs logiques (firstly, moreover, however, in addition, therefore)",
        "Construction de la phrase complexe en anglais (subordonnées, gérondifs)",
    ],
    regle_titre="La structure en trois temps de l'opinion essay",
    regle_contenu=(
        "Un essai d'opinion (opinion essay) en anglais suit une structure fixe en trois "
        "temps :\n\n"
        "1. Une introduction qui reformule le sujet et annonce clairement la position "
        "défendue (la thèse).\n"
        "2. Un développement qui présente plusieurs arguments illustrés par des exemples "
        "concrets, organisé en paragraphes distincts, chacun défendant une seule idée "
        "introduite par un connecteur logique clair (firstly, moreover, however, in "
        "addition...).\n"
        "3. Une conclusion qui résume la position et l'élargit éventuellement à une "
        "perspective plus large.\n\n"
        "Quand le sujet s'y prête, présenter les deux faces d'un débat (arguments 'pour' et "
        "'contre') avant de trancher clairement en conclusion renforce la qualité de "
        "l'argumentation, à condition que la position finale reste nette et non ambiguë."
    ),
    formule_principale=None,
    exemple_enonce="Do you think Health for all by the year 2000 has been achieved?",
    etapes=[
        etape(1, "Rédiger une introduction qui reformule le sujet et annonce la thèse",
              "Le correcteur doit savoir dès les premières lignes quelle position l'essai va défendre.",
              "« When the World Health Organization launched the 'Health for All by the Year 2000' initiative... I strongly believe that this goal has not been fully achieved, even though considerable progress has been made. »"),
        etape(2, "Développer un premier paragraphe présentant les progrès réels obtenus",
              "Reconnaître les avancées réelles avant de nuancer donne plus de crédibilité à l'argumentation qu'une position à sens unique.",
              "Paragraphe sur les campagnes de vaccination, l'espérance de vie, et la construction d'hôpitaux."),
        etape(3, "Développer un second paragraphe qui présente les limites persistantes",
              "C'est ce paragraphe qui justifie la thèse annoncée en introduction (objectif non pleinement atteint).",
              "Paragraphe sur les inégalités entre pays riches et pauvres, l'accès limité aux soins en zone rurale, les maladies évitables qui persistent."),
        etape(4, "Rédiger une conclusion qui reprend la thèse et l'élargit",
              "La conclusion doit clore l'essai sur une idée forte, sans se contenter de répéter l'introduction mot pour mot.",
              "« 'Health for All' remains an ideal rather than a reality... Much work still needs to be done before this promise can honestly be considered fulfilled. »"),
    ],
    exemple_conclusion=(
        "L'essai complet respecte la structure en trois temps (introduction avec thèse "
        "claire, développement équilibré en deux paragraphes, conclusion qui élargit) et se "
        "situe dans la fourchette de 250 à 300 mots imposée par la consigne."
    ),
    erreurs=[
        erreur("Répondre par un simple 'yes' ou 'no' développé sans structure claire",
               "Le correcteur évalue la construction de l'argumentation autant que la position choisie ; une réponse binaire sans paragraphes distincts et sans connecteurs logiques est perçue comme un texte non structuré, même si les idées de fond sont correctes.",
               "Organise toujours ta réponse en introduction, développement en paragraphes distincts, et conclusion, quelle que soit ta position."),
        erreur("Enchaîner les arguments sans aucun connecteur logique entre les paragraphes",
               "Sans connecteurs (firstly, however, in addition, therefore...), le texte perd en cohérence et semble être une liste d'idées juxtaposées plutôt qu'une argumentation construite.",
               "Ouvre chaque nouveau paragraphe par un connecteur logique clair qui indique la relation avec le paragraphe précédent."),
        erreur("Ignorer la fourchette de mots imposée (ici 250 à 300 mots), en écrivant un texte beaucoup trop court ou trop long",
               "Le respect du nombre de mots fait partie des critères de notation d'une production écrite ; un texte trop court manque de développement, un texte trop long risque d'être pénalisé ou de ne pas être entièrement corrigé.",
               "Entraîne-toi à estimer environ 50 mots par paragraphe d'introduction ou de conclusion, et 150 à 180 mots pour les deux paragraphes de développement."),
    ],
    exercices=[
        exo(1, "facile",
            "Rédige uniquement l'introduction (50 à 60 mots) d'un essai répondant à la question : 'Should smoking be banned in all public places?'",
            "L'introduction doit reformuler le sujet puis annoncer clairement une position. Exemple : **Smoking has long been recognized as a serious threat to public health, not only for smokers themselves but also for those around them who breathe second-hand smoke. In my opinion, smoking should indeed be banned in all public places, as the right to breathe clean air outweighs the right to smoke wherever one pleases.** (thèse clairement annoncée dès l'introduction)"),
        exo(2, "moyen",
            "Rédige un paragraphe de développement (environ 80 mots) défendant UN argument en faveur de l'interdiction de fumer dans les lieux publics, introduit par un connecteur logique.",
            "Le paragraphe doit défendre une seule idée, introduite par un connecteur logique explicite, et illustrée par un exemple concret. Exemple : **Firstly, banning smoking in public places protects non-smokers from the harmful effects of passive smoking. Numerous medical studies have shown that second-hand smoke can cause respiratory diseases and even cancer in people who have never smoked a single cigarette. Restaurants, offices and public transport should therefore remain smoke-free, so that everyone, regardless of their own habits, can breathe safely.**"),
        exo(3, "approfondissement",
            "Rédige un essai complet de 250 à 300 mots répondant à la question : 'Do you think social media does more harm than good to young people?' Respecte la structure en trois temps.",
            "L'essai complet doit suivre la structure en trois temps : introduction avec thèse claire, développement en deux paragraphes équilibrés (avantages puis inconvénients, ou l'inverse), conclusion qui tranche. Exemple de structure rédigée : **Introduction** (reformulation du sujet + thèse : les réseaux sociaux font plus de mal que de bien aux jeunes malgré des bénéfices réels) ; **Paragraphe 1** (Firstly, avantages : accès à l'information, maintien des liens sociaux, opportunités d'apprentissage) ; **Paragraphe 2** (However, inconvénients : addiction, comparaison sociale néfaste, exposition au cyberharcèlement, temps perdu au détriment des études) ; **Conclusion** (les risques l'emportent sur les bénéfices tant qu'un usage encadré n'est pas mis en place, appel à une utilisation plus raisonnée). Un candidat doit rédiger ces quatre blocs intégralement en anglais, dans la fourchette de 250 à 300 mots, en respectant scrupuleusement les connecteurs logiques entre paragraphes."),
    ],
    synthese=[
        "Un essai d'opinion se construit toujours en trois temps : introduction avec thèse claire, développement argumenté en paragraphes distincts, conclusion qui élargit.",
        "Reconnaître les deux faces d'un débat avant de trancher renforce ta crédibilité, à condition que ta position finale reste nette.",
        "Chaque paragraphe de développement défend une seule idée, introduite par un connecteur logique explicite.",
        "Respecte la fourchette de mots imposée : ni trop court (argumentation insuffisante), ni trop long (risque de pénalité).",
        "L'essai d'opinion est l'un des trois formats de production écrite les plus fréquents au BAC anglais, avec le discours et la lettre - savoir reconnaître lequel est demandé est la première étape avant même de rédiger.",
    ],
)))

# =====================================================================
# COURS 12 : Redaction d'un discours (FULL)
# =====================================================================
courses.append(("cours_redaction-dun-discours-en-anglais.json", full_course(
    cours_id="cours_redaction-dun-discours-en-anglais",
    titre="Rédaction d'un discours en anglais (speech writing)",
    sous_theme="Production ecrite : discours",
    duree=30,
    tags=["speech writing", "public speaking", "production ecrite"],
    exercice_numero="4",
    rappel_id="rdm-bac-c-d-anglais-2012-cameroun-ex4-q2-0",
    accroche=(
        "Écrire un discours, ce n'est pas écrire un essai qu'on lirait ensuite à voix haute : "
        "c'est un format à part entière, avec ses propres codes d'ouverture, de rythme et de "
        "clôture. Confondre discours et essai fait perdre des points au BAC, même quand le "
        "contenu de fond est excellent. Ce cours te montre comment donner à ton texte une "
        "vraie voix orale."
    ),
    prerequis=[
        "Vocabulaire de politesse et d'adresse à un public (ladies and gentlemen, dear friends)",
        "Impératif et modaux de conseil (should, must, let's)",
    ],
    regle_titre="Les codes obligatoires du discours oral",
    regle_contenu=(
        "Un discours (speech) s'adresse directement à un auditoire précis et respecte des "
        "codes propres à l'oral, absents d'un essai écrit classique :\n\n"
        "1. Une formule d'ouverture qui salue le public (Good morning/afternoon, dear "
        "friends...).\n"
        "2. L'annonce claire du sujet traité, souvent accompagnée d'un remerciement pour "
        "l'invitation à parler.\n"
        "3. Un développement structuré en points clairement séparés, avec un ton plus direct "
        "que l'écrit (phrases courtes, questions rhétoriques adressées au public, usage de "
        "'we'/'you' pour impliquer l'auditoire).\n"
        "4. Une formule de clôture qui remercie l'auditoire et, souvent, l'appelle à agir.\n\n"
        "Le registre reste plus vivant et plus engageant qu'un essai : on écrit comme si l'on "
        "parlait réellement devant les gens visés."
    ),
    formule_principale=None,
    exemple_enonce="You are invited by the youth group of your village to give a talk on hygiene and sanitation. Write the speech to be delivered.",
    etapes=[
        etape(1, "Rédiger la formule d'ouverture et le remerciement",
              "Un discours doit toujours s'adresser explicitement à l'auditoire dès la première phrase, contrairement à un essai qui commence directement par le sujet.",
              "« Good afternoon, dear friends, Thank you for inviting me to speak to you today about a subject that concerns each and every one of us: hygiene and sanitation. »"),
        etape(2, "Structurer le développement en points clairement séparés",
              "Un auditoire qui écoute (plutôt que lit) suit plus facilement un discours organisé en points numérotés ou clairement introduits (First..., Second..., Third...).",
              "Trois conseils pratiques : se laver les mains, boire de l'eau traitée, garder son environnement propre - chacun introduit clairement (First, Second, Third)."),
        etape(3, "Impliquer directement l'auditoire avec des phrases d'adresse directe",
              "Le ton oral d'un discours se construit avec des phrases qui s'adressent explicitement au public ('you', 'we'), pas avec des généralités impersonnelles.",
              "« If each young person here goes home today and washes his or her hands properly... » - adresse directe à l'auditoire présent."),
        etape(4, "Rédiger une formule de clôture qui remercie et appelle à l'action",
              "Un discours se termine toujours par une formule de politesse et souvent un appel à agir, contrairement à un essai qui se termine par une simple conclusion analytique.",
              "« Thank you very much for your attention, and let us all commit today to a cleaner, healthier village. »"),
    ],
    exemple_conclusion=(
        "Le discours complet respecte les quatre codes obligatoires de l'oral (ouverture, "
        "annonce du sujet, développement structuré et adressé au public, clôture avec appel à "
        "l'action), ce qui le distingue clairement d'un essai écrit sur le même thème."
    ),
    erreurs=[
        erreur("Rédiger un discours comme un essai classique, sans formule d'ouverture ni de clôture",
               "L'absence des formules d'adresse au public (Dear friends, Ladies and gentlemen) et de clôture (Thank you for listening) signale immédiatement au correcteur une confusion de format, pénalisée même si le contenu de fond est pertinent.",
               "Ouvre systématiquement par une salutation à l'auditoire et termine par une formule de remerciement."),
        erreur("Garder un ton purement écrit, sans jamais s'adresser directement au public",
               "Un discours qui ne contient aucun 'you' ni 'we' adressé à l'auditoire, et aucune question rhétorique, se lit comme un essai déguisé plutôt que comme un texte destiné à être prononcé.",
               "Insère régulièrement des adresses directes au public et des phrases courtes qui donnent un rythme oral au texte."),
        erreur("Oublier de mentionner explicitement le contexte donné par le sujet (ici, le groupe de jeunes du village)",
               "Un discours générique sur l'hygiène, sans lien avec l'auditoire précis mentionné dans la consigne, ne répond pas complètement à la mise en situation imposée par le sujet.",
               "Ancre ton discours dans le contexte précis donné (ici, les jeunes de ton village), par exemple en les appelant explicitement à agir dans leur propre communauté."),
    ],
    exercices=[
        exo(1, "facile",
            "Rédige uniquement la formule d'ouverture (2 à 3 phrases) d'un discours adressé aux élèves de ton lycée sur le thème du respect entre élèves.",
            "L'ouverture doit saluer le public, remercier pour l'occasion de parler et annoncer le sujet. Exemple : **Good morning, dear schoolmates. Thank you for giving me the opportunity to speak to you today about a value that should guide all of us here: respect among students.**"),
        exo(2, "moyen",
            "Rédige un paragraphe de développement (environ 80 mots) pour un discours sur la protection de l'environnement, adressé à un public de jeunes, avec au moins une adresse directe au public.",
            "Le paragraphe doit contenir une adresse directe au public ('you'/'we') et une question rhétorique pour créer un rythme oral. Exemple : **Have you ever wondered what our village will look like in twenty years if we keep throwing plastic waste into our rivers? Each one of us has the power to change this. By simply picking up litter, planting a tree, or refusing single-use plastic bags, we protect the environment we all depend on for our future.**"),
        exo(3, "approfondissement",
            "Rédige un discours complet de 250 à 300 mots à prononcer devant le club de lecture de ton école, les invitant à lire davantage. Respecte les quatre codes obligatoires du discours.",
            "Le discours complet doit contenir : une ouverture (salutation + remerciement + annonce du sujet), un développement structuré en points séparés (par exemple : la lecture élargit le vocabulaire, la lecture développe l'imagination, la lecture prépare aux examens), des adresses directes régulières au public ('you', 'we', des questions rhétoriques), et une clôture qui remercie et appelle à l'action ('let us all commit to reading at least one book a month'). Un candidat doit rédiger ces quatre éléments intégralement en anglais, dans la fourchette de 250 à 300 mots, en conservant un ton oral vivant du début à la fin plutôt qu'un ton d'essai écrit."),
    ],
    synthese=[
        "Un discours s'adresse toujours directement à un auditoire précis, avec une formule d'ouverture et une formule de clôture obligatoires.",
        "Le ton d'un discours reste plus direct et plus vivant qu'un essai : phrases courtes, questions rhétoriques, adresses explicites au public ('you', 'we').",
        "Structure ton développement en points clairement séparés, plus faciles à suivre à l'oral qu'un paragraphe unique dense.",
        "Ancre toujours ton discours dans le contexte précis donné par le sujet (qui est l'auditoire, dans quelle situation).",
        "Le discours est l'un des trois formats de production écrite testés au BAC anglais : le confondre avec un essai fait perdre des points, même à contenu égal.",
    ],
)))

# =====================================================================
# COURS 13 : Redaction d'une lettre personnelle (FULL)
# =====================================================================
courses.append(("cours_redaction-dune-lettre-personnelle-en-anglais.json", full_course(
    cours_id="cours_redaction-dune-lettre-personnelle-en-anglais",
    titre="Rédaction d'une lettre personnelle en anglais (personal letter)",
    sous_theme="Production ecrite : lettre personnelle",
    duree=30,
    tags=["personal letter", "letter writing", "production ecrite"],
    exercice_numero="4",
    rappel_id="rdm-bac-c-d-anglais-2012-cameroun-ex4-q3-0",
    accroche=(
        "Une lettre à un proche obéit à une présentation précise en anglais, très différente "
        "de celle d'une lettre administrative ou d'un simple essai. Oublier l'en-tête, la "
        "formule d'appel ou la signature fait perdre des points, même quand les conseils "
        "donnés dans la lettre sont excellents sur le fond. Ce cours te montre comment "
        "structurer une lettre personnelle complète et convaincante."
    ),
    prerequis=[
        "Vocabulaire de la santé et des conseils (should, I advise you to, I strongly recommend)",
        "Formules de politesse en anglais adaptées à un registre familial",
    ],
    regle_titre="La présentation obligatoire de la lettre personnelle",
    regle_contenu=(
        "Une lettre à un proche respecte une présentation fixe en anglais :\n\n"
        "1. L'adresse de l'expéditeur, en haut (à droite dans la présentation traditionnelle).\n"
        "2. Une formule d'appel adaptée au destinataire (Dear + prénom pour un proche).\n"
        "3. Un corps de lettre organisé en paragraphes, chacun développant une idée ou un "
        "conseil distinct.\n"
        "4. Une formule de politesse finale adaptée à la relation avec le destinataire (Your "
        "loving brother, Yours affectionately, Love...) suivie de la signature.\n\n"
        "Le registre reste chaleureux et direct, sans les formules très cérémonieuses d'une "
        "lettre administrative (Dear Sir/Madam, Yours faithfully) réservées à un destinataire "
        "inconnu ou officiel. Toutes les données fournies par le sujet (nom, adresse, lien de "
        "parenté) doivent être exploitées dans l'en-tête et la signature."
    ),
    formule_principale=None,
    exemple_enonce=(
        "Your brother Emmanuel Muhum has been hospitalized because of a heart disease. He "
        "has been a cigarette smoker for long and is also very fat. Write a letter advising "
        "him on what to do. Your name is Marcel Muhum and your address is G.H.S. Rex Majama, "
        "P.O. Box 15, Majama."
    ),
    etapes=[
        etape(1, "Rédiger l'en-tête avec l'adresse de l'expéditeur fournie par le sujet",
              "Le sujet donne explicitement l'adresse à utiliser ; l'omettre ou en inventer une autre est une erreur de mise en situation.",
              "« G.H.S. Rex Majama, P.O. Box 15, Majama »"),
        etape(2, "Choisir la formule d'appel adaptée au lien de parenté",
              "S'adresser à son frère appelle une formule chaleureuse et familière, pas une formule cérémonieuse.",
              "« Dear Emmanuel, »"),
        etape(3, "Développer un premier conseil distinct, sur le tabac",
              "Le sujet mentionne explicitement que le frère fume depuis longtemps : ce point doit être traité avec un conseil concret.",
              "Paragraphe conseillant d'arrêter complètement de fumer, avec l'aide d'un médecin."),
        etape(4, "Développer un second conseil distinct, sur le poids et l'alimentation",
              "Le sujet mentionne également que le frère est en surpoids : ce second point doit recevoir son propre conseil, distinct du premier.",
              "Paragraphe conseillant une meilleure alimentation et une activité physique légère."),
        etape(5, "Conclure et signer avec la formule adaptée au lien fraternel",
              "La formule de clôture doit rester cohérente avec le lien familial annoncé dès l'en-tête.",
              "« Your loving brother, Marcel »"),
    ],
    exemple_conclusion=(
        "La lettre complète respecte la présentation obligatoire (adresse, formule d'appel, "
        "corps structuré en conseils distincts, formule de clôture et signature) et exploite "
        "toutes les données fournies par le sujet (nom, adresse, lien de parenté, problèmes de "
        "santé précis du destinataire)."
    ),
    erreurs=[
        erreur("Omettre l'adresse de l'expéditeur ou la formule d'appel, en commençant directement par le corps du texte",
               "Une lettre sans en-tête ni formule d'appel ressemble à un essai déguisé ; ces éléments de présentation font partie des critères de notation d'une lettre, indépendamment de la qualité du contenu.",
               "Commence toujours par l'adresse de l'expéditeur puis la formule d'appel, avant même la première phrase du corps de la lettre."),
        erreur("Utiliser une formule de clôture trop formelle pour un frère, ex. 'Yours faithfully'",
               "'Yours faithfully' est réservé à une lettre officielle adressée à un destinataire inconnu (après 'Dear Sir/Madam') ; pour un proche, il faut une formule chaleureuse comme 'Your loving brother' ou 'Yours affectionately'.",
               "Your loving brother, Marcel"),
        erreur("Ignorer une partie des données fournies par le sujet, par exemple ne conseiller que sur le tabac sans mentionner le poids",
               "Le sujet mentionne explicitement deux problèmes distincts (tabac et surpoids) ; en ignorer un revient à ne pas répondre complètement à la consigne, ce qui est pénalisé par le barème.",
               "Traite chaque élément mentionné dans la mise en situation par un conseil distinct et clairement développé."),
    ],
    exercices=[
        exo(1, "facile",
            "Rédige uniquement l'en-tête et la formule d'appel d'une lettre à ta sœur Aïcha, qui vit à Douala, sachant que ton adresse est Lycée de Bafoussam, B.P. 200, Bafoussam.",
            "L'en-tête reprend l'adresse de l'expéditeur fournie, suivie de la formule d'appel adaptée à une sœur. Exemple : **Lycée de Bafoussam, B.P. 200, Bafoussam. Dear Aïcha,**"),
        exo(2, "moyen",
            "Rédige un paragraphe de conseil (environ 60 mots) à un ami qui néglige ses révisions avant un examen important, en utilisant au moins deux structures de conseil différentes (should, I advise you to).",
            "Le paragraphe doit combiner deux structures de conseil distinctes, dans un registre chaleureux adapté à un ami. Exemple : **You really should start revising more seriously, Paul, especially with the exam coming up so soon. I advise you to make a proper timetable and stick to it every day, even if it is just for one hour after school. Your future depends on the effort you put in now.**"),
        exo(3, "approfondissement",
            "Rédige une lettre complète de 250 à 300 mots à ton cousin qui vient d'échouer à un examen, pour l'encourager et lui donner des conseils concrets pour se préparer différemment l'année suivante. Invente une adresse d'expéditeur cohérente et respecte toute la présentation obligatoire.",
            "La lettre complète doit contenir : une adresse d'expéditeur inventée mais cohérente, une formule d'appel adaptée à un cousin, un corps de lettre organisé en paragraphes distincts (d'abord des mots d'encouragement, puis au moins deux conseils concrets et différents pour l'année suivante, par exemple une meilleure organisation du temps de révision et la recherche d'aide auprès des professeurs), et une formule de clôture chaleureuse suivie de la signature. Un candidat doit rédiger cette lettre intégralement en anglais, dans la fourchette de 250 à 300 mots, en veillant à exploiter toutes les données fournies par la consigne (le lien de cousinage, l'échec à l'examen, la préparation de l'année suivante)."),
    ],
    synthese=[
        "Une lettre personnelle respecte toujours quatre éléments de présentation : adresse de l'expéditeur, formule d'appel, corps structuré, formule de clôture avec signature.",
        "Adapte le registre et la formule de clôture au lien avec le destinataire : chaleureux pour un proche, cérémonieux seulement pour un inconnu ou une autorité.",
        "Exploite systématiquement toutes les données fournies par le sujet (nom, adresse, lien de parenté, éléments de contexte) dans ta lettre.",
        "Chaque problème ou point mentionné dans la mise en situation mérite un conseil distinct et clairement développé, pas une réponse générique.",
        "La lettre personnelle est l'un des trois formats de production écrite testés au BAC anglais, à ne jamais confondre avec la lettre formelle administrative.",
    ],
)))

print("cours 1-13 (FULL) built:", len(courses))

# =====================================================================
# SKELETON COURSES (12 total)
# =====================================================================
skeletons = [
    ("cours_fonctions-communicatives-de-base-en-anglais-2.json",
     skeleton_course("cours_fonctions-communicatives-de-base-en-anglais-2",
                      "Fonctions communicatives de base en anglais (situational language)",
                      "1", "rdm-bac-c-d-anglais-2012-cameroun-ex1-q1b-0")),
    ("cours_fonctions-communicatives-de-base-en-anglais-3.json",
     skeleton_course("cours_fonctions-communicatives-de-base-en-anglais-3",
                      "Fonctions communicatives de base en anglais (situational language)",
                      "1", "rdm-bac-c-d-anglais-2012-cameroun-ex1-q1c-0")),
    ("cours_fonctions-communicatives-de-base-en-anglais-4.json",
     skeleton_course("cours_fonctions-communicatives-de-base-en-anglais-4",
                      "Fonctions communicatives de base en anglais (situational language)",
                      "1", "rdm-bac-c-d-anglais-2012-cameroun-ex1-q1d-0")),
    ("cours_fonctions-communicatives-de-base-en-anglais-5.json",
     skeleton_course("cours_fonctions-communicatives-de-base-en-anglais-5",
                      "Fonctions communicatives de base en anglais (situational language)",
                      "1", "rdm-bac-c-d-anglais-2012-cameroun-ex1-q1e-0")),

    ("cours_choix-lexical-approprie-en-contexte-2.json",
     skeleton_course("cours_choix-lexical-approprie-en-contexte-2",
                      "Choix lexical approprié en contexte (vocabulary in context)",
                      "2", "rdm-bac-c-d-anglais-2012-cameroun-ex2-q1b-0")),
    ("cours_choix-lexical-approprie-en-contexte-3.json",
     skeleton_course("cours_choix-lexical-approprie-en-contexte-3",
                      "Choix lexical approprié en contexte (vocabulary in context)",
                      "2", "rdm-bac-c-d-anglais-2012-cameroun-ex2-q1c-0")),
    ("cours_choix-lexical-approprie-en-contexte-4.json",
     skeleton_course("cours_choix-lexical-approprie-en-contexte-4",
                      "Choix lexical approprié en contexte (vocabulary in context)",
                      "2", "rdm-bac-c-d-anglais-2012-cameroun-ex2-q1d-0")),
    ("cours_choix-lexical-approprie-en-contexte-5.json",
     skeleton_course("cours_choix-lexical-approprie-en-contexte-5",
                      "Choix lexical approprié en contexte (vocabulary in context)",
                      "2", "rdm-bac-c-d-anglais-2012-cameroun-ex2-q1e-0")),

    ("cours_comprehension-ecrite-reperer-et-reformuler-linformation-2.json",
     skeleton_course("cours_comprehension-ecrite-reperer-et-reformuler-linformation-2",
                      "Compréhension écrite : repérer et reformuler l'information (reading comprehension)",
                      "3", "rdm-bac-c-d-anglais-2012-cameroun-ex3-q2-0")),
    ("cours_comprehension-ecrite-reperer-et-reformuler-linformation-3.json",
     skeleton_course("cours_comprehension-ecrite-reperer-et-reformuler-linformation-3",
                      "Compréhension écrite : repérer et reformuler l'information (reading comprehension)",
                      "3", "rdm-bac-c-d-anglais-2012-cameroun-ex3-q3-0")),
    ("cours_comprehension-ecrite-reperer-et-reformuler-linformation-4.json",
     skeleton_course("cours_comprehension-ecrite-reperer-et-reformuler-linformation-4",
                      "Compréhension écrite : repérer et reformuler l'information (reading comprehension)",
                      "3", "rdm-bac-c-d-anglais-2012-cameroun-ex3-q4-0")),
    ("cours_comprehension-ecrite-reperer-et-reformuler-linformation-5.json",
     skeleton_course("cours_comprehension-ecrite-reperer-et-reformuler-linformation-5",
                      "Compréhension écrite : repérer et reformuler l'information (reading comprehension)",
                      "3", "rdm-bac-c-d-anglais-2012-cameroun-ex3-q5-0")),
]

all_courses = courses + skeletons
print("TOTAL courses (full+skeleton):", len(all_courses))

for fname, data in all_courses:
    path = os.path.join(OUT_DIR, f"{EPREUVE}_{fname}")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print("All course files written.")

# quick verbatim self-check for exemple_resolu / regle fields not required,
# but verify cours_id matches filename convention
for fname, data in all_courses:
    expected_suffix = fname.replace(".json", "")
    assert data["cours_id"] == expected_suffix, f"cours_id mismatch: {data['cours_id']} vs {expected_suffix}"
print("cours_id / filename consistency OK")

