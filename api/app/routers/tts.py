import asyncio
import io
import time

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..core.auth import verify_api_key
from ..core.database import get_db
from ..models.request_log import RequestLog
from ..schemas.tts import TTSRequest
from ..services.deepgram_service import synthesize_speech_sync

router = APIRouter()


@router.post(
    "/tts",
    summary="Text-to-Speech",
    description="Synthesizes text into downloadable MP3 audio using Deepgram Aura. "
                "Select a voice via the `voice` field.",
    response_class=StreamingResponse,
    responses={200: {"content": {"audio/mpeg": {}}, "description": "MP3 audio file"}},
)
async def text_to_speech(
    request: TTSRequest,
    _: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    start = time.perf_counter()
    http_status = 200
    try:
        audio_data, chars_synthesized = await asyncio.to_thread(
            synthesize_speech_sync, request.text, request.voice
        )
        latency_ms = (time.perf_counter() - start) * 1000

        db.add(
            RequestLog(
                endpoint="/tts",
                input_data=request.text[:500],
                output_ref=f"audio/{len(audio_data)}_bytes",
                external_usage=f"chars_synthesized={chars_synthesized},voice={request.voice}",
                latency_ms=latency_ms,
                http_status=http_status,
            )
        )
        db.commit()

        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"},
        )

    except HTTPException:
        raise
    except Exception as exc:
        http_status = 500
        latency_ms = (time.perf_counter() - start) * 1000
        db.add(
            RequestLog(
                endpoint="/tts",
                input_data=request.text[:200],
                output_ref=f"ERROR: {str(exc)[:200]}",
                external_usage=None,
                latency_ms=latency_ms,
                http_status=http_status,
            )
        )
        db.commit()
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(exc)}")
