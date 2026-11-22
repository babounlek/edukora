r"""Les 8 exercices de l'epreuve inedite GCE A Level Pure Mathematics with Statistics Paper 3 n.1 (100 marks, 3 h, tout obligatoire).

Structure mesuree sur les Paper 3 de 2024, 2025 et 2026 (8 exercices de 3 a 5 parties, probabilites, donnees groupees, variables aleatoires
discretes et continues, binomiale, Poisson, loi normale, regression) ; aucune donnee, aucun contexte ni aucun jeu de nombres repris d'un sujet reel.
Plan du blueprint bp-cm-gce-al-pmstatistics-p3-1 : 12, 12, 12, 13, 13, 12, 13, 13 points. Chaque sous-question : bareme exact (`pts`), grille `crit`
(somme = pts), rappel, resolution, reponse finale `ans` (recalculee par verifier_reponses_pm_statistics_p3.py). Chaines BRUTES. Numeros affiches : a, b, c...
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from questions_addmaths_p2_a import E, S  # noqa: E402,F401

G = ""


def exercices():
    ex = []

    # ---- Exercice 1 : probability rules (12) ----
    ex.append(E("1", G, 12, r"", [
        S("a", r"In an Upper Sixth class of a school in Bafoussam, a student chosen at random studies Geography ($G$) with probability $0.40$, Economics ($E$) with probability $0.35$, and both subjects with probability $0.15$. Find the probability that the student studies Geography or Economics (or both), and the probability that the student studies neither subject.",
          ["probability rules statistics"], "faible", 3,
          [(r"You use $P(G\cup E)=P(G)+P(E)-P(G\cap E)$", 1), (r"You obtain $P(G\cup E)=0.40+0.35-0.15=0.60$", 1), (r"You obtain $P(\text{neither})=1-0.60=0.40$", 1)],
          r"For any two events, $P(A\cup B)=P(A)+P(B)-P(A\cap B)$, and the probability that neither event occurs is the complement of the probability that at least one occurs.",
          r"$P(G\cup E)=P(G)+P(E)-P(G\cap E)=0.40+0.35-0.15=0.60$. The probability of neither subject is $1-P(G\cup E)=1-0.60=0.40$.",
          ans=r"$P(G\cup E)=0.60$ ; $P(\text{neither})=0.40$"),
        S("b", r"Determine whether the events $G$ and $E$ in part (a) are independent. Find also the probability that a student studies Geography, given that the student studies Economics.",
          ["probability rules statistics", "conditional probability statistics"], "faible", 3,
          [(r"You compute $P(G)\times P(E)=0.40\times0.35=0.14$", 1), (r"You conclude that $G$ and $E$ are not independent because $0.14\neq0.15$", 1), (r"You find $P(G\mid E)=\dfrac{0.15}{0.35}=\dfrac37\approx0.4286$", 1)],
          r"Two events are independent exactly when $P(A\cap B)=P(A)P(B)$; the conditional probability of $A$ given $B$ is $P(A\mid B)=\dfrac{P(A\cap B)}{P(B)}$.",
          r"If $G$ and $E$ were independent, $P(G\cap E)$ would equal $P(G)P(E)=0.40\times0.35=0.14$. The given value is $0.15$, so the events are not independent. Next, $P(G\mid E)=\dfrac{P(G\cap E)}{P(E)}=\dfrac{0.15}{0.35}=\dfrac37\approx0.4286$. This differs from $P(G)=0.40$, which agrees with the lack of independence.",
          ans=r"not independent ; $P(G\mid E)=\dfrac37\approx0.4286$"),
        S("c", r"A bakery in Douala bakes its loaves in two ovens. Oven $A$ bakes $55\%$ of the loaves and oven $B$ bakes the rest. A loaf from oven $A$ is under-baked with probability $0.04$ and a loaf from oven $B$ is under-baked with probability $0.07$. A loaf is chosen at random. Find the probability that it is under-baked.",
          ["probability rules statistics", "conditional probability statistics"], "moyenne", 3,
          [(r"You find $P(A\cap U)=0.55\times0.04=0.022$", 1), (r"You find $P(B\cap U)=0.45\times0.07=0.0315$", 1), (r"You add the two branches: $P(U)=0.0535$", 1)],
          r"When the sample space is split into exclusive cases, the probability of an event is the sum, over the cases, of the probability of the case multiplied by the conditional probability of the event in that case.",
          r"Let $U$ be the event that the loaf is under-baked. The loaf is under-baked either from oven $A$ or from oven $B$: $P(U)=P(A)P(U\mid A)+P(B)P(U\mid B)=0.55\times0.04+0.45\times0.07=0.022+0.0315=0.0535$.",
          ans=r"$P(U)=0.0535$"),
        S("d", r"Given that the loaf chosen in part (c) is under-baked, find the probability that it was baked in oven $B$.",
          ["conditional probability statistics"], "moyenne", 3,
          [(r"You write $P(B\mid U)=\dfrac{P(B\cap U)}{P(U)}$", 1), (r"You substitute $\dfrac{0.0315}{0.0535}$", 1), (r"You obtain $\dfrac{63}{107}\approx0.5888$", 1)],
          r"Reversing a conditioning uses $P(B\mid U)=\dfrac{P(B\cap U)}{P(U)}$, where the numerator is the probability of the branch and the denominator is the total probability of the event that is known to have occurred.",
          r"$P(B\mid U)=\dfrac{P(B\cap U)}{P(U)}=\dfrac{0.0315}{0.0535}=\dfrac{63}{107}\approx0.5888$.",
          ans=r"$\dfrac{63}{107}\approx0.5888$",
          piege=r"Do not answer $0.07$: that is $P(U\mid B)$, the probability that a loaf is under-baked given that it came from oven $B$, which is a different quantity."),
    ]))

    # ---- Exercice 2 : counting and binomial distribution (12) ----
    ex.append(E("2", G, 12, r"", [
        S("a", r"(i) Find the number of different arrangements of all the letters of the word BAMENDA. (ii) Find how many of these arrangements have the two letters A not next to each other.",
          ["permutations and combinations"], "faible", 3,
          [(r"You count the arrangements of $7$ letters with $A$ repeated: $\dfrac{7!}{2!}=2520$", 1), (r"You count the arrangements with the two $A$s together by treating them as one block: $6!=720$", 1), (r"You subtract: $2520-720=1800$", 1)],
          r"The number of arrangements of $n$ letters of which $r$ are identical is $\dfrac{n!}{r!}$; to count arrangements with a condition of the type *not together*, count all of them and subtract those in which the objects are together.",
          r"(i) The word has $7$ letters with $A$ occurring twice, so there are $\dfrac{7!}{2!}=\dfrac{5040}{2}=2520$ arrangements. (ii) If the two $A$s are together, treat $AA$ as one block: the block and the other five letters give $6$ objects, all different, so $6!=720$ arrangements. The number with the $A$s apart is $2520-720=1800$.",
          ans=r"(i) $2520$ ; (ii) $1800$"),
        S("b", r"In a repair shop in Douala, each phone brought in has, independently of the others, a probability $0.2$ of having a faulty battery. A batch of $15$ phones arrives, and $X$ is the number of phones in the batch with a faulty battery. Find $P(X=3)$ and $P(X\geq2)$, each to $4$ decimal places.",
          ["binomial distribution"], "moyenne", 4,
          [(r"You identify $X\sim B(15,0.2)$ and write $P(X=3)=\binom{15}{3}(0.2)^{3}(0.8)^{12}$", 1), (r"You obtain $P(X=3)=0.2501$", 1),
           (r"You write $P(X\geq2)=1-P(X=0)-P(X=1)$ with $P(X=0)=0.0352$ and $P(X=1)=0.1319$", 1), (r"You obtain $P(X\geq2)=0.8329$", 1)],
          r"A count of successes in $n$ independent trials with the same probability $p$ follows $B(n,p)$, with $P(X=r)=\binom{n}{r}p^{r}(1-p)^{n-r}$; a probability of *at least* a number of successes is easier by the complement.",
          r"The trials are independent with constant probability, so $X\sim B(15,0.2)$. $P(X=3)=\binom{15}{3}(0.2)^{3}(0.8)^{12}=455\times0.008\times0.068719=0.2501$. For the second probability, $P(X=0)=0.8^{15}=0.0352$ and $P(X=1)=15\times0.2\times0.8^{14}=0.1319$, so $P(X\geq2)=1-0.0352-0.1319=0.8329$.",
          ans=r"$P(X=3)=0.2501$ ; $P(X\geq2)=0.8329$"),
        S("c", r"For the batch in part (b), write down $E(X)$ and $\mathrm{Var}(X)$.",
          ["binomial distribution"], "faible", 2,
          [(r"You use $E(X)=np=15\times0.2=3$", 1), (r"You use $\mathrm{Var}(X)=npq=15\times0.2\times0.8=2.4$", 1)],
          r"For $X\sim B(n,p)$, the mean is $np$ and the variance is $np(1-p)$.",
          r"$E(X)=np=15\times0.2=3$ and $\mathrm{Var}(X)=np(1-p)=15\times0.2\times0.8=2.4$.",
          ans=r"$E(X)=3$ ; $\mathrm{Var}(X)=2.4$"),
        S("d", r"A technician tests phones, one at a time, from a large delivery in which each phone has probability $0.2$ of a faulty battery. Find the least number $n$ of phones that must be tested so that the probability of finding at least one faulty battery exceeds $0.99$.",
          ["binomial distribution"], "elevee", 3,
          [(r"You write $1-0.8^{n}>0.99$, that is $0.8^{n}<0.01$", 1), (r"You take logarithms and divide by $\ln0.8<0$, reversing the inequality: $n>\dfrac{\ln0.01}{\ln0.8}\approx20.64$", 1), (r"You conclude $n=21$", 1)],
          r"A probability of *at least one* success in $n$ trials is $1-q^{n}$; to solve an inequality with the unknown in an exponent, take logarithms and reverse the inequality when dividing by a negative logarithm.",
          r"$P(\text{at least one faulty})=1-0.8^{n}$, so we need $1-0.8^{n}>0.99$, that is $0.8^{n}<0.01$. Taking logarithms, $n\ln0.8<\ln0.01$. Since $\ln0.8<0$, dividing reverses the inequality: $n>\dfrac{\ln0.01}{\ln0.8}=\dfrac{-4.6052}{-0.2231}\approx20.64$. The least integer is $n=21$. Check: $0.8^{20}=0.0115>0.01$ and $0.8^{21}=0.0092<0.01$.",
          ans=r"$n=21$",
          piege=r"Dividing by $\ln0.8$ without reversing the inequality gives $n<20.64$ and the wrong conclusion $n=20$."),
    ]))

    # ---- Exercice 3 : grouped data (12) ----
    ex.append(E("3", G, 12, r"The waiting times, in minutes, of $80$ customers at a bank in Yaoundé one Monday were recorded in the table below." "\n\n"
                            r"| Waiting time $t$ (minutes) | $0\le t<5$ | $5\le t<10$ | $10\le t<15$ | $15\le t<20$ | $20\le t<30$ | $30\le t<40$ |" "\n"
                            r"|---|---|---|---|---|---|---|" "\n"
                            r"| Number of customers | 6 | 15 | 25 | 18 | 12 | 4 |", [
        S("a", r"Calculate an estimate of the mean and of the standard deviation of the waiting times.",
          ["grouped data statistics"], "faible", 3,
          [(r"You use the class mid-points $2.5,\ 7.5,\ 12.5,\ 17.5,\ 25,\ 35$", 1), (r"You find $\sum fx=1195$ and the mean $\bar x=14.94$ minutes", 1), (r"You find $\sum fx^{2}=22700$ and the standard deviation $7.79$ minutes", 1)],
          r"For grouped data, replace each class by its mid-point $x$; then $\bar x=\dfrac{\sum fx}{\sum f}$ and the standard deviation is $\sqrt{\dfrac{\sum fx^{2}}{\sum f}-\bar x^{2}}$.",
          r"The mid-points are $2.5,\ 7.5,\ 12.5,\ 17.5,\ 25,\ 35$. $\sum fx=6(2.5)+15(7.5)+25(12.5)+18(17.5)+12(25)+4(35)=15+112.5+312.5+315+300+140=1195$, so $\bar x=\dfrac{1195}{80}=14.9375\approx14.94$. $\sum fx^{2}=6(6.25)+15(56.25)+25(156.25)+18(306.25)+12(625)+4(1225)=22700$, so the variance is $\dfrac{22700}{80}-14.9375^{2}=283.75-223.1289=60.6211$ and the standard deviation is $\sqrt{60.6211}\approx7.79$.",
          ans=r"mean $\approx14.94$ minutes ; standard deviation $\approx7.79$ minutes"),
        S("b", r"Construct a cumulative frequency table for these data and, using linear interpolation, estimate the median, the lower quartile, the upper quartile and the interquartile range of the waiting times.",
          ["cumulative frequency statistics", "median and quartiles statistics"], "moyenne", 4,
          [(r"You give the cumulative frequencies $6,\ 21,\ 46,\ 64,\ 76,\ 80$ at the upper class boundaries", 1), (r"You interpolate the median (the $40$th value) in the class $10\le t<15$: $13.8$", 1),
           (r"You interpolate the lower quartile (the $20$th value): $9.67$", 1), (r"You interpolate the upper quartile (the $60$th value): $18.89$, and obtain the interquartile range $9.22$", 1)],
          r"A cumulative frequency is the number of values below the upper boundary of a class; a quartile or the median is found in the class that contains the required position ($\tfrac n4$, $\tfrac n2$, $\tfrac{3n}{4}$) by linear interpolation inside that class.",
          r"| Upper boundary | 5 | 10 | 15 | 20 | 30 | 40 |" "\n" r"|---|---|---|---|---|---|---|" "\n" r"| Cumulative frequency | 6 | 21 | 46 | 64 | 76 | 80 |" "" "\n\n"
          r"Median: the $40$th value lies in $10\le t<15$ (cumulative frequency $21$ before the class, $25$ in the class): $10+\dfrac{40-21}{25}\times5=10+3.8=13.8$. Lower quartile: the $20$th value lies in $5\le t<10$: $5+\dfrac{20-6}{15}\times5=5+4.667=9.67$. Upper quartile: the $60$th value lies in $15\le t<20$: $15+\dfrac{60-46}{18}\times5=15+3.889=18.89$. The interquartile range is $18.89-9.67=9.22$.",
          ans=r"median $\approx13.8$ ; $Q_{1}\approx9.67$ ; $Q_{3}\approx18.89$ ; interquartile range $\approx9.22$ minutes"),
        S("c", r"Estimate the number of customers who waited between $12$ and $25$ minutes, and express it as a percentage of all the customers.",
          ["cumulative frequency statistics"], "moyenne", 3,
          [(r"You estimate the cumulative frequency at $12$ minutes: $21+\tfrac{2}{5}\times25=31$", 1), (r"You estimate the cumulative frequency at $25$ minutes: $64+\tfrac{5}{10}\times12=70$", 1), (r"You obtain $70-31=39$ customers, that is $48.75\%$", 1)],
          r"Assuming the values are spread evenly inside each class, the number of values below a given point is found by linear interpolation of the cumulative frequencies, and the number between two points is the difference.",
          r"At $12$ minutes, which lies in $10\le t<15$: $21+\dfrac{12-10}{5}\times25=21+10=31$. At $25$ minutes, which lies in $20\le t<30$: $64+\dfrac{25-20}{10}\times12=64+6=70$. The number of customers between $12$ and $25$ minutes is $70-31=39$, that is $\dfrac{39}{80}\times100=48.75\%$.",
          ans=r"$39$ customers, that is $48.75\%$"),
        S("d", r"The bank installs new equipment and every waiting time becomes $80\%$ of its previous value. Without recalculating from the table, write down the new mean and the new standard deviation.",
          ["grouped data statistics"], "faible", 2,
          [(r"You multiply the mean by $0.8$: $0.8\times14.9375=11.95$", 1), (r"You multiply the standard deviation by $0.8$: $0.8\times7.786\approx6.23$", 1)],
          r"If every value is multiplied by a constant $c>0$, the mean and the standard deviation are both multiplied by $c$ (and the variance by $c^{2}$).",
          r"The new mean is $0.8\times14.9375=11.95$ minutes. The new standard deviation is $0.8\times7.786=6.229\approx6.23$ minutes.",
          ans=r"mean $\approx11.95$ minutes ; standard deviation $\approx6.23$ minutes"),
    ]))

    # ---- Exercice 4 : discrete random variables (13) ----
    ex.append(E("4", G, 13, r"The number $X$ of sacks of cassava flour sold in one hour by a trader at Mokolo market in Yaoundé has the following probability distribution, where $p$ and $q$ are constants." "\n\n"
                            r"| $x$ | 0 | 1 | 2 | 3 | 4 |" "\n" r"|---|---|---|---|---|---|" "\n" r"| $P(X=x)$ | $0.10$ | $p$ | $0.30$ | $q$ | $0.15$ |" "" "\n\n"
                            r"It is known that $E(X)=2$.", [
        S("a", r"Find the values of $p$ and $q$.",
          ["discrete random variables statistics", "expectation and variance"], "moyenne", 4,
          [(r"You use $\sum P(X=x)=1$ to obtain $p+q=0.45$", 1), (r"You write $E(X)=p+3q+1.2=2$, that is $p+3q=0.8$", 1), (r"You solve the two equations to obtain $q=0.175$", 1), (r"You obtain $p=0.275$", 1)],
          r"The probabilities of a discrete random variable add up to $1$, and $E(X)=\sum x\,P(X=x)$; two unknown probabilities need two equations, one from each of these facts.",
          r"The probabilities sum to $1$: $0.10+p+0.30+q+0.15=1$, so $p+q=0.45$. The expectation is $E(X)=0(0.10)+1(p)+2(0.30)+3(q)+4(0.15)=p+3q+1.2$. Since $E(X)=2$, $p+3q=0.8$. Subtracting the first equation: $2q=0.35$, so $q=0.175$ and $p=0.45-0.175=0.275$.",
          ans=r"$p=0.275$ ; $q=0.175$"),
        S("b", r"Find $\mathrm{Var}(X)$ and the standard deviation of $X$ to $2$ decimal places.",
          ["expectation and variance"], "faible", 3,
          [(r"You compute $E(X^{2})=0.275+1.2+1.575+2.4=5.45$", 1), (r"You use $\mathrm{Var}(X)=E(X^{2})-[E(X)]^{2}=5.45-4=1.45$", 1), (r"You obtain the standard deviation $\sqrt{1.45}\approx1.20$", 1)],
          r"The variance is $\mathrm{Var}(X)=E(X^{2})-[E(X)]^{2}$ with $E(X^{2})=\sum x^{2}P(X=x)$, and the standard deviation is its square root.",
          r"$E(X^{2})=0^{2}(0.10)+1^{2}(0.275)+2^{2}(0.30)+3^{2}(0.175)+4^{2}(0.15)=0.275+1.2+1.575+2.4=5.45$. Then $\mathrm{Var}(X)=5.45-2^{2}=1.45$ and the standard deviation is $\sqrt{1.45}\approx1.20$.",
          ans=r"$\mathrm{Var}(X)=1.45$ ; standard deviation $\approx1.20$"),
        S("c", r"The trader earns a profit of $1500$ FCFA on each sack and pays a rent of $2000$ FCFA for the hour. Let $Y$ be the profit, in thousands of FCFA, in one hour, so that $Y=1.5X-2$. Find $E(Y)$ and $\mathrm{Var}(Y)$.",
          ["expectation and variance"], "faible", 3,
          [(r"You use $E(aX+b)=aE(X)+b$ to write $E(Y)=1.5\times2-2$", 1), (r"You obtain $E(Y)=1$", 1), (r"You use $\mathrm{Var}(aX+b)=a^{2}\mathrm{Var}(X)$ to obtain $\mathrm{Var}(Y)=2.25\times1.45=3.2625$", 1)],
          r"For constants $a$ and $b$, $E(aX+b)=aE(X)+b$ and $\mathrm{Var}(aX+b)=a^{2}\mathrm{Var}(X)$: the added constant shifts the mean but does not change the spread.",
          r"$E(Y)=1.5E(X)-2=1.5\times2-2=1$, so the expected profit is $1000$ FCFA per hour. $\mathrm{Var}(Y)=1.5^{2}\mathrm{Var}(X)=2.25\times1.45=3.2625$.",
          ans=r"$E(Y)=1$ ; $\mathrm{Var}(Y)=3.2625$"),
        S("d", r"Find the probability that the trader makes a profit in a given hour, that is $P(Y>0)$. Find also $P(X\geq2\mid X\geq1)$.",
          ["discrete random variables statistics"], "moyenne", 3,
          [(r"You show that $Y>0$ is equivalent to $X\geq2$ (since $1.5X>2$)", 1), (r"You obtain $P(Y>0)=0.30+0.175+0.15=0.625$", 1), (r"You find $P(X\geq2\mid X\geq1)=\dfrac{0.625}{0.90}=\dfrac{25}{36}\approx0.6944$", 1)],
          r"Translate a condition on a transformed variable into a condition on the original variable before adding probabilities; a conditional probability is the probability of the intersection divided by the probability of the condition.",
          r"$Y>0$ means $1.5X>2$, that is $X>1.33$, so $X\geq2$. Then $P(Y>0)=P(X=2)+P(X=3)+P(X=4)=0.30+0.175+0.15=0.625$. For the conditional probability, $P(X\geq1)=1-P(X=0)=0.90$ and the event $X\geq2$ is contained in $X\geq1$, so $P(X\geq2\mid X\geq1)=\dfrac{0.625}{0.90}=\dfrac{25}{36}\approx0.6944$.",
          ans=r"$P(Y>0)=0.625$ ; $P(X\geq2\mid X\geq1)=\dfrac{25}{36}\approx0.6944$"),
    ]))

    # ---- Exercice 5 : continuous random variables (13) ----
    ex.append(E("5", G, 13, r"The time $X$, in hours, that a bush taxi spends at a motor park before it leaves is a continuous random variable with probability density function" "\n\n"
                            r"$$f(x)=\begin{cases}kx^{2}(4-x), & 0\le x\le4,\\ 0, & \text{otherwise,}\end{cases}$$" "" "\n\n" r"where $k$ is a constant.", [
        S("a", r"Show that $k=\dfrac{3}{64}$.",
          ["probability density functions"], "faible", 3,
          [(r"You use $\displaystyle\int_{0}^{4}f(x)\,dx=1$", 1), (r"You integrate: $k\left[\dfrac{4x^{3}}{3}-\dfrac{x^{4}}{4}\right]_{0}^{4}=k\left(\dfrac{256}{3}-64\right)=\dfrac{64k}{3}$", 1), (r"You conclude $k=\dfrac{3}{64}$", 1)],
          r"The total area under a probability density function is $1$, so the constant is found from $\int f(x)\,dx=1$ over the interval where $f$ is not zero.",
          r"$\displaystyle\int_{0}^{4}kx^{2}(4-x)\,dx=k\int_{0}^{4}\left(4x^{2}-x^{3}\right)dx=k\left[\dfrac{4x^{3}}{3}-\dfrac{x^{4}}{4}\right]_{0}^{4}=k\left(\dfrac{256}{3}-64\right)=\dfrac{64k}{3}$. Setting this equal to $1$ gives $k=\dfrac{3}{64}$.",
          ans=r"$k=\dfrac{3}{64}$"),
        S("b", r"Find $E(X)$ and $\mathrm{Var}(X)$.",
          ["continuous random variables", "probability density functions"], "moyenne", 4,
          [(r"You write $E(X)=\displaystyle\int_{0}^{4}x\,f(x)\,dx$ and integrate $\dfrac{3}{64}\left[x^{4}-\dfrac{x^{5}}{5}\right]_{0}^{4}$", 1), (r"You obtain $E(X)=2.4$", 1),
           (r"You compute $E(X^{2})=\dfrac{3}{64}\left[\dfrac{4x^{5}}{5}-\dfrac{x^{6}}{6}\right]_{0}^{4}=6.4$", 1), (r"You obtain $\mathrm{Var}(X)=6.4-2.4^{2}=0.64$", 1)],
          r"For a continuous random variable, $E(X)=\int x\,f(x)\,dx$ and $E(X^{2})=\int x^{2}f(x)\,dx$ over the interval where $f$ is not zero, and $\mathrm{Var}(X)=E(X^{2})-[E(X)]^{2}$.",
          r"$E(X)=\dfrac{3}{64}\displaystyle\int_{0}^{4}\left(4x^{3}-x^{4}\right)dx=\dfrac{3}{64}\left[x^{4}-\dfrac{x^{5}}{5}\right]_{0}^{4}=\dfrac{3}{64}(256-204.8)=\dfrac{3}{64}\times51.2=2.4$. $E(X^{2})=\dfrac{3}{64}\displaystyle\int_{0}^{4}\left(4x^{4}-x^{5}\right)dx=\dfrac{3}{64}\left[\dfrac{4x^{5}}{5}-\dfrac{x^{6}}{6}\right]_{0}^{4}=\dfrac{3}{64}\left(819.2-682.67\right)=\dfrac{3}{64}\times136.53=6.4$. Therefore $\mathrm{Var}(X)=6.4-2.4^{2}=6.4-5.76=0.64$.",
          ans=r"$E(X)=2.4$ ; $\mathrm{Var}(X)=0.64$"),
        S("c", r"Find the probability that the taxi spends more than $3$ hours at the motor park.",
          ["continuous random variables"], "faible", 3,
          [(r"You write $P(X>3)=\displaystyle\int_{3}^{4}f(x)\,dx$", 1), (r"You evaluate $\dfrac{3}{64}\left[\dfrac{4x^{3}}{3}-\dfrac{x^{4}}{4}\right]_{3}^{4}=\dfrac{3}{64}\left(\dfrac{64}{3}-\dfrac{63}{4}\right)$", 1), (r"You obtain $\dfrac{67}{256}\approx0.2617$", 1)],
          r"The probability that a continuous random variable lies in an interval is the area under the density over that interval: $P(a<X<b)=\int_{a}^{b}f(x)\,dx$.",
          r"$P(X>3)=\dfrac{3}{64}\displaystyle\int_{3}^{4}\left(4x^{2}-x^{3}\right)dx=\dfrac{3}{64}\left[\dfrac{4x^{3}}{3}-\dfrac{x^{4}}{4}\right]_{3}^{4}$. At $x=4$ the bracket is $\dfrac{256}{3}-64=\dfrac{64}{3}$ and at $x=3$ it is $36-\dfrac{81}{4}=\dfrac{63}{4}$. So $P(X>3)=\dfrac{3}{64}\left(\dfrac{64}{3}-\dfrac{63}{4}\right)=\dfrac{3}{64}\times\dfrac{67}{12}=\dfrac{67}{256}\approx0.2617$.",
          ans=r"$\dfrac{67}{256}\approx0.2617$"),
        S("d", r"Show that the median $m$ of $X$ satisfies $3m^{4}-16m^{3}+128=0$, and show that $2.4<m<2.5$.",
          ["probability density functions", "continuous random variables"], "elevee", 3,
          [(r"You write $\displaystyle\int_{0}^{m}f(x)\,dx=\dfrac12$ and integrate to obtain $\dfrac{3}{64}\left(\dfrac{4m^{3}}{3}-\dfrac{m^{4}}{4}\right)=\dfrac12$", 1), (r"You simplify to $3m^{4}-16m^{3}+128=0$", 1),
           (r"You show a change of sign: $g(2.4)=6.3488>0$ and $g(2.5)=-4.8125<0$", 1)],
          r"The median $m$ of a continuous distribution is the value with half of the total area to its left, $\int_{-\infty}^{m}f(x)\,dx=\tfrac12$; when the resulting equation cannot be solved exactly, a change of sign of the function locates a root.",
          r"$\displaystyle\int_{0}^{m}f(x)\,dx=\dfrac{3}{64}\left[\dfrac{4x^{3}}{3}-\dfrac{x^{4}}{4}\right]_{0}^{m}=\dfrac{m^{3}}{16}-\dfrac{3m^{4}}{256}=\dfrac12$. Multiplying by $256$: $16m^{3}-3m^{4}=128$, that is $3m^{4}-16m^{3}+128=0$. Let $g(m)=3m^{4}-16m^{3}+128$. Then $g(2.4)=3(33.1776)-16(13.824)+128=99.5328-221.184+128=6.3488>0$ and $g(2.5)=3(39.0625)-16(15.625)+128=117.1875-250+128=-4.8125<0$. The function is continuous and changes sign, so the root lies between $2.4$ and $2.5$ (it is $m\approx2.457$).",
          ans=r"$3m^{4}-16m^{3}+128=0$ ; $g(2.4)=6.3488>0$ and $g(2.5)=-4.8125<0$, so $2.4<m<2.5$"),
    ]))

    # ---- Exercice 6 : normal distribution (12) ----
    ex.append(E("6", G, 12, r"Statistical tables of the standard normal distribution function $\Phi$ are to be used where necessary.", [
        S("a", r"The time $T$ minutes taken by a motorbike taxi to cover a certain route in Bamenda is normally distributed with mean $25$ and standard deviation $4$. Find the probability that a journey takes (i) more than $31$ minutes, (ii) between $21$ and $30$ minutes.",
          ["normal distribution"], "faible", 4,
          [(r"You standardise $z=\dfrac{31-25}{4}=1.5$", 1), (r"You obtain $P(T>31)=1-\Phi(1.5)=1-0.9332=0.0668$", 1),
           (r"You standardise the limits: $z=-1$ and $z=1.25$", 1), (r"You obtain $\Phi(1.25)-\Phi(-1)=0.8944-0.1587=0.7357$", 1)],
          r"For $T\sim N(\mu,\sigma^{2})$, standardise with $Z=\dfrac{T-\mu}{\sigma}$, read $\Phi$ in the tables, use $\Phi(-z)=1-\Phi(z)$ for a negative value, and subtract two values of $\Phi$ for a probability between two limits.",
          r"(i) $z=\dfrac{31-25}{4}=1.5$, so $P(T>31)=1-\Phi(1.5)=1-0.9332=0.0668$. (ii) The limits are $z_{1}=\dfrac{21-25}{4}=-1$ and $z_{2}=\dfrac{30-25}{4}=1.25$. Then $P(21<T<30)=\Phi(1.25)-\Phi(-1)=\Phi(1.25)-\left(1-\Phi(1)\right)=0.8944-(1-0.8413)=0.8944-0.1587=0.7357$.",
          ans=r"(i) $0.0668$ ; (ii) $0.7357$"),
        S("b", r"The slowest $10\%$ of journeys take longer than $t$ minutes. Find $t$, to $2$ decimal places.",
          ["normal distribution"], "moyenne", 3,
          [(r"You write $P(T>t)=0.10$, so $\Phi(z)=0.90$", 1), (r"You read $z=1.2816$ in the table of percentage points", 1), (r"You obtain $t=25+4\times1.2816=30.13$", 1)],
          r"To find a limit from a given probability, read the value $z$ that gives the required value of $\Phi$ in the table of percentage points, then reverse the standardisation with $t=\mu+z\sigma$.",
          r"$P(T>t)=0.10$ means $P(T\leq t)=0.90$, so $\Phi(z)=0.90$ with $z=\dfrac{t-25}{4}$. The table of percentage points gives $z=1.2816$ (since $\Phi(1.2816)=0.9000$). Then $t=25+4\times1.2816=30.1264\approx30.13$ minutes.",
          ans=r"$t\approx30.13$ minutes"),
        S("c", r"In a survey, $40\%$ of the journeys are paid by mobile money. In a random sample of $150$ journeys, $X$ are paid by mobile money. Find $E(X)$ and $\mathrm{Var}(X)$, and explain why $X$ can be approximated by a normal distribution; state the parameters of this normal distribution.",
          ["normal approximation to the binomial distribution", "normal distribution"], "faible", 2,
          [(r"You find $E(X)=150\times0.4=60$ and $\mathrm{Var}(X)=150\times0.4\times0.6=36$", 1), (r"You justify the approximation ($np=60$ and $nq=90$ are both large) and state $N(60,36)$", 1)],
          r"If $X\sim B(n,p)$ with $n$ large and $p$ not close to $0$ or $1$ (so that $np$ and $nq$ are both greater than about $5$ or $10$), then $X$ is approximately $N(np,\,npq)$.",
          r"$X\sim B(150,0.4)$, so $E(X)=np=150\times0.4=60$ and $\mathrm{Var}(X)=npq=150\times0.4\times0.6=36$. Since $n$ is large and $np=60$ and $nq=90$ are both much greater than $5$, $X$ is approximately normal: $X\approx N(60,36)$, with standard deviation $6$.",
          ans=r"$E(X)=60$ ; $\mathrm{Var}(X)=36$ ; $X\approx N(60,36)$"),
        S("d", r"Use the normal approximation to find the probability that at least $70$ of the $150$ journeys are paid by mobile money, to $4$ decimal places.",
          ["normal approximation to the binomial distribution", "normal distribution"], "moyenne", 3,
          [(r"You apply a continuity correction: $P(X\geq70)\to P(Y>69.5)$", 1), (r"You standardise: $z=\dfrac{69.5-60}{6}=1.58$ (to $2$ decimal places)", 1), (r"You obtain $1-\Phi(1.58)=1-0.9429=0.0571$", 1)],
          r"A discrete count is replaced by a continuous variable, so each integer value $r$ is spread over $r-0.5$ to $r+0.5$: *at least $r$* becomes *greater than $r-0.5$* before standardising.",
          r"Let $Y\sim N(60,36)$. Since $X$ takes integer values, $P(X\geq70)\approx P(Y>69.5)$. Then $z=\dfrac{69.5-60}{6}=1.5833\approx1.58$, and $P(Y>69.5)=1-\Phi(1.58)=1-0.9429=0.0571$.",
          ans=r"$0.0571$",
          piege=r"Using $70$ instead of $69.5$ (no continuity correction) understates the probability, because half of the width of the bar at $70$ is lost."),
    ]))

    # ---- Exercice 7 : Poisson and binomial models (13) ----
    ex.append(E("7", G, 13, r"", [
        S("a", r"The number of customers arriving at a mobile money kiosk in Garoua in any $10$-minute period has a Poisson distribution with mean $2.5$. Find the probability that in a given $10$-minute period (i) exactly $4$ customers arrive, (ii) at most $2$ customers arrive. Give each answer to $4$ decimal places.",
          ["poisson distribution statistics"], "faible", 4,
          [(r"You state $X\sim\mathrm{Po}(2.5)$ and write $P(X=4)=\dfrac{e^{-2.5}2.5^{4}}{4!}$", 1), (r"You obtain $P(X=4)=0.1336$", 1),
           (r"You write $P(X\le2)=e^{-2.5}\left(1+2.5+\dfrac{2.5^{2}}{2}\right)$", 1), (r"You obtain $P(X\le2)=0.5438$", 1)],
          r"If $X\sim\mathrm{Po}(\lambda)$ then $P(X=r)=\dfrac{e^{-\lambda}\lambda^{r}}{r!}$; *at most* a value is a sum of the probabilities of the values from $0$ up to it.",
          r"(i) $P(X=4)=\dfrac{e^{-2.5}\times2.5^{4}}{4!}=\dfrac{0.082085\times39.0625}{24}=0.1336$. (ii) $P(X\le2)=P(0)+P(1)+P(2)=e^{-2.5}\left(1+2.5+\dfrac{6.25}{2}\right)=0.082085\times6.625=0.5438$.",
          ans=r"(i) $0.1336$ ; (ii) $0.5438$"),
        S("b", r"Find the probability that, in a $20$-minute period, no customer arrives, and the probability that at least $2$ customers arrive. Give each answer to $4$ decimal places.",
          ["poisson distribution statistics"], "faible", 3,
          [(r"You scale the mean to the new period: $\lambda=5$", 1), (r"You obtain $P(\text{none})=e^{-5}=0.0067$", 1), (r"You obtain $P(\text{at least }2)=1-e^{-5}(1+5)=0.9596$", 1)],
          r"The mean of a Poisson variable is proportional to the length of the interval, so when the period is changed the mean is rescaled before any probability is calculated.",
          r"For $20$ minutes the mean is $2\times2.5=5$. $P(\text{none})=e^{-5}=0.0067$. $P(\text{at least }2)=1-P(0)-P(1)=1-e^{-5}-5e^{-5}=1-6\times0.006738=1-0.0404=0.9596$.",
          ans=r"$P(\text{none})=0.0067$ ; $P(\text{at least }2)=0.9596$"),
        S("c", r"Each mobile money transfer made through the kiosk fails, independently, with probability $0.015$. In a day, $200$ transfers are made, and $Y$ is the number of failures. Explain why a Poisson distribution can be used as an approximation for $Y$, state its mean, and use it to estimate $P(Y=2)$ to $4$ decimal places.",
          ["poisson distribution statistics", "binomial distribution"], "moyenne", 3,
          [(r"You state that $Y\sim B(200,0.015)$, with $n$ large and $p$ small", 1), (r"You approximate by $\mathrm{Po}(np)=\mathrm{Po}(3)$", 1), (r"You obtain $P(Y=2)\approx\dfrac{e^{-3}3^{2}}{2!}=0.2240$", 1)],
          r"When $n$ is large and $p$ is small, $B(n,p)$ is well approximated by a Poisson distribution with mean $\lambda=np$.",
          r"$Y\sim B(200,0.015)$ has a large $n$ and a small $p$, so it is approximated by a Poisson distribution with mean $\lambda=np=200\times0.015=3$. Then $P(Y=2)\approx\dfrac{e^{-3}\times3^{2}}{2!}=0.049787\times4.5=0.2240$.",
          ans=r"$Y\approx\mathrm{Po}(3)$ ; $P(Y=2)\approx0.2240$"),
        S("d", r"Calculate the exact value of $P(Y=2)$ from the binomial distribution, to $4$ decimal places, and find the difference between this exact value and the Poisson estimate of part (c).",
          ["binomial distribution"], "moyenne", 3,
          [(r"You write $P(Y=2)=\binom{200}{2}(0.015)^{2}(0.985)^{198}$", 1), (r"You obtain $0.2246$", 1), (r"You find the difference $0.2246-0.2240=0.0006$", 1)],
          r"The exact binomial probability is $\binom{n}{r}p^{r}(1-p)^{n-r}$; comparing it with an approximation shows how accurate the approximation is.",
          r"$P(Y=2)=\binom{200}{2}(0.015)^{2}(0.985)^{198}=19900\times0.000225\times0.050162=0.2246$. The difference from the Poisson estimate is $0.2246-0.2240=0.0006$, so the approximation is accurate to three decimal places.",
          ans=r"exact $P(Y=2)=0.2246$ ; difference $0.0006$"),
    ]))

    # ---- Exercice 8 : correlation and regression (13) ----
    ex.append(E("8", G, 13, r"A shop in Bafoussam records, for eight weeks, the amount $x$ (in thousands of FCFA) spent on advertising and the number $y$ of phone chargers sold." "\n\n"
                            r"| Week | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |" "\n" r"|---|---|---|---|---|---|---|---|---|" "\n"
                            r"| Advertising, $x$ | 12 | 15 | 19 | 22 | 26 | 30 | 33 | 38 |" "\n" r"| Chargers sold, $y$ | 34 | 36 | 44 | 41 | 55 | 52 | 63 | 60 |", [
        S("a", r"Calculate the product-moment correlation coefficient between $x$ and $y$, to $4$ decimal places.",
          ["correlation and regression statistics"], "moyenne", 4,
          [(r"You find $\sum x=195$, $\sum y=385$, $\sum x^{2}=5323$, $\sum y^{2}=19367$, $\sum xy=10035$", 1), (r"You find $S_{xx}=569.875$ and $S_{yy}=838.875$", 1), (r"You find $S_{xy}=650.625$", 1), (r"You obtain $r=\dfrac{S_{xy}}{\sqrt{S_{xx}S_{yy}}}=0.9410$", 1)],
          r"The product-moment correlation coefficient is $r=\dfrac{S_{xy}}{\sqrt{S_{xx}S_{yy}}}$ with $S_{xx}=\sum x^{2}-\dfrac{(\sum x)^{2}}{n}$, $S_{yy}=\sum y^{2}-\dfrac{(\sum y)^{2}}{n}$ and $S_{xy}=\sum xy-\dfrac{\sum x\sum y}{n}$.",
          r"With $n=8$: $\sum x=195$, $\sum y=385$, $\sum x^{2}=5323$, $\sum y^{2}=19367$, $\sum xy=10035$. Then $S_{xx}=5323-\dfrac{195^{2}}{8}=569.875$, $S_{yy}=19367-\dfrac{385^{2}}{8}=838.875$ and $S_{xy}=10035-\dfrac{195\times385}{8}=650.625$. Hence $r=\dfrac{650.625}{\sqrt{569.875\times838.875}}=\dfrac{650.625}{691.41}=0.9410$.",
          ans=r"$r=0.9410$"),
        S("b", r"Find the equation of the least squares regression line of $y$ on $x$, giving the coefficients to $3$ decimal places or $4$ significant figures where appropriate.",
          ["correlation and regression statistics"], "moyenne", 4,
          [(r"You find the gradient $b=\dfrac{S_{xy}}{S_{xx}}=1.1417$", 1), (r"You find the means $\bar x=24.375$ and $\bar y=48.125$", 1), (r"You find the intercept $a=\bar y-b\bar x=20.30$", 1), (r"You write $y=20.30+1.142x$", 1)],
          r"The least squares regression line of $y$ on $x$ is $y=a+bx$ with $b=\dfrac{S_{xy}}{S_{xx}}$ and $a=\bar y-b\bar x$, so it passes through the point of means $(\bar x,\bar y)$.",
          r"$b=\dfrac{S_{xy}}{S_{xx}}=\dfrac{650.625}{569.875}=1.1417$. The means are $\bar x=\dfrac{195}{8}=24.375$ and $\bar y=\dfrac{385}{8}=48.125$, so $a=48.125-1.1417\times24.375=48.125-27.829=20.296\approx20.30$. The line is $y=20.30+1.142x$.",
          ans=r"$y=20.30+1.142x$"),
        S("c", r"Use your line to estimate the number of chargers sold in a week with an advertising spend of $28$ thousand FCFA. Explain why the line should not be used to estimate sales for an advertising spend of $60$ thousand FCFA.",
          ["correlation and regression statistics"], "faible", 3,
          [(r"You substitute $x=28$: $y=20.30+1.142\times28$", 1), (r"You obtain about $52$ chargers", 1), (r"You explain that $x=60$ lies far outside the range of the data ($12$ to $38$), so this is unreliable extrapolation", 1)],
          r"A regression line may be used to estimate $y$ for a value of $x$ inside the range of the observed data (interpolation); outside that range the same linear relationship may not hold, so the estimate is unreliable.",
          r"At $x=28$: $y=20.30+1.142\times28=20.30+31.98=52.3$, so about $52$ chargers. The advertising values in the data run from $12$ to $38$; $60$ is well outside that range, so using the line there is extrapolation and nothing in the data shows that the linear relationship continues to hold.",
          ans=r"about $52$ chargers ; $x=60$ is outside the range $12$ to $38$ of the data"),
        S("d", r"Interpret the gradient of the regression line in the context of the question.",
          ["correlation and regression statistics"], "faible", 2,
          [(r"You state that the gradient is $1.142$", 1), (r"You interpret it: each extra thousand FCFA spent on advertising is associated with about $1.1$ more chargers sold per week", 1)],
          r"The gradient of a regression line of $y$ on $x$ is the average change in $y$ associated with an increase of one unit in $x$, expressed with the units of the context.",
          r"The gradient is $1.142$: on average, each additional thousand FCFA spent on advertising in a week goes with about $1.1$ additional chargers sold in that week.",
          ans=r"about $1.1$ more chargers per extra thousand FCFA of advertising"),
    ]))

    return ex
