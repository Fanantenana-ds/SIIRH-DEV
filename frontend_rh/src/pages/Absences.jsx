import React, { useEffect, useState } from "react";
import axios from "axios";
import "../styles/TempsAbsences.css";


export default function TempsAbsences({ navigateToDashboard }) {
  const API_BASE = "http://127.0.0.1:8000/api";
  
  const [tab, setTab] = useState("absences");
  const [employees, setEmployees] = useState([]);
  const [searchEmployee, setSearchEmployee] = useState("");

  // -----------------------------
  // Absences
  const [absences, setAbsences] = useState([]);
  const [absenceForm, setAbsenceForm] = useState({
    employee_id: "",
    date_debut: "",
    date_fin: "",
    type_absence: "maladie",
    statut: "en attente",
    motif: "",
  });
  const [editingAbsenceId, setEditingAbsenceId] = useState(null);
  const [showAbsenceForm, setShowAbsenceForm] = useState(false);

  // Pointages
  const [pointages, setPointages] = useState([]);
  const [pointageForm, setPointageForm] = useState({
    employee_id: "",
    date: "",
    heure_entree: "",
    heure_sortie: "",
  });
  const [editingPointageId, setEditingPointageId] = useState(null);
  const [showPointageForm, setShowPointageForm] = useState(false);

  // Congés
  const [conges, setConges] = useState([]);
  const [congeForm, setCongeForm] = useState({
    employee_id: "",
    date_debut: "",
    date_fin: "",
    type_conge: "annuel",
    statut: "en attente",
    motif: "",
  });
  const [editingCongeId, setEditingCongeId] = useState(null);
  const [showCongeForm, setShowCongeForm] = useState(false);

  // Soldes
  const [soldes, setSoldes] = useState([]);
  const calculateDays = (start, end) => { const sd = new Date(start); const ed = new Date(end); return Math.ceil((ed - sd)/(1000*60*60*24)) + 1; };


  // Export
  const [exportData, setExportData] = useState([]);

  // -----------------------------
  // Popup pour détails
  const [popupData, setPopupData] = useState(null);

  // -----------------------------
  // Fetch Employees
  const fetchEmployees = async () => {
    try {
      const res = await axios.get(`${API_BASE}/employes/`);
      setEmployees(res.data);
    } catch (err) {
      console.error("Erreur récupération employés :", err);
    }
  };

  // Fetch data selon tab
  const fetchData = async () => {
    fetchEmployees();

    try {
      if (tab === "absences") {
        const res = await axios.get(`${API_BASE}/absences/`);
        setAbsences(res.data);
      } else if (tab === "pointages") {
        const res = await axios.get(`${API_BASE}/pointages/`);
        setPointages(res.data);
      } else if (tab === "conges") {
        const res = await axios.get(`${API_BASE}/conges/`);
        setConges(res.data);
      } else if (tab === "soldes") {
        const res = await axios.get(`${API_BASE}/soldes/`);
        setSoldes(res.data);
      } else if (tab === "export") {
        const res = await axios.get(`${API_BASE}/export_paie/`);
        setExportData(res.data);
      }
    } catch (err) {
      console.error("Erreur récupération données :", err);
    }
  };

  useEffect(() => {
    fetchData();
  }, [tab]);

  const handleTabChange = (newTab) => {
    setTab(newTab);
  };
  const filterByEmployee = list => !searchEmployee ? list : list.filter(item => { const emp = employees.find(e => e.id === item.employee_id); if (!emp) return false; const fullName = `${emp.nom} ${emp.prenom}`.toLowerCase(); return fullName.includes(searchEmployee.toLowerCase()); });


  // -----------------------------
  // Handlers Absences
  const handleAbsenceChange = e => setAbsenceForm({ ...absenceForm, [e.target.name]: e.target.value });
  const handleAbsenceSubmit = async (e) => { e.preventDefault(); try { if(editingAbsenceId) await axios.put(`${API_BASE}/absences/${editingAbsenceId}`,absenceForm); else await axios.post(`${API_BASE}/absences/`,absenceForm); if(absenceForm.statut==="validée") setSoldes(prev=>prev.map(s=>s.employee_id===absenceForm.employee_id?{...s,absences_non_payees:s.absences_non_payees+calculateDays(absenceForm.date_debut,absenceForm.date_fin)}:s)); setAbsenceForm({employee_id:"",date_debut:"",date_fin:"",type_absence:"maladie",statut:"en attente",motif:""}); setEditingAbsenceId(null); setShowAbsenceForm(false); fetchData(); } catch(err){console.error("Erreur sauvegarde :",err);} };

  const handleAbsenceEdit = (a) => {
    setAbsenceForm({ employee_id: a.employee_id, date_debut: a.date_debut, date_fin: a.date_fin, type_absence: a.type_absence, statut: a.statut, motif: a.motif || "" });
    setEditingAbsenceId(a.id);
    setShowAbsenceForm(true);
  };
  const handleAbsenceDelete = async (id) => {
    if (!window.confirm("Confirmer la suppression ?")) return;
    await axios.delete(`${API_BASE}/absences/${id}`);
    fetchData();
  };

  // -----------------------------
  // Handlers Pointages
  const handlePointageChange = (e) => setPointageForm({ ...pointageForm, [e.target.name]: e.target.value });
  const handlePointageSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingPointageId) await axios.put(`${API_BASE}/pointages/${editingPointageId}`, pointageForm);
      else await axios.post(`${API_BASE}/pointages/`, pointageForm);

      setPointageForm({ employee_id: "", date: "", heure_entree: "", heure_sortie: "" });
      setEditingPointageId(null);
      setShowPointageForm(false);
      fetchData();
    } catch (err) { console.error("Erreur pointage :", err); }
  };
  const handlePointageEdit = (p) => { setPointageForm({ employee_id: p.employee_id, date: p.date, heure_entree: p.heure_entree, heure_sortie: p.heure_sortie }); setEditingPointageId(p.id); setShowPointageForm(true); };
  const handlePointageDelete = async (id) => { if (!window.confirm("Confirmer la suppression ?")) return; await axios.delete(`${API_BASE}/pointages/${id}`); fetchData(); };

  // -----------------------------
  // Handlers Congés
  const handleCongeChange = (e) => setCongeForm({ ...congeForm, [e.target.name]: e.target.value });
  const handleCongeSubmit = async (e) => { e.preventDefault(); try { if(editingCongeId) await axios.put(`${API_BASE}/conges/${editingCongeId}`,congeForm); else await axios.post(`${API_BASE}/conges/`,congeForm); if(congeForm.statut==="validée") setSoldes(prev=>prev.map(s=>s.employee_id===congeForm.employee_id?{...s,conges_pris:s.conges_pris+calculateDays(congeForm.date_debut,congeForm.date_fin)}:s)); setCongeForm({employee_id:"",date_debut:"",date_fin:"",type_conge:"annuel",statut:"en attente",motif:""}); setEditingCongeId(null); setShowCongeForm(false); fetchData(); } catch(err){console.error("Erreur congé :",err);} };

  const handleCongeEdit = (c) => { setCongeForm({ employee_id: c.employee_id, date_debut: c.date_debut, date_fin: c.date_fin, type_conge: c.type_conge, statut: c.statut, motif: c.motif || "" }); setEditingCongeId(c.id); setShowCongeForm(true); };
  const handleCongeDelete = async (id) => { if (!window.confirm("Confirmer la suppression ?")) return; await axios.delete(`${API_BASE}/conges/${id}`); fetchData(); };

  // -----------------------------
  // Soldes
  const buildPayrollExport = (mois, annee) => employees.map(emp => { const empPointages = pointages.filter(p => p.employee_id === emp.id && new Date(p.date).getMonth() + 1 === mois && new Date(p.date).getFullYear() === annee); let heuresNormales = 0, heuresSup = 0; empPointages.forEach(p => { const diff = (new Date(`1970-01-01T${p.heure_sortie}`) - new Date(`1970-01-01T${p.heure_entree}`)) / 36e5; diff > 8 ? (heuresNormales += 8, heuresSup += diff - 8) : heuresNormales += diff; }); const absencesJours = absences.filter(a => a.employee_id === emp.id && a.statut === "validée").reduce((s,a)=>s+calculateDays(a.date_debut,a.date_fin),0); const congesNonPayes = conges.filter(c => c.employee_id === emp.id && c.statut === "validée" && c.type_conge !== "annuel").reduce((s,c)=>s+calculateDays(c.date_debut,c.date_fin),0); return { employe: `${emp.nom} ${emp.prenom}`, periode: `${mois.toString().padStart(2,"0")}/${annee}`, heures_normales: heuresNormales.toFixed(2), heures_supplementaires: heuresSup.toFixed(2), absences_jours: absencesJours, conges_non_payes_jours: congesNonPayes }; });
  const handleExport = (format) => {
  const mois = parseInt(window.prompt("Mois (1-12)"));
  const annee = parseInt(window.prompt("Année (ex: 2026)"));
  if (!mois || !annee) return alert("Période invalide");

  const rows = employees.map(emp => {
    // POINTAGES
    const empPointages = pointages.filter(p => {
      const d = new Date(p.date);
      return p.employee_id === emp.id && d.getMonth() + 1 === mois && d.getFullYear() === annee;
    });
    let heuresNormales = 0, heuresSup = 0;
    empPointages.forEach(p => {
      const hIn = new Date(`1970-01-01T${p.heure_entree}`);
      const hOut = new Date(`1970-01-01T${p.heure_sortie}`);
      const diff = (hOut - hIn) / (1000 * 60 * 60);
      if (diff > 8) { heuresNormales += 8; heuresSup += diff - 8; } 
      else { heuresNormales += diff; }
    });

    // ABSENCES VALIDÉES
    const absencesJours = absences
      .filter(a => a.employee_id === emp.id && a.statut === "validée")
      .reduce((sum, a) => sum + calculateDays(a.date_debut, a.date_fin), 0);

    // CONGÉS NON PAYÉS (VALIDÉS)
    const congesNonPayes = conges
      .filter(c => c.employee_id === emp.id && c.statut === "validée" && c.type_conge !== "annuel")
      .reduce((sum, c) => sum + calculateDays(c.date_debut, c.date_fin), 0);

    return {
      Employé: `${emp.nom} ${emp.prenom}`,
      Période: `${mois.toString().padStart(2,"0")}/${annee}`,
      "Heures normales": heuresNormales.toFixed(2),
      "Heures supplémentaires": heuresSup.toFixed(2),
      "Absences (jours)": absencesJours,
      "Congés non payés (jours)": congesNonPayes
    };
  });

  if (format === "csv") {
    const header = Object.keys(rows[0]).join(",") + "\n";
    const body = rows.map(r => Object.values(r).join(",")).join("\n");
    const blob = new Blob([header + body], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `export_paie_${mois}_${annee}.csv`;
    link.click();
  }
};
  // -----------------------------
  // Ouvrir popup détails
  const openPopup = (type, employee_id) => {
    const emp = employees.find(e => e.id === employee_id);
    let data = [];
    if (type === "absence") data = absences.filter(a => a.employee_id === employee_id);
    else if (type === "pointage") data = pointages.filter(p => p.employee_id === employee_id);
    else if (type === "conge") data = conges.filter(c => c.employee_id === employee_id);

    setPopupData({ type, emp, data });
  };

  // -----------------------------
  // UI
  return (
    <div className="temps-absences-page">
      <div className="header">
        <h2>Module Temps & Absences</h2>
        <div className="tabs">
          <button onClick={() => handleTabChange("absences")}>Absences</button>
          <button onClick={() => handleTabChange("pointages")}>Pointages</button>
          <button onClick={() => handleTabChange("conges")}>Congés</button>
          <button onClick={() => handleTabChange("soldes")}>Soldes</button>
          <button onClick={() => handleTabChange("export")}>Export Paie</button>
        </div>
      </div>

      {/* ------------------ Absences ------------------ */}
      {tab === "absences" && (
        <div className="tab-content">
          <input type="text" placeholder="Rechercher par employé..." value={searchEmployee} onChange={e => setSearchEmployee(e.target.value)} style={{ marginBottom: "10px", width: "300px" }} />
          <button onClick={() => setShowAbsenceForm(!showAbsenceForm)}>{showAbsenceForm ? "Masquer Formulaire" : "Créer une absence"}</button>
          {showAbsenceForm && (
            <form onSubmit={handleAbsenceSubmit}>
              <label>Employé<input type="text" list="employees-list" name="employee_id" value={absenceForm.employee_id} onChange={handleAbsenceChange} />
                <datalist id="employees-list">{employees.map(emp => <option key={emp.id} value={emp.id}>{emp.nom} {emp.prenom}</option>)}</datalist>
              </label>
              <label>Date début <input type="date" name="date_debut" value={absenceForm.date_debut} onChange={handleAbsenceChange} /></label>
              <label>Date fin <input type="date" name="date_fin" value={absenceForm.date_fin} onChange={handleAbsenceChange} /></label>
              <label>Type<select name="type_absence" value={absenceForm.type_absence} onChange={handleAbsenceChange}>
                <option value="maladie">Maladie</option>
                <option value="conge">Congé</option>
                <option value="non_justifiee">Non justifiée</option>
              </select></label>
              <label>Statut<select name="statut" value={absenceForm.statut} onChange={handleAbsenceChange}>
                <option value="en attente">En attente</option>
                <option value="validée">Validée</option>
                <option value="refusée">Refusée</option>
              </select></label>
              <label>Motif <input type="text" name="motif" value={absenceForm.motif} onChange={handleAbsenceChange} /></label>
              <button type="submit">{editingAbsenceId ? "Modifier" : "Ajouter"}</button>
            </form>
          )}
          <table><thead><tr><th>#</th><th>Employé</th><th>Détail</th><th>Actions</th></tr></thead><tbody>{[...new Map(filterByEmployee(absences).map(a=>[a.employee_id,a])).values()].map((a,i)=>{const emp=employees.find(e=>e.id===a.employee_id);return <tr key={a.employee_id}><td>{i+1}</td><td>{emp?`${emp.nom} ${emp.prenom}`:"—"}</td><td><button onClick={()=>openPopup("absence",a.employee_id)}>⋮</button></td><td><button onClick={()=>handleAbsenceEdit(a)}>✏️</button><button onClick={()=>handleAbsenceDelete(a.id)}>🗑️</button></td></tr>;})}</tbody></table>

        </div>
      )}

      {/* ------------------ Pointages ------------------ */}
      {tab === "pointages" && (
        <div className="tab-content">
          <input type="text" placeholder="Rechercher par employé..." value={searchEmployee} onChange={e => setSearchEmployee(e.target.value)} style={{ marginBottom: "10px", width: "300px" }} />

          <button onClick={() => setShowPointageForm(!showPointageForm)}>{showPointageForm ? "Masquer Formulaire" : "Créer un pointage"}</button>
          {showPointageForm && (
            <form onSubmit={handlePointageSubmit}>
              <label>Employé<input type="text" list="employees-list" value={pointageForm.employee_id} name="employee_id" onChange={handlePointageChange} />
                <datalist id="employees-list">{employees.map(emp => <option key={emp.id} value={emp.id}>{emp.nom} {emp.prenom}</option>)}</datalist>
              </label>
              <label>Date <input type="date" name="date" value={pointageForm.date} onChange={handlePointageChange} /></label>
              <label>Heure entrée <input type="time" name="heure_entree" value={pointageForm.heure_entree} onChange={handlePointageChange} /></label>
              <label>Heure sortie <input type="time" name="heure_sortie" value={pointageForm.heure_sortie} onChange={handlePointageChange} /></label>
              <button type="submit">{editingPointageId ? "Modifier" : "Ajouter"}</button>
            </form>
          )}
          <table><thead><tr><th>#</th><th>Employé</th><th>Détail</th><th>Actions</th></tr></thead><tbody>{[...new Map(filterByEmployee(pointages).map(p=>[p.employee_id,p])).values()].map((p,i)=>{const emp=employees.find(e=>e.id===p.employee_id);return <tr key={p.employee_id}><td>{i+1}</td><td>{emp?`${emp.nom} ${emp.prenom}`:"—"}</td><td><button onClick={()=>openPopup("pointage",p.employee_id)}>⋮</button></td><td><button onClick={()=>handlePointageDelete(p.id)}>🗑️</button></td></tr>;})}</tbody></table>

        </div>
      )}

      {/* ------------------ Congés ------------------ */}
      {tab === "conges" && (
        <div className="tab-content">
          <input type="text" placeholder="Rechercher par employé..." value={searchEmployee} onChange={e => setSearchEmployee(e.target.value)} style={{ marginBottom: "10px", width: "300px" }} />

          <button onClick={() => setShowCongeForm(!showCongeForm)}>{showCongeForm ? "Masquer Formulaire" : "Créer un congé"}</button>
          {showCongeForm && (
            <form onSubmit={handleCongeSubmit}>
              <label>Employé<input type="text" list="employees-list" value={congeForm.employee_id} name="employee_id" onChange={handleCongeChange} />
                <datalist id="employees-list">{employees.map(emp => <option key={emp.id} value={emp.id}>{emp.nom} {emp.prenom}</option>)}</datalist>
              </label>
              <label>Date début <input type="date" name="date_debut" value={congeForm.date_debut} onChange={handleCongeChange} /></label>
              <label>Date fin <input type="date" name="date_fin" value={congeForm.date_fin} onChange={handleCongeChange} /></label>
              <label>Type<select name="type_conge" value={congeForm.type_conge} onChange={handleCongeChange}>
                <option value="annuel">Annuel</option>
                <option value="maladie">Maladie</option>
                <option value="exceptionnel">Exceptionnel</option>
              </select></label>
              <label>Statut<select name="statut" value={congeForm.statut} onChange={handleCongeChange}>
                <option value="en attente">En attente</option>
                <option value="validée">Validée</option>
                <option value="refusée">Refusée</option>
              </select></label>
              <label>Motif <input type="text" name="motif" value={congeForm.motif} onChange={handleCongeChange} /></label>
              <button type="submit">{editingCongeId ? "Modifier" : "Ajouter"}</button>
            </form>
          )}
          <table><thead><tr><th>#</th><th>Employé</th><th>Détail</th><th>Actions</th></tr></thead><tbody>{[...new Map(filterByEmployee(conges).map(c=>[c.employee_id,c])).values()].map((c,i)=>{const emp=employees.find(e=>e.id===c.employee_id);return <tr key={c.employee_id}><td>{i+1}</td><td>{emp?`${emp.nom} ${emp.prenom}`:"—"}</td><td><button onClick={()=>openPopup("conge",c.employee_id)}>⋮</button></td><td><button onClick={()=>handleCongeEdit(c)}>✏️</button><button onClick={()=>handleCongeDelete(c.id)}>🗑️</button></td></tr>;})}</tbody></table>

        </div>
      )}

      {/* ------------------ Soldes ------------------ */}
      {tab === "soldes" && (
        <div className="tab-content">
          <input type="text" placeholder="Rechercher par employé..." value={searchEmployee} onChange={e => setSearchEmployee(e.target.value)} style={{ marginBottom: "10px", width: "300px" }} />

          <h3>Soldes des employés</h3>
          <table><thead><tr><th>Rang</th><th>Employé</th><th>Congés pris</th><th>Absences non payées</th><th>Solde congés</th></tr></thead><tbody>{filterByEmployee(soldes).map((s,i)=>{const emp=employees.find(e=>e.id===s.employee_id);const congesPris=s.conges_pris;const absencesNonPayees=s.absences_non_payees;const soldeConges=30-congesPris;return <tr key={s.employee_id}><td>{i+1}</td><td>{emp?`${emp.nom} ${emp.prenom}`:"—"}</td><td>{congesPris}</td><td>{absencesNonPayees}</td><td>{soldeConges}</td></tr>;})}</tbody></table>

        </div>
      )}

      {/* ------------------ Export ------------------ */}
      {tab === "export" && (
        <div className="tab-content">
          <input type="text" placeholder="Rechercher par employé..." value={searchEmployee} onChange={e => setSearchEmployee(e.target.value)} style={{ marginBottom: "10px", width: "300px" }} />
          <h3>Export Paie</h3>
          <select onChange={e => e.target.value && handleExport(e.target.value)} defaultValue=""><option value="" disabled>Exporter Paie</option><option value="csv">CSV</option><option value="excel">Excel</option></select>
          <table>
            <thead><tr><th>Employé</th><th>Période</th><th>Heures normales</th><th>Heures supplémentaires</th><th>Absences (jours)</th><th>Congés non payés (jours)</th></tr></thead>
            <tbody>{employees.filter(emp=>!searchEmployee||`${emp.nom} ${emp.prenom}`.toLowerCase().includes(searchEmployee.toLowerCase())).map(emp=>{const mois=new Date().getMonth()+1,annee=new Date().getFullYear(),empPointages=pointages.filter(p=>p.employee_id===emp.id&&new Date(p.date).getMonth()+1===mois&&new Date(p.date).getFullYear()===annee);let heuresNormales=0,heuresSup=0;empPointages.forEach(p=>{const hIn=new Date(`1970-01-01T${p.heure_entree}`),hOut=new Date(`1970-01-01T${p.heure_sortie}`),diff=(hOut-hIn)/(1000*60*60);diff>8?(heuresNormales+=8,heuresSup+=diff-8):heuresNormales+=diff;});const absencesJours=absences.filter(a=>a.employee_id===emp.id&&a.statut==="validée").reduce((s,a)=>s+calculateDays(a.date_debut,a.date_fin),0);const congesNonPayes=conges.filter(c=>c.employee_id===emp.id&&c.statut==="validée"&&c.type_conge!=="annuel").reduce((s,c)=>s+calculateDays(c.date_debut,c.date_fin),0);return <tr key={emp.id}><td>{emp.nom} {emp.prenom}</td><td>{mois.toString().padStart(2,"0")}/{annee}</td><td>{heuresNormales.toFixed(2)}</td><td>{heuresSup.toFixed(2)}</td><td>{absencesJours}</td><td>{congesNonPayes}</td></tr>;})}</tbody>
          </table>
        </div>
      )}

      {/* ------------------ Popup Détails ------------------ */}
      {popupData && (
        <div className="popup-overlay" onClick={() => setPopupData(null)}>
          <div className="popup-content" onClick={(e) => e.stopPropagation()}>
            <h3>Détails {popupData.type}</h3>
            <p><strong>Employé :</strong> {popupData.emp ? `${popupData.emp.nom} ${popupData.emp.prenom}` : "—"}</p>
            {popupData.type === "pointage" && <p>{popupData.data.length}/{["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"][new Date(popupData.data[0].date).getMonth()]}</p>}

            {popupData.data.length === 0 ? (
              <p>Aucune donnée</p>
            ) : (
              <ul>
                {popupData.data.map((d, idx) => (
                  <li key={idx}>
                    {popupData.type === "absence" && `Du ${d.date_debut} au ${d.date_fin} — Type: ${d.type_absence} — Statut: ${d.statut} — Motif: ${d.motif || "—"}`}
                    {popupData.type === "pointage" && `Date: ${d.date} — Entrée: ${d.heure_entree} — Sortie: ${d.heure_sortie}`}
                    {popupData.type === "conge" && `Du ${d.date_debut} au ${d.date_fin} — Type: ${d.type_conge} — Statut: ${d.statut} — Motif: ${d.motif || "—"}`}
                  </li>
                ))}
              </ul>
            )}
            <button onClick={() => setPopupData(null)}>Fermer</button>
          </div>
        </div>
      )}
    </div>
  );
}






 
