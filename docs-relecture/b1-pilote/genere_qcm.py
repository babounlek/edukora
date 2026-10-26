"""
Pilote B1 : conversion en QCM des questions ouvertes de maths BEPC (6 thèmes fréquents, sans figure).

Entrée  : /tmp/b1_items.json (export des items ouverts)
Sortie  : /tmp/b1_propositions.json (QCM proposés, RIEN n'est écrit en base)

Chaque proposition porte la bonne réponse et trois mauvaises réponses qui sont chacune une erreur d'élève réaliste
(la raison est écrite dans le corrigé). Les valeurs numériques sont RECALCULÉES ici (assert) avant d'être écrites.
"""
import json
import math
from fractions import Fraction

items = {i["id"]: i for i in json.load(open("/tmp/b1_items.json", encoding="utf-8"))}


def f(x):
    return f"{x}".replace(".", "{,}")


# ---------------------------------------------------------------- contrôles numériques
# statistiques
t1476 = {0: 4, 1: 6, 2: 5, 3: 3, 4: 2}
n = sum(t1476.values())
assert n == 20 and sum(k * v for k, v in t1476.items()) == 33 and Fraction(33, 20) == Fraction(165, 100)
srt = sorted(k for k, v in t1476.items() for _ in range(v))
assert (srt[9] + srt[10]) / 2 == 1.5
temps = [27, 24, 31, 22, 26, 35, 23, 29, 25]
st = sorted(temps)
assert st[4] == 26 and st[3] == 25 and st[5] == 27 and round(sum(temps) / 9, 1) == 26.9
t1478 = {1: 5, 2: 9, 3: 10, 4: 6, 5: 2}
assert sum(t1478.values()) == 32
cum, c = {}, 0
for k, v in t1478.items():
    c += v
    cum[k] = c
assert cum == {1: 5, 2: 14, 3: 24, 4: 30, 5: 32}  # rangs 16 et 17 : valeur 3
assert round(sum(k * v for k, v in t1478.items()) / 32, 2) == 2.72
masses = [6, 7, 8, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 15, 16, 17, 18]
assert len(masses) == 17 and masses[4] == 10 and masses[12] == 14 and masses[3] == 9 and masses[11] == 13
assert (masses[3] + masses[4]) / 2 == 9.5 and (masses[11] + masses[12]) / 2 == 13.5
xs, ys = [10, 15, 20, 25, 30], [80, 95, 130, 150, 170]
assert sum(xs) / 5 == 20 and sum(ys) / 5 == 125 and sorted(ys)[2] == 130
tmp = [28, 31, 26, 33, 29, 27, 30]
assert max(tmp) - min(tmp) == 7 and max(tmp) + min(tmp) == 59 and round(sum(tmp) / 7, 1) == 29.1
notes_eff = {6: 2, 8: 5, 10: 9, 12: 7, 14: 3, 16: 1}
assert 16 - 6 == 10 and sum(notes_eff.values()) == 27 and 9 - 1 == 8 and 16 + 6 == 22
# algèbre
for x in (-3, 0, 1, 2, 5):
    assert (5 * x - 2) ** 2 == 25 * x * x - 20 * x + 4
    assert 9 * x * x - 64 == (3 * x - 8) * (3 * x + 8)
    assert (2 * x + 3) ** 2 - (x - 1) ** 2 == (x + 4) * (3 * x + 2)
    assert (2 * x + 5) * (x - 1) - (2 * x + 5) * (3 * x + 4) == -((2 * x + 5) ** 2)
for x in (Fraction(1), Fraction(2), Fraction(7)):
    assert (x * x - 25) / (x * x + 10 * x + 25) == (x - 5) / (x + 5)
    # les mauvaises réponses ne sont pas égales à la bonne
    assert (x - 5) / (x + 5) != 1 and (x - 5) / (x + 5) != Fraction(-5) / (2 * x + 5) and (x - 5) / (x + 5) != (x + 5) / (x - 5)
