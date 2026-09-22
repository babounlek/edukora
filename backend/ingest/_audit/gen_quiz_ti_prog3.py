"""Troisième passe de quiz TI/Programmation (2026-09-19) : JavaScript, HTML, Spécificateurs de format,
Architecture client-serveur, structure de données. Chaque valeur d'un corrigé est recalculée avant
écriture (node pour le JavaScript, Python pour les formats C et les algorithmes, html.parser pour le
HTML) ; le script échoue si un corrigé et le calcul indépendant divergent.
Usage : py backend/ingest/_audit/gen_quiz_ti_prog3.py
"""
import json
import subprocess
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "_quiz"
OUT = ROOT / "cm"
REQ = {r["competence"]: r for r in json.loads((ROOT / "_batch_cm_prog3_all.json").read_text(encoding="utf-8"))}
MATIERE = "Programmation"


def slugify(theme):
    return "-".join("".join(c if c.isalnum() else " " for c in theme.lower().replace("é", "e")).split())


def item(theme, diff, idx, enonce, rappel, corrige, choix=None, bonne=None):
    r = REQ[theme]
    return {
        "external_id": f"cqc-{slugify(theme)}-{diff.lower().replace('é', 'e')}-{idx}",
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
    (OUT / f"{slugify(theme)}.json").write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(theme, len(items), "items ->", slugify(theme))


def node(code):
    r = subprocess.run(["node", "-e", code], capture_output=True, text=True, encoding="utf-8", check=True)
    return r.stdout.strip()


class Equilibre(HTMLParser):
    VOID = {"input", "br", "meta", "img", "hr"}

    def __init__(self):
        super().__init__()
        self.pile, self.ok = [], True

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.pile.append(tag)

    def handle_endtag(self, tag):
        if not self.pile or self.pile.pop() != tag:
            self.ok = False


def html_equilibre(code):
    p = Equilibre()
    p.feed(code)
    return p.ok and not p.pile


# ============================================================ JavaScript (vérifié avec node)
assert node('var a="4", b="6"; console.log(a + b, Number(a) + Number(b))') == "46 10"
assert node("function somme(n){var s=0;for(var i=1;i<=n;i++){s+=i;}return s;} console.log(somme(4), somme(10), (function(n){var s=0;for(var i=1;i<n;i++){s+=i;}return s;})(4))") == "10 55 6"
assert node("var n=0; do { n = n + 3; } while (n < 10); console.log(n)") == "12"
saisies = ["abc", "25", "-3", "14"]
prompts = 0
note = None
while True:
    v = saisies[prompts]; prompts += 1
    note = node(f'console.log(Number({json.dumps(v)}))')
    invalide = node(f'var note=Number({json.dumps(v)}); console.log(isNaN(note) || note < 0 || note > 20)') == "true"
    if not invalide:
        break
assert (prompts, note) == (4, "14")
# avec && : "abc" est accepté à tort (NaN)
assert node('var note=Number("abc"); console.log(isNaN(note) && note < 0 && note > 20)') == "false"
assert node('var note=Number("abc"); console.log(isNaN(note) && (note < 0 || note > 20))') == "false"

T = "JavaScript"
ecrire(T, [
    item(T, "FAIBLE", 0, """
Quelle balise HTML permet d'insérer du code JavaScript dans une page web ?
""", "Le code JavaScript s'intègre à une page HTML dans une balise dédiée, ouverte et refermée, qui indique au navigateur qu'il doit interpréter son contenu comme un script.",
         "La balise est `<script> ... </script>`. Elle peut contenir le code directement ou pointer vers un fichier externe avec l'attribut `src`. Les balises `<js>`, `<javascript>` et `<code>` n'existent pas pour cet usage (`<code>` sert seulement à afficher du code).",
         ["<js>", "<script>", "<javascript>", "<code>"], "B"),
    item(T, "FAIBLE", 1, """
Dans une page web, `a = prompt("Premier nombre ?")` et `b = prompt("Second nombre ?")` reçoivent les saisies 4 et 6.

Que valent `a + b` et `Number(a) + Number(b)` ? Expliquer la différence.
""", "La fonction `prompt` retourne toujours une chaîne de caractères. L'opérateur `+` concatène deux chaînes ; pour additionner des nombres, il faut d'abord convertir les valeurs (`Number`, `parseInt`, `parseFloat`).",
         "`a` et `b` sont les chaînes `\"4\"` et `\"6\"`. `a + b` les **concatène** et donne la chaîne `\"46\"`. `Number(a) + Number(b)` convertit d'abord en nombres puis additionne : **10**.",
         None),
    item(T, "MOYENNE", 2, """
On considère la fonction JavaScript suivante :

```js
function somme(n) {
    var s = 0;
    for (var i = 1; i <= n; i++) {
        s += i;
    }
    return s;
}
```

1. Donner les valeurs retournées par `somme(4)` et `somme(10)`.
2. Quelle valeur retournerait `somme(4)` si la condition de la boucle était `i < n` ?
""", "Pour simuler une fonction, on suit la valeur de l'accumulateur à chaque tour ; une borne `<=` inclut la valeur limite, une borne `<` l'exclut.",
         """
1. `somme(4)` = 1 + 2 + 3 + 4 = **10** ; `somme(10)` = 1 + 2 + ... + 10 = **55**.
2. Avec `i < n`, le dernier tour est `i = 3` : `somme(4)` = 1 + 2 + 3 = **6**. La valeur `n` n'est plus ajoutée.
""", None),
    item(T, "MOYENNE", 3, """
Quelle valeur ce script affiche-t-il ?

```js
var n = 0;
do {
    n = n + 3;
} while (n < 10);
document.write(n);
```
""", "Dans une boucle `do ... while`, le corps s'exécute avant le test : la condition décide seulement si l'on recommence. On suit la valeur de la variable tour par tour.",
         "`n` vaut successivement 3, 6, 9 puis 12. Après 9, la condition `9 < 10` est vraie donc on recommence ; après 12, `12 < 10` est fausse et la boucle s'arrête. Le script affiche **12** (et non 10 : `n` ne prend jamais cette valeur).",
         ["9", "10", "12", "15"], "C"),
    item(T, "ELEVEE", 4, """
Pour valider une note, un script JavaScript répète la question tant que la saisie est incorrecte :

```js
var note;
do {
    note = Number(prompt("Note sur 20 ?"));
} while (isNaN(note) || note < 0 || note > 20);
```

1. L'utilisateur saisit successivement `abc`, `25`, `-3`, puis `14`. Combien de fois `prompt` est-il appelé et quelle est la valeur finale de `note` ?
2. Que se passerait-il si on remplaçait les `||` par des `&&` ? Justifier avec la saisie `abc`.
""", "Une condition de validation est vraie quand la saisie est **incorrecte** : `||` (ou) regroupe les différents cas d'erreur, un seul suffit à rejeter la saisie. Avec `&&`, il faudrait que tous les cas d'erreur soient réunis en même temps.",
         """
1. `abc` : `Number("abc")` vaut `NaN`, `isNaN` est vrai, on recommence. `25` : supérieur à 20, on recommence. `-3` : inférieur à 0, on recommence. `14` : aucune condition d'erreur n'est vraie, la boucle s'arrête. `prompt` est appelé **4 fois** et `note` vaut **14**.
2. Avec `&&`, la condition devient `isNaN(note) && note < 0 && note > 20`. Pour `abc`, `note` vaut `NaN` : `isNaN(note)` est vrai mais `NaN < 0` est faux, donc l'ensemble est faux et la boucle s'arrête : la saisie `abc` serait **acceptée à tort**. De toute façon, une note ne peut pas être à la fois négative et supérieure à 20 : la condition ne pourrait jamais être vraie.
""", None),
])

# ============================================================ HTML
TABLE1 = """<table>
  <tr><th>Nom</th><th>Classe</th><th>Moyenne</th></tr>
  <tr><td>Amina</td><td>TI1</td><td>14.5</td></tr>
</table>"""
FORM4 = """<form action="enregistrer.php" method="post">
  <table>
    <tr><td>Nom</td><td><input type="text" name="nom"></td></tr>
    <tr><td>Email</td><td><input type="email" name="email"></td></tr>
    <tr><td>Message</td><td><textarea name="message"></textarea></td></tr>
  </table>
  <input type="submit" value="Envoyer">
</form>"""
assert html_equilibre(TABLE1) and html_equilibre(FORM4)
assert FORM4.count("<tr>") == 3 and FORM4.count("<td>") == 6 and 'method="post"' in FORM4 and 'action="enregistrer.php"' in FORM4

T = "HTML"
ecrire(T, [
    item(T, "FAIBLE", 0, """
Quelle balise HTML permet de créer un lien hypertexte vers une autre page ?
""", "Un lien hypertexte se crée avec la balise d'ancre `<a>`, dont l'attribut `href` contient l'adresse de destination.",
         "La balise est `<a href=\"adresse\">texte du lien</a>`. `<link>` sert à relier une feuille de style dans l'en-tête, et `<href>` et `<url>` ne sont pas des balises : `href` est un attribut.",
         ["<a>", "<link>", "<href>", "<url>"], "A"),
    item(T, "FAIBLE", 1, """
Écrire le code HTML d'un tableau de deux lignes et trois colonnes : la première ligne contient les en-têtes « Nom », « Classe » et « Moyenne », la seconde les valeurs « Amina », « TI1 » et « 14.5 ».
""", "Un tableau HTML s'écrit avec `<table>` ; chaque ligne est un `<tr>`, chaque cellule d'en-tête un `<th>` et chaque cellule de données un `<td>`. Toute balise ouverte doit être refermée.",
         f"```html\n{TABLE1}\n```\n\nLa première ligne utilise `<th>` (cellules d'en-tête, en gras et centrées par défaut), la seconde `<td>` (cellules de données). Chaque ligne contient bien trois cellules.",
         None),
    item(T, "MOYENNE", 2, """
1. Écrire la balise HTML d'un champ de saisie destiné à un mot de passe (les caractères tapés sont masqués), nommé `mdp`.
2. Écrire la balise d'un bouton qui envoie le formulaire, avec le texte « Envoyer ».
3. Pourquoi l'attribut `name` du champ est-il indispensable pour le traitement du formulaire ?
""", "Les champs d'un formulaire se créent avec `<input>` : l'attribut `type` choisit le comportement (texte, mot de passe, bouton d'envoi...) et l'attribut `name` sert d'identifiant à la donnée envoyée.",
         """
1. `<input type="password" name="mdp">` : la valeur `password` masque les caractères saisis.
2. `<input type="submit" value="Envoyer">`.
3. À l'envoi, le navigateur transmet des couples « nom = valeur » : le script qui reçoit le formulaire retrouve chaque donnée grâce au `name` du champ. Un champ sans `name` n'est pas envoyé.
""", None),
    item(T, "MOYENNE", 3, """
Que provoque l'attribut `colspan="2"` dans la cellule suivante ?

```html
<td colspan="2">Total</td>
```
""", "Les attributs `colspan` et `rowspan` fusionnent des cellules : `colspan` étend une cellule sur plusieurs **colonnes**, `rowspan` sur plusieurs **lignes**.",
         "`colspan=\"2\"` fait occuper à la cellule la largeur de **deux colonnes** : la cellule est fusionnée horizontalement avec sa voisine. La fusion de deux lignes serait obtenue avec `rowspan=\"2\"`.",
         ["Elle occupe la largeur de deux colonnes", "Elle occupe la hauteur de deux lignes", "Elle ajoute deux colonnes au tableau", "Elle donne à la cellule une largeur de 2 pixels"], "A"),
    item(T, "ELEVEE", 4, """
Écrire le code HTML d'un formulaire composé de trois champs : le nom (texte), l'email (adresse électronique) et un message (zone de texte multiligne), suivis d'un bouton « Envoyer ». Les champs sont organisés dans un tableau de trois lignes et deux colonnes (libellé à gauche, champ à droite). Les données sont envoyées par la méthode POST au fichier `enregistrer.php`.
""", "Un formulaire s'écrit avec `<form action=\"cible\" method=\"post\">` ; on y place les champs (`<input>`, `<textarea>`), chacun avec un `name`. Pour aligner libellés et champs, on les répartit dans les cellules d'un tableau qui est **à l'intérieur** du formulaire.",
         f"```html\n{FORM4}\n```\n\nPoints à vérifier : `action` désigne le script récepteur, `method=\"post\"` indique la méthode, chaque champ a un `name`, et le tableau compte bien 3 lignes de 2 cellules. Le bouton d'envoi est dans le formulaire, hors du tableau.",
         None),
])

# ============================================================ Spécificateurs de format
assert "%d %c %f" % (65, "A", 2.5) == "65 A 2.500000"
assert ("%.2f" % 3.14159, "%5d" % 42, "%05d" % 42) == ("3.14", "   42", "00042")
assert (7 // 2, "%f" % (7 / 2), "%.1f" % (7 / 2), int(3.9)) == (3, "3.500000", "3.5", 3)

T = "Spécificateurs de format"
ecrire(T, [
    item(T, "FAIBLE", 0, """
Quel spécificateur de format permet d'afficher un nombre réel (type `float`) avec `printf` ?
""", "Le spécificateur de format indique le type de la valeur à afficher : `%d` pour un entier, `%f` pour un réel, `%c` pour un caractère, `%s` pour une chaîne.",
         "Un `float` s'affiche avec **`%f`**. `%d` est réservé aux entiers, `%c` aux caractères isolés et `%s` aux chaînes de caractères.",
         ["%d", "%f", "%c", "%s"], "B"),
    item(T, "FAIBLE", 1, """
Qu'affiche l'instruction suivante ?

```c
printf("%d %c %f", 65, 'A', 2.5);
```
""", "Chaque spécificateur de la chaîne de format est remplacé, dans l'ordre, par la valeur correspondante ; `%f` affiche par défaut 6 chiffres après la virgule.",
         "`%d` affiche l'entier 65, `%c` le caractère `A`, et `%f` le réel 2.5 avec six décimales. Le programme affiche **65 A 2.500000**.",
         None),
    item(T, "MOYENNE", 2, """
Donner l'affichage produit par chacune des trois instructions suivantes (les barres verticales, non affichées, indiquent seulement les limites du résultat) :

```c
printf("|%.2f|", 3.14159);
printf("|%5d|", 42);
printf("|%05d|", 42);
```
""", "Entre `%` et la lettre, on peut préciser une largeur (`%5d` : 5 caractères, alignés à droite), un nombre de décimales (`%.2f`) et un remplissage par des zéros (`%05d`).",
         "- `%.2f` limite l'affichage à deux décimales (arrondi) : **|3.14|**.\n- `%5d` réserve 5 caractères et aligne à droite : trois espaces puis 42, soit **|   42|**.\n- `%05d` réserve 5 caractères et complète avec des zéros : **|00042|**.",
         None),
    item(T, "MOYENNE", 3, """
Quelle instruction lit correctement un nombre réel saisi au clavier dans la variable `float x;` ?
""", "Avec `scanf`, le spécificateur doit correspondre au type de la variable (`%f` pour un `float`) et la variable doit être passée par son adresse avec `&`.",
         "L'instruction correcte est `scanf(\"%f\", &x);`. `scanf(\"%d\", &x)` interprète la saisie comme un entier (mauvais type), `scanf(\"%f\", x)` oublie l'opérateur `&` (l'adresse est nécessaire), et `%c` ne lit qu'un caractère.",
         ['scanf("%f", &x);', 'scanf("%d", &x);', 'scanf("%f", x);', 'scanf("%c", &x);'], "A"),
    item(T, "ELEVEE", 4, """
On considère le programme C suivant :

```c
#include <stdio.h>

int main() {
    int a = 7, b = 2;
    printf("%d\\n", a / b);
    printf("%f\\n", (float) a / b);
    printf("%.1f\\n", (float) a / b);
    printf("%d\\n", (int) 3.9);
    return 0;
}
```

1. Donner l'affichage complet du programme, ligne par ligne.
2. Expliquer pourquoi les deux premières lignes sont différentes alors qu'elles concernent les mêmes variables.
""", "En C, le type des opérandes détermine la nature de la division : entière si les deux sont entiers, réelle si l'un est converti en `float` (opérateur de conversion `(float)`). Le spécificateur doit ensuite correspondre au type de la valeur affichée.",
         """
1. Affichage :

```
3
3.500000
3.5
3
```

2. Dans la première ligne, `a / b` est une division **entière** (7 divisé par 2 donne 3, reste 1). Dans la deuxième, `(float) a` convertit `a` en réel avant la division : `7.0 / 2` donne 3.5, affiché avec `%f` (six décimales). La troisième utilise `%.1f` pour une seule décimale. La conversion `(int) 3.9` tronque la partie décimale sans arrondir : le résultat est 3.
""", None),
])

# ============================================================ Architecture client-serveur
T = "client-serveur"
ecrire(T, [
    item(T, "FAIBLE", 0, """
Dans l'architecture client-serveur du Web, quel élément envoie la requête HTTP lorsqu'on consulte une page ?
""", "Dans le modèle client-serveur, le **client** émet une requête et le **serveur** y répond. Sur le Web, le client est généralement le navigateur de l'utilisateur.",
         "C'est le **navigateur** (le client) qui envoie la requête HTTP vers le serveur web. Le serveur web, le SGBD et l'interpréteur PHP se trouvent du côté serveur et ne font que répondre ou traiter.",
         ["Le navigateur", "Le serveur web", "Le SGBD", "L'interpréteur PHP"], "A"),
    item(T, "FAIBLE", 1, """
Définir les termes « client » et « serveur » dans le cadre de la consultation d'une page web, et donner un exemple de chacun.
""", "Un client demande un service, un serveur le fournit : les deux sont des programmes (ou des machines) qui communiquent en suivant un protocole, ici HTTP.",
         "Le **client** est le programme qui demande une page : par exemple un navigateur (Firefox, Chrome). Le **serveur** est le programme, installé sur une machine connectée en permanence, qui reçoit la requête et renvoie la page : par exemple le serveur web Apache.",
         None),
    item(T, "MOYENNE", 2, """
Un navigateur demande une page `index.php` à un serveur qui exécute du PHP.

1. Que reçoit exactement le navigateur en réponse ?
2. Un internaute qui affiche le code source de la page peut-il voir le code PHP ? Justifier.
""", "PHP est un langage exécuté côté **serveur** : l'interpréteur transforme le script en une page HTML avant l'envoi, alors que JavaScript est exécuté côté client par le navigateur.",
         "1. Le navigateur reçoit uniquement le **résultat** de l'exécution du script, c'est-à-dire une page HTML (éventuellement accompagnée de CSS et de JavaScript).\n2. Non : le code PHP est exécuté par le serveur puis remplacé par sa sortie ; il n'est jamais transmis. L'internaute ne voit dans le code source que du HTML.",
         None),
    item(T, "MOYENNE", 3, """
Quelle suite décrit correctement les échanges lors de l'affichage d'une page dynamique qui lit des données dans une base MySQL ?
""", "Une page dynamique suit un aller-retour : la requête part du navigateur vers le serveur web, qui confie le script à l'interpréteur ; celui-ci interroge la base, puis la page HTML construite remonte jusqu'au navigateur.",
         "La suite correcte est : navigateur → serveur web → interpréteur PHP → MySQL, puis MySQL → PHP (données) → serveur web (page HTML) → navigateur. Les autres propositions inversent l'ordre ou font dialoguer directement le navigateur avec la base, ce que l'architecture client-serveur ne permet pas.",
         ["Navigateur, serveur web, PHP, MySQL, puis retour par PHP, serveur web et navigateur", "Navigateur, MySQL, PHP, serveur web",
          "Serveur web, navigateur, PHP, MySQL", "Navigateur, PHP, navigateur, MySQL"], "A"),
    item(T, "ELEVEE", 4, """
Pour chacune des tâches suivantes d'une application web de commande de produits, indiquer si elle s'exécute côté client ou côté serveur :

a) vérifier qu'un champ n'est pas vide avant l'envoi du formulaire (script JavaScript) ;
b) lire la liste des produits dans la base MySQL ;
c) afficher une boîte de dialogue d'alerte avec `alert()` ;
d) enregistrer la commande dans la base ;
e) mettre en forme la page avec une feuille de style CSS.

Expliquer ensuite pourquoi la vérification (a) ne dispense pas de contrôler la saisie côté serveur.
""", "Le code exécuté par le navigateur (HTML, CSS, JavaScript) est côté client ; ce qui accède aux données (PHP, SQL, base MySQL) est côté serveur. Tout ce qui vient du client peut être modifié ou contourné : le serveur doit donc revérifier.",
         """
- a) **client** (JavaScript exécuté par le navigateur) ;
- b) **serveur** (le script PHP interroge MySQL) ;
- c) **client** (`alert()` est une fonction JavaScript du navigateur) ;
- d) **serveur** (l'écriture dans la base passe par PHP et MySQL) ;
- e) **client** (le navigateur applique les règles CSS).

La vérification (a) peut être contournée : l'utilisateur peut désactiver JavaScript ou envoyer directement une requête HTTP sans passer par la page. Elle sert uniquement au confort (réponse immédiate). La sécurité et la cohérence des données exigent une revérification côté serveur avant tout enregistrement.
""", None),
])

# ============================================================ structure de données
T_ = [12, 7, 9, 15, 4]
assert (T_[0], T_[4], len(T_) - 1, T_[1] + T_[3]) == (12, 4, 4, 22)
assert 3 + 4 == 7
T2 = [12, 7, 9, 15, 4, 8]
mn, idx, comp = T2[0], 0, 0
for i in range(1, len(T2)):
    comp += 1
    if T2[i] < mn:
        mn, idx = T2[i], i
assert (mn, idx, comp) == (4, 4, 5)

T = "structure de données"
ecrire(T, [
    item(T, "FAIBLE", 0, """
Parmi les propositions suivantes, laquelle est une structure de données (type non primitif) ?
""", "Un type primitif contient une seule valeur (entier, réel, caractère) ; une structure de données regroupe plusieurs valeurs sous un même nom (tableau, enregistrement, liste...).",
         "Le **tableau** est une structure de données : il regroupe plusieurs valeurs d'un même type sous un seul nom. `int`, `char` et `float` sont des types primitifs : chacun ne contient qu'une seule valeur.",
         ["int", "Un tableau", "char", "float"], "B"),
    item(T, "FAIBLE", 1, """
On considère les déclarations C suivantes :

```c
int notes[5];

struct eleve {
    char nom[30];
    int age;
    float moyenne;
};
```

Laquelle de ces deux déclarations est un tableau et laquelle est un enregistrement (structure) ? Donner la différence essentielle.
""", "Un tableau regroupe des éléments de **même type**, accessibles par leur indice ; un enregistrement (`struct`) regroupe des champs de **types éventuellement différents**, accessibles par leur nom.",
         "`int notes[5];` est un **tableau** : cinq entiers, du même type, accessibles par indice de 0 à 4. `struct eleve` est un **enregistrement** : il regroupe un nom (chaîne), un âge (entier) et une moyenne (réel), de types différents, accessibles par leur nom (`e.age`, `e.moyenne`).",
         None),
    item(T, "MOYENNE", 2, """
On considère le tableau `int T[5] = {12, 7, 9, 15, 4};`

1. Que valent `T[0]`, `T[4]` et `T[1] + T[3]` ?
2. Quel est l'indice du dernier élément ? Que se passe-t-il si on lit `T[5]` ?
""", "Les indices d'un tableau C commencent à 0 : un tableau de n éléments a des indices de 0 à n - 1. Accéder à un indice en dehors de cette plage est une erreur.",
         "1. `T[0]` = **12**, `T[4]` = **4** et `T[1] + T[3]` = 7 + 15 = **22**.\n2. Le dernier indice est **4** (le tableau a 5 éléments, indices 0 à 4). Lire `T[5]` dépasse les limites du tableau : le compilateur C ne l'interdit pas, mais on lit une zone mémoire qui n'appartient pas au tableau (comportement indéfini, valeur imprévisible ou plantage).",
         None),
    item(T, "MOYENNE", 3, """
Qu'affiche le programme suivant ?

```c
struct point { int x; int y; };

int main() {
    struct point p = {3, 4};
    printf("%d", p.x + p.y);
    return 0;
}
```
""", "On accède à un champ d'une variable de type `struct` avec l'opérateur point : `variable.champ`. L'opérateur `+` additionne ici deux entiers.",
         "`p.x` vaut 3 et `p.y` vaut 4 : `p.x + p.y` est l'addition des deux entiers, soit **7**. La valeur 34 serait une concaténation, qui n'existe pas pour des entiers, et 12 un produit.",
         ["34", "7", "12", "3"], "B"),
    item(T, "ELEVEE", 4, """
Écrire une fonction C `int indice_min(int T[], int n)` qui retourne l'indice du plus petit élément d'un tableau `T` de `n` éléments. Faire la trace pour `T = {12, 7, 9, 15, 4, 8}` (`n = 6`) : donner l'indice retourné, la valeur minimale et le nombre de comparaisons effectuées.
""", "Pour chercher un minimum, on retient l'indice du meilleur élément vu jusque-là (initialisé à 0), puis on parcourt les autres éléments en le mettant à jour chaque fois qu'un élément plus petit apparaît.",
         """
```c
int indice_min(int T[], int n) {
    int imin = 0;
    for (int i = 1; i < n; i++)
        if (T[i] < T[imin])
            imin = i;
    return imin;
}
```

Trace pour `T = {12, 7, 9, 15, 4, 8}` : `imin` vaut 0 ; à `i = 1`, 7 < 12 donc `imin = 1` ; `i = 2` (9) et `i = 3` (15) ne changent rien ; à `i = 4`, 4 < 7 donc `imin = 4` ; `i = 5` (8) ne change rien.

La fonction retourne l'indice **4**, la valeur minimale est **4**, et il y a **5 comparaisons** (`n - 1`, une par élément à partir de l'indice 1).
""", None),
])
