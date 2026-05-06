cmake_minimum_required(VERSION 3.15)
project(backtester)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(backtester_test
    src/engine/order_book.cpp
    src/engine/simulation_engine.cpp
    src/engine/main.cpp
)