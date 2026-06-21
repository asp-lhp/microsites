#!/usr/bin/env python3
"""Insert or update one site entry in sites.json. Used by the `publish` script.

Usage: _upsert.py <slug> <title> <tags_csv>
- If the slug exists, update its title; replace tags only if tags_csv is non-empty.
- If new, append it (defaulting to the "Untagged" tag when none given).
"""
import json
import pathlib
import sys

slug, title, tags_csv = sys.argv[1], sys.argv[2], sys.argv[3]
repo = pathlib.Path(__file__).resolve().parent
path = repo / "sites.json"

sites = json.loads(path.read_text()) if path.exists() else []
tags = [t.strip() for t in tags_csv.split(",") if t.strip()]

entry = next((s for s in sites if s.get("slug") == slug), None)
if entry:
    entry["title"] = title
    if tags:
        entry["tags"] = tags
    elif not entry.get("tags"):
        entry["tags"] = ["Untagged"]
else:
    sites.append({"slug": slug, "title": title, "tags": tags or ["Untagged"]})

sites.sort(key=lambda s: s["slug"])
path.write_text(json.dumps(sites, indent=2) + "\n")
