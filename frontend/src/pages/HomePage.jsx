import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faBrain,
  faCode,
  faCheck,
  faHeadset,
  faFile,
  faSpellCheck,
} from "@fortawesome/free-solid-svg-icons";
import "../styles/HomePage.css";
import { useFeature } from "../contexts/FeatureContext";
import ModalUpload from "../components/ModalUpload";
import { createNewChat } from "../services/api";
import { useUser } from "../hooks/useUser";
import { sendChatMessage } from "../services/api";
import LoadingOverlay from "../components/LoadingOverlay";

const HomePage = () => {
  const navigate = useNavigate();
  const { setActiveFeature } = useFeature();
  const { activeFeature } = useFeature();
  const [showModal, setShowModal] = useState(false);
  const [currentFiles, setCurrentFiles] = useState([]);
  const { user } = useUser();
  const [isGenerating, setIsGenerating] = useState(false);
  const abortControllerRef = useRef(null);
  const [messages, setMessages] = useState([]);




  const features = [
    {
      title: "General AI Assistant",
      description: "AI yang mampu menjawab berbagai topik termasuk coding.",
      icon: <FontAwesomeIcon icon={faBrain} size="2x" className="feature-icon" />,
      featureType: "GENERAL",
    },
    {
      title: "Standard Code Checking",
      description: "Menilai kesesuaian code dengan standar perusahaan.",
      icon: <FontAwesomeIcon icon={faCheck} size="2x" className="feature-icon" />,
      featureType: "CODE_CHECK",
    },
    {
      title: "Code Helper",
      description: "Menambahkan dokumentasi dan komentar pada code project.",
      icon: <FontAwesomeIcon icon={faCode} size="2x" className="feature-icon" />,
      featureType: "CODE_HELPER",
    },
    {
      title: "Customer Service Chatbot",
      description: "Menjawab pertanyaan terkait produk perusahaan.",
      icon: <FontAwesomeIcon icon={faHeadset} size="2x" className="feature-icon" />,
      featureType: "CS_CHATBOT",
    },{
      title: "Document Checking",
      description: "Membantu proses review dokumen.",
      icon: <FontAwesomeIcon icon={faFile} size="2x" className="feature-icon" />,
      featureType: "DOCUMENT_CHECKING",
    },
    ,{
      title: "Quick Code Checking",
      description: "Pilih dan periksa code langsung.",
      icon: <FontAwesomeIcon icon={faSpellCheck} size="2x" className="feature-icon" />,
      featureType: "CODE_CHECK",
      quick: true,
    },
  ];

  const handleFeatureClick = (featureType, quick) => {
    setActiveFeature(featureType);
    if (quick) {
      setShowModal(true);
    }
    else {
      navigate("/chats");  // Arahkan ke halaman daftar chat
    }
  };

  const handleQuicCodeCheck = async () => {
    // create new chat
    const newChat = await createNewChat(user.id, activeFeature);
    const chatId = newChat.id;
    const message = "Periksa kode pada file berikut ini";

    setIsGenerating(true);
    const newMessage = { content: message, type: "user-message" };
    setMessages(prevMessages => [...prevMessages, newMessage]);

    abortControllerRef.current = new AbortController();

    try {
      await sendChatMessage(
        user.id,
        chatId,
        message,
        currentFiles,
        abortControllerRef.current.signal,
        (chunk) => {
          setMessages(prevMessages => {
            const lastMessage = prevMessages[prevMessages.length - 1];
            if (lastMessage.type === "bot-message") {
              return [
                ...prevMessages.slice(0, -1),
                { ...lastMessage, content: lastMessage.content + chunk }
              ];
            } else {
              return [...prevMessages, { content: chunk, type: "bot-message" }];
            }
          });
        },
        () => {
          setIsGenerating(false);
          setCurrentFiles([]);  // Clear the current files after sending
        },
        (error) => {
          console.error("Error in chat:", error);
          setMessages(prevMessages => [
            ...prevMessages,
            { content: "An error occurred. Please try again.", type: "bot-message" }
          ]);
          setIsGenerating(false);
        },
        activeFeature
      );
    } catch (error) {
      console.error("Failed to send message:", error);
      setIsGenerating(false);
    }
  
    // navigate to new chat
    navigate(`/chat/${chatId}`);
    setShowModal(false);
  };

  return (
    <>
    <LoadingOverlay isLoading={isGenerating} />
    <ModalUpload 
      isOpen={showModal} 
      onClose={() => setShowModal(false)} 
      files={currentFiles} 
      setFiles={setCurrentFiles}
      process={handleQuicCodeCheck}
    />
    <div className="home-container">
      <div className="grid grid-cols-4 gap-6 w-full 
                xl:grid-cols-4 
                lg:grid-cols-3 
                md:grid-cols-2 
                sm:grid-cols-1">
        {features.map((feature, index) => (
          <div key={index} className="feature-card">
            <div className="feature-header">
              {feature.icon}
              <h2 className="feature-title">{feature.title}</h2>
            </div>
            <div className="feature-content">
              <p className="feature-description">{feature.description}</p>
              {feature.featureType !== 'CODE_CHECK' && (
                <button
                  onClick={() => handleFeatureClick(feature.featureType)}
                  className="feature-button"
                >
                  Start Chat
                </button> 
              )}
              {feature.featureType === "CODE_CHECK" && (
                <>
                  <div className="feature-buttons-container">
                    <button
                      onClick={() => handleFeatureClick("CODE_CHECK_FRONTEND", feature.quick)}
                      className="feature-button"
                    >
                      Frontend
                    </button>
                    <button
                      onClick={() => handleFeatureClick("CODE_CHECK_BACKEND", feature.quick)}
                      className="feature-button"
                    >
                      Backend
                    </button>
                    <button
                      onClick={() => handleFeatureClick("CODE_CHECK_APPS", feature.quick)}
                      className="feature-button"
                    >
                      Apps
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
    </>
  );
};

export default HomePage;