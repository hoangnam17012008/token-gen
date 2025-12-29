import asyncio
import requests


class AIAssistant:
    def __init__(self, api_key: str, service: str = "openrouter"):
        self.api_key = api_key
        self.service = service

    async def answer(self, query) -> str:
        def _request():
            if self.service == "groq":
                url = "https://api.groq.com/openai/v1/chat/completions"
                model = "llama-3.1-8b-instant"
            else:
                url = "https://openrouter.ai/api/v1/chat/completions"
                model = "gpt-4o-mini"

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            system_prompt = """You are an expert at solving Dutch accessibility hCaptcha challenges.
Your task is to determine if the description matches the image context implied by the question.

Rules:
1. Output ONLY 'ja' (yes) or 'nee' (no).
2. Answer 'ja' if the description is reasonably accurate or plausible for the object.
3. Answer 'nee' if the description is clearly wrong, unrelated, or describes a different object.
4. Ignore minor details; focus on the main subject.
5. Do NOT include any explanations, punctuation, or extra whitespace."""

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Question: {query}\nResponse:",
                    },
                ],
            }
            r = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=15,
            )
            return r.json()["choices"][0]["message"]["content"].replace(".", "")

        try:
            return await asyncio.to_thread(_request)
        except Exception:
            return "nee"
