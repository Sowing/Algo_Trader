#!/usr/bin/env python3
import sqlite3
import os
import pandas as pd
import time
import API
import json

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
        #print()
        #_ = input("Press anykey to continue")
        connection.commit()
        return True
    else:
        #print()
        #_ = input("Press anykey to continue")
        return False 

def check_balancey_(user, date):
    #calculate g/l in usd, and return balance
    '''
    USER_ID = 1
    URL = 'http://apilayer.net/api/'
    SOURCE = 'USD'
    API_KEY = '45d4584351c4a10188d67c228f22b2a9'
    TYPE = 'live'
    Total_USD_worth = 0
    for key in currency_holdings:
        CURRENCY = [key]
        current_price = json.loads(API.get_currency_data(URL, SOURCE, API_KEY, TYPE, CURRENCY))['quotes']['USD%s' % key]
        Total_USD_worth = Total_USD_worth + currency_holdings[key]/current_price
    print('Worth total of %s USD' % Total_USD_worth)
    '''
    connection = sqlite3.connect('algoforexdb.db')
    cursor = connection.cursor()
    u_id = cursor.execute('''SELECT u_id FROM users WHERE username = ? ''', [user]).fetchone()[0]
    all_transactions = cursor.execute('''SELECT * FROM transactions join price_table on transactions.p_id = price_table.p_id WHERE transactions.u_id = ? ''', [u_id]).fetchall()
    df = pd.DataFrame(all_transactions, columns=['t_id', 'u_id', 'b/s', 'amount', 'p_id', 'timestamp_', 'p_id_r', 'st_id', 'price', 'date'])
    currency_holdings = {'USD':0}
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
            #currency_holdings['USD'] =  currency_holdings['USD'] - row['amount']/row['price']
        elif row['b/s'] == 's':
            currency_holdings[currency] = currency_holdings[currency] - row['amount'] 
            #currency_holdings['USD'] =  currency_holdings['USD'] + row['amount']/row['price']
    currency_holdings['USD+'] = 0
    currency_holdings['USD-'] = 0
    for currency in currency_holdings:
        if currency_holdings[currency] > 0 and 'USD' not in currency:
            print(currency)
            currency_price = cursor.execute('''SELECT price 
                                                from price_table join source_target_table 
                                                    on price_table.st_id = source_target_table.st_id
                                                where source_target_table.target = ? and price_table.timestamp = ?''', [currency, date]).fetchone()[0]
            currency_holdings['USD+'] = currency_holdings['USD+'] + float(currency_holdings[currency]) / float(currency_price)
        elif currency_holdings[currency] < 0 and 'USD' not in currency:
            print(currency)
            currency_price = cursor.execute('''SELECT price 
                                                from price_table join source_target_table 
                                                    on price_table.st_id = source_target_table.st_id
                                                where source_target_table.target = ? and price_table.timestamp = ?''', [currency, date]).fetchone()[0]
            currency_holdings['USD-'] = currency_holdings['USD-'] - float(currency_holdings[currency]) / float(currency_price)   
    starting_balance = cursor.execute('''SELECT balance FROM users WHERE username = ? ''', [user]).fetchone()[0]
    return starting_balance - currency_holdings['USD-'] - currency_holdings['USD+']

