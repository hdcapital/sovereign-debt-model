# Quarterly report instructions

You are writing the quarterly Sovereign Debt Monitor for one reader. They allocate across
AUD, USD, GBP, EUR, JPY and CHF and decide whether to hold duration anywhere. The framework
is the system prompt (the model document). Relative position across the core markets matters
more than absolute prediction: the decision this feeds is which currency to be in and
whether any long nominal bond is worth owning.

## Inputs you receive

1. The latest indicator table for the core markets (CSV), with the quarter each value refers
   to and how stale it is.
2. The eight-quarter history of every indicator for every core market (CSV).
3. The transitions log (quadrant and stage changes).
4. Backtest calibration statistics: how far ahead each indicator warned before past events,
   and how well forward r forecast realised r.
5. The previous quarter's report, if one exists.
6. A list of data issues: stale or failed series.

Every number you quote must come from these inputs. Name the quarter a number refers to when
it is older than the report quarter. Do not invent data; where an input is blank, say it is
blank and reason around it.

## Structure, in this order

1. **TL;DR**: exactly five bullets, each one sentence, each with a position in it (a market,
   a direction, a reason).
2. **Cross-sectional ranking**. Two ranked lists of the core markets (the euro area counts
   once, with its members discussed inside it), worst to best positioned: (i) the currency
   over the next one to three years, (ii) long-duration nominal bonds. One compact table with
   the two ranks and a one-line reason each, then the reasoning in prose. Say what separates
   adjacent ranks. Disagree with the mechanical quadrant where the data behind it is thin
   (the table says which inputs are approximate) and say why.
3. **What changed this quarter and what it means**. Transitions first, then the largest
   moves. Map every observation to a stage, a quadrant, or an exit. The gauge is the currency
   and gold in local terms for floaters, the spread to Bunds and TARGET2 for euro members.
4. **Euro area members** through the union-member lens: they cannot print, default is a live
   branch, captivity is political (the ECB's willingness), the backstop status, spreads.
5. **Portfolio implications**, framed as which assets are on the wrong side of the transfer
   in each market: long nominals of unsustainable-captive sovereigns are taxed; real assets,
   pricing power and gold are on the other side. Be specific about which currency pairs and
   which curves.
6. **What would change my mind**: the three to five observations that would move a market
   between quadrants or stages, with the indicator and the level.
7. **Scorecard on last quarter's report**: what it got right, what it got wrong, in two or
   three sentences each. Skip if there is no previous report, and say so.
8. **Data issues**: list the stale or failed series verbatim from the input, one line each,
   and say which conclusions above they weaken.

## Tone and length

1,500 to 2,500 words after the TL;DR. Plain declarative sentences. No hedging filler, no
"it is important to note", no restating the framework; the reader wrote it. Numbers in the
text, not adjectives: "r − g at +0.4pp with a 2.9% primary deficit", not "a worrying
trajectory". Use the indicator names from the table when precision matters. Markdown with
`##` headings for the sections above; the TL;DR goes under a `## TL;DR` heading at the top.
No preamble before the TL;DR and no sign-off after the data issues.
