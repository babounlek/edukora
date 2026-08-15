"""
Traduit la sortie JSON de la compétence correction-experte vers nos modèles :
- Mode automatisation (un objet = un exercice) -> Lesson/Exercise/RappelDeMethode
  (ingest_exercise)
- Mode cours (un objet = un cours dérivé d'un rappel de méthode) -> Cours
  (ingest_cours)

Tolère à la fois l'ancienne nomenclature des séries (A, B, C, D, F, G) que
la compétence a pu utiliser avant sa mise à jour, et la nomenclature réelle
actuelle (A, SES, C, D, E, TI, COM) utilisée dans notre base.

Tolère aussi les épreuves communes à plusieurs séries (ex: Maths BAC C/E,
très courant au Cameroun) : le champ `serie` peut contenir plusieurs codes
séparés par un tiret, une virgule ou un slash ("C-E", "C, E", "C/E"), et le
champ `coefficient` peut être une valeur unique ou un objet {code_serie:
coefficient} quand il diffère selon la série (voir _format_coefficient).

Le pays n'est jamais lu dans le JSON (la compétence correction-experte ne le
fournit pas) : il est dérivé du chemin sur disque, convention
`ingest/<code_pays>/<epreuve>/...json` - voir _country_code_from_path.
"""

import json
import re
import unicodedata
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction

from .ingestion_repairs import (
    _dedupe_question_enonce,
    _flag_part_headers_in_intro,
    _repair_double_json_escaping,
    _repair_glued_hline,
    _repair_missing_exercise_heading,
    _repair_missing_matrix_row_separators,
    _repair_narrow_array_columns,
    _strip_em_dash,
)
from .models import Cours, Country, Cursus, Difficulte, Examen, Exercise, Figure, Lesson, LessonType, Origine, OrigineFigure, Question, RappelDeMethode, Series, StatutContenu, Subject, Tag, TypeReponse, _join_fr


class IngestionError(Exception):
    pass


def _normalize(value):
    if value is None:
        return ""
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    return text.strip().lower()


# "A-ABI" (vu sur au moins une épreuve source) : suffixe local sans rapport avec les
# vraies séries multiples ("C-E" = deux séries distinctes sur une même épreuve) -
# "ABI" n'est pas un code de série, juste une précision d'établissement/source sur
# une Série A classique. Retiré avant le découpage générique pour ne pas être pris
# pour une deuxième série inconnue.
_SERIE_NOISE_SUFFIX_RE = re.compile(r"-abi\b", re.IGNORECASE)


def _split_series(serie_raw):
    """'C-E' -> ['C', 'E'] ; 'C, E' -> ['C', 'E'] ; 'C' -> ['C'] ; 'A-ABI' -> ['A'] ;
    'D et TI' -> ['D', 'TI'] (vu sur bac-blanc-d-ti-physique-2025-cameroun)."""
    cleaned = _SERIE_NOISE_SUFFIX_RE.sub("", str(serie_raw or ""))
    parts = re.split(r"[,/\-–—\s]+", cleaned.strip())
    # "et" (conjonction française, jamais un code de série) n'a de sens comme séparateur
    # QUE lorsqu'il tombe entre deux vrais tokens (espaces des deux côtés dans la chaîne
    # d'origine) - un split générique sur tout espace le fait ressortir comme un token à
    # part entière au même titre que "D"/"TI", d'où le filtrage après coup plutôt qu'une
    # simple exclusion de motif dans le pattern de split lui-même.
    return [p for p in parts if p and p.lower() != "et"]


MATIERE_MAP = {
    "mathematiques": "MATHS",
    "maths": "MATHS",
    "physique-chimie": "PHYSIQUE_CHIMIE",
    "physique chimie": "PHYSIQUE_CHIMIE",
    # Certaines épreuves (ex. le Congo) traitent Physique et Chimie comme deux
    # matières distinctes sur la couverture, alors que le référentiel les regroupe
    # en une seule Subject PHYSIQUE_CHIMIE - voir Subject.
    "physique": "PHYSIQUE_CHIMIE",
    "chimie": "PHYSIQUE_CHIMIE",
    "sciences de la vie et de la terre": "SVT",
    "svt": "SVT",
    "francais": "FRANCAIS",
    "langue francaise": "FRANCAIS",
    "philosophie": "PHILOSOPHIE",
    "histoire-geographie": "HISTOIRE_GEO",
    "histoire geographie": "HISTOIRE_GEO",
    "histoire-geo": "HISTOIRE_GEO",
    "anglais": "ANGLAIS",
    "economie": "ECONOMIE",
    "droit": "DROIT",
    "litterature": "LITTERATURE",
    "litterature ou culture generale": "LITTERATURE",
    "culture generale": "LITTERATURE",
    "eps": "EPS",
    "education physique et sportive": "EPS",
    "education physique": "EPS",
}

# Tolère l'ancienne nomenclature (A/B/C/D/F/G) ET la nomenclature actuelle.
# a1/a2 : pas un alias de "A" mais le code réel de deux séries distinctes en Côte
# d'Ivoire (Lettres-Philosophie / Lettres-Langues, voir Series pour ce pays) - le
# Cameroun n'a qu'une série "A" unique, donc ces deux nomenclatures coexistent sans
# collision (Series.code n'est unique que par pays).
SERIE_MAP = {
    "a": "A",
    "a1": "A1",
    "a2": "A2",
    "b": "SES", "ses": "SES",
    "c": "C",
    "d": "D",
    "e": "E",
    "f": "TI", "ti": "TI",
    "g": "COM", "com": "COM",
}

