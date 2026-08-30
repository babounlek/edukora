"""
Rustines mécaniques appliquées à la sortie JSON de correction-experte à l'ingestion,
séparées de la traduction JSON -> modèles elle-même (voir ingestion.py). Chaque
fonction ici compense un défaut RÉCURRENT et déjà identifié de la génération (style,
échappement JSON, LaTeX mal formé, titre de section absent...) - pas une variante de
format légitime que la compétence est censée pouvoir produire (ça, c'est le rôle des
tables/résolveurs de ingestion.py, ex. _normalize_qcm_choix qui tolère plusieurs formes
toutes valides de `choix`/`reponse_correcte`).

Isoler ces rustines ici, plutôt que de les laisser diluées dans ingestion.py, rend leur
nombre visible : à chaque nouvel ajout, se demander si le défaut ne devrait pas plutôt
être corrigé dans le prompt de la compétence elle-même (voir mémoire projet
feedback_correction_experte_consistency - la plupart des entrées ci-dessous y sont
documentées avec leur historique complet, notamment le passage "définitivement résolu"
sur _repair_missing_exercise_heading : un défaut touchant plus qu'une poignée de
fichiers isolés se répète à chaque nouvelle session de génération et ne se résout
durablement que côté plateforme, jamais par un nouveau round de correction manuelle du
contenu).
"""

import re

# Le SKILL.md proscrit déjà l'em dash à la génération, mais un modèle de langage
# n'applique pas une consigne de style avec une fiabilité de 100% sur un texte long -
# filet de sécurité mécanique, appliqué à l'ingestion, plutôt que de compter
# uniquement sur le prompt.
def _strip_em_dash(value):
    """Remplace le tiret cadratin (—) par un tiret simple (-), récursivement dans un
    dict/liste (ex. sections_raw d'un Cours)."""
    if isinstance(value, str):
        return value.replace("—", "-")
    if isinstance(value, list):
        return [_strip_em_dash(item) for item in value]
    if isinstance(value, dict):
        return {key: _strip_em_dash(val) for key, val in value.items()}
    return value


# Séparateur admis entre un numéro de partie (romain ou lettre) et son libellé : point
# ("I.", "A.") ou tiret sous ses trois variantes rencontrées dans le corpus - simple
# ("I - Évaluation des savoirs", "C- Exercices au choix"), demi-cadratin ou cadratin.
# Espace autour du tiret optionnel des deux côtés (vu aussi bien "I - " que "III-").
_PART_LABEL_SEPARATOR = r"\s*[.\-–—]"

# Titre "# Exercice"/"## Problème" (Markdown) OU "**Exercice**"/"**Problème**" (gras) -
# cette 2e forme est celle que produit _repair_missing_exercise_heading (voir plus
# bas) : sans elle ici, un intro auto-complété par ce filet de sécurité ne serait plus
# reconnu comme "déjà un titre" par ce nettoyage, et une sous-question qui recopie
# encore le texte de contexte partagé ne serait plus dédupliquée (le titre injecté
# resterait dans intro_body, qui ne correspondrait alors plus au préfixe de la
# sous-question).
_SECTION_HEADING_RE = re.compile(
    r"^\s*(?:#{1,4}\s*(?:Exercice|Probl[eè]me)\b[^\n]*|\*\*\s*(?:Exercice|Probl[eè]me)\b[^\n]*?\*\*)\n+",
    re.IGNORECASE,
)
_DOUBLED_LABEL_RE = re.compile(r"\(([a-z0-9]+)\)\s*\(\1\)", re.IGNORECASE)
_DOUBLED_NUMBER_LABEL_RE = re.compile(r"\b(\d+)\.\s+\1\.\s+")


def _dedupe_question_enonce(enonce_markdown, exercise_intro):
    """
    Retire trois doublons constatés en production dans l'énoncé d'une sous-question :
    - Le texte de contexte partagé recopié depuis `enonce_intro_markdown` de
      l'exercice au début de `enonce_markdown` - la consigne de correction-experte dit
      déjà de ne pas le répéter (il vit dans `enonce_intro_markdown`), mais ça arrive.
      Sans ce nettoyage, ce texte apparaît deux fois d'affilée à la fois dans le
      corrigé compilé (catalog.rendering.compile_exercise_from_questions concatène
      intro + chaque enonce_markdown) et dans le Quiz (même logique côté frontend).
    - La lettre de sous-question dupliquée : "(a) (a)", "(3) (3)".
    - Le numéro de sous-question dupliqué, style liste numérotée sans parenthèses :
      "1. 1.", "2. 2.".
    """
    text = enonce_markdown
    if exercise_intro:
        intro_body = _SECTION_HEADING_RE.sub("", exercise_intro, count=1).strip()
        stripped = text.strip()
        if intro_body and stripped.startswith(intro_body):
            text = stripped[len(intro_body):].lstrip()
    text = _DOUBLED_LABEL_RE.sub(r"(\1)", text)
    return _DOUBLED_NUMBER_LABEL_RE.sub(r"\1. ", text)


# Filet de sécurité mécanique pour une erreur de composition déjà documentée dans
# SKILL.md (section "Format de sortie par exercice", exemple "Erreur déjà
# rencontrée") : un repère de partie ("**Partie A**", "**II.**"...) doit être porté
# par la première Question de cette partie, jamais casé dans enonce_intro_markdown
# (préambule partagé par tout l'exercice). Sa présence ici signale presque toujours
# que le repère - et souvent du contenu qui va avec - a été mal réparti, laissant les
# questions suivantes de cette partie sans aucune indication de partie côté frontend
# (voir catalog.rendering._render_question_enonce/_ENONCE_ALREADY_LABELED_RE, qui ne
# préfixe le numero que si le texte de la Question elle-même ne porte déjà aucun
# repère).
#
# Le numéro romain acceptait seulement "I." à l'origine ; le corpus SVT/Espagnol
# utilise aussi "I - Évaluation des savoirs"/"III- Exploitation des documents" (tiret,
# avec ou sans espace) - voir _PART_LABEL_SEPARATOR ci-dessus. Sans cette extension,
# _repair_missing_exercise_heading (plus bas) ne reconnaît pas ce repère comme "déjà
# présent" et injecte un second "**Exercice N (points)**" en double au-dessus (scan
# corpus du 2026-08-18 : sciences-de-la-vie-et-de-la-terre-bepc-2018 et 8 autres
# épreuves, voir mémoire projet project_intro_bare_lettered_partie_header_bug).
_INTRO_PART_HEADER_RE = re.compile(rf"\*\*\s*(Partie\s+\S|[IVX]{{1,4}}{_PART_LABEL_SEPARATOR})", re.IGNORECASE)

# Repère de PARTIE lettré sous forme courte ("**A. Évaluation des ressources (10
# points)**"), sans le mot "Partie" - forme observée sur le format d'évaluation par
# compétences (APC) camerounais, distincte de "**PARTIE A : ...**" (déjà couverte par
# _INTRO_PART_HEADER_RE ci-dessus) et jamais reconnue comme repère par
# _exercise_label_key (qui ne cherche que "Exercice"/"Problème"). Volontairement un
# regex séparé plutôt qu'ajouté à _INTRO_PART_HEADER_RE : ce dernier sert aussi à
# _flag_part_headers_in_intro, qui suppose qu'un repère de partie DANS l'intro est mal
# placé (il devrait porter sur une seule Question, pas tout l'exercice) - hypothèse
# fausse ici, puisque "A."/"B." regroupe PLUSIEURS exercices entiers (l'Exercice 1 et
# l'Exercice 2 relèvent tous les deux de "A."), donc sa présence dans l'intro PARTAGÉ de
# chacun de ces exercices est légitime. Seule sert ce garde-fou-ci
# (_repair_missing_exercise_heading) : sans lui, un exercice dont l'intro commence par
# "A."/"B." plutôt que par "Exercice N" est cru sans repère et se voit injecter un
# second "**Exercice N (points)**" en double au-dessus (constaté sur
# bepc-pct-2018-cameroun, lesson 1095 - voir mémoire projet
# feedback_correction_experte_consistency). Même extension tiret que
# _INTRO_PART_HEADER_RE ci-dessus (espagnol-bepc-2018 : "**B - Gramática**",
# sciences-de-la-vie-et-de-la-terre-bac-d-2015 : "**C- Exercices au choix**").
#
# Variante numérotée ("**A1. La vérification des savoirs (5 pts)**", "**A2. ...**") :
# le format APC numérote parfois directement chaque exercice au sein de sa Partie
# ("A1"/"A2" pour la Partie A) plutôt que de le laisser sous "A."/"B." seul - le
# chiffre optionnel entre la lettre et le séparateur couvre ce cas sans retirer la
# forme bare déjà tolérée. Sans lui, "A2." n'est reconnu comme repère ni ici ni par
# _exercise_label_key, et _repair_missing_exercise_heading injecte à tort un second
# "**Exercice N (points)**" au-dessus (bepc-blanc-littoral-2026-cameroun, exercice 2 -
# scan du 2026-08-30).
_BARE_LETTERED_PART_HEADER_RE = re.compile(rf"^\*\*\s*[A-Z]\d*{_PART_LABEL_SEPARATOR}\s")

