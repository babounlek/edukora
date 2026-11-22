r"""Les 50 QCM de l'epreuve inedite GCE A Level Computer Science Paper 1 n.1 (50 x 1 point, 90 min).

Structure mesuree sur les Paper 1 reels 2025 et 2026 (un seul JSON de 50 questions chacun) : 50 questions a MEILLEURE REPONSE (aucun bloc de completion multiple
ni d'assertion-raison), themes melanges d'une question a l'autre, 4 options ; environ un tiers de questions factuelles ou de definition, le reste calculatoire
(numeration, arithmetique binaire, tables de verite, ordonnancement, pagination, SQL, traces d'algorithmes, structures de donnees). Aucune donnee, aucun enonce et
aucun jeu d'options repris d'un sujet reel. Chaque question : `id` (cle du verificateur), enonce, bonne option, trois distracteurs avec l'erreur type qui y mene,
rappel (un seul paragraphe), resolution, valeur de controle `val` recalculee par verifier_reponses_cs_al_p1.py. Les lettres des cles sont placees par le GENERATEUR
(13/13/12/12, jamais trois de suite), pas ici. `cours` (facultatif) = etiquette de la table cours_titres_gce_cs_al.json a utiliser pour le rappel.
Chaines BRUTES (r"...") : une commande a backslash simple dans une chaine ordinaire devient un caractere de controle.
"""

QS = []


def Q(qid, themes, diff, stem, key, dist, rappel, sol, val, conseil=None, cours=None):
    assert len(dist) == 3 and all(len(d) == 2 for d in dist), qid
    texts = [key] + [d[0] for d in dist]
    assert len(set(texts)) == 4, ("options en double", qid)
    assert "\n\n" not in rappel, "rappel : un seul paragraphe"
    assert "—" not in stem + sol + rappel, qid
    QS.append(dict(id=qid, themes=themes, diff=diff, stem=stem, key=key, dist=dist, rappel=rappel, sol=sol, val=val, conseil=conseil, cours=cours))


def questions():
    return QS


# 1
Q("hex2dec", ["number systems"], "faible",
  r"What is the decimal value of the hexadecimal number `2F5`?",
  "757",
  [("773", r"gives the digit F the value 16 instead of 15"),
   ("355", r"keeps F as 15 but uses powers of 10 as the place values"),
   ("253", r"keeps F as 15 but uses powers of 8 as the place values")],
  r"In hexadecimal the place values are powers of 16 from the right (1, 16, 256, ...) and the digits A to F stand for 10 to 15.",
  r"`2F5` has place values 256, 16 and 1, so the value is 2 x 256 + 15 x 16 + 5 x 1 = 512 + 240 + 5 = 757.",
  757)
# 2
Q("bin_add", ["binary arithmetic"], "faible",
  r"Two unsigned 8-bit numbers, `01101101` and `00111011`, are added. The 8-bit result is",
  "`10101000`",
  [("`01010110`", r"adds each column on its own and never passes a carry to the next column"),
   ("`10000000`", r"writes 1 + 1 + 1 as 10 (carry 1, sum 0) instead of 11 (carry 1, sum 1)"),
   ("`10101001`", r"puts a spurious carry into the lowest column before adding")],
  r"Binary addition works column by column from the right: 0 + 0 = 0, 0 + 1 = 1, 1 + 1 = 10 (sum 0, carry 1) and 1 + 1 + 1 = 11 (sum 1, carry 1).",
  r"Check in decimal: `01101101` is 109 and `00111011` is 59, so the sum is 168, which is 128 + 32 + 8 = `10101000`. Adding by columns from the right gives the same string.",
  168)
# 3
Q("twos_neg", ["binary arithmetic"], "faible",
  r"In 8-bit two's complement, the number -45 is stored as",
  "`11010011`",
  [("`11010010`", r"inverts the bits of 45 (`00101101`) but forgets to add 1"),
   ("`10101101`", r"sets the sign bit and keeps the magnitude of 45 (sign and magnitude)"),
   ("`01010011`", r"subtracts 45 from 128 instead of 256 and writes the result in 8 bits")],
  r"To store -n in two's complement, write n in binary, invert every bit and add 1 (equivalently, take 2 raised to the number of bits minus n).",
  r"45 = `00101101`. Inverting gives `11010010` and adding 1 gives `11010011`. Check: 256 - 45 = 211 = 128 + 64 + 16 + 2 + 1 = `11010011`.",
  0b11010011)
# 4
Q("twos_sub", ["binary arithmetic"], "moyenne",
  r"An 8-bit two's complement processor works out `00101110` - `00110100`. The result stored in the 8-bit register is",
  "`11111010`",
  [("`00000110`", r"takes the magnitude of the difference and forgets that the result is negative"),
   ("`11111001`", r"writes -6 in one's complement, so the final 1 is missing"),
   ("`10000110`", r"writes -6 in sign and magnitude")],
  r"A subtraction a - b is done as a + (two's complement of b); a negative result is read back by inverting its bits and adding 1 to get the magnitude.",
  r"`00101110` is 46 and `00110100` is 52, so the result is -6. In 8 bits, 6 = `00000110`, inverted `11111001`, plus 1 gives `11111010`. Adding 46 to the two's complement of 52 (`11001100`) gives the same string.",
  0b11111010)
# 5
Q("overflow", ["binary arithmetic"], "moyenne",
  r"In 8-bit two's complement, `01100100` is added to `00110010`. The stored 8-bit result, read as a two's complement number, is",
  "-106",
  [("150", r"reads the result as an unsigned number and ignores the overflow"),
   ("-22", r"reads the result in sign and magnitude (sign bit 1, magnitude `0010110`)"),
   ("106", r"inverts and adds 1 correctly but forgets to give the answer a minus sign")],
  r"When two positive two's complement numbers give a sum above 127 in 8 bits, the sum overflows into the sign bit and the stored pattern is read as a negative number.",
  r"100 + 50 = 150, which is above 127, so the result is `10010110`. As a two's complement number its value is 150 - 256 = -106 (inverting gives `01101001`, adding 1 gives `01101010` = 106, and the sign bit says negative).",
  -106)
