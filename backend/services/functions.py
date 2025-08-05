import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import os
from openai import OpenAI

# Configurar logging
logger = logging.getLogger(__name__)

# Cliente OpenAI para análisis de imágenes
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_crypto_price(symbol: str) -> Dict[str, Any]:
    """
    Obtiene el precio actual de una criptomoneda usando CoinGecko API
    
    Args:
        symbol: Símbolo de la criptomoneda (ej: BTC, ETH)
    
    Returns:
        Dict con información del precio
    """
    try:
        # Cargar configuración de criptomonedas soportadas
        from config.assistant_config import SUPPORTED_CRYPTO
        
        symbol_mapping = SUPPORTED_CRYPTO
        
        coin_id = symbol_mapping.get(symbol.upper())
        if not coin_id:
            return {
                "success": False,
                "error": f"Símbolo no soportado: {symbol}",
                "supported_symbols": list(symbol_mapping.keys())
            }
        
        # Obtener datos de CoinGecko
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": "usd,eur",
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        coin_data = data.get(coin_id, {})
        
        if not coin_data:
            return {
                "success": False,
                "error": f"No se encontraron datos para {symbol}"
            }
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "price_usd": coin_data.get("usd"),
            "price_eur": coin_data.get("eur"),
            "change_24h": coin_data.get("usd_24h_change"),
            "volume_24h": coin_data.get("usd_24h_vol"),
            "market_cap": coin_data.get("usd_market_cap"),
            "timestamp": datetime.now().isoformat(),
            "source": "CoinGecko"
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error obteniendo precio de {symbol}: {e}")
        return {
            "success": False,
            "error": f"Error de conexión: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error inesperado obteniendo precio de {symbol}: {e}")
        return {
            "success": False,
            "error": f"Error inesperado: {str(e)}"
        }

def get_forex_price(pair: str) -> Dict[str, Any]:
    """
    Obtiene el precio actual de un par de divisas usando una API gratuita
    
    Args:
        pair: Par de divisas (ej: EUR/USD, GBP/USD)
    
    Returns:
        Dict con información del precio
    """
    try:
        # Usar ExchangeRate-API (gratuita con límites)
        base_currency = pair.split('/')[0]
        target_currency = pair.split('/')[1]
        
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if target_currency not in data.get("rates", {}):
            return {
                "success": False,
                "error": f"Par de divisas no soportado: {pair}"
            }
        
        rate = data["rates"][target_currency]
        
        return {
            "success": True,
            "pair": pair,
            "rate": rate,
            "base_currency": base_currency,
            "target_currency": target_currency,
            "timestamp": datetime.now().isoformat(),
            "source": "ExchangeRate-API"
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error obteniendo precio de {pair}: {e}")
        return {
            "success": False,
            "error": f"Error de conexión: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error inesperado obteniendo precio de {pair}: {e}")
        return {
            "success": False,
            "error": f"Error inesperado: {str(e)}"
        }

def analyze_image(image_url: str, analysis_type: str = "complete") -> Dict[str, Any]:
    """
    Analiza una imagen de gráfico de trading usando GPT-4o con visión
    
    Args:
        image_url: URL de la imagen a analizar
        analysis_type: Tipo de análisis (technical, pattern, support_resistance, complete)
    
    Returns:
        Dict con el análisis de la imagen
    """
    try:
        # Definir el prompt según el tipo de análisis
        analysis_prompts = {
            "technical": """
            Analiza este gráfico de trading desde una perspectiva técnica pura. Identifica:
            1. Indicadores técnicos visibles (RSI, MACD, medias móviles, etc.)
            2. Patrones de velas japonesas
            3. Niveles de soporte y resistencia
            4. Tendencias actuales
            5. Momentum y volumen (si es visible)
            
            Proporciona un análisis técnico detallado y objetivo.
            """,
            "pattern": """
            Enfócate en identificar patrones de trading en este gráfico:
            1. Patrones de continuación (triángulos, banderas, etc.)
            2. Patrones de reversión (doble techo, doble suelo, etc.)
            3. Patrones de velas (doji, martillo, estrella fugaz, etc.)
            4. Patrones de Fibonacci
            5. Formaciones de chart (H&S, triángulos, etc.)
            
            Explica cada patrón identificado y su significado.
            """,
            "support_resistance": """
            Analiza específicamente los niveles de soporte y resistencia:
            1. Soportes principales y secundarios
            2. Resistencias principales y secundarias
            3. Zonas de congestión
            4. Breakouts y breakdowns
            5. Niveles psicológicos importantes
            
            Proporciona niveles específicos y su importancia.
            """,
            "complete": """
            Realiza un análisis completo de este gráfico de trading:
            
            ## **RESUMEN EJECUTIVO**
            - Estado actual del mercado
            - Tendencias principales
            
            ## **ANÁLISIS TÉCNICO**
            - Indicadores técnicos relevantes
            - Patrones identificados
            - Momentum y volatilidad
            
            ## **NIVELES CLAVE**
            - Soporte y resistencia principales
            - Zonas de interés
            - Objetivos de precio
            
            ## **GESTIÓN DE RIESGO**
            - Stop-loss recomendado
            - Take-profit sugerido
            - Ratio riesgo/beneficio
            
            ## **RECOMENDACIÓN**
            - Señal de entrada/salida
            - Justificación técnica
            - Advertencias importantes
            
            Incluye siempre las advertencias de riesgo obligatorias.
            """
        }
        
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["complete"])
        
        # Realizar el análisis con GPT-4o
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto analista técnico de trading con más de 15 años de experiencia. Analiza gráficos de manera profesional, objetiva y educativa. Siempre incluye advertencias de riesgo."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        analysis = response.choices[0].message.content
        
        return {
            "success": True,
            "analysis": analysis,
            "analysis_type": analysis_type,
            "image_url": image_url,
            "timestamp": datetime.now().isoformat(),
            "model": "gpt-4o"
        }
        
    except Exception as e:
        logger.error(f"Error analizando imagen: {e}")
        return {
            "success": False,
            "error": f"Error analizando imagen: {str(e)}",
            "image_url": image_url
        }

