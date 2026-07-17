#region Imports

import threading
import unittest
import hashlib
import hmac
import os
import sys

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

#endregion

#region BankAccount

# ==========================
# Creating a BankAccount class
# ==========================
class BankAccount:
    def __init__(self, account_number, owner, balance=0):
        self.account_number = account_number
        self.owner = owner
        self.balance = balance
        self.lock = threading.Lock()

    # ==========================
    # Methods specified in the original assignment brief
    # ==========================

    def deposit(self, amount):
        with self.lock:
            self.balance += amount

    def withdraw(self, amount):
        with self.lock:
            if self.balance >= amount:
                self.balance -= amount
                return True

            return False

    def get_balance(self):
        with self.lock:
            return self.balance

#endregion

#region Transaction Records

# ==========================
# Creating a TransactionRecord class
# ==========================
@dataclass
class TransactionRecord:
    transaction_type: str
    from_account: str
    to_account: str
    amount: int
    success: bool
    message: str
    timestamp: datetime

#endregion

#region Repositories

# ==========================
# Creating repositories to hold users, accounts and transactions
# ==========================
class UserRepository:
    def __init__(self):
        self.users = {}

    def add_user(self, user):
        self.users[user.username] = user

    def get_user(self, username):
        return self.users.get(username)


class AccountRepository:
    def __init__(self):
        self.accounts = {}

    def add_account(self, account):
        self.accounts[account.account_number] = account

    def get_account(self, account_number):
        return self.accounts.get(account_number)

    def get_all_accounts(self):
        return list(self.accounts.values())


class TransactionRepository:
    def __init__(self):
        self.transactions = []

    def add_transaction(self, transaction_record):
        self.transactions.append(transaction_record)

    def get_all_transactions(self):
        return self.transactions

#endregion

#region User Security

# ==========================
# Creating a User class
# ==========================
@dataclass
class User:
    username: str
    password_hash: bytes
    salt: bytes
    role: str


# ==========================
# Creating loggers for authentication attempts
# ==========================
class SecurityLogger:
    def log_successful_login(self, username):
        print(f"SECURITY LOG: successful login for {username}")

    def log_failed_login(self, username):
        print(f"SECURITY LOG: failed login attempt for {username}")


class MockSecurityLogger:
    def __init__(self):
        self.successful_logins = []
        self.failed_logins = []

    def log_successful_login(self, username):
        self.successful_logins.append(username)

    def log_failed_login(self, username):
        self.failed_logins.append(username)


