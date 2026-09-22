"""Deuxième passe de quiz TI/Programmation (2026-09-19) : algorithmique, langage C, boucle for,
boucle while, trace d'exécution. Chaque valeur d'un corrigé est recalculée (Python) avant écriture ;
le script échoue si un corrigé et le calcul indépendant divergent.
Usage : py backend/ingest/_audit/gen_quiz_ti_prog2.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "_quiz"
OUT = ROOT / "cm"
REQ = {r["competence"]: r for r in json.loads((ROOT / "_batch_cm_prog2.json").read_text(encoding="utf-8"))}
MATIERE = "Programmation"


def item(theme, diff, idx, enonce, rappel, corrige, choix=None, bonne=None):
    r = REQ[theme]
    slug = "-".join("".join(c if c.isalnum() else " " for c in theme.lower().replace("é", "e")).split())
    return {
        "external_id": f"cqc-{slug}-{diff.lower().replace('é', 'e')}-{idx}",
        "theme": theme,
        "matiere": MATIERE,
        "cursus": r["cursus"],
        "enonce_markdown": enonce.strip(),
        "corrige_markdown": f"### Rappel de méthode\n\n{rappel.strip()}\n\n### Corrigé\n\n{corrige.strip()}",
        "difficulte_estimee": diff,
        "type_reponse": "QCM" if choix else "OUVERTE",
        "choix": [{"lettre": l, "texte": t} for l, t in zip("ABCD", choix)] if choix else [],
        "reponse_correcte": bonne or "",
        "source_exercises": [m["exercise_id"] for m in r["materiel_reference"]],
    }


def ecrire(theme, items):
    ids = [i["external_id"] for i in items]
    assert len(ids) == len(set(ids))
    for i in items:
        if i["type_reponse"] == "QCM":
            assert i["reponse_correcte"] in {c["lettre"] for c in i["choix"]} and len(i["choix"]) == 4
    slug = "-".join("".join(c if c.isalnum() else " " for c in theme.lower().replace("é", "e")).split())
    (OUT / f"{slug}.json").write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(theme, len(items), "items ->", slug)


# ============================================================ algorithmique
def premier_algo(n):
    i, tours = 2, 0
    while i * i <= n and n % i != 0:
        i += 1
        tours += 1
    return i * i > n, tours


assert premier_algo(17) == (True, 3) and premier_algo(21) == (False, 1)
assert premier_algo(2) == (True, 0) and premier_algo(4) == (False, 0)
for n in range(2, 300):
    assert premier_algo(n)[0] == all(n % d for d in range(2, n)), n


def max3(a, b, c):
    m = a
    if b > m: m = b
    if c > m: m = c
    return m


for t in [(4, 9, 6), (9, 4, 6), (6, 4, 9), (5, 5, 5), (-1, -7, -3)]:
    assert max3(*t) == max(t)
s = 0
for i in range(1, 5):
    if i % 2 == 0: s += i
assert s == 6
a, b = 3, 8
t = a; a = b; b = t
assert (a, b) == (8, 3)

T = "algorithmique"
ecrire(T, [
    item(T, "FAIBLE", 0, """
On considère l'algorithme suivant :

```
Lire a, b
s <- a + b
Afficher s
```

Quelles sont les variables d'entrée et la variable de sortie ?
""", "Les variables d'entrée sont celles dont la valeur est fournie par l'utilisateur (instruction `Lire`) ; les variables de sortie sont celles dont la valeur est communiquée (instruction `Afficher`) ; les autres sont des variables de travail.",
         "`Lire a, b` fournit les valeurs de `a` et `b` : ce sont les **entrées**. `Afficher s` communique le résultat : `s` est la **sortie**. `s` n'est pas lue au clavier, elle est calculée à partir de `a` et `b`.",
         ["Entrées : a et b ; sortie : s", "Entrée : s ; sorties : a et b", "Entrées : a, b et s ; aucune sortie", "Aucune entrée ; sortie : a"], "A"),
    item(T, "FAIBLE", 1, """
Deux variables entières `a` et `b` valent respectivement 3 et 8. On veut échanger leurs contenus.

