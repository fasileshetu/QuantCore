# QuantCore

High-performance algorithmic trading backtester with a Python/C++ hybrid architecture.
Strategy logic is written in Python while a C++ core handles tick parsing, order book
maintenance, order matching, and real-time PnL tracking — connected via pybind11 bindings.

## Architecture

    Python layer (strategy + analysis)
            ↓  pybind11
    C++ core (event loop + order book + matching engine)
            ↓
    Historical market data (NASDAQ ITCH 5.0)

## Stack

- C++17 — order book, event loop, matching engine, position tracking
- pybind11 — Python/C++ bindings
- Python — strategy logic, signal generation, parameter tuning
- pandas / numpy / matplotlib — post-run analysis and plotting
- CMake — build system

## Build

```
bash
mkdir build && cd build
cmake .. -DCMAKE_CXX_COMPILER=/usr/bin/clang++
make
./backtester_test
```
