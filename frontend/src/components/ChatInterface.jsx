import React, { useState, useRef, useEffect, useCallback } from 'react';
import axios from 'axios';
import './ChatInterface.css';

const API_BASE_URL = 'http://localhost:8000';

const ChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [showVisualizer, setShowVisualizer] = useState(false);
    const [voiceMode, setVoiceMode] = useState(false);
    const [selectedLanguage, setSelectedLanguage] = useState('en');
    const [sessionId] = useState(() => `session_${Date.now()}`);
    const [isLoading, setIsLoading] = useState(false);
    const [apiTtsAvailable, setApiTtsAvailable] = useState(false);
    const messagesEndRef = useRef(null);
    const recognitionRef = useRef(null);
    const synthRef = useRef(window.speechSynthesis);
    const visualizerTimerRef = useRef(null);

    const languages = [
        { code: 'en', name: 'English', flag: '🇺🇸' },
        { code: 'fa', name: 'Dari', flag: '🇦🇫' },
        { code: 'ps', name: 'Pashto', flag: '🇦🇫' }
    ];

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Check if backend TTS API is available (OpenAI or DeepSeek configured)
    useEffect(() => {
        const checkTtsAvailability = async () => {
            try {
                const res = await axios.get(`${API_BASE_URL}/api/tts/status/`);
                if (res.data.available) {
                    setApiTtsAvailable(true);
                    console.log('API-based TTS is available:', res.data.provider);
                }
            } catch (err) {
                console.log('API-based TTS not available, using browser TTS');
                setApiTtsAvailable(false);
            }
        };
        checkTtsAvailability();
    }, []);

    // Get voice language code for speech synthesis
    const getVoiceLang = (lang) => {
        const map = { 'en': 'en-US', 'fa': 'fa-IR', 'ps': 'ps-AF' };
        return map[lang] || 'en-US';
    };

    // Find the best available voice for a given language
    const findBestVoice = useCallback((lang, voices) => {
        if (!voices || voices.length === 0) return null;
        
        const langMap = { 'en': 'en', 'fa': 'fa', 'ps': 'ps' };
        const targetLang = langMap[lang] || 'en';
        
        // Strategy 1: Exact match on language code (e.g., 'fa' matches 'fa-IR', 'fa-AF')
        const exactMatch = voices.find(v => v.lang.startsWith(targetLang));
        if (exactMatch) return exactMatch;
        
        // Strategy 2: For Dari (fa), try Arabic (ar) voices as they sound closer
        if (targetLang === 'fa') {
            const arabicVoice = voices.find(v => v.lang.startsWith('ar'));
            if (arabicVoice) return arabicVoice;
        }
        
        // Strategy 3: For Pashto (ps), try Urdu (ur) or Hindi (hi) voices
        if (targetLang === 'ps') {
            const urduVoice = voices.find(v => v.lang.startsWith('ur'));
            if (urduVoice) return urduVoice;
            const hindiVoice = voices.find(v => v.lang.startsWith('hi'));
            if (hindiVoice) return hindiVoice;
        }
        
        // Strategy 4: Any non-English voice as last resort for non-English
        if (targetLang !== 'en') {
            const nonEnglishVoice = voices.find(v => !v.lang.startsWith('en'));
            if (nonEnglishVoice) return nonEnglishVoice;
        }
        
        return null;
    }, []);

    // Speak using the backend API-based TTS (OpenAI TTS)
    const speakViaApi = useCallback(async (text, lang) => {
        try {
            const response = await axios.post(`${API_BASE_URL}/api/tts/speak/`, {
                text: text,
                language: lang
            }, { responseType: 'blob' });
            
            const audioBlob = new Blob([response.data], { type: 'audio/mpeg' });
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            
            audio.onplay = () => {
                setIsSpeaking(true);
                setShowVisualizer(true);
            };
            
            audio.onended = () => {
                setIsSpeaking(false);
                URL.revokeObjectURL(audioUrl);
                if (visualizerTimerRef.current) {
                    clearTimeout(visualizerTimerRef.current);
                }
                visualizerTimerRef.current = setTimeout(() => {
                    setShowVisualizer(false);
                }, 3000);
            };
            
            audio.onerror = () => {
                console.error('API TTS playback error');
                setIsSpeaking(false);
                URL.revokeObjectURL(audioUrl);
                if (visualizerTimerRef.current) {
                    clearTimeout(visualizerTimerRef.current);
                }
                visualizerTimerRef.current = setTimeout(() => {
                    setShowVisualizer(false);
                }, 1000);
            };
            
            audio.play().catch(err => {
                console.error('Audio play failed:', err);
                setIsSpeaking(false);
            });
        } catch (err) {
            console.error('API TTS failed, falling back to browser TTS:', err);
            // Fall back to browser TTS
            speakViaBrowser(text, lang);
        }
    }, []);

    // Speak using browser's SpeechSynthesis API
    const speakViaBrowser = useCallback((text, lang) => {
        if (!synthRef.current) return;
        
        // Cancel any ongoing speech
        synthRef.current.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = getVoiceLang(lang);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        // Try to find the best matching voice for the language
        const voices = synthRef.current.getVoices();
        const bestVoice = findBestVoice(lang, voices);
        if (bestVoice) {
            utterance.voice = bestVoice;
            console.log(`Using browser voice: ${bestVoice.name} (${bestVoice.lang}) for language: ${lang}`);
        } else {
            console.warn(`No suitable voice found for language: ${lang}, using browser default`);
        }
        
        utterance.onstart = () => {
            setIsSpeaking(true);
            setShowVisualizer(true);
        };
        utterance.onend = () => {
            setIsSpeaking(false);
            if (visualizerTimerRef.current) {
                clearTimeout(visualizerTimerRef.current);
            }
            visualizerTimerRef.current = setTimeout(() => {
                setShowVisualizer(false);
            }, 3000);
        };
        utterance.onerror = () => {
            setIsSpeaking(false);
            if (visualizerTimerRef.current) {
                clearTimeout(visualizerTimerRef.current);
            }
            visualizerTimerRef.current = setTimeout(() => {
                setShowVisualizer(false);
            }, 1000);
        };
        
        synthRef.current.speak(utterance);
    }, [findBestVoice]);

    // Main speak function: prefer API TTS for non-English, fallback to browser
    const speakText = useCallback((text, lang) => {
        // For English, always use browser TTS (it works well)
        // For Dari/Pashto, try API TTS first if available, fallback to browser
        if (lang !== 'en' && apiTtsAvailable) {
            speakViaApi(text, lang);
        } else {
            speakViaBrowser(text, lang);
        }
    }, [apiTtsAvailable, speakViaApi, speakViaBrowser]);

    // Stop speaking
    const stopSpeaking = useCallback(() => {
        if (synthRef.current) {
            synthRef.current.cancel();
        }
        setIsSpeaking(false);
        setShowVisualizer(false);
    }, []);

    // Start speech recognition (voice input)
    const startListening = useCallback(() => {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognitionRef.current = recognition;
        
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = getVoiceLang(selectedLanguage);

        recognition.onstart = () => {
            setIsListening(true);
            setShowVisualizer(true);
        };
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            setInputMessage(transcript);
            // In voice mode, auto-send after speech input
            if (voiceMode) {
                sendMessage(transcript);
            }
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            setIsListening(false);
            // Keep visualizer visible briefly even on error
            if (visualizerTimerRef.current) {
                clearTimeout(visualizerTimerRef.current);
            }
            visualizerTimerRef.current = setTimeout(() => {
                setShowVisualizer(false);
            }, 1000);
        };
        
        recognition.onend = () => {
            setIsListening(false);
            // Keep visualizer visible for 3s after listening ends
            if (visualizerTimerRef.current) {
                clearTimeout(visualizerTimerRef.current);
            }
            visualizerTimerRef.current = setTimeout(() => {
                setShowVisualizer(false);
            }, 3000);
        };
        
        recognition.start();
    }, [selectedLanguage, voiceMode]);

    // Stop listening
    const stopListening = useCallback(() => {
        if (recognitionRef.current) {
            recognitionRef.current.stop();
            setIsListening(false);
        }
    }, []);

    // Toggle voice input (microphone button)
    const toggleVoiceInput = () => {
        if (isListening) {
            stopListening();
        } else {
            startListening();
        }
    };

    // Toggle voice mode (full conversational voice like ChatGPT)
    const toggleVoiceMode = () => {
        stopSpeaking();
        stopListening();
        setVoiceMode(prev => !prev);
    };

    const sendMessage = async (text = inputMessage) => {
        if (!text.trim()) return;

        const userMessage = { text, isUser: true, timestamp: new Date() };
        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);

        try {
            const response = await axios.post(`${API_BASE_URL}/api/chat/`, {
                message: text,
                session_id: sessionId,
                language: selectedLanguage
            });

            const aiResponseText = response.data.response;
            const aiMessage = {
                text: aiResponseText,
                isUser: false,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, aiMessage]);

            // In voice mode, automatically speak the AI response
            if (voiceMode) {
                speakText(aiResponseText, selectedLanguage);
                // After speaking, start listening again for continuous conversation
                setTimeout(() => {
                    if (voiceMode) {
                        startListening();
                    }
                }, 500);
            }
        } catch (error) {
            console.error('Chat error:', error);
            const errorMessage = {
                text: getErrorMessage(selectedLanguage),
                isUser: false,
                isError: true,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const getErrorMessage = (language) => {
        const errors = {
            'en': 'Sorry, I encountered an error. Please try again.',
            'fa': 'ببخشید، خطایی رخ داد. لطفاً دوباره تلاش کنید.',
            'ps': 'بخښنه غواړم، یوه تېروتنه رامنځته شوه. مهرباني وکړئ بیا هڅه وکړئ.'
        };
        return errors[language] || errors['en'];
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const quickActions = [
        { 
            en: 'Check my balance', 
            fa: 'بیلانسم را چک کنید', 
            ps: 'زما بیلانس چک کړئ' 
        },
        { 
            en: 'Internet packages', 
            fa: 'بسته های اینترنتی', 
            ps: 'انټرنیټ پیکیجونه' 
        },
        { 
            en: 'Network coverage', 
            fa: 'پوشش شبکه', 
            ps: 'د شبکې پوښښ' 
        }
    ];

    return (
        <div className="chat-interface">
            <div className="chat-header">
                <h2>🏢 Afghan Connect AI Support</h2>
                <div className="header-controls">
                    <button
                        className={`voice-mode-btn ${voiceMode ? 'active' : ''}`}
                        onClick={toggleVoiceMode}
                        title={voiceMode ? 'Disable voice mode' : 'Enable voice mode'}
                    >
                        {voiceMode ? '🎙️' : '🔇'}
                    </button>
                    <div className="language-selector">
                        <select 
                            value={selectedLanguage} 
                            onChange={(e) => setSelectedLanguage(e.target.value)}
                        >
                            {languages.map(lang => (
                                <option key={lang.code} value={lang.code}>
                                    {lang.flag} {lang.name}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>

            {voiceMode && (
                <div className="voice-mode-banner">
                    <span className="voice-mode-indicator">
                        {showVisualizer ? (isListening ? '🔴 Listening...' : isSpeaking ? '🔊 Speaking...' : '🎤 Active') : '🎤 Voice Mode Active'}
                    </span>
                    <span className="voice-mode-hint">
                        {showVisualizer ? (isListening ? 'Speak now...' : isSpeaking ? 'AI is responding...' : 'Processing...') : 'Tap the mic button to start'}
                    </span>
                </div>
            )}

            {/* Voice visualization overlay - shows animated orb when speaking/listening */}
            {showVisualizer && (
                <div className={`voice-visualizer ${isListening ? 'listening' : 'speaking'}`}>
                    <div className="voice-visualizer-inner">
                        <div className="voice-orb">
                            <div className="orb-ring ring-1"></div>
                            <div className="orb-ring ring-2"></div>
                            <div className="orb-ring ring-3"></div>
                            <div className="orb-ring ring-4"></div>
                            <div className="orb-core">
                                {isListening ? (
                                    <svg className="mic-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <rect x="9" y="2" width="6" height="11" rx="3" />
                                        <path d="M5 10a7 7 0 0 0 14 0" />
                                        <line x1="12" y1="19" x2="12" y2="22" />
                                    </svg>
                                ) : (
                                    <div className="speaking-waves">
                                        <span className="wave-bar bar-1"></span>
                                        <span className="wave-bar bar-2"></span>
                                        <span className="wave-bar bar-3"></span>
                                        <span className="wave-bar bar-4"></span>
                                        <span className="wave-bar bar-5"></span>
                                    </div>
                                )}
                            </div>
                        </div>
                        <div className="voice-label">
                            {isListening ? 'Listening...' : 'Speaking...'}
                        </div>
                    </div>
                </div>
            )}

            <div className="quick-actions">
                {quickActions.map((action, index) => (
                    <button
                        key={index}
                        className="quick-action-btn"
                        onClick={() => sendMessage(action[selectedLanguage])}
                    >
                        {action[selectedLanguage]}
                    </button>
                ))}
            </div>

            <div className="messages-container">
                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`message ${message.isUser ? 'user-message' : 'ai-message'} ${message.isError ? 'error-message' : ''}`}
                    >
                        <div className="message-content">
                            {message.text}
                        </div>
                        <div className="message-footer">
                            <span className="message-time">
                                {message.timestamp.toLocaleTimeString()}
                            </span>
                            {!message.isUser && !message.isError && (
                                <button
                                    className="speak-btn"
                                    onClick={() => speakText(message.text, selectedLanguage)}
                                    title="Read aloud"
                                    disabled={isSpeaking}
                                >
                                    🔊
                                </button>
                            )}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="message ai-message">
                        <div className="message-content loading-indicator">
                            <span className="typing-dot"></span>
                            <span className="typing-dot"></span>
                            <span className="typing-dot"></span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="input-area">
                <div className="input-container">
                    <textarea
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder={
                            selectedLanguage === 'en' ? "Type your message..." :
                            selectedLanguage === 'fa' ? "پیام خود را بنویسید..." :
                            "خپل پیام ولیکئ..."
                        }
                        rows="1"
                        disabled={voiceMode}
                    />
                    <button 
                        className={`voice-btn ${isListening ? 'listening' : ''}`}
                        onClick={toggleVoiceInput}
                        title={isListening ? 'Stop recording' : 'Start voice input'}
                    >
                        {isListening ? '🛑' : '🎤'}
                    </button>
                    {isSpeaking && (
                        <button 
                            className="stop-speech-btn"
                            onClick={stopSpeaking}
                            title="Stop speaking"
                        >
                            ⏹️
                        </button>
                    )}
                    <button 
                        className="send-btn"
                        onClick={() => sendMessage()}
                        disabled={!inputMessage.trim() || voiceMode}
                    >
                        📤
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;
