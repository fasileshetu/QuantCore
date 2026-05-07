# QuantCore

High-performance algorithmic trading backtester with a Python/C++ hybrid architecture.
Strategy logic is written in Python while a C++ core handles tick parsing, order book
maintenance, order matching, and real-time PnL tracking — connected via pybind11 bindings.

## Architecture

    Python layer (strategy + analysis)
            ↓  pybind11
    C++ core (event loop + order book + matching engine)
            ↓
    Live market data (Coinbase + Alpaca) / Historical data

## Stack

- C++17 — order book, event loop, matching engine, position tracking
- pybind11 — Python/C++ bindings
- Python — strategy logic, signal generation, parameter tuning
- pandas / numpy / matplotlib — post-run analysis and plotting
- CMake — build system

## Build

    mkdir build && cd build
    cmake .. -DCMAKE_CXX_COMPILER=/usr/bin/clang++
    make

## Live trading

Connects to Coinbase Advanced Trade websocket for real-time BTC-USD and ETH-USD
order book data, and Alpaca for US equities. Mean reversion strategy runs live
on streaming level2 updates.

    cd python/data
    python3 -u live_runner.py

## Performance

C++ engine processes 5000 market events in **9.5ms** vs **111.8ms** for an equivalent
pure Python implementation — **11.8x faster**.

## Live results (sample run)

| Asset   | Events    | Trades | PnL (0.001 size) | PnL (scaled 1.0) |
|---------|-----------|--------|------------------|------------------|
| BTC-USD | 242,500   | 42     | +$0.9114         | +$911.40         |
| ETH-USD | 150,000   | 30     | +$0.0273         | +$27.30          |

## Backtest results (synthetic data)

| Metric        | Value   |
|---------------|---------|
| Realized PnL  | $65.00  |
| Sharpe Ratio  | 0.357   |
| Max Drawdown  | $3.00   |
| Win Rate      | 100%    |
| Total Trades  | 4       |

## Real market data replay (Coinbase — 2M events)

| Asset   | Events      | Trades | PnL (0.001 size) | PnL (scaled 1.0) | Max Drawdown |
|---------|-------------|--------|------------------|------------------|--------------|
| BTC-USD | 1,162,732   | 252    | +$26.26          | +$26,260         | $0.00        |
| ETH-USD | 868,251     | 92     | +$0.23           | +$225.90         | $0.00        |

## Strategy analysis

Mean reversion strategy using z-score signals on real Coinbase order book data.
Gross profitable on 2M real market events but fee-negative at standard retail rates.

### Optimization loop (BTC-USD, 1.16M events)

| Configuration                          | Trades | Gross PnL  | Fees (0.60%) | Net PnL    |
|----------------------------------------|--------|------------|--------------|------------|
| window=100, z=1.5 (original)           | 252    | +$26.26    | -$122.48     | -$96.22    |
| window=500, z=2.5 (better signals)     | 132    | +$13.15    | -$64.16      | -$51.01    |
| window=500, z=2.5, size=0.01 (scaled)  | 132    | +$131.48   | -$641.60     | -$510.12   |

### Break-even fee analysis

| Asset    | Gross PnL | Break-even fee  | Retail fee      | Verdict                          |
|----------|-----------|-----------------|-----------------|----------------------------------|
| BTC-USD  | +$13.15   | 0.1231% / side  | 0.60% / side    | Viable above $1M monthly volume  |
| ETH-USD  | +$0.09    | 0.0989% / side  | 0.60% / side    | Viable above $1M monthly volume  |

### Conclusion

The strategy is structurally a taker strategy — buying at the ask and selling at the bid,
always paying the spread plus fees. At standard retail rates (0.60% per side) fees are
roughly 5x larger than gross profit per trade. Break-even sits at 0.12% per side,
corresponding to Coinbase's $1M+ monthly volume tier.

The strategy is viable at institutional scale where maker rebates and negotiated fee
tiers bring costs below the break-even threshold. This is consistent with how
high-frequency mean reversion is actually deployed in production — exclusively by
firms with exchange relationships and volume-based fee advantages.

Potential Improvements: 
Restructure as a maker strategy posting limit orders to collect the spread rather than 
paying it, and add a trend filter to avoid trading in persistent downtrends.