Part 2
========


11. .Netリソース管理を理解する.

    -  実行環境におけるメモリやそのほかの主要なリソースの管理豊富おを理解する必要がある。.Netの場合は、メモリ管理や
       ガーベッジコレクタ。

    -  イベントハンドラやデリゲートを使用することでオブジェクトの間の結びつきが生まれ、その結果として、地震が意図するよりも長い期間オブジェクトがメモリに存在し続けることがあり得る。

    -  ガーベっじとなったオブジェクトを見つけ出す。GCはアプリケーション内で生存中のオブジェクトからエンティティが到達可能かどうか把握できる。アプリケーションから到達不可能であれば消去される。

    -  また、GCは実行されるたび、コンパクションする。ヒープにある使用中のオブジェクトの再配置が行われる。

12. メンバには割り当て演算子よりもオブジェクト初期化子を利用すること。

    -  各コンストラクタ内でメンバ変数を初期化するのではなく、メンバ変数を宣言した時点で初期化してしまうと良い。

    -  initializer 構文

    -  オブジェクト初期化子：new

    -  オブジェクト初期化子を使用すると、オブジェクトの作成時にアクセスできるフィールドまたはプロパティに、コンストラクターを呼び出して代入ステートメントを使用しなくても、値を割り当てることができます。

       ::

                  Cat cat = new Cat { Age = 10, Name = "Fluffy" };
                  Cat sameCat = new Cat("Fluffy"){ Age = 10 };

    -  メンバ初期化子は、今ストラクより先に実行される。

       ::

                 public class MyClass
                 {
                  private List<string> labels = new List<string>();
                  
                  public MyClass(){...}
                 }

