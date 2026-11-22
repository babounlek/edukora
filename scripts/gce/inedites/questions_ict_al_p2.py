r"""Les 8 exercices de l'epreuve inedite GCE A Level ICT Paper 2 n.1 (134 marks, 2 h 30, tout obligatoire).

Structure mesuree sur les Paper 2 de 2025 et 2026 (8 exercices de 17 marks, 3 ou 4 questions (i)(ii)(iii) par exercice, chacune a plusieurs parties
de 1 a 4 marks : definitions, « describe », « state two », comparaisons, quelques calculs de bases, de fichiers, de tables de verite, de normalisation).
Aucun enonce, aucune donnee, aucun contexte, aucun jeu de nombres repris d'un sujet reel. Le blueprint porte 3 questions par exercice (une par
competence) : chaque sous-question ci-dessous regroupe donc plusieurs parties (i), (ii), (iii).
Chaque sous-question : bareme exact (`pts`), grille `crit` (somme = pts), rappel (un paragraphe general), resolution, reponse finale `ans`
(recalculee par verifier_reponses_ict_al_p2.py). Chaines BRUTES. Numeros affiches : lettres a, b, c (un numero unique par exercice).
Les expressions booleennes, les relations et le code sont en code en ligne ou en bloc ; les calculs en KaTeX.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_addmaths_p2_a import E, S  # noqa: E402,F401

G = ""  # pas de groupes : paper plat (le blueprint n'en porte pas)


def P(*parts):
    """Paragraphes separes par une ligne vide."""
    return "\n\n".join(parts)


# Constantes partagees avec verifier_reponses_ict_al_p2.py et figs_ict_al_p2.py
PSEUDO_5A = """```
total ← 0
heavy ← 0
INPUT w
WHILE w <> 0 DO
    total ← total + w
    IF w >= 50 THEN
        heavy ← heavy + 1
    ENDIF
    INPUT w
ENDWHILE
OUTPUT total, heavy
```"""

PSEUDO_5A_BIS = """```
total ← 0
heavy ← 0
count ← 0
INPUT w
WHILE w <> 0 DO
    total ← total + w
    count ← count + 1
    IF w >= 50 THEN
        heavy ← heavy + 1
    ENDIF
    INPUT w
ENDWHILE
IF count > 0 THEN
    OUTPUT total, heavy, total / count
ELSE
    OUTPUT "No delivery"
ENDIF
```"""

SQL_8B_I = "SELECT FarmerName FROM FARMER WHERE Village = 'Bafang' ORDER BY FarmerName;"
SQL_8B_II = ("SELECT Village, SUM(Kg) FROM FARMER INNER JOIN DELIVERY ON FARMER.FarmerID = DELIVERY.FarmerID "
             "WHERE DeliveryMonth = 'Nov' GROUP BY Village ORDER BY Village;")
SQL_8B_III = ("SELECT DISTINCT FarmerName FROM FARMER INNER JOIN DELIVERY ON FARMER.FarmerID = DELIVERY.FarmerID "
              "WHERE Kg > 100 ORDER BY FarmerName;")


def exercices():
    ex = []

    # ---- Exercice 1 : input devices, operating systems, communication systems (17) ----
    ex.append(E("1", G, 17, "", [
        S("a", P(r"A regional examination board in Bafoussam captures the answers of candidates written on pre-printed multiple-choice sheets, and the registration desk checks each candidate with a fingerprint reader.",
                 r"(i) Name the data capture method that reads the shaded answer boxes of the sheets and describe how it works. (3 marks)",
                 r"(ii) State two advantages of this method over typing the answers on a keyboard. (2 marks)",
                 r"(iii) State one reason why a fingerprint reader may reject a genuine candidate. (1 mark)"),
          ["input devices and data capture"], "faible", 6,
          [(r"You name optical mark recognition (OMR) and its reader", 1),
           (r"You say that shaded boxes reflect less light than blank boxes, so the reader detects which positions are marked", 1),
           (r"You say that the software converts each marked position into an answer and stores it in a file", 1),
           (r"You state a first advantage, for example speed for a large number of sheets", 1),
           (r"You state a second advantage, for example no keying errors", 1),
           (r"You state a valid reason, for example a wet, dirty or injured finger", 1)],
          r"A data capture method turns marks on a document into data without a person typing them; to describe one, say what is sensed (light, shape, pattern), how the position or pattern becomes a value, and where the value is stored, then compare it with manual entry on speed, accuracy and cost.",
          P(r"(i) The method is optical mark recognition (OMR). The OMR reader shines light on the sheet. A shaded box reflects less light than a blank one, so the reader detects which positions on each row are marked. The software converts each marked position into an answer (A, B, C or D) and stores the answers of the candidate in a file for marking.",
            r"(ii) Advantages: a very large number of sheets is read quickly, and there are no keying (transcription) errors because nobody types the answers. A further acceptable advantage is a lower labour cost.",
            r"(iii) A fingerprint reader may reject a genuine candidate when the finger is wet, dirty, oily or injured, so the pattern read does not match the stored pattern closely enough."),
          ans=r"OMR ; speed and fewer errors ; damaged or dirty finger",
          piege=r"OCR reads printed characters and OMR reads marks in boxes: a sheet of shaded boxes is not an OCR job."),
        S("b", P(r"An operating system schedules the jobs waiting for the processor.",
                 r"(i) State two functions of an operating system other than scheduling. (2 marks)",
                 r"(ii) Four processes arrive together at time 0 and wait for one processor. Their CPU burst times are given below.",
                 "| Process | P1 | P2 | P3 | P4 |\n|---|---|---|---|---|\n| Burst time (ms) | 7 | 3 | 5 | 1 |",
                 r"Calculate the average waiting time when the processes run (a) in the order P1, P2, P3, P4 (first come first served) and (b) shortest job first, without pre-emption. Show the waiting time of each process. (4 marks)"),
          ["ict operating systems"], "moyenne", 6,
          [(r"You state two functions, for example memory management, file management, device management, security", 1),
           (r"You find the waiting times $0$, $7$, $10$, $15$ ms for first come first served", 1),
           (r"You obtain an average of $8.0$ ms", 1),
           (r"You order the jobs P4, P2, P3, P1 and find the waiting times $0$, $1$, $4$, $9$ ms", 1),
           (r"You obtain an average of $3.5$ ms for shortest job first", 1),
           (r"You compare: the shorter jobs go first, so the average wait is smaller", 1)],
          r"The waiting time of a process is the time it spends in the ready queue before it first runs, which equals the sum of the burst times of the processes that run before it when there is no pre-emption; the average is the sum of the waiting times divided by the number of processes.",
          P(r"(i) Any two of: memory management (allocating and freeing memory for programs), file management (organising, naming and protecting files), device management (controlling peripherals through drivers), security and user accounts, providing a user interface.",
            r"(ii)(a) First come first served, order P1, P2, P3, P4: P1 waits $0$ ms; P2 waits $7$ ms; P3 waits $7+3=10$ ms; P4 waits $10+5=15$ ms. Average $=\dfrac{0+7+10+15}{4}=\dfrac{32}{4}=8.0$ ms.",
            r"(b) Shortest job first: the order is P4 (1 ms), P2 (3 ms), P3 (5 ms), P1 (7 ms). P4 waits $0$; P2 waits $1$; P3 waits $1+3=4$; P1 waits $4+5=9$ ms. Average $=\dfrac{0+1+4+9}{4}=\dfrac{14}{4}=3.5$ ms. Running the short jobs first reduces the average wait."),
          ans=r"Average waiting time $8.0$ ms (first come first served) and $3.5$ ms (shortest job first)",
          piege=r"The waiting time is not the finishing time: P1 finishes at $7$ ms in the first order, but its waiting time is $0$."),
        S("c", P(r"A cocoa cooperative in Mbouda holds its weekly meeting with its two regional offices by video conferencing.",
                 r"(i) State two items of hardware needed at each site to take part in a video conference. (2 marks)",
                 r"(ii) Each video stream needs $1.5$ Mbit/s and the shared Internet link of the cooperative offers $10$ Mbit/s. Calculate the largest number of streams that the link can carry at the same time. (2 marks)",
                 r"(iii) State one disadvantage of video conferencing compared with a face-to-face meeting. (1 mark)"),
          ["ict communication systems"], "faible", 5,
          [(r"You state two items, for example a webcam, a microphone, a loudspeaker or a screen, a computer with a codec", 2),
           (r"You divide $\dfrac{10}{1.5}=6.67$", 1), (r"You round down to $6$ streams, because a stream cannot be shared in parts", 1),
           (r"You state a valid disadvantage, for example a poor connection breaks the meeting or the cost of the equipment", 1)],
          r"The number of streams a link can carry is the capacity of the link divided by the rate of one stream, rounded down to a whole number because a partial stream cannot be carried; hardware for conferencing must capture and play both sound and picture at each site.",
          P(r"(i) A webcam (to capture the picture) and a microphone (to capture the sound); a screen and a loudspeaker or headset are also needed to see and hear the other sites, and a computer or codec to compress and send the signal.",
            r"(ii) Number of streams $=\dfrac{10}{1.5}=6.67$. Only whole streams can be carried, so the link carries $6$ streams.",
            r"(iii) A disadvantage is that the conference depends on the quality of the Internet connection: a slow or broken link freezes the picture or ends the meeting. The cost of the equipment and the loss of personal contact are also valid."),
          ans=r"$6$ streams",
          piege=r"Do not round $6.67$ up to $7$: seven streams would need $10.5$ Mbit/s, more than the link offers."),
    ]))

    # ---- Exercice 2 : transmission modes, normalisation, database concepts (17) ----
    ex.append(E("2", G, 17, "", [
        S("a", P(r"(i) Distinguish between simplex, half-duplex and full-duplex transmission, giving one example of each. (3 marks)",
                 r"(ii) A text file of $4500$ bytes is sent over a serial link at $9600$ bits per second in asynchronous mode. Each byte of $8$ data bits is framed by one start bit, one parity bit and one stop bit. Calculate the time taken to send the file, to two decimal places. (2 marks)"),
          ["ict transmission modes"], "moyenne", 5,
          [(r"You say that simplex is one direction only, for example a radio broadcast", 1),
           (r"You say that half-duplex is both directions but not at the same time, for example a walkie-talkie", 1),
           (r"You say that full-duplex is both directions at the same time, for example a telephone call", 1),
           (r"You find $8+1+1+1=11$ bits per byte and $4500\times11=49\,500$ bits", 1), (r"You divide by $9600$ and obtain $5.16$ s", 1)],
          r"The direction of a link is described by who may send and when; the time to send a file is the total number of bits, including the extra framing bits added to each byte, divided by the bit rate of the link.",
          P(r"(i) Simplex: data flows in one direction only, for example from a transmitter to a radio receiver. Half-duplex: data flows in both directions but only one direction at a time, for example a walkie-talkie. Full-duplex: data flows in both directions at the same time, for example a telephone conversation.",
            r"(ii) Each byte is sent as $1+8+1+1=11$ bits. Total bits $=4500\times11=49\,500$. Time $=\dfrac{49\,500}{9600}=5.15625\approx5.16$ s."),
          ans=r"$5.16$ s",
          piege=r"Using $4500\times8=36\,000$ bits gives $3.75$ s: the start, parity and stop bits are also sent and must be counted."),
        S("b", P(r"A cocoa buying cooperative records each delivery on one sheet, which is stored in a single relation:",
                 r"`DELIVERY(DeliveryNo, DeliveryDate, FarmerID, FarmerName, Village, ProductCode, ProductName, PricePerKg, KgDelivered)`",
                 r"The primary key is (`DeliveryNo`, `ProductCode`). A delivery has one date and one farmer, and it may contain several products. In addition, `FarmerID` determines `FarmerName` and `Village`, and `ProductCode` determines `ProductName` and `PricePerKg`.",
                 r"(i) Explain why `DELIVERY` is not in second normal form and identify the partial dependencies. (3 marks)",
                 r"(ii) Identify the transitive dependency and explain why it breaks third normal form. (2 marks)",
                 r"(iii) Write the relations in third normal form, showing the primary key and the foreign keys of each. (2 marks)"),
          ["ict database normalisation"], "moyenne", 7,
          [(r"You say that second normal form forbids a non-key attribute that depends on only part of a composite key", 1),
           (r"You identify `DeliveryNo` determining `DeliveryDate` and `FarmerID`, and `ProductCode` determining `ProductName` and `PricePerKg`, as partial dependencies", 2),
           (r"You identify `DeliveryNo` determining `FarmerID` which determines `FarmerName` and `Village`, and say that third normal form forbids a non-key attribute depending on another non-key attribute", 2),
           (r"You write `DELIVERY`, `FARMER` and `PRODUCT` with the correct keys and foreign key", 1),
           (r"You write `DELIVERY_LINE` with the composite key (`DeliveryNo`, `ProductCode`) and `KgDelivered`", 1)],
          r"A relation is in second normal form when it is in first normal form and no non-key attribute depends on part of a composite key, and in third normal form when, in addition, no non-key attribute depends on another non-key attribute; normalising means moving each group of attributes with its determinant into a relation of its own and keeping the key as a foreign key to link the relations.",
          P(r"(i) The key is composite, and some non-key attributes depend on only one part of it. This is a partial dependency, so the relation is not in second normal form. The partial dependencies are: `DeliveryNo` determines `DeliveryDate` and `FarmerID` (and through it the farmer details), and `ProductCode` determines `ProductName` and `PricePerKg`. Only `KgDelivered` depends on the whole key.",
            r"(ii) `DeliveryNo` determines `FarmerID`, and `FarmerID` determines `FarmerName` and `Village`. So `FarmerName` and `Village` depend on `DeliveryNo` only through a non-key attribute (`FarmerID`): this is a transitive dependency. Third normal form forbids it because a farmer's name would be repeated and could be changed inconsistently for each delivery.",
            r"(iii) After removing the partial and the transitive dependencies:",
            "- `DELIVERY(DeliveryNo, DeliveryDate, FarmerID)`: primary key `DeliveryNo`, foreign key `FarmerID`\n- `FARMER(FarmerID, FarmerName, Village)`: primary key `FarmerID`\n- `PRODUCT(ProductCode, ProductName, PricePerKg)`: primary key `ProductCode`\n- `DELIVERY_LINE(DeliveryNo, ProductCode, KgDelivered)`: primary key (`DeliveryNo`, `ProductCode`), foreign keys `DeliveryNo` and `ProductCode`"),
          ans=r"Four relations in third normal form: `DELIVERY`, `FARMER`, `PRODUCT`, `DELIVERY_LINE`",
          conseil=r"Check the result by joining the four relations again: the join must give back every row of the original relation, with no row added and none lost."),
        S("c", P(r"(i) Distinguish between a primary key and a foreign key, using a table of farmers and a table of deliveries as the example. (2 marks)",
                 r"(ii) State three advantages of a database management system over a set of separate files for the same data. (3 marks)"),
          ["ict database concepts"], "faible", 5,
          [(r"You say that a primary key uniquely identifies each record of its table, with no repeated and no empty value", 1),
           (r"You say that a foreign key is a field that is the primary key of another table and so links the two tables, for example the farmer number in the deliveries table", 1),
           (r"You state three advantages, one mark each, for example less redundancy, consistent data, data sharing, security and access rights, easier queries", 3)],
          r"A key is a field or group of fields used to identify records or to link tables; the advantages of a database management system come from storing each fact once and controlling access to the data through one program.",
          P(r"(i) A primary key is a field (or group of fields) whose value uniquely identifies each record in its table, for example `FarmerID` in the farmers table; it cannot be repeated or left empty. A foreign key is a field in one table that holds values of the primary key of another table, for example `FarmerID` in the deliveries table, and it links each delivery to its farmer.",
            r"(ii) Any three of: data redundancy is reduced because each fact is stored once; the data stay consistent because a change is made in one place; several users can share the same data at the same time; security and access rights are controlled by the system; queries and reports are produced more easily; data is independent of the programs that use it."),
          ans=r"Primary key identifies a record ; foreign key links two tables ; three advantages of a DBMS"),
    ]))

    # ---- Exercice 3 : hardware, network topologies, computer networks (15) ----
    ex.append(E("3", G, 15, "", [
        S("a", P(r"(i) State the role of the control unit and the role of the program counter in the fetch-decode-execute cycle. (2 marks)",
                 r"(ii) A processor has a cache memory with an access time of $4$ ns and a main memory with an access time of $50$ ns. Of all the memory requests, $90\%$ find the data in the cache. A request that does not find the data in the cache takes the access time of the main memory only. Calculate the average access time. (2 marks)",
                 r"(iii) State one reason why the cache memory of a processor is small. (1 mark)"),
          ["computer hardware"], "moyenne", 5,
          [(r"You say that the control unit fetches and decodes each instruction and sends signals that coordinate the other parts", 1),
           (r"You say that the program counter holds the address of the next instruction to be fetched", 1),
           (r"You write $0.90\times4+0.10\times50$", 1), (r"You obtain $8.6$ ns", 1),
           (r"You say that fast memory costs much more per byte, so only a small amount is used", 1)],
          r"The control unit directs the fetch-decode-execute cycle and the program counter keeps track of where the next instruction is; an average access time is the weighted mean of the times of each case, each weighted by the fraction of requests that fall in that case.",
          P(r"(i) The control unit fetches each instruction from memory, decodes it and sends control signals to the other parts of the processor (ALU, registers, memory) to carry it out. The program counter holds the address of the next instruction to be fetched and is updated after each fetch.",
            r"(ii) Average time $=0.90\times4+0.10\times50=3.6+5.0=8.6$ ns.",
            r"(iii) Cache memory is made of very fast memory, which costs much more per byte than main memory, so the cache is kept small to limit the cost (and the space on the chip)."),
          ans=r"$8.6$ ns",
          piege=r"The mean of the two access times, $\dfrac{4+50}{2}=27$ ns, ignores that nine requests in ten are served by the cache."),
        S("b", P(r"A lycée in Dschang connects the $12$ computers of its ICT room in a local network built around one central switch.",
                 r"(i) Describe a star topology and state one advantage and one disadvantage of it. (3 marks)",
                 r"(ii) The school compares the star with a full mesh, in which every computer is cabled directly to every other computer. Calculate the number of cables needed for each of the two designs. (2 marks)"),
          ["ict network topologies", "ict computer networks"], "moyenne", 5,
          [(r"You describe a star: every computer is linked by its own cable to a central device (switch or hub)", 1),
           (r"You state an advantage, for example a faulty cable affects only one computer, or a computer is easy to add", 1),
           (r"You state a disadvantage, for example if the central device fails the whole network stops, or each computer needs its own cable", 1),
           (r"You calculate $\dfrac{12\times11}{2}=66$ cables for the full mesh", 1), (r"You state $12$ cables for the star, one per computer", 1)],
          r"In a star topology every device has its own link to a central device, so a fault on one link isolates one device only but a fault on the centre stops everything; counting the cables of a full mesh uses the number of different pairs of devices, which is $\dfrac{n(n-1)}{2}$ for $n$ devices.",
          P(r"(i) In a star topology each computer is connected by its own cable to a central switch (or hub), as shown in the figure below. Advantage: a fault on one cable affects only the computer on that cable, and a new computer is added by one more cable to the switch. Disadvantage: if the central switch fails, the whole network stops; it also needs one cable for each computer.",
            r"(ii) In a full mesh each pair of computers has its own cable, and the number of pairs of $12$ computers is $\dfrac{12\times11}{2}=66$. In the star each computer has one cable to the switch, so $12$ cables are needed. The mesh needs $66-12=54$ more cables."),
          ans=r"Full mesh $66$ cables ; star $12$ cables",
          fig="etoile",
          piege=r"Counting $12\times11=132$ gives each cable twice, once from each end."),
        S("c", P(r"(i) Distinguish between a LAN and a WAN. (2 marks)",
                 r"(ii) A file of $450$ MB is copied over a LAN link rated at $100$ Mbit/s. In practice only $80\%$ of the rated speed is available. Calculate the time taken, in seconds. Take $1$ byte $=8$ bits and $1$ MB $=1\,000\,000$ bytes. (2 marks)",
                 r"(iii) State one factor, other than the rated speed of the cable, that can make a real file transfer slower. (1 mark)"),
          ["ict computer networks"], "moyenne", 5,
          [(r"You say that a LAN covers a small area such as a building, with cabling owned by the organisation", 1),
           (r"You say that a WAN covers a large area such as towns or countries, using links leased from or shared with a carrier", 1),
           (r"You convert $450\ \mathrm{MB}=3600$ Mbit and the usable speed $=80$ Mbit/s", 1), (r"You obtain $\dfrac{3600}{80}=45$ s", 1),
           (r"You state a valid factor, for example network traffic from other users, a slow disk, a busy server or a faulty cable", 1)],
          r"A LAN and a WAN differ in the area they cover and in who owns the links; a transfer time is the quantity of data in bits divided by the usable rate in bits per second, so the data must first be converted from bytes to bits and the rate reduced by the efficiency of the link.",
          P(r"(i) A LAN (local area network) covers a small area such as a room or a building, and its cables and devices belong to the organisation that uses it. A WAN (wide area network) covers a large area such as several towns or countries and uses links provided by telecommunication companies; the Internet is the largest WAN.",
            r"(ii) Size $=450\times8=3600$ Mbit. Usable speed $=0.80\times100=80$ Mbit/s. Time $=\dfrac{3600}{80}=45$ s.",
            r"(iii) Other users sending data on the same network at the same time (traffic), a slow hard disk, a busy server, a faulty cable or a weak signal on a wireless link."),
          ans=r"$45$ s",
          piege=r"A link is rated in megabits per second but a file in megabytes: using $\dfrac{450}{100}=4.5$ s forgets the factor $8$ and the $80\%$."),
    ]))

    # ---- Exercice 4 : internet, licensing, hardware (17) ----
    ex.append(E("4", G, 17, "", [
        S("a", P(r"(i) Explain what a DNS server does when a user types a web address in a browser. (2 marks)",
                 r"(ii) The IPv4 address $172.16.5.200$ is made of four bytes. Write it in binary, one byte at a time. (2 marks)",
                 r"(iii) State the number of different addresses that IPv4 can provide, and give one reason why IPv6 was introduced. (2 marks)"),
          ["internet and web technologies"], "moyenne", 6,
          [(r"You say that the DNS server translates the domain name into the numeric IP address", 1),
           (r"You say that the browser then uses the IP address to contact the web server", 1),
           (r"You convert $172=10101100$ and $16=00010000$", 1), (r"You convert $5=00000101$ and $200=11001000$", 1),
           (r"You state $2^{32}=4\,294\,967\,296$ addresses", 1),
           (r"You state a reason, for example the IPv4 addresses are running out because of the growing number of connected devices", 1)],
          r"People use domain names while computers route data with numeric addresses, so a name must be translated before a page can be requested; an IPv4 address has four bytes, each written in decimal for people and in binary by the machine, so the number of addresses is a power of two.",
          P(r"(i) The DNS (Domain Name System) server holds a table linking domain names to IP addresses. It translates the name typed in the browser into the numeric IP address of the web server, and the browser then uses that address to request the page.",
            r"(ii) $172=128+32+8+4=10101100$; $16=00010000$; $5=00000101$; $200=128+64+8=11001000$. The address is $10101100.00010000.00000101.11001000$.",
            r"(iii) IPv4 uses $32$ bits, so it gives $2^{32}=4\,294\,967\,296$ different addresses. IPv6 was introduced because the IPv4 addresses are not enough for the very large number of connected devices; it uses $128$ bits."),
          ans=r"$10101100.00010000.00000101.11001000$ ; $4\,294\,967\,296$ addresses",
          piege=r"Each byte must be written with eight digits: $5$ is $00000101$, not $101$."),
        S("b", P(r"A technical college in Ngaoundéré equips a computer room with $40$ computers and has to choose how to license an office suite.",
                 r"(i) Distinguish between freeware and open source software. (2 marks)",
                 r"(ii) A licence for one copy costs $12\,500$ FCFA. A site licence covering up to $60$ computers costs $400\,000$ FCFA. Calculate the cost of licensing the $40$ computers copy by copy, say which option is cheaper and by how much, and find the smallest number of copies for which the site licence is the cheaper option. (3 marks)",
                 r"(iii) State one consequence for the college of using copies of the software that are not licensed. (1 mark)"),
          ["software licensing and copyright"], "moyenne", 6,
          [(r"You say that freeware is free to use but its source code is not available and it cannot be modified", 1),
           (r"You say that open source software has its source code available, to study, modify and redistribute under its licence", 1),
           (r"You calculate $40\times12\,500=500\,000$ FCFA", 1), (r"You say that the site licence is cheaper by $100\,000$ FCFA", 1),
           (r"You find $\dfrac{400\,000}{12\,500}=32$, so the site licence is cheaper from $33$ copies", 1),
           (r"You state a consequence, for example a fine or legal action, no updates or support, or a risk of malware in copied software", 1)],
          r"Software licences define what the user may do with a program: freeware gives free use only, open source gives access to the source code; the cheaper licence is found by comparing the two total costs, and the break-even number of copies is the price of the site licence divided by the price of one copy, with equal cost at that number.",
          P(r"(i) Freeware is software that can be used at no cost, but the source code is kept by the author and users may not modify or redistribute it. Open source software is supplied with its source code, which users may study, modify and redistribute under the terms of its licence; it is often, but not always, free of charge.",
            r"(ii) Copy by copy: $40\times12\,500=500\,000$ FCFA. The site licence costs $400\,000$ FCFA, so it is cheaper by $500\,000-400\,000=100\,000$ FCFA. At $32$ copies the cost is $32\times12\,500=400\,000$ FCFA, equal to the site licence; at $33$ copies it is $412\,500$ FCFA. The site licence is cheaper from $33$ copies.",
            r"(iii) Using unlicensed copies breaks copyright law, so the college risks a fine or legal action; it also receives no updates or support, and copied software may carry malware."),
          ans=r"$500\,000$ FCFA ; site licence cheaper by $100\,000$ FCFA ; $33$ copies",
          piege=r"At exactly $32$ copies the two prices are equal, so the site licence is the cheaper option only from $33$ copies."),
        S("c", P(r"(i) Distinguish between RAM and ROM. (2 marks)",
                 r"(ii) A flash drive has a capacity of $8$ GB, with $1$ GB $=1024$ MB. Each photograph of the school open day takes $2.5$ MB. Calculate the greatest number of whole photographs that the drive can hold. (2 marks)",
                 r"(iii) State one reason why a computer needs secondary storage in addition to its main memory. (1 mark)"),
          ["computer hardware"], "faible", 5,
          [(r"You say that RAM is volatile read-write memory that holds the programs and data in use", 1),
           (r"You say that ROM is non-volatile and holds fixed instructions such as the start-up program", 1),
           (r"You convert $8\times1024=8192$ MB", 1), (r"You divide $\dfrac{8192}{2.5}=3276.8$ and give $3276$ photographs", 1),
           (r"You state a reason, for example the data must be kept when the power is off, or the capacity of main memory is too small", 1)],
          r"Main memory holds what the processor is using now and is limited in size, while secondary storage keeps programs and data permanently; the number of files that fit in a storage device is the capacity divided by the size of one file, in the same unit, rounded down to a whole number.",
          P(r"(i) RAM is volatile: it loses its content when the power is switched off, it can be read and written, and it holds the programs and data being used. ROM is non-volatile: its content is kept without power and is normally only read, and it holds fixed instructions such as the start-up program.",
            r"(ii) $8$ GB $=8\times1024=8192$ MB. Number of photographs $=\dfrac{8192}{2.5}=3276.8$, so the drive holds $3276$ whole photographs.",
            r"(iii) Main memory loses its content when the power is switched off and is too small for all the programs and files, so secondary storage (hard disk, flash drive) keeps the data permanently and in large quantity."),
          ans=r"$3276$ photographs",
          piege=r"The answer is rounded down: $3277$ photographs would need $8192.5$ MB, more than the drive holds."),
    ]))

    # ---- Exercice 5 : algorithm design, information systems, internet and web (17) ----
    ex.append(E("5", G, 17, "", [
        S("a", P(r"A cocoa cooperative uses the algorithm below to process the weights, in kg, of the bags brought by a farmer in one visit. The value $0$ ends the input.",
                 PSEUDO_5A,
                 r"(i) Complete a trace table for the input data $42, 65, 50, 18, 73, 0$ and state the values output. (3 marks)",
                 r"(ii) State the purpose of the value $0$ in this algorithm and give the name of such a value. (1 mark)",
                 r"(iii) Modify the algorithm so that it also outputs the average weight per bag, and say what could go wrong when the first value entered is $0$. (2 marks)"),
          ["ict algorithm design"], "moyenne", 6,
          [(r"You complete the trace table with the rows $(42, 42, 0)$, $(65, 107, 1)$, $(50, 157, 2)$, $(18, 175, 2)$, $(73, 248, 3)$ for $w$, `total` and `heavy`", 2),
           (r"You state the output $248$ and $3$", 1),
           (r"You say that $0$ marks the end of the data and is called a sentinel (rogue) value", 1),
           (r"You add a counter of bags and output `total / count`", 1),
           (r"You say that with no bag the division by zero must be avoided by testing the counter", 1)],
          r"A trace table follows each variable line by line for given data; a sentinel value ends a loop that reads an unknown number of inputs and is not part of the data, and an average needs a count of the items, which must be tested against zero before dividing.",
          P(r"(i) Trace table:",
            "| Input `w` | `total` | `heavy` |\n|---|---|---|\n| (start) | 0 | 0 |\n| 42 | 42 | 0 |\n| 65 | 107 | 1 |\n| 50 | 157 | 2 |\n| 18 | 175 | 2 |\n| 73 | 248 | 3 |\n| 0 | loop ends | |",
            r"The algorithm outputs `248` and `3`: the total weight is $248$ kg and $3$ bags weigh $50$ kg or more.",
            r"(ii) The value $0$ tells the algorithm that there is no more data, so the loop stops. It is not a weight and is not added to the total. Such a value is called a sentinel (or rogue, terminator) value.",
            r"(iii) A counter of bags is added and the average is output after the loop, with a test that avoids division by zero:",
            PSEUDO_5A_BIS,
            r"If the first value entered is $0$, no bag has been processed, so `count` is $0$ and the division `total / count` would be a division by zero; the test on `count` prevents this."),
          ans=r"`total` $=248$ and `heavy` $=3$",
          piege=r"The sentinel $0$ is read by the last `INPUT` but the loop stops before the lines that process it, so it is never added to `total`."),
        S("b", P(r"A chain of pharmacies in Douala uses a computer-based information system to manage its sales and its stock.",
                 r"(i) State four components of a computer-based information system. (2 marks)",
                 r"(ii) Distinguish between a transaction processing system and a management information system, giving one example of use of each in the pharmacy chain. (3 marks)",
                 r"(iii) State one way in which a good information system helps the managers of the chain. (1 mark)"),
          ["information systems in organisations"], "faible", 6,
          [(r"You state four components among hardware, software, data, people and procedures", 2),
           (r"You say that a transaction processing system records the daily routine operations, for example each sale at a till", 1),
           (r"You say that a management information system summarises the stored data into reports for managers, for example monthly sales of each pharmacy", 1),
           (r"You give a clear difference between the two, for example detailed and immediate against summarised and periodic", 1),
           (r"You state a way, for example reports of sales and stock help managers to decide what to order", 1)],
          r"An information system is made of the equipment, programs, data, people and rules that collect, store and process information for an organisation; systems are distinguished by their users and their output, from the recording of routine transactions to reports that support management decisions.",
          P(r"(i) Any four of: hardware, software, data, people, procedures.",
            r"(ii) A transaction processing system records the routine, day to day operations of the organisation as they happen, for example each sale entered at a till, and updates the stock. A management information system takes the data collected by the transaction systems and summarises it into reports for managers, for example a monthly report of the sales of each pharmacy. The first deals with detailed, immediate data; the second produces summaries over a period.",
            r"(iii) The reports show which products sell fast and which stocks are low, so managers decide earlier and with better information what to order and where to send it."),
          ans=r"Four components ; TPS records routine transactions ; MIS gives summary reports to managers"),
        S("c", P(r"The cooperative publishes the price of its cocoa on a web page at the address `https://www.cacao-mbouda.example/shop/prices.html`.",
                 r"(i) Identify the protocol, the domain name and the path to the file in this address. (3 marks)",
                 r"(ii) The site also lets buyers pay online. State two measures that protect an online payment. (2 marks)"),
          ["internet and web technologies"], "faible", 5,
          [(r"You identify the protocol `https` (the secure version of HTTP)", 1),
           (r"You identify the domain name `www.cacao-mbouda.example`", 1), (r"You identify the path and file `/shop/prices.html`", 1),
           (r"You state a first measure, for example encryption of the data with a secure connection (padlock)", 1),
           (r"You state a second measure, for example a password or a one-time code to confirm the buyer, or a firewall on the server", 1)],
          r"A web address is made of a protocol that says how the data is exchanged, a domain name that identifies the server and a path that locates the file on it; payments online are protected by keeping the data unreadable on the way and by checking who sends it.",
          P(r"(i) Protocol: `https` (HTTP with encryption). Domain name: `www.cacao-mbouda.example`. Path to the file: `/shop/prices.html`, that is the folder `shop` and the page `prices.html`.",
            r"(ii) Any two of: the payment data is encrypted during transfer (a secure connection with a padlock shown in the browser); the buyer is authenticated by a password or a one-time code; the server is protected by a firewall; the card details are not stored on the shop server."),
          ans=r"`https` ; `www.cacao-mbouda.example` ; `/shop/prices.html`"),
    ]))

    # ---- Exercice 6 : computer networks, network devices, hardware (17) ----
    ex.append(E("6", G, 17, "", [
        S("a", P(r"A lycée in Garoua has to choose between a client-server network and a peer-to-peer network for its $8$ administration computers.",
                 r"(i) Describe a client-server network. (2 marks)",
                 r"(ii) State two advantages of the client-server network over the peer-to-peer network. (2 marks)",
                 r"(iii) State two advantages for the school of networking its computers instead of using them separately. (2 marks)"),
          ["ict computer networks"], "faible", 6,
          [(r"You say that a client-server network has one or more servers that provide services such as files, printing or accounts", 1),
           (r"You say that the other computers, the clients, request the services from the server", 1),
           (r"You state two advantages, for example central backup and security, central management of users, more reliable access to shared files", 2),
           (r"You state two advantages of networking, for example sharing of files, sharing of printers and of an Internet connection", 2)],
          r"In a client-server network the resources are held and managed by dedicated servers that answer requests from client computers, whereas in a peer-to-peer network each computer is both a client and a server for the others; networking a set of computers mainly lets them share resources and communicate.",
          P(r"(i) A client-server network has at least one powerful computer, the server, that stores the shared files and supplies services such as printing, user accounts and e-mail. The other computers, the clients, send requests to the server and receive the results.",
            r"(ii) Any two of: data are stored and backed up centrally; security and user accounts are managed in one place; access to the shared files is more reliable and controlled; it is easier to manage as the network grows.",
            r"(iii) Any two of: files and data are shared between the offices; a printer or a scanner is shared; one Internet connection is shared; software is installed and updated centrally; messages are exchanged easily."),
          ans=r"Server provides services to clients ; central management ; sharing of resources"),
        S("b", P(r"(i) Distinguish between a hub and a switch. (2 marks)",
                 r"(ii) State two functions of a router. (2 marks)",
                 r"(iii) Switches with $8$ ports each are joined in a chain: each cable between two switches uses one port on each of them. Calculate the smallest number of switches needed to connect $30$ computers, each computer using one port. (2 marks)"),
          ["ict network devices", "ict computer networks"], "moyenne", 6,
          [(r"You say that a hub sends the data it receives to all its ports", 1),
           (r"You say that a switch reads the address of the destination and sends the data only to the port of the destination", 1),
           (r"You state two functions of a router, for example connecting different networks such as a LAN to the Internet, and forwarding packets by their IP address", 2),
           (r"You write that $n$ switches in a chain have $8n-2(n-1)=6n+2$ ports left for computers", 1), (r"You find $6n+2\geq30$, so $n=5$ switches", 1)],
          r"A hub repeats every signal to all its ports while a switch learns the address of the device on each port and delivers the data only where it is needed; a router links different networks and chooses the path of each packet; in a chain of switches every link cable uses up two ports.",
          P(r"(i) A hub broadcasts the data it receives to every port, so all the computers receive it and the traffic is shared by all. A switch reads the address of the destination in each frame and sends the data only to the port where the destination is connected.",
            r"(ii) Any two of: it connects two or more different networks, for example the school LAN and the Internet; it forwards packets according to their IP addresses; it chooses the best path for each packet; it can act as a gateway and as a firewall.",
            r"(iii) With $n$ switches in a chain there are $n-1$ link cables, using $2(n-1)$ ports. The ports left for computers are $8n-2(n-1)=6n+2$. We need $6n+2\geq30$, that is $n\geq\dfrac{28}{6}=4.67$, so $n=5$. Check: $4$ switches give $26$ ports, not enough; $5$ switches give $32$ ports."),
          ans=r"$5$ switches",
          piege=r"Multiplying $5\times8=40$ ports and dividing $30$ by $8$ gives $4$ switches: it forgets that each link cable uses two ports."),
        S("c", P(r"(i) Explain what is meant by firmware and give one example. (2 marks)",
                 r"(ii) A processor runs at a clock speed of $2.5$ GHz. A program of $1\,500\,000\,000$ instructions needs an average of $4$ clock cycles per instruction. Calculate the time taken to run the program. (2 marks)",
                 r"(iii) State one factor, other than the clock speed, that affects the performance of a computer. (1 mark)"),
          ["computer hardware"], "moyenne", 5,
          [(r"You say that firmware is permanent software stored in ROM or flash memory that controls a device", 1),
           (r"You give an example, such as the BIOS of a computer or the firmware of a router", 1),
           (r"You calculate the number of cycles $1\,500\,000\,000\times4=6\times10^{9}$", 1), (r"You divide by $2.5\times10^{9}$ cycles per second and obtain $2.4$ s", 1),
           (r"You state a factor, for example the size of the cache, the amount of RAM, the number of cores or the width of the bus", 1)],
          r"A processor with a clock speed of $f$ hertz performs $f$ cycles each second, so the time to run a program is the total number of clock cycles, which is the number of instructions times the cycles per instruction, divided by the clock speed.",
          P(r"(i) Firmware is software stored permanently in ROM or flash memory, built into a device to control its basic operation. Example: the BIOS of a computer, which starts the machine, or the firmware of a router.",
            r"(ii) Total cycles $=1\,500\,000\,000\times4=6\,000\,000\,000$. The clock speed is $2.5\ \mathrm{GHz}=2.5\times10^{9}$ cycles per second. Time $=\dfrac{6\times10^{9}}{2.5\times10^{9}}=2.4$ s.",
            r"(iii) Any one of: the size of the cache memory, the amount of RAM, the number of processor cores, the width of the data bus, the speed of the storage device."),
          ans=r"$2.4$ s",
          conseil=r"$2.5$ GHz is $2.5$ thousand million cycles each second: write the powers of ten explicitly to avoid an error of a factor $1000$."),
    ]))

    # ---- Exercice 7 : output devices, communication systems, systems analysis and design (17) ----
    ex.append(E("7", G, 17, "", [
        S("a", P(r"(i) A monitor shows $1280\times720$ pixels and each pixel uses $24$ bits of colour. Calculate the memory needed to hold one full screen image, in bytes and in MB to two decimal places ($1$ MB $=1\,000\,000$ bytes). (2 marks)",
                 r"(ii) State two differences between an inkjet printer and a laser printer. (2 marks)",
                 r"(iii) A toner cartridge costs $35\,000$ FCFA and prints $2500$ pages. An ink cartridge costs $15\,000$ FCFA and prints $500$ pages. Calculate the cost per page of each and the cost of printing $1200$ pages with each. (2 marks)"),
          ["ict output devices"], "moyenne", 6,
          [(r"You calculate $1280\times720=921\,600$ pixels and $921\,600\times3=2\,764\,800$ bytes ($24$ bits $=3$ bytes)", 1), (r"You convert to $2.76$ MB", 1),
           (r"You state two differences, for example inkjet sprays drops of liquid ink and laser fuses toner powder with a drum and heat; laser is faster; inkjet has a lower purchase price", 2),
           (r"You calculate the cost per page: $14$ FCFA for laser and $30$ FCFA for inkjet", 1),
           (r"You calculate $16\,800$ FCFA for laser and $36\,000$ FCFA for inkjet for $1200$ pages", 1)],
          r"The memory of a screen image is the number of pixels times the number of bytes per pixel, with eight bits in a byte; the running cost of a printer is the price of a cartridge divided by the number of pages it prints, multiplied by the number of pages to be printed.",
          P(r"(i) Pixels $=1280\times720=921\,600$. Each pixel needs $\dfrac{24}{8}=3$ bytes, so the image needs $921\,600\times3=2\,764\,800$ bytes $=2.76$ MB.",
            r"(ii) An inkjet printer forms the characters by spraying tiny drops of liquid ink onto the paper, while a laser printer uses a laser to draw the image on a drum, which attracts toner powder that is fused onto the paper by heat. A laser printer is faster and cheaper per page for large jobs; an inkjet printer is cheaper to buy and is better for small jobs or photographs.",
            r"(iii) Laser: $\dfrac{35\,000}{2500}=14$ FCFA per page, so $1200\times14=16\,800$ FCFA. Inkjet: $\dfrac{15\,000}{500}=30$ FCFA per page, so $1200\times30=36\,000$ FCFA. The laser printer is the cheaper to run."),
          ans=r"$2\,764\,800$ bytes $=2.76$ MB ; $16\,800$ FCFA (laser) and $36\,000$ FCFA (inkjet)",
          piege=r"The cost of one cartridge does not compare with the other directly: the two cartridges print a different number of pages, so the cost per page must be found first."),
        S("b", P(r"A trading company in Douala sends its contracts by e-mail instead of by post.",
                 r"(i) State two advantages of e-mail over ordinary post for sending a contract. (2 marks)",
                 r"(ii) A secretary sends $12$ documents of $3.5$ MB each as attachments over a link of $2$ Mbit/s. Calculate the time needed to send them, in seconds, taking $1$ byte $=8$ bits and $1$ MB $=1\,000\,000$ bytes. (2 marks)",
                 r"(iii) State one disadvantage of e-mail for sending confidential documents. (1 mark)"),
          ["ict communication systems"], "faible", 5,
          [(r"You state two advantages, for example the message arrives within seconds, it costs less, a copy is kept automatically, the same message goes to many people", 2),
           (r"You calculate the total $12\times3.5=42$ MB $=336$ Mbit", 1), (r"You divide $\dfrac{336}{2}=168$ s", 1),
           (r"You state a disadvantage, for example the message can be intercepted or sent to the wrong address", 1)],
          r"Electronic communication is faster and cheaper than the post and leaves a copy; the time to send several files is their total size in bits divided by the rate of the link in bits per second.",
          P(r"(i) Any two of: the e-mail arrives in seconds, while a letter takes days; it costs much less; the sender automatically keeps a copy; the same contract can be sent to several people at once; it can be sent from anywhere with an Internet connection.",
            r"(ii) Total size $=12\times3.5=42$ MB $=42\times8=336$ Mbit. Time $=\dfrac{336}{2}=168$ s, which is $2$ minutes $48$ seconds.",
            r"(iii) An e-mail passes through several servers and may be intercepted or read if it is not encrypted, and it may be sent to a wrong address by mistake."),
          ans=r"$168$ s",
          piege=r"The link is rated in megabits per second and the files in megabytes: the total must be multiplied by $8$ before dividing by $2$."),
        S("c", P(r"The cooperative plans to replace its paper payroll by a computerised payroll system, and a systems analyst is asked to develop it.",
                 r"(i) Name four stages of the systems development life cycle, in the order in which they are carried out. (2 marks)",
                 r"(ii) State two methods the analyst can use to find the facts about the present system, with one advantage of each. (2 marks)",
                 r"(iii) Compare direct changeover and parallel running as methods of changing over to the new system, and say which one is the safer for a payroll. (2 marks)"),
          ["systems analysis and design"], "moyenne", 6,
          [(r"You name four stages, for example investigation (feasibility study), analysis, design, implementation, evaluation and maintenance", 1),
           (r"You give them in a correct order", 1),
           (r"You state two methods with an advantage each, for example interviews give detailed answers and questionnaires reach many people quickly", 2),
           (r"You say that direct changeover replaces the old system at once, which is cheap but risky, and parallel running uses both systems for a time, which costs more but is safe", 1),
           (r"You say that parallel running is the safer for a payroll because the old system is still available if the new one fails", 1)],
          r"A new system is developed in ordered stages from the study of the present system to its maintenance after changeover; fact finding collects information from people and documents, and the method of changeover balances the cost and speed of the change against the risk of a failure.",
          P(r"(i) Investigation (feasibility study), analysis, design, implementation (including testing and changeover), evaluation and maintenance. Four of these, in this order, earn the marks; equivalent names are accepted.",
            r"(ii) Interviews: the analyst can ask follow-up questions and obtains detailed answers, but it takes time. Questionnaires: many people are reached quickly and at low cost, but the answers are less detailed. Observation: the analyst sees what really happens; document study: the forms and reports in use show the data to be processed.",
            r"(iii) In direct changeover the old system is stopped and the new one starts at once: it is cheap and quick but risky, because a fault leaves the organisation with no working system. In parallel running both systems run together for a period and their results are compared: it costs more because the work is done twice, but the old system is still there if the new one fails. For a payroll, which must be paid correctly on time, parallel running is the safer."),
          ans=r"Investigation, analysis, design, implementation ; parallel running is safer",
          piege=r"Testing the new system comes before the changeover, not after it: the stages are not interchangeable."),
    ]))

    # ---- Exercice 8 : logic gates, relational databases, database design (17) ----
    ex.append(E("8", G, 17, "", [
        S("a", P(r"The alarm of a grain store, with output `X`, sounds when the system is switched on (`S` = 1) and the door sensor (`D` = 1) or the window sensor (`W` = 1) is triggered.",
                 r"(i) Write a Boolean expression for `X` and complete its truth table for all the values of `S`, `D` and `W`. (4 marks)",
                 r"(ii) Use De Morgan's laws to write the expression of NOT `X` in terms of NOT `S`, NOT `D` and NOT `W`, and check it for `S` = 1, `D` = 0, `W` = 0. (2 marks)"),
          ["ict logic gates and boolean algebra"], "moyenne", 6,
          [(r"You write `X = S AND (D OR W)`", 1), (r"You list the eight combinations of `S`, `D` and `W`", 1),
           (r"You give the output column `0 0 0 0 0 1 1 1`", 2),
           (r"You write NOT `X` = NOT `S` OR (NOT `D` AND NOT `W`) by De Morgan", 1),
           (r"You check the case `S` = 1, `D` = 0, `W` = 0: `X` = 0 and both sides give 1", 1)],
          r"A condition stated in words is written with AND where both parts must hold and OR where either part is enough, and the truth table lists every combination of the inputs in order; De Morgan's laws turn the complement of an AND into an OR of complements and the complement of an OR into an AND of complements.",
          P(r"(i) The alarm needs the system on AND (door OR window), so `X = S AND (D OR W)`. The circuit, an OR gate on `D` and `W` followed by an AND gate with `S`, is shown below the table.",
            "| `S` | `D` | `W` | `X` |\n|---|---|---|---|\n| 0 | 0 | 0 | 0 |\n| 0 | 0 | 1 | 0 |\n| 0 | 1 | 0 | 0 |\n| 0 | 1 | 1 | 0 |\n| 1 | 0 | 0 | 0 |\n| 1 | 0 | 1 | 1 |\n| 1 | 1 | 0 | 1 |\n| 1 | 1 | 1 | 1 |",
            r"(ii) NOT `X` = NOT (`S AND (D OR W)`) = NOT `S` OR NOT (`D OR W`) = NOT `S` OR (NOT `D` AND NOT `W`). Check for `S` = 1, `D` = 0, `W` = 0: `X` = 1 AND (0 OR 0) = 0, so NOT `X` = 1. The right side gives NOT 1 OR (NOT 0 AND NOT 0) = 0 OR (1 AND 1) = 1. Both sides are 1."),
          ans=r"`X = S AND (D OR W)` ; `X` is 1 for three rows ; NOT `X` = NOT `S` OR (NOT `D` AND NOT `W`)",
          fig="circuit",
          piege=r"De Morgan's laws change AND into OR (and OR into AND) when the complement is distributed: NOT (`D OR W`) is NOT `D` AND NOT `W`, not NOT `D` OR NOT `W`."),
        S("b", P(r"A cooperative stores its data in two tables of a relational database.",
                 r"`FARMER(FarmerID, FarmerName, Village)`",
                 "| FarmerID | FarmerName | Village |\n|---|---|---|\n| F01 | Tchamba Paul | Bafang |\n| F02 | Nkeng Ruth | Mbouda |\n| F03 | Fotso Jean | Bafang |\n| F04 | Mbarga Alice | Mbouda |",
                 r"`DELIVERY(DeliveryID, FarmerID, Kg, DeliveryMonth)`",
                 "| DeliveryID | FarmerID | Kg | DeliveryMonth |\n|---|---|---|---|\n| D1 | F01 | 120 | Oct |\n| D2 | F02 | 80 | Oct |\n| D3 | F01 | 150 | Nov |\n| D4 | F03 | 60 | Nov |\n| D5 | F02 | 90 | Nov |\n| D6 | F04 | 200 | Nov |",
                 r"(i) Write an SQL query that lists the names of the farmers of the village of Bafang in alphabetical order. (2 marks)",
                 r"(ii) Write the result of the following query. (2 marks)",
                 "```\n" + SQL_8B_II + "\n```",
                 r"(iii) Write an SQL query that lists, without repetition and in alphabetical order, the names of the farmers who made at least one delivery of more than $100$ kg, and write its result. (2 marks)"),
          ["ict relational databases"], "moyenne", 6,
          [(r"You write `SELECT FarmerName FROM FARMER WHERE Village = 'Bafang'` with `ORDER BY FarmerName`", 1),
           (r"You do not forget the quotes and the sort, and the result lists Fotso Jean then Tchamba Paul", 1),
           (r"You give the result rows (Bafang, $210$) and (Mbouda, $290$)", 2),
           (r"You write a query joining the two tables on `FarmerID` with the condition `Kg > 100` and `DISTINCT`", 1),
           (r"You give the result Mbarga Alice then Tchamba Paul", 1)],
          r"A query that uses data from two tables joins them on the primary key and foreign key, then filters with a condition and sorts the result; to read the result of a grouping query, first keep the rows that satisfy the condition, then add the values of each group.",
          P(r"(i) " + "`" + SQL_8B_I + "`" + r" The result is: Fotso Jean, Tchamba Paul.",
            r"(ii) The query joins the two tables, keeps the deliveries of November (D3, D4, D5, D6) and totals the kilograms for each village. Bafang: D3 ($150$, Tchamba Paul) and D4 ($60$, Fotso Jean), $150+60=210$. Mbouda: D5 ($90$, Nkeng Ruth) and D6 ($200$, Mbarga Alice), $90+200=290$.",
            "| Village | SUM(Kg) |\n|---|---|\n| Bafang | 210 |\n| Mbouda | 290 |",
            r"(iii) The deliveries of more than $100$ kg are D1 ($120$, F01), D3 ($150$, F01) and D6 ($200$, F04). F01 appears twice, so `DISTINCT` is needed.",
            "```\n" + SQL_8B_III + "\n```",
            r"The result is: Mbarga Alice, Tchamba Paul."),
          ans=r"Fotso Jean, Tchamba Paul ; (Bafang, $210$) and (Mbouda, $290$) ; Mbarga Alice, Tchamba Paul",
          piege=r"The condition on the month is applied before the grouping: adding the kilograms of October deliveries as well would give $330$ for Bafang."),
        S("c", P(r"The library of a lycée lends books to students. A student may borrow many books during the year, and a book may be borrowed by many students over the years.",
                 r"(i) State the type of relationship between `STUDENT` and `BOOK` and explain why it cannot be implemented directly in a relational database. (2 marks)",
                 r"(ii) Show how the relationship is resolved by a third table: give its name, its attributes, its primary key and its foreign keys. (2 marks)",
                 r"(iii) State the purpose of referential integrity for this third table. (1 mark)"),
          ["ict database design"], "moyenne", 5,
          [(r"You state a many-to-many relationship and say that a single foreign key field holds only one value, so it cannot link a record to several records of the other table", 1),
           (r"You introduce a link table, for example `LOAN(StudentID, BookID, LoanDate)`, one record for each loan", 1),
           (r"You give a primary key that identifies a loan, for example (`StudentID`, `BookID`, `LoanDate`), with `StudentID` and `BookID` as foreign keys", 1),
           (r"You say that referential integrity forbids a loan that refers to a student or a book that does not exist", 1),
           (r"You explain that the many-to-many relationship becomes two one-to-many relationships, from `STUDENT` and from `BOOK` to `LOAN`", 1)],
          r"A many-to-many relationship between two entities is resolved by a link table whose records each refer to one record of each entity, so that the relationship becomes two one-to-many relationships; its key must identify each record of the link table, and referential integrity keeps every foreign key pointing to an existing record.",
          P(r"(i) The relationship is many-to-many. A foreign key field in one table holds a single value, so a student could be linked to one book only (or a book to one student) and the many links cannot be stored directly.",
            r"(ii) A link table is added, for example `LOAN(StudentID, BookID, LoanDate)`. Each record is one loan. `StudentID` is a foreign key to `STUDENT` and `BookID` is a foreign key to `BOOK`. The primary key is the combination (`StudentID`, `BookID`, `LoanDate`): the date is included because the same student may borrow the same book again later. The many-to-many relationship is now two one-to-many relationships: one student has many loans, and one book has many loans.",
            r"(iii) Referential integrity makes sure that every `StudentID` and `BookID` in `LOAN` matches an existing record in `STUDENT` and `BOOK`, so a loan cannot refer to a student or a book that does not exist, and a book that has loans cannot be deleted by mistake."),
          ans=r"Many-to-many ; link table `LOAN(StudentID, BookID, LoanDate)`",
          conseil=r"The key of the link table is built from the keys of the two linked tables: this is why they are also foreign keys."),
    ]))

    return ex
