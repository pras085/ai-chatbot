import React from 'react';
import MessageList from './MessageList';
import UserInput from './UserInput';

const ChatInterface = ({ messages, onSendMessage, onBackToList, activeFeature }) => {
    return (
        <div id="chat-container">
            <button className="back-button" onClick={onBackToList}>
                Back to Chat List
            </button>
            <h2>{activeFeature} Chat</h2>
            <div id="chat-messages-container">
                <MessageList messages={messages} />
            </div>
            <UserInput onSendMessage={onSendMessage} />
        </div>
    );
};

export default ChatInterface;