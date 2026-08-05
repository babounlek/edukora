# -*- coding: utf-8 -*-
import json, os

OUTDIR = "/sessions/brave-ecstatic-ritchie/mnt/Epreuves/json/cm/bac-blanc-d-ti-physique-2025-cameroun"
EPREUVE_SOURCE = "bac-blanc-d-ti-physique-2025-cameroun.pdf"
EPREUVE_SLUG = "bac-blanc-d-ti-physique-2025-cameroun"
EPREUVE_ID = "bac-blanc-d-ti-physique-2025-cameroun"
EPREUVE_TITRE = "Baccalaureat blanc D et TI - Physique - Session 2025 (DRES-NORD, evaluations harmonisees regionales)"

RAPPELS_REGISTRY = []  # list of dicts: id, competence, exercice_numero, question_numero, texte

def build_question(numero, enonce_markdown, themes, difficulte, rappel_competence,
                    rappel_text, corps_text, piege_text=None, conseil_text=None,
                    type_reponse="ouverte", choix=None, reponse_correcte=None,
                    exercice_numero="1"):
    parts = ["### Rappel de méthode", rappel_text.strip(), "", "### Corrigé", corps_text.strip()]
    if piege_text:
        parts += ["", "### Piège à éviter", piege_text.strip()]
    if conseil_text:
        parts += ["", "### Conseil", conseil_text.strip()]
    corrige_markdown = "\n".join(parts)

    rappel_id = f"rdm-{EPREUVE_SLUG}-ex{exercice_numero}-q{numero}-0"
    rappel_obj = {
        "id": rappel_id,
        "competence": rappel_competence,
        "contenu_markdown": rappel_text.strip(),
        "cours_genere": True,
        "cours_id": None
    }
    RAPPELS_REGISTRY.append({
        "id": rappel_id, "competence": rappel_competence,
        "exercice_numero": exercice_numero, "question_numero": numero,
        "texte": rappel_text.strip()
    })
    q = {
        "numero": numero,
        "enonce_markdown": enonce_markdown.strip(),
        "corrige_markdown": corrige_markdown,
        "themes": themes,
        "difficulte_estimee": difficulte,
        "type_reponse": type_reponse,
        "choix": choix if choix is not None else [],
        "reponse_correcte": reponse_correcte if reponse_correcte is not None else "",
        "rappels_de_methode": [rappel_obj]
    }
    return q

EXERCISES = {}

# ============================= EXERCICE 1 =============================
ex1_questions = []

ex1_questions.append(build_question(
    numero="1",
    enonce_markdown="Définir : condensateur, stroboscopie.",
    themes=["Condensateur", "Stroboscopie", "Vocabulaire de physique"],
    difficulte="faible",
    rappel_competence="Définitions - condensateur et stroboscopie",
    rappel_text=r"""Une question de définition attend une phrase précise et complète : nature de l'objet ou du phénomène, puis sa caractéristique essentielle. Pas de paraphrase vague, une définition doit permettre de reconnaître l'objet sans ambiguïté.""",
    corps_text=r"""**Condensateur** : un condensateur est un composant électrique constitué de deux armatures conductrices (souvent métalliques) séparées par un isolant appelé diélectrique. Il a la capacité d'emmagasiner de l'énergie électrique sous forme de charges électriques de signes opposés sur ses deux armatures, lorsqu'il est soumis à une tension.

**Stroboscopie** : la stroboscopie est une technique d'observation d'un mouvement périodique rapide à l'aide d'éclairs lumineux brefs et périodiques, produits par un stroboscope. Quand la fréquence des éclairs est adaptée à celle du mouvement observé, l'objet en mouvement paraît immobile ou animé d'un mouvement ralenti.""",
    conseil_text=r"""Au bac, une définition qui contient les mots-clés attendus (armatures, isolant, énergie électrique pour le condensateur ; éclairs, périodique, immobile pour la stroboscopie) rapporte presque toujours le point, même formulée simplement. Structure toujours ta réponse en donnant d'abord la nature de l'objet, puis sa fonction ou sa propriété caractéristique.""",
    exercice_numero="1"
))

ex1_questions.append(build_question(
    numero="2",
    enonce_markdown="Énoncer la loi de Laplace.",
    themes=["Loi de Laplace", "Force électromagnétique", "Champ magnétique"],
    difficulte="faible",
    rappel_competence="La loi de Laplace",
    rappel_text=r"""La loi de Laplace décrit la force subie par un conducteur parcouru par un courant lorsqu'il est placé dans un champ magnétique. Elle se formule vectoriellement à partir de l'intensité du courant, de la longueur du conducteur et du champ magnétique.""",
    corps_text=r"""Tout élément de circuit de longueur $\vec{dl}$, parcouru par un courant d'intensité $I$, placé dans un champ magnétique extérieur $\vec{B}$, subit de la part de ce champ une force électromagnétique $\vec{dF}$ telle que :

$$\vec{dF} = I\,\vec{dl} \wedge \vec{B}$$

La direction de $\vec{dF}$ est perpendiculaire au plan formé par $\vec{dl}$ et $\vec{B}$, son sens est donné par la règle de la main droite (ou règle des trois doigts), et son intensité vaut $dF = I\,dl\,B\sin\theta$, où $\theta$ est l'angle entre $\vec{dl}$ et $\vec{B}$.""",
    piege_text=r"""Ne confonds pas la loi de Laplace (force sur un courant placé dans un champ magnétique) avec la loi de Coulomb (interaction entre deux charges électriques) : le QCM de cet exercice teste justement cette confusion à la question 4.1.""",
    exercice_numero="1"
))

ex1_questions.append(build_question(
    numero="3",
    enonce_markdown="Donner l'expression vectorielle du champ électrostatique créé en un point P par une charge ponctuelle q < 0 placée en un point O, puis représenter ce vecteur sur un schéma.",
    themes=["Champ électrostatique", "Charge ponctuelle", "Loi de Coulomb"],
    difficulte="moyenne",
    rappel_competence="Champ électrostatique créé par une charge ponctuelle",
    rappel_text=r"""Le champ électrostatique créé par une charge ponctuelle en un point de l'espace se calcule à partir de la loi de Coulomb. Sa direction est portée par la droite reliant la charge au point considéré, et son sens dépend du signe de la charge : il s'éloigne d'une charge positive et se dirige vers une charge négative.""",
    corps_text=r"""Le champ électrostatique créé au point P par la charge ponctuelle q placée en O s'écrit :

$$\vec{E}(P) = \dfrac{1}{4\pi\varepsilon_0}\,\dfrac{q}{OP^2}\,\vec{u}_{OP}$$

où $\vec{u}_{OP}$ est le vecteur unitaire porté par la droite (OP), orienté de O vers P, et $\varepsilon_0$ la permittivité du vide.

Comme q < 0, le coefficient devant $\vec{u}_{OP}$ est négatif : le vecteur $\vec{E}(P)$ est donc colinéaire à $\vec{u}_{OP}$ mais de sens opposé, c'est-à-dire dirigé de P vers O. Une charge négative attire vers elle les lignes de champ : le vecteur champ en tout point pointe vers la charge qui le crée.

Schéma : on place O (charge q<0) et P distinct de O. On trace le segment [OP], on y place le vecteur unitaire $\vec{u}_{OP}$ orienté de O vers P, puis on représente $\vec{E}(P)$ sur le support de la droite (OP) mais pointant de P vers O (flèche en sens inverse de $\vec{u}_{OP}$).""",
    piege_text=r"""L'erreur classique est de dessiner $\vec{E}$ dans le sens de $\vec{u}_{OP}$ (de O vers P) par réflexe, sans tenir compte du signe négatif de q. Vérifie toujours le signe de la charge avant de tracer le vecteur : positive, le champ s'en éloigne ; négative, le champ y entre.""",
    exercice_numero="1"
))

ex1_questions.append(build_question(
    numero="4.1",
    enonce_markdown="Question à choix multiples. La loi traduisant l'interaction entre deux particules chargées est : (a) La loi d'attraction universelle (b) La loi de Laplace (c) La loi de Coulomb.",
    themes=["Loi de Coulomb", "Interaction électrique"],
    difficulte="faible",
    rappel_competence="Loi de Coulomb",
    rappel_text=r"""La loi de Coulomb décrit la force d'interaction entre deux charges électriques ponctuelles, proportionnelle au produit des charges et inversement proportionnelle au carré de la distance qui les sépare.""",
    corps_text=r"""La loi d'attraction universelle (Newton) décrit l'interaction gravitationnelle entre deux masses, pas entre deux charges : elle ne convient pas ici. La loi de Laplace décrit la force subie par un courant électrique placé dans un champ magnétique, pas l'interaction entre deux particules chargées au repos. La loi qui décrit directement l'interaction (attraction ou répulsion) entre deux particules chargées est la loi de Coulomb, qui s'écrit $F = k\dfrac{|q_1 q_2|}{r^2}$.

La réponse correcte est **(c) La loi de Coulomb**.""",
    type_reponse="qcm",
    choix=[{"lettre":"a","texte":"La loi d'attraction universelle"},{"lettre":"b","texte":"La loi de Laplace"},{"lettre":"c","texte":"La loi de Coulomb"}],
    reponse_correcte="c",
    exercice_numero="1"
))

ex1_questions.append(build_question(
    numero="4.2",
    enonce_markdown="Le dispositif qui permet de visualiser une grandeur périodique sur un écran est : a) L'oscillographe b) Le stroboscope c) L'oscilloscope.",
    themes=["Oscilloscope", "Signaux périodiques"],
    difficulte="faible",
    rappel_competence="L'oscilloscope, appareil de visualisation des signaux périodiques",
    rappel_text=r"""Un oscilloscope est l'appareil de mesure qui affiche sur un écran l'évolution temporelle d'une tension électrique, ce qui permet de visualiser directement une grandeur périodique.""",
    corps_text=r"""Le stroboscope permet d'observer un mouvement périodique par éclairs successifs, mais ne dispose pas d'écran d'affichage. L'oscillographe est un terme plus général qui désigne un appareil enregistreur de signal, mais l'appareil précisément équipé d'un écran pour visualiser une tension en temps réel est l'oscilloscope.

La réponse correcte est **(c) L'oscilloscope**.""",
    type_reponse="qcm",
    choix=[{"lettre":"a","texte":"L'oscillographe"},{"lettre":"b","texte":"Le stroboscope"},{"lettre":"c","texte":"L'oscilloscope"}],
    reponse_correcte="c",
    exercice_numero="1"
))

ex1_questions.append(build_question(
    numero="4.3",
    enonce_markdown="L'espace situé entre les armatures d'un condensateur est : a) Isolant b) Semi-conducteur c) Conducteur.",
    themes=["Condensateur", "Diélectrique"],
    difficulte="faible",
    rappel_competence="Structure d'un condensateur plan",
    rappel_text=r"""Un condensateur est constitué de deux armatures conductrices séparées par un matériau qui empêche le passage du courant entre elles, appelé diélectrique.""",
    corps_text=r"""Si l'espace entre les armatures était conducteur, les charges positives et négatives se neutraliseraient immédiatement par ce chemin conducteur, et le condensateur ne pourrait stocker aucune charge. C'est justement parce que cet espace est isolant que les charges restent séparées sur les deux armatures et que le condensateur peut emmagasiner de l'énergie.

La réponse correcte est **(a) Isolant**.""",
    type_reponse="qcm",
    choix=[{"lettre":"a","texte":"Isolant"},{"lettre":"b","texte":"Semi-conducteur"},{"lettre":"c","texte":"Conducteur"}],
    reponse_correcte="a",
    exercice_numero="1"
))

ex1_questions.append(build_question(
    numero="4.4",
    enonce_markdown="Deux sources vibrant avec la même période sont dites : a) Isochrones b) Cohérentes c) Synchrones.",
    themes=["Isochronisme", "Vocabulaire des oscillateurs"],
    difficulte="moyenne",
    rappel_competence="Isochronisme, synchronisme, cohérence",
    rappel_text=r"""Deux sources sont isochrones lorsqu'elles vibrent avec la même période (ou la même fréquence), indépendamment de leur phase relative. La cohérence exige en plus une différence de phase constante dans le temps, et le synchronisme exige une phase identique à chaque instant.""",
    corps_text=r"""L'énoncé précise uniquement que les deux sources vibrent « avec la même période », sans rien indiquer sur leur phase relative. Cette seule condition (même période, donc même fréquence) définit l'isochronisme. La cohérence ajouterait l'exigence d'un déphasage constant, et le synchronisme exigerait une identité de phase à chaque instant : ces deux conditions ne sont pas données dans l'énoncé.

La réponse correcte est **(a) Isochrones**.""",
    piege_text=r"""Isochrones, cohérentes et synchrones sont trois notions proches mais distinctes en physique des ondes : ne les utilise pas comme des synonymes. Retiens l'ordre d'exigence croissante : isochronisme (même période) inclus dans cohérence (+ déphasage constant) inclus dans synchronisme (+ phase identique).""",
    type_reponse="qcm",
    choix=[{"lettre":"a","texte":"Isochrones"},{"lettre":"b","texte":"Cohérentes"},{"lettre":"c","texte":"Synchrones"}],
    reponse_correcte="a",
    exercice_numero="1"
))

ex1_questions.append(build_question(
    numero="5.1",
    enonce_markdown="Répondre par vrai ou faux : l'émission photoélectrique dépend de la puissance de la lumière.",
    themes=["Effet photoélectrique", "Fréquence seuil"],
    difficulte="moyenne",
    rappel_competence="Conditions de l'émission photoélectrique",
    rappel_text=r"""L'effet photoélectrique n'a lieu que si la fréquence de la lumière incidente dépasse une fréquence seuil caractéristique du métal éclairé. En dessous de ce seuil, aucun électron n'est arraché, quelle que soit la puissance (l'intensité) de la lumière reçue.""",
    corps_text=r"""L'émission photoélectrique (le fait qu'il y ait ou non émission d'électrons) est conditionnée par la fréquence de la lumière incidente, comparée à la fréquence seuil $\nu_0$ du métal : si $\nu \geq \nu_0$, il y a émission, sinon aucun électron n'est arraché, même en augmentant fortement la puissance lumineuse. La puissance de la lumière influence uniquement le nombre d'électrons arrachés par seconde (donc l'intensité du courant photoélectrique), pas le fait même que l'émission se produise ni l'énergie cinétique maximale des électrons émis.

L'affirmation est donc **fausse**.""",
    piege_text=r"""Beaucoup d'élèves confondent « intensité du courant photoélectrique » (qui dépend bien de la puissance lumineuse) avec « existence de l'émission photoélectrique » (qui dépend uniquement de la fréquence). Ce sont deux grandeurs différentes, gouvernées par deux paramètres différents.""",
    type_reponse="qcm",
    choix=["Vrai", "Faux"],
    reponse_correcte="Faux",
    exercice_numero="1"
))

ex1_questions.append(build_question(
    numero="5.2",
    enonce_markdown="Répondre par vrai ou faux : pour qu'un virage soit réussi, il faut que la réaction et le poids aient la même droite d'action.",
    themes=["Mouvement circulaire", "Virage", "Deuxième loi de Newton"],
    difficulte="moyenne",
    rappel_competence="Équilibre et virage d'un véhicule",
    rappel_text=r"""Pour qu'un véhicule prenne un virage, la résultante des forces qui s'exercent sur lui doit posséder une composante horizontale dirigée vers le centre de la trajectoire, qui assure l'accélération centripète nécessaire au changement de direction.""",
    corps_text=r"""Si la réaction du sol $\vec{R}$ et le poids $\vec{P}$ avaient la même droite d'action (l'une verticale, l'autre portée par cette même droite), leur résultante serait nulle ou verticale : le véhicule ne subirait alors aucune force horizontale, donc aucune accélération centripète, et ne pourrait pas changer de direction. Il continuerait en ligne droite.

Pour qu'un virage soit réussi, la réaction du sol doit au contraire posséder une composante horizontale (liée à l'adhérence ou à l'inclinaison de la chaussée) distincte de la droite d'action du poids, de manière que la résultante $\vec{R}+\vec{P}$ soit dirigée vers le centre du virage.

L'affirmation est donc **fausse**.""",
    conseil_text=r"""Pense à ce cas limite pour vérifier ta réponse le jour de l'examen : une trajectoire rectiligne uniforme correspond exactement au cas où $\vec{R}$ et $\vec{P}$ sont alignées (résultante nulle). Dès qu'il y a virage, il y a nécessairement une résultante non nulle dirigée vers le centre, donc $\vec{R}$ et $\vec{P}$ ne peuvent pas être colinéaires.""",
    type_reponse="qcm",
    choix=["Vrai", "Faux"],
    reponse_correcte="Faux",
    exercice_numero="1"
))

EXERCISES["1"] = {
    "numero_exercice": "1",
    "titre": "Exercice 1 : Vérification des savoirs",
    "points": "8",
    "figures": [],
    "enonce_intro_markdown": "**Exercice 1 : Vérification des savoirs (8 points)**",
    "questions": ex1_questions
}
print("Exercice 1 : ", len(ex1_questions), "questions")

# ============================= EXERCICE 2 =============================
ex2_questions = []

ex2_questions.append(build_question(
    numero="1.1",
    enonce_markdown=r"""**1. Champ électrostatique (2 points)**

Deux charges ponctuelles $q_A$ et $q_B$ sont fixées respectivement en A et en B. La figure ci-dessous représente quelques lignes de champ électrostatique produites par la source $(q_A, q_B)$.

![fig-1](bac-blanc-d-ti-physique-2025-cameroun_exercice_2_fig_1.png)

1.1. Ce champ est-il uniforme ? Justifier la réponse.""",
    themes=["Champ électrostatique uniforme", "Lignes de champ"],
    difficulte="faible",
    rappel_competence="Caractériser un champ électrostatique uniforme à partir des lignes de champ",
    rappel_text=r"""Un champ électrostatique est uniforme lorsque le vecteur champ $\vec{E}$ garde la même direction, le même sens et la même intensité en tout point de l'espace considéré. Sur une carte de lignes de champ, cela se traduit par des lignes parallèles et équidistantes, comme entre les plaques d'un condensateur plan.""",
    corps_text=r"""Sur la figure, les lignes de champ ne sont ni parallèles ni équidistantes : elles sont courbes, divergent depuis $q_A$ et $q_B$, et leur écartement varie d'un point à l'autre de l'espace. Le vecteur champ $\vec{E}$ change donc de direction et d'intensité selon le point considéré.

Ce champ n'est **pas uniforme**.""",
    piege_text=r"""Ne confonds pas « champ radial issu d'une charge ponctuelle » (toujours non uniforme, l'intensité décroissant en $1/r^2$) avec le champ uniforme propre au condensateur plan (lignes parallèles, équidistantes). Une carte de champ avec des lignes courbes ou qui divergent d'un point signale toujours un champ non uniforme.""",
    exercice_numero="2"
))

ex2_questions.append(build_question(
    numero="1.2",
    enonce_markdown="1.2. Déterminer les signes de $q_A$ et $q_B$. Justifier la réponse.",
    themes=["Signe d'une charge", "Lignes de champ", "Champ électrostatique"],
    difficulte="moyenne",
    rappel_competence="Signe d'une charge à partir de l'orientation des lignes de champ",
    rappel_text=r"""Une ligne de champ électrostatique est orientée dans le sens du vecteur $\vec{E}$ : elle part toujours d'une charge positive (ou de l'infini) et arrive toujours sur une charge négative (ou part vers l'infini). Le sens des flèches sur la figure indique donc directement le signe des charges qui créent le champ.""",
    corps_text=r"""Sur la figure, toutes les flèches des lignes de champ pointent en s'éloignant à la fois de $q_A$ et de $q_B$ : aucune ligne n'entre dans l'une ou l'autre charge, toutes en sortent. Un champ électrostatique sort toujours d'une charge positive.

$q_A$ et $q_B$ sont donc **toutes les deux positives** ($q_A > 0$ et $q_B > 0$).""",
    conseil_text=r"""Pour vérifier rapidement ce genre de figure, regarde uniquement le sens des flèches au voisinage immédiat de chaque charge, sans te laisser perturber par la forme globale du faisceau de lignes : c'est ce sens local qui donne le signe.""",
    exercice_numero="2"
))

ex2_questions.append(build_question(
    numero="1.3",
    enonce_markdown=r"1.3. Calculer la distance $d$ entre les charges sachant que le champ créé par la charge A au point B vaut $E = 9\times 10^5\ N/C$ et que $|q_A| = |q_B| = 1\ \mu C$.",
    themes=["Champ électrostatique", "Loi de Coulomb", "Calcul littéral"],
    difficulte="moyenne",
    rappel_competence="Champ créé par une charge ponctuelle - loi de Coulomb appliquée au champ",
    rappel_text=r"""Le champ créé par une charge ponctuelle $q$ à une distance $r$ vaut $E = k\dfrac{|q|}{r^2}$, avec $k = \dfrac{1}{4\pi\varepsilon_0} \approx 9\times10^9\ N\cdot m^2/C^2$. Connaissant $E$ et $|q|$, on isole $r$ par calcul inverse.""",
    corps_text=r"""Le champ créé par la charge $q_A$ au point B, situé à la distance $d = AB$, s'écrit :

$$E = k\dfrac{|q_A|}{d^2}$$

On isole $d^2$ :

$$d^2 = k\dfrac{|q_A|}{E}$$

Application numérique, avec $k = 9\times10^9\ N\cdot m^2/C^2$, $|q_A| = 1\times10^{-6}\ C$ et $E = 9\times10^5\ N/C$ :

$$d^2 = \dfrac{9\times10^9 \times 1\times10^{-6}}{9\times10^5} = \dfrac{9\times10^{3}}{9\times10^{5}} = 1\times10^{-2}\ m^2$$

$$d = \sqrt{1\times10^{-2}} = 1\times10^{-1}\ m = 0{,}1\ m$$

La distance entre les charges est $d = 0{,}1\ m = 10\ cm$.""",
    piege_text=r"""N'oublie pas l'étape de racine carrée finale : beaucoup d'élèves s'arrêtent à $d^2 = 10^{-2}\ m^2$ et donnent cette valeur comme réponse, en oubliant que la question demande $d$, pas $d^2$. Vérifie aussi que l'unité finale est bien un mètre, pas un mètre carré.""",
    exercice_numero="2"
))

ex2_questions.append(build_question(
    numero="2.1",
    enonce_markdown=r"""**2. Application des lois de Newton (2 points)**

Un solide de masse $m = 15\ kg$ est mis en mouvement de translation rectiligne horizontale par une force de traction $F = 75\ N$, exercée par une corde inextensible de direction horizontale. On néglige les frottements et on donne $g = 9{,}8\ m/s^2$.

2.1. Déterminer l'accélération du mouvement du solide.""",
    themes=["Deuxième loi de Newton", "Dynamique", "Translation rectiligne"],
    difficulte="faible",
    rappel_competence="Deuxième loi de Newton (principe fondamental de la dynamique)",
    rappel_text=r"""La deuxième loi de Newton relie la résultante des forces appliquées à un solide à son accélération : $\sum \vec{F} = m\vec{a}$. En l'absence de frottement et pour un mouvement horizontal, seule la force de traction produit une accélération horizontale.""",
    corps_text=r"""Le solide est soumis à son poids $\vec{P}$, à la réaction normale du support $\vec{R}$, et à la force de traction $\vec{F}$. Le poids et la réaction se compensent verticalement (le solide ne décolle pas et ne s'enfonce pas), il ne reste donc que $\vec{F}$ dans le bilan horizontal.

La deuxième loi de Newton appliquée en projection sur l'axe horizontal du mouvement donne :

$$F = m\,a \quad \Longrightarrow \quad a = \dfrac{F}{m}$$

Application numérique :

$$a = \dfrac{75}{15} = 5\ m/s^2$$

L'accélération du solide vaut $a = 5\ m/s^2$.""",
    piege_text=r"""La donnée $g = 9{,}8\ m/s^2$ n'intervient pas dans ce calcul : elle ne sert que pour étudier l'équilibre vertical (par exemple pour calculer la réaction du support), ce qui n'est pas demandé ici. Ne l'utilise pas par réflexe dans une formule qui n'en a pas besoin.""",
    exercice_numero="2"
))

ex2_questions.append(build_question(
    numero="2.2",
    enonce_markdown="2.2. Calculer la vitesse acquise par le solide après $5\\ s$.",
    themes=["Mouvement rectiligne uniformément varié", "Cinématique"],
    difficulte="faible",
    rappel_competence="Mouvement rectiligne uniformément varié - relation vitesse-accélération-temps",
    rappel_text=r"""Pour un mouvement rectiligne uniformément varié partant du repos avec une accélération constante $a$, la vitesse à l'instant $t$ vaut $v(t) = a\,t$.""",
    corps_text=r"""Le solide est « mis en mouvement » par la force de traction : il part donc du repos, avec $v_0 = 0$. Avec une accélération constante $a = 5\ m/s^2$ (question 2.1), la vitesse à l'instant $t$ s'écrit :

$$v(t) = v_0 + a\,t = a\,t$$

Application numérique, pour $t = 5\ s$ :

$$v(5) = 5 \times 5 = 25\ m/s$$

La vitesse acquise après 5 secondes est $v = 25\ m/s$.""",
    conseil_text=r"""25 m/s correspond à 90 km/h : un ordre de grandeur élevé pour un solide tracté au sol, mais cohérent avec les valeurs purement théoriques de l'énoncé (frottements négligés). C'est un bon réflexe de convertir en km/h pour juger si un résultat de cinématique est physiquement raisonnable.""",
    exercice_numero="2"
))

ex2_questions.append(build_question(
    numero="3.1",
    enonce_markdown=r"""**3. Mouvement d'une particule (2 points)**

La loi horaire du mouvement d'un solide est $\theta(t) = -2\cos(100\pi t + \pi/3)$. Déterminer la fréquence du mouvement et sa phase à l'instant initial.""",
    themes=["Mouvement sinusoïdal", "Pulsation", "Phase à l'origine"],
    difficulte="moyenne",
    rappel_competence="Équation horaire d'un mouvement sinusoïdal - amplitude, pulsation, phase",
    rappel_text=r"""Une grandeur sinusoïdale s'écrit sous la forme canonique $\theta(t) = \theta_m\cos(\omega t + \varphi)$, avec $\theta_m > 0$ l'amplitude, $\omega$ la pulsation en $rad/s$, et $\varphi$ la phase à l'origine des temps. La fréquence se déduit de la pulsation par $f = \dfrac{\omega}{2\pi}$. Si l'expression donnée comporte un coefficient négatif devant le cosinus, il faut d'abord la mettre sous forme canonique en utilisant $-\cos(x) = \cos(x+\pi)$.""",
    corps_text=r"""L'expression donnée est $\theta(t) = -2\cos(100\pi t + \pi/3)$, avec un coefficient négatif $-2$ devant le cosinus : ce n'est pas encore la forme canonique, où l'amplitude doit être positive.

On utilise l'identité trigonométrique $-\cos(x) = \cos(x + \pi)$ :

$$\theta(t) = -2\cos(100\pi t + \pi/3) = 2\cos\big(100\pi t + \pi/3 + \pi\big) = 2\cos\big(100\pi t + \tfrac{4\pi}{3}\big)$$

Par identification avec $\theta(t) = \theta_m\cos(\omega t + \varphi)$ :

$$\theta_m = 2\ rad \qquad \omega = 100\pi\ rad/s \qquad \varphi = \dfrac{4\pi}{3}\ rad$$

La fréquence se déduit de la pulsation :

$$f = \dfrac{\omega}{2\pi} = \dfrac{100\pi}{2\pi} = 50\ Hz$$

La phase à l'instant initial est $\varphi = \dfrac{4\pi}{3}\ rad$, ce qui équivaut, modulo $2\pi$, à $\varphi = \dfrac{4\pi}{3} - 2\pi = -\dfrac{2\pi}{3}\ rad$.

La fréquence du mouvement est $f = 50\ Hz$, et sa phase à l'origine des temps est $\varphi = \dfrac{4\pi}{3}\ rad$ (ou, de façon équivalente, $-\dfrac{2\pi}{3}\ rad$).""",
    piege_text=r"""Ne recopie jamais directement $\pi/3$ comme phase à l'origine sous prétexte que c'est le terme qui apparaît dans l'énoncé : ce $\pi/3$ n'est la vraie phase à l'origine que si le coefficient devant le cosinus est positif. Ici il est négatif, il faut donc transformer l'écriture avant de lire la phase.""",
    exercice_numero="2"
))

