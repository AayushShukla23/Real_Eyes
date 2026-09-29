import { useEffect, useState } from 'react';

const LOG_STEPS = [
  '[00:00.02] Ingestion: File buffer received and validated',
  '[00:00.14] Video Decoder: Extracting metadata & total frame counts...',
  '[00:00.32] Frame Sampler: Uniform sampling (T=20 sequence length)',
  '[00:00.68] Spatial Preprocessor: Aspect-ratio center crop -> 224x224 RGB',
  '[00:01.12] Feature Extractor: Invoking InceptionV3 (ImageNet AvgPool)',
  '[00:01.85] Spatial Forward Pass: Generated [20, 2048] embedding tensor',
  '[00:02.10] Sequence Model: Passing tensor to GRU temporal classifier',
  '[00:02.45] Post-Processor: Computing sigmoid decision confidence',
  '[00:02.80] Database Stream: Writing report document to MongoDB Atlas...'
];

export default function LiveTerminal({ progress, state }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    setLogs([]);
    let index = 0;
    const interval = setInterval(() => {
      if (index < LOG_STEPS.length) {
        setLogs((prev) => [...prev, LOG_STEPS[index]]);
        index++;
      } else {
        clearInterval(interval);
      }
    }, 350);

    return () => clearInterval(interval);
  }, [state]);

  return (
    <div className="w-full border-4 border-black bg-[#141414] text-emerald-400 p-5 font-mono text-xs shadow-[8px_8px_0_#000]">
      <div className="flex items-center justify-between border-b border-neutral-800 pb-3 mb-4 text-[#e2a100] font-bold">
        <span>RUNNING_FORENSIC_PIPELINE.EXE</span>
        <span className="animate-pulse">● EXECUTING</span>
      </div>

      <div className="space-y-2 min-h-[220px] max-h-[300px] overflow-y-auto">
        {logs.map((log, idx) => (
          <p key={idx} className="leading-relaxed">
            <span className="text-gray-500 mr-2">&gt;</span>
            {log}
          </p>
        ))}
      </div>

      <div className="mt-4 pt-3 border-t border-neutral-800 flex items-center justify-between text-gray-400">
        <span>Progress: {progress}%</span>
        <span>Target Architecture: InceptionV3 + GRU</span>
      </div>
    </div>
  );
}