r"""Contenu de l'epreuve inedite GCE O Level English Language Paper 2 n.1 (redige). Voir generer_english_p2.py.

Structure copiee des 8 vrais Paper 2 (2019-2026, mesures le 2026-10-20) : Section A = ecriture dirigee (30 points : contenu 14, expression et correction 12,
orientation persuasive 4 ; un texte de 412 a 633 mots ; reponse en deux paragraphes d'au plus 150 mots) ; Section B = une composition de 40 points a choisir parmi
8 sujets a-h (contenu et organisation 12, expression 16, correction 12 ; modeles reels de 451 a 499 mots). Duree 2 heures.
La plateforme ne code pas les regles de choix des inedites : la Section B est UNE question de 40 points qui liste les sujets et dit « choose ONE », avec un
modele de composition pour CHAQUE sujet. Le sujet h (a partir d'images) est omis : pas d'images. Les textes, sujets, noms et modeles sont ORIGINAUX.
Toutes les chaines sont BRUTES (r"...").
"""

PREFIXE = "O Level English - "
LIMITE_A = 150

CONSIGNES_GENERALES = (
    r"**Paper 2 - Directed writing and composition (2 hours).** Answer BOTH sections in the same answer booklet, beginning each section on a new page. "
    r"Begin with SECTION A. You are reminded of the necessity for good English and orderly presentation in your answers. In the directed writing question, "
    r"avoid indiscriminate copying of portions of the passage as your answer, because this will earn you no marks. A pre-prepared or memorised composition "
    r"will earn you no marks. Total: 70 marks (Section A: 30 marks; Section B: 40 marks)."
)

# ------------------------------------------------------------------------------------------------------------------------------ Section A
TACHE_A = (
    r"**SECTION A - DIRECTED WRITING (30 marks)**" "\n\n"
    r"Mark distribution: Content (14 marks); Expression and Accuracy (12 marks); Slanting (04 marks)." "\n\n"
    r"You are the president of the Environment Club of your school and you are worried about the plastic waste that fills the streets of your town. "
    r"Selecting relevant material from the passage below, write a speech to be delivered to your fellow students on the causes of plastic waste in the town "
    r"and the steps that can be taken to reduce it. Your aim is to convince them to act, so choose a persuasive tone. Write in TWO paragraphs of not more than "
    r"**150 words**, paying attention to grammar, spelling, punctuation and handwriting."
)

PASSAGE_A = r"""**PLASTIC WASTE IN OUR TOWNS**

Walk along any gutter in a Cameroonian town after the first rains of April and you will see the same picture: a river of brown water carrying bottles, sachets and torn bags towards the nearest drain. Plastic is cheap, light and clean, and for that reason it has entered every market stall and every kitchen. A town the size of Bamenda now uses several tonnes of plastic every day, yet it has only a few places where the used material can be dumped.

Several habits explain the problem. Many sellers hand out a new bag with every purchase, even when the buyer carries only one small item. Water and juice are sold in sachets that cost almost nothing and are thrown away within minutes. In many neighbourhoods there are no public bins, so people drop waste where they stand or leave it at the roadside for a collection lorry that comes once a month, if it comes at all. Others have never been told that plastic does not rot: a bottle thrown into a field today will still be there when the thrower's grandchildren are old.

The consequences are visible. Blocked gutters turn every heavy rain into a flood that enters homes, damages roads and carries filth into wells and streams. Stagnant water in discarded containers becomes a breeding place for mosquitoes, and malaria cases rise. Goats and cows that eat plastic bags fall sick and die, and farmers lose their animals. When the heaps become too large, families burn them, and the black smoke, which contains harmful chemicals, makes children and old people cough. The cost of cleaning the town falls on the council, which means that the money is not spent on schools or health centres.

Plastic is made from oil through a long industrial process in which hydrocarbons are heated and shaped into polymers. Each type of plastic carries a small number inside a triangle, which tells recyclers how to treat it. Worldwide, millions of tonnes are produced every year, and only a small share is ever recycled.

Solutions exist, and some towns have already tried them. Shops that charge a small amount for each bag soon find that customers bring their own baskets. Neighbourhood groups can place drums as bins and agree on a day each week to sweep the street. Young people who collect bottles can sell them to small factories that melt them into new buckets and pipes, and in this way earn money while cleaning the town. Councils can fine those who dump waste in drains, but they must first provide bins and collection points, because a rule that cannot be obeyed only creates anger.

Schools also have a role. Pupils who learn to sort waste in the classroom carry the habit home, and parents often change when their children insist. In the end, a clean town does not depend on a single machine or law; it depends on millions of small decisions taken by ordinary people each day."""

