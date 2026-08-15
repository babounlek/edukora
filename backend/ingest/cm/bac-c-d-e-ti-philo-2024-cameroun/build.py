# -*- coding: utf-8 -*-
import json, os, re, unicodedata

OUT = "/sessions/wonderful-inspiring-shannon/mnt/Epreuves/json/cm/bac-c-d-e-ti-philo-2024-cameroun"
EPREUVE_SOURCE = "bac-c-d-e-ti-philo-2024-cameroun.pdf"
EPREUVE_ID = "bac-c-d-e-ti-philo-2024-cameroun"

INCERTITUDE_SERIE = "Épreuve commune aux séries C, D, E, TI (bandeau MINESEC/OBC : \"SERIES: C-D-E-TI\") - un seul code retenu par contrainte de schéma (serie = \"C\")."

def slugify(text):
    text = text.replace("'", "").replace("’", "")
    nfkd = unicodedata.normalize('NFKD', text)
    ascii_text = nfkd.encode('ascii', 'ignore').decode('ascii')
    ascii_text = ascii_text.lower()
    ascii_text = re.sub(r'[^a-z0-9]+', '-', ascii_text).strip('-')
    return ascii_text

# ---------------------------------------------------------------------------
# EXERCICE 1 - Premiere partie : evaluation des ressources (explication de texte)
# ---------------------------------------------------------------------------

texte_bachelard = (
    "**Première partie : l'évaluation des ressources (9 points)**\n\n"
    "**Texte**\n\n"
    "« Déjà l'observation a besoin d'un *corps* de précautions qui conduisent à réfléchir avant de regarder, "
    "qui réforment du moins la première vision, de sorte que ce n'est jamais la première observation qui est "
    "la bonne. L'observation scientifique est toujours une observation polémique ; elle confirme ou infirme "
    "une thèse antérieure, un schéma préalable, un plan d'observation ; elle montre en démontrant ; elle "
    "hiérarchise les apparences ; elle transcende l'immédiat ; elle reconstruit le réel après avoir reconstruit "
    "ses schémas. Naturellement, dès qu'on passe de l'observation à l'expérimentation, le caractère polémique "
    "de la connaissance devient plus net encore. Alors il faut que le phénomène soit trié, filtré, épuré, coulé "
    "dans le moule des instruments, produit sur le plan des instruments. Or, les instruments ne sont que des "
    "théories matérialisées. Il en sort des phénomènes qui portent de toutes parts la marque théorique. »\n\n"
    "Gaston Bachelard, *Le Nouvel Esprit scientifique* (1934), PUF, 2003.\n\n"
    "*Lis attentivement le texte ci-dessus et réponds aux questions y afférentes.*"
)

rappel_ex1_q1 = ("Définir un concept en explication de texte philosophique ne consiste pas à réciter une "
    "définition abstraite ou un sens commun du mot, mais à restituer le sens précis que l'auteur lui donne "
    "dans son propre raisonnement, en s'appuyant sur les indices que le texte fournit lui-même.")

corrige_ex1_q1 = (
"### Rappel de méthode\n"
f"{rappel_ex1_q1}\n\n"
"### Corrigé détaillé\n"
"**Première vision.** La perception spontanée et immédiate du réel, celle qui précède tout travail de "
"rectification théorique : on regarde sans avoir au préalable réfléchi à ce que l'on va regarder ni pourquoi. "
"Bachelard la disqualifie d'emblée comme fondement de la connaissance scientifique : « ce n'est jamais la "
"première observation qui est la bonne. »\n\n"
"**Observation scientifique.** Non un simple constat neutre du réel, mais une observation que Bachelard "
"qualifie de « polémique » : elle est orientée par une thèse antérieure, un schéma préalable ou un plan "
"d'observation qu'elle cherche à confirmer ou à infirmer. Elle hiérarchise les apparences et reconstruit le "
"réel plutôt que de l'enregistrer passivement, ce qui la distingue radicalement de la première vision.\n\n"
"**Expérimentation.** Le prolongement actif de l'observation scientifique, dans lequel le phénomène étudié "
"n'est plus seulement regardé mais littéralement produit : trié, filtré, épuré, coulé dans le moule "
"d'instruments eux-mêmes conçus à partir de théories. Bachelard résume ce point d'un mot : « les instruments "
"ne sont que des théories matérialisées. » L'expérimentation porte donc à son comble le caractère théorique "
"déjà présent dans l'observation.\n\n"
"### Piège à éviter\n"
"Ne pas traiter « observation scientifique » comme une version simplement plus attentive ou plus précise de "
"la première vision. La différence que pose Bachelard n'est pas de degré (mieux regarder) mais de nature "
"(regarder à travers une théorie qui structure déjà ce qui est vu)."
)

