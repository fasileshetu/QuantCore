import sys
sys.path.append('/Users/fasil/QuantCore/build')

import quantcore

# build events in Python
events = []

def make_event(event_type, order_id, price, quantity, is_buy):
    e = quantcore.Event()
    e.type     = event_type
    e.order_id = order_id
    e.price    = price
    e.quantity = quantity
    e.is_buy   = is_buy
    return e

events.append(make_event(quantcore.EventType.ADD_ORDER, 1, 99.50, 100, True))
events.append(make_event(quantcore.EventType.ADD_ORDER, 2, 100.00, 150, False))
events.append(make_event(quantcore.EventType.ADD_ORDER, 3, 99.00, 200, True))
events.append(make_event(quantcore.EventType.ADD_ORDER, 4, 100.50, 50, False))
events.append(make_event(quantcore.EventType.ADD_ORDER, 5, 99.75, 100, True))
events.append(make_event(quantcore.EventType.ADD_ORDER, 6, 100.25, 100, False))
events.append(make_event(quantcore.EventType.CANCEL_ORDER, 2, 0, 0, False))
events.append(make_event(quantcore.EventType.ADD_ORDER, 7, 100.10, 200, False))
events.append(make_event(quantcore.EventType.ADD_ORDER, 8, 100.00, 100, True))

# define strategy in Python
def on_tick(book, position):
    spread = book.best_ask() - book.best_bid()
    if spread < 1.0 and position.quantity == 0:
        return 1    # buy
    if position.quantity > 0 and book.best_bid() > position.avg_price + 0.50:
        return -1   # sell
    return 0        # hold

# wire up and run
engine = quantcore.SimulationEngine()
engine.on_tick = on_tick
engine.load_events(events)
engine.run()
engine.print_summary()

print(f"\nPnL from Python: ${engine.get_pnl():.2f}")