# Design Brief — IPO Insight App

Read this before writing any frontend code. This is not optional polish — it's
the difference between the app looking like a hackathon Bootstrap template and
looking like something a judge remembers.

## Calibration: what to actively avoid
AI-generated frontends right now cluster around a few unmistakable tells:
1. Warm cream background (#F4F1EA-ish) + high-contrast serif + terracotta accent
2. Near-black background + single acid-green or vermilion accent
3. Broadsheet layout — hairline rules, zero border-radius, dense newspaper columns
4. Generic fintech navy/teal gradient hero sections with a big rounded "Get Started" button
5. Purple-to-blue gradients on buttons/cards (the single most obvious "AI made this" signal in 2025-2026 SaaS templates)
6. Emoji used as icons instead of a real icon set
7. Every card the same rounded-corner, same-shadow, same-padding treatment with no hierarchy

**Do not default to any of these.** If the agent's first instinct matches one
of the above, revise it before writing code.

## The concept
This app's subject matter has a built-in visual idea nobody's using: the
domain literally centers on **"grey market"** — an informal, unofficial signal
that exists in the fog before something becomes real and certain (the actual
listing). And the app's entire ethical stance is about **honest uncertainty**
— we show confidence, not false certainty. Those two things point to the same
design language: a **grey-to-ink certainty spectrum** as the visual backbone
of the whole app, not just a metaphor in copy.

## Design Tokens

**Color** (named, 6 values):
- `ink` `#14171C` — near-black, used for primary text and high-confidence states, NOT as a background
- `paper` `#F3F1ED` — warm light neutral background (lighter/greyer than cream, not the AI-tell #F4F1EA — verify against it directly, shift cooler)
- `fog` `#C7C6C2` — mid-grey, the "uncertain/unknown" end of the certainty spectrum, used for low-confidence states and dividers
- `signal-amber` `#B8863B` — muted brass/ochre, NOT saturated gold — used sparingly for the verdict accent and primary CTAs, this is the one warm accent in the whole palette
- `risk-rust` `#9C4A3B` — desaturated red-brown, used ONLY for actual negative signals (cooling GMP, high OFS warning) — never decorative
- `confirm-moss` `#5C6E4F` — desaturated green, used ONLY for actual positive signals — never decorative

Notice: no pure red/green (#FF0000/#00FF00 style), no purple, no gradient
buttons. The palette reads "financial publication," not "SaaS landing page."

**Typography** (2+ roles, deliberately NOT Inter+generic-serif):
- Display/headline face: **Fraunces** (variable serif, has real personality —
  slightly quirky ink-trap details at large sizes) for the verdict card
  headline and hero numbers only — used with restraint, not everywhere
- Body/UI face: **Space Grotesk** — geometric but slightly unusual, avoids
  the extremely-common Inter/Helvetica-clone look
- Data/numeric face: **IBM Plex Mono** for ALL numbers — prices, percentages,
  GMP figures, odds. This is the signature typographic choice: monospaced
  figures give every number a ticker-tape, financial-terminal authenticity
  that a normal sans-serif number never achieves, and it makes tables of
  numbers align cleanly for free.

**Layout concept:**
The verdict card sits left-aligned in the top third of the viewport, NOT
centered (centered hero content is a generic-template tell). To its right, at
desktop width, the live GMP trend chart occupies the remaining space —
so the very first thing visible is "the claim" (verdict) next to "the
evidence" (chart), side by side, cause and effect. On mobile this stacks
vertically, verdict first.

```
┌─────────────────────────┬───────────────────────────┐
│  VERDICT CARD             │   GMP TREND (live chart)    │
│  (left-aligned, Fraunces  │   animated line, certainty   │
│  headline, ink/amber)      │   spectrum shading beneath   │
├─────────────────────────┴───────────────────────────┤
│  Explain-layer accordion strip (full width)             │
├───────────────┬───────────────┬─────────────────────┤
│  Allotment      │  Peer backtest │  Prediction factors    │
│  odds (mono      │  table/chart   │  (mono bars)            │
│  numerals)       │                │                         │
└───────────────┴───────────────┴─────────────────────┘
```

## Signature element: The Certainty Spectrum
This is the one thing the app should be remembered by, used consistently
everywhere a probability, confidence, or prediction appears — the verdict
badge, allotment odds, prediction confidence, peer-match strength:

A horizontal bar, `fog` grey on the left fading to `ink` (or `signal-amber`
for positive predictions) on the right, with a small marker dot positioned
along it via a spring animation (Framer Motion) when it loads or updates.
Label the two ends in plain language specific to context — e.g. "Few similar
cases" → "Many similar cases," or "Low confidence" → "High confidence" — never
just "0%" to "100%" with no context, since a bare percentage is exactly the
false-certainty problem this app is designed to avoid.

This single component, reused everywhere, is what makes the app feel
designed rather than assembled from a component library — and it directly
embodies the app's actual ethical stance (see AGENT_RULES.md), which is a
genuinely good story to tell judges: the visual language IS the honesty
principle, not decoration bolted onto it.

## Buttons — making them feel premium
Generic AI-gen buttons: gradient fill, heavy drop shadow, scales up 1.05x on
hover, rounded-full pill shape. Avoid all four defaults simultaneously.

Instead:
- Solid `ink` fill, `paper` text, for primary actions — no gradient
- Border-radius 6-8px, not full-pill, not sharp 0px — a restrained middle
- On hover: background shifts to `signal-amber`, text stays high-contrast,
  transition 150-200ms ease-out — no scale transform, scale-on-hover reads
  as generic and slightly cheap at this point
- On press/active: a subtle 1px inset shadow or slight brightness drop, so
  it feels physically pressed, not just color-swapped
- Secondary buttons: `ink` 1px border, transparent fill, fill-in on hover
- Disabled state: reduce to `fog` with 50% opacity text, never just a dimmed
  version of the same gradient

## Motion principles
- Page/section load: staggered fade+rise for the verdict card contents
  (headline first, then metrics, then disclaimer) — 60-80ms stagger, not
  simultaneous, not a long sequential crawl
- Explain-layer accordion: height auto-animate with Framer Motion's
  `layout` prop, 200ms, no bounce — bounce reads as playful/gimmicky, wrong
  register for a financial tool
- Certainty spectrum marker: spring physics (`type: "spring", stiffness:
  120, damping: 14` as a starting point) when the value updates — this is
  the one place a slightly bouncy, alive motion is appropriate, since it's
  the signature element and deserves personality
- Chart data updates (on refresh): animate the line/point transition, don't
  just snap-redraw — Recharts/Visx support this natively
- Respect `prefers-reduced-motion` — disable non-essential motion for users
  who've set that OS-level preference

## Self-critique checklist before calling the frontend "done"
- [ ] Does any button use a gradient fill? → remove it
- [ ] Is the hero content centered? → it shouldn't be, per the layout concept
- [ ] Are numbers set in the same font as body text? → they should be
      IBM Plex Mono, not the body sans
- [ ] Does every card look identical (same radius/shadow/padding)? → the
      verdict card should have more visual weight than a data table
- [ ] Would a screenshot of this page, with the logo removed, still look
      distinctly like THIS app and not a generic dashboard template? If no,
      revise before moving on.
