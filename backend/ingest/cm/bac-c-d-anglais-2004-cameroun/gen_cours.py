# -*- coding: utf-8 -*-
import json, os

OUTDIR = "/sessions/brave-ecstatic-ritchie/mnt/Epreuves/json/cm/bac-c-d-anglais-2004-cameroun"
EPREUVE_ID = "bac-c-d-anglais-2004-cameroun"
EPREUVE_TITRE = "Baccalaureat C-D Anglais 2004 - Cameroun"

def base_source(exercice_numero, rappel_id, rappels_lies=None):
    return {
        "epreuve_id": EPREUVE_ID,
        "epreuve_titre": EPREUVE_TITRE,
        "exercice_numero": exercice_numero,
        "rappel_id": rappel_id,
        "rappels_lies": rappels_lies or [],
        "correction_id": None
    }

def write_cours(cours):
    fn = os.path.join(OUTDIR, "bac-c-d-anglais-2004-cameroun_cours_%s.json" % cours["_slug"])
    out = {k: v for k, v in cours.items() if k != "_slug"}
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("written", fn)

COURSES = []

# ---------- 1. DESPITE / IN SPITE OF ----------
COURSES.append({
    "_slug": "concession-despite",
    "cours_id": "cours-concession-despite-bac-c-d-angl-2004",
    "meta": {
        "titre": "Exprimer la concession avec Despite / In spite of",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Concession et opposition",
        "duree_estimee_min": 20,
        "tags": ["despite", "in spite of", "concession", "gerondif", "reecriture"],
        "statut": "brouillon"
    },
    "source": base_source("1", "rdm-bac-c-d-anglais-2004-cameroun-ex1-qA.1-0"),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "Au Bac, un exercice de reecriture revient presque chaque annee : transformer une phrase avec \"although\" en une phrase avec \"despite\" ou \"in spite of\", sans en changer le sens. Beaucoup de candidats connaissent la traduction (\"malgre\") mais perdent des points parce qu'ils gardent la structure grammaticale du francais. Ce cours te donne le reflexe exact pour reussir cette transformation a coup sur."
        },
        {
            "type": "prerequis",
            "items": [
                "Reconnaitre une proposition subordonnee (un sujet suivi d'un verbe conjugue)",
                "Savoir former le gerondif d'un verbe (V + -ing)",
                "Distinguer un nom d'une proposition dans une phrase anglaise"
            ]
        },
        {
            "type": "regle",
            "titre": "Despite / In spite of + nom ou V-ing, jamais + proposition",
            "contenu_markdown": "\"Although\", \"though\" et \"even though\" introduisent une proposition complete : sujet + verbe conjugue. \"Despite\" et \"in spite of\" expriment exactement la meme idee de concession, mais ils se construisent uniquement avec un nom, un pronom ou un verbe au gerondif (V-ing) - jamais avec une proposition introduite par \"that\".\n\nPour passer d'une structure a l'autre, il faut donc supprimer le sujet et le verbe conjugue de la subordonnee et les remplacer par un groupe nominal ou un gerondif qui porte la meme information.",
            "formule_principale": "Despite / In spite of + nom | pronom | V-ing  (jamais + that + sujet + verbe)",
            "variantes": [
                {
                    "nom": "Despite the fact that + proposition",
                    "quand_utiliser": "Quand on veut absolument garder une proposition complete apres \"despite\", on ajoute \"the fact that\" comme intermediaire : \"Despite the fact that he was late, he decided not to run.\" Cette variante est correcte mais plus lourde ; a l'ecrit d'examen, le gerondif ou le nom est presque toujours attendu.",
                    "contenu_markdown": "\"The fact that\" transforme la proposition en un groupe nominal complexe (\"the fact that he was late\"), ce qui respecte la regle : despite est toujours suivi d'un nom, jamais directement d'une proposition."
                }
            ]
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "Reecris la phrase suivante en commencant par \"Despite\", sans changer son sens : \"Although he was late, he decided not to run.\"",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Reperer la subordonnee concessive et l'isoler de la principale",
                    "justification": "Seule la partie introduite par \"although\" doit etre transformee ; la principale reste identique",
                    "resultat_markdown": "Subordonnee : \"Although he was late\" / Principale : \"he decided not to run\""
                },
                {
                    "numero": 2,
                    "action": "Identifier le sujet et le verbe de la subordonnee",
                    "justification": "Il faut savoir precisement ce qu'on doit transformer en groupe nominal ou en gerondif",
                    "resultat_markdown": "Sujet : \"he\" / Verbe : \"was late\" (pretérit de \"to be late\")"
                },
                {
                    "numero": 3,
                    "action": "Transformer \"he was late\" en gerondif",
                    "justification": "Despite exige un nom ou un V-ing, jamais un sujet + verbe conjugue ; le gerondif \"being late\" porte exactement la meme information que \"he was late\", le sujet etant deja connu par la principale (\"he decided\")",
                    "resultat_markdown": "\"he was late\" -> \"being late\""
                },
                {
                    "numero": 4,
                    "action": "Reconstruire la phrase complete avec Despite en tete et une virgule avant la principale",
                    "justification": "Quand la proposition/le groupe concessif ouvre la phrase, il est toujours suivi d'une virgule avant la principale",
                    "resultat_markdown": "**Despite being late, he decided not to run.**"
                }
            ],
            "conclusion_markdown": "On vient de transformer une concession exprimee par une proposition complete (\"although\" + sujet + verbe) en une concession exprimee par un gerondif apres \"despite\" - la meme methode s'applique a \"in spite of\"."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Ecrire \"Despite he was late, he decided not to run.\"",
                    "pourquoi_faux": "C'est l'erreur la plus frequente au Bac : elle recopie directement la structure du francais (\"malgre qu'il etait en retard\") sans adapter la grammaire anglaise. \"Despite\" ne peut jamais etre suivi d'un sujet et d'un verbe conjugue.",
                    "correction_markdown": "Transforme toujours \"he was late\" en groupe nominal ou en gerondif avant de le placer apres despite : \"Despite being late\" ou \"Despite his lateness\"."
                },
                {
                    "erreur_markdown": "Oublier la virgule apres le groupe introduit par despite : \"Despite being late he decided not to run.\"",
                    "pourquoi_faux": "A l'ecrit, une virgule separe toujours le groupe ou la proposition concessive de la proposition principale quand elle est placee en tete de phrase ; son absence rend la phrase difficile a lire et peut couter des points de ponctuation au Bac.",
                    "correction_markdown": "Place systematiquement une virgule juste avant le debut de la proposition principale : \"Despite being late, he decided not to run.\""
                },
                {
                    "erreur_markdown": "Utiliser \"despite of\" au lieu de \"despite\" ou \"in spite of\"",
                    "pourquoi_faux": "\"Despite\" ne prend jamais \"of\" apres lui (contrairement a \"in spite of\") ; la confusion entre les deux formes est tres frequente chez les candidats qui les traitent comme des synonymes parfaitement interchangeables sur le plan de la construction.",
                    "correction_markdown": "Retiens les deux constructions separement : \"despite + nom/V-ing\" et \"in spite of + nom/V-ing\", jamais \"despite of\"."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Reecris en commencant par \"Despite\" : \"Although the exam was difficult, she passed with a good grade.\"",
                    "solution_markdown": "La subordonnee est \"Although the exam was difficult\", sujet \"the exam\", verbe \"was difficult\". On transforme en groupe nominal : \"the difficulty of the exam\", ou en gerondif avec reformulation du sujet : \"the exam being difficult\".\n\nOn obtient : **Despite the difficulty of the exam, she passed with a good grade.** (ou : *Despite the exam being difficult, she passed with a good grade.*)"
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "Reecris en commencant par \"In spite of\" : \"Though he had no money, he managed to travel to Europe.\"",
                    "solution_markdown": "La subordonnee est \"Though he had no money\", sujet \"he\", verbe \"had\". \"Having no money\" est un gerondif qui porte la meme information, le sujet etant deja repris dans la principale (\"he managed\").\n\nOn obtient : **In spite of having no money, he managed to travel to Europe.**"
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Reecris en commencant par \"Despite\" : \"Even though the government invested heavily in education, illiteracy rates remained high.\"",
                    "solution_markdown": "La subordonnee \"Even though the government invested heavily in education\" a un sujet different (\"the government\") de celui de la principale (\"illiteracy rates\") : on ne peut donc pas simplement supprimer le sujet comme dans les deux exercices precedents, il faut le transformer en un groupe nominal complet qui integre l'idee d'investissement.\n\n\"The government invested heavily in education\" devient le groupe nominal \"heavy government investment in education\" (ou le gerondif \"the government investing heavily in education\").\n\nOn obtient : **Despite heavy government investment in education, illiteracy rates remained high.** (ou : *Despite the government investing heavily in education, illiteracy rates remained high.*)"
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Devant \"although / though / even though\", attends-toi toujours a un sujet + un verbe conjugue ; devant \"despite / in spite of\", attends-toi toujours a un nom ou un V-ing.",
                "Pour transformer, repere d'abord le sujet et le verbe de la subordonnee, puis reduis-les a un groupe nominal ou a un gerondif.",
                "Si le sujet de la subordonnee est different de celui de la principale, tu dois le garder dans ta transformation (comme sujet du gerondif ou dans le groupe nominal) - ne le fais jamais disparaitre.",
                "N'ecris jamais \"despite of\" : seul \"in spite of\" prend \"of\".",
                "Une virgule separe toujours le groupe concessif de la principale quand il ouvre la phrase.",
                "Au Bac, cette transformation apparait presque systematiquement dans l'exercice de reecriture de la section Grammar : maitriser ce reflexe assure des points faciles a gagner."
            ]
        }
    ]
})

# ---------- 2. COMPOSITION NARRATIVE ET DESCRIPTIVE ----------
COURSES.append({
    "_slug": "composition-narrative-descriptive",
    "cours_id": "cours-composition-narrative-descriptive-bac-c-d-angl-2004",
    "meta": {
        "titre": "Rediger une composition narrative et descriptive a partir d'un souvenir personnel",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Expression ecrite - essay writing",
        "duree_estimee_min": 30,
        "tags": ["essay", "narrative composition", "description", "personal experience", "250 words"],
        "statut": "brouillon"
    },
    "source": base_source("4", "rdm-bac-c-d-anglais-2004-cameroun-ex4-q3-0"),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "\"Describe an occasion that made you very happy.\" Ce type de sujet revient regulierement dans la section Essay du Bac, et il semble facile au premier regard : tout le monde a un souvenir heureux a raconter. La difficulte n'est pas de trouver une idee, elle est de la transformer en un texte structure de 250 mots qui fait vivre la scene au lecteur plutot que de se contenter d'affirmer \"j'etais content\". Ce cours te donne la methode pour construire ce type de composition point par point."
        },
        {
            "type": "prerequis",
            "items": [
                "Conjuguer le preterit simple pour raconter des evenements passes",
                "Connaitre un vocabulaire de base des sentiments (excited, proud, relieved, overjoyed...)",
                "Utiliser les connecteurs chronologiques (first, then, after that, finally...)"
            ]
        },
        {
            "type": "regle",
            "titre": "Combiner recit chronologique et description sensorielle",
            "contenu_markdown": "Une composition narrative et descriptive reussie articule deux mouvements : le recit, qui fait avancer les evenements dans l'ordre chronologique, et la description, qui s'arrete sur les details (lieux, personnes, sensations) pour faire ressentir l'ambiance au lecteur. Un texte qui ne fait qu'enumerer des evenements (\"then... then... then...\") sans jamais s'arreter sur un detail concret manque la moitie de l'exercice, tout comme un texte purement descriptif sans progression narrative.\n\nLa structure attendue en trois temps :\n1. Contexte : ou, quand, avec qui, dans quelle situation l'evenement s'est produit.\n2. Coeur du recit : le moment precis qui a declenche la joie, raconte avec des details concrets (ce qu'on voit, entend, ressent physiquement) et non de simples affirmations abstraites.\n3. Conclusion : ce que cet evenement represente encore aujourd'hui pour le narrateur.",
            "formule_principale": "Contexte -> recit du moment cle avec details sensoriels -> consequence/portee de l'evenement",
            "variantes": [
                {
                    "nom": "Format lettre a un ami",
                    "quand_utiliser": "Quand la consigne precise \"describe this to your friend\", on peut adopter la forme d'une lettre informelle (formule d'appel, corps du recit, formule de cloture) plutot qu'une composition libre : le contenu narratif et descriptif attendu reste identique, seul l'habillage change.",
                    "contenu_markdown": "Ouvrir par \"Dear [prenom],\" et fermer par une formule chaleureuse (\"Best wishes,\" / \"Your friend,\") ; le corps du texte suit exactement la meme structure en trois temps que la composition libre."
                }
            ]
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "\"An occasion that made me very happy.\" Describe this occasion to your friend.",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Choisir un evenement precis et datable, pas une idee vague",
                    "justification": "Un souvenir concret et situe dans le temps donne immediatement une matiere a decrire ; une idee vague (\"quand je suis heureux en general\") ne permet pas de raconter une scene precise",
                    "resultat_markdown": "Evenement choisi : le jour de la reception des resultats du Baccalaureat, en decembre"
                },
                {
                    "numero": 2,
                    "action": "Planter le contexte au debut du texte",
                    "justification": "Le lecteur a besoin de savoir ou, quand et pourquoi avant de suivre le recit du moment cle",
                    "resultat_markdown": "\"It happened last December, when I received the results of the Baccalaureat examination. I had worked so hard all year, and I was extremely anxious as I walked to school to check the notice board.\""
                },
                {
                    "numero": 3,
                    "action": "Raconter le moment cle avec des details sensoriels et une progression chronologique",
                    "justification": "C'est le coeur de la composition : plus les details sont concrets (sensations physiques, reactions immediates), plus la scene devient vivante pour le lecteur",
                    "resultat_markdown": "\"My hands were shaking as I searched for my name on the long list of results. When I finally found my name next to 'PASS', I could not believe my eyes. I shouted with joy, and my classmates around me started congratulating me.\""
                },
                {
                    "numero": 4,
                    "action": "Elargir la scene a l'entourage et conclure sur la portee de l'evenement",
                    "justification": "Terminer uniquement sur le moment precis laisserait le texte incomplet ; montrer les consequences (reaction de la famille, sentiment durable) donne une vraie cloture au recit",
                    "resultat_markdown": "\"I immediately ran home to tell my parents, and my mother cried with happiness while my father hugged me tightly. [...] I will never forget that day.\""
                }
            ],
            "conclusion_markdown": "Le texte complet alterne recit (ce qui se passe, dans l'ordre) et description (les mains qui tremblent, les larmes de la mere), ce qui est exactement ce qu'evalue le correcteur dans ce type de sujet - pas seulement l'affirmation d'un sentiment, mais sa mise en scene concrete."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Se contenter d'affirmer le sentiment sans le montrer : \"I was very happy that day. It was a great day. I will never forget it.\"",
                    "pourquoi_faux": "Ce type de phrase reste abstrait : le correcteur ne voit rien, ne ressent rien, et ne peut pas evaluer la richesse de langue du candidat puisque rien n'est developpe. Repeter le mot \"happy\" sous des formes differentes n'est pas decrire une scene.",
                    "correction_markdown": "Remplace chaque affirmation abstraite par un detail concret qui montre le sentiment : au lieu de \"I was happy\", ecris ce que tu as fait, vu ou ressenti physiquement a ce moment precis (\"my hands were shaking\", \"I shouted with joy\")."
                },
                {
                    "erreur_markdown": "Enchainer les evenements sans aucun connecteur chronologique ni transition : \"I went to school. I saw my name. I was happy. I went home.\"",
                    "pourquoi_faux": "Une succession de phrases courtes sans lien entre elles donne un texte hache qui ne ressemble pas a un recit fluide ; c'est aussi un signe de vocabulaire pauvre qui penalise la note de langue.",
                    "correction_markdown": "Utilise des connecteurs chronologiques (\"first\", \"then\", \"after that\", \"when I finally...\", \"immediately\") pour relier les evenements et donner un rythme naturel au recit."
                },
                {
                    "erreur_markdown": "Choisir un sujet trop vague pour atteindre naturellement 250 mots, puis se repeter pour combler l'espace",
                    "pourquoi_faux": "Un evenement flou (\"un jour ou j'etais content\") oblige a inventer des details artificiels ou a repeter la meme idee sous des formulations differentes, ce qui se voit immediatement a la lecture et penalise la coherence du texte.",
                    "correction_markdown": "Choisis un evenement precis et datable des le brouillon : plus il est concret, plus les 250 mots viennent naturellement sans repetition."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Redige le paragraphe de contexte (3 a 4 phrases) d'une composition sur le sujet : \"A day you received an unexpected gift.\"",
                    "solution_markdown": "Le paragraphe de contexte doit repondre a ou, quand, avec qui, dans quelle situation - sans encore raconter le moment cle lui-meme.\n\n\"It happened on my fifteenth birthday, two years ago. I was not expecting anything special that day because my family had never celebrated birthdays with big gifts. I was sitting in the living room after school, doing my homework as usual, when my elder brother walked in with a large box in his hands.\"\n\nCe paragraphe plante le decor (date, lieu, etat d'esprit initial) et prepare l'entree en scene du moment cle, sans encore le raconter."
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "A partir du contexte de l'exercice 1, redige le paragraphe central (moment cle) en integrant au moins trois details sensoriels ou emotionnels concrets.",
                    "solution_markdown": "Le paragraphe central doit ralentir le recit sur l'instant precis et multiplier les details concrets plutot que de resumer l'action.\n\n\"My hands trembled slightly as I opened the box, not knowing what to expect. Inside, I found the exact pair of football boots I had been dreaming about for months but had never dared to ask for, knowing how expensive they were. My heart raced, and for a few seconds I simply stared at them in silence, unable to say a word. When I finally looked up, my brother was smiling, clearly enjoying my speechless reaction.\"\n\nLes details concrets (\"hands trembled\", \"heart raced\", \"stared in silence\") montrent l'emotion au lieu de se contenter de la nommer, exactement la competence evaluee dans ce type de sujet."
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Redige la composition complete (250 mots minimum) sur le sujet : \"Describe a moment when you helped someone and it made you feel proud.\" Ta reponse doit combiner contexte, recit du moment cle avec details sensoriels, et conclusion sur la portee de l'evenement, en integrant au moins un dialogue rapporte.",
                    "solution_markdown": "Cet exercice combine toutes les competences du cours (structure en trois temps, details concrets, connecteurs chronologiques) avec une contrainte supplementaire : integrer un dialogue rapporte, une technique qui rend un recit encore plus vivant.\n\n\"Dear Marie,\n\nI want to tell you about a moment that made me feel truly proud of myself.\n\nIt happened last month, on my way back from school. As I was walking along the main road, I noticed an old woman struggling to carry several heavy bags of foodstuff, stopping every few steps to catch her breath. Most people walked past without even looking at her.\n\nI hesitated for a moment, worried about being late for my evening classes, but I finally decided to stop. 'Would you like some help carrying these, madam?' I asked. She looked at me, clearly surprised, and said, 'Thank you, my son, God bless you. My legs are not what they used to be.'\n\nI carried her bags all the way to her house, about fifteen minutes away, listening to her talk about her grandchildren along the road. When we finally arrived, she thanked me again and offered me a mango from her garden, which I gratefully accepted.\n\nWalking back home that evening, I felt a warmth in my chest that had nothing to do with the weather. I had missed part of my evening class, but I did not regret it for a second. That small act taught me that helping someone, even in a simple way, can bring more happiness than almost anything else.\n\nBest wishes,\nYour friend\"\n\nLe texte respecte la structure en trois temps, integre un dialogue rapporte authentique et conclut sur une reflexion personnelle qui depasse le simple recit factuel - exactement ce qu'un correcteur valorise a ce niveau."
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Choisis toujours un evenement precis et datable plutot qu'une idee vague : c'est ce qui te permettra de decrire une vraie scene.",
                "Structure ton texte en trois temps : contexte, moment cle riche en details, conclusion sur la portee de l'evenement.",
                "Montre le sentiment par des details concrets (sensations physiques, reactions, dialogue) plutot que de te contenter de l'affirmer.",
                "Utilise des connecteurs chronologiques pour donner du rythme au recit et eviter les phrases hachees.",
                "Un dialogue rapporte, meme court, rend un recit beaucoup plus vivant et montre une maitrise plus fine de la langue.",
                "Au Bac, ce type de sujet apparait dans la section Essay : la longueur minimale (250 mots) se remplit naturellement quand le sujet choisi est concret, jamais en te repetant."
            ]
        }
    ]
})

