import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import ChatList from "../components/ChatList";
import { getUserChats } from "../services/api";

function ChatListPage({ userId }) {
  const [chats, setChats] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

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
    navigate(`/chat/${chatId}`);
  };

  const handleNewChat = useCallback(
    (newChat) => {
      setChats((prevChats) => [newChat, ...prevChats]);
      navigate(`/chat/${newChat.id || newChat.chat_id}`);
    },
    [navigate]
  );

  if (isLoading) return <div>Loading chats...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="chat-list-page">
      <ChatList
        chats={chats}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        userId={userId}
      />
    </div>
  );
}

export default ChatListPage;
