"""Section B (questions B1 a B4, 15 points chacune) de l'epreuve inedite GCE O Level Mathematics Paper 2 n.1."""
from questions_maths_p2_a import E, S

TABLE_TEMPS = (
    "| Time (minutes) | 1 - 10 | 11 - 20 | 21 - 30 | 31 - 40 | 41 - 50 | 51 - 60 |\n"
    "|---|---|---|---|---|---|---|\n"
    "| Number of learners | 6 | 14 | 20 | 12 | 6 | 2 |"
)
TABLE_MOYENNE = (
    "| Time (minutes) | Class mark $x$ | Frequency $f$ | $fx$ |\n"
    "|---|---|---|---|\n"
    "| 1 - 10 | 5.5 | 6 | 33 |\n"
    "| 11 - 20 | 15.5 | 14 | 217 |\n"
    "| 21 - 30 | 25.5 | 20 | 510 |\n"
    "| 31 - 40 | 35.5 | 12 | 426 |\n"
    "| 41 - 50 | 45.5 | 6 | 273 |\n"
    "| 51 - 60 | 55.5 | 2 | 111 |\n"
    "| Total | | 60 | 1 570 |"
)
TABLE_VALEURS = (
    "| $x$ | $-4$ | $-3$ | $-2$ | $-1$ | $0$ | $1$ | $2$ | $3$ |\n"
    "|---|---|---|---|---|---|---|---|---|\n"
    "| $y=f(x)$ | $6$ | | $-4$ | | $-6$ | | $0$ | |"
)
TABLE_VALEURS_COMPLETE = (
    "| $x$ | $-4$ | $-3$ | $-2$ | $-1$ | $0$ | $1$ | $2$ | $3$ |\n"
    "|---|---|---|---|---|---|---|---|---|\n"
    "| $y=f(x)$ | $6$ | $0$ | $-4$ | $-6$ | $-6$ | $-4$ | $0$ | $6$ |"
)


