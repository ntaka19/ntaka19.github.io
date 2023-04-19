Sphinx Tips
===========




#. Sphinx directives

   https://www.sphinx-doc.org/ja/master/usage/restructuredtext/directives.html

#. githubpagesで利用可能とするためには


  ::

    # Minimal makefile for Sphinx documentation
    #

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




