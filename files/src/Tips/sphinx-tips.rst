Sphinx Tips
===========




#. Sphinx directives

   https://www.sphinx-doc.org/ja/master/usage/restructuredtext/directives.html

#. githubpagesで利用可能とするためには:


    .. code-block:: bash
       :linenos:
       :caption: Makefile (files直下にある). make htmlコマンドで、sphinx buildの代わりにautobuildを設定している。ctrl - Sで都度手元でビルドできるようにしている。--host 0.0.0.0 --port 8000 の設定については、docker側のportとローカル側のportの対応関係を規定している。ローカルのブラウザでhttp://localhost:8000/でアクセス可能となる。

        # Minimal makefile for Sphinx documentation

        # You can set these variables from the command line, and also
        # from the environment for the first two.
        SPHINXOPTS    ?=
        SPHINXBUILD   ?= sphinx-build
        SOURCEDIR     = .
        BUILDDIR      = ../docs#_build

        # Put it first so that "make" without argument is like "make help".
        help:
                @$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

        .PHONY: help Makefile

        # Catch-all target: route all unknown targets to Sphinx using the new
        # "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
        # $(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/
        %: Makefile
                # @$(SPHINXBUILD) -b $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
                sphinx-autobuild -b $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) --host 0.0.0.0 --port 8000



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


#. Jupyter executeモジュール(jupyter-execute)。

    .. jupyter-execute::

      from graphviz import Graph
      import math
      
      nodes = 8 
      dot = Graph()

      # Set the default node and edge attributes
      dot.node_attr.update(shape='circle', fixedsize='true', width='0.5')
      dot.edge_attr.update(dir='both')

      # Define the positions of the nodes using polar coordinates
      dot.node('n0', pos='0,0!')
      dot.node('n1', pos='0.9239,0.3827!')
      dot.node('n2', pos='0.9239,-0.382!')
      dot.node('n3', pos='0.3827,-0.9239!')
      dot.node('n4', pos='-0.3827,-0.9239!')
      dot.node('n5', pos='-0.9239,-0.3827!')
      dot.node('n6', pos='-0.9239,0.3827!')
      dot.node('n7', pos='-0.3827,0.9239!')
        
      # Create bidirectional edges between the nodes
      for i in range(nodes):
          for j in range(nodes):
              if i != j:
                  dot.edge("n"+str(i), "n"+str(j), dir='both')


      dot.render('network_graph', format='png')
           

      from IPython.display import Image
        
      Image(filename='network_graph.png')

    
    SABRのボラティリティサーフェス(コード非表示)
   
    .. jupyter-execute::
      :hide-code:

      import numpy as np
      import matplotlib.pyplot as plt

      def SABR_vol(alpha, beta, rho, nu, K, F, T):
          """Calculate the SABR volatility for a given set of parameters."""
          if abs(F - K) < 1e-10:
              # At-the-money (ATM) approximation
              return (F*(1 + (nu**2/24)*(alpha**2/(F**2)))**(0.5)*alpha)
          else:
              # Non-ATM case
              z = (nu/alpha)*(F*K)**((1 - beta)/2)*np.log(F/K)
              x = np.log((np.sqrt(1 - 2*rho*z + z**2) + z - rho)/(1 - rho))
              factor1 = alpha*(F*K)**((beta - 1)/2)
              factor2 = 1 + ((1 - beta)**2/24)*alpha**2*(F*K)**(1 - beta)
              return factor1*factor2*x/z

      # Define the SABR parameters
      alpha = 0.3
      beta = 0.5
      rho = -0.25
      nu = 0.4

      # Define the option strikes and maturities
      strikes = np.linspace(70, 130, 25)
      maturities = np.linspace(0.1, 2, 25)

      # Calculate the implied volatilities for each combination of strike and maturity
      implied_vols = np.zeros((len(strikes), len(maturities)))
      for i in range(len(strikes)):
          for j in range(len(maturities)):
              K = strikes[i]
              T = maturities[j]
              F = 100
              implied_vols[i, j] = SABR_vol(alpha, beta, rho, nu, K, F, T)

      # Plot the implied volatilities as a surface
      X, Y = np.meshgrid(maturities, strikes)
      fig = plt.figure()
      ax = fig.add_subplot(projection='3d')
      ax.plot_surface(X, Y, implied_vols.T)
      ax.set_xlabel('Maturity')
      ax.set_ylabel('Strike')
      ax.set_zlabel('Implied Volatility')
      plt.show()


#. Graphvizモジュールでそのまま実行する方法

    .. graphviz::
        :caption: graphvizでフローチャートを作成する際の主な流れ

        digraph G1 {

            graph [size="4,4"];
            node [shape=diamond] d ;
            node [shape=parallelogram] b c e;
            node [shape=box,style=rounded] a f ;
                a [label="スタート"];
                b [label="Kateでtext fileを編集し、\n dotファイルを作成"];
                c [label="xdotで確認"];
                d [label="正しくできているか"];
                e [label="sphinxに取り込む"];
                f [label="エンド"];


                a->b;
                b->c;
                c->d;
                d->e [label="Yes"];
                d->b [label="No"];
                e->f;

        }

#. Highlight word in sphinx
   (https://stackoverflow.com/questions/49210787/how-do-i-highlight-text-in-python-sphinx)

#. javascriptボタンクリックは実装できるが、chart がなぜかできない。


#. github actionsでgithub pages用にデプロイをスケジューリングしてあげることで、定期的にページの更新を行うことができる。例えば天気予報を取得することができる。github actionsはmainブランチからしか実装できない? 


#. github pagesデプロイまでの流れを抑えておく必要がある。そもそも"home directoryはどこですか？” 

    - files/figures に入れたものがdocs/_images に行く。（正しくビルドされていれば）。そしてdocsの状態のものがgithub pagesにてデプロイされる。したがって、画像はfiles/figuresに入っている必要がある。

#. RSTファイルでinternal link を作る方法 (underscoreを使う)：
    次をrst本文中に書き込む。

    :: 

        .. _RBC25: //これはアンカー

            This is a link to the RST Overview: `RBC25`_. //ここがリンク

#.  Plantuml をdocker + sphinx 環境で入れる方法

    #. pip install する requirements.txtに入れる。

        ::  

            pip install plantuml
            pip install sphinxcontrib-plantuml


    #. ダウンロードしてきたplantuml-1.2023.9.jarを/root/にコピーする。DockerFileを編集する。plantuml-1.2023.9.jarをローカルからDockerのイメージにコピーしないとなぜかconf.pyからは指定できない。(マウントしているのに相対パスで読めないのはなぜ?)

        :: 

            # Install Java (jarを動かすため)
            RUN apt-get update && apt-get install -y openjdk-11-jre

            COPY ./plantuml-1.2023.9.jar /root/
            RUN chmod +r /root/plantuml-1.2023.9.jar
            RUN ls /root/plantuml-1.2023.9.jar



    #. conf.pyをeditする。

        ::

            extensions = ['sphinxcontrib.plantuml']
            plantuml = 'java -jar /root/plantuml-1.2023.9.jar'

    #. rstファイルに記入する。
        
        :: 

            .. uml::

                @startuml
                Class01 -> Class02 : Link
                Class02 --> Class03 : Another link
                @enduml
        
        以下の図を得る。
        
        .. uml::

                @startuml
                Class01 -> Class02 : Link
                Class02 --> Class03 : Another link
                @enduml