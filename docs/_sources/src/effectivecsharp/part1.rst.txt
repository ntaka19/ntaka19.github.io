Part 1
=============================



番号は、本書の「項目」に対応している。
ここではそれらの補足とサマリーを記述しておく。


#. キャストにはisまたはasを利用すること。 簡単に言うと、

   #. 変換できないときの挙動の違い。as演算子の場合はnull.キャストの場合はexception.

   書籍の内容：

   -  強い型付けとはコードおける方の不一致をコンパイラが見つけてくれるということ。しかし場合によっては実行時の型チェックが避けられないケースがある。as演算子を使用する方法とcastを使用して開発者の意思をコンパイラに強制させる方法がある。

   -  むやみにキャストするよりもas演算子のほうが安全で、実行時の効率も優れるためこちらを利用したほうがよい。使えるときは使う。

   -  try catchを避けることができるため、よい。overheadの意味で。

   -  一番の違い：asやisはユーザー定義の変換をまったく行わない。実行時の型をチェックする。キャストは指定の方への変換演算子を利用できる。

   -  as
      演算子はボックス化された値型をボックス化解除されたnull許容型へと変換する場合、新しい型を作成する。

   -  キャストを使用すると、nullは任意の参照型へとキャストできるが、as演算子の場合はnull参照に対して、nullが返される。

      ::

                 object o = Factory.GetObject();
                 MyType t = o as MyType;
                 if(t!=null){
                 ...    
                 }
                 else{
                 ...
                 }

      キャストを使うとnullチェックも必要になってくる。

      ::

                     object o = Factory.GetObject();
                     try {
                         MyType t;
                         t = (MyType)o;
                     }
                     catch (InValidCastException){
                         //処理の失敗を通知する。
                     }

   -  as とcastの違いは、ユーザー定義の変換の違いにある。as
      やisは変換対象となっている実行時の型はチェックするが、それ以外はボックス化を除き、他の処理は行わない。
      特定のオブジェクトが指定の型ではないか、指定のかたから派生した型ではない場合に変換に失敗する。

   -  castは指定の型への変換演算子を利用できる。

   -  　ユーザー定義型にも問題が出てくる。

      ::

                 public class SecondType{
                     private MyType _value;
                     
                     //Convert from SecondType to MyType 
                     public static implicit operator MyType(SecondType t){
                         return t._value;
                     }
                 }

      これをもとに、

      ::

                 //version 1
                 
                 
                 object o = Factory.GetObject();
                 //This will fail. type of o is SecondType
                 MyType t = o as MyType;　//oはMyTypeではない。
                 if(t!=null){
                 ...    
                 }
                 else{
                 ...
                 }
                 
                 //version 2
                 object o = Factory.GetObject();
                     try {
                         MyType t;
                         t = (MyType)o;　//Fails. o is not MyType
                     }
                     catch (InValidCastException){
                         //処理の失敗を通知する。
                     }

      はどちらも失敗する。 version
      ２のキャストは一見ユーザー定義の変換ができるため、うまくいくと考えられるが、実は失敗する。
      version2が失敗する理由はコンパイラはコンパイル時におけるoの型を基準とｓてコードを生成するから。コンパイラはoの実行時の型をしらない。
      コンパイラからしたら、object型のインスタンスである！

      objectからMyTypeに変換するユーザー定義の変換演算子ははない。(MyType)o　のところ
      そこで、object型とMyType型をチェックする。ユーザー定義の変換はないため、コンパイラはoの実行時の型がMyTypeかどうかを判定するコードを生成。oはSecondTypeなのでチェックは失敗する。.
      つまりコンパイルの順番に沿って考えることが重要。

      次のように書けば問題は回避できる。

      ::

                 //version 3
                 object o = Factory.GetObject();
                 SecondType st = o as SecondType;
                     try {
                         MyType t;
                         t = (MyType)o;　// oはMyType
                     }
                     catch (InValidCastException){
                         //処理の失敗を通知する。
                     }

      つまりは、ユーザー定義の変換演算子はオブジェクトのコンパイル時における型のみに対して作用する。ランタイムの型に作用するものではない。

      ::

                 t = (MyType) st;

      の場合はstの宣言次第で挙動が変わる。stがSecondTypeだったら通るが、stがobjectで定義されていたら失敗する。
      一方で、

      ::

                 t = st as MyType;

      と書くと、継承関係がないもののユーザー定義の演算子が存在する場合はコンパイルエラーになる。（継承関係があれば通る、それ以外は通らない、という意味で一貫性がある）

   -  どのようにしてasを使うか。

      ::

                 object o = Factory.GetValue();
                 int i = o as int; //Will not compile!

      This is because int is a value type therefore not accepting null
      as input. However, the code can be rewritten as follows.

      ::

                 object o = Factory.GetValue();
                 var i = o as int?;
                 if(i!=null) Console.WriteLine(i.Value); 

   -  Foreach
      loopではキャストが行われている。なぜなら値型と参照型の両方に対応しないといけないから。ハードコードすると以下のようになる。

      ::

                 public void UsecollectionV2(IEnumerable theCollection){
                     IEnumerator it = theCollection.GetEnumerator();
                     while(it.MoveNext()){
                         MyType t = (MyType)it.Current;
                         t.DoStuff();
                     }
                 }

   で、結局asは使えるときはいつもつかうべきなのか。\ `Stack overflow: C#
   "as" cast vs classic cast
   [duplicate] <https://stackoverflow.com/questions/4926677/c-sharp-as-cast-vs-classic-cast>`__

   With the "classic" method, if the cast fails, an InvalidCastException
   is thrown. With the as method, it results in null, which can be
   checked for, and avoid an exception being thrown.

   Also, you can only use as with reference types, so if you are
   typecasting to a value type, you must still use the "classic" method.

   Note:

   The as method can only be used for types that can be assigned a null
   value. That use to only mean reference types, but when .NET 2.0 came
   out, it introduced the concept of a nullable value type. Since these
   types can be assigned a null value, they are valid to use with the as
   operator.

   他のコメント：

   Null comparison is MUCH faster than throwing and catching exception.
   Exceptions have significant overhead - stack trace must be assembled
   etc.

   Exceptions should represent an unexpected state, which often doesn’t
   represent the situation (which is when as works better).

