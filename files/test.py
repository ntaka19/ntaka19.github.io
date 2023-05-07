import requests
import json
import matplotlib.pyplot as plt

url = 'https://api.open-meteo.com/v1/forecast?latitude=35.6785&longitude=139.6823&daily=temperature_2m_max,temperature_2m_min&timezone=Asia%2FTokyo'

response = requests.get(url)
data = json.loads(response.text)

def draw_chart(data):
    labels = data['daily']['time']
    max_temperatures = data['daily']['temperature_2m_max']
    min_temperatures = data['daily']['temperature_2m_min']

    plt.plot(labels, max_temperatures, label='最高気温', color='red')
    plt.plot(labels, min_temperatures, label='最低気温', color='blue')
    plt.xlabel('日付')
    plt.ylabel('気温（℃）')
    plt.title('東京の天気予報')
    plt.legend()
    plt.show()

draw_chart(data)
