import { React, useState } from "react";
import "../styles/ChatList.css";
import { createNewChat } from "../services/api";

const ChatList = ({ chats = [], onSelectChat, onNewChat, userId }) => {
  const [isCreatingChat, setIsCreatingChat] = useState(false);

  const handleCreateNewChat = async () => {
    setIsCreatingChat(true);

    try {
      const newChat = await createNewChat(userId);
      console.log("New chat created:", newChat); // Tambahkan log ini
      if (newChat && newChat.id) {
        console.log(" created:", newChat); // Tambahkan log ini

        onNewChat(newChat);
      } else {
        throw new Error("Invalid chat data received");
      }
    } catch (error) {
      console.error("Error creating new chat:", error);
      alert("Failed to create new chat. Please try again.");
    } finally {
      setIsCreatingChat(false);
    }
  };

  const getAvatarText = (title) => {
    return title && typeof title === "string" ? title[0].toUpperCase() : "n";
  };
  return (
    <div className="chat-list-container">
      <button
        className="create-chat-btn"
        onClick={handleCreateNewChat}
        disabled={isCreatingChat}
      >
        {isCreatingChat ? "Creating..." : "Create New Chat"}
      </button>
      {chats.length === 0 ? (
        <div className="no-chats-message">
          No chats available. Create a new chat to get started!
        </div>
      ) : (
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
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ChatList;
