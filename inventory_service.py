# Inventory Microservice
# Uses Observer pattern

from flask import Flask, request, jsonify

app = Flask(__name__)


class Inventory:
    """Inventory subject that notifies observers of stock changes"""

    def __init__(self):
        self.stock = {}
        self._observers = []

    def attach(self, observer):
        """Register an observer"""
        if observer not in self._observers:
            self._observers.append(observer)

    def notify(self, item, old_quantity, new_quantity):
        """Notify all observers of inventory changes"""
        for observer in self._observers:
            observer.update(item, old_quantity, new_quantity)

    def add_item(self, item, quantity):
        """Add stock to inventory"""
        old_quantity = self.stock.get(item, 0)
        self.stock[item] = old_quantity + quantity
        new_quantity = self.stock[item]

        self.notify(item, old_quantity, new_quantity)
        return {
            "message": f"{item} stock updated.",
            "total": new_quantity
        }

    def update_item(self, item, quantity):
        """Update stock for an item (for PUT requests)"""
        old_quantity = self.stock.get(item, 0)
        self.stock[item] = quantity

        self.notify(item, old_quantity, quantity)
        return {"message": f"{item} stock updated."}

    def remove_item(self, item, quantity):
        """Remove stock from inventory"""
        old_quantity = self.stock.get(item, 0)

        if item in self.stock and self.stock[item] >= quantity:
            self.stock[item] -= quantity
            new_quantity = self.stock[item]

            self.notify(item, old_quantity, new_quantity)
            return {
                "success": True,
                "message": f"Removed {quantity} {item}(s) from inventory",
                "remaining": new_quantity
            }
        else:
            return {
                "success": False,
                "message": f"Not enough {item} in stock",
                "available": old_quantity
            }

    def check_availability(self, item, quantity):
        """Check if item is available in requested quantity"""
        available = self.stock.get(item, 0)
        return {
            "available": available >= quantity,
            "stock": available,
            "requested": quantity
        }

    def get_stock(self, item=None):
        """Get stock level for specific item or all items"""
        if item:
            stock_level = self.stock.get(item, 0)
            return {"item": item, "stock": stock_level}
        return {"stock": self.stock}


class LowStockObserver:
    """Observer that alerts when stock is low"""

    def __init__(self, threshold=10):
        self.threshold = threshold

    def update(self, item, old_quantity, new_quantity):
        if new_quantity < self.threshold and old_quantity >= self.threshold:
            print(f"🚨 ALERT: {item} is now LOW STOCK! Quantity: {new_quantity}")
        elif new_quantity == 0:
            print(f"🚨 CRITICAL: {item} is OUT OF STOCK!")


# Initialize inventory and observers
inventory = Inventory()
low_stock_observer = LowStockObserver(threshold=5)
inventory.attach(low_stock_observer)


# REST API Endpoints matching test cases
@app.route('/inventory/<item>', methods=['PUT'])
def update_inventory(item):
    """
    Update inventory stock (Test Case 1)
    Example: curl -X PUT http://localhost:5001/inventory/Laptop
             -H "Content-Type: application/json" -d '{"quantity": 5}'
    """
    data = request.json
    quantity = data.get('quantity')

    if quantity is None:
        return jsonify({"error": "quantity is required"}), 400

    result = inventory.update_item(item, quantity)
    return jsonify(result), 200


@app.route('/inventory/<item>', methods=['GET'])
def get_inventory_item(item):
    """
    Get stock level for specific item (Test Case 2)
    Example: curl -X GET http://localhost:5001/inventory/Laptop
    """
    result = inventory.get_stock(item)
    return jsonify(result), 200


@app.route('/inventory/add', methods=['POST'])
def add_inventory():
    """Add items to inventory"""
    data = request.json
    item = data.get('item')
    quantity = data.get('quantity', 1)

    result = inventory.add_item(item, quantity)
    return jsonify(result), 200


@app.route('/inventory/remove', methods=['POST'])
def remove_inventory():
    """Remove items from inventory"""
    data = request.json
    item = data.get('item')
    quantity = data.get('quantity', 1)

    result = inventory.remove_item(item, quantity)
    status_code = 200 if result['success'] else 400
    return jsonify(result), status_code


@app.route('/inventory/check', methods=['POST'])
def check_inventory():
    """Check if item is available"""
    data = request.json
    item = data.get('item')
    quantity = data.get('quantity', 1)

    result = inventory.check_availability(item, quantity)
    return jsonify(result), 200


@app.route('/inventory', methods=['GET'])
def get_all_inventory():
    """Get all inventory stock levels"""
    result = inventory.get_stock()
    return jsonify(result), 200


if __name__ == '__main__':
    # Inventory service runs on port 5001
    print("Starting Inventory Service on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)
