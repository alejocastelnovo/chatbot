# 🚀 Inicio Rápido - Sistema de Assistants API

## ⚡ **Configuración en 5 minutos**

### **1. Configurar Variables de Entorno**

#### **Backend** (`.env`)
```bash
# OpenAI (REQUERIDO)
OPENAI_API_KEY=tu_openai_api_key_aqui

# Firebase (ya configurado)
FIREBASE_PROJECT_ID=tu_proyecto_id
FIREBASE_PRIVATE_KEY=tu_private_key
FIREBASE_CLIENT_EMAIL=tu_client_email
# ... otras variables de Firebase
```

#### **Frontend** (`.env`)
```bash
VITE_API_BASE_URL=http://127.0.0.1:5000
```

### **2. Instalar Dependencias**

#### **Backend**
```bash
cd backend
pip install -r requirements.txt
```

#### **Frontend**
```bash
cd frontend
npm install
```

### **3. Probar el Sistema**

#### **Ejecutar Pruebas Automáticas**
```bash
cd backend
python test_assistant.py
```

**Resultado esperado:**
```
🚀 Iniciando pruebas del Assistant...
==================================================
✅ Variables de entorno configuradas

🧪 Ejecutando: Conexión OpenAI
------------------------------
✅ Conexión con OpenAI exitosa
📊 Modelos disponibles: 50

🧪 Ejecutando: Recuperación Assistant
------------------------------------
✅ Assistant recuperado exitosamente
🆔 ID: asst_G8G7YRvTNUntCd0hAc7qDpBH
📝 Nombre: Mentor Forex 1.0
🧠 Modelo: gpt-4o
🛠️ Herramientas: 3

🧪 Ejecutando: Inicialización Manager
------------------------------------
✅ Assistant Manager inicializado correctamente
📋 Assistant ID: asst_G8G7YRvTNUntCd0hAc7qDpBH
🤖 Nombre: Mentor Forex 1.0
🧠 Modelo: gpt-4o

🧪 Ejecutando: Funciones Externas
--------------------------------
🧪 Probando función get_crypto_price...
✅ Función get_crypto_price funciona
💰 Precio BTC: $43250.25

🧪 Ejecutando: Creación de Thread y Mensaje
------------------------------------------
✅ Thread creado exitosamente
🧵 Thread ID: thread_abc123
📤 Enviando mensaje: Hola, ¿puedes darme el precio actual de Bitcoin?
✅ Mensaje enviado exitosamente
📨 Respuesta: ¡Hola! Te proporciono el precio actual de Bitcoin...

==================================================
📊 Resultados: 5/5 pruebas pasaron
🎉 ¡Todas las pruebas pasaron! El assistant está listo para usar.
```

### **4. Iniciar Servidores**

#### **Backend**
```bash
cd backend
python app.py
```

#### **Frontend**
```bash
cd frontend
npm run dev
```

### **5. Probar en el Navegador**

1. **Abrir** http://localhost:5173
2. **Iniciar sesión** con cuenta premium
3. **Enviar mensaje**: "¿Cuál es el precio de Bitcoin?"
4. **Ver respuesta** con precio actual y análisis

## 🎯 **Casos de Prueba Rápidos**

### **Mensaje Simple**
```
¿Cuál es el precio actual de Bitcoin?
```

### **Análisis de Trading**
```
Analiza la tendencia de EUR/USD en las últimas 24 horas
```

### **Comparación de Activos**
```
Compara los precios de Bitcoin, Ethereum y Cardano
```

### **Análisis de Imagen**
1. **Subir imagen** de gráfico de trading
2. **Preguntar**: "Analiza este gráfico y dime qué patrones ves"

## 🔧 **Configuración Avanzada**

### **Cambiar Assistant ID**
Editar `backend/config/assistant_config.py`:
```python
ASSISTANT_ID = "tu_nuevo_assistant_id"
```

### **Modificar Configuraciones**
Editar `backend/config/assistant_config.py`:
```python
# Cambiar límites de archivos
FILE_CONFIG = {
    "max_file_size_mb": 20,  # Aumentar a 20MB
    "allowed_extensions": ["png", "jpg", "jpeg", "gif", "webp", "pdf"],
    "max_files_per_message": 10
}

# Cambiar timeouts
TIMEOUTS = {
    "openai_request": 120,  # Aumentar a 2 minutos
    "external_api": 15,
    "file_upload": 60,
    "image_analysis": 90
}
```

## 🚨 **Solución de Problemas**

### **Error: "OPENAI_API_KEY no encontrada"**
```bash
# Verificar que el archivo .env existe
ls -la backend/.env

# Verificar contenido
cat backend/.env | grep OPENAI_API_KEY
```

### **Error: "Assistant no encontrado"**
```bash
# Verificar que el assistant ID es correcto
cat backend/config/assistant_config.py | grep ASSISTANT_ID

# Verificar permisos en OpenAI
python backend/test_assistant.py
```

### **Error: "No se pudo conectar con el backend"**
```bash
# Verificar que el servidor está corriendo
curl http://localhost:5000/health

# Verificar logs
tail -f backend/logs/app.log
```

### **Error: "Se requiere cuenta premium"**
1. **Verificar rol** en Firebase
2. **Actualizar a premium** en la consola de Firebase
3. **Reiniciar sesión** en la aplicación

## 📊 **Monitoreo**

### **Logs en Tiempo Real**
```bash
# Backend logs
tail -f backend/logs/app.log

# Ver errores
grep "ERROR" backend/logs/app.log

# Ver requests del assistant
grep "assistant" backend/logs/app.log
```

### **Métricas de Uso**
```bash
# Ver threads creados
grep "Thread creado" backend/logs/app.log

# Ver funciones llamadas
grep "Ejecutando función" backend/logs/app.log

# Ver análisis de imágenes
grep "analizando imagen" backend/logs/app.log
```

## 🎉 **¡Listo para Usar!**

Una vez que todas las pruebas pasen:

- ✅ **Assistant configurado** y funcionando
- ✅ **Funciones externas** operativas
- ✅ **Análisis de imágenes** disponible
- ✅ **Precios en tiempo real** activos
- ✅ **Contexto persistente** habilitado

**¡El sistema está listo para producción!** 🚀

## 📞 **Soporte**

Si encuentras problemas:

1. **Ejecutar** `python test_assistant.py`
2. **Revisar** logs en `backend/logs/app.log`
3. **Verificar** variables de entorno
4. **Comprobar** conectividad con OpenAI

**¡Disfruta usando tu assistant de trading!** 💰📈 