EXAMEN_MAP = {
    "bepc": Examen.BEPC,
    "bfem": Examen.BEPC,  # nom sénégalais du même niveau (fin de collège) - voir ExamenLabel.
    "probatoire": Examen.PROBATOIRE,
    "bac": Examen.BAC,
    "autre": Examen.AUTRE,
    "devoir surveille": Examen.AUTRE,
}

DIFFICULTE_MAP = {
    "faible": Difficulte.FAIBLE,
    "moyenne": Difficulte.MOYENNE,
    "elevee": Difficulte.ELEVEE,
}

ORIGINE_MAP = {
    "officiel": Origine.OFFICIEL,
    "officielle": Origine.OFFICIEL,  # accord grammatical variant ("épreuve officielle") vu sur bac-d-maths-1994/1995/1996/1997-cameroun.
    # "compilation" : sujet officiel réel, simplement transcrit depuis un ouvrage
    # compilant plusieurs sessions plutôt que depuis le sujet de l'année seule (vu sur
    # bac-c-maths-2015-cameroun) - décision utilisateur du 2026-08-03 : traiter comme
    # un sujet officiel classique, sans distinction visible pour l'élève.
    "compilation": Origine.OFFICIEL,
    "examen blanc": Origine.BLANC,
    "blanc": Origine.BLANC,
    "etablissement": Origine.ETABLISSEMENT,
    "epreuve d'etablissement": Origine.ETABLISSEMENT,
    "autre": Origine.AUTRE,
}

REQUIRED_KEYS = [
    "epreuve_source", "numero_exercice", "matiere", "serie", "examen",
]


def _country_code_from_path(path):
    """
    Dérive le code pays (ex: "cm") du chemin sur disque : convention
    `ingest/<code_pays>/<epreuve>/...` (voir INGEST_DIR dans catalog.admin) - le
    sous-dossier direct sous le dossier littéralement nommé "ingest" porte le code
    pays. Fonctionne quel que soit le chemin passé à run_ingestion (dossier racine,
    sous-dossier pays, ou fichier unique) puisqu'on résout toujours le chemin absolu
    avant de chercher ce repère.
    """
    parts = path.resolve().parts
    lowered = [p.lower() for p in parts]
    if "ingest" not in lowered:
        return None
    idx = lowered.index("ingest")
    if idx + 1 >= len(parts):
        return None
    return parts[idx + 1]


def _resolve_country(code):
    if not code:
        raise IngestionError(
            "Impossible de déterminer le pays : le fichier ne se trouve pas sous "
            "un dossier ingest/<code_pays>/...",
        )
    try:
        return Country.objects.get(code__iexact=code)
    except Country.DoesNotExist:
        raise IngestionError(f"Pays inconnu : {code!r} - créez d'abord ce Country en base.")


def _resolve_subject(matiere_raw, country):
    code = MATIERE_MAP.get(_normalize(matiere_raw))
    if not code:
        raise IngestionError(
            f"Matière inconnue : {matiere_raw!r}. Attendu l'une de : {sorted(set(MATIERE_MAP.values()))}",
        )
    try:
        return Subject.objects.get(code=code, country=country)
    except Subject.DoesNotExist:
        raise IngestionError(f"Subject introuvable en base pour le code {code!r} et le pays {country}.")


def _resolve_cursus_list(examen_raw, serie_raw, country):
    """
    Retourne la liste des Cursus concernés (plusieurs si l'épreuve est commune à
    plusieurs séries), toujours filtrée par `country` : Examen est un référentiel
    partagé entre pays, mais Subject/Series/(country, examen, série) sont propres à
    chaque pays - sans ce filtre, deux pays partageant un même (examen, série) (ex:
    BAC Série C ailleurs qu'au Cameroun) feraient lever *.MultipleObjectsReturned.
    """
    examen = EXAMEN_MAP.get(_normalize(examen_raw))
    if not examen:
        raise IngestionError(f"Examen inconnu : {examen_raw!r}. Attendu BEPC/Probatoire/BAC/Autre.")

    if examen == Examen.BEPC:
        try:
            return [Cursus.objects.get(country=country, examen=examen, series__isnull=True)]
        except Cursus.DoesNotExist:
            raise IngestionError(f"Cursus BEPC introuvable en base pour {country}.")

    serie_parts = _split_series(serie_raw)
    if not serie_parts:
        raise IngestionError(f"Série manquante pour un examen {examen_raw!r} qui en requiert une.")

    cursus_list = []
    for part in serie_parts:
        series_code = SERIE_MAP.get(_normalize(part))
        if not series_code:
            raise IngestionError(
                f"Série inconnue : {part!r} (dans {serie_raw!r}). Attendu l'une de : {sorted(set(SERIE_MAP.values()))}",
            )
        try:
            series = Series.objects.get(code=series_code, country=country)
            cursus_list.append(Cursus.objects.get(country=country, examen=examen, series=series))
        except (Series.DoesNotExist, Cursus.DoesNotExist):
            raise IngestionError(f"Cursus introuvable pour pays={country}, examen={examen_raw!r}, série={part!r}.")

    return cursus_list


