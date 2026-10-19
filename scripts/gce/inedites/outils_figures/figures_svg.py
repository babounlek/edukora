#!/usr/bin/env python3
"""
Figures SVG pour les épreuves inédites edukora - bibliothèque sans dépendance (Python 3.8+).

Une figure est une CHAÎNE SVG sur UNE SEULE LIGNE, à coller telle quelle dans un champ Markdown
(`enonce_intro_markdown`, `enonce_markdown`, `corrige_markdown`), entre deux lignes vides. Les règles
que cette bibliothèque applique pour vous (voir SKILL.md, « Figures et tracés ») :

- une seule ligne (le rendu PDF insère un <br> à chaque retour à la ligne, qui casse le SVG) ;
- attributs entre apostrophes, jamais de guillemets droits ni de « » dans un texte, jamais de dollar :
  la plateforme met en italique tout texte entre guillemets et lit « $...$ » comme une formule ;
- couleurs en variables CSS du thème avec repli clair (le site bascule en mode sombre, le PDF reste
  clair) : jamais de couleur en dur ;
- viewBox + largeur 100 % bornée : la figure se réduit sur téléphone sans défiler ;
- <title> et <desc> : texte alternatif lu par un lecteur d'écran ;
- aucun script, aucun <image>, aucune référence externe.

Usage minimal :

    from figures_svg import Fig, Repere
    f = Fig(420, 260, "Courbe de f", "Parabole de sommet (0 ; -2) ...")
    r = Repere(f, 40, 20, 360, 200, -3, 3, -3, 4)
    r.courbe(lambda x: x * x - 2)
    print(f.render())
"""
import html
import math
import zlib

# --------------------------------------------------------------------------- couleurs (thème du site)
FG = "var(--foreground,#161d1a)"
MU = "var(--muted-foreground,#5b6560)"
BD = "var(--border,#c9cfcb)"
BG = "var(--background,#ffffff)"
CARD = "var(--card,#ffffff)"
PR = "var(--primary,#0f6b4f)"
INFO = "var(--info,#2a6fba)"
GD = "var(--gold,#d9a21f)"
DG = "var(--destructive,#c4352e)"
OK = "var(--success,#1a7a36)"
ACC = "var(--accent,#e4f3ec)"

INTERDITS_TEXTE = ('"', "«", "»", "$", "\n")


def _n(v):
    """Nombre court : une décimale au plus, sans zéro final."""
    s = f"{float(v):.1f}"
    return s[:-2] if s.endswith(".0") else s


DECIMAL = ","  # séparateur décimal des graduations : "," pour le contenu français, "." pour le GCE (assigner fs.DECIMAL = ".")


def fmt(v, decimales=None):
    """Nombre pour une graduation : virgule décimale (français) ou point (GCE, voir DECIMAL), vrai signe moins."""
    if decimales is None:
        decimales = 0 if abs(v - round(v)) < 1e-9 else 1
    s = f"{v:.{decimales}f}".replace(".", DECIMAL)
    return s.replace("-", "−")


def esc(texte):
    """Texte sûr pour un SVG posé dans du Markdown. Le texte entre deux balises est LU comme du Markdown : deux
    astérisques (« 0..* » deux fois dans un diagramme de classes) ouvrent puis ferment un passage en italique
    qui avale les balises entre eux et casse la figure. L'astérisque devient donc l'opérateur astérisque U+2217,
    visuellement identique."""
    t = str(texte).replace("*", "∗")
    for interdit in INTERDITS_TEXTE:
        if interdit in t:
            raise ValueError(f"Caractère interdit dans un texte de figure ({interdit!r}) : {t!r}")
    return html.escape(t, quote=False)


def largeur_texte(texte, taille=14, gras=False):
    """Largeur approchée d'un texte sans-serif (0,56 em en moyenne, 0,6 en gras)."""
    return len(str(texte)) * taille * (0.6 if gras else 0.56)


def _attrs(**kw):
    out = []
    for k, v in kw.items():
        if v is None or v is False:
            continue
        out.append(f"{k.rstrip('_').replace('_', '-')}='{v}'")
    return " ".join(out)


