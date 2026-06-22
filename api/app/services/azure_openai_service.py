import base64
import json
import re

from openai import AsyncOpenAI

from ..core.config import settings


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.azure_openai_key,
        base_url=settings.azure_openai_base_url,
    )


def _extract_json(text: str) -> dict:
    if not text:
        raise ValueError("Model returned empty content")
    clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse JSON from model response: {text[:200]}")


def _parse_fields(raw: dict) -> tuple[dict, dict]:
    """
    Split the model's extracted_fields into:
      - flat_fields: {field_name: value_string}  (for display table)
      - annotations: {field_name: {value, bbox}}  (for image overlay)
    Handles both old format (str values) and new format ({value, bbox} objects).
    """
    flat: dict = {}
    ann: dict = {}
    for key, val in raw.items():
        if isinstance(val, dict) and "value" in val:
            flat[key] = str(val["value"])
            ann[key] = {"value": str(val["value"]), "bbox": val.get("bbox")}
        else:
            flat[key] = str(val)
            ann[key] = {"value": str(val), "bbox": None}
    return flat, ann


async def analyze_document(image_bytes: bytes, content_type: str) -> tuple[dict, dict, dict]:
    client = _get_client()
    mime = content_type if content_type in ("image/jpeg", "image/png") else "image/jpeg"
    b64 = base64.b64encode(image_bytes).decode()

    response = await client.chat.completions.create(
        model=settings.azure_openai_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You are a document extraction expert. Analyze this document image "
                            "and extract all visible information.\n\n"
                            "Return ONLY a valid JSON object with exactly three keys:\n"
                            "1. 'document_type': string (e.g. 'National ID Card', 'Passport', 'Invoice')\n"
                            "2. 'confidence': 'high', 'medium', or 'low'\n"
                            "3. 'extracted_fields': object where each key is a field name and "
                            "each value is an object with:\n"
                            "   - 'value': the extracted text string\n"
                            "   - 'bbox': [x1, y1, x2, y2] as decimal fractions (0.0 to 1.0) "
                            "of image width/height indicating where this field appears. "
                            "x1,y1 = top-left corner; x2,y2 = bottom-right corner.\n\n"
                            "Example:\n"
                            "  \"full_name\": {\"value\": \"Juan Pérez\", \"bbox\": [0.10, 0.22, 0.65, 0.30]}\n\n"
                            "Extract every visible field. Do not include markdown or explanation."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    },
                ],
            }
        ],
        max_tokens=1500,
    )

    content = response.choices[0].message.content
    finish_reason = response.choices[0].finish_reason

    if not content:
        raise ValueError(
            f"Model returned no content (finish_reason={finish_reason}). "
            "The image may have triggered a safety filter or is unreadable."
        )

    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }

    parsed = _extract_json(content)
    flat_fields, annotations = _parse_fields(parsed.get("extracted_fields", {}))
    return parsed, flat_fields, annotations, usage
