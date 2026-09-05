import os
import anthropic
from dotenv import load_dotenv
import base64

load_dotenv()

client = anthropic.Anthropic()

image_path = "test.jpg"

with open(image_path,"rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode("utf-8")

response = client.messages.create(
    model = "claude-sonnet-5",
    max_tokens = 300,
    system = "Analyze the image and describe it.",
    messages=[
        {
            "role":"user",
            "content":[
                {
                    "type":"image",
                    "source":{
                        "type":"base64",
                        "media_type":"image/jpeg",
                        "data":image_data,
                    },
                },
                {
                    "type":"text",
                    "text":"What is in this image. Describe in one sentence",
                },
            ],
        }
    ],
)

print("--Multimodal Response----")
print(response.content[0].text)
print(f"\n Tokens Used - Input:{response.usage.input_tokens}, Output: {response.usage.output_tokens}")