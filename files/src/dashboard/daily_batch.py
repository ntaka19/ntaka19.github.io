from openai import OpenAI
import json
import os
import sys
import requests
import django
from django.conf import settings
from django.template import Template, Context
from datetime import datetime
from pytz import timezone

import mplfinance as mpf
from mplfinance.original_flavor import candlestick_ohlc
import pandas as pd
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

from market_extractor import APIExtractor

class ChatGPTWrapper:
    
    def __init__(self):
        self.api = os.environ['OPENAI_API']

    def GetResponse(self, prompt):
        client = OpenAI(
            api_key = self.api
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-3.5-turbo",
        )

        return chat_completion.choices[0].message.content
        

class D001_WeatherForecast_Daily:
    
    def forecast_text_html(self):
        url = 'https://api.open-meteo.com/v1/forecast?latitude=35.69&longitude=139.69&hourly=temperature_2m,rain,showers,weathercode&forecast_days=1&timezone=Asia%2FTokyo'
        response = requests.get(url)
        data = json.loads(response.text)
        
        today = datetime.fromisoformat(data['hourly']['time'][0]).strftime('%m-%d %a')
        updated_time = datetime.now(timezone("Asia/Tokyo")).strftime('%m/%d %H:%M')

        chatgpt = ChatGPTWrapper()
        prompt = "この日の天気を簡潔にキャスターのように予報をして：  {first}".format(first=json.dumps(data))                                
        forecast_text = chatgpt.GetResponse(prompt)

        ##html生成 あとで別のモジュールにしておく。
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

        with open('./files/src/dashboard/template_todayweather.html', 'r') as template_file:
            t = Template(template_file.read())
            c = Context({"today" : today,
                        "forecast_text": forecast_text,
                        "updated_time": updated_time})    
            
            rendered_html = t.render(c)

            # Save the rendered HTML as an HTML file
            with open("./docs/src/dashboard/forecast_text.html", "w") as file:
                file.write(rendered_html)


class D002_FX_Daily:

    def __init__(self):
        #self.market_extractor = APIExtractor(os.environ['FMP_API'])
        self.market_extractor = APIExtractor(sys.argv[1])
        self.data_json = self.market_extractor.Extract_Two_Weeks()
        self.updated_time = datetime.now(timezone("Asia/Tokyo")).strftime('%m/%d %H:%M')


    def draw_candle_chart(self, savepath):
        # Convert JSON to DataFrame
        df = pd.DataFrame(self.data_json)

        # Convert 'date' column to datetime type
        df['date'] = pd.to_datetime(df['date'])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        df_candle = df[['open', 'high', 'low', 'close']]


        fig, ax = plt.subplots(figsize=(10, 4))
        df_candle['date_num'] = mdates.date2num(df_candle.index)
        ohlc = df_candle[['date_num', 'open', 'high', 'low', 'close']].values
        candlestick_ohlc(ax, ohlc, width=0.6, colorup='g', colordown='r')
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))

        # Ensure that every data point has an x-tick
        ax.xaxis.set_major_locator(ticker.FixedLocator(df_candle['date_num']))

        # Setting the y-axis label to the right
        ax.yaxis.set_label_position('right')  # Sets the y-axis label to the right
        ax.yaxis.tick_right()  # Moves the y-axis ticks to the right

        # Annotate high and low values, ensure they are within the spine and border
        for i in range(len(ohlc)):
            # Get the y-axis limit
            y_low, y_high = ax.get_ylim()
            
            # Set offset within bounds
            high_offset = 0.5 if (ohlc[i][2] + 0.5) < y_high else -0.5  # If adding the offset puts the text outside the plot, flip the offset
            low_offset = -0.5 if (ohlc[i][3] - 0.5) > y_low else 0.5  # If subtracting the offset puts the text outside the plot, flip the offset
            # Annotate High and Low
            ax.annotate(f"{ohlc[i][2]}", (ohlc[i][0], ohlc[i][2]), textcoords="offset points", xytext=(0,high_offset), ha='center', color='white', fontsize=8)
            ax.annotate(f"{ohlc[i][3]}", (ohlc[i][0], ohlc[i][3]), textcoords="offset points", xytext=(0,low_offset), ha='center', color='white', fontsize=8)
            ax.annotate(f"{ohlc[i][1]}", (ohlc[i][0], ohlc[i][1]), textcoords="offset points", xytext=(0,high_offset), ha='center', color='white', fontsize=8)
            ax.annotate(f"{ohlc[i][4]}", (ohlc[i][0], ohlc[i][4]), textcoords="offset points", xytext=(0,low_offset), ha='center', color='white', fontsize=8)

        ax.set_title('USD/JPY Daily(timezone EST (*refer to API doc)) ', color='white')
        ax.legend(title='Updated:'+ self.updated_time, loc='upper left')
        ax.patch.set_facecolor('black')
        fig.patch.set_facecolor('black')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white') 
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')

        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(savepath)


    def market_summary_html(self):
        chatgpt = ChatGPTWrapper()
        prompt = "まるで証券アナリストのように、次の為替の状況を簡潔にまとめよ。断定はしてはならない。：  {first}".format(first=json.dumps(self.json_data))                                
        market_summary_text = chatgpt.GetResponse(prompt)

        #market_summary_text = "As a securities analyst, this pattern suggests positive momentum, although the fixed price on \
        #    the last day would require further investigation to understand the underlying cause—be it technical errors... "
        
        ##html生成 あとで別のモジュールにしておく。
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

        with open('./files/src/dashboard/template_market.html', 'r') as template_file:
            t = Template(template_file.read())
            c = Context({"market_summary_text": market_summary_text,
                        "updated_time": self.updated_time})    
            
            rendered_html = t.render(c)

            # Save the rendered HTML as an HTML file
            with open("./docs/src/dashboard/marketinfo.html", "w") as file:
                file.write(rendered_html)

def main():
    print("D001")
    weatherforecast_daily = D001_WeatherForecast_Daily()
    weatherforecast_daily.forecast_text_html()

    print("D002")
    fx_daily = D002_FX_Daily()
    fx_daily.draw_candle_chart('./docs/_images/candlechartUSDJPY.png')
    fx_daily.market_summary_html()

if __name__ == "__main__":
    main()
