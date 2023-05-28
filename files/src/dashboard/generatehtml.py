import django
from django.conf import settings
from django.template import Template, Context
import json
import requests
from abc import ABC, ABCMeta, abstractmethod
import os
import sys

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
                    "date1": formatted_data["date"][0]
                    })

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

        print("rawdata")
        print(rawdata)

        return rawdata


def main():

    #market_extractor = JsonExtractor()
    market_extractor = APIExtractor()
    #rawdata = market_extractor.Extract(os.environ['ENV1'])
    #print(os.environ['ENV1'][0])
    rawdata = market_extractor.Extract(sys.argv[1])

    formatted_data = market_extractor.Format(rawdata)
    
    generator = Generator()
    generator.generate_html(formatted_data)


if __name__ == '__main__':
    main()
