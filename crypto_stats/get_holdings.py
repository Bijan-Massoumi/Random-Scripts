import urllib.request
import ssl
import json
import sys
import sqlite3
import datetime

def calculate_stake(coins,prices):
    #calc
    return_list = {}
    total_val = 0
    for key in prices:
        coin_val = 0
        coin_val += prices[key]["USD"] * coins[key]
        print("Stake in {}: {:f}".format(key, coin_val))
        total_val += coin_val
        return_list[key] = coin_val
    print("Total Stake In Crypto: {:f}".format(total_val))
    return_list["total"] = total_val
    return return_list

def create_connection(db_name):
    try:
        conn = sqlite3.connect(db_name)
        return conn
    except Error as e:
        print(e)
    return None

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def query_crypto_compare(coins):
    context = ssl._create_unverified_context()
    request_url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms="
    for i,key in enumerate(coins):
        if i == len(coins.keys()) - 1:
            request_url += key
        else:
            request_url += "{},".format(key)
    request_url += "&tsyms=USD"

    return json.loads(urllib.request.urlopen(request_url,context = context).read())


def create_table_strings(coins):
    return_list = []

    return_list.append( """CREATE TABLE IF NOT EXISTS total (
         id integer PRIMARY KEY,
         date TEXT,
         num_currency INTEGER,
         value REAL
        );""")

    for coin in coins:
        return_list.append( """CREATE TABLE IF NOT EXISTS {} (
             id integer PRIMARY KEY,
             date TEXT,
             num_coins INTEGER,
             value REAL
        );""".format(coin.lower()))

    return return_list


def update_tables(conn,coins,cash):
    now = datetime.datetime.now()
    try:
        c = conn.cursor()
        c.execute(''' INSERT INTO total(date,num_currency,value)
              VALUES(?,?,?) ''',(now.strftime("%Y-%m-%d"),len(cash),cash['total']))

        for coin in cash:
            if coin == 'total':
                continue

            print((now.strftime("%Y-%m-%d"), coins[coin], cash[coin]))
            c.execute(''' INSERT INTO {}(date,num_coins,value)
              VALUES(?,?,?) '''.format(coin.lower()) , (now.strftime("%Y-%m-%d"), coins[coin], cash[coin]))
        conn.commit()
    except Error as e:
        print(e)



if __name__ == "__main__":
    db_file = "/Users/Bijibaba/Dropbox/Programs/random_scripts/crypto_stats/crypto_totals.db" #change to your own db
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '-i':
            coins = json.loads(input('Insert your coins labels and quantities  in "JSON Format", I.E. seperated by ":" and also seperating each pair by "," \n '
              'EX: {"ETH":3.4,"OMG":500}\n'))
        else:
            coins = {'PIVX': 98, 'ETH':1.290, 'OMG':86.7, 'UFR': 1044}

        prices = query_crypto_compare(coins)
        cash = calculate_stake(coins,prices)
    except:
        raise Exception("ERROR: Check that labels and format are correct")

    conn = create_connection(db_file)
    if conn is not None:
        tables = create_table_strings(cash.keys())
        for table in tables:
            create_table(conn, table)
        update_tables(conn, coins, cash)
    else:
        print("Cannot create the database connection.\n Did you create your own "
              "sqllite db and change the db_file variable?")