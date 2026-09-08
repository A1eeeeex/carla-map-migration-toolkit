"""Check manifest-listed Markdown relative file links and heading anchors."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


def heading_ids(text: str) -> set[str]:
    counts: dict[str, int] = {}
    result: set[str] = set()
    for title in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.MULTILINE):
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        number = counts.get(slug, 0)
        result.add(f"{slug}-{number}" if number else slug)
        counts[slug] = number + 1
    return result


def check_links(root: Path, files: list[str]) -> list[str]:
    root = root.resolve()
    failures: list[str] = []
    for name in files:
        if not name.endswith(".md"):
            continue
        path = root / name
        if not path.is_file():
            failures.append(f"{name}: document missing")
            continue
        text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)
        for target in re.findall(r"\]\(([^)]+)\)", text):
            url = urlsplit(target.strip("<>"))
            if url.scheme or url.netloc:
                continue
            resolved = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not resolved.is_relative_to(root) or not resolved.exists():
                failures.append(f"{name}: missing or outside repository: {target}")
            elif url.fragment and resolved.suffix == ".md":
                if unquote(url.fragment) not in heading_ids(resolved.read_text(encoding="utf-8")):
                    failures.append(f"{name}: missing heading: {target}")
    return failures


def main() -> int:
    root = Path(__file__).resolve().parents[3]
    files = json.loads((root / "PUBLICATION_ALLOWLIST.json").read_text(encoding="utf-8"))["files"]
    failures = check_links(root, files)
    print(json.dumps({"status": "FAIL" if failures else "PASS", "failures": failures}, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
