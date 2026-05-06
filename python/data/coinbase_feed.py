import asyncio
import websockets
import json
from datetime import datetime

class CoinbaseFeed:
    WS_URL = "wss://advanced-trade-ws.coinbase.com"

    def __init__(self, products=["BTC-USD", "ETH-USD"]):
        self.products    = products
        self.order_books = {p: {"bids": {}, "asks": {}} for p in products}
        self.callbacks   = []
        self._order_id   = 1

    def on_event(self, callback):
        """register a callback that receives (product, event_dict) on every update"""
        self.callbacks.append(callback)

    def _next_id(self):
        self._order_id += 1
        return self._order_id

    def _parse_message(self, msg):
        events = []
        channel = msg.get("channel", "")

        if channel not in ("l2_data", "market_trades"):
            return events

        for event in msg.get("events", []):
            product = event.get("product_id", "")
            updates = event.get("updates", [])
            etype   = event.get("type", "")

            for u in updates:
                side     = u.get("side", "")
                price    = float(u.get("price_level", 0))
                quantity = float(u.get("new_quantity", 0))
                book     = self.order_books.get(product, {})

                if quantity == 0:
                    # quantity of 0 means the level was removed
                    events.append({
                        'type':     'CANCEL_ORDER',
                        'order_id': self._next_id(),
                        'price':    price,
                        'quantity': 0,
                        'is_buy':   side == "bid",
                        'product':  product,
                        'time':     msg.get("timestamp", "")
                    })
                else:
                    events.append({
                        'type':     'ADD_ORDER',
                        'order_id': self._next_id(),
                        'price':    price,
                        'quantity': quantity,
                        'is_buy':   side == "bid",
                        'product':  product,
                        'time':     msg.get("timestamp", "")
                    })

        return events

    async def _listen(self):
        async with websockets.connect(
            self.WS_URL,
            max_size=10 * 1024 * 1024  # 10MB limit
        ) as ws:
            subscribe_msg = {
                "type": "subscribe",
                "product_ids": self.products,
                "channel": "level2"
            }
            await ws.send(json.dumps(subscribe_msg))
            print(f"Subscribed to {self.products}")

            async for raw in ws:
                msg    = json.loads(raw)
                events = self._parse_message(msg)

                for event in events:
                    for cb in self.callbacks:
                        cb(event)

    def run(self):
        asyncio.run(self._listen())