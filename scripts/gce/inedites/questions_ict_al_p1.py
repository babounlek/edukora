r"""Les 50 QCM de l'epreuve inedite GCE A Level ICT Paper 1 n.1 (50 x 1 point, 90 min).

Structure mesuree sur les Paper 1 reels 2025 et 2026 (un seul JSON de 50 questions chacun) : 50 questions a meilleure reponse, quatre options a) a d), themes
melanges (materiel, peripheriques, securite, formats, systemes d'information, transmission, reseaux, logiciels, programmation, numeration, bases de donnees,
tableur, projet, etc.), enonces courts, la moitie environ factuelle. Ici : une vingtaine de questions a calcul ou trace verifiables par programme (numeration,
taille de fichier, debit, tableur, tables de verite, traces, requetes SQL executees avec sqlite3, chemin critique) et une trentaine de questions factuelles
de programme (faits sans date ni prix). Aucune donnee, aucun enonce, aucun jeu d'options repris d'un sujet reel.
Chaque question : enonce, bonne option, trois distracteurs avec l'erreur type qui y mene, rappel (un seul paragraphe), resolution, valeur de controle recalculee par
verifier_reponses_ict_al_p1.py. Les lettres des cles sont placees par le GENERATEUR (13/13/12/12, jamais trois de suite).
Chaines BRUTES (r"...") : une commande a backslash simple dans une chaine ordinaire devient un caractere de controle. Le code est en `backticks`.
"""

QS = []


def Q(themes, diff, stem, key, dist, rappel, sol, val=None, conseil=None):
    BS = chr(92)
    stem, key = stem.replace(BS + '"', '"'), key.replace(BS + '"', '"')
    dist = [(d[0].replace(BS + '"', '"'), d[1]) for d in dist]
    assert len(dist) == 3 and all(len(d) == 2 for d in dist), stem[:40]
    texts = [key] + [d[0] for d in dist]
    assert len(set(texts)) == 4, ("options en double", stem[:50])
    assert "\n\n" not in rappel, "rappel : un seul paragraphe"
    QS.append(dict(kind="ba", themes=themes, diff=diff, stem=stem, key=key, dist=dist, rappel=rappel, sol=sol, val=val, conseil=conseil))


def questions():
    return QS


# 1
Q(["computer hardware"], "faible",
  r"A processor has an address bus with 12 lines. How many different memory locations can it address?",
  r"4096",
  [(r"12", r"counts the lines of the bus instead of the number of combinations they can form"),
   (r"2048", r"uses 2 to the power 11, one line fewer than the bus really has"),
   (r"144", r"squares the number of lines instead of raising 2 to that power")],
  r"Each line of the address bus carries one bit, so a bus of n lines can form 2 to the power n different addresses, and each address selects one memory location.",
  r"With n = 12 lines the number of addresses is 2 x 2 x ... x 2 (twelve times) = 4096.",
  4096)
# 2
Q(["ict number systems"], "faible",
  r"Which is the hexadecimal equivalent of the binary number `10110110`?",
  r"`B6`",
  [(r"`6B`", r"reads the two groups of four bits in the wrong order"),
   (r"`A6`", r"reads the group 1011 as ten instead of eleven"),
   (r"`182`", r"writes the decimal value of the number as if it were hexadecimal digits")],
  r"Split a binary number into groups of four bits from the right; each group is one hexadecimal digit, with ten to fifteen written A to F.",
  r"`1011` is eleven, that is `B`, and `0110` is six, that is `6`, so the number is `B6`. In decimal it is 11 x 16 + 6 = 182, but the question asks for the hexadecimal form.",
  "B6")
# 3
Q(["input devices and data capture"], "faible",
  r"An examination board scans answer sheets on which candidates shade small boxes with a pencil. Which method of data capture reads the position of the shaded marks?",
  r"Optical mark recognition",
  [(r"Optical character recognition", r"takes the device that turns printed or typed characters into text for the one that detects marks in fixed positions"),
   (r"Magnetic ink character recognition", r"takes the device used for the characters printed in magnetic ink at the foot of cheques"),
   (r"Barcode reading", r"takes the device that decodes a pattern of bars for the one that detects pencil marks")],
  r"Optical mark recognition detects whether a mark is present at a fixed position on a form, which makes it fast for multiple-choice answer sheets and ballot papers.",
  r"The candidate gives an answer only by shading a box, so the computer needs the position of the mark, not a character shape and not a bar pattern. This is optical mark recognition.")
# 4
Q(["data security and privacy"], "moyenne",
  r"Each letter of the plain text `NETWORK` is replaced by the letter 5 places further along the alphabet, and Z is followed by A. What is the cipher text?",
  r"`SJYBTWP`",
  [(r"`IZORJMF`", r"moves each letter 5 places backwards instead of forwards"),
   (r"`QHWZRUN`", r"uses a shift of 3 instead of the shift of 5 that was given"),
   (r"`PWTBYJS`", r"shifts correctly but then writes the letters in reverse order")],
  r"A substitution cipher of the Caesar type replaces each letter by the one a fixed number of places further along the alphabet, going back to A after Z; decryption shifts back by the same amount.",
  r"N becomes S, E becomes J, T becomes Y, W becomes B (after Z comes A), O becomes T, R becomes W and K becomes P, which gives `SJYBTWP`.",
  "SJYBTWP")