ex2_questions.append(build_question(
    numero="4",
    enonce_markdown=r"""**4. Circuit RLC (2 points)**

On réalise un circuit série constitué d'un conducteur ohmique de résistance $r = 100\ \Omega$, d'un condensateur de capacité $C = 5\times10^{-6}\ F$ et d'une bobine pure d'inductance $L = 0{,}100\ H$. Ce circuit est alimenté par un GBF dont la pulsation est $\omega = 100\ rad/s$. Déterminer l'impédance du circuit.""",
    themes=["Circuit RLC série", "Impédance", "Réactance"],
    difficulte="moyenne",
    rappel_competence="Impédance d'un circuit RLC série en régime sinusoïdal forcé",
    rappel_text=r"""Pour un circuit RLC série en régime sinusoïdal forcé de pulsation $\omega$, l'impédance totale se calcule à partir de la résistance $r$ et de la réactance totale $\left(L\omega - \dfrac{1}{C\omega}\right)$, combinaison de la réactance inductive de la bobine et de la réactance capacitive du condensateur : $Z = \sqrt{r^2 + \left(L\omega - \dfrac{1}{C\omega}\right)^2}$.""",
    corps_text=r"""On calcule séparément la réactance inductive et la réactance capacitive.

Réactance inductive de la bobine :
$$X_L = L\omega = 0{,}100 \times 100 = 10\ \Omega$$

Réactance capacitive du condensateur :
$$X_C = \dfrac{1}{C\omega} = \dfrac{1}{5\times10^{-6} \times 100} = \dfrac{1}{5\times10^{-4}} = 2000\ \Omega$$

Réactance totale du circuit :
$$X_L - X_C = 10 - 2000 = -1990\ \Omega$$

Impédance du circuit :
$$Z = \sqrt{r^2 + (X_L - X_C)^2} = \sqrt{100^2 + (-1990)^2} = \sqrt{10\,000 + 3\,960\,100} = \sqrt{3\,970\,100}$$

$$Z \approx 1992{,}5\ \Omega$$

L'impédance du circuit vaut environ $Z \approx 1{,}99\times10^3\ \Omega$.""",
    piege_text=r"""La réactance capacitive est ici bien plus grande que la réactance inductive ($X_C = 2000\ \Omega \gg X_L = 10\ \Omega$), à cause de la faible pulsation ($\omega = 100\ rad/s$) : le circuit est très majoritairement capacitif. Ne néglige jamais $X_C$ sous prétexte qu'il « semble » petit par rapport à $r$ sans l'avoir calculé numériquement.""",
    conseil_text=r"""Pour vérifier ton résultat, contrôle que $Z$ est toujours supérieure ou égale à $r$ et à $|X_L - X_C|$ pris séparément : ici $Z \approx 1992{,}5\ \Omega$ est bien légèrement supérieure à $|X_L-X_C|=1990\ \Omega$, ce qui est cohérent puisque $Z=\sqrt{r^2+(X_L-X_C)^2}$ est toujours au moins égale au plus grand des deux termes.""",
    exercice_numero="2"
))

EXERCISES["2"] = {
    "numero_exercice": "2",
    "titre": "Exercice 2 : Application des savoirs",
    "points": "8",
    "figures": [
        {
            "id": "fig-1",
            "fichier": "bac-blanc-d-ti-physique-2025-cameroun_exercice_2_fig_1.png",
            "page_source": 1,
            "type": "schema",
            "legende": "Lignes de champ électrostatique créées par deux charges ponctuelles qA et qB",
            "indispensable": True,
            "lisibilite": "bonne",
            "origine_figure": "enonce"
        }
    ],
    "enonce_intro_markdown": "**Exercice 2 : Application des savoirs (8 points)**",
    "questions": ex2_questions
}
print("Exercice 2 : ", len(ex2_questions), "questions")

# ============================= EXERCICE 3 =============================
ex3_questions = []

ex3_questions.append(build_question(
    numero="1.1",
    enonce_markdown=r"""**1. Effet photoélectrique (2 points)**

Une cellule photoélectrique est éclairée par une lumière monochromatique de longueur d'onde dans le vide $\lambda = 410\ nm$. La caractéristique courant-tension de cette cellule est donnée ci-dessous.

![fig-1](bac-blanc-d-ti-physique-2025-cameroun_exercice_3_fig_1.png)

1.1. Quelle est l'interprétation de $U_{AC} = 0\ V$ ?""",
    themes=["Effet photoélectrique", "Caractéristique courant-tension"],
    difficulte="moyenne",
    rappel_competence="Lecture de la caractéristique courant-tension d'une cellule photoélectrique",
    rappel_text=r"""Sur la caractéristique courant-tension d'une cellule photoélectrique, l'abscisse $U_{AC}$ représente la tension entre l'anode et la cathode (accélératrice si positive, retardatrice si négative). La valeur du courant à $U_{AC}=0$ renseigne sur le comportement des photoélectrons en l'absence de tout champ électrique accélérateur.""",
    corps_text=r"""Sur la courbe, à $U_{AC} = 0\ V$, le courant n'est pas nul : il vaut $I = 1{,}6\ \mu A$. Cela signifie qu'en l'absence de toute tension accélératrice entre l'anode et la cathode, un certain nombre de photoélectrons parviennent tout de même jusqu'à l'anode.

Cela montre que les électrons sont arrachés de la cathode avec une énergie cinétique initiale non nulle (une certaine vitesse), suffisante pour traverser seuls l'espace entre les deux électrodes, sans avoir besoin d'être accélérés par un champ électrique extérieur.""",
    piege_text=r"""Ne confonds pas $U_{AC} = 0\ V$ (absence de tension appliquée) avec $I = 0\ \mu A$ (absence de courant, qui correspond en réalité à la tension d'arrêt $U_{AC} = -0{,}8\ V$ sur cette courbe) : ce sont deux points très différents de la caractéristique, utilisés dans deux questions différentes de cet exercice.""",
    exercice_numero="3"
))

ex3_questions.append(build_question(
    numero="1.2",
    enonce_markdown=r"1.2. En utilisant la caractéristique, calculer la vitesse maximale des électrons émis par la cathode, sachant qu'ils arrivent à l'anode avec une vitesse nulle. On donne $m_e = 9{,}11\times10^{-31}\ kg$ et $e = -1{,}6\times10^{-19}\ C$.",
    themes=["Effet photoélectrique", "Tension d'arrêt", "Théorème de l'énergie cinétique"],
    difficulte="élevée",
    rappel_competence="Tension d'arrêt et énergie cinétique maximale des photoélectrons",
    rappel_text=r"""Les électrons émis avec l'énergie cinétique maximale sont ceux qui, freinés par la tension retardatrice, arrivent tout juste à l'anode avec une vitesse nulle : cette tension particulière est la tension d'arrêt $U_0$, lue comme l'abscisse du point où $I = 0$ sur la caractéristique. Le théorème de l'énergie cinétique entre la cathode et l'anode donne alors directement $E_{c,max} = |e|\,U_0$.""",
    corps_text=r"""Sur la caractéristique, le courant s'annule pour $U_{AC} = -0{,}8\ V$ : c'est la tension d'arrêt, $U_0 = 0{,}8\ V$ en valeur absolue. Les électrons émis avec la vitesse maximale $v_{max}$ à la cathode sont exactement ceux qui, freinés par cette tension, arrivent à l'anode avec une vitesse nulle.

Le théorème de l'énergie cinétique appliqué à un électron entre la cathode et l'anode s'écrit :

$$E_{c,anode} - E_{c,cathode} = W(\vec{F_{elec}})$$

$$0 - \dfrac{1}{2}m_e v_{max}^2 = e\,(V_{anode} - V_{cathode})$$

Au moment où le courant s'annule, $V_{anode} - V_{cathode} = U_{AC} = -U_0 = -0{,}8\ V$. Le travail de la force électrique, produit de deux grandeurs négatives ($e<0$ et $U_{AC}<0$), est alors positif : la force électrique s'oppose bien au mouvement de l'électron qui part de la cathode, ce qui est cohérent avec un rôle de force retardatrice. En raisonnant sur les valeurs absolues :

$$\dfrac{1}{2}m_e v_{max}^2 = |e|\,U_0$$

On isole $v_{max}$ :

$$v_{max} = \sqrt{\dfrac{2\,|e|\,U_0}{m_e}}$$

Application numérique, avec $|e| = 1{,}6\times10^{-19}\ C$, $U_0 = 0{,}8\ V$ et $m_e = 9{,}11\times10^{-31}\ kg$ :

$$v_{max} = \sqrt{\dfrac{2\times1{,}6\times10^{-19}\times0{,}8}{9{,}11\times10^{-31}}} = \sqrt{\dfrac{2{,}56\times10^{-19}}{9{,}11\times10^{-31}}} = \sqrt{2{,}81\times10^{11}}$$

$$v_{max} \approx 5{,}3\times10^{5}\ m/s$$

La vitesse maximale des électrons émis par la cathode vaut environ $v_{max} \approx 5{,}3\times10^5\ m/s$.""",
    piege_text=r"""N'utilise pas la longueur d'onde $\lambda = 410\ nm$ dans ce calcul : cette donnée permettrait de retrouver le travail d'extraction du métal via la relation d'Einstein, mais elle n'est pas nécessaire ici puisque la tension d'arrêt est directement lisible sur le graphique. Une donnée fournie dans l'énoncé général n'est pas forcément utile à chaque sous-question.""",
    conseil_text=r"""Vérifie l'ordre de grandeur : une vitesse de $5,3\times10^5\ m/s$ reste très inférieure à la vitesse de la lumière ($3\times10^8\ m/s$, soit moins de 0,2 %), ce qui justifie a posteriori l'usage de la mécanique classique (non relativiste) pour ce calcul.""",
    exercice_numero="3"
))

ex3_questions.append(build_question(
    numero="2.1",
    enonce_markdown=r"""**2. Réaction nucléaire (2 points)**

Lorsqu'un neutron frappe un noyau d'uranium 235, il se produit la réaction d'équation :

$${}^{235}_{92}U + {}^{1}_{0}n \rightarrow {}^{94}_{38}Sr + {}^{140}_{54}Xe + 2\,{}^{1}_{0}n$$

2.1. De quel type de réaction s'agit-il ?""",
    themes=["Réaction nucléaire", "Fission"],
    difficulte="faible",
    rappel_competence="Fission nucléaire provoquée",
    rappel_text=r"""Une réaction nucléaire où un noyau lourd, frappé par un neutron, se scinde en deux noyaux plus légers en libérant plusieurs neutrons est une réaction de fission nucléaire. Elle s'oppose à la fusion, où deux noyaux légers s'assemblent pour former un noyau plus lourd.""",
    corps_text=r"""Dans cette équation, le noyau lourd d'uranium 235 ($A=235$), après avoir absorbé un neutron, se scinde en deux noyaux plus légers, le strontium 94 et le xénon 140, en libérant deux neutrons supplémentaires. Un noyau lourd se brise en noyaux plus légers : c'est la signature d'une réaction de fission nucléaire, ici provoquée (induite) par l'impact d'un neutron incident.

Il s'agit d'une **réaction de fission nucléaire provoquée**.""",
    exercice_numero="3"
))

ex3_questions.append(build_question(
    numero="2.2",
    enonce_markdown=r"2.2. Les énergies de liaison par nucléon des noyaux ${}^{235}_{92}U$, ${}^{94}_{38}Sr$ et ${}^{140}_{54}Xe$ valent respectivement $E_1 = 7{,}59\ MeV$, $E_2 = 8{,}59\ MeV$ et $E_3 = 8{,}29\ MeV$. Calculer l'énergie libérée par cette réaction.",
    themes=["Énergie de liaison", "Bilan énergétique", "Fission nucléaire"],
    difficulte="élevée",
    rappel_competence="Bilan énergétique d'une réaction nucléaire à partir des énergies de liaison",
    rappel_text=r"""L'énergie libérée par une réaction nucléaire est égale à la différence entre l'énergie de liaison totale des noyaux formés et l'énergie de liaison totale des noyaux initiaux (le neutron libre n'a pas d'énergie de liaison). L'énergie de liaison totale d'un noyau s'obtient en multipliant l'énergie de liaison par nucléon par le nombre de nucléons $A$ du noyau.""",
    corps_text=r"""L'énoncé donne les énergies de liaison par nucléon (l'ordre de grandeur, quelques MeV par nucléon, ne peut correspondre qu'à une énergie par nucléon et non à une énergie de liaison totale, qui vaudrait plusieurs centaines de MeV pour ces noyaux). L'énergie de liaison totale de chaque noyau s'obtient en multipliant par son nombre de nucléons $A$ :

Énergie de liaison totale de ${}^{235}_{92}U$ :
$$E_{liaison}(U) = 235 \times 7{,}59 = 1783{,}65\ MeV$$

Énergie de liaison totale de ${}^{94}_{38}Sr$ :
$$E_{liaison}(Sr) = 94 \times 8{,}59 = 807{,}46\ MeV$$

Énergie de liaison totale de ${}^{140}_{54}Xe$ :
$$E_{liaison}(Xe) = 140 \times 8{,}29 = 1160{,}6\ MeV$$

Le neutron, particule libre, n'a pas d'énergie de liaison (il n'est lié à aucun autre nucléon avant la réaction), et les deux neutrons émis n'en ont pas non plus après la réaction.

L'énergie libérée par la réaction est la différence entre l'énergie de liaison totale des produits et celle du réactif :

$$\Delta E = \big[E_{liaison}(Sr) + E_{liaison}(Xe)\big] - E_{liaison}(U)$$

$$\Delta E = (807{,}46 + 1160{,}6) - 1783{,}65 = 1968{,}06 - 1783{,}65$$

$$\Delta E \approx 184{,}4\ MeV$$

L'énergie libérée par cette réaction de fission vaut environ $\Delta E \approx 184{,}4\ MeV$.""",
    piege_text=r"""N'oublie pas de multiplier chaque énergie de liaison par nucléon par le nombre de nucléons $A$ correspondant avant de faire la différence : soustraire directement $E_2+E_3-E_1$ (soit $8{,}59+8{,}29-7{,}59=9{,}29\ MeV$) donnerait un résultat sans signification physique, très éloigné de l'énergie réellement libérée par une fission.""",
    conseil_text=r"""184 MeV est cohérent avec l'ordre de grandeur bien connu de l'énergie libérée par la fission d'un noyau d'uranium 235 (environ 200 MeV au total, répartie entre l'énergie cinétique des fragments, des neutrons et des rayonnements) : ce repère te permet de vérifier rapidement la plausibilité de ton résultat le jour de l'examen.""",
    exercice_numero="3"
))

ex3_questions.append(build_question(
    numero="3.1",
    enonce_markdown=r"""**3. Stroboscopie (3 points)**

Un disque noir sur lequel est peinte, sous forme de croix, une figure de quatre rayons blancs équidistants, tourne à 50 tr/s. On l'éclaire à l'aide d'un stroboscope dont la fréquence des éclairs est réglable entre 50 et 250 Hz.

3.1. Calculer la fréquence de rotation $N$ du disque.""",
    themes=["Fréquence de rotation", "Stroboscopie"],
    difficulte="faible",
    rappel_competence="Fréquence de rotation d'un disque",
    rappel_text=r"""La fréquence de rotation d'un objet correspond au nombre de tours effectués par seconde. Exprimée en tours par seconde (tr/s), elle est numériquement égale à une fréquence en hertz (Hz), les deux étant des grandeurs « par seconde ».""",
    corps_text=r"""Le disque tourne à 50 tours par seconde. La fréquence de rotation est directement cette valeur, convertie en hertz :

$$N = 50\ tr/s = 50\ Hz$$""",
    conseil_text=r"""Ne complique pas une question à faible barème : ici, aucune formule à appliquer, la donnée de l'énoncé EST la réponse, il suffit de reconnaître que « tr/s » et « Hz » désignent la même grandeur pour un mouvement périodique.""",
    exercice_numero="3"
))

ex3_questions.append(build_question(
    numero="3.2",
    enonce_markdown="3.2. Pour quelles fréquences des éclairs $N_e$ le disque paraît-il immobile ?",
    themes=["Stroboscopie", "Immobilité apparente", "Symétrie d'un objet en rotation"],
    difficulte="élevée",
    rappel_competence="Condition d'immobilité apparente en stroboscopie",
    rappel_text=r"""Un disque marqué d'un motif possédant une symétrie de rotation d'ordre $n$ (ici $n=4$, la croix à quatre rayons équidistants se superpose à elle-même tous les quarts de tour) paraît immobile sous éclairage stroboscopique lorsque l'angle parcouru entre deux éclairs successifs est un multiple entier de $\dfrac{360°}{n}$. Cette condition se traduit par $N_e = \dfrac{nN}{k}$, pour $k$ entier positif.""",
    corps_text=r"""La croix à quatre rayons blancs équidistants se superpose exactement à elle-même à chaque rotation de $\dfrac{360°}{4} = 90°$ : c'est une figure à symétrie d'ordre $n=4$.

Entre deux éclairs séparés de $T_e = \dfrac{1}{N_e}$, le disque tourne d'un angle $\Delta\theta = 360° \times N \times T_e = \dfrac{360°\,N}{N_e}$. Pour que le disque paraisse immobile, cet angle doit correspondre à un nombre entier $k$ de motifs identiques, c'est-à-dire être un multiple entier de $90°$ :

$$\dfrac{360°\,N}{N_e} = k\times 90° \quad \Longrightarrow \quad N_e = \dfrac{4N}{k}, \quad k = 1, 2, 3, \ldots$$

Avec $N = 50\ Hz$ :

$$N_e = \dfrac{200}{k}\ Hz$$

On ne garde que les valeurs comprises dans la plage de réglage du stroboscope, $[50\ Hz\,;\,250\ Hz]$ :

- $k=1$ : $N_e = 200\ Hz$ (dans la plage)
- $k=2$ : $N_e = 100\ Hz$ (dans la plage)
- $k=3$ : $N_e = 66{,}7\ Hz$ (dans la plage)
- $k=4$ : $N_e = 50\ Hz$ (dans la plage, valeur limite)
- $k=5$ : $N_e = 40\ Hz$ (hors plage, exclu)

Le disque paraît immobile pour $N_e \in \{200\ Hz\,;\,100\ Hz\,;\,66{,}7\ Hz\,;\,50\ Hz\}$.""",
    piege_text=r"""L'erreur la plus fréquente est d'oublier la symétrie d'ordre 4 de la croix et d'utiliser directement $N_e = N/k$ (comme pour un objet marqué d'un seul repère) : cela ferait perdre les solutions $N_e = 200\ Hz$, $100\ Hz$ et $66,7\ Hz$, qui existent justement parce que la croix se reproduit identique à elle-même quatre fois par tour.""",
    exercice_numero="3"
))

apparent_rappel = r"""Quand la fréquence des éclairs $N_e$ est proche d'une valeur d'immobilité apparente $N_{e0} = \dfrac{4N}{k}$ sans lui être exactement égale, le disque paraît tourner lentement. Le sens apparent dépend du signe de l'écart : si l'angle parcouru entre deux éclairs est légèrement supérieur à un multiple de $90°$, la rotation apparente se fait dans le même sens que la rotation réelle ; s'il est légèrement inférieur, elle paraît inversée."""

ex3_questions.append(build_question(
    numero="3.3.1",
    enonce_markdown=r"""3.3. Qu'observe-t-on :

3.3.1. Si la fréquence des éclairs vaut $195\ Hz$ ?""",
    themes=["Stroboscopie", "Rotation apparente"],
    difficulte="élevée",
    rappel_competence="Rotation apparente lente en stroboscopie",
    rappel_text=apparent_rappel,
    corps_text=r"""$195\ Hz$ est proche de la valeur d'immobilité $N_{e0} = 200\ Hz$ (obtenue pour $k=1$ à la question 3.2), avec un écart de $5\ Hz$ en dessous.

Entre deux éclairs, le disque tourne réellement de :

$$\Delta\theta = \dfrac{360°\times N}{N_e} = \dfrac{360\times50}{195} \approx 92{,}31°$$

Cet angle dépasse de $92{,}31° - 90° = 2{,}31°$ le multiple de $90°$ le plus proche : à chaque éclair, le disque a légèrement plus tourné que ce qu'il faut pour reproduire exactement le même motif, dans le sens réel de rotation.

La fréquence apparente de cette rotation lente, au voisinage de l'harmonique $k=1$, vaut :

$$N_{app} = \left|\dfrac{k\,N_e}{4} - N\right| = \left|\dfrac{195}{4} - 50\right| = |48{,}75 - 50| = 1{,}25\ Hz$$

Le disque paraît tourner **lentement, dans le sens réel de sa rotation**, à la fréquence apparente $N_{app} = 1{,}25\ Hz$.""",
    exercice_numero="3"
))

ex3_questions.append(build_question(
    numero="3.3.2",
    enonce_markdown="3.3.2. Si la fréquence des éclairs vaut $110\\ Hz$ ?",
    themes=["Stroboscopie", "Rotation apparente"],
    difficulte="élevée",
    rappel_competence="Rotation apparente lente en stroboscopie",
    rappel_text=apparent_rappel,
    corps_text=r"""$110\ Hz$ est proche de la valeur d'immobilité $N_{e0} = 100\ Hz$ (obtenue pour $k=2$ à la question 3.2), avec un écart de $10\ Hz$ au-dessus.

Entre deux éclairs, le disque tourne réellement de :

$$\Delta\theta = \dfrac{360°\times N}{N_e} = \dfrac{360\times50}{110} \approx 163{,}64°$$

Ramené au multiple de $90°$ le plus proche (ici $2\times90° = 180°$), l'écart vaut $180° - 163{,}64° = 16{,}36°$ : le disque a tourné $16,36°$ de moins que les deux quarts de tour attendus pour reproduire le motif à l'identique. Ce déficit se traduit visuellement par un mouvement apparent en sens inverse du sens réel de rotation.

La fréquence apparente de cette rotation lente, au voisinage de l'harmonique $k=2$, vaut :

$$N_{app} = \left|\dfrac{k\,N_e}{4} - N\right| = \left|\dfrac{2\times110}{4} - 50\right| = |55 - 50| = 5\ Hz$$

Le disque paraît tourner **lentement, en sens inverse de sa rotation réelle**, à la fréquence apparente $N_{app} = 5\ Hz$.""",
    piege_text=r"""Il faut identifier, pour chaque fréquence d'éclairs donnée, l'harmonique $k$ le plus proche (ici $k=1$ pour $195\ Hz$, proche de $200\ Hz$ ; $k=2$ pour $110\ Hz$, proche de $100\ Hz$) avant d'appliquer la formule de fréquence apparente. Utiliser systématiquement $k=1$ conduirait à un résultat faux pour cette question.""",
    exercice_numero="3"
))

ex3_questions.append(build_question(
    numero="4.1",
    enonce_markdown=r"""**4. Interférences (1 point)**

On dispose d'un dispositif d'interférences constitué d'une source $S$ émettant une radiation monochromatique de longueur d'onde $\lambda = 0{,}6\ \mu m$, qui éclaire deux fentes $S_1$ et $S_2$ parallèles distantes de $a = 4\ mm$. On observe les interférences sur un écran $E$ situé à $D = 2{,}5\ m$ du plan des deux fentes.

4.1. Calculer l'interfrange $i$ du phénomène d'interférence et préciser la nature des franges dont les milieux sont situés aux points d'abscisses respectives $x_1 = 4{,}5\ mm$ et $x_2 = 6\ mm$.""",
    themes=["Interférences lumineuses", "Interfrange", "Franges d'interférence"],
    difficulte="moyenne",
    rappel_competence="Interférences à deux ondes - interfrange et nature des franges",
    rappel_text=r"""Dans le dispositif des fentes de Young, l'interfrange (distance entre deux franges brillantes ou deux franges sombres consécutives) vaut $i = \dfrac{\lambda D}{a}$. Un point d'abscisse $x$ correspond au milieu d'une frange brillante si $x = k\,i$ ($k$ entier, appelé ordre d'interférence), et au milieu d'une frange sombre si $x = (k+\tfrac12)\,i$.""",
    corps_text=r"""Calcul de l'interfrange, avec $\lambda = 0{,}6\times10^{-6}\ m$, $D = 2{,}5\ m$ et $a = 4\times10^{-3}\ m$ :

$$i = \dfrac{\lambda D}{a} = \dfrac{0{,}6\times10^{-6}\times 2{,}5}{4\times10^{-3}} = \dfrac{1{,}5\times10^{-6}}{4\times10^{-3}} = 0{,}375\times10^{-3}\ m$$

$$i = 0{,}375\ mm$$

Nature de la frange en $x_1 = 4{,}5\ mm$ : on calcule le rapport $\dfrac{x_1}{i}$ :

$$\dfrac{x_1}{i} = \dfrac{4{,}5}{0{,}375} = 12$$

12 est un entier : $x_1$ est le milieu d'une **frange brillante**, d'ordre $k=12$.

Nature de la frange en $x_2 = 6\ mm$ : on calcule le rapport $\dfrac{x_2}{i}$ :

$$\dfrac{x_2}{i} = \dfrac{6}{0{,}375} = 16$$

16 est un entier : $x_2$ est également le milieu d'une **frange brillante**, d'ordre $k=16$.

L'interfrange vaut $i = 0{,}375\ mm$ ; les points d'abscisses $x_1=4{,}5\ mm$ et $x_2=6\ mm$ sont tous deux au milieu de franges brillantes, d'ordres respectifs 12 et 16.""",
    piege_text=r"""Si le rapport $x/i$ n'était pas tombé sur un entier exact, il aurait fallu vérifier s'il tombait sur un demi-entier ($k+0,5$) pour conclure à une frange sombre : ne conclus jamais « frange brillante » ou « frange sombre » sans avoir réellement calculé et examiné ce rapport.""",
    exercice_numero="3"
))

EXERCISES["3"] = {
    "numero_exercice": "3",
    "titre": "Exercice 3 : Utilisation des savoirs",
    "points": "8",
    "figures": [
        {
            "id": "fig-1",
            "fichier": "bac-blanc-d-ti-physique-2025-cameroun_exercice_3_fig_1.png",
            "page_source": 2,
            "type": "courbe",
            "legende": "Caractéristique courant-tension I(UAC) d'une cellule photoélectrique éclairée en lumière monochromatique",
            "indispensable": True,
            "lisibilite": "bonne",
            "origine_figure": "enonce"
        }
    ],
    "enonce_intro_markdown": "**Exercice 3 : Utilisation des savoirs (8 points)**",
    "questions": ex3_questions
}
print("Exercice 3 : ", len(ex3_questions), "questions")

# ============================= EXERCICE 4 (Partie B) =============================
ex4_questions = []

