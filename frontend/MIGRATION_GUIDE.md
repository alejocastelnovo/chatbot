# Guía de Migración - Sistema de Assistants API

## 🚀 Cambios Realizados

### ✅ **Componente Reemplazado**
- **Antes**: `Chat` (sistema básico de chat)
- **Ahora**: `AssistantChat` (sistema avanzado con OpenAI Assistants API)

### ✅ **Archivos Modificados**

#### **1. `src/App.jsx`**
```javascript
// ANTES
import Chat from './components/chat';

// AHORA
import AssistantChat from './components/AssistantChat';

// Y en el render:
<AssistantChat 
  userId={user.user_id} 
  selectedChat={selectedChat} 
  onNewChat={handleNewChat} 
  onChatCreated={handleChatCreated}
/>
```

#### **2. `src/config/api.js`**
Agregados nuevos endpoints:
```javascript
// Nuevos endpoints del sistema de Assistants API
assistantChat: `${API_BASE_URL}/api/assistant/chat`,
assistantUpload: `${API_BASE_URL}/api/assistant/upload`,
assistantHistory: `${API_BASE_URL}/api/assistant/history`,
assistantClear: `${API_BASE_URL}/api/assistant/clear`,
assistantAnalyzeImage: `${API_BASE_URL}/api/assistant/analyze-image`
```

#### **3. `src/components/AssistantChat.jsx`**
Nuevo componente con todas las funcionalidades avanzadas.

## 🆕 **Nuevas Funcionalidades**

### **1. Análisis de Imágenes**
- ✅ Subida de imágenes con drag & drop
- ✅ Análisis automático de gráficos de trading
- ✅ Soporte para múltiples formatos (PNG, JPG, GIF, WebP)
- ✅ Límite de 10MB por archivo

### **2. Precios en Tiempo Real**
- ✅ Precios de criptomonedas (Bitcoin, Ethereum, etc.)
- ✅ Precios de pares de divisas (EUR/USD, GBP/USD, etc.)
- ✅ Llamadas automáticas según el contexto

### **3. Contexto Persistente**
- ✅ Threads individuales por usuario
- ✅ Historial mantenido entre sesiones
- ✅ Contexto inteligente para análisis continuos

### **4. Interfaz Mejorada**
- ✅ Efecto de escritura con atajos (ESC/ENTER)
- ✅ Botón para limpiar historial
- ✅ Indicadores de carga y estado
- ✅ Manejo de errores mejorado

## 🔧 **Configuración Requerida**

### **Backend**
1. **Variables de entorno** en `.env`:
   ```bash
   OPENAI_API_KEY=tu_openai_api_key
   ```

2. **Instalar dependencias**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Iniciar el servidor**:
   ```bash
   python app.py
   ```

### **Frontend**
1. **Variables de entorno** en `.env`:
   ```bash
   VITE_API_BASE_URL=http://127.0.0.1:5000
   ```

2. **Instalar dependencias** (si no están):
   ```bash
   cd frontend
   npm install
   ```

3. **Iniciar el desarrollo**:
   ```bash
   npm run dev
   ```

## 🎯 **Diferencias Clave**

### **Sistema Anterior vs Nuevo**

| Característica | Sistema Anterior | Nuevo Sistema |
|---|---|---|
| **Modelo** | GPT-4o básico | GPT-4o con Assistants API |
| **Contexto** | Limitado por tokens | Threads persistentes |
| **Imágenes** | No soportado | Análisis completo |
| **Precios** | Manual | Automático |
| **Funciones** | Básicas | Avanzadas con llamadas externas |
| **Historial** | Firebase básico | Firebase + OpenAI threads |
| **Escalabilidad** | Limitada | Alta |

## 🚨 **Consideraciones Importantes**

### **1. Usuarios Premium**
- Solo usuarios con rol `premium` pueden usar el assistant
- Los usuarios `free` verán un mensaje de actualización

### **2. Costos**
- Cada mensaje consume tokens de OpenAI
- Las llamadas a funciones externas tienen rate limits
- Los threads se mantienen en OpenAI (costo de almacenamiento)

### **3. Límites**
- Máximo 10MB por archivo
- Rate limits en APIs externas
- Timeout de 60 segundos por request

## 🔄 **Flujo de Trabajo del Usuario**

### **1. Usuario Premium**
1. **Inicia sesión** → Se verifica rol premium
2. **Envía mensaje** → Se procesa con assistant
3. **Sube imagen** → Se analiza automáticamente
4. **Recibe respuesta** → Con datos en tiempo real
5. **Historial persistente** → Se mantiene entre sesiones

### **2. Usuario Free**
1. **Inicia sesión** → Se verifica rol free
2. **Ve mensaje** → "Actualiza a Premium para usar el assistant"
3. **No puede usar** → Funcionalidades bloqueadas

## 🛠️ **Troubleshooting**

### **Problemas Comunes**

#### **1. "Se requiere cuenta premium"**
- Verificar que el usuario tenga rol `premium` en Firebase
- Revisar la función `getUserRole()` en el backend

#### **2. "Error de conexión"**
- Verificar que el backend esté corriendo
- Comprobar `VITE_API_BASE_URL` en el frontend
- Revisar logs del backend

#### **3. "Error subiendo archivos"**
- Verificar tamaño del archivo (máximo 10MB)
- Comprobar formato (solo imágenes)
- Revisar permisos de escritura en el servidor

#### **4. "Assistant no responde"**
- Verificar `OPENAI_API_KEY`
- Comprobar límites de rate en OpenAI
- Revisar logs del backend

### **Logs Útiles**

#### **Backend**
```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Buscar errores del assistant
grep "assistant" logs/app.log

# Ver requests de OpenAI
grep "openai" logs/app.log
```

#### **Frontend**
```javascript
// En la consola del navegador
console.log('User role:', userRole);
console.log('API response:', response);
```

## 🔮 **Próximas Mejoras**

### **Planeadas**
1. **Streaming**: Respuestas en tiempo real
2. **Caché**: Cachear precios por 1 minuto
3. **Más APIs**: Integrar más fuentes de datos
4. **Análisis Avanzado**: Patrones más complejos
5. **Notificaciones**: Alertas de precio
6. **Backtesting**: Simulación de estrategias

### **Sugeridas**
1. **Modo Offline**: Funcionalidades básicas sin conexión
2. **Exportar**: Guardar análisis en PDF
3. **Compartir**: Compartir análisis con otros usuarios
4. **Personalización**: Configurar preferencias del assistant

## 📞 **Soporte**

Para problemas o preguntas:

1. **Revisar logs** en `backend/logs/app.log`
2. **Verificar configuración** de variables de entorno
3. **Comprobar conectividad** con OpenAI
4. **Validar permisos** de Firebase

## ✅ **Checklist de Migración**

- [ ] Backend configurado con OpenAI API key
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Variables de entorno configuradas
- [ ] Frontend usando nuevo componente `AssistantChat`
- [ ] Endpoints actualizados en `api.js`
- [ ] Usuarios premium configurados en Firebase
- [ ] Sistema probado con imágenes y precios
- [ ] Historial funcionando correctamente
- [ ] Manejo de errores implementado

¡La migración está completa! El nuevo sistema ofrece capacidades mucho más avanzadas y una experiencia de usuario superior. 