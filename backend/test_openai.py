import openai
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ Missing OpenAI API key. Check your .env file.")
else:
    try:
        client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Create an Abaqus Python script"}]
        )

        print("✅ OpenAI Response:")
        print(response.choices[0].message.content)

    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")

