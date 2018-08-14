#!/usr/bin/env python3
import sqlite3
connection=sqlite3.connect('algoforexdb.db')
cursor= connection.cursor()

try:
	cursor.execute('''
	    CREATE TABLE users(
	    u_id INTEGER PRIMARY KEY AUTOINCREMENT,
	    username TEXT,
	    password TEXT,
	    balance FLOAT 
	    CONSTRAINT username_unique UNIQUE (username)  
	)
	''')
except:
	pass

try:
    cursor.execute('''
        CREATE TABLE source_target_table(
        st_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        target TEXT,
        CONSTRAINT source_target_unique UNIQUE (source, target) 
        )
    ''')
except:
	pass
	
try:
	cursor.execute('''
		CREATE TABLE transactions(
		t_id INTEGER PRIMARY KEY AUTOINCREMENT,

		u_id INTEGER,
		buy_sell TEXT,
		amount FLOAT,
		p_id INTEGER,
		timestamp TEXT,

		CHECK(buy_sell="s" or buy_sell="b"),
		FOREIGN KEY (u_id) REFERENCES users(u_id),
		FOREIGN KEY (p_id) REFERENCES price_table(p_id)
     	)
	''')
except:
	pass


try:	
	cursor.execute('''
		CREATE TABLE price_table(
		p_id INTEGER PRIMARY KEY AUTOINCREMENT,
		st_id INTEGER,
		price FLOAT,
		timestamp TEXT,
		CONSTRAINT source_target_price_unique UNIQUE (st_id, timestamp) 
		FOREIGN KEY (st_id) REFERENCES source_target_table(st_id)
		)
	''')
except:
	raise
connection.commit()
connection.close()
