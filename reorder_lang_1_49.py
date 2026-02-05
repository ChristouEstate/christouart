#!/usr/bin/env python3
from pathlib import Path
import re

START, END = 1, 49

TEXTBLOCK_RE = re.compile(r'(<div\s+class="text-block"\s*>)(.*?)(</div>)', re.DOTALL | re.IGNORECASE)

# Recognize multiple marker styles
EN_TAG_RE = re.compile(r'(<p[^>]*>\s*<strong[^>]*>\s*EN:\s*</strong>\s*</p>|<div[^>]*class="label"[^>]*>\s*EN:\s*</div>|<strong[^>]*>\s*EN:\s*</strong>)', re.IGNORECASE | re.DOTALL)
DE_TAG_RE = re.compile(r'(<p[^>]*>\s*<strong[^>]*>\s*DE:\s*</strong>\s*</p>|<div[^>]*class="label"[^>]*>\s*DE:\s*</div>|<strong[^>]*>\s*DE:\s*</strong>)', re.IGNORECASE | re.DOTALL)

HR_RE = re.compile(r'<hr\s*/?>', re.IGNORECASE)

def pick_filename(i: int) -> Path | None:
    candidates = [Path(f"image{i}.html"), Path(f"image{i:02d}.html")]
    for c in candidates:
        if c.exists():
            return c
    return None

def find_marker(inner: str, which: str):
    if which == "EN":
        m = EN_TAG_RE.search(inner)
        if m: return m.start()
        m2 = re.search(r'\bEN:\b', inner, flags=re.IGNORECASE)
        return m2.start() if m2 else None
    else:
        m = DE_TAG_RE.search(inner)
        if m: return m.start()
        m2 = re.search(r'\bDE:\b', inner, flags=re.IGNORECASE)
        return m2.start() if m2 else None

def strip_boundary_hr(s: str, *, leading=False, trailing=False) -> str:
    if leading:
        s = re.sub(r'^\s*(<hr\s*/?>\s*)+', '', s, flags=re.IGNORECASE)
    if trailing:
        s = re.sub(r'(\s*<hr\s*/?>\s*)+\s*$', '', s, flags=re.IGNORECASE)
    return s.strip()

def process_file(p: Path):
    html = p.read_text(encoding="utf-8", errors="ignore")
    m = TEXTBLOCK_RE.search(html)
    if not m:
        return False, "no text-block"

    open_div, inner, close_div = m.groups()

    en_i = find_marker(inner, "EN")
    de_i = find_marker(inner, "DE")
    if en_i is None or de_i is None:
        return False, "missing EN/DE marker"

    # Split based on order
    if en_i < de_i:
        en_part = inner[en_i:de_i]
        de_part = inner[de_i:]
    else:
        de_part = inner[de_i:en_i]
        en_part = inner[en_i:]

    # Clean boundary hrs to avoid duplicates
    en_part = strip_boundary_hr(en_part, trailing=True)
    de_part = strip_boundary_hr(de_part, leading=True)

    new_inner = f"{en_part}\n      <hr />\n      {de_part}"
    new_block = f"{open_div}\n      {new_inner.strip()}\n    {close_div}"

    new_html = html[:m.start()] + new_block + html[m.end():]
    if new_html != html:
        p.write_text(new_html, encoding="utf-8")
        return True, None
    return False, "already ok/no change"

def main():
    changed = 0
    missing = 0
    failed = 0
    failed_files = []

    for i in range(START, END + 1):
        p = pick_filename(i)
        if p is None:
            missing += 1
            continue

        ok, reason = process_file(p)
        if ok:
            changed += 1
        else:
            # Count as failed only for real parse problems
            if reason in ("no text-block", "missing EN/DE marker"):
                failed += 1
                failed_files.append(f"{p.name}: {reason}")

    print(f"Done. Changed: {changed}, missing: {missing}, failed: {failed}")
    if failed_files:
        print("\nFailed files:")
        for line in failed_files:
            print("  " + line)

if __name__ == "__main__":
    main()