# ---------- 3. VERBES SUIVIS DE L'INFINITIF NEGATIF ----------
COURSES.append({
    "_slug": "verbes-suivis-infinitif-negatif",
    "cours_id": "cours-verbes-suivis-infinitif-negatif-bac-c-d-angl-2004",
    "meta": {
        "titre": "Construire l'infinitif negatif apres des verbes comme warn, tell, advise",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Grammaire - constructions verbales",
        "duree_estimee_min": 18,
        "tags": ["warn", "infinitif negatif", "verbe + COD + to-infinitif"],
        "statut": "brouillon"
    },
    "source": base_source("1", "rdm-bac-c-d-anglais-2004-cameroun-ex1-qB.4-0"),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "\"The doctor warned him ... smoke.\" Faut-il \"not to\", \"don't\" ou \"doesn't\" ? Cette question de grammaire, frequente dans les QCM du Bac, piege les candidats qui traduisent depuis le francais (\"il lui a dit de ne pas fumer\") sans connaitre la construction exacte de l'anglais apres des verbes comme warn, tell ou advise. Ce cours fixe definitivement ce reflexe."
        },
        {
            "type": "prerequis",
            "items": [
                "Connaitre la structure verbe + complement d'objet direct + infinitif avec to (\"I want him to come\")",
                "Savoir former l'infinitif d'un verbe (to + base verbale)"
            ]
        },
        {
            "type": "regle",
            "titre": "Verbe + COD + (not) + to + infinitif",
            "contenu_markdown": "Une famille de verbes anglais (warn, tell, advise, ask, order, remind, want, expect...) se construit avec un complement d'objet direct (la personne concernee) suivi d'un infinitif complet avec \"to\". Pour mettre cet infinitif a la forme negative, on place \"not\" directement devant \"to + verbe\", jamais un auxiliaire conjugue comme \"don't\" ou \"doesn't\", qui ne peuvent s'utiliser qu'avec un verbe conjugue a un temps precis, pas avec un infinitif.",
            "formule_principale": "Sujet + verbe (warn/tell/advise...) + complement + not to + base verbale",
            "variantes": []
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "Complete : \"The doctor warned him ... smoke.\" (not to, don't, doesn't)",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Identifier le verbe principal et sa construction habituelle",
                    "justification": "\"Warn\" appelle la structure warn + quelqu'un + (not) + to + infinitif, ce qui elimine d'emblee toute forme conjuguee comme \"don't\" ou \"doesn't\"",
                    "resultat_markdown": "\"warn someone (not) to do something\""
                },
                {
                    "numero": 2,
                    "action": "Identifier le complement d'objet direct",
                    "justification": "Le complement est deja present dans la phrase, entre le verbe et le blanc",
                    "resultat_markdown": "\"him\" (la personne mise en garde)"
                },
                {
                    "numero": 3,
                    "action": "Determiner le sens attendu : mise en garde contre l'action de fumer",
                    "justification": "Le medecin met en garde CONTRE le tabac, l'infinitif doit donc etre negatif",
                    "resultat_markdown": "infinitif negatif requis avant \"smoke\""
                },
                {
                    "numero": 4,
                    "action": "Choisir la seule forme compatible avec un infinitif : not to",
                    "justification": "\"don't\" et \"doesn't\" sont des auxiliaires conjugues qui ne peuvent jamais preceder un infinitif nu comme \"smoke\" dans cette structure",
                    "resultat_markdown": "**The doctor warned him not to smoke.**"
                }
            ],
            "conclusion_markdown": "Des que \"warn/tell/advise + quelqu'un\" est suivi d'un verbe, seule la forme \"not to + verbe\" permet d'exprimer la negation - jamais un auxiliaire conjugue."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Choisir \"doesn't\" par calque du francais : \"The doctor warned him doesn't smoke.\"",
                    "pourquoi_faux": "\"Doesn't\" est un auxiliaire conjugue au present simple ; il ne peut precéder qu'un verbe conjugue a la base (\"He doesn't smoke\"), jamais un infinitif complement d'un autre verbe comme \"warned\".",
                    "correction_markdown": "Verifie toujours si le verbe qui suit le complement est un infinitif (introduit par \"to\") ou un verbe conjugue independant : ici, \"warned him\" appelle un infinitif, donc \"not to smoke\", jamais \"doesn't smoke\"."
                },
                {
                    "erreur_markdown": "Placer \"not\" apres \"to\" : \"warned him to not smoke\"",
                    "pourquoi_faux": "Cette forme existe dans un anglais tres familier mais n'est pas la construction standard attendue a l'ecrit d'examen ; l'ordre correct place \"not\" avant \"to\".",
                    "correction_markdown": "Respecte l'ordre standard enseigne au Bac : \"not to + verbe\", jamais \"to not + verbe\"."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Complete avec la forme correcte : \"My mother told me ... (not / to be) late for school.\"",
                    "solution_markdown": "\"Tell someone (not) to do something\" suit la meme structure que \"warn\". Le sens attendu est une mise en garde contre le retard, donc l'infinitif negatif.\n\nOn obtient : **My mother told me not to be late for school.**"
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "Transforme au discours rapporte avec un infinitif negatif : Le professeur a dit : \"Don't cheat during the exam.\" (The teacher advised the students ...)",
                    "solution_markdown": "\"Advise someone (not) to do something\" suit la meme construction. L'ordre \"Don't cheat\" au discours direct devient un infinitif negatif au discours rapporte avec \"advise\".\n\nOn obtient : **The teacher advised the students not to cheat during the exam.**"
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Combine ces deux phrases en une seule, en utilisant \"warned ... not to\" : \"The guide gave an instruction. The instruction was: 'Do not touch the animals in the reserve.'\"",
                    "solution_markdown": "Il faut d'abord identifier qui est mis en garde (les touristes, implicites dans le contexte d'une reserve) puis appliquer la structure warn + complement + not to + verbe, en adaptant le verbe \"touch\" a l'infinitif negatif.\n\nOn obtient : **The guide warned the visitors not to touch the animals in the reserve.**\n\nCet exercice montre que la meme regle grammaticale (verbe + COD + not to + infinitif) s'applique aussi bien a \"warn\" qu'a \"tell\" ou \"advise\", des que le verbe introducteur appelle cette construction."
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Warn, tell, advise, ask, order, remind se construisent avec complement + infinitif complet (\"to + verbe\").",
                "Pour nier cet infinitif, place \"not\" juste avant \"to\", jamais un auxiliaire conjugue comme \"don't\" ou \"doesn't\".",
                "Ne traduis jamais mot a mot depuis le francais (\"il lui a dit de ne pas...\") : verifie toujours si l'anglais attend un infinitif ou un verbe conjugue independant.",
                "Cette construction est un classique des QCM de grammaire au Bac : reconnais-la des que tu vois warn/tell/advise suivi d'un complement de personne."
            ]
        }
    ]
})

# ---------- 5. PRONOMS RECIPROQUES ET REFLECHIS ----------
COURSES.append({
    "_slug": "pronoms-reciproques-reflechis",
    "cours_id": "cours-pronoms-reciproques-reflechis-bac-c-d-angl-2004",
    "meta": {
        "titre": "Distinguer pronoms reciproques (each other/one another) et pronoms reflechis (myself, themselves...)",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Grammaire - pronoms",
        "duree_estimee_min": 18,
        "tags": ["each other", "one another", "pronoms reflechis", "themselves"],
        "statut": "brouillon"
    },
    "source": base_source("1", "rdm-bac-c-d-anglais-2004-cameroun-ex1-qB.1-0"),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "\"The couple does not like ... , so they are always fighting.\" Faut-il \"themselves\" ou \"each other\" ? La difference parait subtile en francais, ou \"se detester\" peut s'appliquer aussi bien a soi-meme qu'a une relation entre deux personnes. En anglais, la distinction est stricte et testee regulierement au Bac : ce cours te donne le critere pour ne plus jamais te tromper."
        },
        {
            "type": "prerequis",
            "items": [
                "Identifier le sujet d'une phrase et savoir s'il designe une seule personne, un groupe ou plusieurs entites distinctes"
            ]
        },
        {
            "type": "regle",
            "titre": "Reciprocite entre deux sujets vs action sur soi-meme",
            "contenu_markdown": "Les pronoms reciproques (\"each other\", \"one another\") s'emploient quand deux ou plusieurs sujets distincts exercent une action l'un sur l'autre : A agit sur B et B agit sur A. Les pronoms reflechis (\"myself\", \"yourself\", \"himself\", \"herself\", \"itself\", \"ourselves\", \"yourselves\", \"themselves\") s'emploient quand le sujet exerce l'action sur lui-meme, sans echange avec une autre personne.\n\nLe test simple : si l'on peut reformuler la phrase par \"A fait quelque chose a B ET B fait la meme chose a A\", il s'agit d'une reciprocite (\"each other\"). Si l'action revient uniquement sur celui qui l'accomplit, il s'agit d'un pronom reflechi.",
            "formule_principale": "A + B agissent l'un sur l'autre -> each other / one another  |  chacun agit sur lui-meme -> myself/yourself/himself...",
            "variantes": [
                {
                    "nom": "One another vs each other",
                    "quand_utiliser": "\"Each other\" et \"one another\" sont interchangeables dans la plupart des contextes ; certains guides reservent traditionnellement \"one another\" a plus de deux personnes et \"each other\" a deux personnes exactement, mais cette distinction n'est plus strictement appliquee en anglais contemporain et n'est pas exigee au Bac.",
                    "contenu_markdown": "En pratique, les deux formes sont acceptees indifferemment pour exprimer une reciprocite, que le groupe compte deux ou plusieurs membres."
                }
            ]
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "Choisis la bonne reponse : \"The couple does not like ... , so they are always fighting.\" (themselves, each other, both)",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Identifier le sujet et ce qu'il designe",
                    "justification": "\"The couple\" designe deux personnes distinctes (les deux membres du couple), pas une seule entite qui agirait sur elle-meme",
                    "resultat_markdown": "sujet = deux personnes distinctes"
                },
                {
                    "numero": 2,
                    "action": "Appliquer le test de reciprocite",
                    "justification": "\"They are always fighting\" (ils se disputent constamment) implique une relation ou chacun des deux membres du couple n'apprecie pas l'autre, pas chacun ne s'appreciant pas lui-meme",
                    "resultat_markdown": "A n'aime pas B ET B n'aime pas A -> reciprocite confirmee"
                },
                {
                    "numero": 3,
                    "action": "Eliminer les options incompatibles",
                    "justification": "\"Themselves\" impliquerait que chaque membre du couple ne s'aime pas lui-meme, ce qui ne correspond pas au contexte de la dispute entre deux personnes ; \"both\" est un pronom de quantite, pas un pronom reciproque ou reflechi, il ne peut pas completer \"like\" ici",
                    "resultat_markdown": "\"themselves\" et \"both\" elimines"
                },
                {
                    "numero": 4,
                    "action": "Retenir la forme reciproque",
                    "justification": "Seul \"each other\" exprime correctement l'idee que les deux membres du couple ne s'apprecient pas mutuellement",
                    "resultat_markdown": "**The couple does not like each other, so they are always fighting.**"
                }
            ],
            "conclusion_markdown": "Le mot cle a repérer est le contexte de relation entre deux entites distinctes (\"fighting\" implique deux parties) : c'est ce contexte, pas le verbe seul, qui impose le pronom reciproque."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Choisir \"themselves\" des qu'un sujet pluriel apparait dans la phrase, sans verifier le sens de l'action",
                    "pourquoi_faux": "Un sujet pluriel ne suffit pas a justifier un pronom reflechi : \"the students hurt themselves\" (chacun s'est blesse lui-meme) et \"the students hurt each other\" (ils se sont blesses mutuellement, l'un l'autre) sont deux situations totalement differentes malgre le meme sujet pluriel.",
                    "correction_markdown": "Ne te fie jamais uniquement au nombre (singulier/pluriel) du sujet : demande-toi toujours si l'action revient sur celui qui l'accomplit (reflechi) ou s'echange entre plusieurs sujets distincts (reciproque)."
                },
                {
                    "erreur_markdown": "Utiliser \"both\" comme s'il s'agissait d'un pronom reciproque : \"They love both.\"",
                    "pourquoi_faux": "\"Both\" est un determinant ou pronom de quantite qui signifie \"les deux\", il ne peut jamais exprimer une relation d'echange entre deux sujets comme le fait \"each other\".",
                    "correction_markdown": "Reserve \"both\" aux phrases ou tu veux dire \"les deux\" (\"Both of them passed the exam\"), jamais pour exprimer une reciprocite d'action."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Choisis : \"Before the mirror, she looked at ... for a long time.\" (herself, each other, themselves)",
                    "solution_markdown": "Le sujet \"she\" est une seule personne qui se regarde elle-meme dans un miroir : il n'y a pas d'echange entre deux sujets distincts, il s'agit donc d'un pronom reflechi accorde a la troisieme personne du singulier feminin.\n\nOn obtient : **Before the mirror, she looked at herself for a long time.**"
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "Choisis : \"The two boxers respected ... even after the fight.\" (himself, each other, ourselves)",
                    "solution_markdown": "\"The two boxers\" designe deux personnes distinctes, et \"respected\" implique une relation reciproque : chaque boxeur respecte l'autre. \"Himself\" est au singulier, incompatible avec le sujet pluriel \"the two boxers\" pris comme entites distinctes agissant l'une sur l'autre ; \"ourselves\" ne correspond pas au sujet a la troisieme personne.\n\nOn obtient : **The two boxers respected each other even after the fight.**"
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Complete avec le pronom qui convient et explique ton choix : \"The two neighbouring villages have been at war for years. They no longer trust ..., and even the children have learned to protect ... first.\"",
                    "solution_markdown": "Cette phrase contient deux blancs avec deux logiques differentes, ce qui exige d'appliquer le test de reciprocite separement a chacun.\n\nPremier blanc : \"they no longer trust ...\" - \"they\" designe les deux villages, entites distinctes qui ne se font plus confiance l'une envers l'autre : c'est une reciprocite, donc \"each other\".\n\nSecond blanc : \"the children have learned to protect ... first\" - ici, chaque enfant protege sa propre personne en priorite (avant de penser aux autres) : l'action revient sur celui qui l'accomplit, donc un pronom reflechi, \"themselves\" (accorde au sujet pluriel \"the children\").\n\nOn obtient : **They no longer trust each other, and even the children have learned to protect themselves first.**\n\nCet exercice montre qu'une meme phrase peut combiner les deux types de pronoms : chaque blanc doit etre analyse independamment selon le sens exact de l'action a cet endroit precis."
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Pose-toi toujours la question : est-ce que l'action s'echange entre deux sujets distincts, ou revient-elle sur celui qui l'accomplit ?",
                "Reciprocite entre deux ou plusieurs sujets distincts -> each other / one another.",
                "Action sur soi-meme -> myself, yourself, himself, herself, itself, ourselves, yourselves, themselves (accorde au sujet).",
                "Un sujet pluriel ne garantit pas automatiquement un pronom reflechi : verifie toujours le sens, pas seulement le nombre.",
                "\"Both\" n'est ni reciproque ni reflechi : c'est un pronom/determinant de quantite, a ne jamais confondre avec les deux categories precedentes.",
                "Au Bac, ce point revient regulierement en QCM de grammaire, souvent avec \"both\" comme distracteur pour piéger les candidats peu attentifs."
            ]
        }
    ]
})

