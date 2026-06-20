import time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..core.auth import verify_api_key
from ..core.database import get_db
from ..models.request_log import RequestLog
from ..schemas.idp import IDPResponse
from ..services.azure_openai_service import analyze_document

router = APIRouter()

ALLOWED_MIMETYPES = {"image/jpeg", "image/jpg", "image/png"}


@router.post(
    "/idp/analyze",
    response_model=IDPResponse,
    summary="Intelligent Document Processing",
    description="Accepts a JPG or PNG image of a document (ID, passport, invoice, etc.) "
                "and returns structured JSON with all extracted fields via Azure OpenAI.",
)
async def analyze_document_endpoint(
    image: UploadFile = File(..., description="Document image (JPG or PNG)"),
    _: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
) -> IDPResponse:
    filename = image.filename or "unknown"
    if image.content_type not in ALLOWED_MIMETYPES:
        raise HTTPException(status_code=400, detail="Only JPG and PNG images are accepted.")

    start = time.perf_counter()
    http_status = 200
    try:
        image_bytes = await image.read()
        extracted, usage = await analyze_document(image_bytes, image.content_type)

        latency_ms = (time.perf_counter() - start) * 1000
        usage_str = (
            f"prompt_tokens={usage['prompt_tokens']},"
            f"completion_tokens={usage['completion_tokens']},"
            f"total_tokens={usage['total_tokens']}"
        )

        db.add(
            RequestLog(
                endpoint="/idp/analyze",
                input_data=filename,
                output_ref=str(extracted)[:500],
                external_usage=usage_str,
                latency_ms=latency_ms,
                http_status=http_status,
            )
        )
        db.commit()

        return IDPResponse(
            document_type=extracted.get("document_type", "unknown"),
            extracted_fields=extracted.get("extracted_fields", {}),
            confidence=extracted.get("confidence", "low"),
        )

    except HTTPException:
        raise
    except Exception as exc:
        http_status = 500
        latency_ms = (time.perf_counter() - start) * 1000
        db.add(
            RequestLog(
                endpoint="/idp/analyze",
                input_data=filename,
                output_ref=f"ERROR: {str(exc)[:200]}",
                external_usage=None,
                latency_ms=latency_ms,
                http_status=http_status,
            )
        )
        db.commit()
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(exc)}")
