import os
import time
import requests
import streamlit as st
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI
import base64
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telephone_game_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")

# Initialize session state
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        'running': False,
        'cycles': [],
        'log_path': None
    }

def get_client():
    """Get OpenAI client with API key."""
    api_key = st.session_state.get('api_key', API_KEY)
    if api_key:
        return OpenAI(api_key=api_key)
    return None

def generate_image(prompt):
    """Generate an image using DALL-E based on the prompt."""
    client = get_client()
    if not client:
        logger.error("No OpenAI client available")
        return None, None, None
    
    logger.info(f"Generating image from prompt: '{prompt[:100]}...'")
    
    try:
        response = client.images.generate(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        
        image_url = response.data[0].url
        logger.info(f"Image generated successfully: {image_url}")
        
        # Download the image
        image_response = requests.get(image_url)
        image = Image.open(BytesIO(image_response.content))
        
        # Create output directory if it doesn't exist
        os.makedirs("telephone_game", exist_ok=True)
        
        # Save the image with a timestamp
        timestamp = int(time.time())
        image_path = f"telephone_game/image_{timestamp}.png"
        image.save(image_path)
        logger.info(f"Image saved to {image_path}")
        
        return image, image_path, image_url
    
    except Exception as e:
        logger.error(f"Error generating image: {e}", exc_info=True)
        st.error(f"Error generating image: {e}")
        return None, None, None, None

def analyze_image(image_url):
    """Analyze the image using GPT-4o and generate a description."""
    client = get_client()
    if not client:
        logger.error("No OpenAI client available for image analysis")
        return None
    
    logger.info("Analyzing image with GPT-4o vision...")
    
    try:
        messages = [
            {
                "role": "system",
                "content": "You are a creative and detailed image analyst. Describe what you see in the image with vivid details that could be used to recreate a similar but not identical image. Focus on the main elements, colors, composition, and mood. Your description should be 3-4 sentences long."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in detail. What do you see?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                    },
                ],
            }
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=300
        )
        
        description = response.choices[0].message.content
        logger.info(f"Image analyzed successfully: '{description[:100]}...'")
        return description
    
    except Exception as e:
        logger.error(f"Error analyzing image: {e}", exc_info=True)
        st.error(f"Error analyzing image: {e}")
        return None

