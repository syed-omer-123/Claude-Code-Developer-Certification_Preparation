import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

weather_tool = {
    "name":"get_weather_tool",
    "description":"Get the current weather for a given city",
    "input_schema":{
        "type":"object",
        "properties":{
            "location":{
                "type":"string",
                "description":"The city and state, eg San Fransisco, CA or Tokyo",
            },
            "unit":{
                "type":"string",
                "enum":["celsius","farenheit"],
                "description":"The temperature unit to use"
            }
        },
        "required":["location"]
    }
}

response = client.messages.create(
    model = "claude-sonnet-5",
    max_tokens = 300,
    tools = [weather_tool],
    messages = [
        {
            "role":"user",
            "content":"What is the weather right now in Tokyo?"
        }
    ]
)

print(f"----- STOP REASON: {response.stop_reason}----")

for block in response.content:
    print(f"Block Type: {block.type}")
    if block.type == "tool_use":
        print(f"Tool Requested: {block.name}")
        print(f"Tool Use ID: {block.id}")
        print(f"Extracted Arguments: {block.input}")