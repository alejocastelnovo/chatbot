# Guía de Testing - Sistema de Assistants API

## 🧪 **Casos de Prueba**

### **1. Configuración Inicial**

#### **Backend**
```bash
# 1. Verificar variables de entorno
cat .env | grep OPENAI_API_KEY

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar servidor
python app.py

# 4. Verificar health check
curl http://localhost:5000/health
```

#### **Frontend**
```bash
# 1. Verificar variables de entorno
cat .env | grep VITE_API_BASE_URL

# 2. Instalar dependencias
npm install

# 3. Iniciar desarrollo
npm run dev

# 4. Abrir navegador
open http://localhost:5173
```

### **2. Autenticación y Roles**

#### **Usuario Free**
1. **Crear cuenta free** en Firebase
2. **Iniciar sesión** en la aplicación
3. **Verificar mensaje** "Actualiza a Premium para usar el assistant"
4. **Confirmar** que no puede enviar mensajes

#### **Usuario Premium**
1. **Actualizar rol** a `premium` en Firebase
2. **Iniciar sesión** en la aplicación
3. **Verificar** que puede usar todas las funcionalidades
4. **Confirmar** que el assistant responde

### **3. Funcionalidades Básicas**

#### **Chat Simple**
```javascript
// Mensaje de prueba
"¿Cuál es el precio actual de Bitcoin?"
```

**Resultado esperado:**
- Assistant responde con precio actual
- Incluye análisis técnico básico
- Muestra advertencias de riesgo

#### **Análisis de Trading**
```javascript
// Mensaje de prueba
"Analiza la tendencia de EUR/USD en las últimas 24 horas"
```

**Resultado esperado:**
- Assistant obtiene precio actual
- Proporciona análisis técnico
- Incluye niveles de soporte/resistencia

### **4. Análisis de Imágenes**

#### **Subida de Imagen**
1. **Preparar imagen** de gráfico de trading (PNG/JPG)
2. **Hacer clic** en botón de subida
3. **Seleccionar archivo**
4. **Verificar** que se sube correctamente

#### **Análisis Automático**
```javascript
// Subir imagen y preguntar
"Analiza este gráfico y dime qué patrones ves"
```

**Resultado esperado:**
- Assistant analiza la imagen
- Identifica patrones técnicos
- Proporciona recomendaciones

### **5. Funciones Externas**

#### **Precios de Criptomonedas**
```javascript
// Mensajes de prueba
"¿Cuál es el precio de Ethereum?"
"Muéstrame el precio de Bitcoin y su cambio en 24h"
"Compara los precios de BTC, ETH y ADA"
```

#### **Pares de Divisas**
```javascript
// Mensajes de prueba
"¿Cuál es el tipo de cambio EUR/USD?"
"Analiza GBP/USD y su tendencia"
"Compara USD/JPY con EUR/USD"
```

### **6. Contexto Persistente**

#### **Conversación Continua**
```javascript
// Secuencia de mensajes
"¿Cuál es el precio de Bitcoin?"
"¿Y cuál es tu análisis técnico?"
"¿Qué niveles de soporte y resistencia ves?"
"¿Recomiendas comprar o vender?"
```

**Resultado esperado:**
- Assistant mantiene contexto
- Referencia mensajes anteriores
- Análisis coherente y continuo

### **7. Gestión de Historial**

#### **Limpiar Historial**
1. **Enviar varios mensajes**
2. **Hacer clic** en botón de limpiar
3. **Verificar** que se crea nuevo thread
4. **Confirmar** que el contexto se reinicia

#### **Cargar Historial**
1. **Cerrar y abrir** la aplicación
2. **Verificar** que se carga historial previo
3. **Confirmar** que el contexto se mantiene

### **8. Manejo de Errores**

#### **Archivo Muy Grande**
1. **Intentar subir** archivo > 10MB
2. **Verificar** mensaje de error
3. **Confirmar** que no se procesa

#### **Formato No Válido**
1. **Intentar subir** archivo .txt o .pdf
2. **Verificar** mensaje de error
3. **Confirmar** que solo acepta imágenes

#### **Sin Conexión**
1. **Desconectar** internet
2. **Intentar enviar** mensaje
3. **Verificar** mensaje de error
4. **Reconectar** y probar de nuevo

## 🔍 **Verificación de Logs**

