# QuantCore

High-performance algorithmic trading backtester with a Python/C++ hybrid architecture.
Strategy logic is written in Python while a C++ core handles tick parsing, order book
maintenance, order matching, and real-time PnL tracking — connected via pybind11 bindings.

## Architecture

    Python layer (strategy + analysis)
            ↓  pybind11
    C++ core (event loop + order book + matching engine)
            ↓
    Live market data (Coinbase + Alpaca) / Historical tick files

## Stack

- C++17 — order book, event loop, matching engine, position tracking
- pybind11 — Python/C++ bindings
- Python — strategy logic, signal generation, parameter tuning
- numpy / matplotlib — post-run analysis and plotting
- CMake — build system

## Build

    mkdir build && cd build
    cmake .. -DCMAKE_CXX_COMPILER=/usr/bin/clang++
    make

## Run

    # Live crypto feed (BTC-USD, ETH-USD)
    cd python/data
    python3 -u live_runner.py

    # Live equities feed (AAPL, MSFT, GOOGL)
    python3 -u alpaca_feed.py

    # Replay recorded tick data
    cd python/analysis
    python3 replay_backtest.py

    # Synthetic backtest
    python3 analysis.py

## Performance

C++ engine processes 5000 market events in **9.5ms** vs **111.8ms** for an equivalent
pure Python implementation — **11.8x faster**.

## Results

### Synthetic backtest (50k events)

| Metric       | Value  |
|--------------|--------|
| Realized PnL | $65.00 |
| Sharpe Ratio | 0.357  |
| Max Drawdown | $3.00  |
| Win Rate     | 100%   |
| Trades       | 4      |

### Real market data replay (Coinbase — 2M events, no fees)

| Asset   | Events    | Trades | PnL (0.001 size) | PnL (scaled 1.0) | Max Drawdown |
|---------|-----------|--------|------------------|------------------|--------------|
| BTC-USD | 1,162,732 | 252    | +$26.26          | +$26,260         | $0.00        |
| ETH-USD | 868,251   | 92     | +$0.23           | +$225.90         | $0.00        |

### Fee analysis (Coinbase — 2M events, 0.60% taker fee)

| Configuration                         | Trades | Gross PnL | Fees      | Net PnL   |
|---------------------------------------|--------|-----------|-----------|-----------|
| window=100, z=1.5 (original)          | 252    | +$26.26   | -$122.48  | -$96.22   |
| window=500, z=2.5 (better signals)    | 132    | +$13.15   | -$64.16   | -$51.01   |
| window=500, z=2.5, size=0.01 (scaled) | 132    | +$131.48  | -$641.60  | -$510.12  |

### Break-even fee analysis

| Asset   | Gross PnL | Break-even fee | Retail fee    | Verdict                         |
|---------|-----------|----------------|---------------|---------------------------------|
| BTC-USD | +$13.15   | 0.1231% / side | 0.60% / side  | Viable above $1M monthly volume |
| ETH-USD | +$0.09    | 0.0989% / side | 0.60% / side  | Viable above $1M monthly volume |

### Alpaca live feed (US equities, market hours)

| Symbol | Quotes  | Trades | Notes                                   |
|--------|---------|--------|-----------------------------------------|
| AAPL   | 64,300+ | 2,426  | Fee-negative, entry threshold too loose |
| MSFT   | ~8,000  | 200+   | Same structural fee issue               |
| GOOGL  | 55,300+ | 2,906  | Same structural fee issue               |

## Analysis

The mean reversion strategy is gross profitable on real market data but fee-negative
at standard retail rates. The strategy buys at the ask and sells at the bid — always
paying the spread plus fees. At 0.60% per side, fees are roughly 5x larger than gross
profit per trade.

Break-even sits at 0.12% per side, corresponding to Coinbase's $1M+ monthly volume
tier. The strategy is viable at institutional scale where maker rebates and negotiated
fee tiers bring costs below break-even — consistent with how high-frequency mean
reversion is deployed in production.

## Potential improvements

- Trend filter — detect persistent directional moves and sit out, only trade genuine
  mean-reverting conditions
- Maker strategy — post limit orders to collect the spread rather than pay it,
  restructuring the fee economics entirely
- Longer data collection — extended Coinbase session for more robust Sharpe ratio
  and drawdown estimates