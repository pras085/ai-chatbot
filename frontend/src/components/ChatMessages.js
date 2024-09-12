import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import hljs from "highlight.js";
import "highlight.js/styles/sunburst.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCopy } from "@fortawesome/free-solid-svg-icons";

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

const ChatMessages = ({ messages }) => {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Scroll ke pesan terbaru
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div id="chat-messages">
      {messages.map((msg, index) => (
        <div key={index} className={`message ${msg.type}`}>
          <Message content={msg.content} />
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};

// Komponen untuk pesan
const Message = ({ content }) => {
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
      {content}
    </ReactMarkdown>
  );
};

export default ChatMessages;
