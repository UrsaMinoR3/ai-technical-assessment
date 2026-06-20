from pydantic import BaseModel


class SpeakerSegment(BaseModel):
    speaker: int
    start: float
    end: float
    text: str


class STTResponse(BaseModel):
    transcript: str
    language: str
    duration: float
    speakers: list[SpeakerSegment]
