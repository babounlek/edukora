"""
Cartes de révision (audit produit 2026-11-13, R18, D11) : la règle et les erreurs classiques de chaque cours, rendues en
cartes recto/verso et revues à la répétition espacée. AUCUN contenu à écrire : les cartes se lisent dans `Cours.sections_raw`
au moment de la demande, jamais stockées. Seule la REVUE de l'élève l'est (CarteRevue : palier et échéance).

Une carte = une clé stable dans son cours : « regle » (la règle, avec sa formule) ou « erreur-<n> » (la n-ième erreur classique).
Les paliers sont ceux des thèmes (quiz.services.LEITNER_INTERVALS_JOURS).
"""
from datetime import timedelta

from django.utils import timezone

from catalog.models import StatutContenu
from catalog.rendering import _wrap_bare_formula

from .models import CarteRevue
from .services import LEITNER_INTERVALS_JOURS

CARTES_PAR_REVUE_MAX = 20
TYPE_REGLE, TYPE_ERREUR = "regle", "erreur"


def cartes_du_cours(cours):
    """[{cle, type, recto, verso}] : la règle d'abord, puis les erreurs classiques exploitables (objet à trois champs)."""
    cartes = []
    for section in cours.sections_raw or []:
        genre = section.get("type")
        if genre == "regle":
            titre = (section.get("titre") or "").strip()
            verso = []
            if section.get("formule_principale"):
                verso.append(_wrap_bare_formula(section["formule_principale"]))
            if section.get("contenu_markdown"):
                verso.append(section["contenu_markdown"])
            if titre and verso and not any(c["cle"] == "regle" for c in cartes):
                cartes.append({"cle": "regle", "type": TYPE_REGLE, "recto": titre, "verso": "\n\n".join(verso)})
        elif genre == "erreurs_classiques":
            for i, item in enumerate(section.get("items") or []):
                if not isinstance(item, dict):
                    continue  # une erreur en texte brut n'a pas de verso : pas une carte
                recto = (item.get("erreur_markdown") or "").strip()
                pourquoi = (item.get("pourquoi_faux") or "").strip()
                correction = (item.get("correction_markdown") or "").strip()
                if recto and (pourquoi or correction):
                    cartes.append({
                        "cle": f"erreur-{i}", "type": TYPE_ERREUR, "recto": recto,
                        "verso": "\n\n".join(p for p in (pourquoi, correction and f"**→** {correction}") if p),
                    })
    return cartes


def _etat(revue, aujourdhui):
    if revue is None:
        return "nouvelle"
    return "a_revoir" if revue.due_at <= aujourdhui else "planifiee"


def cartes_avec_etat(profil, cours):
    aujourdhui = timezone.localdate()
    revues = {r.cle: r for r in CarteRevue.objects.filter(profil=profil, cours=cours)}
    return [
        {**c, "etat": _etat(revues.get(c["cle"]), aujourdhui),
         "due_at": revues[c["cle"]].due_at.isoformat() if c["cle"] in revues else None}
        for c in cartes_du_cours(cours)
    ]


def noter(profil, cours, cle, savais):
    """
    Enregistre la revue d'une carte. Savais : la carte monte d'un palier (une nouvelle carte sue entre à J+3, pas à J+1) ;
    ne savais pas : retour au palier 0, revue demain. Une revue faite AVANT l'échéance ne fait pas monter une carte sue : elle
    ne prouve pas qu'elle tient (même règle que les thèmes) et ne change pas son échéance. Renvoie la CarteRevue, ou None si
    la clé n'existe pas dans ce cours.
    """
    if not any(c["cle"] == cle for c in cartes_du_cours(cours)):
        return None
    aujourdhui = timezone.localdate()
    revue = CarteRevue.objects.filter(profil=profil, cours=cours, cle=cle).first()
    if savais and revue is not None and revue.due_at > aujourdhui:
        return revue  # revue anticipée : rien ne bouge
    dernier = len(LEITNER_INTERVALS_JOURS) - 1
    if not savais:
        palier = 0
    elif revue is None:
        palier = 1
    else:
        palier = min(revue.palier + 1, dernier)
    revue, _ = CarteRevue.objects.update_or_create(
        profil=profil, cours=cours, cle=cle,
        defaults={"palier": palier, "due_at": aujourdhui + timedelta(days=LEITNER_INTERVALS_JOURS[palier])},
    )
    return revue


def cartes_dues(profil, limite=CARTES_PAR_REVUE_MAX):
    """Les cartes dont l'échéance est arrivée, la plus en retard d'abord : (total dû, [carte + cours])."""
    dues = (
        CarteRevue.objects.filter(profil=profil, due_at__lte=timezone.localdate(), cours__statut=StatutContenu.VALIDE)
        .select_related("cours").order_by("due_at", "id")
    )
    total = dues.count()
    sortie, cache = [], {}
    for revue in dues[: limite * 2]:  # une carte dont le cours a changé n'existe plus : on en lit un peu plus
        if revue.cours_id not in cache:
            cache[revue.cours_id] = {c["cle"]: c for c in cartes_du_cours(revue.cours)}
        carte = cache[revue.cours_id].get(revue.cle)
        if carte:
            sortie.append({
                **carte, "etat": "a_revoir", "due_at": revue.due_at.isoformat(),
                "cours": {"slug": revue.cours.slug, "titre": revue.cours.titre},
            })
        if len(sortie) >= limite:
            break
    return total, sortie


def paquets_de_l_eleve(profil):
    """
    « Mes cartes » : un paquet par cours dont l'élève a déjà revu au moins une carte. Pour chacun : combien de cartes il compte,
    combien sont à revoir aujourd'hui et la prochaine échéance. Les plus urgents (le plus de cartes dues, puis l'échéance la
    plus proche) d'abord. Une carte dont le clé n'existe plus dans le cours (cours réécrit) ne compte plus.
    """
    aujourdhui = timezone.localdate()
    par_cours = {}
    revues = CarteRevue.objects.filter(profil=profil, cours__statut=StatutContenu.VALIDE).select_related("cours")
    for revue in revues:
        par_cours.setdefault(revue.cours_id, {"cours": revue.cours, "revues": []})["revues"].append(revue)
    paquets = []
    for entree in par_cours.values():
        cours = entree["cours"]
        cles = {c["cle"] for c in cartes_du_cours(cours)}
        revues_valides = [r for r in entree["revues"] if r.cle in cles]
        if not revues_valides:
            continue
        dues = [r for r in revues_valides if r.due_at <= aujourdhui]
        futures = sorted(r.due_at for r in revues_valides if r.due_at > aujourdhui)
        paquets.append({
            "slug": cours.slug, "titre": cours.titre, "total": len(cles), "revues": len(revues_valides), "dues": len(dues),
            "prochaine": futures[0].isoformat() if futures else None,
        })
    paquets.sort(key=lambda p: (-p["dues"], p["prochaine"] or "", p["titre"]))
    return paquets
