// import React, { useEffect, useState } from "react";
// import api from "../api";
// import Absences from "../components/Absences";
// import Conges from "../components/Conges";
// import Soldes from "../components/Soldes";
// import ExportPaie from "../components/ExportPaie";
// import "../styles/TempsAbsences.css";

// export default function TempsAbsences({ navigateToDashboard }) {
//   const [tab, setTab] = useState("absences");
//   const [employees, setEmployees] = useState([]);

//   // fetch employees once and provide datalist for child components
//   const fetchEmployees = async () => {
//     try {
//       const res = await api.get(`/employes/`);
//       setEmployees(res.data || []);
//     } catch (err) {
//       console.error("Erreur récupération employés :", err);
//     }
//   };

//   useEffect(() => {
//     fetchEmployees();
//   }, []);

//   return (
//     <div className="temps-absences-page">
//       <div className="header">
//         <h2>Module Temps & Absences</h2>
//         <div className="tabs">
//           <button
//             className={tab === "absences" ? "active" : ""}
//             onClick={() => setTab("absences")}
//           >
//             Absences
//           </button>

//           {/* Pointages tab completely removed */}

//           <button
//             className={tab === "conges" ? "active" : ""}
//             onClick={() => setTab("conges")}
//           >
//             Congés
//           </button>
//           <button
//             className={tab === "soldes" ? "active" : ""}
//             onClick={() => setTab("soldes")}
//           >
//             Soldes
//           </button>
//           <button
//             className={tab === "export" ? "active" : ""}
//             onClick={() => setTab("export")}
//           >
//             Export Paie
//           </button>
//         </div>
//       </div>

//       {/* Shared datalist for employee selection used by child components */}
//       <datalist id="employees-list">
//         {employees.map((emp) => (
//           <option key={emp.id} value={emp.id}>
//             {emp.nom} {emp.prenom}
//           </option>
//         ))}
//       </datalist>

//       <div className="tab-wrapper">
//         {tab === "absences" && <Absences employees={employees} />}
//         {tab === "conges" && <Conges employees={employees} />}
//         {tab === "soldes" && <Soldes employees={employees} />}
//         {tab === "export" && <ExportPaie employees={employees} />}
//       </div>
//     </div>
//   );
// }
















import React, { useEffect, useState } from "react";
import api from "../api";
import Soldes from "../components/Soldes";
import ExportPaie from "../components/ExportPaie";
import "../styles/TempsAbsences.css";

