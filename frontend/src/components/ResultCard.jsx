export default function ResultCard({ result, onReset }) {
  const fake = result.prediction === 'FAKE';
  const confidence = (result.confidence * 100).toFixed(1);

  return (
    <div className="w-full space-y-4">
      <div
        className={`border-4 border-black p-6 shadow-[10px_10px_0_#000] ${
          fake ? 'bg-[#c43c2d] text-white' : 'bg-[#1f6b4a] text-white'
        }`}
      >
        <p className="mb-2 text-xs font-black uppercase tracking-[0.22em] opacity-80">
          Verdict Stamp
        </p>
        <h2 className="mb-2 text-4xl font-black sm:text-5xl">
          {fake ? 'MANIPULATED' : 'LIKELY REAL'}
        </h2>
        <p className="text-lg font-bold">
          Confidence {confidence}%
        </p>
        <p className="mt-3 max-w-xl text-sm font-medium opacity-90">
          Score is model sigmoid output, not a calibrated probability. Treat this as a decision
          support signal, not courtroom proof.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="border-4 border-black bg-white p-4 shadow-[5px_5px_0_#000]">
          <p className="text-xs font-black uppercase tracking-[0.16em] text-[#5c564c]">Latency</p>
          <p className="mt-1 text-2xl font-black">{result.processing_time_ms} ms</p>
        </div>
        <div className="border-4 border-black bg-white p-4 shadow-[5px_5px_0_#000]">
          <p className="text-xs font-black uppercase tracking-[0.16em] text-[#5c564c]">Frames</p>
          <p className="mt-1 text-2xl font-black">{result.frames_analyzed}</p>
        </div>
        <div className="border-4 border-black bg-white p-4 shadow-[5px_5px_0_#000]">
          <p className="text-xs font-black uppercase tracking-[0.16em] text-[#5c564c]">Stack</p>
          <p className="mt-1 text-lg font-black leading-tight">
            {result.model_metadata.architecture}
          </p>
        </div>
      </div>

      <button
        type="button"
        onClick={onReset}
        className="w-full border-4 border-black bg-[#e2a100] px-4 py-3 text-sm font-black uppercase tracking-wide shadow-[6px_6px_0_#000] transition hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[3px_3px_0_#000]"
      >
        Run another clip
      </button>
    </div>
  );
}