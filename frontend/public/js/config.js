// API Configuration - Updated version
const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

const config = {
    // API endpoint - use localhost in development, RunPod endpoint URL from Vercel env var in production
    apiUrl: isDevelopment 
        ? 'http://localhost:8000'
        : window.NEXT_PUBLIC_API_URL, // Use the Vercel environment variable
    
    // RunPod API key - only used in production
    apiKey: isDevelopment 
        ? null  // No API key needed for local development
        : window.RUNPOD_API_KEY, // Use the Vercel environment variable
    
    // RunPod status endpoint
    statusUrl: isDevelopment
        ? 'http://localhost:8000/status'
        : 'https://api.runpod.ai/v2/xkuvxoekj7yphp/status',
    
    // API endpoints (these are logical names, the actual call goes through the single RunPod endpoint)
    endpoints: {
        // These keys can be used as the 'endpoint' value in the request payload sent to the RunPod handler
        sentiment: 'sentiment',
        mentalHealth: 'mental-health',
        counsel: 'counsel',
        all: 'all',
        keyPoints: 'key-points',
        clearHistory: 'clear-history',
        // Note: The RunPod handler takes the endpoint name in the request body, not the URL path
    },

    // Flag to determine if we're using RunPod
    useRunPod: !isDevelopment
};

// Check if required environment variables are set in production
if (!isDevelopment) {
    if (!config.apiUrl) {
        console.error('Environment variable NEXT_PUBLIC_API_URL is not set!');
    }
    if (!config.apiKey) {
        console.error('Environment variable RUNPOD_API_KEY is not set!');
    }
}

export default config; 