import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFile, faRemove } from "@fortawesome/free-solid-svg-icons";
import { formatFileSize } from "../utils/helpers";

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB in bytes

/**
 * FileUpload Component
 *
 * Menangani unggahan file dan menampilkan file yang sudah diunggah.
 *
 * @param {File[]} currentFiles - Array file yang sudah diunggah
 * @param {Function} onFileUpload - Callback function untuk menangani file yang diunggah
 * @param {Function} onRemoveFile - Callback function untuk menghapus file
 * @param {Function} onPreviewFile - Callback function untuk preview file
 */
function FileUpload({
  currentFiles,
  onFileUpload,
  onRemoveFile,
  onPreviewFile,
}) {
  /**
   * Menangani perubahan pada input file
   * @param {Event} e - Event objek
   */
  const handleFileChange = (e) => {
    const newFiles = Array.from(e.target.files);
    const validFiles = newFiles.filter((file) => {
      if (!isAllowedFileType(file)) {
        alert(`File type not allowed: ${file.name}`);
        return false;
      }
      if (file.size > MAX_FILE_SIZE) {
        alert(
          `File too large: ${file.name}. Maximum size is ${
            MAX_FILE_SIZE / 1024 / 1024
          }MB.`
        );
        return false;
      }
      return true;
    });

    if (validFiles.length > 0) {
      onFileUpload(validFiles);
    }
    e.target.value = ""; // Reset file input
  };

  /**
   * Memeriksa apakah tipe file diizinkan
   * @param {File} file - File yang akan diperiksa
   * @returns {boolean}
   */
  const isAllowedFileType = (file) => {
    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "application/pdf",
      "text/plain",
    ];
    return allowedTypes.includes(file.type);
  };

  return (
    <div>
      <input
        type="file"
        id="file-input"
        style={{ display: "none" }}
        onChange={handleFileChange}
        multiple
      />

      <div className="file-bubbles-container">
        {currentFiles.map((file, index) => (
          <div
            key={index}
            className="file-bubble"
            onClick={() => onPreviewFile(file)}
          >
            <div className="file-info">
              <FontAwesomeIcon icon={faFile} className="i" />
              <span className="file-name">{file.name}</span>
              <span className="file-size">({formatFileSize(file.size)})</span>
            </div>
            <div className="file-actions">
              <FontAwesomeIcon
                icon={faRemove}
                className="i"
                onClick={(e) => {
                  e.stopPropagation();
                  onRemoveFile(file);
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default FileUpload;
