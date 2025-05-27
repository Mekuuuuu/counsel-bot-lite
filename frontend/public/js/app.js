import config from './config.js';

// Theme Management
const themeManager = {
    init() {
        this.setInitialTheme();
        this.setupThemeToggle();
    },

    setInitialTheme() {
        const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        const savedTheme = localStorage.getItem('theme');
        const currentTheme = savedTheme ? savedTheme : systemTheme;
        document.documentElement.classList.toggle('dark', currentTheme === 'dark');
    },

    setupThemeToggle() {
        window.changeTheme = () => {
            const html = document.documentElement;
            html.classList.toggle('dark');
            localStorage.setItem('theme', html.classList.contains('dark') ? 'dark' : 'light');
        };
    }
};

// Navigation Management
const navManager = {
    async init() {
        await this.loadNavComponents();
        this.setActiveNavLink();
        this.setupNavigationLinks();
    },

    async loadNavComponents() {
        const navPlaceholder = document.getElementById('nav-placeholder');
        if (!navPlaceholder) return;

        try {
            const response = await fetch('/public/nav.html');
            const html = await response.text();
            navPlaceholder.innerHTML = html;
        } catch (error) {
            console.error('Error loading navigation components:', error);
        }
    },

    setActiveNavLink() {
        const currentPath = window.location.pathname;
        const links = document.querySelectorAll('.nav-links');
        
        links.forEach(link => {
            const linkPath = link.getAttribute('href');
            // Check if the current path matches the link path or if we're on the index page
            if (linkPath === currentPath || 
                (currentPath === '/' && linkPath === '/') || 
                (currentPath.endsWith('index.html') && linkPath === '/') ||
                (currentPath.endsWith('about.html') && linkPath === '/about')) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    },

    setupNavigationLinks() {
        const links = document.querySelectorAll('.nav-links');
        links.forEach(link => {
            link.addEventListener('click', (e) => {
                if (link.getAttribute('href').startsWith('/')) {
                    e.preventDefault();
                    const path = link.getAttribute('href');
                    window.location.href = path === '/' ? 'index.html' : path.substring(1) + '.html';
                }
            });
        });
    }
};

// Chat Management
const chatManager = {
    chatHistory: [],
    isWaitingForResponse: false,
    sessionId: null,
    
    init() {
        this.setupElements();
        this.setupEventListeners();
        this.initializeSession();
        this.loadChatHistory();
        this.focusInput();
        this.setupVisibilityChange();
        this.setupGlobalKeyboardHandler();
        this.loadNavComponents();
    },

    initializeSession() {
        // Try to get existing session ID from localStorage
        this.sessionId = localStorage.getItem('sessionId');
        
        if (!this.sessionId) {
            // Generate new session ID if none exists
            this.sessionId = crypto.randomUUID();
            localStorage.setItem('sessionId', this.sessionId);
            console.log('Created new session ID:', this.sessionId);
        } else {
            console.log('Using existing session ID:', this.sessionId);
        }

        // Load chat history from localStorage
        const savedHistory = localStorage.getItem('chatHistory');
        if (savedHistory) {
            try {
                this.chatHistory = JSON.parse(savedHistory);
                console.log('Loaded chat history with', this.chatHistory.length, 'messages');
            } catch (e) {
                console.error('Error loading chat history:', e);
                this.chatHistory = [];
            }
        }
    },

    setupElements() {
        this.chatMessages = document.getElementById('chat-messages');
        this.messageForm = document.getElementById('message-form');
        this.messageInput = document.getElementById('message-input');
        this.clearHistoryBtn = document.getElementById('clear-history');
        this.sendButton = this.messageForm.querySelector('button[type="submit"]');
        this.exportHistoryButton = document.getElementById('export-history');
    },

    setupEventListeners() {
        if (this.messageForm) {
            this.messageForm.addEventListener('submit', (e) => this.handleMessageSubmit(e));
        }
        if (this.clearHistoryBtn) {
            this.clearHistoryBtn.addEventListener('click', () => this.clearHistory());
        }
        if (this.messageInput) {
            this.messageInput.addEventListener('input', () => {
                this.updateSendButtonState();
            });
            // Focus input when clicking anywhere in the chat container
            this.chatMessages.parentElement.addEventListener('click', () => this.focusInput());
        }
        if (this.exportHistoryButton) {
            this.exportHistoryButton.addEventListener('click', () => this.exportChatHistory());
        }
    },

    setupGlobalKeyboardHandler() {
        document.addEventListener('keydown', (e) => {
            // Don't capture if input is disabled or if user is typing in input
            if (this.isWaitingForResponse || e.target === this.messageInput) return;

            // Don't capture modifier keys or special keys
            if (e.ctrlKey || e.altKey || e.metaKey || e.key.length > 1) return;

            // Don't capture if user is typing in a form element
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            // Focus input and append the typed character
            this.focusInput();
            const currentValue = this.messageInput.value;
            this.messageInput.value = currentValue + e.key;
            this.updateSendButtonState();
            e.preventDefault();
        });
    },

    setupVisibilityChange() {
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                this.focusInput();
            }
        });
    },

    focusInput() {
        if (this.messageInput && !this.isWaitingForResponse) {
            this.messageInput.focus();
        }
    },

    updateSendButtonState() {
        if (!this.messageInput || !this.sendButton) return;
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || this.isWaitingForResponse;
    },

    setWaitingState(isWaiting) {
        this.isWaitingForResponse = isWaiting;
        this.messageInput.disabled = isWaiting;
        this.updateSendButtonState();
        if (!isWaiting) {
            this.focusInput();
        }
    },

    loadChatHistory() {
        if (this.chatMessages) {
            console.log('Loading', this.chatHistory.length, 'messages into chat');
            
            if (this.chatHistory.length === 0) {
                this.showGreeting();
            } else {
                // Load existing chat history
                this.chatHistory.forEach((msg, index) => {
                    setTimeout(() => {
                        this.addMessage(msg.message, msg.isUser, true);
                    }, index * 100);
                });
            }
        }
    },

    showGreeting() {
        // Array of varied greetings
        const greetings = [
            "Hello! I'm CounselBot, here to listen and support you. How are you feeling today?",
            "Hi there! I'm CounselBot, your mental health companion. What's on your mind?",
            "Welcome! I'm CounselBot, here to chat and help you process your thoughts. How are you doing?",
            "Greetings! I'm CounselBot, ready to listen and support you. What would you like to talk about?",
            "Hello! I'm CounselBot, here to provide a safe space for you to express yourself. How are you feeling?",
            "Hi! I'm CounselBot, your AI companion, ready to chat about anything that's on your mind. How are you today?",
            "Welcome! I'm CounselBot, here to help you navigate your thoughts and feelings. What's going on in your life?",
            "Hello there! I'm CounselBot, ready to listen and support you. What would you like to discuss?",
            "Hi! I'm CounselBot, here to chat and help you process your emotions. How are you feeling right now?",
            "Greetings! I'm CounselBot, your mental health companion. What's been on your mind lately?"
        ];
        
        // Get a random greeting
        const randomGreeting = greetings[Math.floor(Math.random() * greetings.length)];
        
        // Create message container
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex justify-start message-enter py-2';
        
        // Create message bubble with typing indicator
        const messageBubble = document.createElement('div');
        messageBubble.className = 'max-w-[70%] rounded-2xl p-4 bg-white dark:bg-neutral-900 text-gray-800 dark:text-gray-200 rounded-bl-none shadow-sm border border-neutral-200 dark:border-neutral-800';
        
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        
        messageBubble.appendChild(typingIndicator);
        messageDiv.appendChild(messageBubble);
        this.chatMessages.appendChild(messageDiv);
        messageDiv.classList.add('message-enter-active');
        
        // Simulate typing delay
        setTimeout(() => {
            messageBubble.innerHTML = randomGreeting;
            messageBubble.style.transition = 'opacity 0.3s ease-out';
            messageBubble.style.opacity = '0';
            
            // Fade in the greeting
            setTimeout(() => {
                messageBubble.style.opacity = '1';
            }, 50);
            
            // Add to chat history
            this.chatHistory.push({
                message: randomGreeting,
                isUser: false
            });
            this.saveChatHistory();
        }, 1500); // Typing delay
    },

    addMessage(message, isUser = false, isHistorical = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex ${isUser ? 'justify-end' : 'justify-start'} message-enter py-2`;
        
        const messageBubble = document.createElement('div');
        messageBubble.className = `max-w-[70%] rounded-2xl p-4 ${
            isUser 
                ? 'bg-blue-500 text-white rounded-br-none shadow-sm' 
                : 'bg-white dark:bg-neutral-900 text-gray-800 dark:text-gray-200 rounded-bl-none shadow-sm border border-neutral-200 dark:border-neutral-800'
        }`;
        
        messageBubble.textContent = message;
        messageDiv.appendChild(messageBubble);
        this.chatMessages.appendChild(messageDiv);
        messageDiv.classList.add('message-enter-active');

        // Add typing indicator after user message, but only for new messages
        if (isUser && !isHistorical) {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'flex justify-start message-enter py-2 typing-container';
            
            const typingBubble = document.createElement('div');
            typingBubble.className = 'max-w-[70%] rounded-2xl p-4 bg-white dark:bg-neutral-900 text-gray-800 dark:text-gray-200 rounded-bl-none shadow-sm border border-neutral-200 dark:border-neutral-800';
            
            const typingIndicator = document.createElement('div');
            typingIndicator.className = 'typing-indicator';
            typingIndicator.innerHTML = `
                <span></span>
                <span></span>
                <span></span>
            `;
            
            typingBubble.appendChild(typingIndicator);
            typingDiv.appendChild(typingBubble);
            this.chatMessages.appendChild(typingDiv);
            typingDiv.classList.add('message-enter-active');
        }
        
        this.chatMessages.scrollTo({
            top: this.chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    },

    saveChatHistory() {
        localStorage.setItem('chatHistory', JSON.stringify(this.chatHistory));
        console.log('Saved chat history with', this.chatHistory.length, 'messages');
    },

    exportChatHistory() {
        // Create a copy of chat history with formatted data
        const exportData = {
            timestamp: new Date().toISOString(),
            chatHistory: this.chatHistory.map(entry => {
                const baseEntry = {
                    message: entry.message,
                    isUser: entry.isUser,
                    timestamp: new Date().toISOString()
                };

                // Add analysis only for user messages
                if (entry.isUser && entry.metadata) {
                    baseEntry.analysis = {
                        sentiment: entry.metadata.sentiment,
                        mentalHealth: entry.metadata.mentalHealth
                    };
                }

                // Add key points for LLM responses
                if (!entry.isUser && entry.key_points) {
                    baseEntry.key_points = entry.key_points;
                }

                return baseEntry;
            })
        };

        // Convert to JSON string with pretty formatting
        const jsonString = JSON.stringify(exportData, null, 2);
        
        // Create a blob and download link
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat_history_${new Date().toISOString().slice(0,10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    },

    async handleMessageSubmit(e) {
        e.preventDefault();
        
        const message = this.messageInput.value.trim();
        if (!message || this.isWaitingForResponse) return;
        
        // Clear input and disable it while waiting
        this.messageInput.value = '';
        this.setWaitingState(true);
        
        // Add user message to chat
        this.addMessage(message, true);
        
        try {
            if (config.useRunPod) {
                // RunPod API flow
                const response = await fetch(config.apiUrl, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${config.apiKey}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        input: {
                            prompt: message,
                            endpoint: 'all',
                            session_id: this.sessionId
                        }
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                // If the request is queued, poll for status
                if (data.status === 'IN_QUEUE' || data.status === 'IN_PROGRESS') {
                    const result = await this.pollForResult(data.id);
                    
                    // Remove typing indicator
                    const existingTypingContainers = this.chatMessages.querySelectorAll('.typing-container');
                    existingTypingContainers.forEach(container => container.remove());
                    
                    // Extract response data
                    const responseData = result.output.data;
                    
                    // Save user message with analysis metadata
                    this.chatHistory.push({
                        message: message,
                        isUser: true,
                        timestamp: new Date().toISOString(),
                        analysis: {
                            sentiment: responseData.sentiment,
                            mentalHealth: responseData.mental_health
                        }
                    });
                    
                    // Add AI response to chat
                    this.addMessage(responseData.response, false);
                    
                    // Save AI response to chat history
                    this.chatHistory.push({
                        message: responseData.response,
                        isUser: false,
                        timestamp: new Date().toISOString(),
                        key_points: responseData.key_points
                    });
                }
            } else {
                // Local development flow
                console.log('Using session ID:', this.sessionId);
                
                // Get sentiment and mental health classification for user message
                const [sentimentRes, mentalHealthRes] = await Promise.all([
                    fetch(`${config.apiUrl}/analyze/sentiment`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            prompt: message,
                            session_id: this.sessionId
                        })
                    }),
                    fetch(`${config.apiUrl}/analyze/mental-health`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            prompt: message,
                            session_id: this.sessionId
                        })
                    })
                ]);

                const sentimentData = await sentimentRes.json();
                const mentalHealthData = await mentalHealthRes.json();
                
                // Save user message with analysis metadata
                this.chatHistory.push({ 
                    message, 
                    isUser: true,
                    timestamp: new Date().toISOString(),
                    analysis: {
                        sentiment: sentimentData,
                        mentalHealth: mentalHealthData
                    }
                });
                
                // Get main response
                const response = await fetch(`${config.apiUrl}/generate/counsel`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        prompt: message,
                        clear_history: false,
                        session_id: this.sessionId
                    })
                });

                if (!response.ok) {
                    throw new Error(`Failed to get response: ${response.status} ${response.statusText}`);
                }

                const result = await response.json();
                console.log('Received response with key points:', result.key_points);
                
                // Remove any existing typing indicators first
                const existingTypingContainers = this.chatMessages.querySelectorAll('.typing-container');
                existingTypingContainers.forEach(container => container.remove());
                
                // Add the response with key points
                this.addMessage(result.response, false);
                this.chatHistory.push({ 
                    message: result.response, 
                    isUser: false,
                    timestamp: new Date().toISOString(),
                    key_points: result.key_points
                });
            }
            
            // Save chat history
            this.saveChatHistory();
            
        } catch (error) {
            console.error('Error in handleMessageSubmit:', error);
            // Remove typing indicator
            const existingTypingContainers = this.chatMessages.querySelectorAll('.typing-container');
            existingTypingContainers.forEach(container => container.remove());
            
            this.addMessage('I apologize, but I encountered an error. Please try again.', false);
        } finally {
            // Re-enable input
            this.setWaitingState(false);
        }
    },

    async pollForResult(jobId) {
        const maxAttempts = 30; // Maximum number of polling attempts
        const pollInterval = 2000; // Poll every 2 seconds
        
        for (let attempt = 0; attempt < maxAttempts; attempt++) {
            try {
                const response = await fetch(`${config.statusUrl}/${jobId}`, {
                    headers: {
                        'Authorization': `Bearer ${config.apiKey}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                if (data.status === 'COMPLETED') {
                    return data;
                } else if (data.status === 'FAILED') {
                    throw new Error('Job failed');
                }

                // Wait before next poll
                await new Promise(resolve => setTimeout(resolve, pollInterval));
            } catch (error) {
                console.error('Error polling for result:', error);
                throw error;
            }
        }

        throw new Error('Polling timeout');
    },

    handleInputChange() {
        // Implementation of handleInputChange method
    },

    clearHistory() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            // Clear frontend first
            this.chatHistory = [];
            this.saveChatHistory();
            this.chatMessages.innerHTML = '';
            this.focusInput();

            // Show new greeting
            this.showGreeting();

            // Then clear backend history
            if (config.useRunPod) {
                // RunPod clear history
                fetch(config.apiUrl, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${config.apiKey}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        input: {
                            prompt: '',
                            endpoint: 'clear-history',
                            session_id: this.sessionId
                        }
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Failed to clear history: ${response.status} ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('History cleared successfully:', data);
                })
                .catch(error => {
                    console.error('Error clearing history:', error);
                });
            } else {
                // Local clear history
                fetch(`${config.apiUrl}/clear/history`, { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        prompt: '',  // Required by PromptRequest model
                        session_id: this.sessionId,
                        clear_history: false
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Failed to clear history: ${response.status} ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('History cleared successfully:', data);
                })
                .catch(error => {
                    console.error('Error clearing history:', error);
                });
            }
        }
    }
};

// Initialize everything when the DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    themeManager.init();
    await navManager.init();
    chatManager.init();
});

// Add styles for typing indicator
const style = document.createElement('style');
style.textContent = `
    .typing-indicator {
        display: flex;
        gap: 4px;
        padding: 4px 0;
    }
    .typing-indicator span {
        width: 8px;
        height: 8px;
        background: #e2e8f0;
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out;
    }
    .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
    .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    .dark .typing-indicator span {
        background: #4b5563;
    }
`;
document.head.appendChild(style); 