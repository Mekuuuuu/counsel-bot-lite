// API Configuration - Updated version
const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

const config = {
    // API endpoint - use localhost in development, RunPod in production
    apiUrl: isDevelopment 
        ? 'http://localhost:8000'
        : 'https://your-runpod-endpoint.runpod.net',
    
    // API endpoints
    endpoints: {
        health: '/health',
        analyze: '/analyze',
        counsel: '/counsel'
    }
};

export default config; 