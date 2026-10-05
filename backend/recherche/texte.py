"""
Normalisation du texte pour la recherche globale - partagée par l'indexation (ce qu'on
range dans EntreeRecherche) et par la requête (ce que tape l'élève), pour que les deux
côtés parlent exactement la même langue : sans accents, en minuscules, sans LaTeX ni
syntaxe Markdown.

Pas de dépendance à `unaccent`/`pg_trgm` : la base de test est SQLite en mémoire (voir
edtech_cm.settings) et le rôle Postgres applicatif n'a pas forcément le droit de créer
des extensions. Tout ce qui suit est du Python pur, donc identique en test et en prod.
"""

import re
import unicodedata

# Formules : $$...$$, $...$, \(...\), \[...\]. Retirées entières - « x^2 + 3x » n'apporte
# rien à une recherche par mots et pollue le texte indexé (le LaTeX brut n'est jamais
# affichable en extrait non plus, voir apercu()).
_MATH_BLOC = re.compile(r"\$\$.*?\$\$", re.DOTALL)
_MATH_LIGNE = re.compile(r"\$[^$\n]+\$")
_MATH_PAREN = re.compile(r"\\\(.*?\\\)|\\\[.*?\\\]", re.DOTALL)
_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_LIEN = re.compile(r"\[([^\]]*)\]\([^)]*\)")
# Marqueurs internes des contenus compilés (voir catalog.rendering : COURS_LINK/COURS_REF),
# jamais du texte à indexer ni à montrer.
_MARQUEUR = re.compile(r"\[?COURS_(?:LINK|REF)[:=]\w+\]?")
_CALLOUT = re.compile(r"\[![A-Za-z]+\]")
_HTML = re.compile(r"<[^>]+>")
_SYNTAXE = re.compile(r"[#*_`>|~]+")
_ESPACES = re.compile(r"\s+")

# Article/pronom élidé collé au mot suivant : « l'équation », « d'une », « qu'est-ce ».
# Retiré AVANT la normalisation, sinon « d'une » donne les jetons « d » et « une », et le
# « d » isolé est précisément la série D (« bac d maths ») qu'on veut garder.
_ELISION = re.compile(r"\b(?:[ldjmtsc]|qu|jusqu|lorsqu|puisqu)['’]", re.IGNORECASE)

# Mots vides : ne discriminent rien. « a » et les lettres seules sont absents exprès (série A,
# série D...) - voir _ELISION pour les élisions.
MOTS_VIDES = frozenset({
    "de", "du", "des", "la", "le", "les", "un", "une", "et", "ou", "en", "au", "aux",
    "sur", "dans", "par", "pour", "avec", "sans", "est", "que", "qui", "quoi", "ce",
    "se", "sa", "son", "ses", "ma", "mon", "mes", "ta", "ton", "tes", "il", "elle",
    "on", "ne", "pas", "comment", "quel", "quelle", "quels", "quelles",
})

# Synonymes d'examen ajoutés aux clés des contenus : un élève écrit « baccalauréat » ou
# « brevet », le catalogue dit « BAC » et « BEPC ».
SYNONYMES_EXAMEN = {
    "BAC": "baccalaureat terminale tle",
    "BEPC": "brevet bfem troisieme 3eme",
    "PROBATOIRE": "probatoire premiere 1ere",
    "CAP": "certificat aptitude professionnelle",
    "GCE": "general certificate education advanced ordinary level",
}


def normaliser(texte):
    """Minuscules, sans accents ni ponctuation, mots séparés par un seul espace."""
    if not texte:
        return ""
    texte = _ELISION.sub("", str(texte))
    texte = unicodedata.normalize("NFKD", texte.lower())
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    texte = texte.replace("œ", "oe").replace("æ", "ae").replace("ß", "ss")
    texte = re.sub(r"[^a-z0-9]+", " ", texte)
    return texte.strip()


def nettoyer(markdown, limite=None):
    """Texte brut lisible d'un contenu Markdown/LaTeX : formules, images, liens (le libellé
    est gardé), marqueurs internes et syntaxe retirés. `limite` tronque au dernier mot."""
    if not markdown:
        return ""
    texte = str(markdown)
    for motif in (_MATH_BLOC, _MATH_PAREN, _MATH_LIGNE, _IMAGE):
        texte = motif.sub(" ", texte)
    texte = _LIEN.sub(r"\1", texte)
    for motif in (_MARQUEUR, _CALLOUT, _HTML, _SYNTAXE):
        texte = motif.sub(" ", texte)
    texte = _ESPACES.sub(" ", texte).strip()
    if limite is not None and len(texte) > limite:
        coupe = texte[:limite]
        texte = (coupe.rsplit(" ", 1)[0] if " " in coupe else coupe).rstrip(" ,;:.-")
    return texte


def apercu(markdown, longueur=170):
    """Extrait court affichable (texte déjà nettoyé, jamais du LaTeX tronqué en plein milieu),
    avec des points de suspension s'il a été coupé."""
    brut = nettoyer(markdown)
    if len(brut) <= longueur:
        return brut
    return nettoyer(brut, limite=longueur) + "…"


