"""
Bulletin prévisionnel (audit produit 2026-11-13, R15) : par matière, une FOURCHETTE de note sur 20, jamais un chiffre exact.

AFFICHAGE CONDITIONNÉ (décision 3 de l'audit) : une note estimée engage la crédibilité du produit ; elle n'est visible qu'une fois
relue par un enseignant (settings.NOTE_ESTIMEE_ACTIVE) ou par le personnel pour cette relecture. Le calcul, lui, est complet.
La méthode est décrite pour une relecture humaine dans docs-relecture/note-estimee-methode.md ; tout seuil ci-dessous y figure.

Le modèle, volontairement simple :
- Une matière est un ensemble de thèmes (quiz.services.groupes_par_frequence) ; le poids d'un thème est la part des épreuves
  officielles où il est tombé (sa fréquence), ramenée à 1 sur la matière.
- La maîtrise d'un thème est estimée sur les réponses de l'élève (maitrise_par_theme : les rejeux et les quiz chronométrés sont
  neutres) par la moyenne a posteriori d'une loi Bêta(1, 1) : (réussies + 1) / (réponses + 2).
- Les thèmes sont très nombreux (plus de 400 en Mathématiques BEPC) : un élève n'en tente qu'une petite part. Note = 20 × maîtrise
  moyenne des thèmes TENTÉS, pesés par leur fréquence (les autres sont supposés leur ressembler). La fourchette vient de la
  variance Bêta des thèmes tentés, plus ce qu'on ignore des autres : HETEROGENEITE_THEMES × (part non couverte), ± 1,28
  écart-type (environ 80 %), jamais plus étroite que LARGEUR_MIN_POINTS. Peu de thèmes tentés = fourchette large.
- RECALAGE : un quiz mesure moins que l'examen. Avec au moins SIMULATIONS_MIN examens blancs rendus dans la matière, la note est
  la moyenne du quiz et de celle des examens blancs, et la fourchette s'élargit de leur écart. Sans, la note est dite « à confirmer ».
- Affichée seulement après REPONSES_MIN_MATIERE réponses et quand les thèmes réellement tentés pèsent au moins COUVERTURE_MIN
  de la matière : en dessous, on dit combien il manque, on ne devine pas.
"""
from math import sqrt

from catalog.models import StatutContenu, Subject

from .matieres import restreindre_matieres
from .services import COEFFICIENT_PAR_DEFAUT, _coefficient_par_subject, groupes_par_frequence, maitrise_par_theme

REPONSES_MIN_MATIERE = 20
COUVERTURE_MIN = 0.15
HETEROGENEITE_THEMES = 0.2  # écart-type supposé de la maîtrise d'un thème à l'autre (en part de 1) : l'incertitude des thèmes non tentés
SIMULATIONS_MIN = 2
Z_80 = 1.28
LARGEUR_MIN_POINTS = 2
THEMES_RENTABLES = 3
GAIN_MIN_POINTS = 0.1


def _fourchette(centre, ecart_type):
    bas = round(centre - Z_80 * ecart_type)
    haut = round(centre + Z_80 * ecart_type)
    bas, haut = max(0, bas), min(20, haut)
    while haut - bas < LARGEUR_MIN_POINTS:  # trop étroite : un élève lirait une précision que le calcul n'a pas
        if bas > 0:
            bas -= 1
        if haut - bas < LARGEUR_MIN_POINTS and haut < 20:
            haut += 1
    return bas, haut


def _notes_des_examens_blancs(profil, cursus, subject):
    """Les notes sur 20 des examens blancs rendus (annales) de cette matière, pour recaler le quiz."""
    from simulations.models import SimulationEpreuve

    notes = []
    for s in SimulationEpreuve.objects.filter(
        profil=profil, submitted_at__isnull=False, lesson__subject=subject, lesson__cursus=cursus,
        note_obtenue__isnull=False, bareme_snapshot__gt=0,
    ).only("note_obtenue", "bareme_snapshot"):
        notes.append(20 * float(s.note_obtenue) / float(s.bareme_snapshot))
    return notes


