// frontend_rh/src/pages/OffreForm.jsx

import { useState, useEffect } from "react";
import jsPDF from "jspdf";
import logo from "../assets/codel_logo1.png";
import "../styles/OffreForm.css";

export default function OffreForm() {
  const [form, setForm] = useState({
    title: "",
    department: "",
    site: "",
    contract_type: "CDI",
    creation_date: "",
    mission: "",
    activities_public: "",
    goals: "",
    education_level: "",
    exp_required_years: "",
    tech_skills: "",
    soft_skills: "",
    langs_lvl: "",
    w_skills: 0.4,
    w_exp: 0.3,
    w_edu: 0.2,
    w_proj: 0.1,
    threshold: 60,
    scoring_config_path: "/configs/scoring_default.json",
    deadline: "",
    apply_link: "",
  });

  const [jobRef, setJobRef] = useState(null);
  const [generatedText, setGeneratedText] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [offres, setOffres] = useState([]);
  const [filterPost, setFilterPost] = useState("");

  // --- Fetch offres depuis le backend ---
  const fetchOffres = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/offres");
      if (res.ok) {
        const data = await res.json();
        setOffres(
          data.map((o) => ({
            reference: o.job_ref,
            title: o.title,
            post: o.department,
            creation_date: o.creation_date,
            deadline: o.deadline,
          }))
        );
      }
    } catch (err) {
      console.error("Erreur fetch offres:", err);
    }
  };

  useEffect(() => {
    fetchOffres();
  }, []);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setForm({ ...form, [name]: type === "number" ? parseFloat(value) : value });
  };

  const handleGenerate = (ref = jobRef) => {
    const refText = ref ? ref : "En attente de publication dans le backend";
    const text = `
Offre d’emploi : ${form.title || "{TITLE}"}
Référence : ${refText}
Département / Service : ${form.department || "{DEPARTMENT}"}
Lieu : ${form.site || "{SITE}"}
Type de contrat : ${form.contract_type}
Date de création : ${form.creation_date || "{CREATION_DATE}"}

Description du poste :
${form.mission || "Description non fournie."}

Responsabilités principales :
${form.activities_public || "Responsabilités non fournies."}

Objectifs du poste :
${form.goals || "Objectifs non fournis."}

Profil recherché :
Éducation : ${form.education_level || "Niveau non spécifié"}
Expérience : ${form.exp_required_years || "0"} ans minimum
Compétences techniques : ${form.tech_skills || "Non spécifié"}
Compétences comportementales : ${form.soft_skills || "Non spécifié"}
Langues : ${form.langs_lvl || "Non spécifié"}

Candidature :
Date limite : ${form.deadline || "—"}
Lien pour postuler : ${form.apply_link || "—"}
`;
    setGeneratedText(text);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      tech_skills: form.tech_skills
        ? form.tech_skills.split(",").map((s) => s.trim()).filter(Boolean)
        : [],
      soft_skills: form.soft_skills
        ? form.soft_skills.split(",").map((s) => s.trim()).filter(Boolean)
        : [],
      langs_lvl: form.langs_lvl
        ? form.langs_lvl.split(",").reduce((acc, item) => {
          if (item.includes(":")) {
            const [lang, lvl] = item.split(":");
            acc[lang.trim()] = lvl.trim();
          }
          return acc;
        }, {})
        : {},
    };

    try {
      const res = await fetch("http://127.0.0.1:8000/api/offres", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        setJobRef(data.job_ref);
        handleGenerate(data.job_ref);

        alert("Offre publiée ! Référence : " + data.job_ref);

        // Mise à jour liste avec backend fetch
        fetchOffres();

        setShowForm(false);
        setForm({
          title: "",
          department: "",
          site: "",
          contract_type: "CDI",
          creation_date: "",
          mission: "",
          activities_public: "",
          goals: "",
          education_level: "",
          exp_required_years: "",
          tech_skills: "",
          soft_skills: "",
          langs_lvl: "",
          w_skills: 0.4,
          w_exp: 0.3,
          w_edu: 0.2,
          w_proj: 0.1,
          threshold: 60,
          scoring_config_path: "/configs/scoring_default.json",
          deadline: "",
          apply_link: "",
        });
      } else {
        const err = await res.json();
        alert("Erreur validation : " + JSON.stringify(err.detail));
      }
    } catch (error) {
      alert("Erreur réseau : " + error.message);
    }
  };

  const handleExportPDF = () => {
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    let y = 20;

    doc.addImage(logo, "PNG", (pageWidth - 60) / 2, 10, 60, 15);
    y += 25;

    doc.setFontSize(16);
    doc.text("OFFRE D'EMPLOI SIIRH", pageWidth / 2, y, { align: "center" });
    y += 12;

    doc.setFontSize(12);
    generatedText.split("\n").forEach((line) => {
      const splitLines = doc.splitTextToSize(line, pageWidth - 30);
      splitLines.forEach((sline) => {
        if (y > 270) {
          doc.addPage();
          y = 20;
        }
        doc.text(sline, 15, y);
        y += 7;
      });
    });

    y += 20;
    doc.text("Signature / Cachet: _________________________", 15, y + 10);
    doc.save("offre_SIIRH.pdf");
  };

  return (
    <div className="min-h-screen p-8 offre-form-container bg-gray-50">
      <h2 className="mb-6 text-2xl font-bold text-center text-emerald-800">
        Publier une nouvelle offre — SIIRH
      </h2>

      {/* Bouton Créer/Cacher */}
      <button
        onClick={() => setShowForm(!showForm)}
        className="px-4 py-2 mb-4 text-white bg-blue-600 rounded-xl hover:bg-blue-700"
      >
        {showForm ? "Cacher le formulaire" : "Créer une offre"}
      </button>

      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        {/* --- Formulaire scrollable --- */}
        {showForm && (
          <form
            onSubmit={handleSubmit}
            className="bg-white shadow-lg rounded-2xl p-6 overflow-y-auto max-h-[85vh]"
          >
            {/* Identification du poste */}
            <h3 className="text-lg font-semibold text-emerald-700">
              Identification du poste
            </h3>
            <input
              name="title"
              value={form.title}
              onChange={handleChange}
              placeholder="Intitulé du poste"
              className="w-full p-2 mb-2 border rounded-xl"
              required
            />
            <input
              name="department"
              value={form.department}
              onChange={handleChange}
              placeholder="Département"
              className="w-full p-2 mb-2 border rounded-xl"
            />
            <input
              name="site"
              value={form.site}
              onChange={handleChange}
              placeholder="Localisation"
              className="w-full p-2 mb-2 border rounded-xl"
            />
            <select
              name="contract_type"
              value={form.contract_type}
              onChange={handleChange}
              className="w-full p-2 mb-2 border rounded-xl"
            >
              <option value="CDI">CDI</option>
              <option value="CDD">CDD</option>
              <option value="Stage">Stage</option>
              <option value="Freelance">Freelance</option>
            </select>
            <input
              type="date"
              name="creation_date"
              value={form.creation_date}
              onChange={handleChange}
              className="w-full p-2 mb-2 border rounded-xl"
            />

            {/* Description de l’offre */}
            <h3 className="mt-4 text-lg font-semibold text-emerald-700">
              Description de l’offre
            </h3>
            <textarea
              name="mission"
              value={form.mission}
              onChange={handleChange}
              placeholder="Résumé / Mission principale"
              className="w-full p-2 mb-2 border rounded-xl"
            />
            <textarea
              name="activities_public"
              value={form.activities_public}
              onChange={handleChange}
              placeholder="Responsabilités clés"
              className="w-full p-2 mb-2 border rounded-xl"
            />
            <textarea
              name="goals"
              value={form.goals}
              onChange={handleChange}
              placeholder="Objectifs du poste"
              className="w-full p-2 mb-2 border rounded-xl"
            />

            {/* Profil recherché */}
            <h3 className="mt-4 text-lg font-semibold text-emerald-700">
              Profil recherché
            </h3>
            <input
              name="education_level"
              value={form.education_level}
              onChange={handleChange}
              placeholder="Niveau d’études requis"
              className="w-full p-2 mb-2 border rounded-xl"
            />
            <input
              type="number"
              name="exp_required_years"
              value={form.exp_required_years}
              onChange={handleChange}
              placeholder="Années d’expérience"
              className="w-full p-2 mb-2 border rounded-xl"
            />
            <textarea
              name="tech_skills"
              value={form.tech_skills}
              onChange={handleChange}
              placeholder="Compétences techniques (séparées par des virgules)"
              className="w-full p-2 mb-2 border rounded-xl"
            />
            <textarea
              name="soft_skills"
              value={form.soft_skills}
              onChange={handleChange}
              placeholder="Compétences comportementales"
              className="w-full p-2 mb-2 border rounded-xl"
            />
            <input
              name="langs_lvl"
              value={form.langs_lvl}
              onChange={handleChange}
              placeholder="Langues et niveaux (ex: Français:Courant, Anglais:Intermédiaire)"
              className="w-full p-2 mb-2 border rounded-xl"
            />

            {/* Configuration du scoring automatique */}
            <h3 className="mt-4 text-lg font-semibold text-emerald-700">
              Configuration du scoring automatique
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {["w_skills", "w_exp", "w_edu", "w_proj"].map((field) => (
                <div key={field}>
                  <label className="font-medium">
                    {field.replace("w_", " ")}: {Math.round(form[field] * 100)}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    name={field}
                    value={form[field]}
                    onChange={handleChange}
                    className="w-full"
                  />
                </div>
              ))}
              <div className="col-span-2">
                <label className="font-medium">Seuil d’acceptation: {form.threshold}</label>
                <input
                  type="number"
                  name="threshold"
                  value={form.threshold}
                  onChange={handleChange}
                  className="w-full p-2 border rounded-xl"
                />
              </div>
            </div>

            {/* Informations de candidature */}
            <h3 className="mt-4 text-lg font-semibold text-emerald-700">
              Informations de candidature
            </h3>
            <input
              type="date"
              name="deadline"
              value={form.deadline}
              onChange={handleChange}
              className="w-full p-2 mb-2 border rounded-xl"
            />
            <input
              name="apply_link"
              value={form.apply_link}
              onChange={handleChange}
              placeholder="Lien de candidature"
              className="w-full p-2 mb-2 border rounded-xl"
            />

            <div className="flex gap-2 mt-4">
              <button type="button" onClick={handleGenerate} className="px-4 py-2 text-white bg-blue-600 rounded-xl hover:bg-blue-700">
                Générer l’offre
              </button>
              <button type="submit" className="px-4 py-2 text-white bg-emerald-700 rounded-xl hover:bg-emerald-800">
                Publier l’offre
              </button>
              <button type="button" onClick={handleExportPDF} className="px-4 py-2 text-white bg-gray-700 rounded-xl hover:bg-gray-800">
                Exporter PDF
              </button>
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 ml-auto text-white bg-red-600 rounded-xl hover:bg-red-700">
                Annuler
              </button>
            </div>

            {generatedText && (
              <textarea readOnly value={generatedText} className="w-full p-2 mt-4 border rounded-xl h-60" />
            )}
          </form>
        )}

        {/* --- Tableau des offres --- */}
        <div className="bg-white shadow-lg rounded-2xl p-4 overflow-x-auto max-h-[85vh]">
          <input
            placeholder="Filtrer par poste"
            value={filterPost}
            onChange={(e) => setFilterPost(e.target.value)}
            className="w-full p-2 mb-2 border rounded-xl"
          />

          <h3 className="mb-2 text-xl font-bold text-emerald-800">Liste des offres</h3>

          <table className="min-w-full bg-white">
            <thead>
              <tr className="text-white bg-emerald-700">
                <th className="p-2">Référence</th>
                <th className="p-2">Titre</th>
                <th className="p-2">Poste</th>
                <th className="p-2">Date création</th>
                <th className="p-2">Date clôture</th>
              </tr>
            </thead>
            <tbody>
              {offres
                .filter((o) =>
                  (o.post || "").toLowerCase().includes(filterPost.toLowerCase())
                )
                .sort((a, b) => (a.reference > b.reference ? 1 : -1))
                .map((o, i) => (
                  <tr key={i} className="border-b">
                    <td className="p-2">{o.reference}</td>
                    <td className="p-2">{o.title}</td>
                    <td className="p-2">{o.post}</td>
                    <td className="p-2">{o.creation_date}</td>
                    <td className="p-2">{o.deadline}</td>
                  </tr>
                ))}
            </tbody>

          </table>
        </div>
      </div>
    </div>
  );
}
