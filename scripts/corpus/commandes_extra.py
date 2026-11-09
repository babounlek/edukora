"""Sous-commandes de corpus.py autres qu'`audit` : qualifier, head, collecter, synchroniser, controle, registre."""
import json
import os
import subprocess
import sys

import collecte
import decoupe
import doublons
import qualification
import registre
import similarite
import sources
import synchro
from commun import INGEST, ZONE_EN, ZONE_FR


def _cible(args):
    cible = {}
    for cle in ("niveau", "matiere", "annee", "paper", "code", "examen_cible", "origine"):
        valeur = getattr(args, cle, None)
        if valeur is not None:
            cible["examen" if cle == "examen_cible" else cle] = valeur
    return cible or None


def _zones_connues():
    zones = [ZONE_FR, ZONE_EN]
    zones += [os.path.join(INGEST, d) for d in os.listdir(INGEST) if d.startswith("_telechargements_")]
    return zones


def commande_qualifier(args):
    q = qualification.qualifier(args.pdf, _cible(args))
    if args.doublons:
        index = doublons.construire_index(_zones_connues(), cache=os.path.join(INGEST, "_audit", "corpus", "index_empreintes.json"))
        ignores = {os.path.abspath(p) for p in (args.ignorer_source or [])}
        index = {c: e for c, e in index.items() if os.path.abspath(c) not in ignores}
        q["doublons"] = [list(d) for d in doublons.chercher(args.pdf, index)]
        if q["doublons"] and not q["eliminatoires"]:
            q["eliminatoires"].append(("E6", "doublon (%s) de %s" % (q["doublons"][0][0], q["doublons"][0][1])))
            q["decision"] = "DOUBLON"
    if args.rendre:
        q["pages_rendues"] = qualification.rendre_pages(args.pdf, args.rendre)
    print(json.dumps(q, ensure_ascii=False, indent=2))
    return 0 if not q["eliminatoires"] else 3


def commande_head(args):
    r = collecte.verifier_url(args.url, tete_seule=True)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 0 if r["ok"] else 3


def commande_collecter(args):
    nom = args.nom or collecte.nom_normalise(args.examen, args.serie, args.matiere, args.annee, args.paper, args.source or "web")
    fiche = collecte.collecter(args.url, args.langue, nom, cible=_cible(args), source=args.source)
    print(json.dumps(fiche, ensure_ascii=False, indent=2))
    return 0 if fiche.get("fichier") else 3


def commande_synchroniser(args):
    try:
        copies, refus = synchro.synchroniser(args.pdf, args.nom_lot, lecture_validee=args.lecture_validee, date=args.date)
    except PermissionError as exc:
        print(str(exc), file=sys.stderr)
        return 5
    for c in copies:
        print("copié  :", c)
    for nom, motif in refus:
        print("REFUSÉ :", nom, "-", motif)
    return 0 if not refus else 4


def commande_controle(args):
    """Qualifie tous les PDF d'un dossier (lecture seule) : corrigés et mauvaises identités (E1, E4)."""
    bilan = []
    for nom in sorted(os.listdir(args.dossier)):
        if nom.lower().endswith(".pdf"):
            q = qualification.qualifier(os.path.join(args.dossier, nom))
            bilan.append({"fichier": nom, "decision": q["decision"], "eliminatoires": q["eliminatoires"],
                          "avertissements": q["avertissements"]})
    print(json.dumps(bilan, ensure_ascii=False, indent=2))
    return 0


def commande_decouper(args):
    """Une compilation -> un PDF par épreuve (ou simple inventaire avec --liste)."""
    sortie = None if args.liste else (args.dossier_sortie or os.path.join(INGEST, "_audit", "corpus", "decoupes"))
    epreuves = decoupe.decouper(args.pdf, sortie, garde=args.garde or decoupe.GARDE_PAR_DEFAUT)
    for e in epreuves:
        pub = " (pub retirée p%s)" % ",".join(map(str, e["pages_publicitaires"])) if e["pages_publicitaires"] else ""
        print("%-10s %-28s %s  p%-9s %s%s" % (e["examen"], e["matiere"], e["annee"], e["pages_source"], e["fichier"], pub))
    print("%d épreuve(s)%s" % (len(epreuves), "" if args.liste else " écrites dans " + sortie))
    return 0 if epreuves else 3


def _texte_pdf(chemin):
    """Texte du PDF sans pages publicitaires ni mentions « corrigé disponible sur le site » (bruit de comparaison)."""
    import fitz
    with fitz.open(chemin) as doc:
        pages = [p.get_text() for p in doc if not qualification.page_publicitaire(p.get_text())]
    return qualification.MENTIONS_SITE.sub(" ", " ".join(pages))


def commande_base_doublons(args):
    """Compare chaque PDF au contenu de la base locale (lecture seule, via le conteneur Docker)."""
    ici = os.path.dirname(os.path.abspath(__file__))
    candidats = {os.path.basename(p): _texte_pdf(p) for p in args.pdf}
    charge = os.path.join(os.environ.get("TEMP", "."), "candidats_base.json")
    with open(charge, "w", encoding="utf-8") as fh:
        json.dump({"annee_min": args.depuis_annee, "candidats": candidats}, fh, ensure_ascii=False)
    conteneur = "edukora-backend-1"
    for source, cible in ((charge, "candidats_base.json"), (os.path.join(ici, "similarite.py"), "similarite.py"),
                          (os.path.join(ici, "comparer_base.py"), "comparer_base.py")):
        subprocess.run(["docker", "cp", source, "%s:/tmp/%s" % (conteneur, cible)], check=True, capture_output=True)
    r = subprocess.run(["docker", "exec", conteneur, "python", "manage.py", "shell", "-c",
                        "exec(open('/tmp/comparer_base.py', encoding='utf-8').read())"],
                       check=True, capture_output=True, encoding="utf-8")
    bilan = [json.loads(ligne[2:]) for ligne in r.stdout.splitlines() if ligne.startswith("@@")]
    print(json.dumps(bilan, ensure_ascii=False, indent=2))
    return 3 if any(m["niveau"] == "DOUBLON_BASE" for b in bilan for m in b["meilleurs"]) else 0