# ---------- 7. VOIX PASSIVE DISCOURS RAPPORTE ----------
COURSES.append({
    "_slug": "passif-discours-rapporte",
    "cours_id": "cours-passif-discours-rapporte-bac-c-d-angl-2004",
    "meta": {
        "titre": "Passer a la voix passive un ordre rapporte (verbe + COD + to-infinitif)",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Grammaire - voix passive",
        "duree_estimee_min": 20,
        "tags": ["voix passive", "discours rapporte", "told to", "reecriture"],
        "statut": "brouillon"
    },
    "source": base_source("1", "rdm-bac-c-d-anglais-2004-cameroun-ex1-qA.3-0"),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "\"The Principal told the latecomers to sweep the floor.\" On te demande de reecrire cette phrase en commencant par \"The latecomer...\". Le reflexe naturel est de penser au discours indirect avec \"that\", mais ce n'est pas ce qui est demande : commencer par le destinataire de l'ordre est le signal d'un passage a la voix passive. Ce cours t'apprend a reconnaitre ce signal et a appliquer la transformation sans erreur."
        },
        {
            "type": "prerequis",
            "items": [
                "Connaitre la formation de la voix passive de base (be + participe passe)",
                "Reconnaitre la structure active verbe + complement d'objet direct + to-infinitif (\"tell someone to do something\")",
                "Conjuguer be au preterit (was/were) pour former un passif au passe"
            ]
        },
        {
            "type": "regle",
            "titre": "Le complement de l'ordre devient sujet du passif, suivi de be + participe passe + to-infinitif",
            "contenu_markdown": "Quand une phrase active du type \"quelqu'un a dit/ordonne a quelqu'un de faire quelque chose\" (verbe + complement d'objet direct + to + infinitif) doit etre reformulee en mettant en valeur le destinataire de l'ordre, on utilise la voix passive. Le complement d'objet direct de la phrase active (la personne qui recoit l'ordre) devient le sujet de la phrase passive, le verbe se conjugue avec \"be\" au meme temps que dans l'actif suivi du participe passe du verbe d'origine, et l'infinitif complet (\"to + verbe\") reste inchange apres.",
            "formule_principale": "Complement (actif) + be (conjugue au temps de l'actif) + participe passe + to + infinitif  [+ by + agent, facultatif]",
            "variantes": []
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "Reecris en commencant par \"The latecomer...\" : \"The Principal told the latecomers to sweep the floor.\"",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Identifier les elements de la phrase active",
                    "justification": "Il faut reperer precisement sujet, verbe, complement d'objet direct et infinitif avant toute transformation",
                    "resultat_markdown": "Sujet : \"the Principal\" / Verbe : \"told\" (preterit de \"tell\") / COD : \"the latecomers\" / Infinitif : \"to sweep the floor\""
                },
                {
                    "numero": 2,
                    "action": "Placer le complement d'objet direct comme sujet de la phrase passive",
                    "justification": "L'enonce impose de commencer par \"The latecomer(s)\", ce qui correspond exactement au complement d'objet direct de la phrase active",
                    "resultat_markdown": "\"The latecomers ...\""
                },
                {
                    "numero": 3,
                    "action": "Conjuguer be au meme temps que le verbe actif, suivi du participe passe de tell",
                    "justification": "\"Told\" est au preterit ; le passif reprend le meme temps avec \"were\" (accord avec le sujet pluriel \"the latecomers\") + le participe passe \"told\"",
                    "resultat_markdown": "\"were told\""
                },
                {
                    "numero": 4,
                    "action": "Conserver l'infinitif complet tel quel apres le participe passe",
                    "justification": "L'infinitif \"to sweep the floor\" ne change pas de forme, il indique toujours l'action que le sujet doit accomplir",
                    "resultat_markdown": "**The latecomers were told to sweep the floor (by the Principal).**"
                }
            ],
            "conclusion_markdown": "L'agent \"by the Principal\" reste facultatif puisqu'il est deja connu du contexte, mais la phrase reste grammaticalement complete et correcte avec ou sans lui."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Basculer vers le discours indirect avec that : \"The latecomers, the Principal said that they should sweep the floor.\"",
                    "pourquoi_faux": "Cette structure change completement la construction demandee et produit une phrase agrammaticale en commencant par \"The latecomers\" suivi d'une virgule sans role syntaxique clair ; l'enonce demande une transformation a la voix passive, pas un discours indirect.",
                    "correction_markdown": "Des que l'enonce impose de commencer par le destinataire de l'ordre (ici \"the latecomer(s)\"), pense immediatement voix passive, pas discours indirect avec that."
                },
                {
                    "erreur_markdown": "Oublier de conjuguer be au bon temps : \"The latecomers are told to sweep the floor.\"",
                    "pourquoi_faux": "La phrase active est au preterit (\"told\"), ce qui impose \"were\" au passif, pas \"are\" (present). Changer le temps du verbe change le moment ou l'ordre a ete donne.",
                    "correction_markdown": "Verifie toujours le temps du verbe actif avant de conjuguer be dans le passif : le temps doit rester identique entre l'actif et le passif."
                },
                {
                    "erreur_markdown": "Transformer aussi l'infinitif en gerondif ou en forme conjuguee : \"The latecomers were told sweeping the floor.\"",
                    "pourquoi_faux": "L'infinitif complet (\"to + verbe\") apres \"told\" ne change jamais de forme lors du passage a la voix passive, ce n'est que le verbe principal (told/tell) qui subit la transformation.",
                    "correction_markdown": "Garde systematiquement \"to + base verbale\" apres le participe passe du verbe introducteur (told, asked, ordered...)."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Reecris en commencant par \"The students...\" : \"The teacher asked the students to remain silent.\"",
                    "solution_markdown": "Le complement d'objet direct \"the students\" devient sujet du passif ; \"asked\" (preterit) devient \"were asked\" ; l'infinitif \"to remain silent\" reste inchange.\n\nOn obtient : **The students were asked to remain silent (by the teacher).**"
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "Reecris en commencant par \"The workers...\" : \"The manager ordered the workers to finish the project before Friday.\"",
                    "solution_markdown": "\"The workers\", complement d'objet direct, devient sujet ; \"ordered\" (preterit) devient \"were ordered\" ; le reste de l'infinitif (\"to finish the project before Friday\") reste inchange, y compris le complement de temps qui suit.\n\nOn obtient : **The workers were ordered to finish the project before Friday (by the manager).**"
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Reecris en commencant par \"The passengers...\", en conservant le sens exact : \"The airline has advised all the passengers not to bring liquids in their hand luggage.\"",
                    "solution_markdown": "Cet exercice combine deux difficultes : un present perfect (\"has advised\") a transformer au passif, et un infinitif deja negatif a conserver tel quel.\n\nLe complement d'objet direct \"all the passengers\" devient sujet. Le verbe \"has advised\" est au present perfect ; au passif, on conjugue \"have/has been\" + participe passe : \"have been advised\" (accord pluriel avec \"the passengers\"). L'infinitif negatif \"not to bring liquids in their hand luggage\" reste identique, seul le \"not\" garde sa place juste avant \"to\".\n\nOn obtient : **All the passengers have been advised not to bring liquids in their hand luggage (by the airline).**\n\nCet exercice montre que la regle de transformation (COD -> sujet, be conjugue au meme temps + participe passe, infinitif inchange) s'applique a n'importe quel temps verbal de l'actif, pas seulement au preterit simple."
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Verbe + COD + to-infinitif a l'actif (tell, ask, order, advise, warn...) se transforme au passif en mettant le COD en position de sujet.",
                "Conjugue toujours be au meme temps que le verbe actif : preterit -> was/were, present perfect -> have/has been, present simple -> am/is/are.",
                "L'infinitif complet (\"to + verbe\", negatif ou non) ne change jamais de forme pendant la transformation.",
                "Quand l'enonce impose de commencer par le destinataire de l'ordre, c'est le signal d'un passage a la voix passive, pas d'un discours indirect avec that.",
                "L'agent introduit par \"by\" reste toujours facultatif quand il est deja connu du contexte."
            ]
        }
    ]
})

# ---------- 11. QUESTION TAGS APRES ADVERBES NEGATIFS ----------
COURSES.append({
    "_slug": "question-tags-adverbes-negatifs",
    "cours_id": "cours-question-tags-adverbes-negatifs-bac-c-d-angl-2004",
    "meta": {
        "titre": "Construire une question tag apres un adverbe a valeur negative (hardly, never, seldom...)",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Grammaire - question tags",
        "duree_estimee_min": 20,
        "tags": ["question tags", "hardly", "adverbes negatifs", "polarite"],
        "statut": "brouillon"
    },
    "source": base_source("1", "rdm-bac-c-d-anglais-2004-cameroun-ex1-qB.2-0"),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "\"Peter hardly ever does the right thing, ... he?\" La phrase n'a pas de \"not\" visible, alors pourquoi le tag attendu est-il affirmatif et non negatif ? Ce piege classique du Bac repose sur un principe simple une fois qu'on le connait : certains adverbes sont negatifs par leur sens, meme quand la phrase est grammaticalement a la forme affirmative. Ce cours te donne la liste et le reflexe pour ne plus jamais te tromper."
        },
        {
            "type": "prerequis",
            "items": [
                "Connaitre la regle generale des question tags : inversion de polarite entre la phrase principale et le tag",
                "Savoir accorder l'auxiliaire du tag au sujet et au temps de la phrase principale"
            ]
        },
        {
            "type": "regle",
            "titre": "Le sens negatif de l'adverbe prime sur la forme grammaticale de la phrase",
            "contenu_markdown": "La regle generale des question tags est l'inversion de polarite : une phrase principale affirmative appelle un tag negatif, une phrase principale negative appelle un tag affirmatif. Les adverbes \"hardly\", \"barely\", \"scarcely\", \"seldom\", \"rarely\" et \"never\" ont un sens negatif (presque jamais, rarement, jamais) meme lorsque la phrase ne contient aucune negation grammaticale visible (\"not\", \"n't\"). Une phrase qui les contient doit donc etre traitee comme negative pour la construction du tag, ce qui impose un tag affirmatif.",
            "formule_principale": "hardly / barely / scarcely / seldom / rarely / never + phrase affirmative en forme -> tag AFFIRMATIF",
            "variantes": []
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "Complete : \"Peter hardly ever does the right thing, ... he?\" (do, does, doesn't)",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Verifier la forme grammaticale de la phrase principale",
                    "justification": "Il faut d'abord constater qu'aucune negation grammaticale (\"not\", \"n't\") n'apparait dans la phrase",
                    "resultat_markdown": "\"Peter hardly ever does the right thing\" - pas de \"not\" visible, forme grammaticalement affirmative"
                },
                {
                    "numero": 2,
                    "action": "Identifier le sens reel de la phrase grace a l'adverbe hardly",
                    "justification": "\"Hardly ever\" signifie \"presque jamais\", ce qui donne un sens negatif a la phrase malgre l'absence de negation grammaticale",
                    "resultat_markdown": "sens reel : Peter fait rarement/presque jamais la bonne chose -> phrase a traiter comme negative"
                },
                {
                    "numero": 3,
                    "action": "Appliquer l'inversion de polarite a partir du sens, pas de la forme",
                    "justification": "Une phrase de sens negatif appelle un tag affirmatif",
                    "resultat_markdown": "tag affirmatif requis"
                },
                {
                    "numero": 4,
                    "action": "Accorder l'auxiliaire du tag au temps et au sujet de la principale",
                    "justification": "Le verbe principal \"does\" est au present simple, troisieme personne du singulier ; le sujet du tag reprend \"he\" (Peter)",
                    "resultat_markdown": "**Peter hardly ever does the right thing, does he?**"
                }
            ],
            "conclusion_markdown": "Le choix de \"does\" (et non \"doesn't\") repose entierement sur le sens negatif de \"hardly ever\", pas sur la forme grammaticale visible de la phrase."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Choisir \"doesn't\" parce que la phrase semble affirmative en surface (aucun \"not\" visible)",
                    "pourquoi_faux": "C'est exactement le piege que l'exercice teste : s'arreter a la forme grammaticale sans analyser le sens de l'adverbe conduit a l'erreur inverse de celle attendue.",
                    "correction_markdown": "Avant de construire un tag, verifie toujours s'il y a un adverbe a sens negatif (hardly, barely, scarcely, seldom, rarely, never) dans la phrase, meme en l'absence de \"not\"."
                },
                {
                    "erreur_markdown": "Oublier d'accorder l'auxiliaire au temps ou a la personne du verbe principal : \"Peter hardly ever does the right thing, do he?\"",
                    "pourquoi_faux": "Le tag doit toujours reprendre exactement le temps et la personne du verbe de la principale ; \"do\" ne s'accorde pas avec un sujet a la troisieme personne du singulier au present simple.",
                    "correction_markdown": "Verifie systematiquement deux choses separement : la polarite (affirmatif/negatif selon le sens) et l'accord grammatical (temps + personne) de l'auxiliaire du tag."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Ajoute le tag qui convient : \"She never arrives late, ... ?\"",
                    "solution_markdown": "\"Never\" a un sens negatif, meme si la phrase est grammaticalement affirmative (pas de \"not\"). Le tag doit donc etre affirmatif, accorde au present simple et au sujet \"she\".\n\nOn obtient : **She never arrives late, does she?**"
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "Ajoute le tag qui convient : \"The workers seldom complain about their salary, ... ?\"",
                    "solution_markdown": "\"Seldom\" (rarement) fait partie des adverbes a sens negatif. La phrase est grammaticalement affirmative mais son sens est negatif : le tag doit donc etre affirmatif. Le sujet \"the workers\" est pluriel, ce qui impose \"do\" au present simple.\n\nOn obtient : **The workers seldom complain about their salary, do they?**"
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Ajoute le tag qui convient et explique pourquoi le raisonnement change par rapport aux exercices precedents : \"He hasn't hardly finished his homework, ... ?\"",
                    "solution_markdown": "Cette phrase combine deja une negation grammaticale explicite (\"hasn't\") avec un adverbe a sens negatif (\"hardly\") - une double negation qui n'est en realite pas standard en anglais correct (l'anglais standard n'accumule pas deux marqueurs negatifs dans la meme proposition). La phrase correcte attendue en anglais standard serait plutot \"He has hardly finished his homework\" (sans \"not/n't\"), \"hardly\" portant deja a lui seul le sens negatif.\n\nEn corrigeant d'abord la phrase vers la forme standard \"He has hardly finished his homework\", on applique la meme regle que dans les exercices precedents : \"hardly\" donne un sens negatif malgre l'absence de \"not\", donc le tag est affirmatif, accorde au present perfect (has) et au sujet \"he\".\n\nOn obtient : **He has hardly finished his homework, has he?**\n\nCet exercice montre qu'il faut d'abord verifier qu'il n'y a pas de negation grammaticale redondante avec l'adverbe negatif avant meme de construire le tag : en anglais standard, \"hardly\" porte deja la negation a lui seul."
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Hardly, barely, scarcely, seldom, rarely et never ont un sens negatif meme sans \"not\" ni \"n't\" dans la phrase.",
                "Une phrase contenant l'un de ces adverbes se traite comme negative pour la construction du tag : le tag doit alors etre affirmatif.",
                "Verifie toujours deux choses separement : la polarite (a partir du sens, pas seulement de la forme) et l'accord de l'auxiliaire (temps + personne).",
                "En anglais standard, on n'accumule pas \"not/n't\" et un adverbe negatif comme \"hardly\" dans la meme proposition.",
                "Ce piege est un classique des QCM de grammaire au Bac : des que tu vois hardly/never/seldom, pense immediatement tag affirmatif."
            ]
        }
    ]
})

# ---------- 13. CONDITION NEGATIVE AVEC WITHOUT ----------
COURSES.append({
    "_slug": "condition-without",
    "cours_id": "cours-condition-without-bac-c-d-angl-2004",
    "meta": {
        "titre": "Exprimer la condition negative avec Without",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Condition et hypothese",
        "duree_estimee_min": 18,
        "tags": ["without", "condition", "reecriture"],
        "statut": "brouillon"
    },
    "source": base_source("1", "rdm-bac-c-d-anglais-2004-cameroun-ex1-qA.2-0"),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "\"You can only travel abroad if you have a passport.\" Comment dire la meme chose en commencant par \"Without\" ? Cette transformation, frequente dans les exercices de reecriture du Bac, demande de bien comprendre que \"without\" ne se construit jamais comme \"if\" : il remplace toute une condition par un simple nom ou un gerondif, tout en inversant le sens de la proposition principale. Ce cours te montre la methode complete."
        },
        {
            "type": "prerequis",
            "items": [
                "Reconnaitre une proposition conditionnelle introduite par if",
                "Savoir transformer un verbe conjugue en un groupe nominal correspondant"
            ]
        },
        {
            "type": "regle",
            "titre": "Without + nom/V-ing, et inversion de la principale",
            "contenu_markdown": "\"Without\" exprime une condition negative : il signifie \"en l'absence de\", \"si on n'a pas\". Il se construit avec un nom, un pronom ou un gerondif, jamais avec une proposition complete (sujet + verbe conjugue). Pour transformer une phrase du type \"You can only... if you have...\" (condition restrictive positive), on remplace \"if you have + nom\" par \"without + nom\", et on inverse le verbe de la proposition principale a la forme negative, puisque \"without\" indique deja l'absence de la condition necessaire.",
            "formule_principale": "Without + nom/pronom/V-ing, sujet + verbe NEGATIF (l'inverse de la proposition principale d'origine)",
            "variantes": []
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "Reecris en commencant par \"Without\" : \"You can only travel abroad if you have a passport.\"",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Identifier la condition et son sens exact",
                    "justification": "La structure \"only... if\" signifie que le passeport est une condition indispensable pour voyager a l'etranger",
                    "resultat_markdown": "condition : avoir un passeport = condition necessaire au voyage"
                },
                {
                    "numero": 2,
                    "action": "Transformer la condition \"if you have a passport\" en groupe nominal",
                    "justification": "Without exige un nom, pas une proposition ; \"you have a passport\" se reduit au nom central \"a passport\"",
                    "resultat_markdown": "\"without a passport\""
                },
                {
                    "numero": 3,
                    "action": "Inverser la proposition principale a la forme negative",
                    "justification": "\"Without\" indique deja l'absence de la condition ; la consequence logique (ne pas pouvoir voyager) doit donc etre exprimee explicitement au negatif dans la principale",
                    "resultat_markdown": "\"you can only travel abroad\" -> \"you cannot travel abroad\""
                },
                {
                    "numero": 4,
                    "action": "Assembler la phrase complete",
                    "justification": "Combiner le groupe \"without + nom\" et la principale negative donne la reformulation complete demandee",
                    "resultat_markdown": "**Without a passport, you cannot travel abroad.**"
                }
            ],
            "conclusion_markdown": "La transformation repose sur deux mouvements simultanes : reduire la condition a un nom apres without, et rendre la proposition principale negative pour conserver le sens exact de la phrase d'origine."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Garder la principale a la forme affirmative : \"Without a passport, you can travel abroad.\"",
                    "pourquoi_faux": "Cette erreur inverse completement le sens de la phrase d'origine : elle affirmerait qu'on peut voyager meme sans passeport, exactement le contraire de ce que dit la phrase de depart.",
                    "correction_markdown": "Rappelle-toi que \"without\" porte deja l'idee d'absence : la proposition principale doit donc exprimer explicitement l'impossibilite (forme negative) pour que le sens global reste correct."
                },
                {
                    "erreur_markdown": "Construire \"without\" avec une proposition complete : \"Without you have a passport, you cannot travel.\"",
                    "pourquoi_faux": "\"Without\" ne peut jamais etre suivi d'un sujet et d'un verbe conjugue, uniquement d'un nom, d'un pronom ou d'un gerondif.",
                    "correction_markdown": "Reduis toujours la condition a son element nominal central (\"a passport\") ou a un gerondif (\"having a passport\") avant de la placer apres without."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Reecris en commencant par \"Without\" : \"You can only enter the exam room if you have your ID card.\"",
                    "solution_markdown": "La condition \"if you have your ID card\" se reduit au groupe nominal \"your ID card\". La principale \"you can only enter\" devient negative : \"you cannot enter\".\n\nOn obtient : **Without your ID card, you cannot enter the exam room.**"
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "Reecris en commencant par \"Without\" : \"If you don't work hard, you will not succeed in life.\"",
                    "solution_markdown": "Ici la condition est deja negative dans l'original (\"if you don't work hard\"), ce qui inverse le raisonnement habituel : \"working hard\" (sous forme de gerondif, puisqu'il s'agit d'une action et non d'un objet concret) est la condition necessaire absente que \"without\" doit exprimer. La proposition principale, deja negative dans l'original, reste negative apres transformation puisque without porte lui-meme le sens de l'absence.\n\nOn obtient : **Without working hard, you will not succeed in life.**\n\nCet exercice montre que lorsque la condition de depart est deja negative (\"if you don't...\"), c'est l'action positive correspondante (\"working hard\") qui passe apres without, sans changer une seconde fois la polarite de la principale."
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Reecris en commencant par \"Without\" en gardant le meme sens : \"The company would have gone bankrupt if the new investors had not intervened.\"",
                    "solution_markdown": "Cette phrase est un conditionnel de type 3 (hypothese irrealisable dans le passe), ce qui complique la transformation : la condition negative au passe (\"if the new investors had not intervened\") doit devenir un groupe nominal ou un gerondif positif apres without, et la principale doit rester au conditionnel passe.\n\n\"If the new investors had not intervened\" signifie que les investisseurs sont effectivement intervenus (le contraire de l'hypothese negative). L'intervention elle-meme, exprimee positivement, devient \"the intervention of the new investors\" ou \"the new investors' intervention\".\n\nComme la condition d'origine etait deja negative (\"had not intervened\"), sa version positive (\"l'intervention a eu lieu\") est ce qui a empeche la faillite : on la place donc apres without, et la principale garde sa forme telle quelle (\"would have gone bankrupt\"), puisque without exprime deja, en creux, l'absence de cette intervention.\n\nOn obtient : **Without the intervention of the new investors, the company would have gone bankrupt.**\n\nCet exercice combine la regle de without avec un conditionnel de type 3 : le principe reste le meme (without + nom, principale qui exprime la consequence de l'absence), mais applique a une hypothese passee plutot qu'a une condition presente."
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Without exprime une condition negative et se construit uniquement avec un nom, un pronom ou un gerondif, jamais avec une proposition complete.",
                "Reduis toujours la condition de depart a son element nominal central avant de la placer apres without.",
                "Si la condition d'origine etait positive (\"if you have...\"), la principale devient negative apres without.",
                "Si la condition d'origine etait deja negative (\"if you don't...\" ou \"if... had not...\"), c'est sa version positive qui passe apres without, et la principale garde sa forme.",
                "Verifie toujours, une fois la phrase reconstruite, qu'elle exprime exactement le meme sens que la phrase de depart - c'est le meilleur controle avant de rendre ta copie."
            ]
        }
    ]
})