# 6
Q("bool_simpl", ["boolean algebra"], "moyenne",
  r"Which expression is equivalent to `(A AND B) OR (A AND (NOT B) AND C)`?",
  "`A AND (B OR C)`",
  [("`A AND B`", r"drops the second term, which is true when A = 1, B = 0 and C = 1"),
   ("`(A AND B) OR C`", r"drops the factor A from the second term"),
   ("`A OR B OR C`", r"replaces every AND by OR")],
  r"Factor the common variable, then use X OR ((NOT X) AND Y) = X OR Y with X = B and Y = C; a truth table over all 8 input rows settles any doubt.",
  r"`(A AND B) OR (A AND (NOT B) AND C)` = `A AND (B OR ((NOT B) AND C))` = `A AND (B OR C)`. Check the row A = 1, B = 0, C = 1: the original gives 1 and so does `A AND (B OR C)`, while `A AND B` gives 0.",
  "A.(B+C)")
# 7
Q("demorgan", ["boolean algebra"], "faible",
  r"Which expression is equivalent to `NOT (X AND (NOT Y))`?",
  "`(NOT X) OR Y`",
  [("`(NOT X) AND Y`", r"negates the two terms but keeps the AND instead of switching it to OR"),
   ("`X OR (NOT Y)`", r"switches AND to OR but forgets to negate the terms"),
   ("`(NOT X) OR (NOT Y)`", r"negates both terms but forgets that the NOT already on Y cancels")],
  r"De Morgan: NOT (P AND Q) = (NOT P) OR (NOT Q); the NOT of a NOT cancels.",
  r"With P = X and Q = NOT Y: `NOT (X AND (NOT Y))` = `(NOT X) OR (NOT (NOT Y))` = `(NOT X) OR Y`. The truth table agrees: the expression is 0 only when X = 1 and Y = 0.",
  "~X+Y")
# 8
Q("xor_circuit", ["digital logic gates"], "moyenne",
  r"A circuit has inputs A and B. Gate 1 is a NAND gate fed by A and B. Gate 2 is an OR gate fed by A and B. Gate 3 is an AND gate fed by the outputs of gates 1 and 2, and its output is the output of the circuit. The circuit behaves as a",
  "XOR gate",
  [("XNOR gate", r"gives the complement: it outputs 1 when the two inputs are equal"),
   ("AND gate", r"looks only at the last gate and ignores what the NAND and OR gates do to the inputs"),
   ("NOR gate", r"notes that the NAND output is 1 for inputs 0 and 0 and so concludes that the circuit outputs 1 there")],
  r"To identify a circuit, write the output of each gate for the four input pairs 00, 01, 10 and 11 and compare the final column with the truth table of each standard gate.",
  r"For (A, B) = 00: NAND 1, OR 0, AND 0. For 01 and 10: NAND 1, OR 1, AND 1. For 11: NAND 0, OR 1, AND 0. The output column is 0, 1, 1, 0, which is XOR.",
  (0, 1, 1, 0))
# 9
Q("full_adder", ["digital logic circuits"], "faible",
  r"A full adder receives A = 1, B = 1 and a carry-in of 1. Its outputs are",
  "sum 1, carry 1",
  [("sum 0, carry 1", r"ignores the carry-in when forming the sum and adds only 1 + 1 = 10"),
   ("sum 1, carry 0", r"loses the carry produced by the first half adder"),
   ("sum 0, carry 0", r"thinks that three 1s cancel in pairs and so nothing is carried")],
  r"A full adder adds three bits: sum = A XOR B XOR Cin and carry-out = 1 whenever at least two of the three inputs are 1.",
  r"1 + 1 + 1 = 3 = `11` in binary, so sum = 1 and carry-out = 1. In gates: A XOR B = 0, then 0 XOR 1 = 1 gives the sum; the carry is (A AND B) OR (Cin AND (A XOR B)) = 1 OR 0 = 1.",
  (1, 1))
# 10
Q("nand_or", ["digital logic gates"], "moyenne",
  r"Only two-input NAND gates are available. What is the smallest number of them needed to build one OR gate?",
  "3",
  [("2", r"uses a single NAND gate as an inverter for both inputs, which cannot invert two different signals"),
   ("4", r"inverts the output again, which builds a NOR gate"),
   ("1", r"believes a single NAND gate gives the OR function")],
  r"By De Morgan, A OR B = NOT ((NOT A) AND (NOT B)) = (NOT A) NAND (NOT B), and a NAND gate with its inputs tied together is an inverter.",
  r"One NAND gate per input to invert it (NAND of A with itself, NAND of B with itself) and one more NAND gate to combine the two inverted signals: 3 gates in all.",
  3)
# 11
Q("addr_capacity", ["computer memory"], "faible",
  r"A memory unit has a 14-bit address bus. Each addressed location stores 16 bits. The capacity of the unit in bytes is",
  "32 768",
  [("16 384", r"counts the 2 to the power 14 locations as bytes instead of 16-bit words"),
   ("262 144", r"counts the 16 bits of each location as 16 bytes"),
   ("224", r"multiplies the number of address lines by the word length")],
  r"An address bus with n lines selects 2 to the power n locations, and the capacity is the number of locations times the size of one location.",
  r"14 address lines give 16 384 locations. Each holds 16 bits = 2 bytes, so the capacity is 16 384 x 2 = 32 768 bytes (32 KiB).",
  32768)
# 12
Q("download_time", ["data transmission"], "moyenne",
  r"A file of 90 MiB is sent over a link that carries 6 Mbit/s. Take 1 MiB = 1 048 576 bytes and 1 Mbit = 1 000 000 bits, and ignore all overheads. About how long does the transfer take?",
  "126 s",
  [("16 s", r"forgets that a byte has 8 bits"),
   ("120 s", r"uses 1 MiB = 1 000 000 bytes although the stem gives 1 048 576 bytes"),
   ("1007 s", r"multiplies by 8 twice")],
  r"Transfer time = size in bits divided by the rate in bits per second, so a size in bytes must first be multiplied by 8.",
  r"90 MiB = 90 x 1 048 576 = 94 371 840 bytes = 754 974 720 bits. Dividing by 6 000 000 bit/s gives 125.8 s, about 126 s.",
  125.8)