def get_market_sentiment(asset: str) -> Dict[str, Any]:
    """
    Obtiene el sentimiento del mercado para un activo específico
    
    Args:
        asset: Símbolo del activo (ej: BTC, EUR/USD)
    
    Returns:
        Dict con información del sentimiento
    """
    try:
        # Esta función podría integrar múltiples fuentes de sentimiento
        # Por ahora, retornamos datos simulados
        
        return {
            "success": True,
            "asset": asset,
            "sentiment": "neutral",  # bullish, bearish, neutral
            "confidence": 0.75,
            "sources": ["Fear & Greed Index", "Social Media", "News"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo sentimiento para {asset}: {e}")
        return {
            "success": False,
            "error": f"Error obteniendo sentimiento: {str(e)}"
        }

def get_economic_calendar() -> Dict[str, Any]:
    """
    Obtiene el calendario económico para los próximos días
    
    Returns:
        Dict con eventos económicos importantes
    """
    try:
        # Esta función podría integrar APIs de calendario económico
        # Por ahora, retornamos datos simulados
        
        return {
            "success": True,
            "events": [
                {
                    "date": "2024-01-15",
                    "time": "14:30",
                    "currency": "USD",
                    "event": "NFP (Non-Farm Payrolls)",
                    "impact": "high",
                    "forecast": "180K",
                    "previous": "173K"
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo calendario económico: {e}")
        return {
            "success": False,
            "error": f"Error obteniendo calendario: {str(e)}"
        }

def execute_function(function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ejecuta una función específica basada en el nombre
    
    Args:
        function_name: Nombre de la función a ejecutar
        arguments: Argumentos para la función
    
    Returns:
        Resultado de la función
    """
    try:
        logger.info(f"Ejecutando función: {function_name} con argumentos: {arguments}")
        
        if function_name == "get_crypto_price":
            symbol = arguments.get("symbol")
            if not symbol:
                return {"success": False, "error": "Símbolo requerido"}
            return get_crypto_price(symbol)
            
        elif function_name == "get_forex_price":
            pair = arguments.get("pair")
            if not pair:
                return {"success": False, "error": "Par de divisas requerido"}
            return get_forex_price(pair)
            
        elif function_name == "analyze_image":
            image_url = arguments.get("image_url")
            analysis_type = arguments.get("analysis_type", "complete")
            if not image_url:
                return {"success": False, "error": "URL de imagen requerida"}
            return analyze_image(image_url, analysis_type)
            
        elif function_name == "get_market_sentiment":
            asset = arguments.get("asset")
            if not asset:
                return {"success": False, "error": "Activo requerido"}
            return get_market_sentiment(asset)
            
        elif function_name == "get_economic_calendar":
            return get_economic_calendar()
            
        else:
            return {
                "success": False,
                "error": f"Función no reconocida: {function_name}",
                "available_functions": [
                    "get_crypto_price",
                    "get_forex_price", 
                    "analyze_image",
                    "get_market_sentiment",
                    "get_economic_calendar"
                ]
            }
            
    except Exception as e:
        logger.error(f"Error ejecutando función {function_name}: {e}")
        return {
            "success": False,
            "error": f"Error ejecutando función: {str(e)}"
        }

# Función helper para formatear precios
def format_price(price: float, decimals: int = 2) -> str:
    """Formatea un precio con el número de decimales especificado"""
    return f"{price:.{decimals}f}"

# Función helper para calcular porcentaje de cambio
def calculate_change_percentage(current: float, previous: float) -> float:
    """Calcula el porcentaje de cambio entre dos valores"""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100 