#. string.Format()を補間文字列に置き換える.String.Formatは生成される文字が評価、検証されるまでは、その内容が分からないため、ミスを誘発しやすいというデメリットがある。また、引数のインデックスを間違いやすい。
   補間文字列は最初に":math:`\ \{\}"をおく。`

   ::

          Console.WriteLine($@"the ratio of the circumference of a circle to its diameter is {round ? Math.PI.ToString(): Math.PI.ToString("F2"))}"); 

#. カルチャ固有の文字列よりもFormattableStringを使用すること.
   これは例えばdoubleの小数点は、"."を使うが、ヨーロッパは","を使う。
   FormattableStringを特定のカルチャで文字列に変換してくれる。文字列補間をグローバルに。

#. 文字列指定のAPIを使用しないこと。なぜなら型の安全性が損なわれるから。そのためにnameofが使えるようになる。
   「nameofを使用すると、プロパティの名前を変更した場合、イベントの引数に指定された文字列にも変更が反映される。」これが基本的な用法

   ::

          Console.WriteLine(nameof(System.Collections.Generic));  // output: Generic
          Console.WriteLine(nameof(List<int>));  // output: List
          Console.WriteLine(nameof(List<int>.Count));  // output: Count
          Console.WriteLine(nameof(List<int>.Add));  // output: Add

          var numbers = new List<int> { 1, 2, 3 };
          Console.WriteLine(nameof(numbers));  // output: numbers
          Console.WriteLine(nameof(numbers.Count));  // output: Count
          Console.WriteLine(nameof(numbers.Add));  // output: Add

   保守性の高いコードを使うことができる。

   ::

          /// <summary>
      /// モデル
      /// </summary>
      public class AmountModel
      {
          ///<summary>コード</summary>
          public int Code { get; set; }

          ///<summary>税抜き額</summary>
          public decimal Amount1 { get; set; }

          ///<summary>税額</summary>
          public decimal Amount2 { get; set; }
      }


      public class Test
      {
          public void Main()
          {
              // データ作成
              var amountModel = new AmountModel { Code = 1111, Amount1 = 3000m, Amount2 = 300m };

              // 税込み額計算
              var amount = Calculate(amountModel);

              // 結果
              Console.WriteLine($"税込み額:{amount.ToString()}");
              
              // 結果出力
              // 税込み額:3300
          }

          /// <summary>
          /// 計算
          /// </summary>
          /// <typeparam name="T"></typeparam>
          /// <param name="obj"></param>
          /// <returns></returns>
          public decimal Calculate<T>(T obj)
          {
              decimal amount = 0m;

              Type type = typeof(T);
              foreach (PropertyInfo property in type.GetProperties())
              {
                  switch (property.Name)
                  {
                      case "Amount1":
                      case "Amount2":
                          amount += (decimal)type.GetProperty(property.Name).GetValue(obj, null);
                          break;
                      default:
                          break;
                  }
              }

              return amount;
          }
      }

   AmountModelのメンバが変わったとする。

   ::

          public class AmountModel
      {
          ///<summary>コード</summary>
          public int Code { get; set; }

          ///<summary>税抜き額</summary>
          public decimal TaxExcluded { get; set; }

          ///<summary>税額</summary>
          public decimal TaxAmount { get; set; }
      }

   この時、次の箇所でエラーは出るので修正可能。

   ::

          var amountModel = new AmountModel { Code = 1111, TaxExcluded = 3000m, TaxAmount = 300m };

   一方で、Testではエラーが出てこないため(switchにひっかからない）、実行すると税込み額:0が表示される。次のように修正すれば正しくコンパイルエラーになるため、修正できる。

   ::

          switch (property.Name)
      {
          case nameof(AmountModel.Amount1):
          case nameof(AmountModel.Amount2):
              amount += (decimal)type.GetProperty(property.Name).GetValue(obj, null);
              break;
          default:
              break;
      }
          

#. デリゲートを使用してコールバックを表現する: call back
   の例：仕事をふって、その間に自分は作業をしている。どうしても必要な時に自分の手を止める。Callbackはサーバーからの応答を非同期的に待機するような場合に使用する。delegateは主にeventに合わせて利用するが、それだけではない。「特定のクラスの間でデータをやり取りする必要があるものの、互いのインタフェースを使用するほどには密に連携させたくない場合」が最善だったりする。

   -  Callback関数とは呼び出し先の関数の実行中に実行されるようあらかじめ指定しておく関数。eg.
      main
      がcallbackを呼び出して、mainは次の処理を行う。その後に、callback関数の処理が終わったら呼び出し戻す。

   -  イベントハンドラとは、コンピュータプログラムで、特定の出来事（イベント）が発生した時に実行するよう定められた処理のこと。
      対象となるイベントの種類や条件と、処理内容をセットで記述する

#. イベントの呼び出し時にnull条件演算子を使用すること:
   イベントについては、次の手順:

   #. 必要に応じてイベントを定義。

   #. このイベントにアタッチされたイベントハンドラを呼び出すだけ。
      このことによって、後ろに隠されたマルチキャストデリゲートによって、登録された全てのハンドラが成功する限り呼び出される。

   ::

          private EventHanlder<int> Updated; 
          
          public void RaiseUpdates(){
              counter++;
              if (Updates != null)
                  Updated(this, counter);
          }

   ここで、Updatedはイベントでありそこにハンドラ登録されている。
   上のコードの問題点は、null
   checkが通った直後に、イベントが解除された場合、null
   参照となってしまう点である。 マルチスレッドの時に問題起きる。

   スレッドセーフ にするためには以下を行う。
   下のコードでは現在のイベントハンドラを新しいローカル変数handlerに割り当てている。
   handlerには、メンバ変数であるイベントUpdatedから参照されている全ての元ハンドラを参照するようなマルチキャストデリゲートが格納される。

   イベント割り当て演算子では右辺の浅いコピーが割り当てられる。浅いコピーはアタッチされたイベントハンドラそれぞれに対する参照コピーが含まれる。
   別のスレッドでイベントからハンドラが解除されると、登録解除個〇度ではクラスに定義されたイベントフィールドが変更されるが、ローカル変数からはそのハンドラが削除されない。

   ::

          public void RaiseUpdates(){
              counter++;
              var handler = Updated;
              if (handler != null)
                  handler(this, counter)
          }

   -  Event型は参照型であり、一見、Updatedを解除すると、handlerも解除されてしまうように思える。仮にhandlerも解除されてしまえば、意味がないことになる。

   -  しかし、handlerは解除されない。なぜなら、handlerは immutable
      であるから。
      ここが参考にできる\ `why-can-a-temporary-variable-stop-the-client-from-removing-event-handler <https://stackoverflow.com/questions/835274/why-can-a-temporary-variable-stop-the-client-from-removing-event-handler/835301#835301>`__

      The following code snippet is from book Effective C#,

      ::

                 public event AddMessageEventHandler Log;
                 
                 public void AddMsg ( int priority, string msg )
                 
                 {
                     // This idiom discussed below.
                     AddMessageEventHandler l = Log;
                     if ( l != null )
                         l ( null, new LoggerEventArgs( priority, msg ) );
                 }

      The AddMsg method shows the proper way to raise events. The
      temporary variable to reference the log event handler is an
      important safeguard against race conditions in multithreaded
      programs. Without the copy of the reference, clients could remove
      event handlers between the if statement check and the execution of
      the event handler. By copying the reference, that can’t happen.

      Why can a temporary variable stop the client from removing event
      handler? I must be missing something here.

      .. rubric:: Answer
         :name: answer

      It doesn’t stop the client from removing the event handler - it
      just means that you’ll call that event handler anyway.

      The important bit you may be missing is that delegates are
      immutable - when an event handler is removed, the value of Log
      will change to be the new delegate or null. That’s okay though,
      because by that stage you’re using 1 instead of Log.

   -  イベントに関してpub-subの出材パターンがあるが、、、

   上記よりより良い書き方は、次の通り、

   ::

          public void RaiseUpdates(){
              counter++;
              Updated?.Invoke(this, counter);
          }

   まずはnull演算子?により安全性にイベントを呼び出している。
   コンパイラは全てのデリゲートあるいはイベントの定義に対して、タイプセーフInvokeメソッドを生成する。

