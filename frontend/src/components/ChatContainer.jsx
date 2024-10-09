/* eslint-disable no-loop-func */
import React, { useState, useCallback, useRef, useEffect } from "react";
import ChatMessages from "./ChatMessages";
import UserInput from "./UserInput";
import FileUpload from "./FileUpload";
import PreviewModal from "./PreviewModal";
import { sendChatMessage, getChatMessages } from "../services/api";

/**
 * ChatContainer Component
 *
 * Komponen utama untuk menampilkan dan mengelola chat individu.
 * Fitur:
 * - Menampilkan riwayat pesan chat
 * - Memungkinkan pengiriman pesan baru
 * - Menangani upload dan preview file
 * - Menampilkan respons AI secara real-time (streaming)
 *
 * @param {number} chatId - ID chat yang sedang aktif
 * @param {Function} onBackToList - Callback function untuk kembali ke daftar chat
 * @param {string} userId - ID pengguna saat ini
 */
function ChatContainer({ chatId, onBackToList, userId }) {
  const [messages, setMessages] = useState([]);
  const [currentFiles, setCurrentFiles] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [previewFile, setPreviewFile] = useState(null);
  const abortController = useRef(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (chatId) {
      console.log("Loading chat:", chatId);
      loadChatHistory();
    } else {
      console.log("No chat selected");
      onBackToList();
    }
  }, [chatId]);

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

  const sendMessage = useCallback(
    async (message, file) => {
      if (isGenerating) return;
      if (!message && currentFiles.length === 0 && !isGenerating) return;

      let combinedMessage = message;
      if (file) {
        combinedMessage += `\n\n[File attached: ${file.name}]`;
      }

      if (isGenerating) {
        if (abortController.current) {
          abortController.current.abort();
          return;
        }
      }

      setMessages((prev) => [
        ...prev,
        {
          type: "user-message",
          content: combinedMessage,
          file: file || currentFiles[0],
        },
      ]);
      setIsGenerating(true);

      try {
        abortController.current = new AbortController();
        console.log("message: ", message);
        const response = await sendChatMessage(
          userId,
          chatId,
          message,
          currentFiles[0],
          abortController.current.signal
        );

        let fullResponse = "";
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          // let processedChunk = escapeHTML(chunk);

          fullResponse += chunk;

          setMessages((prev) => {
            const newMessages = [...prev];
            if (newMessages[newMessages.length - 1]?.type === "bot-message") {
              newMessages[newMessages.length - 1].content = fullResponse;
            } else {
              newMessages.push({ type: "bot-message", content: fullResponse });
            }
            return newMessages;
          });
        }

        setCurrentFiles([]);
      } catch (error) {
        if (error.name === "AbortError") {
          console.log("Message generation aborted by user");
          setMessages((prev) => [
            ...prev,
            { type: "bot-message", content: "Response generation stopped." },
          ]);
        } else {
          console.error("Error:", error);
          setMessages((prev) => [
            ...prev,
            {
              type: "bot-message",
              content: "An error occurred while sending the message.",
            },
          ]);
        }
      } finally {
        setIsGenerating(false);
        abortController.current = null;
      }
    },
    [currentFiles, isGenerating, chatId, userId]
  );

  const handleFileUpload = useCallback((files) => {
    setCurrentFiles((prev) => [...prev, ...files]);
  }, []);

  const handleRemoveFile = useCallback((fileToRemove) => {
    setCurrentFiles((prev) => prev.filter((file) => file !== fileToRemove));
  }, []);

  const handlePreviewFile = useCallback((file) => {
    setPreviewFile(file);
  }, []);

  // const handleRetry = useCallback(
  //   (messageIndex) => {
  //     console.log("index", messages[messageIndex]);
  //     const messageToRetry = messages[messageIndex];
  //     if (messageToRetry.type === "bot-message") {
  //       // Ambil pesan user sebelum pesan bot yang ingin di-retry
  //       sendMessage(messageToRetry.content, messageToRetry.file);
  //     }
  //   },
  //   [messages, sendMessage]
  // );

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
        // onRetry={handleRetry}
        />
      </div>
      <FileUpload onFileUpload={handleFileUpload} currentFiles={currentFiles} />
      <UserInput
        onSendMessage={sendMessage}
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
