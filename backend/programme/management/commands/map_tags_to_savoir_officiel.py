import re
from collections import Counter

from django.core.management.base import BaseCommand

from catalog.ingestion import _normalize
from catalog.models import Tag
from programme.models import Savoir

# Règles ordonnées (tag_pattern, savoir_pattern) : pour un Tag dont le nom (normalisé -
# ASCII, minuscule, voir catalog.ingestion._normalize) matche `tag_pattern`, on ne
# retient que les Savoir dont le texte de recherche (titre du module + intitulé du
# savoir, même normalisation) matche `savoir_pattern`. Un tag qui matche `tag_pattern`
# mais dont aucun Savoir ne matche `savoir_pattern` (règle mal calibrée, ou notion hors
# du programme officiel simplifié - ex. algèbre abstraite avancée) reste simplement non
# rattaché, jamais forcé sur un mauvais savoir.
#
# La première règle qui matche gagne (ordre = spécificité décroissante nécessaire par
# endroits, ex. transformations complexes avant nombres complexes algébriques, pour ne
# pas laisser une notion géométrique se faire absorber par la règle algébrique plus
# générale qui la suit).
#
# Un jeu de règles par matière, jamais un jeu global : le vocabulaire d'une matière
# matche allègrement les savoirs d'une autre (« fonctions » attrape 28 savoirs de
# Français et 6 de Physique en plus des savoirs de maths visés). Les règles ci-dessous
# ne sont confrontées qu'aux savoirs de la matière traitée - voir _savoirs_de_la_matiere.
RULES_MATHS = [
    # --- Nombres complexes : géométrique (points/transformations via affixes) avant
    # algébrique (sinon "affixe" et "similitude" seraient happés par la règle générale
    # "complexe" plus bas) ---
    (
        r"affixe|similitude|homothetie vectorielle|rotation (complexe|vectorielle|dans l.espace)|"
        r"translation complexe|ecriture complexe|centre d.une (rotation|similitude|symetrie)|"
        r"angle (d.une similitude|de rotation|oriente)|image d.un point par une (similitude|transformation|symetrie)|"
        r"image d.une courbe par une (similitude|transformation|isometrie)|image d.un cercle|"
        r"invariance.*similitude|nombres complexes et isometries|geometrie du plan complexe|"
        r"representation d.un complexe dans le plan|interpretation geometrique des complexes|"
        r"distance entre deux points d.affixes|involution (d.une reflexion)?|composee de|"
        r"decomposition (d.une rotation|en reflexions)|reflexion|isometrie|isometries|"
        r"groupe des isometries|classification des (isometries|symetries)|orbite.*transformation",
        r"nombres complexes ?: approche geometrique",
    ),
    (
        r"complexe|affixe|argument|conjugu|module d.un|racine (carree|cubique)s? d.un.*complexe|"
        r"racines? complexes?|forme (algebrique|trigonometrique|exponentielle)|puissances? de i|"
        r"racines? de l.unite|division par un nombre complexe|multiplication par le conjugue|"
        r"rationalisation d.un quotient complexe|quotient d.affixes|imaginaire pur|"
        r"discriminant complexe|equation (du second degre|complexe).*complexe|nombre complexe racine",
        r"nombres complexes ?: approche algebrique|nombres complexes ?: approche$",
    ),
    # --- Suites ---
    (
        r"\bsuite|recurrence|raison\b|terme general|convergen|point fixe.*suite|"
        r"majoration.*suite|minoration.*suite|encadrement.*suite|monotonie.*suite",
        r"suites? numeriques?",
    ),
    # --- Fonctions génériques (limites/continuité/dérivation/étude/courbes) ---
    (
        r"limite|continuit|deriv|extremum|extrema|tableau de variation|asymptote|branche (infinie|parabolique)|"
        r"point (d.inflexion|anguleux|critique)|tangente(?!.*trigonometr)|sens de variation|"
        r"parite|fonction (composee|affine|constante|rationnelle|homographique|reciproque|"
        r"valeur absolue|impaire|strictement)|croissance compare|forme indetermin|"
        r"domaine de definition|ensemble de definition|courbe representative|"
        r"representation graphique d.une fonction|zero d.une fonction|signe d.une (fonction|derivee)|"
        r"etude (de|complete d.une) fonction|synthese d.une etude de fonction|prolongement par continuite|"
        r"theoreme de la bijection|theoreme des valeurs intermediaires|raccordement de fonctions",
        r"fonctions?|derivees?|courbes? representatives?|etude des fonctions",
    ),
    # --- Logarithme / Exponentielle ---
    (r"logarithm|\bln\b", r"logarithmes?|ln ?neperien"),
    (r"exponentiel", r"exponentielles?"),
    # --- Primitives / Intégrales ---
    (r"primitive", r"primitives?"),
    (r"integral|integration|somme de riemann|relation de chasles", r"integrales?|calcul des integrales"),
    # --- Équations différentielles ---
    (r"equation different|\bedo\b|solution (generale|particuliere)", r"equations? differentielles?"),
    # --- Trigonométrie ---
    (
        r"trigonometri|identite trigonometrique|relation trigonometrique|equation trigonometrique|"
        r"valeurs remarquables de (cos|sin)|tracé? de courbe trigonometrique",
        r"trigonometrie",
    ),
    # --- Probabilités ---
    (
        r"probabilit|loi (binomiale|de probabilite|hypergeometrique)|variable aleatoire|esperance|"
        r"tirage|evenement|equiprobabilit|schema de bernoulli|univers.image|au moins un succes|"
        r"exactement un succes|repetition d.(experiences|epreuves)",
        r"probabilites",
    ),
    # --- Statistiques ---
    (
        r"statistique|effectif|moyenne (arithmetique|geometrique|ponderee|d.une serie)|median|ecart.type|"
        r"variance|histogramme|diagramme circulaire|serie statistique|classe modale|"
        r"tableau (croise|statistique)|nuage de points|ajustement|regression lineaire|"
        r"polygone des effectifs|centre de classe|regroupement de classes",
        r"statistiques?",
    ),
    # --- Dénombrement ---
    (
        r"denombrement|arrangements|combinaisons\b|factorielle|cardinaux d.ensembles|"
        r"principe multiplicatif|inclusion.exclusion",
        r"denombrement",
    ),
    # --- Théorie des graphes ---
    (r"\bgraphe", r"graphes?|theorie des graphes"),
    # --- Arithmétique ---
    (
        r"pgcd|ppmc|divisibilit|diviseur|nombres? premiers?|congruence|division euclidienne(?!.*polyn)|"
        r"bezout|algorithme d.euclide|arithmetique|reste modulo|multiples? de \d|"
        r"petit theoreme de fermat|lemme de gauss|somme de gauss",
        r"arithmetique",
    ),
    # --- Matrices ---
    (
        r"matrice|determinant d.une matrice|diagonalisation|theoreme de cayley|conjugaison matricielle|"
        r"identification (matricielle|de coefficients matriciels)",
        r"matrices et applications lineaires",
    ),
    # --- Espaces vectoriels / applications linéaires (algèbre, pas géométrie du plan) ---
    (
        r"espace vectoriel|sous.espace vectoriel|base (adaptee|orthonorm|du plan|d.un espace|d.un plan)|"
        r"famille (generatrice|libre)|dimension d.un espace|endomorphisme|noyau|image d.un endomorphisme|"
        r"automorphisme|isomorphisme d.espaces|somme directe|combinaison lineaire d.endomorphismes|"
        r"theoreme du rang|valeur propre|vecteur propre|espace propre|projecteur|"
        r"caracterisation de l.image d.un projecteur",
        r"espaces vectoriels",
    ),
    # --- Produit vectoriel / produit mixte ---
    (r"produit vectoriel|produit mixte", r"produit vectoriel"),
    # --- Barycentres ---
    (r"barycentre|isobarycentre", r"barycentres"),
    # --- Transformations affines du plan / applications affines (géométrie, pas algèbre abstraite) ---
    (
        r"application affine|transformation affine|translation(?!.*complexe)|"
        r"homothetie(?!.*vectorielle)|invariant d.une application affine|image d.une courbe par une application affine",
        r"transformations affines du plan|applications lineaires et applications affines",
    ),
    # --- Coniques ---
    (
        r"ellipse|hyperbole|parabole\b|foyer|directrice|excentricit|\bconique",
        r"coniques?",
    ),
    # --- Géométrie analytique du plan / vecteurs du plan ---
    (
        r"\bvecteur|coordonnees (d.un point|cartesiennes|d.intersection|d.un barycentre)|"
        r"droite (parallele|secante|paramétree|passant par)|equation (d.une droite|de droite)|"
        r"pente\b|coefficient directeur|colinearite|non.colinearite|alignement",
        r"geometrie analytique du plan|vecteurs du plan|coordonnees d.un vecteur|equations de droites",
    ),
    # --- Angles inscrits / polygones réguliers / arcs capables ---
    (
        r"angle inscrit|polygone regulier|arc capable|cocyclicit|concyclicit",
        r"angles inscrits|arcs capables|polygones regu",
    ),
    # --- Géométrie dans l'espace ---
    (
        r"sphere|plan (orthogonal|perpendiculaire)|orthogonalite|droite.*plan|intersection.*plan|"
        r"tetraedre|coplanarite|repere affine de l.espace|geometrie analytique dans l.espace|"
        r"geometrie de l.espace|geometrie vectorielle de l.espace",
        r"orthogonalite dans l.espace|geometrie analytique dans|spheres?",
    ),
    # --- Calcul littéral / second degré / équations-inéquations polynomiales (non complexe) ---
    (
        r"factorisation(?!.*complexe)|identites? remarquables?|second degre(?!.*complexe)|"
        r"discriminant(?!.*complexe)|trinome|racine[s]? (carree|d.un polynome)(?!.*complexe)|"
        r"developpement (algebrique|d.un produit)|calcul algebrique|simplification (algebrique|d.expression)|"
        r"polynome(?!.*complexe)|division euclidienne de polyn",
        r"calcul litteral|equations?,? ?inequations?|equations? et inequations?",
    ),
    # --- Thalès (collège/3e) ---
    (r"thales", r"thales"),
]

