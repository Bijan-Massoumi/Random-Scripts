import urllib.request
import ssl
import json
import sys

def calculate_stake(coins,prices):
    #calc
    total_val = 0
    for key in prices:
        coin_val = 0
        coin_val += prices[key]["USD"] * coins[key]
        print("Stake in {}: {:f}".format(key, coin_val))
        total_val += coin_val
    print("Total Stake In Crypto: {:f}".format(total_val))

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '-i':
            coins = json.loads(input('Insert your coins labels and quantities  in "JSON Format", I.E. seperated by ":" and also seperating each pair by "," \n '
              'EX: {"ETH":3.4,"OMG":500}\n'))
        else:
            coins = {'PIVX': 98, 'ETH':1.290, 'OMG':86.7, 'UFR': 1044}

        context = ssl._create_unverified_context()
        request_url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms="
        for i,key in enumerate(coins):
            if i == len(coins.keys()) - 1:
                request_url += key
            else:
                request_url += "{},".format(key)
        request_url += "&tsyms=USD"

        prices = json.loads(urllib.request.urlopen(request_url,context = context).read())

        calculate_stake(coins,prices)
    except:
        raise Exception("ERROR: Check that labels and format are correct")
