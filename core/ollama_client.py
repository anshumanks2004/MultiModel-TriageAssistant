"""Ollama API wrapper for text and vision inference.

Provides a unified interface over Llama3 (text) and LLaVA (vision).
All retry logic and error normalization live here.
"""

import base64
import json
import logging
from typing import Optional

import requests

from config.settings import (
    OLLAMA_BASE_URL,
    OLLAMA_RETRY_ATTEMPTS,
    OLLAMA_TEXT_MODEL,
    OLLAMA_TIMEOUT,
    OLLAMA_VISION_MODEL,
)

logger = logging.getLogger(__name__)


class OllamaClientError(Exception):
    """Raised when the Ollama API returns an unexpected error."""


def _post_with_retry(url: str, payload: dict, timeout: int) -> dict:
    """POST to Ollama with simple retry on connection errors."""
    last_error: Exception = RuntimeError("No attempts made")
    for attempt in range(1, OLLAMA_RETRY_ATTEMPTS + 1):
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as exc:
            last_error = exc
            logger.warning("Ollama connection error (attempt %d/%d): %s", attempt, OLLAMA_RETRY_ATTEMPTS, exc)
        except requests.exceptions.Timeout as exc:
            last_error = exc
            logger.warning("Ollama timeout (attempt %d/%d)", attempt, OLLAMA_RETRY_ATTEMPTS)
        except requests.exceptions.HTTPError as exc:
            raise OllamaClientError(f"Ollama HTTP error: {exc}") from exc
    raise OllamaClientError(f"Ollama unreachable after {OLLAMA_RETRY_ATTEMPTS} attempts: {last_error}") from last_error


def generate_text(
    system_prompt: str,
    user_prompt: str,
    model: str = OLLAMA_TEXT_MODEL,
    temperature: float = 0.1,
) -> str:
    """Call Llama3 for text-only inference.

    Returns the raw response string from the model.
    Raises OllamaClientError on failure.
    """
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": model,
        "stream": False,
        "options": {"temperature": temperature},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    logger.debug("Sending text request to Ollama model=%s", model)
    result = _post_with_retry(url, payload, OLLAMA_TIMEOUT)
    content = result.get("message", {}).get("content", "")
    if not content:
        raise OllamaClientError("Ollama returned empty content for text request")
    logger.debug("Received text response (%d chars)", len(content))
    return content


def generate_vision(
    system_prompt: str,
    user_prompt: str,
    image_base64: str,
    model: str = OLLAMA_VISION_MODEL,
    temperature: float = 0.1,
) -> str:
    """Call LLaVA for vision inference.

    image_base64: base64-encoded image bytes (no data-URI prefix needed).
    Returns the raw response string from the model.
    Raises OllamaClientError on failure.
    """
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": model,
        "stream": False,
        "options": {"temperature": temperature},
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_prompt,
                "images": [image_base64],
            },
        ],
    }
    logger.debug("Sending vision request to Ollama model=%s", model)
    result = _post_with_retry(url, payload, OLLAMA_TIMEOUT)
    content = result.get("message", {}).get("content", "")
    if not content:
        raise OllamaClientError("Ollama returned empty content for vision request")
    logger.debug("Received vision response (%d chars)", len(content))
    return content


def check_health() -> dict[str, bool]:
    """Ping Ollama and check whether required models are loaded.

    Returns a dict: {"ollama": bool, "llama3": bool, "llava": bool}
    """
    status = {"ollama": False, OLLAMA_TEXT_MODEL: False, OLLAMA_VISION_MODEL: False}
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        status["ollama"] = True
        loaded_models = {m["name"].split(":")[0] for m in resp.json().get("models", [])}
        status[OLLAMA_TEXT_MODEL] = OLLAMA_TEXT_MODEL in loaded_models
        status[OLLAMA_VISION_MODEL] = OLLAMA_VISION_MODEL in loaded_models
    except Exception as exc:
        logger.warning("Ollama health check failed: %s", exc)
    return status
