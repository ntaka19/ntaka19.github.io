
Local LLM and Raspbery Pi(★)
=============================

Raspberry Pi 5でLocal LLMを動かしてみたのでその記録。
クラウドに接続せずにMacならまだしも、Raspberry Piで動かせるのは画期的だ。

今回使用したモデルは "DeepSeek: R1 Distill Qwen 1.5B"

昨今話題のDeep Seekが開発したモデル。Qwen 2.5 Math 1.5Bをベースに、DeepSeek-R1の出力を用いて蒸留（distillation）された。
15億パラメータでありながら、数学的推論タスクにおいてGPT-4oやClaude 3.5といった大規模モデルを上回る性能を示しているらしい。
https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B


基本的にはollamaで入れている。(raspberrypiだとsudo pipがうまくいかず、venvなどで仮想環境を作って実施した方がよい。)

::

   git clone https://github.com/ggml-org/llama.cpp
   cd llama.cpp

   pip install -r requirements.txt


次にモデルをクローンしてセットアップする。

::

   #Git LFSのインストール
   sudo apt install git-lfs

   #Git LFSの初期化
   git lfs install

   #モデルのクローン
   git clone https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B

   #GGUFファイル形式にする。
   python convert_hf_to_gguf.py --outfile DeepSeek-R1-Distill-Qwen-1.5B.gguf --outtype f16 ./DeepSeek-R1-Distill-Qwen-1.5B


最後にモデルをollamaに登録して実行する。

::

   #Modelfileを作成し、以下の内容を記述
   FROM deepseek-r1
   PARAMETER gguf_model DeepSeek-R1-Distill-Qwen-1.5B.gguf

   #モデルをollamaに追加
   ollama create deepseek-r1-local -f ./Modelfile

   #インタラクティブモード
   ollama run deepseek-r1-local



実際に試してみると、処理速度は遅いが、内省しつつ思考を深めていくプロセスが見える。
ところどころ隙が見えており、可愛く見えてくる。


質問はHow to find e = mc^2? 
だが、なぜかそれを補足してから、推論が始まる。

.. figure:: emc2part1.mp4
   :align: center
   :width: 320px
   :height: 480px
   :name: figure


かなり思考が長い。5分後くらいの状況：

.. figure:: emc2part2.mp4
   :align: center
   :width: 320px
   :height: 480px
   :name: figure

最終的にはthinkが終わり、答えを出している。

.. figure:: emc2result.jpg
   :align: center
   :width: 320px
   :height: 480px
   :name: figure


しばらく処理させていると、cpuが80度超えることがあったため(vcgencmd measure_tempでわかる)、その場しのぎとして保冷剤を使ってみた。（もちろん冷却ファンも内部でつけているが不十分。）

一定程度効果があることが分かり、つけない場合と比べて温度の立ち上がりは小さくなった。

.. figure:: raspberrypi_cooling.jpg
   :align: center
   :width: 320px
   :name: figure