1. Pourquoi les deux instructions `a <- b` puis `b <- a` ne réalisent-elles pas l'échange ?
2. Écrire une suite d'instructions correcte et donner les valeurs finales de `a` et `b`.
""", "Une affectation écrase l'ancienne valeur de la variable. Pour échanger deux variables, il faut sauvegarder l'une des deux valeurs dans une variable auxiliaire avant de l'écraser.",
         """
1. Après `a <- b`, `a` vaut 8 et l'ancienne valeur 3 est perdue ; l'instruction `b <- a` recopie alors 8 dans `b` : `a` et `b` valent tous deux 8.
2. Avec une variable auxiliaire `t` :

```
t <- a
a <- b
b <- t
```

`t` prend la valeur 3, `a` prend 8, puis `b` prend 3. Valeurs finales : **a = 8 et b = 3**.
""", None),
    item(T, "MOYENNE", 2, """
Écrire un algorithme qui lit trois nombres `a`, `b` et `c` et affiche le plus grand des trois. Le tester avec `a = 4`, `b = 9`, `c = 6`.
""", "Pour chercher un maximum, on retient une valeur candidate (initialisée avec le premier nombre), puis on compare successivement chaque autre nombre au candidat en le remplaçant s'il est plus grand.",
         """
```
Lire a, b, c
max <- a
Si b > max alors max <- b
Si c > max alors max <- c
Afficher max
```

Test avec `a = 4`, `b = 9`, `c = 6` : `max` vaut d'abord 4 ; `9 > 4` donc `max` devient 9 ; `6 > 9` est faux donc `max` reste 9. L'algorithme affiche **9**. Les deux `Si` sont indépendants : chaque nombre est comparé au meilleur candidat courant.
""", None),
    item(T, "MOYENNE", 3, """
On considère l'algorithme suivant (`mod` désigne le reste de la division entière) :

```
s <- 0
Pour i de 1 à 4 faire
    Si i mod 2 = 0 alors
        s <- s + i
    FinSi
FinPour
Afficher s
```

Quelle valeur est affichée ?
""", "Pour exécuter un algorithme à la main, on suit les valeurs de chaque variable tour par tour ; ici la condition `i mod 2 = 0` ne retient que les valeurs paires de `i`.",
         "Seules les valeurs paires de `i` sont ajoutées : pour `i = 1` rien, pour `i = 2` `s` devient 2, pour `i = 3` rien, pour `i = 4` `s` devient 6. L'algorithme affiche **6**. La valeur 10 correspondrait à la somme de tous les entiers de 1 à 4.",
         ["4", "6", "10", "2"], "B"),
    item(T, "ELEVEE", 4, """
On veut savoir si un entier `n` supérieur ou égal à 2 est premier, en cherchant son plus petit diviseur. Voici un algorithme :

```
Lire n
i <- 2
Tant que (i x i <= n) et (n mod i <> 0) faire
    i <- i + 1
FinTantQue
Si i x i > n alors Afficher "premier"
Sinon Afficher "non premier"
FinSi
```

1. Exécuter l'algorithme pour `n = 17` puis pour `n = 21`, en indiquant combien de fois le corps de la boucle est exécuté.
2. Expliquer pourquoi il suffit de tester les diviseurs `i` tels que `i x i <= n`.
""", "Un algorithme avec une condition composée `et` s'arrête dès que l'une des deux conditions devient fausse ; on identifie alors laquelle est la cause de l'arrêt pour interpréter le résultat.",
         """
