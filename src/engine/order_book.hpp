#pragma once
#include <map>
#include <string>

enum class Side { BUY, SELL };

struct Order {
    int    id;
    Side   side;
    double price;
    double quantity;   // changed from int to double
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
    std::map<double, double> bids_;
    std::map<double, double> asks_;
    std::map<int, Order>     orders_;
};