# Repère de tête sous forme "**ÉVALUATION DES RESSOURCES : 10 points**"/"**ÉVALUATION
# DES COMPÉTENCES : 10 points**", sans lettre ni mot "Partie"/"Exercice" - la 3e forme du
# même format d'évaluation par compétences (APC) camerounais que
# _BARE_LETTERED_PART_HEADER_RE ci-dessus (voir son commentaire pour les 2 précédentes).
# Repère à PART entière plutôt qu'un simple synonyme de "Partie" : contrairement aux deux
# regex ci-dessus, il n'introduit pas forcément un groupe de plusieurs exercices - une
# "ÉVALUATION DES COMPÉTENCES" à situation-problème unique (bepc-blanc-pct-2017-
# adventiste-cameroun, Exercice 3) ne porte jamais de repère "Exercice N" nulle part dans
# le texte, le sujet source ne le numérotant tout simplement pas. Sans cette
# reconnaissance, _repair_missing_exercise_heading (plus bas) croit le repère absent et
# injecte "**Exercice 3 (10 points)**" juste au-dessus d'un "**ÉVALUATION DES
# COMPÉTENCES : 10 points**" qui identifiait déjà, à lui seul, cette section - doublon
# visible en lecture (scan du 2026-08-30, 1 occurrence en base à cette date).
_BARE_EVALUATION_HEADER_RE = re.compile(r"^\*\*\s*[EÉ]valuation\s+des\s+(?:ressources|comp[eé]tences)\b", re.IGNORECASE)

# Repère "**Situation-problème N**"/"**Situation problème N (points)**"/"**SITUATION
# PROBLÈME N - barème...**" - une 4e forme du même format d'évaluation par compétences
# (APC) camerounais que les trois regex ci-dessus. Comme _BARE_EVALUATION_HEADER_RE, un
# repère à PART entière : la Partie qui regroupe la situation-problème ("**Partie B :
# Évaluation des compétences**"...) n'est établie qu'une seule fois, sur le premier
# exercice du groupe - les exercices suivants reprennent directement "Situation-problème
# N" en tête sans la répéter (numérotation locale à la situation-problème elle-même -
# 1, 2... - distincte de numero_exercice, l'index global de l'épreuve). Sans cette
# reconnaissance, _repair_missing_exercise_heading (plus bas) croit le repère absent et
# injecte un second "**Exercice N (points)**" au-dessus d'un "**Situation-problème N**"
# qui identifiait déjà, à lui seul, cet exercice - doublon visible en lecture
# (physique-bac-c-2025, exercice 5, scan du 2026-08-30 : 11 autres exercices touchés,
# essentiellement en physique BAC C/D et histoire-géo/éducation civique BEPC).
_BARE_SITUATION_PROBLEME_HEADER_RE = re.compile(r"^\*\*\s*Situation[\s-]+probl[eè]me\b", re.IGNORECASE)

# Repère "**Compétence ciblée**"/"**Compétence visée**"/"**Compétence évaluée**" -
# précède parfois directement _BARE_SITUATION_PROBLEME_HEADER_RE ci-dessus au lieu
# d'être suivi par lui immédiatement (sciences-de-la-vie-et-de-la-terre-bac-c-et-ti-2024,
# exercice 5) : même défaut de fond, la Partie qui regroupe les deux n'a jamais été
# répétée pour cet exercice. Sans cette reconnaissance, c'est "Compétence ciblée" - pas
# "Situation-problème", qui n'apparaît alors qu'en 2e paragraphe - qui occupe la
# première ligne et passe inaperçu, et _repair_missing_exercise_heading injecte quand
# même un "**Exercice N (points)**" en double au-dessus des deux (scan du 2026-08-30).
_BARE_COMPETENCE_LABEL_RE = re.compile(r"^\*\*\s*Comp[eé]tence\s+(?:cibl[eé]e|vis[eé]e|[eé]valu[eé]e)\b", re.IGNORECASE)


def _flag_part_headers_in_intro(exercise):
    if not _INTRO_PART_HEADER_RE.search(exercise.enonce_intro_markdown):
        return
    note = (
        "enonce_intro_markdown contient un repère de partie (\"Partie X\", \"I.\"...) - "
        "doit être porté par la première Question de cette partie, pas par l'intro "
        "partagée de l'exercice (voir SKILL.md, \"Erreur déjà rencontrée\")."
    )
    if note not in exercise.incertitudes:
        exercise.incertitudes = [note, *exercise.incertitudes]
        exercise.save(update_fields=["incertitudes"])


# "\n" seul (backslash+n) est ambigu à l'intérieur d'une zone de maths ($...$ ou
# $$...$$) : un vrai saut de ligne littéral ET des commandes LaTeX légitimes
# commençant par "n" en minuscule après le backslash (\neq, \nabla, \notin, \ne...)
# produisent tous les deux ce même motif une fois décodés - on ne compte comme signal
# que "\n" NON suivi d'une minuscule dans ce cas (une phrase qui suit un vrai saut de
# ligne commence toujours par une majuscule, un chiffre ou un symbole, jamais par une
# minuscule qui continuerait alors le nom d'une commande).
#
# En dehors de toute zone de maths (prose pure), cette ambiguïté n'existe pas : aucune
# commande LaTeX ne s'utilise hors zone de maths dans ce corpus, donc "\n" y est
# TOUJOURS un saut de ligne corrompu, quelle que soit la lettre suivante (repéré sur
# bac-c-e-maths-2025-cameroun, leçon 724, question 4b : "...methode\ne1 appartient..."
# restait à tort non converti, "e1" étant en minuscule, alors qu'il s'agit d'une simple
# phrase après un titre "### Rappel de methode", pas d'une commande LaTeX).
_LITERAL_BACKSLASH_N_RE = re.compile(r"\\n")

# Suite EXACTE de minuscules après le backslash+n pour chaque commande légitime
# réellement utilisée dans ce corpus (\neq, \nabla, \nearrow, \nwarrow, \notin, \nu) -
# vérifié par un scan corpus-entier avant d'écrire cette liste. Un simple "la lettre
# suivante est une minuscule" (ancienne version) protégeait aussi, à tort, tout \n suivi
# d'une minuscule QUELCONQUE - repéré sur bac-c-maths-1987 à 1992/bac-d-maths-2007/
# bac-c-maths-probatoire-2014 (tableaux de variations) : un vrai saut de ligne collé à
# l'étiquette d'une seule lettre de la ligne suivante ("\nf", "\nx", "\ng", "\na" - f(x),
# x, g(x), a ne sont des commandes LaTeX pour aucune d'elles) restait à tort non corrigé.
# EXACT (pas un prefixe) : la suite MAXIMALE de minuscules consécutives doit correspondre
# au mot entier, jamais juste son début - sinon "\nutilise" (un vrai saut de ligne suivi
# du mot français "utilise") serait à tort pris pour "\nu" (la lettre grecque) suivi de
# "tilise", puisque KaTeX lit lui-même tout le mot "nutilise" comme un unique nom de
# commande indéfini (jamais "nu" + "tilise" séparément) - le lookahead sur le mot ENTIER
# reproduit cette même règle de tokenisation.
_REAL_LOWERCASE_N_LATEX_WORDS = frozenset({"eq", "abla", "earrow", "warrow", "otin", "u"})
_LOWERCASE_LETTER_RUN_RE = re.compile(r"[a-z]*")

# "$$" (maths "display", le cas quasi systématique pour un tableau de variations)
# compte comme UNE SEULE paire de délimiteurs, pas deux "$" indépendants : compter
# chaque caractère "$" séparément fausse la parité à l'intérieur d'un bloc "$$...$$" -
# juste après l'ouverture "$$", 2 caractères "$" ont déjà été vus (compte PAIR), donc
# l'ancienne règle ("impair = dans les maths") classait à tort l'INTÉRIEUR d'un
# "$$...$$" comme HORS zone de maths. Conséquence concrète repérée sur
# bac-d-maths-1985/1989/1991-cameroun (et d'autres épreuves du corpus) :
# "\nearrow"/"\nwarrow" (commandes légitimes) à l'intérieur d'un
# "$$\begin{array}...\end{array}$$" étaient traités comme un vrai saut de ligne
# corrompu par _is_real_newline_signal, et mutilés en un saut de ligne réel suivi de
# "earrow"/"warrow" en texte brut - rendu KaTeX cassé. "$${1,2}" (testé glouton, donc
# "$$" prime sur "$" seul) traite chaque paire comme un unique jeton de bascule.
_UNESCAPED_DOLLAR_RE = re.compile(r"(?<!\\)\${1,2}")


