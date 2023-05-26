import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime
import bisect
from pytz import timezone
import sys
import os

def draw_chart(data, preview, savepath):
    labels = data['hourly']['time']
    #only show date date
    new_labels = [datetime.fromisoformat(element).strftime('%Y-%m-%dT%H:%M') for element in labels]
    rain = data['hourly']['rain']
    showers = data['hourly']['showers']
    temperature = data['hourly']['temperature_2m']

    if preview == True:
        half_length = len(labels)//2
        rain = rain[:half_length]
        showers = showers[:half_length]
        temperature = temperature[:half_length]
        new_labels = new_labels[:half_length]

    """
    df = pd.DataFrame({'Date': new_labels,
                       'Temperature': temperature,
                       'Rain': rain,
                       'Showers': showers})
    """
    fig, ax = plt.subplots(figsize=(10, 4))

    # Set the background color to black
    fig.set_facecolor('white')
    ax.set_facecolor('white')

    # Set the tick and title color to white
    ax.tick_params(colors='black')
    ax.xaxis.label.set_color('black')
    ax.yaxis.label.set_color('black')
    ax.title.set_color('black')

    #mark current time (hours) on the graph
    #bisec is not very efficient we know index is at the beginning (within first day)
    current_time = datetime.now(timezone("Asia/Tokyo")).replace(minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M')
    index = bisect.bisect_left(labels, current_time)
    if index < len(labels) and labels[index] == current_time:
        # Match found at index
        marker = [index]
    else:
        # No match found
        marker = [0]

    updated_time = datetime.now(timezone("Asia/Tokyo")).strftime('%H:%M')
    # plot data
    ax.plot(new_labels, temperature, '-D',markevery = marker, color='red', label='Temperature \n ' + "(updated:" + updated_time +")" )
    ax2 = ax.twinx()
    ax2.bar(new_labels, rain, color='blue', label='Rain')
    ax2.bar(new_labels, showers, color='green', label='Showers')
    ax2.set_ylim(0, 5)
    #https://withbrides.co.jp/lady/precipitation_amount-1mm/

    daily_time= data['daily']['time']
    daily_wmo = data['daily']['weathercode']

    wmo_dict = dict(zip(daily_time, daily_wmo))

    # Set xticks
    if preview == True:
        x_labels = [datetime.fromisoformat(label).strftime('%m-%d %a') + \
                 "\n" + "(wmo:" + str(wmo_dict[datetime.fromisoformat(label).strftime("%Y-%m-%d")]) + ")" for label in labels]
        #12時間おきにxticksを設定
        ax.set_xticks(range(0, len(x_labels), 12))
        #24時間置きにラベル文字を設定する。
        ax.set_xticklabels([x_labels[i * 12] if i%2==0 else "" for i in range(len(x_labels[::12]))])

    else: 
        x_labels = [datetime.fromisoformat(label).strftime('%m-%d') + \
                    "\n" + datetime.fromisoformat(label).strftime('%a') for label in labels]

        ax.set_xticks(range(0, len(x_labels), 24))
        ax.set_xticklabels(x_labels[::24])
    
    # set background color of xticks
    for i in range(0, len(new_labels), 24):
        counter = int(i/24)
        
        date_str = labels[i]
        date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        day_of_week = date_obj.strftime('%A')
        
        if counter % 2 == 0:
            ax.axvspan(i, i+24, facecolor='grey', alpha=0.1)
        else :
            ax.axvspan(i, i+24, facecolor='blue', alpha=0.1)

    # set labels and title
    ax.set_xlabel('Date')
    ax.set_ylabel('Temperature')
    ax2.set_ylabel('mm')
    ax.set_title('Weather Forecast (TOKYO) ' + labels[0].split('-')[0])

    # set legend
    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(savepath)

def forecast():
    url = 'https://api.open-meteo.com/v1/forecast?latitude=35.69&longitude=139.69&hourly=temperature_2m,rain,showers&daily=weathercode&forecast_days=14&timezone=Asia%2FTokyo'
    response = requests.get(url)
    data = json.loads(response.text)

    #for deploy
    savepath = './docs/_images/' 

    preview = True
    savefile = './docs/_images/forecast-short.png'
    #savefile = '../../figures/forecast-short.png'
    draw_chart(data, preview, savefile)

    preview = False
    savefile = './docs/_images/forecast.png'
    #savefile = '../../figures/forecast.png'
    draw_chart(data, preview, savefile)


def market(apikey):
   # https://github.com/antoinevulcain/Financial-Modeling-Prep-API
   #Financial Modeling Prep API is Regulated by: Creative Commons Attribution-NonCommercial 4.0 International Public License
    #https://tech-aru.com/githubactions_secret_use/

    """
    symbol = 'amzn'
    url = f"https://financialmodelingprep.com/api/v3/fx?apikey={apikey}"
    response = requests.get(url)
    data = response.json()

    print(data)
    #strPrice = '{:,.2f}'.format(data['price'])
    #print(data['symbol'] + ": $" + strPrice)
    #print(data['updated_at'] + '(UTC)')
    #print('Stock Price: $' + strPrice + ' at ' + data['updated_at'] + '(UTC)')
    """

    data = [
    {
        "ticker": "EUR/USD",
        "bid": "1.08498",
        "ask": "1.08498",
        "open": "1.09158",
        "low": "1.08480",
        "high": "1.09356",
        "changes": -0.006599999999999939,
        "date": "2023-05-14 10:26:27"
    },
    {
        "ticker": "USD/JPY",
        "bid": "135.738",
        "ask": "135.738",
        "open": "134.498",
        "low": "134.404",
        "high": "135.754",
        "changes": 1.240000000000009,
        "date": "2023-05-14 10:26:27"
    }
    ]

    new_data = {}
    for key in data[0].keys():
        if key=="changes":
            new_data[key] = [format(d[key], '.2f') for d in data]

        else: new_data[key] = [d[key] for d in data]

   

    #data = {'name': ['John', 'Mary', 'Peter'], 'age': [30, 25, 35], 'city': ['New York', 'Paris', 'London']}
    df = pd.DataFrame(new_data)

    # Create table plot
    fig, ax = plt.subplots(figsize=(8, 3)) # Set the figure size
    ax.axis('off') # Turn off the axis
    ax.set_title('Example Table', fontweight='bold') # Set the title
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center') # Create the table

    # Highlight the index name in blue
    #print(table[0])
    #index_cells = table[0, :]
    #index_cells.set_facecolor('#0074D9')
    #index_cells._text.set_color('w')

    # Save the plot as PNG
    plt.savefig('example_table.png', dpi=300, bbox_inches='tight')







def main():
    #forecast()
    key = ""
    #key = os.environ["ENV1"]
    market(key)



if __name__ == "__main__":
    main()