export default function TempsAbsences({ navigateToDashboard }) {
  const [tab, setTab] = useState("absences");
  const [employees, setEmployees] = useState([]);
  const [pointages, setPointages] = useState([]);
  const [conges, setConges] = useState([]);
  const [absences, setAbsences] = useState([]);
  const [popupData, setPopupData] = useState(null);
  const [filterEmp, setFilterEmp] = useState("");

  const currentMonth = new Date().getMonth() + 1;
  const currentYear = new Date().getFullYear();
  const daysInMonth = new Date(currentYear, currentMonth, 0).getDate(); // nombre jours du mois courant

  // ---------------- Fetch données ----------------
  const fetchEmployees = async () => {
    try {
      const res = await api.get(`/employes/`);
      setEmployees(res.data || []);
    } catch (err) {
      console.error("Erreur récupération employés :", err);
    }
  };

  const fetchPointages = async () => {
    try {
      const res = await api.get(`/pointages/`);
      setPointages(res.data || []);
    } catch (err) {
      console.error("Erreur pointages :", err);
    }
  };

  const fetchConges = async () => {
    try {
      const res = await api.get(`/conges/`);
      setConges(res.data || []);
    } catch (err) {
      console.error("Erreur congés :", err);
    }
  };

  const fetchAbsences = async () => {
    try {
      const res = await api.get(`/absences/`);
      setAbsences(res.data || []);
    } catch (err) {
      console.error("Erreur absences :", err);
    }
  };

  useEffect(() => {
    fetchEmployees();
    fetchPointages();
    fetchConges();
    fetchAbsences();
  }, []);

  // ---------------- Grouping par employé ----------------
  const employeeList = employees
    .map((emp) => ({
      ...emp,
      pointages: pointages.filter((p) => p.employee_id === emp.id),
      conges: conges.filter((c) => c.employee_id === emp.id),
      absences: absences.filter((a) => a.employee_id === emp.id),
    }))
    .filter((emp) =>
      filterEmp
        ? `${emp.nom} ${emp.prenom}`.toLowerCase().includes(filterEmp.toLowerCase())
        : true
    );

  return (
    <div className="temps-absences-page">
      {/* --- Header --- */}
      <div className="header">
        <h2>Module Temps & Absences</h2>

        <div className="tabs">
          <button className={tab === "absences" ? "active" : ""} onClick={() => setTab("absences")}>Absences</button>
          <button className={tab === "pointages" ? "active" : ""} onClick={() => setTab("pointages")}>Pointages</button>
          <button className={tab === "conges" ? "active" : ""} onClick={() => setTab("conges")}>Congés</button>
          <button className={tab === "soldes" ? "active" : ""} onClick={() => setTab("soldes")}>Soldes</button>
          <button className={tab === "export" ? "active" : ""} onClick={() => setTab("export")}>Export Paie</button>
        </div>

        {/* --- Filtre employé --- */}
        <input
          type="text"
          placeholder="Filtrer par employé..."
          value={filterEmp}
          onChange={(e) => setFilterEmp(e.target.value)}
          style={{ marginTop: "10px", padding: "5px 10px", width: "250px" }}
        />
      </div>

      <div className="tab-wrapper">
        {/* --- Tableau --- */}
        {(tab === "absences" || tab === "pointages" || tab === "conges") && (
          <table>
            <thead>
              <tr style={{ backgroundColor: "green", color: "#fff" }}>
                <th>Nom</th>
                <th>Prénom</th>
                <th>Résumé</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {employeeList.map((emp) => (
                <tr key={emp.id}>
                  <td>{emp.nom}</td>
                  <td>{emp.prenom}</td>
                  <td>
                    {tab === "absences" && `${emp.absences.length} / ${daysInMonth}`}
                    {tab === "pointages" && `${emp.pointages.length} / ${daysInMonth}`}
                    {tab === "conges" && `${emp.conges.length} / ${daysInMonth}`}
                  </td>
                  <td>
                    <button
                      style={{ backgroundColor: "#28a745", color: "#fff" }}
                      onClick={() =>
                        setPopupData({
                          type: tab,
                          data:
                            tab === "absences"
                              ? emp.absences
                              : tab === "pointages"
                              ? emp.pointages
                              : emp.conges,
                          emp,
                        })
                      }
                    >
                      ⋮
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {tab === "soldes" && <Soldes employees={employeeList} />}
        {tab === "export" && <ExportPaie employees={employeeList} />}
      </div>

      {/* --- Popup Détails --- */}
      {popupData && (
        <div
          className="popup-overlay"
          onClick={() => setPopupData(null)}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "rgba(0,0,0,0.5)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 999,
          }}
        >
          <div
            className="popup-content"
            onClick={(e) => e.stopPropagation()}
            style={{
              backgroundColor: "#fff",
              padding: "20px",
              borderRadius: "6px",
              width: "400px",
              maxHeight: "80%",
              overflowY: "auto",
            }}
          >
            <h4>
              {popupData.type === "absences"
                ? "Détail Absences"
                : popupData.type === "conges"
                ? "Détail Congés"
                : "Détail Pointages"}{" "}
              - {popupData.emp.nom} {popupData.emp.prenom}
            </h4>

            {popupData.data.length > 0 ? (
              <ul>
                {popupData.data.map((item, idx) => (
                  <li key={idx}>
                    {popupData.type === "absences" &&
                      `${item.date} : ${item.raison || item.type_absence}`}
                    {popupData.type === "conges" &&
                      `${item.dateDebut} - ${item.dateFin} : ${item.type} (${item.duree} jours)`}
                    {popupData.type === "pointages" &&
                      `${item.date} : Entrée ${item.heure_entree} - Sortie ${item.heure_sortie}`}
                  </li>
                ))}
              </ul>
            ) : (
              <p>Aucune donnée</p>
            )}

            <button
              onClick={() => setPopupData(null)}
              style={{
                marginTop: "10px",
                backgroundColor: "#dc3545",
                color: "#fff",
                padding: "6px 12px",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Fermer
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
