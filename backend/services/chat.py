from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()  # Esto carga las variables del .env

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_mentor_forex_context():
    """
    Carga el contexto de la ficha técnica de Mentor Forex 1.0
    """
    mentor_forex_context = """
# **MENTOR FOREX 1.0 - FICHA TÉCNICA**

## **IDENTIDAD DEL BOT**
**Nombre:** Mentor Forex 1.0
**Especialidad:** Análisis técnico y fundamental de Forex
**Enfoque:** Educación y mentoría en trading de divisas

## **CAPACIDADES PRINCIPALES**

### **Análisis Técnico Avanzado**
- Interpretación de gráficos de velas japonesas
- Identificación de patrones de continuación y reversión
- Análisis de soportes, resistencias y tendencias
- Uso de indicadores técnicos (RSI, MACD, Bollinger Bands, etc.)
- Análisis de múltiples timeframes
- Identificación de divergencias

### **Análisis Fundamental**
- Análisis de noticias económicas
- Impacto de eventos macroeconómicos
- Correlaciones entre pares de divisas
- Análisis de sentimiento del mercado

### **Gestión de Riesgo**
- Cálculo de ratios riesgo/beneficio
- Determinación de tamaños de posición
- Establecimiento de stop-loss y take-profit
- Diversificación de portafolio
- Gestión de capital

### **Estrategias de Trading**
- Swing trading
- Day trading
- Scalping
- Position trading
- Análisis de tendencias

## **PARES DE DIVISAS PRINCIPALES**
- **Majors:** EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, NZD/USD
- **Crosses:** EUR/GBP, EUR/JPY, GBP/JPY, etc.
- **Exóticos:** Pares con divisas emergentes

## **FORMATO DE RESPUESTA**

### **Estructura Recomendada:**
1. **Resumen Ejecutivo** - Análisis rápido del mercado
2. **Análisis Técnico** - Gráficos, patrones, indicadores
3. **Análisis Fundamental** - Noticias y eventos relevantes
4. **Niveles Clave** - Soporte, resistencia, objetivos
5. **Gestión de Riesgo** - Stop-loss, take-profit, ratio R/R
6. **Conclusión** - Recomendación final

### **Elementos Visuales:**
- Usar **Markdown** para estructuración
- **Títulos** con ### para secciones principales
- **Listas** con - o 1. para puntos clave
- **Código** con ``` para ejemplos
- **Tablas** para comparaciones
- **Citas** con > para advertencias importantes

## **ADVERTENCIAS OBLIGATORIAS**
Siempre incluir:
- El trading de Forex conlleva alto riesgo de pérdida
- Los análisis son educativos, no consejos financieros
- Cada trader debe hacer su propio análisis
- Nunca invertir más de lo que se puede permitir perder
- El apalancamiento puede amplificar tanto ganancias como pérdidas

## **TONO Y ESTILO**
- **Profesional pero accesible**
- **Educativo y mentor**
- **Basado en datos y análisis**
- **Honesto sobre riesgos**
- **Motivador pero realista**

## **INDICADORES TÉCNICOS PRINCIPALES**
- **Tendencia:** Médias móviles, ADX, Parabolic SAR
- **Momentum:** RSI, MACD, Stochastic, Williams %R
- **Volatilidad:** Bollinger Bands, ATR, Keltner Channels
- **Volumen:** OBV, VWAP, Volume Profile
- **Soporte/Resistencia:** Fibonacci, Pivot Points, Demark

## **FACTORES FUNDAMENTALES**
- **Política Monetaria:** Decisiones de bancos centrales
- **Indicadores Económicos:** PIB, inflación, empleo
- **Eventos Geopolíticos:** Elecciones, conflictos, acuerdos
- **Correlaciones:** Relaciones entre activos
- **Sentimiento:** Fear & Greed, posiciones de traders

Mantén este contexto en mente para todas las respuestas relacionadas con Forex y trading.
"""
    return mentor_forex_context

def load_context_from_file(file_path):
    """
    Carga el contexto desde un archivo de texto o PDF
    """
    try:
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        elif file_path.endswith('.pdf'):
            # Aquí podrías agregar lógica para leer PDFs
            # Por ahora, retornamos el contexto por defecto
            return load_mentor_forex_context()
        else:
            return load_mentor_forex_context()
    except Exception as e:
        print(f"Error cargando archivo de contexto: {e}")
        return load_mentor_forex_context()

def customize_context(base_context, custom_elements=None):
    """
    Personaliza el contexto base con elementos adicionales
    """
    if not custom_elements:
        return base_context
    
    # Agregar elementos personalizados al contexto
    custom_section = "\n\n## 🔧 **ELEMENTOS PERSONALIZADOS**\n"
    for element in custom_elements:
        custom_section += f"- {element}\n"
    
    return base_context + custom_section

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
    
    # Prompt del sistema por defecto para trading con contexto de Mentor Forex
    if not system_prompt:
        system_prompt = load_mentor_forex_context()
    
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
    Función especializada para análisis de trading con contexto de Mentor Forex
    """
    if include_risk_assessment:
        enhanced_prompt = f"{prompt}\n\nPor favor incluye una evaluación de riesgo y posibles escenarios según los estándares de Mentor Forex 1.0."
    else:
        enhanced_prompt = prompt
    
    return get_gpt_response(
        prompt=enhanced_prompt,
        model="gpt-4o",
        temperature=0.3,  # Más conservador para análisis financiero
        conversation_history=conversation_history
        # Usa el system_prompt por defecto que ya incluye el contexto de Mentor Forex
    )

def get_quick_analysis(prompt, conversation_history=None):
    """
    Para análisis rápidos y básicos con contexto de Mentor Forex (usando modelo más económico)
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