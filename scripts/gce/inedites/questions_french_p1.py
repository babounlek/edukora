r"""Questions de l'epreuve inedite GCE O Level French Paper 1 n.1 (50 QCM). Voir generer_french_p1.py.

Structure copiee des 6 vrais Paper 1 (2020-2023, 2025, 2026 ; code du Board 0545 ; mesures le 2026-10-20) : 50 QCM de 1h30 dont 45 questions isolees (grammaire, conjugaison,
accords, pronoms, articles, vocabulaire, expressions, traduction de proverbes anglais, nombres) puis un texte a trous de 5 questions (46-50). Les phrases, les textes et les
noms sont ORIGINAUX (aucune phrase d'un vrai sujet).

Q(id, themes, difficulte, enonce, bonne option, [(distracteur, RAISON de l'erreur)] x3, rappel, resolution, conseil, phrase complete).
Chaque distracteur porte la raison pour laquelle il est faux : c'est le second passage de verification (« existe-t-il une deuxieme option acceptable ? ») ecrit noir sur blanc,
et c'est l'explication donnee a l'eleve. Toutes les chaines sont BRUTES (r"..."). Les explications sont en anglais (les eleves sont anglophones), les phrases en francais.
"""

PREFIXE = "O Level French - "
BL = r"\_\_\_\_\_\_"

# Texte a trous (questions 46-50) : les cinq trous sont repris, dans l'ordre, par COMPLET.
TEXTE = (
    r"**Text for questions 46 to 50**" "\n\n"
    r"*Read the text below. For each numbered space, choose the answer that completes the text correctly.*" "\n\n"
    r"Dans le village de Ngoumou, il n'y a qu'un seul puits. Chaque matin, les femmes se lèvent très tôt pour aller y " + BL + r" (46) de l'eau. "
    r"Le puits est situé loin des " + BL + r" (47) maisons du quartier et le chemin est long ; " + BL + r" (48) elles rentrent toujours fatiguées. "
    r"Selon le chef, un puits plus proche profiterait à " + BL + r" (49) les femmes du village, car celui " + BL + r" (50) elles utilisent aujourd'hui est devenu "
    r"trop petit pour tout le monde."
)
COMPLET = (
    "Dans le village de Ngoumou, il n'y a qu'un seul puits. Chaque matin, les femmes se lèvent très tôt pour aller y chercher de l'eau. "
    "Le puits est situé loin des premières maisons du quartier et le chemin est long ; c'est pourquoi elles rentrent toujours fatiguées. "
    "Selon le chef, un puits plus proche profiterait à toutes les femmes du village, car celui qu'elles utilisent aujourd'hui est devenu "
    "trop petit pour tout le monde."
)
REPONSES_TEXTE = ["chercher", "premières", "c'est pourquoi", "toutes", "qu'"]

