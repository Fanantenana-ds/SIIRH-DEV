import { useEffect, useState, useRef } from "react";
import { getPaies } from "../api/paieApi";
import PaieForm from "../components/PaieForm";
import PaieTable from "../components/PaieTable";
import "../styles/paie.css";

export default function Paie() {
  const [paies, setPaies] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const formRef = useRef(null);

  const loadPaies = () => {
    getPaies().then((res) => setPaies(res.data));
  };

  useEffect(() => {
    loadPaies();
  }, []);

  return (
    <div className="paie-container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <h1 className="paie-title">Gestion de la Paie</h1>
        <button className="btn-ajout" onClick={() => setShowForm(true)}>Ajouter une Paie</button>
      </div>

      <div className="paie-card">
        <h2 className="paie-section-title">Liste des Paiements</h2>
        <PaieTable paies={paies} onDeleted={loadPaies} />
      </div>

      {showForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2 className="paie-section-title">Nouvelle Paie</h2>
            <PaieForm ref={formRef} onSaved={() => { loadPaies(); setShowForm(false); }} />
            <div style={{ display: "flex", gap: "10px", marginTop: "15px" }}>
              <button className="btn-annuler" onClick={() => setShowForm(false)}>Annuler</button>
              <button className="btn-enregistrer" onClick={() => formRef.current?.submit()}>Ajout</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
