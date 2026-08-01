"use client";

import Link from "next/link";
import { toSlug, getInitials, getSectorBadge, getStatusBadge } from "@/lib/helpers";

interface IpoCardProps {
  ipo: {
    name: string;
    gmp?: number;
    price_band?: number;
    gmp_trend?: string;
    est_listing_gain_pct?: number;
    exchange?: string;
    is_sme?: boolean;
    status?: string;
    sector?: string | null;
    issue_size?: number | null;
    close_date?: string | null;
  };
}

export default function IpoCard({ ipo }: IpoCardProps) {
  const slug = toSlug(ipo.name);
  const initials = getInitials(ipo.name);
  const statusBadge = getStatusBadge(ipo);
  const sectorBadge = getSectorBadge(ipo.sector || null);

  const gainPct = ipo.est_listing_gain_pct ?? (ipo.gmp && ipo.price_band ? Math.round((ipo.gmp / ipo.price_band) * 100) : 0);

  return (
    <div className="bg-card-bg border border-card-border rounded-[14px] p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group">
      <div>
        {/* Top Header Row */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-input-bg border border-input-border flex items-center justify-center text-[14px] font-bold text-primary-text font-mono group-hover:border-accent-indigo transition-colors">
              {initials}
            </div>
            <div>
              <span
                className="text-[10px] font-semibold tracking-wider px-2 py-0.5 rounded-full border uppercase"
                style={{ backgroundColor: statusBadge.bg, color: statusBadge.text, borderColor: statusBadge.border }}
              >
                {statusBadge.label}
              </span>
            </div>
          </div>
          {ipo.is_sme && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-gray-100 text-gray-600 border border-gray-200">
              SME
            </span>
          )}
        </div>

        {/* IPO Name & Sector */}
        <h3 className="text-[17px] font-bold text-primary-text mb-1 group-hover:text-accent-indigo transition-colors line-clamp-1">
          {ipo.name}
        </h3>
        <div className="flex flex-wrap items-center gap-2 mb-4">
          {ipo.sector && (
            <span
              className="text-[11px] font-medium px-2 py-0.5 rounded-full"
              style={{ backgroundColor: sectorBadge.bg, color: sectorBadge.text }}
            >
              {ipo.sector}
            </span>
          )}
          {ipo.exchange && (
            <span className="text-[11px] text-muted-text font-mono">
              {ipo.exchange}
            </span>
          )}
        </div>

        {/* Mini Stats Grid */}
        <div className="grid grid-cols-2 gap-2 bg-input-bg border border-input-border rounded-[10px] p-3 mb-4 text-[12px]">
          <div>
            <div className="text-[10px] uppercase font-semibold text-muted-text tracking-wider mb-0.5">Price / Lot</div>
            <div className="font-semibold text-primary-text">
              {ipo.price_band ? `₹${ipo.price_band}` : "N/A"}
            </div>
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-muted-text tracking-wider mb-0.5">Est. Gain</div>
            <div
              className="font-bold"
              style={{ color: gainPct > 0 ? "var(--color-positive)" : gainPct < 0 ? "var(--color-negative)" : "var(--color-secondary-text)" }}
            >
              {gainPct > 0 ? `+${gainPct}%` : `${gainPct}%`}
            </div>
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-muted-text tracking-wider mb-0.5">GMP</div>
            <div className="font-semibold text-primary-text">
              {ipo.gmp !== undefined && ipo.gmp !== null ? `₹${ipo.gmp}` : "N/A"}
            </div>
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-muted-text tracking-wider mb-0.5">Issue Size</div>
            <div className="font-semibold text-primary-text">
              {ipo.issue_size ? `₹${ipo.issue_size} Cr` : "N/A"}
            </div>
          </div>
        </div>
      </div>

      {/* Footer Link */}
      <div className="pt-2 border-t border-card-border flex items-center justify-between text-[13px]">
        <span className="text-[11px] text-secondary-text font-mono">
          {ipo.close_date ? `Closes ${ipo.close_date}` : "Dates pending"}
        </span>
        <Link
          href={`/analyse/${slug}`}
          className="font-semibold text-accent-indigo hover:underline inline-flex items-center gap-1 group-hover:translate-x-0.5 transition-transform"
        >
          Analyse <span className="text-[14px]">→</span>
        </Link>
      </div>
    </div>
  );
}
