import React, { useState } from 'react';
import { createUserWithEmailAndPassword, signInWithEmailAndPassword } from 'firebase/auth';
import { doc, setDoc } from 'firebase/firestore';
import { auth, db } from '../firebase';
import optradingblanco from '../assets/optradingblanco.png';

function Login({ onLogin }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isRegistering, setIsRegistering] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            let userCredential;
            
            if (isRegistering) {
                // Registrar nuevo usuario
                userCredential = await createUserWithEmailAndPassword(auth, email, password);
                
                // Crear documento del usuario en Firestore
                await setDoc(doc(db, 'users', userCredential.user.uid), {
                    email: email,
                    nombre: '',
                    apellido: '',
                    pais: '',
                    fechaAlta: new Date(),
                    rol: 'free' // Por defecto free
                });
            } else {
                // Iniciar sesión
                userCredential = await signInWithEmailAndPassword(auth, email, password);
            }

            // Obtener el token ID para enviar al backend
            const idToken = await userCredential.user.getIdToken();
            
            onLogin({ 
                user_id: userCredential.user.uid, 
                email: userCredential.user.email,
                idToken: idToken
            });
            
        } catch (err) {
            console.error('Error:', err);
            switch (err.code) {
                case 'auth/user-not-found':
                    setError('Usuario no encontrado');
                    break;
                case 'auth/wrong-password':
                    setError('Contraseña incorrecta');
                    break;
                case 'auth/email-already-in-use':
                    setError('El email ya está registrado');
                    break;
                case 'auth/weak-password':
                    setError('La contraseña debe tener al menos 6 caracteres');
                    break;
                case 'auth/invalid-email':
                    setError('Email inválido');
                    break;
                default:
                    setError('Error de autenticación: ' + err.message);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            overflow: 'hidden',
        }}>
            {/* Fondo de imagen */}
            <img
                src={optradingblanco}
                alt="Fondo login"
                style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100vw',
                    height: '100vh',
                    objectFit: 'cover',
                    zIndex: 0,
                    opacity: 0.25,
                }}
            />
            {/* Capa oscura para mejorar legibilidad */}
            <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100vw',
                height: '100vh',
                background: 'rgba(0,0,0,0.45)',
                zIndex: 1,
            }} />
            <form
                onSubmit={handleSubmit}
                style={{
                    background: 'rgba(255,255,255,0.07)',
                    padding: 32,
                    borderRadius: 16,
                    boxShadow: '0 8px 32px 0 rgba(31, 135, 86, 0.37)',
                    backdropFilter: 'blur(4px)',
                    border: '1px solid rgba(255,255,255,0.18)',
                    display: 'flex',
                    flexDirection: 'column',
                    width: 320,
                    zIndex: 2,
                }}
            >
                <h2 style={{ textAlign: 'center', color: '#fff', marginBottom: 24 }}>
                    {isRegistering ? 'Registrarse' : 'Iniciar sesión'}
                </h2>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    required
                    style={{
                        marginBottom: 16,
                        padding: 12,
                        borderRadius: 8,
                        border: 'none',
                        fontSize: 16
                    }}
                />
                <input
                    type="password"
                    placeholder="Contraseña"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    required
                    style={{
                        marginBottom: 16,
                        padding: 12,
                        borderRadius: 8,
                        border: 'none',
                        fontSize: 16
                    }}
                />
                <button
                    type="submit"
                    disabled={loading}
                    style={{
                        padding: 12,
                        borderRadius: 8,
                        border: 'none',
                        background: loading ? '#666' : '#1ee87a',
                        color: '#232526',
                        fontWeight: 'bold',
                        fontSize: 16,
                        cursor: loading ? 'not-allowed' : 'pointer',
                        marginBottom: 8
                    }}
                >
                    {loading ? 'Cargando...' : (isRegistering ? 'Registrarse' : 'Entrar')}
                </button>
                
                <button
                    type="button"
                    onClick={() => setIsRegistering(!isRegistering)}
                    style={{
                        padding: 8,
                        borderRadius: 8,
                        border: 'none',
                        background: 'transparent',
                        color: '#1ee87a',
                        fontSize: 14,
                        cursor: 'pointer',
                        textDecoration: 'underline'
                    }}
                >
                    {isRegistering ? '¿Ya tienes cuenta? Inicia sesión' : '¿No tienes cuenta? Regístrate'}
                </button>
                
                {error && <p style={{ color: 'red', textAlign: 'center', marginTop: 8 }}>{error}</p>}
            </form>
        </div>
    );
}

export default Login;