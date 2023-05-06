# ToyBox-Batch

## Sitemap
サイトマップ生成・アップロードジョブ

### 概要
ToyBoxの特定のAPIエンドポイントからサイトマップを生成し、生成した`xml`ファイルをWasabiにアップロードする。
配信はcloudflare workersにて行う。

### crontabに登録
登録するシェルスクリプト：`./sitemap/job.sh`
