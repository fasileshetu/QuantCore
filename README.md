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