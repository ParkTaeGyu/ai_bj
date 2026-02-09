# yt_ai_streamer (macOS, 무료 위주)

유튜브 라이브 채팅을 읽고, AI 응답을 **OBS 텍스트 오버레이**로 보여주는 최소 동작 프로토타입입니다.

## 1) 준비물
- Python 3.10+
- YouTube Data API v3 키
- (선택) 로컬 LLM: Ollama
- (선택) 가상 오디오: BlackHole (OBS로 음성 라우팅)

## 2) 설정
```bash
cd /Users/parktaekyu/Documents/ai_bj/yt_ai_streamer
cp .env.example .env
```
`.env`를 열어 아래 값을 채우세요.
- `YOUTUBE_API_KEY`
- `LIVE_CHAT_ID`

### LIVE_CHAT_ID 얻는 방법 (요약)
YouTube Data API의 `liveBroadcasts.list` 또는 `videos.list`로 현재 라이브의 `liveChatId`를 확인합니다.

## 3) 실행
```bash
python3 main.py
```

## 4) OBS에 텍스트 오버레이 연결
OBS에서 `텍스트(FreeType 2)` 소스를 추가하고, 텍스트 내용을 `overlay.txt` 파일로 연결하세요.

## 4-1) 음성(TTS) 라우팅 (BlackHole 권장)
1. BlackHole 설치 후 `Audio MIDI Setup`에서 **Multi-Output Device**를 만듭니다.
2. 출력 장치에 **스피커 + BlackHole**를 함께 체크합니다.
3. macOS 시스템 출력 장치를 그 Multi-Output으로 설정합니다.
4. OBS에서 **오디오 입력 캡처**로 BlackHole을 추가합니다.

## 5) Ollama 사용 (선택)
Ollama를 설치하고 모델을 받아둔 뒤 `.env`에 `OLLAMA_MODEL`을 넣으면 로컬 LLM 응답을 생성합니다.
예: `OLLAMA_MODEL=llama3.1:8b`

### 말투 프리셋 (Ollama 사용 시)
`.env`에 `TONE_PRESET`을 추가하면 말투를 조절합니다.
- `calm` (차분)
- `balanced` (기본)
- `energetic` (텐션업)

## 6) TTS 설정 (macOS 기본 `say`)
`.env`에서 아래 옵션을 설정하세요.
- `TTS_ENABLED=1` (기본 ON)
- `TTS_VOICE=Yuna` (예시)
- `TTS_RATE=180` (말하기 속도)
사용 가능한 음성 목록은 터미널에서 `say -v ?`로 확인합니다.

## 7) 채팅 필터/쿨다운 튜닝
`.env`에서 아래 값을 조정하면 스팸/도배를 줄일 수 있습니다.
- `MIN_MESSAGE_LEN` / `MAX_MESSAGE_LEN`: 너무 짧거나 긴 메시지 제외
- `IGNORED_PREFIXES`: 명령어/봇 트리거 접두어 무시 (예: `!`, `/`)
- `IGNORED_WORDS`: 특정 단어 포함 메시지 무시 (콤마 구분)
- `PER_USER_COOLDOWN_SEC`: 유저별 응답 쿨다운
- `RESPONSE_RANDOM_RATIO`: 응답 확률 (1.0=항상, 0.5=절반)
- `STRIP_URLS`: URL이 포함된 메시지를 `\[링크]`로 대체

## 동작 방식
- 채팅 메시지를 폴링합니다.
- 봇 이름이 포함된 메시지에만 응답합니다 (기본값).
- 최신 질문/응답 1쌍을 `overlay.txt`에 기록합니다.
- 응답을 macOS TTS로 음성 출력합니다.

## 참고
- 유튜브 채팅에 **직접 답글을 보내는 기능**은 OAuth 설정이 필요합니다. 이 프로토타입은 오버레이 출력까지만 포함합니다.
