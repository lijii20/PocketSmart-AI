import json
from typing import Optional
from google import genai
from google.genai import types
from app.config import settings
from app.services.platform_links import platform_links

class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

    def available(self):
        return self.client is not None

    def _clean_json(self, text: str):
        text=text.strip()
        if text.startswith("```"):
            text=text.split("\n",1)[1] if "\n" in text else text
            if text.endswith("```"): text=text[:-3]
        start=text.find("{"); end=text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end+1])
        return json.loads(text)

    def generate(self, planner: str, data: dict, image_bytes: Optional[bytes]=None, mime_type: Optional[str]=None):
        if not self.available():
            return None
        schema_hint='''Return ONLY valid JSON with this shape: {"title":"string","summary":"string","items":[{"category":"string","quantity":1,"estimated_unit_price":0,"estimated_total":0,"reason":"string","platforms":["Amazon"]}],"estimated_total":0,"remaining_budget":0,"additional_suggestions":["string"]}'''
        prompt=f"""You are PocketSmart AI, a budget-aware recommendation assistant. Planner={planner}.\nUser data:\n{json.dumps(data, indent=2)}\n\nRules: stay within the total budget; calculate totals; never claim live inventory or exact current prices; recommendations may be described as estimates; use these platform names only where relevant: Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO. Give practical reasons. {schema_hint}"""
        contents=[prompt]
        if image_bytes:
            contents.insert(0, types.Part.from_bytes(data=image_bytes, mime_type=mime_type or "image/jpeg"))
            contents.append("Analyze the outfit image for visible colors, patterns and style. Do not identify the person. Use that analysis only to improve jewelry matching.")
        try:
            response=self.client.models.generate_content(
                model=settings.gemini_model,
                contents=contents,
                config=types.GenerateContentConfig(temperature=0.3, response_mime_type="application/json")
            )
            result=self._clean_json(response.text)
            for item in result.get("items", []):
                names=item.pop("platforms", None) or ["Amazon"]
                item["links"]=platform_links(item.get("category", planner), names)
            return result
        except Exception:
            return None

gemini_service=GeminiService()
