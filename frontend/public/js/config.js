// API Configuration
const config = {
    // Development API endpoint
    devApiUrl: 'http://localhost:8000',
    
    // Production API endpoint (replace with your RunPod endpoint)
    prodApiUrl: process.env.NEXT_PUBLIC_API_URL || 'https://your-runpod-endpoint.runpod.net',
    
    // Use production URL if not in development
    apiUrl: process.env.NODE_ENV === 'development' 
        ? 'http://localhost:8000'
        : process.env.NEXT_PUBLIC_API_URL || 'https://your-runpod-endpoint.runpod.net',
    
    // API endpoints
    endpoints: {
        health: '/health',
        analyze: '/analyze',
        counsel: '/counsel'
    }
};

export default config; 