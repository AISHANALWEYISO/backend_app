
import base64
import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SOIL_ANALYSIS_PROMPT = """
You are an expert agronomist and soil scientist.

First, determine if this image actually shows soil, dirt, ground, or earth material.

If the image does NOT show soil, respond ONLY with this exact JSON:
{
  "is_soil": false,
  "error": "This image does not appear to show soil. Please upload a clear photo of soil or ground."
}

If the image DOES show soil, respond ONLY with this exact JSON (no extra text, no markdown):
{
  "is_soil": true,
  "soil_health_score": <integer 0-100>,
  "soil_type": "<e.g. Clay, Sandy, Loam, Silt, Peat, Chalky>",
  "texture": "<Fine / Medium / Coarse>",
  "color_analysis": "<what the color indicates>",
  "estimated_nutrients": {
    "nitrogen": "<Low / Medium / High>",
    "phosphorus": "<Low / Medium / High>",
    "potassium": "<Low / Medium / High>",
    "pH_estimate": "<Acidic / Neutral / Alkaline>"
  },
  "recommended_crops": [
    {"name": "<crop>", "suitability": "<Excellent / Good / Fair>", "reason": "<one sentence>"},
    {"name": "<crop>", "suitability": "<Excellent / Good / Fair>", "reason": "<one sentence>"},
    {"name": "<crop>", "suitability": "<Excellent / Good / Fair>", "reason": "<one sentence>"}
  ],
  "fertilizers": [
    {"name": "<fertilizer>", "type": "<Organic / Chemical>", "application": "<how and when>"},
    {"name": "<fertilizer>", "type": "<Organic / Chemical>", "application": "<how and when>"},
    {"name": "<fertilizer>", "type": "<Organic / Chemical>", "application": "<how and when>"}
  ],
  "improvement_tips": ["<tip 1>", "<tip 2>", "<tip 3>"],
  "summary": "<2-3 sentence overall assessment>"
}
"""

def analyze_soil_image(image_data: bytes, media_type: str = "image/jpeg") -> dict:
    base64_image = base64.b64encode(image_data).decode("utf-8")
    image_url = f"data:{media_type};base64,{base64_image}"

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    },
                    {
                        "type": "text",
                        "text": SOIL_ANALYSIS_PROMPT
                    }
                ]
            }
        ],
        max_tokens=1500,
        temperature=0.3,
    )

    response_text = response.choices[0].message.content.strip()
    clean = response_text.replace("```json", "").replace("```", "").strip()
    result = json.loads(clean)

    # If AI says it's not soil, raise an error
    if not result.get("is_soil", True):
        raise ValueError(result.get("error", "Image does not appear to be soil."))

    return result