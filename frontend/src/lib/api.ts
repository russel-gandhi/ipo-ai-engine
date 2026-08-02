const API_BASE = process.env.NEXT_PUBLIC_API_URL 
  || process.env.NEXT_PUBLIC_API_BASE_URL 
  || "https://ipo-insight-backend.onrender.com";

export async function fetchLiveIPOs(name?: string) {
  const url = name
    ? `${API_BASE}/api/live-ipos?name=${encodeURIComponent(name)}`
    : `${API_BASE}/api/live-ipos`;
  const res = await fetch(url, { next: { revalidate: 60 } });
  if (!res.ok) throw new Error(`live-ipos failed: ${res.status}`);
  return res.json();
}

export async function fetchVerdict(features: Record<string, unknown>) {
  const res = await fetch(`${API_BASE}/api/ipo/verdict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(features),
  });
  if (!res.ok) throw new Error(`verdict failed: ${res.status}`);
  return res.json();
}

export async function fetchPeers(issue_size: number, sector: string) {
  const res = await fetch(`${API_BASE}/api/ipo/peers`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ issue_size, sector }),
  });
  if (!res.ok) throw new Error(`peers failed: ${res.status}`);
  return res.json();
}

export async function calculateAllotment(payload: Record<string, unknown>) {
  const res = await fetch(`${API_BASE}/api/ipo/calculate-allotment`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    // Try fallback endpoint
    const fallbackRes = await fetch(`${API_BASE}/api/allotment-odds`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!fallbackRes.ok) {
      const errData = await fallbackRes.json().catch(() => ({}));
      throw new Error(errData.detail || `Calculation failed: ${fallbackRes.status}`);
    }
    return fallbackRes.json();
  }
  return res.json();
}
