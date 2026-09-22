# -*- coding: utf-8 -*-
import json, os

OUT = "/sessions/gifted-confident-heisenberg/mnt/Epreuves/json/cm/epreuve-zero-bac-philo-c-d-e-ti-2020-cameroun"
SRC = "epreuve-zero-bac-philo-c-d-e-ti-2020-cameroun.pdf"

def base_exercice(numero):
    return {
        "epreuve_source": SRC,
        "numero_exercice": numero,
        "pays": "cm",
        "matiere": "Philosophie",
        "nature_epreuve": None,
        "partie_epreuve_francais": None,
        "variante_sujet": None,
        "serie": "C, D, E, TI",
        "filiere_serie_a": None,
        "examen": "bac",
        "origine": "sujet zero",
        "etablissement": None,
        "institution": None,
        "annee": 2020,
        "duree_epreuve": None,
        "coefficient": None,
        "introduction_markdown": None,
        "points": None,
        "groupes": [],
        "figures": [],
    }

# ---------------------------------------------------------------------------
# EXERCICE 1 - Sujet I (dissertation) : "L'inconscient prive-t-il l'homme de sa liberte ?"
# ---------------------------------------------------------------------------

rappel1 = ("Face a une question fermee qui semble appeler une reponse par oui ou par non, "
"la dissertation philosophique ne doit jamais trancher d'emblee : il faut d'abord definir "
"avec precision chacun des termes du sujet, degager la tension qu'ils recelent l'un envers "
"l'autre, puis construire un plan dialectique en trois temps, une these qui accorde une "
"validite reelle a l'une des reponses possibles, une antithese qui lui oppose une objection "
"tout aussi fondee, et une synthese qui depasse l'opposition plutot que de se contenter d'un "
"compromis entre les deux.")