rappel_ex1_q2 = ("Le thème répond à la question « de quoi parle le texte ? » : un sujet général. Le problème "
    "philosophique répond à une question plus exigeante, « quelle tension ou quelle difficulté le texte "
    "cherche-t-il à résoudre ? ». C'est l'identification de cette tension, et non la seule reformulation du "
    "sujet, qui distingue une analyse philosophique d'une paraphrase.")

corrige_ex1_q2 = (
"### Rappel de méthode\n"
f"{rappel_ex1_q2}\n\n"
"### Corrigé détaillé\n"
"**Thème.** Le texte porte sur l'épistémologie, c'est-à-dire sur la nature de la connaissance scientifique : "
"plus précisément, sur le statut de l'observation et de l'expérimentation, et sur leur rapport à la théorie.\n\n"
"**Problème philosophique.** Si l'observation est censée nous donner un accès fidèle au réel, comment "
"peut-elle être en même temps, comme l'affirme Bachelard, une construction théorique qui rectifie, "
"hiérarchise et parfois même produit ce qu'elle prétend seulement constater ? Le texte affronte ainsi le "
"paradoxe suivant : plus la science progresse de l'observation vers l'expérimentation, plus elle semble "
"s'éloigner du réel brut, puisqu'elle le façonne activement au lieu de le recueillir passivement ; et "
"pourtant c'est précisément cet éloignement, cette médiation théorique, qui rend la connaissance scientifique "
"possible et rigoureuse. Le problème est donc de savoir si l'objectivité scientifique se gagne malgré cette "
"construction théorique ou grâce à elle.\n\n"
"### Conseil\n"
"Formule toujours le problème philosophique comme une tension entre deux exigences qui semblent se "
"contredire (ici : fidélité au réel et construction théorique du réel) plutôt que comme une simple question "
"générale sur le sujet du texte : cela montre au correcteur que tu as identifié l'enjeu véritable, pas "
"seulement la matière du texte."
)

rappel_ex1_q3 = ("La thèse est la réponse affirmative que l'auteur apporte au problème philosophique "
    "identifié : une phrase synthétique qui résume sa position, souvent repérable dans une formule dense ou "
    "récurrente du texte.")

corrige_ex1_q3 = (
"### Rappel de méthode\n"
f"{rappel_ex1_q3}\n\n"
"### Corrigé détaillé\n"
"Bachelard soutient que la connaissance scientifique n'est jamais un décalque passif du réel : elle est une "
"construction théorique et polémique de bout en bout. Observer et expérimenter scientifiquement, c'est "
"toujours déjà appliquer, vérifier ou rectifier une théorie préalable, si bien que les phénomènes obtenus, en "
"particulier par l'expérimentation, « portent de toutes parts la marque théorique. »\n\n"
"### Conseil\n"
"Cite la formule la plus dense du texte plutôt que de la paraphraser vaguement : ici, « les instruments ne "
"sont que des théories matérialisées » condense à elle seule toute la thèse de l'auteur, et la citer avec un "
"bref commentaire rapporte des points de rigueur au correcteur."
)

rappel_ex1_q4 = ("La structure logique d'un texte argumentatif s'articule généralement en trois temps : un "
    "postulat de départ (une affirmation posée comme fondement), une série d'arguments qui en tirent les "
    "conséquences, et une conclusion qui synthétise la position finale de l'auteur. Il faut restituer cet "
    "enchaînement dans l'ordre du texte, en montrant comment chaque argument découle du précédent plutôt que "
    "de citer des phrases isolées.")

