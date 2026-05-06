#pragma once
#include <string>

enum class EventType {
    ADD_ORDER,
    CANCEL_ORDER,
    TRADE
};

struct Event {
    EventType type;
    int       order_id;
    double    price;
    double    quantity;   // changed from int to double
    bool      is_buy;
};