import json

import httpx


def list_ollama_models(*, ollama_host: str) -> list[str]:
    url = f"{ollama_host.rstrip('/')}/api/tags"
    response = httpx.get(url, timeout=30.0)
    response.raise_for_status()
    data = response.json()
    models = data.get("models") or []
    names: list[str] = []
    for model in models:
        if isinstance(model, dict):
            name = model.get("name")
            if isinstance(name, str):
                names.append(name)
    return names


def ensure_model_available(*, ollama_host: str, model: str) -> None:
    names = list_ollama_models(ollama_host=ollama_host)
    if model in names:
        return
    if ":" not in model and f"{model}:latest" in names:
        return
    available = ", ".join(names) if names else "<none>"
    raise ValueError(
        f"Model '{model}' not found in Ollama. Available: {available}. "
        f"Run: ollama pull {model}"
    )


def call_ollama_expert(
    *,
    model: str,
    ollama_host: str,
    item_id: str,
    item_text: str,
    round_number: int,
    expert_id: str,
    seed: int,
) -> dict:
    prompt = (
        "You are a Delphi expert. Return only JSON with keys: rating (1-9 integer), "
        "category (string), rationale (short string), confidence (0-1 float). "
        f"Round: {round_number}. Expert: {expert_id}. Item ID: {item_id}. Item: {item_text}"
    )

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"seed": seed, "temperature": 0.2},
    }

    url = f"{ollama_host.rstrip('/')}/api/generate"
    response = httpx.post(url, json=payload, timeout=120.0)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        message = response.text
        raise httpx.HTTPStatusError(
            f"Ollama request failed for model '{model}': {message}",
            request=exc.request,
            response=exc.response,
        ) from exc
    body = response.json()
    text = body.get("response", "{}")
    parsed = json.loads(text)

    return {
        "rating": int(parsed["rating"]),
        "category": str(parsed["category"]),
        "rationale": str(parsed.get("rationale", "")),
        "confidence": float(parsed.get("confidence", 0.5)),
    }