assert 126 == 18 * 7 and 90 == 18 * 5 and math.gcd(126, 90) == 18 and 126 // 9 == 14 and 90 // 9 == 10
assert 126 // 6 == 21 and 90 // 6 == 15
# radicaux
assert 98 == 49 * 2 and 45 == 9 * 5 and 48 == 16 * 3 and 27 == 9 * 3 and 75 == 25 * 3
assert abs(7 * math.sqrt(2) - math.sqrt(98)) < 1e-9
assert abs(3 * math.sqrt(5) - math.sqrt(3) * math.sqrt(15)) < 1e-9
assert abs(2 * math.sqrt(5) - 10 / math.sqrt(5)) < 1e-9
assert abs((3 * math.sqrt(48) - 2 * math.sqrt(27) + math.sqrt(75)) - 11 * math.sqrt(3)) < 1e-9
assert 12 - 6 + 5 == 11 and 4 - 3 + 5 == 6 and 12 + 6 + 5 == 23 and 12 - 6 - 5 == 1
vals = [2 * math.sqrt(5), 10 * math.sqrt(5), 5 * math.sqrt(2), 5 * math.sqrt(5)]
assert len({round(v, 6) for v in vals}) == 4
# géométrie
assert 2 * 5.4 == 10.8 and round(5.4 ** 2, 2) == 29.16
assert 4 * 9 == 36 and math.isclose(math.sqrt(36), 6) and 13 / 2 == 6.5
# repère
A, B = (3, -1), (-2, 4)
assert (B[0] - A[0], B[1] - A[1]) == (-5, 5)
assert ((5 + -1) / 2, (2 + -4) / 2) == (2, -1) and ((5 - -1) / 2, (2 - -4) / 2) == (3, 3)
assert math.hypot(4, 3) == 5
Aa, Bb, Cc, Dd = (-1, 2), (3, 0), (5, 4), (1, 6)
assert (Bb[0] - Aa[0], Bb[1] - Aa[1]) == (4, -2) == (Cc[0] - Dd[0], Cc[1] - Dd[1])
P, Q, R = (-4, 0), (0, 3), (3, -1)
PQ, QR = (Q[0] - P[0], Q[1] - P[1]), (R[0] - Q[0], R[1] - Q[1])
assert PQ == (4, 3) and QR == (3, -4) and PQ[0] * QR[0] + PQ[1] * QR[1] == 0
A2, B2, C2 = (1, 4), (-2, 0), (4, 0)
M2 = ((B2[0] + C2[0]) / 2, (B2[1] + C2[1]) / 2)
assert M2 == (1, 0) and math.hypot(A2[0] - M2[0], A2[1] - M2[1]) == 4
assert math.hypot(A2[0] - B2[0], A2[1] - B2[1]) == 5 and math.hypot(M2[0] - B2[0], 0) == 3 and C2[0] - B2[0] == 6

# ---------------------------------------------------------------- les conversions
# (id, enonce_neuf ou None, bonne, [(fausse, raison), x3])
C = []


def add(i, enonce, bonne, fausses):
    assert len(fausses) == 3, i
    C.append((i, enonce, bonne, fausses))


add(2553, None, r"$25x^2 - 20x + 4$", [
    (r"$25x^2 - 4$", "confusion avec $(a-b)(a+b)$ : le double produit $-2ab$ est oublié."),
    (r"$25x^2 + 20x + 4$", "erreur de signe : le double produit de $(a-b)^2$ est $-2ab$, pas $+2ab$."),
    (r"$5x^2 - 20x + 4$", "le carré de $5x$ est $(5x)^2 = 25x^2$, pas $5x^2$."),
])
add(2554, None, r"$(3x-8)(3x+8)$", [
    (r"$(3x-8)^2$", "confusion entre $a^2-b^2=(a-b)(a+b)$ et le carré d'une différence."),
    (r"$(9x-8)(9x+8)$", "$9x^2$ est le carré de $3x$, pas de $9x$."),
    (r"$(3x+8)^2$", "confusion avec le carré d'une somme : $9x^2-64$ n'a pas de terme en $x$, donc ce n'est pas un carré parfait."),
])
add(2556, None, r"$\dfrac{x-5}{x+5}$", [
    (r"$1$", "le dénominateur $x^2+10x+25$ est un carré $(x+5)^2$, pas une différence de deux carrés."),
    (r"$\dfrac{-5}{2x+5}$", "on ne peut pas simplifier les termes $x^2$ du numérateur et du dénominateur : il faut d'abord factoriser."),
    (r"$\dfrac{x+5}{x-5}$", "le numérateur et le dénominateur sont inversés."),
])
add(2557, None, r"$(x+4)(3x+2)$", [
    (r"$(x+2)(3x+2)$", "$(2x+3)-(x-1)=x+4$ : le signe moins change $-1$ en $+1$."),
    (r"$(x+4)(3x+4)$", "$(2x+3)+(x-1)=3x+2$ : le $-1$ ne devient pas $+1$ dans la somme."),
    (r"$(x+2)(3x+4)$", "les deux erreurs de signe précédentes sont commises à la fois."),
])
add(1476, None, r"$1{,}65$", [
    (r"$2$", "on a fait la moyenne des cinq valeurs $0,1,2,3,4$ sans tenir compte des effectifs."),
    (r"$6{,}6$", "la somme $33$ a été divisée par $5$ (nombre de valeurs) au lieu de $20$ (nombre d'élèves)."),
    (r"$1{,}5$", "c'est la médiane de la série, pas sa moyenne."),
])
add(1477,
    "Lors d'une course scolaire de 5 km, on a chronométré 9 coureurs. Voici les temps obtenus, en minutes :\n\n"
    "27 ; 24 ; 26 ; 31 ; 22 ; 35 ; 23 ; 29 ; 25.\n\nQuelle est la médiane de cette série de temps ?",
    r"$26$ minutes", [
        (r"$26{,}9$ minutes", "c'est la moyenne ($242 \\div 9$), pas la médiane."),
        (r"$22$ minutes", "c'est la $5^{\\text{e}}$ valeur de la liste telle qu'elle est donnée : il faut d'abord ranger les valeurs par ordre croissant."),
        (r"$28{,}5$ minutes", "c'est le milieu entre la plus petite ($22$) et la plus grande ($35$) valeur, pas la valeur centrale de la série rangée."),
    ])
