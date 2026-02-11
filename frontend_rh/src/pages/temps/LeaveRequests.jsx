import { useState, useEffect } from "react";
import axios from "../../api/axios";

function LeaveRequests() {
  const [solde, setSolde] = useState({ paye: 0, non_paye: 0 });
  const [requests, setRequests] = useState([]);
  const [form, setForm] = useState({
    type: "",
    date_debut: "",
    date_fin: "",
    motif: ""
  });

  useEffect(() => {
    fetchSolde();
    fetchRequests();
  }, []);

  const fetchSolde = async () => {
    const res = await axios.get("/conges/solde");
    setSolde(res.data);
  };

  const fetchRequests = async () => {
    const res = await axios.get("/conges/demandes/me");
    setRequests(res.data);
  };

  const sendRequest = async () => {
    await axios.post("/conges/demandes", form);
    setForm({ type: "", date_debut: "", date_fin: "", motif: "" });
    fetchRequests();
    fetchSolde();
  };

  return (
    <div>
      <h2>Mes demandes de congé</h2>

      <div>
        <p><b>Solde congés payés :</b> {solde.paye} j</p>
        <p><b>Solde congés non payés :</b> {solde.non_paye} j</p>
      </div>

      <h3>Faire une demande</h3>

      <select value={form.type}
        onChange={(e) => setForm({ ...form, type: e.target.value })}
      >
        <option value="">--Type--</option>
        <option value="paye">Payé</option>
        <option value="non_paye">Non payé</option>
        <option value="maladie">Maladie</option>
      </select>

      <input type="date" value={form.date_debut}
        onChange={(e) => setForm({ ...form, date_debut: e.target.value })}
      />

      <input type="date" value={form.date_fin}
        onChange={(e) => setForm({ ...form, date_fin: e.target.value })}
      />

      <input placeholder="Motif" value={form.motif}
        onChange={(e) => setForm({ ...form, motif: e.target.value })}
      />

      <button onClick={sendRequest}>Envoyer</button>

      <h3>Historique</h3>
      <table>
        <thead>
          <tr>
            <th>Date</th><th>Type</th><th>Statut</th>
          </tr>
        </thead>
        <tbody>
          {requests.map(r => (
            <tr key={r.id}>
              <td>{r.date_debut} → {r.date_fin}</td>
              <td>{r.type}</td>
              <td>{r.statut}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default LeaveRequests;
