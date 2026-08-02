"use client";

import { useState, useEffect } from "react";
import { calculateAllotment } from "@/lib/api";

interface AllotmentCalculatorProps {
  ipo?: {
    name?: string;
    status?: string | null;
    is_sme?: boolean;
    exchange?: string | null;
    sub_retail?: number | null;
    sub_nii?: number | null;
    sub_qib?: number | null;
    price_band?: number | null;
    lot_size?: number | null;
    issue_size?: number | null;
    offer_breakdown?: {
      retail_pct?: number | null;
      nii_pct?: number | null;
      qib_pct?: number | null;
    } | null;
    lot_distribution?: Array<{
      category: string;
      min_shares?: number;
      min_amount?: number;
      total_lots?: number;
    }> | null;
    basis_of_allotment?: any;
  } | null;
  showVisuals?: boolean;
}

export default function AllotmentCalculator({ ipo }: AllotmentCalculatorProps) {
  const lotSize = ipo?.lot_size ?? 100;
  const priceBand = ipo?.price_band ?? 100;
  const minLotCost = lotSize * priceBand;

  // Primary Input: Planned Investment Amount (Default to 1 min lot or ₹15,000)
  const [plannedAmount, setPlannedAmount] = useState<number>(Math.max(15000, minLotCost));

  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Derived deterministic application metrics
  const appliedLots = Math.max(1, Math.floor(plannedAmount / minLotCost));
  const appliedShares = appliedLots * lotSize;
  const actualAmount = appliedShares * priceBand;

  const subRetail = ipo?.sub_retail ?? null;
  const subNii = ipo?.sub_nii ?? null;
  const subQib = ipo?.sub_qib ?? null;

  useEffect(() => {
    runSimulation();
  }, [plannedAmount, ipo]);

  const runSimulation = async () => {
    setLoading(true);
    setError(null);

    // Initial target category based on investment threshold for payload
    let targetCategory = "RETAIL";
    if (actualAmount > 1000000) {
      targetCategory = "bNII";
    } else if (actualAmount > 200000) {
      targetCategory = "sNII";
    }

    try {
      const payload: any = {
        category: targetCategory,
        applied_amount: actualAmount,
        applied_lots: appliedLots,
        lot_size: lotSize,
        cutoff_price: priceBand,
        sub_retail: subRetail,
        sub_nii: subNii,
        sub_qib: subQib,
        ipo_data: ipo
      };

      const res = await calculateAllotment(payload);
      setResult(res);
    } catch (e: any) {
      console.error("Error running application simulation:", e);
      setResult(null);
      setError("Unable to simulate application: backend service temporarily unavailable.");
    } finally {
      setLoading(false);
    }
  };

  // Convert raw allocation method enums to plain English descriptions
  const getHumanReadableFramework = (method?: string, regime?: string) => {
    if (!method) return "SEBI ICDR Allocation Framework";
    const m = method.toUpperCase();
    if (m.includes("MINIMUM_ALLOTMENT_THEN_LOTTERY") || m.includes("DRAW_OF_LOTS")) {
      return "Minimum allotment lot per successful applicant, allocated via computerised draw of lots if category is oversubscribed.";
    }
    if (m.includes("DRAW_OF_LOTS_FOR_MIN_LOT")) {
      return "Draw of lots to allot minimum sNII lot size to successful applicants; unallotted shares spillover to bNII.";
    }
    if (m.includes("MINIMUM_ALLOTMENT_THEN_PROPORTIONATE") || m.includes("PROPORTIONATE")) {
      return "Minimum lot size to successful applicants followed by proportionate allocation of residual shares based on shares bid.";
    }
    return method;
  };

  const getCategoryExplanation = (cat?: string) => {
    if (!cat) return "Standard investor allocation category.";
    const c = cat.toUpperCase();
    if (c.includes("RETAIL") || c.includes("INDIVIDUAL")) {
      return "Retail Individual Investor (RII): Applications up to ₹2,00,000. Governed by SEBI ICDR Schedule XIII.";
    }
    if (c.includes("SNII") || c.includes("SHNI")) {
      return "Small Non-Institutional Investor (sNII): Applications between ₹2,00,001 and ₹10,00,000 (1/3 of NII Quota).";
    }
    if (c.includes("BNII") || c.includes("BHNI")) {
      return "Big Non-Institutional Investor (bNII): Applications above ₹10,00,000 (2/3 of NII Quota).";
    }
    if (c.includes("QIB")) {
      return "Qualified Institutional Buyer (QIB): Institutional entities governed by SEBI Regulation 32.";
    }
    return "Applicable investor allocation category based on application size.";
  };

  return (
    <div className="bg-white border border-card-border rounded-xl p-6 shadow-xs space-y-6">
      {/* Title & Subtitle */}
      <div>
        <h3 className="text-[18px] font-bold text-slate-800 flex items-center gap-2">
          <span>⚡</span>
          <span>IPO Application Simulator</span>
        </h3>
        <p className="text-[12px] text-secondary-text mt-1 leading-relaxed">
          Enter your planned investment to understand your investor category, application size, current demand and applicable allotment mechanism.
        </p>
      </div>

      {/* SECTION 1: PRIMARY INPUT */}
      <div className="bg-input-bg border border-input-border rounded-xl p-5 space-y-3">
        <label className="block text-[11px] font-semibold uppercase text-muted-text tracking-wider">
          How much are you planning to invest?
        </label>
        <div className="relative flex items-center">
          <span className="absolute left-4 text-[18px] font-bold text-slate-400 font-mono">₹</span>
          <input
            type="number"
            min={minLotCost}
            step={minLotCost}
            value={plannedAmount}
            onChange={(e) => setPlannedAmount(Math.max(1, parseInt(e.target.value) || 1))}
            className="w-full bg-white border border-input-border rounded-lg pl-9 pr-4 py-3 text-[18px] font-bold text-primary-text outline-none focus:border-accent-indigo font-mono shadow-xs"
          />
        </div>
        <div className="flex items-center justify-between text-[11px] text-secondary-text font-mono">
          <span>Market Lot Cost: ₹{minLotCost.toLocaleString("en-IN")} ({lotSize} shares @ ₹{priceBand})</span>
          <span>Calculated Lots: {appliedLots} lot{appliedLots > 1 ? "s" : ""}</span>
        </div>
      </div>

      {/* SECTION 2 & 3: AUTOMATIC CATEGORY CLASSIFICATION & APPLICATION SUMMARY */}
      {result && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* YOUR APPLICATION SUMMARY CARD */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-text">
              Your Application Details
            </div>
            <div className="space-y-2 text-[12px]">
              <div className="flex justify-between items-baseline">
                <span className="text-secondary-text">Actual Application Amount:</span>
                <span className="font-mono font-bold text-slate-800 text-[15px]">
                  ₹{actualAmount.toLocaleString("en-IN")}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-secondary-text">Lots Applied:</span>
                <span className="font-mono font-semibold text-slate-700">{appliedLots} lot{appliedLots > 1 ? "s" : ""}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-secondary-text">Shares Applied:</span>
                <span className="font-mono font-semibold text-slate-700">{appliedShares.toLocaleString("en-IN")} shares</span>
              </div>
              <div className="flex justify-between">
                <span className="text-secondary-text">Price Used (Upper Band):</span>
                <span className="font-mono font-semibold text-slate-700">₹{priceBand}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-secondary-text">Market Lot Size:</span>
                <span className="font-mono font-semibold text-slate-700">{lotSize} shares</span>
              </div>
            </div>
          </div>

          {/* YOUR INVESTOR CATEGORY CARD */}
          <div className="bg-indigo-50/60 border border-indigo-100 rounded-xl p-4 space-y-3 flex flex-col justify-between">
            <div>
              <div className="text-[11px] font-semibold uppercase tracking-wider text-indigo-900 mb-1">
                Your Investor Category
              </div>
              <div className="text-[22px] font-bold text-accent-indigo font-mono">
                {result.category}
              </div>
              <p className="text-[11px] text-indigo-950 mt-2 leading-relaxed">
                {getCategoryExplanation(result.category)}
              </p>
            </div>

            <div className="pt-2 border-t border-indigo-100 text-[10px] font-mono text-indigo-800">
              Resolved Regime: {result.allotment_regime || "SEBI ICDR Framework"}
            </div>
          </div>
        </div>
      )}

      {/* SECTION 4: CURRENT DEMAND (Factual Subscription) */}
      <div className="bg-white border border-card-border rounded-xl p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-text flex items-center gap-1.5">
            <span>📊</span>
            <span>Current Share Subscription</span>
          </div>
          <span className="text-[10px] font-mono text-slate-500">Demand Metric Only</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-[12px]">
          {subRetail != null && (
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
              <div className="text-[10px] text-slate-500 uppercase font-semibold">Retail Demand</div>
              <div className="text-[16px] font-bold text-slate-800 font-mono mt-0.5">{subRetail}x</div>
            </div>
          )}
          {subNii != null && (
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
              <div className="text-[10px] text-slate-500 uppercase font-semibold">NII / HNI Demand</div>
              <div className="text-[16px] font-bold text-slate-800 font-mono mt-0.5">{subNii}x</div>
            </div>
          )}
          {subQib != null && (
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
              <div className="text-[10px] text-slate-500 uppercase font-semibold">QIB Demand</div>
              <div className="text-[16px] font-bold text-slate-800 font-mono mt-0.5">{subQib}x</div>
            </div>
          )}
        </div>

        <p className="text-[11px] text-slate-500 leading-relaxed bg-slate-50 p-2.5 rounded border border-slate-200">
          Share subscription measures total shares bid relative to total shares available. It is a market demand metric and is not converted into allotment probability.
        </p>
      </div>

      {/* SECTION 5: ALLOTMENT MECHANISM */}
      {result && (
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-700">
            Applicable Allotment Framework
          </div>

          <div className="space-y-2 text-[12px]">
            <div className="flex justify-between">
              <span className="text-secondary-text">Target Category:</span>
              <span className="font-bold text-slate-800">{result.category}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-secondary-text">Board Type:</span>
              <span className="font-semibold text-slate-700">{result.audit_trace?.board_type || "Mainboard"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-secondary-text">Regulatory Regime:</span>
              <span className="font-semibold text-slate-700">{result.audit_trace?.regime_id || result.allotment_regime}</span>
            </div>
          </div>

          <div className="bg-white p-3 rounded-lg border border-slate-200 text-[12px] text-slate-700 leading-relaxed">
            <span className="font-semibold text-slate-900">Allotment Method: </span>
            {getHumanReadableFramework(result.audit_trace?.allocation_method, result.allotment_regime)}
          </div>
        </div>
      )}

      {/* SECTION 6: ALLOTMENT PROBABILITY (CONTROLLED & INFORMATIONAL) */}
      {result && (
        <div className="bg-white border border-card-border rounded-xl p-4 space-y-2">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-text">
            Allotment Probability Analysis
          </div>

          {result.calculation_status === "EXACT" ? (
            <div className="flex items-baseline justify-between pt-1">
              <span className="text-[13px] font-medium text-slate-700">Calculated Allotment Probability:</span>
              <span className="text-[24px] font-bold text-accent-indigo font-mono">
                {result.probability_pct}%
              </span>
            </div>
          ) : result.calculation_status === "FINAL_BASIS_OF_ALLOTMENT" ? (
            <div className="flex items-baseline justify-between pt-1">
              <span className="text-[13px] font-medium text-slate-700">Official Basis of Allotment Ratio:</span>
              <span className="text-[24px] font-bold text-emerald-600 font-mono">
                {result.probability_pct}%
              </span>
            </div>
          ) : (
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-[11px] text-slate-600 leading-relaxed space-y-1">
              <div className="font-semibold text-slate-800">Exact Allotment Probability Currently Unavailable</div>
              <div>
                Exact allotment probability is not currently available because valid application-level competition data has not yet been published by the registrar.
              </div>
            </div>
          )}
        </div>
      )}

      {/* SECTION 8: EXPANDABLE METHODOLOGY DRAWER */}
      {result?.audit_trace && (
        <details className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-[12px] space-y-3 group">
          <summary className="font-semibold text-slate-800 cursor-pointer flex items-center justify-between select-none">
            <span className="flex items-center gap-2">
              <span>📜</span>
              <span>Calculation Methodology & SEBI Regulations</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full font-mono font-bold bg-slate-200 text-slate-700">
                {result.audit_trace.rule_id}
              </span>
            </span>
            <span className="text-slate-400 group-open:rotate-180 transition-transform">▼</span>
          </summary>

          <div className="pt-3 border-t border-slate-200 space-y-3 font-mono text-[11px]">
            <div>
              <span className="text-slate-500 font-sans font-semibold block">Regulatory Reference:</span>
              <a
                href={result.audit_trace.source_url}
                target="_blank"
                rel="noreferrer"
                className="text-accent-indigo underline hover:text-indigo-800 font-sans"
              >
                {result.audit_trace.regulation_reference}
              </a>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 bg-white p-3 rounded-lg border border-slate-200 text-[10px]">
              <div>
                <span className="text-slate-400 block">Regime ID:</span>
                <span className="font-bold text-slate-700">{result.audit_trace.regime_id}</span>
              </div>
              <div>
                <span className="text-slate-400 block">Board Type:</span>
                <span className="font-bold text-slate-700">{result.audit_trace.board_type}</span>
              </div>
              <div>
                <span className="text-slate-400 block">Allocation Method:</span>
                <span className="font-bold text-slate-700">{result.audit_trace.allocation_method}</span>
              </div>
            </div>

            <div>
              <span className="text-slate-500 font-sans font-semibold block">Calculation Steps:</span>
              <ul className="list-disc pl-4 space-y-1 text-slate-700 font-sans">
                {result.audit_trace.calculation_steps.map((step: string, idx: number) => (
                  <li key={idx}>{step}</li>
                ))}
              </ul>
            </div>
          </div>
        </details>
      )}
    </div>
  );
}