# 5
Q(["spreadsheet modelling"], "moyenne",
  r"The formula `=$B2*C$1+D2` is typed in cell E2 and copied to cell G4. Which formula is now in cell G4?",
  r"`=$B4*E$1+F4`",
  [(r"`=D4*E3+F4`", r"ignores the dollar signs and moves every reference two columns and two rows"),
   (r"`=$B2*C$1+D2`", r"treats the whole formula as fixed and copies it without any change"),
   (r"`=$B4*C$1+F4`", r"keeps column C in the second reference although only its row is locked")],
  r"When a formula is copied, a relative reference moves by the same number of rows and columns as the cell, while a dollar sign locks the column letter or the row number that follows it.",
  r"G4 is two columns to the right and two rows below E2. `$B2` keeps column B and its row moves to 4, giving `$B4`. `C$1` keeps row 1 and its column moves to E, giving `E$1`. `D2` moves both ways and gives `F4`.")
# 6
Q(["file formats and extensions"], "faible",
  r"A lossless compression utility reduces a text file of 12 MB to 3 MB. By what percentage is the file size reduced?",
  r"75%",
  [(r"25%", r"gives the compressed size as a percentage of the original size instead of the reduction"),
   (r"400%", r"divides the original size by the compressed size and writes the ratio as a percentage"),
   (r"9%", r"takes the 9 MB that was saved and writes it with a percentage sign")],
  r"The percentage reduction is the amount saved divided by the original size, multiplied by 100.",
  r"The amount saved is 12 - 3 = 9 MB, so the reduction is 9 / 12 x 100 = 75%. The compressed file is 25% of the original, which is a different quantity.",
  75)
# 7
Q(["ict transmission modes"], "moyenne",
  r"A file of 45 MB is sent over a link that carries 30 Mb per second without any interruption. Take 1 byte = 8 bits and ignore all overheads. How long does the transfer last?",
  r"12 s",
  [(r"1.5 s", r"divides the number of megabytes by the rate and forgets to convert bytes into bits"),
   (r"0.083 s", r"divides the rate by the size in megabits instead of the size by the rate"),
   (r"360 s", r"converts the size into megabits and then forgets to divide by the rate")],
  r"Transfer time is the quantity of data in bits divided by the rate in bits per second, so a size given in bytes must first be multiplied by 8.",
  r"The size is 45 x 8 = 360 Mb. At 30 Mb per second the time is 360 / 30 = 12 s.",
  12.0)
# 8
Q(["ict programming constructs"], "faible",
  "What is output when this algorithm is run?\n\n```text\ntotal ← 0\nFOR i ← 1 TO 6\n    IF i MOD 2 = 0 THEN\n        total ← total + i * i\n    ENDIF\nNEXT i\nOUTPUT total\n```",
  r"56",
  [(r"91", r"adds the squares of all the values of i instead of only the even ones"),
   (r"12", r"adds the even values of i but forgets to square them"),
   (r"35", r"selects the odd values of i instead of the even ones")],
  r"A trace table follows the loop one pass at a time; `MOD 2 = 0` is true only for even values, so the instruction under IF runs only on those passes.",
  r"The test is true for i = 2, 4 and 6, so total becomes 4, then 4 + 16 = 20, then 20 + 36 = 56, which is output once the loop has finished.",
  56)
# 9
Q(["ict computer networks"], "faible",
  r"Which of these is a valid IPv4 address?",
  r"`172.16.254.1`",
  [(r"`192.168.1.256`", r"accepts the value 256 although each part of an IPv4 address is a number from 0 to 255"),
   (r"`10.0.0`", r"accepts three groups although an IPv4 address has four"),
   (r"`192.168.1.1.5`", r"accepts five groups although an IPv4 address has four")],
  r"An IPv4 address is a 32-bit number written as four decimal groups, each of one byte, so each group is a whole number from 0 to 255 and they are separated by dots.",
  r"`172.16.254.1` has four groups, all between 0 and 255. The other three have a group equal to 256, only three groups or five groups.")
# 10
Q(["ict logic gates and boolean algebra"], "moyenne",
  r"A logic circuit gives the output `X = NOT (A AND B) OR C`. For which combination of inputs is X equal to 0?",
  r"A = 1, B = 1, C = 0",
  [(r"A = 1, B = 0, C = 0", r"reads the bubble gate as a NOR rather than a NAND"),
   (r"A = 0, B = 0, C = 0", r"drops the NOT and evaluates (A AND B) OR C"),
   (r"A = 1, B = 1, C = 1", r"uses AND instead of OR for the last gate")],
  r"An OR gate gives 0 only when both of its inputs are 0, so X is 0 only if the NAND part is 0 and C is 0; the NAND part is 0 only when both A and B are 1.",
  r"`NOT (A AND B)` is 0 only for A = 1 and B = 1. X is the OR of that value with C, so C must also be 0. Every other combination gives X = 1.")
# 11
Q(["information systems in organisations"], "faible",
  r"A bank manager uses a system that combines sales figures, costs and market forecasts so that different 'what if' scenarios can be tried before choosing the site of a new branch. This is an example of a",
  r"decision support system",
  [(r"transaction processing system", r"takes the system that records day-to-day operations such as deposits and withdrawals"),
   (r"management information system", r"takes the system that produces routine summary reports from operational data"),
   (r"office automation system", r"takes the system for documents, messages and schedules")],
  r"A decision support system lets managers model scenarios and test alternatives on collected data; it supports one-off decisions, unlike systems that record transactions or print regular reports.",
  r"The manager does not need a record of an operation or a routine report. The need is to compare scenarios with 'what if' questions, which is the work of a decision support system.")