# ---------- 14. SO...THAT ----------
COURSES.append({
    "_slug": "so-that-consequence",
    "cours_id": "cours-so-that-consequence-bac-c-d-angl-2004",
    "meta": {
        "titre": "Exprimer la consequence avec so...that",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Expression de la consequence",
        "duree_estimee_min": 18,
        "tags": ["so...that", "too...to", "consequence", "intensite"],
        "statut": "brouillon"
    },
    "source": base_source("1", "rdm-bac-c-d-anglais-2004-cameroun-ex1-qB.5-0"),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "\"The film we watched was ... boring that everybody walked out.\" Faut-il \"too\", \"very\" ou \"so\" ? Les trois mots renforcent un adjectif, mais un seul d'entre eux peut introduire une consequence avec \"that\". Ce cours t'apprend a reconnaitre le signal qui impose \"so\" et a eviter la confusion frequente avec \"too\"."
        },
        {
            "type": "prerequis",
            "items": [
                "Reconnaitre un adjectif et sa fonction dans une phrase",
                "Distinguer une proposition introduite par that d'un infinitif introduit par to"
            ]
        },
        {
            "type": "regle",
            "titre": "So + adjectif + that + consequence, a ne pas confondre avec too...to et very",
            "contenu_markdown": "\"So + adjectif + that + proposition\" exprime une consequence directe liee a une intensite : l'adjectif est tellement marque qu'il entraine le resultat exprime dans la proposition introduite par \"that\". \"Too + adjectif + to + infinitif\" exprime au contraire une impossibilite (l'intensite empeche une action), et se construit avec un infinitif, jamais avec \"that\". \"Very\" est un simple renforcateur d'intensite, sans aucun lien de consequence exprime : il ne peut etre suivi ni de \"that + proposition\" ni de \"to + infinitif\" dans ce sens.",
            "formule_principale": "so + adjectif + that + proposition (consequence)  |  too + adjectif + to + infinitif (impossibilite)  |  very + adjectif (simple intensite, sans suite logique)",
            "variantes": []
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "Complete : \"The film we watched was ... boring that everybody walked out.\" (too, very, so)",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Reperer ce qui suit l'adjectif dans la phrase",
                    "justification": "La nature du mot qui suit l'adjectif (that + proposition, ou to + infinitif, ou rien) determine directement quel renforcateur est grammaticalement possible",
                    "resultat_markdown": "\"boring **that** everybody walked out\" - presence de \"that\" suivi d'une proposition complete (sujet + verbe)"
                },
                {
                    "numero": 2,
                    "action": "Eliminer \"too\", incompatible avec that + proposition",
                    "justification": "\"Too\" ne peut etre suivi que d'un infinitif (\"too boring to watch\"), jamais de \"that\" suivi d'une proposition complete",
                    "resultat_markdown": "\"too\" elimine"
                },
                {
                    "numero": 3,
                    "action": "Eliminer \"very\", qui n'introduit aucune consequence",
                    "justification": "\"Very\" est un simple renforcateur ; il n'existe pas de structure \"very + adjectif + that + consequence\" en anglais standard",
                    "resultat_markdown": "\"very\" elimine"
                },
                {
                    "numero": 4,
                    "action": "Retenir \"so\", seul compatible avec that + proposition de consequence",
                    "justification": "\"So + adjectif + that\" est exactement la structure qui introduit une consequence exprimee par une proposition complete",
                    "resultat_markdown": "**The film we watched was so boring that everybody walked out.**"
                }
            ],
            "conclusion_markdown": "Le test decisif est ce qui suit immediatement l'adjectif : la presence de \"that + proposition\" impose \"so\", jamais \"too\" ni \"very\"."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Choisir \"too\" par habitude parce qu'il ressemble a une expression d'intensite forte : \"too boring that everybody walked out\"",
                    "pourquoi_faux": "\"Too\" ne se construit jamais avec \"that\" suivi d'une proposition complete ; il appelle systematiquement un infinitif (\"too boring to watch till the end\"), une structure differente de celle testee ici.",
                    "correction_markdown": "Des que tu vois \"that\" suivi d'un sujet et d'un verbe conjugue apres l'adjectif, pense automatiquement a \"so\", jamais a \"too\"."
                },
                {
                    "erreur_markdown": "Utiliser \"very\" en pensant qu'il s'agit du renforcateur le plus neutre et donc le plus sur : \"very boring that everybody walked out\"",
                    "pourquoi_faux": "\"Very\" n'introduit aucune structure de consequence en anglais standard ; la phrase resultante serait grammaticalement incorrecte, meme si \"very\" est parfaitement correct seul devant un adjectif sans suite logique.",
                    "correction_markdown": "Reserve \"very\" aux phrases ou l'adjectif n'est suivi d'aucune consequence explicite (\"The film was very boring.\", point final)."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Complete avec so ou too : \"The soup was ... hot that she could not drink it immediately.\"",
                    "solution_markdown": "La presence de \"that\" suivi d'une proposition complete (\"she could not drink it\") impose \"so\", jamais \"too\".\n\nOn obtient : **The soup was so hot that she could not drink it immediately.**"
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "Transforme cette phrase avec \"so...that\" en une phrase equivalente avec \"too...to\" : \"The bag was so heavy that she could not carry it.\"",
                    "solution_markdown": "\"Too + adjectif + to + infinitif\" exprime la meme idee d'impossibilite que \"so...that\" quand la proposition introduite par that contient une negation (\"could not\"). Il faut supprimer la negation et la proposition complete pour les remplacer par un infinitif positif.\n\n\"She could not carry it\" devient l'infinitif positif \"to carry\", le sujet de l'infinitif restant implicite car identique au sujet de la principale.\n\nOn obtient : **The bag was too heavy for her to carry.**\n\n(Le sujet de l'infinitif, different de celui de la principale implicite, est reintroduit avec \"for her\".)"
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Complete et justifie ton choix parmi so/too/very : \"The lecture was ... complicated for the first-year students to understand without help.\"",
                    "solution_markdown": "Cet exercice combine un adjectif complexe (\"complicated\"), un infinitif introduit par \"for\" (sujet different de la principale) et l'absence de \"that\" : ces trois indices pointent vers \"too\", pas \"so\".\n\nOn repere d'abord ce qui suit l'adjectif : \"for the first-year students to understand\" est un infinitif avec sujet propre introduit par \"for\", pas une proposition avec \"that\". Cette structure (\"for + sujet + to + infinitif\") est exactement celle de \"too\", jamais celle de \"so\" (qui exige \"that\") ni de \"very\" (qui n'a pas de suite logique).\n\nOn obtient : **The lecture was too complicated for the first-year students to understand without help.**\n\nCet exercice montre que le meme test s'applique meme quand l'infinitif a un sujet propre different de celui de la principale (introduit par \"for\") : c'est toujours la structure qui suit l'adjectif, infinitif ou that-proposition, qui determine le choix entre too et so."
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Regarde toujours ce qui suit l'adjectif : \"that + proposition complete\" impose so, \"to + infinitif\" impose too, l'absence des deux limite le choix a very.",
                "So + adjectif + that exprime une consequence directe liee a une forte intensite.",
                "Too + adjectif + to exprime une impossibilite, avec un sujet d'infinitif introduit par for si different de celui de la principale.",
                "Very renforce simplement l'adjectif, sans jamais introduire de consequence explicite.",
                "Ce point grammatical est un classique des QCM du Bac : entraine-toi a repérer immediatement la structure qui suit l'adjectif avant de choisir."
            ]
        }
    ]
})

# ---------- 15. NOT UNTIL ----------
COURSES.append({
    "_slug": "not-until",
    "cours_id": "cours-not-until-bac-c-d-angl-2004",
    "meta": {
        "titre": "Exprimer la condition temporelle avec Not... until",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Condition et temps",
        "duree_estimee_min": 18,
        "tags": ["not until", "until", "reecriture", "condition temporelle"],
        "statut": "brouillon"
    },
    "source": base_source("1", "rdm-bac-c-d-anglais-2004-cameroun-ex1-qA.5-0"),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "\"You can only enter the bus after buying your ticket.\" Comment reformuler cette idee avec \"Until\" ? Cette transformation demande de comprendre que \"until\" marque le point exact a partir duquel une action devient possible, ce qui impose de rendre la proposition principale negative. Ce cours te montre la methode etape par etape."
        },
        {
            "type": "prerequis",
            "items": [
                "Reconnaitre une structure restrictive avec only... after + V-ing",
                "Savoir construire une proposition avec until + sujet + verbe"
            ]
        },
        {
            "type": "regle",
            "titre": "Until marque le point a partir duquel une action devient possible",
            "contenu_markdown": "\"Not... until\" exprime qu'une action ne peut avoir lieu qu'apres qu'une autre condition soit remplie : elle est impossible jusqu'a ce moment precis, puis devient possible. La structure \"You can only... after + V-ing\" (condition restrictive positive) se reformule en rendant la proposition principale negative et en introduisant la condition par \"until\" suivi d'un sujet et d'un verbe conjugue (au lieu du gerondif utilise apres \"after\").",
            "formule_principale": "Sujet + cannot/could not + verbe + until + sujet + verbe (conjugue)",
            "variantes": [
                {
                    "nom": "Until en tete de phrase",
                    "quand_utiliser": "La proposition en \"until\" peut aussi ouvrir la phrase pour la mettre en valeur, suivie d'une virgule puis de la principale negative.",
                    "contenu_markdown": "\"Until you buy your ticket, you cannot enter the bus.\" produit exactement le meme sens que \"You cannot enter the bus until you buy your ticket.\", seul l'ordre des propositions change."
                }
            ]
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "Reecris en commencant par \"Until\" : \"You can only enter the bus after buying your ticket.\"",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Identifier la condition restrictive et son sens exact",
                    "justification": "\"Only... after buying your ticket\" signifie que l'achat du billet est la condition prealable indispensable pour entrer dans le bus",
                    "resultat_markdown": "condition : achat du billet = etape prealable obligatoire"
                },
                {
                    "numero": 2,
                    "action": "Transformer le gerondif apres after en proposition avec until",
                    "justification": "\"Until\" se construit avec un sujet et un verbe conjugue, contrairement a \"after\" qui accepte le gerondif ; \"buying your ticket\" devient \"you buy your ticket\"",
                    "resultat_markdown": "\"until you buy your ticket\""
                },
                {
                    "numero": 3,
                    "action": "Rendre la proposition principale negative",
                    "justification": "\"Until\" marque un point avant lequel l'action est impossible : il faut donc exprimer explicitement cette impossibilite au negatif dans la principale",
                    "resultat_markdown": "\"you can only enter the bus\" -> \"you cannot enter the bus\""
                },
                {
                    "numero": 4,
                    "action": "Assembler la phrase complete en commencant par Until",
                    "justification": "L'enonce impose de commencer par \"Until\", donc la proposition temporelle ouvre la phrase, suivie d'une virgule puis de la principale",
                    "resultat_markdown": "**Until you buy your ticket, you cannot enter the bus.**"
                }
            ],
            "conclusion_markdown": "La transformation combine deux mouvements : passer du gerondif (\"after + V-ing\") a une proposition complete (\"until + sujet + verbe\"), et rendre la principale negative pour marquer l'impossibilite avant que la condition ne soit remplie."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Garder la principale a la forme affirmative : \"Until you buy your ticket, you can enter the bus.\"",
                    "pourquoi_faux": "Cette phrase affirmerait qu'on peut entrer dans le bus avant meme d'avoir achete son billet, ce qui inverse completement le sens original.",
                    "correction_markdown": "Rappelle-toi qu'until marque une impossibilite avant le moment cite : la principale doit donc etre negative pour respecter le sens de la phrase d'origine."
                },
                {
                    "erreur_markdown": "Garder le gerondif apres until : \"Until buying your ticket, you cannot enter the bus.\"",
                    "pourquoi_faux": "\"Until\" appelle normalement une proposition complete (sujet + verbe conjugue) quand il introduit une condition avec un sujet exprime, pas un gerondif comme \"after\" ou \"before\" peuvent parfois l'accepter dans d'autres contextes.",
                    "correction_markdown": "Transforme toujours le gerondif en proposition complete apres until : \"until you buy\", pas \"until buying\"."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Reecris en commencant par \"Until\" : \"You can only start the exam after receiving the signal from the supervisor.\"",
                    "solution_markdown": "\"After receiving the signal\" devient \"until you receive the signal\" ; la principale \"you can only start\" devient negative \"you cannot start\".\n\nOn obtient : **Until you receive the signal from the supervisor, you cannot start the exam.**"
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "Reecris en commencant par \"Until\" : \"The shop only opens after the manager arrives.\"",
                    "solution_markdown": "\"After the manager arrives\" est deja une proposition complete (pas un gerondif), il suffit de la faire suivre de \"until\" a la place de \"after\". La principale \"the shop only opens\" devient negative : \"the shop does not open\".\n\nOn obtient : **Until the manager arrives, the shop does not open.**\n\nCet exercice montre que la regle s'applique de la meme facon que la condition de depart utilise \"after + V-ing\" ou \"after + proposition complete\" : dans les deux cas, until est suivi d'une proposition complete, et la principale devient negative."
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Reecris en commencant par \"Not until\" (structure avec inversion) en gardant le meme sens : \"The team only celebrated after the referee confirmed the final score.\"",
                    "solution_markdown": "Quand \"Not until\" ouvre la phrase pour la mettre en valeur avec emphase, il declenche une inversion du sujet et de l'auxiliaire dans la proposition principale, comme apres d'autres expressions negatives placees en tete de phrase (never, rarely, hardly...).\n\n\"After the referee confirmed the final score\" devient \"until the referee confirmed the final score\". La principale \"the team celebrated\" doit passer a une structure avec inversion apres \"Not until + condition\", en utilisant l'auxiliaire \"did\" pour porter l'inversion (puisque \"celebrated\" est un verbe lexical simple au preterit).\n\nOn obtient : **Not until the referee confirmed the final score did the team celebrate.**\n\nCet exercice ajoute une difficulte supplementaire a la regle de base : quand \"Not until\" ouvre la phrase avec une intention d'emphase, la principale ne se contente pas de passer au negatif normal, elle subit une inversion sujet-auxiliaire, comme les autres structures negatives emphatiques en tete de phrase."
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Not until exprime qu'une action est impossible avant qu'une condition precise ne soit remplie.",
                "Transforme systematiquement le gerondif ou la proposition apres after en une proposition complete apres until (sujet + verbe conjugue).",
                "Rends toujours la proposition principale negative pour exprimer l'impossibilite avant le moment marque par until.",
                "Not until en tete de phrase declenche une inversion sujet-auxiliaire dans la principale, comme les autres negations emphatiques placees en debut de phrase.",
                "Verifie toujours ta reformulation en te demandant si elle affirme bien l'impossibilite avant la condition, jamais apres."
            ]
        }
    ]
})

