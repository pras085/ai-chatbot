import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faBrain,
  faCode,
  faCheck,
  faHeadset,
  faSignOutAlt,
  faFile,
  faGear,
  faSpellCheck,
  faFolder,
} from "@fortawesome/free-solid-svg-icons";
import "../styles/HomePage.css";
import { ReactComponent as MuatmuatIcon } from "../assets/logo-muatmuat.svg";
import { apiRequest } from "../services/api";
import { useFeature } from "../contexts/FeatureContext";
import FileUpload from "../components/FileUpload";
import ModalUpload from "../components/ModalUpload";

;
const HomePage = () => {
  const navigate = useNavigate();
  const { setActiveFeature } = useFeature();
  const [showModal, setShowModal] = useState(false);

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

  return (
    <>
    <ModalUpload isOpen={showModal} onClose={() => setShowModal(false)}/>
    <div className="home-container">
      <div className="header">
        {/* <MuatmuatIcon className="home-title" /> */}
        {/* {
          localStorage.getItem("username") === "superadmin" && 
          <button onClick={handleSettigsClick} >
            <FontAwesomeIcon icon={faGear} /> Setting
          </button>
        } */}
        {/* <button onClick={handleLogout} className="logout-button">
          <FontAwesomeIcon icon={faSignOutAlt} /> Logout
        </button> */}
      </div>
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