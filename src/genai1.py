import asyncio
import json
import os
from typing import Any, Dict, List
# Import the latest GenAI library and dotenv
from google import genai
from dotenv import load_dotenv
from src.utils.helpers import configure_agent_logger

logger = configure_agent_logger()

# Load environment variables from your external .env file
load_dotenv()

class OptionsSpreadResearcher:
    """
    Research layer utilizing the modern Google GenAI API client to identify 
    defined-risk option structures based on Implied Volatility parameters.
    """
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        
        if api_key:
            self.client = genai.Client(api_key=api_key)
            self.model_name = 'gemini-2.5-flash'
        else:
            self.client = None
            self.model_name = None
            logger.warning("GEMINI_API_KEY not found in environment variables.")

    async def research_spreads(self, prompt: str) -> str:
        """Example method showing how to generate content using the new SDK."""
        if not self.client:
            raise ValueError("API Client is not initialized. Check your GEMINI_API_KEY inside your .env file.")
            
        # Use the consolidated client syntax to generate a response
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text

# ==========================================
# ADD THIS RUNNER BLOCK TO THE BOTTOM:
# ==========================================
async def main():
    print("Initializing researcher...")
    researcher = OptionsSpreadResearcher()
    
    test_prompt = "Hello Gemini! Give me a quick 1-sentence explanation of what a Credit Spread is."
    print(f"Sending prompt: '{test_prompt}'\n")
    
    try:
        # Run the asynchronous method
        result = await researcher.research_spreads(test_prompt)
        print("--- Gemini API Response ---")
        print(result)
        print("---------------------------")
    except Exception as e:
        print(f"An error occurred during API execution: {e}")

if __name__ == "__main__":
    # Standard way to trigger an async main function loop
    asyncio.run(main())
