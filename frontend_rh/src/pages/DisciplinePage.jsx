



// // src/pages/DisciplinePage.jsx
// import React, { useState } from "react";
// import DisciplineForm from "./DisciplineForm";
// import DisciplineReport from "./DisciplineReport";
// import DisciplineApproval from "./DisciplineApproval";
// import "./Discipline.css";

// const DisciplinePage = () => {
//     // Dossiers disciplinaires (stock temporaire)
//     const [dossiers, setDossiers] = useState([
//         {
//             id: 1,
//             employe: "Jean Dupont",
//             date: "2025-01-10",
//             statut: "En attente entretien",
//         },
//         {
//             id: 2,
//             employe: "Marie Curie",
//             date: "2025-01-05",
//             statut: "Clos",
//         },
//     ]);

//     const [activeTab, setActiveTab] = useState(null); // Tabs
//     const [showForm, setShowForm] = useState(false); // Pour afficher/masquer formulaire
//     const [selectedDossier, setSelectedDossier] = useState(null); // Farany "Voir"

//     // Handler rehefa tsindriana ilay tab
//     const handleTab = (tab) => {
//         setActiveTab(tab);
//         setShowForm(false);
//         setSelectedDossier(null);
//     };

//     // Handler rehefa tsindry "Créer dossier"
//     const openCreationForm = () => {
//         setShowForm(true);
//         setSelectedDossier(null);
//     };



//     // Handler rehefa vita ny création → ajout automatique anaty liste
//     const handleCreateDossier = (data) => {
//         if (!data) {
//             // Raha tonga eto dia midika hoe tsindry ANNULER
//             setShowForm(false);
//             return;
//         }

//         // Raha tonga eto dia tena création
//         const newDossier = {
//             id: dossiers.length + 1,
//             employe: data.employe,
//             date: new Date().toISOString().split("T")[0],
//             statut: "En cours",
//         };

//         setDossiers([...dossiers, newDossier]);
//         setShowForm(false);
//     };


//     // Handler rehefa tsindry "Voir"
//     const handleView = (dossier) => {
//         setSelectedDossier(dossier);   // mitahiry ilay dossier voafidy
//         setActiveTab("creation");      // alefa amin’ilay tab mifanaraka amin'ny état
//         setShowForm("view");           // show form mode "view"
//     };

//     return (
//         <div className="discipline-container">
//             <h2 className="discipline-title">Module Gestion Disciplinaire</h2>

//             {/* TABS PRINCIPAUX */}
//             <div className="discipline-tabs">
//                 <button
//                     className={activeTab === "creation" ? "active" : ""}
//                     onClick={() => handleTab("creation")}
//                 >
//                     Création Dossier
//                 </button>

//                 <button
//                     className={activeTab === "report" ? "active" : ""}
//                     onClick={() => handleTab("report")}
//                 >
//                     Compte-rendu Entretien
//                 </button>

//                 <button
//                     className={activeTab === "approval" ? "active" : ""}
//                     onClick={() => handleTab("approval")}
//                 >
//                     Approbation
//                 </button>
//             </div>

//             {/* --- CONTENU PRINCIPAL --- */}
//             <div className="discipline-content">
//                 {/* Raha tsy mbola misafidy tab → message accueil */}
//                 {!activeTab && (
//                     <p className="discipline-info">
//                         Veuillez sélectionner une section ci-dessus.
//                     </p>
//                 )}

//                 {/* =========================
//              1. TAB CRÉATION DOSSIER
//            ========================= */}
//                 {activeTab === "creation" && (
//                     <>
//                         <div className="top-actions">
//                             <button className="btn-create" onClick={openCreationForm}>
//                                 + Créer un dossier disciplinaire
//                             </button>
//                         </div>

//                         {/* A. TABLE DES DOSSIERS EXISTANTS */}
//                         <h3 className="section-title">Liste des dossiers disciplinaires</h3>

