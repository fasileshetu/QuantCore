#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>
#include "order_book.hpp"
#include "simulation_engine.hpp"

namespace py = pybind11;

PYBIND11_MODULE(quantcore, m) {
    m.doc() = "QuantCore — high-performance backtesting engine";

    // expose Side enum
    py::enum_<Side>(m, "Side")
        .value("BUY", Side::BUY)
        .value("SELL", Side::SELL)
        .export_values();

    // expose EventType enum
    py::enum_<EventType>(m, "EventType")
        .value("ADD_ORDER", EventType::ADD_ORDER)
        .value("CANCEL_ORDER", EventType::CANCEL_ORDER)
        .value("TRADE", EventType::TRADE)
        .export_values();

    // expose Event struct
    py::class_<Event>(m, "Event")
        .def(py::init<>())
        .def_readwrite("type",      &Event::type)
        .def_readwrite("order_id",  &Event::order_id)
        .def_readwrite("price",     &Event::price)
        .def_readwrite("quantity",  &Event::quantity)
        .def_readwrite("is_buy",    &Event::is_buy);

    // expose OrderBook
    py::class_<OrderBook>(m, "OrderBook")
        .def(py::init<>())
        .def("add_order",     &OrderBook::add_order)
        .def("cancel_order",  &OrderBook::cancel_order)
        .def("best_bid",      &OrderBook::best_bid)
        .def("best_ask",      &OrderBook::best_ask)
        .def("mid_price",     &OrderBook::mid_price)
        .def("has_bid",       &OrderBook::has_bid)
        .def("has_ask",       &OrderBook::has_ask)
        .def("print",         &OrderBook::print);

    // expose Order struct
    py::class_<Order>(m, "Order")
        .def(py::init<>())
        .def_readwrite("id",       &Order::id)
        .def_readwrite("side",     &Order::side)
        .def_readwrite("price",    &Order::price)
        .def_readwrite("quantity", &Order::quantity);

    // expose Position struct
    py::class_<Position>(m, "Position")
        .def(py::init<>())
        .def_readonly("quantity",     &Position::quantity)
        .def_readonly("avg_price",    &Position::avg_price)
        .def_readonly("realized_pnl", &Position::realized_pnl);

    // expose SimulationEngine
    py::class_<SimulationEngine>(m, "SimulationEngine")
        .def(py::init<>())
        .def("load_events",   &SimulationEngine::load_events)
        .def("run",           &SimulationEngine::run)
        .def("get_pnl",       &SimulationEngine::get_pnl)
        .def("print_summary", &SimulationEngine::print_summary)
        .def("get_pnl_history", &SimulationEngine::get_pnl_history)
        .def("get_mid_history",  &SimulationEngine::get_mid_history)
        .def_readwrite("on_tick", &SimulationEngine::on_tick);
}