# Physique - Terminale C et D partagent des modules au libellé identique, seule la série
# les distingue : les motifs de savoir ci-dessous matchent donc systématiquement deux
# candidats, que la désambiguïsation par l'usage réel (le cursus du tag) tranche. C'est
# aussi pourquoi le garde mono-cursus est indispensable ici : sans lui, un tag partagé
# entre BAC C et BAC D n'aurait aucune raison d'aller vers l'un plutôt que l'autre.
RULES_PHYSIQUE = [
    # Association de dipôles avant condensateur : « association de condensateurs » porte
    # sur le groupement, pas sur l'énergie stockée. Ce savoir n'existe qu'en Tle C ; pour
    # un tag de Tle D la règle ne rend aucun candidat et l'examen continue avec les
    # suivantes, ce qui est le comportement voulu.
    (r"association de (condensateurs|dipoles|resistors|resistances)", r"association des dipoles"),
    # Condensateur avant les circuits : « charge d'un condensateur » relève de l'énergie
    # emmagasinée, pas du régime variable, alors que les deux règles pourraient matcher.
    (
        r"condensateur|capacite d.un condensateur|energie electrostatique|energie emmagasinee|"
        r"charge d.un condensateur|decharge d.un condensateur|armature",
        r"energie emmagasinee dans un condensateur",
    ),
    # Électricité avant magnétisme : « énergie magnétique » est l'énergie d'une bobine
    # dans un circuit, jamais une interaction magnétique entre objets.
    (
        r"circuit r[cl]\b|circuit rlc|circuit r,? ?l,? ?c|constante de temps|"
        r"regime (transitoire|permanent|pseudo.periodique|sinusoidal|variable|libre)|"
        r"oscillations? electriques?|impedance|reactance|bande passante|"
        r"resonance (d.intensite|electrique|lc)|resonance lc|oscillogramme|bobine|inductance|"
        r"auto.induction|energie magnetique|dephasage|facteur de puissance|"
        r"intensite efficace|tension efficace|dipole (rc|rl|rlc)",
        r"circuits electriques en regime variable",
    ),
    (
        r"champ magnetique|force (de laplace|de lorentz|magnetique)|spectrometre de masse|"
        r"cyclotron|induction magnetique|flux magnetique|aimant",
        r"analyse des interactions magnetiques",
    ),
    (
        r"gravitation|kepler|satellite|orbite|masse d.un astre|champ de pesanteur|apesanteur|"
        r"attraction universelle|geostationnaire|mouvement des planetes",
        r"interactions entre objets dues a leur masse",
    ),
    (
        r"electrostatique|champ electrique|force electrique|charge electrique|electrisation|"
        r"deflexion electronique|particule chargee|acceleration de particules|"
        r"pendule electrostatique|potentiel electrique",
        r"interactions entre des objets electriquement charges",
    ),
    # « Oscillations amorties », « oscillations forcées », « oscillateur amorti » sont
    # volontairement absents : ces notions existent à l'identique en mécanique (M2 IV) et
    # en électricité (M3 II), et le nom du tag seul ne permet pas de trancher. Les laisser
    # non rattachés vaut mieux qu'un lien faux, que rien ne viendrait corriger ensuite
    # (Tag.savoir_officiel n'est jamais écrasé). Seules restent les formes sans ambiguïté
    # possible : « petites oscillations » et « faible amplitude » désignent l'approximation
    # des petits angles, donc un pendule.
    (
        r"pendule|oscillateur (elastique|harmonique|mecanique)|petites oscillations|"
        r"oscillations? de faible amplitude|resonance mecanique|"
        r"constante de raideur|frequence propre|periode propre|moment d.inertie|"
        r"mouvement (parabolique|rectiligne|circulaire|sinusoidal|uniforme|varie)|"
        r"chute (des corps|libre)|theoreme du centre d.inertie|lois? de newton|"
        r"energie (cinetique|potentielle|mecanique)|conservation de l.energie|"
        r"travail d.une force|puissance mecanique|quantite de mouvement|\bchoc\b|"
        r"force centripete|virage releve|equations? horaires?|trajectoire|portee horizontale|"
        r"methode d.euler|vitesse maximale|systeme composite|solide compose|referentiel|"
        r"acceleration|cinematique|dynamique",
        r"principes de conservation et des lois de newton",
    ),
    # --- Ondes et physique quantique ---
    (
        r"radioactiv|desintegration|demi.vie|periode radioactive|nucleaire|fission|"
        r"fusion thermonucleaire|isotope|defaut de masse|energie de liaison|becquerel|"
        r"denombrement de noyaux|loi de decroissance|noyau (pere|fils)|activite d.un echantillon",
        r"reactions nucleaires",
    ),
    (
        r"photoelectrique|photon|quantum|quanta|dualite onde.corpuscule|effet compton|"
        r"rendement quantique|travail d.extraction|constante de planck|"
        # Avant la règle « ondes » plus bas, qui capterait « longueur d'onde seuil » sur
        # « longueur d.onde » alors que le seuil est une notion d'effet photoélectrique.
        r"longueur d.onde seuil|frequence seuil|\bseuil\b",
        r"interaction de la lumiere avec la matiere",
    ),
    (
        r"atome d.hydrogene|niveaux? d.energie|energie d.ionisation|"
        r"serie de (balmer|lyman|paschen)|transition electronique|"
        r"spectre (de raies|d.emission|d.absorption)",
        r"transitions de l.atome d.hydrogene",
    ),
    (
        r"interference|fentes? d.young|franges?|difference de marche|interfrange",
        r"interference lumineuse",
    ),
    (
        r"onde stationnaire|corde vibrante|superposition d.ondes|noeud de vibration|ventre de vibration",
        r"superposition d.ondes",
    ),
    (
        r"\bondes?\b|onde progressive|celerite|longueur d.onde|effet doppler|etat vibratoire|diffraction",
        r"description des ondes",
    ),
    # --- Mesures et incertitudes ---
    (
        r"incertitude|precision numerique|ecart relatif|regression lineaire|"
        r"chiffres significatifs|erreur (absolue|relative|de mesure)|"
        r"raisonnement par majoration|validite d.une mesure",
        r"estimation des erreurs",
    ),
]

