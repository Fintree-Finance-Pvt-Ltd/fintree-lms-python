export default function Offer({ limit = 20000 }) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white shadow-xl rounded-xl p-6 w-full max-w-md text-center">
        <h2 className="text-2xl font-semibold mb-2">Loan Offer</h2>

        <p className="text-gray-600 mb-4">Based on your profile, you are eligible for:</p>

        <div className="text-4xl font-bold text-green-600 mb-6">₹ {limit.toLocaleString()}</div>

        <button className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700">
          Take Loan →
        </button>
      </div>
    </div>
  );
}
