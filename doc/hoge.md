## はじめに
2025年4月にVSCode拡張機能であるGithub Copilotにエージェントモードが追加されたことを受け、   
現時点でAIでどこまで開発できるのか、AIを用いた開発は普段とどのように異なるのかなどを検証するために、   
今回Discord Bot "FullParty" を開発することにした。

## 検証結果
名状しがたい検証結果のようなもの

* 完全に部下に仕事を投げている感覚
* 今回のケースだとある程度どのように実装するかプログラマー側が想像できており、具体的な指示を出せる状態だったので比較的スムーズだった
* 具体的な指示が出せないと、アウトプットもあやふやなものになってしまう。ただし、それなりの品質はあるので後から肉付けしていくことも可能
  > 追記: これは最初から段階を踏んでやる想定があり、後続の指示をより具体的なものにするために一旦アバウトな指示を出して様子見していただけだと思われる。
* 設計と同じぐらいテストが大事、テストに人間が介入しない場合、実装がとんでもないスピードで進む
* 結局、1mmもコードを書いていない、というかGithub Copilotにしか入力してない、画像すらChat GPTで作成した
* 唯一プログラマーが実行したのはDev Containerの起動とGithub関係の操作
* ただし、このあたりもMCPを設定すればCopilotから操作できる
* もはやキーボード使うより音声入力したほうが良かったのでは？