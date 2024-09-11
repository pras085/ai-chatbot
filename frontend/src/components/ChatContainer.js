/* eslint-disable no-loop-func */
import React, { useState, useCallback, useRef } from "react";
import ChatMessages from "./ChatMessages";
import UserInput from "./UserInput";
import FileUpload from "./FileUpload";
import PreviewModal from "./PreviewModal";
import { escapeHTML } from "../utils/helpers";

function ChatContainer() {
  const [messages, setMessages] = useState([]);
  const [currentFiles, setCurrentFiles] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [previewFile, setPreviewFile] = useState(null);
  const abortController = useRef(null);

  const sendMessage = useCallback(
    async (message) => {
      if (!message && currentFiles.length === 0 && !isGenerating) return;

      if (isGenerating) {
        if (abortController.current) {
          abortController.current.abort();
          return;
        }
      }

      setMessages((prev) => [
        ...prev,
        { type: "user-message", content: message },
      ]);
      setIsGenerating(true);

      const formData = new FormData();
      formData.append("message", message);
      currentFiles.forEach((file) => {
        formData.append("file", file);
      });

      try {
        abortController.current = new AbortController();
        const response = await fetch("http://localhost:8000/chat", {
          method: "POST",
          body: formData,
          signal: abortController.current.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let fullResponse = "";
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          // parse sebagai JSON, jika gagal gunakan sebagai teks biasa
          let processedChunk;
          try {
            const jsonChunk = JSON.parse(chunk);
            processedChunk = jsonChunk.content || JSON.stringify(jsonChunk);
          } catch (e) {
            processedChunk = chunk;
          }
          // Escape HTML untuk menghindari XSS
          processedChunk = escapeHTML(processedChunk);

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

        // Reset file input setelah selesai
        setCurrentFiles([]);
        console.log("Full Response:", fullResponse);
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
    [currentFiles, isGenerating]
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

  return (
    <div id="chat-container">
      <ChatMessages messages={messages} />
      <FileUpload
        currentFiles={currentFiles}
        onFileUpload={handleFileUpload}
        onRemoveFile={handleRemoveFile}
        onPreviewFile={handlePreviewFile}
      />
      <UserInput onSendMessage={sendMessage} isGenerating={isGenerating} />
      {previewFile && (
        <PreviewModal file={previewFile} onClose={() => setPreviewFile(null)} />
      )}
    </div>
  );
}

export default ChatContainer;
