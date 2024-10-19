import React from "react";
import { useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faBrain,
  faCode,
  faCheck,
  faHeadset,
  faSignOutAlt,
} from "@fortawesome/free-solid-svg-icons";
import "../styles/HomePage.css";
import { ReactComponent as MuatmuatIcon } from "../assets/logo-muatmuat.svg";
import { apiRequest } from "../services/api";
import { useFeature } from "../contexts/FeatureContext";

const HomePage = () => {
  const navigate = useNavigate();
  const { setActiveFeature } = useFeature();

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
    },
  ];

  const handleFeatureClick = (featureType) => {
    setActiveFeature(featureType);
    navigate("/chats");  // Arahkan ke halaman daftar chat
  };

  const handleLogout = async () => {
    try {
      await apiRequest("/logout", { method: "POST" });
      localStorage.removeItem("token");
      navigate("/login");
    } catch (error) {
      console.error("Logout failed:", error);
      localStorage.removeItem("token");
      navigate("/login");
    }
  };

  return (
    <div className="home-container">
      <div className="header">
        <MuatmuatIcon className="home-title" />
        <button onClick={handleLogout} className="logout-button">
          <FontAwesomeIcon icon={faSignOutAlt} /> Logout
        </button>
      </div>
      <div className="feature-grid">
        {features.map((feature, index) => (
          <div key={index} className="feature-card">
            <div className="feature-header">
              {feature.icon}
              <h2 className="feature-title">{feature.title}</h2>
            </div>
            <div className="feature-content">
              <p className="feature-description">{feature.description}</p>
              <button
                onClick={() => handleFeatureClick(feature.featureType)}
                className="feature-button"
              >
                Start Chat
              </button>
              <br></br>
              {feature.featureType === "CODE_CHECK" && (
                <div className="feature-buttons-container">
                  <button
                    onClick={() => handleFeatureClick("CODE_CHECK_FRONTEND")}
                    className="feature-button"
                  >
                    Frontend
                  </button>
                  <button
                    onClick={() => handleFeatureClick("CODE_CHECK_BACKEND")}
                    className="feature-button"
                  >
                    Backend
                  </button>
                  <button
                    onClick={() => handleFeatureClick("CODE_CHECK_APPS")}
                    className="feature-button"
                  >
                    Apps
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HomePage;