RAPPELS = {
    "vocabulaire": r"For a vocabulary question, test each option in the sentence for meaning and for the words it normally keeps company with; options that look alike or sound alike but mean something else are the usual traps.",
    "connecteur": r"A linking word must fit the logic of the two ideas it joins: par conséquent gives a result, pourtant a contrast, parce que a cause that follows its clause, tandis que an opposition.",
    "imparfait": r"The imparfait describes a habit or a situation in the past; with quand j'étais petit or chaque dimanche it is the tense that expresses the repeated action.",
    "conditionnel": r"After si with the imparfait, the result clause takes the conditionnel présent; after si with the plus-que-parfait, it takes the conditionnel passé.",
    "subjonctif": r"Falloir que, bien que and vouloir que are followed by the subjonctif; learn the subjonctif forms of the common irregular verbs.",
    "concordance": r"When one past action happens while another is going on, the action in progress is in the imparfait and the interrupting action is in the passé composé.",
    "accord_cod": r"The past participle used with avoir agrees in gender and number with a direct object placed BEFORE the verb (que, les, combien de...), never with one placed after.",
    "accord_etre": r"With être, the past participle agrees with the subject; with avoir, it stays unchanged unless the direct object comes before the verb.",
    "accord_adj": r"An adjective agrees in gender and number with the noun it describes; with two singular nouns joined by et, it takes the plural.",
    "pluriel": r"A noun takes the plural mark -s (or -x) when it refers to several people or things; the article and the adjective change with it.",
    "conjugaison": r"A verb ending depends on the subject and the tense: learn the present of verbs in -ger (nous mangeons), the irregular present (vous dites, je connais) and the futur stem of voir (verr-).",
    "pronoms": r"The pronouns y and en replace a place or a quantity: y stands for à + a place or thing, en for de + a noun or for a quantity; lui replaces à + a person.",
    "pronoms_demonstratifs": r"Celui, celle, ceux and celles replace a noun already mentioned and agree with it; ce stays masculine and neutral and is not followed by de.",
    "relatifs": r"Que is the direct object, qui the subject, dont replaces a complement with de, and à qui replaces a complement with à when the antecedent is a person.",
    "articles_partitif": r"The partitif (du, de la, de l') names a quantity of something; after a negation or an expression of quantity such as beaucoup, it becomes de or d' alone.",
    "articles_instrument": r"After jouer, use à for a game or sport (jouer au football) and de for a musical instrument (jouer du piano).",
    "expressions": r"An idiom has a meaning of its own that cannot be read word for word; learn each expression with its meaning and the image behind it.",
    "prepositions": r"Many verbs keep one fixed preposition (penser à, parler de) and the preposition dans introduces a place with the idea of being inside it; learn the pairs.",
    "traduction": r"To translate a proverb, look for the French proverb with the same meaning rather than translating word for word; the literal version is the usual trap.",
    "nombres": r"Know the common fractions in numbers (un quart = 15 minutes, trois quarts = 45 minutes, la moitié = half) and write quatre-vingts with an s only when nothing follows it.",
    "negation": r"A negative word of two parts (ne ... rien, ne ... personne, ne ... jamais) is chosen by its meaning: rien for a thing, personne for a person, jamais for time.",
    "genre": r"The feminine of a masculine noun in -eur is often -rice (directeur, directrice) when the noun comes from a verb with a -teur ending.",
    "comparatif": r"The comparative of bon is meilleur (not plus bon) and the comparative of bien is mieux; the superlative uses le, la or les in front.",
    "texte_infinitif": r"After pour or after the verb aller, a second verb is in the infinitive; the infinitive ends in -er, -ir or -re, never in a conjugated form.",
    "texte_accord": r"An adjective, an ordinal number (premier, première) or tout agrees in gender and number with the noun it goes with, and the article before it shows the number.",
}


def Q(qid, theme, diff, stem, ok, bad, rappel, sol, conseil=None, complete=None, extra=None):
    assert len(bad) == 3 and all(len(b) == 2 and b[1] for b in bad), qid
    themes = [PREFIXE + theme] + [PREFIXE + t for t in (extra or [])]
    n = lambda t: t.replace(chr(92) + chr(34), chr(34)) if isinstance(t, str) else t  # un guillemet precede d'un antislash garde l'antislash en chaine brute
    return dict(id=qid, themes=themes, diff=diff, stem=n(stem), ok=n(ok), bad=[n(b[0]) for b in bad], raisons=[n(b[1]) for b in bad],
                rappel=RAPPELS[rappel], sol=n(sol), conseil=n(conseil), complete=n(complete))


