import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from openai import OpenAI
from firebase_config import verify_firebase_token, get_user_role, create_user_document, db
from datetime import datetime
import firebase_admin
from firebase_admin import firestore

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

CORS(app, supports_credentials=True)
CORS(app, resources={r"/*": {"origins": "*"}})

# Inicializar OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Middleware para verificar autenticación
def require_auth(f):
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        print(f"🔍 Verificando autenticación para {f.__name__}")
        print(f"🔍 Auth header: {auth_header[:50] if auth_header else 'None'}...")
        
        if not auth_header or not auth_header.startswith('Bearer '):
            print("❌ No hay header de autorización válido")
            return jsonify({'error': 'Token de autorización requerido'}), 401
        
        id_token = auth_header.split('Bearer ')[1]
        print(f"🔍 Token recibido: {id_token[:20]}...")
        
        decoded_token = verify_firebase_token(id_token)
        
        if not decoded_token:
            print("❌ Token inválido o expirado")
            return jsonify({'error': 'Token inválido'}), 401
        
        print(f"✅ Token válido para usuario: {decoded_token.get('email', 'N/A')}")
        # Agregar información del usuario al request
        request.user = decoded_token
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/', methods=['GET'])
def home():
    return "API funcionando con Firebase", 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check para monitoreo"""
    try:
        # Verificar conexión a Firebase
        db.collection('health').document('test').get()
        
        # Verificar conexión a OpenAI
        client.models.list()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'firebase': 'connected',
                'openai': 'connected'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

@app.route('/create-chat', methods=['POST'])
@require_auth
def create_chat():
    """
    Crea un nuevo chat vacío
    """
    user_id = request.user['uid']
    user_role = get_user_role(user_id)
    
    # Verificar si el usuario es premium
    if user_role != 'premium':
        return jsonify({'error': 'Se requiere cuenta premium para crear chats'}), 403

    try:
        # Crear un nuevo chat
        chat_ref = db.collection('chats').document(user_id).collection('conversations').document()
        chat_id = chat_ref.id
        
        # Crear el documento del chat con metadata
        chat_ref.set({
            'created_at': datetime.now(),
            'user_id': user_id,
            'message_count': 0
        })

        # Limitar a últimos 5 chats
        limit_chats(user_id)

        return jsonify({
            'chat_id': chat_id,
            'message': 'Chat creado exitosamente'
        })

    except Exception as e:
        print(f"Error creando chat: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/chat', methods=['POST'])
@require_auth
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    chat_id = data.get('chat_id')
    
    if not user_message:
        return jsonify({'error': 'Mensaje requerido'}), 400

    user_id = request.user['uid']
    user_role = get_user_role(user_id)
    
    # Verificar si el usuario es premium
    if user_role != 'premium':
        return jsonify({'error': 'Se requiere cuenta premium para chatear'}), 403

    try:
        # Si no hay chat_id, crear un nuevo chat
        if not chat_id:
            chat_ref = db.collection('chats').document(user_id).collection('conversations').document()
            chat_id = chat_ref.id
        else:
            # Verificar que el chat pertenece al usuario
            chat_ref = db.collection('chats').document(user_id).collection('conversations').document(chat_id)
            if not chat_ref.get().exists:
                return jsonify({'error': 'Chat no encontrado'}), 404

        # Guardar mensaje del usuario
        message_data = {
            'sender': 'user',
            'text': user_message,
            'timestamp': datetime.now()
        }
        chat_ref.collection('messages').add(message_data)

                        # Usar el nuevo sistema de Assistants API
        from services.openai_assistant import assistant_manager
        
        # Obtener o crear thread_id para el usuario
        def get_user_thread_id(user_id):
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
                            return thread_id
                        except Exception as e:
                            print(f"Thread {thread_id} no existe, creando uno nuevo")
                
                # Crear nuevo thread
                thread_id = assistant_manager.get_or_create_thread(user_id)
                
                # Guardar thread_id en Firestore
                db.collection('users').document(user_id).update({
                    'thread_id': thread_id,
                    'fechaActualizacion': datetime.now()
                })
                
                return thread_id
                
            except Exception as e:
                print(f"Error obteniendo thread_id para usuario {user_id}: {e}")
                # Fallback: crear thread sin guardar en Firebase
                return assistant_manager.get_or_create_thread(user_id)
        
        thread_id = get_user_thread_id(user_id)
        
        # Enviar mensaje al assistant
        result = assistant_manager.send_message(thread_id, user_message)
        
        if result['success']:
            bot_reply = result['message']
        else:
            bot_reply = f"Error procesando mensaje: {result['error']}"

        # Guardar respuesta del bot
        bot_message_data = {
            'sender': 'bot',
            'text': bot_reply,
            'timestamp': datetime.now()
        }
        chat_ref.collection('messages').add(bot_message_data)

        # Limitar a últimos 5 chats
        limit_chats(user_id)

        return jsonify({
            'chat_id': chat_id, 
            'reply': bot_reply,
            'user_role': user_role
        })

    except Exception as e:
        print(f"Error en chat: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/history', methods=['GET'])
@require_auth
def history():
    user_id = request.user['uid']
    print(f"🔍 Obteniendo historial para usuario: {user_id}")
    
    try:
        # Obtener todos los chats del usuario
        chats_ref = db.collection('chats').document(user_id).collection('conversations')
        
        # Obtener todos los chats sin ordenar primero
        all_chats = list(chats_ref.stream())
        print(f"📊 Total de chats encontrados: {len(all_chats)}")
        
        resultado = []
        for chat in all_chats:
            try:
                chat_data = chat.to_dict()
                print(f"📝 Procesando chat {chat.id}: {chat_data}")
                
                # Obtener mensajes del chat
                messages_ref = chat.reference.collection('messages')
                messages = list(messages_ref.stream())
                
                mensajes = []
                for msg in messages:
                    msg_data = msg.to_dict()
                    mensajes.append({
                        'id': msg.id,
                        'sender': msg_data['sender'],
                        'text': msg_data['text'],
                        'timestamp': msg_data['timestamp'].isoformat() if msg_data['timestamp'] else None
                    })
                
                # Determinar la fecha de creación
                created_at = chat_data.get('created_at')
                if not created_at:
                    created_at = chat_data.get('timestamp', datetime.now())
                
                # Asegurar que created_at sea un datetime
                if not isinstance(created_at, datetime):
                    created_at = datetime.now()
                
                # Incluir el chat si tiene mensajes o es reciente
                # Convertir created_at a datetime naive si es necesario
                if hasattr(created_at, 'replace'):
                    created_at_naive = created_at.replace(tzinfo=None)
                else:
                    created_at_naive = created_at
                
                is_recent = (datetime.now() - created_at_naive).total_seconds() < 3600
                print(f"📅 Chat {chat.id}: created_at={created_at_naive}, is_recent={is_recent}, mensajes={len(mensajes)}")
                
                if mensajes or is_recent:
                    resultado.append({
                        'chat_id': chat.id,
                        'created_at': created_at.isoformat(),
                        'mensajes': mensajes,
                        'message_count': len(mensajes)
                    })
                    print(f"✅ Chat {chat.id} agregado con {len(mensajes)} mensajes")
                
            except Exception as chat_error:
                print(f"❌ Error procesando chat {chat.id}: {chat_error}")
                continue
        
        # Ordenar por fecha de creación (más reciente primero)
        resultado.sort(key=lambda x: x['created_at'], reverse=True)
        resultado = resultado[:5]  # Limitar a 5 chats
        
        print(f"✅ Historial obtenido: {len(resultado)} chats")
        return jsonify({'chats': resultado}), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo historial: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error obteniendo historial: {str(e)}'}), 500

@app.route('/delete_history', methods=['POST'])
@require_auth
def delete_history():
    user_id = request.user['uid']
    
    try:
        # Eliminar todos los chats del usuario
        chats_ref = db.collection('chats').document(user_id).collection('conversations')
        chats = chats_ref.stream()
        
        for chat in chats:
            # Eliminar todos los mensajes del chat
            messages = chat.reference.collection('messages').stream()
            for msg in messages:
                msg.reference.delete()
            # Eliminar el chat
            chat.reference.delete()
        
        return jsonify({'message': 'Historial eliminado'}), 200
        
    except Exception as e:
        print(f"Error eliminando historial: {e}")
        return jsonify({'error': 'Error eliminando historial'}), 500

@app.route('/delete_chat', methods=['POST'])
@require_auth
def delete_chat():
    data = request.get_json()
    chat_id = data.get('chat_id')
    
    if not chat_id:
        return jsonify({'error': 'chat_id requerido'}), 400

    user_id = request.user['uid']
    
    try:
        chat_ref = db.collection('chats').document(user_id).collection('conversations').document(chat_id)
        
        if not chat_ref.get().exists:
            return jsonify({'error': 'Chat no encontrado'}), 404

        # Eliminar todos los mensajes del chat
        messages = chat_ref.collection('messages').stream()
        for msg in messages:
            msg.reference.delete()
        
        # Eliminar el chat
        chat_ref.delete()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Error eliminando chat: {e}")
        return jsonify({'error': 'Error eliminando chat'}), 500

@app.route('/user/role', methods=['GET'])
@require_auth
def get_user_role_endpoint():
    user_id = request.user['uid']
    role = get_user_role(user_id)
    return jsonify({'role': role}), 200

@app.route('/user/profile', methods=['GET'])
@require_auth
def get_user_profile():
    """Obtener el perfil completo del usuario"""
    try:
        user_id = request.user['uid']
        user_doc = db.collection('users').document(user_id).get()
        
        if not user_doc.exists:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        user_data = user_doc.to_dict()
        return jsonify({
            'nombre': user_data.get('nombre', ''),
            'apellido': user_data.get('apellido', ''),
            'pais': user_data.get('pais', ''),
            'email': user_data.get('email', ''),
            'rol': user_data.get('rol', 'free'),
            'fechaCreacion': user_data.get('fechaCreacion', ''),
            'fechaActualizacion': user_data.get('fechaActualizacion', '')
        }), 200
        
    except Exception as e:
        print(f"Error obteniendo perfil: {e}")
        return jsonify({'error': 'Error obteniendo perfil'}), 500

@app.route('/user/profile', methods=['PUT'])
@require_auth
def update_user_profile():
    """Actualizar el perfil del usuario"""
    try:
        user_id = request.user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        # Validar campos requeridos
        required_fields = ['nombre', 'apellido', 'pais']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({'error': f'El campo {field} es requerido'}), 400
        
        # Preparar datos para actualizar
        update_data = {
            'nombre': data['nombre'].strip(),
            'apellido': data['apellido'].strip(),
            'pais': data['pais'].strip(),
            'fechaActualizacion': datetime.now()
        }
        
        # Actualizar en Firestore
        db.collection('users').document(user_id).update(update_data)
        
        return jsonify({
            'message': 'Perfil actualizado correctamente',
            'profile': update_data
        }), 200
        
    except Exception as e:
        print(f"Error actualizando perfil: {e}")
        return jsonify({'error': 'Error actualizando perfil'}), 500

@app.route('/analyze-chart', methods=['POST'])
@require_auth
def analyze_chart():
    """
    Endpoint para análisis de imágenes de gráficos de trading
    """
    data = request.get_json()
    image_url = data.get('image_url', '')
    prompt = data.get('prompt', '')
    
    if not image_url:
        return jsonify({'error': 'URL de imagen requerida'}), 400

    user_id = request.user['uid']
    user_role = get_user_role(user_id)
    
    # Verificar si el usuario es premium
    if user_role != 'premium':
        return jsonify({'error': 'Se requiere cuenta premium para análisis de gráficos'}), 403

    try:
        from services.chat import analyze_chart_image
        analysis = analyze_chart_image(image_url, prompt)
        
        return jsonify({
            'analysis': analysis,
            'image_url': image_url,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Error al analizar el gráfico: {str(e)}'}), 500

@app.route('/user/change-password', methods=['POST'])
@require_auth
def change_password():
    """Cambiar la contraseña del usuario"""
    try:
        user_id = request.user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Contraseña actual y nueva contraseña son requeridas'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'La nueva contraseña debe tener al menos 6 caracteres'}), 400
        
        try:
            from firebase_admin import auth
            # Cambiar contraseña en Firebase Auth
            auth.update_user(
                user_id,
                password=new_password
            )
            
            # Actualizar fecha de actualización en Firestore
            db.collection('users').document(user_id).update({
                'fechaActualizacion': datetime.now()
            })
            
            return jsonify({
                'message': 'Contraseña actualizada correctamente'
            }), 200
            
        except Exception as e:
            print(f"Error cambiando contraseña: {e}")
            return jsonify({'error': 'Error al cambiar la contraseña. Verifica que la contraseña actual sea correcta.'}), 400
        
    except Exception as e:
        print(f"Error en change_password: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/test/create-user', methods=['POST'])
def create_test_user():
    """Endpoint para crear un usuario de prueba"""
    try:
        from firebase_admin import auth
        data = request.get_json()
        email = data.get('email', 'test@example.com')
        password = data.get('password', '123456')
        
        # Crear usuario en Firebase Auth
        user_record = auth.create_user(
            email=email,
            password=password
        )
        
        # Crear documento en Firestore
        create_user_document(user_record.uid, {'email': email})
        
        return jsonify({
            'success': True,
            'user_id': user_record.uid,
            'email': email,
            'message': 'Usuario creado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/test/verify-config', methods=['GET'])
def verify_config():
    """Endpoint para verificar la configuración de Firebase"""
    try:
        from firebase_admin import auth
        # Intentar listar usuarios (esto verifica la configuración)
        users = auth.list_users()
        return jsonify({
            'success': True,
            'message': 'Configuración de Firebase correcta',
            'user_count': len(users.users)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/test/firestore', methods=['GET'])
def test_firestore():
    """Endpoint para verificar que Firestore funciona"""
    try:
        # Intentar hacer una operación simple en Firestore
        test_ref = db.collection('test').document('test')
        test_ref.set({'test': 'data', 'timestamp': datetime.now()})
        test_data = test_ref.get().to_dict()
        test_ref.delete()  # Limpiar
        
        return jsonify({
            'success': True,
            'message': 'Firestore funciona correctamente',
            'test_data': test_data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def limit_chats(user_id):
    """Limita a 5 chats por usuario, eliminando los más antiguos"""
    try:
        chats_ref = db.collection('chats').document(user_id).collection('conversations')
        
        # Intentar ordenar por created_at, si falla usar timestamp
        try:
            chats = chats_ref.order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        except:
            # Fallback para chats antiguos
            chats = chats_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
        
        chat_list = list(chats)
        if len(chat_list) > 5:
            # Eliminar chats más antiguos
            for chat in chat_list[5:]:
                # Eliminar mensajes
                messages = chat.reference.collection('messages').stream()
                for msg in messages:
                    msg.reference.delete()
                # Eliminar chat
                chat.reference.delete()
        
        # Limpiar chats vacíos antiguos (más de 1 hora sin mensajes)
        clean_empty_chats(user_id)
    except Exception as e:
        print(f"Error limitando chats: {e}")

def clean_empty_chats(user_id):
    """Elimina chats vacíos que tienen más de 1 hora sin mensajes"""
    try:
        chats_ref = db.collection('chats').document(user_id).collection('conversations')
        chats = chats_ref.stream()
        
        for chat in chats:
            chat_data = chat.to_dict()
            created_at = chat_data.get('created_at', datetime.now())
            
            # Asegurar que created_at sea un datetime
            if not isinstance(created_at, datetime):
                created_at = datetime.now()
            
            # Verificar si el chat tiene mensajes
            messages = chat.reference.collection('messages').limit(1).stream()
            has_messages = len(list(messages)) > 0
            
            # Si no tiene mensajes y es más antiguo que 1 hora, eliminarlo
            # Convertir created_at a datetime naive si es necesario
            if hasattr(created_at, 'replace'):
                created_at_naive = created_at.replace(tzinfo=None)
            else:
                created_at_naive = created_at
                
            if not has_messages and (datetime.now() - created_at_naive).total_seconds() > 3600:
                chat.reference.delete()
                print(f"Chat vacío eliminado: {chat.id}")
                
    except Exception as e:
        print(f"Error limpiando chats vacíos: {e}")

# Registrar blueprints
from routes.chat import init_app as init_chat_routes
init_chat_routes(app)

if __name__ == '__main__':
    app.run(debug=True)


