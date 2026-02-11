import { useState, useEffect } from "react";
import {
  getCases,
  getCase,
  createConvocation,
  createDecision
} from "../services/disciplineService";

import DisciplineTable from "../components/DisciplineTable";
import DisciplineDetailModal from "../components/DisciplineDetailModal";
import ConvocationForm from "../components/ConvocationForm";
import DecisionForm from "../components/DecisionForm";

import "../styles/Discipline.css";

export default function Discipline() {
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [showConvocation, setShowConvocation] = useState(false);
  const [showDecision, setShowDecision] = useState(false);

  const fetchCases = async () => {
    const data = await getCases();
    setCases(data);
  };

  useEffect(() => { fetchCases(); }, []);

  const handleView = async (caseItem) => {
    const data = await getCase(caseItem.id);
    setSelectedCase(data);
  };

  const handleConvocation = (caseItem) => {
    setSelectedCase(caseItem);
    setShowConvocation(true);
  };

  const handleDecision = (caseItem) => {
    setSelectedCase(caseItem);
    setShowDecision(true);
  };

  const generateConvocation = async (convData) => {
    const pdfUrl = await createConvocation(selectedCase.id, convData);
    window.open(pdfUrl, "_blank");
    setShowConvocation(false);
    fetchCases();
  };

  const generateDecision = async (decisionData) => {
    const pdfUrl = await createDecision(selectedCase.id, decisionData);
    window.open(pdfUrl, "_blank");
    setShowDecision(false);
    fetchCases();
  };

  return (
    <div className="discipline-page">
      <h1>Discipline – Cas en cours</h1>
      <DisciplineTable
        cases={cases}
        onView={handleView}
        onConvocation={handleConvocation}
        onDecision={handleDecision}
      />

      {selectedCase && (
        <DisciplineDetailModal
          selectedCase={selectedCase}
          onClose={() => setSelectedCase(null)}
          onUpdate={fetchCases}
        />
      )}

      {showConvocation && (
        <ConvocationForm
          caseId={selectedCase.id}
          onGenerate={generateConvocation}
        />
      )}

      {showDecision && (
        <DecisionForm
          caseId={selectedCase.id}
          onGenerate={generateDecision}
        />
      )}
    </div>
  );
}
