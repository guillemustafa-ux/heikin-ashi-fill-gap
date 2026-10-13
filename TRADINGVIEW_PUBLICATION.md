# Heikin Ashi Fill Gap: What a Signal Loses at HA Prices

Description to paste as is (between the rules):

---
WHAT IT DOES
On a Heikin Ashi chart a strategy fills its orders at the chart's synthetic prices: the HA open is the midpoint of the previous HA bar, the HA close is the mean of the bar's real open, high, low and close. In a trend both lag the real price, so a long opened at an HA open buys below the market and one closed at an HA open sells above it: the same signal reads better than at real fills. TradingView's strategy option "Fill orders using standard OHLC" removes the effect by filling at real prices. This indicator measures what that option is worth for the symbol on the chart. It runs on a standard chart, requests the HA prices of the chart symbol with one request.security call and compares them with the real prices bar by bar.

WHAT IS ORIGINAL HERE
Scripts that compare Heikin Ashi with real candles usually show the per-bar price difference. This one adds two measures. First, the share of bars where the HA open lies outside the bar's traded range: a fill there is at a price that never traded. The HA close is the mean of the four real prices and always lies inside the range; only the HA open can leave it. Second, the result of one signal under both fill prices: the HA color flip (green = HA close above HA open), filled at the next bar's open. Two ledgers record the same trades and differ only in the fill price: R at the real open of the fill bar, H at its HA open. The difference per trade, H minus R, is the flattery: the part of the result that comes from the fill price alone.

HOW IT IS MEASURED
- One request.security call at global scope for the HA open, high, low and close of the chart symbol on the chart timeframe, with the defaults gaps off and lookahead off.
- Gap open = (HA open - open) / open * 100, gap close = (HA close - close) / close * 100; mean and maximum |gap| with the bar of the maximum; bars where the HA open is below the low or above the high.
- Modes: Long only (default), a flip to green opens a long, a flip to red closes it; Long and short, each flip closes the position against it and opens one in its direction.
- Per closed trade and ledger: return = direction * (exit / entry - 1) * 100; totals are simple sums in percent points, the win rate is the share of trades with a positive return. Flattery = H return minus R return: sum, mean, share of positive trades, largest and most negative with the exit bar.
- No commission or slippage. An open position on the last bar is not counted. Counters move only on confirmed bars; the table is drawn on the last bar; the shading is drawn on every bar, including the realtime one.

HOW TO USE IT
1. Open a standard chart of the symbol and timeframe your HA strategy runs on. On a non-standard chart the table only says "Use a standard chart".
2. Read the Flattery row: the total is what the HA fills add to this signal over the loaded history, the mean is what one fill is worth, the share is how often the HA fill reads better.
3. Hand check: the last row shows the real open and the HA open of the last confirmed bar; switch the chart to Heikin Ashi, hover the same bar and read its open.

HOW TO READ THE TABLE
Header: symbol, timeframe, bars counted, signal mode, closed trades, open position (not counted).
Gap rows: mean and maximum |gap| of the HA open and of the HA close, with the bar of the maximum.
Outside the traded range: bars and share, red as soon as there is one; shaded on the chart.
Real fills, HA fills: total return and win rate of the same trades under each fill price.
Flattery: total (red when positive), mean per trade, share of trades where HA reads better, then the largest and the most negative with their exit bars.
Last confirmed bar: real open, HA open and gap. Dates in the chart symbol's exchange time.

LIMITATIONS
- The HA open is recursive, so its first values depend on where the loaded history starts; the request and the HA chart can differ slightly on the first bars.
- The signal is the plain HA color flip at the next open, without stops, commission or slippage; it stands for signals read from HA bars, not for any particular strategy.
- Totals are sums of per-trade percent returns, not compounded equity.
- Only loaded bars are counted, so history depth, symbol and timeframe change every number. Counts, not a trading rule. Not financial advice.

The chart shows BINANCE:BTCUSDT on the 1 hour timeframe, standard candles, with the default settings. The table is in the bottom right.
---

## Publishing checklist

- [ ] Compile `heikin_ashi_fill_gap.pine` in the Pine Editor with no errors or warnings.
- [ ] Set the chart: BINANCE:BTCUSDT, 1 hour, standard candles, default inputs, table visible.
- [ ] Check the identities: in both fill rows `wins <= closed trades`; `Flattery total = HA fills total - Real fills total`; `HA open outside the traded range <= bars` in the header; the shaded bars are the outside-range bars.
- [ ] Hand check the "Last confirmed bar" row: note its real open and HA open, switch the chart to Heikin Ashi, hover the same bar and read its open. It must match the HA open at the symbol's precision.
- [ ] With the chart on Heikin Ashi: the table shows only "Use a standard chart" and no bar is shaded. Switch back to standard candles.
- [ ] To check for look-ahead, use Bar Replay: start a few hundred bars back and step forward. Counts change only when a bar closes, a trade is recorded only on the bar after its flip, and a shaded bar keeps its tint once closed.
- [ ] Check the title is at most 60 characters (it is 54).
- [ ] Publish as open source, with the MIT license text if the form allows it.
- [ ] Check that the description contains no links, contact info, or performance claims, and is between 3,000 and 4,600 characters.
- [ ] In Final touches, open Show more and fill the tags BEFORE pressing Publish; the field takes 5 tags at most. Suggested tags (one word each): heikinashi, fillprice, backtest, slippage, audit.
- [ ] Before pressing Publish, make sure the chart has no drawings: a stray paste becomes a text drawing in the snapshot.
- [ ] Add the TradingView script URL to `README.md` after publishing.