corrige_ex1_q4 = (
"### Rappel de méthode\n"
f"{rappel_ex1_q4}\n\n"
"### Corrigé détaillé\n"
"**Postulat.** L'observation a besoin d'un corps de précautions qui réforment la première vision : ce n'est "
"jamais la première observation qui est la bonne.\n\n"
"**Arguments.**\n\n"
"1. L'observation scientifique est toujours polémique : elle confirme ou infirme une thèse antérieure, un "
"schéma préalable, un plan d'observation, au lieu de simplement enregistrer ce qui se présente.\n\n"
"2. Cette observation « montre en démontrant » : elle hiérarchise les apparences et transcende l'immédiat, "
"reconstruisant le réel après avoir reconstruit ses propres schémas théoriques.\n\n"
"3. Lorsqu'on passe de l'observation à l'expérimentation, ce caractère polémique s'accentue encore : le "
"phénomène doit être trié, filtré, épuré, coulé dans le moule des instruments.\n\n"
"4. Or les instruments eux-mêmes ne sont que des théories matérialisées, si bien que les phénomènes qu'ils "
"produisent portent nécessairement la marque de la théorie qui les a construits.\n\n"
"**Conclusion.** Il n'existe donc pas d'observation scientifique neutre : toute connaissance du réel en "
"sciences est déjà une construction théorique, polémique par nature, et cette construction s'intensifie à "
"mesure que l'on progresse de la simple observation vers l'expérimentation instrumentée.\n\n"
"### Piège à éviter\n"
"Ne pas confondre la structure logique du texte avec un découpage phrase par phrase : chaque argument doit "
"être reformulé comme une étape du raisonnement qui prépare la conclusion, non comme une citation isolée "
"recopiée sans lien avec les autres."
)

exercice1 = {
  "epreuve_source": EPREUVE_SOURCE,
  "numero_exercice": "1",
  "pays": "cm",
  "matiere": "Philosophie",
  "nature_epreuve": None,
  "serie": "C",
  "examen": "bac",
  "origine": "officiel",
  "etablissement": None,
  "annee": 2024,
  "duree_epreuve": "2h",
  "coefficient": "2",
  "points": 9,
  "figures": [],
  "enonce_intro_markdown": texte_bachelard,
  "questions": [
    {
      "numero": "1",
      "enonce_markdown": "Définis les trois concepts suivants employés dans le texte : première vision, observation scientifique, expérimentation. (1 point par concept, soit 3 points)",
      "corrige_markdown": corrige_ex1_q1,
      "themes": ["épistémologie", "Bachelard", "observation scientifique", "définition de concepts"],
      "difficulte_estimee": "moyenne",
      "type_reponse": "ouverte",
      "choix": [],
      "reponse_correcte": "",
      "rappels_de_methode": [
        {
          "id": "rdm-bac-c-d-e-ti-philo-2024-cameroun-ex1-q1-0",
          "competence": "Définir rigoureusement des concepts philosophiques dans leur contexte",
          "contenu_markdown": rappel_ex1_q1,
          "cours_genere": False,
          "cours_id": None
        }
      ]
    },
    {
      "numero": "2",
      "enonce_markdown": "Présente le thème du texte, puis dégage le problème philosophique qu'il soulève. (2 points)",
      "corrige_markdown": corrige_ex1_q2,
      "themes": ["problématisation", "épistémologie", "philosophie des sciences"],
      "difficulte_estimee": "moyenne",
      "type_reponse": "ouverte",
      "choix": [],
      "reponse_correcte": "",
      "rappels_de_methode": [
        {
          "id": "rdm-bac-c-d-e-ti-philo-2024-cameroun-ex1-q2-0",
          "competence": "Distinguer thème et problème philosophique d'un texte",
          "contenu_markdown": rappel_ex1_q2,
          "cours_genere": False,
          "cours_id": None
        }
      ]
    },
    {
      "numero": "3",
      "enonce_markdown": "Dégage la thèse défendue par l'auteur dans ce texte. (1 point)",
      "corrige_markdown": corrige_ex1_q3,
      "themes": ["thèse d'auteur", "Bachelard", "épistémologie"],
      "difficulte_estimee": "faible",
      "type_reponse": "ouverte",
      "choix": [],
      "reponse_correcte": "",
      "rappels_de_methode": [
        {
          "id": "rdm-bac-c-d-e-ti-philo-2024-cameroun-ex1-q3-0",
          "competence": "Dégager la thèse d'un auteur dans un texte philosophique",
          "contenu_markdown": rappel_ex1_q3,
          "cours_genere": False,
          "cours_id": None
        }
      ]
    },
    {
      "numero": "4",
      "enonce_markdown": "Décline la structure logique du texte, en identifiant son postulat, ses arguments et sa conclusion. (3 points)",
      "corrige_markdown": corrige_ex1_q4,
      "themes": ["structure logique", "postulat", "arguments", "conclusion"],
      "difficulte_estimee": "élevée",
      "type_reponse": "ouverte",
      "choix": [],
      "reponse_correcte": "",
      "rappels_de_methode": [
        {
          "id": "rdm-bac-c-d-e-ti-philo-2024-cameroun-ex1-q4-0",
          "competence": "Analyser la structure logique d'un texte argumentatif (postulat, arguments, conclusion)",
          "contenu_markdown": rappel_ex1_q4,
          "cours_genere": False,
          "cours_id": None
        }
      ]
    }
  ],
  "mots_cles_recherche": ["Bachelard", "épistémologie", "observation scientifique", "expérimentation", "philosophie des sciences", "explication de texte"],
  "incertitudes": [INCERTITUDE_SERIE],
  "statut": "brouillon"
}

