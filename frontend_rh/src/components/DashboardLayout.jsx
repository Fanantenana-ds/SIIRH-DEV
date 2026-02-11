import { LogOut, Users, FileText, DollarSign, FileSpreadsheet } from "lucide-react";

export default function DashboardLayout({ children }) {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-blue-800 text-white flex flex-col">
        <div className="flex items-center justify-center h-16 border-b border-blue-700">
          <img src="/codel_logo1" alt="SIIRH Logo" className="h-10 w-10 mr-2" />
          <h1 className="text-xl font-bold">SIIRH - RH</h1>
        </div>
        <nav className="flex-1 px-4 py-6 space-y-3">
          <a href="/rh/dashboard" className="flex items-center gap-2 hover:bg-blue-700 p-2 rounded">
            <Users size={18}/> Tableau de bord
          </a>
          <a href="/rh/employes" className="flex items-center gap-2 hover:bg-blue-700 p-2 rounded">
            <FileText size={18}/> Employés
          </a>
          <a href="/rh/contrats" className="flex items-center gap-2 hover:bg-blue-700 p-2 rounded">
            <FileSpreadsheet size={18}/> Contrats
          </a>
          <a href="/rh/paie" className="flex items-center gap-2 hover:bg-blue-700 p-2 rounded">
            <DollarSign size={18}/> Paie
          </a>
          <a href="/rh/rapports" className="flex items-center gap-2 hover:bg-blue-700 p-2 rounded">
            <FileText size={18}/> Rapports
          </a>
        </nav>

        {/* Logout */}
        <button className="flex items-center gap-2 p-4 bg-blue-700 hover:bg-blue-600">
          <LogOut size={18}/> Déconnexion
        </button>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-6">{children}</main>
    </div>
  );
}
