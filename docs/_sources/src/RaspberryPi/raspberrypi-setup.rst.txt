Raspbery Piと周辺機器(★)
=============================

Waveshareの透明モニターが近未来感があっていい感じ。
(https://www.waveshare.com/1.51inch-transparent-oled.htm)


今日の夕食を提案してくれる時計を作ってみた。朝にRaspberryPiを起動すると、夜までに食材を買いに行ける。
実際にその通りの食事をしなければならないというわけではないが、少なくとも何かの料理を連想するきっかけにはなる。

今後は画像をドット絵のような形で表現してみたい。


.. figure:: monitor_clock.mp4
   :align: center
   :width: 320px
   :height: 480px
   :name: figure


githubからコードをcloneする。既存のコードを改善することもできる。
実行するコードは以下の通り、

::

   git clone https://github.com/ggml-org/llama.cpp
   cd llama.cpp

   pip install -r requirements.txt


次にモデルをクローンしてセットアップする。


