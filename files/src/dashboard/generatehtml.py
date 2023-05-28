import django
from django.conf import settings
from django.template import Template, Context
import json
import requests
from abc import ABC, ABCMeta, abstractmethod
import os
import sys
from pytz import timezone, utc
from datetime import datetime

class Generator:
    def __init__(self):
        settings.configure(
            DEBUG=True,
            TEMPLATES=[
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'APP_DIRS': True,
                },
            ]
        )
        django.setup()
    

    def generate_html(self, formatted_data):
        # Load the template from file
        with open('./files/src/dashboard/template.html', 'r') as template_file:
            t = Template(template_file.read())

        c = Context({"ticker1": formatted_data["ticker"][0],
                    "bid1": formatted_data["bid"][0],
                    "ask1": formatted_data["ask"][0],
                    "open1": formatted_data["open"][0],
                    "low1": formatted_data["low"][0],
                    "high1": formatted_data["high"][0],
                    "date1": formatted_data["date"][0],
                    })
        """
        "Symbol1": stock_index_data["Symbol"][0],
                "Name1" : stock_index_data["Name"][0],
                "Price1" : stock_index_data["Name"][0],
                "ChangeP1" : stock_index_data["ChangeP"][0],
                "Change1" : stock_index_data["Change"][0],
                "DayLow1" : stock_index_data["DayLow"][0],
                "DayHigh1" : stock_index_data["DayHigh"][0],
                "YearHigh1" : stock_index_data["YearHigh"][0],
                "YearLow1" : stock_index_data["YearLow"][0],
                "Volume1" : stock_index_data["Volume"][0],
                "AverageVolume1" : stock_index_data["AverageVolume"][0],
                "Exchange1" : stock_index_data["Exchange"][0],
                "Open1" : stock_index_data["Open"][0],
                "PreviousClose1" : stock_index_data["PreviousClose"][0],
        """

        rendered_html = t.render(c)

        # Save the rendered HTML as an HTML file
        with open("./docs/src/dashboard/marketinfo.html", "w") as file:
            file.write(rendered_html)


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

    def Extract(self, apikey):
        url = f"https://financialmodelingprep.com/api/v3/fx?apikey={apikey}"
        response = requests.get(url)
        rawdata = response.json()

        return rawdata
    
    def ExtractStockIndex(self, apikey):
        url = f"https://financialmodelingprep.com/api/v3/quote/%5EGSPC,%5EDJI,%5EIXIC?apikey={apikey}"
        response = requests.get(url)
        rawdata = response.json()
        return rawdata



def main():

    #market_extractor = JsonExtractor()
    market_extractor = APIExtractor()

    #fx data
    rawdata = market_extractor.Extract(os.environ['TEST'])
    #rawdata = market_extractor.Extract(sys.argv[1]) #For test
    rawdata = [item for item in rawdata if item["ticker"] == "USD/JPY"]
    formatted_data = market_extractor.Format(rawdata)

    #stock index data
    #stock_index_data = market_extractor.ExtractStockIndex(os.environ['TEST'])
    #stock_index_data = market_extractor.ExtractStockIndex(sys.argv[1])
 
    generator = Generator()
    generator.generate_html(formatted_data)


if __name__ == '__main__':
    main()
