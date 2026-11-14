# 駅・バス時刻（ekibus）

登録した区間（出発地 → 到着地）だけについて、これからの電車・バスの時刻を一覧で表示する、1ファイルのWebアプリです。

公開ページ：https://githitosh.github.io/ekibus/

## できること
- 出発地・到着地を検索して区間を登録（ブラウザの localStorage に保存）
- 登録した複数の区間を並べて表示（乗換回数・路線名・番線／のりば・行先・運賃）
- 「今すぐ」「出発時刻」「到着時刻」で時刻を指定
- 区間を「行き（出勤）」「帰り（帰宅）」で色分けし、自宅・職場と現在地（GPS）から出勤・帰宅を予想して上に表示（位置情報は端末の中だけで使用）
- 電車の番線・バスののりば（データにないときは区間ごとの「のりばメモ」）
- 北鉄バスの時刻と経路を、アプリの中で出発地・到着地から検索（直通と1回乗換。金沢大学線など、収録済みの区間は運賃も表示）
- QRコード・LINE・HTMLファイルでスマホへ送る

## データ
- [Transitous](https://transitous.org/)（[データ提供元](https://transitous.org/sources/)、地図データ © OpenStreetMap contributors）
- 全国のバス停（`busdata/` 都道府県ごと）：[国土数値情報（バス停留所データ、2022年）](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-P11-v3_0.html)（国土交通省、公共データ利用規約 PDL1.0）を [tomtkg/Japanese-Bus-Stop-Data](https://github.com/tomtkg/Japanese-Bus-Stop-Data)（CC BY 4.0）が抜粋したものから停留所名・事業者・系統を加工。時刻は含みません
- 駅名のよみ・位置（ひらがな検索用）：[TrainLCD StationAPI](https://github.com/TrainLCD/StationAPI) の駅データ（© TinyKitten, MIT License）を加工
- 駅すぱあと API（利用者が自分のアクセスキーを設定した場合）
- 北鉄バス：[北陸鉄道 時刻・運賃検索](https://arj.hokutetsu.co.jp/timetable/pathway.php)（令和8年10月1日改正）から収録

表示内容の正確性は保証しません。ご乗車の前に、必ず各交通事業者の公式情報で確認してください。

## ライセンス
MIT License（LICENSE を参照）。QRコードの作成に [qrcode-generator](https://github.com/kazuhikoarase/qrcode-generator)（© 2009 Kazuhiko Arase, MIT License）を使っています。
