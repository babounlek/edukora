"""
Projection canonique de l'ÉTAT EN BASE d'un contenu pédagogique, et diff champ par champ.

L'empreinte d'état détecte une modification faite en production par un autre mécanisme (admin,
fusion de Tags, commande de correctif) depuis la dernière synchronisation. Elle porte sur les
champs de contenu mutables SEULEMENT : sont exclus `statut`, `published_at`, `est_vitrine`
(propriété de l'admin), les dates et toute donnée d'activité des élèves. Les champs compilés
(`Exercise.enonce_markdown` / `corrige_markdown`, `Cours.content_markdown`) sont regroupés sous la clé
`compile` : une retouche manuelle y est détectée, mais un écart limité à `compile` ne rend pas une
adoption « différente » (voir `diff_significatif`).

Les listes d'objets sont projetées en dictionnaires indexés par leur clé naturelle (numéro de
question, id de figure, id de rappel) pour que le diff nomme précisément ce qui a changé.
"""
from . import empreintes as emp


def empreinte_etat(projection):
    return emp.sha256_octets(emp.canoniser(projection, volatiles=()).encode("utf-8", errors="surrogatepass"))


def projeter_exercice(ex):
    questions = {}
    for q in ex.questions.all().prefetch_related("themes"):
        questions[q.numero] = {
            "ordre": q.ordre,
            "enonce_markdown": q.enonce_markdown,
            "corrige_markdown": q.corrige_markdown,
            "difficulte_estimee": q.difficulte_estimee,
            "type_reponse": q.type_reponse,
            "choix": q.choix,
            "reponse_correcte": q.reponse_correcte,
            "points": q.points,
            "savoir_officiel": q.savoir_officiel_id,
            "themes": sorted(t.name for t in q.themes.all()),
        }
    figures = {
        f.external_id: {
            "image": f.image.name, "page_source": f.page_source, "type_figure": f.type_figure,
            "legende": f.legende, "indispensable": f.indispensable, "lisibilite": f.lisibilite, "origine": f.origine,
        }
        for f in ex.figures.all()
    }
    rappels = {
        r.external_id: {"competence": r.competence, "contenu_markdown": r.contenu_markdown}
        for r in ex.rappels_de_methode.all()
    }
    return {
        "points": ex.points,
        "groupes": ex.groupes,
        "groupes_verifies": ex.groupes_verifies,
        "enonce_intro_markdown": ex.enonce_intro_markdown,
        "incertitudes": ex.incertitudes,
        "mots_cles_recherche": sorted(t.name for t in ex.mots_cles_recherche.all()),
        "questions": questions,
        "figures": figures,
        "rappels": rappels,
        # Champs compilés depuis les questions, éditables dans l'admin : une retouche manuelle serait
        # écrasée par la recompilation d'une mise à jour, donc elle doit être vue comme une divergence.
        "compile": {"enonce_markdown": ex.enonce_markdown, "corrige_markdown": ex.corrige_markdown},
    }


def projeter_cours(c):
    return {
        "titre": c.titre,
        "sous_theme": c.sous_theme,
        "duree_estimee_min": c.duree_estimee_min,
        "sections_raw": c.sections_raw,
        "tags": sorted(t.name for t in c.tags.all()),
        "compile": {"content_markdown": c.content_markdown},
    }


def projeter_item(i):
    return {
        "theme": i.theme.name,
        "subject": i.subject_id,
        "enonce_markdown": i.enonce_markdown,
        "corrige_markdown": i.corrige_markdown,
        "difficulte_estimee": i.difficulte_estimee,
        "type_reponse": i.type_reponse,
        "choix": i.choix,
        "reponse_correcte": i.reponse_correcte,
        "cursus": sorted(i.cursus.values_list("pk", flat=True)),
        "figures": {
            f.external_id: {"image": f.image.name, "type_figure": f.type_figure, "legende": f.legende, "origine": f.origine}
            for f in i.figures.all()
        },
    }


def difference(avant, apres, chemin=""):
    """Chemins qui diffèrent entre deux projections (`+x` ajouté, `-x` retiré, `x` modifié)."""
    if isinstance(avant, dict) and isinstance(apres, dict):
        res = []
        for cle in sorted(set(avant) | set(apres), key=str):
            sous = f"{chemin}.{cle}" if chemin else str(cle)
            if cle not in avant:
                res.append(f"+{sous}")
            elif cle not in apres:
                res.append(f"-{sous}")
            else:
                res += difference(avant[cle], apres[cle], sous)
        return res
    return [] if avant == apres else [chemin]


def diff_significatif(diff):
    """Écarts hors champs compilés : seuls ceux-ci changent le CONTENU d'un objet adopté."""
    return [d for d in diff or [] if not d.lstrip("+-").startswith("compile")]
