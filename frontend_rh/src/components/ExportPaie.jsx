import React, { useEffect, useState } from "react";
import axios from "axios";
import jsPDF from "jspdf";
import "jspdf-autotable";

export default function ExportPaie() {
  const [exportData, setExportData] = useState([]);
  const [showExportOptions, setShowExportOptions] = useState(false);

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:8000/api/export_paie/");
        setExportData(res.data || []);
      } catch (err) {
        console.error("Erreur récupération données :", err);
      }
    };
    fetchData();
  }, []);

  const handleExport = (format) => {
    if (!exportData.length) return alert("Aucune donnée à exporter");

    const rows = exportData.map(e => ({
      Employe: `${e.nom} ${e.prenom}`,
      Mois: e.mois,
      Salaire: e.salaire,
      "Heures normales": e.heures_normales,
      "Heures sup": e.heures_supplementaires,
      "Absences non payées": e.absences_non_payees,
      "Congés non payés": e.conges_non_payes
    }));

    if (format === "csv") {
      const header = Object.keys(rows[0]);
      const lines = rows.map(r => Object.values(r).join(','));
      const csvContent = "data:text/csv;charset=utf-8," + [header.join(','), ...lines].join("\n");
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.href = encodedUri;
      link.download = "export_paie.csv";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } else if (format === "pdf") {
      const doc = new jsPDF();
      doc.text("Export Paie", 14, 15);
      doc.autoTable({
        startY: 20,
        head: [Object.keys(rows[0])],
        body: rows.map(r => Object.values(r))
      });
      doc.save("export_paie.pdf");
    }

    setShowExportOptions(false); // cacher options après export
  };

  return (
    <div className="tab-content">
      <h3>Export Paie</h3>
      <div style={{ marginBottom: 12, position: "relative" }}>
        <button onClick={() => setShowExportOptions(!showExportOptions)}>
          Télécharger Export
        </button>

        {showExportOptions && (
          <div style={{
            display: "flex",
            gap: "8px",
            position: "absolute",
            top: "100%",
            left: 0,
            marginTop: "4px",
            background: "#f0f0f0",
            padding: "6px",
            borderRadius: "4px",
            boxShadow: "0 2px 5px rgba(0,0,0,0.2)"
          }}>
            <button onClick={() => handleExport("csv")}>CSV</button>
            <button onClick={() => handleExport("pdf")}>PDF</button>
          </div>
        )}
      </div>

      <table className="data-table" border={1} cellPadding={5}>
        <thead>
          <tr>
            <th>Employé</th>
            <th>Mois</th>
            <th>Salaire</th>
            <th>Heures normales</th>
            <th>Heures sup</th>
            <th>Absences non payées</th>
            <th>Congés non payés</th>
          </tr>
        </thead>
        <tbody>
          {exportData.map(e => (
            <tr key={e.employee_id}>
              <td>{e.nom} {e.prenom}</td>
              <td>{e.mois}</td>
              <td>{e.salaire}</td>
              <td>{e.heures_normales}</td>
              <td>{e.heures_supplementaires}</td>
              <td>{e.absences_non_payees}</td>
              <td>{e.conges_non_payes}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
