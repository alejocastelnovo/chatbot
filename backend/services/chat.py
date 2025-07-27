from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()  # Esto carga las variables del .env

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_gpt_response(prompt, model="gpt-4o", system_prompt=None, temperature=0.7, conversation_history=None):
    """
    Obtiene respuesta de GPT optimizada para trading con contexto de conversación
    
    Args:
        prompt: Mensaje del usuario
        model: Modelo a usar (gpt-4o, gpt-4o-mini, gpt-4-turbo)
        system_prompt: Prompt del sistema para definir el contexto
        temperature: Creatividad de la respuesta (0.0-1.0)
        conversation_history: Lista de mensajes previos para mantener contexto
    """
    
    # Prompt del sistema por defecto para trading
    if not system_prompt:
        system_prompt = """Eres **MentorBot IA**, un experto analista de trading especializado en:

## 📊 **Análisis Técnico**
- Interpretación de gráficos de velas japonesas
- Identificación de patrones de continuación y reversión
- Análisis de soportes, resistencias y tendencias
- Uso de indicadores técnicos (RSI, MACD, Bollinger Bands, etc.)

## 💰 **Gestión de Riesgo**
- Cálculo de ratios riesgo/beneficio
- Determinación de tamaños de posición
- Establecimiento de stop-loss y take-profit
- Diversificación de portafolio

## 📈 **Estrategias de Inversión**
- Swing trading y day trading
- Inversión a largo plazo
- Análisis fundamental básico
- Timing de mercado

## 🎯 **Formato de Respuesta**
Usa **Markdown** para estructurar tus respuestas:
- **Títulos** con ### para secciones principales
- **Listas** con - o 1. para puntos clave
- **Código** con \`\`\` para ejemplos
- **Tablas** para comparaciones
- **Citas** con > para advertencias importantes

## ⚠️ **Advertencias Obligatorias**
Siempre incluye advertencias de riesgo apropiadas y recuerda que:
- El trading conlleva riesgo de pérdida
- Los análisis son educativos, no consejos financieros
- Cada trader debe hacer su propio análisis

Mantén un tono profesional pero accesible, y estructura bien la información para facilitar la lectura."""
    
    # Construir el array de mensajes con contexto
    messages = [{"role": "system", "content": system_prompt}]
    
    # Agregar historial de conversación si existe
    if conversation_history:
        messages.extend(conversation_history)
    
    # Agregar el mensaje actual
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=4000,  # Suficiente para análisis detallado
            stream=False  # Para respuestas completas
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al procesar la respuesta: {str(e)}"

def get_trading_analysis(prompt, include_risk_assessment=True, conversation_history=None):
    """
    Función especializada para análisis de trading con contexto
    """
    if include_risk_assessment:
        enhanced_prompt = f"{prompt}\n\nPor favor incluye una evaluación de riesgo y posibles escenarios."
    else:
        enhanced_prompt = prompt
    
    return get_gpt_response(
        prompt=enhanced_prompt,
        model="gpt-4o",
        temperature=0.3,  # Más conservador para análisis financiero
        conversation_history=conversation_history,
        system_prompt="""Eres un analista de trading experto. Proporciona análisis técnico preciso, 
        identifica patrones en gráficos, calcula niveles de soporte/resistencia, y siempre 
        incluye advertencias de riesgo apropiadas. Usa Markdown para estructurar bien la información."""
    )

def get_quick_analysis(prompt, conversation_history=None):
    """
    Para análisis rápidos y básicos (usando modelo más económico)
    """
    return get_gpt_response(
        prompt=prompt,
        model="gpt-4o-mini",
        temperature=0.5,
        conversation_history=conversation_history
    )

def analyze_chart_image(image_url, prompt=""):
    """
    Para análisis de imágenes de gráficos (requiere GPT-4o con visión)
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto en análisis técnico. Analiza este gráfico de trading identificando patrones, tendencias, soportes, resistencias y posibles señales de entrada/salida."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Analiza este gráfico de trading: {prompt}"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al analizar la imagen: {str(e)}"