def _is_inside_math_zone(text, pos):
    return len(_UNESCAPED_DOLLAR_RE.findall(text[:pos])) % 2 == 1


def _is_real_newline_signal(text, match):
    if not _is_inside_math_zone(text, match.start()):
        return True
    next_pos = match.end()
    if not (next_pos < len(text) and text[next_pos].islower()):
        return True
    letter_run = _LOWERCASE_LETTER_RUN_RE.match(text, next_pos).group(0)
    return letter_run not in _REAL_LOWERCASE_N_LATEX_WORDS


def _has_literal_backslash_n(value):
    if isinstance(value, str):
        return any(_is_real_newline_signal(value, m) for m in _LITERAL_BACKSLASH_N_RE.finditer(value))
    if isinstance(value, list):
        return any(_has_literal_backslash_n(v) for v in value)
    if isinstance(value, dict):
        return any(_has_literal_backslash_n(v) for v in value.values())
    return False


def _convert_literal_newlines(text):
    return _LITERAL_BACKSLASH_N_RE.sub(
        lambda m: "\n" if _is_real_newline_signal(text, m) else m.group(0), text
    )


# Un séparateur de ligne LaTeX (2 backslashes, contenu déjà correct) directement suivi
# d'une commande à backslash simple (ex. un système dont une ligne commence par
# "\sqrt3") forme une suite de 3 backslashes consécutifs, déjà correcte, jamais
# corrompue. Une commande doublée par une couche d'échappement en trop (\bar -> \\bar)
# en forme 2. La distinction ne peut donc PAS se faire sur "2 backslashes précis" :
# elle se fait sur la LONGUEUR TOTALE de la suite consécutive, via un argument de
# parité - une couche d'échappement en trop DOUBLE chaque backslash, donc une suite
# corrompue a TOUJOURS une longueur paire (2, 4, 6...) ; une suite de longueur IMPAIRE
# (1, 3, 5...) est mathématiquement la preuve qu'aucune corruption n'a eu lieu sur
# cette suite précise (repéré sur bac-c-e-maths-2025-cameroun/Proposition-Corrigé-
# Maths-BACC-C-E-2021, leçons 634/697/716/685 : "...\\begin{pmatrix}1\\\sqrt3\\
# end{pmatrix}..." - suite de 3 backslashes déjà correcte - perdait un backslash du
# séparateur, collapsée à tort en 2 par une règle qui ne regardait que la paire la
# plus proche de "sqrt", sans tenir compte du 3e backslash juste avant).
#
# On repère donc la suite ENTIÈRE (pas juste une paire) et on ne la réduit de moitié
# que si sa longueur est paire, jamais si elle est impaire - et seulement si au moins
# 2 lettres consécutives suivent (aucune commande LaTeX standard ne se limite à une
# seule lettre - protège aussi la variable isolée d'une ligne suivante, ex.
# "...=7\\a-2b-2c=18").
_BACKSLASH_RUN_BEFORE_LETTERS_RE = re.compile(r"\\+(?=[a-zA-Z]{2})")


