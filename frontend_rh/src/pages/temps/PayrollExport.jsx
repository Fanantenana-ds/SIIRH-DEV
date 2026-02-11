import { useState } from "react";
import axios from "../../api/axios";

function PayrollExport() {
  const [periode, setPeriode] = useState({
    date_debut: "",
    date_fin: ""
  });
  const [report, setReport] = useState(null);

  const generate = async () => {
    const res = await axios.post("/paie/export", periode);
    setReport(res.data);
  };

  return (
    <div>
      <h2>Export Paie</h2>

      <input type="date" value={periode.date_debut}
        onChange={(e) => setPeriode({ ...periode, date_debut: e.target.value })}
      />
      <input type="date" value={periode.date_fin}
        onChange={(e) => setPeriode({ ...periode, date_fin: e.target.value })}
      />

      <button onClick={generate}>Générer</button>

      {report && (
        <div>
          <h3>Résultat</h3>
          <p>Heures normales : {report.heures_normales}</p>
          <p>Heures supplémentaires : {report.hs}</p>
          <p>Absences : {report.absences}</p>
          <p>Congés non payés : {report.conges_non_payes}</p>

          <a href={report.pdf_url} target="_blank">Télécharger PDF</a>
        </div>
      )}
    </div>
  );
}

export default PayrollExport;