ex4_questions.append(build_question(
    numero="1",
    enonce_markdown=r"""Suite aux plaintes de ses clients sur la qualité des batteries, un vendeur de pièces automobiles décide de vérifier la tension des batteries restant en stock dans son magasin. Il demande à son fils Jean, élève en classe de terminale D, de l'aider dans cette vérification.

![fig-1](bac-blanc-d-ti-physique-2025-cameroun_exercice_4_fig_1.png)

Jean réalise l'expérience suivante : il place un pendule électrostatique, constitué d'une petite boule et d'un fil isolant inextensible, entre deux plaques métalliques verticales et parallèles A et B, alimentées par l'une des batteries du stock. Sous l'effet du champ électrique entre les plaques, le fil s'écarte de la verticale d'un angle $\alpha$. La mesure de cet angle donne $\alpha = 35{,}94°$.

Données : distance entre les plaques $d = 8\ cm$ ; masse de la boule $m = 2\ g$ ; charge de la boule $q = +0{,}1\ mC$ ; intensité de la pesanteur $g = 10\ N/kg$.

**Tâche** : en exploitant cette expérience et à partir d'un raisonnement scientifique, propose la réponse que Jean doit donner à son père.""",
    themes=["Pendule électrostatique", "Équilibre d'un solide sous trois forces", "Champ électrostatique uniforme", "Démarche scientifique"],
    difficulte="élevée",
    rappel_competence="Équilibre d'un pendule électrostatique entre deux plaques - relation entre angle de déviation et tension",
    rappel_text=r"""Une boule chargée, en équilibre entre deux plaques verticales parallèles créant un champ électrostatique uniforme, est soumise à trois forces : son poids $\vec{P}$, la tension du fil $\vec{T}$, et la force électrique $\vec{F} = q\vec{E}$. À l'équilibre, ces trois forces se compensent, et l'angle $\alpha$ que fait le fil avec la verticale vérifie $\tan\alpha = \dfrac{F}{P} = \dfrac{qE}{mg}$, avec $E = \dfrac{U}{d}$ le champ uniforme entre deux plaques parallèles distantes de $d$ et soumises à la tension $U$.""",
    corps_text=r"""**Étape 1 - Bilan des forces et condition d'équilibre.**

La boule, immobile au bout du fil, est soumise à trois forces : son poids $\vec{P}$ (vertical, vers le bas, d'intensité $P = mg$), la tension du fil $\vec{T}$ (le long du fil), et la force électrique $\vec{F} = q\vec{E}$ (horizontale, puisque le champ entre deux plaques verticales parallèles est horizontal). La boule étant en équilibre, la somme de ces trois forces est nulle :

$$\vec{P} + \vec{T} + \vec{F} = \vec{0}$$

Ces trois forces forment un triangle rectangle : $\vec{P}$ est vertical, $\vec{F}$ est horizontal, et $\vec{T}$ est l'hypoténuse, inclinée de l'angle $\alpha$ par rapport à la verticale. Dans ce triangle rectangle, l'angle $\alpha$ entre le fil et la verticale vérifie :

$$\tan\alpha = \dfrac{F}{P}$$

**Étape 2 - Expression de la force électrique et du champ.**

La force électrique sur la boule chargée vaut $F = qE$, avec $E$ le champ électrostatique uniforme entre les plaques A et B, lié à la tension $U$ appliquée par $E = \dfrac{U}{d}$. On a donc :

$$\tan\alpha = \dfrac{qE}{mg} = \dfrac{qU}{mgd}$$

**Étape 3 - Isolation de la tension $U$.**

$$U = \dfrac{mgd\tan\alpha}{q}$$

**Étape 4 - Application numérique.**

Conversion des données en unités SI : $m = 2\ g = 2\times10^{-3}\ kg$ ; $d = 8\ cm = 8\times10^{-2}\ m$ ; $q = 0{,}1\ mC = 1\times10^{-4}\ C$ ; $g = 10\ N/kg$.

Calcul de $\tan(35{,}94°) \approx 0{,}725$.

$$U = \dfrac{2\times10^{-3} \times 10 \times 8\times10^{-2} \times 0{,}725}{1\times10^{-4}}$$

Calcul du numérateur, étape par étape :
$$2\times10^{-3} \times 10 = 2\times10^{-2}$$
$$2\times10^{-2} \times 8\times10^{-2} = 1{,}6\times10^{-3}$$
$$1{,}6\times10^{-3} \times 0{,}725 = 1{,}16\times10^{-3}$$

$$U = \dfrac{1{,}16\times10^{-3}}{1\times10^{-4}} = 11{,}6\ V$$

**Étape 5 - Conclusion et réponse à donner à Jean.**

La tension réellement délivrée par la batterie testée vaut environ $U \approx 11{,}6\ V$, alors que la batterie est étiquetée $12\ V$. L'écart, d'environ $0{,}4\ V$ soit un peu plus de 3 % de la valeur nominale, montre que cette batterie ne délivre pas la tension annoncée sur son étiquetage.

Jean doit donc dire à son père que la batterie testée est **défectueuse (ou déchargée)** : elle ne fournit que $11{,}6\ V$ au lieu des $12\ V$ attendus. Cela confirme les plaintes des clients sur la qualité des batteries du stock, et justifie de retirer cette batterie de la vente ou de la faire vérifier/recharger avant de la proposer à un client.

**Vérification indépendante.** En reprenant $U = 11{,}6\ V$ et en recalculant $\alpha$ dans l'autre sens : $\tan\alpha = \dfrac{qU}{mgd} = \dfrac{1\times10^{-4}\times 11{,}6}{2\times10^{-3}\times10\times8\times10^{-2}} = \dfrac{1{,}16\times10^{-3}}{1{,}6\times10^{-3}} = 0{,}725$, ce qui redonne $\alpha = \arctan(0{,}725) \approx 35{,}94°$ : cette valeur retrouve exactement l'angle mesuré expérimentalement, ce qui confirme la cohérence du résultat.""",
    piege_text=r"""Ne confonds pas la tension $U$ entre les plaques A et B (la grandeur cherchée dans ce problème) avec le champ électrique $E$ : ce sont deux grandeurs liées mais différentes, reliées par $E = U/d$. Beaucoup d'élèves isolent $E$ dans le calcul et livrent sa valeur numérique comme réponse finale, alors que la question porte sur la tension de la batterie.""",
    conseil_text=r"""Dans une situation-problème notée sur un grand nombre de points, structure toujours ta réponse en étapes explicites (bilan des forces, condition d'équilibre, mise en équation, calcul, conclusion) : chaque étape correspond généralement à une fraction du barème, même si l'énoncé ne détaille pas de sous-questions. Une réponse finale juste mais non justifiée perd la majorité des points sur ce type d'exercice.""",
    exercice_numero="4"
))

EXERCISES["4"] = {
    "numero_exercice": "4",
    "titre": "Partie B : Évaluation des compétences - Situation-problème",
    "points": "16",
    "figures": [
        {
            "id": "fig-1",
            "fichier": "bac-blanc-d-ti-physique-2025-cameroun_exercice_4_fig_1.png",
            "page_source": 3,
            "type": "schema",
            "legende": "Montage expérimental : batterie 12V reliée à deux plaques verticales A et B entre lesquelles est suspendu un pendule électrostatique dévié d'un angle alpha",
            "indispensable": False,
            "lisibilite": "bonne",
            "origine_figure": "enonce"
        }
    ],
    "enonce_intro_markdown": "**Partie B : Évaluation des compétences (16 points) - Situation-problème**",
    "questions": ex4_questions
}
print("Exercice 4 : ", len(ex4_questions), "questions")

with open("_registry_dump.json","w",encoding="utf-8") as f:
    json.dump({"exercises": EXERCISES, "rappels": RAPPELS_REGISTRY}, f, ensure_ascii=False, indent=2)
print("Registry dumped. Total rappels:", len(RAPPELS_REGISTRY))

# ============================= COURS GENERATION =============================
import re, unicodedata

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode('ascii')
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s

COURSES = {}   # cours_id -> cours dict
COURSE_FILENAMES = {}  # cours_id -> filename
USED_SLUGS = {}

def register_course_filename(competence):
    base_slug = slugify(competence)
    count = USED_SLUGS.get(base_slug, 0)
    USED_SLUGS[base_slug] = count + 1
    if count == 0:
        return base_slug
    else:
        return f"{base_slug}-{count+1}"

def build_cours(rappel_entry, titre, matiere, sous_theme, duree_estimee_min, tags,
                 accroche, prerequis, regle_titre, regle_markdown, formule_principale,
                 variantes, exemple_enonce, exemple_source, etapes, exemple_conclusion,
                 erreurs, exercices, synthese):
    slug_for_file = register_course_filename(rappel_entry["competence"])
    cours_id = f"cours-{slug_for_file}-terminale-d-ti"
    cours = {
        "cours_id": cours_id,
        "meta": {
            "titre": titre,
            "matiere": matiere,
            "serie": "D et TI",
            "sous_theme": sous_theme,
            "duree_estimee_min": duree_estimee_min,
            "tags": tags,
            "statut": "brouillon"
        },
        "source": {
            "epreuve_id": EPREUVE_ID,
            "epreuve_titre": EPREUVE_TITRE,
            "exercice_numero": rappel_entry["exercice_numero"],
            "rappel_id": rappel_entry["id"],
            "rappels_lies": [],
            "correction_id": None
        },
        "sections": [
            {"type": "accroche", "contenu_markdown": accroche.strip()},
            {"type": "prerequis", "items": prerequis},
            {"type": "regle", "titre": regle_titre, "contenu_markdown": regle_markdown.strip(),
             "formule_principale": formule_principale, "variantes": variantes},
            {"type": "exemple_resolu", "enonce_markdown": exemple_enonce.strip(),
             "epreuve_source": exemple_source, "etapes": etapes,
             "conclusion_markdown": exemple_conclusion.strip()},
            {"type": "erreurs_classiques", "items": erreurs},
            {"type": "exercices_application", "items": exercices},
            {"type": "synthese", "items_markdown": synthese}
        ]
    }
    COURSES[cours_id] = cours
    COURSE_FILENAMES[cours_id] = f"{EPREUVE_SLUG}_cours_{slug_for_file}.json"
    # write back cours_id into the exercise question's rappel
    ex_num = rappel_entry["exercice_numero"]
    q_num = rappel_entry["question_numero"]
    for q in EXERCISES[ex_num]["questions"]:
        if q["numero"] == q_num:
            for r in q["rappels_de_methode"]:
                if r["id"] == rappel_entry["id"]:
                    r["cours_id"] = cours_id
    return cours_id

def find_rappel(ex_num, q_num):
    for r in RAPPELS_REGISTRY:
        if r["exercice_numero"] == ex_num and r["question_numero"] == q_num:
            return r
    raise KeyError((ex_num, q_num))

print("Course builder ready.")

# ---------- EX1 Q1 : Definitions condensateur/stroboscopie ----------
build_cours(find_rappel("1","1"),
    titre="Condensateur et stroboscopie : définitions de base",
    matiere="Physique", sous_theme="Vocabulaire scientifique - électricité et optique",
    duree_estimee_min=15,
    tags=["condensateur", "stroboscopie", "définitions", "diélectrique"],
    accroche=r"""Avant de calculer quoi que ce soit, un examinateur du bac vérifie que tu maîtrises le vocabulaire de base. Une question de définition semble facile, mais elle fait perdre des points bêtement à qui répond de façon approximative. Ce cours te donne la méthode pour construire une définition scientifique solide, à travers deux exemples classiques du programme de physique : le condensateur et la stroboscopie.""",
    prerequis=["Notion de circuit électrique et de courant", "Notion de mouvement périodique (période, fréquence)"],
    regle_titre="Construire une définition scientifique rigoureuse",
    regle_markdown=r"""Une bonne définition scientifique répond toujours à deux exigences dans cet ordre : d'abord identifier la **nature** de l'objet ou du phénomène (à quelle catégorie il appartient), ensuite préciser sa **caractéristique essentielle** (ce qui le distingue de tout le reste). Une définition qui ne contient que des mots vagues ("c'est un truc qui sert à...") ne rapporte pas le point, même si l'idée générale est correcte.

Pour un composant électrique comme le condensateur : nature = composant électrique fait de deux armatures ; caractéristique = séparées par un isolant, capable de stocker des charges.

Pour une technique comme la stroboscopie : nature = technique d'observation ; caractéristique = éclairs périodiques permettant de figer ou ralentir un mouvement rapide.""",
    formule_principale=None,
    variantes=[],
    exemple_enonce="Définir : condensateur, stroboscopie.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Identifier la nature du condensateur", "justification":"Un condensateur appartient à la famille des composants électriques passifs.",
         "resultat_markdown":"Un condensateur est un **composant électrique** constitué de deux armatures conductrices."},
        {"numero":2, "action":"Préciser la caractéristique essentielle du condensateur", "justification":"Ce qui distingue le condensateur de tout autre composant est la présence d'un isolant entre ses armatures et sa capacité de stockage.",
         "resultat_markdown":"Les armatures sont séparées par un isolant (diélectrique) ; le condensateur emmagasine de l'énergie électrique sous forme de charges opposées sur ses deux armatures."},
        {"numero":3, "action":"Identifier la nature de la stroboscopie", "justification":"La stroboscopie appartient à la famille des techniques d'observation optique.",
         "resultat_markdown":"La stroboscopie est une **technique d'observation** d'un mouvement périodique rapide."},
        {"numero":4, "action":"Préciser la caractéristique essentielle de la stroboscopie", "justification":"Ce qui distingue cette technique est l'usage d'éclairs brefs et périodiques produits par un stroboscope.",
         "resultat_markdown":"Elle utilise des éclairs lumineux brefs et périodiques ; quand leur fréquence est adaptée à celle du mouvement, l'objet paraît immobile ou ralenti."}
    ],
    exemple_conclusion="On retient la méthode en deux temps (nature, puis caractéristique) : elle s'applique à toute question de définition en physique, quel que soit l'objet ou le phénomène demandé.",
    erreurs=[
        {"erreur_markdown":"Répondre \"un condensateur, c'est un truc qui stocke de l'électricité\" sans mentionner les armatures ni l'isolant.",
         "pourquoi_faux":"Cette phrase est vague : une pile aussi \"stocke de l'électricité\", mais ce n'est pas un condensateur. Sans la structure (armatures + isolant), la définition ne permet pas de distinguer le condensateur des autres composants.",
         "correction_markdown":"Toujours citer la structure physique de l'objet (deux armatures conductrices séparées par un isolant) avant de parler de sa fonction (stockage de charges)."},
        {"erreur_markdown":"Confondre stroboscopie et oscilloscopie, en disant que le stroboscope \"affiche une courbe sur un écran\".",
         "pourquoi_faux":"C'est l'oscilloscope qui affiche une tension sur un écran. Le stroboscope, lui, envoie des éclairs de lumière sur un objet en mouvement, sans aucun écran.",
         "correction_markdown":"Associe toujours stroboscope à \"éclairs\" et \"mouvement observé directement à l'œil\", et oscilloscope à \"écran\" et \"tension affichée\"."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Définir : dipôle électrique.",
         "solution_markdown":"Un dipôle électrique est un composant électrique possédant deux bornes de raccordement à un circuit. C'est la catégorie la plus générale : résistor, condensateur, bobine, générateur sont tous des dipôles."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Expliquer, en une ou deux phrases, pourquoi un condensateur ne laisse pas passer un courant continu établi depuis longtemps.",
         "solution_markdown":"L'espace entre les deux armatures du condensateur est occupé par un isolant : aucune charge ne peut physiquement traverser cet isolant. En régime continu établi, une fois les armatures chargées, aucun courant ne circule plus à travers le condensateur ; seul un courant transitoire (le temps de charger les armatures) a pu s'établir dans le circuit."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Un disque marqué d'un seul repère tourne à une fréquence inconnue $N$. On l'éclaire avec un stroboscope et on trouve qu'il paraît immobile pour la première fois (en partant des hautes fréquences et en diminuant) à $N_e = 80\\ Hz$. Que peut-on dire de $N$ ?",
         "solution_markdown":"Avec un seul repère ($n=1$), l'immobilité apparente a lieu pour $N_e = N/k$, $k=1,2,3,\\ldots$. La première valeur rencontrée en diminuant $N_e$ depuis les hautes fréquences correspond à $k=1$, donc $N_e = N$. On en déduit $N = 80\\ Hz$."}
    ],
    synthese=[
        "Une définition scientifique se construit en deux temps : nature de l'objet, puis caractéristique qui le distingue.",
        "Le condensateur se définit par sa structure (deux armatures, un isolant) avant sa fonction (stockage de charges).",
        "La stroboscopie se définit par sa méthode (éclairs périodiques) avant son effet (immobilité ou ralentissement apparent).",
        "Ne confonds jamais stroboscope (éclairs, observation directe) et oscilloscope (écran, tension affichée).",
        "Au bac, les questions de définition ouvrent presque toujours l'exercice de vérification des savoirs : elles sont rapides à traiter si le vocabulaire est su par cœur, mais font perdre des points inutilement sinon."
    ]
)
print("cours ex1 q1 done")

# ---------- EX1 Q2 : Loi de Laplace ----------
build_cours(find_rappel("1","2"),
    titre="La loi de Laplace",
    matiere="Physique", sous_theme="Électromagnétisme - force de Laplace",
    duree_estimee_min=20,
    tags=["loi de Laplace", "force électromagnétique", "champ magnétique", "produit vectoriel"],
    accroche=r"""Un fil parcouru par un courant, placé entre les pôles d'un aimant, se met à bouger tout seul : c'est ce phénomène qui fait tourner tous les moteurs électriques du monde. La loi de Laplace donne la formule exacte de la force responsable de ce mouvement. La connaître, c'est comprendre le principe de fonctionnement d'un haut-parleur, d'un moteur ou d'un galvanomètre.""",
    prerequis=["Notion de champ magnétique $\\vec{B}$", "Produit vectoriel de deux vecteurs (direction, sens, norme)", "Notion d'intensité de courant électrique"],
    regle_titre="Force de Laplace sur un élément de courant",
    regle_markdown=r"""Tout élément de circuit parcouru par un courant, placé dans un champ magnétique extérieur, subit une force due à ce champ. Cette force dépend de l'intensité du courant, de la longueur du conducteur, du champ magnétique, et de l'orientation relative du conducteur par rapport au champ.""",
    formule_principale=r"\vec{dF} = I\,\vec{dl} \wedge \vec{B}",
    variantes=[
        {"nom":"Norme de la force", "quand_utiliser":"Quand on veut uniquement l'intensité de la force, sans sa direction.",
         "contenu_markdown":r"$dF = I\,dl\,B\sin\theta$, où $\theta$ est l'angle entre $\vec{dl}$ (sens du courant) et $\vec{B}$. La force est maximale quand le conducteur est perpendiculaire au champ ($\theta=90°$), et nulle quand il lui est parallèle."}
    ],
    exemple_enonce="Énoncer la loi de Laplace.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Identifier les grandeurs en jeu", "justification":"La loi de Laplace relie un courant électrique et un champ magnétique à une force.",
         "resultat_markdown":"Élément de courant $I\\vec{dl}$, champ magnétique extérieur $\\vec{B}$, force résultante $\\vec{dF}$."},
        {"numero":2, "action":"Écrire la relation vectorielle", "justification":"La force de Laplace s'exprime par un produit vectoriel entre l'élément de courant et le champ.",
         "resultat_markdown":r"$\vec{dF} = I\,\vec{dl} \wedge \vec{B}$"},
        {"numero":3, "action":"Décrire la direction et le sens", "justification":"Le produit vectoriel est par définition perpendiculaire aux deux vecteurs qui le composent.",
         "resultat_markdown":"$\\vec{dF}$ est perpendiculaire au plan formé par $\\vec{dl}$ et $\\vec{B}$ ; son sens est donné par la règle de la main droite (ou règle des trois doigts)."},
        {"numero":4, "action":"Écrire la norme", "justification":"La norme d'un produit vectoriel fait intervenir le sinus de l'angle entre les deux vecteurs.",
         "resultat_markdown":r"$dF = I\,dl\,B\sin\theta$"}
    ],
    exemple_conclusion="On vient d'énoncer complètement la loi de Laplace : direction, sens et norme de la force subie par un élément de courant plongé dans un champ magnétique.",
    erreurs=[
        {"erreur_markdown":"Écrire $\\vec{F} = I\\vec{dl}\\times\\vec{B}$ en oubliant que le résultat est perpendiculaire au plan $(\\vec{dl},\\vec{B})$, et donc en essayant de l'additionner directement à $\\vec{dl}$ ou $\\vec{B}$.",
         "pourquoi_faux":"Un produit vectoriel donne toujours un vecteur perpendiculaire aux deux vecteurs de départ. Le confondre avec un vecteur dans le même plan mène à des schémas de force incorrects.",
         "correction_markdown":"Avant de tracer $\\vec{dF}$ sur un schéma, identifie d'abord le plan contenant $\\vec{dl}$ et $\\vec{B}$, puis place $\\vec{dF}$ perpendiculairement à ce plan avec la règle de la main droite."},
        {"erreur_markdown":"Confondre la loi de Laplace avec la loi de Coulomb, en disant que la loi de Laplace décrit l'attraction entre deux charges.",
         "pourquoi_faux":"La loi de Coulomb concerne l'interaction électrostatique entre deux charges au repos. La loi de Laplace concerne la force magnétique sur un courant (des charges en mouvement organisé) dans un champ magnétique : ce sont deux phénomènes physiques différents.",
         "correction_markdown":"Retiens l'association simple : Coulomb → charges immobiles, interaction électrique. Laplace → courant électrique, champ magnétique, force électromagnétique."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Un fil rectiligne de longueur $l = 20\\ cm$, parcouru par un courant $I=2\\ A$, est placé perpendiculairement à un champ magnétique uniforme $B = 0{,}5\\ T$. Calculer l'intensité de la force de Laplace qu'il subit.",
         "solution_markdown":r"Le fil est perpendiculaire au champ, donc $\theta = 90°$ et $\sin\theta = 1$. $F = I\,l\,B\sin\theta = 2\times0{,}2\times0{,}5\times1 = 0{,}2\ N$. La force de Laplace vaut $0{,}2\ N$."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Le même fil ($I=2\\ A$, $l=20\\ cm$, $B=0{,}5\\ T$) fait maintenant un angle de $30°$ avec le champ magnétique. Calculer la nouvelle force de Laplace.",
         "solution_markdown":r"$F = I\,l\,B\sin(30°) = 2\times0{,}2\times0{,}5\times0{,}5 = 0{,}1\ N$. Incliner le fil par rapport au champ réduit la force : elle passe de $0{,}2\ N$ (perpendiculaire) à $0{,}1\ N$ (à $30°$), conformément au facteur $\sin\theta$."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Un cadre rectangulaire parcouru par un courant $I$ est placé dans un champ magnétique uniforme $\\vec{B}$, avec deux côtés parallèles à $\\vec{B}$ et deux côtés perpendiculaires. Montrer que les forces de Laplace sur les côtés parallèles à $\\vec{B}$ sont nulles, et que celles sur les côtés perpendiculaires forment un couple qui tend à faire tourner le cadre.",
         "solution_markdown":r"Pour les côtés parallèles à $\vec{B}$ : l'angle entre $\vec{dl}$ et $\vec{B}$ vaut $\theta=0°$, donc $\sin\theta=0$ et $F=I\,l\,B\sin\theta=0$ : la force de Laplace y est nulle. Pour les côtés perpendiculaires à $\vec{B}$ : $\theta=90°$, la force est maximale, $F=I\,l\,B$, dirigée perpendiculairement au plan du cadre. Ces deux forces, sur les deux côtés opposés, sont de sens contraires (le courant y circule en sens opposé) : elles forment un couple de forces qui fait tourner le cadre autour de son axe. C'est le principe de fonctionnement d'un moteur électrique élémentaire."}
    ],
    synthese=[
        "La loi de Laplace donne la force subie par un courant plongé dans un champ magnétique : $\\vec{dF} = I\\vec{dl}\\wedge\\vec{B}$.",
        "La force est toujours perpendiculaire au plan formé par le conducteur et le champ magnétique.",
        "Son intensité suit $dF = I\\,dl\\,B\\sin\\theta$ : elle est maximale quand le fil est perpendiculaire au champ, nulle quand il lui est parallèle.",
        "Ne confonds jamais avec la loi de Coulomb : Laplace agit sur un courant dans un champ magnétique, Coulomb agit entre deux charges immobiles.",
        "Au bac, cette loi sert de socle à des exercices sur le moteur électrique, le haut-parleur ou le rail de Laplace : sa maîtrise qualitative (direction, sens) compte autant que le calcul numérique."
    ]
)
print("cours ex1 q2 done")

# ---------- EX1 Q3 : Champ electrostatique charge ponctuelle ----------
build_cours(find_rappel("1","3"),
    titre="Champ électrostatique créé par une charge ponctuelle",
    matiere="Physique", sous_theme="Électrostatique - champ créé par une charge ponctuelle",
    duree_estimee_min=20,
    tags=["champ électrostatique", "charge ponctuelle", "loi de Coulomb", "vecteur champ"],
    accroche=r"""Comment une charge électrique agit-elle sur son environnement, même sans contact direct avec une autre charge ? La réponse tient dans la notion de champ électrostatique : une charge modifie l'espace autour d'elle, et toute autre charge placée dans cet espace ressent une force. Ce cours te montre comment écrire, calculer et représenter ce champ pour une charge ponctuelle isolée.""",
    prerequis=["Loi de Coulomb (force entre deux charges ponctuelles)", "Notion de vecteur (direction, sens, norme)"],
    regle_titre="Champ créé par une charge ponctuelle",
    regle_markdown=r"""Une charge ponctuelle $q$ placée en un point O crée, en tout autre point P de l'espace, un champ électrostatique dont la direction est portée par la droite (OP), dont le sens dépend du signe de $q$, et dont l'intensité décroît avec le carré de la distance $OP$.

Si $q>0$, le champ "sort" de la charge : il est dirigé de O vers P (sens de $\vec{u}_{OP}$).
Si $q<0$, le champ "entre" dans la charge : il est dirigé de P vers O (sens opposé à $\vec{u}_{OP}$).""",
    formule_principale=r"\vec{E}(P) = \dfrac{1}{4\pi\varepsilon_0}\,\dfrac{q}{OP^2}\,\vec{u}_{OP}",
    variantes=[],
    exemple_enonce="Donner l'expression vectorielle du champ électrostatique créé en un point P par une charge ponctuelle q < 0 placée en un point O, puis représenter ce vecteur sur un schéma.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Écrire la formule générale du champ créé par une charge ponctuelle", "justification":"C'est la loi fondamentale de l'électrostatique pour une charge isolée.",
         "resultat_markdown":r"$\vec{E}(P) = \dfrac{1}{4\pi\varepsilon_0}\dfrac{q}{OP^2}\vec{u}_{OP}$"},
        {"numero":2, "action":"Examiner le signe du coefficient devant $\\vec{u}_{OP}$", "justification":"Le signe de $q$ détermine si $\\vec{E}$ est colinéaire ou opposé à $\\vec{u}_{OP}$.",
         "resultat_markdown":"Comme $q<0$, le coefficient $\\dfrac{q}{4\\pi\\varepsilon_0 OP^2}$ est négatif."},
        {"numero":3, "action":"En déduire le sens réel de $\\vec{E}(P)$", "justification":"Un coefficient négatif devant un vecteur unitaire inverse son sens.",
         "resultat_markdown":"$\\vec{E}(P)$ est colinéaire à $\\vec{u}_{OP}$ mais de sens opposé : il pointe de P vers O."},
        {"numero":4, "action":"Représenter le schéma", "justification":"Une réponse complète inclut la figure demandée par l'énoncé.",
         "resultat_markdown":"On place O et P, on trace $\\vec{u}_{OP}$ de O vers P, puis $\\vec{E}(P)$ sur le support de (OP) mais orienté de P vers O."}
    ],
    exemple_conclusion="Le champ créé par une charge négative pointe toujours vers cette charge : c'est la règle à retenir pour orienter correctement tout vecteur champ sans erreur de signe.",
    erreurs=[
        {"erreur_markdown":"Tracer systématiquement $\\vec{E}$ dans le sens de $\\vec{u}_{OP}$ (de la charge vers le point), quel que soit le signe de la charge.",
         "pourquoi_faux":"Ce réflexe n'est correct que pour une charge positive. Pour une charge négative, le champ est inversé : il faut vérifier le signe de $q$ avant de tracer quoi que ce soit.",
         "correction_markdown":"Avant de tracer $\\vec{E}$, écris explicitement le signe de $q$ à côté du calcul, puis déduis le sens du vecteur à partir de ce signe."},
        {"erreur_markdown":"Oublier le carré dans $OP^2$ et écrire $E = k\\dfrac{q}{OP}$.",
         "pourquoi_faux":"La loi de Coulomb (et le champ qui en découle) est une loi en inverse du carré de la distance, pas en inverse simple : c'est une propriété physique fondamentale des champs issus d'une source ponctuelle dans l'espace à trois dimensions.",
         "correction_markdown":"Mémorise la formule avec le carré explicite, et vérifie l'unité : $k$ en $N\\cdot m^2/C^2$ multiplié par une charge en $C$ et divisé par une distance au carré en $m^2$ donne bien des $N/C$, l'unité du champ électrique."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Calculer l'intensité du champ créé par une charge ponctuelle $q = 2\\ \\mu C$ à une distance $r = 30\\ cm$.",
         "solution_markdown":r"$E = k\dfrac{|q|}{r^2} = \dfrac{9\times10^9\times 2\times10^{-6}}{0{,}3^2} = \dfrac{1{,}8\times10^4}{0{,}09} = 2\times10^5\ N/C$."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Une charge ponctuelle $q = -5\\ \\mu C$ est placée en O. Représenter, en la justifiant, l'orientation du champ qu'elle crée en un point P situé à 10 cm de O, puis calculer son intensité.",
         "solution_markdown":r"Comme $q<0$, le champ en P est dirigé de P vers O (vers la charge). Intensité : $E = k\dfrac{|q|}{r^2} = \dfrac{9\times10^9\times5\times10^{-6}}{0{,}1^2} = \dfrac{4{,}5\times10^4}{0{,}01} = 4{,}5\times10^6\ N/C$."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Deux charges ponctuelles identiques $q>0$ sont placées en A et B, distantes de $2a$. Montrer qu'au milieu I du segment [AB], le champ électrostatique total est nul.",
         "solution_markdown":r"Au point I, milieu de [AB], la distance à chaque charge vaut $a$. Le champ créé par la charge en A, en I, est dirigé de A vers I (charge positive), donc vers B. Le champ créé par la charge en B, en I, est dirigé de B vers I, donc vers A : les deux champs sont donc colinéaires et de sens opposés. Comme les deux charges sont identiques et à la même distance $a$ de I, les deux champs ont la même intensité $E = k q/a^2$. La somme vectorielle de deux vecteurs opposés et de même norme est nulle : $\\vec{E}_{total}(I) = \\vec{0}$."}
    ],
    synthese=[
        "Le champ créé par une charge ponctuelle est radial : sa direction est toujours portée par la droite reliant la charge au point considéré.",
        "Son sens dépend uniquement du signe de la charge : il sort d'une charge positive, il entre dans une charge négative.",
        "Son intensité décroît en $1/r^2$ avec la distance à la charge.",
        "Avant de tracer un vecteur champ, identifie toujours le signe de la charge qui le crée : c'est la source la plus fréquente d'erreur sur ce type de question.",
        "Cette notion est le socle de tout exercice sur les lignes de champ, le potentiel électrostatique, ou le mouvement d'une charge dans un champ (comme dans l'exercice 2 et la situation-problème de cette épreuve)."
    ]
)
print("cours ex1 q3 done")