# --------------------------------------------------------------------------- figure
class Fig:
    """Une figure. Les formes sont rangées par couches : fond, liens, formes, textes."""

    def __init__(self, largeur, hauteur, titre, description, max_largeur=None, variante=""):
        """variante : mot quelconque qui distingue deux figures identiques d'une même page (la même figure dans
        l'énoncé et dans le corrigé, par exemple) : leurs id (aria, clipPath) doivent différer."""
        self.variante = variante
        self.w, self.h = largeur, hauteur
        self.titre, self.description = esc(titre), esc(description)
        self.max_largeur = max_largeur or largeur
        # identifiant provisoire : remplacé au rendu par une empreinte du contenu, STABLE d'une exécution à l'autre
        # (un compteur repartirait de 1 à chaque lot et deux figures d'une même page auraient les mêmes id)
        self.uid = "UID"
        self.couches = {0: [], 1: [], 2: [], 3: []}
        self.noeuds = {}
        self.defs = []
        self._nclip = 0

    # -- primitives
    def _add(self, s, couche=2):
        self.couches[couche].append(s)

    def rect(self, x, y, w, h, rx=6, fill=CARD, stroke=FG, sw=1.5, dash=None, couche=2):
        self._add(f"<rect {_attrs(x=_n(x), y=_n(y), width=_n(w), height=_n(h), rx=_n(rx), fill=fill, stroke=stroke, stroke_width=sw, stroke_dasharray=dash)}/>", couche)

    def ellipse(self, cx, cy, rx, ry, fill=CARD, stroke=FG, sw=1.5, dash=None, couche=2):
        self._add(f"<ellipse {_attrs(cx=_n(cx), cy=_n(cy), rx=_n(rx), ry=_n(ry), fill=fill, stroke=stroke, stroke_width=sw, stroke_dasharray=dash)}/>", couche)

    def cercle(self, cx, cy, r, fill=CARD, stroke=FG, sw=1.5, couche=2):
        self._add(f"<circle {_attrs(cx=_n(cx), cy=_n(cy), r=_n(r), fill=fill, stroke=stroke, stroke_width=sw)}/>", couche)

    def polygone(self, points, fill=CARD, stroke=FG, sw=1.5, couche=2):
        pts = " ".join(f"{_n(x)},{_n(y)}" for x, y in points)
        self._add(f"<polygon {_attrs(points=pts, fill=fill, stroke=stroke, stroke_width=sw, stroke_linejoin='round')}/>", couche)

    def ligne(self, x1, y1, x2, y2, stroke=MU, sw=1.5, dash=None, couche=1):
        self._add(f"<line {_attrs(x1=_n(x1), y1=_n(y1), x2=_n(x2), y2=_n(y2), stroke=stroke, stroke_width=sw, stroke_dasharray=dash, stroke_linecap='round')}/>", couche)

    def polyligne(self, points, stroke=FG, sw=1.5, dash=None, couche=1):
        pts = " ".join(f"{_n(x)},{_n(y)}" for x, y in points)
        self._add(f"<polyline {_attrs(points=pts, fill='none', stroke=stroke, stroke_width=sw, stroke_dasharray=dash, stroke_linejoin='round', stroke_linecap='round')}/>", couche)

    def chemin(self, d, fill="none", stroke=FG, sw=1.5, dash=None, couche=1, clip=None):
        self._add(f"<path {_attrs(d=d, fill=fill, stroke=stroke, stroke_width=sw, stroke_dasharray=dash, stroke_linejoin='round', clip_path=clip)}/>", couche)

    def texte(self, x, y, s, taille=14, ancre="middle", fill=FG, gras=False, italique=False, souligne=False, halo=False, couche=3):
        """`y` est la ligne de base. `halo` : contour de la couleur du fond, pour lire un texte posé sur un trait."""
        a = _attrs(
            x=_n(x), y=_n(y), font_size=_n(taille), text_anchor=ancre, fill=fill,
            font_weight="bold" if gras else None, font_style="italic" if italique else None,
            text_decoration="underline" if souligne else None,
            stroke=BG if halo else None, stroke_width=4 if halo else None, paint_order="stroke" if halo else None,
            stroke_linejoin="round" if halo else None,
        )
        self._add(f"<text {a}>{esc(s)}</text>", couche)

    def lignes_texte(self, x, y, textes, taille=14, interligne=1.35, **kw):
        for i, t in enumerate(textes):
            self.texte(x, y + i * taille * interligne, t, taille=taille, **kw)

    def fleche(self, x1, y1, x2, y2, stroke=FG, sw=1.5, dash=None, tete="plein", taille_tete=9, couche=1):
        """Trait + pointe au bout (x2, y2). tete : plein, ouvert, triangle_vide, losange_vide, losange_plein, aucune."""
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1
        ux, uy = dx / d, dy / d
        nx, ny = -uy, ux
        t = taille_tete
        if tete == "aucune":
            self.ligne(x1, y1, x2, y2, stroke, sw, dash, couche)
            return
        if tete in ("losange_vide", "losange_plein"):
            # le losange se dessine du côté de (x2, y2) : le trait s'arrête à sa pointe arrière
            bx, by = x2 - ux * 2 * t * 0.9, y2 - uy * 2 * t * 0.9
            self.ligne(x1, y1, bx, by, stroke, sw, dash, couche)
            mx, my = x2 - ux * t * 0.9, y2 - uy * t * 0.9
            pts = [(x2, y2), (mx + nx * t * 0.55, my + ny * t * 0.55), (bx, by), (mx - nx * t * 0.55, my - ny * t * 0.55)]
            self.polygone(pts, fill=stroke if tete == "losange_plein" else BG, stroke=stroke, sw=sw, couche=couche)
            return
        if tete == "triangle_vide":
            bx, by = x2 - ux * t * 1.2, y2 - uy * t * 1.2
            self.ligne(x1, y1, bx, by, stroke, sw, dash, couche)
            self.polygone([(x2, y2), (bx + nx * t * 0.6, by + ny * t * 0.6), (bx - nx * t * 0.6, by - ny * t * 0.6)], fill=BG, stroke=stroke, sw=sw, couche=couche)
            return
        self.ligne(x1, y1, x2, y2, stroke, sw, dash, couche)
        bx, by = x2 - ux * t, y2 - uy * t
        if tete == "ouvert":
            self.polyligne([(bx + nx * t * 0.5, by + ny * t * 0.5), (x2, y2), (bx - nx * t * 0.5, by - ny * t * 0.5)], stroke, sw, None, couche)
        else:
            self.polygone([(x2, y2), (bx + nx * t * 0.45, by + ny * t * 0.45), (bx - nx * t * 0.45, by - ny * t * 0.45)], fill=stroke, stroke=stroke, sw=1, couche=couche)

    def chemin_fleche(self, points, stroke=FG, sw=1.5, dash=None, tete="plein"):
        """Ligne brisée dont le dernier segment porte la pointe (retour de boucle, lien coudé)."""
        if len(points) < 2:
            raise ValueError("au moins deux points")
        if len(points) > 2:
            self.polyligne(points[:-1], stroke, sw, dash)
        (x1, y1), (x2, y2) = points[-2], points[-1]
        self.fleche(x1, y1, x2, y2, stroke, sw, dash, tete)

    def legende(self, s, y=None):
        """Légende sous la figure, en gris (« Figure 1 : ... »)."""
        self.texte(self.w / 2, y if y is not None else self.h - 6, s, taille=13, fill=MU)

    # -- noeuds reliables (réseaux, MCD, classes, algorigrammes)
    def noeud(self, ident, cx, cy, w, h, forme="rect", fill=CARD, stroke=FG, sw=1.5, dash=None):
        self.noeuds[ident] = (cx, cy, w, h, forme)
        if forme == "rect":
            self.rect(cx - w / 2, cy - h / 2, w, h, 6, fill, stroke, sw, dash)
        elif forme == "ellipse":
            self.ellipse(cx, cy, w / 2, h / 2, fill, stroke, sw, dash)
        elif forme == "losange":
            self.polygone([(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)], fill, stroke, sw)
        elif forme == "arrondi":  # début / fin d'algorigramme
            self.rect(cx - w / 2, cy - h / 2, w, h, h / 2, fill, stroke, sw, dash)
        elif forme == "parallelogramme":  # entrée / sortie d'algorigramme
            d = h * 0.35
            self.polygone([(cx - w / 2 + d, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2 - d, cy + h / 2), (cx - w / 2, cy + h / 2)], fill, stroke, sw)
        else:
            raise ValueError(f"forme inconnue : {forme}")

    def _bord(self, ident, vx, vy):
        cx, cy, w, h, forme = self.noeuds[ident]
        n = math.hypot(vx, vy) or 1
        vx, vy = vx / n, vy / n
        if forme in ("rect", "arrondi", "parallelogramme"):
            t = min((w / 2) / abs(vx) if vx else 1e9, (h / 2) / abs(vy) if vy else 1e9)
        elif forme == "ellipse":
            t = 1 / math.sqrt((vx / (w / 2)) ** 2 + (vy / (h / 2)) ** 2)
        else:  # losange
            t = 1 / (abs(vx) / (w / 2) + abs(vy) / (h / 2))
        return cx + vx * t, cy + vy * t

    def lien(self, a, b, etiquette=None, stroke=MU, sw=1.5, dash=None, tete="aucune", etiq_a=None, etiq_b=None, decalage=0, point_a=None, point_b=None):
        """Relie deux noeuds BORD À BORD (jamais à travers une forme).
        etiquette : au milieu ; etiq_a / etiq_b : près de chaque extrémité (cardinalités, multiplicités) ;
        decalage : écarte la ligne en parallèle (pixels) pour deux liens entre les mêmes noeuds."""
        ax, ay, bx, by = self.noeuds[a][0], self.noeuds[a][1], self.noeuds[b][0], self.noeuds[b][1]
        if point_a:
            ax, ay = point_a
        if point_b:
            bx, by = point_b
        vx, vy = bx - ax, by - ay
        n = math.hypot(vx, vy) or 1
        ox, oy = -vy / n * decalage, vx / n * decalage
        p1 = self._bord(a, vx, vy)
        p2 = self._bord(b, -vx, -vy)
        x1, y1, x2, y2 = p1[0] + ox, p1[1] + oy, p2[0] + ox, p2[1] + oy
        self.fleche(x1, y1, x2, y2, stroke, sw, dash, tete)
        ux, uy = (x2 - x1) / (math.hypot(x2 - x1, y2 - y1) or 1), (y2 - y1) / (math.hypot(x2 - x1, y2 - y1) or 1)
        nx, ny = -uy, ux
        if etiquette:
            self.texte((x1 + x2) / 2 + nx * 11, (y1 + y2) / 2 + ny * 11 + 4, etiquette, taille=13, fill=MU, halo=True)
        if etiq_a:
            self.texte(x1 + ux * 16 + nx * 12, y1 + uy * 16 + ny * 12 + 4, etiq_a, taille=13, fill=FG, halo=True)
        if etiq_b:
            self.texte(x2 - ux * 16 + nx * 12, y2 - uy * 16 + ny * 12 + 4, etiq_b, taille=13, fill=FG, halo=True)
        return (x1, y1), (x2, y2)

    def boite(self, ident, cx, cy, lignes, taille=14, forme="rect", gras_premiere=False, w=None, h=None, fill=CARD, stroke=FG, dash=None):
        """Noeud dont la taille s'ajuste au texte. `lignes` : une chaîne ou une liste de chaînes."""
        if isinstance(lignes, str):
            lignes = [lignes]
        largeur = w or max(largeur_texte(l, taille, gras_premiere and i == 0) for i, l in enumerate(lignes)) + (34 if forme in ("ellipse", "losange") else 22)
        hauteur = h or len(lignes) * taille * 1.35 + (16 if forme == "rect" else 22)
        self.noeud(ident, cx, cy, largeur, hauteur, forme, fill, stroke, dash=dash)
        y0 = cy - (len(lignes) - 1) * taille * 1.35 / 2 + taille * 0.35
        for i, l in enumerate(lignes):
            self.texte(cx, y0 + i * taille * 1.35, l, taille=taille, gras=gras_premiere and i == 0)
        return ident

    # -- rendu
    def render(self):
        corps = "".join(self.couches[0] + self.couches[1] + self.couches[2] + self.couches[3])
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        entete = _attrs(
            viewBox=f"0 0 {_n(self.w)} {_n(self.h)}", role="img", aria_labelledby=f"fig{self.uid}t fig{self.uid}d",
            style=f"width:100%;max-width:{_n(self.max_largeur)}px;height:auto;display:block;margin:0.75rem auto",
            xmlns="http://www.w3.org/2000/svg", font_family="system-ui,-apple-system,Segoe UI,Roboto,sans-serif",
        )
        uid = self.uid
        s = f"<svg {entete}><title id='fig{uid}t'>{self.titre}</title><desc id='fig{uid}d'>{self.description}</desc>{defs}{corps}</svg>"
        empreinte = format(zlib.crc32((self.variante + s.replace("UID", "")).encode("utf-8")), "x")
        s = s.replace("UID", empreinte)
        if "\n" in s or '"' in s:
            raise ValueError("SVG non conforme : retour à la ligne ou guillemet droit")
        return s


