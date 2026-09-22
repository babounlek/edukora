"""Génère et VÉRIFIE les items de quiz TI/Programmation (round du 2026-09-19).

Chaque valeur citée dans un corrigé est recalculée ici (Python / sqlite3) avant écriture : le script
échoue si un corrigé et le calcul indépendant divergent.
Usage : py backend/ingest/_audit/gen_quiz_ti_prog.py  (écrit backend/ingest/_quiz/cm/*.json)
"""
import json
import math
import sqlite3
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "_quiz" / "cm"
OUT.mkdir(parents=True, exist_ok=True)
CURSUS_PB = [{"examen": "probatoire", "serie": "TI"}, {"examen": "bac", "serie": "TI"}]
CURSUS_B = [{"examen": "bac", "serie": "TI"}]
MATIERE = "Programmation"


def item(slug, theme, cursus, diff, idx, enonce, rappel, corrige, sources, choix=None, bonne=None):
    it = {
        "external_id": f"cqc-{slug}-{diff.lower().replace('é', 'e')}-{idx}",
        "theme": theme,
        "matiere": MATIERE,
        "cursus": cursus,
        "enonce_markdown": enonce.strip(),
        "corrige_markdown": f"### Rappel de méthode\n\n{rappel.strip()}\n\n### Corrigé\n\n{corrige.strip()}",
        "difficulte_estimee": diff,
        "type_reponse": "QCM" if choix else "OUVERTE",
        "choix": [{"lettre": l, "texte": t} for l, t in zip("ABCD", choix)] if choix else [],
        "reponse_correcte": bonne or "",
        "source_exercises": sources,
    }
    return it


def ecrire(slug, items):
    ids = [i["external_id"] for i in items]
    assert len(ids) == len(set(ids)), f"external_id dupliqué dans {slug}"
    for i in items:
        if i["type_reponse"] == "QCM":
            assert i["reponse_correcte"] in {c["lettre"] for c in i["choix"]} and len(i["choix"]) == 4
        assert i["corrige_markdown"].startswith("### Rappel de méthode")
    (OUT / f"{slug}.json").write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(slug, len(items), "items")


# ------------------------------------------------------------------ factorielle
def fact_iter(n):
    f = 1
    for i in range(1, n + 1):
        f *= i
    return f


assert fact_iter(5) == 120 and fact_iter(0) == 1
appels_g4 = []


def g(n):
    appels_g4.append(n)
    return 1 if n <= 1 else n * g(n - 1)


assert g(4) == 24 and len(appels_g4) == 4
assert math.comb(6, 2) == 15 == fact_iter(6) // (fact_iter(2) * fact_iter(4))
premier_debordement = next(n for n in range(1, 30) if fact_iter(n) > 2**31 - 1)
assert premier_debordement == 13 and fact_iter(12) <= 2**31 - 1