# ---------------------------------------------------------------------------
# EXERCICE 2 - Deuxieme partie : evaluation de l'agir competent (dissertation)
# ---------------------------------------------------------------------------

intro_ex2 = (
    "**Deuxième partie : l'évaluation de l'agir compétent (9 points)**\n\n"
    "**Essai personnel** : en te fondant sur ta culture philosophique et dans le respect des règles de la "
    "logique, est-il légitime de penser qu'autrui est une énigme ?\n\n"
    "**Consigne** : dans le respect de la structure d'une dissertation, rédige ton texte en deux pages au "
    "plus, en prenant en compte les tâches ci-après."
)

rappel_ex2_q1 = ("Dans une dissertation dialectique, la thèse défend honnêtement et rigoureusement une "
    "première réponse au sujet, en l'appuyant sur des arguments construits et des références philosophiques "
    "précises, sans anticiper les objections que l'antithèse viendra développer.")

corrige_ex2_q1 = (
"### Rappel de méthode\n"
f"{rappel_ex2_q1}\n\n"
"### Corrigé détaillé\n"
"**Introduction et problématisation.** Autrui désigne l'autre homme en tant que semblable à moi, un alter "
"ego, une conscience distincte de la mienne mais reconnue comme conscience. Une énigme désigne ce qui "
"résiste à l'élucidation complète, ce dont le sens échappe malgré l'effort pour le comprendre. La difficulté "
"tient à ceci : si autrui est mon semblable, je devrais pouvoir le comprendre par analogie avec moi-même ; "
"mais s'il est une conscience distincte de la mienne, son vécu intérieur exact m'est par définition "
"inaccessible, puisque je ne peux jamais occuper sa place pour vérifier ce qu'il ressent réellement. Le "
"langage, les gestes, le visage d'autrui me donnent l'impression d'un accès à sa conscience, alors que je "
"n'en perçois jamais que des signes extérieurs, jamais la conscience elle-même. Faut-il alors admettre "
"qu'autrui demeure, par nature, une énigme que je ne résoudrai jamais complètement ?\n\n"
"**Argument 1 : l'accès à la conscience d'autrui n'est jamais direct, mais seulement analogique.** Dans les "
"*Méditations cartésiennes* (1931, cinquième méditation), Husserl montre que je ne perçois jamais directement "
"la conscience d'autrui, mais seulement son corps et ses comportements, à partir desquels je lui « "
"appresente » (je lui attribue par analogie) une vie intérieure semblable à la mienne. Cette attribution "
"reste une inférence, jamais une perception directe : la subjectivité d'autrui, en tant que telle, ne m'est "
"jamais donnée « en original », contrairement à ma propre conscience. Autrui est donc structurellement une "
"énigme, puisque je ne peux accéder qu'à ses manifestations extérieures, jamais à son vécu lui-même.\n\n"
"**Argument 2 : le regard d'autrui m'échappe autant qu'il me saisit.** Dans *L'Être et le Néant* (1943), "
"Sartre analyse l'expérience du regard : lorsque autrui me regarde, je fais l'épreuve d'être devenu un objet "
"pour une liberté qui n'est pas la mienne, une liberté que je ne peux ni posséder ni totalement connaître. "
"Autrui, pour Sartre, est « le médiateur indispensable entre moi et moi-même », mais il demeure aussi ce "
"sujet insaisissable dont je ne perçois que les effets sur moi (la honte, la gêne) sans jamais pouvoir "
"occuper son point de vue. C'est ce qui rend, dans *Huis clos* (1944), la formule « l'enfer, c'est les "
"autres » si radicale : autrui me juge depuis un lieu que je ne maîtrise et ne connais jamais complètement.\n\n"
"**Argument 3 : le visage d'autrui résiste à toute totalisation.** Dans *Totalité et Infini* (1961), Levinas "
"soutient que le visage d'autrui échappe par principe à toute connaissance qui prétendrait l'enfermer dans "
"une catégorie ou un concept : autrui s'y présente comme une trace de l'infini, une transcendance que je ne "
"peux jamais réduire à ce que j'en sais ou j'en perçois. Autrui, chez Levinas, n'est justement pas un objet "
"de connaissance : il est, par essence, ce qui déborde toute connaissance, donc une énigme au sens le plus "
"fort du terme.\n\n"
"**Conclusion partielle.** Il est donc légitime de penser qu'autrui est une énigme : la phénoménologie, "
"l'existentialisme et la philosophie de l'altérité convergent pour montrer que la conscience d'autrui, à la "
"différence de son corps et de son comportement, ne m'est jamais donnée directement.\n\n"
"### Conseil\n"
"Mobilise au moins deux références distinctes appuyées sur des œuvres précises (ici Husserl, Sartre et "
"Levinas) plutôt qu'une seule intuition générale sur le mystère d'autrui : cela montre une véritable culture "
"philosophique et évite que la thèse ne repose sur une simple impression."
)

