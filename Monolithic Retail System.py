
# D780: Integrate Components in Step 2 into a Monolithic Retail System
# with testing codes

# Cart Component in Factory Pattern
class Cart:
    # Manages items in the shopping cart
    def __init__(self):
        self.items = []

    def add_item(self, item, quantity):
        self.items.append((item, quantity))
        print(f"Added {quantity} {item}(s) to the cart.")

class CartFactory:
    # Factory class to create a Cart
    @staticmethod
    def create_cart():
        return Cart()

# Inventory Component in Observer Pattern
class InventoryObserver:
    # Sends notifications when inventory is updated
    def notify(self, item, quantity):
        print(f"Notification: {item} stock is now {quantity}.")

class Inventory:
    # Manages stock and notifies observers
    def __init__(self):
        self.stock = {}
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def add_item(self, item, quantity):
        self.stock[item] = self.stock.get(item, 0) + quantity
        self.notify_observers(item)

    def notify_observers(self, item):
        for observer in self.observers:
            observer.notify(item, self.stock[item])

# Payment Component in Strategy Pattern
class PaymentStrategy:
    # Abstract class for payment strategies
    def pay(self, amount):
        raise NotImplementedError

class CreditCardPayment(PaymentStrategy):
    # Processes payment via credit card
    def pay(self, amount):
        print(f"Processing {amount} via Credit Card.")

class PayPalPayment(PaymentStrategy):
    # Processes payment via PayPal
    def pay(self, amount):
        print(f"Processing {amount} via PayPal.")

class PaymentProcessor:
    # Handles payment using a selected strategy
    def __init__(self, strategy):
        self.strategy = strategy

    def process_payment(self, amount):
        self.strategy.pay(amount)

# Main system that integrates cart, inventory, and payment
class RetailSystem:
    
    def __init__(self):
        self.cart = CartFactory.create_cart()
        self.payment_processor = PaymentProcessor(CreditCardPayment())  # Default to Credit Card Payment
        self.inventory = Inventory()

    def add_item_to_inventory(self, item, quantity):
        # Adds items to the inventory
        self.inventory.add_item(item, quantity)

    def add_item_to_cart(self, item, quantity):
        # Adds items to the cart if sufficient stock is available
        if self.inventory.stock.get(item, 0) >= quantity:
            self.cart.add_item(item, quantity)
            self.inventory.stock[item] -= quantity
        else:
            print(f"Not enough stock for {item}.")

    def checkout(self, amount):
        # Processes the payment for the cart's total amount
        self.payment_processor.process_payment(amount)

# Testing the Monolithic Retail System

# Create the retail system
retail_system = RetailSystem()

# Add items to inventory
retail_system.add_item_to_inventory("Laptop", 5)
retail_system.add_item_to_inventory("Phone", 10)

# Add items to the cart
retail_system.add_item_to_cart("Laptop", 2)
retail_system.add_item_to_cart("Phone", 1)

# Perform checkout with a total amount
retail_system.checkout(1500)
