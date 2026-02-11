import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Login.css";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const [showForgot, setShowForgot] = useState(false);
  const [forgotEmail, setForgotEmail] = useState("");
  const [forgotMessage, setForgotMessage] = useState("");
  const [showResetStep, setShowResetStep] = useState(1);
  const [resetToken, setResetToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showToken, setShowToken] = useState(false);

  const [showRegister, setShowRegister] = useState(false);
  const [registerEmail, setRegisterEmail] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");
  const [registerMessage, setRegisterMessage] = useState("");
  const [showRegisterPassword, setShowRegisterPassword] = useState(false);

  // === Login Function ===
  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      // Clear any previous session before login
      localStorage.clear();

      const res = await fetch("http://127.0.0.1:8000/auth/login_rh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Erreur d’authentification");
        return;
      }

      // Set token and user info for this session
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));

      navigate("/rh/dashboard");
    } catch (err) {
      setError("Erreur de connexion au serveur");
      console.error(err);
    }
  };

  // === Forgot Password Step 1 ===
  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setForgotMessage("");

    try {
      const res = await fetch("http://127.0.0.1:8000/auth/forgot_password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: forgotEmail }),
      });

      const data = await res.json();

      if (!res.ok) {
        setForgotMessage(data.detail || "Adresse e-mail introuvable.");
        return;
      }

      setForgotMessage("Un code a été envoyé à votre e-mail.");
      setShowResetStep(2);
    } catch (err) {
      setForgotMessage("Erreur serveur. Vérifiez votre connexion.");
    }
  };

  // === Forgot Password Step 2 ===
  const handleResetPassword = async (e) => {
    e.preventDefault();
    setForgotMessage("");

    try {
      const res = await fetch("http://127.0.0.1:8000/auth/reset_password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: resetToken, new_password: newPassword }),
      });

      const data = await res.json();

      if (!res.ok) {
        setForgotMessage(data.detail || "Erreur lors de la réinitialisation.");
        return;
      }

      setForgotMessage("Mot de passe modifié avec succès !");
      setTimeout(() => {
        setShowForgot(false);
        setShowResetStep(1);
        setResetToken("");
        setNewPassword("");
      }, 2000);
    } catch (err) {
      setForgotMessage("Erreur serveur. Veuillez réessayer.");
    }
  };

  // === Register Function (Secure - No Auto Login) ===
  const handleRegister = async (e) => {
    e.preventDefault();
    setRegisterMessage("");

    try {
      // Clear any previous session before registering
      localStorage.clear();

      const res = await fetch("http://127.0.0.1:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: registerEmail, password: registerPassword }),
      });

      const data = await res.json();

      if (!res.ok) {
        setRegisterMessage(data.detail || "Erreur lors de la création du compte.");
        return;
      }

      // Inform user to login manually
      setRegisterMessage("Compte créé avec succès ! Veuillez vous connecter.");

      setTimeout(() => {
        setShowRegister(false);
        setRegisterEmail("");
        setRegisterPassword("");
        setRegisterMessage("");
      }, 2000);
    } catch (err) {
      setRegisterMessage("Erreur serveur. Veuillez réessayer.");
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleLogin} className="login-box">
        <h2>Connexion RH</h2>

        {error && <div className="error-msg">{error}</div>}

        <label>Email</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />

        <label>Mot de passe</label>
        <div className="password-field">
          <input
            type={showPassword ? "text" : "password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <span onClick={() => setShowPassword(!showPassword)} className="show-hide">
            {showPassword ? "🙈" : "👁️"}
          </span>
        </div>

        <div className="options">
          <button type="button" onClick={() => setShowForgot(true)} className="link-btn">
            Mot de passe oublié ?
          </button>
          <button type="button" onClick={() => setShowRegister(true)} className="link-btn">
            Créer un compte
          </button>
        </div>

        <button type="submit" className="submit-btn">Se connecter</button>
      </form>

      {/* --- Forgot Password Modal --- */}
      {showForgot && (
        <div className="overlay">
          <div className="modal">
            <button className="close-btn" onClick={() => { setShowForgot(false); setShowResetStep(1); }}>✕</button>

            {showResetStep === 1 && (
              <form onSubmit={handleForgotPassword}>
                <h3>Réinitialiser le mot de passe</h3>
                <label>Email</label>
                <input
                  type="email"
                  value={forgotEmail}
                  onChange={(e) => setForgotEmail(e.target.value)}
                  required
                />
                <button type="submit" className="submit-btn">Envoyer le code</button>
              </form>
            )}

            {showResetStep === 2 && (
              <form onSubmit={handleResetPassword}>
                <h3>Entrer le code et nouveau mot de passe</h3>
                <label>Code reçu</label>
                <div className="password-field">
                  <input
                    type={showToken ? "text" : "password"}
                    value={resetToken}
                    onChange={(e) => setResetToken(e.target.value)}
                    required
                  />
                  <span onClick={() => setShowToken(!showToken)} className="show-hide">
                    {showToken ? "🙈" : "👁️"}
                  </span>
                </div>

                <label>Nouveau mot de passe</label>
                <div className="password-field">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                  />
                  <span onClick={() => setShowPassword(!showPassword)} className="show-hide">
                    {showPassword ? "🙈" : "👁️"}
                  </span>
                </div>

                <button type="submit" className="submit-btn">Changer le mot de passe</button>
                {forgotMessage && <p className="info-msg">{forgotMessage}</p>}
              </form>
            )}
          </div>
        </div>
      )}

      {/* --- Register Modal --- */}
      {showRegister && (
        <div className="overlay">
          <div className="modal">
            <button className="close-btn" onClick={() => setShowRegister(false)}>✕</button>
            <form onSubmit={handleRegister}>
              <h3>Créer un compte</h3>
              <label>Email</label>
              <input
                type="email"
                value={registerEmail}
                onChange={(e) => setRegisterEmail(e.target.value)}
                required
              />
              <label>Mot de passe</label>
              <div className="password-field">
                <input
                  type={showRegisterPassword ? "text" : "password"}
                  value={registerPassword}
                  onChange={(e) => setRegisterPassword(e.target.value)}
                  required
                />
                <span onClick={() => setShowRegisterPassword(!showRegisterPassword)} className="show-hide">
                  {showRegisterPassword ? "🙈" : "👁️"}
                </span>
              </div>
              <button type="submit" className="submit-btn">Créer le compte</button>
              {registerMessage && <p className="info-msg">{registerMessage}</p>}
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Login;
