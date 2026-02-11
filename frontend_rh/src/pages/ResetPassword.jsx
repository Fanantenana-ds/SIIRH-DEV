import { useState } from "react";
import "../styles/ResetPassword.css";

function ResetPassword({ onClose }) {
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [step, setStep] = useState(1);
  const [message, setMessage] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showToken, setShowToken] = useState(false);

  // Étape 1: envoyer l'email
  const handleRequestLink = async (e) => {
    e.preventDefault();
    setMessage("");

    try {
      const res = await fetch("http://127.0.0.1:8000/auth/forgot_password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const data = await res.json();
      if (!res.ok) {
        setMessage(data.detail || "Adresse e-mail introuvable.");
        return;
      }

      setMessage("Un code de vérification a été envoyé à votre e-mail.");
      setStep(2);
    } catch {
      setMessage("Erreur de connexion au serveur.");
    }
  };

  // Étape 2: réinitialiser le mot de passe
  const handleResetPassword = async (e) => {
    e.preventDefault();
    setMessage("");

    try {
      const res = await fetch("http://127.0.0.1:8000/auth/reset_password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: newPassword }),
      });

      const data = await res.json();
      if (!res.ok) {
        setMessage(data.detail || "Erreur lors de la réinitialisation.");
        return;
      }

      setMessage("Mot de passe modifié avec succès ! Redirection...");
      setTimeout(() => onClose(), 2000);
    } catch {
      setMessage("Erreur serveur. Veuillez réessayer.");
    }
  };

  return (
    <div className="popup-overlay">
      <div className="popup-box">
        <span className="close-btn" onClick={onClose}>✕</span>

        <h3>Réinitialiser le mot de passe</h3>
        {message && <p className="info">{message}</p>}

        {step === 1 && (
          <form onSubmit={handleRequestLink}>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <button type="submit">Envoyer le code</button>
          </form>
        )}

        {step === 2 && (
          <form onSubmit={handleResetPassword}>
            <div className="input-group">
              <input
                type={showToken ? "text" : "password"}
                placeholder="Code reçu"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                required
              />
              <span
                className="toggle-password"
                onClick={() => setShowToken(!showToken)}
              >
                {showToken ? "🙈" : "👁️"}
              </span>
            </div>

            <div className="password-wrapper">
              <input
                type={showPassword ? "text" : "password"}
                placeholder="Nouveau mot de passe"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />
              <span
                className="toggle-password"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? "🙈" : "👁️"}
              </span>
            </div>

            <button type="submit">Changer le mot de passe</button>
          </form>
        )}
      </div>
    </div>
  );
}

export default ResetPassword;