# ---------- 16. UNLESS + IMPERATIF ----------
COURSES.append({
    "_slug": "unless-imperatif",
    "cours_id": "cours-unless-imperatif-bac-c-d-angl-2004",
    "meta": {
        "titre": "Reformuler une condition en Unless par un imperatif + or/otherwise",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Condition et imperatif",
        "duree_estimee_min": 18,
        "tags": ["unless", "imperatif", "or", "otherwise", "reecriture"],
        "statut": "brouillon"
    },
    "source": base_source("1", "rdm-bac-c-d-anglais-2004-cameroun-ex1-qA.4-0"),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "\"Unless you work hard, you will not succeed.\" Comment reformuler cette phrase en commencant par un ordre direct, \"Work hard...\" ? Cette transformation classique du Bac fait le lien entre une structure conditionnelle et une structure imperative, deux facons differentes d'exprimer la meme exigence. Ce cours t'apprend a passer de l'une a l'autre sans perdre le sens."
        },
        {
            "type": "prerequis",
            "items": [
                "Connaitre le sens de unless (equivalent de if... not)",
                "Savoir former l'imperatif d'un verbe (base verbale seule, sans sujet)"
            ]
        },
        {
            "type": "regle",
            "titre": "Unless = if...not ; reformulation en imperatif + or/otherwise",
            "contenu_markdown": "\"Unless\" equivaut a \"if... not\" et introduit une condition negative : \"unless you work hard\" signifie exactement \"if you do not work hard\". On peut reformuler une phrase construite avec unless en une structure imperative suivie de \"or\" ou \"otherwise\" : l'imperatif reprend l'action positive attendue (le contraire de la condition negative de depart), et \"or\"/\"otherwise\" introduit la consequence qui aura lieu si cette action n'est pas accomplie.",
            "formule_principale": "Imperatif (action positive) + or / otherwise + consequence (inchangee par rapport a la principale d'origine)",
            "variantes": []
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "Reecris en commencant par \"Work hard\" : \"Unless you work hard, you will not succeed.\"",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Reformuler unless en if...not pour clarifier le sens",
                    "justification": "\"Unless you work hard\" equivaut exactement a \"if you do not work hard\", ce qui rend visible la condition negative sous-jacente",
                    "resultat_markdown": "\"unless you work hard\" = \"if you do not work hard\""
                },
                {
                    "numero": 2,
                    "action": "Identifier l'action positive attendue, contraire de la condition negative",
                    "justification": "L'imperatif doit porter l'action que la personne doit accomplir pour eviter la consequence negative : ici, travailler dur",
                    "resultat_markdown": "action positive attendue : \"work hard\""
                },
                {
                    "numero": 3,
                    "action": "Placer cette action a l'imperatif en tete de phrase",
                    "justification": "L'imperatif anglais utilise la base verbale seule, sans sujet ni auxiliaire",
                    "resultat_markdown": "\"Work hard\""
                },
                {
                    "numero": 4,
                    "action": "Ajouter or (ou otherwise) suivi de la consequence inchangee",
                    "justification": "\"Or\"/\"otherwise\" introduit ce qui se passera si l'ordre n'est pas suivi ; la consequence \"you will not succeed\" reste identique a celle de la phrase d'origine",
                    "resultat_markdown": "**Work hard or (otherwise) you will not succeed.**"
                }
            ],
            "conclusion_markdown": "La transformation ne change que la premiere partie de la phrase (la condition devient un ordre) ; la consequence exprimee apres or/otherwise reste rigoureusement identique a celle de la phrase de depart."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Changer la consequence apres or : \"Work hard or you will succeed.\"",
                    "pourquoi_faux": "Cette erreur inverse completement le sens : elle affirmerait que travailler dur entraine l'echec. La consequence apres or/otherwise doit toujours rester celle de la phrase d'origine, sans aucune modification de sa polarite.",
                    "correction_markdown": "Recopie la consequence de la principale d'origine telle quelle apres or/otherwise, sans y toucher : seule la premiere partie de la phrase (condition -> imperatif) change de forme."
                },
                {
                    "erreur_markdown": "Garder un sujet devant le verbe a l'imperatif : \"You work hard or you will not succeed.\"",
                    "pourquoi_faux": "Un imperatif anglais s'exprime uniquement par la base verbale, sans sujet exprime ; ajouter \"you\" devant le verbe transforme la phrase en un simple enonce, pas en un ordre.",
                    "correction_markdown": "Verifie que ta phrase commence directement par la base verbale (\"Work hard\"), jamais par un pronom sujet suivi du verbe."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Reecris en commencant par un imperatif suivi de or : \"Unless you hurry, you will miss the bus.\"",
                    "solution_markdown": "\"Unless you hurry\" equivaut a \"if you don't hurry\". L'action positive attendue est \"hurry\", a l'imperatif ; la consequence \"you will miss the bus\" reste inchangee apres or.\n\nOn obtient : **Hurry or you will miss the bus.**"
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "Reecris en commencant par un imperatif suivi de otherwise : \"Unless the workers respect the safety rules, they will get injured.\"",
                    "solution_markdown": "L'action positive attendue est \"respecter les regles de securite\", a mettre a l'imperatif malgre le sujet pluriel \"the workers\" (l'imperatif anglais n'a pas de marque de personne). La consequence \"they will get injured\" reste inchangee.\n\nOn obtient : **Respect the safety rules, otherwise you will get injured.**\n\n(Le pronom de la consequence passe naturellement a \"you\" puisque l'imperatif s'adresse directement aux destinataires de l'ordre.)"
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Reecris en commencant par un imperatif suivi de or, en gerant la double negation de la phrase d'origine : \"Unless you don't tell lies, people will not trust you.\"",
                    "solution_markdown": "Cette phrase de depart contient une construction fautive frequente chez les candidats : \"unless\" porte deja le sens de \"if...not\", donc ajouter \"don't\" a l'interieur cree une double negation qui inverse le sens attendu (\"unless you don't tell lies\" signifierait litteralement \"sauf si vous ne mentez pas\", c'est-a-dire \"si vous mentez\"). La phrase grammaticalement correcte pour exprimer l'idee visee (\"si tu ne dis pas la verite, on ne te fera pas confiance\") serait : \"Unless you tell the truth, people will not trust you.\"\n\nEn partant de cette version corrigee, l'action positive attendue est \"tell the truth\", a l'imperatif ; la consequence \"people will not trust you\" reste inchangee apres or.\n\nOn obtient : **Tell the truth or people will not trust you.**\n\nCet exercice montre qu'il faut toujours verifier le sens logique de la phrase de depart avant de la transformer : unless porte deja une negation, y ajouter don't/doesn't cree une double negation fautive qu'il faut corriger avant d'appliquer la regle de transformation."
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Unless equivaut a if...not : ne lui ajoute jamais de negation supplementaire (don't/doesn't), ce serait une double negation fautive.",
                "Pour transformer en imperatif, identifie l'action positive attendue (le contraire de la condition negative) et place-la en tete de phrase, sans sujet.",
                "La consequence apres or/otherwise reste toujours identique a celle de la phrase d'origine, sans changer sa polarite.",
                "Un imperatif anglais n'a jamais de sujet exprime devant le verbe : la base verbale seule suffit.",
                "Cette transformation est un grand classique du Bac : entraine-toi a la reconnaitre dans les deux sens, de unless vers l'imperatif et inversement."
            ]
        }
    ]
})

# ---------- 17. VERBES SUIVIS DU GERONDIF ----------
COURSES.append({
    "_slug": "verbes-suivis-gerondif",
    "cours_id": "cours-verbes-suivis-gerondif-bac-c-d-angl-2004",
    "meta": {
        "titre": "Reconnaitre les verbes suivis du gerondif (enjoy, avoid, finish, mind...)",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Grammaire - constructions verbales",
        "duree_estimee_min": 18,
        "tags": ["gerondif", "enjoy", "V-ing", "verbe + verbe"],
        "statut": "brouillon"
    },
    "source": base_source("1", "rdm-bac-c-d-anglais-2004-cameroun-ex1-qB.3-0"),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "\"I enjoy ... songs.\" Faut-il \"sing\", \"to sing\" ou \"singing\" ? Le francais \"j'aime chanter\" pousse naturellement vers l'infinitif par calque, mais l'anglais impose ici une forme differente. Une liste precise de verbes anglais se comporte ainsi : ils exigent systematiquement le gerondif quand ils sont suivis d'un autre verbe. Ce cours te donne cette liste et le reflexe pour ne plus te laisser piéger par la traduction."
        },
        {
            "type": "prerequis",
            "items": [
                "Savoir former le gerondif d'un verbe (verbe + -ing)",
                "Connaitre la difference entre gerondif et infinitif avec to"
            ]
        },
        {
            "type": "regle",
            "titre": "Une liste de verbes a memoriser, independamment de leur traduction francaise",
            "contenu_markdown": "Certains verbes anglais sont systematiquement suivis du gerondif (V-ing) lorsqu'ils sont suivis d'un autre verbe, et non de l'infinitif. Cette regle ne se devine pas a partir de la traduction francaise : elle s'apprend comme une liste fermee de verbes a memoriser en bloc. \"Enjoy\" fait partie de ce groupe, au meme titre que \"avoid\", \"finish\", \"suggest\", \"mind\", \"consider\", \"admit\", \"deny\", \"imagine\", \"practise\" et \"risk\".",
            "formule_principale": "enjoy / avoid / finish / suggest / mind / consider / admit / deny / imagine / practise / risk + V-ing",
            "variantes": [
                {
                    "nom": "Verbes a double construction (like, love, hate, start, begin, continue)",
                    "quand_utiliser": "Certains verbes proches par le sens (like, love, hate, prefer, start, begin, continue) acceptent a la fois le gerondif et l'infinitif avec to, sans grande difference de sens dans la plupart des contextes (\"I like swimming\" et \"I like to swim\" sont tous deux corrects).",
                    "contenu_markdown": "Ne confonds pas ces verbes a double construction avec le groupe strict (enjoy, avoid, finish...) qui n'accepte jamais l'infinitif dans ce sens : \"I enjoy to sing\" reste incorrect, meme si \"I like to sing\" est correct."
                }
            ]
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "Complete : \"I enjoy ... songs.\" (sing, to sing, singing)",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Identifier le verbe qui precede le blanc",
                    "justification": "C'est ce verbe qui determine la forme obligatoire du verbe suivant",
                    "resultat_markdown": "verbe = \"enjoy\""
                },
                {
                    "numero": 2,
                    "action": "Verifier si enjoy fait partie du groupe des verbes suivis du gerondif",
                    "justification": "\"Enjoy\" appartient a la liste fermee des verbes qui exigent systematiquement le gerondif, jamais l'infinitif, quand ils sont suivis d'un autre verbe",
                    "resultat_markdown": "enjoy + V-ing obligatoire"
                },
                {
                    "numero": 3,
                    "action": "Eliminer la base verbale nue et l'infinitif avec to",
                    "justification": "\"Sing\" (base nue, sans to) ne peut suivre enjoy dans aucun contexte standard, et \"to sing\" est exclu par la regle du gerondif obligatoire",
                    "resultat_markdown": "\"sing\" et \"to sing\" elimines"
                },
                {
                    "numero": 4,
                    "action": "Retenir le gerondif",
                    "justification": "\"Singing\" est la seule forme grammaticalement acceptable apres enjoy",
                    "resultat_markdown": "**I enjoy singing songs.**"
                }
            ],
            "conclusion_markdown": "Le choix ne depend pas de la traduction francaise (\"j'aime chanter\", qui suggererait un infinitif) mais uniquement de l'appartenance de \"enjoy\" a la liste fermee des verbes suivis du gerondif."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Traduire litteralement depuis le francais et choisir l'infinitif : \"I enjoy to sing songs.\"",
                    "pourquoi_faux": "Le francais \"j'aime chanter\" utilise un infinitif, ce qui pousse par reflexe a choisir \"to sing\" en anglais ; mais enjoy exige toujours le gerondif, quelle que soit la construction equivalente en francais.",
                    "correction_markdown": "Ne traduis jamais mot a mot la construction verbale : memorise la liste des verbes suivis du gerondif comme un bloc grammatical propre a l'anglais, independant du francais."
                },
                {
                    "erreur_markdown": "Utiliser la base verbale nue apres enjoy : \"I enjoy sing songs.\"",
                    "pourquoi_faux": "La base verbale nue (sans -ing ni to) ne s'utilise qu'apres des verbes de perception (see, hear...) ou des auxiliaires modaux, jamais apres enjoy.",
                    "correction_markdown": "Rappelle-toi qu'un verbe qui suit directement enjoy prend toujours la forme en -ing, sans exception."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Complete avec la forme correcte : \"She avoided ... (answer) the difficult question.\"",
                    "solution_markdown": "\"Avoid\" fait partie de la meme liste que \"enjoy\" : il exige systematiquement le gerondif. \"Answer\" devient \"answering\".\n\nOn obtient : **She avoided answering the difficult question.**"
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "Complete avec la forme correcte : \"Have you finished ... (write) your essay yet?\"",
                    "solution_markdown": "\"Finish\" appartient au meme groupe : il n'accepte jamais l'infinitif avec to dans ce sens, seulement le gerondif. \"Write\" devient \"writing\".\n\nOn obtient : **Have you finished writing your essay yet?**"
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Complete les deux blancs avec la forme correcte et explique la difference de construction : \"I don't mind ... (help) you, but I suggest ... (ask) the teacher first.\"",
                    "solution_markdown": "Cet exercice combine deux verbes du meme groupe (mind, suggest) dans une seule phrase, ce qui permet de verifier que la regle s'applique de facon identique quel que soit le verbe du groupe utilise.\n\n\"Mind\" (au sens de \"cela me derange de...\") exige le gerondif : \"help\" devient \"helping\". \"Suggest\" exige egalement le gerondif quand il est suivi directement d'un verbe (sans sujet propre exprime) : \"ask\" devient \"asking\".\n\nOn obtient : **I don't mind helping you, but I suggest asking the teacher first.**\n\nCet exercice confirme que la regle du gerondif obligatoire ne se limite pas a \"enjoy\" : elle s'applique de la meme facon a tous les verbes de la liste (avoid, finish, mind, suggest, consider, admit, deny, imagine, practise, risk), quel que soit le sens particulier de chacun."
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Enjoy, avoid, finish, suggest, mind, consider, admit, deny, imagine, practise et risk exigent toujours le gerondif quand ils sont suivis d'un autre verbe.",
                "Ne te fie jamais a la traduction francaise pour choisir entre gerondif et infinitif : cette regle est propre a la grammaire anglaise.",
                "Distingue ce groupe strict des verbes a double construction (like, love, hate, start, begin, continue), qui acceptent gerondif et infinitif indifferemment.",
                "Memorise cette liste comme un bloc grammatical a part entiere, au meme titre qu'un vocabulaire a apprendre par coeur.",
                "Ce point revient regulierement en QCM de grammaire au Bac, souvent avec enjoy, avoid ou finish comme verbe teste."
            ]
        }
    ]
})

# ---------- 9. LETTRE INFORMELLE RECIT PERSONNEL ----------
COURSES.append({
    "_slug": "lettre-informelle-recit-personnel",
    "cours_id": "cours-lettre-informelle-recit-personnel-bac-c-d-angl-2004",
    "meta": {
        "titre": "Rediger une lettre informelle racontant un evenement personnel",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Expression ecrite - lettre informelle",
        "duree_estimee_min": 28,
        "tags": ["informal letter", "personal narrative", "dear dad", "essay"],
        "statut": "brouillon"
    },
    "source": base_source("4", "rdm-bac-c-d-anglais-2004-cameroun-ex4-q2-0"),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "\"You got into trouble with a friend and the matter ended up with you going to the police. Tell your father what happened.\" Ce type de sujet demande a la fois de raconter des faits genants et de garder un ton naturel, comme si on parlait vraiment a son pere. Beaucoup de candidats basculent soit dans un recit trop sec, soit dans un registre trop formel qui sonne faux dans une lettre familiale. Ce cours te montre comment construire une lettre informelle credible, meme quand le sujet est delicat."
        },
        {
            "type": "prerequis",
            "items": [
                "Connaitre la structure de base d'une lettre (adresse, date, formule d'appel, corps, formule de cloture)",
                "Savoir raconter des evenements passes dans l'ordre chronologique",
                "Disposer d'un vocabulaire des emotions (frightened, ashamed, relieved, worried...)"
            ]
        },
        {
            "type": "regle",
            "titre": "Structure souple mais organisee, registre familial du debut a la fin",
            "contenu_markdown": "Une lettre informelle adressee a un membre de la famille suit une structure plus souple qu'une lettre formelle, mais reste organisee : adresse et date en haut (souvent reduites a l'essentiel), formule d'appel affectueuse (\"Dear Dad\", \"Dear Mum\"), recit chronologique clair des evenements, expression sincere des sentiments ressentis, et formule de cloture chaleureuse (\"Your loving son/daughter\", \"Love,\"). Le registre de langue reste simple et direct du debut a la fin de la lettre : aucune formule administrative ou soutenue ne doit s'y glisser, meme quand le sujet aborde un evenement grave.",
            "formule_principale": "Dear + [terme affectueux], + recit chronologique + expression des sentiments + formule de cloture chaleureuse",
            "variantes": []
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "You got into trouble with a friend and the matter ended up with you going to the police. Tell your father what happened.",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Annoncer d'emblee le sujet de la lettre sans faire durer le suspense",
                    "justification": "Dans une lettre a un parent, on annonce generalement directement qu'on a quelque chose d'important a dire, ce qui rassure aussi le destinataire sur le fait qu'on ne lui cache rien",
                    "resultat_markdown": "\"I am writing to tell you about something serious that happened to me last week, because I think you should know before you hear it from someone else.\""
                },
                {
                    "numero": 2,
                    "action": "Raconter les faits dans l'ordre chronologique, sans dramatiser ni minimiser",
                    "justification": "Le correcteur evalue la clarte du recit et la richesse du vocabulaire narratif, pas seulement la moralite de l'histoire racontee",
                    "resultat_markdown": "\"It all started when my friend and I had an argument about money he said I owed him. The disagreement got out of hand and we started shouting at each other in the street. A neighbour called the police, and we were both taken to the police station to explain what had happened.\""
                },
                {
                    "numero": 3,
                    "action": "Exprimer sincerement les sentiments ressentis pendant l'evenement",
                    "justification": "Une lettre a un parent proche laisse naturellement transparaitre les emotions vecues, ce qui donne de l'authenticite au recit",
                    "resultat_markdown": "\"I was very frightened, Dad, because I had never been to a police station before.\""
                },
                {
                    "numero": 4,
                    "action": "Conclure sur l'issue de l'evenement et une promesse ou reflexion personnelle",
                    "justification": "Terminer sur l'issue rassure le destinataire et montre une maturite face a l'incident, ce qui renforce la coherence de la lettre",
                    "resultat_markdown": "\"Fortunately, after we explained everything calmly, the police officer let us go with a warning, and my friend and I have since made up. I am telling you all this because I want to be honest with you, and I promise it will not happen again.\""
                }
            ],
            "conclusion_markdown": "La lettre complete, signee \"Your loving son,\", combine un recit chronologique clair, l'expression sincere des sentiments et une conclusion rassurante - exactement ce qu'attend le correcteur d'une lettre informelle bien construite sur un sujet delicat."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Basculer dans un registre trop soutenu : \"I hereby inform you that I was apprehended by the police authorities.\"",
                    "pourquoi_faux": "Ce registre administratif est totalement incoherent dans une lettre a son propre pere ; le jury attend un ton naturel et personnel, pas une formulation qui semble sortie d'un rapport officiel.",
                    "correction_markdown": "Relis ta lettre en te demandant si tu parlerais vraiment ainsi a ton pere a l'oral : si la formulation te semble trop rigide, simplifie-la."
                },
                {
                    "erreur_markdown": "Sauter directement aux consequences sans raconter comment la situation a degenere : \"I had trouble with my friend and went to the police.\"",
                    "pourquoi_faux": "Cette phrase resume l'histoire en une ligne sans aucun detail narratif, ce qui prive le correcteur de la matiere necessaire pour evaluer la richesse de langue et la maitrise du recit chronologique.",
                    "correction_markdown": "Developpe chaque etape de l'histoire (le debut du differend, son aggravation, l'intervention exterieure, la resolution) au lieu de la resumer en une seule phrase."
                },
                {
                    "erreur_markdown": "Oublier d'exprimer un sentiment personnel face a l'evenement raconte",
                    "pourquoi_faux": "Une lettre purement factuelle, sans aucune emotion exprimee, manque l'objectif d'une lettre informelle a un parent : elle doit aussi montrer comment on a vecu la situation, pas seulement ce qui s'est passe.",
                    "correction_markdown": "Ajoute toujours au moins une phrase qui exprime directement ce que tu as ressenti (peur, honte, soulagement) : c'est souvent ce qui distingue une bonne lettre informelle d'un simple compte-rendu."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Redige la formule d'ouverture et la premiere phrase d'une lettre informelle a ta mere, lui annonçant que tu as perdu ton telephone portable.",
                    "solution_markdown": "L'ouverture doit etre affectueuse et annoncer directement le sujet, sans formalisme excessif.\n\n\"Dear Mum,\n\nI am writing to tell you something that I know will make you a bit worried, but I promise everything is under control now: I lost my phone yesterday.\"\n\nCette ouverture respecte le registre familial (\"Dear Mum\") et annonce le sujet sans detour, tout en rassurant immediatement le destinataire, comme dans l'exemple de la lettre au pere."
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "Redige le paragraphe central (recit chronologique, 4 a 5 phrases) racontant comment tu as perdu ton telephone.",
                    "solution_markdown": "Le paragraphe central doit suivre l'ordre chronologique des evenements avec des connecteurs temporels, comme dans le recit de la dispute avec l'ami.\n\n\"I was coming back from school with some classmates when we stopped at a small shop to buy some snacks. I put my phone down on the counter while I was looking for my money, and I completely forgot to pick it up again. It was only when I got home, about twenty minutes later, that I realised it was missing. I rushed back to the shop, but by then someone else had already taken it.\"\n\nLe recit suit une progression claire (a l'ecole -> au magasin -> a la maison -> retour au magasin), exactement la structure chronologique attendue dans ce type de lettre."
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Redige la lettre complete (250 mots minimum) sur le sujet suivant : \"You were involved in a minor accident on your way to school and had to be taken to the hospital. Write to your elder sister, who lives abroad, telling her what happened.\" Integre annonce du sujet, recit chronologique, expression des sentiments, et une conclusion rassurante.",
                    "solution_markdown": "Cet exercice combine toutes les etapes du cours avec une contrainte supplementaire : le destinataire vit a l'etranger, ce qui justifie de donner plus de details qu'a un destinataire proche qui aurait deja entendu parler de l'evenement par d'autres sources.\n\n\"Dear Grace,\n\nI hope this letter finds you well in London. I am writing to tell you about something that happened to me last week, because I did not want you to worry if Mum mentioned it on the phone without giving you the full story.\n\nOn Tuesday morning, as I was cycling to school along the usual road, a motorbike came round the corner too fast and knocked me off my bicycle. I fell hard on my arm and could not get up immediately, so a passer-by called an ambulance, and I was taken to the district hospital for a check-up.\n\nI was really frightened at first, especially when the doctor said they needed to take an X-ray of my arm, but thankfully the results showed no broken bones, only a bad bruise. I had to stay at the hospital for a few hours while they cleaned my wounds and gave me some medication for the pain.\n\nMum and Dad came as soon as they heard the news, and having them by my side made me feel much calmer. I am back home now, resting for a few days before returning to school, and the doctor says I will be completely fine within two weeks.\n\nPlease do not worry too much, Grace. I am safe now, and this experience has just taught me to be more careful on the road. I miss you and hope to see you during your next visit.\n\nLove,\nYour sister\"\n\nLa lettre respecte l'ensemble de la structure enseignee (annonce directe, recit chronologique detaille, expression sincere des sentiments, conclusion rassurante) tout en adaptant le niveau de detail au fait que la destinataire, eloignee, n'a pas assiste aux evenements ni recu d'autres informations au prealable."
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Une lettre informelle a un parent garde un registre simple et direct du debut a la fin, meme sur un sujet grave.",
                "Annonce le sujet de ta lettre des les premieres phrases plutot que de faire durer le suspense.",
                "Raconte les faits dans l'ordre chronologique avec des connecteurs temporels, sans les resumer en une seule phrase.",
                "Exprime toujours au moins un sentiment personnel face a l'evenement : c'est ce qui distingue une lettre vivante d'un simple compte-rendu.",
                "Termine sur l'issue de la situation et une note rassurante ou une reflexion personnelle, jamais en suspens.",
                "Au Bac, ce type de sujet apparait dans la section Essay parmi les choix possibles : verifie toujours a qui tu ecris avant de fixer le registre de ta lettre."
            ]
        }
    ]
})

