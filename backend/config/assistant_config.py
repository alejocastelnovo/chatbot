# Configuración del Assistant de OpenAI
# Este archivo contiene las configuraciones específicas del assistant

# ID del assistant existente en OpenAI
ASSISTANT_ID = "asst_G8G7YRvTNUntCd0hAc7qDpBH"

# Configuración del assistant
ASSISTANT_CONFIG = {
    "name": "Mentor Forex 1.0",
    "model": "gpt-4o",
    "description": "Assistant especializado en análisis técnico y fundamental de trading"
}

# Configuración de threads
THREAD_CONFIG = {
    "max_messages_per_thread": 50,
    "thread_timeout_seconds": 60,
    "cleanup_old_threads_days": 30
}

# Configuración de archivos
FILE_CONFIG = {
    "max_file_size_mb": 10,
    "allowed_extensions": ["png", "jpg", "jpeg", "gif", "webp"],
    "max_files_per_message": 5
}

# Configuración de rate limiting
RATE_LIMIT_CONFIG = {
    "requests_per_minute": 10,
    "requests_per_hour": 100,
    "requests_per_day": 1000
}

# Configuración de logging
LOGGING_CONFIG = {
    "log_level": "INFO",
    "log_file": "logs/assistant.log",
    "max_log_size_mb": 10,
    "backup_count": 5
}

# Configuración de APIs externas
EXTERNAL_APIS = {
    "coingecko": {
        "base_url": "https://api.coingecko.com/api/v3",
        "timeout": 10,
        "rate_limit_per_minute": 50
    },
    "exchangerate": {
        "base_url": "https://api.exchangerate-api.com/v4",
        "timeout": 10,
        "rate_limit_per_minute": 100
    }
}

# Configuración de análisis de imágenes
IMAGE_ANALYSIS_CONFIG = {
    "max_tokens": 2000,
    "temperature": 0.3,
    "analysis_types": ["technical", "pattern", "support_resistance", "complete"],
    "default_analysis_type": "complete"
}

# Configuración de funciones disponibles
AVAILABLE_FUNCTIONS = [
    "get_crypto_price",
    "get_forex_price", 
    "analyze_image",
    "get_market_sentiment",
    "get_economic_calendar"
]

# Configuración de criptomonedas soportadas
SUPPORTED_CRYPTO = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "ADA": "cardano",
    "DOT": "polkadot",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "LTC": "litecoin",
    "BCH": "bitcoin-cash",
    "XRP": "ripple",
    "SOL": "solana"
}

# Configuración de pares de divisas soportados
SUPPORTED_FOREX = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", 
    "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP", 
    "EUR/JPY", "GBP/JPY"
]

# Configuración de timeouts
TIMEOUTS = {
    "openai_request": 60,
    "external_api": 10,
    "file_upload": 30,
    "image_analysis": 45
}

# Configuración de errores y reintentos
RETRY_CONFIG = {
    "max_retries": 3,
    "retry_delay_seconds": 1,
    "backoff_multiplier": 2
}

# Configuración de seguridad
SECURITY_CONFIG = {
    "max_message_length": 2000,
    "max_concurrent_requests": 5,
    "require_authentication": True,
    "require_premium": True
} 