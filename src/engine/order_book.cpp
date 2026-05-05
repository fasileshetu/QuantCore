#include "order_book.hpp"
#include <stdexcept>
#include <iostream>
#include <iomanip>

void OrderBook::add_order(const Order& order) {
    orders_[order.id] = order;

    if (order.side == Side::BUY)
        bids_[order.price] += order.quantity;
    else
        asks_[order.price] += order.quantity;
}

void OrderBook::cancel_order(int order_id) {
    auto it = orders_.find(order_id);
    if (it == orders_.end())
        throw std::runtime_error("cancel_order: unknown order id");

    const Order& o = it->second;
    if (o.side == Side::BUY) {
        bids_[o.price] -= o.quantity;
        if (bids_[o.price] <= 0) bids_.erase(o.price);
    } else {
        asks_[o.price] -= o.quantity;
        if (asks_[o.price] <= 0) asks_.erase(o.price);
    }

    orders_.erase(it);
}

double OrderBook::best_bid() const {
    if (bids_.empty()) throw std::runtime_error("best_bid: no bids");
    return bids_.rbegin()->first;   // highest key
}

double OrderBook::best_ask() const {
    if (asks_.empty()) throw std::runtime_error("best_ask: no asks");
    return asks_.begin()->first;    // lowest key
}

double OrderBook::mid_price() const {
    return (best_bid() + best_ask()) / 2.0;
}

bool OrderBook::has_bid() const { return !bids_.empty(); }
bool OrderBook::has_ask() const { return !asks_.empty(); }

void OrderBook::print() const {
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Order Book ===\n";
    std::cout << "  ASKS:\n";
    for (auto it = asks_.rbegin(); it != asks_.rend(); ++it)
        std::cout << "    " << it->first << "  qty: " << it->second << "\n";
    std::cout << "  --- spread ---\n";
    std::cout << "  BIDS:\n";
    for (auto it = bids_.rbegin(); it != bids_.rend(); ++it)
        std::cout << "    " << it->first << "  qty: " << it->second << "\n";
}