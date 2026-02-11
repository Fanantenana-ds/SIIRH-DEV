// import React, { useEffect, useState } from "react";
// import "../styles/listeEntretiens.css";

// export default function ListeEntretiens() {
//   const [entretiens, setEntretiens] = useState([]);
//   const [error, setError] = useState(null);

//   useEffect(() => {
//     const fetchData = async () => {
//       try {
//         // Fetch candidats et entretiens depuis le backend
//         const [entretienRes, candidatRes] = await Promise.all([
//           fetch("http://localhost:8000/api/entretiens"),
//           fetch("http://localhost:8000/rh/candidatures"),
//         ]);

//         if (!entretienRes.ok) throw new Error("Erreur fetch entretiens");
//         if (!candidatRes.ok) throw new Error("Erreur fetch candidatures");

//         const entretiensData = await entretienRes.json();
//         const candidatsData = await candidatRes.json();

//         const merged = entretiensData.map((e) => {
//           const c = candidatsData.find((x) => x.id === parseInt(e.cand_id));
//           const totalScore =
//             (Number(e.tech_score) +
//               Number(e.soft_score) +
//               Number(e.cult_score) +
//               Number(e.lang_score) +
//               Number(e.disp_score) +
//               Number(e.sal_score)) /
//             6;

//           return {
//             ...e,
//             score: totalScore,
//             candidat: c
//               ? `${c.nom?.toUpperCase()} ${c.prenom || ""}`
//               : `ID-${e.cand_id}`,
//           };
//         });

//         merged.sort((a, b) => b.score - a.score);
//         setEntretiens(merged);
//       } catch (err) {
//         console.error(err);
//         setError(err.message);
//       }
//     };

//     fetchData();
//   }, []);

//   return (
//     <div className="liste-entretien-container">
//       <h2>📋 Liste des entretiens réalisés</h2>

//       {error && <p className="error-message">{error}</p>}

//       <table className="entretien-table">
//         <thead>
//           <tr>
//             <th>Réf. Offre</th>
//             <th>Candidat</th>
//             <th>Type / Tour</th>
//             <th>Date</th>
//             <th>Évaluateur</th>
//             <th>Score</th>
//             <th>Décision</th>
//           </tr>
//         </thead>
//         <tbody>
//           {entretiens.length === 0 ? (
//             <tr>
//               <td colSpan="7" style={{ textAlign: "center" }}>
//                 Aucun entretien enregistré.
//               </td>
//             </tr>
//           ) : (
//             entretiens.map((e) => (
//               <tr key={e.id}>
//                 <td>{e.job_ref}</td>
//                 <td>{e.candidat}</td>
//                 <td>{e.round_type}</td>
//                 <td>
//                   {new Date(e.date).toLocaleDateString("fr-FR", {
//                     day: "2-digit",
//                     month: "2-digit",
//                     year: "numeric",
//                   })}
//                 </td>
//                 <td>{e.evaluators}</td>
//                 <td>
//                   {Math.round(e.score * 10) / 10}/5
//                 </td>
//                 <td
//                   className={`decision ${
//                     e.decision === "GO"
//                       ? "go"
//                       : e.decision === "HOLD"
//                       ? "hold"
//                       : "nogo"
//                   }`}
//                 >
//                   {e.decision}
//                 </td>
//               </tr>
//             ))
//           )}
//         </tbody>
//       </table>
//     </div>
//   );
// }


import React, { useEffect, useState } from "react";
import "../styles/listeEntretiens.css";

export default function ListeEntretiens() {
  const [entretiens, setEntretiens] = useState([]);
  const [candidats, setCandidats] = useState([]);

  // Charger les entretiens depuis le backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [entretienRes, candidatRes] = await Promise.all([
          fetch("http://localhost:8000/api/entretiens"),
          fetch("http://localhost:8000/rh/candidatures"),
        ]);

        const entretiensData = await entretienRes.json();
        const candidatsData = await candidatRes.json();

        // Calcul du score total et association avec candidat
        const merged = entretiensData.map((e) => {
          const c = candidatsData.find((x) => x.id === parseInt(e.cand_id));
          const total =
            (Number(e.tech_score) +
              Number(e.soft_score) +
              Number(e.cult_score) +
              Number(e.lang_score) +
              Number(e.disp_score) +
              Number(e.sal_score)) /
            6;

          return {
            ...e,
            score: total,
            candidat: c
              ? `${c.nom?.toUpperCase()} ${c.prenom || ""}`
              : `ID-${e.cand_id}`,
          };
        });

        // Tri par score décroissant
        merged.sort((a, b) => b.score - a.score);

        setEntretiens(merged);
        setCandidats(candidatsData);
      } catch (error) {
        console.error("Erreur de chargement:", error);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="liste-entretien-container">
      <h2>📋 Liste des entretiens réalisés</h2>
      <table className="entretien-table">
        <thead>
          <tr>
            <th>Rang</th> {/* Nouvelle colonne */}
            <th>Réf. Offre</th>
            <th>Candidat</th>
            <th>Type / Tour</th>
            <th>Date</th>
            <th>Évaluateur</th>
            <th>Score</th>
            <th>Décision</th>
          </tr>
        </thead>
        <tbody>
          {entretiens.length === 0 ? (
            <tr>
              <td colSpan="8" style={{ textAlign: "center" }}>
                Aucun entretien enregistré.
              </td>
            </tr>
          ) : (
            entretiens.map((e, index) => (
              <tr key={e.id}>
                <td>{index + 1}</td> {/* Rang basé sur le score décroissant */}
                <td>{e.job_ref}</td>
                <td>{e.candidat}</td>
                <td>{e.round_type}</td>
                <td>
                  {new Date(e.date).toLocaleDateString("fr-FR", {
                    day: "2-digit",
                    month: "2-digit",
                    year: "numeric",
                  })}
                </td>
                <td>{e.evaluators}</td>
                <td className="score-cell">
                  <span className="score-value">
                    {Math.round(e.score * 10) / 10}/5
                  </span>
                  <div className="score-bar">
                    <div
                      className="score-fill"
                      style={{ width: `${(e.score / 5) * 100}%` }}
                    ></div>
                  </div>
                </td>
                <td
                  className={`decision ${
                    e.decision === "GO"
                      ? "go"
                      : e.decision === "HOLD"
                      ? "hold"
                      : "nogo"
                  }`}
                >
                  {e.decision}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
