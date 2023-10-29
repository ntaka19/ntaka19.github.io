Git
=======


今後まとめてみたいところ。典型的なところを扱いたい。

- git と githubの違い

- Centralized Version Control System: CVCS と分散型の違い

- コミットメッセージの書き方
 
- git rebase, mergeの挙動の違い

- git reset いつ使うか。レポジトリをリモートに合わせるタイミング... (https://stackoverflow.com/questions/9688867/git-pull-not-pulling-everything)

- git actionsの書き方まとめ

- unable to unlink old ... permission denied エラーについて : https://qiita.com/FrogWoman/items/31cd5df4c4a5ae23f7e0

    .. 
        cd  作業ディレクトリ
        sudo chown -R ユーザ名 ./
        sudo chgrp -R グループ名 ./


.. toctree::
   :maxdepth: 1

    ./githubpages.rst
    ./githubactions.rst

    