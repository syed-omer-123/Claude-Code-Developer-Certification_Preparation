import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

response = client.messages.create(
    model = "claude-sonnet-5",
    max_tokens = 15,
    system = "You are a helpul assistant",
    messages = [
        {
            "role":"user",
            "content":[{
                "type":"text","text":"write a very long,detailed paragraph explaining history of quantum computing from 1980 to present day"
                }]
        }
    ]
)

print(f"----STOP REASON: {response.stop_reason}----")
print("----GENERATE TEXT----")
print(response.content[0].text)

if response.stop_reason == "max_tokens":
    print(f"\n----ALERT: the output was cut off because of max_tokens was too restricted")
