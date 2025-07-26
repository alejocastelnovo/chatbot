import React, { useEffect, useState } from 'react';
import { auth } from '../firebase';
import { FiSearch, FiEdit3, FiBook, FiUser } from 'react-icons/fi';

function ChatHistory({ userId, userEmail, onSelectChat, selectedChat, refresh }) {
    const [chats, setChats] = useState([]);
    const [error, setError] = useState('');
    const [editingId, setEditingId] = useState(null);
    const [editTitle, setEditTitle] = useState('');
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchHistory = async () => {
            setError('');
            setLoading(true);
            try {
                const idToken = await auth.currentUser?.getIdToken();
                if (!idToken) {
                    setError('Error de autenticación');
                    return;
                }

                const res = await fetch('http://127.0.0.1:5000/history', {
                    method: 'GET',
                    headers: { 
                        'Authorization': `Bearer ${idToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                const data = await res.json();
                if (res.ok) {
                    setChats(data.chats);
                } else {
                    setError(data.error || 'Error al obtener historial');
                }
            } catch (err) {
                setError('No se pudo conectar con el backend');
            } finally {
                setLoading(false);
            }
        };
        
        if (auth.currentUser) {
            fetchHistory();
        }
        // eslint-disable-next-line
    }, [userId, refresh]);

    // Estilo para la lista de chats
    const chatItemStyle = (isSelected) => ({
        width: '100%',
        padding: '10px 14px',
        border: 'none',
        background: isSelected ? '#232f4b' : 'transparent',
        color: isSelected ? '#3b82f6' : '#fff',
        borderRadius: 8,
        textAlign: 'left',
        fontWeight: isSelected ? 600 : 500,
        fontSize: 15,
        cursor: 'pointer',
        marginBottom: 2,
        transition: 'background 0.15s, color 0.15s',
        outline: 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
    });

    // Acciones de la parte superior
    const actionBtnStyle = {
        width: '100%',
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        padding: '10px 14px',
        border: 'none',
        background: 'transparent',
        color: '#fff',
        fontWeight: 500,
        fontSize: 15,
        borderRadius: 8,
        cursor: 'pointer',
        marginBottom: 2,
        transition: 'background 0.15s, color 0.15s',
        outline: 'none',
    };

    const handleDelete = async (chat_id) => {
        if (!window.confirm('¿Seguro que deseas eliminar este chat?')) return;
        
        try {
            const idToken = await auth.currentUser?.getIdToken();
            if (!idToken) {
                alert('Error de autenticación');
                return;
            }

            const res = await fetch('http://127.0.0.1:5000/delete_chat', {
                method: 'POST',
                headers: { 
                    'Authorization': `Bearer ${idToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ chat_id }),
            });
            const data = await res.json();
            if (res.ok) {
                setChats(chats => chats.filter(c => c.chat_id !== chat_id));
                if (selectedChat && selectedChat.chat_id === chat_id) {
                    onSelectChat(null);
                }
            } else {
                alert(data.error || 'No se pudo eliminar el chat');
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

            const res = await fetch('http://127.0.0.1:5000/delete_history', {
                method: 'POST',
                headers: { 
                    'Authorization': `Bearer ${idToken}`,
                    'Content-Type': 'application/json'
                }
            });
            const data = await res.json();
            if (res.ok) {
                setChats([]);
                onSelectChat(null);
            } else {
                alert(data.error || 'No se pudo eliminar el historial');
            }
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
            padding: 0,
            position: 'relative',
            minWidth: 0,
        }}>
            {/* Acciones */}
            <div style={{ padding: 20, paddingBottom: 10, borderBottom: '1px solid #343541' }}>
                <button
                    style={{ ...actionBtnStyle, color: '#1ee87a' }}
                    onClick={() => onSelectChat(null)}
                    onMouseEnter={e => { e.target.style.background = '#232f4b'; }}
                    onMouseLeave={e => { e.target.style.background = 'transparent'; }}
                >
                    <FiEdit3 size={18} /> Nuevo chat
                </button>
                <div style={{ height: 8 }} />
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
                            borderRadius: 8,
                            border: '1.5px solid #232526',
                            background: '#23272f',
                            color: '#fff',
                            fontSize: 15,
                            marginBottom: 8,
                            outline: 'none',
                        }}
                    />
                </div>
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
            <div style={{ flex: 1, overflowY: 'auto', minHeight: 0, padding: '10px 0 10px 0' }}>
                <div style={{ padding: '0 10px' }}>
                    <div style={{ color: '#b6b6b6', fontSize: 13, margin: '8px 0 6px 6px', letterSpacing: 1 }}>
                        {loading ? 'Cargando...' : `Chats (${chats.length})`}
                    </div>
                </div>
                <ul style={{ listStyle: 'none', padding: '0 10px', margin: 0 }}>
                    {chats.filter(chat => {
                        const firstUserMsg = chat.mensajes.find(m => m.sender === 'user');
                        const title = firstUserMsg ? firstUserMsg.text.toLowerCase() : '';
                        return title.includes(search.toLowerCase());
                    }).map(chat => {
                        const firstUserMsg = chat.mensajes.find(m => m.sender === 'user');
                        const isSelected = selectedChat && selectedChat.chat_id === chat.chat_id;
                        return (
                            <li key={chat.chat_id}>
                                <button
                                    onClick={() => onSelectChat(chat)}
                                    style={chatItemStyle(isSelected)}
                                    onMouseOver={e => { if (!isSelected) e.target.style.background = '#232f4b'; }}
                                    onMouseOut={e => { if (!isSelected) e.target.style.background = 'transparent'; }}
                                >
                                    <span style={{ fontWeight: 500 }}>
                                        {firstUserMsg ? firstUserMsg.text.slice(0, 40) + (firstUserMsg.text.length > 32 ? '...' : '') : 'Chat nuevo'}
                                    </span>
                                    <button
                                        onClick={e => {
                                            e.stopPropagation();
                                            handleDelete(chat.chat_id);
                                        }}
                                        style={{
                                            marginLeft: 12,
                                            background: 'transparent',
                                            color: '#ff4d4f',
                                            border: 'none',
                                            cursor: 'pointer',
                                            fontWeight: 'bold',
                                            fontSize: 18,
                                            transition: 'color 0.2s',
                                        }}
                                        title="Eliminar chat"
                                    >
                                        ×
                                    </button>
                                </button>
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
                padding: '16px 18px',
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                background: '#23272f',
                fontSize: 15,
                color: '#b6b6b6',
                flexShrink: 0
            }}>
                <div style={{
                    width: 32,
                    height: 32,
                    borderRadius: '50%',
                    background: '#444654',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 700,
                    fontSize: 17,
                    color: '#fff',
                }}>
                    <FiUser size={18} />
                </div>
                <span style={{ fontWeight: 500 }}>{userEmail}</span>
            </div>
        </div>
    );
}

export default ChatHistory;