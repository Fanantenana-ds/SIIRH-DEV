



// // // src/pages/DisciplineForm.jsx

// import React, { useState, useEffect } from "react";
// import "./Discipline.css";

// const DisciplineForm = ({ onCreate, isEditing, dossier }) => {
//     // ===============================================
//     //  STATE DE BASE — asa rehetra amin’ny formulaire
//     // ===============================================
//     const [employees, setEmployees] = useState([]);
//     const [selectedEmployee, setSelectedEmployee] = useState("");
//     const [matricule, setMatricule] = useState("");
//     const [poste, setPoste] = useState("");

//     const [faultCategory, setFaultCategory] = useState("");
//     const [faultNature, setFaultNature] = useState("");
//     const [customNature, setCustomNature] = useState(""); // rehefa "Autres"

//     const [description, setDescription] = useState("");

//     const [proofs, setProofs] = useState([]);

//     const [convocationModel, setConvocationModel] = useState("");
//     const [convocationDate, setConvocationDate] = useState("");
//     const [convocationTime, setConvocationTime] = useState("");
//     const [convocationPlace, setConvocationPlace] = useState("");
//     const [convocationManager, setConvocationManager] = useState("");

//     // ===============================================
//     //  OPTIONS REQUIS PAR LE CAHIER DE CHARGES
//     // ===============================================
//     const faultCategories = ["Mineure", "Grave", "Lourde"];

//     const faultNatures = [
//         "Retard répété",
//         "Absence injustifiée",
//         "Manquement aux règles internes",
//         "Insulte / violence",
//         "Non-respect consignes sécurité",
//         "Vol / Fraude",
//         "Autres" // permet de saisir librement
//     ];

//     const convocationModels = ["Modèle A", "Modèle B", "Modèle C"];

//     // ===============================================
//     //  FAKE FETCH employees — ho soloina API backend
//     // ===============================================
//     useEffect(() => {
//         // rehefa misy backend:
//         // fetch("/api/employees") → setEmployees(result);

//         setEmployees([
//             { id: 1, nom: "Jean Dupont", matricule: "E001", poste: "Développeur Web" },
//             { id: 2, nom: "Marie Curie", matricule: "E002", poste: "Responsable RH" },
//             { id: 3, nom: "Albert Einstein", matricule: "E003", poste: "Analyste" }
//         ]);
//     }, []);

//     // ===============================================
//     //  MANAO AUTO-FILL matricule sy poste
//     // ===============================================
//     const handleEmployeeChange = (e) => {
//         const empId = e.target.value;
//         setSelectedEmployee(empId);

//         const emp = employees.find((x) => x.id === parseInt(empId));
//         if (emp) {
//             setMatricule(emp.matricule);
//             setPoste(emp.poste);
//         }
//     };

//     // ===============================================
//     //  GESTION UPLOAD — store fichiers ho an'ny backend
//     // ===============================================
//     const handleProofUpload = (e) => {
//         setProofs([...e.target.files]);
//     };

//     // ===============================================
//     //  ANNULER — fermer & réinitialiser formulaire
//     // ===============================================
//     const handleReset = () => {
//         onCreate(null); // MIANTSO PARENT -> midika hoe ANNULER
//     };

//     // ===============================================
//     //  SUBMIT CREATION — hitondra backend POST taty aoriana
//     // ===============================================
//     const handleSubmit = (e) => {
//         e.preventDefault();

//         // payload handeha amin'ny backend
//         const dossierData = {
//             employe: selectedEmployee,
//             matricule,
//             poste,
//             faultCategory,
//             faultNature: faultNature === "Autres" ? customNature : faultNature,
//             description,
//             proofs,
//             convocationModel,
//             convocationDate,
//             convocationTime,
//             convocationPlace,
//             convocationManager,
//         };

//         // antsoin'ny DisciplinePage → adds to list
//         onCreate(dossierData);

//         alert("Dossier disciplinaire créé avec succès !");
//         handleReset();
//     };

//     return (
//         <form className="discipline-form" onSubmit={handleSubmit}>
//             <h3 className="form-section-title">Informations Employé</h3>

//             {/* SELECT EMPLOYE */}
//             <label>
//                 Employé concerné :
//                 <select
//                     value={selectedEmployee}
//                     onChange={handleEmployeeChange}
//                     required
//                 >
//                     <option value="">-- Sélectionner l'employé --</option>
//                     {employees.map((emp) => (
//                         <option key={emp.id} value={emp.id}>
//                             {emp.nom}
//                         </option>
//                     ))}
//                 </select>
//             </label>

//             {/* AUTO FILL */}
//             <label>
//                 Matricule :
//                 <input
//                     type="text"
//                     value={matricule}
//                     placeholder="Automatique"
//                     readOnly
//                 />
//             </label>

//             <label>
//                 Poste / Département :
//                 <input
//                     type="text"
//                     value={poste}
//                     placeholder="Automatique"
//                     readOnly
//                 />
//             </label>

