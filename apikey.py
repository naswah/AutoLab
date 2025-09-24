import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Get API key from environment
api_key = os.getenv("gemini_api_key")

# Configure Gemini with API key
genai.configure(api_key=api_key)

# Load the model
model = genai.GenerativeModel("gemini-1.5-flash")

# Test with a simple prompt
response = model.generate_content("My name is Naswah.")

print("Response:\n", response.text)