r"""Questions de l'epreuve inedite GCE O Level English Language Paper 1 n.1 (50 QCM). Voir generer_english_p1.py.

Structure copiee des 5 vrais Paper 1 (2021, 2023-2026, mesures le 2026-10-20) : A ecoute 1-10 (un texte lu une fois, trois parties), B lecture 11-25
(un texte), C grammaire 26-40, D vocabulaire 41-50. Les textes et toutes les questions sont ORIGINAUX (aucun theme, personnage ni phrase d'un vrai sujet).

Q(id, theme, difficulte, enonce, bonne option, 3 distracteurs, rappel, resolution, piege, conseil, preuve, complete).
`preuve` : phrase EXACTE du texte qui justifie la cle (verifiee mot pour mot par verifier_reponses_english_p1.py) ; `complete` : la phrase entiere avec la bonne
option, comparee a l'enonce rempli. Toutes les chaines sont BRUTES (r"...").
"""

PREFIXE = "O Level English - "

SECTION_A = "Listening comprehension"

LISTENING = r"""**A Talk and a Story**

**Section One**

Good morning, class. I want to talk to you about money, because the long holidays are near and many of you will help in your parents' shops or sell small things by the roadside. Saving is not about how much you earn. A boy who earns five hundred francs a day and keeps one hundred of it will have more at the end of the month than a boy who earns two thousand francs and spends it all by evening. The first rule is to decide, before you receive the money, how much you will set aside. The second rule is to keep that part where you cannot reach it easily. A small tin under the bed is too easy to open, so ask a trusted adult or a savings group to keep it for you. The third rule is to write down what you spend, because most people are surprised to learn where their money goes. Finally, remember that saving is a habit. Begin with a small amount and be faithful to it; the habit matters more than the first sum.

**Section Two**

Tabe sold roasted groundnuts at the bus park in Bafoussam. One Saturday, a tired traveller bought a small bag, paid with a ten-thousand-franc note and hurried to catch his bus before Tabe could give him his change. Tabe ran after him, calling, but the engine roared and the bus pulled away. He stood for a long time with the note in his hand and the smell of diesel in his nose. Ten thousand francs was more than he earned in a week. A voice inside him whispered, "Nobody saw. Keep it." Yet when he reached home, his grandmother noticed that he ate nothing. "Something is troubling you more than hunger," she said. Tabe told her everything.

**Section Three**

On the next market day, Tabe's grandmother sent him to the bus park with the note folded in his pocket. Every Saturday for a month he looked for the traveller, who never came. In the fifth week the same man stepped off a bus, looking tired and worried, and was surprised to see the boy running towards him. "You left this with me," said Tabe, holding out the note. The man stared at him, then at the note, and finally laughed with relief. He pushed two thousand francs into Tabe's hand and ordered ten bags of groundnuts for his family. From that day he stopped at Tabe's tray each time he passed through the town, and other travellers, hearing the story, did the same. Tabe's tray was never empty again."""

READING = r"""**The Day the Bridge Went Down**

(1) By the time the last bell rang that Thursday, the sky over Wum had turned the colour of a wet slate. Teacher Ayuk warned us to go straight home, but my sister Ma'a, who was nine and believed that rules were for other children, insisted on stopping to buy roasted plantain at Mami Beri's stall. By the time we left the junction, the first drops were already as heavy as pebbles.

(2) Our house stands on the far side of the Mbah stream, which on ordinary days is a cheerful trickle that a goat can cross without wetting its belly. We reached it to find a different creature altogether. The water had swollen to the colour of strong tea and growled between its banks like an old man refusing to share his seat. The wooden footbridge, three planks tied with creeper, shivered under the current. I held Ma'a's hand and stepped forward, only to hear a crack like a gunshot. The middle plank snapped, and the whole bridge folded quietly into the water as though it had been waiting for permission.

(3) We stood frozen. Ma'a, to my surprise, said nothing; she only squeezed my hand until my fingers went numb. Then, through the rain, I heard someone laughing. It was Pa Nkeng, our neighbour, who had retired from the council seven years before and who, according to my mother, had opinions on everything and a solution to none. He was sitting under a plastic sheet on the opposite bank, calmly eating groundnuts.

(4) "You children have chosen a fine afternoon for a swim," he shouted. "Do not move! The water will not wait for you, but it will be gone by dusk. Walk up the bank to the fallen kola tree. It has been there since the wind of March and has never been of any use to anyone. Today it will be." I did not trust a man who joked while we were in danger, but I had no better idea. We climbed the bank with the mud sucking at our shoes, found the huge trunk lying across the stream like a bridge built by a careless giant, and crossed on hands and knees, with Ma'a in front, muttering a prayer in two languages.

(5) When we reached the other side, Pa Nkeng handed each of us a handful of groundnuts as if we had come back from a festival. "Tell your mother," he said, "that the council will repair that bridge about the time the mango trees learn to sing." Then he laughed again, louder this time, and I realised that the man who made jokes in a storm had been more worried than he had let us see: his hands, I noticed, were shaking.

(6) At home my mother scolded us for being late, then hugged us until I could hardly breathe. That night, with the rain drumming on the zinc roof, Ma'a whispered from her mat, "Next time, I will buy my plantain on a dry day." I lay awake smiling at the sentence, and at the memory of a kola tree that had waited three months to be useful."""

