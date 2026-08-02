"use client";

import { useState, useEffect } from "react";
import { calculateAllotment } from "@/lib/api";
import Tooltip from "@/components/Tooltip";

interface AllotmentCalculatorProps {
  ipo?: {
    name?: string;
    status?: string | null;
    sub_retail?: number | null;
    sub_nii?: number | null;
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
  } | null;
  showVisuals?: boolean;
}

export default function AllotmentCalculator({ ipo, showVisuals = true }: AllotmentCalculatorProps) {
  const [categoryTab, setCategoryTab] = useState<"RETAIL" | "sHNI" | "bHNI">("RETAIL");

  // Inputs
  const [pans, setPans] = useState<number>(1);
  const [shniLots, setShniLots] = useState<number>(14);
  const [bhniLots, setBhniLots] = useState<number>(68);

  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Extract IPO data defaults
  const subRetail = ipo?.sub_retail ?? null;
  const subNii = ipo?.sub_nii ?? null;
  const lotSize = ipo?.lot_size ?? 100;
  const priceBand = ipo?.price_band ?? 100;

  // Determine minimum lots per category.
  // Priority: API result (min_allotment_lots) → lot_distribution total_lots → hardcoded SEBI defaults.
  const shniMinRow = ipo?.lot_distribution?.find((r) => r.category.toLowerCase().includes("shni"));
  const bhniMinRow = ipo?.lot_distribution?.find((r) => r.category.toLowerCase().includes("bhni"));

  // These are used as INPUT defaults before the API responds; after the API responds, we prefer result values.
  const defaultShniMinLots = shniMinRow?.total_lots || 14;
  const defaultBhniMinLots = bhniMinRow?.total_lots || 68;

  useEffect(() => {
    runCalculation();
  }, [categoryTab, pans, shniLots, bhniLots, ipo]);

  const runCalculation = async () => {
    // If subscription data is missing, we don't need to call the backend.
    // Display a friendly message instead.
    if ((categoryTab === "RETAIL" && !subRetail) || 
        ((categoryTab === "sHNI" || categoryTab === "bHNI") && !subNii)) {
      setResult(null);
      if (ipo?.status?.toLowerCase() === "upcoming") {
        setError("Allotment odds will be available once the IPO opens and subscription data is published.");
      } else {
        setError("Calculation unavailable: live subscription multiples are missing for this IPO.");
      }
      return;
    }

    setLoading(true);
    setError(null);
    try {
      let payload: any = {
        category: categoryTab,
        lot_size: lotSize,
        cutoff_price: priceBand,
        sub_retail: subRetail,
        sub_nii: subNii
      };

      if (categoryTab === "RETAIL") {
        payload.num_pans = pans;
        payload.sub_retail = subRetail;
      } else if (categoryTab === "sHNI") {
        payload.applied_lots = shniLots;
        payload.sub_nii = subNii;
        // Send IPO-specific threshold so backend doesn't use the hardcoded SEBI default
        if (shniMinRow?.total_lots) payload.min_shni_lots = shniMinRow.total_lots;
      } else if (categoryTab === "bHNI") {
        payload.applied_lots = bhniLots;
        payload.sub_nii = subNii;
        if (bhniMinRow?.total_lots) payload.min_bhni_lots = bhniMinRow.total_lots;
      }

      const res = await calculateAllotment(payload);
      setResult(res);
    } catch (e: any) {
      console.error("Error running allotment calculation:", e);
      setResult(null);
      setError(e.response?.data?.detail || "Calculation unavailable: subscription data is missing or invalid.");
    } finally {
      setLoading(false);
    }
  };

  // Educational note per category
  const getEduNote = () => {
    if (categoryTab === "RETAIL") {
      return "Best strategy: apply through as many family PANs as possible. Each is an independent lottery ticket for 1 lot.";
    }
    if (categoryTab === "sHNI") {
      return "Best strategy: apply for the minimum sHNI lot size. Applying for more lots does not improve your lottery odds within the sHNI pool.";
    }
    return "More capital = more allotment. Unlike retail, this is proportionate — applying for more lots directly increases how much you receive.";
  };

  // Callout text per category
  const getCallout = () => {
    if (categoryTab === "RETAIL") {
      return "Each PAN is an independent lottery entry for exactly 1 lot. Max 1 lot per PAN regardless of how many lots you apply for.";
    }
    if (categoryTab === "sHNI") {
      return "sHNI allotment works differently from retail — you're applying for a larger minimum lot size, and the lottery is within the sHNI pool only.";
    }
    return "bHNI uses proportionate allotment, not a lottery. You get a fraction of what you applied for, proportional to how oversubscribed the category is.";
  };

  return (
    <div className="space-y-6">
      {/* Category Segmented Control Tabs */}
      <div className="flex border-b border-card-border bg-input-bg rounded-t-xl p-1">
        {(["RETAIL", "sHNI", "bHNI"] as const).map((cat) => {
          const isActive = categoryTab === cat;
          return (
            <button
              key={cat}
              onClick={() => setCategoryTab(cat)}
              className={`flex-1 py-2.5 text-[13px] font-bold transition-all rounded-lg ${
                isActive
                  ? "bg-white text-primary-text border-b-2 border-accent-indigo shadow-xs"
                  : "text-secondary-text hover:text-primary-text bg-transparent"
              }`}
            >
              {cat}
            </button>
          );
        })}
      </div>

      {/* Main Grid: Controls + Result Panel */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
        {/* LEFT COLUMN: Input Controls */}
        <div className="bg-input-bg border border-input-border rounded-xl p-5 space-y-4">
          {categoryTab === "RETAIL" && (
            <div>
              <label className="block text-[11px] font-semibold uppercase text-muted-text tracking-wider mb-2">
                Number of Family PAN Applications
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={pans}
                  onChange={(e) => setPans(Math.max(1, parseInt(e.target.value) || 1))}
                  className="w-full bg-white border border-input-border rounded-lg px-3 py-2 text-[14px] font-semibold text-primary-text outline-none focus:border-accent-indigo font-mono"
                />
              </div>
              <p className="text-[11px] text-secondary-text mt-1.5">
                Each family member's PAN counts as 1 separate lottery ticket.
              </p>
            </div>
          )}

          {categoryTab === "sHNI" && (
            <div>
              <label className="block text-[11px] font-semibold uppercase text-muted-text tracking-wider mb-2 flex items-center">
                Number of Lots Applying For (sHNI)
                <Tooltip content="sHNI minimum application threshold is ₹2 Lakhs." />
              </label>
              <input
                type="number"
                min={defaultShniMinLots}
                value={shniLots}
                onChange={(e) => setShniLots(Math.max(defaultShniMinLots, parseInt(e.target.value) || defaultShniMinLots))}
                className="w-full bg-white border border-input-border rounded-lg px-3 py-2 text-[14px] font-semibold text-primary-text outline-none focus:border-accent-indigo font-mono"
              />
              <p className="text-[11px] text-secondary-text mt-1.5 font-mono">
                Min threshold: {defaultShniMinLots} lots (₹{(defaultShniMinLots * lotSize * priceBand).toLocaleString("en-IN")})
              </p>
            </div>
          )}

          {categoryTab === "bHNI" && (
            <div>
              <label className="block text-[11px] font-semibold uppercase text-muted-text tracking-wider mb-2 flex items-center">
                Number of Lots Applying For (bHNI)
                <Tooltip content="bHNI minimum application threshold is ₹10 Lakhs." />
              </label>
              <input
                type="number"
                min={defaultBhniMinLots}
                value={bhniLots}
                onChange={(e) => setBhniLots(Math.max(defaultBhniMinLots, parseInt(e.target.value) || defaultBhniMinLots))}
                className="w-full bg-white border border-input-border rounded-lg px-3 py-2 text-[14px] font-semibold text-primary-text outline-none focus:border-accent-indigo font-mono"
              />
              <p className="text-[11px] text-secondary-text mt-1.5 font-mono">
                Min threshold: {defaultBhniMinLots} lots (₹{(defaultBhniMinLots * lotSize * priceBand).toLocaleString("en-IN")})
              </p>
            </div>
          )}

          {/* Category Rule Callout Box */}
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3.5 text-[12px] text-amber-900 leading-relaxed">
            <span className="font-semibold">{categoryTab} Rule:</span> {getCallout()}
          </div>
        </div>

        {/* RIGHT COLUMN: Category-Specific Result Panel */}
        <div className="bg-white border border-card-border rounded-xl p-5 shadow-xs space-y-4">
          {loading ? (
            <div className="py-8 text-center text-[13px] text-muted-text">Calculating allotment odds...</div>
          ) : error ? (
            <div className="py-8 text-center text-[13px] text-secondary-text bg-input-bg border border-input-border rounded-lg p-4">
              {error}
            </div>
          ) : result ? (
            <>
              {/* Header Status Label */}
              <div className="border-b border-card-border pb-3">
                <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-text mb-1">
                  {result.status_label || "Allotment Analysis"}
                </div>

                {result.calculation_status === "INSUFFICIENT_APPLICATION_DATA" ? (
                  <div className="space-y-2">
                    <div className="text-[20px] font-bold text-slate-700">
                      Exact Odds Unavailable
                    </div>
                    <div className="text-[12px] text-slate-600 bg-slate-100 p-3 rounded-lg border border-slate-200">
                      {result.explain_text || "Valid application-count data is not yet published by the registrar."}
                    </div>
                    {result.share_subscription_multiple != null && (
                      <div className="text-[12px] font-mono text-slate-500 pt-1">
                        Factual Share Subscription: <span className="font-bold text-slate-800">{result.share_subscription_multiple}x</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex items-baseline justify-between">
                    <span className="text-[13px] font-medium text-secondary-text">Probability:</span>
                    <span className="text-[26px] font-bold text-accent-indigo font-mono">
                      {result.probability_pct != null ? `${result.probability_pct}%` : "N/A"}
                    </span>
                  </div>
                )}
              </div>

              {/* Data Metrics Table */}
              <div className="space-y-2 text-[12px]">
                {result.probability_at_least_one_lot != null && (
                  <div className="flex justify-between">
                    <span className="text-secondary-text">Family PAN Odds (&ge; 1 Lot):</span>
                    <span className="font-mono font-medium text-indigo-600 font-bold">
                      {(result.probability_at_least_one_lot * 100).toFixed(1)}%
                    </span>
                  </div>
                )}
                {result.expected_lots != null && (
                  <div className="flex justify-between">
                    <span className="text-secondary-text">Expected Lots Allotted:</span>
                    <span className="font-mono font-medium">{result.expected_lots} lots</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-secondary-text">Regulatory Regime:</span>
                  <span className="font-semibold text-primary-text">{result.allotment_regime}</span>
                </div>
              </div>

              {/* Explain Text */}
              {result.explain_text && result.calculation_status !== "INSUFFICIENT_APPLICATION_DATA" && (
                <div className="bg-input-bg border border-input-border rounded-lg p-3 text-[11px] text-secondary-text leading-relaxed">
                  {result.explain_text}
                </div>
              )}
            </>
          ) : null}
        </div>
      </div>

      {/* Category Specific Visual Element (Grid for Retail, Coin Circle for sHNI, Fill Bar for bHNI) */}
      {showVisuals && result && (
        <div className="bg-white border border-card-border rounded-xl p-5 shadow-xs space-y-3">
          <div className="text-[11px] font-semibold uppercase text-muted-text tracking-wider">
            {categoryTab} Allotment Visualizer
          </div>

          {/* RETAIL: 50-Circle Grid */}
          {categoryTab === "RETAIL" && (
            <div className="space-y-3">
              <div className="grid grid-cols-10 sm:grid-cols-25 gap-1.5">
                {Array.from({ length: 50 }).map((_, i) => {
                  const isWinner = i < Math.min(50, Math.max(1, Math.round((result.odds_per_pan || 0.32) * 50)));
                  return (
                    <div
                      key={i}
                      className={`w-4 h-4 rounded-full border flex items-center justify-center transition-all ${
                        isWinner ? "bg-accent-indigo border-accent-indigo" : "bg-[#f3f4f6] border-[#e5e7eb]"
                      }`}
                    >
                      {isWinner && <div className="w-1 h-1 rounded-full bg-white"></div>}
                    </div>
                  );
                })}
              </div>
              <div className="text-[11px] text-secondary-text font-mono">
                Shows lottery distribution: {Math.round((result.odds_per_pan || 0.32) * 50)} filled slots out of 50.
              </div>
            </div>
          )}

          {/* sHNI: Large Coin Flip Circle */}
          {categoryTab === "sHNI" && (
            <div className="flex flex-col items-center justify-center py-4 space-y-3">
              <div
                className={`w-24 h-24 rounded-full border-4 flex flex-col items-center justify-center font-bold text-center transition-all shadow-md ${
                  result.probability_pct >= 50
                    ? "bg-accent-indigo border-indigo-300 text-white"
                    : "bg-white border-accent-indigo text-accent-indigo"
                }`}
              >
                <div className="text-[20px] font-mono">{result.probability_pct}%</div>
                <div className="text-[9px] uppercase font-mono tracking-wider opacity-90">Odds</div>
              </div>
              <div className="text-[12px] font-medium text-secondary-text text-center">
                sHNI Lottery Pool: {result.probability_pct}% chance of securing minimum allotment lot.
              </div>
            </div>
          )}

          {/* bHNI: Horizontal Fill Bar */}
          {categoryTab === "bHNI" && (
            <div className="space-y-2 py-2">
              <div className="flex justify-between text-[12px] font-semibold">
                <span className="text-secondary-text">Allotment Proportion:</span>
                <span className="font-mono text-accent-indigo">{result.probability_pct}%</span>
              </div>
              <div className="w-full h-4 bg-input-bg rounded-full overflow-hidden border border-input-border">
                <div
                  className="h-full bg-accent-indigo rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, Math.max(0, result.probability_pct || 0))}%` }}
                ></div>
              </div>
              <div className="text-[11px] text-secondary-text font-mono">
                Proportionate scaling across bHNI pool.
              </div>
            </div>
          )}
        </div>
      )}

      {/* Expandable Calculation Methodology & SEBI Regulations Drawer */}
      {result?.audit_trace && (
        <details className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-[12px] space-y-3 group">
          <summary className="font-semibold text-slate-800 cursor-pointer flex items-center justify-between select-none">
            <span className="flex items-center gap-2">
              <span>📜</span>
              <span>Calculation Methodology & SEBI Regulations</span>
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-mono font-bold ${
                result.audit_trace.confidence === "HIGH" 
                  ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                  : result.audit_trace.confidence === "MEDIUM"
                  ? "bg-amber-100 text-amber-800 border border-amber-300"
                  : "bg-slate-200 text-slate-700"
              }`}>
                {result.audit_trace.status} ({result.audit_trace.confidence})
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
              <div>
                <span className="text-slate-400 block">Share Subscription:</span>
                <span className="font-bold text-slate-700">
                  {result.audit_trace.share_subscription_multiple != null 
                    ? `${result.audit_trace.share_subscription_multiple}x` 
                    : "Unavailable"}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block">App Oversubscription:</span>
                <span className="font-bold text-slate-700">
                  {result.audit_trace.application_oversubscription_multiple != null 
                    ? `${result.audit_trace.application_oversubscription_multiple}x` 
                    : "Unavailable"}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block">Min Allotment Unit:</span>
                <span className="font-bold text-slate-700">
                  {result.audit_trace.minimum_allotment_shares} shares
                </span>
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

            {result.audit_trace.assumptions?.length > 0 && (
              <div>
                <span className="text-amber-700 font-sans font-semibold block">Assumptions & Disclaimers:</span>
                <ul className="list-disc pl-4 space-y-1 text-amber-800 font-sans">
                  {result.audit_trace.assumptions.map((item: string, idx: number) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </details>
      )}

      {/* One-Line Educational Strategy Note */}
      <div className="bg-indigo-50/60 border border-indigo-100 rounded-xl p-3.5 text-[12px] text-indigo-900 font-medium flex items-center gap-2">
        <span>💡</span>
        <div>{getEduNote()}</div>
      </div>
    </div>
  );
}
