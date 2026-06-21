import base64
import json
import re

from openai import AsyncOpenAI

from ..core.config import settings


def _get_client() -> AsyncOpenAI:
    # Fresh client per call — avoids stale credentials after env changes
    return AsyncOpenAI(
        api_key=settings.azure_openai_key,
        base_url=settings.azure_openai_base_url,
    )


def _extract_json(text: str) -> dict:
    """Parse JSON from model response, handling markdown code blocks gracefully."""
    if not text:
        raise ValueError("Model returned empty content")

    # Strip markdown code fences if present (```json ... ```)
    clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)

    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        # Last resort: grab the first {...} block
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse JSON from model response: {text[:200]}")


async def analyze_document(image_bytes: bytes, content_type: str) -> tuple[dict, dict]:
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
                            "and extract all relevant information. Identify the document type "
                            "(ID card, passport, invoice, receipt, driver's license, etc.) and "
                            "extract every visible field. Return ONLY a valid JSON object with "
                            "three keys: 'document_type' (string), 'extracted_fields' (object "
                            "with key-value pairs for every field visible), and 'confidence' "
                            "('high', 'medium', or 'low' based on image clarity and extraction "
                            "certainty). Do not include markdown or explanation."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    },
                ],
            }
        ],
        max_tokens=1000,
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

    return _extract_json(content), usage
