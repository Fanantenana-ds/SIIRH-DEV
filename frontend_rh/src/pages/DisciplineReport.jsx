


// // src/pages/DisciplineReport.jsx
// import React, { useState } from "react";
// import "./Discipline.css";

// const DisciplineReport = () => {
//     const [summary, setSummary] = useState("");
//     const [employeeStatement, setEmployeeStatement] = useState("");
//     const [managerStatement, setManagerStatement] = useState("");
//     const [additionalProofs, setAdditionalProofs] = useState([]);
//     const [finalDecision, setFinalDecision] = useState("");
//     const [daysSuspension, setDaysSuspension] = useState(0);
//     const [justification, setJustification] = useState("");

//     const decisions = [
//         "Avertissement simple",
//         "Avertissement final",
//         "Mise à pied",
//         "Mutation disciplinaire",
//         "Licenciement",
//         "Aucune sanction"
//     ];

//     const handleProofs = (e) => setAdditionalProofs([...e.target.files]);
//     const handleSubmit = (e) => {
//         e.preventDefault();
//         alert("Compte-rendu enregistré !");
//         setSummary(""); setEmployeeStatement(""); setManagerStatement(""); setAdditionalProofs([]);
//         setFinalDecision(""); setDaysSuspension(0); setJustification("");
//     };

//     return (
//         <form className="discipline-form" onSubmit={handleSubmit}>
//             <h3>Résumé entretien</h3>
//             <textarea value={summary} onChange={e => setSummary(e.target.value)} required />
//             <h3>Déclarations employé</h3>
//             <textarea value={employeeStatement} onChange={e => setEmployeeStatement(e.target.value)} />
//             <h3>Déclarations manager</h3>
//             <textarea value={managerStatement} onChange={e => setManagerStatement(e.target.value)} />
//             <h3>Preuves complémentaires</h3>
//             <input type="file" multiple onChange={handleProofs} />
//             <h3>Décision finale</h3>
//             <select value={finalDecision} onChange={e => setFinalDecision(e.target.value)} required>
//                 <option value="">--Sélectionner--</option>
//                 {decisions.map(d => <option key={d} value={d}>{d}</option>)}
//             </select>
//             {finalDecision === "Mise à pied" && <label>Nombre de jours : <input type="number" value={daysSuspension} onChange={e => setDaysSuspension(e.target.value)} min={1} /></label>}
//             <h3>Justification</h3>
//             <textarea value={justification} onChange={e => setJustification(e.target.value)} required />
//             <button type="submit" className="btn-submit">Enregistrer Compte-rendu</button>
//         </form>
//     );
// };

// export default DisciplineReport;






// src/pages/DisciplineReport.jsx
import React, { useState } from "react";
import "./Discipline.css";

const DisciplineReport = () => {
    const [summary, setSummary] = useState("");
    const [employeeStatement, setEmployeeStatement] = useState("");
    const [managerStatement, setManagerStatement] = useState("");
    const [additionalProofs, setAdditionalProofs] = useState([]);
    const [finalDecision, setFinalDecision] = useState("");
    const [daysSuspension, setDaysSuspension] = useState(0);
    const [justification, setJustification] = useState("");

    const decisions = [
        "Avertissement simple",
        "Avertissement final",
        "Mise à pied",
        "Mutation disciplinaire",
        "Licenciement",
        "Aucune sanction"
    ];

    const handleProofs = (e) => setAdditionalProofs([...e.target.files]);

    const handleSubmit = (e) => {
        e.preventDefault();
        alert("Compte-rendu enregistré !");
        // reset
        setSummary(""); setEmployeeStatement(""); setManagerStatement(""); setAdditionalProofs([]);
        setFinalDecision(""); setDaysSuspension(0); setJustification("");
    };

    return (
        <form className="discipline-form" onSubmit={handleSubmit}>
            <h3>Résumé entretien</h3>
            <textarea value={summary} onChange={e => setSummary(e.target.value)} placeholder="Résumé de l'entretien" required />

            <h3>Déclarations employé</h3>
            <textarea value={employeeStatement} onChange={e => setEmployeeStatement(e.target.value)} placeholder="Déclaration de l'employé" />

            <h3>Déclarations manager</h3>
            <textarea value={managerStatement} onChange={e => setManagerStatement(e.target.value)} placeholder="Déclaration du manager" />

            <h3>Preuves complémentaires</h3>
            <input type="file" multiple onChange={handleProofs} />

            <h3>Décision finale</h3>
            <select value={finalDecision} onChange={e => setFinalDecision(e.target.value)} required>
                <option value="">--Sélectionner la décision--</option>
                {decisions.map(d => <option key={d} value={d}>{d}</option>)}
            </select>

            {finalDecision === "Mise à pied" && (
                <label>Nombre de jours :
                    <input type="number" value={daysSuspension} onChange={e => setDaysSuspension(e.target.value)} min={1} placeholder="Nombre de jours" />
                </label>
            )}

            <h3>Justification</h3>
            <textarea value={justification} onChange={e => setJustification(e.target.value)} placeholder="Justification détaillée" required />

            <button type="submit" className="btn-submit">Enregistrer Compte-rendu</button>
        </form>
    );
};

export default DisciplineReport;