# ---------- 12. LETTRE FORMELLE DE DESACCORD ----------
COURSES.append({
    "_slug": "lettre-formelle-desaccord",
    "cours_id": "cours-lettre-formelle-desaccord-bac-c-d-angl-2004",
    "meta": {
        "titre": "Rediger une lettre formelle de desaccord (Letter to the Editor)",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Expression ecrite - lettre formelle",
        "duree_estimee_min": 30,
        "tags": ["formal letter", "letter to the editor", "disagreement", "essay"],
        "statut": "brouillon"
    },
    "source": base_source("4", "rdm-bac-c-d-anglais-2004-cameroun-ex4-q1-0"),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "\"You read an article you do not agree with. Write a letter to the Editor expressing your disagreement.\" Ce sujet classique du Bac demande d'exprimer un desaccord ferme tout en restant dans un registre courtois et structure - un exercice d'equilibre que beaucoup de candidats manquent, soit en restant trop vagues, soit en glissant vers un ton agressif incompatible avec une lettre formelle. Ce cours te donne la structure et les reflexes pour reussir cet exercice a coup sur."
        },
        {
            "type": "prerequis",
            "items": [
                "Connaitre la structure d'une lettre formelle (adresse, date, formule d'appel, corps, formule de politesse)",
                "Disposer de connecteurs logiques pour structurer une argumentation (first, second, finally, for these reasons...)",
                "Savoir formuler un desaccord sans agressivite (I disagree with, I do not share the view that, in my opinion...)"
            ]
        },
        {
            "type": "regle",
            "titre": "Structure imposee et registre courtois malgre le desaccord",
            "contenu_markdown": "La lettre formelle adressee a un redacteur en chef (\"Letter to the Editor\") suit une structure imposee : adresse de l'expediteur en haut, date, formule d'appel (\"Dear Editor\" ou \"Dear Sir/Madam\"), introduction qui situe precisement l'article conteste, developpement qui presente les arguments du desaccord de facon organisee, formule de politesse finale (\"Yours faithfully\") et signature. Le registre reste soutenu et courtois du debut a la fin, meme en cas de desaccord marque : la lettre argumente, elle ne s'emporte jamais.",
            "formule_principale": "Adresse + date / Dear Editor, / Introduction (article conteste) / Developpement (arguments organises) / Yours faithfully, / Signature",
            "variantes": []
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "You read an article \"The need to legalize abortion\" in \"The Scientist\" newspaper. You do not share the opinion of the writer. Write a letter to the Editor expressing your disagreement. Your name is Ayuck Victor and your address is Lycee de Mamfe, P.O Box 132 Mamfe.",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Placer l'adresse de l'expediteur et la date en haut de la lettre",
                    "justification": "Une lettre formelle commence toujours par l'adresse de celui qui ecrit, meme quand cette adresse est deja fournie par l'enonce",
                    "resultat_markdown": "\"Lycee de Mamfe\\nP.O Box 132 Mamfe\\n[date]\""
                },
                {
                    "numero": 2,
                    "action": "Ouvrir avec la formule d'appel appropriee",
                    "justification": "\"Dear Editor\" est la formule d'appel standard pour ce type de lettre, ni trop familiere ni excessivement administrative",
                    "resultat_markdown": "\"Dear Editor,\""
                },
                {
                    "numero": 3,
                    "action": "Situer precisement l'article conteste des l'introduction",
                    "justification": "Le redacteur doit immediatement comprendre a quel article la lettre repond, sinon la lettre perd toute credibilite",
                    "resultat_markdown": "\"I am writing in response to the article 'The need to legalize abortion' published in your newspaper, 'The Scientist'. While I understand the writer's concern for women's rights, I strongly disagree with the position defended in the article.\""
                },
                {
                    "numero": 4,
                    "action": "Developper les arguments du desaccord de facon organisee, puis conclure par la formule de politesse",
                    "justification": "Une argumentation structuree (First... Second... Finally...) est plus convaincante et plus facile a suivre pour le lecteur qu'une accumulation d'idees non hierarchisees ; la formule finale ferme formellement la lettre",
                    "resultat_markdown": "\"First, legalizing abortion would [...] encourage irresponsible behaviour [...]. Second, abortion raises a serious ethical question [...]. Finally, [...] our society should invest in sex education [...]\\n\\nFor these reasons, I believe the legalization of abortion would do more harm than good to our society.\\n\\nYours faithfully,\\nAyuck Victor\""
                }
            ],
            "conclusion_markdown": "La lettre complete respecte les six elements imposes (adresse, date, appel, introduction situant l'article, developpement argumente en trois points, formule de politesse) tout en gardant un registre courtois malgre un desaccord ferme - c'est cet equilibre qui distingue une bonne Letter to the Editor."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Ouvrir la lettre avec \"Hi\" ou \"Hello\" au lieu d'une formule formelle",
                    "pourquoi_faux": "Ce registre familier est incompatible avec une lettre adressee a un redacteur en chef inconnu du candidat ; le correcteur penalise systematiquement ce type de confusion de registre au Bac.",
                    "correction_markdown": "N'utilise que \"Dear Editor\" ou \"Dear Sir/Madam\" pour ouvrir une lettre formelle, jamais une salutation familiere."
                },
                {
                    "erreur_markdown": "Exprimer le desaccord de facon agressive ou insultante envers l'auteur de l'article",
                    "pourquoi_faux": "Une lettre formelle argumente, elle ne cherche pas a humilier l'auteur oppose ; un ton agressif nuit a la credibilite des arguments et penalise la note de registre.",
                    "correction_markdown": "Formule ton desaccord avec des expressions mesurees (\"I strongly disagree with...\", \"I cannot share this view because...\") plutot que par des attaques personnelles."
                },
                {
                    "erreur_markdown": "Oublier l'adresse de l'expediteur ou la formule de politesse finale",
                    "pourquoi_faux": "Ces elements font partie de la structure imposee d'une lettre formelle ; leur absence fait perdre des points au bareme, meme quand le contenu argumentatif est solide.",
                    "correction_markdown": "Verifie systematiquement, avant de rendre ta copie, que ta lettre contient bien les six elements de la structure : adresse, date, appel, introduction, developpement, formule de cloture."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Redige uniquement l'introduction (2 a 3 phrases) d'une lettre a l'editeur exprimant ton desaccord avec un article intitule \"School uniforms should be abolished\", publie dans \"The Daily Voice\".",
                    "solution_markdown": "L'introduction doit situer precisement l'article conteste et annoncer clairement le desaccord, comme dans l'exemple sur l'avortement.\n\n\"I am writing in response to the article 'School uniforms should be abolished', published in your newspaper, 'The Daily Voice'. Although I understand the writer's wish for more freedom for students, I do not share this opinion at all.\"\n\nCette introduction respecte la structure attendue : identification precise de l'article et du journal, suivie d'une annonce claire du desaccord."
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "Redige deux arguments structures (\"First,... Second,...\") pour la meme lettre, defendant le maintien de l'uniforme scolaire.",
                    "solution_markdown": "Chaque argument doit etre introduit par un connecteur clair et developpe avec une justification, pas seulement affirme.\n\n\"First, school uniforms reduce inequality among students, since they prevent visible differences in family income from becoming a source of comparison or mockery in the classroom. Second, wearing a uniform helps students develop a sense of discipline and belonging to their school, which contributes to a more serious learning environment.\"\n\nLes deux arguments sont distincts, clairement introduits, et chacun est justifie par une consequence concrete, exactement le niveau d'argumentation attendu dans le developpement d'une lettre formelle."
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Redige la lettre complete (250 mots minimum) sur le sujet suivant : \"You read an article claiming that social media does more good than harm to teenagers. You disagree. Write a letter to the Editor of 'The National Voice' expressing your disagreement. Your name is Mbah Grace and your address is Government Bilingual High School, P.O Box 45, Bamenda.\"",
                    "solution_markdown": "Cet exercice demande d'appliquer la structure complete a un nouveau sujet, avec trois arguments distincts bien organises, comme dans l'exemple resolu sur l'avortement.\n\n\"Government Bilingual High School\\nP.O Box 45, Bamenda\\n[date]\\n\\nDear Editor,\\n\\nI am writing in response to the article claiming that social media does more good than harm to teenagers, published recently in your newspaper, 'The National Voice'. While I agree that social media has some benefits, I strongly disagree with the overall claim defended in the article.\\n\\nFirst, excessive use of social media has been shown to affect the mental health of many teenagers, who often compare their lives to the curated, unrealistic images shared online, leading to anxiety and low self-esteem. Second, social media takes up a considerable amount of time that could otherwise be spent studying or engaging in physical activities, which explains the declining academic performance observed among some heavy users. Finally, teenagers are particularly vulnerable to misinformation and harmful content circulating on these platforms, since they often lack the critical judgment to distinguish reliable sources from false ones.\\n\\nFor these reasons, I believe that, without proper guidance and limits, social media does more harm than good to young people.\\n\\nYours faithfully,\\nMbah Grace\"\n\nCette lettre respecte integralement la structure enseignee (adresse, date, appel, introduction situant l'article, trois arguments distincts et justifies, formule de politesse) tout en s'adaptant a un theme different de l'exemple resolu, ce qui montre que la methode se transfere a n'importe quel sujet de desaccord impose au Bac."
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Une Letter to the Editor suit toujours la meme structure : adresse, date, Dear Editor, introduction situant l'article, developpement argumente, Yours faithfully, signature.",
                "Situe precisement l'article conteste (titre et journal) des l'introduction, sinon ta lettre perd toute credibilite.",
                "Organise toujours au moins deux ou trois arguments distincts avec des connecteurs clairs (First, Second, Finally), plutot qu'une seule idee developpee en boucle.",
                "Garde un registre courtois du debut a la fin, meme quand le desaccord est ferme : une lettre formelle argumente, elle ne s'emporte jamais.",
                "Verifie systematiquement la presence des six elements structurels avant de rendre ta copie.",
                "Au Bac, ce type de sujet fait partie des choix classiques de la section Essay : la maitrise de cette structure fixe est ce qui rapporte le plus de points, independamment du sujet precis propose."
            ]
        }
    ]
})

# ---------- 4. VOCABULAIRE EN CONTEXTE ----------
COURSES.append({
    "_slug": "vocabulaire-contexte",
    "cours_id": "cours-vocabulaire-contexte-bac-c-d-angl-2004",
    "meta": {
        "titre": "Le vocabulaire en contexte : deduire un mot manquant a partir des indices de la phrase",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Vocabulaire - comprehension lexicale",
        "duree_estimee_min": 25,
        "tags": ["vocabulaire en contexte", "collocations", "definition", "inference lexicale"],
        "statut": "brouillon"
    },
    "source": base_source(
        "2", "rdm-bac-c-d-anglais-2004-cameroun-ex2-qA.1-0",
        rappels_lies=[
            "rdm-bac-c-d-anglais-2004-cameroun-ex2-qA.2-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex2-qA.3-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex2-qA.4-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex2-qA.5-0"
        ]
    ),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "\"Scientists sometimes conduct ... in laboratories to test theories.\" Aucune liste de choix n'est fournie : il faut trouver le mot exact, seul, a partir des indices donnes par la phrase. Cet exercice de vocabulaire en contexte teste une competence precise, differente du simple par-coeur : la capacite a lire une phrase comme une enigme dont chaque mot est un indice. Ce cours te donne la methode pour reperer ces indices systematiquement."
        },
        {
            "type": "prerequis",
            "items": [
                "Disposer d'un vocabulaire general suffisant sur des themes courants (sciences, societe, vie quotidienne)",
                "Savoir identifier la fonction grammaticale attendue a l'endroit du blanc (nom, verbe, adjectif...)"
            ]
        },
        {
            "type": "regle",
            "titre": "Trois types d'indices a chercher systematiquement dans la phrase",
            "contenu_markdown": "Pour completer une phrase avec un mot manquant sans liste de choix, il faut s'appuyer sur les indices de sens presents dans le reste de la phrase afin de proposer le mot dont le sens et la construction grammaticale conviennent. Trois types d'indices reviennent le plus souvent :\n\n1. **La collocation** : certains mots s'associent naturellement a d'autres (\"conduct experiments\", \"draw a balance sheet\") ; reconnaitre ces associations frequentes oriente directement vers le mot attendu.\n2. **La definition explicite** : la phrase decrit litteralement ce que le mot signifie (\"an official head count of the number of people\" definit \"census\").\n3. **La reformulation ou justification** : une proposition qui suit (souvent apres un point-virgule ou \"because\") reformule ou justifie le mot recherche (\"they can neither read nor write\" justifie \"illiterate\").\n\nDans les trois cas, la methode est la meme : lire la phrase entiere avant de chercher le mot, reperer quel type d'indice elle contient, puis proposer le mot dont le sens colle exactement a cet indice.",
            "formule_principale": "Lire la phrase entiere -> identifier le type d'indice (collocation / definition / reformulation) -> proposer le mot dont le sens et la grammaire conviennent exactement",
            "variantes": []
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "Complete avec un mot approprie : \"A ... is an official head count of the number of people in a country at a particular time.\"",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Lire la phrase entiere avant de chercher le mot",
                    "justification": "Le mot manquant est ici le sujet de la phrase, defini par tout ce qui suit le verbe \"is\" : il faut donc lire la definition avant de proposer une reponse",
                    "resultat_markdown": "la phrase est une definition complete introduite par \"is\""
                },
                {
                    "numero": 2,
                    "action": "Identifier le type d'indice : une definition explicite",
                    "justification": "\"An official head count of the number of people in a country at a particular time\" ne laisse place a aucune ambiguite : c'est la definition precise d'un terme du vocabulaire socio-economique",
                    "resultat_markdown": "indice = definition litterale, pas collocation ni reformulation implicite"
                },
                {
                    "numero": 3,
                    "action": "Chercher le terme exact correspondant a cette definition",
                    "justification": "Un decompte officiel du nombre d'habitants d'un pays a un moment donne correspond exactement au vocabulaire du recensement de population",
                    "resultat_markdown": "\"census\" = decompte officiel et exhaustif de la population"
                },
                {
                    "numero": 4,
                    "action": "Verifier que le mot convient grammaticalement (article \"a\" devant un nom singulier)",
                    "justification": "L'article indefini \"a\" impose un nom singulier commencant par un son consonantique, ce que \"census\" respecte",
                    "resultat_markdown": "**A census is an official head count of the number of people in a country at a particular time.**"
                }
            ],
            "conclusion_markdown": "Reperer d'abord le type d'indice (ici une definition explicite) permet de restreindre immediatement la recherche a un champ lexical precis, au lieu de chercher au hasard parmi tout le vocabulaire connu."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Proposer un mot proche par la forme mais different par le sens, par confusion entre deux mots qui se ressemblent (ex. \"experience\" au lieu de \"experiments\")",
                    "pourquoi_faux": "\"Experiment\" (une experience scientifique) et \"experience\" (une experience vecue) se ressemblent enormement en anglais mais n'ont pas le meme sens ; seul le premier convient dans un contexte de laboratoire et de test de theories.",
                    "correction_markdown": "Verifie toujours le sens precis du mot que tu proposes, pas seulement sa ressemblance sonore ou orthographique avec le mot attendu : deux mots proches par la forme peuvent avoir des sens totalement differents."
                },
                {
                    "erreur_markdown": "Choisir un mot trop general qui ne colle qu'approximativement a l'indice, sans verifier qu'il correspond exactement (ex. \"workers\" au lieu de \"accountants\" pour une definition tres precise)",
                    "pourquoi_faux": "Quand l'indice est tres specifique (\"supply information, calculate and draw a balance sheet\"), un mot trop general perd la precision recherchee par l'exercice et peut ne pas etre accepte au bareme.",
                    "correction_markdown": "Quand l'indice contient des details tres precis, cherche le mot le plus specifique possible qui les couvre tous, pas une categorie generale qui les engloberait vaguement."
                },
                {
                    "erreur_markdown": "Ignorer l'indice grammatical donne par le contexte (article, preposition, accord) et proposer un mot de la mauvaise categorie grammaticale",
                    "pourquoi_faux": "Meme un mot au sens correct peut etre refuse s'il ne respecte pas la fonction grammaticale attendue a cet endroit de la phrase (nom, adjectif, verbe...).",
                    "correction_markdown": "Verifie toujours, apres avoir trouve un mot dont le sens convient, qu'il s'accorde grammaticalement avec le reste de la phrase (article, temps verbal, accord)."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Complete avec un mot approprie : \"After the long hike, the students were extremely ... and asked for water.\"",
                    "solution_markdown": "L'indice est une reformulation implicite : demander de l'eau apres une longue randonnee est le comportement typique d'une personne qui a tres soif.\n\nOn obtient : **After the long hike, the students were extremely thirsty and asked for water.**"
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "Complete avec un mot approprie : \"A ... is a person who studies the stars, planets and other objects in space.\"",
                    "solution_markdown": "L'indice est une definition explicite, sur le meme modele que \"census\" dans l'exemple resolu : il faut trouver le nom de metier qui correspond exactement a cette description.\n\nOn obtient : **An astronomer is a person who studies the stars, planets and other objects in space.**\n\n(L'article change de \"a\" a \"an\" parce que \"astronomer\" commence par une voyelle - un rappel que la verification grammaticale finale reste indispensable, meme quand le sens est trouve.)"
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Complete avec un mot approprie et identifie le type d'indice mobilise : \"The company's profits fell so sharply last year that many workers had to be ..., which caused a wave of protests in the city.\"",
                    "solution_markdown": "Cet exercice combine deux indices differents dans la meme phrase : une relation de cause a effet (\"profits fell so sharply\" -> consequence sur les travailleurs) et une reformulation implicite (\"caused a wave of protests\" suggere une mesure impopulaire et brutale).\n\nLa chute des profits d'une entreprise entraine generalement des suppressions d'emplois, ce qui provoque logiquement des protestations parmi les travailleurs concernes. Le mot recherche doit donc exprimer un licenciement.\n\nOn obtient : **The company's profits fell so sharply last year that many workers had to be dismissed (ou : made redundant / laid off), which caused a wave of protests in the city.**\n\nCet exercice montre qu'une phrase peut combiner plusieurs indices simultanement (cause-consequence economique et reformulation sociale) : il faut alors les croiser pour restreindre le champ lexical possible avant de choisir le mot final."
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Lis toujours la phrase entiere avant de chercher le mot manquant : la reponse depend du contexte global, pas d'un seul mot isole.",
                "Identifie le type d'indice mobilise : collocation frequente, definition explicite, ou reformulation/justification dans une autre partie de la phrase.",
                "Ne confonds jamais deux mots proches par la forme mais differents par le sens (experiment/experience, census/survey...).",
                "Verifie toujours la coherence grammaticale de ta reponse (article, accord, categorie grammaticale) apres avoir trouve le bon sens.",
                "Cet exercice sans liste de choix teste une lecture active du texte, pas seulement un vocabulaire memorise isolement : entraine-toi a reperer les indices avant de chercher le mot."
            ]
        }
    ]
})

