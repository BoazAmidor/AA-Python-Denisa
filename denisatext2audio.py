import os
import time
import json
from dotenv import load_dotenv
import requests
from PIL import Image
from io import BytesIO
import pygame
from openai import OpenAI

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY)

# Initialize pygame mixer for audio playback
pygame.mixer.init()

def get_user_name():
    """Get the user's name from input."""
    name = input("Please enter your name: ")
    return name

def generate_past_life_story(name):
    """Generate a story about the user's past life."""
    try:
        # Create a prompt for the story generation
        prompt = f"Create a funny and entertaining description of who {name} was in their past life. Include details about their occupation, personality, and some amusing anecdotes. Make it humorous and engaging."
        
        # Generate the story using OpenAI's API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a creative storyteller specializing in humorous past life narratives."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.8
        )
        
        # Extract the story from the response
        story = response.choices[0].message.content.strip()
        
        print(f"\nGenerating a story about {name}'s past life...")
        print("\n" + story + "\n")
        
        return story
    
    except Exception as e:
        print(f"Error generating past life story: {e}")
        return f"In a past life, {name} was a mysterious figure whose story has been lost to time."

def generate_audio_narration(story):
    """Generate audio narration for the past life story."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs("output_audio", exist_ok=True)
        
        # Generate a timestamp for the filename
        timestamp = int(time.time())
        audio_path = f"output_audio/past_life_story_{timestamp}.mp3"
        
        # Generate audio using OpenAI's Text-to-Speech API
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",  # Using a higher pitched voice to approximate the request
            input=story
        )
        
        # Save the audio file
        with open(audio_path, 'wb') as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
        
        print(f"Audio narration has been generated and saved to {audio_path}")
        return audio_path
    
    except Exception as e:
        print(f"Error generating audio narration: {e}")
        return None

def play_audio(audio_path):
    """Play the generated audio file."""
    try:
        if audio_path and os.path.exists(audio_path):
            print(f"Playing audio narration...")
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
    
    except Exception as e:
        print(f"Error playing audio: {e}")

def generate_past_life_face(name):
    """Generate an image of how the person looked in their past life."""
    # Create a detailed prompt for the image generation
    prompt = f"""Generate a realistic portrait of how {name} looked in their past life. Show their face clearly with appropriate period clothing and background."""
    
    try:
        # Generate the image using DALL-E
        response = client.images.generate(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        
        # Get the image URL
        image_url = response.data[0].url
        
        # Download the image
        image_response = requests.get(image_url)
        image = Image.open(BytesIO(image_response.content))
        
        # Create output directory if it doesn't exist
        os.makedirs("oracle_symbols", exist_ok=True)
        
        # Save the image with a timestamp to avoid overwriting
        timestamp = int(time.time())
        image_path = f"oracle_symbols/{name}_past_life_{timestamp}.png"
        image.save(image_path)
        
        print(f"\nPast life appearance for {name} has been generated and saved to {image_path}")
        
        # Display the image if in an environment that supports it
        try:
            image.show()
        except Exception as e:
            print(f"Note: Could not display the image automatically. Please open {image_path} to view it.")
        
        return image_path
    
    except Exception as e:
        print(f"Error generating past life image: {e}")
        return None

def main():
    """Main function to run the oracle."""
    print("=== Past Life Oracle ===")
    print("This oracle will reveal how you looked in your past life and tell your story.")
    print("You will receive both a visual representation and an audio narration.")
    
    name = get_user_name()
    
    # Generate a story about the past life
    story = generate_past_life_story(name)
    
    # Generate the past life face image
    image_path = generate_past_life_face(name)
    
    # Generate audio narration of the story
    audio_path = generate_audio_narration(story)
    
    # Play the audio narration
    if audio_path:
        play_audio(audio_path)

if __name__ == "__main__":
    main()