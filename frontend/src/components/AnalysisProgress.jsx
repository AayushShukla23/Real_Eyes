import { STATES } from '../hooks/useVideoPrediction';

export default function AnalysisProgress({ progress, state }) {
  const uploading = state === STATES.UPLOADING;

  return (
    <div className="w-full border-4 border-black bg-white p-6 shadow-[8px_8px_0_#000]">
      <p className="mb-2 text-xs font-black uppercase tracking-[0.2em] text-[#5c564c]">
        Pipeline Status
      </p>
      <h3 className="mb-2 text-3xl font-black">
        {uploading ? 'Transferring clip' : 'Reading temporal signal'}
      </h3>
      <p className="mb-6 max-w-lg text-sm font-medium text-[#5c564c]">
        {uploading
          ? `Upload progress ${progress}%`
          : 'Frame sampling → Inception features → GRU sequence score'}
      </p>

      <div className="h-6 border-4 border-black bg-[#f3efe6]">
        <div
          className="h-full bg-[#e2a100] transition-all duration-300"
          style={{ width: `${uploading ? progress : 70}%` }}
        />
      </div>
    </div>
  );
}