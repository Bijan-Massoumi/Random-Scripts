import urllib.request
import ssl
import json
import sys
import sqlite3
import datetime
from bashplotlib.scatterplot import plot_scatter

def calculate_stake(coins,prices):
    #calc
    return_list = {}
    total_val = 0
    for key in prices:
        coin_val = 0
        coin_val += prices[key]["USD"] * coins[key]
        print("Stake in {}: ${:f} at ${:f} per coin".format(key, coin_val,prices[key]['USD']))
        total_val += coin_val
        return_list[key] = coin_val
    print("Total Stake In Crypto: ${:f}".format(total_val))
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

    return_list.append( """CREATE TABLE IF NOT EXISTS all_coins (
         coin TEXT PRIMARY KEY
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

            add_to_coin_list(c, coin)

            c.execute(''' INSERT INTO {}(date,num_coins,value)
              VALUES(?,?,?) '''.format(coin.lower()) , (now.strftime("%Y-%m-%d"), coins[coin], cash[coin]))
        conn.commit()
    except Error as e:
        print(e)

def add_to_coin_list(cur, coin):
    cur.execute("""SELECT * FROM all_coins WHERE coin = '{}'""".format(coin))
    switch_val = cur.fetchall()
    if(switch_val == []):
        cur.execute(''' INSERT INTO all_coins(coin)
                  VALUES('{}') '''.format(coin))

def get_all_totals_by_day(conn):
    try:
        c =  conn.cursor()
        c.execute("""SELECT date, avg(value) FROM total GROUP BY date;""")
        return c.fetchall()
    except Error as e:
        print(e)

def get_all_totals_for_day(conn, date): #2018-01-05 format
    try:
        c =  conn.cursor()
        c.execute("""SELECT id, value FROM total WHERE date = '{}';""".format(date))
        return c.fetchall()
    except Error as e:
        print(e)

if __name__ == "__main__":
    db_file = "/Users/Bijibaba/Dropbox/Programs/random_scripts/crypto_stats/crypto_totals.db" #change to your own db
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '-i':
            coins = json.loads(input('Insert your coins labels and quantities  in "JSON Format", I.E. seperated by ":" and also seperating each pair by "," \n '
              'EX: {"ETH":3.4,"OMG":500}\n'))
        else:
            coins = {'XZC': 11.87, 'ETH':1.033, 'OMG':86.7, 'UFR': 1044}

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
        all_vals = get_all_totals_by_day(conn)
        todays_vals = get_all_totals_for_day(conn,"2018-01-05")
        #plot_scatter(todays_vals)
    else:
        print("Cannot create the database connection.\n Did you create your own "
              "sqllite db and change the db_file variable?")