# 12
Q(["ict database concepts"], "moyenne",
  "The table `student` is shown below. A value of NULL means that no mark was recorded.\n\n| sid | name | form | mark |\n|---|---|---|---|\n| 1 | Ada | L6 | 72 |\n| 2 | Bello | L6 | 48 |\n| 3 | Chi | L5 | 65 |\n| 4 | Dina | L6 | NULL |\n| 5 | Emeka | L5 | 80 |\n| 6 | Fon | L5 | 55 |\n| 7 | Gina | L6 | 66 |\n| 8 | Ivo | L6 | 90 |\n\nWhat does this query return?\n\n```sql\nSELECT form, COUNT(*) FROM student WHERE mark >= 60 GROUP BY form ORDER BY form;\n```",
  r"L5: 2 and L6: 3",
  [(r"L5: 3 and L6: 5", r"ignores the WHERE clause and counts every student of each form"),
   (r"L5: 1 and L6: 1", r"counts the students whose mark is below 60 instead of those at or above it"),
   (r"L5: 2 and L6: 4", r"counts Dina although her NULL mark does not satisfy the condition")],
  r"WHERE filters the rows before they are grouped, a comparison with NULL is never true, and COUNT(*) then counts the rows that remain in each group.",
  r"Marks of at least 60 are Chi (65) and Emeka (80) in L5, and Ada (72), Gina (66) and Ivo (90) in L6. Dina's NULL mark fails the test. The result is L5: 2 and L6: 3.")
# 13
Q(["computer crime and malware"], "faible",
  r"A malicious program copies itself from one computer to another across a network without needing to be attached to a host file or to be opened by a user. This program is a",
  r"worm",
  [(r"Trojan horse", r"takes the program that looks useful but does not copy itself"),
   (r"spyware", r"takes the program that secretly collects information about the user"),
   (r"ransomware", r"takes the program that locks or encrypts files until a payment is made")],
  r"A worm is a self-replicating program that spreads through network connections on its own, whereas a virus needs a host file and a Trojan horse needs the user to run it.",
  r"The key features are self-copying and spreading across the network with no host file and no action by the user. Only a worm has both.")
# 14
Q(["ict number systems"], "moyenne",
  r"What is the 8-bit two's complement representation of the denary number -45?",
  r"`11010011`",
  [(r"`11010010`", r"inverts the bits of 45 but forgets to add 1"),
   (r"`10101101`", r"sets the sign bit of the magnitude 45, which is sign and magnitude"),
   (r"`11010001`", r"adds 1 to 45 before inverting the bits instead of after")],
  r"To write a negative number in two's complement, write the positive number in binary, invert every bit, then add 1 to the result.",
  r"45 is `00101101`. Inverting gives `11010010`. Adding 1 gives `11010011`. Check: `11010011` is 128 + 64 + 16 + 2 + 1 = 211, and 211 - 256 = -45.",
  "11010011")
# 15
Q(["ict operating systems"], "faible",
  r"Which function of an operating system makes several programs appear to run at the same time by sharing the processor between them?",
  r"Multitasking",
  [(r"Spooling", r"takes the queueing of print jobs on disk for the sharing of the processor"),
   (r"Virtual memory", r"takes the use of disk space as an extension of RAM for the sharing of the processor"),
   (r"File compression", r"takes the reduction of file size for the sharing of the processor")],
  r"Multitasking lets the operating system give each running program a short slice of processor time in turn, so that they seem to progress together.",
  r"The processor runs only a few instructions for one program before the operating system switches to another. This sharing of the processor is multitasking; the other options concern printing, memory and file size.")
# 16
Q(["html and css"], "faible",
  r"Which line of HTML displays the word Library as a hyperlink to the page `books.html`?",
  r"`<a href=\"books.html\">Library</a>`",
  [(r"`<link href=\"books.html\">Library</link>`", r"uses the tag placed in the head to attach external resources such as style sheets"),
   (r"`<a src=\"books.html\">Library</a>`", r"uses the src attribute, which embeds a file, in place of href"),
   (r"`<href=\"books.html\">Library</href>`", r"treats href as a tag although it is an attribute")],
  r"A hyperlink is made with the anchor tag `a`, whose `href` attribute holds the address of the destination, and the text between the opening and closing tags is what the user clicks.",
  r"Only the first line has an anchor tag with an `href` attribute. The `link` tag belongs in the head, `src` is used by images and scripts, and `href` is never a tag.")
# 17
Q(["ict project management"], "moyenne",
  "A project is made of seven tasks. Task durations and dependencies are shown below.\n\n| Task | Duration (days) | Depends on |\n|---|---|---|\n| A | 3 | none |\n| B | 2 | none |\n| C | 3 | A |\n| D | 5 | A, B |\n| E | 3 | C, D |\n| F | 2 | D |\n| G | 1 | E, F |\n\nWhat is the shortest possible duration of the project?",
  r"12 days",
  [(r"10 days", r"follows only the path A, C, E, G, which is not the longest"),
   (r"19 days", r"adds the durations of all the tasks as if they were done one after another"),
   (r"11 days", r"follows the path A, D, F, G and misses the longer path through E")],
  r"The shortest duration of a project is the length of its longest path from start to finish, the critical path, because tasks that depend on each other cannot overlap.",
  r"The paths are A, C, E, G = 10 days; A, D, E, G = 12 days; A, D, F, G = 11 days; B, D, E, G = 11 days; B, D, F, G = 10 days. The longest is A, D, E, G, so the project lasts 12 days.",
  12)
