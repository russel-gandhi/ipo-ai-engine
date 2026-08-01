"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { fetchLiveIPOs, fetchVerdict, fetchPeers, calculateAllotment } from "@/lib/api";
import { toSlug, getInitials, getSectorBadge, getStatusBadge } from "@/lib/helpers";
import Tooltip from "@/components/Tooltip";

export default function IpoDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const resolvedParams = use(params);
  const slug = resolvedParams.slug;

  const [ipo, setIpo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  // Pattern Match state
  const [verdict, setVerdict] = useState<any>(null);
  const [peersData, setPeersData] = useState<any>(null);
  const [patternLoading, setPatternLoading] = useState(false);

  // Allotment Calculator state
  const [pans, setPans] = useState<number>(1);
  const [allotmentResult, setAllotmentResult] = useState<any>(null);
  const [calcLoading, setCalcLoading] = useState(false);

  useEffect(() => {
    fetchLiveIPOs()
      .then((data) => {
        if (data && data.ipos) {
          const matched = data.ipos.find((item: any) => toSlug(item.name) === slug);
          if (matched) {
            setIpo(matched);
            loadPatternMatch(matched);
            loadInitialAllotment(matched, 1);
          } else {
            setNotFound(true);
          }
        }
      })
      .catch((err) => {
        console.error("Error fetching IPO detail:", err);
        setNotFound(true);
      })
      .finally(() => setLoading(false));
  }, [slug]);

  const loadPatternMatch = async (targetIpo: any) => {
    setPatternLoading(true);
    try {
      const features = {
        issue_size: targetIpo.issue_size || 500.0,
        fresh_vs_ofs_ratio: 0.5,
        sub_retail: targetIpo.sub_retail || 5.0,
        sub_nii: targetIpo.sub_nii || 15.0,
        sub_qib: targetIpo.sub_qib || 25.0,
        sub_overall: targetIpo.sub_overall || 10.0,
        price_band: targetIpo.price_band || 100.0,
        sector: targetIpo.sector || "Manufacturing",
        gmp_trend: targetIpo.gmp_trend || "rising",
        is_sme: targetIpo.is_sme || false,
        anchor_allocation_pct: 0.3,
        relative_issue_size: 1.0,
        gmp_trajectory: 0.1,
        market_regime_nifty_30d: 0.03
      };

      const [vData, pData] = await Promise.all([
        fetchVerdict(features),
        fetchPeers(targetIpo.issue_size || 500.0, targetIpo.sector || "Manufacturing")
      ]);

      setVerdict(vData);
      setPeersData(pData);
    } catch (e) {
      console.error("Error loading pattern match:", e);
    } finally {
      setPatternLoading(false);
    }
  };

  const loadInitialAllotment = async (targetIpo: any, numPans: number) => {
    setCalcLoading(true);
    try {
      const payload = {
        sub_retail: targetIpo.sub_retail || 5.0,
        retail_quota_pct: targetIpo.offer_breakdown?.retail_pct ? targetIpo.offer_breakdown.retail_pct / 100 : 0.35,
        issue_size_cr: targetIpo.issue_size || 100.0,
        lot_size: targetIpo.lot_size || 100,
        cutoff_price: targetIpo.price_band || 100,
        applied_lots_per_pan: 1,
        num_pans: numPans
      };
      const res = await calculateAllotment(payload);
      setAllotmentResult(res);
    } catch (e) {
      console.error("Error calculating allotment:", e);
    } finally {
      setCalcLoading(false);
    }
  };

  const handlePanChange = (num: number) => {
    setPans(num);
    if (ipo) loadInitialAllotment(ipo, num);
  };

  if (loading) {
    return (
      <div className="max-w-[1100px] mx-auto px-6 py-12 animate-pulse space-y-6">
        <div className="h-10 bg-input-bg rounded w-1/3 mb-4"></div>
        <div className="h-40 bg-card-bg rounded-[14px]"></div>
        <div className="h-60 bg-card-bg rounded-[14px]"></div>
      </div>
    );
  }

  if (notFound || !ipo) {
    return (
      <div className="max-w-[800px] mx-auto px-6 py-20 text-center">
        <h1 className="text-[24px] font-bold text-primary-text mb-3">IPO Not Found</h1>
        <p className="text-[14px] text-secondary-text mb-6">
          We couldn't find an IPO matching "{slug}".
        </p>
        <Link href="/" className="inline-block bg-btn-primary text-white text-[13px] font-semibold px-5 py-2.5 rounded-full">
          ← Back to All IPOs
        </Link>
      </div>
    );
  }

  const statusBadge = getStatusBadge(ipo);
  const sectorBadge = getSectorBadge(ipo.sector);
  const initials = getInitials(ipo.name);

  return (
    <div className="max-w-[1100px] mx-auto px-6 py-8 space-y-8">
      {/* Breadcrumb Navigation */}
      <div className="flex items-center gap-2 text-[12px] text-secondary-text">
        <Link href="/" className="hover:text-primary-text transition-colors">
          Home
        </Link>
        <span>/</span>
        <span className="text-primary-text font-medium">{ipo.name}</span>
      </div>

      {/* SECTION 1: IPO Header & Timeline */}
      <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-card-border">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-full bg-input-bg border border-input-border flex items-center justify-center text-[18px] font-bold font-mono text-primary-text shrink-0">
              {initials}
            </div>
            <div>
              <div className="flex items-center gap-2.5 flex-wrap mb-1.5">
                <h1 className="text-[26px] font-bold text-primary-text tracking-tight">{ipo.name}</h1>
                <span
                  className="text-[10px] font-semibold tracking-wider px-2.5 py-0.5 rounded-full border uppercase"
                  style={{ backgroundColor: statusBadge.bg, color: statusBadge.text, borderColor: statusBadge.border }}
                >
                  {statusBadge.label}
                </span>
                {ipo.is_sme && (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-gray-100 text-gray-600 border border-gray-200">
                    SME
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2 text-[13px] text-secondary-text">
                {ipo.sector && (
                  <span
                    className="text-[11px] font-medium px-2.5 py-0.5 rounded-full"
                    style={{ backgroundColor: sectorBadge.bg, color: sectorBadge.text }}
                  >
                    {ipo.sector}
                  </span>
                )}
                {ipo.exchange && <span>• {ipo.exchange}</span>}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-6 bg-input-bg border border-input-border rounded-xl p-4 shrink-0">
            <div>
              <div className="text-[10px] uppercase font-semibold text-muted-text tracking-wider mb-0.5">Price Range</div>
              <div className="text-[16px] font-bold text-primary-text">{ipo.price_band_range || `₹${ipo.price_band || "N/A"}`}</div>
            </div>
            <div className="h-8 w-px bg-card-border"></div>
            <div>
              <div className="text-[10px] uppercase font-semibold text-muted-text tracking-wider mb-0.5 flex items-center">
                Lot Size
                <Tooltip content="Minimum number of shares required to submit 1 retail lot application." />
              </div>
              <div className="text-[16px] font-bold text-primary-text">{ipo.lot_size ? `${ipo.lot_size} shares` : "N/A"}</div>
            </div>
          </div>
        </div>

        {/* Timeline */}
        <div className="pt-6">
          <div className="text-[10px] uppercase font-semibold tracking-wider text-muted-text mb-3">Issue Timeline</div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-input-bg border border-input-border rounded-lg p-3">
              <div className="text-[11px] text-secondary-text mb-0.5">Open Date</div>
              <div className="text-[13px] font-semibold text-primary-text">{ipo.open_date || "TBA"}</div>
            </div>
            <div className="bg-input-bg border border-input-border rounded-lg p-3">
              <div className="text-[11px] text-secondary-text mb-0.5">Close Date</div>
              <div className="text-[13px] font-semibold text-primary-text">{ipo.close_date || "TBA"}</div>
            </div>
            <div className="bg-input-bg border border-input-border rounded-lg p-3">
              <div className="text-[11px] text-secondary-text mb-0.5">Allotment Date</div>
              <div className="text-[13px] font-semibold text-primary-text">{ipo.allotment_date || "TBA"}</div>
            </div>
            <div className="bg-input-bg border border-input-border rounded-lg p-3">
              <div className="text-[11px] text-secondary-text mb-0.5">Listing Date</div>
              <div className="text-[13px] font-semibold text-primary-text">{ipo.listing_date || "TBA"}</div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 2: Subscription Dashboard */}
      <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-[18px] font-bold text-primary-text">Subscription Dashboard</h2>
          <span className="text-[12px] font-mono text-muted-text">Live Multiples</span>
        </div>

        {ipo.sub_retail || ipo.sub_qib || ipo.sub_nii ? (
          <div className="space-y-4">
            {/* QIB Bar */}
            <div>
              <div className="flex justify-between text-[13px] font-medium mb-1">
                <span className="flex items-center">
                  QIB (Institutional)
                  <Tooltip content="Qualified Institutional Buyers: Mutual funds, banks, FPIs." />
                </span>
                <span className="font-mono font-semibold">{ipo.sub_qib ? `${ipo.sub_qib}x` : "N/A"}</span>
              </div>
              <div className="w-full h-3 bg-input-bg rounded-full overflow-hidden border border-input-border">
                <div
                  className="h-full bg-indigo-500 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(((ipo.sub_qib || 0) / 50) * 100, 100)}%` }}
                ></div>
              </div>
            </div>

            {/* NII Bar */}
            <div>
              <div className="flex justify-between text-[13px] font-medium mb-1">
                <span className="flex items-center">
                  NII (High Networth)
                  <Tooltip content="Non-Institutional Investors applying above ₹2 Lakhs." />
                </span>
                <span className="font-mono font-semibold">{ipo.sub_nii ? `${ipo.sub_nii}x` : "N/A"}</span>
              </div>
              <div className="w-full h-3 bg-input-bg rounded-full overflow-hidden border border-input-border">
                <div
                  className="h-full bg-sky-500 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(((ipo.sub_nii || 0) / 50) * 100, 100)}%` }}
                ></div>
              </div>
            </div>

            {/* Retail Bar */}
            <div>
              <div className="flex justify-between text-[13px] font-medium mb-1">
                <span className="flex items-center">
                  Retail Individual
                  <Tooltip content="Individual investors applying up to ₹2 Lakhs." />
                </span>
                <span className="font-mono font-semibold">{ipo.sub_retail ? `${ipo.sub_retail}x` : "N/A"}</span>
              </div>
              <div className="w-full h-3 bg-input-bg rounded-full overflow-hidden border border-input-border">
                <div
                  className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(((ipo.sub_retail || 0) / 50) * 100, 100)}%` }}
                ></div>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-input-bg border border-input-border rounded-xl p-6 text-center text-[13px] text-secondary-text">
            Subscription data not yet available — check back after the issue opens.
          </div>
        )}
      </section>

      {/* SECTION 3: Offer Breakdown */}
      <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs">
        <h2 className="text-[18px] font-bold text-primary-text mb-4">Offer Breakdown</h2>
        {ipo.offer_breakdown ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-input-bg border border-input-border rounded-xl p-4 text-center">
              <div className="text-[26px] font-bold text-accent-indigo">
                {ipo.offer_breakdown.qib_pct ? `${ipo.offer_breakdown.qib_pct}%` : "N/A"}
              </div>
              <div className="text-[12px] font-medium text-secondary-text mt-1 flex items-center justify-center">
                QIB Quota
                <Tooltip content="Percentage allocated to Qualified Institutional Buyers." />
              </div>
            </div>
            <div className="bg-input-bg border border-input-border rounded-xl p-4 text-center">
              <div className="text-[26px] font-bold text-sky-600">
                {ipo.offer_breakdown.nii_pct ? `${ipo.offer_breakdown.nii_pct}%` : "N/A"}
              </div>
              <div className="text-[12px] font-medium text-secondary-text mt-1 flex items-center justify-center">
                NII Quota
                <Tooltip content="Percentage allocated to Non-Institutional Investors." />
              </div>
            </div>
            <div className="bg-input-bg border border-input-border rounded-xl p-4 text-center">
              <div className="text-[26px] font-bold text-emerald-600">
                {ipo.offer_breakdown.retail_pct ? `${ipo.offer_breakdown.retail_pct}%` : "N/A"}
              </div>
              <div className="text-[12px] font-medium text-secondary-text mt-1 flex items-center justify-center">
                Retail Quota
                <Tooltip content="Percentage allocated to Retail Individual Investors." />
              </div>
            </div>
          </div>
        ) : (
          <div className="text-[13px] text-secondary-text">Offer breakdown details pending in RHP.</div>
        )}
      </section>

      {/* SECTION 4: Lot Distribution Table */}
      {ipo.lot_distribution && ipo.lot_distribution.length > 0 && (
        <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs">
          <h2 className="text-[18px] font-bold text-primary-text mb-4">Lot Distribution Table</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-[13px]">
              <thead>
                <tr className="border-b border-card-border text-muted-text uppercase text-[10px] font-semibold tracking-wider">
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Min Shares</th>
                  <th className="py-2.5 px-3 flex items-center">
                    Min Amount
                    <Tooltip content="Calculated at cap price." />
                  </th>
                  <th className="py-2.5 px-3">Total Lots</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-card-border">
                {ipo.lot_distribution.map((row: any, i: number) => (
                  <tr key={i} className="hover:bg-input-bg/50">
                    <td className="py-3 px-3 font-semibold text-primary-text">{row.category}</td>
                    <td className="py-3 px-3 font-mono">{row.min_shares || "N/A"}</td>
                    <td className="py-3 px-3 font-mono font-semibold">
                      {row.min_amount ? `₹${row.min_amount.toLocaleString("en-IN")}` : "N/A"}
                    </td>
                    <td className="py-3 px-3 font-mono">{row.total_lots || "1"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* SECTION 5: SEBI Allotment Calculator */}
      <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-[18px] font-bold text-primary-text">SEBI Allotment Calculator</h2>
            <p className="text-[12px] text-secondary-text">Proportionate lottery odds math per SEBI rule (max 1 lot per PAN)</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
          {/* Controls */}
          <div className="bg-input-bg border border-input-border rounded-xl p-5 space-y-4">
            <div>
              <label className="block text-[11px] font-semibold uppercase text-muted-text tracking-wider mb-2">
                Number of PAN Applications
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={pans}
                  onChange={(e) => handlePanChange(Math.max(1, parseInt(e.target.value) || 1))}
                  className="w-full bg-white border border-input-border rounded-lg px-3 py-2 text-[14px] font-semibold text-primary-text outline-none focus:border-accent-indigo"
                />
              </div>
              <p className="text-[11px] text-secondary-text mt-1.5">
                Each family member's PAN counts as 1 separate lottery ticket.
              </p>
            </div>

            {/* SEBI Callout */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-[12px] text-amber-800 leading-relaxed">
              <span className="font-semibold">SEBI Lottery Rule:</span> Applying for multiple lots on the same PAN does NOT increase your allotment probability. Submitting 1 lot per PAN across distinct family PANs is the optimal strategy.
            </div>
          </div>

          {/* Results Display */}
          <div className="bg-white border border-card-border rounded-xl p-5 shadow-xs space-y-4">
            {calcLoading ? (
              <div className="py-8 text-center text-[13px] text-muted-text">Calculating probability...</div>
            ) : allotmentResult ? (
              <>
                <div className="flex items-baseline justify-between border-b border-card-border pb-3">
                  <span className="text-[13px] font-medium text-secondary-text">Probability of Allotment:</span>
                  <span className="text-[26px] font-bold text-accent-indigo font-mono">
                    {(allotmentResult.probability_at_least_one_lot * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="space-y-2 text-[12px]">
                  <div className="flex justify-between">
                    <span className="text-secondary-text">Probability per PAN:</span>
                    <span className="font-mono font-medium">{(allotmentResult.odds_per_pan * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-secondary-text">Expected Lots Allotted:</span>
                    <span className="font-mono font-medium">{allotmentResult.expected_lots}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-secondary-text">Regime Type:</span>
                    <span className="font-semibold capitalize">{allotmentResult.allotment_regime}</span>
                  </div>
                </div>
                {allotmentResult.explain_text && (
                  <div className="bg-input-bg border border-input-border rounded-lg p-3 text-[11px] text-secondary-text leading-relaxed">
                    {allotmentResult.explain_text}
                  </div>
                )}
              </>
            ) : null}
          </div>
        </div>
      </section>

      {/* SECTION 6: Company Profile & Financials */}
      <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs space-y-6">
        <h2 className="text-[18px] font-bold text-primary-text">Company Profile & Financials</h2>

        {/* About */}
        {ipo.about && (
          <div>
            <h3 className="text-[13px] font-semibold uppercase text-muted-text tracking-wider mb-2">About the Company</h3>
            <p className="text-[14px] text-primary-text leading-relaxed bg-input-bg border border-input-border rounded-xl p-4">
              {ipo.about}
            </p>
          </div>
        )}

        {/* Issue Objectives */}
        {ipo.issue_objective && ipo.issue_objective.length > 0 && (
          <div>
            <h3 className="text-[13px] font-semibold uppercase text-muted-text tracking-wider mb-2">Objects of the Issue</h3>
            <ul className="list-disc list-inside space-y-1.5 text-[13px] text-primary-text bg-input-bg border border-input-border rounded-xl p-4">
              {ipo.issue_objective.map((obj: string, i: number) => (
                <li key={i}>{obj}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Financial Performance Table */}
        {ipo.financials && ipo.financials.length > 0 && (
          <div>
            <h3 className="text-[13px] font-semibold uppercase text-muted-text tracking-wider mb-2">Financial Performance (₹ in Crores)</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-[13px]">
                <thead>
                  <tr className="border-b border-card-border text-muted-text uppercase text-[10px] font-semibold tracking-wider bg-input-bg">
                    <th className="py-2.5 px-3">Period</th>
                    <th className="py-2.5 px-3 text-right">Revenue</th>
                    <th className="py-2.5 px-3 text-right">Profit After Tax (PAT)</th>
                    <th className="py-2.5 px-3 text-right">Total Assets</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-card-border">
                  {ipo.financials.map((row: any, i: number) => (
                    <tr key={i} className="hover:bg-input-bg/50">
                      <td className="py-3 px-3 font-semibold text-primary-text">{row.period}</td>
                      <td className="py-3 px-3 font-mono text-right">{row.revenue ? `₹${row.revenue} Cr` : "N/A"}</td>
                      <td className="py-3 px-3 font-mono text-right font-medium" style={{ color: row.profit > 0 ? "var(--color-positive)" : "var(--color-negative)" }}>
                        {row.profit ? `₹${row.profit} Cr` : "N/A"}
                      </td>
                      <td className="py-3 px-3 font-mono text-right">{row.assets ? `₹${row.assets} Cr` : "N/A"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>

      {/* SECTION 7: Pattern Match Panel */}
      <section className="bg-card-bg border border-card-border rounded-[14px] p-6 shadow-xs space-y-6">
        <div className="flex items-center justify-between border-b border-card-border pb-4">
          <div>
            <div className="text-[10px] font-bold tracking-wider text-accent-indigo uppercase mb-1">
              Historical Reference — Not a Projection
            </div>
            <h2 className="text-[18px] font-bold text-primary-text">Pattern Match Analysis</h2>
          </div>
          {verdict && (
            <span className="bg-indigo-50 text-indigo-700 border border-indigo-200 text-[12px] font-semibold px-3 py-1 rounded-full">
              {verdict.historical_gain_range}
            </span>
          )}
        </div>

        {patternLoading ? (
          <div className="py-8 text-center text-[13px] text-muted-text">Running historical pattern match...</div>
        ) : verdict ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-input-bg border border-input-border rounded-xl p-4">
                <div className="text-[10px] font-semibold text-muted-text uppercase tracking-wider mb-1">Bucket Estimate</div>
                <div className="text-[18px] font-bold text-primary-text capitalize">{verdict.bucket_estimate}</div>
              </div>
              <div className="bg-input-bg border border-input-border rounded-xl p-4">
                <div className="text-[10px] font-semibold text-muted-text uppercase tracking-wider mb-1">Confidence Score</div>
                <div className="text-[18px] font-bold text-primary-text">{verdict.confidence_score}</div>
              </div>
              <div className="bg-input-bg border border-input-border rounded-xl p-4">
                <div className="text-[10px] font-semibold text-muted-text uppercase tracking-wider mb-1">Historical Walk-Forward Accuracy</div>
                <div className="text-[18px] font-bold text-primary-text">{(verdict.walk_forward_accuracy_for_bucket * 100).toFixed(0)}%</div>
              </div>
            </div>

            {/* Proof of Work Peers Table */}
            {peersData && peersData.peers && (
              <div>
                <h3 className="text-[13px] font-semibold uppercase text-muted-text tracking-wider mb-3">Historical Similar Issues (Backtesting Peers)</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-[13px]">
                    <thead>
                      <tr className="border-b border-card-border text-muted-text uppercase text-[10px] font-semibold tracking-wider bg-input-bg">
                        <th className="py-2.5 px-3">Company</th>
                        <th className="py-2.5 px-3 text-right">Actual Gain</th>
                        <th className="py-2.5 px-3 text-right">Retro Range</th>
                        <th className="py-2.5 px-3 text-right">Delta</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-card-border">
                      {peersData.peers.map((peer: any, idx: number) => {
                        const isZaggle = peer.retroactive_gain_range === "N/A" || peer.company_name.toLowerCase().includes("zaggle");
                        return (
                          <tr key={idx} className={`hover:bg-input-bg/50 ${isZaggle ? 'opacity-50' : ''}`}>
                            <td className="py-3 px-3 font-semibold text-primary-text">
                              {peer.company_name}
                              {peer.regime_warning && (
                                <span className="ml-2 bg-amber-100 text-amber-800 border border-amber-200 text-[10px] px-1.5 py-0.5 rounded font-mono">
                                  2021 Bubble
                                </span>
                              )}
                            </td>
                            <td className="py-3 px-3 text-right font-mono font-medium" style={{ color: peer.actual_listing_gain_pct >= 0 ? 'var(--color-positive)' : 'var(--color-negative)' }}>
                              {peer.actual_listing_gain_pct > 0 ? '+' : ''}{peer.actual_listing_gain_pct}%
                            </td>
                            <td className="py-3 px-3 text-right font-mono text-secondary-text">{peer.retroactive_gain_range}</td>
                            <td className="py-3 px-3 text-right font-mono font-bold" style={{ color: Math.abs(peer.delta) <= 15 ? 'var(--color-positive)' : 'var(--color-negative)' }}>
                              {isZaggle ? 'N/A' : `${peer.delta > 0 ? '+' : ''}${peer.delta}%`}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ) : null}

        {/* Verbatim Disclaimer */}
        <div className="bg-input-bg border border-input-border rounded-xl p-4 text-[11px] text-secondary-text leading-relaxed">
          {verdict?.disclaimer || "All outputs are generated via historical pattern matching against past Indian IPO listings. Never interpret predictions as buy/sell recommendations."}
        </div>
      </section>
    </div>
  );
}
