import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './AdminPanel.css';

const API_BASE_URL = 'http://localhost:8000';

const AdminPanel = ({ token, username, onLogout }) => {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [stats, setStats] = useState(null);
    const [packages, setPackages] = useState([]);
    const [coverageAreas, setCoverageAreas] = useState([]);
    const [faqs, setFaqs] = useState([]);
    const [kbEntries, setKbEntries] = useState([]);
    const [loading, setLoading] = useState(false);
    const [editingItem, setEditingItem] = useState(null);
    const [showForm, setShowForm] = useState(false);

    // Settings state
    const [settings, setSettings] = useState({
        ai_provider: 'mock',
        deepseek_api_key: '',
        openai_api_key: '',
    });
    // Track whether a key is already stored on the server (to show placeholder)
    const [hasKey, setHasKey] = useState({ deepseek: false, openai: false });
    const [settingsSaving, setSettingsSaving] = useState(false);
    const [settingsMessage, setSettingsMessage] = useState({ type: '', text: '' });

    // Create axios instance with auth header
    const api = axios.create({
        baseURL: API_BASE_URL,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${token}`,
        },
    });

    // Form state - use unique prefixes to avoid duplicate keys
    const emptyForm = {
        // InternetPackage
        name_en: '', name_dari: '', name_pashto: '',
        price_afn: '', data_amount: '', validity_days: '',
        description_en: '', description_dari: '', description_pashto: '',
        activation_code: '', is_active: true,
        // CoverageArea
        province: '', city: '', coverage_type: '4g', status: 'active',
        notes_en: '', notes_dari: '', notes_pashto: '',
        // FAQ
        faq_category: 'other', faq_question_en: '', faq_question_dari: '', faq_question_pashto: '',
        faq_answer_en: '', faq_answer_dari: '', faq_answer_pashto: '', is_published: true,
        // KnowledgeBase
        kb_question_en: '', kb_question_dari: '', kb_question_pashto: '',
        kb_answer_en: '', kb_answer_dari: '', kb_answer_pashto: '',
        kb_category: 'balance',
    };
    const [formData, setFormData] = useState({ ...emptyForm });

    const tabs = [
        { id: 'dashboard', label: 'Dashboard', icon: '📊' },
        { id: 'packages', label: 'Internet Packages', icon: '📦' },
        { id: 'coverage', label: 'Coverage Areas', icon: '📡' },
        { id: 'faqs', label: 'Support FAQs', icon: '❓' },
        { id: 'knowledge', label: 'Knowledge Base', icon: '📚' },
        { id: 'settings', label: 'Settings', icon: '⚙️' },
    ];

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            if (activeTab === 'dashboard') {
                const res = await api.get('/api/admin/stats/');
                setStats(res.data);
            } else if (activeTab === 'packages') {
                const res = await api.get('/api/admin/packages/');
                setPackages(res.data);
            } else if (activeTab === 'coverage') {
                const res = await api.get('/api/admin/coverage/');
                setCoverageAreas(res.data);
            } else if (activeTab === 'faqs') {
                const res = await api.get('/api/admin/faqs/');
                setFaqs(res.data);
            } else if (activeTab === 'knowledge') {
                const res = await api.get('/api/admin/knowledge-base/');
                setKbEntries(res.data);
            } else if (activeTab === 'settings') {
                const res = await api.get('/api/admin/settings/');
                const data = res.data;
                // Detect if a key value is masked (contains asterisks) — if so,
                // don't put it in the input field, just mark it as existing
                const dsKey = data.deepseek_api_key || '';
                const oaKey = data.openai_api_key || '';
                const hasDsKey = dsKey.length > 0 && dsKey.includes('*');
                const hasOaKey = oaKey.length > 0 && oaKey.includes('*');
                setHasKey({ deepseek: hasDsKey, openai: hasOaKey });
                setSettings(prev => ({
                    ...prev,
                    ai_provider: data.ai_provider || prev.ai_provider,
                    // Only set actual (non-masked) values into the input
                    deepseek_api_key: hasDsKey ? '' : dsKey,
                    openai_api_key: hasOaKey ? '' : oaKey,
                }));
            }
        } catch (err) {
            console.error('Fetch error:', err);
            if (err.response?.status === 401) {
                onLogout();
            }
        } finally {
            setLoading(false);
        }
    }, [activeTab, token, onLogout]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const resetForm = () => {
        setFormData({ ...emptyForm });
        setEditingItem(null);
        setShowForm(false);
    };

    const startEdit = (item) => {
        // Map API field names to prefixed form field names for FAQ and KB
        const mapped = { ...item };
        if (activeTab === 'faqs') {
            mapped.faq_category = item.category;
            mapped.faq_question_en = item.question_en;
            mapped.faq_question_dari = item.question_dari;
            mapped.faq_question_pashto = item.question_pashto;
            mapped.faq_answer_en = item.answer_en;
            mapped.faq_answer_dari = item.answer_dari;
            mapped.faq_answer_pashto = item.answer_pashto;
        }
        if (activeTab === 'knowledge') {
            mapped.kb_category = item.category;
            mapped.kb_question_en = item.question_en;
            mapped.kb_question_dari = item.question_dari;
            mapped.kb_question_pashto = item.question_pashto;
            mapped.kb_answer_en = item.answer_en;
            mapped.kb_answer_dari = item.answer_dari;
            mapped.kb_answer_pashto = item.answer_pashto;
        }
        setFormData(mapped);
        setEditingItem(item);
        setShowForm(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            let url, method;

            if (activeTab === 'packages') {
                url = editingItem
                    ? `/api/admin/packages/${editingItem.id}/`
                    : `/api/admin/packages/`;
                method = editingItem ? 'put' : 'post';
            } else if (activeTab === 'coverage') {
                url = editingItem
                    ? `/api/admin/coverage/${editingItem.id}/`
                    : `/api/admin/coverage/`;
                method = editingItem ? 'put' : 'post';
            } else if (activeTab === 'faqs') {
                url = editingItem
                    ? `/api/admin/faqs/${editingItem.id}/`
                    : `/api/admin/faqs/`;
                method = editingItem ? 'put' : 'post';
            } else if (activeTab === 'knowledge') {
                url = editingItem
                    ? `/api/admin/knowledge-base/${editingItem.id}/`
                    : `/api/admin/knowledge-base/`;
                method = editingItem ? 'put' : 'post';
            }

            // Map form fields for each entity type
            let payload = { ...formData };
            if (activeTab === 'packages') {
                payload.price_afn = parseFloat(payload.price_afn) || 0;
                payload.validity_days = parseInt(payload.validity_days) || 0;
            } else if (activeTab === 'faqs') {
                // Map prefixed form fields back to API field names
                payload = {
                    category: formData.faq_category,
                    question_en: formData.faq_question_en,
                    question_dari: formData.faq_question_dari,
                    question_pashto: formData.faq_question_pashto,
                    answer_en: formData.faq_answer_en,
                    answer_dari: formData.faq_answer_dari,
                    answer_pashto: formData.faq_answer_pashto,
                    is_published: formData.is_published,
                };
            } else if (activeTab === 'knowledge') {
                // Map prefixed form fields back to API field names
                payload = {
                    category: formData.kb_category,
                    question_en: formData.kb_question_en,
                    question_dari: formData.kb_question_dari,
                    question_pashto: formData.kb_question_pashto,
                    answer_en: formData.kb_answer_en,
                    answer_dari: formData.kb_answer_dari,
                    answer_pashto: formData.kb_answer_pashto,
                };
            }

            if (method === 'put') {
                await api.put(url, payload);
            } else {
                await api.post(url, payload);
            }

            resetForm();
            fetchData();
        } catch (err) {
            console.error('Submit error:', err);
            if (err.response?.status === 401) {
                onLogout();
            } else {
                alert('Error saving data. Check console for details.');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Are you sure you want to delete this item?')) return;
        setLoading(true);
        try {
            let url;
            if (activeTab === 'packages') url = `/api/admin/packages/${id}/`;
            else if (activeTab === 'coverage') url = `/api/admin/coverage/${id}/`;
            else if (activeTab === 'faqs') url = `/api/admin/faqs/${id}/`;
            else if (activeTab === 'knowledge') url = `/api/admin/knowledge-base/${id}/`;

            await api.delete(url);
            fetchData();
        } catch (err) {
            console.error('Delete error:', err);
            if (err.response?.status === 401) {
                onLogout();
            } else {
                alert('Error deleting item.');
            }
        } finally {
            setLoading(false);
        }
    };

    // Track which keys have been modified by the user (vs loaded from server as masked)
    const [keyModified, setKeyModified] = useState({ deepseek: false, openai: false });

    // Settings handlers
    const handleSettingsChange = (e) => {
        const { name, value } = e.target;
        setSettings(prev => ({ ...prev, [name]: value }));
        setSettingsMessage({ type: '', text: '' });
        // Mark the corresponding key as modified by user
        if (name === 'deepseek_api_key') setKeyModified(prev => ({ ...prev, deepseek: true }));
        if (name === 'openai_api_key') setKeyModified(prev => ({ ...prev, openai: true }));
    };

    const handleSaveSettings = async () => {
        setSettingsSaving(true);
        setSettingsMessage({ type: '', text: '' });
        try {
            // Save provider first
            await api.post('/api/admin/settings/', {
                key: 'ai_provider',
                value: settings.ai_provider,
            });

            // Save DeepSeek API key (always send, even if empty — to allow clearing)
            if (keyModified.deepseek) {
                await api.post('/api/admin/settings/', {
                    key: 'deepseek_api_key',
                    value: settings.deepseek_api_key || '',
                });
            }

            // Save OpenAI API key (always send, even if empty — to allow clearing)
            if (keyModified.openai) {
                await api.post('/api/admin/settings/', {
                    key: 'openai_api_key',
                    value: settings.openai_api_key || '',
                });
            }

            setSettingsMessage({ type: 'success', text: 'Settings saved successfully! AI service has been updated.' });
            // Refresh settings to get masked values
            const res = await api.get('/api/admin/settings/');
            const data = res.data;
            const dsKey = data.deepseek_api_key || '';
            const oaKey = data.openai_api_key || '';
            const hasDsKey = dsKey.length > 0 && dsKey.includes('*');
            const hasOaKey = oaKey.length > 0 && oaKey.includes('*');
            setHasKey({ deepseek: hasDsKey, openai: hasOaKey });
            setSettings(prev => ({
                ...prev,
                ai_provider: data.ai_provider || prev.ai_provider,
                deepseek_api_key: hasDsKey ? '' : dsKey,
                openai_api_key: hasOaKey ? '' : oaKey,
            }));
            // Reset modification flags after successful save
            setKeyModified({ deepseek: false, openai: false });
        } catch (err) {
            console.error('Settings save error:', err);
            const msg = err.response?.data?.error || 'Failed to save settings. Check console for details.';
            setSettingsMessage({ type: 'error', text: msg });
        } finally {
            setSettingsSaving(false);
        }
    };

    const renderSettings = () => (
        <div className="settings-container">
            <div className="settings-header">
                <h3>⚙️ AI Service Settings</h3>
                <p>Configure your AI provider and API keys. Changes take effect immediately.</p>
            </div>

            {settingsMessage.text && (
                <div className={`settings-message settings-message-${settingsMessage.type}`}>
                    {settingsMessage.type === 'success' ? '✅ ' : '❌ '}
                    {settingsMessage.text}
                </div>
            )}

            <div className="settings-card">
                <div className="settings-card-header">
                    <span className="settings-card-icon">🤖</span>
                    <div>
                        <h4>AI Provider</h4>
                        <p>Select which AI service to use for generating responses</p>
                    </div>
                </div>
                <div className="settings-field">
                    <label>Provider</label>
                    <select
                        name="ai_provider"
                        value={settings.ai_provider || 'mock'}
                        onChange={handleSettingsChange}
                        className="settings-select"
                    >
                        <option value="mock">Mock AI (No API key needed - uses RAG data)</option>
                        <option value="deepseek">DeepSeek API</option>
                        <option value="openai">OpenAI API</option>
                    </select>
                </div>
            </div>

            {(settings.ai_provider === 'deepseek' || settings.ai_provider === 'openai') && (
                <div className="settings-card">
                    <div className="settings-card-header">
                        <span className="settings-card-icon">🔑</span>
                        <div>
                            <h4>API Key</h4>
                            <p>Enter your API key for {settings.ai_provider === 'deepseek' ? 'DeepSeek' : 'OpenAI'}</p>
                        </div>
                    </div>
                    <div className="settings-field">
                        <label>API Key</label>
                        <input
                            type="password"
                            name={settings.ai_provider === 'deepseek' ? 'deepseek_api_key' : 'openai_api_key'}
                            value={settings.ai_provider === 'deepseek' ? (settings.deepseek_api_key || '') : (settings.openai_api_key || '')}
                            onChange={handleSettingsChange}
                            placeholder={
                                settings.ai_provider === 'deepseek'
                                    ? (hasKey.deepseek ? '•••••••• (key saved — leave empty to keep, type new value to change)' : 'Enter your DeepSeek API key')
                                    : (hasKey.openai ? '•••••••• (key saved — leave empty to keep, type new value to change)' : 'Enter your OpenAI API key')
                            }
                            className="settings-input"
                        />
                        <small className="settings-hint">
                            Your key is stored securely in the database and never exposed.
                            {settings.ai_provider === 'deepseek' && ' Get a key at platform.deepseek.com'}
                            {settings.ai_provider === 'openai' && ' Get a key at platform.openai.com'}
                        </small>
                    </div>
                </div>
            )}

            <div className="settings-card">
                <div className="settings-card-header">
                    <span className="settings-card-icon">📊</span>
                    <div>
                        <h4>Current Status</h4>
                        <p>Current AI service status</p>
                    </div>
                </div>
                <div className="settings-status">
                    <div className="status-item">
                        <span className="status-label">Provider:</span>
                        <span className={`status-value status-${settings.ai_provider}`}>
                            {settings.ai_provider === 'mock' ? '🟡 Mock AI' :
                             settings.ai_provider === 'deepseek' ? '🟢 DeepSeek' :
                             settings.ai_provider === 'openai' ? '🟢 OpenAI' : '🔴 Not configured'}
                        </span>
                    </div>
                </div>
            </div>

            <div className="settings-actions">
                <button
                    className="btn-save-settings"
                    onClick={handleSaveSettings}
                    disabled={settingsSaving}
                >
                    {settingsSaving ? '⏳ Saving...' : '💾 Save Settings'}
                </button>
            </div>
        </div>
    );

    const renderDashboard = () => (
        <div className="dashboard-grid">
            <div className="stat-card">
                <span className="stat-icon">💬</span>
                <div className="stat-info">
                    <h3>{stats?.total_conversations || 0}</h3>
                    <p>Total Conversations</p>
                </div>
            </div>
            <div className="stat-card">
                <span className="stat-icon">✉️</span>
                <div className="stat-info">
                    <h3>{stats?.total_messages || 0}</h3>
                    <p>Total Messages</p>
                </div>
            </div>
            <div className="stat-card">
                <span className="stat-icon">📦</span>
                <div className="stat-info">
                    <h3>{stats?.active_packages || 0} / {stats?.total_packages || 0}</h3>
                    <p>Active / Total Packages</p>
                </div>
            </div>
            <div className="stat-card">
                <span className="stat-icon">📡</span>
                <div className="stat-info">
                    <h3>{stats?.active_coverage_areas || 0} / {stats?.total_coverage_areas || 0}</h3>
                    <p>Active / Total Coverage Areas</p>
                </div>
            </div>
            <div className="stat-card">
                <span className="stat-icon">❓</span>
                <div className="stat-info">
                    <h3>{stats?.published_faqs || 0} / {stats?.total_faqs || 0}</h3>
                    <p>Published / Total FAQs</p>
                </div>
            </div>
            <div className="stat-card">
                <span className="stat-icon">📚</span>
                <div className="stat-info">
                    <h3>{stats?.total_kb_entries || 0}</h3>
                    <p>Knowledge Base Entries</p>
                </div>
            </div>
        </div>
    );

    const renderForm = () => {
        const isPackage = activeTab === 'packages';
        const isCoverage = activeTab === 'coverage';
        const isFaq = activeTab === 'faqs';
        const isKb = activeTab === 'knowledge';

        return (
            <div className="form-overlay">
                <div className="form-modal">
                    <div className="form-header">
                        <h3>{editingItem ? 'Edit' : 'Add'} {tabs.find(t => t.id === activeTab)?.label}</h3>
                        <button className="btn-close" onClick={resetForm}>✕</button>
                    </div>
                    <form onSubmit={handleSubmit} className="admin-form">
                        <div className="form-grid">
                            {isPackage && (
                                <>
                                    <div className="form-group">
                                        <label>Name (English) *</label>
                                        <input name="name_en" value={formData.name_en} onChange={handleInputChange} required />
                                    </div>
                                    <div className="form-group">
                                        <label>Name (Dari)</label>
                                        <input name="name_dari" value={formData.name_dari} onChange={handleInputChange} />
                                    </div>
                                    <div className="form-group">
                                        <label>Name (Pashto)</label>
                                        <input name="name_pashto" value={formData.name_pashto} onChange={handleInputChange} />
                                    </div>
                                    <div className="form-group">
                                        <label>Price (AFN) *</label>
                                        <input type="number" name="price_afn" value={formData.price_afn} onChange={handleInputChange} required />
                                    </div>
                                    <div className="form-group">
                                        <label>Data Amount *</label>
                                        <input name="data_amount" value={formData.data_amount} onChange={handleInputChange} placeholder="e.g. 1GB, 3GB, 10GB" required />
                                    </div>
                                    <div className="form-group">
                                        <label>Validity (Days) *</label>
                                        <input type="number" name="validity_days" value={formData.validity_days} onChange={handleInputChange} required />
                                    </div>
                                    <div className="form-group">
                                        <label>Activation Code</label>
                                        <input name="activation_code" value={formData.activation_code} onChange={handleInputChange} placeholder="e.g. *123*1#" />
                                    </div>
                                    <div className="form-group">
                                        <label>Description (English)</label>
                                        <textarea name="description_en" value={formData.description_en} onChange={handleInputChange} rows="2" />
                                    </div>
                                    <div className="form-group">
                                        <label>Description (Dari)</label>
                                        <textarea name="description_dari" value={formData.description_dari} onChange={handleInputChange} rows="2" />
                                    </div>
                                    <div className="form-group">
                                        <label>Description (Pashto)</label>
                                        <textarea name="description_pashto" value={formData.description_pashto} onChange={handleInputChange} rows="2" />
                                    </div>
                                    <div className="form-group checkbox-group">
                                        <label>
                                            <input type="checkbox" name="is_active" checked={formData.is_active} onChange={handleInputChange} />
                                            Active
                                        </label>
                                    </div>
                                </>
                            )}

                            {isCoverage && (
                                <>
                                    <div className="form-group">
                                        <label>Province *</label>
                                        <input name="province" value={formData.province} onChange={handleInputChange} required />
                                    </div>
                                    <div className="form-group">
                                        <label>City *</label>
                                        <input name="city" value={formData.city} onChange={handleInputChange} required />
                                    </div>
                                    <div className="form-group">
                                        <label>Coverage Type</label>
                                        <select name="coverage_type" value={formData.coverage_type} onChange={handleInputChange}>
                                            <option value="2g">2G</option>
                                            <option value="3g">3G</option>
                                            <option value="4g">4G</option>
                                            <option value="5g">5G</option>
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label>Status</label>
                                        <select name="status" value={formData.status} onChange={handleInputChange}>
                                            <option value="active">Active</option>
                                            <option value="planned">Planned</option>
                                            <option value="maintenance">Under Maintenance</option>
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label>Notes (English)</label>
                                        <textarea name="notes_en" value={formData.notes_en} onChange={handleInputChange} rows="2" />
                                    </div>
                                    <div className="form-group">
                                        <label>Notes (Dari)</label>
                                        <textarea name="notes_dari" value={formData.notes_dari} onChange={handleInputChange} rows="2" />
                                    </div>
                                    <div className="form-group">
                                        <label>Notes (Pashto)</label>
                                        <textarea name="notes_pashto" value={formData.notes_pashto} onChange={handleInputChange} rows="2" />
                                    </div>
                                </>
                            )}

                            {(isFaq || isKb) && (
                                <>
                                    {isFaq && (
                                        <div className="form-group">
                                            <label>Category</label>
                                            <select name="faq_category" value={formData.faq_category} onChange={handleInputChange}>
                                                <option value="network">Network Issues</option>
                                                <option value="device">Device Settings</option>
                                                <option value="billing">Billing & Payments</option>
                                                <option value="account">Account Management</option>
                                                <option value="other">Other</option>
                                            </select>
                                        </div>
                                    )}
                                    {isKb && (
                                        <div className="form-group">
                                            <label>Category</label>
                                            <select name="kb_category" value={formData.kb_category} onChange={handleInputChange}>
                                                <option value="balance">Balance & Payments</option>
                                                <option value="packages">Internet Packages</option>
                                                <option value="coverage">Network Coverage</option>
                                                <option value="sim">SIM Registration</option>
                                                <option value="technical">Technical Support</option>
                                            </select>
                                        </div>
                                    )}
                                    <div className="form-group">
                                        <label>Question (English) *</label>
                                        <textarea name={isFaq ? "faq_question_en" : "kb_question_en"} value={isFaq ? formData.faq_question_en : formData.kb_question_en} onChange={handleInputChange} required rows="2" />
                                    </div>
                                    <div className="form-group">
                                        <label>Question (Dari)</label>
                                        <textarea name={isFaq ? "faq_question_dari" : "kb_question_dari"} value={isFaq ? formData.faq_question_dari : formData.kb_question_dari} onChange={handleInputChange} rows="2" />
                                    </div>
                                    <div className="form-group">
                                        <label>Question (Pashto)</label>
                                        <textarea name={isFaq ? "faq_question_pashto" : "kb_question_pashto"} value={isFaq ? formData.faq_question_pashto : formData.kb_question_pashto} onChange={handleInputChange} rows="2" />
                                    </div>
                                    <div className="form-group full-width">
                                        <label>Answer (English) *</label>
                                        <textarea name={isFaq ? "faq_answer_en" : "kb_answer_en"} value={isFaq ? formData.faq_answer_en : formData.kb_answer_en} onChange={handleInputChange} required rows="4" />
                                    </div>
                                    <div className="form-group full-width">
                                        <label>Answer (Dari)</label>
                                        <textarea name={isFaq ? "faq_answer_dari" : "kb_answer_dari"} value={isFaq ? formData.faq_answer_dari : formData.kb_answer_dari} onChange={handleInputChange} rows="4" />
                                    </div>
                                    <div className="form-group full-width">
                                        <label>Answer (Pashto)</label>
                                        <textarea name={isFaq ? "faq_answer_pashto" : "kb_answer_pashto"} value={isFaq ? formData.faq_answer_pashto : formData.kb_answer_pashto} onChange={handleInputChange} rows="4" />
                                    </div>
                                    {isFaq && (
                                        <div className="form-group checkbox-group">
                                            <label>
                                                <input type="checkbox" name="is_published" checked={formData.is_published} onChange={handleInputChange} />
                                                Published
                                            </label>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                        <div className="form-actions">
                            <button type="submit" className="btn-save" disabled={loading}>
                                {loading ? 'Saving...' : (editingItem ? 'Update' : 'Create')}
                            </button>
                            <button type="button" className="btn-cancel" onClick={resetForm}>Cancel</button>
                        </div>
                    </form>
                </div>
            </div>
        );
    };

    const renderTable = () => {
        const getItems = () => {
            if (activeTab === 'packages') return packages;
            if (activeTab === 'coverage') return coverageAreas;
            if (activeTab === 'faqs') return faqs;
            if (activeTab === 'knowledge') return kbEntries;
            return [];
        };

        const items = getItems();

        const renderRow = (item, idx) => {
            if (activeTab === 'packages') {
                return (
                    <tr key={item.id || idx}>
                        <td>{item.name_en}</td>
                        <td>{item.price_afn} AFN</td>
                        <td>{item.data_amount}</td>
                        <td>{item.validity_days} days</td>
                        <td>{item.activation_code || '-'}</td>
                        <td><span className={`badge ${item.is_active ? 'badge-active' : 'badge-inactive'}`}>{item.is_active ? 'Active' : 'Inactive'}</span></td>
                        <td className="actions-cell">
                            <button className="btn-edit" onClick={() => startEdit(item)}>Edit</button>
                            <button className="btn-delete" onClick={() => handleDelete(item.id)}>Delete</button>
                        </td>
                    </tr>
                );
            } else if (activeTab === 'coverage') {
                return (
                    <tr key={item.id || idx}>
                        <td>{item.province}</td>
                        <td>{item.city}</td>
                        <td><span className="badge badge-coverage">{item.coverage_type?.toUpperCase()}</span></td>
                        <td><span className={`badge badge-${item.status}`}>{item.status}</span></td>
                        <td className="actions-cell">
                            <button className="btn-edit" onClick={() => startEdit(item)}>Edit</button>
                            <button className="btn-delete" onClick={() => handleDelete(item.id)}>Delete</button>
                        </td>
                    </tr>
                );
            } else if (activeTab === 'faqs') {
                return (
                    <tr key={item.id || idx}>
                        <td><span className="badge badge-faq">{item.category}</span></td>
                        <td className="text-cell">{item.question_en?.substring(0, 60)}...</td>
                        <td><span className={`badge ${item.is_published ? 'badge-active' : 'badge-inactive'}`}>{item.is_published ? 'Published' : 'Draft'}</span></td>
                        <td className="actions-cell">
                            <button className="btn-edit" onClick={() => startEdit(item)}>Edit</button>
                            <button className="btn-delete" onClick={() => handleDelete(item.id)}>Delete</button>
                        </td>
                    </tr>
                );
            } else if (activeTab === 'knowledge') {
                return (
                    <tr key={item.id || idx}>
                        <td><span className="badge badge-kb">{item.category}</span></td>
                        <td className="text-cell">{item.question_en?.substring(0, 60)}...</td>
                        <td className="actions-cell">
                            <button className="btn-edit" onClick={() => startEdit(item)}>Edit</button>
                            <button className="btn-delete" onClick={() => handleDelete(item.id)}>Delete</button>
                        </td>
                    </tr>
                );
            }
            return null;
        };

        const getHeaders = () => {
            if (activeTab === 'packages') return ['Name', 'Price', 'Data', 'Validity', 'Activation Code', 'Status', 'Actions'];
            if (activeTab === 'coverage') return ['Province', 'City', 'Type', 'Status', 'Actions'];
            if (activeTab === 'faqs') return ['Category', 'Question', 'Status', 'Actions'];
            if (activeTab === 'knowledge') return ['Category', 'Question', 'Actions'];
            return [];
        };

        return (
            <div className="table-container">
                <div className="table-header">
                    <h3>{tabs.find(t => t.id === activeTab)?.label}</h3>
                    <button className="btn-add" onClick={() => setShowForm(true)}>+ Add New</button>
                </div>
                {items.length === 0 ? (
                    <div className="empty-state">
                        <p>No data found. Click "Add New" to create the first entry.</p>
                    </div>
                ) : (
                    <div className="table-wrapper">
                        <table className="data-table">
                            <thead>
                                <tr>{getHeaders().map((h, i) => <th key={i}>{h}</th>)}</tr>
                            </thead>
                            <tbody>
                                {items.map((item, idx) => renderRow(item, idx))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="admin-panel">
            <div className="admin-sidebar">
                <div className="admin-logo">
                    <h2>⚙️ Admin Panel</h2>
                    <p>Telecom Data Management</p>
                </div>
                <nav className="admin-nav">
                    {tabs.map(tab => (
                        <button
                            key={tab.id}
                            className={`nav-btn ${activeTab === tab.id ? 'active' : ''}`}
                            onClick={() => { setActiveTab(tab.id); resetForm(); }}
                        >
                            <span className="nav-icon">{tab.icon}</span>
                            <span className="nav-label">{tab.label}</span>
                        </button>
                    ))}
                </nav>
                <div className="admin-sidebar-footer">
                    <div className="admin-user">
                        <span className="admin-user-icon">👤</span>
                        <span className="admin-user-name">{username}</span>
                    </div>
                    <button className="btn-logout" onClick={onLogout}>
                        🚪 Logout
                    </button>
                </div>
            </div>
            <div className="admin-content">
                {loading && <div className="loading-bar"></div>}
                {activeTab === 'dashboard' && renderDashboard()}
                {activeTab === 'settings' && renderSettings()}
                {activeTab !== 'dashboard' && activeTab !== 'settings' && renderTable()}
                {showForm && renderForm()}
            </div>
        </div>
    );
};

export default AdminPanel;