rappel_ex2_q2 = ("L'antithèse ne consiste pas à nier simplement la thèse, mais à en montrer les limites "
    "internes ou à lui opposer une position tout aussi argumentée, en s'appuyant si possible sur d'autres "
    "références philosophiques que celles mobilisées dans la thèse.")

corrige_ex2_q2 = (
"### Rappel de méthode\n"
f"{rappel_ex2_q2}\n\n"
"### Corrigé détaillé\n"
"**Argument 1 : la perception d'autrui est immédiate, non déduite par analogie.** Dans la *Phénoménologie de "
"la perception* (1945), Merleau-Ponty conteste l'idée d'un accès seulement inférentiel à autrui : le corps "
"d'autrui n'est pas un simple signe extérieur à partir duquel je devrais reconstruire par le raisonnement une "
"conscience cachée, il est d'emblée perçu comme expressif, comme habité par une intention et un sens. "
"Merleau-Ponty parle d'« intercorporéité » pour désigner cette communication immédiate entre les corps, "
"antérieure à toute inférence analogique. Si la perception d'autrui est déjà une perception de sens, "
"l'énigme supposée par Husserl et Sartre est moins radicale qu'elle n'y paraît.\n\n"
"**Argument 2 : la reconnaissance mutuelle permet de sortir de la solitude des consciences.** Dans la "
"*Phénoménologie de l'esprit* (1807), Hegel décrit, dans la dialectique du maître et de l'esclave, comment "
"deux consciences en viennent, à travers une lutte pour la reconnaissance, à se comprendre et à s'accorder "
"une existence réciproque. Ce processus montre qu'autrui n'est pas condamné à demeurer un pur mystère "
"extérieur à moi : c'est précisément par l'épreuve commune de la reconnaissance que deux consciences "
"distinctes parviennent à se rejoindre et à se savoir mutuellement.\n\n"
"**Argument 3 : la vie sociale suppose une compréhension pratique suffisante d'autrui.** Le langage, la "
"coopération, l'amitié, l'amour supposent tous une compréhension d'autrui suffisamment fiable pour agir "
"ensemble. Si autrui était une énigme totale et insurmontable, aucune vie commune, aucune promesse, aucun "
"projet partagé ne serait possible. Or ces réalités existent et fonctionnent quotidiennement, ce qui limite "
"fortement la portée d'un scepticisme radical sur la connaissance d'autrui.\n\n"
"**Conclusion partielle.** La thèse d'une énigme radicale d'autrui se heurte donc à l'évidence de la "
"communication corporelle immédiate, au processus de reconnaissance mutuelle et à la réussite ordinaire de la "
"vie en commun : autrui échappe peut-être à une connaissance absolue, mais pas à une compréhension pratique "
"suffisante pour vivre avec lui.\n\n"
"### Piège à éviter\n"
"Ne te contente pas d'affirmer que « l'énigme est exagérée » : appuie l'antithèse sur une doctrine "
"concurrente clairement identifiée (ici Merleau-Ponty et Hegel), sinon elle n'aura pas la même force "
"argumentative que la thèse."
)

