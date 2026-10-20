r"""Les 50 questions de l'epreuve inedite GCE O Level Commerce Paper 1 n.1 (voir generer_commerce_p1.py).

Commerce : AUCUN ordre de syllabus dans les vrais Paper 1 (themes melanges d'une question a l'autre, mesure sur 8 sujets 2019-2026) ; l'ordre ci-dessous est
donc mele, sans deux questions de meme theme cote a cote. 5 questions « EXCEPT / NOT » (11 % dans le corpus), 4 calculs commerciaux (5,5 % des questions du
corpus contiennent un nombre), aucune figure. Themes = noms de Tag existants de Commerce. Les themes du Paper 2 de la session (principes et avantages de
l'assurance, services bancaires, interet simple, restrictions a l'importation, balance commerciale, conteneurisation, promotion des ventes, inconvenients de la
publicite, protection des consommateurs) ne sont PAS traites ici. Chaines BRUTES.
"""


def Q(n, themes, diff, stem, ok, bad, rappel, sol, piege=None, conseil=None):
    return dict(n=n, themes=themes, diff=diff, stem=stem, ok=ok, bad=bad, rappel=rappel, sol=sol, piege=piege, conseil=conseil, fig=None)


def questions():
    qs = []
    a = qs.append

    a(Q(1, ["co-operative societies"], "faible",
        "A business owned by its members, in which each member has one vote whatever the number of shares held, is a:",
        "Co-operative society.", ["Public limited company.", "Sole proprietorship.", "Public corporation."],
        "In a co-operative society the members own the business and control it democratically: one member, one vote.",
        "Votes are given to persons, not to shares, so the business is a co-operative society. In a company, votes follow the number of shares held.",
        "In a public limited company the more shares a person holds, the more votes he has."))
    a(Q(2, ["commercial banking services"], "faible",
        "Which of the following accounts is operated mainly by means of a cheque book?",
        "Current account.", ["Savings account.", "Fixed deposit account.", "Loan account."],
        "A current account is opened by people and firms who make many payments: it is used with a cheque book and pays little or no interest.",
        "Cheques are written to make payments from the account, so it is a current account.",
        "A savings account is for keeping money and earning interest; withdrawals are made mainly with a passbook or a withdrawal slip."))
    a(Q(3, ["transport in commerce"], "faible",
        "The cheapest means of carrying very heavy and bulky goods over long distances between continents is:",
        "Sea transport.", ["Air transport.", "Road transport.", "Pipeline transport."],
        "Ships carry very large quantities at a low cost per tonne; they are slow but cheap.",
        "For heavy and bulky goods that cross oceans, the cost per tonne is lowest by sea.",
        "Air transport is the fastest but the most expensive."))
    a(Q(4, ["advertising and sales promotion"], "faible",
        "An advertisement that tries to persuade consumers to leave one brand and buy a rival brand is classified as:",
        "Competitive advertising.", ["Informative advertising.", "Generic advertising.", "Institutional advertising."],
        "Competitive advertising promotes one brand against rival brands; informative advertising gives facts; generic advertising promotes a whole kind of product.",
        "The aim is to win customers from rival brands, so the advertising is competitive.",
        "Generic advertising does not name a brand: it promotes the product as a whole, for example milk or tea."))
    a(Q(5, ["profit and mark-up calculations"], "moyenne",
        "A shop buys a radio at CFAF 60,000 and sells it at CFAF 78,000. The mark-up is:",
        "30%.", ["23%.", "18%.", "130%."],
        "Mark-up is the profit expressed as a percentage of the COST price: mark-up = profit ÷ cost price × 100. Margin is the profit as a percentage of the SELLING price.",
        "Profit = 78,000 − 60,000 = 18,000. Mark-up = 18,000 ÷ 60,000 × 100 = 30%.",
        "23% is the margin (18,000 ÷ 78,000 × 100), calculated on the selling price."))
    a(Q(6, ["types of insurance"], "faible",
        "An insurance policy that pays a sum of money to the family of the policyholder when he dies is a:",
        "Life assurance policy.", ["Fire insurance policy.", "Motor insurance policy.", "Burglary insurance policy."],
        "Life assurance pays a sum of money on the death of the insured person, or at the end of an agreed period.",
        "The sum is paid to the family at the death of the policyholder, so the policy is life assurance.",
        "Fire, motor and burglary policies protect property against loss: they do not depend on the death of a person."))
    a(Q(7, ["retail trade"], "faible",
        "A large retail shop in which customers pick the goods themselves from the shelves and pay at the exit is a:",
        "Supermarket.", ["Mail order firm.", "Kiosk.", "Hawker."],
        "A supermarket sells mainly foodstuffs and household goods by self-service: customers serve themselves and pay at the checkout.",
        "Self-service from shelves with payment at the exit describes a supermarket.",
        "A mail order firm sells through catalogues and posts the goods; a hawker moves from place to place."))
    a(Q(8, ["business documents"], "faible",
        "The document that a buyer sends to a seller to ask for the supply of goods is the:",
        "Order.", ["Invoice.", "Delivery note.", "Credit note."],
        "The business documents follow the sale in order: enquiry, quotation, order, delivery note, invoice, statement of account.",
        "The buyer starts the purchase by sending an order to the seller.",
        "The invoice is made by the seller after the order, to ask for payment."))
    a(Q(9, ["methods of payment"], "faible",
        "A cheque that the bank refuses to pay because the account of the drawer has too little money is said to be:",
        "Dishonoured.", ["Endorsed.", "Crossed.", "Certified."],
        "A dishonoured cheque is a cheque that the bank returns unpaid, for example because of insufficient funds in the drawer's account.",
        "The bank refuses payment for lack of funds: the cheque is dishonoured.",
        "Crossing a cheque only limits the way it is paid: it does not make the bank refuse it."))
    a(Q(10, ["company formation documents"], "faible",
        "The document that a public company publishes to invite the public to buy its shares is the:",
        "Prospectus.", ["Articles of association.", "Share certificate.", "Annual report."],
        "A prospectus gives information about the company and its plans so that the public can decide to buy shares.",
        "The invitation to the public is made by the prospectus.",
        "The articles of association are the internal rules of the company, and a share certificate is the proof of ownership given to a shareholder: neither is an invitation to buy shares."))
    a(Q(11, ["foreign trade concepts"], "faible",
        "Goods that a Cameroonian firm sends to another country to be sold there are called:",
        "Exports.", ["Imports.", "Transit goods.", "Tariffs."],
        "Exports are goods and services sold to other countries; imports are goods and services bought from other countries.",
        "Goods leaving Cameroon to be sold abroad are exports.",
        "Imports are goods that come into the country, not goods that leave it."))
    a(Q(12, ["scope of commerce"], "faible",
        "Banking, insurance, transport, advertising and warehousing are together called:",
        "Aids to trade.", ["Primary activities.", "Manufacturing activities.", "Trade barriers."],
        "Aids to trade are the services that help trade to take place by removing hindrances such as distance, risk, lack of money and lack of knowledge.",
        "These services assist trade, so they are the aids to trade.",
        "Primary activities take materials from nature, for example farming and fishing."))
    a(Q(13, ["communication services"], "faible",
        "A letter that the post office records on posting and delivery, and for which it pays compensation if it is lost, is sent by:",
        "Registered post.", ["Ordinary post.", "Franked post.", "Free post."],
        "Registered post gives a receipt on posting and a signature on delivery, with compensation if the item is lost.",
        "The record and the compensation are the features of registered post.",
        "Ordinary post is the cheapest service but it has no record of posting or delivery."))
    a(Q(14, ["commercial banking services"], "faible",
        "A bank customer who is allowed to withdraw more than the balance on his current account, up to an agreed limit, has an:",
        "Overdraft facility.", ["Fixed deposit.", "Credit card.", "Night safe."],
        "An overdraft lets a current account holder draw more than he has, up to a limit; interest is paid only on the amount overdrawn.",
        "Withdrawing more than the balance, up to a limit, is an overdraft.",
        "A fixed deposit is money that the customer lends to the bank for an agreed period: it is not a borrowing by the customer."))
    a(Q(15, ["commercial agents"], "moyenne",
        "An agent who sells goods for a principal, is paid by commission and does not become the owner of the goods is a:",
        "Commission agent.", ["Wholesaler.", "Retailer.", "Merchant."],
        "A commission agent works for a principal, never owns the goods and receives a percentage of the value of the sales.",
        "The three features (works for a principal, paid by commission, no ownership) describe a commission agent.",
        "A wholesaler and a retailer buy the goods and become their owners before selling them."))
    a(Q(16, ["transport in commerce"], "faible",
        "A cargo ship that sails on a fixed route and keeps to a fixed timetable is a:",
        "Liner.", ["Tramp.", "Tanker.", "Trawler."],
        "A liner follows a regular route and timetable; a tramp has no fixed route and sails where cargo is available.",
        "A fixed route and a timetable describe a liner.",
        "A tramp goes wherever there is cargo to carry, at any time."))
    a(Q(17, ["stock turnover"], "moyenne",
        "A trader's average stock is CFAF 2,000,000 and his cost of goods sold during the year is CFAF 12,000,000. His rate of stock turnover is:",
        "6 times.", ["10 times.", "14 times.", "24 times."],
        "Rate of stock turnover = cost of goods sold ÷ average stock. It shows how many times the stock is sold and replaced during the period.",
        "12,000,000 ÷ 2,000,000 = 6 times.",
        "24 times comes from multiplying the two figures instead of dividing."))
    a(Q(18, ["business ownership types"], "moyenne",
        "The following are features of a sole proprietorship EXCEPT:",
        "Its shares are sold on the stock exchange.", ["The owner has unlimited liability.", "It is easy to set up.", "The owner takes all the profit."],
        "A sole proprietor owns the whole business, takes all the profit and bears all the losses; the business has no shares to sell to the public.",
        "A sole proprietorship has no shares: it is owned by one person. The other three statements are features of this form of business.",
        "Shares quoted on a stock exchange belong to public limited companies."))
    a(Q(19, ["advertising and sales promotion"], "faible",
        "An advertisement painted on a large board beside a main road is an example of:",
        "Outdoor advertising.", ["Direct mail advertising.", "Press advertising.", "Broadcast advertising."],
        "Outdoor advertising uses billboards, posters, signs on vehicles and other displays placed in public places.",
        "A board by the roadside is a public display, so it is outdoor advertising.",
        "Press advertising uses newspapers and magazines; broadcast advertising uses radio and television."))
    a(Q(20, ["insurance principles"], "moyenne",
        "The person who visits the scene of a loss and reports to the insurance company on the size of the loss is the:",
        "Loss assessor.", ["Actuary.", "Broker.", "Underwriter."],
        "A loss assessor (or adjuster) investigates a claim and advises the insurer on the amount to be paid.",
        "Investigating the loss and reporting its size is the work of the loss assessor.",
        "An actuary studies risks and calculates premiums: he does not visit the scene of a loss."))
    a(Q(21, ["business documents"], "faible",
        "The document that is signed by the customer on receipt of the goods, to prove that they were delivered, is the:",
        "Delivery note.", ["Invoice.", "Credit note.", "Statement of account."],
        "A delivery note is sent with the goods; the customer signs a copy as proof that he received them.",
        "Proof of delivery signed by the customer is the delivery note.",
        "The invoice states the price and asks for payment: it is not signed as proof of delivery."))
    a(Q(22, ["retail trade"], "moyenne",
        "Which of the following is NOT a retailer?",
        "Wholesaler.", ["Hawker.", "Chain store.", "Mail order firm."],
        "Retailers sell goods in small quantities to the final consumers; wholesalers sell in large quantities to retailers.",
        "The wholesaler sells to retailers and not to the final consumers. The other three sell to consumers.",
        "A mail order firm is a retailer: it sells to consumers, but through catalogues and the post."))
    a(Q(23, ["commercial banking services"], "moyenne",
        "A document sent by a bank to a current account holder, showing the money paid in, the money paid out and the balance, is a:",
        "Bank statement.", ["Pay-in slip.", "Cheque.", "Bank draft."],
        "A bank statement lists the transactions on an account over a period, with the balance after each of them, and shows the bank charges.",
        "A list of the deposits, the payments and the balance is a bank statement.",
        "A pay-in slip is filled by the customer when he deposits money: it comes from the customer, not from the bank."))
    a(Q(24, ["foreign trade concepts"], "moyenne",
        "A country that imports goods in order to export them again, with little or no change, carries on:",
        "Entrepot trade.", ["Barter trade.", "Home trade.", "Retail trade."],
        "Entrepot trade means importing goods for re-export. Ports that serve neighbouring countries often live on this trade.",
        "Importing in order to export again is entrepot trade.",
        "Home trade takes place between traders of the same country."))
    a(Q(25, ["trade discounts and cash discounts"], "faible",
        "A trader sells goods with a list price of CFAF 50,000 and allows a trade discount of 20%. The price shown on the invoice is:",
        "CFAF 40,000.", ["CFAF 10,000.", "CFAF 30,000.", "CFAF 60,000."],
        "Trade discount is a reduction from the list price, given to traders who buy for resale; the invoice shows the list price less the trade discount.",
        "Trade discount = 20% of 50,000 = 10,000. Invoice price = 50,000 − 10,000 = 40,000.",
        "CFAF 10,000 is the amount of the discount, not the price that remains to be paid."))
    a(Q(26, ["warehousing"], "faible",
        "The person who is responsible for receiving, storing and issuing the goods kept in a warehouse is the:",
        "Storekeeper.", ["Cashier.", "Salesman.", "Auditor."],
        "The storekeeper receives the goods, stores them safely, issues them against a written request and keeps the stock records.",
        "Receiving, storing and issuing goods is the work of the storekeeper.",
        "A cashier handles money, not goods."))
    a(Q(27, ["methods of payment"], "moyenne",
        "A means of payment that a bank draws on itself, so that the payee is sure to be paid, is a:",
        "Bank draft.", ["Money order.", "Personal cheque.", "Bill of exchange."],
        "A bank draft is bought from a bank, which draws it on itself: the bank promises to pay, so it cannot be dishonoured for lack of funds.",
        "A cheque drawn by the bank on itself is a bank draft.",
        "A personal cheque is drawn on the customer's account and can be returned unpaid."))
    a(Q(28, ["business documents"], "moyenne",
        "The following are documents used between a buyer and a seller EXCEPT:",
        "Pay-in slip.", ["Order.", "Invoice.", "Delivery note."],
        "A pay-in slip is a banking document that a customer fills when he deposits money in his account.",
        "The order, the invoice and the delivery note pass between the buyer and the seller. The pay-in slip is a document between a customer and his bank.",
        "A credit note, like an invoice, is a document that the seller sends to the buyer."))
    a(Q(29, ["commercial channels of distribution"], "moyenne",
        "A manufacturer may sell directly to retailers because this:",
        "Reduces the cost of distribution.", ["Increases the number of middlemen.", "Raises the profit of wholesalers.", "Removes the need to deliver goods."],
        "When the wholesaler is by-passed, his profit margin disappears from the price: the cost of distribution falls.",
        "Selling directly to retailers removes the wholesaler and his margin, so the cost of distribution is reduced.",
        "Selling directly keeps the manufacturer's task of delivery, and sometimes adds to it."))
    a(Q(30, ["transport in commerce"], "moyenne",
        "The following are disadvantages of road transport EXCEPT:",
        "Door-to-door delivery.", ["Delays caused by traffic jams.", "Damage to goods on bad roads.", "Small loads compared with rail."],
        "Road transport is flexible and can serve places that have no railway; its weaknesses are small loads, congestion and poor road conditions.",
        "Door-to-door delivery is an advantage of road transport. The three other statements are weaknesses.",
        "Door-to-door service is the main reason why road transport is so widely used for short and medium distances."))
    a(Q(31, ["company securities and investors"], "moyenne",
        "A shareholder who receives a fixed rate of dividend, and is paid before ordinary shareholders when profits are shared, holds:",
        "Preference shares.", ["Ordinary shares.", "Debentures.", "Deferred shares."],
        "Preference shareholders have a fixed rate of dividend and are paid before ordinary shareholders; they are owners of the company but have limited voting rights.",
        "A fixed dividend paid first is the right of preference shareholders.",
        "Debenture holders are creditors who receive interest, not shareholders who receive dividends."))
    a(Q(32, ["quotations and delivery terms"], "moyenne",
        "A quotation sent by a seller to a buyer states:",
        "The price and terms on which the seller is ready to supply the goods.", ["The date on which the goods were delivered.", "The amount that the buyer has already paid.", "The goods lost on the way."],
        "A quotation is the answer to an enquiry: it gives the price, the delivery terms and the conditions of payment, and is not yet a sale.",
        "The seller states what he is ready to supply and on what terms: price, delivery and payment.",
        "A quotation is not a bill: nothing has been sold when it is sent."))
    a(Q(33, ["advertising and sales promotion"], "faible",
        "The following are advertising media EXCEPT the:",
        "Invoice.", ["Radio.", "Billboard.", "Newspaper."],
        "Advertising media are the channels used to reach the public: radio, television, newspapers, posters, billboards and the internet.",
        "An invoice is a business document between a seller and a buyer: it does not carry an advertisement to the public.",
        "Newspapers, radio and billboards are media; an invoice is not."))
    a(Q(34, ["insurance documents"], "moyenne",
        "A temporary document that gives the insured cover until the policy is issued is a:",
        "Cover note.", ["Claim form.", "Proposal form.", "Premium receipt."],
        "A cover note is issued by the insurer or his agent as temporary evidence of cover until the policy is ready.",
        "A temporary proof of cover before the policy is issued is a cover note.",
        "The proposal form is filled by the person who wants the insurance, before any cover is given."))
    a(Q(35, ["commercial banking services"], "moyenne",
        "Which of the following can a borrower offer to a bank as security for a loan?",
        "The title deed of a piece of land.", ["A bank statement.", "A delivery note.", "A cheque book."],
        "A bank asks for security, such as a title deed or a life policy, that it can sell to recover the money if the borrower fails to repay.",
        "A title deed is a valuable asset that the bank can hold and sell if the loan is not repaid.",
        "A bank statement only reports what has happened on an account: it has no value of its own."))
    a(Q(36, ["customs administration"], "faible",
        "The government department that collects import duties on goods entering Cameroon at the port of Douala is the:",
        "Customs department.", ["Postal service.", "Ministry of Education.", "Chamber of commerce."],
        "The customs department controls the goods that enter and leave the country and collects import and export duties.",
        "Collecting duties on goods entering the country is the work of the customs department.",
        "A chamber of commerce is an association of traders: it has no power to collect duties."))
    a(Q(37, ["vat calculations"], "moyenne",
        "Goods have a net price of CFAF 80,000. Value added tax (VAT) is charged at 19.25%. The total price payable is:",
        "CFAF 95,400.", ["CFAF 15,400.", "CFAF 80,000.", "CFAF 94,000."],
        "VAT is added to the net price: total price = net price + net price × VAT rate.",
        "VAT = 80,000 × 19.25 ÷ 100 = 15,400. Total price = 80,000 + 15,400 = 95,400.",
        "CFAF 15,400 is only the amount of the tax: the net price must be added."))
    a(Q(38, ["limited liability companies"], "moyenne",
        "A public limited company can raise more capital than a partnership mainly because it:",
        "Can sell its shares to the general public.", ["Has partners with unlimited liability.", "Is owned by the government.", "Has only one owner."],
        "A public limited company issues shares to the public, so it can collect small sums from a very large number of investors.",
        "Selling shares to the public gives access to a very large number of investors, whereas a partnership has only a few partners.",
        "In a public limited company the liability of the shareholders is limited: unlimited liability belongs to partners."))
    a(Q(39, ["commercial agents"], "moyenne",
        "The agent who arranges the transport and the customs clearance of goods on behalf of an exporter is the:",
        "Forwarding agent.", ["Del credere agent.", "Insurance agent.", "Sales agent."],
        "A forwarding agent handles the documents, the customs clearance, the packing and the transport of goods for exporters and importers.",
        "Arranging transport and customs clearance is the work of a forwarding agent.",
        "A del credere agent sells goods and guarantees that the buyers will pay."))
    a(Q(40, ["hire purchase"], "moyenne",
        "In a credit sale, the ownership of the goods passes to the buyer:",
        "At the time of the sale.", ["After the last instalment.", "After the deposit is paid.", "At the end of the year."],
        "In a credit sale the buyer becomes the owner at once and pays later; in hire purchase he becomes the owner only after the last instalment.",
        "The buyer takes the goods and becomes their owner immediately, even though he pays later.",
        "Ownership after the last instalment is the rule of hire purchase, not of credit sale."))
    a(Q(41, ["transport in commerce"], "faible",
        "A small parcel of urgent medicines is to be sent to a distant country. The most suitable means of transport is:",
        "Air transport.", ["Sea transport.", "Rail transport.", "Road transport."],
        "Air transport is the fastest means and suits light, valuable or urgent goods over long distances.",
        "The parcel is small, urgent and travels far: air transport is the best choice.",
        "Sea transport is cheaper but slow: it does not suit urgent goods."))
    a(Q(42, ["division of labour and specialisation"], "faible",
        "The main advantage of division of labour to a firm is:",
        "A higher output per worker.", ["Workers who can do any job.", "Less dependence between workers.", "More interesting work for each worker."],
        "In division of labour each worker does one task, so he becomes quicker and more skilled and the output per worker rises.",
        "Repeating one task makes workers faster, so output per worker rises.",
        "Division of labour makes work repetitive and creates dependence between workers: these are disadvantages."))
    a(Q(43, ["business funding sources"], "faible",
        "Money that a company keeps from its profits to finance its growth is:",
        "Retained profit.", ["Bank overdraft.", "Debentures.", "Trade credit."],
        "Retained (ploughed-back) profit is an internal source of finance: it comes from the business itself.",
        "Profit kept in the business is retained profit.",
        "An overdraft, debentures and trade credit are borrowed from outside the business."))
    a(Q(44, ["trade discounts and cash discounts"], "elevee",
        "A trader buys goods with a list price of CFAF 200,000. He is allowed a trade discount of 25% and a cash discount of 4% for payment within 10 days. If he pays within 10 days, he pays:",
        "CFAF 144,000.", ["CFAF 142,000.", "CFAF 150,000.", "CFAF 192,000."],
        "Trade discount is deducted from the list price first; cash discount is then calculated on the amount that remains to be paid, not on the list price.",
        "Net invoice price = 200,000 − 25% of 200,000 = 150,000. Cash discount = 4% of 150,000 = 6,000. Amount paid = 150,000 − 6,000 = 144,000.",
        "CFAF 142,000 comes from taking the cash discount on the list price (4% of 200,000 = 8,000)."))
    a(Q(45, ["business funding sources"], "moyenne",
        "A small retailer who has no cash to buy stock for the next two weeks can best use:",
        "Trade credit from suppliers.", ["A long-term mortgage.", "An issue of ordinary shares.", "Debentures."],
        "Trade credit means buying goods now and paying the supplier later: it is a short-term source of finance.",
        "The need is small and short, so buying on credit from suppliers is the best source.",
        "Mortgages, shares and debentures are long-term sources: they take time to arrange and suit large amounts."))
    a(Q(46, ["foreign trade documents"], "moyenne",
        "An importer fills a form to declare to the customs the goods that he is bringing into the country. This form is the:",
        "Bill of entry.", ["Bill of lading.", "Certificate of origin.", "Shipping note."],
        "The bill of entry is the declaration of imported goods made to the customs, which then calculates the duty to be paid.",
        "The importer's declaration to the customs is the bill of entry.",
        "The bill of lading is a document issued by the shipping company for the goods carried."))
    a(Q(47, ["social responsibility of business"], "faible",
        "A firm that builds a borehole for the villagers who live near its factory is showing:",
        "Social responsibility.", ["Price discrimination.", "Trade protection.", "Competitive advertising."],
        "Social responsibility means that a firm cares for the people and the environment around it, beyond the profit that it makes.",
        "Helping the community around the factory is social responsibility.",
        "A gift to a community may bring publicity, but its main idea is to meet the needs of the people nearby."))
    a(Q(48, ["transport in commerce"], "faible",
        "A pipeline is used mainly to transport:",
        "Crude oil and gas.", ["Fresh fish.", "Passengers.", "Timber."],
        "A pipeline carries liquids and gases over long distances, for example crude oil, natural gas and water.",
        "Liquids and gases flow along the pipes, so crude oil and gas are the usual cargo.",
        "Solid goods and passengers cannot flow through a pipeline."))
    a(Q(49, ["incoterms"], "elevee",
        "A Cameroonian importer buys goods at a CIF Douala price. Which of the following costs is paid by the importer and is NOT included in the CIF price?",
        "The import duty at Douala.", ["The marine insurance during the voyage.", "The freight from the port of loading to Douala.", "The cost of loading the goods on the ship."],
        "CIF means cost, insurance and freight: the seller pays the cost of the goods, the loading, the marine insurance and the freight up to the port named. Duties and the costs after arrival are paid by the buyer.",
        "Insurance, freight and loading are included in a CIF price. The import duty is a tax of the importing country, paid by the importer.",
        "CIF covers the transport and the insurance up to Douala, not the taxes due in Cameroon."))
    a(Q(50, ["central and commercial banks"], "moyenne",
        "The body that supervises the commercial banks in the countries of Central Africa is:",
        "COBAC.", ["BEAC.", "CEMAC.", "BICEC."],
        "COBAC (the Central African Banking Commission) controls the banks and credit institutions of the region; BEAC is the central bank that issues the currency.",
        "Supervising the banks is the task of COBAC.",
        "BEAC issues the CFA franc of Central Africa; BICEC is a commercial bank."))
    return qs
