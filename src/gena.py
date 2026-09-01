import asyncio
import os
from google import genai
from google.genai import types

# Fetch the key from system environment variables
API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_ACTUAL_API_KEY_HERE")

client = genai.Client(api_key=API_KEY)
model = "gemini-3.1-flash-live-preview"

# Standard dictionary configuration
config = {
    "response_modalities": ["AUDIO"]
}

async def main():
    async with client.aio.live.connect(model=model, config=config) as session:
        print("Session started - Connection alive!")
        
        async def receive_from_gemini():
            try:
                async for response in session.receive():
                    # Unpack server stream data
                    if response.server_content and response.server_content.model_turn:
                        for part in response.server_content.model_turn.parts:
                            if part.inline_data:
                                print(f"🔊 [Receiving live audio chunk...] {len(part.inline_data.data)} bytes")
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"\nConnection closed by server: {e}")

        receive_task = asyncio.create_task(receive_from_gemini())

        print("Sending initial prompt...")
        
        # FIX: Structure inside a simple dictionary block to prevent argument mismatches
        # The SDK natively parses standard Live Client dictionary structures cleanly.
        payload = {
            "turns": [
                {
                    "role": "user",
                    "parts": [{"text": "Hello Gemini! Please say something back to me."}]
                }
            ]
        }
        
        # Transmit via keyword argument unpacking to bypass strict keyword checking
        await session.send_client_content(
            chunks=payload,
            end_of_turn=True
        )

        # Allow 15 seconds of streaming data before closing down
        await asyncio.sleep(15)
        
        receive_task.cancel()
        print("Session closed cleanly.")

if __name__ == "__main__":
    asyncio.run(main())
