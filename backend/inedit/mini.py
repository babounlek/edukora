"""
Mini-inédites : 2 exercices tirés d'épreuves inédites déjà publiées du même cursus, matérialisés en une vraie
EpreuveInedite (est_mini=True). Tout le reste du module (tentative, chrono, notation, bilan par compétence,
révision espacée) fonctionne alors sans aucune modification : une mini-inédite EST une épreuve, juste plus courte.

Choix de conception :
- copie, pas référence : les questions gardent leurs points, critères de notation, thèmes et rappels de méthode ;
  la mini ne casse jamais si l'épreuve source est retirée ou corrigée plus tard ;
- tirage déterministe et idempotent : mêmes sources -> mêmes minis (external_id `mini-<groupe>-<n>`), rejouable sans doublon ;
- 2 exercices d'épreuves DIFFÉRENTES, de thèmes différents quand c'est possible, sans renvoi à un autre exercice ;
- durée proportionnelle au barème de l'épreuve d'origine, arrondie aux 5 minutes (20 à 60 min) ; un exercice qui
  demanderait plus de 35 minutes n'est jamais retenu : la durée affichée reste honnête, jamais plafonnée.
"""
import re
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from catalog.models import StatutContenu

from .models import (
    Blueprint, EpreuveInedite, ExerciceInedite, QuestionInedite, RappelDeMethodeInedite, cle_numero_exercice,
)

DUREE_MIN, DUREE_MAX = 20, 60
MINUTES_MAX_PAR_EXERCICE = 35  # au-delà, l'exercice est un morceau de bravoure, pas un format « mini »
QUESTIONS_MAX_PAR_EXERCICE = 6
# Un exercice qui renvoie à un autre (« d'après l'exercice 1 », « la fonction de la partie A ») ne tient pas seul.
_RENVOI = re.compile(r"\b(exercice|partie)\s+(\d+|[IVX]+|[A-D])\b", re.IGNORECASE)


def _nombre(texte):
    try:
        return Decimal(str(texte or "").replace(",", ".").strip())
    except InvalidOperation:
        return None


def _points_exercice(exercice):
    pts = _nombre(exercice.points)
    if pts is not None and pts > 0:
        return pts
    somme = sum((_nombre(q.points) or Decimal(0)) for q in exercice.questions.all())
    return somme if somme > 0 else None


def _renvoie_ailleurs(exercice):
    textes = [exercice.enonce_intro_markdown] + [q.enonce_markdown for q in exercice.questions.all()]
    return any(_RENVOI.search(t or "") for t in textes)


def candidats(epreuve):
    """Exercices utilisables d'une épreuve : autonomes, de taille raisonnable, avec un barème et une durée estimée."""
    exercices = list(epreuve.exercices.prefetch_related("questions__themes", "rappels_de_methode"))
    total = sum((_points_exercice(e) or Decimal(0)) for e in exercices)
    duree = epreuve.blueprint.duree_minutes
    sortie = []
    for e in exercices:
        pts = _points_exercice(e)
        nb = e.questions.count()
        if not pts or not total or not duree or nb == 0 or nb > QUESTIONS_MAX_PAR_EXERCICE or _renvoie_ailleurs(e):
            continue
        minutes = float(Decimal(duree) * pts / total)
        if minutes > MINUTES_MAX_PAR_EXERCICE:
            continue
        themes = {t.pk for q in e.questions.all() for t in q.themes.all()}
        sortie.append({"epreuve": epreuve, "exercice": e, "minutes": minutes, "points": pts, "themes": themes})
    return sortie


def choisir_paires(epreuves, nombre):
    """Jusqu'à `nombre` paires d'exercices, déterministes : exercices triés du plus court au plus long, deux exercices
    d'épreuves différentes, thèmes disjoints de préférence, aucun exercice réutilisé."""
    tous = sorted(
        (c for e in epreuves for c in candidats(e)),
        key=lambda c: (c["minutes"], c["epreuve"].pk, cle_numero_exercice(c["exercice"].numero_exercice)),
    )
    utilises, paires = set(), []
    for _ in range(nombre):
        meilleure = None
        for i, a in enumerate(tous):
            if a["exercice"].pk in utilises:
                continue
            for b in tous[i + 1:]:
                if b["exercice"].pk in utilises or b["epreuve"].pk == a["epreuve"].pk:
                    continue
                disjoints = not (a["themes"] & b["themes"])
                cout = (0 if disjoints else 1, a["minutes"] + b["minutes"])
                if meilleure is None or cout < meilleure[0]:
                    meilleure = (cout, a, b)
                break  # le premier partenaire valide est le plus court : inutile d'aller plus loin pour ce a
        if meilleure is None:
            break
        _, a, b = meilleure
        utilises |= {a["exercice"].pk, b["exercice"].pk}
        paires.append((a, b))
    return paires


