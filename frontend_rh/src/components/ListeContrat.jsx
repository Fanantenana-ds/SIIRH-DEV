import { useEffect, useState } from "react";
import axios from "axios";

export default function ListeContrat() {
  const [contrats, setContrats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchContrats = async () => {
      try {
        const res = await axios.get("http://localhost:8000/contrats/");
        setContrats(res.data);
      } catch (error) {
        console.error("Erreur lors du chargement des contrats :", error);
      } finally {
        setLoading(false);
      }
    };
    fetchContrats();
  }, []);

  if (loading) return <p>Chargement des contrats...</p>;
  if (!contrats.length) return <p className="text-gray-500">Aucun contrat trouvé.</p>;

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-4">Liste des Contrats</h1>
      <table className="w-full text-left border-t border-gray-200">
        <thead className="bg-gray-100 text-gray-700">
          <tr>
            <th className="p-3">Employé</th>
            <th className="p-3">Type</th>
            <th className="p-3">Date Début</th>
            <th className="p-3">Date Fin</th>
          </tr>
        </thead>
        <tbody>
          {contrats.map((c) => (
            <tr key={c.id} className="border-t hover:bg-gray-50">
              <td className="p-3">{c.employee?.nom || "Inconnu"}</td>
              <td className="p-3">{c.type_contrat}</td>
              <td className="p-3">{c.date_debut}</td>
              <td className="p-3">{c.date_fin || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
