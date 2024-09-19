import React from "react";

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB in bytes
const MAX_FILE_COUNT = 5; // Maksimal 5 file

/**
 * FileUpload Component
 *
 * Menangani unggahan file dan menampilkan file yang sudah diunggah.
 *
 * @param {File[]} currentFiles - Array file yang sudah diunggah
 * @param {Function} onFileUpload - Callback function untuk menangani file yang diunggah
 */
function FileUpload({ onFileUpload, currentFiles }) {
  const handleFileChange = (e) => {
    const newFiles = Array.from(e.target.files);

    // Cek jika total file tidak melebihi batas
    if (currentFiles.length + newFiles.length > MAX_FILE_COUNT) {
      alert(
        `You can only upload a maximum of ${MAX_FILE_COUNT} files. Please remove some files before uploading.`
      );
      e.target.value = ""; // Reset input file
      return;
    }
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
    e.target.value = "";
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