# 18
Q(["ict transmission media"], "faible",
  r"Which transmission medium carries data as pulses of light and is not affected by electromagnetic interference?",
  r"Fibre-optic cable",
  [(r"Coaxial cable", r"believes the copper core is shielded enough to be immune to interference"),
   (r"Unshielded twisted pair cable", r"takes the cable whose twisted pairs only reduce interference for one that is immune to it"),
   (r"Microwave link", r"believes radio waves cannot be disturbed by other electromagnetic sources")],
  r"A fibre-optic cable sends light along a glass or plastic core, so it is not disturbed by electrical noise, whereas copper cables and radio links carry electrical or radio signals that can be disturbed.",
  r"Only the fibre-optic cable carries light rather than an electrical or radio signal, so no electromagnetic source can alter the data it carries.")
# 19
Q(["spreadsheet modelling"], "faible",
  r"Cells B2 to B9 of a worksheet contain 45, 62, 50, 78, 91, 50, 33 and 67. What value does the formula `=COUNTIF(B2:B9,\">=50\")` display?",
  r"6",
  [(r"4", r"leaves out the two values that are equal to 50, as if the test were >50"),
   (r"8", r"counts every cell of the range and ignores the condition"),
   (r"2", r"counts the values below 50 instead of the ones that satisfy the test")],
  r"`COUNTIF` counts the cells of a range that meet a condition, and the operator >= includes the values that are exactly equal to the limit.",
  r"The values of at least 50 are 62, 50, 78, 91, 50 and 67, which makes six cells.",
  6)
# 20
Q(["computer hardware"], "faible",
  r"In the fetch-decode-execute cycle, which register holds the address of the next instruction and is increased after each fetch?",
  r"Program counter",
  [(r"Memory data register", r"takes the register that holds the data or instruction just read from memory"),
   (r"Accumulator", r"takes the register that holds the results of the arithmetic and logic unit"),
   (r"Current instruction register", r"takes the register that holds the instruction being decoded")],
  r"The program counter holds the address of the next instruction and is incremented after each fetch, so the processor moves through a program in order unless a jump changes it.",
  r"The register that is increased after each fetch and gives the address of the next instruction is the program counter. The others hold data, results or the instruction being decoded.")
# 21
Q(["ict data validation"], "elevee",
  r"A code uses a modulus 11 check digit. Each of the nine digits is multiplied by a weight, 10 for the first digit down to 2 for the ninth; the products are added; the check digit is the number that must be added to the total to reach the next multiple of 11. What is the check digit for `735192480`?",
  r"5",
  [(r"6", r"gives the remainder of the division by 11 as the check digit"),
   (r"2", r"works to a multiple of 10 instead of a multiple of 11"),
   (r"0", r"uses the weights 9 down to 1 instead of 10 down to 2")],
  r"A check digit is calculated from the other digits by a fixed rule, so that a mistyped digit or two swapped digits is detected when the rule is applied again to the whole code.",
  r"The total is 7 x 10 + 3 x 9 + 5 x 8 + 1 x 7 + 9 x 6 + 2 x 5 + 4 x 4 + 8 x 3 + 0 x 2 = 248. As 248 = 22 x 11 + 6, the next multiple of 11 is 253 and the check digit is 11 - 6 = 5.",
  5)
# 22
Q(["ict network devices"], "faible",
  r"Which network device forwards a frame only to the port to which the destination computer is connected, using the MAC address of that computer?",
  r"Switch",
  [(r"Hub", r"takes the device that repeats every frame to all of its ports"),
   (r"Repeater", r"takes the device that only regenerates a weakened signal"),
   (r"Router", r"takes the device that forwards packets between networks using IP addresses")],
  r"A switch learns the MAC address of the device on each port and sends a frame only to the port of its destination, which reduces unnecessary traffic compared with a hub.",
  r"Sending a frame to one port only, chosen from the MAC address, is the work of a switch. A hub copies the frame to all ports, a repeater only boosts the signal and a router works between networks with IP addresses.")
# 23
Q(["systems analysis and design"], "faible",
  r"A company keeps its old payroll system running alongside the new one for a month and compares the results of both. Which method of changeover is this?",
  r"Parallel running",
  [(r"Direct changeover", r"takes the method where the old system is stopped and the new one starts at once"),
   (r"Phased implementation", r"takes the method where the new system is introduced one part at a time"),
   (r"Pilot running", r"takes the method where the new system is tried in one branch only")],
  r"In parallel running both systems process the same data for a time, which lets the results be compared and gives a fallback, at the cost of doing the work twice.",
  r"Two systems working on the same payroll with the results compared is the definition of parallel running.")
# 24
Q(["ict programming constructs"], "moyenne",
  "What is output when this algorithm is run?\n\n```text\nn ← 4827\ns ← 0\nWHILE n > 0\n    s ← s + (n MOD 10)\n    n ← n DIV 10\nENDWHILE\nOUTPUT s\n```",
  r"21",
  [(r"4", r"outputs the number of passes of the loop instead of the sum"),
   (r"7284", r"builds the digits in reverse order instead of adding them"),
   (r"133", r"adds the squares of the digits instead of the digits")],
  r"`MOD 10` gives the last digit of a whole number and `DIV 10` removes it, so a loop that repeats them handles every digit from the right.",
  r"The passes take the digits 7, 2, 8, 4 so that s becomes 7, 9, 17 and then 21 when n reaches 0. The output is 21.",
  21)
