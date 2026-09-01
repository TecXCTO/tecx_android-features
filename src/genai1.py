import asyncio
import json
import os
from typing import Any, Dict, List
# 1. Import the latest GenAI library and dotenv
from google import genai
from dotenv import load_dotenv
from src.utils.helpers import configure_agent_logger

logger = configure_agent_logger()

# 2. Load environment variables from your external .env file at the top-level
load_dotenv()

class OptionsSpreadResearcher:
    """
    Research layer utilizing the modern Google GenAI API client to identify 
    defined-risk option structures based on Implied Volatility parameters.
    """
    def __init__(self):
        # The new SDK automatically detects the GEMINI_API_KEY environment variable.
        # However, passing it explicitly ensures compatibility with custom variable names.
        api_key = os.getenv("GEMINI_API_KEY")
        
        if api_key:
            # 3. Use the new unified Client syntax
            self.client = genai.Client(api_key=api_key)
            # Store the preferred model string identifier 
            self.model_name = 'gemini-2.5-flash'
        else:
            self.client = None
            self.model_name = None
            logger.warning("GEMINI_API_KEY not found in environment variables.")

    async def research_spreads(self, prompt: str) -> str:
        """Example method showing how to generate content using the new SDK."""
        if not self.client:
            raise ValueError("API Client is not initialized.")
            
        # 4. Use the consolidated `client.models.generate_content` syntax
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text
