import React, { useState, useCallback } from 'react';

const ChatList = ({ chats, onSelectChat, onNewChat, onDeleteChat, userId }) => {
  const [isCreatingChat, setIsCreatingChat] = useState(false);

  const handleCreateNewChat = useCallback(async () => {
    setIsCreatingChat(true);
    try {
      if (!userId) {
        throw new Error("User ID is not available");
      }
      const newChat = await onNewChat(userId);
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
      <div className="flex-1 max-w-3xl p-5 overflow-y-auto transition-all duration-300 ease-in-out">
        <button
          className="w-full py-2 px-5 bg-blue-500 text-white border-none rounded cursor-pointer hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
          onClick={handleCreateNewChat}
          disabled={isCreatingChat}
        >
          {isCreatingChat ? "Creating..." : "Create New Chat"}
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
                className="py-1 px-2.5 bg-red-500 text-white border-none rounded cursor-pointer hover:bg-red-600"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteChat(chat.chat_id);
                }}
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ChatList;