def check_balance(user, date, selected_currency,buy_sell='None', **kwargs):
    connection = sqlite3.connect('algoforexdb.db')
    cursor = connection.cursor()
    u_id = cursor.execute('''SELECT u_id FROM users WHERE username = ? ''', [user]).fetchone()[0]
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
            currency_holdings[currency] = [0,0]
        if row['b/s'] == 'b':
            currency_holdings[currency] = [currency_holdings[currency][0] - row['amount']/row['price'] , currency_holdings[currency][1] + row['amount']]
            #currency_holdings['USD'] =  currency_holdings['USD'] - row['amount']/row['price']
        elif row['b/s'] == 's':
            currency_holdings[currency] = [currency_holdings[currency][0] + row['amount']/row['price'] , currency_holdings[currency][1] - row['amount']]
            #currency_holdings['USD'] =  currency_holdings['USD'] + row['amount']/row['price']    
    starting_balance = cursor.execute('SELECT balance FROM users WHERE username = ? ', [user]).fetchone()[0]

    buying_power = starting_balance
    for key in currency_holdings:
        if key != selected_currency:
            if currency_holdings[key][0] > 0:
                buying_power = buying_power - currency_holdings[key][0]
            else:
                buying_power = buying_power + currency_holdings[key][0]
        elif buy_sell == 'buy': #if we can buy 4500 JPY , change the minus, buying power = currency short amount + balance
            current_price = cursor.execute('''SELECT price 
                                    from price_table join source_target_table 
                                        on price_table.st_id = source_target_table.st_id
                                    where source_target_table.target = ? and price_table.timestamp = ?''', [selected_currency, date]).fetchone()[0]
            if currency_holdings[key][0] > 0: #short case
                buying_power = buying_power - currency_holdings[key][0] + -1*(currency_holdings[key][1]/current_price)#net debt convert to current date usd
            else: #long case
                buying_power = buying_power + currency_holdings[key][0]  
        elif buy_sell == 'sell': #selling power = currency worth + buying power
            current_price = cursor.execute('''SELECT price 
                                    from price_table join source_target_table 
                                        on price_table.st_id = source_target_table.st_id
                                    where source_target_table.target = ? and price_table.timestamp = ?''', [selected_currency, date]).fetchone()[0]
            if currency_holdings[key][0] > 0: #short case
                buying_power = buying_power - currency_holdings[key][0] 
            else: #long case
                buying_power = buying_power + currency_holdings[key][0] + (currency_holdings[key][1]/current_price)#newtworth of currency to current date usd

    if selected_currency == 'all':
        return currency_holdings, starting_balance, buying_power
    else:             
        return buying_power

def check_portfolio(user, date, *args):
    #aggregate all b/s information and give balance on given date
    connection = sqlite3.connect('algoforexdb.db')
    cursor = connection.cursor()
    currency_holdings, starting_balance, buying_power = check_balance(user,date,'all')
    if not args:
        print('Current holdings:')
        print(currency_holdings)   
    ''' 
    for currency in currency_holdings:
        if currency_holdings[currency] > 0 and 'USD' not in currency:
            print(currency)
            currency_price = cursor.execute('SELECT price 
                                                from price_table join source_target_table 
                                                    on price_table.st_id = source_target_table.st_id
                                                where source_target_table.target = ? and price_table.timestamp = ?', [currency, date]).fetchone()[0]
            currency_holdings['USD+'] = currency_holdings['USD+'] + float(currency_holdings[currency]) / float(currency_price)
        elif currency_holdings[currency] < 0 and 'USD' not in currency:
            print(currency)
            currency_price = cursor.execute('SELECT price 
                                                from price_table join source_target_table 
                                                    on price_table.st_id = source_target_table.st_id
                                                where source_target_table.target = ? and price_table.timestamp = ?', [currency, date]).fetchone()[0]
            currency_holdings['USD-'] = currency_holdings['USD-'] - float(currency_holdings[currency]) / float(currency_price)    
    '''
    #Calculate usd
    
    Total_USD_worth = 0
    msg = []
    for key in currency_holdings:
        if 'USD' not in key:
        #continue
            current_price = cursor.execute('SELECT price from price_table join source_target_table on price_table.st_id = source_target_table.st_id where source_target_table.target = ? and price_table.timestamp = ?', (key, date)).fetchone()[0]
            Total_USD_worth = Total_USD_worth + currency_holdings[key][1]/current_price + currency_holdings[key][0]
            msg.append('You have %s USD of buying power left on %s currency.' % (check_balance(user, date, key, buy_sell='buy'),key))
            msg.append('You have %s USD of selling power left on %s currency.\n' % (check_balance(user, date, key, buy_sell='sell'), key))

    if not args:
        msg.append('Worth total of %s USD.' % (Total_USD_worth + starting_balance)) 
    #Calculate current worth
    
    return msg
