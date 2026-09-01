"""
# Configure the native Google Gemini client using your free environment token
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
  genai.configure(api_key=api_key)
# Use gemini-2.5-flash as it is completely optimized and free
  self.model = genai.GenerativeModel('gemini-2.5-flash')
else:self.model = None
"""
# splt
"""

def __init__(self):
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY")
        self.is_paper = os.getenv("ALPACA_IS_PAPER", "true").lower() == "true
"""
import asyncio
import json
import os
from typing import Any, Dict, List
import google.generativeai as genai
from src.utils.helpers import configure_agent_logger

logger = configure_agent_logger()

class OptionsSpreadResearcher:
    """
    Research layer utilizing Google Gemini API free tier to identify 
    defined-risk option structures based on Implied Volatility parameters.
    """
    def __init__(self):
        # Configure the native Google Gemini client using your free environment token
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            # Use gemini-2.5-flash as it is completely optimized and free
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

    async def analyze_options_chain(self, ticker: str) -> dict:
        logger.info(f"[🔬 Research Agent] Querying active options vectors for {ticker} via MCP data...")
        await asyncio.sleep(0.5)

        # Simulating live market chain metrics from the data layer
        simulated_iv_rank = 65.0
        spot_price = 150.00
        
        if not self.model:
            logger.warning("⚠️ No Gemini API Key discovered. Executing structural fallback strategy.")
            return self._fallback_strategy(ticker, spot_price, simulated_iv_rank)

        # System prompt ordering Gemini to return raw structured JSON strings only
        prompt = (
            f"You are a quantitative options researcher. Analyze this data: Ticker {ticker}, Spot Price {spot_price}, "
            f"IV Rank {simulated_iv_rank}. Because IV Rank is > 50, structure a risk-defined BULL_PUT_SPREAD. "
            f"Return a JSON object with keys: 'strategy' (BULL_PUT_SPREAD), 'underlying' ('{ticker}'), "
            f"'max_risk' (3.50), 'legs' (a list containing two put option leg objects with side, type, strike, expiry)."
            f"Do not write any markdown code fences, only output raw valid JSON text."
        )

        try:
            # Dispatch async loop calling the Google AI Studio container endpoints
            response = self.model.generate_content(prompt)
            parsed_payload = json.loads(response.text.strip())
            return parsed_payload
        except Exception as e:
            logger.error(f"Gemini Inference failed: {e}. Defaulting to fallback safety mechanics.")
            return self._fallback_strategy(ticker, spot_price, simulated_iv_rank)

    def _fallback_strategy(self, ticker: str, spot: float, iv_rank: float) -> dict:
        return {
            "strategy": "BULL_PUT_SPREAD",
            "underlying": ticker.upper(),
            "spot_price": spot,
            "legs": [
                {"side": "SELL", "type": "PUT", "strike": round(spot - 5, 2), "expiry": "2026-10-16"},
                {"side": "BUY", "type": "PUT", "strike": round(spot - 10, 2), "expiry": "2026-10-16"}
            ],
            "net_credit": 1.50,
            "max_risk": 3.50,
            "iv_rank": iv_rank
        }
