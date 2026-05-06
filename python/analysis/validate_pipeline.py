import sys
sys.path.append('/Users/fasil/QuantCore/build')

import quantcore
from generate_ticks import generate_tick_stream

def make_event(d):
    e = quantcore.Event()
    e.type     = quantcore.EventType.ADD_ORDER if d['type'] == 'ADD_ORDER' else quantcore.EventType.CANCEL_ORDER
    e.order_id = d['order_id']
    e.price    = d['price']
    e.quantity = d['quantity']
    e.is_buy   = d['is_buy']
    return e

# generate 500 synthetic ticks
raw_events = generate_tick_stream(n_events=500, seed=42)
events = [make_event(d) for d in raw_events]

print(f"Generated {len(events)} events")
print(f"  ADD_ORDER:    {sum(1 for d in raw_events if d['type'] == 'ADD_ORDER')}")
print(f"  CANCEL_ORDER: {sum(1 for d in raw_events if d['type'] == 'CANCEL_ORDER')}")

# simple rule-based strategy
buy_count  = 0
sell_count = 0

def on_tick(book, position):
    global buy_count, sell_count
    spread = book.best_ask() - book.best_bid()
    mid    = book.mid_price()

    if spread < 0.75 and position.quantity == 0:
        buy_count += 1
        return 1
    if position.quantity > 0 and book.best_bid() > position.avg_price + 0.40:
        sell_count += 1
        return -1
    return 0

engine = quantcore.SimulationEngine()
engine.on_tick = on_tick
engine.load_events(events)
engine.run()

print(f"\nStrategy activity:")
print(f"  Buys:  {buy_count}")
print(f"  Sells: {sell_count}")

engine.print_summary()

# sanity checks
print("\nValidation checks:")
print(f"  [{'OK' if buy_count > 0 else 'FAIL'}] strategy fired at least one buy")
print(f"  [{'OK' if engine.get_pnl() >= 0 or sell_count == 0 else 'CHECK'}] PnL consistent with trade count")
print(f"  [{'OK' if buy_count >= sell_count else 'FAIL'}] no sells without buys")