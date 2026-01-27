import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/Absences.css";

export default function Absences() {
  const API_BASE = "http://127.0.0.1:8000/api";

  const [employees, setEmployees] = useState([]);
  const [absences, setAbsences] = useState([]);

  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);

  const [form, setForm] = useState({
    employee_id: "",
    date_debut: "",
    date_fin: "",
    type_absence: "maladie",
    statut: "en attente",
    motif: "",
  });

  // -----------------------------
  // Load employees + absences
  const fetchEmployees = async () => {
    try {
      const res = await axios.get(`${API_BASE}/employes/`);
      setEmployees(res.data);
    } catch (err) {
      console.error("Erreur employés :", err);
    }
  };

  const fetchAbsences = async () => {
    try {
      const res = await axios.get(`${API_BASE}/absences/`);
      setAbsences(res.data);
    } catch (err) {
      console.error("Erreur absences :", err);
    }
  };

  useEffect(() => {
    fetchEmployees();
    fetchAbsences();
  }, []);

  // -----------------------------
  // Handlers
  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      if (editingId) {
        await axios.put(`${API_BASE}/absences/${editingId}`, form);
      } else {
        await axios.post(`${API_BASE}/absences/`, form);
      }

      setForm({
        employee_id: "",
        date_debut: "",
        date_fin: "",
        type_absence: "maladie",
        statut: "en attente",
        motif: "",
      });

      setEditingId(null);
      setShowForm(false);
      fetchAbsences();
    } catch (err) {
      console.error("Erreur sauvegarde :", err);
    }
  };

  const handleEdit = (a) => {
    setForm({
      employee_id: a.employee_id,
      date_debut: a.date_debut,
      date_fin: a.date_fin,
      type_absence: a.type_absence,
      statut: a.statut,
      motif: a.motif || "",
    });
    setEditingId(a.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Confirmer la suppression ?")) return;

    try {
      await axios.delete(`${API_BASE}/absences/${id}`);
      fetchAbsences();
    } catch (err) {
      console.error("Erreur suppression :", err);
    }
  };

  // -----------------------------
  return (
    <div className="absences-module">
      <h2>Gestion des Absences</h2>

      <button onClick={() => setShowForm(!showForm)}>
        {showForm ? "Masquer le formulaire" : "Créer une absence"}
      </button>

      {showForm && (
        <form className="absence-form" onSubmit={handleSubmit}>
          <label>
            Employé
            <input
              type="text"
              list="employees-list"
              name="employee_id"
              value={form.employee_id}
              onChange={handleChange}
            />
            <datalist id="employees-list">
              {employees.map((emp) => (
                <option key={emp.id} value={emp.id}>
                  {emp.nom} {emp.prenom}
                </option>
              ))}
            </datalist>
          </label>

          <label>
            Date début
            <input
              type="date"
              name="date_debut"
              value={form.date_debut}
              onChange={handleChange}
            />
          </label>

          <label>
            Date fin
            <input
              type="date"
              name="date_fin"
              value={form.date_fin}
              onChange={handleChange}
            />
          </label>

          <label>
            Type
            <select
              name="type_absence"
              value={form.type_absence}
              onChange={handleChange}
            >
              <option value="maladie">Maladie</option>
              <option value="conge">Congé</option>
              <option value="non_justifiee">Non justifiée</option>
            </select>
          </label>

          <label>
            Statut
            <select
              name="statut"
              value={form.statut}
              onChange={handleChange}
            >
              <option value="en attente">En attente</option>
              <option value="validée">Validée</option>
              <option value="refusée">Refusée</option>
            </select>
          </label>

          <label>
            Motif
            <input
              type="text"
              name="motif"
              value={form.motif}
              onChange={handleChange}
            />
          </label>

          <button type="submit">
            {editingId ? "Modifier" : "Ajouter"}
          </button>
        </form>
      )}

      <table className="absences-table">
        <thead>
          <tr>
            <th>Employé</th>
            <th>Date début</th>
            <th>Date fin</th>
            <th>Type</th>
            <th>Statut</th>
            <th>Motif</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          {absences.map((a) => {
            const emp = employees.find((e) => e.id === a.employee_id);

            return (
              <tr key={a.id}>
                <td>{emp ? `${emp.nom} ${emp.prenom}` : "—"}</td>
                <td>{a.date_debut}</td>
                <td>{a.date_fin}</td>
                <td>{a.type_absence}</td>
                <td>{a.statut}</td>
                <td>{a.motif || "—"}</td>
                <td>
                  <button onClick={() => handleEdit(a)}>✏️</button>
                  <button onClick={() => handleDelete(a.id)}>🗑️</button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
