import os
import httpx
import json
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
if not os.environ.get("GOOGLE_API_KEY"):
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("GOOGLE_API_KEY not found")
    exit(1)

def test_http(model_name):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": "Hello"}]
        }]
    }
    
    print(f"Testing {model_name} via HTTP...")
    try:
        response = httpx.post(url, headers=headers, json=data, timeout=30.0)
        if response.status_code == 200:
            print(f"Success! Response: {response.json()}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_http("gemini-1.5-flash")
    test_http("gemini-pro")
