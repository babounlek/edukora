"""
Redessin vectoriel de deux figures de « Physique BAC C 2026 » (test élève F1 et F2, 2026-10-19).

Pas de PDF d'origine pour les épreuves francophones (voir le skill reproduire-figure-sans-filigrane) : les deux
figures ingérées sont des scans (l'un porte le texte fantôme « b193c36 », l'autre est un scan de 281x278 px),
elles sont donc redessinées d'après l'original ET l'énoncé, sans rien y ajouter qui donne une réponse.

    python redessiner.py <dossier_sortie>

Écrit <id>.png (id de Figure) et rapport.jsonl au format de `appliquer_figures_propres` (statut « redessinee »).
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Arc, Circle  # noqa: E402

NOIR = "#111111"
plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans"})


def toile(largeur, hauteur):
    fig = plt.figure(figsize=(largeur / 100, hauteur / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, largeur)
    ax.set_ylim(hauteur, 0)  # y vers le bas, comme une page
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def fleche(ax, x0, y0, x1, y1, lw=1.8):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=NOIR, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=16))


def dispositif():
    """Document 1 : ressort et poignée A, boule (S) en H, point O au bord de la table, chute vers B, trous E, F, G."""
    fig, ax = toile(735, 390)
    ax.text(10, 24, "Document 1 : Dispositif", fontsize=15, fontweight="bold", color=NOIR, va="center")

    y_haut, y_bas = 140, 290
    x_a, x_h, x_o = 150, 350, 450
    # Plan horizontal supérieur : de la poignée jusqu'au point O, puis l'axe x.
    ax.plot([x_a, x_o], [y_haut, y_haut], color=NOIR, lw=2.2, solid_capstyle="butt")
    fleche(ax, x_o, y_haut, 660, y_haut)
    ax.text(668, y_haut - 4, r"$x$", fontsize=17, color=NOIR, va="center")
    # Poignée A, tige, ressort à spires non jointives, tige de poussée.
    y_axe = y_haut - 17                     # hauteur du centre de la boule : la tige et le ressort sont à cette hauteur
    ax.add_patch(Circle((x_a, y_axe), 9, fill=False, ec=NOIR, lw=2))
    ax.text(x_a, y_axe - 30, r"$A$", fontsize=17, color=NOIR, ha="center", va="center")
    ax.plot([x_a + 9, 205], [y_axe, y_axe], color=NOIR, lw=2)
    xs = np.linspace(205, 305, 11)
    ys = [y_axe + (12 if i % 2 else -12) * (0 < i < 10) for i in range(11)]
    ax.plot(xs, ys, color=NOIR, lw=2, solid_joinstyle="miter")
    ax.plot([305, x_h - 17], [y_axe, y_axe], color=NOIR, lw=2)
    # Boule (S) posée en H.
    ax.add_patch(Circle((x_h, y_haut - 17), 17, fill=False, ec=NOIR, lw=2.2))
    ax.text(x_h + 28, y_haut - 58, r"$(S)$", fontsize=16, color=NOIR, ha="center", va="center")
    ax.plot([x_h], [y_haut], "o", color=NOIR, ms=5)
    ax.text(x_h, y_haut + 24, r"$H$", fontsize=16, color=NOIR, ha="center", va="center")
    # Point O et axe y vers le bas, B au pied de la chute.
    ax.plot([x_o], [y_haut], "o", color=NOIR, ms=6)
    ax.text(x_o + 4, y_haut - 22, r"$O$", fontsize=16, color=NOIR, ha="center", va="center")
    fleche(ax, x_o, y_haut, x_o, 372)
    ax.text(x_o + 16, 368, r"$y$", fontsize=17, color=NOIR, va="center")
    # Plan inférieur : B puis trois trous E, F, G à intervalles réguliers (BE = EF = FG = d).
    ax.plot([x_o, 725], [y_bas, y_bas], color=NOIR, lw=2.2, solid_capstyle="butt")
    ax.plot([x_o], [y_bas], "o", color=NOIR, ms=6)
    ax.text(x_o - 22, y_bas - 16, r"$B$", fontsize=16, color=NOIR, ha="center", va="center")
    for lettre, x in (("E", 530), ("F", 610), ("G", 690)):
        # Le trou : un petit godet sous le plan, le plan est interrompu à cet endroit.
        ax.plot([x - 11, x + 11], [y_bas, y_bas], color="white", lw=4, solid_capstyle="butt", zorder=3)
        ax.add_patch(Arc((x, y_bas), 22, 26, theta1=0, theta2=180, color=NOIR, lw=2.2, zorder=4))
        ax.text(x, y_bas + 36, rf"${lettre}$", fontsize=16, color=NOIR, ha="center", va="center")
    return fig


def balancier():
    """Balancier : tige de longueur L = 4R suspendue en O, disque de rayon R soudé par son bord à l'extrémité libre."""
    fig, ax = toile(380, 420)
    x_tige, y_o, r = 190, 60, 52
    y_fin = y_o + 4 * r                     # extrémité libre de la tige : L = 4R
    # Support fixe hachuré et axe (Δ) vu par sa trace, point O.
    ax.plot([x_tige - 70, x_tige + 70], [y_o - 20, y_o - 20], color=NOIR, lw=2.6, solid_capstyle="butt")
    for x in np.arange(x_tige - 66, x_tige + 70, 14):
        ax.plot([x, x + 9], [y_o - 20, y_o - 31], color=NOIR, lw=1.4)
    ax.plot([x_tige, x_tige], [y_o - 20, y_fin], color=NOIR, lw=3, solid_capstyle="butt")
    ax.add_patch(Circle((x_tige, y_o), 6, fc="white", ec=NOIR, lw=2, zorder=5))
    ax.text(x_tige + 17, y_o + 3, r"$O$", fontsize=16, color=NOIR, va="center")
    ax.text(x_tige - 80, y_o - 20, r"$(\Delta)$", fontsize=15, color=NOIR, ha="right", va="center")
    # Disque soudé par son bord à la tige.
    ax.add_patch(Circle((x_tige, y_fin + r), r, fill=False, ec=NOIR, lw=2.6))
    # Cotes : L le long de la tige, R sur le rayon du disque.
    x_cote = x_tige + 78
    ax.annotate("", xy=(x_cote, y_o), xytext=(x_cote, y_fin),
                arrowprops=dict(arrowstyle="<|-|>", color=NOIR, lw=1.4, shrinkA=0, shrinkB=0, mutation_scale=12))
    ax.plot([x_tige + 8, x_cote + 6], [y_o, y_o], color=NOIR, lw=1, ls=(0, (3, 3)))
    ax.plot([x_tige + 8, x_cote + 6], [y_fin, y_fin], color=NOIR, lw=1, ls=(0, (3, 3)))
    ax.text(x_cote + 14, (y_o + y_fin) / 2, r"$L$", fontsize=16, color=NOIR, va="center")
    ax.plot([x_tige, x_tige + r], [y_fin + r, y_fin + r], color=NOIR, lw=1.6, ls=(0, (4, 3)))
    ax.plot([x_tige], [y_fin + r], "o", color=NOIR, ms=3.5)
    ax.text(x_tige + r / 2, y_fin + r - 15, r"$R$", fontsize=15, color=NOIR, ha="center", va="center")
    return fig


def main(dossier):
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    lots = [(1405, dispositif, "Document 1 : Dispositif (Situation 1, exercice 4)"),
            (1233, balancier, "Balancier (exercice 3, partie B)")]
    with open(dossier / "rapport.jsonl", "w", encoding="utf-8") as rapport:
        for figure_id, dessin, note in lots:
            fig = dessin()
            fig.savefig(dossier / f"{figure_id}.png", dpi=100, facecolor="white")
            plt.close(fig)
            rapport.write(json.dumps({"id": figure_id, "statut": "redessinee", "score": 1.0, "note": note}, ensure_ascii=False) + "\n")
    print("écrit dans", dossier)


if __name__ == "__main__":
    main(sys.argv[1])