rappel_ex2_q3 = ("Réussir une synthèse suppose de ne pas se contenter de juxtaposer thèse et antithèse, ni de "
    "trancher arbitrairement en faveur de l'une, mais de reformuler le problème à un niveau supérieur, "
    "généralement en distinguant des sens ou des degrés différents dans les termes du sujet.")

corrige_ex2_q3 = (
"### Rappel de méthode\n"
f"{rappel_ex2_q3}\n\n"
"### Corrigé détaillé\n"
"**Dépassement de l'opposition.** La contradiction entre la thèse et l'antithèse s'atténue si l'on distingue "
"deux niveaux dans la relation à autrui : une **connaissance pratique et fonctionnelle** d'autrui (suffisante "
"pour communiquer, coopérer, vivre en société, comme le montrent Merleau-Ponty et Hegel) et une "
"**connaissance absolue de sa subjectivité** (son vécu intérieur exact, tel qu'il l'éprouve lui-même, qui "
"demeure hors de portée, comme le montrent Husserl et Sartre). L'antithèse a raison au premier niveau, la "
"thèse a raison au second.\n\n"
"**Formulation de la position dépassée.** On peut alors affirmer qu'autrui est une énigme non pas au sens "
"d'un défaut de connaissance à combler, mais au sens d'une transcendance à respecter. C'est précisément la "
"lecture que propose Levinas : le visage d'autrui échappe à ma prise non parce que je manquerais d'outils "
"pour le connaître, mais parce que sa dignité de sujet libre exige justement qu'il ne soit jamais réductible "
"à ce que j'en sais. L'énigme d'autrui n'est donc pas un obstacle à surmonter, elle est la condition même du "
"respect que je lui dois : si je pouvais connaître autrui totalement, comme un objet, j'en ferais une chose "
"que je pourrais entièrement posséder ou manipuler, ce qui nierait précisément sa liberté de sujet.\n\n"
"**Conclusion générale.** Il est donc légitime de penser qu'autrui est une énigme, à condition de comprendre "
"cette énigme non comme un échec de la connaissance qui interdirait toute vie commune, mais comme la marque "
"d'une transcendance irréductible qui rend cette vie commune éthiquement exigeante : je peux comprendre "
"autrui assez pour agir avec lui, sans jamais l'épuiser dans ce que j'en sais, et c'est cette part "
"irréductible qui fonde mon respect pour lui.\n\n"
"### Conseil\n"
"Une synthèse réussie s'appuie sur une distinction conceptuelle précise, ici entre connaissance pratique et "
"connaissance absolue, plutôt que sur une formule vague de compromis du type « il y a du vrai des deux côtés "
"» : c'est cette distinction qui rend la synthèse philosophiquement rigoureuse et démontre une maîtrise "
"réelle de l'exercice dialectique."
)

rappel_ex2_q4 = ("Une dissertation bien notée n'est pas seulement celle qui contient de bons arguments : elle "
    "doit aussi présenter une architecture visible et lisible (introduction avec accroche et annonce du plan, "
    "paragraphes distincts pour chaque grande partie, transitions explicites entre thèse, antithèse et "
    "synthèse, conclusion qui répond clairement au sujet), et être présentée proprement.")