def _format_coefficient(coefficient_raw):
    """
    Le coefficient peut différer selon la série pour une même épreuve commune à
    plusieurs séries (ex: Maths coeff 7 en Série C, coeff 4 en Série E). La compétence
    transmet alors un objet {code_serie: coefficient} plutôt qu'une valeur unique -
    on le formate en chaîne lisible ("C : 7, E : 4") pour le champ d'affichage existant,
    sans changement de schéma. Une valeur simple (chaîne/nombre) passe telle quelle.
    """
    if isinstance(coefficient_raw, dict):
        return ", ".join(f"{serie} : {coef}" for serie, coef in coefficient_raw.items())
    return str(coefficient_raw or "")


def _resolve_origine(origine_raw):
    """Absent du JSON (compétence pas encore mise à jour, ou simplement omis pour un
    sujet officiel) -> OFFICIEL, le cas très largement majoritaire."""
    if not origine_raw:
        return Origine.OFFICIEL
    origine = ORIGINE_MAP.get(_normalize(origine_raw))
    if not origine:
        raise IngestionError(f"Origine inconnue : {origine_raw!r}. Attendu officiel/examen blanc/etablissement/autre.")
    return origine


_CHOIX_PREFIX_RE = re.compile(r"^\s*([A-Za-z])\)\s*(.*)$", re.DOTALL)


def _normalize_qcm_choix(choix_raw, reponse_correcte_raw):
    """
    Normalise `choix`/`reponse_correcte` vers le contrat interne attendu par Question
    (`choix`: [{"lettre": ..., "texte": "..."}], `reponse_correcte`: une lettre seule
    qui identifie un des `choix`) - correction-experte produit ce couple sous
    plusieurs formes observées en production, toutes légitimes :
    - `choix` en objets {lettre, texte} (le contrat documenté) - la lettre n'est pas
      forcément un caractère unique : un QCM d'appariement colonne A/colonne B utilise
      des codes composés ("b1", "b2", "b3"...), pas seulement a/b/c/d.
    - `choix` en chaînes "x) texte" (sans objet) - la lettre est alors extraite du
      préfixe.
    - `choix` en chaînes brutes sans aucune lettre (ex. Vrai/Faux : ["Vrai", "Faux"])
      - une lettre est alors synthétisée par position (a, b, c...), le texte reste la
      chaîne telle quelle.
    - `reponse_correcte` comme le texte complet du bon choix plutôt que sa seule
      lettre (constaté en production : la lettre seule est censée tenir dans
      `reponse_correcte` - max_length=10 - un texte complet dépasse largement et lève
      un DataError Postgres). Sans cette normalisation, la comparaison de correction
      (QuizAnswer.est_correcte) échouerait aussi silencieusement pour toute question
      ainsi mal formée : reponse_choisie est toujours une lettre (le bouton cliqué),
      jamais comparable à une phrase complète.
    """
    choix = []
    for index, item in enumerate(choix_raw or []):
        if isinstance(item, dict):
            lettre = str(item.get("lettre") or "").strip().lower()
            texte = _strip_em_dash(str(item.get("texte") or ""))
        else:
            match = _CHOIX_PREFIX_RE.match(str(item))
            if match:
                lettre, texte = match.group(1).lower(), _strip_em_dash(match.group(2).strip())
            else:
                lettre, texte = chr(ord("a") + index), _strip_em_dash(str(item).strip())
        choix.append({"lettre": lettre, "texte": texte})

    reponse_correcte_raw = str(reponse_correcte_raw or "").strip()
    lettres = {c["lettre"] for c in choix}

    if reponse_correcte_raw.lower() in lettres:
        # Correspondance directe avec une lettre de choix - couvre aussi bien "a" que
        # "b3" (QCM d'appariement), pas seulement les lettres à un caractère.
        reponse_correcte = reponse_correcte_raw.lower()
    else:
        match = _CHOIX_PREFIX_RE.match(reponse_correcte_raw)
        if match:
            reponse_correcte = match.group(1).lower()
        else:
            # Repli : reponse_correcte donné comme le texte d'un choix (sans lettre ni
            # préfixe "x) "), à faire correspondre par contenu plutôt que par position.
            texte_normalise = _strip_em_dash(reponse_correcte_raw)
            matching = next((c for c in choix if c["texte"] == texte_normalise), None)
            if not matching:
                raise IngestionError(
                    f"reponse_correcte ne correspond à aucune lettre ni à aucun texte de choix : {reponse_correcte_raw!r}",
                )
            reponse_correcte = matching["lettre"]

    return choix, reponse_correcte


def _get_or_create_tags(names):
    tags = []
    for name in names or []:
        name = _strip_em_dash(name).strip()
        if not name:
            continue
        tag, _ = Tag.objects.get_or_create(name=name)
        tags.append(tag)
    return tags


