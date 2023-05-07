#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import json
import matplotlib.pyplot as plt

url = 'https://api.open-meteo.com/v1/forecast?latitude=35.6785&longitude=139.6823&daily=temperature_2m_max,temperature_2m_min&timezone=Asia%2FTokyo'

response = requests.get(url)
data = json.loads(response.text)

plt.rcParams['figure.figsize'] = [6, 3]

def draw_chart(data):
    labels = data['daily']['time']

    new_labels = ['-'.join(element.split("-")[1:])  for element in labels]

    max_temperatures = data['daily']['temperature_2m_max']
    min_temperatures = data['daily']['temperature_2m_min']

    plt.plot(new_labels, max_temperatures, label='Max', color='red')
    plt.plot(new_labels, min_temperatures, label='Min', color='blue')
    plt.xlabel('Date')
    plt.ylabel('Temperature')
    plt.title('Weather Forecast(TOKYO) ' + labels[0].split('-')[0] )
    plt.legend()
    plt.show()

draw_chart(data)

