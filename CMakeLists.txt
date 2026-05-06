cmake_minimum_required(VERSION 3.15)
project(quantcore)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(backtester_test
    src/engine/order_book.cpp
    src/engine/simulation_engine.cpp
    src/engine/main.cpp
)

# pybind11 module
find_package(pybind11 REQUIRED)

pybind11_add_module(quantcore
    src/bindings/bindings.cpp
    src/engine/order_book.cpp
    src/engine/simulation_engine.cpp
)

target_include_directories(quantcore PRIVATE src/engine)
target_include_directories(backtester_test PRIVATE src/engine)