//                         <table className="discipline-table">
//                             <thead>
//                                 <tr>
//                                     <th>ID</th>
//                                     <th>Employé</th>
//                                     <th>Date de création</th>
//                                     <th>Statut</th>
//                                     <th>Actions</th>
//                                 </tr>
//                             </thead>

//                             <tbody>
//                                 {dossiers.map((d) => (
//                                     <tr key={d.id}>
//                                         <td>{d.id}</td>
//                                         <td>{d.employe}</td>
//                                         <td>{d.date}</td>
//                                         <td>
//                                             <span className={`status status-${d.statut.replace(" ", "-")}`}>
//                                                 {d.statut}
//                                             </span>
//                                         </td>
//                                         <td>
//                                             <button
//                                                 className="btn-view"
//                                                 onClick={() => handleView(d)}
//                                             >
//                                                 Voir
//                                             </button>
//                                         </td>
//                                     </tr>
//                                 ))}
//                             </tbody>
//                         </table>
//                         {showForm === "view" && selectedDossier && (
//                             <div className="fiche-dossier">
//                                 <h3>Dossier disciplinaire #{selectedDossier.id}</h3>

//                                 <p><strong>Employé :</strong> {selectedDossier.employe}</p>
//                                 <p><strong>Date création :</strong> {selectedDossier.date}</p>
//                                 <p><strong>Statut :</strong> {selectedDossier.statut}</p>

//                                 <button className="btn-submit" onClick={() => setShowForm(false)}>
//                                     Fermer
//                                 </button>
//                             </div>
//                         )}


//                         {/* B. FORMULAIRE DE CRÉATION OU VISUALISATION */}
//                         {showForm && (
//                             <div className="form-wrapper">
//                                 <DisciplineForm
//                                     onCreate={handleCreateDossier}
//                                     isEditing={selectedDossier}
//                                     dossier={selectedDossier}
//                                 />
//                             </div>
//                         )}
//                     </>
//                 )}

//                 {/* =========================
//              2. TAB COMPTE-RENDU
//            ========================= */}
//                 {activeTab === "report" && (
//                     <div className="form-wrapper">
//                         <DisciplineReport />
//                     </div>
//                 )}

//                 {/* =========================
//              3. TAB APPROBATION
//            ========================= */}
//                 {activeTab === "approval" && (
//                     <div className="form-wrapper">
//                         <DisciplineApproval />
//                     </div>
//                 )}
//             </div>
//         </div>
//     );
// };

// export default DisciplinePage;



// src/pages/DisciplinePage.jsx

import React, { useState, useEffect } from "react";
import DisciplineForm from "./DisciplineForm";
import DisciplineReport from "./DisciplineReport";
import DisciplineApproval from "./DisciplineApproval";
import "./Discipline.css";