corrige_ex2_q4 = (
"### Rappel de méthode\n"
f"{rappel_ex2_q4}\n\n"
"### Corrigé détaillé\n"
"Pour obtenir les deux points de présentation, la copie doit satisfaire les deux critères suivants.\n\n"
"**1. Respect de la structure d'une dissertation (1 point).** L'introduction doit définir les concepts-clés "
"(autrui, énigme), poser le problème et annoncer le plan. Chaque partie (thèse, antithèse, synthèse) doit "
"constituer un moment clairement identifiable du développement, séparé par des transitions qui expliquent le "
"passage d'une partie à l'autre, par exemple « Cette position rencontre cependant des limites » entre la "
"thèse et l'antithèse. La conclusion doit répondre explicitement à la question posée en rappelant le chemin "
"argumentatif parcouru.\n\n"
"**2. Allure générale de la copie (1 point).** Une écriture lisible, une orthographe et une syntaxe soignées, "
"des paragraphes visuellement distincts, l'absence de ratures excessives, et le respect de la consigne de "
"longueur (deux pages au plus) contribuent à ce critère.\n\n"
"### Conseil\n"
"Saute une ligne entre l'introduction, la thèse, l'antithèse, la synthèse et la conclusion : cela aide le "
"correcteur à identifier immédiatement la structure respectée, et ces points de présentation se perdent "
"souvent par simple négligence de mise en page plutôt que par manque de contenu."
)

exercice2 = {
  "epreuve_source": EPREUVE_SOURCE,
  "numero_exercice": "2",
  "pays": "cm",
  "matiere": "Philosophie",
  "nature_epreuve": None,
  "serie": "C",
  "examen": "bac",
  "origine": "officiel",
  "etablissement": None,
  "annee": 2024,
  "duree_epreuve": "2h",
  "coefficient": "2",
  "points": 9,
  "figures": [],
  "enonce_intro_markdown": intro_ex2,
  "questions": [
    {
      "numero": "1",
      "enonce_markdown": "1ère tâche : la thèse (3 points). Montre qu'il est légitime de penser qu'autrui est une énigme.",
      "corrige_markdown": corrige_ex2_q1,
      "themes": ["autrui", "énigme", "Husserl", "Sartre", "Levinas", "intersubjectivité"],
      "difficulte_estimee": "élevée",
      "type_reponse": "ouverte",
      "choix": [],
      "reponse_correcte": "",
      "rappels_de_methode": [
        {
          "id": "rdm-bac-c-d-e-ti-philo-2024-cameroun-ex2-q1-0",
          "competence": "Construire une thèse argumentée dans une dissertation philosophique",
          "contenu_markdown": rappel_ex2_q1,
          "cours_genere": False,
          "cours_id": None
        }
      ]
    },
    {
      "numero": "2",
      "enonce_markdown": "2ème tâche : l'antithèse (3 points). Montre les limites de cette thèse.",
      "corrige_markdown": corrige_ex2_q2,
      "themes": ["autrui", "Merleau-Ponty", "Hegel", "reconnaissance", "intercorporéité"],
      "difficulte_estimee": "élevée",
      "type_reponse": "ouverte",
      "choix": [],
      "reponse_correcte": "",
      "rappels_de_methode": [
        {
          "id": "rdm-bac-c-d-e-ti-philo-2024-cameroun-ex2-q2-0",
          "competence": "Construire une antithèse argumentée qui dépasse la simple négation",
          "contenu_markdown": rappel_ex2_q2,
          "cours_genere": False,
          "cours_id": None
        }
      ]
    },
    {
      "numero": "3",
      "enonce_markdown": "3ème tâche : la synthèse (3 points). Dépasse la contradiction entre la thèse et l'antithèse.",
      "corrige_markdown": corrige_ex2_q3,
      "themes": ["autrui", "Levinas", "synthèse dialectique", "transcendance"],
      "difficulte_estimee": "élevée",
      "type_reponse": "ouverte",
      "choix": [],
      "reponse_correcte": "",
      "rappels_de_methode": [
        {
          "id": "rdm-bac-c-d-e-ti-philo-2024-cameroun-ex2-q3-0",
          "competence": "Construire une véritable synthèse dialectique, pas un simple compromis",
          "contenu_markdown": rappel_ex2_q3,
          "cours_genere": False,
          "cours_id": None
        }
      ]
    },
    {
      "numero": "4",
      "enonce_markdown": "Présentation (2 points) : respect de la structure d'une dissertation (1 point) et allure générale de la copie (1 point).",
      "corrige_markdown": corrige_ex2_q4,
      "themes": ["méthodologie de la dissertation", "présentation formelle"],
      "difficulte_estimee": "faible",
      "type_reponse": "ouverte",
      "choix": [],
      "reponse_correcte": "",
      "rappels_de_methode": [
        {
          "id": "rdm-bac-c-d-e-ti-philo-2024-cameroun-ex2-q4-0",
          "competence": "Soigner la présentation formelle d'une copie de dissertation",
          "contenu_markdown": rappel_ex2_q4,
          "cours_genere": False,
          "cours_id": None
        }
      ]
    }
  ],
  "mots_cles_recherche": ["autrui", "énigme", "intersubjectivité", "Sartre", "Levinas", "Husserl", "Hegel", "Merleau-Ponty", "dissertation philosophique"],
  "incertitudes": [INCERTITUDE_SERIE],
  "statut": "brouillon"
}

