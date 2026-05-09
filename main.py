from flask import Flask, request, jsonify

app = Flask(__name__)

# Store orders in memory. In production you'd use a database.
orders = {}

def get_next_dish(data, current_idx):
    menu = [
        ("qty_steak", "New York Steak", "steak"),
        ("qty_coq_au_vin", "Coq Au Vin", "coq"),
        ("qty_eggplant_parm", "Eggplant Parmesan", "eggplant"),
        ("qty_tomato_ceviche", "Tomato Ceviche", "tomato_ceviche"),
        ("qty_coco_ceviche", "Coconut Ceviche", "coco_ceviche"),
        ("qty_chicken_pasta", "Chicken Pasta", "chicken_pasta"),
        ("qty_beef_pasta", "Beef Pasta", "beef_pasta"),
        ("qty_veg_pasta", "Veg Pasta", "veg_pasta"),
        ("qty_chicken_curry", "Chicken Curry", "chicken_curry"),
        ("qty_fish_curry", "Fish Curry", "fish_curry"),
        ("qty_veg_curry", "Veg Curry", "veg_curry"),
        ("qty_piz_canadian", "Canadian Pizza", "piz_canadian"),
        ("qty_pizza_hawaiian", "Hawaiian Pizza", "pizza_hawaiian"),
        ("qty_piz_pepperoni", "Pepperoni Pizza", "piz_pepperoni"),
        ("qty_piz_veggie", "Veggie Pizza", "piz_veggie"),
        ("qty_piz_mediterranean", "Mediterranean Pizza", "piz_mediterranean")
    ]
    
    for i in range(current_idx, len(menu)):
        qty_key, name, prefix = menu[i]
        qty = int(data.get(qty_key, 0) or 0)
        if qty > 0:
            return i, qty_key, name, prefix, qty
    return None, None, None, None, 0

@app.route("/", methods=["POST"])
def endpoint():
    req = request.get_json()
    screen = req.get("screen")
    data = req.get("data", {})
    flow_token = req.get("flow_token")
    
    if flow_token not in orders:
        orders[flow_token] = {"items": {}, "current_dish_idx": 0, "current_item_num": 1}
    
    order = orders[flow_token]
    
    # Screen 1: WELCOME -> QUANTITIES
    if screen == "WELCOME":
        return jsonify({"screen": "QUANTITIES", "data": {}})
    
    # Screen 2: QUANTITIES -> DETAILS
    if screen == "QUANTITIES":
        order["items"] = data
        order["current_dish_idx"] = 0
        order["current_item_num"] = 1
        # Find first dish to customize
        idx, qty_key, name, prefix, qty = get_next_dish(data, 0)
        if idx is None:
            return jsonify({"screen": "REVIEW", "data": {"order_summary": "No items selected."}})
        return build_detail_screen(name, prefix, 1, qty)
    
    # Screen 3: DETAILS -> next DETAILS or REVIEW
    if screen == "DETAILS":
        # Save the detail they just entered
        for k, v in data.items():
            order["items"][k] = v
        
        # Check if more of same dish
        idx, qty_key, name, prefix, total_qty = get_next_dish(order["items"], order["current_dish_idx"])
        if order["current_item_num"] < total_qty:
            order["current_item_num"] += 1
            return build_detail_screen(name, prefix, order["current_item_num"], total_qty)
        
        # Move to next dish type
        order["current_dish_idx"] = idx + 1
        order["current_item_num"] = 1
        idx, qty_key, name, prefix, qty = get_next_dish(order["items"], order["current_dish_idx"])
        if idx is None:
            # All done, go to review
            summary = build_summary(order["items"])
            return jsonify({"screen": "REVIEW", "data": {"order_summary": summary}})
        return build_detail_screen(name, prefix, 1, qty)
    
    # Screen 4: REVIEW -> SUCCESS
    if screen == "REVIEW":
        return jsonify({"screen": "SUCCESS", "data": {}})
    
    return jsonify({"screen": "WELCOME", "data": {}})

def build_detail_screen(dish_name, prefix, item_num, total_qty):
    children = [
        {"type": "TextHeading", "text": f"{dish_name} #{item_num} of {total_qty}"},
    ]
    
    if prefix == "steak":
        children.append({
            "type": "Dropdown", 
            "name": f"{prefix}_{item_num}_doneness", 
            "label": "Doneness", 
            "required": True,
            "data-source": [
                {"id": "rare", "title": "Rare"},
                {"id": "med_rare", "title": "Medium Rare"},
                {"id": "medium", "title": "Medium"},
                {"id": "med_well", "title": "Medium Well"},
                {"id": "well", "title": "Well Done"}
            ]
        })
    elif "piz" in prefix or "pizza" in prefix:
        toppings = [
            {"id": "mushrooms", "title": "Mushrooms"},
            {"id": "onions", "title": "Onions"},
            {"id": "red_onion", "title": "Red Onion"},
            {"id": "extra_cheese", "title": "Extra Cheese"},
            {"id": "goat_cheese", "title": "Goat Cheese"},
            {"id": "pineapple", "title": "Pineapple"},
            {"id": "jalapeno", "title": "Jalapeno"},
            {"id": "extra_queso", "title": "Extra Queso"}
        ]
        if prefix in ["piz_canadian", "pizza_hawaiian", "piz_pepperoni"]:
            toppings = [
                {"id": "canadian_bacon", "title": "Canadian Bacon"},
                {"id": "ham", "title": "Ham"},
                {"id": "pepperoni", "title": "Pepperoni"}
            ] + toppings
        
        children.append({
            "type": "CheckboxGroup",
            "name": f"{prefix}_{item_num}_toppings",
            "label": "Add up to 2 toppings",
            "max-selected-items": 2,
            "data-source": toppings
        })
    
    children.append({
        "type": "TextArea",
        "name": f"{prefix}_{item_num}_note",
        "label": "Special instructions",
        "required": False
    })
    children.append({
        "type": "Footer",
        "label": "Continue",
        "on-click-action": {"name": "data_exchange", "payload": {}}
    })
    
    return jsonify({
        "screen": "DETAILS",
        "data": {
            "layout": {
                "type": "SingleColumnLayout",
                "children": children
            }
        }
    })

def build_summary(items):
    lines = []
    for k, v in items.items():
        if k.startswith("qty_") and int(v or 0) > 0:
            lines.append(f"{k.replace('qty_', '').replace('_', ' ').title()}: {v}")
    return "\n".join(lines) if lines else "No items"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)