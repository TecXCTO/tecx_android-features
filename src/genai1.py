import asyncio
import os
import sys
from google import genai
from dotenv import load_dotenv
from src.utils.helpers import configure_agent_logger

logger = configure_agent_logger()

# Load environment variables from your external .env file
load_dotenv()

class LiveGeminiAssistant:
    """
    A general-purpose, asynchronous AI assistant layer utilizing 
    the modern Google GenAI SDK to stream responses in real time.
    """
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        
        if api_key:
            self.client = genai.Client(api_key=api_key)
            # Use 'gemini-3.5-flash' for stable, continuous free-tier traffic
            self.model_name = 'gemini-3.5-flash'
        else:
            self.client = None
            self.model_name = None
            logger.warning("GEMINI_API_KEY not found in environment variables.")

    async def ask_stream(self, prompt: str):
        """Streams the response chunk-by-chunk live onto the console screen."""
        if not self.client:
            print("\nError: API Client is not initialized. Please verify your .env file setup.")
            return

        try:
            # client.aio hooks into the native async engine
            # generate_content_stream lets text chunks pour in dynamically
            response_stream = await self.client.aio.models.generate_content_stream(
                model=self.model_name,
                contents=prompt
            )
            
            # Print chunks live as they land from Google's cloud servers
            async for chunk in response_stream:
                if chunk.text:
                    print(chunk.text, end="", flush=True)
            print("\n") # Line break at the completion of a full thought
            
        except Exception as e:
            print(f"\n[Execution Error]: {e}\n")

async def main():
    assistant = LiveGeminiAssistant()
    print("==================================================")
    print(f" Live Gemini Chat Initialized ({assistant.model_name})")
    print(" Type your prompt and press Enter. Type 'exit' to quit. ")
    print("==================================================")

    while True:
        # Prompt the user for an input task in the console
        user_prompt = input("\nYou: ").strip()
        
        if not user_prompt:
            continue
        
        if user_prompt.lower() in ['exit', 'quit']:
            print("Exiting live session. Goodbye!")
            break
            
        print("Gemini: ", end="", flush=True)
        # Execute the live asynchronous text stream
        await assistant.ask_stream(user_prompt)

if __name__ == "__main__":
    # Handles async tasks inside terminal environments smoothly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSession interrupted. Exiting...")
