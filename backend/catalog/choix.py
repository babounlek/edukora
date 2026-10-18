"""
Règles « traiter n questions sur m » d'une épreuve (voir Lesson.regles_choix).

Les sujets du GCE ne sont pas tous obligatoires : la Chimie demande « 4 questions sur 5 » dans sa
Section A et « 2 sur 3 » dans la B, la Physique « soit les parties a, b et c, soit d, e et f » de
chaque question de sa Section II. Le texte de la consigne reste dans `introduction_markdown`, lu par
l'élève ; la forme structurée ci-dessous sert à ce qu'un programme sache de quoi il s'agit (proposer
de choisir, ne noter que ce qui compte, ne pas pénaliser une question laissée de côté).

Quatre formes, volontairement peu nombreuses :
  {"type": "parmi", "portee": "SECTION A", "repondre": 4, "sur": 5}
      n exercices à traiter parmi les m du groupe `portee` (un repère de Exercise.groupes) ;
  {"type": "ou", "portee": "SECTION II", "options": [["a", "b", "c"], ["d", "e", "f"]]}
      dans chaque exercice du groupe, un seul des jeux de sous-questions ;
  {"type": "section_unique", "portee": "PAPER 3", "repondre": 4}
      n exercices à traiter, TOUS dans une seule section de l'épreuve (Religious Studies : « Answer
      FOUR questions chosen from ONE SECTION ONLY »). `portee` n'est qu'un libellé pour l'écran : la
      règle vaut pour toute l'épreuve ; une section est une pile de groupes (Exercise.groupes) ;
  {"type": "consigne", "portee": "SECTION I", "texte": "Two questions of different genres."}
      une consigne qu'aucune forme ci-dessus n'exprime : lue par l'élève, sans effet sur la note.
"""


def valider_regles_choix(regles):
    """Renvoie la liste normalisée (textes nettoyés), ou lève ValueError avec un message lisible.
    Aucune règle (None, liste vide) est valide : c'est le cas d'une épreuve sans choix."""
    if regles in (None, ""):
        return []
    if not isinstance(regles, list):
        raise ValueError("regles_choix doit être une liste.")

    normalisees = []
    for position, regle in enumerate(regles, start=1):
        cadre = f"regles_choix[{position}]"
        if not isinstance(regle, dict):
            raise ValueError(f"{cadre} doit être un objet.")
        portee = str(regle.get("portee") or "").strip()
        if not portee:
            raise ValueError(f"{cadre} : « portee » manquante (le groupe concerné, ex. « SECTION A »).")

        genre = regle.get("type")
        if genre == "parmi":
            repondre, sur = regle.get("repondre"), regle.get("sur")
            if not all(isinstance(n, int) and not isinstance(n, bool) for n in (repondre, sur)):
                raise ValueError(f"{cadre} : « repondre » et « sur » doivent être des entiers.")
            if repondre < 1 or sur < repondre:
                raise ValueError(f"{cadre} : il faut 1 <= repondre <= sur (reçu {repondre} sur {sur}).")
            normalisees.append({"type": "parmi", "portee": portee, "repondre": repondre, "sur": sur})
        elif genre == "ou":
            options = regle.get("options")
            if not isinstance(options, list) or len(options) < 2:
                raise ValueError(f"{cadre} : « options » doit contenir au moins deux jeux de sous-questions.")
            jeux = []
            for jeu in options:
                if not isinstance(jeu, list) or not jeu or not all(isinstance(s, str) and s.strip() for s in jeu):
                    raise ValueError(f"{cadre} : chaque option est une liste non vide de repères (ex. [\"a\", \"b\"]).")
                jeux.append([s.strip() for s in jeu])
            repères = [s for jeu in jeux for s in jeu]
            if len(set(repères)) != len(repères):
                raise ValueError(f"{cadre} : un même repère ne peut pas figurer dans deux options.")
            normalisees.append({"type": "ou", "portee": portee, "options": jeux})
        elif genre == "section_unique":
            repondre = regle.get("repondre")
            if not isinstance(repondre, int) or isinstance(repondre, bool) or repondre < 1:
                raise ValueError(f"{cadre} : « repondre » doit être un entier >= 1.")
            normalisees.append({"type": "section_unique", "portee": portee, "repondre": repondre})
        elif genre == "consigne":
            texte = " ".join(str(regle.get("texte") or "").split())
            if not texte:
                raise ValueError(f"{cadre} : « texte » manquant (la consigne à afficher).")
            normalisees.append({"type": "consigne", "portee": portee, "texte": texte})
        else:
            raise ValueError(
                f"{cadre} : type inconnu {genre!r} (attendu « parmi », « ou », « section_unique » ou « consigne »)."
            )
    return normalisees
