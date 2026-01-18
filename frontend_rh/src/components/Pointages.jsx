// import React, { useEffect, useState } from "react";
// import api from "../api";


// export default function Pointages({ employees }) {
// const [pointages, setPointages] = useState([]);
// const [form, setForm] = useState({ employee_id: "", date: "", heure_entree: "", heure_sortie: "" });
// const [editingId, setEditingId] = useState(null);
// const [showForm, setShowForm] = useState(false);


// const fetchPointages = async () => {
// try { const res = await api.get(`/pointages/`); setPointages(res.data || []); } catch (err) { console.error(err); }
// };


// useEffect(() => { fetchPointages(); }, []);


// const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
// const handleSubmit = async (e) => {
// e.preventDefault();
// try {
// if (editingId) await api.put(`/pointages/${editingId}`, form);
// else await api.post(`/pointages/`, form);
// setForm({ employee_id: "", date: "", heure_entree: "", heure_sortie: "" });
// setEditingId(null);
// setShowForm(false);
// fetchPointages();
// } catch (err) { console.error("Erreur pointage :", err); }
// };


// const handleEdit = (p) => { setForm({ employee_id: p.employee_id, date: p.date, heure_entree: p.heure_entree, heure_sortie: p.heure_sortie }); setEditingId(p.id); setShowForm(true); };
// const handleDelete = async (id) => { if (!window.confirm("Confirmer la suppression ?")) return; await api.delete(`/pointages/${id}`); fetchPointages(); };


// const getEmployeeLabel = (id) => { const emp = employees.find(e => e.id === id); return emp ? `${emp.nom} ${emp.prenom}` : "—"; };


// return (
// <div className="tab-content">
// <button onClick={() => setShowForm(!showForm)}>{showForm ? "Masquer Formulaire" : "Créer un pointage"}</button>
// {showForm && (
// <form onSubmit={handleSubmit} className="mini-form">
// <label>Employé<input type="text" list="employees-list" name="employee_id" value={form.employee_id} onChange={handleChange} required /></label>
// <label>Date <input type="date" name="date" value={form.date} onChange={handleChange} required /></label>
// <label>Heure entrée <input type="time" name="heure_entree" value={form.heure_entree} onChange={handleChange} /></label>
// <label>Heure sortie <input type="time" name="heure_sortie" value={form.heure_sortie} onChange={handleChange} /></label>
// <button type="submit">{editingId ? "Modifier" : "Ajouter"}</button>
// </form>
// )}


// <table className="data-table">
// <thead><tr><th>Employé</th><th>Date</th><th>Heure Entrée</th><th>Heure Sortie</th><th>Actions</th></tr></thead>
// <tbody>
// {pointages.map(p => (
// <tr key={p.id}>
// <td>{getEmployeeLabel(p.employee_id)}</td>
// <td>{p.date}</td>
// <td>{p.heure_entree}</td>
// <td>{p.heure_sortie}</td>
// <td>
// <button onClick={() => handleEdit(p)}>✏️</button>
// <button onClick={() => handleDelete(p.id)}>🗑️</button>
// </td>
// </tr>
// ))}
// </tbody>
// </table>
// </div>
// );
// }









// console.log("POINTAGES VERSION PRO CHARGÉE");

// import React, { useEffect, useState } from "react";
// import api from "../api";

// export default function Pointages({ employees }) {
//   const [resume, setResume] = useState([]);
//   const [pointages, setPointages] = useState([]);
//   const [openEmp, setOpenEmp] = useState(null);

//   const [form, setForm] = useState({
//     employee_id: "",
//     date: "",
//     heure_entree: "",
//     heure_sortie: ""
//   });
//   const [editingId, setEditingId] = useState(null);
//   const [showForm, setShowForm] = useState(false);

//   const mois = new Date().getMonth() + 1;
//   const annee = new Date().getFullYear();

//   const fetchResume = async () => {
//     const res = await api.get(`/pointages/resume?mois=${mois}&annee=${annee}`);
//     setResume(res.data || []);
//   };

//   const fetchPointages = async () => {
//     const res = await api.get(`/pointages/`);
//     setPointages(res.data || []);
//   };

//   useEffect(() => {
//     fetchResume();
//     fetchPointages();
//   }, []);

//   const handleChange = (e) =>
//     setForm({ ...form, [e.target.name]: e.target.value });

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     if (editingId)
//       await api.put(`/pointages/${editingId}`, form);
//     else
//       await api.post(`/pointages/`, form);

//     setForm({ employee_id: "", date: "", heure_entree: "", heure_sortie: "" });
//     setEditingId(null);
//     setShowForm(false);
//     fetchResume();
//     fetchPointages();
//   };

