


// src/App.jsx

import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { SystemProvider } from "./context/SystemContext";

import DashboardLayout from "./pages/RHDashboardLayout";
import RHDashboard from "./pages/RHDashboard";
import Employes from "./pages/Employes";
import Contrats from "./pages/Contrats";
import Paie from "./pages/Paie";
import Rapports from "./pages/Rapports";
import EntretienForm from "./pages/EntretienForm";
import ListeEntretiens from "./pages/ListeEntretiens";
import ConvocationPage from "./pages/ConvocationPage";
import OffreForm from "./pages/OffreForm";
import Parametres from "./pages/Parametres";
import Absences from "./pages/Absences";
import DisciplinePage from "./pages/DisciplinePage";

import Login from "./pages/Login";
import ResetPassword from "./pages/ResetPassword";
import CandidatDashboard from "./pages/CandidatDashboard";

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("token");
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function App() {
  const token = localStorage.getItem("token");

  return (
    <SystemProvider>
      <Router>
        <Routes>
          {/* === Auth / ResetPassword === */}
          <Route path="/login" element={<Login />} />
          <Route path="/reset-password" element={<ResetPassword />} />

          {/* === Routes RH === */}
          <Route
            path="/rh/*"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route path="dashboard" element={<RHDashboard />} />
            <Route path="employes" element={<Employes />} />
            <Route path="contrats" element={<Contrats />} />
            <Route path="paie" element={<Paie />} />
            <Route path="Rapports" element={<Rapports />} />
            <Route path="absences" element={<Absences />} />
            <Route path="entretien" element={<EntretienForm />} />
            <Route path="liste-entretiens" element={<ListeEntretiens />} />
            <Route path="convocation" element={<ConvocationPage />} />
            <Route path="offre" element={<OffreForm />} />
            <Route path="parametres" element={<Parametres />} />
            <Route path="discipline" element={<DisciplinePage />} />
          </Route>

          {/* === Routes Candidat === */}
          <Route
            path="/candidat/*"
            element={
              <ProtectedRoute>
                <CandidatDashboard />
              </ProtectedRoute>
            }
          />

          {/* === Catch-all === */}
          <Route
            path="*"
            element={<Navigate to={token ? "/rh/dashboard" : "/login"} replace />}
          />
        </Routes>
      </Router>
    </SystemProvider>
  );
}

export default App;