RULES_CHIMIE = [
    (
        r"dosage acido.basique|dosage ph.metrique|indicateur colore|methode des tangentes|"
        r"point d.equivalence|demi.equivalence|courbe de dosage|zone de virage|titrage acide",
        r"dosages acido.basiques",
    ),
    (
        r"constante d.(acidite|equilibre)|\bka\b|\bpka\b|echelle de pka|couple acide.base|"
        r"diagramme de predominance|solution tampon|dissociation|electroneutralite|henderson|"
        r"produit ionique|\bpke\b",
        r"couples acide.bases et equilibre chimique de dissociation",
    ),
    (
        r"acide (fort|faible)|base (forte|faible)|bronsted|acides et bases|\bph\b|"
        r"acide carboxylique.*acidite|nature d.une solution acide",
        r"structures et proprietes des acides et bases",
    ),
    (
        r"acide (alpha.)?amine|polypeptide|liaison peptidique|zwitterion|peptide|proteine",
        r"synthese des polypeptides",
    ),
    (
        r"chiralite|carbone asymetrique|enantiomere|stereochimie|isomer|fischer|racemique|"
        r"pouvoir rotatoire|representation (de cram|en perspective)|configuration [ld]\b",
        r"representations structurales et steriques des isomeres",
    ),
    (
        r"\bamine\b|\bamines\b|\bamide\b|compose azote|acylation|anhydride.*amine|nitrile",
        r"reactivite et synthese des composes azotes",
    ),
    (
        r"aldehyde|cetone|\balcool\b|acide carboxylique|\bester\b|esterification|hydrolyse d.un ester|"
        r"oxydation menagee|compose oxygene|anhydride d.acide|chlorure d.acyle|"
        r"liqueur de fehling|dnph|reactif de tollens",
        r"reactivite et synthese des composes oxygenes",
    ),
    (
        r"cinetique|vitesse de (disparition|formation|reaction)|facteur cinetique|catalyseur|"
        r"catalyse|\btrempe\b|temps de demi.reaction|vitesse instantanee",
        r"cinetique chimique",
    ),
    (r"nombres? d.oxydation", r"utilisation des nombres d.oxydation"),
    (
        r"dosage d.oxydoreduction|permanganate|dichromate|dosage en retour|dosage colorimetrique",
        r"realisation des dosages d.oxydoreduction",
    ),
]

