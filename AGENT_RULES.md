# Agent Rules — IPO Insight App

Read this before writing any code. These rules govern any AI coding agent
working on this repo and take precedence over speed or "making the demo look
finished."

## 0. Golden Rule: this touches real money decisions — never fabricate
This app deals with real financial decisions real people (including the
builder's own family) might reference. Never:
- Hardcode a plausible-looking prediction number instead of running the real
  model
- Fill in fake historical IPO data to pad the dataset — every row in
  `historical_ipos.csv` must trace to a real, checkable source
- Claim a confidence/accuracy figure that wasn't actually measured via
  cross-validation
- Silently substitute mock/placeholder data for a failed scraper fetch
  without visibly flagging it as stale/failed in the UI

If a component isn't working yet, show an honest "not available" or "data
unavailable" state — never a fabricated success. This mirrors the same
principle from the earlier audio project, and matters MORE here because the
stakes (real money decisions) are higher.

## 1. Financial honesty requirements (specific to this domain)
- Every prediction shown to the user must be framed as a historical pattern
  match, never as a guarantee or as direct financial advice. Check UI copy
  against this before shipping any screen.
- Always show a confidence/sample-size signal alongside any prediction — a
  bucket predicted from 3 similar historical cases must visibly look less
  certain than one predicted from 20.
- Never let the model output an unbounded, false-precision number (e.g.
  "predicted gain: 33.7%") — use bucketed categories with confidence, per
  PROJECT_ARCHITECTURE.md §5.
- The disclaimer is not legal boilerplate to bury in a footer — treat it as
  a first-class piece of UI copy, always visible on the verdict card itself.

## 2. Build order discipline
Follow STAGES.md in order. Do not build frontend screens against a model or
API that hasn't been verified with real data. A polished UI showing
plausible-looking fake numbers is the single worst outcome for this project
— worse than a plain UI showing real, honestly-uncertain numbers.

## 3. Verification requirement
After implementing the model or allotment calculator:
1. Run it against real historical data (not synthetic placeholders)
2. Print actual predicted buckets vs actual real outcomes for a held-out
   sample, and actually look at whether it's remotely sensible
3. For the allotment calculator: verify against at least one real, known
   past IPO's actual subscription multiple and confirm the probability
   output is a sane, explainable number (e.g. run the numbers by hand for
   one case and compare)
4. Only report "done" after seeing real, sane values — not after the code
   merely runs without throwing an exception

## 4. Data sourcing rules
- Every row of historical training data must come from a real, identifiable
  public source (Chittorgarh, NSE/BSE bulletins, financial news archives) —
  keep a `source` column or a data-provenance note, so the dataset itself is
  auditable and defensible if a judge asks "where did this come from"
- The scraper must handle failure gracefully (see PROJECT_ARCHITECTURE.md
  §7) — retry with backoff, fall back to last-known-good data, never crash
  the API or return fabricated placeholder numbers on failure

## 5. Scope control
- Build the allotment calculator FIRST and treat it as non-negotiable — it
  is deterministic, always correct, and the safest, most demoable part of
  the app. If time runs out, this alone plus a clean UI around it is a
  legitimate submission.
- The ML prediction piece is secondary and should be clearly labeled as a
  "pattern analysis, educational" feature throughout — both in code
  comments/naming (`pattern_match_bucket`, not `predicted_gain`) and in UI
  copy.
- Frontend animation polish (per DESIGN_BRIEF.md) is the LAST thing built,
  after backend correctness is verified — see PROJECT_ARCHITECTURE.md §9
  build order.
- Do not expand to more than 2 markets/exchanges or add unrelated features
  (portfolio tracking, brokerage integration, etc.) — this is out of scope
  for the timeline, full stop.

## 6. Deployment discipline
- Confirm the deployed Render instance actually serves live data end-to-end
  before considering the project "done" — a working localhost demo that
  isn't actually reachable at the deployed URL is not a complete submission
- Handle Render free-tier cold-start delays gracefully in the frontend
  (loading state) rather than treating a 30-60s wake-up as a bug — but DO
  verify the cold start actually resolves and doesn't time out or error

## 7. Testing checklist before calling any stage "complete"
- [ ] Allotment calculator checked against a real known IPO's actual numbers
- [ ] Model cross-validation score is real, printed, and reported honestly
      (not just training accuracy)
- [ ] Scraper tested against an actual failure case (e.g. temporarily break
      the URL) to confirm graceful degradation, not a crash
- [ ] Every UI screen reviewed against the "does this overclaim certainty"
      question in Rule 1
- [ ] Deployed URL actually loads and functions, not just localhost

## 8. Communication with the user
- If a genuine blocker comes up (can't source enough historical data,
  scraper consistently blocked, model performing at chance level), say so
  plainly and propose the fallback (allotment calculator + honestly-labeled
  "insufficient data" state) rather than quietly shipping something
  fabricated to look complete.

## 9. Strict SEBI Compliance & Future Licensing Mandate
**CRITICAL DIRECTIVE:** This system is being built with the explicit goal of strict SEBI compliance to support future SEBI registration/licensing (e.g., as an RIA or RA).
- The system must NEVER output "half-baked" math, generic estimations, or unverified probability models.
- All algorithms (especially Allotment Engines) must mirror official, real-world SEBI registrar formulas (including technical rejection buffers, category-specific lot limits, fractional rounding floors, and spillover pooling).
- The platform must maintain strict Data Privacy (Zero-Discovery Protocol for PANs) and never persist sensitive financial identities.
- If a feature cannot be built to strict SEBI regulatory standards, it must be omitted rather than approximated. Do not cut corners to make a feature "work" for a demo.
