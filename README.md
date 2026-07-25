# IPO Insight Engine

An application designed to help retail investors understand IPO allotment mechanics, pure probability odds, and historical pattern-matching without fabricating predictions. 

## SEBI Allotment Engine: Domain Knowledge
The backend of this application implements strict, industry-grade SEBI (Securities and Exchange Board of India) algorithms to calculate actual lottery allotment probabilities. Below are the core mechanical rules governing Indian IPOs:

### 1. The Primary Categories
Indian IPOs are divided into four main categories, each with distinct mathematical allotment rules:

* **Retail Individual Investors (RII)**
  * **Limit:** Up to ₹2,00,000.
  * **Rule:** Allotment via lottery. If the category is oversubscribed, everyone who is selected in the draw gets exactly **1 minimum lot**, regardless of whether they applied for 1 lot or 13 lots. Bidding deeper in retail does *not* increase your odds.
* **Small High Net Worth Individuals (sHNI / sNII)**
  * **Limit:** Strictly between ₹2,00,000 and ₹10,00,000.
  * **Rule:** Allotment via lottery. Winners receive exactly the **minimum sHNI lot size** (usually 14 or 15 lots, just crossing the ₹2L threshold).
* **Big High Net Worth Individuals (bHNI / bNII)**
  * **Limit:** Strictly above ₹10,00,000.
  * **Rule:** Allotment via lottery. Winners receive exactly the **minimum bHNI lot size** (usually 68-70 lots, crossing the ₹10L threshold).
* **Qualified Institutional Buyers (QIB)**
  * **Limit:** Tens to hundreds of crores (Banks, Mutual Funds).
  * **Rule:** Strictly proportional allocation. No lottery. 

*(Note: Some IPOs also feature special categories like Anchor Investors, Employees, and existing Shareholders).*

### 2. Strategy: The 13 vs. 14 Lot Trade-Off
A common investor dilemma is whether to max out the Retail category or jump into the sHNI category. Because lots are fixed (e.g., ₹14,500 each):
* **13 Lots (₹188,500):** Keeps you in Retail. You face a lower subscription multiple, meaning **higher odds** of winning. However, your reward is heavily capped—you only walk away with **1 lot**.
* **14 Lots (₹203,700):** Pushes you into sHNI. You face a different, often higher subscription multiple, meaning **lower odds** of winning. However, if you win, the reward is massive—you take home **all 14 lots**.

### 3. Cross-Category Spillover (The Bakery Analogy)
If an institutional category (QIB) or the Employee quota is undersubscribed (subscription multiple < 1.0x), those shares are not cancelled. Instead, the registrar "spills" the leftover shares into the Retail bucket.

* **Analogy:** Imagine a bakery with 100 croissants for regular customers (Retail) and 100 for corporate catering (QIB). If the corporates only buy 50, the bakery moves the leftover 50 to the regular customer counter. Supply goes up to 150, but the line of people stays the same—meaning the average customer's chance of getting a croissant mathematically jumps up.
* **Tracking:** We know exactly if there will be a spillover before listing because the exchanges lock the subscription numbers at 5:00 PM on the IPO's closing day. 

### 4. Technical Rejection Buffer ($k = 0.03$)
The raw "gross" subscription numbers published by exchanges assume every bid is perfect. Our engine applies a **3% technical rejection buffer** to account for failed UPI mandates, duplicate PANs, and rejected forms. This actively invalidates 3% of the competition before running the lottery math, realistically boosting the user's computed odds of success.

### 5. Fractional Share Floor and Volatility
SEBI mandates that allotments must be whole lots. Our backend strictly uses a mathematical floor function on available shares. Furthermore, for security, the engine operates on a **Zero-Discovery Protocol**—it validates PANs locally and exclusively uses volatile memory, guaranteeing that sensitive investor data is never persisted.
