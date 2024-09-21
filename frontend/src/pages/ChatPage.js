import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import ChatContainer from "../components/ChatContainer";
import "../styles/ChatPage.css";

function ChatPage({ userId }) {
  const { chatId } = useParams();
  const navigate = useNavigate();

  const handleBackToList = () => {
    navigate("/chats");
  };

  return (
    <div className="chat-page">
      <ChatContainer
        chatId={Number(chatId)}
        onBackToList={handleBackToList}
        userId={userId}
      />
    </div>
  );
}

export default ChatPage;
