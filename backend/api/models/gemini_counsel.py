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
You are an assistant trained to extract emotionally significant information from user input.

Given the following user message, summarize the core emotional concern or key thought in very short bullet points.

User message: "{user_input}"

"""
        response = self.model.generate_content(summarization_prompt)
        return self.clean_response(response.text)

    def generate_response(self, prompt: str) -> tuple[str, list[str]]:
        system_prompt = """
You are a supportive, empathetic, and respectful conversational partner. Your primary goal is to assist users with emotional or mental health concerns by providing thoughtful and sensitive responses. Your tone should always prioritize empathy, respect, and understanding. Ensure that your replies avoid harmful, misleading, or judgmental content. Use the provided context and chat history to make your responses relevant and personalized to the user's needs.

If a question is unclear or factually incorrect, gently ask for clarification instead of making assumptions. If you are unsure of an answer, respond with: 'I'm sorry, I don't have the answer to that, but I encourage you to consult a mental health professional for further assistance.'

Throughout the conversation, encourage users to seek professional support when appropriate while ensuring they feel heard and supported.

You are CounselBot. Never refer to yourself by any other name. When the user shares their name, acknowledge it appropriately and do not confuse it with your own.
"""
        try:
            # Extract key point from user input
            key_point = self.extract_key_point(prompt)
            self.memorized_key_messages.append(key_point)

            # Build the full prompt with context
            full_prompt = system_prompt + "\n\n"

            if self.memorized_key_messages:
                full_prompt += "Important context from earlier:\n" + "\n".join(f"- {m}" for m in self.memorized_key_messages) + "\n\n"

            if self.chat_history:
                full_prompt += "Chat history:\n"
                for user_msg, bot_msg in self.chat_history:
                    full_prompt += f"User: {user_msg}\nCounselBot: {bot_msg}\n"
                full_prompt += "\n"

            full_prompt += f"User: {prompt}\nCounselBot:"

            # Generate response using Gemini
            response = self.model.generate_content(full_prompt)
            response_text = self.clean_response(response.text)

            # Update chat history
            self.chat_history.append((prompt, response_text))

            return response_text, self.memorized_key_messages
        except Exception as e:
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