# 13
Q("pc_fetch", ["fetch-execute cycle"], "faible",
  r"On a machine every instruction occupies two consecutive memory words. The program counter (PC) holds 40 when a fetch begins and both words of the instruction are read. What does the PC hold at the end of the fetch stage?",
  "42",
  [("40", r"thinks the PC only changes when the instruction has been executed"),
   ("41", r"increments the PC by 1 whatever the length of the instruction"),
   ("80", r"doubles the PC instead of adding the length of the instruction")],
  r"During the fetch stage the PC is increased by the length of the instruction just read, so that it points to the next instruction unless a jump overwrites it.",
  r"The instruction at 40 and 41 is read, so the PC advances by 2 and holds 42 when the execute stage starts.",
  42, conseil=r"Only a branch or jump instruction replaces the PC with a new address during the execute stage.")
# 14
Q("fetch_regs", ["fetch-execute cycle", "computer architecture"], "moyenne",
  r"Which sequence correctly describes the fetch stage of the fetch-execute cycle?",
  r"The PC is copied to the MAR; the memory location addressed is read into the MDR; the MDR is copied to the IR; the PC is incremented.",
  [(r"The PC is copied to the MDR; the memory location addressed is read into the MAR; the MAR is copied to the IR; the PC is incremented.", r"swaps the roles of the MAR (holds an address) and the MDR (holds data)"),
   (r"The PC is copied to the MAR; the memory location addressed is read into the MDR; the MDR is copied to the PC; the IR is incremented.", r"sends the instruction to the PC and increments the IR instead of the PC"),
   (r"The PC is copied to the MAR; the memory location addressed is read into the accumulator; the accumulator is copied to the IR; the PC is incremented.", r"uses the accumulator, a register for data being processed, as the buffer for the fetched instruction")],
  r"The MAR holds the address to be read, the MDR holds the word that comes back from memory, the IR holds the instruction to be decoded, and the PC is incremented to the next instruction.",
  r"The only order consistent with these roles is PC to MAR, memory to MDR, MDR to IR, then PC + 1. The other options give a register a job it does not have.",
  "fetch")
# 15
Q("acc_trace", ["processor instruction sets"], "moyenne",
  "A one-address machine has an accumulator ACC. In `LDA n` and `ADD n` the operand `n` is a memory address, while `LDA #n` and `ADD #n` use the number n itself. The memory holds the values below.\n\n"
  "| Address | 4 | 10 | 11 | 12 |\n|---|---|---|---|---|\n| Contents | 9 | 7 | 3 | 0 |\n\n"
  "```\nLDA 10\nADD #4\nADD 11\nSTA 12\n```\n\n"
  "After the program has run, the contents of address 12 are",
  "14",
  [("19", r"reads `ADD #4` as an add from address 4 (contents 9)"),
   ("22", r"reads `ADD 11` as adding the number 11 instead of the contents of address 11"),
   ("17", r"reads `LDA 10` as loading the number 10 instead of the contents of address 10")],
  r"Immediate addressing (`#n`) uses the number written in the instruction, direct addressing uses the contents of the memory location whose address is written.",
  r"`LDA 10` loads 7. `ADD #4` gives 7 + 4 = 11. `ADD 11` adds the contents of address 11, which is 3, giving 14. `STA 12` stores 14 at address 12.",
  14)
# 16
Q("process_state", ["operating systems"], "faible",
  r"A running process asks the operating system to read a file from disk and cannot continue until the data arrive. What does the operating system do with the process?",
  "It moves it from the running state to the blocked (waiting) state.",
  [("It moves it from the running state to the ready state.", r"confuses a wait for I/O with the end of a time slice"),
   ("It moves it from the running state to the terminated state.", r"confuses waiting with finishing"),
   ("It moves it from the ready state to the running state.", r"describes the dispatch of another process, not what happens to the one that requested the I/O")],
  r"A process leaves the running state for the blocked state when it must wait for an event such as I/O, and returns to the ready state, not the running state, when the event occurs.",
  r"The CPU cannot be used by a process that waits for the disk, so it becomes blocked and the dispatcher gives the CPU to a ready process. When the transfer ends the process goes back to the ready queue.",
  "blocked")
# 17
Q("fifo_faults", ["memory management"], "elevee",
  r"A process uses three page frames, all empty at the start. It references the pages 3, 1, 2, 3, 4, 1, 5, 3, 2, 1, 4 in that order. With first-in first-out (FIFO) page replacement, how many page faults occur?",
  "9",
  [("10", r"applies least-recently-used replacement instead of FIFO"),
   ("7", r"applies the optimal replacement, which looks at future references and cannot be implemented"),
   ("5", r"counts only the first reference to each distinct page")],
  r"With FIFO, a page fault evicts the page that has been in memory longest, whatever its recent use; a reference to a page already in a frame is a hit and does not change the order.",
  r"Frames (oldest first): 3 fault [3]; 1 fault [3 1]; 2 fault [3 1 2]; 3 hit; 4 fault [1 2 4]; 1 hit; 5 fault [2 4 5]; 3 fault [4 5 3]; 2 fault [5 3 2]; 1 fault [3 2 1]; 4 fault [2 1 4]. Faults: 3, 1, 2, 4, 5, 3, 2, 1, 4 = 9.",
  9)
# 18
Q("paging_addr", ["memory management"], "moyenne",
  r"A system divides memory into pages and frames of 2048 bytes. Logical address 9000 lies in page 4, which the page table maps to frame 11. The physical address is",
  "23 336",
  [("22 528", r"gives the first address of frame 11 and forgets to add the offset"),
   ("31 528", r"adds the whole logical address to the start of the frame instead of only the offset"),
   ("9000", r"treats the logical address as already physical and skips the translation")],
  r"Address translation splits the logical address into page number = address div page size and offset = address mod page size, then forms frame number x page size + offset.",
  r"9000 = 4 x 2048 + 808, so the page is 4 and the offset is 808. Physical address = 11 x 2048 + 808 = 22 528 + 808 = 23 336.",
  23336)