# --------------------------------------------------------------------------- repère cartésien
class Repere:
    """Repère avec graduations, grille légère et tracés. (x0, y0, w, h) : zone de tracé dans la figure."""

    def __init__(self, fig, x0, y0, w, h, xmin, xmax, ymin, ymax, xpas=1, ypas=1, xetiq="x", yetiq="y", grille=True, axes_origine=True, xdec=None, ydec=None):
        self.f, self.x0, self.y0, self.w, self.h = fig, x0, y0, w, h
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        fig._nclip += 1
        self.clip_id = f"clip{fig.uid}_{fig._nclip}"  # UID est remplacé au rendu
        fig.defs.append(f"<clipPath id='{self.clip_id}'><rect x='{_n(x0)}' y='{_n(y0)}' width='{_n(w)}' height='{_n(h)}'/></clipPath>")
        self._graduer(xpas, ypas, xetiq, yetiq, grille, axes_origine, xdec, ydec)

    def px(self, x):
        return self.x0 + (x - self.xmin) / (self.xmax - self.xmin) * self.w

    def py(self, y):
        return self.y0 + self.h - (y - self.ymin) / (self.ymax - self.ymin) * self.h

    def _graduer(self, xpas, ypas, xetiq, yetiq, grille, axes_origine, xdec, ydec):
        f = self.f
        ax = self.py(0) if (axes_origine and self.ymin <= 0 <= self.ymax) else self.y0 + self.h
        ay = self.px(0) if (axes_origine and self.xmin <= 0 <= self.xmax) else self.x0
        k = math.ceil(self.xmin / xpas - 1e-9)
        while k * xpas <= self.xmax + 1e-9:
            v = k * xpas
            x = self.px(v)
            if grille:
                f.ligne(x, self.y0, x, self.y0 + self.h, BD, 1, couche=0)
            f.ligne(x, ax - 3, x, ax + 3, MU, 1.2)
            if abs(v) > 1e-9 or not axes_origine:
                f.texte(x, ax + 17, fmt(v, xdec), taille=12, fill=MU, halo=True)
            k += 1
        k = math.ceil(self.ymin / ypas - 1e-9)
        while k * ypas <= self.ymax + 1e-9:
            v = k * ypas
            y = self.py(v)
            if grille:
                f.ligne(self.x0, y, self.x0 + self.w, y, BD, 1, couche=0)
            f.ligne(ay - 3, y, ay + 3, y, MU, 1.2)
            if abs(v) > 1e-9 or not axes_origine:
                f.texte(ay - 7, y + 4, fmt(v, ydec), taille=12, ancre="end", fill=MU, halo=True)
            k += 1
        if axes_origine and self.xmin <= 0 <= self.xmax and self.ymin <= 0 <= self.ymax:
            f.texte(ay - 7, ax + 16, "0", taille=12, ancre="end", fill=MU, halo=True)
        f.fleche(self.x0, ax, self.x0 + self.w + 6, ax, FG, 1.6, couche=1)
        f.fleche(ay, self.y0 + self.h, ay, self.y0 - 6, FG, 1.6, couche=1)
        f.texte(self.x0 + self.w + 4, ax - 9, xetiq, taille=13, ancre="end", italique=True, halo=True)
        f.texte(ay + 8, self.y0 - 10, yetiq, taille=13, ancre="start", italique=True, halo=True)

    def courbe(self, fonction, a=None, b=None, n=200, couleur=PR, epaisseur=2.5, nom=None, nom_pos=None, dash=None, saut=None):
        """Trace y = fonction(x) sur [a ; b]. Coupe le tracé aux discontinuités (valeurs non finies, saut vertical
        supérieur à `saut`, par défaut la moitié de la hauteur du repère) : jamais de segment à travers une asymptote."""
        a = self.xmin if a is None else a
        b = self.xmax if b is None else b
        saut = saut if saut is not None else (self.ymax - self.ymin) * 0.5
        morceaux, cur, prev = [], [], None
        for i in range(n + 1):
            x = a + (b - a) * i / n
            try:
                y = fonction(x)
            except (ZeroDivisionError, ValueError, OverflowError):
                y = None
            ok = y is not None and isinstance(y, (int, float)) and math.isfinite(y)
            if not ok or (prev is not None and abs(y - prev) > saut):
                if len(cur) > 1:
                    morceaux.append(cur)
                cur = []
            if ok:
                cur.append((self.px(x), self.py(max(min(y, self.ymax + 10 * (self.ymax - self.ymin)), self.ymin - 10 * (self.ymax - self.ymin)))))
                prev = y
            else:
                prev = None
        if len(cur) > 1:
            morceaux.append(cur)
        d = " ".join("M" + " L".join(f"{_n(x)},{_n(y)}" for x, y in m) for m in morceaux)
        self.f.chemin(d, "none", couleur, epaisseur, dash, couche=1, clip=f"url(#{self.clip_id})")
        if nom:
            x, y = nom_pos if nom_pos else (self.x0 + self.w - 8, self.y0 + 14)
            self.f.texte(x, y, nom, taille=14, ancre="end", fill=couleur, gras=True, halo=True)

    def point(self, x, y, etiquette=None, dx=8, dy=-8, couleur=DG, ancre="start"):
        self.f.cercle(self.px(x), self.py(y), 3.5, couleur, couleur, 1)
        if etiquette:
            self.f.texte(self.px(x) + dx, self.py(y) + dy, etiquette, taille=13, ancre=ancre, fill=couleur, halo=True)

    def asymptote_v(self, x, etiquette=None):
        self.f.ligne(self.px(x), self.y0, self.px(x), self.y0 + self.h, DG, 1.3, "5 4")
        if etiquette:
            self.f.texte(self.px(x) + 5, self.y0 + 12, etiquette, taille=12, ancre="start", fill=DG, halo=True)

    def asymptote_h(self, y, etiquette=None):
        self.f.ligne(self.x0, self.py(y), self.x0 + self.w, self.py(y), DG, 1.3, "5 4")
        if etiquette:
            self.f.texte(self.x0 + self.w - 4, self.py(y) - 5, etiquette, taille=12, ancre="end", fill=DG, halo=True)

    def droite(self, a, b, couleur=INFO, nom=None, nom_pos=None):
        self.courbe(lambda x: a * x + b, n=2, couleur=couleur, epaisseur=2, nom=nom, nom_pos=nom_pos, saut=float("inf"))

    def segment(self, x1, y1, x2, y2, couleur=FG, dash=None, epaisseur=1.5, tete="aucune"):
        self.f.fleche(self.px(x1), self.py(y1), self.px(x2), self.py(y2), couleur, epaisseur, dash, tete)

    def nuage(self, points, couleur=PR, rayon=3.5):
        for x, y in points:
            self.f.cercle(self.px(x), self.py(y), rayon, couleur, couleur, 1)

    def histogramme(self, bornes, effectifs, couleur=PR):
        for i, e in enumerate(effectifs):
            x1, x2, y = self.px(bornes[i]), self.px(bornes[i + 1]), self.py(e)
            self.f.rect(x1, y, x2 - x1, self.py(0) - y, 0, fill=couleur, stroke=BG, sw=1)

    def barres(self, categories, valeurs, couleur=PR, largeur_relative=0.6):
        k = len(categories)
        for i, (c, v) in enumerate(zip(categories, valeurs)):
            cx = self.x0 + (i + 0.5) * self.w / k
            bw = self.w / k * largeur_relative
            self.f.rect(cx - bw / 2, self.py(v), bw, self.py(0) - self.py(v), 0, fill=couleur, stroke=BG, sw=1)
            self.f.texte(cx, self.py(0) + 32, c, taille=12, fill=MU)