def duree_mini(a, b):
    total = a["minutes"] + b["minutes"]
    arrondi = int(round(total / 5.0)) * 5
    return max(DUREE_MIN, min(DUREE_MAX, arrondi))


@transaction.atomic
def construire(cle_groupe, titre_base, cursus, sujet, paire, numero):
    """Crée (ou renvoie, si déjà faite) la mini-inédite n° `numero` du groupe `cle_groupe`."""
    a, b = paire
    external_id = f"mini-{cle_groupe}-{numero}"
    existante = EpreuveInedite.objects.filter(external_id=external_id).first()
    if existante is not None:
        return existante, False
    minutes = duree_mini(a, b)
    competences = {t for c in (a, b) for q in c["exercice"].questions.all() for t in q.themes.all()}
    blueprint = Blueprint.objects.create(
        external_id=f"mini-bp-{cle_groupe}-{numero}", subject=sujet, titre=f"{titre_base} n°{numero}",
        sections_plan=[
            {"section": f"Exercice {i}", "source": f"{c['epreuve'].external_id or c['epreuve'].pk} / {c['exercice'].numero_exercice}"}
            for i, c in enumerate((a, b), start=1)
        ],
        duree_minutes=minutes, bareme_total=None, statut=StatutContenu.VALIDE,
    )
    blueprint.cursus.set(cursus)
    blueprint.competences.set(competences)
    epreuve = EpreuveInedite.objects.create(
        blueprint=blueprint, external_id=external_id, subject=sujet, titre=f"{titre_base} n°{numero}",
        statut=StatutContenu.VALIDE, published_at=timezone.now(), est_mini=True,
        sources_mini=[{"epreuve": c["epreuve"].pk, "exercice": c["exercice"].numero_exercice} for c in (a, b)],
    )
    epreuve.cursus.set(cursus)
    for rang, c in enumerate((a, b), start=1):
        source = c["exercice"]
        copie = ExerciceInedite.objects.create(
            epreuve=epreuve, numero_exercice=str(rang), points=source.points, groupes=source.groupes,
            enonce_intro_markdown=source.enonce_intro_markdown,
        )
        for q in source.questions.order_by("ordre"):
            nouvelle = QuestionInedite.objects.create(
                exercice=copie, numero=q.numero, ordre=q.ordre, groupe_local=q.groupe_local,
                enonce_markdown=q.enonce_markdown, corrige_markdown=q.corrige_markdown,
                difficulte_estimee=q.difficulte_estimee, type_reponse=q.type_reponse, choix=q.choix,
                reponse_correcte=q.reponse_correcte, points=q.points, criteres_notation=q.criteres_notation,
            )
            nouvelle.themes.set(q.themes.all())
        for i, rappel in enumerate(source.rappels_de_methode.all(), start=1):
            RappelDeMethodeInedite.objects.create(
                exercice=copie, external_id=f"rdi-{external_id}-ex{rang}-{i}", competence=rappel.competence,
                contenu_markdown=rappel.contenu_markdown, cours=rappel.cours,
            )
    epreuve.compile_from_exercices()
    return epreuve, True


def creer_pour_matiere(code_matiere="MATHS", par_groupe=3, a_blanc=False):
    """Crée les mini-inédites de toutes les épreuves inédites VALIDES (non mini) de la matière, groupées par ensemble de
    cursus. Renvoie [(groupe, titre, durée, sources, créée?)]. `a_blanc` : calcule sans rien écrire."""
    from collections import defaultdict

    groupes = defaultdict(list)
    for e in (EpreuveInedite.objects.filter(subject__code=code_matiere, statut=StatutContenu.VALIDE, est_mini=False)
              .select_related("subject", "blueprint").prefetch_related("cursus__series", "cursus__country")):
        cursus = tuple(sorted(c.pk for c in e.cursus.all()))
        groupes[cursus].append(e)
    rapport = []
    for cursus_ids, epreuves in sorted(groupes.items()):
        paires = choisir_paires(epreuves, par_groupe)
        cursus = list(epreuves[0].cursus.all())
        libelle = " / ".join(sorted({c.examen if not c.series else f"{c.examen} {c.series.code}" for c in cursus}))
        cle = "-".join(str(i) for i in cursus_ids)
        titre = f"Mini-inédite Mathématiques {libelle}"
        for numero, paire in enumerate(paires, start=1):
            if a_blanc:
                rapport.append((cle, f"{titre} n°{numero}", duree_mini(*paire),
                                [(c["epreuve"].pk, c["exercice"].numero_exercice) for c in paire], None))
                continue
            epreuve, creee = construire(cle, titre, cursus, epreuves[0].subject, paire, numero)
            rapport.append((cle, epreuve.titre, epreuve.blueprint.duree_minutes, epreuve.sources_mini, creee))
    return rapport
