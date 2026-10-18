"""
Règles « traiter n exercices sur m » appliquées à la note d'une simulation (Lesson.regles_choix).

`inedit.notation.calculer` somme TOUS les exercices : fidèle pour une épreuve où tout est
obligatoire, injuste pour un sujet du GCE qui demande « 4 questions sur 5 ». Ce module ajuste son
bilan, sans le modifier : seuls les n meilleurs exercices d'un groupe « parmi » comptent, les autres
sont marqués « non comptés » (ni barème, ni note, ni perte, ni révision).

- Les exercices traités sont classés par points obtenus ; un exercice traité mais pas encore noté
  est retenu d'office (l'élève n'a pas fini de se corriger).
- Si l'élève en traite moins de n, les places vides restent dues aux plus gros exercices non
  traités : laisser de côté un exercice se paie toujours.
- Règle « section_unique » (« toutes les questions dans UNE SEULE section ») : seule la section où l'élève
  a le mieux travaillé compte (le plus d'exercices traités, plafonné à n, puis le plus de points) ; les
  autres sont « non comptées », comme les exercices écartés d'une règle « parmi » - sans cela le barème
  additionnerait les 36 questions d'un sujet dont on n'en traite que 4.
- Les règles « ou » (jeux de sous-questions) et « consigne » n'ont aucun effet sur la note : informatives.
"""

from decimal import Decimal

from inedit import notation

from .cadre import simulation_a_la_question

ZERO = Decimal("0")


def _repere(texte):
    return " ".join(str(texte).split()).casefold()


def regles_parmi(lesson):
    return [r for r in (lesson.regles_choix or []) if isinstance(r, dict) and r.get("type") == "parmi"]


def _est_note(exercice, reponse):
    return notation.est_notee(exercice.questions.all()[0], reponse)


def regles_section_unique(lesson):
    return [r for r in (lesson.regles_choix or []) if isinstance(r, dict) and r.get("type") == "section_unique"]


def _retenir(groupe, n, fiche):
    """Les ids des n exercices de `groupe` ([(rang, exercice)]) qui comptent : les traités (en attente de
    notation d'abord, puis les mieux notés), puis - si l'élève en a traité moins de n - les plus gros non
    traités. Tout le groupe est retenu quand il ne dépasse pas n."""
    if len(groupe) <= n:
        return {e.id for _, e in groupe}
    traites = [x for x in groupe if fiche(x)[0]]
    traites.sort(key=lambda x: (not fiche(x)[1], -fiche(x)[2]))
    retenus = traites[:n]
    if len(retenus) < n:
        absents = sorted((x for x in groupe if not fiche(x)[0]), key=lambda x: -fiche(x)[3])
        retenus += absents[: n - len(retenus)]
    return {e.id for _, e in retenus}


def exercices_non_comptes(lesson, exercices, bilan, reponses):
    """{exercice.id} : les exercices écartés par les règles « parmi » et « section_unique ». `reponses` :
    {exercise_id: SimulationReponse} (la question d'un exercice a le pk de l'exercice)."""
    if simulation_a_la_question(lesson):
        return set()

    def fiche(element):
        i, e = element
        ligne = bilan["lignes"][i]
        reponse = reponses.get(e.id)
        traitee = ligne["traitee"]
        en_attente = traitee and not _est_note(e, reponse)
        return traitee, en_attente, ligne["obtenus"], ligne["points"]

    ecartes = set()
    for regle in regles_parmi(lesson):
        portee = _repere(regle["portee"])
        groupe = [
            (i, e) for i, e in enumerate(exercices)
            if portee in {_repere(g) for g in getattr(e, "groupes_bruts", [])}
        ]
        garde = _retenir(groupe, regle["repondre"], fiche)
        ecartes |= {e.id for _, e in groupe if e.id not in garde}

    for regle in regles_section_unique(lesson):
        n = regle["repondre"]
        sections = {}
        for i, e in enumerate(exercices):
            sections.setdefault(tuple(_repere(g) for g in getattr(e, "groupes_bruts", [])), []).append((i, e))

        def valeur(groupe):
            # Le plus d'exercices traités (plafonné à n), puis le plus de points obtenus sur les n meilleurs.
            traites = [x for x in groupe if fiche(x)[0]]
            meilleurs = sorted((fiche(x)[2] for x in traites), reverse=True)[:n]
            return min(len(traites), n), sum(meilleurs)

        # `max` garde la première section en cas d'égalité : rien traité, la première compte.
        choisie = max(sections.values(), key=valeur)
        garde = _retenir(choisie, n, fiche)
        ecartes |= {e.id for e in exercices if e.id not in garde}
    return ecartes


def calculer(simulation, exercices):
    """Bilan de `notation.calculer` ajusté des règles « parmi ». Ajoute au bilan :
    `non_comptes` (ids d'exercices écartés) ; chaque `par_exercice` reçoit `compte`."""
    bilan = notation.calculer(simulation, exercices)
    reponses = {r.exercise_id: r for r in simulation.reponses.all()}
    ecartes = exercices_non_comptes(simulation.lesson, exercices, bilan, reponses)

    for entree, exercice in zip(bilan["par_exercice"], exercices):
        entree["compte"] = exercice.id not in ecartes
    bilan["non_comptes"] = ecartes
    if not ecartes:
        return bilan

    lignes = []
    for i, exercice in enumerate(exercices):
        ligne = bilan["lignes"][i]
        if exercice.id not in ecartes:
            lignes.append(ligne)
            continue
        entree = bilan["par_exercice"][i]
        bilan["note"] -= entree["points_obtenus"]
        bilan["bareme"] -= entree["points_possibles"]
        bilan["questions_total"] -= 1
        if ligne["traitee"]:
            bilan["questions_traitees"] -= 1
            if not _est_note(exercice, reponses.get(exercice.id)):
                bilan["questions_a_noter"] -= 1
        else:
            bilan["questions_non_traitees"] -= 1
        entier = ligne["points"] > 0 and ligne["obtenus"] >= ligne["points"]
        for theme in exercice.questions.all()[0].themes.all():
            stats = bilan["par_theme"].get(theme.name)
            if stats is None:
                continue
            stats["points_possibles"] -= ligne["points"]
            stats["points_obtenus"] -= ligne["obtenus"]
            stats["total"] -= 1
            stats["reussies"] -= entier
            if stats["total"] <= 0:
                del bilan["par_theme"][theme.name]
    bilan["lignes"] = lignes
    return bilan


def regles_exposees(lesson, exercices):
    """Les règles de l'épreuve pour l'écran ; chaque règle « parmi » porte `exercices`, les ids
    des exercices qu'elle concerne (les repères de groupe affichés sont simplifiés : l'écran ne
    saurait pas les rapprocher de `portee`)."""
    exposees = []
    for regle in lesson.regles_choix or []:
        regle = dict(regle)
        if regle.get("type") == "parmi":
            portee = _repere(regle["portee"])
            regle["exercices"] = [
                e.id for e in exercices if portee in {_repere(g) for g in getattr(e, "groupes_bruts", [])}
            ]
        elif regle.get("type") == "section_unique":
            # La règle vaut pour toute l'épreuve : l'écran compte les exercices traités, toutes sections.
            regle["exercices"] = [e.id for e in exercices]
        exposees.append(regle)
    return exposees
