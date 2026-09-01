import asyncio
import os
from google import genai
from google.genai import types

# It is highly recommended to use environment variables instead of hardcoding keys
# To set it in terminal run: export GEMINI_API_KEY="your_key_here"
API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_ACTUAL_API_KEY_HERE")

client = genai.Client(api_key=API_KEY)
model = "gemini-3.1-flash-live-preview"

# Use the official LiveConnectConfig structure
config = types.LiveConnectConfig(
    response_modalities=[types.LiveModality.AUDIO]
)

async def main():
    async with client.aio.live.connect(model=model, config=config) as session:
        print("Session started - Connection alive!")
        
        async def receive_from_gemini():
            try:
                async for response in session.receive():
                    # Handle raw server contents smoothly
                    if response.server_content and response.server_content.model_turn:
                        for part in response.server_content.model_turn.parts:
                            if part.inline_data:
                                print(f"🔊 [Receiving live audio chunk...] {len(part.inline_data.data)} bytes")
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Connection error or closed by server: {e}")

        receive_task = asyncio.create_task(receive_from_gemini())

        print("Sending initial prompt...")
        
        # FIX: send_client_content requires a Content object wrapped in a lists structure
        initial_content = types.Content(
            parts=[types.Part.from_text(text="Hello Gemini! Please say something back to me.")]
        )
        
        # Transmit structured payload to the WebSocket stream
        await session.send_client_content(
            content=initial_content, 
            end_of_turn=True
        )

        # Give the session stream 15 seconds to finish talking before closing down
        await asyncio.sleep(15)
        
        receive_task.cancel()
        print("Session closed.")

if __name__ == "__main__":
    asyncio.run(main())