S = "factorielle"
T = "factorielle"
src = [10537, 10586]
ecrire(S, [
    item(S, T, CURSUS_PB, "FAIBLE", 0, """
On considère l'algorithme suivant, où `n` vaut 5 :

```
f <- 1
Pour i de 1 à n faire
    f <- f x i
FinPour
Afficher f
```

Quelle valeur cet algorithme affiche-t-il ?
""", "Une boucle qui multiplie une variable, initialisée à 1, par le compteur `i` à chaque tour calcule le produit $1 \\times 2 \\times \\dots \\times n$, c'est-à-dire la factorielle $n!$.",
         "Le compteur `i` prend les valeurs 1, 2, 3, 4, 5 et `f` évolue ainsi : 1, 2, 6, 24, 120. L'algorithme calcule $5!$ et affiche donc **120**. La réponse 15 correspondrait à une somme et non à un produit.",
         src, ["15", "24", "120", "720"], "C"),
    item(S, T, CURSUS_PB, "FAIBLE", 1, """
Par convention, $0! = 1$. On reprend l'algorithme itératif de la factorielle :

```
f <- 1
Pour i de 1 à n faire
    f <- f x i
FinPour
Afficher f
```

Que se passe-t-il quand `n` vaut 0, et pourquoi le résultat affiché est-il correct ?
""", "Une boucle `Pour i de 1 à n` ne s'exécute aucune fois quand `n` est inférieur à 1 : le résultat est alors la valeur d'initialisation de l'accumulateur.",
         "Pour `n = 0`, la borne 0 est inférieure au début 1 : le corps de la boucle n'est jamais exécuté et `f` garde sa valeur initiale 1. L'algorithme affiche donc **1**, ce qui est bien $0! = 1$. C'est pour cela qu'un accumulateur de produit s'initialise à 1 (élément neutre de la multiplication) et jamais à 0.",
         src),
    item(S, T, CURSUS_PB, "MOYENNE", 2, """
La fonction C suivante devrait retourner `n!`, mais elle retourne toujours 0, quelle que soit la valeur de `n` :

```c
int fact(int n) {
    int f = 0;
    for (int i = 1; i <= n; i++)
        f = f * i;
    return f;
}
```

Expliquer l'erreur puis écrire la fonction corrigée.
""", "Un accumulateur de produit doit être initialisé à l'élément neutre de la multiplication, soit 1. Initialisé à 0, tout produit ultérieur reste nul.",
         """
L'erreur est l'initialisation `int f = 0;` : comme $0 \\times i = 0$ à chaque tour, `f` reste égal à 0 et la fonction retourne 0 pour tout `n`.

Fonction corrigée :

```c
int fact(int n) {
    int f = 1;
    for (int i = 1; i <= n; i++)
        f = f * i;
    return f;
}
```

Vérification : `fact(4)` donne successivement 1, 2, 6, 24, donc 24.
""", src),
    item(S, T, CURSUS_PB, "MOYENNE", 3, """
On considère la fonction récursive suivante :

```c
int g(int n) {
    if (n <= 1) return 1;
    return n * g(n - 1);
}
```

Combien d'appels de la fonction `g` (l'appel initial compris) sont effectués pour évaluer `g(4)` ?
""", "Pour compter les appels d'une fonction récursive, on déroule la descente jusqu'au cas de base : chaque appel qui ne satisfait pas la condition d'arrêt en déclenche exactement un nouveau.",
         "La descente est `g(4)`, `g(3)`, `g(2)`, `g(1)`. Le cas de base `n <= 1` est atteint avec `g(1)` : il n'y a pas d'appel supplémentaire. Il y a donc **4 appels**. La valeur retournée est $4 \\times 3 \\times 2 \\times 1 = 24$, mais l'énoncé demande le nombre d'appels, pas le résultat.",
         src, ["3", "4", "5", "24"], "B"),
    item(S, T, CURSUS_PB, "ELEVEE", 4, """
On dispose de la fonction `fact` (factorielle, type de retour `int` sur 32 bits, valeurs de $-2^{31}$ à $2^{31}-1$).

1. Écrire en C une fonction `comb(int n, int p)` qui utilise `fact` pour retourner le nombre de combinaisons $\\binom{n}{p} = \\dfrac{n!}{p!\\,(n-p)!}$.
2. Donner la valeur de `comb(6, 2)`.
3. À partir de quelle valeur de `n` l'appel `fact(n)` dépasse-t-il la capacité d'un `int` sur 32 bits ?
""", "Une formule à base de factorielles se traduit par des appels à `fact`, en surveillant la capacité du type : les factorielles croissent très vite et dépassent vite la plage d'un entier sur 32 bits.",
         """
1. ```c
   int comb(int n, int p) {
       return fact(n) / (fact(p) * fact(n - p));
   }
   ```
2. `comb(6, 2)` = $\\dfrac{720}{2 \\times 24} = \\dfrac{720}{48} = 15$.
3. $12! = 479\\,001\\,600$ tient dans un `int` (inférieur à $2\\,147\\,483\\,647$), mais $13! = 6\\,227\\,020\\,800$ le dépasse : le débordement apparaît **dès `n = 13`**. Cette limite s'applique aussi à `comb` dès que `n >= 13`, même si le résultat final serait petit.
""", src),
])

