import { Link } from 'react-router-dom';

export default function LandingPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-12 space-y-12">
      <div className="border-4 border-black bg-[#fffdf8] p-8 shadow-[12px_12px_0_#000] space-y-6">
        <span className="inline-block border-2 border-black bg-[#e2a100] px-3 py-1 text-xs font-black uppercase tracking-[0.2em]">
          AI Safety & Forensics
        </span>
        <h1 className="text-5xl sm:text-6xl font-black leading-[0.95] tracking-tight">
          Detect synthetic face-swaps before they spread.
        </h1>
        <p className="max-w-2xl text-base font-medium text-[#5c564c] leading-relaxed">
          RealEyes combines spatial CNN feature maps with a temporal GRU model to spot frame-to-frame manipulation signatures in deepfake videos.
        </p>

        <div className="pt-2 flex flex-wrap gap-4">
          <Link
            to="/app"
            className="border-4 border-black bg-[#141414] text-white px-6 py-4 text-sm font-black uppercase tracking-wider shadow-[6px_6px_0_#e2a100] hover:translate-x-[2px] hover:translate-y-[2px] transition"
          >
            Launch Forensic Desk →
          </Link>
          <Link
            to="/methodology"
            className="border-4 border-black bg-white text-black px-6 py-4 text-sm font-black uppercase tracking-wider shadow-[6px_6px_0_#000] hover:bg-[#f3efe6] transition"
          >
            Read Architecture
          </Link>
        </div>
      </div>

      <div className="grid gap-6 sm:grid-cols-3">
        <div className="border-4 border-black bg-white p-6 shadow-[8px_8px_0_#000]">
          <h3 className="text-lg font-black uppercase mb-2">1. InceptionV3</h3>
          <p className="text-xs font-medium text-[#5c564c] leading-normal">
            Extracts 2048-dimensional spatial representations from center-cropped square frame inputs.
          </p>
        </div>
        <div className="border-4 border-black bg-white p-6 shadow-[8px_8px_0_#000]">
          <h3 className="text-lg font-black uppercase mb-2">2. GRU Temporal</h3>
          <p className="text-xs font-medium text-[#5c564c] leading-normal">
            Evaluates sequence inconsistencies across fixed 20-frame temporal windows.
          </p>
        </div>
        <div className="border-4 border-black bg-white p-6 shadow-[8px_8px_0_#000]">
          <h3 className="text-lg font-black uppercase mb-2">3. MongoDB Atlas</h3>
          <p className="text-xs font-medium text-[#5c564c] leading-normal">
            Persists prediction reports and telemetry documents asynchronously in the cloud.
          </p>
        </div>
      </div>
    </div>
  );
}