# --------------------------------------------------------------------------- diagrammes prêts à l'emploi
def diagramme_classes(titre, description, classes, associations, largeur=520, hauteur=300, objets=False):
    """classes : liste de (id, nom, [attributs], [operations], cx, cy).
    associations : liste de dict(a, b, mult_a, mult_b, nom, type) ; type = simple | agregation | composition | heritage | dependance.
    Pour une association, a est la classe qui PORTE le losange (le tout) ou la classe fille (héritage).
    objets=True : noms soulignés (diagramme d'objets : nom = ':Classe').
    Un attribut écrit '__nom' est SOULIGNÉ (identifiant d'une entité de MCD, clé primaire)."""
    f = Fig(largeur, hauteur, titre, description)
    for ident, nom, attrs, ops, cx, cy in classes:
        taille = 13
        souligne = [a.startswith("__") for a in attrs]
        attrs = [a[2:] if a.startswith("__") else a for a in attrs]
        lignes_all = [nom] + list(attrs) + list(ops)
        w = max(largeur_texte(l, taille, i == 0) for i, l in enumerate(lignes_all)) + 24
        w = max(w, 90)
        ha = len(attrs) * 17 + (10 if attrs or ops else 4)
        ho = len(ops) * 17 + (10 if ops else 0)
        h = 28 + ha + ho
        f.noeud(ident, cx, cy, w, h, "rect")
        top = cy - h / 2
        f.texte(cx, top + 19, nom, taille=14, gras=not objets, souligne=objets)
        f.ligne(cx - w / 2, top + 28, cx + w / 2, top + 28, FG, 1.2, couche=3)
        for i, a in enumerate(attrs):
            f.texte(cx - w / 2 + 10, top + 28 + 17 + i * 17 - 2, a, taille=taille, ancre="start", souligne=souligne[i])
        if ops:
            y_sep = top + 28 + ha
            f.ligne(cx - w / 2, y_sep, cx + w / 2, y_sep, FG, 1.2, couche=3)
            for i, o in enumerate(ops):
                f.texte(cx - w / 2 + 10, y_sep + 17 + i * 17 - 2, o, taille=taille, ancre="start")
    for a in associations:
        t = a.get("type", "simple")
        tete = {"simple": "aucune", "agregation": "losange_vide", "composition": "losange_plein", "heritage": "triangle_vide", "dependance": "ouvert"}[t]
        dash = "5 4" if t == "dependance" else None
        # le losange / triangle se dessine côté du « tout » / de la classe mère : on trace de b vers a
        if tete in ("losange_vide", "losange_plein", "triangle_vide"):
            f.lien(b=a["a"], a=a["b"], tete=tete, etiq_b=a.get("mult_a"), etiq_a=a.get("mult_b"), etiquette=a.get("nom"), dash=dash, stroke=FG)
        else:
            f.lien(a["a"], a["b"], tete=tete, etiq_a=a.get("mult_a"), etiq_b=a.get("mult_b"), etiquette=a.get("nom"), dash=dash, stroke=FG)
    return f