# ==========================
# Creating an AuthenticationService
# ==========================
class AuthenticationService:
    def __init__(self, user_repository, security_logger):
        self.user_repository = user_repository
        self.security_logger = security_logger

    def hash_password(self, password, salt):
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            100000
        )

    def validate_username(self, username):
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")

    def validate_password(self, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        if password.lower() in ["password", "admin123", "letmein"]:
            raise ValueError("Password is too weak")

    def register_user(self, username, password, role="customer"):
        self.validate_username(username)
        self.validate_password(password)

        salt = os.urandom(16)
        password_hash = self.hash_password(password, salt)

        user = User(
            username=username,
            password_hash=password_hash,
            salt=salt,
            role=role
        )

        self.user_repository.add_user(user)

        return user

    def authenticate(self, username, password):
        user = self.user_repository.get_user(username)

        if not user:
            self.security_logger.log_failed_login(username)
            return False

        attempted_hash = self.hash_password(password, user.salt)

        if hmac.compare_digest(attempted_hash, user.password_hash):
            self.security_logger.log_successful_login(username)
            return True

        self.security_logger.log_failed_login(username)
        return False

#endregion

#region Transaction Manager

# ==========================
# Creating a TransactionManager to handle transfers safely
# - lock in order of account number (lowest first) to prevent circular transactions / deadlock
# - records each transaction 
# ==========================

class TransactionManager:
    def __init__(self, transaction_repository):
        self.transaction_repository = transaction_repository

    def record_transaction(
        self,
        transaction_type,
        from_account,
        to_account,
        amount,
        success,
        message
    ):
        transaction_record = TransactionRecord(
            transaction_type=transaction_type,
            from_account=from_account,
            to_account=to_account,
            amount=amount,
            success=success,
            message=message,
            timestamp=datetime.now()
        )

        self.transaction_repository.add_transaction(transaction_record)

        return transaction_record

    def deposit(self, account, amount):
        account.deposit(amount)

        self.record_transaction(
            transaction_type="deposit",
            from_account="external",
            to_account=account.account_number,
            amount=amount,
            success=True,
            message="Deposit completed"
        )

        return True

    def withdraw(self, account, amount):
        result = account.withdraw(amount)

        if result:
            message = "Withdrawal completed"
        else:
            message = "Withdrawal denied - balance lower than withdrawal amount"

        self.record_transaction(
            transaction_type="withdrawal",
            from_account=account.account_number,
            to_account="external",
            amount=amount,
            success=result,
            message=message
        )

        return result

    def transfer(self, from_account, to_account, amount):

        if from_account.account_number < to_account.account_number:
            first_account = from_account
            second_account = to_account
        else:
            first_account = to_account
            second_account = from_account

        with first_account.lock:
            with second_account.lock:

                if from_account.balance >= amount:
                    from_account.balance -= amount
                    to_account.balance += amount

                    self.record_transaction(
                        transaction_type="transfer",
                        from_account=from_account.account_number,
                        to_account=to_account.account_number,
                        amount=amount,
                        success=True,
                        message="Transfer completed"
                    )

                    return True

                self.record_transaction(
                    transaction_type="transfer",
                    from_account=from_account.account_number,
                    to_account=to_account.account_number,
                    amount=amount,
                    success=False,
                    message="Transfer denied - balance lower than transfer amount"
                )

                return False

#endregion

#region Transaction Monitoring

# ==========================
# Creating transaction monitoring rules
# ==========================
class RiskRule:
    def check(self, transaction_record):
        pass


class LargeTransactionRule(RiskRule):
    def __init__(self, limit):
        self.limit = limit

    def check(self, transaction_record):
        if transaction_record.amount >= self.limit:
            return f"Large transaction detected: £{transaction_record.amount}"

        return None


class FailedTransactionRule(RiskRule):
    def check(self, transaction_record):
        if not transaction_record.success:
            return "Failed transaction detected"

        return None


# ==========================
# Creating a TransactionMonitoringService
# ==========================
class TransactionMonitoringService:
    def __init__(self, risk_rules):
        self.risk_rules = risk_rules

    def analyse_transaction(self, transaction_record):
        alerts = []

        for rule in self.risk_rules:
            result = rule.check(transaction_record)

            if result:
                alerts.append(result)

        return alerts

#endregion

#region Transaction Actions

# ==========================
# Creating transaction actions
# ==========================
class TransactionAction:
    def execute(self):
        pass


class DepositAction(TransactionAction):
    def __init__(self, transaction_manager, account, amount):
        self.transaction_manager = transaction_manager
        self.account = account
        self.amount = amount

    def execute(self):
        return self.transaction_manager.deposit(self.account, self.amount)


# ==========================
# Adding audit behaviour without changing the original action
# ==========================
class AuditDecorator(TransactionAction):
    def __init__(self, transaction_action):
        self.transaction_action = transaction_action

    def execute(self):
        print("AUDIT: transaction action starting")
        result = self.transaction_action.execute()
        print("AUDIT: transaction action complete")

        return result

#endregion

#region Transaction Reporting

# ==========================
# Creating a transaction report visitor
# ==========================
class TransactionReportVisitor:
    def __init__(self):
        self.total_successful = 0
        self.total_failed = 0

    def visit(self, transaction_record):
        if transaction_record.success:
            self.total_successful += 1
        else:
            self.total_failed += 1

    def report(self):
        return {
            "successful_transactions": self.total_successful,
            "failed_transactions": self.total_failed
        }

#endregion

#region Monitoring Factory

# ==========================
# Creating monitoring factories
# ==========================
class StandardMonitoringFactory:
    def create_monitoring_service(self):
        risk_rules = [
            LargeTransactionRule(500),
            FailedTransactionRule()
        ]

        return TransactionMonitoringService(risk_rules)


class StrictMonitoringFactory:
    def create_monitoring_service(self):
        risk_rules = [
            LargeTransactionRule(100),
            FailedTransactionRule()
        ]

        return TransactionMonitoringService(risk_rules)

#endregion

#region Application Setup

# ==========================
# Creating the main banking application
# ==========================
class BankingApplication:
    def __init__(
        self,
        user_repository,
        account_repository,
        transaction_repository,
        authentication_service,
        transaction_manager,
        monitoring_service
    ):
        self.user_repository = user_repository
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
        self.authentication_service = authentication_service
        self.transaction_manager = transaction_manager
        self.monitoring_service = monitoring_service

    def create_account(self, account_number, owner, balance=0):
        account = BankAccount(account_number, owner, balance)
        self.account_repository.add_account(account)

        return account

    def analyse_latest_transaction(self):
        transactions = self.transaction_repository.get_all_transactions()

        if not transactions:
            return []

        latest_transaction = transactions[-1]

        return self.monitoring_service.analyse_transaction(latest_transaction)

#endregion

#region Simulation

# ==========================
# Creating a user for the simulator
# ==========================
class UserforSimulator:
    def __init__(self, user_id, account, number_of_transactions, transaction_manager):
        self.user_id = user_id
        self.account = account
        self.number_of_transactions = number_of_transactions
        self.transaction_manager = transaction_manager

    def perform_transactions(self):
        for transactions in range(self.number_of_transactions):
            self.transaction_manager.deposit(self.account, 10)
            self.transaction_manager.withdraw(self.account, 5)


# ==========================
# Create a Transaction Simulator to validate the thread safety
# ==========================
class TransactionSimulator:
    def __init__(self, account, transaction_manager):
        self.account = account
        self.transaction_manager = transaction_manager
        self.users = []
        self.threads = []

    def create_users(self, number_of_users, transactions_per_user):
        self.users = []

        for user_number in range(number_of_users):
            user = UserforSimulator(
                user_id=user_number + 1,
                account=self.account,
                number_of_transactions=transactions_per_user,
                transaction_manager=self.transaction_manager
            )
            self.users.append(user)

    def run(self, number_of_users=5, transactions_per_user=10):
        self.create_users(number_of_users, transactions_per_user)

        self.threads = []

        for user in self.users:
            thread = threading.Thread(target=user.perform_transactions)
            self.threads.append(thread)
            thread.start()

        for thread in self.threads:
            thread.join()


# ==========================
# Test TransactionManager using DeadlockTestSimulator
# - create accounts, run transfers, compare the total balance
# ==========================
class DeadlockTestSimulator:
    def __init__(self, transaction_manager, starting_balance=1000, transfer_amount=10):
        self.starting_balance = starting_balance
        self.transfer_amount = transfer_amount
        self.accounts = []
        self.manager = transaction_manager

    def create_accounts(self, number_of_accounts):
        self.accounts = []

        for account_number in range(number_of_accounts):
            account = BankAccount(
                account_number=str(10000001 + account_number),
                owner="test_user",
                balance=self.starting_balance
            )
            self.accounts.append(account)

    def get_total_balance(self):
        total = 0

        for account in self.accounts:
            total += account.get_balance()

        return total

    def run(self, number_of_accounts=3, number_of_loops=1, verbose=False):
        self.create_accounts(number_of_accounts)

        starting_total = self.get_total_balance()

        for loop in range(number_of_loops):

            if verbose:
                print(f"\nLoop {loop + 1} starting:")

            threads = []

            for from_account in self.accounts:
                for to_account in self.accounts:
                    if from_account != to_account:

                        thread = threading.Thread(
                            target=self.manager.transfer,
                            args=(from_account, to_account, self.transfer_amount)
                        )

                        threads.append(thread)
                        thread.start()

            for thread in threads:
                thread.join()

            current_total = self.get_total_balance()

            if verbose:
                print(f"\nLoop {loop + 1} complete")
                print("Balances:")

                for account in self.accounts:
                    print(
                        f"Account {account.account_number}: "
                        f"£{account.get_balance()}"
                    )

                print(f"Total balance: £{current_total}")

                if current_total == starting_total:
                    print("PASS - Total balance unchanged\n")

            if current_total != starting_total:
                print("FAIL - Total balance changed")
                return False

        if verbose:
            print("Deadlock prevention successful")

        return True

#endregion

#region Unit Tests

# ==========================
# Unit tests
# ==========================
class TestCapstoneProject(unittest.TestCase):

    def setUp(self):
        self.user_repository = UserRepository()
        self.account_repository = AccountRepository()
        self.transaction_repository = TransactionRepository()

        self.mock_security_logger = MockSecurityLogger()

        self.authentication_service = AuthenticationService(
            user_repository=self.user_repository,
            security_logger=self.mock_security_logger
        )

        self.transaction_manager = TransactionManager(
            transaction_repository=self.transaction_repository
        )

        monitoring_factory = StandardMonitoringFactory()
        self.monitoring_service = monitoring_factory.create_monitoring_service()

        self.application = BankingApplication(
            user_repository=self.user_repository,
            account_repository=self.account_repository,
            transaction_repository=self.transaction_repository,
            authentication_service=self.authentication_service,
            transaction_manager=self.transaction_manager,
            monitoring_service=self.monitoring_service
        )

    def test_01_user_registration(self):
        user = self.authentication_service.register_user(
            "testuser1",
            "SecurePass123",
            "customer"
        )

        self.assertEqual(user.username, "testuser1")
        self.assertNotEqual(user.password_hash, "SecurePass123")

    def test_02_successful_login_is_logged(self):
        self.authentication_service.register_user(
            "testuser1",
            "SecurePass123",
            "customer"
        )

        result = self.authentication_service.authenticate(
            "testuser1",
            "SecurePass123"
        )

        self.assertTrue(result)
        self.assertEqual(self.mock_security_logger.successful_logins, ["testuser1"])

    def test_03_failed_login_is_logged(self):
        self.authentication_service.register_user(
            "testuser1",
            "SecurePass123",
            "customer"
        )

        result = self.authentication_service.authenticate(
            "testuser1",
            "WrongPassword"
        )

        self.assertFalse(result)
        self.assertEqual(self.mock_security_logger.failed_logins, ["testuser1"])

    def test_04_deposit(self):
        account = self.application.create_account("10000001", "testuser1", 0)

        self.transaction_manager.deposit(account, 100)

        self.assertEqual(account.get_balance(), 100)

    def test_05_withdraw(self):
        account = self.application.create_account("10000001", "testuser1", 100)

        result = self.transaction_manager.withdraw(account, 40)

        self.assertTrue(result)
        self.assertEqual(account.get_balance(), 60)

    def test_06_overdraft_withdrawal(self):
        account = self.application.create_account("10000001", "testuser1", 100)

        result = self.transaction_manager.withdraw(account, 200)

        self.assertFalse(result)
        self.assertEqual(account.get_balance(), 100)

    def test_07_transfer_preserves_total_balance(self):
        account_a = self.application.create_account("10000001", "testuser1", 1000)
        account_b = self.application.create_account("10000002", "jane", 1000)

        starting_total = account_a.get_balance() + account_b.get_balance()

        self.transaction_manager.transfer(account_a, account_b, 100)

        ending_total = account_a.get_balance() + account_b.get_balance()

        self.assertEqual(starting_total, ending_total)

    def test_08_transaction_record_created(self):
        account = self.application.create_account("10000001", "testuser1", 0)

        self.transaction_manager.deposit(account, 100)

        transactions = self.transaction_repository.get_all_transactions()

        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].transaction_type, "deposit")

    def test_09_large_transaction_generates_alert(self):
        account = self.application.create_account("10000001", "testuser1", 0)

        self.transaction_manager.deposit(account, 600)

        alerts = self.application.analyse_latest_transaction()

        self.assertEqual(alerts, ["Large transaction detected: £600"])

    def test_10_failed_transaction_generates_alert(self):
        account = self.application.create_account("10000001", "testuser1", 100)

        self.transaction_manager.withdraw(account, 200)

        alerts = self.application.analyse_latest_transaction()

        self.assertEqual(alerts, ["Failed transaction detected"])

    def test_11_decorator_executes_transaction_action(self):
        account = self.application.create_account("10000001", "testuser1", 0)

        deposit_action = DepositAction(
            self.transaction_manager,
            account,
            100
        )

        audited_action = AuditDecorator(deposit_action)

        audited_action.execute()

        self.assertEqual(account.get_balance(), 100)

    def test_12_visitor_reports_transactions(self):
        account = self.application.create_account("10000001", "testuser1", 100)

        self.transaction_manager.deposit(account, 100)
        self.transaction_manager.withdraw(account, 500)

        visitor = TransactionReportVisitor()

        for transaction in self.transaction_repository.get_all_transactions():
            visitor.visit(transaction)

        report = visitor.report()

        self.assertEqual(report["successful_transactions"], 1)
        self.assertEqual(report["failed_transactions"], 1)

    def test_13_transaction_simulator(self):
        account = self.application.create_account("10000001", "testuser1", 0)

        simulator = TransactionSimulator(
            account=account,
            transaction_manager=self.transaction_manager
        )

        simulator.run(5, 10)

        self.assertEqual(account.get_balance(), 250)

    def test_14_deadlock_test_simulator(self):
        deadlock_test = DeadlockTestSimulator(
            transaction_manager=self.transaction_manager
        )

        result = deadlock_test.run(3, 1)

        total = deadlock_test.get_total_balance()

        self.assertTrue(result)
        self.assertEqual(total, 3000)

