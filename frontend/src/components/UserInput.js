import React, { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faPaperPlane,
  faStop,
  faPaperclip,
} from "@fortawesome/free-solid-svg-icons";

/**
 * UserInput Component
 *
 * Komponen untuk input pengguna dalam chat.
 *
 * @param {Function} onSendMessage - Callback function untuk mengirim pesan
 * @param {boolean} isGenerating - Status generasi respons
 */
function UserInput({ onSendMessage, isGenerating }) {
  const [message, setMessage] = useState("");

  /**
   * Menangani pengiriman pesan
   * @param {Event} e - Event objek
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() || isGenerating) {
      onSendMessage(message);
      setMessage("");
    }
  };

  return (
    <form id="user-input" onSubmit={handleSubmit}>
      <input
        type="text"
        id="message-input"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        autoComplete="off"
        placeholder="Type your message..."
      />{" "}
      <button
        type="button"
        id="attach-button"
        onClick={() => document.getElementById("file-input").click()}
        data-tooltip="Upload docs/image"
      >
        <FontAwesomeIcon icon={faPaperclip} />
      </button>
      <button
        id="send-button"
        type="submit"
        className={isGenerating ? "stop" : ""}
        data-tooltip={isGenerating ? "Stop generation" : "Send message"}
      >
        <FontAwesomeIcon icon={isGenerating ? faStop : faPaperPlane} />
      </button>
    </form>
  );
}

export default UserInput;
