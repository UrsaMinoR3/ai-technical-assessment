from fastapi import FastAPI

from .core.database import Base, engine
from .models import RequestLog  # registers model with Base metadata
from .routers import idp, stt, tts

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Technical Assessment API",
    description=(
        "REST API integrating **Azure OpenAI** and **Deepgram** for voice processing "
        "and intelligent document analysis.\n\n"
        "All endpoints require the `X-API-Key` header."
    ),
    version="1.0.0",
)

app.include_router(stt.router, tags=["Speech-to-Text"])
app.include_router(tts.router, tags=["Text-to-Speech"])
app.include_router(idp.router, tags=["Intelligent Document Processing"])


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "version": "1.0.0"}
