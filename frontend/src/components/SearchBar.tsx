"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { fetchLiveIPOs } from "@/lib/api";
import { toSlug, getInitials, getStatusBadge } from "@/lib/helpers";

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState<number>(-1);

  const router = useRouter();
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setHighlightedIndex(-1);
    const timer = setTimeout(() => {
      if (query.trim().length > 0) {
        setLoading(true);
        fetchLiveIPOs(query.trim())
          .then((data) => {
            if (data && data.ipos) {
              setResults(data.ipos);
              setIsOpen(true);
            }
          })
          .catch(console.error)
          .finally(() => setLoading(false));
      } else {
        setResults([]);
        setIsOpen(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query]);

  // Scroll highlighted item into view automatically
  useEffect(() => {
    if (highlightedIndex >= 0) {
      document.getElementById(`result-${highlightedIndex}`)
        ?.scrollIntoView({ block: "nearest" });
    }
  }, [highlightedIndex]);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setHighlightedIndex(-1);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (name: string) => {
    const slug = toSlug(name);
    setQuery("");
    setIsOpen(false);
    setHighlightedIndex(-1);
    router.push(`/analyse/${slug}`);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Tab") {
      setIsOpen(false);
      setHighlightedIndex(-1);
      return;
    }

    if (e.key === "Escape") {
      setIsOpen(false);
      setHighlightedIndex(-1);
      return;
    }

    if (!isOpen || results.length === 0) {
      return;
    }

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlightedIndex((prev) => {
        if (prev === -1 || prev >= results.length - 1) {
          return 0;
        }
        return prev + 1;
      });
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlightedIndex((prev) => {
        if (prev <= 0) {
          return results.length - 1;
        }
        return prev - 1;
      });
    } else if (e.key === "Enter") {
      if (highlightedIndex >= 0 && highlightedIndex < results.length) {
        e.preventDefault();
        handleSelect(results[highlightedIndex].name);
      } else if (highlightedIndex === -1 && results.length === 1) {
        e.preventDefault();
        handleSelect(results[0].name);
      }
    } else {
      // Reset keyboard highlight on typing alphanumeric/keystrokes
      setHighlightedIndex(-1);
    }
  };

  return (
    <div className="relative w-full max-w-[560px] mx-auto" ref={dropdownRef}>
      <div className="relative flex items-center">
        <input
          type="text"
          role="combobox"
          aria-expanded={isOpen}
          aria-activedescendant={highlightedIndex >= 0 ? `result-${highlightedIndex}` : undefined}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => query.trim().length > 0 && setIsOpen(true)}
          placeholder="Search any open or upcoming IPO by name..."
          className="w-full bg-card-bg border border-card-border rounded-xl px-4 py-3.5 pl-11 text-[14px] text-primary-text placeholder:text-muted-text shadow-sm outline-none focus:border-accent-indigo focus:ring-2 focus:ring-accent-indigo/10 transition-all font-sans"
        />
        <svg
          className="absolute left-4 w-4 h-4 text-muted-text pointer-events-none"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        {loading && (
          <div className="absolute right-4 w-4 h-4 border-2 border-accent-indigo border-t-transparent rounded-full animate-spin"></div>
        )}
      </div>

      {/* Autocomplete Dropdown */}
      {isOpen && (
        <div
          role="listbox"
          className="absolute top-full left-0 right-0 mt-2 bg-card-bg border border-card-border rounded-xl shadow-xl overflow-hidden z-50 divide-y divide-card-border max-h-[360px] overflow-y-auto"
        >
          {results.length > 0 ? (
            results.map((ipo, index) => {
              const statusBadge = getStatusBadge(ipo);
              const initials = getInitials(ipo.name);
              const isHighlighted = index === highlightedIndex;

              return (
                <div
                  key={ipo.name}
                  id={`result-${index}`}
                  role="option"
                  aria-selected={isHighlighted}
                  onClick={() => handleSelect(ipo.name)}
                  className={`p-3 cursor-pointer flex items-center justify-between transition-colors hover:bg-input-bg border-l-2 ${
                    isHighlighted
                      ? "bg-[#f5f3ff] border-[#6366f1]"
                      : "border-transparent"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-input-bg border border-input-border flex items-center justify-center text-[11px] font-bold font-mono">
                      {initials}
                    </div>
                    <div>
                      <div className="text-[13px] font-semibold text-primary-text">{ipo.name}</div>
                      <div className="text-[11px] text-secondary-text">
                        {ipo.sector || "IPO"} • {ipo.exchange || "BSE/NSE"}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {ipo.gmp !== undefined && (
                      <span className="text-[11px] font-mono text-secondary-text">
                        GMP ₹{ipo.gmp}
                      </span>
                    )}
                    <span
                      className="text-[10px] font-semibold tracking-wider px-2 py-0.5 rounded-full border uppercase"
                      style={{ backgroundColor: statusBadge.bg, color: statusBadge.text, borderColor: statusBadge.border }}
                    >
                      {statusBadge.label}
                    </span>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="p-4 text-center text-[13px] text-muted-text">
              No matching IPOs found for "{query}"
            </div>
          )}
        </div>
      )}
    </div>
  );
}
