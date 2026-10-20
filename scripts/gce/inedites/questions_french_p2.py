r"""Contenu de l'epreuve inedite GCE O Level French Paper 2 n.1 (traduction et redaction). Voir generer_french_p2.py.

Structure copiee des 8 vrais Paper 2 (2019-2026 ; code 0545 ; mesures le 2026-10-20) : 80 points, deux questions egales. Question 1 = traduction de l'anglais vers le francais
(un texte de quatre paragraphes) ; Question 2 = une redaction en francais de 140 a 150 mots a choisir parmi TROIS sujets : (a) recit guide en trois points, (b) lettre avec nom et
adresse imposes (introduction de 20 mots au plus), (c) sujet fonde sur des images. La plateforme ne code pas les choix des inedites : la Question 2 est UNE question de 40 points qui
liste les sujets et dit « choose ONE », avec un modele pour CHAQUE sujet. Le sujet (c) a images est REMPLACE par un sujet guide sans images (pas d'images). Textes, sujets, noms et modeles
sont ORIGINAUX. Toutes les chaines sont BRUTES (r"..."). Les explications sont en anglais, le francais est en francais.
"""

PREFIXE = "O Level French - "

CONSIGNES_GENERALES = (
    r"**Paper 2 - Translation and composition (2 hours).** Answer both questions, beginning each answer on a new page in the answer booklet. Both answers carry equal marks "
    r"(Question 1: 40 marks; Question 2: 40 marks; total: 80 marks). Credit will be given for accuracy, correct use of a variety of expressions, verbs, vocabulary and idioms. "
    r"You are reminded of the necessity for orderly presentation of your answers."
)

# ------------------------------------------------------------------------------------------------------------------------------ Question 1
ENONCE_Q1 = (
    r"**QUESTION 1 - Translate into French (40 marks)**" "\n\n"
    r"> Many young people in our towns like listening to the radio in the evening. They follow the news, they dance to the music and they learn new words. "
    r"This habit helps them to speak better and to know what is happening in the country." "\n\n"
    r"> Last Saturday, my younger sister and I went to the market with our mother. It was raining and the road was muddy. We bought some tomatoes, onions and fish, "
    r"then we waited for a taxi for a long time. Unfortunately, nobody wanted to stop." "\n\n"
    r"> When we finally arrived home, we found that Father had already lit the fire. He had been waiting for us since noon. We were very tired but happy to see him." "\n\n"
    r"> After the meal, we thanked our mother for her patience and went to bed early."
)

MODELE_Q1 = (
    "Beaucoup de jeunes dans nos villes aiment écouter la radio le soir. Ils suivent les informations, ils dansent sur la musique et ils apprennent de nouveaux mots. "
    "Cette habitude les aide à mieux parler et à savoir ce qui se passe dans le pays.\n\n"
    "Samedi dernier, ma petite sœur et moi sommes allés au marché avec notre mère. Il pleuvait et la route était boueuse. Nous avons acheté des tomates, des oignons "
    "et du poisson, puis nous avons attendu un taxi longtemps. Malheureusement, personne ne voulait s'arrêter.\n\n"
    "Quand nous sommes enfin arrivés à la maison, nous avons constaté que Papa avait déjà allumé le feu. Il nous attendait depuis midi. Nous étions très fatigués, "
    "mais heureux de le voir.\n\n"
    "Après le repas, nous avons remercié notre mère de sa patience et nous sommes allés nous coucher tôt."
)

