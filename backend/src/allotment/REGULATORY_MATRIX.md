# SEBI & Exchange IPO Allotment Regulatory Matrix

This document forms the primary source of truth for allotment rules used by the IPO engine. Every rule implemented in `regimes.py` MUST map directly to a verified row in this matrix.

---

## 1. Regulatory Regimes Summary

| Regime ID | Board Type | Issue Type | Effective From | Effective Until | Publication Date | Operative Regulation Reference | Policy Decision Reference | Exchange Implementation Reference | Source Type | Authority Level | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `MAINBOARD_PRE_2022` | Mainboard | Book-Built | 2018-09-11 | 2022-03-31 | 2018-09-11 | SEBI (ICDR) Regulations 2018, Schedule XIII, Part A | SEBI/HO/CFD/DIL2/CIR/P/2018 | BSE Notice 20180911-1 | `SEBI_REGULATION` | 1 | `VERIFIED` |
| `MAINBOARD_POST_2022` | Mainboard | Book-Built | 2022-04-01 | Present | 2022-01-14 | SEBI (ICDR) (Amendment) Regulations 2021, Regulation 49(2) | SEBI Board Decision Nov 2021 | BSE Notice 20220331-45 | `SEBI_AMENDMENT` | 1 | `VERIFIED` |
| `SME_OLD_FRAMEWORK` | SME | Book-Built / Fixed-Price | 2018-09-11 | 2024-12-31 | 2018-09-11 | Chapter IX of SEBI (ICDR) Regulations 2018, Regulation 253 | SEBI/HO/CFD/DIL2/CIR/P/2018 | BSE SME Guidelines / NSE Emerge Circular | `SEBI_REGULATION` | 2 | `VERIFIED` |
| `SME_2025_FRAMEWORK` | SME | Book-Built / Fixed-Price | 2025-01-01 | Present | 2024-12-18 | SEBI (ICDR) (SME Amendment) Regulations 2024 | SEBI Press Release PR No.32/2024 | BSE Circular 20241220-12 / NSE Circular 2024/89 | `SEBI_CIRCULAR` | 3 | `VERIFIED` |

---

## 2. Allotment Methodology Matrix by Category & Regime

### A. Retail Individual Investors (RII / Retail)

| Regime ID | Category | Minimum Application | Quota Share (% Net Offer) | Allocation Method | Oversubscription Allotment Method | Residual / Undersubscription Handling | Operative Regulation Reference | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `MAINBOARD_PRE_2022` | Retail | 1 Market Lot (up to ₹2 Lakhs) | 35% (or 10% under QIB 75% rule) | Minimum Lot Allotment | Draw of Lots if $N_R > L_R$ ($L_R = \lfloor \text{Quota} / \text{MinLot} \rfloor$) | Spillover to NII/QIB if undersubscribed | SEBI ICDR 2018 Schedule XIII, Part A | `VERIFIED` |
| `MAINBOARD_POST_2022` | Retail | 1 Market Lot (up to ₹2 Lakhs) | 35% (or 10% under QIB 75% rule) | Minimum Lot Allotment | Draw of Lots if $N_R > L_R$ ($L_R = \lfloor \text{Quota} / \text{MinLot} \rfloor$) | Spillover to NII/QIB if undersubscribed | SEBI ICDR 2018 Schedule XIII, Part A | `VERIFIED` |
| `SME_OLD_FRAMEWORK` | Retail | 1 Market Lot (Min ₹1 Lakh) | At least 50% of Net Offer | Minimum Lot Allotment | Draw of Lots if $N_{R\_SME} > L_{R\_SME}$ | Spillover to Non-Retail | SEBI ICDR 2018 Regulation 253 | `VERIFIED` |
| `SME_2025_FRAMEWORK` | Individual Investor | 2 Market Lots (Min > ₹2 Lakhs) | As specified in RHP | Minimum Lot Allotment | Draw of Lots if $N_{\text{Ind}} > L_{\text{Ind}}$ | Spillover to Non-Retail | SEBI 2025 SME Framework Review | `VERIFIED` |

---

### B. Non-Institutional Investors (NII / HNI / sNII / bNII)

| Regime ID | Category | Minimum Application | Quota Share (% Net Offer) | Allocation Method | Oversubscription Allotment Method | Residual / Undersubscription Handling | Operative Regulation Reference | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `MAINBOARD_PRE_2022` | NII (Combined) | > ₹2 Lakhs | 15% | Proportionate Allotment | Strictly Proportionate based on shares bid | Spillover to Retail/QIB | SEBI ICDR 2018 Schedule XIII | `VERIFIED` |
| `MAINBOARD_POST_2022` | sNII (Small NII) | ₹2,00,001 to ₹10,00,000 | 1/3 of NII Quota (5% of Net Offer) | Minimum sNII Lot Allotment | Draw of Lots for minimum sNII lot size if $N_{sNII} > L_{sNII}$ | Unallotted shares spillover to bNII | SEBI ICDR Amendment Reg 2021, Reg 49(2) | `VERIFIED` |
| `MAINBOARD_POST_2022` | bNII (Big NII) | > ₹10,00,000 | 2/3 of NII Quota (10% of Net Offer) | Minimum bNII Lot Allotment + Proportionate | Draw of Lots if $N_{bNII} > L_{bNII}$; else Min Lot + Proportionate Balance | Unallotted shares spillover to sNII | SEBI ICDR Amendment Reg 2021, Reg 49(2) | `VERIFIED` |
| `SME_OLD_FRAMEWORK` | Non-Retail / NII | > ₹1 Lakh | Up to 50% of Net Offer | Proportionate Allotment | Proportionate scaling subject to market lot rounding | Spillover to Retail | SEBI ICDR 2018 Regulation 253(2) | `VERIFIED` |
| `SME_2025_FRAMEWORK` | Non-Individual / NII | As per RHP | As specified in RHP | Proportionate Allotment | Proportionate scaling subject to market lot rounding | Spillover to Individual | SEBI 2025 SME Framework Review | `VERIFIED` |

---

## 3. Data Integrity & Metric Definitions

1. **Share Subscription Multiple ($S_{\text{share}}$)**:
   $$S_{\text{share}} = \frac{\text{Total Shares Bid in Category}}{\text{Total Shares Offered in Category}}$$
2. **Application Oversubscription Multiple ($S_{\text{app}}$)**:
   $$S_{\text{app}} = \frac{\text{Total Valid Applications Received}}{\text{Total Available Minimum Allotments } (L = \lfloor \text{Quota} / \text{MinLot} \rfloor)}$$
3. **Exact Minimum Allotment Draw Probability ($P_{\text{draw}}$)**:
   - Calculated strictly via named primitive `calculate_minimum_allotment_draw_probability()`.
   - Available ONLY when valid application count $N$ and quota allotments $L$ are known.
   - For Draw of Lots: $P_{\text{draw}} = \min\left(100\%, \frac{L}{N} \times 100\%\right)$.
   - If $N$ is unknown: $P_{\text{draw}} = \text{null}$, status = `INSUFFICIENT_APPLICATION_DATA`.
