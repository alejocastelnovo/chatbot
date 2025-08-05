from flask import Blueprint, request, jsonify
from firebase_config import verify_firebase_token, get_user_role, db
from services.openai_assistant import assistant_manager
from services.functions import execute_function
from datetime import datetime
import logging
import os
import tempfile
from werkzeug.utils import secure_filename

# Configurar logging
logger = logging.getLogger(__name__)

# Crear blueprint
chat_bp = Blueprint('chat', __name__)

# Cargar configuración de archivos
from config.assistant_config import FILE_CONFIG

ALLOWED_EXTENSIONS = set(FILE_CONFIG["allowed_extensions"])
MAX_FILE_SIZE = FILE_CONFIG["max_file_size_mb"] * 1024 * 1024

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_thread_id(user_id: str) -> str:
    """
    Obtiene o crea un thread_id para el usuario desde Firebase
    """
    try:
        # Buscar en Firestore si el usuario ya tiene un thread_id
        user_doc = db.collection('users').document(user_id).get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            thread_id = user_data.get('thread_id')
            
            if thread_id:
                # Verificar que el thread aún existe en OpenAI
                try:
                    assistant_manager.client.beta.threads.retrieve(thread_id)
                    logger.info(f"Thread existente encontrado para usuario {user_id}: {thread_id}")
                    return thread_id
                except Exception as e:
                    logger.warning(f"Thread {thread_id} no existe, creando uno nuevo")
        
        # Crear nuevo thread
        thread_id = assistant_manager.get_or_create_thread(user_id)
        
        # Guardar thread_id en Firestore
        db.collection('users').document(user_id).update({
            'thread_id': thread_id,
            'fechaActualizacion': datetime.now()
        })
        
        logger.info(f"Nuevo thread creado y guardado para usuario {user_id}: {thread_id}")
        return thread_id
        
    except Exception as e:
        logger.error(f"Error obteniendo thread_id para usuario {user_id}: {e}")
        # Fallback: crear thread sin guardar en Firebase
        return assistant_manager.get_or_create_thread(user_id)

@chat_bp.route('/assistant/chat', methods=['POST'])
def assistant_chat():
    """
    Endpoint principal para chat con el assistant
    """
    # Verificar autenticación
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Token de autorización requerido'}), 401
    
    id_token = auth_header.split('Bearer ')[1]
    decoded_token = verify_firebase_token(id_token)
    
    if not decoded_token:
        return jsonify({'error': 'Token inválido'}), 401
    
    user_id = decoded_token['uid']
    user_role = get_user_role(user_id)
    
    # Verificar si el usuario es premium
    if user_role != 'premium':
        return jsonify({'error': 'Se requiere cuenta premium para usar el assistant'}), 403
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        message = data.get('message', '').strip()
        # Permitir mensajes vacíos si hay archivos adjuntos
        if not message and not data.get('files'):
            return jsonify({'error': 'Mensaje requerido o archivos adjuntos'}), 400
        
        # Obtener o crear thread_id para el usuario
        thread_id = get_user_thread_id(user_id)
        
        # Procesar archivos si los hay
        file_ids = []
        if 'files' in data and data['files']:
            for file_data in data['files']:
                if file_data.get('type') == 'image' and file_data.get('url'):
                    # El url contiene el file_id que devolvió el endpoint de upload
                    file_ids.append(file_data['url'])
        
        # Enviar mensaje al assistant
        result = assistant_manager.send_message(thread_id, message, file_ids)
        
        if result['success']:
            # Guardar mensaje en Firebase para historial
            save_message_to_firebase(user_id, thread_id, 'user', message)
            save_message_to_firebase(user_id, thread_id, 'assistant', result['message'])
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'thread_id': thread_id,
                'run_id': result.get('run_id')
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"Error en assistant_chat: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@chat_bp.route('/assistant/upload', methods=['POST'])
def upload_file():
    """
    Endpoint para subir archivos al assistant
    """
    # Verificar autenticación
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Token de autorización requerido'}), 401
    
    id_token = auth_header.split('Bearer ')[1]
    decoded_token = verify_firebase_token(id_token)
    
    if not decoded_token:
        return jsonify({'error': 'Token inválido'}), 401
    
    user_id = decoded_token['uid']
    user_role = get_user_role(user_id)
    
    # Verificar si el usuario es premium
    if user_role != 'premium':
        return jsonify({'error': 'Se requiere cuenta premium para subir archivos'}), 403
    
    try:
        # Verificar si hay archivo en la request
        if 'file' not in request.files:
            return jsonify({'error': 'No se encontró archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        # Verificar tipo de archivo
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
        # Verificar tamaño
        file.seek(0, 2)  # Ir al final del archivo
        file_size = file.tell()
        file.seek(0)  # Volver al inicio
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'Archivo demasiado grande (máximo 10MB)'}), 400
        
        # Guardar archivo temporalmente
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Subir archivo a OpenAI
            file_id = assistant_manager.upload_file(temp_path)
            
            return jsonify({
                'success': True,
                'file_id': file_id,
                'filename': filename,
                'size': file_size
            })
            
        except Exception as upload_error:
            logger.error(f"Error subiendo archivo a OpenAI: {upload_error}")
            return jsonify({
                'success': False,
                'error': f'Error subiendo archivo a OpenAI: {str(upload_error)}'
            }), 500
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception as cleanup_error:
                    logger.warning(f"Error limpiando archivo temporal: {cleanup_error}")
                
    except Exception as e:
        logger.error(f"Error subiendo archivo: {e}")
        return jsonify({'error': 'Error subiendo archivo'}), 500

