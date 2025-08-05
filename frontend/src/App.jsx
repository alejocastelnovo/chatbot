import React, { useState, useEffect } from 'react';
import { onAuthStateChanged } from 'firebase/auth';
import { auth } from './firebase';
import Login from './components/login';
import AssistantChat from './components/AssistantChat';
import ChatHistory from './components/chatHistory';
import Navbar from './components/navbar';
import Profile from './components/profile';
import './app.css';

function App() {
  const [user, setUser] = useState(null); // { user_id, email, idToken }
  const [selectedChat, setSelectedChat] = useState(null);
  const [refreshHistory, setRefreshHistory] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showProfile, setShowProfile] = useState(false);

  // Escuchar cambios en la autenticación
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        // Usuario autenticado
        try {
          const idToken = await firebaseUser.getIdToken();
          setUser({
            user_id: firebaseUser.uid,
            email: firebaseUser.email,
            idToken: idToken
          });
        } catch (error) {
          console.error('Error obteniendo token:', error);
          setUser(null);
        }
      } else {
        // Usuario no autenticado
        setUser(null);
        setSelectedChat(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const handleLogout = () => {
    setUser(null);
    setSelectedChat(null);
  };

  const handleNewChat = () => {
    setRefreshHistory(r => !r); // Cambia el valor para forzar el useEffect en ChatHistory
  };

  const handleChatCreated = () => {
    setRefreshHistory(r => !r); // Refrescar historial cuando se crea un chat
  };

  // Mostrar loading mientras se verifica la autenticación
  if (loading) {
    return (
      <div style={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#23272f',
        color: '#fff',
        fontSize: 18
      }}>
        Cargando...
      </div>
    );
  }

  if (!user) {
    return <Login onLogin={setUser} />;
  }

  return (
    <>
      <Navbar onLogout={handleLogout} />
      <div className="main-layout" style={{ paddingTop: 60, boxSizing: 'border-box', height: 'calc(100vh - 0px)' }}>
        <aside className="sidebar">
          <ChatHistory 
            userId={user.user_id} 
            userEmail={user.email} 
            onSelectChat={setSelectedChat} 
            selectedChat={selectedChat} 
            refresh={refreshHistory} 
            showProfile={showProfile}
            setShowProfile={setShowProfile}
            onChatCreated={handleChatCreated}
          />
        </aside>
        <main className="chatbox" style={{ display: 'flex', flexDirection: 'column', flex: 1, height: '100%' }}>
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
            <AssistantChat 
              userId={user.user_id} 
              selectedChat={selectedChat} 
              onNewChat={handleNewChat} 
              onChatCreated={handleChatCreated}
            />
          </div>
        </main>
      </div>
      {showProfile && <Profile onClose={() => setShowProfile(false)} />}
    </>
  );
}

export default App;