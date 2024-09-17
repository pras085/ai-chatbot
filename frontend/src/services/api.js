const API_BASE_URL = "http://localhost:8000"; // Sesuaikan dengan URL backend Anda

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

  const response = await fetch(`${API_BASE_URL}/chat/send`, {
    method: "POST",
    body: formData,
    signal,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response;
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
  try {
    const response = await fetch(`${API_BASE_URL}/chat/${chatId}/messages`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching messages:", error);
  }
};

/**
 * Mengambil daftar chat untuk pengguna tertentu.
 *
 * @param {string} userId - ID pengguna
 * @returns {Promise<Array>} - Array berisi daftar chat pengguna
 */
export const getUserChats = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/${userId}/chats`);
    if (!response.ok) throw new Error("Failed to fetch user chats");
    return await response.json();
  } catch (error) {
    console.error("Error fetching user chats:", error);
    throw error;
  }
};

/**
 * Membuat chat baru untuk pengguna tertentu.
 *
 * @param {string} userId - ID pengguna
 * @returns {Promise<Object>} - Objek berisi informasi chat baru
 */
export const createNewChat = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/${userId}/chats`, {
      method: "POST",
    });
    if (!response.ok) throw new Error("Failed to create new chat");
    return await response.json();
  } catch (error) {
    console.error("Error creating new chat:", error);
    throw error;
  }
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

  const response = await fetch(`${API_BASE_URL}/files/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};
