import { useRef, useState } from "react";

export default function PhotoCapture() {
  const videoRef = useRef(null);
  const [photo, setPhoto] = useState(null);

  const startCamera = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoRef.current.srcObject = stream;
  };

  const takePhoto = () => {
    const canvas = document.createElement("canvas");
    canvas.width = 300;
    canvas.height = 300;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(videoRef.current, 0, 0, 300, 300);
    setPhoto(canvas.toDataURL("image/png"));
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <video ref={videoRef} autoPlay className="rounded-xl shadow-md mb-4"></video>

      <button
        onClick={startCamera}
        className="bg-blue-500 text-white px-4 py-2 rounded-lg"
      >
        Start Camera
      </button>

      <button
        onClick={takePhoto}
        className="mt-3 bg-green-500 text-white px-4 py-2 rounded-lg"
      >
        Capture Photo
      </button>

      {photo && <img src={photo} className="mt-4 w-48 rounded-xl shadow-md" />}
    </div>
  );
}
