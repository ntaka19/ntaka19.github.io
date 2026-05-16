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

import json
import re
from zoneinfo import ZoneInfo

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
        self.api = os.environ.get('PPLX_API')

    def GetResponse(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api}",
            "Content-Type": "application/json"
        }
        
        url = "https://api.perplexity.ai/chat/completions"

        data = {
            "model": "sonar", 
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional financial analyst. Provide detailed, data-driven reports with citations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            "max_tokens": 3000, 
            "temperature": 0.2,
            "return_citations": True
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            # 1. Extract the main report
            assistant_reply = result['choices'][0]['message']['content']
            
            # 2. Extract and format citations (crucial for financial data)
            citations = result.get('citations', [])
            citation_text = ""
            if citations:
                citation_text = "\n\n### 📚 参照ソース (Citations):\n"
                for idx, url_link in enumerate(citations, 1):
                    citation_text += f"{idx}. [{url_link}]({url_link})\n"

            # 3. Build final output
            disclaimer = (
                "\n\n---\n**免責事項 (Disclaimer):**\n"
                "本データはAPI（FMP等）およびLLM（Perplexity/Gemini）により自動生成されたものです。 "
                "利用による損失について作成者は一切の責任を負いません。"
            )
            
            return f"{assistant_reply}{citation_text}{disclaimer}"

        except Exception as e:
            return f"Error occurred: {str(e)}"


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
        # 現在時刻の取得
        updated_time = datetime.now(ZoneInfo("Asia/Tokyo")).strftime('%Y/%m/%d %H:%M')
        perplexity = PerplexityWrapper()
        
        # 1. Perplexityへ投げる「最小限のデータ要求」プロンプト（トークン削減）
        prompt = """
        以下の各項目について、最新の動向をリサーチし、指定のJSONフォーマットでのみ回答してください。
        余計な挨拶、説明文、Markdownのコードブロック（```json など）は一切含めず、純粋なJSONオブジェクト単体を出力してください。
        
        【出力ルール】
        - "trend"（原因➔変化）: 何が原因でどう変化したかを100文字程度で簡潔に。
        - "focus"（注視点）: 今後何に注視すべきかを50文字程度で簡潔に。
        
        【フォーマット】
        {
        "dow": {"trend": "...", "focus": "..."},
        "nasdaq": {"trend": "...", "focus": "..."},
        "sp500": {"trend": "...", "focus": "..."},
        "nikkei": {"trend": "...", "focus": "..."},
        "topix": {"trend": "...", "focus": "..."},
        "usdjpy": {"trend": "...", "focus": "..."},
        "wti": {"trend": "...", "focus": "..."},
        "brent": {"trend": "...", "focus": "..."},
        "jkm": {"trend": "...", "focus": "..."},
        "ttf": {"trend": "...", "focus": "..."},
        "hh": {"trend": "...", "focus": "..."},
        "jepx": {"trend": "...", "focus": "..."},
        "copper": {"trend": "...", "focus": "..."},
        "aluminum": {"trend": "...", "focus": "..."},
        "gold": {"trend": "...", "focus": "..."},
        "silver": {"trend": "...", "focus": "..."},
        "events": [
            {"date": "MM/DD", "name": "イベント名", "reason": "注視すべき理由（1行）"},
            {"date": "MM/DD", "name": "イベント名", "reason": "注視すべき理由（1行）"},
            {"date": "MM/DD", "name": "イベント名", "reason": "注視すべき理由（1行）"}
        ]
        }
        """
        
        # 2. APIから応答を取得し、堅牢にJSONとしてパース
        raw_response = perplexity.GetResponse(prompt)
        try:
            # 万が一json などのマークダウンが含まれていた場合のトリミング
            json_str = re.search(r'\{.*\}', raw_response, re.DOTALL).group(0)
            data = json.loads(json_str)
        except Exception as e:
            print(f"JSONパースエラー。生の応答: {raw_response}")
            return

        # 3. Python側で固定する「各指標の定義・違い」入りのHTML/Markdownテンプレート（バリューチェーン順）
        template = f"""# 📈 経済・コモディティ市場サマリー（{updated_time} 時点）

        ## 🌐 1. マクロ環境（株価・為替）

        ### 🇺🇸 米国主要株価指数
        > 💡 **指標の違いと定義：**
        > * **NYダウ:** 選び抜かれた主要優良企業30社の「株価平均」。値がさ株（高額株）の影響を受けやすい。
        > * **S&P 500:** 主要500社の「時価総額加重平均」。米国市場全体の調子を最も正確に反映し、プロの基準となる。
        > * **NASDAQ:** IT・ハイテク・新興企業中心の約3,000銘柄の指数。金利動向に非常に敏感。

        * **NYダウ**
        * **【原因 ➔ 変化】** {data['dow']['trend']}
        * **【今後の注視点】** {data['dow']['focus']}
        * **S&P 500**
        * **【原因 ➔ 変化】** {data['sp500']['trend']}
        * **【今後の注視点】** {data['sp500']['focus']}
        * **NASDAQ**
        * **【原因 ➔ 変化】** {data['nasdaq']['trend']}
        * **【今後の注視点】** {data['nasdaq']['focus']}

        ### 🇯🇵 日本主要株価指数
        > 💡 **指標の違いと定義：**
        > * **日経平均:** 東証主要225銘柄の「株価平均」。一部の特定の超大型株（ユニクロなど）の上下に振り回されがち。
        > * **TOPIX:** 東証プライム全銘柄の「時価総額加重平均」。日本経済・市場全体の「時流（ウエイト）」を丸ごと反映する。

        * **日経平均株価**
        * **【原因 ➔ 変化】** {data['nikkei']['trend']}
        * **【今後の注視点】** {data['nikkei']['focus']}
        * **TOPIX**
        * **【原因 ➔ 変化】** {data['topix']['trend']}
        * **【今後の注視点】** {data['topix']['focus']}

        ### 💵 為替動向
        * **ドル円（USD/JPY）**
        * **【原因 ➔ 変化】** {data['usdjpy']['trend']}
        * **【今後の注視点】** {data['usdjpy']['focus']}

        ---

        ## ⚡ 2. エネルギー・バリューチェーン（上流 ➔ 下流）

        ### 🛢️ 原油市場（上流：大元の原料）
        > 💡 **指標の定義：**
        > * **WTI:** 米国テキサス産の軽質原油。北米市場の基準。
        > * **ブレント（Brent）:** 英国北海産の原油。欧州や中東、世界の原油価格の主要な国際ベンチマーク。

        * **WTI原油**
        * **【原因 ➔ 変化】** {data['wti']['trend']}
        * **【今後の注視点】** {data['wti']['focus']}
        * **ブレント原油**
        * **【原因 ➔ 変化】** {data['brent']['trend']}
        * **【今後の注視点】** {data['brent']['focus']}

        ### 💨 天然ガス・LNG市場（中流：発電の主燃料）
        > 💡 **指標の定義：**
        > * **HH（Henry Hub）:** 米国ルイジアナ州の拠点を基準とする、北米の天然ガス価格指標。シェールガス増産の影響を受けやすい。
        > * **TTF:** オランダを拠点とする、欧州の主要な天然ガス市場指標。パイプラインや地政学リスクで激しく変動する。
        > * **JKM（Japan Korea Marker）:** 日本・韓国を中心とする、アジア向けの液化天然ガス（LNG）スポット価格指標。

        * **HH（北米ガス）**
        * **【原因 ➔ 変化】** {data['hh']['trend']}
        * **【今後の注視点】** {data['hh']['focus']}
        * **TTF（欧州ガス）**
        * **【原因 ➔ 変化】** {data['ttf']['trend']}
        * ** {data['ttf']['focus']}
        * **JKM（アジアLNG）**
        * **【原因 ➔ 変化】** {data['jkm']['trend']}
        * **【今後の注視点】** {data['jkm']['focus']}

        ### 🔌 電力市場（下流：最終エネルギー消費）
        > 💡 **指標の定義：**
        > * **JEPX:** 日本卸電力取引所。日本の電力スポット価格の基準（燃料費や再エネ供給量、気温に直結）。

        * **JEPX（日本電力市場・海外主要動向）**
        * **【原因 ➔ 変化】** {data['jepx']['trend']}
        * **【今後の注視点】** {data['jepx']['focus']}

        ---

        ## 🏗️ 3. 産業素材・コモディティ

        ### 🪵 LME非鉄金属（景気の先行指標）
        > 💡 **指標の定義：**
        > * **LME:** ロンドン金属取引所。世界最大の非鉄金属取引所。特に「銅」は電気自動車やインフラに必須で、世界景気の先行指標（ドクター・コッパー）と呼ばれる。

        * **銅（Copper）**
        * **【原因 ➔ 変化】** {data['copper']['trend']}
        * **【今後の注視点】** {data['copper']['focus']}
        * **アルミニウム（Aluminum）**
        * **【原因 ➔ 変化】** {data['aluminum']['trend']}
        * **【今後の注視点】** {data['aluminum']['focus']}

        ### 👑 貴金属（安全資産・インフレヘッジ）
        * **金（Gold）**
        * **【原因 ➔ 変化】** {data['gold']['trend']}
        * **【今後の注視点】** {data['gold']['focus']}
        * **銀（Silver）**
        * **【原因 ➔ 変化】** {data['silver']['trend']}
        * **【今後の注視点】** {data['silver']['focus']}

        ---

        ## 📅 4. 今後の最重要経済イベント（厳選）
        """
        # イベント部分を動的に追加
        for ev in data['events']:
            template += f"- **[{ev['date']}] {ev['name']}**\n  - *注視理由:* {ev['reason']}\n"

        # 4. HTMLに変換して保存
        html_output = markdown.markdown(template, extensions=['extra'])
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
