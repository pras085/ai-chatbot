import { useState, useEffect } from "react";
import { getUser } from "../services/api";

export function useUser() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const userData = await getUser();
        setUser(userData);
      } catch (err) {
        console.error("Failed to fetch user data:", err);
        setError(err.message);
        // Hapus token jika ada masalah autentikasi
        if (err.message === "Unauthorized") {
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
}

export default useUser;