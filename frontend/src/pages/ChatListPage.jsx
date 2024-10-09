import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import ChatList from "../components/ChatList";
import { getUserChats } from "../services/api";
import useUser from "../hooks/useUser";

function ChatListPage() {
  const [chats, setChats] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { user, loading: userLoading } = useUser();

  const fetchChats = useCallback(async (uid) => {
    if (!uid) return;
    setIsLoading(true);
    try {
      const userChats = await getUserChats(uid);
      setChats(userChats);
    } catch (err) {
      console.error("Failed to fetch chats:", err);
      setError("Failed to load chats. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user && user.id) {
      fetchChats(user.id);
    }
  }, [user, fetchChats]);

  const handleSelectChat = useCallback((chatId) => {
    console.log("chat id:", chatId);
    navigate(`/chat/${chatId}`);
  }, [navigate]);

  const handleNewChat = useCallback((newChat) => {
    setChats((prevChats) => [newChat, ...prevChats]);
    navigate(`/chat/${newChat.id}`);
  }, [navigate]);

  if (userLoading) return <div>Loading user data...</div>;
  if (!user) return <div>Please log in to view chats.</div>;
  if (isLoading) return <div>Loading chats...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="chat-list-page">
      <ChatList
        chats={chats}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        userId={user.id}
      />
    </div>
  );
}

export default ChatListPage;