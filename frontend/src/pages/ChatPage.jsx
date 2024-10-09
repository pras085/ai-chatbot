import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import ChatContainer from "../components/ChatContainer";
import useUser from "../hooks/useUser";
import "../styles/ChatPage.css";

function ChatPage() {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const { user } = useUser();

  const handleBackToList = () => {
    navigate("/chats");
  };

  if (!user) {
    return <div>Loading user data...</div>;
  }

  return (
    <div className="chat-page">
      <ChatContainer
        chatId={chatId}
        onBackToList={handleBackToList}
        userId={user.id}
      />
    </div>
  );
}

export default ChatPage;