# ---------- EX1 Q4.1 : Loi de Coulomb ----------
build_cours(find_rappel("1","4.1"),
    titre="La loi de Coulomb",
    matiere="Physique", sous_theme="Électrostatique - interaction entre charges",
    duree_estimee_min=18,
    tags=["loi de Coulomb", "interaction électrique", "force électrostatique"],
    accroche=r"""Deux boules chargées se repoussent ou s'attirent sans jamais se toucher. Charles-Augustin de Coulomb a été le premier à mesurer précisément cette force et à en donner la loi mathématique, qui porte aujourd'hui son nom. C'est l'une des lois les plus citées en QCM de physique, précisément parce qu'elle se confond facilement avec d'autres lois qui lui ressemblent par leur forme.""",
    prerequis=["Notion de charge électrique (signe, unité)", "Notion de force (unité, vecteur)"],
    regle_titre="Loi de Coulomb",
    regle_markdown=r"""Deux charges ponctuelles $q_1$ et $q_2$, séparées d'une distance $r$, exercent l'une sur l'autre une force électrostatique dont l'intensité est proportionnelle au produit des charges et inversement proportionnelle au carré de la distance. Si les charges sont de même signe, la force est répulsive ; si elles sont de signes opposés, elle est attractive.""",
    formule_principale=r"F = k\dfrac{|q_1 q_2|}{r^2}, \quad k \approx 9\times10^9\ N\cdot m^2/C^2",
    variantes=[],
    exemple_enonce="La loi traduisant l'interaction entre deux particules chargées est : (a) La loi d'attraction universelle (b) La loi de Laplace (c) La loi de Coulomb.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Écarter la loi d'attraction universelle", "justification":"Cette loi décrit l'interaction gravitationnelle entre deux masses, pas entre deux charges.",
         "resultat_markdown":"La loi de Newton s'écrit $F=G\\dfrac{m_1 m_2}{r^2}$ : elle concerne des masses, pas des charges."},
        {"numero":2, "action":"Écarter la loi de Laplace", "justification":"Cette loi décrit la force sur un courant électrique placé dans un champ magnétique, pas l'interaction entre deux charges au repos.",
         "resultat_markdown":"La loi de Laplace s'écrit $\\vec{dF}=I\\vec{dl}\\wedge\\vec{B}$ : elle fait intervenir un courant et un champ magnétique, absents ici."},
        {"numero":3, "action":"Retenir la loi de Coulomb", "justification":"C'est la seule des trois lois proposées qui décrit directement l'interaction entre deux charges ponctuelles.",
         "resultat_markdown":r"$F = k\dfrac{|q_1 q_2|}{r^2}$, réponse (c)."}
    ],
    exemple_conclusion="La réponse est (c) La loi de Coulomb : c'est la seule loi, parmi les trois proposées, qui relie directement deux charges électriques entre elles.",
    erreurs=[
        {"erreur_markdown":"Confondre la loi de Coulomb avec la loi de la gravitation universelle à cause de leur ressemblance mathématique (toutes deux en $1/r^2$).",
         "pourquoi_faux":"Les deux lois ont effectivement la même forme mathématique, mais elles décrivent des interactions physiquement différentes : l'une entre masses (toujours attractive), l'autre entre charges (attractive ou répulsive selon le signe).",
         "correction_markdown":"Retiens le critère de distinction : gravitation → masses, toujours attractive. Coulomb → charges, attractive ou répulsive selon les signes."},
        {"erreur_markdown":"Oublier la valeur absolue dans la formule et donner une force négative pour deux charges de signes opposés.",
         "pourquoi_faux":"L'intensité d'une force (sa norme) est toujours positive. Le signe du produit $q_1 q_2$ renseigne seulement sur la nature attractive ou répulsive de l'interaction, pas sur l'intensité elle-même.",
         "correction_markdown":"Calcule toujours $F=k|q_1q_2|/r^2$ avec la valeur absolue, puis précise séparément si l'interaction est attractive (charges de signes opposés) ou répulsive (charges de même signe)."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Deux charges ponctuelles $q_1=3\\ \\mu C$ et $q_2=2\\ \\mu C$ sont séparées de $r=20\\ cm$. Calculer l'intensité de la force qu'elles exercent l'une sur l'autre.",
         "solution_markdown":r"$F = k\dfrac{|q_1q_2|}{r^2} = \dfrac{9\times10^9\times3\times10^{-6}\times2\times10^{-6}}{0{,}2^2} = \dfrac{5{,}4\times10^{-2}}{0{,}04} = 1{,}35\ N$."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Deux charges $q_1=-4\\ \\mu C$ et $q_2=+4\\ \\mu C$ sont séparées de $r=50\\ cm$. Préciser si la force est attractive ou répulsive, puis calculer son intensité.",
         "solution_markdown":r"Les charges sont de signes opposés : la force est attractive. $F=k\dfrac{|q_1q_2|}{r^2}=\dfrac{9\times10^9\times4\times10^{-6}\times4\times10^{-6}}{0{,}5^2}=\dfrac{1{,}44\times10^{-1}}{0{,}25}=0{,}576\ N$."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"À quelle distance faut-il placer deux charges identiques $q=1\\ \\mu C$ pour que la force de répulsion entre elles vaille exactement $9\\ N$ ?",
         "solution_markdown":r"$F=k\dfrac{q^2}{r^2} \Rightarrow r^2 = k\dfrac{q^2}{F} = \dfrac{9\times10^9\times(1\times10^{-6})^2}{9} = \dfrac{9\times10^{-3}}{9}=1\times10^{-3}\ m^2$. $r=\sqrt{1\times10^{-3}}\approx 3{,}16\times10^{-2}\ m \approx 3{,}2\ cm$."}
    ],
    synthese=[
        "La loi de Coulomb décrit l'interaction entre deux charges ponctuelles : $F=k|q_1q_2|/r^2$.",
        "Charges de même signe : répulsion. Charges de signes opposés : attraction.",
        "Ne confonds jamais avec la loi de la gravitation (masses) ni avec la loi de Laplace (courant dans un champ magnétique).",
        "La constante $k\\approx 9\\times10^9\\ N\\cdot m^2/C^2$ est à connaître par cœur, elle revient dans presque tous les calculs d'électrostatique.",
        "Cette loi fonde directement le calcul du champ créé par une charge ponctuelle, vu juste avant dans cette même épreuve."
    ]
)
print("cours ex1 q4.1 done")

# ---------- EX1 Q4.2 : Oscilloscope ----------
build_cours(find_rappel("1","4.2"),
    titre="L'oscilloscope, appareil de visualisation des signaux périodiques",
    matiere="Physique", sous_theme="Instruments de mesure - électricité",
    duree_estimee_min=15,
    tags=["oscilloscope", "signaux périodiques", "instruments de mesure"],
    accroche=r"""Comment "voir" une tension électrique qui varie des milliers de fois par seconde ? L'œil humain en est incapable seul. L'oscilloscope résout ce problème en traçant sur un écran l'évolution de cette tension au cours du temps, rendant visible ce qui reste normalement invisible.""",
    prerequis=["Notion de tension électrique", "Notion de grandeur périodique (période, fréquence)"],
    regle_titre="Fonction de l'oscilloscope",
    regle_markdown=r"""L'oscilloscope est un appareil de mesure qui affiche sur un écran l'évolution temporelle d'une tension électrique. Il permet de mesurer directement, par lecture graphique, la période, l'amplitude et la forme d'un signal périodique. Il se distingue du stroboscope, qui n'a pas d'écran et sert à observer un mouvement mécanique (pas une tension) par éclairs.""",
    formule_principale=None,
    variantes=[],
    exemple_enonce="Le dispositif qui permet de visualiser une grandeur périodique sur un écran est : a) L'oscillographe b) Le stroboscope c) L'oscilloscope.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Écarter le stroboscope", "justification":"Le stroboscope n'a pas d'écran : il éclaire directement l'objet en mouvement par flashs.",
         "resultat_markdown":"Le stroboscope sert à l'observation directe d'un mouvement mécanique, sans écran d'affichage."},
        {"numero":2, "action":"Distinguer oscillographe et oscilloscope", "justification":"L'oscillographe est un terme plus général pour tout appareil enregistreur de signal ; l'appareil précis à écran cathodique ou numérique utilisé en laboratoire est l'oscilloscope.",
         "resultat_markdown":"L'appareil couramment utilisé en TP de physique, muni d'un écran affichant la tension en temps réel, est l'oscilloscope."},
        {"numero":3, "action":"Conclure", "justification":"C'est bien l'oscilloscope qui répond exactement à la description de l'énoncé.",
         "resultat_markdown":"Réponse (c) L'oscilloscope."}
    ],
    exemple_conclusion="L'oscilloscope est l'appareil qui matérialise sur un écran une grandeur périodique, ici une tension électrique.",
    erreurs=[
        {"erreur_markdown":"Répondre \"oscillographe\" en confondant ce terme générique avec le nom précis de l'appareil de laboratoire.",
         "pourquoi_faux":"En contexte scolaire camerounais comme dans la plupart des QCM de physique, le terme technique attendu pour l'appareil à écran est \"oscilloscope\", pas \"oscillographe\" qui est un terme plus général et moins usité au lycée.",
         "correction_markdown":"Retiens le nom précis \"oscilloscope\" pour l'appareil à écran utilisé en travaux pratiques d'électricité."},
        {"erreur_markdown":"Répondre \"stroboscope\" parce que ce mot évoque aussi une observation périodique.",
         "pourquoi_faux":"Le stroboscope observe un mouvement mécanique à l'œil nu grâce à des éclairs, il ne trace rien sur un écran et ne mesure pas une tension électrique.",
         "correction_markdown":"Associe systématiquement \"écran\" à oscilloscope, et \"éclairs sur un objet en mouvement\" à stroboscope."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Citer deux grandeurs que l'on peut mesurer directement sur l'écran d'un oscilloscope.",
         "solution_markdown":"On peut mesurer la période (donc en déduire la fréquence) et l'amplitude (valeur maximale) de la tension affichée, en comptant les carreaux de l'écran et en utilisant les réglages de base de temps et de sensibilité verticale."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Sur un oscilloscope réglé avec une base de temps de $2\\ ms$ par division, un signal périodique occupe exactement 4 divisions pour une période complète. Calculer la fréquence du signal.",
         "solution_markdown":r"$T = 4\times2\ ms = 8\ ms = 8\times10^{-3}\ s$. $f = 1/T = 1/(8\times10^{-3}) = 125\ Hz$."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Expliquer pourquoi un oscilloscope ne peut pas être utilisé pour observer directement le mouvement d'un disque tournant, contrairement à un stroboscope.",
         "solution_markdown":"L'oscilloscope affiche une tension électrique en fonction du temps : il faudrait donc convertir le mouvement mécanique du disque en signal électrique (par exemple avec un capteur optique ou magnétique) avant de pouvoir l'observer sur l'écran. Le stroboscope, lui, agit directement sur la perception visuelle du mouvement réel, sans conversion électrique intermédiaire : c'est pour cela qu'il est l'outil adapté à l'observation directe d'un objet mécanique en rotation rapide."}
    ],
    synthese=[
        "L'oscilloscope affiche sur un écran l'évolution temporelle d'une tension électrique.",
        "Il permet de mesurer directement période, fréquence et amplitude d'un signal périodique.",
        "Ne le confonds pas avec le stroboscope, qui observe un mouvement mécanique par éclairs, sans écran ni mesure de tension.",
        "Au bac, ce type de QCM teste la précision du vocabulaire technique : les trois propositions se ressemblent phonétiquement mais désignent des usages différents."
    ]
)
print("cours ex1 q4.2 done")

# ---------- EX1 Q4.3 : Condensateur isolant ----------
build_cours(find_rappel("1","4.3"),
    titre="Structure d'un condensateur plan",
    matiere="Physique", sous_theme="Le condensateur - structure et rôle du diélectrique",
    duree_estimee_min=15,
    tags=["condensateur", "diélectrique", "isolant", "armatures"],
    accroche=r"""Pourquoi un condensateur peut-il garder une charge électrique stockée même après avoir été débranché du circuit qui l'a chargé ? La réponse tient dans la nature de l'espace entre ses deux armatures : ce cours explique pourquoi cet espace doit impérativement être isolant.""",
    prerequis=["Définition du condensateur (deux armatures conductrices)", "Notion de matériau conducteur et de matériau isolant"],
    regle_titre="Rôle de l'isolant entre les armatures",
    regle_markdown=r"""Un condensateur plan est constitué de deux armatures conductrices, séparées par un matériau appelé diélectrique. Ce matériau doit être isolant : c'est cette propriété qui empêche les charges positives et négatives accumulées sur les deux armatures de se neutraliser directement, et qui permet donc au condensateur de stocker durablement de l'énergie électrique sous forme de charges séparées.""",
    formule_principale=None,
    variantes=[],
    exemple_enonce="L'espace situé entre les armatures d'un condensateur est : a) Isolant b) Semi-conducteur c) Conducteur.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Examiner l'hypothèse \"conducteur\"", "justification":"Il faut tester chaque proposition en raisonnant sur ses conséquences physiques.",
         "resultat_markdown":"Si l'espace était conducteur, les charges positives et négatives des deux armatures se neutraliseraient instantanément à travers cet espace : le condensateur ne pourrait stocker aucune charge."},
        {"numero":2, "action":"Examiner l'hypothèse \"semi-conducteur\"", "justification":"Un semi-conducteur laisse partiellement passer le courant selon les conditions : ce n'est pas le comportement recherché pour un stockage durable de charges.",
         "resultat_markdown":"Un semi-conducteur permettrait une fuite progressive des charges stockées, ce qui n'est pas la propriété recherchée pour un condensateur idéal."},
        {"numero":3, "action":"Conclure sur l'isolant", "justification":"Seul un isolant empêche totalement le passage du courant entre les armatures, ce qui permet de conserver les charges séparées.",
         "resultat_markdown":"L'espace entre les armatures doit être isolant. Réponse (a)."}
    ],
    exemple_conclusion="C'est précisément parce que l'espace entre les armatures est isolant que le condensateur peut accumuler et conserver des charges électriques opposées sur ses deux plaques.",
    erreurs=[
        {"erreur_markdown":"Penser qu'un matériau conducteur entre les armatures faciliterait le stockage de charges en \"aidant\" le courant à circuler.",
         "pourquoi_faux":"Le rôle du condensateur n'est pas de laisser circuler le courant en continu, mais de séparer et stocker des charges. Un conducteur entre les armatures court-circuiterait immédiatement le condensateur.",
         "correction_markdown":"Retiens que stocker des charges nécessite de les empêcher de se recombiner : c'est le rôle exact d'un isolant, jamais d'un conducteur."},
        {"erreur_markdown":"Confondre le rôle du diélectrique avec celui d'un fil de connexion conducteur qui relie le condensateur au reste du circuit.",
         "pourquoi_faux":"Les fils de connexion (à l'extérieur du condensateur, entre ses bornes et le circuit) sont bien conducteurs, mais l'espace interne entre les deux armatures est un tout autre endroit, qui doit rester isolant.",
         "correction_markdown":"Distingue toujours l'intérieur du condensateur (armatures + isolant) de son raccordement au reste du circuit (fils conducteurs)."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Citer deux exemples de matériaux isolants couramment utilisés comme diélectrique dans un condensateur.",
         "solution_markdown":"On peut citer l'air, le papier, le mica, la céramique ou certains plastiques (polyester, polypropylène) : tous ces matériaux sont isolants et empêchent le passage direct du courant entre les armatures."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Expliquer pourquoi la capacité d'un condensateur plan augmente lorsqu'on remplace l'air entre les armatures par un diélectrique de permittivité plus élevée.",
         "solution_markdown":"La capacité d'un condensateur plan s'écrit $C=\\varepsilon \\dfrac{S}{e}$, avec $\\varepsilon$ la permittivité du diélectrique, $S$ la surface des armatures et $e$ leur écartement. Un diélectrique de permittivité $\\varepsilon$ plus élevée que celle de l'air augmente donc directement la capacité, à géométrie égale : le matériau isolant ne se contente pas d'empêcher le passage du courant, il influence aussi la quantité de charge stockable pour une tension donnée."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Un condensateur réel présente toujours une légère fuite de charge au cours du temps, même isolé de tout circuit. Expliquer d'où peut provenir cette fuite malgré la présence d'un diélectrique.",
         "solution_markdown":"Aucun isolant réel n'est parfait : un diélectrique réel possède toujours une très faible conductivité résiduelle (contrairement à un isolant idéal théorique), qui permet un lent passage de charges d'une armature à l'autre au fil du temps. C'est ce qui explique la décharge progressive et naturelle d'un condensateur réel laissé au repos, même en l'absence de tout circuit extérieur connecté."}
    ],
    synthese=[
        "Un condensateur est fait de deux armatures conductrices séparées par un isolant, le diélectrique.",
        "Cet isolant empêche les charges opposées des deux armatures de se neutraliser directement : c'est ce qui permet le stockage de charges.",
        "Un espace conducteur entre les armatures annulerait totalement la fonction de stockage du condensateur.",
        "Cette notion de structure est la base de tout calcul ultérieur de capacité, de charge ou d'énergie stockée dans un condensateur."
    ]
)
print("cours ex1 q4.3 done")

# ---------- EX1 Q4.4 : Isochronisme ----------
build_cours(find_rappel("1","4.4"),
    titre="Isochronisme, synchronisme, cohérence : vocabulaire des oscillateurs",
    matiere="Physique", sous_theme="Ondes et oscillateurs - vocabulaire",
    duree_estimee_min=15,
    tags=["isochronisme", "synchronisme", "cohérence", "sources vibrantes"],
    accroche=r"""Deux métronomes réglés sur le même tempo, deux haut-parleurs alimentés par le même générateur : ces situations se ressemblent, mais la physique distingue précisément plusieurs niveaux d'accord entre deux sources vibrantes. Ce cours clarifie trois mots que l'on confond souvent : isochrone, cohérent, synchrone.""",
    prerequis=["Notion de période et de fréquence", "Notion de phase d'un mouvement périodique"],
    regle_titre="Trois niveaux d'accord entre deux sources vibrantes",
    regle_markdown=r"""Deux sources vibrantes sont dites **isochrones** lorsqu'elles ont la même période (ou la même fréquence), sans aucune condition sur leur phase relative. Elles sont dites **cohérentes** lorsqu'en plus d'avoir la même fréquence, leur différence de phase reste constante dans le temps. Elles sont dites **synchrones** lorsque leur phase est identique à chaque instant (cas particulier de sources cohérentes en phase). Chaque notion inclut des exigences supplémentaires par rapport à la précédente.""",
    formule_principale=None,
    variantes=[],
    exemple_enonce="Deux sources vibrant avec la même période sont dites : a) Isochrones b) Cohérentes c) Synchrones.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Identifier l'information donnée par l'énoncé", "justification":"L'énoncé précise uniquement l'égalité des périodes, rien sur la phase.",
         "resultat_markdown":"Seule la condition \"même période\" est donnée, aucune information sur le déphasage."},
        {"numero":2, "action":"Écarter cohérence et synchronisme", "justification":"Ces deux notions exigent en plus une condition sur la phase, non mentionnée dans l'énoncé.",
         "resultat_markdown":"Cohérence exigerait un déphasage constant ; synchronisme exigerait une phase identique à chaque instant : aucune de ces conditions n'est donnée."},
        {"numero":3, "action":"Retenir isochronisme", "justification":"L'isochronisme est défini par la seule égalité des périodes, exactement la condition énoncée.",
         "resultat_markdown":"Réponse (a) Isochrones."}
    ],
    exemple_conclusion="Deux sources qui vibrent avec la même période, sans autre précision, sont dites isochrones : c'est la condition la plus faible des trois, donc celle qui correspond exactement à l'énoncé.",
    erreurs=[
        {"erreur_markdown":"Utiliser \"cohérentes\" et \"isochrones\" comme des synonymes interchangeables.",
         "pourquoi_faux":"La cohérence est une condition plus forte que l'isochronisme : deux sources isochrones ne sont pas nécessairement cohérentes, car rien ne garantit que leur déphasage reste constant dans le temps.",
         "correction_markdown":"Vérifie toujours ce que l'énoncé précise réellement sur la phase avant de choisir entre ces trois mots : période seule → isochrone ; déphasage constant → cohérent ; phase identique → synchrone."},
        {"erreur_markdown":"Croire que \"synchrone\" signifie simplement \"en même temps\" au sens courant, sans lien avec une égalité stricte de phase.",
         "pourquoi_faux":"En physique des ondes, synchrone a un sens précis : les deux sources doivent avoir, à chaque instant, exactement la même valeur de phase, pas seulement \"démarrer ensemble\".",
         "correction_markdown":"Réserve le mot \"synchrone\" aux cas où l'énoncé précise une identité de phase à tout instant, pas seulement un démarrage simultané."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Deux diapasons vibrent tous deux à 440 Hz, mais l'un a été mis en vibration 0,2 seconde après l'autre. Sont-ils isochrones ? Sont-ils synchrones ?",
         "solution_markdown":"Ils ont la même fréquence (440 Hz), donc la même période : ils sont isochrones. En revanche, le décalage temporel de mise en vibration introduit un déphasage entre eux qui n'est a priori pas nul à chaque instant : ils ne sont donc pas synchrones (sauf coïncidence particulière liée à la valeur exacte du décalage par rapport à la période)."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Deux sources sonores S1 et S2 sont alimentées par le même générateur basse fréquence, avec des câbles de longueurs différentes. Expliquer pourquoi elles sont cohérentes mais pas nécessairement synchrones.",
         "solution_markdown":"Les deux sources reçoivent un signal de même fréquence issu du même générateur, avec une différence de phase due à la différence de longueur des câbles : cette différence de phase reste constante dans le temps (le déphasage ne varie pas), donc les sources sont cohérentes. Mais si cette différence de phase n'est pas nulle, les deux sources ne vibrent pas exactement en phase à chaque instant : elles ne sont donc pas synchrones, bien que cohérentes."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Pourquoi la cohérence des deux sources est-elle une condition nécessaire pour observer une figure d'interférences stable (franges fixes dans le temps), alors que le simple isochronisme ne suffit pas ?",
         "solution_markdown":"Une figure d'interférences stable exige que la différence de marche entre les deux ondes, en chaque point de l'écran, reste constante dans le temps : cela nécessite que le déphasage entre les deux sources reste lui-même constant, c'est-à-dire que les sources soient cohérentes. Si les sources sont seulement isochrones (même fréquence, mais déphasage qui varie librement dans le temps), la position des franges brillantes et sombres se déplacerait continuellement, moyennée par l'œil ou le capteur : on n'observerait alors aucune figure stable, seulement un éclairement uniforme."}
    ],
    synthese=[
        "Isochrone : même période, aucune condition sur la phase.",
        "Cohérent : même fréquence, et déphasage constant dans le temps (condition plus forte que l'isochronisme).",
        "Synchrone : même phase à chaque instant (cas particulier de cohérence, avec déphasage nul).",
        "Ces trois notions sont emboîtées par exigence croissante : synchronisme implique cohérence, qui implique isochronisme, mais pas l'inverse.",
        "Au bac, un QCM sur ce vocabulaire teste la lecture précise de l'énoncé : ne choisis jamais un mot plus fort que ce que les données autorisent réellement à conclure."
    ]
)
print("cours ex1 q4.4 done")

# ---------- EX1 Q5.1 : Conditions emission photoelectrique ----------
build_cours(find_rappel("1","5.1"),
    titre="Conditions de l'émission photoélectrique",
    matiere="Physique", sous_theme="Physique quantique - effet photoélectrique",
    duree_estimee_min=20,
    tags=["effet photoélectrique", "fréquence seuil", "photon", "travail d'extraction"],
    accroche=r"""Éclairer un métal avec une lumière très intense mais rouge n'arrache aucun électron, alors qu'une lumière violette, même faible, y parvient instantanément. Ce résultat, inexplicable par la physique ondulatoire classique, a conduit Einstein à proposer la notion de photon. Ce cours explique pourquoi c'est la couleur (la fréquence) de la lumière qui compte, pas sa puissance.""",
    prerequis=["Notion de fréquence et longueur d'onde d'une onde lumineuse", "Notion d'énergie cinétique"],
    regle_titre="Condition d'existence de l'effet photoélectrique",
    regle_markdown=r"""L'effet photoélectrique (arrachement d'électrons d'un métal par la lumière) n'a lieu que si la fréquence $\nu$ de la lumière incidente est supérieure ou égale à une fréquence seuil $\nu_0$, caractéristique du métal éclairé (liée à son travail d'extraction $W_0$ par $W_0 = h\nu_0$). En dessous de ce seuil, aucun électron n'est arraché, quelle que soit la puissance de la lumière reçue. Au-dessus du seuil, augmenter la puissance lumineuse augmente uniquement le nombre d'électrons arrachés par seconde (l'intensité du courant photoélectrique), pas l'énergie cinétique maximale de chaque électron, qui ne dépend que de la fréquence.""",
    formule_principale=r"E_{c,max} = h\nu - W_0, \quad \text{condition d'émission : } \nu \geq \nu_0",
    variantes=[],
    exemple_enonce="Répondre par vrai ou faux : l'émission photoélectrique dépend de la puissance de la lumière.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Distinguer existence de l'émission et intensité du courant", "justification":"Ce sont deux questions physiques différentes, gouvernées par deux paramètres différents de la lumière.",
         "resultat_markdown":"Existence de l'émission : dépend de la fréquence. Intensité du courant si émission il y a : dépend de la puissance."},
        {"numero":2, "action":"Appliquer la condition de seuil", "justification":"L'émission n'existe que si $\\nu \\geq \\nu_0$, indépendamment de la puissance lumineuse.",
         "resultat_markdown":"Même une lumière extrêmement puissante, mais de fréquence inférieure à $\\nu_0$, n'arrache aucun électron."},
        {"numero":3, "action":"Conclure sur l'affirmation", "justification":"L'affirmation attribue à la puissance un rôle qui revient en réalité à la fréquence.",
         "resultat_markdown":"L'affirmation est fausse : c'est la fréquence, pas la puissance, qui conditionne l'existence de l'émission photoélectrique."}
    ],
    exemple_conclusion="On retient que la puissance lumineuse gouverne seulement le nombre d'électrons arrachés par seconde, jamais le fait même que l'émission ait lieu ni l'énergie cinétique maximale des électrons émis.",
    erreurs=[
        {"erreur_markdown":"Penser qu'une lumière plus intense (plus puissante) finira toujours par arracher des électrons si on augmente suffisamment la puissance.",
         "pourquoi_faux":"C'est l'erreur historique que l'effet photoélectrique a justement révélée : en dessous du seuil de fréquence, aucune puissance, même très élevée, ne permet d'arracher un seul électron. L'énergie d'un photon dépend de sa fréquence ($E=h\\nu$), pas du nombre de photons envoyés par seconde.",
         "correction_markdown":"Retiens que chaque photon agit individuellement sur un électron : un photon d'énergie insuffisante ($h\\nu < W_0$) ne peut jamais arracher un électron, même en en envoyant un très grand nombre par seconde."},
        {"erreur_markdown":"Penser que l'énergie cinétique maximale des électrons émis dépend de la puissance de la lumière.",
         "pourquoi_faux":"L'énergie cinétique maximale ne dépend que de la fréquence de la lumière ($E_{c,max}=h\\nu-W_0$) : augmenter la puissance ajoute des photons identiques, donc plus d'électrons arrachés avec la même énergie cinétique maximale chacun, pas des électrons plus rapides.",
         "correction_markdown":"Sépare toujours mentalement deux effets : fréquence → énergie de chaque photon → vitesse maximale des électrons ; puissance → nombre de photons par seconde → nombre d'électrons arrachés, donc intensité du courant."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Une lumière de fréquence $\\nu$ inférieure à la fréquence seuil $\\nu_0$ d'un métal éclaire ce métal avec une puissance très élevée. Y a-t-il émission photoélectrique ?",
         "solution_markdown":"Non. La condition $\\nu \\geq \\nu_0$ n'est pas remplie : aucun électron n'est arraché, quelle que soit la puissance de la lumière incidente."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"On double la puissance d'une lumière de fréquence $\\nu > \\nu_0$ éclairant une cellule photoélectrique. Que devient le courant de saturation ? Que devient l'énergie cinétique maximale des électrons émis ?",
         "solution_markdown":"Doubler la puissance double le nombre de photons reçus par seconde, donc double le nombre d'électrons arrachés par seconde : le courant de saturation double. L'énergie cinétique maximale des électrons émis, en revanche, ne change pas : elle ne dépend que de la fréquence $\\nu$ (inchangée ici), pas de la puissance."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Le travail d'extraction d'un métal vaut $W_0 = 2\\ eV$. Une lumière de longueur d'onde $\\lambda = 400\\ nm$ l'éclaire. Y a-t-il émission photoélectrique ? Justifier par un calcul, sachant $h=6{,}63\\times10^{-34}\\ J\\cdot s$, $c=3\\times10^8\\ m/s$ et $1\\ eV = 1{,}6\\times10^{-19}\\ J$.",
         "solution_markdown":r"Énergie d'un photon : $E=h\dfrac{c}{\lambda}=\dfrac{6{,}63\times10^{-34}\times3\times10^8}{400\times10^{-9}}=\dfrac{1{,}989\times10^{-25}}{4\times10^{-7}}\approx4{,}97\times10^{-19}\ J$. Conversion en eV : $E \approx \dfrac{4{,}97\times10^{-19}}{1{,}6\times10^{-19}} \approx 3{,}11\ eV$. Comme $E=3{,}11\ eV > W_0=2\ eV$, l'énergie du photon dépasse le travail d'extraction : il y a émission photoélectrique."}
    ],
    synthese=[
        "L'émission photoélectrique n'existe que si la fréquence de la lumière dépasse une fréquence seuil propre au métal.",
        "La puissance de la lumière ne joue aucun rôle sur l'existence de l'émission, seulement sur le nombre d'électrons arrachés par seconde.",
        "L'énergie cinétique maximale des électrons émis ne dépend que de la fréquence : $E_{c,max}=h\\nu-W_0$.",
        "Ce résultat historique (inexplicable par la physique ondulatoire classique) a conduit à la notion de photon, grain d'énergie $E=h\\nu$.",
        "Au bac, cette distinction fréquence/puissance revient très souvent en question de cours ou en vrai-faux : c'est un piège classique à bien maîtriser."
    ]
)
print("cours ex1 q5.1 done")