#endregion

#region Main

# ==========================
# Creating the application setup
# ==========================
def create_application(monitoring_type="standard"):
    user_repository = UserRepository()
    account_repository = AccountRepository()
    transaction_repository = TransactionRepository()

    security_logger = SecurityLogger()

    authentication_service = AuthenticationService(
        user_repository=user_repository,
        security_logger=security_logger
    )

    transaction_manager = TransactionManager(
        transaction_repository=transaction_repository
    )

    if monitoring_type == "strict":
        monitoring_factory = StrictMonitoringFactory()
    else:
        monitoring_factory = StandardMonitoringFactory()

    monitoring_service = monitoring_factory.create_monitoring_service()

    application = BankingApplication(
        user_repository=user_repository,
        account_repository=account_repository,
        transaction_repository=transaction_repository,
        authentication_service=authentication_service,
        transaction_manager=transaction_manager,
        monitoring_service=monitoring_service
    )

    return application


# ==========================
# Demonstration
# ==========================
def run_demo():
    application = create_application()

    application.authentication_service.register_user(
        "testuser1",
        "SecurePass123",
        "customer"
    )

    authenticated = application.authentication_service.authenticate(
        "testuser1",
        "SecurePass123"
    )

    if authenticated:
        account_a = application.create_account("10000001", "testuser1", 1000)
        account_b = application.create_account("10000002", "testuser2", 500)

        application.transaction_manager.deposit(account_a, 600)
        application.transaction_manager.transfer(account_a, account_b, 200)
        application.transaction_manager.withdraw(account_b, 1000)

        print("\nTransactions created:")

        for transaction in application.transaction_repository.get_all_transactions():
            print(
                f"{transaction.transaction_type}: "
                f"{transaction.from_account} -> "
                f"{transaction.to_account} "
                f"£{transaction.amount} "
                f"Success: {transaction.success} "
                f"Message: {transaction.message}"
            )

        alerts = application.analyse_latest_transaction()

        print("\nLatest transaction alerts:")
        print(alerts)

        visitor = TransactionReportVisitor()

        for transaction in application.transaction_repository.get_all_transactions():
            visitor.visit(transaction)

        print("\nTransaction report:")
        print(visitor.report())


