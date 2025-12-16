#python -m venv venv    
#venv\Scripts\activate
# pip install openai python-dotenv
# pip install --upgrade openai  
# python 2ImageOracle.py


import os
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("Error: OPENAI_API_KEY not set. Add it to your .env or export it in the environment.")

# Initialize the OpenAI client
client = OpenAI(api_key=API_KEY)

# Define the image URL
image_url = "https://www.weizenbaum-institut.de/media/Personenbilder/fg2_kera_web.jpg"

# Define messages with system and user roles
messages = [
    {
        "role": "system",
        "content": (
            "You are a playful but respectful commentator who focuses on visual details and provides humorous, non-personal observations about images. "
            "Avoid insults, personal attacks, or content that targets real people. Keep commentary light-hearted and constructive."
        ),
    },
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Why should you marry her?"},
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                },
            },
        ],
    }
]

# Make a request to analyze the image
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    max_tokens=300
)

# Print the response
print(response.choices[0].message.content)