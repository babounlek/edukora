\
# -*- coding: utf-8 -*-
import json, os

OUT_DIR = "/sessions/brave-ecstatic-ritchie/mnt/Epreuves/json/cm/bac-c-d-anglais-2012-cameroun"
EPREUVE = "bac-c-d-anglais-2012-cameroun"

intro = (
    "**SECTION D: ESSAY**\n\n"
    "Choose any ONE of the following topics and write an essay of between 250 to 300."
)

# ---------------- Topic 1: opinion essay ----------------
rappel1 = (
    "Un essai d'opinion (opinion essay) en anglais suit une structure fixe en trois temps : "
    "une introduction qui reformule le sujet et annonce clairement la position défendue, un "
    "développement qui présente plusieurs arguments illustrés par des exemples concrets, et "
    "une conclusion qui résume la position et l'élargit. Chaque paragraphe du développement "
    "défend une seule idée, introduite par un connecteur logique clair (firstly, moreover, "
    "however, in addition...)."
)

essay1_text = (
    "**Health for All by the Year 2000: an unfinished goal**\n\n"
    "When the World Health Organization launched the \"Health for All by the Year 2000\" "
    "initiative, the ambition was that every person on earth would enjoy an acceptable level "
    "of health by that date. More than two decades after this deadline, I strongly believe "
    "that this goal has not been fully achieved, even though considerable progress has been "
    "made.\n\n"
    "On the one hand, undeniable advances have taken place. Vaccination campaigns have "
    "eradicated or drastically reduced diseases such as smallpox and polio in most parts of "
    "the world. Life expectancy has increased significantly, even in developing countries, "
    "thanks to better access to clean water, basic medicine and health education. "
    "Governments and international organizations have built hospitals and health centres in "
    "areas that had none before.\n\n"
    "On the other hand, huge inequalities remain between rich and poor countries, and even "
    "within the same country. In many rural areas of Africa, for instance, people still have "
    "to walk for hours to reach the nearest health centre, and qualified doctors remain "
    "extremely scarce there. Diseases that could easily be prevented, such as malaria and "
    "diarrhoea, still kill millions of children every year simply because their families "
    "cannot afford proper treatment. HIV/AIDS, tuberculosis and other epidemics continue to "
    "devastate entire communities, particularly where poverty limits access to medication.\n\n"
    "For all these reasons, \"Health for All\" remains an ideal rather than a reality. The "
    "target has certainly pushed the world in the right direction, but true health equity "
    "will only be achieved when access to quality care stops depending on where a person "
    "happens to be born. Much work still needs to be done before this promise can honestly "
    "be considered fulfilled."
)

q1_corrige = "### Rappel de méthode\n" + rappel1 + "\n\n" + (
    "### Corrigé\n"
    "Le sujet demande une prise de position claire sur la question « Do you think Health for "
    "all by the year 2000 has been achieved? ». L'essai proposé ci-dessous adopte une "
    "position nuancée mais tranchée : l'objectif n'a pas été pleinement atteint, malgré des "
    "progrès réels. Il respecte la structure en trois temps (introduction avec thèse, "
    "développement en deux paragraphes équilibrés « pour » et « contre » qui convergent vers "
    "la même conclusion, puis conclusion) et la fourchette de 250 à 300 mots demandée par la "
    "consigne.\n\n"
    + essay1_text + "\n\n"
    "### Piège à éviter\n"
    "Ne te contente jamais d'un simple « yes » ou « no » sans développement : le correcteur "
    "évalue autant la qualité de l'argumentation et la richesse du vocabulaire que la "
    "position choisie elle-même - les deux camps (« achieved » ou « not achieved ») peuvent "
    "obtenir la note maximale si l'essai est bien construit.\n\n"
    "### Conseil\n"
    "Compte approximativement tes mots par paragraphe pendant l'entraînement (environ 50 "
    "mots pour l'introduction, 150 à 180 pour les deux paragraphes de développement, 50 à 60 "
    "pour la conclusion) : cela t'évite de découvrir en fin d'épreuve que tu es très en "
    "dessous ou très au-dessus de la fourchette imposée."
)

