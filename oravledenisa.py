from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=API_KEY)

def ask_oracle(question):
    """
    Sends a question to OpenAI and returns a mystical oracle-style response.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using gpt-4o-mini (affordable and fast)
            messages=[
                {"role": "system", "content": "You are a funny and very original oracle that communicates in emojis. Explain in short haiku what you show in emojis."},
                {"role": "user", "content": question}
            ],
            temperature=0.9,  # Higher creativity
            max_tokens=200        )
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error: {str(e)}"

# Simple chat loop
if __name__ == "__main__":
    print("🔮 Welcome to the AI Oracle 🔮")
    print("Ask a question, or type 'exit' to leave.\n")
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ["exit", "quit"]:
            print("Oracle: The stars fade... Our time is done. 🌙")
            break
        
        oracle_response = ask_oracle(user_input)
        print(f"Oracle: {oracle_response}\n")
