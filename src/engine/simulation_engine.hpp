#pragma once
#include "order_book.hpp"
#include "event.hpp"
#include <vector>
#include <functional>

struct Position {
    double    quantity    = 0;
    double avg_price   = 0.0;
    double realized_pnl = 0.0;
};

class SimulationEngine {
public:
    void load_events(const std::vector<Event>& events);
    void run();

    double get_pnl() const;
    void   print_summary() const;

    const std::vector<double>& get_pnl_history() const;
    const std::vector<double>& get_mid_history()  const;

    std::function<int(const OrderBook&, const Position&)> on_tick;

private:
    OrderBook          book_;
    Position           position_;
    std::vector<Event> events_;
    std::vector<double> pnl_history_;
    std::vector<double> mid_history_;
    int                next_order_id_ = 1000;

    void process_event(const Event& event);
    void execute_buy(double price, double quantity);
    void execute_sell(double price, double quantity);
};