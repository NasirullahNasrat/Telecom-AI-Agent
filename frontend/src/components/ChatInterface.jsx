import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './ChatInterface.css';

const ChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isListening, setIsListening] = useState(false);
    const [selectedLanguage, setSelectedLanguage] = useState('en');
    const [sessionId] = useState(() => `session_${Date.now()}`);
    const messagesEndRef = useRef(null);

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

    const sendMessage = async (text = inputMessage) => {
        if (!text.trim()) return;

        const userMessage = { text, isUser: true, timestamp: new Date() };
        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');

        try {
            const response = await axios.post('/api/chat/', {
                message: text,
                session_id: sessionId,
                language: selectedLanguage
            });

            const aiMessage = {
                text: response.data.response,
                isUser: false,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            console.error('Chat error:', error);
            const errorMessage = {
                text: getErrorMessage(selectedLanguage),
                isUser: false,
                isError: true,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
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

    const toggleVoiceInput = () => {
        if (!isListening) {
            if ('webkitSpeechRecognition' in window) {
                const recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = selectedLanguage === 'en' ? 'en-US' : 
                                  selectedLanguage === 'fa' ? 'fa-IR' : 'ps-AF';

                recognition.onstart = () => setIsListening(true);
                
                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript;
                    setInputMessage(transcript);
                    sendMessage(transcript);
                };
                
                recognition.onerror = (event) => {
                    console.error('Speech recognition error:', event.error);
                    setIsListening(false);
                };
                
                recognition.onend = () => setIsListening(false);
                
                recognition.start();
            } else {
                alert('Speech recognition not supported in this browser.');
            }
        }
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
                        <div className="message-time">
                            {message.timestamp.toLocaleTimeString()}
                        </div>
                    </div>
                ))}
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
                    />
                    <button 
                        className="voice-btn"
                        onClick={toggleVoiceInput}
                        disabled={isListening}
                    >
                        {isListening ? '🛑' : '🎤'}
                    </button>
                    <button 
                        className="send-btn"
                        onClick={() => sendMessage()}
                        disabled={!inputMessage.trim()}
                    >
                        📤
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;