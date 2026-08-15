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
_INTRO_PART_HEADER_RE = re.compile(r"\*\*\s*(Partie\s+\S|[IVX]{1,4}\s*\.)", re.IGNORECASE)


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
    return not (next_pos < len(text) and text[next_pos].islower())


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
_EXERCISE_HEADING_PRESENT_RE = re.compile(r"^\*\*\s*(Exercice|Probl[eè]me)\b", re.IGNORECASE)
_PURE_NUMERIC_EXERCICE_RE = re.compile(r"^\d+$")


def _build_exercise_heading(numero_exercice, points):
    numero = str(numero_exercice or "").strip()
    points_str = str(points or "").strip()
    suffix = f" ({points_str} points)" if points_str else ""
    if _PURE_NUMERIC_EXERCICE_RE.match(numero):
        return f"**Exercice {numero}{suffix}**"
    if numero.lower().replace("è", "e") == "probleme":
        return f"**Problème{suffix}**"
    return None


def _repair_missing_exercise_heading(data):
    if not isinstance(data, dict):
        return data, False

    intro = data.get("enonce_intro_markdown") or ""
    questions = data.get("questions") or []
    first_question_enonce = (questions[0].get("enonce_markdown") or "") if questions else ""
    text_to_check = intro if intro.strip() else first_question_enonce

    stripped = text_to_check.strip()
    if _EXERCISE_HEADING_PRESENT_RE.match(stripped) or _INTRO_PART_HEADER_RE.match(stripped):
        return data, False

    heading = _build_exercise_heading(data.get("numero_exercice"), data.get("points"))
    if heading is None:
        return data, False

    data = dict(data)
    data["enonce_intro_markdown"] = f"{heading}\n\n{intro}" if intro.strip() else heading
    return data, True
