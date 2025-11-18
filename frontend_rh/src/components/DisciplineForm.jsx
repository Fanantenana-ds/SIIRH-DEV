import React, { useState } from "react";
import DisciplineForm from "./components/DisciplineForm";

import "./discipline.css";

export default function DisciplineForm() {
    const [files, setFiles] = useState([]);

    const handleFile = (e) => {
        setFiles([...files, ...Array.from(e.target.files)]);
    };

    return (
        <div className="discipline-container">
            <h1 className="page-title">Créer un dossier disciplinaire</h1>

            {/* --- INFOS EMPLOYE --- */}
            <div className="card">
                <h2 className="card-title">Informations de l’employé</h2>

                <div className="two-columns">
                    <div className="form-group">
                        <label>Employé concerné</label>
                        <select>
                            <option>-- Sélectionner --</option>
                            <option>Rakoto Jean</option>
                            <option>Rasoa Liva</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Matricule</label>
                        <input type="text" disabled />
                    </div>

                    <div className="form-group">
                        <label>Poste</label>
                        <input type="text" disabled />
                    </div>

                    <div className="form-group">
                        <label>Département</label>
                        <input type="text" disabled />
                    </div>
                </div>
            </div>

            {/* --- TYPE DE FAUTE --- */}
            <div className="card">
                <h2 className="card-title">Détails de la faute</h2>

                <div className="two-columns">
                    <div className="form-group">
                        <label>Catégorie</label>
                        <select>
                            <option>Mineure</option>
                            <option>Grave</option>
                            <option>Lourde</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Nature</label>
                        <select>
                            <option>Retard répété</option>
                            <option>Absence injustifiée</option>
                            <option>Violence</option>
                            <option>Fraude</option>
                        </select>
                    </div>
                </div>

                <div className="form-group full">
                    <label>Description détaillée</label>
                    <textarea rows="4" />
                </div>
            </div>

            {/* --- PREUVES --- */}
            <div className="card">
                <h2 className="card-title">Preuves</h2>

                <div className="upload-box">
                    <p>Uploader des fichiers</p>
                    <input type="file" multiple onChange={handleFile} />
                </div>

                <div className="file-list">
                    {files.map((f, i) => (
                        <div key={i} className="file-item">📎 {f.name}</div>
                    ))}
                </div>
            </div>

            {/* --- CONVOCATION --- */}
            <div className="card">
                <h2 className="card-title">Convocation</h2>

                <div className="two-columns">
                    <div className="form-group">
                        <label>Modèle</label>
                        <select>
                            <option>Standard</option>
                            <option>Faute grave</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Date</label>
                        <input type="date" />
                    </div>

                    <div className="form-group">
                        <label>Heure</label>
                        <input type="time" />
                    </div>

                    <div className="form-group">
                        <label>Lieu</label>
                        <input type="text" placeholder="Salle RH" />
                    </div>

                    <div className="form-group full">
                        <label>Responsable</label>
                        <input type="text" placeholder="Nom du responsable" />
                    </div>
                </div>
            </div>

            {/* --- ACTIONS --- */}
            <div className="footer-actions">
                <button className="btn-secondary">Annuler</button>
                <button className="btn-primary">Enregistrer</button>
                <button className="btn-main">Générer convocation</button>
            </div>
        </div>
    );
}