def _halve_doubled_backslash_runs(text):
    def repl(match):
        run = match.group(0)
        return run[: len(run) // 2] if len(run) % 2 == 0 else run

    return _BACKSLASH_RUN_BEFORE_LETTERS_RE.sub(repl, text)


_MAX_UNESCAPE_LAYERS = 5


def _unescape_one_json_layer(value):
    """
    Défait un ou plusieurs niveaux d'échappement JSON en trop sur `value`, par
    substitution directe et ciblée (pas de ré-encapsulage + json.loads, voir "Erreur
    déjà rencontrée" ci-dessous) : convertit chaque "\\n" littéral en vrai saut de
    ligne (voir _is_real_newline_signal pour la désambiguïsation avec \\neq/\\nabla),
    et divise par 2 la longueur de chaque suite de backslashes suivie d'au moins 2
    lettres (commande LaTeX doublée), mais seulement si cette longueur est paire - voir
    _halve_doubled_backslash_runs pour l'argument de parité. Unicode-safe.
    Retourne (valeur_corrigée, a_changé).

    Erreur déjà rencontrée : une version précédente ré-encapsulait la chaîne entre
    guillemets et la reparsait via json.loads. Mais le jeu d'échappements valides de
    JSON (" \\ / b f n r t u) est bien plus étroit que celui de LaTeX - des commandes
    aussi courantes que "\\end{...}" ou "\\left(" (le 'e'/'l' ne sont pas des
    échappements JSON valides) déclenchaient une JSONDecodeError dès la 1ère
    itération, abandonnant toute correction du champ entier, y compris un saut de
    ligne bien réel ailleurs dans la même chaîne (bac-c-e-maths-2024/2025-cameroun,
    leçons 723/724, quasi systématique dès qu'un champ contient une matrice). La
    substitution directe ci-dessus ne dépend d'aucune grammaire d'échappement JSON,
    donc aucune commande LaTeX ne peut plus la faire échouer.

    Itère (jusqu'à _MAX_UNESCAPE_LAYERS fois) : certains champs ont été échappés plus
    d'une fois de trop (régénérations externes successives ?), un seul passage y
    laisserait le signal "\\n" littéral, détecté comme "encore cassé" à tort. S'arrête
    dès que le signal disparaît ou qu'un passage supplémentaire ne change plus rien.
    """
    if isinstance(value, str):
        current = value
        changed = False
        for _ in range(_MAX_UNESCAPE_LAYERS):
            if "\\" not in current:
                break
            candidate = _halve_doubled_backslash_runs(current)
            candidate = _convert_literal_newlines(candidate)
            if candidate == current:
                break
            current = candidate
            changed = True
            if not _has_literal_backslash_n(current):
                break
        return current, changed
    if isinstance(value, list):
        changed = False
        result = []
        for item in value:
            new_item, did_change = _unescape_one_json_layer(item)
            result.append(new_item)
            changed = changed or did_change
        return result, changed
    if isinstance(value, dict):
        changed = False
        result = {}
        for k, v in value.items():
            new_v, did_change = _unescape_one_json_layer(v)
            result[k] = new_v
            changed = changed or did_change
        return result, changed
    return value, False


def _repair_double_json_escaping(data):
    """
    Filet de sécurité mécanique pour un bug de double échappement JSON récurrent sur
    une partie du corpus ingest/ (fichiers régénérés hors de ce process en cours de
    session - voir mémoire projet "ingest folder external regeneration") : chaque
    backslash du contenu a été échappé une fois de trop avant l'écriture du fichier -
    "\\n" littéral là où un saut de ligne est attendu ("### Rappel de methode\\nOn
    cherche..." au lieu d'un vrai retour à la ligne), backslashes de commandes LaTeX
    doublés ("\\\\mathbb" au lieu de "\\mathbb"). Corrige à l'ingestion plutôt que de
    dépendre d'un nettoyage ponctuel des fichiers source, qui peut être défait par la
    régénération externe - une source figée n'est pas garantie ici.

    Parcourt tout le document à chaque ingestion (pas de garde-fou d'entrée bon marché
    sur un seul signal global) : une version précédente ne tentait la correction que si
    UN champ au moins portait le signal "\\n" littéral - or un champ peut avoir des
    commandes LaTeX doublées (\\\\mathbb) SANS aucun saut de ligne corrompu nulle part
    ailleurs dans le même document (champ court, une seule phrase), auquel cas ce
    garde-fou sautait le document entier à tort. L'ingestion n'étant pas un chemin
    chaud (import par lot, pas une requête utilisateur), le coût du parcours complet
    est négligeable face au risque de laisser un champ non corrigé. La décision de
    corriger ou non se prend champ par champ, voir _unescape_one_json_layer.
    """
    fixed, changed = _unescape_one_json_layer(data)
    return (fixed, True) if changed else (data, False)


# Séparateur de ligne LaTeX manquant à l'intérieur d'un environnement matriciel - une
# erreur d'AUTEUR (pas d'échappement JSON, voir _repair_double_json_escaping plus
# haut) : "\2a+b=0" au lieu de "\\2a+b=0" (un seul backslash au lieu de deux) casse le
# rendu (KaTeX affiche "\2" littéralement au lieu de sauter à la ligne suivante).
# Aucune commande LaTeX standard ne commence par un chiffre ou un signe moins juste
# après le backslash - ce motif, à l'intérieur d'un tel environnement, ne peut donc
# être qu'un séparateur de ligne manquant (repéré sur bac-c-e-maths-2024-cameroun,
# leçon 723, exercice 2, question 1 : les 3 lignes de la matrice et du système
# d'équations y étaient séparées par un seul backslash au lieu de deux, partout dans
# ce champ - rendu affichant "\2a+b+3c=0" et "\-a+b-3c=0" en toutes lettres).
_MATRIX_ENV_BLOCK_RE = re.compile(
    r"\\begin\{(cases|pmatrix|bmatrix|vmatrix|matrix|array)\}(.*?)\\end\{\1\}", re.DOTALL
)
_MISSING_ROW_SEPARATOR_RE = re.compile(r"(?<!\\)\\(?!\\)(?=[-\d])")


def _fix_missing_row_separators_in_text(text):
    def fix_block(env_match):
        env_name = env_match.group(1)
        body = _MISSING_ROW_SEPARATOR_RE.sub(r"\\\\", env_match.group(2))
        return f"\\begin{{{env_name}}}{body}\\end{{{env_name}}}"

    return _MATRIX_ENV_BLOCK_RE.sub(fix_block, text)


def _repair_missing_matrix_row_separators(value):
    if isinstance(value, str):
        fixed = _fix_missing_row_separators_in_text(value)
        return fixed, fixed != value
    if isinstance(value, list):
        changed = False
        result = []
        for item in value:
            new_item, did_change = _repair_missing_matrix_row_separators(item)
            result.append(new_item)
            changed = changed or did_change
        return result, changed
    if isinstance(value, dict):
        changed = False
        result = {}
        for k, v in value.items():
            new_v, did_change = _repair_missing_matrix_row_separators(v)
            result[k] = new_v
            changed = changed or did_change
        return result, changed
    return value, False


# "\hline" collé sans espace au token qui suit - erreur d'AUTEUR (pas d'échappement
# JSON) repérée sur bac-d-maths-1985/1989-cameroun : "\hlinex" ou "\hlineV_1V_2" au
# lieu de "\hline x" / "\hline V_1V_2" dans un tableau de variations. TeX/KaTeX lit un
# mot de commande comme consommant toute la suite de lettres qui suit directement, donc
# "\hlinex" est interprété comme la commande inconnue \hlinex plutôt que \hline suivi
# de "x" - "Undefined control sequence" côté KaTeX. Un espace après \hline est toujours
# neutre en LaTeX (jamais visible dans le rendu), donc l'insertion ne risque pas
# d'altérer un rendu déjà correct.
_GLUED_HLINE_RE = re.compile(r"\\hline(?=[a-zA-Z])")


def _fix_glued_hline_in_text(text):
    return _GLUED_HLINE_RE.sub(r"\\hline ", text)


def _repair_glued_hline(value):
    if isinstance(value, str):
        fixed = _fix_glued_hline_in_text(value)
        return fixed, fixed != value
    if isinstance(value, list):
        changed = False
        result = []
        for item in value:
            new_item, did_change = _repair_glued_hline(item)
            result.append(new_item)
            changed = changed or did_change
        return result, changed
    if isinstance(value, dict):
        changed = False
        result = {}
        for k, v in value.items():
            new_v, did_change = _repair_glued_hline(v)
            result[k] = new_v
            changed = changed or did_change
        return result, changed
    return value, False


# Spécificateur de colonnes d'un \begin{array}{...} trop court pour les lignes qu'il
# contient - erreur d'AUTEUR récurrente sur les tableaux de variations à plusieurs
# points de rupture (chaque point ajoute une colonne de valeur + une colonne de flèche,
# ce que la génération sous-compte systématiquement au-delà de 2-3 points). Repéré sur
# bac-d-maths-1985/1989/1991-cameroun et plusieurs bac-a-abi-maths-cameroun : la ligne
# "x" du tableau porte par exemple 12 cellules ("&"-séparées) quand le spécificateur
# n'en déclare que 10. KaTeX refuse ce désaccord ("Extra alignment tab has been changed
# to \cr" ou équivalent). On élargit uniquement (jamais on ne retire une colonne) en
# répétant le dernier spécificateur l/c/r rencontré : une colonne déclarée en trop est
# invisible au rendu (case vide), donc cette correction ne peut pas casser un tableau
# déjà correct - seulement en resynchroniser un qui, sinon, ne rendrait pas du tout.
_ARRAY_ENV_RE = re.compile(r"\\begin\{array\}\{([^}]*)\}(.*?)\\end\{array\}", re.DOTALL)
_ARRAY_COLSPEC_CHAR_RE = re.compile(r"[lcr]")
_ARRAY_LEADING_HLINE_RE = re.compile(r"^(?:\\hline\s*)+")


def _widen_array_colspec_if_needed(env_match):
    spec = env_match.group(1)
    body = env_match.group(2)
    declared = len(_ARRAY_COLSPEC_CHAR_RE.findall(spec))

    needed = 0
    for row in body.split("\\\\"):
        if not row.strip():
            continue
        cells = _ARRAY_LEADING_HLINE_RE.sub("", row).split("&")
        needed = max(needed, len(cells))

    if needed <= declared:
        return env_match.group(0)

    fill_char = (_ARRAY_COLSPEC_CHAR_RE.findall(spec) or ["c"])[-1]
    extra = fill_char * (needed - declared)
    new_spec = f"{spec[:-1]}{extra}|" if spec.endswith("|") else f"{spec}{extra}"
    return f"\\begin{{array}}{{{new_spec}}}{body}\\end{{array}}"


def _fix_narrow_array_columns_in_text(text):
    return _ARRAY_ENV_RE.sub(_widen_array_colspec_if_needed, text)


def _repair_narrow_array_columns(value):
    if isinstance(value, str):
        fixed = _fix_narrow_array_columns_in_text(value)
        return fixed, fixed != value
    if isinstance(value, list):
        changed = False
        result = []
        for item in value:
            new_item, did_change = _repair_narrow_array_columns(item)
            result.append(new_item)
            changed = changed or did_change
        return result, changed
    if isinstance(value, dict):
        changed = False
        result = {}
        for k, v in value.items():
            new_v, did_change = _repair_narrow_array_columns(v)
            result[k] = new_v
            changed = changed or did_change
        return result, changed
    return value, False


# Titre "**Exercice N**"/"**Problème**" absent en tête de l'énoncé - erreur d'AUTEUR
# massive et récurrente (280 des 491 exercices du corpus au 2026-08-03, toutes
# épreuves confondues, pas un incident isolé) : catalog.rendering._render_exercise_block()
# n'injecte JAMAIS ce titre lui-même (voir sa docstring - décision volontaire pour ne
# jamais dupliquer un repère déjà transcrit fidèlement depuis le sujet source), donc
# quand correction-experte omet ce titre dans enonce_intro_markdown, l'épreuve entière
# perd ses repères "Exercice 1"/"Exercice 2"/"Problème" côté lecture - constaté sur
# bac-d-maths-1994 à 1997, 1998, 2000, 2001, 2002, 2004-cameroun entre autres. Plutôt
# que corriger le JSON source à chaque nouvelle session de la compétence (déjà tenté
# deux fois, revient systématiquement - voir feedback_correction_experte_consistency),
# on fiabilise l'ingestion elle-même : `numero_exercice`/`points` sont des champs
# structurés déjà obligatoires (voir ingestion.REQUIRED_KEYS), donc le titre peut être
# reconstruit de façon déterministe et fiable à 100%, sans dépendre du bon vouloir de
# la génération.
#
# Ne devine JAMAIS pour une forme de numero_exercice ambiguë ("Probleme-IIA", "Section
# I", "B" seul...) : plusieurs Exercise "Probleme-*" distincts peuvent coexister sur la
# même épreuve (voir bac-c-maths-1985-cameroun), leur injecter à tous le même titre
# générique "**Problème**" créerait des repères dupliqués/ambigus pires que l'absence
# de titre - dans ce cas on laisse tel quel plutôt que de mal deviner.
#
# Ne devine pas non plus quand le texte commence déjà par un repère de partie ("**Partie
# B**", "**II.**"...) : repéré sur bac-c-maths-2017-cameroun, où le Problème d'une
# épreuve a été scindé en deux fichiers/Exercise distincts (exercice_4 = "Partie A",
# numero_exercice="4" ; exercice_5 = "Partie B", numero_exercice="5", purement
# numérique) - injecter "**Exercice 5**" devant "**Partie B**" fait croire à tort à un
# 5e exercice indépendant alors que c'est la suite du Problème précédent, et casse la
# numérotation visible (1, 2, 3, Problème, Exercice 5). Même regex que
# _flag_part_headers_in_intro (_INTRO_PART_HEADER_RE), ancrée en tête ici.
# Repère d'exercice en tête de texte, quel que soit son balisage : titre Markdown
# ("### Exercice 1 (6 points)"), gras ("**Exercice I : Chimie organique (5 pts)**") ou
# TEXTE NU ("Exercice 1 (5 points) - hydrocarbures, isomérie et synthèse du TNT").
# Cette dernière forme, non balisée, est celle qui manquait à l'ancienne version de
# cette détection (ancrée sur "**") : _repair_missing_exercise_heading croyait alors le
# repère absent et en injectait un SECOND juste au-dessus, ce qui donnait au lecteur
# jusqu'à trois occurrences d'affilée du même repère (voir _dedupe_exercise_heading).
# Le numéro est facultatif ("**Problème**" seul est un repère valide) et accepté en
# chiffres arabes comme en romains, avec ou sans "N°". "Exercise" (sans le "c") est le
# repère porté par les épreuves d'Anglais, rédigées dans la langue de l'épreuve elle-
# même ("**Exercise 1 (10 points)**", jamais "Exercice") - sans cette variante, ce
# repère pourtant bien présent passait inaperçu et _repair_missing_exercise_heading lui
# injectait un second repère "**Exercice N (points)**", français celui-là, juste
# au-dessus (bepc-anglais-2025-officiel + bac-c-d-anglais-2014, scan du 2026-08-30).
_EXERCISE_LABEL_RE = re.compile(
    r"^\s*(?:#{1,4}\s*)?(?:\*\*\s*)?(Exercice|Exercise|Probl[eè]me)\b\s*(?:n\s*[°ºo]\s*)?([IVXLC]+|\d+)?",
    re.IGNORECASE,
)

# Une ligne qui n'est QUE un titre, et rien d'autre : titre Markdown, ou ligne
# intégralement en gras (ponctuation finale tolérée). La distinction est vitale côté
# question, où la ligne de tête porte souvent le repère ET le début de l'énoncé sur la
# même ligne ("**Section D: Essay (10 marks).** Write an essay about...") - supprimer
# cette ligne entière au motif qu'elle commence par un repère effacerait l'énoncé.
_STANDALONE_HEADING_LINE_RE = re.compile(
    r"^\s*(?:#{1,4}\s*(?P<titre>.+?)|\*\*\s*(?P<gras>.+?)\s*\*\*)\s*[.:]?\s*$",
)

_ROMAN_DIGITS = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}