def sequence(titre, description, participants, messages, largeur=None, pas=44):
    """participants : liste de noms. messages : liste de (de, vers, texte[, 'retour']) dans l'ordre chronologique.
    Les indices sont ceux de `participants`. Un message de retour est tracé en pointillés."""
    k = len(participants)
    col = 170
    w = largeur or max(360, k * col)
    haut = 56 + len(messages) * pas + 30
    f = Fig(w, haut, titre, description)
    xs = [w / (2 * k) + i * w / k for i in range(k)]
    for i, nom in enumerate(participants):
        bw = max(110, largeur_texte(nom, 14) + 22)
        f.rect(xs[i] - bw / 2, 8, bw, 32, 6)
        f.texte(xs[i], 29, nom, taille=14)
        f.ligne(xs[i], 40, xs[i], haut - 10, MU, 1.2, "5 4", couche=0)
    for m, msg in enumerate(messages):
        de, vers, texte = msg[0], msg[1], msg[2]
        retour = len(msg) > 3 and msg[3] == "retour"
        y = 56 + m * pas + 22
        sens = 1 if xs[vers] > xs[de] else -1
        f.fleche(xs[de], y, xs[vers] - sens * 1, y, FG, 1.5, "6 4" if retour else None, "ouvert" if retour else "plein", couche=1)
        f.texte((xs[de] + xs[vers]) / 2, y - 8, f"{m + 1} : {texte}", taille=13, halo=True)
    return f


