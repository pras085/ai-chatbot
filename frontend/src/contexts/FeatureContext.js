import React, { createContext, useState, useContext } from "react";

const FeatureContext = createContext();

export const FeatureProvider = ({ children }) => {
  const [activeFeature, setActiveFeature] = useState("GENERAL");

  return (
    <FeatureContext.Provider value={{ activeFeature, setActiveFeature }}>
      {children}
    </FeatureContext.Provider>
  );
};

export const useFeature = () => useContext(FeatureContext);