//             <h3 className="form-section-title">Type de Faute</h3>

//             {/* CATEGORIE */}
//             <label>
//                 Catégorie de faute :
//                 <select
//                     value={faultCategory}
//                     onChange={(e) => setFaultCategory(e.target.value)}
//                     required
//                 >
//                     <option value="">-- Choisir la catégorie --</option>
//                     {faultCategories.map((fc) => (
//                         <option key={fc} value={fc}>
//                             {fc}
//                         </option>
//                     ))}
//                 </select>
//             </label>

//             {/* NATURE */}
//             <label>
//                 Nature de la faute :
//                 <select
//                     value={faultNature}
//                     onChange={(e) => setFaultNature(e.target.value)}
//                     required
//                 >
//                     <option value="">-- Choisir la nature --</option>
//                     {faultNatures.map((fn) => (
//                         <option key={fn} value={fn}>
//                             {fn}
//                         </option>
//                     ))}
//                 </select>
//             </label>

//             {/* AUTRES */}
//             {faultNature === "Autres" && (
//                 <label>
//                     Précisez la nature :
//                     <input
//                         type="text"
//                         value={customNature}
//                         onChange={(e) => setCustomNature(e.target.value)}
//                         placeholder="Saisir la nature exacte de la faute"
//                         required
//                     />
//                 </label>
//             )}

//             <label>
//                 Description détaillée :
//                 <textarea
//                     value={description}
//                     onChange={(e) => setDescription(e.target.value)}
//                     placeholder="Expliquez en détail la faute commise..."
//                     required
//                 />
//             </label>

//             <h3 className="form-section-title">Preuves jointes</h3>

//             <label>
//                 Ajout fichiers (PDF / JPG / DOCX) :
//                 <input
//                     type="file"
//                     multiple
//                     accept=".pdf,.jpg,.jpeg,.doc,.docx"
//                     onChange={handleProofUpload}
//                 />
//             </label>

//             <h3 className="form-section-title">Convocation</h3>

//             <label>
//                 Modèle de convocation :
//                 <select
//                     value={convocationModel}
//                     onChange={(e) => setConvocationModel(e.target.value)}
//                     required
//                 >
//                     <option value="">-- Choisir le modèle --</option>
//                     {convocationModels.map((cm) => (
//                         <option key={cm} value={cm}>
//                             {cm}
//                         </option>
//                     ))}
//                 </select>
//             </label>

//             <label>
//                 Date de l’entretien :
//                 <input
//                     type="date"
//                     value={convocationDate}
//                     onChange={(e) => setConvocationDate(e.target.value)}
//                     required
//                 />
//             </label>

//             <label>
//                 Heure de l’entretien :
//                 <input
//                     type="time"
//                     value={convocationTime}
//                     onChange={(e) => setConvocationTime(e.target.value)}
//                     required
//                 />
//             </label>

//             <label>
//                 Lieu :
//                 <input
//                     type="text"
//                     value={convocationPlace}
//                     onChange={(e) => setConvocationPlace(e.target.value)}
//                     placeholder="Ex : Salle RH 02"
//                     required
//                 />
//             </label>

//             <label>
//                 Responsable convoquant :
//                 <input
//                     type="text"
//                     value={convocationManager}
//                     onChange={(e) => setConvocationManager(e.target.value)}
//                     placeholder="Nom du responsable"
//                     required
//                 />
//             </label>

//             {/* BOUTONS */}
//             <div className="form-buttons">
//                 <button type="submit" className="btn-submit">
//                     Créer Dossier
//                 </button>

//                 <button
//                     type="button"
//                     className="btn-cancel"
//                     onClick={handleReset}
//                 >
//                     Annuler
//                 </button>
//             </div>
//         </form>
//     );
// };

// export default DisciplineForm;




// src/pages/DisciplineForm.jsx

import React, { useState, useEffect } from "react";
import "./Discipline.css";

