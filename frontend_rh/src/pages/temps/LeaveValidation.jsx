import { useState, useEffect } from "react";
import axios from "../../api/axios";

function LeaveValidation() {
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    fetchPending();
  }, []);

  const fetchPending = async () => {
    const res = await axios.get("/conges/demandes/en-attente");
    setRequests(res.data);
  };

  const approve = async (id) => {
    await axios.post(`/conges/demandes/${id}/approve`);
    fetchPending();
  };

  const reject = async (id) => {
    await axios.post(`/conges/demandes/${id}/reject`);
    fetchPending();
  };

  return (
    <div>
      <h2>Validation des congés</h2>

      <table>
        <thead>
          <tr>
            <th>Employé</th><th>Période</th><th>Type</th><th></th>
          </tr>
        </thead>
        <tbody>
          {requests.map(r => (
            <tr key={r.id}>
              <td>{r.employee.nom} {r.employee.prenom}</td>
              <td>{r.date_debut} → {r.date_fin}</td>
              <td>{r.type}</td>
              <td>
                <button onClick={() => approve(r.id)}>Valider</button>
                <button onClick={() => reject(r.id)}>Refuser</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default LeaveValidation;