# 19
Q("fcfs", ["process scheduling"], "moyenne",
  "Four processes arrive at the times shown and need the CPU for the burst times shown (in ms). The CPU is not pre-empted.\n\n"
  "| Process | A | B | C | D |\n|---|---|---|---|---|\n| Arrival time | 0 | 1 | 2 | 4 |\n| Burst time | 6 | 2 | 7 | 3 |\n\n"
  "With first-come first-served (FCFS) scheduling, the average waiting time in ms is",
  "5.5",
  [("10.0", r"gives the average turnaround time (finish minus arrival) instead of the waiting time"),
   ("4.5", r"serves the shortest waiting job first, which is SJF and not FCFS"),
   ("7.25", r"measures each wait from time 0 and forgets to subtract the arrival time")],
  r"Waiting time = start time minus arrival time; under FCFS the processes run in order of arrival, each one starting when the previous one ends or when it arrives, whichever is later.",
  r"A runs 0 to 6 (wait 0), B runs 6 to 8 (wait 5), C runs 8 to 15 (wait 6), D runs 15 to 18 (wait 11). The average is (0 + 5 + 6 + 11) / 4 = 22 / 4 = 5.5 ms.",
  5.5)
# 20
Q("sjf", ["process scheduling"], "moyenne",
  "Four processes arrive and need the CPU as shown (times in ms). Shortest job first (SJF) is used without pre-emption: when the CPU becomes free, the ready process with the shortest burst runs.\n\n"
  "| Process | P1 | P2 | P3 | P4 |\n|---|---|---|---|---|\n| Arrival time | 0 | 1 | 2 | 3 |\n| Burst time | 5 | 3 | 1 | 4 |\n\n"
  "The average waiting time in ms is",
  "3.5",
  [("4.0", r"runs the processes in order of arrival, which is FCFS"),
   ("2.75", r"lets a shorter job pre-empt the running one, which is the pre-emptive version (SRTF)"),
   ("6.75", r"gives the average turnaround time instead of the waiting time")],
  r"Non-pre-emptive SJF never interrupts the running process; at each completion it picks, among the processes that have already arrived, the one with the smallest burst.",
  r"P1 runs 0 to 5 (wait 0). Then P2, P3 and P4 are all waiting; P3 (burst 1) runs 5 to 6 (wait 3), P2 (burst 3) runs 6 to 9 (wait 5), P4 runs 9 to 13 (wait 6). Average = (0 + 3 + 5 + 6) / 4 = 3.5 ms.",
  3.5)
# 21
Q("rr", ["process scheduling"], "moyenne",
  "Round robin with a time quantum of 3 ms is used. A process that has not finished after its quantum goes to the back of the queue, and a process that arrives during a quantum joins the queue before it. The queue is empty at time 0.\n\n"
  "| Process | P1 | P2 | P3 |\n|---|---|---|---|\n| Arrival time | 0 | 1 | 2 |\n| Burst time | 7 | 4 | 2 |\n\n"
  "At what time does P2 finish?",
  "12 ms",
  [("10 ms", r"uses a quantum of 2 ms instead of 3 ms"),
   ("8 ms", r"gives the finish time of P3, the first process to complete"),
   ("13 ms", r"gives the finish time of P1, the last process to complete")],
  r"In round robin each process runs for at most one quantum; the order of the ready queue changes after every slice, so the schedule must be written out slice by slice.",
  r"0 to 3: P1 (4 left); queue P2, P3, P1. 3 to 6: P2 (1 left). 6 to 8: P3 finishes. 8 to 11: P1 (1 left). 11 to 12: P2 finishes. 12 to 13: P1 finishes. So P2 finishes at 12 ms.",
  12)
# 22
Q("deadlock_safe", ["deadlock"], "elevee",
  "A system has 12 identical tape drives. Three processes hold and may need drives as shown.\n\n"
  "| Process | Allocated | Maximum need |\n|---|---|---|\n| P1 | 5 | 9 |\n| P2 | 2 | 4 |\n| P3 | 3 | 8 |\n\n"
  "Which order of completion is a safe sequence?",
  "P2, P1, P3",
  [("P1, P2, P3", r"lets P1 finish first although it still needs 4 drives and only 2 are free"),
   ("P3, P1, P2", r"lets P3 finish first although it still needs 5 drives and only 2 are free"),
   ("P2, P3, P1", r"lets P3 run second although it needs 5 drives and only 4 are free after P2 finishes")],
  r"With the banker's algorithm a sequence is safe if each process in turn can obtain its remaining need (maximum minus allocated) from the free drives plus those released by the processes that finished before it.",
  r"Free drives = 12 - (5 + 2 + 3) = 2. Remaining needs: P1 4, P2 2, P3 5. P2 can finish (2 <= 2) and returns 4, so 4 are free; P1 can finish (4 <= 4) and returns 9; then P3 (5 <= 9). The only safe sequence is P2, P1, P3.",
  "P2,P1,P3")
# 23
Q("subnet_net", ["computer networks"], "moyenne",
  r"A host has the IP address 172.16.37.200 and the subnet mask 255.255.255.192. The address of the network it belongs to is",
  "172.16.37.192",
  [("172.16.37.128", r"reads the mask as 255.255.255.128 and so keeps only the top bit of the last octet"),
   ("172.16.37.0", r"uses the mask 255.255.255.0"),
   ("172.16.0.0", r"uses the default mask 255.255.0.0 of a class B address")],
  r"The network address is the bitwise AND of the IP address and the subnet mask, octet by octet.",
  r"The last octet of the mask is 192 = `11000000` and 200 = `11001000`; the AND is `11000000` = 192. The first three octets of the mask are 255, so they are unchanged. The network is 172.16.37.192.",
  "172.16.37.192")
