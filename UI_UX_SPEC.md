# UI/UX Specification — IPO Insight App

## 0. Design Thesis
Two people use this app: someone who reads balance sheets for fun, and someone's
dad who just wants to know "should I put money in this or not." The entire UI
is built around **one dataset, two lenses** — never two separate apps, never a
dumbed-down version that hides real numbers from the pro user. Every metric
has a plain-language explanation ONE CLICK away, never forced, never hidden.

This is the single most important UX decision in this app. Get this right and
everything else — the whole "explainable AI" pitch to judges — falls out of it
for free.

## 1. Core Pattern: The Explain Layer
Every metric, number, or prediction on screen follows the same interaction
pattern:

```
┌─────────────────────────────────┐
│  GMP: ₹155  (32% premium)    ⓘ  │  ← the raw metric, always visible
└─────────────────────────────────┘
         │ (tap/hover the ⓘ)
         ▼
┌─────────────────────────────────────────────────┐
│ Grey Market Premium — the price people are        │
│ informally willing to pay above the official issue │
│ price, before the stock officially lists. Think of │
│ it as an early, unofficial guess at demand.         │
│                                                      │
│ ↓ Trending down from ₹203 → ₹155 over the last 4    │
│ days — interest is cooling somewhat.                │
└─────────────────────────────────────────────────┘
```

Rules for this pattern:
- The raw number/metric is ALWAYS shown first, full precision, no dumbing down.
- The ⓘ expands inline (not a separate page/modal that loses context) —
  accordion-style, pushes content down, doesn't cover the screen.
- Every explanation ends with what the CURRENT VALUE means in context (trend,
  comparison to typical range), not just a textbook definition. This is what
  makes it feel intelligent rather than like a glossary.
- No metric ships without an explain-layer entry. If the agent adds a new
  metric to the model, it must add its explanation text in the same PR/commit
  — treat this as non-negotiable, not a "polish later" item.

## 2. Two Display Modes (not two apps — one toggle)
A single top-of-screen toggle: **Simple / Detailed**

- **Simple mode** (default for first-time visitors): shows the verdict, the
  headline numbers (GMP%, subscription multiple, allotment odds, predicted
  gain bucket), each with the explain-layer available but collapsed. Visual
  weight goes to the verdict card (§4).
- **Detailed mode**: same page, same layout, but reveals additional
  technical panels — feature importances behind the prediction, the full
  peer-comparison table, confidence intervals, raw model output. Nothing is
  a different screen; Detailed mode reveals MORE on the same page, it doesn't
  navigate anywhere else. This keeps one mental model for both audiences and
  is dramatically less work than building two separate UIs.

