from flask import Flask, request, jsonify

app = Flask(__name__)

# YOUR MENU - NO EXTRAS ADDED
MENU_ITEMS = {
    "steak_burger": {"name": "Steak Burger", "price": 8.00},
    "chicken_burger": {"name": "Chicken Burger", "price": 7.50},
    "fish_burger": {"name": "Fish Burger", "price": 8.50},
    "veggie_burger": {"name": "Veggie Burger", "price": 7.00},
    "fries": {"name": "Fries", "price": 3.00},
    "onion_rings": {"name": "Onion Rings", "price": 3.50},
    "coleslaw": {"name": "Coleslaw", "price": 2.50},
    "coke": {"name": "Coke", "price": 2.00},
    "sprite": {"name": "Sprite", "price": 2.00},
    "water": {"name": "Water", "price": 1.50},
    "chocolate_shake": {"name": "Chocolate Shake", "price": 4.00},
    "vanilla_shake": {"name": "Vanilla Shake", "price": 4.00},
    "strawberry_shake": {"name": "Strawberry Shake", "price": 4.00},
    "ice_cream": {"name": "Ice Cream", "price": 3.00},
    "brownie": {"name": "Brownie", "price": 3.50},
    "apple_pie": {"name": "Apple Pie", "price": 4.00}
}

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Received:", data)
    
    action = data.get("data", {}).get("action", "start")
    
    if action == "start":
        # First screen: Show menu with quantity inputs
        children = [
            {"type": "TextHeading", "text": "Select your items"},
            {"type": "TextBody", "text": "Enter quantity for each item. Leave blank or 0 if you don't want it."}
        ]
        
        # Add quantity input for each menu item
        for item_id, item in MENU_ITEMS.items():
            children.append({
                "type": "TextInput",
                "name": item_id,
                "label": f"{item['name']} - ${item['price']:.2f}",
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
        # Calculate order total
        order_data = data.get("data", {})
        order_lines = []
        total = 0.0
        
        for item_id, item in MENU_ITEMS.items():
            qty_str = order_data.get(item_id, "0")
            try:
                qty = int(qty_str) if qty_str else 0
            except:
                qty = 0
                
            if qty > 0:
                line_total = qty * item["price"]
                total += line_total
                order_lines.append(f"{qty}x {item['name']} - ${line_total:.2f}")
        
        if not order_lines:
            order_text = "No items selected."
        else:
            order_text = "\n".join(order_lines) + f"\n\nTotal: ${total:.2f}"
        
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
        # Final confirmation - closes the Flow
        return jsonify({
            "screen": "DONE",
            "data": {}
        })
    
    # Default fallback
    return jsonify({"screen": "MENU", "data": {}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
