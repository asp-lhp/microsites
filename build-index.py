#!/usr/bin/env python3
"""Regenerate index.html from sites.json as a 90's corkboard / bulletin board.

Pages are grouped by tag. A page with multiple tags is pinned under each.
Run automatically by the `publish` script; safe to run by hand too.
"""
import html
import json
import datetime
import pathlib

REPO = pathlib.Path(__file__).resolve().parent
sites = []
sp = REPO / "sites.json"
if sp.exists():
    sites = json.loads(sp.read_text())

# Group by tag (a page can appear under several tags).
by_tag = {}
for s in sites:
    for t in (s.get("tags") or ["Untagged"]):
        by_tag.setdefault(t, []).append(s)
for t in by_tag:
    by_tag[t].sort(key=lambda s: s["title"].lower())
ordered_tags = sorted(by_tag.keys(), key=str.lower)

NOTE_COLORS = ["#fff89a", "#ffd6e8", "#c7f5c0", "#bfe3ff", "#ffd8a8", "#e3d0ff"]
PIN_COLORS = ["#e74c3c", "#2d7bd4", "#27ae60", "#e67e22", "#8e44ad"]

updated = datetime.date.today().strftime("%B&nbsp;%d,&nbsp;%Y")
total = len(sites)

NOTE_TPL = """
        <a class="note" href="{slug}/" style="--note:{color}; --pin:{pin}; transform: rotate({rot}deg);">
          <span class="pin"></span>
          <span class="note-title">{title}</span>
          <span class="note-path">/{slug}/</span>
        </a>"""

SECTION_TPL = """
      <section class="board-section">
        <h2 class="tag-label">{label}</h2>
        <div class="notes">{notes}</div>
      </section>"""

ci = 0
sections_html = ""
for t in ordered_tags:
    notes_html = ""
    for s in by_tag[t]:
        color = NOTE_COLORS[ci % len(NOTE_COLORS)]
        pin = PIN_COLORS[ci % len(PIN_COLORS)]
        rot = (ci * 41 % 7) - 3  # deterministic tilt in [-3, 3]
        ci += 1
        notes_html += NOTE_TPL.format(
            slug=html.escape(s["slug"], quote=True),
            color=color, pin=pin, rot=rot,
            title=html.escape(s["title"]),
        )
    sections_html += SECTION_TPL.format(label=html.escape(t), notes=notes_html)

