r"""Les 4 questions (3 parties chacune, 20 points) de l'epreuve inedite GCE O Level Commerce Paper 2 n.1 (voir generer_commerce_p2.py).

Le vrai sujet : 6 questions de 20 points (parties a, b, c de 4 a 12 points), « Answer FOUR questions. All questions carry equal marks », 2 h 30. La plateforme
ne code pas ce choix : l'inedite garde QUATRE questions (version « answer ALL », 80 points). Chaque partie : bareme exact (`pts`), grille `crit` (somme = pts),
corrige = reponse modele complete d'un candidat qui obtient tous les points (introduction, points numerotes en gras, exemples), reponse chiffree `ans` pour les calculs.
Themes du Paper 1 evites (voir questions_commerce_p1.py). Chaines BRUTES.
"""
from questions_addmaths_p2_a import E, S  # noqa: F401  (memes constructeurs)

TABLE_COMMERCE_EXTERIEUR = r"""| Item (million CFAF) | Amount |
|---|---|
| Visible exports | 1,200 |
| Visible imports | 1,450 |
| Invisible exports | 380 |
| Invisible imports | 260 |"""


def section():
    G = "PAPER 2"
    ex = []

    ex.append(E("1", G, 20, "", [
        S("a", "State and explain any FOUR principles of insurance.", ["insurance principles"], "moyenne", 8,
          [("Each principle correctly named: any four of utmost good faith, insurable interest, indemnity, proximate cause, subrogation, contribution (1 mark each)", 4),
           ("Each principle correctly explained (1 mark each)", 4)],
          "The principles of insurance are the rules that make a contract of insurance fair to the insured and to the insurer.",
          "**Introduction.** Insurance is a contract in which the insurer promises to compensate the insured for a loss caused by a risk that has been insured, in return for a premium. The contract is governed by the following principles.\n\n"
          "1. **Utmost good faith.** Both parties must tell each other every important fact. The insured must not hide anything that could change the decision of the insurer; if he does, the contract can be cancelled and a claim refused.\n"
          "2. **Insurable interest.** The insured must stand to lose money if the thing insured is lost or damaged. A trader has an insurable interest in his own shop and stock, but not in the shop of his neighbour.\n"
          "3. **Indemnity.** The insured is paid the actual loss, no more, so that he is put back in the position he was in before the loss. He must not make a profit from insurance.\n"
          "4. **Proximate cause.** The insurer pays only if the loss was caused by an insured risk that is the nearest (main) cause of the loss. A fire policy pays for damage caused by fire, not for goods stolen during a flood.\n\n"
          "*(Subrogation and contribution are also accepted: after paying a claim the insurer takes over the rights of the insured against the person who caused the loss; when the same risk is insured with two insurers, each pays its share.)*",
          piege="A principle must be both named and explained: a list of names earns only half of the marks."),
        S("b", "Explain THREE advantages of insurance to a business.", ["insurance principles", "types of insurance"], "faible", 6,
          [("Each advantage correctly stated (1 mark each)", 3), ("Each advantage correctly explained (1 mark each)", 3)],
          "An advantage must be stated and then explained in terms of what insurance does for the business.",
          "**Introduction.** A business faces many risks, such as fire, theft, accidents and the loss of goods in transport. Insurance turns an unknown and possibly very large loss into a small and known cost, the premium. Its advantages are the following.\n\n"
          "1. **Compensation for losses.** After a fire or a theft the insurer pays the loss, so that the business can replace its stock and machines and continue to trade instead of closing down.\n"
          "2. **Easier credit.** A bank is more ready to lend to a business whose buildings and stock are insured, because the security of the loan is protected against loss.\n"
          "3. **Peace of mind and confidence.** The owner is not afraid of a sudden loss, so he can plan, invest and expand the business without worrying about the risks that are insured.\n\n"
          "*(Other accepted points: the premiums collected are invested by insurance companies in the economy; life policies encourage saving.)*"),
        S("c", "Outline THREE risks that cannot be insured, giving an example of each.", ["insurable and uninsurable risks"], "faible", 6,
          [("Each uninsurable risk correctly outlined (1 mark each)", 3), ("A suitable example of each (1 mark each)", 3)],
          "An uninsurable risk is a risk that the insurer will not cover: the chance of loss cannot be measured, or the loss is not accidental, or the insured has no insurable interest.",
          "These are risks that an insurance company refuses to cover.\n\n"
          "1. **Speculative (gambling) risks.** The person takes the risk on purpose in the hope of a gain. *Example:* money lost in betting or by buying goods in the hope that their price will rise.\n"
          "2. **Changes in fashion and in tastes.** The chance of this loss cannot be measured. *Example:* a clothes trader who cannot sell his stock because the fashion has changed.\n"
          "3. **Losses caused on purpose by the insured.** A loss must be accidental. *Example:* a trader who sets fire to his own shop to claim the insurance money.\n\n"
          "*(Other accepted answers: losses caused by bad management, by competition or by war, if the insurer excludes them.)*"),
    ]))

    ex.append(E("2", G, 20, "", [
        S("a", "Explain any FOUR services that a commercial bank provides to its customers.", ["commercial banking services"], "moyenne", 8,
          [("Each service correctly named (1 mark each)", 4), ("Each service correctly explained (1 mark each)", 4)],
          "A commercial bank is a business that accepts deposits from the public and lends money; it also offers many other services to its customers.",
          "**Introduction.** A commercial bank is a profit-making business that keeps the money of the public and lends it to those who need it. It offers the following services to its customers.\n\n"
          "1. **Acceptance of deposits.** The bank opens current, savings and fixed deposit accounts, so that customers keep their money safely and, on some accounts, earn interest.\n"
          "2. **Safe custody of valuables.** Customers can keep documents, jewellery and other valuables in the strong rooms or the safe deposit boxes of the bank, where they are protected against fire and theft.\n"
          "3. **Foreign exchange.** The bank sells and buys foreign currency, so that traders can pay suppliers abroad and travellers can have money for their journeys.\n"
          "4. **Advice and references.** The bank advises its customers on investment and on the management of their money, and gives references that show the financial position of a customer to a supplier.\n\n"
          "*(Other accepted services: granting loans and overdrafts, payment of cheques and standing orders, transfer of money, night safe, collection of bills, cash machines, mobile banking.)*"),
        S("b", "Distinguish between a standing order and a credit transfer.", ["methods of payment"], "faible", 4,
          [("Standing order: an instruction to pay a fixed amount at regular intervals (1 mark) until it is cancelled, with an example such as rent or insurance premium (1 mark)", 2),
           ("Credit transfer: an instruction to move a sum from one account to another account, paid once (1 mark), with an example such as a salary or a supplier's invoice (1 mark)", 2)],
          "A standing order is repeated by the bank until the customer stops it; a credit transfer is a single instruction to pay a named account.",
          "**Standing order.** It is a written instruction from a customer to his bank to pay a fixed sum of money, at regular dates, to a named person or firm, until the customer cancels it. *Example:* the monthly rent of a shop or the yearly premium of an insurance policy.\n\n"
          "**Credit transfer.** It is an instruction to the bank to move a sum of money from the account of the payer to the account of another person, at the bank or at another bank, without a cheque. It is made once, and the amount can be different each time. *Example:* the payment of the salaries of the workers into their accounts, or the payment of a supplier's invoice.",
          piege="The difference to remember: a standing order is REPEATED at regular dates for a fixed amount; a credit transfer is made ONCE, for the amount stated."),
        S("c", "Mr Ngu borrows CFAF 1,800,000 from a bank for 2 years at a simple interest rate of 12% per year. Calculate:\n\ni) the interest for one year;\n\nii) the total interest for the 2 years;\n\niii) the total amount that Mr Ngu must repay;\n\niv) the monthly instalment, if the total amount is repaid in 24 equal monthly instalments.",
          ["business capital and interest"], "moyenne", 8,
          [("i) interest for one year = 1,800,000 × 12 ÷ 100 = CFAF 216,000", 2), ("ii) total interest = 216,000 × 2 = CFAF 432,000", 2),
           ("iii) total repayment = 1,800,000 + 432,000 = CFAF 2,232,000", 2), ("iv) monthly instalment = 2,232,000 ÷ 24 = CFAF 93,000", 2)],
          "Simple interest = principal × rate × time ÷ 100. The total to repay is the principal plus the interest.",
          "**i) Interest for one year** = principal × rate ÷ 100 = 1,800,000 × 12 ÷ 100 = **CFAF 216,000**.\n\n"
          "**ii) Total interest for 2 years** = 216,000 × 2 = **CFAF 432,000**.\n\n"
          "**iii) Total amount to repay** = principal + interest = 1,800,000 + 432,000 = **CFAF 2,232,000**.\n\n"
          "**iv) Monthly instalment** = 2,232,000 ÷ 24 = **CFAF 93,000**.",
          ans="CFAF 216,000 ; CFAF 432,000 ; CFAF 2,232,000 ; CFAF 93,000",
          piege="The rate is given PER YEAR: for 2 years the interest is twice the interest of one year. The instalments are monthly, so the number of instalments is 24, not 2."),
    ]))

    ex.append(E("3", G, 20, "", [
        S("a", "State and explain THREE methods used by governments to restrict imports.", ["import and export controls"], "faible", 6,
          [("Each method correctly stated: any three of import duties (tariffs), quotas, embargo, import licences, exchange control (1 mark each)", 3), ("Each method correctly explained (1 mark each)", 3)],
          "A government restricts imports to protect local industries, to save foreign currency and to protect consumers.",
          "**Introduction.** Governments control the entry of foreign goods into their country by the following methods.\n\n"
          "1. **Import duties (tariffs).** A tax paid on goods when they enter the country. It makes imported goods dearer than local goods, so people buy fewer of them.\n"
          "2. **Quotas.** A limit fixed by the government on the quantity or the value of a product that may be imported in a period. Once the quota is reached, no more of the product can enter.\n"
          "3. **Embargo.** A complete ban on trade, in one or several products, with a country, usually for political reasons or to protect health and safety.\n\n"
          "*(Import licences, which allow only holders of a permit to import, and exchange control, which limits the foreign currency available for imports, are also accepted.)*"),
        S("b", "The table below shows the foreign trade of country X in one year.\n\n" + TABLE_COMMERCE_EXTERIEUR + "\n\nCalculate, for country X:\n\ni) the balance of trade;\n\nii) the invisible balance;\n\niii) the balance of payments on current account.",
          ["visible and invisible exports"], "faible", 6,
          [("i) balance of trade = visible exports − visible imports = 1,200 − 1,450 = −250 million CFAF (deficit)", 2), ("ii) invisible balance = 380 − 260 = +120 million CFAF (surplus)", 2),
           ("iii) current account = −250 + 120 = −130 million CFAF (deficit)", 2)],
          "The balance of trade is the difference between visible exports and visible imports; the invisible balance is the difference between invisible exports and invisible imports; the balance of payments on current account is the sum of the two.",
          "**i) Balance of trade** = visible exports − visible imports = 1,200 − 1,450 = **−250 million CFAF**. This is a deficit: the country imports more goods than it exports.\n\n"
          "**ii) Invisible balance** = invisible exports − invisible imports = 380 − 260 = **+120 million CFAF**. This is a surplus.\n\n"
          "**iii) Balance of payments on current account** = visible balance + invisible balance = −250 + 120 = **−130 million CFAF**. This is a deficit.",
          ans="−250 million CFAF ; +120 million CFAF ; −130 million CFAF",
          piege="Imports are subtracted from exports, in this order: a negative result is a deficit, and the sign must be shown."),
        S("c", "Explain any FOUR advantages of containerisation in the transport of goods.", ["transport in commerce"], "moyenne", 8,
          [("Each advantage correctly stated (1 mark each)", 4), ("Each advantage correctly explained (1 mark each)", 4)],
          "A container is a large standard steel box in which goods are packed once and carried by ship, rail or road without being unpacked on the way.",
          "**Introduction.** Containerisation is the carriage of goods in standard-size steel containers. Its advantages are the following.\n\n"
          "1. **Safety of the goods.** The goods are locked in a strong container, so they are protected against theft, rain and damage during loading and on the way.\n"
          "2. **Quick loading and unloading.** Cranes lift whole containers in a few minutes, so ships spend less time in port and the cost of port charges falls.\n"
          "3. **Door-to-door carriage.** The same container goes from the factory to the ship, then by rail or lorry to the buyer, without repacking the goods at each change of transport.\n"
          "4. **Lower packing and insurance costs.** The container is itself a strong package, so the goods need less packing, and the lower risk of loss and damage reduces the insurance premium.\n\n"
          "*(Other accepted points: less handling by workers, better use of the space on board, containers can be used again many times.)*"),
    ]))

    ex.append(E("4", G, 20, "", [
        S("a", "State and explain THREE forms of sales promotion that a retailer can use to increase sales.", ["advertising and sales promotion"], "faible", 6,
          [("Each form of sales promotion correctly stated (1 mark each)", 3), ("Each form correctly explained (1 mark each)", 3)],
          "Sales promotion means the short-term methods, other than advertising, used to encourage customers to buy at once.",
          "**Introduction.** Sales promotion is a set of short-term actions that a retailer uses to push customers to buy now. The main forms are the following.\n\n"
          "1. **Free samples.** A small quantity of a new product, such as soap or biscuits, is given free so that customers try it and buy it later.\n"
          "2. **Price reductions (sales).** The retailer sells at a lower price for a short period, for example at the end of a season, to sell old stock and attract buyers.\n"
          "3. **Loyalty rewards.** Customers receive points or a gift for each purchase, so that they come back to the same shop.\n\n"
          "*(Other accepted forms: free gifts, competitions with prizes, demonstrations in the shop, buy-one-get-one-free offers.)*"),
        S("b", "Explain any FOUR disadvantages of advertising to consumers.", ["advertising and sales promotion"], "moyenne", 8,
          [("Each disadvantage correctly stated (1 mark each)", 4), ("Each disadvantage correctly explained (1 mark each)", 4)],
          "The disadvantages to consumers come from the cost of advertising, and from the way in which it can mislead or pressure people to buy.",
          "**Introduction.** Advertising informs the public, but it also has disadvantages for the consumers.\n\n"
          "1. **Higher prices.** Advertising is expensive, and the firm adds its cost to the price of the product, so the consumers finally pay for it.\n"
          "2. **Misleading information.** Some advertisements exaggerate the qualities of a product or hide its weaknesses, so that consumers buy goods that do not give the satisfaction promised.\n"
          "3. **Unnecessary buying.** Persuasive advertisements create wants, and consumers spend money on goods they do not need, sometimes more than they can afford.\n"
          "4. **Confusion and waste.** Many rival advertisements for similar goods make it hard to choose; some advertisements also encourage the use of harmful goods or offend people.\n\n"
          "*(Other accepted points: advertising can influence children too strongly; brands that spend a lot on advertising may drive small firms out of the market.)*"),
        S("c", "Outline THREE ways in which consumers are protected.", ["consumer protection"], "faible", 6,
          [("Each way of protecting consumers correctly stated (1 mark each)", 3), ("Each way correctly explained (1 mark each)", 3)],
          "Consumers are protected by the government through laws and controls, and by associations and bodies that defend their interests.",
          "Consumers need protection against unsafe goods, false descriptions and unfair prices. They are protected in the following ways.\n\n"
          "1. **Laws and government control.** The law forbids the sale of expired, fake or harmful goods and of goods that do not match their description; officials inspect shops and markets and punish those who break the law.\n"
          "2. **Consumer associations.** Associations of consumers receive complaints, test goods, inform the public and put pressure on firms and on the government to defend the rights of consumers.\n"
          "3. **Standards and price control.** Bodies set standards of quality and safety for products and check them; the government fixes or watches the prices of essential goods to prevent exploitation.\n\n"
          "*(Other accepted answers: guarantees and after-sales service given by sellers, correct weights and measures, labelling of goods with the price and the date of expiry.)*"),
    ]))
    return ex
