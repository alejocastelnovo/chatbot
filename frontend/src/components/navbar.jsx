import React from 'react';
import { signOut } from 'firebase/auth';
import { auth } from '../firebase';
import optradingblanco from '../assets/optradingblanco.png';

function Navbar({ onLogout }) {
  const handleLogout = async () => {
    try {
      await signOut(auth);
      onLogout();
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
      // Fallback: cerrar sesión de todas formas
      onLogout();
    }
  };

  return (
    <nav style={{
      width: '100%',
      height: 60,
      background: '#23272f',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 32px',
      position: 'fixed',
      top: 0,
      left: 0,
      zIndex: 100,
      borderBottom: '1.5px solid #232526',
      boxSizing: 'border-box',
      boxShadow: '0 2px 8px rgba(30,46,30,0.10)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', height: '100%' }}>
        <img
          src={optradingblanco}
          alt="Logo MentorBot"
          style={{ height: 40, width: 'auto', marginRight: 12, objectFit: 'contain', filter: 'drop-shadow(0 1px 2px #0006)' }}
        />
        <span style={{ 
          color: '#fff', 
          fontSize: 18, 
          fontWeight: 'bold',
          marginLeft: 8
        }}>
          MentorBot IA
        </span>
      </div>
      <button
        onClick={handleLogout}
        style={{
          background: '#23283f',
          color: '#fff',
          borderRadius: 8,
          padding: '8px 20px',
          fontWeight: 'bold',
          fontSize: 16,
          border: '2px solid #232526',
          cursor: 'pointer',
          transition: 'border 0.2s, color 0.2s',
        }}
        onMouseOver={e => {
          e.target.style.border = '1.5px solid rgb(255, 0, 0)';
          e.target.style.color = 'rgb(255, 0, 0)';
        }}
        onMouseOut={e => {
          e.target.style.border = '2px solid #232526';
          e.target.style.color = '#fff';
        }}
      >
        Cerrar sesión
      </button>
    </nav>
  );
}

export default Navbar;