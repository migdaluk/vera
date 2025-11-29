import os
import asyncio
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Mock environment setup (User needs to provide key when running or have it in env)
# os.environ["GOOGLE_API_KEY"] = "..." 
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

async def run_test():
    print("Initializing Agent with native google_search...")
    agent = Agent(
        name="test_researcher",
        model="gemini-flash-latest",
        instruction="You are a researcher. Find out who won the 2024 Super Bowl.",
        tools=[google_search]
    )

    runner = Runner(agent=agent, app_name="test_app", session_service=InMemorySessionService())
    session_id = "test_session"
    await runner.session_service.create_session(app_name="test_app", user_id="user", session_id=session_id)

    # Prepare input message
    user_msg = types.Content(
        role="user",
        parts=[types.Part.from_text(text="Who won the 2024 Super Bowl?")]
    )

    print("Running agent...")
    try:
        async for event in runner.run_async(
            user_id="user",
            session_id=session_id,
            new_message=user_msg
        ):
            if hasattr(event, 'model_content') and event.model_content:
                print(event.model_content.parts[0].text, end="", flush=True)
            elif hasattr(event, 'content') and event.content:
                print(event.content.parts[0].text, end="", flush=True)
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        key = input("Enter Google API Key: ")
        os.environ["GOOGLE_API_KEY"] = key
    
    asyncio.run(run_test())
