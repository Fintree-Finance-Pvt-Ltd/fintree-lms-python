import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/apiClient";

export default function AdminLogin() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: ""
  });

  const login = async () => {
    try {
      const res = await api.post("/admin/auth/login", form);
      localStorage.setItem("adminToken", res.data.token);
      navigate("/admin/dashboard");
    } catch (err) {
      alert(err.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-700 px-4">
      <div className="bg-white shadow-2xl rounded-xl p-8 w-full max-w-md">
        
        <h1 className="text-3xl font-bold text-center text-slate-800 mb-6">
          Admin Login
        </h1>

        {/* Email */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email Address
          </label>
          <input
            type="email"
            className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500"
            placeholder="admin@example.com"
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        </div>

        {/* Password */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Password
          </label>
          <input
            type="password"
            className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your password"
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </div>

        {/* Button */}
        <button
          onClick={login}
          className="w-full bg-blue-600 text-white py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-all"
        >
          Login
        </button>

        <p className="text-center mt-4 text-sm text-gray-600">
          Don’t have an account?{" "}
          <a
            href="/admin/register"
            className="text-blue-600 font-semibold underline"
          >
            Register
          </a>
        </p>
      </div>
    </div>
  );
}
