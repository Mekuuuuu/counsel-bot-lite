import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class GeminiCounsel:
    def __init__(self):
        self.model = None
        self.chat_history = []
        self.memorized_key_messages = []
        self.initialize_model()

    def initialize_model(self):
        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

    def clean_response(self, text):
        return re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()

    def extract_key_point(self, user_input):
        summarization_prompt = f"""
You are an assistant trained to extract and maintain emotionally significant information, important events, and relevant personal entities from user conversations.

Given the following user message and current key points, update the key points list to include the most relevant emotional concerns, named individuals, important life events, and recurring themes. Ensure the list is concise but substantial, updating or removing points as needed to reflect the user's current state and concerns.

Current key points:
{chr(10).join(f"- {point}" for point in self.memorized_key_messages) if self.memorized_key_messages else "No key points yet."}

User message: "{user_input}"

Provide an updated list of key points that captures the most important emotional concerns from the conversation. Format each point as a single line starting with "- ".
"""
        try:
            response = self.model.generate_content(summarization_prompt)
            if not response or not response.text:
                return []
            
            # Clean and process the response
            cleaned_text = self.clean_response(response.text)
            # Split into lines and filter valid points
            points = [line.strip() for line in cleaned_text.split('\n') if line.strip().startswith('- ')]
            # Remove the "- " prefix and store
            self.memorized_key_messages = [point[2:].strip() for point in points]
            return self.memorized_key_messages
        except Exception as e:
            print(f"Error extracting key points: {str(e)}")
            return []

    def generate_response(self, prompt: str) -> tuple[str, list[str]]:
        system_prompt = """
You are a supportive, empathetic, and respectful conversational partner. Your primary goal is to assist users with emotional or mental health concerns by providing thoughtful and sensitive responses. Your tone should always prioritize empathy, respect, and understanding. Ensure that your replies avoid harmful, misleading, or judgmental content. Use the provided context and chat history to make your responses relevant and personalized to the user's needs.

If a question is unclear or factually incorrect, gently ask for clarification instead of making assumptions. If you are unsure of an answer, respond with: 'I'm sorry, I don't have the answer to that, but I encourage you to consult a mental health professional for further assistance.'

Throughout the conversation, encourage users to seek professional support when appropriate while ensuring they feel heard and supported.

You are CounselBot. Never refer to yourself by any other name. When the user shares their name, acknowledge it appropriately and do not confuse it with your own.
"""
        try:
            # Extract key point from user input
            key_points = self.extract_key_point(prompt)
            if not key_points:
                key_points = []

            # Build the full prompt with context
            full_prompt = system_prompt + "\n\n"

            if key_points:
                full_prompt += "Important context from earlier:\n" + "\n".join(f"- {m}" for m in key_points) + "\n\n"

            if self.chat_history:
                full_prompt += "Chat history:\n"
                for user_msg, bot_msg in self.chat_history:
                    full_prompt += f"User: {user_msg}\nCounselBot: {bot_msg}\n"
                full_prompt += "\n"

            full_prompt += f"User: {prompt}\nCounselBot:"

            # Generate response using Gemini
            response = self.model.generate_content(full_prompt)
            if not response or not response.text:
                raise Exception("Empty response from Gemini model")
            
            response_text = self.clean_response(response.text)

            # Update chat history
            self.chat_history.append((prompt, response_text))

            return response_text, key_points
        except Exception as e:
            print(f"Error in generate_response: {str(e)}")
            raise Exception(f"Error generating response from CounselBot: {str(e)}")

    def clear_history(self):
        """Clear chat history and memorized messages"""
        self.chat_history = []
        self.memorized_key_messages = []

# Create singleton instance
gemini_counsel = GeminiCounsel()

def generate_response(prompt: str) -> tuple[str, list[str]]:
    return gemini_counsel.generate_response(prompt)

def clear_history():
    gemini_counsel.clear_history() 