# ---------------- Topic 2: speech ----------------
rappel2 = (
    "Un discours (speech) s'adresse directement à un auditoire précis et respecte des codes "
    "propres à l'oral : une formule d'ouverture qui salue le public (« Good morning/"
    "afternoon, dear... »), l'annonce claire du sujet traité, un développement structuré en "
    "points clairement séparés, et une formule de clôture qui remercie l'auditoire. Le ton "
    "reste plus direct et plus engageant qu'un essai écrit classique, avec des phrases plus "
    "courtes et des questions rhétoriques adressées au public."
)

essay2_text = (
    "Good afternoon, dear friends,\n\n"
    "Thank you for inviting me to speak to you today about a subject that concerns each and "
    "every one of us: hygiene and sanitation.\n\n"
    "Hygiene and sanitation are not just medical words we hear at school; they are habits "
    "that decide whether we stay healthy or fall sick. Every year, diseases such as cholera, "
    "typhoid fever and diarrhoea kill thousands of people in our country, and in almost "
    "every case, these diseases could have been prevented through simple, everyday "
    "actions.\n\n"
    "Let me share with you three simple habits that can change our lives. First, washing our "
    "hands with soap before eating and after using the toilet remains the single most "
    "effective way of stopping the spread of germs. Second, drinking only clean, boiled or "
    "properly treated water protects us from waterborne diseases that are still far too "
    "common in our villages. Third, keeping our surroundings clean, by properly disposing of "
    "rubbish and building and using latrines correctly, prevents flies and mosquitoes from "
    "spreading disease among our families.\n\n"
    "I know that some of you may think that these actions are too small to matter. But real "
    "change never starts with grand gestures, it starts with small habits repeated every "
    "single day. If each young person here goes home today and washes his or her hands "
    "properly, boils drinking water, and keeps his or her compound clean, we will already be "
    "protecting our families from illnesses that our health centres struggle to treat.\n\n"
    "I therefore urge you, as the youth of this village, to become the ambassadors of "
    "hygiene in your own homes. Talk to your parents, your brothers and sisters, your "
    "neighbours. Show them by example.\n\n"
    "Thank you very much for your attention, and let us all commit today to a cleaner, "
    "healthier village."
)

q2_corrige = "### Rappel de méthode\n" + rappel2 + "\n\n" + (
    "### Corrigé\n"
    "Le sujet impose un format précis - un discours à prononcer devant le groupe de jeunes "
    "du village - et non un essai écrit classique. Le modèle ci-dessous respecte les codes "
    "de l'oral demandés : formule d'ouverture, annonce du thème, développement en trois "
    "conseils pratiques et concrets, puis formule de clôture qui remercie l'auditoire et "
    "l'appelle à agir.\n\n"
    + essay2_text + "\n\n"
    "### Piège à éviter\n"
    "N'écris jamais un discours comme un essai classique sans t'adresser à l'auditoire : "
    "l'absence de formule d'ouverture (« Dear friends », « Ladies and gentlemen »...) et de "
    "formule de clôture (« Thank you for listening »...) fait perdre des points, même si le "
    "contenu sur le fond est excellent.\n\n"
    "### Conseil\n"
    "Utilise des questions rhétoriques et des phrases courtes pour donner un vrai rythme "
    "oral à ton discours : un texte qui se lit comme s'il était prononcé à voix haute "
    "impressionne toujours plus le correcteur qu'un texte purement écrit."
)

# ---------------- Topic 3: personal letter ----------------
rappel3 = (
    "Une lettre à un proche respecte une présentation fixe en anglais : l'adresse de "
    "l'expéditeur en haut à droite, une formule d'appel adaptée au destinataire (« Dear + "
    "prénom » pour un frère), un corps de lettre organisé en paragraphes, et une formule de "
    "politesse finale adaptée à la relation (« Your loving brother », « Yours "
    "affectionately »...) suivie de la signature. Le registre reste chaleureux et direct "
    "puisqu'il s'agit d'un membre de la famille, sans les formules très cérémonieuses d'une "
    "lettre administrative."
)