Toggle state persists across the session (don't reset it on every page nav).

## 3. Visual Design Direction
Financial apps default to navy/dark-green/gold and it reads as generic
fintech-template. Differentiate deliberately:

- **Base palette**: warm off-white / near-black background (not stark white,
  not pure black) — pick ONE accent color that isn't finance-cliché navy or
  green (e.g. a deep amber/terracotta, or an indigo/violet) for primary
  actions and the verdict card. Use red/green ONLY for actual gain/loss
  signals (this is the one place financial-app convention should be kept,
  since red=bad/green=good is genuinely load-bearing here, not decorative).
- **Typography**: a serif or slab-serif for headline numbers (gives it a
  "financial publication" gravitas — think Bloomberg/FT, not "startup SaaS
  dashboard") paired with a clean grotesque sans for body/labels. Numbers
  should feel authoritative, not playful.
- **Data density**: pro users want tables and precise numbers; don't hide
  them behind excessive whitespace. But group related metrics into clear
  cards with breathing room between GROUPS, not between every individual
  number.
- Refer to `/mnt/skills/public/frontend-design/SKILL.md` conventions when the
  agent builds this — don't let it default to generic Bootstrap-looking
  components.

## 4. Screen: The Verdict Card (hero of the whole app)
This is what a user sees within 2 seconds of opening the app for any given
IPO. It must answer "should I invest" — carefully worded, never as direct
advice, but as a synthesized read of the signals.

```
┌───────────────────────────────────────────────────┐
│  INDO-MIM LIMITED                     🟡 MODERATE   │
│  Precision Engineering · Mainboard                  │
│                                                       │
│  Historical pattern match: IPOs with similar GMP     │
│  trend + subscription level have shown MODERATE      │
│  listing gains (15-35%) in 68% of comparable cases    │
│                                                       │
│  ⚠️ Cooling GMP trend (₹203→₹155) — worth watching    │
│  ⚠️ Heavy OFS (87% of issue) — promoters cashing out  │
│  ✓  Subscription steady at 3.07x                      │
│                                                       │
│  Allotment odds for your application: ~XX%           │
│                                                       │
│  [See how we calculated this ⌄]                       │
│                                                       │
│  This is a pattern-based educational estimate, not     │
│  financial advice. Past patterns don't guarantee       │
│  future results. You decide.                           │
└───────────────────────────────────────────────────┘
```

Verdict categories (never binary yes/no — always a graded, honest signal):
🟢 Strong historical pattern match · 🟡 Moderate / mixed signals ·
🔴 Weak historical pattern match · ⚪ Insufficient comparable data

The "insufficient data" state is IMPORTANT to build and show proudly, not
hide — it's proof the model isn't overconfident, and it's a great talking
point with judges (see AGENT_RULES-style honesty principle carried over from
the audio project).

The disclaimer line is ALWAYS visible on the verdict card itself, not buried
in a footer — this is both an ethical requirement and, framed right, a
credibility signal to judges.

## 5. Screen: Allotment Odds Calculator
Standalone, usable even without picking a specific IPO — this is your
guaranteed-solid, dad-can-trust-it feature (see prior conversation). Give it
visual prominence, maybe its own tab, since it's 100% deterministic math and
the safest thing to headline.

- Inputs: category (Retail/sNII/bNII), number of lots applied, subscription
  multiple for that category
- Output: probability of allotment, shown as both a percentage AND a visual
  (e.g. a simple dot-grid or gauge — "roughly 1 in 4 applicants like you get
  shares") — the visual matters here because probability is genuinely hard
  for non-technical users to internalize from a number alone
- Explain layer: how lottery allotment actually works, in the plain-language
  style already established in this conversation

## 6. Screen: Peer Comparison / Backtest
Table + visual, not just a table:
- Each row: peer IPO (e.g. Gala Precision, Poojaa Precision) with subscription,
  GMP trend, predicted bucket (if run through the model retroactively), ACTUAL
  outcome
- A simple scatter or bar chart: predicted vs actual, so the model's
  track record is visually obvious at a glance, not something you have to
  read row by row
- This screen is your credibility proof — treat its clarity as high priority

## 7. Live/Refreshed Data Indicator
- Small, persistent "Last updated: 4 min ago · refreshing every 15 min"
  indicator, not a fake "LIVE 🔴" badge implying tick-by-tick streaming you
  don't have
- Manual refresh button always available for the user to force an update
- If a data source fetch fails, show the last known good data WITH a visible
  "couldn't refresh, showing data from [time]" state — never fail silently or
  show blank/broken UI

## 8. Explainability for the Prediction Itself (Detailed mode)
When showing WHY the model predicted a given bucket, use a simple horizontal
bar list of contributing factors, plain-language labeled:

```
What influenced this prediction:
GMP trend (cooling)         ████████░░  strong negative influence
Subscription level (3.07x)  █████░░░░░  moderate positive influence
Sector historical pattern   ██████░░░░  moderate positive influence
Issue size                  ███░░░░░░░  slight negative influence
```

Don't show raw SHAP values or model internals to Simple-mode users — this bar
list format is legible to both audiences, so it can actually live in Simple
mode too, just smaller/collapsed. This is a good candidate to NOT gate behind
the Detailed toggle, since it's genuinely the most compelling "wow, it's
explainable" moment for judges.

## 9. Tech Recommendation

**Frontend:** React + Vite + Tailwind for layout, **Framer Motion** for all
transitions/reveals/accordion animation (explain-layer expand, verdict card
mount, mode toggle), **Recharts** or **Visx** for charts — both animate
transitions when underlying data changes with far less custom code than raw
D3. This is what actually produces the "fluid" feel: consistent easing curves
and layout animations from Framer Motion, not one-off CSS transitions
scattered per component.

**Backend:** FastAPI serving clean, versioned JSON endpoints (e.g.
`/api/ipo/{id}/verdict`, `/api/ipo/{id}/prediction-factors`,
`/api/allotment-odds`). The model, the scraper/refresh job, and the allotment
math all live behind this API — the frontend never touches them directly, it
only ever renders JSON. This separation is deliberate: it means frontend
animation work and backend model work can proceed independently, and a
frontend bug can never corrupt the data pipeline.

**Build order — backend correctness BEFORE frontend animation polish.**
A stunning animated chart on top of a wrong or undercooked prediction is a
worse outcome than a plain chart on top of a correct one — judges will ask
you to explain the numbers, not the easing curve. Concretely:
1. Get the model + allotment calculator + scraper producing correct,
   verified JSON output first (reuse verification discipline from
   AGENT_RULES.md — print and sanity-check real values before building UI
   around them)
2. THEN build the React frontend against that known-good API
3. Animation polish (Framer Motion transitions, chart animation tuning) is
   the LAST layer added, and the safest thing to keep iterating on right up
   to the deadline — visual bugs are low-stakes and fast to fix, unlike a
   subtly wrong prediction

If time is short, a working React UI with default/minimal animation beats an
elaborate animated UI wired to an unfinished or unverified backend. Cut
animation complexity before cutting backend correctness time.

## 10. Non-negotiable disclaimer placement
- Verdict card (always visible, not collapsed)
- App header/footer (persistent across all screens)
- First-load modal/banner, dismissible but shown once per session, stating
  plainly this is an educational tool built on limited historical data, not
  financial advice, and real investment decisions should consider more than
  this tool alone

## Priority order if time runs short (last-resort scope cut)
1. Verdict card + disclaimer (non-negotiable, ship this no matter what)
2. Allotment odds calculator (your safest, most solid feature)
3. Explain-layer on at least the 3-4 headline metrics
4. Peer comparison screen
5. Simple/Detailed toggle
6. Live-refresh polish
7. Feature-importance bar chart
Cut from the bottom of this list first, never from the top.
