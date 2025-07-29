import sys
import os
import yfinance as yf
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

test = yf.download('AAPL', start='2020-01-01', end='2021-01-01')['Close']
print(test.squeeze())
column_split = test.name.split(" ")
currency = column_split[-1]
test.name = "Close"
print(test.name)

print(type(test.index))
print(test.index.tz)

print('\n \n \n')
test = test.index.tz_localize(None)
print(test)