# Mots dont le « s » final fait partie du mot : « maths » n'est pas le pluriel de « math » (qui
# remonterait `math.h`, un thème de programmation, avant les mathématiques).
MOTS_SANS_RACINE = frozenset({"maths", "physique", "mathematiques"})


def _plier(brut):
    """Version sans accents et en minuscules de `brut`, de MÊME LONGUEUR (un caractère pour un
    caractère) : une position trouvée dans l'une est valable dans l'autre, ce que ne garantit pas
    `normaliser` (qui retire les élisions et fusionne les séparateurs)."""
    sortie = []
    for caractere in brut:
        decompose = "".join(
            c for c in unicodedata.normalize("NFKD", caractere.lower()) if not unicodedata.combining(c)
        )
        sortie.append(decompose[0] if decompose else " ")
    return "".join(sortie)


def extrait(markdown, jetons, longueur=170):
    """Passage de `markdown` autour de la première occurrence d'un des `jetons` (insensible aux
    accents et à la casse), coupé aux limites de mots, avec « … » aux extrémités tronquées. Chaîne
    vide si aucun jeton n'apparaît : l'appelant garde alors l'ouverture du texte."""
    brut = nettoyer(markdown)
    if not brut:
        return ""
    plie = _plier(brut)
    debut_match = None
    for jeton in jetons:
        if len(jeton) < 3:
            continue
        trouve = re.search(r"(?<![a-z0-9])" + re.escape(jeton), plie)
        if trouve and (debut_match is None or trouve.start() < debut_match):
            debut_match = trouve.start()
    if debut_match is None:
        return ""
    debut = max(0, debut_match - longueur // 3)
    if debut > 0:
        debut = brut.rfind(" ", 0, debut) + 1
    fin = min(len(brut), debut + longueur)
    if fin < len(brut):
        coupe = brut.rfind(" ", debut, fin)
        fin = coupe if coupe > debut else fin
    morceau = brut[debut:fin].strip()
    return ("…" if debut > 0 else "") + morceau + ("…" if fin < len(brut) else "")


def racine(jeton):
    """Singulier approximatif d'un jeton de REQUÊTE (« équations » -> « equation ») : retire
    un « s » ou « x » final, jamais sur un mot court. Appliqué côté requête seulement - la
    correspondance se fait par préfixe de mot, donc « equation » trouve aussi « equations »."""
    if jeton in MOTS_SANS_RACINE:
        return jeton
    if len(jeton) >= 4 and jeton[-1] in "sx" and not jeton.isdigit():
        return jeton[:-1]
    return jeton


def jetons(texte):
    """Mots utiles d'une requête, dans l'ordre, sans doublon ni mot vide."""
    vus = []
    for mot in normaliser(texte).split():
        if mot in MOTS_VIDES or mot in vus:
            continue
        vus.append(mot)
    return vus


def est_requis(jeton):
    """Un jeton « requis » doit être présent pour qu'un résultat soit retenu. Les jetons
    très courts (« d », « ti », « 1 ») ne font que départager : exiger « d » écarterait tout
    ce qui n'écrit pas la série en toutes lettres (« formule de l'aire d'un cercle »...)."""
    return len(jeton) >= 3 or (jeton.isdigit() and len(jeton) >= 2)


def distance(a, b, maximum):
    """Distance d'édition de Damerau-Levenshtein (les transpositions comptent pour 1 - la
    faute de frappe la plus fréquente : « thalés » / « thlaés »), arrêtée dès qu'elle dépasse
    `maximum` (renvoie alors maximum + 1)."""
    if abs(len(a) - len(b)) > maximum:
        return maximum + 1
    precedente2 = None
    precedente = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        courante = [i] + [0] * len(b)
        meilleur = courante[0]
        for j, cb in enumerate(b, 1):
            cout = 0 if ca == cb else 1
            valeur = min(precedente[j] + 1, courante[j - 1] + 1, precedente[j - 1] + cout)
            if precedente2 is not None and i > 1 and j > 1 and ca == b[j - 2] and a[i - 2] == cb:
                valeur = min(valeur, precedente2[j - 2] + 1)
            courante[j] = valeur
            meilleur = min(meilleur, valeur)
        if meilleur > maximum:
            return maximum + 1
        precedente2, precedente = precedente, courante
    return precedente[-1]


def ancre_exercice(numero_exercice):
    """Même slug que `exerciceAnchorId` côté frontend (components/EpreuveSommaire.tsx) - le
    repère « 3a », « Problème », « Section III » devient une ancre d'URL stable. À garder
    synchronisé avec cette fonction : la recherche renvoie l'ancre telle quelle."""
    texte = unicodedata.normalize("NFD", str(numero_exercice or "").lower())
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    texte = re.sub(r"[^a-z0-9]+", "-", texte).strip("-")
    return f"exercice-{texte or 'sans-numero'}"
