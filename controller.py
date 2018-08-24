#!/usr/bin/env python3
import model
import view
import sys
from datetime import date as date_module
import API


leverage = 25

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
    if choice == 'SL':
        #lookup currency real-time price
        global leverage
        leverage = int(input('Please set leverage: '))
        print('Leverage is now %s' % leverage)
        _ = input("\n\nHit any key to return")
        return

    elif choice == 'B':
        #Buy
        currency = view.get_currency()
        if not model.check_currency(currency):
            _ = input('\n\nHit any key to return')
            print("Going to selection page")
            return      
        amount = view.get_amount('Buy',leverage)
        #print(amount)
        date = view.enter_date()
        model.buy(current_user, currency, amount, date, leverage)
        return

    elif choice == 'S':
        #Sell
        currency = view.get_currency()
        if not model.check_currency(currency):
            _ = input('\n\nHit any key to return')
            print("Going to selection page")
            return    
        amount = view.get_amount('Sell',leverage)
        date = view.enter_date()
        model.sell(current_user, currency, amount, date, leverage)
        return
    elif choice == 'D':
        #Delete all transactions
        model.delete_all_transactions()
        _ = input('\n\nHit any key to return')
        return
    elif choice == 'L':
        #lookup currency price
        date = view.enter_date()
        model.get_all_currency_information(date)
        _ = input("\n\nHit any key to return")
        return
        
    elif choice == 'LR':
        #lookup currency real-time price
        currency = input('Please enter currency symbol (JPY, EUR and etc.): ')
        model.get_real_time_currency_information(currency)
        _ = input("\n\nHit any key to return")
        return
        
    elif choice == 'V':
        #View balance
        #print("You currently have %s in your balance" % model.get_balance(current_user))
        date = view.enter_date()
       # try:
        model.check_portfolio(current_user, date)
    #    except:
     #       print('No price found')
        _ = input('\n\nHit any key to return')
        return 

    elif choice == 'P':
        #See P/L
        print('Input date range to see performance in these range')
        start_date = view.enter_date()
        end_date = view.enter_date()
        start_date = list(map(int,start_date.split('-')))
        end_date = list(map(int,end_date.split('-')))
        start_date = date_module(start_date[0], start_date[1], start_date[2])
        end_date = date_module(end_date[0], end_date[1], end_date[2])
        for single_date in API.daterange(start_date, end_date):
            DATE = single_date.strftime("%Y-%m-%d")
            print('On Date %s you have %s' % (DATE, model.check_portfolio(current_user,DATE,'calculation')))
        _ = input('\n\nHit any key to return')
        return

    elif choice == 'E':
        # quit
        sys.exit()
    else:
        _ = input('Entered wrong choice!!! Hit any key to retry')
        return

while 1:
    current_user = welcome()
    if current_user:
        while 1:
            select_page(current_user)
