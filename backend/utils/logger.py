import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger(name='mentor_forex'):
    """
    Configura un logger profesional con rotación de archivos
    """
    # Crear directorio de logs si no existe
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar el logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    # Formato de los logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo con rotación (máximo 10MB por archivo, 5 archivos)
    file_handler = RotatingFileHandler(
        f'{log_dir}/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Agregar handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Logger principal de la aplicación
logger = setup_logger()

# Loggers específicos para diferentes módulos
def get_module_logger(module_name):
    """
    Obtiene un logger específico para un módulo
    """
    return logging.getLogger(f'mentor_forex.{module_name}')

# Funciones helper para logging estructurado
def log_request(request_type, endpoint, user_id=None, status_code=None, error=None):
    """
    Log estructurado para requests
    """
    log_data = {
        'type': request_type,
        'endpoint': endpoint,
        'user_id': user_id,
        'status_code': status_code,
        'timestamp': datetime.now().isoformat()
    }
    
    if error:
        log_data['error'] = str(error)
        logger.error(f"Request failed: {log_data}")
    else:
        logger.info(f"Request successful: {log_data}")

def log_auth_event(event_type, user_id, email=None, success=True, error=None):
    """
    Log estructurado para eventos de autenticación
    """
    log_data = {
        'event': event_type,
        'user_id': user_id,
        'email': email,
        'success': success,
        'timestamp': datetime.now().isoformat()
    }
    
    if error:
        log_data['error'] = str(error)
        logger.error(f"Auth event failed: {log_data}")
    else:
        logger.info(f"Auth event: {log_data}")

def log_chat_event(event_type, user_id, chat_id=None, message_length=None, error=None):
    """
    Log estructurado para eventos de chat
    """
    log_data = {
        'event': event_type,
        'user_id': user_id,
        'chat_id': chat_id,
        'message_length': message_length,
        'timestamp': datetime.now().isoformat()
    }
    
    if error:
        log_data['error'] = str(error)
        logger.error(f"Chat event failed: {log_data}")
    else:
        logger.info(f"Chat event: {log_data}") 