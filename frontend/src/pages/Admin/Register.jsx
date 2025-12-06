import { useState } from "react";
import api from "../../api/apiClient";

export default function AdminRegister() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: ""
  });

  const register = async () => {
    try {
      await api.post("/admin/auth/register", form);
      alert("Admin Registered Successfully!");
    } catch (err) {
      alert(err.response?.data?.detail || "Registration failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 to-blue-700 px-4">
      <div className="bg-white shadow-2xl rounded-xl p-8 w-full max-w-md">
        
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">
          Register Admin
        </h1>

        {/* Name */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1 text-gray-700">
            Full Name
          </label>
          <input
            className="w-full border rounded-lg p-3 focus:ring-2 focus:ring-green-500"
            placeholder="Enter name"
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
        </div>

        {/* Email */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1 text-gray-700">
            Email Address
          </label>
          <input
            type="email"
            className="w-full border rounded-lg p-3 focus:ring-2 focus:ring-green-500"
            placeholder="Enter email"
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        </div>

        {/* Password */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-1 text-gray-700">
            Password
          </label>
          <input
            type="password"
            className="w-full border rounded-lg p-3 focus:ring-2 focus:ring-green-500"
            placeholder="Create password"
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </div>

        {/* Register Button */}
        <button
          onClick={register}
          className="w-full bg-green-600 text-white py-3 rounded-lg text-lg font-semibold hover:bg-green-700"
        >
          Register
        </button>

        <p className="text-center mt-4 text-sm text-gray-600">
          Already have an account?{" "}
          <a href="/" className="text-blue-600 underline">
            Login
          </a>
        </p>
      </div>
    </div>
  );
}
