import React, { useEffect, useState } from 'react';
import { auth } from '../firebase';
import { API_ENDPOINTS, getAuthHeaders, apiRequest } from '../config/api';
import { FiSearch, FiEdit3, FiBook, FiUser, FiSettings } from 'react-icons/fi';

function ChatHistory({ userId, userEmail, onSelectChat, selectedChat, refresh, showProfile, setShowProfile, onChatCreated }) {
    const [chats, setChats] = useState([]);
    const [error, setError] = useState('');
    const [editingId, setEditingId] = useState(null);
    const [editTitle, setEditTitle] = useState('');
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(false);

    const fetchHistory = async () => {
        setError('');
        setLoading(true);
        try {
            const idToken = await auth.currentUser?.getIdToken();
            if (!idToken) {
                setError('Error de autenticación');
                return;
            }

            // Usar el nuevo endpoint del assistant
            const data = await apiRequest(API_ENDPOINTS.assistantHistory, {
                headers: getAuthHeaders(idToken)
            });
            
            if (data.success && data.messages) {
                // Convertir mensajes del assistant a formato de chats
                const assistantChats = [{
                    chat_id: data.thread_id || 'assistant',
                    created_at: new Date().toISOString(),
                    mensajes: data.messages.map(msg => ({
                        sender: msg.role === 'assistant' ? 'bot' : 'user',
                        text: msg.content
                    })),
                    message_count: data.messages.length
                }];
                setChats(assistantChats);
            } else {
                setChats([]);
            }
        } catch (err) {
            setError('No se pudo conectar con el backend');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (auth.currentUser) {
            fetchHistory();
        }
        // eslint-disable-next-line
    }, [userId, refresh]);

    // Refrescar historial cuando cambie el selectedChat
    useEffect(() => {
        if (auth.currentUser && selectedChat) {
            fetchHistory();
        }
    }, [selectedChat]);

    // Estilo para la lista de chats
    const chatItemStyle = (isSelected) => ({
        width: '100%',
        padding: '12px 12px',
        border: 'none',
        background: isSelected ? '#232f4b' : 'transparent',
        color: isSelected ? '#3b82f6' : '#fff',
        borderRadius: 10,
        textAlign: 'left',
        fontWeight: isSelected ? 600 : 500,
        fontSize: 14,
        cursor: 'pointer',
        marginBottom: 4,
        transition: 'background 0.15s, color 0.15s',
        outline: 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        userSelect: 'none', // Para evitar selección de texto
        minWidth: 0, // Permitir que se ajuste al contenedor
        gap: 8, // Espacio entre título y botón
        boxSizing: 'border-box', // Incluir padding en el ancho total
    });

    // Acciones de la parte superior
    const actionBtnStyle = {
        width: '100%',
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        padding: '12px 12px',
        border: 'none',
        background: 'transparent',
        color: '#fff',
        fontWeight: 500,
        fontSize: 14,
        borderRadius: 10,
        cursor: 'pointer',
        marginBottom: 4,
        transition: 'background 0.15s, color 0.15s',
        outline: 'none',
        minWidth: 0, // Permitir que se ajuste al contenedor
        boxSizing: 'border-box', // Incluir padding en el ancho total
    };

    const handleDelete = async (chat_id) => {
        if (!window.confirm('¿Seguro que deseas eliminar este chat?')) return;
        
        try {
            const idToken = await auth.currentUser?.getIdToken();
            if (!idToken) {
                alert('Error de autenticación');
                return;
            }

            // Usar el nuevo endpoint del assistant para limpiar historial
            await apiRequest(API_ENDPOINTS.assistantClear, {
                method: 'POST',
                headers: getAuthHeaders(idToken)
            });
            
            setChats([]);
            if (selectedChat && selectedChat.chat_id === chat_id) {
                onSelectChat(null);
            }

        } catch (err) {
            alert('Error al eliminar el chat');
        }
    };

    const handleDeleteAll = async () => {
        if (!window.confirm('¿Seguro que deseas eliminar todo el historial? Esta acción no se puede deshacer.')) return;
        
        try {
            const idToken = await auth.currentUser?.getIdToken();
            if (!idToken) {
                alert('Error de autenticación');
                return;
            }

            // Usar el nuevo endpoint del assistant para limpiar historial
            await apiRequest(API_ENDPOINTS.assistantClear, {
                method: 'POST',
                headers: getAuthHeaders(idToken)
            });
            setChats([]);
            onSelectChat(null);
        } catch (err) {
            alert('Error al eliminar el historial');
        }
    };

    return (
        <div style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            height: '100vh',
            background: '#23272f',
            color: '#fff',
            padding: '0 12px 0 12px', // Reducir padding para más espacio
            position: 'relative',
            minWidth: 0,
            overflow: 'hidden', // Prevenir scroll horizontal
        }}>
            {/* Acciones */}
            <div style={{ padding: '24px 0 16px 0', borderBottom: '1px solid #343541' }}>
                <button
                    style={{ ...actionBtnStyle, color: '#1ee87a' }}
                    onClick={async () => {
                        try {
                            const idToken = await auth.currentUser?.getIdToken();
                            if (!idToken) {
                                alert('Error de autenticación');
                                return;
                            }

                            // Para el nuevo sistema, simplemente limpiar el historial
                            // y crear un nuevo thread automáticamente
                            await apiRequest(API_ENDPOINTS.assistantClear, {
                                method: 'POST',
                                headers: getAuthHeaders(idToken)
                            });
                            
                            // Crear un objeto de chat vacío para el assistant
                            const newChat = {
                                chat_id: 'assistant',
                                mensajes: []
                            };
                            onSelectChat(newChat);
                            // Refrescar el historial
                            onChatCreated && onChatCreated();
                        } catch (err) {
                            alert('Error al crear nuevo chat');
                        }
                    }}
                    onMouseEnter={e => { e.target.style.background = '#232f4b'; }}
                    onMouseLeave={e => { e.target.style.background = 'transparent'; }}
                >
                    <FiEdit3 size={18} /> Nuevo chat
                </button>
                <div style={{ height: 12 }} />
                <div style={{ position: 'relative' }}>
                    <FiSearch style={{ position: 'absolute', left: 12, top: 12, color: '#b6b6b6', fontSize: 17 }} />
                    <input
                        type="text"
                        placeholder="Buscar chats..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '8px 8px 8px 36px',
                            borderRadius: 10,
                            border: '1.5px solid #232526',
                            background: '#23272f',
                            color: '#fff',
                            fontSize: 14,
                            marginBottom: 12,
                            outline: 'none',
                            boxSizing: 'border-box',
                        }}
                    />
                </div>
                <div style={{ height: 8 }} />
                <button
                    style={{ ...actionBtnStyle, color: '#3b82f6', fontSize: 13 }}
                    onClick={fetchHistory}
                    onMouseEnter={e => { e.target.style.background = '#232f4b'; }}
                    onMouseLeave={e => { e.target.style.background = 'transparent'; }}
                >
                    Actualizar historial
                </button>
                {chats.length > 0 && (
                    <button
                        style={{ ...actionBtnStyle, color: '#ff6b6b', fontSize: 13 }}
                        onClick={handleDeleteAll}
                        onMouseEnter={e => { e.target.style.background = '#2d1b1b'; }}
                        onMouseLeave={e => { e.target.style.background = 'transparent'; }}
                    >
                        Eliminar todo el historial
                    </button>
                )}
            </div>

            {/* Lista de chats con scroll */}
            <div style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', minHeight: 0, padding: '16px 0 16px 0' }}>
                <div style={{ padding: '0 0' }}>
                    <div style={{ color: '#b6b6b6', fontSize: 13, margin: '12px 0 8px 0', letterSpacing: 1 }}>
                        {loading ? 'Cargando...' : `Chats (${chats.length})`}
                    </div>
                </div>
                <ul style={{ listStyle: 'none', padding: '0 0', margin: 0 }}>
                    {chats.filter(chat => {
                        const firstUserMsg = chat.mensajes.find(m => m.sender === 'user');
                        const title = firstUserMsg ? firstUserMsg.text.toLowerCase() : '';
                        return title.includes(search.toLowerCase());
                    }).map(chat => {
                        const firstUserMsg = chat.mensajes.find(m => m.sender === 'user');
                        const isSelected = selectedChat && selectedChat.chat_id === chat.chat_id;
                        const isEmpty = chat.mensajes.length === 0;
                        return (
                            <li key={chat.chat_id}>
                                <div
                                    onClick={() => onSelectChat(chat)}
                                    style={chatItemStyle(isSelected)}
                                    onMouseOver={e => { if (!isSelected) e.target.style.background = '#232f4b'; }}
                                    onMouseOut={e => { if (!isSelected) e.target.style.background = 'transparent'; }}
                                >
                                    <span style={{ 
                                        fontWeight: 500,
                                        color: isEmpty ? '#888' : '#fff',
                                        fontStyle: isEmpty ? 'italic' : 'normal',
                                        flex: 1,
                                        minWidth: 0,
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        whiteSpace: 'nowrap',
                                        paddingRight: 4, // Pequeño espacio antes del botón
                                    }}>
                                        {firstUserMsg ? 
                                            firstUserMsg.text.slice(0, 35) + (firstUserMsg.text.length > 35 ? '...' : '') : 
                                            'Chat nuevo'
                                        }
                                    </span>
                                    <button
                                        onClick={e => {
                                            e.stopPropagation();
                                            handleDelete(chat.chat_id);
                                        }}
                                        style={{
                                            background: 'transparent',
                                            color: '#ff4d4f',
                                            border: 'none',
                                            cursor: 'pointer',
                                            fontWeight: 'bold',
                                            fontSize: 16,
                                            transition: 'all 0.2s ease',
                                            padding: '4px 6px',
                                            borderRadius: 4,
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            minWidth: '24px',
                                            height: '24px',
                                            flexShrink: 0,
                                        }}
                                        onMouseEnter={e => {
                                            e.target.style.background = '#2d1b1b';
                                            e.target.style.color = '#ff6b6b';
                                        }}
                                        onMouseLeave={e => {
                                            e.target.style.background = 'transparent';
                                            e.target.style.color = '#ff4d4f';
                                        }}
                                        title="Eliminar chat"
                                    >
                                        ×
                                    </button>
                                </div>
                            </li>
                        );
                    })}
                </ul>
                {chats.length === 0 && !loading && (
                    <div style={{ 
                        textAlign: 'center', 
                        color: '#666', 
                        padding: '40px 20px',
                        fontSize: 14
                    }}>
                        No hay chats aún. ¡Crea uno nuevo!
                    </div>
                )}
            </div>

            {/* Pie de usuario SIEMPRE visible */}
            <div style={{
                borderTop: '1px solid #343541',
                padding: '20px 0 16px 0',
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                background: '#23272f',
                fontSize: 15,
                color: '#b6b6b6',
                flexShrink: 0
            }}>

                <span style={{ 
                    fontWeight: 500, 
                    flex: 1,
                    fontSize: 15,
                    color: '#b6b6b6'
                }}>
                    {userEmail}
                </span>
                <button
                    onClick={() => setShowProfile(true)}
                    style={{
                        background: 'transparent',
                        border: 'none',
                        color: '#b6b6b6',
                        cursor: 'pointer',
                        padding: '6px',
                        borderRadius: 6,
                        transition: 'all 0.2s ease',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}
                    onMouseEnter={(e) => {
                        e.target.style.color = '#1ee87a';
                        e.target.style.background = '#343541';
                    }}
                    onMouseLeave={(e) => {
                        e.target.style.color = '#b6b6b6';
                        e.target.style.background = 'transparent';
                    }}
                    title="Configuración del perfil"
                >
                    <FiSettings size={16} />
                </button>
            </div>
        </div>
    );
}

export default ChatHistory;