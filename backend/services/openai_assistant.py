import os
import json
import time
from openai import OpenAI
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

# Configurar logging
logger = logging.getLogger(__name__)

class OpenAIAssistant:
    def __init__(self):
        """Inicializa el cliente de OpenAI y configura el assistant"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Cargar configuración del assistant
        from config.assistant_config import ASSISTANT_ID, ASSISTANT_CONFIG
        
        self.assistant_id = ASSISTANT_ID
        self.assistant_name = ASSISTANT_CONFIG["name"]
        self.model = ASSISTANT_CONFIG["model"]
        self.instructions = self._load_instructions()
        self.tools = self._load_tools()
        
        # Verificar que el assistant existe y configurarlo
        self._verify_and_setup_assistant()
    
    def _load_instructions(self) -> str:
        """Carga las instrucciones base del assistant desde el archivo de configuración"""
        from config.mentor_forex_config import BOT_NAME, BOT_SPECIALTY, RISK_WARNINGS
        
        instructions = f"""
# **{BOT_NAME} - ASISTENTE DE TRADING**

## **IDENTIDAD Y ESPECIALIDAD**
- **Nombre:** {BOT_NAME}
- **Especialidad:** {BOT_SPECIALTY}
- **Enfoque:** Educación, análisis técnico y fundamental, gestión de riesgo

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
- Swing trading, Day trading, Scalping, Position trading
- Análisis de tendencias y momentum

## **PARES DE DIVISAS PRINCIPALES**
- **Majors:** EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, NZD/USD
- **Crosses:** EUR/GBP, EUR/JPY, GBP/JPY, etc.
- **Criptomonedas:** BTC/USD, ETH/USD, y otros pares principales

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
{chr(10).join([f"- {warning}" for warning in RISK_WARNINGS])}

## **TONO Y ESTILO**
- **Profesional pero accesible**
- **Educativo y mentor**
- **Basado en datos y análisis**
- **Honesto sobre riesgos**
- **Motivador pero realista**

## **FUNCIONES DISPONIBLES**
Puedes usar las siguientes funciones para obtener información en tiempo real:
- `get_crypto_price`: Obtener precios actuales de criptomonedas
- `get_forex_price`: Obtener precios actuales de pares de divisas
- `analyze_image`: Analizar imágenes de gráficos subidas por el usuario

