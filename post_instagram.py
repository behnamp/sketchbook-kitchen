#!/usr/bin/env python3
"""Publishes today's Instagram post from posts.json. Runs daily on GitHub Actions.
Needs repository secrets IG_USER_ID and IG_TOKEN; without them it exits quietly."""
import datetime, json, os, sys, time, urllib.parse, urllib.request
from zoneinfo import ZoneInfo
uid, tok = os.environ.get("IG_USER_ID", ""), os.environ.get("IG_TOKEN", "")
if not uid or not tok:
    print("Instagram secrets not set yet; nothing to do."); sys.exit(0)
day = os.environ.get("POST_DATE") or datetime.datetime.now(ZoneInfo("America/Toronto")).date().isoformat()
post = next((p for p in json.load(open("posts.json")) if p["date"] == day), None)
if not post:
    print("No post scheduled for", day); sys.exit(0)
API = "https://graph.facebook.com/v21.0"
def call(path, **data):
    body = urllib.parse.urlencode({**data, "access_token": tok}).encode()
    with urllib.request.urlopen(urllib.request.Request(f"{API}/{path}", data=body), timeout=60) as r:
        return json.load(r)
media = call(f"{uid}/media", image_url=post["image_url"], caption=post["caption"])
for _ in range(20):            # wait until Instagram has fetched the image
    time.sleep(6)
    with urllib.request.urlopen(f"{API}/{media['id']}?fields=status_code&access_token={tok}", timeout=60) as q:
        if json.load(q).get("status_code") == "FINISHED": break
print("Published", day, call(f"{uid}/media_publish", creation_id=media["id"]))
