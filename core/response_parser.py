"""Parse and validate raw LLM output into structured data.

LLMs occasionally wrap JSON in markdown code fences or add preamble text.
This module strips that noise and validates the result against Pydantic schemas.
"""

import json
import logging
import re
from typing import Any, Type, TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Matches ```json ... ``` or ``` ... ``` blocks
_CODE_FENCE_PATTERN = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


def _extract_json_string(raw: str) -> str:
    """Strip markdown fences and extract the JSON substring."""
    fence_match = _CODE_FENCE_PATTERN.search(raw)
    if fence_match:
        return fence_match.group(1).strip()

    # Try to find the first { ... } block if no fence
    brace_start = raw.find("{")
    brace_end = raw.rfind("}")
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        return raw[brace_start : brace_end + 1].strip()

    return raw.strip()


def parse_llm_response(raw: str, schema: Type[T]) -> T:
    """Parse raw LLM text into a validated Pydantic model.

    Raises:
        ValueError: if the JSON cannot be parsed or schema validation fails.
    """
    json_str = _extract_json_string(raw)

    try:
        data: dict[str, Any] = json.loads(json_str)
    except json.JSONDecodeError as exc:
        logger.error("JSON parse failure. Raw snippet: %s", json_str[:300])
        raise ValueError(f"LLM response is not valid JSON: {exc}") from exc

    try:
        return schema.model_validate(data)
    except ValidationError as exc:
        logger.error("Schema validation failure: %s", exc)
        raise ValueError(f"LLM JSON does not match expected schema: {exc}") from exc