add(1478,
    "Un vétérinaire a recensé, pour 32 animaux d'un même élevage, le nombre de vaccins reçus au cours de l'année écoulée. "
    "Les résultats sont donnés dans le tableau suivant :\n\n"
    "| $x_i$ (nombre de vaccins) | 1 | 2 | 3 | 4 | 5 |\n|---|---|---|---|---|---|\n"
    "| $n_i$ (nombre d'animaux) | 5 | 9 | 10 | 6 | 2 |\n\n"
    "Quelle est la médiane du nombre de vaccins reçus par animal ?",
    r"$3$", [
        (r"$2{,}72$", "c'est la moyenne ($87 \div 32$), pas la médiane."),
        (r"$16$", "$16$ est le rang du milieu ($32 \div 2$), pas une valeur de la série."),
        (r"$10$", "$10$ est le plus grand effectif, pas la médiane."),
    ])
add(1479,
    "Un contrôleur qualité a mesuré la masse, en kg, de 17 sacs de riz prélevés au hasard dans un entrepôt. Les masses obtenues, "
    "déjà rangées par ordre croissant, sont (en kg) :\n\n6 ; 7 ; 8 ; 9 ; 10 ; 10 ; 11 ; 11 ; 12 ; 12 ; 13 ; 13 ; 14 ; 15 ; 16 ; 17 ; 18.\n\n"
    "On rappelle que le rang de $Q_1$ est $\\dfrac{n}{4}$ et celui de $Q_3$ est $\\dfrac{3n}{4}$, arrondis à l'entier supérieur lorsque ce ne sont pas des entiers ($n$ est l'effectif total).\n\n"
    "Quels sont le premier quartile $Q_1$ et le troisième quartile $Q_3$ de cette série ?",
    r"$Q_1 = 10$ et $Q_3 = 14$", [
        (r"$Q_1 = 9$ et $Q_3 = 13$", "le rang $4{,}25$ s'arrondit à l'entier supérieur ($5$), pas à l'entier inférieur."),
        (r"$Q_1 = 9{,}5$ et $Q_3 = 13{,}5$", "on a fait la moyenne de deux valeurs voisines : ce n'est pas la règle du cours."),
        (r"$Q_1 = 4{,}25$ et $Q_3 = 12{,}75$", "ce sont les rangs, pas les valeurs de la série qui occupent ces rangs."),
    ])