if not sites:
    sections_html = (
        '\n      <section class="board-section"><p class="empty">'
        'No pages pinned yet. Publish one to see it here!</p></section>'
    )

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Andre's Microsites</title>
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: "Comic Sans MS", "Chalkboard SE", "Segoe Print", cursive, sans-serif;
    color: #2b2b2b;
    background-color: #b07e4f;
    background-image:
      radial-gradient(rgba(0,0,0,.16) 1px, transparent 1.4px),
      radial-gradient(rgba(255,255,255,.07) 1px, transparent 1.4px);
    background-size: 7px 7px, 7px 7px;
    background-position: 0 0, 3px 4px;
    padding: 22px;
  }
  .frame {
    max-width: 1100px;
    margin: 0 auto;
    border: 16px solid #6b4423;
    border-radius: 6px;
    box-shadow: 0 0 0 3px #3d2616, inset 0 0 80px rgba(0,0,0,.28), 0 22px 50px rgba(0,0,0,.5);
    background: rgba(176,126,79,.25);
    padding: 26px 26px 40px;
  }
  .banner {
    background: repeating-linear-gradient(45deg, #fffbe6, #fffbe6 12px, #fff3b0 12px, #fff3b0 24px);
    border: 3px solid #333;
    box-shadow: 5px 5px 0 rgba(0,0,0,.45);
    text-align: center;
    padding: 16px 12px 14px;
    margin: 4px auto 10px;
    max-width: 720px;
    transform: rotate(-1.2deg);
    position: relative;
  }
  .banner::before, .banner::after {
    content: ""; position: absolute; top: -9px; width: 16px; height: 16px;
    background: #c0392b; border-radius: 50%; box-shadow: inset -2px -2px 3px rgba(0,0,0,.4);
  }
  .banner::before { left: 14px; }
  .banner::after { right: 14px; }
  .banner h1 {
    margin: 0; font-family: Impact, "Haettenschweiler", "Arial Black", sans-serif;
    font-size: clamp(1.9rem, 6vw, 3.2rem); letter-spacing: 1px;
    color: #1d6b3a; text-shadow: 2px 2px 0 #fff, 4px 4px 0 rgba(0,0,0,.2);
  }
  .marquee {
    overflow: hidden; white-space: nowrap; max-width: 720px; margin: 0 auto 26px;
    color: #fff; font-weight: bold; text-shadow: 1px 1px 0 #000;
  }
  .marquee span { display: inline-block; padding-left: 100%; animation: scroll 16s linear infinite; }
  @keyframes scroll { to { transform: translateX(-100%); } }
  .board-section { margin: 0 0 30px; }
  .tag-label {
    display: inline-block; margin: 0 0 14px;
    background: #2d7bd4; color: #fff; font-family: "Courier New", monospace;
    font-weight: bold; font-size: 1.15rem; letter-spacing: .5px;
    padding: 7px 16px; border: 3px solid #14406f;
    box-shadow: 4px 4px 0 rgba(0,0,0,.4); transform: rotate(-1deg);
    text-transform: uppercase;
  }
  .tag-label::before { content: "\\1F4CC  "; }
  .notes { display: flex; flex-wrap: wrap; gap: 22px; }
  .note {
    position: relative; display: flex; flex-direction: column; justify-content: center;
    width: 200px; min-height: 130px; padding: 22px 16px 16px;
    background: var(--note); color: #222; text-decoration: none;
    box-shadow: 4px 6px 12px rgba(0,0,0,.4);
    transition: transform .12s ease, box-shadow .12s ease;
  }
  .note:hover {
    transform: rotate(0deg) scale(1.05) !important;
    box-shadow: 6px 10px 18px rgba(0,0,0,.5); z-index: 3;
  }
  .pin {
    position: absolute; top: -9px; left: 50%; margin-left: -9px;
    width: 18px; height: 18px; border-radius: 50%;
    background: radial-gradient(circle at 35% 30%, #fff7, var(--pin) 45%, rgba(0,0,0,.4));
    box-shadow: 0 2px 3px rgba(0,0,0,.5);
  }
  .note-title { font-size: 1.12rem; font-weight: bold; line-height: 1.25; }
  .note-path { margin-top: 8px; font-family: "Courier New", monospace; font-size: .72rem; color: #555; }
  .empty { color: #fff; font-size: 1.1rem; }
  .footer {
    margin-top: 30px; padding-top: 16px; border-top: 2px dashed rgba(255,255,255,.5);
    text-align: center; color: #fff2d8; font-size: .85rem; text-shadow: 1px 1px 0 rgba(0,0,0,.4);
  }
  .footer .blink { animation: blink 1s steps(2, start) infinite; color: #ffe14d; font-weight: bold; }
  @keyframes blink { to { visibility: hidden; } }
  .counter {
    display: inline-block; background: #000; color: #2bff5a; font-family: "Courier New", monospace;
    padding: 2px 8px; border: 1px solid #2bff5a; letter-spacing: 3px; margin: 0 4px;
  }
</style>
</head>
<body>
  <div class="frame">
    <div class="banner"><h1>Andre's Microsites</h1></div>
    <div class="marquee"><span>&#9733;&#9733;&#9733; Welcome to my corner of the web &mdash; pin it, share it, surf on! &#9733;&#9733;&#9733;</span></div>
"""

FOOT = """
    <div class="footer">
      <p>You are visitor <span class="counter">000042</span> &middot; Pages pinned: <strong>{total}</strong> &middot; Last updated {updated}</p>
      <p><span class="blink">&#128679; Under Construction &#128679;</span> &middot; Best viewed in Netscape Navigator 4.0 at 800&times;600</p>
    </div>
  </div>
</body>
</html>
""".format(total=total, updated=updated)

(REPO / "index.html").write_text(HEAD + sections_html + FOOT)
print(f"Rebuilt index.html with {total} page(s) across {len(ordered_tags)} tag(s).")