_PURE_NUMERIC_EXERCICE_RE = re.compile(r"^\d+$")


def _first_non_empty_line(text):
    """(première ligne non vide, tout le reste tel quel) - ("", "") si texte vide."""
    lines = text.split("\n")
    for index, line in enumerate(lines):
        if line.strip():
            return line, "\n".join(lines[index + 1:])
    return "", ""


def _normalize_heading_number(token):
    """
    Ramène le numéro d'un repère à une forme comparable entre deux écritures du même
    exercice : "I" et "1" désignent le même exercice quand l'intro le numérote en
    romain et la question en arabe (constaté sur les épreuves de chimie).
    """
    if not token:
        return ""
    token = token.lower()
    if token.isdigit():
        return str(int(token))
    if all(char in _ROMAN_DIGITS for char in token):
        total = 0
        highest = 0
        for char in reversed(token):
            value = _ROMAN_DIGITS[char]
            total += -value if value < highest else value
            highest = max(highest, value)
        return str(total)
    return token


def _exercise_label_key(text):
    """
    ("exercice", "1") pour un texte commençant par un repère d'exercice, quel que soit
    son balisage et son écriture du numéro - None sinon. Sert à la fois à constater
    qu'un repère est DÉJÀ présent (_repair_missing_exercise_heading) et à reconnaître
    deux écritures du MÊME repère (_dedupe_exercise_heading).
    """
    match = _EXERCISE_LABEL_RE.match(text)
    if not match:
        return None
    mot = "probleme" if match.group(1).lower().startswith("probl") else "exercice"
    return mot, _normalize_heading_number(match.group(2))


def _standalone_heading_content(line):
    """Texte d'une ligne qui n'est qu'un titre, débarrassé de son balisage - None si la
    ligne porte autre chose que le titre (voir _STANDALONE_HEADING_LINE_RE)."""
    match = _STANDALONE_HEADING_LINE_RE.match(line)
    if not match:
        return None
    return (match.group("titre") or match.group("gras")).strip()


def _build_exercise_heading(numero_exercice, points):
    numero = str(numero_exercice or "").strip()
    points_str = str(points or "").strip()
    suffix = f" ({points_str} points)" if points_str else ""
    if _PURE_NUMERIC_EXERCICE_RE.match(numero):
        return f"**Exercice {numero}{suffix}**"
    if numero.lower().replace("è", "e") == "probleme":
        return f"**Problème{suffix}**"
    return None


# `sections` (mode cours) attendu par catalog.rendering._render_cours_section/
# compile_cours_from_sections est une LISTE de blocs {"type": ..., ...} - forme
# unique et déjà majoritaire dans tout le corpus (voir n'importe quel `_cours_*.json`
# déjà ingéré sans erreur). Repéré sur 5 dossiers isolés mais denses (bac-c-maths-
# 1985/1986/1991/1992-cameroun, bac-c-maths-blanc-2003-cameroun - 124 fichiers cours
# au total, mais TOUS les cours de ces 5 dossiers, sans exception, jamais un mélange
# des deux formes au sein d'un même dossier) : une forme radicalement différente,
# un DICT à clés fixes ("accroche", "prerequis", "regle", "exemple_resolu",
# "erreurs_classiques", "exercices_application", "synthese"), où "regle"/
# "exemple_resolu" sont déjà les sous-objets attendus (juste sans clé "type"),
# "prerequis"/"erreurs_classiques"/"exercices_application" sont des listes nues
# (sans l'enveloppe {"items": [...]} attendue), et "accroche"/"synthese" sont des
# chaînes nues (au lieu de {"contenu_markdown": ...}/{"items_markdown": [...]}).
# Itérer un dict en Python donne ses CLÉS (des chaînes) : `for section in
# cours.sections_raw: section.get("type")` levait donc `'str' object has no
# attribute 'get'` sur chacun des 124 fichiers, pas une exception ponctuelle.
#
# Transformation purement mécanique et sans perte (chaque clé a une correspondance
# 1:1 vers la forme liste, tous les sous-champs déjà présents sont conservés tels
# quels) : cohérente avec le principe de ce module (défaut RÉCURRENT et
# systématique, jamais un mélange partiel à deviner au cas par cas - voir la
# docstring de tête). Vraisemblablement une ancienne convention de sortie du mode
# cours, avant qu'il ne se stabilise sur la forme liste utilisée partout ailleurs.
_COURS_SECTION_ORDER = [
    "accroche", "prerequis", "regle", "exemple_resolu",
    "erreurs_classiques", "exercices_application", "synthese",
]


def _normalize_cours_section_entry(section_type, value):
    if section_type == "accroche":
        return {"type": "accroche", "contenu_markdown": value if isinstance(value, str) else ""}
    if section_type == "prerequis":
        return {"type": "prerequis", "items": value if isinstance(value, list) else []}
    if section_type in ("regle", "exemple_resolu"):
        # Déjà la forme sous-objet attendue (titre/contenu_markdown/... ou
        # enonce_markdown/etapes/...) - il ne manque que la clé "type" elle-même.
        return {"type": section_type, **(value if isinstance(value, dict) else {})}
    if section_type in ("erreurs_classiques", "exercices_application"):
        return {"type": section_type, "items": value if isinstance(value, list) else []}
    if section_type == "synthese":
        items = value if isinstance(value, list) else ([value] if value else [])
        return {"type": "synthese", "items_markdown": items}
    # Clé imprévue : conservée plutôt que silencieusement perdue - _render_cours_section
    # ignore de toute façon tout "type" qu'il ne reconnaît pas (return "" par défaut).
    return {"type": section_type, "value": value}


# Séries annoncées par le NOM DU DOSSIER mais absentes du champ `serie` du JSON - 62
# dossiers / 244 fichiers au scan corpus du 2026-08-15 (chimie 20, anglais 19, physique
# 5, informatique 4, géographie 4, français 2, philo 2, lit-cg 2, maths 2, svt 1, éco 1).
# Conséquence directe pour l'élève : "bac-c-d-chimie-2003-cameroun" n'était rattachée
# qu'au cursus Série C, donc introuvable pour un candidat de Série D alors que l'épreuve
# est explicitement commune aux deux.
#
# Purement ADDITIF : on n'enlève jamais une série que le JSON est seul à connaître -
# 7 dossiers du corpus sont dans ce cas (ex. bac-c-maths-2019-cameroun, dont le JSON
# porte C et E quand le nom ne dit que "c"), et c'est alors le NOM qui est incomplet.
# Un token du nom qui n'est pas un code de série connu est ignoré, jamais une erreur :
# ce filet ne doit pas faire échouer une ingestion qui passait avant lui.
#
# Une CONTRADICTION franche (le nom dit D, le JSON dit E) n'est pas arbitrable ici et
# produit alors l'union des deux : 3 dossiers du corpus (bac-a-maths-2003,
# bac-c-svt-2015, probatoire-c-d-chimie-2013). Ces cas-là se tranchent sur le PDF
# source, en corrigeant celui des deux qui a tort - y compris en renommant le dossier
# quand c'est son nom qui se trompe, sans quoi ce filet réintroduirait la série fautive
# à chaque ingestion.
def _series_tokens_from_folder_name(folder_name, series_map):
    tokens = str(folder_name or "").lower().split("-")
    index = 1 if tokens and tokens[0] in ("bac", "probatoire", "bepc") else 0
    if tokens[:2] == ["bac", "blanc"]:
        index = 2
    found = []
    while index < len(tokens) and tokens[index] in series_map:
        found.append(tokens[index])
        index += 1
    return found