# 1480 (point moyen d'une série à deux variables) : NON converti, hors niveau BEPC d'après le relecteur indépendant.
add(3344, None, r"$7$ °C", [
    (r"$33$ °C", "c'est la plus grande valeur, pas l'étendue."),
    (r"$29$ °C", "c'est la médiane de la série, pas son étendue."),
    (r"$29{,}1$ °C", "c'est la moyenne de la série, pas son étendue."),
])
add(3345, None, r"$10$ points", [
    (r"$8$ points", "l'étendue se calcule sur les notes, jamais sur les effectifs ($9-1$)."),
    (r"$27$ points", "$27$ est l'effectif total, pas l'étendue."),
    (r"$16$ points", "c'est la plus grande note : l'étendue est la différence entre la plus grande et la plus petite note."),
])
add(1176,
    r"On considère l'expression $E(x) = (2x+5)(x-1) - (2x+5)(3x+4)$. Quelle est la forme factorisée de $E(x)$ ?",
    r"$-(2x+5)^2$", [
        (r"$(2x+5)^2$", "le facteur $(x-1)-(3x+4)$ vaut $-(2x+5)$ : le signe moins ne disparaît pas."),
        (r"$(2x+5)(-2x+3)$", "dans $(x-1)-(3x+4)$, le signe moins s'applique aux deux termes de la parenthèse : $x-1-3x-4=-2x-5$."),
        (r"$(2x+5)(4x+3)$", "on a additionné les deux produits au lieu de les soustraire."),
    ])
add(1177,
    r"On donne $a = 126$ et $b = 90$, dont le plus grand commun diviseur est $18$. On écrit $a = 18a'$ et $b = 18b'$. "
    r"Quelles sont les valeurs de $a'$ et de $b'$ ?",
    r"$a' = 7$ et $b' = 5$", [
        (r"$a' = 108$ et $b' = 72$", "on a soustrait $18$ au lieu de diviser par $18$."),
        (r"$a' = 14$ et $b' = 10$", "on a divisé par $9$ : $14$ et $10$ ne sont pas premiers entre eux, donc $9$ n'est pas le pgcd."),
        (r"$a' = 21$ et $b' = 15$", "on a divisé par $6$ : $21$ et $15$ ne sont pas premiers entre eux."),
    ])
add(2673, None, r"$7\sqrt{2}$", [
    (r"$49\sqrt{2}$", "on sort $49$ de la racine alors qu'il faut sortir sa racine carrée, $7$."),
    (r"$7\sqrt{14}$", "$14$ contient encore le facteur $2$ et $98 \\neq 7 \\times 14$ sous la bonne forme : on n'a pas décomposé $98 = 49 \\times 2$."),
    (r"$2\sqrt{7}$", "les rôles sont échangés : c'est $\\sqrt{49}=7$ qui sort de la racine."),
])
add(2675, None, r"$3\sqrt{5}$", [
    (r"$5\sqrt{3}$", "les rôles sont échangés : $\\sqrt{9}=3$ sort de la racine, $5$ y reste."),
    (r"$9\sqrt{5}$", "on sort $9$ de la racine alors qu'il faut sortir sa racine carrée, $3$."),
    (r"$3\sqrt{2}$", "on a additionné $3$ et $15$ sous la racine : $\\sqrt{3}\\times\\sqrt{15}=\\sqrt{3\\times15}$."),
])
add(2676, None, r"$2\sqrt{5}$", [
    (r"$10\sqrt{5}$", "après avoir multiplié par $\\sqrt{5}$, le dénominateur vaut $5$ : il faut encore diviser $10\\sqrt{5}$ par $5$."),
    (r"$2$", "on a multiplié seulement le dénominateur par $\\sqrt{5}$ : il faut multiplier aussi le numérateur."),
    (r"$5\sqrt{5}$", "$10\\sqrt{5}$ a été divisé par $2$ au lieu de $5$."),
])
add(2678, None, r"$11\sqrt{3}$", [
    (r"$6\sqrt{3}$", "les coefficients $3$ et $2$ placés devant les racines ont été oubliés ($4-3+5$)."),
    (r"$23\sqrt{3}$", "le signe de $-2\\sqrt{27}$ n'a pas été respecté ($12+6+5$)."),
    (r"$\sqrt{3}$", "le signe de $+\\sqrt{75}$ n'a pas été respecté ($12-6-5$)."),
])
add(2685, None, r"$10{,}8$ cm", [
    (r"$5{,}4$ cm", "$RJ$ est la moitié de l'hypoténuse $ST$, pas sa longueur."),
    (r"$2{,}7$ cm", "on a pris la moitié de $RJ$ au lieu de la doubler."),
    (r"$16{,}2$ cm", "confusion avec la propriété du centre de gravité (un tiers, deux tiers) : ici la médiane relative à l'hypoténuse vaut exactement la moitié de l'hypoténuse."),
])
add(2687,
    r"Dans un triangle $MNP$, $K$ est le milieu du segment $[MN]$. On donne $MN = 15$ cm et $PK = 7{,}5$ cm. Que peut-on affirmer ?",
    r"Le triangle $MNP$ est rectangle en $P$", [
        (r"Le triangle $MNP$ est rectangle en $M$", "l'angle droit est au sommet $P$, opposé au côté $[MN]$ dont $K$ est le milieu."),
        (r"Le triangle $MNP$ est rectangle en $N$", "l'angle droit est au sommet $P$, opposé au côté $[MN]$ dont $K$ est le milieu."),
        (r"Le triangle $MNP$ est isocèle en $P$", "$PK=\\dfrac{MN}{2}$ ne dit rien sur les longueurs $PM$ et $PN$."),
    ])