def _attach_figures(exercise, figures_data, source_dir):
    """
    Crée un Figure par entrée de `figures_data`, en lisant le PNG depuis `source_dir`
    (le dossier du fichier JSON source - voir SKILL.md "Traitement des figures et
    images" : les PNG sont livrés à côté des JSON de l'épreuve, jamais encodés dans
    le JSON). Réécrit ensuite chaque occurrence du nom de fichier original par l'URL
    réelle du fichier stocké, pour que le placeholder `![fig-N](nom_original.png)`
    pointe vers une image effectivement servable.

    Appelée après création des Question de `exercise` (voir ingest_exercise) : une
    figure peut être partagée par plusieurs sous-questions (ex. un graphique lu par
    la question 1 et exploité de nouveau en question 3), donc le placeholder est
    recherché dans le texte de chaque Question plutôt que dans un unique champ comme
    avant la scission en sous-questions - ainsi que dans enonce_intro_markdown, qui
    peut lui aussi référencer une figure partagée en préambule.
    """
    if not figures_data:
        return

    if source_dir is None:
        raise IngestionError("figures présentes dans le JSON mais aucun dossier source fourni pour résoudre les PNG.")

    questions = list(exercise.questions.all())
    illisibles_indispensables = []

    for fig_data in figures_data:
        filename = fig_data.get("fichier")
        fig_id = fig_data.get("id")
        if not filename or not fig_id:
            raise IngestionError(f"Figure incomplète (id/fichier manquant) : {fig_data!r}")

        image_path = source_dir / filename
        if not image_path.is_file():
            raise IngestionError(f"Fichier de figure introuvable : {image_path}")

        try:
            page_source = int(fig_data["page_source"]) if fig_data.get("page_source") not in (None, "") else None
        except (TypeError, ValueError):
            page_source = None

        indispensable = bool(fig_data.get("indispensable", True))
        lisibilite = str(fig_data.get("lisibilite") or "")
        origine = OrigineFigure.CORRIGE if _normalize(fig_data.get("origine_figure")) == "corrige" else OrigineFigure.ENONCE

        figure = Figure.objects.create(
            exercise=exercise,
            external_id=fig_id,
            image=ContentFile(image_path.read_bytes(), name=filename),
            page_source=page_source,
            type_figure=_strip_em_dash(str(fig_data.get("type") or "")),
            legende=_strip_em_dash(str(fig_data.get("legende") or "")),
            indispensable=indispensable,
            lisibilite=lisibilite,
            origine=origine,
        )

        for question in questions:
            enonce = question.enonce_markdown.replace(filename, figure.image.url)
            corrige = question.corrige_markdown.replace(filename, figure.image.url)
            if enonce != question.enonce_markdown or corrige != question.corrige_markdown:
                question.enonce_markdown = enonce
                question.corrige_markdown = corrige
                question.save(update_fields=["enonce_markdown", "corrige_markdown", "updated_at"])

        intro = exercise.enonce_intro_markdown.replace(filename, figure.image.url)
        if intro != exercise.enonce_intro_markdown:
            exercise.enonce_intro_markdown = intro
            exercise.save(update_fields=["enonce_intro_markdown", "updated_at"])

        if indispensable and _normalize(lisibilite) == "illisible":
            illisibles_indispensables.append(fig_id)

    # Filet de sécurité mécanique pour la règle SKILL.md ("figure indispensable et
    # illisible -> incertitude majeure, mentionnée en premier") : la compétence est
    # censée le signaler elle-même dans son JSON, mais on ne s'y fie pas à 100% - même
    # logique que la protection mécanique déjà en place pour l'em dash.
    if illisibles_indispensables:
        note = (
            f"Figure(s) indispensable(s) mais illisible(s) : {', '.join(illisibles_indispensables)} - "
            "questions dépendantes non fiables."
        )
        if note not in exercise.incertitudes:
            exercise.incertitudes = [note, *exercise.incertitudes]
            exercise.save(update_fields=["incertitudes"])


