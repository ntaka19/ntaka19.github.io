SOA and Microservice
==============================

参考文献：
https://aws.amazon.com/jp/what-is/service-oriented-architecture/#:~:text=%E3%82%B5%E3%83%BC%E3%83%93%E3%82%B9%E6%8C%87%E5%90%91%E3%82%A2%E3%83%BC%E3%82%AD%E3%83%86%E3%82%AF%E3%83%81%E3%83%A3%20(SOA)%20%E3%81%AF,%E3%81%99%E3%82%8B%E3%81%93%E3%81%A8%E3%82%82%E3%81%A7%E3%81%8D%E3%81%BE%E3%81%99%E3%80%82


Service Oriented Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

メリット

* 
* 相互運用性＝各サービスが異なる言語を利用していても動く
* 抽象化=SOA のクライアントまたはサービスユーザーは、サービスのコードロジックや実装の詳細を知る必要はない。ブラックボックス。


通信プロトコル

* Simple Object Access Protocol (SOAP)
* RESTful HTTP
* Apache Thrift
* Apache ActiveMQ
* Java Message Service (JMS)
* IBM MQ


コンシューマー：情報をリクエストし、入力データをサービスに送信する。

Eg. アプリケーションが承認サービスを利用する場合、そのアプリケーションはサービスにユーザー名とパスワードを提供します。
このサービスは、それらのユーザー名とパスワードを検証し、適切なレスポンスを返します。



Microservice
~~~~~~~~~~~~~

* マイクロサービスアーキテクチャはSOA アーキテクチャスタイルが進化したもの。