def cas_utilisation(titre, description, systeme, acteurs, cas, liens, relations=(), largeur=560, hauteur=360):
    """systeme : (titre, x, y, w, h). acteurs : liste de (id, nom, x, y). cas : liste de (id, libelle, cx, cy).
    liens : liste de (acteur_id, cas_id). relations : liste de (cas_source, cas_cible, 'include'|'extend')."""
    f = Fig(largeur, hauteur, titre, description)
    stit, sx, sy, sw, sh = systeme
    f.rect(sx, sy, sw, sh, 8, fill="none", stroke=FG, sw=1.5, couche=0)
    f.texte(sx + 12, sy + 20, stit, taille=14, ancre="start", gras=True)
    for ident, nom, x, y in acteurs:
        f.noeuds[ident] = (x, y + 4, 28, 60, "rect")
        f.cercle(x, y - 14, 8, CARD, FG, 1.6)
        f.ligne(x, y - 6, x, y + 16, FG, 1.6, couche=2)
        f.ligne(x - 12, y, x + 12, y, FG, 1.6, couche=2)
        f.ligne(x, y + 16, x - 10, y + 32, FG, 1.6, couche=2)
        f.ligne(x, y + 16, x + 10, y + 32, FG, 1.6, couche=2)
        f.texte(x, y + 50, nom, taille=13)
    for ident, libelle, cx, cy in cas:
        f.boite(ident, cx, cy, libelle, taille=13, forme="ellipse")
    for a, c in liens:
        f.lien(a, c, stroke=FG, sw=1.3)
    for src, dst, kind in relations:
        f.lien(src, dst, etiquette=f"<<{kind}>>", stroke=MU, dash="5 4", tete="ouvert")
    return f


