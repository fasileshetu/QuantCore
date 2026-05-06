#include "order_book.hpp"
#include "simulation_engine.hpp"
#include <iostream>
#include <vector>

int main() {
    SimulationEngine engine;

    // simple strategy: buy if spread is tight, sell if we're profitable
    engine.on_tick = [](const OrderBook& book, const Position& pos) -> int {
        double spread = book.best_ask() - book.best_bid();
        double mid    = book.mid_price();

        if (spread < 1.0 && pos.quantity == 0)
            return 1;   // buy when spread is tight and flat
        if (pos.quantity > 0 && book.best_bid() > pos.avg_price + 0.50)
            return -1;  // sell when 50 cents profitable
        return 0;
    };

    // simulate a sequence of market events
    std::vector<Event> events = {
        {EventType::ADD_ORDER, 1, 99.50, 100, true },   // bid
        {EventType::ADD_ORDER, 2, 100.00, 150, false},   // ask
        {EventType::ADD_ORDER, 3, 99.00, 200, true },   // bid
        {EventType::ADD_ORDER, 4, 100.50,  50, false},   // ask
        {EventType::ADD_ORDER, 5, 99.75, 100, true },   // tighter bid
        {EventType::ADD_ORDER, 6, 100.25, 100, false},   // tighter ask
        {EventType::CANCEL_ORDER, 2, 0, 0, false},       // ask removed
        {EventType::ADD_ORDER, 7, 100.10, 200, false},   // new ask
        {EventType::ADD_ORDER, 8, 100.00, 100, true },   // bid moves up
    };

    engine.load_events(events);
    engine.run();
    engine.print_summary();

    return 0;
}