INTRO_B = r"**Read the passage below carefully and answer questions 11 to 25.**"
INTRO_A = (
    r"**Listening passage.** In the real examination the examiner reads this passage aloud once. Read it once, then answer questions 1 to 10."
)
SECTION_C = r"**Section C - Grammar.** For questions 26 to 40, choose the best answer to complete each sentence."
SECTION_D1 = r"**Section D - Vocabulary.** For questions 41 to 46, choose the answer that best completes each sentence."
SECTION_D2 = (
    r"**For questions 47 and 48, choose the answer that best explains the meaning of the word in bold.**"
)
SECTION_D3 = r"**For questions 49 and 50, choose the answer that gives the opposite of the word in bold.**"

RAPPELS = {
    "ecoute": r"In a listening test, read the question first, then follow the speaker's words: the right option says what was said or what the words clearly suggest, never what merely sounds likely in real life.",
    "lecture_detail": r"In a reading comprehension question about a detail, find the sentence in the passage that answers it and compare each option with that sentence word for word; the correct option is the one the text supports.",
    "lecture_inference": r"An inference question asks what the passage suggests without stating it: collect the clues in the text, then choose the option that all the clues support and that no sentence contradicts.",
    "contexte": r"To find the meaning of a word in context, read the sentence around it, test each option in place of the word, and keep the one that fits both the meaning and the grammar of the sentence.",
    "figures": r"A simile compares two things using like or as, a metaphor states that one thing is another, and an oxymoron joins two opposite ideas; name the device by looking at the exact words used.",
    "classes": r"A word class is decided by the job the word does in its sentence: a word that tells how, when or where an action happens is an adverb, and one that describes a noun is an adjective.",
    "temps": r"Choose the verb form from the time words in the sentence: since and for with a situation that continues up to now need the present perfect, a finished past time needs the simple past.",
    "conditionals": r"After unless, if not or when a future result is promised, the verb in the condition stays in the present tense, while the result clause uses will or can.",
    "pronouns": r"After a preposition or a verb, use the object pronoun (me, him, her, us, them); use the subject pronoun (I, he, she, we, they) only when the pronoun is the subject of a verb.",
    "accord": r"The verb agrees with the head noun of the subject, not with the noun nearest to it: in a phrase like the list of books, the head noun is list.",
    "prepositions": r"Many adjectives and verbs keep one fixed preposition (allergic to, good at, afraid of); learn them as pairs because no rule gives the right choice.",
    "connecteurs": r"A connector must fit the logic of the two ideas it joins: although and in spite of introduce a contrast, because and since give a cause, so introduces a result.",
    "adverbes": r"An adverb of manner modifies a verb and usually ends in -ly; an adjective cannot do this job, and a noun cannot either.",
    "tags": r"A question tag repeats the auxiliary of the statement with the opposite polarity; the fixed forms are let's... shall we and the imperative... will you.",
    "indirect": r"When direct speech becomes reported speech after a past reporting verb, the tense moves back (will becomes would, can becomes could) and time words change (tomorrow becomes the next day).",
    "passif": r"To make a passive sentence, move the object to the subject position and use the matching form of be with the past participle; the tense of be stays the tense of the active verb.",
    "possessifs": r"A plural noun that does not end in -s takes 's to show ownership (children's), whereas a regular plural takes only the apostrophe (girls').",
    "ordre_adj": r"Adjectives before a noun follow a fixed order: opinion, size, age, shape, colour, origin, material, then the noun.",
    "pluriels": r"Nouns ending in -f or -fe often change to -ves in the plural (thief, thieves); learn the common exceptions and irregular plurals one by one.",
    "ponctuation": r"A relative clause that only adds extra information is closed off with commas on both sides; a clause that identifies the noun takes no commas.",
    "phrasal": r"A phrasal verb is a verb plus a particle with a new meaning: called off means cancelled, while the same verb with another particle means something different.",
    "lexique": r"For a vocabulary question, test each option in the sentence for meaning and for the words it normally keeps company with, and drop options that are close in sound but different in meaning.",
    "confusables": r"Affect is a verb meaning to influence; effect is a noun meaning a result; many pairs of similar words differ in their word class as well as in their meaning.",
    "formation": r"A suffix changes the word class of a base word: -ness turns an adjective into a noun (kind, kindness), while -ity, -ment and -ance attach to other kinds of base.",
    "idiomes": r"An idiom has a fixed meaning that cannot be read word for word; learn it with its meaning and test the options against what the speaker actually says.",
    "synonymes": r"A synonym replaces the word without changing the meaning of the sentence; test each option in the sentence and eliminate the ones that change the meaning.",
    "antonymes": r"An antonym is the word with the opposite meaning in the same context: first define the word in bold, then pick the option that says the reverse.",
}


