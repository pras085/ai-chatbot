import React from "react";
import { useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faBrain,
  faCode,
  faCheck,
  faHeadset,
} from "@fortawesome/free-solid-svg-icons";
import "../styles/HomePage.css"; // Pastikan file CSS ini ada
import { ReactComponent as MuatmuatIcon } from "../assets/logo-muatmuat.svg";

const HomePage = () => {
  const navigate = useNavigate();

  const features = [
    {
      title: "General AI Assistant",
      description: "AI yang mampu menjawab berbagai topik termasuk coding.",
      icon: faBrain,
      route: "/chats",
    },
    {
      title: "Standard Code Checking",
      description: "Menilai kesesuaian code dengan standar perusahaan.",
      icon: faCheck,
      route: "/code-check",
    },
    {
      title: "Code Helper",
      description: "Menambahkan dokumentasi dan komentar pada code project.",
      icon: faCode,
      route: "/code-helper",
    },
    {
      title: "Customer Service Chatbot",
      description: "Menjawab pertanyaan terkait produk perusahaan.",
      icon: faHeadset,
      route: "/cs-chatbot",
    },
  ];

  return (
    <div className="home-container">
      <MuatmuatIcon className="home-title" />
      <div className="feature-grid">
        {features.map((feature, index) => (
          <div key={index} className="feature-card">
            <div className="feature-header">
              <FontAwesomeIcon
                icon={feature.icon}
                size="2x"
                className="feature-icon"
              />
              <h2 className="feature-title">{feature.title}</h2>
            </div>
            <div className="feature-content">
              <p className="feature-description">{feature.description}</p>
              <button
                onClick={() => navigate(feature.route)}
                className="feature-button"
              >
                {feature.title === "General AI Assistant"
                  ? "Start Chat"
                  : "Access Feature"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HomePage;
