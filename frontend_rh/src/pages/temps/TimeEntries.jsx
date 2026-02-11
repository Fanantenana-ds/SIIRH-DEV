import { useState, useEffect } from "react";
import axios from "../../api/axios";

function TimeEntries() {
  const [entries, setEntries] = useState([]);
  const [csvFile, setCsvFile] = useState(null);
  const [manual, setManual] = useState({
    employee_id: "",
    date: "",
    check_in: "",
    check_out: ""
  });

  useEffect(() => {
    fetchEntries();
  }, []);

  const fetchEntries = async () => {
    const res = await axios.get("/temps/pointage");
    setEntries(res.data);
  };

  const importCSV = async () => {
    const form = new FormData();
    form.append("file", csvFile);

    await axios.post("/temps/pointage/import", form);
    fetchEntries();
  };

  const saveManual = async () => {
    await axios.post("/temps/pointage/manual", manual);
    setManual({ employee_id: "", date: "", check_in: "", check_out: "" });
    fetchEntries();
  };

  return (
    <div>
      <h2>Pointage / Temps</h2>

      {/* Import CSV */}
      <div>
        <h3>Import CSV</h3>
        <input type="file" onChange={(e) => setCsvFile(e.target.files[0])} />
        <button onClick={importCSV}>Importer</button>
      </div>

      {/* Saisie manuelle */}
      <div>
        <h3>Saisie manuelle</h3>
        <input placeholder="ID employé" value={manual.employee_id}
          onChange={(e) => setManual({ ...manual, employee_id: e.target.value })}
        />
        <input type="date" value={manual.date}
          onChange={(e) => setManual({ ...manual, date: e.target.value })}
        />
        <input type="time" value={manual.check_in}
          onChange={(e) => setManual({ ...manual, check_in: e.target.value })}
        />
        <input type="time" value={manual.check_out}
          onChange={(e) => setManual({ ...manual, check_out: e.target.value })}
        />
        <button onClick={saveManual}>Enregistrer</button>
      </div>

      {/* Table */}
      <h3>Historique</h3>
      <table>
        <thead>
          <tr>
            <th>ID</th><th>Employé</th><th>Date</th><th>Entrée</th><th>Sortie</th>
          </tr>
        </thead>
        <tbody>
          {entries.map(e => (
            <tr key={e.id}>
              <td>{e.id}</td>
              <td>{e.employee?.nom} {e.employee?.prenom}</td>
              <td>{e.date}</td>
              <td>{e.check_in}</td>
              <td>{e.check_out}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TimeEntries;
