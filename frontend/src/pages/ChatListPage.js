import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import ChatList from "../components/ChatList";
import { getUserChats } from "../services/api";
import { useUser } from "../hooks/useUser";

function ChatListPage({ userId }) {
  const [chats, setChats] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { user, loading: userLoading } = useUser(); // Menggunakan hook useUser

  const fetchChats = async (uid) => {
    try {
      const userChats = await getUserChats(uid);
      setChats(userChats);
    } catch (err) {
      console.error("Failed to fetch chats:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchChats(userId);
    }
  }, [userId]);

  const handleSelectChat = (chatId) => {
    navigate(`/chat/${chatId}`);
  };

  const handleNewChat = useCallback(
    (newChat) => {
      setChats((prevChats) => [newChat, ...prevChats]);
      navigate(`/chat/${newChat.id || newChat.chat_id}`);
    },
    [navigate]
  );

  if (userLoading || isLoading) return <div>Loading chats...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="chat-list-page">
      <ChatList
        chats={chats}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        userId={user?.id} // Menggunakan id dari user yang diambil dari hook
      />
    </div>
  );
}

export default ChatListPage;