def section_b():
    B = "SECTION B"
    ex = []

    # ------------------------------------------------------------------ B1 : arithmetique commerciale
    ex.append(E("B1", B, 15,
                r"Ngo Nyobe, a trader in Bafoussam, buys $40$ bags of rice at $24\,500$ FCFA per bag. She also pays $20\,000$ FCFA to transport all the bags.",
                [
        S("a", r"Calculate the cost of the $40$ bags of rice.", ["consumer arithmetic"], "faible", 1,
          [("You calculate $40\\times24\\,500=980\\,000$ FCFA", 1)],
          r"The cost of several identical items is the number of items multiplied by the price of one.",
          r"$40\times24\,500=980\,000$.", r"$980\,000$ FCFA"),
        S("b", r"Find her total cost price, including transport.", ["consumer arithmetic"], "faible", 1,
          [("You add the transport: $980\\,000+20\\,000=1\\,000\\,000$ FCFA", 1)],
          r"The cost price is the purchase cost plus every cost needed to bring the goods to the point of sale.",
          r"$980\,000+20\,000=1\,000\,000$.", r"$1\,000\,000$ FCFA"),
        S("c", r"She sells $\dfrac{3}{4}$ of the bags at $31\,000$ FCFA per bag. Calculate the amount she receives.", ["common fractions", "consumer arithmetic"], "faible", 2,
          [("You find $\\dfrac{3}{4}\\times40=30$ bags", 1), ("You calculate $30\\times31\\,000=930\\,000$ FCFA", 1)],
          r"Find the number of items first, then multiply by the selling price of one.",
          r"$\dfrac{3}{4}\times40=30$ bags. Amount received: $30\times31\,000=930\,000$.", r"$930\,000$ FCFA"),
        S("d", r"She sells the remaining bags at a $10\%$ discount on the price of $31\,000$ FCFA. Calculate the selling price of one of these bags.", ["percentages"], "faible", 2,
          [("You find the discount $\\dfrac{10}{100}\\times31\\,000=3\\,100$", 1), ("You subtract: $31\\,000-3\\,100=27\\,900$ FCFA", 1)],
          r"A discount of $r\%$ is subtracted from the original price; equivalently the new price is $(100-r)\%$ of the original.",
          r"Discount: $\dfrac{10}{100}\times31\,000=3\,100$. New price: $31\,000-3\,100=27\,900$. (Equivalently $0.9\times31\,000=27\,900$.)",
          r"$27\,900$ FCFA"),
        S("e", r"Calculate the amount she receives from the remaining bags.", ["consumer arithmetic"], "faible", 1,
          [("You calculate $10\\times27\\,900=279\\,000$ FCFA", 1)],
          r"The number of bags left is the total minus the number already sold.",
          r"$40-30=10$ bags remain, so she receives $10\times27\,900=279\,000$.", r"$279\,000$ FCFA"),
        S("f", r"Show that the total amount she receives is $1\,209\,000$ FCFA, and calculate her profit.", ["consumer arithmetic"], "faible", 2,
          [("You add $930\\,000+279\\,000=1\\,209\\,000$", 1), ("You calculate the profit $1\\,209\\,000-1\\,000\\,000=209\\,000$ FCFA", 1)],
          r"Profit is the selling price (total received) minus the cost price.",
          r"Total received: $930\,000+279\,000=1\,209\,000$. Profit: $1\,209\,000-1\,000\,000=209\,000$.", r"Profit $=209\,000$ FCFA"),
        S("g", r"Calculate her percentage profit.", ["percentages", "consumer arithmetic"], "moyenne", 3,
          [("You write $\\dfrac{\\text{profit}}{\\text{cost price}}\\times100$", 1), ("You substitute $\\dfrac{209\\,000}{1\\,000\\,000}\\times100$", 1), ("You obtain $20.9\\%$", 1)],
          r"Percentage profit $=\dfrac{\text{profit}}{\text{cost price}}\times100$, where the cost price is the total cost including transport.",
          r"$\dfrac{209\,000}{1\,000\,000}\times100=20.9$.", r"$20.9\%$",
          piege=r"Divide by the cost price $1\,000\,000$, not by the amount received $1\,209\,000$ (which gives about $17.3\%$)."),
        S("h", r"She shares the profit between her two sons in the ratio $5:3$. Calculate the larger share.", ["ratio and proportion"], "moyenne", 3,
          [("You find the total number of parts: $5+3=8$", 1), ("You find one part: $209\\,000\\div8=26\\,125$", 1), ("You calculate $5\\times26\\,125=130\\,625$ FCFA", 1)],
          r"To share in a ratio, add the parts, find the value of one part, then multiply by the number of parts of each share.",
          r"Number of parts: $5+3=8$. One part: $209\,000\div8=26\,125$. The larger share has $5$ parts: $5\times26\,125=130\,625$. (The smaller share is $3\times26\,125=78\,375$, and $130\,625+78\,375=209\,000$.)",
          r"$130\,625$ FCFA"),
    ]))

    # ------------------------------------------------------------------ B2 : statistiques et ensembles
    ex.append(E("B2", B, 15, "", [
        S("a", "The table shows the time, in minutes, taken by $60$ learners of a school in Garoua to walk to school.\n\n" + TABLE_TEMPS +
          "\n\nState the upper class boundary of the class $21-30$.", ["statistics"], "faible", 1,
          [("You state $30.5$", 1)],
          r"For classes of whole numbers, the class boundaries lie halfway between the end of one class and the start of the next.",
          r"The class $21-30$ ends at $30$ and the next class starts at $31$. The boundary between them is $\dfrac{30+31}{2}=30.5$.",
          r"$30.5$", groupe_local="(i) Statistics (10 marks)"),
        S("b", r"State the modal class.", ["statistics"], "faible", 1, [("You state $21-30$", 1)],
          r"The modal class is the class with the highest frequency.",
          r"The highest frequency is $20$, so the modal class is $21-30$.", r"$21-30$"),
        S("c", r"Find the class mark of each class.", ["statistics"], "faible", 2,
          [("You use $\\dfrac{\\text{lowest}+\\text{highest}}{2}$ for the classes", 1), ("You obtain $5.5,\\ 15.5,\\ 25.5,\\ 35.5,\\ 45.5,\\ 55.5$", 1)],
          r"The class mark is the midpoint of a class: the sum of its lowest and highest values divided by two.",
          r"For $1-10$: $\dfrac{1+10}{2}=5.5$. The classes have width $10$, so each following class mark is $10$ more.",
          r"$5.5,\ 15.5,\ 25.5,\ 35.5,\ 45.5,\ 55.5$"),
        S("d", r"Calculate the mean time to $2$ decimal places.", ["statistics"], "moyenne", 4,
          [("You calculate $fx$ for each class", 1), ("You find $\\sum fx=1\\,570$", 1), ("You write $\\dfrac{\\sum fx}{\\sum f}=\\dfrac{1\\,570}{60}$", 1), ("You obtain $26.17$ minutes", 1)],
          r"The mean of grouped data is $\dfrac{\sum fx}{\sum f}$, using the class marks $x$.",
          "Multiply each class mark by its frequency:\n\n" + TABLE_MOYENNE + "\n\n" +
          r"Mean $=\dfrac{1\,570}{60}=26.1666\ldots\approx26.17$ minutes.",
          r"$26.17$ minutes",
          piege=r"Divide by $\sum f=60$, the number of learners, not by the number of classes ($6$)."),
        S("e", r"Find the probability that a learner chosen at random takes more than $40$ minutes.", ["statistics", "probability"], "moyenne", 2,
          [("You add the frequencies of $41-50$ and $51-60$: $6+2=8$", 1), ("You write $\\dfrac{8}{60}=\\dfrac{2}{15}$", 1)],
          r"Probability $=\dfrac{\text{favourable}}{\text{total}}$; the favourable cases are the learners in the classes above the limit.",
          r"Learners who take more than $40$ minutes are in the classes $41-50$ and $51-60$: $6+2=8$. $P=\dfrac{8}{60}=\dfrac{2}{15}$.",
          r"$\dfrac{2}{15}$"),
        S("f", r"In a group of $52$ learners, $27$ belong to the music club $(M)$, $21$ belong to the drama club $(D)$ and $8$ belong to both clubs. Draw a Venn diagram showing the number of learners in each region.",
          ["set theory"], "moyenne", 2,
          [("You draw two overlapping circles inside a rectangle and write $8$ in the overlap", 1), ("You write $19$ and $13$ in the other two regions and $12$ outside", 1)],
          r"Start with the overlap, then subtract it from each club total to fill the rest of each circle.",
          r"Both clubs: $8$. Music only: $27-8=19$. Drama only: $21-8=13$. Neither club is found in the next part. See the figure below.",
          r"Music only $19$, both $8$, drama only $13$, neither $12$", fig="venn", groupe_local="(ii) Sets and probability (5 marks)"),
        S("g", r"Find the number of learners who belong to neither club.", ["set theory"], "faible", 1,
          [("You calculate $52-(19+8+13)=12$", 1)],
          r"The learners in neither club are the total minus all the learners who belong to at least one club.",
          r"Learners in at least one club: $19+8+13=40$. Neither club: $52-40=12$.", r"$12$"),
        S("h", r"Find the probability that a learner chosen at random belongs to exactly one of the two clubs.", ["probability", "set theory"], "elevee", 2,
          [("You add $19+13=32$", 1), ("You write $\\dfrac{32}{52}=\\dfrac{8}{13}$", 1)],
          r"'Exactly one' excludes the overlap: add the two regions that belong to one circle only.",
          r"Exactly one club: $19+13=32$ learners. $P=\dfrac{32}{52}=\dfrac{8}{13}$.", r"$\dfrac{8}{13}$",
          piege=r"$\dfrac{27+21}{52}$ counts the $8$ learners of the overlap twice."),
    ]))

    # ------------------------------------------------------------------ B3 : fonctions, suites, construction
    ex.append(E("B3", B, 15, "", [
        S("a", r"Two functions are defined for every real number $x$ by $f(x)=5-2x$ and $g(x)=x^{2}-4$. Calculate $f(-3)$.",
          ["functions and mappings"], "faible", 1, [("You obtain $f(-3)=11$", 1)],
          r"To evaluate a function, replace $x$ by the given value, keeping the brackets around a negative number.",
          r"$f(-3)=5-2(-3)=5+6=11$.", r"$11$", groupe_local="(i) Functions (7 marks)"),
        S("b", r"Find $f^{-1}(x)$.", ["functions and mappings"], "moyenne", 2,
          [("You write $y=5-2x$ and make $x$ the subject", 1), ("You obtain $f^{-1}(x)=\\dfrac{5-x}{2}$", 1)],
          r"To find an inverse, write $y=f(x)$, make $x$ the subject, then replace $y$ by $x$.",
          r"Let $y=5-2x$. Then $2x=5-y$, so $x=\dfrac{5-y}{2}$. Hence $f^{-1}(x)=\dfrac{5-x}{2}$.", r"$f^{-1}(x)=\dfrac{5-x}{2}$",
          conseil=r"Check: $f(3)=-1$ and $f^{-1}(-1)=\dfrac{5+1}{2}=3$."),
        S("c", r"Find $gf(x)$ and write it as a quadratic expression in $x$ in its simplest form.", ["functions and mappings"], "moyenne", 2,
          [("You write $gf(x)=g(5-2x)=(5-2x)^{2}-4$", 1), ("You expand and simplify to $4x^{2}-20x+21$", 1)],
          r"$gf(x)$ means apply $f$ first, then $g$ to the result: replace $x$ in $g$ by the expression for $f(x)$.",
          r"$gf(x)=g(5-2x)=(5-2x)^{2}-4=25-20x+4x^{2}-4=4x^{2}-20x+21$.", r"$gf(x)=4x^{2}-20x+21$",
          piege=r"$(5-2x)^{2}$ is not $25+4x^{2}$: the middle term $-20x$ must be written."),
        S("d", r"Solve the equation $gf(x)=0$.", ["functions and mappings", "quadratic equations"], "moyenne", 2,
          [("You factorise $4x^{2}-20x+21=(2x-3)(2x-7)$", 1), ("You obtain $x=\\dfrac{3}{2}$ or $x=\\dfrac{7}{2}$", 1)],
          r"Factorise the quadratic, set each factor equal to zero and solve each linear equation.",
          r"$4x^{2}-20x+21=0$ factorises as $(2x-3)(2x-7)=0$, because $2x\times(-7)+(-3)\times2x=-20x$. So $2x-3=0$ or $2x-7=0$. (Directly: $(5-2x)^{2}=4$ gives $5-2x=\pm2$.)",
          r"$x=\dfrac{3}{2}$ or $x=\dfrac{7}{2}$"),
        S("e", r"The first three terms of a geometric sequence are $4,\ 12,\ 36,\ \dots$ Find the common ratio.", ["sequences and series"], "faible", 1,
          [("You write $\\dfrac{12}{4}=3$", 1)],
          r"In a geometric sequence each term is the previous term multiplied by the common ratio $r$, so $r=\dfrac{T_{2}}{T_{1}}$.",
          r"$r=\dfrac{12}{4}=3$. Check: $\dfrac{36}{12}=3$.", r"$3$", groupe_local="(ii) Sequences (3 marks)"),
        S("f", r"Find the $6$th term.", ["sequences and series"], "faible", 1,
          [("You calculate $4\\times3^{5}=972$", 1)],
          r"The $n$th term of a geometric sequence is $ar^{n-1}$.",
          r"$T_{6}=4\times3^{6-1}=4\times243=972$.", r"$972$",
          piege=r"The power is $n-1=5$, not $6$."),
        S("g", r"Find the sum of the first $5$ terms.", ["sequences and series"], "faible", 1,
          [("You calculate $\\dfrac{4(3^{5}-1)}{3-1}=484$", 1)],
          r"The sum of the first $n$ terms of a geometric sequence is $S_{n}=\dfrac{a(r^{n}-1)}{r-1}$ for $r\neq1$.",
          r"$S_{5}=\dfrac{4(3^{5}-1)}{3-1}=\dfrac{4\times242}{2}=484$. Check by adding: $4+12+36+108+324=484$.", r"$484$"),
        S("h", r"Using a pencil, a ruler and a pair of compasses only, construct the triangle $ABC$ in which $AB=6$ cm, $BC=5$ cm and $AC=4$ cm.",
          ["geometric construction"], "moyenne", 3,
          [("You draw $AB=6$ cm and label the end points", 1), ("You draw arcs of radius $5$ cm from $B$ and $4$ cm from $A$ that meet at $C$", 1),
           ("You join $AC$ and $BC$ and keep the construction arcs visible", 1)],
          r"To construct a triangle from three sides, draw one side, then draw two arcs whose radii are the other two sides, centred on the ends of the first side.",
          r"Draw $AB=6$ cm. With the compasses set to $5$ cm and centre $B$, draw an arc above $AB$. Set the compasses to $4$ cm and with centre $A$ draw an arc that cuts the first arc at $C$. Join $CA$ and $CB$. The result is shown in the figure after part j.",
          r"Triangle $ABC$ drawn with $AB=6$ cm, $BC=5$ cm, $AC=4$ cm", groupe_local="(iii) Construction (5 marks)"),
        S("i", r"Construct the bisector of the angle $ABC$ and let it meet $AC$ at $D$.", ["geometric construction"], "moyenne", 1,
          [("You draw an arc from $B$ cutting $BA$ and $BC$, then two equal arcs that cross, and join the crossing to $B$ to meet $AC$ at $D$", 1)],
          r"To bisect an angle, draw an arc from the vertex cutting both arms, then equal arcs from those two points; the line through their crossing and the vertex is the bisector.",
          r"With centre $B$ draw an arc cutting $BA$ and $BC$. With the same radius and centres on those two points draw arcs that cross inside the angle. Join $B$ to the crossing point and extend it until it meets $AC$ at $D$.",
          r"Bisector of angle $ABC$ drawn, meeting $AC$ at $D$"),
        S("j", r"Measure and state the length of $BD$.", ["geometric construction"], "faible", 1,
          [("You state a length between $5.0$ cm and $5.2$ cm", 1)],
          r"When a length is read from a drawing, give it to the nearest millimetre; an accurate drawing gives a value within $0.1$ cm of the exact one.",
          r"On an accurate construction, $BD\approx5.1$ cm (exact calculation: $BD=\sqrt{AB\times BC\left(1-\dfrac{AC^{2}}{(AB+BC)^{2}}\right)}=\sqrt{30\times\dfrac{105}{121}}\approx5.10$ cm). Any value from $5.0$ cm to $5.2$ cm is accepted.",
          r"$BD\approx5.1$ cm", fig="construction"),
    ]))

    # ------------------------------------------------------------------ B4 : courbe et equation du second degre
    ex.append(E("B4", B, 15, "", [
        S("a", "The function $f$ is given by $f(x)=x^{2}+x-6$ for $-4\\leq x\\leq3$. Copy and complete the table of values.\n\n" + TABLE_VALEURS,
          ["graphs"], "faible", 2,
          [("You find $f(-3)=0$ and $f(-1)=-6$", 1), ("You find $f(1)=-4$ and $f(3)=6$", 1)],
          r"Complete a table of values by substituting each value of $x$ into the formula, keeping the brackets around negative numbers.",
          r"$f(-3)=9-3-6=0$. $f(-1)=1-1-6=-6$. $f(1)=1+1-6=-4$. $f(3)=9+3-6=6$." + "\n\n" + TABLE_VALEURS_COMPLETE,
          r"$f(-3)=0,\ f(-1)=-6,\ f(1)=-4,\ f(3)=6$", groupe_local="(i) Graph (10 marks)"),
        S("b", r"Using a scale of $2$ cm to $1$ unit on the $x$-axis and $1$ cm to $1$ unit on the $y$-axis, draw the graph of $y=f(x)$.",
          ["graphs"], "moyenne", 3,
          [("You draw and graduate both axes with the stated scales", 1), ("You plot the eight points accurately", 1), ("You join them with a smooth curve", 1)],
          r"To draw a curve, plot every point of the table accurately, then join them with one smooth curve, never with straight segments.",
          r"Draw the $x$-axis from $-4$ to $3$ (with $2$ cm per unit) and the $y$-axis from $-7$ to $7$ ($1$ cm per unit). Plot $(-4,\ 6)$, $(-3,\ 0)$, $(-2,\ -4)$, $(-1,\ -6)$, $(0,\ -6)$, $(1,\ -4)$, $(2,\ 0)$ and $(3,\ 6)$ and join them with a smooth curve. The expected graph is shown in the figure after part f.",
          r"Parabola through the eight points, lowest point near $(-0.5,\ -6.25)$"),
        S("c", r"Use your graph to solve the equation $x^{2}+x-6=0$.", ["graphs", "quadratic equations"], "faible", 1,
          [("You read the $x$-coordinates where the curve crosses the $x$-axis: $-3$ and $2$", 1)],
          r"The solutions of $f(x)=0$ are the $x$-coordinates of the points where the curve meets the $x$-axis.",
          r"The curve crosses the $x$-axis at $x=-3$ and $x=2$. (Check by factorising: $(x+3)(x-2)=0$.)", r"$x=-3$ or $x=2$"),
        S("d", r"Write down the equation of the line of symmetry of the curve.", ["graphs"], "moyenne", 1,
          [("You state $x=-0.5$", 1)],
          r"The line of symmetry of a parabola is the vertical line midway between two points of the curve that have the same $y$-value.",
          r"The curve crosses the $x$-axis at $-3$ and $2$, so the line of symmetry is $x=\dfrac{-3+2}{2}=-0.5$.", r"$x=-0.5$"),
        S("e", r"Write down the minimum value of $f(x)$.", ["graphs"], "moyenne", 1,
          [("You state $-6.25$ (a reading of about $-6.3$ is accepted)", 1)],
          r"The minimum value of a parabola that opens upwards is the $y$-coordinate of its lowest point, on the line of symmetry.",
          r"At $x=-0.5$: $f(-0.5)=0.25-0.5-6=-6.25$. Read from the graph, the lowest point is at about $y=-6.3$.", r"$-6.25$"),
        S("f", r"By drawing a suitable straight line on your graph, solve the equation $x^{2}+x-2=0$.", ["graphs", "quadratic equations"], "elevee", 2,
          [("You draw the line $y=-4$", 1), ("You read $x=-2$ and $x=1$", 1)],
          r"To solve $f(x)=k$ graphically, draw the horizontal line $y=k$ and read the $x$-coordinates of the points where it meets the curve.",
          r"$x^{2}+x-2=0$ is the same as $x^{2}+x-6=-4$. Draw the line $y=-4$: it meets the curve at $x=-2$ and $x=1$. (Check: $(x+2)(x-1)=x^{2}+x-2$.)",
          r"$x=-2$ or $x=1$", fig="parabole"),
        S("g", r"The length of a rectangle is $3$ cm more than its width. The width is $x$ cm and the area is $40\ \text{cm}^{2}$. Show that $x^{2}+3x-40=0$.",
          ["quadratic equations"], "faible", 1,
          [("You write $x(x+3)=40$ and expand", 1)],
          r"The area of a rectangle is length times width; write the length in terms of $x$ before forming the equation.",
          r"The length is $(x+3)$ cm, so $x(x+3)=40$. Expanding: $x^{2}+3x=40$, so $x^{2}+3x-40=0$.", r"$x^{2}+3x-40=0$",
          groupe_local="(ii) Quadratic equation (5 marks)"),
        S("h", r"Solve the equation $x^{2}+3x-40=0$.", ["quadratic equations"], "moyenne", 3,
          [("You find two numbers with product $-40$ and sum $3$", 1), ("You factorise $(x+8)(x-5)=0$", 1), ("You obtain $x=-8$ or $x=5$", 1)],
          r"To factorise $x^{2}+bx+c$, find two numbers whose product is $c$ and whose sum is $b$, then set each factor equal to zero.",
          r"The numbers with product $-40$ and sum $3$ are $8$ and $-5$. So $(x+8)(x-5)=0$, which gives $x=-8$ or $x=5$.", r"$x=-8$ or $x=5$"),
        S("i", r"State the dimensions of the rectangle and calculate its perimeter.", ["quadratic equations"], "moyenne", 1,
          [("You reject $x=-8$, state $5$ cm by $8$ cm, and find the perimeter $26$ cm", 1)],
          r"A length cannot be negative: reject any solution that gives a negative dimension, then return to the question asked.",
          r"A width cannot be negative, so $x=5$. The width is $5$ cm and the length is $5+3=8$ cm. Check the area: $5\times8=40$. Perimeter: $2(5+8)=26$ cm.",
          r"$5$ cm by $8$ cm, perimeter $26$ cm"),
    ]))

    return ex
