"""Quick LLM test with .env loading."""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("="*60)
print("LLM Configuration Test")
print("="*60)

print(f"\nLLM_ENABLED: {os.getenv('LLM_ENABLED')}")
print(f"API_KEY: {os.getenv('OPENAI_API_KEY')[:20]}...")
print(f"Model: {os.getenv('GEMINI_MODEL')}")

# Import and test LLM client
from supervisor.reasoning.llm_client import LLMClient

client = LLMClient()

print(f"\nProvider: {client.provider}")
print(f"Enabled: {client.is_enabled()}")

if client.is_enabled():
    print("\n✅ LLM is ENABLED and ready!")
    print("\nTrying a quick API call...")
    
    response = client.generate(
        "Say 'AI is working!' and nothing else.",
        temperature=0.3,
        max_tokens=10
    )
    
    if response:
        print(f"✅ API Response: {response.strip()}")
        print("\n🎉 LLM reasoning is fully operational!")
    else:
        print("❌ API call failed")
else:
    print("\n❌ LLM is NOT enabled")
