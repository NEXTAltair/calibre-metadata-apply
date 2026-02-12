# calibre-metadata-apply

Apply metadata updates to existing Calibre books via `calibredb` over a Content server.

## Setup

1. Install Calibre on the machine where this script will run.
   - Required binary: `calibredb`
2. Ensure `calibredb` is on `PATH`.
3. Ensure Calibre Content server is reachable (host/port).
4. Use `--with-library` in this format:
   - `http://HOST:PORT/#LIBRARY_ID`
   - Always set explicit `HOST:PORT`; do not rely on localhost defaults.
5. If auth is enabled, pass:
   - `--username <user>`
   - `--password-env <ENV_VAR>`

## Important

OpenClaw being installed is not enough by itself. The runtime executing this skill also needs access to `calibredb`.

On Windows, metadata writes can fail if the Calibre library path is protected by Microsoft Defender Controlled Folder Access (or equivalent security controls).
If write calls fail with path/access errors (for example WinError 2/5), add the Calibre library folder and/or Calibre binaries to the allow/exception list.

## Safety model

- JSONL input (one update per line)
- `id` is required
- default is dry-run; add `--apply` to execute writes

## Quick test (dry-run)

```bash
cat references/changes.example.jsonl | python3 scripts/calibredb_apply.py \
  --with-library "http://127.0.0.1:8080/#MyLibrary"
```
