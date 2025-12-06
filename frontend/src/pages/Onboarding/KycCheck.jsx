export default function KycCheck() {
  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-gray-100 p-4">
      <div className="bg-white shadow-lg rounded-xl p-6 max-w-md w-full text-center">

        <div className="animate-spin h-10 w-10 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>

        <h2 className="text-xl font-semibold">Running KYC Checks</h2>
        <p className="text-gray-500 mt-2">PAN Validation, Aadhaar, Bureau fetching…</p>
      </div>
    </div>
  );
}
