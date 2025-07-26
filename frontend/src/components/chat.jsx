import React, { useState, useEffect, useRef } from 'react';
import { auth } from '../firebase';
import optradingblanco from '../assets/optradingblanco.png';
import ReactMarkdown from 'react-markdown';

function Chat({ userId, selectedChat, onNewChat }) {
    const [mensaje, setMensaje] = useState('');
    const [mensajes, setMensajes] = useState([]);
    const [chatId, setChatId] = useState(null);
    const [error, setError] = useState('');
    const [userRole, setUserRole] = useState('free');
    const [loading, setLoading] = useState(false);
    const chatEndRef = useRef(null);
    const [inputFocus, setInputFocus] = useState(false);
    const [typingBotMsg, setTypingBotMsg] = useState('');
    const typingTimeout = useRef(null);

    // Función para obtener el rol del usuario
    const getUserRole = async () => {
        try {
            const idToken = await auth.currentUser?.getIdToken(true); // Force refresh
            if (idToken) {
                const res = await fetch('http://127.0.0.1:5000/user/role', {
                    method: 'GET',
                    headers: { 
                        'Authorization': `Bearer ${idToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                if (res.ok) {
                    const data = await res.json();
                    setUserRole(data.role);
                }
            }
        } catch (err) {
            console.error('Error obteniendo rol:', err);
        }
    };

    // Obtener el rol del usuario al cargar
    useEffect(() => {
        if (auth.currentUser) {
            getUserRole();
        }
    }, []);

    useEffect(() => {
        if (selectedChat) {
            setChatId(selectedChat.chat_id);
            setMensajes(selectedChat.mensajes.map(m => ({
                sender: m.sender,
                text: m.text
            })));
        } else {
            setChatId(null);
            setMensajes([]);
        }
    }, [selectedChat]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [mensajes]);

    const handleSend = async (e) => {
        e.preventDefault();
        setError('');
        if (!mensaje.trim()) return;

        // Verificar si el usuario es premium
        if (userRole !== 'premium') {
            setError('Se requiere cuenta premium para chatear. Actualiza tu plan.');
            return;
        }

        setLoading(true);
        try {
            const idToken = await auth.currentUser?.getIdToken();
            if (!idToken) {
                setError('Error de autenticación');
                return;
            }

            const res = await fetch('http://127.0.0.1:5000/chat', {
                method: 'POST',
                headers: { 
                    'Authorization': `Bearer ${idToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    chat_id: chatId,
                    message: mensaje
                }),
            });
            const data = await res.json();
            if (res.ok) {
                if (!chatId && data.chat_id) {
                    onNewChat && onNewChat();
                }
                setChatId(data.chat_id);
                setMensajes(prev => [
                    ...prev,
                    { sender: 'user', text: mensaje }
                ]);
                setMensaje('');
                // Efecto de escritura para el bot
                typeBotMessage(data.reply);
            } else {
                setError(data.error || 'Error al enviar mensaje');
            }
        } catch (err) {
            setError('No se pudo conectar con el backend');
        } finally {
            setLoading(false);
        }
    };

    const typeBotMessage = (fullText) => {
        setTypingBotMsg('');
        let i = 0;
        if (typingTimeout.current) clearTimeout(typingTimeout.current);

        const type = () => {
            setTypingBotMsg(prev => prev + fullText[i]);
            i++;
            if (i < fullText.length) {
                typingTimeout.current = setTimeout(type, 25); // velocidad de escritura
            } else {
                // Cuando termina, lo agrega a la lista de mensajes
                setMensajes(prev => [
                    ...prev,
                    { sender: 'bot', text: fullText }
                ]);
                setTypingBotMsg('');
            }
        };
        type();
    };

    return (
        <div style={{
            position: 'relative',
            background: '#23272f',
            borderRadius: 16,
            minWidth: 0, // importante para flexbox responsive
            maxWidth: '100%',
            width: '100%',
            boxShadow: '0 8px 32px 0 rgba(31,38,135,0.18)',
            border: '1.5px solid #232526',
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
            margin: 0,
            overflow: 'hidden',
        }}>
            {/* Fondo de imagen */}
            <img
                src={optradingblanco}
                alt="Fondo chat"
                style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    width: '180px',
                    height: '180px',
                    transform: 'translate(-50%, -50%)',
                    objectFit: 'contain',
                    zIndex: 0,
                    opacity: 0.10,
                    pointerEvents: 'none',
                }}
            />
            {/* Capa oscura para mejorar legibilidad */}
            <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                background: 'rgba(0,0,0,0.18)',
                zIndex: 1,
            }} />
            <div style={{ position: 'relative', zIndex: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
                {/* Header del bot, centrado y alineado */}
                <div style={{
                    width: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 0 12px 0',
                    padding: '18px 0 0 0',
                    background: 'transparent',
                    borderBottom: '1px solid #232526',
                }}>
                    <div style={{
                        maxWidth: 700,
                        width: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: '0 32px',
                    }}>
                        <h1 style={{
                            fontSize: '1.3rem',
                            marginBottom: 4,
                            fontWeight: 700,
                            color: '#fff',
                            letterSpacing: 0.5,
                            textAlign: 'center',
                        }}>
                            MentorBot IA - Asistente de Trading
                        </h1>
                        <p style={{
                            fontSize: '1rem',
                            marginBottom: 0,
                            color: '#b6b6b6',
                            letterSpacing: 0.1,
                            textAlign: 'center',
                            margin: '0 0 16px 0',
                        }}>
                            Tu asistente inteligente para análisis técnico y fundamental, gestión de riesgo y estrategias de inversión en acciones, ETFs y criptomonedas. Consultá cualquier duda de trading y finanzas.
                        </p>
                        {/* Mostrar rol del usuario */}
                        <div style={{
                            background: userRole === 'premium' ? '#1ee87a' : '#ff6b6b',
                            color: userRole === 'premium' ? '#232526' : '#fff',
                            padding: '4px 12px',
                            borderRadius: 12,
                            fontSize: '0.8rem',
                            fontWeight: 'bold',
                            textTransform: 'uppercase'
                        }}>
                            Plan: {userRole === 'premium' ? 'Premium' : 'Free'}
                        </div>
                    </div>
                </div>
                <div style={{
                    flex: 1,
                    overflowY: 'auto',
                    padding: '32px 0 24px 0',
                    background: 'transparent',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 12,
                    minHeight: 0, // para que flexbox no expanda
                    maxHeight: 'calc(100vh - 250px)',
                }}>
                    {mensajes.map((m, i) => (
                        <div
                            key={i}
                            style={{
                                display: 'flex',
                                justifyContent: m.sender === 'user' ? 'flex-end' : 'flex-start',
                                width: '100%',
                            }}
                        >
                            <span
                                style={{
                                    background: m.sender === 'user' ? '#2d313a' : '#343541',
                                    color: '#fff',
                                    borderRadius: 16,
                                    padding: '14px 20px',
                                    maxWidth: '70%',
                                    wordBreak: 'break-word',
                                    fontSize: 16,
                                    boxShadow: m.sender === 'user' ? '0 2px 8px #23252633' : '0 2px 8px #0002',
                                    marginRight: m.sender === 'user' ? 16 : 0,
                                    marginLeft: m.sender === 'bot' ? 16 : 0,
                                    border: m.sender === 'user' ? '1.5px solid #1ee87a' : '1.5px solid #232526',
                                }}
                            >
                                {m.sender === 'bot' ? (
                                    <ReactMarkdown
                                        children={m.text}
                                        components={{
                                            h1: ({node, ...props}) => <h1 style={{fontSize: 22, fontWeight: 700, margin: '16px 0 8px 0'}} {...props} />,
                                            h2: ({node, ...props}) => <h2 style={{fontSize: 18, fontWeight: 700, margin: '12px 0 6px 0'}} {...props} />,
                                            li: ({node, ...props}) => <li style={{marginLeft: 16, marginBottom: 4}} {...props} />,
                                            strong: ({node, ...props}) => <strong style={{fontWeight: 700}} {...props} />,
                                            // Podés agregar más estilos si querés
                                        }}
                                    />
                                ) : m.text}
                            </span>
                        </div>
                    ))}
                    {typingBotMsg && (
                        <div style={{ display: 'flex', justifyContent: 'flex-start', width: '100%' }}>
                            <span
                                style={{
                                    background: '#343541',
                                    color: '#fff',
                                    borderRadius: 16,
                                    padding: '14px 20px',
                                    maxWidth: '70%',
                                    wordBreak: 'break-word',
                                    fontSize: 16,
                                    boxShadow: '0 2px 8px #0002',
                                    marginLeft: 16,
                                    border: '1.5px solid #232526',
                                    fontStyle: 'italic'
                                }}
                            >
                                {typingBotMsg}
                                <span className='blinking-cursor'>|</span>
                            </span>
                        </div>
                    )}
                    <div ref={chatEndRef} />
                </div>
                <form onSubmit={handleSend} style={{
                    display: 'flex',
                    gap: 12,
                    background: '#23272f',
                    borderTop: '1.5px solid #232526',
                    padding: 20,
                    borderRadius: '0 0 0px 0px',
                    boxShadow: '0 -2px 8px #0002',
                }}>
                    <input
                        type="text"
                        value={mensaje}
                        onChange={e => setMensaje(e.target.value)}
                        placeholder={userRole === 'premium' ? "Preguntá lo que quieras..." : "Actualiza a Premium para chatear"}
                        disabled={userRole !== 'premium' || loading}
                        onFocus={() => setInputFocus(true)}
                        onBlur={() => setInputFocus(false)}
                        style={{
                            flex: 1,
                            padding: 18,
                            borderRadius: 12,
                            border: inputFocus ? '1.5px solid #1ee87a' : '1.5px solid #232526',
                            fontSize: 16,
                            background: userRole !== 'premium' ? '#444654' : '#23272f',
                            color: userRole !== 'premium' ? '#666' : '#fff',
                            outline: 'none',
                            boxShadow: '0 2px 8px #0001',
                            transition: 'border 0.2s',
                            cursor: userRole !== 'premium' ? 'not-allowed' : 'text',
                        }}
                    />
                    <button
                        type="submit"
                        disabled={userRole !== 'premium' || loading}
                        style={{
                            padding: '0 32px',
                            borderRadius: 12,
                            border: 'none',
                            background: userRole !== 'premium' ? '#666' : (loading ? '#5c5f70' : '#444654'),
                            color: '#fff',
                            fontWeight: 'bold',
                            fontSize: 18,
                            cursor: userRole !== 'premium' || loading ? 'not-allowed' : 'pointer',
                            boxShadow: '0 2px 8px #0002',
                            transition: 'background 0.2s, color 0.2s',
                        }}
                        onMouseOver={e => {
                            if (userRole === 'premium' && !loading) {
                                e.currentTarget.style.background = '#5c5f70';
                            }
                        }}
                        onMouseOut={e => {
                            if (userRole === 'premium' && !loading) {
                                e.currentTarget.style.background = '#444654';
                            }
                        }}
                    >
                        {loading ? 'Enviando...' : (userRole === 'premium' ? 'Enviar' : 'Premium')}
                    </button>
                </form>
                {error && <p style={{ color: 'red', textAlign: 'center', marginTop: 8 }}>{error}</p>}
            </div>
        </div>
    );
}

export default Chat;