MODELE_A = (
    "Fellow students, our town is drowning in plastic, and we are partly to blame. Shops give a new bag with every purchase, sachets are thrown away "
    "within minutes, and many streets have no bins. The lorry that should collect waste comes once a month, and some people still believe that plastic "
    "rots like leaves.\n\n"
    "We can change this. Let us carry our own baskets so that shops stop giving bags, place drums as bins in our neighbourhoods and sweep the street "
    "every week. Let us collect bottles and sell them to recyclers, and let the council fine dumpers only after providing collection points. Sorting "
    "waste at school will teach our parents too. Join the Environment Club this week, and let us clean our town together!"
)

# (point repris dans le modele, phrase du texte qui le fonde : verifiee mot pour mot)
POINTS_A = [
    ("a new bag with every purchase", "hand out a new bag with every purchase"),
    ("sachets are thrown away within minutes", "thrown away within minutes"),
    ("many streets have no bins", "there are no public bins"),
    ("lorry that should collect waste comes once a month", "a collection lorry that comes once a month"),
    ("plastic rots like leaves", "plastic does not rot"),
    ("carry our own baskets", "customers bring their own baskets"),
    ("drums as bins", "place drums as bins"),
    ("sweep the street every week", "a day each week to sweep the street"),
    ("sell them to recyclers", "sell them to small factories"),
    ("fine dumpers only after providing collection points", "they must first provide bins and collection points"),
    ("Sorting waste at school", "learn to sort waste in the classroom"),
]

POURQUOI_A = (
    r"**Why this works (selection and slanting).** The speech must give the CAUSES of plastic waste and the STEPS to reduce it, and it must convince "
    r"the audience to act. Paragraph one keeps the causes from the passage (a new bag with every purchase, sachets thrown away within minutes, no bins, "
    r"a lorry that comes once a month, the belief that plastic rots). Paragraph two keeps the steps (own baskets, drums as bins and a weekly sweep, "
    r"selling bottles to recyclers, fines only after bins are provided, sorting at school) and ends with a direct call to action. The points that only "
    r"describe consequences (floods, malaria, sick animals, smoke) and the paragraph on how plastic is made are left out, because the task does not "
    r"ask for them. The tone is firm and friendly (\"Fellow students\", \"we can change this\", \"let us\"), every idea is put in the candidate's own words, "
    r"and the text is in TWO paragraphs of fewer than 150 words."
)

GRILLE_A = (
    "**Marking guide**\n\n"
    "| Criterion | Marks | What earns the marks |\n|---|---|---|\n"
    "| Content | 14 | Relevant causes AND steps taken from the passage (about 8 well-chosen points), with no unrelated material |\n"
    "| Expression and Accuracy | 12 | Own words (no lifting of whole sentences), varied linking, correct grammar, spelling and punctuation, TWO paragraphs, 150 words at most |\n"
    "| Slanting | 4 | The whole speech aims at convincing the students to act: a persuasive tone, a direct appeal and a call to action |"
)

PIEGE_A = (
    r"Do not copy whole sentences from the passage, because the instructions say that indiscriminate copying earns no marks. Do not describe the consequences "
    r"(floods, malaria, smoke) when the task asks for causes and steps, and do not write one paragraph or three instead of TWO, or go over 150 words."
)
CONSEIL_A = r"Underline the causes in one colour and the steps in another before you write: the first paragraph then takes the causes and the second takes the steps."
RAPPEL_A = (
    r"In a directed writing task, select only the ideas that answer the exact question, put them in your own words, respect the number of paragraphs and "
    r"the word limit, and keep the tone asked for (here persuasion) from the first sentence to the last."
)

# ------------------------------------------------------------------------------------------------------------------------------ Section B
FIN_A_RECITER = r"... and I have never taken a shortcut since."

