import React, { useState, useEffect } from 'react';
import { auth } from '../firebase';

function Profile({ onClose }) {
    const [userData, setUserData] = useState({
        nombre: '',
        apellido: '',
        pais: '',
        email: '',
        rol: 'free'
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [validationErrors, setValidationErrors] = useState({});
    const [showPasswordModal, setShowPasswordModal] = useState(false);
    const [passwordData, setPasswordData] = useState({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    });
    const [changingPassword, setChangingPassword] = useState(false);
    const [passwordError, setPasswordError] = useState('');
    const [passwordSuccess, setPasswordSuccess] = useState('');
    const [editingFields, setEditingFields] = useState({
        nombre: false,
        apellido: false,
        pais: false
    });
    const [originalData, setOriginalData] = useState({
        nombre: '',
        apellido: '',
        pais: ''
    });

    useEffect(() => {
        loadUserData();
    }, []);

    const loadUserData = async () => {
        try {
            const token = await auth.currentUser.getIdToken();
            const response = await fetch('/api/user/profile', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setUserData({
                    nombre: data.nombre || '',
                    apellido: data.apellido || '',
                    pais: data.pais || '',
                    email: data.email || auth.currentUser.email || '',
                    rol: data.rol || 'free'
                });
                setOriginalData({
                    nombre: data.nombre || '',
                    apellido: data.apellido || '',
                    pais: data.pais || ''
                });
            } else {
                const errorData = await response.json();
                setError(errorData.error || 'Error al cargar los datos del usuario');
            }
        } catch (err) {
            console.error('Error cargando datos del usuario:', err);
            setError('Error de conexión al cargar los datos del usuario');
        } finally {
            setLoading(false);
        }
    };

    const validateForm = () => {
        const errors = {};
        
        if (!userData.nombre.trim()) {
            errors.nombre = 'El nombre es requerido';
        } else if (userData.nombre.trim().length < 2) {
            errors.nombre = 'El nombre debe tener al menos 2 caracteres';
        }
        
        if (!userData.apellido.trim()) {
            errors.apellido = 'El apellido es requerido';
        } else if (userData.apellido.trim().length < 2) {
            errors.apellido = 'El apellido debe tener al menos 2 caracteres';
        }
        
        if (!userData.pais.trim()) {
            errors.pais = 'El país es requerido';
        } else if (userData.pais.trim().length < 2) {
            errors.pais = 'El país debe tener al menos 2 caracteres';
        }
        
        setValidationErrors(errors);
        return Object.keys(errors).length === 0;
    };

    const handleSave = async (e) => {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }
        
        setSaving(true);
        setError('');
        setSuccess('');

        try {
            const token = await auth.currentUser.getIdToken();
            const response = await fetch('/api/user/profile', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    nombre: userData.nombre.trim(),
                    apellido: userData.apellido.trim(),
                    pais: userData.pais.trim()
                })
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess(data.message || 'Perfil actualizado correctamente');
                // Limpiar errores de validación
                setValidationErrors({});
                setOriginalData(userData); // Actualizar datos originales
            } else {
                setError(data.error || 'Error al actualizar el perfil');
            }
        } catch (err) {
            console.error('Error actualizando perfil:', err);
            setError('Error de conexión al actualizar el perfil');
        } finally {
            setSaving(false);
        }
    };

    const handleInputChange = (field, value) => {
        setUserData(prev => ({
            ...prev,
            [field]: value
        }));
        
        // Limpiar error de validación del campo cuando el usuario empiece a escribir
        if (validationErrors[field]) {
            setValidationErrors(prev => ({
                ...prev,
                [field]: ''
            }));
        }
    };

    const getInputStyle = (field) => {
        const baseStyle = {
            width: '100%',
            padding: 12,
            borderRadius: 8,
            border: '1px solid #343541',
            background: '#23272f',
            color: '#fff',
            fontSize: 16
        };
        
        if (validationErrors[field]) {
            return {
                ...baseStyle,
                border: '1px solid #ff6b6b',
                boxShadow: '0 0 0 1px #ff6b6b'
            };
        }
        
        return baseStyle;
    };

    const handleFieldClick = (field) => {
        setEditingFields(prev => ({
            ...prev,
            [field]: true
        }));
    };

    const handleFieldSave = async (field) => {
        // Validar el campo específico
        const errors = {};
        if (!userData[field].trim()) {
            errors[field] = `El campo ${field} es requerido`;
        } else if (userData[field].trim().length < 2) {
            errors[field] = `El campo ${field} debe tener al menos 2 caracteres`;
        }
        
        if (Object.keys(errors).length > 0) {
            setValidationErrors(errors);
            return;
        }

        setSaving(true);
        setError('');
        setSuccess('');

        try {
            const token = await auth.currentUser.getIdToken();
            const response = await fetch('/api/user/profile', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    nombre: userData.nombre.trim(),
                    apellido: userData.apellido.trim(),
                    pais: userData.pais.trim()
                })
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess(data.message || 'Campo actualizado correctamente');
                setEditingFields(prev => ({
                    ...prev,
                    [field]: false
                }));
                setOriginalData(prev => ({
                    ...prev,
                    [field]: userData[field].trim()
                }));
                setValidationErrors({});
            } else {
                setError(data.error || 'Error al actualizar el campo');
            }
        } catch (err) {
            console.error('Error actualizando campo:', err);
            setError('Error de conexión al actualizar el campo');
        } finally {
            setSaving(false);
        }
    };

    const handleFieldCancel = (field) => {
        setEditingFields(prev => ({
            ...prev,
            [field]: false
        }));
        // Restaurar valor original
        setUserData(prev => ({
            ...prev,
            [field]: originalData[field]
        }));
        // Limpiar error de validación
        setValidationErrors(prev => ({
            ...prev,
            [field]: ''
        }));
    };

    const handleFieldKeyPress = (e, field) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleFieldSave(field);
        } else if (e.key === 'Escape') {
            e.preventDefault();
            handleFieldCancel(field);
        }
    };

    const EditableField = ({ field, label, placeholder, value, onChange, isEditing, onSave, onCancel, onKeyPress, error, disabled = false }) => {
        const fieldLabels = {
            nombre: 'Nombre',
            apellido: 'Apellido',
            pais: 'País'
        };

        if (isEditing) {
            return (
                <div style={{ marginBottom: 20 }}>
                    <label style={{ display: 'block', color: '#fff', marginBottom: 8, fontWeight: 500 }}>
                        {fieldLabels[field]}
                    </label>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                        <input
                            type="text"
                            value={value}
                            onChange={onChange}
                            onKeyPress={onKeyPress}
                            style={{
                                flex: 1,
                                padding: 12,
                                borderRadius: 8,
                                border: error ? '1px solid #ff6b6b' : '1px solid #1ee87a',
                                background: '#23272f',
                                color: '#fff',
                                fontSize: 16,
                                boxShadow: error ? '0 0 0 1px #ff6b6b' : '0 0 0 1px #1ee87a'
                            }}
                            placeholder={placeholder}
                            autoFocus
                        />
                        <button
                            type="button"
                            onClick={() => onSave(field)}
                            disabled={saving}
                            style={{
                                padding: '8px 12px',
                                borderRadius: 6,
                                border: 'none',
                                background: saving ? '#666' : '#1ee87a',
                                color: saving ? '#999' : '#000',
                                fontSize: 14,
                                cursor: saving ? 'not-allowed' : 'pointer',
                                fontWeight: 'bold'
                            }}
                        >
                            {saving ? '...' : '✓'}
                        </button>
                        <button
                            type="button"
                            onClick={() => onCancel(field)}
                            disabled={saving}
                            style={{
                                padding: '8px 12px',
                                borderRadius: 6,
                                border: '1px solid #666',
                                background: 'transparent',
                                color: '#666',
                                fontSize: 14,
                                cursor: saving ? 'not-allowed' : 'pointer'
                            }}
                        >
                            ✕
                        </button>
                    </div>
                    {error && (
                        <p style={{ color: '#ff6b6b', fontSize: 12, marginTop: 4 }}>{error}</p>
                    )}
                </div>
            );
        }

        return (
            <div style={{ marginBottom: 20 }}>
                <label style={{ display: 'block', color: '#fff', marginBottom: 8, fontWeight: 500 }}>
                    {fieldLabels[field]}
                </label>
                <div
                    onClick={() => !disabled && handleFieldClick(field)}
                    style={{
                        width: '100%',
                        padding: 12,
                        borderRadius: 8,
                        border: '1px solid #343541',
                        background: disabled ? '#444654' : '#23272f',
                        color: disabled ? '#666' : '#fff',
                        fontSize: 16,
                        cursor: disabled ? 'not-allowed' : 'pointer',
                        transition: 'all 0.2s ease',
                        position: 'relative'
                    }}
                    onMouseEnter={(e) => {
                        if (!disabled) {
                            e.target.style.border = '1px solid #1ee87a';
                            e.target.style.background = '#2a2f3a';
                        }
                    }}
                    onMouseLeave={(e) => {
                        if (!disabled) {
                            e.target.style.border = '1px solid #343541';
                            e.target.style.background = '#23272f';
                        }
                    }}
                >
                    {value || placeholder}
                    {!disabled && (
                        <span style={{
                            position: 'absolute',
                            right: 12,
                            top: '50%',
                            transform: 'translateY(-50%)',
                            color: '#666',
                            fontSize: 14
                        }}>
                            ✏️
                        </span>
                    )}
                </div>
                {disabled && (
                    <small style={{ color: '#666', fontSize: 12 }}>
                        Este campo no se puede modificar
                    </small>
                )}
            </div>
        );
    };

    const handlePasswordChange = async (e) => {
        e.preventDefault();
        
        // Validar contraseñas
        if (passwordData.newPassword !== passwordData.confirmPassword) {
            setPasswordError('Las contraseñas no coinciden');
            return;
        }
        
        if (passwordData.newPassword.length < 6) {
            setPasswordError('La nueva contraseña debe tener al menos 6 caracteres');
            return;
        }
        
        setChangingPassword(true);
        setPasswordError('');
        setPasswordSuccess('');

        try {
            const token = await auth.currentUser.getIdToken();
            const response = await fetch('/api/user/change-password', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    currentPassword: passwordData.currentPassword,
                    newPassword: passwordData.newPassword
                })
            });

            const data = await response.json();

            if (response.ok) {
                setPasswordSuccess(data.message || 'Contraseña actualizada correctamente');
                setPasswordData({
                    currentPassword: '',
                    newPassword: '',
                    confirmPassword: ''
                });
                // Cerrar modal después de 2 segundos
                setTimeout(() => {
                    setShowPasswordModal(false);
                    setPasswordSuccess('');
                }, 2000);
            } else {
                setPasswordError(data.error || 'Error al cambiar la contraseña');
            }
        } catch (err) {
            console.error('Error cambiando contraseña:', err);
            setPasswordError('Error de conexión al cambiar la contraseña');
        } finally {
            setChangingPassword(false);
        }
    };

    const PasswordModal = () => {
        if (!showPasswordModal) return null;

        return (
            <div style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'rgba(0,0,0,0.9)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 2000
            }}>
                <div style={{
                    background: '#23272f',
                    borderRadius: 16,
                    padding: 32,
                    width: '90%',
                    maxWidth: 400,
                    border: '1px solid #343541'
                }}>
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: 24,
                        borderBottom: '1px solid #343541',
                        paddingBottom: 16
                    }}>
                        <h3 style={{ margin: 0, color: '#fff', fontSize: 20, fontWeight: 700 }}>
                            🔒 Cambiar Contraseña
                        </h3>
                        <button
                            onClick={() => setShowPasswordModal(false)}
                            style={{
                                background: 'transparent',
                                border: 'none',
                                color: '#666',
                                fontSize: 24,
                                cursor: 'pointer',
                                padding: 4
                            }}
                        >
                            ×
                        </button>
                    </div>

                    <form onSubmit={handlePasswordChange}>
                        <div style={{ marginBottom: 20 }}>
                            <label style={{ display: 'block', color: '#fff', marginBottom: 8, fontWeight: 500 }}>
                                Contraseña Actual
                            </label>
                            <input
                                type="password"
                                value={passwordData.currentPassword}
                                onChange={(e) => setPasswordData(prev => ({...prev, currentPassword: e.target.value}))}
                                style={{
                                    width: '100%',
                                    padding: 12,
                                    borderRadius: 8,
                                    border: '1px solid #343541',
                                    background: '#23272f',
                                    color: '#fff',
                                    fontSize: 16
                                }}
                                placeholder="Tu contraseña actual"
                                required
                            />
                        </div>

                        <div style={{ marginBottom: 20 }}>
                            <label style={{ display: 'block', color: '#fff', marginBottom: 8, fontWeight: 500 }}>
                                Nueva Contraseña
                            </label>
                            <input
                                type="password"
                                value={passwordData.newPassword}
                                onChange={(e) => setPasswordData(prev => ({...prev, newPassword: e.target.value}))}
                                style={{
                                    width: '100%',
                                    padding: 12,
                                    borderRadius: 8,
                                    border: '1px solid #343541',
                                    background: '#23272f',
                                    color: '#fff',
                                    fontSize: 16
                                }}
                                placeholder="Nueva contraseña (mín. 6 caracteres)"
                                required
                            />
                        </div>

                        <div style={{ marginBottom: 24 }}>
                            <label style={{ display: 'block', color: '#fff', marginBottom: 8, fontWeight: 500 }}>
                                Confirmar Nueva Contraseña
                            </label>
                            <input
                                type="password"
                                value={passwordData.confirmPassword}
                                onChange={(e) => setPasswordData(prev => ({...prev, confirmPassword: e.target.value}))}
                                style={{
                                    width: '100%',
                                    padding: 12,
                                    borderRadius: 8,
                                    border: '1px solid #343541',
                                    background: '#23272f',
                                    color: '#fff',
                                    fontSize: 16
                                }}
                                placeholder="Confirma la nueva contraseña"
                                required
                            />
                        </div>

                        {passwordError && (
                            <div style={{
                                background: '#ff6b6b',
                                color: '#fff',
                                padding: 12,
                                borderRadius: 8,
                                marginBottom: 16,
                                fontSize: 14
                            }}>
                                {passwordError}
                            </div>
                        )}

                        {passwordSuccess && (
                            <div style={{
                                background: '#1ee87a',
                                color: '#000',
                                padding: 12,
                                borderRadius: 8,
                                marginBottom: 16,
                                fontSize: 14
                            }}>
                                {passwordSuccess}
                            </div>
                        )}

                        <div style={{
                            display: 'flex',
                            gap: 12,
                            justifyContent: 'flex-end'
                        }}>
                            <button
                                type="button"
                                onClick={() => setShowPasswordModal(false)}
                                style={{
                                    padding: '12px 24px',
                                    borderRadius: 8,
                                    border: '1px solid #343541',
                                    background: 'transparent',
                                    color: '#fff',
                                    fontSize: 16,
                                    cursor: 'pointer'
                                }}
                            >
                                Cancelar
                            </button>
                            <button
                                type="submit"
                                disabled={changingPassword}
                                style={{
                                    padding: '12px 24px',
                                    borderRadius: 8,
                                    border: 'none',
                                    background: changingPassword ? '#666' : '#1ee87a',
                                    color: changingPassword ? '#999' : '#000',
                                    fontSize: 16,
                                    fontWeight: 'bold',
                                    cursor: changingPassword ? 'not-allowed' : 'pointer'
                                }}
                            >
                                {changingPassword ? 'Cambiando...' : 'Cambiar Contraseña'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        );
    };

    if (loading) {
        return (
            <div style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'rgba(0,0,0,0.8)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000
            }}>
                <div style={{ color: '#fff', fontSize: 18 }}>Cargando perfil...</div>
            </div>
        );
    }

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
        }}>
            <div style={{
                background: '#23272f',
                borderRadius: 16,
                padding: 32,
                width: '90%',
                maxWidth: 500,
                maxHeight: '90vh',
                overflowY: 'auto',
                border: '1px solid #343541'
            }}>
                {/* Header */}
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: 24,
                    borderBottom: '1px solid #343541',
                    paddingBottom: 16
                }}>
                    <h2 style={{ margin: 0, color: '#fff', fontSize: 24, fontWeight: 700 }}>
                        ⚙️ Configuración del Perfil
                    </h2>
                    <button
                        onClick={onClose}
                        style={{
                            background: 'transparent',
                            border: 'none',
                            color: '#666',
                            fontSize: 24,
                            cursor: 'pointer',
                            padding: 4
                        }}
                    >
                        ×
                    </button>
                </div>

                {/* Plan del usuario */}
                <div style={{
                    background: userData.rol === 'premium' ? '#1ee87a' : '#666',
                    color: userData.rol === 'premium' ? '#000' : '#fff',
                    padding: '12px 16px',
                    borderRadius: 12,
                    marginBottom: 24,
                    textAlign: 'center',
                    fontWeight: 'bold',
                    fontSize: 16
                }}>
                    Plan: {userData.rol === 'premium' ? 'Premium' : 'Free'}
                </div>

                {/* Instrucciones */}
                <div style={{
                    background: '#343541',
                    padding: 16,
                    borderRadius: 8,
                    marginBottom: 24,
                    border: '1px solid #1ee87a'
                }}>
                    <p style={{ color: '#fff', margin: '0 0 8px 0', fontSize: 14, fontWeight: 500 }}>
                        💡 <strong>¿Cómo editar?</strong>
                    </p>
                    <p style={{ color: '#ccc', margin: 0, fontSize: 13, lineHeight: 1.4 }}>
                        Haz clic en cualquier campo para editarlo. Usa <strong>Enter</strong> para guardar o <strong>Escape</strong> para cancelar.
                    </p>
                </div>

                {/* Formulario */}
                <form onSubmit={handleSave}>
                    <div style={{ marginBottom: 20 }}>
                        <label style={{ display: 'block', color: '#fff', marginBottom: 8, fontWeight: 500 }}>
                            Email
                        </label>
                        <input
                            type="email"
                            value={userData.email}
                            disabled
                            style={{
                                width: '100%',
                                padding: 12,
                                borderRadius: 8,
                                border: '1px solid #343541',
                                background: '#444654',
                                color: '#666',
                                fontSize: 16
                            }}
                        />
                        <small style={{ color: '#666', fontSize: 12 }}>
                            El email no se puede modificar
                        </small>
                    </div>

                    <EditableField
                        field="nombre"
                        label="Nombre"
                        placeholder="Tu nombre"
                        value={userData.nombre}
                        onChange={(e) => handleInputChange('nombre', e.target.value)}
                        isEditing={editingFields.nombre}
                        onSave={handleFieldSave}
                        onCancel={handleFieldCancel}
                        onKeyPress={(e) => handleFieldKeyPress(e, 'nombre')}
                                                 error={validationErrors.nombre}
                         disabled={false}
                     />

                     <EditableField
                         field="apellido"
                         label="Apellido"
                         placeholder="Tu apellido"
                         value={userData.apellido}
                         onChange={(e) => handleInputChange('apellido', e.target.value)}
                         isEditing={editingFields.apellido}
                         onSave={handleFieldSave}
                         onCancel={handleFieldCancel}
                         onKeyPress={(e) => handleFieldKeyPress(e, 'apellido')}
                         error={validationErrors.apellido}
                         disabled={false}
                     />

                     <EditableField
                         field="pais"
                         label="País"
                         placeholder="Tu país"
                         value={userData.pais}
                         onChange={(e) => handleInputChange('pais', e.target.value)}
                         isEditing={editingFields.pais}
                         onSave={handleFieldSave}
                         onCancel={handleFieldCancel}
                         onKeyPress={(e) => handleFieldKeyPress(e, 'pais')}
                         error={validationErrors.pais}
                         disabled={false}
                     />

                    {/* Sección de seguridad */}
                    <div style={{
                        borderTop: '1px solid #343541',
                        paddingTop: 24,
                        marginBottom: 24
                    }}>
                        <h3 style={{ color: '#fff', marginBottom: 16, fontSize: 18 }}>🔒 Seguridad</h3>
                        
                        <div style={{
                            background: '#343541',
                            padding: 16,
                            borderRadius: 8,
                            marginBottom: 16
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div>
                                    <h4 style={{ color: '#fff', margin: '0 0 4px 0', fontSize: 16 }}>Contraseña</h4>
                                    <p style={{ color: '#666', margin: 0, fontSize: 14 }}>
                                        Última actualización: {userData.fechaActualizacion ? new Date(userData.fechaActualizacion).toLocaleDateString('es-AR') : 'No disponible'}
                                    </p>
                                </div>
                                <button
                                    type="button"
                                    onClick={() => setShowPasswordModal(true)}
                                    style={{
                                        padding: '8px 16px',
                                        borderRadius: 6,
                                        border: '1px solid #1ee87a',
                                        background: 'transparent',
                                        color: '#1ee87a',
                                        fontSize: 14,
                                        cursor: 'pointer',
                                        fontWeight: 500
                                    }}
                                >
                                    Cambiar
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Mensajes de error y éxito */}
                    {error && (
                        <div style={{
                            background: '#ff6b6b',
                            color: '#fff',
                            padding: 12,
                            borderRadius: 8,
                            marginBottom: 16,
                            fontSize: 14
                        }}>
                            {error}
                        </div>
                    )}

                    {success && (
                        <div style={{
                            background: '#1ee87a',
                            color: '#000',
                            padding: 12,
                            borderRadius: 8,
                            marginBottom: 16,
                            fontSize: 14
                        }}>
                            {success}
                        </div>
                    )}

                    {/* Botones */}
                    <div style={{
                        display: 'flex',
                        gap: 12,
                        justifyContent: 'flex-end'
                    }}>
                        <button
                            type="button"
                            onClick={onClose}
                            style={{
                                padding: '12px 24px',
                                borderRadius: 8,
                                border: '1px solid #343541',
                                background: 'transparent',
                                color: '#fff',
                                fontSize: 16,
                                cursor: 'pointer'
                            }}
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            disabled={saving}
                            style={{
                                padding: '12px 24px',
                                borderRadius: 8,
                                border: 'none',
                                background: saving ? '#666' : '#1ee87a',
                                color: saving ? '#999' : '#000',
                                fontSize: 16,
                                fontWeight: 'bold',
                                cursor: saving ? 'not-allowed' : 'pointer'
                            }}
                        >
                            {saving ? 'Guardando...' : 'Guardar Cambios'}
                        </button>
                    </div>
                </form>
            </div>
            <PasswordModal />
        </div>
    );
}

export default Profile; 