essay3_text = (
    "G.H.S. Rex Majama\n\n"
    "P.O. Box 15\n\n"
    "Majama\n\n"
    "Dear Emmanuel,\n\n"
    "I was deeply saddened to learn that you have been hospitalized because of your heart "
    "condition, and I wanted to write to you as soon as possible to share a few thoughts, "
    "out of the love and concern I have for you as your brother.\n\n"
    "I know that smoking has been part of your life for many years now, and that giving it "
    "up will not be easy. However, cigarettes are doing serious damage to your heart and "
    "your lungs, and every single one you smoke makes your recovery harder. I strongly "
    "advise you to speak to your doctor about a proper plan to quit smoking completely, "
    "rather than simply reducing the number of cigarettes you smoke.\n\n"
    "I also want to mention your weight, Emmanuel, because I care about you. Carrying too "
    "much weight puts extra strain on your heart, exactly the organ that is already "
    "struggling. Once you leave the hospital, I would really encourage you to eat more "
    "fruit and vegetables, cut down on fatty and sugary food, and start light physical "
    "exercise such as walking, as soon as your doctor allows it.\n\n"
    "Please remember that our whole family is behind you. Mother has not stopped worrying "
    "since she heard the news, and we are all praying for your quick recovery. Do not "
    "hesitate to call me if you need anything at all, whether it is company at the hospital "
    "or simply someone to talk to.\n\n"
    "Take good care of yourself, Emmanuel. Your health matters more than any habit.\n\n"
    "Your loving brother,\n\n"
    "Marcel"
)

q3_corrige = "### Rappel de méthode\n" + rappel3 + "\n\n" + (
    "### Corrigé\n"
    "Le sujet fournit toutes les données nécessaires à la mise en situation : l'expéditeur "
    "(Marcel Muhum), son adresse (G.H.S. Rex Majama, P.O. Box 15, Majama) et le destinataire "
    "(son frère Emmanuel, hospitalisé, fumeur et en surpoids). La lettre modèle ci-dessous "
    "reprend ces éléments dans l'en-tête et la signature, puis développe deux conseils "
    "distincts (arrêter de fumer, corriger l'alimentation et l'activité physique), avant de "
    "conclure sur le soutien familial.\n\n"
    + essay3_text + "\n\n"
    "### Piège à éviter\n"
    "N'oublie jamais les éléments de présentation propres à la lettre personnelle (adresse, "
    "formule d'appel, formule de clôture) : même une lettre au contenu pertinent perd des "
    "points si elle ressemble à un simple essai sans en-tête ni signature.\n\n"
    "### Conseil\n"
    "Utilise systématiquement les données fournies par le sujet (ici le nom Marcel Muhum et "
    "l'adresse G.H.S. Rex Majama, P.O. Box 15, Majama) dans l'en-tête et la signature de ta "
    "lettre : le correcteur vérifie que tu as bien exploité toutes les consignes de la mise "
    "en situation, pas seulement le thème général."
)

ex4_questions = [
    {
        "numero": "1",
        "enonce_markdown": "1) Do you think Health for all by the year 2000 has been achieved?",
        "corrige_markdown": q1_corrige,
        "themes": ["opinion essay", "essay writing", "global health"],
        "difficulte_estimee": "élevée",
        "type_reponse": "ouverte",
        "choix": [],
        "reponse_correcte": "",
        "rappels_de_methode": [{
            "id": "rdm-bac-c-d-anglais-2012-cameroun-ex4-q1-0",
            "competence": "Rédaction d'un essai d'opinion en anglais (opinion essay)",
            "contenu_markdown": rappel1,
            "cours_genere": True,
            "cours_id": "cours_redaction-dun-essai-dopinion-en-anglais"
        }]
    },
    {
        "numero": "2",
        "enonce_markdown": "2) You are invited by the youth group of your village to give a talk on hygiene and sanitation. Write the speech to be delivered.",
        "corrige_markdown": q2_corrige,
        "themes": ["speech writing", "public speaking", "hygiene and sanitation"],
        "difficulte_estimee": "élevée",
        "type_reponse": "ouverte",
        "choix": [],
        "reponse_correcte": "",
        "rappels_de_methode": [{
            "id": "rdm-bac-c-d-anglais-2012-cameroun-ex4-q2-0",
            "competence": "Rédaction d'un discours en anglais (speech writing)",
            "contenu_markdown": rappel2,
            "cours_genere": True,
            "cours_id": "cours_redaction-dun-discours-en-anglais"
        }]
    },
    {
        "numero": "3",
        "enonce_markdown": (
            "3) Your brother Emmanuel Muhum has been hospitalized because of a heart disease. "
            "He has been a cigarette smoker for long and is also very fat. Write a letter "
            "advising him on what to do. Your name is Marcel Muhum and your address is "
            "G.H.S. Rex Majama, P.O. Box 15, Majama."
        ),
        "corrige_markdown": q3_corrige,
        "themes": ["personal letter", "letter of advice", "letter writing format"],
        "difficulte_estimee": "élevée",
        "type_reponse": "ouverte",
        "choix": [],
        "reponse_correcte": "",
        "rappels_de_methode": [{
            "id": "rdm-bac-c-d-anglais-2012-cameroun-ex4-q3-0",
            "competence": "Rédaction d'une lettre personnelle en anglais (personal letter)",
            "contenu_markdown": rappel3,
            "cours_genere": True,
            "cours_id": "cours_redaction-dune-lettre-personnelle-en-anglais"
        }]
    },
]