RULES_SVT = [
    (
        r"mitochondrie|respiration cellulaire|\batp\b|glycolyse|cycle de krebs|fermentation|"
        r"exercice musculaire|phosphorylation",
        r"renouvellement de l.atp",
    ),
    (
        r"crossing.over|genes lies|brassage|diversite genetique|recombinaison",
        r"diversite genetique",
    ),
    (r"\bmeiose\b|fecondation|gamete|spermatogenese|ovogenese", r"meiose et fecondation"),
    (
        r"anomalie (chromosomique|genetique)|trisomie|caryotype|translocation|cytogenetique|"
        r"\bchromosomes?\b|non.disjonction|garniture chromosomique",
        r"anomalies",
    ),
    (
        r"hemophilie|daltonisme|heredite liee au sexe|maladie (genique|chromosomique)|"
        r"risque genetique|arbre genealogique|mucoviscidose|drepanocytose",
        r"maladies geniques",
    ),
    (
        r"immunolog|anticorps|antigene|phagocytose|lymphocyte|vaccin|\bsida\b|\bvih\b|"
        r"systeme immunitaire|reponse immunitaire",
        r"systeme immunitaire",
    ),
    (r"synapse|transmission synaptique|neurotransmetteur|acetylcholine", r"transmission synaptique"),
    (r"reflexe|bell.magendie|nerf rachidien|moelle epiniere|arc reflexe", r"mouvements reflexes"),
    (r"cervelet|motricite|cortex moteur", r"controle de la motricite"),
    (r"neurone|potentiel d.action|conduction nerveuse|fibre nerveuse|myeline", r"neurones"),
    (r"tissu nerveux|systeme nerveux|substance (grise|blanche)", r"tissu nerveux"),
    (
        r"osmose|pression osmotique|echanges membranaires|membrane plasmique|turgescence|"
        r"plasmolyse|hematie|permeabilite",
        r"echanges d.eau",
    ),
    (
        r"procreation medicalement assistee|\bpma\b|infertilite|sterilite|appareil genital|"
        r"hormones? sexuelles?|hypothalamo.hypophysaire|gnrh|cycle (ovarien|menstruel)|testosterone",
        r"hormones sexuelles|infertilite",
    ),
    (
        r"glycemie|insuline|glucagon|diabete|pression arterielle",
        r"regulation de la glycemie",
    ),
    (r"biocarburant|biogaz|biomasse|sources? d.energie", r"nouvelles sources d.energie"),
    (r"\bdechets?\b|recyclage|compost", r"transformation et recyclage des dechets"),
    (r"conservation des fruits|appertisation|pasteurisation", r"conservation des fruits"),
]

