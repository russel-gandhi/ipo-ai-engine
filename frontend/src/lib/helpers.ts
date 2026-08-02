export function toSlug(name: string): string {
  return (name || "")
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/[\s_]+/g, "-")
    .replace(/-+/g, "-");
}

export function fromSlug(slug: string): string {
  return (slug || "")
    .split("-")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export function getInitials(name: string): string {
  if (!name) return "IP";
  const words = name.trim().split(/\s+/);
  if (words.length === 1) return words[0].substring(0, 2).toUpperCase();
  return (words[0][0] + words[1][0]).toUpperCase();
}

export function getSectorBadge(sector?: string | null): { label: string; bg: string; text: string } {
  const s = (sector || "").toLowerCase();
  if (s.includes("tech") || s.includes("software") || s.includes("it")) {
    return { label: sector || "Technology", bg: "bg-blue-100", text: "text-blue-800" };
  }
  if (s.includes("health") || s.includes("pharma") || s.includes("medical")) {
    return { label: sector || "Healthcare", bg: "bg-emerald-100", text: "text-emerald-800" };
  }
  if (s.includes("finance") || s.includes("bank") || s.includes("fintech")) {
    return { label: sector || "Financials", bg: "bg-purple-100", text: "text-purple-800" };
  }
  if (s.includes("consumer") || s.includes("retail") || s.includes("fmcg")) {
    return { label: sector || "Consumer", bg: "bg-amber-100", text: "text-amber-800" };
  }
  if (s.includes("industrial") || s.includes("manufactur") || s.includes("engineer")) {
    return { label: sector || "Manufacturing", bg: "bg-slate-100", text: "text-slate-800" };
  }
  return { label: sector || "General", bg: "bg-gray-100", text: "text-gray-800" };
}

export function getStatusBadge(input?: any): { label: string; bg: string; text: string; border?: string } {
  let statusStr = "";
  if (typeof input === "string") {
    statusStr = input;
  } else if (input && typeof input === "object") {
    statusStr = input.status || input.gmp_status || "";
  }
  const s = statusStr.toLowerCase();
  if (s.includes("open") || s.includes("active") || s.includes("live")) {
    return { label: "LIVE NOW", bg: "bg-emerald-100 border border-emerald-200", text: "text-emerald-800", border: "#a7f3d0" };
  }
  if (s.includes("closed") || s.includes("allotment")) {
    return { label: "CLOSED", bg: "bg-rose-100 border border-rose-200", text: "text-rose-800", border: "#fecdd3" };
  }
  return { label: "UPCOMING", bg: "bg-blue-100 border border-blue-200", text: "text-blue-800", border: "#bfdbfe" };
}

