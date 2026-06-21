#!/usr/bin/env python3
"""Inject a small floating link back to the bulletin board into a published page.

Called by `pin` on the copied index.html (never the source). Idempotent via the
data-board-link marker, and skips the root board itself.
"""
import re
import sys

path = sys.argv[1]
html = open(path, encoding="utf-8").read()

if "data-board-link" in html:
    sys.exit(0)

link = (
    '<a href="../" data-board-link aria-label="Back to all pages" '
    'style="position:fixed;top:14px;right:14px;z-index:9999;'
    "background:rgba(255,255,255,.92);color:#23342f;"
    "font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,sans-serif;"
    "font-weight:700;font-size:14px;text-decoration:none;padding:8px 14px;"
    "border-radius:999px;box-shadow:0 4px 14px rgba(0,0,0,.22);"
    '-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);">← All pages</a>'
)

if re.search(r"</body>", html, re.I):
    html = re.sub(r"</body>", link + "\n</body>", html, count=1, flags=re.I)
else:
    html += link

open(path, "w", encoding="utf-8").write(html)