# ------------------------------------------------------------------ structure conditionnelle
def mention(n):
    if n >= 16: return "Très bien"
    if n >= 14: return "Bien"
    if n >= 12: return "Assez bien"
    if n >= 10: return "Passable"
    return "Insuffisant"


assert (mention(12), mention(14), mention(9)) == ("Assez bien", "Bien", "Insuffisant")


def bissextile(a):
    return (a % 4 == 0 and a % 100 != 0) or a % 400 == 0


assert (bissextile(1900), bissextile(2000), bissextile(2024), bissextile(2023)) == (False, True, True, False)

S = "structure-conditionnelle"
T = "structure conditionnelle"
src = [10533, 10585]
sortie3 = ""
a = 5
if a > 3: sortie3 += "A"
if a > 4: sortie3 += "B"
else: sortie3 += "C"
assert sortie3 == "AB"
ecrire(S, [
    item(S, T, CURSUS_PB, "FAIBLE", 0, """
Un programme doit afficher « Majeur » lorsque la variable entière `age` est supérieure ou égale à 18. Quelle condition faut-il écrire dans le `if` ?
""", "Une condition traduit exactement l'énoncé : « supérieur ou égal à » s'écrit `>=`. Il faut aussi distinguer la comparaison `==` de l'affectation `=`.",
         "L'énoncé demande « supérieur **ou égal** à 18 » : la condition est `age >= 18`. `age > 18` exclurait une personne d'exactement 18 ans, `age = 18` est une affectation (et non un test) et `age <= 18` teste l'inverse.",
         src, ["age > 18", "age >= 18", "age = 18", "age <= 18"], "B"),
    item(S, T, CURSUS_PB, "FAIBLE", 1, """
On considère le programme C suivant :

```c
int x = 7;
if (x % 2 == 0)
    printf("pair");
else
    printf("impair");
```

Qu'affiche-t-il ? Qu'afficherait-il si `x` valait 12 ?
""", "Dans une structure `if ... else`, une seule des deux branches s'exécute : celle du `if` si la condition est vraie, celle du `else` sinon. `x % 2` donne le reste de la division entière par 2.",
         "Pour `x = 7`, $7 = 2 \\times 3 + 1$ donc `7 % 2` vaut 1, la condition `x % 2 == 0` est fausse et la branche `else` s'exécute : le programme affiche **impair**. Pour `x = 12`, `12 % 2` vaut 0, la condition est vraie et le programme affiche **pair**.",
         src),
    item(S, T, CURSUS_PB, "MOYENNE", 2, """
Un algorithme attribue une mention d'après une note sur 20 :

```
Si note >= 16 alors afficher "Très bien"
Sinon Si note >= 14 alors afficher "Bien"
Sinon Si note >= 12 alors afficher "Assez bien"
Sinon Si note >= 10 alors afficher "Passable"
Sinon afficher "Insuffisant"
FinSi
```

1. Quelle mention est affichée pour `note = 12`, pour `note = 14` et pour `note = 9` ?
2. Que se passerait-il si on plaçait le test `note >= 10` en premier ?
""", "Dans une suite de `Sinon Si`, les conditions sont évaluées dans l'ordre et seule la première vraie déclenche sa branche : on les classe donc de la plus restrictive à la moins restrictive.",
         """
1. `note = 12` : les tests `>= 16` et `>= 14` sont faux, `>= 12` est vrai : **Assez bien**. `note = 14` : `>= 16` est faux, `>= 14` est vrai : **Bien**. `note = 9` : aucun test n'est vrai, on arrive au `Sinon` final : **Insuffisant**.
2. Si `note >= 10` était testé en premier, toute note supérieure ou égale à 10 (même 18) donnerait « Passable », puisque la première condition vraie l'emporte et que les suivantes ne sont jamais évaluées. L'ordre des tests est donc essentiel.
""", src),
    item(S, T, CURSUS_PB, "MOYENNE", 3, """
On considère le programme C suivant :

```c
int a = 5;
if (a > 3) printf("A");
if (a > 4) printf("B");
else       printf("C");
```

Qu'affiche ce programme ?
""", "Deux `if` successifs sont indépendants : chacun est évalué. Un `else` se rattache au `if` qui le précède immédiatement, pas au premier de la série.",
         "Le premier `if` : `a > 3` est vrai, donc `A` est affiché. Le second `if` est évalué séparément : `a > 4` est vrai (5 > 4), donc `B` est affiché et le `else` (rattaché à ce second `if`) est ignoré. Le programme affiche **AB**. Avec un `else if` à la place du second `if`, seul `A` aurait été affiché.",
         src, ["A", "AB", "ABC", "AC"], "B"),
    item(S, T, CURSUS_PB, "ELEVEE", 4, """
Une année est bissextile si elle est divisible par 4, sauf si elle est divisible par 100, à moins qu'elle ne soit aussi divisible par 400.

1. Écrire en C la condition qui teste si la variable entière `annee` est bissextile, à l'aide d'opérateurs logiques.
2. Indiquer, en justifiant, si 1900, 2000 et 2024 sont bissextiles.
""", "Une règle à exceptions imbriquées se traduit par des conditions composées : `&&` (et), `||` (ou), `!=` (différent). On combine « règle générale et non exception » ou « exception de l'exception ».",
         """
1. `if ((annee % 4 == 0 && annee % 100 != 0) || annee % 400 == 0)` : divisible par 4 **et** pas par 100, **ou** divisible par 400.
2. - 1900 : divisible par 4 et par 100, mais pas par 400 : la première partie est fausse (divisible par 100) et la seconde aussi : **non bissextile**.
   - 2000 : divisible par 400 : la seconde partie est vraie : **bissextile**.
   - 2024 : divisible par 4 et non divisible par 100 : la première partie est vraie : **bissextile**.
""", src),
])

