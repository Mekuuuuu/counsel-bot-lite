import runpod
import json
import uuid
from api.inference import (
    predict_sentiment,
    classify_mental_health,
    generate_response,
    clear_history,
    AnalysisResponse,
    SentimentResponse,
    MentalHealthResponse,
    LlamaResponse,
    KeyPointsResponse
)

def handler(event):
    """
    This is the main handler function that RunPod will call.
    """
    try:
        # Get the input from the event
        input_data = event["input"]
        
        # Extract common parameters
        prompt = input_data.get("prompt", "")
        clear_history_flag = input_data.get("clear_history", False)
        session_id = input_data.get("session_id", str(uuid.uuid4()))
        
        # Determine which endpoint to call based on the input
        endpoint = input_data.get("endpoint", "all")
        
        if endpoint == "sentiment":
            result = predict_sentiment(prompt)
            return {
                "status": "success",
                "data": {
                    "sentiment": result["sentiment"],
                    "probabilities": result["probabilities"]
                }
            }
        elif endpoint == "mental-health":
            result = classify_mental_health(prompt)
            return {
                "status": "success",
                "data": {
                    "condition": result["condition"],
                    "probabilities": result["probabilities"]
                }
            }
        elif endpoint == "counsel":
            if clear_history_flag:
                clear_history(session_id)
            response, key_points = generate_response(prompt, session_id)
            return {
                "status": "success",
                "data": {
                    "response": response,
                    "key_points": key_points,
                    "session_id": session_id
                }
            }
        elif endpoint == "key-points":
            from api.models.gemini_counsel import gemini_counsel
            session = gemini_counsel.get_session(session_id)
            return {
                "status": "success",
                "data": {
                    "key_points": session['memorized_key_messages'],
                    "session_id": session_id
                }
            }
        elif endpoint == "clear-history":
            if not session_id:
                return {
                    "status": "error",
                    "error": "session_id is required"
                }
            clear_history(session_id)
            return {
                "status": "success",
                "data": {
                    "message": "History cleared successfully",
                    "session_id": session_id
                }
            }
        else:  # "all" endpoint
            # Clear history if requested
            if clear_history_flag:
                clear_history(session_id)
                
            # Get all analyses
            sentiment_result = predict_sentiment(prompt)
            mental_health_result = classify_mental_health(prompt)
            response, key_points = generate_response(prompt, session_id)
            
            return {
                "status": "success",
                "data": {
                    "response": response,
                    "sentiment": sentiment_result,
                    "mental_health": mental_health_result,
                    "key_points": key_points,
                    "session_id": session_id
                }
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Start the RunPod serverless function
runpod.serverless.start({"handler": handler}) 