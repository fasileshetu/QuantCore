import sys
sys.path.append('/Users/fasil/QuantCore/build')
sys.path.append('/Users/fasil/QuantCore/python/analysis')
sys.path.append('/Users/fasil/QuantCore/python/strategies')

import time
import numpy as np
import quantcore
from generate_ticks import generate_tick_stream

N          = 5000
RUNS       = 5
raw_events = generate_tick_stream(n_events=N, seed=42)

print(f"Benchmarking over {N} events ({RUNS} runs each)...\n")

# ── pure Python order book ────────────────────────────────────
class PythonOrderBook:
    def __init__(self):
        self.bids   = {}
        self.asks   = {}
        self.orders = {}

    def add_order(self, order_id, price, quantity, is_buy):
        self.orders[order_id] = (price, quantity, is_buy)
        if is_buy:
            self.bids[price] = self.bids.get(price, 0) + quantity
        else:
            self.asks[price] = self.asks.get(price, 0) + quantity

    def cancel_order(self, order_id):
        if order_id not in self.orders:
            return
        price, quantity, is_buy = self.orders.pop(order_id)
        if is_buy:
            self.bids[price] -= quantity
            if self.bids[price] <= 0:
                del self.bids[price]
        else:
            self.asks[price] -= quantity
            if self.asks[price] <= 0:
                del self.asks[price]

    def best_bid(self):
        return max(self.bids.keys()) if self.bids else None

    def best_ask(self):
        return min(self.asks.keys()) if self.asks else None

def run_python(raw_events):
    book = PythonOrderBook()
    for d in raw_events:
        if d['type'] == 'ADD_ORDER':
            book.add_order(d['order_id'], d['price'], d['quantity'], d['is_buy'])
        elif d['type'] == 'CANCEL_ORDER':
            book.cancel_order(d['order_id'])
        book.best_bid()
        book.best_ask()

# ── pre-build C++ events outside timing window ────────────────
def make_event(d):
    e = quantcore.Event()
    e.type     = quantcore.EventType.ADD_ORDER if d['type'] == 'ADD_ORDER' else quantcore.EventType.CANCEL_ORDER
    e.order_id = d['order_id']
    e.price    = d['price']
    e.quantity = d['quantity']
    e.is_buy   = d['is_buy']
    return e

cpp_events = [make_event(d) for d in raw_events]

def run_cpp(events):
    engine = quantcore.SimulationEngine()
    engine.load_events(events)
    engine.run()

# ── benchmark ─────────────────────────────────────────────────
py_times = []
for _ in range(RUNS):
    t0 = time.perf_counter()
    run_python(raw_events)
    py_times.append(time.perf_counter() - t0)

cpp_times = []
for _ in range(RUNS):
    t0 = time.perf_counter()
    run_cpp(cpp_events)
    cpp_times.append(time.perf_counter() - t0)

py_avg  = np.mean(py_times)
cpp_avg = np.mean(cpp_times)
speedup = py_avg / cpp_avg

print(f"Pure Python:  {py_avg*1000:.1f} ms  (avg over {RUNS} runs)")
print(f"C++ engine:   {cpp_avg*1000:.1f} ms  (avg over {RUNS} runs)")
print(f"Speedup:      {speedup:.1f}x faster")