# ---------- EX1 Q5.2 : Virage equilibre ----------
build_cours(find_rappel("1","5.2"),
    titre="Équilibre et mouvement circulaire d'un véhicule en virage",
    matiere="Physique", sous_theme="Mécanique - mouvement circulaire, dynamique du point",
    duree_estimee_min=20,
    tags=["virage", "mouvement circulaire", "force centripète", "deuxième loi de Newton"],
    accroche=r"""Pourquoi une voiture qui roule trop vite dans un virage risque-t-elle de déraper vers l'extérieur ? La réponse tient à une exigence physique simple mais souvent mal comprise : pour changer de direction, un véhicule a besoin d'une force résultante non nulle, dirigée vers le centre du virage. Ce cours explique pourquoi cette exigence interdit que la réaction du sol et le poids soient alignés pendant un virage.""",
    prerequis=["Deuxième loi de Newton", "Notion de mouvement circulaire et d'accélération centripète"],
    regle_titre="Condition dynamique d'un virage réussi",
    regle_markdown=r"""Un véhicule qui prend un virage décrit une trajectoire circulaire (ou approximativement circulaire) : il subit donc une accélération centripète, dirigée vers le centre du virage. D'après la deuxième loi de Newton, la résultante des forces appliquées au véhicule doit donc elle aussi être dirigée vers ce centre, donc posséder une composante horizontale non nulle. Le poids étant vertical, cette composante horizontale ne peut provenir que de la réaction du sol (via l'adhérence des pneus ou l'inclinaison de la chaussée) : réaction et poids ne peuvent donc pas avoir la même droite d'action pendant un virage.""",
    formule_principale=r"\sum \vec{F} = m\vec{a}_{centripète}, \quad \vec{a}_{centripète} \text{ dirigée vers le centre du virage}",
    variantes=[],
    exemple_enonce="Répondre par vrai ou faux : pour qu'un virage soit réussi, il faut que la réaction et le poids aient la même droite d'action.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Analyser le cas où R et P sont colinéaires", "justification":"Il faut examiner ce que cette hypothèse impliquerait pour le mouvement.",
         "resultat_markdown":"Si $\\vec{R}$ et $\\vec{P}$ avaient la même droite d'action, leur résultante serait verticale (ou nulle) : aucune force horizontale ne s'exercerait sur le véhicule."},
        {"numero":2, "action":"Relier à la deuxième loi de Newton", "justification":"Un virage exige une accélération centripète, donc une résultante des forces non nulle et horizontale.",
         "resultat_markdown":"Sans force horizontale résultante, l'accélération centripète serait nulle : le véhicule ne pourrait pas changer de direction, il irait tout droit."},
        {"numero":3, "action":"Conclure sur l'affirmation", "justification":"L'affirmation décrit en réalité la condition d'un mouvement rectiligne, pas d'un virage réussi.",
         "resultat_markdown":"L'affirmation est fausse : un virage réussi exige au contraire que $\\vec{R}$ et $\\vec{P}$ ne soient pas colinéaires."}
    ],
    exemple_conclusion="Le cas où réaction et poids sont alignés correspond exactement à l'absence de virage (résultante nulle, trajectoire rectiligne) : c'est l'opposé de la situation décrite par l'énoncé.",
    erreurs=[
        {"erreur_markdown":"Penser que \"équilibre des forces\" (réaction qui compense le poids) est toujours une condition favorable, y compris pour un virage.",
         "pourquoi_faux":"Un équilibre parfait entre réaction et poids correspond à une résultante nulle, donc à une accélération nulle : c'est la condition d'un mouvement rectiligne uniforme (ou de l'immobilité), pas d'un changement de direction.",
         "correction_markdown":"Distingue toujours \"équilibre\" (résultante nulle, pas d'accélération) et \"virage\" (résultante non nulle, accélération centripète) : ce sont deux situations dynamiques opposées."},
        {"erreur_markdown":"Oublier que c'est la réaction du sol, et non le poids, qui fournit la force horizontale nécessaire au virage.",
         "pourquoi_faux":"Le poids reste toujours vertical, quelle que soit la situation : il ne peut jamais fournir directement de composante horizontale. Toute force horizontale provient nécessairement d'une autre force, ici la réaction du sol (adhérence, inclinaison de la route).",
         "correction_markdown":"Dans un bilan de forces pour un virage, identifie systématiquement quelle force fournit la composante horizontale : ce n'est jamais le poids seul."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Un véhicule roule en ligne droite à vitesse constante sur une route horizontale. Que peut-on dire de la droite d'action de la réaction du sol et du poids ?",
         "solution_markdown":"En ligne droite à vitesse constante, l'accélération est nulle, donc la résultante des forces est nulle : la réaction du sol et le poids sont alors directement opposés, sur la même droite d'action verticale."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Un véhicule de masse $m=1000\\ kg$ prend un virage de rayon $R=50\\ m$ à la vitesse $v=54\\ km/h$ sur une route plate. Calculer l'intensité de la force horizontale nécessaire pour effectuer ce virage.",
         "solution_markdown":r"Conversion : $v=54\ km/h = 15\ m/s$. Force centripète nécessaire : $F=\dfrac{mv^2}{R}=\dfrac{1000\times15^2}{50}=\dfrac{1000\times225}{50}=4500\ N$. Cette force horizontale doit être fournie par l'adhérence des pneus sur la route (composante horizontale de la réaction du sol)."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Expliquer pourquoi les virages routiers sont souvent inclinés (relevés) vers l'intérieur du virage, en lien avec la condition d'équilibre étudiée dans ce cours.",
         "solution_markdown":"Sur une route plate, seule l'adhérence (le frottement entre pneus et chaussée) peut fournir la composante horizontale nécessaire au virage, ce qui limite la vitesse maximale avant dérapage. En inclinant la route vers l'intérieur du virage, la réaction normale du sol elle-même n'est plus verticale : elle acquiert naturellement une composante horizontale dirigée vers le centre du virage, en plus (ou à la place) de l'adhérence. Cela permet de fournir une partie ou la totalité de la force centripète nécessaire sans dépendre uniquement du frottement, ce qui rend le virage réalisable à plus haute vitesse, en toute sécurité."}
    ],
    synthese=[
        "Un virage correspond à un mouvement circulaire, donc à une accélération centripète dirigée vers le centre.",
        "D'après la deuxième loi de Newton, cette accélération exige une résultante des forces non nulle, elle aussi dirigée vers le centre.",
        "Le poids étant toujours vertical, la composante horizontale nécessaire provient de la réaction du sol : réaction et poids ne peuvent donc pas être colinéaires pendant un virage.",
        "Réaction et poids colinéaires correspond en réalité à une résultante nulle, donc à un mouvement rectiligne uniforme (ou à l'immobilité), pas à un virage.",
        "Cette notion revient régulièrement dans les exercices sur les manèges, les virages routiers relevés, ou tout mobile en trajectoire circulaire : le réflexe à avoir est toujours de chercher qui fournit la composante horizontale de la résultante."
    ]
)
print("cours ex1 q5.2 done")

# ---------- EX2 Q1.1 : Champ uniforme ----------
build_cours(find_rappel("2","1.1"),
    titre="Caractériser un champ électrostatique uniforme à partir des lignes de champ",
    matiere="Physique", sous_theme="Électrostatique - cartes de champ",
    duree_estimee_min=15,
    tags=["champ uniforme", "lignes de champ", "condensateur plan"],
    accroche=r"""Une carte de lignes de champ ressemble parfois à un dessin abstrait, mais chaque détail (courbure, écartement, direction) porte une information physique précise. Ce cours t'apprend à lire une carte de champ pour décider, d'un simple coup d'œil argumenté, si le champ représenté est uniforme ou non.""",
    prerequis=["Notion de vecteur champ électrostatique", "Notion de ligne de champ (courbe tangente au vecteur E en chaque point)"],
    regle_titre="Reconnaître un champ uniforme sur une carte de lignes de champ",
    regle_markdown=r"""Un champ électrostatique est uniforme lorsque le vecteur $\vec{E}$ garde la même direction, le même sens et la même intensité en tout point de la région considérée. Sur une carte de lignes de champ, cette propriété se traduit visuellement par des lignes **parallèles** entre elles et **équidistantes** (également espacées) : c'est le cas typique entre les deux plaques d'un condensateur plan, loin des bords. Dès que les lignes sont courbes, convergentes, divergentes, ou inégalement espacées, le champ n'est pas uniforme.""",
    formule_principale=None,
    variantes=[],
    exemple_enonce="Deux charges ponctuelles qA et qB sont fixées en A et B. La figure représente quelques lignes de champ produites par la source (qA, qB). Ce champ est-il uniforme ? Justifier.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Observer la forme des lignes", "justification":"La première caractéristique à examiner sur une carte de champ est la rectitude ou la courbure des lignes.",
         "resultat_markdown":"Les lignes issues de deux charges ponctuelles sont courbes, pas rectilignes."},
        {"numero":2, "action":"Observer l'espacement des lignes", "justification":"L'écartement des lignes traduit l'intensité locale du champ : des lignes resserrées indiquent un champ plus intense.",
         "resultat_markdown":"Les lignes se resserrent près de chaque charge et s'écartent en s'en éloignant : l'espacement n'est pas constant."},
        {"numero":3, "action":"Conclure sur l'uniformité", "justification":"Un champ uniforme exige simultanément rectitude et équidistance des lignes.",
         "resultat_markdown":"Aucune des deux conditions n'est remplie : le champ n'est pas uniforme."}
    ],
    exemple_conclusion="Une carte de champ courbe et à espacement variable signale toujours un champ non uniforme : c'est le cas de toute source formée de charges ponctuelles, contrairement au condensateur plan.",
    erreurs=[
        {"erreur_markdown":"Conclure \"champ uniforme\" simplement parce que la figure paraît symétrique.",
         "pourquoi_faux":"La symétrie d'une figure ne garantit pas l'uniformité du champ : deux charges identiques donnent une carte symétrique, mais avec des lignes courbes et un champ d'intensité variable, donc non uniforme.",
         "correction_markdown":"Vérifie toujours les deux critères précis (lignes parallèles ET équidistantes), pas une impression générale de régularité ou de symétrie."},
        {"erreur_markdown":"Confondre \"champ uniforme\" avec \"champ constant dans le temps\".",
         "pourquoi_faux":"Uniforme qualifie une répartition dans l'espace (même valeur en tout point à un instant donné), pas une évolution dans le temps. Un champ peut être uniforme et varier dans le temps, ou non uniforme et constant dans le temps.",
         "correction_markdown":"Réserve le mot \"uniforme\" à une comparaison entre différents points de l'espace, à un instant donné."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Entre les deux plaques planes et parallèles d'un condensateur, loin des bords, les lignes de champ sont rectilignes et équidistantes. Ce champ est-il uniforme ?",
         "solution_markdown":"Oui : lignes rectilignes et équidistantes sont exactement les deux critères d'un champ uniforme."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Une carte de champ présente des lignes parallèles entre elles, mais dont l'écartement diminue progressivement d'une région à l'autre. Ce champ est-il uniforme ?",
         "solution_markdown":"Non. Bien que les lignes soient parallèles (direction constante), leur espacement variable indique que l'intensité du champ change d'une région à l'autre : le champ n'est donc pas uniforme, malgré le parallélisme des lignes."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Près des bords d'un condensateur plan réel (effets de bord), les lignes de champ se courbent, contrairement à la zone centrale. Expliquer ce que cela implique pour l'hypothèse de champ uniforme utilisée dans les calculs de cours.",
         "solution_markdown":"L'hypothèse de champ uniforme entre les plaques d'un condensateur n'est rigoureusement valable que loin des bords, là où les lignes restent effectivement parallèles et équidistantes. Près des bords, la courbure des lignes traduit une perte d'uniformité locale (effets de bord) : les formules usuelles ($E=U/d$ constant partout) deviennent alors approximatives. Dans la plupart des exercices de terminale, on suppose implicitement que les dimensions des plaques sont grandes devant leur écartement, ce qui rend les effets de bord négligeables et justifie l'hypothèse de champ uniforme sur toute la zone utile."}
    ],
    synthese=[
        "Un champ uniforme a même direction, même sens et même intensité en tout point de la région considérée.",
        "Sur une carte de champ, cela se traduit par des lignes rectilignes ET équidistantes.",
        "Toute courbure ou tout espacement variable des lignes signale un champ non uniforme.",
        "Le champ créé par une ou plusieurs charges ponctuelles n'est jamais uniforme ; celui d'un condensateur plan (loin des bords) l'est.",
        "Cette lecture de carte de champ précède presque toujours, au bac, une question sur le signe des charges qui créent ce champ."
    ]
)
print("cours ex2 q1.1 done")

# ---------- EX2 Q1.2 : Signe charge lignes de champ ----------
build_cours(find_rappel("2","1.2"),
    titre="Signe d'une charge à partir de l'orientation des lignes de champ",
    matiere="Physique", sous_theme="Électrostatique - lecture d'une carte de champ",
    duree_estimee_min=15,
    tags=["signe d'une charge", "lignes de champ", "champ électrostatique"],
    accroche=r"""Sur une carte de lignes de champ, chaque flèche encode une information : le sens du vecteur champ électrostatique en ce point. En observant simplement où les flèches pointent au voisinage d'une charge, on peut déterminer son signe sans aucun calcul. Ce cours te donne cette méthode de lecture directe.""",
    prerequis=["Notion de ligne de champ orientée", "Champ créé par une charge ponctuelle (sort d'une charge positive, entre dans une charge négative)"],
    regle_titre="Lire le signe d'une charge sur une carte de champ",
    regle_markdown=r"""Une ligne de champ est orientée dans le sens du vecteur $\vec{E}$ en chacun de ses points. Une charge positive est toujours une **source** de lignes de champ (les flèches en sortent), une charge négative est toujours un **puits** de lignes de champ (les flèches y entrent). Il suffit donc d'observer le sens des flèches au voisinage immédiat de la charge, sans se préoccuper de la forme globale du faisceau de lignes.""",
    formule_principale=None,
    variantes=[],
    exemple_enonce="Sur la figure de l'exercice, déterminer les signes de qA et de qB. Justifier.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Observer le sens des flèches au voisinage de qA", "justification":"C'est ce sens local qui donne directement le signe de la charge.",
         "resultat_markdown":"Les flèches s'éloignent de qA dans toutes les directions."},
        {"numero":2, "action":"Observer le sens des flèches au voisinage de qB", "justification":"On applique la même méthode pour la seconde charge.",
         "resultat_markdown":"Les flèches s'éloignent également de qB dans toutes les directions."},
        {"numero":3, "action":"Conclure sur les signes", "justification":"Un champ qui sort d'une charge signale une charge positive.",
         "resultat_markdown":"qA et qB sont toutes deux positives."}
    ],
    exemple_conclusion="Le sens local des flèches suffit à déterminer le signe de chaque charge, sans avoir besoin d'analyser la forme globale de la carte de champ.",
    erreurs=[
        {"erreur_markdown":"Se laisser guider par la forme globale de la carte (par exemple penser \"les lignes semblent aller de A vers B, donc A est positive et B négative\") plutôt que par le sens local des flèches près de chaque charge.",
         "pourquoi_faux":"Pour deux charges de même signe, les lignes entre elles peuvent sembler se rapprocher visuellement sans qu'aucune ligne ne relie réellement les deux charges : seul le sens précis des flèches, observé tout près de chaque charge, donne l'information correcte.",
         "correction_markdown":"Zoome mentalement sur chaque charge séparément et regarde uniquement le sens des flèches à son contact immédiat, en ignorant la forme d'ensemble du faisceau."},
        {"erreur_markdown":"Croire qu'une ligne de champ qui relie directement deux charges signifie qu'elles sont de signes opposés.",
         "pourquoi_faux":"C'est vrai en général (une ligne va d'une charge positive à une charge négative), mais il ne faut pas conclure à l'inverse que l'absence de ligne reliant deux charges signifie qu'elles ont le même signe : il faut vérifier le sens des flèches, pas seulement la présence ou l'absence d'une ligne reliant les deux points.",
         "correction_markdown":"Base toujours ta conclusion sur le sens des flèches observées, jamais sur une impression de connexion visuelle entre deux charges."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Sur une carte de champ, toutes les lignes convergent vers une charge ponctuelle q, flèches pointant vers elle. Quel est le signe de q ?",
         "solution_markdown":"Les flèches entrent dans la charge : q est négative."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Deux charges qA et qB sont représentées avec des lignes de champ qui partent de qA et entrent dans qB. Déterminer les signes de qA et qB.",
         "solution_markdown":"Les lignes sortent de qA : qA est positive. Les lignes entrent dans qB : qB est négative. C'est la configuration typique d'un dipôle électrostatique (deux charges opposées)."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Expliquer pourquoi, pour deux charges de signes opposés et de même valeur absolue, certaines lignes de champ relient directement les deux charges, alors que pour deux charges de même signe, aucune ligne ne les relie jamais directement.",
         "solution_markdown":"Une ligne de champ part toujours d'une charge positive et arrive toujours sur une charge négative (ou part vers/vient de l'infini). Pour deux charges de signes opposés, il existe donc des lignes qui partent effectivement de la charge positive pour arriver directement sur la charge négative, reliant les deux charges. Pour deux charges de même signe (toutes deux positives, par exemple), toute ligne partant de l'une des charges ne peut pas se terminer sur l'autre (qui est également une source, pas un puits) : les lignes issues des deux charges se repoussent mutuellement et divergent vers l'infini, sans jamais relier directement les deux charges entre elles."}
    ],
    synthese=[
        "Une ligne de champ est orientée dans le sens du vecteur E.",
        "Une charge positive est une source de lignes de champ (flèches sortantes) ; une charge négative est un puits (flèches entrantes).",
        "Le signe d'une charge se lit directement sur le sens des flèches à son voisinage immédiat, sans analyser la carte globale.",
        "Deux charges de même signe : aucune ligne ne les relie directement. Deux charges de signes opposés : certaines lignes vont directement de l'une à l'autre.",
        "Cette lecture graphique revient très souvent après une question sur l'uniformité du champ, comme dans cet exercice."
    ]
)
print("cours ex2 q1.2 done")

# ---------- EX2 Q1.3 : Champ cree par charge ponctuelle - calcul distance ----------
build_cours(find_rappel("2","1.3"),
    titre="Calculer une distance à partir du champ créé par une charge ponctuelle",
    matiere="Physique", sous_theme="Électrostatique - calculs sur le champ d'une charge ponctuelle",
    duree_estimee_min=20,
    tags=["champ électrostatique", "loi de Coulomb", "calcul inverse", "distance"],
    accroche=r"""Connaître l'intensité d'un champ électrostatique en un point permet de remonter à la distance qui sépare ce point de la charge qui le crée : c'est un calcul inverse très fréquent au bac, qui demande simplement de manipuler correctement la formule du champ d'une charge ponctuelle.""",
    prerequis=["Formule du champ créé par une charge ponctuelle", "Manipulation d'une équation avec un carré et une racine carrée"],
    regle_titre="Isoler la distance dans la formule du champ",
    regle_markdown=r"""Le champ créé par une charge ponctuelle $q$ à une distance $r$ vaut $E=k\dfrac{|q|}{r^2}$. Connaissant $E$ et $|q|$, on isole $r^2$ puis on prend la racine carrée pour obtenir $r$. Il faut impérativement travailler en unités SI (charge en coulombs, distance en mètres, champ en $N/C$) pour que le résultat soit directement exploitable.""",
    formule_principale=r"r = \sqrt{k\dfrac{|q|}{E}}",
    variantes=[],
    exemple_enonce="Calculer la distance d entre les charges A et B sachant que le champ créé par la charge A au point B vaut E = 9x10^5 N/C et que |qA|=|qB|=1 µC.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Écrire la formule du champ", "justification":"Point de départ obligatoire de tout calcul impliquant le champ d'une charge ponctuelle.",
         "resultat_markdown":r"$E = k\dfrac{|q_A|}{d^2}$"},
        {"numero":2, "action":"Isoler d²", "justification":"On multiplie les deux membres par $d^2$ puis on divise par $E$.",
         "resultat_markdown":r"$d^2 = k\dfrac{|q_A|}{E}$"},
        {"numero":3, "action":"Faire l'application numérique de d²", "justification":"On substitue les valeurs en unités SI.",
         "resultat_markdown":r"$d^2 = \dfrac{9\times10^9\times1\times10^{-6}}{9\times10^5} = 1\times10^{-2}\ m^2$"},
        {"numero":4, "action":"Prendre la racine carrée", "justification":"La question demande la distance d, pas d².",
         "resultat_markdown":r"$d = \sqrt{1\times10^{-2}} = 0{,}1\ m$"}
    ],
    exemple_conclusion="On obtient d = 0,1 m = 10 cm : la méthode d'isolement puis de racine carrée s'applique à tout calcul inverse de ce type.",
    erreurs=[
        {"erreur_markdown":"S'arrêter à $d^2 = 10^{-2}\\ m^2$ et donner cette valeur comme réponse finale.",
         "pourquoi_faux":"La question demande la distance $d$, pas son carré. Oublier l'étape finale de racine carrée est l'erreur la plus fréquente sur ce type de calcul.",
         "correction_markdown":"Relis toujours la question juste avant de conclure : si elle demande $d$, vérifie que ta dernière ligne de calcul contient bien $d$ et pas $d^2$."},
        {"erreur_markdown":"Utiliser $|q_A|$ en microcoulombs directement dans la formule sans le convertir en coulombs.",
         "pourquoi_faux":"La constante $k=9\\times10^9$ est définie pour des charges en coulombs (unité SI). Utiliser une valeur en µC sans conversion donnerait un résultat numérique complètement faux, décalé d'un facteur $10^6$.",
         "correction_markdown":"Convertis systématiquement toutes les données en unités SI avant de substituer dans une formule physique : $1\\ \\mu C = 1\\times10^{-6}\\ C$."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Une charge $q=2\\ \\mu C$ crée un champ $E=5\\times10^4\\ N/C$ à une distance $r$. Calculer $r$.",
         "solution_markdown":r"$r^2 = k\dfrac{|q|}{E} = \dfrac{9\times10^9\times2\times10^{-6}}{5\times10^4} = \dfrac{1{,}8\times10^4}{5\times10^4} = 0{,}36\ m^2$. $r=\sqrt{0{,}36}=0{,}6\ m$."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"À quelle distance d'une charge $q=0{,}5\\ \\mu C$ le champ créé vaut-il exactement $2\\times10^6\\ N/C$ ?",
         "solution_markdown":r"$r^2=k\dfrac{|q|}{E}=\dfrac{9\times10^9\times0{,}5\times10^{-6}}{2\times10^6}=\dfrac{4{,}5\times10^3}{2\times10^6}=2{,}25\times10^{-3}\ m^2$. $r=\sqrt{2{,}25\times10^{-3}}\approx4{,}74\times10^{-2}\ m\approx4{,}7\ cm$."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Deux charges identiques $|q_A|=|q_B|=q$ sont séparées d'une distance $d$. On double cette distance sans changer les charges. Par quel facteur le champ créé par qA au point B est-il alors multiplié ?",
         "solution_markdown":r"Le champ varie en $1/r^2$. En doublant la distance ($r \to 2r$), le champ devient $E'=k\dfrac{q}{(2r)^2}=k\dfrac{q}{4r^2}=\dfrac{E}{4}$. Le champ est donc divisé par 4, pas simplement par 2 : c'est la conséquence directe de la dépendance en carré inverse de la distance."}
    ],
    synthese=[
        "Le champ créé par une charge ponctuelle décroît en $1/r^2$ avec la distance.",
        "Pour retrouver une distance à partir du champ, on isole $r^2$ puis on prend la racine carrée : ne jamais oublier cette dernière étape.",
        "Toutes les grandeurs doivent être converties en unités SI avant tout calcul numérique.",
        "Doubler la distance divise le champ par 4, pas par 2 : c'est une conséquence directe du carré au dénominateur, à retenir comme réflexe de vérification d'ordre de grandeur."
    ]
)
print("cours ex2 q1.3 done")

# ---------- EX2 Q2.1 : Deuxieme loi de Newton ----------
build_cours(find_rappel("2","2.1"),
    titre="Deuxième loi de Newton (principe fondamental de la dynamique)",
    matiere="Physique", sous_theme="Mécanique - dynamique du point",
    duree_estimee_min=20,
    tags=["deuxième loi de Newton", "dynamique", "accélération", "bilan des forces"],
    accroche=r"""Pourquoi une voiture accélère-t-elle plus vite qu'un camion pour une même force de traction ? La réponse est au cœur de toute la mécanique classique : la deuxième loi de Newton relie force, masse et accélération en une seule équation, la plus utilisée de toute la physique du mouvement.""",
    prerequis=["Notion de force et de vecteur force", "Notion d'accélération"],
    regle_titre="Deuxième loi de Newton",
    regle_markdown=r"""Pour un solide de masse $m$ constante, la somme vectorielle des forces extérieures appliquées est égale au produit de la masse par le vecteur accélération du centre d'inertie. Pour résoudre un problème de dynamique, on procède toujours dans le même ordre : faire l'inventaire complet des forces appliquées, projeter la relation sur les axes pertinents, puis isoler l'inconnue cherchée.""",
    formule_principale=r"\sum \vec{F}_{ext} = m\vec{a}",
    variantes=[],
    exemple_enonce="Un solide de masse m=15 kg est mis en mouvement de translation horizontale par une force de traction F=75 N, corde inextensible horizontale, frottements négligés, g=9,8 m/s². Déterminer l'accélération du mouvement.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Faire l'inventaire des forces", "justification":"Toute application de la deuxième loi de Newton commence par un bilan complet des forces.",
         "resultat_markdown":"Poids $\\vec{P}$, réaction normale $\\vec{R}$, force de traction $\\vec{F}$."},
        {"numero":2, "action":"Identifier les forces qui se compensent", "justification":"Le mouvement étant horizontal et le solide restant au contact du support, poids et réaction s'équilibrent verticalement.",
         "resultat_markdown":"$\\vec{P}$ et $\\vec{R}$ se compensent : leur résultante verticale est nulle."},
        {"numero":3, "action":"Projeter la loi de Newton sur l'axe horizontal", "justification":"Seule $\\vec{F}$ contribue au mouvement horizontal.",
         "resultat_markdown":r"$F = m\,a \Rightarrow a = F/m$"},
        {"numero":4, "action":"Application numérique", "justification":"On substitue les valeurs données.",
         "resultat_markdown":r"$a = 75/15 = 5\ m/s^2$"}
    ],
    exemple_conclusion="La méthode (bilan des forces, compensation verticale, projection horizontale, isolement de l'inconnue) s'applique à tout problème de translation rectiligne sans frottement.",
    erreurs=[
        {"erreur_markdown":"Utiliser $g$ dans le calcul de l'accélération horizontale alors qu'il n'intervient que dans l'équilibre vertical.",
         "pourquoi_faux":"$g$ n'apparaît que dans les termes liés au poids, qui est vertical. Le mouvement étudié ici est horizontal et ne dépend, dans ce bilan simplifié sans frottement, que de la force de traction.",
         "correction_markdown":"N'introduis une donnée dans un calcul que si elle apparaît réellement dans l'équation projetée sur l'axe étudié."},
        {"erreur_markdown":"Oublier de vérifier que le solide reste au contact du support (donc que R et P se compensent) avant de simplifier le bilan de forces.",
         "pourquoi_faux":"Cette compensation n'est vraie que si le mouvement est purement horizontal, sans décollement ni enfoncement : c'est une hypothèse à vérifier (ou à admettre explicitement), pas un fait toujours acquis.",
         "correction_markdown":"Mentionne toujours explicitement l'hypothèse de mouvement horizontal pur avant de simplifier le bilan vertical des forces."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Un solide de masse $m=4\\ kg$ est soumis à une force horizontale unique $F=20\\ N$, sans frottement. Calculer son accélération.",
         "solution_markdown":r"$a = F/m = 20/4 = 5\ m/s^2$."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Un solide de masse $m=10\\ kg$ est tracté horizontalement par une force $F=60\\ N$, mais subit aussi une force de frottement $f=10\\ N$ qui s'oppose au mouvement. Calculer l'accélération.",
         "solution_markdown":r"Bilan horizontal : $F - f = m\,a \Rightarrow a = \dfrac{F-f}{m} = \dfrac{60-10}{10} = 5\ m/s^2$."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Un solide de masse $m=8\\ kg$ est tracté par une force $F=40\\ N$ dont la direction fait un angle de $30°$ avec l'horizontale (plutôt qu'une traction parfaitement horizontale). Calculer l'accélération horizontale du solide, en négligeant les frottements.",
         "solution_markdown":r"Seule la composante horizontale de $F$ contribue au mouvement horizontal : $F_x = F\cos(30°) = 40\times0{,}866 \approx 34{,}64\ N$. $a = F_x/m = 34{,}64/8 \approx 4{,}33\ m/s^2$. On retrouve un résultat inférieur au cas purement horizontal ($F/m=5\ m/s^2$), ce qui est cohérent : incliner la force réduit sa composante utile au mouvement horizontal."}
    ],
    synthese=[
        "La deuxième loi de Newton s'écrit $\\sum\\vec{F}=m\\vec{a}$ : elle relie force résultante, masse et accélération.",
        "La méthode systématique : inventaire des forces, compensation des forces qui s'équilibrent, projection sur l'axe utile, isolement de l'inconnue.",
        "N'utilise une donnée dans un calcul que si elle intervient réellement dans l'équation projetée sur l'axe étudié.",
        "Cette loi est le socle de tout exercice de dynamique du point au programme de terminale, quelle que soit la série."
    ]
)
print("cours ex2 q2.1 done")