# 24
Q("parity", ["data transmission"], "faible",
  r"Even parity is used on 8-bit bytes, the 8th bit being the parity bit. Four bytes are received. Which one must contain a transmission error?",
  "`10110101`",
  [("`01101100`", r"has four 1s, an even number, so it passes the even-parity check"),
   ("`10011001`", r"has four 1s, an even number, so it passes the even-parity check"),
   ("`11000110`", r"has four 1s, an even number, so it passes the even-parity check")],
  r"With even parity the number of 1s in each byte, parity bit included, must be even, so a byte with an odd number of 1s was damaged in transmission.",
  r"Counting the 1s: `10110101` has 5 (odd, error); `01101100` has 4; `10011001` has 4; `11000110` has 4. Only the first byte fails the check.",
  "10110101")
# 25
Q("switch_mac", ["network devices"], "faible",
  r"Which device builds a table of the MAC addresses seen on each port and forwards a frame only to the port behind which the destination address was learned?",
  "A switch",
  [("A hub", r"repeats every incoming frame to all ports"),
   ("A repeater", r"only regenerates the signal and knows no addresses"),
   ("A modem", r"converts between digital data and an analogue line signal")],
  r"A switch learns MAC addresses and forwards each frame to one port, while a hub or a repeater works at the signal level and sends everything everywhere.",
  r"Selective forwarding on the learned destination MAC address is the job of a switch; the other devices have no address table.",
  "switch")
# 26
Q("caesar", ["data security"], "moyenne",
  r"A message was encrypted with a Caesar cipher that moves every letter 4 places forward in the alphabet (A becomes E, and Z wraps round to D). The ciphertext is `WIVZIV`. The plaintext is",
  "`SERVER`",
  [("`AMZDMZ`", r"shifts the letters 4 places forward again instead of back"),
   ("`TFSWFS`", r"shifts back by only 3 places"),
   ("`RDQUDQ`", r"shifts back by 5 places")],
  r"A Caesar cipher is undone by shifting every letter back by the key, wrapping from A round to Z.",
  r"W - 4 = S, I - 4 = E, V - 4 = R, Z - 4 = V, I - 4 = E, V - 4 = R, so the plaintext is `SERVER`. Encrypting `SERVER` with a shift of 4 gives back `WIVZIV`.",
  "SERVER")
# 27
Q("trojan", ["computer security threats"], "faible",
  r"A free screensaver works as advertised but also quietly opens a port that lets an attacker control the computer. This malware is a",
  "Trojan horse",
  [("worm", r"takes the program for malware that copies itself across a network without help from the user"),
   ("logic bomb", r"takes the program for code that waits for a condition, such as a date, before it does damage"),
   ("keylogger", r"takes the program for software that only records keystrokes")],
  r"A Trojan horse hides harmful behaviour inside a program that looks useful; it does not copy itself, unlike a worm or a virus.",
  r"The useful screensaver is the disguise and the open port is the hidden payload, which is the definition of a Trojan horse.",
  "trojan")
# 28
Q("sql_group", ["sql queries"], "moyenne",
  "The table Pupil holds the following rows.\n\n"
  "| pid | name | town | mark |\n|---|---|---|---|\n| 1 | Ada | Buea | 62 |\n| 2 | Bih | Limbe | 48 |\n| 3 | Che | Buea | 55 |\n| 4 | Dul | Kumba | 71 |\n| 5 | Eno | Limbe | 66 |\n| 6 | Fon | Buea | 43 |\n| 7 | Gwen | Limbe | 59 |\n\n"
  "```\nSELECT town, AVG(mark)\nFROM Pupil\nWHERE mark >= 50\nGROUP BY town\nHAVING COUNT(*) >= 2\nORDER BY town;\n```\n\n"
  "The query returns",
  "Buea 58.5 and Limbe 62.5",
  [("Buea 53.3 and Limbe 57.7", r"applies the condition `mark >= 50` after grouping instead of before it, so the marks below 50 are still averaged"),
   ("Buea 58.5, Kumba 71.0 and Limbe 62.5", r"applies `HAVING COUNT(*) >= 2` to the original rows, so Kumba, which has one row with mark 50 or more, is kept"),
   ("Buea 2 and Limbe 2", r"reports the number of rows in each group instead of the average")],
  r"In a query, WHERE filters the rows first, GROUP BY forms the groups from the remaining rows, HAVING filters the groups, and the aggregate (here AVG) is computed on each surviving group.",
  r"WHERE keeps the marks 62, 55, 71, 66 and 59. Grouping gives Buea (62, 55), Kumba (71) and Limbe (66, 59). HAVING keeps the groups with at least two rows, so Kumba goes. The averages are Buea (62 + 55) / 2 = 58.5 and Limbe (66 + 59) / 2 = 62.5.",
  "sql_group")
# 29
Q("sql_join", ["sql queries"], "faible",
  "Two tables are stored. Customer: (1, Mba), (2, Nji), (3, Oben), (4, Pa) as (cid, cname). Orders: (10, 1, 200), (11, 1, 150), (12, 3, 400), (13, 3, 50), (14, 5, 90) as (oid, cid, amount).\n\n"
  "```\nSELECT c.cname, o.amount\nFROM Customer c LEFT JOIN Orders o ON c.cid = o.cid;\n```\n\n"
  "How many rows does the query return?",
  "6",
  [("4", r"counts only the customers who have orders, which is the result of an inner join"),
   ("5", r"counts every order, including order 14 whose customer does not exist"),
   ("20", r"counts every pairing of a customer with an order, which is a cross join")],
  r"A LEFT JOIN keeps every row of the left table: each match gives a row, and a left row with no match gives one row with NULL in the right columns; right rows without a left partner are dropped.",
  r"Mba matches 2 orders (2 rows), Nji has none (1 row with NULL), Oben matches 2 orders (2 rows), Pa has none (1 row with NULL). Order 14 has no customer and disappears. Total = 2 + 1 + 2 + 1 = 6.",
  6)
