from flask import Flask, request, jsonify

app = Flask(__name__)

# YOUR ACTUAL MENU FROM LA ISLA DULCE CAFE - GTQ PRICES
MENU_ITEMS = {
    # CURRY
    "curry_vegetarian": {"name": "Green Curry - Vegetarian", "price": 135},
    "curry_chicken": {"name": "Green Curry - Chicken", "price": 135},
    "curry_fish": {"name": "Green Curry - Fish", "price": 150},
    
    # CEVICHE
    "robalo_ceviche": {"name": "Robalo Ceviche", "price": 130},
    
    # PASTA
    "pasta_chicken_beef": {"name": "Fettuchine - Chicken/Beef", "price": 135},
    "pasta_vegetarian": {"name": "Fettuchine - Vegetarian", "price": 120},
    
    # MAINS
    "steak_diane": {"name": "Steak Diane", "price": 195},
    "coq_au_vin": {"name": "Coq Au Vin", "price": 150},
    "eggplant_parmigiana": {"name": "Eggplant Parmigiana", "price": 145},
    
    # PIZZA - ALL GTQ 115
    "pizza_canadian": {"name": "Canadian Pizza", "price": 115},
    "pizza_hawaiian": {"name": "Hawaiian Pizza", "price": 115},
    "pizza_pepperoni": {"name": "Pepperoni Pizza", "price": 115},
    "pizza_isla_vegetarian": {"name": "La Isla Vegetarian Pizza", "price": 115},
    "pizza_isla_mediterranean": {"name": "La Isla Mediterranean Pizza", "price": 115},
    
    # ADDITIONAL TOPPINGS
    "topping_tomatoes": {"name": "Extra Tomatoes", "price": 10},
    "topping_pineapple": {"name": "Extra Pineapple", "price": 10},
    "topping_jalapeno": {"name": "Extra Jalapeno Pepper", "price": 10},
    "topping_mushrooms": {"name": "Extra Mushrooms", "price": 10},
    "topping_red_onion": {"name": "Extra Red Onion", "price": 10},
    "topping_extra_cheese": {"name": "Extra Cheese", "price": 10}
}

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Received:", data)
    
    action = data.get("data", {}).get("action", "start")
    
    if action == "start":
        children = [
            {"type": "TextHeading", "text": "La Isla Dulce - Place Order"},
            {"type": "TextBody", "text": "Enter quantity for each item. Orders by 4 PM for 7 PM seating. Leave blank or 0 if you don't want it."}
        ]
        
        for item_id, item in MENU_ITEMS.items():
            children.append({
                "type": "TextInput",
                "name": item_id,
                "label": f"{item['name']} - GTQ {item['price']}",
                "input-type": "number"
            })
        
        children.append({
            "type": "Footer",
            "label": "Review Order",
            "on-click-action": {
                "name": "data_exchange",
                "payload": {"action": "review"}
            }
        })
        
        return jsonify({
            "screen": "CART",
            "data": {},
            "layout": {
                "type": "SingleColumnLayout",
                "children": children
            }
        })
    
    elif action == "review":
        order_data = data.get("data", {})
        order_lines = []
        total = 0
        
        for item_id, item in MENU_ITEMS.items():
            qty_str = order_data.get(item_id, "0")
            try:
                qty = int(qty_str) if qty_str else 0
            except:
                qty = 0
                
            if qty > 0:
                line_total = qty * item["price"]
                total += line_total
                order_lines.append(f"{qty}x {item['name']} - GTQ {line_total}")
        
        if not order_lines:
            order_text = "No items selected."
        else:
            order_text = "\n".join(order_lines) + f"\n\nTotal: GTQ {total}"
        
        return jsonify({
            "screen": "REVIEW",
            "data": {"order_summary": order_text},
            "layout": {
                "type": "SingleColumnLayout",
                "children": [
                    {"type": "TextHeading", "text": "Review Your Order"},
                    {"type": "TextBody", "text": "${data.order_summary}"},
                    {
                        "type": "Footer",
                        "label": "Submit Order",
                        "on-click-action": {
                            "name": "data_exchange",
                            "payload": {"action": "submit"}
                        }
                    }
                ]
            }
        })
    
    elif action == "submit":
        return jsonify({
            "screen": "DONE",
            "data": {}
        })
    
    return jsonify({"screen": "MENU", "data": {}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