# ---------- EX2 Q2.2 : MRUV ----------
build_cours(find_rappel("2","2.2"),
    titre="Mouvement rectiligne uniformément varié : relation vitesse-accélération-temps",
    matiere="Physique", sous_theme="Cinématique - mouvement rectiligne",
    duree_estimee_min=15,
    tags=["MRUV", "cinématique", "vitesse", "accélération constante"],
    accroche=r"""Une fois l'accélération d'un mobile connue, comment prédire sa vitesse à n'importe quel instant ultérieur ? C'est la question centrale de la cinématique du mouvement uniformément varié, l'un des calculs les plus fréquents de tout exercice de mécanique.""",
    prerequis=["Notion de vitesse instantanée", "Accélération constante (mouvement uniformément varié)"],
    regle_titre="Relation vitesse-temps en mouvement uniformément varié",
    regle_markdown=r"""Pour un mobile animé d'un mouvement rectiligne à accélération constante $a$, partant à l'instant initial avec la vitesse $v_0$, la vitesse à l'instant $t$ s'obtient par intégration directe de l'accélération : $v(t) = v_0 + a\,t$. Si le mobile part du repos, $v_0=0$ et la relation se simplifie en $v(t)=a\,t$.""",
    formule_principale=r"v(t) = v_0 + a\,t",
    variantes=[],
    exemple_enonce="Un solide, mis en mouvement à partir du repos avec une accélération a=5 m/s², calculer sa vitesse après 5 s.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Identifier la vitesse initiale", "justification":"\"Mis en mouvement\" signifie que le solide était immobile avant l'application de la force.",
         "resultat_markdown":"$v_0 = 0$"},
        {"numero":2, "action":"Écrire la loi horaire de la vitesse", "justification":"Avec une accélération constante, la vitesse varie linéairement avec le temps.",
         "resultat_markdown":r"$v(t) = v_0 + a\,t = a\,t$"},
        {"numero":3, "action":"Application numérique", "justification":"On substitue $a=5\\ m/s^2$ et $t=5\\ s$.",
         "resultat_markdown":r"$v(5) = 5\times5 = 25\ m/s$"}
    ],
    exemple_conclusion="La vitesse croît proportionnellement au temps tant que l'accélération reste constante : c'est la signature du mouvement uniformément varié.",
    erreurs=[
        {"erreur_markdown":"Oublier de vérifier si le mobile part réellement du repos, et utiliser $v(t)=at$ même quand une vitesse initiale non nulle est donnée dans l'énoncé.",
         "pourquoi_faux":"La formule simplifiée $v=at$ n'est valable que si $v_0=0$. Ignorer une vitesse initiale non nulle donnée dans l'énoncé fausse tout le résultat.",
         "correction_markdown":"Relis toujours l'énoncé pour repérer une éventuelle vitesse initiale avant d'appliquer la formule simplifiée."},
        {"erreur_markdown":"Confondre accélération constante et vitesse constante, en pensant qu'une accélération non nulle implique une vitesse qui ne varie pas régulièrement.",
         "pourquoi_faux":"Une accélération constante signifie que la vitesse varie de façon régulière (linéaire) avec le temps, pas qu'elle reste fixe : ce sont deux notions bien distinctes.",
         "correction_markdown":"Retiens que l'accélération est le taux de variation de la vitesse : accélération constante signifie vitesse qui augmente ou diminue régulièrement, jamais une vitesse figée."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Un mobile part du repos avec une accélération constante $a=2\\ m/s^2$. Calculer sa vitesse après 10 s.",
         "solution_markdown":r"$v = a\,t = 2\times10 = 20\ m/s$."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Un mobile a une vitesse initiale $v_0=4\\ m/s$ et une accélération constante $a=3\\ m/s^2$. Calculer sa vitesse après 6 s.",
         "solution_markdown":r"$v(6) = v_0 + a\,t = 4 + 3\times6 = 4+18 = 22\ m/s$."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Un mobile part du repos avec une accélération constante $a$ et atteint la vitesse $v=30\\ m/s$ après avoir parcouru une distance $d=45\\ m$. Calculer $a$, sachant que pour un mouvement uniformément varié parti du repos, $v^2=2ad$.",
         "solution_markdown":r"$a = \dfrac{v^2}{2d} = \dfrac{30^2}{2\times45} = \dfrac{900}{90} = 10\ m/s^2$."}
    ],
    synthese=[
        "En mouvement rectiligne à accélération constante, la vitesse varie linéairement avec le temps : $v(t)=v_0+at$.",
        "Si le mobile part du repos, la formule se simplifie en $v(t)=at$.",
        "Vérifie toujours l'énoncé pour une éventuelle vitesse initiale non nulle avant de simplifier la formule.",
        "Cette relation complète la deuxième loi de Newton (qui donne l'accélération) pour obtenir la cinématique complète du mouvement."
    ]
)
print("cours ex2 q2.2 done")

# ---------- EX2 Q3.1 : Equation horaire mouvement sinusoidal ----------
build_cours(find_rappel("2","3.1"),
    titre="Équation horaire d'un mouvement sinusoïdal : amplitude, pulsation, phase",
    matiere="Physique", sous_theme="Oscillations mécaniques - mouvement sinusoïdal",
    duree_estimee_min=25,
    tags=["mouvement sinusoïdal", "pulsation", "phase à l'origine", "fréquence"],
    accroche=r"""Un pendule, une masse sur un ressort, un point d'un haut-parleur : tous ces mouvements périodiques suivent la même écriture mathématique, la fonction sinusoïdale. Savoir en extraire amplitude, fréquence et phase à partir d'une expression donnée, même écrite sous une forme inhabituelle, est une compétence transversale essentielle en physique des oscillations.""",
    prerequis=["Fonctions cosinus et sinus, identités trigonométriques de base", "Notion de période et de fréquence"],
    regle_titre="Forme canonique d'une grandeur sinusoïdale",
    regle_markdown=r"""Toute grandeur sinusoïdale s'écrit sous la forme canonique $x(t) = X_m\cos(\omega t + \varphi)$, avec $X_m > 0$ l'amplitude (toujours positive par convention), $\omega$ la pulsation en $rad/s$, et $\varphi$ la phase à l'origine des temps, comprise conventionnellement entre $-\pi$ et $\pi$. La fréquence se déduit de la pulsation par $f=\omega/(2\pi)$, et la période par $T=1/f=2\pi/\omega$. Si l'expression fournie comporte un coefficient négatif devant le cosinus, il faut la transformer avant de pouvoir lire directement l'amplitude et la phase, en utilisant l'identité $-\cos(x)=\cos(x+\pi)$.""",
    formule_principale=r"x(t) = X_m\cos(\omega t + \varphi), \quad f = \dfrac{\omega}{2\pi}",
    variantes=[
        {"nom":"Cas d'un coefficient négatif", "quand_utiliser":"Quand l'expression donnée s'écrit $x(t)=-X_m\\cos(\\omega t+\\varphi_0)$ avec $X_m>0$.",
         "contenu_markdown":r"On transforme avec $-\cos(x)=\cos(x+\pi)$ : $x(t) = X_m\cos(\omega t + \varphi_0 + \pi)$, ce qui donne la vraie phase à l'origine $\varphi = \varphi_0+\pi$ (à ramener éventuellement dans $]-\pi,\pi]$ en soustrayant $2\pi$ si besoin)."}
    ],
    exemple_enonce="La loi horaire du mouvement d'un solide est θ(t) = -2cos(100πt + π/3). Déterminer la fréquence du mouvement et sa phase à l'instant initial.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Repérer le coefficient négatif", "justification":"L'amplitude doit être positive dans la forme canonique : -2 n'est pas une amplitude valide telle quelle.",
         "resultat_markdown":"Le coefficient devant le cosinus est $-2$, négatif."},
        {"numero":2, "action":"Transformer l'écriture avec l'identité trigonométrique", "justification":"On utilise $-\\cos(x)=\\cos(x+\\pi)$ pour obtenir une amplitude positive.",
         "resultat_markdown":r"$\theta(t) = 2\cos\big(100\pi t + \pi/3 + \pi\big) = 2\cos\big(100\pi t + \tfrac{4\pi}{3}\big)$"},
        {"numero":3, "action":"Identifier pulsation et phase", "justification":"Par identification directe avec la forme canonique.",
         "resultat_markdown":r"$\omega = 100\pi\ rad/s$, $\varphi = \dfrac{4\pi}{3}\ rad$ (ou $-\dfrac{2\pi}{3}\ rad$, valeur équivalente modulo $2\pi$)"},
        {"numero":4, "action":"Calculer la fréquence", "justification":"$f=\\omega/(2\\pi)$.",
         "resultat_markdown":r"$f = \dfrac{100\pi}{2\pi} = 50\ Hz$"}
    ],
    exemple_conclusion="On retient la fréquence f=50 Hz et la phase à l'origine φ=4π/3 rad : la transformation du signe négatif est l'étape décisive qui évite l'erreur de lecture directe.",
    erreurs=[
        {"erreur_markdown":"Lire directement $\\varphi=\\pi/3$ comme phase à l'origine, en ignorant le signe négatif devant le cosinus.",
         "pourquoi_faux":"$\\pi/3$ n'est la vraie phase à l'origine que si le coefficient devant le cosinus est positif. Avec un coefficient négatif, il faut d'abord transformer l'expression : la vraie phase est $\\pi/3+\\pi=4\\pi/3$, pas $\\pi/3$.",
         "correction_markdown":"Vérifie systématiquement le signe du coefficient devant le cosinus avant de lire la phase : s'il est négatif, applique d'abord $-\\cos(x)=\\cos(x+\\pi)$."},
        {"erreur_markdown":"Donner $X_m=-2$ comme amplitude.",
         "pourquoi_faux":"Une amplitude représente une valeur maximale atteinte par une grandeur physique : elle est par convention toujours positive. Un signe négatif devant le cosinus n'est pas une amplitude négative, c'est un déphasage supplémentaire de $\\pi$.",
         "correction_markdown":"Retiens que l'amplitude est toujours annoncée positive ; tout signe négatif doit être absorbé dans la phase via l'identité trigonométrique, jamais laissé devant l'amplitude."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Une grandeur sinusoïdale s'écrit $x(t)=3\\cos(50\\pi t + \\pi/4)$. Donner directement son amplitude, sa pulsation, sa phase à l'origine et sa fréquence.",
         "solution_markdown":r"Le coefficient devant le cosinus est déjà positif, lecture directe : $X_m=3$, $\omega=50\pi\ rad/s$, $\varphi=\pi/4\ rad$. Fréquence : $f=\omega/(2\pi)=50\pi/(2\pi)=25\ Hz$."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Une grandeur sinusoïdale s'écrit $x(t)=-5\\sin(20\\pi t)$. Mettre cette expression sous forme canonique en cosinus avec une amplitude positive, puis donner sa phase à l'origine.",
         "solution_markdown":r"On utilise $\sin(x)=\cos(x-\pi/2)$ : $x(t) = -5\cos(20\pi t - \pi/2)$. Le coefficient reste négatif, on applique ensuite $-\cos(y)=\cos(y+\pi)$ : $x(t) = 5\cos(20\pi t - \pi/2 + \pi) = 5\cos(20\pi t + \pi/2)$. Amplitude $X_m=5$, phase à l'origine $\varphi = \pi/2\ rad$."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Deux grandeurs sinusoïdales de même pulsation $\\omega$ s'écrivent $x_1(t)=A\\cos(\\omega t)$ et $x_2(t)=-A\\cos(\\omega t)$. Montrer qu'elles sont en opposition de phase (déphasage de $\\pi$), et interpréter physiquement ce résultat pour une figure d'interférences.",
         "solution_markdown":r"En transformant $x_2$ : $x_2(t) = -A\cos(\omega t) = A\cos(\omega t+\pi)$. Les deux grandeurs ont la même pulsation et la même amplitude, mais une différence de phase de $\pi$ exactement : elles sont donc en opposition de phase. Physiquement, quand $x_1$ est à son maximum, $x_2$ est à son minimum (et réciproquement) : si ces deux grandeurs représentaient deux ondes lumineuses ou sonores cohérentes arrivant en un même point, leur superposition correspondrait à une interférence destructive en ce point (les deux amplitudes s'annulent exactement à chaque instant, puisque $x_1(t)+x_2(t)=0$)."}
    ],
    synthese=[
        "Toute grandeur sinusoïdale s'écrit sous forme canonique $x(t)=X_m\\cos(\\omega t+\\varphi)$, avec $X_m>0$ toujours positif.",
        "Un coefficient négatif devant le cosinus doit être transformé via $-\\cos(x)=\\cos(x+\\pi)$ avant de lire la phase.",
        "La fréquence se déduit toujours de la pulsation par $f=\\omega/(2\\pi)$, jamais l'inverse.",
        "Ne confonds jamais amplitude négative (qui n'existe pas physiquement) et déphasage supplémentaire de $\\pi$ (qui, lui, est réel).",
        "Cette lecture d'équation horaire est transversale : elle s'applique aussi bien à un mouvement de rotation, un pendule, un courant alternatif ou une onde."
    ]
)
print("cours ex2 q3.1 done")

# ---------- EX2 Q4 : Impedance RLC ----------
build_cours(find_rappel("2","4"),
    titre="Impédance d'un circuit RLC série en régime sinusoïdal forcé",
    matiere="Physique", sous_theme="Électricité - circuits RLC en régime sinusoïdal",
    duree_estimee_min=25,
    tags=["circuit RLC", "impédance", "réactance", "régime sinusoïdal forcé"],
    accroche=r"""Un circuit alimenté en courant alternatif ne se comporte pas comme en courant continu : la présence d'un condensateur et d'une bobine introduit une opposition au passage du courant qui dépend de la fréquence, appelée réactance. Ce cours te montre comment combiner résistance, réactance inductive et réactance capacitive pour obtenir l'impédance totale d'un circuit RLC série.""",
    prerequis=["Loi d'Ohm pour un résistor", "Notion de pulsation d'un signal sinusoïdal"],
    regle_titre="Impédance d'un circuit RLC série",
    regle_markdown=r"""Pour un circuit série comportant une résistance $r$, une bobine d'inductance $L$ et un condensateur de capacité $C$, alimenté en régime sinusoïdal de pulsation $\omega$, l'impédance totale du circuit combine la résistance et la réactance totale (différence entre réactance inductive $X_L=L\omega$ et réactance capacitive $X_C=1/(C\omega)$) selon un théorème de Pythagore électrique : $Z=\sqrt{r^2+(X_L-X_C)^2}$.""",
    formule_principale=r"Z = \sqrt{r^2 + \left(L\omega - \dfrac{1}{C\omega}\right)^2}",
    variantes=[],
    exemple_enonce="Circuit série r=100Ω, C=5×10⁻⁶F, L=0,100H, alimenté par un GBF de pulsation ω=100rad/s. Déterminer l'impédance du circuit.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Calculer la réactance inductive", "justification":"$X_L=L\\omega$ est la réactance propre à la bobine.",
         "resultat_markdown":r"$X_L = 0{,}100\times100 = 10\ \Omega$"},
        {"numero":2, "action":"Calculer la réactance capacitive", "justification":"$X_C=1/(C\\omega)$ est la réactance propre au condensateur.",
         "resultat_markdown":r"$X_C = \dfrac{1}{5\times10^{-6}\times100} = 2000\ \Omega$"},
        {"numero":3, "action":"Calculer la réactance totale", "justification":"C'est la différence algébrique entre réactance inductive et capacitive.",
         "resultat_markdown":r"$X_L - X_C = 10 - 2000 = -1990\ \Omega$"},
        {"numero":4, "action":"Calculer l'impédance totale", "justification":"On applique la formule combinant résistance et réactance totale.",
         "resultat_markdown":r"$Z = \sqrt{100^2+(-1990)^2} = \sqrt{3\,970\,100} \approx 1992{,}5\ \Omega$"}
    ],
    exemple_conclusion="L'impédance du circuit vaut environ 1992,5 Ω : elle est dominée ici par la réactance capacitive, très supérieure à la résistance et à la réactance inductive, du fait de la faible pulsation du générateur.",
    erreurs=[
        {"erreur_markdown":"Additionner directement $r + X_L - X_C$ au lieu d'utiliser la formule avec la racine carrée d'une somme de carrés.",
         "pourquoi_faux":"En régime sinusoïdal, la résistance et la réactance ne sont pas en phase : elles se combinent comme les deux côtés d'un triangle rectangle (représentation de Fresnel ou complexe), pas comme des grandeurs directement additives.",
         "correction_markdown":"Retiens la structure de la formule comme un théorème de Pythagore : $Z=\\sqrt{r^2+(X_L-X_C)^2}$, jamais une simple somme algébrique."},
        {"erreur_markdown":"Oublier le signe négatif de $(X_L-X_C)$ avant de l'élever au carré, ou croire que ce signe négatif rend l'impédance négative.",
         "pourquoi_faux":"Le carré d'un nombre négatif est positif : le signe de $(X_L-X_C)$ indique seulement si le circuit est globalement inductif ou capacitif, il n'affecte jamais le signe (toujours positif) de l'impédance elle-même.",
         "correction_markdown":"Calcule toujours $(X_L-X_C)$ avec son signe, mais rappelle-toi que ce terme est ensuite élevé au carré : l'impédance finale, après racine carrée d'une somme de carrés, est toujours positive."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Un circuit RLC série a $r=50\\ \\Omega$, $X_L=80\\ \\Omega$ et $X_C=20\\ \\Omega$. Calculer son impédance.",
         "solution_markdown":r"$Z=\sqrt{r^2+(X_L-X_C)^2}=\sqrt{50^2+(80-20)^2}=\sqrt{2500+3600}=\sqrt{6100}\approx78{,}1\ \Omega$."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Un circuit RLC série comporte $r=40\\ \\Omega$, $L=0{,}2\\ H$, $C=4\\times10^{-5}\\ F$, alimenté à la pulsation $\\omega=200\\ rad/s$. Calculer l'impédance du circuit.",
         "solution_markdown":r"$X_L=L\omega=0{,}2\times200=40\ \Omega$. $X_C=\dfrac{1}{C\omega}=\dfrac{1}{4\times10^{-5}\times200}=\dfrac{1}{8\times10^{-3}}=125\ \Omega$. $Z=\sqrt{40^2+(40-125)^2}=\sqrt{1600+7225}=\sqrt{8825}\approx94{,}0\ \Omega$."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Montrer qu'il existe une pulsation particulière $\\omega_0$ pour laquelle l'impédance d'un circuit RLC série est minimale et égale à $r$ seule, et exprimer cette pulsation en fonction de $L$ et $C$.",
         "solution_markdown":r"L'impédance $Z=\sqrt{r^2+(L\omega-1/(C\omega))^2}$ est minimale quand le terme $(L\omega-1/(C\omega))^2$ est minimal, c'est-à-dire nul (un carré est toujours positif ou nul). Cela correspond à $L\omega_0=\dfrac{1}{C\omega_0}$, soit $\omega_0^2=\dfrac{1}{LC}$, donc $\omega_0=\dfrac{1}{\sqrt{LC}}$. À cette pulsation, appelée pulsation de résonance, l'impédance se réduit à $Z=r$ : elle est minimale, et le courant dans le circuit est alors maximal pour une tension d'alimentation donnée. C'est le phénomène de résonance d'intensité."}
    ],
    synthese=[
        "L'impédance d'un circuit RLC série combine résistance et réactance totale : $Z=\\sqrt{r^2+(X_L-X_C)^2}$.",
        "Réactance inductive $X_L=L\\omega$ augmente avec la pulsation ; réactance capacitive $X_C=1/(C\\omega)$ diminue avec la pulsation.",
        "Le signe de $(X_L-X_C)$ indique le caractère inductif ou capacitif dominant du circuit, mais l'impédance elle-même est toujours positive.",
        "À la pulsation de résonance $\\omega_0=1/\\sqrt{LC}$, l'impédance est minimale et égale à $r$ : c'est un résultat à connaître pour les exercices sur la résonance.",
        "Ce calcul d'impédance est la porte d'entrée de tout exercice sur les circuits RLC, qu'il s'agisse de calculer un courant, une tension ou d'étudier la résonance."
    ]
)
print("cours ex2 q4 done")

# ---------- EX3 Q1.1 : Lecture caracteristique photoelectrique ----------
build_cours(find_rappel("3","1.1"),
    titre="Lecture de la caractéristique courant-tension d'une cellule photoélectrique",
    matiere="Physique", sous_theme="Effet photoélectrique - caractéristique expérimentale",
    duree_estimee_min=20,
    tags=["cellule photoélectrique", "caractéristique I-U", "photoélectrons"],
    accroche=r"""Un graphique reliant le courant photoélectrique à la tension appliquée contient, à lui seul, une grande partie des informations nécessaires pour caractériser l'émission d'électrons par un métal éclairé : ce cours t'apprend à identifier les points clés de cette courbe et ce que chacun signifie physiquement.""",
    prerequis=["Notion d'effet photoélectrique (arrachement d'électrons par la lumière)", "Notion de tension entre deux électrodes"],
    regle_titre="Points remarquables d'une caractéristique I(UAC)",
    regle_markdown=r"""Dans une cellule photoélectrique, la tension $U_{AC}$ entre anode et cathode peut accélérer ou freiner les photoélectrons émis. Trois zones caractérisent la courbe $I(U_{AC})$ : pour $U_{AC}$ très négative, le courant est nul (tous les électrons sont repoussés) ; à $U_{AC}=0$, un courant non nul subsiste si les électrons sont émis avec une énergie cinétique initiale suffisante pour traverser seuls l'espace inter-électrodes ; pour $U_{AC}$ suffisamment positive, le courant atteint un palier de saturation (tous les électrons émis sont collectés).""",
    formule_principale=None,
    variantes=[],
    exemple_enonce="Une cellule photoélectrique est éclairée en lumière monochromatique. Quelle est l'interprétation de UAC = 0V sur la caractéristique donnée ?",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Lire la valeur du courant à UAC=0V sur le graphique", "justification":"Il faut d'abord relever la donnée graphique avant de l'interpréter.",
         "resultat_markdown":"$I(U_{AC}=0) = 1{,}6\\ \\mu A$, valeur non nulle."},
        {"numero":2, "action":"Interpréter physiquement ce courant non nul", "justification":"En l'absence de tension accélératrice, seuls les électrons possédant une énergie cinétique initiale suffisante peuvent atteindre l'anode.",
         "resultat_markdown":"Des photoélectrons parviennent à l'anode sans avoir été accélérés par aucun champ électrique extérieur."},
        {"numero":3, "action":"Conclure sur la signification physique", "justification":"Ce résultat renseigne directement sur l'état cinétique des électrons à leur émission.",
         "resultat_markdown":"Les électrons sont émis avec une énergie cinétique initiale non nulle, suffisante pour traverser seuls l'espace cathode-anode."}
    ],
    exemple_conclusion="Un courant non nul à tension nulle est la preuve directe que les photoélectrons possèdent, dès leur émission, une énergie cinétique non nulle.",
    erreurs=[
        {"erreur_markdown":"Penser que $U_{AC}=0$ signifie automatiquement $I=0$, par analogie avec un circuit ohmique classique sans générateur.",
         "pourquoi_faux":"Contrairement à un simple résistor, la cellule photoélectrique contient une source d'énergie propre : la lumière incidente, qui communique de l'énergie cinétique aux électrons indépendamment de toute tension appliquée.",
         "correction_markdown":"Retiens que dans une cellule photoélectrique, le courant à tension nulle dépend uniquement de l'énergie cinétique initiale des électrons, pas d'un raisonnement de circuit électrique classique."},
        {"erreur_markdown":"Confondre le point $U_{AC}=0$ (où I≠0) avec le point où le courant s'annule réellement (tension d'arrêt, ici $U_{AC}=-0,8V$).",
         "pourquoi_faux":"Ce sont deux points très différents de la courbe, exploités dans deux questions différentes de l'exercice : l'un renseigne sur l'existence d'une énergie cinétique initiale, l'autre permet de calculer sa valeur maximale.",
         "correction_markdown":"Repère toujours précisément, sur l'axe des abscisses, où se situe le point demandé avant d'en tirer une interprétation."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Sur une caractéristique I(UAC), le courant vaut 0 pour toute tension inférieure à -1,2V et devient positif au-delà. Que représente cette valeur -1,2V ?",
         "solution_markdown":"C'est la tension d'arrêt (ou tension de seuil négative) : en dessous de cette valeur, même les électrons les plus rapides émis par la cathode sont repoussés avant d'atteindre l'anode."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Sur une caractéristique donnée, le courant atteint un palier constant à partir de UAC=+2V. Comment interpréter ce palier ?",
         "solution_markdown":"Ce palier est le courant de saturation : à partir de cette tension, tous les photoélectrons émis par la cathode sont collectés par l'anode ; augmenter encore la tension n'augmente plus le courant, car il n'y a plus d'électrons supplémentaires à collecter."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Expliquer pourquoi le courant de saturation d'une cellule photoélectrique augmente si l'on augmente la puissance de la lumière incidente, à fréquence constante, alors que la tension d'arrêt, elle, ne change pas.",
         "solution_markdown":"Augmenter la puissance lumineuse à fréquence constante augmente le nombre de photons reçus par seconde, donc le nombre d'électrons arrachés par seconde : le courant de saturation, proportionnel à ce nombre d'électrons collectés, augmente donc. En revanche, l'énergie cinétique maximale de chaque électron individuel ne dépend que de la fréquence de la lumière (via $E_{c,max}=h\\nu-W_0$), pas de la puissance : la tension d'arrêt, qui mesure justement cette énergie cinétique maximale, reste donc inchangée."}
    ],
    synthese=[
        "La caractéristique I(UAC) d'une cellule photoélectrique comporte trois zones : courant nul (tension très négative), courant non nul à U=0 si les électrons ont une énergie cinétique initiale, palier de saturation (tension suffisamment positive).",
        "Un courant non nul à UAC=0 prouve que les photoélectrons sont émis avec une énergie cinétique initiale non nulle.",
        "Ne confonds jamais le point UAC=0 avec la tension d'arrêt (où le courant s'annule réellement) : ce sont deux informations physiques distinctes.",
        "Cette lecture graphique précède presque toujours, au bac, un calcul de vitesse maximale des électrons à partir de la tension d'arrêt."
    ]
)
print("cours ex3 q1.1 done")

