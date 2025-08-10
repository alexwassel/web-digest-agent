
import json
from typing import Dict, Any
from .base import ModelClient

class AnthropicClient(ModelClient):
    def __init__(self, api_key: str, model: str):
        self.key = api_key
        self.model = model
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            raise RuntimeError("Anthropic SDK not installed. pip install anthropic") from e

    def complete_text(self, prompt: str, max_tokens: int = 800) -> str:
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join([b.text for b in msg.content])

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
