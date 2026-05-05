#include "order_book.hpp"
#include <iostream>

int main() {
    OrderBook book;

    book.add_order({1, Side::BUY,  99.50, 100});
    book.add_order({2, Side::BUY,  99.00, 200});
    book.add_order({3, Side::SELL, 100.00, 150});
    book.add_order({4, Side::SELL, 100.50,  50});

    book.print();

    std::cout << "\nBest bid: " << book.best_bid() << "\n";
    std::cout << "Best ask: " << book.best_ask() << "\n";
    std::cout << "Mid price: " << book.mid_price() << "\n";

    std::cout << "\nCancelling order 1 (bid at 99.50)...\n";
    book.cancel_order(1);
    book.print();

    return 0;
}