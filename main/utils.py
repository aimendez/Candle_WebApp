import pandas as pd 
from yahooquery import Ticker

def get_data(symbol, start=None, end=None):

	# Historical Data with yfinance:
	#ticker = yf.Ticker(symbol)
	#data = ticker.history(period="max")
	#data = data[['Open', 'High', 'Low', 'Close', 'Volume']]

	# Historical Data with alpaca API
	#data = api_.get_barset(symbol, timeframe='1D', start=start, end=end).df
	#data.columns = ['open', 'high', 'low', 'close', 'volume']

	# Historical Data with yahooquery
	ticker = Ticker(symbol, asynchronous=True)
	if start == None and end == None:
		data = ticker.history(period='1d', interval='1d')
	else:
		data = ticker.history(period='1d', interval='1d', start=start, end=end)

	if not isinstance(data, dict):
		data = data.droplevel(0)
		return data
	else:
		data = pd.DataFrame()
		return data 