#. ボックス化およびボックス化解除を最小限に抑える。
   (そのほかの参考：\ `https://ufcpp.net/study/csharp/rmboxing.html <参考>`__

   -  値型は多態性を持たない型。 一方で.NetではSystem.Object
      というすべてのオブジェクトの親である参照型を定義している。

   -  ギャップをうめるために、ボックス化とボックス化解除を用意している。

      -  ボックス化：値型を不定な参照型オブジェクトのメンバとすることで参照型が必要な場面においても値型を利用できる仕組み

      -  ボックス化解除：ボックス化された値型のコピーを取り出すこと。

   -  System.Objectやインタフェースを必要とする場面で値型を使用する場合に利用する。常にパフォーマンスを落とす。また、ボックス化（解除）は常にコピーは一時的なコピーを作るため潜在的なバグの温床。

   -  ボックスはヒープ上に確保される。
      ヒープ、スタック、領域についてどこかで整理しておく必要あり。

   -  ボックスに格納された値型を参照する場合、格納庫された値型のコピーが生成されて返される。ボックスの中身にアクセス（参照）する際は毎回コピーされた新しい値が返される。

   -  名前のない参照型が作成される。（値型をSystem.Objectbの参照に変換するため）

   -  例えば、

      ::

                 int x = 5;
                 object y = x; //box
                 int z = (int)y; //unbox

      あるいは、

      ::

                 Console.WriteLine($"first {firstNumber}$);

      においては、

      ::

             int i=25;
             object o=j;
             Console.WriteLine(o.ToString());

      が起きている。

   -  一般的にヒープ領域確保はスタックと比べると重たい処理である。値型の利点はスタック上に値を置く。（ヒープを使わないことによる性能向上である）
      ボックス化を避けるためには 具体的な方をできる限り指定する。

      ::

                 class Program
             {
                 static void Main()
                 {
                     ObjectWriteLine(5);
                     IntWriteLine(5);
                 }
             
                 static void ObjectWriteLine(object x)
                 {
                     // object.ToString が呼ばれる
                     // 値型に対してはボックス化が必要
                     Console.WriteLine(x.ToString());
                 }
             
                 static void IntWriteLine(int x)
                 {
                     // こういう場合は、int.ToString が直接呼ばれる
                     // virtual メソッドだからといって、必ず virtual に呼ばれるわけじゃない
                     // コンパイルの時点で型が確定してるなら、非 virtual にメソッドを呼ぶ
                     Console.WriteLine(x.ToString());
                 }
             }

      int.ToString(int側でオーバーライドしたもの）が直接呼ばれるため、ボックス化する必要はない。一方で引数がオブジェクトの時ボックス化が起きる。

   -  もう一つの例：

      ::

                 Console.WriteLine($@"数値 {firstnumber.ToString()}");

      あらかじめ文字列インスタンスに変換されている。
      暗黙的にSystem.Objectへの変換が行われることを注意するべき。

   -  構造体は値型。これのコレクションはコピーができてしまう。不変な値型を作成するべき。

   -  ジェネリック型について：

#. 親クラスの変更に応じる場合のみnew修飾子を使用すること。

   -  Virtual method: 一つの制約を表すことができる。Virtual
      メソッドは派生クラスにおいてその実装が変更されることを期待している。

   -  非Virtual
      methodがnew修飾子によって上書きされないように注意するべき。(派生クラスと基底クラスで振る舞いが変わる）

      ::

                 public class MyClass{
                     public void MagicMethod(){
                         Console.WriteLine("myclass");
                     }
                 }
                 
                 public class MyOtherClass : MyClass{
                     //MagicMethodをこのクラス用に再定義
                     public new void MagicMethod(){
                         Console.WriteLine("myotherclass");
                     }
                 }
                 

      一方で、「基本的にVirtual」な設計とは派生クラスにおいて全ての挙動を変更しても構わないということ。

   -  メソッドにnewを使用するべき場面はただ一つ：派生クラスですでに使用済みのメソッド名が、新しいバージョンの親クラスに定義されたメンバと競合した場合。

      例えば、BaesWidgetの新しいバージョンに"NormalizeValues"メソッドが新たに追加されていた場合、MyWidgetですでにその名前を使っていたとすると競合起きてしまう。そこで、MyWidgetの関数名を変えるか、それが現実的でない場合は、new演算子でリダイレクトする。
      長期運用シナリオを考えた場合は、やはり名前を変えた方が良い。

      ::

                 public class MyWidget: BaseWidget{
                     public new void NormalizeValues(){
                         ...
                         base.Normalizevalues();
                     }
                 }

