# ------------------------------------------------------------
# Unit 2 Case Study
# Designing Real World Application with SOLID Principles
# ------------------------------------------------------------


# ------------------------------------------------------------
# Provided Version
# ------------------------------------------------------------


def __init__(self):

    self.items = []


def add_item(self, item):

    self.items.append(item)


def calculate_total(self):

    return sum(item.price for item in self.items)


def pay(self, payment_type):

    if payment_type == "credit":

        print("Processing credit card payment...")

    elif payment_type == "paypal":

        print("Processing PayPal payment...") #Adding a new method requires modifying this class.


# ------------------------------------------------------------
# Updated Version - Applying SOLID Principles
# ------------------------------------------------------------

"""
This version separates responsibilities.

Separating Order into Order & PaymentProcessor
Order manages items and calculates the total.
PaymentProcessor uses a shared pay method which can be used by the newly introduced payment methods,
CreditCardPayment, PayPalPayment and CryptoPayment.

This means new payment methods can be added without rewriting Order.

SOLID is applied by:
SRP - Order manages the order, PaymentProcessor handles payment.
OCP - New payment types can be added without rewriting Order.
LSP - Each payment method can be used where a payment method is expected.
ISP - The payment classes only need to provide pay(), so they are not forced to include methods they do not need.
DIP - Order depends on a payment method being passed in, rather than hardcoding specific payment types.
"""


class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price


class Order:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def calculate_total(self):
        return sum(item.price for item in self.items)

    def pay(self, payment_processor, payment_method):
        payment_processor.process_payment(self.calculate_total(), payment_method)


class PaymentProcessor:
    def process_payment(self, amount, payment_method):
        payment_method.pay(amount)


class CreditCardPayment:
    def pay(self, amount):
        print(f"Processing credit card payment of £{amount}")


class PayPalPayment:
    def pay(self, amount):
        print(f"Processing PayPal payment of £{amount}")


class CryptoPayment:
    def pay(self, amount):
        print(f"Processing crypto payment of £{amount}")


order = Order()

order.add_item(Product("Keyboard", 50))
order.add_item(Product("Mouse", 25))

payment_processor = PaymentProcessor()

print(f"Order total: £{order.calculate_total()}")

order.pay(payment_processor, CreditCardPayment())
order.pay(payment_processor, PayPalPayment())
order.pay(payment_processor, CryptoPayment())