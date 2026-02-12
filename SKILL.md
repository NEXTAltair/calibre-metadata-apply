---
name: calibre-metadata-apply
description: Apply metadata updates to existing Calibre books via calibredb over a Content server. Use for controlled metadata edits after target IDs are confirmed by a read-only lookup.
---

# calibre-metadata-apply

Calibre既存書籍のメタデータを書き換えるスキル。

## Requirements

- `calibredb` が実行環境のPATH上にあること
- 到達可能な Calibre Content server URL
  - `http://HOST:PORT/#LIBRARY_ID`
- 認証有効時は `--username` + `--password-env`

## Supported fields

### Direct fields (`set_metadata --field`)
- `title`
- `title_sort`
- `authors` (string with `&` or array)
- `author_sort`
- `series`
- `series_index`
- `tags` (string or array)
- `publisher`
- `pubdate` (`YYYY-MM-DD`)
- `languages`
- `comments`

### Helper fields
- `comments_html` (OC marker block upsert)
- `analysis` (comments用HTML自動生成)
- `analysis_tags` (tagsへ追加)
- `tags_merge` (default `true`)
- `tags_remove` (merge後に指定タグ削除)

## Required execution flow

### A. Target confirmation (mandatory)
1. read-onlyで候補抽出
2. `id,title,authors,series,series_index` を提示
3. ユーザーに最終対象IDを確認
4. 確定IDだけJSONL化

### B. Proposal synthesis (metadata不足時)
1. ファイル抽出 + Web候補を集約
2. 1回の提案表に統合して提示
   - `candidate`, `source`, `confidence (high|medium|low)`
   - `title_sort_candidate`, `author_sort_candidate`
3. ユーザー承認
   - `approve all`
   - `approve only: <fields>`
   - `reject: <fields>`
   - `edit: <field>=<value>`
4. 承認項目のみ反映
5. 低確信/衝突時は空欄維持を優先

### C. Apply
1. dry-run実行（必須）
2. ユーザー明示OK後に `--apply`
3. 再読取で最終値を報告

## Analysis worker policy

- 重めの候補生成は `sessions_spawn` を使う
- 解析は軽量subagentモデルを使う（main重モデルを避ける）
- 最終判断/dry-run/applyはmainで実施

## Long-run turn-split policy (library-wide)

ライブラリ横断の重い処理は、必ずターン分割で実行する。

### Turn 1 (start)
1. mainで対象範囲を確定
2. `sessions_spawn` で解析ジョブ起動
3. `scripts/run_state.py upsert` で `run_id/session_key/task` を保存
4. ユーザーには「解析開始」を返し、通常チャットを継続

### Turn 2 (completion)
1. subagent完了通知を受ける
2. 結果JSONを保存
3. `scripts/handle_completion.py --run-id ... --result-json ...` で完了処理
4. mainで提案要約を返す（必要時のみapply）

run state file:
- `state/runs.json`

## PDF extraction policy

1. `ebook-convert` を先に試す
2. 空/失敗時は `pdftotext` にフォールバック
3. 両方失敗なら web-evidence-first に切替

## Sort reading policy

- 日本語sortはユーザー設定の `reading_script` を使用
  - `katakana` / `hiragana` / `latin`
- 初回のみ確認して永続化し、以後は再利用
- デフォルトはフル読み（省略なし）
- 保存先: `~/.config/calibre-metadata-apply/config.json`
  - key: `reading_script`

## Usage

Dry-run:

```bash
cat changes.jsonl | python3 skills/calibre-metadata-apply/scripts/calibredb_apply.py \
  --with-library "http://127.0.0.1:8080/#MyLibrary" \
  --lang ja
```

Apply:

```bash
cat changes.jsonl | python3 skills/calibre-metadata-apply/scripts/calibredb_apply.py \
  --with-library "http://127.0.0.1:8080/#MyLibrary" \
  --apply
```

## Do not

- 曖昧タイトルだけで直接 `--apply` しない
- 未確認IDを混ぜて適用しない
- 低確信候補を無断で埋めない