def commande_registre(args):
    if args.action == "ajouter":
        fait = registre.enregistrer(args.cible, args.resultat, sources=args.source, motif=args.motif or "",
                                    recontrole_apres=args.recontrole_apres)
        print(json.dumps(fait, ensure_ascii=False))
    elif args.action == "a-refaire":
        print("oui" if registre.a_refaire(args.cible) else "non")
    else:
        for fait in registre.charger():
            print(json.dumps(fait, ensure_ascii=False))
    return 0


def commande_liens(args):
    """Liens pertinents pour une cible : recherche de chaque site, rubriques, Scribd, Google limité au site."""
    cible = _cible(args) or {}
    if args.serie:
        cible["serie"] = args.serie
    if args.langue:
        cible["langue"] = args.langue
    print(sources.rapport_markdown(cible))
    return 0


def commande_sources(args):
    for s in sources.charger():
        print("%-20s %-28s %-12s %s" % (s["id"], s["domaine"], "automatique" if s.get("automatisable") else "à la main", s["verifie_le"]))
    return 0


def ajouter(sous):
    def cible_opts(p):
        p.add_argument("--niveau")
        p.add_argument("--matiere")
        p.add_argument("--annee", type=int)
        p.add_argument("--paper", type=int)
        p.add_argument("--code")
        p.add_argument("--examen-cible", dest="examen_cible", help="bepc|probatoire|bac|cap")
        p.add_argument("--origine", help="OFFICIEL pour déclencher E5")

    q = sous.add_parser("qualifier", help="qualifie un PDF (éliminatoires, page de garde, score) ; n'écrit rien")
    q.add_argument("pdf")
    cible_opts(q)
    q.add_argument("--doublons", action="store_true", help="compare aux zones connues")
    q.add_argument("--ignorer-source", action="append", help="PDF à ne pas compter comme doublon (la compilation dont le candidat est extrait)")
    q.add_argument("--rendre", help="dossier où rendre les pages en PNG (lecture visuelle)")
    q.set_defaults(fonction=commande_qualifier)

    d = sous.add_parser("decouper", help="découpe une compilation en un PDF par épreuve (pages de garde), sans pages publicitaires")
    d.add_argument("pdf")
    d.add_argument("--dossier-sortie", help="défaut : ingest/_audit/corpus/decoupes")
    d.add_argument("--garde", help="expression avec groupes nommés matiere, annee (et examen) pour un autre format de page de garde")
    d.add_argument("--liste", action="store_true", help="inventaire seulement, rien n'est écrit")
    d.set_defaults(fonction=commande_decouper)

    bd = sous.add_parser("base-doublons", help="compare des PDF au contenu déjà en base (lecture seule, Docker requis)")
    bd.add_argument("pdf", nargs="+")
    bd.add_argument("--depuis-annee", type=int, default=2019)
    bd.set_defaults(fonction=commande_base_doublons)

    h = sous.add_parser("head", help="valide une URL de PDF sans la télécharger")
    h.add_argument("url")
    h.set_defaults(fonction=commande_head)

    c = sous.add_parser("collecter", help="télécharge dans trous/fr ou trous/en (mode COLLECTE)")
    c.add_argument("url")
    c.add_argument("--langue", required=True, choices=("fr", "en"))
    c.add_argument("--nom")
    c.add_argument("--examen", default="inconnu")
    c.add_argument("--serie")
    c.add_argument("--source")
    cible_opts(c)
    c.set_defaults(fonction=commande_collecter)

    s = sous.add_parser("synchroniser", help="copie les ACCEPTÉS vers ingest/_telechargements_* (jamais prepare/publish)")
    s.add_argument("pdf", nargs="+")
    s.add_argument("--nom-lot", required=True)
    s.add_argument("--date")
    s.add_argument("--lecture-validee", action="store_true")
    s.set_defaults(fonction=commande_synchroniser)

    k = sous.add_parser("controle", help="qualifie tous les PDF d'un dossier (lecture seule)")
    k.add_argument("dossier")
    k.set_defaults(fonction=commande_controle)

    r = sous.add_parser("registre", help="registre des recherches")
    r.add_argument("action", choices=("lister", "ajouter", "a-refaire"))
    r.add_argument("--cible")
    r.add_argument("--resultat", choices=registre.RESULTATS)
    r.add_argument("--source", action="append")
    r.add_argument("--motif")
    r.add_argument("--recontrole-apres")
    r.set_defaults(fonction=commande_registre)

    li = sous.add_parser("liens", help="liens pertinents (recherche par site) pour une cible ; à utiliser quand le téléchargement direct est impossible")
    cible_opts(li)
    li.add_argument("--examen", dest="examen_cible", help="bepc|probatoire|bac|cap")
    li.add_argument("--serie")
    li.add_argument("--langue", choices=("fr", "en"))
    li.set_defaults(fonction=commande_liens)

    so = sous.add_parser("sources", help="liste des sites du registre et de leur mode d'accès")
    so.set_defaults(fonction=commande_sources)
