"""Unified AI client — uses Vertex AI (Gemini) as primary, with Anthropic & OpenRouter fallbacks."""
import json
import logging
from typing import Optional, List, Dict, Any
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class AIClient:
    """Multi-provider AI client with automatic fallback chain:
       1. Vertex AI (Gemini) — primary
       2. Anthropic (Claude) — fallback #1
       3. OpenRouter — fallback #2
       4. Groq — fallback #3
    """

    def __init__(self):
        self._providers = []
        if settings.vertex_ai_api_key:
            self._providers.append(("vertex_ai", settings.vertex_ai_api_key))
        if settings.anthropic_api_key:
            self._providers.append(("anthropic", settings.anthropic_api_key))
        if settings.openrouter_api_key:
            self._providers.append(("openrouter", settings.openrouter_api_key))
        if settings.groq_api_key:
            self._providers.append(("groq", settings.groq_api_key))

        if not self._providers:
            logger.warning("No AI provider API keys configured!")

    @property
    def primary_provider(self) -> str:
        return self._providers[0][0] if self._providers else "none"

    async def generate(
        self,
        prompt: str,
        *,
        system: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.3,
        json_mode: bool = False,
    ) -> str:
        """Generate text using the best available provider, with automatic fallback."""
        for provider_name, api_key in self._providers:
            try:
                result = await self._call_provider(
                    provider_name, api_key, prompt,
                    system=system,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    json_mode=json_mode,
                )
                if result:
                    logger.info(f"AI response from {provider_name} ({len(result)} chars)")
                    return result
            except Exception as exc:
                logger.warning(f"AI provider {provider_name} failed: {exc}, trying next...")
                continue

        logger.error("All AI providers failed")
        raise RuntimeError("All AI providers exhausted")

    async def generate_json(self, prompt: str, *, system: str = "", max_tokens: int = 1024) -> dict:
        """Generate and parse a JSON response."""
        text = await self.generate(prompt, system=system, max_tokens=max_tokens, json_mode=True)
        # Strip markdown code fences if present
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        return json.loads(text)

    async def _call_provider(
        self,
        provider: str,
        api_key: str,
        prompt: str,
        *,
        system: str = "",
        max_tokens: int = 1024,
        temperature: float = 0.3,
        json_mode: bool = False,
    ) -> Optional[str]:
        if provider == "vertex_ai":
            return await self._call_vertex_ai(api_key, prompt, system, max_tokens, temperature, json_mode)
        elif provider == "anthropic":
            return await self._call_anthropic(api_key, prompt, system, max_tokens, temperature)
        elif provider == "openrouter":
            return await self._call_openrouter(api_key, prompt, system, max_tokens, temperature)
        elif provider == "groq":
            return await self._call_groq(api_key, prompt, system, max_tokens, temperature)
        return None

    async def _call_vertex_ai(
        self, api_key: str, prompt: str, system: str,
        max_tokens: int, temperature: float, json_mode: bool,
    ) -> str:
        """Call Google Vertex AI Gemini API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

        contents = [{"parts": [{"text": prompt}]}]
        body: dict = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        }

        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}

        if json_mode:
            body["generationConfig"]["responseMimeType"] = "application/json"

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=body)
            resp.raise_for_status()
            data = resp.json()

        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError("No candidates in Vertex AI response")

        parts = candidates[0].get("content", {}).get("parts", [])
        return parts[0].get("text", "") if parts else ""

    async def _call_anthropic(
        self, api_key: str, prompt: str, system: str,
        max_tokens: int, temperature: float,
    ) -> str:
        """Call Anthropic Claude API."""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {
            "model": "claude-sonnet-4-6",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            body["system"] = system

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=body, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        return data["content"][0]["text"]

    async def _call_openrouter(
        self, api_key: str, prompt: str, system: str,
        max_tokens: int, temperature: float,
    ) -> str:
        """Call OpenRouter API (OpenAI-compatible)."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": "google/gemini-2.0-flash-exp:free",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=body, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        return data["choices"][0]["message"]["content"]

    async def _call_groq(
        self, api_key: str, prompt: str, system: str,
        max_tokens: int, temperature: float,
    ) -> str:
        """Call Groq API (OpenAI-compatible, ultra-fast inference)."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": "llama-3.3-70b-versatile",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=body, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        return data["choices"][0]["message"]["content"]


# Singleton instance
ai_client = AIClient()
