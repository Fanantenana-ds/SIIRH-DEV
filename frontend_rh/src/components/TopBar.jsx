import React, { useState, useEffect } from "react";
import { Sun, Moon } from "lucide-react";

export default function TopBar() {
  const [theme, setTheme] = useState(localStorage.getItem("theme") || "light");
  const [lang, setLang] = useState(localStorage.getItem("lang") || "fr");

  useEffect(() => {
    document.body.className = theme;
    localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    localStorage.setItem("lang", lang);
  }, [lang]);

  const toggleTheme = () => {
    setTheme(theme === "light" ? "dark" : "light");
  };

  return (
    <div className="topbar">
      <div className="topbar-right">
        <select
          value={lang}
          onChange={(e) => setLang(e.target.value)}
          className="lang-select"
        >
          <option value="fr">FR</option>
          <option value="en">EN</option>
        </select>

        <button onClick={toggleTheme} className="theme-btn">
          {theme === "light" ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </div>
  );
}