# ==========================
# Run TransactionSimulator with custom values
# ==========================
def run_transaction_simulator(users, transactions):
    application = create_application()

    account = application.create_account("10000001", "testuser1", 0)

    simulator = TransactionSimulator(
        account=account,
        transaction_manager=application.transaction_manager
    )

    simulator.run(users, transactions)

    expected_balance = users * transactions * 5
    actual_balance = account.get_balance()

    print("\nTransactionSimulator")
    print(f"Users: {users}")
    print(f"Transactions per user: {transactions}")
    print(f"Expected balance: £{expected_balance}")
    print(f"Actual balance: £{actual_balance}")

    if actual_balance == expected_balance:
        print("PASS - Final balance matched expected value")
    else:
        print("FAIL - Final balance did not match expected value")


# ==========================
# Run DeadlockTestSimulator with custom values
# ==========================
def run_deadlock_test(accounts, loops):
    application = create_application()

    deadlock_test = DeadlockTestSimulator(
        transaction_manager=application.transaction_manager
    )

    result = deadlock_test.run(accounts, loops)

    expected_total = accounts * 1000
    actual_total = deadlock_test.get_total_balance()

    print("\nDeadlockTestSimulator")
    print(f"Accounts: {accounts}")
    print(f"Loops: {loops}")
    print(f"Expected total balance: £{expected_total}")
    print(f"Actual total balance: £{actual_total}")

    if result and actual_total == expected_total:
        print("PASS - Total balance unchanged and no deadlock occurred")
    else:
        print("FAIL - Total balance changed or deadlock test failed")


