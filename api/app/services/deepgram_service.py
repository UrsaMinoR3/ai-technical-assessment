import httpx

from ..core.config import settings

_DEEPGRAM_STT_URL = "https://api.deepgram.com/v1/listen"
_DEEPGRAM_TTS_URL = "https://api.deepgram.com/v1/speak"
_TIMEOUT = 120.0


def _headers() -> dict:
    return {"Authorization": f"Token {settings.deepgram_api_key}"}


def transcribe_audio_sync(audio_bytes: bytes, mimetype: str) -> dict:
    params = {
        "model": "nova-2",
        "detect_language": "true",
        "diarize": "true",
        "smart_format": "true",
        "punctuate": "true",
    }
    headers = {**_headers(), "Content-Type": mimetype}
    with httpx.Client(timeout=_TIMEOUT) as client:
        response = client.post(
            _DEEPGRAM_STT_URL,
            params=params,
            headers=headers,
            content=audio_bytes,
        )
    response.raise_for_status()
    return response.json()


def synthesize_speech_sync(text: str, voice: str) -> tuple[bytes, int]:
    params = {"model": voice, "encoding": "mp3"}
    headers = {**_headers(), "Content-Type": "application/json"}
    with httpx.Client(timeout=_TIMEOUT) as client:
        response = client.post(
            _DEEPGRAM_TTS_URL,
            params=params,
            headers=headers,
            json={"text": text},
        )
    response.raise_for_status()
    return response.content, len(text)
