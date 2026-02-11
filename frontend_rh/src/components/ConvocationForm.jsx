import React, { useState } from "react";
import "../styles/ConvocationForm.css";

function ConvocationForm({ onSuccess }) {
  const [formData, setFormData] = useState({
    date: "",
    heure: "",
    lieu: "",
    interval_minute: 15,
  });
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("⏳ Création de la convocation...");

    try {
      const response = await fetch("http://localhost:8000/convocations/create-convocation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error("Erreur lors de la création");

      const data = await response.json();
      setMessage("✅ Convocation créée avec succès !");
      console.log("Convocation:", data);

      // Réinitialiser formulaire
      setFormData({ date: "", heure: "", lieu: "", interval_minute: 15 });

      if (onSuccess) onSuccess(); // callback si besoin pour refresh
    } catch (err) {
      console.error(err);
      setMessage("❌ Erreur lors de la création de la convocation.");
    }
  };

  return (
    <div className="convocation-container">
      <h2>Créer une convocation</h2>

      <form onSubmit={handleSubmit} className="convocation-form">
        <label>Date :</label>
        <input
          type="date"
          name="date"
          value={formData.date}
          onChange={handleChange}
          required
        />

        <label>Heure :</label>
        <input
          type="time"
          name="heure"
          value={formData.heure}
          onChange={handleChange}
          required
        />

        <label>Lieu :</label>
        <input
          type="text"
          name="lieu"
          placeholder="Ex : Siège CODEL - Antananarivo"
          value={formData.lieu}
          onChange={handleChange}
          required
        />

        <label>Intervalle (minutes) :</label>
        <input
          type="number"
          name="interval_minute"
          value={formData.interval_minute}
          onChange={handleChange}
          min={1}
        />

        <button type="submit">💾 Créer convocation</button>
      </form>

      {message && <p className="status-message">{message}</p>}
    </div>
  );
}

export default ConvocationForm;
