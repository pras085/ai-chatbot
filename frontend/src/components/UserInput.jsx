import React, { useState, useRef, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faPaperPlane,
  faStop,
  faPaperclip,
  faFile,
  faRemove,
  faSpinner,
} from "@fortawesome/free-solid-svg-icons";
import { formatFileSize } from "../utils/helpers";

function UserInput({
  onSendMessage,
  isGenerating,
  currentFiles,
  onRemoveFile,
  onPreviewFile,
}) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef(null);

  useEffect(() => {
    adjustTextareaHeight();
  }, [message]);

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      const scrollHeight = textarea.scrollHeight;
      textarea.style.height = `${Math.min(scrollHeight, 150)}px`; // Max height 150px
    }
  };

  const handleChange = (e) => {
    setMessage(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!isGenerating && message.trim()) {
      onSendMessage(message, currentFiles[0]);
      setMessage("");
    }
  };

  return (
    <form id="user-input" onSubmit={handleSubmit}>
      <div className="input-container">
        <div className="file-bubbles-container">
          {currentFiles.map((file, index) => (
            <div
              key={index}
              className="file-bubble"
              onClick={() => onPreviewFile(file)}
            >
              {file.type.startsWith("image/") ? (
                <img
                  src={URL.createObjectURL(file)}
                  alt="Preview"
                  className="file-preview"
                />
              ) : (
                <FontAwesomeIcon icon={faFile} className="i" />
              )}
              <span className="file-name">{file.name}</span>
              <span className="file-size">({formatFileSize(file.size)})</span>
              <FontAwesomeIcon
                icon={faRemove}
                className="i"
                onClick={(e) => {
                  e.stopPropagation();
                  onRemoveFile(file);
                }}
              />
            </div>
          ))}
        </div>
        <textarea
          ref={textareaRef}
          id="message-input"
          value={message}
          onChange={handleChange}
          autoComplete="off"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
          placeholder="Type your message..."
        />
      </div>
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
        {isGenerating ? (
          <FontAwesomeIcon icon={faSpinner} spin />
        ) : (
          <FontAwesomeIcon icon={isGenerating ? faStop : faPaperPlane} />
        )}
      </button>
    </form>
  );
}

export default UserInput;