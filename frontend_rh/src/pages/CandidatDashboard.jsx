import React, { useEffect, useState } from "react";
import axios from "axios";

export default function CandidatDashboard() {
  const [candidature, setCandidature] = useState(null);
  const [entretien, setEntretien] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCandidatData();
  }, []);

  const fetchCandidatData = async () => {
    try {
      // Exemple : récupérer les infos du candidat connecté (à ajuster selon auth)
      const candidatId = localStorage.getItem("candidat_id") || 1;

      const [candRes, entRes] = await Promise.all([
        axios.get(`http://localhost:8000/candidatures/${candidatId}`),
        axios.get(`http://localhost:8000/entretiens/${candidatId}`)
      ]);

      setCandidature(candRes.data);
      setEntretien(entRes.data);
    } catch (error) {
      console.error("Erreur lors du chargement :", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-gray-600">Chargement...</div>;
  }

  if (!candidature) {
    return <div className="p-8 text-center text-red-600">Aucune candidature trouvée.</div>;
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-center mb-6 text-blue-700">
        Espace Candidat
      </h1>

      {/* Section infos candidature */}
      <section className="bg-white p-6 shadow rounded-xl mb-6">
        <h2 className="text-xl font-semibold mb-3 text-blue-800">Votre candidature</h2>
        <div className="space-y-2">
          <p><strong>Nom :</strong> {candidature.nom}</p>
          <p><strong>Prénom :</strong> {candidature.prenom}</p>
          <p><strong>Poste demandé :</strong> {candidature.poste}</p>
          <p><strong>Statut :</strong> {candidature.statut || "En attente"}</p>
          <p><strong>Date de soumission :</strong> {candidature.date_candidature}</p>
        </div>
      </section>

      {/* Section entretien */}
      {entretien && (
        <section className="bg-white p-6 shadow rounded-xl">
          <h2 className="text-xl font-semibold mb-3 text-green-800">Votre entretien</h2>
          <div className="space-y-2">
            <p><strong>Date :</strong> {entretien.date}</p>
            <p><strong>Heure :</strong> {entretien.heure}</p>
            <p><strong>Lieu :</strong> {entretien.lieu}</p>
            <p><strong>Commentaire :</strong> {entretien.commentaire ?? "Aucun"}</p>
          </div>
        </section>
      )}

      {!entretien && (
        <section className="bg-white p-6 shadow rounded-xl">
          <h2 className="text-xl font-semibold mb-3 text-gray-700">Entretien</h2>
          <p className="text-gray-600">Aucun entretien planifié pour le moment.</p>
        </section>
      )}
    </div>
  );
}
