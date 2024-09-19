import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faCopy,
  faRedo,
  faChevronDown,
  faChevronUp,
} from "@fortawesome/free-solid-svg-icons";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";

const RenderCodeBlock = ({ language, value }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

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
    <div className="code-block">
      <div className="code-header">
        <span className="language-label">{language || "plaintext"}</span>
        <div className="code-actions">
          <button
            className="action-button"
            onClick={handleCopy}
            title="Copy code"
          >
            <FontAwesomeIcon icon={faCopy} />
          </button>
          <button
            className="action-button"
            onClick={toggleCollapse}
            title={isCollapsed ? "Expand" : "Collapse"}
          >
            <FontAwesomeIcon icon={isCollapsed ? faChevronDown : faChevronUp} />
          </button>
        </div>
      </div>
      {!isCollapsed && (
        <div className="code-content">
          <SyntaxHighlighter
            language={language}
            style={vscDarkPlus}
            customStyle={{ margin: 0, borderRadius: "0 0 4px 4px" }}
          >
            {value}
          </SyntaxHighlighter>
        </div>
      )}
    </div>
  );
};

// function ChatMessages({ messages, onPreviewFile, onRetry }) {
function ChatMessages({ messages, onPreviewFile }) {
  const messagesEndRef = useRef(null);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      alert("Pesan berhasil disalin!");
    });
  };

  useEffect(() => {
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
              {/* <button
                onClick={() => onRetry(index)}
                className="action-button"
                title="Ulangi generasi"
              >
                <FontAwesomeIcon icon={faRedo} />
              </button> */}
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
      <div ref={messagesEndRef} />
    </div>
  );
}

const Message = ({ content }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeRaw]}
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || "");
          return !inline && match ? (
            <RenderCodeBlock
              language={match[1]}
              value={String(children).replace(/\n$/, "")}
            />
          ) : (
            <code className={"inline-code"} {...props}>
              {children}
            </code>
          );
        },
        h1: ({ node, ...props }) => <h1 className="markdown-h1" {...props} />,
        h2: ({ node, ...props }) => <h2 className="markdown-h2" {...props} />,
        h3: ({ node, ...props }) => <h3 className="markdown-h3" {...props} />,
        ul: ({ node, ...props }) => <ul className="markdown-ul" {...props} />,
        ol: ({ node, ...props }) => <ol className="markdown-ol" {...props} />,
        li: ({ node, ...props }) => <li className="markdown-li" {...props} />,
        p: ({ node, ...props }) => <p className="markdown-p" {...props} />,
        a: ({ node, ...props }) => <a className="markdown-a" {...props} />,
        blockquote: ({ node, ...props }) => (
          <blockquote className="markdown-blockquote" {...props} />
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
};

export default ChatMessages;