corps1 = (
"Un acte manque, un lapsus, un reve dont le sens echappe a celui qui le fait : la psychanalyse "
"freudienne a bouleverse, au tournant du vingtieme siecle, l'image que l'homme se faisait de "
"lui-meme comme sujet transparent a sa propre conscience. L'inconscient designe cette instance "
"psychique faite de desirs refoules, de pulsions et de representations qui echappent a la "
"conscience du sujet tout en continuant d'agir sur ses pensees, ses paroles et ses actes. La "
"liberte, elle, designe la capacite de se determiner soi-meme, d'agir en connaissance de cause "
"selon sa propre volonte raisonnee plutot que sous l'effet d'une contrainte exterieure ou d'une "
"determination qu'on ignore. Si des forces qui echappent a ma conscience gouvernent une part de "
"ce que je pense, dis et fais, comment puis-je encore me pretendre l'auteur veritable de mes "
"actes ? Mais si la psychanalyse propose precisement de porter au jour ces determinations "
"inconscientes, ne fournit-elle pas du meme coup les moyens d'une liberte reconquise, plus haute "
"que la liberte naive de celui qui s'ignore ? Nous montrerons d'abord que l'inconscient, tel que "
"le decrit Freud, prive effectivement l'homme de la maitrise qu'il croit avoir sur lui-meme, "
"avant d'examiner la these sartrienne selon laquelle la conscience demeure malgre tout "
"integralement libre, pour comprendre enfin que la liberte humaine se joue precisement dans le "
"travail de reconnaissance de ses propres determinations.\n\n"
"**I. L'inconscient prive l'homme de sa liberte**\n\n"
"Freud, dans l'Introduction a la psychanalyse, affirme que le moi n'est pas maitre dans sa "
"propre maison : la conscience ne percoit qu'une fraction infime de la vie psychique, le reste "
"demeurant gouverne par des representations refoulees, inaccessibles a l'introspection directe "
"mais actives dans les reves, les lapsus et les symptomes nevrotiques. Un lapsus n'est jamais un "
"simple accident de langage : il trahit un desir que le sujet ne s'avoue pas et qui s'impose a "
"lui malgre sa volonte consciente. Si les motifs reels de mes actes echappent ainsi a ma "
"conscience, alors le sentiment que j'ai de choisir librement n'est qu'une illusion "
"retrospective : je crois vouloir ce que je fais, alors que je suis en realite agi par des "
"causes que j'ignore. Spinoza, dans une lettre celebre a Schuller reprise dans l'Ethique, "
"formule cette meme idee sous une forme radicale : les hommes se trompent lorsqu'ils se croient "
"libres, pour la seule raison qu'ils sont conscients de leurs desirs mais ignorants des causes "
"qui les determinent. Ainsi concu, le sentiment de liberte n'est que le decalage entre la "
"conscience de l'effet, le desir ressenti, et l'ignorance de la cause, la pulsion inconsciente "
"qui le produit.\n\n"
"**II. La conscience demeure libre malgre l'inconscient**\n\n"
"Cette these ne va cependant pas sans difficulte. Sartre, dans L'Etre et le Neant, conteste "
"precisement la possibilite meme d'un inconscient au sens freudien : comment un psychisme "
"pourrait-il a la fois savoir, pour refouler un contenu qu'il juge inacceptable, et ne pas "
"savoir, puisque ce contenu lui est par definition inconscient ? Pour Sartre, la conscience est "
"toujours transparente a elle-meme : ce que Freud appelle refoulement est en realite un projet "
"de mauvaise foi, une maniere dont je me mens a moi-meme sur mes propres motifs tout en les "
"connaissant confusement. L'homme, selon la formule sartrienne, est condamne a etre libre : "
"meme le rapport que j'entretiens avec mes desirs les plus obscurs demeure un choix, puisque "
"c'est moi qui decide de m'en detourner ou de les assumer. Freud lui-meme n'a d'ailleurs jamais "
"fait de la psychanalyse une doctrine de resignation : le but de la cure est precisement de "
"transformer l'inconscient en conscient, selon la formule allemande Wo Es war, soll Ich werden, "
"la ou etait le Ca, le Moi doit advenir. Si l'analyse peut elargir le champ de la conscience et "
"donner au moi une prise sur ce qui le determinait a son insu, alors l'inconscient n'abolit pas "
"la liberte, il ne fait que reveler qu'elle n'est jamais donnee d'emblee.\n\n"
"**III. Une liberte a conquerir contre les determinations inconscientes**\n\n"
"Les deux positions precedentes ne s'opposent en realite que si l'on confond deux sens du mot "
"liberte. Si l'on entend par liberte l'absence totale de toute determination, une spontaneite "
"pure et sans cause, alors l'inconscient la rend effectivement impossible, et Spinoza a raison "
"de denoncer cette liberte comme une illusion. Mais si l'on entend par liberte, avec Kant dans "
"la Critique de la raison pratique, la capacite de se determiner selon la raison plutot que "
"selon les seules inclinations naturelles, alors rien n'empeche que cette determination "
"rationnelle s'exerce precisement contre les poussees de l'inconscient, a condition de les "
"avoir d'abord reconnues. C'est tout le sens du travail analytique : il ne supprime pas "
"l'inconscient, mais il transforme le rapport du sujet a ses propres determinations, faisant "
"d'une contrainte subie un donne avec lequel composer consciemment. La liberte humaine n'est "
"alors ni la maitrise immediate que s'attribue le sujet naif, ni la pure fiction que denonce le "
"determinisme, mais une conquete progressive, toujours a recommencer, contre ce qui en nous agit "
"sans notre su.\n\n"
"**Conclusion**\n\n"
"L'inconscient ne prive donc pas l'homme de sa liberte de facon absolue et definitive : il "
"ruine seulement l'illusion d'une liberte immediate et transparente a elle-meme, celle du sujet "
"qui se croit spontanement maitre de ses choix. Il ouvre en revanche la voie a une liberte plus "
"exigeante, gagnee par le travail de connaissance de soi, dont la psychanalyse offre un "
"instrument privilegie mais non exclusif. Cette conclusion invite a s'interroger sur les "
"limites de cette connaissance de soi : peut-on jamais rendre pleinement conscientes toutes les "
"determinations qui nous traversent, et la responsabilite morale ou juridique d'un acte commis "
"sous l'influence de mobiles inconscients peut-elle etre pleinement engagee ?"
)

piege1 = ("Ne reduis pas ce sujet a un simple resume de la theorie freudienne de l'inconscient : "
"la question porte sur la liberte, pas sur l'inconscient en lui-meme, et chaque partie doit "
"revenir explicitement a ce que cela change pour la possibilite d'agir librement.")

