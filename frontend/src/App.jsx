import { BrowserRouter, Routes, Route } from "react-router-dom";
import AdminLogin from "./pages/Admin/Login";
import AdminRegister from "./pages/Admin/Register";
import AdminDashboard from "./pages/Admin/Dashboard";
import AdminProtectedRoute from "./components/AdminProtectedRoute";
import PanUpload from "./pages/Onboarding/PanUpload";
import CustomerOnboarding from "./pages/Customer/CustomerOnboarding";


export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AdminLogin />} />
        <Route path="/admin/register" element={<AdminRegister />} />

        <Route
          path="/admin/dashboard"
          element={
            <AdminProtectedRoute>
              <AdminDashboard />
            </AdminProtectedRoute>
          }
        />

         {/* Onboarding – for now accessible directly.
            Later we can add link from Dashboard. */}
        <Route
          path="/onboarding/pan"
          element={
            <AdminProtectedRoute>
              <PanUpload />
            </AdminProtectedRoute>
          }
        />  

        <Route
  path="/customer/onboarding"
  element={
    <AdminProtectedRoute>
      <CustomerOnboarding />
    </AdminProtectedRoute>
  }
/>

      </Routes>
    </BrowserRouter>
  );
}
