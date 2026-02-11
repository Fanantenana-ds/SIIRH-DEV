import React, { useEffect, useState } from "react";
import axios from "axios";
import { FileText, Search, ChevronDown } from "lucide-react";
import "./Contrats.css";

const Contrats = () => {
  const [contrats, setContrats] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [exportDropdown, setExportDropdown] = useState(null); // contrat_id

  const [formData, setFormData] = useState({
    employee_id: "",
    searchEmployee: "",
    filteredEmployees: [],
    type_contrat: "CDI",
    date_debut: "",
    date_fin: "",
    salaire: "",
    poste: "",
    periode: "",
    avantages: "",
    clauses: "",
    type_travail: "Temps plein",
    preavis: "",
    indemnites: ""
  });

  // ------------------ FETCH DATA ------------------
  const fetchEmployees = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/api/employes/");
      setEmployees(res.data);
    } catch (err) {
      console.error("Erreur fetch employés:", err);
    }
  };

  const fetchContrats = async () => {
    if (!employees.length) return;
    try {
      const res = await axios.get("http://127.0.0.1:8000/api/contrats/");
      const contratsWithNom = res.data.map(c => {
        const emp = employees.find(e => e.id === c.employee_id);
        return { ...c, nom_complet: emp ? emp.nom + " " + emp.prenom : "—" };
      });
      setContrats(contratsWithNom);
    } catch (err) {
      console.error("Erreur fetch contrats:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchEmployees(); }, []);
  useEffect(() => { fetchContrats(); }, [employees]);

  // ------------------ FORM HANDLERS ------------------
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    let updated = { ...formData, [name]: value };
    if (name === "type_contrat" || name === "date_debut") {
      updated = calculateAutomatic(updated);
    }
    setFormData(updated);
  };

  const calculateAutomatic = (data) => {
    let preavis = "";
    let indemnites = "";
    if (data.type_contrat === "CDI") preavis = "30 jours";
    if (data.type_contrat === "CDD") preavis = "15 jours avant échéance";
    if (data.type_contrat === "Stage") preavis = "48 heures";
    if (data.type_contrat === "Alternance") preavis = "1 semaine";
    if (data.type_contrat === "CDD") indemnites = "10% de la rémunération brute totale";
    return { ...data, preavis, indemnites };
  };

  // ------------------ AUTOCOMPLETE EMPLOYE ------------------
  const handleEmployeeSearch = (e) => {
    const term = e.target.value.toLowerCase();
    setFormData({
      ...formData,
      searchEmployee: e.target.value,
      filteredEmployees: employees.filter(emp =>
        emp.nom.toLowerCase().includes(term) ||
        emp.prenom.toLowerCase().includes(term)
      )
    });
  };

  const handleSelectEmployee = (emp) => {
    setFormData({
      ...formData,
      employee_id: emp.id,
      searchEmployee: emp.nom + " " + emp.prenom,
      filteredEmployees: []
    });
  };

  // ------------------ SUBMIT ------------------
  const handleFormSubmit = async (e) => {
    e.preventDefault();
    if (!formData.employee_id) return alert("Veuillez sélectionner un employé.");
    try {
      const payload = {
        employee_id: formData.employee_id,
        type_contrat: formData.type_contrat,
        date_debut: formData.date_debut,
        date_fin: formData.date_fin || null,
        salaire: formData.salaire ? parseFloat(formData.salaire) : 0,
        poste: formData.poste,
        periode: formData.periode,
        avantages: formData.avantages,
        clauses: formData.clauses,
        type_travail: formData.type_travail,
        preavis: formData.preavis,
        indemnites: formData.indemnites
      };
      const res = await axios.post("http://127.0.0.1:8000/api/contrats/", payload);
      const employee = employees.find(emp => emp.id === formData.employee_id);
      const newContrat = { ...res.data, nom_complet: employee ? employee.nom + " " + employee.prenom : "—" };
      setContrats([...contrats, newContrat]);
      setShowForm(false);
      setFormData({
        employee_id: "",
        searchEmployee: "",
        filteredEmployees: [],
        type_contrat: "CDI",
        date_debut: "",
        date_fin: "",
        salaire: "",
        poste: "",
        periode: "",
        avantages: "",
        clauses: "",
        type_travail: "Temps plein",
        preavis: "",
        indemnites: ""
      });
    } catch (err) {
      console.error("Erreur création contrat:", err);
      alert("Erreur lors de la création du contrat");
    }
  };

  // ------------------ SEARCH ------------------
  const handleSearch = (e) => setSearchTerm(e.target.value.toLowerCase());
  const filteredContrats = contrats.filter(c => {
    const nom = c.nom_complet?.toLowerCase() || "";
    const type = c.type_contrat?.toLowerCase() || "";
    return nom.includes(searchTerm) || type.includes(searchTerm);
  });

  // ------------------ EXPORT HANDLER ------------------
  const handleExport = async (contrat_id, format) => {
    try {
      const res = await axios.get(
        `http://127.0.0.1:8000/api/contrats/export/${contrat_id}?format=${format}`,
        { responseType: "blob" }
      );
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `contrat_${contrat_id}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setExportDropdown(null);
    } catch (err) {
      console.error("Erreur export contrat:", err);
      alert("Erreur lors de l'export du contrat");
    }
  };

  // ------------------ RENDER ------------------
  return (
    <div className="contrats-wrapper">
      <div className="contrats-header">
        <h1 className="contrats-title">
          <FileText className="contrats-title-icon" />
          Gestion des Contrats
        </h1>
        <div className="contrats-search-container">
          <div className="search-wrapper">
            <Search className="search-icon" />
            <input type="text" placeholder="Rechercher par nom ou type de contrat..." value={searchTerm} onChange={handleSearch} />
          </div>
          <button onClick={() => setShowForm(true)} className="btn-add">+ Créer Contrat</button>
        </div>
      </div>

      {showForm && (
        <div className="contrat-form-overlay">
          <div className="contrat-form">
            <h2>Créer un Contrat</h2>
            <form onSubmit={handleFormSubmit}>
              {/* EMPLOYE */}
              <div className="form-group">
                <label>Employé</label>
                <input
                  type="text"
                  placeholder="Rechercher un employé..."
                  value={formData.searchEmployee}
                  onChange={handleEmployeeSearch}
                />
                {formData.filteredEmployees.length > 0 && (
                  <div className="autocomplete-list">
                    {formData.filteredEmployees.map(emp => (
                      <div key={emp.id} className="autocomplete-item" onClick={() => handleSelectEmployee(emp)}>
                        {emp.nom} {emp.prenom}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* TYPE CONTRAT */}
              <div className="form-group">
                <label>Type de contrat</label>
                <select name="type_contrat" value={formData.type_contrat} onChange={handleFormChange}>
                  <option value="CDI">CDI</option>
                  <option value="CDD">CDD</option>
                  <option value="Stage">Stage</option>
                  <option value="Alternance">Alternance</option>
                </select>
              </div>

              {/* POSTE */}
              <div className="form-group">
                <label>Poste</label>
                <input type="text" name="poste" value={formData.poste} onChange={handleFormChange} required />
              </div>

              {/* PERIODE */}
              <div className="form-group">
                <label>Période du contrat</label>
                <input type="text" placeholder="Ex: 6 mois, 1 an" name="periode" value={formData.periode} onChange={handleFormChange} />
              </div>

              {/* DATE DEBUT */}
              <div className="form-group">
                <label>Date début</label>
                <input type="date" name="date_debut" value={formData.date_debut} onChange={handleFormChange} required />
              </div>

              {/* DATE FIN */}
              <div className="form-group">
                <label>Date fin</label>
                <input type="date" name="date_fin" value={formData.date_fin} onChange={handleFormChange} />
              </div>

              {/* SALAIRE */}
              <div className="form-group">
                <label>Salaire</label>
                <input type="number" name="salaire" value={formData.salaire} onChange={handleFormChange} />
              </div>

              {/* AVANTAGES */}
              <div className="form-group">
                <label>Avantages</label>
                <textarea name="avantages" value={formData.avantages} onChange={handleFormChange} placeholder="Repas, transport, assurance..." />
              </div>

              {/* CLAUSES */}
              <div className="form-group">
                <label>Clauses particulières</label>
                <textarea name="clauses" value={formData.clauses} onChange={handleFormChange} />
              </div>

              {/* TYPE TRAVAIL */}
              <div className="form-group">
                <label>Type de travail</label>
                <select name="type_travail" value={formData.type_travail} onChange={handleFormChange}>
                  <option>Temps plein</option>
                  <option>Temps partiel</option>
                </select>
              </div>

              {/* PREAVIS */}
              <div className="form-group">
                <label>Préavis (auto)</label>
                <input type="text" value={formData.preavis} disabled />
              </div>

              {/* INDEMNITES */}
              <div className="form-group">
                <label>Indemnités (auto)</label>
                <input type="text" value={formData.indemnites} disabled />
              </div>

              <div className="form-actions">
                <button type="button" onClick={() => setShowForm(false)} className="btn-cancel">Annuler</button>
                <button type="submit" className="btn-submit">Enregistrer</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {!loading ? (
        <div className="contrats-table-container">
          <table className="contrats-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nom complet</th>
                <th>Type</th>
                <th>Poste</th>
                <th>Date début</th>
                <th>Date fin</th>
                <th>Salaire</th>
                <th>Exporter</th>
              </tr>
            </thead>
            <tbody>
              {filteredContrats.map(c => (
                <tr key={c.id}>
                  <td>{c.id}</td>
                  <td>{c.nom_complet || "—"}</td>
                  <td>{c.type_contrat}</td>
                  <td>{c.poste || "—"}</td>
                  <td>{c.date_debut ? new Date(c.date_debut).toLocaleDateString() : "—"}</td>
                  <td>{c.date_fin ? new Date(c.date_fin).toLocaleDateString() : "—"}</td>
                  <td>{c.salaire || "—"}</td>
                  <td>
                    <div className="export-container">
                      <button className="btn-export" onClick={() => setExportDropdown(exportDropdown === c.id ? null : c.id)}>
                        Exporter <ChevronDown size={16} />
                      </button>
                      {exportDropdown === c.id && (
                        <div className="export-dropdown">
                          <div onClick={() => handleExport(c.id, "pdf")}>PDF</div>
                          <div onClick={() => handleExport(c.id, "docx")}>DOCX</div>
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="contrats-loading">Chargement des contrats...</div>
      )}
    </div>
  );
};

export default Contrats;
