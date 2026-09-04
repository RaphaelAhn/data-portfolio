"""Optional OpenAI-compatible structured classifier. Keys are read only from the environment."""
from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen

def classify_with_openai(ticket: dict) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key: raise RuntimeError("OPENAI_API_KEY is required with --use-openai; never commit API keys.")
    payload = {"model": os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"), "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": "Classify a synthetic CS ticket. Return JSON with issue_type, urgency (normal|high), and summary. Do not make policy or compensation decisions."}, {"role": "user", "content": json.dumps({"issue_type_hint": ticket["issue_type"], "body": ticket["masked_body"]}, ensure_ascii=False)}], "temperature": 0}
    request = Request("https://api.openai.com/v1/chat/completions", data=json.dumps(payload).encode(), headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=30) as response: content = json.loads(response.read())["choices"][0]["message"]["content"]
    result = json.loads(content)
    if result.get("urgency") not in {"normal", "high"} or not all(result.get(key) for key in ("issue_type", "summary")): raise ValueError("LLM response violates the classification contract")
    return result
