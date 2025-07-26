import os
import firebase_admin
from firebase_admin import credentials, auth, firestore
from dotenv import load_dotenv

load_dotenv()

# Verificar que las variables de entorno estén cargadas
print("🔧 Configurando Firebase Admin...")
print(f"🔧 Project ID: {os.getenv('FIREBASE_PROJECT_ID')}")
print(f"🔧 Client Email: {os.getenv('FIREBASE_CLIENT_EMAIL')}")

# Configurar credenciales de Firebase Admin
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
    "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
    "auth_uri": os.getenv('FIREBASE_AUTH_URI'),
    "token_uri": os.getenv('FIREBASE_TOKEN_URI'),
    "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL')
})

# Inicializar Firebase Admin
try:
    firebase_admin.initialize_app(cred)
    print("✅ Firebase Admin inicializado correctamente")
except ValueError:
    print("⚠️ Firebase Admin ya inicializado")

# Obtener instancia de Firestore
db = firestore.client()

def verify_firebase_token(id_token):
    """Verifica el token de Firebase y retorna el usuario"""
    try:
        print(f"🔍 Verificando token: {id_token[:20]}...")
        # Agregar tolerancia de tiempo para manejar desincronización del reloj
        decoded_token = auth.verify_id_token(id_token, check_revoked=False)
        print(f"✅ Token válido para: {decoded_token.get('email', 'N/A')}")
        return decoded_token
    except Exception as e:
        print(f"❌ Error verificando token: {e}")
        # Si es error de tiempo, intentar con tolerancia
        if "used too early" in str(e) or "clock" in str(e).lower():
            try:
                print("🕐 Intentando con tolerancia de tiempo...")
                import time
                # Esperar un momento y reintentar
                time.sleep(2)
                decoded_token = auth.verify_id_token(id_token, check_revoked=False)
                print(f"✅ Token válido (con tolerancia): {decoded_token.get('email', 'N/A')}")
                return decoded_token
            except Exception as e2:
                print(f"❌ Error incluso con tolerancia: {e2}")
        return None

def get_user_role(uid):
    """Obtiene el rol del usuario desde Firestore"""
    try:
        print(f"🔍 Obteniendo rol para usuario: {uid}")
        user_doc = db.collection('users').document(uid).get()
        if user_doc.exists:
            role = user_doc.to_dict().get('rol', 'free')
            print(f"✅ Rol encontrado: {role}")
            return role
        print(f"⚠️ Usuario no encontrado, rol por defecto: free")
        return 'free'
    except Exception as e:
        print(f"❌ Error obteniendo rol: {e}")
        return 'free'

def create_user_document(uid, user_data):
    """Crea el documento del usuario en Firestore"""
    try:
        user_ref = db.collection('users').document(uid)
        user_ref.set({
            'email': user_data.get('email'),
            'nombre': user_data.get('nombre', ''),
            'apellido': user_data.get('apellido', ''),
            'pais': user_data.get('pais', ''),
            'fechaAlta': firestore.SERVER_TIMESTAMP,
            'rol': 'free'  # Por defecto free
        })
        print(f"✅ Usuario creado en Firestore: {uid}")
        return True
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        return False 