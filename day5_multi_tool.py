"""Practising for a Scenario like:
"Can you check the shipping status for order #9876, and if it's delayed, look up our return policy?"
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# 1. Now defining multiple tools
tools = [
    {
        "name":"check_order_status",
        "description":"Check the live shipping status and tracking updates for a customer order.",
        "input_schema":{
            "type":"object",
            "properties":{
                "order_id":{
                    "type":"string",
                    "description":"The customer order identifier. eg:9876"
                }
            },
            "required":["order_id"]
        }
    },
    {
        "name":"get_refund_policy",
        "description":"Retrieve comapny return and refund and shipping delay compensation guidelines....",
        "input_schema":{
            "type":"object",
            "properties":{
                "topic":{
                    "type":"string",
                    "description":"the specifc policy topic to search for",
                }
            },
            "required":["topic"]
        }
    }
]

# 2. Local mock fucntions stimulating the backend databases
def check_order_status(order_id:str):
    #Mock database lookup
    mock_db = {
        "9876": "Status: Delayed in transit due to severe regional weather. eTA Pending"
    }
    return mock_db.get(order_id,f"Error: Order ID {order_id} not found in the database")

def get_return_policy(topic:str):
    #Mock policy document lookup
    if "delay" in topic.lower() or "shipping" in topic.lower():
        return "Policy: Customers experiencing shipping delays over 48 hours due to weather are eligible for a 50% shipping refund upon request."
    return "Policy: Standard returns are accepted within 30 days of delivery for a full refund."

# 3. First, user prompt requiring multi-step reasoning across multiple blocks
messages = [{
    "role":"user",
    "content":"Can you check the shipping status for the order #9876, and if its delayed, look up our return and refund policy?"
}]

print(".....Starting Multi-Tool Autonomous Agent Loop.....")

# 4. Agent Loop safety bounds
max_iterations = 5
current_iterations = 0
agent_finished = False

# 5. Core Agent Loop Execution
while not agent_finished and current_iterations<max_iterations:
    current_iterations = current_iterations + 1
    print(f"\n ----- Agent Iteration number is: [{current_iterations}/{max_iterations}]---")

    response = client.messages.create(
        model = "claude-sonnet-5",
        max_tokens=500,
        tools = tools,
        messages = messages
    )

    print(f"Model Stop reason 1: {response.stop_reason}")

    if response.stop_reason == "end_turn":
        final_text = next((block.text for block in response.content if block.type =="text"),"No final text provided.")
        print(f"\nAgent Task Complete: Final Answer:\n{final_text}")
        agent_finished = True
        break

    elif response.stop_reason == "tool_use":
        messages.append(
            {
                "role":"assistant",
                "content":response.content
            }
        )

        tool_use_blocks = [block for block in response.content if block.type == "tool_use"]

        for tool_block in tool_use_blocks:
            print(f"Claude selected the tool: '{tool_block.name}' with inputs: {tool_block.input}")

        # Locally executing with safety boundary
            try:
                if tool_block.name == "check_order_status":
                    tool_output = check_order_status(**tool_block.input)
                elif tool_block.name == "get_refund_policy":
                    tool_output = get_return_policy(**tool_block.input)
                else:
                    tool_output = f"Error: Unknown tool name '{tool_block.name}'."
            except Exception as e:
                tool_output = f"Tool execution failed with exception: {str(e)}"

            messages.append({
                "role":"user",
                "content":[
                    {
                        "type":"tool_result",
                        "tool_use_id":tool_block.id,
                        "content":tool_output
                    }
                ]
            })
    else:
        print(f"Unexpected stop_reason: {response.stop_reason}")

    if current_iterations>=max_iterations and not agent_finished:
        print("\n[Safety Warning]: Agent terminated because max iterations cap was reached.")

"""
And here is the output i got:

".....Starting Multi-Tool Autonomous Agent Loop.....

 ----- Agent Iteration number is: [1/5]---
Model Stop reason 1: tool_use
Claude selected the tool: 'check_order_status' with inputs: {'order_id': '9876'}

 ----- Agent Iteration number is: [2/5]---
Model Stop reason 1: tool_use
Claude selected the tool: 'get_refund_policy' with inputs: {'topic': 'shipping delay compensation'}

 ----- Agent Iteration number is: [3/5]---
Model Stop reason 1: end_turn

Agent Task Complete: Final Answer:
Here's the summary for order **#9876**:

**Shipping Status:**
- Currently **delayed in transit** due to severe regional weather.
- ETA is pending at this time.

**Relevant Policy — Shipping Delay Compensation:**
- Since your delay is weather-related, if it exceeds **48 hours**, you're eligible for a **50% refund on shipping costs** upon request.

**Next steps:** If the delay has already crossed the 48-hour mark (or does once it clears), just let me know and I can help you submit a request for the shipping refund. Would you like me to assist with that?"""