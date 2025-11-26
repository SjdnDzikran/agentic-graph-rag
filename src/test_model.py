from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv, find_dotenv
import os
import time

load_dotenv(find_dotenv())
if not os.environ.get("GOOGLE_API_KEY"):
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

def test_model(model_name):
    print(f"Testing model: {model_name}")
    try:
        llm = ChatGoogleGenerativeAI(model=model_name, max_retries=0)
        response = llm.invoke("Hello")
        print(f"Success! Response: {response.content}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_model("gemini-exp-1206")
    test_model("gemini-2.0-flash-thinking-exp")
    test_model("models/gemini-exp-1206")
