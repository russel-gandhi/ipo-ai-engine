"use client";

import { useState } from "react";
import { calculateAllotment } from "@/lib/api";

export default function LearnPage() {
  // Allotment Simulator state
  const [subRetail, setSubRetail] = useState<number>(3.07);
  const [pans, setPans] = useState<number>(1);
  const [simResult, setSimResult] = useState<any>(null);
  const [simLoading, setSimLoading] = useState<boolean>(false);

  // Accordion state for 9.1 Lifecycle
  const [openStep, setOpenStep] = useState<number | null>(0);

  const runSimulation = async (pCount: number, sRetail: number) => {
    setSimLoading(true);
    try {
      const res = await calculateAllotment({
        sub_retail: sRetail,
        retail_quota_pct: 0.35,
        issue_size_cr: 500,
        lot_size: 100,
        cutoff_price: 100,
        applied_lots_per_pan: 1,
        num_pans: pCount
      });
      setSimResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setSimLoading(false);
    }
  };

  const lifecycleSteps = [
    {
      title: "1. DRHP Filing",
      subtitle: "Draft Red Herring Prospectus",
      description: "The company files its preliminary document with SEBI containing business details, financial statements, risks, and promoter history. No price band or dates are fixed yet."
    },
    {
      title: "2. SEBI Approval & RHP",
      subtitle: "Red Herring Prospectus",
      description: "After SEBI observations are addressed, the final RHP is filed with the Registrar of Companies (RoC), specifying issue dates and price band."
    },
    {
      title: "3. Subscription Window",
      subtitle: "3 to 5 Bidding Days",
      description: "Investors place bids via ASBA (Application Supported by Blocked Amount). Funds remain blocked in your bank account until allotment."
    },
    {
      title: "4. Basis of Allotment",
      subtitle: "SEBI Proportionate Lottery",
      description: "If oversubscribed in Retail category, lots are allotted via computerised random draw so every valid applicant has equal odds per PAN."
    },
    {
      title: "5. Listing Day",
      subtitle: "Trading Begins on BSE / NSE",
      description: "Shares are credited to demat accounts and unblock requests sent to banks. Trading commences at 10:00 AM on listing date."
    }
  ];

  const caseStudies = [
    {
      name: "Zomato Ltd. (2021)",
      year: "2021",
      listingGain: "+53%",
      summary: "First major Indian tech unicorn IPO. Oversubscribed 38x. High retail enthusiasm drove strong listing gains.",
      lesson: "Strong brand visibility and market momentum can drive early listing gains despite loss-making balance sheets."
    },
    {
      name: "Paytm (One97 Communications, 2021)",
      year: "2021",
      listingGain: "-27%",
      summary: "Largest IPO at ₹18,300 Cr. Priced aggressively at upper band of ₹2,150. Listed at severe discount.",
      lesson: "Massive issue sizes without path to profitability struggle to sustain premium valuations on listing day."
    },
    {
      name: "LIC India (2022)",
      year: "2022",
      listingGain: "-8%",
      summary: "Mega issue of ₹21,000 Cr. Huge retail participant base but macro headwinds and high float capped upside.",
      lesson: "Government PSU divestments require reasonable pricing relative to embedded value to reward retail applicants."
    },
    {
      name: "Nykaa (FSN E-Commerce, 2021)",
      year: "2021",
      listingGain: "+96%",
      summary: "Profitable niche e-commerce player. Subscribed 82x. Doubled on listing day.",
      lesson: "Demonstrated profitability alongside high growth commands premium institutional demand."
    },
    {
      name: "Hyundai Motor India (2024)",
      year: "2024",
      listingGain: "-1.5%",
      summary: "India's largest IPO at ₹27,870 Cr. 100% Offer for Sale. Subscribed 2.3x overall.",
      lesson: "Entirely OFS issues create no fresh capital for company growth, making valuation multiples critical."
    }
  ];

  return (
    <div className="max-w-[1000px] mx-auto px-6 py-10 space-y-12">
      {/* Header */}
      <div>
        <div className="text-[11px] font-bold tracking-[0.12em] text-accent-indigo uppercase mb-2">
          EDUCATIONAL CENTER
        </div>
        <h1 className="text-[32px] font-bold text-primary-text tracking-tight mb-2">
          How IPOs Work in India
        </h1>
        <p className="text-[14px] text-secondary-text leading-relaxed max-w-[640px]">
          Learn SEBI allotment rules, category dynamics, grey market math, and landmark historical case studies.
        </p>
      </div>

      {/* SECTION 9.1: IPO Lifecycle */}
      <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs">
        <h2 className="text-[18px] font-bold text-primary-text mb-4">9.1 — The 5 Stages of an IPO</h2>
        <div className="space-y-3">
          {lifecycleSteps.map((step, idx) => (
            <div
              key={idx}
              className="border border-card-border rounded-xl overflow-hidden transition-colors"
            >
              <button
                onClick={() => setOpenStep(openStep === idx ? null : idx)}
                className="w-full text-left p-4 bg-input-bg flex items-center justify-between font-semibold text-[14px] text-primary-text hover:bg-input-bg/80"
              >
                <span>{step.title} <span className="text-[12px] text-secondary-text font-normal ml-2">({step.subtitle})</span></span>
                <span className="text-[16px] text-muted-text">{openStep === idx ? "−" : "+"}</span>
              </button>
              {openStep === idx && (
                <div className="p-4 bg-white text-[13px] text-secondary-text leading-relaxed border-t border-card-border">
                  {step.description}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* SECTION 9.2: Interactive Allotment Simulator */}
      <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs space-y-6">
        <div>
          <h2 className="text-[18px] font-bold text-primary-text">9.2 — Interactive SEBI Allotment Simulator</h2>
          <p className="text-[13px] text-secondary-text mt-1">
            Simulate how SEBI's proportionate lottery algorithm awards shares when a retail category is oversubscribed.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
          <div className="bg-input-bg border border-input-border rounded-xl p-5 space-y-4">
            <div>
              <label className="block text-[11px] font-semibold uppercase text-muted-text tracking-wider mb-2">
                Retail Subscription Multiple
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  step="0.1"
                  min="1"
                  value={subRetail}
                  onChange={(e) => setSubRetail(parseFloat(e.target.value) || 1)}
                  className="w-full bg-white border border-input-border rounded-lg px-3 py-2 text-[14px] font-semibold text-primary-text outline-none focus:border-accent-indigo"
                />
                <span className="text-[14px] font-mono text-muted-text">x</span>
              </div>
              <p className="text-[11px] text-secondary-text mt-1">
                Example: 3.07x means 3.07 valid applications per available retail lot.
              </p>
            </div>

            <div>
              <label className="block text-[11px] font-semibold uppercase text-muted-text tracking-wider mb-2">
                Number of Family PANs
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={pans}
                onChange={(e) => setPans(Math.max(1, parseInt(e.target.value) || 1))}
                className="w-full bg-white border border-input-border rounded-lg px-3 py-2 text-[14px] font-semibold text-primary-text outline-none focus:border-accent-indigo"
              />
            </div>

            <button
              onClick={() => runSimulation(pans, subRetail)}
              className="w-full bg-btn-primary text-white text-[13px] font-semibold py-2.5 rounded-lg hover:bg-black transition-colors"
            >
              {simLoading ? "Running Simulation..." : "Calculate Odds"}
            </button>
          </div>

          <div className="bg-white border border-card-border rounded-xl p-5 shadow-xs space-y-3 text-[13px]">
            <div className="text-[11px] font-semibold text-muted-text uppercase tracking-wider mb-1">
              Simulation Result
            </div>
            {simResult ? (
              <>
                <div className="text-[28px] font-bold text-accent-indigo font-mono">
                  {(simResult.probability_at_least_one_lot * 100).toFixed(1)}%
                </div>
                <div className="text-[12px] text-secondary-text border-t border-card-border pt-3 space-y-1.5">
                  <div className="flex justify-between">
                    <span>Odds per PAN:</span>
                    <span className="font-mono font-medium">{(simResult.odds_per_pan * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Expected Lots:</span>
                    <span className="font-mono font-medium">{simResult.expected_lots}</span>
                  </div>
                </div>
                <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-[11px] text-emerald-800 leading-relaxed">
                  <span className="font-semibold">Key takeaway:</span> Under SEBI's rule, 1 lot application per PAN across {pans} family members gives you {pans} independent raffle tickets.
                </div>
              </>
            ) : (
              <div className="py-8 text-center text-muted-text">
                Click "Calculate Odds" to run simulation.
              </div>
            )}
          </div>
        </div>
      </section>

      {/* SECTION 9.3: Category Explainer */}
      <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs">
        <h2 className="text-[18px] font-bold text-primary-text mb-4">9.3 — Investor Categories Explained</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-input-bg border border-input-border rounded-xl p-5">
            <div className="text-[12px] font-bold text-accent-indigo uppercase tracking-wider mb-1">QIB</div>
            <h3 className="text-[15px] font-bold text-primary-text mb-2">Qualified Institutional Buyers</h3>
            <p className="text-[12px] text-secondary-text leading-relaxed">
              Mutual funds, foreign portfolio investors (FPIs), banks, and insurance companies. Minimum 50% reservation in standard issues.
            </p>
          </div>

          <div className="bg-input-bg border border-input-border rounded-xl p-5">
            <div className="text-[12px] font-bold text-sky-600 uppercase tracking-wider mb-1">NII / HNI</div>
            <h3 className="text-[15px] font-bold text-primary-text mb-2">Non-Institutional Investors</h3>
            <p className="text-[12px] text-secondary-text leading-relaxed">
              High networth individuals and corporates applying above ₹2 Lakhs. Subdivided into sHNI (₹2L–₹10L) and bHNI (above ₹10L).
            </p>
          </div>

          <div className="bg-input-bg border border-input-border rounded-xl p-5">
            <div className="text-[12px] font-bold text-emerald-600 uppercase tracking-wider mb-1">Retail</div>
            <h3 className="text-[15px] font-bold text-primary-text mb-2">Retail Individual Investors</h3>
            <p className="text-[12px] text-secondary-text leading-relaxed">
              Individual investors applying for lots up to ₹2 Lakhs total application value.
            </p>
          </div>
        </div>
      </section>

      {/* SECTION 9.4: GMP Explainer */}
      <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs space-y-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-[18px] font-bold text-primary-text">9.4 — Understanding Grey Market Premium (GMP)</h2>
            <span className="bg-amber-100 text-amber-800 border border-amber-200 text-[10px] font-semibold px-2 py-0.5 rounded uppercase font-mono">
              Unregulated Data
            </span>
          </div>
          <p className="text-[13px] text-secondary-text leading-relaxed">
            GMP represents unofficial forward trades executed in informal grey markets prior to listing. It is not regulated by SEBI or stock exchanges.
          </p>
        </div>

        <div className="bg-input-bg border border-input-border rounded-xl p-6 text-center space-y-3">
          <div className="text-[13px] font-semibold text-primary-text">GMP Calculation Formula</div>
          <div className="text-[20px] font-bold font-mono text-accent-indigo bg-white border border-card-border rounded-lg p-3 max-w-[480px] mx-auto">
            Expected Listing Price = Issue Price + GMP
          </div>
          <p className="text-[12px] text-secondary-text max-w-[540px] mx-auto leading-relaxed">
            Example: If an IPO is priced at ₹100 and has a GMP of ₹30, the unofficial expected listing price is ₹130 (+30% gain).
          </p>
        </div>
      </section>

      {/* SECTION 9.5: Landmark Case Studies */}
      <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs space-y-6">
        <div>
          <h2 className="text-[18px] font-bold text-primary-text">9.5 — Landmark Historical Case Studies</h2>
          <p className="text-[13px] text-secondary-text mt-1">
            Key takeaways from major Indian IPO listings.
          </p>
        </div>

        {/* 2021 Bubble Accuracy Warning Callout */}
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-[12px] text-amber-900 leading-relaxed flex items-start gap-3">
          <span className="text-[18px]">💡</span>
          <div>
            <span className="font-bold">Model Accuracy Note:</span> Our walk-forward validation shows model accuracy was lowest during the 2021 IPO boom (<span className="font-bold text-amber-700">27%</span> vs <span className="font-bold text-emerald-700">48%</span> overall average). Extreme market euphoria distorts historical pattern matching.
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {caseStudies.map((cs, i) => (
            <div key={i} className="bg-input-bg border border-input-border rounded-xl p-5 space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-[15px] font-bold text-primary-text">{cs.name}</h3>
                <span
                  className="font-mono font-bold text-[13px] px-2.5 py-0.5 rounded-full"
                  style={{
                    backgroundColor: cs.listingGain.startsWith("+") ? "#f0fdf4" : "#fef2f2",
                    color: cs.listingGain.startsWith("+") ? "#16a34a" : "#dc2626"
                  }}
                >
                  Listing: {cs.listingGain}
                </span>
              </div>
              <p className="text-[13px] text-primary-text leading-relaxed">{cs.summary}</p>
              <div className="text-[12px] font-medium text-accent-indigo pt-1">
                Key Lesson: {cs.lesson}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
