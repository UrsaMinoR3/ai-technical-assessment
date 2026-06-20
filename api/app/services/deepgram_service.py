from deepgram import DeepgramClient, PrerecordedOptions, SpeakOptions

from ..core.config import settings


def _get_client() -> DeepgramClient:
    return DeepgramClient(settings.deepgram_api_key)


def transcribe_audio_sync(audio_bytes: bytes, mimetype: str) -> dict:
    client = _get_client()
    options = PrerecordedOptions(
        model="nova-2",
        detect_language=True,
        diarize=True,
        smart_format=True,
        punctuate=True,
    )
    response = client.listen.rest.v("1").transcribe_file(
        {"buffer": audio_bytes, "mimetype": mimetype},
        options,
    )
    return response


def synthesize_speech_sync(text: str, voice: str) -> tuple[bytes, int]:
    client = _get_client()
    options = SpeakOptions(model=voice)
    response = client.speak.rest.v("1").stream_memory({"text": text}, options)

    stream = response.stream_memory
    if hasattr(stream, "getvalue"):
        audio_data = stream.getvalue()
    elif hasattr(stream, "read"):
        audio_data = stream.read()
    else:
        audio_data = bytes(stream)

    return audio_data, len(text)
