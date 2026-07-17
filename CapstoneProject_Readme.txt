README - Capstone Project Banking System

This README provides instructions for reproducing the test results for the Capstone Project banking system.

:: Unit Tests

python CapstoneProject.py

or:

python CapstoneProject.py UnitTests

Expected result:
All 14 unit tests should pass.


:: Demo

python CapstoneProject.py Demo

Expected result:
The demo should create three transactions:
- deposit - successful
- transfer - successful
- withdrawal - failed

The transaction report should show:
successful_transactions: 2
failed_transactions: 1


:: AuthenticationTest

python CapstoneProject.py AuthenticationTest

Expected result:
The successful login should return True.
The failed login should return False.
The failed login should be recorded by the injected MockSecurityLogger.

This demonstrates dependency injection, as AuthenticationService is tested using a mock logger instead of the normal SecurityLogger.


:: MonitoringTest - standard monitoring

python CapstoneProject.py MonitoringTest 600 standard

Expected result:
Standard monitoring should flag the £600 transaction as a large transaction.


:: MonitoringTest - strict monitoring

python CapstoneProject.py MonitoringTest 150 strict

Expected result:
Strict monitoring should flag the £150 transaction as a large transaction.


########
## For the following tests, the numbers can be modified for different scenarios / stress testing
########


:: TransactionSimulator

python CapstoneProject.py TransactionSimulator 50 100

Runs TransactionSimulator with 50 users performing 100 transactions each.

Expected result:
Final balance = £25000.


:: DeadlockTestSimulator

python CapstoneProject.py DeadlockTestSimulator 10 3

Runs DeadlockTestSimulator with 10 accounts and 3 test loops.

Expected result:
The total balance remains unchanged and no deadlock occurs.
Total balance = £10000.


:: OverdraftTransferTest

python CapstoneProject.py OverdraftTransferTest 7 1 100 50

Runs OverdraftTransferTest with 7 accounts, 1 loop, a starting balance of £100 and a transfer amount of £50.

Expected result:
Some transfers may be denied if balances are too low, but the total balance remains unchanged.
Total balance = £700.