conseil1 = ("Appuie-toi sur un exemple precis de lapsus ou d'acte manque pour rendre concrete la "
"these freudienne avant de la discuter : un correcteur valorise toujours une notion abstraite "
"illustree par un cas clair, plutot qu'une discussion qui reste entierement dans la generalite.")

corrige1 = ("### Rappel de methode\n" + rappel1 + "\n\n" + corps1 +
            "\n\n### Piege a eviter\n" + piege1 + "\n\n### Conseil\n" + conseil1)

ex1 = base_exercice("1")
ex1["introduction_markdown"] = "NB : le candidat traitera l'un des sujets au choix."
ex1["enonce_intro_markdown"] = "**Sujet I**"
ex1["questions"] = [{
    "numero": "1",
    "enonce_markdown": "L'inconscient prive-t-il l'homme de sa liberte ?",
    "corrige_markdown": corrige1,
    "themes": ["inconscient", "liberte", "psychanalyse", "Freud", "determinisme"],
    "savoir_officiel": {"classe": "Tle", "serie_label": "C-D-E-TI", "module_numero": "1", "savoir_numero": "IV"},
    "difficulte_estimee": "élevée",
    "type_reponse": "ouverte",
    "choix": [],
    "reponse_correcte": None,
    "rappels_de_methode": [{
        "id": "rdm-epreuve-zero-bac-philo-c-d-e-ti-2020-cameroun-ex1-q1-0",
        "competence": "Construire un plan dialectique sur une question fermee",
        "contenu_markdown": rappel1,
        "cours_genere": False,
        "cours_id": None
    }]
}]
ex1["mots_cles_recherche"] = ["inconscient", "liberte", "Freud", "Spinoza", "Sartre", "Kant", "psychanalyse", "dissertation"]
ex1["incertitudes"] = [
    "Le PDF source contient de nombreuses erreurs de saisie/OCR (« ct » pour « et », « cc » pour « ce », « dc » pour « de », « tes » pour « les », etc.) ; ces erreurs n'affectent pas les intitules des sujets de dissertation (Sujet I et Sujet II), lisibles sans ambiguite dans le texte source.",
    "Aucune duree d'epreuve ni coefficient n'est indique sur ce sujet zero (specimen sans bareme ni bandeau ministeriel visible) : les deux champs sont laisses a null.",
    "savoir_officiel du Sujet I (savoir IV, 'La Conscience et l'Inconscient') est un rattachement raisonne : le sujet mobilise egalement la notion de liberte (savoir VIII), mais le concept central introduit par l'enonce est l'inconscient, ce qui justifie le choix du savoir IV plutot que VIII."
]
ex1["statut"] = "brouillon"

# ---------------------------------------------------------------------------
# EXERCICE 2 - Sujet II (dissertation) : citation de Max Stirner
# ---------------------------------------------------------------------------

rappel2 = ("Discuter une citation d'auteur consiste a en degager d'abord le sens precis et la "
"these qu'elle defend, puis a examiner successivement dans quelle mesure elle est fondee et "
"dans quelle mesure elle peut etre contestee, avant de proposer une position personnelle "
"argumentee qui ne se contente ni d'approuver ni de rejeter l'affirmation en bloc, mais qui en "
"precise les limites et les conditions de validite.")

