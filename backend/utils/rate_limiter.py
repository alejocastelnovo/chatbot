from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from flask import request, jsonify
import time

# Configuración de rate limiting
RATE_LIMITS = {
    'default': '200 per day, 50 per hour',
    'chat': '10 per minute',  # Chat más restrictivo
    'auth': '5 per minute',   # Autenticación muy restrictiva
    'history': '30 per minute', # Historial moderado
    'upload': '5 per minute'   # Uploads restrictivos
}

def create_limiter(app):
    """
    Crea y configura el rate limiter
    """
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[RATE_LIMITS['default']],
        storage_uri="memory://",  # En producción usar Redis
        strategy="fixed-window"
    )
    return limiter

def rate_limit_by_user(f):
    """
    Decorador para rate limiting basado en usuario autenticado
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtener user_id del request si está disponible
        user_id = getattr(request, 'user', {}).get('uid', None)
        
        if user_id:
            # Rate limit específico por usuario
            key = f"user:{user_id}"
        else:
            # Rate limit por IP
            key = get_remote_address()
        
        # Verificar límites
        limit_key = f"{key}:{f.__name__}"
        current_time = time.time()
        
        # Implementación simple de rate limiting
        # En producción usar Redis o similar
        if not hasattr(request, '_rate_limit_data'):
            request._rate_limit_data = {}
        
        if limit_key in request._rate_limit_data:
            last_request, count = request._rate_limit_data[limit_key]
            
            # Reset contador si pasó 1 minuto
            if current_time - last_request > 60:
                request._rate_limit_data[limit_key] = (current_time, 1)
            else:
                # Verificar límite (10 requests por minuto)
                if count >= 10:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'message': 'Demasiadas requests. Intenta en 1 minuto.'
                    }), 429
                
                request._rate_limit_data[limit_key] = (current_time, count + 1)
        else:
            request._rate_limit_data[limit_key] = (current_time, 1)
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_rate_limit_config(endpoint_type):
    """
    Obtiene la configuración de rate limit para un tipo de endpoint
    """
    return RATE_LIMITS.get(endpoint_type, RATE_LIMITS['default'])

# Decoradores específicos para diferentes tipos de endpoints
def chat_rate_limit(f):
    """Rate limit específico para endpoints de chat"""
    return rate_limit_by_user(f)

def auth_rate_limit(f):
    """Rate limit específico para endpoints de autenticación"""
    return rate_limit_by_user(f)

def history_rate_limit(f):
    """Rate limit específico para endpoints de historial"""
    return rate_limit_by_user(f) 