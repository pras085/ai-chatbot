import { useState, useEffect } from "react";
import { apiRequest } from "../services/api";

export const useUser = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await apiRequest("/user");
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
          setError(null);
        } else {
          throw new Error("Failed to fetch user data");
        }
      } catch (error) {
        console.error("Failed to fetch user data:", error);
        setError(error.message);
        // Hapus token jika ada masalah autentikasi
        if (error.message === "Authentication failed") {
          localStorage.removeItem("token");
        }
      } finally {
        setLoading(false);
      }
    };

    if (localStorage.getItem("token")) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  return { user, loading, error };
};
