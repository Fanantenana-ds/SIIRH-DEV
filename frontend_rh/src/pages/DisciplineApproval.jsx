

// // src/pages/DisciplineApproval.jsx
// import React, { useState } from "react";
// import "./Discipline.css";

// const DisciplineApproval = () => {
//     const [role, setRole] = useState("");
//     const [decision, setDecision] = useState("");
//     const [comment, setComment] = useState("");

//     const roles = ["Manager", "RH", "Direction"];
//     const decisions = ["Approuvé", "Rejeté"];

//     const handleSubmit = (e) => {
//         e.preventDefault();
//         alert("Décision enregistrée !");
//         setRole(""); setDecision(""); setComment("");
//     };

//     return (
//         <form className="discipline-form" onSubmit={handleSubmit}>
//             <h3>Approbation</h3>

//             <label>Rôle :
//                 <select value={role} onChange={e => setRole(e.target.value)} required>
//                     <option value="">--Sélectionner le rôle--</option>
//                     {roles.map(r => <option key={r} value={r}>{r}</option>)}
//                 </select>
//             </label>

//             <label>Décision :
//                 <select value={decision} onChange={e => setDecision(e.target.value)} required>
//                     <option value="">--Sélectionner la décision--</option>
//                     {decisions.map(d => <option key={d} value={d}>{d}</option>)}
//                 </select>
//             </label>

//             <label>Commentaire :
//                 <textarea value={comment} onChange={e => setComment(e.target.value)} placeholder="Ajouter un commentaire" required />
//             </label>

//             <button type="submit" className="btn-submit">Valider</button>
//         </form>
//     );
// };

// export default DisciplineApproval;



// =========================================================
//   DISCIPLINE REPORT — PARTIE 3
//   Compte-rendu final d’un dossier disciplinaire
//   Misy commentaires madio tsara & logique backend ready
// =========================================================

import React, { useState } from "react";
import "./Discipline.css";

const DisciplineReport = ({ onSaveReport }) => {

    // =======================
    //     STATES PRINCIPAUX
    // =======================
    const [summary, setSummary] = useState("");                // Résumé de l'entretien
    const [employeeStatement, setEmployeeStatement] = useState(""); // Déclaration employé
    const [managerStatement, setManagerStatement] = useState("");   // Déclaration manager
    const [additionalProofs, setAdditionalProofs] = useState([]);   // Preuves complémentaires
    const [finalDecision, setFinalDecision] = useState("");         // Décision finale
    const [daysSuspension, setDaysSuspension] = useState("");       // Durée mise à pied
    const [justification, setJustification] = useState("");         // Justification décision

    // ==========================
    //    OPTIONS DÉCISION FINALE
    // ==========================
    const decisions = [
        "Avertissement simple",
        "Avertissement final",
        "Mise à pied",
        "Mutation disciplinaire",
        "Licenciement",
        "Aucune sanction"
    ];

    // ==========================
    //      IMPORT DE FICHIERS
    // ==========================
    const handleProofs = (e) => {
        setAdditionalProofs([...e.target.files]);
    };

    // =======================================
    //       VALIDATION FORMULAIRE
    //       (Hiantso backend atsy ho atsy)
    // =======================================
    const handleSubmit = (e) => {
        e.preventDefault();

        const reportData = {
            summary,
            employeeStatement,
            managerStatement,
            additionalProofs,
            finalDecision,
            daysSuspension: finalDecision === "Mise à pied" ? daysSuspension : null,
            justification
        };

        onSaveReport(reportData); // handefa any amin'ny parent (backend any aoriana)

        alert("Compte-rendu enregistré avec succès !");

        // reset
        setSummary("");
        setEmployeeStatement("");
        setManagerStatement("");
        setAdditionalProofs([]);
        setFinalDecision("");
        setDaysSuspension("");
        setJustification("");
    };

    return (
        <form className="discipline-form" onSubmit={handleSubmit}>

            <h3 className="form-section-title">Résumé de l'entretien</h3>
            <textarea
                value={summary}
                placeholder="Décrivez ici le déroulement de l'entretien..."
                onChange={(e) => setSummary(e.target.value)}
                required
            />

            <h3 className="form-section-title">Déclaration de l'employé</h3>
            <textarea
                value={employeeStatement}
                placeholder="Déclaration ou explication de l'employé..."
                onChange={(e) => setEmployeeStatement(e.target.value)}
            />

            <h3 className="form-section-title">Déclaration du manager</h3>
            <textarea
                value={managerStatement}
                placeholder="Commentaires ou remarques du manager..."
                onChange={(e) => setManagerStatement(e.target.value)}
            />

            <h3 className="form-section-title">Preuves complémentaires</h3>
            <input type="file" multiple onChange={handleProofs} />

            <h3 className="form-section-title">Décision Finale</h3>
            <select
                value={finalDecision}
                onChange={(e) => setFinalDecision(e.target.value)}
                required
            >
                <option value="">-- Sélectionner la décision --</option>
                {decisions.map((d) => (
                    <option key={d} value={d}>{d}</option>
                ))}
            </select>

            {finalDecision === "Mise à pied" && (
                <label>
                    Nombre de jours :
                    <input
                        type="number"
                        min="1"
                        placeholder="Ex : 3"
                        value={daysSuspension}
                        onChange={(e) => setDaysSuspension(e.target.value)}
                        required
                    />
                </label>
            )}

            <h3 className="form-section-title">Justification de la décision</h3>
            <textarea
                value={justification}
                placeholder="Expliquez pourquoi cette décision a été retenue..."
                onChange={(e) => setJustification(e.target.value)}
                required
            />

            <div className="form-buttons">
                <button type="submit" className="btn-submit">
                    Enregistrer le compte-rendu
                </button>
            </div>
        </form>
    );
};

export default DisciplineReport;
