import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# Defining tool schema
weather_tool = {
    "name":"get_weather_tool",
    "description":"Get current weather for a given city",
    "input_schema":{
        "type":"object",
        "properties":{
            "location":{
                "type":"string",
                "description":"the city and state, eg San Francisco, CA or Tokyo",
            },
            "unit":{
                "type":"string",
                "enum":["celsius","farenheit"],
                "description":"The temeprature unit to use."
            }
        },
        "required":["location"]
    }
}

# 2. Define the actual local function that "does all the work"
def get_weather_tool(location:str,unit:str="celsius"):
    # In a real app, this would call a live weather API (like OpenWeatherMap)
    # Here we stimulate a database/APi response
    return f"The weather in {location} is 22 degrees {unit}, sunny and clear"

# 3. Initial user message
messages = [
    {
        "role": "user",
        "content":"what is the weather right now in Tokyo"
    }
]

print("Sending inital request to Claude...")
response = client.messages.create(
    model = "claude-sonnet-5",
    max_tokens = 300,
    tools = [weather_tool],
    messages = messages
)

print(f"\n--- this is just for my reference... the initial response from the claude on my inital request: {response.content}\n")
# 4. Checking if the claude wants to use a tool
tool_use_block = next((block for block in response.content if block.type == "tool_use"),None)

if tool_use_block:
    print(f"\nClaude paused execution. Tool Requested: {tool_use_block.name}")
    print(f"\nExtracted arguments: {tool_use_block.input}")

    # A. Execute local python fucntion using the arguments Claude extracted
    local_result = get_weather_tool(**tool_use_block.input)
    print(f"\nLocal function executed. Result: {local_result}")

    # B. Append Claude's Assistant message (containing tool use result) to our conversation history...
    messages.append({
        "role":"assistant",
        "content": response.content
    })

    # C. Now appending tool execution's result back to conversation history the role "user"
    messages.append(
        {
            "role":"user",
            "content":[{
                "type":"tool_result",
                "tool_use_id":tool_use_block.id, # Must match the ID give by claude
                 "content":local_result

            }
        ]
        }
    )

    # D. Sending the updated conversation back to claude to get the final natural language answer
    final_response = client.messages.create(
        model = "claude-sonnet-5",
        max_tokens = 300,
        tools = [weather_tool],
        messages = messages
    )

    # now safely extracting the final text response
    final_text = next((block.text for block in final_response.content if block.type=="text"), "No text was found here XD.......")
    print(f"\n Final Claude reponse:{final_text}")

else:
    print("\nClaude didnt request the tool...")
 