# ---------- 10. NUANCES DE VOCABULAIRE ----------
COURSES.append({
    "_slug": "nuances-vocabulaire",
    "cours_id": "cours-nuances-vocabulaire-bac-c-d-angl-2004",
    "meta": {
        "titre": "Choisir le mot juste parmi plusieurs synonymes proches (nuances de vocabulaire)",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Vocabulaire - nuances lexicales",
        "duree_estimee_min": 25,
        "tags": ["nuances de vocabulaire", "synonymes", "collocations", "faux amis"],
        "statut": "brouillon"
    },
    "source": base_source(
        "2", "rdm-bac-c-d-anglais-2004-cameroun-ex2-qB.1-0",
        rappels_lies=[
            "rdm-bac-c-d-anglais-2004-cameroun-ex2-qB.2-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex2-qB.3-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex2-qB.4-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex2-qB.5-0"
        ]
    ),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "\"You can't tell what someone is like just from their ... (character, appearance, personality, looking).\" Les quatre options se traduisent presque toutes par des mots proches en francais, et pourtant une seule est correcte ici. Ce type d'exercice ne teste pas ta connaissance du vocabulaire de base, mais ta capacite a sentir la nuance exacte entre des mots que le francais confond parfois sous une seule traduction. Ce cours te donne la methode pour ne plus te laisser piéger par cette proximite trompeuse."
        },
        {
            "type": "prerequis",
            "items": [
                "Disposer d'un vocabulaire de base suffisant pour comprendre le sens general de chaque option proposee",
                "Savoir identifier la fonction grammaticale attendue a l'endroit du blanc (nom, verbe...)"
            ]
        },
        {
            "type": "regle",
            "titre": "Analyser precisement ce que chaque mot designe, pas seulement sa traduction approximative",
            "contenu_markdown": "Ce type d'exercice propose plusieurs mots proches par le sens mais pas interchangeables. Il faut analyser precisement ce que chaque mot designe pour choisir celui qui correspond exactement au sens de la phrase, plutot que de se fier a une traduction francaise unique qui gommerait la distinction. Trois sources de nuance reviennent frequemment :\n\n1. **La categorie grammaticale** : un mot peut etre exclu simplement parce que ce n'est pas la bonne nature (un verbe la ou il faut un nom, par exemple).\n2. **La collocation figee** : certains mots s'associent obligatoirement a d'autres (\"heavy rain\", jamais \"great rain\"), independamment de leur sens general.\n3. **Le champ semantique precis** : deux mots peuvent partager un sens general (\"gagner\") mais s'appliquer a des contextes differents (earn = un salaire merite, win = une victoire, gain = un avantage progressif).",
            "formule_principale": "Identifier ce qui distingue precisement chaque option (categorie grammaticale, collocation figee, champ semantique) avant de choisir",
            "variantes": []
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "Choisis le mot le plus approprie : \"You can't tell what someone is like just from their ... .\" (character, appearance, personality, looking)",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Eliminer d'abord l'option incorrecte grammaticalement",
                    "justification": "Apres le determinant possessif \"their\", la phrase attend un nom ; \"looking\" est un participe present, pas un nom autonome dans ce contexte",
                    "resultat_markdown": "\"looking\" elimine pour raison grammaticale"
                },
                {
                    "numero": 2,
                    "action": "Analyser le contraste logique construit par la phrase",
                    "justification": "\"You can't tell what someone is like just from...\" oppose ce qu'on peut observer de l'exterieur a ce qu'une personne est vraiment ; il faut identifier lequel des trois noms restants designe l'exterieur visible",
                    "resultat_markdown": "contraste : visible de l'exterieur (\"just from\") vs. ce que la personne est reellement (\"what someone is like\")"
                },
                {
                    "numero": 3,
                    "action": "Distinguer les champs semantiques de character, personality et appearance",
                    "justification": "\"Character\" et \"personality\" designent tous deux l'interieur d'une personne (ses traits moraux, son temperament), tandis que \"appearance\" designe specifiquement ce qui se voit de l'exterieur",
                    "resultat_markdown": "character/personality = interieur ; appearance = exterieur visible"
                },
                {
                    "numero": 4,
                    "action": "Retenir le mot qui correspond exactement au contraste construit par la phrase",
                    "justification": "La phrase affirme qu'on ne peut pas deviner l'interieur d'une personne seulement a partir de l'exterieur : c'est donc \"appearance\" qui doit completer la phrase",
                    "resultat_markdown": "**You can't tell what someone is like just from their appearance.**"
                }
            ],
            "conclusion_markdown": "\"Character\" et \"personality\" sont justement ce que la phrase affirme qu'on ne peut pas deviner a partir de l'apparence : les choisir inverserait completement la logique de la phrase, meme si leur traduction francaise semble proche de celle des autres options."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Choisir un mot uniquement parce que sa traduction francaise semble correspondre au sens general de la phrase, sans verifier la nuance precise",
                    "pourquoi_faux": "Le francais utilise parfois un seul mot (\"gagner\") la ou l'anglais en distingue plusieurs selon le contexte (earn/win/gain) ; se fier uniquement a la traduction fait perdre la nuance testee par l'exercice.",
                    "correction_markdown": "Demande-toi toujours dans quel contexte precis chaque mot s'utilise en anglais, pas seulement quelle est sa traduction francaise approximative."
                },
                {
                    "erreur_markdown": "Ignorer les collocations figees et choisir un mot dont le sens general semble correct mais qui ne s'associe jamais au nom de la phrase (ex. \"great rain\" au lieu de \"heavy rain\")",
                    "pourquoi_faux": "Certains couples adjectif-nom sont figes par l'usage, independamment de leur logique semantique apparente : \"great\" est un intensificateur parfaitement correct avec beaucoup de noms, mais pas avec \"rain\".",
                    "correction_markdown": "Memorise les collocations frequentes comme des blocs figes (heavy rain, heavy traffic, heavy smoker), plutot que de recomposer l'association a partir du sens general de chaque mot."
                },
                {
                    "erreur_markdown": "Confondre un mot qui designe un processus avec le mot qui designe son resultat (ex. \"research\" au lieu de \"findings\")",
                    "pourquoi_faux": "\"Research\" est un processus en cours ou une activite generale, tandis que \"findings\" designe le produit final, les conclusions d'une enquete deja terminee : les deux ne sont pas interchangeables des que la phrase implique un resultat acheve.",
                    "correction_markdown": "Verifie si la phrase parle d'un processus en cours ou d'un resultat deja obtenu : ce distinguo revient souvent dans les nuances de vocabulaire testees au Bac."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Choisis le mot le plus approprie : \"The doctor gave her some ... about how to take the medicine.\" (advice, advise, suggestion)",
                    "solution_markdown": "\"Advise\" est un verbe, exclu apres \"some\" qui attend un nom. Entre \"advice\" (conseil general, non comptable) et \"suggestion\" (une proposition ponctuelle, comptable), le contexte medical (\"how to take the medicine\") correspond precisement au sens de recommandation pratique donnee par un professionnel, ce qui est le sens propre d'\"advice\".\n\nOn obtient : **The doctor gave her some advice about how to take the medicine.**"
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "Choisis le mot le plus approprie : \"The two countries finally reached an ... after months of difficult negotiations.\" (agreement, argument, arrangement)",
                    "solution_markdown": "\"Argument\" designe une dispute ou un desaccord, ce qui contredit l'idee de negociations aboutissant a un resultat positif. Entre \"agreement\" (accord formel, souvent apres une negociation officielle) et \"arrangement\" (dispositif plus pratique et informel), le contexte de \"negociations\" entre deux pays pointe vers un accord diplomatique formel.\n\nOn obtient : **The two countries finally reached an agreement after months of difficult negotiations.**"
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Choisis le mot le plus approprie et justifie ton elimination des autres options : \"The government has promised to ... unemployment among young people within the next five years.\" (raise, rise, reduce, decrease)",
                    "solution_markdown": "Cet exercice combine deux distinctions differentes dans une seule liste d'options : \"raise\" (transitif, augmenter quelque chose) et \"rise\" (intransitif, augmenter soi-meme, sans complement d'objet direct) forment une premiere paire a distinguer par leur construction grammaticale, tandis que \"reduce\" et \"decrease\" forment une seconde paire proche par le sens mais differente par la construction.\n\n\"Rise\" est exclu d'emblee : c'est un verbe intransitif, il ne peut pas avoir de complement d'objet direct comme \"unemployment\" juste apres lui (\"rise unemployment\" est agrammatical). \"Raise\" irait grammaticalement (verbe transitif) mais contredit le sens de la promesse gouvernementale, qui vise a diminuer le chomage, pas a l'augmenter. Entre \"reduce\" et \"decrease\", les deux sont transitifs et proches par le sens, mais \"decrease\" s'emploie generalement de facon intransitive dans l'usage courant (\"unemployment decreased\") ou comme verbe transitif plus formel/statistique, tandis que \"reduce\" est le verbe transitif standard pour exprimer une action volontaire visant a diminuer quelque chose, ce qui correspond exactement a une promesse politique active.\n\nOn obtient : **The government has promised to reduce unemployment among young people within the next five years.**\n\nCet exercice montre que la nuance testee peut porter a la fois sur la construction grammaticale (transitif/intransitif) et sur le sens precis (action volontaire vs. simple constat statistique), deux criteres a verifier systematiquement l'un apres l'autre."
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Ne te fie jamais uniquement a la traduction francaise d'un mot : plusieurs mots anglais peuvent partager une meme traduction tout en ayant des usages differents.",
                "Elimine d'abord les options dont la categorie grammaticale ne convient pas (verbe la ou il faut un nom, par exemple).",
                "Repere le contraste logique construit par la phrase (interieur/exterieur, processus/resultat, action volontaire/simple constat) pour orienter ton choix.",
                "Memorise les collocations figees comme des blocs (heavy rain, conduct experiments, draw a balance sheet) plutot que de les recomposer a partir du sens general.",
                "Cet exercice teste la precision du vocabulaire, pas sa quantite : mieux vaut connaitre finement la difference entre earn/win/gain que memoriser cent mots vagues.",
                "Au Bac, ce type de QCM revient systematiquement dans la section Vocabulary : entraine-toi a analyser chaque option separement avant de choisir, plutot que de te fier a une premiere impression."
            ]
        }
    ]
})

# ---------- 6. COMPREHENSION ECRITE : CITATION + REFORMULATION ----------
COURSES.append({
    "_slug": "comprehension-ecrite-citation-reformulation",
    "cours_id": "cours-comprehension-ecrite-citation-reformulation-bac-c-d-angl-2004",
    "meta": {
        "titre": "Repondre a une question de comprehension de texte : citation et reformulation",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Comprehension ecrite",
        "duree_estimee_min": 28,
        "tags": ["reading comprehension", "own words", "justification textuelle", "inference"],
        "statut": "brouillon"
    },
    "source": base_source(
        "3", "rdm-bac-c-d-anglais-2004-cameroun-ex3-q1-0",
        rappels_lies=[
            "rdm-bac-c-d-anglais-2004-cameroun-ex3-q2-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex3-q3-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex3-q4-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex3-q5-0"
        ]
    ),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "\"Use your own words as far as possible.\" Cette consigne, presente dans presque toutes les sections de comprehension du Bac, deroute de nombreux candidats : faut-il recopier le texte, ou tout reformuler au risque de perdre l'information exacte ? La reponse tient en une methode simple, la meme pour les cinq types de questions les plus frequents (why, how much/how old, give reasons, why do you think, did... justify). Ce cours te donne cette methode, point par point."
        },
        {
            "type": "prerequis",
            "items": [
                "Savoir lire un texte en anglais de niveau Bac et en degager les idees principales",
                "Reperer les mots interrogatifs (why, how, did, what) et ce qu'ils attendent comme type de reponse",
                "Rediger des phrases completes en anglais, sans se limiter a des mots isoles"
            ]
        },
        {
            "type": "regle",
            "titre": "Citer le texte pour prouver, reformuler pour repondre",
            "contenu_markdown": "Une reponse de comprehension ecrite bien notee repose toujours sur deux mouvements combines : reperer dans le texte l'information exacte qui repond a la question (la citation, ou au moins l'idee precise), puis la reformuler en une phrase complete et personnelle qui repond directement a la question posee (la reformulation). La consigne \"use your own words as far as possible\" interdit de recopier le texte mot pour mot comme unique reponse, mais elle n'interdit pas de s'appuyer sur les elements du texte : elle demande de prouver sa comprehension en reformulant, pas d'inventer une reponse detachee du passage.\n\nLa methode varie legerement selon le type de question :\n- **Why...?** -> expliquer une cause complete, en reliant plusieurs indices du texte si necessaire.\n- **How old/How much/How many...?** (donnee factuelle explicite) -> relever la donnee precise et la reformuler en phrase complete, sans reformulation excessive puisqu'il s'agit d'un fait, pas d'une idee.\n- **Give [n] reasons...** -> fournir exactement le nombre de raisons demande, chacune justifiee par un element distinct du texte.\n- **Why do you think...?** -> une interpretation personnelle, mais ancree dans les indices du texte, jamais une pure speculation.\n- **Did...? Justify.** -> une reponse tranchee (oui/non) suivie obligatoirement d'une justification textuelle : la reponse seule, sans justification, ne rapporte pas tous les points.",
            "formule_principale": "Reperer l'information exacte dans le texte -> reformuler en phrase complete qui repond directement a la question -> (si demande) justifier explicitement par un element du texte",
            "variantes": []
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "\"Why did Charles Taylor attach a lot of importance to his marriage?\" (question posee a propos d'un texte relatant le mariage mediatise de Charles Taylor, candidat a l'election liberienne)",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Identifier le type de question et ce qu'elle attend",
                    "justification": "\"Why\" attend une explication causale complete, pas une simple citation ni une reponse en un mot",
                    "resultat_markdown": "type de question : explication causale (Why)"
                },
                {
                    "numero": 2,
                    "action": "Reperer dans le texte les elements qui repondent a cette cause",
                    "justification": "Le texte precise deux informations complementaires necessaires pour comprendre la cause complete : le caractere mediatique du personnage et le contexte electoral",
                    "resultat_markdown": "\"the ever media-conscious and publicity hungry Charles Taylor\" ; \"succeeded in making a political occasion out of his recent wedding day\" ; \"plans to stand in the Liberian election scheduled for May 30th\""
                },
                {
                    "numero": 3,
                    "action": "Relier ces indices en une explication causale coherente",
                    "justification": "Une reponse bien notee relie toujours la citation a son interpretation : il ne suffit pas de recopier les mots-cles, il faut expliquer le lien logique entre eux",
                    "resultat_markdown": "Taylor cherche a soigner son image publique parce qu'une election approche et qu'il compte s'y presenter ; le mariage devient donc un outil de communication politique"
                },
                {
                    "numero": 4,
                    "action": "Rediger la reponse en une phrase complete, avec ses propres mots",
                    "justification": "La consigne \"use your own words\" impose de reformuler plutot que de recopier telle quelle la phrase du texte",
                    "resultat_markdown": "**Charles Taylor attached a lot of importance to his marriage because he was about to stand in the presidential election and wanted to use the wedding as an opportunity to gain publicity and improve his popular image before the vote.**"
                }
            ],
            "conclusion_markdown": "La reponse combine deux informations du texte (le trait de caractere mediatique de Taylor et l'election a venir) reformulees en une explication causale unique, plutot que de simplement juxtaposer des citations sans les relier."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Recopier une citation du texte sans l'expliquer, en pensant que la citation seule suffit comme reponse",
                    "pourquoi_faux": "Recopier \"media-conscious and publicity hungry\" sans preciser ce que cela signifie dans le contexte electoral ne montre pas que le candidat a compris le lien de cause a effet ; une reponse bien notee relie toujours la citation a son interpretation.",
                    "correction_markdown": "Ne t'arrete jamais a la citation : ajoute toujours une phrase qui explique en quoi cet element du texte repond precisement a la question posee."
                },
                {
                    "erreur_markdown": "Repondre a une question fermee (\"Did...? Justify.\") par un simple \"Yes\" ou \"No\" sans justification",
                    "pourquoi_faux": "La consigne \"Justify\" fait explicitement partie du bareme : une reponse tranchee sans justification ne rapporte qu'une fraction des points attribues a la question, meme si la reponse elle-meme est correcte.",
                    "correction_markdown": "Traite toujours \"Justify\" comme une partie obligatoire de la question, jamais comme une option facultative : appuie systematiquement ta reponse oui/non sur un element precis du texte."
                },
                {
                    "erreur_markdown": "Fournir une seule raison developpee quand la question en demande explicitement deux (\"give any two reasons\")",
                    "pourquoi_faux": "Meme une seule raison tres bien argumentee ne peut rapporter que la moitie des points quand la consigne en exige deux distinctes : le bareme recompense le nombre d'idees demandees, pas seulement leur qualite individuelle.",
                    "correction_markdown": "Compte toujours le nombre exact d'elements demandes dans la question (two reasons, two examples...) et assure-toi de fournir ce nombre precis, sous forme de points clairement separes."
                },
                {
                    "erreur_markdown": "Repondre a une question \"Why do you think...?\" par une pure speculation detachee du texte, sans ancrer l'interpretation dans un indice reel",
                    "pourquoi_faux": "\"Why do you think\" invite a une interpretation personnelle, mais celle-ci doit rester justifiee par des elements du texte ; une reponse totalement inventee, meme plausible en general, n'est pas ancree dans le passage etudie et perd des points.",
                    "correction_markdown": "Meme pour une question d'interpretation, appuie toujours ta reponse sur au moins un indice explicite du texte, jamais sur des connaissances generales completement deconnectees du passage."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Dans un texte qui precise : \"The school was founded in 1975 and now has over 2,000 students,\" reponds a la question : \"How many students does the school have now?\"",
                    "solution_markdown": "Il s'agit d'une donnee factuelle explicite (comme \"how old was the groom\" dans l'exemple resolu) : il suffit de la relever precisement et de la replacer dans une phrase complete, sans reformulation superflue.\n\nOn obtient : **The school now has over 2,000 students.**"
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "Dans un texte qui explique qu'un village a construit une nouvelle route grace a la contribution financiere volontaire de tous les habitants, malgre la pauvrete generale, reponds a la question : \"Why do you think the villagers agreed to contribute financially despite their poverty?\"",
                    "solution_markdown": "Cette question de type \"Why do you think\" demande une interpretation personnelle ancree dans le contexte donne (la pauvrete generale et le benefice collectif d'une route), pas une pure speculation.\n\nOn obtient : **The villagers probably agreed to contribute despite their poverty because they understood that a new road would benefit the whole community in the long run, for example by making it easier to transport goods and reach medical services, which outweighed the short-term financial sacrifice.**\n\nCette reponse relie explicitement l'interpretation (comprehension du benefice collectif) aux elements donnes par le contexte (pauvrete, projet collectif), exactement la methode attendue pour ce type de question."
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Dans un texte qui rapporte qu'une entrepreneure a d'abord echoue deux fois avant de reussir sa troisieme entreprise, en s'appuyant a chaque fois sur les lecons tirees de ses echecs precedents, reponds successivement aux deux questions suivantes en respectant strictement leurs consignes : (1) \"Give any two reasons that explain why her third business succeeded.\" (2 marks) (2) \"Did she give up after her first failure? Justify.\" (2 marks)",
                    "solution_markdown": "Cet exercice combine deux types de questions differents (raisons multiples chiffrees, et question fermee justifiee) sur le meme passage, ce qui exige d'appliquer deux methodes distinctes dans la meme reponse.\n\nPour la question 1, la consigne exige exactement deux raisons distinctes, chacune justifiee separement : **(1) She had learned from the specific mistakes made in her first two businesses, which allowed her to avoid repeating them in her third venture. (2) Her previous failures had taught her practical lessons about managing money and understanding her customers' needs, which she was able to apply successfully the third time.**\n\nPour la question 2, la consigne \"Did...? Justify\" exige une reponse tranchee suivie d'une justification textuelle explicite, jamais une reponse seule : **No, she did not give up after her first failure. According to the text, she started a second business afterwards, and even after that second failure, she went on to start a third one, which shows that she persisted despite repeated setbacks rather than abandoning her entrepreneurial project.**\n\nCet exercice montre que deux questions sur le meme texte peuvent exiger des methodes de reponse tres differentes : compter precisement le nombre d'elements demandes pour la premiere, et ne jamais omettre la justification textuelle explicite pour la seconde."
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Repere toujours d'abord l'information exacte dans le texte avant de rediger ta reponse : ne reponds jamais de memoire sans revenir au passage.",
                "\"Use your own words\" signifie reformuler pour prouver ta comprehension, pas recopier mot pour mot - mais cela n'interdit pas de s'appuyer sur les elements precis du texte.",
                "Adapte ta methode au type de question : Why -> explication causale complete ; donnee factuelle -> relever precisement ; give [n] reasons -> exactement ce nombre, chacune distincte ; Why do you think -> interpretation ancree dans le texte ; Did...? Justify -> reponse tranchee ET justification obligatoire.",
                "Ne t'arrete jamais a une citation seule : explique toujours en quoi elle repond precisement a la question posee.",
                "Compte le nombre d'elements demandes dans chaque question et fournis exactement ce nombre, presente de facon clairement separee.",
                "Au Bac, la section Comprehension represente une part importante de la note globale d'anglais : maitriser ces cinq types de questions permet de securiser un maximum de points sur un texte que tu comprends deja globalement."
            ]
        }
    ]
})

