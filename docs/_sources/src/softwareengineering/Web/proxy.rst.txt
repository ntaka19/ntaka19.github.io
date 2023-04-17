プロキシ・リバースプロキシサーバー
===========================================

* https://qiita.com/yamionp/items/8f8d52d6b41bf9d4d16d
* https://eset-info.canon-its.jp/malware_info/special/detail/201021.html


だれを守っているかの視点がよいかも。



proxy
~~~~~~~

社内LAN ⇆ (forward) proxy ⇆ Internet ⇆ Web server



#. 社内LANのPCからproxyサーバーへリクエスト
#. プロキシサーバーが外部のwebへリクエストを転送
#. web serverからproxyへレスポンス

* Cache
* ユーザー認証
* filtering
* 匿名性


Reverse proxy
~~~~~~~~~~~~~~

Client ⇆ Internet ⇆ Firewall ⇆ Reverse proxy ⇆ 内部ネットワーク ⇆ web server

#. Client からinternetでリクエストを送信
#. リバースプロキシがwebサーバーへリクエストを転送する
#. Webサーバーはリバースプロキシにレスポンスを返す。


* 負荷分散
* Cache
* SSL高速化: web serverではなく、ここで暗号化・複合化を行う。
