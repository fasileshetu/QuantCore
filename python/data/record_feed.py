import sys
import json
import datetime
sys.path.append('/Users/fasil/QuantCore/python/data')

from coinbase_feed import CoinbaseFeed

timestamp  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f"/Users/fasil/QuantCore/data/ticks_{timestamp}.jsonl"

products   = ["BTC-USD", "ETH-USD"]
event_counts = {p: 0 for p in products}
total        = 0

print(f"Recording to {output_path}")
print("Press Ctrl+C to stop\n")

f = open(output_path, 'w')

def on_event(d):
    global total
    f.write(json.dumps(d) + '\n')
    f.flush()

    product = d['product']
    event_counts[product] += 1
    total += 1

    if total % 5000 == 0:
        print(f"Recorded {total} events  |  BTC: {event_counts['BTC-USD']}  ETH: {event_counts['ETH-USD']}")

feed = CoinbaseFeed(products=products)
feed.on_event(on_event)

try:
    feed.run()
except KeyboardInterrupt:
    f.close()
    print(f"\nDone. Recorded {total} events to {output_path}")
    for p in products:
        print(f"  {p}: {event_counts[p]} events")