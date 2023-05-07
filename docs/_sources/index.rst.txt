.. githubpages documentation master file, created by
   sphinx-quickstart on Sat Mar 18 00:21:20 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. image:: ./figures/profile2.png 
   :align: left
   :width: 70

四季~Letter~
==============

Weather data by Open-Meteo.com<https://open-meteo.com/>

.. jupyter-execute::
  :hide-code:
  
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


(★) : Hot article


théma 
~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2
    
   ./src/theme/morningsatelite.rst
   ./src/theme/chatgpt_papers.rst
   ./src/theme/stablediffusion_papers.rst
   ./src/theme/zerotoone.rst

.. raw:: html

   <a class="show-more" href="./src/theme/index.html"> >>Show more</a>

.. toctree::
   :maxdepth: 2
   :hidden:

   ./src/theme/index.rst




mathimatiká
~~~~~~~~~~~~~
.. toctree::
   :maxdepth: 1

   ./src/mathematics/stochasticcalculus/index


michanikí
~~~~~~~~~~~~~
.. toctree::
   :maxdepth: 1
   
   ./src/kit/2020-03-13-arduino-network-lamp.rst
   ./src/effectivecsharp/index.rst
   ./src/softwareengineering/index.rst
   ./src/MLApp/index.rst


oikonomía
~~~~~~~~~~~~~
.. toctree::
   :maxdepth: 1

   ./src/securitiestradelifecycle/index
   ./src/deephedge/index.rst
   ./src/regulations/frtb.rst
   ./src/regulations/benchmarkreform.rst
   

nevroepistími
~~~~~~~~~~~~~
.. toctree::
   :maxdepth: 1

   ./src/neuroscience/index.rst

Tips
~~~~~
.. toctree::
   :maxdepth: 1

   ./src/Tips/sphinx-tips.rst
   ./src/excel/index.rst
   ./src/Tips/tennis.rst
   ./src/Tips/todo.rst


Indices and tables
~~~~~~~~~~~~~~~~~~~

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