# ---------- EX3 Q1.2 : Tension arret energie cinetique max ----------
build_cours(find_rappel("3","1.2"),
    titre="Tension d'arrêt et énergie cinétique maximale des photoélectrons",
    matiere="Physique", sous_theme="Effet photoélectrique - énergie cinétique des électrons",
    duree_estimee_min=25,
    tags=["tension d'arrêt", "énergie cinétique", "théorème de l'énergie cinétique", "photoélectrons"],
    accroche=r"""Comment mesurer la vitesse d'électrons trop petits et trop rapides pour être observés directement ? En les freinant électriquement, jusqu'à trouver exactement la tension qui les arrête pile avant l'anode. Cette tension d'arrêt, lue simplement sur un graphique, permet de calculer la vitesse maximale des électrons par un raisonnement énergétique élégant.""",
    prerequis=["Théorème de l'énergie cinétique", "Lecture de la caractéristique I(UAC) d'une cellule photoélectrique"],
    regle_titre="Relation entre tension d'arrêt et vitesse maximale",
    regle_markdown=r"""La tension d'arrêt $U_0$ est la tension retardatrice (en valeur absolue) pour laquelle même les électrons les plus rapides, émis avec la vitesse maximale $v_{max}$, arrivent tout juste à l'anode avec une vitesse nulle. Le théorème de l'énergie cinétique, appliqué entre la cathode et l'anode à ce point particulier, donne directement la relation entre $v_{max}$ et $U_0$.""",
    formule_principale=r"\dfrac{1}{2}m_e v_{max}^2 = |e|\,U_0 \quad \Longrightarrow \quad v_{max} = \sqrt{\dfrac{2|e|U_0}{m_e}}",
    variantes=[],
    exemple_enonce="Calculer la vitesse maximale des électrons émis par la cathode, sachant qu'ils arrivent à l'anode avec une vitesse nulle, avec me=9,11×10⁻³¹kg et e=-1,6×10⁻¹⁹C.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Lire la tension d'arrêt sur le graphique", "justification":"C'est l'abscisse du point où le courant s'annule.",
         "resultat_markdown":"$U_{AC}=-0{,}8\\ V$, donc $U_0=0{,}8\\ V$ en valeur absolue."},
        {"numero":2, "action":"Appliquer le théorème de l'énergie cinétique", "justification":"Entre la cathode (vitesse $v_{max}$) et l'anode (vitesse nulle), la variation d'énergie cinétique est égale au travail de la force électrique.",
         "resultat_markdown":r"$0 - \dfrac{1}{2}m_ev_{max}^2 = e\,U_{AC}$"},
        {"numero":3, "action":"Passer aux valeurs absolues", "justification":"Le produit de deux grandeurs négatives ($e<0$ et $U_{AC}<0$) donne un travail positif, cohérent avec une force qui freine l'électron.",
         "resultat_markdown":r"$\dfrac{1}{2}m_ev_{max}^2 = |e|\,U_0$"},
        {"numero":4, "action":"Isoler et calculer $v_{max}$", "justification":"On résout l'équation pour la vitesse.",
         "resultat_markdown":r"$v_{max}=\sqrt{\dfrac{2\times1{,}6\times10^{-19}\times0{,}8}{9{,}11\times10^{-31}}}\approx5{,}3\times10^5\ m/s$"}
    ],
    exemple_conclusion="La tension d'arrêt lue graphiquement permet, via le théorème de l'énergie cinétique, de calculer directement la vitesse maximale des photoélectrons sans jamais les observer directement.",
    erreurs=[
        {"erreur_markdown":"Utiliser la tension $U_{AC}=0$ (et non la tension d'arrêt) dans la formule de la vitesse maximale.",
         "pourquoi_faux":"C'est la tension d'arrêt, où le courant s'annule, qui correspond à l'arrêt des électrons les plus rapides. La tension $U_{AC}=0$ correspond à une tout autre situation (absence de champ accélérateur, mais courant encore présent).",
         "correction_markdown":"Repère précisément sur le graphique le point où $I=0$ : c'est cette abscisse-là, et uniquement elle, qui sert au calcul de $v_{max}$."},
        {"erreur_markdown":"Utiliser $\\lambda=410\\ nm$ dans le calcul de $v_{max}$ alors que cette donnée n'est pas nécessaire ici.",
         "pourquoi_faux":"La longueur d'onde permettrait de calculer le travail d'extraction du métal via la relation d'Einstein, mais dès lors que la tension d'arrêt est disponible graphiquement, le calcul de $v_{max}$ n'a pas besoin de cette donnée supplémentaire.",
         "correction_markdown":"Identifie, pour chaque sous-question, les données réellement nécessaires : une donnée fournie dans l'énoncé général de l'exercice n'est pas automatiquement utile à chaque calcul."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"La tension d'arrêt d'une cellule photoélectrique vaut $U_0=1{,}5\\ V$. Calculer la vitesse maximale des photoélectrons ($m_e=9{,}11\\times10^{-31}\\ kg$, $|e|=1{,}6\\times10^{-19}\\ C$).",
         "solution_markdown":r"$v_{max}=\sqrt{\dfrac{2\times1{,}6\times10^{-19}\times1{,}5}{9{,}11\times10^{-31}}}=\sqrt{\dfrac{4{,}8\times10^{-19}}{9{,}11\times10^{-31}}}=\sqrt{5{,}27\times10^{11}}\approx7{,}26\times10^5\ m/s$."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Des photoélectrons sont émis avec une vitesse maximale $v_{max}=4\\times10^5\\ m/s$. Calculer la tension d'arrêt correspondante.",
         "solution_markdown":r"$\dfrac{1}{2}m_ev_{max}^2=|e|U_0 \Rightarrow U_0=\dfrac{m_ev_{max}^2}{2|e|}=\dfrac{9{,}11\times10^{-31}\times(4\times10^5)^2}{2\times1{,}6\times10^{-19}}=\dfrac{9{,}11\times10^{-31}\times1{,}6\times10^{11}}{3{,}2\times10^{-19}}\approx0{,}456\ V$."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Deux lumières monochromatiques de fréquences différentes $\\nu_1<\\nu_2$ (toutes deux supérieures au seuil du métal) éclairent successivement la même cellule photoélectrique. Comparer, sans calcul, les deux tensions d'arrêt obtenues, et justifier.",
         "solution_markdown":"L'énergie cinétique maximale des photoélectrons vaut $E_{c,max}=h\\nu-W_0$ : elle augmente avec la fréquence de la lumière incidente. Comme $U_0=E_{c,max}/|e|$, une fréquence plus élevée ($\\nu_2>\\nu_1$) donne une énergie cinétique maximale plus grande, donc une tension d'arrêt plus grande : $U_{0,2}>U_{0,1}$. La lumière de plus haute fréquence arrache des électrons plus énergétiques, qu'il faut donc freiner avec une tension retardatrice plus importante pour les arrêter complètement."}
    ],
    synthese=[
        "La tension d'arrêt U0 est la tension (en valeur absolue) pour laquelle même les électrons les plus rapides sont tout juste arrêtés avant l'anode.",
        "Le théorème de l'énergie cinétique donne directement $\\frac{1}{2}m_ev_{max}^2=|e|U_0$, d'où $v_{max}=\\sqrt{2|e|U_0/m_e}$.",
        "La tension d'arrêt se lit graphiquement comme l'abscisse du point où le courant photoélectrique s'annule.",
        "Ne confonds jamais U0 avec UAC=0 : ce sont deux points différents de la caractéristique, aux significations physiques distinctes.",
        "Ce calcul, combiné à la relation d'Einstein $E_{c,max}=h\\nu-W_0$, permet de déterminer le travail d'extraction d'un métal si la fréquence de la lumière est connue."
    ]
)
print("cours ex3 q1.2 done")

# ---------- EX3 Q2.1 : Fission nucleaire provoquee ----------
build_cours(find_rappel("3","2.1"),
    titre="Fission nucléaire provoquée",
    matiere="Physique", sous_theme="Physique nucléaire - réactions de fission",
    duree_estimee_min=15,
    tags=["fission nucléaire", "réaction nucléaire provoquée", "uranium 235"],
    accroche=r"""Un seul neutron, projeté sur un noyau d'uranium, peut déclencher la libération d'une énergie colossale et la production de nouveaux neutrons capables de répéter le processus : c'est le principe de la fission en chaîne, à la base des centrales nucléaires. Ce cours pose les bases pour reconnaître et décrire une réaction de fission.""",
    prerequis=["Notation symbolique d'un noyau (nombre de masse A, numéro atomique Z)", "Lois de conservation dans une réaction nucléaire (nombre de masse, charge)"],
    regle_titre="Reconnaître une réaction de fission",
    regle_markdown=r"""Une réaction de fission nucléaire correspond à la scission d'un noyau lourd en deux (ou plusieurs) noyaux plus légers, généralement accompagnée de l'émission de neutrons. Quand cette scission est déclenchée par l'impact d'une particule extérieure (typiquement un neutron), on parle de fission **provoquée** (ou induite), par opposition à la fission spontanée qui se produit sans intervention extérieure, pour certains noyaux très instables.""",
    formule_principale=None,
    variantes=[
        {"nom":"Fusion nucléaire", "quand_utiliser":"Quand deux noyaux légers s'assemblent pour former un noyau plus lourd (cas opposé à la fission).",
         "contenu_markdown":"La fusion réunit deux noyaux légers en un noyau plus lourd, avec libération d'énergie si les noyaux de départ sont plus légers que le fer : c'est le processus qui alimente les étoiles."}
    ],
    exemple_enonce="Lorsqu'un neutron frappe un noyau d'uranium 235, il se produit la réaction U-235 + n → Sr-94 + Xe-140 + 2n. De quel type de réaction s'agit-il ?",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Identifier le noyau initial et sa masse", "justification":"Il faut caractériser le noyau de départ avant de qualifier la réaction.",
         "resultat_markdown":"Noyau initial : uranium 235, noyau lourd ($A=235$)."},
        {"numero":2, "action":"Identifier les noyaux produits", "justification":"On observe si le noyau initial s'est scindé ou si deux noyaux se sont assemblés.",
         "resultat_markdown":"Produits : strontium 94 et xénon 140, deux noyaux plus légers que l'uranium initial, plus des neutrons libérés."},
        {"numero":3, "action":"Identifier l'élément déclencheur", "justification":"La réaction est initiée par l'impact d'un neutron incident sur le noyau d'uranium.",
         "resultat_markdown":"La réaction est déclenchée par l'impact d'un neutron extérieur."},
        {"numero":4, "action":"Conclure sur le type de réaction", "justification":"Scission d'un noyau lourd en noyaux plus légers, déclenchée par un neutron incident : c'est la définition de la fission provoquée.",
         "resultat_markdown":"Il s'agit d'une réaction de fission nucléaire provoquée."}
    ],
    exemple_conclusion="Un noyau lourd qui se scinde en noyaux plus légers sous l'impact d'un neutron est le schéma caractéristique de toute réaction de fission provoquée.",
    erreurs=[
        {"erreur_markdown":"Confondre fission et fusion en se basant uniquement sur le fait qu'une réaction nucléaire est en jeu, sans regarder le sens de la transformation.",
         "pourquoi_faux":"Fission et fusion sont deux processus opposés : la fission part d'un noyau lourd qui se divise, la fusion part de noyaux légers qui s'assemblent. Il faut toujours comparer la masse du (des) noyau(x) de départ à celle des noyaux d'arrivée.",
         "correction_markdown":"Compare systématiquement le nombre de masse A du noyau initial à ceux des noyaux finaux : une diminution (un noyau devient plusieurs plus légers) signale une fission, une augmentation (plusieurs noyaux deviennent un plus lourd) signale une fusion."},
        {"erreur_markdown":"Oublier de préciser \"provoquée\" et répondre simplement \"fission\", sans mentionner le rôle du neutron incident.",
         "pourquoi_faux":"Une réponse complète distingue la fission provoquée (déclenchée par une particule extérieure) de la fission spontanée (qui se produit sans intervention extérieure, pour certains noyaux naturellement très instables) : cette précision fait partie de la réponse attendue.",
         "correction_markdown":"Précise toujours si la fission est provoquée ou spontanée en identifiant la présence ou l'absence d'une particule incidente dans l'équation de réaction."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Un noyau de plutonium 239 se scinde sous l'impact d'un neutron en deux noyaux plus légers et plusieurs neutrons. Comment nomme-t-on ce type de réaction ?",
         "solution_markdown":"C'est une réaction de fission nucléaire provoquée, similaire à celle de l'uranium 235 : un noyau lourd (plutonium 239) se scinde en noyaux plus légers sous l'impact d'un neutron incident."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Deux noyaux de deutérium (hydrogène lourd) s'assemblent pour former un noyau d'hélium, avec émission d'un neutron. Ce type de réaction est-il une fission ou une fusion ? Justifier.",
         "solution_markdown":"C'est une fusion : deux noyaux légers (deutérium) s'assemblent pour former un noyau plus lourd (hélium), à l'inverse du schéma de fission où un noyau lourd unique se scinde en noyaux plus légers."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Expliquer pourquoi la libération de plusieurs neutrons lors de la fission de l'uranium 235 rend possible une réaction en chaîne, et à quelle condition cette chaîne s'auto-entretient.",
         "solution_markdown":"Chaque fission d'un noyau d'uranium 235 libère en moyenne deux à trois neutrons supplémentaires. Si au moins un de ces neutrons produits provoque à son tour la fission d'un autre noyau d'uranium 235 présent dans le milieu, le processus peut se répéter de façon autonome sans apport extérieur de neutrons : c'est la réaction en chaîne. Pour que cette chaîne s'auto-entretienne (facteur de multiplication proche de 1), il faut une masse suffisante de matière fissile (masse critique) pour que la probabilité qu'un neutron émis rencontre un autre noyau fissile avant de s'échapper du milieu soit suffisamment élevée."}
    ],
    synthese=[
        "La fission est la scission d'un noyau lourd en noyaux plus légers, généralement avec émission de neutrons.",
        "Elle est dite provoquée quand elle est déclenchée par l'impact d'une particule extérieure, typiquement un neutron.",
        "Elle s'oppose à la fusion, où deux noyaux légers s'assemblent pour former un noyau plus lourd.",
        "Les neutrons libérés lors d'une fission peuvent déclencher d'autres fissions : c'est le principe de la réaction en chaîne, exploité dans les réacteurs nucléaires.",
        "Reconnaître le type de réaction (comparer les nombres de masse avant/après) précède toujours, au bac, le calcul du bilan énergétique associé."
    ]
)
print("cours ex3 q2.1 done")

# ---------- EX3 Q2.2 : Bilan energetique reaction nucleaire ----------
build_cours(find_rappel("3","2.2"),
    titre="Bilan énergétique d'une réaction nucléaire à partir des énergies de liaison",
    matiere="Physique", sous_theme="Physique nucléaire - énergie de liaison et énergie libérée",
    duree_estimee_min=25,
    tags=["énergie de liaison", "énergie libérée", "fission", "bilan énergétique nucléaire"],
    accroche=r"""L'énergie colossale libérée par la fission d'un seul gramme d'uranium provient d'une différence de stabilité entre noyaux : les noyaux issus de la fission sont globalement plus liés (plus stables) que le noyau initial. Ce cours montre comment quantifier précisément cette énergie libérée à partir des énergies de liaison des noyaux en jeu.""",
    prerequis=["Notion d'énergie de liaison d'un noyau", "Identifier une réaction de fission ou de fusion"],
    regle_titre="Calcul de l'énergie libérée par une réaction nucléaire",
    regle_markdown=r"""L'énergie libérée par une réaction nucléaire est égale à la différence entre l'énergie de liaison totale des noyaux formés (produits) et l'énergie de liaison totale des noyaux initiaux (réactifs). Quand l'énoncé donne des énergies de liaison **par nucléon**, il faut d'abord les multiplier par le nombre de nucléons $A$ de chaque noyau pour obtenir l'énergie de liaison totale, avant de faire la différence. Les particules libres comme le neutron n'ont pas d'énergie de liaison (elles ne sont liées à aucun autre nucléon).""",
    formule_principale=r"\Delta E = \sum E_{liaison}(\text{produits}) - \sum E_{liaison}(\text{réactifs}), \quad E_{liaison} = A \times E_{\text{par nucléon}}",
    variantes=[],
    exemple_enonce="Énergies de liaison par nucléon: U-235: 7,59 MeV, Sr-94: 8,59 MeV, Xe-140: 8,29 MeV. Calculer l'énergie libérée par la réaction de fission.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Calculer l'énergie de liaison totale de l'uranium 235", "justification":"On multiplie l'énergie par nucléon par le nombre de nucléons A=235.",
         "resultat_markdown":r"$E_{liaison}(U) = 235\times7{,}59 = 1783{,}65\ MeV$"},
        {"numero":2, "action":"Calculer l'énergie de liaison totale du strontium 94", "justification":"Même méthode, avec A=94.",
         "resultat_markdown":r"$E_{liaison}(Sr) = 94\times8{,}59 = 807{,}46\ MeV$"},
        {"numero":3, "action":"Calculer l'énergie de liaison totale du xénon 140", "justification":"Même méthode, avec A=140.",
         "resultat_markdown":r"$E_{liaison}(Xe) = 140\times8{,}29 = 1160{,}6\ MeV$"},
        {"numero":4, "action":"Calculer l'énergie libérée par différence", "justification":"On soustrait l'énergie de liaison du réactif à celle des produits (les neutrons libres n'ont pas d'énergie de liaison).",
         "resultat_markdown":r"$\Delta E = (807{,}46+1160{,}6) - 1783{,}65 = 184{,}4\ MeV$"}
    ],
    exemple_conclusion="Le noyau d'uranium se scinde en deux noyaux globalement plus stables (plus liés par nucléon) : cette différence de stabilité libère environ 184,4 MeV, cohérente avec les valeurs mesurées expérimentalement pour la fission de l'uranium 235.",
    erreurs=[
        {"erreur_markdown":"Soustraire directement les énergies par nucléon sans les multiplier par A : $E_2+E_3-E_1=8{,}59+8{,}29-7{,}59=9{,}29\\ MeV$.",
         "pourquoi_faux":"Cette différence de quelques MeV par nucléon n'a pas de sens physique direct comme énergie totale libérée : il faut impérativement ramener chaque énergie de liaison à sa valeur totale (par noyau entier) avant de comparer, sinon on compare des grandeurs qui ne représentent pas la même chose (par nucléon contre par noyau).",
         "correction_markdown":"Multiplie systématiquement chaque énergie de liaison par nucléon par le nombre de nucléons A du noyau correspondant, avant toute soustraction."},
        {"erreur_markdown":"Inclure une énergie de liaison pour les neutrons libres (initial ou émis) dans le bilan.",
         "pourquoi_faux":"Un neutron libre, non lié à un autre nucléon, n'a pas d'énergie de liaison : lui attribuer une valeur fausserait le bilan énergétique.",
         "correction_markdown":"Ne considère l'énergie de liaison que pour les noyaux composés de plusieurs nucléons liés entre eux ; les particules libres (neutron, proton isolé) n'y contribuent jamais."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Un noyau X de nombre de masse A=100 a une énergie de liaison par nucléon de 8,5 MeV. Calculer son énergie de liaison totale.",
         "solution_markdown":r"$E_{liaison} = 100\times8{,}5 = 850\ MeV$."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Une réaction de fission transforme un noyau A (énergie de liaison totale 1800 MeV) en deux noyaux B et C (énergies de liaison totales respectives 850 MeV et 900 MeV), plus des neutrons libres. Calculer l'énergie libérée.",
         "solution_markdown":r"$\Delta E = (E_B+E_C) - E_A = (850+900)-1800 = 1750-1800 = -50\ MeV$. Le résultat négatif indique qu'une telle réaction, si elle était possible, absorberait de l'énergie au lieu d'en libérer : elle ne correspond pas à une fission spontanément favorable (les produits sont ici globalement moins liés que le réactif)."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Sachant qu'une fission d'uranium 235 libère environ 184 MeV, calculer, en joules, l'énergie libérée par la fission d'une mole de noyaux d'uranium 235 (nombre d'Avogadro $N_A=6{,}02\\times10^{23}\\ mol^{-1}$, $1\\ MeV=1{,}6\\times10^{-13}\\ J$). Comparer à l'ordre de grandeur de l'énergie libérée par la combustion d'une tonne de charbon (environ $3\\times10^{10}\\ J$).",
         "solution_markdown":r"Énergie par fission en joules : $184\times1{,}6\times10^{-13} = 2{,}944\times10^{-11}\ J$. Pour une mole (soit $6{,}02\times10^{23}$ noyaux) : $E = 6{,}02\times10^{23}\times2{,}944\times10^{-11} \approx 1{,}77\times10^{13}\ J$. Cette énergie, dégagée par environ 235 grammes d'uranium 235 (une mole), est très supérieure à celle d'une tonne de charbon ($3\times10^{10}\ J$) : le rapport est d'environ $590$, ce qui illustre concrètement pourquoi l'énergie nucléaire libère une quantité d'énergie considérablement plus grande que l'énergie chimique, à masse de combustible comparable."}
    ],
    synthese=[
        "L'énergie libérée par une réaction nucléaire est la différence entre l'énergie de liaison totale des produits et celle des réactifs.",
        "Une énergie de liaison donnée par nucléon doit toujours être multipliée par A avant d'être utilisée dans un bilan énergétique.",
        "Les particules libres (comme un neutron isolé) n'ont pas d'énergie de liaison.",
        "Une énergie libérée positive signifie que les produits sont globalement plus stables (plus liés) que les réactifs.",
        "L'ordre de grandeur de quelques centaines de MeV par fission, comparé aux quelques eV des réactions chimiques, explique la puissance énergétique de l'énergie nucléaire : c'est un repère à retenir pour vérifier tes résultats."
    ]
)
print("cours ex3 q2.2 done")

# ---------- EX3 Q3.1 : Frequence de rotation ----------
build_cours(find_rappel("3","3.1"),
    titre="Fréquence de rotation d'un disque",
    matiere="Physique", sous_theme="Stroboscopie - grandeurs de base du mouvement de rotation",
    duree_estimee_min=10,
    tags=["fréquence de rotation", "tours par seconde", "hertz"],
    accroche=r"""Avant d'étudier des phénomènes stroboscopiques complexes, il faut maîtriser la grandeur la plus simple : la fréquence de rotation d'un objet, qui compte combien de tours il effectue chaque seconde.""",
    prerequis=["Notion de fréquence (grandeur par seconde)", "Unité hertz (Hz)"],
    regle_titre="Fréquence de rotation en tours par seconde",
    regle_markdown=r"""La fréquence de rotation $N$ d'un objet correspond au nombre de tours complets qu'il effectue en une seconde. Exprimée en tours par seconde (tr/s), elle est numériquement identique à une fréquence exprimée en hertz (Hz), puisque les deux grandeurs comptent un nombre d'événements périodiques par seconde.""",
    formule_principale=r"N\ (\text{en } tr/s) = N\ (\text{en } Hz)",
    variantes=[],
    exemple_enonce="Un disque tourne à 50 tr/s. Calculer sa fréquence de rotation N.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Relever la donnée de l'énoncé", "justification":"La vitesse de rotation est directement donnée en tours par seconde.",
         "resultat_markdown":"Le disque effectue 50 tours chaque seconde."},
        {"numero":2, "action":"Convertir en hertz", "justification":"1 tr/s correspond exactement à 1 Hz pour une grandeur périodique.",
         "resultat_markdown":r"$N = 50\ tr/s = 50\ Hz$"}
    ],
    exemple_conclusion="La fréquence de rotation est directement la donnée fournie, convertie en hertz : aucun calcul complexe n'est nécessaire ici.",
    erreurs=[
        {"erreur_markdown":"Chercher à appliquer une formule complexe (comme $N=1/T$ avec un calcul de période intermédiaire) alors que la fréquence est déjà donnée directement dans l'énoncé.",
         "pourquoi_faux":"Quand l'énoncé donne directement \"X tours par seconde\", cette valeur EST déjà la fréquence de rotation : ajouter un calcul intermédiaire inutile fait perdre du temps sans rien apporter.",
         "correction_markdown":"Vérifie toujours si la donnée demandée n'est pas déjà fournie littéralement dans l'énoncé avant de te lancer dans un calcul."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Un moteur tourne à 3000 tours par minute. Exprimer sa fréquence de rotation en Hz.",
         "solution_markdown":r"Conversion en tours par seconde : $3000\ tr/min = \dfrac{3000}{60}\ tr/s = 50\ tr/s = 50\ Hz$."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Un disque effectue 900 tours en 30 secondes. Calculer sa fréquence de rotation.",
         "solution_markdown":r"$N = \dfrac{\text{nombre de tours}}{\text{durée}} = \dfrac{900}{30} = 30\ tr/s = 30\ Hz$."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Une roue de voiture de diamètre 60 cm tourne à une fréquence N=8 Hz. Calculer la vitesse linéaire d'un point situé sur la jante (à la périphérie de la roue).",
         "solution_markdown":r"Périmètre de la roue : $p=\pi D=\pi\times0{,}6\approx1{,}885\ m$. Vitesse linéaire : $v=N\times p=8\times1{,}885\approx15{,}08\ m/s$, soit environ $54{,}3\ km/h$."}
    ],
    synthese=[
        "La fréquence de rotation compte le nombre de tours effectués par seconde.",
        "Tours par seconde (tr/s) et hertz (Hz) sont numériquement identiques pour une grandeur périodique.",
        "Une donnée déjà exprimée en tr/s dans l'énoncé n'a besoin d'aucune conversion supplémentaire pour devenir une fréquence en Hz.",
        "Cette grandeur de base sert de point de départ à tout exercice de stroboscopie, notamment pour déterminer les fréquences d'éclairs donnant une immobilité apparente."
    ]
)
print("cours ex3 q3.1 done")

# ---------- EX3 Q3.2 : Condition immobilite apparente stroboscopie ----------
build_cours(find_rappel("3","3.2"),
    titre="Condition d'immobilité apparente en stroboscopie",
    matiere="Physique", sous_theme="Stroboscopie - immobilité apparente d'un objet à symétrie",
    duree_estimee_min=25,
    tags=["stroboscopie", "immobilité apparente", "symétrie de rotation", "harmoniques"],
    accroche=r"""Un stroboscope bien réglé peut figer, à l'œil nu, un objet qui tourne à plusieurs dizaines de tours par seconde. Ce résultat spectaculaire s'explique par une condition mathématique précise entre la fréquence de rotation de l'objet et la fréquence des éclairs, condition qui dépend en plus de la symétrie du motif observé.""",
    prerequis=["Fréquence de rotation d'un objet", "Notion de symétrie de rotation (motif qui se reproduit identique à lui-même après une fraction de tour)"],
    regle_titre="Fréquences d'éclairs donnant une immobilité apparente",
    regle_markdown=r"""Un objet marqué d'un motif possédant une symétrie de rotation d'ordre $n$ (le motif se superpose à lui-même $n$ fois par tour complet) paraît immobile sous éclairage stroboscopique lorsque l'angle parcouru par l'objet entre deux éclairs successifs est un multiple entier de $\dfrac{360°}{n}$. Cette condition géométrique se traduit en fréquences par $N_e=\dfrac{nN}{k}$, pour tout entier $k\geq1$, où $N$ est la fréquence de rotation réelle de l'objet. Plus $k$ est grand, plus $N_e$ est petite ; seules les valeurs de $N_e$ comprises dans la plage de réglage du stroboscope sont physiquement observables.""",
    formule_principale=r"N_e = \dfrac{nN}{k}, \quad k = 1, 2, 3, \ldots",
    variantes=[],
    exemple_enonce="Un disque marqué d'une croix à 4 rayons équidistants tourne à N=50 Hz. Le stroboscope est réglable entre 50 et 250 Hz. Pour quelles fréquences des éclairs Ne le disque paraît-il immobile ?",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Déterminer l'ordre de symétrie du motif", "justification":"La croix à 4 rayons équidistants se superpose à elle-même tous les quarts de tour.",
         "resultat_markdown":"Ordre de symétrie $n=4$ (motif identique tous les $90°$)."},
        {"numero":2, "action":"Écrire la condition d'immobilité générale", "justification":"On applique la formule générale avec l'ordre de symétrie déterminé.",
         "resultat_markdown":r"$N_e = \dfrac{4N}{k} = \dfrac{200}{k}\ Hz$, $k=1,2,3,\ldots$"},
        {"numero":3, "action":"Calculer les valeurs successives", "justification":"On énumère les valeurs pour k croissant jusqu'à sortir de la plage de réglage.",
         "resultat_markdown":"$k=1: 200\\ Hz$ ; $k=2: 100\\ Hz$ ; $k=3: 66,7\\ Hz$ ; $k=4: 50\\ Hz$ ; $k=5: 40\\ Hz$ (hors plage)."},
        {"numero":4, "action":"Ne garder que les valeurs dans la plage [50 Hz ; 250 Hz]", "justification":"Seules les fréquences réglables sur l'appareil sont physiquement observables.",
         "resultat_markdown":"$N_e \\in \\{200\\ Hz\\,;\\,100\\ Hz\\,;\\,66,7\\ Hz\\,;\\,50\\ Hz\\}$"}
    ],
    exemple_conclusion="Quatre réglages distincts du stroboscope permettent d'observer le disque comme immobile, exactement parce que la croix possède quatre positions indiscernables par tour.",
    erreurs=[
        {"erreur_markdown":"Utiliser $N_e=N/k$ (comme pour un objet marqué d'un seul repère) sans tenir compte de la symétrie du motif observé.",
         "pourquoi_faux":"Cela ignore que le motif se reproduit identique à lui-même plusieurs fois par tour : on perdrait alors les solutions correspondant aux ordres de symétrie supérieurs à 1 (ici 200 Hz, 100 Hz et 66,7 Hz).",
         "correction_markdown":"Détermine toujours l'ordre de symétrie $n$ du motif observé avant d'appliquer la formule $N_e=nN/k$."},
        {"erreur_markdown":"Oublier de vérifier que chaque valeur de $N_e$ calculée appartient bien à la plage de réglage réelle du stroboscope.",
         "pourquoi_faux":"Une valeur mathématiquement valide (comme $N_e=40\\ Hz$ dans cet exemple) peut être physiquement inaccessible si elle sort de la plage de réglage de l'appareil utilisé.",
         "correction_markdown":"Termine toujours ce type de question en filtrant les solutions selon les contraintes matérielles données dans l'énoncé (plage de réglage du stroboscope)."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Un disque marqué d'un seul repère (n=1) tourne à N=30 Hz. Un stroboscope réglable entre 10 et 100 Hz l'éclaire. Pour quelles fréquences le disque paraît-il immobile ?",
         "solution_markdown":r"$N_e=\dfrac{N}{k}=\dfrac{30}{k}$. $k=1:30\ Hz$ (dans la plage). $k=2:15\ Hz$ (dans la plage). $k=3:10\ Hz$ (dans la plage, limite). $k=4:7{,}5\ Hz$ (hors plage). Solutions : $N_e\in\{30\ Hz;15\ Hz;10\ Hz\}$."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Un disque porte un motif à symétrie d'ordre n=3 (par exemple trois secteurs identiques) et tourne à N=40 Hz. Calculer les trois plus grandes fréquences d'éclairs donnant une immobilité apparente.",
         "solution_markdown":r"$N_e=\dfrac{3\times40}{k}=\dfrac{120}{k}$. $k=1:120\ Hz$. $k=2:60\ Hz$. $k=3:40\ Hz$. Les trois plus grandes valeurs sont $120\ Hz$, $60\ Hz$ et $40\ Hz$."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Un stroboscope réglable seulement entre 100 Hz et 120 Hz éclaire un disque à symétrie d'ordre n=6, tournant à une fréquence N inconnue. On observe l'immobilité apparente exactement à 110 Hz, et à aucune autre fréquence dans cette plage. Déterminer N et la valeur de k correspondante.",
         "solution_markdown":r"$N_e=\dfrac{6N}{k}=110 \Rightarrow N=\dfrac{110k}{6}$. On cherche k entier tel que $N_e=110$ soit la seule solution dans $[100;120]$ Hz. Testons $k=6$ : $N=\dfrac{110\times6}{6}=110\ Hz$, alors $N_e=\dfrac{6\times110}{k'}=\dfrac{660}{k'}$ ; pour $k'=6$, $N_e=110\ Hz$ (bien retrouvé) ; pour $k'=5$, $N_e=132\ Hz$ (hors plage) ; pour $k'=7$, $N_e\approx94{,}3\ Hz$ (hors plage). Une seule solution dans la plage $[100;120]$ Hz est bien obtenue avec $N=110\ Hz$ et $k=6$."}
    ],
    synthese=[
        "L'immobilité apparente en stroboscopie dépend de l'ordre de symétrie n du motif observé, pas seulement de sa fréquence de rotation N.",
        "La condition générale est $N_e=nN/k$, pour tout entier positif k.",
        "Un motif à symétrie d'ordre n offre n fois plus de fréquences d'immobilité apparente qu'un objet marqué d'un seul repère.",
        "Toujours filtrer les solutions calculées selon la plage de réglage réelle du stroboscope utilisé.",
        "Cette condition d'immobilité prépare l'étude, plus fine, de la rotation apparente lente quand la fréquence des éclairs s'écarte légèrement de ces valeurs exactes."
    ]
)
print("cours ex3 q3.2 done")

