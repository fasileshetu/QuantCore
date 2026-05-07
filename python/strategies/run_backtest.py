import sys
sys.path.append('/Users/fasil/QuantCore/build')
sys.path.append('/Users/fasil/QuantCore/python/analysis')

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

# generate a longer tick stream for a more realistic backtest
raw_events = generate_tick_stream(n_events=50000, seed=42)
events = [make_event(d) for d in raw_events]

print(f"Running backtest over {len(events)} events...")

strategy = MeanReversionStrategy(window=50, entry_z=2.0, exit_z=0.5)

engine = quantcore.SimulationEngine()
engine.on_tick = strategy.on_tick
engine.load_events(events)
engine.run()

strategy.print_trade_log()
engine.print_summary()