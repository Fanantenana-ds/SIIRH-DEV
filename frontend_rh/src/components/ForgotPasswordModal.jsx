import React, { useState } from "react";

export default function ForgotPasswordModal({ onClose }) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState(null); // 'loading' | 'success' | 'error'
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) {
      setMessage("Veuillez saisir une adresse e-mail.");
      return;
    }
    setStatus("loading");
    setMessage("");

    try {
      // API endpoint attendu : POST /api/auth/forgot-password { email }
      const res = await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!res.ok) {
        const err = await res.json().catch(()=>({message:'Erreur serveur'}));
        throw new Error(err.message || "Erreur");
      }

      setStatus("success");
      setMessage("Un e-mail de réinitialisation a été envoyé si l'adresse existe.");
    } catch (err) {
      setStatus("error");
      setMessage(err.message || "Erreur lors de l'envoi.");
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <h3>Mot de passe oublié</h3>
        <form onSubmit={handleSubmit} className="forgot-form">
          <input
            type="email"
            placeholder="Votre e-mail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <button type="submit" disabled={status==="loading"} className="param-btn">
            {status==="loading" ? "Envoi..." : "Envoyer le lien"}
          </button>

          {message && <p className={`msg ${status}`}>{message}</p>}

          <button type="button" className="btn-secondary" onClick={onClose}>
            Fermer
          </button>
        </form>
      </div>
    </div>
  );
}