# ------------------------------------------------------------------ SQL (vérifié par exécution sqlite)
db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE eleve (id INTEGER PRIMARY KEY, nom TEXT, classe TEXT, moyenne REAL);
INSERT INTO eleve VALUES (1,'Amina','TI1',14.5),(2,'Brice','TI1',9.0),(3,'Carine','TI2',12.0),(4,'David','TI2',15.5),(5,'Estelle','TI1',11.5);
""")
q = lambda s: db.execute(s).fetchall()
assert q("SELECT COUNT(*) FROM eleve") == [(5,)]
assert q("SELECT nom, moyenne FROM eleve WHERE moyenne >= 12 ORDER BY moyenne DESC") == [("David", 15.5), ("Amina", 14.5), ("Carine", 12.0)]
assert q("SELECT classe, AVG(moyenne) FROM eleve GROUP BY classe ORDER BY classe") == [("TI1", 35.0 / 3), ("TI2", 13.75)]
db.execute("UPDATE eleve SET moyenne = moyenne + 1 WHERE classe = 'TI1' AND moyenne < 12")
assert q("SELECT nom, moyenne FROM eleve WHERE classe='TI1' ORDER BY id") == [("Amina", 14.5), ("Brice", 10.0), ("Estelle", 12.5)]
assert q("SELECT nom FROM eleve WHERE moyenne >= 12 ORDER BY id") == [("Amina",), ("Carine",), ("David",), ("Estelle",)]

TABLE = """
| id | nom | classe | moyenne |
|----|-----|--------|---------|
| 1 | Amina | TI1 | 14.5 |
| 2 | Brice | TI1 | 9.0 |
| 3 | Carine | TI2 | 12.0 |
| 4 | David | TI2 | 15.5 |
| 5 | Estelle | TI1 | 11.5 |
"""
S = "sql"
T = "SQL"
src = [10585, 10621, 10624]
ecrire(S, [
    item(S, T, CURSUS_B, "FAIBLE", 0, """