# --------------------------------------------------------------------------- icônes réseau
def icone_reseau(f, ident, type_, cx, cy, etiquette, sous_etiquette=None, position="bas"):
    """Icône simple pour un schéma réseau ; enregistre un noeud (rectangle englobant) à relier avec f.lien().
    type_ : pc | serveur | commutateur | routeur | nuage | tablette | imprimante."""
    if type_ == "pc":
        f.noeud(ident, cx, cy, 54, 40)
        f.rect(cx - 21, cy - 16, 42, 26, 3, CARD, FG, 1.5)
        f.ligne(cx - 10, cy + 16, cx + 10, cy + 16, FG, 2, couche=2)
        f.ligne(cx, cy + 10, cx, cy + 16, FG, 2, couche=2)
    elif type_ == "tablette":
        f.noeud(ident, cx, cy, 36, 46)
        f.rect(cx - 15, cy - 20, 30, 40, 4, CARD, FG, 1.5)
        f.cercle(cx, cy + 14, 2, FG, FG, 1)
    elif type_ == "serveur":
        f.noeud(ident, cx, cy, 46, 52)
        for i in range(3):
            f.rect(cx - 20, cy - 24 + i * 17, 40, 14, 3, CARD, FG, 1.5)
            f.cercle(cx + 13, cy - 17 + i * 17, 2, PR, PR, 1)
    elif type_ == "commutateur":
        f.noeud(ident, cx, cy, 64, 28)
        f.rect(cx - 30, cy - 12, 60, 24, 3, CARD, FG, 1.5)
        for i in range(5):
            f.rect(cx - 24 + i * 10, cy - 3, 6, 7, 1, FG, FG, 1)
    elif type_ == "routeur":
        f.noeud(ident, cx, cy, 52, 40, "ellipse")
        f.ellipse(cx, cy, 24, 18, CARD, FG, 1.5)
        f.fleche(cx - 12, cy, cx + 12, cy, FG, 1.5, couche=3)
        f.fleche(cx + 12, cy, cx - 12, cy, FG, 1.5, couche=3)
    elif type_ == "nuage":
        f.noeud(ident, cx, cy, 90, 54, "ellipse")
        f.chemin(f"M{_n(cx-34)},{_n(cy+14)} a14,14 0 0 1 4,-27 a18,18 0 0 1 34,-6 a15,15 0 0 1 28,10 a12,12 0 0 1 -4,23 z", CARD, FG, 1.5, couche=2)
    elif type_ == "imprimante":
        f.noeud(ident, cx, cy, 46, 36)
        f.rect(cx - 20, cy - 4, 40, 18, 3, CARD, FG, 1.5)
        f.rect(cx - 12, cy - 16, 24, 12, 1, CARD, FG, 1.5)
    else:
        raise ValueError(type_)
    demi = f.noeuds[ident][3] / 2
    if position == "haut":
        f.texte(cx, cy - demi - (17 if sous_etiquette else 6), etiquette, taille=13, gras=True)
        if sous_etiquette:
            f.texte(cx, cy - demi - 4, sous_etiquette, taille=12, fill=MU)
    else:
        f.texte(cx, cy + demi + 15, etiquette, taille=13, gras=True)
        if sous_etiquette:
            f.texte(cx, cy + demi + 29, sous_etiquette, taille=12, fill=MU)