### **Backend Logs**
```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Buscar errores
grep "ERROR" logs/app.log

# Ver requests del assistant
grep "assistant" logs/app.log

# Ver llamadas a funciones
grep "function" logs/app.log
```

### **Frontend Console**
```javascript
// Abrir DevTools (F12)
// Verificar en Console:
console.log('User role:', userRole);
console.log('API response:', response);
console.log('Error:', error);
```

## 📊 **Métricas de Rendimiento**

### **Tiempos de Respuesta**
- **Mensaje simple**: < 5 segundos
- **Con función externa**: < 10 segundos
- **Análisis de imagen**: < 15 segundos

### **Uso de Recursos**
- **Memoria**: < 500MB
- **CPU**: < 50% durante requests
- **Red**: < 10MB por request

## 🚨 **Casos Edge**

### **1. Rate Limits**
```javascript
// Enviar 10 mensajes rápidamente
// Verificar que se maneja correctamente
```

### **2. Tokens Expirados**
```javascript
// Esperar 1 hora
// Intentar enviar mensaje
// Verificar renovación automática
```

### **3. Imágenes Corruptas**
```javascript
// Subir imagen corrupta
// Verificar manejo de error
```

### **4. Mensajes Muy Largos**
```javascript
// Enviar mensaje de 2000+ caracteres
// Verificar procesamiento
```

## ✅ **Checklist de Testing**

### **Funcionalidades Básicas**
- [ ] Login/logout funciona
- [ ] Usuario free ve mensaje de upgrade
- [ ] Usuario premium puede usar assistant
- [ ] Mensajes se envían y reciben
- [ ] Historial se carga correctamente

### **Análisis de Imágenes**
- [ ] Subida de archivos funciona
- [ ] Validación de tamaño (10MB)
- [ ] Validación de formato (imágenes)
- [ ] Análisis de imágenes funciona
- [ ] Manejo de errores de subida

### **Funciones Externas**
- [ ] Precios de crypto funcionan
- [ ] Precios de forex funcionan
- [ ] Rate limits se manejan
- [ ] Errores de API se manejan

### **Contexto y Persistencia**
- [ ] Threads se crean correctamente
- [ ] Contexto se mantiene entre mensajes
- [ ] Historial persiste entre sesiones
- [ ] Limpiar historial funciona

### **Interfaz de Usuario**
- [ ] Efecto de escritura funciona
- [ ] Atajos ESC/ENTER funcionan
- [ ] Botones de acción funcionan
- [ ] Responsive design funciona
- [ ] Manejo de errores en UI

### **Seguridad**
- [ ] Autenticación requerida
- [ ] Autorización por roles
- [ ] Validación de inputs
- [ ] Sanitización de datos

## 🎯 **Escenarios de Prueba**

### **Escenario 1: Usuario Nuevo**
1. Crear cuenta free
2. Verificar limitaciones
3. Actualizar a premium
4. Probar todas las funcionalidades

### **Escenario 2: Análisis Completo**
1. Subir imagen de gráfico
2. Preguntar sobre patrones
3. Solicitar análisis técnico
4. Pedir recomendaciones

### **Escenario 3: Conversación Larga**
1. Iniciar conversación sobre crypto
2. Cambiar a forex
3. Subir imágenes
4. Solicitar análisis comparativo

### **Escenario 4: Manejo de Errores**
1. Probar sin conexión
2. Subir archivos inválidos
3. Enviar mensajes muy largos
4. Verificar recuperación

## 📝 **Reporte de Bugs**

### **Template de Bug Report**
```
**Título**: [Descripción breve del problema]

**Severidad**: [Alta/Media/Baja]

**Pasos para reproducir**:
1. [Paso 1]
2. [Paso 2]
3. [Paso 3]

**Resultado esperado**: [Qué debería pasar]

**Resultado actual**: [Qué está pasando]

**Logs**:
[Pegar logs relevantes]

**Screenshots**: [Si aplica]

**Navegador/Sistema**: [Versiones]
```

## 🎉 **Criterios de Aceptación**

El sistema está listo para producción cuando:

- [ ] Todos los casos de prueba pasan
- [ ] No hay errores críticos
- [ ] Rendimiento es aceptable
- [ ] Seguridad está validada
- [ ] UX es satisfactoria
- [ ] Documentación está completa

¡El sistema está listo para testing! 🚀 