corps2 = (
"Dans l'histoire comme dans l'actualite, les puissances victorieuses ont souvent presente leur "
"domination comme legitime du seul fait qu'elles l'avaient emporte par la force. Cette idee "
"trouve une formulation radicale chez Max Stirner, penseur allemand de L'Unique et sa propriete "
"(1844), pour qui tout droit pretendument superieur a l'individu, droit naturel, morale, Etat, "
"n'est qu'un spectre destine a l'aliener, si bien que seule sa force effective fonde ce qu'il "
"peut legitimement s'approprier. La force designe ici la puissance physique ou coercitive "
"capable d'imposer sa volonte malgre une resistance ; le droit designe un ensemble de regles "
"reconnues comme legitimes, qui obligent moralement et pas seulement par la contrainte. Si le "
"droit se reduit ainsi purement et simplement a un rapport de force, alors la notion meme de "
"justice perd tout contenu propre, puisque toute domination deviendrait juste du seul fait "
"qu'elle est victorieuse. Mais une societe peut-elle vraiment se passer d'une legitimite "
"independante du rapport de force, sous peine de ne plus pouvoir distinguer le vainqueur "
"legitime du simple oppresseur ? Nous examinerons d'abord en quel sens la force a effectivement "
"pu fonder historiquement le droit, avant de montrer que le droit veritable s'oppose au "
"contraire par nature a la seule force, pour comprendre enfin que la force n'est legitimement "
"qu'un instrument au service d'un droit dont le fondement est ailleurs.\n\n"
"**I. La force fonde effectivement le droit**\n\n"
"Hobbes, dans le Leviathan, decrit l'etat de nature comme un etat de guerre de tous contre "
"tous, dans lequel chacun dispose d'un droit sur toute chose a la mesure exacte de sa force et "
"de son habilete a se l'approprier : le droit naturel s'y confond entierement avec le pouvoir "
"effectif de chaque individu de se conserver. Spinoza reprend une idee voisine dans le Traite "
"theologico-politique lorsqu'il pose que le droit naturel de chaque etre s'etend aussi loin que "
"s'etend sa puissance, de sorte que le poisson a naturellement droit de nager et le grand "
"poisson droit de devorer le petit. Stirner radicalise cette intuition en la retournant contre "
"toute forme de contrat ou d'Etat : si le droit n'est jamais que la puissance de chacun, alors "
"le contrat social lui-meme, en pretendant fonder un droit commun superieur aux individus, "
"n'est qu'une fiction alienante de plus, un spectre auquel l'Unique n'a aucune raison de se "
"soumettre au-dela de ce que sa propre force lui impose. En ce sens, l'affirmation de Stirner "
"ne fait que tirer la consequence ultime d'une longue tradition qui, de Hobbes a Spinoza, "
"identifie le droit originaire a la puissance.\n\n"
"**II. Le droit s'oppose par nature a la seule force**\n\n"
"Rousseau conteste pourtant frontalement cette identification dans un chapitre celebre du "
"Contrat social intitule Du droit du plus fort. Il y montre que cette expression est proprement "
"contradictoire : la force est une puissance physique, et l'on ne voit pas quelle moralite peut "
"resulter de ses effets ; ceder a la force est un acte de necessite, non de volonte, tout au "
"plus un acte de prudence ; en quel sens cela pourrait-il etre un devoir ? Si la force cesse des "
"qu'une force superieure survient, alors ce pretendu droit change de main a chaque changement de "
"rapport de force, ce qui prouve precisement qu'il n'etait pas un droit veritable, puisque le "
"droit veritable oblige independamment des circonstances. Rousseau en conclut que la force ne "
"fait point le droit, et qu'on n'est oblige d'obeir qu'aux puissances legitimes. Pascal, dans "
"les Pensees, formule un constat proche lorsqu'il observe que la justice sans la force est "
"impuissante et que la force sans la justice est tyrannique : n'ayant pu faire que ce qui est "
"juste soit fort, les hommes ont fait que ce qui est fort soit dit juste, ce qui n'est pas "
"confondre les deux mais denoncer une usurpation de langage. Le droit du plus fort n'est donc "
"pas un droit, mais l'habillage moral d'une simple domination de fait.\n\n"
"**III. La force, instrument necessaire d'un droit dont la legitimite vient d'ailleurs**\n\n"
"Ces deux positions se rejoignent si l'on distingue la question de l'effectivite du droit de "
"celle de sa legitimite. Kant, dans la Doctrine du droit, definit le droit comme la faculte de "
"contraindre legitimement quiconque porterait atteinte a la liberte d'autrui selon une loi "
"universelle : la coercition, c'est-a-dire une forme de force, y demeure necessaire pour que le "
"droit ne reste pas un voeu pieux dans une societe d'etres libres et parfois malveillants, mais "
"elle n'en constitue jamais le fondement, seulement le moyen de son application effective. Ce "
"que Stirner appelle droit du plus fort n'est donc, en toute rigueur, qu'un pouvoir de fait, non "
"un droit au sens normatif du terme, puisqu'il ne pretend obliger personne en conscience, il ne "
"fait que contraindre. Sa critique garde cependant une part de verite qu'il ne faut pas balayer "
": elle a le merite de denoncer les pretendus droits naturels ou etatiques qui ne sont en "
"realite que des rapports de domination deguises sous le langage de la legitimite, un spectre "
"servant a obtenir une soumission que la seule force n'aurait pas suffi a obtenir. Le droit "
"veritable articule ainsi deux exigences : une force suffisante pour se faire respecter, et une "
"legitimite rationnelle ou collectivement reconnue qui seule peut fonder l'obligation morale d'y "
"obeir.\n\n"
"**Conclusion**\n\n"
"L'affirmation de Stirner contient donc une part de verite genealogique, la force a bien souvent "
"precede et permis l'instauration historique des droits, mais elle echoue comme definition du "
"droit veritable, qui suppose une legitimite que la seule victoire du plus fort ne peut jamais "
"produire. Cette question demeure d'une actualite pressante : dans les relations internationales "
"contemporaines, ou aucune puissance coercitive superieure aux Etats n'existe veritablement, la "
"primaute du droit international sur les seuls rapports de force reste un ideal fragile, sans "
"cesse menace par la tentation de confondre, comme le fait Stirner, ce qui est puissant avec ce "
"qui est juste."
)

