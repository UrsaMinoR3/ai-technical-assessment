from typing import Any

from pydantic import BaseModel


class FieldAnnotation(BaseModel):
    value: str
    bbox: list[float] | None = None  # [x1, y1, x2, y2] as 0.0–1.0 fractions


class IDPResponse(BaseModel):
    document_type: str
    extracted_fields: dict[str, Any]        # flat {field: value} for display
    annotations: dict[str, FieldAnnotation] | None = None  # includes bbox for UI overlay
    confidence: str
