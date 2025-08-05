// Configuración centralizada de la API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000';

export const API_ENDPOINTS = {
    // Endpoints del sistema anterior (para mantener compatibilidad)
    chat: `${API_BASE_URL}/chat`,
    history: `${API_BASE_URL}/history`,
    deleteChat: `${API_BASE_URL}/delete_chat`,
    deleteHistory: `${API_BASE_URL}/delete_history`,
    createChat: `${API_BASE_URL}/create-chat`,
    userRole: `${API_BASE_URL}/user/role`,
    userProfile: `${API_BASE_URL}/user/profile`,
    changePassword: `${API_BASE_URL}/user/change-password`,
    analyzeChart: `${API_BASE_URL}/analyze-chart`,
    health: `${API_BASE_URL}/health`,
    
    // Nuevos endpoints del sistema de Assistants API
    assistantChat: `${API_BASE_URL}/api/assistant/chat`,
    assistantUpload: `${API_BASE_URL}/api/assistant/upload`,
    assistantHistory: `${API_BASE_URL}/api/assistant/history`,
    assistantClear: `${API_BASE_URL}/api/assistant/clear`,
    assistantAnalyzeImage: `${API_BASE_URL}/api/assistant/analyze-image`
};

// Configuración de headers comunes
export const getAuthHeaders = (token) => ({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
});

// Función helper para requests
export const apiRequest = async (endpoint, options = {}) => {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    };

    const response = await fetch(endpoint, {
        ...defaultOptions,
        ...options
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return response.json();
}; 