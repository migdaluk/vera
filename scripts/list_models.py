import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    print("Please set it in your .env file or export it in your shell.")
    # Try to look for a dummy key or ask user (simulated)
    # For now, just exit if no key
else:
    print(f"Found API Key: {api_key[:5]}...{api_key[-5:]}")
    genai.configure(api_key=api_key)

    print("\nListing available models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
