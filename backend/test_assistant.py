#!/usr/bin/env python3
"""
Script de prueba para verificar que el assistant funciona correctamente
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_assistant_connection():
    """Prueba la conexión con el assistant"""
    try:
        from services.openai_assistant import assistant_manager
        
        print("✅ Assistant Manager inicializado correctamente")
        print(f"📋 Assistant ID: {assistant_manager.assistant_id}")
        print(f"🤖 Nombre: {assistant_manager.assistant_name}")
        print(f"🧠 Modelo: {assistant_manager.model}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando Assistant Manager: {e}")
        return False

def test_openai_connection():
    """Prueba la conexión con OpenAI"""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Verificar que la API key funciona
        models = client.models.list()
        print("✅ Conexión con OpenAI exitosa")
        print(f"📊 Modelos disponibles: {len(models.data)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error conectando con OpenAI: {e}")
        return False

def test_assistant_retrieval():
    """Prueba la recuperación del assistant específico"""
    try:
        from openai import OpenAI
        from config.assistant_config import ASSISTANT_ID
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Intentar recuperar el assistant
        assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
        
        print("✅ Assistant recuperado exitosamente")
        print(f"🆔 ID: {assistant.id}")
        print(f"📝 Nombre: {assistant.name}")
        print(f"🧠 Modelo: {assistant.model}")
        print(f"🛠️ Herramientas: {len(assistant.tools)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error recuperando assistant: {e}")
        return False

def test_thread_creation():
    """Prueba la creación de un thread"""
    try:
        from services.openai_assistant import assistant_manager
        
        # Crear un thread de prueba
        thread_id = assistant_manager.get_or_create_thread("test_user")
        
        print("✅ Thread creado exitosamente")
        print(f"🧵 Thread ID: {thread_id}")
        
        return thread_id
        
    except Exception as e:
        print(f"❌ Error creando thread: {e}")
        return None

def test_message_sending(thread_id):
    """Prueba el envío de un mensaje"""
    try:
        from services.openai_assistant import assistant_manager
        
        # Enviar un mensaje de prueba
        test_message = "Hola, ¿puedes darme el precio actual de Bitcoin?"
        
        print(f"📤 Enviando mensaje: {test_message}")
        
        result = assistant_manager.send_message(thread_id, test_message)
        
        if result['success']:
            print("✅ Mensaje enviado exitosamente")
            print(f"📨 Respuesta: {result['message'][:100]}...")
            return True
        else:
            print(f"❌ Error enviando mensaje: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")
        return False

def test_function_calls():
    """Prueba las funciones externas"""
    try:
        from services.functions import execute_function
        
        print("🧪 Probando función get_crypto_price...")
        
        result = execute_function("get_crypto_price", {"symbol": "BTC"})
        
        if result['success']:
            print("✅ Función get_crypto_price funciona")
            print(f"💰 Precio BTC: ${result['price_usd']}")
            return True
        else:
            print(f"❌ Error en función: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando funciones: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del Assistant...")
    print("=" * 50)
    
    # Verificar variables de entorno
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY no encontrada en variables de entorno")
        return False
    
    print("✅ Variables de entorno configuradas")
    
    # Ejecutar pruebas
    tests = [
        ("Conexión OpenAI", test_openai_connection),
        ("Recuperación Assistant", test_assistant_retrieval),
        ("Inicialización Manager", test_assistant_connection),
        ("Funciones Externas", test_function_calls),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Ejecutando: {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASÓ")
        else:
            print(f"❌ {test_name}: FALLÓ")
    
    # Prueba de thread y mensaje (solo si las anteriores pasaron)
    if passed == total:
        print(f"\n🧪 Ejecutando: Creación de Thread y Mensaje")
        print("-" * 30)
        
        thread_id = test_thread_creation()
        if thread_id:
            if test_message_sending(thread_id):
                passed += 1
                print("✅ Thread y Mensaje: PASÓ")
            else:
                print("❌ Thread y Mensaje: FALLÓ")
        else:
            print("❌ Thread y Mensaje: FALLÓ")
        total += 1
    
    # Resumen
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El assistant está listo para usar.")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 