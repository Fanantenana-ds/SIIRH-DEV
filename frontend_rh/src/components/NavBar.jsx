import React from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token_rh");

  const logout = () => {
    localStorage.removeItem("token_rh");
    navigate("/");
  };

  return (
    <nav className="navbar">
      <Link to="/dashboard" className="nav-logo">SIIRH - RH</Link>
      <div>
        {token ? (
          <>
            <Link to="/candidats">Candidats</Link>
            <Link to="/contrats">Contrats</Link>
            <Link to="/paie">Paie</Link>
            <Link to="/rapports">Rapports</Link>
            <button onClick={logout}>Déconnexion</button>
          </>
        ) : (
          <></>
        )}
      </div>
    </nav>
  );
}