def main():
    st.set_page_config(
        page_title="AI Telephone Game",
        page_icon="📞",
        layout="wide"
    )
    
    st.title("📞 AI Telephone Game with Images")
    st.markdown("""
    This game demonstrates how AI-generated content can drift through multiple iterations:
    1. Start with a text prompt
    2. Generate an image from that prompt (DALL-E)
    3. Analyze the image to get a description (GPT-4o Vision)
    4. Use that description to generate a new image
    5. Repeat and watch the concept evolve!
    """)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key = st.text_input("OpenAI API Key", type="password", value=API_KEY or "")
        if api_key:
            st.session_state.api_key = api_key
        
        cycles = st.slider("Number of cycles", min_value=1, max_value=5, value=3)
        
        if st.button("🗑️ Clear Game History"):
            logger.info("Clearing game history")
            st.session_state.game_state = {
                'running': False,
                'cycles': [],
                'log_path': None
            }
            st.rerun()
        
        st.markdown("---")
        st.subheader("📋 Logs")
        
        # Display application log
        if os.path.exists('telephone_game_app.log'):
            if st.button("🔍 View Application Log"):
                with open('telephone_game_app.log', 'r') as f:
                    log_content = f.read()
                st.text_area("Application Log", log_content, height=300)
            
            with open('telephone_game_app.log', 'r') as f:
                app_log_content = f.read()
            st.download_button(
                label="📥 Download App Log",
                data=app_log_content,
                file_name=f"app_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        
        # Display current game log
        if st.session_state.game_state['log_path'] and os.path.exists(st.session_state.game_state['log_path']):
            if st.button("📖 View Current Game Log"):
                with open(st.session_state.game_state['log_path'], 'r') as f:
                    game_log_content = f.read()
                st.text_area("Current Game Log", game_log_content, height=300)
    
    # Main content
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Start the Game")
        initial_prompt = st.text_area(
            "Initial Prompt",
            placeholder="e.g., A cat wearing a wizard hat in a mystical forest",
            height=100
        )
        
        start_button = st.button("🎮 Start Telephone Game", type="primary", disabled=st.session_state.game_state['running'])
    
    with col2:
        if not get_client():
            st.warning("⚠️ Please enter your OpenAI API key in the sidebar to start.")
        elif start_button and initial_prompt:
            logger.info(f"Starting new game with prompt: '{initial_prompt[:100]}...'")
            st.session_state.game_state = {
                'running': True,
                'cycles': [],
                'log_path': None
            }
            
            # Create log file
            os.makedirs("telephone_game", exist_ok=True)
            timestamp = int(time.time())
            log_path = f"telephone_game/game_log_{timestamp}.txt"
            st.session_state.game_state['log_path'] = log_path
            logger.info(f"Created game log at: {log_path}")
            
            with open(log_path, "w") as log_file:
                log_file.write(f"=== AI Telephone Game with Images ===\n")
                log_file.write(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                log_file.write(f"Initial Prompt: {initial_prompt}\n\n")
            
            current_prompt = initial_prompt
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Run the game
            for cycle in range(1, cycles + 1):
                logger.info(f"Starting cycle {cycle} of {cycles}")
                status_text.text(f"🔄 Cycle {cycle} of {cycles}: Generating image...")
                progress_bar.progress((cycle - 1) / cycles)
                
                # Generate image
                image, image_path, image_url = generate_image(current_prompt)
                if not image:
                    logger.error(f"Failed to generate image in cycle {cycle}")
                    st.error(f"Failed to generate image in cycle {cycle}")
                    break
                
                status_text.text(f"🔄 Cycle {cycle} of {cycles}: Analyzing image...")
                
                # Analyze image
                new_description = analyze_image(image_url)
                if not new_description:
                    logger.error(f"Failed to analyze image in cycle {cycle}")
                    st.error(f"Failed to analyze image in cycle {cycle}")
                    break
                
                # Store cycle data
                cycle_data = {
                    'cycle': cycle,
                    'prompt': current_prompt,
                    'image': image,
                    'image_path': image_path,
                    'description': new_description
                }
                st.session_state.game_state['cycles'].append(cycle_data)
                
                # Log to file
                with open(log_path, "a") as log_file:
                    log_file.write(f"--- Cycle {cycle} of {cycles} ---\n")
                    log_file.write(f"Prompt: {current_prompt}\n")
                    log_file.write(f"Image Path: {image_path}\n")
                    log_file.write(f"Description: {new_description}\n\n")
                
                # Update prompt for next cycle
                current_prompt = new_description
                
                if cycle < cycles:
                    time.sleep(1)  # Small delay between cycles
            
            progress_bar.progress(1.0)
            status_text.text("✅ Game completed!")
            logger.info("Game completed successfully")
            
            with open(log_path, "a") as log_file:
                log_file.write(f"\nGame completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            st.session_state.game_state['running'] = False
    
    # Display results
    if st.session_state.game_state['cycles']:
        st.markdown("---")
        st.header("🎯 Game Results")
        
        for cycle_data in st.session_state.game_state['cycles']:
            with st.expander(f"🔄 Cycle {cycle_data['cycle']}", expanded=True):
                col_img, col_text = st.columns([1, 1])
                
                with col_img:
                    st.image(cycle_data['image'], caption=f"Cycle {cycle_data['cycle']} Image", use_container_width=True)
                
                with col_text:
                    st.markdown("**Prompt:**")
                    st.info(cycle_data['prompt'])
                    
                    st.markdown("**AI Description:**")
                    st.success(cycle_data['description'])
        
        # Download log file
        if st.session_state.game_state['log_path']:
            with open(st.session_state.game_state['log_path'], 'r') as f:
                log_content = f.read()
            
            st.download_button(
                label="📥 Download Game Log",
                data=log_content,
                file_name=f"telephone_game_{int(time.time())}.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()