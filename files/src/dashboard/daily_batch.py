from openai import OpenAI
from google import genai
import json
import os
import sys
import requests
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
import textwrap
import yfinance as yf

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
            "return_citations": True,
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
        self.updated_time = datetime.now(timezone("Asia/Tokyo")).strftime('%m/%d %H:%M')
        try:
            self.market_extractor = APIExtractor(os.environ['FMP_API'])
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
        perplexity = PerplexityWrapper()

        # 1. Yahoo Finance APIから正確な市場数値を一括取得
        # 主要アセットのティッカーシンボル（日経平均, ダウ, ナスダック, ドル円, WTI原油, 金, 銅）
        tickers = {
            # 1. 主要株価指数
            "日経平均": "^N225",
            "NYダウ": "^DJI",
            "ナスダック": "^IXIC",
            "S&P500": "^GSPC",
            "英FTSE100": "^FTSE",
            "独DAX": "^GDAXI",

            # 2. 為替（主要クロス円・ドルインデックス）
            "ドル円 (USD/JPY)": "JPY=X",
            "ユーロ円 (EUR/JPY)": "EURJPY=X",
            "ポンド円 (GBP/JPY)": "GBPJPY=X",
            "ユーロドル (EUR/USD)": "EURUSD=X",
            "ドルインデックス (DXY)": "DX-Y.NYB",

            # 3. エネルギー市場
            "WTI原油先物": "CL=F",
            "ブレント原油先物": "BZ=F",
            "天然ガス先物 (米HenryHub)": "NG=F",  # ※欧州TTFやJKMはyfinanceでの常時取得が難しいため、世界指標の米先物で代用

            # 4. 貴金属市場
            "NY金先物 (Gold)": "GC=F",
            "NY銀先物 (Silver)": "SI=F",
            "NYプラチナ先物": "PL=F",

            # 5. 非鉄金属市場（COMEX/CME先物：LMEの代用として世界中で参照される指標）
            "COMEX銅先物": "HG=F",
            "CMEアルミニウム先物": "ALI=F",

            # 6. 債券・金利指標（マクロ経済の最重要ファクター）
            "米国債10年物利回り": "^TNX",
            "米国債2年物利回り": "^IRX",
            "日本国債10年物利回り": "^GJGB10"  # ※データ配信状況によりエラーになる場合はスキップされます
        }

        market_data_html = "<ul>"
        for name, ticker in tickers.items():
            try:
                t = yf.Ticker(ticker)
                # 直近2日分のデータを取得して騰落率を計算
                hist = t.history(period="2d")
                
                if len(hist) >= 2:
                    close_latest = hist['Close'].iloc[-1]
                    close_prev = hist['Close'].iloc[-2]
                    change = close_latest - close_prev
                    pct_change = (change / close_prev) * 100
                    
                    # アセットごとの最適なフォーマット設定
                    if "JPY" in ticker or "EURJPY" in ticker or "GBPJPY" in ticker:
                        fmt = ".2f"  # 為替クロス円は小数点2桁（135.42など）
                    elif "EURUSD" in ticker:
                        fmt = ".4f"  # ユーロドルは小数点4桁（1.0852など）
                    elif ticker in ["^TNX", "^IRX", "^GJGB10"]:
                        fmt = ".3f"  # 金利（利回り）は小数点3桁（4.250など）
                    else:
                        fmt = ".2f"  # その他株価・コモディティは通常2桁
                        
                    sign = "+" if change >= 0 else ""
                    
                    # 金利指標の場合は単位を「%」に、その他は「騰落率%」として整形
                    if ticker in ["^TNX", "^IRX", "^GJGB10"]:
                        market_data_html += f"<li><strong>{name}:</strong> {close_latest:{fmt}}% ({sign}{change:.3f}pt)</li>"
                    else:
                        market_data_html += f"<li><strong>{name}:</strong> {close_latest:{fmt}} ({sign}{pct_change:.2f}%)</li>"
                elif len(hist) == 1:
                    # データが1日分しか取れなかった場合
                    close_latest = hist['Close'].iloc[-1]
                    market_data_html += f"<li><strong>{name}:</strong> {close_latest:.2f} (前日比データ不足)</li>"
                else:
                    market_data_html += f"<li><strong>{name}:</strong> 配信データなし</li>"
                    
            except Exception as e:
                market_data_html += f"<li><strong>{name}:</strong> データ取得エラー</li>"

        market_data_html += "</ul>"
        print(market_data_html)


        # 2. Perplexity用のプロンプト（数値の探索は免除し、背景解説に集中させる）
        prompt = f"""
        現在の日時は {updated_time} です。
        この日時より前（直近1週間以内）にWeb上に公開された最新のニュース、市場レポート、経済記事を【項目ごとに個別に検索】し、市場を動かしている背景や要因をまとめてください。
        ※具体的な現在価格や騰落率の数値については、別途システム側で取得するため、ここでは【ニュースが報じている事実、需給要因、背景の解説】に完全に集中して記述してください。

        # 役割とルール
        プロの商品市場アナリストとして、直近1週間のWebニュースから市場を動かしている【変動要因と事実】を漏らさず引っ掛けて抽出し、簡潔な箇条書きでまとめてください。

        【最重要ルール】
        ・「記事が不足」「未提示」として空欄にすることは完全に禁止します。数値ではなくニュースの「事実」ベースで必ず各項目を埋めてください。
        ・詳細すぎる背景は避け、ファクトベースで端的に記述すること。

        # 経済・商品市場ニュース解説（{updated_time} 時点）

        ## 📅 主要市場の背景ニュース
        - 【株価動向の背景】NYダウ・ナスダック・日経平均の直近の地合いを左右している主な要因。
        - 【為替動向の背景】ドル円（USD/JPY）の直近の変動要因と市場の心理。

        ## 🛢️ エネルギー市場の背景ニュース
        - **原油（WTI/ブレント）:** OPEC+の方針、地政学的リスク（中東情勢など）、在庫統計に関する最新の動き。
        - **LNG（JKM/TTF）:** アジア・欧州の需給、在庫状況、気温予測に関する最新の動き。
        - **電力（JEPX等）:** 日本のJEPX需給、気温変動、発電燃料価格の連動に関する最新の動き。

        ## ⚖️ 貴金属・非鉄市場の背景ニュース
        - **金・銀:** ドル相場や米金利動向、安全資産需要に関する最新の動き。
        - **LME（銅・アルミ）:** 中国需要や製造業景況感、取引所在庫に関する最新の動き。

        ## 🗓️ 注目イベント（今後1ヶ月）
        - 今後1ヶ月以内に予定されている重要イベント（FOMC、主要経済指標発表など）の日付と、市場が注目している争点。

        ## 📝 ひとこと整理
        - 今回のニュース検索から言える、市場全体の最大の焦点とボラティリティの主因を2〜3行で総括してください。
        """

        # 3. Perplexityから解説テキストを取得
        market_summary_text = perplexity.GetResponse(prompt)
        print(market_summary_text)

        # MarkdownをHTMLに変換
        perplexity_html = markdown.markdown(market_summary_text)

        # 4. Yahoo Financeの確定数値と、Perplexityのニュース解説をHTMLとして統合
        final_html_output = f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <title>経済・商品市場サマリー</title>
        </head>
        <body>
            <h1>📊 リアルタイム市場データ ({updated_time} 時点)</h1>
            {market_data_html}
            <hr>
            {perplexity_html}
        </body>
        </html>
        """

        # ファイルに書き出し
        with open("./docs/src/dashboard/marketinfo.html", "w", encoding="utf-8") as file:
            file.write(final_html_output)

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
