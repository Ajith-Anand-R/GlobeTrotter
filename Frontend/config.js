const config = {
    // Default to port 8000, but allow easy switching if needed
    API_BASE_URL: "http://localhost:8000",

    // Helper to get full URL
    getApiUrl: function (endpoint) {
        return `${this.API_BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
    }
};

// Make it available globally
window.config = config;