# 30
Q("sql_subq", ["sql queries"], "moyenne",
  "The table Staff holds (name, salary): (Aba, 320), (Bessem, 450), (Chi, 280), (Dione, 510), (Epie, 300), (Fru, 390), (Gah, 380).\n\n"
  "```\nSELECT name\nFROM Staff\nWHERE salary > (SELECT AVG(salary) FROM Staff);\n```\n\n"
  "The query returns the names",
  "Bessem, Dione, Fru and Gah",
  [("Bessem, Dione and Fru", r"compares with the median salary (380) instead of the mean"),
   ("Aba, Chi and Epie", r"selects the salaries below the average, as if the condition were `<`"),
   ("Aba, Bessem, Dione, Epie, Fru and Gah", r"compares with the lowest salary, not the average")],
  r"The subquery in brackets is evaluated first and returns one value, here the mean of all the salaries, which the outer WHERE then compares with each row.",
  r"The mean is (320 + 450 + 280 + 510 + 300 + 390 + 380) / 7 = 2630 / 7, about 375.7. The salaries above it are 450, 510, 390 and 380, that is Bessem, Dione, Fru and Gah.",
  "sql_subq")
# 31
Q("normal_form", ["relational databases"], "moyenne",
  r"A relation Line(OrderID, ProductID, ProductName, Quantity) has the composite primary key (OrderID, ProductID). Each ProductID always has the same ProductName, and Quantity depends on the whole key. What is the highest normal form this relation satisfies?",
  "First normal form",
  [("Second normal form", r"overlooks that ProductName depends on ProductID alone, which is a part of the key"),
   ("Third normal form", r"checks for transitive dependencies and skips the test for partial dependencies that comes first"),
   ("Boyce-Codd normal form", r"assumes a normal form that needs 3NF (and so 2NF) to hold first")],
  r"First normal form needs atomic values; second normal form also removes partial dependencies on part of a composite key; third removes transitive dependencies; BCNF requires every determinant to be a candidate key.",
  r"ProductName is determined by ProductID, which is only a part of the key, so there is a partial dependency and the relation is not in 2NF. The values are atomic, so it is in 1NF, its highest form.",
  "1NF")
# 32
Q("trace_loop", ["algorithm tracing"], "faible",
  "```\ntotal = 0\nfor i in range(1, 9):\n    if i % 3 == 0:\n        total = total + i\n    else:\n        total = total - 1\nprint(total)\n```\n\n"
  "(`range(1, 9)` gives 1, 2, ..., 8 and `%` gives the remainder of a division.) The program prints",
  "3",
  [("4", r"stops the loop at i = 7 instead of i = 8"),
   ("9", r"adds the multiples of 3 and forgets the subtractions"),
   ("-8", r"subtracts 1 at every pass and forgets the additions")],
  r"To trace a loop, list the value of the loop variable on every pass, decide which branch is taken, and update the variable that accumulates the result.",
  r"i = 3 and i = 6 give the first branch: +3 and +6 = +9. The six other values (1, 2, 4, 5, 7, 8) each subtract 1: -6. total = 9 - 6 = 3.",
  3)
# 33
Q("bubble", ["sorting algorithms"], "faible",
  r"A bubble sort puts the list `9 4 7 1 8 3` in ascending order. It compares adjacent pairs from the left and swaps them when they are in the wrong order. After exactly two complete passes the list is",
  "`4 1 7 3 8 9`",
  [("`4 7 1 8 3 9`", r"stops after the first pass"),
   ("`1 4 3 7 8 9`", r"goes on to a third pass"),
   ("`1 3 7 9 8 4`", r"applies selection sort, which puts the two smallest values first")],
  r"In each pass of a bubble sort the largest remaining value moves to the end because adjacent out-of-order pairs are swapped as the scan goes along the list.",
  r"Pass 1: 9 moves along: `4 7 1 8 3 9`. Pass 2 on the first five values: 4 7 (no swap), 7 1 swap, 7 8 (no swap), 8 3 swap: `4 1 7 3 8 9`.",
  "4 1 7 3 8 9")
# 34
Q("insertion", ["sorting algorithms"], "moyenne",
  r"An insertion sort sorts the list `5 2 9 1 7 3` in ascending order. Each time a value is moved one place to the right to make room, it counts as one shift. How many shifts are made in total?",
  "8",
  [("11", r"counts the comparisons (including the ones that stop an inner loop) instead of the shifts"),
   ("5", r"counts the passes of the outer loop"),
   ("15", r"gives the worst case for six values, the number of pairs out of order in a reversed list")],
  r"Insertion sort takes each value in turn and shifts every larger value of the sorted part one place right; the total number of shifts equals the number of inversions in the list.",
  r"2 shifts past 5 (1 shift); 9 stays (0); 1 passes 9, 5, 2 (3 shifts); 7 passes 9 (1 shift); 3 passes 9, 7, 5 (3 shifts). Total = 1 + 0 + 3 + 1 + 3 = 8.",
  8)
# 35
Q("binsearch", ["searching algorithms"], "moyenne",
  r"A binary search looks for 40 in the sorted list `4 9 13 18 22 27 31 36 40 45 51 58 63` (positions 0 to 12). At each step the middle position is the integer part of (low + high) / 2, and each examination of a middle value counts as one comparison. How many comparisons are made before 40 is found?",
  "4",
  [("3", r"does not count the comparison that finds the item"),
   ("5", r"adds an extra comparison to confirm the result"),
   ("9", r"gives the number of comparisons of a linear search")],
  r"Binary search compares the target with the middle value and keeps the half in which the target can lie, so the number of steps grows like the logarithm of the list size.",
  r"low 0, high 12: middle 6 holds 31, below 40, so low = 7. Middle 9 holds 45, above 40, so high = 8. Middle 7 holds 36, below 40, so low = 8. Middle 8 holds 40: found. That is 4 comparisons; a linear search needs 9.",
  4)
