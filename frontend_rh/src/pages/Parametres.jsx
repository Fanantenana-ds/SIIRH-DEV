import React, { useState, useEffect } from "react";
import axios from "axios";
import "./Parametres.css";

export default function Parametres() {
  const [darkMode, setDarkMode] = useState(document.body.classList.contains("dark-mode"));
  const [lang, setLang] = useState(localStorage.getItem("lang") || "fr");

  // SMTP settings
  const [smtpEmail, setSmtpEmail] = useState("");
  const [smtpPassword, setSmtpPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isSmtpOpen, setIsSmtpOpen] = useState(false);

  // Retour backend
  const [msg, setMsg] = useState({ text: "", type: "" });

  // Dark mode
  useEffect(() => {
    if (darkMode) document.body.classList.add("dark-mode");
    else document.body.classList.remove("dark-mode");
  }, [darkMode]);

  // Langue
  useEffect(() => {
    localStorage.setItem("lang", lang);
  }, [lang]);

  const toggleDarkMode = () => setDarkMode(prev => !prev);
  const handleLangChange = e => setLang(e.target.value);

  // Envoyer SMTP au backend
  const handleSmtpSubmit = async e => {
    e.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:8000/api/settings/smtp", {
        email: smtpEmail,
        password: smtpPassword
      });
      if (response.data.success) {
        setMsg({ text: lang === "fr" ? "Configuration SMTP enregistrée !" : "SMTP settings saved!", type: "success" });
      } else {
        setMsg({ text: lang === "fr" ? "Erreur lors de l'enregistrement." : "Error saving settings.", type: "error" });
      }
    } catch (error) {
      setMsg({ text: lang === "fr" ? "Erreur serveur." : "Server error.", type: "error" });
    }
  };

  return (
    <div className="param-wrapper">
      <div className="param-container">
        <div className="param-card">
          <h2>{lang === "fr" ? "Paramètres du système" : "System Settings"}</h2>

          {/* Mode sombre */}
          <div className="param-item">
            <span className="param-label">{lang === "fr" ? "Mode sombre :" : "Dark Mode:"}</span>
            <button className={`param-btn ${darkMode ? "active" : ""}`} onClick={toggleDarkMode}>
              {darkMode ? (lang === "fr" ? "Activé" : "Enabled") : (lang === "fr" ? "Désactivé" : "Disabled")}
            </button>
          </div>

          {/* Langue */}
          <div className="param-item">
            <span className="param-label">{lang === "fr" ? "Langue :" : "Language:"}</span>
            <select className="param-select" value={lang} onChange={handleLangChange}>
              <option value="fr">Français</option>
              <option value="en">English</option>
            </select>
          </div>

          {/* SMTP profil-like menu */}
          <div className="param-item">
            <span className="param-label">{lang === "fr" ? "SMTP :" : "SMTP:"}</span>
            <button className="param-btn" onClick={() => setIsSmtpOpen(prev => !prev)}>...</button>
          </div>

          {isSmtpOpen && (
            <div className="profile-menu smtp-menu">
              <form onSubmit={handleSmtpSubmit}>
                <div className="input-group">
                  <label>{lang === "fr" ? "Adresse e-mail SMTP" : "SMTP Email"}</label>
                  <input
                    type="email"
                    placeholder={lang === "fr" ? "Entrez l'adresse email" : "Enter email"}
                    value={smtpEmail}
                    onChange={e => setSmtpEmail(e.target.value)}
                    required
                  />
                </div>

                <div className="input-group" style={{ position: "relative" }}>
                  <label>{lang === "fr" ? "App Password" : "App Password"}</label>
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder={lang === "fr" ? "Entrez le mot de passe" : "Enter password"}
                    value={smtpPassword}
                    onChange={e => setSmtpPassword(e.target.value)}
                    required
                  />
                  <span className="eye-icon" onClick={() => setShowPassword(!showPassword)}>
                    {showPassword ? "👁️" : "🙈"}
                  </span>
                </div>

                <button type="submit" className="param-btn btn-submit">
                  {lang === "fr" ? "Enregistrer" : "Save"}
                </button>

                {msg.text && <div className={`msg ${msg.type}`} style={{ marginTop: "10px" }}>{msg.text}</div>}
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
