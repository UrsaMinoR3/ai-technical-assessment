from typing import Any

from pydantic import BaseModel


class IDPResponse(BaseModel):
    document_type: str
    extracted_fields: dict[str, Any]
    confidence: str
