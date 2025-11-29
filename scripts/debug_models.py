import os
import google.generativeai as genai
from google.api_core import exceptions

def list_models():
    api_key = input("Enter your Google API Key: ").strip()
    if not api_key:
        print("API Key is required.")
        return

    genai.configure(api_key=api_key)

    print("\nListing available models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except exceptions.PermissionDenied:
        print("Error: Permission Denied. Check your API Key.")
    except exceptions.NotFound:
        print("Error: Endpoint not found. Check your region or API settings.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("This script uses 'google-generativeai' (AI Studio) to list models.")
    list_models()
