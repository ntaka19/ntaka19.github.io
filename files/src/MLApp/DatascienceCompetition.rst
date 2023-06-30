データサイエンスコンペで作った雛形(★)
======================================

目的：

* 効率的に機械学習のアルゴリズムを試したいときに、拡張可能なものを準備した
* システム化を念頭において、デザインパターンをpythonで実装した。 
* 今後もライブラリのアップデートとともに更新する可能性はある。


#. Factory Methodでまとめてみる

    .. uml:: 

        @startuml

        interface IFactory {
            + factoryMethod(): Product
        }

        interface IProduct {
            + operation(): void
        }

        class ConcreteFactory {
            + factoryMethod(): Product
        }
        
        class ConcreteProduct {
            + operation(): void
        }

        IFactory -right--> IProduct : create
        ConcreteFactory -right--> ConcreteProduct : create

        IFactory <|.. ConcreteFactory : implements
        IProduct <|.. ConcreteProduct : implements

        @enduml


    これをpythonで書くと、


#. 利用のパターンについて