13. Staticメンバを適切に初期化すること

    -  staticメンバ変数は型のインスタンスが1つ以上作成されるよりも前に初期化されるべき。（どういう意味？）
       newする前にstatic member=5みたいに設定する。

    -  CLRは、「型がアプリケーション空間(AppDomain)において初めてアクセスする」よりも前の時点で、その型のstatic
       コンストラクタを自動的に呼び出す。staticコンストラクタで例外が出た場合、型の初期化に失敗する（Appdomainで呼び出さる前に）。その派生型によっても問題が引き起こされる。AppDomainがアンロードされない限り型を初期化されない状態になる。

    -  　staticメンバの初期化はオブジェクト初期化ではなく、staticコンストラクタで行うべき。
       staticメンバに対してオブジェクト初期化子を使用する場合、発生した例外をクラス自身で処理できない。　staticコンストラクタの場合はクラス内での例外処理が可能.

       ::

                  static MySingleton(){
                      try {
                          theOneAndOnly = new MySingleton();
                      }
                      catch{
                      
                      }
                  }

       　

    -  staticコンストラクタ：ほかのメソッドや変数、プロパティに対するアクセスよりも前に実行される。これによりsingleton
       patternの強制などができる。

    -  static変数初期化子(=new
       をメンバ定義時に行う）、staticコンストラクタはクラス内のstaticメンバを初期化する場合に最適な方法。

14. 初期化ロジックの重複を最小化する。(デフォルト引数 vs.
    コンストラクタオーバーライド）

    -  コンストラクタを定義するという作業は幾度となく繰り返されるもの。

    -  デフォルト引数は、引数の名前とそのデフォルト値がpublic
       interfaceの一部になる。つまり引数の名前を変更した場合、このクラスを使用する全てのコードが名前の変更に追従しないといけない。

    -  static プロパティはコンパイル時定数ではない。

       -  コンパイル時定数：コンパイルした後に値を直書きしたときと同じように扱われる。

    -  利用側を再コンパイルするまで...ライブラリだけコンパイルして再配布はできない。

    -  名前付き引数は、それを追従しているときにエラーが出る可能性がある。これはどういうことかというと、

       ::

                  static int Sum(int x, int y = 1, int z = 1)
                      {
                          return x + y + z;
                      }

       に対して、

       ::

                  Sum(x: 0, y: 1, z: 2);

       と呼び出しできるし、

       ::

                  Sum(x:0, z:2);

       としても呼び出すことができるが、 例えば、

       ::

                  static int Sum(int x, int y = 1, int zzz = 1)
                      {
                          return x + y + zzz;
                      }

       と変更した場合、呼び出しがエラーになる。

    -  将来起こりうる変化に対しては、オーバーロードされたコンストラクタの方が耐性がある。

    -  コンストラクタに共有する処理を別メソッドとして切り出す方法にはデメリットがある。

       -  コンパイラはいくつかの機能を呼び出すためのコードを自動的にコンストラクタに追加する。

       -  全ての変数に愛するオブジェクト初期化子用のぶんを追加する。

       -  こっちが実装として良い：（「コンパイル時にオブジェクト初期化子用のコードがよばれる回数が少なくて済む。親クラスのコンストラクタ呼び出しの回数(object())も一回だけ)

          ::

             　　  public class MyClass{
                   private List<ImportantDat> call;
                 
                   private string name;
                 
                   public Myclass(null, ""){
                   }
                   public MyClass(int initialCount):this(initialCount, string.Empty){
                   
                   }
                   public MyClass(int initialCount, string name){            //コンパイル時にここでオブジェクトだったり、初期化子用のコードがよばれる。

                     col =(initialCount > 0) ? new List<ImportantData>(initialCount) : new List<ImportantData>();
                     this.name = name;
                   }
                 }

          共通の機能を切り出してしまうと、非効率的になる。

          ::

               public class MyClass{
               private List<ImportantDat> call;

               private string name;

               public Myclass(null, ""){
                   //コンパイル時にここでオブジェクトだったり、初期化子用のコードがよばれる。
                 commonConstructor(null, "");
               }

               public MyClass(int initialCount):this(initialCount, string.Empty){
                 //コンパイル時にここでオブジェクトだったり、初期化子用のコードがよばれる。
                 commonConstructor(initialCount, name);
               }

               private void commonConstructor(int count, string name){
                 col =(initialCount > 0) ? new List<ImportantData>(initialCount) : new List<ImportantData>();
                 this.name = name;
               }
             }

       -  型のインスタンスが初めて生成される際に行われる処理の流れ：

          #. static変数のメモリストレージがnullに初期化される

          #. static変数の初期化子が実行される

          #. 親クラスの staticコンストラクタが実行される

          #. staticコンストラクタが実行される

          #. インスタンス変数のメモリストレージがnullに初期化される

          #. インスタンス変数の初期化子が実行される

          #. 適切な親クラスのコンストラクタが実行される

          #. インスタンスコンストラクタが実行される

          型の初期化処理は1回しか行われない。同じ型の別インスタンスにおける初期化処理は手順5(「インスタンス変数のメモリストレージが初期化」から始まる。

    -  「static初期化子はクラスのロード時に行われる」

15. 不必要なオブジェクト生成を避けること

    -  ヒープオブジェクト：いろんなことができる。スタックは、

    -  参照型のオブジェクトをメソッド中でローカル変数として大量に使用s流ほど、アプリケーショのパフォーマンスに大きな影響を与えることになる。

    -  GCの実行条件はメモリの確保料と確保の頻度！GCにできるだけ仕事させないこと！

       ::

              protected override void OnPaint(PaintEventArgs e)
              {
                  using (Font MyFont = new Font("Arial",10.0f){
                      e.Graphics.DrawString(DateTime.Now.ToString(), myFont, Brushes.Black,newPointF(0, 0)); 
                  }
                  base.OnPaint(e);
              }

       Fontオブジェクトが毎回破棄されなければならなくなる。
       その代わりメンバに昇格させると良い。

       ::

              private readonly Font myFont = newFont("Arial", 10.0f);
              protected override void OnPaint(PaintEventArgs e)
              {
                  e.Graphics.DrawString(DateTime.Now.ToString(), myFont, Brushes.Black,newPointF(0, 0)); 
                  base.OnPaint(e);
              }

    -  Fontオブジェクトのように、IDisposableインターフェイスを実装するオブジェクトをローカル変数からメンバ変数に昇格させる場合は、暮らす自身にもIDisposableインタフェースを実装するべき。

    -  

.Net frameworkの構造から頑張る必要がある。



