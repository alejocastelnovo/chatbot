# OpenAI Assistants API - Sistema de Trading

Este documento explica cómo usar el nuevo sistema de OpenAI Assistants API implementado en el backend.

## 🚀 Características Principales

### ✅ Funcionalidades Implementadas

1. **Assistant Persistente**: Un assistant especializado en trading que mantiene su configuración
2. **Threads por Usuario**: Cada usuario tiene su propio thread para mantener contexto
3. **Funciones Externas**: Integración con APIs para precios en tiempo real
4. **Análisis de Imágenes**: Capacidad de analizar gráficos de trading
5. **Gestión de Archivos**: Subida y procesamiento de archivos
6. **Historial Persistente**: Conversaciones guardadas en Firebase

### 🔧 Funciones Disponibles

El assistant puede llamar automáticamente a estas funciones:

- **`get_crypto_price(symbol)`**: Obtiene precios de criptomonedas (BTC, ETH, etc.)
- **`get_forex_price(pair)`**: Obtiene precios de pares de divisas (EUR/USD, etc.)
- **`analyze_image(image_url, analysis_type)`**: Analiza imágenes de gráficos

## 📁 Estructura de Archivos

```
backend/
├── services/
│   ├── openai_assistant.py    # Manejador principal del assistant
│   └── functions.py           # Funciones externas disponibles
├── routes/
│   └── chat.py               # Endpoints de la API
└── config/
    └── mentor_forex_config.py # Configuración del bot
```

## 🔌 Endpoints Disponibles

### POST `/api/assistant/chat`
Envía un mensaje al assistant y obtiene respuesta.

**Body:**
```json
{
  "message": "¿Cuál es el precio actual de Bitcoin?",
  "files": [
    {
      "type": "image",
      "url": "https://ejemplo.com/grafico.png"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Respuesta del assistant...",
  "thread_id": "thread_abc123",
  "run_id": "run_xyz789"
}
```

### POST `/api/assistant/upload`
Sube un archivo al assistant.

**Form Data:**
- `file`: Archivo a subir (imagen)

**Response:**
```json
{
  "success": true,
  "file_id": "file_abc123",
  "filename": "grafico.png",
  "size": 1024000
}
```

### GET `/api/assistant/history`
Obtiene el historial de mensajes del usuario.

**Response:**
```json
{
  "success": true,
  "messages": [
    {
      "id": "msg_123",
      "role": "user",
      "content": "Mensaje del usuario",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "thread_id": "thread_abc123"
}
```

### POST `/api/assistant/clear`
Limpia el historial del usuario (crea nuevo thread).

### POST `/api/assistant/analyze-image`
Análisis específico de imágenes.

**Body:**
```json
{
  "image_url": "https://ejemplo.com/grafico.png",
  "analysis_type": "complete",
  "prompt": "Analiza los patrones de velas"
}
```

## ⚙️ Configuración

### Variables de Entorno Requeridas

```bash
# OpenAI
OPENAI_API_KEY=tu_openai_api_key

# Firebase (ya configurado)
FIREBASE_PROJECT_ID=tu_proyecto_id
FIREBASE_PRIVATE_KEY=tu_private_key
FIREBASE_CLIENT_EMAIL=tu_client_email
# ... otras variables de Firebase
```

### Configuración del Assistant

El assistant usa el ID existente: `asst_G8G7YRvTNUntCd0hAc7qDpBH`

**Configuración automática:**
- **Modelo**: GPT-4o
- **Instrucciones**: Especializadas en trading y análisis técnico
- **Herramientas**: Funciones para precios y análisis de imágenes
- **Persistencia**: Se mantiene entre reinicios del servidor

**Para cambiar el assistant ID:**
Edita `backend/config/assistant_config.py` y modifica la variable `ASSISTANT_ID`

## 🔄 Flujo de Trabajo

1. **Usuario envía mensaje** → `/api/assistant/chat`
2. **Sistema obtiene/crea thread** → Busca en Firebase o crea nuevo
3. **Assistant procesa mensaje** → Usa contexto del thread
4. **Si necesita datos externos** → Llama funciones automáticamente
5. **Genera respuesta** → Con datos actualizados
6. **Guarda en Firebase** → Para historial y persistencia

## 🛠️ Uso en el Frontend

### Ejemplo de Integración

```javascript
// Enviar mensaje
const response = await fetch('/api/assistant/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${idToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: '¿Cuál es el análisis técnico de BTC?'
  })
});

const data = await response.json();
console.log(data.message); // Respuesta del assistant
```

### Subir Imagen

```javascript
const formData = new FormData();
formData.append('file', imageFile);

const response = await fetch('/api/assistant/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${idToken}`
  },
  body: formData
});
```

## 🧪 Testing del Assistant

### **Script de Prueba Automática**
```bash
# Ejecutar pruebas completas
cd backend
python test_assistant.py
```

Este script verifica:
- ✅ Conexión con OpenAI
- ✅ Recuperación del assistant
- ✅ Inicialización del manager
- ✅ Funciones externas
- ✅ Creación de threads
- ✅ Envío de mensajes

### **Prueba Manual**
```bash
# 1. Iniciar el servidor
python app.py

# 2. En otra terminal, probar endpoints
curl -X POST http://localhost:5000/api/assistant/chat \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuál es el precio de Bitcoin?"}'
```

## 🔍 Monitoreo y Logs

El sistema incluye logging detallado:

- **Creación de threads**
- **Llamadas a funciones externas**
- **Errores y excepciones**
- **Uso de recursos**

Los logs se guardan en `logs/app.log` con rotación automática.

## 🚨 Consideraciones Importantes

### Límites y Costos

1. **OpenAI API**: Cada mensaje consume tokens
2. **Rate Limits**: Las APIs externas tienen límites
3. **Almacenamiento**: Los threads se mantienen en OpenAI
4. **Archivos**: Máximo 10MB por archivo

### Seguridad

1. **Autenticación**: Requiere token de Firebase válido
2. **Autorización**: Solo usuarios premium pueden usar el assistant
3. **Validación**: Archivos y mensajes son validados
4. **Sanitización**: Inputs son sanitizados

### Optimización

1. **Threads**: Se reutilizan para mantener contexto
2. **Caché**: Los precios se podrían cachear (futuro)
3. **Límites**: Historial limitado a 50 mensajes
4. **Timeouts**: Requests con timeout de 60 segundos

## 🔮 Próximas Mejoras

1. **Streaming**: Respuestas en tiempo real
2. **Caché**: Cachear precios por 1 minuto
3. **Más APIs**: Integrar más fuentes de datos
4. **Análisis Avanzado**: Patrones más complejos
5. **Notificaciones**: Alertas de precio
6. **Backtesting**: Simulación de estrategias

## 🐛 Troubleshooting

### Problemas Comunes

1. **Thread no encontrado**: Se crea automáticamente uno nuevo
2. **API rate limit**: Se maneja con reintentos
3. **Archivo muy grande**: Límite de 10MB
4. **Token expirado**: Renovar token de Firebase

### Logs Útiles

```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Buscar errores
grep "ERROR" logs/app.log

# Ver requests del assistant
grep "assistant" logs/app.log
```

## 📞 Soporte

Para problemas o preguntas:

1. Revisar logs en `logs/app.log`
2. Verificar variables de entorno
3. Comprobar conectividad con OpenAI
4. Validar permisos de Firebase 