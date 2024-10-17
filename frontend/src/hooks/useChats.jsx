import { useState, useCallback } from "react";
import { getUserChats } from "../services/api";

export const useChats = (userId, activeFeature) => {
  const [chats, setChats] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchChats = useCallback(async () => {
    if (!userId) return;
    setIsLoading(true);
    setError(null);
    try {
      const fetchedChats = await getUserChats(userId, activeFeature);
      setChats(fetchedChats);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  return { chats, isLoading, error, fetchChats, setChats };
};
export default useChats;
