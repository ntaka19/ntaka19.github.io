import pandas as pd
from pandas_datareader import data  as pdr #修正
from datetime import date
from dateutil.relativedelta import relativedelta
import yfinance as yf #追加
yf.pdr_override() #追加

#today = date.today()
#ago = today - relativedelta(years=1)
#data = pdr.get_data_yahoo('^N225',  ago, today) #修正
#print(data)


forex_data_minute = yf.download('USDJPY=X', period='1d', interval='1m')

# Set the index to a datetime object
forex_data_minute.index = pd.to_datetime(forex_data_minute.index)

# Display the last five rows
print(forex_data_minute.tail())

