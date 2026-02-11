import "./Sidebar.css";
import logo from "../assets/codel_logo1.png";
import { NavLink, useNavigate } from "react-router-dom";
import {
  LogOut, Users, FileSpreadsheet, DollarSign, FileText,
  BarChart3, Calendar, Gavel, BarChart, Settings,
  ClipboardCheck, Briefcase, Mail, Lock, Eye, EyeOff,
  ChevronUp, ChevronDown, User
} from "lucide-react";
import { useRef, useState, useEffect } from "react";

const translations = {
  fr: {
    dashboard: "Tableau de bord",
    payroll: "Paie",
    reports: "Talents & Reporting",
    absences: "Absences & Temps",
    discipline: "Discipline",
    settings: "Paramètres système",
    convocation: "Convocation",
    interview: "Entretien",
    offers: "Offres",
    contrats: "Contrats",
    changePhoto: "Changer la photo",
    update: "Mettre à jour",
    logout: "Se déconnecter",
  },
  en: {
    dashboard: "Dashboard",
    payroll: "Payroll",
    reports: "Reports",
    absences: "Absences & Times",
    discipline: "Discipline",
    settings: "System settings",
    convocation: "Summons",
    interview: "Interview",
    offers: "Offers",
    contrats: "Contracts",
    changePhoto: "Change photo",
    update: "Update",
    logout: "Logout",
  },
};

export default function Sidebar() {
  const navigate = useNavigate();
  const navRef = useRef(null);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [lang, setLang] = useState(localStorage.getItem("lang") || "fr");
  const [user, setUser] = useState(
    JSON.parse(localStorage.getItem("user")) || {
      name: "admin",
      role: "Administrateur",
      photo: localStorage.getItem("photo") || "https://via.placeholder.com/40",
      email: "admin@exemple.com",
    }
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setLang(localStorage.getItem("lang") || "fr");
    }, 500);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  const handleProfileClick = () => setIsProfileOpen(!isProfileOpen);

  const handleAccountChange = (e) => {
    e.preventDefault();
    const updatedUser = { ...user, email, password };
    localStorage.setItem("user", JSON.stringify(updatedUser));
    alert("Profil mis à jour !");
    setEmail("");
    setPassword("");
  };

  const handlePhotoUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        localStorage.setItem("photo", reader.result);
        setUser((prev) => ({ ...prev, photo: reader.result }));
      };
      reader.readAsDataURL(file);
    }
  };

  const navItems = [
    { path: "/rh/dashboard", key: "dashboard", icon: <BarChart3 size={18} /> },
    { path: "/rh/paie", key: "payroll", icon: <DollarSign size={18} /> },
    { path: "/rh/rapports", key: "reports", icon: <FileText size={18} /> },
    { path: "/rh/absences", key: "absences", icon: <Calendar size={18} /> },
    { path: "/rh/discipline", key: "discipline", icon: <Gavel size={18} /> },
    { path: "/rh/parametres", key: "settings", icon: <Settings size={18} /> },
    { path: "/rh/convocation", key: "convocation", icon: <FileText size={18} /> },
    { path: "/rh/entretien", key: "interview", icon: <ClipboardCheck size={18} /> },
    { path: "/rh/offre", key: "offers", icon: <Briefcase size={18} /> },
    { path: "/rh/contrats", key: "contrats", icon: <FileText size={18} /> }, // lien nouveau
  ];

  navItems.sort((a, b) =>
    translations[lang][a.key].localeCompare(translations[lang][b.key])
  );

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <img src={logo} alt="codel_logo1" />
        <h1>SIIRH – RH</h1>
      </div>

      <nav className="sidebar-nav" ref={navRef}>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => (isActive ? "active" : "")}
          >
            {item.icon} {translations[lang][item.key]}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="sidebar-profile" onClick={handleProfileClick}>
          <img src={user.photo} alt="Profil" className="profile-pic" />
          <div className="profile-info">
            <p className="profile-name">{user.name}</p>
            <p className="profile-role">{user.role}</p>
          </div>
          {isProfileOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </div>

        {isProfileOpen && (
          <div className="profile-menu">
            <form onSubmit={handleAccountChange}>
              <div className="photo-upload">
                <label htmlFor="photo-upload">
                  <User size={16} /> {translations[lang].changePhoto}
                </label>
                <input
                  id="photo-upload"
                  type="file"
                  accept="image/*"
                  onChange={handlePhotoUpload}
                />
              </div>

              <div className="input-group">
                <Mail size={16} />
                <input
                  type="email"
                  placeholder="Nouvel e-mail"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div className="input-group">
                <Lock size={16} />
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Nouveau mot de passe"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                {showPassword ? (
                  <EyeOff size={16} onClick={() => setShowPassword(false)} className="eye-icon" />
                ) : (
                  <Eye size={16} onClick={() => setShowPassword(true)} className="eye-icon" />
                )}
              </div>

              <button type="submit" className="btn-update">
                {translations[lang].update}
              </button>
            </form>

            <button onClick={handleLogout} className="btn-logout">
              <LogOut size={16} /> {translations[lang].logout}
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}
