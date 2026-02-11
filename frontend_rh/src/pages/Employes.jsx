import { useEffect, useState } from "react";
import axios from "axios";

export default function Employes() {
  const [employes, setEmployes] = useState([]);

  useEffect(() => {
    const fetchEmployes = async () => {
      try {
       const res = await axios.get("http://localhost:8000/api/employes");
        console.log(res.data); 
        setEmployes(res.data);
      } catch (error) {
        console.error("Erreur lors du chargement des employés :", error);
      }
    };
    fetchEmployes();
  }, []);
  console.log(employes);
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Liste des Employés</h1>

      <table className="w-full bg-white shadow rounded-lg">
        <thead>
          <tr className="bg-gray-100 text-left text-gray-700">
            <th className="p-3">Nom complet</th>
            <th className="p-3">Poste</th>
            <th className="p-3">Email</th>
            <th className="p-3">Téléphone</th>
          </tr>
        </thead>

        <tbody>
          {employes.length > 0 ? (
            employes.map((emp) => (
              <tr key={emp.id} className="border-t hover:bg-gray-50">
                <td className="p-3">{emp.nom} {emp.prenom}</td>
                <td className="p-3">{emp.poste}</td>
                <td className="p-3">{emp.email}</td>
                <td className="p-3">{emp.phone}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="4" className="p-3 text-center text-gray-500">
                Aucun employé trouvé.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
