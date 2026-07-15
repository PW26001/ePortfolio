"""
Unit 9 - Object-Oriented Software Architecture

A simplified e-commerce system for ShopEase.

The system demonstrates:

- Layered architecture
- User management
- Product catalogue
- Order processing
- Password hashing and authentication
- Dependency injection
- Strategy Pattern for payment methods
- Observer Pattern for notifications
- Replaceable data-access classes
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import hashlib
import hmac
import os


# ============================================================
# DOMAIN OBJECTS
# ============================================================

@dataclass
class Product:
    product_id: int
    name: str
    price: float
    stock: int


@dataclass
class OrderItem:
    product: Product
    quantity: int

    def calculate_price(self):
        return self.product.price * self.quantity


@dataclass
class Order:
    order_id: int
    username: str
    items: list
    total: float
    payment_method: str
    status: str = "Created"


class User:
    def __init__(self, username, password):
        self.username = username
        self.__salt = os.urandom(16)
        self.__password_hash = self.__hash_password(password)

    def __hash_password(self, password):
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            self.__salt,
            310000
        )

    def verify_password(self, password):
        supplied_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            self.__salt,
            310000
        )

        return hmac.compare_digest(
            self.__password_hash,
            supplied_hash
        )


# ============================================================
# DATA ACCESS LAYER
# ============================================================

class UserRepository(ABC):

    @abstractmethod
    def add_user(self, user):
        pass

    @abstractmethod
    def get_user(self, username):
        pass


class ProductRepository(ABC):

    @abstractmethod
    def add_product(self, product):
        pass

    @abstractmethod
    def get_product(self, product_id):
        pass

    @abstractmethod
    def get_all_products(self):
        pass


class OrderRepository(ABC):

    @abstractmethod
    def add_order(self, order):
        pass

    @abstractmethod
    def get_orders(self):
        pass


class InMemoryUserRepository(UserRepository):

    def __init__(self):
        self.users = {}

    def add_user(self, user):
        self.users[user.username] = user

    def get_user(self, username):
        return self.users.get(username)


class InMemoryProductRepository(ProductRepository):

    def __init__(self):
        self.products = {}

    def add_product(self, product):
        self.products[product.product_id] = product

    def get_product(self, product_id):
        return self.products.get(product_id)

    def get_all_products(self):
        return list(self.products.values())


class InMemoryOrderRepository(OrderRepository):

    def __init__(self):
        self.orders = []

    def add_order(self, order):
        self.orders.append(order)

    def get_orders(self):
        return self.orders.copy()


# ============================================================
# PAYMENT STRATEGIES
# ============================================================

class PaymentStrategy(ABC):

    @abstractmethod
    def pay(self, amount):
        pass


class CardPayment(PaymentStrategy):

    def pay(self, amount):
        return f"Card payment of £{amount:.2f} completed"


class PayPalPayment(PaymentStrategy):

    def pay(self, amount):
        return f"PayPal payment of £{amount:.2f} completed"


class BankTransferPayment(PaymentStrategy):

    def pay(self, amount):
        return f"Bank transfer of £{amount:.2f} completed"


# ============================================================
# OBSERVER PATTERN
# ============================================================

class OrderObserver(ABC):

    @abstractmethod
    def update(self, order):
        pass


class EmailNotification(OrderObserver):

    def update(self, order):
        print(
            f"Email notification: Order {order.order_id} "
            f"for {order.username} is now {order.status}"
        )


class AuditLogger(OrderObserver):

    def update(self, order):
        print(
            f"Audit log: Order {order.order_id}, "
            f"user={order.username}, status={order.status}"
        )


# ============================================================
# BUSINESS LOGIC LAYER
# ============================================================

class AuthenticationService:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def register_user(self, username, password):
        if not username or not password:
            raise ValueError("Username and password are required")

        if self.user_repository.get_user(username):
            raise ValueError("Username already exists")

        if len(password) < 8:
            raise ValueError(
                "Password must contain at least eight characters"
            )

        user = User(username, password)
        self.user_repository.add_user(user)

        return user

    def authenticate(self, username, password):
        user = self.user_repository.get_user(username)

        if not user:
            return False

        return user.verify_password(password)


class ProductService:

    def __init__(self, product_repository):
        self.product_repository = product_repository

    def add_product(self, product_id, name, price, stock):
        if price < 0:
            raise ValueError("Product price cannot be negative")

        if stock < 0:
            raise ValueError("Product stock cannot be negative")

        product = Product(
            product_id,
            name,
            price,
            stock
        )

        self.product_repository.add_product(product)

        return product

    def search_products(self, search_term):
        search_term = search_term.lower()

        return [
            product
            for product in self.product_repository.get_all_products()
            if search_term in product.name.lower()
        ]


class OrderService:

    def __init__(
        self,
        product_repository,
        order_repository,
        payment_strategy
    ):
        self.product_repository = product_repository
        self.order_repository = order_repository
        self.payment_strategy = payment_strategy
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, order):
        for observer in self.observers:
            observer.update(order)

    def create_order(self, order_id, username, requested_items):
        order_items = []

        for product_id, quantity in requested_items:
            product = self.product_repository.get_product(product_id)

            if not product:
                raise ValueError(
                    f"Product {product_id} does not exist"
                )

            if quantity <= 0:
                raise ValueError(
                    "Quantity must be greater than zero"
                )

            if product.stock < quantity:
                raise ValueError(
                    f"Insufficient stock for {product.name}"
                )

            order_items.append(
                OrderItem(product, quantity)
            )

        total = sum(
            item.calculate_price()
            for item in order_items
        )

        payment_result = self.payment_strategy.pay(total)
        print(payment_result)

        for item in order_items:
            item.product.stock -= item.quantity

        order = Order(
            order_id=order_id,
            username=username,
            items=order_items,
            total=total,
            payment_method=self.payment_strategy.__class__.__name__,
            status="Paid"
        )

        self.order_repository.add_order(order)
        self.notify_observers(order)

        return order


# ============================================================
# PRESENTATION LAYER
# ============================================================

class ShopEaseApplication:
    """
    A simple presentation layer which provides access to
    business services without changing the data-access layer.
    """

    def __init__(
        self,
        authentication_service,
        product_service,
        order_service
    ):
        self.authentication_service = authentication_service
        self.product_service = product_service
        self.order_service = order_service

    def register_user(self, username, password):
        return self.authentication_service.register_user(
            username,
            password
        )

    def authenticate_user(self, username, password):
        return self.authentication_service.authenticate(
            username,
            password
        )

    def add_product(self, product_id, name, price, stock):
        return self.product_service.add_product(
            product_id,
            name,
            price,
            stock
        )

    def search_products(self, search_term):
        return self.product_service.search_products(
            search_term
        )

    def create_order(self, order_id, username, requested_items):
        return self.order_service.create_order(
            order_id,
            username,
            requested_items
        )


# ============================================================
# DEPENDENCY CONFIGURATION
# ============================================================

def main():
    user_repository = InMemoryUserRepository()
    product_repository = InMemoryProductRepository()
    order_repository = InMemoryOrderRepository()

    authentication_service = AuthenticationService(
        user_repository
    )

    product_service = ProductService(
        product_repository
    )

    payment_strategy = CardPayment()

    order_service = OrderService(
        product_repository,
        order_repository,
        payment_strategy
    )

    order_service.add_observer(
        EmailNotification()
    )

    order_service.add_observer(
        AuditLogger()
    )

    application = ShopEaseApplication(
        authentication_service,
        product_service,
        order_service
    )

    application.register_user(
        "phil",
        "SecurePass123"
    )

    authenticated = application.authenticate_user(
        "phil",
        "SecurePass123"
    )

    print(f"Authentication successful: {authenticated}")

    application.add_product(
        1,
        "Python Book",
        24.99,
        10
    )

    application.add_product(
        2,
        "Laptop",
        799.99,
        4
    )

    application.add_product(
        3,
        "USB Cable",
        8.50,
        30
    )

    results = application.search_products("book")

    for product in results:
        print(
            f"{product.product_id}: "
            f"{product.name} - £{product.price:.2f}"
        )

    order = application.create_order(
        order_id=1001,
        username="phil",
        requested_items=[
            (1, 1),
            (3, 2)
        ]
    )

    print(
        f"Order {order.order_id} completed "
        f"with a total of £{order.total:.2f}"
    )


if __name__ == "__main__":
    main()