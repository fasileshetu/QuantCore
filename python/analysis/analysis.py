import sys
sys.path.append('/Users/fasil/QuantCore/build')
sys.path.append('/Users/fasil/QuantCore/python/strategies')
sys.path.append('/Users/fasil/QuantCore/python/analysis')

import numpy as np
import matplotlib.pyplot as plt
import quantcore
from generate_ticks import generate_tick_stream
from mean_reversion import MeanReversionStrategy

def make_event(d):
    e = quantcore.Event()
    e.type     = quantcore.EventType.ADD_ORDER if d['type'] == 'ADD_ORDER' else quantcore.EventType.CANCEL_ORDER
    e.order_id = d['order_id']
    e.price    = d['price']
    e.quantity = d['quantity']
    e.is_buy   = d['is_buy']
    return e

# ── run backtest ──────────────────────────────────────────────
raw_events = generate_tick_stream(n_events=2000, seed=42)
events     = [make_event(d) for d in raw_events]
strategy   = MeanReversionStrategy(window=50, entry_z=2.0, exit_z=0.5)

engine = quantcore.SimulationEngine()
engine.on_tick = strategy.on_tick
engine.load_events(events)
engine.run()

pnl_history = list(engine.get_pnl_history())
mid_history = list(engine.get_mid_history())

# ── metrics ───────────────────────────────────────────────────
def sharpe_ratio(pnl_history):
    returns = np.diff(pnl_history)
    if len(returns) == 0 or np.std(returns) == 0:
        return 0.0
    return np.mean(returns) / np.std(returns) * np.sqrt(252)

def max_drawdown(pnl_history):
    peak = pnl_history[0]
    max_dd = 0.0
    for pnl in pnl_history:
        if pnl > peak:
            peak = pnl
        dd = peak - pnl
        if dd > max_dd:
            max_dd = dd
    return max_dd

def win_rate(trade_log):
    sells = [t for t in trade_log if 'SELL' in t['action']]
    if not sells:
        return 0.0
    # a sell is a win if price is above avg entry
    wins = [t for t in sells if t['z_score'] > -2.0]
    return len(wins) / len(sells) * 100

sharpe = sharpe_ratio(pnl_history)
max_dd = max_drawdown(pnl_history)
wr     = win_rate(strategy.trade_log)

print("=== Performance Metrics ===")
print(f"  Realized PnL:  ${engine.get_pnl():.2f}")
print(f"  Sharpe Ratio:  {sharpe:.3f}")
print(f"  Max Drawdown:  ${max_dd:.2f}")
print(f"  Win Rate:      {wr:.1f}%")
print(f"  Total trades:  {len(strategy.trade_log)}")

# ── plot ──────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
fig.suptitle('QuantCore — Mean Reversion Backtest', fontsize=14)

# PnL curve
ax1.plot(pnl_history, color='#2ecc71', linewidth=1.5)
ax1.axhline(0, color='gray', linewidth=0.5, linestyle='--')
ax1.set_title('Realized PnL over time')
ax1.set_ylabel('PnL ($)')
ax1.set_xlabel('Tick')
ax1.grid(True, alpha=0.3)

# mid price
ax2.plot(mid_history, color='#3498db', linewidth=1.0)
ax2.set_title('Mid price over time')
ax2.set_ylabel('Price ($)')
ax2.set_xlabel('Tick')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/Users/fasil/QuantCore/python/analysis/backtest_results.png', dpi=150)
plt.show()
print("\nPlot saved to python/analysis/backtest_results.png")