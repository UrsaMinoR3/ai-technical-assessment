from pydantic import BaseModel, Field


AVAILABLE_VOICES = [
    "aura-asteria-en",
    "aura-luna-en",
    "aura-stella-en",
    "aura-athena-en",
    "aura-hera-en",
    "aura-orion-en",
    "aura-arcas-en",
    "aura-perseus-en",
    "aura-orpheus-en",
    "aura-helios-en",
    "aura-zeus-en",
]


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="Text to synthesize")
    voice: str = Field(
        default="aura-asteria-en",
        description=f"Deepgram voice model. Options: {', '.join(AVAILABLE_VOICES)}",
    )
