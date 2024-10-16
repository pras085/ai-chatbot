import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useFeature } from '../contexts/FeatureContext';

const FeatureCard = ({ title, description, icon, featureType }) => {
    const navigate = useNavigate();
    const { setActiveFeature } = useFeature();

    const handleClick = () => {
        setActiveFeature(featureType);
        navigate('/chat'); // Navigasi ke halaman chat
    };

    return (
        <div className="feature-card">
            <div className="feature-header">
                {icon}
                <h2 className="feature-title">{title}</h2>
            </div>
            <div className="feature-content">
                <p className="feature-description">{description}</p>
                <button onClick={handleClick} className="feature-button">
                    Start Chat
                </button>
            </div>
        </div>
    );
};

export default FeatureCard;