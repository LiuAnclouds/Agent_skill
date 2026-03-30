#!/usr/bin/env python3
"""Compatibility wrapper for the merged article-note-mentor finalization script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    current = Path(__file__).resolve()
    target = (
        current.parents[2]
        / "article-note-mentor"
        / "scripts"
        / "feishu_docx_finalize.py"
    )
    if not target.exists():
        print(
            "ERROR: article-note-mentor/scripts/feishu_docx_finalize.py was not found.",
            file=sys.stderr,
        )
        return 1
    print(
        "NOTICE: article-note-feishu-polish has been merged into article-note-mentor. "
        "Forwarding this command to the unified finalization script.",
        file=sys.stderr,
    )
    result = subprocess.run([sys.executable, str(target), *sys.argv[1:]], check=False)
    return int(result.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
