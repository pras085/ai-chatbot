import React, { useState, useEffect } from 'react';
import ChatInterface from '../components/ChatInterface';
import { sendChatMessage } from '../services/api';

const GeneralAIChat = () => {
    const [messages, setMessages] = useState([]);
    const [isGenerating, setIsGenerating] = useState(false);

    const handleSendMessage = async (message) => {
        setIsGenerating(true);
        try {
            const response = await sendChatMessage(message, 'GENERAL');
            setMessages(prevMessages => [...prevMessages,
            { content: message, type: 'user-message' },
            { content: response, type: 'bot-message' }
            ]);
        } catch (error) {
            console.error('Error sending message:', error);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="general-ai-chat">
            <h2>General AI Assistant</h2>
            <ChatInterface
                onSendMessage={handleSendMessage}
                messages={messages}
                isGenerating={isGenerating}
            />
        </div>
    );
};

export default GeneralAIChat;