# ---------------------------------------------------------------------------
# Verification de fidelite (rappel contenu_markdown doit etre substring du corrige_markdown)
# ---------------------------------------------------------------------------
errors = []
for ex in (exercice1, exercice2):
    for q in ex["questions"]:
        for r in q["rappels_de_methode"]:
            if r["contenu_markdown"] not in q["corrige_markdown"]:
                errors.append((ex["numero_exercice"], q["numero"], r["id"]))

if errors:
    print("ERREURS DE FIDELITE:", errors)
else:
    print("OK: tous les rappels de methode sont verifies mot pour mot dans leur corrige_markdown.")

with open(os.path.join(OUT, "bac-c-d-e-ti-philo-2024-cameroun_exercice_1.json"), "w", encoding="utf-8") as f:
    json.dump(exercice1, f, ensure_ascii=False, indent=2)

with open(os.path.join(OUT, "bac-c-d-e-ti-philo-2024-cameroun_exercice_2.json"), "w", encoding="utf-8") as f:
    json.dump(exercice2, f, ensure_ascii=False, indent=2)

print("Exercices ecrits.")

# ---------------------------------------------------------------------------
# COURS EN LOT - toutes les competences correspondent a un titre deja
# existant dans le catalogue philo Cameroun (bac-c-d-e-ti-philo-2025-cameroun /
# bac-d-philo-2024-cameroun) -> squelettes minimaux uniquement.
# ---------------------------------------------------------------------------

CATALOGUE_TITRES = {
    "Définir rigoureusement des concepts philosophiques dans leur contexte",
    "Distinguer thème et problème philosophique d'un texte",
    "Dégager la thèse d'un auteur dans un texte philosophique",
    "Analyser la structure logique d'un texte argumentatif (postulat, arguments, conclusion)",
    "Construire une thèse argumentée dans une dissertation philosophique",
    "Construire une antithèse argumentée qui dépasse la simple négation",
    "Construire une véritable synthèse dialectique, pas un simple compromis",
    "Soigner la présentation formelle d'une copie de dissertation",
}

rappel_refs = []
for ex in (exercice1, exercice2):
    for q in ex["questions"]:
        for r in q["rappels_de_methode"]:
            rappel_refs.append({
                "exercice_numero": ex["numero_exercice"],
                "question_numero": q["numero"],
                "rappel_id": r["id"],
                "competence": r["competence"],
            })

epreuve_titre = "Baccalauréat ESG - Épreuve de Philosophie - Séries C-D-E-TI - Session 2024"

cours_files = []
for ref in rappel_refs:
    titre = ref["competence"]
    assert titre in CATALOGUE_TITRES, f"Competence sans correspondance catalogue: {titre}"
    slug = slugify(titre)
    cours_id = f"cours-{slug}-terminale"
    cours = {
        "cours_id": cours_id,
        "meta": {
            "titre": titre,
            "matiere": "Philosophie",
            "pays": "cm",
            "serie": None,
            "sous_theme": None,
            "duree_estimee_min": None,
            "tags": [],
            "statut": "brouillon"
        },
        "source": {
            "epreuve_id": EPREUVE_ID,
            "epreuve_titre": epreuve_titre,
            "exercice_numero": ref["exercice_numero"],
            "rappel_id": ref["rappel_id"],
            "rappels_lies": [],
            "correction_id": None
        },
        "sections": []
    }
    fname = f"bac-c-d-e-ti-philo-2024-cameroun_cours_{slug}.json"
    path = os.path.join(OUT, fname)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cours, f, ensure_ascii=False, indent=2)
    cours_files.append(fname)

print("Cours (squelettes, titres deja au catalogue) ecrits:")
for c in cours_files:
    print(" -", c)