# ---------- 8. WORD FORMATION ----------
COURSES.append({
    "_slug": "word-formation",
    "cours_id": "cours-word-formation-bac-c-d-angl-2004",
    "meta": {
        "titre": "La transformation morphologique des mots selon le contexte (word formation)",
        "matiere": "Anglais",
        "serie": None,
        "sous_theme": "Vocabulaire et grammaire - derivation lexicale",
        "duree_estimee_min": 35,
        "tags": ["word formation", "suffixes", "prefixes", "derivation", "pluriel irregulier", "comparatif irregulier"],
        "statut": "brouillon"
    },
    "source": base_source(
        "1", "rdm-bac-c-d-anglais-2004-cameroun-ex1-qC.1-0",
        rappels_lies=[
            "rdm-bac-c-d-anglais-2004-cameroun-ex1-qC.2-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex1-qC.3-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex1-qC.4-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex1-qC.6-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex2-qD.1-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex2-qD.2-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex2-qD.3-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex2-qD.4-0",
            "rdm-bac-c-d-anglais-2004-cameroun-ex2-qD.5-0"
        ]
    ),
    "sections": [
        {
            "type": "accroche",
            "contenu_markdown": "\"Mosquitoes are ... insects. (harm)\" On te donne un mot de base entre parentheses, mais jamais sous la forme attendue par la phrase. C'est l'exercice de word formation, un classique du Bac qui revient chaque annee sous forme d'une dizaine d'items : il teste ta capacite a transformer un mot d'une categorie grammaticale a une autre (nom, adjectif, verbe, adverbe) grace aux suffixes, prefixes et formes irregulieres de l'anglais. Ce cours te donne la methode et les familles de transformation les plus frequentes."
        },
        {
            "type": "prerequis",
            "items": [
                "Connaitre les principales categories grammaticales (nom, verbe, adjectif, adverbe) et savoir les reconnaitre dans une phrase",
                "Avoir deja rencontre les suffixes et prefixes anglais les plus courants (-ful, -less, -ment, -ist, -er/-or, dis-, un-, in-)",
                "Connaitre les pluriels et comparatifs irreguliers les plus frequents (child/children, good/better, bad/worse)"
            ]
        },
        {
            "type": "regle",
            "titre": "Identifier la categorie manquante, puis appliquer la transformation adaptee",
            "contenu_markdown": "La formation du mot selon la fonction grammaticale exigee par la phrase consiste a repérer d'abord quelle categorie grammaticale manque (nom, adjectif, adverbe, verbe, comparatif...) a l'endroit du blanc, en observant les mots qui l'entourent (article, auxiliaire, preposition, nom a qualifier), puis a transformer le mot donne entre parentheses a l'aide des suffixes, prefixes ou formes irregulieres appropries pour obtenir cette categorie.\n\nLes familles de transformation les plus frequentes au Bac :\n- **Adjectif -> adverbe de comparaison** : \"late\" -> \"later\" (comparatif), utilise apres un verbe de deplacement pour comparer un moment a un autre.\n- **Adjectif -> verbe** : \"weak\" -> \"weaken\" (suffixe -en), pour exprimer l'action de rendre quelque chose ainsi.\n- **Adjectif -> adjectif negatif** : \"honest\" -> \"dishonest\" (prefixe dis-, irregulier ici : ni un- ni in-).\n- **Nom -> nom de personne/metier** : \"science\" -> \"scientist\" (suffixe -ist), pour designer celui qui exerce cette discipline.\n- **Nom -> nom abstrait de peine/etat** : \"prison\" -> \"imprisonment\" (suffixe -ment), terme juridique standard.\n- **Nom -> adjectif** : \"harm\" -> \"harmful\" (suffixe -ful, \"qui cause\") ou son oppose \"harmless\" (suffixe -less, \"sans\").\n- **Pluriels irreguliers** : \"child\" -> \"children\" (forme totalement irreguliere, a memoriser).\n- **Comparatifs irreguliers** : \"good\" -> \"better\" (jamais \"gooder\").\n- **Formes verbales imposees par un connecteur** : \"while\" + participe present quand le sujet n'est pas repete (\"travel\" -> \"travelling\") ; conditionnel de type 3 imposant le plus-que-parfait (\"see\" -> \"had seen\").",
            "formule_principale": "Reperer les mots autour du blanc (article, auxiliaire, preposition, connecteur) -> en deduire la categorie grammaticale attendue -> transformer le mot donne avec le suffixe/prefixe/forme irreguliere correspondant",
            "variantes": []
        },
        {
            "type": "exemple_resolu",
            "enonce_markdown": "Complete avec la forme appropriee du mot entre parentheses : \"Mosquitoes are ... insects. (harm)\"",
            "epreuve_source": True,
            "etapes": [
                {
                    "numero": 1,
                    "action": "Observer les mots qui entourent le blanc",
                    "justification": "Le blanc se situe entre le verbe \"are\" et le nom pluriel \"insects\" : cette position est typique d'un adjectif epithete qui qualifie le nom",
                    "resultat_markdown": "position : are + [BLANC] + insects -> adjectif attendu"
                },
                {
                    "numero": 2,
                    "action": "Identifier la nature du mot donne entre parentheses",
                    "justification": "\"Harm\" est un nom (le tort, la nuisance) qu'il faut transformer en adjectif pour qu'il puisse qualifier \"insects\"",
                    "resultat_markdown": "\"harm\" (nom) -> adjectif recherche"
                },
                {
                    "numero": 3,
                    "action": "Determiner le sens exact attendu par le contexte",
                    "justification": "Les moustiques sont connus pour causer des nuisances (transmission de maladies), pas pour en etre exempts : il faut donc l'adjectif qui signifie \"qui cause du tort\", pas son oppose",
                    "resultat_markdown": "sens attendu : \"qui cause du tort\" (pas \"sans tort\")"
                },
                {
                    "numero": 4,
                    "action": "Appliquer le suffixe correspondant a ce sens",
                    "justification": "Le suffixe \"-ful\" signifie \"plein de, qui cause\", exactement le sens recherche ici ; \"-less\" signifierait au contraire \"sans\", ce qui inverserait le sens",
                    "resultat_markdown": "**Mosquitoes are harmful insects.**"
                }
            ],
            "conclusion_markdown": "La methode complete (position dans la phrase -> categorie attendue -> sens exact -> suffixe correspondant) permet de ne jamais confondre deux suffixes opposes comme -ful et -less, qui produisent des sens totalement contraires a partir du meme mot de base."
        },
        {
            "type": "erreurs_classiques",
            "items": [
                {
                    "erreur_markdown": "Confondre deux suffixes opposes qui se ressemblent, comme -ful et -less (\"harmful\" vs \"harmless\")",
                    "pourquoi_faux": "Les suffixes -ful (\"qui contient, qui cause\") et -less (\"sans, depourvu de\") sont opposes par le sens mais se ressemblent par la forme ; sous la pression de l'examen, beaucoup de candidats les confondent et produisent l'adjectif contraire de celui attendu.",
                    "correction_markdown": "Relis toujours le sens global de la phrase apres avoir choisi ton suffixe, pour verifier qu'il ne l'inverse pas par rapport a ce que le contexte decrit reellement."
                },
                {
                    "erreur_markdown": "Appliquer un suffixe regulier a un mot qui a en realite une forme irreguliere (\"gooder\" au lieu de \"better\", \"childs\" au lieu de \"children\")",
                    "pourquoi_faux": "Certains adjectifs et noms tres frequents (good, bad, child, man, woman, foot, tooth...) ont des formes de comparatif ou de pluriel completement irregulieres, qui ne suivent aucune regle de suffixe : les regles regulieres ne s'y appliquent jamais.",
                    "correction_markdown": "Memorise les irreguliers les plus frequents comme des exceptions a apprendre par coeur, independamment de toute regle de suffixe."
                },
                {
                    "erreur_markdown": "Laisser le mot a sa categorie grammaticale d'origine sans le transformer, en pensant qu'il convient tel quel (\"late\" au lieu de \"later\", \"weak\" au lieu de \"weaken\")",
                    "pourquoi_faux": "Un mot laisse sous sa forme de base ne peut pas toujours occuper la position grammaticale attendue par la phrase (un adjectif ne peut pas fonctionner comme un verbe conjugue, par exemple) ; l'exercice de word formation demande justement de reconnaitre quand une transformation est necessaire.",
                    "correction_markdown": "Verifie systematiquement la fonction grammaticale attendue a la position du blanc avant de decider si le mot donne doit etre transforme ou peut rester tel quel."
                },
                {
                    "erreur_markdown": "Ignorer un connecteur ou une structure temporelle qui impose une forme verbale precise (while + V-ing, conditionnel type 3 + plus-que-parfait)",
                    "pourquoi_faux": "Certains connecteurs imposent une forme verbale specifique independamment du sens general du verbe : \"while\" sans sujet repete appelle un participe present, et une principale au conditionnel passe impose un plus-que-parfait dans la subordonnee en if, quel que soit le verbe utilise.",
                    "correction_markdown": "Repere toujours le connecteur ou la structure temporelle qui entoure le blanc (while, if, la principale deja conjuguee) avant de choisir la forme du verbe, pas seulement le sens du mot de base."
                }
            ]
        },
        {
            "type": "exercices_application",
            "items": [
                {
                    "numero": 1,
                    "difficulte": "facile",
                    "enonce_markdown": "Complete avec la forme appropriee : \"It was very ... of him to help the old man cross the road. (kind)\"",
                    "solution_markdown": "Le blanc se situe entre \"very\" et \"of him\", position typique d'un adjectif (\"very\" ne modifie que des adjectifs ou des adverbes). \"Kind\" est deja un adjectif, mais la phrase attend ici une qualification du comportement decrit ensuite par \"to help\" : la forme adjective reste identique, sans transformation supplementaire necessaire dans ce cas simple.\n\nOn obtient : **It was very kind of him to help the old man cross the road.**\n\n(Cet exercice rappelle qu'il faut d'abord verifier si une transformation est reellement necessaire : ici, \"kind\" est deja a la bonne categorie grammaticale.)"
                },
                {
                    "numero": 2,
                    "difficulte": "moyen",
                    "enonce_markdown": "Complete avec la forme appropriee : \"The government has taken measures to ensure the ... of all citizens. (safe)\"",
                    "solution_markdown": "Le blanc suit l'article defini \"the\" et precede \"of all citizens\" : cette position attend un nom abstrait, pas un adjectif. \"Safe\" (adjectif) doit etre transforme en nom abstrait grace au suffixe \"-ty\", qui donne \"safety\" (la securite).\n\nOn obtient : **The government has taken measures to ensure the safety of all citizens.**"
                },
                {
                    "numero": 3,
                    "difficulte": "approfondissement",
                    "enonce_markdown": "Complete les trois blancs avec la forme appropriee et identifie a chaque fois la categorie grammaticale visee : \"Despite her ... (weak), she showed great ... (brave) during the operation, which the doctors found truly ... (admire).\"",
                    "solution_markdown": "Cet exercice combine trois transformations differentes dans une seule phrase, ce qui exige d'appliquer la methode complete (position -> categorie -> suffixe) trois fois de suite, sans se laisser influencer par la transformation precedente.\n\nPremier blanc : apres \"her\" (determinant possessif), la phrase attend un nom. \"Weak\" (adjectif) devient le nom \"weakness\" grace au suffixe \"-ness\" (qui forme des noms abstraits a partir d'adjectifs).\n\nDeuxieme blanc : apres \"great\" (adjectif qui modifie un nom), la phrase attend egalement un nom. \"Brave\" (adjectif) devient \"bravery\" grace au suffixe \"-ery\".\n\nTroisieme blanc : apres \"truly\" (adverbe qui modifie un adjectif) et le verbe \"found\" (qui introduit un attribut de l'objet), la phrase attend un adjectif. \"Admire\" (verbe) devient l'adjectif \"admirable\" grace au suffixe \"-able\" (\"qui merite d'etre admire\").\n\nOn obtient : **Despite her weakness, she showed great bravery during the operation, which the doctors found truly admirable.**\n\nCet exercice montre que dans une meme phrase, chaque blanc doit etre analyse independamment : la categorie attendue change a chaque fois selon les mots qui l'entourent, meme quand plusieurs blancs se suivent dans un texte court."
                }
            ]
        },
        {
            "type": "synthese",
            "items_markdown": [
                "Observe toujours les mots qui entourent le blanc (article, auxiliaire, preposition, connecteur) avant de choisir la transformation : ils te disent quelle categorie grammaticale est attendue.",
                "Verifie ensuite le sens exact demande par le contexte, en particulier quand deux suffixes opposes existent pour le meme mot de base (-ful/-less, positif/negatif).",
                "Memorise les formes irregulieres les plus frequentes (good/better, bad/worse, child/children, man/men) : aucune regle de suffixe ne s'y applique.",
                "Repere les connecteurs qui imposent une forme verbale precise (while + V-ing sans sujet repete, conditionnel type 3 + plus-que-parfait).",
                "Ne transforme jamais un mot par reflexe : verifie d'abord s'il est deja a la bonne categorie grammaticale pour la phrase.",
                "Au Bac, cet exercice compte souvent une dizaine d'items sur plusieurs sections de l'epreuve : automatiser la methode (position -> categorie -> sens -> suffixe/forme) permet de gagner du temps et de securiser des points faciles."
            ]
        }
    ]
})

# ---------- WRITE ALL FILES ----------
for c in COURSES:
    write_cours(c)

print()
print("TOTAL COURSES WRITTEN:", len(COURSES))
print(sorted(c["cours_id"] for c in COURSES))
