# Orchestrator

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Microservice URLs
INVENTORY_SERVICE_URL = "http://localhost:5001"
PAYMENT_SERVICE_URL = "http://localhost:5002"
CART_SERVICE_URL = "http://localhost:5003"


class RetailOrchestrator:
    """Orchestrates the retail workflow across microservices"""

    def checkout(self, item, quantity, method, amount):
        """
        Orchestrates checkout process (Test Case 3):
        1. Check inventory availability
        2. Process payment
        3. Update inventory
        """
        # Step 1: Check inventory availability
        try:
            check_response = requests.post(
                f"{INVENTORY_SERVICE_URL}/inventory/check",
                json={"item": item, "quantity": quantity},
                timeout=5
            )

            if check_response.status_code != 200:
                return {"error": "Inventory service unavailable"}, 503

            availability = check_response.json()

            if not availability['available']:
                return {
                    "error": f"Not enough stock for {item}. Available: {availability['stock']}"
                }, 400
        except requests.exceptions.RequestException as e:
            return {"error": f"Inventory service error: {str(e)}"}, 503

        # Step 2: Process payment
        try:
            payment_response = requests.post(
                f"{PAYMENT_SERVICE_URL}/payment/process",
                json={"method": method, "amount": amount},
                timeout=5
            )

            if payment_response.status_code != 200:
                return {"error": "Payment processing failed"}, 500

            payment_result = payment_response.json()

            if 'error' in payment_result:
                return {"error": payment_result['error']}, 400

        except requests.exceptions.RequestException as e:
            return {"error": f"Payment service error: {str(e)}"}, 503

        # Step 3: Update inventory (remove purchased items)
        try:
            inventory_response = requests.post(
                f"{INVENTORY_SERVICE_URL}/inventory/remove",
                json={"item": item, "quantity": quantity},
                timeout=5
            )

            if inventory_response.status_code != 200:
                # Payment already processed, this is a critical error
                return {
                    "error": "Inventory update failed after payment",
                    "payment": payment_result
                }, 500
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Inventory update error: {str(e)}",
                "payment": payment_result
            }, 503

        # Return payment result message
        return payment_result, 200


# Initialize orchestrator
orchestrator = RetailOrchestrator()


# REST API Endpoints
@app.route('/checkout', methods=['POST'])
def checkout_endpoint():
    """
    Process checkout (Test Case 3)
    Example: curl -X POST http://localhost:5000/checkout
             -H "Content-Type: application/json"
             -d '{"item": "Laptop", "quantity": 2, "method": "credit_card", "amount": 2000}'
    """
    data = request.json
    item = data.get('item')
    quantity = data.get('quantity')
    method = data.get('method', 'credit_card')
    amount = data.get('amount')

    if not item or not quantity or not amount:
        return jsonify({"error": "item, quantity, and amount are required"}), 400

    result, status_code = orchestrator.checkout(item, quantity, method, amount)
    return jsonify(result), status_code


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    # Orchestrator service runs on port 5000
    print("=" * 70)
    print("Retail Orchestrator Service")
    print("=" * 70)
    print("This service coordinates the microservices:")
    print(f"  - Inventory Service: {INVENTORY_SERVICE_URL}")
    print(f"  - Payment Service: {PAYMENT_SERVICE_URL}")
    print("=" * 70)
    app.run(host='0.0.0.0', port=5000, debug=True)