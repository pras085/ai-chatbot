import React, { useState, useCallback, useRef, useEffect } from "react";
import ChatMessages from "./ChatMessages";
import UserInput from "./UserInput";
import FileUpload from "./FileUpload";
import PreviewModal from "./PreviewModal";
import { sendChatMessage, getChatMessages } from "../services/api";

function ChatContainer({ chatId, onBackToList, userId }) {
  const [messages, setMessages] = useState([]);
  const [currentFiles, setCurrentFiles] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [previewFile, setPreviewFile] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    if (chatId) {
      console.log("Loading chat:", chatId);
      loadChatHistory();
    } else {
      console.log("No chat selected");
      onBackToList();
    }
  }, [chatId, onBackToList]);

  const loadChatHistory = async () => {
    if (chatId === undefined) {
      console.error("Cannot load chat history: chatId is undefined");
      return;
    }
    setIsLoading(true);

    try {
      const response = await getChatMessages(chatId);
      const formattedMessages = response.messages.map((message) => ({
        type: message.is_user ? "user-message" : "bot-message",
        content: message.content,
        timestamp: message.timestamp,
        file_url: message.file_url,
        file_name: message.file_name,
      }));
      console.info("messages:", formattedMessages);
      setMessages(formattedMessages);
      setError(null);
    } catch (error) {
      console.error("Error loading chat history:", error);
      setError("Failed to load chat history. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (message, file) => {
    if (!message.trim() && !file) return;

    setIsGenerating(true);
    const newMessage = { content: message, type: "user-message" };
    setMessages(prevMessages => [...prevMessages, newMessage]);

    abortControllerRef.current = new AbortController();

    try {
      await sendChatMessage(
        userId,
        chatId,
        message,
        file,
        abortControllerRef.current.signal,
        (chunk) => {
          setMessages(prevMessages => {
            const lastMessage = prevMessages[prevMessages.length - 1];
            if (lastMessage.type === "bot-message") {
              return [
                ...prevMessages.slice(0, -1),
                { ...lastMessage, content: lastMessage.content + chunk }
              ];
            } else {
              return [...prevMessages, { content: chunk, type: "bot-message" }];
            }
          });
        },
        () => {
          setIsGenerating(false);
          setCurrentFiles([]);  // Clear the current files after sending
        },
        (error) => {
          console.error("Error in chat:", error);
          setMessages(prevMessages => [
            ...prevMessages,
            { content: "An error occurred. Please try again.", type: "bot-message" }
          ]);
          setIsGenerating(false);
        }
      );
    } catch (error) {
      console.error("Failed to send message:", error);
      setIsGenerating(false);
    }
  };

  const handleFileUpload = useCallback((files) => {
    setCurrentFiles((prev) => [...prev, ...files]);
  }, []);

  const handleRemoveFile = useCallback((fileToRemove) => {
    setCurrentFiles((prev) => prev.filter((file) => file !== fileToRemove));
  }, []);

  const handlePreviewFile = useCallback((file) => {
    setPreviewFile(file);
  }, []);

  if (isLoading) return <div>Loading chat...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div id="chat-container">
      <button className="back-button" onClick={onBackToList}>
        Back to Chat List
      </button>
      <div id="chat-messages-container">
        <ChatMessages
          messages={messages}
          onPreviewFile={handlePreviewFile}
          isGenerating={isGenerating}
        />
      </div>
      <FileUpload onFileUpload={handleFileUpload} currentFiles={currentFiles} />
      <UserInput
        onSendMessage={handleSendMessage}
        isGenerating={isGenerating}
        currentFiles={currentFiles}
        onRemoveFile={handleRemoveFile}
        onPreviewFile={handlePreviewFile}
      />
      {previewFile && (
        <PreviewModal file={previewFile} onClose={() => setPreviewFile(null)} />
      )}
    </div>
  );
}

export default ChatContainer;