@chat_bp.route('/assistant/history', methods=['GET'])
def get_assistant_history():
    """
    Obtiene el historial de mensajes del assistant para el usuario
    """
    # Verificar autenticación
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Token de autorización requerido'}), 401
    
    id_token = auth_header.split('Bearer ')[1]
    decoded_token = verify_firebase_token(id_token)
    
    if not decoded_token:
        return jsonify({'error': 'Token inválido'}), 401
    
    user_id = decoded_token['uid']
    user_role = get_user_role(user_id)
    
    # Verificar si el usuario es premium
    if user_role != 'premium':
        return jsonify({'error': 'Se requiere cuenta premium para ver historial'}), 403
    
    try:
        # Obtener thread_id del usuario
        user_doc = db.collection('users').document(user_id).get()
        if not user_doc.exists:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        user_data = user_doc.to_dict()
        thread_id = user_data.get('thread_id')
        
        if not thread_id:
            return jsonify({'messages': []})
        
        # Obtener mensajes del thread
        messages = assistant_manager.get_thread_messages(thread_id, limit=50)
        
        return jsonify({
            'success': True,
            'messages': messages,
            'thread_id': thread_id
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        return jsonify({'error': 'Error obteniendo historial'}), 500

@chat_bp.route('/assistant/clear', methods=['POST'])
def clear_assistant_history():
    """
    Limpia el historial del assistant para el usuario
    """
    # Verificar autenticación
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Token de autorización requerido'}), 401
    
    id_token = auth_header.split('Bearer ')[1]
    decoded_token = verify_firebase_token(id_token)
    
    if not decoded_token:
        return jsonify({'error': 'Token inválido'}), 401
    
    user_id = decoded_token['uid']
    user_role = get_user_role(user_id)
    
    # Verificar si el usuario es premium
    if user_role != 'premium':
        return jsonify({'error': 'Se requiere cuenta premium'}), 403
    
    try:
        # Obtener thread_id del usuario
        user_doc = db.collection('users').document(user_id).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            thread_id = user_data.get('thread_id')
            
            if thread_id:
                # Eliminar thread existente
                assistant_manager.delete_thread(thread_id)
        
        # Crear nuevo thread
        new_thread_id = assistant_manager.get_or_create_thread(user_id)
        
        # Actualizar en Firebase
        db.collection('users').document(user_id).update({
            'thread_id': new_thread_id,
            'fechaActualizacion': datetime.now()
        })
        
        return jsonify({
            'success': True,
            'message': 'Historial limpiado correctamente',
            'new_thread_id': new_thread_id
        })
        
    except Exception as e:
        logger.error(f"Error limpiando historial: {e}")
        return jsonify({'error': 'Error limpiando historial'}), 500

@chat_bp.route('/assistant/analyze-image', methods=['POST'])
def analyze_image():
    """
    Endpoint específico para análisis de imágenes
    """
    # Verificar autenticación
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Token de autorización requerido'}), 401
    
    id_token = auth_header.split('Bearer ')[1]
    decoded_token = verify_firebase_token(id_token)
    
    if not decoded_token:
        return jsonify({'error': 'Token inválido'}), 401
    
    user_id = decoded_token['uid']
    user_role = get_user_role(user_id)
    
    # Verificar si el usuario es premium
    if user_role != 'premium':
        return jsonify({'error': 'Se requiere cuenta premium para análisis de imágenes'}), 403
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        image_url = data.get('image_url', '').strip()
        analysis_type = data.get('analysis_type', 'complete')
        prompt = data.get('prompt', '').strip()
        
        if not image_url:
            return jsonify({'error': 'URL de imagen requerida'}), 400
        
        # Ejecutar análisis de imagen
        result = execute_function('analyze_image', {
            'image_url': image_url,
            'analysis_type': analysis_type
        })
        
        if result['success']:
            # Si hay un prompt adicional, enviarlo al assistant
            if prompt:
                thread_id = get_user_thread_id(user_id)
                full_message = f"Analiza esta imagen: {image_url}\n\nPrompt adicional: {prompt}"
                
                assistant_result = assistant_manager.send_message(thread_id, full_message, [image_url])
                
                if assistant_result['success']:
                    result['assistant_analysis'] = assistant_result['message']
            
            return jsonify({
                'success': True,
                'analysis': result['analysis'],
                'assistant_analysis': result.get('assistant_analysis'),
                'image_url': image_url,
                'analysis_type': analysis_type
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"Error analizando imagen: {e}")
        return jsonify({'error': 'Error analizando imagen'}), 500

def save_message_to_firebase(user_id: str, thread_id: str, sender: str, text: str):
    """
    Guarda un mensaje en Firebase para el historial
    """
    try:
        # Crear documento de chat si no existe
        chat_ref = db.collection('chats').document(user_id).collection('conversations').document(thread_id)
        
        # Guardar mensaje
        chat_ref.collection('messages').add({
            'sender': sender,
            'text': text,
            'timestamp': datetime.now(),
            'thread_id': thread_id
        })
        
        # Actualizar metadata del chat
        chat_ref.set({
            'thread_id': thread_id,
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_message': datetime.now()
        }, merge=True)
        
    except Exception as e:
        logger.error(f"Error guardando mensaje en Firebase: {e}")

# Registrar blueprint en la aplicación principal
def init_app(app):
    app.register_blueprint(chat_bp, url_prefix='/api') 