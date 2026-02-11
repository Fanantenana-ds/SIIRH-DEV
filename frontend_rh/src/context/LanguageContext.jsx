// src/context/LanguageContext.jsx
import React, { createContext, useState, useEffect } from "react";

export const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [lang, setLang] = useState("fr");

  useEffect(() => {
    const savedLang = localStorage.getItem("lang") || "fr";
    setLang(savedLang);
  }, []);

  const changeLang = (newLang) => {
    setLang(newLang);
    localStorage.setItem("lang", newLang);
  };

  return (
    <LanguageContext.Provider value={{ lang, changeLang }}>
      {children}
    </LanguageContext.Provider>
  );
};
