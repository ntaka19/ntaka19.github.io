
from pandas_datareader import data  as pdr #修正
from datetime import date
from dateutil.relativedelta import relativedelta
import yfinance as yf #追加
yf.pdr_override() #追加

today = date.today()
ago = today - relativedelta(years=10)
data = pdr.get_data_yahoo('^N225',  ago, today) #修正
print(data)

