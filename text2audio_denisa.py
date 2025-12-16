import os
import time
from dotenv import load_dotenv
import requests
from PIL import Image
from io import BytesIO
import pygame
from openai import OpenAI

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client (will be None if API key missing)
client = None
if API_KEY:
    client = OpenAI(api_key=API_KEY)
else:
    print("Warning: OPENAI_API_KEY not set. AI features will fail until you provide an API key.")

# Initialize pygame mixer for audio playback (safe init)
pygame_available = True
try:
    pygame.mixer.init()
except Exception:
    pygame_available = False
    print("Note: pygame mixer could not be initialized; audio playback may not work in this environment.")


def get_user_name():
    """Get the user's name from input."""
    name = input("Please enter your name: ")
    return name.strip()


def generate_past_life_story(name):
    """Generate a humorous past-life story for the given name.

    Returns a string with the story. If the OpenAI client is not available,
    returns a fallback message.
    """
    prompt = (
        f"Create a funny and entertaining description of who {name} was in their past life. "
        "Include details about their occupation, personality, and some amusing anecdotes. "
        "Make it humorous and engaging."
    )

    if client is None:
        # Fallback story when API key missing
        return f"In a past life, {name} was a mysterious figure who loved adventure and tea. (Provide OPENAI_API_KEY to generate a richer story.)"

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a creative storyteller specializing in humorous past life narratives."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=400,
            temperature=0.8,
        )

        # Extract story text from response
        story = response.choices[0].message.content.strip()
        return story

    except Exception as e:
        print(f"Error generating past life story: {e}")
        return f"In a past life, {name} was a mysterious figure whose story has been lost to time."


def generate_audio_narration(story):
    """Generate audio narration for the past life story and save it to a file.

    Returns the path to the generated audio file or None on failure.
    """
    os.makedirs("output_audio", exist_ok=True)
    timestamp = int(time.time())
    audio_path = f"output_audio/past_life_story_{timestamp}.mp3"

    if client is None:
        print("OpenAI client not available; skipping audio generation.")
        return None

    try:
        # Use text-to-speech endpoint
        # Try a high-pitched 'baby' voice first; if the API rejects it, fall back to a safer voice.
        preferred_voices = ["baby", "highpitched-baby", "alloy"]
        response = None
        last_exc = None
        for voice_name in preferred_voices:
            try:
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice_name,
                    input=story,
                )
                # If we got a response without exception, stop trying further voices
                break
            except Exception as e:
                last_exc = e
                # try next voice
                response = None

        if response is None:
            # Raise the last exception so the outer except block catches and reports it
            raise last_exc

        # Prefer SDK helper to stream to file, otherwise try to write raw bytes
        try:
            response.stream_to_file(audio_path)
        except Exception:
            if hasattr(response, "content") and isinstance(response.content, (bytes, bytearray)):
                with open(audio_path, "wb") as f:
                    f.write(response.content)
            else:
                raise

        print(f"Audio narration has been generated and saved to {audio_path}")
        return audio_path

    except Exception as e:
        print(f"Error generating audio narration: {e}")
        return None


def play_audio(audio_path):
    """Play the generated audio file if possible."""
    if not audio_path or not os.path.exists(audio_path):
        print("Audio file not found; skipping playback.")
        return

    if not pygame_available:
        print("Pygame not available; cannot play audio in this environment.")
        return

    try:
        print("Playing audio narration...")
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Error playing audio: {e}")


def generate_past_life_face(name):
    """Generate an image representing how the user looked in a past life.

    Saves an image to `oracle_symbols/` and returns the image path, or None on failure.
    """
    prompt = (
        f"Generate a realistic portrait of how {name} looked in their past life. "
        "Show their face clearly with appropriate historical clothing and background."
    )

    os.makedirs("oracle_symbols", exist_ok=True)
    timestamp = int(time.time())
    image_path = f"oracle_symbols/{name}_past_life_{timestamp}.png"

    if client is None:
        print("OpenAI client not available; skipping image generation.")
        return None

    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            n=1,
            size="1024x1024",
        )

        image_info = response.data[0]

        # Some SDKs return a URL, others return base64 in b64_json
        if getattr(image_info, "url", None):
            image_response = requests.get(image_info.url)
            image = Image.open(BytesIO(image_response.content))
            image.save(image_path)
        elif getattr(image_info, "b64_json", None):
            import base64

            image_bytes = base64.b64decode(image_info.b64_json)
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            image = Image.open(image_path)
        else:
            raise RuntimeError("Unexpected image response format from API")

        print(f"Past life appearance for {name} saved to {image_path}")
        try:
            image.show()
        except Exception:
            print(f"Cannot display image automatically; open {image_path} to view it.")

        return image_path

    except Exception as e:
        print(f"Error generating past life image: {e}")
        return None


def main():
    print("=== Past Life Oracle ===")
    print("This oracle will reveal how you looked in your past life and tell your story.")
    print("You will receive both a visual representation and an audio narration.")

    name = get_user_name()
    if not name:
        print("No name provided; exiting.")
        return

    story = generate_past_life_story(name)
    print("\nStory:\n", story)

    image_path = generate_past_life_face(name)

    audio_path = generate_audio_narration(story)
    if audio_path:
        play_audio(audio_path)


if __name__ == "__main__":
    main()
