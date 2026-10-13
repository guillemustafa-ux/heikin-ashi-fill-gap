# Heikin Ashi Fill Gap

Open-source TradingView indicator (Pine Script v6) that measures, on a standard chart, how far the Heikin Ashi prices of the chart symbol sit from its real prices on every confirmed bar, how often the HA open falls outside the bar's traded range, and how much better the same signal reads when its orders fill at HA prices instead of real ones.

Published on TradingView: not yet. The script URL goes here after publishing.

## What it measures

On a Heikin Ashi chart a strategy fills its orders at the chart's prices unless its "Fill orders using standard OHLC" option (`fill_orders_on_standard_ohlc` in `strategy()`) is on. The HA open is the midpoint of the previous HA bar's open and close, and the HA close is the mean of the bar's real open, high, low and close, so in a trend both lag the real price: a long opened at an HA open buys below where the market was trading, a position closed at an HA open sells above it, and the same signal reads better than it would with real fills. The indicator runs on a standard chart and:

1. **Requests the HA prices of the chart symbol.** One `request.security` call with `ticker.heikinashi(syminfo.tickerid)` on a standard chart, the chart timeframe, the tuple `[open, close]`, `gaps = barmerge.gaps_off` and `lookahead = barmerge.lookahead_off`. The chart's ticker id keeps its extended session, dividend adjustment and currency conversion, so the HA bars are built from the same real bars the chart shows.
2. **Measures the gaps on every confirmed bar.** `gapOpenPct = (haOpen - open) / open * 100` and `gapClosePct = (haClose - close) / close * 100`; mean and maximum of |gap| with the bar of the maximum.
3. **Counts the bars where the HA open is outside the traded range.** `haOpen < low or haOpen > high`: a fill at that HA open is at a price that never traded in the bar. The HA close is `(open + high + low + close) / 4` and always lies inside the range, so only the HA open can leave it.
4. **Runs one signal under both fill prices.** The HA color flip (green = `haClose > haOpen`; a change of color on a confirmed bar is the signal, the fill is the next bar's open) feeds two ledgers of the same trades: R fills at the real `open` of the fill bar, H fills at the HA open of the same bar. Per closed trade, return = direction × (exit / entry − 1) × 100 and flattery = H return − R return.

It does not read the code of any strategy. It shows what the HA prices of this symbol would have done to this signal on the loaded chart.

## Counting rules

The counters update only on confirmed bars (`barstate.isconfirmed`) of a standard chart (`chart.is_standard`) for which the request returned HA values, in this order:

1. **Fill of the previous bar's signal.** If a flip is pending, the position against it closes at this bar's `open` (ledger R) and at this bar's HA open (ledger H); then a position opens in the flip's direction, longs in both modes, shorts only in "Long and short". A closed trade adds to: trades, wins per ledger (return > 0), sum of returns per ledger (a simple sum in percent points, not compounded), sum of flattery, count of trades with flattery > 0, and the maximum and minimum flattery with the open time of the exit bar.
2. **Gap measures.** Bars counted, the sums of |gapOpenPct| and |gapClosePct| behind the means, the maxima with the open time of the bar where they were measured, the count of bars with the HA open outside the traded range, and the real open, HA open and gapOpenPct of the bar for the "Last confirmed bar" row.
3. **This bar's flip.** The HA color (green or not green) is compared with the previous confirmed bar's; a change is stored as the pending signal for the next bar. The first measured bar has no previous color and gives no signal.

Modes: "Long only" (default): a flip to green opens a long, a flip to red closes it. "Long and short": a flip to green closes any short and opens a long, a flip to red closes any long and opens a short.

Consequences:

- The realtime bar is never in the counts until it confirms. The table is drawn on the last bar on every tick, the counters are not. A trade is recorded on the confirmation of its fill bar, one bar after the flip.
- A position still open on the last bar is not counted; the header says so.
- No commission or slippage in either ledger: the measure is the fill price alone.
- On a non-standard chart (Heikin Ashi, Renko, Kagi, Line break, Point & figure, Range) the table shows "Use a standard chart" and nothing is counted or shaded. The request still runs, as Pine requires `request.security` at global scope; there the ticker goes through `ticker.standard` first, which strips the chart-type modifier so the call stays valid. On a standard chart the ticker id is used as is: `ticker.standard` also strips the extended session, dividend adjustment and currency conversion, and the HA bars would then come from other real bars than the chart's.
- No other `request.*` call, no look-ahead, no recalculation of a count after its bar has closed. The shading of outside-range bars is drawn on every bar, including the realtime one, whose high and low are still forming: a tint there can disappear as the bar's range widens.

## Settings

| Input | Default | Meaning |
| --- | --- | --- |
| Signal | Long only | Long only or Long and short, as above. |
| Shade bars where the HA open is outside the traded range | on | Red tint on the bars where the HA open is below the low or above the high. |
| Table position | Bottom right | Four corners. |
| Table text size | Small | Tiny, Small or Normal. |

## How to read the table

| Row | Meaning |
| --- | --- |
| Header | Symbol, timeframe and confirmed bars counted; signal mode, closed trades, and whether a position is open on the last bar (not counted). |
| HA open vs real open | Mean and maximum \|gap\| in percent of the real open, and the bar of the maximum. |
| HA close vs real close | Same for the close. |
| HA open outside the traded range | Bars and their share of the bars counted. Red when there is at least one, green when there is none and at least one bar was counted. |
| Real fills | Total return (simple sum of per-trade returns, in percent points) and win rate of the trades filled at the real open. |
| HA fills | The same trades, filled at the HA open. |
| Flattery · HA minus real | Total: HA fills total minus Real fills total, taken from the two totals as shown, so the identity holds on the printed figures (it is the sum of per-trade flattery up to that rounding). Mean per trade, and share of trades where the HA fill reads better. Red when the total is positive, green otherwise. |
| Largest flattery | Largest and most negative flattery, each with its exit bar. |
| Last confirmed bar | Real open and HA open at the symbol's precision, and the gap in percent, for a hand check against the HA chart. |

The footer reminds that the numbers are counts on confirmed bars and names the timezone of the dates (`syminfo.timezone`). Percentages are shown with two decimals, rates with one.

## Files

- `heikin_ashi_fill_gap.pine`: the indicator.
- `TRADINGVIEW_PUBLICATION.md`: title, description text and checklist for publishing.
- `tools/simulate_ha_fill_gap.py`: standard-library Python simulation of the measures and both ledgers on a seeded synthetic hourly series of 2,000 bars (`python -I tools/simulate_ha_fill_gap.py`). It prints the shape of the result to expect: HA fills reading better than real fills in a trending series.
- `LICENSE`: MIT.

## Check it yourself

1. Add the indicator to BINANCE:BTCUSDT on 1 hour, standard candles, from the Pine Editor and confirm it compiles without errors or warnings.
2. Check the identities: in both fill rows `wins <= closed trades`; `Flattery total = HA fills total - Real fills total`; `HA open outside the traded range <= bars` in the header; the shaded bars are the outside-range bars.
3. Hand check the "Last confirmed bar" row: note its real open and HA open, switch the chart to Heikin Ashi, hover the same bar and read its open. It must match the HA open at the symbol's precision. Switch back to standard candles.
4. Switch the chart to Heikin Ashi: the table shows only "Use a standard chart" and no bar is shaded.
5. To check for look-ahead, use Bar Replay: start a few hundred bars back and step forward. Counts change only when a bar closes, a trade is recorded only on the bar after its flip, and a shaded bar keeps its tint once closed.
6. Compare with `tools/simulate_ha_fill_gap.py`. The symbol differs, so the numbers will too; what should carry over is the shape: HA fills with a higher total and win rate than real fills, a positive flattery total, HA reading better in most trades, and a mean |gap| of the open larger than the mean |gap| of the close. Output on 2026-10-13:

```
Series: 2000 hourly bars, seed 7, 5 drift regimes, first open 100.00, last close 159.00

Long only  (2000 bars, 230 closed trades, no position open at the end, not counted)
  HA open vs real open    mean |gap| 0.34%   max |gap| 1.98% on bar 1808
  HA close vs real close  mean |gap| 0.20%   max |gap| 1.14% on bar 1968
  HA open outside range   1120 bars   56.0% of bars
  Real fills              total +37.15%   wins 41.3%
  HA fills                total +175.43%   wins 68.7%
  Flattery                total +138.28%   mean +0.60% per trade   HA reads better 95.2%
  Largest flattery        max +2.49% on bar 1974   min -0.24% on bar 5

Long and short  (2000 bars, 459 closed trades, short position open at the end, not counted)
  HA open vs real open    mean |gap| 0.34%   max |gap| 1.98% on bar 1808
  HA close vs real close  mean |gap| 0.20%   max |gap| 1.14% on bar 1968
  HA open outside range   1120 bars   56.0% of bars
  Real fills              total +23.10%   wins 37.0%
  HA fills                total +298.95%   wins 65.6%
  Flattery                total +275.85%   mean +0.60% per trade   HA reads better 96.1%
  Largest flattery        max +2.49% on bar 1974   min -0.45% on bar 1957

Expected sign: in a trending series HA fills flatter the signal, so the flattery total is positive. Observed: +138.28% long only, +275.85% long and short.
```

Result on TradingView: not yet compiled. Record the compiled result here after step 1, as the table reads it.

## Limitations

- The HA open is recursive, so its first values depend on where the loaded history starts. The request's HA series and the HA chart can differ by a small amount on the first bars and converge within a few bars; the hand check in step 3 is on the last bar, where they agree.
- The signal is the plain HA color flip, filled at the next open, without stops, commission or slippage. It stands for the class of signals read from HA bars, not for any particular strategy; a strategy with a different frequency of trades will show a different total.
- Totals are simple sums of per-trade percent returns, not compounded equity.
- The simulation in `tools/` is a random walk with drift; a real market has gaps, sessions and volatility clusters it does not have, so only the shape of its result is meant to carry over.
- Only bars loaded on the chart are counted, so history depth, symbol and timeframe change every number.
- It reports counts, not a trading rule. Not financial advice.
- The script has not been compiled outside TradingView; compile it in the Pine Editor before relying on it.

## Pine API notes

What the Pine Script v6 reference says about the built-ins the script relies on, read on 2026-10-13 through the context7 documentation index of the reference:

- `chart.is_standard` (simple bool): "Returns true if the chart type is not one of the following: Renko, Kagi, Line break, Point & figure, Range, Heikin Ashi; false otherwise." This is the test the script uses.
- `chart.is_heikinashi` (simple bool): "Returns true if the chart type is Heikin Ashi, false otherwise." Not used: `chart.is_standard` covers Heikin Ashi and the other synthetic types in one test.
- `ticker.heikinashi(symbol) → simple string` (also a series overload): "Creates a ticker identifier for requesting Heikin Ashi bar values." The argument is a symbol ticker identifier; the return value is a ticker id "that can be supplied to request.security()". The reference example is `request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, close)`.
- `ticker.standard(symbol) → simple string` (also a series overload): returns "a string representing the ticker of a standard chart in the 'prefix:ticker' format"; the argument defaults to `syminfo.tickerid`, and an argument without prefix and ticker information is returned as is. The reference example requests "data from the standard chart type, regardless of the chart type the script is running on". The description adds that the ticker it creates is "unaffected by modifiers like extended session, dividend adjustment, currency conversion, and the calculations of non-standard chart types", so the script applies it only off the standard chart, where nothing is measured, and in the table header.
- `syminfo.tickerid` (simple string): the value "can also include information about data modifications such as dividend adjustment, non-standard chart type, currency conversion, etc.", and the remarks recommend running it through `ticker.standard()` for a consistent "prefix:ticker" form. The header shows it that way.
- `math.round(number, precision)` (float overloads): rounds to the given number of decimals. The table rounds the two ledger totals to two decimals and takes the flattery total as their difference.
- `request.security(symbol, timeframe, expression, gaps, lookahead, ignore_invalid_symbol, currency, calc_bars_count) → series <type>`: the `expression` can be "a variable, function, object, array, matrix, or map of series int/float/bool/string/color/enum, or a tuple of these", and the function returns "a result determined by `expression`". The reference example `[open1D, high1D, low1D, close1D, ema1D] = request.security(syminfo.tickerid, "1D", [open, high, low, close, ta.ema(close, 10)])` is the form the script uses. The reference also notes the limit of 40 unique `request.*()` calls per script.
- `strategy()` parameter `fill_orders_on_standard_ohlc` (const bool): "When true, forces strategies running on Heikin Ashi charts to fill orders using actual OHLC prices, for more realistic results. Optional. The default is false." The remarks of `strategy()` add that strategies "always use the chart's prices to enter and exit positions" and that using them on non-standard chart types "will produce misleading results, as their prices are synthetic". The parameter is named in the description only; the indicator does not use it.

## License

MIT. See `LICENSE`.
