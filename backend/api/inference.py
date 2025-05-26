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
import uvicorn
import uuid

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

class PromptRequest(BaseModel):
    prompt: str
    clear_history: bool = False
    session_id: Optional[str] = None

class SentimentResponse(BaseModel):
    sentiment: str
    probabilities: Dict[str, float]

class MentalHealthResponse(BaseModel):
    condition: str
    probabilities: Dict[str, float]

class LlamaResponse(BaseModel):
    response: str
    key_points: List[str]

class KeyPointsResponse(BaseModel):
    key_points: List[str]

class AnalysisResponse(BaseModel):
    response: str
    sentiment: dict
    mental_health: dict
    key_points: List[str]

@app.get("/key-points/{session_id}", response_model=KeyPointsResponse)
async def get_key_points(session_id: str):
    try:
        from .models.gemini_counsel import gemini_counsel
        session = gemini_counsel.get_session(session_id)
        return KeyPointsResponse(key_points=session['memorized_key_messages'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/sentiment", response_model=SentimentResponse)
async def analyze_sentiment_endpoint(request: PromptRequest):
    try:
        result = predict_sentiment(request.prompt)
        return SentimentResponse(
            sentiment=result["sentiment"],
            probabilities=result["probabilities"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/mental-health", response_model=MentalHealthResponse)
async def analyze_mental_health_endpoint(request: PromptRequest):
    try:
        result = classify_mental_health(request.prompt)
        return MentalHealthResponse(
            condition=result["condition"],
            probabilities=result["probabilities"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear/history")
async def clear_history_endpoint(request: PromptRequest):
    try:
        if not request.session_id:
            raise HTTPException(status_code=400, detail="session_id is required")
        clear_history(request.session_id)
        return {"message": "History cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/counsel", response_model=LlamaResponse)
async def generate_counsel(request: PromptRequest):
    try:
        # Generate a session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Clear history if requested
        if request.clear_history:
            clear_history(session_id)
        
        # Generate response
        response, key_points = generate_response(request.prompt, session_id)
        return LlamaResponse(response=response, key_points=key_points)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/all", response_model=AnalysisResponse)
async def analyze_all(request: PromptRequest):
    try:
        # Generate a session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get all analyses
        sentiment_result = predict_sentiment(request.prompt)
        mental_health_result = classify_mental_health(request.prompt)
        response, key_points = generate_response(request.prompt, session_id)
        
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
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000"))
    ) 