## **INSTRUCCIONES ESPECÍFICAS**
1. Siempre verifica los precios actuales antes de dar recomendaciones
2. Analiza imágenes de gráficos cuando el usuario las proporcione
3. Proporciona análisis detallados pero comprensibles
4. Incluye siempre gestión de riesgo en tus recomendaciones
5. Mantén un tono educativo y profesional
"""
        return instructions
    
    def _load_tools(self) -> List[Dict[str, Any]]:
        """Define las herramientas/funciones disponibles para el assistant"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_crypto_price",
                    "description": "Obtiene el precio actual de una criptomoneda en tiempo real",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Símbolo de la criptomoneda (ej: BTC, ETH, ADA)",
                                "enum": ["BTC", "ETH", "ADA", "DOT", "LINK", "UNI", "LTC", "BCH", "XRP", "SOL"]
                            }
                        },
                        "required": ["symbol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_forex_price",
                    "description": "Obtiene el precio actual de un par de divisas en tiempo real",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pair": {
                                "type": "string",
                                "description": "Par de divisas (ej: EUR/USD, GBP/USD)",
                                "enum": ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP", "EUR/JPY", "GBP/JPY"]
                            }
                        },
                        "required": ["pair"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_image",
                    "description": "Analiza una imagen de gráfico de trading para identificar patrones y tendencias",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "image_url": {
                                "type": "string",
                                "description": "URL de la imagen a analizar"
                            },
                            "analysis_type": {
                                "type": "string",
                                "description": "Tipo de análisis a realizar",
                                "enum": ["technical", "pattern", "support_resistance", "complete"],
                                "default": "complete"
                            }
                        },
                        "required": ["image_url"]
                    }
                }
            }
        ]
    
    def _verify_and_setup_assistant(self):
        """Verifica que el assistant existe y lo configura"""
        try:
            # Verificar que el assistant existe
            assistant = self.client.beta.assistants.retrieve(self.assistant_id)
            logger.info(f"Assistant verificado: {assistant.id} - {assistant.name}")
            
            # Actualizar assistant si es necesario
            self._update_assistant_if_needed(assistant)
                
        except Exception as e:
            logger.error(f"Error verificando assistant: {e}")
            logger.error("Asegúrate de que el assistant_id sea correcto y que tengas permisos para acceder a él")
            raise
    
    def _update_assistant_if_needed(self, existing_assistant):
        """Actualiza el assistant si las instrucciones o herramientas han cambiado"""
        try:
            # Verificar si necesita actualización
            needs_update = False
            
            if existing_assistant.instructions != self.instructions:
                needs_update = True
                logger.info("Instrucciones actualizadas")
            
            # Comparar herramientas
            current_tools = existing_assistant.tools
            if len(current_tools) != len(self.tools):
                needs_update = True
                logger.info("Herramientas actualizadas")
            
            if needs_update:
                self.client.beta.assistants.update(
                    assistant_id=self.assistant_id,
                    instructions=self.instructions,
                    tools=self.tools
                )
                logger.info("Assistant actualizado")
                
        except Exception as e:
            logger.error(f"Error actualizando assistant: {e}")
    
    def get_or_create_thread(self, user_id: str) -> str:
        """Obtiene o crea un thread para el usuario"""
        try:
            # Aquí deberías buscar en tu base de datos si el usuario ya tiene un thread_id
            # Por ahora, creamos uno nuevo cada vez
            thread = self.client.beta.threads.create()
            logger.info(f"Nuevo thread creado para usuario {user_id}: {thread.id}")
            return thread.id
            
        except Exception as e:
            logger.error(f"Error creando thread: {e}")
            raise
    
    def send_message(self, thread_id: str, message: str, file_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Envía un mensaje al thread y obtiene la respuesta"""
        try:
            # Crear el mensaje
            message_data = {
                "role": "user",
                "content": message
            }
            
            if file_ids:
                message_data["file_ids"] = file_ids
            
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                **message_data
            )
            
            # Ejecutar el run
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id
            )
            
            # Esperar a que termine
            run = self._wait_for_run_completion(thread_id, run.id)
            
            if run.status == "completed":
                # Obtener la respuesta
                messages = self.client.beta.threads.messages.list(thread_id=thread_id)
                assistant_message = messages.data[0]  # El más reciente
                
                return {
                    "success": True,
                    "message": assistant_message.content[0].text.value,
                    "run_id": run.id
                }
            else:
                return {
                    "success": False,
                    "error": f"Run falló con status: {run.status}",
                    "run_id": run.id
                }
                
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _wait_for_run_completion(self, thread_id: str, run_id: str, timeout: int = 60) -> Any:
        """Espera a que el run se complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            if run.status in ["completed", "failed", "cancelled", "expired"]:
                return run
            
            # Si requiere acción, manejarla
            if run.status == "requires_action":
                run = self._handle_required_action(thread_id, run)
                if run.status in ["completed", "failed", "cancelled", "expired"]:
                    return run
            
            time.sleep(1)
        
        raise TimeoutError("Run no completó en el tiempo especificado")
    
    def _handle_required_action(self, thread_id: str, run: Any) -> Any:
        """Maneja las acciones requeridas por el assistant (llamadas a funciones)"""
        try:
            if run.required_action and run.required_action.type == "submit_tool_outputs":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    # Ejecutar la función correspondiente
                    from .functions import execute_function
                    result = execute_function(function_name, arguments)
                    
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(result)
                    })
                
                # Enviar los resultados
                run = self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                
                return run
                
        except Exception as e:
            logger.error(f"Error manejando acción requerida: {e}")
            raise
    
    def upload_file(self, file_path: str) -> str:
        """Sube un archivo y retorna el file_id"""
        try:
            with open(file_path, "rb") as file:
                uploaded_file = self.client.files.create(
                    file=file,
                    purpose="assistants"
                )
            
            # En la nueva API, los archivos se asocian automáticamente con el assistant
            # cuando se usan en un mensaje, no necesitamos asociarlos manualmente
            
            logger.info(f"Archivo subido: {uploaded_file.id}")
            return uploaded_file.id
            
        except Exception as e:
            logger.error(f"Error subiendo archivo: {e}")
            raise
    
    def get_thread_messages(self, thread_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene los mensajes de un thread"""
        try:
            messages = self.client.beta.threads.messages.list(
                thread_id=thread_id,
                limit=limit
            )
            
            formatted_messages = []
            for msg in messages.data:
                formatted_messages.append({
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content[0].text.value if msg.content else "",
                    "created_at": msg.created_at
                })
            
            return formatted_messages
            
        except Exception as e:
            logger.error(f"Error obteniendo mensajes: {e}")
            return []
    
    def delete_thread(self, thread_id: str) -> bool:
        """Elimina un thread"""
        try:
            self.client.beta.threads.delete(thread_id)
            logger.info(f"Thread eliminado: {thread_id}")
            return True
        except Exception as e:
            logger.error(f"Error eliminando thread: {e}")
            return False

# Instancia global del assistant
assistant_manager = OpenAIAssistant() 