def _matiere(profil, cursus, subject, maitrise):
    base = {"subject_id": subject.id, "subject_label": subject.label, "subject_code": subject.code}
    frequences = groupes_par_frequence(cursus, subject)
    if frequences is None or not frequences[3]:
        return {**base, "statut": "sans_donnees"}
    groupes = list(frequences[3].values())
    somme = sum(g["nb_epreuves"] for g in groupes) or 1

    par_tag = {m["theme_id"]: m for m in maitrise}
    lignes, reponses, couverture = [], 0, 0.0
    for g in groupes:
        n = sum(par_tag[t]["total"] for t in g["tag_ids"] if t in par_tag)
        r = sum(par_tag[t]["reussies"] for t in g["tag_ids"] if t in par_tag)
        poids = g["nb_epreuves"] / somme
        p = (r + 1) / (n + 2)
        lignes.append({"theme": g["nom"], "poids": poids, "p": p, "n": n, "var": p * (1 - p) / (n + 3)})
        reponses += n
        if n:
            couverture += poids
    if reponses < REPONSES_MIN_MATIERE or couverture < COUVERTURE_MIN:
        return {
            **base, "statut": "pas_assez", "reponses": reponses, "reponses_min": REPONSES_MIN_MATIERE,
            "couverture_pct": round(100 * couverture), "couverture_min_pct": round(100 * COUVERTURE_MIN),
        }

    # Les thèmes jamais tentés (la plupart : une matière en compte des centaines) ne valent pas 50 % : ils sont supposés
    # ressembler à ceux que l'élève a tentés. La note est donc la maîtrise moyenne des thèmes tentés, pesés par leur fréquence ;
    # ce qu'on ignore des autres entre dans la fourchette (HETEROGENEITE_THEMES, d'autant plus que la couverture est faible).
    tentes = [l for l in lignes if l["n"]]
    p_matiere = sum(l["poids"] * l["p"] for l in tentes) / couverture
    note_quiz = 20 * p_matiere
    ecart = 20 * sqrt(
        sum((l["poids"] / couverture) ** 2 * l["var"] for l in tentes) + (HETEROGENEITE_THEMES * (1 - couverture)) ** 2,
    )
    blancs = _notes_des_examens_blancs(profil, cursus, subject)
    calibre = len(blancs) >= SIMULATIONS_MIN
    centre = note_quiz
    if calibre:
        note_blancs = sum(blancs) / len(blancs)
        centre = (note_quiz + note_blancs) / 2
        ecart = max(ecart, abs(note_quiz - note_blancs) / 2)
    bas, haut = _fourchette(centre, ecart)

    # Un thème jamais tenté compte avec la maîtrise moyenne de la matière : s'il est lourd, c'est le conseil « commence par là ».
    rentables = sorted(
        (
            {"theme": l["theme"], "points": round(2 * 20 * l["poids"] * (1 - (l["p"] if l["n"] else p_matiere))) / 2, "reponses": l["n"]}
            for l in lignes
        ),
        key=lambda x: (-x["points"], x["theme"]),
    )
    rentables = [x for x in rentables if x["points"] >= GAIN_MIN_POINTS][:THEMES_RENTABLES]
    return {
        **base, "statut": "estimee", "bas": bas, "haut": haut, "centre": centre, "calibre": calibre,
        "examens_blancs": len(blancs), "reponses": reponses, "themes_rentables": rentables,
    }


def note_estimee(profil, cursus):
    """{matieres: [...], moyenne: {bas, haut, matieres, total}|None} ; voir le module pour ce que chaque champ veut dire."""
    sujets = restreindre_matieres(
        profil, Subject.objects.filter(lessons__statut=StatutContenu.VALIDE, lessons__cursus=cursus).distinct(),
    )
    coefficients = _coefficient_par_subject(cursus)
    maitrise = maitrise_par_theme(profil, cursus)
    matieres = []
    for subject in sorted(sujets, key=lambda s: s.label):
        ligne = _matiere(profil, cursus, subject, maitrise)
        ligne["coefficient"] = coefficients.get(subject.id)
        matieres.append(ligne)

    estimees = [m for m in matieres if m["statut"] == "estimee"]
    moyenne = None
    if estimees:
        poids = [float(m["coefficient"] if m["coefficient"] is not None else COEFFICIENT_PAR_DEFAUT) for m in estimees]
        total_poids = sum(poids)
        moyenne = {
            "bas": round(sum(p * m["bas"] for p, m in zip(poids, estimees)) / total_poids),
            "haut": round(sum(p * m["haut"] for p, m in zip(poids, estimees)) / total_poids),
            "matieres": len(estimees),
            "total": len(matieres),
        }
    for m in matieres:
        m.pop("centre", None)  # le milieu de la fourchette ne sort pas : un chiffre précis serait lu comme une promesse
    return {"matieres": matieres, "moyenne": moyenne}
