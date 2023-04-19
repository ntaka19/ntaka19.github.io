Docker
=========

sphinxの環境構築をDockerの学習がてら行う。

目的は

* githubでソースは管理できること
* それと同時に必要な環境はDocker imageで管理できること。

したがって、ソースは永続性を持たせることに。



参考：
* https://qiita.com/ntatsuya/items/ef8f48d5e482d4b0f100




Dockerfile
~~~~~~~~~~~

sphinx環境をセットアップするためのDockerfileは以下の通り。

::

    #ベースイメージはubuntuにしておく。alpineが軽量?
    FROM ubuntu:20.04

    # time zoneを設定
    ENV TZ=Asia/Tokyo
    RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

    # 必要そうなものをinstall
    RUN apt-get update && apt-get install -y --no-install-recommends wget build-essential libreadline-dev \ 
    libncursesw5-dev libssl-dev libsqlite3-dev libgdbm-dev libbz2-dev liblzma-dev zlib1g-dev uuid-dev libffi-dev libdb-dev

    #任意バージョンのpython install
    RUN wget --no-check-certificate https://www.python.org/ftp/python/3.9.5/Python-3.9.5.tgz \
    && tar -xf Python-3.9.5.tgz \
    && cd Python-3.9.5 \
    && ./configure --enable-optimizations\
    && make \
    && make install

    #サイズ削減のため不要なものは削除
    RUN apt-get autoremove -y

    #必要なpythonパッケージをpipでインストール
    #RUN pip3 install --upgrade pip && pip3 install --no-cache-dir jupyterlab

    RUN apt-get update
    RUN apt install -y graphviz

    # requirementsはコンテナにコピーしておく必要がある。(ホスト側は見ない) 
    COPY ./requirements.txt /root/
    
    #requirements.txtなら以下のように
    #pipなどは最後の方にしておく。apt-getでとったものに依存する可能性があるため。
    RUN pip3 install -r /root/requirements.txt


* apt installをするときにTimezone 設定をしろと言われてフリーズしてしまう問題。(https://northshorequantum.com/archives/dockerbuild_tz_hang.html)
  以下を設定することで解消

  ::
    
    ENV TZ=Asia/Tokyo
    RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > 


* Docker buildはimageからコンテナを作成する。すでにimageをビルドしたことがあり、その後にDockerfileで追記したとして、同じimageを指定してビルドした場合、差分からビルドしてくれる模様。(頭からのビルドには基本的にはならない)  


* 特定のpythonのバージョンを指定して持ってきたい場合...
  https://qiita.com/ntatsuya/items/ef8f48d5e482d4b0f100

* ポートをexposeする場合(sphinx-autobuildが使いたくなる場合)
  ホストのブラウザからアクセスするためにはポートをマッピングする必要がある。


イメージの作成・コンテナの起動
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Docker build

    ::
     
      docker build . -t image3
        

#. コンテナの起動test

    ::
    
      docker run -p 8000:8000 -it --name container2 --mount type=bind,source="$(pwd)",target=/home image3

    
    ここで--mountはbind mountを行なっている。volumeとの違いは後でのせる。sourceはホスト側のディレクトリ。

    ポートはexposeしておく必要がある。コンテナ内の8000ポートとホストの8000ポートを一致させる。

    



Docker Composeとは
~~~~~~~~~~~~~~~~~~

  

