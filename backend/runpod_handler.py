import runpod
import json
from api.inference import (
    analyze_sentiment,
    analyze_mental_health,
    generate_counsel,
    analyze_all,
    TextRequest
)

def handler(event):
    """
    This is the main handler function that RunPod will call.
    """
    try:
        # Get the input from the event
        input_data = event["input"]
        
        # Create a TextRequest object
        request = TextRequest(
            prompt=input_data.get("prompt", ""),
            clear_history=input_data.get("clear_history", False)
        )
        
        # Determine which endpoint to call based on the input
        endpoint = input_data.get("endpoint", "all")
        
        if endpoint == "sentiment":
            result = analyze_sentiment(request)
            return {
                "status": "success",
                "data": {
                    "sentiment": result.sentiment,
                    "probabilities": result.probabilities
                }
            }
        elif endpoint == "mental-health":
            result = analyze_mental_health(request)
            return {
                "status": "success",
                "data": {
                    "condition": result.condition,
                    "probabilities": result.probabilities
                }
            }
        elif endpoint == "counsel":
            result = generate_counsel(request)
            return {
                "status": "success",
                "data": {
                    "response": result.response
                }
            }
        else:  # "all" endpoint
            result = analyze_all(request)
            return {
                "status": "success",
                "data": {
                    "response": result.response,
                    "sentiment": result.sentiment,
                    "mental_health": result.mental_health
                }
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Start the RunPod serverless function
runpod.serverless.start({"handler": handler}) 