#!/usr/bin/env python3
"""
Fetch one or more M3U playlists and write them into the repo root.

Edit PLAYLISTS below to add/remove/change sources.
"""

from pathlib import Path
import sys
import urllib.request

# =============================================================================
# EDIT THIS LIST
# Each entry needs:
#   "url"      = full URL that returns an M3U
#   "filename" = file name in the repo root
# =============================================================================
PLAYLISTS = [
    {
        "url": "https://thetvapp.mmonterrosa970.workers.dev/?url=https://thetvapp.plus/watch/soccer-streams&format=m3u",
        "filename": "THETVAPP-SOCCER.m3u",
    },
    {
        "url": "https://thetvapp.mmonterrosa970.workers.dev/?url=https://thetvapp.plus/watch/mma-streams&format=m3u",
        "filename": "THETVAPP-MMA.m3u",
    },
    {
        "url": "https://fctv33.mmonterrosa970.workers.dev/?url=https://www.fctv33hd.icu/football.html&format=m3u",
        "filename": "FCTV33-FOOTBALL.m3u",
    },
    # Add more like this (copy the block, change url + filename):
    # {
    #     "url": "https://thetvapp.mmonterrosa970.workers.dev/?url=https://thetvapp.plus/watch/cfb-streams&format=m3u",
    #     "filename": "THETVAPP-CFB.M3U",
    # },
]

# scripts/updater.py → parent = scripts/ → parent.parent = repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
TIMEOUT_SECONDS = 120
USER_AGENT = "GitHubActions-LIVESPORTS-LISTS-AUTOUPDATER/1.0"


def fetch_m3u(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/plain, application/vnd.apple.mpegurl, */*",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        return resp.read().decode("utf-8", errors="replace")


def update_one(url: str, filename: str) -> bool:
    print(f"\n--- {filename} ---")
    print(f"Fetching: {url}")

    try:
        body = fetch_m3u(url)
    except Exception as e:
        print(f"ERROR: fetch failed: {e}", file=sys.stderr)
        return False

    body = body.strip() + "\n"

    if not body.startswith("#EXTM3U"):
        print("ERROR: response is not an M3U playlist", file=sys.stderr)
        print(body[:500], file=sys.stderr)
        return False

    channel_count = sum(
        1
        for line in body.splitlines()
        if line.strip() and not line.strip().startswith("#")
    )
    print(f"OK – {channel_count} stream URL(s)")

    out = REPO_ROOT / filename
    out.write_text(body, encoding="utf-8")
    print(f"Wrote: {out.resolve()}")
    return True


def main() -> int:
    print(f"Repo root: {REPO_ROOT.resolve()}")

    if not PLAYLISTS:
        print("ERROR: PLAYLISTS list is empty", file=sys.stderr)
        return 1

    ok = 0
    failed = 0
    written = []

    for entry in PLAYLISTS:
        url = (entry.get("url") or "").strip()
        filename = (entry.get("filename") or "").strip()

        if not url or not filename:
            print("ERROR: each entry needs url and filename", file=sys.stderr)
            failed += 1
            continue

        if "/" in filename or "\\" in filename or filename in (".", ".."):
            print(f"ERROR: invalid filename: {filename}", file=sys.stderr)
            failed += 1
            continue

        if update_one(url, filename):
            ok += 1
            written.append(filename)
        else:
            failed += 1

    print(f"\nDone. success={ok} failed={failed}")
    if written:
        print("Files written:", ", ".join(written))
    if ok == 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