add(2688, None, r"$6$ cm", [
    (r"$6{,}5$ cm", "c'est la moitié de l'hypoténuse $BC = 13$ cm, qui ne vaut $AH$ que dans un cas particulier."),
    (r"$36$ cm", "$36$ est $AH^2$ : il faut encore prendre la racine carrée."),
    (r"$\sqrt{13}$ cm", "la relation est $AH^2 = BH \\times HC$ (produit), pas $BH + HC$ (somme)."),
])
add(2865, None, r"$(-5\,;\,5)$", [
    (r"$(5\,;\,-5)$", "ce sont les coordonnées de $\\overrightarrow{BA}$ : on retranche le départ à l'arrivée, pas l'inverse."),
    (r"$(1\,;\,3)$", "on a additionné les coordonnées au lieu de les soustraire."),
    (r"$(-5\,;\,3)$", "$y_B - y_A = 4 - (-1) = 5$ : le signe moins devant $-1$ devient $+1$."),
])
add(2866, None, r"$K(2\,;\,-1)$", [
    (r"$K(4\,;\,-2)$", "les sommes n'ont pas été divisées par $2$."),
    (r"$K(3\,;\,3)$", "on a soustrait les coordonnées au lieu de les additionner."),
    (r"$K(2\,;\,3)$", "pour $y$, on a soustrait au lieu d'additionner."),
])
add(2867, None, r"$5$ cm", [
    (r"$7$ cm", "on a additionné $4$ et $3$ : la distance est $\\sqrt{4^2+3^2}$."),
    (r"$25$ cm", "il manque la racine carrée : $4^2+3^2=25$ est le carré de la distance."),
    (r"$\sqrt{7}$ cm", "on a pris la racine de $4+3$ au lieu de $4^2+3^2$."),
])
add(2868,
    r"Dans un repère orthonormé, on donne $A(-1\,;\,2)$, $B(3\,;\,0)$, $C(5\,;\,4)$ et $D(1\,;\,6)$. "
    r"On compare les vecteurs $\overrightarrow{AB}$ et $\overrightarrow{DC}$. Quelle affirmation est correcte ?",
    r"$\overrightarrow{AB}(4\,;\,-2)$ et $\overrightarrow{DC}(4\,;\,-2)$ : ils sont égaux, donc $ABCD$ est un parallélogramme", [
        (r"$\overrightarrow{AB}(-4\,;\,2)$ et $\overrightarrow{DC}(4\,;\,-2)$ : ils sont opposés, donc $ABCD$ n'est pas un parallélogramme",
         "$\\overrightarrow{AB}$ a pour coordonnées $(x_B-x_A\\,;\\,y_B-y_A)=(4\\,;\\,-2)$ : on a calculé $\\overrightarrow{BA}$, en retranchant l'arrivée au départ."),
        (r"$\overrightarrow{AB}(4\,;\,-2)$ et $\overrightarrow{DC}(-4\,;\,2)$ : ils sont opposés, donc $ABCD$ n'est pas un parallélogramme",
         "$\\overrightarrow{DC}$ a pour coordonnées $(x_C-x_D\\,;\\,y_C-y_D)=(4\\,;\\,-2)$ : on a calculé $\\overrightarrow{CD}$."),
        (r"$\overrightarrow{AB}(4\,;\,2)$ et $\overrightarrow{DC}(4\,;\,-2)$ : ils sont différents, donc $ABCD$ n'est pas un parallélogramme",
         "$y_B - y_A = 0 - 2 = -2$ : une erreur de signe sur la seconde coordonnée."),
    ])
