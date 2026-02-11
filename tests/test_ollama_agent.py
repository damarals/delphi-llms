import pytest

from delphi_llms.agents import ollama


def test_ensure_model_available_accepts_exact_match(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        ollama,
        "list_ollama_models",
        lambda *, ollama_host: ["qwen3-4b", "llama3.2:latest"],
    )
    ollama.ensure_model_available(ollama_host="http://ollama:11434", model="qwen3-4b")


def test_ensure_model_available_raises_for_missing_model(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        ollama,
        "list_ollama_models",
        lambda *, ollama_host: ["llama3.2:latest"],
    )
    with pytest.raises(ValueError) as exc:
        ollama.ensure_model_available(ollama_host="http://ollama:11434", model="qwen3-4b")
    assert "Model 'qwen3-4b' not found" in str(exc.value)