# ==========================
# Run OverdraftTransferTest with custom values
# ==========================
def run_overdraft_transfer_test(accounts, loops, starting_balance, transfer_amount):
    application = create_application()

    overdraft_test = DeadlockTestSimulator(
        transaction_manager=application.transaction_manager,
        starting_balance=starting_balance,
        transfer_amount=transfer_amount
    )

    result = overdraft_test.run(accounts, loops, verbose=True)

    expected_total = accounts * starting_balance
    actual_total = overdraft_test.get_total_balance()

    print("\nOverdraftTransferTest")
    print(f"Accounts: {accounts}")
    print(f"Loops: {loops}")
    print(f"Starting balance per account: £{starting_balance}")
    print(f"Transfer amount: £{transfer_amount}")
    print(f"Expected total balance: £{expected_total}")
    print(f"Actual total balance: £{actual_total}")

    if result and actual_total == expected_total:
        print("PASS - Failed transfers were handled and total balance was protected")
    else:
        print("FAIL - Total balance changed")


# ==========================
# Run AuthenticationTest
# ==========================
def run_authentication_test():
    user_repository = UserRepository()
    mock_security_logger = MockSecurityLogger()

    authentication_service = AuthenticationService(
        user_repository=user_repository,
        security_logger=mock_security_logger
    )

    authentication_service.register_user(
        "testuser1",
        "SecurePass123",
        "customer"
    )

    successful_login = authentication_service.authenticate(
        "testuser1",
        "SecurePass123"
    )

    failed_login = authentication_service.authenticate(
        "testuser1",
        "WrongPassword"
    )

    print("\nAuthenticationTest")
    print(f"Successful login returned: {successful_login}")
    print(f"Failed login returned: {failed_login}")
    print(f"Successful login records: {mock_security_logger.successful_logins}")
    print(f"Failed login records: {mock_security_logger.failed_logins}")

    if successful_login and not failed_login:
        print("PASS - Authentication and failed login logging worked")
    else:
        print("FAIL - Authentication test failed")


