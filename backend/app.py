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

        # Obtener respuesta de OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": user_message}]
        )
        bot_reply = response.choices[0].message.content

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
    
    try:
        # Obtener todos los chats del usuario
        chats_ref = db.collection('chats').document(user_id).collection('conversations')
        chats = chats_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5).stream()
        
        resultado = []
        for chat in chats:
            chat_data = chat.to_dict()
            messages_ref = chat.reference.collection('messages').order_by('timestamp', direction=firestore.Query.ASCENDING)
            messages = messages_ref.stream()
            
            mensajes = []
            for msg in messages:
                msg_data = msg.to_dict()
                mensajes.append({
                    'id': msg.id,
                    'sender': msg_data['sender'],
                    'text': msg_data['text'],
                    'timestamp': msg_data['timestamp'].isoformat() if msg_data['timestamp'] else None
                })
            
            resultado.append({
                'chat_id': chat.id,
                'created_at': chat_data.get('timestamp', datetime.now()).isoformat(),
                'mensajes': mensajes
            })
        
        return jsonify({'chats': resultado}), 200
        
    except Exception as e:
        print(f"Error obteniendo historial: {e}")
        return jsonify({'error': 'Error obteniendo historial'}), 500

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

def limit_chats(user_id):
    """Limita a 5 chats por usuario, eliminando los más antiguos"""
    try:
        chats_ref = db.collection('chats').document(user_id).collection('conversations')
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
    except Exception as e:
        print(f"Error limitando chats: {e}")

if __name__ == '__main__':
    app.run(debug=True)


