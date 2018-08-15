#!/usr/bin/env python3
import os

def welcome():
    os.system('clear')
    print('''******************************************\n''')
    print('''Welcome to Forex Terminal Trader!\n''')

    choice = input('login? or new user \n' \
        'login (1) \n'\
        'register (2)\n')
    return choice    

def register():
    os.system('clear')
    print('''******************************************\n''')
    print('''Registration Page\n''')    
    username = input('please enter your username: ')
    password = input('please enter your password: ')
    return [username, password]

def login():
    os.system('clear')
    print('''******************************************\n''')
    print('''Login Page\n''')  
    username = input('please enter your username: ')
    password = input('please enter your password: ')   
    return [username, password]

def select():
    os.system('clear')
    print('''******************************************\n''')
    print('''Terminal Trader\n''')
    print('''[B] Buy\n''')
    print('''[S] Sell\n''')
    print('''[D] Delete All transactions\n''')
    print('''[L] Look-up currency price on a date\n''')
    print('''[LR] Look-up real-time currency price\n''')
    print('''[V] View Balance\n''')
    print('''[P] See P/L\n''')
    print('''[E] Exit\n\n''')
    selection = input('What do you want to do?\n')
    return selection

def get_currency():
    currency = input('Which currency you want to trade?')
    print("You would like to trade currency %s" % currency)
    return currency

def get_amount(type):

    amount = input('How much money you want to %s (In USD)?' % type)
    print("You would like to %s %s USD" % (type,amount))
    return amount

def enter_date():
    amount = input('Please enter date (From 2017-07-04 to 2018-08-02): ')
    return amount