RULES_INFORMATIQUE = [
    (
        r"formule de calcul|references? de cellules?|fonctions? (somme|moyenne|si)\b|"
        r"formule dans un tableur",
        r"utiliser les fonctions dans un tableur",
    ),
    (r"courbe dans un tableur|graphique dans un tableur", r"inserer et modifier une courbe"),
    (r"tableur|feuille de calcul|classeur|\bexcel\b", r"utiliser un tableur"),
    (
        r"messagerie|courriel|e.mail|adresse electronique|boite mail|\bcc\b|expedition d.un message",
        r"messagerie electronique",
    ),
    (
        r"moteur de recherche|recherche d.information sur internet|mot.cle de recherche",
        r"rechercher de l.information sur internet",
    ),
    (r"navigateur|site web|\burl\b|page web", r"utiliser un navigateur"),
    (
        r"reseau (informatique|local)|client.serveur|poste a poste|equipements? d.interconnexion|"
        r"routeur|commutateur|\bmodem\b|connexion (a internet|au reseau)|architecture reseau",
        r"environnement reseau",
    ),
    (
        r"numeration|base 2|\bbinaire\b|conversion (decimal|binaire)|hexadecimal|\boctal\b",
        r"systemes de numeration",
    ),
    (
        r"\bbit\b|\boctet\b|kilo.octet|mega.octet|giga.octet|unites? de mesure de l.information|"
        r"capacite de stockage|taille d.un fichier|conversion go mo ko",
        r"unites de mesure en informatique",
    ),
    (r"codage (de l.information|des caracteres)|coder une information|\bascii\b", r"coder une information"),
    (r"transfert de donnees|\bdebit\b|support de transmission", r"transfert de donnees"),
    (r"inserer un objet|image dans un document|objets dans un document texte", r"inserer les objets"),
    (r"table des matieres|sommaire automatique|pagination|styles de document", r"longs documents texte"),
]

