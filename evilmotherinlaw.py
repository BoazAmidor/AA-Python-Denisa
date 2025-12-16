import os
import base64
import argparse
import shutil
import textwrap
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI


# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("Error: OPENAI_API_KEY not set. Add it to your .env or export it in the environment.")


# Initialize the OpenAI client
client = OpenAI(api_key=API_KEY)


def encode_image_to_data_url(path: str) -> str | None:
    """Encode a local image file to a data URL (data:image/...;base64,...) or return None if not found.

    Returns the data URL string when the path exists and is readable. Supports common extensions.
    """
    p = Path(path.strip("'\"")).expanduser()
    if not p.exists() or not p.is_file():
        return None
    ext = p.suffix.lower().lstrip('.')
    # Map some common extensions to MIME types
    mime = {
        'jpg': 'jpeg',
        'jpeg': 'jpeg',
        'png': 'png',
        'gif': 'gif',
        'webp': 'webp'
    }.get(ext, 'jpeg')
    try:
        with p.open('rb') as f:
            data = f.read()
    except Exception:
        return None
    b64 = base64.b64encode(data).decode('ascii')
    return f"data:image/{mime};base64,{b64}"


def pretty_print(text: str, width: int | None = None) -> None:
    """Wrap and print text to the current terminal width (preserves blank lines).

    If width is None, detect terminal width with a sensible fallback.
    """
    if width is None:
        width = shutil.get_terminal_size(fallback=(80, 24)).columns
    # Preserve existing blank lines and wrap each paragraph
    paragraphs = text.splitlines()
    for para in paragraphs:
        if not para.strip():
            print()
        else:
            print(textwrap.fill(para, width=width))


def build_messages(image_url_or_dataurl: str):
    """Build the messages payload for the chat completion API."""
    return [
        {
            "role": "system",
            "content": (
                "You are the opposite of a polite, constructive critic who focuses on visual details and provides "
                "respectful, descriptive observations about images. Offer helpful, non-personal critiques "
                "and avoid insults or personal attacks."
            )
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What do you see in this image?"},
                {"type": "image_url", "image_url": {"url": image_url_or_dataurl}}
            ]
        }
    ]


def main():
    parser = argparse.ArgumentParser(description='Analyze an image using the OpenAI chat vision model.')
    parser.add_argument('image', nargs='?', default=None,
                        help='Local image path or public http(s) image URL. If omitted, a default remote image is used.')
    parser.add_argument('--nowrap', action='store_true', default=False,
                        help='Disable wrapping of the model output (print raw).')
    args = parser.parse_args()

    default_remote = "https://www.weizenbaum-institut.de/media/Personenbilder/fg2_kera_web.jpg"
    image_input = args.image or default_remote

    # If the input looks like a local path (exists), encode it to a data URL
    data_url = encode_image_to_data_url(image_input)
    if data_url:
        payload_url = data_url
    else:
        # Treat as URL; validate basic scheme
        if image_input.startswith(('http://', 'https://')):
            payload_url = image_input
        else:
            raise SystemExit(f"Error: local file not found and value is not a valid http(s) URL: {image_input}")

    messages = build_messages(payload_url)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=300
        )
        resp_text = response.choices[0].message.content
        if args.nowrap:
            print(resp_text)
        else:
            pretty_print(resp_text)
    except Exception as e:
        print("Error calling API:", str(e))


if __name__ == '__main__':
    main()