const DisciplineForm = ({ onCreate }) => {
    const [employees, setEmployees] = useState([]);
    const [selectedEmployee, setSelectedEmployee] = useState("");
    const [matricule, setMatricule] = useState("");
    const [poste, setPoste] = useState("");

    const [faultCategory, setFaultCategory] = useState("");
    const [faultNature, setFaultNature] = useState("");
    const [customNature, setCustomNature] = useState("");

    const [description, setDescription] = useState("");

    const [proofs, setProofs] = useState([]);

    const [convocationModel, setConvocationModel] = useState("");
    const [convocationDate, setConvocationDate] = useState("");
    const [convocationTime, setConvocationTime] = useState("");
    const [convocationPlace, setConvocationPlace] = useState("");
    const [convocationManager, setConvocationManager] = useState("");

    // TEMPORY LIST → backend real API
    useEffect(() => {
        setEmployees([
            { id: 1, nom: "Jean Dupont", matricule: "E001", poste: "Développeur Web" },
            { id: 2, nom: "Marie Curie", matricule: "E002", poste: "Responsable RH" },
            { id: 3, nom: "Albert Einstein", matricule: "E003", poste: "Analyste" }
        ]);
    }, []);

    const handleEmployeeChange = (e) => {
        const empId = e.target.value;
        setSelectedEmployee(empId);

        const emp = employees.find((x) => x.id === parseInt(empId));
        if (emp) {
            setMatricule(emp.matricule);
            setPoste(emp.poste);
        }
    };

    const handleProofUpload = (e) => {
        setProofs([...e.target.files]); // store File objects
    };

    // =============================
    //      SUBMIT FORM → BACKEND
    // =============================
    const handleSubmit = async (e) => {
        e.preventDefault();

        // Prepare formData MULTIPART
        const formData = new FormData();

        // MANDRAY FITAKIANA API EXACT
        formData.append("employee_id", selectedEmployee);
        formData.append("fault_category", faultCategory);
        formData.append("fault_nature", faultNature === "Autres" ? customNature : faultNature);
        formData.append("description", description);

        proofs.forEach((file) => formData.append("proofs", file));

        formData.append("convocation_model", convocationModel);
        formData.append("convocation_date", convocationDate);
        formData.append("convocation_time", convocationTime);
        formData.append("convocation_place", convocationPlace);
        formData.append("convocation_manager", convocationManager);

        try {
            const response = await fetch("http://localhost:8000/api/discipline/with-files", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error("Erreur lors de la création");
            }

            const result = await response.json();

            alert("Dossier créé avec succès !");
            onCreate(result);

        } catch (error) {
            console.error("Erreur:", error);
            alert("Erreur lors de l’enregistrement du dossier.");
        }
    };

    return (
        <form className="discipline-form" onSubmit={handleSubmit}>
            <h3 className="form-section-title">Informations Employé</h3>

            <label>
                Employé concerné :
                <select value={selectedEmployee} onChange={handleEmployeeChange} required>
                    <option value="">-- Sélectionner --</option>
                    {employees.map(emp => (
                        <option key={emp.id} value={emp.id}>{emp.nom}</option>
                    ))}
                </select>
            </label>

            <label>
                Matricule :
                <input type="text" value={matricule} readOnly />
            </label>

            <label>
                Poste :
                <input type="text" value={poste} readOnly />
            </label>

            <h3 className="form-section-title">Type de Faute</h3>

            <label>
                Catégorie :
                <select value={faultCategory} onChange={(e) => setFaultCategory(e.target.value)} required>
                    <option value="">-- Choisir --</option>
                    <option value="Mineure">Mineure</option>
                    <option value="Grave">Grave</option>
                    <option value="Lourde">Lourde</option>
                </select>
            </label>

            <label>
                Nature :
                <select value={faultNature} onChange={(e) => setFaultNature(e.target.value)} required>
                    <option value="">-- Choisir --</option>
                    <option value="Retard répété">Retard répété</option>
                    <option value="Absence injustifiée">Absence injustifiée</option>
                    <option value="Manquement aux règles internes">Manquement interne</option>
                    <option value="Insulte / violence">Insulte / violence</option>
                    <option value="Non-respect consignes sécurité">Sécurité</option>
                    <option value="Vol / Fraude">Vol / Fraude</option>
                    <option value="Autres">Autres</option>
                </select>
            </label>

            {faultNature === "Autres" && (
                <label>
                    Précisez :
                    <input type="text" value={customNature} onChange={(e) => setCustomNature(e.target.value)} />
                </label>
            )}

            <label>
                Description :
                <textarea value={description} onChange={(e) => setDescription(e.target.value)} required />
            </label>

            <h3 className="form-section-title">Preuves jointes</h3>

            <label>
                Ajouter fichiers :
                <input type="file" multiple onChange={handleProofUpload} />
            </label>

            <h3 className="form-section-title">Convocation</h3>

            <label>
                Modèle :
                <select value={convocationModel} onChange={(e) => setConvocationModel(e.target.value)} required>
                    <option value="">-- Choisir --</option>
                    <option value="A">Modèle A</option>
                    <option value="B">Modèle B</option>
                    <option value="C">Modèle C</option>
                </select>
            </label>

            <label>
                Date :
                <input type="date" value={convocationDate} onChange={(e) => setConvocationDate(e.target.value)} required />
            </label>

            <label>
                Heure :
                <input type="time" value={convocationTime} onChange={(e) => setConvocationTime(e.target.value)} required />
            </label>

            <label>
                Lieu :
                <input type="text" value={convocationPlace} onChange={(e) => setConvocationPlace(e.target.value)} required />
            </label>

            <label>
                Responsable :
                <input type="text" value={convocationManager} onChange={(e) => setConvocationManager(e.target.value)} required />
            </label>

            <div className="form-buttons">
                <button type="submit" className="btn-submit">Créer Dossier</button>
                <button type="button" className="btn-cancel" onClick={() => onCreate(null)}>Annuler</button>
            </div>
        </form>
    );
};

export default DisciplineForm;
