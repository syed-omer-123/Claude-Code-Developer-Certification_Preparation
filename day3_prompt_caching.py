import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

large_system_context = """
You are an expert enterprise software architect and security auditor. 
Your job is to analyze complex codebases, map out microservice dependencies, 
and enforce rigid compliance rules across multiple software stacks.

Here is the master reference compliance standard for 2026:
1. All database passwords must use dynamic secret management (e.g., Vault).
2. Hardcoded API keys or plaintext credentials are critical violations (CWE-798).
3. All network requests must use TLS 1.3 encryption.
4. Logging must never expose Personally Identifiable Information (PII).
[Simulate 500+ more words of extensive compliance rules, architectural blueprints, 
and coding guidelines to cross the minimum token threshold required for caching...]
"""

print("Sending Request 1 (this will trigger the cache write).....")

response_1 = client.messages.create(
    model = "claude-sonnet-5",
    max_tokens=100,
    system = [
        {
            "type":"text",
            "text": large_system_context,
            "cache_control":{"type":"ephemeral"}
        }
    ],
    messages = [
        {
            "role":"user",
            "content":"Summarize rule number 2 in one sentence."
        }
    ]
)

response_1_text = next((block.text for block in response_1.content if block.type == "text"), "no text found")

print(f"Response 1 Text: {response_1_text}")
print("--- Usage Metadata (Request 1) ---")
print(f"Input Tokens (Base): {response_1.usage.input_tokens}")
print(f"Cache Creation Input Tokens (Write): {response_1.usage.cache_creation_input_tokens}")
print(f"Cache Read Input Tokens (Read): {response_1.usage.cache_read_input_tokens}")

print("\n--------------------------------------------------\n")

print("Sending Request 2(Identical Prefix- This will trigger the cache Read.)")

response_2 = client.messages.create(
    model = "claude-sonnet-5",
    max_tokens = 100,
    system = [{
        "type":"text",
        "text":large_system_context,
        "cache_control":{"type":"ephemeral"}
        }
    ],
    messages = [
        {
            "role":"user",
            "content":"Summarize rule number 3 in one sentence."
        }
    ]
)

response_2_text = next((block.text for block in response_2.content if block.type == "text"), "no text found")

print(f"Response 2 Text: {response_2_text}")
print("--- Usage Metadata (Request 2) ---")
print(f"Input Tokens (Base): {response_2.usage.input_tokens}")
print(f"Cache Creation Input Tokens (Write): {response_2.usage.cache_creation_input_tokens}")
print(f"Cache Read Input Tokens (Read): {response_2.usage.cache_read_input_tokens}")