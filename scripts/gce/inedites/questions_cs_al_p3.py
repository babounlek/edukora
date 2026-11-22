r"""Les 7 exercices de l'epreuve inedite GCE A Level Computer Science Paper 3 n.1 (100 marks, 2 h, tout obligatoire).

Structure mesuree sur les Paper 3 de 2025 et 2026 (7 taches : conception de base de donnees, SQL, trace d'algorithme, pseudocode, programme C,
jeu d'essai ; 2 a 4 sous-questions par tache) ; aucune donnee, aucun scenario ni aucun nom repris d'un sujet reel : la base de donnees est celle
d'une compagnie de bus (Savannah Express), le programme celui d'un releve de pluies a des stations du mont Cameroun.
Les donnees « du jour » des vrais sujets n'existent pas dans le PDF : tout est ecrit dans l'enonce (tableaux, code donne, jeux d'essai).
Chaque sous-question : bareme exact (`pts`), grille `crit` (somme = pts), rappel (un paragraphe general), resolution, reponse.
TOUT le code du corrige est execute par verifier_reponses_cs_al_p3.py : SQL sur sqlite3, C compile avec gcc (docker alpine, -ansi -pedantic
-Wall -Wextra), pseudocode traduit en Python par un mini-transpileur. Les sorties imprimees dans le corrige sont comparees aux sorties reelles.
Convention des blocs du corrige : ```sql (requete ; le tableau Markdown qui suit est le resultat attendu), ```c (code), ```text (sortie d'un
programme, ou schema), ```pseudo (pseudocode). Chaines BRUTES. Numeros affiches : lettres a, b, c (un numero unique par exercice).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_addmaths_p2_a import E, S  # noqa: E402,F401

G = ""  # pas de groupes : paper plat (le blueprint n'en porte pas)


def P(*parts):
    """Paragraphes separes par une ligne vide."""
    return "\n\n".join(parts)


def T(entetes, lignes):
    """Tableau Markdown."""
    out = ["| " + " | ".join(entetes) + " |", "|" + "---|" * len(entetes)]
    for l in lignes:
        out.append("| " + " | ".join(str(c) for c in l) + " |")
    return "\n".join(out)


# ------------------------------------------------------------------------------------------------ donnees de la base Savannah Express
PASSENGER = [("P01", "Ngwa Divine", "677100201"), ("P02", "Fotso Carine", "699340552"), ("P03", "Tabi Michael", "670228911"),
             ("P04", "Mbarga Sandrine", "655731420"), ("P05", "Akum Lilian", "677884300"), ("P06", "Kamga Rodrigue", "699015678"),
             ("P07", "Eyenga Blaise", "655902734")]
ROUTE = [("R1", "Buea", "Douala", 2500), ("R2", "Douala", "Yaounde", 4500), ("R3", "Bamenda", "Bafoussam", 3000),
         ("R4", "Yaounde", "Bertoua", 5000), ("R5", "Douala", "Limbe", 2000)]
TRIP = [("T101", "R1", "2026-03-02"), ("T102", "R2", "2026-03-02"), ("T103", "R1", "2026-03-03"), ("T104", "R3", "2026-03-04"),
        ("T105", "R2", "2026-03-05"), ("T106", "R4", "2026-03-05"), ("T107", "R1", "2026-03-06"), ("T108", "R5", "2026-03-07")]
BOOKING = [("P01", "T101", 3), ("P02", "T101", 4), ("P03", "T101", 7), ("P01", "T107", 2), ("P04", "T102", 1), ("P05", "T104", 5),
           ("P06", "T102", 6), ("P02", "T105", 2), ("P04", "T105", 3), ("P06", "T106", 1), ("P03", "T103", 9), ("P05", "T108", 4)]


def tables_base():
    """Les quatre tableaux de donnees, chacun precede de son nom en gras (le verificateur les relit dans l'enonce)."""
    return P("**Passenger**\n\n" + T(["PassengerID", "FullName", "Phone"], PASSENGER),
             "**Route**\n\n" + T(["RouteCode", "Origin", "Destination", "Fare"], ROUTE),
             "**Trip**\n\n" + T(["TripCode", "RouteCode", "DepartureDate"], TRIP),
             "**Booking**\n\n" + T(["PassengerID", "TripCode", "SeatNo"], BOOKING))


DDL_TROIS_TABLES = r"""```sql
CREATE TABLE Passenger (
    PassengerID VARCHAR(4) PRIMARY KEY,
    FullName    VARCHAR(40) NOT NULL,
    Phone       VARCHAR(12)
);
CREATE TABLE Route (
    RouteCode   VARCHAR(4) PRIMARY KEY,
    Origin      VARCHAR(20) NOT NULL,
    Destination VARCHAR(20) NOT NULL,
    Fare        INT NOT NULL
);
CREATE TABLE Trip (
    TripCode      VARCHAR(5) PRIMARY KEY,
    RouteCode     VARCHAR(4) NOT NULL REFERENCES Route(RouteCode),
    DepartureDate DATE NOT NULL
);
```"""

R_LIGNES = [("P01", "Ngwa Divine", "677100201", "T101", "2026-03-02", "R1", "Buea", "Douala", 2500, 3),
            ("P02", "Fotso Carine", "699340552", "T101", "2026-03-02", "R1", "Buea", "Douala", 2500, 4),
            ("P01", "Ngwa Divine", "677100201", "T107", "2026-03-06", "R1", "Buea", "Douala", 2500, 2),
            ("P04", "Mbarga Sandrine", "655731420", "T102", "2026-03-02", "R2", "Douala", "Yaounde", 4500, 1),
            ("P04", "Mbarga Sandrine", "655731420", "T105", "2026-03-05", "R2", "Douala", "Yaounde", 4500, 3),
            ("P05", "Akum Lilian", "677884300", "T104", "2026-03-04", "R3", "Bamenda", "Bafoussam", 3000, 5)]
R_ENTETES = ["PassengerID", "FullName", "Phone", "TripCode", "DepartureDate", "RouteCode", "Origin", "Destination", "Fare", "SeatNo"]

# ------------------------------------------------------------------------------------------------ code C donne (exercice 6) et sorties
C_DONNE = r"""```c
#include <stdio.h>

#define STATIONS 4
#define MONTHS 6

const char *station_name[STATIONS] = {"Debundscha", "Idenau", "Buea", "Tiko"};
const char *month_name[MONTHS] = {"Jan", "Feb", "Mar", "Apr", "May", "Jun"};

int rain[STATIONS][MONTHS] = {
    {310, 280, 405, 520, 690, 840},
    {120,  95, 210, 340, 480, 610},
    { 40,  55, 130, 210, 290, 350},
    { 25,  18,  90, 160, 240, 310}
};
```"""

C_STATION_TOTAL = r"""int station_total(int r[][MONTHS], int s)
{
    int m, total = 0;

    for (m = 0; m < MONTHS; m++)
        total += r[s][m];
    return total;
}"""

C_WETTEST = r"""int wettest_month(int r[][MONTHS], int s)
{
    int m, best = 0;

    for (m = 1; m < MONTHS; m++)
        if (r[s][m] > r[s][best])
            best = m;
    return best;
}"""

C_ABOVE = r"""int stations_above(int r[][MONTHS], int m, int limit)
{
    int s, count = 0;

    for (s = 0; s < STATIONS; s++)
        if (r[s][m] > limit)
            count++;
    return count;
}"""

C_REPORT = r"""void print_report(int r[][MONTHS])
{
    int s, m, month_sum, grand = 0;

    printf("%-12s", "Station");
    for (m = 0; m < MONTHS; m++)
        printf("%5s", month_name[m]);
    printf("%7s\n", "Total");

    for (s = 0; s < STATIONS; s++)
    {
        printf("%-12s", station_name[s]);
        for (m = 0; m < MONTHS; m++)
            printf("%5d", r[s][m]);
        printf("%7d\n", station_total(r, s));
    }

    printf("%-12s", "All stations");
    for (m = 0; m < MONTHS; m++)
    {
        month_sum = 0;
        for (s = 0; s < STATIONS; s++)
            month_sum += r[s][m];
        printf("%5d", month_sum);
        grand += month_sum;
    }
    printf("%7d\n", grand);
}"""

SORTIE_REPORT = r"""Station       Jan  Feb  Mar  Apr  May  Jun  Total
Debundscha    310  280  405  520  690  840   3045
Idenau        120   95  210  340  480  610   1855
Buea           40   55  130  210  290  350   1075
Tiko           25   18   90  160  240  310    843
All stations  495  448  835 1230 1700 2110   6818"""

C_READ = r"""int read_in_range(const char *prompt, int low, int high)
{
    int value;

    do
    {
        printf("%s", prompt);
        scanf("%d", &value);
        if (value < low || value > high)
            printf("Invalid: enter a number from %d to %d.\n", low, high);
    } while (value < low || value > high);
    return value;
}"""

C_MAIN = r"""int main(void)
{
    int s, m, limit, best;

    print_report(rain);
    printf("\n");
    s = read_in_range("Enter a station number (1-4): ", 1, STATIONS) - 1;
    best = wettest_month(rain, s);
    printf("%s: total %d mm, wettest month %s (%d mm)\n",
           station_name[s], station_total(rain, s), month_name[best], rain[s][best]);
    m = read_in_range("Enter a month number (1-6): ", 1, MONTHS) - 1;
    printf("Enter a rainfall limit in mm: ");
    scanf("%d", &limit);
    printf("Stations above %d mm in %s: %d\n", limit, month_name[m], stations_above(rain, m, limit));
    return 0;
}"""

SORTIE_MAIN = SORTIE_REPORT + "\n\n" + r"""Enter a station number (1-4): Invalid: enter a number from 1 to 4.
Enter a station number (1-4): Invalid: enter a number from 1 to 4.
Enter a station number (1-4): Buea: total 1075 mm, wettest month Jun (350 mm)
Enter a month number (1-6): Enter a rainfall limit in mm: Stations above 100 mm in Mar: 3"""

C_FAUTIF = r"""int wettest_month(int r[][MONTHS], int s)
{
    int m, best = 0;

    for (m = 1; m < MONTHS; m++)
        if (r[s][m] >= r[s][best])
            best = m;
    return best;
}"""

SORTIE_7A = r"""limit 100: 3
limit 130: 2
limit 1000: 0"""

SORTIE_7B = r"""faulty: 2
corrected: 1"""


def exercices():
    ex = []

    # ---- Exercice 1 : database design (10) ----
    ex.append(E("1", G, 10, P(
        r"**Question 1: Database design.** Savannah Express is a bus company that runs trips between towns of Cameroon. The seats booked during the first week of March 2026 were first recorded in a single relation **R**. A part of **R** is shown below.",
        T(R_ENTETES, R_LIGNES),
        "The following facts are true for all the data of the company:\n\n"
        "- a passenger has one identifier, one name and one phone number;\n"
        "- a trip has one departure date and runs on exactly one route; a route has one origin, one destination and one fare, and several trips can run on the same route;\n"
        "- a passenger can book several trips, but only one seat on a given trip, and two passengers never hold the same seat on the same trip."), [
        S("a", P(r"(i) State, with a reason, the highest normal form that the relation **R** satisfies. *[2 marks]*",
                 r"(ii) Name one partial dependency and one transitive dependency found in **R**. *[2 marks]*"),
          ["database normalisation", "keys and relationships"], "faible", 4,
          [(r"You say that **R** is in first normal form (every value is atomic and the key is (PassengerID, TripCode))", 1),
           (r"You give the reason why it is not in second normal form: some non-key attributes depend on only a part of the composite key", 1),
           (r"You name a partial dependency, for example PassengerID determines FullName and Phone, or TripCode determines DepartureDate and RouteCode", 1),
           (r"You name the transitive dependency: RouteCode, which is not a key of **R**, determines Origin, Destination and Fare", 1)],
          r"A relation is in first normal form when every attribute holds a single value and the relation has a key; it is in second normal form when, in addition, no non-key attribute depends on only a part of a composite key, and in third normal form when no non-key attribute depends on another non-key attribute.",
          P(r"(i) Every value of **R** is atomic and the pair (PassengerID, TripCode) identifies each row, so **R** is in first normal form. It is not in second normal form, because non-key attributes depend on only a part of that key: FullName and Phone depend on PassengerID alone, and DepartureDate and RouteCode depend on TripCode alone.",
            r"(ii) A partial dependency: PassengerID determines FullName and Phone (or TripCode determines DepartureDate and RouteCode). A transitive dependency: TripCode determines RouteCode, and RouteCode, which is not a key of **R**, determines Origin, Destination and Fare."),
          ans=r"**R** is in first normal form only",
          piege=r"SeatNo depends on the whole key (a passenger holds one seat on a given trip), so it is not a partial dependency; the repeated passenger and route data are the sign of the partial and transitive dependencies."),
        S("b", r"Normalise the relation **R** to third normal form. Write each relation as `Name(attribute, attribute, ...)` and write (PK) after each attribute of a primary key and (FK) after each foreign key. *[3 marks]*",
          ["database normalisation"], "moyenne", 3,
          [(r"You create `Passenger(PassengerID (PK), FullName, Phone)` for the passenger data", 1),
           (r"You create `Route(RouteCode (PK), Origin, Destination, Fare)` and `Trip(TripCode (PK), DepartureDate, RouteCode (FK))`, which removes the transitive dependency", 1),
           (r"You create `Booking(PassengerID (PK)(FK), TripCode (PK)(FK), SeatNo)` with the original composite key", 1)],
          r"To normalise a relation, group the attributes by the attribute that determines them, make that determinant the primary key of a new relation, and keep it as a foreign key in any relation that needs to refer to it, while the composite key of the original relation remains the key of the relation that links the others.",
          P(r"Each determinant becomes the key of its own relation: PassengerID fixes FullName and Phone, RouteCode fixes Origin, Destination and Fare, and TripCode fixes DepartureDate and RouteCode. SeatNo depends on the whole key (PassengerID, TripCode), so it stays with the link relation.",
            "```text\nPassenger(PassengerID (PK), FullName, Phone)\nRoute(RouteCode (PK), Origin, Destination, Fare)\nTrip(TripCode (PK), DepartureDate, RouteCode (FK))\nBooking(PassengerID (PK)(FK), TripCode (PK)(FK), SeatNo)\n```"),
          conseil=r"RouteCode appears twice, as a primary key in `Route` and as a foreign key in `Trip`: that repetition is the link between the two relations."),
        S("c", P(r"The entity-relationship diagram of the normalised database is drawn below as text. Each relationship is read from left to right and from right to left, and the symbols (a) to (f) stand for the cardinality at the end of each line: **1** (one) or **M** (many).",
                 "```text\nPassenger  (a)----------- makes -----------(b)  Booking\nBooking    (c)---------- is for -----------(d)  Trip\nTrip       (e)--------- runs on -----------(f)  Route\n```",
                 r"Write the value, 1 or M, of each of the symbols (a) to (f). *[3 marks]*"),
          ["entity relationship modelling", "keys and relationships"], "faible", 3,
          [(r"You give (a) = 1 and (b) = M: one passenger makes many bookings", 1), (r"You give (c) = M and (d) = 1: many bookings are for one trip", 1),
           (r"You give (e) = M and (f) = 1: many trips run on one route", 1)],
          r"In a relationship between two entities, the cardinality at an end tells how many rows of that entity can be linked to one row of the other entity, and in the relational model the foreign key is stored in the table that is on the many side.",
          P(r"A passenger can have several bookings, but each booking belongs to one passenger: (a) = 1 and (b) = M. A trip can have many bookings (one per seat), but each booking is for one trip: (c) = M and (d) = 1. A route can be used by many trips, but each trip runs on one route: (e) = M and (f) = 1.",
            "```text\nPassenger  (1)----------- makes -----------(M)  Booking\nBooking    (M)---------- is for -----------(1)  Trip\nTrip       (M)--------- runs on -----------(1)  Route\n```",
            r"The many-to-many link between passengers and trips is resolved by the entity Booking, whose primary key is made of the two foreign keys."),
          ans=r"(a) 1, (b) M, (c) M, (d) 1, (e) M, (f) 1"),
    ]))

    # ---- Exercice 2 : SQL queries (12) ----
    ex.append(E("2", G, 12, P(
        r"**Question 2: SQL queries.** In this question and in Question 3, write standard SQL statements for the Savannah Express database of Question 1 (any relational database management system can be used). Three tables have already been created with these statements:",
        DDL_TROIS_TABLES,
        r"The four tables hold the rows printed below. The table **Booking** is created in part (a) and then filled with the rows shown.",
        tables_base()), [
        S("a", r"Write the SQL statement that creates the table `Booking` with these properties: the columns `PassengerID` and `TripCode` have the same types as the columns they refer to and `SeatNo` is a whole number; the primary key is made of `PassengerID` and `TripCode`; `PassengerID` and `TripCode` are foreign keys; `SeatNo` is always between 1 and 70, because a bus has 70 seats; two passengers never hold the same seat on the same trip. *[4 marks]*",
          ["relational databases", "sql queries"], "faible", 4,
          [(r"You declare `PassengerID VARCHAR(4)`, `TripCode VARCHAR(5)` and `SeatNo INT` as NOT NULL", 1),
           (r"You declare the composite primary key `PRIMARY KEY (PassengerID, TripCode)`", 1),
           (r"You declare the two foreign keys with `REFERENCES Passenger(PassengerID)` and `REFERENCES Trip(TripCode)`", 1),
           (r"You limit the seat number with `CHECK (SeatNo BETWEEN 1 AND 70)` and forbid a repeated seat with `UNIQUE (TripCode, SeatNo)`", 1)],
          r"A CREATE TABLE statement lists each column with its data type and constraints, then the constraints of the table: PRIMARY KEY for the key (a composite key is listed in brackets), REFERENCES or FOREIGN KEY for each link to another table, CHECK for a range of valid values and UNIQUE for a combination of values that must never repeat.",
          P(r"The two key columns copy the types of the columns they refer to. The pair (PassengerID, TripCode) is the primary key, each column of the pair is also a foreign key, the range of the seat number is a CHECK and the rule on seats is a UNIQUE constraint on the pair (TripCode, SeatNo), because the same seat number may exist on different trips.",
            "```sql\nCREATE TABLE Booking (\n    PassengerID VARCHAR(4) NOT NULL REFERENCES Passenger(PassengerID),\n    TripCode    VARCHAR(5) NOT NULL REFERENCES Trip(TripCode),\n    SeatNo      INT NOT NULL CHECK (SeatNo BETWEEN 1 AND 70),\n    PRIMARY KEY (PassengerID, TripCode),\n    UNIQUE (TripCode, SeatNo)\n);\n```"),
          piege=r"A UNIQUE constraint on `SeatNo` alone would forbid two different buses from having a seat 3: the seat is unique only inside one trip."),
        S("b", P(r"Write the SQL statements that carry out the following changes of the database, and give the new `Fare` of each route that changes.",
                 r"(i) Add a new passenger: P08, Tchinda Aurelie, phone 650441287.",
                 r"(ii) Raise by 300 FCFA the fare of every route whose origin is Douala.",
                 r"(iii) The booking of passenger P06 on trip T106 is cancelled: delete it. *[4 marks]*"),
          ["sql queries"], "faible", 4,
          [(r"You write an INSERT INTO Passenger statement with the three values in the order of the columns", 1),
           (r"You write `UPDATE Route SET Fare = Fare + 300`", 1),
           (r"You restrict the update with `WHERE Origin = 'Douala'` and give the new fares: R2 4800 and R5 2300", 1),
           (r"You write a DELETE FROM Booking statement with both conditions, `PassengerID = 'P06' AND TripCode = 'T106'`", 1)],
          r"INSERT INTO adds a complete row, UPDATE with SET changes the columns of the rows chosen by WHERE, and DELETE FROM removes the rows chosen by WHERE; an UPDATE or a DELETE without WHERE acts on every row of the table.",
          P(r"The three statements are:",
            "```sql\nINSERT INTO Passenger VALUES ('P08', 'Tchinda Aurelie', '650441287');\nUPDATE Route SET Fare = Fare + 300 WHERE Origin = 'Douala';\nDELETE FROM Booking WHERE PassengerID = 'P06' AND TripCode = 'T106';\n```",
            r"Only the routes R2 (Douala to Yaounde) and R5 (Douala to Limbe) start in Douala, so their fares become 4800 and 2300 FCFA. The query `SELECT * FROM Route;` then gives:",
            "```sql\nSELECT * FROM Route;\n```\n\n" + T(["RouteCode", "Origin", "Destination", "Fare"],
                                                       [("R1", "Buea", "Douala", 2500), ("R2", "Douala", "Yaounde", 4800), ("R3", "Bamenda", "Bafoussam", 3000),
                                                        ("R4", "Yaounde", "Bertoua", 5000), ("R5", "Douala", "Limbe", 2300)])),
          ans=r"R2 = 4800 FCFA and R5 = 2300 FCFA",
          piege=r"Without the WHERE clause, the UPDATE would raise the fare of all five routes, and the DELETE would remove every booking."),
        S("c", r"Write a query that gives the `FullName` and the `SeatNo` of every passenger booked on trip T101, in ascending order of `SeatNo`. Write the result of the query. *[4 marks]*",
          ["sql queries", "relational databases"], "faible", 4,
          [(r"You select `FullName` and `SeatNo`", 1), (r"You join `Passenger` and `Booking` with the condition `Passenger.PassengerID = Booking.PassengerID`", 1),
           (r"You keep only the trip with `WHERE Booking.TripCode = 'T101'`", 1), (r"You sort with `ORDER BY SeatNo`, and the result has three rows: seats 3, 4 and 7", 1)],
          r"A join links two tables by a condition that equates the key of one with the foreign key of the other; the WHERE clause then keeps the wanted rows and ORDER BY sorts the result in ascending order unless DESC is added.",
          P(r"The name is in `Passenger` and the seat is in `Booking`, so the two tables are joined on `PassengerID`:",
            "```sql\nSELECT Passenger.FullName, Booking.SeatNo\nFROM Passenger JOIN Booking ON Passenger.PassengerID = Booking.PassengerID\nWHERE Booking.TripCode = 'T101'\nORDER BY Booking.SeatNo;\n```\n\n"
            + T(["FullName", "SeatNo"], [("Ngwa Divine", 3), ("Fotso Carine", 4), ("Tabi Michael", 7)])),
          ans=r"three rows: Ngwa Divine (3), Fotso Carine (4), Tabi Michael (7)"),
    ]))

    # ---- Exercice 3 : advanced SQL queries (16) ----
    ex.append(E("3", G, 16, P(
        r"**Question 3: Advanced SQL queries.** Use the Savannah Express database as it was at the start of Question 2, with the tables printed below (the changes of Question 2 part (b) are not made).",
        tables_base()), [
        S("a", r"Write one query that lists, for every booking on a trip that leaves on or after 5 March 2026, the `FullName` of the passenger, the `Origin` and the `Destination` of the route and the `DepartureDate`. Sort the result by `DepartureDate`, and then by `FullName`. Write the result of the query. *[5 marks]*",
          ["sql queries"], "moyenne", 5,
          [(r"You select FullName, Origin, Destination and DepartureDate, naming the table when the column is ambiguous", 1),
           (r"You join `Booking` to `Passenger` with `PassengerID`", 1),
           (r"You join `Booking` to `Trip` with `TripCode` and `Trip` to `Route` with `RouteCode`", 1),
           (r"You filter with `WHERE DepartureDate >= '2026-03-05'`", 1),
           (r"You sort with `ORDER BY DepartureDate, FullName`, and the result has five rows", 1)],
          r"When the data comes from several tables, each table is joined to the next through the key and the foreign key that link them; a column name that exists in two tables is written with the name of its table, then WHERE filters the rows and ORDER BY sorts on several columns in turn.",
          P(r"The passenger name is in `Passenger`, the date is in `Trip` and the towns are in `Route`, so the chain is Booking, Passenger, Trip, Route:",
            "```sql\nSELECT Passenger.FullName, Route.Origin, Route.Destination, Trip.DepartureDate\nFROM Booking\nJOIN Passenger ON Booking.PassengerID = Passenger.PassengerID\nJOIN Trip ON Booking.TripCode = Trip.TripCode\nJOIN Route ON Trip.RouteCode = Route.RouteCode\nWHERE Trip.DepartureDate >= '2026-03-05'\nORDER BY Trip.DepartureDate, Passenger.FullName;\n```\n\n"
            + T(["FullName", "Origin", "Destination", "DepartureDate"],
                [("Fotso Carine", "Douala", "Yaounde", "2026-03-05"), ("Kamga Rodrigue", "Yaounde", "Bertoua", "2026-03-05"),
                 ("Mbarga Sandrine", "Douala", "Yaounde", "2026-03-05"), ("Ngwa Divine", "Buea", "Douala", "2026-03-06"),
                 ("Akum Lilian", "Douala", "Limbe", "2026-03-07")])),
          ans=r"five rows, the first three on 2026-03-05"),
        S("b", r"Each booking pays the `Fare` of the route of its trip. Write one query that gives, for each route, its `RouteCode`, the number of bookings and the total of the fares paid. Name the two calculated columns `Bookings` and `Revenue`. Keep only the routes that have at least two bookings, and put the route with the highest `Revenue` first. Write the result of the query. *[6 marks]*",
          ["sql queries"], "elevee", 6,
          [(r"You join `Booking`, `Trip` and `Route` so that each booking carries the fare of its route", 1),
           (r"You calculate `COUNT(*) AS Bookings` and `SUM(Route.Fare) AS Revenue`", 2),
           (r"You group the rows with `GROUP BY Route.RouteCode`", 1), (r"You keep the groups of two bookings or more with `HAVING COUNT(*) >= 2`", 1),
           (r"You sort with `ORDER BY Revenue DESC`, and the result is R2 (4 bookings, 18000) then R1 (5 bookings, 12500)", 1)],
          r"GROUP BY forms one group of rows for each value of the grouping column, the aggregate functions COUNT and SUM are then calculated for each group, and HAVING keeps or rejects whole groups after the calculation, whereas WHERE filters single rows before it.",
          P(r"The fare is stored once in `Route`, so each booking must be joined to its trip and to the route of that trip before the rows are grouped by route. A condition on a count cannot be written in WHERE, because the count exists only after the grouping: it goes in HAVING.",
            "```sql\nSELECT Route.RouteCode, COUNT(*) AS Bookings, SUM(Route.Fare) AS Revenue\nFROM Booking\nJOIN Trip ON Booking.TripCode = Trip.TripCode\nJOIN Route ON Trip.RouteCode = Route.RouteCode\nGROUP BY Route.RouteCode\nHAVING COUNT(*) >= 2\nORDER BY Revenue DESC;\n```\n\n"
            + T(["RouteCode", "Bookings", "Revenue"], [("R2", 4, 18000), ("R1", 5, 12500)]),
            r"R1 has five bookings of 2500 FCFA ($5\times2500=12500$), R2 has four bookings of 4500 FCFA ($4\times4500=18000$), and R3, R4 and R5 have only one booking each, so they are removed by HAVING."),
          ans=r"R2 first with 18000 FCFA, then R1 with 12500 FCFA",
          piege=r"`WHERE COUNT(*) >= 2` is a syntax error: an aggregate function cannot be used in WHERE."),
        S("c", P(r"(i) Write a query that gives the `FullName` of every passenger who has no booking. Write the result. *[3 marks]*",
                 r"(ii) A clerk runs `INSERT INTO Booking VALUES ('P07', 'T999', 10);` where T999 is not the code of any trip. State what the database does and name the rule that is applied. *[2 marks]*"),
          ["sql queries", "keys and relationships"], "moyenne", 5,
          [(r"You write a query with a subquery `NOT IN (SELECT PassengerID FROM Booking)`, or a LEFT JOIN with `IS NULL`", 2),
           (r"You give the result: Eyenga Blaise", 1),
           (r"You say that the database rejects the row with a foreign key error", 1),
           (r"You name the rule: referential integrity, a foreign key value must match a primary key value of the parent table", 1)],
          r"A subquery with NOT IN returns the keys found in another table, so selecting the rows whose key is not in that list gives the rows without a match; a foreign key constraint is checked by the database, which refuses any row whose foreign key value does not exist as a primary key value in the parent table, and this rule is called referential integrity.",
          P(r"(i) The bookings of a passenger are rows of `Booking` with the same `PassengerID`, so the passengers without a booking are those whose identifier is not in that column:",
            "```sql\nSELECT FullName\nFROM Passenger\nWHERE PassengerID NOT IN (SELECT PassengerID FROM Booking);\n```\n\n" + T(["FullName"], [("Eyenga Blaise",)]),
            r"(ii) The statement is rejected: the database stops with the error `FOREIGN KEY constraint failed`, because the value T999 of the foreign key `TripCode` does not exist in the column `TripCode` of `Trip`. The rule is referential integrity: every value of a foreign key must match a primary key value in the table it refers to."),
          ans=r"(i) Eyenga Blaise ; (ii) the insertion is rejected, referential integrity"),
    ]))

    # ---- Exercice 4 : algorithm tracing (12) ----
    ex.append(E("4", G, 12, P(
        r"**Question 4: Algorithm tracing.** The weather station of Idenau records the rainfall of each day, in mm. Algorithm 1 analyses the readings of nine days. In the pseudocode, `←` is the assignment, the first item of an array has the index 1, and `DIV` gives the whole-number quotient of a division.",
        "**Algorithm 1**",
        "```pseudo\nrain ← [4, 12, 15, 0, 11, 22, 30, 3, 14]\nwet ← 0\nrun ← 0\nbest ← 0\nFOR i ← 1 TO 9\n    IF rain[i] > 10 THEN\n        wet ← wet + 1\n        run ← run + 1\n        IF run > best THEN\n            best ← run\n        ENDIF\n    ELSE\n        run ← 0\n    ENDIF\nNEXT i\nOUTPUT wet, best\n```"), [
        S("a", P(r"Complete the trace table below for Algorithm 1: write in each row the value of every variable at the end of the pass of the loop for that value of `i`. Then write the output of the algorithm.",
                 T(["i", "rain[i]", "wet", "run", "best"], [(i, "", "", "", "") for i in range(1, 10)]), r"*[5 marks]*"),
          ["algorithm tracing"], "faible", 5,
          [(r"You write the values of `rain[i]` and the counter `wet` correctly in all nine rows (0, 1, 2, 2, 3, 4, 5, 5, 6)", 1),
           (r"You show `run` going up on the days above 10 and back to 0 on days 1, 4 and 8", 2),
           (r"You show `best` staying at its largest value so far (0, 1, 2, 2, 2, 2, 3, 3, 3)", 1),
           (r"You write the output: 6 and 3", 1)],
          r"To trace an algorithm, follow the instructions in order with the given data, write in a table the value of each variable after each pass of the loop, and leave a variable unchanged in its column until an instruction modifies it.",
          P(r"A day with more than 10 mm adds 1 to `wet` and to `run`, and `best` takes the value of `run` whenever `run` is larger; a day with 10 mm or less sets `run` back to 0.",
            T(["i", "rain[i]", "wet", "run", "best"],
              [(1, 4, 0, 0, 0), (2, 12, 1, 1, 1), (3, 15, 2, 2, 2), (4, 0, 2, 0, 2), (5, 11, 3, 1, 2), (6, 22, 4, 2, 2), (7, 30, 5, 3, 3), (8, 3, 5, 0, 3), (9, 14, 6, 1, 3)]),
            r"The algorithm outputs `6 3`."),
          ans=r"output: 6 and 3"),
        S("b", P(r"(i) State what the variable `wet` and the variable `best` represent when the algorithm ends. *[2 marks]*",
                 r"(ii) State the output of Algorithm 1 if the nine readings are all equal to 10. *[1 mark]*"),
          ["algorithm tracing"], "faible", 3,
          [(r"You say that `wet` is the number of days with more than 10 mm", 1),
           (r"You say that `best` is the longest spell of consecutive days with more than 10 mm", 1),
           (r"You give the output 0 and 0, because 10 is not greater than 10", 1)],
          r"The purpose of an algorithm is found by looking at what each variable accumulates and under which condition: a counter that changes on every pass that satisfies a test counts the cases, a second variable that is set back to zero and then compared remembers the longest run, and the exact comparison operator decides what happens at the boundary value.",
          P(r"(i) `wet` is incremented on every day with more than 10 mm, so it is the number of such days. `run` counts the consecutive days with more than 10 mm and is reset by a dry day, and `best` keeps the largest value of `run`, so it is the longest spell of consecutive days with more than 10 mm.",
            r"(ii) The test is `rain[i] > 10`: a reading of exactly 10 is not greater than 10, so the ELSE branch is taken on every day, `wet` and `best` stay at 0, and the output is `0 0`."),
          ans=r"(i) number of days above 10 mm and longest spell ; (ii) 0 and 0"),
        S("c", P(r"The stations of the mountain are sorted by increasing altitude, in m. Algorithm 2 looks for an altitude in this list.",
                 "**Algorithm 2**",
                 "```pseudo\nalt ← [150, 420, 650, 980, 1250, 1620, 2100, 2800]\ntarget ← 1000\nlow ← 1\nhigh ← 8\nfound ← FALSE\nWHILE low <= high AND NOT found\n    mid ← (low + high) DIV 2\n    IF alt[mid] = target THEN\n        found ← TRUE\n    ELSEIF alt[mid] < target THEN\n        low ← mid + 1\n    ELSE\n        high ← mid - 1\n    ENDIF\nENDWHILE\nIF found THEN\n    OUTPUT \"Found at position\", mid\nELSE\n    OUTPUT \"Not found\"\nENDIF\n```",
                 r"Trace Algorithm 2: write in a table the values of `low`, `high` and `mid` at the end of each pass of the WHILE loop, and write the output. *[4 marks]*"),
          ["algorithm tracing"], "moyenne", 4,
          [(r"You find `mid = 4` in the first pass and `low = 5`, because alt[4] = 980 is less than 1000", 1),
           (r"You find `mid = 6` in the second pass and `high = 5`, because alt[6] = 1620 is greater than 1000", 1),
           (r"You find `mid = 5` in the third pass and `high = 4`, and stop because low is greater than high", 1),
           (r"You write the output: Not found", 1)],
          r"A binary search compares the target with the middle item of the part of the sorted list that is still possible, then discards the half that cannot contain it by moving low up or high down, and it stops when the item is found or when low becomes greater than high.",
          P(r"Before the loop, `low = 1` and `high = 8`.",
            T(["Pass", "mid", "alt[mid]", "low", "high", "found"],
              [(1, 4, 980, 5, 8, "FALSE"), (2, 6, 1620, 5, 5, "FALSE"), (3, 5, 1250, 5, 4, "FALSE")]),
            r"After the third pass `low = 5` is greater than `high = 4`, so the loop ends with `found` still FALSE and the output is `Not found`."),
          ans=r"Not found",
          conseil=r"`mid` is a whole-number quotient: $(1+8)$ DIV $2$ is $4$, not $4.5$."),
    ]))

    # ---- Exercice 5 : pseudocode and subprograms (12) ----
    ex.append(E("5", G, 12, P(
        r"**Question 5: Pseudocode and subprograms.** The rainfall data of a month is processed by an algorithm made of subprograms. Write your answers in pseudocode, with the keywords `FUNCTION`, `ENDFUNCTION`, `FOR`, `NEXT`, `REPEAT`, `UNTIL`, `IF`, `ENDIF`, `INPUT`, `OUTPUT` and `RETURN`, and use `←` for the assignment. An array is indexed from 1."), [
        S("a", r"Write a pseudocode function `ReadRainfall()` with no parameter that asks the user for the rainfall of one day, a whole number of mm between 0 and 500 inclusive. If the value is not valid, the function displays the message `Invalid rainfall` and asks again. When the value is valid, the function returns it. *[4 marks]*",
          ["pseudocode algorithms", "program control constructs"], "faible", 4,
          [(r"You display a prompt and read the value inside a loop", 1), (r"You write the correct condition of an invalid value: `value < 0 OR value > 500`", 1),
           (r"You display the message `Invalid rainfall` for an invalid value", 1), (r"You use a REPEAT UNTIL loop (or an equivalent loop that runs at least once) and you return the valid value", 1)],
          r"A function that validates an input repeats the prompt inside a loop that tests the condition of a valid value, displays an error message for an invalid value and returns the valid value; a loop that must run at least once is a REPEAT UNTIL loop whose condition describes the valid value.",
          P(r"The prompt and the reading must be done at least once, so a REPEAT UNTIL loop is the natural choice, and the loop ends when the value is between 0 and 500:",
            "```pseudo\nFUNCTION ReadRainfall() RETURNS INTEGER\n    REPEAT\n        OUTPUT \"Enter the rainfall in mm (0 to 500)\"\n        INPUT value\n        IF value < 0 OR value > 500 THEN\n            OUTPUT \"Invalid rainfall\"\n        ENDIF\n    UNTIL value >= 0 AND value <= 500\n    RETURN value\nENDFUNCTION\n```",
            r"For example, if the user types -5, then 620, then 35, the function displays `Invalid rainfall` twice and returns 35."),
          piege=r"The UNTIL condition is the condition of a VALID value: writing `UNTIL value < 0 OR value > 500` would stop the loop on an invalid value."),
        S("b", r"Write a pseudocode function `CountAbove(rain, n, limit)` where `rain` is an array of `n` whole numbers, indexed from 1 to `n`, and `limit` is a whole number. The function returns the number of values of the array that are strictly greater than `limit`. *[4 marks]*",
          ["subprograms", "program control constructs"], "moyenne", 4,
          [(r"You give the function the three parameters and a counter set to 0 before the loop", 1),
           (r"You loop on the positions of the array with `FOR i ← 1 TO n`", 1),
           (r"You compare each value with `IF rain[i] > limit` and add 1 to the counter", 1),
           (r"You return the counter after the loop, outside the loop", 1)],
          r"A function that works on an array receives the array and its size as parameters, visits every position with a FOR loop, applies a comparison to each item with an IF and uses a counter set to zero before the loop; the result is given back to the caller with RETURN after the loop has ended.",
          P(r"The counter is set to 0 first, each value greater than `limit` adds 1, and the value is returned only when all the positions have been examined:",
            "```pseudo\nFUNCTION CountAbove(rain, n, limit) RETURNS INTEGER\n    count ← 0\n    FOR i ← 1 TO n\n        IF rain[i] > limit THEN\n            count ← count + 1\n        ENDIF\n    NEXT i\n    RETURN count\nENDFUNCTION\n```",
            r"For example, with the seven values 20, 35, 0, 48, 10, 52 and 5 and `limit = 10`, the function returns 4 (the values 20, 35, 48 and 52)."),
          piege=r"A RETURN inside the FOR loop would end the function after the first value."),
        S("c", r"Write the main pseudocode algorithm that asks the user how many days of data there are (assume that the number `n` typed is between 1 and 31), reads the `n` rainfalls into an array, using the function `ReadRainfall()`, and then displays the average rainfall rounded to one decimal place and the number of days with more than 20 mm, using the function `CountAbove`. *[4 marks]*",
          ["pseudocode algorithms", "subprograms"], "moyenne", 4,
          [(r"You declare the array of 31 values and read `n`", 1),
           (r"You call `ReadRainfall()` once per day in a FOR loop, store each value in the array and accumulate the total", 1),
           (r"You calculate and display the average `total / n` rounded to one decimal place", 1),
           (r"You call `CountAbove(rain, n, 20)` and display the result", 1)],
          r"A main algorithm declares its array, reads the number of items, uses a FOR loop to call an input function once for each reading while it accumulates a total, divides the total by the number of readings to get the mean and passes the array and its size to the subprogram that counts.",
          P(r"The loop calls `ReadRainfall()` `n` times. The average is the total divided by `n`, and the count of the days above 20 mm is obtained with the limit 20:",
            "```pseudo\nDECLARE rain : ARRAY[1..31] OF INTEGER\nOUTPUT \"How many days of data (1 to 31)?\"\nINPUT n\ntotal ← 0\nFOR i ← 1 TO n\n    rain[i] ← ReadRainfall()\n    total ← total + rain[i]\nNEXT i\naverage ← total / n\nOUTPUT \"Average rainfall:\", ROUND(average, 1)\nOUTPUT \"Days above 20 mm:\", CountAbove(rain, n, 20)\n```",
            r"With $n=7$ and the readings 20, 35, 0, 48, 10, 52 and 5, the total is 170, the average is 24.3 and three days (35, 48 and 52) have more than 20 mm:",
            "```text\nAverage rainfall: 24.3\nDays above 20 mm: 3\n```"),
          conseil=r"The reading of 20 mm is not counted by `CountAbove(rain, n, 20)`, because the comparison is strictly greater."),
    ]))

    # ---- Exercice 6 : programming in C (30) ----
    ex.append(E("6", G, 30, P(
        r"**Question 6: Programming in C.** A program in ANSI C analyses the rainfall of four weather stations of the Mount Cameroon region, in mm, for the six months from January to June. The data and the declarations are given below (this code is already written and must not be changed). The rows of the two-dimensional array `rain` are the stations and its columns are the months.",
        C_DONNE,
        r"Station numbers and month numbers typed by the user start at 1, and the indices of the arrays start at 0. In your answers, you may assume that the user always types whole numbers."), [
        S("a", P(r"Write three C functions. In each of them the parameter `r` is the two-dimensional array of the rainfall and the parameter list must show how a two-dimensional array is received.",
                 r"(i) `int station_total(int r[][MONTHS], int s)` returns the total rainfall of the station with index `s` over the six months. *[3 marks]*",
                 r"(ii) `int wettest_month(int r[][MONTHS], int s)` returns the index of the month with the highest rainfall at the station with index `s` (the first one if several months are equal). *[4 marks]*",
                 r"(iii) `int stations_above(int r[][MONTHS], int m, int limit)` returns the number of stations whose rainfall in the month with index `m` is strictly greater than `limit`. *[3 marks]*"),
          ["programming in c", "two-dimensional arrays", "subprograms"], "moyenne", 10,
          [(r"`station_total` adds `r[s][m]` for every month in a loop and returns the sum", 3),
           (r"`wettest_month` starts with the index 0 as the best month and loops over the other months, from 1 to `MONTHS - 1`", 2),
           (r"`wettest_month` replaces the index only when `r[s][m] > r[s][best]` and returns the index, not the rainfall", 2),
           (r"`stations_above` loops over the stations with the month index `m` kept fixed, and compares `r[s][m]` with `limit` using `>`", 2),
           (r"`stations_above` counts the stations and returns the count", 1)],
          r"In C, a function that receives a two-dimensional array must give the number of columns in its parameter, as in int r[][MONTHS], because the compiler needs it to find the address of an element; the indices of rows and columns start at 0, a total is built with an accumulator set to zero before the loop, and a maximum is found by keeping the index of the best element so far.",
          P(r"The first function adds the six values of one row. The second keeps the index of the best month: it starts with month 0 and compares each following month with the best one found, using `>` so that the first of several equal months is kept. The third function runs along one column, with the station index changing and the month index fixed.",
            "```c\n" + C_STATION_TOTAL + "\n\n" + C_WETTEST + "\n\n" + C_ABOVE + "\n```",
            r"For example, for Buea (index 2) `station_total` returns 1075 and `wettest_month` returns 5, which is June (350 mm); in March (index 2), `stations_above` with the limit 100 returns 3 (Debundscha, Idenau and Buea)."),
          piege=r"`wettest_month` must return the index of the month, not the largest rainfall: the main program needs the index to print the name of the month."),
        S("b", P(r"Write the C function `void print_report(int r[][MONTHS])` that displays the rainfall table in the layout below: a title line, one line per station with its six values and its total, and a last line `All stations` with the total of each month and the grand total. The station names are written in a field of 12 characters, left-justified; each month name and each value in a field of 5 characters, right-justified; the totals in a field of 7 characters, right-justified. Use the function `station_total`.",
                 "```text\n" + SORTIE_REPORT + "\n```", r"*[10 marks]*"),
          ["programming in c", "two-dimensional arrays", "subprograms"], "elevee", 10,
          [(r"You print the title line with `%-12s` for `Station`, `%5s` for each month name and `%7s` for `Total`", 2),
           (r"You print each station line with two nested loops, the name with `%-12s`, each value with `%5d` and the total returned by `station_total` with `%7d`", 3),
           (r"You print the line `All stations` with an inner loop on the stations, with the month index fixed, that accumulates the total of each month", 3),
           (r"You accumulate the grand total, print it with `%7d` and end each line with a new line, so that the output is identical to the layout", 2)],
          r"A table is displayed with an outer loop on the rows and an inner loop on the columns, and the field widths of printf, such as %-12s for a left-justified text and %5d for a right-justified number, align the columns; the total of a column needs an inner loop in which the column index is fixed and the row index changes, with a new line printed only at the end of each row.",
          P(r"The title line uses the widths 12, 5 and 7. For each station, the outer loop prints the name, the inner loop prints the six values and the total comes from `station_total`. For the last line, the outer loop is on the months and the inner loop adds the rainfall of the four stations; the grand total is the sum of the six month totals.",
            "```c\n" + C_REPORT + "\n```",
            r"Called with `print_report(rain)`, the function displays exactly the layout of the question:",
            "```text\n" + SORTIE_REPORT + "\n```"),
          conseil=r"Check the last line by adding it up twice: the six month totals and the four station totals both give 6818."),
        S("c", P(r"(i) Write the C function `int read_in_range(const char *prompt, int low, int high)` that displays `prompt`, reads a whole number, and repeats while the number is smaller than `low` or greater than `high`. Each time the number is not valid it displays `Invalid: enter a number from low to high.` with the two limits written in the message. The function returns the valid number. *[4 marks]*",
                 r"(ii) Write the function `main` that: calls `print_report(rain)` and then prints an empty line; reads a station number from 1 to 4 with `read_in_range`; prints one line with the name of the station, its total and the name and the rainfall of its wettest month, in the form `Buea: total 1075 mm, wettest month Jun (350 mm)`; reads a month number from 1 to 6 with `read_in_range`; reads a limit in mm; and prints, in the form `Stations above 100 mm in Mar: 3`, the number of stations above the limit in that month. *[6 marks]*",
                 r"Give the complete output of your program when the user types the values 7, 0, 3, 3 and 100, in this order. The typed values are not echoed in the output."),
          ["programming in c", "subprograms"], "moyenne", 10,
          [(r"`read_in_range` displays the prompt and reads the value with `scanf` and `&value` inside a do-while loop", 2),
           (r"`read_in_range` displays the message with the two limits for an invalid number, repeats until the number is between `low` and `high`, and returns it", 2),
           (r"`main` calls `print_report`, reads the station with `read_in_range(..., 1, STATIONS)` and converts it to an index by subtracting 1", 2),
           (r"`main` prints the name of the station, its total and the name and the rainfall of its wettest month using `wettest_month`", 2),
           (r"`main` reads the month and the limit, and prints the result of `stations_above`; the output shown is the one of the program", 2)],
          r"Input validation in C uses a do-while loop that displays the prompt, reads the value with scanf using the address of the variable, tests the range and repeats until the value is valid; a function that returns the value can be called several times with different prompts and limits, and a number typed by the user, which starts at 1, is converted to an array index by subtracting 1.",
          P(r"(i) The loop must run at least once, so a do-while loop is used. The message is displayed inside the loop when the value is out of range.",
            "```c\n" + C_READ + "\n```",
            r"(ii) The station and the month are typed from 1, so 1 is subtracted before they are used as indices:",
            "```c\n" + C_MAIN + "\n```",
            r"The complete program is the code given in the question, followed by the five functions of parts (a), (b) and (c)(i) and by `main`. It compiles with the ANSI C options of gcc without any warning. With the typed values 7, 0, 3, 3 and 100, the values 7 and 0 are rejected, 3 selects Buea and then March, and 100 is the limit:",
            "```text\n" + SORTIE_MAIN + "\n```"),
          piege=r"The month name and the rainfall must be read with the index `best` returned by `wettest_month`: `month_name[best]` and `rain[s][best]`."),
    ]))

    # ---- Exercice 7 : software testing (8) ----
    ex.append(E("7", G, 8, P(
        r"**Question 7: Software testing.** This question is about the functions of Question 6; the declarations and the table `rain` of Question 6 are used."), [
        S("a", P(r"The function `stations_above` of Question 6 is tested for the month of March (index 2), with the data of the table `rain`. Give three tests, one with normal data, one with boundary data and one with extreme data. For each test, give the value of `limit` and the result that you expect before you run the program.",
                 T(["Type of test", "Value of limit", "Expected result"], [("Normal", "", ""), ("Boundary", "", ""), ("Extreme", "", "")]), r"*[3 marks]*"),
          ["software testing", "programming in c"], "faible", 3,
          [(r"You give a normal test with a result that you calculated, for example `limit = 100` and the expected result 3", 1),
           (r"You give a boundary test where `limit` is equal to a value of the March column, for example 130 with the expected result 2, because the comparison is strictly greater", 1),
           (r"You give an extreme test, for example `limit = 1000` with the expected result 0", 1)],
          r"A test plan lists test data of three kinds, normal data that the program must accept, boundary data at the edge of what is allowed or at the value where a comparison changes its result, and extreme data far outside the usual values, each with the result predicted by hand before the program is run.",
          P(r"The March column of the table is 405, 210, 130 and 90. The expected results are worked out by hand and then confirmed by running the function:",
            T(["Type of test", "Value of limit", "Expected result"], [("Normal", 100, 3), ("Boundary", 130, 2), ("Extreme", 1000, 0)]),
            r"The boundary test is chosen at 130, a value of the column: the comparison is strictly greater, so the station with exactly 130 mm is not counted, and the result is 2. A program that used `>=` would give 3 and would be detected. The function run on these three values displays:",
            "```text\n" + SORTIE_7A + "\n```"),
          ans=r"100 gives 3, 130 gives 2, 1000 gives 0"),
        S("b", P(r"A student wrote this faulty version of `wettest_month`:",
                 "```c\n" + C_FAUTIF + "\n```",
                 r"(i) Give a row of six rainfall values that shows the fault. Write the result that is expected and the result that the faulty function returns for your row. *[2 marks]*",
                 r"(ii) Write the correction. *[1 mark]*"),
          ["software testing", "programming in c"], "moyenne", 3,
          [(r"You give a row in which the largest value appears twice, for example 50, 90, 90, 10, 20, 30", 1),
           (r"You state the expected result 1 (the first of the two equal months) and the faulty result 2", 1),
           (r"You correct the comparison: replace `>=` by `>`", 1)],
          r"To find a logic error, choose data for which the faulty code and the correct code behave differently, predict the correct result by hand, run the program and compare the two results; the correction is made at the instruction that carries the wrong operator or the wrong condition.",
          P(r"With `>=`, a month that is equal to the best one replaces it, so the function returns the last of several equal months and not the first. The row `{50, 90, 90, 10, 20, 30}` has its maximum in February and in March: the expected index is 1 and the faulty function returns 2. The faulty and the corrected functions, run on this row, display:",
            "```text\n" + SORTIE_7B + "\n```",
            r"The correction is to replace `>=` by `>` in the comparison `if (r[s][m] > r[s][best])`, as in the function of Question 6."),
          ans=r"row 50, 90, 90, 10, 20, 30: expected 1, faulty 2 ; replace >= by >"),
        S("c", P(r"(i) Name the type of error in the faulty function. *[1 mark]*",
                 r"(ii) Explain why the compiler does not report this error and why a run with the table `rain` of Question 6 does not show it. *[1 mark]*"),
          ["software testing"], "faible", 2,
          [(r"You name a logic error", 1),
           (r"You explain that the code is valid C, so the compiler accepts it, and that no station of the table has two equal months, so the two versions give the same results on this data", 1)],
          r"Errors are classified by the way they are detected: a violation of the rules of the language is reported by the compiler before the program runs, whereas an instruction that is valid but does the wrong thing is found only by running the program on test data for which the result is known.",
          P(r"(i) It is a logic error: the program compiles and runs, but it does not do what it is meant to do.",
            r"(ii) The comparison `>=` is a correct instruction of the C language, so the compiler has nothing to report. The fault shows only when two months have the same largest rainfall, and in the table of Question 6 every station has a single largest value, so the faulty and the corrected functions return the same month for the four stations."),
          ans=r"logic error"),
    ]))
    return ex
