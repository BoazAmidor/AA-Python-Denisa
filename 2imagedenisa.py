import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=API_KEY)

def encode_image(image_path):
    """Encode a local image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(image_source):
    """
    Analyze an image using OpenAI's GPT-4o Vision.
    
    Args:
        image_source: Either a URL (must be publicly accessible) or a local file path
    """
    # Check if it's a local file
    if os.path.exists(image_source):
        print(f"Using local image: {image_source}")
        base64_image = encode_image(image_source)
        image_url = f"data:image/jpeg;base64,{base64_image}"
    else:
        print(f"Using URL: {image_source}")
        image_url = image_source
    
    # Define messages with system and user roles
    messages = [
        {
            "role": "system",
            "content": "Describe the tasks this gate performs for people. Identify signs of those tasks — bars, rotating arms, card reader, green indicator, full height, hidden motor. Explain how each part replaces a guard."
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "For a purpose of a play, make up a name for this gate. Then, describe the tasks this gate performs for people. Identify signs of those tasks — bars, rotating arms, card reader, green indicator, full height, hidden motor. Explain how each part replaces a guard."},
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
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Example 1: Using a public URL (make sure it's accessible)
    # image_source = "https://example.com/photo.jpg"
    
    # Example 2: Using a local file
    # image_source = "path/to/your/image.jpg"
    
    # Default: Ask user for input
    print("🖼️  Image Analysis Tool 🖼️")
    print("You can provide either:")
    print("  1. A local image file path (e.g., photo.jpg)")
    print("  2. A publicly accessible URL (e.g., https://example.com/image.jpg)")
    print("\nNote: Google Lens URLs don't work - download the image first!\n")
    
    image_source = input("Enter image path or URL: ").strip()
    
    if not image_source:
        print("Error: No image source provided.")
    else:
        result = analyze_image(image_source)
        print(f"\n✨ Analysis Result:\n{result}")