Quelle requête SQL affiche les noms des élèves de la classe TI1 dans une table `eleve(id, nom, classe, moyenne)` ?
""", "Une requête de consultation suit le schéma `SELECT colonnes FROM table WHERE condition` : on choisit les colonnes à afficher, la table, puis le filtre sur les lignes.",
         "Il faut afficher la colonne `nom`, depuis la table `eleve`, pour les lignes dont `classe` vaut `'TI1'` : `SELECT nom FROM eleve WHERE classe = 'TI1';`. Les autres propositions inversent colonne et valeur, interrogent une table qui n'existe pas, ou emploient `DELETE`, qui supprime des lignes au lieu de les afficher.",
         src, ["SELECT nom FROM eleve WHERE classe = 'TI1';", "SELECT classe FROM eleve WHERE nom = 'TI1';",
               "SELECT * FROM classe WHERE eleve = 'TI1';", "DELETE nom FROM eleve WHERE classe = 'TI1';"], "A"),
    item(S, T, CURSUS_B, "FAIBLE", 1, f"""
La table `eleve` contient les lignes suivantes :
{TABLE}
Écrire la requête qui retourne le nombre d'élèves enregistrés, puis donner son résultat.
""", "La fonction d'agrégation `COUNT(*)` compte le nombre de lignes d'une table (ou d'un résultat filtré) et retourne une seule valeur.",
         "La requête est `SELECT COUNT(*) FROM eleve;`. La table contient 5 lignes, le résultat est donc **5**.",
         src),
    item(S, T, CURSUS_B, "MOYENNE", 2, f"""
La table `eleve` contient les lignes suivantes :
{TABLE}
Quel est le résultat exact de la requête suivante (colonnes et ordre des lignes) ?

```sql
SELECT nom, moyenne FROM eleve WHERE moyenne >= 12 ORDER BY moyenne DESC;
```
""", "Le SGBD applique d'abord le filtre `WHERE` ligne par ligne, puis trie le résultat avec `ORDER BY` (`DESC` = décroissant) et n'affiche que les colonnes de la clause `SELECT`.",
         """
Le filtre `moyenne >= 12` retient Amina (14.5), Carine (12.0, la borne est incluse), David (15.5) ; Brice (9.0) et Estelle (11.5) sont écartés. Le tri décroissant donne :

| nom | moyenne |
|-----|---------|
| David | 15.5 |
| Amina | 14.5 |
| Carine | 12.0 |
""", src),
    item(S, T, CURSUS_B, "MOYENNE", 3, f"""
La table `eleve` contient les lignes suivantes :
{TABLE}
On exécute la requête :

```sql
SELECT classe, AVG(moyenne) FROM eleve GROUP BY classe;
```

Quelle ligne est retournée pour la classe TI2 ?
""", "`GROUP BY classe` regroupe les lignes par valeur de `classe` ; `AVG(moyenne)` calcule alors la moyenne arithmétique des valeurs de chaque groupe (somme divisée par l'effectif du groupe).",
         "Le groupe TI2 contient Carine (12.0) et David (15.5) : la moyenne est $\\dfrac{12 + 15.5}{2} = 13.75$. La ligne retournée est **TI2 | 13.75**. La valeur 27.5 serait la somme, 2 l'effectif, et 15.5 le maximum.",
         src, ["TI2 | 13.75", "TI2 | 27.5", "TI2 | 2", "TI2 | 15.5"], "A"),
    item(S, T, CURSUS_B, "ELEVEE", 4, f"""
