r"""Section C (Statistics and Probability, questions 9 et 10, 34 points) de l'epreuve inedite GCE O Level Additional Mathematics Paper 2 n.2.

Le vrai sujet donne trois questions de Mecanique (B) et trois de Statistiques et Probabilites (C) : tout A puis DEUX questions de B OU de C. Cette inedite
garde deux questions de la Section C (version « answer ALL »). Chaines BRUTES.
"""
from questions_addmaths_p2_a import E, S

TABLE_TEMPS = r"""| Time $t$ (minutes) | $0\leq t<10$ | $10\leq t<20$ | $20\leq t<30$ | $30\leq t<40$ | $40\leq t<50$ |
|---|---|---|---|---|---|
| Frequency | 6 | 14 | 28 | 20 | 12 |"""

TABLE_CUMUL = r"""| $t$ less than | 10 | 20 | 30 | 40 | 50 |
|---|---|---|---|---|---|
| Cumulative frequency | 6 | | | | 80 |"""

TABLE_CUMUL_COMPLETE = r"""| $t$ less than | 10 | 20 | 30 | 40 | 50 |
|---|---|---|---|---|---|
| Cumulative frequency | 6 | 20 | 48 | 68 | 80 |"""


def section_c():
    G = "SECTION C"
    ex = []

    ex.append(E("9", G, 17, "The table shows the time, $t$ minutes, that each of $80$ players spent on the pitch in a school football tournament.\n\n" + TABLE_TEMPS, [
        S("a", r"Calculate an estimate of the mean time spent on the pitch.", ["mean and standard deviation of grouped data"], "faible", 3,
          [(r"You use the mid-class values $5$, $15$, $25$, $35$ and $45$", 1), (r"You calculate $\sum fx=30+210+700+700+540=2180$", 1), (r"You obtain the mean $\dfrac{2180}{80}=27.25$ minutes", 1)],
          r"For a grouped frequency table, use the mid-class value $x$ of each class: $\bar{x}=\dfrac{\sum fx}{\sum f}$.",
          r"Mid-class values: $5,15,25,35,45$. $\sum fx=5(6)+15(14)+25(28)+35(20)+45(12)=30+210+700+700+540=2180$. $\sum f=80$. Mean $=\dfrac{2180}{80}=27.25$ minutes.",
          ans=r"$27.25$ minutes"),
        S("b", r"Calculate an estimate of the standard deviation of the times.", ["mean and standard deviation of grouped data"], "moyenne", 4,
          [(r"You calculate $\sum fx^{2}=150+3150+17500+24500+24300=69600$", 1), (r"You use the formula $\sigma^{2}=\dfrac{\sum fx^{2}}{\sum f}-\bar{x}^{2}$", 1),
           (r"You obtain the variance $870-27.25^{2}=127.4375$", 1), (r"You obtain the standard deviation $\sigma\approx11.3$ minutes", 1)],
          r"The variance of a frequency distribution is $\sigma^{2}=\dfrac{\sum fx^{2}}{\sum f}-\bar{x}^{2}$ and the standard deviation is its square root.",
          r"$\sum fx^{2}=6(25)+14(225)+28(625)+20(1225)+12(2025)=150+3150+17500+24500+24300=69600$. Variance $=\dfrac{69600}{80}-27.25^{2}=870-742.5625=127.4375$. Standard deviation $=\sqrt{127.4375}\approx11.3$ minutes.",
          ans=r"$11.3$ minutes",
          piege=r"The square of the mean is subtracted from the mean of the squares, $\dfrac{\sum fx^{2}}{\sum f}$, before the square root is taken."),
        S("c", r"Copy and complete the cumulative frequency table.\n\n".replace(r"\n", "\n") + TABLE_CUMUL, ["cumulative frequency graphs and quartiles"], "faible", 1,
          [(r"You complete the table: $20$, $48$, $68$", 1)],
          r"The cumulative frequency at the upper boundary of a class is the total of the frequencies of that class and of all the classes before it.",
          "$6+14=20$, $20+28=48$, $48+20=68$ and $68+12=80$.\n\n" + TABLE_CUMUL_COMPLETE,
          ans=r"$20$, $48$, $68$"),
        S("d", r"Draw the cumulative frequency curve for these times, using a scale of $2$ cm to $10$ minutes on the horizontal axis and $2$ cm to $10$ players on the vertical axis.", ["cumulative frequency graphs and quartiles"], "moyenne", 3,
          [(r"You plot the points at the upper class boundaries: $(10,6)$, $(20,20)$, $(30,48)$, $(40,68)$ and $(50,80)$", 1), (r"You include the starting point $(0,0)$", 1), (r"You join the points with a smooth curve", 1)],
          r"A cumulative frequency graph is plotted against the upper class boundaries, with $(0,0)$ as the starting point when no player is below the lowest boundary.",
          r"Plot $(0,0)$, $(10,6)$, $(20,20)$, $(30,48)$, $(40,68)$ and $(50,80)$ and join them with a smooth curve, increasing from $0$ to $80$. The curve is steepest between $t=20$ and $t=30$, where the class frequency is the greatest.",
          ans=None, fig="cf"),
        S("e", r"Use your graph to estimate the median time.", ["cumulative frequency graphs and quartiles"], "faible", 1,
          [(r"You read the median at the $40^{\text{th}}$ player: about $27$ minutes (accept $26.5$ to $27.5$)", 1)],
          r"The median is the value of the middle player: on the graph, read across from half of the total frequency, $\dfrac{80}{2}=40$.",
          r"Read across from $40$ on the vertical axis to the curve, then down to the $t$-axis: about $27$ minutes. (Interpolating in the class $20\leq t<30$: $20+\dfrac{40-20}{28}\times10\approx27.1$.)",
          ans=r"about $27$ minutes"),
        S("f", r"Use your graph to estimate the lower quartile, the upper quartile and the interquartile range.", ["cumulative frequency graphs and quartiles"], "faible", 2,
          [(r"You read $Q_{1}$ at the $20^{\text{th}}$ player, $20$ minutes, and $Q_{3}$ at the $60^{\text{th}}$ player, about $36$ minutes", 1), (r"You calculate the interquartile range $36-20=16$ minutes", 1)],
          r"The quartiles are read at $\dfrac{1}{4}$ and $\dfrac{3}{4}$ of the total frequency; the interquartile range is $Q_{3}-Q_{1}$.",
          r"$\dfrac{80}{4}=20$ and $\dfrac{3\times80}{4}=60$. From the graph, $Q_{1}=20$ minutes and $Q_{3}\approx36$ minutes. The interquartile range is $36-20=16$ minutes.",
          ans=r"$Q_{1}=20$, $Q_{3}\approx36$, interquartile range $16$ minutes"),
        S("g", r"Use your graph to estimate the number of players who spent more than $35$ minutes on the pitch.", ["cumulative frequency graphs and quartiles"], "faible", 2,
          [(r"You read the cumulative frequency at $t=35$: about $58$", 1), (r"You subtract from the total: $80-58=22$ players", 1)],
          r"The number of players with a value above $t$ is the total frequency minus the cumulative frequency at $t$.",
          r"Read up from $t=35$ to the curve, then across to the vertical axis: about $58$ players spent less than $35$ minutes. So $80-58=22$ players spent more than $35$ minutes.",
          ans=r"$22$ players",
          piege=r"The graph gives the number of players who spent LESS than $35$ minutes: it must be subtracted from $80$."),
        S("h", r"Another group of players has a mean time of $25$ minutes and a standard deviation of $6.2$ minutes. State, with a reason, which of the two groups has the more consistent playing times.", ["mean and standard deviation of grouped data"], "faible", 1,
          [(r"You state that the other group is more consistent, because its standard deviation $6.2$ is smaller than $11.3$", 1)],
          r"The standard deviation measures the spread of the values around the mean: the smaller it is, the more consistent the values.",
          r"The standard deviation of the other group, $6.2$, is smaller than that of the $80$ players, $11.3$. Its playing times are less spread out, so the other group is the more consistent.",
          ans=r"the other group (smaller standard deviation)"),
    ]))

    ex.append(E("10", G, 17, "", [
        S("i-a", r"(i)(a) A discrete random variable $X$ takes the values $0$, $1$, $2$ and $3$ only, and $P(X=x)=k(4-x)$, where $k$ is a constant. Find the value of $k$.",
          ["probability mass function and expectation"], "faible", 2,
          [(r"You use $\sum P(X=x)=1$: $4k+3k+2k+k=1$", 1), (r"You obtain $10k=1$, so $k=0.1$", 1)],
          r"The probabilities of all the possible values of a discrete random variable add up to $1$.",
          r"$P(X=0)=4k$, $P(X=1)=3k$, $P(X=2)=2k$ and $P(X=3)=k$. Their sum is $10k=1$, so $k=0.1$.",
          ans=r"$k=0.1$"),
        S("i-b", r"(i)(b) Find $P(X\geq2)$.", ["probability mass function and expectation"], "faible", 1,
          [(r"You add $P(X=2)+P(X=3)=0.2+0.1=0.3$", 1)],
          r"$P(X\geq2)$ is the sum of the probabilities of the values $2$ and $3$.",
          r"With $k=0.1$: $P(X=2)=0.2$ and $P(X=3)=0.1$, so $P(X\geq2)=0.3$.",
          ans=r"$0.3$"),
        S("i-c", r"(i)(c) Calculate $E(X)$.", ["probability mass function and expectation"], "moyenne", 3,
          [(r"You write the distribution: $0.4$, $0.3$, $0.2$, $0.1$ for $x=0,1,2,3$", 1), (r"You use $E(X)=\sum xP(X=x)$", 1), (r"You obtain $E(X)=0+0.3+0.4+0.3=1$", 1)],
          r"The expectation of a discrete random variable is $E(X)=\sum xP(X=x)$.",
          r"| $x$ | 0 | 1 | 2 | 3 |\n|---|---|---|---|---|\n| $P(X=x)$ | 0.4 | 0.3 | 0.2 | 0.1 |\n\n".replace(r"\n", "\n") + r"$E(X)=0(0.4)+1(0.3)+2(0.2)+3(0.1)=0.3+0.4+0.3=1$.",
          ans=r"$E(X)=1$"),
        S("i-d", r"(i)(d) Calculate $\text{Var}(X)$.", ["probability mass function and expectation"], "moyenne", 3,
          [(r"You calculate $E(X^{2})=\sum x^{2}P(X=x)=0.3+0.8+0.9=2$", 1), (r"You use $\text{Var}(X)=E(X^{2})-[E(X)]^{2}$", 1), (r"You obtain $\text{Var}(X)=2-1^{2}=1$", 1)],
          r"The variance is $\text{Var}(X)=E(X^{2})-[E(X)]^{2}$, where $E(X^{2})=\sum x^{2}P(X=x)$.",
          r"$E(X^{2})=0^{2}(0.4)+1^{2}(0.3)+2^{2}(0.2)+3^{2}(0.1)=0.3+0.8+0.9=2$. $\text{Var}(X)=2-1^{2}=1$.",
          ans=r"$\text{Var}(X)=1$",
          piege=r"The square of the expectation, $[E(X)]^{2}$, is subtracted: $E(X^{2})$ and $[E(X)]^{2}$ are different quantities."),
        S("ii-a", r"(ii)(a) A machine produces light bulbs and $70\%$ of the bulbs pass a quality test, independently of one another. A sample of $8$ bulbs is taken and $X$ is the number of bulbs in the sample that pass the test. Find the probability that exactly $6$ bulbs pass the test.",
          ["binomial distribution (additional maths)", "binomial probability of successes"], "moyenne", 3,
          [(r"You state that $X\sim B(8,0.7)$", 1), (r"You calculate $\dbinom{8}{6}(0.7)^{6}(0.3)^{2}$", 1), (r"You obtain $0.2965$", 1)],
          r"If $X\sim B(n,p)$ then $P(X=r)=\dbinom{n}{r}p^{r}(1-p)^{n-r}$.",
          r"$X\sim B(8,0.7)$. $P(X=6)=\dbinom{8}{6}(0.7)^{6}(0.3)^{2}=28\times0.117649\times0.09=0.2965$.",
          ans=r"$0.2965$"),
        S("ii-b", r"(ii)(b) For the same sample, find the probability that at least $7$ bulbs pass the test.", ["binomial distribution (additional maths)", "binomial probability of successes"], "moyenne", 3,
          [(r"You write $P(X\geq7)=P(X=7)+P(X=8)$", 1), (r"You calculate $\dbinom{8}{7}(0.7)^{7}(0.3)+(0.7)^{8}=0.1977+0.0576$", 1), (r"You obtain $0.2553$", 1)],
          r"“At least $7$” means $7$ or $8$: add the two probabilities.".replace(r"“", "“").replace(r"”", "”"),
          r"$P(X=7)=\dbinom{8}{7}(0.7)^{7}(0.3)=8\times0.0823543\times0.3=0.1977$ and $P(X=8)=(0.7)^{8}=0.0576$. So $P(X\geq7)=0.1977+0.0576=0.2553$.",
          ans=r"$0.2553$"),
        S("ii-c", r"(ii)(c) Find the mean and the variance of $X$.", ["binomial distribution (additional maths)"], "faible", 2,
          [(r"You use the mean $np=8\times0.7=5.6$", 1), (r"You use the variance $np(1-p)=8\times0.7\times0.3=1.68$", 1)],
          r"For $X\sim B(n,p)$ the mean is $np$ and the variance is $np(1-p)$.",
          r"Mean $=np=8\times0.7=5.6$. Variance $=np(1-p)=8\times0.7\times0.3=1.68$.",
          ans=r"mean $5.6$, variance $1.68$"),
    ]))
    return ex
