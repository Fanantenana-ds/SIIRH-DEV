import React, { useEffect, useState } from "react";
import { api } from "../api";

export default function Candidats() {
  const [candidats, setCandidats] = useState([]);

  useEffect(() => {
    api.get("/rh/candidats").then((res) => setCandidats(res.data));
  }, []);

  return (
    <div className="page">
      <h2>Liste des candidats</h2>
      <table>
        <thead>
          <tr>
            <th>Nom</th>
            <th>Email</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {candidats.map((c) => (
            <tr key={c.id}>
              <td>{c.username}</td>
              <td>{c.email}</td>
              <td>{c.score ?? "Non évalué"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
