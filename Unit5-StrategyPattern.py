#%%
# ------------------------------------------------------------
# Unit 5 - Implementing the Strategy Pattern
# ------------------------------------------------------------

"""
Strategy - chooses from interchangeable methods to complete the action.

The original version works, but the payment logic is held inside one
if / elif block.

This means that every new payment method would require PaymentProcessor
to be edited, which makes the code harder to maintain and expand.

The Strategy Pattern separates each payment method into its own class.
PaymentProcessor is then passed the payment method to use, and does not
need to know the detail of how that payment is processed.
"""


# ------------------------------------------------------------
# Original Version
# ------------------------------------------------------------

class OriginalPaymentProcessor:
    def process_payment(self, payment_type, amount):
        if payment_type == "credit_card":
            print(f"Processing credit card payment of £{amount}")
        elif payment_type == "paypal":
            print(f"Processing PayPal payment of £{amount}")
        elif payment_type == "bank_transfer":
            print(f"Processing bank transfer of £{amount}")
        else:
            raise ValueError("Invalid payment type")


original_processor = OriginalPaymentProcessor()
original_processor.process_payment("credit_card", 100)
original_processor.process_payment("paypal", 75)
original_processor.process_payment("bank_transfer", 50)


# ------------------------------------------------------------
# Refactored Version - Strategy Pattern
# ------------------------------------------------------------

class CreditCardPayment:
    def pay(self, amount):
        print(f"Processing credit card payment of £{amount}")


class PayPalPayment:
    def pay(self, amount):
        print(f"Processing PayPal payment of £{amount}")


class BankTransferPayment:
    def pay(self, amount):
        print(f"Processing bank transfer of £{amount}")


class CryptoPayment:
    def pay(self, amount):
        print(f"Processing crypto payment of £{amount}")


class PaymentProcessor:
    def __init__(self, payment_strategy):
        self.payment_strategy = payment_strategy

    def process_payment(self, amount):
        self.payment_strategy.pay(amount)


# ------------------------------------------------------------
# Demonstration
# ------------------------------------------------------------

payments = [
    CreditCardPayment(),
    PayPalPayment(),
    BankTransferPayment(),
    CryptoPayment()
]

for payment in payments:
    processor = PaymentProcessor(payment)
    processor.process_payment(100)

# %%