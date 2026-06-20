import base64
import json

from openai import AsyncOpenAI

from ..core.config import settings

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.azure_openai_key,
            base_url=settings.azure_openai_base_url,
        )
    return _client


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
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }
    return json.loads(content), usage
