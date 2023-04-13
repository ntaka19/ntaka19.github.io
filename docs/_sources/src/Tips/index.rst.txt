Tips
=====




#. Sphinx directives

   https://www.sphinx-doc.org/ja/master/usage/restructuredtext/directives.html

#. Pandocコマンド

    .. code-block:: bash
       :linenos:
       :caption: Markdown to Restructured Text (RST)

       pandoc -f markdown -t rst -o README.rst README.md

    .. code-block:: bash
       :linenos:
       :caption: tex to Restructured Text (RST)

       pandoc README.tex -o README.rst


#. コンテナを作成して、build, srcなどはvolumeとしておいておく

   srcだけはvolumeでマウントさせておく? githubでコミットするsrc...などはおいておきたいし.. makeもおいておきたい。https://qiita.com/supaiku2452/items/5d6e78d10094f64d269f が参考になるかも。テストでは例えば、graphvizをホストマシンからアンインストールして、そのあと、


#. rstでは#を用いたナンバリングはインデントが大事。端末の設定にもよるが、2回インデントしないと1.からスタートにリセットされる場合もある。 




