import React, { useState, useCallback, useRef } from "react";
import ChatMessages from "./ChatMessages";
import UserInput from "./UserInput";
import FileUpload from "./FileUpload";
import PreviewModal from "./PreviewModal";

function ChatContainer() {
  const [messages, setMessages] = useState([]);
  const [currentFiles, setCurrentFiles] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [previewFile, setPreviewFile] = useState(null);
  const abortControllerRef = useRef(null);

  const sendMessage = useCallback(
    async (message) => {
      if (!message && currentFiles.length === 0 && !isGenerating) return;

      if (isGenerating) {
        if (abortControllerRef.current) {
          abortControllerRef.current.abort();
          return;
        }
      }

      setMessages((prev) => [...prev, { type: "user", content: message }]);
      setIsGenerating(true);

      const formData = new FormData();
      formData.append("message", message);
      currentFiles.forEach((file) => {
        formData.append(`file`, file);
      });

      try {
        abortControllerRef.current = new AbortController();
        const response = await fetch("http://localhost:3000/chat", {
          method: "POST",
          body: formData,
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let fullMessage = "";

        const updateMessages = (newContent) => {
          setMessages((prevMessages) => {
            const newMessages = [...prevMessages];
            if (newMessages[newMessages.length - 1]?.type === "bot") {
              newMessages[newMessages.length - 1].content = newContent;
            } else {
              newMessages.push({ type: "bot", content: newContent });
            }
            return newMessages;
          });
        };

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          try {
            const jsonChunk = JSON.parse(chunk);
            fullMessage += jsonChunk.content || JSON.stringify(jsonChunk);
          } catch (e) {
            fullMessage += chunk;
          }

          updateMessages(fullMessage); // Panggil fungsi pembaruan
        }
      } catch (error) {
        if (error.name === "AbortError") {
          console.log("Generasi respons dihentikan oleh pengguna");
          setMessages((prev) => [
            ...prev,
            { type: "bot", content: "Response dihentikan." },
          ]);
        } else {
          console.error("Error:", error.message);
          setMessages((prev) => [
            ...prev,
            {
              type: "bot",
              content:
                "Terjadi kesalahan saat mengirim pesan: " + error.message,
            },
          ]);
        }
      } finally {
        abortControllerRef.current = null;
        setIsGenerating(false);
        setCurrentFiles([]);
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
