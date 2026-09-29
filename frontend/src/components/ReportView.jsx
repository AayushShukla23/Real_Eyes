import { useState } from 'react';

export default function ReportView({ report, onReset }) {
  const [activeTab, setActiveTab] = useState('verdict');
  const [copied, setCopied] = useState(false);

  const fake = report.prediction === 'FAKE';
  const confidence = (report.confidence * 100).toFixed(1);

  const handleCopyJSON = () => {
    navigator.clipboard.writeText(JSON.stringify(report, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-full space-y-4">
      {/* Tabs Bar */}
      <div className="flex border-4 border-black bg-white p-1 shadow-[6px_6px_0_#000] gap-1">
        <button
          type="button"
          onClick={() => setActiveTab('verdict')}
          className={`flex-1 py-2 text-xs font-black uppercase tracking-wider transition ${
            activeTab === 'verdict' ? 'bg-[#e2a100] border-2 border-black' : 'hover:bg-[#f3efe6]'
          }`}
        >
          1. Verdict
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('telemetry')}
          className={`flex-1 py-2 text-xs font-black uppercase tracking-wider transition ${
            activeTab === 'telemetry' ? 'bg-[#e2a100] border-2 border-black' : 'hover:bg-[#f3efe6]'
          }`}
        >
          2. ML Telemetry
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('raw')}
          className={`flex-1 py-2 text-xs font-black uppercase tracking-wider transition ${
            activeTab === 'raw' ? 'bg-[#e2a100] border-2 border-black' : 'hover:bg-[#f3efe6]'
          }`}
        >
          3. Mongo JSON
        </button>
      </div>

      {/* Tab 1: Verdict */}
      {activeTab === 'verdict' && (
        <div className="space-y-4">
          <div
            className={`border-4 border-black p-6 shadow-[8px_8px_0_#000] ${
              fake ? 'bg-[#c43c2d] text-white' : 'bg-[#1f6b4a] text-white'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-black uppercase tracking-[0.2em] opacity-80">
                Classification Stamp
              </span>
              <span className="text-xs font-mono font-bold bg-black/40 px-2 py-1 border border-white/20">
                {report.report_id}
              </span>
            </div>

            <h2 className="text-4xl font-black sm:text-5xl mb-2">
              {fake ? 'DEEPFAKE DETECTED' : 'AUTHENTIC STREAM'}
            </h2>
            <p className="text-lg font-bold">Confidence Rating: {confidence}%</p>

            <div className="mt-4 w-full bg-black/40 h-3 border border-white/30 overflow-hidden">
              <div className="h-full bg-white transition-all duration-1000" style={{ width: `${confidence}%` }} />
            </div>
          </div>

          <div className="border-4 border-black bg-white p-4 shadow-[6px_6px_0_#000] space-y-2 text-xs font-medium">
            <p className="font-bold text-sm uppercase">Forensic Summary:</p>
            <p>
              Target file <strong className="font-mono">{report.filename}</strong> evaluated across{' '}
              {report.frames_analyzed} temporal frames. Spatial feature maps extracted using pretrained InceptionV3
              and passed to a GRU temporal classification head.
            </p>
          </div>
        </div>
      )}

      {/* Tab 2: Telemetry */}
      {activeTab === 'telemetry' && (
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="border-4 border-black bg-white p-4 shadow-[5px_5px_0_#000]">
            <p className="text-[10px] font-black uppercase text-[#5c564c]">Processing Latency</p>
            <p className="text-2xl font-black mt-1">{report.processing_time_ms} ms</p>
          </div>
          <div className="border-4 border-black bg-white p-4 shadow-[5px_5px_0_#000]">
            <p className="text-[10px] font-black uppercase text-[#5c564c]">Frame Sequence Length</p>
            <p className="text-2xl font-black mt-1">{report.frames_analyzed} frames</p>
          </div>
          <div className="border-4 border-black bg-white p-4 shadow-[5px_5px_0_#000]">
            <p className="text-[10px] font-black uppercase text-[#5c564c]">Raw Sigmoid Output</p>
            <p className="text-2xl font-black mt-1 font-mono">{report.raw_score}</p>
          </div>
          <div className="border-4 border-black bg-white p-4 shadow-[5px_5px_0_#000]">
            <p className="text-[10px] font-black uppercase text-[#5c564c]">Pipeline Version</p>
            <p className="text-2xl font-black mt-1">v{report.model_metadata?.version || '1.0.0'}</p>
          </div>
        </div>
      )}

      {/* Tab 3: Mongo JSON */}
      {activeTab === 'raw' && (
        <div className="border-4 border-black bg-[#141414] p-4 shadow-[6px_6px_0_#000] text-emerald-400 font-mono text-xs">
          <div className="flex items-center justify-between mb-3 border-b border-neutral-800 pb-2 text-[#e2a100]">
            <span>MONGO_DOCUMENT_VIEW</span>
            <button
              type="button"
              onClick={handleCopyJSON}
              className="bg-white text-black px-2 py-0.5 text-[10px] font-black uppercase border border-black hover:bg-[#e2a100]"
            >
              {copied ? 'Copied!' : 'Copy JSON'}
            </button>
          </div>
          <pre className="overflow-x-auto p-2 bg-black/50 border border-neutral-800 max-h-[260px]">
            {JSON.stringify(report, null, 2)}
          </pre>
        </div>
      )}

      <button
        type="button"
        onClick={onReset}
        className="w-full border-4 border-black bg-[#e2a100] px-4 py-3 text-xs font-black uppercase shadow-[6px_6px_0_#000] hover:translate-x-[1px] hover:translate-y-[1px] transition cursor-pointer"
      >
        Run Another Video Analysis
      </button>
    </div>
  );
}