import { useState } from "react";
import axios from "axios";

export default function TypesContrat() {
  const [type, setType] = useState("");
  const [employeeId, setEmployeeId] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://localhost:8000/contrats/", {
        type_contrat: type,
        employee_id: Number(employeeId),
        date_debut: new Date(),
      });
      alert(`Contrat créé avec succès (ID: ${res.data.id})`);
      setType("");
      setEmployeeId("");
    } catch (err) {
      console.error(err);
      alert("Erreur lors de la création du contrat.");
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6 max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-4">Créer un Type de Contrat</h1>
      <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
        <input
          type="text"
          value={type}
          onChange={(e) => setType(e.target.value)}
          placeholder="Type de contrat"
          required
          className="p-3 border rounded focus:outline-none focus:ring-2 focus:ring-green-500"
        />
        <input
          type="number"
          value={employeeId}
          onChange={(e) => setEmployeeId(e.target.value)}
          placeholder="ID Employé"
          required
          className="p-3 border rounded focus:outline-none focus:ring-2 focus:ring-green-500"
        />
        <button
          type="submit"
          className="p-3 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Envoyer
        </button>
      </form>
    </div>
  );
}
