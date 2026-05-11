import React, { useState } from 'react';
import axios from 'axios';
import './Login.css';

const API_BASE_URL = 'http://localhost:8000';

const Login = ({ onLogin }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const res = await axios.post(`${API_BASE_URL}/api/admin/login/`, {
                username,
                password,
            });
            const { token, username: uname } = res.data;
            localStorage.setItem('admin_token', token);
            localStorage.setItem('admin_username', uname);
            onLogin(token, uname);
        } catch (err) {
            setError('Invalid username or password. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="login-wrapper">
                {/* Left decorative panel */}
                <div className="login-brand">
                    <div className="brand-content">
                        <div className="brand-icon">
                            <span className="brand-icon-ring">
                                <svg viewBox="0 0 80 80" fill="none">
                                    <circle cx="40" cy="40" r="36" stroke="currentColor" strokeWidth="2" opacity="0.3" />
                                    <circle cx="40" cy="40" r="24" stroke="currentColor" strokeWidth="2" opacity="0.5" />
                                    <circle cx="40" cy="40" r="12" stroke="currentColor" strokeWidth="2" />
                                    <circle cx="40" cy="28" r="3" fill="currentColor" />
                                    <circle cx="52" cy="40" r="3" fill="currentColor" />
                                    <circle cx="40" cy="52" r="3" fill="currentColor" />
                                    <circle cx="28" cy="40" r="3" fill="currentColor" />
                                </svg>
                            </span>
                        </div>
                        <h1 className="brand-title">Telecom AI</h1>
                        <p className="brand-subtitle">Admin Management Portal</p>
                        <div className="brand-features">
                            <div className="brand-feature">
                                <span className="feature-icon">📡</span>
                                <span>Manage Internet Packages</span>
                            </div>
                            <div className="brand-feature">
                                <span className="feature-icon">🗺️</span>
                                <span>Coverage Areas</span>
                            </div>
                            <div className="brand-feature">
                                <span className="feature-icon">❓</span>
                                <span>FAQ & Knowledge Base</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right login form panel */}
                <div className="login-panel">
                    <div className="login-panel-inner">
                        <div className="login-panel-header">
                            <h2>Welcome Back</h2>
                            <p>Sign in to manage your telecom data</p>
                        </div>

                        <form onSubmit={handleSubmit} className="login-form">
                            {error && (
                                <div className="login-error">
                                    <span className="error-icon">⚠️</span>
                                    {error}
                                </div>
                            )}

                            <div className="login-field">
                                <label htmlFor="username">
                                    <span className="field-icon">👤</span>
                                    Username
                                </label>
                                <div className="input-wrapper">
                                    <input
                                        id="username"
                                        type="text"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        placeholder="Enter your username"
                                        required
                                        autoFocus
                                        autoComplete="username"
                                    />
                                </div>
                            </div>

                            <div className="login-field">
                                <label htmlFor="password">
                                    <span className="field-icon">🔒</span>
                                    Password
                                </label>
                                <div className="input-wrapper">
                                    <input
                                        id="password"
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        placeholder="Enter your password"
                                        required
                                        autoComplete="current-password"
                                    />
                                </div>
                            </div>

                            <button type="submit" className="login-btn" disabled={loading}>
                                {loading ? (
                                    <span className="btn-loading">
                                        <span className="spinner"></span>
                                        Signing in...
                                    </span>
                                ) : (
                                    <span className="btn-text">
                                        Sign In
                                        <svg className="btn-arrow" width="20" height="20" viewBox="0 0 20 20" fill="none">
                                            <path d="M4 10H16M16 10L11 5M16 10L11 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                        </svg>
                                    </span>
                                )}
                            </button>
                        </form>

                        <div className="login-divider">
                            <span>Default Credentials</span>
                        </div>

                        <div className="login-credentials">
                            <div className="credential-row">
                                <span className="credential-label">Username</span>
                                <span className="credential-value">admin</span>
                            </div>
                            <div className="credential-row">
                                <span className="credential-label">Password</span>
                                <span className="credential-value">admin123</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;