# 25
Q(["software licensing and copyright"], "faible",
  r"A school buys one single-user licence for a program and installs it on 40 computers. This is an example of",
  r"software piracy",
  [(r"the use of shareware", r"takes software that may be tried for a limited time for the unlicensed copying of paid software"),
   (r"the use of open-source software", r"takes software whose licence allows the copying for software whose licence does not"),
   (r"the use of a site licence", r"takes an agreement that would have to be bought for the 40 computers")],
  r"A licence gives the buyer the right to use the software under stated conditions, and copying or installing it beyond those conditions is software piracy.",
  r"The licence covers one user, so the 39 other installations break the licence terms. A site licence would allow them but was not bought, and the copying is not allowed by shareware or open-source terms.")
# 26
Q(["e-commerce and e-services"], "faible",
  r"A wholesaler sells goods through its website to shop owners who resell them to the public. This type of e-commerce is",
  r"business-to-business",
  [(r"business-to-consumer", r"takes the sale to the final user for a sale to another business"),
   (r"consumer-to-consumer", r"takes the sale between private individuals"),
   (r"consumer-to-business", r"takes the sale of a service by an individual to a company")],
  r"E-commerce is named after the two parties of the sale: business-to-business is trade between companies, business-to-consumer is a sale to the final customer and consumer-to-consumer is trade between individuals.",
  r"Both the seller and the buyers are businesses, since the shop owners buy in order to resell. The type is business-to-business.")
# 27
Q(["data security and privacy"], "moyenne",
  r"A full backup is made on Sunday night and an incremental backup (the files changed since the previous backup) on each of Monday, Tuesday and Wednesday nights. The disk fails on Thursday morning. How many backup sets are needed to restore the data?",
  r"4",
  [(r"1", r"uses only the most recent backup as if it held everything"),
   (r"2", r"uses the full backup and the last incremental one, as for a differential backup"),
   (r"3", r"uses the three incremental backups and forgets the full backup")],
  r"An incremental backup copies only what changed since the previous backup of any kind, so a restore needs the last full backup and then every incremental backup made after it, in order.",
  r"The full backup holds the starting state, and each incremental set adds only one day of changes. All of Sunday, Monday, Tuesday and Wednesday are needed, which makes 4 sets.",
  4)
# 28
Q(["ict transmission modes"], "elevee",
  r"An asynchronous serial link sends each character as 8 data bits plus 1 start bit and 1 stop bit, at 9600 bits per second. How long does it take to send 6000 characters?",
  r"6.25 s",
  [(r"5 s", r"counts only the 8 data bits of each character and ignores the start and stop bits"),
   (r"5.625 s", r"adds the start bit but forgets the stop bit"),
   (r"0.625 s", r"treats each character as one bit instead of ten")],
  r"In asynchronous transmission every character is framed by a start bit and a stop bit, so the number of bits actually sent per character is larger than the number of data bits, and the time is the total number of bits divided by the rate.",
  r"Each character uses 8 + 1 + 1 = 10 bits, so 6000 characters need 60 000 bits. At 9600 bits per second the time is 60 000 / 9600 = 6.25 s.",
  6.25)
# 29
Q(["ict database concepts"], "faible",
  r"In a relational database, a field of one table that holds values of the primary key of another table is called a",
  r"foreign key",
  [(r"composite key", r"takes a primary key made of two or more fields"),
   (r"candidate key", r"takes a field that could be chosen as the primary key of its own table"),
   (r"secondary index", r"takes a structure that speeds up searches but does not link tables")],
  r"A foreign key is a field whose values must match values of the primary key of another table, and this is how the tables of a relational database are linked.",
  r"The field that refers to the primary key of another table is a foreign key. A composite key and a candidate key concern the keys of the table itself.")
# 30
Q(["spreadsheet modelling"], "moyenne",
  r"Cells A2 to A7 contain East, West, East, North, West and East. Cells B2 to B7 contain 120, 90, 60, 150, 30 and 45. What does `=SUMIF(A2:A7,\"East\",B2:B7)` display?",
  r"225",
  [(r"3", r"counts the cells that contain East instead of adding the matching values"),
   (r"495", r"adds every value of column B and ignores the condition"),
   (r"75", r"averages the matching values instead of adding them")],
  r"`SUMIF` adds the cells of the sum range that lie in the same rows as the cells of the criteria range that meet the condition.",
  r"East appears in A2, A4 and A7, whose values in column B are 120, 60 and 45. Their sum is 225.",
  225)
# 31
Q(["ict health and safety"], "faible",
  r"A data-entry clerk types for several hours every day and feels pain in the wrists and fingers. Which measure best reduces this risk?",
  r"Regular breaks and a wrist rest",
  [(r"An anti-glare screen filter", r"uses a measure that reduces eye strain for a problem of the wrists"),
   (r"Cable ducts along the floor", r"uses a measure that prevents tripping for a problem of the wrists"),
   (r"A chair with lumbar support", r"uses a measure that helps the lower back for a problem of the wrists")],
  r"Repetitive strain injury comes from repeating the same small movements for long periods; the remedies are rests from the keyboard and a keyboard set so that the wrists stay straight and supported.",
  r"The pain is in the wrists and fingers, so the best measure acts on the repeated movements: regular breaks and a wrist rest. The others deal with eyes, falls and the back.")
