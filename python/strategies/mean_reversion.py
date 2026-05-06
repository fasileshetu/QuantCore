import sys
sys.path.append('/Users/fasil/QuantCore/build')

import numpy as np
import quantcore
from collections import deque

class MeanReversionStrategy:
    def __init__(self, window=100, entry_z=1.5, exit_z=0.3):
        self.window  = window
        self.entry_z = entry_z
        self.exit_z  = exit_z
        self.prices  = deque(maxlen=window)
        self.trade_log = []

    def on_tick(self, book, position):
        mid = book.mid_price()
        self.prices.append(mid)

        # need a full window before trading
        if len(self.prices) < self.window:
            return 0

        mean = np.mean(self.prices)
        std  = np.std(self.prices)

        # avoid division by zero in flat markets
        if std < 1e-6:
            return 0

        z = (mid - mean) / std

        # entry signals
        if z < -self.entry_z and position.quantity == 0:
            self.trade_log.append({
                'action': 'BUY',
                'price': mid,
                'z_score': round(z, 3)
            })
            return 1   # buy — price unusually low

        if z > self.entry_z and position.quantity > 0:
            self.trade_log.append({
                'action': 'SELL',
                'price': mid,
                'z_score': round(z, 3)
            })
            return -1  # sell — price unusually high

        # exit signal — close position when price reverts toward mean
        if position.quantity > 0 and abs(z) < self.exit_z:
            self.trade_log.append({
                'action': 'SELL (revert)',
                'price': mid,
                'z_score': round(z, 3)
            })
            return -1

        return 0

    def print_trade_log(self):
        print(f"\nTrade log ({len(self.trade_log)} trades):")
        for t in self.trade_log:
            print(f"  {t['action']:20s}  price={t['price']:.2f}  z={t['z_score']:.3f}")