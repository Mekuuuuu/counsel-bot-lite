from transformers import AutoTokenizer, AutoConfig, AutoModel
import torch
import torch.nn.functional as F
import os
from dotenv import load_dotenv
from .custom_bert import CustomModel
import logging
from huggingface_hub import hf_hub_download

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
MENTAL_HEALTH_MODEL = os.getenv("MENTAL_HEALTH_MODEL", "mental/mental-health-classifier")

class MentalHealthBERT:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = self._get_device()
        self.initialize_model()

    def _get_device(self):
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def _remap_state_dict(self, state_dict):
        """Remap the state dict keys from model.* to bert.*"""
        new_state_dict = {}
        for key, value in state_dict.items():
            if key.startswith("model."):
                new_key = "bert." + key[6:]  # Replace "model." with "bert."
                new_state_dict[new_key] = value
            else:
                new_state_dict[key] = value
        return new_state_dict

    def initialize_model(self):
        try:
            # Initialize BERT model for mental health classification
            logger.info(f"Loading tokenizer from {MENTAL_HEALTH_MODEL}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                MENTAL_HEALTH_MODEL,
                token=HUGGINGFACE_TOKEN,
                trust_remote_code=True
            )
            
            # Use float32 for CPU, float16 for GPU
            torch_dtype = torch.float32 if self.device == "cpu" else torch.float16
            
            # First load the config
            logger.info("Loading model configuration")
            config = AutoConfig.from_pretrained(
                MENTAL_HEALTH_MODEL,
                token=HUGGINGFACE_TOKEN,
                trust_remote_code=True
            )
            
            # Download and load the model weights to get vocabulary size
            logger.info("Downloading model weights")
            model_path = hf_hub_download(
                repo_id=MENTAL_HEALTH_MODEL,
                filename="pytorch_model.bin",
                token=HUGGINGFACE_TOKEN
            )
            
            # Load the state dict to get vocabulary size
            logger.info("Loading model weights to get vocabulary size")
            state_dict = torch.load(model_path, map_location=self.device)
            
            # Get vocabulary size from the word embeddings
            vocab_size = None
            for key, value in state_dict.items():
                if key.endswith("word_embeddings.weight"):
                    vocab_size = value.size(0)
                    break
            
            if vocab_size is None:
                raise ValueError("Could not determine vocabulary size from model weights")
            
            logger.info(f"Found vocabulary size: {vocab_size}")
            
            # Update config with correct vocabulary size
            config.vocab_size = vocab_size
            
            # Initialize the model with the updated config
            logger.info("Initializing model with updated config")
            self.model = CustomModel(config)
            
            # Remap the state dict keys
            logger.info("Remapping state dict keys")
            remapped_state_dict = self._remap_state_dict(state_dict)
            
            # Load the state dict into the model
            logger.info("Loading state dict into model")
            self.model.load_state_dict(remapped_state_dict)
            self.model = self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def classify_mental_health(self, text: str) -> dict:
        if self.model is None:
            raise RuntimeError("Model not initialized")
            
        # Tokenize input
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)

        # Get prediction
        with torch.no_grad():
            logits, _ = self.model(**inputs)  # Unpack the tuple returned by the model
            probabilities = F.softmax(logits, dim=1)
            predicted_class = torch.argmax(logits, dim=1).item()

        # Map prediction to label
        mental_health_map = {
            0: "normal",
            1: "depression",
            2: "suicidal",
            3: "anxiety",
            4: "bipolar",
            5: "stress",
            6: "personality disorder"
        }

        # Get probabilities for each class
        probs = {
            mental_health_map[i]: round(prob.item() * 100, 2)
            for i, prob in enumerate(probabilities[0])
        }

        return {
            "condition": mental_health_map[predicted_class],
            "probabilities": probs
        }

# Create singleton instance
mental_health_bert = MentalHealthBERT()

def classify_mental_health(text: str) -> dict:
    return mental_health_bert.classify_mental_health(text) 