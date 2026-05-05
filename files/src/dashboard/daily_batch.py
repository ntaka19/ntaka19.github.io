from openai import OpenAI
from google import genai
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
import markdown

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
            model="gpt-4o-mini",
        )

        return chat_completion.choices[0].message.content

class HFWrapper:
    def __init__(self):
        self.api = os.environ['HF']

    def GetResponse(self, prompt):
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=self.api,
        )

        chat_completion = client.chat.completions.create(
            model="openai/gpt-oss-20b:fireworks-ai",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        return chat_completion.choices[0].message.content


class PerplexityWrapper:
    def __init__(self):
        self.api = os.environ['PPLX_API']

    def GetResponse(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api}",
            "Content-Type": "application/json"
        }
        # API endpoint
        url = "https://api.perplexity.ai/chat/completions"

        # The data payload
        data = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": "Be precise and concise."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))

        output = ""

        if response.status_code == 200:
            # Parse the JSON response
            result = response.json()

            # Extract the assistant's reply
            assistant_reply = result['choices'][0]['message']['content']
            #output += "Assistant's reply:\n"
            output += assistant_reply + "\n"

            # Extract citations
            citations = result.get('citations', [])
            if citations:
                output += "\n\n**Citations:**\n\n"
                for idx, citation in enumerate(citations, 1):
                    output += f"{idx}. [{citation}]({citation})\n\n"
            else:
                output += "\nNo citations found in the response.\n"
        else:
            output += f"Error: {response.status_code}\n"
            output += response.text + "\n"

        #Disclaimer
        output += "\n\n**Disclaimer:**\n\n"
        output += "The data presented herein is sourced through an API (FMP). The information provided is automatically generated from LLM (Gemini API). Accordingly, the creators expressly disclaim any liability for losses or damages incurred as a result of using this information."
        return output




class GeminiWrapper:
    def __init__(self):
        self.client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

    def GetResponse(self, prompt):
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text


class D001_WeatherForecast_Daily:
    
    def forecast_text_html(self):
        url = 'https://api.open-meteo.com/v1/forecast?latitude=35.6604&longitude=139.7451&hourly=temperature_2m,rain,showers,weathercode&forecast_days=1&daily=sunshine_duration,uv_index_max&timezone=Asia%2FTokyo'
        response = requests.get(url)
        data = json.loads(response.text)
        
        today = datetime.fromisoformat(data['hourly']['time'][0]).strftime('%m-%d %a')
        updated_time = datetime.now(timezone("Asia/Tokyo"))

        chatgpt = GeminiWrapper()
        prompt = "天気予報士のように、この日の天気を簡潔に教えて。加えて、UV indexと日照時間の情報をもとに日傘が必要か教えて。：  {first}".format(first=json.dumps(data))  

        forecast_text = f"# 今日の天気 ({updated_time.strftime('%m-%d %a')})\n\n"
        forecast_text += chatgpt.GetResponse(prompt)

        # Convert Markdown to HTML
        html_output = markdown.markdown(forecast_text)
        with open("./docs/src/dashboard/forecast_text.html", "w", encoding="utf-8") as file:
            file.write(html_output)

        ##html生成 あとで別のモジュールにしておく。
        """
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
        """


class D002_FX_Daily:

    def __init__(self):
        self.market_extractor = APIExtractor(os.environ['FMP_API'])
        self.updated_time = datetime.now(timezone("Asia/Tokyo")).strftime('%m/%d %H:%M')
        try:
            self.data_json = self.market_extractor.Extract_Two_Weeks()
        except Exception as e:
            print(f"FMP API skipped: {e}")
            self.data_json = None


    def draw_candle_chart(self, savepath):
        if self.data_json is None:
            print("draw_candle_chart skipped: no FMP data")
            return
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
        updated_time = datetime.now(timezone("Asia/Tokyo")).strftime('%Y/%m/%d %H:%M')
        perplexity = GeminiWrapper()
        
        prompt = f"""
        # 経済ニュースサマリー：商品市場の動向と展望

        ## 📅 最新の市場動向（{updated_time}時点）
        - 世界経済に関する主要なニュースを簡潔にまとめて。
        - 顕著な株価の増減（例：NYダウ、NASDAQ、日経平均）とその背景を説明して。
        - USD/JPYの現在の動向、変動要因、今後の見通しを分析して。

        ## ⛏️ 商品市場の動向
        - 以下の各商品について、直近の価格動向、主要な変動要因、今後の見通しを詳細に分析してください。

        ### 1. 原油市場
        - **価格動向:** 直近1週間のWTIとブレント原油の価格推移と、直近1ヶ月のトレンドを分析。
        - **変動要因:** OPEC+の減産方針、地政学的リスク（中東情勢など）、米国の在庫統計、世界経済の需要見通しに焦点を当てて。

        ### 2. LNG（液化天然ガス）市場
        - **価格動向:** アジア（JKM）と欧州（TTF）の価格動向を比較分析。
        - **変動要因:** 欧州の備蓄状況、主要輸出国の生産動向（例：米国の輸出施設）、冬季の需要予測に焦点を当てて。

        ### 3. 電力市場
        - **価格動向:** 日本（JEPX）、欧州、北米の主要な電力市場価格の動向。
        - **変動要因:** 再生可能エネルギーの供給量、気温変動による需要の変化、発電燃料（LNG、石炭）の価格動向に焦点を当てて。

        ### 4. 貴金属・LME（非鉄金属）市場
        - **貴金属（金・銀）:**
            - **価格動向:** 金と銀の価格推移（ドル建てスポット価格）。
            - **変動要因:** 金融政策（利上げ・利下げ観測）、ドル相場、安全資産としての需要動向に焦点を当てて。
        - **LME（銅・アルミなど）:**
            - **価格動向:** 主要な非鉄金属（銅、アルミ）の価格推移。
            - **変動要因:** 中国の需要動向、世界的な製造業の景況感、主要生産国の供給状況に焦点を当てて。

        ## 🗓️ 今後の重要な経済イベント
        - 今後1週間から1ヶ月の間に予定されている重要な経済イベント（例：FOMC、ECB理事会、各国の雇用統計など）をリストアップしてください。

        **生成時の注意点:**
        - 各項目の分析は、複数の要因を網羅的に記載し、深掘りした内容にしてください。
        - 情報源の信頼性を確保し、正確なデータに基づいて記述してください。
        - 専門用語には簡単な補足を加えてください。
        """
        
        market_summary_text = perplexity.GetResponse(prompt)
        print(market_summary_text)

        # Convert Markdown to HTML
        html_output = markdown.markdown(market_summary_text)
        with open("./docs/src/dashboard/marketinfo.html", "w", encoding="utf-8") as file:
            file.write(html_output)

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
