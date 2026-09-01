import asyncio
import os
from google import genai
from google.genai import types

# Fetch the key from system environment variables
API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_ACTUAL_API_KEY_HERE")

client = genai.Client(api_key=API_KEY)
model = "gemini-3.1-flash-live-preview"

# FIX: Use simple string literals inside a standard dictionary configuration
config = {
    "response_modalities": ["AUDIO"]
}

async def main():
    async with client.aio.live.connect(model=model, config=config) as session:
        print("Session started - Connection alive!")
        
        async def receive_from_gemini():
            try:
                async for response in session.receive():
                    # Safely unpack the incoming server streaming data
                    if response.server_content and response.server_content.model_turn:
                        for part in response.server_content.model_turn.parts:
                            if part.inline_data:
                                print(f"🔊 [Receiving live audio chunk...] {len(part.inline_data.data)} bytes")
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Connection closed: {e}")

        receive_task = asyncio.create_task(receive_from_gemini())

        print("Sending initial prompt...")
        
        # Structure the payload explicitly using the core Content definitions
        initial_content = types.Content(
            parts=[types.Part.from_text(text="Hello Gemini! Please say something back to me.")]
        )
        
        # Transmit correctly structured content over the websocket pipeline
        await session.send_client_content(
            content=initial_content, 
            end_of_turn=True
        )

        # Allow 15 seconds of streaming data before gracefully closing down
        await asyncio.sleep(15)
        
        receive_task.cancel()
        print("Session closed cleanly.")

if __name__ == "__main__":
    asyncio.run(main())
