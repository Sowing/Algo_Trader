#!/usr/bin/env python3
import model
import view
import sys

def welcome():
    choice = view.welcome()
    if choice == '1':
        return login()
    elif choice == '2':
        return register()
    else:
        return welcome()    


def login():
    login_info = view.login()
    if not model.check_user(login_info[0]):
        print("No user found, please register!")
        _ = input('\n\nHit any key to retry')
        return
    elif not model.check_login(login_info[0], login_info[1]):
        print("Password is wrong, please retry")
        _ = input('\n\nHit any key to retry')
        return 
    else:
        print("User %s login successfully" % login_info[0])
        _ = input('\n\nHit any key to continue')
        return login_info[0]

def register():
    user = view.register()
    model.send_to_database(user)
    
def select_page(current_user):
    choice = view.select()
    if choice == 'B':
        #Buy
        currency = view.get_currency()
        if not model.check_currency(currency):
            _ = input('\n\nHit any key to return')
            print("Going to selection page")
            return      
        amount = view.get_amount('Buy')
        #print(amount)
        date = '2018-07-30'
        model.buy(current_user, currency, amount, date)
        return

    elif choice == 'S':
        #Sell
        currency = view.get_currency()
        if not model.check_currency(currency):
            _ = input('\n\nHit any key to return')
            print("Going to selection page")
            return    
        amount = view.get_amount('Sell')
        date = '2018-07-30'
        model.sell(current_user, currency, amount, date)
        return
        '''
    elif choice == 'L':
        #lookup ticker
        model.get_all_ticker_information()
        _ = input("\n\nHit any key to return")
        return
    elif choice == 'Q':
        #Quote symbol
        return
        '''

    elif choice == 'V':
        #View balance
        #print("You currently have %s in your balance" % model.get_balance(current_user))
        date = '2018-08-03'
        model.check_portfolio(current_user, date)
        _ = input('\n\nHit any key to return')
        return 
    '''
    elif choice == 'See P/L':
        #See P/L
        print('Not working yet')
        _ = input('\n\nHit any key to return')
        return
    elif choice == 'E':
        # quit
        sys.exit()
    else:
        _ = input('Entered wrong choice!!! Hit any key to retry')
        return
    '''
while 1:
    current_user = welcome()
    if current_user:
        while 1:
            select_page(current_user)