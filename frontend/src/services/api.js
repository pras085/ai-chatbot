const API_BASE_URL = "http://localhost:8000"; // Sesuaikan dengan URL backend Anda

/**
 * Melakukan request API dengan penanganan token otentikasi.
 *
 * @param {string} endpoint - Endpoint API yang akan diakses.
 * @param {Object} options - Opsi untuk request fetch.
 * @param {string} options.method - Metode HTTP (GET, POST, PUT, DELETE, dll).
 * @param {Object} [options.headers] - Header tambahan untuk request.
 * @param {Object|string} [options.body] - Body request untuk metode POST/PUT.
 * @param {boolean} [options.requiresAuth=true] - Apakah request memerlukan otentikasi.
 * @returns {Promise<Response>} - Promise yang resolve ke objek Response.
 * @throws {Error} Jika terjadi kesalahan dalam request atau otentikasi.
 */
export const apiRequest = async (endpoint, options = {}) => {
  const {
    method = "GET",
    headers = {},
    body,
    requiresAuth = true,
    ...otherOptions
  } = options;

  const requestHeaders = new Headers(headers);

  if (requiresAuth) {
    const token = localStorage.getItem("token");
    if (!token) {
      throw new Error("No authentication token found");
    }
    requestHeaders.set("Authorization", `Bearer ${token}`);
  }

  if (!requestHeaders.has("Content-Type") && !(body instanceof FormData)) {
    requestHeaders.set("Content-Type", "application/json");
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method,
      headers: requestHeaders,
      body: body instanceof FormData ? body : JSON.stringify(body),
      ...otherOptions,
    });

    if (response.status === 401 && requiresAuth) {
      localStorage.removeItem("token");
      window.location.href = "/login";
      throw new Error("Authentication failed");
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  } catch (error) {
    console.error(`API request failed for endpoint ${endpoint}:`, error);
    throw error;
  }
};

export const getUser = async () => {
  const response = await apiRequest("/user");
  return response.json();
};

/**
 * Mengirim pesan chat baru.
 *
 * @param {string} userId - ID pengguna
 * @param {number} chatId - ID chat
 * @param {string} message - Isi pesan
 * @param {File} file - File yang diunggah (opsional)
 * @param {AbortSignal} signal - Signal untuk abort request (opsional)
 * @returns {Promise<Response>} - Response dari server
 */
export const sendChatMessage = async (
  userId,
  chatId,
  message,
  file,
  signal
) => {
  const formData = new FormData();
  formData.append("message", message);
  formData.append("chat_id", chatId);
  formData.append("user_id", userId);
  if (file) {
    formData.append("file", file);
  }
  const response = await apiRequest(`/chat/send`, {
    method: "POST",
    body: formData,
    signal,
  });
  return response.json();
};

/**
 * Mengambil pesan-pesan dari chat tertentu.
 *
 * @param {number} chatId - ID chat
 * @returns {Promise<Array>} - Array berisi pesan-pesan chat
 */
export const getChatMessages = async (chatId) => {
  if (!chatId) {
    console.error("Invalid chat ID");
    return;
  }
  const response = await apiRequest(`/chat/${chatId}/messages`);
  const data = await response.json();
  console.log("API response for user chats:", data);
  return data;
};

/**
 * Mengambil daftar chat untuk pengguna tertentu.
 *
 * @param {string} userId - ID pengguna
 * @returns {Promise<Array>} - Array berisi daftar chat pengguna
 */
export const getUserChats = async (userId) => {
  const response = await apiRequest(`/user/${userId}/chats`);
  return response.json();
};

/**
 * Membuat chat baru untuk pengguna tertentu.
 *
 * @param {string} userId - ID pengguna
 * @returns {Promise<Object>} - Objek berisi informasi chat baru
 */
export const createNewChat = async (userId) => {
  console.log("Creating new chat for user:", userId);
  const response = await apiRequest(`/user/${userId}/chats`, {
    method: "POST",
  });
  return response.json();
};
/**
 * Mengunggah file.
 *
 * @param {File} file - File yang akan diunggah
 * @returns {Promise<Object>} - Objek berisi informasi file yang diunggah
 */
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await apiRequest("/files/upload", {
    method: "POST",
    body: formData,
  });
  return response.json();
};

/**
 * Menghapus chat tertentuu untuk pengguna tertentu.
 *
 * @param {string} userId - ID pengguna
 * @param {string} chatId - ID chat
 * @returns {Promise<Object>} - Objek berisi informasi chat baru
 */
export const deleteChat = async (userId, chatId) => {
  const response = await apiRequest(`/api/${userId}chats/${chatId}`, {
    method: "DELETE",
  });
  return response.json();
};
