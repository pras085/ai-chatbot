import { React, useState } from "react";
import "../styles/ChatListPage.css";
import { createNewChat, deleteChat } from "../services/api"; // Tambahkan API deleteChat

const ChatList = ({ chats = [], onSelectChat, onNewChat, userId }) => {
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

  const getAvatarText = (title) => {
    return title && typeof title === "string" ? title[0].toUpperCase() : "n";
  };
  // Fungsi untuk menampilkan context menu pada klik kanan
  // const handleRightClick = (event, chatId) => {
  //   event.preventDefault(); // Mencegah context menu browser default
  //   setContextMenu({
  //     mouseX: event.clientX,
  //     mouseY: event.clientY,
  //     chatId,
  //   });
  // };

  // Fungsi untuk menghapus chat
  const handleDeleteChat = async (userId, chatId) => {
    try {
      await deleteChat(userId, chatId); // Panggil API deleteChat
      alert("Chat berhasil dihapus");
      onNewChat(chats.filter((chat) => chat.chat_id !== chatId));
    } catch (error) {
      alert("Gagal menghapus chat. Silakan coba lagi.");
    }
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
              <button
                className="chat-delete"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteChat(userId, chat.chat_id);
                }}
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
      {/* {contextMenu && (
        <div
          className="context-menu"
          style={{
            top: contextMenu.mouseY,
            left: contextMenu.mouseX,
            position: "absolute",
            backgroundColor: "white",
            boxShadow: "0px 4px 8px rgba(0, 0, 0, 0.2)",
          }}
        >
          <ul>
            <li onClick={() => handleDeleteChat(contextMenu.chatId)}>
              Hapus Chat
            </li>
          </ul>
        </div>
      )} */}
    </div>
  );
};

export default ChatList;
