# The model

This document is the analytical framework behind every indicator, threshold and report in
this repository. It is also the system prompt for the quarterly narrative. Nothing in the
code should contradict it; if the two drift, this document wins and the code is wrong.

## 1. The question is not "will they pay"

A government that issues its own currency and borrows in that currency cannot be forced into a
nominal default. The central bank can always create the money and absorb the debt. It does
not even need to buy at auction: primary dealers buy, the central bank buys from dealers, and
if dealers run out of balance sheet the central bank repo-finances them or the law is changed.
Nominal payment is therefore never in doubt for such a sovereign, and any analysis that starts
from "can they pay?" is answering the wrong question.

The right questions are:

1. **Is the debt trajectory sustainable?**
2. **If not, who pays, and through which channel?**

There are only three exits from an unsustainable trajectory:

- **(a) Real fiscal correction.** Primary surpluses large enough, for long enough, to bend the
  path. Politically rare without outside help (a falling currency, an easing central bank, a
  booming trading partner).
- **(b) Financial repression and inflation.** Holders are made to accept returns below
  inflation, so the real value of the stock is eroded. The transfer runs from bondholders and
  savers to the state.
- **(c) Currency collapse, hyperinflation, or formal default.** The disorderly version of (b),
  or the only version available to a state that cannot print what it owes.

Developed sovereigns with their own currency almost always end in (b). The model's job is to
say which countries are on that path, how far along they are, and when the regime is shifting.

## 2. The arithmetic

The change in the debt ratio is mechanical:

```
Δ(debt/GDP) ≈ (r − g) × (debt/GDP) − primary_balance
```

- `r` is the **average effective interest rate on the outstanding stock**: interest paid in the
  year divided by the debt stock at the start of the year. It is not the market yield.
- `g` is **nominal** GDP growth. Inflation counts fully, which is why exit (b) works.
- `primary_balance` is the budget balance excluding interest, surplus positive.

If `r > g` and the primary balance is in deficit, the debt ratio rises with no further decisions
required. Stock-flow adjustments (bank bailouts, valuation effects, below-the-line financing)
make the actual change differ from the identity, and the gap is itself a diagnostic: a country
whose debt rises faster than the identity predicts is hiding something off budget.

## 3. The lag: average versus marginal

Most sovereign debt is fixed-coupon. The average rate `r` therefore moves slowly, converging
towards the marginal market yield only as the stock rolls over. Roughly `1 / average_maturity`
of the stock reprices each year, plus all new issuance to fund the deficit.

The gap between the current average rate and the marginal yield is **interest cost already
committed**. It will show up in the budget whether or not anything else changes. So the
informative quantity is not today's `r` but **forward r**: the average rate the stock will
carry in N years if yields stay where they are and issuance continues on its current pattern.
Forward `r − g` is the model's main trajectory variable.

A country can look fine on current `r − g` and be on an unsustainable path on forward `r − g`.
The reverse also happens: a country that locked in long cheap debt can run a primary deficit
for years while the market yield is well above its average coupon.

## 4. The sorting variable: captivity

Debt/GDP on its own is almost useless as a crisis predictor. Russia defaulted at about 55% of
GDP, Argentina at about 50%, Turkey had a currency crisis at about 30%. Japan has sat above
200% for a generation without one, and the UK carried 180% through the 1920s.

What separates these cases is whether the holders of the debt can leave. **Captivity** is the
degree to which the holder base has no practical exit:

- share held by residents versus non-residents;
- share held by the central bank (the ultimate captive buyer);
- average maturity: short debt means holders are effectively free, since they are repaid soon
  and choose whether to come back;
- regulatory captivity: banks, pensions and insurers compelled by liquidity, solvency and
  collateral rules to hold government paper;
- capital controls;
- reserve-currency status: for the United States the rest of the world is the captive holder;
- the size of the domestic savings pool relative to the debt.

Captivity does not make debt sustainable. It determines **how** an unsustainable path resolves:
slowly through repression, or quickly through flight.

## 5. The quadrants

Cross the trajectory question with the captivity question:

|                                                         | Holders captive                                                                                   | Holders free                                                                                   |
|---------------------------------------------------------|---------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| **Sustainable** (forward r ≤ g, or primary surplus)     | Nothing to see. Germany, Switzerland.                                                             | Fine until the trajectory turns. Australia, Canada.                                            |
| **Unsustainable** (forward r > g with primary deficit)  | **Japan equilibrium.** Slow grind: repression, negative real rates, currency erosion, for decades. Japan, US, UK, Italy, France. | **Crisis within a cycle.** Currency collapse or default; the threshold can be 30–50% of GDP. Argentina, Turkey, Russia 1998, Greece. |

The two unsustainable cells have opposite time signatures. The captive cell is a decades-long
transfer that is easy to predict in direction and nearly impossible to time. The free cell
resolves within a business cycle. The indicators exist to catch movement between cells and
along the stage sequence below.

## 6. The stages of a spiral

Each stage has observable tells. The code's `stage_estimate` is a rule-based reading of these
tells (rules in `config/stages.yaml`).