def ingest_exercise(data, source_dir=None, force=False):
    """
    Ingère un objet JSON (un exercice). Retourne (exercise, created).
    Lève IngestionError si les champs de classification ne peuvent pas être résolus.
    Idempotent par défaut : si un Exercise existe déjà pour ce (lesson, numero_exercice),
    il n'est jamais modifié - un ré-import ne recouvre pas une correction manuelle faite
    depuis.

    `force=True` outrepasse volontairement cette protection : l'Exercise existant est
    supprimé (cascade propre sur Question/Figure/RappelDeMethode - voir leurs
    `on_delete`) puis recréé depuis `data`, exactement comme une première ingestion.
    Réservé à un ré-import délibéré après correction du JSON source (voir l'action
    admin sur ExerciseAdmin) - jamais utilisé par `run_ingestion`/la tâche planifiée,
    qui doivent conserver le comportement idempotent par défaut.

    Valide et compile automatiquement : l'Exercise et le Lesson passent directement en
    VALIDE, et le Lesson est recompilé à chaque nouvel exercice ingéré - le contenu est
    donc immédiatement visible côté frontend, sans étape de validation manuelle. Le champ
    `statut` reste modifiable après coup (admin) pour retirer un contenu qui s'avère
    incorrect - ce n'est plus un verrou de publication, seulement un filtre a posteriori.

    `source_dir` : dossier où chercher les fichiers PNG référencés par `data["figures"]`
    (voir _attach_figures) - toujours le dossier du fichier JSON source, transmis par
    run_ingestion. Sert aussi, désormais, à déterminer le pays de l'épreuve (voir
    _country_code_from_path) : obligatoire même sans figures dans le JSON.

    `data["questions"]` porte la décomposition en sous-questions atomiques (voir
    catalog.models.Question) - toujours au moins une entrée, même pour un exercice à
    une seule question. enonce_markdown/corrige_markdown de l'Exercise ne sont plus lus
    depuis le JSON : ils sont compilés depuis les Question créées (voir
    Exercise.compile_from_questions), appelée en toute fin de cette fonction.
    """
    data, was_repaired = _repair_double_json_escaping(data)
    data, had_missing_separators = _repair_missing_matrix_row_separators(data)
    data, had_glued_hline = _repair_glued_hline(data)
    data, had_narrow_columns = _repair_narrow_array_columns(data)

    missing = [key for key in REQUIRED_KEYS if not data.get(key)]
    if missing:
        raise IngestionError(f"Champs obligatoires manquants : {missing}")

    questions_data = data.get("questions") or []
    if not questions_data:
        raise IngestionError("'questions' est requis et doit contenir au moins une entrée.")

    data, had_missing_heading = _repair_missing_exercise_heading(data)

    if source_dir is None:
        raise IngestionError("source_dir manquant : impossible de déterminer le pays de cet exercice.")
    country = _resolve_country(_country_code_from_path(source_dir))

    subject = _resolve_subject(data["matiere"], country)
    cursus_list = _resolve_cursus_list(data["examen"], data.get("serie"), country)

    year = None
    if data.get("annee"):
        try:
            year = int(data["annee"])
        except (TypeError, ValueError):
            raise IngestionError(f"Année invalide : {data['annee']!r}")

    epreuve_source = data["epreuve_source"]

    # Tout ce qui suit est all-or-nothing (y compris la création du Lesson s'il est
    # nouveau) : sans ce bloc, une IngestionError levée plus loin par _attach_figures
    # (ex. PNG manquant sur disque) laisserait un Lesson VALIDE déjà committé, avec
    # zéro exercice et un content_markdown vide - visible publiquement dans le
    # catalogue comme une fiche cassée, sans qu'un ré-import puisse la réparer (le
    # Lesson "existe déjà" et le reste de la fonction repart de cet état incohérent).
    with transaction.atomic():
        # cursus est M2M : ne peut pas faire partie de la clé de get_or_create.
        # Une épreuve est identifiée par (source, matière, année) ; le(s) cursus s'y ajoutent ensuite.
        # Filtré par pays (via cursus__country) pour ne jamais fusionner deux épreuves
        # de pays différents qui partageraient par coïncidence (source, matière, année)
        # - ex. deux "bac-blanc-maths-2024" non désambiguïsés dans leur epreuve_source.
        lesson = Lesson.objects.filter(
            epreuve_source=epreuve_source, subject=subject, year=year, lesson_type=LessonType.CORR,
            cursus__country=country,
        ).distinct().first()
        if lesson is None:
            # Regroupe par examen pour ne pas répéter le diplôme quand l'épreuve concerne
            # plusieurs séries : "BAC C et E" plutôt que "BAC - Série C / BAC - Série E".
            groups = {}
            for c in cursus_list:
                group = groups.setdefault(c.examen, {"examen_display": c.display_examen(), "series": []})
                if c.series:
                    group["series"].append(c.series.code)
            cursus_label = " / ".join(
                f"{g['examen_display']} {_join_fr(g['series'])}" if g["series"] else g["examen_display"]
                for g in groups.values()
            )
            origine = _resolve_origine(data.get("origine"))
            etablissement = str(data.get("etablissement") or "")

            # Jamais de suffixe "Corrigé" : ce titre est affiché tel quel sur des
            # surfaces qui ne montrent QUE le sujet (fiche catalogue, page détail
            # avant abonnement, en-tête du PDF de sujet public - voir sujet_pdf.py) -
            # y annoncer "Corrigé" est trompeur pour un visiteur qui n'y voit que
            # l'énoncé. Le statut "corrigé" se lit déjà via lesson_type ailleurs.
            title = f"{subject.label} {cursus_label} {year or ''}".replace("  ", " ").strip()
            if origine == Origine.ETABLISSEMENT and etablissement:
                # Sans ça, deux épreuves d'établissements différents pour le même
                # (matière, cursus, année) produisent des titres identiques -
                # indiscernables dans le catalogue tant qu'on n'a pas cliqué dessus.
                title = f"{title} - {etablissement}"

            lesson = Lesson.objects.create(
                epreuve_source=epreuve_source, subject=subject, year=year, lesson_type=LessonType.CORR,
                title=title, statut=StatutContenu.VALIDE,
                duree_epreuve=str(data.get("duree_epreuve") or ""),
                coefficient=_format_coefficient(data.get("coefficient")),
                origine=origine,
                etablissement=etablissement,
            )
        for cursus in cursus_list:
            lesson.cursus.add(cursus)

        # duree_epreuve/coefficient sont des attributs de l'épreuve entière, répétés par
        # exercice dans le JSON (même convention que matiere/serie/examen) : on complète
        # le Lesson si un exercice ultérieur les fournit alors que le premier ne les avait pas.
        update_fields = []
        if not lesson.duree_epreuve and data.get("duree_epreuve"):
            lesson.duree_epreuve = str(data["duree_epreuve"])
            update_fields.append("duree_epreuve")
        if not lesson.coefficient and data.get("coefficient"):
            lesson.coefficient = _format_coefficient(data["coefficient"])
            update_fields.append("coefficient")
        if not lesson.etablissement and data.get("etablissement"):
            lesson.etablissement = str(data["etablissement"])
            update_fields.append("etablissement")
        if update_fields:
            lesson.save(update_fields=[*update_fields, "updated_at"])

        numero_exercice = str(data["numero_exercice"])
        existing = Exercise.objects.filter(lesson=lesson, numero_exercice=numero_exercice).first()
        cours_par_external_id = {}
        if existing:
            if not force:
                return existing, False
            # cours_genere n'est qu'une propriété calculée (cours_id is not None), pas
            # un champ à part - un rappel déjà à l'origine d'un Cours perdrait cette
            # trace si on le laissait simplement disparaître avec l'Exercise supprimé.
            # On la restaure après recréation, en faisant correspondre par external_id
            # (unique=True, voir RappelDeMethode).
            cours_par_external_id = dict(
                existing.rappels_de_methode.exclude(cours__isnull=True).values_list("external_id", "cours_id"),
            )
            # Chemins relevés avant suppression : Figure cascade avec l'Exercise (voir
            # catalog.models), mais Django ne supprime jamais le fichier physique d'un
            # FileField quand la ligne qui le porte disparaît - sans ça, chaque
            # réingestion "force" (ex. action admin "Réingérer depuis le fichier JSON
            # source") laisserait l'ancienne image orpheline sur le disque/Spaces.
            # Même geste déjà fait par LessonAdmin.purge_view pour la même raison.
            figure_paths = list(existing.figures.exclude(image="").values_list("image", flat=True))
            existing.delete()
            for storage_path in figure_paths:
                if default_storage.exists(storage_path):
                    default_storage.delete(storage_path)

        points = str(data.get("points") or "").split("(")[0].strip()

        exercise = Exercise.objects.create(
            lesson=lesson,
            numero_exercice=numero_exercice,
            points=points,
            enonce_intro_markdown=_strip_em_dash(str(data.get("enonce_intro_markdown") or "")),
            incertitudes=data.get("incertitudes") or [],
            statut=StatutContenu.VALIDE,
        )

        exercise.mots_cles_recherche.set(_get_or_create_tags(data.get("mots_cles_recherche")))

        for ordre, q_data in enumerate(questions_data, start=1):
            if not q_data.get("enonce_markdown") or not q_data.get("corrige_markdown"):
                raise IngestionError(f"questions[{ordre - 1}] : enonce_markdown et corrige_markdown sont requis.")

            difficulte = DIFFICULTE_MAP.get(_normalize(q_data.get("difficulte_estimee")), "")
            type_reponse = TypeReponse.QCM if _normalize(q_data.get("type_reponse")) == "qcm" else TypeReponse.OUVERTE

            if type_reponse == TypeReponse.QCM:
                choix, reponse_correcte = _normalize_qcm_choix(q_data.get("choix"), q_data.get("reponse_correcte"))
            else:
                choix, reponse_correcte = [], ""

            enonce = _dedupe_question_enonce(_strip_em_dash(q_data["enonce_markdown"]), exercise.enonce_intro_markdown)
            question = Question.objects.create(
                exercise=exercise,
                numero=str(q_data.get("numero") or ordre),
                ordre=ordre,
                enonce_markdown=enonce,
                corrige_markdown=_strip_em_dash(q_data["corrige_markdown"]),
                difficulte_estimee=difficulte,
                type_reponse=type_reponse,
                choix=choix,
                reponse_correcte=reponse_correcte,
            )
            question.themes.set(_get_or_create_tags(q_data.get("themes")))

            for rappel_data in q_data.get("rappels_de_methode") or []:
                # _strip_em_dash appliqué identiquement ici et sur corrige_markdown
                # ci-dessus : _annotate_cours_links (voir models.py) fait correspondre
                # les deux par inclusion de chaîne exacte, donc une normalisation qui
                # diffère entre les deux casserait ce rapprochement silencieusement.
                # Le rappel reste rattaché à l'Exercise (pas à la Question) : Cours
                # continue de se générer au niveau de l'épreuve, pas de la sous-question.
                RappelDeMethode.objects.get_or_create(
                    external_id=rappel_data["id"],
                    defaults={
                        "exercise": exercise,
                        # `.get(key) or ""` et pas `.get(key, "")` : correction-experte
                        # émet parfois explicitement `null` plutôt que d'omettre la clé
                        # ou de tomber sur ""; hors valeur absente, `.get(key, "")` ne
                        # retourne son défaut que si la clé est absente, jamais si sa
                        # valeur JSON vaut déjà null - le None traverse alors jusqu'à
                        # la colonne NOT NULL (DataError Postgres constaté en prod).
                        "competence": _strip_em_dash(rappel_data.get("competence") or ""),
                        "contenu_markdown": _strip_em_dash(rappel_data.get("contenu_markdown") or ""),
                    },
                )

        _attach_figures(exercise, data.get("figures") or [], source_dir)
        _flag_part_headers_in_intro(exercise)
        if was_repaired:
            note = "Contenu source JSON doublement échappé, corrigé automatiquement à l'ingestion (voir _repair_double_json_escaping) - vérifier qu'aucune commande LaTeX n'a été altérée."
            if note not in exercise.incertitudes:
                exercise.incertitudes = [note, *exercise.incertitudes]
                exercise.save(update_fields=["incertitudes"])
        if had_missing_separators:
            note = "Séparateur de ligne LaTeX manquant dans une matrice/un système d'équations, corrigé automatiquement à l'ingestion (voir _repair_missing_matrix_row_separators) - vérifier le rendu."
            if note not in exercise.incertitudes:
                exercise.incertitudes = [note, *exercise.incertitudes]
                exercise.save(update_fields=["incertitudes"])
        if had_glued_hline:
            note = "\\hline collé au token suivant dans un tableau, corrigé automatiquement à l'ingestion (voir _repair_glued_hline) - vérifier le rendu."
            if note not in exercise.incertitudes:
                exercise.incertitudes = [note, *exercise.incertitudes]
                exercise.save(update_fields=["incertitudes"])
        if had_narrow_columns:
            note = "Spécificateur de colonnes trop court sur un \\begin{array}, élargi automatiquement à l'ingestion (voir _repair_narrow_array_columns) - vérifier le rendu."
            if note not in exercise.incertitudes:
                exercise.incertitudes = [note, *exercise.incertitudes]
                exercise.save(update_fields=["incertitudes"])
        if had_missing_heading:
            note = "Titre \"Exercice N\"/\"Problème\" absent de l'énoncé source, reconstruit automatiquement depuis numero_exercice/points à l'ingestion (voir _repair_missing_exercise_heading)."
            if note not in exercise.incertitudes:
                exercise.incertitudes = [note, *exercise.incertitudes]
                exercise.save(update_fields=["incertitudes"])
        exercise.compile_from_questions()

        if cours_par_external_id:
            for rappel in exercise.rappels_de_methode.filter(external_id__in=cours_par_external_id):
                rappel.cours_id = cours_par_external_id[rappel.external_id]
                rappel.save(update_fields=["cours"])

        lesson.compile_from_exercises()

    return exercise, True


