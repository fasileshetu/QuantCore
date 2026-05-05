#pragma once
#include <map>
#include <string>

enum class Side { BUY, SELL };

struct Order {
    int    id;
    Side   side;
    double price;
    int    quantity;
};

class OrderBook {
public:
    void   add_order(const Order& order);
    void   cancel_order(int order_id);

    double best_bid() const;
    double best_ask() const;
    double mid_price() const;

    bool   has_bid() const;
    bool   has_ask() const;

    void   print() const;

private:
    // price -> total quantity at that level
    std::map<double, int> bids_;   // highest price = best bid
    std::map<double, int> asks_;   // lowest price  = best ask

    // order_id -> Order (needed for cancellation)
    std::map<int, Order> orders_;
};