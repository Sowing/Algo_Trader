#!/usr/bin/env python3
import model
import view
import sys
from datetime import date as date_module
import API
from flask import Flask
from flask import request
from flask import render_template, abort, url_for, redirect,session
from flask_bootstrap import Bootstrap
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
Bootstrap(app)

leverage = 25

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/trader_welcome', methods=['POST', 'GET'] )
def welcome():
    error = None
    if request.method == 'POST':
        choice = request.form['choice']#view.welcome()
        if choice == '1':
            return redirect(url_for('login'))
        elif choice == '2':
            return redirect(url_for('register'))
        else:
            error = "Invalid Input"
            return render_template('trader_welcome.html', error=error)
    else:  
        return render_template('trader_welcome.html')  

@app.route('/trader_welcome/login', methods=['POST', 'GET'] )
def login():
    error = None
    if request.method == 'POST':
        login_info = [request.form['username'], request.form['password']]
        if not model.check_user(login_info[0]):
            error = "No user found, please register!"
            return render_template('trader_login.html', error=error)

        elif not model.check_login(login_info[0], login_info[1]):
            error = "Password is wrong, please retry"
            return render_template('trader_login.html', error=error)

        else:
            print("User %s login successfully" % login_info[0])
            session['username'] = login_info[0]
            session['leverage'] = 25
            session['level'] = 0
            return redirect(url_for('select_page',username=login_info[0],leverage=session['leverage'],level=session['level']))
    else:
        return render_template('trader_login.html')

@app.route('/trader_welcome/register', methods=['POST', 'GET'] )
def register():
    if request.method == 'POST':
        user = [request.form['username'], request.form['password']]
        status = model.send_to_database(user)
        if status:
            error = "User %s Successfully created" % user[0]
            return redirect(url_for('welcome'))
        else:
            print('111')
            error = "User %s already exits, try another name" % user[0]
            return render_template('trader_register.html', error=error)
        
    return render_template('trader_register.html')

@app.route('/trader_welcome/select_page', methods=['POST', 'GET'] )    
def select_page():
    current_user = session['username']
    print(session)
    error = None
    #choice = view.select()
    if request.method == 'POST':
        choice = request.form['choice']
        #level = request.args['level']
        #print(level, choice)
        if choice == 'SL':
            if session['level'] == 0:
                session['level'] = 1
                return render_template('trader_select.html', choice=choice,leverage=session['leverage'],level=session['level'])      
            elif session['level'] == 1:# request.args['level'] == 1:
                print('333')
                print('new leverage %s' % request.form['leverage'])
                session['leverage'] = request.form['leverage']
                session['level'] = 0
                print('new leverage %s' % session['leverage'])
                return render_template('trader_select.html', choice=choice, leverage=session['leverage'], level=session['level'])

        elif choice == 'B':
            if session['level'] == 0:
                session['level'] = 1
                return render_template('trader_select.html', choice=choice,leverage=session['leverage'],level=session['level'])      
            elif session['level'] == 1:
                currency = request.form['currency']
                if not model.check_currency(currency):
                    error = 'No such currency found'
                    return render_template('trader_select.html', error=error, choice=choice, leverage=session['leverage'], level=session['level'])      
                amount = request.form['amount']
                date = request.form['date']
                session['level'] = 0
                print(currency,amount, date)
                msg = model.buy(session['username'], currency, amount, date, session['leverage'])
                return render_template('trader_select.html', choice=choice, leverage=session['leverage'], level=session['level'], msg=msg) 

        elif choice == 'S':
            if session['level'] == 0:
                session['level'] = 1
                return render_template('trader_select.html', choice=choice,leverage=session['leverage'],level=session['level'])      
            elif session['level'] == 1:
                currency = request.form['currency']
                if not model.check_currency(currency):
                    error = 'No such currency found'
                    return render_template('trader_select.html', error=error, choice=choice, leverage=session['leverage'], level=session['level'])      

                amount = request.form['amount']
                date =  request.form['date']
                session['level'] = 0
                msg = model.sell(session['username'], currency, amount, date, session['leverage'])
                return render_template('trader_select.html', choice=choice, leverage=session['leverage'], level=session['level'], msg=msg) 
            
        elif choice == 'D':
            #Delete all transactions
            if session['level'] == 0:
                session['level'] = 1
                return render_template('trader_select.html', choice=choice,leverage=session['leverage'],level=session['level'])      
            elif session['level'] == 1:
                if request.form['delete'] == '1':
                    msg = model.delete_all_transactions()
                    session['level'] = 0
                    return render_template('trader_select.html', choice=choice,leverage=session['leverage'],level=session['level'], msg=msg) 
                else:
                    return render_template('trader_select.html', choice=choice,leverage=session['leverage'],level=session['level'])
        elif choice == 'L':
            #lookup currency price
            if session['level'] == 0:
                session['level'] = 1
                return render_template('trader_select.html', choice=choice,leverage=session['leverage'],level=session['level'])      
            elif session['level'] == 1:
                date = request.form['date']
                msg = model.get_all_currency_information(date)
                session['level'] = 0
                return render_template('trader_select.html', choice=choice,leverage=session['leverage'],level=session['level'], msg=msg) 
             
        elif choice == 'LR':
            #lookup currency real-time price
            if session['level'] == 0:
                session['level'] = 1
                return render_template('trader_select.html', choice=choice,leverage=session['leverage'],level=session['level'])      
            elif session['level'] == 1:
                currency = request.form['currency']
                msg = model.get_real_time_currency_information(currency)
                return render_template('trader_select.html', choice=choice,leverage=session['leverage'],level=session['level'], msg=msg) 

            
        elif choice == 'V':
            #View balance
            #print("You currently have %s in your balance" % model.get_balance(current_user))
            if session['level'] == 0:
                session['level'] = 1
                return render_template('trader_select.html', choice=choice,leverage=session['leverage'],level=session['level'])      
            elif session['level'] == 1:
                date = request.form['date']
           # try:
                msg = model.check_portfolio(session['username'], date)
        #    except:
         #       print('No price found')
                return render_template('trader_select.html', choice=choice,leverage=session['leverage'],level=session['level'], msg=msg) 

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
            session.clear()
            return redirect(url_for('welcome'))
        else:
            _ = input('Entered wrong choice!!! Hit any key to retry')
            return
    session['level'] = 0
    return render_template('trader_select.html', error=error)

if __name__ == "__main__":
        app.run()
'''
while 1:
    current_user = welcome()
    if current_user:
        while 1:
            select_page(current_user)
'''
