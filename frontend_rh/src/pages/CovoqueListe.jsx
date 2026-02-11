import React, { useEffect, useState } from "react";

export default function CovoqueListe() {
  const [convoques, setConvoques] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetchConvoques();
  }, []);

  const fetchConvoques = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/rh/candidatures");
      if (!res.ok) throw new Error("Erreur chargement convoqués");
      const data = await res.json();
   
      setConvoques(data.filter(c => c.statut === "Convoqué"));
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value.toLowerCase());
  };

  const filteredConvoques = convoques.filter(
    c =>
      c.nom?.toLowerCase().includes(searchTerm) ||
      c.prenom?.toLowerCase().includes(searchTerm) ||
      c.poste?.toLowerCase().includes(searchTerm)
  );

  return (
    <div className="dashboard-wrapper">
      <h2 className="text-xl font-bold mb-4">Liste des candidats convoqués</h2>

      <input
        type="text"
        placeholder="Rechercher un candidat ou un poste..."
        onChange={handleSearch}
        value={searchTerm}
        style={{
          padding: "5px 8px",
          borderRadius: "6px",
          border: "1px solid #ccc",
          marginBottom: "10px",
          width: "250px",
        }}
      />

      {loading ? (
        <p>Chargement...</p>
      ) : (
        <table className="entretien-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nom</th>
              <th>Prénom</th>
              <th>Poste</th>
              <th>Date / Heure Convocation</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {filteredConvoques.map(c => (
              <tr key={c.id}>
                <td>{c.id}</td>
                <td>{c.nom}</td>
                <td>{c.prenom}</td>
                <td>{c.poste}</td>
                <td>{c.date_convocation} {c.heure_convocation}</td>
                <td>{c.score_total || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
