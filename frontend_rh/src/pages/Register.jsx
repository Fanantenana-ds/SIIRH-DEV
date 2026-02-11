import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Register.css";

function Register() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    // Vérification des mots de passe
    if (password !== confirmPassword) {
      setError("Les mots de passe ne correspondent pas");
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Erreur lors de la création du compte");
        return;
      }

      setSuccess("Compte créé avec succès ! Vous allez être redirigé...");
      setEmail("");
      setPassword("");
      setConfirmPassword("");

      // Redirection après 2 secondes
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      console.error(err);
      setError("Erreur serveur. Veuillez réessayer.");
    }
  };

  return (
    <div className="register-container">
      <form className="register-box" onSubmit={handleRegister}>
        <h2>Créer un compte</h2>

        {error && <div className="error-msg">{error}</div>}
        {success && <div className="success-msg">{success}</div>}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <div className="password-wrapper">
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Mot de passe"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <span
            className="toggle-password"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? "🙈" : "👁️"}
          </span>
        </div>

        <div className="password-wrapper">
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Confirmer le mot de passe"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </div>

        <button type="submit">Créer le compte</button>

        <div className="login-link">
          <span onClick={() => navigate("/login")}>Déjà un compte ? Se connecter</span>
        </div>
      </form>
    </div>
  );
}

export default Register;
