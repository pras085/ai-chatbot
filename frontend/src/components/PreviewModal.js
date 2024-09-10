import React, { useEffect, useState } from "react";

/**
 * PreviewModal Component
 *
 * Menampilkan preview untuk file yang dipilih.
 *
 * @param {File} file - File yang akan di-preview
 * @param {Function} onClose - Callback function untuk menutup modal
 */
function PreviewModal({ file, onClose }) {
  const [preview, setPreview] = useState(null);

  useEffect(() => {
    if (file) {
      if (file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onload = (e) =>
          setPreview({ type: "image", content: e.target.result });
        reader.readAsDataURL(file);
      } else if (
        file.type === "text/plain" ||
        file.type === "application/json" ||
        file.type === "text/html"
      ) {
        const reader = new FileReader();
        reader.onload = (e) =>
          setPreview({ type: "text", content: e.target.result });
        reader.readAsText(file);
      } else {
        setPreview({ type: "unsupported" });
      }
    }
  }, [file]);

  if (!file) return null;

  /**
   * Format ukuran file ke dalam bentuk yang mudah dibaca
   * @param {number} bytes - Ukuran file dalam bytes
   * @returns {string} Ukuran file yang diformat
   */
  function formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  }

  return (
    <div id="preview-modal" style={{ display: "block" }}>
      <div id="preview-content">
        <span id="preview-close" onClick={onClose}>
          &times;
        </span>
        {preview?.type === "image" && (
          <img id="preview-image" src={preview.content} alt="Preview" />
        )}
        {preview?.type === "text" && (
          <pre id="preview-text">{preview.content}</pre>
        )}
        {preview?.type === "unsupported" && (
          <p>Preview not available for this file type.</p>
        )}
        <div id="preview-info">
          File Name: {file.name}, Size: {formatFileSize(file.size)}
        </div>
      </div>
    </div>
  );
}

export default PreviewModal;
