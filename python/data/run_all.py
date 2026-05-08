import threading
import sys

def run_coinbase():
    from live_runner import feed
    print("Starting Coinbase feed (BTC-USD, ETH-USD)...")
    feed.run()

def run_alpaca():
    from alpaca_feed import run
    run()

if __name__ == '__main__':
    t1 = threading.Thread(target=run_coinbase, daemon=True)
    t2 = threading.Thread(target=run_alpaca,   daemon=True)

    t1.start()
    t2.start()

    try:
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        print("\nShutting down all feeds...")
        sys.exit(0)