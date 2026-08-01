"use client";

import { useState, useEffect } from "react";
import { fetchLiveIPOs } from "@/lib/api";
import SearchBar from "@/components/SearchBar";
import IpoCard from "@/components/IpoCard";

export default function LandingPage() {
  const [ipos, setIpos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLiveIPOs()
      .then((data) => {
        if (data && data.ipos) {
          setIpos(data.ipos);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-[calc(100vh-52px)] pb-16">
      {/* Hero Section */}
      <section className="pt-14 pb-12 px-6 max-w-[720px] mx-auto text-center">
        <div className="text-[11px] font-bold tracking-[0.12em] text-accent-indigo uppercase mb-3">
          INDIA'S IPO ANALYSIS ENGINE
        </div>
        <h1 className="text-[34px] md:text-[42px] font-bold text-primary-text leading-tight mb-4 tracking-tight">
          Understand any IPO <span className="text-accent-indigo">before you apply</span>
        </h1>
        <p className="text-[14px] text-secondary-text leading-relaxed max-w-[580px] mx-auto mb-8">
          Search any open or upcoming issue in India for subscription metrics, SEBI proportionate allotment odds, and historical pattern matching.
        </p>

        {/* Search Bar */}
        <SearchBar />
      </section>

      {/* Currently Open & Upcoming IPOs Grid */}
      <section className="max-w-[1200px] mx-auto px-6 pt-6">
        <div className="flex items-center justify-between border-b border-card-border pb-4 mb-6">
          <div>
            <h2 className="text-[18px] font-bold text-primary-text">Currently Open & Upcoming IPOs</h2>
            <p className="text-[12px] text-secondary-text">
              Real-time issues tracked across BSE & NSE mainboard and SME segments
            </p>
          </div>
          <div className="text-[12px] font-mono text-muted-text">
            {ipos.length} issues tracked
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="bg-card-bg border border-card-border rounded-[14px] p-6 h-[260px] animate-pulse">
                <div className="w-10 h-10 rounded-full bg-input-bg mb-4"></div>
                <div className="h-5 bg-input-bg rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-input-bg rounded w-1/2 mb-6"></div>
                <div className="h-20 bg-input-bg rounded w-full"></div>
              </div>
            ))}
          </div>
        ) : ipos.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {ipos.map((ipo) => (
              <IpoCard key={ipo.name} ipo={ipo} />
            ))}
          </div>
        ) : (
          <div className="bg-card-bg border border-card-border rounded-[14px] p-12 text-center text-secondary-text">
            No live IPOs available at the moment.
          </div>
        )}
      </section>
    </div>
  );
}
