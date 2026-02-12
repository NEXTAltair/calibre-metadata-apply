---
name: calibre-metadata-apply
description: Apply metadata updates to existing Calibre books via calibredb over a Content server. Use for controlled title rename and series/series_index updates after IDs are confirmed by a read-only lookup.
---

# calibre-metadata-apply

Write metadata changes to existing books in Calibre.

## Requirements

- `calibredb` available on PATH in the runtime where the script is executed.
  - Practically, this means Calibre must be installed on that runtime (or `calibredb` provided separately).
- Reachable Calibre Content server URL in `--with-library` format.
- Do not assume localhost/127.0.0.1.
  - Always provide an explicit reachable `HOST:PORT` for your network path (for example from WSL to Windows host).
- If auth is enabled, pass `--username` and `--password-env`.

## Safety model

- Input is JSONL, one change per line.
- Each line must include `id`.
- Default is dry-run (`--apply` is required to write).
- Never apply directly from ambiguous title guesses. Confirm target IDs first.

## Target narrowing + confirmation flow (required)

Always run this sequence before `--apply`:

1. **Read-only candidate search**
   - Search by user instruction (title/author/series keywords).
   - Build candidate list with: `id`, `title`, `authors`, `series`, `series_index`.
2. **User confirmation gate (mandatory)**
   - Show candidate list and ask:
     - Is this list sufficient?
     - Any missing books to add?
     - Any extra books to exclude?
   - Request explicit final target IDs (example: `apply ids: 3,4`).
3. **Prepare JSONL only for confirmed IDs**
4. **Dry-run and show planned commands**
5. **Apply only after explicit user OK**
6. **Post-apply verification**
   - Re-read same targets and report final values.

If target IDs are not explicitly confirmed, stop at dry-run.

## Supported fields

### Direct Calibre fields (`set_metadata --field`)

- `title`
- `authors` (string with `&` separator or array)
- `series`
- `series_index`
- `tags` (string with `,`/`;` separator or array; deduped)
- `publisher`
- `pubdate` (`YYYY-MM-DD`)
- `languages` (string with `,`/`;` separator or array)
- `comments`

### Extended helper fields (tool-side)

- `comments_html`: HTML block to upsert into `comments` using marker block:
  - `<!-- OC_ANALYSIS_START --> ... <!-- OC_ANALYSIS_END -->`
- `analysis`: structured object to auto-render HTML summary + reread guide into comments.
  - Language follows `analysis.lang` when provided (`ja`/`en`), otherwise CLI default `--lang` (default: `ja`).
- `analysis_tags`: extra tags to merge into `tags`.
- `tags_merge` (default `true`): merge with existing Calibre tags instead of replacing.

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

Example JSONL lines:

```json
{"id": 123, "title": "New Title", "series": "My Series", "series_index": 4, "tags": ["tech", "to-read"]}
{"id": 124, "analysis": {"summary": "Chapter 3 design guidance is practical.", "highlights": ["Cache strategy", "Rollback flow"], "reread": [{"section": "Chapter 3", "page": "45-62", "chunk_id": "c3p45", "reason": "Review before implementation"}], "tags": ["reread", "ai-summary"], "file_hash": "sha256:..."}}
```

## Notes

- Run `calibre-catalog-read` first to confirm target IDs.
- This skill is independent from `calibre-catalog-read` (no runtime import dependency).
