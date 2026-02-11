import React, { useState } from "react";
import { uploadEvidence } from "../services/disciplineService";

export default function DisciplineDetailModal({ selectedCase, onClose, onUpdate }) {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    if (!file) return;
    await uploadEvidence(selectedCase.id, file);
    alert("Fichier uploadé avec succès !");
    onUpdate();
  };

  return (
    <div className="modal">
      <h2>Détails du cas #{selectedCase.id}</h2>
      <p>Employé: {selectedCase.employee_name}</p>
      <p>Type de faute: {selectedCase.fault_type}</p>
      <p>Description: {selectedCase.description}</p>
      <p>Status: {selectedCase.status}</p>

      <h3>Preuves:</h3>
      <ul>
        {selectedCase.evidences.map((e, i) => (
          <li key={i}>
            <a href={e.file_url} target="_blank" rel="noreferrer">{e.file_name}</a>
          </li>
        ))}
      </ul>

      <div>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={handleUpload}>Upload preuve</button>
      </div>

      <h3>Historique des events:</h3>
      <ul>
        {selectedCase.events.map((ev, i) => (
          <li key={i}>{ev.event_type} : {JSON.stringify(ev.event_data)}</li>
        ))}
      </ul>

      <button onClick={onClose}>Fermer</button>
    </div>
  );
}
