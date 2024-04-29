import requests
from abc import ABC, ABCMeta, abstractmethod
from pytz import timezone, utc
from datetime import datetime
import json
import os

from datetime import datetime, timedelta


class AbstractMarketExtractor(metaclass=ABCMeta):
    @abstractmethod
    def Extract(self):
        pass

    def Format(self, rawdata):
        formatted_data = {}
        for key in rawdata[0].keys():
            if key=="changes":
                formatted_data[key] = [format(d[key], '.2f') for d in rawdata]
            
            elif key == "date":
                formatted_data[key] = \
                    [timezone("America/New_York").localize(datetime.strptime(d[key], "%Y-%m-%d %H:%M:%S")).astimezone(timezone("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S") for d in rawdata]
                #      [ datetime.strptime(d[key], "%Y-%m-%d %H:%M:%S").replace(tzinfo=utc).astimezone(timezone("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S") for d in rawdata]
                # need localize method to incorporate summer time.
                # print("date " + ','.join(formatted_data[key]))

            else: formatted_data[key] = [d[key] for d in rawdata]
        return formatted_data
    
class JsonExtractor(AbstractMarketExtractor):
    
    def Extract(self):
        # Open the JSON file
        with open('./files/src/dashboard/sample.json') as f:
            # Load the JSON data
            rawdata = json.load(f)
        return rawdata

class APIExtractor(AbstractMarketExtractor):
    def __init__(self, apikey):
        self.apikey = apikey

    def Extract(self):
        url = f"https://financialmodelingprep.com/api/v3/fx?apikey={self.apikey}"
        response = requests.get(url)
        rawdata = response.json()

        #前営業日を取りたい。
        url = f"https://financialmodelingprep.com/api/v3/historical-price-full/USDJPY?apikey={self.apikey}"
        return rawdata
    
    #USD/JPYの日次のレートを取得する
    def Extract_Two_Weeks(self):
        today = datetime.now().date()
        two_weeks_before = today - timedelta(weeks=2)
        today_str = today.strftime("%Y-%m-%d")
        two_weeks_before_str = two_weeks_before.strftime("%Y-%m-%d")
        url = f"https://financialmodelingprep.com/api/v3/historical-chart/1day/USDJPY?from={two_weeks_before_str}&to={today_str}&apikey={self.apikey}"
        response = requests.get(url)
        data_json = response.json()
        return data_json

    
    def ExtractStockIndex(self):
        url = f"https://financialmodelingprep.com/api/v3/quote/%5EGSPC,%5EDJI,%5EIXIC?apikey={self.apikey}"
        response = requests.get(url)
        rawdata = response.json()
        return rawdata
    
