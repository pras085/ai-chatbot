import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import hljs from "highlight.js";
import "highlight.js/styles/sunburst.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCopy, faRedo } from "@fortawesome/free-solid-svg-icons";
import DOMPurify from "dompurify";

// Komponen untuk menangani render kode dengan Markdown dan membuatnya collapsible
const RenderCodeBlock = ({ language, value }) => {
  const [isCollapsed, setIsCollapsed] = useState(true);
  const codeRef = useRef(null);

  useEffect(() => {
    if (codeRef.current && !isCollapsed) {
      hljs.highlightElement(codeRef.current);
    }
  }, [value, isCollapsed]);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(value).then(
      () => {
        alert("Code copied to clipboard!");
      },
      (err) => {
        console.error("Failed to copy: ", err);
      }
    );
  };

  return (
    <div className="collapsible-code-block">
      <div
        className="collapsible-header"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div>
          <span className="language-label">{language || "plaintext"}</span>
          <button className="toggle-btn" onClick={toggleCollapse}>
            {isCollapsed ? "Show code" : "Hide code"}
          </button>
        </div>
        {!isCollapsed && (
          <FontAwesomeIcon
            icon={faCopy}
            className="copy-icon"
            onClick={handleCopy}
            title="Copy code"
          />
        )}
      </div>
      {!isCollapsed && (
        <pre className="hljs">
          <code ref={codeRef}>{value}</code>
        </pre>
      )}
    </div>
  );
};

function ChatMessages({ messages, onPreviewFile, onRetry }) {
  const messagesEndRef = useRef(null);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      alert("Pesan berhasil disalin!");
    });
  };

  useEffect(() => {
    // Scroll ke pesan terbaru
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div id="chat-messages">
      {messages.map((message, index) => (
        <div key={index} className={`message ${message.type}`}>
          <Message content={message.content} />
          {message.type === "bot-message" && (
            <div className="message-actions">
              <button
                onClick={() => copyToClipboard(message.content)}
                className="action-button"
                title="Salin pesan"
              >
                <FontAwesomeIcon icon={faCopy} />
              </button>
              <button
                onClick={() => onRetry(index)}
                className="action-button"
                title="Ulangi generasi"
              >
                <FontAwesomeIcon icon={faRedo} />
              </button>
            </div>
          )}
          {message.file && (
            <div className="file-attachment">
              {message.file.type.startsWith("image/") ? (
                <img
                  src={URL.createObjectURL(message.file)}
                  alt="Uploaded"
                  className="uploaded-image"
                  onClick={() => onPreviewFile(message.file)}
                />
              ) : (
                <span onClick={() => onPreviewFile(message.file)}>
                  {message.file.name}
                </span>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// Komponen untuk pesan
const Message = ({ content }) => {
  const sanitizedContent = DOMPurify.sanitize(content);
  return (
    <ReactMarkdown
      components={{
        code({ inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || "");
          return !inline && match ? (
            <RenderCodeBlock
              language={match[1]}
              value={String(children).replace(/\n$/, "")}
            />
          ) : (
            <code className={className} {...props}>
              {children}
            </code>
          );
        },
      }}
    >
      {sanitizedContent}
    </ReactMarkdown>
  );
};

export default ChatMessages;