# 32
Q(["ict logic gates and boolean algebra"], "moyenne",
  r"A circuit gives the output `X = (A XOR B) AND (NOT C)`. For how many of the eight possible combinations of A, B and C is X equal to 1?",
  r"2",
  [(r"3", r"reads XOR as OR, which is also true when A and B are both 1"),
   (r"4", r"forgets the condition on C and counts the combinations for which A XOR B is 1"),
   (r"6", r"reads the last gate as OR NOT C instead of AND NOT C")],
  r"An XOR gate is 1 only when its two inputs differ, an AND gate needs both of its inputs at 1, and a truth table with three inputs has 2 x 2 x 2 = 8 rows to examine.",
  r"A XOR B is 1 for (A, B) = (0, 1) and (1, 0). X also needs C = 0. The combinations are 010 and 100, which makes 2.",
  2)
# 33
Q(["ict programming paradigms"], "faible",
  r"In object-oriented programming, the mechanism by which a new class takes the attributes and methods of an existing class is called",
  r"inheritance",
  [(r"encapsulation", r"takes the grouping of data and the methods that use it inside a class with restricted access"),
   (r"polymorphism", r"takes the ability of one method name to behave differently for different classes"),
   (r"instantiation", r"takes the creation of an object from a class")],
  r"Inheritance lets a subclass reuse the attributes and methods of a parent class and add or change some of them, which avoids writing the same code twice.",
  r"A class that obtains the attributes and methods of another one uses inheritance. Encapsulation, polymorphism and instantiation describe other features of objects.")
# 34
Q(["internet and web technologies"], "faible",
  r"In the web address `https://www.school.cm:8080/library/books.html?id=42`, the part `/library/books.html` is the",
  r"path to the resource on the server",
  [(r"protocol used to fetch the page", r"takes the first part of the address, before the colon"),
   (r"domain name of the web server", r"takes the part that names the server, which comes before the path"),
   (r"query string sent to the server", r"takes the part that follows the question mark")],
  r"A web address is made of the protocol, the domain name (with an optional port number), the path to the resource on the server and, after a question mark, an optional query string.",
  r"`https` is the protocol, `www.school.cm` the domain name, `8080` the port, `/library/books.html` the path to the file on the server and `id=42` the query string.")
# 35
Q(["ict database concepts"], "moyenne",
  "Two tables are shown below.\n\n`customer`\n\n| cid | cname | town |\n|---|---|---|\n| 1 | Ama | Douala |\n| 2 | Bih | Buea |\n| 3 | Cyrille | Douala |\n| 4 | Dora | Limbe |\n\n`orders`\n\n| oid | cid | amount |\n|---|---|---|\n| 101 | 1 | 5000 |\n| 102 | 1 | 2500 |\n| 103 | 3 | 4000 |\n| 104 | 2 | 1500 |\n| 105 | 3 | 3000 |\n\nWhat does this query return?\n\n```sql\nSELECT c.cname, SUM(o.amount) FROM customer c JOIN orders o ON c.cid = o.cid\nGROUP BY c.cname ORDER BY SUM(o.amount) DESC LIMIT 1;\n```",
  r"Ama, 7500",
  [(r"Bih, 1500", r"sorts the totals in ascending order instead of descending"),
   (r"Ama, 5000", r"takes the largest single order instead of the total of each customer"),
   (r"Ama, 2", r"counts the orders of the customer instead of adding the amounts")],
  r"JOIN pairs each order with its customer, GROUP BY gives one row per customer with the total of the amounts, ORDER BY ... DESC puts the largest total first and LIMIT 1 keeps that row only.",
  r"The totals are Ama 5000 + 2500 = 7500, Bih 1500 and Cyrille 4000 + 3000 = 7000; Dora has no order and does not appear in the join. The largest is Ama with 7500.")
# 36
Q(["ict number systems"], "moyenne",
  r"What is the sum of the hexadecimal numbers `3F` and `2D`?",
  r"`6C`",
  [(r"`5C`", r"forgets to carry 1 to the next column after F + D"),
   (r"`6D`", r"gives F the value 16 instead of 15"),
   (r"`108`", r"adds the two numbers in denary and writes the denary total")],
  r"In hexadecimal addition a column total of 16 or more gives a carry of 1 to the next column, and the letters A to F stand for ten to fifteen.",
  r"F + D = 15 + 13 = 28 = 16 + 12, so write `C` and carry 1. Then 3 + 2 + 1 = 6. The sum is `6C`, that is 63 + 45 = 108 in denary.",
  "6C")
# 37
Q(["ict programming constructs"], "moyenne",
  "What is output when this algorithm is run?\n\n```text\nx ← 3\nREPEAT\n    x ← x * 2\nUNTIL x > 20\nOUTPUT x\n```",
  r"24",
  [(r"12", r"outputs the value before the last doubling"),
   (r"3", r"believes that the test is made first and that the body never runs"),
   (r"48", r"makes one pass too many after the condition is already true")],
  r"A REPEAT ... UNTIL loop runs its body once before it tests the condition, and it stops as soon as the condition is true.",
  r"The passes give x = 6, 12 and then 24. The test `x > 20` is false for 6 and 12, and true for 24, so the loop stops and 24 is output.",
  24)
# 38
Q(["input devices and data capture"], "faible",
  r"Goods in a warehouse carry small tags that are read through their packaging by radio waves from a few metres away, with no need for a line of sight. Which technology is used?",
  r"RFID",
  [(r"Barcode", r"takes the optical code that must be in direct view of the reader"),
   (r"Magnetic stripe", r"takes the strip that must be swiped through a reader"),
   (r"QR code", r"takes the optical code that must be seen by a camera")],
  r"RFID tags answer a radio signal sent by the reader, so they can be read through packaging, at a distance and several at a time, which optical codes cannot do.",
  r"Reading by radio waves, through packaging and without a line of sight is the feature of RFID. Barcodes and QR codes are optical and a magnetic stripe needs a swipe.")