RULES_BY_SUBJECT = {
    "MATHS": RULES_MATHS,
    "PHYSIQUE": RULES_PHYSIQUE,
    "CHIMIE": RULES_CHIMIE,
    "SVT": RULES_SVT,
    "INFORMATIQUE": RULES_INFORMATIQUE,
}

COMPILED_RULES_BY_SUBJECT = {
    subject: [(re.compile(tp), re.compile(sp)) for tp, sp in rules]
    for subject, rules in RULES_BY_SUBJECT.items()
}


class Command(BaseCommand):
    help = (
        "Passe de curation semi-automatique : rattache les Tag déjà en base (Cameroun) "
        "à un Savoir officiel via des règles de correspondance mot-clé propres à chaque "
        "matière, sans jamais deviner - un tag qui ne matche aucune règle, ou dont "
        "plusieurs Savoir candidats restent après désambiguïsation par l'usage réel "
        "(le(s) Cursus des Question/Lesson qui portent ce tag), reste non rattaché et "
        "listé pour revue manuelle plutôt que d'être forcé sur un savoir probable. Un "
        "tag dont l'usage s'étend à plusieurs cursus est écarté d'office : "
        "Tag.savoir_officiel est une FK unique, elle ne peut pas représenter fidèlement "
        "un tag qui vit dans deux programmes à la fois. Jamais d'écrasement d'un Tag "
        "déjà rattaché (voir catalog.ingestion._link_tags_to_savoir, même règle). "
        "Toujours par --dry-run d'abord."
    )

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="N'écrit rien en base, affiche seulement le rapport.")
        parser.add_argument("--country", default="CM", help="Code pays (défaut CM - seul pays avec un référentiel programme aujourd'hui).")
        parser.add_argument(
            "--subject", default="MATHS",
            help="Code matière (défaut MATHS). Doit avoir un jeu de règles dédié - voir RULES_BY_SUBJECT.",
        )
        parser.add_argument(
            "--allow-multi-cursus", action="store_true",
            help=(
                "DÉCONSEILLÉ : rattache aussi les tags utilisés dans plusieurs cursus. Le "
                "lien retenu est alors faux pour tous les usages sauf un, et les outils de "
                "pilotage font confiance à savoir_officiel dès qu'il est renseigné."
            ),
        )
        parser.add_argument("--verbose-unmapped", action="store_true", help="Détaille chaque tag non rattaché (sinon, juste un décompte par cause).")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        country_code = options["country"]
        subject_code = options["subject"]
        allow_multi_cursus = options["allow_multi_cursus"]

        compiled_rules = COMPILED_RULES_BY_SUBJECT.get(subject_code)
        if compiled_rules is None:
            # Échouer plutôt que de retomber sur un autre jeu de règles : appliquer les
            # règles de maths à des tags de physique produisait des rattachements faux
            # (constaté le 2026-08-16, 7 tags de physique captés par la règle « intégrales »).
            self.stderr.write(self.style.ERROR(
                f"Aucun jeu de règles pour la matière {subject_code!r}. "
                f"Matières couvertes : {', '.join(sorted(RULES_BY_SUBJECT))}.",
            ))
            return

        # Restreint à la matière traitée : le pool global laissait le vocabulaire d'une
        # matière matcher les savoirs d'une autre, ce qui rendait la quasi-totalité des
        # tags « ambigus » (163 tags de maths bloqués par la seule règle « fonctions »,
        # qui remontait 75 candidats dont 28 savoirs de Français).
        savoirs = list(
            Savoir.objects.select_related("module")
            .filter(module__subject__code=subject_code, module__subject__country__code=country_code)
        )
        for s in savoirs:
            s._search_text = _normalize(f"{s.module.titre} {s.intitule}")

        tags = (
            Tag.objects.filter(
                savoir_officiel__isnull=True,
                lessons_as_theme__subject__country__code=country_code,
                lessons_as_theme__subject__code=subject_code,
            )
            .distinct()
            .order_by("name")
        )

        mapped = 0
        no_rule = 0
        no_savoir_for_rule = 0
        multi_cursus = 0
        ambiguous = Counter()
        ambiguous_detail = []
        per_savoir = Counter()

        for tag in tags:
            normalized_name = _normalize(tag.name)

            tag_pattern_matched = None
            candidates = []
            for tag_re, savoir_re in compiled_rules:
                if tag_re.search(normalized_name):
                    tag_pattern_matched = tag_re.pattern
                    candidates = [s for s in savoirs if savoir_re.search(s._search_text)]
                    if candidates:
                        break

            if tag_pattern_matched is None:
                no_rule += 1
                continue
            if not candidates:
                no_savoir_for_rule += 1
                continue

            # L'usage réel du tag : à quel(s) Cursus est-il déjà associé, via les
            # Question/Lesson qui le portent ? Sert deux fois - d'abord comme garde
            # (un tag transverse n'a pas UN savoir), ensuite pour départager des
            # candidats équivalents à la série près (Tle C et Tle D ont des modules de
            # physique aux libellés identiques, seul le cursus les distingue).
            used_cursus_ids = (
                set(tag.lessons_as_theme.values_list("cursus", flat=True))
                | set(tag.questions_as_theme.values_list("exercise__lesson__cursus", flat=True))
            )
            used_cursus_ids.discard(None)

            if len(used_cursus_ids) > 1 and not allow_multi_cursus:
                multi_cursus += 1
                continue

            if len(candidates) > 1 and used_cursus_ids:
                narrowed = [s for s in candidates if s.module.cursus.filter(pk__in=used_cursus_ids).exists()]
                if len(narrowed) == 1:
                    candidates = narrowed

            if len(candidates) != 1:
                key = f"{len(candidates)} candidats pour la règle {tag_pattern_matched!r}"
                ambiguous[key] += 1
                ambiguous_detail.append(f"{tag.name!r} -> " + ", ".join(f"{s.module.classe}/{s.module.serie_label}/M{s.module.numero}/{s.numero}:{s.intitule}" for s in candidates))
                continue

            savoir = candidates[0]
            per_savoir[str(savoir)] += 1
            mapped += 1
            self.stdout.write(f"{'[dry-run] ' if dry_run else ''}{tag.name!r} -> {savoir.module.classe}/{savoir.module.serie_label or '-'} M{savoir.module.numero} : {savoir}")
            if not dry_run:
                tag.savoir_officiel = savoir
                tag.save(update_fields=["savoir_officiel"])

        total = tags.count()
        unmapped_total = no_rule + no_savoir_for_rule + multi_cursus + sum(ambiguous.values())
        self.stdout.write(self.style.SUCCESS(
            f"\n[{subject_code}] {mapped}/{total} tag(s) rattaché(s)"
            + (" (dry-run, rien n'a été écrit)" if dry_run else "")
            + f". {unmapped_total} non rattaché(s) :"
            f" {no_rule} sans règle applicable, {no_savoir_for_rule} règle sans savoir correspondant, "
            f"{multi_cursus} à usage transverse (plusieurs cursus), "
            f"{sum(ambiguous.values())} ambigus après désambiguïsation par l'usage.",
        ))
        if ambiguous:
            self.stdout.write(self.style.WARNING("\nCas ambigus par cause :"))
            for cause, count in ambiguous.most_common():
                self.stdout.write(f"  - {cause} : {count}")
            if options["verbose_unmapped"]:
                self.stdout.write(self.style.WARNING("\nDétail des cas ambigus :"))
                for line in ambiguous_detail:
                    self.stdout.write(f"  - {line}")
        if per_savoir:
            self.stdout.write(self.style.SUCCESS("\nRépartition par savoir (top 15) :"))
            for savoir_str, count in per_savoir.most_common(15):
                self.stdout.write(f"  - {savoir_str} : {count}")
