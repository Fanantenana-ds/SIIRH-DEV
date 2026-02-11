import React, { useEffect, useState } from "react";
import api from "../api"; 
import "./Soldes.css";

export default function Soldes() {
  const [soldes, setSoldes] = useState([]);

  const fetchSoldes = async () => {
    try {
      const res = await api.get("/api/soldes/");
      setSoldes(res.data || []);
    } catch (err) {
      console.error("Erreur fetch soldes :", err);
      setSoldes([]);
    }
  };

  useEffect(() => {
    // fetch voalohany
    fetchSoldes();

    // rehefa miverina eo amin'ny tab Soldes
    const onVisible = () => {
      if (document.visibilityState === "visible") {
        fetchSoldes();
      }
    };

    document.addEventListener("visibilitychange", onVisible);
    return () => document.removeEventListener("visibilitychange", onVisible);
  }, []);

  return (
    <div className="tab-content">
      <h3>Soldes des employés</h3>

      <div style={{ overflowX: "auto" }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Employé</th>
              <th>Congés pris</th>
              <th>Absences non payées</th>
              <th>Solde Congés</th>
            </tr>
          </thead>
          <tbody>
            {soldes.length === 0 ? (
              <tr>
                <td colSpan="4" style={{ textAlign: "center" }}>
                  Aucune donnée disponible
                </td>
              </tr>
            ) : (
              soldes.map((s) => (
                <tr key={s.employee_id}>
                  <td>{s.nom} {s.prenom}</td>
                  <td>{s.conges_pris}</td>
                  <td>{s.absences_non_payees}</td>
                  <td>{s.solde_conges}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

