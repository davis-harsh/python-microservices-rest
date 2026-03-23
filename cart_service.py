# Cart Microservice
# Uses Repository pattern

from flask import Flask, request, jsonify

app = Flask(__name__)


class Cart:
    """Individual cart for a specific user"""

    def __init__(self, user_id):
        self.user_id = user_id
        self.items = []

    def add_item(self, item, quantity):
        self.items.append((item, quantity))
        return {"message": f"Added {quantity} {item}(s) to cart for user {self.user_id}"}

    def get_items(self):
        return self.items

    def clear(self):
        self.items = []
        return {"message": f"Cart cleared for user {self.user_id}"}


class CartRepository:
    """Repository manages all carts - one per user"""

    def __init__(self):
        self._carts = {}

    def get_cart(self, user_id):
        if user_id not in self._carts:
            self._carts[user_id] = Cart(user_id)
        return self._carts[user_id]

    def remove_cart(self, user_id):
        if user_id in self._carts:
            del self._carts[user_id]
            return {"message": f"Cart removed for user {user_id}"}
        return {"error": "Cart not found"}


# Initialize the repository
cart_repo = CartRepository()


# REST API Endpoints
@app.route('/cart/<user_id>/add', methods=['POST'])
def add_to_cart(user_id):
    """Add item to user's cart"""
    data = request.json
    item = data.get('item')
    quantity = data.get('quantity', 1)

    cart = cart_repo.get_cart(user_id)
    result = cart.add_item(item, quantity)
    return jsonify(result), 200


@app.route('/cart/<user_id>', methods=['GET'])
def get_cart(user_id):
    """Get user's cart contents"""
    cart = cart_repo.get_cart(user_id)
    return jsonify({"user_id": user_id, "items": cart.get_items()}), 200


@app.route('/cart/<user_id>/clear', methods=['DELETE'])
def clear_cart(user_id):
    """Clear user's cart"""
    cart = cart_repo.get_cart(user_id)
    result = cart.clear()
    return jsonify(result), 200


if __name__ == '__main__':
    # Cart service runs on port 5001
    print("Starting Cart Service on port 5001...")
    app.run(host='0.0.0.0', port=5003, debug=True)