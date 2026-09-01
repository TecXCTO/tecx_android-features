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
