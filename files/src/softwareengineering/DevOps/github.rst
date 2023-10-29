Github
========

Github Pages
~~~~~~~~~~~~~

- 静的ウェブサイト
- 内容が更新されるのはPush時。

    * git pagesで表示するブランチ(gh-pages)と、内容をコミットするブランチ(mainとする)を決める。
    * git actionsで更新することができる。



Github Actions
~~~~~~~~~~~~~~~~

開発のワークフローを自動化するためのスクリプトを設定できる。この仕組みを利用することでウェブページの更新を行える。

- .github/workflowsフォルダを作り、そこにyamlファイルを定義する。
- secrets.GITHUB_TOKEN を用いる。
- API keyについても、secretsで登録することができる。

.. code-block:: bash
       :linenos:
       :caption: 1時間ごと(0分)にpythonスクリプトを実行し、gh-pagesブランチにコミットする。

        name: Deploy to Gh-pages (Scheduled)

        on:
        push:
        schedule:
            - cron:  '0 * * * *'

        jobs:
        build:

            runs-on: ubuntu-latest

            steps:
            - uses: actions/checkout@v2
            - name: Set up Python 3.9
            uses: actions/setup-python@v4
            with:
                python-version: 3.9
                cache: 'pip' #dependency caching
            - name: Install dependencies
            run: |
                python -m pip install --upgrade pip
                pip install -r requirements-api.txt
            - name: Run script
            run: |
                python ./files/src/dashboard/forecast.py #メインスクリプトを実行

            - name: Run marketgenerate script
            run: |
                python ./files/src/dashboard/generatehtml.py #メインスクリプトを実行
            env:
                FMP_API: ${{ secrets.FMP_API }}

            - name: deploy
            uses: peaceiris/actions-gh-pages@v3
            with:
                github_token: ${{ secrets.GITHUB_TOKEN }}
                publish_dir: .
                publish_branch: gh-pages







