from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
#import torch
import os
from dotenv import load_dotenv
from .models.sentiment_bert import predict_sentiment
from .models.mental_health_bert import classify_mental_health
from .models.gemini_counsel import generate_response, clear_history
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

app = FastAPI(title="CounselBot API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    prompt: str
    clear_history: Optional[bool] = False

class SentimentResponse(BaseModel):
    sentiment: str
    probabilities: Dict[str, float]

class MentalHealthResponse(BaseModel):
    condition: str
    probabilities: Dict[str, float]

class LlamaResponse(BaseModel):
    response: str
    key_points: Optional[List[str]] = None

class KeyPointsResponse(BaseModel):
    key_points: List[str]

class AnalysisResponse(BaseModel):
    response: Optional[str] = None
    sentiment: Optional[Dict[str, Any]] = None
    mental_health: Optional[Dict[str, Any]] = None
    key_points: Optional[List[str]] = None

@app.get("/key-points", response_model=KeyPointsResponse)
async def get_key_points() -> KeyPointsResponse:
    try:
        return KeyPointsResponse(key_points=gemini_counsel.memorized_key_messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: TextRequest) -> SentimentResponse:
    try:
        result = predict_sentiment(request.prompt)
        return SentimentResponse(
            sentiment=result["sentiment"],
            probabilities=result["probabilities"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/mental-health", response_model=MentalHealthResponse)
async def analyze_mental_health(request: TextRequest) -> MentalHealthResponse:
    try:
        result = classify_mental_health(request.prompt)
        return MentalHealthResponse(
            condition=result["condition"],
            probabilities=result["probabilities"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear/history")
async def clear_history_endpoint():
    try:
        clear_history()
        return {"status": "History cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/counsel", response_model=LlamaResponse)
async def generate_counsel(request: TextRequest) -> LlamaResponse:
    try:
        response, key_points = generate_response(request.prompt)
        return LlamaResponse(response=response, key_points=key_points)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/all", response_model=AnalysisResponse)
async def analyze_all(request: TextRequest) -> AnalysisResponse:
    try:
        # Get sentiment analysis
        sentiment_result = predict_sentiment(request.prompt)
        
        # Get mental health classification
        mental_health_result = classify_mental_health(request.prompt)
        
        # Generate response using Gemini
        response, key_points = generate_response(request.prompt)
        
        return AnalysisResponse(
            response=response,
            sentiment=sentiment_result,
            mental_health=mental_health_result,
            key_points=key_points
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Welcome to CounselBot API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000"))
    ) 