def _n(t):
    """Dans une chaine BRUTE, un guillemet precede d'un antislash garde l'antislash : on le retire (les guillemets droits sont permis dans un QCM)."""
    return t.replace(chr(92) + chr(34), chr(34)) if isinstance(t, str) else t


def Q(qid, theme, diff, stem, ok, bad, rappel, sol, piege=None, conseil=None, preuve=None, complete=None, extra=None):
    themes = [PREFIXE + theme] + [PREFIXE + t for t in (extra or [])]
    return dict(id=qid, themes=themes, diff=diff, stem=_n(stem), ok=_n(ok), bad=[_n(b) for b in bad], rappel=RAPPELS[rappel], sol=_n(sol),
                piege=_n(piege), conseil=_n(conseil), preuve=preuve, complete=complete)


def questions():
    q = []
    a = q.append
    BL = r"\_\_\_\_\_\_"
    PA = "(Listening passage in question 1, "
    PB = "(Reading passage, questions 11 to 25) "

    # ---------------------------------------------------------------- Section A : listening comprehension (Section One, questions 1-4)
    a(Q("e01", "listening comprehension", "faible",
        INTRO_A + "\n\n" + LISTENING + "\n\n**Questions 1 to 4 (Section One)**\n\nIn this talk, the speaker is mainly advising the students on " + BL + ".",
        r"how to keep part of the money they receive",
        [r"how to earn more money during the holidays", r"how to open a small shop by the roadside", r"how to ask adults for pocket money"],
        "ecoute",
        r"The talk opens with the holidays and money, then insists that saving is not about how much you earn and gives three rules for keeping part of what you receive. The advice is therefore about keeping money, not about earning more or asking for more.",
        r"Earning more or selling things by the roadside is mentioned only as the situation of the students, not as the advice given.",
        None, r"Saving is not about how much you earn."))
    a(Q("e02", "listening comprehension", "faible",
        PA + r"Section One) According to the speaker, the boy who earns five hundred francs a day may end the month with more money because he " + BL + ".",
        r"keeps a part of what he earns",
        [r"works longer hours than the other boy", r"sells more goods in the market", r"never buys anything for himself"],
        "ecoute",
        r"The speaker compares two boys: one earns five hundred francs a day and keeps one hundred of it, the other earns two thousand francs and spends it all by evening. The first boy ends the month with more because he keeps part of his earnings.",
        r"Do not choose the option about working longer or selling more: the speaker says nothing about hours or goods, only about keeping or spending.",
        None, r"keeps one hundred of it"))
    a(Q("e03", "listening comprehension", "faible",
        PA + r"Section One) The speaker says that a small tin under the bed is a poor place for savings because " + BL + ".",
        r"it is too easy to open",
        [r"visitors might find it", r"it is too small for notes", r"rats could damage the money"],
        "ecoute",
        r"The second rule says to keep the money where you cannot reach it easily, and the tin is rejected because it is too easy to open.",
        r"Each wrong option is a worry a listener might add by themselves (visitors, size, rats); only the reason given in the talk counts.",
        None, r"too easy to open"))
    a(Q("e04", "listening comprehension", "moyenne",
        PA + r"Section One) In the talk, the expression \"be faithful to it\" means " + BL + ".",
        r"keep on doing it regularly",
        [r"tell everyone about it", r"be proud of the first sum", r"be careful not to lose it"],
        "contexte",
        r"The speaker is talking about the habit of saving: begin with a small amount and be faithful to it, because the habit matters more than the first sum. To be faithful to the habit is to keep on doing it.",
        r"The word faithful is often linked to honesty or religion; here it describes loyalty to a plan, as the sentence about the habit shows.",
        None, r"be faithful to it", extra=["vocabulary in context"]))

    # ---------------------------------------------------------------- Section Two (questions 5-7)
    a(Q("e05", "listening comprehension", "faible",
        PA + r"Section Two) Tabe ran after the traveller because " + BL + ".",
        r"he had not yet given the traveller his change",
        [r"the traveller had forgotten his luggage", r"he wanted to sell the traveller more groundnuts", r"the bus driver had asked him to call the traveller"],
        "ecoute",
        r"The traveller hurried to catch his bus before Tabe could give him his change, so Tabe ran after him with the money he still owed.",
        r"A traveller who hurries away may seem to have forgotten something, but the text names the change as the reason.",
        None, r"before Tabe could give him his change"))
    a(Q("e06", "listening comprehension", "moyenne",
        PA + r"Section Two) The word \"whispered\" in \"A voice inside him whispered\" shows that the voice was " + BL + ".",
        r"tempting him in a quiet way",
        [r"shouting a warning to him", r"praising him for his work", r"scolding him for running"],
        "contexte",
        r"A whisper is quiet and private. The voice says that nobody saw and tells him to keep the note, so it is quietly tempting him to do wrong.",
        r"Do not read the voice as a warning: a warning would tell him to avoid the danger, while this voice tells him to keep what is not his.",
        None, r"A voice inside him whispered", extra=["vocabulary in context"]))
    a(Q("e07", "listening comprehension", "faible",
        PA + r"Section Two) Tabe's grandmother knew that he was troubled because he " + BL + ".",
        r"did not eat his food",
        [r"spoke loudly all evening", r"came home very late", r"refused to go to the bus park"],
        "ecoute",
        r"When he reached home, his grandmother noticed that he ate nothing, and she said that something was troubling him more than hunger.",
        r"Only the loss of appetite is reported; coming home late and speaking loudly are not mentioned.",
        None, r"his grandmother noticed that he ate nothing"))

    # ---------------------------------------------------------------- Section Three (questions 8-10)
    a(Q("e08", "listening comprehension", "moyenne",
        PA + r"Section Three) The man was surprised to see Tabe running towards him. This suggests that the man " + BL + ".",
        r"had not expected to see Tabe again",
        [r"had been waiting for Tabe at the bus park", r"was angry that the boy had come to the bus park", r"wanted to buy more groundnuts from him"],
        "ecoute",
        r"Surprise comes from the unexpected. Tabe had looked for him for four weeks and he never came, so the man had no reason to think the boy was waiting with his note; he did not expect to meet Tabe again.",
        r"Waiting for Tabe or being angry would not make him surprised, and the wish to buy groundnuts comes only later, after Tabe returns the note.",
        None, r"was surprised to see the boy running towards him"))
    a(Q("e09", "listening comprehension", "faible",
        PA + r"Section Three) The expression \"laughed with relief\" suggests that the man was " + BL + ".",
        r"glad that his money was safe",
        [r"amused by the way Tabe was dressed", r"angry that Tabe had made him wait", r"ashamed that others were watching him"],
        "ecoute",
        r"Relief is the feeling that a worry has gone. The man had left a ten-thousand-franc note behind, so his laugh shows gladness that the money was safe.",
        r"Laughter does not always mean amusement; the word relief shows which feeling is meant.",
        None, r"laughed with relief"))
    a(Q("e10", "listening comprehension", "moyenne",
        PA + r"Section Three) The best lesson of the story is that " + BL + ".",
        r"honest behaviour can bring lasting rewards",
        [r"travellers often forget their change", r"it is wiser to avoid strangers at a bus park", r"hard work is more useful than honesty"],
        "ecoute",
        r"Tabe resisted the temptation to keep the note and returned it. The man rewarded him and sent customers his way, so his tray was never empty again. The story teaches that honest behaviour is rewarded for a long time.",
        r"The first wrong option is a detail of the story, not its lesson, and the last one is contradicted by the ending.",
        r"Ask what happens to the main character because of his choice: the answer is usually the lesson.",
        r"Tabe's tray was never empty again."))

    # ---------------------------------------------------------------- Section B : reading comprehension (questions 11-25)
    a(Q("e11", "reading comprehension", "faible",
        INTRO_B + "\n\n" + READING + "\n\n**Questions 11 to 25**\n\nThe narrator and his sister reached home late because " + BL + ".",
        r"Ma'a insisted on stopping to buy plantain",
        [r"their teacher kept them back in class", r"the bridge had already fallen when they left school", r"they lost their way in the rain"],
        "lecture_detail",
        r"Paragraph 1 says that Ma'a insisted on stopping to buy roasted plantain at a stall, although the teacher had told the pupils to go straight home.",
        r"The teacher actually told them to go home straight away, and the bridge falls later in the passage.",
        None, r"insisted on stopping to buy roasted plantain"))
    a(Q("e12", "reading comprehension", "faible",
        PB + r"In paragraph 1, the phrase \"the colour of a wet slate\" tells the reader that the sky was " + BL + ".",
        r"dark and grey",
        [r"bright and clear", r"red and golden", r"white with thin clouds"],
        "contexte",
        r"A wet slate is a dark grey stone, and the paragraph goes on to speak of heavy drops of rain, so the sky was dark and grey.",
        None, None, r"the colour of a wet slate", extra=["vocabulary in context"]))
    a(Q("e13", "reading comprehension", "faible",
        PB + r"According to paragraph 2, on ordinary days the Mbah stream is " + BL + ".",
        r"small and harmless",
        [r"dangerous even to goats", r"completely dry", r"always as dark as tea"],
        "lecture_detail",
        r"Paragraph 2 calls it a cheerful trickle that a goat can cross without wetting its belly, so on ordinary days it is small and harmless.",
        r"The colour of strong tea belongs to the stream in flood, not to its ordinary state.",
        None, r"a cheerful trickle that a goat can cross"))
    a(Q("e14", "reading comprehension", "moyenne",
        PB + r"In paragraph 2, the stream is said to growl \"like an old man refusing to share his seat\". This comparison is a " + BL + ".",
        r"simile",
        [r"metaphor", r"oxymoron", r"proverb"],
        "figures",
        r"The comparison uses the word like to link the growling stream with an old man, so it is a simile. A metaphor would say that the stream was an old man, with no link word.",
        r"Many learners call every comparison a metaphor; the word like is the sign of a simile.",
        r"Look for like or as before you decide on the device.",
        r"like an old man refusing to share his seat", extra=["figures of speech"]))
    a(Q("e15", "reading comprehension", "moyenne",
        PB + r"In paragraph 2, the words \"folded quietly into the water\" suggest that the bridge " + BL + ".",
        r"gave way without any struggle",
        [r"was lifted carefully out of the stream", r"floated away upright", r"was repaired by the current"],
        "contexte",
        r"To fold is to bend and give way, and quietly adds that nothing resisted. The bridge gave way without any struggle, as if it had been waiting for permission.",
        r"Folded and floated are both soft words, but only folded suggests collapse.",
        None, r"folded quietly into the water", extra=["vocabulary in context"]))
    a(Q("e16", "reading comprehension", "faible",
        PB + r"In paragraph 3, Ma'a squeezed her brother's hand until his fingers went numb because she was " + BL + ".",
        r"frightened",
        [r"excited", r"angry with him", r"tired of walking"],
        "lecture_inference",
        r"The children stood frozen in front of the broken bridge and Ma'a, who usually spoke freely, said nothing. A tight grip with silence shows fear.",
        None, None, r"squeezed my hand until my fingers went numb"))
    a(Q("e17", "reading comprehension", "moyenne",
        PB + r"According to the narrator's mother, Pa Nkeng " + BL + ".",
        r"gave opinions on everything but rarely solved a problem",
        [r"had solved every problem in the village", r"never gave an opinion in public", r"was a retired teacher"],
        "lecture_detail",
        r"The passage reports that he had opinions on everything and a solution to none, which means he gave opinions on everything but rarely solved a problem.",
        r"Pa Nkeng retired from the council, not from teaching, and the mother's remark is the opposite of the first wrong option.",
        None, r"had opinions on everything and a solution to none"))
    a(Q("e18", "reading comprehension", "faible",
        PB + r"The word \"calmly\" in paragraph 3 is used as a/an " + BL + ".",
        r"adverb",
        [r"noun", r"adjective", r"verb"],
        "classes",
        r"Calmly describes how Pa Nkeng was eating, so it modifies the verb and is an adverb. The ending -ly is a clue, though the job of the word is what decides.",
        None, None, r"calmly eating groundnuts", extra=["reading comprehension"]))
    a(Q("e19", "reading comprehension", "moyenne",
        PB + r"Pa Nkeng's advice about the fallen kola tree shows that he was " + BL + ".",
        r"resourceful",
        [r"forgetful", r"unkind", r"dishonest"],
        "lecture_inference",
        r"Pa Nkeng saw that a tree which had lain by the stream for months could serve as a bridge, and he told the children exactly where to find it. Finding a use for what is at hand is being resourceful.",
        r"His jokes may look unkind at first, but he helps the children cross; he is neither forgetful nor dishonest.",
        None, r"Walk up the bank to the fallen kola tree."))
    a(Q("e20", "reading comprehension", "moyenne",
        PB + r"At first the narrator did not trust Pa Nkeng because he " + BL + ".",
        r"made jokes while the children were in danger",
        [r"had once told them a lie", r"lived on the far side of the stream", r"was a stranger to the family"],
        "lecture_detail",
        r"Paragraph 4 says the narrator did not trust a man who joked while they were in danger, but he had no better idea.",
        r"Pa Nkeng is a neighbour, so he is not a stranger, and no earlier lie is mentioned.",
        None, r"I did not trust a man who joked while we were in danger"))
    a(Q("e21", "reading comprehension", "faible",
        PB + r"The children crossed the stream " + BL + ".",
        r"on a fallen tree",
        [r"on a rope tied by Pa Nkeng", r"in a borrowed canoe", r"by walking through shallow water"],
        "lecture_detail",
        r"They found the huge trunk lying across the stream and crossed on hands and knees.",
        None, None, r"crossed on hands and knees"))
    a(Q("e22", "reading comprehension", "elevee",
        PB + r"Pa Nkeng says that the council will repair the bridge \"about the time the mango trees learn to sing\". This means that the repair " + BL + ".",
        r"will probably never be done",
        [r"will be finished by the evening", r"will start in the mango season", r"will be done by the villagers"],
        "lecture_inference",
        r"Mango trees cannot learn to sing, so the time he names will never come. Pa Nkeng is saying, with a joke, that the council will not repair the bridge.",
        r"A time-word such as season misleads: the phrase belongs to a joke about something impossible.",
        r"When a speaker names an impossible event as the time, he means never.",
        r"about the time the mango trees learn to sing"))
    a(Q("e23", "reading comprehension", "moyenne",
        PB + r"The narrator realised that Pa Nkeng had been worried because " + BL + ".",
        r"his hands were shaking",
        [r"he stopped laughing at once", r"he shouted at the children", r"he gave them food to eat"],
        "lecture_inference",
        r"The narrator says that the man who made jokes in a storm had been more worried than he had let them see, and he gives the proof: the man's hands were shaking.",
        r"He actually laughed again, louder, and the food was a handful of groundnuts; neither shows worry.",
        None, r"his hands, I noticed, were shaking"))
    a(Q("e24", "reading comprehension", "moyenne",
        PB + r"Which of the following best describes the writer's attitude throughout the passage?",
        r"light-hearted but touched with concern",
        [r"gloomy and bitter", r"angry and critical", r"formal and distant"],
        "lecture_inference",
        r"The writer uses jokes, comparisons and Pa Nkeng's humour throughout, yet the danger at the stream and the shaking hands show real concern. The tone is light-hearted but touched with concern.",
        r"The danger could suggest a gloomy tone, but the humour of the narration and the happy ending rule it out.",
        None, None))
    a(Q("e25", "reading comprehension", "faible",
        PB + r"Which of the following is the most suitable title for the passage?",
        r"The Day an Idle Tree Became a Bridge",
        [r"A Meeting of the Village Council", r"How Pa Nkeng Lost His Groundnuts", r"Ma'a Learns to Swim"],
        "lecture_detail",
        r"A good title covers the whole passage: the bridge falls, and a tree that had been of no use to anyone saves the children. The first option names both the tree and the bridge.",
        r"The council, the groundnuts and swimming are small details or events that never happen.",
        None, None))

    # ---------------------------------------------------------------- Section C : grammar (questions 26-40)
    a(Q("e26", "verb tenses", "faible",
        SECTION_C + "\n\nMy cousin " + BL + " in Douala since he left school.",
        r"has lived", [r"lived", r"is living", r"lives"],
        "temps",
        r"Since he left school marks a period that began in the past and still continues, so the present perfect has lived is needed.",
        r"The simple past lived would suit a finished time such as last year, but since points to the present.",
        None, None, r"My cousin has lived in Douala since he left school."))
    a(Q("e27", "conditionals", "faible",
        r"Unless you " + BL + r" your homework, the teacher will not let you go out.",
        r"finish", [r"will finish", r"finished", r"would finish"],
        "conditionals",
        r"After unless, the verb stays in the present tense, and the result clause carries will: Unless you finish your homework, the teacher will not let you go out.",
        r"Will after unless is a common slip: the future is expressed in the result clause only.",
        None, None, r"Unless you finish your homework, the teacher will not let you go out."))
    a(Q("e28", "pronouns", "faible",
        r"The prize was shared between Ebot and " + BL + ".",
        r"me", [r"I", r"myself", r"mine"],
        "pronouns",
        r"After the preposition between, the object pronoun is needed, so the sentence is: The prize was shared between Ebot and me.",
        r"Many learners think that I sounds more polite; it is correct only as the subject of a verb.",
        None, None, r"The prize was shared between Ebot and me."))
    a(Q("e29", "subject-verb agreement", "moyenne",
        r"The list of required books " + BL + " pinned on the notice board.",
        r"is", [r"are", r"were", r"have been"],
        "accord",
        r"The head noun of the subject is list, which is singular, so the verb is singular: The list of required books is pinned on the notice board.",
        r"The nearest noun, books, is plural and pulls the verb towards are, but it is only part of the phrase that describes the list.",
        None, None, r"The list of required books is pinned on the notice board."))
    a(Q("e30", "prepositions", "faible",
        r"The little girl is allergic " + BL + " groundnut oil.",
        r"to", [r"of", r"with", r"against"],
        "prepositions",
        r"The adjective allergic keeps the preposition to: allergic to groundnut oil.",
        None, None, None, r"The little girl is allergic to groundnut oil."))
    a(Q("e31", "connectors", "moyenne",
        r"The match went on " + BL + " the heavy rain.",
        r"in spite of", [r"because of", r"instead of", r"owing to"],
        "connecteurs",
        r"The idea is a contrast: the rain could have stopped the match, but it did not. In spite of introduces that contrast, while the other options give a cause or a replacement.",
        r"Because of and owing to give a cause, which would mean that the rain made the match continue.",
        None, None, r"The match went on in spite of the heavy rain."))
    a(Q("e32", "adverbs", "faible",
        r"The pupils listened " + BL + " to the headmaster's warning.",
        r"attentively", [r"attentive", r"attention", r"attentiveness"],
        "adverbes",
        r"The word describes how the pupils listened, so an adverb is needed: attentively.",
        r"Attentive is an adjective and can describe the pupils, but it cannot describe the verb listened.",
        None, None, r"The pupils listened attentively to the headmaster's warning."))
    a(Q("e33", "question tags", "moyenne",
        r"Let's wait for the others, " + BL + "?",
        r"shall we", [r"will we", r"don't we", r"do we"],
        "tags",
        r"The statement begins with Let's, and the fixed tag for it is shall we.",
        r"Learners often build the tag from the apparent verb, giving don't we, but let's has its own tag.",
        None, None, r"Let's wait for the others, shall we?"))
    a(Q("e34", "reported speech", "moyenne",
        r"\"I will bring the books tomorrow,\" said Ndi. Ndi said that he " + BL + r" the books the next day.",
        r"would bring", [r"will bring", r"brings", r"had brought"],
        "indirect",
        r"The reporting verb said is in the past, so will moves back to would, and tomorrow becomes the next day: Ndi said that he would bring the books the next day.",
        r"Keeping will is a common slip; had brought would change the meaning to an earlier time.",
        None, None, r"Ndi said that he would bring the books the next day."))
    a(Q("e35", "passive voice", "moyenne",
        r"The cook is preparing the meal. In the passive, this becomes: The meal " + BL + " by the cook.",
        r"is being prepared", [r"is prepared", r"has been prepared", r"was being prepared"],
        "passif",
        r"The active verb is in the present continuous, so the passive uses the present continuous of be with the past participle: is being prepared.",
        r"Is prepared drops the continuous idea, and the other two options change the tense.",
        None, None, r"The meal is being prepared by the cook."))
    a(Q("e36", "possessives", "faible",
        r"The " + BL + " playground is next to the church.",
        r"children's", [r"childrens'", r"childrens's", r"children'"],
        "possessifs",
        r"Children is already plural without -s, so ownership is shown with 's: the children's playground.",
        r"Childrens' treats the word as if it were a regular plural; there is no -s to follow.",
        None, None, r"The children's playground is next to the church."))
    a(Q("e37", "adjective order", "moyenne",
        r"She wore a " + BL + " dress to the wedding.",
        r"beautiful long red cotton", [r"red long beautiful cotton", r"long beautiful cotton red", r"cotton beautiful long red"],
        "ordre_adj",
        r"The order is opinion (beautiful), size (long), colour (red) and material (cotton), then the noun: a beautiful long red cotton dress.",
        r"The other options put colour or material too early.",
        None, None, r"She wore a beautiful long red cotton dress to the wedding."))
    a(Q("e38", "plural nouns", "faible",
        r"The police arrested the " + BL + " at dawn.",
        r"thieves", [r"thiefs", r"thiefes", r"thieve"],
        "pluriels",
        r"Thief ends in -f, which changes to -v before -es in the plural: thieves.",
        None, None, None, r"The police arrested the thieves at dawn."))
    a(Q("e39", "spelling and punctuation", "moyenne",
        r"Which sentence is correctly punctuated?",
        r"My sister, who lives in Kumba, is a nurse.",
        [r"My sister who lives in Kumba, is a nurse.", r"My sister, who lives in Kumba is a nurse.", r"My sister who, lives in Kumba, is a nurse."],
        "ponctuation",
        r"The clause who lives in Kumba only adds extra information about my sister, so it is closed off by a comma before and a comma after.",
        r"Each wrong option leaves out one of the two commas or puts a comma in the wrong place.",
        r"Read the sentence aloud: the pauses fall where the commas belong.", None))
    a(Q("e40", "phrasal verbs", "moyenne",
        r"The meeting was " + BL + " because of the strike.",
        r"called off", [r"called on", r"called at", r"called up"],
        "phrasal",
        r"To call off an event is to cancel it, which is what a strike would cause: The meeting was called off because of the strike.",
        r"Called on and called up exist but mean to visit someone and to summon, and called at means to stop at a place.",
        None, None, r"The meeting was called off because of the strike."))

    # ---------------------------------------------------------------- Section D : vocabulary (questions 41-50)
    a(Q("e41", "vocabulary in context", "faible",
        SECTION_D1 + "\n\nThe headmaster " + BL + " the pupils for their excellent results.",
        r"commended", [r"condemned", r"commanded", r"commenced"],
        "lexique",
        r"To commend is to praise, which suits excellent results: The headmaster commended the pupils for their excellent results.",
        r"Condemned, commanded and commenced look like commended but mean to blame, to order and to begin.",
        None, None, r"The headmaster commended the pupils for their excellent results."))
    a(Q("e42", "vocabulary in context", "moyenne",
        r"The thief managed to " + BL + " the police by hiding among the market stalls.",
        r"evade", [r"invade", r"evacuate", r"evoke"],
        "lexique",
        r"To evade someone is to escape from them cleverly, which is what hiding from the police does.",
        r"Invade is close in spelling but means to enter by force, and evacuate means to leave a place.",
        None, None, r"The thief managed to evade the police by hiding among the market stalls."))
    a(Q("e43", "confusable words", "moyenne",
        r"The long drought had a serious " + BL + " on the maize harvest.",
        r"effect", [r"affect", r"infect", r"defect"],
        "confusables",
        r"After the article a and the adjective serious, a noun is needed, and the noun meaning a result is effect.",
        r"Affect is a verb, so it cannot follow a serious in this sentence.",
        None, None, r"The long drought had a serious effect on the maize harvest.", ))
    a(Q("e44", "vocabulary in context", "moyenne",
        r"The old man was too " + BL + " to climb the steep hill without a stick.",
        r"frail", [r"flimsy", r"rigid", r"stubborn"],
        "lexique",
        r"Frail describes a weak person, which fits a man who needs a stick for a steep hill.",
        r"Flimsy describes objects that break easily, and rigid and stubborn do not explain the need for a stick.",
        None, None, r"The old man was too frail to climb the steep hill without a stick."))
    a(Q("e45", "word formation", "faible",
        r"Her kind" + BL + " to strangers is known all over the village.",
        r"ness", [r"ity", r"ment", r"ance"],
        "formation",
        r"The sentence needs a noun made from the adjective kind, and the suffix that does this is -ness: kindness.",
        r"The suffixes -ity, -ment and -ance form nouns from other bases and do not fit kind.",
        None, None, r"Her kindness to strangers is known all over the village."))
    a(Q("e46", "idioms and proverbs", "moyenne",
        r"When the manager said that he was \"under the weather\", he meant that he was " + BL + ".",
        r"feeling ill", [r"late for work", r"standing in the rain", r"very angry"],
        "idiomes",
        r"The idiom under the weather means to feel unwell, so the manager was saying that he was ill.",
        r"The words suggest rain, but an idiom must be read as a whole and not word for word.",
        None, None, None))
    a(Q("e47", "synonyms and antonyms", "faible",
        SECTION_D2 + "\n\nThe farmer was **reluctant** to sell his land.",
        r"unwilling", [r"eager", r"afraid", r"forced"],
        "synonymes",
        r"Reluctant means not willing to do something, so unwilling keeps the meaning of the sentence.",
        r"Eager is the opposite, and afraid and forced change the meaning.",
        None, None, None, extra=["vocabulary in context"]))
    a(Q("e48", "synonyms and antonyms", "moyenne",
        r"The lawyer gave a **concise** summary of the case.",
        r"short and clear", [r"long and detailed", r"angry and loud", r"careless and quick"],
        "synonymes",
        r"A concise summary says much in few words, so short and clear is the closest meaning.",
        r"Long and detailed is the opposite of concise.",
        None, None, None, extra=["vocabulary in context"]))
    a(Q("e49", "synonyms and antonyms", "faible",
        SECTION_D3 + "\n\nThe river is very **shallow** at this point.",
        r"deep", [r"narrow", r"wide", r"muddy"],
        "antonymes",
        r"Shallow means not deep, so the opposite is deep.",
        r"Narrow and wide describe breadth, not depth, so they cannot be the opposite of shallow.",
        None, None, None))
    a(Q("e50", "synonyms and antonyms", "elevee",
        r"The manager's answer was **ambiguous**.",
        r"clear", [r"polite", r"short", r"rude"],
        "antonymes",
        r"Ambiguous means open to more than one meaning, so the opposite is clear: an answer that can be read only one way.",
        r"Polite, short and rude describe the manner or the length of an answer, not whether its meaning is clear.",
        r"Define the word in your own words first, then look for the option that says the reverse.", None))
    return q
