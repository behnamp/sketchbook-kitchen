#!/usr/bin/env python3
"""Writes feed.xml for Pinterest auto-publish: one item per day up to today (Toronto time),
from pins.json. Runs daily on GitHub Actions and on every local publish."""
import datetime, html, json, os
from email.utils import format_datetime
from zoneinfo import ZoneInfo
TZ = ZoneInfo("America/Toronto")
here = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(here, "pins.json")))
today = datetime.datetime.now(TZ).date().isoformat()
start = data.get("rss_start") or "0000"
items = [p for p in data["pins"] if start <= p["date"] <= today][-60:]      # newest 60 days is plenty
items = [data["series_item"]] + items if data.get("series_item") else items
def esc(s): return html.escape(str(s), quote=True)
out = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/"><channel>',
       f"<title>{esc(data['title'])}</title><link>{esc(data['site'])}</link>",
       f"<description>{esc(data['description'])}</description><language>en</language>"]
for p in reversed(items):
    when = datetime.datetime.fromisoformat(p["date"] + "T18:00:00").replace(tzinfo=TZ)
    out.append("<item>"
               f"<title>{esc(p['title'])}</title><link>{esc(p['link'])}</link>"
               f"<guid isPermaLink=\"false\">{esc(p['image'])}</guid><pubDate>{format_datetime(when)}</pubDate>"
               f"<description>{esc(p['description'])}</description>"
               f"<enclosure url=\"{esc(p['image'])}\" type=\"image/jpeg\" length=\"0\"/>"
               f"<media:content url=\"{esc(p['image'])}\" medium=\"image\" type=\"image/jpeg\"/>"
               "</item>")
out.append("</channel></rss>")
open(os.path.join(here, "feed.xml"), "w", encoding="utf-8").write("\n".join(out))
print(f"feed.xml: {len(items)} items up to {today}")
