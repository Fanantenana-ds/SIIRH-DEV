// src/context/SystemContext.jsx
import React, { createContext, useContext, useState, useEffect } from "react";

const SystemContext = createContext();

export function SystemProvider({ children }) {
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("darkMode") === "true";
  });

  const [language, setLanguage] = useState(() => {
    return localStorage.getItem("language") || "fr";
  });

  useEffect(() => {
    localStorage.setItem("darkMode", darkMode);
    document.body.classList.toggle("dark-mode", darkMode);
  }, [darkMode]);

  useEffect(() => {
    localStorage.setItem("language", language);
  }, [language]);

  return (
    <SystemContext.Provider value={{ darkMode, setDarkMode, language, setLanguage }}>
      {children}
    </SystemContext.Provider>
  );
}

export function useSystem() {
  return useContext(SystemContext);
}
