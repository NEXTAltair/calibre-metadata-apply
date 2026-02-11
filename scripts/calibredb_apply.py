#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from typing import Any

ALLOWED = {
    "title", "authors", "series", "series_index", "tags", "publisher", "pubdate", "languages", "comments"
}


def run(cmd: list[str]) -> tuple[int, str, str]:
    cp = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return cp.returncode, cp.stdout, cp.stderr


def common_args(ns: argparse.Namespace) -> list[str]:
    args = ["--with-library", ns.with_library]
    if ns.username:
        args += ["--username", ns.username]
    if ns.password_env:
        pw = os.environ.get(ns.password_env, "")
        if pw:
            args += ["--password", pw]
    return args


def to_field_value(v: Any) -> str:
    if isinstance(v, list):
        return ",".join(str(x) for x in v)
    return str(v)


def build_set_metadata_cmd(ns: argparse.Namespace, rec: dict[str, Any]) -> list[str]:
    bid = str(rec.get("id", "")).strip()
    if not bid:
        raise ValueError("missing id")

    fields = []
    for k, v in rec.items():
        if k == "id":
            continue
        if k not in ALLOWED:
            continue
        if v is None:
            continue
        fields += ["--field", f"{k}:{to_field_value(v)}"]

    if not fields:
        raise ValueError("no updatable fields")

    return ["calibredb", "set_metadata", bid] + fields + common_args(ns)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-library", required=True)
    ap.add_argument("--username")
    ap.add_argument("--password-env", default="CALIBRE_PASSWORD")
    ap.add_argument("--apply", action="store_true")
    ns = ap.parse_args()

    lines = [ln.strip() for ln in sys.stdin.read().splitlines() if ln.strip()]
    if not lines:
        print(json.dumps({"ok": True, "summary": {"total": 0, "planned": 0, "applied": 0, "failed": 0}, "results": []}, ensure_ascii=False, indent=2))
        return 0

    results = []
    planned = 0
    applied = 0
    failed = 0

    for i, ln in enumerate(lines, start=1):
        try:
            rec = json.loads(ln)
            cmd = build_set_metadata_cmd(ns, rec)
            planned += 1

            if not ns.apply:
                results.append({"line": i, "id": rec.get("id"), "action": "planned", "cmd": " ".join(shlex.quote(x) for x in cmd)})
                continue

            rc, out, err = run(cmd)
            if rc == 0:
                applied += 1
                results.append({"line": i, "id": rec.get("id"), "action": "applied", "stdout": out.strip()})
            else:
                failed += 1
                results.append({"line": i, "id": rec.get("id"), "action": "failed", "stderr": err.strip(), "rc": rc})
        except Exception as e:
            failed += 1
            results.append({"line": i, "action": "error", "error": str(e)})

    ok = failed == 0
    print(json.dumps({
        "ok": ok,
        "mode": "apply" if ns.apply else "dry-run",
        "summary": {"total": len(lines), "planned": planned, "applied": applied, "failed": failed},
        "results": results,
    }, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
