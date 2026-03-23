# Payment Microservice
# Uses Strategy pattern

from flask import Flask, request, jsonify

app = Flask(__name__)


class PaymentStrategy:
    """Base payment strategy interface"""

    def process_payment(self, amount):
        raise NotImplementedError


class CreditCardStrategy(PaymentStrategy):
    """Credit card payment strategy"""

    def process_payment(self, amount):
        return {
            "message": f"Processed {amount} via Credit Card."
        }


class PayPalStrategy(PaymentStrategy):
    """PayPal payment strategy"""

    def process_payment(self, amount):
        return {
            "message": f"Processed {amount} via PayPal."
        }


class PaymentContext:
    """Payment context that uses different strategies"""

    def __init__(self):
        self._strategies = {
            'credit_card': CreditCardStrategy(),
            'paypal': PayPalStrategy()
        }

    def execute_payment(self, method, amount):
        """Execute payment using specified method"""
        if method not in self._strategies:
            return {
                "error": f"Unsupported payment method: {method}"
            }

        strategy = self._strategies[method]
        return strategy.process_payment(amount)


# Initialize payment context
payment_context = PaymentContext()


# REST API Endpoints
@app.route('/payment/process', methods=['POST'])
def process_payment():
    """Process a payment"""
    data = request.json
    method = data.get('method', 'credit_card')
    amount = data.get('amount')

    if not amount:
        return jsonify({"error": "Amount is required"}), 400

    result = payment_context.execute_payment(method, amount)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result), 200


@app.route('/payment/methods', methods=['GET'])
def get_payment_methods():
    """Get available payment methods"""
    return jsonify({
        "methods": ["credit_card", "paypal"]
    }), 200


if __name__ == '__main__':
    # Payment service runs on port 5002
    print("Starting Payment Service on port 5002...")
    app.run(host='0.0.0.0', port=5002, debug=True)