def _link_rappels_lies(cours, source):
    """
    SKILL.md (mode cours) documente `source.rappels_lies` : d'autres rappels de la
    même épreuve, déjà ingérés, que ce même cours couvre aussi - cas du mode
    interactif où plusieurs blocs "### Rappel de méthode" fournis ensemble donnent
    lieu à un seul cours (le mode automatisation produit toujours un rappel par
    fichier cours, donc une liste vide). Sans ce rattachement, ces rappels
    resteraient cours_genere=false alors qu'un cours existe bel et bien pour eux -
    silencieux jusqu'à ce qu'un élève tombe dessus ailleurs dans la même épreuve.
    Best-effort : un identifiant introuvable est ignoré plutôt que de faire échouer
    tout l'ingestion du cours pour une donnée secondaire.
    """
    external_ids = source.get("rappels_lies") or []
    if external_ids:
        RappelDeMethode.objects.filter(external_id__in=external_ids).update(cours=cours)


def ingest_cours(data):
    """
    Ingère un objet JSON produit par le mode cours de correction-experte. Retourne
    (cours, created). Lève IngestionError si le rappel de méthode source (déjà ingéré
    via ingest_exercise) est introuvable - un cours ne peut pas exister sans épreuve
    source tracée. Idempotent via `cours_id` (external_id).

    Valide et compile automatiquement (voir ingest_exercise) : le Cours passe directement
    en VALIDE et son content_markdown est compilé avant de retourner - visible côté
    frontend dès l'ingestion, sans étape de validation manuelle.
    """
    data, _ = _repair_double_json_escaping(data)
    data, _ = _repair_missing_matrix_row_separators(data)

    meta = data.get("meta") or {}
    source = data.get("source") or {}

    cours_id = data.get("cours_id")
    if not cours_id or not meta.get("titre") or not meta.get("matiere") or not source.get("rappel_id"):
        raise IngestionError("Champs obligatoires manquants : cours_id, meta.titre, meta.matiere, source.rappel_id")

    try:
        rappel = RappelDeMethode.objects.select_related("exercise__lesson").get(external_id=source["rappel_id"])
    except RappelDeMethode.DoesNotExist:
        raise IngestionError(
            f"RappelDeMethode introuvable pour source.rappel_id={source['rappel_id']!r} - "
            "l'exercice source doit être ingéré avant le cours qui en dérive.",
        )

    existing = Cours.objects.filter(external_id=cours_id).first()
    if existing:
        return existing, False

    # Dédoublonnage par titre : une même notion (ex. "Résolution d'équations du second
    # degré") peut être extraite de plusieurs épreuves différentes - avec la génération
    # de cours désormais systématique côté compétence (voir SKILL.md), inutile de
    # publier un Cours quasi identique à chaque occurrence. Même mécanisme (titre
    # exact, insensible à la casse) que celui déjà utilisé pour lier les prérequis
    # entre cours (voir Cours._render_section) : on rattache ce nouveau rappel au
    # Cours existant plutôt que d'en créer un doublon.
    titre = _strip_em_dash(meta["titre"])
    duplicate = Cours.objects.filter(titre__iexact=titre, statut=StatutContenu.VALIDE).first()
    if duplicate:
        rappel.cours = duplicate
        rappel.save(update_fields=["cours"])
        _link_rappels_lies(duplicate, source)
        return duplicate, False

    # Un Cours n'a pas de dossier source à lui (pas de source_dir ici, contrairement à
    # ingest_exercise) : le pays se déduit du Cursus déjà résolu pour l'exercice dont
    # il dérive plutôt que d'être re-parsé - garanti non vide, cursus est obligatoire
    # sur Lesson (voir Lesson.cursus) et déjà peuplé à ce stade de l'ingestion.
    country = rappel.exercise.lesson.cursus.first().country
    subject = _resolve_subject(meta["matiere"], country)

    # all-or-nothing, même raison que le bloc équivalent d'ingest_exercise : sans ce
    # bloc, une exception levée par compile_from_sections() (ex. une forme de section
    # inattendue - voir Cours._render_section) laisserait un Cours VALIDE déjà
    # committé, avec un content_markdown vide - visible publiquement dans le
    # catalogue comme une fiche cassée, sans qu'un ré-import ne puisse la réparer
    # (le Cours "existe déjà" via external_id et le reste de la fonction repart de
    # cet état incohérent).
    with transaction.atomic():
        cours = Cours.objects.create(
            external_id=cours_id,
            titre=titre,
            subject=subject,
            sous_theme=_strip_em_dash(meta.get("sous_theme") or ""),
            duree_estimee_min=meta.get("duree_estimee_min") or None,
            sections_raw=_strip_em_dash(data.get("sections") or []),
            statut=StatutContenu.VALIDE,
        )

        # meta.serie/niveau ne portent pas l'examen (BEPC/Probatoire/BAC) requis pour
        # résoudre un Cursus - on hérite donc directement des cursus de l'épreuve source
        # plutôt que de re-parser ces champs. serie=null ("toutes séries") laisse cursus
        # vide : le cours reste alors accessible à tout abonné actif (voir has_access).
        if meta.get("serie"):
            cours.cursus.set(rappel.exercise.lesson.cursus.all())

        cours.tags.set(_get_or_create_tags(meta.get("tags")))
        cours.compile_from_sections()

        rappel.cours = cours
        rappel.save(update_fields=["cours"])
        _link_rappels_lies(cours, source)

    return cours, True


