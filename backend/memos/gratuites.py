"""
Les sessions d'une fiche, examen par examen, et les fiches gratuites de chaque examen.

Une même fiche (« Syndicat ») peut préparer le BEPC et le Probatoire. Les années affichées doivent être celles de l'examen
que l'on prépare : dire à un élève de Première « tombé en 2018 » parce que c'est tombé au BEPC serait faux. Chaque session
garde donc la liste des examens (ids de Cursus) où elle a eu lieu.
"""

from .models import Memo

GRATUITES_PAR_EXAMEN = 5


def fusionner_sessions(anciennes, nouvelles):
    """Réunit deux listes de sessions : une entrée par (année, origine), avec tous les examens concernés."""
    par_cle = {}
    for s in [*(anciennes or []), *(nouvelles or [])]:
        cle = (s["annee"], s["origine"])
        par_cle.setdefault(cle, set()).update(s.get("cursus") or [])
    return [
        {"annee": a, "origine": o, "cursus": sorted(cursus)}
        for (a, o), cursus in sorted(par_cle.items())
    ]


def sessions_de(memo, cursus_id):
    """Les sessions de cette fiche à CET examen, sans la liste des examens (une session sans liste vaut pour tous)."""
    return [
        {"annee": s["annee"], "origine": s["origine"]}
        for s in (memo.sessions or [])
        if cursus_id is None or not s.get("cursus") or cursus_id in s["cursus"]
    ]


def cle_de_tri(memo, cursus_id):
    """D'abord les notions tombées le plus souvent à l'examen officiel, puis le plus récemment, puis l'ordre choisi."""
    officielles = [s["annee"] for s in sessions_de(memo, cursus_id) if s["origine"] == "OFFICIEL"]
    return (-len(officielles), -max(officielles, default=0), memo.ordre, memo.terme)


def assurer_gratuites(subject):
    """
    Chaque examen d'une matière a au moins GRATUITES_PAR_EXAMEN fiches lisibles sans abonnement, prises parmi les plus
    souvent tombées à cet examen. On n'en retire jamais (un choix fait dans l'administration reste).
    """
    memos = list(Memo.objects.filter(subject=subject).prefetch_related("cursus"))
    examens = sorted({c.pk for m in memos for c in m.cursus.all()})
    for cursus_id in examens:
        siens = sorted((m for m in memos if cursus_id in {c.pk for c in m.cursus.all()}), key=lambda m: cle_de_tri(m, cursus_id))
        manque = GRATUITES_PAR_EXAMEN - sum(1 for m in siens if m.gratuit)
        for memo in siens:
            if manque <= 0:
                break
            if not memo.gratuit and not memo.modifie_a_la_main:
                memo.gratuit = True
                Memo.objects.filter(pk=memo.pk).update(gratuit=True)
                manque -= 1