# ---------- EX3 Q3.3.1 et Q3.3.2 : Rotation apparente lente (meme competence, 2 cours) ----------
def build_rotation_apparente_cours(rappel_entry, exemple_enonce, ne_val, k_val, ne0_val, sens, napp_val, etape4_detail, exemple_conclusion):
    return build_cours(rappel_entry,
        titre="Rotation apparente lente en stroboscopie",
        matiere="Physique", sous_theme="Stroboscopie - rotation apparente lente au voisinage d'un harmonique",
        duree_estimee_min=25,
        tags=["stroboscopie", "rotation apparente", "harmonique", "sens de rotation apparent"],
        accroche=r"""Quand la fréquence des éclairs d'un stroboscope n'est pas exactement réglée sur une valeur d'immobilité, l'objet observé ne paraît pas figé : il semble tourner lentement, parfois même dans le sens contraire de sa rotation réelle. Ce cours explique comment prévoir cette vitesse et ce sens apparents.""",
        prerequis=["Condition d'immobilité apparente en stroboscopie", "Notion d'harmonique (multiple entier k d'une fréquence de référence)"],
        regle_titre="Fréquence et sens de rotation apparente au voisinage d'un harmonique",
        regle_markdown=r"""Quand la fréquence des éclairs $N_e$ est proche d'une valeur d'immobilité apparente $N_{e0}=\dfrac{nN}{k}$ sans lui être exactement égale, le disque paraît tourner lentement. La fréquence apparente de cette rotation lente, au voisinage de l'harmonique $k$, vaut $N_{app}=\left|\dfrac{kN_e}{n}-N\right|$. Le sens apparent dépend du signe de l'écart : si $\dfrac{kN_e}{n}<N$ (c'est-à-dire $N_e$ légèrement inférieure à $N_{e0}$), la rotation apparente se fait dans le même sens que la rotation réelle ; si $\dfrac{kN_e}{n}>N$ (c'est-à-dire $N_e$ légèrement supérieure à $N_{e0}$), elle paraît inversée.""",
        formule_principale=r"N_{app} = \left|\dfrac{k\,N_e}{n} - N\right|",
        variantes=[],
        exemple_enonce=exemple_enonce,
        exemple_source=True,
        etapes=[
            {"numero":1, "action":"Identifier l'harmonique le plus proche", "justification":"On compare Ne à chacune des valeurs d'immobilité apparente déterminées précédemment.",
             "resultat_markdown":f"$N_e={ne_val}\\ Hz$ est proche de $N_{{e0}}={ne0_val}\\ Hz$, obtenue pour $k={k_val}$."},
            {"numero":2, "action":"Calculer l'angle réellement parcouru entre deux éclairs", "justification":"Cet angle permet de visualiser l'écart par rapport à un multiple exact de 360°/n.",
             "resultat_markdown":etape4_detail},
            {"numero":3, "action":"Calculer la fréquence apparente", "justification":"On applique la formule générale de la rotation apparente au voisinage de l'harmonique identifié.",
             "resultat_markdown":f"$N_{{app}} = \\left|\\dfrac{{{k_val}\\times{ne_val}}}{{4}} - 50\\right| = {napp_val}\\ Hz$"},
            {"numero":4, "action":"Déterminer le sens apparent", "justification":"Le signe de l'écart entre kNe/n et N donne le sens de la rotation apparente.",
             "resultat_markdown":f"Rotation apparente dans le sens **{sens}** de la rotation réelle."}
        ],
        exemple_conclusion=exemple_conclusion,
        erreurs=[
            {"erreur_markdown":"Utiliser systématiquement k=1 dans la formule, quelle que soit la fréquence d'éclairs étudiée.",
             "pourquoi_faux":"Chaque fréquence d'éclairs doit être comparée à l'harmonique le plus proche parmi toutes les valeurs d'immobilité apparente possibles, pas seulement la première (k=1) : utiliser le mauvais k conduit à une fréquence apparente et un sens complètement faux.",
             "correction_markdown":"Identifie toujours, pour la fréquence d'éclairs donnée, quelle valeur d'immobilité apparente (quel k) est la plus proche, avant d'appliquer la formule."},
            {"erreur_markdown":"Confondre le sens apparent \"même sens\" et \"sens inverse\" en oubliant de comparer kNe/n à N.",
             "pourquoi_faux":"Le sens apparent n'est pas arbitraire : il découle directement du signe de l'écart entre la rotation réelle effectuée et le multiple entier de motif visé. Une inversion de ce signe inverse la conclusion sur le sens.",
             "correction_markdown":"Calcule toujours explicitement le signe de (kNe/n - N) avant de conclure sur le sens apparent, plutôt que de deviner."}
        ],
        exercices=[
            {"numero":1, "difficulte":"facile", "enonce_markdown":"Un disque à un seul repère (n=1) tourne à N=20 Hz. Le stroboscope est réglé à Ne=21 Hz. Calculer la fréquence de rotation apparente et préciser son sens.",
             "solution_markdown":r"Harmonique le plus proche : k=1, Ne0=20 Hz. $N_{app}=|N_e-N|=|21-20|=1\ Hz$. Comme $N_e=21>N_{e0}=20$, la rotation apparente est en sens inverse de la rotation réelle, à 1 Hz."},
            {"numero":2, "difficulte":"moyen", "enonce_markdown":"Un disque à symétrie n=2 tourne à N=60 Hz. Le stroboscope est réglé à Ne=58 Hz. Calculer la fréquence de rotation apparente et son sens (on admettra que Ne est proche de l'harmonique k=1, soit Ne0=2N=120 Hz... attention, vérifier l'harmonique le plus proche avant de répondre).",
             "solution_markdown":r"Les valeurs d'immobilité sont $N_{e0}=2\times60/k=120/k$ : k=1→120 Hz, k=2→60 Hz. Ne=58 Hz est proche de k=2 (60 Hz), pas de k=1. $N_{app}=|kN_e/n-N|=|2\times58/2-60|=|58-60|=2\ Hz$. Comme $kN_e/n=58<N=60$, la rotation apparente se fait dans le même sens que la rotation réelle, à 2 Hz."},
            {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Montrer que si Ne est réglée exactement à mi-chemin entre deux valeurs consécutives d'immobilité apparente, l'objet paraît tourner à sa vitesse apparente maximale possible dans cette zone : exprimer cette fréquence apparente maximale en fonction de N et n.",
             "solution_markdown":r"Deux valeurs consécutives d'immobilité (pour un k et k+1) sont $N_{e0}(k)=nN/k$ et $N_{e0}(k+1)=nN/(k+1)$. Entre ces deux valeurs, la fréquence apparente $N_{app}=|kN_e/n-N|$ varie de façon continue, nulle aux deux extrémités (immobilité) et maximale au milieu de l'intervalle. Ce maximum se produit approximativement à mi-chemin, où l'écart relatif entre kNe/n et N est le plus grand compte tenu des contraintes aux bords : la fréquence apparente maximale dans cette zone est de l'ordre de N/(2k(k+1)) en première approximation pour des k grands, mais reste bornée par la moitié de l'écart entre les deux fréquences d'éclairs limites, soit environ $\\frac{n}{2}\\left(\\frac{N}{k}-\\frac{N}{k+1}\\right)\\times\\frac{k}{n}$. Ce résultat qualitatif retient surtout que la vitesse apparente croît en s'éloignant d'une valeur d'immobilité, jusqu'à un maximum situé entre deux harmoniques consécutifs, avant de redécroître vers zéro en approchant l'harmonique suivant."}
        ],
        synthese=[
            "Au voisinage d'un harmonique k, la fréquence apparente de rotation vaut Napp = |kNe/n - N|.",
            "Si kNe/n < N (éclairs légèrement plus lents que l'harmonique exact), la rotation apparente se fait dans le sens réel.",
            "Si kNe/n > N (éclairs légèrement plus rapides), la rotation apparente est inversée.",
            "Il faut toujours identifier l'harmonique k le plus proche de la fréquence d'éclairs étudiée avant d'appliquer la formule.",
            "Ce phénomène de rotation apparente lente, parfois inversée, est le même principe qui explique l'illusion des roues de voiture qui semblent tourner à l'envers dans les films ou sous éclairage fluorescent."
        ]
    )

r331 = find_rappel("3","3.3.1")
build_rotation_apparente_cours(
    r331,
    exemple_enonce="Qu'observe-t-on si la fréquence des éclairs vaut 195 Hz, pour un disque à croix (n=4) tournant à N=50 Hz ?",
    ne_val="195", k_val="1", ne0_val="200",
    sens="réel (identique à la rotation réelle)",
    napp_val="1{,}25",
    etape4_detail=r"$\Delta\theta = \dfrac{360\times50}{195}\approx92{,}31°$, soit $2{,}31°$ de plus qu'un multiple exact de $90°$",
    exemple_conclusion="Le disque paraît tourner lentement, dans le sens réel de sa rotation, à la fréquence apparente 1,25 Hz."
)
print("cours ex3 q3.3.1 done")

r332 = find_rappel("3","3.3.2")
build_rotation_apparente_cours(
    r332,
    exemple_enonce="Qu'observe-t-on si la fréquence des éclairs vaut 110 Hz, pour un disque à croix (n=4) tournant à N=50 Hz ?",
    ne_val="110", k_val="2", ne0_val="100",
    sens="inverse (opposé à la rotation réelle)",
    napp_val="5",
    etape4_detail=r"$\Delta\theta = \dfrac{360\times50}{110}\approx163{,}64°$, soit $16{,}36°$ de moins que le multiple exact $2\times90°=180°$",
    exemple_conclusion="Le disque paraît tourner lentement, en sens inverse de sa rotation réelle, à la fréquence apparente 5 Hz."
)
print("cours ex3 q3.3.2 done")

# ---------- EX3 Q4.1 : Interferences interfrange ----------
build_cours(find_rappel("3","4.1"),
    titre="Interférences à deux ondes : interfrange et nature des franges",
    matiere="Physique", sous_theme="Optique ondulatoire - interférences lumineuses",
    duree_estimee_min=25,
    tags=["interférences", "interfrange", "fentes de Young", "franges brillantes et sombres"],
    accroche=r"""Deux faisceaux de lumière issus de la même source, superposés sur un écran, ne donnent pas un simple éclairement uniforme : ils dessinent une alternance régulière de bandes claires et sombres. Ce phénomène d'interférences, observé pour la première fois par Young, permet de mesurer des longueurs d'onde avec une précision remarquable à partir d'une simple mesure de distance sur un écran.""",
    prerequis=["Notion de longueur d'onde d'une lumière monochromatique", "Notion de superposition d'ondes cohérentes"],
    regle_titre="Interfrange et nature d'une frange",
    regle_markdown=r"""Dans le dispositif des fentes de Young (deux fentes S1, S2 distantes de $a$, écran à une distance $D$), la distance entre deux franges brillantes (ou deux franges sombres) consécutives, appelée interfrange, vaut $i=\dfrac{\lambda D}{a}$. Un point d'abscisse $x$ sur l'écran est au milieu d'une frange brillante si $x=k\,i$ (k entier relatif, appelé ordre d'interférence), et au milieu d'une frange sombre si $x=(k+\tfrac12)\,i$. Pour déterminer la nature d'une frange en un point donné, on calcule le rapport $x/i$ et on regarde s'il tombe sur un entier ou un demi-entier.""",
    formule_principale=r"i = \dfrac{\lambda D}{a}",
    variantes=[],
    exemple_enonce="λ=0,6µm, fentes distantes de a=4mm, écran à D=2,5m. Calculer l'interfrange et la nature des franges en x1=4,5mm et x2=6mm.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Calculer l'interfrange", "justification":"On applique directement la formule avec les données converties en unités SI.",
         "resultat_markdown":r"$i=\dfrac{\lambda D}{a}=\dfrac{0{,}6\times10^{-6}\times2{,}5}{4\times10^{-3}}=0{,}375\times10^{-3}\ m=0{,}375\ mm$"},
        {"numero":2, "action":"Calculer le rapport x1/i", "justification":"Ce rapport détermine si le point est au centre d'une frange brillante ou sombre.",
         "resultat_markdown":r"$\dfrac{x_1}{i}=\dfrac{4{,}5}{0{,}375}=12$, entier : frange brillante"},
        {"numero":3, "action":"Calculer le rapport x2/i", "justification":"Même méthode pour le second point.",
         "resultat_markdown":r"$\dfrac{x_2}{i}=\dfrac{6}{0{,}375}=16$, entier : frange brillante"}
    ],
    exemple_conclusion="Les deux points sont au milieu de franges brillantes, d'ordres respectifs 12 et 16 : le calcul du rapport x/i, et son examen (entier ou demi-entier), suffit à trancher la nature de n'importe quelle frange.",
    erreurs=[
        {"erreur_markdown":"Conclure à une frange brillante ou sombre sans avoir réellement calculé et examiné le rapport x/i, en se fiant à une impression visuelle ou à un arrondi approximatif.",
         "pourquoi_faux":"Seul le calcul exact du rapport permet de distinguer un entier (frange brillante) d'un demi-entier (frange sombre) : une approximation grossière peut faire manquer cette distinction, qui repose sur une différence de 0,5 dans le rapport.",
         "correction_markdown":"Calcule toujours précisément x/i avant de conclure, et vérifie explicitement s'il s'agit d'un nombre entier ou d'un entier plus 0,5."},
        {"erreur_markdown":"Oublier de convertir toutes les longueurs dans la même unité avant de calculer l'interfrange ou le rapport x/i.",
         "pourquoi_faux":"Mélanger des mm, µm et m sans conversion cohérente conduit à des erreurs d'ordre de grandeur importantes, en particulier avec les puissances de 10 très différentes de λ (µm) et D (m).",
         "correction_markdown":"Convertis systématiquement toutes les longueurs en mètres (unité SI) avant tout calcul, puis reconvertis le résultat final dans l'unité demandée si nécessaire."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Un dispositif de fentes de Young a λ=500 nm, a=2 mm, D=1,5 m. Calculer l'interfrange.",
         "solution_markdown":r"$i=\dfrac{\lambda D}{a}=\dfrac{500\times10^{-9}\times1{,}5}{2\times10^{-3}}=\dfrac{7{,}5\times10^{-7}}{2\times10^{-3}}=3{,}75\times10^{-4}\ m=0{,}375\ mm$."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Avec l'interfrange calculé à l'exercice 1 (i=0,375 mm), déterminer la nature de la frange située en x=1,3125 mm.",
         "solution_markdown":r"$\dfrac{x}{i}=\dfrac{1{,}3125}{0{,}375}=3{,}5$. C'est un demi-entier (3+0,5) : le point est au milieu d'une frange sombre, d'ordre k=3."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"On souhaite déterminer expérimentalement la longueur d'onde d'une lumière inconnue en mesurant la distance L entre 10 interfranges consécutives sur l'écran (L=3,2 mm), avec a=3 mm et D=2 m. Calculer la longueur d'onde utilisée.",
         "solution_markdown":r"La distance entre 10 interfranges consécutives correspond à $10\,i$ : $i=L/10=3{,}2/10=0{,}32\ mm=3{,}2\times10^{-4}\ m$. On isole λ dans $i=\lambda D/a$ : $\lambda=\dfrac{i\,a}{D}=\dfrac{3{,}2\times10^{-4}\times3\times10^{-3}}{2}=4{,}8\times10^{-7}\ m=480\ nm$. Cette méthode, mesurer plusieurs interfranges plutôt qu'une seule, réduit l'erreur relative de mesure, un réflexe expérimental utile à connaître."}
    ],
    synthese=[
        "L'interfrange dans le dispositif des fentes de Young vaut $i=\\lambda D/a$.",
        "Un point d'abscisse x est au milieu d'une frange brillante si x/i est entier, sombre si x/i est un demi-entier.",
        "Convertis systématiquement toutes les longueurs en unités SI avant tout calcul.",
        "Mesurer plusieurs interfranges consécutives plutôt qu'une seule réduit l'erreur de mesure expérimentale.",
        "Ce calcul d'interfrange est l'un des rares exercices d'optique ondulatoire vraiment quantitatifs et récurrents au bac : la méthode se transpose telle quelle à tout dispositif à deux fentes."
    ]
)
print("cours ex3 q4.1 done")

# ---------- EX4 Q1 : Equilibre pendule electrostatique ----------
build_cours(find_rappel("4","1"),
    titre="Équilibre d'un pendule électrostatique entre deux plaques parallèles",
    matiere="Physique", sous_theme="Électrostatique appliquée - équilibre d'une charge sous trois forces",
    duree_estimee_min=30,
    tags=["pendule électrostatique", "équilibre de trois forces", "champ uniforme", "tension entre plaques"],
    accroche=r"""Une simple boule chargée suspendue à un fil peut servir de voltmètre improvisé : en observant de combien elle dévie entre deux plaques sous tension, on peut remonter à la valeur exacte de cette tension, sans aucun appareil de mesure électrique. C'est exactement le raisonnement qu'un technicien peut mobiliser sur le terrain pour vérifier une batterie suspecte, comme dans la situation-problème de cette épreuve.""",
    prerequis=["Équilibre d'un solide soumis à trois forces non parallèles", "Champ électrostatique uniforme entre deux plaques planes parallèles ($E=U/d$)", "Trigonométrie de base dans un triangle rectangle"],
    regle_titre="Équilibre d'une boule chargée entre deux plaques sous tension",
    regle_markdown=r"""Une boule de masse $m$ et de charge $q$, suspendue par un fil entre deux plaques verticales parallèles distantes de $d$ et soumises à une tension $U$, est en équilibre sous l'action de trois forces : son poids $\vec{P}=m\vec{g}$ (vertical), la tension du fil $\vec{T}$ (le long du fil), et la force électrique $\vec{F}=q\vec{E}$ (horizontale, avec $E=U/d$ le champ uniforme entre les plaques). Ces trois forces se compensent, ce qui forme un triangle rectangle où le poids et la force électrique sont les deux côtés perpendiculaires et la tension l'hypoténuse. L'angle $\alpha$ que fait le fil avec la verticale vérifie alors $\tan\alpha=\dfrac{F}{P}=\dfrac{qU}{mgd}$, ce qui permet de calculer U à partir d'une simple mesure d'angle.""",
    formule_principale=r"U = \dfrac{mgd\tan\alpha}{q}",
    variantes=[],
    exemple_enonce="Un pendule électrostatique (bille m=2g, q=+0,1mC) est placé entre deux plaques distantes de d=8cm, alimentées par une batterie. Le fil dévie de α=35,94° par rapport à la verticale. Déterminer la tension réellement délivrée par la batterie et conclure si elle correspond à la valeur nominale de 12V.",
    exemple_source=True,
    etapes=[
        {"numero":1, "action":"Faire le bilan des forces à l'équilibre", "justification":"Toute résolution d'un problème d'équilibre commence par l'inventaire complet des forces appliquées au solide étudié.",
         "resultat_markdown":r"$\vec{P}+\vec{T}+\vec{F}=\vec{0}$, avec $\vec{P}$ vertical, $\vec{F}$ horizontal, $\vec{T}$ le long du fil."},
        {"numero":2, "action":"Établir la relation trigonométrique", "justification":"Les trois forces forment un triangle rectangle dont l'angle au sommet est justement l'angle de déviation du fil.",
         "resultat_markdown":r"$\tan\alpha=\dfrac{F}{P}$"},
        {"numero":3, "action":"Exprimer F et P en fonction des données du problème", "justification":"On relie force électrique et champ uniforme, poids et masse.",
         "resultat_markdown":r"$F=qE=q\dfrac{U}{d}$, $P=mg$, donc $\tan\alpha=\dfrac{qU}{mgd}$"},
        {"numero":4, "action":"Isoler U et calculer numériquement", "justification":"On résout l'équation pour la seule inconnue restante, la tension U.",
         "resultat_markdown":r"$U=\dfrac{mgd\tan\alpha}{q}=\dfrac{2\times10^{-3}\times10\times8\times10^{-2}\times\tan(35{,}94°)}{1\times10^{-4}}\approx11{,}6\ V$"},
        {"numero":5, "action":"Conclure par comparaison à la valeur nominale", "justification":"Le problème demande une conclusion pratique, pas seulement une valeur numérique.",
         "resultat_markdown":r"$11{,}6\ V < 12\ V$ (valeur nominale) : la batterie ne délivre pas la tension annoncée, elle est défectueuse ou déchargée."}
    ],
    exemple_conclusion="La mesure d'un simple angle de déviation, combinée à l'équilibre des trois forces, permet de retrouver précisément la tension réelle d'une batterie et de juger de sa conformité à sa valeur nominale : c'est le principe même du pendule électrostatique utilisé comme voltmètre de fortune.",
    erreurs=[
        {"erreur_markdown":"Confondre le champ électrique E et la tension U dans le calcul final, en donnant la valeur de E comme réponse à la question posée sur U.",
         "pourquoi_faux":"E et U sont deux grandeurs liées par $E=U/d$ mais physiquement distinctes : E est un champ (en V/m), U est une tension (en V). La question posée porte sur la tension de la batterie, pas sur le champ entre les plaques.",
         "correction_markdown":"Relis toujours la question pour identifier précisément quelle grandeur est demandée (E ou U), et vérifie que ta dernière ligne de calcul correspond bien à cette grandeur."},
        {"erreur_markdown":"Oublier de convertir toutes les données (masse en grammes, distance en centimètres, charge en millicoulombs) en unités SI avant de substituer dans la formule.",
         "pourquoi_faux":"Utiliser des grammes au lieu de kilogrammes, ou des centimètres au lieu de mètres, décale le résultat final de plusieurs ordres de grandeur sans qu'aucune erreur de méthode ne soit visible dans le raisonnement.",
         "correction_markdown":"Prends toujours le réflexe de lister les données en unités SI avant même de commencer les calculs, en particulier pour les masses en grammes et les charges en milli- ou microcoulombs."},
        {"erreur_markdown":"Négliger l'étape de vérification indépendante du résultat (recalculer α à partir de U trouvé).",
         "pourquoi_faux":"Sans cette vérification, une erreur de calcul non détectée peut se glisser dans la réponse finale d'une situation-problème notée sur un grand nombre de points, sans qu'aucun contrôle ne permette de la repérer avant la remise de la copie.",
         "correction_markdown":"Pour toute situation-problème où une valeur expérimentale (ici l'angle) sert à retrouver une grandeur physique, reviens toujours en arrière avec ta valeur trouvée pour vérifier qu'elle redonne bien la donnée expérimentale de départ."}
    ],
    exercices=[
        {"numero":1, "difficulte":"facile", "enonce_markdown":"Une boule de masse m=1g et de charge q=+50µC est en équilibre entre deux plaques distantes de d=5cm sous une tension U=10V. Calculer l'angle de déviation du fil par rapport à la verticale (g=10 N/kg).",
         "solution_markdown":r"$\tan\alpha=\dfrac{qU}{mgd}=\dfrac{50\times10^{-6}\times10}{1\times10^{-3}\times10\times5\times10^{-2}}=\dfrac{5\times10^{-4}}{5\times10^{-4}}=1$. $\alpha=\arctan(1)=45°$."},
        {"numero":2, "difficulte":"moyen", "enonce_markdown":"Une boule de masse m=3g et de charge inconnue q est en équilibre, dévié d'un angle α=30°, entre deux plaques distantes de d=10cm sous une tension U=15V (g=10 N/kg). Calculer la charge q de la boule.",
         "solution_markdown":r"$\tan\alpha=\dfrac{qU}{mgd} \Rightarrow q=\dfrac{mgd\tan\alpha}{U}=\dfrac{3\times10^{-3}\times10\times0{,}1\times\tan(30°)}{15}=\dfrac{3\times10^{-3}\times0{,}577}{15}\approx1{,}15\times10^{-4}\ C=115\ \mu C$."},
        {"numero":3, "difficulte":"approfondissement", "enonce_markdown":"Montrer que pour deux boules de masses différentes mais de même rapport charge/masse (q/m), soumises à la même tension U entre les mêmes plaques (même d), l'angle de déviation à l'équilibre est identique. Commenter la portée pratique de ce résultat pour l'utilisation d'un pendule électrostatique comme voltmètre.",
         "solution_markdown":r"La relation d'équilibre s'écrit $\tan\alpha=\dfrac{qU}{mgd}=\dfrac{U}{gd}\times\dfrac{q}{m}$. Si le rapport $q/m$ est identique pour deux boules différentes, alors, à U, g et d fixés, $\tan\alpha$ prend la même valeur pour les deux boules : l'angle de déviation à l'équilibre ne dépend donc que du rapport charge/masse, pas des valeurs individuelles de q et m. Sur le plan pratique, cela signifie qu'un pendule électrostatique conçu comme instrument de mesure de tension doit être étalonné avec une boule dont on connaît précisément le rapport q/m (et non m et q séparément) : deux fabricants utilisant des boules différentes, mais de même rapport q/m, obtiendraient exactement le même angle pour une même tension, ce qui rend l'instrument reproductible indépendamment des dimensions exactes de la boule utilisée."}
    ],
    synthese=[
        "Une boule chargée en équilibre entre deux plaques sous tension est soumise à trois forces : poids, tension du fil, force électrique.",
        "Ces trois forces forment un triangle rectangle où $\\tan\\alpha=F/P=qU/(mgd)$.",
        "Cette relation permet de calculer la tension U à partir d'une simple mesure de l'angle de déviation α.",
        "Toujours vérifier le résultat en recalculant α à partir de la valeur de U trouvée : la cohérence confirme l'absence d'erreur de calcul.",
        "Ce montage illustre un principe general important en physique expérimentale : mesurer une grandeur mécanique (un angle) pour en déduire une grandeur électrique (une tension), sans aucun appareil de mesure électrique direct."
    ]
)
print("cours ex4 q1 done")

print("TOTAL COURSES:", len(COURSES))

# ============================= WRITE FINAL FILES =============================
for ex_num, ex_data in EXERCISES.items():
    out = {
        "epreuve_source": EPREUVE_SOURCE,
        "numero_exercice": ex_data["numero_exercice"],
        "matiere": "Physique",
        "serie": "D et TI",
        "examen": "bac",
        "origine": "examen blanc",
        "etablissement": None,
        "annee": 2025,
        "duree_epreuve": "3h",
        "coefficient": "2",
        "points": ex_data["points"],
        "figures": ex_data["figures"],
        "enonce_intro_markdown": ex_data["enonce_intro_markdown"],
        "questions": ex_data["questions"],
        "mots_cles_recherche": [],
        "incertitudes": [],
        "statut": "brouillon"
    }
    fname = f"{EPREUVE_SLUG}_exercice_{ex_num}.json"
    with open(os.path.join(OUTDIR, fname), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("Wrote", fname)

for cours_id, cours_data in COURSES.items():
    fname = COURSE_FILENAMES[cours_id]
    with open(os.path.join(OUTDIR, fname), "w", encoding="utf-8") as f:
        json.dump(cours_data, f, ensure_ascii=False, indent=2)
    print("Wrote", fname)

print("ALL FILES WRITTEN")
