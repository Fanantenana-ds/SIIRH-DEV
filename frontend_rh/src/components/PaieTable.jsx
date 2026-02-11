// PaieTable.jsx
import React from "react";
import { deletePaie } from "../api/paieApi";

export default function PaieTable({ paies, onDeleted }) {
  const handleDelete = async (id) => {
    if (!window.confirm("Voulez-vous vraiment supprimer cette paie ?")) return;
    try {
      await deletePaie(id);
      onDeleted(); // recharge la liste après suppression
    } catch (err) {
      console.error(err);
      alert("Erreur lors de la suppression.");
    }
  };

  return (
    <table className="paie-table">
      <thead>
        <tr>
          <th>Employé</th>
          <th>Mois</th>
          <th>Année</th>
          <th>Primes</th>
          <th>Heures supp.</th>
          <th>Déductions</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {paies.length === 0 ? (
          <tr>
            <td colSpan="7">Aucune paie trouvée.</td>
          </tr>
        ) : (
          paies.map((paie) => (
            <tr key={paie.id}>
              <td>{paie.employee?.fullname}</td>
              <td>{paie.mois}</td>
              <td>{paie.annee}</td>
              <td>{paie.primes}</td>
              <td>{paie.heures_supp}</td>
              <td>{paie.deductions}</td>
              <td>
                <button
                  className="paie-delete-btn"
                  onClick={() => handleDelete(paie.id)}
                >
                  Supprimer
                </button>
              </td>
            </tr>
          ))
        )}
      </tbody>
    </table>
  );
}
