import React from "react";

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
function FileUpload({ onFileUpload }) {
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
    <input
      type="file"
      id="file-input"
      style={{ display: "none" }}
      onChange={handleFileChange}
      multiple
    />
  );
}

export default FileUpload;