add(2869,
    r"Dans un repère orthonormé, on donne les points $P(-4\,;\,0)$, $Q(0\,;\,3)$ et $R(3\,;\,-1)$. Que peut-on affirmer du triangle $PQR$ ?",
    r"Il est rectangle en $Q$", [
        (r"Il est rectangle en $P$",
         "$PQ^2+PR^2=25+50=75$ n'est pas égal à $QR^2=25$ : l'angle droit est en face du plus grand côté $[PR]$, donc en $Q$."),
        (r"Il est rectangle en $R$",
         "$QR^2+PR^2=25+50=75$ n'est pas égal à $PQ^2=25$ : l'angle droit est en face du plus grand côté $[PR]$, donc en $Q$."),
        (r"Il n'est pas rectangle",
         "avec $PQ^2=25$, $QR^2=25$ et $PR^2=50$, on a $PQ^2+QR^2=PR^2$ : la réciproque du théorème de Pythagore donne un angle droit en $Q$."),
    ])
add(2870,
    r"Dans un repère orthonormé (unité : $1$ cm), on donne les points $A(1\,;\,4)$, $B(-2\,;\,0)$ et $C(4\,;\,0)$. "
    r"$M$ est le milieu du segment $[BC]$. Quelle est la longueur $AM$ ?",
    r"$4$ cm", [
        (r"$5$ cm", "$5$ est la longueur $AB$ (ou $AC$), pas $AM$."),
        (r"$3$ cm", "$3$ est la longueur $BM$, la moitié de $BC$."),
        (r"$6$ cm", "$6$ est la longueur $BC$, pas $AM$."),
    ])

# ---------------------------------------------------------------- assemblage
# Place de la bonne réponse (0 = a ... 3 = d) : suite fixe, répartie sur les quatre lettres.
POS = [1, 3, 0, 2, 2, 0, 3, 1, 3, 2, 0, 0, 2, 1, 3, 1, 0, 3, 2, 2, 3, 0, 1, 3, 0]
assert len(POS) == len(C), (len(POS), len(C))
t2 = [27, 24, 26, 31, 22, 35, 23, 29, 25]
assert sorted(t2) == st and t2[4] == 22 and (22 + 35) / 2 == 28.5 and t2[4] != 26
assert math.isclose(math.sqrt(3 + 15), 3 * math.sqrt(2)) and 126 - 18 == 108 and 90 - 18 == 72
assert len({round(v, 6) for v in (10.8, 5.4, 2.7, 16.2)}) == 4
import re


def virgules_math(s):
    """Dans les formules $...$ seulement : 5,4 devient 5{,}4 (sinon KaTeX affiche « 5, 4 »)."""
    return re.sub(r"\$\$[\s\S]+?\$\$|\$[^$\n]+\$", lambda m: re.sub(r"(?<=\d),(?=\d)", "{,}", m.group(0)), s)
LETTRES = "abcd"
out = []
for (i, enonce, bonne, fausses), pos in zip(C, POS):
    it = items[i]
    textes = [t for t, _ in fausses]
    textes.insert(pos, bonne)
    assert len(set(textes)) == 4, i
    choix = [{"lettre": LETTRES[k], "texte": t} for k, t in enumerate(textes)]
    reponses = "\n".join(f"- **{LETTRES[k]})** {fausses_raison}" for k, fausses_raison in
                         [(k, dict(fausses)[textes[k]]) for k in range(4) if k != pos])
    corrige = it["corrige"].rstrip() + "\n\n### Pourquoi les autres réponses sont fausses\n\n" + reponses + "\n"
    enonce_final = enonce if enonce else it["enonce"]
    if i == 1476:
        enonce_final = enonce_final.replace("une classe de 4e", "une classe de 3e")  # quiz BEPC : niveau 3e
    # $$ ... $$ : la regex précédente lit les blocs comme des formules, c'est le but ; $$ doublés non touchés par $[^$]+$ s'ils sont vides
    enonce_final, corrige = virgules_math(enonce_final), virgules_math(corrige)
    out.append({
        "id": i, "external_id": it["external_id"], "theme": it["theme"], "difficulte": it["difficulte"],
        "type_reponse": "QCM", "enonce_markdown": enonce_final, "corrige_markdown": corrige,
        "choix": choix, "reponse_correcte": LETTRES[pos],
    })

from collections import Counter
rep = Counter(o["reponse_correcte"] for o in out)
assert max(rep.values()) / len(out) <= 0.35, rep
print("N", len(out), "REPARTITION", dict(sorted(rep.items())))
json.dump(out, open("/tmp/b1_propositions.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
