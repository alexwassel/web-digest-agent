
import json
from typing import Dict, Any
from .base import ModelClient

class OpenAIClient(ModelClient):
    def __init__(self, api_key: str, model: str):
        self.key = api_key
        self.model = model
        try:
            import openai
            self.openai = openai
            self.openai.api_key = api_key
        except Exception as e:
            raise RuntimeError("OpenAI SDK not installed. pip install openai") from e

    def complete_text(self, prompt: str, max_tokens: int = 800) -> str:
        resp = self.openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "system", "content": "You are a concise analyst."},
                      {"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=max_tokens,
        )
        return resp["choices"][0]["message"]["content"].strip()

    def complete_json(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        instruct = (
            "Return ONLY valid JSON matching this schema: " + json.dumps(schema) +
            "\nIf unsure, return an empty JSON object {}.\n\n" + prompt
        )
        text = self.complete_text(instruct, max_tokens=600)
        try:
            return json.loads(text)
        except Exception:
            import re
            m = re.search(r"\{[\s\S]*\}$", text.strip())
            return json.loads(m.group(0)) if m else {}