# ==========================
# Run MonitoringTest
# ==========================
def run_monitoring_test(amount, monitoring_type):
    application = create_application(monitoring_type)

    account = application.create_account("10000001", "testuser1", 0)

    application.transaction_manager.deposit(account, amount)

    alerts = application.analyse_latest_transaction()

    print("\nMonitoringTest")
    print(f"Monitoring type: {monitoring_type}")
    print(f"Deposit amount: £{amount}")
    print(f"Alerts: {alerts}")

    if alerts:
        print("PASS - Monitoring rule generated an alert")
    else:
        print("PASS - No monitoring alert was generated")


# ==========================
# Run unit tests
# ==========================
def run_unit_tests():
    result = unittest.main(
        argv=[sys.argv[0]],
        exit=False
    )

    if result.result.wasSuccessful():
        print("\nAll tests completed successfully\n")


if __name__ == "__main__":

    if len(sys.argv) > 1:

        mode = sys.argv[1]

        if mode == "Demo":
            run_demo()

        elif mode == "TransactionSimulator":
            users = int(sys.argv[2])
            transactions = int(sys.argv[3])

            run_transaction_simulator(users, transactions)

        elif mode == "DeadlockTestSimulator":
            accounts = int(sys.argv[2])
            loops = int(sys.argv[3])

            run_deadlock_test(accounts, loops)

        elif mode == "OverdraftTransferTest":
            accounts = int(sys.argv[2])
            loops = int(sys.argv[3])
            starting_balance = int(sys.argv[4])
            transfer_amount = int(sys.argv[5])

            run_overdraft_transfer_test(
                accounts,
                loops,
                starting_balance,
                transfer_amount
            )

        elif mode == "AuthenticationTest":
            run_authentication_test()

        elif mode == "MonitoringTest":
            amount = int(sys.argv[2])
            monitoring_type = sys.argv[3]

            run_monitoring_test(amount, monitoring_type)

        elif mode == "UnitTests":
            run_unit_tests()

        else:
            print("Unknown mode selected")

    else:
        run_unit_tests()

#endregion