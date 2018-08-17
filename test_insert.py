#!/usr/bin/env python3
def useless():
    import sqlite3
    connection=sqlite3.connect('algoforexdb.db')
    cursor= connection.cursor()
    cursor.execute('''
    INSERT INTO users(
    username,password,balance)
    VALUES(?,?,?)''',
    ['nan1','222',100000.00])
    print("User %s Successfully created" % 'nan1')
    connection.commit()

#test
from datetime import timedelta, date

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = date(2013, 1, 1)
end_date = date(2015, 6, 2)
for single_date in daterange(start_date, end_date):
    print(single_date.strftime("%Y-%m-%d"))
