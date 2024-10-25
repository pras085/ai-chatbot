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
  const { method = "GET", headers = {}, body, requiresAuth = true, ...otherOptions } = options;

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
      localStorage.removeItem("username");
      window.location.href = "/login";
      throw new Error("Authentication failed");
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  } catch (error) {
    if (error.response) {
      console.error("Server error:", error.response.data);
      // Tampilkan pesan error ke pengguna
    } else if (error.request) {
      console.error("Network error:", error.request);
      // Tampilkan pesan error jaringan ke pengguna
    } else {
      console.error("Error:", error.message);
      // Tampilkan pesan error umum ke pengguna
    }
    throw error;
  }
};

export const getUser = async () => {
  const response = await apiRequest("/user");
  return response.json();
};

/**
 * Mengirim pesan chat baru dan menangani respons streaming.
 *
 * @param {string} userId - ID pengguna
 * @param {string} chatId - ID chat
 * @param {string} message - Isi pesan
 * @param {File} file - File yang diunggah (opsional)
 * @param {AbortSignal} signal - Signal untuk abort request (opsional)
 * @param {function} onChunk - Callback untuk setiap chunk pesan
 * @param {function} onDone - Callback ketika streaming selesai
 * @param {function} onError - Callback untuk menangani error
 */
export const sendChatMessage = async (
  userId,
  chatId,
  message,
  files,
  signal,
  onChunk,
  onDone,
  onError,
  activeFeature
) => {
  const formData = new FormData();
  formData.append("message", message);
  formData.append("chat_id", chatId);
  formData.append("user_id", userId);
  if (files && files.length > 0) {
    for (let i = 0; i < files.length; i++) {
      formData.append(`files`, files[i]);
    }
  }
  console.log("FormData contents:", [...formData.entries()]);

  try {
    const response = await fetch(`${API_BASE_URL}/chat/send?feature=${activeFeature}`, {
      method: "POST",
      body: formData,
      signal,
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop();

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(5));
            switch (data.type) {
              case "message":
                onChunk(data.content);
                break;
              case "error":
                onError(new Error(data.content));
                break;
              case "done":
                onDone();
                break;
            }
          } catch (e) {
            console.error("Error parsing SSE data:", e);
          }
        }
      }
    }
  } catch (error) {
    onError(error);
  }
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
export const getUserChats = async (userId, activeFeature) => {
  const response = await apiRequest(`/user/${userId}/chats?feature=${activeFeature}`);
  return response.json();
};

/**
 * Membuat chat baru untuk pengguna tertentu.
 *
 * @param {string} userId - ID pengguna
 * @returns {Promise<Object>} - Objek berisi informasi chat baru
 */
export const createNewChat = async (userId, activeFeature) => {
  console.log("Creating new chat for user:", userId);
  const response = await apiRequest(`/user/${userId}/chats?feature=${activeFeature}`, {
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
 * @param {string} chatId - ID chat
 */
export const deleteChat = async (chatId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chats/${chatId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to delete chat");
    }

    return await response.json();
  } catch (error) {
    console.error("Error deleting chat:", error);
    throw error;
  }
};

export const getContext = async () => {
  const response = await apiRequest("/contexts");
  if (!response.ok) {
    throw new Error("Failed to get context");
  }

  return await response.json();
};

/**
 * Menghapus context tertentuu untuk pengguna tertentu.
 *
 * @param {string} contextID - ID context
 */ export const deleteContext = async (contextID) => {
  try {
    const response = await apiRequest(`/context/${contextID}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to delete context");
    }

    return await response.json();
  } catch (error) {
    console.error("Error deleting context:", error);
    throw error;
  }
};

export const uploadContext = async (formData) => {
  try {
    console.log("Uploading context with formData:", Object.fromEntries(formData));
    const response = await apiRequest("/context", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Server response:", errorData);
      throw new Error(errorData.detail || "Failed to upload context");
    }

    const result = await response.json();
    console.log("Context upload successful:", result);
    return result;
  } catch (error) {
    console.error("Error uploading context:", error);
    throw error;
  }
};
export const login = async (username, password) => {
  const response = await fetch("/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      username: username,
      password: password,
    }),
  });

  if (!response.ok) {
    throw new Error("Login failed");
  }

  const data = await response.json();
  localStorage.setItem("token", data.access_token);
  localStorage.setItem("username", username);
  return data;
};

export const fetchAllRules = async () => {
  const response = await apiRequest("/code-check-rules");
  const data = await response.json();
  return data;
};

export const updateRule = async (feature, rule) => {
  const response = await apiRequest(`/code-check-rules/${feature}`, {
    method: "PUT",
    body: {
      'rule': rule
    },
  });
  return response.json();
}

export const fetchAllKnowledges = async () => {
  const response = await apiRequest("/knowledge-base");
  const data = await response.json();
  return data;
}

export const createKnowledge = async (question, answer) => {
  const response = await apiRequest(`/knowledge-base?question=${question}&answer=${answer}`, {
    method: "POST"
  });
  return response.json();
}

export const deleteKnowledge = async (id) => {
  const response = await apiRequest(`/knowledge-base/${id}`, {
    method: "DELETE"
  });
  return response.json();
}

export const updateKnowledge = async (id, question, answer) => {
  const response = await apiRequest(`/knowledge-base/${id}?question=${question}&answer=${answer}`, {
    method: "PUT"
  });
  return response.json();
}

export const getKnowledgeById = async (id) => {
  const response = await apiRequest(`/knowledge-base/${id}`);
  return response.json();
}