Latex
======


overleafをローカルに移植するために行った手順の備忘録:


- texworksに入れる場合は、「編集」→「設定」でタイプセットの方法を追加する。jbookを利用する場合は、pLatexを追加。(DVItoPDFも必要に応じて追加). platex.exeもtexliveをインストールしたときに入っているはず。
- Pygmentizeを入れる場合は、anaconda3/Scriptsのパスを通す。バッチを利用する場合はそこに書いても問題ない。


.. code-block:: bash
       :linenos:
       :caption: dviを作成し、pdfを作成するバッチファイル。

        set file=main.tex
        set dvifile=main.bat

        platex -shell-escape $file
        dvipdfmx $dvifile



