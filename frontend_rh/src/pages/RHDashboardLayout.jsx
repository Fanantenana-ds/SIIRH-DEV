// import React, { useEffect, useState } from "react";
// import { Outlet } from "react-router-dom";
// import Sidebar from "../components/Sidebar";
// import { FaRobot, FaBell } from "react-icons/fa"; // Icône robot + cloche
// import "./RHDashboardlayout.css";

// const DashboardLayout = () => {
//   const [darkMode, setDarkMode] = useState(localStorage.getItem("theme") === "dark");
//   const [lang, setLang] = useState(localStorage.getItem("lang") || "fr");
//   const [notifications, setNotifications] = useState([]);
//   const [showNotif, setShowNotif] = useState(false);
//   const [enAttenteCount, setEnAttenteCount] = useState(0);

//   // Gestion thème
//   useEffect(() => {
//     document.body.classList.toggle("dark-mode", darkMode);
//     localStorage.setItem("theme", darkMode ? "dark" : "light");
//   }, [darkMode]);

//   useEffect(() => {
//     localStorage.setItem("lang", lang);
//   }, [lang]);

//   const handleLangChange = (e) => setLang(e.target.value);
//   const handleThemeToggle = () => setDarkMode((prev) => !prev);
//   const toggleNotif = () => setShowNotif((prev) => !prev);

//   // --- Fetch notifications ---
//   const fetchNotifications = async () => {
//     try {
//       const res = await fetch("http://127.0.0.1:8000/rh/notifications");
//       if (res.ok) {
//         const data = await res.json();
//         setNotifications(data);
//       }
//     } catch (err) {
//       console.error(err);
//     }
//   };

//   useEffect(() => {
//     fetchNotifications();
//     const interval = setInterval(fetchNotifications, 30000); // refresh automatique
//     return () => clearInterval(interval);
//   }, []);

//   // --- Polling pour candidatures "En attente" ---
//   useEffect(() => {
//     const fetchEnAttente = async () => {
//       try {
//         const res = await fetch("http://127.0.0.1:8000/rh/candidatures");
//         if (res.ok) {
//           const data = await res.json();
//           const count = data.filter(c => c.statut === "En attente").length;
//           setEnAttenteCount(count);
//         }
//       } catch (err) {
//         console.error(err);
//       }
//     };

//     fetchEnAttente();
//     const interval = setInterval(fetchEnAttente, 5000);
//     return () => clearInterval(interval);
//   }, []);

//   // --- Marquer notification comme read ---
//   const markAsRead = async (id) => {
//     try {
//       await fetch(`http://127.0.0.1:8000/rh/notifications/${id}/read`, { method: "PUT" });
//       setNotifications((prev) =>
//         prev.map((n) => (n.id === id ? { ...n, read: true } : n))
//       );
//     } catch (err) {
//       console.error(err);
//     }
//   };

//   const unreadCount = notifications.filter(n => !n.read).length;

//   return (
//     <div className={`main-layout ${darkMode ? "dark" : ""}`}>
//       {/* Sidebar */}
//       <Sidebar />

//       <div className="dashboard-wrapper">
//         {/* Topbar */}
//         <div className="dashboard-topbar">
//           <FaRobot className="dashboard-icon" />

//           <h1 className="dashboard-title">
//             Système d’Information Intelligent des <br /> Ressources Humaines
//           </h1>

//           <div className="dashboard-controls">
//             {/* Cloche notifications */}
//             <div className="notification-bell" onClick={toggleNotif}>
//               <FaBell size={20} />
//               {unreadCount > 0 && <span className="notification-count">{unreadCount}</span>}
//             </div>

//             {showNotif && (
//               <div className="notification-dropdown">
//                 {notifications.length === 0 ? (
//                   <p className="no-notifications">Aucune notification</p>
//                 ) : (
//                   notifications.map((n) => (
//                     <div
//                       key={n.id}
//                       className={`notification-item ${n.read ? "" : "unread"}`}
//                       onClick={() => markAsRead(n.id)}
//                     >
//                       <div className="message">{n.message}</div>
//                       <small className="date">{new Date(n.date).toLocaleString()}</small>
//                     </div>
//                   ))
//                 )}
//               </div>
//             )}

//             {/* Sélecteur langue */}
//             <select value={lang} onChange={handleLangChange} className="lang-select">
//               <option value="fr">Français</option>
//               <option value="en">English</option>
//             </select>