def buy(user, currency, amount, date, leverage = 25):
    amount = int(amount) * int(leverage)
    connection = sqlite3.connect('algoforexdb.db')
    cursor = connection.cursor()
    starting_balance = cursor.execute('''SELECT balance FROM users WHERE username = ? ''', [user]).fetchone()[0]
    if check_balance(user, date, currency, buy_sell='buy')<= 0:
        return "You do not have enough balance"
    u_id = cursor.execute('''SELECT u_id FROM users WHERE username = ? ''', [user]).fetchone()[0]
    st_id = cursor.execute('''SELECT st_id FROM source_target_table WHERE target = ? ''', [currency]).fetchone()[0]
    p_id = cursor.execute('''SELECT p_id FROM price_table WHERE st_id = ? and timestamp = ? ''', [st_id, date]).fetchone()[0]
    price = cursor.execute('''SELECT price FROM price_table WHERE st_id = ? and timestamp = ? ''', [st_id, date]).fetchone()[0]
    trading_amount = float(amount)*float(price)  #amount passed in parameter is in USD
    if amount > check_balance(user, date, currency, buy_sell='buy'):
        msg = "You do not enough money to perform this transaction.\nTransaction failed."
        msg = msg + "\nYou can only buy %s of USD now" % check_balance(user, date, currency)
        return msg       
    cursor.execute('''INSERT INTO transactions (u_id, buy_sell, amount, p_id) values (?, ?, ?, ?) ''', (u_id, 'b', trading_amount, p_id))
    connection.commit()
    msg = 'You successfully bought %s USD worth of %s which is %s %s' % (amount, currency, trading_amount, currency)
    return msg
    #check_balance
    #insert a buy record


def sell(user, currency, amount, date, leverage = 25):
    #check_portfolio to see if user holds enough share
    amount = int(amount) * int(leverage)
    connection = sqlite3.connect('algoforexdb.db')
    cursor = connection.cursor()
    starting_balance = cursor.execute('''SELECT balance FROM users WHERE username = ? ''', [user]).fetchone()[0]
    if check_balance(user,date,currency, buy_sell='sell') < 0:
        msg = "You cannot short anymore"
        msg = msg + "\nYou can only short %s of USD now" % check_balance(user, date, currency)
        return msg
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
    '''
    if total_current_holdings < 0:        
        print("You don't have this currency")
        _ = input("Press anykey to continue")
        return
    elif total_current_holdings - float(amount) < 0:
        print("You don't have enough currency to sell ")
        print("Currently you only have %s in USD of %s " % (total_current_holdings/price, currency))
        _ = input("Press anykey to continue")
        return
    '''    
        
    #else:
    if amount < check_balance(user,date, currency, buy_sell='sell'):
        trading_amount = float(amount)*float(price)  #amount passed in parameter is in USD
        cursor.execute('''INSERT INTO transactions (u_id, buy_sell, amount, p_id) values (?, ?, ?, ?) ''', (u_id, 's', trading_amount, p_id))
        connection.commit()            
        msg = 'You successfully sold %s USD worth of %s which is %s %s' % (amount, currency, trading_amount, currency)
        return msg
    else:
        msg = "You don't have enough money to short.\nTransaction failed."
        msg = "\nYou can only short %s of USD now" % check_balance(user, date, currency)
    return msg

def delete_all_transactions():
    connection = sqlite3.connect('algoforexdb.db')
    cursor = connection.cursor()
    cursor.execute('''DELETE FROM transactions;''')
    cursor.execute('''VACUUM;''')
    connection.commit()
    return 'Successfully deleted all transactions'

def get_all_currency_information(date):
    connection = sqlite3.connect('algoforexdb.db')
    cursor = connection.cursor()
    current_price = cursor.execute('''SELECT source, target, price from price_table join source_target_table on price_table.st_id = source_target_table.st_id where price_table.timestamp = ?''', (date, )).fetchall()
    msg = []   
    for price in current_price:
        msg.append("1 %s equals %s %s " % (price[0], price[2], price[1]))
    connection.commit()
    return msg

def get_real_time_currency_information(currency):
    USER_ID = 1
    URL = 'http://apilayer.net/api/'
    SOURCE = 'USD'
    API_KEY = '45d4584351c4a10188d67c228f22b2a9'
    TYPE = 'live'
    CURRENCY = [currency]
    current_price = json.loads(API.get_currency_data(URL, SOURCE, API_KEY, TYPE, CURRENCY))['quotes']
    msg = []
    for currency in current_price:
        msg.append('1 %s equals %s %s' % ('USD', current_price[currency], currency[3:]))
    return msg

def strategy_1():
    pass