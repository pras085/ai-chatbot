import React from "react";
import { isAllowedFileType, allowedExtensions } from "../utils/helpers";

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB in bytes
const MAX_FILE_COUNT = 50; // Maksimal 5 file

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
      const fileExt = file.name.split(".").pop().toLowerCase();

      if (!isAllowedFileType(file)) {
        alert(`File type .${fileExt} not allowed`);
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

  return (
    <>
      <input
        type="file"
        id="file-input"
        style={{ display: "none" }}
        onChange={handleFileChange}
        multiple
        accept={allowedExtensions.toString()}
      />
      <input
        type="file"
        id="folder-input"
        style={{ display: "none" }}
        onChange={handleFileChange}
        multiple
        accept={allowedExtensions.toString()}
        webkitdirectory=""
        directory=""
      />
    </>
  );
}

export default FileUpload;