piege2 = ("Ne te contente pas d'affirmer que Stirner a tort parce que la force ne devrait pas "
"commander : le sujet demande d'abord de comprendre pourquoi cette these a pu sembler fondee "
"historiquement, avant de la refuter avec l'argument precis de Rousseau sur la contradiction "
"interne de l'expression droit du plus fort.")

conseil2 = ("Cite la formule de Rousseau presque mot pour mot, ou est le devoir : quand un "
"correcteur lit un argument aussi celebre restitue avec precision plutot que vaguement "
"paraphrase, il reconnait immediatement une copie qui maitrise ses references.")

corrige2 = ("### Rappel de methode\n" + rappel2 + "\n\n" + corps2 +
            "\n\n### Piege a eviter\n" + piege2 + "\n\n### Conseil\n" + conseil2)

ex2 = base_exercice("2")
ex2["enonce_intro_markdown"] = "**Sujet II**"
ex2["questions"] = [{
    "numero": "1",
    "enonce_markdown": "Que pensez-vous de cette affirmation de Max Stirner : « Celui qui a la force a le droit » ?",
    "corrige_markdown": corrige2,
    "themes": ["droit", "force", "justice", "Stirner", "contrat social"],
    "savoir_officiel": {"classe": "Tle", "serie_label": "C-D-E-TI", "module_numero": "1", "savoir_numero": "VI"},
    "difficulte_estimee": "élevée",
    "type_reponse": "ouverte",
    "choix": [],
    "reponse_correcte": None,
    "rappels_de_methode": [{
        "id": "rdm-epreuve-zero-bac-philo-c-d-e-ti-2020-cameroun-ex2-q1-0",
        "competence": "Discuter une citation d'auteur en dissertation philosophique",
        "contenu_markdown": rappel2,
        "cours_genere": False,
        "cours_id": None
    }]
}]
ex2["mots_cles_recherche"] = ["droit", "force", "justice", "Max Stirner", "Rousseau", "Hobbes", "Pascal", "Kant", "dissertation"]
ex2["incertitudes"] = [
    "Aucune duree d'epreuve ni coefficient n'est indique sur ce sujet zero : les deux champs sont laisses a null.",
    "savoir_officiel VI ('Le Droit et la Justice') retenu car le sujet porte explicitement sur le fondement du droit par la force, theme classique de ce savoir (Rousseau, 'Du droit du plus fort')."
]
ex2["statut"] = "brouillon"

with open(os.path.join(OUT, "epreuve-zero-bac-philo-c-d-e-ti-2020-cameroun_exercice_1.json"), "w", encoding="utf-8") as f:
    json.dump(ex1, f, ensure_ascii=False, indent=2)
with open(os.path.join(OUT, "epreuve-zero-bac-philo-c-d-e-ti-2020-cameroun_exercice_2.json"), "w", encoding="utf-8") as f:
    json.dump(ex2, f, ensure_ascii=False, indent=2)

print("ex1 words:", len(corps1.split()))
print("ex2 words:", len(corps2.split()))
print("done part 1")
