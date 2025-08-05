import React, { useState, useEffect, useRef } from 'react';
import { auth } from '../firebase';
import optradingblanco from '../assets/optradingblanco.png';
import ReactMarkdown from 'react-markdown';
import { API_ENDPOINTS, getAuthHeaders, apiRequest } from '../config/api';
import { FiUpload, FiImage, FiSend, FiTrash2, FiRefreshCw } from 'react-icons/fi';

function AssistantChat({ userId, selectedChat, onNewChat, onChatCreated }) {
    const [mensaje, setMensaje] = useState('');
    const [mensajes, setMensajes] = useState([]);
    const [error, setError] = useState('');
    const [userRole, setUserRole] = useState('free');
    const [loading, setLoading] = useState(false);
    const [isTyping, setIsTyping] = useState(false);
    const [typingText, setTypingText] = useState('');
    const [fullResponse, setFullResponse] = useState('');
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [uploadingFiles, setUploadingFiles] = useState(false);
    const chatEndRef = useRef(null);
    const fileInputRef = useRef(null);
    const [windowWidth, setWindowWidth] = useState(window.innerWidth);
    const typingInterval = useRef(null);
    const typingSpeed = 8;

    // Hook para detectar cambios en el tamaño de la ventana
    useEffect(() => {
        const handleResize = () => {
            setWindowWidth(window.innerWidth);
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    // Función para obtener el rol del usuario
    const getUserRole = async () => {
        try {
            const idToken = await auth.currentUser?.getIdToken(true);
            if (idToken) {
                const data = await apiRequest(API_ENDPOINTS.userRole, {
                    headers: getAuthHeaders(idToken)
                });
                setUserRole(data.role);
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

    // Cargar historial del assistant
    const loadAssistantHistory = async () => {
        try {
            const idToken = await auth.currentUser?.getIdToken();
            if (!idToken) return;

            const response = await fetch(API_ENDPOINTS.assistantHistory, {
                headers: getAuthHeaders(idToken)
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success && data.messages) {
                    const formattedMessages = data.messages.map(msg => ({
                        sender: msg.role === 'assistant' ? 'bot' : 'user',
                        text: msg.content
                    }));
                    setMensajes(formattedMessages);
                }
            }
        } catch (err) {
            console.error('Error cargando historial:', err);
        }
    };

    useEffect(() => {
        if (userRole === 'premium') {
            loadAssistantHistory();
        }
    }, [userRole]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [mensajes, typingText]);

    // Función para simular escritura
    const simulateTyping = (text) => {
        setIsTyping(true);
        setTypingText('');
        setFullResponse(text);
        
        let currentIndex = 0;
        
        const typeNextChar = () => {
            if (currentIndex < text.length) {
                const charsToAdd = Math.min(5, text.length - currentIndex);
                const newText = text.slice(currentIndex, currentIndex + charsToAdd);
                setTypingText(prev => prev + newText);
                currentIndex += charsToAdd;
                
                if (currentIndex < text.length) {
                    typingInterval.current = setTimeout(typeNextChar, typingSpeed);
                } else {
                    setIsTyping(false);
                    setMensajes(prev => [
                        ...prev,
                        { sender: 'bot', text: text }
                    ]);
                    setTypingText('');
                    setFullResponse('');
                }
            }
        };
        
        typeNextChar();
    };

    // Función para manejar selección de archivos
    const handleFileSelect = (event) => {
        const files = Array.from(event.target.files);
        const imageFiles = files.filter(file => 
            file.type.startsWith('image/') && file.size <= 10 * 1024 * 1024
        );
        
        setSelectedFiles(prev => [...prev, ...imageFiles]);
    };

    // Función para subir archivos
    const uploadFiles = async () => {
        if (selectedFiles.length === 0) return [];
        
        setUploadingFiles(true);
        const uploadedFiles = [];
        
        try {
            for (const file of selectedFiles) {
                const formData = new FormData();
                formData.append('file', file);
                
                const idToken = await auth.currentUser?.getIdToken();
                const response = await fetch(API_ENDPOINTS.assistantUpload, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${idToken}`
                    },
                    body: formData
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.success && data.file_id) {
                        uploadedFiles.push({
                            type: 'image',
                            url: data.file_id,
                            filename: file.name
                        });
                    } else {
                        console.error('Error en respuesta de upload:', data);
                        setError(`Error subiendo ${file.name}: ${data.error || 'Error desconocido'}`);
                    }
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    console.error('Error HTTP en upload:', response.status, errorData);
                    setError(`Error subiendo ${file.name}: ${errorData.error || 'Error de servidor'}`);
                }
            }
        } catch (err) {
            console.error('Error subiendo archivos:', err);
            setError('Error subiendo archivos');
        } finally {
            setUploadingFiles(false);
            setSelectedFiles([]);
        }
        
        return uploadedFiles;
    };

    // Función para enviar mensaje
    const handleSend = async (e) => {
        e.preventDefault();
        setError('');
        if (!mensaje.trim() && selectedFiles.length === 0) return;

        if (userRole !== 'premium') {
            setError('Se requiere cuenta premium para usar el assistant');
            return;
        }

        if (typingInterval.current) {
            clearTimeout(typingInterval.current);
            setIsTyping(false);
            setTypingText('');
        }

        const userMessage = mensaje.trim();
        setMensaje('');
        setLoading(true);

        // Agregar mensaje del usuario
        setMensajes(prev => [
            ...prev,
            { sender: 'user', text: userMessage }
        ]);

        try {
            const idToken = await auth.currentUser?.getIdToken();
            if (!idToken) {
                setError('Error de autenticación');
                return;
            }

            // Subir archivos si los hay
            const uploadedFiles = await uploadFiles();
            
            // Preparar datos del mensaje
            const messageData = {
                message: userMessage || 'Analiza las imágenes adjuntas'
            };
            
            if (uploadedFiles.length > 0) {
                messageData.files = uploadedFiles;
            }

            const response = await fetch(API_ENDPOINTS.assistantChat, {
                method: 'POST',
                headers: {
                    ...getAuthHeaders(idToken),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(messageData)
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    simulateTyping(data.message);
                    onNewChat && onNewChat();
                    onChatCreated && onChatCreated();
                } else {
                    setError(data.error || 'Error procesando mensaje');
                }
            } else {
                const errorData = await response.json();
                setError(errorData.error || 'Error de conexión');
            }
        } catch (err) {
            setError('No se pudo conectar con el assistant');
        } finally {
            setLoading(false);
        }
    };

    // Función para limpiar historial
    const clearHistory = async () => {
        try {
            const idToken = await auth.currentUser?.getIdToken();
            if (!idToken) return;

            const response = await fetch(API_ENDPOINTS.assistantClear, {
                method: 'POST',
                headers: getAuthHeaders(idToken)
            });

            if (response.ok) {
                setMensajes([]);
                setError('');
            }
        } catch (err) {
            console.error('Error limpiando historial:', err);
        }
    };

    // Función para analizar imagen específica
    const analyzeImage = async (imageUrl, prompt = '') => {
        try {
            const idToken = await auth.currentUser?.getIdToken();
            if (!idToken) return;

            const response = await fetch(API_ENDPOINTS.assistantAnalyzeImage, {
                method: 'POST',
                headers: {
                    ...getAuthHeaders(idToken),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image_url: imageUrl,
                    analysis_type: 'complete',
                    prompt: prompt
                })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    simulateTyping(data.analysis);
                }
            }
        } catch (err) {
            console.error('Error analizando imagen:', err);
        }
    };

    // Cleanup al desmontar
    useEffect(() => {
        return () => {
            if (typingInterval.current) {
                clearTimeout(typingInterval.current);
            }
        };
    }, []);

    // Atajos de teclado durante la escritura
    useEffect(() => {
        const handleKeyPress = (e) => {
            if (isTyping) {
                if (e.key === 'Escape') {
                    if (typingInterval.current) {
                        clearTimeout(typingInterval.current);
                    }
                    setIsTyping(false);
                    setMensajes(prev => [
                        ...prev,
                        { sender: 'bot', text: typingText }
                    ]);
                    setTypingText('');
                    setFullResponse('');
                } else if (e.key === 'Enter') {
                    if (typingInterval.current) {
                        clearTimeout(typingInterval.current);
                    }
                    setIsTyping(false);
                    setMensajes(prev => [
                        ...prev,
                        { sender: 'bot', text: fullResponse }
                    ]);
                    setTypingText('');
                    setFullResponse('');
                }
            }
        };

        if (isTyping) {
            document.addEventListener('keydown', handleKeyPress);
        }

        return () => {
            document.removeEventListener('keydown', handleKeyPress);
        };
    }, [isTyping, typingText, fullResponse]);

    return (
        <div style={{
            position: 'relative',
            background: '#23272f',
            borderRadius: 16,
            minWidth: 0,
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
            
            {/* Capa oscura */}
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
                {/* Header */}
                {mensajes.length === 0 && !isTyping && (
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
                                Assistant IA - Análisis Avanzado
                            </h1>
                            <p style={{
                                fontSize: '1rem',
                                marginBottom: 0,
                                color: '#b6b6b6',
                                letterSpacing: 0.1,
                                textAlign: 'center',
                                margin: '0 0 16px 0',
                            }}>
                                Tu asistente inteligente con capacidades avanzadas: análisis de imágenes, precios en tiempo real, y contexto persistente.
                            </p>
                            <div style={{
                                background: userRole === 'premium' ? '#1ee87a' : '#ff6b6b',
                                color: userRole === 'premium' ? '#232526' : '#fff',
                                padding: '4px 12px',
                                borderRadius: 12,
                                fontSize: '0.8rem',
                                fontWeight: 'bold',
                                textTransform: 'uppercase',
                                marginBottom: 16,
                            }}>
                                Plan: {userRole === 'premium' ? 'Premium' : 'Free'}
                            </div>
                        </div>
                    </div>
                )}

                {/* Archivos seleccionados */}
                {selectedFiles.length > 0 && (
                    <div style={{
                        padding: '12px 16px',
                        background: '#2a2f3a',
                        borderBottom: '1px solid #232526',
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: 8,
                    }}>
                        {selectedFiles.map((file, index) => (
                            <div key={index} style={{
                                background: '#343541',
                                padding: '8px 12px',
                                borderRadius: 8,
                                fontSize: '0.8rem',
                                color: '#fff',
                                display: 'flex',
                                alignItems: 'center',
                                gap: 8,
                            }}>
                                <FiImage size={14} />
                                {file.name}
                                <button
                                    onClick={() => setSelectedFiles(prev => prev.filter((_, i) => i !== index))}
                                    style={{
                                        background: 'none',
                                        border: 'none',
                                        color: '#ff6b6b',
                                        cursor: 'pointer',
                                        padding: 0,
                                    }}
                                >
                                    ×
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                {/* Mensajes */}
                <div style={{
                    flex: 1,
                    overflowY: 'auto',
                    padding: mensajes.length === 0 ? '32px 0 24px 0' : '16px 0 24px 0',
                    background: 'transparent',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 12,
                    minHeight: 0,
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
                                    maxWidth: windowWidth <= 1366 ? '85%' : '70%',
                                    wordBreak: 'break-word',
                                    fontSize: windowWidth <= 1366 ? 14 : 16,
                                    boxShadow: m.sender === 'user' ? '0 2px 8px #23252633' : '0 2px 8px #0002',
                                    marginRight: m.sender === 'user' ? 16 : 0,
                                    marginLeft: m.sender === 'bot' ? 16 : 0,
                                    border: m.sender === 'user' ? '1.5px solid #1ee87a' : '1.5px solid #232526',
                                }}
                            >
                                {m.sender === 'bot' ? (
                                    <div className="chat-markdown">
                                        <ReactMarkdown
                                            children={m.text}
                                            components={{
                                                h1: ({node, ...props}) => <h1 style={{
                                                    fontSize: windowWidth <= 1366 ? 18 : 22, 
                                                    fontWeight: 700, 
                                                    margin: '16px 0 8px 0',
                                                    color: '#fff'
                                                }} {...props} />,
                                                h2: ({node, ...props}) => <h2 style={{
                                                    fontSize: windowWidth <= 1366 ? 16 : 18, 
                                                    fontWeight: 700, 
                                                    margin: '12px 0 6px 0',
                                                    color: '#fff'
                                                }} {...props} />,
                                                h3: ({node, ...props}) => <h3 style={{
                                                    fontSize: windowWidth <= 1366 ? 14 : 16, 
                                                    fontWeight: 600, 
                                                    margin: '10px 0 5px 0',
                                                    color: '#fff'
                                                }} {...props} />,
                                                p: ({node, ...props}) => <p style={{
                                                    margin: '8px 0',
                                                    lineHeight: 1.5,
                                                    color: '#fff'
                                                }} {...props} />,
                                                ul: ({node, ...props}) => <ul style={{
                                                    margin: '8px 0',
                                                    paddingLeft: 20,
                                                    color: '#fff'
                                                }} {...props} />,
                                                ol: ({node, ...props}) => <ol style={{
                                                    margin: '8px 0',
                                                    paddingLeft: 20,
                                                    color: '#fff'
                                                }} {...props} />,
                                                li: ({node, ...props}) => <li style={{
                                                    marginBottom: 4,
                                                    lineHeight: 1.4,
                                                    color: '#fff'
                                                }} {...props} />,
                                                strong: ({node, ...props}) => <strong style={{
                                                    fontWeight: 700,
                                                    color: '#1ee87a'
                                                }} {...props} />,
                                                em: ({node, ...props}) => <em style={{
                                                    fontStyle: 'italic',
                                                    color: '#b6b6b6'
                                                }} {...props} />,
                                                code: ({node, inline, ...props}) => inline ? (
                                                    <code style={{
                                                        background: '#232526',
                                                        padding: '2px 6px',
                                                        borderRadius: 4,
                                                        fontSize: '0.9em',
                                                        fontFamily: 'monospace',
                                                        color: '#1ee87a'
                                                    }} {...props} />
                                                ) : (
                                                    <pre style={{
                                                        background: '#232526',
                                                        padding: 12,
                                                        borderRadius: 8,
                                                        overflow: 'auto',
                                                        margin: '12px 0',
                                                        border: '1px solid #343541'
                                                    }}>
                                                        <code style={{
                                                            fontFamily: 'monospace',
                                                            fontSize: windowWidth <= 1366 ? 12 : 14,
                                                            color: '#fff',
                                                            lineHeight: 1.4
                                                        }} {...props} />
                                                    </pre>
                                                ),
                                                blockquote: ({node, ...props}) => <blockquote style={{
                                                    borderLeft: '4px solid #1ee87a',
                                                    paddingLeft: 16,
                                                    margin: '12px 0',
                                                    fontStyle: 'italic',
                                                    color: '#b6b6b6',
                                                    background: '#2a2f3a',
                                                    padding: '8px 16px',
                                                    borderRadius: '0 8px 8px 0'
                                                }} {...props} />,
                                            }}
                                        />
                                    </div>
                                ) : m.text}
                            </span>
                        </div>
                    ))}
                    
                    {/* Indicador de escritura */}
                    {isTyping && (
                        <div style={{ display: 'flex', justifyContent: 'flex-start', width: '100%' }}>
                            <span
                                style={{
                                    background: '#343541',
                                    color: '#fff',
                                    borderRadius: 16,
                                    padding: '14px 20px',
                                    maxWidth: windowWidth <= 1366 ? '85%' : '70%',
                                    wordBreak: 'break-word',
                                    fontSize: windowWidth <= 1366 ? 14 : 16,
                                    boxShadow: '0 2px 8px #0002',
                                    marginLeft: 16,
                                    border: '1.5px solid #232526',
                                }}
                            >
                                <div className="chat-markdown">
                                    <ReactMarkdown
                                        children={typingText}
                                        components={{
                                            h1: ({node, ...props}) => <h1 style={{
                                                fontSize: windowWidth <= 1366 ? 18 : 22, 
                                                fontWeight: 700, 
                                                margin: '16px 0 8px 0',
                                                color: '#fff'
                                            }} {...props} />,
                                            h2: ({node, ...props}) => <h2 style={{
                                                fontSize: windowWidth <= 1366 ? 16 : 18, 
                                                fontWeight: 700, 
                                                margin: '12px 0 6px 0',
                                                color: '#fff'
                                            }} {...props} />,
                                            h3: ({node, ...props}) => <h3 style={{
                                                fontSize: windowWidth <= 1366 ? 14 : 16, 
                                                fontWeight: 600, 
                                                margin: '10px 0 5px 0',
                                                color: '#fff'
                                            }} {...props} />,
                                            p: ({node, ...props}) => <p style={{
                                                margin: '8px 0',
                                                lineHeight: 1.5,
                                                color: '#fff'
                                            }} {...props} />,
                                            ul: ({node, ...props}) => <ul style={{
                                                margin: '8px 0',
                                                paddingLeft: 20,
                                                color: '#fff'
                                            }} {...props} />,
                                            ol: ({node, ...props}) => <ol style={{
                                                margin: '8px 0',
                                                paddingLeft: 20,
                                                color: '#fff'
                                            }} {...props} />,
                                            li: ({node, ...props}) => <li style={{
                                                marginBottom: 4,
                                                lineHeight: 1.4,
                                                color: '#fff'
                                            }} {...props} />,
                                            strong: ({node, ...props}) => <strong style={{
                                                fontWeight: 700,
                                                color: '#1ee87a'
                                            }} {...props} />,
                                            em: ({node, ...props}) => <em style={{
                                                fontStyle: 'italic',
                                                color: '#b6b6b6'
                                            }} {...props} />,
                                            code: ({node, inline, ...props}) => inline ? (
                                                <code style={{
                                                    background: '#232526',
                                                    padding: '2px 6px',
                                                    borderRadius: 4,
                                                    fontSize: '0.9em',
                                                    fontFamily: 'monospace',
                                                    color: '#1ee87a'
                                                }} {...props} />
                                            ) : (
                                                <pre style={{
                                                    background: '#232526',
                                                    padding: 12,
                                                    borderRadius: 8,
                                                    overflow: 'auto',
                                                    margin: '12px 0',
                                                    border: '1px solid #343541'
                                                }}>
                                                    <code style={{
                                                        fontFamily: 'monospace',
                                                        fontSize: windowWidth <= 1366 ? 12 : 14,
                                                        color: '#fff',
                                                        lineHeight: 1.4
                                                    }} {...props} />
                                                </pre>
                                            ),
                                            blockquote: ({node, ...props}) => <blockquote style={{
                                                borderLeft: '4px solid #1ee87a',
                                                paddingLeft: 16,
                                                margin: '12px 0',
                                                fontStyle: 'italic',
                                                color: '#b6b6b6',
                                                background: '#2a2f3a',
                                                padding: '8px 16px',
                                                borderRadius: '0 8px 8px 0'
                                            }} {...props} />,
                                        }}
                                    />
                                </div>
                                <span 
                                    style={{
                                        display: 'inline-block',
                                        width: '2px',
                                        height: '1.2em',
                                        background: '#1ee87a',
                                        marginLeft: '2px',
                                        animation: 'blink 1s infinite',
                                        verticalAlign: 'middle'
                                    }}
                                />
                                <div style={{
                                    position: 'absolute',
                                    bottom: '-20px',
                                    left: '20px',
                                    fontSize: '10px',
                                    color: '#666',
                                    fontStyle: 'italic'
                                }}>
                                    ESC: frenar • ENTER: completar
                                </div>
                            </span>
                        </div>
                    )}
                    
                    <div ref={chatEndRef} />
                </div>

                {/* Formulario de entrada */}
                <form onSubmit={handleSend} style={{
                    display: 'flex',
                    gap: windowWidth <= 1366 ? 8 : 12,
                    background: '#23272f',
                    borderTop: '1.5px solid #232526',
                    padding: windowWidth <= 1366 ? 16 : 20,
                    borderRadius: '0 0 16px 16px',
                    boxShadow: '0 -2px 8px #0002',
                    marginTop: 'auto',
                    flexShrink: 0,
                }}>
                    {/* Botón de subir archivo */}
                    <button
                        type="button"
                        onClick={() => fileInputRef.current?.click()}
                        disabled={userRole !== 'premium' || loading || uploadingFiles}
                        style={{
                            padding: windowWidth <= 1366 ? 12 : 16,
                            borderRadius: 12,
                            border: '1.5px solid #232526',
                            background: userRole !== 'premium' ? '#666' : '#343541',
                            color: '#fff',
                            cursor: userRole !== 'premium' || loading || uploadingFiles ? 'not-allowed' : 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            transition: 'all 0.2s',
                        }}
                        title="Subir imagen"
                    >
                        {uploadingFiles ? (
                            <FiRefreshCw size={20} style={{ animation: 'spin 1s linear infinite' }} />
                        ) : (
                            <FiUpload size={20} />
                        )}
                    </button>

                    {/* Input de archivo oculto */}
                    <input
                        ref={fileInputRef}
                        type="file"
                        multiple
                        accept="image/*"
                        onChange={handleFileSelect}
                        style={{ display: 'none' }}
                    />

                    {/* Input de texto */}
                    <input
                        type="text"
                        value={mensaje}
                        onChange={e => setMensaje(e.target.value)}
                        placeholder={userRole === 'premium' ? "Preguntá o subí una imagen..." : "Actualiza a Premium para usar el assistant"}
                        disabled={userRole !== 'premium' || loading || isTyping}
                        style={{
                            flex: 1,
                            padding: windowWidth <= 1366 ? 14 : 18,
                            borderRadius: 12,
                            border: '1.5px solid #232526',
                            fontSize: windowWidth <= 1366 ? 14 : 16,
                            background: userRole !== 'premium' ? '#444654' : '#23272f',
                            color: userRole !== 'premium' ? '#666' : '#fff',
                            outline: 'none',
                            boxShadow: '0 2px 8px #0001',
                            transition: 'border 0.2s',
                            cursor: userRole !== 'premium' ? 'not-allowed' : 'text',
                        }}
                    />

                    {/* Botón de enviar */}
                    <button
                        type={isTyping ? "button" : "submit"}
                        onClick={isTyping ? (() => {
                            if (typingInterval.current) {
                                clearTimeout(typingInterval.current);
                            }
                            setIsTyping(false);
                            setMensajes(prev => [
                                ...prev,
                                { sender: 'bot', text: fullResponse }
                            ]);
                            setTypingText('');
                            setFullResponse('');
                        }) : undefined}
                        disabled={userRole !== 'premium' || loading}
                        style={{
                            padding: windowWidth <= 1366 ? '0 24px' : '0 32px',
                            borderRadius: 12,
                            border: 'none',
                            background: userRole !== 'premium' ? '#666' : (loading ? '#5c5f70' : isTyping ? '#ff6b6b' : '#444654'),
                            color: '#fff',
                            fontWeight: 'bold',
                            fontSize: windowWidth <= 1366 ? 16 : 18,
                            cursor: userRole !== 'premium' || loading ? 'not-allowed' : 'pointer',
                            boxShadow: '0 2px 8px #0002',
                            transition: 'background 0.2s, color 0.2s',
                        }}
                    >
                        {loading ? 'Enviando...' : isTyping ? 'Frenar' : (userRole === 'premium' ? 'Enviar' : 'Premium')}
                    </button>

                    {/* Botón de limpiar historial */}
                    {mensajes.length > 0 && (
                        <button
                            type="button"
                            onClick={clearHistory}
                            disabled={userRole !== 'premium' || loading || isTyping}
                            style={{
                                padding: windowWidth <= 1366 ? 12 : 16,
                                borderRadius: 12,
                                border: '1.5px solid #232526',
                                background: userRole !== 'premium' ? '#666' : '#ff6b6b',
                                color: '#fff',
                                cursor: userRole !== 'premium' || loading || isTyping ? 'not-allowed' : 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                transition: 'all 0.2s',
                            }}
                            title="Limpiar historial"
                        >
                            <FiTrash2 size={20} />
                        </button>
                    )}
                </form>

                {error && (
                    <p style={{ 
                        color: '#ff6b6b', 
                        textAlign: 'center', 
                        marginTop: 8, 
                        padding: '0 16px',
                        fontSize: '0.9rem'
                    }}>
                        {error}
                    </p>
                )}
            </div>
            
            {/* CSS para animaciones */}
            <style>{`
                @keyframes blink {
                    0%, 50% { opacity: 1; }
                    51%, 100% { opacity: 0; }
                }
                
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    );
}

export default AssistantChat; 