def _merge_series_from_folder_name(data, source_dir, series_map, split_series):
    if not isinstance(data, dict) or source_dir is None:
        return data, False

    du_nom = _series_tokens_from_folder_name(getattr(source_dir, "name", ""), series_map)
    if not du_nom:
        return data, False

    deja_la = {str(part).lower() for part in split_series(data.get("serie"))}
    manquantes = [token for token in du_nom if token not in deja_la]
    if not manquantes:
        return data, False

    existantes = [str(part) for part in split_series(data.get("serie"))]
    data = dict(data)
    data["serie"] = ", ".join([*existantes, *(token.upper() for token in manquantes)])
    return data, True


def _repair_dict_shaped_cours_sections(data):
    if not isinstance(data, dict):
        return data, False
    sections = data.get("sections")
    if not isinstance(sections, dict):
        return data, False

    ordered_keys = [key for key in _COURS_SECTION_ORDER if key in sections]
    ordered_keys += [key for key in sections if key not in ordered_keys]

    data = dict(data)
    data["sections"] = [_normalize_cours_section_entry(key, sections[key]) for key in ordered_keys]
    return data, True


def _has_own_reference_further_down(stripped, repere_propre):
    """
    True si une ligne de `stripped` (au-delà de la première, déjà vérifiée par
    l'appelant) porte déjà le repère de CET exercice - voir le commentaire de
    _repair_missing_exercise_heading juste au-dessus de son appel. `repere_propre`
    est le ("exercice"|"probleme", numéro normalisé) attendu pour CET exercice
    (dérivé de numero_exercice).

    Un numéro purement décimal ("Exercice 2") doit égaler celui de `repere_propre` à
    l'identique - garde-fou d'origine, qui évite qu'une référence à un AUTRE exercice
    ("comme vu à l'Exercice 3") fasse à tort passer celui-ci pour déjà titré. Un
    numéro romain ou lettré ("Exercice II", "Exercice a"), lui, est accepté quel que
    soit le numéro qu'il porte : ces écritures numérotent LOCALEMENT à leur propre
    Partie/groupe (I, II, III y redémarrent à chaque groupe - voir
    catalog.rendering._exercise_group_paths), donc ne peuvent par construction
    jamais coïncider avec numero_exercice (l'index global, à plat, de toute
    l'épreuve) - le exiger reviendrait à ne JAMAIS reconnaître le repère d'un
    exercice appartenant à une 2e Partie ou suivante.
    """
    for ligne in stripped.splitlines():
        match = _EXERCISE_LABEL_RE.match(ligne.strip())
        if not match:
            continue
        mot = "probleme" if match.group(1).lower().startswith("probl") else "exercice"
        if mot != repere_propre[0]:
            continue
        numero_brut = match.group(2)
        if numero_brut and not _PURE_NUMERIC_EXERCICE_RE.match(numero_brut):
            return True
        if _normalize_heading_number(numero_brut) == repere_propre[1]:
            return True
    return False


def _repair_missing_exercise_heading(data):
    if not isinstance(data, dict):
        return data, False

    intro = data.get("enonce_intro_markdown") or ""
    questions = data.get("questions") or []
    first_question_enonce = (questions[0].get("enonce_markdown") or "") if questions else ""
    text_to_check = intro if intro.strip() else first_question_enonce
    stripped = text_to_check.strip()

    heading = _build_exercise_heading(data.get("numero_exercice"), data.get("points"))
    if heading is None:
        return data, False

    # Le repère vit le plus souvent sur la première ligne : la chercher là plutôt que
    # sur le texte entier évite qu'un repère non balisé passe inaperçu (voir
    # _EXERCISE_LABEL_RE) et qu'un repère de partie SANS RAPPORT avec CET exercice
    # (ex. un "I." isolé servant à numéroter un item de QCM, pas une partie - voir
    # mémoire projet project_partie_header_dash_and_stacked_labels) fasse croire à tort
    # qu'un repère existe déjà. Un chapeau partagé par TOUTE l'épreuve précède parfois
    # le repère du tout premier exercice ("*L'épreuve comporte deux exercices et un
    # problème...*\n\n### Exercice 1 - 6 points\n\n...") : cette 4e condition cherche
    # spécifiquement LE REPÈRE DE CET EXERCICE sur une ligne plus loin dans le texte,
    # sans élargir la détection à un repère générique quelconque - constaté sur
    # mathematiques-probatoire-c-et-e-2000/2001/2002 (chapeau + titre Markdown "###")
    # et 6 exercices de physique BAC D (repère texte nu collé juste après, sans
    # chapeau) - scan corpus du 2026-08-19. Le numéro trouvé doit alors égaler
    # numero_exercice - SAUF s'il est romain/lettré (voir _has_own_reference_further_down) :
    # une Partie qui redémarre sa propre numérotation "I/II/III" à chaque groupe
    # (mathematiques-bepc-2000/2001/2002-cameroun, Partie B : "Exercice II"/"III" alors
    # que numero_exercice - l'index global de l'épreuve entière - vaut 5/6) ne peut par
    # construction JAMAIS coïncider avec numero_exercice ; exiger l'égalité dans ce cas
    # revient à ne jamais reconnaître le repère et à en injecter un second, faux, en
    # tête ("**Exercice 5 (1 points)**" devant "Exercice II (1 pt)" déjà présent plus
    # bas) - scan corpus du 2026-08-22.
    premiere_ligne, _ = _first_non_empty_line(stripped)
    repere_propre = _exercise_label_key(heading.strip("*"))
    # _INTRO_PART_HEADER_RE/_BARE_LETTERED_PART_HEADER_RE sont ancrés en tout DÉBUT de
    # texte : un chapeau d'épreuve entièrement en italique ("*MINESEC-DECC - BEPC - ... -
    # Session 2020*"), sans ligne vide qui l'annoncerait comme un cadre séparé, se
    # retrouve alors seul à occuper cette position, et les deux vérifications ne voient
    # plus le repère de groupe qui le suit directement ("**Partie A - ...**") - faux
    # "**Exercice 1**" injecté devant les deux (chapeau + repère de groupe réel) sur un
    # exercice qui EST la Partie, sans référence propre (comme "Partie B" pour l'exercice
    # suivant, jamais subordonné à celui-ci) - bepc-ecm-2020-officiel-cameroun, scan
    # corpus du 2026-08-30. `stripped` reste la base de _has_own_reference_further_down
    # ci-dessous : elle parcourt déjà tout le texte, chapeau compris.
    stripped_sans_chapeau = _skip_leading_italic_chapeau(stripped)
    if (
        _exercise_label_key(premiere_ligne)
        or _INTRO_PART_HEADER_RE.match(stripped_sans_chapeau)
        or _BARE_LETTERED_PART_HEADER_RE.match(stripped_sans_chapeau)
        or _BARE_EVALUATION_HEADER_RE.match(stripped_sans_chapeau)
        or _BARE_SITUATION_PROBLEME_HEADER_RE.match(stripped_sans_chapeau)
        or _BARE_COMPETENCE_LABEL_RE.match(stripped_sans_chapeau)
        or _has_own_reference_further_down(stripped, repere_propre)
    ):
        return data, False

    data = dict(data)
    data["enonce_intro_markdown"] = f"{heading}\n\n{intro}" if intro.strip() else heading
    return data, True


# Un seul "*...*" (pas "**...**") suivi d'un saut de ligne : un chapeau d'épreuve
# entièrement en italique, jamais la propre référence de l'exercice (voir
# _repair_missing_exercise_heading ci-dessus). Le lookahead négatif exclut "**" (un
# repère en gras ne doit jamais être confondu avec ce chapeau).
_LEADING_ITALIC_CHAPEAU_RE = re.compile(r"\A\*(?!\*)[^*\n]+\*\s*\n+")


def _skip_leading_italic_chapeau(stripped):
    """`stripped` sans son premier paragraphe s'il est entièrement en italique - inchangé
    sinon (y compris si `stripped` ne commence par aucun repère). Voir
    _LEADING_ITALIC_CHAPEAU_RE et son unique appelant ci-dessus."""
    match = _LEADING_ITALIC_CHAPEAU_RE.match(stripped)
    return stripped[match.end():] if match else stripped


# Paragraphe entièrement enveloppé d'italique ("*Cette partie comporte trois exercices
# indépendants I, II et III.*") - sous-titre de Partie au même titre qu'un repère "A -"/
# "Partie A" en gras (_INTRO_PART_HEADER_RE/_BARE_LETTERED_PART_HEADER_RE), mais jamais
# reconnu par ces deux regex (qui exigent "**", pas "*" seul) : sert de cadre au même
# titre pour _reposition_trailing_exercise_reference ci-dessous, sans quoi le repère
# "Exercice N" repositionné se retrouverait CALÉ ENTRE le titre de Partie et son propre
# sous-titre au lieu d'après les deux.
_ITALIC_ONLY_PARAGRAPH_RE = re.compile(r"\A\*(?!\*)[^*]+\*\Z")

