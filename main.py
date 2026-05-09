from flask import Flask, request, jsonify
import base64
import json

app = Flask(__name__)

# YOUR ACTUAL MENU FROM LA ISLA DULCE CAFE - GTQ PRICES
MENU_ITEMS = {
    "curry_vegetarian": {"name": "Green Curry - Vegetarian", "price": 135},
    "curry_chicken": {"name": "Green Curry - Chicken", "price": 135},
    "curry_fish": {"name": "Green Curry - Fish", "price": 150},
    "robalo_ceviche": {"name": "Robalo Ceviche", "price": 130},
    "pasta_chicken_beef": {"name": "Fettuchine - Chicken/Beef", "price": 135},
    "pasta_vegetarian": {"name": "Fettuchine - Vegetarian", "price": 120},
    "steak_diane": {"name": "Steak Diane", "price": 195},
    "coq_au_vin": {"name": "Coq Au Vin", "price": 150},
    "eggplant_parmigiana": {"name": "Eggplant Parmigiana", "price": 145},
    "pizza_canadian": {"name": "Canadian Pizza", "price": 115},
    "pizza_hawaiian": {"name": "Hawaiian Pizza", "price": 115},
    "pizza_pepperoni": {"name": "Pepperoni Pizza", "price": 115},
    "pizza_isla_vegetarian": {"name": "La Isla Vegetarian Pizza", "price": 115},
    "pizza_isla_mediterranean": {"name": "La Isla Mediterranean Pizza", "price": 115},
    "topping_tomatoes": {"name": "Extra Tomatoes", "price": 10},
    "topping_pineapple": {"name": "Extra Pineapple", "price": 10},
    "topping_jalapeno": {"name": "Extra Jalapeno Pepper", "price": 10},
    "topping_mushrooms": {"name": "Extra Mushrooms", "price": 10},
    "topping_red_onion": {"name": "Extra Red Onion", "price": 10},
    "topping_extra_cheese": {"name": "Extra Cheese", "price": 10}
}

def make_response(payload):
    # Meta requires ALL responses to be Base64 encoded
    return base64.b64encode(json.dumps(payload).encode()).decode()

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
    except:
        # Health check with no JSON body
        return make_response({"data": {"status": "active"}}), 200, {"Content-Type": "text/plain"}
    
    if not data:
        return make_response({"data": {"status": "active"}}), 200, {"Content-Type": "text/plain"}
    
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
        
        payload = {
            "screen": "CART",
            "data": {},
            "layout": {
                "type": "SingleColumnLayout",
                "children": children
            }
        }
        return make_response(payload), 200, {"Content-Type": "text/plain"}
    
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
        
        payload = {
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
        }
        return make_response(payload), 200, {"Content-Type": "text/plain"}
    
    elif action == "submit":
        payload = {
            "screen": "DONE",
            "data": {}
        }
        return make_response(payload), 200, {"Content-Type": "text/plain"}
    
    return make_response({"screen": "MENU", "data": {}}), 200, {"Content-Type": "text/plain"}

@app.route("/", methods=["GET"])
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
