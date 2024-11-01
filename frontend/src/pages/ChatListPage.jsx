import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import ChatList from "../components/ChatList";
import { deleteContext, deleteChat, getContext, uploadContext, createNewChat } from "../services/api";
import useUser from "../hooks/useUser";
import { useChats } from "../hooks/useChats";
import ProductInformation from "../components/ProductInformation";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronLeft, faChevronRight } from "@fortawesome/free-solid-svg-icons";
import { useFeature } from '../contexts/FeatureContext';
import CodeCheckDetail from "../components/CodeCheckDetail";

function ChatListPage() {
  const navigate = useNavigate();
  const { user, loading: userLoading } = useUser();
  const [contexts, setContexts] = useState([]);
  const [showProductInfo, setShowProductInfo] = useState(true);
  const { activeFeature } = useFeature();
  const { chats, isLoading, error, fetchChats, setChats } = useChats(user?.id, activeFeature);

  useEffect(() => {
    if (user && user.id) {
      fetchChats();
      fetchContext();
    }
  }, [user, fetchChats]);


  const fetchContext = async () => {
    try {
      const response = await getContext();
      console.log('Fetched context:', response);
      if (Array.isArray(response)) {
        setContexts(response);
      } else {
        console.warn('Expected array, received:', response);
        setContexts([]); // Atur menjadi array kosong jika respons tidak sesuai
      }
    } catch (error) {
      console.error('Failed to fetch context:', error);
      setContexts([]);
    }
  };

  const handleContextUpdate = async (formData) => {
    try {
      console.log('Attempting to update context...');
      const updatedContext = await uploadContext(formData);
      console.log('Context updated successfully:', updatedContext);
      setContexts(prevContexts => [...prevContexts, updatedContext]);
      // Tambahkan notifikasi sukses untuk pengguna di sini jika diperlukan
    } catch (error) {
      console.error('Failed to update context:', error);
      setContexts([]);
      // Tambahkan notifikasi error untuk pengguna di sini
    }
  };
  const handleDeleteContext = async (contextId) => {
    try {
      await deleteContext(contextId);
      setContexts(prevContexts => prevContexts.filter(ctx => ctx.id !== contextId));
      console.log('Context deleted successfully');
      // Tambahkan notifikasi sukses untuk pengguna di sini
    } catch (error) {
      console.error('Failed to delete context:', error);
      // Tambahkan notifikasi error untuk pengguna di sini
    }
  };

  const handleSelectChat = useCallback((chatId) => {
    console.log("chat id:", chatId);
    navigate(`/chat/${chatId}`);
  }, [navigate]);

  const handleNewChat = useCallback((newChat) => {
    setChats((prevChats) => [newChat, ...prevChats]);
    navigate(`/chat/${newChat.id}`);
  }, [navigate, setChats]);

  const createNewChats = async () => {
    const newChat = await createNewChat(user.id, activeFeature);
    handleNewChat(newChat);
    return newChat;
  };

  const handleDeleteChat = useCallback(async (deletedChatId) => {
    try {
      await deleteChat(deletedChatId);
      setChats((prevChats) => prevChats.filter(chat => chat.chat_id !== deletedChatId));
      if (user && user.id) {
        fetchChats(user.id);
      }
    } catch (error) {
      console.error("Failed to delete chat:", error);
      alert("Failed to delete chat. Please try again.");
    }
  }, [user, fetchChats, setChats]);

  if (userLoading) return <div>Loading user data...</div>;
  if (!user) return <div>Please log in to view chats.</div>;
  if (isLoading) return <div>Loading chats...</div>;
  if (error) return <div>{error}</div>;

  // console.log('Token:', localStorage.getItem('token'));
  // console.log('User ID:', user.id);
  // console.log('Current context:', contexts);

  return (
    <div className="flex h-[90vh] justify-between overflow-hidden">
      {activeFeature.includes("CODE_CHECK") && 
        <div className={`flex-1 max-w-full p-5 pt-10 transition-all duration-300 ease-in-out ${!showProductInfo ? 'max-w-full justify-center flex' : ''}`}>
          <CodeCheckDetail feature={activeFeature} />
        </div>
      }

      <div className={`flex-1 max-w-full p-5 transition-all duration-300 ease-in-out ${!showProductInfo ? 'max-w-full justify-center flex' : ''}`}>
        <ChatList
          chats={chats}
          onSelectChat={handleSelectChat}
          onNewChat={createNewChats}
          onDeleteChat={handleDeleteChat}
          userId={user.id}
        />
      </div>
      
      {activeFeature == "GENERAL" &&
        <div className={`relative transition-all duration-300 ease-in-out ${showProductInfo ? 'w-96' : 'w-0'} flex-none`}>
          {/* <button
            className="absolute top-1/2 left-[-50px] transform -translate-y-1/2 bg-blue-500 text-white w-12 h-12 rounded-full flex items-center justify-center z-10 transition-all duration-300 ease-in-out"
            onClick={() => setShowProductInfo(!showProductInfo)}
            >
            <FontAwesomeIcon icon={showProductInfo ? faChevronRight : faChevronLeft} />
          </button> */}
          <div className={`h-full w-96 p-5 bg-white shadow-md overflow-y-auto transition-transform duration-300 ease-in-out ${showProductInfo ? '' : 'translate-x-full'}`}>
            <ProductInformation
              contexts={contexts}
              onContextUpdate={handleContextUpdate}
              onContextDelete={handleDeleteContext}
            />
          </div>
        </div>
      }

    </div>
  );
}

export default ChatListPage;
