# 🤖 MentorBot IA - Asistente de Trading

Un chatbot inteligente especializado en análisis técnico, gestión de riesgo y estrategias de inversión para acciones, ETFs y criptomonedas.

## 🚀 Características

- **Autenticación segura** con Firebase Auth
- **Roles de usuario** (Free/Premium)
- **Chat inteligente** con OpenAI GPT-4
- **Historial de conversaciones** persistente
- **Control de acceso** basado en roles
- **Base de datos** Firestore
- **UI moderna** y responsive

## 🛠️ Tecnologías

### Frontend
- React 19 + Vite
- Firebase Auth & Firestore
- React Markdown
- CSS-in-JS

### Backend
- Python Flask
- Firebase Admin SDK
- OpenAI API
- Firestore Database

## 📦 Instalación

### Prerrequisitos
- Node.js 18+
- Python 3.11+
- Cuenta de Firebase
- API Key de OpenAI

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
# Configurar variables de entorno
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Configurar variables de entorno
python app.py
```

## 🔧 Configuración

### Variables de entorno Frontend (.env)
```env
VITE_FIREBASE_API_KEY=tu_api_key
VITE_FIREBASE_AUTH_DOMAIN=tu_proyecto.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=tu_proyecto_id
VITE_FIREBASE_STORAGE_BUCKET=tu_proyecto.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=tu_sender_id
VITE_FIREBASE_APP_ID=tu_app_id
VITE_BACKEND_URL=http://localhost:5000
```

### Variables de entorno Backend (.env)
```env
OPENAI_API_KEY=tu_api_key_de_openai
FIREBASE_PROJECT_ID=tu_proyecto_id
FIREBASE_PRIVATE_KEY_ID=tu_private_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=tu_client_email
FIREBASE_CLIENT_ID=tu_client_id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=tu_cert_url
SECRET_KEY=tu_secret_key_super_segura
```

## 🚀 Deploy

### Frontend (Vercel)
```bash
cd frontend
npm run build
# Subir a Vercel
```

### Backend (Railway)
```bash
# Conectar repositorio a Railway
# Configurar variables de entorno
```

## 📁 Estructura del proyecto

```
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat.jsx
│   │   │   ├── chatHistory.jsx
│   │   │   ├── login.jsx
│   │   │   └── navbar.jsx
│   │   ├── firebase.js
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── app.py
│   ├── firebase_config.py
│   ├── requirements.txt
│   └── .env
└── README.md
```

## 🔐 Seguridad

- Autenticación JWT con Firebase
- Verificación de roles en backend
- CORS configurado
- Variables de entorno seguras

## 📝 Licencia

MIT License

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AltaFeature`)
3. Commit tus cambios (`git commit -m 'Agregue alta Feature'`)
4. Push a la rama (`git push origin feature/AltaFeature`)
5. Abre un Pull Request

## 📞 Soporte

Para soporte, email: castelnovo12@gmail.com