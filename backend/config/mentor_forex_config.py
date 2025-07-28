# Configuración de Mentor Forex 1.0
# Aquí puedes personalizar el contexto y comportamiento del bot

# Configuración básica
BOT_NAME = "Mentor Forex 1.0"
BOT_VERSION = "1.0"
BOT_SPECIALTY = "Análisis técnico y fundamental de Forex"

# Pares de divisas principales que el bot conoce
MAJOR_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", 
    "AUD/USD", "USD/CAD", "NZD/USD"
]

CROSS_PAIRS = [
    "EUR/GBP", "EUR/JPY", "GBP/JPY", "EUR/CHF",
    "GBP/CHF", "AUD/JPY", "CAD/JPY"
]

EXOTIC_PAIRS = [
    "USD/TRY", "USD/ZAR", "USD/BRL", "USD/MXN",
    "EUR/TRY", "GBP/ZAR"
]

# Indicadores técnicos que el bot utiliza
TECHNICAL_INDICATORS = {
    "trend": ["Moving Averages", "ADX", "Parabolic SAR", "Ichimoku"],
    "momentum": ["RSI", "MACD", "Stochastic", "Williams %R", "CCI"],
    "volatility": ["Bollinger Bands", "ATR", "Keltner Channels"],
    "volume": ["OBV", "VWAP", "Volume Profile", "Money Flow Index"],
    "support_resistance": ["Fibonacci", "Pivot Points", "Demark", "Gann"]
}

# Configuración de análisis
ANALYSIS_SETTINGS = {
    "default_timeframes": ["1H", "4H", "1D"],
    "risk_reward_ratio": "1:2",  # Ratio mínimo recomendado
    "max_risk_per_trade": "1-2%",  # Porcentaje máximo de riesgo por operación
    "position_sizing": "Fixed Risk",  # Método de sizing
}

# Configuración de respuesta
RESPONSE_SETTINGS = {
    "include_risk_warnings": True,
    "include_technical_analysis": True,
    "include_fundamental_analysis": True,
    "include_support_resistance": True,
    "include_risk_management": True,
    "max_response_length": 4000,  # tokens
}

# Elementos personalizados que puedes agregar
CUSTOM_ELEMENTS = [
    # Agrega aquí elementos específicos de tu estrategia
    # "Análisis de correlaciones entre pares",
    # "Estrategias específicas de scalping",
    # "Análisis de noticias en tiempo real",
]

# Configuración de tono y estilo
TONE_SETTINGS = {
    "style": "profesional_educativo",
    "language": "español",
    "formality_level": "medio",  # bajo, medio, alto
    "motivation_level": "alto",  # bajo, medio, alto
}

# Configuración de advertencias
RISK_WARNINGS = [
    "El trading de Forex conlleva alto riesgo de pérdida",
    "Los análisis son educativos, no consejos financieros",
    "Cada trader debe hacer su propio análisis",
    "Nunca invertir más de lo que se puede permitir perder",
    "El apalancamiento puede amplificar tanto ganancias como pérdidas",
    "Los resultados pasados no garantizan resultados futuros"
]

# Configuración de eventos económicos importantes
ECONOMIC_EVENTS = [
    "NFP (Non-Farm Payrolls)",
    "Decisiones de Bancos Centrales",
    "PIB (Producto Interno Bruto)",
    "Inflación (CPI, PPI)",
    "Tasas de interés",
    "Elecciones políticas",
    "Eventos geopolíticos"
]

# Configuración de timeframes para análisis
TIMEFRAMES = {
    "scalping": ["1M", "5M", "15M"],
    "day_trading": ["15M", "1H", "4H"],
    "swing_trading": ["4H", "1D", "1W"],
    "position_trading": ["1D", "1W", "1M"]
}

# Configuración de gestión de riesgo
RISK_MANAGEMENT = {
    "stop_loss_types": ["Fixed", "Trailing", "Break-even"],
    "take_profit_types": ["Fixed", "Trailing", "Multiple targets"],
    "position_sizing_methods": ["Fixed Risk", "Fixed Amount", "Kelly Criterion"],
    "max_daily_loss": "5%",
    "max_weekly_loss": "15%",
    "max_monthly_loss": "30%"
} 