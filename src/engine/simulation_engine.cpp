#include "simulation_engine.hpp"
#include <iostream>
#include <iomanip>

void SimulationEngine::load_events(const std::vector<Event>& events) {
    events_ = events;
}

void SimulationEngine::run() {
    for (const Event& event : events_) {
        process_event(event);

        if (on_tick && book_.has_bid() && book_.has_ask()) {
            int signal = on_tick(book_, position_);
            if (signal == 1)
                execute_buy(book_.best_ask(), 100);
            else if (signal == -1)
                execute_sell(book_.best_bid(), 100);
        }
    }
}

void SimulationEngine::process_event(const Event& event) {
    if (event.type == EventType::ADD_ORDER) {
        Order o;
        o.id       = event.order_id;
        o.side     = event.is_buy ? Side::BUY : Side::SELL;
        o.price    = event.price;
        o.quantity = event.quantity;
        book_.add_order(o);
    }
    else if (event.type == EventType::CANCEL_ORDER) {
        book_.cancel_order(event.order_id);
    }
}

void SimulationEngine::execute_buy(double price, int quantity) {
    double cost = price * quantity;
    double prev_total = position_.avg_price * position_.quantity;

    position_.quantity  += quantity;
    position_.avg_price  = (prev_total + cost) / position_.quantity;
}

void SimulationEngine::execute_sell(double price, int quantity) {
    if (position_.quantity < quantity) return;

    double pnl = (price - position_.avg_price) * quantity;
    position_.realized_pnl += pnl;
    position_.quantity     -= quantity;
}

double SimulationEngine::get_pnl() const {
    return position_.realized_pnl;
}

void SimulationEngine::print_summary() const {
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Simulation Summary ===\n";
    std::cout << "  Realized PnL:  $" << position_.realized_pnl << "\n";
    std::cout << "  Open position: "  << position_.quantity << " shares\n";
    std::cout << "  Avg price:     $" << position_.avg_price << "\n";
}