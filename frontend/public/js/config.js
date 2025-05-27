// API Configuration - Updated version
const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

const config = {
    // API endpoint - use localhost in development, RunPod endpoint URL from Vercel env var in production
    apiUrl: isDevelopment 
        ? 'http://localhost:8000'
        : process.env.NEXT_PUBLIC_API_URL, // Use the Vercel environment variable
    
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
    }
};

// Check if NEXT_PUBLIC_API_URL is set in production
if (!isDevelopment && !config.apiUrl) {
    console.error('Environment variable NEXT_PUBLIC_API_URL is not set!');
    // Optionally display an error to the user or use a fallback URL
    // config.apiUrl = 'https://your-default-fallback-runpod-url.runpod.net'; // Example fallback
}

export default config; 