# (point du texte anglais, piege, bonne forme, extrait du modele qui contient la bonne forme : verifie mot pour mot)
POINTS_Q1 = [
    (r"\"like listening\"", r"*aiment écoutant* or *aiment à écouter*", r"*aiment écouter* (verb + infinitive, no preposition)", "aiment écouter"),
    (r"\"in our towns\"", r"*en nos villes*", r"*dans nos villes*", "dans nos villes"),
    (r"\"in the evening\" (habit)", r"*dans le soir*", r"*le soir* (the article alone expresses a habit)", "le soir"),
    (r"\"dance to the music\"", r"*dansent à la musique*", r"*dansent sur la musique*", "dansent sur la musique"),
    (r"\"helps them to speak better\"", r"*aide eux à parler meilleur*", r"*les aide à mieux parler* (pronoun *les*, adverb *mieux*, not *meilleur*)", "les aide à mieux parler"),
    (r"\"what is happening\"", r"*quoi se passe* or *ce que se passe*", r"*ce qui se passe* (*ce qui* is the subject)", "ce qui se passe"),
    (r"\"Last Saturday\"", r"*Le samedi dernier* (a habit)", r"*Samedi dernier* (a single day, no article)", "Samedi dernier"),
    (r"\"It was raining\"", r"*Il a plu* (a completed action)", r"*Il pleuvait* (imparfait for the weather in the scene)", "Il pleuvait"),
    (r"\"waited for a taxi\"", r"*attendu pour un taxi*", r"*attendu un taxi* (attendre takes a direct object)", "attendu un taxi"),
    (r"\"nobody wanted to stop\"", r"*personne voulait s'arrêter* (no *ne*)", r"*personne ne voulait s'arrêter* (negation with *ne*; reflexive verb)", "personne ne voulait s'arrêter"),
    (r"\"had already lit the fire\"", r"*a déjà allumé* (no pluperfect)", r"*avait déjà allumé le feu* (plus-que-parfait with *avoir*)", "avait déjà allumé le feu"),
    (r"\"had been waiting for us since noon\"", r"*avait attendu pour nous depuis midi*", r"*nous attendait depuis midi* (imparfait with *depuis*)", "nous attendait depuis midi"),
    (r"\"thanked our mother for her patience\"", r"*remercié à notre mère*", r"*remercié notre mère de sa patience* (*remercier* takes a direct object; *pour sa patience* is also accepted)", "remercié notre mère de sa patience"),
    (r"\"went to bed\"", r"*nous avons allé nous coucher*", r"*nous sommes allés nous coucher* (*aller* takes *être*; the participle agrees with the subject)", "sommes allés nous coucher"),
    (r"\"very tired but happy\"", r"*fatigué* and *heureux* left in the singular", r"*fatigués* ... *heureux* (agreement with *nous*; the feminine *fatiguées*, *heureuses* is also accepted if the writer is a girl)", "très fatigués, mais heureux"),
]

NOTE_Q1 = (
    "**Marking note**\n\n"
    "The text is short, so every sentence counts. Credit goes to accuracy (tenses, agreements, accents) and to natural French rather than word-for-word translation. "
    "The writer's sex is not given, so *allés* or *allées*, *fatigués* or *fatiguées* are all accepted, provided the choice is the same throughout."
)
PIEGE_Q1 = (
    r"Do not leave out a sentence or part of a sentence (for example \"for a long time\" or \"for her patience\"): everything in the source must be translated. Do not use one tense "
    r"for the whole text: the general statements are in the present, the scene is described in the imparfait, the events are in the passé composé and what happened earlier is in the plus-que-parfait."
)
CONSEIL_Q1 = r"Read the whole English text first and mark the tense of each verb before you translate, then check each French verb against your marks at the end."
RAPPEL_Q1 = (
    r"To translate a text into French, translate sentence by sentence without leaving anything out, choose the tense from the time of each action (present for general facts, "
    r"imparfait for a scene or a state, passé composé for completed events, plus-que-parfait for what came before), and prefer natural French to a word-for-word version."
)
CRITERES_Q1 = [
    (r"You translate every sentence and every part of a sentence: nothing is left out or added", 12),
    (r"You choose the right tenses: the present for general statements, the imparfait for the scene, the passé composé for the events and the plus-que-parfait for what came earlier", 10),
    (r"Your agreements, articles, pronouns and negations are correct", 10),
    (r"Your French is natural: vocabulary, prepositions and expressions are not translated word for word", 8),
]

# ------------------------------------------------------------------------------------------------------------------------------ Question 2
INTRO_Q2 = (
    r"**QUESTION 2 - Composition (40 marks)**" "\n\n"
    r"*Using a tense suitable to your chosen topic, write an essay in French, of at least 140 and not more than 150 words (not counting figures, words in brackets, abbreviations "
    r"and names of people or places), on ONE of the following topics. Do not write on more than one topic.*" "\n\n"
    r"*If you choose topic (b), the letter, your name must be NOELA and your address Collège de Foumban. Use of a different name and/or address will be seriously penalised. "
    r"The usual introduction to the letter must not be more than 20 words.*" "\n\n"
    r"*Credit will be given for the correct use of a variety of expressions, verbs, vocabulary and idioms. Off-topic material will earn no marks.*" "\n\n"
)

