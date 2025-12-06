import { useState } from "react";
import api from "../../api/apiClient";

export default function CustomerOnboarding() {
  const [panImage, setPanImage] = useState(null);
  const [panNumber, setPanNumber] = useState("");
  const [mobile, setMobile] = useState("");
  const [email, setEmail] = useState("");

  const [panData, setPanData] = useState(null);
  const [ocrData, setOcrData] = useState(null);
  const [form, setForm] = useState({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  // ---------------------------
  // Auto-fill form after PAN verify
  // ---------------------------
  const autoFillForm = (d) => {
    setForm({
      pan: d.pan,
      fullName: d.name,
      dob: formatDob(d.dob),
      address: d.address,
      city: d.city,
      state: d.state,
      country: d.country,
      pincode: d.pincode,
      maskedAadhaar: d.maskedAadhaar,
      mobile: mobile,
      email: email,
    });
  };

  // Format DOB to yyyy-mm-dd
  const formatDob = (dob) => {
    if (!dob) return "";
    if (dob.includes("/")) {
      const [day, month, year] = dob.split("/");
      return `${year}-${month}-${day}`;
    }
    return dob;
  };

  // ---------------------------
  // OCR + PAN Verification
  // ---------------------------
  const uploadAndVerifyPAN = async () => {
    if (!panImage) return alert("Upload PAN Image");
    if (!mobile) return alert("Enter Mobile Number");
    if (!email) return alert("Enter Email");

    setLoading(true);

    const formData = new FormData();
    formData.append("file", panImage);

    try {
      const res = await api.post("/pan/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const ocr = res.data.ocr;
      const pd = res.data.panDetails;

      setOcrData(ocr);
      setPanData(pd);
      setPanNumber(pd.pan);

      autoFillForm(pd);
    } catch (err) {
      console.error(err);
      alert("OCR Failed. Try manual entry.");
    }

    setLoading(false);
  };

  // ---------------------------
  // Manual PAN Verification
  // ---------------------------
  const verifyPANManual = async () => {
    if (!panNumber) return alert("Enter PAN");
    if (!mobile) return alert("Enter Mobile Number");
    if (!email) return alert("Enter Email");

    setLoading(true);

    try {
      const res = await api.post("/pan/verify", {
        panNumber,
        mobile,
        email,
      });

      const pd = res.data.data;
      setPanData(pd);

      autoFillForm(pd);
    } catch (err) {
      console.error(err);
      alert("PAN Verification failed");
    }

    setLoading(false);
  };

  // ---------------------------
  // Full KYC Flow:
  // 1) Save Basic
  // 2) Aadhaar Verify
  // 3) Experian Score
  // ---------------------------
  const handleSaveCustomer = async () => {
    if (!form.pan) return alert("PAN is missing in form");
    if (!form.mobile) return alert("Mobile is missing");
    if (!form.email) return alert("Email is missing");

    setSaving(true);

    try {
      // Step 1 — Save Basic Customer
      const basicRes = await api.post("/customer/save-basic", form);
      const { customerId, customerCode } = basicRes.data;

      console.log("✔ Basic Customer Saved → ", customerCode);

      // Step 2 — Aadhaar Verify (if you have txn id in future)
      if (form.aadhaarTransactionId) {
        const aadhaarRes = await api.post("/customer/aadhaar/verify", {
          customerCode,
          unifiedTransactionId: form.aadhaarTransactionId,
        });
        console.log("✔ Aadhaar Verified:", aadhaarRes.data);
      }

      // Step 3 — Experian Score (CIBIL)
      const experianRes = await api.post("/customer/experian/score", {
        customerCode,
        pan: form.pan,
      });
      console.log("✔ Experian Score:", experianRes.data);

      alert("Customer KYC completed successfully!");

    } catch (err) {
      console.error(err);
      alert("Customer save or KYC failed.");
    }

    setSaving(false);
  };

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h2 className="text-2xl font-bold mb-4">Customer Onboarding</h2>

      {/* =================== Contact Inputs =================== */}
      <div className="bg-white p-4 rounded-xl shadow mb-6">
        <h3 className="text-lg font-semibold">Customer Contact Details</h3>

        <div className="grid grid-cols-2 gap-4 mt-3">
          <input
            className="border p-2 rounded"
            placeholder="Mobile Number"
            value={mobile}
            onChange={(e) => setMobile(e.target.value)}
          />
          <input
            className="border p-2 rounded"
            placeholder="Email ID"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
      </div>

      {/* =================== Upload PAN =================== */}
      <div className="bg-white p-4 rounded-xl shadow mb-6">
        <h3 className="text-lg font-semibold">Upload PAN Image (OCR)</h3>

        <input
          type="file"
          accept="image/*,application/pdf"
          onChange={(e) => setPanImage(e.target.files[0])}
          className="mt-3"
        />

        <button
          onClick={uploadAndVerifyPAN}
          className="ml-3 bg-blue-600 text-white px-4 py-2 rounded"
        >
          {loading ? "Processing..." : "Upload & OCR PAN"}
        </button>
      </div>

      {/* =================== Manual PAN Entry =================== */}
      <div className="bg-white p-4 rounded-xl shadow mb-6">
        <h3 className="text-lg font-semibold">Or Enter PAN Manually</h3>

        <div className="flex gap-3 mt-3">
          <input
            className="border p-2 rounded"
            placeholder="Enter PAN"
            value={panNumber}
            onChange={(e) => setPanNumber(e.target.value.toUpperCase())}
          />

          <button
            onClick={verifyPANManual}
            className="bg-indigo-600 text-white px-4 py-2 rounded"
          >
            {loading ? "Verifying..." : "Verify PAN"}
          </button>
        </div>
      </div>

      {/* =================== Auto-Filled Customer Form =================== */}
      {panData && (
        <div className="bg-white p-4 rounded-xl shadow">
          <h3 className="text-lg font-semibold mb-4">Customer Details</h3>

          <div className="grid grid-cols-2 gap-4">
            {Object.keys(form).map((key) => (
              <div key={key}>
                <label className="text-sm font-medium capitalize">{key}</label>
                <input
                  className="border w-full p-2 rounded"
                  value={form[key] || ""}
                  onChange={(e) =>
                    setForm({ ...form, [key]: e.target.value })
                  }
                />
              </div>
            ))}
          </div>

          <button
            onClick={handleSaveCustomer}
            className="mt-4 bg-green-600 text-white px-4 py-2 rounded"
          >
            {saving ? "Saving..." : "Save Customer & Run KYC"}
          </button>
        </div>
      )}
    </div>
  );
}
