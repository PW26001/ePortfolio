README - Unit 6 Banking System

This README provides instructions for reproducing the test results for the Unit 6 banking system.

Run unit tests:
python BankingApp.py

Run TransactionSimulator with 50 users performing 100 transactions each:
python BankingApp.py TransactionSimulator 50 100

Run DeadlockTestSimulator with 10 accounts and 3 test loops:
python BankingApp.py DeadlockTestSimulator 10 3

Run OverdraftTransferTest with 7 accounts, 1 loop, a starting balance of £100 and a transfer amount of £50:
python BankingApp.py OverdraftTransferTest 7 1 100 50

The parameters can be modified to vary the number of accounts, loops, transactions or transfer amounts in order to perform additional validation and stress testing.