Docker
=========

ここではsphinxの環境構築をテーマにDockerの学習記録を記載する。

目的は

* githubでソースの管理できること
* 必要な環境はDocker imageで管理できること。(sphinx autobuildなども使いたい)

→ したがって、ファイルソースは永続性を持たせて環境と分離することに。


参考：

* https://qiita.com/ntatsuya/items/ef8f48d5e482d4b0f100
* Containers from scratch (https://www.youtube.com/watch?v=8fi7uSYlOdc)


Dockerfile
~~~~~~~~~~~

sphinx環境をセットアップするためのイメージはDockerfileで記述する。

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

  #必要なpythonパッケージをpipでインストール
  #RUN pip3 install --upgrade pip && pip3 install --no-cache-dir jupyterlab
  RUN apt-get update
  RUN apt install -y graphviz

  #サイズ削減のため不要なものは削除
  RUN apt-get autoremove -y

  COPY ./requirements.txt /root/
  #requirements.txtなら以下のように
  RUN pip3 install -r /root/requirements.txt

  # docker run後の最初のディレクトリ
  WORKDIR /home/files
  
  # なぜかmakeが動かない。bind mountする前に実行されるから?
  # RUN make html



* apt installをするときにTimezone 設定をしろと言われてフリーズしてしまう問題。(https://northshorequantum.com/archives/dockerbuild_tz_hang.html)
  以下を設定することで解消

  ::
    
    ENV TZ=Asia/Tokyo
    RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > 



* 特定のpythonのバージョンを指定して持ってきたい場合...
  https://qiita.com/ntatsuya/items/ef8f48d5e482d4b0f100



イメージの作成・コンテナの起動
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Docker build (Dockerfileからイメージの作成)

    ::
     
      docker build . -t イメージ名
        
    * Dockerfileは今のディレクトリにある想定。
    * Docker buildはimageからコンテナを作成する。すでにimageをビルドしたことがあり、その後にDockerfileで追記したとして、同じimageを指定してビルドした場合、差分からビルドしてくれる模様。(頭からのビルドには基本的にはならない。頭からのビルドだとpython3の導入など含み10分以上かかる場合もある)  


#. Docker run (= docker create + start) (イメージからコンテナの作成と起動)

    ::
    
      docker run -p 8000:8000 -it --name コンテナ名 --mount type=bind,source="$(pwd)",target=/home イメージ名

    
    * --mountはbind mountを行なっている。volumeとの違いは後述。sourceはホスト側のディレクトリ。

    * -p: ポートはexposeしておく必要がある。コンテナ内の8000ポートとホストの8000ポートを一致させる。左側がホストのポート。

      * これをしないとsphinx-autobuildで建てられたサーバーにホスト側のブラウザからアクセスできなくなる。
      * また、sphinx-autobuild側の設定でも対応するポートを指定しておく必要がある。(--host --port設定).
        sphinxのMakefileに以下を記述。

      ::
        
        %: Makefile
        sphinx-autobuild -b $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) --host 0.0.0.0 --port 8000


#. コンテナを止める。ctrl-D


#. (すでに作られている）コンテナの起動

    ::
       
      docker start -i コンテナ名
    
    * iを入れることでコンテナの中でターミナルから操作が可能になる。
    * -i (interactive) と-a (attach)の違いは?

    * https://qiita.com/kooohei/items/f0352f408056861a8f74


Docker Composeとは
~~~~~~~~~~~~~~~~~~

  
* そもそもDocker engineの一部ではなくpython製のツール。



Docker Composeで何ができるか？

* Wordpress + SQL の二種類のコンテナを用意して実行することができる。
* もしかしたら、FTP/SFTPなどを複数のコンテナを用意して試せるかもしれない。


基本的な文法：

::

  version: "Docker composeのバージョン値?"
  services:
  コンテナ名:
    build: Dockerfileのパス 
    ports:
      - "ホスト側のポート:コンテナのポート"
  コンテナ名:
    image: "イメージ名"
    ports:
      - "ホスト側のポート:コンテナのポート"



今回作成したdocker-compose.yml：

::

  version: "3"
  services:
  container3:
    build: .
    ports:
      - "8000:8000"
    image: "image4"
    stdin_open: true # docker run -i
    tty: true        # docker run -t
    command: /bin/bash
    volumes:
      - type: bind
        source: .
        target: "/home"

実行方法：

::

  docker compose up -d


この後に、中にexecできる。

::

  docker-compose exec container3 bash


Requirements.txtを更新したいとき
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

イメージを再度作成する。

::
     
      docker build . -t イメージ名

docker composeし直してコンテナを作る。

::

  docker compose up -d


Kubernetes
~~~~~~~~~~~~