# 39
Q(["ict applications in society"], "faible",
  r"Using ICT to examine and advise patients who are in another place, for example by video link and by sending scans, is called",
  r"telemedicine",
  [(r"e-learning", r"takes the use of ICT for teaching and learning"),
   (r"telebanking", r"takes the use of ICT for managing a bank account from a distance"),
   (r"teleshopping", r"takes the use of ICT for buying goods from a distance")],
  r"Telemedicine uses communication links to give medical examination, diagnosis and advice to patients at a distance, which helps people who live far from a hospital.",
  r"The service is medical care given at a distance, which is telemedicine. The other terms apply to teaching, banking and shopping.")
# 40
Q(["spreadsheet modelling"], "moyenne",
  "Cells A2 to C5 of a worksheet contain the following data, and cell E1 contains P103.\n\n| | A | B | C |\n|---|---|---|---|\n| 2 | P101 | Pen | 250 |\n| 3 | P102 | Ruler | 400 |\n| 4 | P103 | Eraser | 150 |\n| 5 | P104 | Stapler | 1200 |\n\nWhat does the formula `=VLOOKUP(E1,A2:C5,3,FALSE)` display?",
  r"150",
  [(r"Eraser", r"uses column 2 of the range instead of column 3"),
   (r"P103", r"returns column 1, which is the value searched, instead of column 3"),
   (r"400", r"reads the price of the row above after miscounting the rows of the range")],
  r"`VLOOKUP` searches for a value in the first column of a range, finds the row where it is, and returns the cell of that row in the column whose number within the range is given; FALSE requires an exact match.",
  r"P103 is found in the first column, on the row of the eraser. Column 3 of the range A to C is column C, whose value on that row is 150.",
  150)
# 41
Q(["ict database normalisation"], "moyenne",
  r"A table `orderline(OrderID, ProductID, ProductName, Quantity)` has the composite primary key (OrderID, ProductID). ProductName depends only on ProductID. What is the lowest normal form that this table fails to meet?",
  r"Second normal form, because of a partial dependency",
  [(r"First normal form, because of a repeating group", r"believes that a composite key means the table has repeating groups"),
   (r"Third normal form, because of a transitive dependency", r"mixes a dependency on a part of the key with a dependency between two non-key fields"),
   (r"None, because a composite key is always allowed", r"believes that a composite key never causes any problem of dependency")],
  r"A table is in second normal form when it is in first normal form and every non-key field depends on the whole of the primary key; a field that depends on only part of a composite key is a partial dependency.",
  r"ProductName is determined by ProductID alone, which is only part of the key. This partial dependency breaks second normal form. The cure is a separate `product(ProductID, ProductName)` table.")
# 42
Q(["ict system software"], "faible",
  r"Which translator converts a whole high-level language program into machine code before it is run, so that the program can then be executed without the source code?",
  r"Compiler",
  [(r"Interpreter", r"takes the translator that translates and runs the program one statement at a time"),
   (r"Assembler", r"takes the translator for assembly language, which is a low-level language"),
   (r"Linker", r"takes the utility that joins separately translated modules and does not translate")],
  r"A compiler translates the whole source program into an object program in one go, whereas an interpreter translates and executes one statement at a time and must be present each time the program runs.",
  r"Translating the whole high-level program before it is run is what a compiler does. The interpreter works line by line, an assembler handles assembly language and a linker only joins modules.")
# 43
Q(["ict programming constructs"], "moyenne",
  r"The list `7 3 9 2 6` is sorted into ascending order with a bubble sort that compares neighbouring items from left to right. What does the list look like after the first complete pass?",
  r"`3 7 2 6 9`",
  [(r"`3 2 6 7 9`", r"shows the list after the second pass"),
   (r"`2 3 9 7 6`", r"applies a selection sort, which swaps the smallest item to the front"),
   (r"`2 3 6 7 9`", r"gives the fully sorted list instead of the list after one pass")],
  r"A bubble sort compares each pair of neighbouring items and swaps them when they are in the wrong order, so that the largest item of the unsorted part moves to the end during each pass.",
  r"Pass 1: 7 and 3 swap, 7 and 9 stay, 9 and 2 swap, 9 and 6 swap, which gives `3 7 2 6 9` with the largest value in place.",
  "3 7 2 6 9")
# 44
Q(["ict transmission modes"], "moyenne",
  r"Bytes are sent with even parity, the parity bit being the leftmost bit of each byte. Which received byte shows that an error occurred during transmission?",
  r"`10110101`",
  [(r"`11001100`", r"counts four bits set to 1, an even number, so this byte passes the check"),
   (r"`01111110`", r"counts six bits set to 1, an even number, so this byte passes the check"),
   (r"`10000001`", r"counts two bits set to 1, an even number, so this byte passes the check")],
  r"With even parity the sender sets the parity bit so that the total number of bits equal to 1 in the byte is even, and the receiver reports an error when it counts an odd number.",
  r"`10110101` contains five bits equal to 1, which is odd, so it cannot be a correct even-parity byte. The other three bytes contain four, six and two such bits.",
  "10110101")
