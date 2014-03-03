#!/usr/bin/python
import fetcher
import operator
import sys

if len(sys.argv) == 2:
    ratio = float(sys.argv[1])
else:
    ratio = 0.99

#conservatively estimate profit with 1% total fees (usually less)
fee_ratio = 0.01

simpleArb       = []
ltcMarkets      = []
btcMarkets      = []
doubleMarkets   = []
outBuff         = {}

#helper function to format floats
def ff(f):
    return format(f, '.8f')

try:
    print "Fetching market data."
    fetcher.fetchMarketData()
except:
    sys.exit("ERROR: Could not fetch market data.")

print "Processing market data."
for marketName in fetcher.marketData['return']['markets']:
    try:
        lo_sell = fetcher.marketData['return']['markets'][marketName]['sellorders'][0]['price']
        hi_buy  = fetcher.marketData['return']['markets'][marketName]['buyorders'][0]['price']
        sn = fetcher.marketData['return']['markets'][marketName]['primarycode']
        marketid = fetcher.marketData['return']['markets'][marketName]['marketid']
        if hi_buy > lo_sell:
            proft = hi_buy - lo_sell
            simpleArb.append({'profit' : profit, 'market': marketName, 'hi_buy': hi_buy, 'lo_sell': lo_sell, 'sn': sn})
        if fetcher.marketData['return']['markets'][marketName]['secondarycode'] == 'LTC':
            ltcMarkets.append({'market': marketName, 'hi_buy': hi_buy, 'lo_sell': lo_sell, 'sn': sn, 'marketid': marketid})
        if fetcher.marketData['return']['markets'][marketName]['secondarycode'] == 'BTC':
            btcMarkets.append({'market': marketName, 'hi_buy': hi_buy, 'lo_sell': lo_sell, 'sn': sn, 'marketid': marketid})
    except:
        pass

try:
    print "Fetching LTC price."
    ltc_price = float(fetcher.getLTCPrice())
    print("LTC Price: " + format(ltc_price, '.8f')) 
except:
    sys.exit("ERROR: Could not fetch LTC price.")

try:
    print "Fetching balances."
    balances = fetcher.getBalances()
    btc_balance = float(balances['BTC'])
    ltc_balance = float(balances['LTC'])
except:
    sys.exit("ERROR: Could not fetch balances.")

#check for simple arb opps
for mkt in simpleArb:
    print(mkt['market'] + " : " + mkt['profit'])

#check for ltc -> btc arb opps or btc -> ltc arb opps
print "Processing arbitrage opportunities."
for lmkt in ltcMarkets:
    for bmkt in btcMarkets:
        if lmkt['sn'] == bmkt['sn']:
            print("Checking " + lmkt['sn'] + "...")
            try:
                sn              = lmkt['sn']
                ltc_marketid    = lmkt['marketid']
                btc_marketid    = bmkt['marketid']
                ltc_hi_buy      = float(lmkt['hi_buy'])
                btc_hi_buy      = float(bmkt['hi_buy'])
                ltc_lo_sell     = float(lmkt['lo_sell'])
                btc_lo_sell     = float(bmkt['lo_sell'])
                ltc_hi_buy_btc  = ltc_hi_buy * ltc_price
                ltc_lo_sell_btc = ltc_lo_sell * ltc_price

                print("Comparing buy price of " + ff(ltc_lo_sell) + " LTC to sell price of " + ff(btc_hi_buy) + " BTC")
                if btc_hi_buy > ltc_lo_sell_btc:
                    #profit to be made buying for LTC and selling for BTC
                    num_purchasable = (ltc_balance / ltc_lo_sell) * ratio
                    total_fees      = (num_purchasable * ltc_lo_sell) * fee_ratio
                    total_profit    = ((btc_hi_buy - ltc_lo_sell) * num_purchasable) - total_fees
                    print("Calculated total profit: " + ff(total_profit))
                    outstr          = "buy\t" + ff(num_purchasable) + "\t" + sn
                    outstr         += "\t@\t" + ff(ltc_lo_sell) + " LTC"
                    outstr         += "\tsell\t@\t" + ff(btc_hi_buy) + " BTC"
                    outstr         += "\t(" + ff(total_profit) + " BTC profit)? (y/n): "
                    outBuff[total_profit] = {
                        'outstr'            : outstr,
                        'num_purchasable'   : num_purchasable,
                        'buy_marketid'      : ltc_marketid,
                        'sell_marketid'     : btc_marketid,
                        'price'             : ff(ltc_lo_sell)
                    }

                print("Comparing buy price of " + ff(btc_lo_sell) + " BTC to sell price of " + ff(ltc_hi_buy) + " LTC")
                if ltc_hi_buy_btc > btc_lo_sell:
                    #profit to be made buying for BTC and selling for LTC
                    num_purchasable = (btc_balance / btc_lo_sell) * ratio
                    total_fees      = (num_purchasable * btc_lo_sell) * fee_ratio
                    total_profit    = ((ltc_hi_buy_btc - btc_lo_sell) * num_purchasable) - total_fees
                    print("Calculated total profit: " + ff(total_profit))
                    outstr          = "buy\t" + ff(num_purchasable) + "\t" + sn
                    outstr         += "\t@\t" + ff(btc_lo_sell) + " BTC"
                    outstr         += "\tsell\t@\t" + ff(ltc_hi_buy) + " LTC"
                    outstr         += "\t(" + ff(total_profit) + " BTC profit)? (y/n): "
                    outBuff[total_profit] = {
                        'outstr'            : outstr,
                        'num_purchasable'   : num_purchasable,
                        'buy_marketid'      : btc_marketid,
                        'sell_marketid'     : ltc_marketid,
                        'price'             : ff(btc_lo_sell)
                    }

                print("-----------")

            except:
                pass

sorted_data = sorted(outBuff.iteritems(), key=operator.itemgetter(0), reverse=True)

for (total_profit, data) in sorted_data:
    if data['num_purchasable'] > 0 and total_profit > 0:
        place_order =  raw_input(data['outstr'])
        if place_order == 'y':
            r = fetcher.placeOrder(data['buy_marketid'], 'Buy', data['num_purchasable'], data['price'])
            print(str(r))

print "Done."