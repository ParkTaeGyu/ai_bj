#!/usr/bin/env python3
import json
import os
import subprocess
import time
import urllib.parse
import urllib.request
import re


def load_env(path: str) -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def http_get_json(url: str, timeout: int = 15) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "yt-ai-streamer/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read().decode("utf-8")
    return json.loads(data)


def http_post_json(url: str, payload: dict, timeout: int = 30) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "yt-ai-streamer/0.1"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read().decode("utf-8")
    return json.loads(data)


def list_live_chat_messages(api_key: str, live_chat_id: str, page_token: str | None) -> dict:
    params = {
        "key": api_key,
        "liveChatId": live_chat_id,
        "part": "snippet,authorDetails",
    }
    if page_token:
        params["pageToken"] = page_token
    url = "https://www.googleapis.com/youtube/v3/liveChatMessages?" + urllib.parse.urlencode(params)
    return http_get_json(url)


def generate_response(author: str, message: str, bot_name: str, ollama_model: str | None) -> str:
    if ollama_model:
        prompt = (
            f"너는 유튜브 라이브 스트리머 AI야. 한국어로 짧고 친근하게 답변해. "
            f"대화 상대는 시청자 {author}이고, 메시지는: {message}\n"
            f"{bot_name}:"
        )
        payload = {
            "model": ollama_model,
            "prompt": prompt,
            "stream": False,
        }
        try:
            result = http_post_json("http://localhost:11434/api/generate", payload)
            text = result.get("response", "").strip()
            if text:
                return text
        except Exception:
            pass
    return f"안녕하세요 {author}님! 메시지 잘 봤어요: {message}"


def write_overlay(path: str, lines: list[str]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).strip() + "\n")


def speak(text: str, voice: str | None, rate: str | None) -> None:
    cmd = ["say"]
    if voice:
        cmd += ["-v", voice]
    if rate:
        cmd += ["-r", rate]
    cmd.append(text)
    subprocess.run(cmd, check=False)


def main() -> None:
    load_env(os.path.join(os.path.dirname(__file__), ".env"))

    api_key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    live_chat_id = os.environ.get("LIVE_CHAT_ID", "").strip()
    bot_name = os.environ.get("BOT_NAME", "AI")
    overlay_path = os.environ.get("OVERLAY_PATH", os.path.join(os.path.dirname(__file__), "overlay.txt"))
    ollama_model = os.environ.get("OLLAMA_MODEL")
    tone_preset = os.environ.get("TONE_PRESET", "balanced").strip().lower()
    only_when_mentioned = os.environ.get("ONLY_WHEN_MENTIONED", "1") != "0"
    cooldown_sec = int(os.environ.get("RESPONSE_COOLDOWN_SEC", "10"))
    tts_enabled = os.environ.get("TTS_ENABLED", "1") != "0"
    tts_voice = os.environ.get("TTS_VOICE")
    tts_rate = os.environ.get("TTS_RATE")
    min_msg_len = int(os.environ.get("MIN_MESSAGE_LEN", "2"))
    max_msg_len = int(os.environ.get("MAX_MESSAGE_LEN", "200"))
    ignored_prefixes = [p.strip() for p in os.environ.get("IGNORED_PREFIXES", "!/").split(",") if p.strip()]
    ignored_words = [w.strip().lower() for w in os.environ.get("IGNORED_WORDS", "").split(",") if w.strip()]
    per_user_cooldown = int(os.environ.get("PER_USER_COOLDOWN_SEC", "20"))
    response_random_ratio = float(os.environ.get("RESPONSE_RANDOM_RATIO", "1.0"))
    strip_urls = os.environ.get("STRIP_URLS", "1") != "0"

    if not api_key or not live_chat_id:
        raise SystemExit("YOUTUBE_API_KEY 또는 LIVE_CHAT_ID가 필요합니다. .env를 확인하세요.")

    tone_map = {
        "calm": "차분하고 안정적인 말투",
        "balanced": "친근하고 자연스러운 말투",
        "energetic": "텐션 높고 밝은 말투",
    }
    tone_desc = tone_map.get(tone_preset, tone_map["balanced"])

    page_token = None
    last_response_ts = 0.0
    last_user_ts: dict[str, float] = {}
    last_msg_hashes: dict[str, float] = {}
    print("[yt-ai-streamer] 시작합니다.")

    while True:
        try:
            data = list_live_chat_messages(api_key, live_chat_id, page_token)
            page_token = data.get("nextPageToken")
            polling_ms = int(data.get("pollingIntervalMillis", 5000))
            items = data.get("items", [])

            for item in items:
                snippet = item.get("snippet", {})
                author = item.get("authorDetails", {}).get("displayName", "시청자")
                msg = snippet.get("displayMessage", "").strip()
                msg_type = snippet.get("type")
                if msg_type != "textMessageEvent" or not msg:
                    continue

                msg_norm = re.sub(r"\s+", " ", msg).strip()
                if strip_urls:
                    msg_norm = re.sub(r"https?://\\S+", "[링크]", msg_norm, flags=re.IGNORECASE)

                if len(msg_norm) < min_msg_len or len(msg_norm) > max_msg_len:
                    continue

                if any(msg_norm.startswith(p) for p in ignored_prefixes):
                    continue

                lower_msg = msg_norm.lower()
                if any(w in lower_msg for w in ignored_words):
                    continue

                now = time.time()
                last_u = last_user_ts.get(author, 0.0)
                if (now - last_u) < per_user_cooldown:
                    continue

                # Simple dedupe to avoid repeating very similar spam
                msg_key = f"{author}:{lower_msg}"
                last_h = last_msg_hashes.get(msg_key, 0.0)
                if (now - last_h) < max(per_user_cooldown, 30):
                    continue

                mention_ok = (bot_name.lower() in msg.lower()) or not only_when_mentioned
                if response_random_ratio < 1.0:
                    # Randomly skip to reduce spam response frequency
                    if (hash(msg_key) % 100) > int(response_random_ratio * 100):
                        continue
                if mention_ok and (now - last_response_ts) >= cooldown_sec:
                    if ollama_model:
                        # Tone control is applied to the model prompt only.
                        base_msg = msg_norm
                        prompt_hint = f"말투는 {tone_desc}로 해줘."
                        response = generate_response(author, f"{base_msg}\n{prompt_hint}", bot_name, ollama_model)
                    else:
                        response = generate_response(author, msg_norm, bot_name, ollama_model)
                    lines = [
                        f"{author}: {msg_norm}",
                        f"{bot_name}: {response}",
                    ]
                    write_overlay(overlay_path, lines)
                    if tts_enabled:
                        speak(response, tts_voice, tts_rate)
                    print(f"[chat] {author}: {msg}")
                    print(f"[bot] {response}")
                    last_response_ts = now
                    last_user_ts[author] = now
                    last_msg_hashes[msg_key] = now

            time.sleep(max(polling_ms, 1000) / 1000.0)
        except Exception as exc:
            print(f"[error] {exc}")
            time.sleep(5)


if __name__ == "__main__":
    main()