# 36
Q("stack_pops", ["data structures", "stacks and queues"], "faible",
  "A stack is empty and the following operations are performed in order.\n\n"
  "```\npush 4\npush 9\npop\npush 2\npush 7\npop\npop\n```\n\n"
  "The values returned by the three pop operations, in order, are",
  "9, 7, 2",
  [("4, 9, 2", r"treats the structure as a queue and removes the oldest item each time"),
   ("2, 7, 9", r"lists the values in the reverse of the order in which they come out"),
   ("9, 7, 4", r"forgets the `push 2`, so the last pop reaches the bottom value")],
  r"A stack is last in first out: pop returns the most recently pushed value that has not yet been removed.",
  r"The stack evolves as 4; 4 9; pop returns 9; 4 2; 4 2 7; pop returns 7; pop returns 2. The returned values are 9, 7, 2.",
  (9, 7, 2))
# 37
Q("bst_post", ["data structures"], "moyenne",
  r"The values 40, 25, 60, 10, 30, 50, 70, 28, 35 are inserted in this order into an empty binary search tree (smaller values to the left). A post-order traversal (left subtree, right subtree, then the node) visits the values in the order",
  "10, 28, 35, 30, 25, 50, 70, 60, 40",
  [("40, 25, 10, 30, 28, 35, 60, 50, 70", r"gives the pre-order traversal, where the node comes first"),
   ("10, 25, 28, 30, 35, 40, 50, 60, 70", r"gives the in-order traversal, which lists the values in sorted order"),
   ("40, 25, 60, 10, 30, 50, 70, 28, 35", r"gives the level-by-level order, which is the order of insertion")],
  r"In a post-order traversal each node is visited after its left and right subtrees; in a binary search tree the in-order traversal gives the sorted list and the pre-order traversal visits each node before its subtrees.",
  r"The tree has root 40; 25 (children 10 and 30, and 30 has children 28 and 35) on the left; 60 (children 50 and 70) on the right. Post-order: 10, then the subtree of 30 (28, 35, 30), then 25, then 50, 70, 60, then 40.",
  (10, 28, 35, 30, 25, 50, 70, 60, 40))
# 38
Q("postfix", ["stacks and queues"], "moyenne",
  r"The postfix (reverse Polish) expression `15 4 3 + 2 * -` is evaluated with a stack. Its value is",
  "1",
  [("-1", r"reverses the operands of the final subtraction"),
   ("14", r"stops before the final operator, with 14 on top of the stack"),
   ("29", r"adds 15 and 14 in the last step instead of subtracting")],
  r"To evaluate postfix, push each number and, at each operator, pop the two top values, apply the operator with the first value popped on the right, and push the result.",
  r"Push 15, 4, 3. The `+` replaces 4 and 3 by 7. Push 2; the `*` replaces 7 and 2 by 14. The `-` takes 15 and 14 and gives 15 - 14 = 1.",
  1)
# 39
Q("byval_byref", ["programming concepts"], "elevee",
  "```\nPROCEDURE Mix(BYVAL a, BYREF b)\n    a <- a + 5\n    b <- b * 2\n    a <- a + b\nENDPROCEDURE\n\nx <- 3\ny <- 4\nCALL Mix(x, y)\nOUTPUT x, y\n```\n\n"
  "`OUTPUT x, y` prints the two values on one line, separated by a space. It prints",
  "3 8",
  [("16 8", r"passes both parameters by reference, so x is changed as well"),
   ("3 4", r"passes both parameters by value, so nothing changes in the caller"),
   ("16 4", r"swaps the two modes: a by reference and b by value")],
  r"A BYVAL parameter is a copy, so changes stay inside the procedure; a BYREF parameter is the caller's own variable, so every assignment to it changes the caller's variable.",
  r"a is a copy of x (3), b is y itself (4). a becomes 8; b becomes 8 and so does y; a becomes 8 + 8 = 16, but only the copy. After the call x is still 3 and y is 8.",
  (3, 8), cours="parameter passing")
# 40
Q("logic_paradigm", ["programming paradigms"], "faible",
  r"A program is written as a set of facts and rules, and the language system works out the answers to queries by inference. This is",
  "logic programming",
  [("procedural programming", r"takes it for programming in which the programmer writes the steps that change variables one after the other"),
   ("object-oriented programming", r"takes it for programming in which data and the methods that act on it are grouped in classes"),
   ("event-driven programming", r"takes it for programming in which handlers run when events such as clicks occur")],
  r"In logic programming (Prolog is the best-known language) the programmer states facts and rules and the system searches for the answers, instead of describing the steps.",
  r"Facts and rules plus queries answered by inference are the marks of logic programming, a declarative paradigm.",
  "logic")
# 41
Q("compiler_phases", ["translators and compilers"], "faible",
  r"Which is the usual order of the main phases of a compiler?",
  "Lexical analysis, syntax analysis, semantic analysis, code generation",
  [("Syntax analysis, lexical analysis, semantic analysis, code generation", r"puts the parsing of the grammar before the splitting of the source text into tokens"),
   ("Lexical analysis, semantic analysis, syntax analysis, code generation", r"checks meaning before the grammar of the token stream has been checked"),
   ("Lexical analysis, syntax analysis, code generation, semantic analysis", r"generates the machine code before the meaning of the program has been checked")],
  r"A compiler first splits the source into tokens (lexical analysis), then checks the grammar and builds a parse tree (syntax analysis), then checks types and scope (semantic analysis), and only then generates code.",
  r"Each phase uses the output of the one before: tokens feed the parser, the parse tree feeds the semantic checks, and only a checked tree is turned into code.",
  "compiler")
# 42
Q("boundary_tests", ["software testing", "software engineering"], "faible",
  r"A form accepts an age from 18 to 60 inclusive. Which set of test values is the boundary test data?",
  "17, 18, 60, 61",
  [("18, 39, 60", r"tests the two limits and a typical value but never a value just outside the range"),
   ("0, 18, 60, 100", r"uses extreme values far from the limits"),
   ("19, 59", r"tests only values just inside the limits")],
  r"Boundary testing picks the values on each limit of the valid range and the nearest values on each side of it, because errors in comparisons such as `>` and `>=` show up there.",
  r"The limits are 18 and 60. The values just outside are 17 and 61, so the boundary set is 17, 18, 60 and 61.",
  (17, 18, 60, 61))