# lettre, sujet, temps choisis, modele, noms propres a ne pas compter, introduction de la lettre (non comptee), couverture : (point du sujet, extrait du modele qui le traite)
TOPICS = [
    dict(
        lettre="a",
        sujet=(
            "(a) Vous avez perdu votre sac pendant un voyage en car." "\n\n"
            "- Décrivez le voyage et dites comment vous avez découvert la perte ;" "\n"
            "- expliquez les démarches que vous avez entreprises pour retrouver votre sac ;" "\n"
            "- dites comment cette aventure s'est terminée."
        ),
        temps=(
            r"the passé composé for the events, with the imparfait to describe the journey and the state of the writer. A past tense is needed because the story is told after the events."
        ),
        modele=(
            "Le mois dernier, j'ai voyagé en car pour rendre visite à ma grand-mère. Le trajet était long et je me suis endormi près de la fenêtre. En arrivant à la gare, "
            "j'ai voulu prendre mon sac et j'ai compris qu'il avait disparu. Mon argent, mes vêtements et mon téléphone étaient dedans. J'étais désespéré et mon cœur battait très fort.\n\n"
            "Aussitôt, je suis allé voir le chef de gare et je lui ai décrit mon sac : il était bleu, avec une grande étiquette. Il a téléphoné au chauffeur, qui avait déjà "
            "quitté la ville. Pendant ce temps, j'ai fouillé tous les bancs de la gare.\n\n"
            "Une heure plus tard, le chauffeur est revenu avec mon sac. Un passager l'avait pris par erreur ! J'ai remercié tout le monde et j'ai promis de faire plus "
            "attention. Depuis ce jour, je garde toujours mes affaires sur mes genoux."
        ),
        noms=[], intro="",
        couverture=[("how the loss was discovered", "j'ai compris qu'il avait disparu"), ("what was done to find the bag", "je suis allé voir le chef de gare"),
                    ("how it ended", "le chauffeur est revenu avec mon sac")],
    ),
    dict(
        lettre="b",
        sujet=(
            "(b) Votre cousin Brice vient de réussir à son examen. Écrivez-lui une lettre pour le féliciter. Dans votre lettre :" "\n\n"
            "- dites ce que vous avez ressenti en apprenant la nouvelle ;" "\n"
            "- donnez-lui trois conseils pour la suite de ses études ;" "\n"
            "- proposez-lui une rencontre pour fêter son succès."
        ),
        temps=(
            r"the passé composé and the imparfait for what the writer felt on hearing the news, the present and the imperative for the advice, and the future for the visit. "
            r"The letter has a place and date, a salutation, a body and a closing formula, and it is signed *Noela* with the address *Collège de Foumban* as required."
        ),
        modele=(
            "Foumban, le 12 mai. Cher Brice,\n\n"
            "J'ai appris ta réussite à l'examen par ma mère et j'ai crié de joie. Je ne pouvais pas y croire : tu as tellement travaillé ! J'étais si fière de toi que j'ai "
            "raconté la nouvelle à toutes mes camarades. Ma mère a même préparé un gâteau pour célébrer ta victoire.\n\n"
            "Maintenant, je voudrais te donner trois conseils pour la suite de tes études. D'abord, garde le même rythme de travail et ne te relâche jamais. Ensuite, choisis une "
            "filière qui te plaît, car on réussit mieux ce qu'on aime. Enfin, n'hésite pas à demander de l'aide à tes professeurs quand tu ne comprends pas une leçon.\n\n"
            "Si tes parents sont d'accord, je viendrai te voir pendant les vacances et nous fêterons ton succès avec toute la famille. Nous irons aussi nous promener au bord du fleuve. Je t'apporterai un petit cadeau.\n\n"
            "Je t'embrasse très fort.\n\n"
            "Noela\nCollège de Foumban"
        ),
        noms=["Brice", "Noela", "Foumban", "Collège"], intro="Foumban, le 12 mai. Cher Brice,",
        couverture=[("what the writer felt", "j'ai crié de joie"), ("three pieces of advice", "D'abord, garde le même rythme de travail"),
                    ("a meeting to celebrate", "nous fêterons ton succès avec toute la famille")],
    ),
    dict(
        lettre="c",
        sujet=(
            "(c) Décrivez la dernière fête de fin d'année de votre école." "\n\n"
            "- Décrivez le lieu et les préparatifs ;" "\n"
            "- dites ce qui s'est passé pendant la fête ;" "\n"
            "- donnez l'importance de ce genre de fête."
        ),
        temps=(
            r"the passé composé for what happened during the party, the imparfait and the plus-que-parfait for the place and the preparations, and the present for the importance of such a party."
        ),
        modele=(
            "Vendredi dernier, notre école a organisé sa fête de fin d'année dans la grande cour. Pendant une semaine, les élèves avaient décoré les murs avec des dessins et des "
            "guirlandes colorées. Le jour de la fête, des chaises étaient alignées devant une scène et les parents arrivaient en grand nombre.\n\n"
            "La cérémonie a commencé par le discours du directeur. Ensuite, les élèves ont chanté, dansé et joué une petite pièce de théâtre très drôle. Les meilleurs élèves ont reçu des "
            "prix, et tout le monde les a applaudis longtemps. Le directeur a aussi remercié les parents pour leur soutien pendant l'année. À la fin, nous avons partagé un grand repas dans la cour.\n\n"
            "Ces fêtes sont importantes, car elles rapprochent les élèves, les parents et les professeurs. Elles nous permettent aussi de nous reposer avant les vacances et de "
            "garder de beaux souvenirs."
        ),
        noms=[], intro="",
        couverture=[("the place and the preparations", "avaient décoré les murs"), ("what happened during the party", "La cérémonie a commencé par le discours du directeur"),
                    ("the importance of such a party", "Ces fêtes sont importantes")],
    ),
]

