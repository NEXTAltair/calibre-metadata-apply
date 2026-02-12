# calibre-metadata-apply

`calibredb` を使って、既存Calibre書籍のメタデータを更新するスキルです。

## セットアップ

1. このスキルを実行する環境にCalibreをインストールする
   - 必須: `calibredb`
2. PDF調査用に `pdffonts` を使えるようにする（例: `poppler-utils`）
3. `calibredb` と `pdffonts` が `PATH` で実行できることを確認する
4. Calibre Content server に到達できることを確認する
5. `--with-library` は次の形式で指定する
   - `http://HOST:PORT/#LIBRARY_ID`
   - localhost前提にしない（明示的なHOST:PORTを使う）
6. 認証が有効な場合は次を指定する
   - `--username <user>`
   - `--password-env <ENV_VAR>`

### ユーザーが先に実行すること（例: Ubuntu/WSL）

```bash
sudo apt update
sudo apt install -y calibre poppler-utils
```

## 重要

OpenClawが入っているだけでは不十分です。実行環境側に `calibredb` が必要です。

WindowsではDefender Controlled Folder Access等の影響で書き込みが失敗する場合があります。
`WinError 2/5` などのパス/アクセス系エラーが出る場合は、Calibreライブラリフォルダや実行バイナリを許可リストに追加してください。

## 安全モデル

- 入力はJSONL（1行=1更新）
- `id` 必須
- デフォルトはdry-run（`--apply` 指定時のみ書き込み）

## クイックテスト（dry-run）

```bash
cat references/changes.example.jsonl | python3 scripts/calibredb_apply.py \
  --with-library "http://127.0.0.1:8080/#MyLibrary"
```
