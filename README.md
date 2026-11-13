# 駅・バス時刻（ekibus）

登録した区間（出発地 → 到着地）だけについて、これからの電車・バスの時刻を一覧で表示する、1ファイルのWebアプリです。

公開ページ：https://githitosh.github.io/ekibus/

## できること
- 出発地・到着地を検索して区間を登録（ブラウザの localStorage に保存）
- 登録した複数の区間を並べて表示（乗換回数・路線名・番線／のりば・行先・運賃）
- 「今すぐ」「出発時刻」「到着時刻」で時刻を指定
- 金沢大学自然研前と、金沢駅・武蔵ヶ辻・近江町市場・香林坊・兼六園下・金沢城・東金沢駅・西金沢の間の北鉄バス（アプリ内の時刻表）
- QRコード・LINE・HTMLファイルでスマホへ送る

## データ
- [Transitous](https://transitous.org/)（[データ提供元](https://transitous.org/sources/)、地図データ © OpenStreetMap contributors）
- 駅すぱあと API（利用者が自分のアクセスキーを設定した場合）
- 北鉄バス：[北陸鉄道 時刻・運賃検索](https://arj.hokutetsu.co.jp/timetable/pathway.php)（令和8年10月1日改正）から収録

表示内容の正確性は保証しません。ご乗車の前に、必ず各交通事業者の公式情報で確認してください。

## ライセンス
MIT License（LICENSE を参照）。QRコードの作成に [qrcode-generator](https://github.com/kazuhikoarase/qrcode-generator)（© 2009 Kazuhiko Arase, MIT License）を使っています。