//             <button
//               onClick={handleThemeToggle}
//               className="theme-toggle"
//               aria-label="Changer de mode"
//             >
//               {darkMode ? "🌙" : "☀️"}
//             </button>
//           </div>
//         </div>

//         {/* Contenu dynamique */}
//         <div className="dashboard-content">
//           <Outlet />
//         </div>
//       </div>
//     </div>
//   );
// };

// export default DashboardLayout;







import React, { useEffect, useState, useRef } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { FaRobot, FaBell } from "react-icons/fa";
import "./RHDashboardlayout.css";

const DashboardLayout = () => {
  const [darkMode, setDarkMode] = useState(localStorage.getItem("theme") === "dark");
  const [lang, setLang] = useState(localStorage.getItem("lang") || "fr");
  const [notifications, setNotifications] = useState([]);
  const [showNotif, setShowNotif] = useState(false);
  const [enAttenteCount, setEnAttenteCount] = useState(0);

  const notifRef = useRef(null); // Ref ho an'ny dropdown

  // --- Gestion thème ---
  useEffect(() => {
    document.body.classList.toggle("dark-mode", darkMode);
    localStorage.setItem("theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  useEffect(() => {
    localStorage.setItem("lang", lang);
  }, [lang]);

  const handleLangChange = (e) => setLang(e.target.value);
  const handleThemeToggle = () => setDarkMode((prev) => !prev);
  const toggleNotif = () => setShowNotif((prev) => !prev);

  // --- Fetch notifications ---
  const fetchNotifications = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/rh/notifications");
      if (res.ok) {
        const data = await res.json();
        setNotifications(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000); // refresh automatique
    return () => clearInterval(interval);
  }, []);

  // --- Polling pour candidatures "En attente" ---
  useEffect(() => {
    const fetchEnAttente = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/rh/candidatures");
        if (res.ok) {
          const data = await res.json();
          const count = data.filter(c => c.statut === "En attente").length;
          setEnAttenteCount(count);
        }
      } catch (err) {
        console.error(err);
      }
    };

    fetchEnAttente();
    const interval = setInterval(fetchEnAttente, 5000);
    return () => clearInterval(interval);
  }, []);

  // --- Marquer notification comme read ---
  const markAsRead = async (id) => {
    try {
      await fetch(`http://127.0.0.1:8000/rh/notifications/${id}/read`, { method: "PUT" });
      // Havaozina eo an-toerana ny state
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, read: true } : n))
      );
    } catch (err) {
      console.error(err);
    }
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  // --- Click outside dropdown ---
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (notifRef.current && !notifRef.current.contains(event.target)) {
        setShowNotif(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className={`main-layout ${darkMode ? "dark" : ""}`}>
      {/* Sidebar */}
      <Sidebar />

      <div className="dashboard-wrapper">
        {/* Topbar */}
        <div className="dashboard-topbar">
          <FaRobot className="dashboard-icon" />

          <h1 className="dashboard-title">
            Système d’Information Intelligent des <br /> Ressources Humaines
          </h1>

          <div className="dashboard-controls">
            {/* Cloche notifications */}
            <div className="notification-bell" onClick={toggleNotif}>
              <FaBell size={20} />
              {unreadCount > 0 && <span className="notification-count">{unreadCount}</span>}
            </div>

            {/* Dropdown notifications */}
            {showNotif && (
              <div className="notification-dropdown" ref={notifRef}>
                {notifications.length === 0 ? (
                  <p className="no-notifications">Aucune notification</p>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      className={`notification-item ${n.read ? "" : "unread"}`}
                      onClick={() => markAsRead(n.id)}
                    >
                      <div className="message">{n.message}</div>
                      <small className="date">{new Date(n.date).toLocaleString()}</small>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Sélecteur langue */}
            <select value={lang} onChange={handleLangChange} className="lang-select">
              <option value="fr">Français</option>
              <option value="en">English</option>
            </select>

            <button
              onClick={handleThemeToggle}
              className="theme-toggle"
              aria-label="Changer de mode"
            >
              {darkMode ? "🌙" : "☀️"}
            </button>
          </div>
        </div>

        {/* Contenu dynamique */}
        <div className="dashboard-content">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default DashboardLayout;
