import React, { useState, useEffect } from "react";
import ChatList from "./ChatList";
import { getUserChats, createNewChat } from "../services/api";
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
  const [currentChatId, setCurrentChatId] = useState(null);
  const [chats, setChats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const initializeChats = async () => {
      setIsLoading(true);
      try {
        let userChats = await getUserChats(userId);
        // if (userChats.length === 0) {
        //   const newChat = await createNewChat(userId);
        //   if (newChat) userChats = [newChat];
        // }
        setChats(userChats);
        setError(null);
      } catch (err) {
        setError("Failed to initialize chats. Please try again later.");
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    initializeChats();
  }, [userId]);

  const handleSelectChat = (chatId) => {
    console.log("Selecting chat:", chatId);
    setCurrentChatId(chatId);
    setCurrentView("chat");
  };

  const handleBackToList = () => {
    setCurrentView("list");
  };

  const handleNewChat = async () => {
    try {
      const newChat = await createNewChat(userId);
      if (newChat && newChat.id) {
        setChats((prevChats) => [...prevChats, newChat]);
      } else {
        throw new Error("Invalid chat data received");
      }
    } catch (error) {
      console.error("Error creating new chat:", error);
      setError("Failed to create new chat. Please try again.");
    }
  };

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
          chatId={currentChatId || null}
          onBackToList={handleBackToList}
          userId={userId}
        />
      )}
    </div>
  );
}

export default ChatApp;
