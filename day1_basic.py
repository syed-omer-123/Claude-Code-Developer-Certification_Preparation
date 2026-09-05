import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

response = client.messages.create(
    model = "claude-sonnet-5",
    max_tokens=300,
    system = "You are a precise, technical AI instructor who answers in exactly one sentence.",
    messages=[
        {
            "role":"user",
            "content":[
                {
                    "type":"text",
                    "text":"Explain what an Application programming interface(API) is."

                }
                
            ]
        }
    ]
)

print("RAW Response...")
print(response)
print("Extracted response...")
print(response.content[0].text)
print(f"\nToken Used -Input:{response.usage.input_tokens}, Output: {response.usage.output_tokens}")