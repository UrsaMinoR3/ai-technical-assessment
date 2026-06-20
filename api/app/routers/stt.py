import asyncio
import time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..core.auth import verify_api_key
from ..core.database import get_db
from ..models.request_log import RequestLog
from ..schemas.stt import SpeakerSegment, STTResponse
from ..services.deepgram_service import transcribe_audio_sync

router = APIRouter()

ALLOWED_MIMETYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/wave",
    "audio/x-wav",
    "audio/vnd.wave",
}


def _group_words_by_speaker(words: list[dict]) -> list[SpeakerSegment]:
    """Group consecutive word dicts (from Deepgram JSON) into speaker segments."""
    if not words:
        return []

    segments: list[SpeakerSegment] = []
    current_speaker = None
    current_words: list[str] = []
    current_start = 0.0
    current_end = 0.0

    for word in words:
        speaker = word.get("speaker")
        if speaker != current_speaker:
            if current_words:
                segments.append(
                    SpeakerSegment(
                        speaker=current_speaker if current_speaker is not None else 0,
                        start=current_start,
                        end=current_end,
                        text=" ".join(current_words),
                    )
                )
            current_speaker = speaker
            current_words = [word.get("word", "")]
            current_start = float(word.get("start", 0))
            current_end = float(word.get("end", 0))
        else:
            current_words.append(word.get("word", ""))
            current_end = float(word.get("end", 0))

    if current_words:
        segments.append(
            SpeakerSegment(
                speaker=current_speaker if current_speaker is not None else 0,
                start=current_start,
                end=current_end,
                text=" ".join(current_words),
            )
        )

    return segments


def _log(db: Session, endpoint: str, input_data: str, output_ref: str,
         usage: str | None, latency_ms: float, http_status: int) -> None:
    db.add(
        RequestLog(
            endpoint=endpoint,
            input_data=input_data,
            output_ref=output_ref[:500] if output_ref else None,
            external_usage=usage,
            latency_ms=latency_ms,
            http_status=http_status,
        )
    )
    db.commit()


@router.post(
    "/stt",
    response_model=STTResponse,
    summary="Speech-to-Text",
    description="Transcribes an MP3 or WAV audio file using Deepgram Nova-2. "
                "Returns transcript, detected language, duration, and per-speaker segments.",
)
async def speech_to_text(
    audio: UploadFile = File(..., description="Audio file (MP3 or WAV)"),
    _: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
) -> STTResponse:
    filename = audio.filename or "unknown"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if audio.content_type not in ALLOWED_MIMETYPES and ext not in ("mp3", "wav"):
        raise HTTPException(status_code=400, detail="Only MP3 and WAV files are accepted.")

    start = time.perf_counter()
    http_status = 200
    try:
        audio_bytes = await audio.read()
        mimetype = audio.content_type or "audio/mpeg"

        response = await asyncio.to_thread(transcribe_audio_sync, audio_bytes, mimetype)

        # Parse Deepgram JSON response
        metadata = response.get("metadata", {})
        duration = float(metadata.get("duration", 0.0))

        channels = response.get("results", {}).get("channels", [])
        channel = channels[0] if channels else {}

        language = channel.get("detected_language", "unknown") or "unknown"
        alternatives = channel.get("alternatives", [])
        alternative = alternatives[0] if alternatives else {}

        transcript = alternative.get("transcript", "")
        words = alternative.get("words", [])

        speakers = _group_words_by_speaker(words)
        latency_ms = (time.perf_counter() - start) * 1000

        _log(db, "/stt", filename, transcript, f"duration={duration:.2f}s", latency_ms, http_status)

        return STTResponse(
            transcript=transcript,
            language=language or "unknown",
            duration=duration,
            speakers=speakers,
        )

    except HTTPException:
        raise
    except Exception as exc:
        http_status = 500
        latency_ms = (time.perf_counter() - start) * 1000
        _log(db, "/stt", filename, f"ERROR: {str(exc)[:200]}", None, latency_ms, http_status)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(exc)}")
