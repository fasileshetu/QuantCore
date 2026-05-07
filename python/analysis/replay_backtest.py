import sys
sys.path.append('/Users/fasil/QuantCore/build')
sys.path.append('/Users/fasil/QuantCore/python/strategies')
sys.path.append('/Users/fasil/QuantCore/python/analysis')

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime
import quantcore
from collections import deque

TICK_FILE = '/Users/fasil/QuantCore/data/ticks_20260506_200140.jsonl'
PRODUCTS  = ['BTC-USD', 'ETH-USD']
WINDOW    = 100
ENTRY_Z   = 1.5
EXIT_Z    = 0.3
QUANTITY  = 0.001

class ProductBacktest:
    def __init__(self, product):
        self.product    = product
        self.book       = quantcore.OrderBook()
        self.prices     = deque(maxlen=WINDOW)
        self.position   = 0.0
        self.avg_price  = 0.0
        self.pnl        = 0.0
        self.pnl_history = []
        self.mid_history = []
        self.trade_log  = []
        self.event_count = 0
        self.order_map  = {}  # track order_id -> price for cancels

    def process(self, d):
        self.event_count += 1

        try:
            if d['type'] == 'ADD_ORDER':
                order          = quantcore.Order()
                order.id       = d['order_id']
                order.side     = quantcore.Side.BUY if d['is_buy'] else quantcore.Side.SELL
                order.price    = d['price']
                order.quantity = d['quantity']
                self.book.add_order(order)
                self.order_map[d['order_id']] = d['price']
            elif d['type'] == 'CANCEL_ORDER':
                pass  # skip cancels — order ids don't match across sessions
        except Exception:
            pass

        if not self.book.has_bid() or not self.book.has_ask():
            return

        mid = self.book.mid_price()
        self.prices.append(mid)
        self.mid_history.append(mid)

        if len(self.prices) < WINDOW:
            self.pnl_history.append(self.pnl)
            return

        mean = np.mean(self.prices)
        std  = np.std(self.prices)
        if std < 1e-6:
            self.pnl_history.append(self.pnl)
            return

        z = (mid - mean) / std
        z = max(-7.0, min(7.0, z))  # cap z-score

        if z < -ENTRY_Z and self.position == 0:
            self.position  = QUANTITY
            self.avg_price = self.book.best_ask()
            self.trade_log.append({
                'action': 'BUY',
                'price':  self.avg_price,
                'z':      round(z, 3),
                'tick':   self.event_count
            })

        elif self.position > 0 and abs(z) < EXIT_Z:
            sell_price  = self.book.best_bid()
            self.pnl   += (sell_price - self.avg_price) * self.position
            self.trade_log.append({
                'action': 'SELL',
                'price':  sell_price,
                'z':      round(z, 3),
                'tick':   self.event_count
            })
            self.position  = 0
            self.avg_price = 0.0

        self.pnl_history.append(self.pnl)

def sharpe(pnl_history):
    returns = np.diff(pnl_history)
    if len(returns) == 0 or np.std(returns) == 0:
        return 0.0
    return np.mean(returns) / np.std(returns) * np.sqrt(252)

def max_drawdown(pnl_history):
    peak   = pnl_history[0]
    max_dd = 0.0
    for pnl in pnl_history:
        if pnl > peak:
            peak = pnl
        dd = peak - pnl
        if dd > max_dd:
            max_dd = dd
    return max_dd

# ── replay ────────────────────────────────────────────────────
backtests = {p: ProductBacktest(p) for p in PRODUCTS}

print(f"Replaying {TICK_FILE}")
print("This may take a moment for 2M events...\n")

with open(TICK_FILE, 'r') as f:
    for i, line in enumerate(f):
        d = json.loads(line)
        product = d.get('product')
        if product in backtests:
            backtests[product].process(d)

        if i % 200000 == 0 and i > 0:
            print(f"  {i:,} events processed...")

# ── results ───────────────────────────────────────────────────
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_path  = f"/Users/fasil/QuantCore/data/replay_{timestamp}.log"

with open(log_path, 'w') as log:
    for product, bt in backtests.items():
        sh  = sharpe(bt.pnl_history)
        mdd = max_drawdown(bt.pnl_history)
        wins = [t for t in bt.trade_log if t['action'] == 'SELL']
        wr   = 100.0 if not wins else sum(
            1 for t in wins if t['price'] > bt.avg_price
        ) / len(wins) * 100

        print(f"\n=== {product} ===")
        print(f"  Events:       {bt.event_count:,}")
        print(f"  Trades:       {len(bt.trade_log)}")
        print(f"  Realized PnL: ${bt.pnl:.4f}")
        print(f"  Sharpe:       {sh:.3f}")
        print(f"  Max Drawdown: ${mdd:.4f}")

        log.write(f"=== {product} ===\n")
        log.write(f"  Events:       {bt.event_count:,}\n")
        log.write(f"  Trades:       {len(bt.trade_log)}\n")
        log.write(f"  Realized PnL: ${bt.pnl:.4f}\n")
        log.write(f"  Sharpe:       {sh:.3f}\n")
        log.write(f"  Max Drawdown: ${mdd:.4f}\n\n")
        log.write("  Trade log:\n")
        for t in bt.trade_log:
            log.write(f"    {t['action']:5s}  price={t['price']:.2f}  z={t['z']:.3f}  tick={t['tick']:,}\n")

print(f"\nLog saved to {log_path}")

# ── plot ──────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('QuantCore — Real Market Data Replay (Coinbase)', fontsize=14)

colors = {'BTC-USD': '#f39c12', 'ETH-USD': '#3498db'}

for i, (product, bt) in enumerate(backtests.items()):
    color = colors[product]

    # PnL curve
    axes[0][i].plot(bt.pnl_history, color='#2ecc71', linewidth=1.0)
    axes[0][i].axhline(0, color='gray', linewidth=0.5, linestyle='--')
    axes[0][i].set_title(f'{product} — Realized PnL')
    axes[0][i].set_ylabel('PnL ($)')
    axes[0][i].set_xlabel('Tick')
    axes[0][i].grid(True, alpha=0.3)

    # mid price
    axes[1][i].plot(bt.mid_history, color=color, linewidth=0.5)
    axes[1][i].set_title(f'{product} — Mid Price')
    axes[1][i].set_ylabel('Price ($)')
    axes[1][i].set_xlabel('Tick')
    axes[1][i].grid(True, alpha=0.3)

plt.tight_layout()
img_path = f'/Users/fasil/QuantCore/data/replay_{timestamp}.png'
plt.savefig(img_path, dpi=150)
print(f"Plot saved to {img_path}")