//   const handleEdit = (p) => {
//     setForm(p);
//     setEditingId(p.id);
//     setShowForm(true);
//   };

//   const handleDelete = async (id) => {
//     if (!window.confirm("Confirmer la suppression ?")) return;
//     await api.delete(`/pointages/${id}`);
//     fetchResume();
//     fetchPointages();
//   };

//   return (
//     <div className="tab-content">

//       <button onClick={() => setShowForm(!showForm)}>
//         {showForm ? "Masquer Formulaire" : "Créer un pointage"}
//       </button>

//       {showForm && (
//         <form onSubmit={handleSubmit} className="mini-form">
//           <input list="employees-list" name="employee_id" value={form.employee_id} onChange={handleChange} required />
//           <input type="date" name="date" value={form.date} onChange={handleChange} required />
//           <input type="time" name="heure_entree" value={form.heure_entree} onChange={handleChange} />
//           <input type="time" name="heure_sortie" value={form.heure_sortie} onChange={handleChange} />
//           <button type="submit">{editingId ? "Modifier" : "Ajouter"}</button>
//         </form>
//       )}

//       <table className="data-table">
//         <thead>
//           <tr>
//             <th>Employé</th>
//             <th>Présence</th>
//             <th>Absences</th>
//             <th>Détails</th>
//           </tr>
//         </thead>
//         <tbody>
//           {resume.map(emp => (
//             <React.Fragment key={emp.employee_id}>
//               <tr>
//                 <td>{emp.nom} {emp.prenom}</td>
//                 <td>{emp.jours_travailles} / {emp.jours_theoriques}</td>
//                 <td>{emp.absences}</td>
//                 <td>
//                   <button onClick={() =>
//                     setOpenEmp(openEmp === emp.employee_id ? null : emp.employee_id)
//                   }>⋯</button>
//                 </td>
//               </tr>

//               {openEmp === emp.employee_id && (
//                 <tr>
//                   <td colSpan="4">
//                     <table className="sub-table">
//                       <thead>
//                         <tr>
//                           <th>Date</th>
//                           <th>Entrée</th>
//                           <th>Sortie</th>
//                           <th>Actions</th>
//                         </tr>
//                       </thead>
//                       <tbody>
//                         {pointages
//                           .filter(p => p.employee_id === emp.employee_id)
//                           .map(p => (
//                             <tr key={p.id}>
//                               <td>{p.date}</td>
//                               <td>{p.heure_entree}</td>
//                               <td>{p.heure_sortie}</td>
//                               <td>
//                                 <button onClick={() => handleEdit(p)}>✏️</button>
//                                 <button onClick={() => handleDelete(p.id)}>🗑️</button>
//                               </td>
//                             </tr>
//                           ))}
//                       </tbody>
//                     </table>
//                   </td>
//                 </tr>
//               )}
//             </React.Fragment>
//           ))}
//         </tbody>
//       </table>
//     </div>
//   );
// }

















