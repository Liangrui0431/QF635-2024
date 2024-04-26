"""
In object-oriented programming, A class represents an entity with properties and behavior (methods).

Reference: https://realpython.com/python3-object-oriented-programming/#what-is-object-oriented-programming-in-python

"""


# Define an Account class
class Account:
    # A constructor method to initialize account with an identifier
    def __init__(self, identifier):
        self.identifier=identifier
        self.balance=0

    # Provide output when account object is printed
    def __str__(self):
        return "Account identifier={}, balance={:.2f}".format(self.identifier, self.balance)

    # To get balance of this account
    def balance(self):
        return self.balance

    # to deposit money to this account
    def deposit(self, amount):
        self.balance=self.balance+amount

    # to withdraw money from this account
    def withdraw(self, amount):
        self.balance=self.balance-amount


# Define a main method
if __name__ == '__main__':
    account1=Account('current')

    print(account1)
    account1.deposit(1000000)
    account1.withdraw(50000)
    print(account1)
