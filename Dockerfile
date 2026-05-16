# QuantLibの互換性と最新AI対応を両立するため、Python 3.10 を採用
FROM python:3.10-slim

# タイムゾーンの設定
ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# システムパッケージのインストール
# ※ OSの仕様（trixieリポジトリ）に合わせて Java 21 を指定
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    graphviz \
    openjdk-21-jre-headless \
    wget \
    && rm -rf /var/lib/apt/lists/*

# pip, setuptools, wheel を最新にアップデート
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# PlantUML の配置
COPY ./plantuml-1.2023.9.jar /root/
RUN chmod +r /root/plantuml-1.2023.9.jar

# Pythonパッケージのインストール
COPY ./requirements.txt /root/
RUN pip install --no-cache-dir -r /root/requirements.txt

# ★ Jupyter用のpython3カーネルを明示的に登録 (This fixes the Sphinx error)
RUN python -m ipykernel install --name python3 --user

# 作業ディレクトリの設定
WORKDIR /home/files
