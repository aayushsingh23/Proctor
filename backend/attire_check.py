import os
import base64
from openai import OpenAI
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Classification prompt
text_prompt = """
You are an attire classification engine. Analyze the person's clothing and classify the dress code into one of three labels:
- 'formal'
- 'informal'
- 'semi-formal' (only if you are uncertain between the two)

Rules:
- Only output JSON. No comments, no explanations outside JSON.
- Include these fields in your JSON output:

{
  "dress_code": "formal | informal | semi-formal",
  "reason": "Brief justification for the classification",
  "formal_score": float between 0 and 1,
  "informal_score": float between 0 and 1,
  "confidence": float between 0 and 1 (confidence in your final label)
}

Scoring guidelines:
- 'formal_score' measures how well the attire fits typical formal standards (e.g., shirt, tie, trousers, tucked-in, formal shoes).
- 'informal_score' measures presence of casual indicators (e.g., t-shirt, jeans, sneakers, rolled sleeves, untucked shirt).
- Use 'semi-formal' only if the scores are very close (e.g., within 0.1 of each other).
- 'confidence' should be high (near 1) only if the difference between scores is large (> 0.4), and low (near 0.5) if close.

You must always return a complete and valid JSON object.
You must return only raw JSON. Do not wrap it in triple backticks. Do not add markdown formatting.
"""

def check_attire(base64_image: str) -> dict:
    """
    Sends the image to OpenAI GPT-4o model for attire classification.
    Returns the parsed JSON object from the model response.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        { "type": "text", "text": text_prompt },
                        { "type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}" }
                        }
                    ]
                }
            ],
            max_tokens=300,
            temperature=0.3
        )

        # Model should return valid JSON
        # return json.loads(response.choices[0].message.content)
        output_text = response.choices[0].message.content.strip()

        # 🧼 Remove markdown code block if present
        if output_text.startswith("```json"):
            output_text = output_text.replace("```json", "").replace("```", "").strip()

        try:
            result = json.loads(output_text)
        except json.JSONDecodeError as e:
            print("❌ Failed to parse JSON from OpenAI:", e)
            result = {
                "error": "Invalid JSON from OpenAI",
                "raw": output_text
            }



    except Exception as e:
        print("❌ Attire check failed:", e)
        return {
            "error": str(e),
            "dress_code": "unknown",
            "reason": "Failed to analyze attire",
            "formal_score": 0,
            "informal_score": 0,
            "confidence": 0
        }
