import random

def generate_tick_stream(n_events=500, seed=42):
    random.seed(seed)
    events = []
    order_id = 1
    price = 100.00
    active_orders = []

    for _ in range(n_events):
        action = random.random()

        if action < 0.4:
            # add a buy order near current price
            bid_price = round(price - random.uniform(0.25, 1.00), 2)
            events.append({
                'type': 'ADD_ORDER',
                'order_id': order_id,
                'price': bid_price,
                'quantity': random.choice([50, 100, 150, 200]),
                'is_buy': True
            })
            active_orders.append(order_id)
            order_id += 1

        elif action < 0.8:
            # add a sell order near current price
            ask_price = round(price + random.uniform(0.25, 1.00), 2)
            events.append({
                'type': 'ADD_ORDER',
                'order_id': order_id,
                'price': ask_price,
                'quantity': random.choice([50, 100, 150, 200]),
                'is_buy': False
            })
            active_orders.append(order_id)
            order_id += 1

        elif action < 0.9 and active_orders:
            # cancel a random existing order
            cancel_id = random.choice(active_orders)
            active_orders.remove(cancel_id)
            events.append({
                'type': 'CANCEL_ORDER',
                'order_id': cancel_id,
                'price': 0,
                'quantity': 0,
                'is_buy': False
            })

        # drift the price slightly
        price += random.uniform(-0.10, 0.10)
        price = round(price, 2)

    return events