import React, { useState, useEffect, useCallback } from "react";
import ChatList from "./ChatList";
import { getUserChats } from "../services/api";
import ChatContainer from "../components/ChatContainer";
/**
 * ChatApp Component
 *
 * Komponen utama yang mengelola perpindahan antara daftar chat dan tampilan chat individu.
 * Bertanggung jawab untuk:
 * - Menampilkan daftar chat atau chat individu berdasarkan state currentView
 * - Mengelola perpindahan antara tampilan daftar dan tampilan chat
 * - Menyimpan dan mengatur currentChatId untuk chat yang sedang aktif
 */
function ChatApp({ userId }) {
  const [currentView, setCurrentView] = useState("list");
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [chats, setChats] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const fetchChats = useCallback(async () => {
    setIsLoading(true);
    try {
      const userChats = await getUserChats(userId);
      setChats(userChats);
      setError(null);
    } catch (err) {
      setError("Failed to fetch chats. Please try again later.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchChats();
  }, [fetchChats]);

  const handleSelectChat = (chatId) => {
    const numericChatId = Number(chatId);
    console.log("Selecting chat:", numericChatId);
    setSelectedChatId(numericChatId);
    setCurrentView("chat");
  };

  const handleBackToList = useCallback(() => {
    setCurrentView("list");
    fetchChats(); // Refresh the chat list when returning to it
  }, [fetchChats]);

  const handleNewChat = useCallback((newChat) => {
    setChats((prevChats) => [newChat, ...prevChats]);
    setSelectedChatId(newChat.id || newChat.chat_id);
    setCurrentView("chat");
  }, []);

  if (isLoading) return <div>Loading chats...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="chat-app">
      {currentView === "list" ? (
        <ChatList
          chats={chats}
          onSelectChat={handleSelectChat}
          onNewChat={handleNewChat}
          userId={userId}
        />
      ) : (
        <ChatContainer
          chatId={selectedChatId}
          onBackToList={handleBackToList}
          userId={userId}
        />
      )}
    </div>
  );
}

export default ChatApp;
