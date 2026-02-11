---
name: calibre-metadata-apply
description: Apply metadata updates to existing Calibre books via calibredb over a Content server. Use for controlled title rename and series/series_index updates after IDs are confirmed by a read-only lookup.
---

# calibre-metadata-apply

Write metadata changes to existing books in Calibre.

## Requirements

- `calibredb` available on PATH in the runtime where the script is executed.
- Reachable Calibre Content server URL in `--with-library` format.
- If auth is enabled, pass `--username` and `--password-env`.

## Safety model

- Input is JSONL, one change per line.
- Each line must include `id`.
- Default is dry-run (`--apply` is required to write).

## Supported fields

- `title`
- `authors` (string with `&` separator or array)
- `series`
- `series_index`
- `tags` (string with `,` separator or array)
- `publisher`
- `pubdate` (`YYYY-MM-DD`)
- `languages` (string with `,` separator or array)
- `comments`

## Usage

Dry-run:

```bash
cat changes.jsonl | python3 skills/calibre-metadata-apply/scripts/calibredb_apply.py \
  --with-library "http://127.0.0.1:8080/#MyLibrary"
```

Apply:

```bash
cat changes.jsonl | python3 skills/calibre-metadata-apply/scripts/calibredb_apply.py \
  --with-library "http://127.0.0.1:8080/#MyLibrary" \
  --apply
```

Example JSONL line:

```json
{"id": 123, "title": "New Title", "series": "My Series", "series_index": 4}
```

## Notes

- Run `calibre-catalog-read` first to confirm target IDs.
- This skill is independent from `calibre-catalog-read` (no runtime import dependency).