TOPICS = [
    dict(
        lettre="a",
        sujet=r"Tell a story that ends with, \"... and I have never taken a shortcut since.\"",
        plan=["Introduction: the morning of an important examination and a late start.", "The decision to take a shortcut across a farm.",
              "The mishap at the swollen stream.", "The consequence at school and the father's words.", "The lesson, ending with the given line."],
        modele=(
            "The morning of the Mathematics paper began badly. My alarm clock, which had served me faithfully for three years, chose that day to stay silent, and I woke "
            "at ten past seven with the examination due to begin at eight. I swallowed a piece of bread, grabbed my geometry set and ran out of the compound without even "
            "greeting my mother.\n\n"
            "The main road to school is a long curve that passes the market and the police station, and I knew that I could not cover it in fifty minutes. Then I "
            "remembered the footpath that the herdsmen use across Atanga's old cassava farm. Everyone said that it cut the journey by half. Nobody said that it crossed a "
            "stream, but at that moment I did not care. A good candidate, I told myself, does not arrive late.\n\n"
            "The path was narrow and slippery with the dew of the rainy season. I jumped over roots, pushed aside wet leaves and felt proud of my cleverness until I reached "
            "the stream. After the rains of the night before, the water was brown and swollen, and the two logs that served as a bridge were gone. I looked left and right, "
            "but there was nobody to ask. Time was passing, so I took off my shoes, held them above my head and stepped into the water.\n\n"
            "I had hardly crossed half of the stream when my foot slipped on a smooth stone. I fell heavily, and the current carried away my geometry set, my pen and my "
            "admission slip. I caught a branch and pulled myself out, shaking with cold and fear, with a painful ankle and my uniform soaked in mud. By the time I limped to "
            "the road and found a motorbike taxi, it was already ten minutes past eight.\n\n"
            "At the school gate, the supervisor looked at my muddy clothes and shook his head. \"Without an admission slip, I cannot let you in,\" he said gently. I begged "
            "him until he called the headmaster, who listened to my story and finally signed a replacement slip. I entered the hall forty minutes late, still trembling, with a "
            "borrowed pen and a mind that refused to work. I left the paper half finished and walked home in tears.\n\n"
            "That evening, my father did not shout. He sat beside me and said quietly, \"A short road is not always a quick road, my son. The long way would have cost you "
            "twenty minutes; the short way has cost you your paper.\" His words hurt more than any scolding because they were true.\n\n"
            "Since that painful day, I leave home early and follow the road that everyone follows, even when it is longer. I have learnt that patience and preparation are "
            "better friends than haste, and I have never taken a shortcut since."
        ),
        piege=r"Ending with a different sentence: the given line must be the last words of the story and must follow naturally from what happened.",
    ),
    dict(
        lettre="b",
        sujet=r"Describe a village football match that was stopped by a sudden storm.",
        plan=["The crowd and the setting before the match.", "The match in the heat.", "The sky changes: wind, shadow and thunder.",
              "The storm breaks and the field empties.", "After the rain: the sun, the handshake and a closing thought."],
        modele=(
            "On the last Saturday of the dry season, the whole village of Njinikom gathered at the football field behind the Presbyterian church. It was the final of the "
            "Inter-Quarter Cup, and the two teams, Up Quarter in red and Down Quarter in green, had not lost a match all year. By two o'clock the field was ringed with "
            "people: women with babies tied on their backs, old men on wooden stools and children perched like birds in the branches of the mango trees. Vendors walked "
            "among the crowd selling roasted corn, cold water in plastic bags and sugarcane cut into short sticks.\n\n"
            "The match began in blistering heat. The grass was yellow, and the dust rose in little clouds each time the players ran. The referee, a retired teacher whose "
            "whistle had served twenty seasons, blew the first blast, and the crowd roared. In the tenth minute, the captain of Down Quarter, a tall boy with a bandage on his "
            "knee, struck the ball so hard that it flew over the bar and landed on the roof of a nearby house. Laughter rolled around the field like a wave.\n\n"
            "Soon after, the sky changed. A heavy shadow slid across the sun, and the air, which had been dry and hot, turned cool and smelt of wet earth. The leaves of the "
            "mango trees began to tremble. Far away to the west, the hills disappeared behind a grey curtain, and a low rumble, like a lorry crossing a wooden bridge, rolled "
            "towards us. The children in the trees looked at one another, but nobody wanted to leave before the end of the half.\n\n"
            "The first drops fell just as the red team scored. They were big and cold, and each made a small crater in the dust. Then, without warning, the sky opened. Rain "
            "came down in thick silver ropes, and a sharp flash of lightning split the clouds, followed by a clap of thunder that shook the ground. The vendors covered their "
            "baskets, the women threw wrappers over their children's heads, and the players, soaked to the skin, stood in the middle of the field, not knowing whether to "
            "laugh or to run.\n\n"
            "The referee blew a long final blast and waved both hands above his head. In a minute the field was empty. People ran towards the church porch, the market shed and "
            "the nearest houses, shouting, slipping and laughing. The goalposts stood alone in the storm, and the ball floated slowly in a pool at the centre of the pitch like "
            "a forgotten orange.\n\n"
            "An hour later, when the rain had thinned to a drizzle, the sun returned with a pale gold light. The red and the green teams, dripping and muddy, shook hands under "
            "a mango tree, and the final was fixed for the following Sunday. I walked home through the puddles with my shoes in my hand, thinking that no goal in the world "
            "could have been as memorable as that sudden storm."
        ),
        piege=r"Telling a story instead of describing: use colours, sounds, smells and movement, and keep the order of events clear.",
    ),
    dict(
        lettre="c",
        sujet=r"Hospitality.",
        plan=["Introduction: what hospitality means in our communities.", "An example from life: a grandmother's welcome.",
              "Reasons why hospitality matters.", "Its dangers and limits.", "Hospitality today and a closing thought."],
        modele=(
            "Hospitality is the warm and generous welcome that a person gives to a visitor, whether that visitor is a relative, a neighbour or a total stranger. In our "
            "communities it is not only a habit but a source of pride, and a family that sends a guest away hungry is spoken of with shame for many years.\n\n"
            "From my childhood, I have watched my grandmother practise this virtue. Whenever a traveller knocked at our door, she brought a stool, a bowl of water to wash "
            "his hands and a cup of tea before asking a single question. Only after the guest had eaten and rested did she enquire about his journey. When the food was little, "
            "she gave the guest the biggest share and ate what was left without complaint. I once asked her why she did this for people she had never met. She smiled and "
            "said, \"Today he is a stranger in my house; tomorrow I may be a stranger in his.\" Her words have stayed with me ever since.\n\n"
            "Hospitality matters for several reasons. First, it creates friendship and trust. Many lifelong friendships began with a cup of water offered to a tired traveller. "
            "Second, it keeps communities united, since people who share food and shelter are less likely to quarrel. Third, it is a form of insurance in a land with few "
            "hotels: a person who has been generous will find an open door in another town. Finally, it teaches the young to think of others before themselves, which is the "
            "foundation of good character.\n\n"
            "However, hospitality has its dangers and limits. A host who spends beyond his means to impress a visitor may fall into debt, and a guest who stays for months "
            "without helping becomes a burden. Some people also abuse the kindness of others, arriving at mealtimes without invitation and leaving without a word of thanks. "
            "Wise hospitality is therefore generous but not foolish. A good host gives freely what he can afford, and a good guest gives thanks, helps in the house and knows "
            "when it is time to leave.\n\n"
            "Many people say that hospitality is dying because of busy lives, high walls and fear of strangers. I do not agree entirely. In the town where I live, I have "
            "seen a shopkeeper share her lunch with a stranded driver and neighbours open their doors to families whose houses were destroyed by floods. The form may change, "
            "but the spirit remains.\n\n"
            "Hospitality is a priceless gift that costs little and returns much. A smile, a seat and a glass of water can turn a stranger into a friend, and a society that "
            "keeps this tradition alive will always be a home for everybody."
        ),
        piege=r"Writing only a definition or only a story: a one-word topic needs an introduction, several developed ideas with examples, and a conclusion.",
    ),
    dict(
        lettre="d",
        sujet=r"School uniforms should be abolished. Do you agree?",
        plan=["Introduction: the question and the writer's position.", "The arguments of those who want uniforms abolished.",
              "Three reasons for keeping uniforms: equality, discipline and security, pride.", "Answers to the objections of cost and freedom.", "Conclusion: the position restated."],
        modele=(
            "Every school morning, thousands of pupils across Cameroon pull on the same khaki shirts, grey trousers or blue skirts before leaving for class. Some people "
            "believe that this habit is outdated and that uniforms should be abolished. I do not agree, and in this essay I shall explain why.\n\n"
            "Those who want uniforms abolished have some reasons. They argue that uniforms are expensive, since parents with many children must buy several sets every year. "
            "They add that pupils should be free to express their personality through their clothes. Finally, they point out that a uniform soaked by rain or torn in play is "
            "uncomfortable.\n\n"
            "These points deserve respect, but they do not outweigh the benefits of uniforms. First, a uniform removes the pressure of fashion. Without it, children from rich "
            "families would arrive in expensive clothes, and children from poor families would feel ashamed of their old ones. In a uniform, a farmer's daughter and a "
            "minister's son sit side by side as equals, and the only difference between them is the quality of their work. Second, uniforms help discipline and security. A "
            "teacher can recognise a stranger on the compound at once, and a lost pupil in the market can easily be returned to his school. Third, a uniform creates a sense "
            "of belonging and pride. Pupils who defend the colours of their school in a sports competition feel that they belong to something bigger than themselves.\n\n"
            "It is also true that ordinary clothes can distract pupils. I have seen classmates spend half of a lesson comparing shoes and watches instead of listening to the "
            "teacher. When everybody wears the same thing, attention returns to the lesson.\n\n"
            "Uniforms make life easier for families every morning as well. A child who must choose what to wear may waste time, arrive late and quarrel with his parents, "
            "while a child in uniform is dressed in a few minutes and walks to school with a clear mind. Uniforms are also easy to see on the road at dawn, which helps drivers "
            "to notice small pupils, and they hide the stains of a long day's play, so that parents wash fewer clothes and spend less on soap.\n\n"
            "As for cost, a uniform is usually cheaper than several sets of fashionable clothes, and it lasts the whole year. If some families struggle, the answer is to help "
            "them with low prices, exchanges of used uniforms or sponsorship, not to remove a system that serves everyone. Freedom of expression, for its part, can be enjoyed "
            "after school, at home and at weekends.\n\n"
            "Uniforms promote equality, discipline and pride at a modest cost. Schools should keep them, make them more affordable and let pupils express themselves in other "
            "ways. That is why I strongly disagree that school uniforms should be abolished."
        ),
        piege=r"Giving only one side: an argumentative essay states a clear position, meets the opposite view and answers it, and keeps the same position to the end.",
    ),
    dict(
        lettre="e",
        sujet=r"Write a story to illustrate the proverb: \"A single hand cannot tie a bundle.\"",
        plan=["Introduction: a proud farmer who refuses help.", "The warning and the rising storm.", "The failed attempt to tie the harvest alone.",
              "The neighbours help and the harvest is saved.", "The lesson linked to the proverb."],
        modele=(
            "In the village of Mbengwi lived an old farmer named Pa Fru, who was famous for two things: his large field of maize and his pride. Each year at harvest time, "
            "while the neighbours helped one another to cut the stalks and tie them into bundles, Pa Fru worked alone from dawn until dusk. \"I have two hands that have never "
            "failed me,\" he used to say. \"A man who needs help is a weak man.\"\n\n"
            "That year, the maize was heavier than ever. His neighbour, Mami Akwen, passed by one morning and offered to bring her sons and daughters to help him. Pa Fru "
            "refused with a wave of his stick. His own son, Chia, who had returned from the city for the holidays, also begged him, but the old man only laughed. \"Go and "
            "sleep,\" he said. \"By the end of the week, every stalk will be tied and stored.\"\n\n"
            "Seven days later, he had cut nearly the whole field, but only a third of the maize was tied. He was tired, his hands were swollen with blisters and his back ached "
            "terribly. On the eighth afternoon, an old woman who sold vegetables at the roadside shouted to him that the sky was turning black. Pa Fru looked up and saw heavy "
            "clouds moving fast across the hills. If the rain caught the loose stalks, the whole harvest would rot in the field.\n\n"
            "He worked as quickly as he could, but every time he tried to lift a pile of stalks and bind it with the rope, the stalks slid from his arms and scattered on the "
            "ground. The wind rose, the first drops of rain fell, and tears of shame and fear filled his eyes. For the first time in his life, Pa Fru understood that he could "
            "not do it alone. His arms trembled, his knees gave way, and he sat on a heap of wet stalks and covered his face with his hands.\n\n"
            "Then he heard voices. Mami Akwen was running across the field with her sons and daughters, and behind them came Chia with a dozen young men from the village. "
            "\"Hold the bundle, Pa!\" cried one. \"Pull the rope!\" cried another. Hands passed stalks, tied knots and carried bundles to the barn. Within an hour, the whole "
            "harvest was under the roof, and the rain came down as heavy as a flood.\n\n"
            "That night, Pa Fru sat among his neighbours in the barn, with a bowl of hot soup warming his blistered hands. \"Forgive an old fool,\" he said quietly. \"I have "
            "learnt this evening what our elders always knew: a single hand cannot tie a bundle.\" From that day, he was the first to run to any neighbour who needed help."
        ),
        piege=r"Explaining the proverb instead of illustrating it: the story itself must show the meaning, and the proverb is usually recalled only at the end.",
    ),
    dict(
        lettre="f",
        sujet=r"What problems do small-scale farmers in your region face, and how can these problems be solved?",
        plan=["Introduction: the importance of small-scale farmers.", "Problems: transport, storage, prices and costs, weather.", "Solutions for each problem.",
              "The role of farmers, the government and young people.", "Conclusion."],
        modele=(
            "Small-scale farmers feed most of the families of our region. With a few hectares of land and simple tools, they produce the maize, cassava, beans and vegetables "
            "that fill our markets every week. Yet these men and women, on whom the country depends, face serious problems that keep them poor.\n\n"
            "The first problem is the poor state of the roads. During the rainy season, many villages are cut off, and a farmer who carries a heavy load of tomatoes on his "
            "head or on a bicycle may arrive at the market too late or not at all. Part of the harvest rots on the way. The second problem is the lack of storage. After a "
            "good harvest, prices fall, and farmers have no barns or dryers to keep the produce until the price improves. Third, middlemen often buy at very low prices "
            "and sell at high ones, so that the farmer works for months and earns very little.\n\n"
            "Farmers also suffer from the high cost of seeds, fertilisers and tools, and few banks will lend money to someone without a title to his land. Finally, changes in "
            "the weather have become a heavy burden. Rains arrive late or stop too early, and pests destroy crops that took months of work. Women, who do much of the work in "
            "the fields, often have no title to the land they cultivate and no voice in the decisions that affect it, so they cannot borrow money or plan for the future.\n\n"
            "These problems can be solved if everybody plays a part. The government should repair rural roads and build village markets and storehouses. Extension workers "
            "should visit farmers regularly to teach them about improved seeds, simple irrigation and the control of pests. Banks and development projects can offer small loans "
            "with fair conditions, and the law should protect the land rights of women and of families who have farmed the same plots for generations. Farmers can also join "
            "common initiative groups, so that they can buy inputs in large quantities at a lower price, share a lorry to the town and sell together at better prices. "
            "Processing crops, for example drying cassava or making tomato paste, also adds value and reduces waste.\n\n"
            "Young people have a role as well. Instead of leaving for the cities, educated youths can bring new ideas, use mobile phones to learn market prices and keep "
            "records, and show that farming can be a respected and profitable profession.\n\n"
            "Small-scale farmers will never be rich while their roads are bad, their stores are empty and their prices are decided by others. With better roads, storage, "
            "training and cooperation, they can feed the nation and live in dignity. Their success is the success of the whole country, because a nation that cannot feed "
            "itself can never be truly free."
        ),
        piege=r"Listing the problems without solutions, or giving solutions that do not match the problems: pair each problem with a realistic remedy.",
    ),
    dict(
        lettre="g",
        sujet=(
            r"Write a letter to your cousin Nsame, who has just started boarding school and feels homesick, to encourage him and to give him advice. Your name is Fonyuy "
            r"Lucas and your address is P.O. Box 17 Fundong."
        ),
        plan=["Address, date and greeting.", "Opening: health, news and the reason for writing.", "Encouragement: homesickness is normal and will pass.",
              "Advice: friends, studies, routine, contact with home.", "Closing: wishes, promise to visit and signing off."],
        modele=(
            "P.O. Box 17,\nFundong.\n14th October, 2026.\n\n"
            "Dear Nsame,\n\n"
            "How are you after your first weeks at school? I hope that you are eating well and sleeping soundly. Everybody at home is well, and your mother sends you her love and a big hug. Your little "
            "brother asks every evening when you will come back, and he has already promised to keep your football safe until then. I am writing because I learnt from your "
            "mother that you were sad during the first days at boarding school, and I wanted to tell you that I understand.\n\n"
            "When I entered boarding school three years ago, I cried every night for two weeks. I missed my mother's cooking, my little sister's jokes and even the sound of "
            "the cock in the morning. I thought that I would never get used to the dormitory, the early bell and the endless rows of beds. Yet today I look back on those "
            "days with a smile. Feeling homesick does not mean that you are weak. It only shows that you love your family, and with time, the feeling will fade.\n\n"
            "Here are a few habits that helped me. First, make friends quickly. Greet your dormmates, share your snacks and join them for football or for study "
            "groups in the evening. When you are busy with friends, sadness has little room. Second, take your studies seriously from the first week. Write your notes "
            "neatly, ask questions when you do not understand and revise a little every day, so that the work never piles up. Third, keep to a routine: wake up early, "
            "wash, eat well and sleep on time. A tired boy sees problems bigger than they are. Next, never hide an illness or a worry. If you feel sick, tell the matron or "
            "your class master at once, and if someone troubles you, report it calmly to a teacher instead of keeping it inside. Finally, write to us often. A letter or a "
            "short call on visiting day will remind you that you are never alone.\n\n"
            "Remember also why you are there. Your parents are working hard to give you a good education, and many children in our village would love to be in your place. "
            "Every page that you learn is a step towards the job that you dream of.\n\n"
            "I shall visit you in the second week of next month and bring you your favourite dried fish and a pot of honey. Until then, be strong, be kind to others and be "
            "proud of yourself. Remember that the first term is always the hardest, and that by the second term the school will feel like a second home.\n\n"
            "Please give my greetings to your teachers, and write to me soon.\n\n"
            "Your loving cousin,\n\nFonyuy Lucas."
        ),
        piege=r"Forgetting the layout of an informal letter (your address, the date, a greeting and a closing) or writing only advice with no encouragement.",
    ),
]

