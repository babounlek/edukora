"""Figures du Paper 2 Physics inedit : un circuit (ENONCE de la question 3) et le graphique de Hooke (CORRIGE de la question 7).
Le trace attendu (graphique) n'est que dans le corrige ; les donnees et le calcul du ressort sont les constantes de ce fichier."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from figs_physics_p1 import circuit_serie_parallele, fs  # noqa: E402
from figures_svg import Fig, Repere, FG, MU, PR, DG  # noqa: E402

CIRCUIT_P2 = {"U": 24, "R1": 5, "R2": 12, "R3": 4}
HOOKE_FORCE = [0, 2, 4, 6, 8, 10, 12]  # N
HOOKE_EXT = [0, 1.0, 2.1, 3.0, 4.1, 5.0, 6.2]  # cm


def pente_origine(xs, ys):
    """Meilleure droite passant par l'origine (moindres carres) : k = somme(x*y) / somme(x*x)."""
    return sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)


def circuit_p2():
    c = CIRCUIT_P2
    return circuit_serie_parallele(
        c["U"], c["R1"], c["R2"], c["R3"], "Figure 1", "Circuit avec une pile, un amperemetre et trois resistances",
        f"Pile de {c['U']} volts en serie avec un amperemetre et une resistance de {c['R1']} ohms, puis deux resistances de {c['R2']} ohms "
        f"et {c['R3']} ohms montees en parallele.")


def graphe_hooke():
    k = pente_origine(HOOKE_EXT, HOOKE_FORCE)
    f = Fig(460, 338, "Graphique de la force en fonction de l'allongement d'un ressort",
            f"Sept points mesures, de 0 a 12 newtons et de 0 a 6,2 centimetres, alignes sur une droite qui passe par l'origine ; la pente "
            f"de la meilleure droite est d'environ {k:.2f} newtons par centimetre.")
    r = Repere(f, 54, 14, 380, 256, 0, 7, 0, 14, xpas=1, ypas=2, xetiq="", yetiq="")
    r.droite(k, 0, couleur=PR)
    for x, y in zip(HOOKE_EXT, HOOKE_FORCE):
        r.point(x, y, couleur=DG)
    f.texte(r.x0 + r.w / 2, 308, "Extension (cm)", taille=14)
    f.texte(r.x0 + 6, r.y0 + 10, "Force (N)", taille=13, ancre="start", fill=MU)
    f.legende("Solution: graph of force against extension", y=330)
    return f.render(), k


def toutes():
    g, k = graphe_hooke()
    return {"circuit": circuit_p2(), "hooke": g, "_k": k}


if __name__ == "__main__":
    for nom, v in toutes().items():
        print(nom, v if nom == "_k" else len(v))
