import os
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai

load_dotenv(find_dotenv())
if not os.environ.get("GOOGLE_API_KEY"):
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

print("Available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
