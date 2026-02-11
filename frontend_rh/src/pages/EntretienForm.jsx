import React, { useState } from "react";
import "../styles/Entretien.css";
import StarRating from "../components/StarRating";

export default function EntretienForm() {
  const [formData, setFormData] = useState({
    jobRef: "",
    candId: "",
    roundType: "",
    date: "",
    time: "",
    evaluators: "",
    techScore: 0,
    softScore: 0,
    cultScore: 0,
    langScore: 0,
    dispScore: 0,
    salScore: 0,
    notes: "",
    risks: "",
    decision: "GO",
    proposalType: "",
    proposalSalary: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleStarChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost:8000/api/entretiens", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_ref: formData.jobRef,
          cand_id: formData.candId,
          round_type: formData.roundType,
          date: formData.date,
          time: formData.time,
          evaluators: formData.evaluators,
          tech_score: formData.techScore,
          soft_score: formData.softScore,
          cult_score: formData.cultScore,
          lang_score: formData.langScore,
          disp_score: formData.dispScore,
          sal_score: formData.salScore,
          notes: formData.notes,
          risks: formData.risks,
          decision: formData.decision,
          proposal_type: formData.proposalType,
          proposal_salary: formData.proposalSalary,
        }),
      });

      if (!response.ok) throw new Error("Erreur lors de l’enregistrement");

      alert("✅ Entretien enregistré avec succès !");
      window.location.href = "/rh/liste-entretiens";
    } catch (error) {
      console.error(error);
      alert("❌ Une erreur est survenue lors de l’enregistrement.");
    }
  };

  return (
    <div className="entretien-container">
      <h2>🧩 SIIRH — Grille d’entretien & Scorecard</h2>

      <form className="entretien-form" onSubmit={handleSubmit}>
        <div className="form-section">
          <label>Réf. offre</label>
          <input name="jobRef" onChange={handleChange} required />

          <label>ID Candidat</label>
          <input name="candId" onChange={handleChange} required />

          <label>Type / Tour</label>
          <input name="roundType" onChange={handleChange} placeholder="RH / Technique..." />

          <label>Date</label>
          <input type="date" name="date" onChange={handleChange} required />

          <label>Heure</label>
          <input type="time" name="time" onChange={handleChange} required />

          <label>Évaluateurs</label>
          <input name="evaluators" onChange={handleChange} placeholder="Nom complet" />
        </div>

        <h3>⭐ Critères d’évaluation</h3>
        <div className="criteria-section">
          <div>
            <label>Expertise technique</label>
            <StarRating value={formData.techScore} onChange={(v) => handleStarChange("techScore", v)} />
          </div>

          <div>
            <label>Soft skills / Communication</label>
            <StarRating value={formData.softScore} onChange={(v) => handleStarChange("softScore", v)} />
          </div>

          <div>
            <label>Culture / Valeurs</label>
            <StarRating value={formData.cultScore} onChange={(v) => handleStarChange("cultScore", v)} />
          </div>

          <div>
            <label>Langues / Client-facing</label>
            <StarRating value={formData.langScore} onChange={(v) => handleStarChange("langScore", v)} />
          </div>

          <div>
            <label>Disponibilité / Mobilité</label>
            <StarRating value={formData.dispScore} onChange={(v) => handleStarChange("dispScore", v)} />
          </div>

          <div>
            <label>Pertinence salaire vs budget</label>
            <StarRating value={formData.salScore} onChange={(v) => handleStarChange("salScore", v)} />
          </div>
        </div>

        <h3>📝 Observations & Preuves</h3>
        <textarea name="notes" rows="3" onChange={handleChange} placeholder="Notes libres, remarques..." />

        <h3>⚠️ Risques / Drapeaux</h3>
        <textarea name="risks" rows="2" onChange={handleChange} placeholder="Gaps, mobilité, remarques..." />

        <h3>✅ Recommandation & Suite</h3>
        <div className="form-section">
          <label>Recommandation</label>
          <select name="decision" onChange={handleChange}>
            <option value="GO">GO</option>
            <option value="HOLD">HOLD</option>
            <option value="NO-GO">NO-GO</option>
          </select>

          <label>Proposition contrat</label>
          <select name="decision" onChange={handleChange}>
            <option value="CDI">CDI</option>
            <option value="CDD">CDD</option>
            <option value="Stage">Stage</option>
          </select>

          <label>Salaire cible</label>
          <input name="proposalSalary" onChange={handleChange} placeholder="ex: 1 200 000 Ar" />
        </div>

        <button type="submit" className="submit-btn">
          💾 Soumettre
        </button>
      </form>
    </div>
  );
}
