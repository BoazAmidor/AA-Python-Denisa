import os
import time
import requests
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=API_KEY)

def generate_image(prompt):
    """Generate an image using DALL-E based on the prompt."""
    print(f"\nGenerating image from prompt: '{prompt}'")
    
    try:
        response = client.images.generate(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        
        image_url = response.data[0].url
        
        # Download the image
        image_response = requests.get(image_url)
        image = Image.open(BytesIO(image_response.content))
        
        # Create output directory if it doesn't exist
        os.makedirs("telephone_game", exist_ok=True)
        
        # Save the image with a timestamp
        timestamp = int(time.time())
        image_path = f"telephone_game/image_{timestamp}.png"
        image.save(image_path)
        
        print(f"Image saved to {image_path}")
        
        # Try to display the image
        try:
            image.show()
        except Exception as e:
            print(f"Note: Could not display the image automatically. Please open {image_path} to view it.")
        
        return image_url, image_path
    
    except Exception as e:
        print(f"Error generating image: {e}")
        return None, None

def analyze_image(image_url):
    """Analyze the image using GPT-4o and generate a description."""
    print("\nAnalyzing the image...")
    
    try:
        # For image_path, we'll download the image and convert to base64
        if image_url.startswith('http'):
            # Download the image
            image_response = requests.get(image_url)
            image_data = BytesIO(image_response.content).getvalue()
            import base64
            # Convert to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            # Create the proper data URL format
            data_url = f"data:image/jpeg;base64,{base64_image}"
        else:
            # If it's a local path
            with open(image_url, "rb") as image_file:
                image_data = image_file.read()
                import base64
                base64_image = base64.b64encode(image_data).decode('utf-8')
                data_url = f"data:image/jpeg;base64,{base64_image}"
        
        messages = [
            {
                "role": "system",
                "content": "You are a kid playing a game of telephone."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in detail. What do you see?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url,
                        },
                    },
                ],
            }
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o",  # Updated to use gpt-4o which has vision capabilities
            messages=messages,
            temperature=0.9,
            max_tokens=300
        )
        
        description = response.choices[0].message.content
        print(f"\nImage description: {description}")
        
        return description
    
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return None

def run_telephone_game(initial_prompt, cycles=3):
    """Run the AI Telephone Game for the specified number of cycles."""
    print("=== AI Telephone Game with Images ===")
    print(f"Starting with prompt: '{initial_prompt}'")
    print(f"Running for {cycles} cycles")
    
    # Create a log file to track the game
    os.makedirs("telephone_game", exist_ok=True)
    timestamp = int(time.time())
    log_path = f"telephone_game/game_log_{timestamp}.txt"
    
    with open(log_path, "w") as log_file:
        log_file.write(f"=== AI Telephone Game with Images ===\n")
        log_file.write(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Initial Prompt: {initial_prompt}\n\n")
        
        current_prompt = initial_prompt
        
        for cycle in range(1, cycles + 1):
            print(f"\n--- Cycle {cycle} of {cycles} ---")
            log_file.write(f"--- Cycle {cycle} of {cycles} ---\n")
            
            # Generate image from the current prompt
            image_url, image_path = generate_image(current_prompt)
            if not image_url:
                print(f"Failed to generate image in cycle {cycle}. Stopping the game.")
                log_file.write(f"Failed to generate image in cycle {cycle}. Game stopped.\n")
                break
            
            log_file.write(f"Prompt: {current_prompt}\n")
            log_file.write(f"Image Path: {image_path}\n")
            
            # Analyze the image to get a new description
            new_description = analyze_image(image_url)
            if not new_description:
                print(f"Failed to analyze image in cycle {cycle}. Stopping the game.")
                log_file.write(f"Failed to analyze image in cycle {cycle}. Game stopped.\n")
                break
            
            log_file.write(f"Description: {new_description}\n\n")
            
            # Use the description as the next prompt
            current_prompt = new_description
            
            # Add a small delay to avoid rate limiting
            if cycle < cycles:
                print("Waiting a moment before the next cycle...")
                time.sleep(2)
        
        log_file.write(f"\nGame completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"\nAI Telephone Game completed! Log saved to {log_path}")

def main():
    """Main function to run the AI Telephone Game."""
    print("Welcome to the AI Telephone Game with Images!")
    print("This game generates an image from a prompt, then describes that image to create a new prompt, and so on.")
    
    initial_prompt = input("Enter your initial prompt for the first image: ")
    
    try:
        cycles = int(input("How many cycles would you like to run? (default: 3): ") or 3)
    except ValueError:
        cycles = 3
        print("Invalid input. Using default of 3 cycles.")
    
    run_telephone_game(initial_prompt, cycles)

if __name__ == "__main__":
    main()