import React, { useEffect, useState } from "react";
import api from "../api";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from "chart.js";
import "./Pointages.css";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function Pointages({ employees }) {
  const [pointages, setPointages] = useState([]);
  const [resume, setResume] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState({
    employee_id: "",
    date: "",
    heure_entree: "",
    heure_sortie: "",
    mode: "manual"
  });

  const [selectedEmp, setSelectedEmp] = useState(null);
  const [filterMonth, setFilterMonth] = useState(new Date().getMonth() + 1);
  const [searchEmp, setSearchEmp] = useState("");

  const moisCourant = new Date().getMonth() + 1;
  const anneeCourant = new Date().getFullYear();

  // ======================
  // FETCH POINTAGES
  // ======================
  const fetchPointages = async () => {
    try {
      const res = await api.get(`/pointages/`);
      setPointages(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchResume = async (mois = moisCourant) => {
    try {
      const res = await api.get(`/pointages/resume?mois=${mois}&annee=${anneeCourant}`);
      setResume(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchPointages();
    fetchResume(filterMonth);
  }, [filterMonth]);

  // ======================
  // FORM HANDLERS
  // ======================
  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId)
        await api.put(`/pointages/${editingId}`, {
          ...form,
          employee_id: Number(form.employee_id)
        });
      else
        await api.post(`/pointages/`, {
          ...form,
          employee_id: Number(form.employee_id)
        });

      setForm({ employee_id: "", date: "", heure_entree: "", heure_sortie: "", mode: "manual" });
      setEditingId(null);
      setShowForm(false);
      fetchPointages();
      fetchResume(filterMonth);
    } catch (err) {
      console.error("Erreur pointage :", err);
    }
  };

  const handleEdit = (p) => {
    setForm({
      employee_id: p.employee_id,
      date: p.date,
      heure_entree: p.heure_entree,
      heure_sortie: p.heure_sortie,
      mode: p.mode || "manual"
    });
    setEditingId(p.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Confirmer la suppression ?")) return;
    await api.delete(`/pointages/${id}`);
    fetchPointages();
    fetchResume(filterMonth);
    if (selectedEmp)
      setSelectedEmp(prev => ({
        ...prev,
        pointages: prev.pointages.filter(p => p.id !== id)
      }));
  };

  const getEmployeeLabel = (id) => {
    const emp = employees.find(e => e.id === id);
    return emp ? `${emp.nom} ${emp.prenom}` : "—";
  };

  // ======================
  // FILTER + SEARCH
  // ======================
  const filteredResume = resume.filter(emp =>
    emp.nom.toLowerCase().includes(searchEmp.toLowerCase()) ||
    emp.prenom.toLowerCase().includes(searchEmp.toLowerCase())
  );

  // ======================
  // CHART DATA
  // ======================
  const chartData = {
    labels: filteredResume.map(emp => `${emp.nom} ${emp.prenom}`),
    datasets: [
      {
        label: "Jours travaillés",
        data: filteredResume.map(emp => emp.jours_travailles),
        backgroundColor: "rgba(54, 162, 235, 0.7)"
      },
      {
        label: "Absences",
        data: filteredResume.map(emp => emp.absences),
        backgroundColor: "rgba(255, 99, 132, 0.7)"
      }
    ]
  };
  const chartOptions = { responsive: true, plugins: { legend: { position: "top" } } };

  return (
    <div className="tab-content">

      {/* Filtre et recherche */}
      <div className="top-bar">
        <select value={filterMonth} onChange={(e) => setFilterMonth(Number(e.target.value))}>
          {[
            "Janvier","Février","Mars","Avril","Mai","Juin",
            "Juillet","Août","Septembre","Octobre","Novembre","Décembre"
          ].map((m,i)=><option key={i} value={i+1}>{m}</option>)}
        </select>

        <input
          type="text"
          placeholder="Recherche employé..."
          value={searchEmp}
          onChange={(e)=>setSearchEmp(e.target.value)}
        />
      </div>

      {/* Formulaire */}
      <button onClick={() => setShowForm(!showForm)}>
        {showForm ? "Masquer Formulaire" : "Créer un pointage"}
      </button>

      {showForm && (
        <form onSubmit={handleSubmit} className="mini-form">
          <input type="number" name="employee_id" placeholder="ID Employé" value={form.employee_id} onChange={handleChange} required/>
          <input type="date" name="date" value={form.date} onChange={handleChange} required/>
          <input type="time" name="heure_entree" value={form.heure_entree} onChange={handleChange}/>
          <input type="time" name="heure_sortie" value={form.heure_sortie} onChange={handleChange}/>
          <button type="submit">{editingId ? "Modifier" : "Ajouter"}</button>
        </form>
      )}

      {/* Table résumé */}
      <table className="data-table">
        <thead><tr><th>Employé</th><th>Présence</th><th>Absences</th><th>Détails</th></tr></thead>
        <tbody>
          {filteredResume.map(emp => (
            <tr key={emp.employee_id}>
              <td>{emp.nom} {emp.prenom}</td>
              <td>{emp.jours_travailles} / {emp.jours_theoriques}</td>
              <td>{emp.absences}</td>
              <td><button onClick={() => setSelectedEmp(emp)}>⋯</button></td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Graphique */}
      <div className="chart-container">
        <Bar data={chartData} options={chartOptions}/>
      </div>

      {/* Modal détails */}
      {selectedEmp && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>{selectedEmp.nom} {selectedEmp.prenom}</h3>
            <p>Présence : <b>{selectedEmp.jours_travailles}</b> / {selectedEmp.jours_theoriques}</p>

            <table className="sub-table">
              <thead><tr><th>Date</th><th>Entrée</th><th>Sortie</th><th>Actions</th></tr></thead>
              <tbody>
                {selectedEmp.pointages.length === 0 ? (
                  <tr><td colSpan="4">Aucun pointage</td></tr>
                ) : selectedEmp.pointages.map(p=>(
                  <tr key={p.id}>
                    <td>{p.date}</td>
                    <td>{p.heure_entree || "—"}</td>
                    <td>{p.heure_sortie || "—"}</td>
                    <td>
                      <button onClick={()=>handleEdit(p)}>✏️</button>
                      <button onClick={()=>handleDelete(p.id)}>🗑️</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <button className="close-btn" onClick={()=>setSelectedEmp(null)}>Fermer</button>
          </div>
        </div>
      )}

    </div>
  );
}
