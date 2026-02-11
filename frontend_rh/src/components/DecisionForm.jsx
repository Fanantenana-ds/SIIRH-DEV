import React, { useState } from "react";

export default function DecisionForm({ type = "discipline", caseId, candidatId, onSuccess }) {
  const [decisionType, setDecisionType] = useState("");
  const [notes, setNotes] = useState("");
  const [message, setMessage] = useState("");

  const handleGenerate = async () => {
    if (!decisionType) return alert("Sélectionnez un type de décision");

    setMessage("⏳ Génération de la décision en cours...");

    try {
      let url = "";
      let payload = { decision_type: decisionType, decision_notes: notes };

      if (type === "discipline") {
        url = `http://localhost:8000/discipline/cases/${caseId}/decision`;
      } else if (type === "candidature") {
        url = `http://localhost:8000/rh/candidatures/${candidatId}/decision`;
      } else {
        throw new Error("Type invalide");
      }

      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error("Erreur lors de la génération");

      const data = await response.json();
      setMessage("✅ Décision générée avec succès !");
      console.log("Decision PDF:", data);

      // Ouvrir PDF automatique si Discipline
      if (type === "discipline" && data.pdf_url) window.open(data.pdf_url, "_blank");

      setDecisionType("");
      setNotes("");

      if (onSuccess) onSuccess();
    } catch (err) {
      console.error(err);
      setMessage("❌ Erreur lors de la génération de la décision.");
    }
  };

  return (
    <div className="decision-form">
      <select value={decisionType} onChange={(e) => setDecisionType(e.target.value)}>
        <option value="">Sélectionner décision</option>
        <option value="Avertissement">Avertissement</option>
        <option value="Mise à pied">Mise à pied</option>
        <option value="Licenciement">Licenciement</option>
      </select>

      <textarea
        placeholder="Notes / Commentaire"
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
      />

      <button onClick={handleGenerate}>Générer Décision PDF</button>

      {message && <p className="status-message">{message}</p>}
    </div>
  );
}
