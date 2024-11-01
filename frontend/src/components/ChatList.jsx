import React, { useState, useCallback } from 'react';
import { useFeature } from '../contexts/FeatureContext';


const ChatList = ({ chats, onSelectChat, onNewChat, onDeleteChat, userId }) => {
  const [isCreatingChat, setIsCreatingChat] = useState(false);
  const { activeFeature } = useFeature();

  const handleCreateNewChat = useCallback(async () => {
    setIsCreatingChat(true);
    try {
      if (!userId) {
        throw new Error("User ID is not available");
      }
      const newChat = await onNewChat(userId);
      console.log(`buat chat baru: ${newChat.id}`);
      console.log(newChat);
      onSelectChat(newChat.id);
    } catch (error) {
      console.error("Error creating new chat:", error);
      alert("Failed to create new chat. Please try again.");
    } finally {
      setIsCreatingChat(false);
    }
  }, [userId, onNewChat, onSelectChat]);

  const handleDeleteChat = useCallback((chatId) => {
    if (window.confirm("Are you sure you want to delete this chat?")) {
      onDeleteChat(chatId);
    }
  }, [onDeleteChat]);

  const getAvatarText = useCallback((title) => {
    return title && typeof title === "string" ? title[0].toUpperCase() : "N";
  }, []);

  return (
    <div className="flex flex-col h-screen justify-end overflow-hidden">
      <div className="flex-1 max-w-full p-5 overflow-y-auto transition-all duration-300 ease-in-out">
        <button
          className="w-full py-2 px-5 bg-blue-500 text-white border-none rounded cursor-pointer hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
          onClick={handleCreateNewChat}
          disabled={isCreatingChat}
        >
          {isCreatingChat ? "Creating..." : `Create New Chat ${activeFeature}`}
        </button>

        <ul className="list-none p-0 m-0 flex-grow overflow-y-auto mt-4">
          {chats.map((chat) => (
            <li
              key={chat.chat_id}
              className="flex items-center p-2.5 border border-gray-300 mb-1 cursor-pointer transition-colors duration-100 bg-gray-50 hover:bg-gray-100 rounded"
              onClick={() => onSelectChat(chat.chat_id)}
            >
              <div className="w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center text-lg mr-4">
                {getAvatarText(chat.title)}
              </div>
              <div className="flex-1">
                <div className="text-sm font-bold text-gray-800 mb-1">
                  {chat.title || "Untitled Chat"}
                </div>
                <div className="text-xs text-gray-600">
                  {chat.created_at
                    ? new Date(chat.created_at).toLocaleString()
                    : "Unknown date"}
                </div>
              </div>
              <button
                className="w-6 h-6 flex items-center justify-center text-red-500 hover:bg-red-100 rounded-full transition-colors duration-200"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteChat(chat.chat_id);
                }}
                aria-label="Delete chat"
              >
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  className="h-5 w-5" 
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path 
                    fillRule="evenodd" 
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" 
                    clipRule="evenodd" 
                  />
                </svg>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ChatList;