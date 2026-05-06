import sys
sys.path.append('/Users/fasil/QuantCore/build')
sys.path.append('/Users/fasil/QuantCore/python/strategies')

import numpy as np
import quantcore
from coinbase_feed import CoinbaseFeed
from collections import deque

# per-product state
class ProductState:
    def __init__(self, product):
        self.product    = product
        self.book       = quantcore.OrderBook()
        self.prices     = deque(maxlen=100)
        self.position   = 0.0
        self.avg_price  = 0.0
        self.pnl        = 0.0
        self.trade_log  = []
        self.event_count = 0
        self.order_counter = 1

    def next_id(self):
        self.order_counter += 1
        return self.order_counter

states = {
    "BTC-USD": ProductState("BTC-USD"),
    "ETH-USD": ProductState("ETH-USD"),
}

WINDOW   = 100
ENTRY_Z  = 1.5
EXIT_Z   = 0.3
QUANTITY = 0.001  # trade 0.001 BTC / ETH at a time

def on_event(d):
    product = d['product']
    if product not in states:
        return

    s = states[product]
    s.event_count += 1

    # update order book directly
    try:
        if d['type'] == 'ADD_ORDER':
            order = quantcore.Order()
            order.id       = s.next_id()
            order.side     = quantcore.Side.BUY if d['is_buy'] else quantcore.Side.SELL
            order.price    = d['price']
            order.quantity = d['quantity']
            s.book.add_order(order)
        elif d['type'] == 'CANCEL_ORDER':
            # best effort cancel — ignore if order not found
            pass
    except Exception:
        pass

    # need both sides to compute mid
    if not s.book.has_bid() or not s.book.has_ask():
        return

    mid = s.book.mid_price()
    s.prices.append(mid)

    # need full window
    if len(s.prices) < WINDOW:
        if s.event_count % 100 == 0:
            print(f"[{product}] {s.event_count} events — warming up ({len(s.prices)}/{WINDOW})")
        return

    mean = np.mean(s.prices)
    std  = np.std(s.prices)
    if std < 1e-6:
        return

    z = (mid - mean) / std

    # strategy logic
    if z < -ENTRY_Z and s.position == 0:
        s.position  = QUANTITY
        s.avg_price = s.book.best_ask()
        s.trade_log.append({'action': 'BUY', 'price': s.avg_price, 'z': round(z, 3)})

    elif s.position > 0 and abs(z) < EXIT_Z:
        sell_price = s.book.best_bid()
        s.pnl     += (sell_price - s.avg_price) * s.position
        s.trade_log.append({'action': 'SELL', 'price': sell_price, 'z': round(z, 3)})
        s.position  = 0
        s.avg_price = 0.0

    # print every 500 events once warmed up
    if s.event_count % 500 == 0:
        print(f"\n[{product}] {s.event_count} events processed")
        print(f"  Mid:     ${mid:,.2f}")
        print(f"  Z-score: {z:.4f}  (threshold: ±{ENTRY_Z})")
        print(f"  PnL:     ${s.pnl:.4f}")
        print(f"  Trades:  {len(s.trade_log)}")
        if s.trade_log:
            last = s.trade_log[-1]
            print(f"  Last:    {last['action']} @ ${last['price']:,.2f}  z={last['z']}")

feed = CoinbaseFeed(products=["BTC-USD", "ETH-USD"])
feed.on_event(on_event)

print("Connecting to Coinbase websocket...")
print("Press Ctrl+C to stop\n")

try:
    feed.run()
except KeyboardInterrupt:
    print("\n\nFinal summary:")
    for product, s in states.items():
        print(f"\n[{product}]")
        print(f"  Events:  {s.event_count}")
        print(f"  Trades:  {len(s.trade_log)}")
        print(f"  PnL:     ${s.pnl:.4f}")