#!/usr/bin/env python3
"""
Fetch soccer M3U from Cloudflare Worker and write THETVAPP-SOCCER.M3U
in the repo root.
"""

from pathlib import Path
import sys
import urllib.request

# Worker URL – must use format=m3u for a real playlist file
SOURCE_URL = (
    "https://thetvapp.mmonterrosa970.workers.dev/"
    "?url=https://thetvapp.plus/watch/soccer-streams"
    "&format=m3u"
)

# Output file in the repository root
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "THETVAPP-SOCCER.M3U"

TIMEOUT_SECONDS = 120


def main() -> int:
    print(f"Fetching: {SOURCE_URL}")
    try:
        req = urllib.request.Request(
            SOURCE_URL,
            headers={
                "User-Agent": "GitHubActions-TheTVApp-M3U-Updater/1.0",
                "Accept": "text/plain, application/vnd.apple.mpegurl, */*",
            },
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"ERROR: failed to fetch playlist: {e}", file=sys.stderr)
        return 1

    body = body.strip() + "\n"

    if not body.startswith("#EXTM3U"):
        print("ERROR: response does not look like an M3U playlist", file=sys.stderr)
        print(body[:500], file=sys.stderr)
        return 1

    # Count channels (lines that are not empty and not comments)
    channel_count = sum(
        1
        for line in body.splitlines()
        if line.strip() and not line.strip().startswith("#")
    )
    print(f"Playlist OK – {channel_count} stream URL(s)")

    OUTPUT_FILE.write_text(body, encoding="utf-8")
    print(f"Wrote: {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