PLAN_ENONCE_B = (
    r"**SECTION B - COMPOSITION (40 marks)**" "\n\n"
    r"Mark distribution: Content and Organisation (12 marks); Expression (16 marks); Accuracy (12 marks)." "\n\n"
    r"Choose ONE of the following topics and write a composition of about 450 words, paying attention to grammar, spelling, punctuation and handwriting. "
    r"Do not write on more than one topic." "\n\n"
)

GRILLE_B = (
    "**Marking grid**\n\n"
    "| Criterion | Marks | What earns the marks |\n|---|---|---|\n"
    "| Content and Organisation | 12 | The topic is covered fully and stays relevant, in clear paragraphs (introduction, development, conclusion), with the layout asked for |\n"
    "| Expression | 16 | Varied vocabulary and sentence structures, a style and tone suited to the topic, fluent links between ideas |\n"
    "| Accuracy | 12 | Correct grammar, tenses, spelling and punctuation |"
)

RAPPEL_B = (
    r"A good composition answers the exact topic, follows a plan with an introduction, a developed middle and a conclusion, uses a style that suits the type "
    r"of writing (story, description, argument or letter), and is checked for tenses, spelling and punctuation before it is handed in."
)
CONSEIL_B = r"Spend five minutes on a plan before you write, and keep five minutes at the end to reread your composition for tenses, spelling and punctuation."
PIEGE_B_GENERAL = (
    r"Do not write on two topics, do not memorise a composition in advance (it earns no marks), and do not leave the conclusion unfinished because time ran out. "
    r"Check also the special demand of your topic: the given last line of a story, the layout of a letter or both sides of an argument."
)

CRITERES_A = [
    (r"You select about eight relevant points on both the causes and the steps from the passage, and leave out unrelated material", 14),
    (r"You write in your own words, link your sentences, keep grammar, spelling and punctuation correct, and respect TWO paragraphs of at most 150 words", 12),
    (r"Your whole speech aims at convincing the students: a persuasive tone, a direct appeal and a call to action", 4),
]
CRITERES_B = [
    (r"You cover the whole topic you chose, stay relevant, use clear paragraphs and respect the layout or the given line of your topic", 12),
    (r"You use varied vocabulary and sentence structures, a style and tone that suit the topic, and fluent links between ideas", 16),
    (r"Your grammar, tenses, spelling and punctuation are correct", 12),
]
