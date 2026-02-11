// import React, { useEffect, useState } from "react";
// import api from "../api";


// export default function Conges({ employees }) {
// const [conges, setConges] = useState([]);
// const [form, setForm] = useState({ employee_id: "", date_debut: "", date_fin: "", type_conge: "annuel", statut: "en attente", motif: "" });
// const [editingId, setEditingId] = useState(null);
// const [showForm, setShowForm] = useState(false);


// const fetchConges = async () => { try { const res = await api.get(`/conges/`); setConges(res.data || []); } catch (err) { console.error(err); } };
// useEffect(() => { fetchConges(); }, []);


// const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
// const handleSubmit = async (e) => {
// e.preventDefault();
// try {
// if (editingId) await api.put(`/conges/${editingId}`, form);
// else await api.post(`/conges/`, form);
// setForm({ employee_id: "", date_debut: "", date_fin: "", type_conge: "annuel", statut: "en attente", motif: "" });
// setEditingId(null);
// setShowForm(false);
// fetchConges();
// } catch (err) { console.error("Erreur congé :", err); }
// };


// const handleEdit = (c) => { setForm({ employee_id: c.employee_id, date_debut: c.date_debut, date_fin: c.date_fin, type_conge: c.type_conge, statut: c.statut, motif: c.motif || "" }); setEditingId(c.id); setShowForm(true); };
// const handleDelete = async (id) => { if (!window.confirm("Confirmer la suppression ?")) return; await api.delete(`/conges/${id}`); fetchConges(); };


// const getEmployeeLabel = (id) => { const emp = employees.find(e => e.id === id); return emp ? `${emp.nom} ${emp.prenom}` : "—"; };


// return (
// <div className="tab-content">
// <button onClick={() => setShowForm(!showForm)}>{showForm ? "Masquer Formulaire" : "Créer un congé"}</button>
// {showForm && (
// <form onSubmit={handleSubmit} className="mini-form">
// <label>Employé<input type="text" list="employees-list" value={form.employee_id} name="employee_id" onChange={handleChange} required /></label>
// <label>Date début <input type="date" name="date_debut" value={form.date_debut} onChange={handleChange} required /></label>
// <label>Date fin <input type="date" name="date_fin" value={form.date_fin} onChange={handleChange} required /></label>
// <label>Type<select name="type_conge" value={form.type_conge} onChange={handleChange}><option value="annuel">Annuel</option><option value="maladie">Maladie</option><option value="exceptionnel">Exceptionnel</option></select></label>
// <label>Statut<select name="statut" value={form.statut} onChange={handleChange}><option value="en attente">En attente</option><option value="validée">Validée</option><option value="refusée">Refusée</option></select></label>
// <label>Motif <input type="text" name="motif" value={form.motif} onChange={handleChange} /></label>
// <button type="submit">{editingId ? "Modifier" : "Ajouter"}</button>
// </form>
// )}


// <table className="data-table">
// <thead><tr><th>Employé</th><th>Début</th><th>Fin</th><th>Type</th><th>Statut</th><th>Motif</th><th>Actions</th></tr></thead>
// <tbody>
// {conges.map(c => (
// <tr key={c.id}>
// <td>{getEmployeeLabel(c.employee_id)}</td>
// <td>{c.date_debut}</td>
// <td>{c.date_fin}</td>
// <td>{c.type_conge}</td>
// <td>{c.statut}</td>
// <td>{c.motif || "—"}</td>
// <td>
// <button onClick={() => handleEdit(c)}>✏️</button>
// <button onClick={() => handleDelete(c.id)}>🗑️</button>
// </td>
// </tr>
// ))}
// </tbody>
// </table>
// </div>
// );
// }





















import React, { useEffect, useState } from "react";
import api from "../api";

export default function Conges({ employees }) {
  const [conges, setConges] = useState([]);
  const [form, setForm] = useState({
    employee_id: "",
    date_debut: "",
    date_fin: "",
    type_conge: "annuel",
    motif: ""
  });
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);

  // 🔹 Récupérer tous les congés
  const fetchConges = async () => {
    try {
      const res = await api.get("/conges/");
      setConges(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchConges();
  }, []);

  // 🔹 Changement dans le formulaire
  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  // 🔹 Soumission formulaire
  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      employee_id: parseInt(form.employee_id),
      type_conge: form.type_conge, // mapping type_conge → type
      date_debut: form.date_debut,
      date_fin: form.date_fin,
      motif: form.motif || ""
    };

    try {
      if (editingId) {
        await api.put(`/conges/${editingId}`, payload);
      } else {
        await api.post("/conges/", payload);
      }

      setForm({
        employee_id: "",
        date_debut: "",
        date_fin: "",
        type_conge: "annuel",
        motif: ""
      });
      setEditingId(null);
      setShowForm(false);
      fetchConges();
    } catch (err) {
      console.error("Erreur congé :", err.response?.data || err);
    }
  };

  // 🔹 Edition
  const handleEdit = (c) => {
    setForm({
      employee_id: c.employee_id.toString(),
      date_debut: c.date_debut,
      date_fin: c.date_fin,
      type_conge: c.type_conge,
      motif: c.motif || ""
    });
    setEditingId(c.id);
    setShowForm(true);
  };

  // 🔹 Suppression
  const handleDelete = async (id) => {
    if (!window.confirm("Confirmer la suppression ?")) return;
    await api.delete(`/conges/${id}`);
    fetchConges();
  };

  // 🔹 Label employé
  const getEmployeeLabel = (id) => {
    const emp = employees.find((e) => e.id === id);
    return emp ? `${emp.nom} ${emp.prenom}` : "—";
  };

  return (
    <div className="tab-content">
      <button onClick={() => setShowForm(!showForm)}>
        {showForm ? "Masquer Formulaire" : "Créer un congé"}
      </button>

      {showForm && (
        <form onSubmit={handleSubmit} className="mini-form">
          <label>
            Employé
            <select
              name="employee_id"
              value={form.employee_id}
              onChange={handleChange}
              required
            >
              <option value="">-- Sélectionner --</option>
              {employees.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.nom} {e.prenom}
                </option>
              ))}
            </select>
          </label>

          <label>
            Date début
            <input
              type="date"
              name="date_debut"
              value={form.date_debut}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            Date fin
            <input
              type="date"
              name="date_fin"
              value={form.date_fin}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            Type
            <select
              name="type_conge"
              value={form.type_conge}
              onChange={handleChange}
            >
              <option value="annuel">Annuel</option>
              <option value="maladie">Maladie</option>
              <option value="exceptionnel">Exceptionnel</option>
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

          <button type="submit">{editingId ? "Modifier" : "Ajouter"}</button>
        </form>
      )}

      <table className="data-table">
        <thead>
          <tr>
            <th>Employé</th>
            <th>Début</th>
            <th>Fin</th>
            <th>Type</th>
            <th>Motif</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {conges.map((c) => (
            <tr key={c.id}>
              <td>{getEmployeeLabel(c.employee_id)}</td>
              <td>{c.date_debut}</td>
              <td>{c.date_fin}</td>
              <td>{c.type_conge}</td>
              <td>{c.motif || "—"}</td>
              <td>
                <button onClick={() => handleEdit(c)}>✏️</button>
                <button onClick={() => handleDelete(c.id)}>🗑️</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
