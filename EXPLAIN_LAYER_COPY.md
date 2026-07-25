# Explain-Layer Copy — Analogies & Plain-Language Text

This is the actual copy for the ⓘ explain-layer pattern defined in
UI_UX_SPEC.md §1. Use this verbatim or as a strong starting draft — don't let
the agent invent generic textbook definitions instead. Each entry follows the
same shape: **raw definition → analogy → what the CURRENT value means.**

Rule for the agent: the analogy is not decoration, it's the primary teaching
tool. If a new metric gets added later, write its analogy in this same style
before shipping it — see AGENT_RULES.md's "every metric needs an explain-layer
entry" rule.

---

## Grey Market Premium (GMP)

**Definition:** The extra amount people are informally willing to pay for a
share before it officially starts trading — an unofficial early guess at demand.

**Analogy:** Think of it like the resale line outside a concert before doors
open. The tickets have a printed face price, but if word gets out the show is
amazing, people start paying scalpers more than face value just to guarantee
a spot. That extra amount people are willing to pay above face price — before
the show has even started — is the GMP. It's not a guarantee the show will be
as good as the line suggests, just a read on how excited the crowd is *right now*.

**Rising GMP:** "More people are joining that resale line and paying more —
excitement is building as the listing approaches."

**Falling GMP:** "Fewer people are willing to pay extra now than a few days
ago — some of the early excitement is cooling off. This doesn't mean it's
bad, just that the crowd's enthusiasm has come down a notch."

**Template for current value:** "GMP has gone from ₹{X} to ₹{Y} over the last
{N} days — {rising/falling/flat}, meaning demand has been {building/cooling/
holding steady}."

---

## Subscription Multiple

**Definition:** How many times more shares people have bid for than are
actually available.

**Analogy:** A bakery has 10 fresh croissants ready this morning, but 30
people are standing in line for them. That's 3x subscribed — three times more
demand than supply. Some people in that line will get a croissant, most won't,
and it's decided by picking names at random, not by who got there first.

**Template for current value:** "This IPO is subscribed {X}x — for every
share available, {X} shares' worth of demand has been placed. {Context: below
5x is modest interest, 5-20x is strong, 20x+ is very hot demand}."

---

## Allotment Odds (Lottery)

**Definition:** The probability your specific application actually gets
shares, given how oversubscribed your category is.

**Analogy:** It's a raffle at a fair. You buy a raffle ticket (your
application/lot), and if there are more tickets sold than prizes available,
the organizers draw winners at random. Buying more tickets (applying for more
lots) doesn't guarantee a win, but the math behind it is exactly like a raffle
draw — the more oversubscribed, the fewer people go home with a prize.

**Template for current value:** "Based on {X}x subscription in your category,
your estimated odds of getting at least one lot are roughly {Y}% — think of
it like {Y} out of 100 raffle tickets like yours winning something."

---

## Offer for Sale (OFS) vs. Fresh Issue

**Definition:** Whether the money raised goes INTO the company (fresh issue)
or to existing owners cashing out their stake (OFS).

**Analogy:** Imagine a bakery selling shares of itself. If it's a **fresh
issue**, the money you pay goes straight into the bakery's till — they use it
to buy new ovens, hire more bakers, open a second location. If it's an
**OFS**, you're not giving the bakery any new money at all — you're buying
out the founder's own stake, and the cash goes straight into THEIR pocket,
not the business. The bakery itself doesn't get richer or better equipped
either way; only who owns it changes.

**Template for current value:** "{X}% of this IPO is OFS — meaning {X}% of
the money raised goes to existing shareholders cashing out, not into the
company's own growth. {If high, e.g. >70%:} That's a notably large share
being sold by insiders, worth factoring in."

---

## Historical Pattern Match / Prediction Confidence

**Definition:** How many genuinely similar past IPOs the estimate is based on,
and how much they agree with each other.

**Analogy:** It's like a weather forecaster predicting tomorrow based on
patterns. If they've seen this exact weather setup happen 30 times before and
it rained 27 of those times, that's a confident forecast. If they've only
seen it happen twice before, the forecast is really more of an educated
guess than a confident prediction — even if the direction (rain) is the same.
This app works the same way: the more genuinely similar past IPOs we have to
compare against, the more weight the pattern deserves.

**Template for current value:** "This estimate is based on {N} historically
comparable IPOs. {If N is small, e.g. <8:} That's a small sample — treat this
as a rough directional read, not a confident forecast. {If N is larger:}
That's a reasonably sized comparison group, giving this pattern more weight."

---

## Listing Gain Bucket (the model's actual prediction)

**Definition:** A range-based estimate of what listing day might look like,
based on historical patterns — never a single guaranteed number.

**Analogy:** This is like a doctor saying "patients with these symptoms
usually fall into a mild, moderate, or severe case" rather than promising
"you will feel exactly this much better by Tuesday." The bucket tells you
the likely ballpark based on what's happened to similar cases before — it's
not a promise about YOUR specific outcome.

**Template for current value:** "Historical pattern suggests a
{loss/flat/moderate gain/high gain} outcome is most likely for IPOs with
this profile — but remember, this is a pattern from the past, not a
guarantee about this listing."

---

## Certainty Spectrum Component (the signature visual)
Every one of the above "current value" templates should ALSO drive the
CertaintySpectrum component from DESIGN_BRIEF.md — map the sample size /
subscription clarity / GMP consistency into where the marker sits on the
grey-to-ink spectrum, so the visual and the copy are always telling the same
story. Never let the copy say "low confidence" while the visual marker sits
near the confident end, or vice versa — check this consistency explicitly
when wiring up each metric.

---

## Tone notes for the agent writing any NEW copy in this style
- Keep analogies grounded in everyday physical things (queues, raffles,
  bakeries, weather) — not abstract finance-on-finance comparisons (don't
  explain GMP using another stock market concept, that defeats the purpose)
- One analogy per metric, used consistently everywhere that metric appears —
  don't invent a new metaphor each time, consistency is what makes it feel
  authoritative rather than random
- Never let the analogy soften or hide the actual risk — e.g. the OFS
  analogy still has to make clear that money isn't going to the company,
  don't write it in a way that makes OFS sound harmless
- End every explain-layer entry on the CURRENT value in context, never just
  the dictionary definition — the context is what makes it feel intelligent
