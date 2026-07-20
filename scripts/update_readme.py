#!/usr/bin/env python3
"""Regenerate the Formulae/Casks tables in README.md from Formula/*.rb and Casks/*.rb.

Run with no arguments; exits non-zero if README.md is missing the markers
this script relies on.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

DESC_RE = re.compile(r'^\s*desc\s+"((?:[^"\\]|\\.)*)"', re.MULTILINE)
HOMEPAGE_RE = re.compile(r'^\s*homepage\s+"((?:[^"\\]|\\.)*)"', re.MULTILINE)


def parse_entries(directory: Path) -> list[tuple[str, str, str]]:
    entries = []
    for path in sorted(directory.glob("*.rb")):
        name = path.stem
        text = path.read_text()
        desc_match = DESC_RE.search(text)
        homepage_match = HOMEPAGE_RE.search(text)
        homepage = homepage_match.group(1) if homepage_match else ""
        source_label = homepage.rstrip("/").rsplit("/", 1)[-1] if homepage else name
        entries.append((name, homepage, source_label))
    return entries


def build_table(entries: list[tuple[str, str, str]], header: str, cask: bool) -> str:
    install_flag = "--cask " if cask else ""
    lines = [f"| {header} | Install | Source |", "| --- | --- | --- |"]
    for name, homepage, source_label in entries:
        install_cmd = f"brew install {install_flag}danielriddell21/tap/{name}"
        source = f"[{source_label}]({homepage})" if homepage else source_label
        lines.append(f"| `{name}` | `{install_cmd}` | {source} |")
    return "\n".join(lines)


def replace_section(content: str, start_marker: str, end_marker: str, table: str) -> str:
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL
    )
    if not pattern.search(content):
        print(f"error: markers {start_marker!r}/{end_marker!r} not found in README.md", file=sys.stderr)
        sys.exit(1)
    replacement = f"{start_marker}\n{table}\n{end_marker}"
    return pattern.sub(replacement, content)


def main() -> None:
    formulae = parse_entries(ROOT / "Formula")
    casks = parse_entries(ROOT / "Casks")

    content = README.read_text()
    content = replace_section(
        content,
        "<!-- FORMULAE_TABLE_START -->",
        "<!-- FORMULAE_TABLE_END -->",
        build_table(formulae, "Formula", cask=False),
    )
    content = replace_section(
        content,
        "<!-- CASKS_TABLE_START -->",
        "<!-- CASKS_TABLE_END -->",
        build_table(casks, "Cask", cask=True),
    )
    README.write_text(content)


if __name__ == "__main__":
    main()
