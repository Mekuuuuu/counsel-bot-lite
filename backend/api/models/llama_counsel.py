from unsloth import FastLanguageModel, get_chat_template
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "Mekuu/LLAMA3.1-8b-Counsel-v1.3")

class LlamaCounsel:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = self._get_device()
        self.initialize_model()

    def _get_device(self):
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def initialize_model(self):
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            LLAMA_MODEL,
            token=HUGGINGFACE_TOKEN,
            trust_remote_code=True
        )

        # Apply ChatML template
        self.tokenizer = get_chat_template(
            self.tokenizer,
            chat_template="chatml",
            mapping={"role": "from", "content": "value", "user": "human", "assistant": "gpt"},
        )

        # Load model with Unsloth optimization
        self.model, _ = FastLanguageModel.from_pretrained(
            model_name=LLAMA_MODEL,
            token=HUGGINGFACE_TOKEN,
            dtype=getattr(torch, os.getenv("TORCH_DTYPE", "float16")), # Will auto-use bf16 or fp16 depending on system if set to None
            load_in_4bit=os.getenv("LOAD_IN_4BIT", "true").lower() == "true",
            device_map="auto",
            trust_remote_code=True,
        )

    def generate_response(self, prompt: str) -> str:
        # Format input with chat template
        input_text = self.tokenizer.apply_chat_template(
            [
                {"from": "gpt", "value": "Hello, how are you doing, how can I help you today?"},
                {"from": "human", "value": prompt},
            ],
            tokenize=False,
            add_generation_prompt=True,
        )
        
        # Tokenize and generate
        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=1000,
            temperature=0.7,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )

        # Decode and clean up response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the prompt from the response
        response = response.replace(input_text, "").strip()
        return response

# Create singleton instance
llama_counsel = LlamaCounsel()

def generate_response(prompt: str) -> str:
    return llama_counsel.generate_response(prompt) 