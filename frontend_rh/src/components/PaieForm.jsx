import React, { forwardRef, useEffect, useState, useImperativeHandle } from "react";
import { getEmployees } from "../api/employeeApi";
import { createPaie } from "../api/paieApi";

const PaieForm = forwardRef(({ onSaved }, ref) => {
  const [employees, setEmployees] = useState([]);
  const [form, setForm] = useState({
    employee_id: "",
    primes: 0,
    heures_supp: 0,
    deductions: 0,
    mois: "",
    annee: ""
  });
  const [employeeInput, setEmployeeInput] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);

  // Load employees
  useEffect(() => {
    getEmployees().then(res => setEmployees(res.data));
  }, []);

  // Handle input change
  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  // Submit handler
  const handleSubmit = async (e) => {
    if (e.preventDefault) e.preventDefault();

    // Capitalize mois pour backend
    const moisFormatted = form.mois.charAt(0).toUpperCase() + form.mois.slice(1);

    const payload = {
      employee_id: parseInt(form.employee_id),
      mois: moisFormatted,
      annee: parseInt(form.annee),
      primes: parseFloat(form.primes) || 0,
      heures_supp: parseFloat(form.heures_supp) || 0,
      deductions: parseFloat(form.deductions) || 0,
      salaire_base: 0,
      absence_deduction: 0,
      salaire_net: 0,
      montant: 0
    };

    try {
      await createPaie(payload);
      onSaved();
      setForm({
        employee_id: "",
        primes: 0,
        heures_supp: 0,
        deductions: 0,
        mois: "",
        annee: ""
      });
      setEmployeeInput("");
    } catch (err) {
      console.error(err);
      alert("Erreur lors de l'enregistrement. Vérifiez les champs et réessayez.");
    }
  };

  // Forward ref submit
  useImperativeHandle(ref, () => ({
    submit: () => handleSubmit({ preventDefault: () => {} })
  }));

  // Filter employees
  const filteredEmployees = employees.filter(emp => {
    const name = emp.fullname || `${emp.nom} ${emp.prenom}`;
    return name.toLowerCase().includes(employeeInput.toLowerCase());
  });

  // Current year
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 10 }, (_, i) => currentYear - i);

  // French months
  const months = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
  ];

  return (
    <form onSubmit={handleSubmit} className="paie-form">
      {/* Employé */}
      <label>Employé</label>
      <div style={{ position: "relative", width: "100%" }}>
        <input
          type="text"
          placeholder="Sélectionner un employé"
          value={employeeInput}
          onChange={e => { setEmployeeInput(e.target.value); setShowDropdown(true); }}
          onFocus={() => setShowDropdown(true)}
          onBlur={() => setTimeout(() => setShowDropdown(false), 100)}
          required
        />
        {showDropdown && filteredEmployees.length > 0 && (
          <ul style={{
            position: "absolute",
            top: "100%",
            left: 0,
            right: 0,
            maxHeight: "150px",
            overflowY: "auto",
            backgroundColor: "#fff",
            border: "1px solid #bbb",
            borderRadius: "6px",
            margin: 0,
            padding: 0,
            listStyle: "none",
            zIndex: 1000
          }}>
            {filteredEmployees.map(emp => {
              const name = emp.fullname || `${emp.nom} ${emp.prenom}`;
              return (
                <li
                  key={emp.id}
                  style={{ padding: "8px", cursor: "pointer" }}
                  onMouseDown={() => {
                    setForm(prev => ({ ...prev, employee_id: emp.id }));
                    setEmployeeInput(name);
                    setShowDropdown(false);
                  }}
                >
                  {name}
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {/* Primes */}
      <label>Primes</label>
      <input
        type="number"
        name="primes"
        value={form.primes}
        onChange={handleChange}
        placeholder="Montant des primes"
      />

      {/* Heures supplémentaires */}
      <label>Heures supplémentaires</label>
      <input
        type="number"
        name="heures_supp"
        value={form.heures_supp}
        onChange={handleChange}
        placeholder="Nombre d'heures"
      />

      {/* Déductions */}
      <label>Déductions</label>
      <input
        type="number"
        name="deductions"
        value={form.deductions}
        onChange={handleChange}
        placeholder="Montant des déductions"
      />

      {/* Mois */}
      <label>Mois</label>
      <select name="mois" value={form.mois} onChange={handleChange} required>
        <option value="">Sélectionner un mois</option>
        {months.map(m => <option key={m} value={m}>{m}</option>)}
      </select>

      {/* Année */}
      <label>Année</label>
      <select name="annee" value={form.annee} onChange={handleChange} required>
        <option value="">Sélectionner une année</option>
        {years.map(y => <option key={y} value={y}>{y}</option>)}
      </select>
    </form>
  );
});

export default PaieForm;