# 45
Q(["ict logic gates and boolean algebra"], "faible",
  r"A logic circuit has five inputs. How many rows does its complete truth table have?",
  r"32",
  [(r"10", r"multiplies the number of inputs by 2 instead of raising 2 to that power"),
   (r"25", r"squares the number of inputs instead of raising 2 to that power"),
   (r"16", r"uses 2 to the power 4, one input fewer than the circuit has")],
  r"Each input can be 0 or 1, so a circuit with n inputs has 2 to the power n combinations, and each combination is one row of the truth table.",
  r"With n = 5 the number of rows is 2 x 2 x 2 x 2 x 2 = 32.",
  32)
# 46
Q(["html and css"], "faible",
  r"A style sheet contains `p { margin: 5px 15px 25px 35px; }`. What is the width of the left margin of a paragraph?",
  r"35px",
  [(r"5px", r"reads the first value, which is the top margin, as the left margin"),
   (r"15px", r"reads the second value, which is the right margin, as the left margin"),
   (r"25px", r"reads the third value, which is the bottom margin, as the left margin")],
  r"With four values the CSS `margin` shorthand gives the top, right, bottom and left margins in that order, clockwise from the top.",
  r"The four values are top 5px, right 15px, bottom 25px and left 35px, so the left margin is 35px.")
# 47
Q(["ict project management"], "elevee",
  "A project is made of seven tasks. Task durations and dependencies are shown below.\n\n| Task | Duration (days) | Depends on |\n|---|---|---|\n| A | 3 | none |\n| B | 2 | none |\n| C | 3 | A |\n| D | 5 | A, B |\n| E | 3 | C, D |\n| F | 2 | D |\n| G | 1 | E, F |\n\nWhat is the total float of task C, that is the delay it can suffer without delaying the end of the project?",
  r"2 days",
  [(r"0 days", r"treats C as a task of the critical path"),
   (r"1 day", r"gives the float of tasks B or F instead of the float of C"),
   (r"3 days", r"takes the duration of C for its float")],
  r"The total float of a task is its latest finish time minus its earliest finish time; a task with zero float is on the critical path and any delay on it delays the whole project.",
  r"C can start at day 3 and finish at day 6. Task E can start at day 8 at the latest, since the project ends at day 12 and E and G take 3 + 1 days after day 8, so C must finish by day 8. Its float is 8 - 6 = 2 days.",
  2)
# 48
Q(["ict database concepts"], "moyenne",
  """The table `student` is shown below. A value of NULL means that no mark was recorded.

| sid | name | form | mark |
|---|---|---|---|
| 1 | Ada | L6 | 72 |
| 2 | Bello | L6 | 48 |
| 3 | Chi | L5 | 65 |
| 4 | Dina | L6 | NULL |
| 5 | Emeka | L5 | 80 |
| 6 | Fon | L5 | 55 |
| 7 | Gina | L6 | 66 |
| 8 | Ivo | L6 | 90 |

What does this query return?

```sql
SELECT COUNT(mark), COUNT(*), AVG(mark) FROM student;
```""",
  r"7, 8, 68",
  [(r"8, 8, 68", r"counts the NULL mark in COUNT(mark)"),
   (r"7, 8, 59.5", r"divides the sum of the marks by 8 as if the NULL mark were zero"),
   (r"8, 7, 68", r"swaps the results of COUNT(mark) and COUNT(*)")],
  r"`COUNT(*)` counts rows, while `COUNT(column)` and `AVG(column)` ignore the NULL values of that column, so they use only the rows that actually hold a value.",
  r"`COUNT(*)` counts all 8 rows. `COUNT(mark)` counts the 7 recorded marks. Their sum is 476, and `AVG(mark)` divides it by 7, giving 68.")
# 49
Q(["ict number systems"], "moyenne",
  r"A bitmap image is 1024 pixels wide and 768 pixels high, and each pixel can take any of 16 colours. Take 1 KB = 1024 bytes. What is the size of the image file, ignoring any header and compression?",
  r"384 KB",
  [(r"1536 KB", r"uses 16 bits per pixel, taking the number of colours for the number of bits"),
   (r"3072 KB", r"uses 4 bytes per pixel instead of 4 bits"),
   (r"96 KB", r"uses 1 bit per pixel, as for a black and white image")],
  r"The number of bits per pixel is the power of 2 that gives the number of colours, and the file size in bits is the number of pixels multiplied by the bits per pixel, then divided by 8 for bytes.",
  r"16 colours need 4 bits per pixel. The image has 1024 x 768 = 786 432 pixels, that is 3 145 728 bits or 393 216 bytes. Divided by 1024 this gives 384 KB.",
  384)
# 50
Q(["spreadsheet modelling"], "moyenne",
  r"Cell B2 contains 35 and cell C2 contains 62. What does the formula `=IF(AND(B2>=40,C2>=40),\"Pass\",IF(OR(B2>=40,C2>=40),\"Resit\",\"Fail\"))` display?",
  r"Resit",
  [(r"Pass", r"reads AND as OR in the first test"),
   (r"Fail", r"stops at the first value, which is below 40, and does not read the second test"),
   (r"TRUE", r"displays the logical result of the inner test instead of the text")],
  r"`AND` is true only if all its conditions are true and `OR` is true if at least one is; in a nested `IF` the second test is evaluated only when the first is false.",
  r"B2 is below 40, so `AND(B2>=40,C2>=40)` is false and the formula evaluates the inner `IF`. `OR(B2>=40,C2>=40)` is true because C2 is 62, so the result is the text Resit.")
