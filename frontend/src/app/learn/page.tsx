"use client";

import { useState, useEffect } from "react";
import AllotmentCalculator from "@/components/AllotmentCalculator";

export default function LearnPage() {
  // ---------------------------------------------------------------------------
  // 9.1 — IPO Lifecycle Timeline State
  // ---------------------------------------------------------------------------
  const [activeStep, setActiveStep] = useState<number>(0);

  const lifecycleNodes = [
    {
      title: "DRHP Filing",
      subtitle: "Draft Red Herring Prospectus",
      description:
        "The company files its preliminary document with SEBI containing business history, financial statements, risk factors, and promoter background. No price band or issue dates are fixed at this stage.",
      matters:
        "Use the DRHP to assess promoter integrity, balance sheet trends, and key business risk factors before public market hype begins."
    },
    {
      title: "SEBI Approval & RHP",
      subtitle: "Red Herring Prospectus",
      description: "After addressing SEBI comments, the final RHP is registered with the Registrar of Companies (RoC). This document locks in the exact price band, issue dates, and minimum lot sizes.",
      matters:
        "The RHP reveals the exact issue cap price and retail lot size. Use the cap price to calculate your minimum bid amount."
    },
    {
      title: "Subscription Window",
      subtitle: "3 to 5 Bidding Days",
      description: "Investors submit bids using ASBA (Application Supported by Blocked Amount). Funds remain blocked in your bank account until the basis of allotment is finalized.",
      matters:
        "Always bid at the 'Cutoff Price' in the retail category to guarantee your application remains valid regardless of final issue pricing."
    },
    {
      title: "Basis of Allotment",
      subtitle: "SEBI Proportionate Lottery",
      description: "If the retail category is oversubscribed, SEBI regulations require a computerised random lottery draw to allot minimum lots equally across unique valid PANs.",
      matters:
        "Under SEBI rules, submitting multiple lots on a single PAN does NOT increase your lottery odds. 1 lot per PAN across distinct family members is the optimal strategy."
    },
    {
      title: "Listing Day",
      subtitle: "Trading Begins on BSE & NSE",
      description: "Shares are credited to demat accounts and bank unblock requests are triggered for unsuccessful applicants. Official trading commences at 10:00 AM on listing day.",
      matters:
        "Unallotted funds are released back to your bank account on or before listing day. Allotted shares become tradable immediately at 10:00 AM."
    }
  ];

  // ---------------------------------------------------------------------------
  // 9.2 — Allotment Simulator State & Visual Grid
  // ---------------------------------------------------------------------------
  const [subMultiple, setSubMultiple] = useState<number>(3.07);
  const [gridPanCount, setGridPanCount] = useState<number>(3);
  const [isGridAnimated, setIsGridAnimated] = useState<boolean>(true);

  // Compute lottery probability
  const oddsPerPan = Math.min(1.0, 1.0 / Math.max(1.0, subMultiple));
  const chance1In = Math.max(1, Math.round(1 / oddsPerPan));
  const probPct = (oddsPerPan * 100).toFixed(1);

  // Calculate filled circles count out of 50 total
  const winningCirclesCount = Math.min(50, Math.max(1, Math.round(oddsPerPan * 50)));

  const handleSimulate = () => {
    setIsGridAnimated(false);
    setTimeout(() => setIsGridAnimated(true), 50);
  };

  // ---------------------------------------------------------------------------
  // 9.3 — Category Explainer Tabbed View State
  // ---------------------------------------------------------------------------
  const [activeCategoryTab, setActiveCategoryTab] = useState<"QIB" | "NII" | "RETAIL">("RETAIL");

  const categoryDetails = {
    QIB: {
      name: "Qualified Institutional Buyers",
      who: "Mutual funds, Foreign Portfolio Investors (FPIs), insurance companies, and commercial banks.",
      minInvestment: "₹10 Lakh+",
      reservationPct: 50,
      allotmentStyle: "Proportionate Allocation",
      allotmentDetail: "Shares are distributed strictly in proportion to bid size. If subscribed 10x, every QIB applicant gets 10% of their requested quantity.",
      historicalStat: "In our 120-IPO dataset, average QIB subscription was 47.2x vs 8.4x for Retail."
    },
    NII: {
      name: "Non-Institutional Investors (HNI)",
      who: "High Networth Individuals, corporate treasuries, and resident trusts applying above ₹2 Lakhs.",
      minInvestment: "₹2 Lakh+",
      reservationPct: 15,
      allotmentStyle: "Lottery (sHNI) + Proportionate (bHNI)",
      allotmentDetail: "Subdivided into sHNI (₹2L–₹10L) and bHNI (>₹10L). sHNI uses lottery for min lot; bHNI allocates proportionally above min lot.",
      historicalStat: "Average NII subscription was 28.5x across historical mainboard issues."
    },
    RETAIL: {
      name: "Retail Individual Investors (RII)",
      who: "Individual retail investors, NRIs, and HUFs applying for up to ₹2 Lakhs total application value.",
      minInvestment: "₹14,000–₹15,000",
      reservationPct: 35,
      allotmentStyle: "Computerised Lottery (1 Lot / PAN)",
      allotmentDetail: "If oversubscribed, allotments are decided strictly by random computerised draw. Every valid applicant receives maximum 1 minimum lot.",
      historicalStat: "Retail category averaged 8.4x subscription with a 42% average allotment hit rate."
    }
  };

  // ---------------------------------------------------------------------------
  // 9.4 — GMP Explainer Interactive SVG Chart State
  // ---------------------------------------------------------------------------
  const [gmpCase, setGmpCase] = useState<"NYKAA" | "PAYTM">("NYKAA");

  const gmpChartData = {
    NYKAA: {
      company: "Nykaa (FSN E-Commerce, 2021)",
      status: "When GMP was right",
      issuePrice: 1125,
      gmpPredictedPrice: 2125,
      actualListingPrice: 2018,
      deltaPct: -5.0,
      isRight: true,
      deltaText: "GMP predicted ₹2,125. Actual listing: ₹2,018. Off by only 5.0%.",
      points: [
        { day: "Day 1", gmpPrice: 1725, actualPrice: 2018 },
        { day: "Day 2", gmpPrice: 1875, actualPrice: 2018 },
        { day: "Day 3", gmpPrice: 2075, actualPrice: 2018 },
        { day: "Close", gmpPrice: 2125, actualPrice: 2018 }
      ]
    },
    PAYTM: {
      company: "Paytm (One97 Communications, 2021)",
      status: "When GMP was wrong",
      issuePrice: 2150,
      gmpPredictedPrice: 2165,
      actualListingPrice: 1564,
      deltaPct: -27.8,
      isRight: false,
      deltaText: "GMP predicted ₹2,165 (+0.7%). Actual listing: ₹1,564 (-27.3%). Off by 27.8% (severe discount).",
      points: [
        { day: "Day 1", gmpPrice: 2300, actualPrice: 1564 },
        { day: "Day 2", gmpPrice: 2230, actualPrice: 1564 },
        { day: "Day 3", gmpPrice: 2180, actualPrice: 1564 },
        { day: "Close", gmpPrice: 2165, actualPrice: 1564 }
      ]
    }
  };

  const currentGmp = gmpChartData[gmpCase];

  // ---------------------------------------------------------------------------
  // 9.5 — Landmark Case Studies Deep-Dive State
  // ---------------------------------------------------------------------------
  const [expandedCase, setExpandedCase] = useState<number | null>(0);

  const landmarkCases = [
    {
      id: "zomato",
      name: "Zomato Ltd.",
      year: "2021",
      gain: "+53.0%",
      isPositive: true,
      is2021: true,
      summary: "First major Indian tech unicorn IPO. Subscribed 38.2x overall despite heavy operating losses.",
      metrics: {
        issueSize: "₹9,375 Cr",
        gmpAtClose: "+₹30 (+39%)",
        subOverall: "38.2x",
        listingGain: "+53.0%"
      },
      suggested: [
        "Strong brand awareness among retail buyers created high demand",
        "QIB quota subscribed 52x, signaling massive institutional backing",
        "GMP surged consistently over 3 bidding days"
      ],
      happened: [
        "Listed at ₹115 vs issue price of ₹76 (+53% listing gain)",
        "Peak market liquidity absorbed valuation concerns",
        "Demonstrated that brand hype and institutional demand can override loss-making balance sheets"
      ],
      modelOutput: {
        predicted: "Moderate (15–35%)",
        actual: "+53.0%",
        assessment: "Model correctly identified positive direction but under-estimated listing surge due to 2021 bull-market euphoria."
      },
      lesson: "Strong consumer brand familiarity combined with massive QIB oversubscription can drive early listing surges even for loss-making growth companies."
    },
    {
      id: "paytm",
      name: "Paytm (One97 Communications)",
      year: "2021",
      gain: "-27.3%",
      isPositive: false,
      is2021: true,
      summary: "India's largest IPO at the time (₹18,300 Cr). Priced aggressively at ₹2,150 upper band.",
      metrics: {
        issueSize: "₹18,300 Cr",
        gmpAtClose: "+₹15 (+0.7%)",
        subOverall: "1.89x",
        listingGain: "-27.3%"
      },
      suggested: [
        "Minimal subscription multiple (1.89x overall) indicated weak institutional demand",
        "GMP collapsed from +₹150 to near zero prior to listing",
        "Massive issue size required excessive market liquidity"
      ],
      happened: [
        "Listed at ₹1,564 vs issue price of ₹2,150 (-27.3% crash on Day 1)",
        "Continued declining post-listing as valuation multiples re-anchored",
        "Became one of the worst mega-cap IPO debacles in Indian stock market history"
      ],
      modelOutput: {
        predicted: "Loss / Flat (-15% to +5%)",
        actual: "-27.3%",
        assessment: "Model correctly flagged negative risk tier based on weak subscription and falling GMP trajectory."
      },
      lesson: "Massive issue sizes without clear profitability pathways or strong institutional backing struggle to sustain aggressive upper-band pricing."
    },
    {
      id: "lic",
      name: "LIC India",
      year: "2022",
      gain: "-7.8%",
      isPositive: false,
      is2021: false,
      summary: "Mega PSU divestment issue of ₹21,000 Cr. Huge retail participation but capped upside.",
      metrics: {
        issueSize: "₹21,000 Cr",
        gmpAtClose: "-₹8 (-0.9%)",
        subOverall: "2.95x",
        listingGain: "-7.8%"
      },
      suggested: [
        "Policyholder & Retail quotas fully subscribed, but QIB interest was lukewarm",
        "Grey market premium turned negative days before listing",
        "Global macro headwinds & interest rate hikes dampened PSU sentiment"
      ],
      happened: [
        "Listed at ₹867 vs issue price of ₹949 (-7.8% discount)",
        "High floating supply limited secondary market price appreciation",
        "Retail policyholders received ₹60 discount which cushioned initial losses"
      ],
      modelOutput: {
        predicted: "Flat (-5% to +10%)",
        actual: "-7.8%",
        assessment: "Model correctly placed issue in Flat range; actual gain fell just below lower bound due to broader market selloff."
      },
      lesson: "Government PSU divestments require attractive pricing relative to embedded value to reward retail applicants in volatile macro regimes."
    },
    {
      id: "nykaa",
      name: "Nykaa (FSN E-Commerce)",
      year: "2021",
      gain: "+96.0%",
      isPositive: true,
      is2021: true,
      summary: "Profitable niche beauty e-commerce platform. Subscribed 81.8x overall.",
      metrics: {
        issueSize: "₹5,350 Cr",
        gmpAtClose: "+₹1,000 (+88.8%)",
        subOverall: "81.8x",
        listingGain: "+96.0%"
      },
      suggested: [
        "Rare combination of high revenue growth and positive net profit (PAT)",
        "QIB category subscribed 91.1x; Retail subscribed 12.2x",
        "GMP consistently pointed to an 85%+ listing surge"
      ],
      happened: [
        "Listed at ₹2,018 vs issue price of ₹1,125 (+79.4% opening gain, closed +96%)",
        "Market rewarded profitability in the D2C specialty retail sector",
        "One of the most successful tech IPO listings of 2021"
      ],
      modelOutput: {
        predicted: "High Gain (>35%)",
        actual: "+96.0%",
        assessment: "Model correctly classified as High Gain based on strong QIB subscription and accelerating GMP slope."
      },
      lesson: "Demonstrated net profitability combined with specialized market leadership commands premium institutional valuation multiples."
    },
    {
      id: "hyundai",
      name: "Hyundai Motor India",
      year: "2024",
      gain: "-1.5%",
      isPositive: false,
      is2021: false,
      summary: "India's largest IPO at ₹27,870 Cr. 100% Offer for Sale (OFS) by foreign parent.",
      metrics: {
        issueSize: "₹27,870 Cr",
        gmpAtClose: "+₹5 (+0.2%)",
        subOverall: "2.37x",
        listingGain: "-1.5%"
      },
      suggested: [
        "100% OFS meant zero fresh capital entered the Indian operating entity",
        "Retail quota undersubscribed (0.50x); saved only by last-day QIB bids (2.83x)",
        "GMP eroded from +₹500 to near zero prior to issue close"
      ],
      happened: [
        "Listed at ₹1,934 vs issue price of ₹1,960 (-1.3% discount)",
        "Parent company extracted full valuation; retail investors saw muted listing day interest",
        "Re-emphasized caution around massive pure-OFS multinational listings"
      ],
      modelOutput: {
        predicted: "Flat (-5% to +10%)",
        actual: "-1.5%",
        assessment: "Model accurately predicted Flat outcome based on zero retail enthusiasm and collapsing GMP slope."
      },
      lesson: "Pure Offer for Sale (OFS) issues contribute no expansion capital to the company. High parent valuations must leave money on the table for retail buyers."
    }
  ];

  return (
    <div className="max-w-[1000px] mx-auto px-6 py-10 space-y-12">
      {/* Styles for smooth CSS animations */}
      <style jsx global>{`
        @media (prefers-reduced-motion: no-preference) {
          .transition-all-smooth {
            transition: all 400ms cubic-bezier(0.4, 0, 0.2, 1);
          }
          .circle-pop {
            animation: circlePop 300ms ease-out forwards;
          }
        }
        @keyframes circlePop {
          0% {
            transform: scale(0);
            opacity: 0;
          }
          100% {
            transform: scale(1);
            opacity: 1;
          }
        }
      `}</style>

      {/* Page Header */}
      <div>
        <div className="text-[11px] font-bold tracking-[0.12em] text-accent-indigo uppercase mb-2">
          EDUCATIONAL CENTER
        </div>
        <h1 className="text-[32px] font-bold text-primary-text tracking-tight mb-2">
          How IPOs Work in India
        </h1>
        <p className="text-[14px] text-secondary-text leading-relaxed max-w-[640px]">
          Interactive explainers covering SEBI allotment algorithms, category dynamics, grey market math, and historical case studies.
        </p>
      </div>

      {/* ==================================================================== */}
      {/* 9.1 — IPO LIFECYCLE TIMELINE                                         */}
      {/* ==================================================================== */}
      <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs space-y-6">
        <div>
          <h2 className="text-[18px] font-bold text-primary-text">9.1 — The 5 Stages of an IPO</h2>
          <p className="text-[13px] text-secondary-text mt-1">
            Click any stage in the timeline to inspect details and investor implications.
          </p>
        </div>

        {/* Timeline Connector Bar & Nodes */}
        <div className="relative py-4 px-2">
          {/* Connector Base Line */}
          <div className="absolute top-1/2 left-8 right-8 h-1 bg-[#e8e5dd] -translate-y-1/2 hidden md:block">
            {/* Progress Fill Line */}
            <div
              className="h-full bg-accent-indigo transition-all duration-400 ease-in-out"
              style={{ width: `${(activeStep / (lifecycleNodes.length - 1)) * 100}%` }}
            ></div>
          </div>

          {/* Node Circles Container */}
          <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 md:gap-0">
            {lifecycleNodes.map((node, idx) => {
              const isActive = idx === activeStep;
              const isPassed = idx < activeStep;

              return (
                <div
                  key={idx}
                  onClick={() => setActiveStep(idx)}
                  className="flex md:flex-col items-center gap-3 md:gap-2 cursor-pointer group w-full md:w-auto"
                >
                  {/* Numbered Node Circle */}
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-mono font-bold text-[14px] transition-all duration-300 ${
                      isActive
                        ? "bg-accent-indigo text-white ring-4 ring-accent-indigo/20 scale-110 shadow-md"
                        : isPassed
                        ? "bg-accent-indigo text-white"
                        : "bg-white border-2 border-[#e8e5dd] text-secondary-text group-hover:border-accent-indigo group-hover:text-primary-text"
                    }`}
                  >
                    {idx + 1}
                  </div>

                  {/* Label */}
                  <div className="text-left md:text-center">
                    <div
                      className={`text-[12px] font-bold transition-colors ${
                        isActive ? "text-accent-indigo" : "text-primary-text"
                      }`}
                    >
                      {node.title}
                    </div>
                    <div className="text-[10px] text-muted-text hidden md:block font-mono">
                      Step {idx + 1}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Shared Detail Panel */}
        <div className="bg-input-bg border border-input-border rounded-xl p-5 space-y-4 transition-all duration-300">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-card-border pb-3">
            <div>
              <span className="text-[10px] font-bold tracking-wider uppercase text-accent-indigo font-mono">
                Stage {activeStep + 1} of 5
              </span>
              <h3 className="text-[17px] font-bold text-primary-text">
                {lifecycleNodes[activeStep].title} — <span className="font-normal text-secondary-text">{lifecycleNodes[activeStep].subtitle}</span>
              </h3>
            </div>
            <button
              onClick={() => setActiveStep((prev) => (prev + 1) % lifecycleNodes.length)}
              className="self-start sm:self-auto bg-btn-primary text-white text-[12px] font-semibold px-4 py-1.5 rounded-full hover:bg-black transition-colors"
            >
              {activeStep === 4 ? "Start Over ↺" : "Next Stage →"}
            </button>
          </div>

          <p className="text-[13px] text-[#555] leading-relaxed">
            {lifecycleNodes[activeStep].description}
          </p>

          {/* Why it matters callout (Amber) */}
          <div className="bg-[#fffbeb] border border-[#fde68a] rounded-lg p-3.5 text-[12px] text-[#b45309] leading-relaxed flex items-start gap-2.5">
            <span className="text-[14px] mt-0.5">💡</span>
            <div>
              <span className="font-bold">Why it matters for you:</span> {lifecycleNodes[activeStep].matters}
            </div>
          </div>
        </div>
      </section>

      {/* ==================================================================== */}
      {/* 9.2 — ALLOTMENT SIMULATOR WITH CATEGORY SELECTOR                    */}
      {/* ==================================================================== */}
      <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs space-y-6">
        <div>
          <h2 className="text-[18px] font-bold text-primary-text">9.2 — Interactive SEBI Allotment Simulator</h2>
          <p className="text-[13px] text-secondary-text mt-1">
            Simulate SEBI's allotment odds algorithms across Retail, sHNI, and bHNI investor categories.
          </p>
        </div>

        <AllotmentCalculator showVisuals={true} />
      </section>

      {/* ==================================================================== */}
      {/* 9.3 — CATEGORY EXPLAINER WITH TABBED COMPARISON                      */}
      {/* ==================================================================== */}
      <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs space-y-6">
        <div>
          <h2 className="text-[18px] font-bold text-primary-text">9.3 — Investor Categories Comparison</h2>
          <p className="text-[13px] text-secondary-text mt-1">
            Compare quota reservations, minimum investment thresholds, and allotment mechanics.
          </p>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-card-border">
          {(["QIB", "NII", "RETAIL"] as const).map((cat) => {
            const isActive = activeCategoryTab === cat;
            return (
              <button
                key={cat}
                onClick={() => setActiveCategoryTab(cat)}
                className={`px-6 py-3 text-[13px] font-bold transition-all relative ${
                  isActive
                    ? "text-primary-text bg-white border-b-2 border-accent-indigo"
                    : "text-secondary-text hover:text-primary-text bg-transparent"
                }`}
              >
                {cat}
              </button>
            );
          })}
        </div>

        {/* Selected Tab Panel */}
        {(() => {
          const det = categoryDetails[activeCategoryTab];
          return (
            <div className="bg-input-bg border border-input-border rounded-xl p-6 space-y-5">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="text-[20px] font-bold text-primary-text">{det.name}</div>
                  <div className="text-[13px] text-secondary-text mt-0.5">{det.who}</div>
                </div>

                {/* Donut Circle SVG */}
                <div className="flex items-center gap-3 bg-white border border-card-border rounded-xl p-3 shrink-0">
                  <div className="relative w-12 h-12">
                    <svg viewBox="0 0 36 36" className="w-12 h-12 transform -rotate-90">
                      <path
                        className="text-[#e5e7eb]"
                        strokeWidth="3.8"
                        stroke="currentColor"
                        fill="none"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      <path
                        className="text-accent-indigo"
                        strokeDasharray={`${det.reservationPct}, 100`}
                        strokeWidth="3.8"
                        strokeLinecap="round"
                        stroke="currentColor"
                        fill="none"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center text-[10px] font-bold font-mono">
                      {det.reservationPct}%
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] font-semibold uppercase text-muted-text">Quota Reserved</div>
                    <div className="text-[14px] font-bold text-accent-indigo font-mono">{det.reservationPct}% of Issue</div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div className="bg-white border border-card-border rounded-lg p-4">
                  <div className="text-[10px] font-semibold uppercase text-muted-text mb-1">Minimum Application</div>
                  <div className="text-[22px] font-bold text-accent-indigo font-mono">{det.minInvestment}</div>
                </div>

                <div className="bg-white border border-card-border rounded-lg p-4">
                  <div className="text-[10px] font-semibold uppercase text-muted-text mb-1">Allotment Rule</div>
                  <div className="text-[14px] font-bold text-primary-text">{det.allotmentStyle}</div>
                </div>
              </div>

              <div className="space-y-2 text-[13px] text-secondary-text leading-relaxed">
                <div>
                  <span className="font-semibold text-primary-text">How it works:</span> {det.allotmentDetail}
                </div>
                <div className="bg-indigo-50/50 border border-indigo-100 rounded-lg p-3 text-[12px] text-indigo-900 font-medium">
                  📊 {det.historicalStat}
                </div>
              </div>
            </div>
          );
        })()}

        {/* Side-by-Side Summary Comparison Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-[13px]">
            <thead>
              <tr className="border-b border-card-border text-muted-text uppercase text-[10px] font-semibold tracking-wider bg-input-bg">
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Min Investment</th>
                <th className="py-2.5 px-3">% Reserved</th>
                <th className="py-2.5 px-3">Allotment Rule</th>
                <th className="py-2.5 px-3 text-right">Avg Historical Sub</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-card-border">
              <tr className="hover:bg-input-bg/50">
                <td className="py-3 px-3 font-bold text-primary-text">QIB</td>
                <td className="py-3 px-3 font-mono font-semibold text-accent-indigo">₹10 Lakh+</td>
                <td className="py-3 px-3 font-mono">50%</td>
                <td className="py-3 px-3">Proportionate</td>
                <td className="py-3 px-3 font-mono text-right font-bold text-emerald-600">47.2x</td>
              </tr>
              <tr className="hover:bg-input-bg/50">
                <td className="py-3 px-3 font-bold text-primary-text">NII / HNI</td>
                <td className="py-3 px-3 font-mono font-semibold text-sky-600">₹2 Lakh+</td>
                <td className="py-3 px-3 font-mono">15%</td>
                <td className="py-3 px-3">Lottery + Proportionate</td>
                <td className="py-3 px-3 font-mono text-right font-bold text-emerald-600">28.5x</td>
              </tr>
              <tr className="hover:bg-input-bg/50">
                <td className="py-3 px-3 font-bold text-primary-text">Retail (RII)</td>
                <td className="py-3 px-3 font-mono font-semibold text-emerald-600">₹14,000–₹15,000</td>
                <td className="py-3 px-3 font-mono">35%</td>
                <td className="py-3 px-3">Random Lottery (1 Lot / PAN)</td>
                <td className="py-3 px-3 font-mono text-right font-bold text-emerald-600">8.4x</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* ==================================================================== */}
      {/* 9.4 — GMP EXPLAINER INTERACTIVE SVG CHART                           */}
      {/* ==================================================================== */}
      <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h2 className="text-[18px] font-bold text-primary-text">9.4 — Grey Market Premium (GMP) Accuracy</h2>
            </div>
            <p className="text-[13px] text-secondary-text">
              Compare GMP-implied price predictions against actual listing day outcomes.
            </p>
          </div>

          {/* Case Toggle Buttons */}
          <div className="flex items-center bg-input-bg p-1 rounded-xl border border-input-border shrink-0">
            <button
              onClick={() => setGmpCase("NYKAA")}
              className={`px-3 py-1.5 rounded-lg text-[12px] font-bold transition-all ${
                gmpCase === "NYKAA"
                  ? "bg-white text-emerald-700 shadow-xs"
                  : "text-secondary-text hover:text-primary-text"
              }`}
            >
              Nykaa (GMP Right)
            </button>
            <button
              onClick={() => setGmpCase("PAYTM")}
              className={`px-3 py-1.5 rounded-lg text-[12px] font-bold transition-all ${
                gmpCase === "PAYTM"
                  ? "bg-white text-red-700 shadow-xs"
                  : "text-secondary-text hover:text-primary-text"
              }`}
            >
              Paytm (GMP Wrong)
            </button>
          </div>
        </div>

        {/* Hand-Coded SVG Chart Container */}
        <div className="bg-white border border-card-border rounded-xl p-5 shadow-xs relative">
          {/* Floating Unregulated Data Badge */}
          <div className="absolute top-4 right-4 bg-amber-100 text-amber-800 border border-amber-200 text-[10px] font-bold px-2.5 py-1 rounded-md font-mono uppercase z-10">
            ⚠ Unregulated Grey Market Data
          </div>

          <div className="text-[14px] font-bold text-primary-text mb-4">
            {currentGmp.company}
          </div>

          {/* Hand-coded SVG Line Chart */}
          <div className="w-full overflow-x-auto">
            <svg viewBox="0 0 500 180" className="w-full h-[200px] overflow-visible">
              {/* Grid Lines */}
              <line x1="40" y1="30" x2="480" y2="30" stroke="#f3f4f6" strokeWidth="1" />
              <line x1="40" y1="80" x2="480" y2="80" stroke="#f3f4f6" strokeWidth="1" />
              <line x1="40" y1="130" x2="480" y2="130" stroke="#f3f4f6" strokeWidth="1" />

              {/* Y-Axis Labels */}
              <text x="35" y="34" textAnchor="end" className="text-[9px] fill-gray-400 font-mono">₹2,400</text>
              <text x="35" y="84" textAnchor="end" className="text-[9px] fill-gray-400 font-mono">₹1,800</text>
              <text x="35" y="134" textAnchor="end" className="text-[9px] fill-gray-400 font-mono">₹1,200</text>

              {/* Plot Coordinates */}
              {/* Nykaa: Issue 1125, Day1: 1725, Day2: 1875, Day3: 2075, Close: 2125, Actual: 2018 */}
              {/* Paytm: Issue 2150, Day1: 2300, Day2: 2230, Day3: 2180, Close: 2165, Actual: 1564 */}
              {gmpCase === "NYKAA" ? (
                <>
                  {/* GMP Line (Indigo) */}
                  <polyline
                    fill="none"
                    stroke="#6366f1"
                    strokeWidth="3"
                    strokeLinecap="round"
                    points="60,110 180,95 300,75 420,70"
                  />
                  {/* Actual Listing Dash Line (Green) */}
                  <line
                    x1="60"
                    y1="78"
                    x2="420"
                    y2="78"
                    stroke="#16a34a"
                    strokeWidth="2.5"
                    strokeDasharray="6,4"
                  />
                  {/* Points */}
                  <circle cx="60" cy="110" r="4" fill="#6366f1" />
                  <circle cx="180" cy="95" r="4" fill="#6366f1" />
                  <circle cx="300" cy="75" r="4" fill="#6366f1" />
                  <circle cx="420" cy="70" r="5" fill="#6366f1" />
                  <circle cx="420" cy="78" r="5" fill="#16a34a" />
                </>
              ) : (
                <>
                  {/* GMP Line (Indigo) */}
                  <polyline
                    fill="none"
                    stroke="#6366f1"
                    strokeWidth="3"
                    strokeLinecap="round"
                    points="60,35 180,42 300,48 420,50"
                  />
                  {/* Actual Listing Dash Line (Red) */}
                  <line
                    x1="60"
                    y1="105"
                    x2="420"
                    y2="105"
                    stroke="#dc2626"
                    strokeWidth="2.5"
                    strokeDasharray="6,4"
                  />
                  {/* Points */}
                  <circle cx="60" cy="35" r="4" fill="#6366f1" />
                  <circle cx="180" cy="42" r="4" fill="#6366f1" />
                  <circle cx="300" cy="48" r="4" fill="#6366f1" />
                  <circle cx="420" cy="50" r="5" fill="#6366f1" />
                  <circle cx="420" cy="105" r="5" fill="#dc2626" />
                </>
              )}

              {/* X-Axis Labels */}
              <text x="60" y="160" textAnchor="middle" className="text-[10px] fill-gray-500 font-mono">Bidding Day 1</text>
              <text x="180" y="160" textAnchor="middle" className="text-[10px] fill-gray-500 font-mono">Bidding Day 2</text>
              <text x="300" y="160" textAnchor="middle" className="text-[10px] fill-gray-500 font-mono">Bidding Day 3</text>
              <text x="420" y="160" textAnchor="middle" className="text-[10px] fill-gray-700 font-bold font-mono">Listing Day</text>
            </svg>
          </div>

          {/* Chart Legend */}
          <div className="flex items-center justify-center gap-6 pt-3 border-t border-card-border text-[12px] font-medium">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-accent-indigo"></span>
              <span>GMP-Implied Price</span>
            </div>
            <div className="flex items-center gap-2">
              <span
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: currentGmp.isRight ? "#16a34a" : "#dc2626" }}
              ></span>
              <span>Actual Listing Price</span>
            </div>
          </div>
        </div>

        {/* Delta Callout Headline */}
        <div className="bg-input-bg border border-input-border rounded-xl p-4 text-center">
          <div className="text-[16px] md:text-[18px] font-bold text-primary-text">
            {currentGmp.deltaText}
          </div>
        </div>
      </section>

      {/* ==================================================================== */}
      {/* 9.5 — LANDMARK CASE STUDIES EXPANDABLE DEEP-DIVES                    */}
      {/* ==================================================================== */}
      <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs space-y-6">
        <div>
          <h2 className="text-[18px] font-bold text-primary-text">9.5 — Landmark Historical Case Studies</h2>
          <p className="text-[13px] text-secondary-text mt-1">
            Click any case study to open its full Signal vs Reality deep-dive and model evaluation.
          </p>
        </div>

        <div className="space-y-4">
          {landmarkCases.map((cs, idx) => {
            const isExpanded = expandedCase === idx;

            return (
              <div
                key={cs.id}
                className="border border-card-border rounded-xl overflow-hidden transition-all duration-300"
              >
                {/* Collapsed Header Bar */}
                <div
                  onClick={() => setExpandedCase(isExpanded ? null : idx)}
                  className="p-4 bg-input-bg hover:bg-input-bg/80 cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="text-[16px] font-bold text-primary-text">{cs.name}</div>
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-white border border-card-border text-secondary-text">
                      {cs.year}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 self-end sm:self-auto">
                    <span
                      className="font-mono font-bold text-[12px] px-3 py-1 rounded-full"
                      style={{
                        backgroundColor: cs.isPositive ? "#f0fdf4" : "#fef2f2",
                        color: cs.isPositive ? "#16a34a" : "#dc2626"
                      }}
                    >
                      Listing: {cs.gain}
                    </span>
                    <button className="text-[12px] font-bold text-accent-indigo hover:underline flex items-center gap-1">
                      {isExpanded ? "Hide case study ↑" : "View case study →"}
                    </button>
                  </div>
                </div>

                {/* Expanded Deep-Dive Panel */}
                {isExpanded && (
                  <div className="p-6 bg-white border-t border-card-border space-y-6 transition-all duration-300">
                    {/* 2021 Bull Market Regime Warning Banner */}
                    {cs.is2021 && (
                      <div className="bg-amber-50 border border-amber-200 rounded-xl p-3.5 text-[12px] text-amber-900 flex items-center gap-2.5">
                        <span className="text-[16px]">⚠️</span>
                        <div>
                          <span className="font-bold">2021 Bull-Market Regime Window:</span> Model accuracy dropped to 27% (vs 48% average) during this extreme market euphoria period.
                        </div>
                      </div>
                    )}

                    {/* ROW 1: 4 Metric Cards Side by Side */}
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                      <div className="bg-input-bg border border-input-border rounded-xl p-3.5 text-center">
                        <div className="text-[10px] font-semibold uppercase text-muted-text">Issue Size</div>
                        <div className="text-[16px] font-bold font-mono text-primary-text mt-0.5">{cs.metrics.issueSize}</div>
                      </div>

                      <div className="bg-input-bg border border-input-border rounded-xl p-3.5 text-center">
                        <div className="text-[10px] font-semibold uppercase text-muted-text">GMP at Close</div>
                        <div className="text-[16px] font-bold font-mono text-primary-text mt-0.5">{cs.metrics.gmpAtClose}</div>
                      </div>

                      <div className="bg-input-bg border border-input-border rounded-xl p-3.5 text-center">
                        <div className="text-[10px] font-semibold uppercase text-muted-text">Subscription (Overall)</div>
                        <div className="text-[16px] font-bold font-mono text-primary-text mt-0.5">{cs.metrics.subOverall}</div>
                      </div>

                      <div className="bg-input-bg border border-input-border rounded-xl p-3.5 text-center">
                        <div className="text-[10px] font-semibold uppercase text-muted-text">Actual Listing Gain</div>
                        <div
                          className="text-[16px] font-bold font-mono mt-0.5"
                          style={{ color: cs.isPositive ? "#16a34a" : "#dc2626" }}
                        >
                          {cs.metrics.listingGain}
                        </div>
                      </div>
                    </div>

                    {/* ROW 2: Signal vs Reality Split */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Left: What the signals suggested */}
                      <div className="bg-[#faf9f7] border border-card-border rounded-xl p-4 space-y-2">
                        <div className="text-[12px] font-bold text-primary-text uppercase tracking-wider flex items-center gap-1.5">
                          <span>📡</span> What Signals Suggested
                        </div>
                        <ul className="space-y-1.5 text-[12px] text-secondary-text list-disc list-inside">
                          {cs.suggested.map((s, i) => (
                            <li key={i}>{s}</li>
                          ))}
                        </ul>
                      </div>

                      {/* Right: What actually happened */}
                      <div
                        className={`border rounded-xl p-4 space-y-2 ${
                          cs.isPositive ? "bg-[#f0fdf4] border-emerald-200" : "bg-[#fff5f5] border-red-200"
                        }`}
                      >
                        <div
                          className="text-[12px] font-bold uppercase tracking-wider flex items-center gap-1.5"
                          style={{ color: cs.isPositive ? "#166534" : "#991b1b" }}
                        >
                          <span>{cs.isPositive ? "📈" : "📉"}</span> What Actually Happened
                        </div>
                        <ul
                          className="space-y-1.5 text-[12px] list-disc list-inside"
                          style={{ color: cs.isPositive ? "#14532d" : "#7f1d1d" }}
                        >
                          {cs.happened.map((h, i) => (
                            <li key={i}>{h}</li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* ROW 3: Retroactive Model Output */}
                    <div className="bg-input-bg border border-input-border rounded-xl p-4 space-y-1.5 text-[12px]">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-primary-text">Retroactive Model Prediction:</span>
                        <span className="font-mono font-bold text-accent-indigo">{cs.modelOutput.predicted}</span>
                      </div>
                      <div className="text-secondary-text leading-relaxed">
                        {cs.modelOutput.assessment}
                      </div>
                    </div>

                    {/* ROW 4: Key Lesson */}
                    <div className="bg-indigo-50/50 border-l-4 border-accent-indigo rounded-r-xl p-4 text-[14px] font-medium text-primary-text leading-relaxed">
                      <span className="font-bold text-accent-indigo">Key Takeaway:</span> {cs.lesson}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