1. **n = 17** : `i` vaut 2, 3, 4 (17 n'est divisible par aucun de ces entiers, et `i x i` reste inférieur ou égal à 17), le corps est exécuté **3 fois**, puis `i` vaut 5 et `5 x 5 = 25 > 17` arrête la boucle. Comme `i x i > n`, l'algorithme affiche « premier ».
   **n = 21** : pour `i = 2`, `21 mod 2 = 1`, le corps est exécuté **1 fois**, `i` vaut 3 ; `21 mod 3 = 0` fait échouer la seconde condition et arrête la boucle avec `i x i = 9 <= 21`. L'algorithme affiche « non premier » (3 divise 21).
2. Si `n` avait un diviseur `d` strictement supérieur à $\\sqrt{n}$, alors `n / d` serait un diviseur strictement inférieur à $\\sqrt{n}$ et aurait été trouvé avant. Il suffit donc de tester `i` jusqu'à $\\sqrt{n}$, c'est-à-dire tant que `i x i <= n`, ce qui évite de parcourir tous les entiers jusqu'à `n - 1`.
""", None),
])

# ============================================================ langage C
def puissance(x, n):
    r = 1
    for _ in range(n):
        r *= x
    return r


assert 7 // 2 == 3 and 7 % 2 == 1
assert sum([4, 7, 1, 8]) == 20

T = "langage C"
ecrire(T, [
    item(T, "FAIBLE", 0, """
Quelle instruction C lit au clavier un entier et le range dans la variable `int n;` ?
""", "`scanf` reçoit un format (`%d` pour un `int`) et l'**adresse** de la variable à remplir, obtenue avec l'opérateur `&`, car la fonction doit pouvoir modifier la variable.",
         "L'instruction correcte est `scanf(\"%d\", &n);` : `%d` est le format d'un entier et `&n` est l'adresse de `n`. Sans `&`, `scanf` recevrait la valeur de `n` au lieu de son adresse ; `%f` est le format d'un réel ; `input(n)` n'existe pas en C.",
         ['scanf("%d", n);', 'scanf("%d", &n);', 'scanf("%f", &n);', "input(n);"], "B"),
    item(T, "FAIBLE", 1, """
On considère le programme C suivant :

```c
#include <stdio.h>

int total = 10;

void ajouter(int x) {
    int total = 0;
    total = total + x;
}

int main() {
    ajouter(5);
    printf("%d", total);
    return 0;
}
```

Qu'affiche ce programme ? Expliquer pourquoi.
""", "Une variable déclarée dans une fonction est locale à cette fonction ; si elle porte le même nom qu'une variable globale, elle la masque à l'intérieur de la fonction sans jamais modifier la variable globale.",
         "Le programme affiche **10**. Dans `ajouter`, la déclaration `int total = 0;` crée une variable locale qui masque la variable globale `total` : l'addition `total + x` porte sur la variable locale (qui vaut 5), détruite à la fin de la fonction. La variable globale `total`, lue dans `main`, n'a jamais été modifiée.",
         None),
    item(T, "MOYENNE", 2, """
Écrire en C une fonction `int somme(int T[], int n)` qui retourne la somme des `n` premiers éléments du tableau `T`, puis donner la valeur retournée par `somme(T, 4)` pour `T = {4, 7, 1, 8}`.
""", "Une fonction qui parcourt un tableau utilise une variable accumulateur initialisée à 0 et une boucle qui visite chaque indice de 0 à `n - 1`.",
         """
```c
int somme(int T[], int n) {
    int s = 0;
    for (int i = 0; i < n; i++)
        s = s + T[i];
    return s;
}
```

Pour `T = {4, 7, 1, 8}` et `n = 4`, `s` prend successivement les valeurs 4, 11, 12 puis 20. La fonction retourne **20**. Les indices d'un tableau C commencent à 0 : la boucle s'arrête à `n - 1`.
""", None),
    item(T, "MOYENNE", 3, """
Qu'affiche l'instruction suivante en langage C ?

```c
printf("%d", 7 / 2);
```
""", "En C, la division de deux entiers est une division entière : le résultat est le quotient tronqué, sans partie décimale. L'opérateur `%` donne le reste.",
         "`7` et `2` sont deux entiers : `7 / 2` est une division entière dont le quotient est 3 (le reste `7 % 2` vaut 1). `printf(\"%d\", 7 / 2)` affiche donc **3**, et non 3.5. Pour obtenir 3.5, il faudrait au moins un opérande réel, par exemple `7 / 2.0`.",
         ["3.5", "3", "4", "3.0"], "B"),
    item(T, "ELEVEE", 4, """
On souhaite échanger les valeurs de deux variables entières avec une fonction. Voici une première version :

```c
#include <stdio.h>

void echanger(int a, int b) {
    int t = a;
    a = b;
    b = t;
}

int main() {
    int x = 3, y = 8;
    echanger(x, y);
    printf("%d %d", x, y);
    return 0;
}
```

1. Qu'affiche ce programme ? Pourquoi l'échange n'a-t-il pas lieu ?
2. Réécrire la fonction et l'appel pour que l'échange fonctionne, puis indiquer l'affichage obtenu.
""", "En C, les paramètres sont passés par valeur : la fonction travaille sur des copies. Pour modifier une variable de l'appelant, on passe son adresse (`&x`) et la fonction la manipule par un pointeur (`*a`).",
         """
1. Le programme affiche **3 8**. `echanger` reçoit des copies de `x` et de `y` ; l'échange est effectué sur ces copies, qui disparaissent à la fin de la fonction, et `x` et `y` ne sont pas modifiés.
2. En passant les adresses :

```c
void echanger(int *a, int *b) {
    int t = *a;
    *a = *b;
    *b = t;
}

/* dans main : */
echanger(&x, &y);
printf("%d %d", x, y);
```

La fonction modifie directement les variables de `main` : l'affichage est **8 3**.
""", None),
])

# ============================================================ boucle for
assert [i * 2 for i in range(1, 6)] == [2, 4, 6, 8, 10]
assert len(range(0, 10, 3)) == 4 and list(range(0, 10, 3)) == [0, 3, 6, 9]
assert list(range(10, 0, -2)) == [10, 8, 6, 4, 2]
i = 1; s = 0
while i <= 100:
    s += i; i += 1
assert s == 5050
assert sum(1 for i in range(1, 4) for j in range(1, 3)) == 6
assert puissance(2, 10) == 1024 and puissance(5, 0) == 1 and puissance(3, 4) == 81

T = "boucle for"
ecrire(T, [
    item(T, "FAIBLE", 0, """
Qu'affiche la boucle suivante ?

```c
for (int i = 1; i <= 5; i++)
    printf("%d ", i * 2);
```
""", "Une boucle `for (init; condition; pas)` initialise le compteur, teste la condition avant chaque tour et applique le pas après chaque tour ; la borne `<=` est incluse.",
         "Le compteur `i` prend les valeurs 1, 2, 3, 4, 5 (la borne 5 est incluse avec `<=`), et chaque tour affiche `i * 2` : **2 4 6 8 10**.",
         ["2 4 6 8", "2 4 6 8 10", "1 2 3 4 5", "2 4 6 8 10 12"], "B"),
    item(T, "FAIBLE", 1, """
Donner le nombre de tours (itérations) de chacune des deux boucles suivantes, en précisant les valeurs prises par `i` :

```c
for (i = 0; i < 10; i = i + 3) { ... }
for (i = 10; i > 0; i = i - 2) { ... }
```
""", "Pour compter les tours d'une boucle `for`, on liste les valeurs du compteur qui satisfont la condition, en partant de l'initialisation et en appliquant le pas jusqu'à ce que la condition devienne fausse.",
         "1. Première boucle : `i` vaut 0, 3, 6, 9 ; à `i = 12` la condition `i < 10` est fausse. Elle s'exécute **4 fois**.\n2. Seconde boucle : `i` vaut 10, 8, 6, 4, 2 ; à `i = 0` la condition `i > 0` est fausse. Elle s'exécute **5 fois**.",
         None),
    item(T, "MOYENNE", 2, """
Réécrire avec une boucle `for` le code suivant, puis donner la valeur finale de `s` :

```c
int i = 1, s = 0;
while (i <= 100) {
    s = s + i;
    i = i + 1;
}
```
""", "Une boucle `while` dont le compteur est initialisé avant la boucle, testé dans la condition et incrémenté à la fin du corps se réécrit en `for (init; condition; pas)` en regroupant ces trois éléments dans l'en-tête.",
         """
```c
int s = 0;
for (int i = 1; i <= 100; i++)
    s = s + i;
```

`s` est la somme des entiers de 1 à 100 : $\\dfrac{100 \\times 101}{2} = 5050$. La valeur finale de `s` est **5050**.
""", None),
    item(T, "MOYENNE", 3, """
Combien de caractères `*` le programme suivant affiche-t-il ?

```c
for (i = 1; i <= 3; i++)
    for (j = 1; j <= 2; j++)
        printf("*");
```
""", "Dans deux boucles imbriquées, la boucle interne s'exécute entièrement à chaque tour de la boucle externe : le nombre total d'exécutions du corps est le produit des nombres de tours.",
         "La boucle externe fait 3 tours et, à chaque tour, la boucle interne en fait 2 : le corps est exécuté $3 \\times 2 = 6$ fois et le programme affiche **6** étoiles.",
         ["5", "6", "3", "9"], "B"),
    item(T, "ELEVEE", 4, """
Écrire en C, avec une boucle `for` et sans utiliser la fonction `pow`, une fonction `int puissance(int x, int n)` qui retourne $x^n$ pour un entier $n \\geq 0$. Donner `puissance(2, 10)` et `puissance(5, 0)`, et expliquer pourquoi le cas `n = 0` est correctement traité.
""", "Une puissance se calcule par multiplications répétées : on initialise un accumulateur à 1 (élément neutre de la multiplication) et on le multiplie `n` fois par `x`.",
         """
```c
int puissance(int x, int n) {
    int r = 1;
    for (int i = 1; i <= n; i++)
        r = r * x;
    return r;
}
```

- `puissance(2, 10)` : 10 multiplications par 2 à partir de 1, résultat **1024**.
- `puissance(5, 0)` : la boucle ne s'exécute jamais (`1 <= 0` est faux), `r` garde sa valeur initiale : résultat **1**, ce qui est bien $5^0 = 1$.
""", None),
])

# ============================================================ boucle while
k = 20; exec_k = 0
while k > 5:
    k -= 4; exec_k += 1
assert (exec_k, k) == (4, 4)
n = 3; sortie = []
while n > 0:
    sortie.append(n); n -= 1
assert sortie == [3, 2, 1]
n = 4729; s = 0; trace = []
while n > 0:
    s += n % 10; n //= 10; trace.append((n, s))
assert trace == [(472, 9), (47, 11), (4, 18), (0, 22)]

T = "boucle while"
ecrire(T, [
    item(T, "FAIBLE", 0, """
Qu'affiche le programme suivant ?

```c
int n = 3;
while (n > 0) {
    printf("%d ", n);
    n--;
}
```
""", "Une boucle `while` teste sa condition **avant** chaque tour : le corps s'exécute tant que la condition est vraie, et on suit l'évolution de la variable testée.",
         "`n` vaut 3 : on affiche 3 puis `n` devient 2 ; on affiche 2 puis `n` devient 1 ; on affiche 1 puis `n` devient 0. La condition `n > 0` est alors fausse et la boucle s'arrête sans afficher 0. Le programme affiche **3 2 1**.",
         ["3 2 1", "3 2 1 0", "2 1 0", "0 1 2 3"], "A"),
    item(T, "FAIBLE", 1, """
Combien de fois le corps de la boucle suivante est-il exécuté, et quelle est la valeur finale de `k` ?

```c
int k = 20;
while (k > 5)
    k = k - 4;
```
""", "Pour compter les tours d'une boucle `while`, on suit la valeur de la variable testée : chaque fois que la condition est vraie, le corps s'exécute une fois de plus.",
         "`k` vaut successivement 20, 16, 12, 8 puis 4. Les tests `20 > 5`, `16 > 5`, `12 > 5` et `8 > 5` sont vrais : le corps est exécuté **4 fois**. Le test `4 > 5` est faux et la boucle s'arrête avec **k = 4**.",
         None),
    item(T, "MOYENNE", 2, """
On considère le programme suivant :

```c
int x = 10;
while (x < 5)
    printf("A");
do {
    printf("B");
} while (x < 5);
```

Qu'affiche-t-il ? Quelle différence de comportement cela illustre-t-il entre `while` et `do ... while` ?
""", "`while` teste la condition avant le premier tour (le corps peut ne jamais s'exécuter) ; `do ... while` exécute le corps une première fois avant de tester la condition (au moins un tour).",
         "Le programme affiche **B**. Avec `while (x < 5)`, la condition est fausse dès le départ (10 n'est pas inférieur à 5) : le corps n'est jamais exécuté et rien n'est affiché. Avec `do ... while`, le corps est exécuté une première fois (affichage de `B`) avant que la condition soit testée ; elle est fausse et la boucle s'arrête.",
         None),
    item(T, "MOYENNE", 3, """
Laquelle de ces boucles ne se termine jamais ?
""", "Une boucle `while` se termine si le corps modifie une variable de la condition de façon à la rendre fausse ; sans cette modification, la condition reste vraie indéfiniment.",
         "La boucle `int i = 0; while (i < 5) { printf(\"x\"); }` ne modifie jamais `i` : la condition `i < 5` reste toujours vraie et la boucle est infinie. Dans les trois autres, la variable testée est modifiée à chaque tour (`i++` ou `i--`) et la condition finit par devenir fausse.",
         ["int i = 0; while (i < 5) i++;", 'int i = 0; while (i < 5) { printf("x"); }', "int i = 5; while (i > 0) i--;", "int i = 1; while (i <= 3) i++;"], "B"),
    item(T, "ELEVEE", 4, """
Écrire en C une boucle `while` qui calcule la somme des chiffres d'un entier `n > 0` (par exemple 4729), en utilisant les opérateurs `%` et `/`. Présenter les valeurs de `n` et de `s` à la fin de chaque tour pour `n = 4729`, et donner le résultat.
""", "Le reste de la division par 10 (`n % 10`) donne le dernier chiffre de `n` et le quotient (`n / 10`) supprime ce chiffre ; on répète jusqu'à ce que `n` vaille 0.",
         """
```c
int s = 0;
while (n > 0) {
    s = s + n % 10;
    n = n / 10;
}
```

Trace pour `n = 4729` (valeurs en fin de tour) :

| Tour | s | n |
|------|---|---|
| 1 | 9 | 472 |
| 2 | 11 | 47 |
| 3 | 18 | 4 |
| 4 | 22 | 0 |

Quand `n` vaut 0 la condition est fausse. La somme des chiffres est **22** ($4 + 7 + 2 + 9$).
""", None),
])

# ============================================================ trace d'exécution
def trace_swap():
    a, b = 2, 5
    a = a + b
    b = a - b
    a = a - b
    return a, b


assert trace_swap() == (5, 2)
s = 0; tr = []
for i in range(1, 5):
    s += i * i; tr.append(s)
assert tr == [1, 5, 14, 30]
T_ = [3, 1, 4, 1, 5]
mx = T_[0]; chg = 0
for i in range(1, 5):
    if T_[i] > mx:
        mx = T_[i]; chg += 1
assert (mx, chg) == (5, 2)
n = 5; r = 1
while n > 1:
    r *= n; n -= 2
assert r == 15
appels = []


def f(n):
    appels.append(n)
    return 0 if n == 0 else n % 10 + f(n // 10)


assert f(345) == 12 and appels == [345, 34, 3, 0]

T = "trace d'exécution"
ecrire(T, [
    item(T, "FAIBLE", 0, """
On exécute la suite d'instructions suivante :

```c
int a = 2, b = 5;
a = a + b;
b = a - b;
a = a - b;
```

Quelles sont les valeurs de `a` et de `b` à la fin ?
""", "Pour faire la trace d'une suite d'affectations, on note la valeur de chaque variable après chaque instruction, dans l'ordre, en utilisant à chaque fois les valeurs **courantes**.",
         "Trace : au départ `a = 2`, `b = 5`. Après `a = a + b`, `a = 7`. Après `b = a - b`, `b = 7 - 5 = 2`. Après `a = a - b`, `a = 7 - 2 = 5`. Les valeurs finales sont **a = 5 et b = 2** : ces instructions échangent les deux variables sans variable auxiliaire.",
         ["a = 7 et b = 5", "a = 5 et b = 2", "a = 2 et b = 5", "a = 7 et b = 2"], "B"),
    item(T, "FAIBLE", 1, """
Faire la trace d'exécution du code suivant (valeurs de `i` et de `s` à chaque tour) et donner la valeur finale de `s` :

```c
int s = 0;
for (int i = 1; i <= 4; i++)
    s = s + i * i;
```
""", "Une trace d'exécution se présente sous forme de tableau : une ligne par tour de boucle, une colonne par variable, pour lire l'évolution des valeurs sans rien sauter.",
         """
| Tour | i | i × i | s |
|------|---|-------|---|
| 1 | 1 | 1 | 1 |
| 2 | 2 | 4 | 5 |
| 3 | 3 | 9 | 14 |
| 4 | 4 | 16 | 30 |

La valeur finale de `s` est **30**, somme des carrés des entiers de 1 à 4.
""", None),
    item(T, "MOYENNE", 2, """
On considère le tableau `T = [3, 1, 4, 1, 5]` (indices 0 à 4) et le code :

```c
int max = T[0];
for (int i = 1; i < 5; i++)
    if (T[i] > max)
        max = T[i];
```

Faire la trace d'exécution (valeur de `T[i]` et de `max` à chaque tour), donner la valeur finale de `max` et le nombre de fois où `max` est modifiée.
""", "Pour tracer un parcours de tableau, on note à chaque tour l'indice, l'élément lu, le résultat du test et la valeur de la variable modifiée éventuellement.",
         """
Au départ `max = 3`.

| i | T[i] | T[i] > max ? | max après |
|---|------|--------------|-----------|
| 1 | 1 | non | 3 |
| 2 | 4 | oui | 4 |
| 3 | 1 | non | 4 |
| 4 | 5 | oui | 5 |

La valeur finale de `max` est **5**, et `max` est modifiée **2 fois** (aux tours `i = 2` et `i = 4`).
""", None),
    item(T, "MOYENNE", 3, """
Quelle est la valeur de `r` à la fin de l'exécution du code suivant ?

```c
int n = 5, r = 1;
while (n > 1) {
    r = r * n;
    n = n - 2;
}
```
""", "On suit conjointement les variables modifiées par la boucle et on vérifie la condition avant chaque tour, y compris pour arrêter la boucle.",
         "Départ : `n = 5`, `r = 1`. Tour 1 (`5 > 1`) : `r = 5`, `n = 3`. Tour 2 (`3 > 1`) : `r = 15`, `n = 1`. Le test `1 > 1` est faux : la boucle s'arrête avec **r = 15**. La valeur 120 serait $5!$, mais le pas de la boucle est de 2 et non de 1.",
         ["120", "15", "5", "3"], "B"),
    item(T, "ELEVEE", 4, """
On considère la fonction récursive suivante :

```c
int f(int n) {
    if (n == 0) return 0;
    return n % 10 + f(n / 10);
}
```

Faire la trace de l'appel `f(345)` : indiquer la suite des appels (phase de descente), les valeurs retournées lors de la remontée, le nombre total d'appels et le résultat.
""", "La trace d'une fonction récursive se fait en deux phases : la descente (chaque appel déclenche le suivant jusqu'au cas de base), puis la remontée (chaque appel en attente calcule sa valeur dès que l'appel suivant lui répond, dans l'ordre inverse).",
         """
**Descente** : `f(345)` appelle `f(34)`, qui appelle `f(3)`, qui appelle `f(0)`, cas de base qui retourne 0. Il y a **4 appels** au total.

**Remontée** :

| Appel | Calcul | Valeur retournée |
|-------|--------|------------------|
| `f(0)` | cas de base | 0 |
| `f(3)` | 3 % 10 + f(0) = 3 + 0 | 3 |
| `f(34)` | 34 % 10 + f(3) = 4 + 3 | 7 |
| `f(345)` | 345 % 10 + f(34) = 5 + 7 | 12 |

Le résultat est **12**, somme des chiffres de 345.
""", None),
])