# Repère de groupe "matière" à l'état brut, sans "Partie" ni numérotation - une épreuve
# combinant plusieurs matières (ex. Physique-Chimie) ouvre chaque bloc sur le seul nom de
# la matière ("**CHIMIE / 10 points**", puis plus loin "**PHYSIQUE / 10 points**" -
# chimie-probatoire-a-2019-a4-bilingue). Même détection que
# catalog.rendering._BARE_MATIERE_LABEL_RE/_is_bare_matiere_label, dupliquée ici plutôt
# qu'importée (voir la docstring de tête de ce fichier) : sans elle,
# _reposition_trailing_exercise_reference ne reconnaissait pas ce repère comme un CADRE et
# permutait à tort son propre repère de matière avec celui de l'exercice qui le suit
# ("**EXERCICE 1 : CHIMIE ORGANIQUE / 5 points**" se retrouvait AVANT "**CHIMIE / 10
# points**" au lieu d'après) - scan corpus du 2026-08-23,
# bac-a-abi-physique-chimie-2019-officiel-cameroun. EXCLUDE exclut explicitement
# "Exercice"/"Problème"/"Partie"/"Section" : sans lui, "EXERCICE 1 : ..." rejoindrait à
# tort le cadre au lieu de rester LE repère à repositionner.
_BARE_MATIERE_EXCLUDE_RE = re.compile(r"\A(?:Exercice|Probl[eè]me|Partie|Section)\b", re.IGNORECASE)
_BARE_MATIERE_LABEL_RE = re.compile(
    r"\A[A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜÇŒ][A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜÇŒ' \-]{1,40}?(?:\s*[/:]\s*[\d.,]+\s*(?:points?|pts?|marks?))?\Z",
)


def _is_bare_matiere_paragraph(paragraphe):
    contenu = _standalone_heading_content(paragraphe)
    if contenu is None:
        return False
    return bool(_BARE_MATIERE_LABEL_RE.match(contenu)) and not _BARE_MATIERE_EXCLUDE_RE.match(contenu)


def _split_paragraphs(text):
    """Paragraphes de `text` - blocs de lignes non vides séparés par une ou plusieurs
    lignes vides, chacun rejoint par un simple '\\n' (un bloc multi-lignes SANS ligne
    vide interne, comme un tableau Markdown, reste un seul paragraphe)."""
    paragraphes = []
    courant = []
    for ligne in text.split("\n"):
        if ligne.strip():
            courant.append(ligne)
        elif courant:
            paragraphes.append("\n".join(courant))
            courant = []
    if courant:
        paragraphes.append("\n".join(courant))
    return paragraphes


def _is_frame_paragraph(paragraphe):
    """True si `paragraphe` est un repère de CADRE (titre de Partie, repère de matière
    nue, sous-titre en italique) - jamais la propre référence de l'exercice, qui n'est
    pas un cadre mais LE repère à repositionner (voir _is_reference_paragraph)."""
    return bool(
        _INTRO_PART_HEADER_RE.match(paragraphe)
        or _BARE_LETTERED_PART_HEADER_RE.match(paragraphe)
        or _ITALIC_ONLY_PARAGRAPH_RE.match(paragraphe)
        or _is_bare_matiere_paragraph(paragraphe),
    )


def _is_reference_paragraph(paragraphe):
    """True si `paragraphe` n'est RIEN d'autre que la référence de l'exercice
    ("**Exercice N (points)**", "### Problème") - voir _standalone_heading_content/
    _exercise_label_key, déjà utilisés par _repair_missing_exercise_heading."""
    contenu = _standalone_heading_content(paragraphe)
    return contenu is not None and _exercise_label_key(contenu) is not None


def _reposition_trailing_exercise_reference(data):
    """
    Repère "Exercice N"/"Problème" présent dans enonce_intro_markdown mais placé APRÈS
    le préambule qu'il est censé annoncer, au lieu d'avant - constaté sur
    mathematiques-bepc-2000/2001/2002/2003-cameroun : correction-experte écrit le
    préambule partagé d'une Partie (chapeau + sous-titre + données/figure) puis SEULEMENT
    ENSUITE la référence propre de l'exercice ("Un magasin a fait une réduction de 25 %
    sur le prix de ses marchandises.\\n\\n**Exercice I (2 pts)**" au lieu de "**Exercice I
    (2 pts)**\\n\\nUn magasin a fait..."). _repair_missing_exercise_heading (ci-dessus) et
    _exercise_titre_et_points côté rendering.py savent déjà RETROUVER ce repère où qu'il
    soit dans le texte (voir _has_own_reference_further_down), donc le sommaire et le
    titre affiché étaient déjà corrects - mais le CORPS de l'énoncé, lui, montre le
    préambule avant son propre titre, ce qui se lit à l'envers (scan corpus du 2026-08-23).

    Le repère est déplacé juste après tout CADRE de tête déjà présent (titre de Partie et/
    ou son sous-titre en italique - voir _is_frame_paragraph) : un exercice qui ouvre sa
    Partie garde donc "Titre de Partie" > "Sous-titre" > "Exercice N" > préambule propre,
    jamais "Exercice N" intercalé entre le titre de Partie et son sous-titre. Un exercice
    SANS cadre de tête (le cas le plus courant, ex. l'Exercice II/III qui suit dans la même
    Partie) voit son repère déplacé tout en tête.

    Ne touche RIEN si le repère est déjà bien placé (immédiatement après le cadre, y
    compris quand il n'y a aucun cadre) : un paragraphe qui suit un repère déjà en bonne
    position n'est jamais confondu avec un second repère à déplacer, puisque la recherche
    d'un repère à repositionner ne se déclenche que si le paragraphe attendu à cette
    position n'EST PAS déjà ce repère.
    """
    if not isinstance(data, dict):
        return data, False
    intro = data.get("enonce_intro_markdown") or ""
    if not intro.strip():
        return data, False

    paragraphes = _split_paragraphs(intro.strip())
    if len(paragraphes) < 2:
        return data, False

    index_cadre = 0
    while index_cadre < len(paragraphes) and _is_frame_paragraph(paragraphes[index_cadre]):
        index_cadre += 1

    if index_cadre >= len(paragraphes) or _is_reference_paragraph(paragraphes[index_cadre]):
        return data, False

    index_reference = next(
        (i for i in range(index_cadre, len(paragraphes)) if _is_reference_paragraph(paragraphes[i])),
        None,
    )
    if index_reference is None:
        return data, False

    reste = paragraphes[:index_reference] + paragraphes[index_reference + 1:]
    nouveaux = reste[:index_cadre] + [paragraphes[index_reference]] + reste[index_cadre:]

    data = dict(data)
    data["enonce_intro_markdown"] = "\n\n".join(nouveaux)
    return data, True


# Même repère d'exercice porté À LA FOIS par enonce_intro_markdown et par la tête d'une
# de ses questions - doublon directement visible en lecture, puisque
# catalog.rendering.compile_exercise_from_questions concatène l'intro puis chaque
# enonce_markdown. Constaté sur 201 questions réparties sur 53 épreuves (scan corpus du
# 2026-08-15), avec jusqu'à TROIS occurrences d'affilée sur probatoire-c-d-chimie-2003 :
#
#     Exercice 1 (5 points)                                        <- injecté par
#                                                                     _repair_missing_exercise_heading
#     Exercice 1 (5 points) - hydrocarbures, isomérie et TNT        <- intro d'origine
#     Exercice 1 (5 points)                                        <- tête de la question
#
# La 1re occurrence disparaît d'elle-même depuis que ce filet reconnaît un repère non
# balisé (voir _EXERCISE_LABEL_RE) ; c'est la 3e que cette fonction retire.
#
# _dedupe_question_enonce ne rattrape pas ce cas : il ne retire de la question que le
# texte de l'intro recopié VERBATIM, or les deux repères diffèrent ici par leur balisage
# (gras contre texte nu) autant que par leur sous-titre.
#
# Le repère survivant est TOUJOURS celui de l'intro, jamais celui de la question :
# catalog.rendering.exercise_display_title lit la première ligne de l'intro pour
# alimenter le sommaire du lecteur - vider l'intro de son repère y viderait le sommaire.
# Quand la question porte le repère le plus informatif des deux (sous-titre absent de
# l'intro, ex. "Exercice 2 : Oxydoréduction (6 points)" contre "Exercice 2"), c'est ce
# texte-là qui est promu dans l'intro, dans le style de balisage que l'intro utilisait
# déjà : dédupliquer ne doit jamais faire perdre d'information.
def _promote_heading_into(ligne_intro, contenu):
    """Réécrit la ligne de repère de l'intro avec `contenu`, en conservant son balisage."""
    nue = ligne_intro.strip()
    titre_markdown = re.match(r"^(#{1,4}\s*)", nue)
    if titre_markdown:
        return f"{titre_markdown.group(1)}{contenu}"
    if nue.startswith("**"):
        return f"**{contenu}**"
    return contenu