ex4 = {
    "epreuve_source": f"{EPREUVE}.pdf",
    "numero_exercice": "4",
    "matiere": "Anglais",
    "serie": "C/D",
    "examen": "bac",
    "origine": "officiel",
    "etablissement": None,
    "annee": 2012,
    "duree_epreuve": None,
    "coefficient": None,
    "points": None,
    "figures": [],
    "enonce_intro_markdown": intro,
    "questions": ex4_questions,
    "mots_cles_recherche": [
        "anglais", "essay writing", "speech writing", "letter writing", "production ecrite",
        "opinion essay", "personal letter", "BAC C D"
    ],
    "incertitudes": [
        "L'en-tete du sujet indique «BACCALAUREAT «C & D»» : l'epreuve s'adresse identiquement aux deux series C et D. Le champ serie a ete renseigne «C/D» faute de code combine dans le referentiel, par coherence avec les exercices 1, 2 et 3 de la meme epreuve.",
        "Section D (Essay) n'affiche aucun bareme explicite sur la page source, contrairement aux sections A, B et C (chacune «10 MARKS» explicitement indique) ; par symetrie avec le reste du sujet (total de 30 points deja confirme sur les sections A+B+C), il est tres vraisemblable que cette section vaille egalement 10 points (total 40), mais ce n'est pas garanti par le texte de l'epreuve - le champ points a donc ete laisse a null plutot que de deviner cette valeur.",
        "La consigne source s'arrete a « write an essay of between 250 to 300 » sans indiquer explicitement l'unite (« words » manque a la fin de la phrase dans le PDF source) ; reproduite fidelement telle quelle dans enonce_intro_markdown, cette consigne est neanmoins interpretee dans les trois corriges comme demandant environ 250 a 300 mots, unite standard pour ce type d'exercice au BAC.",
        "Une seule des trois consignes doit etre traitee par le candidat le jour de l'examen (« Choose any ONE of the following topics »). Les trois sujets ont neanmoins ete corriges integralement (essai d'opinion, discours, lettre personnelle), chacun illustrant un format de production ecrite different explicitement au programme de la matiere - utile pour un usage pedagogique de revision couvrant les trois formats plutot qu'un seul.",
        "Chacune des trois sous-questions de l'Exercice 4 correspond a un format de production distinct (essai d'opinion, discours, lettre personnelle) : contrairement aux exercices 1 a 3 de cette meme epreuve, aucune mutualisation de cours n'a ete appliquee ici, les trois rappels de methode etant genuinement distincts."
    ],
    "statut": "brouillon"
}

with open(os.path.join(OUT_DIR, f"{EPREUVE}_exercice_4.json"), "w", encoding="utf-8") as f:
    json.dump(ex4, f, ensure_ascii=False, indent=2)

print("exercice_4 written")

for q in ex4_questions:
    for r in q["rappels_de_methode"]:
        assert r["contenu_markdown"] in q["corrige_markdown"], f"MISMATCH {q['numero']}"
print("ex4 verbatim OK")

# word counts for the three model productions
for name, txt in [("essay1", essay1_text), ("essay2 (speech)", essay2_text), ("essay3 (letter)", essay3_text)]:
    # strip markdown bold markers and headers for counting
    import re as _re
    clean = _re.sub(r"[*#]", "", txt)
    words = len(clean.split())
    print(name, "word count:", words)
