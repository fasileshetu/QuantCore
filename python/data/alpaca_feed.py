import os
import sys
sys.path.append('/Users/fasil/QuantCore/python/strategies')

from dotenv import load_dotenv
from alpaca.data.live import StockDataStream
from alpaca.data.enums import DataFeed
from collections import deque
import numpy as np

load_dotenv('/Users/fasil/QuantCore/.env')

API_KEY    = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')

SYMBOLS  = ['AAPL', 'MSFT', 'GOOGL']
WINDOW   = 50
ENTRY_Z  = 1.5
EXIT_Z   = 0.3
QUANTITY = 1  # 1 share at a time

class StockState:
    def __init__(self, symbol):
        self.symbol      = symbol
        self.prices      = deque(maxlen=WINDOW)
        self.position    = 0
        self.avg_price   = 0.0
        self.pnl         = 0.0
        self.trade_log   = []
        self.quote_count = 0

states = {symbol: StockState(symbol) for symbol in SYMBOLS}

def on_quote(quote):
    symbol = quote.symbol
    if symbol not in states:
        return

    s = states[symbol]
    s.quote_count += 1

    # mid price from bid/ask
    if quote.bid_price is None or quote.ask_price is None:
        return
    if quote.bid_price <= 0 or quote.ask_price <= 0:
        return

    mid = (float(quote.bid_price) + float(quote.ask_price)) / 2.0
    s.prices.append(mid)

    if len(s.prices) < WINDOW:
        if s.quote_count % 20 == 0:
            print(f"[{symbol}] warming up ({len(s.prices)}/{WINDOW})")
        return

    mean = np.mean(s.prices)
    std  = np.std(s.prices)
    if std < 1e-6:
        return

    z = (mid - mean) / std

    # strategy
    if z < -ENTRY_Z and s.position == 0:
        s.position  = QUANTITY
        s.avg_price = float(quote.ask_price)
        s.trade_log.append({'action': 'BUY', 'price': s.avg_price, 'z': round(z, 3)})
        print(f"[{symbol}] BUY  @ ${s.avg_price:.2f}  z={z:.3f}")

    elif s.position > 0 and abs(z) < EXIT_Z:
        sell_price  = float(quote.bid_price)
        s.pnl      += (sell_price - s.avg_price) * s.position
        s.trade_log.append({'action': 'SELL', 'price': sell_price, 'z': round(z, 3)})
        print(f"[{symbol}] SELL @ ${sell_price:.2f}  z={z:.3f}  PnL: ${s.pnl:.4f}")
        s.position  = 0
        s.avg_price = 0.0

    if s.quote_count % 50 == 0:
        print(f"[{symbol}] {s.quote_count} quotes  mid=${mid:.2f}  z={z:.3f}  PnL=${s.pnl:.4f}  trades={len(s.trade_log)}")

async def quote_handler(quote):
    on_quote(quote)

def run():
    print(f"Connecting to Alpaca for {SYMBOLS}...")
    print("Note: full stream requires market hours (9:30am-4:00pm ET Mon-Fri)")
    print("Press Ctrl+C to stop\n")

    stream = StockDataStream(API_KEY, SECRET_KEY, feed=DataFeed.IEX)

    for symbol in SYMBOLS:
        stream.subscribe_quotes(quote_handler, symbol)

    stream.run()

if __name__ == '__main__':
    run()