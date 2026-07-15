import threading

# ==========================
# Creating a BankAccount class
# ==========================
class BankAccount:
    def __init__(self, account_number, balance=0):
        self.account_number = account_number
        self.balance = balance
        self.lock = threading.Lock()

    # ==========================
    # Methods specified in the assignment brief
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

# ==========================
# First test Block for sanity checking
# ==========================
"""
account = BankAccount("10000001")

account.deposit(100)
account.withdraw(25)
account.deposit(50)
account.withdraw(100)

print(f"Account {account.account_number}:  £{account.get_balance()}")
"""
# ==========================
# Creating a user for the simulator
# ==========================
class UserforSimulator:
    def __init__(self, user_id, account, number_of_transactions):
        self.user_id = user_id
        self.account = account
        self.number_of_transactions = number_of_transactions

    def perform_transactions(self):
        for transactions in range(self.number_of_transactions):
            self.account.deposit(10)
            self.account.withdraw(5)

# ==========================            
# Create a Transaction Simulator to validate the thread safety 
#       - allow number of users and transactions to be varied during testing
# ==========================            

class TransactionSimulator:
    def __init__(self, account):
        self.account = account
        self.users = []
        self.threads = []

    def create_users(self, number_of_users, transactions_per_user):
        self.users = []

        for user_number in range(number_of_users):
            user = UserforSimulator(
                user_id=user_number + 1,
                account=self.account,
                number_of_transactions=transactions_per_user
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

sim_account = BankAccount("10000002")

simulator = TransactionSimulator(account=sim_account)
# ==========================
# Second test Block for sanity checking
# ==========================
"""
simulator.run()
print(f"Account {sim_account.account_number}:  £{sim_account.get_balance()}")

simulator.run(50, 100)
print(f"Account {sim_account.account_number}:  £{sim_account.get_balance()}")
"""

# ==========================
# Creating a TransactionManager to handle transfers safely
# - lock in order of account number (lowest first) to prevent circular transactions / deadlock
# ==========================
class TransactionManager:
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
                    return True

                print(
                    f"Transfer denied: "
                    f"{from_account.account_number} -> "
                    f"{to_account.account_number} "
                    f"(£{amount}) "
                    f"- balance lower than withdrawal amount"
                )

                return False

# ==========================
# Test Transaction Manager using DeaadlockTestSimulator to run multiple transactions between accounts
# - include a loop to allow for stress testing. 
# - create a number of accounts, give each account £1000, get total balance, multiple transfers between each, compare total balance
# ==========================
class DeadlockTestSimulator:
    def __init__(self, starting_balance=1000, transfer_amount=10):
        self.starting_balance = starting_balance
        self.transfer_amount = transfer_amount
        self.accounts = []
        self.manager = TransactionManager()

    def create_accounts(self, number_of_accounts):
        self.accounts = []

        for account_number in range(number_of_accounts):
            account = BankAccount(
                account_number=str(10000001 + account_number),
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
                return

        if verbose:
            print("Deadlock prevention successful")

# ==========================
# Third test Block for sanity checking
# ==========================
"""
deadlock_test = DeadlockTestSimulator()

deadlock_test.run()
"""

# ==========================
# Unit tests
# ==========================

import unittest
import sys

class TestBankingSystem(unittest.TestCase):

    def test_01_account_created(self):
        account = BankAccount("10000001")

        self.assertEqual(account.account_number, "10000001")
        self.assertEqual(account.get_balance(), 0)

        print("account creation tested successfully")

    def test_02_deposit(self):
        account = BankAccount("10000001")

        account.deposit(100)

        self.assertEqual(account.get_balance(), 100)

        print("\ndeposit tested successfully")

    def test_03_withdraw(self):
        account = BankAccount("10000001", 100)

        account.withdraw(40)

        self.assertEqual(account.get_balance(), 60)

        print("\nwithdrawal tested successfully")

    def test_04_get_balance(self):
        account = BankAccount("10000001", 500)

        self.assertEqual(account.get_balance(), 500)

        print("\nget_balance tested successfully")

    def test_05_overdraft_withdrawal(self):
        account = BankAccount("10000001", 100)

        result = account.withdraw(200)

        self.assertFalse(result)
        self.assertEqual(account.get_balance(), 100)

        print("\noverdraft withdrawal tested successfully")

    def test_06_transaction_simulator(self):
        account = BankAccount("10000001")

        simulator = TransactionSimulator(account)

        simulator.run(5, 10)

        self.assertEqual(account.get_balance(), 250)

        print("\ntransaction simulator tested successfully")

    def test_07_transaction_manager(self):
        account_a = BankAccount("10000001", 1000)
        account_b = BankAccount("10000002", 1000)

        manager = TransactionManager()

        starting_total = (
            account_a.get_balance()
            + account_b.get_balance()
        )

        manager.transfer(account_a, account_b, 100)

        ending_total = (
            account_a.get_balance()
            + account_b.get_balance()
        )

        self.assertEqual(starting_total, ending_total)

        print("\ntransaction manager tested successfully")

    def test_08_deadlock_test_simulator(self):
        deadlock_test = DeadlockTestSimulator()

        deadlock_test.run(3, 1)

        total = deadlock_test.get_total_balance()

        self.assertEqual(total, 3000)

        print("\ndeadlock test simulator tested successfully")


if __name__ == "__main__":

    if len(sys.argv) > 1:

        mode = sys.argv[1]

        if mode == "TransactionSimulator":
            users = int(sys.argv[2])
            transactions = int(sys.argv[3])

            sim_account = BankAccount("10000002")
            simulator = TransactionSimulator(sim_account)

            simulator.run(users, transactions)

            print(
                f"Account {sim_account.account_number}: "
                f"£{sim_account.get_balance()}"
            )

        elif mode == "DeadlockTestSimulator":
            accounts = int(sys.argv[2])
            loops = int(sys.argv[3])

            deadlock_test = DeadlockTestSimulator()
            deadlock_test.run(accounts, loops)

        elif mode == "OverdraftTransferTest":
            accounts = int(sys.argv[2])
            loops = int(sys.argv[3])
            starting_balance = int(sys.argv[4])
            transfer_amount = int(sys.argv[5])

            overdraft_test = DeadlockTestSimulator(
                starting_balance=starting_balance,
                transfer_amount=transfer_amount
            )

            overdraft_test.run(accounts, loops, verbose=True)
    else:
        result = unittest.main(exit=False)

        if result.result.wasSuccessful():
            print("\nAll tests completed successfully\n")