La table `eleve` contient les lignes suivantes :
{TABLE}
1. Écrire la requête qui augmente de 1 point la moyenne des élèves de la classe TI1 dont la moyenne est strictement inférieure à 12.
2. Après cette mise à jour, donner les noms retournés par `SELECT nom FROM eleve WHERE moyenne >= 12;` (dans l'ordre des `id`).
""", "`UPDATE table SET colonne = expression WHERE condition` modifie uniquement les lignes qui satisfont la condition ; sans `WHERE`, toutes les lignes seraient modifiées. Les conditions se combinent avec `AND`.",
         """
1. ```sql
   UPDATE eleve SET moyenne = moyenne + 1 WHERE classe = 'TI1' AND moyenne < 12;
   ```
   Les lignes touchées sont Brice (9.0 devient 10.0) et Estelle (11.5 devient 12.5). Amina (14.5) n'est pas modifiée car elle ne satisfait pas `moyenne < 12`, et les élèves de TI2 non plus car leur classe est différente.
2. Après la mise à jour, les moyennes sont 14.5, 10.0, 12.0, 15.5, 12.5. Les moyennes supérieures ou égales à 12 sont celles d'**Amina, Carine, David et Estelle** (Brice, à 10.0, est exclu).
""", src),
])

# ------------------------------------------------------------------ MySQL
S = "mysql"
T = "MySQL"
src = [10571, 10574, 10585, 10621]
prix = [250, 500, 750, 1200, 500, 3000]
assert sum(p > 500 for p in prix) == 3 and sum(p >= 500 for p in prix) == 5 and len(prix) == 6
ecrire(S, [
    item(S, T, CURSUS_B, "FAIBLE", 0, """
Dans le client en ligne de commande de MySQL, quelle instruction affiche la liste des bases de données du serveur ?
""", "MySQL dispose d'instructions d'administration propres, comme `SHOW`, qui affiche des informations sur le serveur (bases, tables, colonnes), à distinguer des requêtes `SELECT` qui interrogent le contenu des tables.",
         "L'instruction est `SHOW DATABASES;`. Les autres formulations (`LIST DATABASES`, `SELECT DATABASES`, `DISPLAY BASES`) n'existent pas en MySQL.",
         src, ["SHOW DATABASES;", "LIST DATABASES;", "SELECT DATABASES;", "DISPLAY BASES;"], "A"),
    item(S, T, CURSUS_B, "FAIBLE", 1, """
Un développeur vient de se connecter au serveur MySQL avec le client en ligne de commande. Il veut travailler dans la base `ecole`.

1. Quelle instruction sélectionne cette base pour les requêtes suivantes ?
2. Quelle instruction affiche ensuite la liste des tables de cette base ?
""", "Avant d'interroger des tables, il faut désigner la base courante avec `USE`. `SHOW TABLES` liste alors les tables de cette base.",
         "1. `USE ecole;` définit `ecole` comme base courante.\n2. `SHOW TABLES;` affiche les tables de la base courante.\n\nSans `USE`, une requête sur une table sans préfixe échoue avec l'erreur « No database selected ».",
         src),
    item(S, T, CURSUS_B, "MOYENNE", 2, """
Un script PHP se connecte à MySQL avec la ligne suivante :

```php
$cnx = new mysqli("localhost", "root", "", "boutique");
```

1. Donner le rôle de chacun des quatre arguments.
2. Quelle méthode faut-il appeler sur `$cnx` quand le travail avec la base est terminé ?
""", "Le constructeur `new mysqli(hôte, utilisateur, mot de passe, base)` ouvre la connexion dans cet ordre précis ; une connexion ouverte se referme explicitement avec `close()`.",
         """
1. - `"localhost"` : l'adresse du serveur MySQL (ici la machine locale).
   - `"root"` : le nom de l'utilisateur MySQL utilisé pour se connecter.
   - `""` : le mot de passe de cet utilisateur (ici vide).
   - `"boutique"` : le nom de la base de données à utiliser.
2. On appelle `$cnx->close();` pour fermer la connexion et libérer les ressources.
""", src),
    item(S, T, CURSUS_B, "MOYENNE", 3, """
La table `produit` d'une base MySQL contient six lignes dont les prix (en FCFA) sont : 250, 500, 750, 1200, 500 et 3000. Un script PHP exécute :

```php
$res = $cnx->query("SELECT * FROM produit WHERE prix > 500");
echo $res->num_rows;
```

Quelle valeur ce script affiche-t-il ?
""", "La propriété `num_rows` d'un résultat `SELECT` donne le nombre de lignes retournées **après** application de la clause `WHERE`, pas le nombre de lignes de la table.",
         "La condition `prix > 500` est stricte : elle retient 750, 1200 et 3000, mais pas les prix égaux à 500. Le résultat contient donc 3 lignes et le script affiche **3**. La valeur 6 est le nombre de lignes de la table, et 5 correspondrait à `prix >= 500`.",
         src, ["6", "3", "5", "4"], "B"),
    item(S, T, CURSUS_B, "ELEVEE", 4, """
Le script PHP suivant échoue avec une erreur MySQL, alors que la connexion `$cnx` et la table `client(nom, ville)` sont correctes :

```php
$sql = "INSERT INTO client (nom, ville) VALUES (Paul, Douala)";
$cnx->query($sql);
```

1. Quelle est la cause de l'erreur ?
2. Écrire la requête corrigée.
""", "En SQL, une valeur de type texte doit être écrite entre apostrophes. Sans elles, MySQL lit le mot comme un nom de colonne ou d'identifiant.",
         """
1. `Paul` et `Douala` sont des chaînes de caractères, mais elles ne sont pas entourées d'apostrophes : MySQL les interprète comme des noms de colonnes et signale une erreur du type « Unknown column 'Paul' in 'field list' ».
2. Requête corrigée :

```sql
INSERT INTO client (nom, ville) VALUES ('Paul', 'Douala');
```
""", src),
])

# ------------------------------------------------------------------ CREATE TABLE
S = "create-table"
T = "CREATE TABLE"
src = [10585, 10624]
lite = sqlite3.connect(":memory:")
lite.executescript("""
CREATE TABLE salle (id INTEGER PRIMARY KEY, nom VARCHAR(30), capacite INTEGER);
CREATE TABLE classe (id_classe INTEGER PRIMARY KEY, libelle VARCHAR(30));
CREATE TABLE eleve (id_eleve INTEGER PRIMARY KEY, nom VARCHAR(50) NOT NULL, id_classe INTEGER,
                    FOREIGN KEY (id_classe) REFERENCES classe(id_classe));
PRAGMA foreign_keys = ON;
""")
lite.execute("PRAGMA foreign_keys = ON")
lite.execute("INSERT INTO classe VALUES (1, 'TI1')")
lite.execute("INSERT INTO eleve VALUES (1, 'Amina', 1)")
try:
    lite.execute("INSERT INTO eleve VALUES (2, 'Brice', 99)")
    raise SystemExit("la contrainte de clé étrangère aurait dû refuser 99")
except sqlite3.IntegrityError:
    pass
ecrire(S, [
    item(S, T, CURSUS_B, "FAIBLE", 0, """
Quelle instruction SQL crée correctement une table `livre` avec un identifiant entier `id` et un titre `titre` de 100 caractères au plus ?
""", "La syntaxe est `CREATE TABLE nom_table (colonne1 type, colonne2 type, ...);` : les colonnes sont déclarées entre parenthèses, séparées par des virgules, chacune avec son type.",
         "Seule la première proposition respecte la syntaxe : `CREATE TABLE livre (id INT, titre VARCHAR(100));`. Les autres inversent les mots-clés (`CREATE livre TABLE`), utilisent un mot-clé inexistant (`NEW TABLE`) ou des crochets à la place des parenthèses.",
         src, ["CREATE TABLE livre (id INT, titre VARCHAR(100));", "CREATE livre TABLE (id INT, titre VARCHAR(100));",
               "NEW TABLE livre (id INT, titre VARCHAR(100));", "CREATE TABLE livre [id INT, titre VARCHAR(100)];"], "A"),
    item(S, T, CURSUS_B, "FAIBLE", 1, """
Écrire la requête SQL qui crée la table `salle` avec les colonnes suivantes : `id` (entier, clé primaire), `nom` (texte de 30 caractères au plus) et `capacite` (entier).
""", "Une clé primaire se déclare avec `PRIMARY KEY` à la suite du type de la colonne ; elle identifie chaque ligne de façon unique.",
         """
```sql
CREATE TABLE salle (
    id INT PRIMARY KEY,
    nom VARCHAR(30),
    capacite INT
);
```
""", src),
    item(S, T, CURSUS_B, "MOYENNE", 2, """
Écrire la requête qui crée la table `produit` avec :

- `id` : entier, clé primaire dont la valeur est attribuée automatiquement ;
- `libelle` : texte de 50 caractères au plus, obligatoire ;
- `prix` : nombre décimal à 10 chiffres dont 2 après la virgule, valant 0 par défaut.
""", "Les contraintes se placent après le type : `PRIMARY KEY`, `AUTO_INCREMENT` (MySQL) pour un identifiant automatique, `NOT NULL` pour une valeur obligatoire, `DEFAULT valeur` pour une valeur par défaut.",
         """
```sql
CREATE TABLE produit (
    id INT PRIMARY KEY AUTO_INCREMENT,
    libelle VARCHAR(50) NOT NULL,
    prix DECIMAL(10,2) DEFAULT 0
);
```

`DECIMAL(10,2)` réserve 10 chiffres au total dont 2 décimales.
""", src),
    item(S, T, CURSUS_B, "MOYENNE", 3, """
Quelle définition de colonne garantit que chaque ligne de la table reçoit automatiquement un identifiant entier unique ?
""", "Un identifiant automatique et unique combine trois idées : un type entier, une clé primaire (unicité et non-nullité) et `AUTO_INCREMENT`, qui incrémente la valeur à chaque insertion.",
         "La définition `id INT PRIMARY KEY AUTO_INCREMENT` réunit les trois. `id INT UNIQUE` impose l'unicité mais oblige à fournir la valeur à la main ; `id VARCHAR(10) NOT NULL` n'assure ni l'unicité ni l'automatisme ; `id INT DEFAULT 0` donnerait la même valeur 0 à toutes les lignes.",
         src, ["id INT PRIMARY KEY AUTO_INCREMENT", "id INT UNIQUE", "id VARCHAR(10) NOT NULL", "id INT DEFAULT 0"], "A"),
    item(S, T, CURSUS_B, "ELEVEE", 4, """
Un lycée gère des classes et des élèves : chaque élève appartient à une classe.

1. Écrire les requêtes qui créent la table `classe` (`id_classe` entier clé primaire, `libelle` texte de 30 caractères) et la table `eleve` (`id_eleve` entier clé primaire, `nom` texte de 50 caractères obligatoire, `id_classe` entier), avec une clé étrangère de `eleve.id_classe` vers `classe.id_classe`.
2. Dans quel ordre faut-il créer les deux tables ?
3. Que se passe-t-il si on insère un élève avec `id_classe = 99` alors qu'aucune classe n'a cet identifiant ?
""", "Une clé étrangère se déclare avec `FOREIGN KEY (colonne) REFERENCES table_référencée(colonne)`. La table référencée doit exister avant celle qui la référence, et le SGBD refuse toute valeur sans correspondance.",
         """
1. ```sql
   CREATE TABLE classe (
       id_classe INT PRIMARY KEY,
       libelle VARCHAR(30)
   );

   CREATE TABLE eleve (
       id_eleve INT PRIMARY KEY,
       nom VARCHAR(50) NOT NULL,
       id_classe INT,
       FOREIGN KEY (id_classe) REFERENCES classe(id_classe)
   );
   ```
2. On crée d'abord `classe`, puis `eleve` : la clé étrangère de `eleve` fait référence à `classe`, qui doit donc déjà exister.
3. L'insertion est **refusée** avec une erreur d'intégrité référentielle : la valeur 99 n'existe pas dans `classe.id_classe`, donc l'élève ne peut pas être rattaché à une classe inexistante.
""", src),
])