# Une ligne réduite à son repère : le mot, son numéro, éventuellement le barème, et
# éventuellement un sous-titre introduit par un séparateur ("Exercice 1 (5 points) -
# hydrocarbures et isomérie"). Distingue ce repère d'une VRAIE phrase d'énoncé qui
# commencerait par le même mot ("Exercice 2 étudie la réaction suivante...") - seule la
# première est supprimable sans perte.
_POINTS_ENTRE_PARENTHESES_RE = re.compile(
    r"^\(\s*[\d.,/]+\s*(?:points?|pts?|marks?)\s*\)", re.IGNORECASE,
)
_DEBUT_DE_SOUS_TITRE_RE = re.compile(r"^[-–—:•]")


def _est_repere_seul(contenu):
    match = _EXERCISE_LABEL_RE.match(contenu)
    if not match:
        return False
    reste = _POINTS_ENTRE_PARENTHESES_RE.sub("", contenu[match.end():].strip()).strip()
    return not reste or bool(_DEBUT_DE_SOUS_TITRE_RE.match(reste))


def _collapse_intro_heading(ligne, reste):
    """
    Deux repères identiques empilés DANS l'intro elle-même - état hérité des épreuves
    ingérées avant que _repair_missing_exercise_heading ne sache reconnaître un repère
    non balisé : il en injectait un second au-dessus de celui qui existait déjà.
    Les fusionne en une seule ligne, qui garde le balisage du premier (le sommaire du
    lecteur ne sait lire qu'un titre Markdown ou un segment en gras - voir
    rendering.exercise_display_title) et le texte du plus informatif des deux.
    """
    suivante, apres = _first_non_empty_line(reste)
    if not suivante or _exercise_label_key(suivante) != _exercise_label_key(ligne):
        return ligne, reste, False

    contenu_suivant = _standalone_heading_content(suivante) or suivante.strip()
    if not _est_repere_seul(contenu_suivant):
        return ligne, reste, False

    contenu_actuel = _standalone_heading_content(ligne) or ligne.strip()
    if len(contenu_suivant) > len(contenu_actuel):
        ligne = _promote_heading_into(ligne, contenu_suivant)
    return ligne, apres, True


def _dedupe_exercise_heading(data):
    if not isinstance(data, dict):
        return data, False

    intro = data.get("enonce_intro_markdown") or ""
    ligne_intro, reste_intro = _first_non_empty_line(intro)
    cle_intro = _exercise_label_key(ligne_intro)
    if cle_intro is None:
        # Aucun repère dans l'intro : celui que porte éventuellement une question est
        # alors le seul du lot, donc légitime - c'est même le repli documenté
        # d'exercise_display_title. Rien à dédupliquer.
        return data, False

    ligne_gardee, reste_intro, modifie = _collapse_intro_heading(ligne_intro, reste_intro)
    questions = []
    for question in data.get("questions") or []:
        enonce = (question.get("enonce_markdown") or "") if isinstance(question, dict) else ""
        premiere, reste = _first_non_empty_line(enonce)
        contenu = _standalone_heading_content(premiere)
        if contenu is None or _exercise_label_key(contenu) != cle_intro:
            questions.append(question)
            continue

        if len(contenu) > len(_standalone_heading_content(ligne_gardee) or ligne_gardee.strip()):
            ligne_gardee = _promote_heading_into(ligne_gardee, contenu)
        question = dict(question)
        question["enonce_markdown"] = reste.lstrip("\n")
        questions.append(question)
        modifie = True

    if not modifie:
        return data, False

    data = dict(data)
    data["questions"] = questions
    data["enonce_intro_markdown"] = f"{ligne_gardee}\n{reste_intro}" if reste_intro else ligne_gardee
    return data, True


# `_dedupe_exercise_heading` ci-dessus ne dédoublonne le repère que s'il est porté par
# la PREMIÈRE LIGNE de l'intro (voir `_first_non_empty_line(intro)` en tête de cette
# fonction) - hypothèse qui échoue dès que l'intro s'ouvre sur un chapeau partagé par
# l'épreuve entière AVANT le repère de CET exercice (fiche d'identité en italique,
# "*Ministère des Enseignements Secondaires...*", "*L'épreuve comporte deux exercices
# et un problème...*") : le repère vit alors plus loin dans l'intro, sur sa DERNIÈRE
# ligne, juste avant le contenu propre à l'exercice - jamais reconnu par
# `_first_non_empty_line`, donc jamais dédupliqué par _dedupe_exercise_heading, qui
# rend la main sans rien faire dès que `cle_intro` est None.
#
# Constaté sur mathematiques-probatoire-c-1999-cameroun et -c-e-maths-2015/2016/2017/
# 2018-cameroun (repère répété À L'IDENTIQUE en tête de la première question, ex.
# "**EXERCICE 1 : 4 points**" à la fois en fin d'intro et en tête de Q1) et -c-e-maths-
# 2013-cameroun (répété SANS le barème : "**Exercice 1**" en tête de Q1 contre
# "**Exercice 1 (5 points)**" en fin d'intro) - scan corpus du 2026-08-22, 6 exercices
# au total, tous des probatoire C/E de mathématiques : cause commune, la fiche
# d'identité en italique que ces épreuves ouvrent désormais systématiquement n'existait
# pas encore quand _dedupe_exercise_heading a été écrite (elle ne connaît que le cas
# "repère nu en tête d'intro"). La comparaison entre les deux repères se fait par CLÉ
# (mot + numéro, voir _exercise_label_key), jamais par égalité de texte brut, pour
# absorber la variante 2013 sans se limiter à un doublon parfaitement identique.
def _last_bold_reference_line(intro):
    """Dernière ligne non vide de `intro` si elle se réduit à un repère d'exercice/
    problème en gras (voir _standalone_heading_content/_exercise_label_key) - None
    sinon. Ne cherche JAMAIS plus haut qu'elle : sur les 6 occurrences trouvées au scan
    corpus qui motive cette fonction, le repère vit toujours en dernière ligne d'intro,
    jamais ailleurs - remonter plus haut risquerait de confondre le repère avec une
    simple mention du mot "Exercice" dans le chapeau partagé de l'épreuve."""
    lignes = [ligne.strip() for ligne in (intro or "").split("\n") if ligne.strip()]
    if not lignes:
        return None
    contenu = _standalone_heading_content(lignes[-1])
    if contenu is None or _exercise_label_key(contenu) is None:
        return None
    return lignes[-1]


def _strip_duplicated_trailing_reference(intro, question_enonce):
    """`question_enonce` sans son repère de tête quand celui-ci répète (même clé
    mot+numéro, voir _exercise_label_key - jamais une égalité de texte brut, voir
    _last_bold_reference_line) la dernière ligne de `intro` - None si rien à retirer.

    Fonction pure (aucune dépendance à Question/Exercise) pour être réutilisable aussi
    bien à l'ingestion, sur le `data` JSON encore brut (voir
    _dedupe_trailing_exercise_reference ci-dessous), qu'en backfill rétroactif sur des
    Question déjà en base (voir la commande de management
    dedupe_trailing_exercise_reference)."""
    ligne_intro, _ = _first_non_empty_line(intro or "")
    if _exercise_label_key(ligne_intro) is not None:
        # Repère déjà en tête d'intro : c'est le cas que _dedupe_exercise_heading sait
        # déjà traiter - ne pas s'en mêler, pour ne jamais faire tourner les deux
        # réparations à la fois sur la même paire intro/question.
        return None

    ligne_reference = _last_bold_reference_line(intro)
    if ligne_reference is None:
        return None

    premiere_ligne, reste = _first_non_empty_line(question_enonce or "")
    contenu = _standalone_heading_content(premiere_ligne)
    if contenu is None or _exercise_label_key(contenu) != _exercise_label_key(ligne_reference):
        return None

    return reste.lstrip("\n")


def _dedupe_trailing_exercise_reference(data):
    """
    Variante JSON (ingestion) de _strip_duplicated_trailing_reference : applique la
    même réparation à la PREMIÈRE `questions[]` de `data`, seule position où ce
    doublon peut apparaître - Exercise.enonce_markdown compile intro puis questions
    dans l'ordre (voir catalog.rendering.compile_exercise_from_questions), donc seule
    la première question suit immédiatement l'intro dans le texte affiché.
    """
    if not isinstance(data, dict):
        return data, False

    questions = data.get("questions") or []
    if not questions or not isinstance(questions[0], dict):
        return data, False

    nouveau = _strip_duplicated_trailing_reference(
        data.get("enonce_intro_markdown") or "", questions[0].get("enonce_markdown") or "",
    )
    if nouveau is None:
        return data, False

    data = dict(data)
    questions = list(questions)
    questions[0] = {**questions[0], "enonce_markdown": nouveau}
    data["questions"] = questions
    return data, True
