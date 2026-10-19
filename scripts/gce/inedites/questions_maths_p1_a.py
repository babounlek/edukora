"""Questions 1 a 25 de l'epreuve inedite GCE O Level Mathematics Paper 1 n.1 (voir generer_maths_p1.py)."""


def Q(n, themes, diff, stem, ok, bad, rappel, sol, piege=None, conseil=None, fig=None):
    return dict(n=n, themes=themes, diff=diff, stem=stem, ok=ok, bad=bad, rappel=rappel, sol=sol,
                piege=piege, conseil=conseil, fig=fig)


def questions():
    qs = []
    a = qs.append

    a(Q(1, ["order of operations", "arithmetic"], "faible",
        r"The value of $20-3\times4\div2$ is",
        r"$14$", [r"$34$", r"$6$", r"$26$"],
        r"Do brackets first, then multiplication and division from left to right, then addition and subtraction.",
        r"Multiplication and division come before subtraction. From left to right: $3\times4=12$, then $12\div2=6$. Finally $20-6=14$.",
        r"Working through the whole expression from left to right gives $\dfrac{(20-3)\times4}{2}=34$, which ignores the order of operations."))

    a(Q(2, ["arithmetic"], "faible",
        r"The Lowest Common Multiple (LCM) of $12$, $18$ and $30$ is",
        r"$180$", [r"$6$", r"$90$", r"$360$"],
        r"The Lowest Common Multiple is found by writing each number as a product of prime factors and taking the highest power of every prime that appears.",
        r"$12=2^{2}\times3$, $18=2\times3^{2}$ and $30=2\times3\times5$. The highest powers are $2^{2}$, $3^{2}$ and $5$, so the LCM is $4\times9\times5=180$.",
        r"$6$ is the Highest Common Factor (lowest powers of the common primes). $360=12\times30$ is a common multiple but it is not the lowest one."))

    a(Q(3, ["decimal numbers"], "faible",
        r"Arranged in descending order, the numbers $0.409,\ 0.49,\ 0.4,\ 0.094$ are",
        r"$0.49,\ 0.409,\ 0.4,\ 0.094$",
        [r"$0.094,\ 0.4,\ 0.409,\ 0.49$", r"$0.409,\ 0.49,\ 0.4,\ 0.094$", r"$0.49,\ 0.4,\ 0.409,\ 0.094$"],
        r"To compare decimals, write them with the same number of decimal places, then compare them as whole numbers.",
        r"With three decimal places the numbers become $0.409,\ 0.490,\ 0.400,\ 0.094$. In descending order: $0.490>0.409>0.400>0.094$.",
        r"A longer decimal is not a larger decimal. $0.409$ is smaller than $0.49$ because $0.490>0.409$."))

    a(Q(4, ["common fractions"], "faible",
        r"$2\dfrac{1}{4}+1\dfrac{2}{3}$ is equal to",
        r"$3\dfrac{11}{12}$", [r"$3\dfrac{3}{7}$", r"$3\dfrac{7}{12}$", r"$2\dfrac{11}{12}$"],
        r"To add mixed numbers, add the whole parts and add the fractional parts over a common denominator.",
        r"Whole parts: $2+1=3$. Fractional parts: $\dfrac{1}{4}+\dfrac{2}{3}=\dfrac{3}{12}+\dfrac{8}{12}=\dfrac{11}{12}$. The sum is $3\dfrac{11}{12}$.",
        r"Adding the numerators together and the denominators together gives $\dfrac{3}{7}$. Fractions can only be added after they are written with the same denominator."))

    a(Q(5, ["standard form"], "faible",
        r"The number $0.00047$ written in standard form is",
        r"$4.7\times10^{-4}$", [r"$4.7\times10^{-3}$", r"$4.7\times10^{4}$", r"$47\times10^{-5}$"],
        r"A number in standard form is written $a\times10^{n}$ with $1\leq a<10$; for a number smaller than $1$, $n$ is negative and gives the number of places the decimal point moves to the right.",
        r"Move the decimal point $4$ places to the right to reach $4.7$, which lies between $1$ and $10$. Therefore $0.00047=4.7\times10^{-4}$.",
        r"$47\times10^{-5}$ is the same number but it is not in standard form, since $47$ is not between $1$ and $10$. $4.7\times10^{-3}$ moves the decimal point only $3$ places."))

    a(Q(6, ["significant figures"], "faible",
        r"The number $48\,639$ correct to $2$ significant figures is",
        r"$49\,000$", [r"$48\,000$", r"$4\,900$", r"$49$"],
        r"To round to $n$ significant figures, keep the first $n$ digits from the left, round on the next digit, and fill the remaining places with zeros.",
        r"The first two significant figures are $4$ and $8$. The next digit is $6$, which is at least $5$, so the $8$ rounds up to $9$. The zeros keep the size of the number: $49\,000$.",
        r"$48\,000$ forgets to round up. $4\,900$ and $49$ change the size of the number, because the place values were not kept with zeros."))

    a(Q(7, ["ratio and proportion"], "faible",
        r"Mr Fomba shares $240\,000$ FCFA among his three grandchildren in the ratio $3:5:4$. The largest share is",
        r"$100\,000$ FCFA", [r"$60\,000$ FCFA", r"$80\,000$ FCFA", r"$120\,000$ FCFA"],
        r"To share in a given ratio, add the parts, find the value of one part, then multiply it by the number of parts of each share.",
        r"The number of parts is $3+5+4=12$, so one part is $240\,000\div12=20\,000$ FCFA. The largest share has $5$ parts: $5\times20\,000=100\,000$ FCFA.",
        r"$60\,000$ and $80\,000$ are the other two shares ($3$ and $4$ parts). Read the question again: it asks for the largest share."))

    a(Q(8, ["percentages"], "faible",
        r"The price of a pair of football boots rises from $8\,000$ FCFA to $9\,200$ FCFA. The percentage increase is",
        r"$15\%$", [r"$12\%$", r"$13\%$", r"$115\%$"],
        r"A percentage change is the change divided by the original value, multiplied by $100$.",
        r"The increase is $9\,200-8\,000=1\,200$ FCFA. Percentage increase $=\dfrac{1\,200}{8\,000}\times100=15\%$.",
        r"The original price is always the base. Dividing by the new price $9\,200$ gives about $13\%$, and $115\%$ is the new price as a percentage of the old one, not the increase."))

    a(Q(9, ["consumer arithmetic"], "moyenne",
        r"Ayuk invests $450\,000$ FCFA at a simple interest rate of $6\%$ per annum. The total amount in his account after $3$ years is",
        r"$531\,000$ FCFA", [r"$81\,000$ FCFA", r"$477\,000$ FCFA", r"$27\,000$ FCFA"],
        r"Simple interest is $I=\dfrac{P\times R\times T}{100}$, and the final amount is the principal plus the interest.",
        r"$I=\dfrac{450\,000\times6\times3}{100}=81\,000$ FCFA. The amount is $450\,000+81\,000=531\,000$ FCFA.",
        r"$81\,000$ FCFA is only the interest, while the question asks for the total amount. $27\,000$ FCFA is the interest for one year and $477\,000$ FCFA the amount after one year."))

    a(Q(10, ["set theory"], "faible",
        r"In Figure 1, the numbers show how many learners belong to each region of the Venn diagram, where $A$ and $B$ are two clubs. The value of $n(A'\cap B)$ is",
        r"$11$", [r"$6$", r"$14$", r"$17$"],
        r"$A'\cap B$ is the set of elements that belong to $B$ but not to $A$: read the part of circle $B$ that lies outside the overlap.",
        r"$A'$ is everything outside circle $A$. Its overlap with $B$ is the part of $B$ that is not in $A$, which contains $11$ elements. So $n(A'\cap B)=11$.",
        r"$17=n(B)$ counts the overlap as well ($11+6$), and $14$ is the number of elements outside both circles.",
        fig="venn"))

    a(Q(11, ["set theory"], "faible",
        r"A set with $4$ elements has exactly how many subsets?",
        r"$16$", [r"$8$", r"$4$", r"$15$"],
        r"A set with $n$ elements has $2^{n}$ subsets, counting the empty set and the set itself.",
        r"$2^{4}=16$. For example the set $\{a,b,c,d\}$ has $1$ empty subset, $4$ subsets of one element, $6$ of two, $4$ of three and $1$ of four: $1+4+6+4+1=16$.",
        r"$15$ is the number of proper subsets: it leaves out the set itself, which is also a subset."))

    a(Q(12, ["set theory"], "moyenne",
        r"In a class of $45$ learners, $28$ study Physics, $22$ study Chemistry and $8$ study neither subject. The number of learners who study both subjects is",
        r"$13$", [r"$5$", r"$8$", r"$17$"],
        r"Use $n(P\cup C)=n(P)+n(C)-n(P\cap C)$, remembering that $n(P\cup C)$ leaves out those who belong to neither set.",
        r"Learners who study at least one subject: $45-8=37$. Then $37=28+22-n(P\cap C)$, so $n(P\cap C)=50-37=13$.",
        r"Forgetting the $8$ learners who study neither subject gives $28+22-45=5$."))

    a(Q(13, ["logic"], "faible",
        r"Let $p$: Tabi passes Mathematics and $q$: Tabi wins a prize. The contrapositive of $p\to q$ is",
        r"${\sim}q\to{\sim}p$", [r"$q\to p$", r"${\sim}p\to{\sim}q$", r"$p\to{\sim}q$"],
        r"For the implication $p\to q$, the converse is $q\to p$, the inverse is ${\sim}p\to{\sim}q$ and the contrapositive is ${\sim}q\to{\sim}p$; only the contrapositive is always equivalent to $p\to q$.",
        r"The contrapositive reverses the implication and negates both statements: ${\sim}q\to{\sim}p$. In words: if Tabi does not win a prize, then Tabi did not pass Mathematics.",
        r"$q\to p$ is the converse and ${\sim}p\to{\sim}q$ is the inverse. Neither is equivalent to $p\to q$."))

    a(Q(14, ["functions and mappings"], "faible",
        r"Figure 2 shows the mapping $x\mapsto x^{2}$ from the domain $\{-1,\ 0,\ 1,\ 2\}$ to a set of numbers. The range of the mapping is",
        r"$\{0,\ 1,\ 4\}$", [r"$\{0,\ 1,\ 2,\ 4,\ 5\}$", r"$\{-1,\ 0,\ 1,\ 2\}$", r"$\{1,\ 4\}$"],
        r"The range of a mapping is the set of images that the arrows actually reach; the codomain may contain extra elements that receive no arrow.",
        r"Follow each arrow: $-1\to1$, $0\to0$, $1\to1$ and $2\to4$. The images are $1,\ 0,\ 1,\ 4$. Writing each value once, the range is $\{0,\ 1,\ 4\}$.",
        r"$\{0,\ 1,\ 2,\ 4,\ 5\}$ is the whole right-hand set (the codomain), not the range: $2$ and $5$ receive no arrow.",
        r"Count the arrows that end on each element of the right-hand set. An element with no arrow is not in the range.",
        fig="mapping"))

    a(Q(15, ["functions and mappings"], "moyenne",
        r"Given that $f(x)=2x+3$ and $g(x)=x^{2}-1$, the value of $gf(2)$ is",
        r"$48$", [r"$9$", r"$10$", r"$21$"],
        r"$gf(x)$ means that $f$ is applied first and $g$ is applied to the result.",
        r"$f(2)=2(2)+3=7$. Then $g(7)=7^{2}-1=48$.",
        r"Applying $g$ first gives $fg(2)=f(3)=9$. The sum $f(2)+g(2)=10$ and the product $f(2)\times g(2)=21$ are not composite functions."))

    a(Q(16, ["functions and mappings"], "faible",
        r"The inverse of the function $f:x\mapsto3x-4$ is $f^{-1}:x\mapsto$",
        r"$\dfrac{x+4}{3}$", [r"$\dfrac{x-4}{3}$", r"$3x+4$", r"$\dfrac{1}{3x-4}$"],
        r"To find an inverse function, write $y=f(x)$, make $x$ the subject, then replace $y$ by $x$.",
        r"Let $y=3x-4$. Then $y+4=3x$, so $x=\dfrac{y+4}{3}$. Hence $f^{-1}(x)=\dfrac{x+4}{3}$.",
        r"$\dfrac{1}{3x-4}$ is the reciprocal of $f(x)$, not its inverse. Moving $-4$ to the other side must change its sign.",
        r"Check with a number: $f(3)=5$ and $f^{-1}(5)=\dfrac{5+4}{3}=3$, which returns the starting value."))

    a(Q(17, ["angles and polygons"], "faible",
        r"In Figure 3, $AB$ is parallel to $CD$ and the line $PQ$ cuts them at $P$ and $Q$. Given that $\angle BPQ=118^\circ$, the angle $x=\angle PQD$ is",
        r"$62^\circ$", [r"$118^\circ$", r"$72^\circ$", r"$152^\circ$"],
        r"When a transversal cuts two parallel lines, co-interior angles add up to $180^\circ$, while alternate angles are equal and corresponding angles are equal.",
        r"$\angle BPQ$ and $\angle PQD$ lie between the parallel lines on the same side of $PQ$, so they are co-interior angles. Therefore $\angle PQD=180^\circ-118^\circ=62^\circ$.",
        r"$118^\circ$ is the alternate angle $\angle PQC$, not $\angle PQD$. Decide which pair of angles you have before choosing the rule.",
        fig="paralleles"))

    a(Q(18, ["angles and polygons"], "moyenne",
        r"The sum of the interior angles of a regular polygon is $1440^\circ$. Each exterior angle of the polygon is",
        r"$36^\circ$", [r"$18^\circ$", r"$40^\circ$", r"$144^\circ$"],
        r"The interior angles of an $n$-sided polygon add up to $(n-2)\times180^\circ$, and the exterior angles of any polygon add up to $360^\circ$.",
        r"$(n-2)\times180=1440$ gives $n-2=8$, so $n=10$. Each exterior angle of a regular decagon is $\dfrac{360^\circ}{10}=36^\circ$.",
        r"$144^\circ$ is each interior angle ($1440^\circ\div10$). The question asks for the exterior angle."))

    a(Q(19, ["similar triangles"], "moyenne",
        r"Triangles $ABC$ and $PQR$ are similar, with $AB$ corresponding to $PQ$ and $BC$ corresponding to $QR$. Given that $AB=6$ cm, $PQ=9$ cm and $BC=14$ cm, the length of $QR$ is",
        r"$21$ cm", [r"$9.3$ cm", r"$17$ cm", r"$31.5$ cm"],
        r"In similar figures, corresponding lengths are in the same ratio: the scale factor.",
        r"The scale factor from $ABC$ to $PQR$ is $\dfrac{PQ}{AB}=\dfrac{9}{6}=1.5$. So $QR=1.5\times14=21$ cm.",
        r"Using the inverse ratio gives $14\times\dfrac{6}{9}\approx9.3$ cm. Squaring the scale factor, which is correct for areas only, gives $31.5$ cm."))

    a(Q(20, ["mensuration"], "faible",
        r"Figure 4 shows a plane shape in which all the angles are right angles. Its area, in $\text{cm}^{2}$, is",
        r"$81$", [r"$88$", r"$96$", r"$111$"],
        r"For a composite shape, find the area of the enclosing rectangle and subtract the missing rectangle, or split the shape into rectangles and add their areas.",
        r"The enclosing rectangle measures $12$ cm by $8$ cm, so its area is $96\ \text{cm}^{2}$. The missing corner has width $12-7=5$ cm and height $3$ cm, so its area is $15\ \text{cm}^{2}$. The area of the shape is $96-15=81\ \text{cm}^{2}$.",
        r"$96$ ignores the missing corner and $111$ adds it instead of removing it. The width of the corner is not given directly: it is $12-7$.",
        fig="forme_L"))

    a(Q(21, ["mensuration"], "moyenne",
        r"A cylindrical water tank has diameter $140$ cm and height $1$ m. Taking $\pi=\dfrac{22}{7}$, the capacity of the tank, in litres, is",
        r"$1\,540$", [r"$154$", r"$6\,160$", r"$1\,540\,000$"],
        r"The volume of a cylinder is $\pi r^{2}h$ where $r$ is the radius; to change cm$^{3}$ into litres divide by $1\,000$.",
        r"The radius is $140\div2=70$ cm and the height is $100$ cm. $V=\dfrac{22}{7}\times70^{2}\times100=\dfrac{22}{7}\times4\,900\times100=1\,540\,000\ \text{cm}^{3}$. Since $1$ litre is $1\,000\ \text{cm}^{3}$, the capacity is $1\,540$ litres.",
        r"$1\,540\,000$ is the volume in $\text{cm}^{3}$, and $6\,160$ comes from using the diameter in place of the radius.",
        r"Write all lengths in the same unit before substituting: here the height $1$ m is $100$ cm."))

    a(Q(22, ["mensuration"], "faible",
        r"The cuboid in Figure 5 has length $9$ cm, width $5$ cm and height $4$ cm. Its total surface area, in $\text{cm}^{2}$, is",
        r"$202$", [r"$101$", r"$162$", r"$180$"],
        r"The total surface area of a cuboid is $2(lw+lh+wh)$: it has three pairs of equal rectangular faces.",
        r"$lw=9\times5=45$, $lh=9\times4=36$ and $wh=5\times4=20$. The area is $2(45+36+20)=2\times101=202\ \text{cm}^{2}$.",
        r"$180$ is the volume ($9\times5\times4$), $101$ is only half of the surface and $162$ misses the pair of faces $5$ cm by $4$ cm.",
        fig="cuboid"))

    a(Q(23, ["mensuration", "circle"], "moyenne",
        r"A sector of a circle has radius $14$ cm and an angle of $135^\circ$ at the centre. Taking $\pi=\dfrac{22}{7}$, the length of its arc, in cm, is",
        r"$33$", [r"$66$", r"$88$", r"$231$"],
        r"The arc length of a sector is $\dfrac{\theta}{360}\times2\pi r$ and its area is $\dfrac{\theta}{360}\times\pi r^{2}$.",
        r"The circumference is $2\pi r=2\times\dfrac{22}{7}\times14=88$ cm. The arc is $\dfrac{135}{360}\times88=\dfrac{3}{8}\times88=33$ cm.",
        r"$88$ is the whole circumference and $231$ is the area of the sector ($\dfrac{3}{8}\times616$), measured in $\text{cm}^{2}$."))

    a(Q(24, ["circle theorems"], "moyenne",
        r"In Figure 6, $O$ is the centre of the circle and $A$, $B$ and $C$ are points on the circumference. Given that $\angle ACB=34^\circ$, the angle $\angle OAB$ is",
        r"$56^\circ$", [r"$34^\circ$", r"$68^\circ$", r"$112^\circ$"],
        r"The angle at the centre is twice the angle at the circumference standing on the same arc, and a triangle with two radii as sides is isosceles.",
        r"$\angle AOB=2\times\angle ACB=2\times34^\circ=68^\circ$. Triangle $OAB$ is isosceles because $OA=OB$ are radii, so $\angle OAB=\dfrac{180^\circ-68^\circ}{2}=56^\circ$.",
        r"$68^\circ$ is the angle at the centre. $112^\circ$ is the sum of the two equal base angles of the triangle $OAB$, not one of them.",
        fig="cercle"))

    a(Q(25, ["coordinate geometry"], "faible",
        r"The gradient of the line joining $P(-2,\ 5)$ and $Q(4,\ -7)$ is",
        r"$-2$", [r"$2$", r"$-\dfrac{1}{2}$", r"$\dfrac{1}{2}$"],
        r"The gradient of the line through $(x_1,y_1)$ and $(x_2,y_2)$ is $\dfrac{y_2-y_1}{x_2-x_1}$: the change in $y$ over the change in $x$.",
        r"$m=\dfrac{-7-5}{4-(-2)}=\dfrac{-12}{6}=-2$.",
        r"Writing the change in $x$ over the change in $y$ gives $-\dfrac{1}{2}$. Keep the same order of subtraction in the numerator and in the denominator."))

    return qs
