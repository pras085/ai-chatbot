import React, { useState } from "react";
import "../styles/ChatListPage.css";
import { createNewChat } from "../services/api";

const ChatList = ({ chats = [], onSelectChat, onNewChat, onDeleteChat, userId }) => {
  const [isCreatingChat, setIsCreatingChat] = useState(false);

  // Fungsi untuk membuat chat baru
  const handleCreateNewChat = async () => {
    setIsCreatingChat(true);
    try {
      if (!userId) {
        throw new Error("User ID is not available");
      }
      const newChat = await createNewChat(userId);
      console.log("New chat created:", newChat);
      onNewChat(newChat);
      onSelectChat(newChat.id);
    } catch (error) {
      console.error("Error creating new chat:", error);
      alert("Failed to create new chat. Please try again.");
    } finally {
      setIsCreatingChat(false);
    }
  };

  const handleDeleteChat = async (chatId) => {
    if (window.confirm("Are you sure you want to delete this chat?")) {
      try {
        await onDeleteChat(chatId);
      } catch (error) {
        console.error(`Error deleting chat: ${chatId}:`, error);
        alert(`Error deleting chat: ${error.message}`);
      }
    }
  };

  const getAvatarText = (title) => {
    return title && typeof title === "string" ? title[0].toUpperCase() : "n";
  };

  return (
    <div className="chat-list-container">
      <div className="chat-list-header">
        <button
          className="create-chat-btn"
          onClick={handleCreateNewChat}
          disabled={isCreatingChat}
        >
          {isCreatingChat ? "Creating..." : "Create New Chat"}
        </button>
      </div>

      <div className="chat-list-content">
        <ul className="chat-list">
          {chats.map((chat) => (
            <li
              key={chat.chat_id}
              className="chat-item"
              onClick={() => onSelectChat(chat.chat_id)}
            >
              <div className="chat-avatar">{getAvatarText(chat.title)}</div>
              <div className="chat-content">
                <div className="chat-title">
                  {chat.title || "Untitled Chat"}
                </div>
                <div className="chat-timestamp">
                  {chat.created_at
                    ? new Date(chat.created_at).toLocaleString()
                    : "Unknown date"}
                </div>
              </div>
              <button
                className="chat-delete"
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

        <div className="product-knowledge-panel">
          <h3>Product Information</h3>
        </div>

      </div>
    </div>
  );
};

export default ChatList;