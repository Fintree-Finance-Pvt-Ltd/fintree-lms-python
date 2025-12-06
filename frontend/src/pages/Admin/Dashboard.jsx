import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/apiClient";

export default function AdminDashboard() {
  const [admin, setAdmin] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.get("/admin/auth/me")
      .then((res) => setAdmin(res.data.admin))
      .catch(() => {
        localStorage.removeItem("adminToken");
        navigate("/");
      });
  }, []);

  const logout = () => {
    localStorage.removeItem("adminToken");
    navigate("/");
  };

  return (
    <div className="flex min-h-screen bg-gray-100">

      {/* SIDEBAR */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        <h2 className="text-xl font-bold p-5 border-b border-slate-700">
          Fintree Admin
        </h2>

        <nav className="flex-1 p-4 space-y-2">
          <button className="w-full text-left px-3 py-2 rounded hover:bg-slate-800">
            Dashboard
          </button>
          <button
            onClick={() => navigate("/customer/onboarding")}
            className="w-full text-left px-3 py-2 rounded hover:bg-slate-800"
          >
            Customer
          </button>
          <button className="w-full text-left px-3 py-2 rounded hover:bg-slate-800">
            Loans
          </button>
          <button className="w-full text-left px-3 py-2 rounded hover:bg-slate-800">
            Collections
          </button>
        </nav>

        <button
          onClick={logout}
          className="m-4 py-2 rounded bg-red-500 hover:bg-red-600"
        >
          Logout
        </button>
      </aside>

      {/* MAIN */}
      <main className="flex-1">

        {/* TOPBAR */}
        <header className="h-16 bg-white shadow flex items-center justify-between px-6">
          <h1 className="text-xl font-semibold">Dashboard</h1>
          {admin && (
            <div className="text-sm text-gray-600">
              {admin.name}{" "}
              <span className="px-2 py-1 ml-2 bg-gray-200 rounded text-xs">
                {admin.role}
              </span>
            </div>
          )}
        </header>

        {/* CONTENT */}
        <section className="p-6 grid grid-cols-1 md:grid-cols-3 gap-4">

          {/* Card 1 */}
          <div className="bg-white rounded-xl shadow p-6">
            <p className="text-gray-500 text-sm">Total Customers</p>
            <p className="text-3xl font-bold text-slate-900 mt-2">0</p>
          </div>

          {/* Card 2 */}
          <div className="bg-white rounded-xl shadow p-6">
            <p className="text-gray-500 text-sm">Active Loans</p>
            <p className="text-3xl font-bold text-slate-900 mt-2">0</p>
          </div>

          {/* Card 3 */}
          <div className="bg-white rounded-xl shadow p-6">
            <p className="text-gray-500 text-sm">Total Disbursed</p>
            <p className="text-3xl font-bold text-green-600 mt-2">₹0</p>
          </div>
        </section>

      </main>
    </div>
  );
}
