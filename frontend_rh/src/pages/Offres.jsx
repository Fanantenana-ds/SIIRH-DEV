// src/pages/Offres.jsx
import { useState } from "react";

export default function Offres() {
  const [form, setForm] = useState({
    title: "",
    job_ref: "",
    department: "",
    site: "",
    contract_type: "",
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

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      ...form,
      tech_skills: form.tech_skills.split(",").map((s) => s.trim()),
      soft_skills: form.soft_skills.split(",").map((s) => s.trim()),
      langs_lvl: form.langs_lvl
        .split(",")
        .reduce((acc, item) => {
          const [lang, lvl] = item.split(":");
          if (lang && lvl) acc[lang.trim()] = lvl.trim();
          return acc;
        }, {}),
    };

    const res = await fetch("http://127.0.0.1:8000/api/offres", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      alert("✅ Offre publiée avec succès !");
      setForm({
        title: "",
        job_ref: "",
        department: "",
        site: "",
        contract_type: "",
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
      alert("⚠️ Erreur lors de la publication.");
    }
  };

  return (
    <div className="flex-1 p-8 bg-gray-50 min-h-screen">
      <h2 className="text-2xl font-bold mb-6 text-emerald-800 text-center">
        Publier une nouvelle offre — SIIRH
      </h2>

      <form
        onSubmit={handleSubmit}
        className="bg-white shadow-lg rounded-2xl p-8 grid grid-cols-2 gap-4"
      >
        {/* Section Identification */}
        <h3 className="col-span-2 text-lg font-semibold text-emerald-700">
          Identification du poste
        </h3>
        <input
          name="title"
          value={form.title}
          onChange={handleChange}
          placeholder="Intitulé du poste"
          className="border rounded-xl p-2"
          required
        />
        <input
          name="job_ref"
          value={form.job_ref}
          onChange={handleChange}
          placeholder="Référence (ex: OFF-2025-003)"
          className="border rounded-xl p-2"
        />
        <input
          name="department"
          value={form.department}
          onChange={handleChange}
          placeholder="Département"
          className="border rounded-xl p-2"
        />
        <input
          name="site"
          value={form.site}
          onChange={handleChange}
          placeholder="Localisation"
          className="border rounded-xl p-2"
        />
        <input
          name="contract_type"
          value={form.contract_type}
          onChange={handleChange}
          placeholder="Type de contrat (CDI, CDD, Stage...)"
          className="border rounded-xl p-2"
        />
        <input
          type="date"
          name="creation_date"
          value={form.creation_date}
          onChange={handleChange}
          className="border rounded-xl p-2"
        />

        {/* Section Description */}
        <h3 className="col-span-2 text-lg font-semibold text-emerald-700 mt-4">
          Description de l’offre
        </h3>
        <textarea
          name="mission"
          value={form.mission}
          onChange={handleChange}
          placeholder="Résumé / Mission principale"
          className="border rounded-xl p-2 col-span-2"
        />
        <textarea
          name="activities_public"
          value={form.activities_public}
          onChange={handleChange}
          placeholder="Responsabilités clés"
          className="border rounded-xl p-2 col-span-2"
        />
        <textarea
          name="goals"
          value={form.goals}
          onChange={handleChange}
          placeholder="Objectifs du poste"
          className="border rounded-xl p-2 col-span-2"
        />

        {/* Section Profil recherché */}
        <h3 className="col-span-2 text-lg font-semibold text-emerald-700 mt-4">
          Profil recherché
        </h3>
        <input
          name="education_level"
          value={form.education_level}
          onChange={handleChange}
          placeholder="Niveau d’études requis"
          className="border rounded-xl p-2"
        />
        <input
          type="number"
          name="exp_required_years"
          value={form.exp_required_years}
          onChange={handleChange}
          placeholder="Années d’expérience requises"
          className="border rounded-xl p-2"
        />
        <textarea
          name="tech_skills"
          value={form.tech_skills}
          onChange={handleChange}
          placeholder="Compétences techniques (séparées par des virgules)"
          className="border rounded-xl p-2 col-span-2"
        />
        <textarea
          name="soft_skills"
          value={form.soft_skills}
          onChange={handleChange}
          placeholder="Compétences comportementales (séparées par des virgules)"
          className="border rounded-xl p-2 col-span-2"
        />
        <input
          name="langs_lvl"
          value={form.langs_lvl}
          onChange={handleChange}
          placeholder="Langues et niveaux (ex: Français:Courant, Anglais:Intermédiaire)"
          className="border rounded-xl p-2 col-span-2"
        />

        {/* Section Scoring automatique */}
        <h3 className="col-span-2 text-lg font-semibold text-emerald-700 mt-4">
          Configuration du scoring automatique
        </h3>
        <div className="grid grid-cols-5 gap-2 col-span-2">
          <label className="text-sm text-gray-600">Poids Compétences (%)</label>
          <input
            type="number"
            name="w_skills"
            value={form.w_skills}
            onChange={handleChange}
            className="border rounded-xl p-2"
          />
          <label className="text-sm text-gray-600">Expérience (%)</label>
          <input
            type="number"
            name="w_exp"
            value={form.w_exp}
            onChange={handleChange}
            className="border rounded-xl p-2"
          />
          <label className="text-sm text-gray-600">Études (%)</label>
          <input
            type="number"
            name="w_edu"
            value={form.w_edu}
            onChange={handleChange}
            className="border rounded-xl p-2"
          />
          <label className="text-sm text-gray-600">Projets (%)</label>
          <input
            type="number"
            name="w_proj"
            value={form.w_proj}
            onChange={handleChange}
            className="border rounded-xl p-2"
          />
        </div>
        <input
          type="number"
          name="threshold"
          value={form.threshold}
          onChange={handleChange}
          placeholder="Seuil d’acceptation (score minimal)"
          className="border rounded-xl p-2 col-span-2"
        />

        {/* Section candidature */}
        <h3 className="col-span-2 text-lg font-semibold text-emerald-700 mt-4">
          Informations de candidature
        </h3>
        <input
          type="date"
          name="deadline"
          value={form.deadline}
          onChange={handleChange}
          className="border rounded-xl p-2"
        />
        <input
          name="apply_link"
          value={form.apply_link}
          onChange={handleChange}
          placeholder="Lien de candidature"
          className="border rounded-xl p-2"
        />

        {/* Submit */}
        <button
          type="submit"
          className="col-span-2 bg-emerald-700 text-white py-3 rounded-xl hover:bg-emerald-800 font-semibold"
        >
          Publier l’offre complète
        </button>
      </form>
    </div>
  );
}