# 43
Q("parallel_running", ["systems development life cycle"], "faible",
  r"A bank installs a new payroll system. For two months it processes every payroll with both the old and the new system and compares the results before it switches the old one off. This method of changeover is",
  "parallel running",
  [("direct changeover", r"takes it for a change in which the old system stops on one day and the new one starts"),
   ("phased changeover", r"takes it for a change introduced module by module"),
   ("pilot running", r"takes it for a change in which the whole new system is used in one branch only")],
  r"Parallel running keeps the old and new systems working side by side on the same data until the new results are trusted; it costs more work but is the safest changeover.",
  r"Running both systems on every payroll and comparing the outputs is the definition of parallel running.",
  "parallel")
# 44
Q("amdahl", ["parallel and distributed computing"], "moyenne",
  r"70% of the running time of a program can be shared perfectly among processors and the remaining 30% is serial. By Amdahl's law, what is the speed-up on 4 processors, to one decimal place?",
  "2.1",
  [("2.8", r"multiplies the parallel fraction 0.7 by the number of processors"),
   ("3.3", r"divides 1 by the serial fraction, which is the limit for an unlimited number of processors"),
   ("4.0", r"takes the ideal speed-up equal to the number of processors")],
  r"Amdahl's law: speed-up = 1 / (s + p / N), where s is the serial fraction, p = 1 - s the parallel fraction and N the number of processors.",
  r"speed-up = 1 / (0.3 + 0.7 / 4) = 1 / (0.3 + 0.175) = 1 / 0.475 = 2.105, that is 2.1.",
  2.105)
# 45
Q("recursion_g", ["programming concepts", "algorithm tracing"], "moyenne",
  "```\nFUNCTION g(n)\n    IF n = 0 THEN\n        RETURN 2\n    ENDIF\n    RETURN g(n - 1) * 2 + 1\nENDFUNCTION\n```\n\n"
  "The value returned by `g(4)` is",
  "47",
  [("62", r"adds 1 before the multiplication by 2, that is (g(n - 1) + 1) * 2"),
   ("32", r"drops the + 1 at every level"),
   ("23", r"stops one level early and gives g(3)")],
  r"A recursive call is traced by writing the chain of calls until the base case, then returning the values back up the chain, applying the expression of the function at each level.",
  r"g(0) = 2; g(1) = 2 x 2 + 1 = 5; g(2) = 5 x 2 + 1 = 11; g(3) = 11 x 2 + 1 = 23; g(4) = 23 x 2 + 1 = 47.",
  47)
# 46
Q("dvd_backup", ["computer storage devices"], "faible",
  r"A school must back up 120 GB of data on 4.7 GB DVDs. Take 1 GB = 1000 MB and 4.7 GB = 4700 MB. What is the smallest number of DVDs needed?",
  "26",
  [("25", r"rounds 25.5 down instead of up"),
   ("27", r"converts 120 GB into 122 880 MB with 1024 MB per GB although the stem gives 1 GB = 1000 MB"),
   ("24", r"uses 5 GB per disc instead of 4.7 GB")],
  r"The number of discs is the data size divided by the capacity of one disc, rounded UP to the next whole number, since a part of a disc is still a disc.",
  r"120 000 MB / 4700 MB = 25.53, which needs 26 discs (25 discs hold only 117.5 GB).",
  26, cours="file backup")
# 47
Q("tps", ["information systems"], "faible",
  r"At a supermarket till every sale is recorded and the stock level of each item is updated at once. Which kind of information system does this?",
  "A transaction processing system",
  [("A decision support system", r"takes the system for one that models alternatives to help a manager choose"),
   ("A management information system", r"takes the system for one that summarises transactions into periodic reports for managers"),
   ("An expert system", r"takes the system for one that reasons from a knowledge base to advise a user")],
  r"A transaction processing system records each routine business event as it happens and updates the files at once; management information and decision support systems build on that data.",
  r"Recording each sale and updating the stock immediately is the work of a transaction processing system.",
  "tps")
# 48
Q("scaling", ["algorithm design"], "faible",
  r"A program takes time proportional to the square of the input size (O(n squared)). It takes 3 seconds for n = 500. Using the same machine, what time is expected for n = 1500?",
  "27 s",
  [("9 s", r"treats the time as proportional to n and multiplies by 3 only"),
   ("81 s", r"treats the time as proportional to n cubed"),
   ("6 s", r"adds the ratio 3 to the 3 seconds")],
  r"If the time is proportional to the square of n, multiplying n by k multiplies the time by k squared.",
  r"n grows by a factor 1500 / 500 = 3, so the time grows by 3 squared = 9 and becomes 3 x 9 = 27 s.",
  27, cours="algorithm complexity")
# 49
Q("hex_octal", ["number systems"], "faible",
  r"The binary number `1100110` is written in octal as",
  "146",
  [("630", r"groups the bits in threes from the left instead of from the right, so the last group is `0`"),
   ("102", r"gives the decimal value of the number"),
   ("66", r"gives the hexadecimal form of the number, which uses groups of four bits")],
  r"To convert binary to octal, group the bits in threes starting from the right (pad the left with zeros) and replace each group by its digit from 0 to 7.",
  r"`1100110` = `001 100 110` = 1, 4, 6, so the octal number is 146. Check: 1 x 64 + 4 x 8 + 6 = 102 and `1100110` is 64 + 32 + 4 + 2 = 102.",
  "146")
# 50
Q("bits_colours", ["data representation"], "faible",
  r"A graphics file gives each pixel an index into a palette of 300 different colours, and every index has the same number of bits. What is the minimum number of bits per index?",
  "9",
  [("8", r"stops at 256 values, which is too few for 300 colours"),
   ("10", r"takes the next power of two above the number of bits needed"),
   ("38", r"divides 300 by 8 instead of taking the logarithm")],
  r"With n bits there are 2 to the power n different patterns, so the minimum n is the smallest integer with 2 to the power n at least equal to the number of items.",
  r"2 to the power 8 is 256, which is less than 300; 2 to the power 9 is 512, which is enough. So 9 bits are needed.",
  9)