const DisciplinePage = () => {

    // ==============================
    //   LISTE REELLE AVY BACKEND
    // ==============================
    const [dossiers, setDossiers] = useState([]);
    const [activeTab, setActiveTab] = useState(null);
    const [showForm, setShowForm] = useState(false);
    const [selectedDossier, setSelectedDossier] = useState(null);

    // ==============================
    //    GET ALL DISCIPLINES (API)
    // ==============================
    const fetchDossiers = async () => {
        try {
            const res = await fetch("http://localhost:8000/api/discipline");
            const data = await res.json();
            setDossiers(data);
        } catch (err) {
            console.error("Erreur fetch dossiers:", err);
        }
    };

    useEffect(() => {
        fetchDossiers();
    }, []);

    // ==============================
    //      CHOISIR TAB
    // ==============================
    const handleTab = (tab) => {
        setActiveTab(tab);
        setShowForm(false);
        setSelectedDossier(null);
    };

    // ==============================
    //   OUVERTURE FORMULAIRE CREATE
    // ==============================
    const openCreationForm = () => {
        setShowForm(true);
        setSelectedDossier(null);
    };

    // =======================================================
    //      RECEPTION RESULTAT CREATE (APPEL DE DisciplineForm)
    // =======================================================
    const handleCreateDossier = (created) => {
        if (!created) {
            setShowForm(false);
            return;
        }

        // Backend miverina toy izao:
        // {
        //   id: 12,
        //   employee_id: 1,
        //   fault_category: "...",
        //   ...
        // }

        fetchDossiers(); // Refresh auto
        setShowForm(false);
    };

    // ==============================
    //      BOUTON "VOIR"
    // ==============================
    const handleView = (dossier) => {
        setSelectedDossier(dossier);
        setActiveTab("creation");
        setShowForm("view");
    };

    return (
        <div className="discipline-container">
            <h2 className="discipline-title">Module Gestion Disciplinaire</h2>

            {/* ----------------------- */}
            {/*       TABS PRINCIPAUX   */}
            {/* ----------------------- */}
            <div className="discipline-tabs">
                <button
                    className={activeTab === "creation" ? "active" : ""}
                    onClick={() => handleTab("creation")}
                >
                    Création Dossier
                </button>

                <button
                    className={activeTab === "report" ? "active" : ""}
                    onClick={() => handleTab("report")}
                >
                    Compte-rendu Entretien
                </button>

                <button
                    className={activeTab === "approval" ? "active" : ""}
                    onClick={() => handleTab("approval")}
                >
                    Approbation
                </button>
            </div>

            <div className="discipline-content">

                {/* MESSAGE ACCUEIL */}
                {!activeTab && (
                    <p className="discipline-info">
                        Veuillez sélectionner une section ci-dessus.
                    </p>
                )}

                {/* =====================================================
                    1) TAB CRÉATION DES DOSSIERS
                   ===================================================== */}
                {activeTab === "creation" && (
                    <>
                        <div className="top-actions">
                            <button className="btn-create" onClick={openCreationForm}>
                                + Créer un dossier disciplinaire
                            </button>
                        </div>

                        <h3 className="section-title">Liste des dossiers disciplinaires</h3>

                        {/* TABLE LISTE AVY BACKEND */}
                        <table className="discipline-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Employé (ID)</th>
                                    <th>Date convocation</th>
                                    <th>Statut</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>

                            <tbody>
                                {dossiers.map((d) => (
                                    <tr key={d.id}>
                                        <td>{d.id}</td>
                                        <td>{d.employee_id}</td>
                                        <td>{d.convocation_date}</td>
                                        <td>
                                            <span className="status status-En-cours">
                                                En cours
                                            </span>
                                        </td>
                                        <td>
                                            <button
                                                className="btn-view"
                                                onClick={() => handleView(d)}
                                            >
                                                Voir
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        {/* MODE VIEW */}
                        {showForm === "view" && selectedDossier && (
                            <div className="fiche-dossier">
                                <h3>Dossier disciplinaire #{selectedDossier.id}</h3>

                                <p><strong>ID Employé :</strong> {selectedDossier.employee_id}</p>
                                <p><strong>Catégorie :</strong> {selectedDossier.fault_category}</p>
                                <p><strong>Date convocation :</strong> {selectedDossier.convocation_date}</p>

                                <button
                                    className="btn-submit"
                                    onClick={() => setShowForm(false)}
                                >
                                    Fermer
                                </button>
                            </div>
                        )}

                        {/* FORMULAIRE CREATE */}
                        {showForm && showForm !== "view" && (
                            <div className="form-wrapper">
                                <DisciplineForm
                                    onCreate={handleCreateDossier}
                                />
                            </div>
                        )}
                    </>
                )}

                {/* =====================================================
                    2) TAB REPORT ENTRETIEN
                   ===================================================== */}
                {activeTab === "report" && (
                    <div className="form-wrapper">
                        <DisciplineReport />
                    </div>
                )}

                {/* =====================================================
                    3) TAB APPROBATION
                   ===================================================== */}
                {activeTab === "approval" && (
                    <div className="form-wrapper">
                        <DisciplineApproval />
                    </div>
                )}
            </div>
        </div>
    );
};

export default DisciplinePage;
