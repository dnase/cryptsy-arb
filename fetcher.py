import time
import Cryptsy

#time to hold in cache, in seconds - this only applies for google AppEngine
ttc = 5

lastFetchTime = 0

cryptsy_pubkey = 'YOUR_PUBLIC_KEY'
cryptsy_privkey = 'YOUR_PRIVATE_KEY'

def fetchMarketData():
    global lastFetchTime
    global cryptsy_pubkey
    global cryptsy_privkey
    global cryptsyHandle
    global marketData

    if getCachedTime():
        cryptsyHandle = Cryptsy.Cryptsy(cryptsy_pubkey, cryptsy_privkey)
        marketData = cryptsyHandle.getMarketDataV2()
        try:
            if marketData['success'] == 1:
                lastFetchTime = time.time()
        except:
            fetchMarketData()
        
def getLTCPrice():
    global cryptsyHandle
    cryptsyHandle = Cryptsy.Cryptsy(cryptsy_pubkey, cryptsy_privkey)
    r = cryptsyHandle.getSingleMarketData(3)
    try:
        return r['return']['markets']['LTC']['sellorders'][0]['price']
    except:
        getLTCPrice()

def getBalances():
    global cryptsyHandle
    cryptsyHandle = Cryptsy.Cryptsy(cryptsy_pubkey, cryptsy_privkey)
    r = cryptsyHandle.getInfo()
    return r['return']['balances_available']

def placeOrder(marketid, ordertype, quantity, price):
    global cryptsyHandle
    cryptsyHandle = Cryptsy.Cryptsy(cryptsy_pubkey, cryptsy_privkey)
    return cryptsyHandle.createOrder(marketid, ordertype, quantity, price)

def getCachedTime():
    return (time.time() - lastFetchTime) > ttc
