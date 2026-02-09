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


def main() -> None:
    parser = argparse.ArgumentParser(description="Get activeLiveChatId from a live video ID.")
    parser.add_argument("--api-key", dest="api_key", default=os.environ.get("YOUTUBE_API_KEY", ""))
    parser.add_argument("--video-id", dest="video_id", default=os.environ.get("VIDEO_ID", ""))
    args = parser.parse_args()

    api_key = args.api_key.strip()
    video_id = args.video_id.strip()

    if not api_key or not video_id:
        print("YOUTUBE_API_KEY(또는 --api-key)와 VIDEO_ID(또는 --video-id)가 필요합니다.", file=sys.stderr)
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
