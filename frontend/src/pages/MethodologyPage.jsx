export default function MethodologyPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-12 space-y-8">
      <div className="border-4 border-black bg-[#fffdf8] p-8 shadow-[10px_10px_0_#000] space-y-4">
        <span className="border-2 border-black bg-[#e2a100] px-2.5 py-1 text-xs font-black uppercase">
          Engineering Specification
        </span>
        <h1 className="text-4xl font-black">System Architecture & ML Pipeline</h1>
        <p className="text-sm font-medium text-[#5c564c] leading-relaxed">
          RealEyes decouples spatial representation learning from temporal sequence modeling to maximize parameter efficiency and evaluation reliability.
        </p>
      </div>

      <div className="border-4 border-black bg-white p-6 shadow-[8px_8px_0_#000] space-y-4 font-mono text-xs">
        <p className="font-bold text-sm text-black">PIPELINE EXECUTION STEPS:</p>
        <div className="p-4 bg-[#f3efe6] border-2 border-black space-y-2">
          <p>1. Video Ingestion → MP4 / AVI Container Validation</p>
          <p>2. Frame Decoding → OpenCV Uniform Sampling (T=20)</p>
          <p>3. Spatial Preprocess → Center Crop (preserve aspect ratio) → 224x224 RGB</p>
          <p>4. CNN Pass → InceptionV3 Feature Map Extraction (2048-dim embedding)</p>
          <p>5. Temporal Classification → Masked GRU Recurrent Classifier</p>
          <p>6. Report Output → Sigmoid Decision + MongoDB Atlas Document Persistence</p>
        </div>
      </div>
    </div>
  );
}