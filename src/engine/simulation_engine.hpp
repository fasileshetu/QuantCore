#pragma once
#include "order_book.hpp"
#include "event.hpp"
#include <vector>
#include <functional>

struct Position {
    int    quantity = 0;
    double avg_price = 0.0;
    double realized_pnl = 0.0;
};

class SimulationEngine {
public:
    void load_events(const std::vector<Event>& events);
    void run();

    double get_pnl() const;
    void   print_summary() const;

    // strategy hook — the engine calls this on every tick
    // the strategy returns 1 to buy, -1 to sell, 0 to do nothing
    std::function<int(const OrderBook&, const Position&)> on_tick;

private:
    OrderBook          book_;
    Position           position_;
    std::vector<Event> events_;
    int                next_order_id_ = 1000;

    void process_event(const Event& event);
    void execute_buy(double price, int quantity);
    void execute_sell(double price, int quantity);
};