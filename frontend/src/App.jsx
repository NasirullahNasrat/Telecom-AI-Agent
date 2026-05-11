import React, { useState } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import ChatInterface from './components/ChatInterface';
import AdminPanel from './components/AdminPanel';
import Login from './components/Login';
import './App.css';

function App() {
    const navigate = useNavigate();
    const location = useLocation();

    // Authentication state
    const [token, setToken] = useState(localStorage.getItem('admin_token'));
    const [username, setUsername] = useState(localStorage.getItem('admin_username'));

    const handleLogin = (newToken, newUsername) => {
        setToken(newToken);
        setUsername(newUsername);
        navigate('/admin');
    };

    const handleLogout = () => {
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_username');
        setToken(null);
        setUsername(null);
        navigate('/');
    };

    const isAdminRoute = location.pathname.startsWith('/admin');

    return (
        <div className="App">
            {/* Only show nav bar on the chat page */}
            {location.pathname === '/' && (
                <div className="app-nav">
                    <button
                        className="app-nav-btn active"
                        onClick={() => navigate('/')}
                    >
                        💬 Chat Support
                    </button>
                    {token && (
                        <button
                            className="app-nav-btn"
                            onClick={() => navigate('/admin')}
                        >
                            ⚙️ Admin Panel
                        </button>
                    )}
                </div>
            )}

            <Routes>
                <Route path="/" element={<ChatInterface />} />
                <Route
                    path="/admin"
                    element={
                        token ? (
                            <AdminPanel
                                token={token}
                                username={username}
                                onLogout={handleLogout}
                            />
                        ) : (
                            <Login onLogin={handleLogin} />
                        )
                    }
                />
            </Routes>
        </div>
    );
}

export default App;
