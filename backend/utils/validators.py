from marshmallow import Schema, fields, ValidationError, validate
from datetime import datetime

class ChatMessageSchema(Schema):
    """Esquema de validación para mensajes de chat"""
    message = fields.Str(
        required=True, 
        validate=[
            validate.Length(min=1, max=2000, error="El mensaje debe tener entre 1 y 2000 caracteres"),
            validate.Regexp(r'^[^\x00-\x08\x0B\x0C\x0E-\x1F\x7F]+$', error="El mensaje contiene caracteres no válidos")
        ]
    )
    chat_id = fields.Str(required=False, allow_none=True)

class CreateChatSchema(Schema):
    """Esquema de validación para crear chats"""
    # No requiere campos específicos, pero valida que no haya campos extraños
    pass

class DeleteChatSchema(Schema):
    """Esquema de validación para eliminar chats"""
    chat_id = fields.Str(required=True, validate=validate.Length(min=1))

class UserProfileSchema(Schema):
    """Esquema de validación para perfiles de usuario"""
    nombre = fields.Str(validate=validate.Length(max=50))
    apellido = fields.Str(validate=validate.Length(max=50))
    pais = fields.Str(validate=validate.Length(max=50))
    fechaAlta = fields.DateTime(allow_none=True)

class ChangePasswordSchema(Schema):
    """Esquema de validación para cambio de contraseña"""
    current_password = fields.Str(required=True, validate=validate.Length(min=6))
    new_password = fields.Str(
        required=True, 
        validate=[
            validate.Length(min=6, error="La nueva contraseña debe tener al menos 6 caracteres"),
            validate.Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)', 
                error="La contraseña debe contener al menos una minúscula, una mayúscula y un número"
            )
        ]
    )

class ChartAnalysisSchema(Schema):
    """Esquema de validación para análisis de gráficos"""
    image_url = fields.Str(required=True, validate=validate.URL())
    analysis_type = fields.Str(validate=validate.OneOf(['technical', 'fundamental', 'both']))

def validate_request_data(schema_class, data):
    """
    Valida los datos de request usando un esquema específico
    
    Args:
        schema_class: Clase del esquema de validación
        data: Datos a validar
    
    Returns:
        dict: Datos validados y limpios
    
    Raises:
        ValidationError: Si los datos no son válidos
    """
    try:
        schema = schema_class()
        validated_data = schema.load(data)
        return validated_data
    except ValidationError as e:
        raise ValidationError(f"Datos inválidos: {e.messages}")

def sanitize_string(text):
    """
    Sanitiza una cadena de texto removiendo caracteres peligrosos
    
    Args:
        text (str): Texto a sanitizar
    
    Returns:
        str: Texto sanitizado
    """
    if not text:
        return text
    
    # Remover caracteres de control excepto tab y newline
    import re
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Limitar longitud
    if len(text) > 2000:
        text = text[:2000]
    
    return text.strip()

def validate_email(email):
    """
    Valida formato de email
    
    Args:
        email (str): Email a validar
    
    Returns:
        bool: True si es válido
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_user_id(user_id):
    """
    Valida formato de user_id de Firebase
    
    Args:
        user_id (str): User ID a validar
    
    Returns:
        bool: True si es válido
    """
    if not user_id:
        return False
    
    # Firebase UIDs tienen 28 caracteres alfanuméricos
    import re
    pattern = r'^[a-zA-Z0-9]{28}$'
    return bool(re.match(pattern, user_id)) 