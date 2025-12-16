import os
import time
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import requests
from PIL import Image, ImageDraw, ImageStat
from io import BytesIO

# Try to load from .env file, but don't fail if it doesn't exist
try:
    load_dotenv()
except Exception as e:
    st.warning("Could not load .env file, but continuing anyway...")

# Initialize the OpenAI client with API key from environment or Streamlit secrets
API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
if not API_KEY:
    st.error("OpenAI API key not found. Please set it in Streamlit secrets or .env file.")
    st.stop()

client = OpenAI(api_key=API_KEY)

def generate_sacred_symbol(name):
    """Generate a sacred symbol based on the user's name."""
    # Create a detailed prompt for the image generation
    prompt = f"""Generate a unique, sacred symbol that represents a personal cosmic message for {name}. 
    The glyph should resemble ancient runes, celestial diagrams, or alchemical sigils.
    It should include hidden elements that hint at an interpretation, with layered, intersecting lines and geometric symmetry.
    The symbol should be mystical, intricate, and personalized to the essence of the name {name}.
    Use a dark background with luminous, glowing lines in gold, silver, or ethereal blue. Include at least one distinct purple element (for example a purple star, sigil, or glowing accent) that stands out visually.
    The symbol should appear as if it was discovered in an ancient grimoire or celestial map. Incorporate subtle, respectful Jewish-inspired motifs if appropriate."""
    
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
        image = Image.open(BytesIO(image_response.content)).convert("RGBA")

        # Detect whether the generated image is effectively grayscale / desaturated.
        # If so, add a visible purple accent so the final output will include purple.
        try:
            hsv = image.convert('HSV')
            stat = ImageStat.Stat(hsv)
            # HSV channels: H, S, V. stat.mean[1] is mean saturation (0-255)
            mean_saturation = stat.mean[1] / 255.0
        except Exception:
            mean_saturation = 1.0

        if mean_saturation < 0.15:
            # Add a clear purple accent in the lower-right corner.
            # Create an overlay and draw a solid purple circle, then blur it to form a glow.
            from PIL import ImageFilter

            overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            w, h = image.size
            # Strong purple (RGB) and high alpha for visibility
            purple_rgb = (106, 13, 173)
            alpha = 220
            radius = int(min(w, h) * 0.12)
            cx = int(w * 0.78)
            cy = int(h * 0.78)

            # Draw a solid purple disc
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=(purple_rgb[0], purple_rgb[1], purple_rgb[2], alpha))

            # Create a blurred version for glow
            glow = overlay.filter(ImageFilter.GaussianBlur(radius // 2 if radius // 2 > 0 else 4))

            # Composite glow then the solid disc to make purple dominant
            image = Image.alpha_composite(image, glow)
            image = Image.alpha_composite(image, overlay)
        
        # Create output directory if it doesn't exist
        os.makedirs("oracle_symbols", exist_ok=True)
        
        # Save the image with a timestamp to avoid overwriting
        timestamp = int(time.time())
        image_path = f"oracle_symbols/{name}_sacred_symbol_{timestamp}.png"
        image.save(image_path)
        
        return image, image_path
    
    except Exception as e:
        st.error(f"Error generating sacred symbol: {e}")
        return None, None

def main():
    st.set_page_config(
        page_title="Sacred Symbol Oracle",
        page_icon="🔮",
        layout="centered"
    )
    
    st.title("🔮 Sacred Symbol Oracle")
    st.markdown("""
    Welcome to the Sacred Symbol Oracle! This mystical tool will generate a unique sacred symbol 
    based on your name, containing hidden elements that hint at a personal cosmic message.
    """)
    
    # Sidebar for API key input
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("OpenAI API Key", type="password", value=API_KEY or "")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            client.api_key = api_key
    
    # Main content
    name = st.text_input("Enter your name:", placeholder="Your name here...")
    
    if st.button("Generate Sacred Symbol"):
        if not name:
            st.warning("Please enter your name first!")
        elif not client.api_key:
            st.error("Please enter your OpenAI API key in the sidebar!")
        else:
            with st.spinner("Generating your sacred symbol... This may take a moment."):
                image, image_path = generate_sacred_symbol(name)
                
                if image:
                    # Display image (caption rendered separately so we can color it purple)
                    st.image(image, use_container_width=True)

                    # Purple caption (uses HTML so color can be applied)
                    st.markdown(
                        f"<div style='margin-top:8px; font-weight:600; color:purple;'>Sacred Symbol for {name}</div>",
                        unsafe_allow_html=True,
                    )

                    # Interpretation with a highlighted purple phrase
                    st.markdown(f"### Interpretation of {name}'s Sacred Symbol:")
                    st.markdown(
                        (
                            "This unique cosmic glyph contains elements that resonate with "
                            f"<span style='color:purple; font-weight:600'>{name}</span>. "
                            "The intersecting lines represent the convergence of past, present, and future paths. "
                            "Hidden within its geometry are symbols of personal strength and cosmic connection. "
                            "Meditate on this symbol to reveal deeper meanings unique to your journey."
                        ),
                        unsafe_allow_html=True,
                    )
                    
                    # Download button
                    with open(image_path, "rb") as file:
                        st.download_button(
                            label="Download Symbol",
                            data=file,
                            file_name=f"{name}_sacred_symbol.png",
                            mime="image/png"
                        )

if __name__ == "__main__":
    main()