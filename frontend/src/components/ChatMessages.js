import React, { useEffect, useRef } from "react";
import { marked } from "marked";
import hljs from "highlight.js";

/**
 * ChatMessages Component
 *
 * Menampilkan pesan-pesan dalam chat.
 *
 * @param {Object[]} messages - Array pesan untuk ditampilkan
 */
function ChatMessages({ messages }) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    marked.use({
      highlight: function (code, lang) {
        const language = hljs.getLanguage(lang) ? lang : "plaintext";
        return hljs.highlight(code, { language }).value;
      },
      langPrefix: "hljs language-",
      renderer: {
        code(code, language) {
          const validLanguage = hljs.getLanguage(language)
            ? language
            : "plaintext";
          const highlightedCode = hljs.highlight(code, {
            language: validLanguage,
          }).value;
          return `
                        <div class="collapsible-code-block">
                            <div class="collapsible-header">
                                <span class="language-label">${validLanguage}</span>
                                <button class="toggle-btn">Show code</button>
                            </div>
                            <pre class="code-content" style="display:none;">
                                <code class="hljs language-${validLanguage}">${highlightedCode}</code>
                            </pre>
                        </div>`;
        },
      },
    });
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /**
   * Render pesan individu
   * @param {Object} message - Objek pesan
   * @returns {JSX.Element}
   */
  const renderMessage = (message) => {
    if (message.type === "bot") {
      return (
        <div dangerouslySetInnerHTML={{ __html: marked(message.content) }} />
      );
    }
    return <div>{message.content}</div>;
  };

  return (
    <div id="chat-messages">
      {messages.map((msg, index) => (
        <div key={index} className={`message ${msg.type}-message`}>
          {renderMessage(msg)}
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default ChatMessages;