def run_ingestion(path):
    """
    Ingère tous les fichiers .json sous `path` (fichier unique, ou dossier - recherche
    récursive), qu'il s'agisse d'exercices (mode automatisation) ou de cours (mode
    cours). Point d'entrée partagé par la commande `ingest_corrections` et le bouton
    d'ingestion de l'admin, pour que les deux se comportent identiquement.

    Idempotent : ré-ingérer un fichier déjà traité ne recrée ni ne modifie rien (voir
    ingest_exercise/ingest_cours), donc relancer sur le même dossier sans le vider
    entre-temps est sans risque.

    Retourne {"files_found": int, "created": int, "skipped": int, "errors": [str, ...]}.
    """
    path = Path(path)
    # Tout composant de chemin préfixé par "_" (dossier ou fichier) est du tooling/état
    # interne, jamais du contenu à ingérer - convention déjà utilisée par "_quiz"
    # (sous-arbre réservé aux lots CompetenceItem du skill concepteur-quiz-competence,
    # voir quiz.ingestion.run_ingestion) et généralisée ici après un cas réel :
    # bac-blanc-d-ti-physique-2025-cameroun contenait un `_registry_dump.json` (état
    # interne de la génération) et un `_tmp_pages/` (crops PNG intermédiaires) laissés
    # par erreur dans l'arbre publié - un objet de ce genre n'a ni "epreuve_source" ni
    # "sections", donc atterrit dans exercice_items et fait échouer ingest_exercise sur
    # "Champs obligatoires manquants" à chaque ingestion, pour une erreur qui n'en est
    # pas une. Exclu ici plutôt que de laisser cette pollution se répéter à chaque
    # nouveau nom de fichier interne que la génération pourrait introduire.
    files = (
        [path] if path.is_file()
        else sorted(
            f for f in path.rglob("*.json")
            if not any(part.startswith("_") for part in f.relative_to(path).parts)
        )
    )

    # Un cours référence toujours un rappel de méthode déjà ingéré comme exercice
    # (source.rappel_id) : on ingère donc tous les exercices d'abord, puis tous les
    # cours, quel que soit l'ordre alphabétique des fichiers sur le disque.
    exercice_items = []
    cours_items = []
    errors = []

    for file_path in files:
        try:
            raw = json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(f"{file_path}: JSON invalide ({exc})")
            continue

        for data in raw if isinstance(raw, list) else [raw]:
            # Un objet "cours" (mode cours) porte "sections" ; un objet "exercice"
            # (mode automatisation) porte "corrige_markdown" - jamais les deux.
            if isinstance(data, dict) and "sections" in data:
                cours_items.append((file_path, data))
            else:
                exercice_items.append((file_path, data))

    created = 0
    skipped = 0
    lesson_ids = set()

    for file_path, data in exercice_items:
        # Fichier neutralisé intentionnellement (contenu dupliqué déjà fusionné dans un
        # autre fichier de l'épreuve, suppression physique refusée par l'utilisateur -
        # voir bac-c-e-maths-2015-cameroun_exercice_5.json) : "questions" y est laissé
        # vide pour signaler qu'il ne doit jamais être ingéré, mais ingest_exercise ne
        # connaît pas cette convention et lève IngestionError dessus à chaque lot -
        # une "erreur" qui n'en est pas une et qu'aucune correction de contenu ne peut
        # jamais faire disparaître. On l'ignore proprement ici, avant d'atteindre cette
        # validation, plutôt que de la compter comme un échec d'ingestion.
        if isinstance(data, dict) and str(data.get("statut", "")).startswith("obsolete"):
            skipped += 1
            continue
        try:
            exercise, was_created = ingest_exercise(data, source_dir=file_path.parent)
            lesson_ids.add(exercise.lesson_id)
            created += 1 if was_created else 0
            skipped += 0 if was_created else 1
        except Exception as exc:
            # Exception générique, pas seulement IngestionError : une erreur DB
            # inattendue (ex. DataError sur un champ mal formé par la compétence) ne
            # doit pas non plus planter tout le lot en cours de route et priver les
            # fichiers suivants d'être traités - chaque appel est déjà dans sa propre
            # transaction atomique (voir ingest_exercise), donc annuler celle-ci et
            # continuer est sans risque pour les autres fichiers.
            numero = data.get("numero_exercice", "?") if isinstance(data, dict) else "?"
            errors.append(f"{file_path} (exercice {numero}): {exc}")

    for file_path, data in cours_items:
        try:
            _, was_created = ingest_cours(data)
            created += 1 if was_created else 0
            skipped += 0 if was_created else 1
        except Exception as exc:
            cours_id = data.get("cours_id", "?") if isinstance(data, dict) else "?"
            errors.append(f"{file_path} (cours {cours_id}): {exc}")

    return {
        "files_found": len(files), "created": created, "skipped": skipped, "errors": errors,
        "lesson_ids": sorted(lesson_ids),
    }
