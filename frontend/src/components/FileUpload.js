import React from "react";

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
    const validFiles = newFiles.filter((file) => isAllowedFileType(file));
    onFileUpload(validFiles);
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
      <button
        id="attach-button"
        onClick={() => document.getElementById("file-input").click()}
        data-tooltip="Upload docs/image"
      >
        <i className="fas fa-paperclip"></i>
      </button>
      <div className="file-bubbles-container">
        {currentFiles.map((file, index) => (
          <div
            key={index}
            className="file-bubble"
            onClick={() => onPreviewFile(file)}
          >
            <div className="file-info">
              <i className="fas fa-file"></i>
              <span className="file-name">{file.name}</span>
            </div>
            <div className="file-actions">
              <i
                className="fas fa-times remove-file"
                onClick={(e) => {
                  e.stopPropagation();
                  onRemoveFile(file);
                }}
              ></i>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default FileUpload;