def questions():
    q = []
    a = q.append

    # ------------------------------------------------------------------------------------------------ vocabulaire (6)
    a(Q("f01", "vocabulary", "faible",
        r"Le mécanicien a " + BL + r" la voiture avant de la rendre à son propriétaire.",
        r"réparé", [(r"répété", r"is the past participle of répéter, to repeat"), (r"réparti", r"is the past participle of répartir, to share out"), (r"repéré", r"is the past participle of repérer, to spot")],
        "vocabulaire",
        r"A mechanic repairs a car, and the verb réparer fits the sentence: Le mécanicien a réparé la voiture avant de la rendre à son propriétaire.",
        None, r"Le mécanicien a réparé la voiture avant de la rendre à son propriétaire."))
    a(Q("f02", "vocabulary", "faible",
        r"Pour traverser le fleuve, les voyageurs utilisent une " + BL + r".",
        r"pirogue", [(r"pirouette", r"is a spinning jump of a dancer, not a boat"), (r"pipette", r"is a small tube used in a laboratory"), (r"pierrade", r"is a cooking stone for grilling meat")],
        "vocabulaire",
        r"A pirogue is a narrow boat used on African rivers, which is what travellers use to cross a river.",
        None, r"Pour traverser le fleuve, les voyageurs utilisent une pirogue."))
    a(Q("f03", "vocabulary", "faible",
        r"Mon père travaille dans une banque ; il est " + BL + r".",
        r"banquier", [(r"bancaire", r"is an adjective (un compte bancaire) and cannot name a person"), (r"banquette", r"is a bench to sit on"), (r"banque", r"is the institution and not the person who works in it")],
        "vocabulaire",
        r"The noun that names a person who works in a bank is banquier: Mon père travaille dans une banque ; il est banquier.",
        None, r"Mon père travaille dans une banque ; il est banquier."))
    a(Q("f04", "vocabulary", "moyenne",
        r"Il a beaucoup plu cette nuit ; " + BL + r", la route de Bamenda est impraticable.",
        r"par conséquent", [(r"pourtant", r"introduces a contrast, but the rain explains the bad road"), (r"tandis que", r"opposes two facts and does not link a cause to its result"),
                            (r"parce que", r"introduces a cause and cannot follow a semicolon and open a main clause")],
        "connecteur",
        r"The road is impassable because of the rain: the second idea is the result of the first, and par conséquent introduces a result.",
        r"Ask yourself whether the second idea is a result, a cause or a contrast before you choose the linking word.",
        r"Il a beaucoup plu cette nuit ; par conséquent, la route de Bamenda est impraticable."))
    a(Q("f05", "vocabulary", "faible",
        r"Le médecin a prescrit des " + BL + r" pour soigner la toux de l'enfant.",
        r"médicaments", [(r"médecines", r"is used for branches of medicine (les médecines douces), not for what the doctor prescribes"), (r"médicales", r"is an adjective and needs a noun"), (r"médicins", r"is a spelling mistake: the profession is médecin")],
        "vocabulaire",
        r"A doctor prescribes médicaments (medicines) to cure a cough.",
        None, r"Le médecin a prescrit des médicaments pour soigner la toux de l'enfant."))
    a(Q("f06", "vocabulary", "moyenne",
        r"Le candidat a " + BL + r" à l'examen parce qu'il n'avait pas révisé.",
        r"échoué", [(r"réussi", r"is the opposite of what the sentence says"), (r"obtenu", r"cannot be followed by à l'examen in this sense"), (r"gagné", r"is used for a game or a prize, not for an examination")],
        "vocabulaire",
        r"The candidate did not revise, so he failed the examination: échouer à un examen means not to pass it.",
        None, r"Le candidat a échoué à l'examen parce qu'il n'avait pas révisé."))

    # ------------------------------------------------------------------------------------------------ temps et modes (6)
    a(Q("f07", "tenses and moods", "faible",
        r"Quand j'étais petit, nous " + BL + r" chaque dimanche au marché.",
        r"allions", [(r"irons", r"is the future and the sentence speaks of the past"), (r"allons", r"is the present and the sentence speaks of the past"), (r"irions", r"is the conditionnel and does not describe a habit")],
        "imparfait",
        r"Quand j'étais petit and chaque dimanche show a habit in the past, so the verb is in the imparfait: nous allions.",
        None, r"Quand j'étais petit, nous allions chaque dimanche au marché.", extra=["verb conjugation"]))
    a(Q("f08", "tenses and moods", "faible",
        r"Si tu étudiais davantage, tu " + BL + r" ton examen.",
        r"réussirais", [(r"réussiras", r"is the future, but si with the imparfait needs the conditionnel"), (r"réussissais", r"is the imparfait, and the result clause needs the conditionnel"),
                        (r"as réussi", r"is the passé composé and does not fit si with the imparfait")],
        "conditionnel",
        r"The pattern is si + imparfait in the condition and the conditionnel présent in the result: Si tu étudiais davantage, tu réussirais ton examen.",
        None, r"Si tu étudiais davantage, tu réussirais ton examen."))
    a(Q("f09", "tenses and moods", "moyenne",
        r"Il faut que vous " + BL + r" avant midi.",
        r"partiez", [(r"partez", r"is the present indicative, but il faut que needs the subjonctif"), (r"partirez", r"is the future, which cannot follow il faut que"), (r"partiriez", r"is the conditionnel, which cannot follow il faut que")],
        "subjonctif",
        r"Il faut que is followed by the subjonctif, and the subjonctif of partir with vous is partiez.",
        r"Replace vous by tu or il in your head: il faut que tu partes shows that the verb is in the subjonctif.",
        r"Il faut que vous partiez avant midi.", extra=["verb conjugation"]))
    a(Q("f10", "tenses and moods", "moyenne",
        r"Hier soir, pendant que je " + BL + r" mes devoirs, la lumière s'est éteinte.",
        r"faisais", [(r"ai fait", r"is the passé composé, but pendant que describes an action in progress"), (r"ferai", r"is the future and the sentence is in the past"), (r"fis", r"is the passé simple, which does not go with the passé composé s'est éteinte")],
        "concordance",
        r"The homework was in progress when the light went out: the action in progress is in the imparfait (je faisais) and the interruption is in the passé composé (s'est éteinte).",
        None, r"Hier soir, pendant que je faisais mes devoirs, la lumière s'est éteinte.", extra=["verb conjugation"]))
    a(Q("f11", "tenses and moods", "moyenne",
        r"Si j'avais su la vérité, je ne " + BL + r" pas venu.",
        r"serais", [(r"suis", r"is the present, but si with the plus-que-parfait needs the conditionnel passé"), (r"serai", r"is the future, which cannot follow si with the plus-que-parfait"),
                    (r"étais", r"is the imparfait, but the conditionnel passé is needed in the result")],
        "conditionnel",
        r"Si with the plus-que-parfait (j'avais su) is followed by the conditionnel passé, whose auxiliary is in the conditionnel: je ne serais pas venu.",
        None, r"Si j'avais su la vérité, je ne serais pas venu.", extra=["verb conjugation"]))
    a(Q("f12", "tenses and moods", "moyenne",
        r"Bien qu'il " + BL + r" très fatigué, il a continué à travailler.",
        r"soit", [(r"est", r"is the indicative, but bien que needs the subjonctif"), (r"sera", r"is the future, which cannot follow bien que"), (r"serait", r"is the conditionnel, which cannot follow bien que")],
        "subjonctif",
        r"Bien que is followed by the subjonctif, and the subjonctif présent of être with il is soit.",
        None, r"Bien qu'il soit très fatigué, il a continué à travailler.", extra=["verb conjugation"]))

    # ------------------------------------------------------------------------------------------------ accords (6)
    a(Q("f13", "agreement", "moyenne",
        r"Les fleurs que ma mère a " + BL + r" sont magnifiques.",
        r"plantées", [(r"planté", r"does not agree with les fleurs, the direct object placed before the verb"), (r"plantés", r"is masculine plural, but fleurs is feminine"), (r"plante", r"is a present form and a participle is needed after a")],
        "accord_cod",
        r"The direct object que stands for les fleurs, which is feminine plural and comes before a planté, so the participle agrees: plantées.",
        None, r"Les fleurs que ma mère a plantées sont magnifiques.", extra=["verb conjugation"]))
    a(Q("f14", "agreement", "faible",
        r"Ces garçons sont " + BL + r" de leurs résultats.",
        r"fiers", [(r"fier", r"is singular, but the subject ces garçons is plural"), (r"fière", r"is feminine singular"), (r"fières", r"is feminine plural, but garçons is masculine")],
        "accord_adj",
        r"The adjective agrees with the subject ces garçons, which is masculine plural: ils sont fiers.",
        None, r"Ces garçons sont fiers de leurs résultats.", extra=["gender and number"]))
    a(Q("f15", "agreement", "moyenne",
        r"Marie et Awa sont " + BL + r" au marché ce matin.",
        r"allées", [(r"allé", r"is masculine singular"), (r"allés", r"is masculine plural, but both names are feminine"), (r"allée", r"is feminine singular, but there are two subjects")],
        "accord_etre",
        r"Aller takes être, so the participle agrees with the subject Marie et Awa, which is feminine plural: allées.",
        None, r"Marie et Awa sont allées au marché ce matin.", extra=["verb conjugation"]))
    a(Q("f16", "agreement", "faible",
        r"Tous les " + BL + r" du village ont participé à la fête.",
        r"habitants", [(r"habitant", r"is singular, but tous les needs a plural noun"), (r"habitante", r"is feminine singular"), (r"habitantes", r"is feminine, but tous les goes with a masculine plural noun")],
        "pluriel",
        r"Tous les is followed by a plural noun, and the plural of habitant is habitants: Tous les habitants du village ont participé à la fête.",
        None, r"Tous les habitants du village ont participé à la fête.", extra=["gender and number"]))
    a(Q("f17", "agreement", "faible",
        r"La mer et la plage sont " + BL + r" ce matin.",
        r"calmes", [(r"calme", r"is singular, but there are two subjects"), (r"calmement", r"is an adverb and cannot describe the subjects after sont"), (r"calmer", r"is an infinitive and cannot follow sont here")],
        "accord_adj",
        r"Two feminine nouns joined by et call for a plural adjective, and calme takes an s: calmes.",
        None, r"La mer et la plage sont calmes ce matin.", extra=["gender and number"]))
    a(Q("f18", "agreement", "elevee",
        r"Combien de livres as-tu " + BL + r" cette année ?",
        r"lus", [(r"lu", r"stays invariable, but the direct object combien de livres comes before the verb"), (r"lue", r"is feminine singular, but livres is masculine plural"), (r"lues", r"is feminine plural, but livres is masculine")],
        "accord_cod",
        r"The direct object combien de livres is placed before as lu, so the participle agrees with it: masculine plural, lus.",
        r"Find the direct object by asking what: tu as lu quoi ? The answer, livres, is placed in front, so the participle agrees.",
        r"Combien de livres as-tu lus cette année ?", extra=["verb conjugation"]))

    # ------------------------------------------------------------------------------------------------ conjugaison (5)
    a(Q("f19", "verb conjugation", "faible",
        r"Nous " + BL + r" le riz avant de partir.",
        r"mangeons", [(r"mangons", r"misses the e that keeps the soft g before o"), (r"mangeont", r"is not a form of manger"), (r"mangez", r"is the form for vous")],
        "conjugaison",
        r"Verbs in -ger keep an e before -ons so that the g stays soft: nous mangeons.",
        None, r"Nous mangeons le riz avant de partir."))
    a(Q("f20", "verb conjugation", "faible",
        r"Vous " + BL + r" la vérité.",
        r"dites", [(r"disez", r"is a regular form that does not exist for dire"), (r"disent", r"is the form for ils"), (r"dire", r"is the infinitive and cannot be conjugated here")],
        "conjugaison",
        r"Dire is irregular: with vous the present is dites, like faites and êtes.",
        None, r"Vous dites la vérité."))
    a(Q("f21", "verb conjugation", "moyenne",
        r"Nous " + BL + r" nos amis demain.",
        r"verrons", [(r"voyons", r"is the present and demain needs the future"), (r"verrions", r"is the conditionnel"), (r"voirons", r"is a regular future that does not exist for voir")],
        "conjugaison",
        r"Demain asks for the future, and the future stem of voir is verr-: nous verrons.",
        None, r"Nous verrons nos amis demain.", extra=["tenses and moods"]))
    a(Q("f22", "verb conjugation", "faible",
        r"Ils ne " + BL + r" pas rentrer avant minuit.",
        r"peuvent", [(r"peut", r"is the form for il, but the subject is ils"), (r"peuvents", r"is not a form of pouvoir"), (r"peuvant", r"is a spelling mistake")],
        "conjugaison",
        r"With ils the present of pouvoir is peuvent.",
        None, r"Ils ne peuvent pas rentrer avant minuit."))
    a(Q("f23", "verb conjugation", "faible",
        r"Je ne " + BL + r" pas ce mot.",
        r"connais", [(r"connaît", r"is the form for il"), (r"connaissent", r"is the form for ils"), (r"connaître", r"is the infinitive")],
        "conjugaison",
        r"With je the present of connaître is connais.",
        None, r"Je ne connais pas ce mot."))

    # ------------------------------------------------------------------------------------------------ pronoms (4) et relatifs (2)
    a(Q("f24", "pronouns", "faible",
        r"Mes parents habitent à Limbe ; j'" + BL + r" vais chaque été.",
        r"y", [(r"en", r"replaces de + a noun or a quantity, not a place one goes to"), (r"là", r"is an adverb and cannot follow j'"), (r"le", r"replaces a masculine noun object, not a place")],
        "pronoms",
        r"Y replaces a place introduced by à: j'y vais means I go there.",
        None, r"Mes parents habitent à Limbe ; j'y vais chaque été."))
    a(Q("f25", "pronouns", "moyenne",
        r"Tu as acheté des mangues ? Oui, j'" + BL + r" ai acheté trois.",
        r"en", [(r"y", r"replaces a place with à, not a quantity of fruit"), (r"les", r"cannot be used when a number follows the verb"), (r"des", r"is an article and not a pronoun")],
        "pronoms",
        r"En replaces des mangues and the number trois stays after the verb: j'en ai acheté trois.",
        None, r"Tu as acheté des mangues ? Oui, j'en ai acheté trois."))
    a(Q("f26", "pronouns", "faible",
        r"Ce livre est à moi ; ce n'est pas " + BL + r" de ma sœur.",
        r"celui", [(r"celle", r"is feminine, but livre is masculine"), (r"ceux", r"is plural, but livre is singular"), (r"ce", r"cannot be followed by de to replace a noun")],
        "pronoms_demonstratifs",
        r"The pronoun replaces le livre, which is masculine singular: celui de ma sœur.",
        None, r"Ce livre est à moi ; ce n'est pas celui de ma sœur."))
    a(Q("f27", "pronouns", "moyenne",
        r"Marie est ma voisine ; je " + BL + r" ai prêté mon vélo.",
        r"lui", [(r"la", r"is a direct object, but prêter qch à qqn takes an indirect object"), (r"leur", r"is plural, but Marie is one person"), (r"y", r"replaces a place or a thing, not a person")],
        "pronoms",
        r"Prêter quelque chose à quelqu'un takes the indirect object lui for one person: je lui ai prêté mon vélo.",
        None, r"Marie est ma voisine ; je lui ai prêté mon vélo."))
    a(Q("f28", "relative pronouns", "faible",
        r"Voici la maison " + BL + r" mon grand-père a construite.",
        r"que", [(r"qui", r"is a subject, but maison is the object of a construite"), (r"dont", r"replaces a complement with de, which the verb does not have"), (r"où", r"replaces a place or a time and does not suit construire")],
        "relatifs",
        r"Mon grand-père a construit la maison: the house is the direct object, so the relative pronoun is que.",
        None, r"Voici la maison que mon grand-père a construite.", extra=["agreement"]))
    a(Q("f29", "relative pronouns", "moyenne",
        r"Le directeur " + BL + r" j'ai parlé est très aimable.",
        r"à qui", [(r"qui", r"is a subject and would leave parler without its preposition"), (r"que", r"is a direct object, but parler takes à"), (r"dont", r"replaces de + noun, and parler à needs à")],
        "relatifs",
        r"Parler à quelqu'un takes à, and the antecedent is a person, so the relative pronoun is à qui.",
        None, r"Le directeur à qui j'ai parlé est très aimable."))

    # ------------------------------------------------------------------------------------------------ articles (4)
    a(Q("f30", "articles", "faible",
        r"Il y a " + BL + r" eau dans le puits.",
        r"de l'", [(r"du", r"is used before a masculine noun, but eau is feminine and starts with a vowel"), (r"l'", r"is the definite article and does not give a quantity"), (r"des", r"is plural, but eau is singular")],
        "articles_partitif",
        r"A quantity of water takes the partitif, and before a vowel it is de l': Il y a de l'eau dans le puits.",
        None, r"Il y a de l'eau dans le puits."))
    a(Q("f31", "articles", "moyenne",
        r"Nous n'avons pas " + BL + r" argent pour acheter ce téléphone.",
        r"d'", [(r"de l'", r"becomes d' after a negation"), (r"l'", r"is the definite article and does not give a quantity"), (r"un", r"is an indefinite article that does not follow pas")],
        "articles_partitif",
        r"After a negation the partitif becomes de, and before a vowel d': nous n'avons pas d'argent.",
        None, r"Nous n'avons pas d'argent pour acheter ce téléphone."))
    a(Q("f32", "articles", "faible",
        r"Ma sœur joue " + BL + r" piano chaque soir.",
        r"du", [(r"au", r"is used for a game or a sport, not for an instrument"), (r"le", r"cannot follow jouer without a preposition"), (r"de", r"is missing the masculine article that goes with piano")],
        "articles_instrument",
        r"After jouer, an instrument takes de + the article, and de + le becomes du: jouer du piano.",
        None, r"Ma sœur joue du piano chaque soir.", extra=["prepositions"]))
    a(Q("f33", "articles", "moyenne",
        r"Beaucoup " + BL + r" élèves sont absents aujourd'hui.",
        r"d'", [(r"des", r"cannot follow beaucoup, which takes de alone"), (r"de les", r"is never written like this: de and les contract to des"), (r"les", r"cannot follow beaucoup without de")],
        "articles_partitif",
        r"An expression of quantity such as beaucoup is followed by de alone, and before a vowel d': beaucoup d'élèves.",
        None, r"Beaucoup d'élèves sont absents aujourd'hui."))

    # ------------------------------------------------------------------------------------------------ expressions (3)
    a(Q("f34", "idioms", "faible",
        r"Il pleut des cordes. L'expression signifie que :",
        r"la pluie tombe très fort.", [(r"la pluie tombe par intervalles.", r"gives the idea of a light shower, which is the opposite"), (r"il fait très froid.", r"says nothing about the cold"), (r"la pluie est terminée.", r"says the contrary of the sentence")],
        "expressions",
        r"Il pleut des cordes is an image for heavy rain, as if ropes were falling from the sky.",
        None, None))
    a(Q("f35", "idioms", "moyenne",
        r"Mon cousin a le cœur sur la main. L'expression signifie qu'il :",
        r"est très généreux.", [(r"est malade du cœur.", r"reads the words literally and gives a health problem"), (r"est timide.", r"does not match the image of an open hand"), (r"est en colère.", r"does not match the image of an open hand")],
        "expressions",
        r"Avoir le cœur sur la main means to be generous: the heart is offered openly, as a hand holds out a gift.",
        None, None))
    a(Q("f36", "idioms", "elevee",
        r"Pour recevoir leurs invités, ils ont mis les petits plats dans les grands. L'expression signifie qu'ils :",
        r"ont préparé un repas somptueux.", [(r"ont rangé la vaisselle.", r"takes the words literally"), (r"ont acheté de nouveaux plats.", r"confuses the dishes with the food"), (r"ont cassé la vaisselle.", r"takes the words literally")],
        "expressions",
        r"Mettre les petits plats dans les grands means to prepare a splendid meal for guests; the expression is about the food and the effort, not about the dishes.",
        None, None))

    # ------------------------------------------------------------------------------------------------ prepositions (2)
    a(Q("f37", "prepositions", "faible",
        r"Les enfants jouent " + BL + r" la cour de l'école.",
        r"dans", [(r"sur", r"is used for a surface on top, which does not suit a yard"), (r"à", r"would read as at the court (à la cour), which does not name the school yard"), (r"en", r"is not followed by an article before a noun like cour")],
        "prepositions",
        r"Dans introduces a place seen as an enclosed space: les enfants jouent dans la cour de l'école.",
        None, r"Les enfants jouent dans la cour de l'école."))
    a(Q("f38", "prepositions", "moyenne",
        r"Je pense " + BL + r" mes examens depuis ce matin.",
        r"à", [(r"de", r"is used for opinions (que penses-tu de ?), not for thinking about something"), (r"sur", r"is not used with penser in this sense"), (r"pour", r"is not used with penser in this sense")],
        "prepositions",
        r"Penser à quelque chose means to have it in mind: je pense à mes examens.",
        None, r"Je pense à mes examens depuis ce matin."))

    # ------------------------------------------------------------------------------------------------ traduction (2)
    a(Q("f39", "translation into French", "moyenne",
        r"\"Better late than never.\" Can be translated as:",
        r"Mieux vaut tard que jamais.", [(r"Mieux est tard que jamais.", r"is not French: the verb is valoir, not être"), (r"Plus tard que jamais.", r"is a word-for-word version without a verb and without the idea of preference"),
                                         (r"Mieux vaut jamais que tard.", r"reverses the meaning of the proverb")],
        "traduction",
        r"The French proverb with the same meaning is Mieux vaut tard que jamais.",
        None, None, extra=["idioms"]))
    a(Q("f40", "translation into French", "elevee",
        r"\"Let sleeping dogs lie.\" Can be translated as:",
        r"Il ne faut pas réveiller le chat qui dort.", [(r"Chien qui aboie ne mord pas.", r"is another proverb: a barking dog does not bite, about threats that are not carried out"),
                                                        (r"Les chiens qui dorment sont fatigués.", r"changes the meaning of the proverb"), (r"Il faut réveiller les chiens endormis.", r"says the opposite")],
        "traduction",
        r"The French equivalent keeps the idea of not disturbing a danger that sleeps, with a cat instead of dogs: Il ne faut pas réveiller le chat qui dort.",
        None, None, extra=["idioms"]))

    # ------------------------------------------------------------------------------------------------ nombres (2), negation (1), genre (1), comparaison (1)
    a(Q("f41", "numbers and fractions", "faible",
        r"Trois quarts d'heure, c'est " + BL + r" minutes.",
        r"quarante-cinq", [(r"trente-cinq", r"is less than three quarters of an hour"), (r"cinquante-cinq", r"is more than three quarters of an hour"), (r"soixante-quinze", r"is more than an hour")],
        "nombres",
        r"One quarter of an hour is 15 minutes, so three quarters is 3 x 15 = 45 minutes: quarante-cinq.",
        None, r"Trois quarts d'heure, c'est quarante-cinq minutes."))
    a(Q("f42", "numbers and fractions", "faible",
        r"La moitié de cent cinquante, c'est " + BL + r".",
        r"soixante-quinze", [(r"soixante-dix", r"is 70 and half of 150 is 75"), (r"cinquante", r"is a third of 150, not a half"), (r"quatre-vingts", r"is 80 and half of 150 is 75")],
        "nombres",
        r"Half of 150 is 75, and 75 is written soixante-quinze (60 + 15).",
        None, r"La moitié de cent cinquante, c'est soixante-quinze."))
    a(Q("f43", "negation", "moyenne",
        r"Mon frère ne boit " + BL + r" de lait.",
        r"jamais", [(r"rien", r"refers to a thing and cannot be followed by de lait"), (r"personne", r"refers to a person"), (r"aucun", r"is followed by a noun directly, not by de lait")],
        "negation",
        r"A negation of frequency is built with jamais, and the partitif becomes de after it: mon frère ne boit jamais de lait.",
        None, r"Mon frère ne boit jamais de lait."))
    a(Q("f44", "gender and number", "faible",
        r"Au féminin, le mot « directeur » devient :",
        r"directrice", [(r"directeuse", r"is a regular feminine that does not exist for this word"), (r"directeure", r"is not a feminine of directeur"), (r"directeur", r"is the masculine form")],
        "genre",
        r"Many nouns in -teur take -trice in the feminine: directeur, directrice.",
        None, None))
    a(Q("f45", "comparison", "faible",
        r"Ce chocolat est " + BL + r" que celui d'hier.",
        r"meilleur", [(r"mieux", r"is the comparative of bien, an adverb, and cannot describe a noun"), (r"plus bon", r"is not used: the comparative of bon is meilleur"), (r"plus meilleur", r"doubles the comparative")],
        "comparatif",
        r"The comparative of the adjective bon is meilleur: Ce chocolat est meilleur que celui d'hier.",
        None, r"Ce chocolat est meilleur que celui d'hier."))

    # ------------------------------------------------------------------------------------------------ texte a trous (46-50)
    a(Q("f46", "reading comprehension", "faible",
        TEXTE + "\n\n**Space 46:** choose the answer that fills it.",
        r"chercher", [(r"cherché", r"is a participle and cannot follow aller y"), (r"cherchent", r"is a conjugated form, but pour aller y needs an infinitive"), (r"cherchez", r"is a conjugated form for vous")],
        "texte_infinitif",
        r"The verb after pour aller y is an infinitive: chercher de l'eau.",
        None, None, extra=["verb conjugation"]))
    a(Q("f47", "reading comprehension", "moyenne",
        r"(Text for questions 46 to 50 above)" "\n\n" r"**Space 47:** choose the answer that fills it.",
        r"premières", [(r"premier", r"is masculine singular, but maisons is feminine plural"), (r"premiers", r"is masculine plural, but maisons is feminine"), (r"première", r"is feminine singular, but maisons is plural")],
        "texte_accord",
        r"The adjective describes maisons, which is feminine plural: les premières maisons.",
        None, None, extra=["agreement"]))
    a(Q("f48", "reading comprehension", "moyenne",
        r"(Text for questions 46 to 50 above)" "\n\n" r"**Space 48:** choose the answer that fills it.",
        r"c'est pourquoi", [(r"parce que", r"gives the cause, but the tiredness is the result of the long way"), (r"bien que", r"introduces a concession and needs the subjonctif"), (r"alors que", r"introduces an opposition and does not fit the result")],
        "connecteur",
        r"The long way causes the tiredness, so the second idea is a result, and c'est pourquoi introduces a result.",
        None, None, extra=["vocabulary"]))
    a(Q("f49", "reading comprehension", "moyenne",
        r"(Text for questions 46 to 50 above)" "\n\n" r"**Space 49:** choose the answer that fills it.",
        r"toutes", [(r"tout", r"is masculine singular, but femmes is feminine plural"), (r"tous", r"is masculine plural, but femmes is feminine"), (r"toute", r"is feminine singular, but femmes is plural")],
        "texte_accord",
        r"Tout agrees with the noun it determines: les femmes is feminine plural, so toutes les femmes.",
        None, None, extra=["agreement"]))
    a(Q("f50", "reading comprehension", "elevee",
        r"(Text for questions 46 to 50 above)" "\n\n" r"**Space 50:** choose the answer that fills it.",
        r"qu'", [(r"qui", r"is a subject, but celui is the object of utilisent"), (r"dont", r"replaces de + noun, and utiliser does not take de"), (r"où", r"replaces a place or a time")],
        "relatifs",
        r"Celui stands for le puits, the direct object of utilisent, so the relative pronoun is que, which becomes qu' before elles.",
        None, None, extra=["relative pronouns"]))
    return q
