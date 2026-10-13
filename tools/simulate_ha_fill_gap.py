"""Sanity simulation of the Heikin Ashi fill gap on a synthetic hourly series.

Standard library only. Run with:  python -I tools/simulate_ha_fill_gap.py

The series is a seeded geometric random walk with drift and a few regime changes, about 2,000 hourly bars
with open, high, low and close. Heikin Ashi values follow the standard recursion:

    haClose = (open + high + low + close) / 4
    haOpen  = (previous haOpen + previous haClose) / 2, seeded with (open + close) / 2 on the first bar

For every bar the simulation does what the Pine script does on a confirmed bar, in the same order: it fills
the previous bar's signal at this bar's open (ledger R at the real open, ledger H at the HA open), measures
the gaps in percent of the real price, counts the bars where the HA open lies outside the traded range, and
reads this bar's HA color flip (green = haClose > haOpen) as the signal for the next bar. Returns are
direction * (exit / entry - 1) * 100 without commission or slippage; the flattery of a trade is its H return
minus its R return.

Printed for both signal modes: bars, mean and max |gap| for the open and the close, the outside-range share,
closed trades, total return and win rate under real and HA fills, total and mean flattery and the share of
trades where the HA fill reads better. These are the magnitudes to compare with the TradingView table after
compiling; the symbol will differ, the sign of the flattery should not.
"""

import math
import random

SEED = 7
STEPS = 12  # intrabar steps that build the high and the low of each bar
# Regimes as (bars, hourly drift, hourly volatility): up, down, flat, up, down. 2,000 bars in all.
REGIMES = [(500, 0.0008, 0.004), (400, -0.0006, 0.006), (300, 0.0, 0.003), (500, 0.0010, 0.005), (300, -0.0008, 0.007)]


def make_series(seed):
    """Hourly (open, high, low, close) bars of a geometric random walk; each bar opens at the previous close."""
    rng = random.Random(seed)
    bars = []
    price = 100.0
    for n, mu, sigma in REGIMES:
        for _ in range(n):
            o = price
            path = [o]
            for _ in range(STEPS):
                price *= math.exp(mu / STEPS + sigma / math.sqrt(STEPS) * rng.gauss(0.0, 1.0))
                path.append(price)
            bars.append((o, max(path), min(path), price))
    return bars


def heikin_ashi(bars):
    """(haOpen, haClose) per bar with the standard recursion."""
    ha = []
    for i, (o, h, l, c) in enumerate(bars):
        ha_close = (o + h + l + c) / 4
        ha_open = (o + c) / 2 if i == 0 else (ha[-1][0] + ha[-1][1]) / 2
        ha.append((ha_open, ha_close))
    return ha


def signed(v):
    """Same template as fmtSigned() in the Pine script ("0.00" with an explicit plus)."""
    return f"{v:+.2f}%"


def simulate(bars, ha, long_short):
    n_bars = 0
    sum_gap_o = sum_gap_c = 0.0
    max_gap_o = max_gap_c = 0.0
    max_gap_o_bar = max_gap_c_bar = None
    outside = 0
    prev_state = pending = pos = 0
    entry_r = entry_h = None
    trades = wins_r = wins_h = 0
    sum_r = sum_h = sum_flat = 0.0
    n_flat_pos = 0
    max_flat = min_flat = None
    max_flat_bar = min_flat_bar = None
    for i, ((o, h, l, c), (ha_o, ha_c)) in enumerate(zip(bars, ha)):
        # 1) Fill of the previous bar's signal at this bar's open, real and HA.
        if pending:
            if pos and pos != pending:
                ret_r = pos * (o / entry_r - 1) * 100
                ret_h = pos * (ha_o / entry_h - 1) * 100
                flat = ret_h - ret_r
                trades += 1
                wins_r += ret_r > 0
                wins_h += ret_h > 0
                sum_r += ret_r
                sum_h += ret_h
                sum_flat += flat
                n_flat_pos += flat > 0
                if max_flat is None or flat > max_flat:
                    max_flat, max_flat_bar = flat, i
                if min_flat is None or flat < min_flat:
                    min_flat, min_flat_bar = flat, i
                pos = 0
            if pos == 0 and (pending == 1 or long_short):
                pos, entry_r, entry_h = pending, o, ha_o
            pending = 0
        # 2) Gap measures.
        gap_o = abs((ha_o - o) / o * 100)
        gap_c = abs((ha_c - c) / c * 100)
        n_bars += 1
        sum_gap_o += gap_o
        sum_gap_c += gap_c
        if gap_o > max_gap_o:
            max_gap_o, max_gap_o_bar = gap_o, i
        if gap_c > max_gap_c:
            max_gap_c, max_gap_c_bar = gap_c, i
        if ha_o < l or ha_o > h:
            outside += 1
        # 3) This bar's flip, filled on the next bar.
        state = 1 if ha_c > ha_o else -1
        if prev_state and state != prev_state:
            pending = state
        prev_state = state

    print(f"{'Long and short' if long_short else 'Long only'}  ({n_bars} bars, {trades} closed trades, "
          f"{'long' if pos == 1 else 'short' if pos == -1 else 'no'} position open at the end, not counted)")
    print(f"  HA open vs real open    mean |gap| {sum_gap_o / n_bars:.2f}%   max |gap| {max_gap_o:.2f}% on bar {max_gap_o_bar}")
    print(f"  HA close vs real close  mean |gap| {sum_gap_c / n_bars:.2f}%   max |gap| {max_gap_c:.2f}% on bar {max_gap_c_bar}")
    print(f"  HA open outside range   {outside} bars   {100.0 * outside / n_bars:.1f}% of bars")
    print(f"  Real fills              total {signed(sum_r)}   wins {100.0 * wins_r / trades:.1f}%")
    print(f"  HA fills                total {signed(sum_h)}   wins {100.0 * wins_h / trades:.1f}%")
    print(f"  Flattery                total {signed(sum_flat)}   mean {signed(sum_flat / trades)} per trade   "
          f"HA reads better {100.0 * n_flat_pos / trades:.1f}%")
    print(f"  Largest flattery        max {signed(max_flat)} on bar {max_flat_bar}   min {signed(min_flat)} on bar {min_flat_bar}")
    print()
    return sum_flat


def main():
    bars = make_series(SEED)
    ha = heikin_ashi(bars)
    print(f"Series: {len(bars)} hourly bars, seed {SEED}, {len(REGIMES)} drift regimes, "
          f"first open {bars[0][0]:.2f}, last close {bars[-1][3]:.2f}\n")
    flat_long = simulate(bars, ha, long_short=False)
    flat_both = simulate(bars, ha, long_short=True)
    print("Expected sign: in a trending series HA fills flatter the signal, so the flattery total is positive. "
          f"Observed: {signed(flat_long)} long only, {signed(flat_both)} long and short.")


if __name__ == "__main__":
    main()
