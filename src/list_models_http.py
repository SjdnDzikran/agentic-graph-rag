import os
import httpx
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
if not os.environ.get("GOOGLE_API_KEY"):
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("GOOGLE_API_KEY not found")
    exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

print(f"Querying {url}...")
try:
    response = httpx.get(url)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print("Available models:")
        for m in models:
            if '1.5' in m['name'] and 'generateContent' in m.get('supportedGenerationMethods', []):
                print(m['name'])
    else:
        print(f"Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Exception: {e}")
