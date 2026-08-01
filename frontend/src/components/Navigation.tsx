"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

export function Navigation() {
  const pathname = usePathname();
  const isAnalyseActive = pathname === "/" || pathname.startsWith("/analyse");

  return (
    <>
      {/* SEBI Compliance Disclaimer Banner */}
      <div className="bg-warning-bg border-b border-warning-border py-1.5 px-4 text-center text-[11px] font-medium text-warning-text flex items-center justify-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-warning-text animate-pulse"></span>
        <span>Educational platform for Indian market analysis. All outputs are framed as historical pattern matching — not buy/sell advice.</span>
      </div>

      <header className="sticky top-0 z-40 w-full h-[52px] border-b border-card-border bg-card-bg/95 backdrop-blur flex items-center shadow-xs">
        <div className="max-w-[1200px] w-full mx-auto flex h-full items-center justify-between px-6">
          <Link href="/" className="flex items-center space-x-2.5 group">
            <div className="w-3 h-3 rounded-full bg-accent-indigo group-hover:scale-110 transition-transform"></div>
            <span className="font-bold tracking-tight text-[15px] text-primary-text">IPO INSIGHT</span>
          </Link>
          
          <nav className="flex items-center space-x-2 text-[13px] font-medium">
            <Link
              href="/"
              className={cn(
                "px-4 py-1.5 transition-colors border",
                isAnalyseActive
                  ? "bg-btn-primary text-white border-btn-primary rounded-full shadow-xs"
                  : "bg-transparent text-secondary-text border-card-border rounded-full hover:text-primary-text hover:border-secondary-text"
              )}
            >
              Analyse
            </Link>
            <Link
              href="/learn"
              className={cn(
                "px-4 py-1.5 transition-colors border",
                pathname.startsWith("/learn")
                  ? "bg-btn-primary text-white border-btn-primary rounded-full shadow-xs"
                  : "bg-transparent text-secondary-text border-card-border rounded-full hover:text-primary-text hover:border-secondary-text"
              )}
            >
              Learn
            </Link>
          </nav>
        </div>
      </header>
    </>
  );
}