CRITERES_Q2 = [
    (r"Your French is accurate: verb forms, agreements, spelling and accents are correct, and the tense you chose is used correctly", 16),
    (r"You use a variety of expressions: linking words (d'abord, ensuite, enfin, heureusement) and set phrases", 6),
    (r"You use a variety of verbs instead of être, avoir and faire only", 6),
    (r"Your vocabulary and idioms suit the topic and are used correctly", 6),
    (r"You cover all three bullet points, stay on the topic, and write between 140 and 150 words (and, for the letter, follow the layout and the name and address required)", 6),
]

GRILLE_Q2 = (
    "**Marking criteria**\n\n"
    "| Criterion | Marks | What earns the marks |\n|---|---|---|\n"
    "| Accuracy | 16 | Correct verb forms, agreements, spelling and accents; correct use of the tense chosen |\n"
    "| Variety of expressions | 6 | Linking words (*d'abord*, *ensuite*, *enfin*, *heureusement*) and set phrases |\n"
    "| Variety of verbs | 6 | Several different verbs instead of *être*, *avoir* and *faire* only |\n"
    "| Vocabulary and idioms | 6 | Words and expressions suited to the topic; idioms used correctly |\n"
    "| Relevance and length | 6 | All three bullet points covered; between 140 and 150 words |"
)
RAPPEL_Q2 = (
    r"In a French composition, choose one tense frame that suits the topic and keep it (passé composé for the events and imparfait for the description in a story), cover every bullet point "
    r"in its own paragraph, vary the linking words and the verbs, and keep to the word limit by counting before you hand in."
)
PIEGE_Q2 = (
    r"Do not mix the passé composé and the imparfait without a reason: events are in the passé composé and descriptions in the imparfait. Do not forget one of the three bullet points, "
    r"do not write fewer than 140 or more than 150 words, and for the letter do not use another name or address than the one required."
)
CONSEIL_Q2 = r"Write the three bullet points in the margin, give each one a paragraph, and count your words line by line before you copy the final version."

PREFIXE_THEME_A = "narrative essay"
