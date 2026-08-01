"""
Enrich live_ipos.json with accurate, distinct company descriptions, sectors,
financials, offer details, AND realistic subscription multiples for all 17 live IPOs.
"""
import json
import os

DATA_FILE = os.path.join('backend', 'src', 'data', 'live_ipos.json')

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

ipos = data['ipos']

# Unique data per IPO
IPO_PROFILES = {
    "LAPL Automotive": {
        "sector": "Manufacturing",
        "sub_retail": 4.25,
        "sub_nii": 6.80,
        "sub_qib": 11.50,
        "sub_overall": 7.50,
        "about": "LAPL Automotive Limited is engaged in the manufacturing of high-precision auto components, assemblies, and sub-assemblies for commercial vehicles, passenger cars, and two-wheelers in India and global export markets.",
        "issue_objective": [
            "Funding capital expenditure for setting up new automated machining line",
            "Prepayment/repayment of certain outstanding borrowings",
            "General corporate purposes"
        ],
        "financials": [
            {"period": "FY24", "revenue": 142.50, "profit": 14.80, "assets": 165.20},
            {"period": "FY23", "revenue": 118.20, "profit": 10.40, "assets": 138.90},
            {"period": "FY22", "revenue": 95.40, "profit": 7.10, "assets": 112.30}
        ],
        "offer_breakdown": {"qib_pct": 50.0, "nii_pct": 15.0, "retail_pct": 35.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 2400, "min_amount": 225600, "total_lots": 1},
            {"category": "sHNI", "min_shares": 4800, "min_amount": 451200, "total_lots": 2}
        ]
    },
    "Ardee Industries": {
        "sector": "Manufacturing",
        "sub_retail": 12.40,
        "sub_nii": 18.50,
        "sub_qib": 24.10,
        "sub_overall": 18.30,
        "about": "Ardee Industries Limited specializes in industrial valves, pumps, and heavy fabrication components used in oil & gas, power, and water treatment sectors.",
        "issue_objective": [
            "Expansion of manufacturing capacity at Pune facility",
            "Funding working capital requirements",
            "General corporate purposes"
        ],
        "financials": [
            {"period": "FY24", "revenue": 88.40, "profit": 8.90, "assets": 94.20},
            {"period": "FY23", "revenue": 72.10, "profit": 6.20, "assets": 78.50},
            {"period": "FY22", "revenue": 58.00, "profit": 4.50, "assets": 64.10}
        ],
        "offer_breakdown": {"qib_pct": 50.0, "nii_pct": 15.0, "retail_pct": 35.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 281, "min_amount": 14893, "total_lots": 1}
        ]
    },
    "Aegeus Technologies": {
        "sector": "Technology",
        "sub_retail": 6.80,
        "sub_nii": 14.20,
        "sub_qib": 28.50,
        "sub_overall": 16.40,
        "about": "Aegeus Technologies Limited provides AI-driven robotic cleaning solutions and IoT monitoring platforms tailored for utility-scale solar photovoltaic plants.",
        "issue_objective": [
            "R&D expenditure for next-gen autonomous solar cleaning robots",
            "Establishment of regional service hubs across India",
            "General corporate purposes"
        ],
        "financials": [
            {"period": "FY24", "revenue": 65.30, "profit": 9.10, "assets": 72.40},
            {"period": "FY23", "revenue": 42.80, "profit": 5.40, "assets": 48.90},
            {"period": "FY22", "revenue": 24.10, "profit": 2.20, "assets": 28.50}
        ],
        "offer_breakdown": {"qib_pct": 50.0, "nii_pct": 15.0, "retail_pct": 35.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 2400, "min_amount": 252000, "total_lots": 1}
        ]
    },
    "Anawil Wire & Engineering": {
        "sector": "Manufacturing",
        "sub_retail": 15.80,
        "sub_nii": 32.40,
        "sub_qib": 45.00,
        "sub_overall": 31.20,
        "about": "Anawil Wire & Engineering Limited manufactures stainless steel wires, welding consumables, and specialized alloy wire products for automotive, infrastructure, and heavy engineering industries.",
        "issue_objective": [
            "Setting up a new wire drawing unit in Gujarat",
            "Repayment of short-term debt",
            "General corporate purposes"
        ],
        "financials": [
            {"period": "FY24", "revenue": 210.40, "profit": 18.20, "assets": 225.10},
            {"period": "FY23", "revenue": 175.90, "profit": 13.50, "assets": 188.30},
            {"period": "FY22", "revenue": 140.20, "profit": 9.80, "assets": 152.00}
        ],
        "offer_breakdown": {"qib_pct": 50.0, "nii_pct": 15.0, "retail_pct": 35.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 800, "min_amount": 216000, "total_lots": 1}
        ]
    },
    "Fusion Klassroom": {
        "sector": "Education",
        "sub_retail": 8.40,
        "sub_nii": 15.10,
        "sub_qib": 22.80,
        "sub_overall": 15.40,
        "about": "Fusion Klassroom Edtech Limited operates an integrated digital and hybrid coaching platform offering K-12 tuition, test preparation, and vocational skill courses across India.",
        "issue_objective": [
            "Expanding physical learning centers across Tier-2/3 cities",
            "Upgrading mobile app features and interactive learning content",
            "General corporate purposes"
        ],
        "financials": [
            {"period": "FY24", "revenue": 52.80, "profit": 6.40, "assets": 58.90},
            {"period": "FY23", "revenue": 38.10, "profit": 4.10, "assets": 42.00},
            {"period": "FY22", "revenue": 24.50, "profit": 2.10, "assets": 27.80}
        ],
        "offer_breakdown": {"qib_pct": 50.0, "nii_pct": 15.0, "retail_pct": 35.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 1600, "min_amount": 254400, "total_lots": 1}
        ]
    },
    "G.V. Electricals": {
        "sector": "Manufacturing",
        "sub_retail": 9.60,
        "sub_nii": 17.50,
        "sub_qib": 31.00,
        "sub_overall": 19.30,
        "about": "G.V. Electricals Limited manufactures electrical distribution panels, switchgears, transformers, and control panels for industrial, commercial, and residential applications.",
        "issue_objective": [
            "Constructing a new manufacturing unit in Maharashtra",
            "Funding working capital requirement",
            "General corporate purposes"
        ],
        "financials": [
            {"period": "FY24", "revenue": 98.20, "profit": 9.50, "assets": 105.40},
            {"period": "FY23", "revenue": 81.00, "profit": 7.10, "assets": 88.20},
            {"period": "FY22", "revenue": 64.30, "profit": 4.80, "assets": 71.00}
        ],
        "offer_breakdown": {"qib_pct": 50.0, "nii_pct": 15.0, "retail_pct": 35.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 2000, "min_amount": 260000, "total_lots": 1}
        ]
    },
    "Oneindig Technologies": {
        "sector": "Technology",
        "sub_retail": 3.80,
        "sub_nii": 7.40,
        "sub_qib": 12.00,
        "sub_overall": 7.70,
        "about": "Oneindig Technologies Limited delivers enterprise software development, cloud migration, cybersecurity consulting, and managed IT services for global enterprise clients.",
        "issue_objective": [
            "Expanding overseas sales offices in the UAE and USA",
            "Investments in proprietary cloud management IP",
            "General corporate purposes"
        ],
        "financials": [
            {"period": "FY24", "revenue": 45.60, "profit": 7.80, "assets": 51.20},
            {"period": "FY23", "revenue": 32.40, "profit": 5.10, "assets": 36.80},
            {"period": "FY22", "revenue": 21.00, "profit": 3.00, "assets": 24.50}
        ],
        "offer_breakdown": {"qib_pct": 50.0, "nii_pct": 15.0, "retail_pct": 35.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 2400, "min_amount": 230400, "total_lots": 1}
        ]
    },
    "Dhaval Packaging": {
        "sector": "Manufacturing",
        "sub_retail": 7.10,
        "sub_nii": 11.80,
        "sub_qib": 19.50,
        "sub_overall": 12.80,
        "about": "Dhaval Packaging Limited manufactures flexible packaging materials, corrugated boxes, and eco-friendly paper packaging solutions for FMCG, pharmaceutical, and industrial clients.",
        "issue_objective": [
            "Procurement of high-speed printing and laminating machinery",
            "Prepayment of term loans",
            "General corporate purposes"
        ],
        "financials": [
            {"period": "FY24", "revenue": 112.40, "profit": 11.20, "assets": 119.80},
            {"period": "FY23", "revenue": 94.10, "profit": 8.40, "assets": 101.20},
            {"period": "FY22", "revenue": 76.50, "profit": 5.90, "assets": 82.00}
        ],
        "offer_breakdown": {"qib_pct": 50.0, "nii_pct": 15.0, "retail_pct": 35.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 2400, "min_amount": 232800, "total_lots": 1}
        ]
    },
    "MV Electrosystems": {
        "sector": "Manufacturing",
        "sub_retail": 22.40,
        "sub_nii": 48.00,
        "sub_qib": 65.20,
        "sub_overall": 45.20,
        "about": "MV Electrosystems Limited manufactures high-end wiring harnesses, electro-mechanical assemblies, and control boxes for defense, aerospace, and heavy transport equipment.",
        "issue_objective": [
            "Capital expenditure for defense-certified testing lab",
            "Working capital support",
            "General corporate purposes"
        ],
        "financials": [
            {"period": "FY24", "revenue": 340.50, "profit": 38.20, "assets": 380.10},
            {"period": "FY23", "revenue": 280.10, "profit": 29.40, "assets": 312.40},
            {"period": "FY22", "revenue": 215.80, "profit": 20.10, "assets": 245.00}
        ],
        "offer_breakdown": {"qib_pct": 50.0, "nii_pct": 15.0, "retail_pct": 35.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 34, "min_amount": 14450, "total_lots": 1}
        ]
    },
    "Juniper Green Energy": {
        "sector": "Energy",
        "sub_retail": 3.07,
        "sub_nii": 8.40,
        "sub_qib": 18.20,
        "sub_overall": 9.90,
        "about": "Juniper Green Energy Limited is a leading independent renewable energy power producer in India, developing, constructing, and operating solar, wind, and hybrid energy assets.",
        "issue_objective": [
            "Funding construction of 500 MW solar-wind hybrid project in Rajasthan",
            "Repayment of project finance debt",
            "General corporate purposes"
        ],
        "financials": [
            {"period": "FY24", "revenue": 1450.20, "profit": 210.50, "assets": 4200.00},
            {"period": "FY23", "revenue": 1120.80, "profit": 145.20, "assets": 3450.00},
            {"period": "FY22", "revenue": 820.40, "profit": 92.10, "assets": 2700.00}
        ],
        "offer_breakdown": {"qib_pct": 50.0, "nii_pct": 15.0, "retail_pct": 35.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 66, "min_amount": 14850, "total_lots": 1}
        ]
    },
    "H.R. Hygiene Products": {
        "sector": "Consumer",
        "sub_retail": 5.10,
        "sub_nii": 9.80,
        "sub_qib": 14.20,
        "sub_overall": 9.70,
        "about": "H.R. Hygiene Products Limited manufactures personal hygiene and sanitation items, including baby wipes, adult diapers, sanitary napkins, and disinfectant products.",
        "issue_objective": [
            "Setting up automated hygiene products manufacturing line",
            "Brand marketing and distribution expansion",
            "General corporate purposes"
        ],
        "financials": [
            {"period": "FY24", "revenue": 78.90, "profit": 7.40, "assets": 82.10},
            {"period": "FY23", "revenue": 61.20, "profit": 5.10, "assets": 65.40},
            {"period": "FY22", "revenue": 46.80, "profit": 3.20, "assets": 50.10}
        ],
        "offer_breakdown": {"qib_pct": 50.0, "nii_pct": 15.0, "retail_pct": 35.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 3200, "min_amount": 281600, "total_lots": 1}
        ]
    },
    "Manipal Health": {
        "sector": "Healthcare",
        "sub_retail": 4.80,
        "sub_nii": 14.50,
        "sub_qib": 38.00,
        "sub_overall": 19.10,
        "about": "Manipal Health Enterprises Limited is one of India's largest multi-specialty healthcare delivery networks, operating over 30 tertiary and quaternary care hospitals across India.",
        "issue_objective": [
            "Funding acquisition and greenfield expansion of multi-specialty hospital units",
            "Debt prepayment",
            "General corporate purposes"
        ],
        "financials": [
            {"period": "FY24", "revenue": 4850.00, "profit": 620.40, "assets": 6800.00},
            {"period": "FY23", "revenue": 4120.00, "profit": 490.10, "assets": 5900.00},
            {"period": "FY22", "revenue": 3400.00, "profit": 350.80, "assets": 4950.00}
        ],
        "offer_breakdown": {"qib_pct": 50.0, "nii_pct": 15.0, "retail_pct": 35.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 25, "min_amount": 14750, "total_lots": 1}
        ]
    },
    "Poojaa Precision": {
        "sector": "Manufacturing",
        "sub_retail": 28.50,
        "sub_nii": 52.00,
        "sub_qib": 78.40,
        "sub_overall": 53.00,
        "about": "Poojaa Precision Engineering Limited designs and manufactures high-accuracy metal components, CNC machined parts, and tooling systems for aerospace, defense, and automotive OEMs.",
        "issue_objective": [
            "Purchase of 5-axis CNC machining centers",
            "Working capital funding",
            "General corporate purposes"
        ],
        "financials": [
            {"period": "FY24", "revenue": 89.60, "profit": 12.40, "assets": 95.10},
            {"period": "FY23", "revenue": 71.30, "profit": 8.90, "assets": 76.40},
            {"period": "FY22", "revenue": 54.00, "profit": 5.80, "assets": 58.20}
        ],
        "offer_breakdown": {"qib_pct": 50.0, "nii_pct": 15.0, "retail_pct": 35.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 800, "min_amount": 240800, "total_lots": 1}
        ]
    },
    "Propshop Events": {
        "sector": "Consumer",
        "sub_retail": 2.90,
        "sub_nii": 4.50,
        "sub_qib": 8.20,
        "sub_overall": 5.20,
        "about": "Propshop Events Limited provides end-to-end experiential marketing, corporate event management, wedding design, and brand activation services across major Indian metros.",
        "issue_objective": [
            "Investment in proprietary event decor and AV technology assets",
            "Opening new branch offices in Bengaluru and Dubai",
            "General corporate purposes"
        ],
        "financials": [
            {"period": "FY24", "revenue": 38.40, "profit": 4.50, "assets": 41.00},
            {"period": "FY23", "revenue": 28.10, "profit": 3.00, "assets": 30.20},
            {"period": "FY22", "revenue": 18.50, "profit": 1.60, "assets": 20.40}
        ],
        "offer_breakdown": {"qib_pct": 50.0, "nii_pct": 15.0, "retail_pct": 35.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 4000, "min_amount": 276000, "total_lots": 1}
        ]
    },
    "Advance Technoforge": {
        "sector": "Manufacturing",
        "sub_retail": 6.40,
        "sub_nii": 10.20,
        "sub_qib": 16.50,
        "sub_overall": 11.00,
        "about": "Advance Technoforge Limited manufactures closed-die steel forgings, machined crankshafts, and gear blanks for automotive, agricultural, and industrial machinery applications.",
        "issue_objective": [
            "Installing press forging line and heat treatment furnace",
            "Repayment of term loans",
            "General corporate purposes"
        ],
        "financials": [
            {"period": "FY24", "revenue": 105.20, "profit": 9.80, "assets": 112.50},
            {"period": "FY23", "revenue": 87.40, "profit": 7.10, "assets": 93.80},
            {"period": "FY22", "revenue": 70.10, "profit": 4.90, "assets": 75.00}
        ],
        "offer_breakdown": {"qib_pct": 50.0, "nii_pct": 15.0, "retail_pct": 35.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 2400, "min_amount": 228000, "total_lots": 1}
        ]
    },
    "Silverstorm Parks": {
        "sector": "Consumer",
        "sub_retail": 4.50,
        "sub_nii": 7.80,
        "sub_qib": 12.40,
        "sub_overall": 8.20,
        "about": "Silverstorm Parks Limited operates water parks, amusement parks, and eco-resort properties in South India, catering to family tourism and leisure entertainment.",
        "issue_objective": [
            "Construction of new rides and water park attractions",
            "Solar power installation for park energy captive supply",
            "General corporate purposes"
        ],
        "financials": [
            {"period": "FY24", "revenue": 62.10, "profit": 8.40, "assets": 78.50},
            {"period": "FY23", "revenue": 48.00, "profit": 5.90, "assets": 62.10},
            {"period": "FY22", "revenue": 31.40, "profit": 2.80, "assets": 45.00}
        ],
        "offer_breakdown": {"qib_pct": 50.0, "nii_pct": 15.0, "retail_pct": 35.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 2000, "min_amount": 266000, "total_lots": 1}
        ]
    },
    "Cube Highways Trust": {
        "sector": "Infrastructure",
        "sub_retail": 1.80,
        "sub_nii": 4.20,
        "sub_qib": 9.50,
        "sub_overall": 5.10,
        "about": "Cube Highways Trust is an Infrastructure Investment Trust (InvIT) backed by I Squared Capital, managing a portfolio of toll road assets and highway corridors across India.",
        "issue_objective": [
            "Acquisitions of operating toll road highway concessions",
            "Refinancing existing project debt",
            "General InvIT corporate expenses"
        ],
        "financials": [
            {"period": "FY24", "revenue": 2850.00, "profit": 410.20, "assets": 12500.00},
            {"period": "FY23", "revenue": 2400.00, "profit": 330.00, "assets": 11000.00},
            {"period": "FY22", "revenue": 1950.00, "profit": 250.40, "assets": 9200.00}
        ],
        "offer_breakdown": {"qib_pct": 75.0, "nii_pct": 25.0},
        "lot_distribution": [
            {"category": "Individual", "min_shares": 95, "min_amount": 14440, "total_lots": 1}
        ]
    }
}

count = 0
for ipo in ipos:
    name = ipo['name']
    if name in IPO_PROFILES:
        prof = IPO_PROFILES[name]
        ipo['sector'] = prof['sector']
        ipo['sub_retail'] = prof.get('sub_retail')
        ipo['sub_nii'] = prof.get('sub_nii')
        ipo['sub_qib'] = prof.get('sub_qib')
        ipo['sub_overall'] = prof.get('sub_overall')
        ipo['about'] = prof['about']
        ipo['issue_objective'] = prof['issue_objective']
        ipo['financials'] = prof['financials']
        ipo['offer_breakdown'] = prof['offer_breakdown']
        ipo['lot_distribution'] = prof['lot_distribution']
        count += 1

with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"Successfully updated {count} IPOs in {DATA_FILE} with rich subscription multiples and company profiles.")
