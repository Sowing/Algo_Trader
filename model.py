#!/usr/bin/env python3
import sqlite3
import os
import pandas as pd
import time

def check_user(name):
    connection = sqlite3.connect('algoforexdb.db')
    cursor = connection.cursor()
    cursor.execute('''
    SELECT * FROM users
    WHERE username=?
    ''', (name,))
    return cursor.fetchall()

def check_login(name, password):
    connection = sqlite3.connect('algoforexdb.db')
    cursor = connection.cursor()
    cursor.execute('''
    SELECT * FROM users
    WHERE username=? and password=?
    ''', (name,password))
    return cursor.fetchone()

def new_user(name, password):
    check = check_user(name)
    #print(check)
    if not check:
        connection = sqlite3.connect('algoforexdb.db')
        cursor = connection.cursor()
        cursor.execute('''
        INSERT INTO users(
        username,password,balance)
        VALUES(?,?,?)''',
        [name,password,100000.00])
        print("User %s Successfully created" % name)
        connection.commit()
        _ = input("Press anykey to continue")
        return True
    else:
        print("User %s already exits, try another name" % name)
        _ = input("Press anykey to continue")
        return False

def check_currency(currency):
    connection = sqlite3.connect('algoforexdb.db')
    cursor = connection.cursor()
    data = cursor.execute('''
    SELECT * FROM source_target_table WHERE target = ? ''', [currency]).fetchall()
    if data:
        return True
    else:
        print("No such currency found")
        return False

def send_to_database(registration):

    name= registration[0]
    password= registration[1]
    balance= 100000.00   

    check = check_user(name)
    #print(check)
    if not check:
        connection = sqlite3.connect('algoforexdb.db')
        cursor = connection.cursor()
        cursor.execute('''
        INSERT INTO users(
        username,password,balance)
        VALUES(?,?,?)''',
        (name,password,100000.00))
        print("User %s Successfully created" % name)
        _ = input("Press anykey to continue")
        connection.commit()
        return True
    else:
        print("User %s already exits, try another name" % name)
        _ = input("Press anykey to continue")
        return False

def check_balance(user, date):
    #calculate g/l in usd, and return balance
    return 0

def check_portfolio(user, date):
    #aggregate all b/s information and give balance on given date
    connection = sqlite3.connect('algoforexdb.db')
    cursor = connection.cursor()
    u_id = cursor.execute('''SELECT u_id FROM users WHERE username = ? ''', [user]).fetchone()[0]
    print(u_id)
    all_transactions = cursor.execute('''SELECT * FROM transactions join price_table on transactions.p_id = price_table.p_id WHERE transactions.u_id = ? ''', [u_id]).fetchall()
    df = pd.DataFrame(all_transactions, columns=['t_id', 'u_id', 'b/s', 'amount', 'p_id', 'timestamp_', 'p_id_r', 'st_id', 'price', 'date'])
    currency_holdings = {}
    for index, row in df.iterrows():
        transaction_time = time.strptime(row['date'], "%Y-%m-%d")
        current_time = time.strptime(date, "%Y-%m-%d")
        #if date is smaller than current given date
        if transaction_time > current_time:
            continue
        currency = cursor.execute('''SELECT target FROM source_target_table WHERE st_id = ? ''', [row['st_id']]).fetchone()[0]
        if currency not in currency_holdings:
            currency_holdings[currency] = 0
        if row['b/s'] == 'b':
            currency_holdings[currency] = currency_holdings[currency] + row['amount']
        elif row['b/s'] == 's':
            currency_holdings[currency] = currency_holdings[currency] - row['amount'] 
    print(currency_holdings)       
    #Calculate usd

    #Calculate current worth
    return

def buy(user, currency, amount, date):

    connection = sqlite3.connect('algoforexdb.db')
    cursor = connection.cursor()
    starting_balance = cursor.execute('''SELECT balance FROM users WHERE username = ? ''', [user]).fetchone()[0]
    if check_balance(user, date) + starting_balance <= 0:
        print("You do not have enough balance")
        _ = input("Press anykey to continue")
        return
    u_id = cursor.execute('''SELECT u_id FROM users WHERE username = ? ''', [user]).fetchone()[0]
    st_id = cursor.execute('''SELECT st_id FROM source_target_table WHERE target = ? ''', [currency]).fetchone()[0]
    p_id = cursor.execute('''SELECT p_id FROM price_table WHERE st_id = ? and timestamp = ? ''', [st_id, date]).fetchone()[0]
    price = cursor.execute('''SELECT price FROM price_table WHERE st_id = ? and timestamp = ? ''', [st_id, date]).fetchone()[0]
    trading_amount = float(amount)*float(price)  #amount passed in parameter is in USD
    cursor.execute('''INSERT INTO transactions (u_id, buy_sell, amount, p_id) values (?, ?, ?, ?) ''', (u_id, 'b', trading_amount, p_id))
    connection.commit()
    print('You successfully bought %s USD worth of %s which is %s %s' % (amount, currency, trading_amount, currency))
    _ = input("Press anykey to continue")
    return
    #check_balance
    #insert a buy record


def sell(user, currency, amount, date):
    #check_portfolio to see if user holds enough share
    connection = sqlite3.connect('algoforexdb.db')
    cursor = connection.cursor()
    u_id = cursor.execute('''SELECT u_id FROM users WHERE username = ? ''', [user]).fetchone()[0]
    st_id = cursor.execute('''SELECT st_id FROM source_target_table WHERE target = ? ''', [currency]).fetchone()[0]
    p_id = cursor.execute('''SELECT p_id FROM price_table WHERE st_id = ? and timestamp = ? ''', [st_id, date]).fetchone()[0]
    price = cursor.execute('''SELECT price FROM price_table WHERE st_id = ? and timestamp = ? ''', [st_id, date]).fetchone()[0]
    all_transactions = cursor.execute('''SELECT * FROM transactions join price_table on transactions.p_id = price_table.p_id
         WHERE transactions.u_id = ? and price_table.st_id = ? ''', (u_id, st_id)).fetchall()
    df = pd.DataFrame(all_transactions, columns=['t_id', 'u_id', 'b/s', 'amount', 'p_id', 'timestamp_', 'p_id_r', 'st_id', 'price', 'date'])
    total_current_holdings = 0.0
    for index, row in df.iterrows():
        transaction_time = time.strptime(row['date'], "%Y-%m-%d")
        current_time = time.strptime(date, "%Y-%m-%d")
        #if date is smaller than current given date
        if transaction_time > current_time:
            continue
        if row['b/s'] == 'b':
            total_current_holdings = total_current_holdings + row['amount']
        elif row['b/s'] == 's':
            total_current_holdings = total_current_holdings - row['amount']

    if total_current_holdings <= 0:
        print("You don't have this currency")
        _ = input("Press anykey to continue")
        return
    elif total_current_holdings - float(amount) < 0:
        print("You don't have enough currency to sell ")
        print("Currently you only have %s in USD of %s " % (total_current_holdings/price, currency))
        _ = input("Press anykey to continue")
        return
    else:
        trading_amount = float(amount)*float(price)  #amount passed in parameter is in USD
        cursor.execute('''INSERT INTO transactions (u_id, buy_sell, amount, p_id) values (?, ?, ?, ?) ''', (u_id, 's', trading_amount, p_id))
        connection.commit()            
        print('You successfully sold %s USD worth of %s which is %s %s' % (amount, currency, trading_amount, currency))
        _ = input("Press anykey to continue")
        return
    return









