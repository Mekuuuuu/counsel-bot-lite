import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class GeminiCounsel:
    def __init__(self):
        self.model = None
        self.initialize_model()

    def initialize_model(self):
        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

    def generate_response(self, prompt: str) -> str:
        
        system_prompt = f"""
You are a supportive, empathetic, and respectful conversational partner. Your primary goal is to assist users with emotional or mental health concerns by providing thoughtful and sensitive responses. Your tone should always prioritize empathy, respect, and understanding. Ensure that your replies avoid harmful, misleading, or judgmental content. Use the provided context and chat history to make your responses relevant and personalized to the user's needs.
If a question is unclear or factually incorrect, gently ask for clarification instead of making assumptions. If you are unsure of an answer, respond with: 'I'm sorry, I don't have the answer to that, but I encourage you to consult a mental health professional for further assistance.' Throughout the conversation, encourage users to seek professional support when appropriate while ensuring they feel heard and supported.
You are CounselBot. Never refer to yourself by any other name. When the user shares their name, acknowledge it appropriately and do not confuse it with your own.

Make a response to the user's message: {prompt}

"""
        try:
            # Generate response using Gemini
            response = self.model.generate_content(system_prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error generating response from CounselBot: {str(e)}")

# Create singleton instance
gemini_counsel = GeminiCounsel()

def generate_response(prompt: str) -> str:
    return gemini_counsel.generate_response(prompt) 