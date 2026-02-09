#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request


def http_get_json(url: str, timeout: int = 15) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "yt-ai-streamer/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read().decode("utf-8")
    return json.loads(data)


def extract_video_id(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    # Direct ID
    if len(value) >= 6 and all(c.isalnum() or c in "-_" for c in value):
        # Might be an ID or a URL; if it looks like a URL, parse it below.
        if not value.startswith("http"):
            return value
    # URL cases
    try:
        parsed = urllib.parse.urlparse(value)
        if parsed.netloc in ("youtu.be", "www.youtu.be"):
            return parsed.path.strip("/").split("/")[0]
        if "youtube.com" in parsed.netloc:
            qs = urllib.parse.parse_qs(parsed.query)
            if "v" in qs and qs["v"]:
                return qs["v"][0]
            # Shorts and live URLs: /shorts/{id}, /live/{id}
            parts = [p for p in parsed.path.split("/") if p]
            if len(parts) >= 2 and parts[0] in ("shorts", "live"):
                return parts[1]
    except Exception:
        return ""
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Get activeLiveChatId from a live video ID.")
    parser.add_argument("--api-key", dest="api_key", default=os.environ.get("YOUTUBE_API_KEY", ""))
    parser.add_argument("--video-id", dest="video_id", default=os.environ.get("VIDEO_ID", ""))
    parser.add_argument(
        "--url",
        dest="video_url",
        default=os.environ.get("VIDEO_URL", ""),
        help="YouTube video URL (v=, youtu.be, /live/, /shorts/).",
    )
    args = parser.parse_args()

    api_key = args.api_key.strip()
    video_id = extract_video_id(args.video_id) or extract_video_id(args.video_url)

    if not api_key or not video_id:
        print(
            "YOUTUBE_API_KEY(또는 --api-key)와 VIDEO_ID(--video-id) 또는 URL(--url)가 필요합니다.",
            file=sys.stderr,
        )
        sys.exit(1)

    params = {"part": "liveStreamingDetails", "id": video_id, "key": api_key}
    url = "https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode(params)
    data = http_get_json(url)

    items = data.get("items", [])
    if not items:
        print("해당 VIDEO_ID의 정보를 찾지 못했습니다. 영상 ID를 확인하세요.", file=sys.stderr)
        sys.exit(2)

    live_details = items[0].get("liveStreamingDetails", {}) or {}
    live_chat_id = live_details.get("activeLiveChatId")
    if not live_chat_id:
        print("activeLiveChatId가 없습니다. 라이브가 진행 중인지 확인하세요.", file=sys.stderr)
        sys.exit(3)

    print(live_chat_id)


if __name__ == "__main__":
    main()
