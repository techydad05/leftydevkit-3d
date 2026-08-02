#!/usr/bin/env python3
import sys, json
from youtube_transcript_api import YouTubeTranscriptApi

vid = "Q7AOvWpIVHU"
try:
    api = YouTubeTranscriptApi()
    l = api.list(vid)
    # prefer manual english
    try: tr = api.fetch(vid, languages=['en'])
    except Exception:
        tr = l.find_transcript(['en']) if hasattr(l,'find_transcript') else api.fetch(vid)
    out = []
    for s in tr:
        t = int(s.start)
        m, sec = divmod(t, 60)
        out.append(f"[{m:02d}:{sec:02d}] {s.text}")
    print("\n".join(out))
except Exception as e:
    print("ERR", type(e).__name__, e)
