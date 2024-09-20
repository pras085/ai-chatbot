import React, { useEffect, useState } from "react";
import { formatFileSize } from "../utils/helpers";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faClose } from "@fortawesome/free-solid-svg-icons";

/**
 * PreviewModal Component
 *
 * Menampilkan preview untuk file yang dipilih.
 *
 * @param {Object} file - File yang akan di-preview (bisa berupa File object atau {name, url, size})
 * @param {Function} onClose - Callback function untuk menutup modal
 */
function PreviewModal({ file, onClose }) {
  const [preview, setPreview] = useState(null);

  useEffect(() => {
    if (file) {
      if (file.url) {
        // File from server
        if (file.url.match(/\.(jpeg|jpg|gif|png)$/)) {
          setPreview({ type: "image", content: file.url });
        } else {
          setPreview({ type: "unsupported" });
        }
      } else if (file instanceof File) {
        // File from local upload
        if (file.type.startsWith("image/")) {
          const reader = new FileReader();
          reader.onload = (e) =>
            setPreview({ type: "image", content: e.target.result });
          reader.readAsDataURL(file);
        } else {
          const reader = new FileReader();
          reader.onload = (e) =>
            setPreview({ type: "text", content: e.target.result });
          reader.readAsText(file);
        }
      }
    }
  }, [file]);

  if (!file) return null;

  return (
    <div id="preview-modal" style={{ display: "block" }}>
      <div id="preview-content">
        <FontAwesomeIcon icon={faClose} id="preview-close" onClick={onClose} />
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
          <span className="text-bold">File Name</span>: {file.name}, {""}
          <span className="text-bold">Size</span>: {formatFileSize(file.size)}
        </div>{" "}
      </div>
    </div>
  );
}

export default PreviewModal;