0. **Fuel.** A persistent primary deficit that does not close in expansions.
1. **Trigger.** `r` rises above `g`. Usually because the central bank hikes against inflation,
   not because buyers vanish. Tell: marginal yield above the average coupon, so the interest
   bill is rising on autopilot.
2. **Pricing.** The market starts charging for the risk: term premium rises, breakevens rise,
   auction tails widen.
3. **Choice.** The central bank is forced to choose between the currency and the bond market.
   Tells: hikes pause with inflation still above target; purchases justified as "market
   functioning" rather than policy.
4. **Fiscal dominance.** The bank chooses the bond market. Policy rate below inflation; the
   central bank's share of the stock rising; balance sheet growing faster than nominal GDP;
   the treasury shortening issuance into bills.
5. **Flight.** The currency falls without further easing; gold at record highs in local terms;
   capital controls and repression intensify.
6. **Resolution.** One of three: a real fiscal correction (which has historically needed a
   falling currency, an easing central bank and a booming trading partner, as in Canada 1994–95
   and Sweden 1992–94); a repression grind (UK and US after 1945, Japan now); or hyperinflation
   and default.

Stages are not strictly sequential and countries can sit in one for years. The tells are
there to catch transitions, which is what the model can actually predict.

## 7. What the model predicts, and how confidently

- **Direction, long run: high confidence.** For unsustainable-captive sovereigns: negative real
  returns on nominal bonds, currency erosion against hard assets, intensifying repression, and
  central banks that tolerate above-target inflation at every forced choice.
- **Timing: low confidence.** Captive systems persist for decades. Nothing here is a timing
  signal on its own.
- **Regime transitions: moderate confidence.** Movement between quadrants and along stages is
  observable in the tells, with lead times that the backtest measures rather than assumes.

Portfolio implications follow directly. Long nominal bonds of unsustainable-captive sovereigns
are the asset that gets taxed. Real assets, equities with pricing power and gold are on the
other side of the transfer. The currency, not the bond yield, is the pressure gauge: a yield
can be pinned, a currency cannot be pinned without reserves. Expect the central bank to
surprise dovish whenever it is forced to choose.

## 8. Monetary regime changes the analysis

Every country in `config/universe.yaml` carries a `monetary_regime`:
`sovereign_float`, `currency_union_member`, `pegged`, or `dollarised`. The claim in section 1
("can always pay nominally") holds **only for `sovereign_float`**. The other regimes change the
analysis in four ways.

**Union members cannot print.** Germany, France, Italy, the Netherlands and Greece borrow in a
currency they do not individually issue. They can miss a coupon (Greece 2012), so genuine
default is a live resolution branch for them. They also cannot inflate away their own debt;
the repression exit exists only at bloc level, through the ECB, and the bloc's inflation is
shared with members who did not need it.

**Captivity for a union member is political, not structural.** The decisive captive holder is
the ECB, and the ECB stays captive only as long as the other members tolerate purchases skewed
towards the stressed member (PEPP reinvestment flexibility, the Transmission Protection
Instrument). The captivity score therefore includes a `central_bank_control` term: a country
with its own central bank gets full credit for central-bank holdings, a union member gets
partial credit, a dollarised country gets none. The weights are configuration.

**The pressure gauge swaps.** For floaters the gauge is the currency and gold in local terms.
For union members and pegs it is the **spread to the anchor** (BTP–Bund, OAT–Bund) and, inside
the euro area, TARGET2 balances. The euro's own exchange rate tells you about the bloc, not
about the member. The code computes both the bloc-level identity (the ECB's constraint: can the
euro area as a whole print its way out) and the member-level identity (who gets squeezed within
the bloc).

**Stage rules differ.** A union member at stage 3 does not show a falling currency. It shows a
widening spread and a central bank announcing a backstop. Stage 5 for a member is a spread
blow-out with TARGET2 flight, not a currency collapse. For a peg, stage 5 is reserve loss and
a parallel-rate premium. `config/stages.yaml` carries these as `regime_overrides`.

Historical regimes matter for the backtest. Italy in 1992 was a peg (ERM), not a union member;
Argentina 1991–2001 was a currency board; Sweden 1992 was an ECU peg. The universe file records
`regime_history` so each event is read under the regime in force at the time.

## 9. How the code maps to this document

| Model concept                      | Indicator block (see `docs/INDICATORS.md`)                                  |
|-----------------------------------|------------------------------------------------------------------------------|
| Arithmetic, lag, forward r         | Trajectory block: `r_effective`, `g_nominal`, `avg_coupon_gap`, `forward_r_5y`, `debt_gdp_projection_10y` |
| Captivity                          | Captivity block: holder shares, maturity, bill/linker share, `captivity_score` |
| Stage tells                        | Pressure block: real policy rate, central-bank share change, issuance shortening, currency and gold, spread to anchor |
| Quadrants and transitions          | `trajectory_unsustainable`, `holders_captive`, `quadrant`, transition flags |
| Confidence claims                  | Backtest: lead times, false positives, forward real returns by quadrant, forward-r accuracy |
