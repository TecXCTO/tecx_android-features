import asyncio

from google import genai


client = genai.Client(api_key="YOUR_API_KEY")

 

model = "gemini-3.1-flash-live-preview"

config = {"response_modalities": ["AUDIO"]}

"""

async def main():

    async with client.aio.live.connect(model=model, config=config) as session:

        print("Session started")

        # Send content...
"""


async def main():
    async with client.aio.live.connect(model=model, config=config) as session:
        print("Session started - Connection alive!")
        
        # 1. Start a background task to constantly listen for audio from Gemini
        async def receive_from_gemini():
            try:
                async for response in session.receive():
                    server_content = response.server_content
                    if server_content is not None and server_content.model_turn is not None:
                        for part in server_content.model_turn.parts:
                            # This is where Gemini sends raw live PCM audio chunks
                            if part.inline_data:
                                print("🔊 [Receiving live audio chunk...]", len(part.inline_data.data), "bytes")
                                # Note: To hear this locally in Termux, you would stream these bytes to PyAudio
            except asyncio.CancelledError:
                pass

        # Spin up the background listening task
        receive_task = asyncio.create_task(receive_from_gemini())

        # 2. Keep the live session open and send a text prompt to kick things off
        print("Sending initial prompt...")
        await session.send(input="Hello Gemini! Please say something back to me.", end_of_turn=True)

        # Keep the session open for 15 seconds to give Gemini time to stream audio back
        await asyncio.sleep(15)
        
        # Clean up background loops on finish
        receive_task.cancel()
        print("Session closed.")






if __name__ == "__main__":

    asyncio.run(main())
