/**
 * Format ukuran file ke dalam bentuk yang mudah dibaca
 * @param {number} bytes - Ukuran file dalam bytes
 * @returns {string} Ukuran file yang diformat
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

export function escapeHTML(value) {
  if (typeof value !== "string") {
    // Jika bukan string, konversi ke JSON string
    value = JSON.stringify(value);
  }
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

export const formatDate = (dateString) => {
  const options = { year: "numeric", month: "short", day: "numeric" };
  return new Date(dateString).toLocaleDateString(undefined, options);
};
export const allowedExtensions = [
  // Gambar
  "jpg",
  "jpeg",
  "png",
  "gif",
  "svg",
  // PDF
  "pdf",
  // Codingan
  "txt",
  "js",
  "css",
  "html",
  "json",
  "xml",
  "py",
  "java",
  "cpp",
  "c",
  "h",
  "cs",
  "php",
  "rb",
  "go",
  "ts",
  "dart",
];

export function isAllowedFileType(file) {
  const allowedMimeTypes = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/svg+xml",
    "application/pdf",
    "text/plain",
    "text/javascript",
    "text/css",
    "text/html",
    "text/dart",
    "application/json",
    "application/xml",
    "text/x-python",
    "text/x-java",
    "text/x-c++src",
  ];

  const fileExtension = file.name.split(".").pop().toLowerCase();

  return (
    allowedMimeTypes.includes(file.type) ||
    allowedExtensions.includes(fileExtension)
  );
}
