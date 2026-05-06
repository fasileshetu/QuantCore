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
    int       quantity;
    bool      is_buy;
};