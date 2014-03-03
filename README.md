cryptsy-arb
===========

Python script for simple Cryptsy arbitrage

No special libraries or dependencies. Works best on Python 2.7, I haven't tested on 3.3+

Make sure to edit fetcher.py and put in your cryptsy public and private API keys.

Credit to https://github.com/ScriptProdigy/CryptsyPythonAPI for the Cryptsy API interface. I hacked it up a bit for my purposes.

Run with "python cmd.py [max % to spend in BTC/LTC as float]"

i.e.

python cmd.py 0.25

or

chmod +x cmd.py
./cmd.py 0.33

Default max percentage to spend on a buy order is 99%.

This script will not make sell orders, only buy orders.

USE AT YOUR OWN RISK. SEE GPL.txt FOR LICENSE TERMS.
