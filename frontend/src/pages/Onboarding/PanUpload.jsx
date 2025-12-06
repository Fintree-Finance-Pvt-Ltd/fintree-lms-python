import { useState } from "react";
import api from "../../api/apiClient";

export default function PanUpload() {
  const [panImage, setPanImage] = useState(null);
  const [form, setForm] = useState({
    mobile: "",
    email: "",
    address_line1: "",
    city: "",
    state: "",
    pincode: "",
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!panImage) {
      alert("Please upload PAN image");
      return;
    }

    const fd = new FormData();
    fd.append("pan_image", panImage);
    Object.entries(form).forEach(([key, val]) => {
      fd.append(key, val);
    });

    try {
      setLoading(true);
      const res = await api.post("/onboarding/pan-upload", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Failed to start onboarding");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex justify-center items-center px-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-3xl grid md:grid-cols-2 gap-8">
        {/* Left: Form */}
        <div>
          <h2 className="text-2xl font-bold text-slate-800 mb-2">
            Customer Onboarding
          </h2>
          <p className="text-sm text-slate-500 mb-4">
            Upload customer PAN image and basic details. We will run OCR and
            auto-read the PAN information.
          </p>

          <label className="block text-sm font-medium mb-1">
            PAN Image
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setPanImage(e.target.files?.[0] || null)}
            className="w-full border border-gray-300 rounded-lg p-2 mb-4 text-sm"
          />

          <div className="grid grid-cols-1 gap-3">
            <input
              className="border rounded-lg p-2 text-sm"
              placeholder="Mobile Number"
              onChange={(e) =>
                setForm({ ...form, mobile: e.target.value })
              }
            />
            <input
              className="border rounded-lg p-2 text-sm"
              placeholder="Email"
              onChange={(e) =>
                setForm({ ...form, email: e.target.value })
              }
            />
            <input
              className="border rounded-lg p-2 text-sm"
              placeholder="Address Line 1"
              onChange={(e) =>
                setForm({ ...form, address_line1: e.target.value })
              }
            />
            <div className="grid grid-cols-2 gap-2">
              <input
                className="border rounded-lg p-2 text-sm"
                placeholder="City"
                onChange={(e) =>
                  setForm({ ...form, city: e.target.value })
                }
              />
              <input
                className="border rounded-lg p-2 text-sm"
                placeholder="State"
                onChange={(e) =>
                  setForm({ ...form, state: e.target.value })
                }
              />
            </div>
            <input
              className="border rounded-lg p-2 text-sm"
              placeholder="Pincode"
              onChange={(e) =>
                setForm({ ...form, pincode: e.target.value })
              }
            />
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="mt-4 w-full bg-blue-600 text-white py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 disabled:opacity-60"
          >
            {loading ? "Processing..." : "Start Onboarding"}
          </button>
        </div>

        {/* Right: OCR Result / Auto-fill */}
        <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
          <h3 className="text-lg font-semibold text-slate-800 mb-3">
            PAN OCR Result
          </h3>

          {!result && (
            <p className="text-sm text-slate-500">
              After uploading PAN and submitting, extracted PAN details will
              appear here (PAN number, name, DOB, customer ID).
            </p>
          )}

          {result && (
            <div className="space-y-2 text-sm">
              <p>
                <span className="font-medium">Customer ID:</span>{" "}
                {result.customer_id}
              </p>
              <p>
                <span className="font-medium">PAN:</span>{" "}
                {result.pan_details.pan}
              </p>
              <p>
                <span className="font-medium">Name:</span>{" "}
                {result.pan_details.name}
              </p>
              <p>
                <span className="font-medium">DOB:</span>{" "}
                {result.pan_details.dob}
              </p>
              <p className="text-xs text-slate-500 mt-2">
                Status: {result.message}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
