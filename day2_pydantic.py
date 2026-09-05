import os
import anthropic
import json 
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

load_dotenv()
client = anthropic.Anthropic()

class CodeReviewAnalysis(BaseModel):
    is_secure:bool = Field(description = "True if code has no critical flaws, else False.")
    risk_level:str = Field(description = "Must be exactly one of: Low,Medium,High")
    summary:str = Field(description="A concise one-sentence critique of the code.")

prompt = '''
Analyze the following Python snippet for security risks:
password = "admin123"

You must output valid JSON only, matching this exact structure:
{
  "is_secure": boolean,
  "risk_level": "Low" or "Medium" or "High",
  "summary": "string"
}
'''

response = client.messages.create(
    model = "claude-sonnet-5",
    max_tokens = 250,
    system = "You are a strict code security auditor that outputs raw Json only.",
    messages = [
        {
            "role":"user",
            "content":[{"type":"text","text":prompt}]
        }
    ]
)

raw_text = response.content[0].text
print("---RAW MODEL OUTPUT---")
print(raw_text)

try:
    # LLMs often wrap JSON in markdown blocks like ```json ... ```. We clean that up.
    cleaned_text = raw_text.strip().replace("```json", "").replace("```", "").strip()
    
    # Pass the clean text string into Pydantic to validate and parse into a Python object
    parsed_data = CodeReviewAnalysis.model_validate_json(cleaned_text)
    
    print("\n--- VALIDATION SUCCESSFUL ---")
    print(f"Is Secure (Python bool): {parsed_data.is_secure} (Type: {type(parsed_data.is_secure)})")
    print(f"Risk Level (Python str): {parsed_data.risk_level}")
    print(f"Summary: {parsed_data.summary}")

except (ValidationError, json.JSONDecodeError) as e:
    print("\n\n--- VALIDATION FAILED ---")
    print(f"The model output did not match the expected schema: {e}")